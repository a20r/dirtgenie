import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import RouteMap from './RouteMap';

interface TripResultsProps {
    response: any;
    onReviseClick: () => void;
}

const TripResults: React.FC<TripResultsProps> = ({ response, onReviseClick }) => {
    if (!response || !response.success) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-red-800 mb-2">❌ Planning Failed</h3>
                <p className="text-red-700">{response?.error || 'An error occurred while planning your trip.'}</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Trip Summary */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-800 mb-4">🎉 Your Adventure is Planned!</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white rounded-lg p-4">
                        <div className="text-sm text-gray-600">Total Distance</div>
                        <div className="text-2xl font-bold text-green-700">
                            {response.total_distance ? `${response.total_distance.toFixed(1)} km` : 'N/A'}
                        </div>
                    </div>

                    <div className="bg-white rounded-lg p-4">
                        <div className="text-sm text-gray-600">Trip Status</div>
                        <div className="text-2xl font-bold text-green-700">Ready to Go!</div>
                    </div>
                </div>

                <div className="mt-4 flex gap-3">
                    <button
                        onClick={onReviseClick}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200"
                    >
                        ✏️ Revise Plan
                    </button>

                    <button
                        onClick={() => window.print()}
                        className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition duration-200"
                    >
                        🖨️ Print Plan
                    </button>
                </div>
            </div>

            {/* Trip Plan */}
            {response.trip_plan && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">📋 Detailed Trip Plan</h3>
                    <div className="prose prose-slate max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {(() => {
                                // Clean up the markdown content - remove any code block wrapping
                                let content = response.trip_plan;
                                
                                // Remove markdown code block wrapping if present
                                if (content.startsWith('```markdown\n')) {
                                    content = content.replace(/^```markdown\n/, '').replace(/\n```$/, '');
                                } else if (content.startsWith('```\n')) {
                                    content = content.replace(/^```\n/, '').replace(/\n```$/, '');
                                } else if (content.startsWith('```')) {
                                    content = content.replace(/^```[a-zA-Z]*\n/, '').replace(/\n```$/, '');
                                }
                                
                                // Fix the italic text at the end that might be in a code block
                                content = content.replace(/```\n\*\((.*?)\)\*\n```/g, '*($1)*');
                                
                                return content;
                            })()}
                        </ReactMarkdown>
                    </div>
                </div>
            )}

            {/* Interactive Route Map */}
            {response.geojson && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🗺️ Route Map</h3>
                    <RouteMap geojson={response.geojson} />
                </div>
            )}
        </div>
    );
};

export default TripResults;
