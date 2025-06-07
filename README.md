# 🚴‍♀️ Intelligent Bikepacking Trip Planner

An AI-powered trip planner that creates detailed bikepacking itineraries using OpenAI's GPT models and Google Maps routing data. The planner uses an intelligent 3-step methodology: **Plan → Route → Generate** for truly optimized bikepacking experiences.

## 🧠 Intelligent Planning Methodology

Unlike simple route planners that just find the shortest path and add accommodations along it, this planner uses a sophisticated 3-step approach:

1. **🎯 Plan Tour Itinerary**: Uses AI to first determine interesting destinations, optimal daily distances, and strategic overnight locations based on your preferences
2. **🗺️ Get Multi-Waypoint Directions**: Uses Google Maps to get bicycle directions between the planned waypoints  
3. **📝 Generate Detailed Plan**: Creates comprehensive trip plans with accommodations, attractions, and practical advice based on the optimized route

This "plan-first" approach creates more meaningful and enjoyable bikepacking adventures compared to "route-first" methods.

## Features

- **🤖 AI-Powered Tour Planning**: Uses OpenAI to intelligently plan waypoints and overnight stops before routing
- **🚴‍♀️ Bicycle-Specific Routing**: Uses Google Maps API to get bicycle-specific directions between planned waypoints
- **🎯 Personalized Recommendations**: Asks follow-up questions to tailor trips to your preferences
- **📋 Detailed Itineraries**: Generates comprehensive day-by-day plans with accommodations, points of interest, and practical advice
- **🗺️ Rich Output Formats**: 
  - Detailed markdown trip plan with day-by-day breakdown
  - GeoJSON file with high-fidelity route data for mapping applications
  - **Precise overnight accommodation markers** showing exactly where you'll camp/stay each night
  - Enhanced metadata including daily highlights and distance estimates
- **⚙️ Flexible Preferences**: Accommodates various fitness levels, accommodation types, budgets, and interests
- **🔄 Backwards Compatible**: Maintains compatibility with existing tools and workflows

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key

#### Google Maps API Key  
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Directions API
   - Geocoding API
   - Maps JavaScript API (optional, for viewing routes)
4. Create credentials (API Key)
5. Copy the key

### 3. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export GOOGLE_MAPS_API_KEY="your-google-maps-api-key-here"
```

Or create a `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
```

## Usage

```bash
python bikepacking_planner.py "San Francisco, CA" "Los Angeles, CA" 7
```

### Arguments
- `start`: Starting location (city, address, or landmark)
- `end`: Ending location (city, address, or landmark)  
- `nights`: Number of nights for the trip

### Interactive Questions

The script will ask you several questions to customize your trip:

- **Accommodation preference**: camping, hotels, or mixed
- **Stealth camping**: whether wild/stealth camping is appropriate
- **Fitness level**: beginner, intermediate, or advanced
- **Daily distance**: preferred daily cycling distance
- **Terrain preference**: paved roads, gravel, mixed, or challenging
- **Budget**: budget, moderate, or luxury
- **Special interests**: food, photography, history, nature, adventure, etc.

## Output Files

### Trip Plan (Markdown)
A comprehensive markdown file containing:
- Trip overview and route summary
- Day-by-day detailed itinerary
- Accommodation recommendations
- Points of interest and attractions
- Packing suggestions
- Safety and emergency information  
- Budget estimates
- Local tips and considerations

### Route Data (GeoJSON)
A detailed GeoJSON file containing:
- Complete route geometry with coordinates
- Trip metadata (distance, duration, preferences)
- Waypoints and key locations
- Compatible with mapping applications like:
  - [geojson.io](https://geojson.io)
  - QGIS
  - Garmin BaseCamp
  - Mobile mapping apps

## Example Usage

```bash
# Plan a week-long trip from Portland to Seattle
python bikepacking_planner.py "Portland, OR" "Seattle, WA" 6

# Plan a weekend trip in wine country
python bikepacking_planner.py "Sonoma, CA" "Napa, CA" 2

# Plan a cross-state adventure
python bikepacking_planner.py "Denver, CO" "Moab, UT" 10
```

## Tips

- **Be specific with locations**: Include city/state or use specific addresses for better routing
- **Check your API quotas**: Both OpenAI and Google Maps APIs have usage limits
- **Review generated routes**: Always verify routes and accommodations before your trip
- **Download offline maps**: Consider downloading offline maps as backup
- **Check seasonal conditions**: The AI will provide seasonal advice, but always verify current conditions

## Troubleshooting

### Common Issues

1. **"No route found"**: 
   - Check location spelling
   - Try more specific addresses
   - Ensure locations are bikeable (not across oceans!)

2. **API Key errors**:
   - Verify keys are set correctly
   - Check API quotas and billing
   - Ensure required APIs are enabled in Google Cloud

3. **Poor route quality**:
   - Google Maps bicycle routing may suggest roads unsuitable for loaded touring
   - Always cross-reference with local cycling resources
   - Consider using the route as a starting point for manual refinement

## 🔧 Technical Improvements

### New 3-Step Planning Architecture

The planner has been completely redesigned with a new intelligent methodology:

#### Step 1: `plan_tour_itinerary()` 
- Uses OpenAI to plan the tour **before** getting directions
- Determines optimal waypoints based on user preferences and trip duration
- Identifies strategic overnight locations (camping areas, towns with services)
- Plans daily distances appropriate for fitness level and terrain
- Returns structured JSON with waypoints, overnight locations, and daily highlights

#### Step 2: `get_multi_waypoint_directions()`
- Gets bicycle-specific directions between planned waypoints
- Uses Google Maps Directions API with multiple intermediate stops
- Ensures the route connects all planned destinations optimally
- Maintains high route quality while hitting desired waypoints

#### Step 3: `generate_trip_plan()`
- Creates detailed day-by-day plans based on the optimized route
- Incorporates real distance/timing data from Google Maps
- Enhances overnight locations with specific accommodation details
- Adds practical advice tailored to the actual route

### Enhanced GeoJSON Output

- **Precise Overnight Markers**: Uses waypoint coordinates instead of distance estimates
- **Rich Metadata**: Includes daily highlights, distances, and accommodation details  
- **Structured Properties**: Each marker includes day information and precise location data
- **Enhanced Compatibility**: Works seamlessly with mapping applications and GPS devices

### Backwards Compatibility

- All existing functions and interfaces remain functional
- Fallback mechanisms ensure operation even with limited API access
- Test suite validates both old and new workflows
- Existing GeoJSON files remain compatible with mapping tools

## Contributing

Feel free to submit issues and enhancement requests!

---

**Happy bikepacking! 🏕️🚴‍♀️**
