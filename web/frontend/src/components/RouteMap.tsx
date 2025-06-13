import { TileLayer } from '@deck.gl/geo-layers';
import { BitmapLayer, GeoJsonLayer } from '@deck.gl/layers';
import DeckGL from '@deck.gl/react';
import React, { useMemo, useState } from 'react';

interface RouteMapProps {
    geojson: any;
    className?: string;
}

const RouteMap: React.FC<RouteMapProps> = ({ geojson, className = '' }) => {
    // Calculate bounds and center from GeoJSON data
    const { bounds, center } = useMemo(() => {
        if (!geojson || !geojson.features || geojson.features.length === 0) {
            // Default to Massachusetts area
            return {
                bounds: [[-72.0, 41.5], [-70.0, 43.0]],
                center: [-71.0, 42.25]
            };
        }

        let minLng = Infinity, maxLng = -Infinity;
        let minLat = Infinity, maxLat = -Infinity;

        geojson.features.forEach((feature: any) => {
            if (feature.geometry.type === 'LineString') {
                feature.geometry.coordinates.forEach((coord: [number, number]) => {
                    const [lng, lat] = coord;
                    minLng = Math.min(minLng, lng);
                    maxLng = Math.max(maxLng, lng);
                    minLat = Math.min(minLat, lat);
                    maxLat = Math.max(maxLat, lat);
                });
            } else if (feature.geometry.type === 'Point') {
                const [lng, lat] = feature.geometry.coordinates;
                minLng = Math.min(minLng, lng);
                maxLng = Math.max(maxLng, lng);
                minLat = Math.min(minLat, lat);
                maxLat = Math.max(maxLat, lat);
            }
        });

        // Add padding
        const lngPadding = (maxLng - minLng) * 0.1;
        const latPadding = (maxLat - minLat) * 0.1;

        return {
            bounds: [
                [minLng - lngPadding, minLat - latPadding],
                [maxLng + lngPadding, maxLat + latPadding]
            ],
            center: [(minLng + maxLng) / 2, (minLat + maxLat) / 2]
        };
    }, [geojson]);

    const [viewState, setViewState] = useState({
        longitude: center[0],
        latitude: center[1],
        zoom: 10,
        pitch: 0,
        bearing: 0
    });

    // Create layers from GeoJSON data
    const layers = useMemo(() => {
        const baseLayers = [
            new TileLayer({
                id: 'base-map',
                data: 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 19,
                tileSize: 256,
                renderSubLayers: (props: any) => {
                    const {
                        bbox: { west, south, east, north }
                    } = props.tile;
                    return new BitmapLayer({
                        ...props,
                        data: null,
                        image: props.data,
                        bounds: [west, south, east, north]
                    });
                }
            })
        ];

        if (!geojson || !geojson.features) return baseLayers;

        return [
            ...baseLayers,
            new GeoJsonLayer({
                id: 'route-layer',
                data: geojson,
                pickable: true,
                stroked: true,
                filled: true,
                extruded: false,
                pointType: 'circle',
                lineWidthScale: 1,
                lineWidthMinPixels: 4,
                pointRadiusMinPixels: 10,
                getLineColor: (d: any) => {
                    // Color code by feature type or properties
                    if (d.properties?.type === 'start') return [34, 197, 94]; // Green for start
                    if (d.properties?.type === 'end') return [239, 68, 68]; // Red for end
                    if (d.properties?.type === 'waypoint') return [59, 130, 246]; // Blue for waypoints
                    return [168, 85, 247]; // Purple for route lines
                },
                getFillColor: (d: any) => {
                    if (d.properties?.type === 'start') return [34, 197, 94, 200];
                    if (d.properties?.type === 'end') return [239, 68, 68, 200];
                    if (d.properties?.type === 'waypoint') return [59, 130, 246, 200];
                    return [168, 85, 247, 50];
                },
                getPointRadius: 15,
                getLineWidth: 6,
                onHover: ({ object, x, y }: any) => {
                    // You can add tooltip functionality here
                },
                updateTriggers: {
                    getLineColor: geojson,
                    getFillColor: geojson
                }
            })
        ];
    }, [geojson]);

    if (!geojson || !geojson.features || geojson.features.length === 0) {
        return (
            <div className={`bg-gray-100 rounded-lg h-96 flex items-center justify-center ${className}`}>
                <div className="text-center text-gray-600">
                    <div className="text-4xl mb-2">🗺️</div>
                    <div className="font-medium">No Route Data</div>
                    <div className="text-sm">Plan a trip to see the route on the map</div>
                </div>
            </div>
        );
    }

    return (
        <div className={`relative rounded-lg overflow-hidden ${className}`} style={{ height: '400px' }}>
            <DeckGL
                viewState={viewState}
                onViewStateChange={({ viewState }: any) => setViewState(viewState)}
                controller={true}
                layers={layers}
                getCursor={() => 'pointer'}
                style={{ position: 'relative', width: '100%', height: '100%' }}
            />

            {/* Map controls overlay */}
            <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3 text-xs z-10">
                <div className="font-semibold text-gray-800 mb-2">Route Legend</div>
                <div className="space-y-1">
                    <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                        <span className="text-gray-700">Start</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                        <span className="text-gray-700">End</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                        <span className="text-gray-700">Waypoint</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-3 h-1 bg-purple-500 mr-2"></div>
                        <span className="text-gray-700">Route</span>
                    </div>
                </div>
            </div>

            {/* Zoom controls */}
            <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg overflow-hidden z-10">
                <button
                    onClick={() => setViewState(prev => ({ ...prev, zoom: Math.min(prev.zoom + 1, 18) }))}
                    className="block w-8 h-8 bg-white hover:bg-gray-50 border-b border-gray-200 flex items-center justify-center text-gray-700 font-bold text-sm"
                >
                    +
                </button>
                <button
                    onClick={() => setViewState(prev => ({ ...prev, zoom: Math.max(prev.zoom - 1, 3) }))}
                    className="block w-8 h-8 bg-white hover:bg-gray-50 flex items-center justify-center text-gray-700 font-bold text-sm"
                >
                    −
                </button>
            </div>

            {/* Reset view button */}
            <div className="absolute bottom-4 right-4 z-10">
                <button
                    onClick={() => setViewState({
                        longitude: center[0],
                        latitude: center[1],
                        zoom: 10,
                        pitch: 0,
                        bearing: 0
                    })}
                    className="bg-white hover:bg-gray-50 text-gray-700 px-3 py-2 rounded-lg shadow-lg text-xs font-medium"
                >
                    Reset View
                </button>
            </div>

            {/* Attribution */}
            <div className="absolute bottom-2 left-2 text-xs text-gray-500 bg-white bg-opacity-75 px-2 py-1 rounded z-10">
                Interactive Route Map • {geojson.features?.length || 0} features
            </div>
        </div>
    );
};

export default RouteMap;
