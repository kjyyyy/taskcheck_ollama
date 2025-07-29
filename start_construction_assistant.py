#!/usr/bin/env python3
"""
Construction TaskCheck Assistant Startup Script
Handles Ollama and Flask server startup for construction assistant
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('construction_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConstructionAssistantStartup:
    def __init__(self):
        """Initialize construction assistant startup"""
        self.ollama_process = None
        self.flask_process = None
        self.project_root = Path(__file__).parent
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        # Check Python packages
        required_packages = [
            'flask', 'langchain', 'faiss-cpu', 'sentence-transformers',
            'requests', 'flask-cors'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✓ {package} is installed")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"✗ {package} is missing")
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            logger.info("Install missing packages with: pip install " + " ".join(missing_packages))
            return False
        
        # Check Ollama installation
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"✓ Ollama is installed: {result.stdout.strip()}")
            else:
                logger.error("✗ Ollama is not properly installed")
                return False
        except FileNotFoundError:
            logger.error("✗ Ollama is not installed")
            logger.info("Install Ollama from: https://ollama.ai/")
            return False
        
        return True
    
    def check_ollama_connection(self):
        """Check if Ollama server is running"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                logger.info("✓ Ollama server is running")
                return True
            else:
                logger.warning("✗ Ollama server responded with error")
                return False
        except Exception as e:
            logger.warning(f"✗ Cannot connect to Ollama server: {e}")
            return False
    
    def start_ollama_server(self):
        """Start Ollama server if not running"""
        if self.check_ollama_connection():
            logger.info("Ollama server is already running")
            return True
        
        logger.info("Starting Ollama server...")
        try:
            self.ollama_process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if self.check_ollama_connection():
                    logger.info("✓ Ollama server started successfully")
                    return True
            
            logger.error("✗ Ollama server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            logger.error(f"✗ Failed to start Ollama server: {e}")
            return False
    
    def check_model_availability(self):
        """Check if required model is available"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                
                # Check for construction model or fallback to mistral
                if "mistral-construction-uk:latest" in model_names:
                    logger.info("✓ Construction model is available")
                    return True
                elif "mistral:latest" in model_names:
                    logger.info("✓ Mistral model is available (will use as fallback)")
                    return True
                else:
                    logger.warning("✗ Required model not found")
                    return False
            else:
                logger.error("✗ Cannot check model availability")
                return False
        except Exception as e:
            logger.error(f"✗ Error checking model availability: {e}")
            return False
    
    def pull_model_if_needed(self):
        """Pull the required model if not available"""
        if self.check_model_availability():
            return True
        
        logger.info("Pulling required model...")
        try:
            # Try to pull construction model first
            result = subprocess.run(
                ['ollama', 'pull', 'mistral-construction-uk:latest'],
                capture_output=True, text=True, timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("✓ Construction model pulled successfully")
                return True
            else:
                logger.warning("Construction model not found, pulling standard mistral...")
                result = subprocess.run(
                    ['ollama', 'pull', 'mistral:latest'],
                    capture_output=True, text=True, timeout=300
                )
                
                if result.returncode == 0:
                    logger.info("✓ Mistral model pulled successfully")
                    return True
                else:
                    logger.error("✗ Failed to pull model")
                    return False
                    
        except Exception as e:
            logger.error(f"✗ Error pulling model: {e}")
            return False
    
    def start_flask_app(self):
        """Start Flask application"""
        logger.info("Starting Flask application...")
        
        # Change to webapp directory
        webapp_dir = self.project_root / 'webapp'
        if not webapp_dir.exists():
            logger.error(f"✗ Webapp directory not found: {webapp_dir}")
            return False
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env['FLASK_APP'] = 'app.py'
            env['FLASK_ENV'] = 'development'
            
            # Start Flask app
            self.flask_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd=webapp_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for Flask to start
            time.sleep(3)
            
            # Check if Flask is running
            try:
                import requests
                response = requests.get("http://localhost:5000/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✓ Flask application started successfully")
                    return True
                else:
                    logger.error("✗ Flask application failed to start")
                    return False
            except Exception as e:
                logger.error(f"✗ Cannot connect to Flask app: {e}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Failed to start Flask application: {e}")
            return False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, cleaning up...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Clean up processes on shutdown"""
        logger.info("Cleaning up processes...")
        
        if self.flask_process:
            logger.info("Stopping Flask application...")
            self.flask_process.terminate()
            try:
                self.flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
        
        if self.ollama_process:
            logger.info("Stopping Ollama server...")
            self.ollama_process.terminate()
            try:
                self.ollama_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()
        
        logger.info("Cleanup completed")
    
    def run(self):
        """Main startup sequence"""
        logger.info("🏗️ Starting Construction TaskCheck Assistant...")
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("❌ Dependency check failed")
            return False
        
        # Start Ollama server
        if not self.start_ollama_server():
            logger.error("❌ Failed to start Ollama server")
            return False
        
        # Pull model if needed
        if not self.pull_model_if_needed():
            logger.error("❌ Failed to pull required model")
            return False
        
        # Start Flask application
        if not self.start_flask_app():
            logger.error("❌ Failed to start Flask application")
            return False
        
        logger.info("✅ Construction TaskCheck Assistant started successfully!")
        logger.info("🌐 Web interface available at: http://localhost:5000")
        logger.info("🔧 API endpoints available at: http://localhost:5000/health")
        logger.info("📝 Press Ctrl+C to stop the assistant")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    startup = ConstructionAssistantStartup()
    success = startup.run()
    
    if success:
        logger.info("Construction assistant started successfully")
        sys.exit(0)
    else:
        logger.error("Failed to start construction assistant")
        sys.exit(1)

if __name__ == "__main__":
    main() 