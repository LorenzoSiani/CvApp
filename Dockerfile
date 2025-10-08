# Multi-stage Docker build for WordPress Management App optimized for Render.com
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Install npm latest version and clear cache
RUN npm install -g npm@latest && npm cache clean --force

# Copy package files (using npm instead of yarn)
COPY frontend/package*.json ./

# Install dependencies with legacy peer deps to handle conflicts
RUN npm install --legacy-peer-deps --no-optional

# Copy frontend source
COPY frontend/ ./

# Build frontend with increased memory limit
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend

# Copy built frontend from first stage
COPY --from=frontend-builder /app/frontend/build ./frontend_build

# Expose port for Render.com
EXPOSE 10000

# Set environment variables for Render.com
ENV PORT=10000
ENV PYTHONUNBUFFERED=1

# Start command optimized for Render.com
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "10000"]