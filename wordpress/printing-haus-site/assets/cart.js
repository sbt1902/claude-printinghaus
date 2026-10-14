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

/* Printing Haus cart: product image and name link back to the product page, plus an "Edit" link.
 * Selector items open with the same choices and artwork (Printing Haus Selector 0.7.2+);
 * the cart item key comes from each item's Remove link. */
(function () {
  'use strict';
  if (!window.phCart || !phCart.items) { return; }

  function keyFor(item) {
    var remove = item.querySelector('a[href*="remove_item="]');
    if (!remove) { return ''; }
    var m = remove.getAttribute('href').match(/[?&]remove_item=([^&#]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function linkify(node, url, label) {
    if (!node || node.closest('a') || node.dataset.phLinked) { return; }
    node.dataset.phLinked = '1';
    var a = document.createElement('a');
    a.href = url;
    a.className = 'ph-cart-link';
    if (label) { a.setAttribute('aria-label', label); }
    node.parentNode.insertBefore(a, node);
    a.appendChild(node);
  }

  function setup() {
    var items = document.querySelectorAll('body.woocommerce-cart .woocommerce-cart-form__cart-item');
    Array.prototype.forEach.call(items, function (item) {
      if (item.dataset.phLinks) { return; }
      var info = phCart.items[keyFor(item)];
      if (!info) { return; }
      item.dataset.phLinks = '1';

      var img = item.querySelector('img.brxe-image');
      var name = item.querySelector('.brxe-block > .brxe-text-basic:first-child');
      var title = name ? name.textContent.trim() : 'product';
      linkify(img, info.url, (info.edit ? 'Edit ' : 'View ') + title);
      linkify(name, info.url, '');

      if (info.edit) {
        var remove = item.querySelector('a[href*="remove_item="]');
        if (remove && !item.querySelector('.ph-cart-edit')) {
          var edit = document.createElement('a');
          edit.href = info.url;
          edit.className = 'ph-cart-edit';
          edit.textContent = 'Edit';
          edit.setAttribute('aria-label', 'Edit ' + title);
          remove.parentNode.insertBefore(edit, remove);
        }
      }
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
