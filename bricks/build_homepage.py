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
    "business_cards": "/product-category/business-cards/",
    "stationery": "/product-category/letterhead-envelopes/",
    "notecards": "/product-category/notecards-postcards/",
    "invitations": "/product-category/invitations/",
    "packaging": "/product-category/packaging-labels/",
    "art_prints": "/product-category/art-prints/",
    "paper": "/paper/",
    "finishes": "/print-methods-finishes/",
    "samples": "/sample-pack/",
    "quote": "/request-a-quote/",
    "contact": "/contact/",
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
    # Products ------------------------------------------------------------
    "ph-products": """
%root% {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(36px, 4vw, 56px) clamp(16px, 2vw, 28px);
}
@media (max-width: 991px) { %root% { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { %root% { gap: 32px 12px; } %root% .ph-card__text { display: none; } }
""",
    "ph-card__spec": """
%root% { margin: -8px 0 0; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--ph-olive); }
""",
    # Papers --------------------------------------------------------------
    "ph-papers": """
%root% {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(16px, 2vw, 28px);
}
@media (max-width: 991px) { %root% { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { %root% { grid-template-columns: 1fr; } }
""",
    "ph-paper": """
%root% { display: flex; flex-direction: column; gap: 12px; }
%root% .ph-media { margin-bottom: 10px; box-shadow: 0 24px 40px -28px rgba(10,10,10,.45); }
""",
    "ph-media--paper": """
%root% { background: radial-gradient(120% 80% at 25% 20%, #fff, transparent 65%), linear-gradient(160deg, #FDFCFA 0%, #ECE8E1 100%); }
""",
    "ph-media--duplex": """
%root% { background: linear-gradient(160deg, var(--ph-paper) 0%, var(--ph-sand) 100%); }
%root%::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 10px; background: var(--ph-oxblood); }
""",
    # Print methods -------------------------------------------------------
    "ph-methods": "%root% { display: flex; flex-direction: column; border-bottom: 1px solid var(--ph-stone); }",
    "ph-method": """
%root% {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
  align-items: baseline;
  padding: 30px 0;
  border-top: 1px solid var(--ph-stone);
  transition: padding .3s ease, color .3s ease;
}
%root%:hover { padding-left: 12px; }
%root%:hover .ph-method__title { color: var(--ph-oxblood); }
@media (max-width: 767px) { %root% { grid-template-columns: 48px minmax(0, 1fr); } %root% > :last-child { grid-column: 2; } }
""",
    "ph-method__title": """
%root% { margin: 0; font-size: clamp(26px, 3vw, 44px); font-weight: 500; letter-spacing: -0.03em; line-height: 1; transition: color .3s ease; }
%root% em { font-family: var(--ph-serif); font-style: italic; font-weight: 400; }
""",
    "ph-methods__foot": "%root% { margin-top: 36px; }",
    # Promise (on ink) ----------------------------------------------------
    "ph-details--light": """
%root% { border-top-color: rgba(249,247,243,.22); }
%root% .ph-detail + .ph-detail { border-left-color: rgba(249,247,243,.22); }
%root% .ph-detail__text { color: var(--ph-stone); }
%root% .ph-detail__num { color: var(--ph-blush); }
@media (max-width: 991px) { %root% .ph-detail { border-bottom-color: rgba(249,247,243,.22); } }
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
# Page content: an elevated printer, not a design studio.
# Voice: refined but never precious; clear, warm, quietly confident about craft.
# ---------------------------------------------------------------------------
def product_card(title, spec, blurb, url, variant, alt):
    return link_block("ph-card", url, [
        media(variant, alt),
        heading(title, "h3", "ph-card__title"),
        text(spec, "ph-card__spec"),
        text(blurb, "ph-card__text"),
        text(f"Shop now {ARROW}", "ph-card__more", tag="span"),
    ])


def paper(name, feel, body, variant):
    return div("ph-paper", [
        media("ph-media--square " + variant, f"{name} paper swatch, close-up"),
        heading(name, "h3", "ph-detail__title"),
        text(feel, "ph-card__spec"),
        text(body, "ph-detail__text"),
    ])


def method(num, title, body):
    return div("ph-method", [
        text(num, "ph-card__num"),
        heading(title, "h3", "ph-method__title"),
        text(body, "ph-detail__text"),
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


def section_head(eyebrow, title, lead=None, aside=None):
    side = ([text(lead, "ph-lead")] if lead else []) + (aside or [])
    return div("ph-head", [
        div("", [text(eyebrow, "ph-eyebrow"), heading(title, "h2", "ph-h2")]),
        div("ph-head__aside", side),
    ])


FINISHES = ["Letterpress", "Foil stamping", "Embossing", "Painted edges",
            "Duplex stocks", "Cotton paper", "Debossing", "Die cutting"]
marquee_html = "".join(
    f"<span>{f}</span><i aria-hidden=\"true\">/</i>" for f in FINISHES * 2
)

PAGE = [
    # 1. Hero -------------------------------------------------------------
    section("ph-hero", [container([
        div("ph-hero__grid", [
            div("", [
                text("Premium printing &mdash; Cards, stationery &amp; packaging", "ph-eyebrow"),
                heading("Good ideas look <em>better printed.</em>", "h1", "ph-hero__title"),
                text("Exceptional paper, specialty finishes and print you can feel the "
                     "difference in. Upload your design, approve your proof, and we'll "
                     "handle the rest.", "ph-lead ph-hero__lead"),
                div("ph-actions", [
                    button("Shop business cards", LINKS["business_cards"], "ph-btn--dark"),
                    button("Get a sample pack", LINKS["samples"], "ph-btn--ghost"),
                ]),
            ]),
            div("ph-hero__visual", [
                media("", "Foil-stamped business cards on thick cotton paper in soft daylight"),
                div("ph-hero__tag", [
                    text("Details you can feel.", "ph-hero__tag-title"),
                    text("Foil, letterpress and embossing on cotton, duplex and recycled stocks.",
                         "ph-hero__tag-text"),
                ]),
            ]),
        ]),
        div("ph-hero__points", [
            text("<strong>Proof before print</strong>Every order is checked and proofed before it goes to press.", "ph-point"),
            text("<strong>Premium papers</strong>Cotton, duplex and recycled stocks, chosen for feel and finish.", "ph-point"),
            text("<strong>Specialty finishes</strong>Foil, letterpress, embossing and painted edges.", "ph-point"),
        ]),
    ])], "Hero"),

    # 2. Finishes marquee -------------------------------------------------
    section("ph-section--ink ph-section--tight", [
        div("ph-marquee", [text(marquee_html, "ph-marquee__track", tag="div")]),
    ], "Finishes marquee"),

    # 3. Shop by product --------------------------------------------------
    section("", [container([
        section_head("01 / Shop by product", "Everything worth <em>printing well.</em>",
                     "Professional print for business and life's occasions, from a box of "
                     "cards to a full stationery suite.",
                     [text_link(f"Shop all products {ARROW}", LINKS["shop"])]),
        div("ph-products", [
            product_card("Business Cards", "Cotton &middot; Duplex &middot; Foil",
                         "The card you hand over says it first. Make it weighty, tactile and unmistakably yours.",
                         LINKS["business_cards"], "", "Stack of duplex business cards with a painted edge"),
            product_card("Letterhead &amp; Envelopes", "Matching stationery",
                         "Correspondence that feels considered, on stocks that pair with your cards.",
                         LINKS["stationery"], "ph-media--paper", "Letterhead and envelopes on a linen surface"),
            product_card("Notecards &amp; Postcards", "Flat &middot; Folded",
                         "Thank-yous, notes and mailers worth keeping on the fridge.",
                         LINKS["notecards"], "ph-media--olive", "Folded notecards with envelopes"),
            product_card("Invitations", "Weddings &middot; Events",
                         "Suites, save-the-dates and menus with a real sense of occasion.",
                         LINKS["invitations"], "ph-media--blush", "Letterpress wedding invitation suite with wax seal"),
            product_card("Packaging &amp; Labels", "Boxes &middot; Sleeves &middot; Stickers",
                         "Branded packaging, tags and labels that make the unboxing part of the experience.",
                         LINKS["packaging"], "ph-media--oxblood", "Branded boxes, sleeves and stickers"),
            product_card("Art Prints", "Fine art papers",
                         "Gallery-quality prints with rich colour and a beautiful surface.",
                         LINKS["art_prints"], "", "Close-up of an art print on textured paper"),
        ]),
    ])], "Shop by product"),

    # 4. Papers -----------------------------------------------------------
    section("ph-section--sand", [container([
        section_head("02 / Choose your paper", "It starts with <em>the paper.</em>",
                     "The right stock changes everything: how a card feels, how ink sits, "
                     "how it's remembered. Here's what we print on.",
                     [text_link(f"Compare our papers {ARROW}", LINKS["paper"])]),
        div("ph-papers", [
            paper("Smooth", "Crisp &middot; Bright",
                  "A refined everyday premium. Sharp detail and true colour on an elegant uncoated finish.",
                  "ph-media--paper"),
            paper("Cotton", "Soft &middot; Tactile",
                  "Made from cotton fibres with a gentle tooth that takes letterpress and embossing beautifully.",
                  ""),
            paper("Duplex", "Thick &middot; Substantial",
                  "Two sheets bonded together for serious weight and a contrasting colour edge.",
                  "ph-media--duplex"),
            paper("Recycled", "Natural &middot; Considered",
                  "Characterful recycled stocks for brands who care how things are made.",
                  "ph-media--olive"),
        ]),
    ])], "Papers"),

    # 5. Print methods & finishes -----------------------------------------
    section("", [container([
        section_head("03 / Print methods &amp; finishes", "Printing methods, <em>done properly.</em>",
                     "From fast, full-colour digital to traditional letterpress, we match the "
                     "method to the piece."),
        div("ph-methods", [
            method("01", "Digital", "Sharp, vibrant and quick. Ideal for full-colour designs and shorter runs."),
            method("02", "Offset", "Precise, consistent colour for larger runs and brand-critical work."),
            method("03", "Letterpress", "Ink pressed deep into soft cotton paper for an impression you can feel."),
            method("04", "Foil <em>stamping</em>", "Metallic and pigment foils that catch the light: gold, copper, silver and more."),
            method("05", "Embossing", "Raised or recessed detail, with or without ink, for quiet, tactile impact."),
            method("06", "Painted <em>edges</em>", "A flash of colour along the edge of thick stocks. A small detail with a big effect."),
        ]),
        div("ph-methods__foot", [
            text_link(f"Not sure which? Talk to a print specialist {ARROW}", LINKS["contact"]),
        ]),
    ])], "Print methods"),

    # 6. Statement --------------------------------------------------------
    section("ph-section--oxblood", [container([
        div("ph-split", [
            media("ph-media--square", "Macro shot of a blind emboss on cotton paper"),
            div("ph-stack", [
                text("Why Printing Haus", "ph-eyebrow ph-eyebrow--light"),
                heading("Made to be <em>held onto.</em>", "h2", "ph-statement"),
                text("Print is the part of your brand people can pick up. So we obsess over "
                     "the details: the weight of the stock, the bite of the press, the colour "
                     "on the edge. Elevated print, made accessible.", "ph-lead"),
                button("Get a sample pack", LINKS["samples"], "ph-btn--light"),
            ]),
        ]),
    ])], "Statement"),

    # 7. How to order -----------------------------------------------------
    section("", [container([
        section_head("04 / How to order", "From file to <em>in hand.</em>", None,
                     [button("Start your order", LINKS["shop"], "ph-btn--dark")]),
        div("ph-steps", [
            step("01", "Pick your product", "Choose your format, paper and finish. Not sure? Order a sample pack first."),
            step("02", "Upload your design", "Send print-ready artwork, or let our team set up your file for you."),
            step("03", "Approve your proof", "We check every file and send a proof. Nothing prints until you're happy."),
            step("04", "Printed &amp; shipped", "Carefully printed, finished and packed to arrive in perfect condition."),
        ]),
    ])], "How to order"),

    # 8. The Haus promise -------------------------------------------------
    section("ph-section--ink", [container([
        div("ph-head", [
            div("", [
                text("The Haus promise", "ph-eyebrow ph-eyebrow--light"),
                heading("Print you can <em>count on.</em>", "h2", "ph-h2"),
            ]),
        ]),
        div("ph-details ph-details--light", [
            detail("i.", "Checked by people", "A real person reviews every file before it goes to press."),
            detail("ii.", "Proof before print", "Nothing is printed until you've approved your proof."),
            detail("iii.", "Made right", "If something isn't right with your order, we'll make it right."),
            detail("iv.", "Packed with care", "Protected, flat-packed and ready to hand out the day it arrives."),
        ]),
    ])], "Promise"),

    # 9. For business -----------------------------------------------------
    section("ph-section--sand", [container([
        div("ph-split ph-split--reverse", [
            media("ph-media--blush", "Branded packaging and stationery for a boutique business"),
            div("ph-stack", [
                text("05 / For business", "ph-eyebrow"),
                heading("Your print partner, <em>run after run.</em>", "h2", "ph-h2"),
                text("Larger runs, custom packaging, brand-matched colour and easy reorders. "
                     "Tell us about your project and we'll put together a custom quote.",
                     "ph-lead"),
                div("ph-tags", [
                    text("Bulk &amp; repeat orders", "ph-tag", tag="span"),
                    text("Brand colour matching", "ph-tag", tag="span"),
                    text("Custom packaging", "ph-tag", tag="span"),
                    text("File setup &amp; design help", "ph-tag", tag="span"),
                ]),
                div("ph-actions", [
                    button("Request a quote", LINKS["quote"], "ph-btn--dark"),
                ]),
            ]),
        ]),
    ])], "For business"),

    # 10. Closing CTA -----------------------------------------------------
    section("ph-section--ink ph-cta", [container([
        div("ph-cta__inner", [
            text("Feel the difference", "ph-eyebrow ph-eyebrow--light"),
            heading("Good ideas look <em>better printed.</em>", "h2", "ph-cta__title"),
            text("Not sure which paper is right? Order a sample pack and feel our stocks "
                 "and finishes in hand before you print.", "ph-lead ph-cta__lead"),
            div("ph-actions ph-actions--center", [
                button("Shop business cards", LINKS["business_cards"], "ph-btn--light"),
                button("Get a sample pack", LINKS["samples"], "ph-btn--ghost-light"),
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
            for name, css in CLASSES.items() if name in used
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
