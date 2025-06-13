import io
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the src directory to Python path BEFORE imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from dirtgenie.planner import (create_default_profile, create_geojson, create_geojson_with_keys, generate_trip_plan,
                               generate_trip_plan_with_keys, get_bicycle_directions, get_multi_waypoint_directions,
                               get_multi_waypoint_directions_with_keys, initialize_clients, load_profile,
                               plan_tour_itinerary, plan_tour_itinerary_with_keys, revise_trip_plan_with_feedback,
                               save_profile)

app = FastAPI(
    title="DirtGenie API",
    description="AI-Powered Bikepacking Trip Planner API",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response


class TripPreferences(BaseModel):
    accommodation: str = Field(default="mixed", description="Accommodation preference")
    stealth_camping: bool = Field(default=False, description="Allow stealth camping")
    fitness_level: str = Field(default="intermediate", description="Fitness level")
    daily_distance: str = Field(default="50-80", description="Daily distance range in km")
    terrain: str = Field(default="mixed", description="Terrain preference")
    tire_size: str = Field(default="700x35c (Gravel - Standard)", description="Bike tire size")
    budget: str = Field(default="moderate", description="Budget preference")
    interests: List[str] = Field(default=[], description="Interests and activities")


class TripPlanRequest(BaseModel):
    desires: List[str] = Field(default=[], description="User desires and specific requests")
    start_location: str = Field(..., description="Starting location")
    end_location: str = Field(..., description="Ending location")
    nights: int = Field(..., ge=1, le=30, description="Number of nights (1-30)")
    departure_date: Optional[str] = Field(None, description="Departure date (YYYY-MM-DD)")
    preferences: TripPreferences


class TripRevisionRequest(BaseModel):
    original_plan: str = Field(..., description="Original trip plan markdown")
    feedback: str = Field(..., description="User feedback for revision")
    trip_request: TripPlanRequest


class TripPlanResponse(BaseModel):
    success: bool
    trip_plan: Optional[str] = None
    itinerary: Optional[Dict[str, Any]] = None
    geojson: Optional[Dict[str, Any]] = None
    total_distance: Optional[float] = None
    error: Optional[str] = None


class ProfileRequest(BaseModel):
    profile_name: str = Field(..., description="Profile name")
    preferences: TripPreferences


class NotionExportRequest(BaseModel):
    trip_plan: str = Field(..., description="Trip plan markdown")
    page_title: str = Field(..., description="Title for the Notion page")
    start_location: Optional[str] = Field(None, description="Start location")
    end_location: Optional[str] = Field(None, description="End location")


class ApiKeyTestRequest(BaseModel):
    openai_key: str = Field(..., description="OpenAI API key to test")
    google_maps_key: str = Field(..., description="Google Maps API key to test")


class DownloadRequest(BaseModel):
    trip_plan: str = Field(..., description="Trip plan markdown")
    geojson: Optional[Dict[str, Any]] = Field(None, description="GeoJSON route data")
    total_distance: Optional[float] = Field(None, description="Total distance in km")
    start_location: Optional[str] = Field(None, description="Start location")
    end_location: Optional[str] = Field(None, description="End location")


# Global variables for storing trip data (in production, use a proper database)
trip_cache = {}


@app.on_event("startup")
async def startup_event():
    """Initialize API clients on startup"""
    try:
        initialize_clients()
    except Exception as e:
        print(f"Warning: Could not initialize API clients: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "DirtGenie API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/test-keys")
async def test_api_keys(request: ApiKeyTestRequest):
    """Test the provided API keys"""
    try:
        # Test OpenAI API key
        try:
            from openai import OpenAI
            test_openai_client = OpenAI(api_key=request.openai_key)
            # Make a minimal test request
            test_response = test_openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            if not test_response:
                raise Exception("OpenAI API test failed")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OpenAI API key is invalid: {str(e)}")
        
        # Test Google Maps API key
        try:
            import googlemaps
            test_gmaps_client = googlemaps.Client(key=request.google_maps_key)
            # Make a minimal test request
            test_result = test_gmaps_client.geocode("San Francisco, CA")  # type: ignore
            if not test_result:
                raise Exception("Google Maps API test failed")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Google Maps API key is invalid: {str(e)}")
        
        return {"success": True, "message": "API keys are valid"}
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing API keys: {str(e)}")


@app.get("/api/default-profile")
async def get_default_profile():
    """Get default user profile"""
    try:
        profile = create_default_profile()
        return {"success": True, "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/save-profile")
async def save_user_profile(request: ProfileRequest):
    """Save user profile"""
    try:
        # Convert preferences to dict
        preferences_dict = request.preferences.dict()

        # Save profile (this would typically go to a database)
        profile_data = {
            "name": request.profile_name,
            **preferences_dict
        }

        # For demo purposes, just return success
        # In production, save to database or file system
        return {"success": True, "message": f"Profile '{request.profile_name}' saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plan-trip", response_model=TripPlanResponse)
async def plan_trip(
    request: TripPlanRequest, 
    background_tasks: BackgroundTasks,
    x_openai_key: Optional[str] = Header(None),
    x_google_maps_key: Optional[str] = Header(None)
):
    """Plan a bikepacking trip"""
    try:
        # Get API keys from headers (for user-supplied keys) or environment (for development)
        openai_key = x_openai_key or os.getenv("OPENAI_API_KEY")
        google_maps_key = x_google_maps_key or os.getenv("GOOGLE_MAPS_API_KEY")
        
        if not openai_key or not google_maps_key:
            raise HTTPException(
                status_code=400, 
                detail="Missing API keys. Please provide OpenAI and Google Maps API keys."
            )

        # Convert preferences to dict format expected by planner
        preferences = request.preferences.dict()

        # Step 1: Plan the itinerary (with API keys)
        itinerary = plan_tour_itinerary_with_keys(
            start=request.start_location,
            end=request.end_location,
            nights=request.nights,
            preferences=preferences,
            desires=request.desires,
            departure_date=request.departure_date,
            openai_key=openai_key,
            google_maps_key=google_maps_key
        )

        # Step 2: Get route directions (with API keys)
        directions = get_multi_waypoint_directions_with_keys(
            itinerary, 
            google_maps_key=google_maps_key
        )

        if not directions or 'legs' not in directions:
            raise HTTPException(
                status_code=400, detail="Could not find a bicycle route between the specified locations")

        # Step 3: Generate detailed trip plan (with API keys)
        trip_plan = generate_trip_plan_with_keys(
            start=request.start_location,
            end=request.end_location,
            nights=request.nights,
            preferences=preferences,
            itinerary=itinerary,
            directions=directions,
            departure_date=request.departure_date,
            openai_key=openai_key
        )

        # Step 4: Create GeoJSON
        geojson_data = create_geojson_with_keys(
            start=request.start_location,
            end=request.end_location,
            directions=directions,
            preferences=preferences,
            trip_plan=trip_plan,
            itinerary=itinerary,
            google_maps_key=google_maps_key
        )

        # Calculate total distance
        total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000

        # Store in cache for potential revisions
        trip_id = f"{request.start_location}_{request.end_location}_{request.nights}_{datetime.now().timestamp()}"
        trip_cache[trip_id] = {
            "request": request,
            "itinerary": itinerary,
            "directions": directions,
            "trip_plan": trip_plan
        }

        return TripPlanResponse(
            success=True,
            trip_plan=trip_plan,
            itinerary=itinerary,
            geojson=geojson_data,
            total_distance=total_distance
        )

    except Exception as e:
        return TripPlanResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/revise-trip", response_model=TripPlanResponse)
async def revise_trip(request: TripRevisionRequest):
    """Revise a trip plan based on user feedback"""
    try:
        # Convert preferences to dict format
        preferences = request.trip_request.preferences.dict()

        # For this demo, we'll need to re-plan since we don't have the original data
        # In production, you'd store and retrieve the original itinerary and directions

        # Re-plan the itinerary first
        itinerary = plan_tour_itinerary(
            start=request.trip_request.start_location,
            end=request.trip_request.end_location,
            nights=request.trip_request.nights,
            preferences=preferences,
            desires=request.trip_request.desires,
            departure_date=request.trip_request.departure_date
        )

        # Get route directions
        directions = get_multi_waypoint_directions(itinerary)

        # Generate revised trip plan
        revised_plan = revise_trip_plan_with_feedback(
            original_plan=request.original_plan,
            feedback=request.feedback,
            start=request.trip_request.start_location,
            end=request.trip_request.end_location,
            nights=request.trip_request.nights,
            preferences=preferences,
            itinerary=itinerary,
            directions=directions,
            departure_date=request.trip_request.departure_date
        )

        # Create updated GeoJSON
        geojson_data = create_geojson(
            start=request.trip_request.start_location,
            end=request.trip_request.end_location,
            directions=directions,
            preferences=preferences,
            trip_plan=revised_plan,
            itinerary=itinerary
        )

        # Calculate total distance
        total_distance = sum(leg['distance']['value'] for leg in directions['legs']) / 1000

        return TripPlanResponse(
            success=True,
            trip_plan=revised_plan,
            itinerary=itinerary,
            geojson=geojson_data,
            total_distance=total_distance
        )

    except Exception as e:
        return TripPlanResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/tire-options")
async def get_tire_options():
    """Get available tire size options"""
    return {
        "tire_options": [
            "700x23c (Road - Narrow)",
            "700x25c (Road - Standard)",
            "700x28c (Road - Wide)",
            "700x32c (Gravel - Narrow)",
            "700x35c (Gravel - Standard)",
            "700x40c (Gravel - Wide)",
            "650b x 47mm (Gravel+)",
            "650b x 2.1in (Mountain - XC)",
            "650b x 2.25in (Mountain - Trail)",
            "650b x 2.35in (Mountain - All Mountain)",
            "26\" x 2.1in (Mountain - XC)",
            "26\" x 2.25in (Mountain - Trail)",
            "29\" x 2.1in (Mountain - XC)",
            "29\" x 2.25in (Mountain - Trail)",
            "29\" x 2.35in (Mountain - All Mountain)"
        ]
    }


def create_gpx_from_geojson(geojson_data: Dict[str, Any], title: str = "Bikepacking Route") -> str:
    """Convert GeoJSON route data to GPX format"""
    try:
        if not geojson_data or 'features' not in geojson_data:
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="DirtGenie">
  <trk>
    <name>{title}</name>
    <trkseg>
      <!-- No route data available -->
    </trkseg>
  </trk>
</gpx>"""

        # Extract coordinates from the first LineString feature
        coordinates = []
        for feature in geojson_data['features']:
            if feature['geometry']['type'] == 'LineString':
                coordinates.extend(feature['geometry']['coordinates'])
                break

        if not coordinates:
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="DirtGenie">
  <trk>
    <name>{title}</name>
    <trkseg>
      <!-- No coordinate data available -->
    </trkseg>
  </trk>
</gpx>"""

        # Create GPX content
        gpx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="DirtGenie" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>{title}</name>
    <desc>Bikepacking route generated by DirtGenie</desc>
    <time>{datetime.now().isoformat()}</time>
  </metadata>
  <trk>
    <name>{title}</name>
    <type>cycling</type>
    <trkseg>
"""

        # Add track points
        for coord in coordinates:
            lon, lat = coord[0], coord[1]
            gpx_content += f'      <trkpt lat="{lat}" lon="{lon}"></trkpt>\n'

        gpx_content += """    </trkseg>
  </trk>
</gpx>"""

        return gpx_content

    except Exception as e:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="DirtGenie">
  <trk>
    <name>{title}</name>
    <trkseg>
      <!-- Error creating GPX: {str(e)} -->
    </trkseg>
  </trk>
</gpx>"""


@app.post("/api/download-trip-package")
async def download_trip_package(request: DownloadRequest):
    """Generate and download a zip package with GeoJSON, GPX, and Markdown files"""
    try:
        # Create in-memory zip file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add GeoJSON file
            if request.geojson:
                geojson_content = json.dumps(request.geojson, indent=2)
                zip_file.writestr("route.geojson", geojson_content)
            
            # Add GPX file
            if request.geojson:
                route_name = f"{request.start_location} to {request.end_location}" if request.start_location and request.end_location else "Bikepacking Route"
                gpx_content = create_gpx_from_geojson(request.geojson, route_name)
                zip_file.writestr("route.gpx", gpx_content)
            
            # Add Markdown file (instead of PDF/HTML)
            if request.trip_plan:
                zip_file.writestr("trip_plan.md", request.trip_plan)
            
            # Add a readme file
            readme_content = f"""DirtGenie Trip Package
=====================

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Route: {request.start_location or 'Unknown'} to {request.end_location or 'Unknown'}
Total Distance: {request.total_distance:.1f} km

Files included:
- route.geojson: Route data in GeoJSON format (import into mapping apps)
- route.gpx: Route data in GPX format (import into GPS devices)
- trip_plan.md: Detailed trip plan in Markdown format

Enjoy your adventure!
"""
            zip_file.writestr("README.txt", readme_content)
        
        zip_buffer.seek(0)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=trip-package-{datetime.now().strftime('%Y-%m-%d')}.zip"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating download package: {str(e)}")


@app.post("/api/export-to-notion")
async def export_to_notion(request: NotionExportRequest):
    """Create a shareable link that opens directly in Notion with the trip plan"""
    try:
        # Clean up the markdown content
        clean_content = request.trip_plan
        
        # Remove code block wrapping if present
        if clean_content.startswith('```markdown\n'):
            clean_content = clean_content.replace('```markdown\n', '').replace('\n```', '')
        elif clean_content.startswith('```\n'):
            clean_content = clean_content.replace('```\n', '').replace('\n```', '')
        elif clean_content.startswith('```'):
            clean_content = clean_content.replace('```', '').replace('\n```', '')
        
        # Escape content for safe HTML embedding
        import html
        escaped_content = html.escape(clean_content)
        safe_content = clean_content.replace('`', '\\`').replace('${', '\\${')
        
        # Create HTML content that auto-redirects to Notion
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Opening in Notion...</title>
    <meta charset="utf-8">
</head>
<body>
    <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
        <h2>🚀 Opening your trip plan in Notion...</h2>
        <p>Content copied to clipboard! If Notion doesn't open automatically, <a href="https://www.notion.so/new" target="_blank">click here to open Notion</a> and paste your content.</p>
        <div style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 8px; text-align: left; max-width: 600px; margin: 30px auto;">
            <h3>{request.page_title}</h3>
            <pre style="white-space: pre-wrap; font-size: 11px; max-height: 200px; overflow-y: auto;">{escaped_content[:800]}...</pre>
            <button onclick="copyToClipboard()" style="margin-top: 10px; padding: 8px 16px; background: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer;">Copy Again</button>
        </div>
    </div>
    
    <script>
        const content = `{safe_content}`;
        
        function copyToClipboard() {{
            navigator.clipboard.writeText(content).then(() => {{
                alert('✅ Copied to clipboard! Now paste in Notion.');
            }}).catch(() => {{
                const textArea = document.createElement('textarea');
                textArea.value = content;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('✅ Copied to clipboard! Now paste in Notion.');
            }});
        }}
        
        window.onload = function() {{
            // Auto-copy to clipboard
            navigator.clipboard.writeText(content).catch(() => {{}});
            
            // Try Notion deep links
            setTimeout(() => {{
                // Try app first
                window.location.href = 'notion://new';
                // Fallback to web
                setTimeout(() => {{
                    window.open('https://www.notion.so/new', '_blank');
                }}, 1500);
            }}, 800);
        }};
    </script>
</body>
</html>"""
        
        return {
            "success": True,
            "html_content": html_content,
            "message": "Notion export ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Notion export: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
