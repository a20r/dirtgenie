#!/usr/bin/env python3
"""
Streamlit Web App for Bikepacking Trip Planner

A web interface that wraps around the bikepacking_planner.py CLI tool.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

# Import our bikepacking planner modules
from bikepacking_planner import (create_default_profile, create_geojson, generate_trip_plan,
                                 get_multi_waypoint_directions, initialize_clients, plan_tour_itinerary,
                                 revise_trip_plan_with_feedback)


def load_env_api_keys():
    """Load API keys from environment variables."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    google_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    return openai_key, google_key


def set_api_keys(openai_key: str, google_key: str):
    """Set API keys in environment variables."""
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["GOOGLE_MAPS_API_KEY"] = google_key


def validate_api_keys():
    """Validate that API keys are set and not empty."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    google_key = os.getenv("GOOGLE_MAPS_API_KEY", "")

    if not openai_key:
        st.error("❌ OpenAI API Key is required")
        return False
    if not google_key:
        st.error("❌ Google Maps API Key is required")
        return False

    return True


def create_geojson_layer(geojson_data):
    """Create a pydeck layer for GeoJSON visualization."""
    features = geojson_data.get("features", [])

    # Extract route coordinates
    route_coords = []
    waypoint_coords = []
    overnight_coords = []

    for feature in features:
        if feature["geometry"]["type"] == "LineString":
            # Main route
            coords = feature["geometry"]["coordinates"]
            route_coords = [[lng, lat] for lng, lat in coords]
        elif feature["geometry"]["type"] == "Point":
            props = feature["properties"]
            coord = feature["geometry"]["coordinates"]

            if props.get("type") == "waypoint":
                waypoint_coords.append({
                    "coordinates": [coord[0], coord[1]],
                    "name": props.get("name", "Waypoint"),
                    "type": "waypoint"
                })
            elif props.get("type") == "overnight_accommodation":
                overnight_coords.append({
                    "coordinates": [coord[0], coord[1]],
                    "name": props.get("location_name", "Accommodation"),
                    "type": "accommodation"
                })

    layers = []

    # Route line layer
    if route_coords:
        route_df = pd.DataFrame({"path": [route_coords]})
        layers.append(
            pdk.Layer(
                "PathLayer",
                data=route_df,
                get_path="path",
                get_width=5,
                get_color=[51, 128, 255],
                width_scale=20,
                width_min_pixels=2,
                pickable=True,
            )
        )

    # Waypoint markers
    if waypoint_coords:
        waypoint_df = pd.DataFrame(waypoint_coords)
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=waypoint_df,
                get_position="coordinates",
                get_color=[255, 165, 0],
                get_radius=1000,
                radius_scale=1,
                pickable=True,
            )
        )

    # Overnight accommodation markers
    if overnight_coords:
        overnight_df = pd.DataFrame(overnight_coords)
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=overnight_df,
                get_position="coordinates",
                get_color=[255, 75, 75],
                get_radius=1500,
                radius_scale=1,
                pickable=True,
            )
        )

    return layers, route_coords


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="🚴‍♀️ Bikepacking Trip Planner",
        page_icon="🚴‍♀️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🚴‍♀️ Bikepacking Trip Planner")
    st.markdown("Plan your perfect bikepacking adventure with AI-powered route optimization!")

    # Sidebar for API keys
    st.sidebar.header("🔑 API Configuration")
    st.sidebar.markdown("Configure your API keys to use the planner:")

    # Load default API keys from environment
    default_openai, default_google = load_env_api_keys()

    # API Key inputs
    openai_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=default_openai,
        type="password",
        help="Required for AI trip planning"
    )

    google_key = st.sidebar.text_input(
        "Google Maps API Key",
        value=default_google,
        type="password",
        help="Required for route directions"
    )

    # Set API keys in environment
    if openai_key and google_key:
        set_api_keys(openai_key, google_key)
        st.sidebar.success("✅ API Keys configured")
    else:
        st.sidebar.warning("⚠️ Please enter both API keys")

    # Main form
    st.header("📍 Trip Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        start_location = st.text_input(
            "Start Location",
            placeholder="e.g., Boston, MA",
            help="Starting point for your bikepacking trip"
        )

    with col2:
        end_location = st.text_input(
            "End Location",
            placeholder="e.g., Portland, ME",
            help="Destination for your trip"
        )

    with col3:
        nights = st.number_input(
            "Number of Nights",
            min_value=1,
            max_value=30,
            value=3,
            help="How many nights you want to spend on the trip"
        )

    # Profile preferences
    st.header("🏕️ Trip Preferences")

    # Load default profile for prefilled values
    default_profile = create_default_profile()

    col1, col2 = st.columns(2)

    with col1:
        accommodation = st.selectbox(
            "Accommodation Preference",
            options=["camping", "hotels", "mixed"],
            index=["camping", "hotels", "mixed"].index(default_profile["accommodation"]),
            help="Type of accommodation you prefer"
        )

        fitness_level = st.selectbox(
            "Fitness Level",
            options=["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(default_profile["fitness_level"]),
            help="Your cycling fitness level"
        )

        terrain = st.selectbox(
            "Terrain Preference",
            options=["paved", "gravel", "mixed", "challenging"],
            index=["paved", "gravel", "mixed", "challenging"].index(default_profile["terrain"]),
            help="Type of terrain you prefer to ride"
        )

    with col2:
        stealth_camping = st.checkbox(
            "Allow Stealth/Wild Camping",
            value=default_profile["stealth_camping"],
            help="Whether you're comfortable with stealth camping"
        )

        daily_distance = st.slider(
            "Daily Distance (km)",
            min_value=20,
            max_value=150,
            value=(50, 80),  # Default range
            help="Preferred daily distance range"
        )

        budget = st.selectbox(
            "Budget Range",
            options=["budget", "moderate", "luxury"],
            index=["budget", "moderate", "luxury"].index(default_profile["budget"]),
            help="Your daily budget range"
        )

    # Interests (multi-select)
    interests = st.multiselect(
        "Special Interests",
        options=["nature", "adventure", "history", "food", "photography", "culture", "wildlife", "mountains", "coast"],
        default=default_profile["interests"],
        help="Select your interests to customize recommendations"
    )

    # Plan Trip button
    st.header("🚀 Generate Your Trip")

    if st.button("🗺️ Plan Trip", type="primary", use_container_width=True):
        if not start_location or not end_location:
            st.error("❌ Please enter both start and end locations")
            return

        if not validate_api_keys():
            st.error("❌ Please configure your API keys in the sidebar")
            return

        # Create preferences dictionary
        preferences = {
            "accommodation": accommodation,
            "stealth_camping": stealth_camping,
            "fitness_level": fitness_level,
            "daily_distance": f"{daily_distance[0]}-{daily_distance[1]}",  # Convert slider to string format
            "terrain": terrain,
            "budget": budget,
            "interests": interests
        }

        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Initialize clients
            status_text.text("🔧 Initializing API clients...")
            progress_bar.progress(10)
            initialize_clients()

            # Step 1: Plan the itinerary
            status_text.text("🧠 Planning your tour itinerary...")
            progress_bar.progress(30)
            itinerary = plan_tour_itinerary(start_location, end_location, nights, preferences)

            # Step 2: Get route directions
            status_text.text("🗺️ Getting bicycle route information...")
            progress_bar.progress(50)
            directions = get_multi_waypoint_directions(itinerary)

            if not directions or 'legs' not in directions:
                st.error("❌ Could not find a bicycle route between the specified locations")
                return

            # Step 3: Generate detailed trip plan
            status_text.text("📝 Generating detailed trip plan...")
            progress_bar.progress(70)
            trip_plan = generate_trip_plan(start_location, end_location, nights, preferences, itinerary, directions)

            # Step 4: Create GeoJSON
            status_text.text("📍 Creating route visualization...")
            progress_bar.progress(90)
            geojson_data = create_geojson(start_location, end_location, directions, preferences, trip_plan, itinerary)

            progress_bar.progress(100)
            status_text.text("✅ Trip planning complete!")

            # Display results
            st.success("🎉 Your bikepacking trip has been planned!")

            # Calculate total distance
            total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000
            st.metric("Total Distance", f"{total_distance:.1f} km")

            # Store data in session state for feedback functionality
            if 'trip_data' not in st.session_state:
                st.session_state.trip_data = {}
            
            st.session_state.trip_data = {
                'start_location': start_location,
                'end_location': end_location,
                'nights': nights,
                'preferences': preferences,
                'itinerary': itinerary,
                'directions': directions,
                'trip_plan': trip_plan,
                'geojson_data': geojson_data
            }

            # Create tabs for better layout
            tab1, tab2 = st.tabs(["📄 Trip Plan", "🗺️ Route Map"])
            
            with tab1:
                st.markdown(trip_plan)
                
                # Download button for markdown
                st.download_button(
                    label="💾 Download Trip Plan",
                    data=trip_plan,
                    file_name=f"bikepacking_trip_{start_location.replace(' ', '_')}_to_{end_location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
                # Feedback section
                st.header("💬 Feedback & Revisions")
                feedback = st.text_area(
                    "Any changes you'd like to make to this plan?",
                    placeholder="e.g., 'I'd prefer more camping options instead of hotels' or 'Can we add more scenic stops along the route?' or 'The daily distances seem too long for my fitness level'",
                    help="Provide specific feedback about what you'd like to change in your trip plan"
                )
                
                if st.button("🔄 Revise Plan", disabled=not feedback):
                    with st.spinner("🤖 Revising your trip plan based on feedback..."):
                        try:
                            revised_plan = revise_trip_plan_with_feedback(
                                trip_plan, feedback, start_location, end_location, 
                                nights, preferences, itinerary, directions
                            )
                            st.session_state.trip_data['trip_plan'] = revised_plan
                            st.success("✅ Plan revised! Check the updated trip plan above.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error revising plan: {str(e)}")

            with tab2:
                # Create map visualization
                layers, route_coords = create_geojson_layer(geojson_data)

                if route_coords:
                    # Calculate map center
                    center_lat = sum(coord[1] for coord in route_coords) / len(route_coords)
                    center_lng = sum(coord[0] for coord in route_coords) / len(route_coords)

                    # Create deck
                    deck = pdk.Deck(
                        map_style='mapbox://styles/mapbox/outdoors-v11',
                        initial_view_state=pdk.ViewState(
                            latitude=center_lat,
                            longitude=center_lng,
                            zoom=10,
                            pitch=0,
                        ),
                        layers=layers,
                        tooltip={
                            "text": "{name}\nType: {type}"  # type: ignore
                        }
                    )

                    st.pydeck_chart(deck)

                    # Legend
                    st.markdown("""
                    **Map Legend:**
                    - 🔵 Blue line: Bike route
                    - 🟠 Orange dots: Waypoints
                    - 🔴 Red dots: Overnight accommodation
                    """)
                else:
                    st.warning("⚠️ Could not generate map visualization")

                # Download button for GeoJSON
                st.download_button(
                    label="💾 Download Route Data (GeoJSON)",
                    data=json.dumps(geojson_data, indent=2),
                    file_name=f"bikepacking_route_{start_location.replace(' ', '_')}_to_{end_location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson",
                    mime="application/json"
                )

        except Exception as e:
            st.error(f"❌ Error generating trip plan: {str(e)}")
            st.exception(e)
        finally:
            progress_bar.empty()
            status_text.empty()

    # Display existing trip if it's in session state (for continued feedback)
    elif 'trip_data' in st.session_state and st.session_state.trip_data:
        st.header("📋 Your Current Trip Plan")
        trip_data = st.session_state.trip_data
        
        # Display current trip metrics
        total_distance = sum(leg['distance']['value'] for leg in trip_data['directions']['legs']) / 1000
        st.metric("Total Distance", f"{total_distance:.1f} km")
        
        # Create tabs for better layout
        tab1, tab2 = st.tabs(["📄 Trip Plan", "🗺️ Route Map"])
        
        with tab1:
            st.markdown(trip_data['trip_plan'])
            
            # Download button for markdown
            st.download_button(
                label="💾 Download Trip Plan",
                data=trip_data['trip_plan'],
                file_name=f"bikepacking_trip_{trip_data['start_location'].replace(' ', '_')}_to_{trip_data['end_location'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
            # Feedback section
            st.header("💬 Feedback & Revisions")
            feedback = st.text_area(
                "Any changes you'd like to make to this plan?",
                placeholder="e.g., 'I'd prefer more camping options instead of hotels' or 'Can we add more scenic stops along the route?' or 'The daily distances seem too long for my fitness level'",
                help="Provide specific feedback about what you'd like to change in your trip plan"
            )
            
            if st.button("🔄 Revise Plan", disabled=not feedback):
                with st.spinner("🤖 Revising your trip plan based on feedback..."):
                    try:
                        revised_plan = revise_trip_plan_with_feedback(
                            trip_data['trip_plan'], feedback, trip_data['start_location'], 
                            trip_data['end_location'], trip_data['nights'], trip_data['preferences'], 
                            trip_data['itinerary'], trip_data['directions']
                        )
                        st.session_state.trip_data['trip_plan'] = revised_plan
                        st.success("✅ Plan revised! The updated trip plan is shown above.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error revising plan: {str(e)}")

        with tab2:
            # Create map visualization
            layers, route_coords = create_geojson_layer(trip_data['geojson_data'])

            if route_coords:
                # Calculate map center
                center_lat = sum(coord[1] for coord in route_coords) / len(route_coords)
                center_lng = sum(coord[0] for coord in route_coords) / len(route_coords)

                # Create deck
                deck = pdk.Deck(
                    map_style='mapbox://styles/mapbox/outdoors-v11',
                    initial_view_state=pdk.ViewState(
                        latitude=center_lat,
                        longitude=center_lng,
                        zoom=10,
                        pitch=0,
                    ),
                    layers=layers,
                    tooltip={
                        "text": "{name}\nType: {type}"  # type: ignore
                    }
                )

                st.pydeck_chart(deck)

                # Legend
                st.markdown("""
                **Map Legend:**
                - 🔵 Blue line: Bike route
                - 🟠 Orange dots: Waypoints
                - 🔴 Red dots: Overnight accommodation
                """)
            else:
                st.warning("⚠️ Could not generate map visualization")

            # Download button for GeoJSON
            st.download_button(
                label="💾 Download Route Data (GeoJSON)",
                data=json.dumps(trip_data['geojson_data'], indent=2),
                file_name=f"bikepacking_route_{trip_data['start_location'].replace(' ', '_')}_to_{trip_data['end_location'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson",
                mime="application/json"
            )

    # Footer
    st.markdown("---")
    st.markdown("""
    **🚴‍♀️ Bikepacking Trip Planner** - Plan your perfect bikepacking adventure with AI-powered route optimization!
    
    Features:
    - 🧠 AI-powered itinerary planning
    - 🗺️ Google Maps bicycle route optimization  
    - 📍 Interactive map visualization
    - 📝 Detailed trip plans with current information
    - 🏕️ Accommodation and camping recommendations
    - 🌤️ Weather-aware planning
    """)


if __name__ == "__main__":
    main()
