FROM python:3.12-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser

RUN apt-get update && apt-get install -y \
    curl \
    # ... other deps
    && rm -rf /var/lib/apt/lists/*


# Copy requirements and install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code and fix ownership
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port and run the app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
