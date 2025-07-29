#!/bin/bash

# Construction TaskCheck Assistant Startup Script
# For Linux and macOS

echo "🏗️ Starting Construction TaskCheck Assistant..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama from https://ollama.ai/"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Start the construction assistant
echo "🚀 Starting Construction TaskCheck Assistant..."
python3 start_construction_assistant.py 