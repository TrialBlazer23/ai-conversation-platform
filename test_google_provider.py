#!/usr/bin/env python3
"""
Test script for the updated Google provider
Tests both streaming and non-streaming responses
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
        print("Example: export GOOGLE_API_KEY='your-api-key-here'")
        print("\nYou can get an API key from: https://makersuite.google.com/app/apikey")
        return
    
    try:
        # Initialize provider
        provider = GoogleProvider(
            api_key=api_key,
            model='gemini-1.5-flash',  # Using flash for faster responses
            temperature=0.7
        )
        
        # Test messages
        messages = [
            {"role": "user", "content": "Say 'Hello World' and nothing else."}
        ]
        
        print("Testing Google Provider with Gemini API")
        print("=" * 70)
        print(f"Model: {provider.model}")
        print(f"Base URL: {provider.base_url}")
        print(f"Streaming supported: {provider.supports_streaming}")
        
        # Test non-streaming response
        print("\n--- Testing non-streaming response ---")
        response = provider.generate_response(messages)
        print(f"Response: {response}")
        print(f"Response length: {len(response)} characters")
        
        # Test streaming response
        print("\n--- Testing streaming response ---")
        print("Streaming response: ", end="", flush=True)
        chunks = []
        for chunk in provider.generate_response_stream(messages):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        print()
        
        print(f"\nChunks received: {len(chunks)}")
        print(f"Total characters: {sum(len(c) for c in chunks)}")
        
        # Verify streaming worked
        if len(chunks) > 0:
            print("\n✅ Streaming is working correctly!")
            print(f"   - Received {len(chunks)} chunk(s)")
            print(f"   - Full response assembled successfully")
        else:
            print("\n❌ WARNING: No chunks received from streaming!")
            print("   This indicates the streaming fix may not be working.")
        
        print("\n✅ Google provider test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing Google provider: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check your internet connection")
        print("3. Ensure you have access to Gemini API")
        print("4. Try a different model (e.g., gemini-1.5-flash)")

if __name__ == "__main__":
    test_google_provider()