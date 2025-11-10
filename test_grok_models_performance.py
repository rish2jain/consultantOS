"""
Test script to compare performance of different Grok models
"""
import os
import time
import json
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

# Models to test (in order of expected speed)
models_to_test = [
    "grok-3-fast",
    "grok-3-mini",
    "grok-3",
    "grok-2",
    "grok-4-all",
    "grok-4-beta",
    "grok-4-mini-beta"
]

def test_model_performance(model_name: str) -> dict:
    """Test a single model's performance"""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"{'='*60}")
    
    prompt = "Analyze sentiment on X (Twitter) for 'Tesla' over the last 7 days. Provide a brief summary with overall sentiment score (-1 to 1)."
    
    try:
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        elapsed = time.time() - start_time
        content = response.choices[0].message.content
        
        # Get token usage if available
        tokens_used = None
        if hasattr(response, 'usage') and response.usage:
            tokens_used = response.usage.total_tokens
        
        print(f"✅ Success!")
        print(f"   Response time: {elapsed:.2f} seconds")
        print(f"   Tokens used: {tokens_used or 'N/A'}")
        print(f"   Response length: {len(content)} characters")
        print(f"   Preview: {content[:150]}...")
        
        return {
            "model": model_name,
            "success": True,
            "response_time": elapsed,
            "tokens_used": tokens_used,
            "response_length": len(content),
            "error": None
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed: {error_msg[:100]}")
        
        return {
            "model": model_name,
            "success": False,
            "response_time": None,
            "tokens_used": None,
            "response_length": None,
            "error": error_msg
        }

def main():
    print("\n" + "="*60)
    print("GROK MODELS PERFORMANCE COMPARISON")
    print("="*60)
    
    results = []
    
    for model_name in models_to_test:
        result = test_model_performance(model_name)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        print(f"\n✅ Available Models ({len(successful)}):")
        # Sort by response time
        successful.sort(key=lambda x: x["response_time"] or float('inf'))
        
        for result in successful:
            print(f"\n  {result['model']}:")
            print(f"    ⏱️  Response time: {result['response_time']:.2f}s")
            print(f"    💰 Tokens: {result['tokens_used'] or 'N/A'}")
        
        # Find fastest
        fastest = successful[0]
        print(f"\n🏆 Fastest Model: {fastest['model']} ({fastest['response_time']:.2f}s)")
        
        # Find most capable (slowest = most comprehensive)
        slowest = successful[-1]
        print(f"🧠 Most Comprehensive: {slowest['model']} ({slowest['response_time']:.2f}s)")
        
        # Recommendation
        print(f"\n💡 Recommendation:")
        if fastest['response_time'] < 5:
            print(f"   For real-time: Use {fastest['model']} ({fastest['response_time']:.2f}s)")
        if len(successful) > 1:
            print(f"   For comprehensive analysis: Use {slowest['model']} ({slowest['response_time']:.2f}s)")
    
    if failed:
        print(f"\n❌ Unavailable Models ({len(failed)}):")
        for result in failed:
            error_short = result['error'][:50] if result['error'] else "Unknown error"
            print(f"  - {result['model']}: {error_short}")

if __name__ == "__main__":
    main()

