# Chapter 1 — Introduction (The Problem and Its Background)

- Introduction (broad overview, why it matters today, definitions of key concepts)
- Background (evolution/milestones, frameworks, why it fails — home for the stats)
- Statement of the problem (one-sentence gap)
- Objectives of the study (general + specific)
- Research questions (own section, **after** Objectives)
- Scope and Limitations
- Significance of the study

## Notes

> Professor's generic Chapter 1 writing guide. Reference for structure/rubric — examples below are the professor's ML/healthcare illustrations, **not** our study's content.

### Why Chapter 1 matters
- Anchor of the paper: makes the study relevant, purposeful, impactful — not just technically sound.
- Goal: take the reader from a broad real-world problem down to the specific algorithmic solution proposed.
- It's the persuasive intro that convinces the audience the research deserves attention.

### Section structure
- **Introduction** — broad overview of the field; why it matters today (applications); clear definitions of key concepts.
- **Background** — evolution of the field; major milestones; relevant frameworks/technologies.
  - Tip: engaging but grounded. Avoid clichés ("Since the dawn of time…"). Back claims with current stats or recent foundational papers.
- **Problem Statement** — define the knowledge gap / challenge the research addresses.
  - Ex: "Despite advances in predictive analytics, current models struggle with real-time anomaly detection in streaming data."
- **Objectives** — general + specific (see below).
- **Research Questions** — guiding questions; **own section, placed after Objectives** (professor's order).
  - Ex: "How can machine learning improve decision-making in big data environments?"
- **Significance** — academic + practical value, by stakeholder (see below).
- **Scope and Limitations** — boundaries and constraints. Our chapter uses the **Limitations** framing (not "Delimitations"): state chosen scope boundaries with reasons, then real-world constraints. The delimitation-vs-limitation table below is kept only as reference for the distinction.

### Objectives
**General objective** — overall aim; broad, high-level statement of purpose.
- Ex: "To develop and evaluate ML models that improve diagnostic accuracy in healthcare data analytics."

**Specific objectives** — narrower, actionable, measurable; break the general objective into tasks.
- Ex: "To collect and preprocess patient datasets for training."
- "To compare decision trees, random forests, and deep learning models."
- "To evaluate accuracy using precision, recall, and F1-score."
- "To identify key features contributing most to predictions."

| Aspect | General Objective | Specific Objectives |
|---|---|---|
| Scope | Broad, overall aim | Narrow, detailed tasks |
| Focus | Purpose of the study | Steps to achieve the purpose |
| Measurement | Harder to measure directly | Measurable and testable |
| Example | "Improve fraud detection using ML" | "Test logistic regression vs. NN on transaction data" |

### Significance of the Study
Explain academic contribution (theory/methodology) and practical impact, broken down by stakeholder:
- **Field (CS / Data Science):** more efficient loss function? better training optimization?
- **Industry practitioners:** how does a company/doctor/policymaker use the model to save money, time, or lives?
- **Future researchers:** how does it serve as a building block for future studies?

### Scope, Delimitations & Limitations
Define boundaries so you aren't penalized for things you never intended to do.
- **Scope (what's included):** the dataset, exact frameworks (e.g., PyTorch, Scikit-Learn), metrics evaluated.
- **Delimitations (intentionally excluded):** "This study focuses strictly on tabular data, not unstructured text," or "optimized for edge devices, not high-dimensional cloud environments."

| Feature | Delimitations (your choice) | Limitations (out of your control) |
|---|---|---|
| Who decided | You (the researcher) | The environment / reality |
| Purpose | Narrow scope, keep project manageable | Be honest about weaknesses in findings |
| When set | Before the research | Discovered during / after the research |
| Key phrase | "This study focuses exclusively on…" | "Due to constraints in [X], this study could not…" |

**Delimitations** — what you chose to exclude; the parameters you set. Require logical justification.
- Data: "delimited to tabular data 2022–2025; image/text excluded to keep focus on structured financial auditing."
- Algorithm: "delimited to supervised, tree-based ensembles; deep learning exceeds standard enterprise compute budgets."
- Metrics: "delimited to F1-score and ROC-AUC; inference latency not measured."

**Limitations** — flaws/constraints imposed by reality, beyond your control. Acknowledging them shows rigor and honesty.
- Data: "high volume of missing values in the public dataset required imputation that may introduce bias."
- Hardware: "no multi-GPU cluster access; model trained only 50 epochs, may not have reached full convergence."
- Black box: "extreme non-linearity of the DNN limits interpretability of feature weights, hard to explain predictions to end-users."


