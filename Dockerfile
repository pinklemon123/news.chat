# Dockerfile for FastAPI backend
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY api /app

# Start backend service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]