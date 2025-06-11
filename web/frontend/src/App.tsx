import { useState } from 'react';
import './App.css';
import TripPlannerForm from './components/TripPlannerForm';
import TripResults from './components/TripResults';
import TripRevisionModal from './components/TripRevisionModal';
import { TripPlanRequest } from './types/api';

function App() {
    const [tripResponse, setTripResponse] = useState<any>(null);
    const [tripRequest, setTripRequest] = useState<TripPlanRequest | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isRevisionModalOpen, setIsRevisionModalOpen] = useState(false);

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
