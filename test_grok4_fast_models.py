"""
Test the grok-4-fast variants that appeared in the models list
"""
import os
import time
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

# Test the fast variants that appeared in the list
models_to_test = [
    "grok-4-fast",
    "grok-4-fast-reasoning",
    "grok-4-fast-reasoning-latest",
    "grok-4-fast-non-reasoning",
    "grok-4-fast-non-reasoning-latest",
    "grok-4-latest",
    "grok-4",
    "grok-4-0709",
    "grok-4-all"  # Baseline
]

def test_model(model_name: str):
    """Test a single model"""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"{'='*60}")
    
    prompt = "Analyze sentiment on X (Twitter) for 'Apple' over the last 7 days. Provide overall sentiment score (-1 to 1) and brief summary."
    
    try:
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        elapsed = time.time() - start_time
        content = response.choices[0].message.content
        
        tokens_used = None
        if hasattr(response, 'usage') and response.usage:
            tokens_used = response.usage.total_tokens
        
        print(f"✅ Success!")
        print(f"   ⏱️  Response time: {elapsed:.2f} seconds")
        print(f"   💰 Tokens: {tokens_used or 'N/A'}")
        print(f"   📝 Preview: {content[:200]}...")
        
        return {
            "model": model_name,
            "success": True,
            "response_time": elapsed,
            "tokens_used": tokens_used
        }
        
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "无权" in error_msg:
            print(f"⚠️  Not available (permission denied)")
        else:
            print(f"❌ Error: {error_msg[:100]}")
        
        return {
            "model": model_name,
            "success": False,
            "response_time": None,
            "tokens_used": None
        }

def main():
    print("\n" + "="*60)
    print("TESTING GROK-4-FAST VARIANTS")
    print("="*60)
    
    results = []
    
    for model_name in models_to_test:
        result = test_model(model_name)
        results.append(result)
        time.sleep(1)  # Rate limit protection
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        print(f"\n✅ Available Models ({len(successful)}):")
        successful.sort(key=lambda x: x["response_time"] or float('inf'))
        
        for result in successful:
            print(f"  • {result['model']:40s} {result['response_time']:6.2f}s  ({result['tokens_used'] or 'N/A'} tokens)")
        
        fastest = successful[0]
        print(f"\n🏆 Fastest: {fastest['model']} ({fastest['response_time']:.2f}s)")
        print(f"💡 Recommended for real-time: {fastest['model']}")
    
    if failed:
        print(f"\n❌ Unavailable ({len(failed)} models)")

if __name__ == "__main__":
    main()

