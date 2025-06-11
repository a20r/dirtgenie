# DirtGenie Web Application

A modern web frontend for DirtGenie, built with React and FastAPI, providing an alternative to the Streamlit dashboard.

## Features

- 🚴‍♂️ **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- 🗺️ **Trip Planning**: Complete bikepacking trip planning with AI assistance  
- 🛞 **Tire Size Integration**: Smart route recommendations based on bike setup
- 📅 **Departure Date Planning**: Weather and seasonal planning capabilities
- ✏️ **Trip Revisions**: Easy plan modifications with AI assistance
- 📱 **Mobile Friendly**: Responsive design that works on all devices

## Architecture

### Backend (FastAPI)
- RESTful API built with FastAPI
- Direct integration with DirtGenie planner modules
- CORS enabled for frontend communication
- Automatic API documentation at `/docs`

### Frontend (React + TypeScript)
- Modern React 18 with TypeScript
- Tailwind CSS for styling
- Axios for API communication
- React Markdown for trip plan rendering

## Quick Start

1. **Prerequisites**:
   - Python 3.8+
   - Node.js 16+
   - OpenAI API Key
   - Google Maps API Key

2. **Environment Setup**:
   ```bash
   # Set your API keys in the parent directory's .env file
   echo "OPENAI_API_KEY=your_key_here" >> ../.env
   echo "GOOGLE_MAPS_API_KEY=your_key_here" >> ../.env
   ```

3. **Start the Application**:
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

## Development

The application is structured for easy development:

- **Backend**: FastAPI with automatic reload
- **Frontend**: React with hot reload
- **API Communication**: Typed interfaces with TypeScript
- **Styling**: Tailwind CSS utility classes

## Production Deployment

For production deployment:

1. Build the frontend:
   ```bash
   cd frontend && npm run build
   ```

2. Serve the backend with a production ASGI server:
   ```bash
   cd backend && pip install gunicorn && gunicorn main:app -k uvicorn.workers.UvicornWorker
   ```

3. Serve the built frontend with nginx or similar

## Comparison to Streamlit Version

| Feature           | Streamlit     | React Web App      |
| ----------------- | ------------- | ------------------ |
| UI Framework      | Streamlit     | React + Tailwind   |
| State Management  | Session state | React state        |
| Customization     | Limited       | Full control       |
| Mobile Experience | Basic         | Responsive         |
| API Architecture  | Monolithic    | Decoupled          |
| Deployment        | Single app    | Frontend + Backend |
| Performance       | Server-side   | Client-side        |

## Future Enhancements

- 🗺️ Interactive Leaflet map integration
- 💾 User authentication and profile persistence
- 📊 Trip analytics and statistics
- 🔄 Real-time collaboration on trip planning
- 📱 Progressive Web App (PWA) capabilities
- 🧭 Offline route access

## Contributing

The web application follows modern web development best practices:
- TypeScript for type safety
- Component-based architecture
- API-first design
- Responsive design principles
