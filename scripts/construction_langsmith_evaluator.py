#!/usr/bin/env python3
"""
Construction LangSmith Evaluator
Evaluates the performance of the construction assistant using LangSmith
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import re

from langsmith import Client
from langchain.smith import RunEvalConfig
from langchain.evaluation import EvaluatorType
from langchain.evaluation.criteria import Criteria

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('construction_langsmith_eval.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ConstructionTestCase:
    """Test case for construction assistant evaluation"""
    category: str
    question: str
    expected_materials: List[str]
    expected_cost_range: str
    expected_timeline: str
    expected_regulations: List[str]
    expected_risks: List[str]
    description: str
    complexity: str  # low, medium, high

@dataclass
class ConstructionEvaluationResult:
    """Result of construction evaluation"""
    test_case: ConstructionTestCase
    response: str
    material_accuracy: float
    cost_realism: float
    regulatory_accuracy: float
    response_relevance: float
    task_analysis_accuracy: float
    context_precision: float
    context_recall: float
    overall_score: float
    metadata: Dict[str, Any]

class ConstructionLangSmithEvaluator:
    def __init__(self, langsmith_api_key: Optional[str] = None):
        """
        Initialize construction LangSmith evaluator
        
        Args:
            langsmith_api_key: LangSmith API key (optional, can use env var)
        """
        self.setup_langsmith(langsmith_api_key)
        self.test_cases = self._load_construction_test_cases()
        self.results = []
        
    def setup_langsmith(self, api_key: Optional[str] = None):
        """Setup LangSmith configuration"""
        if api_key:
            os.environ["LANGCHAIN_API_KEY"] = api_key
        
        # Set LangSmith environment variables
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_PROJECT"] = "construction-taskcheck"
        
        # Initialize LangSmith client
        try:
            self.client = Client()
            logger.info("✅ LangSmith client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LangSmith client: {e}")
            self.client = None
    
    def _load_construction_test_cases(self) -> List[ConstructionTestCase]:
        """Load construction-specific test cases"""
        return [
            ConstructionTestCase(
                category="material_sourcing",
                question="What materials do I need for a residential extension?",
                expected_materials=["concrete", "steel", "timber", "bricks", "insulation"],
                expected_cost_range="£20,000-£80,000",
                expected_timeline="8-16 weeks",
                expected_regulations=["Building Regulations", "Planning Permission"],
                expected_risks=["planning delays", "budget overruns"],
                description="Basic material sourcing for residential project",
                complexity="medium"
            ),
            ConstructionTestCase(
                category="material_sourcing",
                question="I need materials for foundation work on a commercial building",
                expected_materials=["concrete", "steel", "reinforcement", "damp proofing"],
                expected_cost_range="£50,000-£200,000",
                expected_timeline="4-12 weeks",
                expected_regulations=["Building Regulations Part A", "Ground conditions"],
                expected_risks=["ground conditions", "structural issues"],
                description="Foundation materials for commercial project",
                complexity="high"
            ),
            ConstructionTestCase(
                category="tender_analysis",
                question="How do I analyze a tender document for a commercial building project?",
                expected_materials=[],  # Not applicable for tender analysis
                expected_cost_range="",  # Not applicable
                expected_timeline="",    # Not applicable
                expected_regulations=["CDM Regulations", "Fire Safety"],
                expected_risks=["complex planning", "budget management"],
                description="Tender document analysis guidance",
                complexity="high"
            ),
            ConstructionTestCase(
                category="rfd_processing",
                question="What are the key requirements for an RFD submission?",
                expected_materials=[],  # Not applicable
                expected_cost_range="",  # Not applicable
                expected_timeline="",    # Not applicable
                expected_regulations=["Documentation standards", "Compliance requirements"],
                expected_risks=["incomplete documentation", "compliance issues"],
                description="RFD processing requirements",
                complexity="medium"
            ),
            ConstructionTestCase(
                category="regulatory_compliance",
                question="What are the UK building regulations for foundations?",
                expected_materials=["concrete", "steel", "damp proofing"],
                expected_cost_range="£10,000-£50,000",
                expected_timeline="2-8 weeks",
                expected_regulations=["Building Regulations Part A", "BS EN 206-1"],
                expected_risks=["ground conditions", "structural integrity"],
                description="Regulatory compliance for foundations",
                complexity="medium"
            ),
            ConstructionTestCase(
                category="material_sourcing",
                question="I need roofing materials for a heritage building",
                expected_materials=["slate", "lead", "copper", "traditional tiles"],
                expected_cost_range="£15,000-£60,000",
                expected_timeline="3-10 weeks",
                expected_regulations=["Heritage regulations", "Planning permission"],
                expected_risks=["heritage constraints", "material availability"],
                description="Heritage building roofing materials",
                complexity="high"
            ),
            ConstructionTestCase(
                category="electrical_work",
                question="What electrical materials do I need for a new build house?",
                expected_materials=["consumer unit", "cables", "sockets", "lighting"],
                expected_cost_range="£8,000-£25,000",
                expected_timeline="2-6 weeks",
                expected_regulations=["IET Wiring Regulations", "Building Regulations Part P"],
                expected_risks=["electrical safety", "compliance issues"],
                description="Electrical materials for new build",
                complexity="medium"
            ),
            ConstructionTestCase(
                category="plumbing",
                question="What plumbing materials are required for a bathroom renovation?",
                expected_materials=["pipes", "fittings", "bathroom suite", "tiles"],
                expected_cost_range="£5,000-£20,000",
                expected_timeline="2-4 weeks",
                expected_regulations=["Water Regulations", "Building Regulations"],
                expected_risks=["water damage", "compliance issues"],
                description="Plumbing materials for bathroom",
                complexity="medium"
            ),
            ConstructionTestCase(
                category="insulation",
                question="What insulation materials do I need for cavity wall insulation?",
                expected_materials=["cavity wall insulation", "mineral wool", "polystyrene"],
                expected_cost_range="£3,000-£12,000",
                expected_timeline="1-3 weeks",
                expected_regulations=["Building Regulations Part L", "Energy efficiency"],
                expected_risks=["moisture issues", "thermal performance"],
                description="Cavity wall insulation materials",
                complexity="low"
            ),
            ConstructionTestCase(
                category="windows_doors",
                question="What are the energy efficiency requirements for windows?",
                expected_materials=["double glazing", "low-e glass", "thermal breaks"],
                expected_cost_range="£4,000-£15,000",
                expected_timeline="1-3 weeks",
                expected_regulations=["Building Regulations Part L", "Energy Performance"],
                expected_risks=["thermal performance", "security standards"],
                description="Energy efficiency for windows",
                complexity="medium"
            )
        ]
    
    def extract_materials_from_response(self, response: str) -> List[str]:
        """Extract materials mentioned in the response"""
        # Common construction materials
        material_keywords = [
            "concrete", "steel", "timber", "bricks", "insulation", "roof tiles",
            "windows", "doors", "plumbing", "electrical", "flooring", "paint",
            "render", "plaster", "cement", "slate", "lead", "copper", "tiles",
            "consumer unit", "cables", "sockets", "lighting", "pipes", "fittings",
            "bathroom suite", "cavity wall insulation", "mineral wool", "polystyrene",
            "double glazing", "low-e glass", "thermal breaks", "reinforcement",
            "damp proofing", "traditional tiles"
        ]
        
        response_lower = response.lower()
        found_materials = []
        
        for material in material_keywords:
            if material in response_lower:
                found_materials.append(material)
        
        return found_materials
    
    def extract_cost_from_response(self, response: str) -> Optional[str]:
        """Extract cost information from response"""
        # Look for cost patterns
        cost_patterns = [
            r'£[\d,]+(?:\.\d{2})?',
            r'\$[\d,]+(?:\.\d{2})?',
            r'cost[:\s]+([^\n]+)',
            r'budget[:\s]+([^\n]+)',
            r'estimated[:\s]+([^\n]+)',
            r'price[:\s]+([^\n]+)'
        ]
        
        for pattern in cost_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(0) if '£' in pattern or '$' in pattern else match.group(1).strip()
        
        return None
    
    def extract_timeline_from_response(self, response: str) -> Optional[str]:
        """Extract timeline information from response"""
        # Look for timeline patterns
        timeline_patterns = [
            r'\d+\s*(?:weeks?|months?|days?)',
            r'timeline[:\s]+([^\n]+)',
            r'duration[:\s]+([^\n]+)',
            r'completion[:\s]+([^\n]+)',
            r'deadline[:\s]+([^\n]+)'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(0) if 'weeks?' in pattern or 'months?' in pattern or 'days?' in pattern else match.group(1).strip()
        
        return None
    
    def extract_regulations_from_response(self, response: str) -> List[str]:
        """Extract regulatory references from response"""
        # UK construction regulations
        regulation_keywords = [
            "building regulations", "planning permission", "cdm regulations",
            "fire safety", "party wall act", "health and safety",
            "environmental impact assessment", "breeam", "energy performance",
            "iet wiring regulations", "water regulations", "heritage regulations",
            "bs en 206-1", "bs 8500", "part a", "part l", "part p"
        ]
        
        response_lower = response.lower()
        found_regulations = []
        
        for regulation in regulation_keywords:
            if regulation in response_lower:
                found_regulations.append(regulation)
        
        return found_regulations
    
    def extract_risks_from_response(self, response: str) -> List[str]:
        """Extract risk factors from response"""
        # Common construction risks
        risk_keywords = [
            "risk", "hazard", "safety", "delay", "cost overrun",
            "weather", "ground conditions", "structural", "access",
            "planning delays", "budget overruns", "compliance issues",
            "heritage constraints", "material availability", "electrical safety",
            "water damage", "moisture issues", "thermal performance",
            "security standards"
        ]
        
        response_lower = response.lower()
        found_risks = []
        
        for risk in risk_keywords:
            if risk in response_lower:
                found_risks.append(risk)
        
        return found_risks
    
    def evaluate_material_accuracy(self, response: str, expected_materials: List[str]) -> float:
        """Evaluate material recommendation accuracy"""
        if not expected_materials:
            return 1.0  # No materials expected for this test case
        
        found_materials = self.extract_materials_from_response(response)
        
        if not found_materials:
            return 0.0
        
        # Calculate precision and recall
        correct_materials = set(found_materials) & set(expected_materials)
        precision = len(correct_materials) / len(found_materials) if found_materials else 0
        recall = len(correct_materials) / len(expected_materials) if expected_materials else 0
        
        # F1 score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return f1_score
    
    def evaluate_cost_realism(self, response: str, expected_range: str) -> float:
        """Evaluate cost estimate realism"""
        if not expected_range:
            return 1.0  # No cost expected for this test case
        
        extracted_cost = self.extract_cost_from_response(response)
        
        if not extracted_cost:
            return 0.0
        
        # Simple heuristic: check if cost is mentioned and seems reasonable
        # In a real implementation, you'd want more sophisticated cost analysis
        return 0.8 if extracted_cost else 0.0
    
    def evaluate_regulatory_accuracy(self, response: str, expected_regulations: List[str]) -> float:
        """Evaluate regulatory reference accuracy"""
        if not expected_regulations:
            return 1.0  # No regulations expected for this test case
        
        found_regulations = self.extract_regulations_from_response(response)
        
        if not found_regulations:
            return 0.0
        
        # Calculate precision and recall
        correct_regulations = set(found_regulations) & set(expected_regulations)
        precision = len(correct_regulations) / len(found_regulations) if found_regulations else 0
        recall = len(correct_regulations) / len(expected_regulations) if expected_regulations else 0
        
        # F1 score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return f1_score
    
    def evaluate_response_relevance(self, response: str, question: str) -> float:
        """Evaluate response relevance to the question"""
        # Simple heuristic: check if response contains relevant keywords
        question_lower = question.lower()
        response_lower = response.lower()
        
        # Extract key terms from question
        key_terms = []
        if "materials" in question_lower:
            key_terms.extend(["material", "supplier", "cost", "specification"])
        if "tender" in question_lower:
            key_terms.extend(["tender", "requirement", "deadline", "specification"])
        if "rfd" in question_lower:
            key_terms.extend(["document", "requirement", "submission", "compliance"])
        if "regulation" in question_lower:
            key_terms.extend(["regulation", "compliance", "standard", "requirement"])
        
        if not key_terms:
            return 0.8  # Default score if no specific terms found
        
        # Check how many key terms are mentioned in response
        mentioned_terms = sum(1 for term in key_terms if term in response_lower)
        relevance_score = mentioned_terms / len(key_terms)
        
        return relevance_score
    
    def evaluate_task_analysis_accuracy(self, response: str, test_case: ConstructionTestCase) -> float:
        """Evaluate task analysis accuracy"""
        # Check if response mentions appropriate complexity, timeline, and risks
        response_lower = response.lower()
        
        # Check for complexity indicators
        complexity_indicators = {
            "low": ["simple", "straightforward", "basic"],
            "medium": ["moderate", "standard", "typical"],
            "high": ["complex", "challenging", "difficult", "specialist"]
        }
        
        complexity_score = 0.0
        expected_complexity = test_case.complexity
        indicators = complexity_indicators.get(expected_complexity, [])
        
        for indicator in indicators:
            if indicator in response_lower:
                complexity_score = 1.0
                break
        
        # Check for timeline mention
        timeline_score = 1.0 if self.extract_timeline_from_response(response) else 0.0
        
        # Check for risk mention
        risk_score = 1.0 if self.extract_risks_from_response(response) else 0.0
        
        # Average of complexity, timeline, and risk scores
        return (complexity_score + timeline_score + risk_score) / 3
    
    def evaluate_context_precision(self, response: str, test_case: ConstructionTestCase) -> float:
        """Evaluate context retrieval precision"""
        # This would typically be evaluated by LangSmith's built-in evaluators
        # For now, we'll use a simple heuristic based on response quality
        response_length = len(response)
        if response_length < 50:
            return 0.0  # Too short to be useful
        elif response_length < 200:
            return 0.5  # Somewhat useful
        else:
            return 0.8  # Likely contains detailed information
    
    def evaluate_context_recall(self, response: str, test_case: ConstructionTestCase) -> float:
        """Evaluate context retrieval recall"""
        # Check if response covers the main aspects of the test case
        response_lower = response.lower()
        
        # Check for material mentions (if applicable)
        material_score = 1.0
        if test_case.expected_materials:
            found_materials = self.extract_materials_from_response(response)
            if found_materials:
                material_score = len(set(found_materials) & set(test_case.expected_materials)) / len(test_case.expected_materials)
            else:
                material_score = 0.0
        
        # Check for regulation mentions (if applicable)
        regulation_score = 1.0
        if test_case.expected_regulations:
            found_regulations = self.extract_regulations_from_response(response)
            if found_regulations:
                regulation_score = len(set(found_regulations) & set(test_case.expected_regulations)) / len(test_case.expected_regulations)
            else:
                regulation_score = 0.0
        
        # Average of material and regulation scores
        return (material_score + regulation_score) / 2
    
    def evaluate_test_case(self, test_case: ConstructionTestCase, response: str) -> ConstructionEvaluationResult:
        """Evaluate a single test case"""
        logger.info(f"Evaluating test case: {test_case.category} - {test_case.description}")
        
        # Calculate individual metrics
        material_accuracy = self.evaluate_material_accuracy(response, test_case.expected_materials)
        cost_realism = self.evaluate_cost_realism(response, test_case.expected_cost_range)
        regulatory_accuracy = self.evaluate_regulatory_accuracy(response, test_case.expected_regulations)
        response_relevance = self.evaluate_response_relevance(response, test_case.question)
        task_analysis_accuracy = self.evaluate_task_analysis_accuracy(response, test_case)
        context_precision = self.evaluate_context_precision(response, test_case)
        context_recall = self.evaluate_context_recall(response, test_case)
        
        # Calculate overall score (weighted average)
        weights = {
            'material_accuracy': 0.25,
            'cost_realism': 0.15,
            'regulatory_accuracy': 0.20,
            'response_relevance': 0.15,
            'task_analysis_accuracy': 0.15,
            'context_precision': 0.05,
            'context_recall': 0.05
        }
        
        overall_score = (
            material_accuracy * weights['material_accuracy'] +
            cost_realism * weights['cost_realism'] +
            regulatory_accuracy * weights['regulatory_accuracy'] +
            response_relevance * weights['response_relevance'] +
            task_analysis_accuracy * weights['task_analysis_accuracy'] +
            context_precision * weights['context_precision'] +
            context_recall * weights['context_recall']
        )
        
        # Create metadata
        metadata = {
            "test_case_category": test_case.category,
            "test_case_complexity": test_case.complexity,
            "found_materials": self.extract_materials_from_response(response),
            "found_regulations": self.extract_regulations_from_response(response),
            "found_risks": self.extract_risks_from_response(response),
            "extracted_cost": self.extract_cost_from_response(response),
            "extracted_timeline": self.extract_timeline_from_response(response),
            "response_length": len(response)
        }
        
        return ConstructionEvaluationResult(
            test_case=test_case,
            response=response,
            material_accuracy=material_accuracy,
            cost_realism=cost_realism,
            regulatory_accuracy=regulatory_accuracy,
            response_relevance=response_relevance,
            task_analysis_accuracy=task_analysis_accuracy,
            context_precision=context_precision,
            context_recall=context_recall,
            overall_score=overall_score,
            metadata=metadata
        )
    
    def run_evaluation(self, rag_chat_instance) -> Dict[str, Any]:
        """Run the full evaluation"""
        logger.info("🏗️ Starting Construction LangSmith Evaluation")
        
        if not self.client:
            logger.error("❌ LangSmith client not available")
            return {"error": "LangSmith client not available"}
        
        results = []
        total_score = 0
        successful_tests = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"Running test {i}/{len(self.test_cases)}: {test_case.category} - {test_case.description}")
            
            try:
                # Get response from RAG system
                response = rag_chat_instance.ask(
                    test_case.question,
                    use_context=True,
                    analyze_task=True
                )
                
                if response and "answer" in response:
                    answer = response["answer"]
                    
                    # Evaluate the response
                    evaluation_result = self.evaluate_test_case(test_case, answer)
                    results.append(evaluation_result)
                    
                    successful_tests += 1
                    total_score += evaluation_result.overall_score
                    
                    logger.info(f"✅ Test {i} completed - Score: {evaluation_result.overall_score:.2f}")
                    logger.info(f"   Material Accuracy: {evaluation_result.material_accuracy:.2f}")
                    logger.info(f"   Regulatory Accuracy: {evaluation_result.regulatory_accuracy:.2f}")
                    logger.info(f"   Response Relevance: {evaluation_result.response_relevance:.2f}")
                    
                else:
                    logger.error(f"❌ Test {i} failed - No response received")
                    
            except Exception as e:
                logger.error(f"❌ Test {i} failed with error: {e}")
        
        # Calculate overall metrics
        overall_score = total_score / len(self.test_cases) if self.test_cases else 0
        success_rate = successful_tests / len(self.test_cases) if self.test_cases else 0
        
        # Generate summary
        summary = {
            "total_tests": len(self.test_cases),
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "overall_score": overall_score,
            "results": [self._result_to_dict(result) for result in results],
            "timestamp": datetime.now().isoformat()
        }
        
        # Log summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 CONSTRUCTION LANGSMITH EVALUATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Successful Tests: {summary['successful_tests']}")
        logger.info(f"Success Rate: {summary['success_rate']:.2%}")
        logger.info(f"Overall Score: {summary['overall_score']:.2f}")
        
        # Category breakdown
        categories = {}
        for result in results:
            category = result.test_case.category
            if category not in categories:
                categories[category] = {"count": 0, "score": 0}
            categories[category]["count"] += 1
            categories[category]["score"] += result.overall_score
        
        logger.info("\n📈 Category Breakdown:")
        for category, stats in categories.items():
            avg_score = stats["score"] / stats["count"]
            logger.info(f"{category}: {stats['count']} tests, avg score: {avg_score:.2f}")
        
        return summary
    
    def _result_to_dict(self, result: ConstructionEvaluationResult) -> Dict[str, Any]:
        """Convert evaluation result to dictionary"""
        return {
            "test_case": {
                "category": result.test_case.category,
                "question": result.test_case.question,
                "description": result.test_case.description,
                "complexity": result.test_case.complexity
            },
            "metrics": {
                "material_accuracy": result.material_accuracy,
                "cost_realism": result.cost_realism,
                "regulatory_accuracy": result.regulatory_accuracy,
                "response_relevance": result.response_relevance,
                "task_analysis_accuracy": result.task_analysis_accuracy,
                "context_precision": result.context_precision,
                "context_recall": result.context_recall,
                "overall_score": result.overall_score
            },
            "metadata": result.metadata
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = "construction_langsmith_results.json"):
        """Save evaluation results to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"✅ Results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable report"""
        report = f"""
# Construction LangSmith Evaluation Report

**Generated:** {results['timestamp']}
**Total Tests:** {results['total_tests']}
**Successful Tests:** {results['successful_tests']}
**Success Rate:** {results['success_rate']:.2%}
**Overall Score:** {results['overall_score']:.2f}

## Test Results

"""
        
        for i, result in enumerate(results['results'], 1):
            test_case = result['test_case']
            metrics = result['metrics']
            
            report += f"""
### Test {i}: {test_case['category']} - {test_case['description']}

**Question:** {test_case['question']}
**Complexity:** {test_case['complexity']}

**Metrics:**
- Material Accuracy: {metrics['material_accuracy']:.2f}
- Cost Realism: {metrics['cost_realism']:.2f}
- Regulatory Accuracy: {metrics['regulatory_accuracy']:.2f}
- Response Relevance: {metrics['response_relevance']:.2f}
- Task Analysis Accuracy: {metrics['task_analysis_accuracy']:.2f}
- Context Precision: {metrics['context_precision']:.2f}
- Context Recall: {metrics['context_recall']:.2f}
- Overall Score: {metrics['overall_score']:.2f}

"""
        
        return report

# Global instance
construction_langsmith_evaluator = None

def get_construction_langsmith_evaluator(langsmith_api_key: Optional[str] = None):
    """Get or create construction LangSmith evaluator instance"""
    global construction_langsmith_evaluator
    if construction_langsmith_evaluator is None:
        construction_langsmith_evaluator = ConstructionLangSmithEvaluator(langsmith_api_key)
    return construction_langsmith_evaluator

if __name__ == "__main__":
    # Test the evaluator
    evaluator = ConstructionLangSmithEvaluator()
    print(f"Loaded {len(evaluator.test_cases)} test cases")
    
    # Test a sample evaluation
    test_case = evaluator.test_cases[0]
    sample_response = "For a residential extension, you'll need concrete for foundations, steel for structural support, timber for framing, bricks for walls, and insulation for thermal performance."
    
    result = evaluator.evaluate_test_case(test_case, sample_response)
    print(f"Sample evaluation result: {result.overall_score:.2f}") 