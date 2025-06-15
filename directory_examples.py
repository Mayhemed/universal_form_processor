#!/usr/bin/env python3
"""
Example: Directory Configuration Usage
Shows different ways to configure and use directories with the Universal Form Processor
"""

import os
import subprocess
from pathlib import Path

def example_1_default_directories():
    """Example 1: Using default directory structure"""
    print("📁 Example 1: Default Directory Structure")
    print("="*50)
    
    # This assumes you have:
    # forms/sample_form.pdf
    # data/sample_data.txt
    
    cmd = [
        "python3", "agentic_form_filler.py",
        "--form", "sample_form.pdf",           # Looks in ./forms/
        "--sources", "sample_data.txt",        # Looks in ./data/
        "--output", "sample_filled.pdf",       # Saves to ./output/
        "--ai-provider", "pattern"              # No API key needed
    ]
    
    print("Command:")
    print(" ".join(cmd))
    print("\nThis will:")
    print("• Look for form in: ./forms/sample_form.pdf")
    print("• Look for data in: ./data/sample_data.txt") 
    print("• Save output to: ./output/sample_filled.pdf")
    print()

def example_2_environment_variables():
    """Example 2: Using environment variables"""
    print("📁 Example 2: Environment Variables")
    print("="*50)
    
    # Set custom directories
    os.environ['FORMS_DIR'] = '/Users/lawyer/legal_forms'
    os.environ['DATA_DIR'] = '/Users/lawyer/client_data'
    os.environ['OUTPUT_DIR'] = '/Users/lawyer/completed_forms'
    
    cmd = [
        "python3", "agentic_form_filler.py",
        "--form", "family_law/divorce_petition.pdf",
        "--sources", "2024/smith_case/intake.pdf", "2024/smith_case/financial.txt",
        "--output", "2024/smith_divorce_filled.pdf",
        "--ai-provider", "anthropic"
    ]
    
    print("Environment variables:")
    print(f"FORMS_DIR={os.environ['FORMS_DIR']}")
    print(f"DATA_DIR={os.environ['DATA_DIR']}")
    print(f"OUTPUT_DIR={os.environ['OUTPUT_DIR']}")
    print()
    
    print("Command:")
    print(" ".join(cmd))
    print("\nThis will:")
    print("• Look for form in: /Users/lawyer/legal_forms/family_law/divorce_petition.pdf")
    print("• Look for data in: /Users/lawyer/client_data/2024/smith_case/")
    print("• Save output to: /Users/lawyer/completed_forms/2024/smith_divorce_filled.pdf")
    print()

def example_3_absolute_paths():
    """Example 3: Using absolute paths"""
    print("📁 Example 3: Absolute Paths")
    print("="*50)
    
    cmd = [
        "python3", "agentic_form_filler.py",
        "--form", "/Users/lawyer/forms/bankruptcy/chapter7_petition.pdf",
        "--sources", 
            "/Users/lawyer/clients/jones_case/debtor_info.pdf",
            "/Users/lawyer/clients/jones_case/creditor_list.xlsx",
        "--output", "/Users/lawyer/completed/2024/jones_chapter7_filled.pdf",
        "--ai-provider", "openai",
        "--model", "gpt-4",
        "--max-iterations", "3"
    ]
    
    print("Command:")
    print("\\\n  ".join(cmd))
    print("\nThis will:")
    print("• Use exact paths specified")
    print("• No directory resolution needed")
    print("• Maximum control over file locations")
    print()

def example_4_legal_practice_workflow():
    """Example 4: Real legal practice workflow"""
    print("📁 Example 4: Legal Practice Workflow")
    print("="*50)
    
    # Simulate a law firm's directory structure
    practice_dirs = {
        'FORMS_DIR': '/Users/lawyer/LegalPractice/forms',
        'DATA_DIR': '/Users/lawyer/LegalPractice/clients', 
        'OUTPUT_DIR': '/Users/lawyer/LegalPractice/completed'
    }
    
    # Different case types
    cases = [
        {
            'name': 'Divorce Case - Smith',
            'form': 'family_law/california_divorce_petition.pdf',
            'sources': ['active/smith_case/client_intake.pdf', 'active/smith_case/financial_disclosure.txt'],
            'output': '2024/family_law/smith_divorce_petition.pdf'
        },
        {
            'name': 'Bankruptcy Case - Jones', 
            'form': 'bankruptcy/chapter7_petition.pdf',
            'sources': ['active/jones_case/debtor_schedule.pdf', 'active/jones_case/creditor_matrix.xlsx'],
            'output': '2024/bankruptcy/jones_chapter7_petition.pdf'
        },
        {
            'name': 'Real Estate - Property Transfer',
            'form': 'real_estate/deed_transfer.pdf',
            'sources': ['active/property_sale/purchase_agreement.pdf', 'active/property_sale/title_report.pdf'],
            'output': '2024/real_estate/property_deed_transfer.pdf'
        }
    ]
    
    for case in cases:
        print(f"\n🏛️  {case['name']}")
        print("-" * len(case['name']) + "---")
        
        cmd = [
            "python3", "agentic_form_filler.py",
            "--form", case['form'],
            "--sources"] + case['sources'] + [
            "--output", case['output'],
            "--ai-provider", "anthropic",
            "--quality-check",
            "--max-iterations", "3"
        ]
        
        print("Command:")
        print("  " + " \\\n    ".join(cmd))

def example_5_batch_processing():
    """Example 5: Batch processing multiple forms"""
    print("\n📁 Example 5: Batch Processing")
    print("="*50)
    
    print("Bash script for processing multiple forms:")
    print()
    
    script = '''#!/bin/bash
# Batch process multiple forms for the same client

CLIENT="martinez_case"
CASE_DIR="active_cases/${CLIENT}"
OUTPUT_DIR="2024/family_law"

# Set environment for this session
export FORMS_DIR="/Users/lawyer/forms"
export DATA_DIR="/Users/lawyer/client_data"
export OUTPUT_DIR="/Users/lawyer/completed"

# Forms to process
FORMS=(
    "family_law/divorce_petition.pdf"
    "family_law/financial_disclosure.pdf" 
    "family_law/child_support_worksheet.pdf"
    "family_law/parenting_plan.pdf"
)

# Common data sources
SOURCES=(
    "${CASE_DIR}/client_intake.pdf"
    "${CASE_DIR}/financial_documents.pdf"
    "${CASE_DIR}/correspondence.txt"
)

# Process each form
for form in "${FORMS[@]}"; do
    form_name=$(basename "$form" .pdf)
    output_file="${OUTPUT_DIR}/${CLIENT}_${form_name}_filled.pdf"
    
    echo "📝 Processing: $form"
    
    python3 agentic_form_filler.py \\
        --form "$form" \\
        --sources "${SOURCES[@]}" \\
        --output "$output_file" \\
        --ai-provider anthropic \\
        --max-iterations 2 \\
        --verbose
        
    echo "✅ Completed: $output_file"
    echo
done

echo "🎉 Batch processing complete!"'''
    
    print(script)

def main():
    """Run all examples"""
    print("🗂️  Universal Form Processor - Directory Configuration Examples")
    print("=" * 70)
    print()
    
    example_1_default_directories()
    example_2_environment_variables()
    example_3_absolute_paths()
    example_4_legal_practice_workflow()
    example_5_batch_processing()
    
    print("\n" + "=" * 70)
    print("📖 For detailed setup instructions, run: ./setup_directories.sh")
    print("📖 For complete documentation, see: DIRECTORY_SETUP.md")
    print("🧪 To test your configuration, run: python3 test_directories.py")

if __name__ == "__main__":
    main()
