# Appendix: Expert-Panel Rating Form

This appendix reproduces the layout of the web-based rating form that delivers the human-proxy consensus instrument of Section 4.2.3. The form has two screens. Screen A is shown once: it states the task, the ground rules (independent, self-paced, blind to the model's predictions and to the other raters), and the palette reference sheet the rater keeps open while rating. Screen B repeats for each of the [N = 100] real generative text crops: the crop is displayed beside an excerpt of the reference sheet, and the rater makes exactly one required choice — the closest palette font, found through a searchable list, or the "Unknown / hallucinated" verdict when no palette font matches.

The layout is platform-neutral: it specifies the content and controls of each screen, not a hosting service, so any standard web-form platform can deliver it without altering the instrument. The item texts shown (crop wording, specimen names, item counter) are illustrative.

**Figure A1**

*Expert-Panel Rating Form — Instructions Screen and Per-Crop Rating Item*

![Two-panel wireframe. Panel A, the instructions screen: task description (rate 100 text crops from AI-generated images, pick the closest Google Font or mark Unknown/hallucinated), ground rules (work independently, self-paced, never shown the model's predictions or other raters' answers), a callout for the palette reference sheet, and a begin button. Panel B, the rating item: an item counter with progress bar, the AI-generated text crop displayed beside a palette-reference-sheet excerpt of labeled specimens, a required question with a searchable palette dropdown, an alternative Unknown/hallucinated radio option, and Back / Save-and-next buttons with per-item saving noted](../../../assets/figures/expert_panel_form.png)

Per-item responses save individually, so a rater may pause and resume without loss; each rater submits one complete response set, and the three sets are combined under the 2-of-3 consensus rule of Section 4.2.3.
