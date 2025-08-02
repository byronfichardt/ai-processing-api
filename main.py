from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import openai
import os
import time
from dotenv import load_dotenv
import json
from datetime import datetime
import requests
import asyncio
import re
import json
from urllib.parse import urlparse
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging for Ollama responses
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ollama_responses.log', mode='a'),
        logging.StreamHandler()
    ]
)
ollama_logger = logging.getLogger('ollama_responses')

# Initialize FastAPI app
app = FastAPI(
    title="AI Processing API",
    description="A simple API that processes requests with AI and returns formatted JSON",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure AI providers
openai.api_key = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Base system prompt for JSON structuring
DEFAULT_SYSTEM_PROMPT = """You are a JSON structuring engine.

RULES:
1. Take the input EXACTLY as provided by the user.
2. Do NOT interpret, summarize, rewrite, or add any information.
3. Preserve ALL words, spelling, punctuation, symbols, line breaks, and formatting EXACTLY as they appear.
4. Do NOT infer product names, descriptions, or create extra data not explicitly present in the input.
5. Output ONLY valid JSON. Do NOT include explanations or any text outside the JSON.
6. If unsure, wrap the input exactly as-is into the "raw_input" field.

Your output format must always be:

{
  "structured": {
    // Create keys ONLY for clearly identifiable sections or labels in the input.
    // Use the exact wording from the input for the values.
    // If no structure is identifiable, leave this object empty.
  }
}

- Do NOT rephrase or interpret values when filling fields.
- If there are no fields to extract, leave "structured" as an empty object."""

# Request models
class ProcessRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    task_type: Optional[str] = "general"
    format_type: Optional[str] = "json"
    additional_context: Optional[str] = None
    model_provider: Optional[str] = "openai"  # "openai" or "ollama"
    model_name: Optional[str] = None  # Specific model name for the provider
    system_prompt: Optional[str] = None  # Custom system instructions for the AI model

class ProcessResponse(BaseModel):
    success: bool
    result: str
    model_used: str
    processing_time: float
    source_type: str  # "text" or "url"
    source: str  # original text or URL

@app.get("/")
async def root():
    """Root endpoint - serves the web interface"""
    return FileResponse("static/index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "AI Processing API",
        "version": "1.0.0",
        "endpoints": {
            "/process": "POST - Process text with AI",
            "/health": "GET - Health check",
            "/models": "GET - List available models",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/models")
def list_models():
    """List available models from both providers with detailed information"""
    models = {
        "openai": [],
        "ollama": []
    }
    
    # OpenAI models (static list of common ones)
    if openai.api_key:
        models["openai"] = [
            {
                "name": "gpt-3.5-turbo",
                "context_window": 4096,
                "description": "Fast and efficient model for most tasks"
            },
            {
                "name": "gpt-4",
                "context_window": 8192,
                "description": "More capable model for complex tasks"
            },
            {
                "name": "gpt-4-turbo-preview",
                "context_window": 128000,
                "description": "Latest model with extended context"
            }
        ]
    
    # Ollama models with detailed information
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=30)
        if response.status_code == 200:
            data = response.json()
            ollama_models = []
            
            for model in data.get("models", []):
                model_info = {
                    "name": model["name"],
                    "size": model.get("size", "Unknown"),
                    "modified_at": model.get("modified_at", "Unknown"),
                    "details": {},  # Will be updated below
                    "model_info": {},  # Will be updated below
                    "capabilities": []  # Will be updated below
                }
                
                # Try to get detailed model information including context window
                try:
                    ollama_logger.info(f"Requesting details for model: {model['name']}")
                    detail_response = requests.post(
                        f"{OLLAMA_BASE_URL}/api/show",
                        json={"model": model["name"]},
                        timeout=30
                    )
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        
                        # Log the full response
                        ollama_logger.info(f"Ollama response for {model['name']}: {json.dumps(detail_data, indent=2)}")
                        
                        # Extract context window from model parameters
                        if "model_info" in detail_data:
                            model_info["model_info"] = detail_data["model_info"]
                        
                        # Add additional model details
                        if "details" in detail_data:
                            model_info["details"] = detail_data["details"]

                        if "capabilities" in detail_data:
                            model_info["capabilities"] = detail_data["capabilities"]
                        
                except Exception as e:
                    # If detailed info fails, keep basic info
                    ollama_logger.error(f"Error getting details for {model['name']}: {str(e)}")
                    pass
                
                ollama_models.append(model_info)
            
            models["ollama"] = ollama_models
            
    except Exception:
        pass  # Silently fail if Ollama is not available
    
    return models

@app.post("/show")
def show_model_details(request: Dict[str, Any]):
    """Get detailed information about a specific model"""
    provider = request.get("provider")
    model_name = request.get("model")
    detailed = request.get("detailed", False)
    
    if not provider or not model_name:
        raise HTTPException(status_code=400, detail="Provider and model name are required")
    
    if provider == "ollama":
        try:
            # Log the request
            ollama_logger.info(f"Show endpoint - Requesting details for model: {model_name}")
            
            # Call Ollama's show endpoint to get detailed model information
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/show",
                json={"model": model_name},
                timeout=30
            )
            
            if response.status_code == 200:
                model_data = response.json()
                
                # Log the response without tensors to reduce log size
                log_data = {k: v for k, v in model_data.items() if k != 'tensors'}
                ollama_logger.info(f"Show endpoint - Ollama response for {model_name}: {json.dumps(log_data, indent=2)}")
                
                # If detailed info is requested, return the full response
                if detailed:
                    return {
                        "models": [model_data]
                    }
                else:
                    # Return basic model info
                    return {
                        "models": [{
                            "name": model_data.get("name", model_name),
                            "size": model_data.get("size"),
                            "modified_at": model_data.get("modified_at"),
                            "description": f"Ollama model: {model_name}"
                        }]
                    }
            else:
                ollama_logger.error(f"Show endpoint - Failed to get details for {model_name}: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Failed to get model details from Ollama")
                
        except requests.exceptions.RequestException as e:
            ollama_logger.error(f"Show endpoint - Request exception for {model_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")
    
    elif provider == "openai":
        # For OpenAI, return basic model info
        return {
            "models": [{
                "name": model_name,
                "description": f"OpenAI model: {model_name}",
                "provider": "openai"
            }]
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check OpenAI availability
    openai_available = bool(openai.api_key)
    
    # Check Ollama availability
    ollama_available = False
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=30)
        ollama_available = response.status_code == 200
    except:
        pass
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "providers": {
            "openai": {
                "available": openai_available,
                "configured": bool(openai.api_key)
            },
            "ollama": {
                "available": ollama_available,
                "base_url": OLLAMA_BASE_URL
            }
        }
    }

@app.post("/process", response_model=ProcessResponse)
async def process_with_ai(request: ProcessRequest):
    """
    Process text with AI and return formatted JSON response
    """
    import time
    start_time = time.time()
    
    try:
        # Determine the source of the input
        if request.url:
            source_type = "url"
            source_text = await fetch_web_content(request.url)
            source = request.url
        elif request.text:
            source_type = "text"
            source_text = request.text
            source = request.text[:100] + "..." if len(request.text) > 100 else request.text
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'text' or 'url' must be provided for processing."
            )
        
        # Build the prompt
        prompt = build_prompt(source_text, source_type)
        
        # Determine which AI service to use
        if request.model_provider == "ollama":
            result = await call_ollama(prompt, request.model_name, request.system_prompt)
            model_used = f"ollama:{request.model_name or 'llama2'}"
        else:
            result = await call_openai(prompt, request.model_name, request.system_prompt)
            model_used = f"openai:{request.model_name or 'gpt-3.5-turbo'}"
        
        processing_time = time.time() - start_time
        
        return ProcessResponse(
            success=True,
            result=result,
            model_used=model_used,
            processing_time=processing_time,
            source_type=source_type,
            source=source
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )

@app.post("/process-stream")
async def process_with_ai_stream(request: ProcessRequest):
    """
    Process text with AI and return streaming response
    """
    import time
    start_time = time.time()
    
    try:
        # Determine the source of the input
        if request.url:
            source_type = "url"
            source_text = await fetch_web_content(request.url)
            source = request.url
        elif request.text:
            source_type = "text"
            source_text = request.text
            source = request.text[:100] + "..." if len(request.text) > 100 else request.text
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'text' or 'url' must be provided for processing."
            )
        
        # Build the prompt
        prompt = build_prompt(source_text, source_type)
        
        # Determine which AI service to use and stream the response
        if request.model_provider == "ollama":
            return StreamingResponse(
                stream_ollama_response(prompt, request.model_name, source_type, source, start_time, request.system_prompt),
                media_type="text/plain"
            )
        else:
            return StreamingResponse(
                stream_openai_response(prompt, request.model_name, source_type, source, start_time, request.system_prompt),
                media_type="text/plain"
            )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )

async def call_openai(prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
    """Call OpenAI API"""
    if not openai.api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )
    
    model = model_name or "gpt-3.5-turbo"
    
    # Use custom system prompt if provided, otherwise use default
    system_content = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content.strip()

async def call_ollama(prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
    """Call Ollama API"""
    model = model_name or "llama2"
    
    try:
        # Log the request
        ollama_logger.info(f"Generate request - Model: {model}, Prompt length: {len(prompt)}")
        
        # Use custom system prompt if provided, otherwise use default
        system_content = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": f"{system_content}\n\n{prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            },
            timeout=120
        )
        
        if response.status_code != 200:
            ollama_logger.error(f"Generate request - API error for {model}: {response.status_code} - {response.text}")
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        
        data = response.json()
        response_text = data.get("response", "").strip()
        
        # Log the response (truncated for readability)
        response_preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
        ollama_logger.info(f"Generate request - Response for {model}: {response_preview}")
        
        return response_text
        
    except requests.exceptions.RequestException as e:
        ollama_logger.error(f"Generate request - Connection error for {model}: {str(e)}")
        raise Exception(f"Failed to connect to Ollama at {OLLAMA_BASE_URL}: {str(e)}")
    except Exception as e:
        ollama_logger.error(f"Generate request - General error for {model}: {str(e)}")
        raise Exception(f"Ollama API error: {str(e)}")

def build_prompt(text: str, source_type: str = "text") -> str:
    """Build a structured prompt for AI processing"""
    source_info = f"web page content" if source_type == "url" else "text"
    
    return f"""
Please process the following {source_info} and return a well-formatted JSON response:

{text}

Requirements:
- Return valid JSON format
- Include relevant information extracted or generated from the {source_info}
- Structure the response logically
- If the {source_info} contains questions, provide answers
- If the {source_info} contains data, organize it appropriately
- If processing a web page, extract key information, summarize content, and identify main topics
"""

# Helper function to validate and fetch web content
async def fetch_web_content(url: str) -> str:
    """Fetch and extract text content from a web URL"""
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Fetch content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Extract text content (basic implementation)
        content = response.text
        
        # Remove HTML tags and clean up
        # Remove script and style elements
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # Limit content length to avoid token limits
        if len(content) > 8000:
            content = content[:8000] + "... [Content truncated]"
        
        return content
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing URL: {str(e)}")

async def stream_ollama_response(prompt: str, model_name: Optional[str], source_type: str, source: str, start_time: float, system_prompt: Optional[str] = None):
    """Stream response from Ollama"""
    model = model_name or "llama2"
    
    try:
        # Log the request
        ollama_logger.info(f"Stream request - Model: {model}, Prompt length: {len(prompt)}")
        
        # Use custom system prompt if provided, otherwise use default
        system_content = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
        
        # Stream the response from Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": f"{system_content}\n\n{prompt}",
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            },
            timeout=120,
            stream=True
        )
        
        if response.status_code != 200:
            ollama_logger.error(f"Stream request - API error for {model}: {response.status_code} - {response.text}")
            yield f"data: {json.dumps({'error': f'Ollama API error: {response.status_code}'})}\n\n"
            return
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'response' in data:
                        chunk = data['response']
                        full_response += chunk
                        yield f"data: {json.dumps({'chunk': chunk, 'done': data.get('done', False)})}\n\n"
                    
                    if data.get('done', False):
                        processing_time = time.time() - start_time
                        yield f"data: {json.dumps({'done': True, 'processing_time': processing_time, 'model_used': f'ollama:{model}', 'source_type': source_type, 'source': source})}\n\n"
                        break
                        
                except json.JSONDecodeError:
                    continue
                    
    except requests.exceptions.RequestException as e:
        ollama_logger.error(f"Stream request - Connection error for {model}: {str(e)}")
        yield f"data: {json.dumps({'error': f'Failed to connect to Ollama: {str(e)}'})}\n\n"
    except Exception as e:
        ollama_logger.error(f"Stream request - General error for {model}: {str(e)}")
        yield f"data: {json.dumps({'error': f'Ollama API error: {str(e)}'})}\n\n"

async def stream_openai_response(prompt: str, model_name: Optional[str], source_type: str, source: str, start_time: float, system_prompt: Optional[str] = None):
    """Stream response from OpenAI"""
    if not openai.api_key:
        yield f"data: {json.dumps({'error': 'OpenAI API key not configured'})}\n\n"
        return
    
    model = model_name or "gpt-3.5-turbo"
    
    try:
        # Use custom system prompt if provided, otherwise use default
        system_content = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
        
        # Stream the response from OpenAI
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield f"data: {json.dumps({'chunk': content, 'done': False})}\n\n"
        
        processing_time = time.time() - start_time
        yield f"data: {json.dumps({'done': True, 'processing_time': processing_time, 'model_used': f'openai:{model}', 'source_type': source_type, 'source': source})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': f'OpenAI API error: {str(e)}'})}\n\n"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 