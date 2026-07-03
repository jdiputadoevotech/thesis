# Bibliography — Planning Notes

## Purpose
The reference list for the whole thesis, in **APA 7th edition**. It is generated from `literature/references.md` (the single source of truth, currently 35 rows). This folder holds the formatted output (`draft.md`), the APA rubric (`CLAUDE.md`), and this planner.

## Convention
- **`draft.md`** = the finished APA reference list (alphabetical, one entry per source). Nothing else.
- **`notes.md`** (this file) = planning, source→APA mapping, and verification flags. Never essay prose.
- When `references.md` gains a row, add its APA entry to `draft.md` in the correct alphabetical slot.

## Build rule (row → APA)
- **Journal article:** Author(s). (Year). Title in sentence case. *Journal Name in Title Case, Volume*(Issue), pages. https://doi.org/…
- **Conference paper:** Author(s). (Year). Title in sentence case. In *Proceedings…* (pp. x–y). https://…
- **Preprint (arXiv/OpenReview, not yet in proceedings):** Author(s). (Year). Title in sentence case. *arXiv*. https://arxiv.org/abs/…
- **Book:** Author(s). (Year). *Title in italics*. Publisher. URL if online.
- Alphabetize by first author surname; hanging indent + double spacing on export.

## Verification flags (confirm before final submission)
These entries were normalized to real venues/DOIs; a few need a human eyeball:

1. **Row 30 (DeepFont).** `references.md` lists author "Aseem, A." — that is the *first name* of **Aseem Agarwala**. `draft.md` corrects it to **Agarwala, A.** and restores co-author **Brandt, J.** (full list: Wang, Yang, Jin, Shechtman, Agarwala, Brandt, Huang). Fix the row in `references.md` to match.
2. **Row 6 (DINOv2).** `references.md` truncates the author list with "et al." `draft.md` gives the APA 21+‑author form (first 19 … last author, Bojanowski). Verify the middle names against the paper if a perfect list is required.
3. **Row 21 (TransTab).** Journal inferred as *Machine Learning with Applications* (Elsevier, ISSN 2666‑8270) from the ScienceDirect PII. Confirm exact journal, volume, and article number.
4. **Row 26 (Bhunia et al., 2018).** Venue inferred as *ICPR 2018* from the IEEE Xplore doc ID. Confirm the exact conference name/pages; add a DOI if available.
5. **Rows 22, 23, 24 (Procedia CS / Neurocomputing / Applied Soft Computing).** Journal names confirmed from PII ranges; volume, issue, and pages still need filling from each article's landing page.
6. **arXiv rows (2, 10–19, 35-adjacent).** Where a source has since been formally published (proceedings/journal), upgrade the preprint entry to the published citation.
7. **Page/volume numbers** are omitted where `references.md` did not record them. Add on final pass.

## Status
- [x] All 35 rows converted to APA 7th and placed alphabetically in `draft.md`.
- [ ] Human verification of the 7 flags above.
- [ ] Fill missing volume/issue/page numbers on final pass.
