FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
RUN uv sync --no-dev

COPY lucid_server/ lucid_server/

EXPOSE 3001

CMD ["uv", "run", "uvicorn", "lucid_server.main:app", "--host", "0.0.0.0", "--port", "3001"]
