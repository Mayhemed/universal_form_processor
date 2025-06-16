💎 Premium:** gpt-4o, claude-3-5-sonnet, claude-3-opus, o1-preview

### **Cost-Effective Strategies**

```bash
# 1. Use budget models for simple tasks
python3 agentic_form_filler.py --form simple_form.pdf --sources data.txt \
  --ai-provider openai --model gpt-4o-mini

# 2. Auto-select with budget priority
python3 agentic_form_filler.py --form form.pdf --sources data.pdf \
  --ai-provider anthropic --auto-select-model --budget-priority

# 3. Get budget recommendations
python3 model_selector.py --recommend data_extraction --budget-priority

# 4. Use local models for privacy/cost
python3 agentic_form_filler.py --form form.pdf --sources data.pdf \
  --ai-provider ollama --model llama3.2
```

## 🛠️ **Model Selection Tools**

### **1. Interactive Selection Wizard**
```bash
python3 model_selector.py --interactive
```
**Guides you through:**
- Task type selection
- Budget preferences  
- Available model discovery
- Configuration saving

### **2. Command-Line Discovery**
```bash
# List all models
python3 model_selector.py --list-all

# Get task-specific recommendations
python3 model_selector.py --recommend legal_forms

# Compare specific models
python3 model_selector.py --compare gpt-4o claude-3-opus-20240229

# Test API connections
python3 model_selector.py --test-access
```

### **3. Integration with Form Filler**
```bash
# Built-in model discovery
python3 agentic_form_filler.py --list-models

# Get recommendations for specific task
python3 agentic_form_filler.py --recommend-model legal_forms

# Auto-select best model
python3 agentic_form_filler.py --form form.pdf --sources data.pdf \
  --ai-provider anthropic --auto-select-model
```

## 🔧 **Setup Instructions**

### **OpenAI Setup**
1. **Get API Key:** https://platform.openai.com/api-keys
2. **Set Environment Variable:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```
3. **Or use in command:**
   ```bash
   python3 agentic_form_filler.py --ai-provider openai --api-key "sk-your-key"
   ```

### **Anthropic Setup**
1. **Get API Key:** https://console.anthropic.com/
2. **Set Environment Variable:**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"
   ```
3. **Or use in command:**
   ```bash
   python3 agentic_form_filler.py --ai-provider anthropic --api-key "sk-ant-your-key"
   ```

### **Ollama Setup (Local)**
1. **Install Ollama:** https://ollama.ai/
2. **Start Ollama:**
   ```bash
   ollama serve
   ```
3. **Install Models:**
   ```bash
   ollama pull llama3.2
   ollama pull deepseek-r1
   ```
4. **Use (no API key needed):**
   ```bash
   python3 agentic_form_filler.py --ai-provider ollama --model llama3.2
   ```

## 📊 **Model Comparison Examples**

### **Accuracy vs Speed vs Cost**

| Task | Model | Speed | Accuracy | Cost | Best For |
|------|-------|-------|----------|------|----------|
| **Simple Forms** | gpt-4o-mini | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | Daily processing |
| **Legal Forms** | claude-3-5-sonnet | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💎 | Critical documents |
| **Data Extraction** | gpt-4o | ⚡⚡ | ⭐⭐⭐⭐ | 💎 | Complex extraction |
| **Budget Processing** | claude-3-haiku | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | Volume processing |
| **Local/Private** | llama3.2 | ⚡ | ⭐⭐ | 🆓 | Privacy-sensitive |

### **Real-World Usage Examples**

#### **Law Firm - Daily Operations**
```bash
# Morning: Simple intake forms (budget model)
python3 agentic_form_filler.py --form intake.pdf --sources client_info.txt \
  --ai-provider openai --model gpt-4o-mini

# Afternoon: Important legal documents (premium model)  
python3 agentic_form_filler.py --form divorce_petition.pdf --sources case_docs/ \
  --ai-provider anthropic --model claude-3-5-sonnet-20241022 --max-iterations 3

# End of day: Batch processing (auto-select)
for case in case_*; do
  python3 agentic_form_filler.py --form forms/standard.pdf --sources "$case/" \
    --ai-provider anthropic --auto-select-model --budget-priority
done
```

#### **Document Processing Service**
```bash
# High-volume processing (cost-optimized)
python3 agentic_form_filler.py --form template.pdf --sources batch_data/ \
  --ai-provider openai --model gpt-4o-mini --recursive

# Quality review (premium accuracy)
python3 agentic_form_filler.py --form complex_form.pdf --sources review_docs/ \
  --ai-provider anthropic --model claude-3-opus-20240229 --max-iterations 5
```

#### **Privacy-Sensitive Processing**
```bash
# Local processing (no data leaves your machine)
python3 agentic_form_filler.py --form confidential.pdf --sources sensitive_data/ \
  --ai-provider ollama --model llama3.2
```

## 🎯 **Quick Decision Matrix**

**Choose your model based on priority:**

### **🎯 Accuracy First**
1. **claude-3-5-sonnet-20241022** - Latest Anthropic model
2. **claude-3-opus-20240229** - Highest accuracy Claude
3. **o1-preview** - Best reasoning capabilities

### **💰 Cost First**  
1. **llama3.2** (Ollama) - Free local processing
2. **gpt-4o-mini** - Best OpenAI budget option
3. **claude-3-haiku** - Fast and affordable Claude

### **⚡ Speed First**
1. **gpt-4o-mini** - Fast OpenAI model
2. **claude-3-haiku** - Fastest Claude model
3. **gpt-3.5-turbo** - Quick for simple tasks

### **🔒 Privacy First**
1. **llama3.2** (Ollama) - Completely local
2. **deepseek-r1** (Ollama) - Local with good performance
3. Any Ollama model - No data leaves your machine

## 🔧 **Advanced Configuration**

### **Model Configuration Files**
```bash
# Export current setup
python3 model_selector.py --export my_models.json --task legal_forms

# Use saved configuration
python3 agentic_form_filler.py --config my_models.json
```

### **Environment-Based Selection**
```bash
# .env file configuration
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEFAULT_AI_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-5-sonnet-20241022
BUDGET_MODE=false
```

### **Batch Processing with Different Models**
```bash
#!/bin/bash
# process_cases.sh - Use different models for different case types

# Simple forms with budget model
find simple_forms/ -name "*.pdf" -exec \
  python3 agentic_form_filler.py --form {} --sources simple_data/ \
  --ai-provider openai --model gpt-4o-mini --output processed/{} \;

# Complex forms with premium model  
find complex_forms/ -name "*.pdf" -exec \
  python3 agentic_form_filler.py --form {} --sources complex_data/ \
  --ai-provider anthropic --model claude-3-5-sonnet-20241022 \
  --max-iterations 3 --output processed/{} \;
```

## 🆘 **Troubleshooting**

### **Common Issues**

#### **"No models available"**
```bash
# Check API access
python3 model_selector.py --test-access

# Verify API keys
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

#### **"Model not found"**
```bash
# List available models
python3 model_selector.py --list-all --provider openai

# Use auto-selection
python3 agentic_form_filler.py --auto-select-model
```

#### **"API key required"**
```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Or use command line
python3 agentic_form_filler.py --api-key "your-key"
```

#### **"Rate limit exceeded"**
```bash
# Use budget model (lower rate limits)
python3 agentic_form_filler.py --model gpt-4o-mini

# Add delays between requests
python3 agentic_form_filler.py --max-iterations 1
```

## 📚 **Additional Resources**

- **[model_selector.py](model_selector.py)** - Complete model discovery tool
- **[llm_client.py](llm_client.py)** - Model integration library
- **[OpenAI Models](https://platform.openai.com/docs/models)** - Official OpenAI documentation
- **[Anthropic Models](https://docs.anthropic.com/claude/docs/models-overview)** - Official Anthropic documentation  
- **[Ollama Models](https://ollama.ai/library)** - Available local models

## 🚀 **Getting Started Checklist**

1. **✅ Install Dependencies**
   ```bash
   pip install openai anthropic requests tabulate
   ```

2. **✅ Set Up API Keys**
   ```bash
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   ```

3. **✅ Test Access**
   ```bash
   python3 model_selector.py --test-access
   ```

4. **✅ Get Recommendations**
   ```bash
   python3 model_selector.py --recommend legal_forms
   ```

5. **✅ Start Processing**
   ```bash
   python3 agentic_form_filler.py --form form.pdf --sources data.pdf \
     --auto-select-model
   ```

**🎯 You're ready to process forms with the perfect AI model for your needs!**
