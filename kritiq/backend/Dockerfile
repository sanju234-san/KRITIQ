# ── Build stage ──────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

# Install OS-level deps (none needed right now, but layer is cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Runtime stage ────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy only installed packages from build stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Install Playwright Chromium and system dependencies
RUN playwright install chromium --with-deps

# Copy application code
COPY app/ app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
