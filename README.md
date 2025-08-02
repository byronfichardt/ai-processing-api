# AI Processing API

[![CI](https://github.com/byronfichardt/ai-processing-api/actions/workflows/ci.yml/badge.svg)](https://github.com/byronfichardt/ai-processing-api/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

A powerful FastAPI-based API that processes text and web content with AI and returns formatted JSON responses. Supports both OpenAI and local Ollama models with advanced features including streaming responses, URL processing, and a web interface.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/byronfichardt/ai-processing-api.git
cd ai-processing-api

# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here

# Run with Docker Compose (includes Ollama)
docker-compose up -d

# Access the API
curl http://localhost:8000/health

# Access the web interface
open http://localhost:8000/static/
```

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/byronfichardt/ai-processing-api.git
cd ai-processing-api

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env_example.txt .env
# Edit .env with your API keys

# Run the server
python start.py
```

## ✨ Features

- **Text & URL Processing**: Process both direct text input and web content from URLs
- **Multiple AI Providers**: Support for OpenAI and local Ollama models
- **Streaming Responses**: Real-time streaming of AI responses for better UX
- **Web Interface**: Built-in web UI for easy testing and interaction
- **Advanced Task Types**: Support for summarization, analysis, extraction, translation, and custom tasks
- **JSON Structuring**: Intelligent JSON formatting with custom system prompts
- **Error Handling**: Comprehensive error handling and validation
- **Health Checks**: Built-in health monitoring with AI provider status
- **CORS Support**: Cross-origin request support
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Logging**: Detailed logging of Ollama responses for debugging

## 📋 Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional, for cloud AI)
- Ollama (optional, for local AI models)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy the example file
cp env_example.txt .env

# Edit the .env file and add your API keys
OPENAI_API_KEY=your_actual_openai_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

**Get your OpenAI API key from:** [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 3. Set up Ollama (Optional)

If you want to use local Ollama models:

1. **Install Ollama**: Visit [https://ollama.ai](https://ollama.ai) and follow the installation instructions
2. **Start Ollama**: Run `ollama serve` to start the Ollama server
3. **Pull a model**: Run `ollama pull llama2` to download a model
4. **Verify connection**: The API will automatically detect if Ollama is running

### 4. Run the API

```bash
python start.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`
The web interface will be available at: `http://localhost:8000/static/`

## 🌐 Web Interface

Access the built-in web interface at `http://localhost:8000/static/` for:

- **Easy Testing**: No need for curl or Postman
- **Real-time Streaming**: See AI responses as they're generated
- **Model Selection**: Choose between OpenAI and Ollama models
- **Task Configuration**: Configure different task types and formats
- **URL Processing**: Test URL content extraction directly
- **Response History**: View and copy previous responses

## API Endpoints

### Root Endpoint
- **GET** `/` - API information and available endpoints
- **GET** `/api` - Detailed API information

### Health Check
- **GET** `/health` - Check API health and AI provider availability

### Process Content
- **POST** `/process` - Process text or URL content with AI
- **POST** `/process-stream` - Stream AI responses in real-time

### Models
- **GET** `/models` - List available models from all providers
- **POST** `/show` - Get detailed information about specific models

### Web Interface
- **GET** `/static/` - Built-in web interface for testing

### API Documentation
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation

## Usage Examples

### Basic Text Processing

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog.",
    "task_type": "analyze",
    "format_type": "json"
  }'
```

### URL Content Processing

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "task_type": "summarize",
    "format_type": "json"
  }'
```

### Streaming Response

```bash
curl -X POST "http://localhost:8000/process-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Write a short story about a robot learning to paint.",
    "task_type": "general",
    "format_type": "json"
  }'
```

### Text Summarization

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text content here...",
    "task_type": "summarize",
    "format_type": "json"
  }'
```

### Information Extraction

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact John Doe at john@example.com or call 555-1234",
    "task_type": "extract",
    "format_type": "json",
    "additional_context": "Extract contact information"
  }'
```

### Using Ollama Models

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you today?",
    "task_type": "analyze",
    "format_type": "json",
    "model_provider": "ollama",
    "model_name": "llama2"
  }'
```

### Custom System Prompts

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Analyze this technical document",
    "task_type": "analyze",
    "format_type": "json",
    "system_prompt": "You are a technical expert. Focus on identifying key technical concepts and their relationships."
  }'
```

## Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | No* | null | The text to be processed |
| `url` | string | No* | null | URL to fetch and process content from |
| `task_type` | string | No | "general" | Type of processing: "general", "summarize", "analyze", "extract", "translate" |
| `format_type` | string | No | "json" | Response format: "json" or "text" |
| `additional_context` | string | No | null | Additional context or instructions |
| `model_provider` | string | No | "openai" | AI provider: "openai" or "ollama" |
| `model_name` | string | No | null | Specific model name for the provider |
| `system_prompt` | string | No | null | Custom system instructions for the AI model |

*Either `text` or `url` must be provided

## Response Format

### Standard Response
```json
{
  "success": true,
  "result": "AI processed result",
  "model_used": "gpt-3.5-turbo",
  "processing_time": 1.234,
  "source_type": "text",
  "source": "original text or URL"
}
```

### Streaming Response
The `/process-stream` endpoint returns a Server-Sent Events (SSE) stream with real-time updates.

## Error Handling

The API returns structured error responses:

```json
{
  "success": false,
  "result": "",
  "model_used": "",
  "processing_time": 0.123,
  "source_type": "text",
  "source": "original input",
  "error": "Error description"
}
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t ai-processing-api .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ai-processing-api
```

## 🧪 Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API

1. Start the server
2. Visit `http://localhost:8000/docs` for interactive testing
3. Use the Swagger UI to test endpoints
4. Visit `http://localhost:8000/static/` for the web interface
5. Run automated tests: `python test_api.py`

### Code Quality

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Security checks
bandit -r .
safety check
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📦 Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type annotations
- **OpenAI**: Python client for OpenAI API
- **python-dotenv**: Environment variable management
- **python-multipart**: Form data parsing
- **requests**: HTTP library for Ollama integration and URL fetching

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [OpenAI](https://openai.com/) for providing the AI API
- [Ollama](https://ollama.ai/) for local AI model support 