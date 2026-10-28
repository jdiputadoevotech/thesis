# Real-generative evaluation set

The out-of-distribution test of the thesis (Section 4.3.1): text crops from real text-to-image outputs, labeled by the three-rater panel (Section 4.2.3). Nothing here is ever used for training or tuning.

## Steps

0. **Plan.** `python src/data/generate_real.py plan` writes `plan.csv`: 84 images (60 SDXL, 12 ChatGPT, 12 Gemini), each with an opaque id (`r001`...), the family and severity it asks for, the text and the prompt. Prompts use fictional names only. Read them and commit `plan.csv` before generating anything; a new plan after images exist would no longer match their ids, so the script refuses.
1. **Collect.** Every image is logged in `prompts.csv` (image, generator, prompt, date, plan_id, seed).
   - *SDXL, free.* In a Colab or Kaggle GPU notebook: `git clone https://github.com/jdiputadoevotech/thesis && cd thesis`, then `pip install -q diffusers transformers accelerate safetensors`, then `python src/data/generate_real.py sdxl`. About 30 s per image on a T4. Download `data/real/images/` and `data/real/prompts.csv` into the same paths here. `--limit 5` for a trial run; `--offload` for GPUs under 12 GB.
   - *ChatGPT and Gemini, by API* (24 images; a few dollars at most). Put the keys in the shell for this session only, never in a file or the chat: `export OPENAI_API_KEY=...` and `export GEMINI_API_KEY=...`. List the image models each key can use, pick the current ChatGPT-image and Gemini-image ones, and try one image each:

     ```sh
     curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | grep -o '"id": *"[^"]*image[^"]*"'
     curl -s https://generativelanguage.googleapis.com/v1beta/models -H "x-goog-api-key: $GEMINI_API_KEY" | grep -o '"name": *"[^"]*image[^"]*"'
     python src/data/generate_real.py api --only chatgpt --openai-model <id> --limit 1
     python src/data/generate_real.py api --only gemini --gemini-model <id> --limit 1
     ```

     Look at both images, then drop `--limit 1` (and `--only`, with both model flags) for the other 22. One request per prompt, first output kept; the model id is logged in `prompts.csv`. A refused or blocked prompt is listed at the end: make that one by hand. OpenAI may ask you to verify the organization before it serves its image models.
   - *By hand, only if an API refuses a prompt.* `python src/data/generate_real.py intake` lists what is missing, with the prompt to paste. Save each result under its id, e.g. `r023.png`, in `images/`, then run `intake` again to log it. Keep the first result; do not retry for a better one.

   Images never go in git (`images/` is ignored). Check each tool's terms for research use.
2. **Localize and select.** `src/model/real.py localize` cuts every image into word crops (on a Mac add `--no-gpu`). Then `python src/data/generate_real.py select` keeps whole images, cell by cell, until each family × severity cell holds about N/12 crops, taking turns between generators and reading only the plan. It rewrites `crops.csv` with the selection (the full list stays in `crops_all.csv`) and writes `selection.json`. Run `localize` and `select` together again if you add images. Then look at the crops and delete boxes that are not text; keep a note of what was removed and why.
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

## Reading the plan

- Family and severity are what each prompt asks for; the generator may deliver something else. The panel's consensus labels measure what came out, so compare the "unknown" and "mixed" rates across the severity cells as a check that the severe prompts really produced worse text.
- Crops from one image share a style and a generator. Resample images, not crops, when computing confidence intervals.
- Crop ids (`r012_03`) carry no generator or cell, and the rater app does not show `plan.csv`.
