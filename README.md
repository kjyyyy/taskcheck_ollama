# 🏗️ Construction TaskCheck Assistant

A specialized AI assistant for the UK construction industry, helping professionals with material sourcing, tender document analysis, RFD processing, and construction project management.

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

## 🏗️ Technical Architecture

Built with LangChain, Ollama, and Flask, providing:
- **RAG-powered knowledge system** for construction industry data
- **Document processing** for tender documents and RFDs
- **Material database** with UK suppliers and specifications
- **Regulatory compliance** checking for UK construction standards

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd taskcheck_ollama

# Install dependencies
pip install -r requirements.txt

# Start the assistant
python start_construction_assistant.py
```

## 📋 Usage Examples

### Material Sourcing
```
User: "I need materials for a residential extension project"
Assistant: "For a residential extension, you'll need:
- Structural materials: Concrete, steel, timber
- Insulation: Cavity wall and roof insulation
- Finishing materials: Plaster, paint, flooring
- Recommended suppliers: [UK suppliers list]
- Estimated cost: £X,XXX
- Timeline: 8-12 weeks"
```

### Tender Analysis
```
User: "Analyze this tender document for a commercial building project"
Assistant: "Key requirements identified:
- Project scope: 5-story office building
- Timeline: 18 months
- Budget: £2.5M
- Critical deadlines: [specific dates]
- Compliance requirements: [regulations]
- Risk factors: [identified risks]"
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
6. Budget and cost breakdown"
```

## 🔧 Configuration

### Environment Variables
- `OLLAMA_HOST`: Ollama server host (default: localhost)
- `OLLAMA_PORT`: Ollama server port (default: 11434)
- `MODEL_NAME`: Ollama model name (default: mistral)
- `CONSTRUCTION_DB_PATH`: Path to construction materials database

### Knowledge Base
The assistant uses a comprehensive knowledge base including:
- UK construction standards and regulations
- Material specifications and suppliers
- Tender document templates
- RFD processing guidelines
- Project management best practices

## 📚 Documentation

For detailed technical documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

## ⚠️ Important Disclaimer

This construction assistant is for informational and planning purposes only. It is not a substitute for professional construction advice, engineering consultation, or legal guidance. Always consult with qualified construction professionals, architects, engineers, and legal experts for your specific project requirements.
