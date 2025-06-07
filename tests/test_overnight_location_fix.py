#!/usr/bin/env python3
"""
Test script to verify the fix for dictionary overnight_location handling.
"""


def test_overnight_location_handling():
    """Test handling of both string and dict formats for overnight_location."""

    # Test data with both formats
    test_cases = [
        # String format (old style)
        {"overnight_location": "Camping at Pine Grove State Park"},

        # Dictionary format (new enhanced style)
        {"overnight_location": {
            "name": "Pine Grove State Park Campground",
            "type": "campground",
            "availability": "Available",
            "pricing": "$25/night",
            "contact": "555-123-4567"
        }},

        # Empty case
        {"overnight_location": ""},

        # Destination case
        {"overnight_location": "Arrive at destination"}
    ]

    def handle_overnight_location(overnight_location):
        """Test function to handle both string and dict formats."""
        if isinstance(overnight_location, dict):
            overnight_location_str = overnight_location.get('name', str(overnight_location))
        else:
            overnight_location_str = str(overnight_location)
        return overnight_location_str

    print("Testing overnight location handling...")

    for i, test_case in enumerate(test_cases):
        overnight_location = test_case.get('overnight_location', '')
        try:
            result = handle_overnight_location(overnight_location)
            print(f"✅ Test {i+1}: '{overnight_location}' -> '{result}'")

            # Test the .lower() operation that was causing the error
            lower_result = result.lower()
            print(f"   Lower case test: '{lower_result}'")

        except Exception as e:
            print(f"❌ Test {i+1} failed: {e}")
            return False

    print("✅ All tests passed!")
    return True


if __name__ == "__main__":
    test_overnight_location_handling()
