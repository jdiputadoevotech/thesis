## 4.8 Software Development and Tools

The stack is chosen against a few criteria: every tool is free and open-source, so the system can be replicated at no licensing cost, which is consistent with the free-reconstruction goal of the study; each is mature and widely supported, so documentation and community help are available; and each is the standard choice in its layer, which keeps the learning curve low for a two-person team. Because the served system is stateless and persists nothing between requests (Section 4.7.2), no database is used, so the database-connectivity criterion does not apply. Table 2 lists the tools by function, with the version used, an access link, and its role in the project.

**Table 2**

*Software and Tools Used in the Development of the System*

| Function | Tool | Version | Access link | Use |
|----------|------|---------|-------------|-----|
| Language and model | Python | 3.13 | https://www.python.org | Primary language for the data pipeline, model, and backend |
| Language and model | PyTorch | 2.6 | https://pytorch.org | Deep-learning framework for the encoder, metric head, and training |
| Language and model | Hugging Face Transformers | 4.49 | https://github.com/huggingface/transformers | Loads the DINOv2 backbone and the baseline classifiers |
| Language and model | Hugging Face Hub | 0.28 | https://huggingface.co | Pulls pre-trained weights and stores the trained metric head |
| Language and model | NumPy | 2.2 | https://numpy.org | Array and numerical operations |
| Language and model | scikit-learn | 1.6 | https://scikit-learn.org | Evaluation metrics, stratified k-fold split, confusion matrix |
| Data and rendering | Pillow (PIL) | 11.1 | https://python-pillow.org | Renders font specimens into word-crop images |
| Data and rendering | OpenCV | 4.11 | https://opencv.org | Elastic warp and other degradation operations |
| Data and rendering | EasyOCR | 1.7 | https://github.com/JaidedAI/EasyOCR | Off-the-shelf text localization and cropping |
| Backend | FastAPI | 0.115 | https://fastapi.tiangolo.com | REST inference API (`/predict` endpoint) |
| Backend | Uvicorn | 0.34 | https://www.uvicorn.org | ASGI server that runs the FastAPI app |
| Backend | Pydantic | 2.10 | https://docs.pydantic.dev | Request and response schema validation |
| Frontend | React | 19 | https://react.dev | Browser UI for image upload and the results gallery |
| Frontend | Vite | 6 | https://vite.dev | Frontend build tool and development server |
| Frontend | Node.js | 22 LTS | https://nodejs.org | JavaScript runtime for the frontend toolchain |
| Deployment | Docker | 27 | https://www.docker.com | Containerizes the backend for reproducible deployment |
| Version control | Git | 2.47 | https://git-scm.com | Source-code version control |
| Version control | GitHub | (web service) | https://github.com | Repository hosting and collaboration |
| Documentation | Matplotlib | 3.10 | https://matplotlib.org | Generates the thesis figures |
| Documentation | Pandoc | 3.10 | https://pandoc.org | Exports the Markdown chapters to DOCX |
| Documentation | Visual Studio Code | 1.98 | https://code.visualstudio.com | Primary code editor |

*Note.* Versions are current as of July 2026 and are pinned in the project's dependency lockfiles; a replicator should confirm the latest compatible releases at the time of setup. All tools are open-source and free to use; the hosted collaboration service (GitHub) offers a no-cost tier sufficient for this project.
