/* Printing Haus cart: "Have a promo code?" link that slides open the Bricks coupon form.
 * The Bricks cart totals are re-rendered when the cart changes, so the link is re-attached
 * whenever the panel is replaced, and its open/closed state is kept. */
(function () {
  'use strict';
  var open = false;

  function apply(panel, form, btn) {
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    form.classList.toggle('is-open', open);
    var inner = form.querySelector('.coupon');
    if (inner) { inner.inert = !open; }
  }

  function setup() {
    var panels = document.querySelectorAll('body.woocommerce-cart .cart_totals');
    Array.prototype.forEach.call(panels, function (panel) {
      var form = panel.querySelector(':scope > .brxe-woocommerce-cart-coupon');
      if (!form || panel.querySelector(':scope > .ph-cart-promo')) { return; }
      if (!form.id) { form.id = 'ph-cart-coupon'; }

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ph-cart-promo';
      btn.textContent = 'Have a promo code?';
      btn.setAttribute('aria-controls', form.id);
      panel.insertBefore(btn, form);
      panel.classList.add('ph-cart-promo-ready');
      apply(panel, form, btn);

      btn.addEventListener('click', function () {
        open = !open;
        apply(panel, form, btn);
        if (open) {
          var input = form.querySelector('input[name="coupon_code"]');
          if (input) { setTimeout(function () { input.focus(); }, 200); }
        }
      });
    });
  }

  var queued = false;
  function queue() {
    if (queued) { return; }
    queued = true;
    requestAnimationFrame(function () { queued = false; setup(); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setup);
  } else {
    setup();
  }
  new MutationObserver(queue).observe(document.body, { childList: true, subtree: true });
})();
