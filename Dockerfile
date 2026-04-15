FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
# - libpq-dev: PostgreSQL client headers (needed by psycopg)
# - gcc / build-essential: compile C extensions
# - dos2unix: fix Windows line endings on shell scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq-dev gcc build-essential dos2unix \
    && rm -rf /var/lib/apt/lists/*

# uv: fast Python package installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_LINK_MODE=copy

# Install Python deps first (layer-cached unless pyproject.toml / uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Playwright — install chromium for PDF generation
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN uv run playwright install --with-deps chromium

# Copy application source
COPY . .

# Ensure runtime directories exist
RUN mkdir -p logs staticfiles media

# Fix Windows line endings and make executable
COPY entrypoint.sh .
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]