FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq-dev gcc build-essential netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Set UV to use copy mode instead of hardlink
ENV UV_LINK_MODE=copy

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Install Playwright and browser dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN uv run playwright install --with-deps chromium

# Copy entire project
COPY . .

# Ensure logs/staticfiles/media directories exist
RUN mkdir -p logs staticfiles media

# Make entrypoint executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]