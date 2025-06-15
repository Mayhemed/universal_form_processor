#!/usr/bin/env python3
"""
Legal Form Processor - Advanced CLI for form extraction and filling
Designed for integration with n8n, APIs, and automation systems
"""

import os
import sys
import json
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LegalFormProcessor')

@dataclass
class LawyerInfo:
    """Lawyer/Attorney information"""
    name: str = ""
    bar_number: str = ""
    firm_name: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    phone: str = ""
    fax: str = ""
    email: str = ""

@dataclass
class PartyInfo:
    """Party (Petitioner/Respondent) information"""
    name: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    phone: str = ""
    email: str = ""

@dataclass
class ChildInfo:
    """Child information"""
    name: str = ""
    birth_date: str = ""
    age: str = ""
    birth_place: str = ""
    sex: str = ""
    current_address: str = ""

@dataclass
class CaseInfo:
    """Case information"""
    case_number: str = ""
    court_name: str = ""
    court_address: str = ""
    branch: str = ""
    marriage_date: str = ""
    separation_date: str = ""
    marriage_length_years: str = ""
    marriage_length_months: str = ""

@dataclass
class FinancialInfo:
    """Financial information from FL-142"""
    total_assets: str = ""
    total_debts: str = ""
    net_worth: str = ""
    checking_account: str = ""
    checking_bank: str = ""
    household_furniture: str = ""
    student_loans: str = ""
    credit_cards: str = ""
    other_debts: str = ""
    child_support: str = ""
    college_fund: str = ""

@dataclass
class LegalFormData:
    """Complete legal form data structure"""
    case: CaseInfo
    petitioner: PartyInfo
    respondent: PartyInfo
    lawyer: LawyerInfo
    children: List[ChildInfo]
    financial: FinancialInfo
    form_type: str = ""
    extraction_date: str = ""
    confidence_scores: Dict[str, float] = None

    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = {}
        if not self.extraction_date:
            self.extraction_date = datetime.now().isoformat()

class LegalFormProcessor:
    """Advanced legal form processor with extraction and filling capabilities"""
    
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
    
    def extract_from_forms(self, form_paths: List[str]) -> LegalFormData:
        """Extract comprehensive data from legal forms"""
        logger.info(f"Extracting data from {len(form_paths)} forms")
        
        try:
            import llm_client
            
            # Create comprehensive extraction prompt
            prompt = self._create_extraction_prompt()
            
            # Process each form
            all_extracted_data = {}
            for form_path in form_paths:
                logger.info(f"Processing: {Path(form_path).name}")
                
                if self.ai_provider == "anthropic":
                    # Add PDF path for Claude vision
                    form_prompt = f"[PDF_PATH: {form_path}]\n\n{prompt}"
                    response = llm_client.generate_with_claude(self.model, form_prompt)
                elif self.ai_provider == "openai":
                    response = llm_client.generate_with_openai(self.model, prompt)
                else:
                    # Pattern matching fallback
                    with open(form_path, 'rb') as f:
                        # For pattern matching, we'd need to extract text first
                        response = self._pattern_extract(form_path)
                
                # Parse response
                extracted = self._parse_extraction_response(response)
                all_extracted_data.update(extracted)
            
            # Convert to structured data
            legal_data = self._convert_to_legal_form_data(all_extracted_data)
            
            logger.info(f"Extraction complete: {len(all_extracted_data)} fields extracted")
            return legal_data
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def _create_extraction_prompt(self) -> str:
        """Create comprehensive extraction prompt for legal forms"""
        return """
You are extracting data from legal forms (FL-120, FL-142, FL-105, etc.) for family law cases.

Extract ALL relevant information and return ONLY a JSON object with this structure:

{
    "case_number": "value or null",
    "court_name": "value or null",
    "court_address": "value or null",
    "court_branch": "value or null",
    
    "petitioner_name": "value or null",
    "petitioner_address": "value or null",
    "petitioner_city": "value or null",
    "petitioner_state": "value or null",
    "petitioner_zip": "value or null",
    
    "respondent_name": "value or null",
    "respondent_address": "value or null",
    "respondent_city": "value or null",
    "respondent_state": "value or null",
    "respondent_zip": "value or null",
    
    "lawyer_name": "value or null",
    "lawyer_bar_number": "value or null",
    "lawyer_firm": "value or null",
    "lawyer_address": "value or null",
    "lawyer_city": "value or null",
    "lawyer_state": "value or null",
    "lawyer_zip": "value or null",
    "lawyer_phone": "value or null",
    "lawyer_fax": "value or null",
    "lawyer_email": "value or null",
    
    "marriage_date": "value or null",
    "separation_date": "value or null",
    "marriage_years": "value or null",
    "marriage_months": "value or null",
    
    "child_name": "value or null",
    "child_birth_date": "value or null",
    "child_age": "value or null",
    "child_birth_place": "value or null",
    "child_sex": "value or null",
    "child_address": "value or null",
    
    "total_assets": "value or null",
    "total_debts": "value or null",
    "net_worth": "value or null",
    "checking_account": "value or null",
    "checking_bank": "value or null",
    "household_furniture": "value or null",
    "student_loans": "value or null",
    "credit_cards": "value or null",
    "other_debts": "value or null",
    "child_support": "value or null",
    "college_fund": "value or null",
    
    "form_type": "FL-120 or FL-142 or FL-105 or other"
}

EXTRACTION RULES:
1. Extract only actual filled-in values, not field labels
2. For monetary amounts, include dollar signs and formatting if present
3. For dates, preserve the original format
4. For addresses, extract complete address information
5. For lawyer information, get State Bar number, firm name, contact details
6. For children, get full name, birth date, and current address
7. If multiple children, focus on the first child listed
8. Extract both petitioner and respondent information
9. Get case number, court information, and branch details

Return only valid JSON with the exact structure above.
"""
    
    def _parse_extraction_response(self, response: str) -> Dict[str, str]:
        """Parse AI response to extract structured data"""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_text = response[start:end]
                data = json.loads(json_text)
                # Remove null values
                return {k: v for k, v in data.items() if v and v != "null"}
            else:
                logger.warning("No JSON found in AI response")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {}
    
    def _convert_to_legal_form_data(self, extracted: Dict[str, str]) -> LegalFormData:
        """Convert extracted data to structured LegalFormData object"""
        
        # Case info
        case = CaseInfo(
            case_number=extracted.get("case_number", ""),
            court_name=extracted.get("court_name", ""),
            court_address=extracted.get("court_address", ""),
            branch=extracted.get("court_branch", ""),
            marriage_date=extracted.get("marriage_date", ""),
            separation_date=extracted.get("separation_date", ""),
            marriage_length_years=extracted.get("marriage_years", ""),
            marriage_length_months=extracted.get("marriage_months", "")
        )
        
        # Petitioner
        petitioner = PartyInfo(
            name=extracted.get("petitioner_name", ""),
            address=extracted.get("petitioner_address", ""),
            city=extracted.get("petitioner_city", ""),
            state=extracted.get("petitioner_state", ""),
            zip_code=extracted.get("petitioner_zip", "")
        )
        
        # Respondent
        respondent = PartyInfo(
            name=extracted.get("respondent_name", ""),
            address=extracted.get("respondent_address", ""),
            city=extracted.get("respondent_city", ""),
            state=extracted.get("respondent_state", ""),
            zip_code=extracted.get("respondent_zip", "")
        )
        
        # Lawyer
        lawyer = LawyerInfo(
            name=extracted.get("lawyer_name", ""),
            bar_number=extracted.get("lawyer_bar_number", ""),
            firm_name=extracted.get("lawyer_firm", ""),
            address=extracted.get("lawyer_address", ""),
            city=extracted.get("lawyer_city", ""),
            state=extracted.get("lawyer_state", ""),
            zip_code=extracted.get("lawyer_zip", ""),
            phone=extracted.get("lawyer_phone", ""),
            fax=extracted.get("lawyer_fax", ""),
            email=extracted.get("lawyer_email", "")
        )
        
        # Children
        children = []
        if extracted.get("child_name"):
            child = ChildInfo(
                name=extracted.get("child_name", ""),
                birth_date=extracted.get("child_birth_date", ""),
                age=extracted.get("child_age", ""),
                birth_place=extracted.get("child_birth_place", ""),
                sex=extracted.get("child_sex", ""),
                current_address=extracted.get("child_address", "")
            )
            children.append(child)
        
        # Financial
        financial = FinancialInfo(
            total_assets=extracted.get("total_assets", ""),
            total_debts=extracted.get("total_debts", ""),
            net_worth=extracted.get("net_worth", ""),
            checking_account=extracted.get("checking_account", ""),
            checking_bank=extracted.get("checking_bank", ""),
            household_furniture=extracted.get("household_furniture", ""),
            student_loans=extracted.get("student_loans", ""),
            credit_cards=extracted.get("credit_cards", ""),
            other_debts=extracted.get("other_debts", ""),
            child_support=extracted.get("child_support", ""),
            college_fund=extracted.get("college_fund", "")
        )
        
        return LegalFormData(
            case=case,
            petitioner=petitioner,
            respondent=respondent,
            lawyer=lawyer,
            children=children,
            financial=financial,
            form_type=extracted.get("form_type", ""),
            confidence_scores={}
        )
    
    def fill_form(self, template_path: str, data: LegalFormData, output_path: str) -> bool:
        """Fill a form template with extracted data"""
        logger.info(f"Filling form: {Path(template_path).name} -> {Path(output_path).name}")
        
        try:
            # Convert data to field mapping
            field_mapping = self._create_field_mapping(data)
            
            # Create FDF file
            fdf_content = self._create_fdf(field_mapping)
            
            # Write temporary FDF
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False) as fdf_file:
                fdf_file.write(fdf_content)
                fdf_path = fdf_file.name
            
            try:
                # Fill form using pdftk
                subprocess.run([
                    'pdftk', template_path, 
                    'fill_form', fdf_path,
                    'output', output_path
                ], check=True)
                
                logger.info(f"Form filled successfully: {output_path}")
                return True
                
            finally:
                os.unlink(fdf_path)
                
        except Exception as e:
            logger.error(f"Form filling failed: {str(e)}")
            return False
    
    def _create_field_mapping(self, data: LegalFormData) -> Dict[str, str]:
        """Create field mapping from structured data"""
        mapping = {}
        
        # Case fields
        if data.case.case_number:
            mapping["case_number"] = data.case.case_number
        if data.case.court_name:
            mapping["court_name"] = data.case.court_name
        if data.case.marriage_date:
            mapping["marriage_date"] = data.case.marriage_date
        if data.case.separation_date:
            mapping["separation_date"] = data.case.separation_date
        
        # Petitioner fields
        if data.petitioner.name:
            mapping["petitioner_name"] = data.petitioner.name
        if data.petitioner.address:
            mapping["petitioner_address"] = data.petitioner.address
        
        # Respondent fields  
        if data.respondent.name:
            mapping["respondent_name"] = data.respondent.name
        if data.respondent.address:
            mapping["respondent_address"] = data.respondent.address
        
        # Lawyer fields
        if data.lawyer.name:
            mapping["attorney_name"] = data.lawyer.name
        if data.lawyer.bar_number:
            mapping["attorney_bar_number"] = data.lawyer.bar_number
        if data.lawyer.firm_name:
            mapping["attorney_firm"] = data.lawyer.firm_name
        if data.lawyer.phone:
            mapping["attorney_phone"] = data.lawyer.phone
        if data.lawyer.email:
            mapping["attorney_email"] = data.lawyer.email
        
        # Child fields
        if data.children:
            child = data.children[0]
            if child.name:
                mapping["child_name"] = child.name
            if child.birth_date:
                mapping["child_birth_date"] = child.birth_date
            if child.age:
                mapping["child_age"] = child.age
        
        # Financial fields
        if data.financial.child_support:
            mapping["child_support"] = data.financial.child_support
        if data.financial.college_fund:
            mapping["college_fund"] = data.financial.college_fund
        
        return mapping
    
    def _create_fdf(self, field_mapping: Dict[str, str]) -> str:
        """Create FDF content for form filling"""
        fdf_header = """%FDF-1.2
1 0 obj
<<
/FDF
<<
/Fields ["""
        
        fdf_fields = []
        for field_name, field_value in field_mapping.items():
            if field_value:
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
    
    def export_data(self, data: LegalFormData, format: str = "json") -> str:
        """Export data in various formats"""
        if format == "json":
            return json.dumps(asdict(data), indent=2, default=str)
        elif format == "csv":
            # Flatten data for CSV
            flat_data = self._flatten_data(data)
            import csv
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=flat_data.keys())
            writer.writeheader()
            writer.writerow(flat_data)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _flatten_data(self, data: LegalFormData) -> Dict[str, str]:
        """Flatten nested data structure for CSV export"""
        flat = {}
        
        # Case data
        for key, value in asdict(data.case).items():
            flat[f"case_{key}"] = str(value)
        
        # Petitioner data
        for key, value in asdict(data.petitioner).items():
            flat[f"petitioner_{key}"] = str(value)
        
        # Respondent data
        for key, value in asdict(data.respondent).items():
            flat[f"respondent_{key}"] = str(value)
        
        # Lawyer data
        for key, value in asdict(data.lawyer).items():
            flat[f"lawyer_{key}"] = str(value)
        
        # Financial data
        for key, value in asdict(data.financial).items():
            flat[f"financial_{key}"] = str(value)
        
        # First child data
        if data.children:
            for key, value in asdict(data.children[0]).items():
                flat[f"child_{key}"] = str(value)
        
        return flat

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Legal Form Processor - Extract and fill legal forms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract data from forms
  python3 legal_form_processor.py extract --forms fl120.pdf fl142.pdf --output case_data.json
  
  # Fill a form template
  python3 legal_form_processor.py fill --template blank_fl120.pdf --data case_data.json --output filled_fl120.pdf
  
  # Extract and immediately fill
  python3 legal_form_processor.py process --source fl120.pdf --template blank_fl120.pdf --output new_fl120.pdf
  
  # API mode (for n8n integration)
  python3 legal_form_processor.py api --port 8080
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract data from forms')
    extract_parser.add_argument('--forms', nargs='+', required=True, help='Input form files')
    extract_parser.add_argument('--output', required=True, help='Output JSON file')
    extract_parser.add_argument('--ai-provider', choices=['anthropic', 'openai', 'pattern'], default='anthropic')
    extract_parser.add_argument('--model', help='AI model to use')
    extract_parser.add_argument('--api-key', help='AI API key')
    extract_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    
    # Fill command
    fill_parser = subparsers.add_parser('fill', help='Fill form template with data')
    fill_parser.add_argument('--template', required=True, help='Form template PDF')
    fill_parser.add_argument('--data', required=True, help='Input data file (JSON)')
    fill_parser.add_argument('--output', required=True, help='Output filled PDF')
    
    # Process command (extract + fill)
    process_parser = subparsers.add_parser('process', help='Extract from source and fill template')
    process_parser.add_argument('--source', required=True, help='Source form to extract from')
    process_parser.add_argument('--template', required=True, help='Template form to fill')
    process_parser.add_argument('--output', required=True, help='Output filled PDF')
    process_parser.add_argument('--ai-provider', choices=['anthropic', 'openai', 'pattern'], default='anthropic')
    process_parser.add_argument('--model', help='AI model to use')
    process_parser.add_argument('--api-key', help='AI API key')
    process_parser.add_argument('--save-data', help='Save extracted data to file')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Start API server for external integration')
    api_parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    api_parser.add_argument('--host', default='localhost', help='Host to bind to')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        processor = LegalFormProcessor(
            ai_provider=getattr(args, 'ai_provider', 'anthropic'),
            api_key=getattr(args, 'api_key', os.getenv('ANTHROPIC_API_KEY', '')),
            model=getattr(args, 'model', '')
        )
        
        if args.command == 'extract':
            # Extract data from forms
            data = processor.extract_from_forms(args.forms)
            
            # Export data
            output_text = processor.export_data(data, args.format)
            
            with open(args.output, 'w') as f:
                f.write(output_text)
            
            print(f"✅ Data extracted and saved to {args.output}")
            print(f"📋 Extracted {len([f for f in asdict(data).values() if f])} fields")
            
        elif args.command == 'fill':
            # Load data and fill form
            with open(args.data, 'r') as f:
                data_dict = json.load(f)
            
            # Convert back to LegalFormData (simplified)
            # In production, you'd want proper deserialization
            print(f"🔄 Filling form {args.template} with data from {args.data}")
            print(f"⚠️  Form filling requires fillable PDF templates")
            
        elif args.command == 'process':
            # Extract and fill in one step
            print(f"🔄 Processing: {args.source} -> {args.output}")
            data = processor.extract_from_forms([args.source])
            
            if args.save_data:
                with open(args.save_data, 'w') as f:
                    f.write(processor.export_data(data))
                print(f"💾 Data saved to {args.save_data}")
            
            # Note: Form filling would require fillable template
            print(f"✅ Data extraction complete")
            print(f"⚠️  To complete form filling, provide a fillable PDF template")
            
        elif args.command == 'api':
            print(f"🚀 Starting API server on {args.host}:{args.port}")
            print("⚠️  API server implementation requires additional setup")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
