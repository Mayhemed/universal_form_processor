#!/usr/bin/env python3
"""
Agentic PDF Form Filler - Command Line AI Agent System
Author: Assistant
Description: Command-line AI agent system for intelligent PDF form filling
"""

import os
import sys
import json
import argparse
import asyncio
import logging
import traceback
import glob
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Directory configuration from environment variables
DEFAULT_FORMS_DIR = os.getenv('FORMS_DIR', './forms')
DEFAULT_DATA_DIR = os.getenv('DATA_DIR', './data') 
DEFAULT_OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agentic_form_filler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AgenticFormFiller')

def resolve_path(path: str, default_dir: str = "") -> str:
    """Resolve a path, checking default directories if relative"""
    if os.path.isabs(path):
        return path
    
    # Try the path as-is first
    if os.path.exists(path):
        return path
    
    # Try in the default directory
    if default_dir:
        default_path = os.path.join(default_dir, path)
        if os.path.exists(default_path):
            return default_path
    
    # Return original path (might not exist, but let the calling code handle it)
    return path

def resolve_form_path(form_path: str) -> str:
    """Resolve path to a form file"""
    return resolve_path(form_path, DEFAULT_FORMS_DIR)

def resolve_data_paths(data_paths: List[str]) -> List[str]:
    """Resolve paths to data files"""
    return [resolve_path(path, DEFAULT_DATA_DIR) for path in data_paths]

def resolve_output_path(output_path: str) -> str:
    """Resolve output path, creating directory if needed"""
    if not os.path.isabs(output_path):
        # If relative, use default output directory
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, output_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path

def expand_file_patterns(patterns: List[str], base_dir: str = "") -> List[str]:
    """Expand file patterns and globs to actual file paths"""
    expanded_files = []
    
    for pattern in patterns:
        # Handle absolute paths
        if os.path.isabs(pattern):
            if '*' in pattern or '?' in pattern:
                # Glob pattern
                matches = glob.glob(pattern)
                expanded_files.extend(matches)
            elif os.path.isfile(pattern):
                expanded_files.append(pattern)
            elif os.path.isdir(pattern):
                # Directory - find all PDFs
                pdf_files = glob.glob(os.path.join(pattern, "*.pdf"))
                expanded_files.extend(pdf_files)
        else:
            # Relative path - try with base directory
            full_pattern = os.path.join(base_dir, pattern) if base_dir else pattern
            
            if '*' in pattern or '?' in pattern:
                # Glob pattern
                matches = glob.glob(full_pattern)
                if not matches and base_dir:
                    # Try without base directory
                    matches = glob.glob(pattern)
                expanded_files.extend(matches)
            elif os.path.isfile(full_pattern):
                expanded_files.append(full_pattern)
            elif os.path.isfile(pattern):
                expanded_files.append(pattern)
            elif os.path.isdir(full_pattern):
                # Directory - find all PDFs
                pdf_files = glob.glob(os.path.join(full_pattern, "*.pdf"))
                expanded_files.extend(pdf_files)
            elif os.path.isdir(pattern):
                # Directory without base
                pdf_files = glob.glob(os.path.join(pattern, "*.pdf"))
                expanded_files.extend(pdf_files)
    
    # Remove duplicates and sort
    return sorted(list(set(expanded_files)))

def expand_source_files(source_patterns: List[str]) -> List[str]:
    """Expand source file patterns, supporting various file types"""
    expanded_files = []
    
    for pattern in source_patterns:
        # Handle absolute paths
        if os.path.isabs(pattern):
            if '*' in pattern or '?' in pattern:
                # Glob pattern
                matches = glob.glob(pattern)
                expanded_files.extend(matches)
            elif os.path.isfile(pattern):
                expanded_files.append(pattern)
            elif os.path.isdir(pattern):
                # Directory - find all supported files
                for ext in ['*.pdf', '*.txt', '*.json', '*.csv', '*.md', '*.docx', '*.xlsx']:
                    files = glob.glob(os.path.join(pattern, ext))
                    expanded_files.extend(files)
        else:
            # Relative path - try with DATA_DIR
            full_pattern = os.path.join(DEFAULT_DATA_DIR, pattern)
            
            if '*' in pattern or '?' in pattern:
                # Glob pattern
                matches = glob.glob(full_pattern)
                if not matches:
                    # Try without base directory
                    matches = glob.glob(pattern)
                expanded_files.extend(matches)
            elif os.path.isfile(full_pattern):
                expanded_files.append(full_pattern)
            elif os.path.isfile(pattern):
                expanded_files.append(pattern)
            elif os.path.isdir(full_pattern):
                # Directory - find all supported files
                for ext in ['*.pdf', '*.txt', '*.json', '*.csv', '*.md', '*.docx', '*.xlsx']:
                    files = glob.glob(os.path.join(full_pattern, ext))
                    expanded_files.extend(files)
            elif os.path.isdir(pattern):
                # Directory without base
                for ext in ['*.pdf', '*.txt', '*.json', '*.csv', '*.md', '*.docx', '*.xlsx']:
                    files = glob.glob(os.path.join(pattern, ext))
                    expanded_files.extend(files)
    
    return sorted(list(set(expanded_files)))

def find_pdf_files_in_directory(directory: str) -> List[str]:
    """Find all PDF files in a directory and subdirectories"""
    pdf_files = []
    
    # Check if directory exists
    if not os.path.isdir(directory):
        return pdf_files
    
    # Find PDFs recursively
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    return sorted(pdf_files)

@dataclass
class ExtractionResult:
    """Result from AI extraction"""
    extracted_data: Dict[str, str]
    confidence_scores: Dict[str, float]
    quality_score: float
    issues_found: List[str]
    ai_provider: str
    iteration: int

@dataclass
class QualityAssessment:
    """AI Quality Assessment result"""
    overall_score: float
    completion_rate: float
    confidence_avg: float
    issues: List[str]
    recommendations: List[str]
    corrected_fields: Dict[str, str]
    should_retry: bool

class AIAgent:
    """Base class for AI agents"""
    
    def __init__(self, name: str, provider: str = "pattern", model: str = "", api_key: str = ""):
        self.name = name
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.logger = logging.getLogger(f'Agent.{name}')
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        raise NotImplementedError("Subclasses must implement execute method")

class DataExtractionAgent(AIAgent):
    """Agent responsible for extracting data from sources"""
    
    def __init__(self, provider: str = "pattern", model: str = "", api_key: str = ""):
        super().__init__("DataExtraction", provider, model, api_key)
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from provided sources"""
        try:
            self.logger.info(f"Starting data extraction with {self.provider}")
            
            sources = task_data.get('sources', [])
            form_fields = task_data.get('form_fields', [])
            
            # Collect all text from sources
            all_text = await self._collect_text_from_sources(sources)
            
            # Perform extraction based on provider
            if self.provider == "openai":
                extracted_data, confidence_scores = await self._extract_with_openai(all_text, form_fields)
            elif self.provider == "anthropic":
                extracted_data, confidence_scores = await self._extract_with_anthropic(all_text, form_fields)
            else:
                extracted_data, confidence_scores = await self._extract_with_patterns(all_text, form_fields)
            
            # Calculate initial quality score
            quality_score = self._calculate_quality_score(extracted_data, confidence_scores, form_fields)
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'confidence_scores': confidence_scores,
                'quality_score': quality_score,
                'text_analyzed': len(all_text),
                'fields_extracted': len(extracted_data),
                'ai_provider': self.provider
            }
            
        except Exception as e:
            self.logger.error(f"Data extraction failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'extracted_data': {},
                'confidence_scores': {},
                'quality_score': 0.0
            }

    
    async def _collect_text_from_sources(self, sources: List[str]) -> str:
        """Collect text from all provided sources"""
        all_text = ""
        
        for source in sources:
            self.logger.info(f"Processing source: {source}")
            if source.startswith('http'):
                # URL source
                text = await self._extract_from_url(source)
            elif Path(source).exists():
                # File source
                text = await self._extract_from_file(source)
            else:
                # Direct text
                text = source
                
            all_text += f"\n\n=== Source: {source[:50]}... ===\n{text}"
            
        return all_text
    
    async def _extract_from_file(self, file_path: str) -> str:
        """Extract text from file"""
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.pdf':
                # For PDFs, return special marker for direct processing
                return f"[PDF_PATH: {file_path}]"
            elif file_path.suffix.lower() in ['.txt', '.md', '.csv']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            else:
                return f"Unsupported file type: {file_path.suffix}"
                
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            return f"Error reading file: {str(e)}"
    
    async def _extract_from_url(self, url: str) -> str:
        """Extract text from URL"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            self.logger.error(f"Error extracting from URL {url}: {str(e)}")
            return f"Error extracting from URL: {str(e)}"
    
    async def _extract_with_patterns(self, text: str, form_fields: List[Dict]) -> Tuple[Dict[str, str], Dict[str, float]]:
        """Extract data using pattern matching (fallback method)"""
        import re
        
        extracted_data = {}
        confidence_scores = {}
        
        # Common patterns for legal/business documents
        patterns = {
            'case_number': r'(?i)case\s*(?:number|no\.?|#)\s*:?\s*([A-Z0-9\-]+)',
            'phone': r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'date': r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            'money': r'\$\s*([0-9,]+(?:\.[0-9]{2})?)',
            'address': r'\d+\s+[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)',
            'name': r'(?i)name\s*:?\s*([A-Za-z\s\.]+)',
            'ssn': r'(?:\d{3}-\d{2}-\d{4})',
            'zip': r'(?i)(?:zip|postal)\s*:?\s*(\d{5}(?:-\d{4})?)',
        }
        
        for field in form_fields:
            field_name = field.get('name', '')
            field_type = field.get('field_type', 'Text')
            alt_text = field.get('alt_text', '')
            
            field_lower = field_name.lower()
            alt_lower = alt_text.lower() if alt_text else ""
            
            # Try to match field names to patterns
            matched = False
            for pattern_name, pattern in patterns.items():
                if pattern_name in field_lower or pattern_name in alt_lower:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        if pattern_name == 'phone' and isinstance(matches[0], tuple) and len(matches[0]) >= 3:
                            # Format phone number
                            extracted_data[field_name] = f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
                        else:
                            extracted_data[field_name] = str(matches[0])
                        confidence_scores[field_name] = 0.8
                        matched = True
                        break
            
            # If pattern matching didn't work, try to find field name in text
            if not matched:
                search_terms = []
                if alt_text:
                    search_terms.append(alt_text)
                
                # Add cleaned up field name
                cleaned_name = field_name.replace('_', ' ').replace('.', ' ').strip()
                if cleaned_name:
                    search_terms.append(cleaned_name)
                
                for term in search_terms:
                    if not term:
                        continue
                    
                    # Try exact phrase with colon
                    pattern = rf'{re.escape(term)}\s*:?\s*([^\n\r]+)'
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        if len(value) > 0 and len(value) < 200:  # Reasonable length
                            extracted_data[field_name] = value
                            confidence_scores[field_name] = 0.6
                            break
        
        return extracted_data, confidence_scores
    
    def _calculate_quality_score(self, extracted_data: Dict[str, str], 
                               confidence_scores: Dict[str, float], 
                               form_fields: List[Dict]) -> float:
        """Calculate overall quality score"""
        if not form_fields:
            return 0.0
            
        total_fields = len(form_fields)
        filled_fields = len(extracted_data)
        
        # Completion rate (40% of score)
        completion_rate = filled_fields / total_fields
        
        # Average confidence (40% of score)
        if confidence_scores:
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        else:
            avg_confidence = 0.0
            
        # Quality bonus for high-confidence fields (20% of score)
        high_confidence_count = sum(1 for conf in confidence_scores.values() if conf > 0.8)
        quality_bonus = high_confidence_count / max(filled_fields, 1) if filled_fields > 0 else 0
        
        quality_score = (completion_rate * 0.4) + (avg_confidence * 0.4) + (quality_bonus * 0.2)
        return min(quality_score, 1.0)

    
    async def _extract_with_openai(self, text: str, form_fields: List[Dict]) -> Tuple[Dict[str, str], Dict[str, float]]:
        """Extract using OpenAI"""
        try:
            # Try to import llm_client from your existing code
            try:
                import llm_client
            except ImportError:
                self.logger.warning("llm_client not available, falling back to pattern matching")
                return await self._extract_with_patterns(text, form_fields)
            
            # Set API key
            os.environ["OPENAI_API_KEY"] = self.api_key
            
            # Create extraction prompt
            prompt = self._create_extraction_prompt(text, form_fields)
            
            # Use selected model or default
            model = self.model if self.model else "gpt-4-turbo"
            
            response_text = llm_client.generate_with_openai(model, prompt)
            
            return self._parse_ai_response(response_text)
            
        except Exception as e:
            self.logger.error(f"OpenAI extraction error: {str(e)}")
            return await self._extract_with_patterns(text, form_fields)
    
    async def _extract_with_anthropic(self, text: str, form_fields: List[Dict]) -> Tuple[Dict[str, str], Dict[str, float]]:
        """Extract using Anthropic Claude"""
        try:
            # Try to import llm_client from your existing code
            try:
                import llm_client
            except ImportError:
                self.logger.warning("llm_client not available, falling back to pattern matching")
                return await self._extract_with_patterns(text, form_fields)
            
            # Set API key
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
            
            # Create extraction prompt
            prompt = self._create_extraction_prompt(text, form_fields)
            
            # Use selected model or default
            model = self.model if self.model else "claude-3-sonnet-20240229"
            
            response_text = llm_client.generate_with_claude(model, prompt)
            
            return self._parse_ai_response(response_text)
            
        except Exception as e:
            self.logger.error(f"Anthropic extraction error: {str(e)}")
            return await self._extract_with_patterns(text, form_fields)
    
    def _create_extraction_prompt(self, text: str, form_fields: List[Dict]) -> str:
        """Create prompt for AI extraction"""
        field_names = [f.get('name', '') for f in form_fields]
        field_descriptions = [f.get('alt_text', f.get('name', '')) for f in form_fields]
        
        return f"""
You are extracting data from a COMPLETED PDF form to populate a blank PDF form with the same structure.

TASK: Extract the client's actual responses/values from the completed form text below.

TARGET FORM FIELDS TO POPULATE:
{json.dumps(dict(zip(field_names, field_descriptions)), indent=2)}

COMPLETED FORM TEXT TO ANALYZE:
{text[:8000]}

EXTRACTION RULES:
1. Look for FILLED-IN VALUES, not field labels or instructions
2. Extract actual data entries like:
   - Names: "TAHIRA FRANCIS", "SHAWN ROGERS"  
   - Case numbers: "24STFL00615"
   - Monetary amounts
   - Account details
   - Addresses and descriptions of assets/debts
   - Dates and other specific client information

3. IGNORE:
   - Form instructions and field labels
   - Empty fields showing "0.00" or blank
   - Template text like "Give details", "Attach copy", etc.

4. FOCUS ON:
   - Actual names, numbers, and descriptions entered by the client
   - Monetary values that are NOT 0.00
   - Specific account information, addresses, creditor names
   - Any handwritten or typed responses

RETURN FORMAT:
{{
    "extracted_data": {{
        "field_name": "actual_client_value"
    }},
    "confidence_scores": {{
        "field_name": 0.95
    }}
}}

Extract only the CLIENT'S ACTUAL DATA ENTRIES, not form structure or empty fields.
        """
    
    def _parse_ai_response(self, response_text: str) -> Tuple[Dict[str, str], Dict[str, float]]:
        """Parse AI response to extract data and confidence scores"""
        try:
            # Find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_text = response_text[start:end]
                try:
                    result = json.loads(json_text)
                    extracted_data = result.get("extracted_data", {})
                    confidence_scores = result.get("confidence_scores", {})
                    
                    # If missing confidence scores, generate defaults
                    if extracted_data and not confidence_scores:
                        confidence_scores = {key: 0.8 for key in extracted_data.keys()}
                        
                    return extracted_data, confidence_scores
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse AI response JSON, using empty result")
                    return {}, {}
            else:
                self.logger.warning("No JSON found in AI response")
                return {}, {}
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {str(e)}")
            return {}, {}


class QualityAssuranceAgent(AIAgent):
    """Agent responsible for quality assessment and improvement"""
    
    def __init__(self, provider: str = "pattern", model: str = "", api_key: str = ""):
        super().__init__("QualityAssurance", provider, model, api_key)
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality and suggest improvements"""
        try:
            self.logger.info("Starting quality assessment")
            
            extracted_data = task_data.get('extracted_data', {})
            confidence_scores = task_data.get('confidence_scores', {})
            form_fields = task_data.get('form_fields', [])
            source_text = task_data.get('source_text', '')
            
            # Perform quality assessment
            assessment = await self._assess_quality(
                extracted_data, confidence_scores, form_fields, source_text
            )
            
            return {
                'success': True,
                'assessment': asdict(assessment),
                'should_retry': assessment.should_retry,
                'corrected_fields': assessment.corrected_fields
            }
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'should_retry': False,
                'corrected_fields': {}
            }
    async def _assess_quality(self, extracted_data: Dict[str, str], 
                            confidence_scores: Dict[str, float],
                            form_fields: List[Dict], 
                            source_text: str) -> QualityAssessment:
        """Assess the quality of extraction and suggest improvements"""
        
        total_fields = len(form_fields)
        filled_fields = len(extracted_data)
        
        completion_rate = filled_fields / total_fields if total_fields > 0 else 0
        confidence_avg = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
        
        issues = []
        recommendations = []
        corrected_fields = {}
        
        # Check for missing required fields
        for field in form_fields:
            field_name = field.get('name', '')
            if field_name not in extracted_data:
                # Try to find the field in the source text
                potential_value = await self._find_missing_field(field, source_text)
                if potential_value:
                    corrected_fields[field_name] = potential_value
                    recommendations.append(f"Found missing field '{field_name}': {potential_value}")
                else:
                    issues.append(f"Missing required field: {field_name}")
        
        # Check for low confidence fields
        for field_name, confidence in confidence_scores.items():
            if confidence < 0.6:
                issues.append(f"Low confidence for field '{field_name}': {confidence:.2f}")
                # Try to improve the field
                improved_value = await self._improve_field_extraction(field_name, source_text)
                if improved_value and improved_value != extracted_data.get(field_name):
                    corrected_fields[field_name] = improved_value
                    recommendations.append(f"Improved field '{field_name}': {improved_value}")
        
        # Calculate overall score
        corrected_completion = (filled_fields + len(corrected_fields)) / total_fields if total_fields > 0 else 0
        overall_score = (corrected_completion * 0.6) + (confidence_avg * 0.4)
        
        # Determine if retry is needed
        should_retry = overall_score < 0.8 and len(corrected_fields) > 0
        
        return QualityAssessment(
            overall_score=overall_score,
            completion_rate=completion_rate,
            confidence_avg=confidence_avg,
            issues=issues,
            recommendations=recommendations,
            corrected_fields=corrected_fields,
            should_retry=should_retry
        )
    
    async def _find_missing_field(self, field: Dict, source_text: str) -> Optional[str]:
        """Try to find a missing field in the source text"""
        import re
        
        field_name = field.get('name', '')
        alt_text = field.get('alt_text', '')
        
        # Search patterns based on field name
        search_terms = [alt_text, field_name.replace('_', ' ')]
        
        for term in search_terms:
            if not term:
                continue
                
            # Try different patterns
            patterns = [
                rf'{re.escape(term)}\s*:?\s*([^\n\r]+)',
                rf'(?i){re.escape(term)}\s*[:\-]\s*([^\n\r]+)',
                rf'(?i){re.escape(term.lower())}\s*[:\-]?\s*([^\n\r]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, source_text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if len(value) > 0 and len(value) < 200:
                        return value
        
        return None
    
    async def _improve_field_extraction(self, field_name: str, source_text: str) -> Optional[str]:
        """Try to improve extraction for a specific field"""
        import re
        
        # Try more aggressive pattern matching
        field_name_clean = field_name.lower().replace('_', ' ')
        
        # Enhanced patterns for common field types
        if 'name' in field_name_clean:
            pattern = r'(?i)(?:name|petitioner|respondent)\s*:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)'
            match = re.search(pattern, source_text)
            if match:
                return match.group(1).strip()
                
        elif 'case' in field_name_clean:
            pattern = r'(?i)case\s*(?:number|no\.?|#)\s*:?\s*([A-Z0-9\-]+)'
            match = re.search(pattern, source_text)
            if match:
                return match.group(1).strip()
                
        elif 'amount' in field_name_clean or 'total' in field_name_clean:
            pattern = r'\$\s*([0-9,]+(?:\.[0-9]{2})?)'
            matches = re.findall(pattern, source_text)
            if matches:
                # Return the largest amount found
                amounts = [float(amt.replace(',', '')) for amt in matches]
                return f"${max(amounts):,.2f}"
        
        return None


class FormFieldExtractor:
    """Utility class for extracting PDF form fields"""
    
    @staticmethod
    async def extract_pdf_fields(pdf_path: str) -> List[Dict[str, Any]]:
        """Extract form fields from PDF using pdftk"""
        import subprocess
        
        try:
            # Check if pdftk is available
            subprocess.run(['pdftk', '--version'], capture_output=True, check=True)
            
            # Extract fields using pdftk
            result = subprocess.run([
                'pdftk', pdf_path, 'dump_data_fields'
            ], capture_output=True, text=True, check=True)
            
            # Parse the output
            fields = FormFieldExtractor._parse_pdftk_output(result.stdout)
            return fields
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting PDF fields: {e}")
            raise Exception(f"Error extracting fields: {e}")
        except FileNotFoundError:
            raise Exception(
                "pdftk not found. Please install pdftk:\n"
                "macOS: brew install pdftk-java\n"
                "Ubuntu: sudo apt install pdftk\n"
                "Windows: Download from pdftk.org"
            )
    
    @staticmethod
    def _parse_pdftk_output(output: str) -> List[Dict[str, Any]]:
        """Parse pdftk dump_data_fields output"""
        fields = []
        current_field = {}
        
        for line in output.strip().split('\n'):
            if line.startswith('---'):
                if current_field:
                    field = {
                        'name': current_field.get('FieldName', ''),
                        'field_type': current_field.get('FieldType', 'Text'),
                        'alt_text': current_field.get('FieldNameAlt', ''),
                        'flags': int(current_field.get('FieldFlags', 0)),
                        'justification': current_field.get('FieldJustification', 'Left'),
                        'state_options': current_field.get('FieldStateOption', [])
                    }
                    fields.append(field)
                current_field = {}
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'FieldStateOption':
                    if key not in current_field:
                        current_field[key] = []
                    current_field[key].append(value)
                else:
                    current_field[key] = value

        # Add the last field
        if current_field:
            field = {
                'name': current_field.get('FieldName', ''),
                'field_type': current_field.get('FieldType', 'Text'),
                'alt_text': current_field.get('FieldNameAlt', ''),
                'flags': int(current_field.get('FieldFlags', 0)),
                'justification': current_field.get('FieldJustification', 'Left'),
                'state_options': current_field.get('FieldStateOption', [])
            }
            fields.append(field)

        return fields


class PDFFormFiller:
    """Utility class for filling PDF forms"""
    
    @staticmethod
    async def fill_pdf_form(pdf_path: str, field_data: Dict[str, str], output_path: str) -> bool:
        """Fill PDF form with data"""
        import subprocess
        import tempfile
        
        try:
            # Create FDF file
            fdf_content = PDFFormFiller._create_fdf(field_data)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False) as fdf_file:
                fdf_file.write(fdf_content)
                fdf_path = fdf_file.name

            try:
                # Fill the form using pdftk
                subprocess.run([
                    'pdftk', pdf_path, 'fill_form', fdf_path,
                    'output', output_path
                ], check=True)

                return True

            finally:
                # Clean up temporary FDF file
                os.unlink(fdf_path)

        except Exception as e:
            logger.error(f"Error filling PDF form: {str(e)}")
            return False
    
    @staticmethod
    def _create_fdf(field_data: Dict[str, str]) -> str:
        """Create FDF content for form filling"""
        fdf_header = """%FDF-1.2
1 0 obj
<<
/FDF
<<
/Fields ["""

        fdf_fields = []
        for field_name, field_value in field_data.items():
            if field_value:  # Only include non-empty fields
                escaped_value = field_value.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                fdf_fields.append(f"""<<
/T ({field_name})
/V ({escaped_value})
>>""")

        fdf_footer = """]
>>
>>
endobj
trailer

<<
/Root 1 0 R
>>
%%EOF"""

        return fdf_header + '\n' + '\n'.join(fdf_fields) + '\n' + fdf_footer



class AgenticFormFillerOrchestrator:
    """Main orchestrator for the agentic form filling system"""
    
    def __init__(self, ai_provider: str = "pattern", model: str = "", api_key: str = ""):
        self.ai_provider = ai_provider
        self.model = model
        self.api_key = api_key
        
        # Initialize agents
        self.data_extraction_agent = DataExtractionAgent(ai_provider, model, api_key)
        self.quality_assurance_agent = QualityAssuranceAgent(ai_provider, model, api_key)
        
        self.logger = logging.getLogger('Orchestrator')
        
    async def process_form(self, pdf_path: str, sources: List[str], 
                          output_path: str = None, max_iterations: int = 3) -> Dict[str, Any]:
        """Process a PDF form with agentic AI system"""
        
        results = {
            'success': False,
            'pdf_path': pdf_path,
            'sources': sources,
            'iterations': [],
            'final_data': {},
            'quality_score': 0.0,
            'filled_pdf_path': output_path
        }
        
        try:
            self.logger.info(f"Starting agentic processing of {pdf_path}")
            
            # Step 1: Extract form fields from PDF
            self.logger.info("Extracting form fields...")
            form_fields = await FormFieldExtractor.extract_pdf_fields(pdf_path)
            self.logger.info(f"Found {len(form_fields)} form fields")
            
            # Step 2: Initial data extraction
            extraction_result = await self._perform_extraction_iteration(
                sources, form_fields, iteration=1
            )
            results['iterations'].append(extraction_result)
            
            current_data = extraction_result['extracted_data']
            current_quality = extraction_result['quality_score']
            
            # Step 3: Iterative quality improvement
            for iteration in range(2, max_iterations + 1):
                if current_quality >= 0.9:  # Quality threshold met
                    self.logger.info(f"Quality threshold met: {current_quality:.2f}")
                    break
                    
                self.logger.info(f"Starting quality improvement iteration {iteration}")
                
                # Quality assessment
                qa_result = await self.quality_assurance_agent.execute({
                    'extracted_data': current_data,
                    'confidence_scores': extraction_result.get('confidence_scores', {}),
                    'form_fields': form_fields,
                    'source_text': extraction_result.get('source_text', '')
                })
                
                if not qa_result['success'] or not qa_result['should_retry']:
                    self.logger.info("No quality improvements suggested")
                    break
                
                # Apply corrections
                corrected_fields = qa_result['corrected_fields']
                if corrected_fields:
                    current_data.update(corrected_fields)
                    self.logger.info(f"Applied {len(corrected_fields)} corrections")
                    
                    # Re-evaluate quality
                    current_quality = self._calculate_quality_score(
                        current_data, 
                        extraction_result.get('confidence_scores', {}),
                        form_fields
                    )
                    
                    results['iterations'].append({
                        'iteration': iteration,
                        'type': 'quality_improvement',
                        'corrections_applied': corrected_fields,
                        'quality_score': current_quality,
                        'issues_resolved': len(corrected_fields)
                    })
            
            # Step 4: Fill the PDF form
            if output_path and current_data:
                self.logger.info("Filling PDF form...")
                filled_successfully = await PDFFormFiller.fill_pdf_form(
                    pdf_path, current_data, output_path
                )
                
                if filled_successfully:
                    self.logger.info(f"PDF filled successfully: {output_path}")
                    results['filled_pdf_path'] = output_path
                else:
                    self.logger.error("Failed to fill PDF form")
            
            # Final results
            results.update({
                'success': True,
                'final_data': current_data,
                'quality_score': current_quality,
                'total_iterations': len(results['iterations']),
                'fields_extracted': len(current_data),
                'total_fields': len(form_fields)
            })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            results['error'] = str(e)
            return results
    
    async def _perform_extraction_iteration(self, sources: List[str], 
                                          form_fields: List[Dict], 
                                          iteration: int) -> Dict[str, Any]:
        """Perform a single extraction iteration"""
        
        self.logger.info(f"Data extraction iteration {iteration}")
        
        # Collect source text for quality assessment
        all_source_text = ""
        for source in sources:
            if Path(source).exists():
                try:
                    if source.endswith('.pdf'):
                        all_source_text += f"[PDF_PATH: {source}]"
                    else:
                        with open(source, 'r', encoding='utf-8') as f:
                            all_source_text += f.read()
                except Exception as e:
                    self.logger.warning(f"Could not read source {source}: {e}")
            else:
                all_source_text += source
        
        # Perform extraction
        extraction_result = await self.data_extraction_agent.execute({
            'sources': sources,
            'form_fields': form_fields
        })
        
        # Add source text for quality assessment
        extraction_result['source_text'] = all_source_text
        extraction_result['iteration'] = iteration
        
        return extraction_result
    
    def _calculate_quality_score(self, extracted_data: Dict[str, str], 
                               confidence_scores: Dict[str, float], 
                               form_fields: List[Dict]) -> float:
        """Calculate overall quality score"""
        if not form_fields:
            return 0.0
            
        total_fields = len(form_fields)
        filled_fields = len(extracted_data)
        
        # Completion rate (60% of score)
        completion_rate = filled_fields / total_fields
        
        # Average confidence (40% of score)
        if confidence_scores:
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        else:
            avg_confidence = 0.0
            
        quality_score = (completion_rate * 0.6) + (avg_confidence * 0.4)
        return min(quality_score, 1.0)


def print_results_summary(results: Dict[str, Any]):
    """Print a formatted summary of the results"""
    
    print("\n" + "="*60)
    print("🤖 AI-POWERED PDF FORM FILLER RESULTS")
    print("="*60)
    
    if results['success']:
        print(f"✅ Status: SUCCESS")
        print(f"📄 PDF Form: {results['pdf_path']}")
        print(f"📊 Quality Score: {results['quality_score']:.1%}")
        print(f"📝 Fields Extracted: {results['fields_extracted']}/{results['total_fields']}")
        print(f"🔄 AI Iterations: {results['total_iterations']}")
        
        if results.get('filled_pdf_path'):
            print(f"💾 Output: {results['filled_pdf_path']}")
        
        print(f"\n🎯 PERFORMANCE METRICS:")
        completion_rate = results['fields_extracted'] / results['total_fields'] if results['total_fields'] > 0 else 0
        print(f"  • Completion Rate: {completion_rate:.1%}")
        print(f"  • AI Provider: {results.get('ai_provider', 'Pattern Matching')}")
        
        # Show iteration details
        if results['iterations']:
            print(f"\n🔄 ITERATION DETAILS:")
            for i, iteration in enumerate(results['iterations'], 1):
                if iteration.get('type') == 'quality_improvement':
                    print(f"  Iteration {iteration['iteration']}: Quality Improvement")
                    print(f"    - Corrections Applied: {iteration['corrections_applied']}")
                    print(f"    - Issues Resolved: {iteration['issues_resolved']}")
                else:
                    print(f"  Iteration {i}: Data Extraction")
                    print(f"    - Fields Found: {iteration.get('fields_extracted', 0)}")
                    print(f"    - Quality Score: {iteration.get('quality_score', 0):.1%}")
        
    else:
        print(f"❌ Status: FAILED")
        print(f"🚨 Error: {results.get('error', 'Unknown error')}")
    
    print("="*60)


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Agentic AI-Powered PDF Form Filler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic form filling with pattern matching
  python agentic_form_filler.py --form form.pdf --sources data.txt --output filled.pdf
  
  # Process all PDFs in a directory as sources
  python agentic_form_filler.py --form form.pdf --sources "data/*.pdf" --output filled.pdf
  
  # Use entire directory as source (all supported file types)
  python agentic_form_filler.py --form form.pdf --sources client_documents/ --output filled.pdf
  
  # Multiple patterns and directories
  python agentic_form_filler.py --form form.pdf --sources "case1/*.pdf" "case2/*.txt" documents/ --output filled.pdf
  
  # AI-powered with OpenAI
  python agentic_form_filler.py --form form.pdf --sources "data/*.pdf" --output filled.pdf --ai-provider openai --api-key sk-...
  
  # Recursive directory search
  python agentic_form_filler.py --form form.pdf --sources client_data/ --recursive --output filled.pdf
        """
    )
    
    # Arguments (form and sources are required unless using discovery commands)
    parser.add_argument('--form', help='Path to the blank PDF form (supports wildcards like "forms/*.pdf")')
    parser.add_argument('--sources', nargs='*', 
                       help='Data sources: files, directories, or patterns (e.g., "data/*.pdf", "client_docs/")')
    
    # File selection options
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Search directories recursively for files')
    parser.add_argument('--include-extensions', nargs='+',
                       default=['pdf', 'txt', 'json', 'csv', 'md', 'docx', 'xlsx'],
                       help='File extensions to include when processing directories')
    
    # Optional arguments
    parser.add_argument('--output', help='Output path for filled PDF')
    parser.add_argument('--ai-provider', choices=['pattern', 'openai', 'anthropic'], 
                       default='pattern', help='AI provider for extraction')
    parser.add_argument('--model', help='AI model to use (e.g., gpt-4o, claude-3-5-sonnet-20241022)')
    parser.add_argument('--api-key', help='API key for AI provider')
    parser.add_argument('--max-iterations', type=int, default=3, 
                       help='Maximum iterations for quality improvement')
    
    # Model discovery and selection
    parser.add_argument('--list-models', action='store_true',
                       help='List available models and exit')
    parser.add_argument('--recommend-model', choices=['legal_forms', 'data_extraction', 'simple_forms', 'complex_analysis'],
                       help='Get model recommendations for task type and exit')
    parser.add_argument('--budget-priority', action='store_true',
                       help='Prioritize cost-effective models in recommendations')
    parser.add_argument('--auto-select-model', action='store_true',
                       help='Automatically select best model for the task')
    
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Handle model discovery commands first (before other processing)
    if args.list_models or args.recommend_model:
        try:
            import llm_client
            
            # Get API keys
            openai_key = args.api_key if args.ai_provider == 'openai' else os.getenv("OPENAI_API_KEY")
            anthropic_key = args.api_key if args.ai_provider == 'anthropic' else os.getenv("ANTHROPIC_API_KEY")
            
            if args.list_models:
                print("🤖 Available AI Models")
                print("=" * 50)
                
                all_models = llm_client.get_all_available_models(openai_key, anthropic_key)
                
                if not all_models:
                    print("❌ No models available. Check your API keys:")
                    print("   export OPENAI_API_KEY='your-key-here'")
                    print("   export ANTHROPIC_API_KEY='your-key-here'")
                    sys.exit(1)
                
                # Group by provider
                providers = {}
                for model_id, info in all_models.items():
                    provider = info.get("provider", "unknown")
                    if provider not in providers:
                        providers[provider] = []
                    providers[provider].append((model_id, info))
                
                for provider, models in providers.items():
                    print(f"\n🔵 {provider.upper()} ({len(models)} models):")
                    for model_id, info in models:
                        context = info.get("context_window", 0)
                        cost = info.get("cost_tier", "unknown")
                        caps = ", ".join(info.get("capabilities", [])[:2])
                        print(f"  • {model_id}")
                        print(f"    Context: {context:,} tokens, Cost: {cost}, Capabilities: {caps}")
                
                print(f"\n💡 Usage example:")
                sample_model = list(all_models.keys())[0]
                sample_provider = all_models[sample_model].get("provider")
                print(f"   python3 agentic_form_filler.py --form form.pdf --sources data.pdf \\")
                print(f"     --ai-provider {sample_provider} --model {sample_model}")
                sys.exit(0)
            
            if args.recommend_model:
                print(f"🎯 Model Recommendations for: {args.recommend_model}")
                if args.budget_priority:
                    print("💰 Prioritizing cost-effective options")
                print("=" * 50)
                
                all_models = llm_client.get_all_available_models(openai_key, anthropic_key)
                
                if not all_models:
                    print("❌ No models available for recommendations")
                    sys.exit(1)
                
                recommendations = llm_client.recommend_model_for_task(
                    args.recommend_model, all_models, args.budget_priority
                )
                
                if not recommendations:
                    print(f"❌ No suitable models found for {args.recommend_model}")
                    sys.exit(1)
                
                print(f"📋 Top {len(recommendations)} recommendations:")
                
                for i, model_id in enumerate(recommendations[:3], 1):
                    model_info = all_models[model_id]
                    provider = model_info.get("provider", "unknown")
                    cost = model_info.get("cost_tier", "unknown")
                    context = model_info.get("context_window", 0)
                    description = model_info.get("description", "")
                    
                    print(f"\n{i}. 🤖 {model_id}")
                    print(f"   Provider: {provider.title()}")
                    print(f"   Cost: {cost.title()}")
                    print(f"   Context: {context:,} tokens")
                    print(f"   Description: {description}")
                    print(f"   Usage:")
                    print(f"     python3 agentic_form_filler.py --form form.pdf --sources data.pdf \\")
                    print(f"       --ai-provider {provider} --model {model_id}")
                
                sys.exit(0)
                
        except ImportError:
            print("❌ Model discovery requires llm_client.py")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error during model discovery: {e}")
            sys.exit(1)
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate required arguments (unless using discovery commands)
    if not args.list_models and not args.recommend_model:
        if not args.form:
            print("❌ Error: --form is required")
            print("   Use --list-models or --recommend-model for model discovery")
            sys.exit(1)
        
        if not args.sources:
            print("❌ Error: --sources is required")
            print("   Use --list-models or --recommend-model for model discovery")
            sys.exit(1)
    
    # Resolve and validate paths
    args.form = resolve_form_path(args.form)
    
    # Expand source patterns and directories
    print(f"🔍 Expanding source patterns: {args.sources}")
    args.sources = expand_source_files(args.sources)
    
    if args.verbose:
        print(f"📁 Resolved form: {args.form}")
        print(f"📁 Expanded sources ({len(args.sources)} files):")
        for src in args.sources[:10]:  # Show first 10
            print(f"   - {src}")
        if len(args.sources) > 10:
            print(f"   ... and {len(args.sources) - 10} more files")
    
    if not Path(args.form).exists():
        print(f"❌ Error: PDF form not found: {args.form}")
        print(f"   Searched in: {DEFAULT_FORMS_DIR}")
        sys.exit(1)
        
    # Check if we found any sources
    if not args.sources:
        print(f"❌ Error: No source files found matching patterns")
        print(f"   Patterns tried: {' '.join(sys.argv)}")
        print(f"   Searched in: {DEFAULT_DATA_DIR}")
        sys.exit(1)
        
    # Check data sources exist
    missing_sources = [src for src in args.sources if not Path(src).exists()]
    if missing_sources:
        print(f"❌ Error: {len(missing_sources)} source files not found:")
        for src in missing_sources[:5]:  # Show first 5
            print(f"   - {src}")
        if len(missing_sources) > 5:
            print(f"   ... and {len(missing_sources) - 5} more files")
        sys.exit(1)
    
    print(f"✅ Found {len(args.sources)} source files for processing")
    
    # Auto-select model if requested
    if args.auto_select_model and args.ai_provider != 'pattern':
        try:
            import llm_client
            
            # Get API keys
            openai_key = args.api_key if args.ai_provider == 'openai' else os.getenv("OPENAI_API_KEY")
            anthropic_key = args.api_key if args.ai_provider == 'anthropic' else os.getenv("ANTHROPIC_API_KEY")
            
            print(f"🤖 Auto-selecting best model for {args.ai_provider}...")
            
            all_models = llm_client.get_all_available_models(openai_key, anthropic_key)
            
            # Filter models by provider
            provider_models = {k: v for k, v in all_models.items() 
                             if v.get("provider") == args.ai_provider}
            
            if provider_models:
                # Determine task type based on context
                task_type = "legal_forms"  # Default for this application
                
                recommendations = llm_client.recommend_model_for_task(
                    task_type, provider_models, args.budget_priority
                )
                
                if recommendations:
                    args.model = recommendations[0]
                    model_info = provider_models[args.model]
                    print(f"✅ Auto-selected: {args.model}")
                    print(f"   Reason: {model_info.get('description', 'Best match for task')}")
                else:
                    print("⚠️ No specific recommendations, using provider default")
            else:
                print(f"⚠️ No models available for {args.ai_provider}")
                
        except Exception as e:
            print(f"⚠️ Auto-selection failed: {e}")
            print("   Continuing with manual model selection...")
    
    # Check for API key requirement
    if args.ai_provider in ['openai', 'anthropic'] and not args.api_key:
        # Try to get from environment
        env_key = f"{args.ai_provider.upper()}_API_KEY"
        args.api_key = os.getenv(env_key)
        
        if not args.api_key:
            print(f"❌ Error: API key required for {args.ai_provider}")
            print(f"   Set {env_key} environment variable or use --api-key")
            sys.exit(1)
    
    # Set default output path and resolve it
    if not args.output:
        form_path = Path(args.form)
        args.output = f"{form_path.stem}_filled.pdf"
    
    args.output = resolve_output_path(args.output)
    
    print(f"🚀 Starting Agentic PDF Form Filler...")
    print(f"📄 Form: {args.form}")
    print(f"📊 AI Provider: {args.ai_provider}")
    print(f"📝 Sources: {len(args.sources)} items")
    
    # Initialize orchestrator
    orchestrator = AgenticFormFillerOrchestrator(
        ai_provider=args.ai_provider,
        model=args.model or "",
        api_key=args.api_key or ""
    )
    
    # Process the form
    results = await orchestrator.process_form(
        pdf_path=args.form,
        sources=args.sources,
        output_path=args.output,
        max_iterations=args.max_iterations
    )
    
    # Print results
    print_results_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    asyncio.run(main())
