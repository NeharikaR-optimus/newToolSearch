
# Use official Python 3.11 image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy config.py from project root
COPY config.py /app/

# Copy backend code and requirements
COPY backend/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (default for FastAPI/uvicorn)
EXPOSE 8000

# Start FastAPI with Gunicorn using Uvicorn workers on port 8000
CMD ["gunicorn", "fastAPI.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
