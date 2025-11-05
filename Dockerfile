# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY mcq_api/requirements.txt /app/requirements.txt
COPY data_loader/requirements.txt /app/data_loader_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r data_loader_requirements.txt

# Copy application code
COPY . /app/

# Create data directory for database
RUN mkdir -p /app/data

# Copy database if it exists, otherwise create empty directory
COPY data_loader/nclex_simple.db* /app/ 2>/dev/null || true

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:$PORT/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "mcq_api.main:app", "--host", "0.0.0.0", "--port", "8000"]