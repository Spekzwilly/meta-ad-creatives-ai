#!/bin/bash

# Meta Ad Creatives AI - Run Script
echo "🚀 Starting Meta Ad Creatives AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from template..."
    cp .env.example .env
    echo "✏️  Please edit .env file and add your Gemini API key"
fi

# Run Streamlit app
echo "🚀 Launching Streamlit application..."
streamlit run app.py

echo "✅ Application started! Open your browser to http://localhost:8501"
