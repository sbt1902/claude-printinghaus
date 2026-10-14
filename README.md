# claude-printinghaus

The Printing Haus header, homepage and footer, built as **Bricks Builder** templates. They follow
the *Printing Haus Brand System, Vol. 01* and the *Website Design & Brand Voice Brief*.

| File | What it is |
| --- | --- |
| `bricks/printinghaus-header.bricks.json` | Header template (logo, Shop / Design Studio / About / Contact, Search, Account, Cart) |
| `bricks/printinghaus-homepage.bricks.json` | Homepage content, sections A–H |
| `bricks/printinghaus-product.bricks.json` | Single product template (WooCommerce) |
| `bricks/printinghaus-footer.bricks.json` | Footer template (contact, shipping, FAQs, artwork, returns, privacy, terms) |
| `bricks/printinghaus.css` | **The stylesheet.** Paste it into Bricks → Settings → Custom code → Custom CSS |
| `bricks/build_homepage.py` | Source of truth for copy, links and styles. Re-run it to regenerate all files |
| `preview/homepage.html`, `preview/product.html` | Static draft previews. Gray blocks and [bracketed] text are placeholders |

## Homepage sequence

| | Section | Content source |
| --- | --- | --- |
| A | **Hero**: "Make an Impression." with *Shop the Collection* and *Explore the Design Studio* | Brief copy, plus your hero photo |
| B | **Shop by category** | **Live**: a Bricks query loop over WooCommerce product categories (empty categories are hidden) |
| C | **Featured products** | **Live**: a query loop over WooCommerce products, showing the real name, image and price (Woo shows a price range only when the price varies) |
| D | **Paper & finishes** | Plain-language descriptions. Items marked [Confirm] need checking |
| E | **Design studio**: "An idea worth putting on paper." with *Tell Us About Your Project* | Brief copy |
| F | **Customer work** | Placeholder. Hide it until you have approved projects |
| G | **Material approach** | One verified statement (FSC certification is attributed to partners) plus placeholders |
| H | **Email sign-up**: "Notes from the Haus." | Bricks form. Connect it to your email platform |
| I | **Footer** | Separate template |

## Product page

The product page is built from WooCommerce's own Bricks elements, together with the **Printing Haus Selector**
plugin. The selector hooks into the Add to Cart element (`woocommerce_before_add_to_cart_button`), so it
appears inside the template automatically. It provides the option buttons, the live price, artwork upload with
file checks, *Design online*, and the delivery estimate. The template doesn't duplicate any of these.

1. **Summary:** breadcrumbs, gallery, category, name and the short description as an opening line.
   The product's own price stays hidden on configured products, because the selector shows the live total.
2. **Selector and Add to Cart:** the selector is restyled in `printinghaus.css` (rules starting `body .ph-phs .phs…`)
   with square option buttons, a serif total, and brand colors and rules. The plugin itself is unchanged.
3. **Ordering facts:** artwork, proof and delivery, written to match what the selector actually does.
4. **Design support:** "Need help with the artwork?" with a **Request Design Support** link.
5. **About this product** (the full Woo description) beside a plain-language **paper & finish guide**.
6. **FAQs:** native expanding questions that work with a keyboard.
7. **Related products:** WooCommerce related items. Selector products show "Priced to your specs".

To install: import `printinghaus-product.bricks.json`, then in **Template settings → Conditions**
apply it to *All products*. You can also apply it to one category first to test.
If the selector doesn't appear, add a Shortcode element with `[phs_selector]` above the Add to Cart element.

**Still to fill in:** the real proof process (the selector checks files, but it doesn't describe a proof step),
the [Confirm] finishes in the guide, and delivery times in each shipping method. The delivery estimate only
appears when those times are set.

## Visual system

- **Type:** Tiempos (editorial serif) for headlines and Neue Haas Grotesk for body, navigation and labels.
  Until the licensed fonts are added, the page uses Newsreader / Inter Tight, then Georgia / Helvetica.
- **Color:** warm neutrals (Paper `#F9F7F3`, Ink `#0A0A0A`, Sand `#E8E1D6`, Paper gray `#DEDAD3`).
  Oxblood is used once, for the design-studio section.
- **Controls:** rectangular buttons, thin rules and underlined text links. No pills, gradients, heavy
  shadows or scrolling slogans.
- **Motion:** only a gentle image zoom and underline on hover, and it turns off for visitors who
  have reduced motion turned on. Nothing important is shown only on hover.
- **Accessibility:** visible focus outlines, a labeled email field, buttons at least 44px tall, and no horizontal scrolling at 390px.

## Install in Bricks

1. **Stylesheet (required):** copy all of `bricks/printinghaus.css` into
   **Bricks → Settings → Custom code → Custom CSS** and save. All the styling lives in that file.
   Without it the templates show as plain unstyled text. (Alternatively, add it as a site-wide CSS snippet in WPCode.)
   If Bricks is set to load CSS from external files, click **Settings → Performance → Regenerate CSS files** afterwards.
2. **Import:** go to **Bricks → Templates → Import** and upload the JSON files. If you imported an
   earlier version, delete that one first.
3. **Header and footer (optional):** you can keep your existing header and footer. To use these instead, open each template, then in **Template settings → Conditions** set it to *Entire website*.
   - Choose your **approved logo** in each Logo element. The footer sits on black, so it needs a light version.
   - Create a WordPress menu (**Appearance → Menus**) with *Shop, Design Studio, About, Contact*, then select it
     in both Nav Menu elements. One is for desktop and one shows as a "Menu" toggle on mobile.
   - The Cart element uses Bricks' WooCommerce mini cart.
4. **Homepage:** open the Home page in Bricks and insert *Printing Haus - Homepage* from **Templates**.
5. **Featured products:** select the "Featured product loop" element and open its **Query** settings.
   Filter it to featured products (or a specific category), or pick the products by hand.
6. **Category images:** these come from each WooCommerce category's thumbnail (**Products → Categories**).
7. **Newsletter:** the form currently emails each sign-up to the site admin. In the form's
   **Actions**, connect Mailchimp, Sendinblue or a webhook instead.
8. **Links:** placeholder URLs are listed in `LINKS` in `build_homepage.py`. Change them there or in Bricks.

## Must be supplied before launch

**Assets**
- Approved logo files, in dark and light versions
- Hero product photo, plus the "[Shown: …]" caption naming the product, stock and finish
- Photos for the six paper and finish tiles and the studio section. These should show real products and
  finishes, not generated images, and any illustrative mockup should be labeled
- Licensed Tiempos and Neue Haas Grotesk web fonts (Klim and Adobe Fonts)

**Verified business information**
- Paper and finish tiles marked [Confirm]: smooth matte, textured and heavyweight stocks, foil and embossing.
  Raised spot UV comes from the brief, so it's assumed to be offered.
- Any extra design-studio services besides custom artwork, stationery and packaging
- Approved customer projects (section F), naming the product, stock and finish. Never invent these
- Two more specific, verified material and production practices (section G)
- Footer contact details: email, phone, address or service area
- Pages the footer links to: shipping, FAQs, artwork guidelines, returns and order issues, privacy, terms

**Already verified in the brief**
- "We work with printing partners that hold FSC certifications." This is attributed to partners only,
  no FSC mark is used, and it is not a headline message.
- "Part of Production Haus" appears only in the footer.

## Editing

```sh
python3 bricks/build_homepage.py   # rewrites all three JSON files + the preview
```
