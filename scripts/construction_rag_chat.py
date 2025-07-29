#!/usr/bin/env python3
"""
Construction RAG Chat Backend for TaskCheck Assistant
Uses LangChain + FAISS for context retrieval and Ollama for inference
"""

import os
import json
import logging
import time
from typing import List, Dict, Optional
from pathlib import Path

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langsmith import Client
from construction_task_analyzer import get_construction_task_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('construction_rag_chat.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConstructionRAGChat:
    def __init__(self, context_dir: str = "context", model_name: str = "mistral-construction:latest"):
        """
        Initialize the construction RAG chat system
        
        Args:
            context_dir: Directory containing knowledge base files
            model_name: Ollama model name to use
        """
        # Handle context directory path relative to project root
        if not Path(context_dir).is_absolute():
            # Try to find the project root by looking for the context directory
            current_dir = Path.cwd()
            project_root = None
            
            # Look for context directory in current directory or parent directories
            for parent in [current_dir] + list(current_dir.parents):
                if (parent / context_dir).exists():
                    project_root = parent
                    break
            
            if project_root:
                self.context_dir = project_root / context_dir
            else:
                # Fallback to current directory
                self.context_dir = Path(context_dir)
        else:
            self.context_dir = Path(context_dir)
            
        self.model_name = model_name
        self.vectorstore = None
        self.qa_chain = None
        self.embeddings = None
        self.ollama_available = False
        self.task_analyzer = get_construction_task_analyzer()
        
        # Initialize components
        self._setup_embeddings()
        self._load_context()
        self._setup_qa_chain()
    
    def _setup_embeddings(self):
        """Initialize embeddings model"""
        try:
            # Use a lightweight embedding model for production
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            logger.info("Embeddings model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            raise
    
    def _load_context(self):
        """Load and process context files"""
        logger.info(f"Loading context from directory: {self.context_dir}")
        
        if not self.context_dir.exists():
            logger.warning(f"Context directory {self.context_dir} not found. Creating empty vectorstore.")
            self.vectorstore = FAISS.from_texts(["No context available"], self.embeddings)
            return
        
        documents = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Load text files
        files_loaded = 0
        for file_path in self.context_dir.rglob("*.txt"):
            try:
                logger.debug(f"Loading file: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={"source": str(file_path)}
                    )
                    documents.append(doc)
                    logger.info(f"Loaded {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        # Load markdown files
        for file_path in self.context_dir.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={"source": str(file_path)}
                    )
                    documents.append(doc)
                    logger.info(f"Loaded {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        if documents:
            # Split documents into chunks
            texts = text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(texts)} chunks")
            
            # Create vectorstore
            self.vectorstore = FAISS.from_documents(texts, self.embeddings)
            logger.info("Vectorstore created successfully")
        else:
            logger.warning("No documents found in context directory")
            self.vectorstore = FAISS.from_texts(["No context available"], self.embeddings)
    
    def _check_ollama_connection(self):
        """Check if Ollama is available"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any(m.get("name") == self.model_name for m in models):
                    self.ollama_available = True
                    logger.info(f"Ollama is available with model {self.model_name}")
                    return True
                else:
                    logger.warning(f"Model {self.model_name} not found in Ollama")
                    return False
            else:
                logger.warning("Ollama responded with error")
                return False
        except Exception as e:
            logger.warning(f"Cannot connect to Ollama: {e}")
            return False
    
    def _setup_qa_chain(self):
        """Setup the QA chain with Ollama"""
        try:
            # Check Ollama connection first
            if not self._check_ollama_connection():
                logger.warning("Ollama not available, QA chain will not be initialized")
                self.qa_chain = None
                return
            
            # Initialize Ollama
            llm = Ollama(model=self.model_name)
            
            # Test the connection
            try:
                test_response = llm("Hello")
                logger.info("Ollama connection test successful")
            except Exception as e:
                logger.error(f"Ollama connection test failed: {e}")
                self.qa_chain = None
                return
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True
            )
            logger.info("QA chain setup successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup QA chain: {e}")
            self.qa_chain = None
    
    def ask(self, question: str, use_context: bool = True, analyze_task: bool = False) -> Dict:
        """
        Ask a question and get response with LangSmith tracing
        
        Args:
            question: User's question
            use_context: Whether to use RAG context or direct model response
            analyze_task: Whether to perform task analysis
            
        Returns:
            Dict with answer and metadata
        """
        try:
            # Initialize LangSmith client if available
            langsmith_client = None
            try:
                if os.getenv("LANGCHAIN_API_KEY"):
                    langsmith_client = Client()
                    logger.info("LangSmith tracing enabled")
                else:
                    logger.info("LangSmith not configured, running without tracing")
            except Exception as e:
                logger.warning(f"LangSmith initialization failed: {e}")
            
            # Check if Ollama is available
            if not self.ollama_available:
                self._check_ollama_connection()
            
            # Perform task analysis if requested
            task_analysis = None
            if analyze_task and self.task_analyzer:
                try:
                    task_analysis = self.task_analyzer.analyze_construction_task(question)
                except Exception as e:
                    logger.error(f"Error in task analysis: {e}")
            
            # Start LangSmith trace if available
            if langsmith_client:
                with langsmith_client.trace() as tracer:
                    # Add construction-specific metadata
                    tracer.add_metadata({
                        "construction_task_type": self._identify_task_type(question),
                        "use_context": use_context,
                        "analyze_task": analyze_task,
                        "model_name": self.model_name
                    })
                    
                    response = self._get_response_with_tracing(question, use_context, task_analysis, tracer)
            else:
                response = self._get_response_without_tracing(question, use_context, task_analysis)
            
            return response
                
        except Exception as e:
            logger.error(f"Error in ask method: {e}")
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "sources": [],
                "used_context": use_context,
                "model": self.model_name,
                "error": True
            }
    
    def _identify_task_type(self, question: str) -> str:
        """Identify the type of construction task from the question"""
        question_lower = question.lower()
        
        task_patterns = {
            "material_sourcing": ["material", "supplier", "cost", "specification"],
            "tender_analysis": ["tender", "bid", "proposal", "requirement"],
            "rfd_processing": ["rfd", "document", "submission", "requirement"],
            "regulatory_compliance": ["regulation", "compliance", "standard", "requirement"],
            "project_management": ["timeline", "schedule", "milestone", "deadline"],
            "risk_assessment": ["risk", "hazard", "safety", "mitigation"]
        }
        
        for task_type, keywords in task_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                return task_type
        
        return "general_construction"
    
    def _get_response_with_tracing(self, question: str, use_context: bool, task_analysis, tracer) -> Dict:
        """Get response with LangSmith tracing"""
        if use_context and self.qa_chain and self.ollama_available:
            # Use RAG with context
            result = self.qa_chain({"query": question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "Unknown") for doc in result.get("source_documents", [])]
            
            # Add construction-specific metadata to trace
            tracer.add_metadata({
                "materials_mentioned": self._extract_materials(answer),
                "regulations_referenced": self._extract_regulations(answer),
                "cost_mentioned": self._extract_cost(answer),
                "timeline_mentioned": self._extract_timeline(answer),
                "sources_count": len(sources)
            })
            
            response = {
                "answer": answer,
                "sources": sources,
                "used_context": True,
                "model": self.model_name
            }
            
            # Add task analysis if available
            if task_analysis:
                response["task_analysis"] = {
                    "task_type": task_analysis.task_type,
                    "recommended_materials": task_analysis.recommended_materials,
                    "complexity_level": task_analysis.complexity_level.value,
                    "estimated_timeline": task_analysis.estimated_timeline,
                    "cost_estimate": task_analysis.cost_estimate,
                    "regulatory_requirements": task_analysis.regulatory_requirements,
                    "risk_factors": task_analysis.risk_factors,
                    "supplier_recommendations": task_analysis.supplier_recommendations
                }
            
            return response
        elif self.ollama_available:
            # Direct model response without context
            llm = Ollama(model=self.model_name)
            answer = llm(question)
            
            # Add construction-specific metadata to trace
            tracer.add_metadata({
                "materials_mentioned": self._extract_materials(answer),
                "regulations_referenced": self._extract_regulations(answer),
                "cost_mentioned": self._extract_cost(answer),
                "timeline_mentioned": self._extract_timeline(answer),
                "sources_count": 0
            })
            
            response = {
                "answer": answer,
                "sources": [],
                "used_context": False,
                "model": self.model_name
            }
            
            # Add task analysis if available
            if task_analysis:
                response["task_analysis"] = {
                    "task_type": task_analysis.task_type,
                    "recommended_materials": task_analysis.recommended_materials,
                    "complexity_level": task_analysis.complexity_level.value,
                    "estimated_timeline": task_analysis.estimated_timeline,
                    "cost_estimate": task_analysis.cost_estimate,
                    "regulatory_requirements": task_analysis.regulatory_requirements,
                    "risk_factors": task_analysis.risk_factors,
                    "supplier_recommendations": task_analysis.supplier_recommendations
                }
            
            return response
        else:
            # Fallback response when Ollama is not available
            return {
                "answer": "I'm sorry, but I'm currently unable to process your request. Please make sure Ollama is running and the model is available. You can start Ollama with 'ollama serve' and pull the model with 'ollama pull mistral'.",
                "sources": [],
                "used_context": False,
                "model": "unavailable",
                "error": "Ollama not available"
            }
    
    def _get_response_without_tracing(self, question: str, use_context: bool, task_analysis) -> Dict:
        """Get response without LangSmith tracing"""
        if use_context and self.qa_chain and self.ollama_available:
            # Use RAG with context
            result = self.qa_chain({"query": question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "Unknown") for doc in result.get("source_documents", [])]
            
            response = {
                "answer": answer,
                "sources": sources,
                "used_context": True,
                "model": self.model_name
            }
            
            # Add task analysis if available
            if task_analysis:
                response["task_analysis"] = {
                    "task_type": task_analysis.task_type,
                    "recommended_materials": task_analysis.recommended_materials,
                    "complexity_level": task_analysis.complexity_level.value,
                    "estimated_timeline": task_analysis.estimated_timeline,
                    "cost_estimate": task_analysis.cost_estimate,
                    "regulatory_requirements": task_analysis.regulatory_requirements,
                    "risk_factors": task_analysis.risk_factors,
                    "supplier_recommendations": task_analysis.supplier_recommendations
                }
            
            return response
        elif self.ollama_available:
            # Direct model response without context
            llm = Ollama(model=self.model_name)
            answer = llm(question)
            
            response = {
                "answer": answer,
                "sources": [],
                "used_context": False,
                "model": self.model_name
            }
            
            # Add task analysis if available
            if task_analysis:
                response["task_analysis"] = {
                    "task_type": task_analysis.task_type,
                    "recommended_materials": task_analysis.recommended_materials,
                    "complexity_level": task_analysis.complexity_level.value,
                    "estimated_timeline": task_analysis.estimated_timeline,
                    "cost_estimate": task_analysis.cost_estimate,
                    "regulatory_requirements": task_analysis.regulatory_requirements,
                    "risk_factors": task_analysis.risk_factors,
                    "supplier_recommendations": task_analysis.supplier_recommendations
                }
            
            return response
        else:
            # Fallback response when Ollama is not available
            return {
                "answer": "I'm sorry, but I'm currently unable to process your request. Please make sure Ollama is running and the model is available. You can start Ollama with 'ollama serve' and pull the model with 'ollama pull mistral'.",
                "sources": [],
                "used_context": False,
                "model": "unavailable",
                "error": "Ollama not available"
            }
    
    def _extract_materials(self, text: str) -> List[str]:
        """Extract materials mentioned in text"""
        material_keywords = [
            "concrete", "steel", "timber", "bricks", "insulation", "roof tiles",
            "windows", "doors", "plumbing", "electrical", "flooring", "paint",
            "render", "plaster", "cement", "slate", "lead", "copper", "tiles"
        ]
        
        text_lower = text.lower()
        found_materials = []
        
        for material in material_keywords:
            if material in text_lower:
                found_materials.append(material)
        
        return found_materials
    
    def _extract_regulations(self, text: str) -> List[str]:
        """Extract regulations mentioned in text"""
        regulation_keywords = [
            "building regulations", "planning permission", "cdm regulations",
            "fire safety", "party wall act", "health and safety",
            "environmental impact assessment", "breeam", "energy performance"
        ]
        
        text_lower = text.lower()
        found_regulations = []
        
        for regulation in regulation_keywords:
            if regulation in text_lower:
                found_regulations.append(regulation)
        
        return found_regulations
    
    def _extract_cost(self, text: str) -> Optional[str]:
        """Extract cost information from text"""
        import re
        cost_patterns = [
            r'£[\d,]+(?:\.\d{2})?',
            r'\$[\d,]+(?:\.\d{2})?',
            r'cost[:\s]+([^\n]+)',
            r'budget[:\s]+([^\n]+)',
            r'estimated[:\s]+([^\n]+)'
        ]
        
        for pattern in cost_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0) if '£' in pattern or '$' in pattern else match.group(1).strip()
        
        return None
    
    def _extract_timeline(self, text: str) -> Optional[str]:
        """Extract timeline information from text"""
        import re
        timeline_patterns = [
            r'\d+\s*(?:weeks?|months?|days?)',
            r'timeline[:\s]+([^\n]+)',
            r'duration[:\s]+([^\n]+)',
            r'completion[:\s]+([^\n]+)'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0) if 'weeks?' in pattern or 'months?' in pattern or 'days?' in pattern else match.group(1).strip()
        
        return None
    
    def reload_context(self):
        """Reload context files"""
        logger.info("Reloading context...")
        self._load_context()
        self._setup_qa_chain()
        logger.info("Context reloaded successfully")
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "ollama_available": self.ollama_available,
            "model_name": self.model_name,
            "vectorstore_loaded": self.vectorstore is not None,
            "qa_chain_available": self.qa_chain is not None
        }

# Global instance for Flask app
construction_rag_chat = None

def get_construction_rag_chat():
    """Get or create construction RAG chat instance"""
    global construction_rag_chat
    if construction_rag_chat is None:
        construction_rag_chat = ConstructionRAGChat()
    return construction_rag_chat

if __name__ == "__main__":
    # Test the construction RAG chat system
    chat = ConstructionRAGChat()
    
    test_questions = [
        "What materials do I need for a residential extension?",
        "How do I analyze a tender document for a commercial building?",
        "What are the key requirements for an RFD submission?",
        "What are the UK building regulations for foundations?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        response = chat.ask(question)
        print(f"Answer: {response['answer']}")
        if response['sources']:
            print(f"Sources: {response['sources']}") 