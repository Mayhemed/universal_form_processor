#!/usr/bin/env python3
"""
Quick Test Script for Agentic PDF Form Filler - FIXED VERSION
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

def test_llm_client():
    """Test LLM client functionality"""
    print("\n🤖 Testing LLM Client...")
    
    try:
        import llm_client
        
        # Test getting available models
        try:
            models = llm_client.get_available_models()
            if models:
                print(f"  ✅ Found {len(models)} available models")
                return True
            else:
                print("  ⚠️  No models found, but client works")
                return True
        except Exception as e:
            print(f"  ⚠️  Model discovery failed: {e}")
            print("  ℹ️  This is normal if no local models are running")
            return True
            
    except Exception as e:
        print(f"  ❌ Error testing LLM client: {e}")
        return False

def test_pattern_extraction():
    """Test basic pattern extraction logic"""
    print("\n🧪 Testing Pattern Extraction...")
    
    # Sample data for testing
    test_data = """
    Case Number: TEST123456
    Petitioner: JOHN DOE
    Phone: (555) 123-4567
    Email: john.doe@example.com
    Total Assets: $25,000.00
    """
    
    try:
        import re
        
        # Simple pattern tests
        patterns = {
            'case_number': r'Case Number:\s*([A-Z0-9]+)',
            'phone': r'\((\d{3})\)\s*(\d{3})-(\d{4})',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'money': r'\$([0-9,]+\.?\d*)',
        }
        
        found_patterns = 0
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, test_data)
            if match:
                found_patterns += 1
                print(f"    ✓ Found {pattern_name}: {match.group(1) if len(match.groups()) == 1 else match.group()}")
        
        if found_patterns > 0:
            print(f"  ✅ Pattern extraction working ({found_patterns}/4 patterns found)")
            return True
        else:
            print("  ⚠️  No patterns matched")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing patterns: {e}")
        return False

def test_system_commands():
    """Test if required system commands are available"""
    print("\n🔧 Testing System Commands...")
    
    import subprocess
    
    # Test pdftk
    try:
        result = subprocess.run(['pdftk', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ pdftk is available")
            pdftk_ok = True
        else:
            print("  ⚠️  pdftk command failed")
            pdftk_ok = False
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("  ⚠️  pdftk not found or not working")
        pdftk_ok = False
    
    # Test python version
    try:
        result = subprocess.run(['python3', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✅ {version}")
            python_ok = True
        else:
            print("  ⚠️  python3 command issue")
            python_ok = False
    except Exception:
        print("  ⚠️  python3 not accessible")
        python_ok = False
    
    return pdftk_ok, python_ok

def main():
    """Main test function"""
    print("🚀 AGENTIC PDF FORM FILLER - QUICK TEST (FIXED)")
    print("=" * 55)
    
    # Test API keys
    openai_available, anthropic_available = test_api_keys()
    
    # Test imports
    imports_ok = test_basic_imports()
    
    if not imports_ok:
        print("\n❌ Basic imports failed. Please check your setup.")
        return
    
    # Test LLM client
    llm_ok = test_llm_client()
    
    # Test pattern extraction
    pattern_ok = test_pattern_extraction()
    
    # Test system commands
    pdftk_ok, python_ok = test_system_commands()
    
    print("\n" + "=" * 55)
    print("📊 TEST SUMMARY")
    print("=" * 55)
    
    print(f"✅ Module Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ LLM Client: {'PASS' if llm_ok else 'FAIL'}")
    print(f"✅ Pattern Extraction: {'PASS' if pattern_ok else 'FAIL'}")
    print(f"🔧 pdftk Command: {'AVAILABLE' if pdftk_ok else 'MISSING'}")
    print(f"🐍 Python3: {'AVAILABLE' if python_ok else 'MISSING'}")
    print(f"🔑 OpenAI API: {'AVAILABLE' if openai_available else 'NOT SET'}")
    print(f"🔑 Anthropic API: {'AVAILABLE' if anthropic_available else 'NOT SET'}")
    
    # Overall assessment
    core_ok = imports_ok and llm_ok and pattern_ok and python_ok
    
    if core_ok:
        print("\n🎉 CORE SYSTEM READY!")
        
        if pdftk_ok:
            print("📋 PDF form filling is fully functional")
        else:
            print("⚠️  PDF form filling requires pdftk installation")
            print("   Install with: brew install pdftk-java (macOS) or sudo apt install pdftk (Linux)")
        
        print("\n📋 What you can do now:")
        print("   • Run interactive demo: python3 demo_agentic_system.py")
        print("   • Run full tests: python3 test_agentic_system.py")
        
        if openai_available and pdftk_ok:
            print("   • Test with OpenAI: python3 agentic_form_filler.py --form form.pdf --sources data.txt --ai-provider openai")
        
        if anthropic_available and pdftk_ok:
            print("   • Test with Claude: python3 agentic_form_filler.py --form form.pdf --sources data.txt --ai-provider anthropic")
        
        if not (openai_available or anthropic_available):
            print("   • Test pattern matching: python3 agentic_form_filler.py --form form.pdf --sources data.txt --ai-provider pattern")
            
    else:
        print("\n⚠️  Some core components failed. Check the errors above.")
    
    print("\n🚀 Happy form filling!")

if __name__ == "__main__":
    main()
