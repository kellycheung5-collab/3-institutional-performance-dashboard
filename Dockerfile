# Base image: Official lightweight Python runtime
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and database
COPY . .

# Expose Gunicorn port
EXPOSE 8050

# Run application using Gunicorn
CMD ["gunicorn", "app.app:server", "--bind", "0.0.0.0:8050", "--workers", "4", "--threads", "2", "--timeout", "120"]