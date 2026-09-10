FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose default port
EXPOSE 10000

# Set Python module path
ENV PYTHONPATH=/app

# Bind dynamically to $PORT (defaults to 10000 on Render)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 --threads 4 app.app:server"]