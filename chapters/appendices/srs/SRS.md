# APPENDIX A

# SOFTWARE REQUIREMENTS SPECIFICATION

IEEE 830 / ISO·IEC·IEEE 29148 Format

**Addressing Typographic Hallucination in Generative AI Images: An Open-Set Metric Learning Approach to Font Style Recognition**

Version 1.2 · August 3, 2026

By
Janritch Diputado
Matt Cabarrubias

Christine D. Bandalan, MEng
Faculty Adviser

## Revision History

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-07-16 | 1.0 | Initial thesis-scoped SRS | Research team |
| 2026-07-26 | 1.1 | Restructured to the IEEE 830 capstone template; adviser format revisions | Research team |
| 2026-08-03 | 1.2 | Post-defense revisions: word-level localization, mixed-typography verdict, word-merge presentation | Research team |

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for **FontID** version 1.x, the web demonstrator that exposes the thesis's font-recognition model to a user. It is the *artifact* half of the study's build method (Ch4 §4.10): a single-page application that accepts a generative-AI image, runs the open-set metric-learning pipeline, and returns a ranked shortlist of the closest Google Fonts for each detected line of text — or rejects the text as out-of-palette. The software will not perform font vectorization, licensing, or any commercial identification.

### 1.2 Document Conventions

Each requirement is labeled `REQ-<section>-<n>` (e.g., REQ-4.1-2) with priority **High / Med / Low**. Mandatory behavior uses **shall**; desired behavior uses **should**. Tables and figures follow APA 7th edition formatting.

### 1.3 Intended Audience and Reading Suggestions

The document is intended for the two researcher-developers, the faculty adviser, and the panel evaluating the demonstrator. The panel and adviser may read Section 2 for a high-level view of scope and functions; the developers should read Sections 3–5 in full; evaluators verifying the demo should focus on Section 4 (features) and Section 5 (non-functional requirements) to derive test cases.

### 1.4 Product Scope

FontID is a **local demonstration harness**, not a production service. It wraps the trained model so that hallucinated text crops map to a localized palette of the top 50–100 Google Fonts for free template reconstruction. Explicitly **out of scope**: user accounts, multi-user scaling, persistent storage, payment/licensing, and font vectorization. The app is single-page with three zones — **Input → Processing → Results** — and runs on one machine for the defense demo.

### 1.5 References

| Ref# | Document Title | Version/Date | Source |
| :--- | :--- | :--- | :--- |
| [1] | Thesis Chapter 4 — Methodology (conceptual framework §4.4, architecture §4.5, build method §4.10) | 2026 | This thesis |
| [2] | IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications | 1998 | IEEE |
| [3] | ISO/IEC/IEEE 29148:2018, Requirements engineering | 2018 | ISO/IEC/IEEE |
| [4] | Google Fonts open-source font library | current | https://fonts.google.com |

## 2. Overall Description

### 2.1 Product Perspective

FontID is a **new, self-contained** front end over an existing trained model; it adds no new learning logic. The runtime path is layered — React client → FastAPI backend → PyTorch inference service → model weights and font assets — as detailed in the system-architecture diagram (Ch4 §4.5.2, Fig 9). The trained metric head is produced offline; the app only *loads and serves* it.

### 2.2 Product Functions

- Accept a GenAI image by drag-drop, file browse, or a bundled sample — drawn from a pool of at least 10 real AI-generated demo images, never part of any training data, with 3 offered at random each start-up.
- Localize the text in the image at word granularity and crop each word.
- Embed each crop, check it for font homogeneity, and rank it against the font palette.
- Return a Top-K shortlist per crop with a similarity score, reject it as out-of-palette, or report it as mixed typography; adjacent words with the same verdict merge into one result.
- Render each candidate font as a live preview of the detected text for visual confirmation.

### 2.3 User Classes and Characteristics

| User class | Characteristics | Privileges/Access |
| :--- | :--- | :--- |
| Designer / end user | Non-technical; wants a free font match to rebuild a template. | Standard access: uploads an image, reads the Top-K shortlist. |
| Researcher / evaluator | The team + panel; technical. | Full local access: drives the demo, inspects backend score/τ logs, confirms open-set reject behavior. |

### 2.4 Operating Environment

- **Client:** current Chrome / Firefox / Edge (latest two versions), desktop viewport.
- **Server:** Python 3.11+, FastAPI, PyTorch, packaged with Docker; runs on the presenter's laptop (`localhost`). GPU optional — CPU inference acceptable for single-image demo latency.
- **Assets:** DINOv2 + baseline weights from HuggingFace Hub; Google Fonts files for palette matching and preview rendering.

### 2.5 Design and Implementation Constraints

- Stack is fixed by the methodology (Ch4 §4.8): **React** (frontend), **FastAPI** (backend), **PyTorch + HuggingFace** (inference), **Docker** (deploy).
- Preprocessing (square-pad → 224² → ImageNet normalize) **shall** run inside the model forward pass to avoid train–serve skew (Ch4 §4.3.2).
- Only open-source fonts (the Google Fonts palette) may be returned — no commercial font identifiers or licenses.

### 2.6 Assumptions and Dependencies

- The trained metric head and palette are available on disk at startup.
- The uploaded image contains legible rendered text (not handwriting / heavy occlusion).
- The off-the-shelf text-localization component is available and returns bounding boxes.
- The HuggingFace Hub remains reachable for the one-time weight download; after that the app runs offline.

## 3. External Interface Requirements

### 3.1 User Interfaces

Single page, three vertically stacked zones (wireframe below):

1. **Input** — a drag-drop/browse dropzone, sample thumbnails, and an **Identify Fonts** action.
2. **Processing** — the uploaded image with detected text regions boxed, plus a pipeline status/progress indicator.
3. **Results** — a carousel showing one card at a time per result region, adjacent word crops sharing a verdict having been merged into one, navigated with previous/next arrows, a region indicator ("Region 1 of 2"), and pagination dots. Each card holds the crop thumbnail, its Top-K font shortlist (name · preview · similarity bar), and a **KNOWN / UNKNOWN / MIXED** badge for the open-set decision.

The interface shall work at desktop widths and keep all three zones reachable on one page. Standard affordances: every result font preview offers a copy-name / preview action.

**Figure A1**

*FontID Single-Page Wireframe (Input → Processing → Results)*

![FontID single-page wireframe with three stacked zones: an upload dropzone with sample thumbnails, a processing zone showing detected text regions and a pipeline checklist that includes the font-homogeneity check, and a results carousel of per-region cards whose badge carries one of the three verdicts KNOWN, UNKNOWN, or MIXED](../../../assets/figures/app_wireframe.png)

*Note.* Three-zone single page. Results are a carousel, one card per detected region: Region 1 accepts (Top-3 in palette); Region 2, reached with the next arrow, is rejected as out-of-palette (max similarity < τ), demonstrating open-set behavior.

### 3.2 Hardware Interfaces

No dedicated hardware interface exists. The system runs on a commodity laptop; an NVIDIA GPU, when present, is used through the standard CUDA driver stack, and CPU-only operation is supported. No scanners, sensors, or printers are involved.

### 3.3 Software Interfaces

| Interface | Purpose | Data exchanged |
| :--- | :--- | :--- |
| `POST /predict` (FastAPI REST) | Client sends the image; server returns results. | Request: image (multipart). Response: JSON — per crop, bounding box + Top-K `{font, score}` + `known` flag. |
| HuggingFace Hub | Load DINOv2 + baseline weights at startup. | Model tensors (read-once). |
| Google Fonts assets | Palette matching + preview rendering of candidate fonts. | Font files (`.ttf`/`.woff2`). |

### 3.4 Communications Interfaces

All client–server traffic is HTTP over `localhost` (REST, JSON, multipart upload). No external network traffic occurs at request time, no email or notification channels exist, and no TLS is required for the single-machine demo.

## 4. System Features

### 4.1 Image Input

#### 4.1.1 Description and Priority

User supplies a GenAI image by drag-drop, file browse, or a bundled sample. Priority: **High**.

#### 4.1.2 Stimulus/Response Sequences

User drops/selects an image → client shows a preview and enables **Identify Fonts** → click posts the image to `/predict`.

#### 4.1.3 Functional Requirements

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-4.1-1 | The system shall accept an image via drag-drop, file picker, or a bundled sample. | High |
| REQ-4.1-2 | The system shall accept raster images in PNG (`.png`), JPEG (`.jpg`, `.jpeg`), and WebP (`.webp`) up to 10 MB, and reject any other type (e.g., SVG, GIF, HEIC, TIFF) with a clear message. | High |
| REQ-4.1-3 | The system shall display a preview of the uploaded image before processing. | Med |
| REQ-4.1-4 | The app shall bundle a pool of at least 10 real AI-generated sample images (e.g., DALL·E, Midjourney, Stable Diffusion output), none part of any training data; the samples offered shall be randomly selected from this pool at each start-up, and the interface shall label their origin. | Med |

### 4.2 Text Localization and Processing

#### 4.2.1 Description and Priority

The backend finds text regions and prepares each crop for matching. Priority: **High**.

#### 4.2.2 Stimulus/Response Sequences

`/predict` receives the image → localizer returns bounding boxes → each crop is preprocessed and embedded → status advances in the Processing zone.

#### 4.2.3 Functional Requirements

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-4.2-1 | The system shall localize text at word granularity (one bounding box per word) and crop each word for independent matching. | High |
| REQ-4.2-2 | The system shall preprocess each crop (square-pad → 224² → grayscale → normalize) inside the model forward pass. | High |
| REQ-4.2-3 | The system shall show processing status/progress and detected-region boxes while inference runs. | Med |
| REQ-4.2-4 | The system should return an informative error if no text region is found. | Med |
| REQ-4.2-5 | The system shall check each crop for font homogeneity using the encoder's patch-level features; a flagged crop shall be split once at the detected boundary and each half matched independently. | High |

### 4.3 Font Matching and Top-K Results

#### 4.3.1 Description and Priority

For each crop, the system ranks the palette and decides known, unknown, or mixed typography. Priority: **High**.

#### 4.3.2 Stimulus/Response Sequences

Embedding is compared to the palette → if best similarity ≥ τ, return the ranked Top-K; else mark the crop out-of-palette.

#### 4.3.3 Functional Requirements

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-4.3-1 | The system shall return a Top-K (K = 3) ranked shortlist of Google Fonts per crop, each with a similarity score. | High |
| REQ-4.3-2 | The system shall reject a crop as "unknown / out-of-palette" when its best similarity falls below threshold τ (open-set). | High |
| REQ-4.3-3 | The system shall present each result as its own card in a carousel with previous/next navigation and a region indicator (e.g., "Region 1 of 2"), each card labeled KNOWN, UNKNOWN, or MIXED. | High |
| REQ-4.3-4 | The system should report a typographic-distance (SSIM) score between the crop and the top match. | Low |
| REQ-4.3-5 | The backend should log each crop's similarity scores and its threshold (τ) decision for researcher analysis; these diagnostics are not shown in the user interface. | Low |
| REQ-4.3-6 | The system shall report a crop that remains font-inhomogeneous after one split as "mixed typography" rather than assigning a single font, and shall merge adjacent word crops that share the same verdict into one region card. | High |

### 4.4 Font Preview

#### 4.4.1 Description and Priority

The user visually confirms a match against live-rendered candidates. Priority: **Med**.

#### 4.4.2 Stimulus/Response Sequences

For each candidate font, the app renders the detected text string in that font beside the crop.

#### 4.4.3 Functional Requirements

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-4.4-1 | The system shall render each shortlisted font as a live preview of the detected text. | Med |
| REQ-4.4-2 | The system should let the user copy a candidate font's name for reuse. | Low |

## 5. Other Nonfunctional Requirements

### 5.1 Performance Requirements

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-5.1-1 | The system shall return results for a single-image, ≤5-region upload within ~10 s on the demo laptop (CPU acceptable). | High |
| REQ-5.1-2 | Model weights shall load once at startup, not per request. | High |

### 5.2 Safety Requirements

The system controls no physical process, so no physical-safety hazards exist. Against data loss: uploaded images are processed in memory and never written to disk, so a crash can lose at most the in-flight request; model weights and font assets are read-only at runtime.

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-5.2-1 | The system shall open model weights and font assets read-only at runtime, so a failed request cannot corrupt them. | Med |

### 5.3 Security Requirements

As a single-user local demo the app has no authentication and no persistence; no personal data is collected, so no retention obligations arise under data-privacy regulation.

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-5.3-1 | The system shall process uploads in memory and discard them when the request completes; no upload shall be stored beyond the request lifetime. | High |
| REQ-5.3-2 | The server shall bind only to the `localhost` interface and accept no remote connections. | Med |

### 5.4 Software Quality Attributes

| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| REQ-5.4-1 | Usability: a first-time user shall complete upload → results without instructions, in one page with no navigation. | High |
| REQ-5.4-2 | Usability: scores and known/unknown status shall be visible without interaction. | Med |
| REQ-5.4-3 | Reliability: the system shall handle an unreadable/oversized/textless upload without crashing, returning a clear message. | High |
| REQ-5.4-4 | Portability: the system shall run from a single Docker image on a clean machine with no manual dependency setup. | Med |

### 5.5 Business Rules

- Only fonts from the open-source Google Fonts palette may be named in a result; the system never identifies or recommends a commercial font.
- A crop whose best similarity falls below τ must be reported as unknown; the system never forces a closed-set label onto an out-of-palette crop.
- Bundled sample images must come from real generative-AI output and must never overlap any training data.

## 6. Other Requirements

- **Licensing:** every runtime component and font asset is open-source; the system shall carry no mandatory license or subscription cost.
- **Data retention:** none — the system stores no user data (see REQ-5.3-1).
- **Internationalization:** the interface is English-only; the recognition palette is limited to Latin-script fonts, matching the thesis scope.

## Appendix A: Glossary

| Term | Definition |
| :--- | :--- |
| Typographic hallucination | Probabilistic glyph deformation (warping, kerning jitter, smear) that GenAI introduces into rendered text. |
| Palette | The curated closed set of 50–100 known Google Fonts the model can name. |
| Open-set / reject | Returning "unknown" when a crop's best match falls below threshold **τ**, instead of forcing a wrong label. |
| Mixed typography | Verdict for a crop whose patch-level features indicate more than one typeface and that stays inhomogeneous after one split; no single font is assigned. |
| Top-K | The K highest-ranked font candidates for one text crop (K = 3 in the demo). |
| Embedding | The fixed-length style vector produced by the DINOv2 encoder + metric head. |
| Prototype | One reference embedding per palette font, the average of that font's training crops; a match is scored against the prototypes, not against raw examples. |
| SSIM | Structural Similarity Index — re-render score between the input crop and the predicted font. |

## Appendix B: Analysis Models

The analysis models for this system live in Chapter 4 and are not duplicated here: the conceptual framework (Fig 8, §4.4.2) models the offline-training versus at-use data flow, the system-architecture diagram (Fig 9, §4.5.2) models the layered client-server structure, and the iterative-incremental SDLC model (Fig 10, §4.6) models the build sequence.

**Traceability.** System features 4.1–4.4 realize the §4.5.1 functional requirements (upload · isolate crop · Top-K or unknown · font preview) and are served by the §4.5.2 architecture (Fig 9). Zones in the §3.1 wireframe map one-to-one to features 4.1 (Input), 4.2 (Processing), and 4.3–4.4 (Results).
