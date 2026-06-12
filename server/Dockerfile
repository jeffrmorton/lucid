FROM python:3.13-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

COPY lucid_server/ lucid_server/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home appuser
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/lucid_server /app/lucid_server

ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 3001
CMD ["uvicorn", "lucid_server.main:app", "--host", "0.0.0.0", "--port", "3001"]
