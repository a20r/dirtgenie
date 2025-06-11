import axios from 'axios';
import { TripPlanRequest, TripPlanResponse, TripRevisionRequest } from '../types/api';

// In unified mode, API calls are proxied through nginx with /api prefix
// In development mode, direct calls to backend port
const API_BASE_URL = process.env.REACT_APP_API_URL || 
    (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const dirtgenieApi = {
    // Health check
    healthCheck: () => api.get('/health'),

    // Get default profile
    getDefaultProfile: () => api.get('/api/default-profile'),

    // Plan a trip
    planTrip: (request: TripPlanRequest): Promise<TripPlanResponse> =>
        api.post('/api/plan-trip', request).then(response => response.data),

    // Revise a trip
    reviseTrip: (request: TripRevisionRequest): Promise<TripPlanResponse> =>
        api.post('/api/revise-trip', request).then(response => response.data),

    // Get tire options
    getTireOptions: () => api.get('/api/tire-options'),

    // Save profile
    saveProfile: (profileName: string, preferences: any) =>
        api.post('/api/save-profile', { profile_name: profileName, preferences }),
};

export default dirtgenieApi;
