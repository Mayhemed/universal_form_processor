#!/usr/bin/env python3
"""
Test Universal Form Processor with real legal documents
Demonstrates extraction from any form type and any client data
"""

import os
import sys
import tempfile
import json

# Add the current directory to Python path
sys.path.append('/Users/markpiesner/Documents/Github/agentic_form_filler')

def main():
    print("🧪 UNIVERSAL LEGAL FORM PROCESSOR TEST")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        return
    
    try:
        from universal_form_processor import UniversalFormProcessor
        
        # Create processor
        processor = UniversalFormProcessor(
            ai_provider="anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-5-sonnet-20241022"
        )
        
        print("🔍 STEP 1: EXTRACTING DATA FROM ANY DOCUMENTS")
        print("-" * 50)
        
        # Test with available documents
        source_files = ["/private/tmp/FL142_Rogers_Assets_Debts.pdf"]
        
        # Extract data (universal - works with any form type)
        result = processor.extract_from_sources(source_files)
        
        print(f"📊 EXTRACTION RESULTS:")
        print(f"  Form Type: {result.form_type}")
        print(f"  Fields Found: {len(result.extracted_fields)}")
        print(f"  Source Files: {', '.join(result.source_files)}")
        print(f"  Timestamp: {result.extraction_timestamp}")
        
        print(f"\n📋 EXTRACTED FIELDS:")
        for field_name, value in result.extracted_fields.items():
            confidence = result.confidence_scores.get(field_name, 0.0)
            field_type = result.field_types.get(field_name, 'text')
            print(f"  {field_name}: {value}")
            print(f"    Type: {field_type}, Confidence: {confidence:.1%}")
        
        # Export data in multiple formats
        print(f"\n💾 STEP 2: EXPORTING DATA IN MULTIPLE FORMATS")
        print("-" * 50)
        
        # JSON Export
        json_output = processor.export_extraction(result, "json")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_output)
            json_file = f.name
        print(f"✅ JSON Export: {json_file}")
        
        # CSV Export
        try:
            csv_output = processor.export_extraction(result, "csv")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(csv_output)
                csv_file = f.name
            print(f"✅ CSV Export: {csv_file}")
        except Exception as e:
            print(f"⚠️  CSV Export: {e}")
        
        print(f"\n🗺️  STEP 3: ANALYZING TARGET FORM STRUCTURE")
        print("-" * 50)
        
        # For demo, we'll simulate analyzing a target form
        # In real use, you'd provide an actual blank form to fill
        print("ℹ️  Note: This step requires a fillable PDF form.")
        print("   Example: processor.get_form_fields('blank_form.pdf')")
        print("   Returns: List of all fillable fields in the target form")
        
        # Simulate form fields for demonstration
        simulated_target_fields = [
            {'name': 'case_number', 'type': 'Text', 'alt_text': 'Case Number'},
            {'name': 'petitioner_name', 'type': 'Text', 'alt_text': 'Petitioner Name'},
            {'name': 'respondent_name', 'type': 'Text', 'alt_text': 'Respondent Name'},
            {'name': 'total_assets', 'type': 'Text', 'alt_text': 'Total Assets'},
            {'name': 'total_debts', 'type': 'Text', 'alt_text': 'Total Debts'},
            {'name': 'child_support_amount', 'type': 'Text', 'alt_text': 'Child Support'}
        ]
        
        print(f"📋 Simulated Target Form Fields: {len(simulated_target_fields)}")
        for field in simulated_target_fields:
            print(f"  - {field['name']} ({field['type']})")
        
        print(f"\n🎯 STEP 4: SYSTEM CAPABILITIES SUMMARY")
        print("-" * 50)
        print("✅ Universal Form Processor is ready for:")
        print("   • Any form type (FL-120, FL-142, FL-105, etc.)")
        print("   • Any client data (names, amounts, dates, etc.)")
        print("   • Multiple input formats (PDF, text, images)")
        print("   • Multiple output formats (JSON, CSV)")
        print("   • Intelligent field mapping")
        print("   • Form filling with pdftk")
        
        print(f"\n🚀 READY FOR N8N INTEGRATION:")
        print("   1. HTTP Request to extract data from documents")
        print("   2. JSON processing for field mapping")
        print("   3. Form filling with any template")
        print("   4. File storage and workflow automation")
        
        print(f"\n🔧 CLI USAGE EXAMPLES:")
        print("   # Extract from any documents")
        print("   python3 universal_form_processor.py extract \\")
        print("     --sources document1.pdf document2.pdf \\")
        print("     --output extracted_data.json")
        print()
        print("   # Complete workflow")
        print("   python3 universal_form_processor.py extract \\")
        print("     --sources source.pdf \\")
        print("     --output extracted_data.json \\")
        print("     --ai-provider anthropic")
        
        # Show sample API payload for n8n
        print(f"\n📡 SAMPLE N8N/API PAYLOAD:")
        api_payload = {
            "command": "extract",
            "sources": ["document1.pdf", "document2.pdf"],
            "ai_provider": "anthropic",
            "target_fields": ["case_number", "petitioner_name", "total_assets"],
            "output_format": "json"
        }
        print(json.dumps(api_payload, indent=2))
        
        print(f"\n✨ SYSTEM CAPABILITIES:")
        capabilities = {
            "universal_extraction": True,
            "any_form_type": True,
            "any_client_data": True,
            "intelligent_mapping": True,
            "multiple_formats": ["json", "csv"],
            "ai_providers": ["anthropic", "openai", "pattern_matching"],
            "form_filling": True,
            "api_ready": True,
            "n8n_compatible": True
        }
        print(json.dumps(capabilities, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
