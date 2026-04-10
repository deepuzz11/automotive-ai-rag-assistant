# Use official Python base image (slim for performance)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies for FAISS and production stability
RUN apt-get update && apt-get install -y \
    build-essential \
    libomp-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Optimize pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Copy application code (with ownership assigned to appuser)
COPY --chown=appuser:appuser . .

# Expose port for FastAPI
EXPOSE 8000

# Health check to ensure the container is running correctly
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Metadata
LABEL maintainer="AI Engineer Candidate"
LABEL project="Ford Vehicle Intelligence System"
LABEL version="1.2.0"

# Run application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

