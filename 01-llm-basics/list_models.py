from google import genai
import os
from dotenv import load_dotenv

# Load .env file from parent directory
load_dotenv(dotenv_path='../.env')

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

print("=" * 70)
print("Available Gemini Models".center(70))
print("=" * 70)

try:
    # List all available models
    models = client.models.list()
    
    print("\n📋 Available Models:\n")
    for model in models:
        print(f"✓ {model.name}")
        if hasattr(model, 'display_name'):
            print(f"  Display Name: {model.display_name}")
        if hasattr(model, 'description'):
            print(f"  Description: {model.description}")
        print()
        
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying alternative method...")
    
    # Try to get specific model info
    common_models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-flash"
    ]
    
    print("\nTesting common model names:\n")
    for model_name in common_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hi"
            )
            print(f"✓ {model_name} - WORKS")
        except Exception as e:
            print(f"✗ {model_name} - {str(e)[:50]}...")
