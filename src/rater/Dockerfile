# Rater app image. Build context is the repo root (Coolify: base directory "/", Dockerfile "/src/rater/Dockerfile").
# data/real (crops, rater links, answers, audit log) is NOT in the image: mount it at /app/data/real.
FROM oven/bun:1 AS web
WORKDIR /web
COPY src/rater/package.json src/rater/bun.lock ./
RUN bun install --frozen-lockfile
COPY src/rater/ ./
RUN bun run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# same pins as requirements.txt (the server imports render_corpus, which needs cv2)
RUN pip install --no-cache-dir numpy==2.2.6 pillow==12.3.0 opencv-python-headless==5.0.0.93
COPY src/data/render_corpus.py src/data/render_mixed.py src/data/words.txt src/data/
COPY src/rater/server.py src/rater/
COPY --from=web /web/dist src/rater/dist
COPY data/palette.csv data/unknown.csv data/
COPY data/fonts data/fonts
EXPOSE 8000
CMD ["python", "src/rater/server.py", "--host", "0.0.0.0", "--port", "8000"]
