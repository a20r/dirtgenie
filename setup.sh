#!/bin/bash

# Setup script for Bikepacking Trip Planner
# Run this script to set up your environment variables

echo "🚴‍♀️ Bikepacking Trip Planner Setup"
echo "=================================="
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "📄 Found existing .env file"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "🔑 Setting up API keys..."
echo ""

# Get OpenAI API key
echo "1. OpenAI API Key"
echo "   Get your key from: https://platform.openai.com/api-keys"
read -p "   Enter your OpenAI API key: " OPENAI_KEY

# Get Google Maps API key  
echo ""
echo "2. Google Maps API Key"
echo "   Get your key from: https://console.cloud.google.com/"
echo "   Make sure to enable Directions API and Geocoding API"
read -p "   Enter your Google Maps API key: " GOOGLE_MAPS_KEY

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=$OPENAI_KEY
GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_KEY
EOF

echo ""
echo "✅ Environment variables saved to .env file"
echo ""
echo "📝 To use the environment variables, run:"
echo "   source .env  # or"
echo "   export \$(cat .env | xargs)"
echo ""
echo "🎯 You're all set! Try running:"
echo "   python bikepacking_planner.py 'San Francisco, CA' 'Los Angeles, CA' 5"
echo ""
