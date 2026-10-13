#!/usr/bin/env python3
"""Build the Printing Haus homepage as a Bricks Builder template.

Outputs (next to this script):
  printinghaus-homepage.bricks.json  -> import in WP admin: Bricks > Templates > Import
  ../preview/homepage.html           -> static preview of the same element tree

All styling lives in Bricks *global classes* (custom CSS using %root%), so it
travels with the template and stays editable in the builder under
Style > CSS classes. Edit copy, links and classes here, then re-run:

  python3 bricks/build_homepage.py
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "printinghaus-homepage.bricks.json"
OUT_PREVIEW = HERE.parent / "preview" / "homepage.html"

# ---------------------------------------------------------------------------
# Links: update to match the real WordPress / WooCommerce URLs
# ---------------------------------------------------------------------------
LINKS = {
    "shop": "/shop/",
    "quote": "/contact/",
    "consult": "/design-studio/",
    "business_cards": "/product-category/business-cards/",
    "invitations": "/product-category/invitations/",
    "packaging": "/product-category/packaging/",
    "art_prints": "/product-category/art-prints/",
    "studio": "/design-studio/",
    "finishes": "/finishes/",
    "instagram": "https://www.instagram.com/",
}

# ---------------------------------------------------------------------------
# Brand tokens (Printing Haus Brand System, Vol. 01)
# ---------------------------------------------------------------------------
TOKENS = """
  --ph-paper: #F9F7F3;
  --ph-ink: #0A0A0A;
  --ph-sand: #E8E1D6;
  --ph-stone: #D6D1CA;
  --ph-olive: #6B6A5A;
  --ph-muted: #777069;
  --ph-oxblood: #54151B;
  --ph-midnight: #1636D9;
  --ph-blush: #E7C9D2;
  --ph-chartreuse: #C6D600;
  --ph-sans: "Neue Haas Grotesk Display", "neue-haas-grotesk-display", "Neue Haas Grotesk Text", "neue-haas-grotesk-text", "Inter Tight", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --ph-serif: "Tiempos Headline", "Tiempos Text", "Newsreader", Georgia, "Times New Roman", serif;
  --ph-gutter: clamp(20px, 5vw, 72px);
  --ph-space: clamp(80px, 11vw, 160px);
  --ph-max: 1360px;
"""

# ---------------------------------------------------------------------------
# Global classes: name -> CSS (%root% = the class selector)
# ---------------------------------------------------------------------------
CLASSES = {
    # Layout --------------------------------------------------------------
    "ph-section": f"""
%root% {{{TOKENS}
  width: 100%;
  padding: var(--ph-space) var(--ph-gutter);
  background: var(--ph-paper);
  color: var(--ph-ink);
  font-family: var(--ph-sans);
  -webkit-font-smoothing: antialiased;
}}
%root% *, %root% *::before, %root% *::after {{ box-sizing: border-box; }}
:where(%root% a) {{ color: inherit; }}
""",
    "ph-section--sand": "%root% { background: var(--ph-sand); }",
    "ph-section--ink": "%root% { background: var(--ph-ink); color: var(--ph-paper); }",
    "ph-section--oxblood": "%root% { background: var(--ph-oxblood); color: var(--ph-paper); }",
    "ph-section--tight": "%root% { padding-top: 0; padding-bottom: 0; }",
    "ph-container": """
%root% {
  width: 100%;
  max-width: var(--ph-max);
  margin: 0 auto;
}
""",
    # Type ----------------------------------------------------------------
    "ph-eyebrow": """
%root% {
  margin: 0 0 28px;
  font-family: var(--ph-sans);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ph-olive);
}
""",
    "ph-eyebrow--light": "%root% { color: var(--ph-stone); }",
    "ph-h2": """
%root% {
  margin: 0;
  max-width: 16ch;
  font-family: var(--ph-sans);
  font-size: clamp(36px, 5vw, 72px);
  font-weight: 500;
  line-height: 0.98;
  letter-spacing: -0.035em;
}
%root% em { font-family: var(--ph-serif); font-style: italic; font-weight: 400; letter-spacing: -0.02em; }
""",
    "ph-lead": """
%root% {
  margin: 0;
  max-width: 46ch;
  font-size: clamp(17px, 1.4vw, 20px);
  line-height: 1.55;
  color: inherit;
  opacity: 0.82;
}
""",
    "ph-link": """
%root% {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-decoration: none;
  border-bottom: 1px solid currentColor;
  padding-bottom: 4px;
  transition: gap .25s ease, opacity .25s ease;
}
%root%:hover { gap: 16px; opacity: .7; }
""",
    # Buttons -------------------------------------------------------------
    "ph-btn": """
%root% {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 54px;
  padding: 0 30px;
  border: 1px solid var(--ph-ink);
  border-radius: 999px;
  font-family: var(--ph-sans);
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.01em;
  line-height: 1;
  text-decoration: none;
  cursor: pointer;
  transition: background .25s ease, color .25s ease, border-color .25s ease, transform .25s ease;
}
%root%:hover { transform: translateY(-2px); }
%root%:focus-visible { outline: 2px solid var(--ph-midnight); outline-offset: 3px; }
""",
    "ph-btn--dark": """
%root% { background: var(--ph-ink); color: var(--ph-paper); }
%root%:hover { background: var(--ph-oxblood); border-color: var(--ph-oxblood); color: var(--ph-paper); }
""",
    "ph-btn--ghost": """
%root% { background: transparent; color: var(--ph-ink); }
%root%:hover { background: var(--ph-ink); color: var(--ph-paper); }
""",
    "ph-btn--light": """
%root% { background: var(--ph-paper); color: var(--ph-ink); border-color: var(--ph-paper); }
%root%:hover { background: var(--ph-blush); border-color: var(--ph-blush); color: var(--ph-ink); }
""",
    "ph-btn--ghost-light": """
%root% { background: transparent; color: var(--ph-paper); border-color: rgba(249,247,243,.5); }
%root%:hover { background: var(--ph-paper); color: var(--ph-ink); border-color: var(--ph-paper); }
""",
    "ph-actions": """
%root% { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 40px; }
""",
    # Media placeholder (shows a warm paper tone until a photo is chosen) --
    "ph-media": """
%root% {
  position: relative;
  overflow: hidden;
  width: 100%;
  aspect-ratio: 4 / 5;
  border-radius: 2px;
  background:
    radial-gradient(120% 80% at 20% 15%, rgba(255,255,255,.55), transparent 60%),
    linear-gradient(160deg, var(--ph-sand) 0%, var(--ph-stone) 100%);
}
%root% img {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 1.2s cubic-bezier(.2,.7,.2,1);
}
""",
    "ph-media--blush": "%root% { background: linear-gradient(160deg, #F1DDE3 0%, var(--ph-blush) 100%); }",
    "ph-media--olive": "%root% { background: linear-gradient(160deg, #8C8B7A 0%, var(--ph-olive) 100%); }",
    "ph-media--oxblood": "%root% { background: linear-gradient(160deg, #6E2229 0%, #3E0F14 100%); }",
    "ph-media--wide": "%root% { aspect-ratio: 16 / 10; }",
    "ph-media--square": "%root% { aspect-ratio: 1 / 1; }",
    # Hero ----------------------------------------------------------------
    "ph-hero": """
%root% { padding-top: clamp(48px, 7vw, 110px); padding-bottom: clamp(56px, 7vw, 110px); }
""",
    "ph-hero__grid": """
%root% {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
  gap: clamp(40px, 6vw, 96px);
  align-items: end;
}
@media (max-width: 991px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-hero__title": """
%root% {
  margin: 0;
  font-family: var(--ph-sans);
  font-size: clamp(54px, 8.4vw, 132px);
  font-weight: 500;
  line-height: 0.9;
  letter-spacing: -0.05em;
  text-transform: uppercase;
}
%root% em {
  display: block;
  font-family: var(--ph-serif);
  font-style: italic;
  font-weight: 400;
  text-transform: none;
  letter-spacing: -0.03em;
  color: var(--ph-oxblood);
}
""",
    "ph-hero__lead": "%root% { margin-top: 36px; }",
    "ph-hero__visual": """
%root% { position: relative; }
""",
    "ph-hero__tag": """
%root% {
  position: absolute;
  left: clamp(-56px, -4vw, -16px);
  bottom: 40px;
  max-width: 230px;
  padding: 22px 24px;
  background: var(--ph-paper);
  box-shadow: 0 30px 60px -30px rgba(10,10,10,.35);
}
%root% p { margin: 0; }
@media (max-width: 991px) { %root% { left: 16px; bottom: 16px; } }
""",
    "ph-hero__tag-title": """
%root% { margin: 0 0 6px; font-family: var(--ph-serif); font-style: italic; font-size: 24px; line-height: 1.1; }
""",
    "ph-hero__tag-text": "%root% { font-size: 13px; line-height: 1.5; color: var(--ph-muted); }",
    "ph-hero__points": """
%root% {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  margin-top: clamp(56px, 7vw, 96px);
  padding-top: 28px;
  border-top: 1px solid var(--ph-stone);
}
@media (max-width: 767px) { %root% { grid-template-columns: 1fr; gap: 16px; } }
""",
    "ph-point": """
%root% { margin: 0; font-size: 14px; line-height: 1.5; color: var(--ph-muted); }
%root% strong { display: block; margin-bottom: 4px; font-weight: 500; color: var(--ph-ink); letter-spacing: 0.01em; }
""",
    # Finishes marquee ----------------------------------------------------
    "ph-marquee": """
%root% {
  overflow: hidden;
  padding: 22px 0;
  white-space: nowrap;
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
          mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
}
""",
    "ph-marquee__track": """
%root% {
  display: inline-flex;
  margin: 0;
  font-size: clamp(18px, 2vw, 26px);
  letter-spacing: -0.01em;
  animation: ph-marquee 38s linear infinite;
}
%root% span { padding: 0 28px; }
%root% span:nth-child(even) { font-family: var(--ph-serif); font-style: italic; color: var(--ph-stone); }
%root% i { font-style: normal; color: var(--ph-chartreuse); }
@keyframes ph-marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@media (prefers-reduced-motion: reduce) { %root% { animation: none; } }
""",
    # Section head --------------------------------------------------------
    "ph-head": """
%root% {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-end;
  gap: 32px;
  margin-bottom: clamp(48px, 6vw, 80px);
}
""",
    "ph-head__aside": "%root% { display: flex; flex-direction: column; align-items: flex-start; gap: 24px; max-width: 420px; }",
    # Collection cards ----------------------------------------------------
    "ph-cards": """
%root% {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: clamp(28px, 3vw, 44px) clamp(16px, 2vw, 28px);
}
%root% > :nth-child(-n+2) { grid-column: span 3; }
%root% > :nth-child(n+3) { grid-column: span 2; }
%root% > :nth-child(-n+2) .ph-media { aspect-ratio: 5 / 4; }
@media (max-width: 991px) {
  %root% > :nth-child(n) { grid-column: span 3; }
  %root% > :last-child { grid-column: 1 / -1; }
  %root% > :last-child .ph-media { aspect-ratio: 16 / 9; }
}
@media (max-width: 600px) { %root% > :nth-child(n) { grid-column: 1 / -1; } }
""",
    "ph-card": """
%root% {
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: inherit;
  text-decoration: none;
}
%root%:hover .ph-media img { transform: scale(1.04); }
%root%:hover .ph-card__more { gap: 16px; }
""",
    "ph-card__meta": """
%root% { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; }
""",
    "ph-card__title": """
%root% { margin: 0; font-size: clamp(20px, 1.8vw, 26px); font-weight: 500; letter-spacing: -0.02em; line-height: 1.15; }
""",
    "ph-card__num": "%root% { margin: 0; font-size: 12px; letter-spacing: .16em; color: var(--ph-muted); }",
    "ph-card__text": "%root% { margin: 0; max-width: 40ch; font-size: 15px; line-height: 1.55; color: var(--ph-muted); }",
    "ph-card__more": """
%root% { display: inline-flex; gap: 10px; font-size: 14px; font-weight: 500; transition: gap .25s ease; }
""",
    # Statement / split ---------------------------------------------------
    "ph-split": """
%root% {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: clamp(40px, 7vw, 120px);
  align-items: center;
}
@media (max-width: 991px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-split--reverse": """
%root% > :first-child { order: 2; }
@media (max-width: 991px) { %root% > :first-child { order: 0; } }
""",
    "ph-statement": """
%root% {
  margin: 0;
  font-family: var(--ph-serif);
  font-size: clamp(44px, 6.4vw, 104px);
  font-weight: 400;
  line-height: 0.98;
  letter-spacing: -0.03em;
}
%root% em { font-style: italic; color: var(--ph-blush); }
""",
    "ph-stack": "%root% { display: flex; flex-direction: column; align-items: flex-start; gap: 28px; }",
    # Details grid --------------------------------------------------------
    "ph-details": """
%root% {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border-top: 1px solid rgba(10,10,10,.18);
}
@media (max-width: 991px) { %root% { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 600px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-detail": """
%root% {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 32px 28px 8px 0;
}
%root% + %root% { padding-left: 28px; border-left: 1px solid rgba(10,10,10,.18); }
@media (max-width: 991px) {
  %root%, %root% + %root% { padding: 32px 24px 24px 0; border-left: 0; border-bottom: 1px solid rgba(10,10,10,.18); }
}
""",
    "ph-detail__num": """
%root% { margin: 0 0 24px; font-family: var(--ph-serif); font-style: italic; font-size: 40px; line-height: 1; color: var(--ph-oxblood); }
""",
    "ph-detail__title": "%root% { margin: 0; font-size: 20px; font-weight: 500; letter-spacing: -0.01em; }",
    "ph-detail__text": "%root% { margin: 0; font-size: 15px; line-height: 1.6; color: #4C4A44; }",
    # Process -------------------------------------------------------------
    "ph-steps": """
%root% {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(24px, 3vw, 48px);
  counter-reset: ph-step;
}
@media (max-width: 991px) { %root% { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 600px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-step": """
%root% { display: flex; flex-direction: column; gap: 12px; padding-top: 22px; border-top: 2px solid var(--ph-ink); }
""",
    "ph-step__num": "%root% { margin: 0 0 18px; font-size: 13px; letter-spacing: .16em; color: var(--ph-muted); }",
    # Studio --------------------------------------------------------------
    "ph-tags": "%root% { display: flex; flex-wrap: wrap; gap: 10px; margin: 0; padding: 0; list-style: none; }",
    "ph-tag": """
%root% {
  margin: 0;
  padding: 9px 16px;
  border: 1px solid var(--ph-stone);
  border-radius: 999px;
  font-size: 13px;
  letter-spacing: 0.02em;
  color: var(--ph-ink);
  background: rgba(255,255,255,.4);
}
""",
    # Closing CTA ---------------------------------------------------------
    "ph-cta": "%root% { text-align: center; }",
    "ph-cta__inner": "%root% { display: flex; flex-direction: column; align-items: center; }",
    "ph-cta__title": """
%root% {
  margin: 0;
  font-family: var(--ph-sans);
  font-size: clamp(48px, 9vw, 150px);
  font-weight: 500;
  line-height: 0.88;
  letter-spacing: -0.055em;
  text-transform: uppercase;
}
%root% em {
  font-family: var(--ph-serif);
  font-style: italic;
  font-weight: 400;
  text-transform: none;
  letter-spacing: -0.03em;
  color: var(--ph-blush);
}
""",
    "ph-cta__lead": "%root% { margin: 36px auto 0; text-align: center; }",
    "ph-actions--center": "%root% { justify-content: center; }",
}


# ---------------------------------------------------------------------------
# Tiny element-tree DSL
# ---------------------------------------------------------------------------
def _id(seed: str) -> str:
    """Deterministic 6-char Bricks id (lowercase letters), stable across rebuilds."""
    h = hashlib.sha1(seed.encode()).hexdigest()
    return "".join(chr(97 + int(c, 16) % 26) for c in h[:6])


class_ids = {name: _id("class:" + name) for name in CLASSES}


class El:
    def __init__(self, name, classes="", children=None, **settings):
        self.name = name
        self.classes = classes.split()
        self.children = children or []
        self.settings = settings
        self.label = settings.pop("label", None)


def section(classes, children, label):
    return El("section", "ph-section " + classes, children, label=label)


def container(children, classes="ph-container"):
    return El("container", classes, children)


def div(classes, children, tag=None, label=None):
    kw = {"label": label} if label else {}
    if tag:
        kw["tag"] = "custom"
        kw["customTag"] = tag
    return El("div", classes, children, **kw)


def link_block(classes, url, children):
    return El("div", classes, children, tag="a", link={"type": "external", "url": url})


def heading(text, tag="h2", classes=""):
    return El("heading", classes, text=text, tag=tag)


def text(html, classes="", tag="p"):
    return El("text-basic", classes, text=html, tag=tag)


def button(label, url, classes):
    return El("button", "ph-btn " + classes, text=label, link={"type": "external", "url": url})


def text_link(label, url, classes="ph-link"):
    return El("text-link", classes, text=label, link={"type": "external", "url": url})


def media(variant="", alt=""):
    """A photo slot. Pick an image in Bricks; until then the warm placeholder shows."""
    return div("ph-media " + variant, [El("image", "", altText=alt, label="Photo")],
               label="Photo slot")


ARROW = "&rarr;"

# ---------------------------------------------------------------------------
# Page content (brand voice: refined, warm, design-literate, quietly playful)
# ---------------------------------------------------------------------------
def collection_card(i, title, blurb, url, variant, alt):
    return link_block("ph-card", url, [
        media(variant, alt),
        div("ph-card__meta", [
            heading(title, "h3", "ph-card__title"),
            text(f"{i:02d}", "ph-card__num"),
        ]),
        text(blurb, "ph-card__text"),
        text(f"Explore {ARROW}", "ph-card__more", tag="span"),
    ])


def detail(num, title, body):
    return div("ph-detail", [
        text(num, "ph-detail__num"),
        heading(title, "h3", "ph-detail__title"),
        text(body, "ph-detail__text"),
    ])


def step(num, title, body):
    return div("ph-step", [
        text(f"Step {num}", "ph-step__num"),
        heading(title, "h3", "ph-detail__title"),
        text(body, "ph-detail__text"),
    ])


FINISHES = ["Letterpress", "Foil stamping", "Blind embossing", "Painted edges",
            "Duplex stocks", "Cotton paper", "Die cutting", "Spot gloss"]
marquee_html = "".join(
    f"<span>{f}</span><i aria-hidden=\"true\">/</i>" for f in FINISHES * 2
)

PAGE = [
    # 1. Hero -------------------------------------------------------------
    section("ph-hero", [container([
        div("ph-hero__grid", [
            div("", [
                text("Printing Haus &mdash; Design-led print studio", "ph-eyebrow"),
                heading("Good ideas look <em>better printed.</em>", "h1", "ph-hero__title"),
                text("Business cards, stationery, invitations and packaging, thoughtfully "
                     "produced on beautiful paper. Made to be held onto.",
                     "ph-lead ph-hero__lead"),
                div("ph-actions", [
                    button("Start your order", LINKS["shop"], "ph-btn--dark"),
                    button("Book a design consult", LINKS["consult"], "ph-btn--ghost"),
                ]),
            ]),
            div("ph-hero__visual", [
                media("", "Letterpress business cards on textured cotton paper in soft daylight"),
                div("ph-hero__tag", [
                    text("Details you can feel.", "ph-hero__tag-title"),
                    text("Foil, emboss and letterpress finishes on considered stocks.",
                         "ph-hero__tag-text"),
                ]),
            ]),
        ]),
        div("ph-hero__points", [
            text("<strong>Considered paper</strong>Stocks chosen for how they look and how they feel in hand.", "ph-point"),
            text("<strong>Specialty finishes</strong>Foil, embossing and letterpress for the moments that deserve them.", "ph-point"),
            text("<strong>Design support</strong>Bring your files, or let our studio shape the idea with you.", "ph-point"),
        ]),
    ])], "Hero"),

    # 2. Finishes marquee -------------------------------------------------
    section("ph-section--ink ph-section--tight", [
        div("ph-marquee", [text(marquee_html, "ph-marquee__track", tag="div")]),
    ], "Finishes marquee"),

    # 3. Collection -------------------------------------------------------
    section("", [container([
        div("ph-head", [
            div("", [
                text("01 / The collection", "ph-eyebrow"),
                heading("Printed matter, <em>thoughtfully</em> produced.", "h2", "ph-h2"),
            ]),
            div("ph-head__aside", [
                text("From the card you hand over to the box it arrives in, every piece "
                     "is designed to make a quiet, lasting impression.", "ph-lead"),
                text_link(f"Shop everything {ARROW}", LINKS["shop"]),
            ]),
        ]),
        div("ph-cards", [
            collection_card(1, "Business cards &amp; stationery",
                            "First impressions, weighted properly. Cards, letterheads and notecards on stocks worth keeping.",
                            LINKS["business_cards"], "", "Stack of premium business cards with foil detail"),
            collection_card(2, "Invitations &amp; correspondence",
                            "For the dates that matter. Suites, save-the-dates and thank-yous with a sense of occasion.",
                            LINKS["invitations"], "ph-media--blush", "Wedding invitation suite with envelope and wax seal"),
            collection_card(3, "Packaging &amp; collateral",
                            "Boxes, sleeves, tags and stickers that make the unboxing part of the brand.",
                            LINKS["packaging"], "ph-media--olive", "Branded packaging and tissue in warm neutrals"),
            collection_card(4, "Art prints &amp; specialty finishes",
                            "Gallery-quality prints and finishing touches you notice with your fingertips.",
                            LINKS["art_prints"], "", "Close-up of an embossed art print on cotton paper"),
            collection_card(5, "Bespoke design studio",
                            "No artwork yet? Our designers will take you from idea to print-ready.",
                            LINKS["studio"], "ph-media--oxblood", "Designer reviewing proofs at a studio table"),
        ]),
    ])], "Collection"),

    # 4. Statement --------------------------------------------------------
    section("ph-section--oxblood", [container([
        div("ph-split", [
            media("ph-media--square", "Macro shot of paper fibres and a blind emboss"),
            div("ph-stack", [
                text("Our approach", "ph-eyebrow ph-eyebrow--light"),
                heading("Made to be <em>held onto.</em>", "h2", "ph-statement"),
                text("Print is the part of your brand people can pick up. So we sweat the "
                     "small things: the weight of the stock, the bite of the press, the edge "
                     "of the card. Elevated, never precious, and always within reach.",
                     "ph-lead"),
                button("Explore our finishes", LINKS["finishes"], "ph-btn--light"),
            ]),
        ]),
    ])], "Statement"),

    # 5. Details / material education -------------------------------------
    section("ph-section--sand", [container([
        div("ph-head", [
            div("", [
                text("02 / Details you can feel", "ph-eyebrow"),
                heading("The difference is in <em>the details.</em>", "h2", "ph-h2"),
            ]),
            div("ph-head__aside", [
                text("Not sure what to choose? Here's what we consider on every job, and "
                     "we're always happy to talk it through.", "ph-lead"),
            ]),
        ]),
        div("ph-details", [
            detail("i.", "Paper", "Cotton, textured and recycled stocks, chosen for colour, weight and how they feel in hand."),
            detail("ii.", "Finish", "Foil, blind embossing, letterpress and painted edges, used with restraint for maximum effect."),
            detail("iii.", "Colour", "Warm neutrals and curated accents, matched carefully and checked before anything goes to press."),
            detail("iv.", "Craft", "A real person reviews every file, so what arrives is exactly what you imagined."),
        ]),
    ])], "Details"),

    # 6. Process ----------------------------------------------------------
    section("", [container([
        div("ph-head", [
            div("", [
                text("03 / How it works", "ph-eyebrow"),
                heading("From idea to <em>in hand.</em>", "h2", "ph-h2"),
            ]),
            div("ph-head__aside", [
                button("Start your order", LINKS["shop"], "ph-btn--dark"),
            ]),
        ]),
        div("ph-steps", [
            step("01", "Choose your piece", "Browse the collection and pick your format, paper and finish."),
            step("02", "Upload or design with us", "Send print-ready artwork, or brief our studio and we'll design it for you."),
            step("03", "Approve your proof", "We check your file and share a proof. Nothing prints until you're happy."),
            step("04", "Printed &amp; delivered", "Carefully produced, packed with care and sent to your door."),
        ]),
    ])], "Process"),

    # 7. Studio -----------------------------------------------------------
    section("ph-section--sand", [container([
        div("ph-split ph-split--reverse", [
            media("ph-media--blush", "Stationery suite laid out on a linen tablecloth with soft shadows"),
            div("ph-stack", [
                text("04 / The Haus studio", "ph-eyebrow"),
                heading("Need a designer? <em>We'd love to help.</em>", "h2", "ph-h2"),
                text("From a single business card to a full identity and packaging system, our "
                     "studio turns good ideas into things worth printing. Clear advice, no "
                     "jargon, and a finished piece you'll be proud to hand over.", "ph-lead"),
                div("ph-tags", [
                    text("Small businesses", "ph-tag", tag="span"),
                    text("Weddings &amp; events", "ph-tag", tag="span"),
                    text("Studios &amp; agencies", "ph-tag", tag="span"),
                    text("Hospitality", "ph-tag", tag="span"),
                    text("Makers &amp; retail", "ph-tag", tag="span"),
                ]),
                button("Book a design consult", LINKS["consult"], "ph-btn--dark"),
            ]),
        ]),
    ])], "Studio"),

    # 8. Closing CTA ------------------------------------------------------
    section("ph-section--ink ph-cta", [container([
        div("ph-cta__inner", [
            text("Let's make something", "ph-eyebrow ph-eyebrow--light"),
            heading("Good ideas look <em>better printed.</em>", "h2", "ph-cta__title"),
            text("Tell us what you're working on and we'll help you choose the paper, "
                 "finish and format to bring it to life.", "ph-lead ph-cta__lead"),
            div("ph-actions ph-actions--center", [
                button("Start your order", LINKS["shop"], "ph-btn--light"),
                button("Talk to the studio", LINKS["quote"], "ph-btn--ghost-light"),
            ]),
        ]),
    ])], "Closing CTA"),
]


# ---------------------------------------------------------------------------
# Serialise to Bricks JSON
# ---------------------------------------------------------------------------
def flatten(nodes):
    out, counter = [], [0]

    def walk(node, parent):
        counter[0] += 1
        eid = _id(f"el:{counter[0]}:{node.name}")
        entry = {"id": eid, "name": node.name, "parent": parent, "children": [],
                 "settings": dict(node.settings)}
        if node.classes:
            entry["settings"]["_cssGlobalClasses"] = [class_ids[c] for c in node.classes]
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


def build_json():
    used = set()

    def collect(n):
        used.update(n.classes)
        for c in n.children:
            collect(c)
    for n in PAGE:
        collect(n)
    missing = used - CLASSES.keys()
    assert not missing, f"classes used but not defined: {missing}"

    return {
        "title": "Printing Haus - Homepage",
        "templateType": "content",
        "content": flatten(PAGE),
        "pageSettings": [],
        "templateSettings": [],
        "globalClasses": [
            {"id": class_ids[name], "name": name, "settings": {"_cssCustom": css.strip()}}
            for name, css in CLASSES.items()
        ],
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
.brxe-block{display:flex;flex-direction:column;width:100%}
.brxe-button{display:inline-flex}
.brxe-text-link{display:inline-flex}
"""

TAG_FOR = {"section": "section", "container": "div", "div": "div", "image": "img"}


def render(node):
    classes = " ".join(["brxe-" + node.name] + node.classes)
    s = node.settings
    inner = "".join(render(c) for c in node.children)
    if node.name == "heading":
        return f'<{s["tag"]} class="{classes}">{s["text"]}</{s["tag"]}>'
    if node.name == "text-basic":
        return f'<{s.get("tag", "p")} class="{classes}">{s["text"]}</{s.get("tag", "p")}>'
    if node.name in ("button", "text-link"):
        return f'<a class="{classes}" href="{s["link"]["url"]}">{s["text"]}</a>'
    if node.name == "image":
        return ""  # empty slot in preview -> placeholder background shows
    if s.get("tag") == "a":
        return f'<a class="{classes}" href="{s["link"]["url"]}">{inner}</a>'
    tag = s.get("customTag") or TAG_FOR[node.name]
    return f'<{tag} class="{classes}">{inner}</{tag}>'


def build_preview():
    css = "\n".join(c.replace("%root%", "." + name) for name, c in CLASSES.items())
    body = "".join(render(n) for n in PAGE)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Printing Haus Homepage</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&display=swap">
<style>{BRICKS_BASE}
{css}</style></head>
<body>{body}</body></html>
"""


if __name__ == "__main__":
    OUT_JSON.write_text(json.dumps(build_json(), indent=2, ensure_ascii=False) + "\n")
    OUT_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    OUT_PREVIEW.write_text(build_preview())
    print(f"wrote {OUT_JSON.relative_to(HERE.parent)} and {OUT_PREVIEW.relative_to(HERE.parent)}")
