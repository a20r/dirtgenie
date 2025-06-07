# 🚴‍♀️ DirtGenie - AI-Powered Bikepacking Trip Planner

An intelligent trip planner that creates detailed bikepacking itineraries using OpenAI's GPT models and Google Maps routing data. DirtGenie features both a powerful CLI tool and a beautiful web interface built with Streamlit.

## ✨ Features

### 🧠 Intelligent Planning
- **AI-Powered Tour Planning**: Uses OpenAI to intelligently plan waypoints and overnight stops
- **3-Step Methodology**: Plan → Route → Generate for optimized experiences
- **Personalized Recommendations**: Tailors trips to your preferences and fitness level
- **Iterative Feedback**: Revise plans with natural language feedback until perfect

### 🗺️ Advanced Routing
- **Bicycle-Specific Routing**: Uses Google Maps API for bike-optimized directions
- **Multi-Waypoint Support**: Plans complex routes with multiple strategic stops
- **Rich Output Formats**: Detailed markdown plans + GeoJSON for mapping apps

### �️ Dual Interface
- **🖥️ Web App**: Beautiful Streamlit interface with interactive maps and real-time feedback
- **⌨️ CLI Tool**: Powerful command-line interface for automation and scripting
- **📱 Mobile-Friendly**: Web interface works great on tablets and phones

### 🎯 Smart Customization
- **Accommodation Types**: Camping, hotels, or mixed options
- **Fitness Levels**: Beginner to advanced with appropriate daily distances
- **Terrain Preferences**: Paved roads, gravel, mixed, or challenging routes
- **Budget Options**: Budget-conscious to luxury experiences
- **Special Interests**: Nature, food, photography, history, and more

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Google Maps API Key ([Setup guide](https://console.cloud.google.com/))

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/a20r/DirtGenie.git
cd DirtGenie

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 2. API Setup

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
```

Or set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export GOOGLE_MAPS_API_KEY="your-google-maps-api-key-here"
```

### 3. Run the Web App (Recommended)

```bash
# Start the Streamlit web interface
streamlit run src/dirtgenie/web_app.py

# Or use the convenience script
./scripts/dirtgenie-web
```

Open your browser to `http://localhost:8501` and start planning!

### 4. Use the CLI Tool

```bash
# Plan a trip from command line
python src/dirtgenie/planner.py "San Francisco, CA" "Los Angeles, CA" 7

# Or use the convenience script
./scripts/dirtgenie "Portland, OR" "Seattle, WA" 5
```

## 🐳 Docker Quick Start

### Run with Docker (Recommended)

```bash
# Run the web app
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_key_here \
  -e GOOGLE_MAPS_API_KEY=your_google_key_here \
  ghcr.io/a20r/dirtgenie:latest

# Or use docker-compose for easier management
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "GOOGLE_MAPS_API_KEY=your_google_key_here" >> .env
docker-compose up dirtgenie-web
```

### Docker Commands

```bash
# Start web interface
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_key \
  -e GOOGLE_MAPS_API_KEY=your_google_key \
  ghcr.io/a20r/dirtgenie:latest web

# Run CLI command
docker run -v $(pwd):/data \
  -e OPENAI_API_KEY=your_openai_key \
  -e GOOGLE_MAPS_API_KEY=your_google_key \
  ghcr.io/a20r/dirtgenie:latest cli --start "Berlin" --end "Prague" --days 7

# Interactive shell
docker run -it \
  -e OPENAI_API_KEY=your_openai_key \
  -e GOOGLE_MAPS_API_KEY=your_google_key \
  ghcr.io/a20r/dirtgenie:latest shell

# Show help
docker run ghcr.io/a20r/dirtgenie:latest help
```

## 📖 Usage Examples

### Web Interface
1. **Open the web app**: `streamlit run src/dirtgenie/web_app.py`
2. **Enter your API keys** in the sidebar
3. **Plan your trip**: Fill in start/end locations, nights, and preferences
4. **Get your plan**: View detailed itinerary and interactive map
5. **Provide feedback**: Use natural language to refine your plan
6. **Download**: Get markdown plan and GeoJSON route data

### Command Line Examples

```bash
# Weekend wine country tour
./scripts/dirtgenie "Sonoma, CA" "Napa, CA" 2

# Cross-state adventure
./scripts/dirtgenie "Denver, CO" "Moab, UT" 10

# Pacific Coast classic
./scripts/dirtgenie "San Francisco, CA" "Los Angeles, CA" 14
```

## 🏗️ Project Structure

```
DirtGenie/
├── src/dirtgenie/           # Main package
│   ├── __init__.py          # Package initialization
│   ├── planner.py           # Core planning logic (CLI)
│   └── web_app.py           # Streamlit web interface
├── scripts/                 # Convenience scripts
│   ├── dirtgenie            # CLI entry point
│   └── dirtgenie-web        # Web app entry point
├── tests/                   # Test suite
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
├── setup.py                 # Package setup
└── README.md               # This file
```

## 🧠 How It Works

DirtGenie uses a sophisticated 3-step planning methodology that creates better bikepacking experiences:

### 1. 🎯 Plan Tour Itinerary
- AI analyzes your preferences, fitness level, and trip duration
- Determines optimal waypoints and overnight locations
- Plans realistic daily distances and strategic stops
- Considers terrain, interests, and accommodation preferences

### 2. 🗺️ Get Multi-Waypoint Directions  
- Uses Google Maps to get bicycle-specific directions
- Connects all planned waypoints with bike-optimized routes
- Calculates precise distances and elevation profiles
- Ensures route quality while hitting desired destinations

### 3. 📝 Generate Detailed Plan
- Creates comprehensive day-by-day itineraries
- Searches for current accommodation availability and pricing
- Adds points of interest, food stops, and practical advice
- Incorporates real-time weather and local conditions

### 💬 Iterative Feedback (Web App Only)
- Review your generated plan
- Provide natural language feedback ("more camping", "shorter days", etc.)
- AI revises the plan based on your input
- Repeat until you're completely satisfied

## 📱 Web App Features

The Streamlit web interface provides a user-friendly experience with:

- **📊 Interactive Dashboard**: Input fields for all trip parameters
- **🗺️ Live Map Visualization**: See your route with overnight stops marked
- **📄 Formatted Trip Plans**: Beautiful, readable itineraries
- **💬 Feedback System**: Iteratively improve your plan with natural language
- **📥 Download Options**: Get markdown plans and GeoJSON route data
- **🔧 API Key Management**: Secure in-session storage of your credentials
- **📱 Mobile-Friendly**: Works great on tablets and phones

## 🎯 Smart Features

### Accommodation Intelligence
- **Mixed Options**: Combines camping, hotels, and unique stays
- **Budget Awareness**: Finds options matching your budget range
- **Availability Checking**: Searches for current availability and pricing
- **Backup Options**: Provides multiple accommodation choices per location

### Route Optimization  
- **Fitness-Appropriate**: Distances tailored to your cycling level
- **Terrain-Aware**: Considers your preference for paved vs. gravel vs. challenging routes
- **Interest-Based**: Incorporates stops for photography, food, history, nature
- **Weather-Informed**: Accounts for seasonal conditions and forecasts

### Safety & Practicality
- **Emergency Planning**: Includes backup plans and emergency contacts
- **Resupply Points**: Identifies food and water sources along the route
- **Bike Shops**: Locates repair services and bike shops
- **Local Tips**: Provides region-specific advice and considerations

## 🛠️ API Requirements

### Google Maps APIs (Required)
Enable these APIs in [Google Cloud Console](https://console.cloud.google.com/):
- **Directions API**: For bicycle routing
- **Geocoding API**: For location lookup
- **Places API**: For accommodation and POI search (optional)

### OpenAI API (Required)
- GPT-4 or GPT-3.5-turbo access
- Sufficient quota for trip planning (typically 2000-4000 tokens per plan)

## 📊 Output Formats

### 1. Detailed Markdown Report
```markdown
# Your Bikepacking Adventure: San Francisco to Los Angeles

## Trip Overview
- Duration: 7 nights, 8 days
- Total Distance: 542 km
- Daily Average: 77 km

## Day 1: San Francisco to Santa Cruz (89 km)
### Route
- Start: Golden Gate Park, San Francisco
- Highlights: Pacific Coast Highway, Half Moon Bay
- End: Santa Cruz Beach Boardwalk

### Accommodation
- **Primary**: Santa Cruz KOA Kampground ($45/night)
- **Backup**: Dream Inn Santa Cruz ($180/night)
...
```

### 2. GeoJSON Route Data
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[-122.4194, 37.7749], ...]
      },
      "properties": {
        "name": "Main Route",
        "distance_km": 542.1,
        "type": "route"
      }
    },
    {
      "type": "Feature", 
      "geometry": {
        "type": "Point",
        "coordinates": [-121.9018, 36.9741]
      },
      "properties": {
        "name": "Santa Cruz KOA",
        "type": "overnight_accommodation",
        "day": 1
      }
    }
  ]
}
```

## 🔧 Development

### Running Tests
```bash
# Run the test suite
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/dirtgenie
```

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `python -m pytest`
5. Submit a pull request

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/

# Type checking
mypy src/
```

## 💡 Tips & Best Practices

### Planning Your Trip
- **Be specific with locations**: Include city/state for better routing
- **Start small**: Try a 2-3 night trip first to test the system
- **Check seasonal conditions**: AI provides seasonal advice, but verify current conditions
- **Review generated routes**: Always verify routes and accommodations before departure

### Using the Tools
- **Web App**: Best for interactive planning and iterative refinement
- **CLI Tool**: Great for batch processing or scripting multiple trips
- **API Quotas**: Monitor your OpenAI and Google Maps API usage
- **Offline Backup**: Download offline maps as backup for remote areas

### Route Quality
- Google Maps bicycle routing is generally excellent but may occasionally suggest roads unsuitable for loaded touring
- Cross-reference with local cycling resources and recent rider reports
- Use the route as a starting point and refine based on local knowledge

## 🐛 Troubleshooting

### Common Issues

**"No route found"**
- Check location spelling and try more specific addresses
- Ensure locations are bicycle-accessible (not across oceans!)
- Try alternative nearby locations if remote areas cause issues

**API Key errors**
- Verify keys are set correctly in `.env` file or environment variables
- Check API quotas and billing status in respective consoles
- Ensure required APIs are enabled in Google Cloud Console

**Poor route suggestions**
- Provide more specific preferences (terrain type, fitness level)
- Use the feedback system in the web app to refine results
- Consider the route as a starting point for manual refinement

**Streamlit app issues**
- Clear browser cache and restart the app
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version compatibility (3.8+)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT models that power the intelligent planning
- **Google Maps** for comprehensive bicycle routing data
- **Streamlit** for the amazing web app framework
- **The bikepacking community** for inspiration and real-world testing

## 🚀 Roadmap

### Upcoming Features
- **GPX Export**: Direct export to GPX format for GPS devices
- **Elevation Profiles**: Visual elevation charts and climbing analysis
- **Weather Integration**: Real-time weather forecasts and alerts
- **Community Features**: Share and discover routes from other users
- **Mobile App**: Native mobile application for on-the-go planning

### Long-term Vision
- **Multi-modal Planning**: Integrate train/bus connections for point-to-point trips
- **Group Planning**: Plan trips for multiple riders with different preferences
- **Real-time Updates**: Live route updates based on conditions and closures
- **AI Learning**: Improve recommendations based on user feedback and trip reports

---

**Happy bikepacking! 🏕️🚴‍♀️**

*DirtGenie - Where AI meets adventure*
