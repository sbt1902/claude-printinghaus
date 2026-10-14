<?php
/**
 * Plugin Name: Printing Haus Site
 * Description: Loads the Printing Haus brand stylesheet for the Bricks templates and gives the Bricks (Checkout v2) WooCommerce checkout a calm, Shopify-style finish, with a shipping dropdown, a slide-open discount code and a USPS address check.
 * Version:     1.4.0
 * Author:      Printing Haus
 * Requires at least: 6.0
 * Requires PHP: 7.4
 *
 * Generated alongside bricks/build_homepage.py. assets/printinghaus.css is rebuilt by
 * that script; assets/checkout.css and assets/checkout.js are edited by hand.
 */

defined( 'ABSPATH' ) || exit;

define( 'PH_SITE_VERSION', '1.4.0' );

require_once __DIR__ . '/includes/class-ph-address-check.php';
add_action( 'plugins_loaded', array( 'PH_Address_Check', 'init' ) );

/**
 * Styles and scripts. Priority 20 so they load after Bricks and WooCommerce and win ties.
 */
add_action( 'wp_enqueue_scripts', function () {
	$url = plugin_dir_url( __FILE__ ) . 'assets/';

	// Interim open-source fonts. Remove once licensed Tiempos + Neue Haas Grotesk are added in Bricks > Custom fonts.
	wp_enqueue_style( 'ph-site-fonts', 'https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400&display=swap', array(), null );
	wp_enqueue_style( 'ph-site', $url . 'printinghaus.css', array( 'ph-site-fonts' ), PH_SITE_VERSION );

	if ( function_exists( 'is_cart' ) && is_cart() ) {
		wp_enqueue_style( 'ph-cart', $url . 'cart.css', array( 'ph-site' ), PH_SITE_VERSION );
		wp_enqueue_script( 'ph-cart', $url . 'cart.js', array(), PH_SITE_VERSION, true );
	}

	if ( ph_site_is_checkout() ) {
		wp_enqueue_style( 'ph-checkout', $url . 'checkout.css', array( 'ph-site' ), PH_SITE_VERSION );
		wp_enqueue_script( 'ph-checkout', $url . 'checkout.js', array( 'jquery', 'wc-checkout' ), PH_SITE_VERSION, true );
		wp_localize_script( 'ph-checkout', 'phCheckout', array(
			'emptyCode'      => __( 'Please enter a discount code.', 'printing-haus-site' ),
			'addressCheck'   => PH_Address_Check::enabled(),
			'addressConfirm' => PH_Address_Check::CONFIRM,
			'addressMessage' => PH_Address_Check::message(),
		) );
	}
}, 20 );

/** True on the checkout form, not on the order-received or pay-for-order screens. */
function ph_site_is_checkout() {
	return function_exists( 'is_checkout' ) && is_checkout()
		&& ! is_wc_endpoint_url( 'order-received' ) && ! is_wc_endpoint_url( 'order-pay' );
}

/* -------------------------------------------------------------------------
 * Shortcodes for the Bricks order summary
 *
 *   [ph_checkout_shipping]  shipping options as a dropdown (or a single line when there is one option)
 *   [ph_checkout_coupon]    "Add discount code" button that slides open a code field, plus applied codes
 *
 * Add each with a Bricks Shortcode element inside the Order summary, under the totals' shipping row.
 * Both refresh with the totals through WooCommerce's checkout fragments.
 * ---------------------------------------------------------------------- */

add_action( 'init', function () {
	add_shortcode( 'ph_checkout_shipping', 'ph_site_shipping_html' );
	add_shortcode( 'ph_checkout_coupon', 'ph_site_coupon_html' );
} );

/** Keep both blocks current whenever WooCommerce refreshes the checkout totals. */
add_filter( 'woocommerce_update_order_review_fragments', function ( $fragments ) {
	$fragments['.ph-co-shipping']         = ph_site_shipping_html();
	$fragments['.ph-co-coupon__applied']  = ph_site_coupon_applied_html();
	return $fragments;
} );

/** "Standard: $5.00" without the delivery-estimate markup other plugins append. */
function ph_site_rate_text( $rate ) {
	$label = wc_cart_totals_shipping_method_label( $rate );
	$label = preg_replace( '#<br\s*/?>\s*<small[^>]*>.*?</small>#is', '', $label );
	return trim( html_entity_decode( wp_strip_all_tags( $label ), ENT_QUOTES, get_bloginfo( 'charset' ) ) );
}

/** The delivery estimate (added by Printing Haus Selector) for a rate, if any. */
function ph_site_rate_eta( $rate ) {
	$label = wc_cart_totals_shipping_method_label( $rate );
	return preg_match( '#<small[^>]*>.*?</small>#is', $label, $m ) ? $m[0] : '';
}

function ph_site_shipping_html() {
	if ( ! function_exists( 'WC' ) || ! WC()->cart ) {
		return '<div class="ph-co-shipping"></div>';
	}
	if ( ! WC()->cart->needs_shipping() ) {
		return '<div class="ph-co-shipping"></div>';
	}

	$packages = WC()->shipping()->get_packages();
	$chosen   = WC()->session ? (array) WC()->session->get( 'chosen_shipping_methods', array() ) : array();
	$multi    = count( $packages ) > 1;

	ob_start();
	echo '<div class="ph-co-shipping">';
	foreach ( $packages as $i => $package ) {
		$rates    = isset( $package['rates'] ) ? $package['rates'] : array();
		$selected = isset( $chosen[ $i ] ) && isset( $rates[ $chosen[ $i ] ] ) ? $chosen[ $i ] : (string) key( $rates );
		$field_id = 'ph-shipping-method-' . $i;
		$title    = $multi
			? apply_filters( 'woocommerce_shipping_package_name', sprintf( __( 'Shipping %d', 'woocommerce' ), $i + 1 ), $i, $package )
			: __( 'Shipping', 'woocommerce' );

		echo '<div class="ph-co-shipping__package">';
		echo '<label class="ph-co-shipping__label" for="' . esc_attr( $field_id ) . '">' . esc_html( $title ) . '</label>';

		if ( count( $rates ) > 1 ) {
			echo '<select name="shipping_method[' . esc_attr( $i ) . ']" data-index="' . esc_attr( $i ) . '" id="' . esc_attr( $field_id ) . '" class="shipping_method ph-co-select">';
			foreach ( $rates as $rate ) {
				echo '<option value="' . esc_attr( $rate->id ) . '" ' . selected( $rate->id, $selected, false ) . '>' . esc_html( ph_site_rate_text( $rate ) ) . '</option>';
			}
			echo '</select>';
		} elseif ( $rates ) {
			$only = reset( $rates );
			echo '<input type="hidden" name="shipping_method[' . esc_attr( $i ) . ']" data-index="' . esc_attr( $i ) . '" id="' . esc_attr( $field_id ) . '" value="' . esc_attr( $only->id ) . '" class="shipping_method">';
			echo '<p class="ph-co-shipping__single">' . esc_html( ph_site_rate_text( $only ) ) . '</p>';
		} else {
			$note = WC()->customer && WC()->customer->has_calculated_shipping()
				? apply_filters( 'woocommerce_no_shipping_available_html', __( 'There are no shipping options available. Please ensure that your address has been entered correctly, or contact us if you need any help.', 'woocommerce' ) )
				: apply_filters( 'woocommerce_shipping_may_be_available_html', __( 'Enter your address to view shipping options.', 'woocommerce' ) );
			echo '<p class="ph-co-shipping__note">' . wp_kses_post( $note ) . '</p>';
		}

		if ( $rates && isset( $rates[ $selected ] ) ) {
			$eta = ph_site_rate_eta( $rates[ $selected ] );
			if ( $eta ) {
				echo '<div class="ph-co-shipping__eta">' . wp_kses_post( $eta ) . '</div>';
			}
		}
		echo '</div>';
	}
	echo '</div>';
	return ob_get_clean();
}

function ph_site_coupon_applied_html() {
	$html = '<ul class="ph-co-coupon__applied">';
	if ( function_exists( 'WC' ) && WC()->cart ) {
		foreach ( WC()->cart->get_coupons() as $code => $coupon ) {
			$html .= '<li><span class="ph-co-coupon__code">' . esc_html( wc_format_coupon_code( $code ) ) . '</span>'
				. '<span class="ph-co-coupon__amount">' . wc_cart_totals_coupon_html( $coupon, false ) . '</span></li>';
		}
	}
	return $html . '</ul>';
}

function ph_site_coupon_html() {
	if ( ! function_exists( 'wc_coupons_enabled' ) || ! wc_coupons_enabled() ) {
		return '';
	}
	ob_start();
	?>
	<div class="ph-co-coupon">
		<button type="button" class="ph-co-coupon__toggle" aria-expanded="false" aria-controls="ph-co-coupon-panel">
			<?php esc_html_e( 'Add discount code', 'printing-haus-site' ); ?>
		</button>
		<div class="ph-co-coupon__panel" id="ph-co-coupon-panel">
			<div class="ph-co-coupon__inner" inert>
				<div class="ph-co-coupon__row">
					<label class="screen-reader-text" for="ph-co-coupon-code"><?php esc_html_e( 'Discount code', 'printing-haus-site' ); ?></label>
					<input type="text" id="ph-co-coupon-code" class="input-text" placeholder="<?php esc_attr_e( 'Discount code', 'printing-haus-site' ); ?>" autocomplete="off" autocapitalize="characters">
					<button type="button" class="ph-co-coupon__apply"><?php esc_html_e( 'Apply', 'printing-haus-site' ); ?></button>
				</div>
			</div>
		</div>
		<div class="ph-co-coupon__msg" aria-live="polite"></div>
		<?php echo ph_site_coupon_applied_html(); // phpcs:ignore WordPress.Security.EscapeOutput -- escaped above ?>
	</div>
	<?php
	return ob_get_clean();
}

/** Plain, standard button wording. */
add_filter( 'woocommerce_order_button_text', function () {
	return __( 'Pay now', 'printing-haus-site' );
} );
