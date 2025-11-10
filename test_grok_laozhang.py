"""
Test script for Grok API via laozhang.ai
Tests sentiment analysis capabilities for social media monitoring
"""
import os
import asyncio
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_grok_basic():
    """Test 1: Basic Grok API connection and simple query"""
    print("\n" + "="*60)
    print("TEST 1: Basic Grok API Connection")
    print("="*60)
    
    api_key = os.getenv("LAOZHANG_API_KEY")
    if not api_key:
        print("❌ ERROR: LAOZHANG_API_KEY not found in environment variables")
        return False
    
    # Try different model names that might be available
    models_to_try = [
        "grok-4-all",  # Found via models.list()
        "grok-2",
        "grok-beta",
        "grok-3",
        "grok-3-fast",
        "grok-3-mini",
        "grok-4-beta",
        "grok-4-mini-beta"
    ]
    
    client = OpenAI(
        base_url="https://api.laozhang.ai/v1",
        api_key=api_key
    )
    
    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name}...")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": "What is the current sentiment about Tesla on X (Twitter) in the last 7 days? Provide a brief summary."}
                ],
                max_tokens=500
            )
            
            print(f"✅ Connection successful with model: {model_name}!")
            print(f"Model: {response.model}")
            print(f"Response:\n{response.choices[0].message.content}")
            return model_name  # Return the working model name
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "无权" in error_msg or "permission" in error_msg.lower():
                print(f"  ⚠️  Model {model_name} not available (permission denied)")
                continue
            else:
                print(f"  ❌ Error with {model_name}: {error_msg}")
                continue
    
    print("❌ None of the tested models are available with this API key")
    return False


def test_grok_sentiment_analysis(working_model=None):
    """Test 2: Structured sentiment analysis query"""
    print("\n" + "="*60)
    print("TEST 2: Structured Sentiment Analysis")
    print("="*60)
    
    api_key = os.getenv("LAOZHANG_API_KEY")
    if not api_key:
        print("❌ ERROR: LAOZHANG_API_KEY not found")
        return False
    
    if not working_model:
        print("⚠️  No working model found from previous test, trying common models...")
        models_to_try = ["grok-4-all", "grok-2", "grok-beta", "grok-3", "grok-3-fast", "grok-3-mini"]
    else:
        models_to_try = [working_model]
    
    client = OpenAI(
        base_url="https://api.laozhang.ai/v1",
        api_key=api_key
    )
    
    prompt = """
    Analyze sentiment on X (Twitter) for "Apple" over the last 7 days.
    Provide a JSON response with:
    {
        "overall_sentiment": float between -1 and 1,
        "sentiment_label": "positive" or "negative" or "neutral",
        "key_themes": ["theme1", "theme2", "theme3"],
        "sample_trending_topics": ["topic1", "topic2"],
        "summary": "brief summary of sentiment"
    }
    """
    
    for model_name in models_to_try:
        try:
            # Try with JSON format first
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=1000
                )
            except:
                # Fallback: try without JSON format requirement
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt + "\n\nPlease format your response as valid JSON."}],
                    max_tokens=1000
                )
            
            print(f"✅ Sentiment analysis successful with {model_name}!")
            content = response.choices[0].message.content
            
            try:
                # Try to parse as JSON
                data = json.loads(content)
                print("\n📊 Parsed Response:")
                print(json.dumps(data, indent=2))
            except:
                print(f"\n📄 Raw Response (not JSON):\n{content}")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "无权" in error_msg:
                print(f"  ⚠️  Model {model_name} not available, trying next...")
                continue
            else:
                print(f"❌ Error with {model_name}: {error_msg}")
                continue
    
    print("❌ Could not find a working model for sentiment analysis")
    return False


def test_grok_company_monitoring(working_model=None):
    """Test 3: Company monitoring query (similar to SocialMediaAgent)"""
    print("\n" + "="*60)
    print("TEST 3: Company Monitoring Query")
    print("="*60)
    
    api_key = os.getenv("LAOZHANG_API_KEY")
    if not api_key:
        print("❌ ERROR: LAOZHANG_API_KEY not found")
        return False
    
    if not working_model:
        models_to_try = ["grok-4-all", "grok-2", "grok-beta", "grok-3", "grok-3-fast", "grok-3-mini"]
    else:
        models_to_try = [working_model]
    
    client = OpenAI(
        base_url="https://api.laozhang.ai/v1",
        api_key=api_key
    )
    
    company = "Microsoft"
    keywords = ["Microsoft", "MSFT", "Azure", "Windows"]
    
    prompt = f"""
    Monitor social media sentiment for {company} on X (Twitter) over the last 7 days.
    Keywords to track: {', '.join(keywords)}
    
    Provide analysis including:
    1. Overall sentiment score (-1 to 1)
    2. Sentiment breakdown (positive %, neutral %, negative %)
    3. Top 5 trending topics/hashtags
    4. Key influencers or accounts discussing this
    5. Any crisis alerts or negative sentiment spikes
    6. Competitor mentions if relevant
    
    Format as JSON with clear structure.
    """
    
    for model_name in models_to_try:
        try:
            # Try with JSON format first
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=1500
                )
            except:
                # Fallback: try without JSON format requirement
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt + "\n\nPlease format your response as valid JSON."}],
                    max_tokens=1500
                )
            
            print(f"✅ Company monitoring for {company} successful with {model_name}!")
            content = response.choices[0].message.content
            
            try:
                data = json.loads(content)
                print("\n📊 Monitoring Results:")
                print(json.dumps(data, indent=2))
            except:
                print(f"\n📄 Raw Response (not JSON):\n{content}")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "无权" in error_msg:
                print(f"  ⚠️  Model {model_name} not available, trying next...")
                continue
            else:
                print(f"❌ Error with {model_name}: {error_msg}")
                continue
    
    print("❌ Could not find a working model for company monitoring")
    return False


def test_grok_performance(working_model=None):
    """Test 4: Performance test - measure response time"""
    print("\n" + "="*60)
    print("TEST 4: Performance Test")
    print("="*60)
    
    api_key = os.getenv("LAOZHANG_API_KEY")
    if not api_key:
        print("❌ ERROR: LAOZHANG_API_KEY not found")
        return False
    
    if not working_model:
        # Try faster/cheaper models first
        models_to_try = ["grok-4-all", "grok-3-mini", "grok-3-fast", "grok-2", "grok-beta", "grok-3"]
    else:
        models_to_try = [working_model]
    
    client = OpenAI(
        base_url="https://api.laozhang.ai/v1",
        api_key=api_key
    )
    
    for model_name in models_to_try:
        try:
            import time
            start_time = time.time()
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": "What's the sentiment about AI companies on X right now? Keep it brief."}
                ],
                max_tokens=300
            )
            
            elapsed = time.time() - start_time
            
            print(f"✅ Response time: {elapsed:.2f} seconds")
            print(f"Model: {response.model}")
            print(f"Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            print(f"Response preview: {response.choices[0].message.content[:200]}...")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "无权" in error_msg:
                print(f"  ⚠️  Model {model_name} not available, trying next...")
                continue
            else:
                print(f"❌ Error with {model_name}: {error_msg}")
                continue
    
    print("❌ Could not find a working model for performance test")
    return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("GROK API VIA LAOZHANG.AI - TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests - find working model first
    working_model = test_grok_basic()
    if working_model and working_model is not True:
        # working_model contains the model name
        print(f"\n✅ Found working model: {working_model}")
        results.append(("Basic Connection", True))
    else:
        results.append(("Basic Connection", False))
        working_model = None
    
    # Use working model for subsequent tests
    results.append(("Sentiment Analysis", test_grok_sentiment_analysis(working_model)))
    results.append(("Company Monitoring", test_grok_company_monitoring(working_model)))
    results.append(("Performance", test_grok_performance(working_model)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Grok API via laozhang.ai is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    main()

