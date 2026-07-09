## 4.4 Concept

### 4.4.1 Core Concept and Vision

The system is a font-identification service for hallucinated type. Given a fragment of text lifted from a generative-AI image, it returns a ranked shortlist of the closest open-source Google Fonts, or an explicit "unknown" verdict when the glyph belongs to no font in its palette. Its purpose is practical reconstruction: letting a designer rebuild a generative image's typography from a free, license-clear palette instead of paying a commercial identifier to name a font that may not be reusable. The framework is deliberately scoped. Rather than matching against the entire commercial typeface universe, it trades exhaustive coverage for a tractable, localized palette of the top 50 to 100 Google Fonts, which is what makes free reconstruction possible. A web application built on top of the model exposes this capability interactively, so the system can be tested in real time on uploaded images.

### 4.4.2 Conceptual Framework

The framework follows an input-process-output (IPO) structure, shown in Figure 8. The input is a graphic designer and the generative-AI image they supply, whose text is probabilistically deformed. The process is a three-layer stack: a web-app frontend that accepts the upload and displays results, a backend API that routes the request, and the ML inference engine that does the recognition. Inside the engine, the crop is preprocessed, encoded by a frozen DINOv2 Vision Transformer, projected by the metric head $f_\theta$ into a font-style embedding, and passed to the open-set decision that either rejects the crop as unknown or ranks the palette. The output is a Top-K Google Fonts shortlist, or an unknown verdict, returned to the designer, who uses it for free template reuse. A separate offline subsystem, the researchers' synthetic rendering, degradation, and triplet-training pipeline, produces the trained weights the engine loads, and appears as the lower band feeding the encoder and head.

**Figure 8**

*Conceptual Framework of the Proposed Font-Identification System*

![Input-process-output diagram showing a graphic designer and GenAI image feeding a web-app frontend, backend API, and ML inference engine (preprocessing, frozen DINOv2 encoder, metric head, open-set decision), producing a Top-K Google Fonts shortlist or unknown verdict, with an offline synthetic-training subsystem supplying the model weights](../../../assets/figures/conceptual_framework.png)

As shown in Figure 8, the runtime path (designer to frontend to backend to inference engine to shortlist) is cleanly separated from the offline training path (Google Fonts to synthetic render to degradation to triplet training). The two meet at a single point: the trained weights loaded by the frozen encoder and metric head. This separation is what lets the same model serve real-time web requests while remaining fully reproducible from the researcher-controlled data pipeline.

### 4.4.3 Value Proposition

The design suits its problem for three reasons. It is open-set: unlike a closed-set classifier that must name some font for every input, it can refuse, which matters when many generative crops correspond to no real typeface. It is trained on the hallucination distribution itself rather than on pristine glyphs, so it does not collapse on the warped, re-kerned input that defeats commercial identifiers and clean-glyph baselines. And because it targets a localized open-source palette, every match it returns is immediately reusable at no cost, turning recognition into a usable reconstruction rather than a paywalled lookup.

### 4.4.4 High-Level Operational Logic

From the user's side the interaction is simple. A designer opens the web application, uploads a generative-AI image containing text, and waits a moment while the system isolates the text crop and runs it through the inference engine. The application then displays a short, ranked list of candidate Google Fonts, each shown as a rendered preview, or an "unknown" message when the system judges the glyph to fall outside its palette. The designer picks the closest match and reuses it directly in their own document. The user needs no knowledge of embeddings, thresholds, or the training pipeline; the technical machinery of Sections 4.2 and 4.3 stays hidden behind a single upload-and-review interaction.
