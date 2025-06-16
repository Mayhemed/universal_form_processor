import os
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests not available - Ollama features disabled")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ anthropic not available - Claude features disabled")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ openai not available - OpenAI features disabled")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

import json
from typing import List, Dict, Optional, Tuple

# Load environment variables from a .env file if present.
if DOTENV_AVAILABLE:
    try:
        load_dotenv()
    except:
        pass  # dotenv is optional

# Base URL for your local Ollama proxy.
OLLAMA_URL = "http://localhost:11434"

# Retrieve API keys from environment.
openai_api_key = os.getenv("OPENAI_API_KEY", "<YOUR_OPENAI_API_KEY>")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "<YOUR_ANTHROPIC_API_KEY>")

# Create the new OpenAI client if available
if OPENAI_AVAILABLE:
    client = OpenAI(api_key=openai_api_key)
else:
    client = None

def generate_with_openai(openai_model, prompt):
    """
    Send a prompt to the OpenAI ChatCompletion API using the new interface.
    """
    try:
        params = {}
        # For models that are not O1/O3, pass a temperature setting.
        if not ("o1" in openai_model or "o3" in openai_model):
            params["temperature"] = 0.7

        response = client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}],
            **params
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

def generate_with_claude(claude_model, prompt):
    """
    Generate a response from Claude using Anthropic's Python SDK.
    """
    # Normalize the model name
    if not claude_model.startswith("claude-"):
        claude_model = "claude-" + claude_model

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        # Check if the prompt contains a PDF file path
        if "[PDF_PATH:" in prompt:
            try:
                # Extract the PDF path
                pdf_path_start = prompt.find("[PDF_PATH:") + len("[PDF_PATH:")
                pdf_path_end = prompt.find("]", pdf_path_start)
                pdf_path = prompt[pdf_path_start:pdf_path_end].strip()
                
                # Remove the PDF path marker from the text prompt
                text_prompt = prompt.replace(f"[PDF_PATH: {pdf_path}]", "").strip()
                
                # Encode the PDF file to base64 for Claude
                import base64
                try:
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        
                        # Create messages with both text and PDF content
                        message = client.messages.create(
                            model=claude_model,
                            max_tokens=8192,
                            messages=[{
                                "role": "user",
                                "content": [
                                    # PDF document must use type "document" not "image"
                                    {
                                        "type": "document",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "application/pdf",
                                            "data": base64_pdf
                                        }
                                    },
                                    # Text prompt comes after the document
                                    {"type": "text", "text": text_prompt}
                                ]
                            }],
                            temperature=0.7,
                            stream=False,
                        )
                except Exception as e:
                    # Fall back to text-only
                    message = client.messages.create(
                        model=claude_model,
                        max_tokens=8192,
                        messages=[{"role": "user", "content": text_prompt}],
                        temperature=0.7,
                        stream=False,
                    )
            except Exception as e:
                # Fall back to text-only
                message = client.messages.create(
                    model=claude_model,
                    max_tokens=8192,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    stream=False,
                )
        else:
            # Standard text-only message
            message = client.messages.create(
                model=claude_model,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=False,
            )
        
        # Extract text from response
        result_text = ""
        if hasattr(message, "content"):
            content_blocks = message.content
        else:
            content_blocks = []
            
        for block in content_blocks:
            if hasattr(block, "text"):
                result_text += block.text
                
        return result_text
    except Exception as e:
        return f"Error calling Claude messages API: {e}"

# ===== MODEL DISCOVERY AND SELECTION SYSTEM =====

def get_available_openai_models(api_key: Optional[str] = None) -> Dict[str, Dict]:
    """
    Get available OpenAI models with detailed information
    Returns dict with model info including context windows, capabilities, etc.
    """
    if not api_key:
        api_key = openai_api_key
    
    if not api_key or api_key == "<YOUR_OPENAI_API_KEY>":
        return get_default_openai_models()
    
    try:
        temp_client = OpenAI(api_key=api_key)
        models_response = temp_client.models.list()
        
        models_info = {}
        for model in models_response.data:
            model_id = model.id
            
            # Add detailed info based on known model capabilities
            models_info[model_id] = {
                "id": model_id,
                "provider": "openai",
                "context_window": get_openai_context_window(model_id),
                "max_output": get_openai_max_output(model_id),
                "capabilities": get_openai_capabilities(model_id),
                "cost_tier": get_openai_cost_tier(model_id),
                "recommended_for": get_openai_recommendations(model_id),
                "created": getattr(model, 'created', None)
            }
        
        return models_info
        
    except Exception as e:
        print(f"Error fetching OpenAI models: {e}")
        return get_default_openai_models()

def get_available_anthropic_models(api_key: Optional[str] = None) -> Dict[str, Dict]:
    """
    Get available Anthropic models with detailed information
    """
    if not api_key:
        api_key = ANTHROPIC_API_KEY
    
    if not api_key or api_key == "<YOUR_ANTHROPIC_API_KEY>":
        return get_default_anthropic_models()
    
    try:
        temp_client = anthropic.Anthropic(api_key=api_key)
        # Note: Anthropic doesn't have a public models.list() endpoint
        # So we return our curated list with the latest known models
        return get_default_anthropic_models()
        
    except Exception as e:
        print(f"Error with Anthropic client: {e}")
        return get_default_anthropic_models()

def get_available_ollama_models() -> Dict[str, Dict]:
    """
    Get available local Ollama models
    """
    if not REQUESTS_AVAILABLE:
        print("⚠️ requests library not available - cannot check Ollama models")
        return {}
        
    try:
        resp = requests.get(f"{OLLAMA_URL}/v1/models", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        models_info = {}
        for model_data in data.get("data", []):
            model_id = model_data.get("id", "")
            if model_id:
                models_info[model_id] = {
                    "id": model_id,
                    "provider": "ollama",
                    "context_window": get_ollama_context_window(model_id),
                    "max_output": 4096,  # Default for most Ollama models
                    "capabilities": ["text_generation", "local_inference"],
                    "cost_tier": "free",
                    "recommended_for": ["privacy", "offline_use", "experimentation"],
                    "local": True
                }
        
        return models_info
        
    except Exception as e:
        print(f"Ollama not available: {e}")
        return {}

def get_all_available_models(openai_key: Optional[str] = None, 
                           anthropic_key: Optional[str] = None) -> Dict[str, Dict]:
    """
    Get all available models from all providers
    """
    all_models = {}
    
    # Get OpenAI models
    openai_models = get_available_openai_models(openai_key)
    all_models.update(openai_models)
    
    # Get Anthropic models
    anthropic_models = get_available_anthropic_models(anthropic_key)
    all_models.update(anthropic_models)
    
    # Get Ollama models
    ollama_models = get_available_ollama_models()
    all_models.update(ollama_models)
    
    return all_models

# Default model definitions (fallback when API calls fail)

def get_default_openai_models() -> Dict[str, Dict]:
    """Default OpenAI models with known specifications"""
    return {
        "gpt-4o": {
            "id": "gpt-4o",
            "provider": "openai",
            "context_window": 128000,
            "max_output": 4096,
            "capabilities": ["text_generation", "reasoning", "vision", "function_calling"],
            "cost_tier": "premium",
            "recommended_for": ["complex_reasoning", "code_generation", "analysis"],
            "description": "Most advanced OpenAI model with vision capabilities"
        },
        "gpt-4o-mini": {
            "id": "gpt-4o-mini",
            "provider": "openai", 
            "context_window": 128000,
            "max_output": 16384,
            "capabilities": ["text_generation", "reasoning", "vision", "function_calling"],
            "cost_tier": "budget",
            "recommended_for": ["cost_effective", "fast_inference", "simple_tasks"],
            "description": "Efficient model balancing cost and capability"
        },
        "gpt-4-turbo": {
            "id": "gpt-4-turbo",
            "provider": "openai",
            "context_window": 128000,
            "max_output": 4096,
            "capabilities": ["text_generation", "reasoning", "vision", "function_calling"],
            "cost_tier": "premium",
            "recommended_for": ["complex_analysis", "long_documents", "accuracy"],
            "description": "High-performance model for complex tasks"
        },
        "gpt-3.5-turbo": {
            "id": "gpt-3.5-turbo",
            "provider": "openai",
            "context_window": 16385,
            "max_output": 4096,
            "capabilities": ["text_generation", "function_calling"],
            "cost_tier": "budget",
            "recommended_for": ["simple_tasks", "cost_optimization", "fast_response"],
            "description": "Fast and cost-effective for simple tasks"
        },
        "o1-preview": {
            "id": "o1-preview",
            "provider": "openai",
            "context_window": 128000,
            "max_output": 32768,
            "capabilities": ["advanced_reasoning", "complex_problem_solving"],
            "cost_tier": "premium",
            "recommended_for": ["complex_reasoning", "scientific_analysis", "mathematics"],
            "description": "Advanced reasoning model for complex problems"
        },
        "o1-mini": {
            "id": "o1-mini",
            "provider": "openai",
            "context_window": 128000,
            "max_output": 65536,
            "capabilities": ["reasoning", "problem_solving"],
            "cost_tier": "standard",
            "recommended_for": ["logical_reasoning", "coding", "analysis"],
            "description": "Efficient reasoning model"
        }
    }

def get_default_anthropic_models() -> Dict[str, Dict]:
    """Default Anthropic models with known specifications"""
    return {
        "claude-3-5-sonnet-20241022": {
            "id": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
            "context_window": 200000,
            "max_output": 8192,
            "capabilities": ["text_generation", "reasoning", "vision", "analysis"],
            "cost_tier": "premium",
            "recommended_for": ["legal_documents", "complex_analysis", "writing"],
            "description": "Latest Claude model with enhanced capabilities"
        },
        "claude-3-5-haiku-20241022": {
            "id": "claude-3-5-haiku-20241022",
            "provider": "anthropic",
            "context_window": 200000,
            "max_output": 8192,
            "capabilities": ["text_generation", "vision", "fast_inference"],
            "cost_tier": "budget",
            "recommended_for": ["cost_effective", "simple_tasks", "speed"],
            "description": "Fast and efficient Claude model"
        },
        "claude-3-opus-20240229": {
            "id": "claude-3-opus-20240229",
            "provider": "anthropic",
            "context_window": 200000,
            "max_output": 4096,
            "capabilities": ["text_generation", "reasoning", "vision", "complex_analysis"],
            "cost_tier": "premium",
            "recommended_for": ["highest_accuracy", "complex_reasoning", "creative_writing"],
            "description": "Most capable Claude model for complex tasks"
        },
        "claude-3-sonnet-20240229": {
            "id": "claude-3-sonnet-20240229",
            "provider": "anthropic",
            "context_window": 200000,
            "max_output": 4096,
            "capabilities": ["text_generation", "reasoning", "vision"],
            "cost_tier": "standard",
            "recommended_for": ["balanced_performance", "general_use", "document_analysis"],
            "description": "Balanced Claude model for general use"
        },
        "claude-3-haiku-20240307": {
            "id": "claude-3-haiku-20240307",
            "provider": "anthropic",
            "context_window": 200000,
            "max_output": 4096,
            "capabilities": ["text_generation", "vision", "fast_response"],
            "cost_tier": "budget",
            "recommended_for": ["speed", "simple_extraction", "cost_optimization"],
            "description": "Fastest Claude model for simple tasks"
        }
    }

# Helper functions for model capabilities

def get_openai_context_window(model_id: str) -> int:
    """Get context window for OpenAI model"""
    if "gpt-4o" in model_id or "gpt-4-turbo" in model_id:
        return 128000
    elif "o1" in model_id:
        return 128000
    elif "gpt-4" in model_id:
        return 8192
    elif "gpt-3.5" in model_id:
        return 16385
    return 4096

def get_openai_max_output(model_id: str) -> int:
    """Get max output tokens for OpenAI model"""
    if "o1-mini" in model_id:
        return 65536
    elif "o1-preview" in model_id:
        return 32768
    elif "gpt-4o-mini" in model_id:
        return 16384
    return 4096

def get_openai_capabilities(model_id: str) -> List[str]:
    """Get capabilities for OpenAI model"""
    base_caps = ["text_generation"]
    
    if "gpt-4" in model_id or "gpt-4o" in model_id:
        base_caps.extend(["reasoning", "vision", "function_calling"])
    elif "o1" in model_id:
        base_caps.extend(["advanced_reasoning", "complex_problem_solving"])
    elif "gpt-3.5" in model_id:
        base_caps.append("function_calling")
    
    return base_caps

def get_openai_cost_tier(model_id: str) -> str:
    """Get cost tier for OpenAI model"""
    if "o1-preview" in model_id or "gpt-4o" in model_id:
        return "premium"
    elif "gpt-4o-mini" in model_id or "gpt-3.5" in model_id:
        return "budget"
    elif "o1-mini" in model_id or "gpt-4" in model_id:
        return "standard"
    return "standard"

def get_openai_recommendations(model_id: str) -> List[str]:
    """Get recommendations for when to use OpenAI model"""
    if "o1" in model_id:
        return ["complex_reasoning", "scientific_analysis", "mathematics", "logic_problems"]
    elif "gpt-4o" in model_id:
        return ["complex_analysis", "vision_tasks", "code_generation", "reasoning"]
    elif "gpt-4" in model_id:
        return ["accuracy", "complex_tasks", "professional_writing"]
    elif "gpt-3.5" in model_id:
        return ["cost_optimization", "simple_tasks", "fast_response"]
    return ["general_use"]

def get_ollama_context_window(model_id: str) -> int:
    """Get context window for Ollama model"""
    if "llama" in model_id.lower():
        return 8192
    elif "deepseek" in model_id.lower():
        return 4096
    elif "qwen" in model_id.lower():
        return 8192
    return 4096

def recommend_model_for_task(task_type: str, available_models: Dict[str, Dict], 
                           budget_priority: bool = False) -> List[str]:
    """
    Recommend models for specific tasks
    
    Args:
        task_type: Type of task (legal_forms, data_extraction, etc.)
        available_models: Dict of available models
        budget_priority: Whether to prioritize cost-effective models
    
    Returns:
        List of recommended model IDs in order of preference
    """
    recommendations = []
    
    task_requirements = {
        "legal_forms": {
            "capabilities": ["text_generation", "reasoning", "analysis"],
            "context_window_min": 32000,
            "accuracy_priority": True
        },
        "data_extraction": {
            "capabilities": ["text_generation", "vision"],
            "context_window_min": 8000,
            "accuracy_priority": True
        },
        "simple_forms": {
            "capabilities": ["text_generation"],
            "context_window_min": 4000,
            "accuracy_priority": False
        },
        "complex_analysis": {
            "capabilities": ["reasoning", "complex_analysis"],
            "context_window_min": 50000,
            "accuracy_priority": True
        }
    }
    
    requirements = task_requirements.get(task_type, task_requirements["data_extraction"])
    
    # Score models based on requirements
    model_scores = []
    for model_id, model_info in available_models.items():
        score = 0
        
        # Check capabilities
        model_caps = model_info.get("capabilities", [])
        for req_cap in requirements["capabilities"]:
            if req_cap in model_caps:
                score += 10
        
        # Check context window
        context_window = model_info.get("context_window", 0)
        if context_window >= requirements["context_window_min"]:
            score += 20
        
        # Cost consideration
        cost_tier = model_info.get("cost_tier", "standard")
        if budget_priority:
            if cost_tier == "budget":
                score += 15
            elif cost_tier == "standard":
                score += 10
            elif cost_tier == "premium":
                score += 5
        else:
            if cost_tier == "premium":
                score += 15
            elif cost_tier == "standard":
                score += 10
            elif cost_tier == "budget":
                score += 5
        
        # Accuracy priority boost
        if requirements["accuracy_priority"]:
            recommended_for = model_info.get("recommended_for", [])
            if any(term in recommended_for for term in ["accuracy", "complex_analysis", "legal_documents"]):
                score += 10
        
        model_scores.append((model_id, score))
    
    # Sort by score and return top recommendations
    model_scores.sort(key=lambda x: x[1], reverse=True)
    return [model_id for model_id, score in model_scores[:5]]
