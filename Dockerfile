# Minimal Dockerfile for the Python FastAPI backend on Railway
FROM python:3.11-slim

# Prevent python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install deps first (better caching)
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source
COPY backend /app

# Expose the port Railway sets via $PORT
ENV PORT=8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "${PORT}"]
