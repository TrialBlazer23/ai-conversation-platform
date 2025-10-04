#!/usr/bin/env python3
"""
Test script for the updated Google provider
"""
import os
import sys
sys.path.append('.')

from providers.google_provider import GoogleProvider

def test_google_provider():
    """Test the Google provider with a simple message"""
    
    # Get API key from environment or prompt
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        return
    
    try:
        # Initialize provider
        provider = GoogleProvider(
            api_key=api_key,
            model='gemini-2.5-pro',
            temperature=0.7
        )
        
        # Test messages
        messages = [
            {"role": "user", "content": "Hello! Can you tell me a short joke?"}
        ]
        
        print("Testing Google Provider with new API format...")
        print(f"Model: {provider.model}")
        print(f"Base URL: {provider.base_url}")
        
        # Test non-streaming response
        print("\n--- Testing non-streaming response ---")
        response = provider.generate_response(messages)
        print(f"Response: {response}")
        
        # Test streaming response
        print("\n--- Testing streaming response ---")
        print("Streaming response: ", end="")
        for chunk in provider.generate_response_stream(messages):
            print(chunk, end="", flush=True)
        print("\n")
        
        print("✅ Google provider test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Google provider: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_google_provider()