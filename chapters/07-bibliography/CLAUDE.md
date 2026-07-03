# Bibliography — APA 7th Edition Format Rules

Reference this when editing `draft.md` in this folder. `draft.md` is the thesis reference list; it must follow **APA 7th edition** exactly. Source of record for what goes in it is `literature/references.md`.

## Non-negotiable rules
1. **One list, alphabetical.** All sources in a single list, ordered by the first author's surname (letter by letter). No numbering, no grouping by type.
2. **Hanging indent.** Each entry: first line flush left, subsequent lines indented 0.5 in. (Markdown can't show this; apply on DOCX/PDF export.)
3. **Double spacing** throughout, both within and between entries. Body 12 pt.
4. **Every in-text citation has exactly one matching entry here, and vice versa.** No orphans in either direction.

## Author names
- Invert every author: **Surname, F. M.** (initials, not full first names).
- Up to **20 authors**: list all, use `&` before the last.
- **21+ authors**: list the first **19**, then `…` (ellipsis), then the **final** author. No `&`.
- Group/organization authors: spell out fully.

## Element order and style
`Author(s). (Year). Title. Source. DOI/URL.`
- **Year** in parentheses, then a period.
- **Title of the work** (article/chapter/paper): **sentence case** — capitalize only the first word, the first word after a colon, and proper nouns. *Not italicized.*
- **Title of the container** (journal, book, proceedings): **Title Case** and *italicized*.
- **Journal:** *Journal Name, Volume*(Issue), pp–pp. Volume italicized; issue not; no "pp." for journals.
- **Book:** *Title in italics* (sentence case). Publisher.
- **Conference paper:** In *Proceedings of…* (pp. x–y). Publisher/URL.
- **Preprint (arXiv / OpenReview, not formally published):** *arXiv*. https://arxiv.org/abs/XXXX — upgrade to the published citation once available.

## DOIs and URLs
- Prefer a **DOI** as `https://doi.org/10.xxxx/…` (no "DOI:" label, no trailing period).
- If no DOI, use a stable URL (publisher landing page, arXiv abs, proceedings hash).
- One locator per entry; do not stack DOI + arXiv + publisher.

## Titles: capitalization quick check
- Article/paper/book title → **sentence case**.
- Journal / proceedings / conference name → **Title Case, italic**.
- Preserve proper nouns and acronyms as-is (e.g., DINOv2, SSIM, OCR, ViT, EMNLP).

## Self-check before considering `draft.md` done
- [ ] Alphabetical by first author surname; ties broken by second author, then year.
- [ ] Every entry inverts author names to `Surname, F. M.` with `&` before the last (≤20 authors) or the `… last` form (21+).
- [ ] Work titles in sentence case; container titles Title Case + italic.
- [ ] Volume italic, issue not, correct page ranges for journal articles.
- [ ] One DOI/URL per entry, DOI as `https://doi.org/…`, no trailing period after it.
- [ ] Each entry maps to a row in `literature/references.md`; no orphan citations.
- [ ] Hanging indent + double spacing applied on export.
