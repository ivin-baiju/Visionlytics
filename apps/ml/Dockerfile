FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY visionlytics_ml visionlytics_ml
RUN useradd -m ml && chown -R ml /app
USER ml
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/healthz')"
CMD [".venv/bin/uvicorn", "visionlytics_ml.app:app", "--host", "0.0.0.0", "--port", "8000"]
