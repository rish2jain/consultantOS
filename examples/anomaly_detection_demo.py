"""
Anomaly Detection Demo

Demonstrates Prophet-based anomaly detection with example data.
"""

import asyncio
from datetime import datetime, timedelta

import numpy as np

from consultantos.monitoring.anomaly_detector import AnomalyDetector


async def demo_basic_anomaly_detection():
    """Demonstrate basic anomaly detection"""
    print("=" * 60)
    print("DEMO 1: Basic Point Anomaly Detection")
    print("=" * 60)

    # Initialize detector
    detector = AnomalyDetector(confidence_mode="balanced", enable_seasonality=True)

    # Generate 30 days of normal revenue data
    print("\n1. Generating historical revenue data (30 days)...")
    start_date = datetime.utcnow() - timedelta(days=30)
    np.random.seed(42)

    # Normal revenue around $1M/day with 5% variance
    base_revenue = 1_000_000
    revenues = np.random.normal(loc=base_revenue, scale=base_revenue * 0.05, size=30)
    dates = [start_date + timedelta(days=i) for i in range(30)]
    historical_data = list(zip(dates, revenues))

    print(f"   Average daily revenue: ${np.mean(revenues):,.0f}")
    print(f"   Standard deviation: ${np.std(revenues):,.0f}")

    # Train Prophet model
    print("\n2. Training Prophet model...")
    success = detector.fit_model("daily_revenue", historical_data)
    print(f"   Model trained: {success}")

    # Test normal value (should NOT trigger alert)
    print("\n3. Testing normal value ($1,000,000)...")
    normal_anomaly = detector.detect_anomalies("daily_revenue", 1_000_000)
    if normal_anomaly:
        print(f"   ⚠️  Anomaly detected (unexpected!)")
    else:
        print(f"   ✅ No anomaly (as expected)")

    # Test anomalous value (should trigger alert)
    print("\n4. Testing anomalous value ($1,500,000 - 50% spike)...")
    spike_anomaly = detector.detect_anomalies("daily_revenue", 1_500_000)
    if spike_anomaly:
        print(f"   🚨 ANOMALY DETECTED!")
        print(f"      Type: {spike_anomaly.anomaly_type.value}")
        print(f"      Severity: {spike_anomaly.severity:.1f}/10")
        print(f"      Confidence: {spike_anomaly.confidence:.0%}")
        print(f"      Explanation: {spike_anomaly.explanation}")
        print(f"      Forecast: ${spike_anomaly.forecast_value:,.0f}")
        print(f"      Actual: ${spike_anomaly.actual_value:,.0f}")
        print(f"      Confidence interval: ${spike_anomaly.lower_bound:,.0f} - ${spike_anomaly.upper_bound:,.0f}")
    else:
        print(f"   ⚠️  No anomaly detected (unexpected!)")


async def demo_trend_reversal():
    """Demonstrate trend reversal detection"""
    print("\n" + "=" * 60)
    print("DEMO 2: Trend Reversal Detection")
    print("=" * 60)

    detector = AnomalyDetector(confidence_mode="balanced", enable_seasonality=True)

    # Generate data with trend reversal
    print("\n1. Generating revenue data with trend reversal...")
    start_date = datetime.utcnow() - timedelta(days=30)
    np.random.seed(42)

    # Growing trend for first 20 days
    growing_trend = np.linspace(1_000_000, 1_300_000, 20)
    growing_revenue = growing_trend + np.random.normal(0, 20_000, 20)

    # Declining trend for last 10 days
    declining_trend = np.linspace(1_300_000, 1_100_000, 10)
    declining_revenue = declining_trend + np.random.normal(0, 20_000, 10)

    revenues = list(growing_revenue) + list(declining_revenue)
    dates = [start_date + timedelta(days=i) for i in range(30)]
    series = list(zip(dates, revenues))

    print(f"   Days 1-20: Growing from $1.0M to $1.3M")
    print(f"   Days 21-30: Declining from $1.3M to $1.1M")

    # Train model
    print("\n2. Training Prophet model...")
    detector.fit_model("revenue_trend", series)

    # Analyze trend
    print("\n3. Analyzing trends...")
    analysis = detector.trend_analysis("revenue_trend", recent_window_days=7)

    if analysis:
        print(f"   Historical trend: {analysis.historical_trend}")
        print(f"   Current trend: {analysis.current_trend}")
        print(f"   Trend strength: {analysis.trend_strength:.0%}")
        print(f"   Reversal detected: {analysis.reversal_detected}")
        if analysis.reversal_detected:
            print(f"   🔄 TREND REVERSAL DETECTED!")
            print(f"      Confidence: {analysis.reversal_confidence:.0%}")


async def demo_volatility_spike():
    """Demonstrate volatility spike detection"""
    print("\n" + "=" * 60)
    print("DEMO 3: Volatility Spike Detection")
    print("=" * 60)

    detector = AnomalyDetector(confidence_mode="balanced", enable_seasonality=True)

    print("\n1. Generating revenue data with volatility change...")
    np.random.seed(42)

    # Historical: stable revenue ($1M ± 5%)
    historical_revenue = np.random.normal(1_000_000, 50_000, 30)

    # Recent: volatile revenue ($1M ± 15%)
    recent_revenue = np.random.normal(1_000_000, 150_000, 7)

    print(f"   Historical volatility: ±${np.std(historical_revenue):,.0f}")
    print(f"   Recent volatility: ±${np.std(recent_revenue):,.0f}")

    # Detect volatility spike
    print("\n2. Detecting volatility spike...")
    spike = detector.detect_volatility_spike(
        metric_name="daily_revenue",
        recent_values=list(recent_revenue),
        historical_values=list(historical_revenue),
    )

    if spike:
        print(f"   📊 VOLATILITY SPIKE DETECTED!")
        print(f"      Severity: {spike.severity:.1f}/10")
        print(f"      Confidence: {spike.confidence:.0%}")
        print(f"      Explanation: {spike.explanation}")
    else:
        print(f"   ✅ No volatility spike detected")


async def demo_forecast_visualization():
    """Demonstrate forecast generation"""
    print("\n" + "=" * 60)
    print("DEMO 4: Forecast Generation")
    print("=" * 60)

    detector = AnomalyDetector(confidence_mode="balanced", enable_seasonality=True)

    # Generate growing revenue
    print("\n1. Generating 30 days of growing revenue...")
    start_date = datetime.utcnow() - timedelta(days=30)
    np.random.seed(42)

    base_revenue = 1_000_000
    growth_rate = 0.02  # 2% growth per day
    revenues = [
        base_revenue * (1 + growth_rate) ** i + np.random.normal(0, 20_000)
        for i in range(30)
    ]
    dates = [start_date + timedelta(days=i) for i in range(30)]
    series = list(zip(dates, revenues))

    print(f"   Starting revenue: ${revenues[0]:,.0f}")
    print(f"   Ending revenue: ${revenues[-1]:,.0f}")

    # Train model
    print("\n2. Training Prophet model...")
    detector.fit_model("revenue", series)

    # Generate forecast
    print("\n3. Generating 7-day forecast...")
    forecast = detector.get_forecast("revenue", periods=7)

    if forecast is not None:
        # Show last 3 days of history + 7 days forecast
        recent_forecast = forecast.tail(10)
        print("\n   Forecast (last 3 days + next 7 days):")
        print("   " + "-" * 70)
        for _, row in recent_forecast.iterrows():
            date = row['ds'].strftime('%Y-%m-%d')
            yhat = row['yhat']
            lower = row['yhat_lower']
            upper = row['yhat_upper']
            print(f"   {date}: ${yhat:>12,.0f}  (${lower:>12,.0f} - ${upper:>12,.0f})")
        print("   " + "-" * 70)


async def demo_seasonality():
    """Demonstrate seasonality detection"""
    print("\n" + "=" * 60)
    print("DEMO 5: Weekly Seasonality Detection")
    print("=" * 60)

    detector = AnomalyDetector(confidence_mode="balanced", enable_seasonality=True)

    print("\n1. Generating 60 days with weekly pattern...")
    start_date = datetime.utcnow() - timedelta(days=60)
    np.random.seed(42)

    # Weekly pattern: peak on Monday, low on Sunday
    base_revenue = 1_000_000
    revenues = [
        base_revenue + 200_000 * np.sin(2 * np.pi * i / 7) + np.random.normal(0, 30_000)
        for i in range(60)
    ]
    dates = [start_date + timedelta(days=i) for i in range(60)]
    series = list(zip(dates, revenues))

    print(f"   Pattern: Weekly cycle with ±$200K variation")

    # Train model with seasonality
    print("\n2. Training Prophet with weekly seasonality...")
    detector.fit_model("weekly_revenue", series)

    # Test Monday (high) - should NOT be anomaly
    monday_revenue = base_revenue + 200_000
    monday_anomaly = detector.detect_anomalies("weekly_revenue", monday_revenue)

    print("\n3. Testing Monday peak ($1.2M)...")
    if monday_anomaly:
        print(f"   ⚠️  Anomaly detected (unexpected with seasonality)")
    else:
        print(f"   ✅ No anomaly - recognized as normal Monday peak")

    # Test Sunday (low) - should NOT be anomaly
    sunday_revenue = base_revenue - 200_000
    sunday_anomaly = detector.detect_anomalies("weekly_revenue", sunday_revenue)

    print("\n4. Testing Sunday low ($800K)...")
    if sunday_anomaly:
        print(f"   ⚠️  Anomaly detected (unexpected with seasonality)")
    else:
        print(f"   ✅ No anomaly - recognized as normal Sunday dip")


async def demo_performance_benchmark():
    """Benchmark detection performance"""
    print("\n" + "=" * 60)
    print("DEMO 6: Performance Benchmark")
    print("=" * 60)

    detector = AnomalyDetector(confidence_mode="balanced", enable_seasonality=False)

    # Generate data
    print("\n1. Generating test data (30 days)...")
    start_date = datetime.utcnow() - timedelta(days=30)
    np.random.seed(42)
    revenues = np.random.normal(1_000_000, 50_000, 30)
    dates = [start_date + timedelta(days=i) for i in range(30)]
    series = list(zip(dates, revenues))

    # Train model
    print("2. Training model...")
    import time
    train_start = time.time()
    detector.fit_model("revenue", series)
    train_time = (time.time() - train_start) * 1000

    print(f"   Training time: {train_time:.0f}ms")

    # Benchmark detection
    print("\n3. Running detection benchmark (100 iterations)...")
    detect_start = time.time()
    for _ in range(100):
        detector.detect_anomalies("revenue", 1_000_000)
    detect_time = (time.time() - detect_start) * 1000 / 100

    print(f"   Average detection time: {detect_time:.1f}ms")
    print(f"   Target: <500ms")
    print(f"   Result: {'✅ PASS' if detect_time < 500 else '❌ FAIL'}")


async def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("PROPHET ANOMALY DETECTION DEMO")
    print("=" * 60)

    await demo_basic_anomaly_detection()
    await demo_trend_reversal()
    await demo_volatility_spike()
    await demo_forecast_visualization()
    await demo_seasonality()
    await demo_performance_benchmark()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
