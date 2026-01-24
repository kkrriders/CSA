FROM python:3.11.9-slim

WORKDIR /app

# Install system deps for pillow, pymongo etc
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY adaptive-learning-platform/backend ./backend

# Upgrade build tools
RUN pip install --upgrade pip setuptools wheel

# Install python deps
RUN pip install -r backend/requirements.txt

# Start FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
