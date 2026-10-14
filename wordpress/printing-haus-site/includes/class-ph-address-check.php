<?php
/**
 * USPS address check at checkout.
 *
 * When the customer clicks Pay now, the delivery address is checked against the USPS Addresses API (v3)
 * before payment. If USPS has a better version, checkout pauses and the customer chooses between the
 * suggestion and what they typed (see assets/checkout.js). Customers are never blocked: "Keep as entered"
 * always continues, and any USPS outage, timeout or rate limit lets checkout through unchanged.
 *
 * Also repairs a common autocomplete mix-up: neighborhood in Street address and the real street in
 * Apartment/suite. If the address as entered isn't found but Apartment looks like a street address,
 * it is checked in its place and offered as the suggestion.
 *
 * Settings: Settings > Address check (USPS Consumer Key + Secret from developer.usps.com).
 * Or define PH_USPS_CLIENT_ID and PH_USPS_CLIENT_SECRET in wp-config.php.
 */

defined( 'ABSPATH' ) || exit;

class PH_Address_Check {

	const API       = 'https://apis.usps.com';
	const COUNTRIES = array( 'US', 'PR', 'VI', 'GU', 'AS', 'MP' );
	const SESSION   = 'ph_addr_pending';
	const CONFIRM   = 'ph_addr_confirmed';

	public static function init() {
		add_action( 'woocommerce_after_checkout_validation', array( __CLASS__, 'validate' ), 20, 2 );
		add_action( 'wc_ajax_ph_address_pending', array( __CLASS__, 'ajax_pending' ) );
		add_action( 'admin_menu', array( __CLASS__, 'admin_menu' ) );
		add_action( 'admin_init', array( __CLASS__, 'register_settings' ) );
	}

	/* ------------------------------------------------------------ settings */

	public static function client_id() {
		return defined( 'PH_USPS_CLIENT_ID' ) ? PH_USPS_CLIENT_ID : (string) get_option( 'ph_usps_client_id', '' );
	}

	public static function client_secret() {
		return defined( 'PH_USPS_CLIENT_SECRET' ) ? PH_USPS_CLIENT_SECRET : (string) get_option( 'ph_usps_client_secret', '' );
	}

	public static function enabled() {
		return '1' === (string) get_option( 'ph_usps_enabled', '1' ) && self::client_id() && self::client_secret();
	}

	public static function admin_menu() {
		add_options_page( 'Address check', 'Address check', 'manage_options', 'ph-address-check', array( __CLASS__, 'settings_page' ) );
	}

	public static function register_settings() {
		register_setting( 'ph_address_check', 'ph_usps_enabled', array( 'type' => 'string', 'sanitize_callback' => function ( $v ) { return $v ? '1' : '0'; }, 'default' => '1' ) );
		register_setting( 'ph_address_check', 'ph_usps_client_id', array( 'type' => 'string', 'sanitize_callback' => 'sanitize_text_field' ) );
		register_setting( 'ph_address_check', 'ph_usps_client_secret', array(
			'type'              => 'string',
			// Leaving the field blank keeps the saved secret.
			'sanitize_callback' => function ( $v ) {
				$v = sanitize_text_field( $v );
				return '' === $v ? (string) get_option( 'ph_usps_client_secret', '' ) : $v;
			},
		) );
		foreach ( array( 'ph_usps_client_id', 'ph_usps_client_secret' ) as $opt ) {
			add_action( 'update_option_' . $opt, function () {
				delete_transient( 'ph_usps_token' );
			} );
		}
	}

	public static function settings_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		$test = null;
		if ( isset( $_GET['ph_test'] ) && check_admin_referer( 'ph_usps_test' ) ) {
			delete_transient( 'ph_usps_token' );
			$token = self::token();
			$test  = $token ? 'Connected to USPS.' : 'Could not connect. Check the Consumer Key and Secret.';
		}
		?>
		<div class="wrap">
			<h1>Address check (USPS)</h1>
			<p>Checks US delivery addresses with USPS when a customer clicks Pay now, and offers a corrected version if there is one.
				Customers can always keep the address they entered. Get a free Consumer Key and Secret by creating an app at
				<a href="https://developer.usps.com" target="_blank" rel="noopener">developer.usps.com</a>.</p>
			<?php if ( $test ) : ?>
				<div class="notice <?php echo false !== strpos( $test, 'Connected' ) ? 'notice-success' : 'notice-error'; ?>"><p><?php echo esc_html( $test ); ?></p></div>
			<?php endif; ?>
			<form method="post" action="options.php">
				<?php settings_fields( 'ph_address_check' ); ?>
				<table class="form-table" role="presentation">
					<tr><th scope="row">Check addresses</th><td><label><input type="checkbox" name="ph_usps_enabled" value="1" <?php checked( '1', get_option( 'ph_usps_enabled', '1' ) ); ?>> On</label></td></tr>
					<tr><th scope="row"><label for="ph_usps_client_id">Consumer Key</label></th><td>
						<?php if ( defined( 'PH_USPS_CLIENT_ID' ) ) : ?>Set in wp-config.php<?php else : ?>
						<input type="text" class="regular-text" id="ph_usps_client_id" name="ph_usps_client_id" value="<?php echo esc_attr( get_option( 'ph_usps_client_id', '' ) ); ?>" autocomplete="off"><?php endif; ?></td></tr>
					<tr><th scope="row"><label for="ph_usps_client_secret">Consumer Secret</label></th><td>
						<?php if ( defined( 'PH_USPS_CLIENT_SECRET' ) ) : ?>Set in wp-config.php<?php else : ?>
						<input type="password" class="regular-text" id="ph_usps_client_secret" name="ph_usps_client_secret" value="" placeholder="<?php echo get_option( 'ph_usps_client_secret' ) ? esc_attr( 'Saved. Leave blank to keep' ) : ''; ?>" autocomplete="new-password"><?php endif; ?></td></tr>
				</table>
				<?php submit_button(); ?>
			</form>
			<p><a class="button" href="<?php echo esc_url( wp_nonce_url( admin_url( 'options-general.php?page=ph-address-check&ph_test=1' ), 'ph_usps_test' ) ); ?>">Test connection</a></p>
			<p class="description">New USPS apps have a low hourly request limit. Results are cached for a day, and if the limit is reached checkout simply continues without the check.
				You can ask USPS for a higher limit from your developer account.</p>
		</div>
		<?php
	}

	/* --------------------------------------------------------------- USPS */

	/** OAuth token, cached until shortly before it expires. */
	public static function token() {
		$cached = get_transient( 'ph_usps_token' );
		if ( $cached ) {
			return $cached;
		}
		$res = wp_remote_post( self::API . '/oauth2/v3/token', array(
			'timeout' => 8,
			'headers' => array( 'Content-Type' => 'application/json', 'Accept' => 'application/json' ),
			'body'    => wp_json_encode( array(
				'grant_type'    => 'client_credentials',
				'client_id'     => self::client_id(),
				'client_secret' => self::client_secret(),
			) ),
		) );
		if ( is_wp_error( $res ) || 200 !== (int) wp_remote_retrieve_response_code( $res ) ) {
			return '';
		}
		$body = json_decode( wp_remote_retrieve_body( $res ), true );
		if ( empty( $body['access_token'] ) ) {
			return '';
		}
		$ttl = isset( $body['expires_in'] ) ? max( 60, (int) $body['expires_in'] - 300 ) : 3600;
		set_transient( 'ph_usps_token', $body['access_token'], $ttl );
		return $body['access_token'];
	}

	/**
	 * Look up one address.
	 *
	 * @return array|string|null Normalized result array, 'not_found', or null when USPS can't be reached (fail open).
	 */
	public static function lookup( $street, $secondary, $city, $state, $zip ) {
		$query = array_filter( array(
			'streetAddress'    => $street,
			'secondaryAddress' => $secondary,
			'city'             => $city,
			'state'            => $state,
			'ZIPCode'          => substr( preg_replace( '/\D/', '', (string) $zip ), 0, 5 ),
		), 'strlen' );
		if ( empty( $query['streetAddress'] ) || empty( $query['state'] ) || ( empty( $query['city'] ) && empty( $query['ZIPCode'] ) ) ) {
			return null;
		}

		$key    = 'ph_usps_' . md5( wp_json_encode( $query ) );
		$cached = get_transient( $key );
		if ( false !== $cached ) {
			return $cached;
		}

		$token = self::token();
		if ( ! $token ) {
			return null;
		}
		$res = wp_remote_get( self::API . '/addresses/v3/address?' . http_build_query( $query, '', '&', PHP_QUERY_RFC3986 ), array(
			'timeout' => 6,
			'headers' => array( 'Authorization' => 'Bearer ' . $token, 'Accept' => 'application/json' ),
		) );
		if ( is_wp_error( $res ) ) {
			return null;
		}
		$code = (int) wp_remote_retrieve_response_code( $res );
		$body = json_decode( wp_remote_retrieve_body( $res ), true );

		if ( 401 === $code ) {
			delete_transient( 'ph_usps_token' );
			return null;
		}
		if ( 404 === $code || ( 400 === $code && self::says_not_found( $body ) ) ) {
			set_transient( $key, 'not_found', DAY_IN_SECONDS );
			return 'not_found';
		}
		if ( 200 !== $code || empty( $body['address'] ) ) {
			return null; // Rate limit (429), outage, or a request USPS didn't like: let checkout continue.
		}

		$result = self::parse( $body );
		set_transient( $key, $result, DAY_IN_SECONDS );
		return $result;
	}

	private static function says_not_found( $body ) {
		$msg = isset( $body['error']['message'] ) ? (string) $body['error']['message'] : '';
		return '' !== $msg && false !== stripos( $msg, 'not found' );
	}

	/** Reduce a USPS response to the fields the check needs. */
	public static function parse( array $body ) {
		$a   = $body['address'];
		$zip = isset( $a['ZIPCode'] ) ? (string) $a['ZIPCode'] : '';
		if ( ! empty( $a['ZIPPlus4'] ) ) {
			$zip .= '-' . $a['ZIPPlus4'];
		}
		return array(
			'address_1' => isset( $a['streetAddress'] ) ? (string) $a['streetAddress'] : '',
			'address_2' => isset( $a['secondaryAddress'] ) ? (string) $a['secondaryAddress'] : '',
			'city'      => isset( $a['city'] ) ? (string) $a['city'] : '',
			'state'     => isset( $a['state'] ) ? (string) $a['state'] : '',
			'postcode'  => $zip,
			'dpv'       => isset( $body['additionalInfo']['DPVConfirmation'] ) ? (string) $body['additionalInfo']['DPVConfirmation'] : '',
		);
	}

	/* ---------------------------------------------------------- comparison */

	const WORDS = array(
		'STREET' => 'ST', 'AVENUE' => 'AVE', 'AV' => 'AVE', 'ROAD' => 'RD', 'BOULEVARD' => 'BLVD', 'DRIVE' => 'DR',
		'LANE' => 'LN', 'COURT' => 'CT', 'PLACE' => 'PL', 'TERRACE' => 'TER', 'PARKWAY' => 'PKWY', 'HIGHWAY' => 'HWY',
		'SQUARE' => 'SQ', 'CIRCLE' => 'CIR', 'TRAIL' => 'TRL', 'PLAZA' => 'PLZ', 'EXPRESSWAY' => 'EXPY',
		'APARTMENT' => 'APT', 'SUITE' => 'STE', 'UNIT' => 'UNIT', 'FLOOR' => 'FL', 'BUILDING' => 'BLDG', 'ROOM' => 'RM',
		'NORTH' => 'N', 'SOUTH' => 'S', 'EAST' => 'E', 'WEST' => 'W',
		'NORTHEAST' => 'NE', 'NORTHWEST' => 'NW', 'SOUTHEAST' => 'SE', 'SOUTHWEST' => 'SW',
		'FIRST' => '1ST', 'SECOND' => '2ND', 'THIRD' => '3RD', 'FOURTH' => '4TH', 'FIFTH' => '5TH',
		'SAINT' => 'ST', 'MOUNT' => 'MT', 'FORT' => 'FT',
	);

	/** Upper-case, punctuation-free, with common street words abbreviated the USPS way. */
	public static function norm( $s ) {
		$s = strtoupper( (string) $s );
		$s = preg_replace( '/[^A-Z0-9 ]+/', ' ', $s );
		$words = preg_split( '/\s+/', trim( $s ) );
		$out   = array();
		foreach ( $words as $w ) {
			if ( '' === $w ) {
				continue;
			}
			$out[] = isset( self::WORDS[ $w ] ) ? self::WORDS[ $w ] : $w;
		}
		return implode( ' ', $out );
	}

	/** Same delivery address, allowing for case, punctuation, abbreviations and ZIP+4. */
	public static function same( array $entered, array $usps ) {
		$line = function ( $a ) {
			return self::norm( trim( $a['address_1'] . ' ' . $a['address_2'] ) );
		};
		return $line( $entered ) === $line( $usps )
			&& self::norm( $entered['city'] ) === self::norm( $usps['city'] )
			&& strtoupper( $entered['state'] ) === strtoupper( $usps['state'] )
			&& substr( preg_replace( '/\D/', '', $entered['postcode'] ), 0, 5 ) === substr( preg_replace( '/\D/', '', $usps['postcode'] ), 0, 5 );
	}

	/** "125 COURT ST APT 4B" -> "125 Court St Apt 4B", keeping directionals, PO Box and unit letters upper-case. */
	public static function pretty( $s ) {
		$s     = ucwords( strtolower( (string) $s ) );
		$upper = array( 'N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW', 'PO', 'US', 'FM', 'RR', 'HC' );
		$words = explode( ' ', $s );
		foreach ( $words as $i => $w ) {
			if ( in_array( strtoupper( $w ), $upper, true ) || preg_match( '/^\d+[a-z]$|^[a-z]\d+$/i', $w ) ) {
				$words[ $i ] = strtoupper( $w );
			} elseif ( preg_match( '/^(\d+)(st|nd|rd|th)$/i', $w, $m ) ) {
				$words[ $i ] = $m[1] . strtolower( $m[2] );
			}
		}
		return implode( ' ', $words );
	}

	/** Apartment/suite looks like a full street address ("125 Court St") while Street address doesn't ("Cobble Hill"). */
	public static function looks_swapped( array $a ) {
		return '' !== trim( $a['address_2'] )
			&& preg_match( '/^\s*\d+[A-Z]?\s+\S+/i', $a['address_2'] )
			&& ! preg_match( '/^\s*\d/', $a['address_1'] );
	}

	public static function hash( array $a ) {
		return md5( self::norm( implode( '|', array( $a['address_1'], $a['address_2'], $a['city'], $a['state'], $a['postcode'] ) ) ) );
	}

	/**
	 * Decide what to do with an address.
	 *
	 * @param array    $entered address_1, address_2, city, state, postcode.
	 * @param callable $lookup  fn( street, secondary, city, state, zip ) => array|'not_found'|null.
	 * @return array|null null = fine (or USPS unavailable); otherwise array( type, suggested? ).
	 */
	public static function assess( array $entered, callable $lookup ) {
		$r = $lookup( $entered['address_1'], $entered['address_2'], $entered['city'], $entered['state'], $entered['postcode'] );
		if ( null === $r ) {
			return null;
		}

		// Neighborhood in Street address, real street in Apartment: try the street on its own.
		if ( ( 'not_found' === $r || 'N' === $r['dpv'] ) && self::looks_swapped( $entered ) ) {
			$fixed = $lookup( $entered['address_2'], '', $entered['city'], $entered['state'], $entered['postcode'] );
			if ( is_array( $fixed ) && 'N' !== $fixed['dpv'] ) {
				return array( 'type' => 'suggestion', 'suggested' => $fixed );
			}
		}

		if ( 'not_found' === $r || 'N' === $r['dpv'] ) {
			return array( 'type' => 'not_found' );
		}
		if ( 'D' === $r['dpv'] ) {
			return array( 'type' => 'missing_unit', 'suggested' => $r );
		}
		if ( 'S' === $r['dpv'] ) {
			return array( 'type' => 'unit_unconfirmed', 'suggested' => $r );
		}
		return self::same( $entered, $r ) ? null : array( 'type' => 'suggestion', 'suggested' => $r );
	}

	/* ------------------------------------------------------------ checkout */

	public static function validate( $data, $errors ) {
		if ( WC()->session ) {
			WC()->session->set( self::SESSION, null ); // Never show a result from an earlier attempt.
		}
		if ( ! self::enabled() || ( $errors instanceof WP_Error && $errors->has_errors() ) ) {
			return; // Let the customer fix other errors first.
		}
		if ( ! WC()->cart || ! WC()->cart->needs_shipping() ) {
			return;
		}

		$group = ! empty( $data['ship_to_different_address'] ) ? 'shipping' : 'billing';
		if ( ! in_array( isset( $data[ $group . '_country' ] ) ? $data[ $group . '_country' ] : '', self::COUNTRIES, true ) ) {
			return;
		}
		$entered = array();
		foreach ( array( 'address_1', 'address_2', 'city', 'state', 'postcode' ) as $f ) {
			$entered[ $f ] = isset( $data[ $group . '_' . $f ] ) ? trim( (string) $data[ $group . '_' . $f ] ) : '';
		}

		$hash = self::hash( $entered );
		// phpcs:ignore WordPress.Security.NonceVerification.Missing -- WooCommerce verifies the checkout nonce.
		$confirmed = isset( $_POST[ self::CONFIRM ] ) ? sanitize_text_field( wp_unslash( $_POST[ self::CONFIRM ] ) ) : '';
		if ( $confirmed && hash_equals( $hash, $confirmed ) ) {
			WC()->session->set( self::SESSION, null );
			return; // The customer chose to keep this exact address.
		}

		$result = self::assess( $entered, array( __CLASS__, 'lookup' ) );
		if ( null === $result ) {
			WC()->session->set( self::SESSION, null );
			return;
		}

		WC()->session->set( self::SESSION, array(
			'type'      => $result['type'],
			'group'     => $group,
			'hash'      => $hash,
			'entered'   => $entered,
			'suggested' => isset( $result['suggested'] ) ? self::display( $result['suggested'] ) : null,
		) );
		$errors->add( 'ph_address_check', self::message() );
	}

	/** Shown as the checkout error; assets/checkout.js recognises it and opens the address dialog instead. */
	public static function message() {
		return __( 'Please confirm your delivery address.', 'printing-haus-site' );
	}

	/** A USPS result as it will be filled into the form. */
	public static function display( array $a ) {
		return array(
			'address_1' => self::pretty( $a['address_1'] ),
			'address_2' => self::pretty( $a['address_2'] ),
			'city'      => self::pretty( $a['city'] ),
			'state'     => strtoupper( $a['state'] ),
			'postcode'  => $a['postcode'],
		);
	}

	/** The pending check for the dialog in assets/checkout.js. */
	public static function ajax_pending() {
		$pending = WC()->session ? WC()->session->get( self::SESSION ) : null;
		wp_send_json( array( 'pending' => $pending ? $pending : null ) );
	}
}
