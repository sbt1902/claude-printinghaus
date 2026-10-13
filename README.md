# claude-printinghaus

Homepage for printinghaus.co, built as a **Bricks Builder** template from the
*Printing Haus Brand System, Vol. 01* (Paper / Ink / Sand / Olive / Oxblood
palette, Neue Haas Grotesk + Tiempos type, "refined but never precious" voice).

| File | What it is |
| --- | --- |
| `bricks/printinghaus-homepage.bricks.json` | Bricks template to import into WordPress |
| `bricks/build_homepage.py` | Source of truth: copy, links, and styles. Re-run it to regenerate |
| `preview/homepage.html` | Static preview of the same layout (open it in a browser) |

## Page structure

1. **Hero**: "Good ideas look *better printed.*" with order and consult CTAs, a photo slot with a "Details you can feel" tag, and three value points
2. **Finishes marquee**: letterpress, foil, embossing and other finishes on Ink (it stops scrolling when the visitor has reduced motion turned on)
3. **The collection**: five category cards, one for each area in the brand guide
4. **Statement** (Oxblood): "Made to be *held onto.*"
5. **Details you can feel** (Sand): paper / finish / colour / craft
6. **How it works**: four steps from order to delivery
7. **The Haus studio**: design services, with audience tags
8. **Closing CTA** (Ink): "Good ideas look *better printed.*"

## Install in Bricks

1. In WP admin, go to **Bricks → Templates → Import** and upload `printinghaus-homepage.bricks.json`.
   The 63 `ph-*` global classes come with it, and all styling lives in those classes.
2. Open the Home page in Bricks. Use **Templates (folder icon) → My templates → Printing Haus - Homepage → Insert**.
   Delete or keep your existing sections as needed.
3. **Photos:** every "Photo slot" holds an Image element. Click it and pick a photo. Until then
   a warm paper-toned placeholder shows. Follow the guide's image direction: close-up paper
   fibres, embossing, soft daylight, art-directed still lifes. Each slot's alt text already describes the
   shot it was designed for.
4. **Links:** the buttons point to placeholder URLs (`/shop/`, `/design-studio/`, `/product-category/...`).
   Update them in Bricks, or edit `LINKS` in `build_homepage.py` and rebuild.
5. **Fonts:** the CSS asks for *Neue Haas Grotesk* and *Tiempos* first. Add them as licensed
   fonts (Adobe Fonts / Klim) in **Bricks → Custom fonts**, or through a header link in
   **Bricks → Settings → Custom code**. Until then it falls back to Inter Tight / Newsreader
   if loaded, then Helvetica / Georgia.
6. Your header and footer stay in your Bricks header and footer templates. This template is page content only.

## Copy to confirm before launch

Some lines describe the service, so check that each one is true for you:

- The finishes listed in the marquee and hero (letterpress, foil, blind emboss, painted edges, duplex, cotton, die cut, spot gloss)
- "A real person reviews every file" and "Nothing prints until you're happy" (the proof step)
- The design-studio offer and the audience tags (weddings, hospitality, and so on)

There are no testimonials yet. If you have real client quotes, a short quote band between
"How it works" and "The Haus studio" would add social proof.

## Editing

```sh
python3 bricks/build_homepage.py   # rewrites the JSON + preview
```
