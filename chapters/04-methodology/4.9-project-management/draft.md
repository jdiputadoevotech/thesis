## 4.9 Project Management

### 4.9.1 Schedule and Timeline

The project runs from June to December 2026. The schedule follows the increment order of Section 4.6, with the written chapters interleaved so that each empirical chapter is drafted as its results become available. Figure 11 shows the plan as a Gantt chart. As of the reporting date (July 10, 2026), Chapters 2 and 3 are complete and Chapter 4 is in progress; the four development increments, the results and conclusion chapters, and the final revisions follow through December.

**Figure 11**

*Project Schedule and Timeline (June to December 2026)*

![Weekly-cell Gantt grid spanning June to December 2026 with four week columns per month, tasks grouped into Writing, Development, and Closeout. Writing shows Chapter 2 and Chapter 3 completed, Chapter 4 in progress at the July 10 marker, and Chapters 5 and 6 planned. Development breaks the four increments into subtasks (palette and rendering, degradation operator, encoder and metric head, training and distillation, open-set and Top-K, evaluation and human panel, backend API, frontend and Docker). Closeout covers revisions and final defense in December](../../../assets/figures/gantt_timeline.png)

As shown in Figure 11, the early months cover the written groundwork (Chapters 2 and 3), the middle months carry the build increments from the synthetic data pipeline through the web application, and the final months are reserved for the results and conclusion chapters and for revision ahead of the defense. The development increments overlap the empirical chapters deliberately, because Chapter 5 reports the evaluation that increment 3 produces.

### 4.9.2 Responsibilities

The study is carried out by two researchers, both of whom act as researcher and developer. Table 3 divides the work. The split follows the two sides of the system: one member owns the Python model and data side, the other owns the service and interface side, and the writing is shared with cross-review.

**Table 3**

*Division of Responsibilities*

| Member | Role | Responsibilities |
|--------|------|------------------|
| Janritch Diputado | Researcher and developer | Python scripting: synthetic data pipeline, model training, and the inference engine. Lead author of Chapter 2 (Review of Related Literature) and Chapter 3 (Technical Background). |
| Matt Cabarrubias | Researcher and developer | Backend REST API (FastAPI) and the React frontend web application. Lead author of Chapter 4 (Methodology); contributor and reviewer for Chapters 2 and 3. |
| Both (shared) | Researchers and developers | System design, integration, evaluation and human-proxy panel coordination, and preparation for the final defense. |

*Note.* Authorship is stated by lead contributor; both members reviewed and contributed to all chapters.

### 4.9.3 Budget and Cost Management

The budget below estimates what it would cost another researcher or organization to replicate this study, not only the out-of-pocket cost to the current team. It therefore includes labor, since replication effort is the largest real cost, alongside compute, utilities, documentation, and contingency. Because the entire software stack is open-source (Section 4.8), the study carries no mandatory license or subscription cost, which is a deliberate outcome of the free-reconstruction design. Table 4 lists the estimate.

**Table 4**

*Estimated Replication Budget*

| Category | Item | Basis / assumption | Est. cost (PHP) |
|----------|------|--------------------|-----------------|
| Labor | 2 researcher-developers | ~30 weeks × ~15 hr/week each ≈ 900 hours total, at an illustrative ₱250/hr | 225,000 |
| Compute | Cloud GPU for training and experiments | ~100 to 150 GPU-hours; the backbone is frozen and only the metric head trains, so free Colab/Kaggle tiers can bring this near ₱0 | 5,000 |
| Subscriptions | Software stack | Fully open-source; none required | 0 |
| Data storage | Synthetic dataset | Generated locally (a few GB); no paid storage | 0 |
| Utilities | Internet and electricity | ~₱1,500/month × 7 months, shared | 10,500 |
| Documentation | Hard-bound thesis copies | ~₱1,500 × 3 copies | 4,500 |
| Contingency | Overhead on non-labor items | ~10% | 2,000 |
| **Total (with labor)** | | Full replication cost | **~247,000** |
| **Total (materials only)** | | If replicated by unpaid students | **~22,000** |

*Note.* Figures are planning estimates, not incurred expenses. The labor line dominates and is the most adjustable: it scales with the hourly rate and with how much of the pipeline a replicator reuses from the released code. The materials-only total reflects the near-zero software cost that the open-source stack makes possible.
