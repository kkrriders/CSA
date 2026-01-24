FROM python:3.11.9-slim

# Force rebuild - updated 2026-01-24
WORKDIR /app

# Install system deps for pillow, pymongo, and SSL libraries for MongoDB
RUN apt-get update && apt-get install -y \
    gcc \
    ca-certificates \
    libssl-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY adaptive-learning-platform/backend ./backend

# Change working directory to backend so Python can find the 'app' module
WORKDIR /app/backend

# Upgrade build tools
RUN pip install --upgrade pip setuptools wheel

# Install python deps (now we're in /app/backend)
RUN pip install -r requirements-prod.txt

# Start FastAPI - use app.main:app since we're in /app/backend directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
