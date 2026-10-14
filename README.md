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

The page positions Printing Haus as an elevated printer, not a design studio. It takes the
product-led shopping of MOO and the print-craft authority of Paper Chase Press.

1. **Hero**: "Good ideas look *better printed.*" with "Shop business cards" and "Get a sample pack" buttons, plus three points: proof before print, premium papers, specialty finishes
2. **Finishes marquee**: letterpress, foil, embossing and other finishes on Ink
3. **Shop by product**: six product cards (business cards, letterhead and envelopes, notecards, invitations, packaging and labels, art prints)
4. **Choose your paper** (Sand): Smooth, Cotton, Duplex and Recycled swatches
5. **Print methods & finishes**: an editorial list of digital, offset, letterpress, foil, embossing and painted edges
6. **Statement** (Oxblood): "Made to be *held onto.*"
7. **How to order**: pick a product, upload, approve the proof, printed and shipped
8. **The Haus promise** (Ink): checked by people, proof before print, made right, packed with care
9. **For business** (Sand): bulk and repeat orders, colour matching, custom packaging, with a "Request a quote" button
10. **Closing CTA** (Ink): a sample pack and business-card push

## Install in Bricks

1. In WP admin, go to **Bricks → Templates → Import** and upload `printinghaus-homepage.bricks.json`.
   The `ph-*` global classes come with it, and all styling lives in those classes.
2. Open the Home page in Bricks. Use **Templates (folder icon) → My templates → Printing Haus - Homepage → Insert**.
   Delete or keep your existing sections as needed.
3. **Photos:** every "Photo slot" holds an Image element. Click it and pick a photo. Until then
   a warm paper-toned placeholder shows. Follow the guide's image direction: close-up paper
   fibres, embossing, soft daylight, art-directed still lifes. Each slot's alt text already describes the
   shot it was designed for.
4. **Links:** the buttons point to placeholder URLs (`/shop/`, `/sample-pack/`, `/request-a-quote/`, `/product-category/...`).
   Update them in Bricks, or edit `LINKS` in `build_homepage.py` and rebuild.
5. **Fonts:** the CSS asks for *Neue Haas Grotesk* and *Tiempos* first. Add them as licensed
   fonts (Adobe Fonts / Klim) in **Bricks → Custom fonts**, or through a header link in
   **Bricks → Settings → Custom code**. Until then it falls back to Inter Tight / Newsreader
   if loaded, then Helvetica / Georgia.
6. Your header and footer stay in your Bricks header and footer templates. This template is page content only.

## Copy to confirm before launch

The page makes promises about the service, so check that each one is true for you:

- **Papers:** Smooth, Cotton, Duplex, Recycled. Rename them to your real stock names.
- **Methods and finishes:** digital, offset, letterpress, foil, embossing, painted edges, die cutting
- **Sample pack:** the page links to one in three places. If you don't offer one, change those buttons to "Contact us".
- **Promise:** "A real person reviews every file", "Nothing prints until you approve", "If it isn't right, we'll make it right"
- **For business:** bulk and repeat orders, brand colour matching, custom packaging, file setup

To make the page sell harder, add two things that MOO uses well:

- **Starting prices** on each product card, such as "From $XX / 50 cards". Add a Basic Text element under each card's spec line.
- **Real reviews or a review score** in a band between "How to order" and the promise section

## Editing

```sh
python3 bricks/build_homepage.py   # rewrites the JSON + preview
```
