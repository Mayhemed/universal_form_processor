#!/usr/bin/env python3
"""
Quick Test Script for Agentic PDF Form Filler
Tests basic functionality and API connectivity
"""

import os
import tempfile
import json

def test_api_keys():
    """Test if API keys are properly set"""
    print("🔑 Testing API Keys...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key and openai_key.startswith("sk-"):
        print("  ✅ OpenAI API key found")
        openai_available = True
    else:
        print("  ⚠️  OpenAI API key not found or invalid")
        openai_available = False
    
    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        print("  ✅ Anthropic API key found")
        anthropic_available = True
    else:
        print("  ⚠️  Anthropic API key not found or invalid")
        anthropic_available = False
    
    return openai_available, anthropic_available

def test_basic_imports():
    """Test if all modules can be imported"""
    print("\n📦 Testing Module Imports...")
    
    try:
        import agentic_form_filler
        print("  ✅ agentic_form_filler module imported")
    except Exception as e:
        print(f"  ❌ Error importing agentic_form_filler: {e}")
        return False
    
    try:
        import llm_client
        print("  ✅ llm_client module imported")
    except Exception as e:
        print(f"  ❌ Error importing llm_client: {e}")
        return False
    
    try:
        import python_agentic_framework
        print("  ✅ python_agentic_framework module imported")
    except Exception as e:
        print(f"  ❌ Error importing python_agentic_framework: {e}")
        return False
    
    return True

def create_test_data():
    """Create sample test data"""
    print("\n📄 Creating Test Data...")
    
    # Create sample case data
    sample_data = """
    SAMPLE LEGAL CASE DATA
    =====================
    Case Number: TEST123456
    Petitioner: JOHN DOE
    Respondent: JANE SMITH
    
    Financial Information:
    - Bank Account: $5,000.00
    - Monthly Income: $3,500.00
    - Monthly Expenses: $2,800.00
    - Total Assets: $25,000.00
    - Total Debts: $15,000.00
    
    Contact Information:
    - Phone: (555) 123-4567
    - Email: john.doe@example.com
    - Address: 123 Main St, Anytown, CA 90210
    """
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_data)
        test_file = f.name
    
    print(f"  ✅ Test data created: {test_file}")
    return test_file

def test_pattern_extraction():
    """Test pattern-based extraction without API"""
    print("\n🧪 Testing Pattern Extraction...")
    
    test_file = create_test_data()
    
    try:
        import subprocess
        result = subprocess.run([
            'python3', 'agentic_form_filler.py',
            '--form', '/dev/null',  # Use /dev/null since we're just testing extraction logic
            '--sources', test_file,
            '--ai-provider', 'pattern',
            '--verbose'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Pattern extraction completed successfully")
        else:
            print(f"  ⚠️  Pattern extraction returned code {result.returncode}")
            print(f"     Error: {result.stderr[:200]}...")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"  ❌ Error testing pattern extraction: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(test_file)
        except:
            pass

def main():
    """Main test function"""
    print("🚀 AGENTIC PDF FORM FILLER - QUICK TEST")
    print("=" * 50)
    
    # Test API keys
    openai_available, anthropic_available = test_api_keys()
    
    # Test imports
    imports_ok = test_basic_imports()
    
    if not imports_ok:
        print("\n❌ Basic imports failed. Please check your setup.")
        return
    
    # Test pattern extraction
    pattern_ok = test_pattern_extraction()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    print(f"✅ Module Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ Pattern Extraction: {'PASS' if pattern_ok else 'FAIL'}")
    print(f"🔑 OpenAI API: {'AVAILABLE' if openai_available else 'NOT SET'}")
    print(f"🔑 Anthropic API: {'AVAILABLE' if anthropic_available else 'NOT SET'}")
    
    if imports_ok and pattern_ok:
        print("\n🎉 SYSTEM READY!")
        print("\n📋 What you can do now:")
        
        if openai_available:
            print("   • Test OpenAI: python3 agentic_form_filler.py --form form.pdf --sources data.txt --ai-provider openai --output filled.pdf")
        
        if anthropic_available:
            print("   • Test Anthropic: python3 agentic_form_filler.py --form form.pdf --sources data.txt --ai-provider anthropic --output filled.pdf")
        
        print("   • Run Demo: python3 demo_agentic_system.py")
        print("   • Full Tests: python3 test_agentic_system.py")
        
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("\n🚀 Happy form filling!")

if __name__ == "__main__":
    main()
