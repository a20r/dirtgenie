#!/bin/bash
set -e

echo "🔨 Building DirtGenie Unified Docker Container..."
echo "Building from parent directory to access both src/ and web/ directories"

# Build the unified container
docker build -f Dockerfile.unified -t dirtgenie-unified .

echo "✅ Build complete!"
echo ""
echo "🚀 To run the unified container:"
echo "docker run -p 80:80 --env-file .env dirtgenie-unified"
echo ""
echo "Or with docker-compose:"
echo "docker compose -f docker-compose.unified.yml up"
echo ""
echo "Or with environment variables:"
echo "docker run -p 80:80 \\"
echo "  -e OPENAI_API_KEY=your_key \\"
echo "  -e GOOGLE_MAPS_API_KEY=your_key \\"
echo "  dirtgenie-unified"
echo ""
echo "Then visit: http://localhost"
