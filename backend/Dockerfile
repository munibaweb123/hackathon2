# syntax=docker/dockerfile:1

# ===================================
# Multi-stage Dockerfile for FastAPI Backend
# Production-optimized with security hardening
# ===================================

# -----------------------------------
# Stage 1: Builder - Has build tools and dependencies
# -----------------------------------
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies for Python packages with native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies into user site-packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -----------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------
FROM python:3.13-slim AS runtime

WORKDIR /app

# Runtime environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONPATH="/home/appuser/.local/lib/python3.13/site-packages:$PYTHONPATH"

# Install runtime dependencies only (libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with UID 10001+ for Kubernetes pod security compliance
# Using numeric UID for portability across container runtimes
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -m appuser && \
    mkdir -p /app && \
    chown -R appuser:appgroup /app

# Copy Python dependencies from builder stage
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user (use numeric UID for portability)
USER 10001

# Expose application port
EXPOSE 8000

# Health check using native Python (no curl needed - smaller attack surface)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/livez')" || exit 1

# Production command with optimized settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
