# DirtGenie Unified Web Application

🚀 **Single Docker Container** that runs both the React frontend and FastAPI backend together!

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key
- Google Maps API key

### 1. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Run with Docker Compose (Recommended)
```bash
docker compose -f docker-compose.unified.yml up --build
```

### 3. Or Build and Run Manually
```bash
./build-unified.sh
docker run -p 80:80 --env-file .env dirtgenie-unified
```

### 4. Access the Application
Open your browser to: **http://localhost**

## What's Included

- ✅ **React Frontend** - Modern, interactive web interface with deck.gl map visualization
- ✅ **FastAPI Backend** - High-performance API server with AI trip planning
- ✅ **nginx** - Serves frontend and proxies API calls
- ✅ **Supervisor** - Manages both services in a single container
- ✅ **Health Checks** - Built-in monitoring and auto-restart
- ✅ **Production Ready** - Optimized builds and proper logging

## Architecture

```
┌─────────────────────────────────────┐
│           Single Container          │
├─────────────────────────────────────┤
│  nginx (Port 80)                    │
│  ├─ Serves React frontend           │
│  └─ Proxies /api/* to FastAPI       │
│                                     │
│  FastAPI Backend (Internal 8000)    │
│  ├─ AI trip planning                │
│  ├─ Google Maps integration         │
│  └─ Route optimization              │
│                                     │
│  Supervisor                         │
│  ├─ Manages both services           │
│  └─ Auto-restart on failure         │
└─────────────────────────────────────┘
```

## Features

### Frontend (React + TypeScript)
- 🗺️ Interactive route maps with deck.gl
- 📱 Responsive, mobile-friendly design
- 🎨 Modern UI with Tailwind CSS
- ⚡ Fast, optimized React build

### Backend (FastAPI + Python)
- 🤖 AI-powered trip planning with OpenAI
- 🚴 Bicycle-specific routing with Google Maps
- 📍 Multi-waypoint route optimization
- 🏕️ Overnight location suggestions
- 📊 Detailed trip reports and statistics

## Development

### Run Individual Services (Development)
If you want to run frontend and backend separately for development:

```bash
# Terminal 1 - Backend
cd web/backend
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 - Frontend  
cd web/frontend
npm install
npm start
```

### Build Production Image
```bash
docker build -f Dockerfile.unified -t dirtgenie-unified .
```

### Environment Variables
- `OPENAI_API_KEY` - Required for AI trip planning
- `GOOGLE_MAPS_API_KEY` - Required for routing and geocoding
- `NODE_ENV` - Set to `production` for optimizations

## Troubleshooting

### Container Won't Start
- Check that ports 80 is available
- Verify environment variables are set
- Check logs: `docker logs <container_name>`

### API Calls Failing
- Verify API keys are correct
- Check backend logs for errors
- Ensure `/api/health` endpoint responds

### Frontend Not Loading
- Check nginx configuration
- Verify frontend build completed successfully
- Check browser console for errors

## Health Check
The container includes a health check endpoint:
```bash
curl http://localhost/health
```

## Logs
View logs for both services:
```bash
docker logs <container_name>
```

## Contributing
1. Make changes to source code
2. Test with development setup
3. Build and test unified container
4. Submit pull request

---

**🎯 Happy Bikepacking Planning!** 🚴‍♀️
