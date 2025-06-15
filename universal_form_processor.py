#!/usr/bin/env python3
"""
Universal Legal Form Processor - CLI for any form type and any client data
Designed for integration with n8n, APIs, and automation systems
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import subprocess
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('UniversalFormProcessor')

@dataclass
class FormFieldMapping:
    """Universal form field mapping"""
    source_field: str
    target_field: str
    value: str
    confidence: float = 0.0
    field_type: str = "text"  # text, checkbox, dropdown, date, currency
    validation_rule: str = ""

@dataclass
class ExtractionResult:
    """Universal extraction result"""
    extracted_fields: Dict[str, str]
    confidence_scores: Dict[str, float]
    field_types: Dict[str, str]
    form_type: str
    extraction_timestamp: str
    source_files: List[str]

    def __post_init__(self):
        if not self.extraction_timestamp:
            self.extraction_timestamp = datetime.now().isoformat()

class UniversalFormProcessor:
    """Universal form processor for any legal form type and client data"""
    
    def __init__(self, ai_provider: str = "anthropic", api_key: str = "", model: str = ""):
        self.ai_provider = ai_provider
        self.api_key = api_key
        self.model = model
        self.setup_ai()
    
    def setup_ai(self):
        """Set up AI configuration"""
        if self.ai_provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
            if not self.model:
                self.model = "claude-3-5-sonnet-20241022"
        elif self.ai_provider == "openai":
            os.environ["OPENAI_API_KEY"] = self.api_key
            if not self.model:
                self.model = "gpt-4-turbo"
    
    def extract_from_sources(self, source_paths: List[str], target_fields: List[str] = None) -> ExtractionResult:
        """Extract data from any source documents"""
        logger.info(f"Extracting data from {len(source_paths)} sources")
        
        try:
            import llm_client
            
            # Create universal extraction prompt
            prompt = self._create_universal_extraction_prompt(target_fields)
            
            # Process each source
            all_extracted_data = {}
            all_confidence_scores = {}
            detected_form_types = []
            
            for source_path in source_paths:
                logger.info(f"Processing: {Path(source_path).name}")
                
                if self.ai_provider == "anthropic":
                    # Add PDF path for Claude vision
                    source_prompt = f"[PDF_PATH: {source_path}]\n\n{prompt}"
                    response = llm_client.generate_with_claude(self.model, source_prompt)
                elif self.ai_provider == "openai":
                    response = llm_client.generate_with_openai(self.model, prompt)
                else:
                    # Pattern matching fallback
                    response = self._pattern_extract_universal(source_path, target_fields)
                
                # Parse response
                extracted, confidence, form_type = self._parse_universal_response(response)
                all_extracted_data.update(extracted)
                all_confidence_scores.update(confidence)
                if form_type:
                    detected_form_types.append(form_type)
            
            # Determine field types
            field_types = self._infer_field_types(all_extracted_data)
            
            result = ExtractionResult(
                extracted_fields=all_extracted_data,
                confidence_scores=all_confidence_scores,
                field_types=field_types,
                form_type=", ".join(set(detected_form_types)) if detected_form_types else "Unknown",
                extraction_timestamp=datetime.now().isoformat(),
                source_files=[str(Path(p).name) for p in source_paths]
            )
            
            logger.info(f"Extraction complete: {len(all_extracted_data)} fields extracted")
            return result
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def _create_universal_extraction_prompt(self, target_fields: List[str] = None) -> str:
        """Create universal extraction prompt that works for any form type"""
        
        field_guidance = ""
        if target_fields:
            field_guidance = f"""
TARGET FIELDS TO EXTRACT (if found):
{json.dumps(target_fields, indent=2)}
"""
        
        return f"""
You are a universal legal document data extractor. Extract ALL relevant information from any type of legal form or document.

{field_guidance}

Extract data and return ONLY a JSON object with this structure:

{{
    "extracted_data": {{
        "field_name": "actual_value_found"
    }},
    "confidence_scores": {{
        "field_name": 0.95
    }},
    "form_type": "detected_form_type",
    "field_types": {{
        "field_name": "text|date|currency|checkbox|dropdown"
    }}
}}

UNIVERSAL EXTRACTION RULES:
1. Extract ALL filled-in values, regardless of form type
2. Use descriptive field names based on the content:
   - Personal info: "full_name", "first_name", "last_name", "address", "phone", "email"
   - Case info: "case_number", "court_name", "filing_date"
   - Legal parties: "petitioner_name", "respondent_name", "plaintiff_name", "defendant_name"
   - Financial: "total_assets", "total_debts", "income", "expenses", "child_support"
   - Property: "real_estate", "vehicles", "bank_accounts", "investments"
   - Children: "child_name", "child_dob", "child_age", "custody_arrangement"
   - Dates: "marriage_date", "separation_date", "service_date", "hearing_date"
   - Legal representation: "attorney_name", "attorney_firm", "attorney_phone", "attorney_email", "bar_number"

3. FIELD TYPE DETECTION:
   - "text": Regular text fields
   - "date": Dates in any format
   - "currency": Dollar amounts ($1,234.56)
   - "checkbox": Yes/No, checked/unchecked values
   - "dropdown": Options from a list

4. VALUE EXTRACTION:
   - For currency: Include $ and formatting ("$1,234.56")
   - For dates: Preserve original format
   - For checkboxes: Use "Yes"/"No" or "Checked"/"Unchecked"
   - For names: Extract full names as written
   - For addresses: Extract complete address strings
   - For phone: Preserve formatting "(555) 123-4567"

5. CONFIDENCE SCORING:
   - 0.95+: Clearly labeled field with obvious value
   - 0.8-0.94: Value found but field label unclear
   - 0.6-0.79: Inferred value based on context
   - 0.4-0.59: Possible value, low confidence
   - <0.4: Very uncertain

6. FORM TYPE DETECTION:
   Look for form headers, titles, or identifiers like:
   - "FL-120", "FL-142", "FL-105" (California family law)
   - "Petition", "Response", "Motion", "Declaration"
   - "Divorce", "Custody", "Support", "Assets", "Debts"
   - "Bankruptcy", "Probate", "Civil", "Criminal"

Extract ONLY actual filled-in values, not empty fields or form instructions.
Return only valid JSON with the exact structure above.
"""
    
    def _parse_universal_response(self, response: str) -> Tuple[Dict[str, str], Dict[str, float], str]:
        """Parse AI response for universal extraction"""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_text = response[start:end]
                data = json.loads(json_text)
                
                extracted = data.get("extracted_data", {})
                confidence = data.get("confidence_scores", {})
                form_type = data.get("form_type", "")
                
                # Remove null values
                extracted = {k: v for k, v in extracted.items() if v and v != "null"}
                confidence = {k: v for k, v in confidence.items() if k in extracted}
                
                return extracted, confidence, form_type
            else:
                logger.warning("No JSON found in AI response")
                return {}, {}, ""
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {}, {}, ""
    
    def _infer_field_types(self, extracted_data: Dict[str, str]) -> Dict[str, str]:
        """Infer field types from extracted data"""
        field_types = {}
        
        for field_name, value in extracted_data.items():
            field_types[field_name] = self._detect_field_type(field_name, value)
        
        return field_types
    
    def _detect_field_type(self, field_name: str, value: str) -> str:
        """Detect field type based on name and value"""
        field_lower = field_name.lower()
        value_str = str(value).strip()
        
        # Currency detection
        if ('$' in value_str or 
            'amount' in field_lower or 'total' in field_lower or 
            'income' in field_lower or 'debt' in field_lower or
            'asset' in field_lower or 'support' in field_lower):
            return "currency"
        
        # Date detection
        if ('date' in field_lower or 'dob' in field_lower or
            re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', value_str) or
            re.search(r'\d{4}-\d{2}-\d{2}', value_str)):
            return "date"
        
        # Checkbox detection
        if (value_str.lower() in ['yes', 'no', 'true', 'false', 'checked', 'unchecked', 'x'] or
            'check' in field_lower or 'select' in field_lower):
            return "checkbox"
        
        # Default to text
        return "text"
    
    def _pattern_extract_universal(self, source_path: str, target_fields: List[str] = None) -> str:
        """Universal pattern-based extraction fallback"""
        try:
            # Simple pattern matching for common legal form data
            patterns = {
                'case_number': r'(?i)case\s*(?:number|no\.?|#)\s*:?\s*([A-Z0-9\-]+)',
                'phone': r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                'date': r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
                'currency': r'\$\s*([0-9,]+(?:\.[0-9]{2})?)',
                'full_name': r'(?i)(?:name|petitioner|respondent|plaintiff|defendant)\s*:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            }
            
            extracted = {}
            confidence = {}
            
            # Simple text extraction from file
            try:
                with open(source_path, 'rb') as f:
                    content = str(f.read())
                    
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        if isinstance(matches[0], tuple):
                            # For phone numbers
                            extracted[pattern_name] = f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
                        else:
                            extracted[pattern_name] = str(matches[0])
                        confidence[pattern_name] = 0.7
            except:
                # If file reading fails, return empty
                pass
            
            return json.dumps({
                "extracted_data": extracted,
                "confidence_scores": confidence,
                "form_type": "Pattern Extracted",
                "field_types": {k: self._detect_field_type(k, v) for k, v in extracted.items()}
            })
            
        except Exception as e:
            logger.error(f"Pattern extraction error: {e}")
            return '{"extracted_data": {}, "confidence_scores": {}, "form_type": "Error"}'
    
    def export_extraction(self, result: ExtractionResult, format: str = "json") -> str:
        """Export extraction result in various formats"""
        if format == "json":
            return json.dumps(asdict(result), indent=2, default=str)
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            fieldnames = ['field_name', 'value', 'confidence', 'field_type']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for field_name, value in result.extracted_fields.items():
                writer.writerow({
                    'field_name': field_name,
                    'value': value,
                    'confidence': result.confidence_scores.get(field_name, 0.0),
                    'field_type': result.field_types.get(field_name, 'text')
                })
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

def main():
    """Universal CLI interface"""
    parser = argparse.ArgumentParser(
        description="Universal Legal Form Processor - Works with any form type and client data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract data from any legal documents
  python3 universal_form_processor.py extract --sources document1.pdf document2.pdf --output extracted_data.json
  
  # Extract with specific target fields
  python3 universal_form_processor.py extract --sources doc.pdf --target-fields case_number petitioner_name --output data.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract data from any documents')
    extract_parser.add_argument('--sources', nargs='+', required=True, help='Source documents to extract from')
    extract_parser.add_argument('--output', required=True, help='Output file for extracted data')
    extract_parser.add_argument('--ai-provider', choices=['anthropic', 'openai', 'pattern'], default='anthropic')
    extract_parser.add_argument('--model', help='AI model to use')
    extract_parser.add_argument('--api-key', help='AI API key')
    extract_parser.add_argument('--format', choices=['json', 'csv'], default='json')
    extract_parser.add_argument('--target-fields', nargs='*', help='Specific fields to extract')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        processor = UniversalFormProcessor(
            ai_provider=getattr(args, 'ai_provider', 'anthropic'),
            api_key=getattr(args, 'api_key', os.getenv('ANTHROPIC_API_KEY', '')),
            model=getattr(args, 'model', '')
        )
        
        if args.command == 'extract':
            # Extract data from sources
            result = processor.extract_from_sources(
                args.sources, 
                getattr(args, 'target_fields', None)
            )
            
            # Export result
            output_text = processor.export_extraction(result, args.format)
            
            with open(args.output, 'w') as f:
                f.write(output_text)
            
            print(f"✅ Data extracted from {len(args.sources)} sources")
            print(f"📊 Found {len(result.extracted_fields)} fields")
            print(f"📋 Form type: {result.form_type}")
            print(f"💾 Saved to: {args.output}")
            
            # Show extracted fields
            print(f"\n📋 EXTRACTED FIELDS:")
            for field_name, value in result.extracted_fields.items():
                confidence = result.confidence_scores.get(field_name, 0.0)
                field_type = result.field_types.get(field_name, 'text')
                print(f"  {field_name}: {value} ({field_type}, {confidence:.1%})")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"CLI Error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
