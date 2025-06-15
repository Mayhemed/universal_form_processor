import os
import requests
import anthropic
from openai import OpenAI  # after migration, use the OpenAI class
from dotenv import load_dotenv  # pip install python-dotenv

# Load environment variables from a .env file if present.
load_dotenv()

# Base URL for your local Ollama proxy.
OLLAMA_URL = "http://localhost:11434"

# Retrieve API keys from environment.
openai_api_key = os.getenv("OPENAI_API_KEY", "<YOUR_OPENAI_API_KEY>")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "<YOUR_ANTHROPIC_API_KEY>")

# Create the new OpenAI client.
client = OpenAI(api_key=openai_api_key)

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
