## 4.5 Analysis and Design

This section turns the concept of Section 4.4 into a specification. Section 4.5.1 states what the system must do and the qualities it must have, scoped to a local testing deployment rather than a public service. Section 4.5.2 describes the architecture that satisfies those requirements and how its parts communicate.

### 4.5.1 Requirements Analysis

**Functional requirements.** The system must:

1. Accept an uploaded generative-AI image in common raster formats (PNG, JPEG) through the browser.
2. Localize and crop each text region in the image using an off-the-shelf text detector.
3. Preprocess each crop and embed it with the frozen DINOv2 encoder and the trained metric head.
4. Apply the open-set decision to each crop, either rejecting it as "unknown" or ranking the localized palette.
5. Return, for every detected region, a Top-K shortlist of candidate Google Fonts or an "unknown" verdict.
6. Render a preview of each candidate font so the user can compare it against the source text.
7. Expose the recognition pipeline through a REST endpoint (`/predict`) that the frontend calls.
8. Load the trained model weights once at startup and reuse them across requests.

**Non-functional requirements.** The system should also:

1. Be usable through a single upload-and-review interaction that hides the underlying model (usability).
2. Return results at interactive latency on a single machine, targeting a response within a few seconds per image (responsiveness).
3. Produce the same output for the same input, through deterministic preprocessing and pinned model weights and seeds (reproducibility).
4. Run from a single Docker image on one host, with no external service dependencies at inference time beyond the bundled weights and font files (portability).
5. Keep the localizer, encoder, metric head, and open-set decision as separable components, so any one can be replaced without rewriting the others (maintainability).
6. Operate as a single-user local demo, with no authentication, accounts, or multi-user scaling in scope (a deliberate delimitation, consistent with Section 4.1).
7. Report an honest "unknown" rather than a forced guess when the open-set score falls below threshold (transparency).

### 4.5.2 System Architecture

The architecture is a layered client-server design, shown in Figure 9. It separates a thin presentation layer from a Python inference backend, and separates both from the model and font resources they depend on.

**Figure 9**

*System Architecture of the Font-Identification Web Application*

![Layered architecture diagram with a user tier (graphic designer), a client tier (React frontend), an API tier (FastAPI backend in Docker), an inference tier (PyTorch service running text localization, preprocessing, the frozen DINOv2 encoder, the metric head, and the open-set decision), and a resources tier (HuggingFace model store, offline-trained metric-head weights, and Google Fonts assets), with a request path down and a results path back up to the client](../../../assets/figures/system_architecture.png)

As shown in Figure 9, a request flows top to bottom and the result returns to the client. The **client tier** is a React single-page application in the browser: it handles the image upload and renders the Top-K results gallery with font previews. It calls the **API tier**, a FastAPI backend packaged in a Docker image, which exposes the `/predict` endpoint, orchestrates the inference call, and loads the model weights when it starts. The API hands each request to the **inference tier**, a PyTorch service that runs the pipeline of Section 4.4: off-the-shelf text localization, preprocessing, the frozen DINOv2 encoder, the metric head $f_\theta$, and the open-set decision that produces a Top-K shortlist or an "unknown" verdict per crop. The **resources tier** holds what the inference tier reads but does not compute at request time: the DINOv2 backbone and baseline weights pulled from the HuggingFace Hub, the metric-head weights trained offline, and the Google Fonts files used both as the recognition palette and to render the candidate previews.

Two design choices in this layout matter for the rest of the chapter. First, the inference tier is the only stateful-at-startup component and the only one specific to this thesis; the localizer above it and the font assets beside it are replaceable off-the-shelf parts. Second, the offline training that produces the metric-head weights is not part of the request path at all. It runs separately and deposits weights into the resource tier, which keeps the served system reproducible from the researcher-controlled pipeline and lets the model be retrained or swapped without touching the API or the frontend.
