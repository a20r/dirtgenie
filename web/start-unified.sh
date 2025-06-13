#!/bin/bash
set -e

echo "🚀 Starting DirtGenie Unified Web Application..."
echo "Frontend: React app served by nginx on port 80"
echo "Backend: FastAPI server on internal port 8000"
echo "Visit: http://localhost:80"

# Create necessary directories
mkdir -p /var/log/supervisor
mkdir -p /var/log/nginx
mkdir -p /var/lib/nginx/body
mkdir -p /var/lib/nginx/fastcgi
mkdir -p /var/lib/nginx/proxy
mkdir -p /var/lib/nginx/scgi
mkdir -p /var/lib/nginx/uwsgi

# Set proper permissions
chown -R dirtgenie:dirtgenie /var/log/supervisor
touch /var/log/nginx/access.log /var/log/nginx/error.log
chown dirtgenie:dirtgenie /var/log/nginx/access.log /var/log/nginx/error.log

# Test nginx configuration
nginx -t

# Start services with supervisor
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
