#!/usr/bin/env python3
"""
Startup script for the AI Processing API
Checks environment setup and starts the server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        import pydantic
        import dotenv
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has API keys"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  No .env file found")
        print("Creating .env file from template...")
        
        # Copy from env_example.txt if it exists
        example_file = Path("env_example.txt")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Created .env file from template")
        else:
            # Create basic .env file
            with open(env_file, 'w') as f:
                f.write("# OpenAI API Configuration\n")
                f.write("# Get your API key from: https://platform.openai.com/api-keys\n")
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                f.write("\n# Ollama Configuration\n")
                f.write("OLLAMA_BASE_URL=http://localhost:11434\n")
            print("✅ Created basic .env file")
        
        print("⚠️  Please edit .env file and add your API keys")
        return False
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  OpenAI API key not configured in .env file")
        print("Please edit .env file and add your OpenAI API key")
        print("Note: You can still use Ollama models without OpenAI")
        return False
    
    print("✅ OpenAI API key is configured")
    print(f"✅ Ollama URL configured: {ollama_url}")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting AI Processing API...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        print("\n⚠️  Environment not fully configured")
        print("You can still start the server, but AI processing will not work without an API key")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n✅ Environment check completed")
    print("Starting server...")
    print("=" * 50)
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 