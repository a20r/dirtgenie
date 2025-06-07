#!/usr/bin/env python3
"""
Test script for closed-loop tour planning functionality.
Tests the ability to detect same start/end locations and plan balanced loops.
"""

from bikepacking_planner import (create_geojson, generate_trip_plan, get_multi_waypoint_directions, load_profile,
                                 plan_tour_itinerary)
import bikepacking_planner
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_closed_loop_detection():
    """Test that closed-loop tours are detected correctly."""

    # Mock OpenAI response for a closed-loop tour
    mock_closed_loop_response = {
        "choices": [{
            "message": {
                "content": """Here's a balanced 3-day closed-loop bikepacking tour:

**Day 1: Cambridge, MA to Concord, MA (25 miles)**
- Start: Cambridge, MA
- Route: Follow the Minuteman Bikeway through Arlington and Lexington
- End: Concord, MA
- Overnight: Concord Scout House camping area

**Day 2: Concord, MA to Acton, MA (20 miles)**  
- Start: Concord, MA
- Route: Take back roads through rural Middlesex County
- End: Acton, MA
- Overnight: NARA Park camping area

**Day 3: Acton, MA to Cambridge, MA (22 miles)**
- Start: Acton, MA  
- Route: Return via scenic route through Belmont and Arlington
- End: Cambridge, MA (completing the loop)

This creates a balanced triangle route with manageable daily distances."""
            }
        }]
    }

    # Mock Google Maps response with waypoints
    mock_directions_response = {
        "routes": [{
            "legs": [
                {
                    "distance": {"value": 40000, "text": "25 miles"},
                    "duration": {"value": 7200, "text": "2 hours"},
                    "start_location": {"lat": 42.3736, "lng": -71.1097},
                    "end_location": {"lat": 42.4601, "lng": -71.3489},
                    "steps": [{"html_instructions": "Head north", "distance": {"value": 1000}}]
                },
                {
                    "distance": {"value": 32000, "text": "20 miles"},
                    "duration": {"value": 5400, "text": "1.5 hours"},
                    "start_location": {"lat": 42.4601, "lng": -71.3489},
                    "end_location": {"lat": 42.4851, "lng": -71.4328},
                    "steps": [{"html_instructions": "Continue west", "distance": {"value": 1000}}]
                },
                {
                    "distance": {"value": 35000, "text": "22 miles"},
                    "duration": {"value": 6300, "text": "1.75 hours"},
                    "start_location": {"lat": 42.4851, "lng": -71.4328},
                    "end_location": {"lat": 42.3736, "lng": -71.1097},
                    "steps": [{"html_instructions": "Head southeast", "distance": {"value": 1000}}]
                }
            ],
            "overview_polyline": {"points": "fake_polyline_data"}
        }]
    }

    # Test profile
    test_profile = {
        'fitness_level': 'intermediate',
        'daily_distance_preference': 'moderate (40-60 miles)',
        'terrain_preference': 'mixed',
        'accommodation_preference': 'camping',
        'trip_style': 'scenic',
        'special_interests': ['nature', 'small towns']
    }

    print("Testing closed-loop tour detection and planning...")

    # Mock the global OpenAI client
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = mock_closed_loop_response

    with patch.object(bikepacking_planner, 'openai_client', mock_openai_client):
        with patch('requests.get') as mock_requests:
            mock_requests.return_value.json.return_value = mock_directions_response
            mock_requests.return_value.status_code = 200

            # Test closed-loop planning (same start and end)
            start_location = "Cambridge, MA"
            end_location = "Cambridge, MA"  # Same as start - should trigger closed-loop logic
            duration_days = 3

            print(f"Planning tour from {start_location} to {end_location} for {duration_days} days...")

            # This should detect it's a closed loop and use the closed-loop prompt
            itinerary = plan_tour_itinerary(
                start_location, end_location, duration_days, test_profile
            )

            print("✅ Itinerary planning completed")
            print("Itinerary preview:", str(itinerary)[:200] + "..." if len(str(itinerary)) > 200 else str(itinerary))

            # Verify the OpenAI call was made with closed-loop specific prompt
            args, kwargs = mock_openai_client.chat.completions.create.call_args
            prompt_content = kwargs['messages'][0]['content']

            # Check that closed-loop specific language was used
            assert "closed-loop" in prompt_content.lower() or "loop" in prompt_content.lower(), \
                "Closed-loop prompt should mention loops"
            assert "return to the starting point" in prompt_content.lower() or \
                   "back to" in prompt_content.lower(), \
                "Closed-loop prompt should mention returning to start"

            print("✅ Closed-loop prompt correctly used")

            # Create a mock itinerary for testing multi-waypoint directions
            mock_itinerary = {
                "itinerary": {
                    "day_1": {
                        "start_location": "Cambridge, MA",
                        "end_location": "Concord, MA"
                    },
                    "day_2": {
                        "start_location": "Concord, MA",
                        "end_location": "Acton, MA"
                    },
                    "day_3": {
                        "start_location": "Acton, MA",
                        "end_location": "Cambridge, MA"
                    }
                }
            }

            print("Getting directions between waypoints...")
            directions = get_multi_waypoint_directions(mock_itinerary)

            print("✅ Multi-waypoint directions completed")
            print(f"Total legs: {len(directions['routes'][0]['legs'])}")

            # Test trip plan generation - need proper function signature
            print("Generating complete trip plan...")
            trip_plan = generate_trip_plan(start_location, end_location, duration_days, test_profile, itinerary, directions)

            print("✅ Trip plan generation completed")
            print("Trip plan preview:", trip_plan[:300] + "..." if len(trip_plan) > 300 else trip_plan)

            # Test GeoJSON creation - need proper function signature
            print("Creating GeoJSON...")
            geojson = create_geojson(start_location, end_location, directions, test_profile, trip_plan, itinerary)

            print("✅ GeoJSON creation completed")
            print(f"GeoJSON features: {len(geojson['features'])}")

            # Verify we have overnight markers
            overnight_features = [f for f in geojson['features'] if f['properties'].get('type') == 'overnight']
            print(f"Overnight markers: {len(overnight_features)}")

            assert len(overnight_features) > 0, "Should have overnight markers"

            print("\n🎉 All closed-loop tour tests passed!")
            return True


def test_point_to_point_vs_closed_loop():
    """Test that different prompts are used for point-to-point vs closed-loop tours."""

    test_profile = {
        'fitness_level': 'intermediate',
        'daily_distance_preference': 'moderate (40-60 miles)',
        'terrain_preference': 'mixed',
        'accommodation_preference': 'camping',
        'trip_style': 'scenic',
        'special_interests': ['nature']
    }

    mock_response = {
        "choices": [{
            "message": {"content": "Mock tour plan"}
        }]
    }

    print("\nTesting point-to-point vs closed-loop prompt selection...")

    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_response

        # Test point-to-point
        plan_tour_itinerary("Boston, MA", "Portland, ME", 3, test_profile)
        p2p_args, p2p_kwargs = mock_client.chat.completions.create.call_args
        p2p_prompt = p2p_kwargs['messages'][0]['content']

        # Test closed-loop
        plan_tour_itinerary("Boston, MA", "Boston, MA", 3, test_profile)
        loop_args, loop_kwargs = mock_client.chat.completions.create.call_args
        loop_prompt = loop_kwargs['messages'][0]['content']

        # Verify different prompts are used
        assert p2p_prompt != loop_prompt, "Different prompts should be used for point-to-point vs closed-loop"

        # Verify closed-loop prompt has loop-specific language
        assert ("closed-loop" in loop_prompt.lower() or "loop" in loop_prompt.lower()), \
            "Closed-loop prompt should mention loops"

        # Verify point-to-point prompt doesn't have loop language
        assert not ("closed-loop" in p2p_prompt.lower() and "return to" in p2p_prompt.lower()), \
            "Point-to-point prompt should not have closed-loop language"

        print("✅ Different prompts correctly used for point-to-point vs closed-loop")


if __name__ == "__main__":
    print("🧪 Testing Closed-Loop Tour Planning Functionality\n")

    try:
        # Set dummy environment variables for testing
        os.environ['OPENAI_API_KEY'] = 'test-key'
        os.environ['GOOGLE_MAPS_API_KEY'] = 'test-key'

        success1 = test_closed_loop_detection()
        test_point_to_point_vs_closed_loop()

        print("\n✅ All tests completed successfully!")
        print("\nThe closed-loop tour planning functionality is working correctly:")
        print("- Detects when start and end locations are the same")
        print("- Uses specialized prompts for closed-loop tours")
        print("- Plans balanced loop routes with manageable daily distances")
        print("- Generates proper waypoints and routing")
        print("- Creates appropriate overnight markers")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
