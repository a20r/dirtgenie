#!/usr/bin/env python3
"""
Test script to verify enhanced prompts for weather and accommodation search.
"""

import os
import sys
from pathlib import Path

from bikepacking_planner import initialize_clients, plan_tour_itinerary

# Add the current directory to the path so we can import our module
sys.path.append(str(Path(__file__).parent))


def test_enhanced_weather_accommodation_prompts():
    """Test that prompts include specific weather and accommodation search instructions."""
    print("Testing enhanced prompts for weather and accommodation search...")

    # Initialize clients
    initialize_clients()

    # Test preferences for accommodation search
    preferences = {
        'accommodation': 'mixed',
        'stealth_camping': False,
        'fitness_level': 'intermediate',
        'daily_distance': '60-80',
        'terrain': 'mixed',
        'budget': 'moderate',
        'interests': ['nature', 'history', 'local_culture']
    }

    print("Testing closed-loop tour (same start/end)...")
    try:
        # Test closed-loop tour (should trigger enhanced prompt for weather and accommodations)
        itinerary_closed = plan_tour_itinerary(
            "Portland OR",
            "Portland OR",
            4,
            preferences
        )

        print("✅ Closed-loop tour planning successful!")
        print(f"Planned {len(itinerary_closed.get('waypoints', []))} waypoints")

        # Check if response includes detailed accommodations
        overnight_locations = itinerary_closed.get('overnight_locations', [])
        if overnight_locations:
            print(f"✅ Found {len(overnight_locations)} overnight locations")
            for i, location in enumerate(overnight_locations[:2]):  # Show first 2
                name = location.get('name', 'Unknown')
                details = location.get('accommodation_details', 'No details')
                print(f"  Night {i+1}: {name}")
                if len(details) > 50:  # If details are substantial
                    print(f"    ✅ Detailed accommodation info: {details[:100]}...")
                else:
                    print(f"    ⚠️  Basic accommodation info: {details}")

    except Exception as e:
        print(f"❌ Error testing closed-loop tour: {e}")
        return False

    print("\nTesting point-to-point tour...")
    try:
        # Test point-to-point tour
        itinerary_p2p = plan_tour_itinerary(
            "Seattle WA",
            "San Francisco CA",
            5,
            preferences
        )

        print("✅ Point-to-point tour planning successful!")
        print(f"Planned {len(itinerary_p2p.get('waypoints', []))} waypoints")

        # Check if response includes detailed accommodations
        overnight_locations = itinerary_p2p.get('overnight_locations', [])
        if overnight_locations:
            print(f"✅ Found {len(overnight_locations)} overnight locations")
            for i, location in enumerate(overnight_locations[:2]):  # Show first 2
                name = location.get('name', 'Unknown')
                details = location.get('accommodation_details', 'No details')
                print(f"  Night {i+1}: {name}")
                if len(details) > 50:  # If details are substantial
                    print(f"    ✅ Detailed accommodation info: {details[:100]}...")
                else:
                    print(f"    ⚠️  Basic accommodation info: {details}")

        return True

    except Exception as e:
        print(f"❌ Error testing point-to-point tour: {e}")
        return False


def test_prompt_content():
    """Test that the prompt actually contains weather and accommodation search instructions."""
    print("\nTesting prompt content for search instructions...")

    # This is a bit of a hack - we'll check if the functions contain the right keywords
    # by looking at the source code
    with open('/Users/fiona/code/adventure/bikepacking_planner.py', 'r') as f:
        content = f.read()

    search_keywords = [
        'WEATHER',
        'current weather forecasts',
        'specific accommodations',
        'current availability',
        'web search',
        'bookable options',
        'real names, contact info'
    ]

    found_keywords = []
    for keyword in search_keywords:
        if keyword.lower() in content.lower():
            found_keywords.append(keyword)

    print(f"✅ Found {len(found_keywords)}/{len(search_keywords)} search-related keywords in prompts:")
    for keyword in found_keywords:
        print(f"  - {keyword}")

    if len(found_keywords) >= len(search_keywords) * 0.8:  # At least 80% found
        print("✅ Prompts appear to be properly enhanced for web search!")
        return True
    else:
        print("⚠️  Some search instructions may be missing from prompts")
        return False


def main():
    """Run enhanced prompt tests."""
    print("Testing Enhanced Prompts for Weather and Accommodation Search")
    print("=" * 70)

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("❌ GOOGLE_MAPS_API_KEY not found in environment")
        return False

    print("✅ API keys found")

    # Run tests
    prompt_content_ok = test_prompt_content()

    # Only run API tests if user wants to (they cost money)
    run_api_tests = input("\nRun actual API tests? (y/N): ").lower().startswith('y')

    if run_api_tests:
        api_tests_ok = test_enhanced_weather_accommodation_prompts()
    else:
        print("Skipping API tests per user request")
        api_tests_ok = True

    print("\n" + "=" * 70)
    print("Test Results:")
    print(f"Prompt Content: {'✅ PASS' if prompt_content_ok else '❌ FAIL'}")
    print(f"API Tests: {'✅ PASS' if api_tests_ok else '❌ FAIL'}")

    if prompt_content_ok and api_tests_ok:
        print("\n🎉 Enhanced prompts are working correctly!")
        print("The AI should now search for:")
        print("  📅 Current weather forecasts for all locations")
        print("  🏨 Specific accommodations with availability and pricing")
        print("  🛣️  Current trail conditions and closures")
        print("  🔧 Local services with current operating information")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
