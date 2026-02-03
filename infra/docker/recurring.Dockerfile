# Recurring Task Service Dockerfile

FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.13-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy service code
COPY backend/services/recurring ./recurring
COPY backend/app/events ./events
COPY backend/app/models ./models
COPY backend/app/services/recurrence_service.py ./services/

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')" || exit 1

# Run the service
CMD ["python", "-m", "recurring.main"]
