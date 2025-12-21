# Backend Dockerfile - FastAPI + Engine

FROM python:3.11-slim AS base

# Install Node.js and npm (needed for BAML CLI)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install BAML CLI globally
RUN npm install -g @boundaryml/baml@0.213.0

# Set working directory
WORKDIR /app

# Copy engine requirements (from root)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy engine package (needed by API)
COPY packages/engine /app/packages/engine

# Generate BAML client in engine
WORKDIR /app/packages/engine
RUN baml generate

# Copy API code
WORKDIR /app/apps/api
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api .

# Set Python path to include engine
ENV PYTHONPATH=/app/packages/engine:${PYTHONPATH}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
