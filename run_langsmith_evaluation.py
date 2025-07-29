#!/usr/bin/env python3
"""
LangSmith Evaluation Runner for Construction TaskCheck Assistant
Runs comprehensive evaluation using LangSmith and custom construction metrics
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add scripts directory to path
current_dir = Path(__file__).parent
scripts_dir = current_dir / 'scripts'

if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('langsmith_evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run LangSmith evaluation for construction assistant"""
    logger.info("🏗️ Starting Construction LangSmith Evaluation")
    
    # Check if LangSmith is configured
    if not os.getenv("LANGCHAIN_API_KEY"):
        logger.error("❌ LangSmith API key not found. Please set LANGCHAIN_API_KEY in your environment.")
        logger.info("💡 You can get a free API key from https://smith.langchain.com/")
        return False
    
    try:
        # Import evaluation modules
        from construction_langsmith_evaluator import get_construction_langsmith_evaluator
        from construction_rag_chat import get_construction_rag_chat
        
        # Initialize evaluator and RAG system
        logger.info("🔧 Initializing evaluation components...")
        evaluator = get_construction_langsmith_evaluator()
        rag_chat = get_construction_rag_chat()
        
        # Check if RAG system is working
        status = rag_chat.get_status()
        logger.info(f"RAG System Status: {status}")
        
        if not status['ollama_available']:
            logger.error("❌ Ollama is not available. Please start Ollama first.")
            logger.info("💡 Run: ollama serve")
            return False
        
        # Run evaluation
        logger.info("📊 Running construction evaluation...")
        results = evaluator.run_evaluation(rag_chat)
        
        if "error" in results:
            logger.error(f"❌ Evaluation failed: {results['error']}")
            return False
        
        # Save results
        evaluator.save_results(results, "construction_langsmith_results.json")
        
        # Generate report
        report = evaluator.generate_report(results)
        with open("construction_langsmith_report.md", 'w') as f:
            f.write(report)
        
        logger.info("✅ Evaluation completed successfully!")
        logger.info("📄 Results saved to: construction_langsmith_results.json")
        logger.info("📄 Report saved to: construction_langsmith_report.md")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏗️ CONSTRUCTION LANGSMITH EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful Tests: {results['successful_tests']}")
        print(f"Success Rate: {results['success_rate']:.2%}")
        print(f"Overall Score: {results['overall_score']:.2f}")
        
        # Performance recommendations
        if results['overall_score'] >= 0.8:
            print("\n🎉 Excellent performance! Your construction assistant is working well.")
            print("💡 Consider adding advanced features like multi-modal processing.")
        elif results['overall_score'] >= 0.6:
            print("\n⚠️ Good performance with room for improvement.")
            print("💡 Consider optimizing prompts and context retrieval.")
        else:
            print("\n❌ Performance needs improvement.")
            print("💡 Consider:")
            print("   - Adding more construction-specific context")
            print("   - Optimizing the Ollama model")
            print("   - Implementing fallback APIs")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ Evaluation failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 