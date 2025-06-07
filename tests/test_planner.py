#!/usr/bin/env python3
"""
Test script for bikepacking planner with mock data
This allows testing the core functionality without API keys
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to the path so we can import our module
sys.path.append(str(Path(__file__).parent.parent / "src"))
from dirtgenie.planner import ask_follow_up_questions, create_geojson, extract_route_points, save_outputs

# Mock Google Maps directions response
MOCK_DIRECTIONS = {
    "legs": [
        {
            "distance": {"value": 85000, "text": "85 km"},
            "duration": {"value": 18000, "text": "5 hours"},
            "start_address": "San Francisco, CA, USA",
            "end_address": "San Jose, CA, USA",
            "start_location": {"lat": 37.7749, "lng": -122.4194},
            "end_location": {"lat": 37.3382, "lng": -121.8863},
            "steps": [
                {
                    "start_location": {"lat": 37.7749, "lng": -122.4194},
                    "end_location": {"lat": 37.7549, "lng": -122.4094},
                    "polyline": {"points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"}
                },
                {
                    "start_location": {"lat": 37.7549, "lng": -122.4094},
                    "end_location": {"lat": 37.3382, "lng": -121.8863},
                    "polyline": {"points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"}
                }
            ]
        }
    ],
    "summary": "US-101 S",
    "warnings": [],
    "copyrights": "Map data ©2024 Google"
}


def generate_mock_trip_plan(start: str, end: str, nights: int, preferences: dict) -> str:
    """Generate a mock trip plan for testing."""

    return f"""# Bikepacking Trip: {start} to {end}

## Trip Overview
- **Duration**: {nights} nights
- **Total Distance**: 85 km
- **Daily Average**: {85/nights:.1f} km per day
- **Accommodation**: {preferences.get('accommodation', 'mixed')}
- **Fitness Level**: {preferences.get('fitness_level', 'intermediate')}

## Day-by-Day Itinerary

### Day 1: {start} to Halfway Point
- **Distance**: 42 km
- **Highlights**: Beautiful coastal views, charming seaside towns
- **Accommodation**: {preferences.get('accommodation', 'camping')} at Seaside Campground
- **Meals**: Breakfast at local café, lunch at scenic overlook, dinner at camp

### Day 2: Halfway Point to {end}
- **Distance**: 43 km  
- **Highlights**: Rolling hills, historic landmarks
- **Accommodation**: Arrive at destination
- **Meals**: Breakfast at camp, lunch in town, celebration dinner

## Packing List
- Tent and sleeping gear
- Bike repair tools
- Weather-appropriate clothing
- First aid kit
- Navigation tools

## Safety Information
- Emergency contacts: 911
- Nearest hospitals along route
- Weather considerations for the season

## Budget Estimate
- **{preferences.get('budget', 'moderate')} budget**: $50-100 per day
- Includes meals, accommodation, and incidentals

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


def test_core_functionality():
    """Test the core functionality with mock data."""

    print("🧪 Testing Bikepacking Trip Planner Core Functionality")
    print("=" * 60)

    # Test parameters
    start = "San Francisco, CA"
    end = "San Jose, CA"
    nights = 2

    print(f"📍 Planning trip from {start} to {end} for {nights} nights")

    # Test preferences collection (skip interactive part for automated testing)
    preferences = {
        'accommodation': 'camping',
        'stealth_camping': True,
        'fitness_level': 'intermediate',
        'daily_distance': '40-60',
        'terrain': 'mixed',
        'budget': 'moderate',
        'interests': ['photography', 'nature']
    }

    print("✅ Mock preferences set")

    # Test route point extraction
    print("🗺️  Testing route point extraction...")
    points = extract_route_points(MOCK_DIRECTIONS)
    print(f"✅ Extracted {len(points)} route points")

    # Test trip plan generation (mock)
    print("� Testing trip plan generation...")
    trip_plan = generate_mock_trip_plan(start, end, nights, preferences)
    print("✅ Generated mock trip plan")

    # Test GeoJSON creation with real trip plan
    print("� Testing GeoJSON creation with trip plan...")
    geojson_data = create_geojson(start, end, MOCK_DIRECTIONS, preferences, trip_plan)
    print(f"✅ Created GeoJSON with {len(geojson_data['features'])} features")

    # Test file saving
    print("💾 Testing file output...")
    md_file, geojson_file = save_outputs(trip_plan, geojson_data, start, end)
    print(f"✅ Saved files:")
    print(f"   📄 {md_file}")
    print(f"   🗺️  {geojson_file}")

    # Display sample content
    print("\n📋 Sample Trip Plan Preview:")
    print("-" * 40)
    print(trip_plan[:500] + "..." if len(trip_plan) > 500 else trip_plan)

    print(f"\n🎉 All core functionality tests passed!")
    print(f"The script structure is working correctly.")
    print(f"To use with real data, set up your API keys and run:")
    print(f"python src/dirtgenie/planner.py --start '{start}' --end '{end}' --nights {nights}")


if __name__ == "__main__":
    test_core_functionality()
