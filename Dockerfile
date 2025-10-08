# Multi-stage Docker build for WordPress Management App optimized for Render.com
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Update npm and clear cache
RUN npm install -g npm@10.8.2 && npm cache clean --force

# Copy package files
COPY frontend/package*.json ./

# Create .npmrc file to handle peer dependency issues
RUN echo "legacy-peer-deps=true" > .npmrc && \
    echo "fund=false" >> .npmrc && \
    echo "audit=false" >> .npmrc

# Install dependencies with error handling
RUN npm ci --legacy-peer-deps --no-optional --no-fund --no-audit || \
    npm install --legacy-peer-deps --no-optional --no-fund --no-audit

# Copy frontend source
COPY frontend/ ./

# Build frontend with optimizations
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV CI=true
ENV GENERATE_SOURCEMAP=false
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend

# Copy built frontend from first stage (with fallback)
COPY --from=frontend-builder /app/frontend/build ./frontend_build

# Create a simple index.html fallback if frontend build fails
RUN if [ ! -f "./frontend_build/index.html" ]; then \
        mkdir -p ./frontend_build && \
        echo '<!DOCTYPE html><html><head><title>CVLTURE WordPress Manager</title></head><body><h1>Loading...</h1><script>window.location.href="/api/";</script></body></html>' > ./frontend_build/index.html; \
    fi

# Expose port for Render.com
EXPOSE 10000

# Set environment variables for Render.com
ENV PORT=10000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/api/ || exit 1

# Start command optimized for Render.com
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "10000"]