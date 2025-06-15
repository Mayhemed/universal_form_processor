# 📁 Directory Configuration Guide

This guide shows you how to organize and configure directories for your Universal Form Processor.

## 🗂️ **Directory Structure Options**

### **Option 1: Default Structure (Recommended)**

```
your_project/
├── forms/           # Place blank PDF forms here
│   ├── divorce_form.pdf
│   ├── bankruptcy_form.pdf
│   └── custody_form.pdf
├── data/            # Place client data files here
│   ├── client_docs.pdf
│   ├── financial_info.txt
│   └── case_details.json
├── output/          # Filled forms will be saved here
│   ├── smith_divorce_filled.pdf
│   └── jones_bankruptcy_filled.pdf
└── agentic_form_filler.py
```

**Usage with default structure:**
```bash
# Simple usage - searches in default directories
python agentic_form_filler.py \
    --form "divorce_form.pdf" \
    --sources "client_docs.pdf" "financial_info.txt" \
    --output "smith_divorce_filled.pdf"
```

### **Option 2: Custom Directory Structure**

```
/Users/lawyer/
├── legal_forms/
│   ├── family_law/
│   │   ├── divorce_forms/
│   │   └── custody_forms/
│   └── bankruptcy/
├── client_data/
│   ├── 2024/
│   │   ├── smith_case/
│   │   └── jones_case/
│   └── 2023/
└── completed_forms/
    ├── 2024/
    └── archive/
```

## 🔧 **Configuration Methods**

### **Method 1: Environment Variables (Recommended)**

Set your preferred directories once:

```bash
# Add to your ~/.bashrc, ~/.zshrc, or .env file
export FORMS_DIR="/Users/lawyer/legal_forms"
export DATA_DIR="/Users/lawyer/client_data" 
export OUTPUT_DIR="/Users/lawyer/completed_forms"

# For AI providers
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Usage with environment variables:**
```bash
# Now you can use relative paths
python agentic_form_filler.py \
    --form "family_law/divorce_forms/standard_divorce.pdf" \
    --sources "2024/smith_case/documents.pdf" \
    --output "2024/smith_divorce_filled.pdf"
```

### **Method 2: Full Absolute Paths**

```bash
python agentic_form_filler.py \
    --form "/Users/lawyer/legal_forms/family_law/divorce_forms/standard_divorce.pdf" \
    --sources "/Users/lawyer/client_data/2024/smith_case/documents.pdf" \
              "/Users/lawyer/client_data/2024/smith_case/financial.txt" \
    --output "/Users/lawyer/completed_forms/2024/smith_divorce_filled.pdf"
```

### **Method 3: Working Directory**

```bash
# Navigate to your project directory
cd /Users/lawyer/law_practice

# Use relative paths from that location
python agentic_form_filler.py \
    --form "legal_forms/divorce_form.pdf" \
    --sources "client_data/smith/docs.pdf" \
    --output "completed_forms/smith_filled.pdf"
```

## 📋 **Setup Scripts**

### **Quick Setup Script**

```bash
#!/bin/bash
# setup_directories.sh

# Create default directory structure
mkdir -p forms data output

# Set environment variables for current session
export FORMS_DIR="$(pwd)/forms"
export DATA_DIR="$(pwd)/data"
export OUTPUT_DIR="$(pwd)/output"

echo "✅ Directory structure created:"
echo "   📁 Forms: $FORMS_DIR"
echo "   📁 Data: $DATA_DIR" 
echo "   📁 Output: $OUTPUT_DIR"

# Make permanent (optional)
echo "# Universal Form Processor Directories" >> ~/.bashrc
echo "export FORMS_DIR=\"$FORMS_DIR\"" >> ~/.bashrc
echo "export DATA_DIR=\"$DATA_DIR\"" >> ~/.bashrc
echo "export OUTPUT_DIR=\"$OUTPUT_DIR\"" >> ~/.bashrc

echo "✅ Environment variables added to ~/.bashrc"
echo "   Run 'source ~/.bashrc' to apply permanently"
```

### **Legal Practice Setup**

```bash
#!/bin/bash
# legal_practice_setup.sh

BASE_DIR="/Users/$(whoami)/LegalPractice"

# Create comprehensive directory structure
mkdir -p "$BASE_DIR"/{forms,clients,output}/{family_law,bankruptcy,personal_injury,real_estate}
mkdir -p "$BASE_DIR"/forms/family_law/{divorce,custody,adoption}
mkdir -p "$BASE_DIR"/clients/{active,completed,archived}
mkdir -p "$BASE_DIR"/output/{2024,2023,archive}

# Set environment variables
cat >> ~/.bashrc << EOF

# Legal Practice Form Processor Configuration
export FORMS_DIR="$BASE_DIR/forms"
export DATA_DIR="$BASE_DIR/clients"
export OUTPUT_DIR="$BASE_DIR/output"
EOF

echo "✅ Legal practice directory structure created at: $BASE_DIR"
```

## 🎯 **Real-World Examples**

### **Divorce Case Processing**

```bash
# Setup
export FORMS_DIR="/Users/lawyer/forms"
export DATA_DIR="/Users/lawyer/clients"
export OUTPUT_DIR="/Users/lawyer/completed"

# Process divorce form
python agentic_form_filler.py \
    --form "family_law/california_divorce_petition.pdf" \
    --sources "smith_case/client_intake.pdf" \
              "smith_case/financial_disclosure.txt" \
              "smith_case/property_list.json" \
    --output "2024/smith_divorce_petition_filled.pdf" \
    --ai-provider anthropic \
    --max-iterations 3
```

### **Bankruptcy Filing**

```bash
# High-accuracy processing for complex bankruptcy forms
python agentic_form_filler.py \
    --form "bankruptcy/chapter7_petition.pdf" \
    --sources "jones_case/debtor_info.pdf" \
              "jones_case/creditor_matrix.xlsx" \
              "jones_case/asset_schedule.txt" \
    --output "2024/jones_chapter7_filled.pdf" \
    --ai-provider openai \
    --model "gpt-4" \
    --quality-check \
    --max-iterations 5
```

### **Batch Processing**

```bash
#!/bin/bash
# batch_process.sh

# Process multiple forms for the same client
CLIENT="martinez_case"
FORMS=("divorce_petition" "financial_disclosure" "child_support_worksheet")

for form in "${FORMS[@]}"; do
    python agentic_form_filler.py \
        --form "family_law/${form}.pdf" \
        --sources "${CLIENT}/intake.pdf" "${CLIENT}/documents.txt" \
        --output "2024/${CLIENT}_${form}_filled.pdf" \
        --ai-provider anthropic
done
```

## ⚙️ **Configuration File (Advanced)**

Create a `config.json` file:

```json
{
    "directories": {
        "forms": "/Users/lawyer/legal_forms",
        "data": "/Users/lawyer/client_data",
        "output": "/Users/lawyer/completed_forms"
    },
    "ai_settings": {
        "default_provider": "anthropic",
        "default_model": "claude-3-sonnet-20240229",
        "max_iterations": 3,
        "quality_check": true
    },
    "file_patterns": {
        "forms": "*.pdf",
        "data": ["*.pdf", "*.txt", "*.json", "*.xlsx"],
        "output_suffix": "_filled"
    }
}
```

## 🚀 **Best Practices**

### **1. Organize by Practice Area**
```
forms/
├── family_law/
├── bankruptcy/
├── personal_injury/
├── real_estate/
└── corporate/
```

### **2. Date-Based Client Data**
```
clients/
├── 2024/
│   ├── january/
│   ├── february/
│   └── ...
└── archive/
```

### **3. Automated Output Organization**
```
output/
├── 2024/
│   ├── completed/
│   ├── pending_review/
│   └── filed/
└── templates/
```

### **4. Security Considerations**
- Keep sensitive client data in encrypted directories
- Use environment variables for API keys (never hardcode)
- Regular backups of completed forms
- Separate production and testing directories

## 🔍 **Troubleshooting**

### **File Not Found Errors**
```bash
# Check current environment variables
echo "Forms: $FORMS_DIR"
echo "Data: $DATA_DIR" 
echo "Output: $OUTPUT_DIR"

# Test file resolution
python -c "
import os
print('Forms dir exists:', os.path.exists('$FORMS_DIR'))
print('Data dir exists:', os.path.exists('$DATA_DIR'))
print('Output dir exists:', os.path.exists('$OUTPUT_DIR'))
"
```

### **Permission Issues**
```bash
# Fix permissions
chmod -R 755 /path/to/your/directories

# Create missing directories
mkdir -p "$FORMS_DIR" "$DATA_DIR" "$OUTPUT_DIR"
```

## 📞 **Quick Start**

1. **Default Setup (Easiest)**:
   ```bash
   mkdir -p forms data output
   python agentic_form_filler.py --form forms/your_form.pdf --sources data/your_data.pdf --output output/filled.pdf
   ```

2. **Environment Variables**:
   ```bash
   export FORMS_DIR="/your/forms/path"
   export DATA_DIR="/your/data/path"
   export OUTPUT_DIR="/your/output/path"
   ```

3. **Full Paths**:
   ```bash
   python agentic_form_filler.py --form "/full/path/to/form.pdf" --sources "/full/path/to/data.pdf"
   ```

Choose the method that works best for your workflow! 🎯
