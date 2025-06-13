#!/usr/bin/env python3
"""
DirtGenie - AI-Powered Trip Planner

An intelligent trip planner that uses OpenAI's API to create detailed bikepacking itineraries
with route information from Google Maps.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import googlemaps
import polyline  # For decoding Google Maps polylines
import yaml  # For loading profile configurations
from openai import OpenAI


# Load environment variables from .env file if it exists
def load_env():
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


# Load environment variables
load_env()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize clients only if API keys are available
openai_client = None
gmaps: googlemaps.Client | None = None


def initialize_clients():
    """Initialize API clients and check for required API keys."""
    global openai_client, gmaps

    if not OPENAI_API_KEY:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("Please set GOOGLE_MAPS_API_KEY environment variable")

    # Initialize clients
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


def get_bicycle_directions(start: str, end: str, waypoints: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get bicycle directions from Google Maps API.

    Args:
        start: Starting location
        end: Ending location
        waypoints: Optional list of waypoint locations

    Returns:
        Dictionary containing route information
    """
    if not gmaps:
        raise ValueError("Google Maps client not initialized. Please set GOOGLE_MAPS_API_KEY.")

    try:
        # Handle None waypoints for the API call
        waypoints_param = waypoints if waypoints else None

        directions_result = gmaps.directions(  # type: ignore
            origin=start,
            destination=end,
            mode="bicycling",
            waypoints=waypoints_param,
            optimize_waypoints=True,
            units="metric"
        )

        if not directions_result:
            raise ValueError("No route found between the specified locations")

        return directions_result[0]  # Return the first (best) route
    except Exception as e:
        print(f"Error getting directions: {e}")
        return {}


def extract_route_points(directions: Dict[str, Any]) -> List[Tuple[float, float]]:
    """
    Extract coordinate points from Google Maps directions for GeoJSON.

    Args:
        directions: Google Maps directions result

    Returns:
        List of (longitude, latitude) tuples
    """
    points = []

    if not directions or 'legs' not in directions:
        return points

    for leg in directions['legs']:
        for step in leg['steps']:
            # Add start point
            start_lat = step['start_location']['lat']
            start_lng = step['start_location']['lng']
            points.append((start_lng, start_lat))

            # Try to add polyline points if available
            try:
                if 'polyline' in step and 'points' in step['polyline']:
                    polyline_points = polyline.decode(step['polyline']['points'])
                    for point in polyline_points:
                        points.append((point[1], point[0]))  # polyline returns [lat, lng], we want [lng, lat]
            except Exception as e:
                print(f"Warning: Could not decode polyline for step: {e}")
                # Continue without detailed polyline points

    # Add final destination
    if directions['legs']:
        last_leg = directions['legs'][-1]
        end_lat = last_leg['end_location']['lat']
        end_lng = last_leg['end_location']['lng']
        points.append((end_lng, end_lat))

    return points


def create_default_profile() -> Dict[str, Any]:
    """
    Create a default profile configuration.

    Returns:
        Dictionary with default preferences
    """
    return {
        'accommodation': 'mixed',
        'stealth_camping': False,
        'fitness_level': 'intermediate',
        'daily_distance': '50-80',
        'terrain': 'mixed',
        'tire_size': '700x35c (Gravel - Standard)',
        'budget': 'moderate',
        'interests': ['nature', 'adventure']
    }


def load_profile(profile_path: str) -> Dict[str, Any]:
    """
    Load user preferences from a YAML profile file.

    Args:
        profile_path: Path to the YAML profile file

    Returns:
        Dictionary of user preferences

    Raises:
        FileNotFoundError: If profile file doesn't exist
        yaml.YAMLError: If profile file is invalid YAML
        ValueError: If profile file is missing required fields
    """
    profile_file = Path(profile_path)

    if not profile_file.exists():
        print(f"❌ Profile file not found: {profile_path}")
        print(f"💡 Creating default profile at: {profile_path}")

        # Create default profile
        default_profile = create_default_profile()
        save_profile(default_profile, profile_path)

        print(f"✅ Default profile created. You can edit {profile_path} to customize your preferences.")
        return default_profile

    try:
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile_data = yaml.safe_load(f)

        if not isinstance(profile_data, dict):
            raise ValueError("Profile file must contain a YAML dictionary")

        # Validate required fields
        required_fields = ['accommodation', 'fitness_level', 'daily_distance', 'terrain', 'budget']
        missing_fields = [field for field in required_fields if field not in profile_data]

        if missing_fields:
            raise ValueError(f"Profile file missing required fields: {', '.join(missing_fields)}")

        # Set defaults for optional fields
        if 'stealth_camping' not in profile_data:
            profile_data['stealth_camping'] = False
        if 'interests' not in profile_data:
            profile_data['interests'] = []

        print(f"✅ Loaded profile from: {profile_path}")
        return profile_data

    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in profile file {profile_path}: {e}")
    except Exception as e:
        raise ValueError(f"Error loading profile file {profile_path}: {e}")


def save_profile(profile_data: Dict[str, Any], profile_path: str) -> None:
    """
    Save user preferences to a YAML profile file.

    Args:
        profile_data: Dictionary of user preferences
        profile_path: Path where to save the profile file
    """
    profile_file = Path(profile_path)
    profile_file.parent.mkdir(parents=True, exist_ok=True)

    # Create a well-documented YAML file
    yaml_content = f"""# DirtGenie Profile
# Edit this file to customize your default trip preferences

# Accommodation preference: camping, hotels, or mixed
accommodation: {profile_data['accommodation']}

# Allow stealth/wild camping: true or false
stealth_camping: {profile_data['stealth_camping']}

# Fitness level: beginner, intermediate, or advanced
fitness_level: {profile_data['fitness_level']}

# Daily distance preference in km (e.g., "30-50", "50-80", "80-120")
daily_distance: {profile_data['daily_distance']}

# Terrain preference: paved, gravel, mixed, or challenging
terrain: {profile_data['terrain']}

# Tire size (e.g., "700x35c", "650b x 2.25in", "29\" x 2.1in")
tire_size: {profile_data.get('tire_size', '700x35c (Gravel - Standard)')}

# Budget range: budget, moderate, or luxury
budget: {profile_data['budget']}

# Special interests (list of keywords)
interests:
{yaml.dump(profile_data['interests'], default_flow_style=False, indent=2).strip()}
"""

    with open(profile_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)


def get_user_preferences(interactive: bool = False, profile_path: str = "profile.yml") -> Dict[str, Any]:
    """
    Get user preferences either interactively or from a profile file.

    Args:
        interactive: If True, ask questions interactively
        profile_path: Path to YAML profile file (used when not interactive)

    Returns:
        Dictionary of user preferences
    """
    if interactive:
        return ask_follow_up_questions()
    else:
        print(f"\n📋 Loading preferences from profile: {profile_path}")
        return load_profile(profile_path)


def ask_follow_up_questions() -> Dict[str, str]:
    """
    Ask the user follow-up questions to tailor the trip.

    Returns:
        Dictionary of user preferences
    """
    print("\n🏕️  Let's customize your adventure!")
    print("I'll ask you a few questions to tailor the perfect trip for you.\n")

    preferences = {}

    # Accommodation preference
    while True:
        accommodation = input("💤 Accommodation preference (camping/hotels/mixed): ").strip().lower()
        if accommodation in ['camping', 'hotels', 'mixed']:
            preferences['accommodation'] = accommodation
            break
        print("Please choose: camping, hotels, or mixed")

    # Stealth camping
    if preferences['accommodation'] in ['camping', 'mixed']:
        while True:
            stealth = input("🏕️  Is stealth camping appropriate/desired? (yes/no): ").strip().lower()
            if stealth in ['yes', 'no', 'y', 'n']:
                preferences['stealth_camping'] = stealth in ['yes', 'y']
                break
            print("Please answer yes or no")

    # Fitness level
    while True:
        fitness = input("💪 Fitness level (beginner/intermediate/advanced): ").strip().lower()
        if fitness in ['beginner', 'intermediate', 'advanced']:
            preferences['fitness_level'] = fitness
            break
        print("Please choose: beginner, intermediate, or advanced")

    # Daily distance preference
    distance_ranges = {
        'beginner': '30-50',
        'intermediate': '50-80',
        'advanced': '80-120'
    }
    default_range = distance_ranges[preferences['fitness_level']]
    daily_distance = input(f"🚴 Preferred daily distance in km (default: {default_range}): ").strip()
    preferences['daily_distance'] = daily_distance if daily_distance else default_range

    # Terrain preference
    while True:
        terrain = input("🏔️  Terrain preference (paved/gravel/mixed/challenging): ").strip().lower()
        if terrain in ['paved', 'gravel', 'mixed', 'challenging']:
            preferences['terrain'] = terrain
            break
        print("Please choose: paved, gravel, mixed, or challenging")

    # Tire size
    print("\n🚴 What tire size are you riding?")
    print("1. Road bike (700x23-28c)")
    print("2. Gravel bike (700x32-40c)")
    print("3. Mountain bike (26\", 27.5\", or 29\")")
    print("4. Other/Custom")

    while True:
        tire_choice = input("Choose option (1-4): ").strip()
        if tire_choice == '1':
            preferences['tire_size'] = input(
                "Specific size (e.g., 700x25c) or press Enter for 700x25c: ").strip() or "700x25c"
            break
        elif tire_choice == '2':
            preferences['tire_size'] = input(
                "Specific size (e.g., 700x35c) or press Enter for 700x35c: ").strip() or "700x35c"
            break
        elif tire_choice == '3':
            preferences['tire_size'] = input(
                "Specific size (e.g., 29\" x 2.25in) or press Enter for 29\" x 2.1in: ").strip() or "29\" x 2.1in"
            break
        elif tire_choice == '4':
            preferences['tire_size'] = input("Enter your tire size (e.g., 650b x 47mm): ").strip() or "700x35c"
            break
        print("Please choose 1, 2, 3, or 4")

    # Budget
    while True:
        budget = input("💰 Daily budget range (budget/moderate/luxury): ").strip().lower()
        if budget in ['budget', 'moderate', 'luxury']:
            preferences['budget'] = budget
            break
        print("Please choose: budget, moderate, or luxury")

    # Interests
    interests = input("🎯 Special interests (food/photography/history/nature/adventure - separate with commas): ").strip()
    preferences['interests'] = [interest.strip() for interest in interests.split(',') if interest.strip()]

    return preferences


def plan_tour_itinerary(start: str, end: str, nights: int, preferences: Dict[str, str], desires: List[str], departure_date: Optional[str] = None) -> Dict[str, Any]:
    """
    First step: Plan the tour itinerary with specific waypoints and overnight stops.
    This determines WHERE to go before figuring out HOW to get there.

    Args:
        start: Starting location
        end: Ending location
        nights: Number of nights
        preferences: User preferences from follow-up questions
        departure_date: Optional departure date (format: YYYY-MM-DD)

    Returns:
        Dictionary containing planned itinerary with waypoints and overnight stops
    """
    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")

    # Get daily distance preference
    daily_distance = preferences.get('daily_distance', '60-80')
    if 'km' in daily_distance:
        daily_distance = daily_distance.replace('km', '').strip()

    # Detect if this is a closed-loop tour (start and end are the same or very similar)
    is_closed_loop = (start.lower().strip() == end.lower().strip() or
                      # Also check if they're essentially the same location with slight variations
                      (start.replace(',', '').replace(' ', '').lower() in end.replace(',', '').replace(' ', '').lower() or
                       end.replace(',', '').replace(' ', '').lower() in start.replace(',', '').replace(' ', '').lower()))

    # Estimate rough distance for planning
    try:
        if is_closed_loop:
            # For closed loops, we can't use direct distance, so estimate based on daily distance and nights
            # Parse daily distance range to get average
            if '-' in daily_distance:
                min_dist, max_dist = map(int, daily_distance.split('-'))
                avg_daily_distance = (min_dist + max_dist) / 2
            else:
                avg_daily_distance = int(daily_distance.split()[0]) if daily_distance else 60

            total_distance = avg_daily_distance * (nights + 1)
        else:
            # Get a quick direct route estimate for planning purposes only
            rough_directions = get_bicycle_directions(start, end)
            total_distance = sum(leg['distance']['value'] for leg in rough_directions['legs']) / 1000
    except:
        # Fallback if route query fails
        total_distance = 100  # Default assumption

    # Incorporate desires into the planning process
    if desires:
        print(f"User desires: {', '.join(desires)}")
    # Create different prompts for closed-loop vs point-to-point tours
    if is_closed_loop:
        # Calculate maximum practical radius for closed-loop planning
        # Conservative estimate: assume you need to be able to get back within remaining days
        if '-' in daily_distance:
            min_daily, max_daily = map(int, daily_distance.split('-'))
            avg_daily = (min_daily + max_daily) / 2
        else:
            avg_daily = int(daily_distance.split()[0]) if daily_distance else 50

        # Maximum radius is roughly: (total_days * avg_daily) / (2 * pi) for a circular tour
        # But we'll be more conservative and use about 30-40% of total distance as max radius
        max_radius_km = int(avg_daily * (nights + 1) * 0.35)

        prompt = f"""
You are an expert bikepacking tour planner with access to current web information. Your job is to plan a CLOSED-LOOP TOUR itinerary - a route that starts and ends at the same location.

IMPORTANT: Use web search to find current, up-to-date information about:
- Campgrounds and accommodations (availability, booking info, current status)
- Bike trails and cycling routes (conditions, closures, recent reviews)
- Local bike shops and services along the route
- Current weather patterns and seasonal considerations
- Local events or festivals that might affect the trip
- Recent cyclist reviews and recommendations for the area

TRIP PARAMETERS:
- Start/End: {start}
- Duration: {nights} nights ({nights + 1} days)
- Daily distance preference: {daily_distance} km per day
- Estimated total loop distance: {total_distance:.0f} km
- Departure date: {departure_date if departure_date else "Not specified"}

USER PREFERENCES:
- Accommodation: {preferences.get('accommodation', 'mixed')}
- Stealth camping allowed: {preferences.get('stealth_camping', False)}
- Fitness level: {preferences.get('fitness_level', 'intermediate')}
- Terrain preference: {preferences.get('terrain', 'mixed')}
- Tire size: {preferences.get('tire_size', '700x35c (Gravel - Standard)')}
- Budget: {preferences.get('budget', 'moderate')}
- Interests: {', '.join(preferences.get('interests', []))}

TASK: Plan a {nights + 1}-day CLOSED-LOOP itinerary that starts and ends at the same location.

CRITICAL REQUIREMENTS FOR CLOSED-LOOP TOURS:
1. **Every single day MUST be within {daily_distance} km** - including the final return day
2. **Plan a true loop, not out-and-back** - avoid going straight out and straight back
3. **Maximum radius calculation** - with {nights + 1} days and {daily_distance} km/day, you can only go about {max_radius_km}km from start as the crow flies
4. **Think circular/polygonal** - plan destinations that form a roughly circular or polygonal pattern around the start point
5. **Balance the loop** - ensure you're never more than {max_radius_km}km from home at any point

ROUTE SURFACE AND TIRE COMPATIBILITY:
Based on tire size "{preferences.get('tire_size', '700x35c (Gravel - Standard)')}" and terrain preference "{preferences.get('terrain', 'mixed')}":
- If tire size contains "23", "25", or "28mm": Prioritize paved roads, light gravel paths, and well-maintained bike paths
- If tire size contains "32", "35", "40mm" or "650b": Good for mixed terrain - paved roads, gravel paths, and light trails
- If tire size contains "2.1", "2.25", "2.35", or "2.8": Can handle mountain bike trails, singletrack, and rougher terrain
- Always match route surface recommendations to tire capabilities for safety and comfort

LOOP PLANNING STRATEGY:
For a {nights + 1}-day loop with {daily_distance} km daily distance:
- **Maximum distance from start**: About {max_radius_km}km radius (straight-line distance)
- **Loop geometry**: Plan waypoints that form a circle/polygon, not a line
- **Progressive planning**: Each day should move you around the loop, not just away from start
- **Return consideration**: Every waypoint should be positioned such that you can get home within the remaining days at {daily_distance} km/day

BEFORE PLANNING: Calculate if each overnight location can get you back to {start} within the remaining days.
Example: If it's day 3 of 6, and you're in location X, can you get from X to {start} in 3 days at {daily_distance} km/day?

VALIDATION CHECKLIST FOR EACH DAY:
- Day 1 destination: Can you get back to {start} in {nights} days at {daily_distance} km/day?
- Day 2 destination: Can you get back to {start} in {nights-1} days at {daily_distance} km/day?
- Day 3 destination: Can you get back to {start} in {nights-2} days at {daily_distance} km/day?
- Continue this pattern...
- Final day: MUST be exactly within {daily_distance} km of {start}

Think of this as planning waypoints on a circle or polygon around {start}, not a straight line out and back.

Return the plan in this exact JSON format:

{{
    "itinerary": {{
        "day_1": {{
            "start_location": "{start}",
            "end_location": "Town/City within {daily_distance.split('-')[0] if '-' in daily_distance else daily_distance[:2]}km of start",
            "overnight_location": "Specific accommodation name or camping area",
            "highlights": ["attraction 1", "attraction 2"],
            "estimated_distance_km": {daily_distance.split('-')[0] if '-' in daily_distance else daily_distance[:2]},
            "distance_from_start_km": "Straight-line distance from {start}",
            "days_remaining_to_return": {nights}
        }},
        "day_2": {{
            "start_location": "Previous end location",
            "end_location": "Next waypoint continuing around the loop (not further from start)",
            "overnight_location": "Specific accommodation name or camping area", 
            "highlights": ["attraction 1", "attraction 2"],
            "estimated_distance_km": {daily_distance.split('-')[1] if '-' in daily_distance else daily_distance[:2]},
            "distance_from_start_km": "Straight-line distance from {start}",
            "days_remaining_to_return": {nights-1}
        }},
        ...continue for all {nights + 1} days...
        "day_{nights + 1}": {{
            "start_location": "Previous end location",
            "end_location": "{start}",
            "overnight_location": "Back home",
            "highlights": ["final attractions", "return home"],
            "estimated_distance_km": {daily_distance.split('-')[0] if '-' in daily_distance else daily_distance[:2]},
            "distance_from_start_km": 0,
            "days_remaining_to_return": 0
        }}
    }},
    "total_estimated_distance": {total_distance:.0f},
    "route_summary": "Closed-loop tour starting and ending at {start}, max radius {max_radius_km}km",
    "validation_note": "Each overnight location verified to be returnable within remaining days at {daily_distance} km/day"
}}

IMPORTANT: Every overnight location MUST be positioned such that:
(distance_from_start_km * 1.4) <= (days_remaining_to_return * max_daily_distance)
This ensures you can always get back within your daily distance constraints.

SEARCH REQUIREMENTS:
- Search for current weather forecasts for all planned locations and travel dates{f" (starting {departure_date})" if departure_date else ""}
- Find specific, bookable accommodations with current availability and pricing
- Verify trail conditions and any seasonal closures or restrictions
- Look up local services and attractions with current operating information
- Check for seasonal events, festivals, or special conditions during the planned travel period
"""
    else:
        prompt = f"""
You are an expert bikepacking tour planner. Your job is to plan the ITINERARY first - determining the best places to visit and stay overnight.

TRIP PARAMETERS:
- Start: {start}
- End: {end}
- Duration: {nights} nights ({nights + 1} days)
- Rough total distance: {total_distance:.0f} km
- Daily distance preference: {daily_distance} km per day
- Departure date: {departure_date if departure_date else "Not specified"}

USER PREFERENCES:
- Accommodation: {preferences.get('accommodation', 'mixed')}
- Stealth camping allowed: {preferences.get('stealth_camping', False)}
- Fitness level: {preferences.get('fitness_level', 'intermediate')}
- Terrain preference: {preferences.get('terrain', 'mixed')}
- Tire size: {preferences.get('tire_size', '700x35c (Gravel - Standard)')}
- Budget: {preferences.get('budget', 'moderate')}
- Interests: {', '.join(preferences.get('interests', []))}

TASK: Plan a {nights + 1}-day itinerary with specific waypoints and overnight locations.

SEARCH REQUIREMENTS:
- Search for current weather forecasts for all planned locations and travel dates{f" (starting {departure_date})" if departure_date else ""}
- Find specific, bookable accommodations with current availability and pricing
- Verify trail conditions and any seasonal closures or restrictions
- Look up local services and attractions with current operating information
- Check for seasonal events, festivals, or special conditions during the planned travel period

PLANNING REQUIREMENTS:
1. Identify the best intermediate destinations that make sense for a bikepacking tour
2. Consider scenic routes, points of interest, accommodation availability
3. Plan realistic daily segments based on terrain and fitness level - stay within {daily_distance} km per day
4. Choose specific towns/cities/landmarks as overnight stops
5. Ensure progression toward the final destination

ROUTE SURFACE AND TIRE COMPATIBILITY:
Based on tire size "{preferences.get('tire_size', '700x35c (Gravel - Standard)')}" and terrain preference "{preferences.get('terrain', 'mixed')}":
- If tire size contains "23", "25", or "28mm": Prioritize paved roads, light gravel paths, and well-maintained bike paths
- If tire size contains "32", "35", "40mm" or "650b": Good for mixed terrain - paved roads, gravel paths, and light trails  
- If tire size contains "2.1", "2.25", "2.35", or "2.8": Can handle mountain bike trails, singletrack, and rougher terrain
- Always match route surface recommendations to tire capabilities for safety and comfort

Return the plan in this exact JSON format with EXTENSIVE DETAIL:

{{
    "itinerary": {{
        "day_1": {{
            "start_location": "{start}",
            "end_location": "Specific Town/City Name",
            "waypoints": [
                "Waypoint 1 name (15km) - Description and services",
                "Waypoint 2 name (35km) - Description and services", 
                "Waypoint 3 name (55km) - Description and services"
            ],
            "overnight_location": "Specific accommodation name with contact info",
            "highlights": ["attraction 1 with details", "attraction 2 with details", "attraction 3 with details"],
            "estimated_distance_km": 75,
            "elevation_gain_m": 850,
            "difficulty": "moderate",
            "surface_types": "40km paved road, 25km gravel path, 10km dirt trail",
            "food_stops": ["Restaurant Name at km 20", "Grocery Store at km 45"],
            "water_sources": ["Public fountain at km 10", "Stream at km 30", "Town well at km 60"]
        }},
        "day_2": {{
            "start_location": "Previous end location",
            "end_location": "Next Town/City Name",
            "waypoints": [
                "Day 2 waypoint 1 (20km) - Description and services",
                "Day 2 waypoint 2 (45km) - Description and services"
            ],
            "overnight_location": "Specific accommodation name with contact info",
            "highlights": ["day 2 attraction 1 with details", "day 2 attraction 2 with details"],
            "estimated_distance_km": 80,
            "elevation_gain_m": 650,
            "difficulty": "easy",
            "surface_types": "50km paved road, 30km gravel path",
            "food_stops": ["Food options for day 2"],
            "water_sources": ["Water sources for day 2"]
        }},
        ...continue for all {nights + 1} days with the same level of detail...
        "day_{nights + 1}": {{
            "start_location": "Previous end location",
            "end_location": "{end}",
            "waypoints": ["Final day waypoints with descriptions"],
            "overnight_location": "Arrive at destination",
            "highlights": ["final day attractions with details"],
            "estimated_distance_km": 65,
            "elevation_gain_m": 400,
            "difficulty": "moderate",
            "surface_types": "final day surface breakdown",
            "food_stops": ["final day food options"],
            "water_sources": ["final day water sources"]
        }}
    }},
    "total_estimated_distance": 400,
    "total_elevation_gain": 2000,
    "route_summary": "Comprehensive description of the overall route including terrain, highlights, and challenges",
    "best_months": ["April", "May", "September", "October"],
    "gear_recommendations": ["specific gear for this route"],
    "emergency_contacts": ["relevant emergency contacts for the route area"],
    "permits_required": ["any permits or fees needed"],
    "difficulty_rating": "beginner/intermediate/advanced"
}}

Be specific with location names (include city, state/province). Choose real places that make sense for bikepacking.

IMPORTANT: Use web search to find:
1. Current weather forecasts for each location and planned travel dates
2. Specific accommodations with real names, contact info, current availability and pricing
3. Verify all locations and services are real and currently operating
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                    "content": "You are an expert bikepacking tour planner with access to current web information. CRITICAL: You must respond with ONLY valid JSON exactly as requested - no additional text, no markdown, no explanations outside the JSON. Be extremely detailed within the JSON structure. IMPORTANT: Use your web search capabilities to find current information about: 1) Specific accommodations (campgrounds, hotels, hostels) with availability, pricing, and booking details, 2) Current weather forecasts for the planned travel dates and locations, 3) Trail conditions and any closures, 4) Local attractions and their current operating status. Search for real, specific places and current information. Include MANY waypoints and detailed descriptions for each day."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )

        import json
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")

        itinerary_json = content.strip()

        # More robust JSON extraction
        # Look for JSON content between markers or extract the first complete JSON object
        if itinerary_json.startswith('```json'):
            itinerary_json = itinerary_json[7:]
        if itinerary_json.endswith('```'):
            itinerary_json = itinerary_json[:-3]

        # Find the start and end of the JSON object
        json_start = itinerary_json.find('{')
        if json_start == -1:
            raise ValueError("No JSON object found in response")

        # Find the matching closing brace by counting braces
        brace_count = 0
        json_end = -1
        for i, char in enumerate(itinerary_json[json_start:], json_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

        if json_end == -1:
            # Fallback: try to parse the whole cleaned content
            json_content = itinerary_json.strip()
        else:
            json_content = itinerary_json[json_start:json_end]

        itinerary = json.loads(json_content)
        return itinerary

    except Exception as e:
        print(f"Error planning itinerary: {e}")
        # Fallback to simple 2-stop itinerary
        return {
            "itinerary": {
                "day_1": {
                    "start_location": start,
                    "end_location": f"Midpoint between {start} and {end}",
                    "overnight_location": "Local camping area",
                    "highlights": ["Scenic route", "Local attractions"],
                    "estimated_distance_km": 80
                },
                f"day_{nights + 1}": {
                    "start_location": f"Midpoint between {start} and {end}",
                    "end_location": end,
                    "overnight_location": "Arrive at destination",
                    "highlights": ["Final stretch", "Destination arrival"],
                    "estimated_distance_km": 80
                }
            },
            "total_estimated_distance": 160,
            "route_summary": f"Simple route from {start} to {end}"
        }


def get_multi_waypoint_directions(itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get bicycle directions for the planned itinerary with multiple waypoints.

    Args:
        itinerary: Planned itinerary from plan_tour_itinerary()

    Returns:
        Google Maps directions with all waypoints
    """
    if not gmaps:
        raise ValueError("Google Maps client not initialized. Please set GOOGLE_MAPS_API_KEY.")

    # Extract waypoints from itinerary
    daily_plans = itinerary['itinerary']
    waypoints = []

    # Get all intermediate stops (exclude final destination)
    for day_key in sorted(daily_plans.keys()):
        day_plan = daily_plans[day_key]
        end_location = day_plan['end_location']

        # Don't add the final destination as a waypoint (it will be the destination)
        if day_key != max(daily_plans.keys()):
            waypoints.append(end_location)

    # First location is start, last location is end
    first_day = daily_plans[min(daily_plans.keys())]
    last_day = daily_plans[max(daily_plans.keys())]

    start_location = first_day['start_location']
    end_location = last_day['end_location']

    try:
        return get_bicycle_directions(start_location, end_location, waypoints)
    except Exception as e:
        print(f"Error getting multi-waypoint directions: {e}")
        # Fallback to simple start-to-end route
        return get_bicycle_directions(start_location, end_location)


def generate_trip_plan(start: str, end: str, nights: int, preferences: Dict[str, str],
                       itinerary: Dict[str, Any], directions: Dict[str, Any], departure_date: Optional[str] = None,
                       desires: Optional[List[str]] = None) -> str:
    """
    Generate a detailed trip plan using the planned itinerary and route data.

    Args:
        start: Starting location
        end: Ending location
        nights: Number of nights
        preferences: User preferences from follow-up questions
        itinerary: Planned itinerary with waypoints
        directions: Google Maps directions data for the planned route
        departure_date: Optional departure date (format: YYYY-MM-DD)

    Returns:
        Detailed trip plan as markdown string
    """

    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")

    # Extract route information
    total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000  # Convert to km
    total_duration = sum(leg['duration']['value'] for leg in directions['legs']) / 3600  # Convert to hours

    # Format route and itinerary information
    route_info = format_route_info(directions)
    itinerary_text = format_itinerary_for_prompt(itinerary)

    # Create detailed prompt for OpenAI
    departure_info = f"\n- Departure date: {departure_date}" if departure_date else ""

    desires_text = ', '.join(desires) if desires else 'No specific desires provided.'

    prompt = f"""
    USER DESIRES:
    - {desires_text}

You are an expert bikepacking trip planner with access to current web information. Create a detailed {nights}-night bikepacking itinerary based on the planned route.

EXAMPLE OF EXCELLENT OUTPUT FORMAT:
Here is an example of the exact format and level of detail you should provide:

# 🚴‍♂️ TRIP OVERVIEW & DAILY SUMMARY

## 📊 Trip Summary Table

| Day | Date | Start Location | End Location | Overnight | Daily Distance | Cumulative | Weather | Highlights |
|-----|------|----------------|--------------|-----------|----------------|------------|---------|------------|
| 1 | Sep 15 | San Francisco | Half Moon Bay | Camping | 45km | 45km | Sunny 22°C | Golden Gate Bridge, Pacific Coast |
| 2 | Sep 16 | Half Moon Bay | Santa Cruz | Hotel | 52km | 97km | Partly Cloudy 20°C | Lighthouse, Beaches |

## 🗺️ ROUTE DETAILS
[Detailed route information follows based on actual directions]

## 📍 DAILY ITINERARY
[Daily breakdown with specific stops, accommodations, and activities]

## 🏕️ ACCOMMODATION DETAILS
[Specific accommodation information and booking details]

## 🍽️ FOOD & WATER STRATEGY
[Resupply points and meal planning]

## 🚴‍♂️ GEAR RECOMMENDATIONS
[Bike setup and packing recommendations]

## 📱 EMERGENCY CONTACTS & SAFETY
[Local emergency contacts and safety information]

TRIP DETAILS:
- Start: {start}
- End: {end}
- Duration: {nights} nights
- Accommodation preference: {preferences.get('accommodation', 'mixed')}
- Fitness level: {preferences.get('fitness_level', 'intermediate')}
- Daily distance: {preferences.get('daily_distance', '50-80')} km
- Terrain: {preferences.get('terrain', 'mixed')}
- Budget: {preferences.get('budget', 'moderate')}
- Interests: {', '.join(preferences.get('interests', []))}
- Allow stealth camping: {preferences.get('stealth_camping', False)}
- Tire size: {preferences.get('tire_size', '700x35c (Gravel - Standard)')}{departure_info}

ROUTE INFORMATION:
{route_info}

ITINERARY STOPS:
{itinerary_text}

Please create a comprehensive trip plan following the example format above. Include practical details like specific accommodation options, food stops, water sources, and safety considerations. Make it engaging and informative."""

    try:
        # Make API call to OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert bikepacking trip planner with extensive knowledge of cycling routes, accommodations, and outdoor safety."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )

        trip_plan = response.choices[0].message.content
        if trip_plan:
            trip_plan = trip_plan.strip()
        else:
            trip_plan = "Error: Empty response from OpenAI"
        print(f"\n✅ Generated trip plan with {len(trip_plan)} characters")
        return trip_plan

    except Exception as e:
        error_msg = f"❌ Error generating trip plan: {e}"
        print(error_msg)
        return f"Error generating trip plan: {e}"


def revise_trip_plan_with_feedback(original_plan: str, feedback: str, start: str, end: str, nights: int,
                                   preferences: Dict[str, Any], itinerary: Dict[str, Any],
                                   directions: Dict[str, Any], departure_date: Optional[str] = None) -> str:
    """
    Revise an existing trip plan based on user feedback.
    """
    if not openai_client:
        return "Error: OpenAI client not initialized"

    # Format the route information
    route_info = format_route_info(directions)
    itinerary_text = format_itinerary_for_prompt(itinerary)

    departure_info = f"\n- Departure date: {departure_date}" if departure_date else ""

    prompt = f"""
You are revising a bikepacking trip plan based on user feedback. Here is the original plan and the user's feedback:

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

TRIP DETAILS:
- Start: {start}
- End: {end}
- Duration: {nights} nights
- Accommodation preference: {preferences.get('accommodation', 'mixed')}
- Fitness level: {preferences.get('fitness_level', 'intermediate')}
- Daily distance: {preferences.get('daily_distance', '50-80')} km
- Terrain: {preferences.get('terrain', 'mixed')}
- Budget: {preferences.get('budget', 'moderate')}
- Interests: {', '.join(preferences.get('interests', []))}
- Allow stealth camping: {preferences.get('stealth_camping', False)}
- Tire size: {preferences.get('tire_size', '700x35c (Gravel - Standard)')}{departure_info}

ROUTE INFORMATION:
{route_info}

ITINERARY STOPS:
{itinerary_text}

Please revise the trip plan based on the user's feedback while maintaining the same format and structure. Address their specific concerns and incorporate their suggestions where possible."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert bikepacking trip planner. Revise the existing plan based on the user's feedback while maintaining high quality and practical advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )

        revised_plan = response.choices[0].message.content
        if revised_plan:
            revised_plan = revised_plan.strip()
        else:
            revised_plan = "Error: Empty response from OpenAI"
        print(f"\n✅ Revised trip plan with {len(revised_plan)} characters")
        return revised_plan

    except Exception as e:
        error_msg = f"❌ Error revising trip plan: {e}"
        print(error_msg)
        return f"Error revising trip plan: {e}"


def main():
    """Main function to run the trip planner."""
    parser = argparse.ArgumentParser(description="DirtGenie - AI-Powered Bikepacking Trip Planner")
    parser.add_argument("start", help="Starting location")
    parser.add_argument("end", help="Ending location")
    parser.add_argument("nights", type=int, help="Number of nights")
    parser.add_argument("--departure-date", help="Departure date (YYYY-MM-DD)")
    parser.add_argument("--profile", help="Profile file to load preferences from")
    parser.add_argument("--output-dir", default="trips", help="Output directory for trip files")

    args = parser.parse_args()

    # Initialize clients
    initialize_clients()

    # Load profile if specified
    preferences = {}
    if args.profile:
        try:
            profile_data = load_profile(args.profile)
            preferences = profile_data
            print(f"✅ Loaded profile from {args.profile}")
        except Exception as e:
            print(f"⚠️  Could not load profile {args.profile}: {e}")
            preferences = create_default_profile()
    else:
        preferences = create_default_profile()

    print(f"\n🗺️  Planning trip from {args.start} to {args.end} for {args.nights} nights...")

    try:
        # Step 1: Plan the itinerary
        print("\n📍 Planning itinerary...")
        itinerary = plan_tour_itinerary(
            start=args.start,
            end=args.end,
            nights=args.nights,
            preferences=preferences,
            desires=[],
            departure_date=args.departure_date
        )

        # Step 2: Get route directions
        print("\n🛣️  Getting route directions...")
        directions = get_multi_waypoint_directions(itinerary)

        if not directions or 'legs' not in directions:
            print("❌ Could not find a route between the specified locations")
            return

        # Step 3: Generate detailed trip plan
        print("\n📝 Generating detailed trip plan...")
        trip_plan = generate_trip_plan(
            start=args.start,
            end=args.end,
            nights=args.nights,
            preferences=preferences,
            itinerary=itinerary,
            directions=directions,
            departure_date=args.departure_date,
            desires=[]
        )

        # Step 4: Create GeoJSON
        print("\n🗺️  Creating route map...")
        geojson_data = create_geojson(
            start=args.start,
            end=args.end,
            directions=directions,
            preferences=preferences,
            trip_plan=trip_plan,
            itinerary=itinerary
        )

        # Step 5: Save output files
        output_dir = Path(args.output_dir)
        trip_name = f"{args.start.lower().replace(' ', '-').replace(',', '')}-to-{args.end.lower().replace(' ', '-').replace(',', '')}"
        trip_dir = output_dir / trip_name

        # Create output directory
        trip_dir.mkdir(parents=True, exist_ok=True)

        # Save trip plan
        plan_file = trip_dir / "report.md"
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(trip_plan)

        # Save GeoJSON
        geojson_file = trip_dir / "route.geojson"
        with open(geojson_file, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2)

        # Save profile used
        profile_file = trip_dir / "profile.yml"
        with open(profile_file, 'w', encoding='utf-8') as f:
            yaml.dump(preferences, f, default_flow_style=False)

        print(f"\n✅ Trip plan completed!")
        print(f"📁 Files saved to: {trip_dir}")
        print(f"📄 Trip plan: {plan_file}")
        print(f"🗺️  Route map: {geojson_file}")
        print(f"⚙️  Profile: {profile_file}")

        # Calculate and display total distance
        total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000
        print(f"🚴‍♂️ Total distance: {total_distance:.1f} km")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()


def format_route_info(directions: Dict[str, Any]) -> str:
    """
    Format route information from Google Maps directions for AI prompt.

    Args:
        directions: Google Maps directions result

    Returns:
        Formatted string with route details
    """
    if not directions or 'legs' not in directions:
        return "Route information not available"

    route_info = []
    total_distance = 0
    total_duration = 0

    for i, leg in enumerate(directions['legs'], 1):
        distance_km = leg['distance']['value'] / 1000
        duration_hours = leg['duration']['value'] / 3600

        total_distance += distance_km
        total_duration += duration_hours

        route_info.append(f"Leg {i}: {leg['start_address']} to {leg['end_address']}")
        route_info.append(f"  Distance: {distance_km:.1f} km")
        route_info.append(f"  Duration: {duration_hours:.1f} hours")
        route_info.append("")

    route_info.append(f"Total Distance: {total_distance:.1f} km")
    route_info.append(f"Total Duration: {total_duration:.1f} hours")

    return "\n".join(route_info)


def format_itinerary_for_prompt(itinerary: Dict[str, Any]) -> str:
    """
    Format itinerary information for AI prompt.

    Args:
        itinerary: Planned itinerary data

    Returns:
        Formatted string with itinerary details
    """
    if 'itinerary' not in itinerary:
        return "Itinerary information not available"

    itinerary_info = []
    daily_plans = itinerary['itinerary']

    for day_key in sorted(daily_plans.keys()):
        day_plan = daily_plans[day_key]
        day_num = day_key.replace('day_', '')

        itinerary_info.append(f"Day {day_num}:")
        itinerary_info.append(f"  Start: {day_plan.get('start_location', 'Unknown')}")
        itinerary_info.append(f"  End: {day_plan.get('end_location', 'Unknown')}")
        itinerary_info.append(f"  Overnight: {day_plan.get('overnight_location', 'Unknown')}")

        if 'highlights' in day_plan:
            itinerary_info.append(f"  Highlights: {', '.join(day_plan['highlights'])}")

        if 'estimated_distance_km' in day_plan:
            itinerary_info.append(f"  Distance: {day_plan['estimated_distance_km']} km")

        itinerary_info.append("")

    return "\n".join(itinerary_info)


def create_geojson(start: str, end: str, directions: Dict[str, Any],
                   preferences: Dict[str, Any], trip_plan: str,
                   itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create GeoJSON data from the trip plan and directions.

    Args:
        start: Starting location
        end: Ending location
        directions: Google Maps directions result
        preferences: User preferences
        trip_plan: Generated trip plan text
        itinerary: Planned itinerary data

    Returns:
        GeoJSON FeatureCollection
    """
    features = []

    # Extract route points from directions
    route_points = extract_route_points(directions)

    if route_points:
        # Create the main route line
        route_feature = {
            "type": "Feature",
            "properties": {
                "name": f"Route from {start} to {end}",
                "description": "Main bikepacking route",
                "stroke": "#0066cc",
                "stroke-width": 4,
                "stroke-opacity": 0.8
            },
            "geometry": {
                "type": "LineString",
                "coordinates": route_points
            }
        }
        features.append(route_feature)

    # Add waypoint markers from itinerary
    if 'itinerary' in itinerary:
        daily_plans = itinerary['itinerary']

        for day_key in sorted(daily_plans.keys()):
            day_plan = daily_plans[day_key]
            day_num = day_key.replace('day_', '')

            # Try to get coordinates for the end location
            end_location = day_plan.get('end_location', '')
            if end_location and gmaps:
                try:
                    geocode_result = gmaps.geocode(end_location)  # type: ignore
                    if geocode_result:
                        location = geocode_result[0]['geometry']['location']

                        waypoint_feature = {
                            "type": "Feature",
                            "properties": {
                                "name": f"Day {day_num}: {end_location}",
                                "description": f"Overnight: {day_plan.get('overnight_location', 'Unknown')}",
                                "marker-color": "#ff6600",
                                "marker-size": "large",
                                "marker-symbol": f"{day_num}"
                            },
                            "geometry": {
                                "type": "Point",
                                "coordinates": [location['lng'], location['lat']]
                            }
                        }
                        features.append(waypoint_feature)
                except Exception as e:
                    print(f"Warning: Could not geocode {end_location}: {e}")

    # Create the GeoJSON FeatureCollection
    geojson_data = {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "name": f"Bikepacking Trip: {start} to {end}",
            "description": "Generated by DirtGenie AI Trip Planner"
        }
    }

    return geojson_data


def plan_tour_itinerary_with_keys(start: str, end: str, nights: int, preferences: Dict[str, str],
                                  desires: List[str], departure_date: Optional[str] = None,
                                  openai_key: Optional[str] = None, google_maps_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Plan tour itinerary with user-provided API keys.
    """
    # Temporarily set up clients with user-provided keys
    original_openai_client = globals().get('openai_client')
    original_gmaps = globals().get('gmaps')

    try:
        if openai_key:
            global openai_client
            openai_client = OpenAI(api_key=openai_key)

        if google_maps_key:
            global gmaps
            gmaps = googlemaps.Client(key=google_maps_key)

        return plan_tour_itinerary(start, end, nights, preferences, desires, departure_date)

    finally:
        # Restore original clients
        globals()['openai_client'] = original_openai_client
        globals()['gmaps'] = original_gmaps


def get_multi_waypoint_directions_with_keys(itinerary: Dict[str, Any], google_maps_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Get multi-waypoint directions with user-provided Google Maps API key.
    """
    original_gmaps = globals().get('gmaps')

    try:
        if google_maps_key:
            global gmaps
            gmaps = googlemaps.Client(key=google_maps_key)

        return get_multi_waypoint_directions(itinerary)

    finally:
        # Restore original client
        globals()['gmaps'] = original_gmaps


def generate_trip_plan_with_keys(start: str, end: str, nights: int, preferences: Dict[str, str],
                                 itinerary: Dict[str, Any], directions: Dict[str, Any],
                                 departure_date: Optional[str] = None, desires: Optional[List[str]] = None,
                                 openai_key: Optional[str] = None) -> str:
    """
    Generate trip plan with user-provided OpenAI API key.
    """
    original_openai_client = globals().get('openai_client')

    try:
        if openai_key:
            global openai_client
            openai_client = OpenAI(api_key=openai_key)

        return generate_trip_plan(start, end, nights, preferences, itinerary, directions, departure_date, desires)

    finally:
        # Restore original client
        globals()['openai_client'] = original_openai_client


def create_geojson_with_keys(start: str, end: str, directions: Dict[str, Any],
                             preferences: Dict[str, Any], trip_plan: str,
                             itinerary: Dict[str, Any], google_maps_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Create GeoJSON with user-provided Google Maps API key.
    """
    original_gmaps = globals().get('gmaps')

    try:
        if google_maps_key:
            global gmaps
            gmaps = googlemaps.Client(key=google_maps_key)

        return create_geojson(start, end, directions, preferences, trip_plan, itinerary)

    finally:
        # Restore original client
        globals()['gmaps'] = original_gmaps
