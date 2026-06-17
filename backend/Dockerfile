# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for common Python packages)
RUN apt-get update && apt-get install -y \
    build-essential sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for caching)
COPY requirements.txt ./requirements.txt
COPY pyproject.toml ./pyproject.toml

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy source code (so setuptools can see /app/src/backend)
COPY src ./src/

# Editable install (now src exists)
RUN pip install -e .
RUN mkdir -p /data

# Expose FastAPI port
EXPOSE 8000

# Default command: run FastAPI app with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
