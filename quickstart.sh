#!/bin/bash
# Quick Start Script for BaseModel Agent (Linux/macOS)

echo "============================================================"
echo "BaseModel Agent - Quick Start"
echo "============================================================"
echo ""

# Check if Docker is running
echo "Checking Docker..."
if docker ps &> /dev/null; then
    echo "  ✓ Docker is running"
    
    # Check for Restack container
    echo ""
    echo "Checking Restack container..."
    if docker ps --filter "name=restack" --format "{{.Names}}" | grep -q "restack"; then
        echo "  ✓ Restack container is running"
    else
        echo "  ⚠ Restack container not found"
        echo "  Starting Restack container..."
        docker run -d --pull always --name restack -p 5233:5233 -p 6233:6233 ghcr.io/restackio/restack:main
        echo "  ✓ Restack container started!"
        sleep 3
    fi
else
    echo "  ✗ Docker is not running or not installed"
    echo "  Please install Docker and start it"
fi

# Check for .env file
echo ""
echo "Checking environment file..."
if [ -f ".env" ]; then
    echo "  ✓ .env file exists"
else
    echo "  ⚠ .env file not found, creating from .env.example..."
    cp .env.example .env
    echo "  ✓ .env file created!"
fi

# Check for virtual environment
echo ""
echo "Checking Python environment..."
if [ -d ".venv" ]; then
    echo "  ✓ Virtual environment exists"
else
    echo "  ⚠ Creating virtual environment..."
    python3 -m venv .venv
    echo "  ✓ Virtual environment created!"
fi

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
echo "       source .venv/bin/activate"
echo ""
echo "  2. Install dependencies:"
echo "       pip install -e ."
echo ""
echo "  3. Open TWO terminal windows:"
echo ""
echo "     Terminal 1 (Service):"
echo "       python src/service.py"
echo ""
echo "     Terminal 2 (Schedule Agent):"
echo "       python src/schedule.py"
echo ""
echo "  4. View UI in browser:"
echo "       http://localhost:5233"
echo ""
echo "Tip: Run 'python dev_check.py' to verify everything is set up correctly"
echo ""
