# Chapter 3 (Technical Background) — Grading Criteria

Reference this when outlining or modifying `notes.md`/`draft.md` in this folder. These are the professor's requirements (source: `professor-criteria.md`).

## Purpose (what a passing Technical Background does)
Provide the reader with the **theoretical and technical foundation** needed to understand the research. It is the **bridge between general knowledge and the specific problem statement** — not a literature review (that is Ch2), and not the methodology (that is Ch4). It equips the reader with the concepts, models, and tools that later chapters assume.

## Required outline (cover these sections in order)
1. **Introduction to the Domain** — overview of the subfield (e.g., machine learning, computer vision, typography/OCR); why the area is important.
2. **Core Concepts & Definitions** — algorithms, data structures, mathematical models; formal definitions (e.g., complexity classes, probability models).
3. **Theoretical Foundations** — key principles (e.g., supervised vs. unsupervised learning, metric learning, open-set recognition); equations or models that underpin the research.
4. **Existing Technologies & Frameworks** — tools, libraries, or architectures (e.g., PyTorch/TensorFlow, ViT/DINO, SSIM); **how they work AND their limitations**.
5. **Problem Context** — technical challenges in the field; why current solutions are insufficient (this sets up the thesis gap).
6. **Illustrations** — diagrams of architectures, flowcharts, or conceptual models.

## Non-negotiable rules
1. **General → specific.** Start broad (the field), then narrow to the sub-area the thesis addresses. Example arc: "ML is a subset of AI… within ML, CNNs are widely used for image classification…" then down to font-style metric learning.
2. **Define every term before use.** Introduce technical terms, theories, and models that appear later in the thesis, with clear definitions and, where appropriate, equations or diagrams. Avoid jargon unless defined.
3. **Explain underlying principles.** Cover the scientific/mathematical foundations relevant to the work (optimization methods, probability theory, computational complexity, distance metrics).
4. **Present frameworks with strengths AND limitations.** Every tool/framework discussion names both what it does well and where it falls short (e.g., "PyTorch provides dynamic computation graphs, making it flexible for research prototyping").
5. **Situate the problem.** Explicitly state the technical challenges/gaps that motivate the research (e.g., "Despite CNNs' success, their computational cost remains a barrier…").
6. **End with a transition to methodology.** Close the chapter by pointing toward Ch4 (e.g., "Having established the theoretical foundations of CNNs, the next chapter outlines the specific architecture and training procedure employed in this study.").
7. **APA citations throughout.** Cite whenever explaining a concept, framework, or prior work. Paraphrase most of the time; quote sparingly. Example: "CNNs exploit spatial hierarchies in images, making them more efficient than fully connected networks (LeCun, Bengio, & Hinton, 2015)."
8. **Balance detail.** Enough depth to inform, but not so much it becomes a textbook.

## Writing tips (professor's checklist)
- **Clarity first** — avoid jargon unless you define it.
- **Logical flow** — move from general to specific.
- **Balance detail** — inform without over-explaining.
- **Visual aids** — diagrams, tables, or equations make complex ideas digestible.
- **Citations** — anchor every major claim in APA style.

## Visuals: how to integrate every table/figure
Each visual needs **three things**: (a) an in-text introduction, (b) a caption that explains it and cites the source if adapted, (c) a follow-up sentence explaining its relevance.
- **Introduce before it appears:** "Table 2.1 compares traditional ML methods with CNNs, highlighting the advantages of automatic feature extraction."
- **Explain after it appears:** "As shown in Figure 2.2, CNNs process images through successive layers of convolution, pooling, and classification, enabling hierarchical feature learning."
- **Cite if adapted:** put an APA citation in the caption/note — e.g., "Figure 2.2. Simplified CNN architecture (adapted from Krizhevsky et al., 2012)."
- The caption explains the visual and cites the source; the paragraph integrates it into the narrative; citations appear in **both** caption and text.

### APA rules for Tables
- **Numbering:** consecutive in order of appearance (Table 1, Table 2…); number is **bold**, placed **above** the table.
- **Title:** clear, concise, in *italics*, title case, placed directly **below the number**. Example — `Table 2` / *Comparison of CNNs and Traditional ML Methods*.
- **Formatting:** clean and simple — **no vertical lines**, minimal horizontal lines; consistent body font (Arial 12 pt); align numbers/text neatly (decimal points aligned).
- **Notes (below table, if needed):** *General* note (explains the whole table), *Specific* note (a particular column/row), *Probability* note (statistical significance, e.g., p < .05). Example — "Note. CNN = Convolutional Neural Network; SVM = Support Vector Machine. Adapted from LeCun, Bengio, & Hinton (2015)."
- **Citations:** if adapted, cite in the note and include the full reference in the reference list.
- **Placement:** near first mention; always referred to in the narrative.

### APA rules for Figures
- **Numbering:** consecutive in order of appearance (Figure 1, Figure 2…); number is **bold**, placed **above** the figure.
- **Caption:** descriptive, in *italics*, title case, placed directly **below the figure**. Example — `Figure 2` / *Simplified architecture of a Convolutional Neural Network (CNN).*
- **Formatting:** clear, high-quality, professional — no decorative elements; labels inside the figure match the text (e.g., "Convolution Layer," "Pooling Layer").
- **Notes (below caption, if needed):** explain abbreviations, symbols, or source — e.g., "Note. Adapted from Krizhevsky, Sutskever, & Hinton (2012)."
- **Citations:** if adapted/reproduced, cite in the note and include the full reference. In-text example: "As shown in Figure 2, CNNs process images hierarchically (LeCun, Bengio, & Hinton, 2015)."
- **Placement:** near first mention; always referred to in the narrative.

## Steps to write (professor's procedure)
1. **Start broad, then narrow** — overview of the field → zoom to the thesis sub-area.
2. **Define key concepts** — terms/theories/models that appear later; use clear definitions, equations, or diagrams.
3. **Explain underlying principles** — the scientific/mathematical foundations relevant to the work.
4. **Discuss existing technologies/frameworks** — describe common tools/libraries/systems; highlight strengths and limitations.
5. **Situate the problem** — the technical challenges/gaps motivating the research.
6. **Use APA citations throughout** — cite each concept/framework/prior work; paraphrase mostly, quote sparingly.
7. **End with a transition** — point toward the methodology chapter.

## Self-check before considering a section done
- [ ] Flows general → specific (domain → sub-area → thesis-specific concepts).
- [ ] Every technical term is defined before it is used.
- [ ] Underlying principles are explained (equations/models where relevant).
- [ ] Each framework/tool is presented with **both** strengths and limitations.
- [ ] The problem context makes clear why current solutions are insufficient.
- [ ] Chapter ends with a transition into Ch4 (Methodology).
- [ ] Every major claim has a valid APA in-text citation that exists in `literature/references.md`.
- [ ] Every table/figure is introduced in text, captioned (bold number above, italic title below), explained afterward, and cited if adapted.
- [ ] Tables have no vertical lines, minimal horizontal lines, consistent font, aligned numbers.
