"""
Test script to verify which Groq model works.
Run this to find a working model before using the app.
"""

import os
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Loaded .env file")
    else:
        print("⚠️  .env file not found in current directory")
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables only")

from groq import Groq

# Get API key
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("❌ GROQ_API_KEY not set")
    print("\nTrying to read from .env file directly...")
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GROQ_API_KEY'):
                    api_key = line.split('=')[1].strip().strip('"').strip("'")
                    print(f"✅ Found API key in .env: {api_key[:10]}...")
                    break
    except:
        pass
    
    if not api_key:
        print("\n❌ Could not find GROQ_API_KEY")
        print("Please set it:")
        print("  Windows: set GROQ_API_KEY=your_key")
        print("  Linux/Mac: export GROQ_API_KEY=your_key")
        exit(1)

print(f"🔑 Using API key: {api_key[:10]}...")

client = Groq(api_key=api_key)

# Models to test (updated for 2024)
models_to_test = [
    "llama-3.3-70b-versatile",  # Newest 70B model
    "llama-3.1-8b-instant",     # Fast 8B model
    "llama3-70b-8192",          # Alternative 70B
    "llama3-8b-8192",           # Alternative 8B
    "mixtral-8x7b-32768",       # Mixtral model
    "gemma2-9b-it",             # Google Gemma
    "llama-3.2-90b-text-preview",  # Preview model
]

print("🔍 Testing Groq models to find one that follows JSON instructions...")
print("=" * 70)

test_prompt = """Return this exact JSON and nothing else:
{
  "test": "success",
  "number": 42
}"""

for model in models_to_test:
    print(f"\n📝 Testing: {model}")
    print("-" * 70)
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond with ONLY JSON."},
                {"role": "user", "content": test_prompt}
            ],
            temperature=0.1,
            max_completion_tokens=100,
        )
        
        response = completion.choices[0].message.content
        print(f"Response (first 150 chars):\n{response[:150]}")
        
        # Check if it's valid JSON
        import json
        try:
            parsed = json.loads(response.strip().replace("```json", "").replace("```", "").strip())
            print(f"✅ SUCCESS - Returns valid JSON!")
            print(f"   Parsed: {parsed}")
            print(f"\n💡 USE THIS MODEL IN YOUR .env:")
            print(f"   GROQ_MODEL={model}")
            break  # Found a working model!
        except json.JSONDecodeError:
            print(f"❌ FAILED - Response is not valid JSON")
            print(f"   Got: {response[:100]}")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        if "model" in str(e).lower():
            print(f"   (Model might not exist)")

print("\n" + "=" * 70)
print("✅ Test complete! Update your .env with the working model above.")