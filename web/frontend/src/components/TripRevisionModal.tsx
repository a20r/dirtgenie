import React, { useState } from 'react';
import dirtgenieApi from '../services/api';

interface TripRevisionModalProps {
    isOpen: boolean;
    onClose: () => void;
    tripResponse: any;
    tripRequest: any;
    onRevisionComplete: (newResponse: any) => void;
}

const TripRevisionModal: React.FC<TripRevisionModalProps> = ({
    isOpen,
    onClose,
    tripResponse,
    tripRequest,
    onRevisionComplete
}) => {
    const [feedback, setFeedback] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!feedback.trim()) {
            alert('Please provide feedback for your revision');
            return;
        }

        setIsSubmitting(true);

        try {
            const revisionRequest = {
                original_plan: tripResponse.trip_plan,
                feedback: feedback,
                trip_request: tripRequest
            };

            const response = await dirtgenieApi.reviseTrip(revisionRequest);
            onRevisionComplete(response);
            onClose();
            setFeedback('');
        } catch (error) {
            console.error('Error revising trip:', error);
            alert('Error revising trip. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-bold text-gray-900">✏️ Revise Your Trip Plan</h2>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 text-2xl"
                        >
                            ×
                        </button>
                    </div>

                    <div className="mb-6">
                        <p className="text-gray-700 mb-4">
                            What would you like to change about your trip plan? Be specific about:
                        </p>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                            <li>Accommodation preferences or specific places to stay</li>
                            <li>Route modifications or alternative paths</li>
                            <li>Activities or points of interest to add/remove</li>
                            <li>Budget adjustments or dining preferences</li>
                            <li>Daily distance or pacing changes</li>
                        </ul>
                    </div>

                    <form onSubmit={handleSubmit}>
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Your Feedback
                            </label>
                            <textarea
                                value={feedback}
                                onChange={(e) => setFeedback(e.target.value)}
                                rows={6}
                                placeholder="Example: I'd like to add more camping options instead of hotels, and I'm interested in visiting local breweries along the route..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        <div className="flex gap-3">
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition duration-200"
                            >
                                {isSubmitting ? '🔄 Revising Plan...' : '✨ Apply Revisions'}
                            </button>

                            <button
                                type="button"
                                onClick={onClose}
                                className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition duration-200"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default TripRevisionModal;
