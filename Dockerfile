# Browser Tracking Server - Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY database.py .
COPY logger.py .
COPY cloud_config.json ./config.json

# Create necessary directories
RUN mkdir -p /var/lib/browser-tracking \
    && mkdir -p /var/log/browser-tracking \
    && mkdir -p /var/backups/browser-tracking

# Create non-root user
RUN useradd -m -u 1000 browsertracking && \
    chown -R browsertracking:browsertracking /app /var/lib/browser-tracking /var/log/browser-tracking /var/backups/browser-tracking

# Switch to non-root user
USER browsertracking

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "server.py"]
