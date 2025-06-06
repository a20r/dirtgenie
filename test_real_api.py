#!/usr/bin/env python3
"""
Simple test to validate the improved closed-loop planning with actual API calls.
This will require real API keys but will show if the improvements work.
"""

from bikepacking_planner import initialize_clients, plan_tour_itinerary
import os
import sys
from pathlib import Path

# Load environment from .env if it exists
env_file = Path(".env")
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_with_real_api():
    """Test the improved closed-loop prompt with real API."""

    # Check if we have API keys
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("❌ API keys not found. Please set OPENAI_API_KEY and GOOGLE_MAPS_API_KEY")
        print("This test requires real API keys to validate the improved prompt.")
        return False

    try:
        # Initialize clients
        initialize_clients()
        print("✅ API clients initialized")

        # Test parameters
        start_location = "Cambridge, MA"
        end_location = "Cambridge, MA"  # Same = closed loop
        nights = 3  # Shorter test
        preferences = {
            'daily_distance': '40-50',
            'accommodation': 'camping',
            'stealth_camping': True,
            'fitness_level': 'advanced',
            'terrain': 'mixed',
            'budget': 'moderate',
            'interests': ['nature', 'small towns']
        }

        print(f"Planning {nights + 1}-day closed-loop tour from {start_location}")
        print(f"Daily distance: {preferences['daily_distance']} km")
        print("This should now respect the daily distance constraints for ALL days including the return...")

        # Plan the tour
        result = plan_tour_itinerary(start_location, end_location, nights, preferences)

        print("✅ Tour planning completed!")
        print("\nItinerary summary:")

        if isinstance(result, dict) and 'itinerary' in result:
            for day_key, day_data in result['itinerary'].items():
                if isinstance(day_data, dict):
                    start = day_data.get('start_location', 'Unknown')
                    end = day_data.get('end_location', 'Unknown')
                    distance = day_data.get('estimated_distance_km', 'Unknown')
                    print(f"  {day_key}: {start} → {end} ({distance} km)")

                    # Check if it's a reasonable distance
                    if isinstance(distance, (int, float)) and distance > 60:
                        print(f"    ⚠️  WARNING: {distance} km might exceed daily preference of 40-50 km")

        print(f"\nRoute summary: {result.get('route_summary', 'Not available')}")

        # Check for validation note
        if 'validation_note' in result:
            print(f"✅ Validation: {result['validation_note']}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Testing Improved Closed-Loop Planning with Real API\n")

    success = test_with_real_api()

    if success:
        print("\n✅ Test completed!")
        print("\nImprovements implemented:")
        print("1. Maximum radius calculation (≈87km for 6-day, 40-50km/day trip)")
        print("2. Day-by-day validation checklist ensuring return feasibility")
        print("3. Mathematical constraint: distance_from_start * 1.4 ≤ remaining_days * max_daily")
        print("4. Focus on circular/polygonal patterns, not out-and-back")
        print("5. Explicit validation that final day stays within daily distance limits")
        print("\nThis should prevent the AI from planning destinations too far away!")
    else:
        print("\n❌ Test failed or API keys not available")
        print("To test with real API, set OPENAI_API_KEY and GOOGLE_MAPS_API_KEY in .env file")
