<?php
/**
 * Checkout shipping row as a dropdown (replaces WooCommerce's radio list on the checkout only).
 *
 * WooCommerce's checkout script already listens for changes on `select.shipping_method`
 * and refreshes the totals, so no extra JavaScript is needed for the select itself.
 *
 * Variables are the same as WooCommerce's cart/cart-shipping.php template.
 *
 * @var array  $available_methods
 * @var string $chosen_method
 * @var int    $index
 * @var string $package_name
 * @var bool   $show_package_details
 * @var string $package_details
 * @var bool   $has_calculated_shipping
 */

defined( 'ABSPATH' ) || exit;

$available_methods       = isset( $available_methods ) ? (array) $available_methods : array();
$chosen_method           = isset( $chosen_method ) ? (string) $chosen_method : '';
$index                   = isset( $index ) ? (int) $index : 0;
$has_calculated_shipping = ! empty( $has_calculated_shipping );
$field_id                = 'ph-shipping-method-' . $index;

if ( $available_methods && ! isset( $available_methods[ $chosen_method ] ) ) {
	$chosen_method = (string) key( $available_methods );
}

/** Option text: "Standard: $5.00", without the delivery estimate markup added by other plugins. */
$ph_option_text = static function ( $method ) {
	$label = wc_cart_totals_shipping_method_label( $method );
	$label = preg_replace( '#<br\s*/?>\s*<small[^>]*>.*?</small>#is', '', $label );
	return trim( html_entity_decode( wp_strip_all_tags( $label ), ENT_QUOTES, get_bloginfo( 'charset' ) ) );
};
?>
<tr class="woocommerce-shipping-totals shipping ph-co-shipping">
	<th><label for="<?php echo esc_attr( $field_id ); ?>"><?php echo wp_kses_post( $package_name ); ?></label></th>
	<td data-title="<?php echo esc_attr( $package_name ); ?>">
		<?php if ( $available_methods ) : ?>
			<?php if ( count( $available_methods ) > 1 ) : ?>
				<select name="shipping_method[<?php echo esc_attr( $index ); ?>]" data-index="<?php echo esc_attr( $index ); ?>" id="<?php echo esc_attr( $field_id ); ?>" class="shipping_method ph-co-select">
					<?php foreach ( $available_methods as $method ) : ?>
						<option value="<?php echo esc_attr( $method->id ); ?>" <?php selected( $method->id, $chosen_method ); ?>><?php echo esc_html( $ph_option_text( $method ) ); ?></option>
					<?php endforeach; ?>
				</select>
			<?php else : ?>
				<?php $only = reset( $available_methods ); ?>
				<input type="hidden" name="shipping_method[<?php echo esc_attr( $index ); ?>]" data-index="<?php echo esc_attr( $index ); ?>" id="<?php echo esc_attr( $field_id ); ?>" value="<?php echo esc_attr( $only->id ); ?>" class="shipping_method">
			<?php endif; ?>

			<?php
			// Under the dropdown: the delivery estimate for the chosen option (added by Printing Haus Selector),
			// or the full label when there is only one option.
			$ph_full = wc_cart_totals_shipping_method_label( $available_methods[ $chosen_method ] );
			$ph_eta  = preg_match( '#<small[^>]*>.*?</small>#is', $ph_full, $m ) ? $m[0] : '';
			$ph_show = count( $available_methods ) > 1 ? $ph_eta : $ph_full;
			ob_start();
			do_action( 'woocommerce_after_shipping_rate', $available_methods[ $chosen_method ], $index );
			$ph_after = ob_get_clean();
			if ( '' !== trim( $ph_show . $ph_after ) ) :
				?>
				<div class="ph-co-ship-detail"><?php echo wp_kses_post( $ph_show ); ?><?php echo $ph_after; // phpcs:ignore WordPress.Security.EscapeOutput -- output of other plugins' hooks ?></div>
			<?php endif; ?>
		<?php elseif ( ! $has_calculated_shipping ) : ?>
			<p class="ph-co-ship-note"><?php echo wp_kses_post( apply_filters( 'woocommerce_shipping_may_be_available_html', __( 'Enter your address to view shipping options.', 'woocommerce' ) ) ); ?></p>
		<?php else : ?>
			<p class="ph-co-ship-note"><?php echo wp_kses_post( apply_filters( 'woocommerce_no_shipping_available_html', __( 'There are no shipping options available. Please ensure that your address has been entered correctly, or contact us if you need any help.', 'woocommerce' ) ) ); ?></p>
		<?php endif; ?>

		<?php if ( ! empty( $show_package_details ) && ! empty( $package_details ) ) : ?>
			<p class="woocommerce-shipping-contents"><small><?php echo esc_html( $package_details ); ?></small></p>
		<?php endif; ?>
	</td>
</tr>
