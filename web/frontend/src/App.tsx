import { useEffect, useState } from 'react';
import './App.css';
import ApiKeySetup from './components/ApiKeySetup';
import TripPlannerForm from './components/TripPlannerForm';
import TripResults from './components/TripResults';
import TripRevisionModal from './components/TripRevisionModal';
import { TripPlanRequest } from './types/api';

function App() {
    const [tripResponse, setTripResponse] = useState<any>(null);
    const [tripRequest, setTripRequest] = useState<TripPlanRequest | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isRevisionModalOpen, setIsRevisionModalOpen] = useState(false);
    const [apiKeysSet, setApiKeysSet] = useState(false);
    const [isCheckingKeys, setIsCheckingKeys] = useState(true);

    useEffect(() => {
        // Check if we're in development (localhost) or if API keys are set in environment
        const checkApiKeys = async () => {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    // If health check passes, check if we're in development mode or if keys are already configured
                    const isDevelopment = window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1';

                    if (isDevelopment) {
                        // In development, assume keys are set in environment
                        setApiKeysSet(true);
                    } else {
                        // In production, check if keys are in session storage
                        const hasSessionKeys = sessionStorage.getItem('openai_api_key') &&
                            sessionStorage.getItem('google_maps_api_key');
                        setApiKeysSet(!!hasSessionKeys);
                    }
                }
            } catch (error) {
                console.error('Error checking API keys:', error);
                // If we can't reach the backend, assume we need to set keys
                setApiKeysSet(false);
            } finally {
                setIsCheckingKeys(false);
            }
        };

        checkApiKeys();
    }, []);

    const handleApiKeysSet = (keys: { openaiKey: string; googleMapsKey: string }) => {
        setApiKeysSet(true);
    };

    const handlePlanGenerated = (response: any, request: TripPlanRequest) => {
        setTripResponse(response);
        setTripRequest(request);
    };

    const handleRevisionComplete = (newResponse: any) => {
        setTripResponse(newResponse);
    };

    const handleStartOver = () => {
        setTripResponse(null);
        setTripRequest(null);
    };

    // Show loading while checking API keys
    if (isCheckingKeys) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Checking configuration...</p>
                </div>
            </div>
        );
    }

    // Show API key setup if keys are not configured
    if (!apiKeysSet) {
        return <ApiKeySetup onApiKeysSet={handleApiKeysSet} />;
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <div className="flex items-center">
                            <h1 className="text-3xl font-bold text-gray-900">
                                🌲 DirtGenie
                            </h1>
                            <span className="ml-3 text-lg text-gray-600">
                                AI-Powered Bikepacking Planner
                            </span>
                        </div>

                        <div className="flex items-center gap-3">
                            {/* API Key indicator for production */}
                            {window.location.hostname !== 'localhost' && (
                                <div className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                                    🔑 API Keys Active
                                </div>
                            )}

                            {tripResponse && (
                                <button
                                    onClick={handleStartOver}
                                    className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition duration-200"
                                >
                                    🔄 Plan New Trip
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {!tripResponse ? (
                    /* Trip Planning Form */
                    <div className="max-w-4xl mx-auto">
                        <TripPlannerForm
                            onPlanGenerated={handlePlanGenerated}
                            isLoading={isLoading}
                            setIsLoading={setIsLoading}
                        />
                    </div>
                ) : (
                    /* Trip Results */
                    <div className="max-w-6xl mx-auto">
                        <TripResults
                            response={tripResponse}
                            onReviseClick={() => setIsRevisionModalOpen(true)}
                        />
                    </div>
                )}
            </main>

            {/* Revision Modal */}
            {tripRequest && (
                <TripRevisionModal
                    isOpen={isRevisionModalOpen}
                    onClose={() => setIsRevisionModalOpen(false)}
                    tripResponse={tripResponse}
                    tripRequest={tripRequest}
                    onRevisionComplete={handleRevisionComplete}
                />
            )}

            {/* Footer */}
            <footer className="bg-white border-t mt-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="text-center text-gray-600">
                        <p className="mb-2">
                            Powered by OpenAI and Google Maps • Built with React and FastAPI
                        </p>
                        <p className="text-sm">
                            Plan responsibly and always check local conditions before departing
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default App;
