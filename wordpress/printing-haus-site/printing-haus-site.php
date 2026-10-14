<?php
/**
 * Plugin Name: Printing Haus Site
 * Description: Loads the Printing Haus brand stylesheet for the Bricks templates and gives the WooCommerce checkout a calm, Shopify-style layout.
 * Version:     1.1.1
 * Author:      Printing Haus
 * Requires at least: 6.0
 * Requires PHP: 7.4
 *
 * Generated alongside bricks/build_homepage.py. assets/printinghaus.css is rebuilt by
 * that script; assets/checkout.css is edited by hand.
 */

defined( 'ABSPATH' ) || exit;

define( 'PH_SITE_VERSION', '1.1.1' );

/**
 * Styles. Priority 20 so they load after Bricks and WooCommerce and win ties.
 */
add_action( 'wp_enqueue_scripts', function () {
	$url = plugin_dir_url( __FILE__ ) . 'assets/';

	// Interim open-source fonts. Remove once licensed Tiempos + Neue Haas Grotesk are added in Bricks > Custom fonts.
	wp_enqueue_style( 'ph-site-fonts', 'https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400&display=swap', array(), null );
	wp_enqueue_style( 'ph-site', $url . 'printinghaus.css', array( 'ph-site-fonts' ), PH_SITE_VERSION );

	if ( ph_site_is_checkout() ) {
		wp_enqueue_style( 'ph-checkout', $url . 'checkout.css', array( 'ph-site' ), PH_SITE_VERSION );
		wp_enqueue_script( 'ph-checkout', $url . 'checkout.js', array( 'jquery', 'wc-checkout' ), PH_SITE_VERSION, true );
		wp_localize_script( 'ph-checkout', 'phCheckout', array(
			'emptyCode' => __( 'Please enter a discount code.', 'printing-haus-site' ),
		) );
	}
}, 20 );

/** True on the checkout form, not on the order-received or pay-for-order screens. */
function ph_site_is_checkout() {
	return function_exists( 'is_checkout' ) && is_checkout()
		&& ! is_wc_endpoint_url( 'order-received' ) && ! is_wc_endpoint_url( 'order-pay' );
}

/**
 * Checkout layout (classic WooCommerce checkout).
 * Left: your details, shipping address, payment. Right: order summary.
 */
add_action( 'init', function () {
	if ( ! class_exists( 'WooCommerce' ) ) {
		return;
	}

	// Move payment out of the summary column and under the address fields, as on Shopify.
	// WooCommerce refreshes the payment block by its class, so this keeps working with AJAX updates.
	if ( false !== has_action( 'woocommerce_checkout_order_review', 'woocommerce_checkout_payment' ) ) {
		remove_action( 'woocommerce_checkout_order_review', 'woocommerce_checkout_payment', 20 );
		add_action( 'woocommerce_checkout_after_customer_details', 'ph_site_payment_heading', 15 );
		add_action( 'woocommerce_checkout_after_customer_details', 'woocommerce_checkout_payment', 20 );
	}

	// "Order summary" heading inside the summary column (the default "Your order" heading is hidden in CSS).
	add_action( 'woocommerce_checkout_order_review', function () {
		echo '<h2 class="ph-co-heading ph-co-heading--summary">' . esc_html__( 'Order summary', 'printing-haus-site' ) . '</h2>';
	}, 5 );
}, 20 );

/**
 * Shipping options as a dropdown in the checkout summary (the cart page keeps WooCommerce's default).
 */
add_filter( 'wc_get_template', function ( $template, $template_name ) {
	if ( 'cart/cart-shipping.php' === $template_name && function_exists( 'is_checkout' ) && is_checkout() ) {
		return plugin_dir_path( __FILE__ ) . 'templates/cart-shipping.php';
	}
	return $template;
}, 10, 2 );

/**
 * Discount code: a button under shipping that slides open a code field (handled by assets/checkout.js).
 * Replaces the "Have a coupon?" bar above the form.
 */
add_action( 'init', function () {
	if ( ! class_exists( 'WooCommerce' ) ) {
		return;
	}
	remove_action( 'woocommerce_before_checkout_form', 'woocommerce_checkout_coupon_form', 10 );
	add_action( 'woocommerce_review_order_before_order_total', 'ph_site_coupon_row' );
}, 20 );

function ph_site_coupon_row() {
	if ( ! function_exists( 'wc_coupons_enabled' ) || ! wc_coupons_enabled() ) {
		return;
	}
	?>
	<tr class="ph-co-coupon">
		<td colspan="2">
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
		</td>
	</tr>
	<?php
}

function ph_site_payment_heading() {
	echo '<h2 class="ph-co-heading ph-co-heading--payment">' . esc_html__( 'Payment', 'printing-haus-site' ) . '</h2>';
}

/**
 * Product thumbnail beside each line in the order summary. A quantity badge appears only for
 * ordinary products bought more than once; Printing Haus Selector items show their print
 * quantity on their own line (e.g. "× 100").
 */
// Only inside the checkout summary table, so the header mini cart is left alone.
add_action( 'woocommerce_review_order_before_cart_contents', function () {
	$GLOBALS['ph_site_in_review'] = true;
} );
add_action( 'woocommerce_review_order_after_cart_contents', function () {
	$GLOBALS['ph_site_in_review'] = false;
} );

add_filter( 'woocommerce_cart_item_name', function ( $name, $cart_item, $cart_item_key ) {
	if ( empty( $GLOBALS['ph_site_in_review'] ) ) {
		return $name;
	}
	if ( empty( $cart_item['data'] ) || ! is_object( $cart_item['data'] ) ) {
		return $name;
	}
	$qty   = isset( $cart_item['quantity'] ) ? (int) $cart_item['quantity'] : 1;
	$badge = ( $qty > 1 && empty( $cart_item['phs'] ) )
		? '<span class="ph-co-badge" aria-hidden="true">' . esc_html( number_format_i18n( $qty ) ) . '</span>'
		: '';
	return '<span class="ph-co-item"><span class="ph-co-thumb">' . $cart_item['data']->get_image( 'woocommerce_thumbnail' ) . $badge
		. '</span><span class="ph-co-name">' . $name . '</span></span>';
}, 10, 3 );

/** Plain, standard button wording. */
add_filter( 'woocommerce_order_button_text', function () {
	return __( 'Pay now', 'printing-haus-site' );
} );

/** Clearer section names on the checkout form only. */
add_filter( 'gettext_woocommerce', function ( $translation, $text ) {
	if ( ! ph_site_is_checkout() && ! wp_doing_ajax() ) {
		return $translation;
	}
	switch ( $text ) {
		case 'Billing details':
			return __( 'Contact & billing', 'printing-haus-site' );
		case 'Billing &amp; Shipping':
			return __( 'Contact & delivery', 'printing-haus-site' );
	}
	return $translation;
}, 10, 2 );
