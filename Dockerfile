# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies (add postgresql-client here)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add project root to Python path so "config" and "src" can be imported
ENV PYTHONPATH=/app

# Command to run the ETL script
CMD ["python", "src/data_ingestion.py"]
