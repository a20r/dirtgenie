# DirtGenie Unified Docker Container

This unified Docker container runs both the React frontend and FastAPI backend in a single container, making it easy to deploy and run the complete DirtGenie web application.

## Architecture

- **Frontend**: React app built and served by nginx on port 80
- **Backend**: FastAPI server running on internal port 8000
- **Proxy**: nginx proxies `/api/*` requests to the FastAPI backend
- **Process Management**: supervisor manages both nginx and FastAPI processes

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Build and run
docker-compose -f docker-compose.unified.yml up --build
```

### Option 2: Using Docker Build Script

```bash
# Build the container
./build-unified.sh

# Run with environment file
docker run -p 80:80 --env-file .env dirtgenie-unified

# Or run with inline environment variables
docker run -p 80:80 \
  -e OPENAI_API_KEY=your_openai_key \
  -e GOOGLE_MAPS_API_KEY=your_google_maps_key \
  dirtgenie-unified
```

### Option 3: Manual Docker Commands

```bash
# Build the image
docker build -f Dockerfile.unified -t dirtgenie-unified .

# Run the container
docker run -p 80:80 \
  -e OPENAI_API_KEY=your_openai_key \
  -e GOOGLE_MAPS_API_KEY=your_google_maps_key \
  dirtgenie-unified
```

## Access the Application

Once running, visit: **http://localhost**

- Frontend: Served directly by nginx
- API: Available at `/api/*` endpoints (proxied to FastAPI)
- Health check: http://localhost/health

## Environment Variables

Required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key for trip planning
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key for route calculation

## Development vs Production

### Development Mode
For development, it's still recommended to run frontend and backend separately:

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend  
cd frontend
npm start
```

### Production Mode
Use the unified container for production deployments:

```bash
docker-compose -f docker-compose.unified.yml up -d
```

## Container Structure

```
/app/
├── backend/           # FastAPI backend source
├── frontend/build/    # Built React app (served by nginx)
├── src/              # Shared DirtGenie source code
└── start-unified.sh  # Container startup script
```

## Logs

View logs from both services:

```bash
# All logs
docker-compose -f docker-compose.unified.yml logs -f

# Backend only
docker exec -it <container> tail -f /var/log/supervisor/fastapi.log

# Frontend/nginx only
docker exec -it <container> tail -f /var/log/supervisor/nginx.log
```

## Health Monitoring

The container includes a health check endpoint at `/health` that returns:
- HTTP 200 "healthy" when services are running
- Used by Docker health checks and load balancers

## Troubleshooting

### Container won't start
1. Check that ports 80 is available
2. Verify environment variables are set
3. Check logs: `docker logs <container_name>`

### API calls failing
1. Check that backend is running: `curl http://localhost/health`
2. Verify API keys are properly set
3. Check nginx proxy configuration in container

### Frontend not loading
1. Verify nginx is serving files: `curl http://localhost`
2. Check that React build completed successfully
3. Inspect browser network tab for errors

## Files

- `Dockerfile.unified`: Multi-stage build for the unified container
- `nginx.conf`: nginx configuration for serving frontend and proxying API
- `supervisord.conf`: Supervisor configuration for managing processes
- `start-unified.sh`: Container startup script
- `build-unified.sh`: Helper script for building the container
- `docker-compose.unified.yml`: Docker Compose configuration
