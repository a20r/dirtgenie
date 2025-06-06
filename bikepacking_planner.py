#!/usr/bin/env python3
"""
Bikepacking Trip Planner

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
    yaml_content = f"""# Bikepacking Trip Planner Profile
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
    print("\n🏕️  Let's customize your bikepacking adventure!")
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


def plan_tour_itinerary(start: str, end: str, nights: int, preferences: Dict[str, str]) -> Dict[str, Any]:
    """
    First step: Plan the tour itinerary with specific waypoints and overnight stops.
    This determines WHERE to go before figuring out HOW to get there.

    Args:
        start: Starting location
        end: Ending location
        nights: Number of nights
        preferences: User preferences from follow-up questions

    Returns:
        Dictionary containing planned itinerary with waypoints and overnight stops
    """
    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")

    # Get daily distance preference
    daily_distance = preferences.get('daily_distance', '60-80')
    if 'km' in daily_distance:
        daily_distance = daily_distance.replace('km', '').strip()

    # Estimate rough distance for planning
    try:
        # Get a quick direct route estimate for planning purposes only
        rough_directions = get_bicycle_directions(start, end)
        total_distance = sum(leg['distance']['value'] for leg in rough_directions['legs']) / 1000
    except:
        # Fallback if route query fails
        total_distance = 100  # Default assumption

    prompt = f"""
You are an expert bikepacking tour planner. Your job is to plan the ITINERARY first - determining the best places to visit and stay overnight.

TRIP PARAMETERS:
- Start: {start}
- End: {end}
- Duration: {nights} nights ({nights + 1} days)
- Rough total distance: {total_distance:.0f} km
- Daily distance preference: {daily_distance} km per day

USER PREFERENCES:
- Accommodation: {preferences.get('accommodation', 'mixed')}
- Stealth camping allowed: {preferences.get('stealth_camping', False)}
- Fitness level: {preferences.get('fitness_level', 'intermediate')}
- Terrain preference: {preferences.get('terrain', 'mixed')}
- Budget: {preferences.get('budget', 'moderate')}
- Interests: {', '.join(preferences.get('interests', []))}

TASK: Plan a {nights + 1}-day itinerary with specific waypoints and overnight locations.

REQUIREMENTS:
1. Identify the best intermediate destinations that make sense for a bikepacking tour
2. Consider scenic routes, points of interest, accommodation availability
3. Plan realistic daily segments based on terrain and fitness level
4. Choose specific towns/cities/landmarks as overnight stops
5. Return the plan in this exact JSON format:

{{
    "itinerary": {{
        "day_1": {{
            "start_location": "{start}",
            "end_location": "Specific Town/City Name",
            "overnight_location": "Specific accommodation name or camping area",
            "highlights": ["attraction 1", "attraction 2"],
            "estimated_distance_km": 75
        }},
        "day_2": {{
            "start_location": "Previous end location",
            "end_location": "Next Town/City Name",
            "overnight_location": "Specific accommodation name or camping area",
            "highlights": ["attraction 1", "attraction 2"],
            "estimated_distance_km": 80
        }},
        ...continue for all {nights + 1} days...
        "day_{nights + 1}": {{
            "start_location": "Previous end location",
            "end_location": "{end}",
            "overnight_location": "Arrive at destination",
            "highlights": ["final attractions"],
            "estimated_distance_km": 65
        }}
    }},
    "total_estimated_distance": 400,
    "route_summary": "Brief description of the overall route"
}}

Be specific with location names (include city, state/province). Choose real places that make sense for bikepacking.
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert bikepacking tour planner. Always respond with valid JSON exactly as requested."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.9
        )

        import json
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")

        itinerary_json = content.strip()

        # Clean up the response to ensure it's valid JSON
        if itinerary_json.startswith('```json'):
            itinerary_json = itinerary_json[7:]
        if itinerary_json.endswith('```'):
            itinerary_json = itinerary_json[:-3]

        itinerary = json.loads(itinerary_json)
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
                       itinerary: Dict[str, Any], directions: Dict[str, Any]) -> str:
    """
    Generate a detailed trip plan using the planned itinerary and route data.

    Args:
        start: Starting location
        end: Ending location
        nights: Number of nights
        preferences: User preferences from follow-up questions
        itinerary: Planned itinerary with waypoints
        directions: Google Maps directions data for the planned route

    Returns:
        Detailed trip plan as markdown string
    """

    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")

    # Extract route information
    total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000  # Convert to km
    total_duration = sum(leg['duration']['value'] for leg in directions['legs']) / 3600  # Convert to hours

    # Create detailed prompt for OpenAI
    prompt = f"""
You are an expert bikepacking trip planner. Create a detailed {nights}-night bikepacking itinerary based on the planned route.

PLANNED ITINERARY:
{json.dumps(itinerary, indent=2)}

ACTUAL ROUTE INFORMATION:
- Total distance: {total_distance:.1f} km
- Estimated cycling time: {total_duration:.1f} hours
- Route segments: {len(directions['legs'])} legs

USER PREFERENCES:
- Accommodation: {preferences.get('accommodation', 'mixed')}
- Stealth camping allowed: {preferences.get('stealth_camping', False)}
- Fitness level: {preferences.get('fitness_level', 'intermediate')}
- Daily distance preference: {preferences.get('daily_distance', '50-80')} km
- Terrain preference: {preferences.get('terrain', 'mixed')}
- Budget: {preferences.get('budget', 'moderate')}
- Interests: {', '.join(preferences.get('interests', []))}

REQUIREMENTS:
1. Use the planned itinerary as your foundation
2. Enhance each day with detailed recommendations
3. Include specific accommodation details for each overnight location
4. Add points of interest, food stops, and resupply opportunities along each leg
5. Include packing suggestions and safety considerations
6. Provide weather and seasonal considerations
7. Include emergency contacts and backup plans

FORMAT as detailed markdown with:
- Trip overview matching the planned route
- Daily itineraries with actual distances, elevation, accommodation, highlights
- Specific recommendations for each planned waypoint
- Packing list
- Safety and emergency information
- Budget estimates
- Additional tips and considerations

Make this a comprehensive, actionable plan that follows the planned itinerary.
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert bikepacking guide with extensive knowledge of routes, gear, safety, and local attractions worldwide."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.5
        )

        return response.choices[0].message.content or "Error: Empty response from OpenAI"
    except Exception as e:
        print(f"Error generating trip plan: {e}")
        return generate_trip_plan_fallback(start, end, nights, preferences, itinerary, directions)


def generate_trip_plan_fallback(start: str, end: str, nights: int, preferences: Dict[str, str],
                                itinerary: Dict[str, Any], directions: Dict[str, Any]) -> str:
    """
    Fallback trip plan generation without function calling.
    """
    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")

    # Extract route information
    total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000  # Convert to km
    total_duration = sum(leg['duration']['value'] for leg in directions['legs']) / 3600  # Convert to hours

    # Create a simple trip plan based on the itinerary
    daily_plans = itinerary.get('itinerary', {})

    trip_plan = f"""# Bikepacking Trip: {start} to {end}

## Trip Overview
- **Duration**: {nights} nights ({nights + 1} days)
- **Total Distance**: {total_distance:.1f} km
- **Estimated Cycling Time**: {total_duration:.1f} hours
- **Accommodation Style**: {preferences.get('accommodation', 'mixed')}
- **Fitness Level**: {preferences.get('fitness_level', 'intermediate')}

## Daily Itinerary
"""

    for day_key in sorted(daily_plans.keys()):
        day_plan = daily_plans[day_key]
        day_num = day_key.split('_')[1]

        trip_plan += f"""
### Day {day_num}: {day_plan['start_location']} to {day_plan['end_location']}
- **Distance**: {day_plan.get('estimated_distance_km', 'TBD')} km
- **Accommodation**: {day_plan.get('overnight_location', 'TBD')}
- **Highlights**: {', '.join(day_plan.get('highlights', []))}
"""

    trip_plan += f"""
## Packing List
- Tent and sleeping gear
- Bike repair tools and spare tubes
- Weather-appropriate clothing
- First aid kit
- Navigation tools (GPS device or smartphone)
- Water bottles and purification tablets
- Cooking gear and food

## Safety Information
- Emergency contacts: 911 (US/Canada)
- Check weather conditions before departure
- Inform someone of your planned route
- Carry identification and emergency information

## Budget Estimate
- **{preferences.get('budget', 'moderate')} budget**: Estimated $50-150 per day
- Includes meals, accommodation, and incidentals

Generated with fallback method on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return trip_plan


def extract_overnight_locations(trip_plan: str, itinerary: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Extract overnight accommodation locations from the trip plan text or structured itinerary.

    Args:
        trip_plan: The generated trip plan as markdown text
        itinerary: Optional structured itinerary data

    Returns:
        List of location names where overnight stays are planned
    """
    overnight_locations = []

    # If we have structured itinerary data, use that first (more reliable)
    if itinerary and 'itinerary' in itinerary:
        daily_plans = itinerary['itinerary']
        for day_key in sorted(daily_plans.keys()):
            day_plan = daily_plans[day_key]
            overnight_location = day_plan.get('overnight_location', '')
            if overnight_location and overnight_location != "Arrive at destination":
                overnight_locations.append(overnight_location)
        return overnight_locations

    # Fallback to text parsing if no structured itinerary
    import re

    # Look for accommodation patterns in the trip plan
    accommodation_patterns = [
        r'\*\*Accommodation\*\*:\s*([^*\n]+)',  # **Accommodation**: Location
        r'Accommodation:\s*([^*\n]+)',          # Accommodation: Location
        r'camping\s+(?:near|at)\s+([^,.\n]+)',  # camping near/at Location
        r'staying\s+(?:at|in)\s+([^,.\n]+)',    # staying at/in Location
        r'camp\s+(?:at|near)\s+([^,.\n]+)',     # camp at/near Location
        r'stealth\s+camping\s+(?:near|at)\s+([^,.\n]+)',  # stealth camping near/at Location
    ]

    for pattern in accommodation_patterns:
        matches = re.finditer(pattern, trip_plan, re.IGNORECASE)
        for match in matches:
            location = match.group(1).strip()
            # Clean up the location string
            location = re.sub(r'\([^)]*\)', '', location)  # Remove parentheses content
            location = location.replace('**', '').strip()   # Remove markdown bold
            if location and location not in overnight_locations:
                overnight_locations.append(location)

    return overnight_locations


def create_geojson(start: str, end: str, directions: Dict[str, Any],
                   preferences: Dict[str, str], trip_plan: str = "",
                   itinerary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a GeoJSON file with detailed route information.

    Args:
        start: Starting location
        end: Ending location
        directions: Google Maps directions data
        preferences: User preferences
        trip_plan: Generated trip plan text (optional)
        itinerary: Planned itinerary with structured waypoint data (optional)

    Returns:
        GeoJSON data structure
    """

    # Extract route coordinates
    coordinates = extract_route_points(directions)

    # Calculate total distance and duration
    total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000
    total_duration = sum(leg['duration']['value'] for leg in directions['legs']) / 3600

    # Create GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": {
                    "trip_type": "bikepacking",
                    "start_location": start,
                    "end_location": end,
                    "total_distance_km": round(total_distance, 2),
                    "estimated_cycling_hours": round(total_duration, 2),
                    "user_preferences": preferences,
                    "generated_date": datetime.now().isoformat(),
                    "route_summary": directions.get('summary', 'Generated route'),
                    "warnings": [warning.get('text', warning) if isinstance(warning, dict) else str(warning)
                                 for warning in directions.get('warnings', [])],
                    "copyrights": directions.get('copyrights', '')
                }
            }
        ]
    }

    # Add waypoints as separate features
    for i, leg in enumerate(directions['legs']):
        # Start point
        start_point = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    leg['start_location']['lng'],
                    leg['start_location']['lat']
                ]
            },
            "properties": {
                "type": "waypoint",
                "leg_number": i + 1,
                "address": leg['start_address'],
                "distance_km": round(leg['distance']['value'] / 1000, 2),
                "duration_hours": round(leg['duration']['value'] / 3600, 2)
            }
        }
        geojson["features"].append(start_point)

    # Add final destination
    if directions['legs']:
        last_leg = directions['legs'][-1]
        end_point = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    last_leg['end_location']['lng'],
                    last_leg['end_location']['lat']
                ]
            },
            "properties": {
                "type": "destination",
                "address": last_leg['end_address']
            }
        }
        geojson["features"].append(end_point)

    # Add overnight accommodation markers if trip plan is provided
    if trip_plan:
        overnight_locations = extract_overnight_locations(trip_plan, itinerary)

        # Try to get more precise locations from itinerary structure first
        if itinerary and 'itinerary' in itinerary:
            daily_plans = itinerary['itinerary']
            legs_per_day = {}

            # Map days to legs based on the multi-waypoint structure
            leg_index = 0
            for day_key in sorted(daily_plans.keys()):
                if leg_index < len(directions['legs']):
                    legs_per_day[day_key] = leg_index
                    leg_index += 1

            # Add overnight markers at the end of each day's route
            for day_key in sorted(daily_plans.keys()):
                day_plan = daily_plans[day_key]
                overnight_location = day_plan.get('overnight_location', '')

                # Skip if this is the final day (arrival at destination)
                if 'arrive at destination' in overnight_location.lower() or day_key == max(daily_plans.keys()):
                    continue

                # Get the leg for this day
                if day_key in legs_per_day:
                    leg_idx = legs_per_day[day_key]
                    if leg_idx < len(directions['legs']):
                        leg = directions['legs'][leg_idx]

                        # Use the end point of this leg as the overnight location
                        overnight_marker = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [
                                    leg['end_location']['lng'],
                                    leg['end_location']['lat']
                                ]
                            },
                            "properties": {
                                "type": "overnight_accommodation",
                                "day": day_key,
                                "location_name": overnight_location,
                                "address": leg['end_address'],
                                "precise_location": True,
                                "marker_symbol": "campground",
                                "marker_color": "#FF6B35",
                                "description": f"{day_key.replace('_', ' ').title()} accommodation: {overnight_location}",
                                "highlights": day_plan.get('highlights', []),
                                "estimated_distance_km": day_plan.get('estimated_distance_km', 0)
                            }
                        }
                        geojson["features"].append(overnight_marker)

        # Fallback to distance-based estimation if no structured itinerary
        elif overnight_locations:
            route_coordinates = []
            for leg in directions['legs']:
                for step in leg['steps']:
                    if 'polyline' in step and 'points' in step['polyline']:
                        try:
                            decoded_points = polyline.decode(step['polyline']['points'])
                            route_coordinates.extend(decoded_points)
                        except Exception:
                            continue

            if route_coordinates:
                for i, location in enumerate(overnight_locations):
                    # Estimate position along route (distribute evenly by distance)
                    position_ratio = (i + 1) / (len(overnight_locations) + 1)
                    coord_index = int(position_ratio * len(route_coordinates))

                    if coord_index < len(route_coordinates):
                        lat, lng = route_coordinates[coord_index]

                        overnight_marker = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [lng, lat]
                            },
                            "properties": {
                                "type": "overnight_accommodation",
                                "night_number": i + 1,
                                "location_name": location,
                                "estimated_location": True,
                                "marker_symbol": "campground",
                                "marker_color": "#FF6B35",
                                "description": f"Night {i + 1} accommodation: {location}"
                            }
                        }
                        geojson["features"].append(overnight_marker)

    return geojson


def save_outputs(trip_plan: str, geojson_data: Dict[str, Any], start: str, end: str) -> Tuple[str, str]:
    """
    Save the trip plan and GeoJSON to files.

    Args:
        trip_plan: Markdown trip plan content
        geojson_data: GeoJSON data structure
        start: Starting location (for filename)
        end: Ending location (for filename)

    Returns:
        Tuple of (markdown_filename, geojson_filename)
    """

    # Create safe filenames
    safe_start = "".join(c for c in start if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_end = "".join(c for c in end if c.isalnum() or c in (' ', '-', '_')).rstrip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save markdown file
    md_filename = f"bikepacking_trip_{safe_start}_to_{safe_end}_{timestamp}.md"
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(trip_plan)

    # Save GeoJSON file
    geojson_filename = f"bikepacking_route_{safe_start}_to_{safe_end}_{timestamp}.geojson"
    with open(geojson_filename, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, indent=2, ensure_ascii=False)

    return md_filename, geojson_filename


# OpenAI tools definitions for intelligent route planning
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_bicycle_route",
            "description": "Get bicycle directions between two locations using Google Maps",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "string",
                        "description": "Starting location (city, address, or landmark)"
                    },
                    "end": {
                        "type": "string",
                        "description": "Ending location (city, address, or landmark)"
                    },
                    "waypoints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional intermediate stops along the route"
                    }
                },
                "required": ["start", "end"]
            }
        }
    }
]


def openai_function_get_bicycle_route(start: str, end: str, waypoints: Optional[List[str]] = None) -> str:
    """
    OpenAI function to get bicycle route information.

    Returns:
        JSON string with route information
    """
    try:
        directions = get_bicycle_directions(start, end, waypoints)
        if not directions or 'legs' not in directions:
            return json.dumps({"error": "No route found"})

        total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000
        total_duration = sum(leg['duration']['value'] for leg in directions['legs']) / 3600

        route_info = {
            "total_distance_km": round(total_distance, 2),
            "estimated_hours": round(total_duration, 2),
            "legs": len(directions['legs']),
            "summary": directions.get('summary', 'Route found'),
            "warnings": [w.get('text', '') for w in directions.get('warnings', [])]
        }

        return json.dumps(route_info)
    except Exception as e:
        return json.dumps({"error": str(e)})


def main():
    """
    Main function to run the bikepacking trip planner.
    """
    # Initialize API clients first
    try:
        initialize_clients()
    except ValueError as e:
        print(f"❌ {e}")
        print("Please set up your API keys and try again.")
        return

    parser = argparse.ArgumentParser(description="Intelligent Bikepacking Trip Planner")
    parser.add_argument("start", help="Starting location")
    parser.add_argument("end", help="Ending location")
    parser.add_argument("nights", type=int, help="Number of nights for the trip")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enable interactive mode to ask preference questions")
    parser.add_argument("-p", "--profile", default="profile.yml",
                        help="Path to YAML profile file with preferences (default: profile.yml)")

    args = parser.parse_args()

    print("🚴‍♀️ Bikepacking Trip Planner")
    print("=" * 50)
    print(f"Planning a {args.nights}-night trip from {args.start} to {args.end}")

    # Get user preferences (either interactive or from profile)
    preferences = get_user_preferences(interactive=args.interactive, profile_path=args.profile)

    print(f"\n🧠 Planning your tour itinerary (determining waypoints and overnight stops)...")

    # Step 1: Plan the tour itinerary first
    itinerary = plan_tour_itinerary(args.start, args.end, args.nights, preferences)

    print(f"✅ Itinerary planned with {len(itinerary.get('itinerary', {}))} days")

    print(f"\n🗺️  Getting bicycle route information for your planned tour...")

    # Step 2: Get multi-waypoint directions for the planned itinerary
    directions = get_multi_waypoint_directions(itinerary)
    if not directions or 'legs' not in directions:
        print("❌ Could not get route information. Please check your locations and try again.")
        return

    total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000
    print(f"✅ Route found: {total_distance:.1f} km total distance")

    print(f"\n🤖 Generating your detailed trip plan with OpenAI...")

    # Step 3: Generate detailed trip plan based on the itinerary and route
    trip_plan = generate_trip_plan(args.start, args.end, args.nights, preferences, itinerary, directions)

    print(f"\n📍 Creating detailed route GeoJSON...")

    # Create GeoJSON
    geojson_data = create_geojson(args.start, args.end, directions, preferences, trip_plan, itinerary)

    print(f"\n💾 Saving files...")

    # Save outputs
    md_file, geojson_file = save_outputs(trip_plan, geojson_data, args.start, args.end)

    print(f"\n🎉 Trip planning complete!")
    print(f"📄 Trip plan saved to: {md_file}")
    print(f"🗺️  Route data saved to: {geojson_file}")
    print(f"\nHappy bikepacking! 🚴‍♀️🏕️")


if __name__ == "__main__":
    main()
