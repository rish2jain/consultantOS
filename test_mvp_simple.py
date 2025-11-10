#!/usr/bin/env python
"""
Simple MVP testing script
Tests agents directly without full server startup
"""
import asyncio
import sys
from datetime import datetime


async def test_conversational_agent():
    """Test conversational agent"""
    print("\n" + "=" * 60)
    print("TESTING CONVERSATIONAL AGENT")
    print("=" * 60)

    try:
        from consultantos.agents.conversational_agent_mvp import ConversationalAgentMVP

        agent = ConversationalAgentMVP(timeout=30)
        print("✓ Agent initialized successfully")

        # Test 1: Basic query
        print("\nTest 1: Basic query...")
        result = await agent.execute({
            "query": "What is competitive strategy?",
            "conversation_id": "test_conv_1"
        })

        if result["success"]:
            print(f"✓ Query successful")
            print(f"  Response: {result['data']['response'][:100]}...")
            print(f"  Conversation ID: {result['data']['conversation_id']}")
        else:
            print(f"✗ Query failed: {result['error']}")
            return False

        # Test 2: Follow-up query
        print("\nTest 2: Follow-up query with conversation context...")
        result2 = await agent.execute({
            "query": "Can you give me an example?",
            "conversation_id": "test_conv_1"
        })

        if result2["success"]:
            print(f"✓ Follow-up successful")
            print(f"  Response: {result2['data']['response'][:100]}...")
        else:
            print(f"✗ Follow-up failed: {result2['error']}")
            return False

        print("\n✓ Conversational Agent: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Conversational Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_forecasting_agent():
    """Test forecasting agent"""
    print("\n" + "=" * 60)
    print("TESTING FORECASTING AGENT")
    print("=" * 60)

    try:
        from consultantos.agents.forecasting_agent_mvp import ForecastingAgentMVP

        agent = ForecastingAgentMVP(timeout=30)
        print("✓ Agent initialized successfully")

        # Test 1: Default forecast
        print("\nTest 1: Default 30-day forecast...")
        result = await agent.execute({
            "metric_name": "Revenue",
            "periods": 30
        })

        if result["success"]:
            data = result["data"]
            print(f"✓ Forecast successful")
            print(f"  Metric: {data['metric_name']}")
            print(f"  Predictions: {len(data['predictions'])} days")
            print(f"  Confidence: {data['confidence_level']}")

            # Show first prediction
            first = data['predictions'][0]
            print(f"\n  First prediction:")
            print(f"    Date: {first['date']}")
            print(f"    Value: ${first['value']:,.2f}")
            print(f"    Range: ${first['lower_bound']:,.2f} - ${first['upper_bound']:,.2f}")
        else:
            print(f"✗ Forecast failed: {result['error']}")
            return False

        # Test 2: Custom 7-day forecast
        print("\nTest 2: Custom 7-day forecast...")
        result2 = await agent.execute({
            "metric_name": "Sales",
            "periods": 7
        })

        if result2["success"]:
            data2 = result2["data"]
            print(f"✓ Custom forecast successful")
            print(f"  Metric: {data2['metric_name']}")
            print(f"  Predictions: {len(data2['predictions'])} days")
        else:
            print(f"✗ Custom forecast failed: {result2['error']}")
            return False

        print("\n✓ Forecasting Agent: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Forecasting Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_models():
    """Test model validation"""
    print("\n" + "=" * 60)
    print("TESTING PYDANTIC MODELS")
    print("=" * 60)

    try:
        from consultantos.models.mvp import (
            ChatRequest, ChatResponse,
            ForecastPrediction, ForecastResult
        )

        # Test ChatRequest
        chat_req = ChatRequest(
            query="Test query",
            conversation_id="test_123"
        )
        print("✓ ChatRequest model works")

        # Test ChatResponse
        chat_resp = ChatResponse(
            response="Test response",
            conversation_id="test_123",
            timestamp=datetime.now()
        )
        print("✓ ChatResponse model works")

        # Test ForecastPrediction
        pred = ForecastPrediction(
            date="2025-12-01",
            value=100000.0,
            lower_bound=95000.0,
            upper_bound=105000.0
        )
        print("✓ ForecastPrediction model works")

        # Test ForecastResult
        result = ForecastResult(
            metric_name="Revenue",
            predictions=[pred],
            confidence_level=0.95,
            generated_at=datetime.now()
        )
        print("✓ ForecastResult model works")

        print("\n✓ Pydantic Models: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Model Validation Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MVP BACKEND TESTING SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")

    results = []

    # Test models first
    results.append(("Models", await test_models()))

    # Test agents
    results.append(("Conversational Agent", await test_conversational_agent()))
    results.append(("Forecasting Agent", await test_forecasting_agent()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - MVP READY FOR DEMO")
    else:
        print("✗ SOME TESTS FAILED - REVIEW ERRORS ABOVE")
    print("=" * 60)
    print(f"Completed at: {datetime.now().isoformat()}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
