#!/usr/bin/env python3
"""Build the Printing Haus header, homepage and footer as Bricks Builder templates.

Outputs:
  bricks/printinghaus-header.bricks.json    -> Bricks > Templates > Import (type: Header)
  bricks/printinghaus-homepage.bricks.json  -> Bricks > Templates > Import (type: Section/content)
  bricks/printinghaus-footer.bricks.json    -> Bricks > Templates > Import (type: Footer)
  bricks/printinghaus.css                   -> site-wide stylesheet (Bricks > Settings > Custom code)
  preview/homepage.html                     -> static preview of all three

Styling lives in ONE stylesheet, bricks/printinghaus.css, which is pasted into
Bricks > Settings > Custom code > Custom CSS. The templates only carry the
ph-* class names in each element's plain CSS classes field.

Categories and featured products are Bricks *query loops* over the live
WooCommerce catalog, so names, images and prices always come from the store.
The preview fills those loops with clearly labeled sample data.

Text in [square brackets] is a placeholder that must be supplied before launch.

  python3 bricks/build_homepage.py
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_PREVIEW = HERE.parent / "preview" / "homepage.html"

# ---------------------------------------------------------------------------
# Links: update to match the real WordPress / WooCommerce URLs
# ---------------------------------------------------------------------------
LINKS = {
    "home": "/",
    "shop": "/shop/",
    "studio": "/design-studio/",
    "studio_brief": "/design-studio/#project-form",
    "about": "/about/",
    "contact": "/contact/",
    "paper": "/paper-and-finishes/",
    "account": "/my-account/",
    "shipping": "/shipping/",
    "faq": "/faq/",
    "artwork": "/artwork-guidelines/",
    "returns": "/returns-and-order-issues/",
    "privacy": "/privacy-policy/",
    "terms": "/terms/",
}

# ---------------------------------------------------------------------------
# Brand tokens (Printing Haus Brand System Vol. 01 + website brief)
# ---------------------------------------------------------------------------
TOKENS = """
  --ph-paper: #F9F7F3;
  --ph-ink: #0A0A0A;
  --ph-sand: #E8E1D6;
  --ph-stone: #DEDAD3;
  --ph-rule: #CFC9BF;
  --ph-olive: #5F5E4F;
  --ph-muted: #5E5A54;
  --ph-oxblood: #54151B;
  --ph-blush: #E7C9D2;
  --ph-display: "Tiempos Headline", "Tiempos Text", "Newsreader", Georgia, "Times New Roman", serif;
  --ph-sans: "Neue Haas Grotesk Text", "neue-haas-grotesk-text", "Neue Haas Grotesk Display", "neue-haas-grotesk-display", "Inter Tight", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --ph-gutter: clamp(20px, 5vw, 64px);
  --ph-space: clamp(72px, 9vw, 136px);
  --ph-max: 1320px;
"""

BASE = f"""
%root% {{{TOKENS}
  box-sizing: border-box;
  width: 100%;
  background: var(--ph-paper);
  color: var(--ph-ink);
  font-family: var(--ph-sans);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}
%root% *, %root% *::before, %root% *::after {{ box-sizing: border-box; }}
:where(%root% a) {{ color: inherit; }}
%root% a:not(.ph-btn) {{ color: inherit; }}
%root% :where(h1, h2, h3, h4, p, li, label) {{ color: inherit; text-transform: none; }}
%root% a:focus-visible, %root% button:focus-visible, %root% input:focus-visible {{
  outline: 2px solid currentColor; outline-offset: 3px;
}}
"""

# ---------------------------------------------------------------------------
# Global classes: name -> CSS (%root% = the class selector)
# ---------------------------------------------------------------------------
CLASSES = {
    # Layout --------------------------------------------------------------
    "ph-section": BASE + """
%root% { padding: var(--ph-space) var(--ph-gutter); }
""",
    "ph-section--sand": "%root% { background: var(--ph-sand); }",
    "ph-section--oxblood": "%root% { background: var(--ph-oxblood); color: var(--ph-paper); }",
    "ph-section--flush": "%root% { padding-top: 0; }",
    "ph-container": "%root% { width: 100%; max-width: var(--ph-max); margin: 0 auto; padding: 0; } %root% > * { width: 100%; }",
    "ph-rule": "%root% { width: 100%; padding-top: var(--ph-space); border-top: 1px solid var(--ph-rule); }",

    # Type ----------------------------------------------------------------
    "ph-label": """
%root% {
  margin: 0 0 18px;
  font-family: var(--ph-sans);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.08em;
  line-height: 1.4;
  text-transform: uppercase;
  color: var(--ph-olive);
}
""",
    "ph-label--light": "%root% { color: var(--ph-blush); }",
    "ph-h2": """
%root% {
  margin: 0;
  max-width: 18ch;
  font-family: var(--ph-display);
  font-size: clamp(34px, 4.2vw, 56px);
  font-weight: 400;
  line-height: 1.04;
  letter-spacing: -0.015em;
}
""",
    "ph-h3": """
%root% { margin: 0; font-family: var(--ph-sans); font-size: 18px; font-weight: 500; line-height: 1.3; letter-spacing: -0.005em; }
""",
    "ph-body": "%root% { margin: 0; max-width: 46ch; font-size: 15px; line-height: 1.6; color: var(--ph-muted); }",
    "ph-body--light": "%root% { color: rgba(249,247,243,.82); }",
    "ph-lead": "%root% { margin: 0; max-width: 44ch; font-size: clamp(17px, 1.3vw, 19px); line-height: 1.55; }",
    "ph-link": """
%root% {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  font-size: 15px;
  font-weight: 500;
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 6px;
  transition: opacity .2s ease;
}
%root%:hover { opacity: .65; }
""",

    # Buttons (rectangular, quiet) ----------------------------------------
    "ph-btn": """
%root% {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  padding: 0 28px;
  border: 1px solid var(--ph-ink);
  border-radius: 0;
  font-family: var(--ph-sans);
  font-size: 15px;
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: normal;
  text-transform: none;
  text-decoration: none;
  cursor: pointer;
  transition: background .2s ease, color .2s ease, border-color .2s ease;
}
""",
    "ph-btn--dark": """
%root% { background: var(--ph-ink); color: var(--ph-paper); }
%root%:hover { background: #2E2B28; border-color: #2E2B28; }
""",
    "ph-btn--outline": """
%root% { background: transparent; color: var(--ph-ink); }
%root%:hover { background: var(--ph-ink); color: var(--ph-paper); }
""",
    "ph-btn--light": """
%root% { background: var(--ph-paper); color: var(--ph-ink); border-color: var(--ph-paper); }
%root%:hover { background: var(--ph-sand); border-color: var(--ph-sand); }
""",
    "ph-actions": "%root% { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 28px; margin-top: 36px; }",

    # Media slot: flat paper-gray block until a photo is chosen -----------
    "ph-media": """
%root% {
  position: relative;
  overflow: hidden;
  width: 100%;
  aspect-ratio: 4 / 5;
  background: var(--ph-stone);
}
%root% img {
  position: absolute; inset: 0; z-index: 1;
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform .8s cubic-bezier(.2,.7,.2,1);
}
@media (prefers-reduced-motion: reduce) { %root% img { transition: none; } }
""",
    "ph-media__label": """
%root% {
  position: absolute; left: 16px; bottom: 14px; right: 16px;
  margin: 0;
  font-size: 12px; line-height: 1.4;
  color: var(--ph-muted);
}
""",
    "ph-media--landscape": "%root% { aspect-ratio: 4 / 3; }",
    "ph-media--square": "%root% { aspect-ratio: 1 / 1; }",
    "ph-media--hero": "%root% { aspect-ratio: 6 / 5; }",
    "ph-caption": "%root% { margin: 12px 0 0; font-size: 13px; color: var(--ph-muted); }",

    # Header --------------------------------------------------------------
    "ph-header": BASE + """
%root% { padding: 0 var(--ph-gutter); border-bottom: 1px solid var(--ph-rule); }
""",
    "ph-header__bar": """
%root% {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 48px;
  width: 100%;
  min-height: 76px;
}
@media (max-width: 767px) { %root% { grid-template-columns: 1fr auto auto; gap: 16px; } }
""",
    "ph-logo": "%root% { display: inline-flex; align-items: center; } %root% img { height: 28px; width: auto; }",
    "ph-nav": """
%root% { font-size: 15px; }
%root% ul { display: flex; gap: 32px; margin: 0; padding: 0; list-style: none; }
%root% a { display: inline-block; padding: 6px 0; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color .2s ease; }
%root% a:hover, %root% .current-menu-item > a { border-bottom-color: currentColor; }
""",
    "ph-utility": """
%root% { display: flex; align-items: center; justify-content: flex-end; gap: 24px; font-size: 15px; }
%root% a { text-decoration: none; }
%root% a:hover { text-decoration: underline; text-underline-offset: 5px; }
""",
    "ph-hide-mobile": "@media (max-width: 767px) { %root% { display: none !important; } }",
    "ph-show-mobile-only": "@media (min-width: 768px) { %root% { display: none !important; } }",

    # Hero ----------------------------------------------------------------
    "ph-hero": "%root% { padding-top: clamp(40px, 6vw, 88px); padding-bottom: clamp(64px, 8vw, 120px); }",
    "ph-hero__grid": """
%root% {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: clamp(40px, 6vw, 96px);
  align-items: center;
}
@media (max-width: 991px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-hero__title": """
%root% {
  margin: 0;
  font-family: var(--ph-display);
  font-size: clamp(48px, 6.4vw, 92px);
  font-weight: 400;
  line-height: 0.98;
  letter-spacing: -0.025em;
}
""",
    "ph-hero__lead": "%root% { margin-top: 28px; max-width: 30ch; }",

    # Section head --------------------------------------------------------
    "ph-head": """
%root% {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px 48px;
  width: 100%;
  margin-bottom: clamp(36px, 4.5vw, 64px);
}
""",

    # Grids ---------------------------------------------------------------
    "ph-grid-3": """
%root% { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: clamp(32px, 4vw, 56px) clamp(16px, 2vw, 32px); width: 100%; }
@media (max-width: 767px) { %root% { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
""",
    "ph-grid-4": """
%root% { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(32px, 4vw, 48px) clamp(16px, 2vw, 28px); width: 100%; }
@media (max-width: 991px) { %root% { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
""",

    # Cards ---------------------------------------------------------------
    "ph-card": """
%root% { display: flex; flex-direction: column; gap: 6px; color: inherit; text-decoration: none; }
%root% .ph-media { margin-bottom: 14px; }
%root%:hover .ph-media img { transform: scale(1.03); }
%root%:hover .ph-h3 { text-decoration: underline; text-underline-offset: 5px; text-decoration-thickness: 1px; }
@media (prefers-reduced-motion: reduce) { %root%:hover .ph-media img { transform: none; } }
""",
    "ph-price": "%root% { margin: 0; font-size: 15px; color: var(--ph-muted); } %root% del { opacity: .6; margin-right: 6px; }",

    # Paper & finishes ----------------------------------------------------
    "ph-materials": """
%root% { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0 clamp(16px, 2vw, 32px); width: 100%; }
@media (max-width: 767px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-material": """
%root% { display: flex; flex-direction: column; gap: 8px; padding: 0 0 48px; }
%root% .ph-media { margin-bottom: 16px; }
""",
    "ph-material__group": "%root% { grid-column: 1 / -1; margin: 0; padding: 16px 0 24px; border-top: 1px solid var(--ph-rule); }",

    # Studio --------------------------------------------------------------
    "ph-split": """
%root% {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: clamp(40px, 7vw, 112px);
  align-items: center;
  width: 100%;
}
@media (max-width: 991px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-stack": "%root% { display: flex; flex-direction: column; align-items: flex-start; gap: 24px; }",
    "ph-list": """
%root% { width: 100%; max-width: 440px; margin: 8px 0 0; padding: 0; list-style: none; border-top: 1px solid rgba(249,247,243,.28); }
%root% li { padding: 14px 0; border-bottom: 1px solid rgba(249,247,243,.28); font-size: 15px; }
""",

    # Material approach ---------------------------------------------------
    "ph-approach": """
%root% { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: clamp(32px, 6vw, 96px); }
@media (max-width: 991px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-facts": """
%root% { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 32px clamp(24px, 3vw, 48px); }
@media (max-width: 600px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-fact": "%root% { display: flex; flex-direction: column; gap: 8px; padding-top: 18px; border-top: 1px solid var(--ph-rule); }",

    # Newsletter ----------------------------------------------------------
    "ph-signup": """
%root% { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 32px clamp(40px, 6vw, 96px); align-items: end; width: 100%; }
@media (max-width: 991px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-form": """
%root% { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px; align-items: end; width: 100%; }
%root% .form-group { margin: 0; padding: 0; width: 100%; }
%root% label { display: block; margin-bottom: 8px; font-size: 13px; font-weight: 500; }
%root% input[type=email] {
  width: 100%; min-height: 52px; padding: 0 16px;
  border: 1px solid var(--ph-ink); border-radius: 0; background: var(--ph-paper);
  font: inherit; font-size: 16px; color: var(--ph-ink);
}
%root% button[type=submit], %root% .bricks-button {
  min-height: 52px !important; padding: 0 28px !important; border: 1px solid var(--ph-ink) !important;
  border-radius: 0 !important; background: var(--ph-ink) !important; color: var(--ph-paper) !important;
  font-family: var(--ph-sans) !important; font-size: 15px !important; font-weight: 500 !important;
  letter-spacing: normal !important; text-transform: none !important; cursor: pointer;
}
%root% .submit-button-wrapper { margin: 0; }
@media (max-width: 480px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-small": "%root% { margin: 0; font-size: 13px; color: var(--ph-muted); }",

    # Footer --------------------------------------------------------------
    "ph-footer": BASE + """
%root% { padding: clamp(64px, 7vw, 104px) var(--ph-gutter) 32px; background: var(--ph-ink); color: var(--ph-paper); }
%root% a { text-decoration: none; }
%root% a:hover { text-decoration: underline; text-underline-offset: 4px; }
""",
    "ph-footer__grid": """
%root% { display: grid; grid-template-columns: 1.4fr repeat(3, minmax(0, 1fr)); gap: 48px clamp(24px, 3vw, 48px); width: 100%; }
@media (max-width: 991px) { %root% { grid-template-columns: repeat(2, minmax(0, 1fr)); } %root% > :first-child { grid-column: 1 / -1; } }
""",
    "ph-footer__col": "%root% { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; font-size: 15px; }",
    "ph-footer__head": "%root% { margin: 0 0 8px; font-size: 12px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; color: var(--ph-rule); }",
    "ph-footer__legal": """
%root% {
  display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px 32px;
  width: 100%;
  margin-top: clamp(56px, 6vw, 88px); padding-top: 24px;
  border-top: 1px solid rgba(249,247,243,.2);
  font-size: 13px; color: var(--ph-rule);
}
%root% p { margin: 0; }
%root% nav { display: flex; gap: 24px; }
""",
}


# ---------------------------------------------------------------------------
# Tiny element-tree DSL
# ---------------------------------------------------------------------------
def _id(seed: str) -> str:
    """Deterministic 6-char Bricks id, stable across rebuilds."""
    h = hashlib.sha1(seed.encode()).hexdigest()
    return "".join(chr(97 + int(c, 16) % 26) for c in h[:6])




class El:
    def __init__(self, name, classes="", children=None, label=None, preview=None, **settings):
        self.name = name
        self.classes = classes.split()
        self.children = children or []
        self.settings = settings
        self.label = label
        self.preview = preview  # loop sample rows, used by the preview only


def url(u):
    return {"type": "external", "url": u}


def dyn(tag):
    return {"type": "dynamic", "dynamicData": tag}


def section(classes, children, label):
    return El("section", "ph-section " + classes, children, label=label)


def container(children, classes="ph-container"):
    return El("container", classes, children)


def div(classes, children, label=None, **kw):
    return El("div", classes, children, label=label, **kw)


def link_block(classes, link, children, **kw):
    return El("div", classes, children, tag="a", link=link, **kw)


def heading(text, tag="h2", classes="ph-h2"):
    return El("heading", classes, text=text, tag=tag)


def text(html, classes="", tag="p"):
    if tag in ("p", "span", "div"):
        return El("text-basic", classes, text=html, tag=tag)
    # Other tags (ul, dl, details...) go through Basic Text's "Custom" tag option
    return El("text-basic", classes, text=html, tag="custom", customTag=tag)


def button(label, href, variant):
    # A styled text link rather than a Bricks Button element, so the site's
    # theme button styles (uppercase, colors) never override it.
    return El("text-link", "ph-btn " + variant, text=label, link=url(href))


def text_link(label, href, classes="ph-link"):
    return El("text-link", classes, text=label, link=url(href))


def media(variant="", note="", dynamic=None):
    """Photo slot. Static slots show a labeled placeholder until a photo is chosen
    (the photo covers the label); dynamic slots pull the image from WooCommerce."""
    kids = [] if dynamic else [text(f"[Photo: {note}]", "ph-media__label")]
    image = {"image": {"useDynamicData": dynamic, "size": "large"}} if dynamic else {}
    kids.append(El("image", "", label="Photo", **image))
    return div("ph-media " + variant, kids, label="Photo slot")


def section_head(label, title, aside=None, light=False):
    return div("ph-head", [
        div("", [text(label, "ph-label" + (" ph-label--light" if light else "")), heading(title)]),
        *(aside or []),
    ])


# ---------------------------------------------------------------------------
# HEADER  (Shop / Design Studio / About / Contact + search, account, cart)
# ---------------------------------------------------------------------------
HEADER = [
    El("section", "ph-header", [container([
        div("ph-header__bar", [
            El("logo", "ph-logo", label="Logo (choose the approved logo file)",
               link=url(LINKS["home"])),
            El("nav-menu", "ph-nav ph-hide-mobile",
               label="Primary menu: Shop / Design Studio / About / Contact"),
            div("ph-utility", [
                El("search", "ph-hide-mobile", searchType="overlay", label="Search"),
                text_link("Account", LINKS["account"], "ph-hide-mobile"),
                El("woocommerce-mini-cart", "", label="Cart"),
                El("nav-menu", "ph-show-mobile-only", label="Mobile menu (same WP menu)",
                   mobileMenu="always"),
            ]),
        ]),
    ])], label="Header", tag="custom", customTag="header"),
]

# ---------------------------------------------------------------------------
# HOMEPAGE  (brief sequence A-H; footer is its own template)
# ---------------------------------------------------------------------------
CATEGORY_SAMPLES = [{"{term_name}": "[Category from your store]"}] * 3
PRODUCT_SAMPLES = [{"{post_title}": "[Product name]",
                    "{woo_product_price}": "[Price from store]"}] * 4

# Plain-language material notes. [Confirm] items must be checked against
# what is actually offered before launch.
MATERIALS_PAPER = [
    ("[Confirm stock] Smooth matte",
     "A soft matte surface. Smooth to the touch, with even, true color.",
     "smooth matte stock in raking light"),
    ("[Confirm stock] Textured",
     "Paper with presence. A gentle texture you can feel under your fingertips.",
     "textured stock close-up, paper fibers visible"),
    ("[Confirm stock] Heavyweight",
     "A substantial stock with a visible edge, so your card feels considered in hand.",
     "stack of thick cards showing the edge"),
]
MATERIALS_FINISH = [
    ("Raised spot UV",
     "A little gloss where it counts. Raised spot UV adds shine and dimension to selected details.",
     "light catching raised spot UV"),
    ("[Confirm] Foil",
     "A metallic finish applied to selected parts of your design, so it catches the light.",
     "foil detail on a textured stock"),
    ("[Confirm] Embossing",
     "A raised impression pressed into the paper, so your design can be felt as well as seen.",
     "embossed detail in soft side light"),
]


def material(name, body, note):
    return div("ph-material", [
        media("ph-media--landscape", note),
        heading(name, "h3", "ph-h3"),
        text(body, "ph-body"),
    ])


HOME = [
    # A. Hero -------------------------------------------------------------
    section("ph-hero", [container([
        div("ph-hero__grid", [
            div("", [
                heading("Make an Impression.", "h1", "ph-hero__title"),
                text("Considered paper. Distinctive finishes. Print that feels like you.",
                     "ph-lead ph-hero__lead"),
                div("ph-actions", [
                    button("Shop the Collection", LINKS["shop"], "ph-btn--dark"),
                    text_link("Explore the Design Studio", LINKS["studio"]),
                ]),
            ]),
            div("", [
                media("ph-media--hero", "one strong product composition, e.g. business "
                      "cards showing their edge and raised spot UV in natural light"),
                text("[Shown: product name, stock and finish]", "ph-caption"),
            ]),
        ]),
    ])], "A. Hero"),

    # B. Shop by category (live WooCommerce categories) --------------------
    section("ph-section--flush", [container([
        section_head("Shop", "Shop by category",
                     [text_link("View all products", LINKS["shop"])]),
        div("ph-grid-3", [
            link_block("ph-card", dyn("{term_url}"), [
                media("", dynamic="{woo_product_cat_image}"),
                heading("{term_name}", "h3", "ph-h3"),
            ], hasLoop=True, label="Category loop (live WooCommerce product categories)",
               query={"objectType": "term", "taxonomy": ["product_cat"],
                      "number": "6", "hide_empty": True},
               preview=CATEGORY_SAMPLES),
        ]),
    ])], "B. Shop by category"),

    # C. Featured products (live WooCommerce products) ---------------------
    section("ph-section--flush", [container([
        div("ph-rule", [
            section_head("Featured", "A few favorites",
                         [text_link("Shop the Collection", LINKS["shop"])]),
            div("ph-grid-4", [
                link_block("ph-card", dyn("{post_url}"), [
                    media("ph-media--square", dynamic="{featured_image}"),
                    heading("{post_title}", "h3", "ph-h3"),
                    text("{woo_product_price}", "ph-price", tag="div"),
                ], hasLoop=True, label="Featured product loop (filter Query to featured products)",
                   query={"objectType": "post", "post_type": ["product"],
                          "posts_per_page": "4", "orderby": "menu_order", "order": "ASC"},
                   preview=PRODUCT_SAMPLES),
            ]),
        ]),
    ])], "C. Featured products"),

    # D. Paper & finishes --------------------------------------------------
    section("ph-section--sand", [container([
        section_head("Paper &amp; finishes", "Details you can feel",
                     [text("What each paper and finish looks and feels like, in plain "
                           "language. Not sure which to choose? We're happy to help.",
                           "ph-body")]),
        div("ph-materials", [
            text("Paper", "ph-label ph-material__group"),
            *[material(*m) for m in MATERIALS_PAPER],
            text("Finishes", "ph-label ph-material__group"),
            *[material(*m) for m in MATERIALS_FINISH],
        ]),
        div("ph-actions", [button("Explore Paper &amp; Finishes", LINKS["paper"], "ph-btn--outline")]),
    ])], "D. Paper & finishes"),

    # E. Design studio -----------------------------------------------------
    section("ph-section--oxblood", [container([
        div("ph-split", [
            div("ph-stack", [
                text("Design Studio", "ph-label ph-label--light"),
                heading("An idea worth putting on paper."),
                text("Something more individual? Our design studio brings a considered eye "
                     "to your next print project, from the first idea to the finishing detail.",
                     "ph-lead"),
                text("<li>Custom artwork</li><li>Stationery</li><li>Packaging</li>"
                     "<li>[Confirm any other studio services]</li>", "ph-list", tag="ul"),
                div("ph-actions", [button("Tell Us About Your Project", LINKS["studio_brief"],
                                          "ph-btn--light")]),
            ]),
            media("", "studio table with proofs, paper samples and a finished stationery set"),
        ]),
    ])], "E. Design studio"),

    # F. Customer work (approved projects only) ----------------------------
    section("", [container([
        section_head("Customer work", "Recently printed",
                     [text("[Approved customer projects only. Hide this section in Bricks "
                           "until you have them.]", "ph-small")]),
        div("ph-grid-3", [
            div("ph-card", [
                media("", "approved customer project"),
                heading("[Customer or project name]", "h3", "ph-h3"),
                text("[Product &middot; stock &middot; finish]", "ph-body"),
            ]) for _ in range(3)
        ]),
    ])], "F. Customer work"),

    # G. Material approach -------------------------------------------------
    section("ph-section--flush", [container([
        div("ph-rule ph-approach", [
            div("", [
                text("Material approach", "ph-label"),
                heading("How we choose and print"),
            ]),
            div("ph-facts", [
                div("ph-fact", [
                    heading("Paper first", "h3", "ph-h3"),
                    text("We choose each stock for how it prints and how it feels in hand, "
                         "then match the finish to the paper.", "ph-body"),
                ]),
                div("ph-fact", [
                    heading("Our printing partners", "h3", "ph-h3"),
                    text("We work with printing partners that hold FSC certifications. If "
                         "certified paper matters for your project, ask us about the options.",
                         "ph-body"),
                ]),
                div("ph-fact", [
                    heading("[Verified practice]", "h3", "ph-h3"),
                    text("[Add a specific, verified sourcing or production practice.]", "ph-body"),
                ]),
                div("ph-fact", [
                    heading("[Verified practice]", "h3", "ph-h3"),
                    text("[Add a specific, verified sourcing or production practice.]", "ph-body"),
                ]),
            ]),
        ]),
    ])], "G. Material approach"),

    # H. Email sign-up -----------------------------------------------------
    section("ph-section--sand", [container([
        div("ph-signup", [
            div("ph-stack", [
                heading("Notes from the Haus."),
                text("New collections, paper discoveries, and studio news. "
                     "A considered addition to your inbox.", "ph-lead"),
            ]),
            div("ph-stack", [
                El("form", "ph-form", label="Newsletter form (connect your email platform)",
                   fields=[{"id": _id("field:email"), "type": "email", "label": "Email address",
                            "placeholder": "", "required": True}],
                   submitButtonText="Subscribe",
                   actions=["email"],
                   emailSubject="New newsletter sign-up",
                   emailTo="admin_email",
                   successMessage="Thank you. You're on the list."),
                text("Unsubscribe at any time. See our "
                     f"<a href=\"{LINKS['privacy']}\">privacy policy</a>.", "ph-small"),
            ]),
        ]),
    ])], "H. Email sign-up"),
]

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
def footer_col(title, links):
    return div("ph-footer__col", [text(title, "ph-footer__head"),
                                  *[text_link(l, u, "") for l, u in links]])


FOOTER = [
    El("section", "ph-footer", [container([
        div("ph-footer__grid", [
            div("ph-footer__col", [
                El("logo", "ph-logo", label="Logo (choose the approved light logo file)",
                   link=url(LINKS["home"])),
                text("[Email address]<br>[Phone number]<br>[Studio address or service area]",
                     "ph-body ph-body--light"),
            ]),
            footer_col("Shop", [("All products", LINKS["shop"]),
                                ("Paper &amp; finishes", LINKS["paper"]),
                                ("Design Studio", LINKS["studio"])]),
            footer_col("Help", [("Shipping information", LINKS["shipping"]),
                                ("FAQs", LINKS["faq"]),
                                ("Artwork guidelines", LINKS["artwork"]),
                                ("Returns &amp; order issues", LINKS["returns"])]),
            footer_col("Printing Haus", [("About", LINKS["about"]),
                                         ("Contact", LINKS["contact"]),
                                         ("Account", LINKS["account"])]),
        ]),
        div("ph-footer__legal", [
            text("&copy; {current_date:Y} Printing Haus. Part of Production Haus.", ""),
            div("", [text_link("Privacy policy", LINKS["privacy"], ""),
                     text_link("Terms", LINKS["terms"], "")], tag="custom", customTag="nav"),
        ]),
    ])], label="Footer", tag="custom", customTag="footer"),
]

# ---------------------------------------------------------------------------
# PRODUCT PAGE  (WooCommerce single product, brief section 7)
# Woo elements render the real product: gallery, title, price, options,
# upload field and Add to Cart all come from the store.
# ---------------------------------------------------------------------------
CLASSES.update({
    "ph-crumbs": """
%root% { margin: 0 0 clamp(24px, 3vw, 40px); font-size: 13px; color: var(--ph-muted); }
%root% a { text-decoration: none; }
%root% a:hover { text-decoration: underline; text-underline-offset: 4px; }
""",
    "ph-pdp": """
%root% {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  gap: clamp(32px, 6vw, 96px);
  align-items: start;
  width: 100%;
}
@media (max-width: 991px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-pdp__gallery": """
%root% .woocommerce-product-gallery { margin: 0; width: 100% !important; float: none !important; }
%root% .woocommerce-product-gallery__image img, %root% .woocommerce-product-gallery img { width: 100%; height: auto; display: block; background: var(--ph-stone); }
%root% .flex-control-thumbs { display: grid !important; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; margin: 8px 0 0 !important; padding: 0; list-style: none; }
%root% .flex-control-thumbs li { width: auto !important; float: none !important; margin: 0 !important; }
%root% .flex-control-thumbs img { opacity: .55; cursor: pointer; transition: opacity .2s ease; }
%root% .flex-control-thumbs img.flex-active, %root% .flex-control-thumbs img:hover { opacity: 1; }
""",
    "ph-pdp__summary": "%root% { display: flex; flex-direction: column; align-items: stretch; gap: 0; }",
    "ph-pdp__title": """
%root%, %root% h1 {
  margin: 0 0 12px;
  font-family: var(--ph-display);
  font-size: clamp(36px, 3.6vw, 52px);
  font-weight: 400;
  line-height: 1.05;
  letter-spacing: -0.015em;
  text-transform: none;
  color: var(--ph-ink);
}
""",
    "ph-pdp__price": """
%root%, %root% .price { margin: 0 0 20px; font-size: 18px; font-weight: 500; color: var(--ph-ink); }
%root%:empty, %root% .price:empty { display: none; }
%root% del { opacity: .55; margin-right: 8px; font-weight: 400; }
%root% ins { text-decoration: none; }
""",
    "ph-pdp__intro": "%root%, %root% p { margin: 0 0 28px; font-size: 17px; line-height: 1.6; max-width: 46ch; }",
    "ph-pdp__buy": """
%root% { padding: 24px 0 28px; border-top: 1px solid var(--ph-rule); }
%root% form.cart { display: flex; flex-wrap: wrap; gap: 12px; margin: 0; }
%root% table.variations { width: 100%; margin: 0 0 8px; border: 0; border-collapse: collapse; }
%root% table.variations tr { display: block; margin-bottom: 16px; }
%root% table.variations th, %root% table.variations td { display: block; padding: 0; border: 0; text-align: left; background: none; }
/* Only WooCommerce's native variation fields and quantity are styled here.
   The Printing Haus options plugin renders and styles its own controls. */
%root% table.variations label { display: block; margin: 0 0 8px; font-size: 13px; font-weight: 500; color: var(--ph-ink); text-transform: none; letter-spacing: normal; }
%root% table.variations select, %root% .quantity input.qty {
  min-height: 48px; padding: 0 14px;
  border: 1px solid var(--ph-ink); border-radius: 0; background: var(--ph-paper);
  font-family: var(--ph-sans); font-size: 16px; color: var(--ph-ink);
}
%root% table.variations select { width: 100%; }
%root% .reset_variations { display: inline-block; margin-top: 8px; font-size: 13px; }
%root% .single_variation_wrap, %root% .woocommerce-variation-add-to-cart { width: 100%; }
%root% .woocommerce-variation-add-to-cart { display: flex; flex-wrap: wrap; gap: 12px; }
%root% .woocommerce-variation-price { margin: 0 0 12px; font-size: 18px; font-weight: 500; }
%root% .quantity input.qty { width: 88px; text-align: center; padding: 0 8px; }
%root% .single_add_to_cart_button {
  flex: 1 1 200px; min-height: 52px !important; padding: 0 28px !important;
  border: 1px solid var(--ph-ink) !important; border-radius: 0 !important;
  background: var(--ph-ink) !important; color: var(--ph-paper) !important;
  font-family: var(--ph-sans) !important; font-size: 15px !important; font-weight: 500 !important;
  letter-spacing: normal !important; text-transform: none !important; cursor: pointer;
}
%root% .single_add_to_cart_button:hover { background: #2E2B28 !important; border-color: #2E2B28 !important; }
%root% .single_add_to_cart_button.disabled { opacity: .45; cursor: not-allowed; }
%root% .stock { width: 100%; margin: 0 0 8px; font-size: 14px; }
""",
    # Printing Haus Selector plugin (.phs): brand skin over its own stylesheet
    "ph-phs": """
%root% .phs {
  --phs-ink: var(--ph-ink); --phs-mute: var(--ph-muted); --phs-line: var(--ph-rule);
  --phs-bg: var(--ph-paper); --phs-accent: var(--ph-ink);
  width: 100%; margin: 0 0 20px; padding: 0; border: 0; background: transparent;
  font-family: var(--ph-sans); font-size: 15px; line-height: 1.5; color: var(--ph-ink);
}
%root% .phs-field { margin: 0 0 22px; }
%root% .phs-label { margin: 0 0 10px; font-size: 13px; font-weight: 500; letter-spacing: normal; text-transform: none; }
%root% .phs-help { font-size: 13px; color: var(--ph-muted); }
%root% .phs-chips { gap: 8px; }
%root% .phs-chip span {
  display: flex; flex-direction: column; justify-content: center;
  min-height: 46px; padding: 10px 16px;
  border: 1px solid var(--ph-rule); border-radius: 0; background: var(--ph-paper);
  font-size: 15px; transition: border-color .15s ease, background-color .15s ease;
}
%root% .phs-chip:hover span { border-color: var(--ph-ink); }
%root% .phs-chip input:checked + span { border-color: var(--ph-ink); background: var(--ph-ink); color: var(--ph-paper); }
%root% .phs-chip small { font-size: 12px; opacity: .75; }
%root% .phs-number input, %root% .phs-ship-row select, %root% .phs-ship-row input {
  min-height: 46px; padding: 0 14px; border: 1px solid var(--ph-ink); border-radius: 0;
  background: var(--ph-paper); font: inherit; font-size: 16px; color: var(--ph-ink);
}
%root% .phs-quote { margin-top: 8px; padding-top: 20px; border-top: 1px solid var(--ph-rule); }
%root% .phs-total { font-family: var(--ph-display); font-size: 36px; font-weight: 400; letter-spacing: -0.01em; line-height: 1; }
%root% .phs-unit { font-size: 14px; color: var(--ph-muted); }
%root% .phs-art { margin-top: 24px; padding: 20px; border: 1px solid var(--ph-rule); background: var(--ph-paper); }
%root% .phs-art-title { margin: 0 0 12px; font-size: 13px; font-weight: 500; }
%root% .phs-drop { min-height: 88px; display: flex; align-items: center; justify-content: center; padding: 16px; border: 1px dashed var(--ph-olive); color: var(--ph-muted); font-size: 14px; }
%root% .phs-drop:hover, %root% .phs-drop.is-over { border-color: var(--ph-ink); color: var(--ph-ink); background: var(--ph-sand); }
%root% .phs-btn { min-height: 46px; padding: 0 20px; border: 1px solid var(--ph-ink); border-radius: 0; background: transparent; color: var(--ph-ink); font-size: 15px; font-weight: 500; }
%root% .phs-btn:hover { background: var(--ph-ink); color: var(--ph-paper); }
%root% .phs-badge { padding: 2px 8px; font-size: 12px; font-weight: 500; }
%root% .phs-ship { margin-top: 24px; }
%root% .phs-ship-rates li { border-bottom-color: var(--ph-rule); }
%root% .phs-eta { color: var(--ph-muted); opacity: 1; }
%root% .phs-pill { border-radius: 2px; border-color: var(--ph-rule); background: var(--ph-paper); }
%root% .phs-payin4 { color: var(--ph-muted); opacity: 1; }
""",
    "ph-pdp__facts": """
%root% { margin: 0; padding: 0; border-top: 1px solid var(--ph-rule); }
%root% > div { display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--ph-rule); }
%root% dt { margin: 0; font-size: 13px; font-weight: 500; }
%root% dd { margin: 0; font-size: 14px; line-height: 1.55; color: var(--ph-muted); }
%root% dd a { text-decoration: underline; text-underline-offset: 3px; }
@media (max-width: 480px) { %root% > div { grid-template-columns: 1fr; gap: 4px; } }
""",
    "ph-pdp__help": """
%root% { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; margin-top: 28px; padding: 22px 24px; background: var(--ph-sand); }
""",
    "ph-pdp__content": """
%root% { max-width: 62ch; font-size: 16px; line-height: 1.7; }
%root% p { margin: 0 0 1em; }
%root% h2, %root% h3 { font-family: var(--ph-sans); font-size: 18px; font-weight: 500; margin: 1.6em 0 .5em; }
%root% ul { padding-left: 1.2em; }
""",
    "ph-glossary": """
%root% { margin: 0; border-top: 1px solid var(--ph-rule); }
%root% > div { padding: 18px 0; border-bottom: 1px solid var(--ph-rule); }
%root% dt { margin: 0 0 4px; font-size: 16px; font-weight: 500; }
%root% dd { margin: 0; font-size: 15px; line-height: 1.6; color: var(--ph-muted); }
""",
    "ph-faq": """
%root% { width: 100%; max-width: 860px; border-top: 1px solid var(--ph-rule); }
%root% details { border-bottom: 1px solid var(--ph-rule); }
%root% summary {
  display: flex; justify-content: space-between; align-items: center; gap: 24px;
  min-height: 64px; padding: 16px 0; cursor: pointer; list-style: none;
  font-size: 17px; font-weight: 500;
}
%root% summary::-webkit-details-marker { display: none; }
%root% summary::after { content: "+"; font-size: 22px; font-weight: 400; line-height: 1; }
%root% details[open] summary::after { content: "\\2212"; }
%root% summary:focus-visible { outline: 2px solid currentColor; outline-offset: 4px; }
%root% details p { margin: 0 0 20px; max-width: 64ch; font-size: 15px; line-height: 1.65; color: var(--ph-muted); }
%root% details a { text-decoration: underline; text-underline-offset: 3px; }
""",
    "ph-related": """
%root% { width: 100%; }
%root% .related > h2, %root% .upsells > h2 { display: none; }
%root% ul.products { display: grid !important; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 40px 24px; margin: 0 !important; padding: 0; list-style: none; }
%root% ul.products::before, %root% ul.products::after { display: none !important; }
%root% ul.products li.product { width: auto !important; margin: 0 !important; float: none !important; padding: 0; text-align: left; }
%root% li.product a { text-decoration: none; color: inherit; }
%root% li.product img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; margin: 0 0 14px; background: var(--ph-stone); }
%root% .woocommerce-loop-product__title { margin: 0 0 4px; padding: 0; font-family: var(--ph-sans); font-size: 16px; font-weight: 500; text-transform: none; letter-spacing: normal; }
%root% li.product .price { display: block; font-size: 15px; color: var(--ph-muted); }
%root% li.product .button, %root% li.product .star-rating { display: none; }
@media (max-width: 991px) { %root% ul.products { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
""",
})


def fact(term, html):
    return text(f"<dt>{term}</dt><dd>{html}</dd>", "", tag="div")


def gloss(term, html):
    return text(f"<dt>{term}</dt><dd>{html}</dd>", "", tag="div")


def faq(q, a):
    return text(f"<summary>{q}</summary><p>{a}</p>", "", tag="details")


PRODUCT = [
    # Product summary -----------------------------------------------------
    section("ph-hero", [container([
        El("woocommerce-breadcrumbs", "ph-crumbs", label="Breadcrumbs"),
        div("ph-pdp", [
            div("ph-pdp__gallery", [El("product-gallery", "", label="Product gallery (real product photos)")]),
            div("ph-pdp__summary", [
                text("{post_terms_product_cat:plain}", "ph-label"),
                El("product-title", "ph-pdp__title", label="Product name"),
                El("product-price", "ph-pdp__price", label="Price (updates with the selection)"),
                El("product-short-description", "ph-pdp__intro",
                   label="Opening description (WooCommerce short description)"),
                div("ph-pdp__buy ph-phs", [El("product-add-to-cart", "",
                                       label="Add to Cart: Printing Haus Selector renders options, price, artwork and delivery here")]),
                div("ph-pdp__facts", [
                    fact("Artwork",
                         "Upload your file in the artwork box above. It lists the file types this product "
                         "accepts, and we check your file as it uploads. Size and bleed are covered in our "
                         f"<a href=\"{LINKS['artwork']}\">artwork guidelines</a>."),
                    fact("Proof",
                         "[Describe your actual proof step, e.g. when a proof is sent and how to approve it.]"),
                    fact("Delivery",
                         "Enter your ZIP code above for a delivery estimate, production included. Final "
                         f"shipping is confirmed at checkout. See <a href=\"{LINKS['shipping']}\">shipping information</a>."),
                ], tag="custom", customTag="dl", label="Ordering facts (keep visible)"),
                div("ph-pdp__help", [
                    heading("Need help with the artwork?", "h2", "ph-h3"),
                    text("Our design studio can set up your file or design something new.", "ph-body"),
                    text_link("Request Design Support", LINKS["studio_brief"]),
                ]),
            ]),
        ]),
    ])], "Product summary"),

    # Description + paper & finish guide ----------------------------------
    section("ph-section--sand", [container([
        div("ph-approach", [
            div("ph-stack", [
                text("About this product", "ph-label"),
                El("product-content", "ph-pdp__content", label="Full description (WooCommerce)"),
            ]),
            div("ph-stack", [
                text("Paper &amp; finish guide", "ph-label"),
                div("ph-glossary", [
                    gloss("Raised spot UV",
                          "A little gloss where it counts. Raised spot UV adds shine and dimension to "
                          "selected details: a glossy, raised finish you can see and feel."),
                    gloss("[Confirm] Foil",
                          "A metallic finish applied to selected parts of your design, so it catches the light."),
                    gloss("[Confirm] Embossing",
                          "A raised impression pressed into the paper, so your design can be felt as well as seen."),
                    gloss("Paper weight",
                          "How thick and substantial a stock feels. Heavier stocks feel more rigid in hand "
                          "and show more of their edge."),
                ], tag="custom", customTag="dl"),
                text_link("Explore Paper &amp; Finishes", LINKS["paper"]),
            ]),
        ]),
    ])], "Description & guide"),

    # FAQs ----------------------------------------------------------------
    section("", [container([
        section_head("Questions", "Before you order"),
        div("ph-faq", [
            faq("What file types can I upload?",
                "The artwork box lists the file types and maximum file size for each product. We check "
                "your file as it uploads and tell you if anything needs attention. Our "
                f"<a href=\"{LINKS['artwork']}\">artwork guidelines</a> cover size, bleed and resolution."),
            faq("Will I see a proof before you print?",
                "[Describe your actual proof process.]"),
            faq("How long will my order take?",
                "Enter your ZIP code on the product page for a delivery estimate. It includes production "
                "time, and your final shipping is confirmed at checkout. See "
                f"<a href=\"{LINKS['shipping']}\">shipping information</a>."),
            faq("I don't have artwork yet. Can you help?",
                "Yes. Our design studio can set up your file or design something new. "
                f"<a href=\"{LINKS['studio_brief']}\">Request design support</a>."),
            faq("What if something is wrong with my order?",
                f"Contact us and we'll look into it. See <a href=\"{LINKS['returns']}\">returns &amp; order issues</a>."),
        ]),
    ])], "FAQs"),

    # Related -------------------------------------------------------------
    section("ph-section--flush", [container([
        div("ph-rule", [
            section_head("More to explore", "You may also like"),
            div("ph-related", [El("product-related", "", label="Related products (WooCommerce)")]),
        ]),
    ])], "Related products"),
]


TEMPLATES = {
    "header": ("Printing Haus - Header", "header", HEADER),
    "homepage": ("Printing Haus - Homepage", "content", HOME),
    "footer": ("Printing Haus - Footer", "footer", FOOTER),
    "product": ("Printing Haus - Product", "wc_product", PRODUCT),
}


# ---------------------------------------------------------------------------
# Serialise to Bricks JSON
# ---------------------------------------------------------------------------
def used_classes(nodes):
    used = set()

    def go(n):
        used.update(n.classes)
        for c in n.children:
            go(c)
    for n in nodes:
        go(n)
    missing = used - CLASSES.keys()
    assert not missing, f"classes used but not defined: {missing}"
    return used


def flatten(nodes, prefix):
    out, counter = [], [0]

    def walk(node, parent):
        counter[0] += 1
        eid = _id(f"{prefix}:{counter[0]}:{node.name}")
        entry = {"id": eid, "name": node.name, "parent": parent, "children": [],
                 "settings": dict(node.settings)}
        if node.classes:
            # Plain "CSS classes" field (Style > CSS), written straight into the
            # HTML. Not global classes: those are not carried over by template import.
            entry["settings"]["_cssClasses"] = " ".join(node.classes)
        if node.label:
            entry["label"] = node.label
        out.append(entry)
        entry["children"] = [walk(c, eid) for c in node.children]
        return eid

    for n in nodes:
        walk(n, 0)
    ids = [e["id"] for e in out]
    assert len(ids) == len(set(ids)), "duplicate element ids"
    return out


def build_json(key):
    title, ttype, nodes = TEMPLATES[key]
    used_classes(nodes)  # asserts every class has CSS
    return {
        "title": title,
        "templateType": ttype,
        # Bricks keeps header and footer templates under their own key, not "content"
        {"header": "header", "footer": "footer"}.get(ttype, "content"): flatten(nodes, key),
        "pageSettings": [],
        "templateSettings": [],
        "version": "1.10",
    }


# ---------------------------------------------------------------------------
# Static preview (mimics Bricks' markup and base element styles)
# ---------------------------------------------------------------------------
BRICKS_BASE = """
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:#F9F7F3}
img{max-width:100%;display:block}
.brxe-section{display:flex;flex-direction:column;align-items:center;width:100%}
.brxe-container{display:flex;flex-direction:column;align-items:flex-start;width:1100px;max-width:100%;margin:0 auto}
.brxe-button,.brxe-text-link{display:inline-flex}
.brxe-logo{font:600 14px/1 Helvetica,Arial,sans-serif;letter-spacing:.12em;border:1px dashed currentColor;padding:8px 10px;text-decoration:none}
.phs-chips{display:flex;flex-wrap:wrap}.phs-chip{position:relative}.phs-chip input{position:absolute;opacity:0;inset:0;margin:0}
.phs-quote{display:flex;justify-content:space-between;align-items:baseline}.phs-art-actions,.phs-ship-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}.phs-drop{flex:1 1 14rem}
.preview-flag{position:fixed;right:12px;bottom:12px;z-index:9;padding:8px 12px;background:#0A0A0A;color:#F9F7F3;font:12px/1.3 Helvetica,Arial,sans-serif}
"""


def render(node, sub=None):
    if node.preview and sub is None:
        return "".join(render(node, row) for row in node.preview)

    def s_(v):
        for k, r in (sub or {}).items():
            v = v.replace(k, r)
        return (v.replace("{current_date:Y}", "2026")
                 .replace("{post_terms_product_cat:plain}", "[Category]"))

    classes = " ".join(["brxe-" + node.name] + node.classes)
    s, n = node.settings, node.name
    inner = "".join(render(c, sub) for c in node.children)
    href = s.get("link", {}).get("url", "#")
    if n == "heading":
        return f'<{s["tag"]} class="{classes}">{s_(s["text"])}</{s["tag"]}>'
    if n == "text-basic":
        t = s.get("customTag") or s.get("tag", "p")
        return f'<{t} class="{classes}">{s_(s["text"])}</{t}>'
    if n in ("button", "text-link"):
        return f'<a class="{classes}" href="{href}">{s["text"]}</a>'
    if n == "image":
        return ""
    if n == "logo":
        return f'<a class="{classes}" href="/">[LOGO]</a>'
    if n == "nav-menu":
        if s.get("mobileMenu") == "always":
            return f'<a class="{classes}" href="#">Menu</a>'
        items = "".join(f'<li><a href="#">{x}</a></li>'
                        for x in ["Shop", "Design Studio", "About", "Contact"])
        return f'<nav class="{classes}" aria-label="Primary"><ul>{items}</ul></nav>'
    if n == "search":
        return f'<a class="{classes}" href="#">Search</a>'
    if n == "woocommerce-mini-cart":
        return f'<a class="{classes}" href="#">Cart (0)</a>'
    if n in WOO_MOCK:
        return f'<div class="{classes}">{WOO_MOCK[n]}</div>'
    if n == "form":
        f = s["fields"][0]
        return (f'<form class="{classes}" onsubmit="return false"><div class="form-group">'
                f'<label for="pv-email">{f["label"]}</label><input id="pv-email" type="email" required>'
                f'</div><div class="submit-button-wrapper"><button type="submit">'
                f'{s["submitButtonText"]}</button></div></form>')
    if s.get("tag") == "a":
        return f'<a class="{classes}" href="{href}">{inner}</a>'
    tag = s.get("customTag") or ("section" if n == "section" else "div")
    return f'<{tag} class="{classes}">{inner}</{tag}>'


def build_css():
    """One site-wide stylesheet. `body .class` outranks Bricks' own element
    defaults and theme styles without needing !important everywhere."""
    head = ("@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500"
            "&family=Newsreader:opsz,wght@6..72,400&display=swap');\n"
            "/* Printing Haus - site styles for the ph-* Bricks templates.\n"
            "   Interim open-source fonts above; remove the @import once licensed\n"
            "   Tiempos + Neue Haas Grotesk are added under Bricks > Custom fonts.\n"
            "   Generated by bricks/build_homepage.py - edit there and rebuild.\n"
            "   Paste into Bricks > Settings > Custom code > Custom CSS. */\n")
    return head + "\n".join(
        f"/* {name} */\n" + c.strip().replace("%root%", f"body .{name}") + "\n"
        for name, c in CLASSES.items())


WOO_MOCK = {
    "woocommerce-breadcrumbs": '<nav><a href="#">Home</a> / <a href="#">[Category]</a> / [Product name]</nav>',
    "product-gallery": ('<div class="woocommerce-product-gallery"><div class="ph-media ph-media--square">'
                        '<p class="ph-media__label">[Real product photo from WooCommerce]</p></div>'
                        '<ol class="flex-control-thumbs">' + '<li><img alt="" style="aspect-ratio:1"></li>' * 5 + '</ol></div>'),
    "product-title": '<h1 class="product_title">[Product name]</h1>',
    # Printing Haus Selector returns an empty price on configured products and shows its live total instead
    "product-price": '<p class="price"></p>',
    "product-short-description": ('<p>[Short description, e.g. "A small introduction, thoughtfully made. '
                                  'Choose your paper and finish, then make it yours."]</p>'),
    "product-add-to-cart": (
        '<form class="cart" onsubmit="return false"><div class="phs">'
        '<div class="phs-field"><p class="phs-label">Size</p><div class="phs-chips">'
        '<label class="phs-chip"><input type="radio" name="s" checked><span>[Size A]</span></label>'
        '<label class="phs-chip"><input type="radio" name="s"><span>[Size B]</span></label></div></div>'
        '<div class="phs-field"><p class="phs-label">Paper</p><div class="phs-chips">'
        + "".join(f'<label class="phs-chip"><input type="radio" name="p"{" checked" if x == "A" else ""}>'
                  f'<span>[Stock {x}]<small>[weight]</small></span></label>' for x in "ABC")
        + '</div></div>'
        '<div class="phs-field"><p class="phs-label">Finish</p><div class="phs-chips">'
        '<label class="phs-chip"><input type="radio" name="f" checked><span>None</span></label>'
        '<label class="phs-chip"><input type="radio" name="f"><span>Raised spot UV</span></label></div></div>'
        '<div class="phs-field"><p class="phs-label">Quantity</p><div class="phs-chips">'
        + "".join(f'<label class="phs-chip"><input type="radio" name="q"{" checked" if q == 100 else ""}>'
                  f'<span>{q}</span></label>' for q in (50, 100, 250, 500))
        + '</div></div>'
        '<div class="phs-quote"><span class="phs-total">[$00.00]</span><span class="phs-unit">[$0.00 each]</span></div>'
        '<div class="phs-art"><p class="phs-art-title">Your artwork</p><div class="phs-art-actions">'
        '<label class="phs-drop">Drop a file here or choose one (PDF, PNG, JPG, JPEG, TIF, TIFF, AI, INDD, up to [N] MB)</label>'
        '<button type="button" class="phs-btn">Design online</button></div></div>'
        '<div class="phs-ship"><p class="phs-art-title">Delivery estimate</p><div class="phs-ship-row">'
        '<select aria-label="Country"><option>United States</option></select>'
        '<input class="phs-ship-zip" placeholder="ZIP or postal code" aria-label="ZIP or postal code"></div></div>'
        '</div><div class="woocommerce-variation-add-to-cart">'
        '<button type="submit" class="single_add_to_cart_button button">Add to Cart</button></div></form>'),
    "product-content": '<p>[Full product description from WooCommerce: sizes, stocks, finishes and what is included.]</p>',
    "product-related": ('<section class="related products"><h2>Related products</h2><ul class="products">'
                        + '<li class="product"><a href="#"><img alt=""><h2 class="woocommerce-loop-product__title">'
                          '[Product name]</h2><span class="price">[Price]</span></a></li>' * 4 + '</ul></section>'),
}


def page(title, nodes):
    css = build_css()
    body = "".join(render(n) for n in nodes)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500&family=Newsreader:opsz,wght@6..72,400&display=swap">
<style>{BRICKS_BASE}
{css}</style></head>
<body>{body}<div class="preview-flag">Draft preview &middot; [bracketed] text and gray blocks are placeholders</div></body></html>
"""


if __name__ == "__main__":
    for key in TEMPLATES:
        path = HERE / f"printinghaus-{key}.bricks.json"
        path.write_text(json.dumps(build_json(key), indent=2, ensure_ascii=False) + "\n")
        print("wrote", path.relative_to(HERE.parent))
    (HERE / "printinghaus.css").write_text(build_css())
    print("wrote bricks/printinghaus.css")
    OUT_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    OUT_PREVIEW.write_text(page("Printing Haus Homepage", HEADER + HOME + FOOTER))
    (OUT_PREVIEW.parent / "product.html").write_text(page("Printing Haus Product", HEADER + PRODUCT + FOOTER))
    print("wrote preview/homepage.html and preview/product.html")
