#!/bin/bash
# DirtGenie Quick Start Script

set -e

echo "🚴‍♀️ DirtGenie - AI-Powered Bikepacking Trip Planner"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "� Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Install in development mode
echo "⚙️ Installing DirtGenie package..."
pip install -e . > /dev/null 2>&1

echo ""
echo "✅ Setup complete!"
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "📄 Found existing .env file with API keys"
    echo "🚀 Choose how to run DirtGenie:"
    echo "   1) Web App (Recommended): streamlit run src/dirtgenie/web_app.py"
    echo "   2) CLI Tool: ./scripts/dirtgenie 'Start Location' 'End Location' nights"
    echo ""
else
    echo "🔑 API keys not found. Let's set them up..."
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
    read -p "   Enter your Google Maps API key: " GOOGLE_KEY

    # Create .env file
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << EOF
OPENAI_API_KEY=$OPENAI_KEY
GOOGLE_MAPS_API_KEY=$GOOGLE_KEY
EOF

    echo "✅ API keys saved to .env file"
    echo ""
    echo "🚀 Choose how to run DirtGenie:"
    echo "   1) Web App (Recommended): streamlit run src/dirtgenie/web_app.py"
    echo "   2) CLI Tool: ./scripts/dirtgenie 'Start Location' 'End Location' nights"
    echo ""
fi

# Ask user what they want to do
read -p "🤖 Start the web app now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Starting web app..."
    streamlit run src/dirtgenie/web_app.py
fi
