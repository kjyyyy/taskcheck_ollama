#!/bin/bash

# Construction TaskCheck Assistant Docker Start Script

echo "🏗️ Starting Construction TaskCheck Assistant in Docker..."

# Start Ollama in background
echo "🚀 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Check if Ollama is running
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama is running"
        break
    fi
    echo "⏳ Waiting for Ollama... ($i/30)"
    sleep 2
done

# Pull model if needed
echo "📦 Checking for required model..."
if ! ollama list | grep -q "mistral"; then
    echo "📥 Pulling Mistral model..."
    ollama pull mistral
fi

# Start Flask application
echo "🌐 Starting Flask application..."
cd /app
python webapp/app.py

# Cleanup
echo "🧹 Cleaning up..."
kill $OLLAMA_PID 2>/dev/null 