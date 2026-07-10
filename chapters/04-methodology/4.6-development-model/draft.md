## 4.6 Development Model

### 4.6.1 Identification of the Model

This study follows an **iterative-incremental** development model. The system is built as a sequence of increments, each of which runs a full Analyze, Design, Build, and Evaluate cycle and delivers a working slice that integrates into the growing whole. The model is shown in Figure 10.

### 4.6.2 Justification

The iterative-incremental model fits this project better than a single-pass model such as Waterfall for two reasons. First, the work is part research: the behavior of the metric embedding and the open-set threshold cannot be fully specified in advance, and each increment's evaluation, such as Top-K accuracy or the rejection rate on held-out crops, feeds back into the design of the next. A model that froze the design before any results existed would not survive contact with the data. Second, the components have a natural build order and dependencies: the recognizer cannot be trained without the synthetic dataset, the open-set decision cannot be tuned without a trained embedding, and the web application only has something to serve once the recognizer works. Delivering these as increments keeps a working, testable artifact in hand at every stage and isolates risk to one increment at a time, which suits a two-person team without a dedicated QA role.

### 4.6.3 Phases of the Model

The project is organized into four increments, each producing a deliverable that the next increment consumes.

1. **Increment 1: Synthetic data pipeline.** Analyze the documented deformation modes, design the rendering and degradation operator $D$, build the pipeline, and evaluate the crops against the target hallucination distribution. Deliverable: a labeled corpus of pristine and degraded crops (Section 4.3.1).
2. **Increment 2: Metric embedding.** Design and build the frozen DINOv2 encoder with the trained metric head, and evaluate embedding separability across fonts and families. Deliverable: the frozen encoder plus the trained head $f_\theta$ (Section 4.3.2).
3. **Increment 3: Open-set decision and evaluation.** Add the rejection score, the calibrated Top-K, and the structural-distance verification, then evaluate against the baselines and the human-proxy panel. Deliverable: the full recognizer with its Top-K, rejection, and metric outputs (Sections 4.2 and 4.10).
4. **Increment 4: Web application.** Wrap the recognizer in the FastAPI backend and React frontend, then evaluate it interactively on real uploaded images. Deliverable: the running demo application (Section 4.5).

### 4.6.4 SDLC Diagram

**Figure 10**

*Iterative-Incremental Development Model*

![Diagram of four increments (synthetic data pipeline, metric embedding, open-set and evaluation, web application) arranged left to right, each running an Analyze, Design, Build, and Evaluate cycle with a refine loop and producing a deliverable, and each deliverable integrating into a cumulative working system band beneath them](../../../assets/figures/sdlc_model.png)

As shown in Figure 10, the four increments proceed left to right, but the arrows within each increment show that development is not linear inside it: the Analyze, Design, Build, and Evaluate phases repeat, and each evaluation refines the same increment before the next one begins. The deliverables accumulate into a single working system rather than being integrated only at the end, so that a failure surfaced late, for example an open-set threshold that rejects too many valid crops, can be traced to the increment that introduced it.
