import React, { useState } from 'react';

interface ApiKeySetupProps {
    onApiKeysSet: (keys: { openaiKey: string; googleMapsKey: string }) => void;
}

const ApiKeySetup: React.FC<ApiKeySetupProps> = ({ onApiKeysSet }) => {
    const [openaiKey, setOpenaiKey] = useState('');
    const [googleMapsKey, setGoogleMapsKey] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!openaiKey.trim() || !googleMapsKey.trim()) {
            alert('Please enter both API keys');
            return;
        }

        setIsSubmitting(true);

        try {
            // Store API keys temporarily in sessionStorage (not localStorage for security)
            sessionStorage.setItem('openai_api_key', openaiKey.trim());
            sessionStorage.setItem('google_maps_api_key', googleMapsKey.trim());

            // Test the API keys by making a test call
            const testResponse = await fetch('/api/test-keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    openai_key: openaiKey.trim(),
                    google_maps_key: googleMapsKey.trim()
                })
            });

            if (testResponse.ok) {
                onApiKeysSet({ openaiKey: openaiKey.trim(), googleMapsKey: googleMapsKey.trim() });
            } else {
                const error = await testResponse.json();
                alert(`API key validation failed: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error validating API keys:', error);
            alert('Failed to validate API keys. Please check your connection and try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
                <div className="text-center mb-6">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">🌲 DirtGenie</h1>
                    <p className="text-gray-600">AI-Powered Bikepacking Planner</p>
                </div>

                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h3 className="text-lg font-semibold text-blue-800 mb-2">🔑 API Keys Required</h3>
                    <p className="text-sm text-blue-700 mb-3">
                        To use DirtGenie, you need to provide your own API keys. This ensures you have full control over usage and costs.
                    </p>
                    <ul className="text-sm text-blue-700 space-y-1">
                        <li>• OpenAI API key for trip planning</li>
                        <li>• Google Maps API key for routing</li>
                    </ul>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            🤖 OpenAI API Key
                        </label>
                        <input
                            type="password"
                            value={openaiKey}
                            onChange={(e) => setOpenaiKey(e.target.value)}
                            placeholder="sk-..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Get your key at <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">platform.openai.com/api-keys</a>
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            🗺️ Google Maps API Key
                        </label>
                        <input
                            type="password"
                            value={googleMapsKey}
                            onChange={(e) => setGoogleMapsKey(e.target.value)}
                            placeholder="AIza..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Get your key at <a href="https://developers.google.com/maps/documentation/javascript/get-api-key" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Cloud Console</a>
                        </p>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <p className="text-xs text-yellow-800">
                            🔒 <strong>Security Note:</strong> Your API keys are stored temporarily in your browser session and are never saved permanently or shared.
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-2 px-4 rounded-lg transition duration-200"
                    >
                        {isSubmitting ? '🔍 Validating Keys...' : '🚀 Start Planning'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ApiKeySetup;
