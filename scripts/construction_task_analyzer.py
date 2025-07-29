#!/usr/bin/env python3
"""
Construction Task Analyzer for TaskCheck Assistant
Analyzes construction tasks and provides material sourcing, timeline, and cost recommendations
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('construction_task_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    COMPLEX = "complex"

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

class ConstructionTaskAnalyzer:
    def __init__(self):
        """Initialize construction task analyzer with UK construction knowledge"""
        self.task_patterns = self._load_task_patterns()
        self.material_mapping = self._load_material_mapping()
        self.regulatory_requirements = self._load_regulatory_requirements()
        self.supplier_database = self._load_supplier_database()
    
    def _load_task_patterns(self) -> Dict[str, Dict]:
        """Load task patterns and requirements"""
        return {
            "residential_extension": {
                "patterns": [
                    r"residential extension", r"house extension", r"home extension",
                    r"single storey", r"double storey", r"loft conversion",
                    r"conservatory", r"garage conversion"
                ],
                "materials": [
                    "Concrete for foundations", "Steel for structural support",
                    "Timber for framing", "Bricks/blocks for walls",
                    "Roof tiles", "Insulation", "Windows and doors"
                ],
                "complexity": ComplexityLevel.MEDIUM,
                "timeline": "8-16 weeks",
                "cost_range": "£20,000-£80,000",
                "regulations": ["Building Regulations", "Planning Permission", "Party Wall Act"],
                "risks": ["Planning delays", "Structural issues", "Budget overruns"],
                "suppliers": ["Travis Perkins", "Wickes", "Jewson", "Local builders merchants"]
            },
            "commercial_building": {
                "patterns": [
                    r"commercial building", r"office building", r"retail space",
                    r"warehouse", r"industrial unit", r"commercial development"
                ],
                "materials": [
                    "Steel frame", "Concrete slabs", "Glass curtain walling",
                    "HVAC systems", "Electrical systems", "Fire protection"
                ],
                "complexity": ComplexityLevel.HIGH,
                "timeline": "6-18 months",
                "cost_range": "£500,000-£5,000,000",
                "regulations": ["Building Regulations", "Fire Safety", "CDM Regulations"],
                "risks": ["Complex planning", "Budget management", "Stakeholder coordination"],
                "suppliers": ["British Steel", "CEMEX", "Kingspan", "Specialist contractors"]
            },
            "foundation_work": {
                "patterns": [
                    r"foundation", r"footings", r"piling", r"groundwork",
                    r"excavation", r"substructure"
                ],
                "materials": [
                    "Concrete", "Steel reinforcement", "Damp proofing",
                    "Insulation", "Drainage systems"
                ],
                "complexity": ComplexityLevel.MEDIUM,
                "timeline": "2-8 weeks",
                "cost_range": "£10,000-£50,000",
                "regulations": ["Building Regulations Part A", "Ground conditions"],
                "risks": ["Ground conditions", "Weather delays", "Structural integrity"],
                "suppliers": ["Hanson", "CEMEX", "Tarmac", "Local concrete suppliers"]
            },
            "roofing": {
                "patterns": [
                    r"roofing", r"roof", r"tiles", r"slate", r"flat roof",
                    r"pitched roof", r"roof replacement"
                ],
                "materials": [
                    "Roof tiles", "Slate", "Membrane", "Insulation",
                    "Gutters and downpipes", "Roof windows"
                ],
                "complexity": ComplexityLevel.MEDIUM,
                "timeline": "1-4 weeks",
                "cost_range": "£5,000-£25,000",
                "regulations": ["Building Regulations Part L", "Weather resistance"],
                "risks": ["Weather delays", "Access issues", "Structural integrity"],
                "suppliers": ["Marley", "Redland", "Sika", "Local roofing suppliers"]
            },
            "electrical_work": {
                "patterns": [
                    r"electrical", r"wiring", r"consumer unit", r"lighting",
                    r"power", r"electrical installation"
                ],
                "materials": [
                    "Cables", "Consumer units", "Sockets and switches",
                    "Lighting fixtures", "Circuit breakers"
                ],
                "complexity": ComplexityLevel.MEDIUM,
                "timeline": "1-3 weeks",
                "cost_range": "£2,000-£15,000",
                "regulations": ["IET Wiring Regulations", "Building Regulations Part P"],
                "risks": ["Safety hazards", "Compliance issues", "Integration problems"],
                "suppliers": ["Screwfix", "CEF", "Toolstation", "Electrical wholesalers"]
            },
            "plumbing": {
                "patterns": [
                    r"plumbing", r"pipes", r"heating", r"bathroom", r"kitchen",
                    r"water supply", r"drainage"
                ],
                "materials": [
                    "Copper pipes", "PEX pipes", "Fittings", "Boilers",
                    "Radiators", "Bathroom fixtures"
                ],
                "complexity": ComplexityLevel.MEDIUM,
                "timeline": "1-4 weeks",
                "cost_range": "£3,000-£20,000",
                "regulations": ["Water Regulations", "Building Regulations Part G"],
                "risks": ["Water damage", "Compliance issues", "Integration problems"],
                "suppliers": ["Wolseley", "Plumb Center", "Screwfix", "Plumbing merchants"]
            },
            "insulation": {
                "patterns": [
                    r"insulation", r"cavity wall", r"loft insulation",
                    r"thermal", r"energy efficiency"
                ],
                "materials": [
                    "Mineral wool", "PIR boards", "Phenolic foam",
                    "Spray foam", "Natural insulation"
                ],
                "complexity": ComplexityLevel.LOW,
                "timeline": "1-2 weeks",
                "cost_range": "£1,000-£8,000",
                "regulations": ["Building Regulations Part L", "Energy efficiency"],
                "risks": ["Moisture issues", "Installation quality", "Performance"],
                "suppliers": ["Kingspan", "Celotex", "Rockwool", "Insulation specialists"]
            },
            "windows_doors": {
                "patterns": [
                    r"windows", r"doors", r"glazing", r"uPVC", r"timber",
                    r"aluminium", r"composite"
                ],
                "materials": [
                    "uPVC frames", "Timber frames", "Aluminium frames",
                    "Double glazing", "Triple glazing", "Hardware"
                ],
                "complexity": ComplexityLevel.LOW,
                "timeline": "1-3 weeks",
                "cost_range": "£3,000-£20,000",
                "regulations": ["Building Regulations Part L", "FENSA requirements"],
                "risks": ["Installation quality", "Energy performance", "Security"],
                "suppliers": ["Anglian", "Everest", "Safestyle", "Local installers"]
            },
            "flooring": {
                "patterns": [
                    r"flooring", r"floor", r"carpet", r"laminate", r"hardwood",
                    r"vinyl", r"tiles"
                ],
                "materials": [
                    "Hardwood", "Engineered wood", "Laminate", "Vinyl",
                    "Carpet", "Ceramic tiles"
                ],
                "complexity": ComplexityLevel.LOW,
                "timeline": "1-2 weeks",
                "cost_range": "£2,000-£15,000",
                "regulations": ["Building Regulations Part M", "Slip resistance"],
                "risks": ["Installation quality", "Moisture issues", "Durability"],
                "suppliers": ["Tarkett", "Forbo", "Interface", "Flooring specialists"]
            },
            "demolition": {
                "patterns": [
                    r"demolition", r"demolish", r"knock down", r"strip out",
                    r"clearance", r"removal"
                ],
                "materials": [
                    "Demolition equipment", "Waste containers", "Safety equipment",
                    "Recycling facilities"
                ],
                "complexity": ComplexityLevel.MEDIUM,
                "timeline": "1-4 weeks",
                "cost_range": "£5,000-£50,000",
                "regulations": ["CDM Regulations", "Waste management", "Asbestos"],
                "risks": ["Structural collapse", "Environmental hazards", "Waste disposal"],
                "suppliers": ["Demolition contractors", "Waste management", "Safety equipment"]
            }
        }
    
    def _load_material_mapping(self) -> Dict[str, str]:
        """Load material descriptions"""
        return {
            "Concrete": "Structural material for foundations and slabs",
            "Steel": "Structural material for frames and reinforcement",
            "Timber": "Natural material for framing and finishing",
            "Bricks": "Traditional building material for walls",
            "Insulation": "Thermal and acoustic insulation materials",
            "Roof tiles": "Weather protection for pitched roofs",
            "Windows": "Glazed openings for light and ventilation",
            "Doors": "Access points with security and insulation",
            "Electrical": "Power and lighting systems",
            "Plumbing": "Water supply and drainage systems"
        }
    
    def _load_regulatory_requirements(self) -> Dict[str, List[str]]:
        """Load regulatory requirements by project type"""
        return {
            "residential": [
                "Building Regulations", "Planning Permission", "Party Wall Act",
                "Energy Performance Certificate", "Fire Safety"
            ],
            "commercial": [
                "Building Regulations", "CDM Regulations", "Fire Safety",
                "Accessibility", "Energy Performance"
            ],
            "industrial": [
                "Building Regulations", "CDM Regulations", "Health and Safety",
                "Environmental permits", "Fire Safety"
            ],
            "heritage": [
                "Listed Building Consent", "Conservation Area consent",
                "Heritage impact assessment", "Traditional building methods"
            ]
        }
    
    def _load_supplier_database(self) -> Dict[str, List[str]]:
        """Load supplier database by material type"""
        return {
            "concrete": ["Hanson", "CEMEX", "Tarmac", "Aggregate Industries"],
            "steel": ["British Steel", "Tata Steel", "ArcelorMittal"],
            "timber": ["James Latham", "Arnold Laver", "Travis Perkins"],
            "insulation": ["Kingspan", "Celotex", "Rockwool"],
            "roofing": ["Marley", "Redland", "Sandtoft"],
            "windows": ["Anglian", "Everest", "Safestyle"],
            "electrical": ["Screwfix", "CEF", "Toolstation"],
            "plumbing": ["Wolseley", "Plumb Center", "Screwfix"],
            "flooring": ["Tarkett", "Forbo", "Interface"]
        }
    
    def analyze_construction_task(self, task_description: str, project_type: Optional[str] = None) -> ConstructionTaskAnalysis:
        """
        Analyze construction task and provide recommendations
        
        Args:
            task_description: Text describing the construction task
            project_type: Type of project (residential, commercial, etc.)
            
        Returns:
            ConstructionTaskAnalysis object with recommendations
        """
        logger.info(f"Analyzing construction task: {task_description[:100]}...")
        logger.debug(f"Project type: {project_type}")
        
        task_description = task_description.lower()
        
        # Find matching task category
        matched_task = self._find_matching_task(task_description)
        logger.info(f"Matched task: {matched_task}")
        
        if not matched_task:
            # Default to general construction task
            return ConstructionTaskAnalysis(
                task_type="General construction",
                recommended_materials=["Standard construction materials"],
                complexity_level=ComplexityLevel.MEDIUM,
                estimated_timeline="4-12 weeks",
                cost_estimate="£10,000-£100,000",
                regulatory_requirements=["Building Regulations", "Health and Safety"],
                risk_factors=["Project complexity", "Budget management", "Timeline delays"],
                supplier_recommendations=["Local builders merchants", "Specialist contractors"]
            )
        
        task_info = self.task_patterns[matched_task]
        
        # Adjust complexity based on project type and specific requirements
        complexity_level = self._assess_complexity(task_description, task_info["complexity"])
        
        # Generate recommendations
        regulatory_requirements = self._get_regulatory_requirements(matched_task, project_type)
        risk_factors = self._assess_risks(task_description, matched_task)
        supplier_recommendations = self._get_supplier_recommendations(task_info["materials"])
        
        return ConstructionTaskAnalysis(
            task_type=matched_task.replace('_', ' ').title(),
            recommended_materials=task_info["materials"],
            complexity_level=complexity_level,
            estimated_timeline=task_info["timeline"],
            cost_estimate=task_info["cost_range"],
            regulatory_requirements=regulatory_requirements,
            risk_factors=risk_factors,
            supplier_recommendations=supplier_recommendations
        )
    
    def _assess_complexity(self, task_description: str, base_complexity: ComplexityLevel) -> ComplexityLevel:
        """Assess complexity level based on task description"""
        task_lower = task_description.lower()
        
        # Check for high complexity indicators
        high_complexity_indicators = [
            "complex", "large scale", "multi-storey", "high rise",
            "specialist", "innovative", "custom", "bespoke"
        ]
        
        for indicator in high_complexity_indicators:
            if indicator in task_lower:
                return ComplexityLevel.COMPLEX
        
        # Check for medium complexity indicators
        medium_complexity_indicators = [
            "extension", "renovation", "conversion", "modification",
            "structural", "foundation", "roofing"
        ]
        
        for indicator in medium_complexity_indicators:
            if indicator in task_lower:
                return ComplexityLevel.MEDIUM
        
        return base_complexity
    
    def _find_matching_task(self, task_description: str) -> Optional[str]:
        """Find the best matching task category"""
        best_match = None
        best_score = 0
        
        for task, info in self.task_patterns.items():
            score = 0
            for pattern in info["patterns"]:
                if re.search(pattern, task_description, re.IGNORECASE):
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = task
        
        return best_match
    
    def _get_regulatory_requirements(self, task_type: str, project_type: Optional[str]) -> List[str]:
        """Get regulatory requirements for task and project type"""
        requirements = []
        
        # Add task-specific requirements
        if task_type in self.task_patterns:
            requirements.extend(self.task_patterns[task_type]["regulations"])
        
        # Add project-type requirements
        if project_type and project_type in self.regulatory_requirements:
            requirements.extend(self.regulatory_requirements[project_type])
        
        return list(set(requirements))  # Remove duplicates
    
    def _assess_risks(self, task_description: str, task_type: str) -> List[str]:
        """Assess risks for the construction task"""
        risks = []
        
        # Add task-specific risks
        if task_type in self.task_patterns:
            risks.extend(self.task_patterns[task_type]["risks"])
        
        # Add general construction risks
        general_risks = [
            "Weather delays", "Material availability", "Cost overruns",
            "Timeline delays", "Quality control", "Safety hazards"
        ]
        
        risks.extend(general_risks)
        return list(set(risks))  # Remove duplicates
    
    def _get_supplier_recommendations(self, materials: List[str]) -> List[str]:
        """Get supplier recommendations based on materials"""
        suppliers = []
        
        for material in materials:
            material_lower = material.lower()
            
            # Map materials to supplier categories
            if "concrete" in material_lower:
                suppliers.extend(self.supplier_database.get("concrete", []))
            elif "steel" in material_lower:
                suppliers.extend(self.supplier_database.get("steel", []))
            elif "timber" in material_lower:
                suppliers.extend(self.supplier_database.get("timber", []))
            elif "insulation" in material_lower:
                suppliers.extend(self.supplier_database.get("insulation", []))
            elif "roof" in material_lower:
                suppliers.extend(self.supplier_database.get("roofing", []))
            elif "window" in material_lower or "door" in material_lower:
                suppliers.extend(self.supplier_database.get("windows", []))
            elif "electrical" in material_lower:
                suppliers.extend(self.supplier_database.get("electrical", []))
            elif "plumbing" in material_lower:
                suppliers.extend(self.supplier_database.get("plumbing", []))
            elif "floor" in material_lower:
                suppliers.extend(self.supplier_database.get("flooring", []))
        
        return list(set(suppliers))  # Remove duplicates
    
    def get_material_info(self, material: str) -> Dict[str, Any]:
        """Get detailed information about a construction material"""
        description = self.material_mapping.get(material, "Construction material")
        
        return {
            "material": material,
            "description": description,
            "common_applications": self._get_common_applications(material),
            "typical_cost": self._get_typical_cost(material),
            "suppliers": self._get_material_suppliers(material)
        }
    
    def _get_common_applications(self, material: str) -> List[str]:
        """Get common applications for a material"""
        application_map = {
            "Concrete": ["Foundations", "Structural elements", "Slabs", "Walls"],
            "Steel": ["Structural frames", "Reinforcement", "Connections"],
            "Timber": ["Framing", "Flooring", "Cladding", "Structural elements"],
            "Bricks": ["Walls", "Facades", "Partitions"],
            "Insulation": ["Cavity walls", "Roofs", "Floors", "External walls"],
            "Roof tiles": ["Pitched roofs", "Weather protection"],
            "Windows": ["Light and ventilation", "Energy efficiency"],
            "Doors": ["Access control", "Security", "Insulation"]
        }
        
        return application_map.get(material, ["Various applications"])
    
    def _get_typical_cost(self, material: str) -> str:
        """Get typical cost range for a material"""
        cost_map = {
            "Concrete": "£80-120 per cubic metre",
            "Steel": "£600-1200 per tonne",
            "Timber": "£20-80 per square metre",
            "Bricks": "£300-800 per 1000",
            "Insulation": "£8-25 per square metre",
            "Roof tiles": "£25-80 per square metre",
            "Windows": "£300-1500 per window",
            "Doors": "£200-2000 per door"
        }
        
        return cost_map.get(material, "Variable cost")
    
    def _get_material_suppliers(self, material: str) -> List[str]:
        """Get suppliers for a specific material"""
        material_lower = material.lower()
        
        if "concrete" in material_lower:
            return self.supplier_database.get("concrete", [])
        elif "steel" in material_lower:
            return self.supplier_database.get("steel", [])
        elif "timber" in material_lower:
            return self.supplier_database.get("timber", [])
        elif "insulation" in material_lower:
            return self.supplier_database.get("insulation", [])
        elif "roof" in material_lower:
            return self.supplier_database.get("roofing", [])
        elif "window" in material_lower or "door" in material_lower:
            return self.supplier_database.get("windows", [])
        elif "electrical" in material_lower:
            return self.supplier_database.get("electrical", [])
        elif "plumbing" in material_lower:
            return self.supplier_database.get("plumbing", [])
        elif "floor" in material_lower:
            return self.supplier_database.get("flooring", [])
        
        return ["Various suppliers"]

# Global instance
construction_task_analyzer = None

def get_construction_task_analyzer():
    """Get or create construction task analyzer instance"""
    global construction_task_analyzer
    if construction_task_analyzer is None:
        construction_task_analyzer = ConstructionTaskAnalyzer()
    return construction_task_analyzer

if __name__ == "__main__":
    # Test the construction task analyzer
    analyzer = ConstructionTaskAnalyzer()
    
    # Test cases
    test_cases = [
        "I need materials for a residential extension project",
        "How do I analyze a tender document for a commercial building?",
        "What are the requirements for foundation work?",
        "I need to replace the roof on my house"
    ]
    
    for task in test_cases:
        print(f"\nTask: {task}")
        analysis = analyzer.analyze_construction_task(task)
        print(f"Task Type: {analysis.task_type}")
        print(f"Recommended Materials: {analysis.recommended_materials[:3]}...")
        print(f"Complexity: {analysis.complexity_level.value}")
        print(f"Timeline: {analysis.estimated_timeline}")
        print(f"Cost Estimate: {analysis.cost_estimate}")
        print(f"Regulatory Requirements: {analysis.regulatory_requirements[:3]}...")
        print(f"Risk Factors: {analysis.risk_factors[:3]}...")
        print(f"Supplier Recommendations: {analysis.supplier_recommendations[:3]}...") 