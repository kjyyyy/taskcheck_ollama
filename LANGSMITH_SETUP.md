# 🏗️ LangSmith Integration for Construction TaskCheck Assistant

This guide explains how to set up and use LangSmith for evaluating and monitoring your construction assistant's performance.

## 📋 Table of Contents

1. [What is LangSmith?](#what-is-langsmith)
2. [Setup Instructions](#setup-instructions)
3. [Configuration](#configuration)
4. [Running Evaluations](#running-evaluations)
5. [Understanding Results](#understanding-results)
6. [API Endpoints](#api-endpoints)
7. [Troubleshooting](#troubleshooting)

## 🤔 What is LangSmith?

LangSmith is a platform for debugging, testing, evaluating, and monitoring LLM applications. For your construction assistant, it provides:

- **Performance Tracking**: Monitor how well your assistant handles construction queries
- **Construction-Specific Metrics**: Evaluate material accuracy, regulatory compliance, cost realism
- **Trace Analysis**: See exactly how your RAG system processes construction documents
- **A/B Testing**: Compare different prompts and configurations
- **Production Monitoring**: Track real-world usage patterns

## 🚀 Setup Instructions

### Step 1: Get LangSmith API Key

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Sign up for a free account
3. Navigate to Settings → API Keys
4. Create a new API key
5. Copy the API key

### Step 2: Configure Environment Variables

Create a `.env` file in your `taskcheck_ollama` directory:

```bash
# Copy the example file
cp env.example .env

# Edit the file with your API key
nano .env
```

Update the following variables in your `.env` file:

```env
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=construction-taskcheck
```

### Step 3: Install Dependencies

```bash
# Install LangSmith and other dependencies
pip install -r requirements.txt
```

### Step 4: Verify Setup

```bash
# Test LangSmith connection
python run_langsmith_evaluation.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGCHAIN_API_KEY` | Your LangSmith API key | Required |
| `LANGCHAIN_PROJECT` | Project name in LangSmith | `construction-taskcheck` |
| `LANGCHAIN_TRACING_V2` | Enable tracing | `true` |
| `LANGCHAIN_ENDPOINT` | LangSmith API endpoint | `https://api.smith.langchain.com` |

### Construction-Specific Configuration

The system automatically tracks construction-specific metrics:

- **Material Accuracy**: How well it recommends appropriate materials
- **Cost Realism**: Whether cost estimates are realistic for UK construction
- **Regulatory Compliance**: Accuracy of UK building regulations references
- **Task Analysis**: Quality of construction task classification
- **Response Relevance**: How well responses match construction queries

## 📊 Running Evaluations

### Method 1: Command Line

```bash
# Run comprehensive evaluation
python run_langsmith_evaluation.py
```

### Method 2: API Endpoint

```bash
# Start the Flask app
python webapp/app.py

# Run evaluation via API
curl -X POST http://localhost:5000/evaluate
```

### Method 3: Python Script

```python
from scripts.construction_langsmith_evaluator import get_construction_langsmith_evaluator
from scripts.construction_rag_chat import get_construction_rag_chat

# Initialize components
evaluator = get_construction_langsmith_evaluator()
rag_chat = get_construction_rag_chat()

# Run evaluation
results = evaluator.run_evaluation(rag_chat)

# Save results
evaluator.save_results(results, "my_evaluation_results.json")
```

## 📈 Understanding Results

### Evaluation Metrics

The system evaluates your construction assistant on 10 test cases across different categories:

#### **Material Sourcing Tests**
- Residential extension materials
- Commercial building materials
- Foundation work materials
- Heritage building materials

#### **Document Analysis Tests**
- Tender document analysis
- RFD processing requirements
- Regulatory compliance queries

#### **Technical Tests**
- Electrical work materials
- Plumbing requirements
- Insulation specifications
- Windows and doors

### Score Interpretation

| Score Range | Performance | Recommendations |
|-------------|-------------|-----------------|
| 0.8 - 1.0 | 🎉 Excellent | Consider advanced features |
| 0.6 - 0.8 | ⚠️ Good | Optimize prompts and context |
| 0.4 - 0.6 | ⚠️ Fair | Add more construction context |
| 0.0 - 0.4 | ❌ Poor | Major improvements needed |

### Key Metrics Explained

#### **Material Accuracy (25% weight)**
- **What it measures**: How well the assistant recommends appropriate materials
- **Example**: For a residential extension, does it mention concrete, steel, timber, bricks?
- **Good score**: >0.8

#### **Cost Realism (15% weight)**
- **What it measures**: Whether cost estimates are realistic for UK construction
- **Example**: Does it provide realistic cost ranges for different project types?
- **Good score**: >0.7

#### **Regulatory Accuracy (20% weight)**
- **What it measures**: Accuracy of UK building regulations references
- **Example**: Does it correctly reference Building Regulations, CDM, etc.?
- **Good score**: >0.9

#### **Response Relevance (15% weight)**
- **What it measures**: How well responses match construction queries
- **Example**: Does the answer address the specific construction question?
- **Good score**: >0.8

#### **Task Analysis Accuracy (15% weight)**
- **What it measures**: Quality of construction task classification
- **Example**: Does it correctly identify project type and complexity?
- **Good score**: >0.7

## 🔌 API Endpoints

### Evaluation Endpoints

#### `POST /evaluate`
Run a comprehensive evaluation of the construction assistant.

**Request:**
```json
{
  "evaluation_type": "comprehensive"
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "total_tests": 10,
    "successful_tests": 9,
    "success_rate": 0.9,
    "overall_score": 0.85,
    "results": [...]
  },
  "message": "Evaluation completed successfully"
}
```

#### `GET /langsmith-status`
Check LangSmith configuration status.

**Response:**
```json
{
  "langsmith_configured": true,
  "tracing_enabled": true,
  "project_name": "construction-taskcheck"
}
```

### Construction-Specific Endpoints

#### `GET /materials`
Get available construction materials.

#### `GET /materials/<material_name>`
Get detailed information about a specific material.

#### `GET /tasks`
Get available construction task types.

## 📊 LangSmith Dashboard

### Accessing Your Project

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Navigate to your project: `construction-taskcheck`
3. View traces, runs, and evaluations

### Key Dashboard Features

#### **Traces**
- See individual query processing
- View construction-specific metadata
- Analyze response quality

#### **Evaluations**
- View evaluation results
- Compare different configurations
- Track performance over time

#### **Datasets**
- Manage test cases
- Add new construction scenarios
- Version control your test data

## 🔧 Troubleshooting

### Common Issues

#### **"LangSmith API key not found"**
```bash
# Check your .env file
cat .env | grep LANGCHAIN_API_KEY

# Verify the key is set
echo $LANGCHAIN_API_KEY
```

#### **"Evaluation failed"**
```bash
# Check if Ollama is running
ollama list

# Check if the model is available
ollama pull mistral
```

#### **"Import error"**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import langsmith; print('LangSmith imported successfully')"
```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment variable
export EVAL_LOG_LEVEL=DEBUG

# Run evaluation with debug output
python run_langsmith_evaluation.py
```

### Manual Testing

Test individual components:

```python
# Test LangSmith connection
from langsmith import Client
client = Client()
print("LangSmith connection successful")

# Test RAG system
from scripts.construction_rag_chat import get_construction_rag_chat
rag_chat = get_construction_rag_chat()
response = rag_chat.ask("What materials do I need for a residential extension?")
print(f"Response: {response['answer'][:100]}...")
```

## 📈 Performance Optimization

### Improving Scores

#### **Material Accuracy**
- Add more material specifications to context files
- Include supplier information and costs
- Add regional variations for UK construction

#### **Cost Realism**
- Update cost estimates in context files
- Include inflation factors
- Add regional cost variations

#### **Regulatory Compliance**
- Keep building regulations up to date
- Add more regulatory references
- Include compliance checklists

#### **Response Relevance**
- Optimize prompts for construction queries
- Improve context retrieval
- Add construction-specific examples

### Advanced Features

#### **Custom Evaluators**
```python
# Add custom construction evaluators
def evaluate_heritage_compliance(response, expected_regulations):
    """Evaluate heritage building compliance"""
    # Custom logic for heritage projects
    pass
```

#### **Multi-Modal Evaluation**
```python
# Future: Evaluate blueprints and technical drawings
def evaluate_blueprint_understanding(response, blueprint_image):
    """Evaluate understanding of construction drawings"""
    # Use vision models for blueprint analysis
    pass
```

## 🚀 Next Steps

1. **Run Initial Evaluation**: `python run_langsmith_evaluation.py`
2. **Review Results**: Check the generated report and LangSmith dashboard
3. **Optimize Performance**: Based on results, improve prompts and context
4. **Set Up Monitoring**: Configure production monitoring for real-world usage
5. **Add Custom Tests**: Create construction-specific test cases for your use cases

## 📞 Support

- **LangSmith Documentation**: [https://docs.smith.langchain.com/](https://docs.smith.langchain.com/)
- **Construction Assistant Issues**: Check the project repository
- **Community**: Join LangChain Discord for support

---

**⚠️ Important**: This evaluation system is designed specifically for construction use cases. Always validate results with construction professionals for critical decisions. 