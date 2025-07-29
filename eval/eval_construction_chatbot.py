#!/usr/bin/env python3
"""
Construction Chatbot Evaluation Script
Evaluates the performance of the construction assistant
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add scripts directory to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
scripts_dir = project_root / 'scripts'

if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('construction_eval.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConstructionChatbotEvaluator:
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        """
        Initialize construction chatbot evaluator
        
        Args:
            api_base_url: Base URL for the Flask API
        """
        self.api_base_url = api_base_url
        self.test_cases = self._load_test_cases()
        self.results = []
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases for construction assistant evaluation"""
        return [
            {
                "category": "Material Sourcing",
                "question": "What materials do I need for a residential extension?",
                "expected_keywords": ["concrete", "steel", "timber", "bricks", "insulation"],
                "expected_task_type": "residential_extension",
                "description": "Basic material sourcing for residential project"
            },
            {
                "category": "Material Sourcing",
                "question": "I need materials for foundation work on a commercial building",
                "expected_keywords": ["concrete", "steel", "foundation", "reinforcement"],
                "expected_task_type": "foundation_work",
                "description": "Foundation materials for commercial project"
            },
            {
                "category": "Tender Analysis",
                "question": "How do I analyze a tender document for a commercial building project?",
                "expected_keywords": ["tender", "requirements", "deadline", "specifications"],
                "expected_task_type": "commercial_building",
                "description": "Tender document analysis guidance"
            },
            {
                "category": "RFD Processing",
                "question": "What are the key requirements for an RFD submission?",
                "expected_keywords": ["rfd", "documents", "requirements", "submission"],
                "expected_task_type": "general_construction",
                "description": "RFD processing requirements"
            },
            {
                "category": "Project Management",
                "question": "What are the UK building regulations for foundations?",
                "expected_keywords": ["building regulations", "foundations", "compliance"],
                "expected_task_type": "foundation_work",
                "description": "Regulatory compliance for foundations"
            },
            {
                "category": "Material Sourcing",
                "question": "I need roofing materials for a heritage building",
                "expected_keywords": ["roof", "tiles", "slate", "heritage"],
                "expected_task_type": "roofing",
                "description": "Heritage building roofing materials"
            },
            {
                "category": "Electrical Work",
                "question": "What electrical materials do I need for a new build house?",
                "expected_keywords": ["electrical", "wiring", "consumer unit", "cables"],
                "expected_task_type": "electrical_work",
                "description": "Electrical materials for new build"
            },
            {
                "category": "Plumbing",
                "question": "What plumbing materials are required for a bathroom renovation?",
                "expected_keywords": ["plumbing", "pipes", "bathroom", "fixtures"],
                "expected_task_type": "plumbing",
                "description": "Plumbing materials for bathroom"
            },
            {
                "category": "Insulation",
                "question": "What insulation materials do I need for cavity wall insulation?",
                "expected_keywords": ["insulation", "cavity wall", "thermal", "energy"],
                "expected_task_type": "insulation",
                "description": "Cavity wall insulation materials"
            },
            {
                "category": "Windows and Doors",
                "question": "What are the energy efficiency requirements for windows?",
                "expected_keywords": ["windows", "energy efficiency", "glazing", "standards"],
                "expected_task_type": "windows_doors",
                "description": "Energy efficiency for windows"
            }
        ]
    
    def test_api_health(self) -> bool:
        """Test if the API is healthy"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API Health: {data.get('status', 'unknown')}")
                return data.get('status') in ['healthy', 'degraded']
            else:
                logger.error(f"API health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"API health check error: {e}")
            return False
    
    def test_basic_query(self, question: str, use_context: bool = True, analyze_task: bool = True) -> Dict[str, Any]:
        """Test a basic query to the construction assistant"""
        try:
            payload = {
                "question": question,
                "use_context": use_context,
                "analyze_task": analyze_task
            }
            
            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Query failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {"error": str(e)}
    
    def evaluate_response(self, response: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a response against expected criteria"""
        evaluation = {
            "test_case": test_case,
            "response_received": bool(response and "answer" in response),
            "has_error": "error" in response,
            "has_task_analysis": "task_analysis" in response,
            "keyword_matches": 0,
            "expected_keywords_found": [],
            "task_type_match": False,
            "response_quality_score": 0
        }
        
        if not evaluation["response_received"]:
            return evaluation
        
        # Check for expected keywords
        answer_lower = response["answer"].lower()
        for keyword in test_case["expected_keywords"]:
            if keyword.lower() in answer_lower:
                evaluation["expected_keywords_found"].append(keyword)
                evaluation["keyword_matches"] += 1
        
        # Check task analysis
        if evaluation["has_task_analysis"]:
            task_analysis = response["task_analysis"]
            expected_task = test_case["expected_task_type"]
            actual_task = task_analysis.get("task_type", "").lower()
            evaluation["task_type_match"] = expected_task in actual_task or actual_task in expected_task
        
        # Calculate response quality score
        total_keywords = len(test_case["expected_keywords"])
        if total_keywords > 0:
            keyword_score = evaluation["keyword_matches"] / total_keywords
        else:
            keyword_score = 0
        
        task_score = 1.0 if evaluation["task_type_match"] else 0.0
        analysis_score = 1.0 if evaluation["has_task_analysis"] else 0.0
        
        # Weighted quality score
        evaluation["response_quality_score"] = (
            keyword_score * 0.4 +
            task_score * 0.3 +
            analysis_score * 0.3
        )
        
        return evaluation
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run the full evaluation"""
        logger.info("🏗️ Starting Construction Chatbot Evaluation")
        
        # Test API health first
        if not self.test_api_health():
            logger.error("❌ API is not healthy. Cannot run evaluation.")
            return {"error": "API not healthy"}
        
        logger.info("✅ API is healthy. Running test cases...")
        
        results = []
        total_score = 0
        successful_tests = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"Running test {i}/{len(self.test_cases)}: {test_case['category']} - {test_case['description']}")
            
            # Test with context and task analysis
            response = self.test_basic_query(
                test_case["question"],
                use_context=True,
                analyze_task=True
            )
            
            # Evaluate response
            evaluation = self.evaluate_response(response, test_case)
            results.append(evaluation)
            
            if evaluation["response_received"] and not evaluation["has_error"]:
                successful_tests += 1
                total_score += evaluation["response_quality_score"]
                
                logger.info(f"✅ Test {i} passed - Score: {evaluation['response_quality_score']:.2f}")
                logger.info(f"   Keywords found: {evaluation['keyword_matches']}/{len(test_case['expected_keywords'])}")
                logger.info(f"   Task analysis: {'✅' if evaluation['has_task_analysis'] else '❌'}")
                logger.info(f"   Task type match: {'✅' if evaluation['task_type_match'] else '❌'}")
            else:
                logger.error(f"❌ Test {i} failed")
                if evaluation["has_error"]:
                    logger.error(f"   Error: {response.get('error', 'Unknown error')}")
        
        # Calculate overall metrics
        overall_score = total_score / len(self.test_cases) if self.test_cases else 0
        success_rate = successful_tests / len(self.test_cases) if self.test_cases else 0
        
        # Generate summary
        summary = {
            "total_tests": len(self.test_cases),
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "overall_score": overall_score,
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Log summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 EVALUATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Successful Tests: {summary['successful_tests']}")
        logger.info(f"Success Rate: {summary['success_rate']:.2%}")
        logger.info(f"Overall Score: {summary['overall_score']:.2f}")
        
        # Category breakdown
        categories = {}
        for result in results:
            category = result["test_case"]["category"]
            if category not in categories:
                categories[category] = {"count": 0, "score": 0}
            categories[category]["count"] += 1
            categories[category]["score"] += result["response_quality_score"]
        
        logger.info("\n📈 Category Breakdown:")
        for category, stats in categories.items():
            avg_score = stats["score"] / stats["count"]
            logger.info(f"{category}: {stats['count']} tests, avg score: {avg_score:.2f}")
        
        return summary
    
    def save_results(self, results: Dict[str, Any], filename: str = "construction_eval_results.json"):
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
# Construction Chatbot Evaluation Report

**Generated:** {results['timestamp']}
**Total Tests:** {results['total_tests']}
**Successful Tests:** {results['successful_tests']}
**Success Rate:** {results['success_rate']:.2%}
**Overall Score:** {results['overall_score']:.2f}

## Test Results

"""
        
        for i, result in enumerate(results['results'], 1):
            test_case = result['test_case']
            report += f"""
### Test {i}: {test_case['category']} - {test_case['description']}

**Question:** {test_case['question']}

**Status:** {'✅ PASS' if result['response_received'] and not result['has_error'] else '❌ FAIL'}

**Metrics:**
- Keywords Found: {result['keyword_matches']}/{len(test_case['expected_keywords'])}
- Task Analysis: {'✅' if result['has_task_analysis'] else '❌'}
- Task Type Match: {'✅' if result['task_type_match'] else '❌'}
- Quality Score: {result['response_quality_score']:.2f}

**Expected Keywords:** {', '.join(test_case['expected_keywords'])}
**Found Keywords:** {', '.join(result['expected_keywords_found'])}

"""
        
        # Category summary
        categories = {}
        for result in results['results']:
            category = result['test_case']['category']
            if category not in categories:
                categories[category] = {"count": 0, "score": 0, "passed": 0}
            categories[category]["count"] += 1
            categories[category]["score"] += result["response_quality_score"]
            if result['response_received'] and not result['has_error']:
                categories[category]["passed"] += 1
        
        report += """
## Category Summary

"""
        for category, stats in categories.items():
            avg_score = stats["score"] / stats["count"]
            pass_rate = stats["passed"] / stats["count"]
            report += f"- **{category}**: {stats['count']} tests, {stats['passed']} passed ({pass_rate:.1%}), avg score: {avg_score:.2f}\n"
        
        return report

def main():
    """Main evaluation function"""
    evaluator = ConstructionChatbotEvaluator()
    
    # Run evaluation
    results = evaluator.run_evaluation()
    
    if "error" in results:
        logger.error(f"Evaluation failed: {results['error']}")
        return
    
    # Save results
    evaluator.save_results(results)
    
    # Generate and save report
    report = evaluator.generate_report(results)
    with open("construction_eval_report.md", 'w') as f:
        f.write(report)
    
    logger.info("✅ Evaluation completed successfully!")
    logger.info("📄 Results saved to: construction_eval_results.json")
    logger.info("📄 Report saved to: construction_eval_report.md")

if __name__ == "__main__":
    main() 