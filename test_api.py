#!/usr/bin/env python3
"""
Test script for the AI Processing API
Demonstrates various usage examples
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root_endpoint():
    """Test the root endpoint"""
    print("🏠 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_text_analysis():
    """Test text analysis"""
    print("📊 Testing text analysis...")
    data = {
        "text": "The quick brown fox jumps over the lazy dog. This is a classic pangram that contains every letter of the English alphabet at least once.",
        "task_type": "analyze",
        "format_type": "json"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_text_summarization():
    """Test text summarization"""
    print("📝 Testing text summarization...")
    data = {
        "text": """
        Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. 
        Some of the activities computers with artificial intelligence are designed for include speech recognition, learning, planning, and problem solving. 
        AI has been used in various fields including healthcare, finance, transportation, and entertainment. 
        Machine learning, a subset of AI, enables computers to learn and improve from experience without being explicitly programmed.
        """,
        "task_type": "summarize",
        "format_type": "json"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_information_extraction():
    """Test information extraction"""
    print("🔍 Testing information extraction...")
    data = {
        "text": "Contact John Doe at john.doe@example.com or call +1-555-123-4567. Office address: 123 Main Street, New York, NY 10001.",
        "task_type": "extract",
        "format_type": "json",
        "additional_context": "Extract contact information including email, phone, and address"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_translation():
    """Test text translation"""
    print("🌍 Testing text translation...")
    data = {
        "text": "Hello, how are you today?",
        "task_type": "translate",
        "format_type": "json",
        "additional_context": "Translate to Spanish"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_general_processing():
    """Test general text processing"""
    print("⚙️ Testing general text processing...")
    data = {
        "text": "The weather is beautiful today with clear skies and a gentle breeze.",
        "task_type": "general",
        "format_type": "json"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_ollama_processing():
    """Test Ollama processing"""
    print("🦙 Testing Ollama processing...")
    data = {
        "text": "Hello, how are you today?",
        "task_type": "analyze",
        "format_type": "json",
        "model_provider": "ollama",
        "model_name": "llama2"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_models_endpoint():
    """Test models endpoint"""
    print("📋 Testing models endpoint...")
    response = requests.get(f"{BASE_URL}/models")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting AI Processing API Tests")
    print("=" * 50)
    
    try:
        # Test basic endpoints
        test_health_check()
        test_root_endpoint()
        
        # Test AI processing endpoints
        test_text_analysis()
        test_text_summarization()
        test_information_extraction()
        test_translation()
        test_general_processing()
        
        # Test Ollama and models
        test_models_endpoint()
        test_ollama_processing()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main() 