## 4.8 Software Development and Tools

The stack is chosen against a few criteria: every tool is free and open-source, so the system can be replicated at no licensing cost, which is consistent with the free-reconstruction goal of the study; each is mature and widely supported, so documentation and community help are available; and each is the standard choice in its layer, which keeps the learning curve low for a two-person team. Because the served system is stateless and persists nothing between requests (Section 4.7.2), no database is used, so the database-connectivity criterion does not apply. Table 2 lists the tools by function, with the version used and an access link; the role each tool plays is discussed below the table.

**Table 2**

*Software and Tools Used in the Development of the System*

| Function | Tool | Version | Access link |
|----------|------|---------|-------------|
| Language and model | Python | 3.13 | https://www.python.org |
| Language and model | PyTorch | 2.6 | https://pytorch.org |
| Language and model | Hugging Face Transformers | 4.49 | https://github.com/huggingface/transformers |
| Language and model | Hugging Face Hub | 0.28 | https://huggingface.co |
| Language and model | NumPy | 2.2 | https://numpy.org |
| Language and model | scikit-learn | 1.6 | https://scikit-learn.org |
| Data and rendering | Pillow (PIL) | 11.1 | https://python-pillow.org |
| Data and rendering | OpenCV | 4.11 | https://opencv.org |
| Data and rendering | EasyOCR | 1.7 | https://github.com/JaidedAI/EasyOCR |
| Backend | FastAPI | 0.115 | https://fastapi.tiangolo.com |
| Backend | Uvicorn | 0.34 | https://www.uvicorn.org |
| Backend | Pydantic | 2.10 | https://docs.pydantic.dev |
| Frontend | React | 19 | https://react.dev |
| Frontend | Vite | 6 | https://vite.dev |
| Frontend | Node.js | 22 LTS | https://nodejs.org |
| Deployment | Docker | 27 | https://www.docker.com |
| Version control | Git | 2.47 | https://git-scm.com |
| Version control | GitHub | (web service) | https://github.com |
| Documentation | Matplotlib | 3.10 | https://matplotlib.org |
| Documentation | Pandoc | 3.10 | https://pandoc.org |
| Documentation | Visual Studio Code | 1.98 | https://code.visualstudio.com |

*Note.* Versions are current as of July 2026 and are pinned in the project's dependency lockfiles; a replicator should confirm the latest compatible releases at the time of setup. All tools are open-source and free to use; the hosted collaboration service (GitHub) offers a no-cost tier sufficient for this project.

In the language-and-model layer, Python is the primary language for the data pipeline, the model, and the backend, with PyTorch as the deep-learning framework for the encoder, the metric head, and training. Hugging Face Transformers loads the DINOv2 backbone and the baseline classifiers, the Hugging Face Hub pulls pre-trained weights and stores the trained metric head, NumPy carries the array and numerical operations, and scikit-learn supplies the evaluation metrics, the stratified k-fold split, and the confusion matrix. In data and rendering, Pillow renders font specimens into word-crop images, OpenCV applies the elastic warp and the other degradation operations, and EasyOCR performs the off-the-shelf text localization and cropping. The backend exposes inference through FastAPI's `/predict` REST endpoint, served by the Uvicorn ASGI server, with Pydantic validating request and response schemas; the frontend is a React interface for image upload and the results gallery, built by Vite on the Node.js runtime. Docker containerizes the backend for reproducible deployment, Git and GitHub provide version control and repository hosting, and the documentation toolchain uses Matplotlib to generate the thesis figures, Pandoc to export the Markdown chapters to DOCX, and Visual Studio Code as the primary editor.
