import React, { KeyboardEvent, useEffect, useState } from 'react';
import dirtgenieApi from '../services/api';
import { TripPlanRequest } from '../types/api';
import CookingLoader from './CookingLoader';


interface TripPlannerFormProps {
    onPlanGenerated: (response: any, request: TripPlanRequest) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
}

const TripPlannerForm: React.FC<TripPlannerFormProps> = ({
    onPlanGenerated,
    isLoading,
    setIsLoading
}) => {
    const [formData, setFormData] = useState<TripPlanRequest>({
        start_location: '',
        end_location: '',
        nights: 3,
        departure_date: '',
        desires: [], // Initialize desires as an empty array
        preferences: {
            accommodation: 'mixed',
            stealth_camping: false,
            fitness_level: 'intermediate',
            daily_distance: '50-80',
            terrain: 'mixed',
            tire_size: '700x35c (Gravel - Standard)',
            budget: 'moderate',
            interests: []
        }
    });

    const [tireOptions, setTireOptions] = useState<string[]>([]);
    const [desireInput, setDesireInput] = useState('');
    const [desires, setDesires] = useState<string[]>([]);
    const [customTireSize, setCustomTireSize] = useState('');

    useEffect(() => {
        // Load tire options
        dirtgenieApi.getTireOptions()
            .then(response => setTireOptions(response.data.tire_options))
            .catch(console.error);
    }, []);

    useEffect(() => {
        // Check for debug URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const debugParam = urlParams.get('debug');

        if (debugParam === 'true') {
            // Pre-fill form with debug data
            const debugFormData: TripPlanRequest = {
                start_location: "11 pearson ave somerville ma",
                end_location: "62 carriage house rd warren vt",
                nights: 5,
                departure_date: "2025-07-18",
                desires: [
                    "nature",
                    "by the water",
                    "mountains",
                    "rivers",
                    "farms",
                    "breweries"
                ],
                preferences: {
                    accommodation: "camping",
                    stealth_camping: true,
                    fitness_level: "advanced",
                    daily_distance: "50-80",
                    terrain: "gravel",
                    tire_size: "Other/Custom",
                    budget: "budget",
                    interests: []
                }
            };

            setFormData(debugFormData);
            setDesires(debugFormData.desires);
            setCustomTireSize("700x40c (Custom Gravel)"); // Set a custom tire size for debug
        }
    }, []);

    const handleInputChange = (field: string, value: any) => {
        if (field.startsWith('preferences.')) {
            const prefField = field.replace('preferences.', '');
            setFormData(prev => ({
                ...prev,
                preferences: {
                    ...prev.preferences,
                    [prefField]: value
                }
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [field]: value
            }));
        }
    };

    const handleDesireKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Tab' && desireInput.trim()) {
            e.preventDefault();
            setDesires(prev => [...prev, desireInput.trim()]);
            setDesireInput('');
        }
    };
    const handleSubmit = async (e: React.FormEvent) => {
        formData.desires = desires; // Add desires to formData
        e.preventDefault();

        if (!formData.start_location || !formData.end_location) {
            alert('Please enter both start and end locations');
            return;
        }

        setIsLoading(true);

        try {
            const response = await dirtgenieApi.planTrip(formData);
            onPlanGenerated(response, formData);
        } catch (error) {
            console.error('Error planning trip:', error);
            alert('Error planning trip. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const getTireCapabilityInfo = (tireSize: string) => {
        if (tireSize.includes('23') || tireSize.includes('25') || tireSize.includes('28')) {
            return { type: 'Road bike setup', icon: '🏁', desc: 'Best for paved roads and smooth surfaces' };
        } else if (tireSize.includes('32') || tireSize.includes('35') || tireSize.includes('40') || tireSize.includes('650b x 47')) {
            return { type: 'Gravel bike setup', icon: '🛤️', desc: 'Great for mixed terrain, gravel roads, and light trails' };
        } else if (tireSize.includes('2.1') || tireSize.includes('2.25') || tireSize.includes('2.35') || tireSize.includes('2.8')) {
            return { type: 'Mountain bike setup', icon: '🏔️', desc: 'Perfect for trails, singletrack, and challenging terrain' };
        }
        return { type: 'Custom setup', icon: '🚴', desc: 'Route recommendations will be customized to your tire size' };
    };

    const currentTireSize = formData.preferences.tire_size === 'Other/Custom' ? customTireSize : formData.preferences.tire_size;
    const tireInfo = getTireCapabilityInfo(currentTireSize);

    return (
        <>
            <CookingLoader isVisible={isLoading} />
            <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">🚴‍♂️ Plan Your Bikepacking Adventure</h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Trip Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                📍 Start Location
                            </label>
                            <input
                                type="text"
                                value={formData.start_location}
                                onChange={(e) => handleInputChange('start_location', e.target.value)}
                                placeholder="e.g., San Francisco, CA"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                🏁 End Location
                            </label>
                            <input
                                type="text"
                                value={formData.end_location}
                                onChange={(e) => handleInputChange('end_location', e.target.value)}
                                placeholder="e.g., Portland, OR"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                🌙 Number of Nights
                            </label>
                            <input
                                type="number"
                                value={formData.nights}
                                onChange={(e) => handleInputChange('nights', parseInt(e.target.value))}
                                min="1"
                                max="30"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                📅 Departure Date (Optional)
                            </label>
                            <input
                                type="date"
                                value={formData.departure_date}
                                onChange={(e) => handleInputChange('departure_date', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                    </div>

                    {/* Preferences */}
                    <div className="border-t pt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Trip Preferences</h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    🏨 Accommodation Style
                                </label>
                                <select
                                    value={formData.preferences.accommodation}
                                    onChange={(e) => handleInputChange('preferences.accommodation', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="camping">Camping only</option>
                                    <option value="mixed">Mixed (camping + hotels)</option>
                                    <option value="hotels">Hotels/B&Bs only</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    💪 Fitness Level
                                </label>
                                <select
                                    value={formData.preferences.fitness_level}
                                    onChange={(e) => handleInputChange('preferences.fitness_level', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="beginner">Beginner</option>
                                    <option value="intermediate">Intermediate</option>
                                    <option value="advanced">Advanced</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    🗻 Terrain Preference
                                </label>
                                <select
                                    value={formData.preferences.terrain}
                                    onChange={(e) => handleInputChange('preferences.terrain', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="road">Paved roads</option>
                                    <option value="gravel">Gravel roads</option>
                                    <option value="mountain">Mountain trails</option>
                                    <option value="mixed">Mixed terrain</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    📏 Daily Distance
                                </label>
                                <select
                                    value={formData.preferences.daily_distance}
                                    onChange={(e) => handleInputChange('preferences.daily_distance', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="30-50">30-50 km/day (Easy)</option>
                                    <option value="50-80">50-80 km/day (Moderate)</option>
                                    <option value="80-120">80-120 km/day (Challenging)</option>
                                    <option value="120+">120+ km/day (Expert)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Bike Setup */}
                    <div className="border-t pt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚴 Bike Setup</h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    🛞 Tire Size
                                </label>
                                <select
                                    value={formData.preferences.tire_size}
                                    onChange={(e) => handleInputChange('preferences.tire_size', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    {tireOptions.map(option => (
                                        <option key={option} value={option}>{option}</option>
                                    ))}
                                    <option value="Other/Custom">Other/Custom</option>
                                </select>

                                {formData.preferences.tire_size === 'Other/Custom' && (
                                    <input
                                        type="text"
                                        value={customTireSize}
                                        onChange={(e) => setCustomTireSize(e.target.value)}
                                        placeholder="e.g., 650b x 2.8in"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mt-2"
                                    />
                                )}
                            </div>

                            <div className="flex items-center">
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <div className="flex items-center">
                                        <span className="text-2xl mr-2">{tireInfo.icon}</span>
                                        <div>
                                            <div className="font-medium text-blue-900">{tireInfo.type}</div>
                                            <div className="text-sm text-blue-700">{tireInfo.desc}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>


                    <div className="border-t pt-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    💰 Budget
                                </label>
                                <select
                                    value={formData.preferences.budget}
                                    onChange={(e) => handleInputChange('preferences.budget', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="budget">Budget ($30-60/day)</option>
                                    <option value="moderate">Moderate ($60-120/day)</option>
                                    <option value="luxury">Luxury ($120+/day)</option>
                                </select>
                            </div>

                            <div className="flex items-center">
                                <label className="flex items-center">
                                    <input
                                        type="checkbox"
                                        checked={formData.preferences.stealth_camping}
                                        onChange={(e) => handleInputChange('preferences.stealth_camping', e.target.checked)}
                                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className="ml-2 text-sm text-gray-700">🏕️ Allow stealth camping</span>
                                </label>
                            </div>
                        </div>
                    </div>

                    {/* Desires Input */}
                    <div className="border-t pt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Your Desires</h3>
                        <div className="flex flex-wrap gap-2 mb-4">
                            {desires.map((desire, index) => (
                                <span key={index} className="bg-blue-100 text-blue-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded">
                                    {desire}
                                </span>
                            ))}
                        </div>
                        <input
                            type="text"
                            value={desireInput}
                            onChange={(e) => setDesireInput(e.target.value)}
                            onKeyDown={handleDesireKeyDown}
                            placeholder="Type your desire and press TAB"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div className="border-t pt-6">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className={`w-full font-bold py-3 px-4 rounded-lg transition duration-200 ${isLoading
                                ? 'bg-yellow-500 text-white cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700 text-white'
                                }`}
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center">
                                    <span className="animate-spin mr-2">🍳</span>
                                    Cooking up your adventure...
                                </span>
                            ) : (
                                '🗺️ Plan My Trip'
                            )}
                        </button>

                        {isLoading && (
                            <p className="text-center text-sm text-gray-600 mt-2">
                                ⏰ This can take up to 3 minutes - we're crafting the perfect trip for you!
                            </p>
                        )}
                    </div>
                </form>
            </div>
        </>
    );
};

export default TripPlannerForm;
