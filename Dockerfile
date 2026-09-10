FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose app port
EXPOSE 8050

# Option A: Bind directly to 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app.app:server"]