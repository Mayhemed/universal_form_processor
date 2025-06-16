#!/usr/bin/env python3
"""
AI Model Selection Tool
Discover, compare, and select AI models for the Universal Form Processor
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional

# Try to import optional dependencies
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    
    def tabulate(data, headers=None, tablefmt="grid"):
        """Fallback tabulate implementation"""
        if not data:
            return "No data"
        
        # Simple text table fallback
        result = []
        if headers:
            result.append(" | ".join(str(h)[:15] for h in headers))
            result.append("-" * 80)
        
        for row in data:
            result.append(" | ".join(str(cell)[:15] for cell in row))
        
        return "\n".join(result)

# Add current directory to path for imports
sys.path.append('.')

try:
    from llm_client import (
        get_all_available_models, 
        get_available_openai_models,
        get_available_anthropic_models, 
        get_available_ollama_models,
        recommend_model_for_task,
        get_default_openai_models,
        get_default_anthropic_models
    )
except ImportError as e:
    print(f"❌ Error importing llm_client: {e}")
    print("Make sure llm_client.py is in the current directory")
    sys.exit(1)

def list_all_models(openai_key: Optional[str] = None, anthropic_key: Optional[str] = None, 
                   show_details: bool = False, provider_filter: Optional[str] = None):
    """List all available models"""
    print("🔍 Discovering available AI models...")
    print()
    
    all_models = get_all_available_models(openai_key, anthropic_key)
    
    if provider_filter:
        all_models = {k: v for k, v in all_models.items() 
                     if v.get("provider", "").lower() == provider_filter.lower()}
    
    if not all_models:
        print("❌ No models found")
        if not openai_key and not anthropic_key:
            print("💡 Tip: Set API keys to see available models:")
            print("   export OPENAI_API_KEY='your-key-here'")
            print("   export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Group by provider
    providers = {}
    for model_id, info in all_models.items():
        provider = info.get("provider", "unknown")
        if provider not in providers:
            providers[provider] = {}
        providers[provider][model_id] = info
    
    for provider, models in providers.items():
        print(f"🤖 {provider.upper()} Models ({len(models)} available)")
        print("=" * 60)
        
        # Simple listing format
        for model_id, info in models.items():
            context = info.get("context_window", 0)
            cost = info.get("cost_tier", "unknown")
            caps = info.get("capabilities", [])
            
            print(f"  • {model_id}")
            print(f"    Context: {context:,} tokens")
            print(f"    Cost: {cost.title()}")
            print(f"    Capabilities: {', '.join(caps[:3])}")
            
            if show_details:
                desc = info.get("description", "")
                if desc:
                    print(f"    Description: {desc}")
                recommended = info.get("recommended_for", [])
                if recommended:
                    print(f"    Best for: {', '.join(recommended[:3])}")
            print()
        print()

def recommend_models(task_type: str, budget_priority: bool = False, 
                    openai_key: Optional[str] = None, anthropic_key: Optional[str] = None):
    """Recommend models for specific tasks"""
    print(f"🎯 Recommending models for: {task_type}")
    if budget_priority:
        print("💰 Prioritizing cost-effective options")
    print()
    
    all_models = get_all_available_models(openai_key, anthropic_key)
    
    if not all_models:
        print("❌ No models available for recommendations")
        return
    
    recommendations = recommend_model_for_task(task_type, all_models, budget_priority)
    
    if not recommendations:
        print(f"❌ No suitable models found for {task_type}")
        return
    
    print(f"📋 Top {len(recommendations)} recommended models:")
    print()
    
    # Show recommendations
    for i, model_id in enumerate(recommendations[:3], 1):
        if model_id in all_models:
            model_info = all_models[model_id]
            provider = model_info.get("provider", "unknown")
            cost = model_info.get("cost_tier", "unknown")
            context = model_info.get("context_window", 0)
            description = model_info.get("description", "")
            
            print(f"{i}. 🤖 {model_id}")
            print(f"   Provider: {provider.title()}")
            print(f"   Cost: {cost.title()}")
            print(f"   Context: {context:,} tokens")
            print(f"   Description: {description}")
            print(f"   Usage:")
            print(f"     python3 agentic_form_filler.py --form form.pdf --sources data.pdf \\")
            print(f"       --ai-provider {provider} --model {model_id}")
            print()

def test_model_access(openai_key: Optional[str] = None, anthropic_key: Optional[str] = None):
    """Test access to different AI providers"""
    print("🧪 Testing AI provider access...")
    print()
    
    # Test OpenAI
    print("🔵 OpenAI:")
    try:
        openai_models = get_available_openai_models(openai_key)
        if openai_models:
            print(f"✅ Connected - {len(openai_models)} models available")
            sample_model = list(openai_models.keys())[0]
            print(f"   Sample model: {sample_model}")
        else:
            print("⚠️ Connected but no models found")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        if not openai_key:
            print("   💡 Set OPENAI_API_KEY environment variable")
    print()
    
    # Test Anthropic
    print("🟣 Anthropic:")
    try:
        anthropic_models = get_available_anthropic_models(anthropic_key)
        if anthropic_models:
            print(f"✅ Connected - {len(anthropic_models)} models available")
            sample_model = list(anthropic_models.keys())[0]
            print(f"   Sample model: {sample_model}")
        else:
            print("⚠️ Connected but no models found")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        if not anthropic_key:
            print("   💡 Set ANTHROPIC_API_KEY environment variable")
    print()
    
    # Test Ollama
    print("🟠 Ollama (Local):")
    try:
        ollama_models = get_available_ollama_models()
        if ollama_models:
            print(f"✅ Connected - {len(ollama_models)} models available")
            sample_model = list(ollama_models.keys())[0]
            print(f"   Sample model: {sample_model}")
        else:
            print("⚠️ Ollama running but no models installed")
            print("   💡 Install models with: ollama pull llama3.2")
    except Exception as e:
        print(f"❌ Ollama not available: {e}")
        print("   💡 Install Ollama from https://ollama.ai/")
    print()

def interactive_model_selection():
    """Interactive model selection wizard"""
    print("🧙‍♂️ Interactive AI Model Selection Wizard")
    print("=" * 50)
    
    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key:
        openai_key = input("🔵 OpenAI API Key (press Enter to skip): ").strip()
        if not openai_key:
            openai_key = None
    
    if not anthropic_key:
        anthropic_key = input("🟣 Anthropic API Key (press Enter to skip): ").strip()
        if not anthropic_key:
            anthropic_key = None
    
    print()
    
    # Get available models
    all_models = get_all_available_models(openai_key, anthropic_key)
    
    if not all_models:
        print("❌ No models available. Using default models for demonstration.")
        all_models = {**get_default_openai_models(), **get_default_anthropic_models()}
    
    print(f"✅ Found {len(all_models)} available models")
    print()
    
    # Ask about use case
    print("What type of task will you be doing?")
    tasks = {
        "1": ("legal_forms", "Legal document processing (high accuracy needed)"),
        "2": ("data_extraction", "General data extraction from documents"),
        "3": ("simple_forms", "Simple form filling (cost-effective)"),
        "4": ("complex_analysis", "Complex document analysis")
    }
    
    for key, (task_id, description) in tasks.items():
        print(f"  {key}. {description}")
    
    task_choice = input("\nSelect task type (1-4): ").strip()
    task_type = tasks.get(task_choice, ("data_extraction", "General data extraction"))[0]
    
    # Ask about budget priority
    budget_choice = input("\nPrioritize cost-effectiveness over performance? (y/n): ").strip().lower()
    budget_priority = budget_choice in ['y', 'yes']
    
    print()
    print("🎯 Finding best models for your needs...")
    print()
    
    # Get recommendations
    recommendations = recommend_model_for_task(task_type, all_models, budget_priority)
    
    if not recommendations:
        print("❌ No suitable models found")
        return
    
    print(f"📋 Top recommendations for {task_type}:")
    print()
    
    # Show top 3 recommendations with details
    for i, model_id in enumerate(recommendations[:3], 1):
        model_info = all_models[model_id]
        provider = model_info.get("provider", "unknown")
        cost = model_info.get("cost_tier", "unknown")
        context = model_info.get("context_window", 0)
        description = model_info.get("description", "")
        
        print(f"{i}. 🤖 {model_id}")
        print(f"   Provider: {provider.title()}")
        print(f"   Cost: {cost.title()}")
        print(f"   Context: {context:,} tokens")
        print(f"   Description: {description}")
        
        # Show usage command
        print(f"   Command:")
        print(f"   python3 agentic_form_filler.py \\")
        print(f"     --form your_form.pdf \\")
        print(f"     --sources your_data.pdf \\")
        print(f"     --ai-provider {provider} \\")
        print(f"     --model {model_id} \\")
        print(f"     --output filled_form.pdf")
        print()

def show_provider_setup():
    """Show setup instructions for different providers"""
    print("🛠️ AI Provider Setup Instructions")
    print("=" * 50)
    
    print("🔵 OpenAI Setup:")
    print("1. Get API key from: https://platform.openai.com/api-keys")
    print("2. Set environment variable:")
    print("   export OPENAI_API_KEY='sk-your-key-here'")
    print("3. Or use --openai-key flag")
    print()
    
    print("🟣 Anthropic Setup:")
    print("1. Get API key from: https://console.anthropic.com/")
    print("2. Set environment variable:")
    print("   export ANTHROPIC_API_KEY='sk-ant-your-key-here'")
    print("3. Or use --anthropic-key flag")
    print()
    
    print("🟠 Ollama Setup (Local):")
    print("1. Install Ollama: https://ollama.ai/")
    print("2. Start Ollama: ollama serve")
    print("3. Install models: ollama pull llama3.2")
    print("4. No API key needed!")
    print()
    
    print("💡 Quick Test:")
    print("python3 model_selector.py --test-access")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="AI Model Selection Tool for Universal Form Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available models
  python3 model_selector.py --list-all
  
  # List only OpenAI models with details
  python3 model_selector.py --list-all --provider openai --details
  
  # Get recommendations for legal forms
  python3 model_selector.py --recommend legal_forms
  
  # Interactive selection wizard
  python3 model_selector.py --interactive
  
  # Test API access
  python3 model_selector.py --test-access
        """
    )
    
    # API key arguments
    parser.add_argument('--openai-key', help='OpenAI API key')
    parser.add_argument('--anthropic-key', help='Anthropic API key')
    
    # Main actions
    parser.add_argument('--list-all', action='store_true', 
                       help='List all available models')
    parser.add_argument('--provider', choices=['openai', 'anthropic', 'ollama'],
                       help='Filter by provider')
    parser.add_argument('--details', action='store_true',
                       help='Show detailed model information')
    
    parser.add_argument('--recommend', choices=['legal_forms', 'data_extraction', 'simple_forms', 'complex_analysis'],
                       help='Recommend models for specific task type')
    parser.add_argument('--budget-priority', action='store_true',
                       help='Prioritize cost-effective models')
    
    parser.add_argument('--test-access', action='store_true',
                       help='Test access to AI providers')
    
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive model selection wizard')
    
    parser.add_argument('--setup', action='store_true',
                       help='Show provider setup instructions')
    
    args = parser.parse_args()
    
    # Use provided API keys or fall back to environment
    openai_key = args.openai_key or os.getenv("OPENAI_API_KEY")
    anthropic_key = args.anthropic_key or os.getenv("ANTHROPIC_API_KEY")
    
    # Execute commands
    if args.setup:
        show_provider_setup()
    elif args.test_access:
        test_model_access(openai_key, anthropic_key)
    elif args.interactive:
        interactive_model_selection()
    elif args.list_all:
        list_all_models(openai_key, anthropic_key, args.details, args.provider)
    elif args.recommend:
        recommend_models(args.recommend, args.budget_priority, openai_key, anthropic_key)
    else:
        # Default action - show help and quick info
        print("🤖 AI Model Selector for Universal Form Processor")
        print("=" * 60)
        print()
        print("Quick Start:")
        print("  --list-all          List all available models")
        print("  --interactive       Interactive selection wizard")
        print("  --test-access       Test API connections")
        print("  --setup             Show setup instructions")
        print()
        print("Examples:")
        print("  python3 model_selector.py --list-all")
        print("  python3 model_selector.py --recommend legal_forms")
        print("  python3 model_selector.py --interactive")
        print()
        print("For full help: python3 model_selector.py --help")

if __name__ == "__main__":
    main()
