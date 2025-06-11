# DirtGenie Web Application - Quick Start Guide

## 🎉 What We Built

A complete modern web application that replaces the Streamlit dashboard:

### ✅ Backend (FastAPI) - RUNNING ✅
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Features**:
  - RESTful API with automatic documentation
  - Direct integration with DirtGenie planner modules
  - Tire size recommendations included
  - Departure date planning
  - Trip revision capabilities

### 🚀 Frontend (React + TypeScript)
- **URL**: http://localhost:3000 (when started)
- **Features**:
  - Modern, responsive UI with Tailwind CSS
  - Complete trip planning form with tire size selection
  - Trip results display with markdown rendering
  - Mobile-friendly design
  - Real-time API communication

## 🏃‍♂️ Quick Start

### Backend is Already Running! ✅
The FastAPI backend is running on port 8000. You can test it:
```bash
curl http://localhost:8000/health
```

### Start the Frontend:
```bash
cd /Users/fiona/code/dirtgenie/web/frontend
npm start
```

### Or Use the Automated Script:
```bash
cd /Users/fiona/code/dirtgenie/web
./start.sh
```

## 🧪 Testing the API

The backend is fully functional. Test these endpoints:

1. **Health Check**: 
   ```bash
   curl http://localhost:8000/health
   ```

2. **Default Profile**:
   ```bash
   curl http://localhost:8000/api/default-profile
   ```

3. **Tire Options**:
   ```bash
   curl http://localhost:8000/api/tire-options
   ```

4. **API Documentation**: Visit http://localhost:8000/docs

## 🎯 Key Features Implemented

### ✅ Tire Size Integration
- 16 predefined tire options
- Custom tire size input
- Smart route recommendations based on tire capabilities
- Visual tire type indicators (road/gravel/mountain)

### ✅ Complete Trip Planning
- Start/end location input
- Nights selection (1-30)
- Departure date planning
- All preferences from original Streamlit app

### ✅ Modern Architecture
- **Decoupled**: Frontend and backend are separate
- **Scalable**: Easy to deploy and maintain
- **Type-safe**: TypeScript for reliable development
- **Fast**: React for responsive UI, FastAPI for high-performance API

## 🚀 Next Steps

1. **Start the frontend**: `cd frontend && npm start`
2. **Open**: http://localhost:3000
3. **Plan a trip**: Fill out the form and test the full workflow
4. **Enjoy**: Your new modern bikepacking planner!

## 🆚 Streamlit vs React Comparison

| Feature          | Streamlit     | React Web App      |
| ---------------- | ------------- | ------------------ |
| UI Framework     | Python-based  | React + TypeScript |
| Customization    | Limited       | Full control       |
| Mobile           | Basic         | Responsive design  |
| Performance      | Server-side   | Client-side        |
| Deployment       | Single app    | Microservices      |
| State Management | Session-based | React state        |
| API              | Built-in      | RESTful API        |

The new web app provides all the functionality of the Streamlit version with a modern, professional interface!
