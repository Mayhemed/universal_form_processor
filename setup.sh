#!/bin/bash
# Quick Setup Script for Agentic PDF Form Filler

echo "🚀 Setting up Agentic PDF Form Filler..."
echo "========================================"

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
}

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt || {
    echo "⚠️  Some dependencies failed to install. You can install them manually:"
    echo "   pip3 install openai anthropic python-dotenv PyPDF2 pdfplumber requests beautifulsoup4"
}

# Check for pdftk
echo "🔧 Checking for pdftk..."
if command -v pdftk &> /dev/null; then
    echo "✅ pdftk found"
else
    echo "⚠️  pdftk not found. Install with:"
    echo "   macOS: brew install pdftk-java"
    echo "   Ubuntu: sudo apt install pdftk"
    echo "   Windows: Download from pdftk.org"
fi

# Make scripts executable
echo "🔒 Making scripts executable..."
chmod +x agentic_form_filler.py
chmod +x test_agentic_system.py
chmod +x demo_agentic_system.py
chmod +x python_agentic_framework.py

# Run tests
echo "🧪 Running tests..."
python3 test_agentic_system.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Set your API keys:"
echo "      export OPENAI_API_KEY='sk-your-key'"
echo "      export ANTHROPIC_API_KEY='sk-ant-your-key'"
echo ""
echo "   2. Try the demo:"
echo "      python3 demo_agentic_system.py"
echo ""
echo "   3. Fill your first form:"
echo "      python3 agentic_form_filler.py --form form.pdf --sources data.txt --output filled.pdf"
echo ""
echo "🚀 Happy form filling!"
