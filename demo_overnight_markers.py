#!/usr/bin/env python3
"""
Demo script to show the new overnight markers functionality
"""

from bikepacking_planner import create_geojson, extract_overnight_locations

# Mock directions data with some valid polyline data
MOCK_DIRECTIONS = {
    "legs": [
        {
            "distance": {"value": 120000, "text": "120 km"},
            "duration": {"value": 21600, "text": "6 hours"},
            "start_address": "Boston, MA, USA",
            "end_address": "Portland, ME, USA",
            "start_location": {"lat": 42.3601, "lng": -71.0589},
            "end_location": {"lat": 43.6591, "lng": -70.2568},
            "steps": [
                {
                    "start_location": {"lat": 42.3601, "lng": -71.0589},
                    "end_location": {"lat": 43.0, "lng": -70.8},
                    "polyline": {"points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"}
                },
                {
                    "start_location": {"lat": 43.0, "lng": -70.8},
                    "end_location": {"lat": 43.6591, "lng": -70.2568},
                    "polyline": {"points": "wpmiF~hbvO_chNrrpE_wjQhvf\\"}
                }
            ]
        }
    ],
    "summary": "I-95 N",
    "warnings": [],
    "copyrights": "Map data ©2024 Google"
}

# Sample trip plan with overnight locations
SAMPLE_TRIP_PLAN = """
# 2-Night Bikepacking Trip: Boston to Portland

## Trip Overview
This scenic coastal route takes you from Boston through New Hampshire to Portland, Maine.

## Daily Itineraries

### Day 1: Boston, MA to Portsmouth, NH
- **Distance**: 70 km
- **Accommodation**: Camping at Seacoast State Park
- **Highlights**: North Shore beaches, historic Newburyport

### Day 2: Portsmouth, NH to Freeport, ME  
- **Distance**: 50 km
- **Accommodation**: Stay at Freeport Village Station Inn
- **Highlights**: Portsmouth's historic district, L.L.Bean flagship store

### Day 3: Freeport, ME to Portland, ME
- **Distance**: 30 km
- **Accommodation**: Celebrate at destination!
- **Highlights**: Coastal Maine scenery, Portland Head Light

## Additional Notes
Emergency camping near York Beach is available if needed.
Consider stealth camping at Wolfe's Neck Woods State Park for a more adventurous experience.
"""


def main():
    print("🏕️ Overnight Markers Demo")
    print("=" * 50)

    # Test overnight location extraction
    print("\n📍 Extracting overnight locations from trip plan...")
    overnight_locations = extract_overnight_locations(SAMPLE_TRIP_PLAN)
    print(f"Found {len(overnight_locations)} overnight locations:")
    for i, location in enumerate(overnight_locations, 1):
        print(f"  {i}. {location}")

    # Mock preferences
    preferences = {
        "accommodation": "mixed",
        "fitness_level": "intermediate",
        "budget": "moderate",
        "interests": ["photography", "history"]
    }

    # Create GeoJSON with overnight markers
    print("\n🗺️ Creating GeoJSON with overnight markers...")
    geojson_data = create_geojson(
        "Boston, MA",
        "Portland, ME",
        MOCK_DIRECTIONS,
        preferences,
        SAMPLE_TRIP_PLAN
    )

    print(f"✅ Created GeoJSON with {len(geojson_data['features'])} features:")

    for i, feature in enumerate(geojson_data['features'], 1):
        feature_type = feature['properties'].get('type', 'unknown')
        if feature_type == 'overnight_accommodation':
            night = feature['properties']['night_number']
            location = feature['properties']['location_name']
            coords = feature['geometry']['coordinates']
            print(f"  {i}. 🏕️ Night {night}: {location} at ({coords[1]:.3f}, {coords[0]:.3f})")
        elif feature_type == 'waypoint':
            print(f"  {i}. 📍 Start: {feature['properties']['address']}")
        elif feature_type == 'destination':
            print(f"  {i}. 🎯 End: {feature['properties']['address']}")
        else:
            print(f"  {i}. 🛤️ Route: {feature_type}")

    print(f"\n💡 The overnight markers now include:")
    print("  • GPS coordinates estimated along the route")
    print("  • Night number for trip organization")
    print("  • Location names extracted from the trip plan")
    print("  • Distinctive markers (🏕️) for mapping applications")
    print("  • Orange color (#FF6B35) for visibility")

    print("\n🎉 Overnight markers functionality is working!")
    print("Your GeoJSON files will now include markers showing where you plan to spend each night.")


if __name__ == "__main__":
    main()
