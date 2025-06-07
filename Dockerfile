# DirtGenie - AI-Powered Bikepacking Trip Planner
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create entrypoint script (do this as root before creating user)
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Install the package in development mode
RUN pip install -e .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash dirtgenie
RUN chown -R dirtgenie:dirtgenie /app
USER dirtgenie

# Expose Streamlit port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app/src
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Default command runs the web app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["web"]
