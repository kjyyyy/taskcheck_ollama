#!/usr/bin/env python3
"""
Flask API Server for Construction TaskCheck Assistant
Provides chat UI and RAG inference endpoint for TypeScript integration
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import logging
import sys
import os
from pathlib import Path
import json
from werkzeug.utils import secure_filename
import os

# Add language detection
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # For consistent results
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("Warning: langdetect not available. Install with: pip install langdetect")

# Add scripts directory to path - handle different working directories
current_dir = Path(__file__).parent
project_root = current_dir.parent
scripts_dir = project_root / 'scripts'

# Add scripts directory to Python path
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Also add project root to path for context directory access
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from construction_rag_chat import get_construction_rag_chat
    from construction_document_processor import get_construction_document_processor
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Scripts directory: {scripts_dir}")
    print(f"Python path: {sys.path}")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('construction_flask_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CORS(app)  # Enable CORS for TypeScript frontend integration

# Initialize construction RAG chat system
construction_rag_chat = None
construction_document_processor = None

def detect_language(text: str) -> str:
    """
    Detect the language of the input text
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code ('en', 'zh-cn', 'zh-tw', 'tl', 'ms') or 'en' as default
    """
    if not LANGDETECT_AVAILABLE:
        return 'en'
    
    try:
        # Detect language
        lang_code = detect(text)
        
        # Map language codes to our supported languages
        if lang_code == 'zh-cn':
            return 'zh-cn'  # Simplified Chinese (Singapore)
        elif lang_code == 'zh-tw':
            return 'zh-tw'  # Traditional Chinese (Hong Kong)
        elif lang_code == 'zh':
            # For generic Chinese, try to determine simplified vs traditional
            simplified_chars = ['简', '体', '汉', '语']
            traditional_chars = ['簡', '體', '漢', '語']
            
            has_simplified = any(char in text for char in simplified_chars)
            has_traditional = any(char in text for char in traditional_chars)
            
            if has_traditional and not has_simplified:
                return 'zh-tw'  # Traditional Chinese (Hong Kong)
            else:
                return 'zh-cn'  # Default to Simplified Chinese (Singapore)
        elif lang_code == 'tl':
            return 'tl'  # Tagalog (Philippines)
        elif lang_code == 'ms':
            return 'ms'  # Malay (Malaysia)
        else:
            return 'en'  # Default to English
            
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return 'en'  # Default to English

def get_chat_system():
    """Get or initialize the construction RAG chat system"""
    global construction_rag_chat
    if construction_rag_chat is None:
        try:
            construction_rag_chat = get_construction_rag_chat()
            logger.info("Construction RAG chat system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize construction RAG chat system: {e}")
            return None
    return construction_rag_chat

def get_doc_processor():
    """Get or initialize the construction document processor"""
    global construction_document_processor
    if construction_document_processor is None:
        try:
            # Get OpenRouter API key from environment
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            construction_document_processor = get_construction_document_processor(openrouter_key)
            logger.info("Construction document processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize construction document processor: {e}")
            return None
    return construction_document_processor

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def chat_ui():
    """Serve the chat UI"""
    return render_template('chat.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        chat_system = get_chat_system()
        if chat_system:
            status = chat_system.get_status()
            return jsonify({
                "status": "healthy" if status["ollama_available"] else "degraded",
                "model": chat_system.model_name,
                "context_loaded": chat_system.vectorstore is not None,
                "ollama_available": status["ollama_available"],
                "qa_chain_available": status["qa_chain_available"]
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "error": "Construction RAG chat system not initialized"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    RAG inference endpoint for TypeScript integration
    
    Expected JSON payload:
    {
        "question": "What materials do I need for a residential extension?",
        "use_context": true,
        "language": "en" (optional - auto-detected if not provided)
    }
    
    Returns:
    {
        "answer": "Response text",
        "sources": ["source1", "source2"],
        "used_context": true,
        "model": "mistral",
        "detected_language": "en"
    }
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided in request")
            return jsonify({"error": "No JSON data provided"}), 400
        
        question = data.get('question', '').strip()
        use_context = data.get('use_context', True)
        analyze_task = data.get('analyze_task', False)
        user_language = data.get('language', None)  # Allow user to specify language
        
        logger.info(f"Processing question: {question[:100]}...")
        logger.debug(f"use_context: {use_context}, analyze_task: {analyze_task}")
        
        if not question:
            logger.warning("Empty question provided")
            return jsonify({"error": "Question is required"}), 400
        
        # Detect language if not provided
        if user_language:
            detected_language = user_language
            logger.info(f"Using user-specified language: {detected_language}")
        else:
            detected_language = detect_language(question)
            logger.info(f"Detected language: {detected_language}")
        
        # Get chat system
        chat_system = get_chat_system()
        if not chat_system:
            logger.error("Chat system not available")
            return jsonify({"error": "Chat system not available"}), 500
        
        # Get response
        logger.info("Getting response from chat system")
        response = chat_system.ask(question, use_context=use_context, analyze_task=analyze_task)
        
        # Add language information to response
        response['detected_language'] = detected_language
        
        # Log response summary
        if response.get("task_analysis"):
            logger.info(f"Task analysis provided for task type: {response['task_analysis'].get('task_type', 'unknown')}")
        
        # Return response
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in ask endpoint: {e}", exc_info=True)
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "answer": "Sorry, I encountered an error processing your request.",
            "sources": [],
            "used_context": False,
            "model": "unknown",
            "detected_language": "en"
        }), 500

@app.route('/ask/stream', methods=['POST'])
def ask_question_stream():
    """
    Streaming RAG inference endpoint (for future use)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        question = data.get('question', '').strip()
        use_context = data.get('use_context', True)
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # For now, return non-streaming response
        # This can be extended to use streaming in the future
        chat_system = get_chat_system()
        if not chat_system:
            return jsonify({"error": "Chat system not available"}), 500
        
        response = chat_system.ask(question, use_context=use_context)
        
        def generate():
            yield f"data: {json.dumps(response)}\n\n"
        
        return Response(generate(), mimetype='text/plain')
        
    except Exception as e:
        logger.error(f"Error in streaming ask endpoint: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/reload', methods=['POST'])
def reload_context():
    """Reload context files"""
    try:
        chat_system = get_chat_system()
        if not chat_system:
            return jsonify({"error": "Chat system not available"}), 500
        
        chat_system.reload_context()
        return jsonify({"message": "Context reloaded successfully"})
        
    except Exception as e:
        logger.error(f"Error reloading context: {e}")
        return jsonify({"error": f"Failed to reload context: {str(e)}"}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    try:
        chat_system = get_chat_system()
        if chat_system:
            return jsonify({
                "current_model": chat_system.model_name,
                "available_models": ["mistral", "llama2", "codellama"]  # Add your available models
            })
        else:
            return jsonify({"error": "Chat system not available"}), 500
    except Exception as e:
        return jsonify({"error": f"Error listing models: {str(e)}"}), 500

@app.route('/context', methods=['GET'])
def get_context_info():
    """Get information about loaded context"""
    try:
        chat_system = get_chat_system()
        if not chat_system:
            return jsonify({"error": "Chat system not available"}), 500
        
        # Count context files
        context_dir = Path(__file__).parent.parent / 'context'
        context_files = []
        if context_dir.exists():
            for file_path in context_dir.rglob("*.txt"):
                context_files.append(str(file_path.name))
            for file_path in context_dir.rglob("*.md"):
                context_files.append(str(file_path.name))
        
        return jsonify({
            "context_files": context_files,
            "total_files": len(context_files),
            "vectorstore_loaded": chat_system.vectorstore is not None
        })
        
    except Exception as e:
        logger.error(f"Error getting context info: {e}")
        return jsonify({"error": f"Error getting context info: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process construction document"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get document processor
        doc_processor = get_doc_processor()
        if not doc_processor:
            return jsonify({"error": "Document processor not available"}), 500
        
        # Process document
        document_type = request.form.get('document_type', 'tender_document')
        result = doc_processor.process_construction_document(filepath, True, document_type)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing uploaded document: {e}")
        return jsonify({"error": f"Error processing document: {str(e)}"}), 500

@app.route('/process-text', methods=['POST'])
def process_text():
    """Process construction document text directly"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        text = data.get('text', '').strip()
        document_type = data.get('document_type', 'tender_document')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Get document processor
        doc_processor = get_doc_processor()
        if not doc_processor:
            return jsonify({"error": "Document processor not available"}), 500
        
        # Parse construction document
        document_data = doc_processor.parse_construction_document(text)
        
        # Generate document
        document = doc_processor.generate_construction_document(document_data, document_type)
        
        return jsonify({
            "extracted_data": document_data,
            "generated_document": document,
            "document_type": document_type
        })
        
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return jsonify({"error": f"Error processing text: {str(e)}"}), 500

@app.route('/document-types', methods=['GET'])
def get_document_types():
    """Get available document types"""
    return jsonify({
        "document_types": [
            "tender_document",
            "rfd_request", 
            "material_specification",
            "project_plan"
        ]
    })

@app.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get supported file formats"""
    doc_processor = get_doc_processor()
    if doc_processor:
        return jsonify({
            "supported_formats": doc_processor.supported_formats
        })
    else:
        return jsonify({"error": "Document processor not available"}), 500

@app.route('/materials', methods=['GET'])
def get_materials():
    """Get available construction materials"""
    try:
        chat_system = get_chat_system()
        if chat_system and chat_system.task_analyzer:
            materials = list(chat_system.task_analyzer.material_mapping.keys())
            return jsonify({
                "materials": materials,
                "total_materials": len(materials)
            })
        else:
            return jsonify({"error": "Task analyzer not available"}), 500
    except Exception as e:
        return jsonify({"error": f"Error getting materials: {str(e)}"}), 500

@app.route('/materials/<material_name>', methods=['GET'])
def get_material_info(material_name):
    """Get detailed information about a specific material"""
    try:
        chat_system = get_chat_system()
        if chat_system and chat_system.task_analyzer:
            material_info = chat_system.task_analyzer.get_material_info(material_name)
            return jsonify(material_info)
        else:
            return jsonify({"error": "Task analyzer not available"}), 500
    except Exception as e:
        return jsonify({"error": f"Error getting material info: {str(e)}"}), 500

@app.route('/tasks', methods=['GET'])
def get_task_types():
    """Get available construction task types"""
    try:
        chat_system = get_chat_system()
        if chat_system and chat_system.task_analyzer:
            task_types = list(chat_system.task_analyzer.task_patterns.keys())
            return jsonify({
                "task_types": task_types,
                "total_tasks": len(task_types)
            })
        else:
            return jsonify({"error": "Task analyzer not available"}), 500
    except Exception as e:
        return jsonify({"error": f"Error getting task types: {str(e)}"}), 500

@app.route('/evaluate', methods=['POST'])
def run_evaluation():
    """Run LangSmith evaluation"""
    try:
        from construction_langsmith_evaluator import get_construction_langsmith_evaluator
        
        evaluator = get_construction_langsmith_evaluator()
        chat_system = get_chat_system()
        
        if not chat_system:
            return jsonify({"error": "Chat system not initialized"}), 500
        
        # Run evaluation
        results = evaluator.run_evaluation(chat_system)
        
        if "error" in results:
            return jsonify({"error": results["error"]}), 500
        
        # Save results
        evaluator.save_results(results, "construction_evaluation_results.json")
        
        return jsonify({
            "success": True,
            "results": results,
            "message": "Evaluation completed successfully"
        })
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get supported languages for the construction assistant"""
    try:
        return jsonify({
            "supported_languages": [
                {
                    "code": "en",
                    "name": "English",
                    "native_name": "English",
                    "region": "UK"
                },
                {
                    "code": "zh-cn",
                    "name": "Simplified Chinese",
                    "native_name": "简体中文",
                    "region": "Singapore"
                },
                {
                    "code": "zh-tw",
                    "name": "Traditional Chinese", 
                    "native_name": "繁體中文",
                    "region": "Hong Kong"
                },
                {
                    "code": "tl",
                    "name": "Tagalog",
                    "native_name": "Tagalog",
                    "region": "Philippines"
                },
                {
                    "code": "ms",
                    "name": "Malay",
                    "native_name": "Bahasa Malaysia",
                    "region": "Malaysia"
                }
            ],
            "default_language": "en",
            "auto_detection": LANGDETECT_AVAILABLE,
            "regional_focus": [
                "Hong Kong",
                "Singapore", 
                "Malaysia",
                "Philippines",
                "UK"
            ]
        })
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/langsmith-status', methods=['GET'])
def get_langsmith_status():
    """Check LangSmith configuration status"""
    langsmith_configured = bool(os.getenv("LANGCHAIN_API_KEY"))
    
    return jsonify({
        "langsmith_configured": langsmith_configured,
        "tracing_enabled": os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
        "project_name": os.getenv("LANGCHAIN_PROJECT", "construction-taskcheck")
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Initialize chat system on startup
    logger.info("Initializing construction taskcheck assistant...")
    get_chat_system()
    
    # Run the app
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5050,
        debug=False  # Set to False for production
    ) 