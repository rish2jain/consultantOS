# Multi-stage optimized build for ConsultantOS
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

# Install numpy first to prevent binary compatibility issues
# This ensures all packages are built against the same numpy version
RUN pip install --user --no-warn-script-location \
    --no-cache-dir "numpy>=1.24.0,<2.0.0"

# Install remaining dependencies with wheel caching
# This creates wheels that can be reused across builds
RUN pip install --user --no-warn-script-location \
    --no-cache-dir -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Update PATH to include user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Expose port (default to 8080, but Cloud Run sets PORT dynamically)
EXPOSE 8080

# Health check (use PORT env var if set, default to 8080)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import os, requests; port = os.getenv('PORT', '8080'); requests.get(f'http://localhost:{port}/health', timeout=5)" || exit 1

# Run application (respect PORT env var set by Cloud Run, default to 8080)
CMD ["sh", "-c", "uvicorn consultantos.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
