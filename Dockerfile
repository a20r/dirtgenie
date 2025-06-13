# Simplified Single-Stage Unified Dockerfile for DirtGenie
# This builds frontend and backend in a single stage to avoid Docker snapshot issues

FROM python:3.11-slim

# Set environment variables to avoid debconf issues
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    gcc \
    nginx \
    supervisor \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy and install Python backend dependencies
COPY web/backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source and main dirtgenie source
COPY web/backend/ ./backend/
COPY src ./src

# Copy and build frontend
COPY web/frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci --only=production

COPY web/frontend/ ./
# Set production environment for build so API uses /api instead of localhost:8000
ENV NODE_ENV=production
RUN npm run build

# Switch back to app directory
WORKDIR /app

# Configure nginx to serve frontend and proxy API calls
COPY web/nginx.conf /etc/nginx/nginx.conf

# Create supervisor configuration
COPY web/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create startup script
COPY web/start-unified.sh /app/start-unified.sh
RUN chmod +x /app/start-unified.sh

# Create non-root user and set permissions
RUN useradd --create-home --shell /bin/bash dirtgenie \
    && chown -R dirtgenie:dirtgenie /app \
    && mkdir -p /var/log/nginx /var/lib/nginx \
    && chown -R dirtgenie:dirtgenie /var/log/nginx \
    && chown -R dirtgenie:dirtgenie /var/lib/nginx

# Expose port 80 for the unified app
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/app/src
ENV NODE_ENV=production

# Use startup script to run both services
CMD ["/app/start-unified.sh"]
