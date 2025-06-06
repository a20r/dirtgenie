# 🎯 Bikepacking Trip Planner - Complete Example

This is a complete, fully functional bikepacking trip planner that uses OpenAI's GPT models and Google Maps API to create intelligent, personalized bikepacking itineraries.

## ✅ What You Get

A fully runnable script that:

1. **Takes simple inputs**: Start location, end location, number of nights
2. **Asks intelligent follow-up questions** to personalize your trip:
   - Accommodation preferences (camping vs hotels)
   - Fitness level and daily distance goals
   - Budget considerations
   - Special interests (photography, food, history, etc.)
   - Terrain preferences

3. **Generates two comprehensive outputs**:
   - **Detailed markdown trip plan** with day-by-day itineraries
   - **High-fidelity GeoJSON file** with complete route data

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys
Run the interactive setup:
```bash
./setup.sh
```

Or manually set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_MAPS_API_KEY="your-google-maps-api-key" 
```

### 3. Plan Your First Trip
```bash
python bikepacking_planner.py "Portland, OR" "Seattle, WA" 5
```

The script will:
- Ask you personalization questions
- Get real bicycle route data from Google Maps  
- Generate an intelligent trip plan with OpenAI
- Save detailed outputs to files

## 📋 Example Usage Session

```bash
$ python bikepacking_planner.py "San Francisco, CA" "Los Angeles, CA" 7

🚴‍♀️ Bikepacking Trip Planner
==================================================
Planning a 7-night trip from San Francisco, CA to Los Angeles, CA

🏕️  Let's customize your bikepacking adventure!
I'll ask you a few questions to tailor the perfect trip for you.

💤 Accommodation preference (camping/hotels/mixed): camping
🏕️  Is stealth camping appropriate/desired? (yes/no): yes
💪 Fitness level (beginner/intermediate/advanced): intermediate
🚴 Preferred daily distance in km (default: 50-80): 60-90
🏔️  Terrain preference (paved/gravel/mixed/challenging): mixed
💰 Daily budget range (budget/moderate/luxury): moderate
🎯 Special interests (food/photography/history/nature/adventure): photography,food,nature

🗺️  Getting route information from Google Maps...
✅ Route found: 684.2 km total distance

🤖 Generating your personalized trip plan with OpenAI...
📍 Creating detailed route GeoJSON...
💾 Saving files...

🎉 Trip planning complete!
📄 Trip plan saved to: bikepacking_trip_San Francisco CA_to_Los Angeles CA_20250606_140230.md
🗺️  Route data saved to: bikepacking_route_San Francisco CA_to_Los Angeles CA_20250606_140230.geojson

Happy bikepacking! 🚴‍♀️🏕️
```

## 📁 Generated Files

### Trip Plan (Markdown)
A comprehensive plan including:
- Daily distances and elevation profiles
- Accommodation recommendations
- Points of interest and photo opportunities  
- Food stops and resupply locations
- Weather considerations
- Packing suggestions
- Safety information
- Emergency contacts

### Route Data (GeoJSON)
Complete route geometry with:
- GPS coordinates for the entire route
- Waypoints and key locations
- Trip metadata and preferences
- Compatible with Garmin, mapping apps, and GIS software

## 🛠️ Testing & Validation

Test the core functionality without API keys:
```bash
python test_planner.py
```

Check your setup:
```bash
python demo.py
```

## 🌟 Key Features

- **Real Google Maps bicycle routing** - not just straight lines
- **Intelligent AI planning** - considers fitness, preferences, and local knowledge
- **Interactive customization** - asks the right questions to personalize your trip
- **Professional output formats** - ready to use for actual trip planning
- **Comprehensive safety info** - includes emergency planning and local considerations
- **Budget planning** - estimates costs based on your preferences
- **Seasonal awareness** - provides weather and seasonal riding advice

## 🔧 Technical Details

- **OpenAI Integration**: Uses GPT-4 for intelligent trip planning
- **Google Maps API**: Real bicycle routing with turn-by-turn directions
- **Polyline Decoding**: High-fidelity route geometry extraction
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Extensible Design**: Easy to add new features and customizations

This is a production-ready tool that creates genuinely useful bikepacking itineraries by combining the power of AI with real-world route data.

---

**Ready to plan your next adventure? 🚴‍♀️🏕️**
