#!/usr/bin/env python3
"""
Test script for Construction TaskCheck Assistant setup
Verifies all components are working correctly
"""

import sys
import os
import requests
import json
import subprocess
import time
from pathlib import Path

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    print("🔍 Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            models = response.json().get("models", [])
            if models:
                model_names = [m['name'] for m in models]
                print(f"   Available models: {model_names}")
                
                # Check if mistral is available
                if any("mistral" in m for m in model_names):
                    print("✅ Mistral model is available")
                    return True
                else:
                    print("⚠️  Mistral model not found. Run: ollama pull mistral")
                    return False
            else:
                print("   ⚠️  No models found. Run: ollama pull mistral")
                return False
        else:
            print("❌ Ollama responded with error")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False

def test_ollama_installation():
    """Test if Ollama is installed"""
    print("🔧 Testing Ollama installation...")
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not installed or not in PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama is not installed")
        print("   Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        return False

def test_context_files():
    """Test if context files are present"""
    print("\n📁 Testing context files...")
    context_dir = Path("context")
    if not context_dir.exists():
        print("❌ Context directory not found")
        return False
    
    files = list(context_dir.glob("*.txt")) + list(context_dir.glob("*.md"))
    if files:
        print(f"✅ Found {len(files)} context files:")
        for file in files:
            print(f"   - {file.name}")
        return True
    else:
        print("⚠️  No context files found in context/ directory")
        print("   Add .txt or .md files to the context/ directory")
        return False

def test_python_dependencies():
    """Test if required Python packages are installed"""
    print("\n🐍 Testing Python dependencies...")
    required_packages = {
        "flask": "flask",
        "langchain": "langchain",
        "langchain_community": "langchain_community",
        "langchain_core": "langchain_core",
        "faiss-cpu": "faiss",
        "sentence-transformers": "sentence_transformers",
        "requests": "requests",
        "PyPDF2": "PyPDF2",
        "python-docx": "docx",
        "beautifulsoup4": "bs4",
        "pandas": "pandas",
        "schedule": "schedule"
    }

    missing_packages = []
    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {pip_name}")
        except ImportError:
            print(f"❌ {pip_name} - not installed")
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"\n   Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    return True

def test_rag_system():
    """Test the construction RAG system"""
    print("\n🧠 Testing Construction RAG system...")
    try:
        sys.path.append('scripts')
        from construction_rag_chat import ConstructionRAGChat
        
        # Test initialization
        chat = ConstructionRAGChat()
        print("✅ Construction RAG system initialized")
        
        # Check status
        status = chat.get_status()
        print(f"   Ollama available: {status['ollama_available']}")
        print(f"   Vectorstore loaded: {status['vectorstore_loaded']}")
        print(f"   QA chain available: {status['qa_chain_available']}")
        
        # Test a simple query
        response = chat.ask("What materials do I need for a residential extension?", use_context=True)
        if response and "answer" in response:
            print("✅ Construction RAG query successful")
            print(f"   Response: {response['answer'][:100]}...")
            if response.get('error'):
                print(f"   ⚠️  Warning: {response.get('error')}")
            return True
        else:
            print("❌ Construction RAG query failed")
            return False
            
    except Exception as e:
        print(f"❌ Construction RAG system test failed: {e}")
        return False

def test_task_analyzer():
    """Test the construction task analyzer"""
    print("\n🔧 Testing Construction Task Analyzer...")
    try:
        sys.path.append('scripts')
        from construction_task_analyzer import ConstructionTaskAnalyzer
        
        # Test initialization
        analyzer = ConstructionTaskAnalyzer()
        print("✅ Construction Task Analyzer initialized")
        
        # Test task analysis
        analysis = analyzer.analyze_construction_task("I need materials for a residential extension")
        if analysis:
            print("✅ Task analysis successful")
            print(f"   Task Type: {analysis.task_type}")
            print(f"   Complexity: {analysis.complexity_level.value}")
            print(f"   Timeline: {analysis.estimated_timeline}")
            print(f"   Cost Estimate: {analysis.cost_estimate}")
            return True
        else:
            print("❌ Task analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Construction Task Analyzer test failed: {e}")
        return False

def test_flask_app():
    """Test if Flask app can start"""
    print("\n🌐 Testing Flask app...")
    try:
        # Import the app
        sys.path.append('webapp')
        from app import app
        
        # Test app creation
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Flask app is working")
                return True
            else:
                print("❌ Flask health check failed")
                return False
                
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if Flask is running"""
    print("\n🔌 Testing API endpoints...")
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
            return False
        
        # Test ask endpoint with task analysis
        test_data = {
            "question": "What materials do I need for a residential extension?",
            "use_context": True,
            "analyze_task": True
        }
        response = requests.post(
            "http://localhost:5000/ask",
            json=test_data,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Ask endpoint working")
            print(f"   Response: {data.get('answer', '')[:100]}...")
            
            # Check for task analysis
            if data.get('task_analysis'):
                print("✅ Task analysis working")
                task = data['task_analysis']
                print(f"   Task Type: {task.get('task_type', 'unknown')}")
                print(f"   Complexity: {task.get('complexity_level', 'unknown')}")
                print(f"   Timeline: {task.get('estimated_timeline', 'unknown')}")
                print(f"   Cost Estimate: {task.get('cost_estimate', 'unknown')}")
            else:
                print("⚠️  Task analysis not available")
        else:
            print(f"❌ Ask endpoint failed: {response.status_code}")
            return False
        
        # Test materials endpoint
        response = requests.get("http://localhost:5000/materials", timeout=5)
        if response.status_code == 200:
            print("✅ Materials endpoint working")
            materials = response.json()
            print(f"   Available materials: {len(materials.get('materials', []))}")
        else:
            print("❌ Materials endpoint failed")
            return False
        
        # Test tasks endpoint
        response = requests.get("http://localhost:5000/tasks", timeout=5)
        if response.status_code == 200:
            print("✅ Tasks endpoint working")
            tasks = response.json()
            print(f"   Available tasks: {len(tasks.get('task_types', []))}")
        else:
            print("❌ Tasks endpoint failed")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
        print("   Make sure Flask app is running: python webapp/app.py")
        return False

def start_ollama_if_needed():
    """Start Ollama if it's not running"""
    print("\n🚀 Checking if Ollama needs to be started...")
    
    # Check if Ollama is already running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama is already running")
            return True
    except:
        pass
    
    # Try to start Ollama
    print("   Starting Ollama...")
    try:
        # Start Ollama in background
        process = subprocess.Popen(["ollama", "serve"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        
        # Wait a bit for it to start
        time.sleep(3)
        
        # Check if it's running now
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama started successfully")
                return True
            else:
                print("❌ Ollama failed to start properly")
                return False
        except:
            print("❌ Ollama failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        return False

def main():
    """Run all tests"""
    print("🏗️ Construction TaskCheck Assistant Setup Test")
    print("=" * 50)
    
    # First check if Ollama is installed
    ollama_installed = test_ollama_installation()
    
    # Try to start Ollama if needed
    if ollama_installed:
        start_ollama_if_needed()
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Context Files", test_context_files),
        ("Python Dependencies", test_python_dependencies),
        ("Construction RAG System", test_rag_system),
        ("Construction Task Analyzer", test_task_analyzer),
        ("Flask App", test_flask_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your construction assistant is ready to use.")
        print("\nNext steps:")
        print("1. Start the Flask app: python webapp/app.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Start asking construction questions!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before proceeding.")
        
        # Provide specific guidance based on failures
        ollama_failed = not any(name == "Ollama Connection" and result for name, result in results)
        rag_failed = not any(name == "Construction RAG System" and result for name, result in results)
        
        if ollama_failed:
            print("\n💡 Ollama Issues - Quick fixes:")
            print("- Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("- Start Ollama: ollama serve")
            print("- Pull model: ollama pull mistral")
            print("- Make sure Ollama is running in a separate terminal")
        
        if rag_failed:
            print("\n💡 Construction RAG System Issues:")
            print("- Make sure Ollama is running: ollama serve")
            print("- Check if mistral model is available: ollama list")
            print("- Install missing dependencies: pip install -r requirements.txt")
        
        if not any(name == "Python Dependencies" and result for name, result in results):
            print("\n💡 Python Dependencies:")
            print("- Install dependencies: pip install -r requirements.txt")
        
        print("\n🔄 To run both servers together:")
        print("1. Terminal 1: ollama serve")
        print("2. Terminal 2: python webapp/app.py")
        print("3. Open http://localhost:5000")

if __name__ == "__main__":
    main() 