#!/bin/bash
set -e

# DirtGenie Docker Entrypoint
# Supports running either the web app or CLI commands

case "${1}" in
    web|streamlit)
        echo "🚀 Starting DirtGenie Web App..."
        exec streamlit run src/dirtgenie/web_app.py \
            --server.port=8501 \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --browser.gatherUsageStats=false
        ;;
    cli)
        echo "🗺️ Running DirtGenie CLI..."
        shift
        exec dirtgenie "$@"
        ;;
    bash|shell)
        echo "🐚 Starting interactive shell..."
        exec /bin/bash
        ;;
    help|--help|-h)
        echo "DirtGenie Docker Container"
        echo ""
        echo "Usage: docker run [OPTIONS] dirtgenie [COMMAND] [ARGS...]"
        echo ""
        echo "Commands:"
        echo "  web, streamlit    Start the Streamlit web application (default)"
        echo "  cli [ARGS...]     Run the DirtGenie CLI with arguments"
        echo "  bash, shell       Start an interactive bash shell"
        echo "  help              Show this help message"
        echo ""
        echo "Examples:"
        echo "  # Start web app (default)"
        echo "  docker run -p 8501:8501 dirtgenie"
        echo ""
        echo "  # Run CLI command"
        echo "  docker run -v \$(pwd):/data dirtgenie cli --start 'Berlin' --end 'Prague' --days 7"
        echo ""
        echo "  # Interactive shell"
        echo "  docker run -it dirtgenie shell"
        ;;
    *)
        echo "🗺️ Running DirtGenie CLI with arguments: $@"
        exec dirtgenie "$@"
        ;;
esac
