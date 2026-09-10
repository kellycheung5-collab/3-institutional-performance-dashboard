FROM python:3.12-slim

WORKDIR /app

# Copy dependencies list
COPY requirements.txt .

# Upgrade pip and install requirements + gunicorn explicitly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project files
COPY . .

# Set Python search path
ENV PYTHONPATH=/app

# Expose default port
EXPOSE 10000

# Run Gunicorn with dynamic port binding
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 --threads 4 app.app:server"]