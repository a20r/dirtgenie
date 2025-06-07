#!/usr/bin/env python3
"""
Test the improved closed-loop tour planning functionality.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_closed_loop_prompt():
    """Test the improved closed-loop prompt generation."""
    from bikepacking_planner import plan_tour_itinerary

    # Mock data
    start_location = "Cambridge, MA"
    end_location = "Cambridge, MA"  # Same location = closed loop
    nights = 5
    preferences = {
        'daily_distance': '40-50',
        'accommodation': 'camping',
        'stealth_camping': True,
        'fitness_level': 'advanced',
        'terrain': 'mixed',
        'budget': 'moderate',
        'interests': ['nature', 'small towns']
    }

    # Import the required modules and set up mocking
    from unittest.mock import MagicMock, patch

    import bikepacking_planner

    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = """{
    "itinerary": {
        "day_1": {
            "start_location": "Cambridge, MA",
            "end_location": "Concord, MA",
            "overnight_location": "Walden Pond State Reservation camping",
            "highlights": ["Walden Pond", "Concord Center"],
            "estimated_distance_km": 45,
            "distance_from_start_km": 30,
            "days_remaining_to_return": 5
        },
        "day_2": {
            "start_location": "Concord, MA", 
            "end_location": "Fitchburg, MA",
            "overnight_location": "Pearl Hill State Park camping",
            "highlights": ["Nashua River Rail Trail", "Fitchburg Art Museum"],
            "estimated_distance_km": 42,
            "distance_from_start_km": 45,
            "days_remaining_to_return": 4
        },
        "day_3": {
            "start_location": "Fitchburg, MA",
            "end_location": "Gardner, MA", 
            "overnight_location": "Dunn State Park camping",
            "highlights": ["Mount Watatic", "Gardner Heritage State Park"],
            "estimated_distance_km": 40,
            "distance_from_start_km": 55,
            "days_remaining_to_return": 3
        },
        "day_4": {
            "start_location": "Gardner, MA",
            "end_location": "Athol, MA",
            "overnight_location": "Miller's River camping area", 
            "highlights": ["Quabbin Reservoir views", "Miller's River"],
            "estimated_distance_km": 38,
            "distance_from_start_km": 65,
            "days_remaining_to_return": 2
        },
        "day_5": {
            "start_location": "Athol, MA",
            "end_location": "Barre, MA",
            "overnight_location": "Barre Falls Dam recreation area",
            "highlights": ["Barre Falls Dam", "Quabbin Reservoir"],
            "estimated_distance_km": 44,
            "distance_from_start_km": 50,
            "days_remaining_to_return": 1
        },
        "day_6": {
            "start_location": "Barre, MA", 
            "end_location": "Cambridge, MA",
            "overnight_location": "Back home",
            "highlights": ["Return through rural Central MA", "return home"],
            "estimated_distance_km": 48,
            "distance_from_start_km": 0,
            "days_remaining_to_return": 0
        }
    },
    "total_estimated_distance": 257,
    "route_summary": "Closed-loop tour starting and ending at Cambridge, MA, max radius 87km",
    "validation_note": "Each overnight location verified to be returnable within remaining days at 40-50 km/day"
}"""

    print("Testing improved closed-loop prompt...")

    # Mock the OpenAI client
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = mock_response

    with patch.object(bikepacking_planner, 'openai_client', mock_openai_client):
        try:
            result = plan_tour_itinerary(start_location, end_location, nights, preferences)

            print("✅ Plan generated successfully")
            print(f"Result length: {len(result)} characters")

            # Check the prompt that was used
            call_args = mock_openai_client.chat.completions.create.call_args
            prompt = call_args[1]['messages'][0]['content']

            # Verify the prompt includes the new improvements
            assert "Maximum radius calculation" in prompt
            assert "VALIDATION CHECKLIST" in prompt
            assert "days_remaining_to_return" in prompt
            assert "Can you get back to Cambridge, MA" in prompt

            print("✅ Improved prompt elements found")

            # Check that radius calculation was included
            assert "87km radius" in prompt or "max radius" in prompt
            print("✅ Radius calculation included")

            # Verify validation instructions are present
            assert "distance_from_start_km * 1.4" in prompt
            print("✅ Return validation formula included")

            print("\n🎉 All improved closed-loop prompt tests passed!")
            print("\nKey improvements implemented:")
            print("- Maximum radius calculation based on daily distance and trip length")
            print("- Day-by-day validation checklist for return feasibility")
            print("- Explicit constraint that every overnight must be returnable")
            print("- Focus on circular/polygonal route planning vs out-and-back")
            print("- Mathematical validation formula to prevent overextension")

            return True

        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("🧪 Testing Improved Closed-Loop Tour Planning\n")

    # Set dummy environment variables for testing
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['GOOGLE_MAPS_API_KEY'] = 'test-key'

    success = test_closed_loop_prompt()

    if success:
        print("\n✅ Test completed successfully!")
        print("\nThe improved closed-loop planning should now:")
        print("1. Calculate a realistic maximum radius based on daily distance limits")
        print("2. Validate each overnight location for return feasibility")
        print("3. Prevent planning routes that require massive final-day rides")
        print("4. Encourage true loop geometry rather than out-and-back patterns")

        print("\nFor your 5-night, 40-50km/day trip, the max radius is approximately 87km")
        print("This should prevent the AI from planning destinations in Vermont/NH that")
        print("would require a 200+ km final day to return home!")
    else:
        print("\n❌ Test failed - check the error messages above")
        sys.exit(1)
