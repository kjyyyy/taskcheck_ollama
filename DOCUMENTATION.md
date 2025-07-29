# 🏗️ Construction TaskCheck Assistant - Technical Documentation

## Overview

The Construction TaskCheck Assistant is a specialized AI system built with LangChain, Ollama, and Flask, designed to help construction professionals with material sourcing, tender document analysis, RFD processing, and construction project management. It provides a RAG (Retrieval-Augmented Generation) powered knowledge system specifically tailored for the UK construction industry.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TypeScript    │    │   Flask API     │    │   Ollama LLM    │
│   Frontend      │◄──►│   Server        │◄──►│   (Mistral)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   LangChain     │
                       │   + FAISS       │
                       │   RAG System    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Construction  │
                       │   Knowledge     │
                       │   Base (.txt)   │
                       └─────────────────┘
```

## 📁 Project Structure

```
taskcheck_ollama/
├── Modelfile                           # Ollama system prompt configuration
├── context/                            # Knowledge base files
│   ├── construction_materials.txt      # Material specifications and suppliers
│   ├── tender_documents.txt           # Tender analysis guidelines
│   └── rfd_processing.txt             # RFD processing procedures
├── scripts/
│   ├── construction_rag_chat.py       # Core RAG system implementation
│   ├── construction_task_analyzer.py  # Task analysis and recommendations
│   └── construction_document_processor.py # Document processing
├── webapp/
│   ├── app.py                         # Flask API server
│   ├── templates/chat.html            # Chat UI template
│   └── static/style.css               # UI styling
├── start_construction_assistant.py    # Main startup script
├── start.sh                           # Linux/Mac startup script
├── start.bat                          # Windows startup script
├── requirements.txt                   # Python dependencies
└── README.md                          # User guide
```

## 🎯 Core Capabilities

### 1. Material Sourcing
- **Material Identification**: Help identify appropriate materials for specific construction projects
- **Supplier Recommendations**: Suggest reliable UK suppliers and manufacturers
- **Cost Analysis**: Provide cost estimates and budget planning for materials
- **Quality Standards**: Ensure materials meet UK construction standards and regulations

### 2. Tender Document Analysis
- **Document Summarization**: Extract key requirements, deadlines, and specifications
- **Requirement Analysis**: Identify critical project requirements and constraints
- **Risk Assessment**: Highlight potential risks and compliance requirements
- **Timeline Planning**: Help with project scheduling and milestone tracking

### 3. RFD (Request for Documents) Processing
- **Document Organization**: Structure and organize RFD requirements
- **Compliance Checking**: Ensure documents meet regulatory requirements
- **Template Generation**: Create standardized RFD templates
- **Submission Support**: Assist with document preparation and submission

### 4. Construction Project Management
- **Project Planning**: Assist with timeline development and resource allocation
- **Regulatory Compliance**: Ensure adherence to UK construction standards
- **Risk Management**: Identify and mitigate construction risks
- **Cost Control**: Help with budget planning and cost management

## 🔧 Technical Implementation

### 1. RAG System (`scripts/construction_rag_chat.py`)

**Purpose**: The heart of the system that combines LangChain with FAISS vector store and Ollama for intelligent construction responses.

**Key Features**:
- **Context Loading**: Automatically loads construction knowledge from context files
- **Text Chunking**: Splits documents into manageable chunks (1000 chars with 200 char overlap)
- **Vector Embeddings**: Uses HuggingFace's `all-MiniLM-L6-v2` for semantic search
- **FAISS Vector Store**: Fast similarity search for relevant context retrieval
- **Ollama Integration**: Connects to local Ollama server for LLM inference
- **Task Analysis**: Integrates with construction task analyzer for detailed recommendations

**Technical Implementation**:
```python
class ConstructionRAGChat:
    def __init__(self, context_dir: str = "context", model_name: str = "mistral-construction-uk:latest"):
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
```

### 2. Task Analyzer (`scripts/construction_task_analyzer.py`)

**Purpose**: Specialized system for analyzing construction tasks and providing material, timeline, and cost recommendations.

**Task Categories**:
- **Residential Extension**: House extensions, loft conversions, conservatories
- **Commercial Building**: Office buildings, retail spaces, warehouses
- **Foundation Work**: Excavation, piling, substructure work
- **Roofing**: Roof replacement, flat roofs, pitched roofs
- **Electrical Work**: Wiring, consumer units, lighting systems
- **Plumbing**: Pipework, heating systems, bathroom installations
- **Insulation**: Cavity wall, loft, thermal insulation
- **Windows & Doors**: Installation, energy efficiency
- **Flooring**: Various flooring materials and installation
- **Demolition**: Site clearance and demolition work

**Analysis Output**:
```python
@dataclass
class ConstructionTaskAnalysis:
    task_type: str
    recommended_materials: List[str]
    complexity_level: ComplexityLevel
    estimated_timeline: str
    cost_estimate: str
    regulatory_requirements: List[str]
    risk_factors: List[str]
    supplier_recommendations: List[str]
```

### 3. Flask API Server (`webapp/app.py`)

**Purpose**: Provides RESTful API endpoints for TypeScript frontend integration and serves the chat UI.

**Key Endpoints**:
- `GET /`: Chat interface
- `POST /ask`: Main RAG inference endpoint
- `GET /health`: System health check
- `GET /materials`: Available construction materials
- `GET /materials/<material_name>`: Detailed material information
- `GET /tasks`: Available construction task types
- `POST /upload`: Document upload and processing
- `POST /process-text`: Text-based document processing

**API Request Format**:
```json
{
  "question": "What materials do I need for a residential extension?",
  "use_context": true,
  "analyze_task": true
}
```

**API Response Format**:
```json
{
  "answer": "For a residential extension, you'll need...",
  "sources": ["context/construction_materials.txt"],
  "used_context": true,
  "model": "mistral-construction-uk",
  "task_analysis": {
    "task_type": "Residential Extension",
    "recommended_materials": ["Concrete", "Steel", "Timber"],
    "complexity_level": "medium",
    "estimated_timeline": "8-16 weeks",
    "cost_estimate": "£20,000-£80,000",
    "regulatory_requirements": ["Building Regulations", "Planning Permission"],
    "risk_factors": ["Planning delays", "Structural issues"],
    "supplier_recommendations": ["Travis Perkins", "Wickes", "Jewson"]
  }
}
```

### 4. Knowledge Base Structure

**Construction Materials** (`context/construction_materials.txt`):
- Structural materials (concrete, steel, timber)
- Insulation materials (cavity wall, roof insulation)
- Finishing materials (plaster, render, flooring)
- Roofing materials (tiles, membranes)
- Windows and doors
- Plumbing and electrical materials
- Sustainability and green materials
- Material selection guidelines
- Regulatory compliance
- Supplier selection criteria

**Tender Documents** (`context/tender_documents.txt`):
- Tender document types (ITT, PQQ, RFP)
- Key document sections
- Tender analysis process
- Common requirements
- Risk assessment
- Response strategy
- Evaluation criteria
- Best practices

**RFD Processing** (`context/rfd_processing.txt`):
- RFD overview and types
- Processing workflow
- Common requirements
- Response strategy
- Document management
- Technology solutions
- Performance metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Ollama installed (https://ollama.ai/)
- Git

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd taskcheck_ollama
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the assistant**:
```bash
# Linux/Mac
./start.sh

# Windows
start.bat

# Or directly
python start_construction_assistant.py
```

4. **Access the web interface**:
   - Open your browser to `http://localhost:5000`
   - The assistant will be ready to help with construction tasks

## 📋 Usage Examples

### Material Sourcing
```
User: "I need materials for a residential extension project"
Assistant: "For a residential extension, you'll need:
- Structural materials: Concrete for foundations, steel for support, timber for framing
- Insulation: Cavity wall and roof insulation for energy efficiency
- Finishing materials: Plaster, render, flooring options
- Windows and doors: Energy-efficient glazing
- Recommended suppliers: Travis Perkins, Wickes, Jewson
- Estimated cost: £20,000-£80,000
- Timeline: 8-16 weeks"
```

### Tender Analysis
```
User: "Analyze this tender document for a commercial building project"
Assistant: "Key requirements identified:
- Project scope: 5-story office building
- Timeline: 18 months
- Budget: £2.5M
- Critical deadlines: [specific dates]
- Compliance requirements: Building Regulations, Fire Safety, CDM
- Risk factors: Complex planning, budget management, stakeholder coordination
- Technical requirements: Steel frame, concrete slabs, HVAC systems"
```

### RFD Processing
```
User: "Help me prepare an RFD for a bridge construction project"
Assistant: "RFD Structure:
1. Project specifications and requirements
2. Technical documentation needed
3. Regulatory compliance documents
4. Safety and environmental assessments
5. Timeline and milestone requirements
6. Budget and cost breakdown
7. Risk assessment and mitigation strategies"
```

## 🔧 Configuration

### Environment Variables
- `OLLAMA_HOST`: Ollama server host (default: localhost)
- `OLLAMA_PORT`: Ollama server port (default: 11434)
- `MODEL_NAME`: Ollama model name (default: mistral-construction-uk)
- `OPENROUTER_API_KEY`: API key for OpenRouter models (optional)

### Model Configuration

**Ollama Modelfile** (`Modelfile`):
```
FROM mistral

SYSTEM "You are a specialized UK construction assistant with expertise in construction materials, tender documents, RFDs (Request for Documents), and construction project management. Your role is to:

1. MATERIAL SOURCING: Help construction professionals find and source appropriate materials for projects
2. TENDER ANALYSIS: Analyze and summarize tender documents, highlighting key requirements and deadlines
3. RFD PROCESSING: Process and organize Request for Documents (RFDs) for construction projects
4. CONSTRUCTION GUIDANCE: Provide information about UK construction standards, regulations, and best practices
5. PROJECT MANAGEMENT: Assist with construction project planning, timelines, and resource allocation

IMPORTANT GUIDELINES:
- Always consider UK construction standards and regulations (Building Regulations, CDM, etc.)
- Recommend appropriate materials based on project requirements and specifications
- Provide information about construction services, procurement processes, and industry standards
- Include relevant UK construction guidelines and best practices
- Always remind users that this is not a substitute for professional construction advice
- Encourage consultation with qualified construction professionals, architects, and engineers
- Consider UK-specific construction terminology and industry structures
- Focus on practical, actionable advice for construction projects

When analyzing construction tasks, structure your response to include:
1. Project overview and requirements
2. Material recommendations and sourcing options
3. Timeline and resource considerations
4. Regulatory compliance requirements
5. Risk assessment and mitigation strategies
6. Cost considerations and budget planning"
```

## 🔌 Integration Points

### TypeScript/React Integration

```typescript
// Basic API call
const response = await fetch("http://localhost:5000/ask", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question: "What materials do I need for a residential extension?",
    use_context: true,
    analyze_task: true
  })
});

const data = await response.json();
console.log(data.answer);
console.log(data.task_analysis);
```

### Material Information API

```typescript
// Get available materials
const materialsResponse = await fetch("http://localhost:5000/materials");
const materials = await materialsResponse.json();

// Get detailed material info
const materialInfo = await fetch("http://localhost:5000/materials/Concrete");
const concreteInfo = await materialInfo.json();
```

### Task Types API

```typescript
// Get available task types
const tasksResponse = await fetch("http://localhost:5000/tasks");
const tasks = await tasksResponse.json();
```

## 🧪 Testing and Evaluation

### Manual Testing

**Chat Interface**: http://localhost:5000
**API Testing**: Use curl or Postman
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What materials for foundation work?", "use_context": true, "analyze_task": true}'
```

### Health Check
```bash
curl http://localhost:5000/health
```

## 🔧 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Check if Ollama is running: `ollama serve`
   - Verify model availability: `ollama list`
   - Pull missing model: `ollama pull mistral`

2. **Import Errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version: `python3 --version`
   - Verify virtual environment (if using)

3. **Context Not Loading**
   - Check file permissions
   - Verify UTF-8 encoding
   - Ensure files are in `context/` directory

4. **Flask App Won't Start**
   - Check port availability: `netstat -tulpn | grep 5000`
   - Verify Python path configuration
   - Check for import errors in logs

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=1
python3 webapp/app.py
```

## 🚀 Performance Considerations

### Optimization Strategies

1. **Vector Store Caching**: FAISS index is cached in memory
2. **Embedding Model**: Uses lightweight `all-MiniLM-L6-v2`
3. **Chunk Size**: Optimized for construction text (1000 chars)
4. **Retrieval**: Top-3 most relevant chunks
5. **Connection Pooling**: Reuses Ollama connections

### Scalability Options

1. **Horizontal Scaling**: Multiple Flask instances behind load balancer
2. **Vector Store**: Replace FAISS with Pinecone or Weaviate
3. **Model Serving**: Use Ollama in separate container
4. **Caching**: Add Redis for response caching
5. **CDN**: Serve static files via CDN

## 🔒 Security Considerations

### Data Protection

- **No Sensitive Storage**: System doesn't store sensitive project information
- **Local Processing**: All processing happens on local/private servers
- **Context Validation**: Sanitize construction content before loading
- **Access Control**: Implement authentication for production use

### Production Hardening

1. **HTTPS**: Enable SSL/TLS encryption
2. **Authentication**: Add user authentication system
3. **Rate Limiting**: Implement API rate limiting
4. **Input Validation**: Sanitize all user inputs
5. **Logging**: Comprehensive audit logging

## 📈 Monitoring and Observability

### Health Checks

- **System Health**: `/health` endpoint
- **Ollama Status**: Connection and model availability
- **Context Status**: File loading and vector store health
- **API Metrics**: Response times and error rates

### Logging

- **Application Logs**: Flask and RAG system logs
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time monitoring
- **Usage Analytics**: Query patterns and frequency

## 🔄 Maintenance

### Regular Tasks

1. **Context Updates**: Refresh construction knowledge base
2. **Model Updates**: Pull latest Ollama models
3. **Dependency Updates**: Update Python packages
4. **Backup**: Backup context files and configurations
5. **Monitoring**: Review system logs and metrics

### Update Procedures

1. **Code Updates**: Git-based deployment
2. **Context Updates**: Replace files in `context/` directory
3. **Model Updates**: `ollama pull mistral:latest`
4. **Dependency Updates**: `pip install -r requirements.txt --upgrade`

## 📚 Additional Resources

### Documentation
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)

### Construction Standards
- [UK Building Regulations](https://www.gov.uk/building-regulations)
- [CDM Regulations](https://www.hse.gov.uk/construction/cdm/)
- [British Standards](https://www.bsigroup.com/)

### Technical References
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [HuggingFace Models](https://huggingface.co/models)

---

**⚠️ Important Disclaimer**: This construction assistant is for informational and planning purposes only. It is not a substitute for professional construction advice, engineering consultation, or legal guidance. Always consult with qualified construction professionals, architects, engineers, and legal experts for your specific project requirements. 