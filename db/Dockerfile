# DB Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install SQLite runtime
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy initialization scripts (if any)
COPY init.sql ./init.sql
COPY src ./src

# Install Python dependencies (ORM, LangChain, etc.)
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -e .

# Create a default folder for SQLite DB
RUN mkdir -p /var/lib/sqlite

# Expose mount path for persistence
VOLUME ["/var/lib/sqlite"]

# Default command: run DB service (can be overridden)
CMD ["python", "src/db/main.py"]
