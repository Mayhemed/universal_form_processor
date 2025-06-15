#!/usr/bin/env python3
"""
Create a Simple Fillable FL-142 Form for Testing
"""

import subprocess
import tempfile
import os

def create_fillable_form():
    """Create a basic fillable FL-142 form"""
    
    # Create FDF with form fields
    fdf_content = """%FDF-1.2
1 0 obj
<<
/FDF
<<
/Fields [
<<
/T (case_number)
/V ()
>>
<<
/T (petitioner)
/V ()
>>
<<
/T (respondent)
/V ()
>>
<<
/T (household_furniture)
/V ()
>>
<<
/T (checking_account)
/V ()
>>
<<
/T (checking_account_bank)
/V ()
>>
<<
/T (total_assets)
/V ()
>>
<<
/T (student_loans)
/V ()
>>
<<
/T (unsecured_loans)
/V ()
>>
<<
/T (credit_cards)
/V ()
>>
<<
/T (total_debts)
/V ()
>>
<<
/T (net_worth)
/V ()
>>
]
>>
>>
endobj
trailer

<<
/Root 1 0 R
>>
%%EOF"""

    # Write FDF file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False) as f:
        f.write(fdf_content)
        fdf_path = f.name

    try:
        # Create fillable PDF using your existing FL-142 as template
        subprocess.run([
            'pdftk', 
            '/private/tmp/FL142_Rogers_Assets_Debts.pdf',
            'fill_form', fdf_path,
            'output', 'fl142_fillable_template.pdf'
        ], check=True)
        
        print("✅ Created fillable form: fl142_fillable_template.pdf")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating form: {e}")
        return False
    finally:
        os.unlink(fdf_path)

if __name__ == "__main__":
    print("🛠️  Creating Fillable FL-142 Template...")
    if create_fillable_form():
        print("\n🎯 Now you can test with:")
        print("python3 agentic_form_filler.py \\")
        print("  --form fl142_fillable_template.pdf \\")
        print("  --sources /private/tmp/FL142_Rogers_Assets_Debts.pdf \\")
        print("  --ai-provider anthropic \\")
        print("  --model claude-3-5-sonnet-20241022 \\")
        print("  --output completed_form.pdf")
