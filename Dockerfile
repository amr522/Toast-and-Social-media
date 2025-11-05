FROM python:3.11-slim AS base

# Install system deps for building some Python packages
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies first (better cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8080

EXPOSE 8080

# Default command starts the health/API server
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

