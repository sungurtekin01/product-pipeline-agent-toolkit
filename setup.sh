#!/bin/bash
# Setup script for Product Pipeline Toolkit

set -e  # Exit on error

echo "🚀 Setting up Product Pipeline Toolkit..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
    else
        echo "⚠️  No .env file found. Please create one with GEMINI_API_KEY"
    fi
else
    echo "✓ .env file already exists"
fi

# Check if BAML client exists
if [ ! -d "baml_client" ]; then
    echo ""
    echo "⚠️  BAML client not found!"
    echo "Please install BAML CLI and generate the client:"
    echo ""
    echo "  npm install -g @boundaryml/baml"
    echo "  baml-cli generate --from ./baml_src --to ./baml_client"
    echo ""
else
    echo "✓ BAML client found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Edit .env and add your GEMINI_API_KEY"
echo "3. Run scripts with: PYTHONPATH=. python scripts/generate_brd.py"
echo ""
