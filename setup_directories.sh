#!/bin/bash
# setup_directories.sh - Quick directory setup for Universal Form Processor

set -e

echo "🗂️  Setting up Universal Form Processor directories..."

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create default directory structure
echo "📁 Creating directory structure..."
mkdir -p forms data output

# Create subdirectories for better organization
mkdir -p forms/{family_law,bankruptcy,personal_injury,real_estate,other}
mkdir -p data/{active_cases,completed_cases,templates}
mkdir -p output/{2024,2023,archive}

echo "✅ Directory structure created:"
echo "   📂 forms/ - Place your blank PDF forms here"
echo "      ├── family_law/"
echo "      ├── bankruptcy/"
echo "      ├── personal_injury/"
echo "      ├── real_estate/"
echo "      └── other/"
echo "   📂 data/ - Place client data and source documents here"
echo "      ├── active_cases/"
echo "      ├── completed_cases/"
echo "      └── templates/"
echo "   📂 output/ - Filled forms will be saved here"
echo "      ├── 2024/"
echo "      ├── 2023/"
echo "      └── archive/"

# Set environment variables for current session
export FORMS_DIR="$(pwd)/forms"
export DATA_DIR="$(pwd)/data"
export OUTPUT_DIR="$(pwd)/output"

echo ""
echo "🔧 Environment variables set for current session:"
echo "   FORMS_DIR=$FORMS_DIR"
echo "   DATA_DIR=$DATA_DIR"
echo "   OUTPUT_DIR=$OUTPUT_DIR"

# Ask user if they want to make environment variables permanent
echo ""
read -p "🤔 Would you like to make these environment variables permanent? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Detect shell configuration file
    SHELL_CONFIG=""
    if [[ -f "$HOME/.zshrc" && "$SHELL" == *"zsh"* ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    else
        SHELL_CONFIG="$HOME/.bashrc"  # Create if doesn't exist
    fi
    
    echo ""
    echo "📝 Adding environment variables to $SHELL_CONFIG..."
    
    # Add environment variables to shell config
    cat >> "$SHELL_CONFIG" << EOF

# Universal Form Processor Directory Configuration
export FORMS_DIR="$FORMS_DIR"
export DATA_DIR="$DATA_DIR"
export OUTPUT_DIR="$OUTPUT_DIR"
EOF
    
    echo "✅ Environment variables added to $SHELL_CONFIG"
    echo "   Run 'source $SHELL_CONFIG' or restart your terminal to apply"
fi

# Create sample configuration files
echo ""
echo "📄 Creating sample files..."

# Sample form (placeholder)
cat > forms/sample_form_info.txt << 'EOF'
# Sample Forms Directory

Place your PDF forms in this directory or its subdirectories:

forms/
├── family_law/
│   ├── divorce_petition.pdf
│   ├── custody_agreement.pdf
│   └── child_support_worksheet.pdf
├── bankruptcy/
│   ├── chapter7_petition.pdf
│   └── creditor_matrix.pdf
└── other/
    └── general_intake_form.pdf

The system will automatically find forms when you use relative paths:
  python agentic_form_filler.py --form "family_law/divorce_petition.pdf" ...
EOF

# Sample data info
cat > data/sample_data_info.txt << 'EOF'
# Sample Data Directory

Place your client data and source documents here:

data/
├── active_cases/
│   ├── smith_case/
│   │   ├── intake_form.pdf
│   │   ├── financial_documents.pdf
│   │   └── correspondence.txt
│   └── jones_case/
│       ├── client_interview.txt
│       └── supporting_docs.pdf
├── completed_cases/
│   └── archived_cases.zip
└── templates/
    ├── client_intake_template.txt
    └── standard_responses.json

Usage examples:
  python agentic_form_filler.py --sources "active_cases/smith_case/intake_form.pdf" ...
  python agentic_form_filler.py --sources "templates/client_intake_template.txt" ...
EOF

# Sample output info
cat > output/README.txt << 'EOF'
# Output Directory

Completed forms will be saved here automatically.

The system organizes output by:
- Year (2024/, 2023/, etc.)
- Case type or custom organization you specify

Example outputs:
  output/2024/smith_divorce_petition_filled.pdf
  output/2024/jones_bankruptcy_chapter7_filled.pdf
  output/archive/old_completed_forms.pdf

You can specify custom output paths:
  python agentic_form_filler.py --output "2024/important_case_filled.pdf" ...
EOF

echo "✅ Sample configuration files created"

# Create a simple test script
cat > test_directories.py << 'EOF'
#!/usr/bin/env python3
"""Test script to verify directory configuration"""

import os
import sys

def test_directories():
    """Test directory configuration and access"""
    print("🧪 Testing directory configuration...\n")
    
    # Test environment variables
    forms_dir = os.getenv('FORMS_DIR', './forms')
    data_dir = os.getenv('DATA_DIR', './data')
    output_dir = os.getenv('OUTPUT_DIR', './output')
    
    print(f"📁 Configured directories:")
    print(f"   Forms:  {forms_dir}")
    print(f"   Data:   {data_dir}")
    print(f"   Output: {output_dir}")
    print()
    
    # Test directory existence
    all_good = True
    for name, path in [("Forms", forms_dir), ("Data", data_dir), ("Output", output_dir)]:
        if os.path.exists(path):
            print(f"✅ {name} directory exists: {path}")
            # Test write permissions
            try:
                test_file = os.path.join(path, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"   ✅ Write permissions OK")
            except:
                print(f"   ⚠️  Write permissions issue")
                all_good = False
        else:
            print(f"❌ {name} directory missing: {path}")
            all_good = False
        print()
    
    # Test form processor import
    try:
        sys.path.append('.')
        import agentic_form_filler
        print("✅ Form processor import successful")
    except ImportError as e:
        print(f"⚠️  Form processor import issue: {e}")
        all_good = False
    
    print(f"\n{'✅ All tests passed!' if all_good else '⚠️  Some issues found - check above'}")
    return all_good

if __name__ == "__main__":
    test_directories()
EOF

chmod +x test_directories.py

echo "✅ Test script created: test_directories.py"

# Display usage examples
echo ""
echo "🎯 Quick Usage Examples:"
echo ""
echo "1️⃣  Test your setup:"
echo "   python3 test_directories.py"
echo ""
echo "2️⃣  Basic form filling (using default directories):"
echo "   python3 agentic_form_filler.py \\"
echo "     --form \"forms/your_form.pdf\" \\"
echo "     --sources \"data/your_data.pdf\" \\"
echo "     --output \"output/filled_form.pdf\""
echo ""
echo "3️⃣  With AI processing:"
echo "   export ANTHROPIC_API_KEY=\"sk-ant-your-key\""
echo "   python3 agentic_form_filler.py \\"
echo "     --form \"family_law/divorce_petition.pdf\" \\"
echo "     --sources \"active_cases/smith/intake.pdf\" \\"
echo "     --output \"2024/smith_divorce_filled.pdf\" \\"
echo "     --ai-provider anthropic"
echo ""
echo "4️⃣  Pattern matching (no API key needed):"
echo "   python3 agentic_form_filler.py \\"
echo "     --form \"forms/simple_form.pdf\" \\"
echo "     --sources \"data/text_data.txt\" \\"
echo "     --output \"output/filled.pdf\""
echo ""
echo "📖 For more detailed examples, see: DIRECTORY_SETUP.md"
echo ""
echo "🎉 Setup complete! Your Universal Form Processor is ready to use."
