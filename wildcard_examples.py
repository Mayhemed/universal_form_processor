pdf --sources "data/*" --verbose',
            "solution": "Use --verbose flag to see file expansion and resolution details"
        },
        {
            "issue": "Files found but processing fails",
            "command": 'python3 agentic_form_filler.py --form form.pdf --sources "*.pdf"',
            "solution": "Check file permissions, ensure files aren't corrupted, try with single file first"
        },
        {
            "issue": "Want only specific file types from directory",
            "command": 'python3 agentic_form_filler.py --form form.pdf --sources data/ --include-extensions pdf txt',
            "solution": "Use --include-extensions to filter file types when processing directories"
        }
    ]
    
    for i, item in enumerate(issues, 1):
        print(f"{i}. {item['issue']}")
        print(f"   Command: {item['command']}")
        print(f"   Solution: {item['solution']}")
        print()

def debug_file_patterns():
    """Debug function to test file pattern expansion"""
    print("\n🧪 Debug: Test File Pattern Expansion")
    print("="*60)
    
    print("Python test script to debug file patterns:")
    print()
    
    test_script = '''#!/usr/bin/env python3
import glob
import os

def test_patterns():
    """Test various file patterns"""
    patterns = [
        "examples/client_data/*/*.pdf",
        "examples/client_data/smith_case/*",
        "examples/client_data/*/financial*",
        "examples/forms/*.pdf"
    ]
    
    for pattern in patterns:
        print(f"Pattern: {pattern}")
        matches = glob.glob(pattern)
        if matches:
            for match in sorted(matches):
                print(f"  ✅ {match}")
        else:
            print(f"  ❌ No matches found")
        print()

def test_directories():
    """Test directory listings"""
    directories = [
        "examples/client_data/smith_case",
        "examples/client_data",
        "examples/forms"
    ]
    
    for directory in directories:
        print(f"Directory: {directory}")
        if os.path.isdir(directory):
            files = os.listdir(directory)
            for file in sorted(files):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    print(f"  📄 {file}")
                elif os.path.isdir(file_path):
                    print(f"  📁 {file}/")
        else:
            print(f"  ❌ Directory not found")
        print()

if __name__ == "__main__":
    test_patterns()
    test_directories()'''
    
    print(test_script)

def main():
    """Run all examples"""
    print("🔍 Universal Form Processor - Wildcard and Directory Selection Examples")
    print("=" * 80)
    print()
    
    # Create sample structure first
    create_sample_structure()
    
    # Run all examples
    example_1_single_directory()
    example_2_wildcard_patterns()
    example_3_multiple_directories()
    example_4_recursive_search()
    example_5_file_type_filtering()
    example_6_real_world_scenarios()
    example_7_batch_processing()
    example_8_troubleshooting()
    debug_file_patterns()
    
    print("\n" + "=" * 80)
    print("📖 Summary of File Selection Options:")
    print()
    print("🗂️  DIRECTORIES:")
    print("   --sources client_data/                    # All files in directory")
    print("   --sources client_data/ --recursive        # All files recursively")
    print()
    print("🔍 WILDCARDS:")
    print("   --sources \"data/*.pdf\"                   # All PDFs in data/")
    print("   --sources \"*/case_*.txt\"                 # case_*.txt in any subdir") 
    print("   --sources \"client_data/*/*.pdf\"          # PDFs in any case subdir")
    print()
    print("📄 FILE TYPE FILTERING:")
    print("   --sources data/ --include-extensions pdf txt    # Only PDF and TXT")
    print()
    print("🔗 COMBINATIONS:")
    print("   --sources \"case1/*.pdf\" \"case2/*.txt\" docs/  # Multiple patterns")
    print()
    print("🧪 DEBUGGING:")
    print("   --verbose                                 # Show file expansion")
    print("   python3 debug_patterns.py                # Test patterns")
    print()
    print("🎯 Ready to process any combination of files and directories!")

if __name__ == "__main__":
    main()
