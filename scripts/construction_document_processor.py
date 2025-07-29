#!/usr/bin/env python3
"""
Construction Document Processor for TaskCheck Assistant
Handles tender documents, RFDs, material specifications, and construction project documents
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import PyPDF2
from docx import Document
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('construction_document_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ConstructionDocumentData:
    """Structured data extracted from construction documents"""
    document_type: str
    project_title: str
    project_description: str
    timeline: str
    budget: str
    materials_required: List[str]
    technical_requirements: List[str]
    regulatory_requirements: List[str]
    risk_factors: List[str]
    key_dates: List[str]
    contact_info: Dict[str, str]
    specifications: Dict[str, Any]

class ConstructionDocumentProcessor:
    def __init__(self, openrouter_api_key: Optional[str] = None):
        """
        Initialize construction document processor
        
        Args:
            openrouter_api_key: API key for OpenRouter models (optional)
        """
        self.openrouter_api_key = openrouter_api_key
        self.supported_formats = ['pdf', 'docx', 'txt']
        
        # Document type patterns
        self.document_patterns = {
            'tender_document': {
                'patterns': [
                    r'tender', r'bid', r'proposal', r'request for proposal',
                    r'rfp', r'itt', r'invitation to tender'
                ],
                'extractors': [
                    self._extract_tender_requirements,
                    self._extract_project_specifications,
                    self._extract_timeline_and_budget
                ]
            },
            'rfd_request': {
                'patterns': [
                    r'request for documents', r'rfd', r'document request',
                    r'submission requirements', r'documentation needed'
                ],
                'extractors': [
                    self._extract_rfd_requirements,
                    self._extract_document_types,
                    self._extract_submission_deadlines
                ]
            },
            'material_specification': {
                'patterns': [
                    r'material spec', r'specification', r'materials required',
                    r'product data', r'technical specification'
                ],
                'extractors': [
                    self._extract_material_specifications,
                    self._extract_quality_standards,
                    self._extract_supplier_requirements
                ]
            },
            'project_plan': {
                'patterns': [
                    r'project plan', r'construction plan', r'methodology',
                    r'work schedule', r'project timeline'
                ],
                'extractors': [
                    self._extract_project_timeline,
                    self._extract_work_methodology,
                    self._extract_resource_requirements
                ]
            }
        }
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from file based on extension"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return self.extract_text_from_pdf(str(file_path))
        elif file_path.suffix.lower() == '.docx':
            return self.extract_text_from_docx(str(file_path))
        elif file_path.suffix.lower() == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading text file {file_path}: {e}")
                return ""
        else:
            logger.warning(f"Unsupported file format: {file_path.suffix}")
            return ""
    
    def parse_construction_document(self, text: str) -> ConstructionDocumentData:
        """
        Parse construction document text and extract structured data
        
        Args:
            text: Document text content
            
        Returns:
            ConstructionDocumentData object with extracted information
        """
        logger.info("Parsing construction document...")
        
        # Determine document type
        document_type = self._identify_document_type(text)
        
        # Extract basic information
        project_title = self._extract_project_title(text)
        project_description = self._extract_project_description(text)
        timeline = self._extract_timeline(text)
        budget = self._extract_budget(text)
        
        # Extract specific requirements based on document type
        materials_required = self._extract_materials_required(text)
        technical_requirements = self._extract_technical_requirements(text)
        regulatory_requirements = self._extract_regulatory_requirements(text)
        risk_factors = self._extract_risk_factors(text)
        key_dates = self._extract_key_dates(text)
        contact_info = self._extract_contact_info(text)
        specifications = self._extract_specifications(text)
        
        return ConstructionDocumentData(
            document_type=document_type,
            project_title=project_title,
            project_description=project_description,
            timeline=timeline,
            budget=budget,
            materials_required=materials_required,
            technical_requirements=technical_requirements,
            regulatory_requirements=regulatory_requirements,
            risk_factors=risk_factors,
            key_dates=key_dates,
            contact_info=contact_info,
            specifications=specifications
        )
    
    def _identify_document_type(self, text: str) -> str:
        """Identify the type of construction document"""
        text_lower = text.lower()
        
        for doc_type, config in self.document_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    return doc_type
        
        return 'general_construction'
    
    def _extract_project_title(self, text: str) -> str:
        """Extract project title from document"""
        # Look for common title patterns
        title_patterns = [
            r'project title[:\s]+([^\n]+)',
            r'project name[:\s]+([^\n]+)',
            r'title[:\s]+([^\n]+)',
            r'project[:\s]+([^\n]+)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: extract first meaningful line
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('Page'):
                return line
        
        return "Untitled Project"
    
    def _extract_project_description(self, text: str) -> str:
        """Extract project description"""
        # Look for description sections
        desc_patterns = [
            r'project description[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'overview[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'scope[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "No description available"
    
    def _extract_timeline(self, text: str) -> str:
        """Extract project timeline"""
        timeline_patterns = [
            r'timeline[:\s]+([^\n]+)',
            r'duration[:\s]+([^\n]+)',
            r'project duration[:\s]+([^\n]+)',
            r'completion date[:\s]+([^\n]+)',
            r'deadline[:\s]+([^\n]+)'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Timeline not specified"
    
    def _extract_budget(self, text: str) -> str:
        """Extract project budget"""
        budget_patterns = [
            r'budget[:\s]+([^\n]+)',
            r'estimated cost[:\s]+([^\n]+)',
            r'project cost[:\s]+([^\n]+)',
            r'value[:\s]+([^\n]+)',
            r'£[\d,]+(?:\.\d{2})?',
            r'\$[\d,]+(?:\.\d{2})?'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Budget not specified"
    
    def _extract_materials_required(self, text: str) -> List[str]:
        """Extract required materials"""
        materials = []
        
        # Common construction materials
        material_keywords = [
            'concrete', 'steel', 'timber', 'bricks', 'insulation',
            'roof tiles', 'windows', 'doors', 'plumbing', 'electrical',
            'flooring', 'paint', 'render', 'plaster', 'cement'
        ]
        
        text_lower = text.lower()
        for material in material_keywords:
            if material in text_lower:
                materials.append(material.title())
        
        # Look for material specifications
        material_patterns = [
            r'materials required[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'materials[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'specifications[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in material_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                spec_text = match.group(1)
                # Extract individual materials from specification text
                for material in material_keywords:
                    if material in spec_text.lower():
                        materials.append(material.title())
        
        return list(set(materials))  # Remove duplicates
    
    def _extract_technical_requirements(self, text: str) -> List[str]:
        """Extract technical requirements"""
        requirements = []
        
        # Look for technical requirement sections
        tech_patterns = [
            r'technical requirements[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'specifications[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'requirements[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in tech_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                req_text = match.group(1)
                # Split into individual requirements
                lines = req_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10:
                        requirements.append(line)
        
        return requirements
    
    def _extract_regulatory_requirements(self, text: str) -> List[str]:
        """Extract regulatory requirements"""
        regulations = []
        
        # UK construction regulations
        uk_regulations = [
            'Building Regulations', 'CDM Regulations', 'Fire Safety',
            'Planning Permission', 'Party Wall Act', 'Health and Safety',
            'Environmental Impact Assessment', 'BREEAM', 'Energy Performance'
        ]
        
        text_lower = text.lower()
        for regulation in uk_regulations:
            if regulation.lower() in text_lower:
                regulations.append(regulation)
        
        return regulations
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract risk factors"""
        risks = []
        
        # Common construction risks
        risk_keywords = [
            'risk', 'hazard', 'safety', 'delay', 'cost overrun',
            'weather', 'ground conditions', 'structural', 'access'
        ]
        
        text_lower = text.lower()
        for risk in risk_keywords:
            if risk in text_lower:
                risks.append(risk.title())
        
        return risks
    
    def _extract_key_dates(self, text: str) -> List[str]:
        """Extract key dates from document"""
        dates = []
        
        # Date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'\+?[\d\s\-\(\)]{10,}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
        
        return contact_info
    
    def _extract_specifications(self, text: str) -> Dict[str, Any]:
        """Extract detailed specifications"""
        specs = {}
        
        # Look for specification sections
        spec_patterns = [
            r'dimensions[:\s]+([^\n]+)',
            r'size[:\s]+([^\n]+)',
            r'quantity[:\s]+([^\n]+)',
            r'quality[:\s]+([^\n]+)',
            r'standard[:\s]+([^\n]+)'
        ]
        
        for pattern in spec_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                specs[key] = match.group(1).strip()
        
        return specs
    
    def _extract_tender_requirements(self, text: str) -> Dict[str, Any]:
        """Extract tender-specific requirements"""
        requirements = {}
        
        # Look for tender requirements
        tender_patterns = [
            r'submission deadline[:\s]+([^\n]+)',
            r'bid deadline[:\s]+([^\n]+)',
            r'evaluation criteria[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'selection criteria[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in tender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                requirements[key] = match.group(1).strip()
        
        return requirements
    
    def _extract_rfd_requirements(self, text: str) -> Dict[str, Any]:
        """Extract RFD-specific requirements"""
        requirements = {}
        
        # Look for RFD requirements
        rfd_patterns = [
            r'documents required[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'submission format[:\s]+([^\n]+)',
            r'deadline[:\s]+([^\n]+)',
            r'compliance requirements[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in rfd_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                requirements[key] = match.group(1).strip()
        
        return requirements
    
    def _extract_material_specifications(self, text: str) -> Dict[str, Any]:
        """Extract material specifications"""
        specs = {}
        
        # Look for material specifications
        material_patterns = [
            r'material type[:\s]+([^\n]+)',
            r'grade[:\s]+([^\n]+)',
            r'standard[:\s]+([^\n]+)',
            r'certification[:\s]+([^\n]+)',
            r'quality requirements[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in material_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                specs[key] = match.group(1).strip()
        
        return specs
    
    def _extract_project_timeline(self, text: str) -> Dict[str, Any]:
        """Extract project timeline information"""
        timeline = {}
        
        # Look for timeline information
        timeline_patterns = [
            r'start date[:\s]+([^\n]+)',
            r'completion date[:\s]+([^\n]+)',
            r'milestones[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'phases[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                timeline[key] = match.group(1).strip()
        
        return timeline
    
    def _extract_work_methodology(self, text: str) -> Dict[str, Any]:
        """Extract work methodology"""
        methodology = {}
        
        # Look for methodology information
        method_patterns = [
            r'methodology[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'approach[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'work sequence[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'procedures[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                methodology[key] = match.group(1).strip()
        
        return methodology
    
    def _extract_resource_requirements(self, text: str) -> Dict[str, Any]:
        """Extract resource requirements"""
        resources = {}
        
        # Look for resource information
        resource_patterns = [
            r'manpower[:\s]+([^\n]+)',
            r'equipment[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'materials[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'resources[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in resource_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                resources[key] = match.group(1).strip()
        
        return resources
    
    def _extract_quality_standards(self, text: str) -> Dict[str, Any]:
        """Extract quality standards"""
        standards = {}
        
        # Look for quality standards
        quality_patterns = [
            r'quality standard[:\s]+([^\n]+)',
            r'certification[:\s]+([^\n]+)',
            r'compliance[:\s]+([^\n]+)',
            r'quality requirements[:\s]+([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in quality_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                standards[key] = match.group(1).strip()
        
        return standards
    
    def _extract_supplier_requirements(self, text: str) -> Dict[str, Any]:
        """Extract supplier requirements"""
        requirements = {}
        
        # Look for supplier requirements
        supplier_patterns = [
            r'supplier qualification[:\s]+([^\n]+(?:\n[^\n]+)*)',
            r'certification[:\s]+([^\n]+)',
            r'experience[:\s]+([^\n]+)',
            r'financial capacity[:\s]+([^\n]+)'
        ]
        
        for pattern in supplier_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0].strip()
                requirements[key] = match.group(1).strip()
        
        return requirements
    
    def _extract_document_types(self, text: str) -> List[str]:
        """Extract required document types"""
        doc_types = []
        
        # Common document types
        document_types = [
            'technical specifications', 'method statements', 'risk assessments',
            'quality plans', 'safety documentation', 'environmental assessments',
            'financial statements', 'insurance certificates', 'references',
            'certifications', 'licenses', 'permits'
        ]
        
        text_lower = text.lower()
        for doc_type in document_types:
            if doc_type in text_lower:
                doc_types.append(doc_type.title())
        
        return doc_types
    
    def _extract_submission_deadlines(self, text: str) -> List[str]:
        """Extract submission deadlines"""
        deadlines = []
        
        # Look for deadline patterns
        deadline_patterns = [
            r'submission deadline[:\s]+([^\n]+)',
            r'deadline[:\s]+([^\n]+)',
            r'due date[:\s]+([^\n]+)',
            r'closing date[:\s]+([^\n]+)'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadlines.append(match.group(1).strip())
        
        return deadlines
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API for enhanced extraction"""
        if not self.openrouter_api_key:
            return ""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a construction document analysis expert. Extract key information from construction documents in a structured format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return ""
    
    def _extract_ai_enhanced_info(self, text: str, document_type: str) -> Dict[str, Any]:
        """Extract information using AI enhancement"""
        if not self.openrouter_api_key:
            return {}
        
        prompt = f"""
        Analyze this construction document and extract key information:
        
        Document Type: {document_type}
        Document Text: {text[:2000]}...
        
        Please extract and return as JSON:
        - Project title and description
        - Timeline and budget
        - Materials required
        - Technical requirements
        - Regulatory requirements
        - Risk factors
        - Key dates and deadlines
        - Contact information
        """
        
        ai_response = self._call_openrouter(prompt)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON")
        
        return {}
    
    def process_construction_document(self, file_path: str, use_ai: bool = False, document_type: str = "general") -> Dict[str, Any]:
        """
        Process a construction document file
        
        Args:
            file_path: Path to the document file
            use_ai: Whether to use AI enhancement
            document_type: Type of document being processed
            
        Returns:
            Dictionary with extracted information
        """
        logger.info(f"Processing construction document: {file_path}")
        
        # Extract text from file
        text = self.extract_text_from_file(file_path)
        if not text:
            return {"error": "Could not extract text from file"}
        
        # Parse document
        document_data = self.parse_construction_document(text)
        
        # AI enhancement if requested
        ai_enhanced = {}
        if use_ai and self.openrouter_api_key:
            ai_enhanced = self._extract_ai_enhanced_info(text, document_type)
        
        # Convert to dictionary
        result = {
            "document_type": document_data.document_type,
            "project_title": document_data.project_title,
            "project_description": document_data.project_description,
            "timeline": document_data.timeline,
            "budget": document_data.budget,
            "materials_required": document_data.materials_required,
            "technical_requirements": document_data.technical_requirements,
            "regulatory_requirements": document_data.regulatory_requirements,
            "risk_factors": document_data.risk_factors,
            "key_dates": document_data.key_dates,
            "contact_info": document_data.contact_info,
            "specifications": document_data.specifications,
            "ai_enhanced": ai_enhanced
        }
        
        return result
    
    def generate_construction_document(self, document_data: ConstructionDocumentData, document_type: str) -> str:
        """
        Generate a construction document based on extracted data
        
        Args:
            document_data: Extracted document data
            document_type: Type of document to generate
            
        Returns:
            Generated document text
        """
        logger.info(f"Generating {document_type} document")
        
        if document_type == "tender_document":
            return self._generate_tender_document(document_data)
        elif document_type == "rfd_request":
            return self._generate_rfd_request(document_data)
        elif document_type == "material_specification":
            return self._generate_material_specification(document_data)
        elif document_type == "project_plan":
            return self._generate_project_plan(document_data)
        else:
            return self._generate_general_document(document_data)
    
    def _generate_tender_document(self, data: ConstructionDocumentData) -> str:
        """Generate a tender document"""
        doc = f"""
# TENDER DOCUMENT

## Project Information
**Project Title:** {data.project_title}
**Project Description:** {data.project_description}

## Project Details
**Timeline:** {data.timeline}
**Budget:** {data.budget}

## Technical Requirements
"""
        for req in data.technical_requirements:
            doc += f"- {req}\n"
        
        doc += f"""
## Materials Required
"""
        for material in data.materials_required:
            doc += f"- {material}\n"
        
        doc += f"""
## Regulatory Requirements
"""
        for reg in data.regulatory_requirements:
            doc += f"- {reg}\n"
        
        doc += f"""
## Risk Factors
"""
        for risk in data.risk_factors:
            doc += f"- {risk}\n"
        
        doc += f"""
## Key Dates
"""
        for date in data.key_dates:
            doc += f"- {date}\n"
        
        return doc
    
    def _generate_rfd_request(self, data: ConstructionDocumentData) -> str:
        """Generate an RFD request document"""
        doc = f"""
# REQUEST FOR DOCUMENTS (RFD)

## Project Information
**Project Title:** {data.project_title}
**Project Description:** {data.project_description}

## Documents Required
"""
        for req in data.technical_requirements:
            doc += f"- {req}\n"
        
        doc += f"""
## Submission Requirements
- All documents must be submitted in PDF format
- Include company certifications and insurance certificates
- Provide technical specifications and method statements
- Include risk assessments and quality plans

## Key Dates
"""
        for date in data.key_dates:
            doc += f"- {date}\n"
        
        return doc
    
    def _generate_material_specification(self, data: ConstructionDocumentData) -> str:
        """Generate a material specification document"""
        doc = f"""
# MATERIAL SPECIFICATION

## Project Information
**Project Title:** {data.project_title}
**Project Description:** {data.project_description}

## Materials Required
"""
        for material in data.materials_required:
            doc += f"- {material}\n"
        
        doc += f"""
## Technical Specifications
"""
        for spec in data.technical_requirements:
            doc += f"- {spec}\n"
        
        doc += f"""
## Quality Standards
"""
        for reg in data.regulatory_requirements:
            doc += f"- {reg}\n"
        
        return doc
    
    def _generate_project_plan(self, data: ConstructionDocumentData) -> str:
        """Generate a project plan document"""
        doc = f"""
# PROJECT PLAN

## Project Information
**Project Title:** {data.project_title}
**Project Description:** {data.project_description}

## Project Timeline
**Duration:** {data.timeline}
**Budget:** {data.budget}

## Work Methodology
"""
        for req in data.technical_requirements:
            doc += f"- {req}\n"
        
        doc += f"""
## Resource Requirements
"""
        for material in data.materials_required:
            doc += f"- {material}\n"
        
        doc += f"""
## Risk Assessment
"""
        for risk in data.risk_factors:
            doc += f"- {risk}\n"
        
        return doc
    
    def _generate_general_document(self, data: ConstructionDocumentData) -> str:
        """Generate a general construction document"""
        doc = f"""
# CONSTRUCTION DOCUMENT

## Project Information
**Project Title:** {data.project_title}
**Project Description:** {data.project_description}

## Project Details
**Timeline:** {data.timeline}
**Budget:** {data.budget}

## Requirements
"""
        for req in data.technical_requirements:
            doc += f"- {req}\n"
        
        doc += f"""
## Materials
"""
        for material in data.materials_required:
            doc += f"- {material}\n"
        
        return doc

# Global instance
construction_document_processor = None

def get_construction_document_processor(openrouter_api_key: Optional[str] = None):
    """Get or create construction document processor instance"""
    global construction_document_processor
    if construction_document_processor is None:
        construction_document_processor = ConstructionDocumentProcessor(openrouter_api_key)
    return construction_document_processor

if __name__ == "__main__":
    # Test the construction document processor
    processor = ConstructionDocumentProcessor()
    
    # Test with sample text
    sample_text = """
    TENDER DOCUMENT
    
    Project Title: Residential Extension Project
    Project Description: Single storey extension to existing property
    
    Timeline: 8-12 weeks
    Budget: £25,000-£35,000
    
    Materials Required:
    - Concrete for foundations
    - Steel for structural support
    - Timber for framing
    - Bricks for walls
    - Roof tiles
    - Insulation
    
    Technical Requirements:
    - Building Regulations compliance
    - Planning permission required
    - Party wall agreement needed
    
    Key Dates:
    - Submission deadline: 15/12/2024
    - Project start: 01/01/2025
    - Completion: 31/03/2025
    """
    
    result = processor.parse_construction_document(sample_text)
    print(f"Document Type: {result.document_type}")
    print(f"Project Title: {result.project_title}")
    print(f"Materials: {result.materials_required}")
    print(f"Timeline: {result.timeline}")
    print(f"Budget: {result.budget}") 