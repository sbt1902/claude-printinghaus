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

/* Printing Haus checkout: USPS address check dialog.
 * The server checks the delivery address when the customer clicks Pay now (includes/class-ph-address-check.php).
 * If USPS has a better version, checkout stops with a short error; this replaces that error with a dialog
 * where the customer picks the suggested or the entered address, then checkout continues. */
(function ($) {
  'use strict';
  if (typeof wc_checkout_params === 'undefined' || !window.phCheckout || !phCheckout.addressCheck) {
    return;
  }

  var COPY = {
    suggestion: {
      title: 'Confirm your address',
      text: 'USPS suggests a small change to your delivery address.'
    },
    missing_unit: {
      title: 'Add your apartment or suite?',
      text: 'This address has more than one unit. Add your apartment, suite or unit number so your order reaches you.'
    },
    unit_unconfirmed: {
      title: 'Check your apartment or suite',
      text: 'USPS found the building but couldn’t confirm the apartment or suite number.'
    },
    not_found: {
      title: 'We couldn’t find this address',
      text: 'USPS doesn’t recognize this address. Please check it, or continue if you’re sure it’s right.'
    }
  };

  var $dlg = null;
  var pending = null;

  function esc(s) { return $('<div>').text(s == null ? '' : String(s)).html(); }

  function lines(a) {
    var street = a.address_1 + (a.address_2 ? ', ' + a.address_2 : '');
    return esc(street) + '<br>' + esc(a.city + ', ' + a.state + ' ' + a.postcode);
  }

  function field(group, name) {
    return $('form.checkout [name="' + group + '_' + name + '"]');
  }

  function fill(group, a) {
    ['address_1', 'address_2', 'city', 'postcode'].forEach(function (f) {
      field(group, f).val(a[f] || '').trigger('input').trigger('change');
    });
    field(group, 'state').val(a.state).trigger('change');
  }

  function keepAsEntered(hash) {
    var $form = $('form.checkout');
    var $input = $form.find('input[name="' + phCheckout.addressConfirm + '"]');
    if (!$input.length) {
      $input = $('<input type="hidden">').attr('name', phCheckout.addressConfirm).appendTo($form);
    }
    $input.val(hash);
  }

  // Submit once WooCommerce has finished refreshing totals for any changed fields.
  function submit(waitForUpdate) {
    var done = false;
    function go() {
      if (done) { return; }
      done = true;
      $('form.checkout').trigger('submit');
    }
    if (waitForUpdate) {
      $(document.body).one('updated_checkout', go);
      setTimeout(go, 2500);
    } else {
      go();
    }
  }

  function edit(fieldName) {
    close();
    var $f = field(pending.group, fieldName || 'address_1');
    if ($f.length) {
      $('html, body').animate({ scrollTop: Math.max(0, $f.offset().top - 120) }, 200);
      $f.trigger('focus');
    }
  }

  function close() {
    if ($dlg && $dlg[0].open) { $dlg[0].close(); }
  }

  function build() {
    $dlg = $(
      '<dialog class="ph-addr" aria-labelledby="ph-addr-title" aria-describedby="ph-addr-text">' +
        '<form method="dialog" class="ph-addr__inner">' +
          '<button type="button" class="ph-addr__close" aria-label="Close">&times;</button>' +
          '<h2 class="ph-addr__title" id="ph-addr-title"></h2>' +
          '<p class="ph-addr__text" id="ph-addr-text"></p>' +
          '<div class="ph-addr__body"></div>' +
          '<div class="ph-addr__actions"></div>' +
        '</form>' +
      '</dialog>'
    ).appendTo('body');
    $dlg.on('click', '.ph-addr__close', function () { edit(); });
    $dlg.on('cancel', function (e) { e.preventDefault(); edit(); });
  }

  function show(p) {
    pending = p;
    if (!$dlg) { build(); }
    var copy = COPY[p.type] || COPY.not_found;
    $dlg.find('.ph-addr__title').text(copy.title);
    $dlg.find('.ph-addr__text').text(copy.text);
    var $body = $dlg.find('.ph-addr__body').empty();
    var $actions = $dlg.find('.ph-addr__actions').empty();

    if (p.type === 'suggestion' && p.suggested) {
      $body.append(
        '<fieldset class="ph-addr__choices"><legend class="screen-reader-text">Delivery address</legend>' +
          '<label class="ph-addr__choice"><input type="radio" name="ph-addr-choice" value="suggested" checked>' +
            '<span><strong>Suggested</strong><span class="ph-addr__lines">' + lines(p.suggested) + '</span></span></label>' +
          '<label class="ph-addr__choice"><input type="radio" name="ph-addr-choice" value="entered">' +
            '<span><strong>As entered</strong><span class="ph-addr__lines">' + lines(p.entered) + '</span></span></label>' +
        '</fieldset>'
      );
      $('<button type="button" class="ph-addr__primary">Use this address</button>').appendTo($actions).on('click', function () {
        if ($body.find('input[name="ph-addr-choice"]:checked').val() === 'suggested') {
          fill(p.group, p.suggested);
          close();
          submit(true);
        } else {
          keepAsEntered(p.hash);
          close();
          submit(false);
        }
      });
      $('<button type="button" class="ph-addr__secondary">Edit address</button>').appendTo($actions).on('click', function () { edit(); });
    } else {
      $body.append('<div class="ph-addr__entered">' + lines(p.entered) + '</div>');
      if (p.type === 'missing_unit' || p.type === 'unit_unconfirmed') {
        $('<button type="button" class="ph-addr__primary">' + (p.type === 'missing_unit' ? 'Add unit number' : 'Edit unit number') + '</button>')
          .appendTo($actions).on('click', function () { edit('address_2'); });
        $('<button type="button" class="ph-addr__secondary">Continue without</button>').appendTo($actions).on('click', function () {
          keepAsEntered(p.hash);
          close();
          submit(false);
        });
      } else {
        $('<button type="button" class="ph-addr__primary">Edit address</button>').appendTo($actions).on('click', function () { edit(); });
        $('<button type="button" class="ph-addr__secondary">Use as entered</button>').appendTo($actions).on('click', function () {
          keepAsEntered(p.hash);
          close();
          submit(false);
        });
      }
    }

    // Hide WooCommerce's short error: the dialog explains it.
    $('.woocommerce-NoticeGroup-checkout').filter(function () {
      return $(this).text().indexOf(phCheckout.addressMessage) !== -1 && $(this).find('li').length <= 1;
    }).remove();

    $dlg[0].showModal();
    $dlg.find('.ph-addr__primary').trigger('focus');
  }

  $(document.body).on('checkout_error', function (e, message) {
    var text = $('<div>').html(message || '').text();
    if (text.indexOf(phCheckout.addressMessage) === -1) {
      return;
    }
    $.ajax({
      url: wc_checkout_params.wc_ajax_url.toString().replace('%%endpoint%%', 'ph_address_pending'),
      dataType: 'json'
    }).done(function (res) {
      if (res && res.pending) {
        show(res.pending);
      }
    });
  });
})(jQuery);
