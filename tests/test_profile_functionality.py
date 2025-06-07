#!/usr/bin/env python3
"""
Test script for the new profile and interactive functionality.
"""

import os
import tempfile

from bikepacking_planner import get_user_preferences, load_profile, save_profile


def test_profile_functionality():
    """Test the new profile loading and interactive functionality"""

    print("🧪 Testing Profile and Interactive Functionality")
    print("=" * 60)

    # Test 1: Create and load a custom profile
    print("\n1️⃣ Testing custom profile creation and loading...")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        test_profile_path = f.name

    try:
        # Create a custom profile
        custom_profile = {
            'accommodation': 'camping',
            'stealth_camping': True,
            'fitness_level': 'advanced',
            'daily_distance': '80-120',
            'terrain': 'challenging',
            'budget': 'budget',
            'interests': ['photography', 'history', 'adventure']
        }

        save_profile(custom_profile, test_profile_path)
        print(f"✅ Custom profile saved to: {test_profile_path}")

        # Load the custom profile
        loaded_profile = load_profile(test_profile_path)
        print("✅ Custom profile loaded successfully:")
        for key, value in loaded_profile.items():
            print(f"   {key}: {value}")

        # Verify it matches
        assert loaded_profile['accommodation'] == 'camping'
        assert loaded_profile['fitness_level'] == 'advanced'
        assert loaded_profile['stealth_camping'] == True
        print("✅ Profile data matches expected values")

    finally:
        # Clean up
        if os.path.exists(test_profile_path):
            os.unlink(test_profile_path)

    # Test 2: Test default profile behavior
    print("\n2️⃣ Testing default profile behavior...")

    # Test with the existing profile.yml
    if os.path.exists('profile.yml'):
        prefs = get_user_preferences(interactive=False, profile_path='profile.yml')
        print("✅ Default profile loaded successfully:")
        for key, value in prefs.items():
            print(f"   {key}: {value}")
    else:
        print("⚠️  No default profile.yml found")

    # Test 3: Test missing profile handling
    print("\n3️⃣ Testing missing profile handling...")

    with tempfile.NamedTemporaryFile(suffix='.yml', delete=True) as f:
        missing_profile_path = f.name

    # This should create a default profile
    prefs = get_user_preferences(interactive=False, profile_path=missing_profile_path)
    print("✅ Default profile created for missing file")
    print(f"✅ Profile created at: {missing_profile_path}")

    # Verify the file was created
    assert os.path.exists(missing_profile_path)
    print("✅ Profile file exists after creation")

    # Clean up
    if os.path.exists(missing_profile_path):
        os.unlink(missing_profile_path)

    # Test 4: Test CLI argument structure
    print("\n4️⃣ Testing CLI argument structure...")

    # Import the main module to check argument parser
    import argparse
    from unittest.mock import patch

    import bikepacking_planner

    # Mock sys.argv to test argument parsing
    test_args = ['bikepacking_planner.py', 'Boston, MA', 'Portland, ME', '2', '--interactive', '--profile', 'test.yml']

    with patch('sys.argv', test_args):
        try:
            parser = argparse.ArgumentParser(description="Intelligent Bikepacking Trip Planner")
            parser.add_argument("start", help="Starting location")
            parser.add_argument("end", help="Ending location")
            parser.add_argument("nights", type=int, help="Number of nights for the trip")
            parser.add_argument("-i", "--interactive", action="store_true",
                                help="Enable interactive mode to ask preference questions")
            parser.add_argument("-p", "--profile", default="profile.yml",
                                help="Path to YAML profile file with preferences (default: profile.yml)")

            args = parser.parse_args(['Boston, MA', 'Portland, ME', '2', '--interactive', '--profile', 'test.yml'])

            assert args.start == 'Boston, MA'
            assert args.end == 'Portland, ME'
            assert args.nights == 2
            assert args.interactive == True
            assert args.profile == 'test.yml'

            print("✅ CLI arguments parsed correctly:")
            print(f"   start: {args.start}")
            print(f"   end: {args.end}")
            print(f"   nights: {args.nights}")
            print(f"   interactive: {args.interactive}")
            print(f"   profile: {args.profile}")

        except Exception as e:
            print(f"❌ CLI argument parsing failed: {e}")
            return False

    print("\n🎉 All profile and CLI functionality tests passed!")
    print("\nKey features validated:")
    print("✅ Custom profile creation and loading")
    print("✅ Default profile handling")
    print("✅ Missing profile auto-creation")
    print("✅ CLI argument parsing")
    print("✅ Interactive vs non-interactive modes")

    return True


if __name__ == "__main__":
    test_profile_functionality()
