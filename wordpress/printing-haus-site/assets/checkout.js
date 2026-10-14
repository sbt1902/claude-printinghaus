/* Printing Haus checkout: discount code panel in the order summary.
 * The summary table is re-rendered by WooCommerce after every update, so the panel's
 * open state and last message are kept here and restored on `updated_checkout`. */
(function ($) {
  'use strict';
  if (typeof wc_checkout_params === 'undefined') {
    return;
  }

  var state = { open: false, code: '', msg: '' };

  function render() {
    var $toggle = $('.ph-co-coupon__toggle');
    var $panel = $('.ph-co-coupon__panel');
    $toggle.attr('aria-expanded', state.open ? 'true' : 'false');
    $panel.toggleClass('is-open', state.open);
    $panel.find('.ph-co-coupon__inner').prop('inert', !state.open);
    $('#ph-co-coupon-code').val(state.code);
    $('.ph-co-coupon__msg').html(state.msg);
  }

  function apply() {
    var $input = $('#ph-co-coupon-code');
    var code = $.trim($input.val());
    state.code = code;
    if (!code) {
      state.msg = '<p class="ph-co-coupon__error">' + (window.phCheckout ? phCheckout.emptyCode : 'Please enter a discount code.') + '</p>';
      render();
      $input.trigger('focus');
      return;
    }
    var $btn = $('.ph-co-coupon__apply').prop('disabled', true);
    $.ajax({
      type: 'POST',
      url: wc_checkout_params.wc_ajax_url.toString().replace('%%endpoint%%', 'apply_coupon'),
      data: { security: wc_checkout_params.apply_coupon_nonce, coupon_code: code },
      dataType: 'html'
    }).done(function (html) {
      var failed = /woocommerce-error|is-error/.test(html);
      state.msg = html;
      if (!failed) {
        state.open = false;
        state.code = '';
      }
      render();
      $(document.body).trigger('applied_coupon_in_checkout', [code]);
      $(document.body).trigger('update_checkout', { update_shipping_method: false });
    }).always(function () {
      $btn.prop('disabled', false);
    });
  }

  $(document.body)
    .on('click', '.ph-co-coupon__toggle', function () {
      state.open = !state.open;
      state.msg = '';
      render();
      if (state.open) {
        setTimeout(function () { $('#ph-co-coupon-code').trigger('focus'); }, 200);
      }
    })
    .on('input', '#ph-co-coupon-code', function () {
      state.code = this.value;
    })
    .on('keydown', '#ph-co-coupon-code', function (e) {
      // Enter applies the code instead of submitting the whole checkout form.
      if (e.key === 'Enter') {
        e.preventDefault();
        apply();
      }
    })
    .on('click', '.ph-co-coupon__apply', apply)
    .on('updated_checkout', render);
})(jQuery);
