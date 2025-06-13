# DirtGenie Web Application

A modern web frontend for DirtGenie, built with React and FastAPI, providing a complete bikepacking trip planning solution.

## Features

- 🚴‍♂️ **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- 🗺️ **Trip Planning**: Complete bikepacking trip planning with AI assistance  
- 🛞 **Tire Size Integration**: Smart route recommendations based on bike setup
- 📅 **Departure Date Planning**: Weather and seasonal planning capabilities
- ✏️ **Trip Revisions**: Easy plan modifications with AI assistance
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🔄 **Export Options**: Download trip packages and export to Notion
- 🔐 **API Key Management**: User-provided API keys for secure, cost-controlled usage

## Architecture

### Backend (FastAPI)
- RESTful API built with FastAPI
- Direct integration with DirtGenie planner modules
- CORS enabled for frontend communication
- User-provided API key handling
- Automatic API documentation at `/docs`

### Frontend (React + TypeScript)
- Modern React 18 with TypeScript
- Tailwind CSS for styling
- Axios for API communication
- React Markdown for trip plan rendering
- API key setup and management

## Quick Start

1. **Prerequisites**:
   - Python 3.8+
   - Node.js 16+
   - OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
   - Google Maps API Key ([Get one here](https://developers.google.com/maps/documentation/javascript/get-api-key))

2. **Start the Application**:
   ```bash
   ./start.sh
   ```

   This will:
   - Create Python virtual environment
   - Install all dependencies
   - Start both backend (port 8000) and frontend (port 3000)
   - Open your browser to http://localhost:3000

## Manual Setup

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/default-profile` - Get default user profile
- `POST /api/plan-trip` - Plan a new trip
- `POST /api/revise-trip` - Revise an existing trip
- `GET /api/tire-options` - Get available tire sizes
- `POST /api/save-profile` - Save user profile
- `POST /api/download-trip-package` - Download trip files
- `POST /api/export-to-notion` - Export to Notion

## Production Deployment

### Docker (Unified Container)
```bash
# Build the unified container (from project root)
docker build -f Dockerfile.simple -t dirtgenie .

# Run with environment variables
docker run -p 80:80 \
  -e OPENAI_API_KEY=your_key \
  -e GOOGLE_MAPS_API_KEY=your_key \
  dirtgenie
```

### Railway Deployment
1. Deploy using the `railway.json` configuration in the project root
2. Users will be prompted to enter their own API keys on first visit
3. No need to set API keys as environment variables in Railway

## Development

The application is structured for easy development:

- **Backend**: FastAPI with automatic reload
- **Frontend**: React with hot reload
- **API Communication**: Typed interfaces with TypeScript
- **Styling**: Tailwind CSS utility classes
- **API Keys**: Session-based storage for user security

## User Experience

### First-Time Users
1. Visit the application URL
2. Enter OpenAI and Google Maps API keys when prompted
3. Keys are stored in browser session (not persistent)
4. Start planning trips immediately

### API Key Security
- Keys are stored in sessionStorage (cleared when browser closes)
- Keys are sent via request headers to backend
- No server-side storage of user API keys
- Each user uses their own API quotas and billing
