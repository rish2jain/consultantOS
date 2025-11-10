"""
Test script to list available models from laozhang.ai
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("LAOZHANG_API_KEY")
if not api_key:
    print("❌ ERROR: LAOZHANG_API_KEY not found")
    exit(1)

client = OpenAI(
    base_url="https://api.laozhang.ai/v1",
    api_key=api_key
)

print("Attempting to list available models...\n")

try:
    # Try to list models
    models = client.models.list()
    print("✅ Successfully retrieved models list!")
    print(f"\nAvailable models:\n")
    # Check the structure
    if hasattr(models, 'data'):
        model_list = []
        for model in models.data:
            if hasattr(model, 'id'):
                model_list.append(model.id)
            elif isinstance(model, str):
                model_list.append(model)
            else:
                model_list.append(str(model))
        # If it's a list of characters, join them
        if len(model_list) > 0 and all(len(m) == 1 for m in model_list):
            full_name = ''.join(model_list)
            print(f"  - {full_name}")
        else:
            for model_name in model_list:
                print(f"  - {model_name}")
    else:
        print(f"  Response: {models}")
except Exception as e:
    print(f"❌ Could not list models: {e}")
    print("\nTrying alternative approach: testing common model names...\n")
    
    # Try some alternative model names
    test_models = [
        "grok",
        "grok-1",
        "grok-1.5",
        "grok-2.0",
        "grok-2.5",
        "grok-3.0",
        "grok-4.0",
        "x-grok",
        "xai-grok",
        "grok-beta",
        "grok-pro",
        "grok-ultra"
    ]
    
    for model_name in test_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            print(f"✅ Model '{model_name}' is available!")
            break
        except Exception as e:
            error_msg = str(e)
            if "403" not in error_msg and "无权" not in error_msg:
                # Different error - might be available but with different issue
                print(f"  ⚠️  Model '{model_name}': {error_msg[:100]}")
            continue

