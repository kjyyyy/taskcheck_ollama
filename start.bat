@echo off

REM Construction TaskCheck Assistant Startup Script
REM For Windows

echo 🏗️ Starting Construction TaskCheck Assistant...

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama is not installed. Please install Ollama from https://ollama.ai/
    pause
    exit /b 1
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Start the construction assistant
echo 🚀 Starting Construction TaskCheck Assistant...
python start_construction_assistant.py

pause 