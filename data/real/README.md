# Real-generative evaluation set

The out-of-distribution test of the thesis (Section 4.3.1): text crops from real text-to-image outputs, labeled by the three-rater panel (Section 4.2.3). Nothing here is ever used for training or tuning.

## Steps

1. **Collect.** Save each generated image in `images/`, and log it in `prompts.csv`, one row per image: file name, generator, prompt, date. Use the sampling quota in `plans/plans.md`: four font families × mild to severe hallucination, from more than one generator.
2. **Localize.** `src/model/real.py localize` runs EasyOCR, the same localizer the app uses, and cuts every image into word crops. Output: `crops/` and `crops.csv`. Check the crops; delete rows for boxes that are not text, and keep a note of what was removed.
3. **Contact sheets.** `src/model/real.py sheet` writes `sheet_01.png` and so on. Each crop is labeled with its `crop_id`, for the raters.
4. **Label (the panel).** Each rater labels every crop on their own, without seeing the model's output. The answers go in `labels.csv`, one row per rater per crop:

   | column | value |
   |---|---|
   | `crop_id` | as on the contact sheet |
   | `rater` | `r1`, `r2` or `r3` |
   | `font` | a palette family name (e.g. `Open Sans`) or `unknown` |
   | `coherence` | `one`, `two` or `cannot_tell` (is the crop set in one typeface?) |

5. **Predict.** `src/model/real.py predict` runs the frozen model and both baselines. Output: `predictions.csv`, which is not committed. Run it any time; just keep the file away from the raters until labelling is done.
6. **Score.** `src/model/real.py score` gives the consensus labels (2 of 3), Fleiss' kappa, every model against the consensus, and the homogeneity check against the panel's coherence judgment. Output: `reports/real/real_eval.json`.
