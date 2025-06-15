import React, { useEffect, useState } from 'react';

interface CookingLoaderProps {
    isVisible: boolean;
}

const CookingLoader: React.FC<CookingLoaderProps> = ({ isVisible }) => {
    const [cookingPhase, setCookingPhase] = useState(0);
    const [elapsedTime, setElapsedTime] = useState(0);

    const cookingMessages = [
        { icon: '🧩', text: 'Gathering route ingredients...' },
        { icon: '🗺️', text: 'Mapping the perfect adventure...' },
        { icon: '🏔️', text: 'Finding scenic waypoints...' },
        { icon: '🏕️', text: 'Locating cozy camping spots...' },
        { icon: '🚴‍♂️', text: 'Calculating bike-friendly routes...' },
        { icon: '🌟', text: 'Adding special attractions...' },
        { icon: '🍳', text: 'Seasoning with local flavor...' },
        { icon: '⚡', text: 'Optimizing for your fitness level...' },
        { icon: '🎯', text: 'Fine-tuning the perfect itinerary...' },
        { icon: '🚀', text: 'Almost ready for your adventure!' }
    ];

    useEffect(() => {
        if (!isVisible) {
            setCookingPhase(0);
            setElapsedTime(0);
            return;
        }

        const phaseInterval = setInterval(() => {
            setCookingPhase(prev => (prev + 1) % cookingMessages.length);
        }, 3000); // Change message every 3 seconds

        const timeInterval = setInterval(() => {
            setElapsedTime(prev => prev + 1);
        }, 1000); // Update timer every second

        return () => {
            clearInterval(phaseInterval);
            clearInterval(timeInterval);
        };
    }, [isVisible, cookingMessages.length]);

    if (!isVisible) return null;

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const currentMessage = cookingMessages[cookingPhase];

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md mx-4 text-center">
                {/* Cooking Animation */}
                <div className="relative mb-6">
                    <div className="text-6xl mb-4 animate-bounce">
                        {currentMessage.icon}
                    </div>

                    {/* Steam animation */}
                    <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-2">
                        <div className="flex space-x-1">
                            <div className="w-1 h-8 bg-gray-300 rounded-full animate-pulse opacity-70"></div>
                            <div className="w-1 h-6 bg-gray-300 rounded-full animate-pulse opacity-50" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-1 h-4 bg-gray-300 rounded-full animate-pulse opacity-30" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                    </div>
                </div>

                {/* Message */}
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    Cooking up your adventure...
                </h3>
                <p className="text-gray-600 mb-4">
                    {currentMessage.text}
                </p>

                {/* Progress indicator */}
                <div className="mb-4">
                    <div className="flex justify-center space-x-2 mb-2">
                        {cookingMessages.map((_, index) => (
                            <div
                                key={index}
                                className={`w-2 h-2 rounded-full transition-colors duration-300 ${index <= cookingPhase ? 'bg-blue-500' : 'bg-gray-300'
                                    }`}
                            />
                        ))}
                    </div>
                    <div className="text-sm text-gray-500">
                        Phase {cookingPhase + 1} of {cookingMessages.length}
                    </div>
                </div>

                {/* Timer */}
                <div className="text-sm text-gray-400">
                    Cooking time: {formatTime(elapsedTime)}
                </div>

                {/* Chef's hat spinning animation */}
                <div className="mt-4">
                    <div className="text-2xl animate-spin" style={{ animationDuration: '3s' }}>
                        👨‍🍳
                    </div>
                </div>

                {/* Helpful tip */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-700">
                        💡 <strong>Pro tip:</strong> Great adventures take time to plan perfectly!
                        We're considering terrain, accommodations, and local attractions.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default CookingLoader;
