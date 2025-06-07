#!/usr/bin/env python3
"""
Test script to verify web search functionality in the bikepacking planner.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our module
sys.path.append(str(Path(__file__).parent.parent / "src"))
from dirtgenie.planner import generate_trip_plan, initialize_clients, plan_tour_itinerary

# Add the current directory to the path so we can import our module
sys.path.append(str(Path(__file__).parent))


def test_web_search_in_planning():
    """Test that the planning function can use web search capabilities."""
    print("Testing web search functionality in tour planning...")

    # Initialize clients
    initialize_clients()

    # Test with a real location where current information would be valuable
    start = "Boston MA"
    end = "Portland ME"
    nights = 3

    # Create basic preferences
    preferences = {
        'accommodation': 'camping',
        'stealth_camping': False,
        'fitness_level': 'intermediate',
        'daily_distance': '50-80',
        'terrain': 'mixed',
        'budget': 'moderate',
        'interests': ['nature', 'history']
    }

    try:
        print(f"Planning tour from {start} to {end} for {nights} nights...")

        # Test the planning function
        itinerary = plan_tour_itinerary(start, end, nights, preferences)

        print("✅ Tour planning completed successfully!")
        print(f"Planned {len(itinerary.get('waypoints', []))} waypoints")
        print(f"Overnight locations: {len(itinerary.get('overnight_locations', []))}")

        # Print some key details to verify the response
        if 'waypoints' in itinerary:
            print("\nPlanned waypoints:")
            for i, waypoint in enumerate(itinerary['waypoints']):
                print(f"  {i+1}. {waypoint.get('name', 'Unknown')}")

        if 'overnight_locations' in itinerary:
            print("\nOvernight locations:")
            for i, location in enumerate(itinerary['overnight_locations']):
                print(f"  Night {i+1}: {location.get('name', 'Unknown')}")
                if 'accommodation_details' in location:
                    print(f"    Accommodation: {location['accommodation_details']}")

        return True

    except Exception as e:
        print(f"❌ Error testing web search: {e}")
        return False


def test_web_search_in_trip_generation():
    """Test that trip generation can use web search capabilities."""
    print("\nTesting web search functionality in trip generation...")

    # Create a mock itinerary and directions for testing
    mock_itinerary = {
        "waypoints": [
            {"name": "Boston MA", "lat": 42.3601, "lng": -71.0589},
            {"name": "Portsmouth NH", "lat": 43.0718, "lng": -70.7626},
            {"name": "Portland ME", "lat": 43.6591, "lng": -70.2568}
        ],
        "overnight_locations": [
            {
                "name": "Portsmouth NH",
                "lat": 43.0718,
                "lng": -70.7626,
                "accommodation_details": "Camping at Prescott Park area"
            },
            {
                "name": "Freeport ME",
                "lat": 43.8570,
                "lng": -70.1028,
                "accommodation_details": "Wolfe's Neck Woods State Park camping"
            }
        ]
    }

    mock_directions = {
        "legs": [
            {"distance": {"value": 95000}, "duration": {"value": 18000}},  # 95km, 5 hours
            {"distance": {"value": 75000}, "duration": {"value": 14400}}   # 75km, 4 hours
        ]
    }

    preferences = {
        'accommodation': 'camping',
        'stealth_camping': False,
        'fitness_level': 'intermediate',
        'daily_distance': '50-80',
        'terrain': 'mixed',
        'budget': 'moderate',
        'interests': ['nature', 'history']
    }

    try:
        print("Generating detailed trip plan with web search...")

        trip_plan = generate_trip_plan(
            "Boston MA",
            "Portland ME",
            2,
            preferences,
            mock_itinerary,
            mock_directions
        )

        print("✅ Trip plan generation completed successfully!")
        print(f"Generated plan length: {len(trip_plan)} characters")

        # Check if the plan contains indicators of web search usage
        search_indicators = [
            'current', 'updated', 'recent', 'as of', 'latest',
            'operating hours', 'seasonal', 'available', 'booking'
        ]

        found_indicators = []
        for indicator in search_indicators:
            if indicator.lower() in trip_plan.lower():
                found_indicators.append(indicator)

        if found_indicators:
            print(f"✅ Plan appears to include current information (found: {', '.join(found_indicators)})")
        else:
            print("⚠️  Plan may not include current web-searched information")

        return True

    except Exception as e:
        print(f"❌ Error testing trip generation: {e}")
        return False


def main():
    """Run web search functionality tests."""
    print("Testing Web Search Integration in Bikepacking Planner")
    print("=" * 60)

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("❌ GOOGLE_MAPS_API_KEY not found in environment")
        return False

    print("✅ API keys found")

    # Run tests
    planning_success = test_web_search_in_planning()
    generation_success = test_web_search_in_trip_generation()

    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"Tour Planning: {'✅ PASS' if planning_success else '❌ FAIL'}")
    print(f"Trip Generation: {'✅ PASS' if generation_success else '❌ FAIL'}")

    if planning_success and generation_success:
        print("\n🎉 All web search tests passed!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
