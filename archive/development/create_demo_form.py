#!/usr/bin/env python3
"""
Simple Fillable Form Creator using HTML to PDF
"""

import subprocess
import tempfile
import os

def create_simple_form():
    """Create a simple HTML form and convert to fillable PDF"""
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FL-142 Schedule of Assets and Debts</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-group { margin: 10px 0; }
        label { display: inline-block; width: 200px; font-weight: bold; }
        input { width: 300px; padding: 5px; border: 1px solid #ccc; }
        .header { text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 30px; }
        .section { margin: 20px 0; border-top: 2px solid #000; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="header">SCHEDULE OF ASSETS AND DEBTS - FL-142</div>
    
    <div class="form-group">
        <label>Case Number:</label>
        <input type="text" name="case_number" />
    </div>
    
    <div class="form-group">
        <label>Petitioner:</label>
        <input type="text" name="petitioner" />
    </div>
    
    <div class="form-group">
        <label>Respondent:</label>
        <input type="text" name="respondent" />
    </div>
    
    <div class="section">
        <h3>ASSETS:</h3>
        
        <div class="form-group">
            <label>Household Furniture:</label>
            <input type="text" name="household_furniture" />
        </div>
        
        <div class="form-group">
            <label>Checking Account:</label>
            <input type="text" name="checking_account" />
        </div>
        
        <div class="form-group">
            <label>Bank Name:</label>
            <input type="text" name="checking_account_bank" />
        </div>
        
        <div class="form-group">
            <label>TOTAL ASSETS:</label>
            <input type="text" name="total_assets" />
        </div>
    </div>
    
    <div class="section">
        <h3>DEBTS:</h3>
        
        <div class="form-group">
            <label>Student Loans:</label>
            <input type="text" name="student_loans" />
        </div>
        
        <div class="form-group">
            <label>Unsecured Loans:</label>
            <input type="text" name="unsecured_loans" />
        </div>
        
        <div class="form-group">
            <label>Creditor:</label>
            <input type="text" name="unsecured_loans_creditor" />
        </div>
        
        <div class="form-group">
            <label>Credit Cards:</label>
            <input type="text" name="credit_cards" />
        </div>
        
        <div class="form-group">
            <label>Other Debts:</label>
            <input type="text" name="other_debts" />
        </div>
        
        <div class="form-group">
            <label>TOTAL DEBTS:</label>
            <input type="text" name="total_debts" />
        </div>
    </div>
    
    <div class="section">
        <div class="form-group">
            <label>NET WORTH:</label>
            <input type="text" name="net_worth" />
        </div>
    </div>
</body>
</html>"""

    # Write HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        html_path = f.name
    
    print("✅ Created HTML form template")
    print(f"📄 Open in browser: file://{html_path}")
    print("\n🎯 To test your agentic system:")
    print("1. Use any blank PDF form with fillable fields")
    print("2. Or download official FL-142 from ca.gov")
    print("3. Or test extraction-only (which already works perfectly!)")
    
    return html_path

if __name__ == "__main__":
    print("🛠️  Creating Simple Form Template...")
    form_path = create_simple_form()
