#!/usr/bin/env python3
"""
Demo script for the Bikepacking Trip Planner
Shows example usage and validates the setup
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed."""
    print("🔍 Checking dependencies...")

    try:
        import openai
        print("✅ OpenAI library found")
    except ImportError:
        print("❌ OpenAI library not found. Run: pip install openai")
        return False

    try:
        import googlemaps
        print("✅ Google Maps library found")
    except ImportError:
        print("❌ Google Maps library not found. Run: pip install googlemaps")
        return False

    return True


def check_api_keys():
    """Check if API keys are configured."""
    print("\n🔑 Checking API keys...")

    openai_key = os.getenv("OPENAI_API_KEY")
    gmaps_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    else:
        print(f"✅ OpenAI API key found (ends with: ...{openai_key[-4:]})")

    if not gmaps_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in environment variables")
        print("   Set it with: export GOOGLE_MAPS_API_KEY='your-key-here'")
        return False
    else:
        print(f"✅ Google Maps API key found (ends with: ...{gmaps_key[-4:]})")

    return True


def show_examples():
    """Show example usage commands."""
    print("\n🎯 Example usage:")
    print("="*50)

    examples = [
        {
            "title": "Weekend Wine Country Trip",
            "command": "python src/dirtgenie/planner.py --start 'Sonoma, CA' --end 'Napa, CA' --nights 2",
            "description": "Short scenic trip through California wine country"
        },
        {
            "title": "Pacific Coast Adventure",
            "command": "python src/dirtgenie/planner.py --start 'San Francisco, CA' --end 'Los Angeles, CA' --nights 7",
            "description": "Classic week-long Pacific Coast ride"
        },
        {
            "title": "Desert Southwest Journey",
            "command": "python src/dirtgenie/planner.py --start 'Flagstaff, AZ' --end 'Moab, UT' --nights 5",
            "description": "Stunning desert landscapes and red rock country"
        },
        {
            "title": "New England Fall Colors",
            "command": "python src/dirtgenie/planner.py --start 'Boston, MA' --end 'Burlington, VT' --nights 4",
            "description": "Beautiful autumn foliage tour"
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   {example['description']}")
        print(f"   Command: {example['command']}")

    print(f"\n💡 Tips:")
    print(f"   • Be specific with locations (include city, state)")
    print(f"   • The script will ask follow-up questions to customize your trip")
    print(f"   • Generated files will be saved in the current directory")
    print(f"   • Review routes carefully - always verify conditions before traveling")


def main():
    """Run the demo and setup validation."""
    print("🚴‍♀️ Bikepacking Trip Planner - Demo & Setup Check")
    print("="*60)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup incomplete. Please install missing dependencies.")
        return False

    # Check API keys
    if not check_api_keys():
        print("\n❌ Setup incomplete. Please configure your API keys.")
        print("\n🛠️  Quick setup options:")
        print("   1. Run the setup script: ./setup.sh")
        print("   2. Or manually set environment variables:")
        print("      export OPENAI_API_KEY='your-openai-key'")
        print("      export GOOGLE_MAPS_API_KEY='your-google-maps-key'")
        return False

    print("\n✅ All dependencies and API keys are configured!")

    # Show examples
    show_examples()

    print(f"\n🚀 Ready to plan your adventure!")
    print(f"   Try running one of the examples above, or create your own route.")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
