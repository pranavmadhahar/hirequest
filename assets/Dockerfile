# Assets Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for FAISS build)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src
COPY entrypoint.sh ./entrypoint.sh

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -e . \
    && chmod +x entrypoint.sh

# Run full pipeline (preprocess → chunks → index)
CMD ["./entrypoint.sh"]
