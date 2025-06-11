export interface TripPreferences {
    accommodation: string;
    stealth_camping: boolean;
    fitness_level: string;
    daily_distance: string;
    terrain: string;
    tire_size: string;
    budget: string;
    interests: string[];
}

export interface TripPlanRequest {
    start_location: string;
    end_location: string;
    nights: number;
    departure_date?: string;
    preferences: TripPreferences;
}

export interface TripPlanResponse {
    success: boolean;
    trip_plan?: string;
    itinerary?: any;
    geojson?: any;
    total_distance?: number;
    error?: string;
}

export interface TripRevisionRequest {
    original_plan: string;
    feedback: string;
    trip_request: TripPlanRequest;
}
