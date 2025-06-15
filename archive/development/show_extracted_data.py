#!/usr/bin/env python3
"""
Quick Data Extraction Demo - Show what Claude found in your FL-142
"""

import os
import sys
import json

# Add the current directory to Python path
sys.path.append('/Users/markpiesner/Documents/Github/agentic_form_filler')

def main():
    print("🔍 FL-142 DATA EXTRACTION DEMO")
    print("=" * 50)
    
    # Set API keys from environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        return
    
    try:
        import llm_client
        
        # Read PDF and analyze with Claude
        pdf_path = "/private/tmp/FL142_Rogers_Assets_Debts.pdf"
        
        prompt = """
        Extract ALL financial and personal data from this FL-142 Schedule of Assets and Debts form.
        
        Return ONLY a JSON object with this exact format:
        {
            "case_number": "value or null",
            "petitioner": "value or null", 
            "respondent": "value or null",
            "household_furniture": "value or null",
            "checking_account": "value or null",
            "checking_account_bank": "value or null", 
            "total_assets": "value or null",
            "student_loans": "value or null",
            "unsecured_loans": "value or null",
            "unsecured_loans_creditor": "value or null",
            "credit_cards": "value or null",
            "credit_cards_companies": "value or null",
            "other_debts": "value or null",
            "other_debts_companies": "value or null",
            "total_debts": "value or null",
            "net_worth": "value or null"
        }
        
        Extract ONLY the actual filled-in values, not $0.00 amounts.
        """
        
        # Add PDF path marker for Claude
        full_prompt = f"[PDF_PATH: {pdf_path}]\n\n{prompt}"
        
        print("🤖 Asking Claude to analyze your FL-142 form...")
        response = llm_client.generate_with_claude("claude-3-5-sonnet-20241022", full_prompt)
        
        print("\n📋 CLAUDE'S RESPONSE:")
        print("-" * 30)
        print(response)
        
        # Try to parse JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_text = response[start:end]
                data = json.loads(json_text)
                
                print("\n💰 EXTRACTED FINANCIAL DATA:")
                print("=" * 40)
                for key, value in data.items():
                    if value and value != "null":
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                        
        except Exception as e:
            print(f"\n⚠️  Could not parse JSON: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you're in the right directory and virtual environment is active")

if __name__ == "__main__":
    main()
