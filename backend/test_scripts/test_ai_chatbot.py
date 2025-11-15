#!/usr/bin/env python3
"""
Test script for AI Chatbot endpoint.

Tests the Gemini 2.5 Pro integration via the /ai/chat endpoint.

Usage:
    python test_scripts/test_ai_chatbot.py
    
    # Test with a specific message
    python test_scripts/test_ai_chatbot.py "What is the best time to plant rice?"
    
    # Test direct module import (bypasses HTTP)
    python test_scripts/test_ai_chatbot.py --direct
"""
import requests
import json
import sys
import os
import argparse
from dotenv import load_dotenv

# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"


def test_ai_chat_via_http(message: str = "Hello, what farming advice can you give me?"):
    """Test the /ai/chat endpoint via HTTP request."""
    endpoint = f"{BASE_URL}/ai/chat"
    
    print("=" * 60)
    print("Testing AI Chatbot Endpoint (HTTP)")
    print("=" * 60)
    print(f"\nEndpoint: {endpoint}")
    print(f"Message: {message}\n")
    
    try:
        payload = {"message": message}
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            
            print("✅ SUCCESS: AI response received")
            print("\n" + "-" * 60)
            print("AI Response:")
            print("-" * 60)
            print(f"\n{reply}\n")
            print("-" * 60)
            
            # Print full JSON response
            print("\n📄 Full Response JSON:")
            print(json.dumps(data, indent=2))
            
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error Text: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server.")
        print(f"   Make sure the backend is running at {BASE_URL}")
        print("   Start it with: uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out (30 seconds)")
        print("   The AI response may be taking too long.")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_chat_direct(message: str = "Hello, what farming advice can you give me?"):
    """Test the AI chatbot by directly importing and calling the module."""
    print("=" * 60)
    print("Testing AI Chatbot (Direct Module Import)")
    print("=" * 60)
    print(f"\nMessage: {message}\n")
    
    try:
        # Import the AI module
        from app.ai import chat, ChatRequest
        
        # Check if API key is configured
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
            print("   Make sure your .env file contains GEMINI_API_KEY")
            return False
        
        print(f"✅ GEMINI_API_KEY found (length: {len(gemini_key)} characters)")
        
        # Create request
        request = ChatRequest(message=message)
        
        print("\n🔄 Calling Gemini API...")
        print("-" * 60)
        
        # Call the chat function
        response = chat(request)
        
        reply = response.reply
        
        print("✅ SUCCESS: AI response received")
        print("\n" + "-" * 60)
        print("AI Response:")
        print("-" * 60)
        print(f"\n{reply}\n")
        print("-" * 60)
        
        return True
    
    except ValueError as e:
        print(f"❌ ERROR: Configuration error - {str(e)}")
        return False
    except ImportError as e:
        print(f"❌ ERROR: Import error - {str(e)}")
        print("   Make sure google-generativeai is installed:")
        print("   pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_messages():
    """Test multiple different messages to verify consistency."""
    print("\n" + "=" * 60)
    print("Testing Multiple Messages")
    print("=" * 60)
    
    test_messages = [
        "What is the best time to plant rice?",
        "How do I control pests in my cotton field?",
        "What crops grow well in dry weather?",
        "Tell me about organic farming",
    ]
    
    results = []
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i}/{len(test_messages)} ---")
        print(f"Message: {message}")
        success = test_ai_chat_via_http(message)
        results.append(success)
        if i < len(test_messages):
            print("\n" + "-" * 60)
    
    print("\n" + "=" * 60)
    print("Multiple Messages Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    for i, (msg, success) in enumerate(zip(test_messages, results), 1):
        status = "✅" if success else "❌"
        print(f"  {status} Test {i}: {msg[:50]}...")
    
    return all(results)


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test AI Chatbot endpoint")
    parser.add_argument(
        "message",
        nargs="?",
        default="Hello, what farming advice can you give me?",
        help="Message to send to the chatbot"
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Test by directly importing the module (bypasses HTTP)"
    )
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Test multiple different messages"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("AI CHATBOT TEST SUITE")
    print("=" * 60)
    print("\nTesting Google Gemini 2.5 Pro Integration")
    print(f"Backend URL: {BASE_URL}")
    
    # Check environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY configured (length: {len(gemini_key)} characters)")
    else:
        print("⚠️  WARNING: GEMINI_API_KEY not found in environment")
        print("   The test may fail if the key is not set in .env file")
    
    print()
    
    success = False
    
    if args.multiple:
        success = test_multiple_messages()
    elif args.direct:
        success = test_ai_chat_direct(args.message)
    else:
        success = test_ai_chat_via_http(args.message)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
        print("\nTroubleshooting:")
        print("1. Make sure GEMINI_API_KEY is set in your .env file")
        print("2. Make sure google-generativeai is installed: pip install google-generativeai")
        print("3. Make sure the backend server is running: uvicorn app.main:app --reload")
        print("4. Check backend logs for detailed error messages")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


