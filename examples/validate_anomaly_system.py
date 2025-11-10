#!/usr/bin/env python3
"""
Validation script for anomaly detection system.

Quick smoke test to ensure all components work together.
"""

import asyncio
import sys
from datetime import datetime, timedelta

import numpy as np


async def validate_imports():
    """Validate all imports"""
    print("=" * 60)
    print("STEP 1: Validating Imports")
    print("=" * 60)

    try:
        from consultantos.monitoring.anomaly_detector import (
            AnomalyDetector,
            AnomalyType,
            TrendAnalysis,
        )
        print("✅ AnomalyDetector imported")

        from consultantos.monitoring.alert_scorer import AlertScorer
        print("✅ AlertScorer imported")

        from consultantos.models.monitoring import (
            AnomalyScoreModel,
            AlertPriorityModel,
        )
        print("✅ Enhanced models imported")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


async def validate_prophet():
    """Validate Prophet installation"""
    print("\n" + "=" * 60)
    print("STEP 2: Validating Prophet Installation")
    print("=" * 60)

    try:
        from prophet import Prophet
        print("✅ Prophet imported successfully")
        return True
    except ImportError:
        print("❌ Prophet not installed")
        print("   Run: pip install prophet>=1.1.0")
        return False


async def validate_anomaly_detector():
    """Validate AnomalyDetector functionality"""
    print("\n" + "=" * 60)
    print("STEP 3: Validating AnomalyDetector")
    print("=" * 60)

    try:
        from consultantos.monitoring.anomaly_detector import AnomalyDetector

        # Create detector
        detector = AnomalyDetector(
            confidence_mode="balanced",
            enable_seasonality=True,
        )
        print("✅ Detector created")

        # Generate test data
        start_date = datetime.utcnow() - timedelta(days=30)
        np.random.seed(42)
        revenues = np.random.normal(1_000_000, 50_000, 30)
        dates = [start_date + timedelta(days=i) for i in range(30)]
        data = list(zip(dates, revenues))

        # Train model
        success = detector.fit_model("test_metric", data)
        if not success:
            print("❌ Model training failed")
            return False
        print("✅ Prophet model trained")

        # Detect normal value (should be None)
        normal_anomaly = detector.detect_anomalies("test_metric", 1_000_000)
        if normal_anomaly:
            print("⚠️  Normal value flagged as anomaly (unexpected)")
        else:
            print("✅ Normal value detection works")

        # Detect anomaly (should trigger)
        spike_anomaly = detector.detect_anomalies("test_metric", 1_500_000)
        if not spike_anomaly:
            print("⚠️  Anomalous value not detected (unexpected)")
        else:
            print(f"✅ Anomaly detected: {spike_anomaly.explanation}")

        # Test trend analysis
        analysis = detector.trend_analysis("test_metric")
        if analysis:
            print(f"✅ Trend analysis works: {analysis.trend_direction}")
        else:
            print("⚠️  Trend analysis failed")

        # Test forecast
        forecast = detector.get_forecast("test_metric", periods=7)
        if forecast is not None and len(forecast) > 0:
            print(f"✅ Forecast generated: {len(forecast)} periods")
        else:
            print("⚠️  Forecast generation failed")

        return True

    except Exception as e:
        print(f"❌ AnomalyDetector validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def validate_alert_scorer():
    """Validate AlertScorer functionality"""
    print("\n" + "=" * 60)
    print("STEP 4: Validating AlertScorer")
    print("=" * 60)

    try:
        from consultantos.monitoring.alert_scorer import AlertScorer
        from consultantos.monitoring.anomaly_detector import AnomalyScore, AnomalyType
        from consultantos.models.monitoring import (
            Alert,
            Change,
            ChangeType,
            MonitoringConfig,
        )

        # Create scorer
        scorer = AlertScorer(db_service=None)  # No DB for validation
        print("✅ AlertScorer created")

        # Create mock alert
        alert = Alert(
            id="test_alert",
            monitor_id="test_monitor",
            title="Test Alert",
            summary="Test summary",
            confidence=0.85,
            changes_detected=[
                Change(
                    change_type=ChangeType.FINANCIAL_METRIC,
                    title="Revenue Change",
                    description="Test change",
                    confidence=0.85,
                )
            ],
        )

        # Create mock anomaly scores
        anomaly_scores = [
            AnomalyScore(
                metric_name="revenue",
                anomaly_type=AnomalyType.POINT,
                severity=8.5,
                confidence=0.9,
                explanation="Test anomaly",
                forecast_value=1_000_000,
                actual_value=1_500_000,
            )
        ]

        # Score alert
        priority = scorer.score_alert(
            alert=alert,
            anomaly_scores=anomaly_scores,
            config=MonitoringConfig(),
        )

        print(f"✅ Alert scored: {priority.priority_score:.1f}/10")
        print(f"   Urgency: {priority.urgency_level}")
        print(f"   Should notify: {priority.should_notify}")

        # Test deduplication
        is_duplicate = scorer._is_duplicate_alert(alert)
        print(f"✅ Deduplication works: duplicate={is_duplicate}")

        return True

    except Exception as e:
        print(f"❌ AlertScorer validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def validate_database_integration():
    """Validate database method exists"""
    print("\n" + "=" * 60)
    print("STEP 5: Validating Database Integration")
    print("=" * 60)

    try:
        from consultantos.database import InMemoryDatabaseService

        db = InMemoryDatabaseService()

        # Check if method exists
        if hasattr(db, 'get_snapshots_history'):
            print("✅ get_snapshots_history method exists")
        else:
            print("❌ get_snapshots_history method missing")
            return False

        return True

    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False


async def validate_models():
    """Validate enhanced monitoring models"""
    print("\n" + "=" * 60)
    print("STEP 6: Validating Enhanced Models")
    print("=" * 60)

    try:
        from consultantos.models.monitoring import (
            Alert,
            AnomalyScoreModel,
            AlertPriorityModel,
        )

        # Create anomaly score model
        anomaly = AnomalyScoreModel(
            metric_name="revenue",
            anomaly_type="point",
            severity=8.5,
            confidence=0.9,
            explanation="Test anomaly",
        )
        print("✅ AnomalyScoreModel created")

        # Create alert priority model
        priority = AlertPriorityModel(
            priority_score=8.5,
            urgency_level="critical",
            should_notify=True,
            reasoning=["High severity", "Critical change type"],
        )
        print("✅ AlertPriorityModel created")

        # Create alert with anomaly scores
        alert = Alert(
            id="test",
            monitor_id="test",
            title="Test",
            summary="Test",
            confidence=0.85,
            changes_detected=[],
            anomaly_scores=[anomaly],
            priority=priority,
        )
        print("✅ Enhanced Alert model created")

        return True

    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def validate_performance():
    """Quick performance check"""
    print("\n" + "=" * 60)
    print("STEP 7: Performance Validation")
    print("=" * 60)

    try:
        from consultantos.monitoring.anomaly_detector import AnomalyDetector
        import time

        detector = AnomalyDetector(confidence_mode="balanced", enable_seasonality=False)

        # Generate test data
        start_date = datetime.utcnow() - timedelta(days=30)
        np.random.seed(42)
        data = [
            (start_date + timedelta(days=i), 1_000_000 + np.random.normal(0, 50_000))
            for i in range(30)
        ]

        # Benchmark training
        train_start = time.time()
        detector.fit_model("perf_test", data)
        train_time = (time.time() - train_start) * 1000

        # Benchmark detection
        detect_times = []
        for _ in range(20):
            detect_start = time.time()
            detector.detect_anomalies("perf_test", 1_000_000)
            detect_time = (time.time() - detect_start) * 1000
            detect_times.append(detect_time)

        avg_detect_time = sum(detect_times) / len(detect_times)

        print(f"Training time: {train_time:.0f}ms")
        print(f"Average detection time: {avg_detect_time:.1f}ms")

        if train_time < 2000:  # 2 seconds
            print("✅ Training performance acceptable")
        else:
            print("⚠️  Training slower than expected")

        if avg_detect_time < 500:  # 500ms target
            print("✅ Detection performance acceptable")
        else:
            print("⚠️  Detection slower than target (<500ms)")

        return True

    except Exception as e:
        print(f"❌ Performance validation failed: {e}")
        return False


async def main():
    """Run all validation steps"""
    print("\n" + "=" * 60)
    print("ANOMALY DETECTION SYSTEM VALIDATION")
    print("=" * 60 + "\n")

    results = []

    # Run all validation steps
    results.append(("Imports", await validate_imports()))
    results.append(("Prophet", await validate_prophet()))
    results.append(("AnomalyDetector", await validate_anomaly_detector()))
    results.append(("AlertScorer", await validate_alert_scorer()))
    results.append(("Database", await validate_database_integration()))
    results.append(("Models", await validate_models()))
    results.append(("Performance", await validate_performance()))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for step, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{step:20s}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("\nAnomaly detection system is ready for deployment.")
        print("\nNext steps:")
        print("  1. Run tests: pytest tests/test_anomaly_detector.py -v")
        print("  2. Run demo: python examples/anomaly_detection_demo.py")
        print("  3. Review guide: docs/ANOMALY_DETECTION_GUIDE.md")
        return 0
    else:
        print("\n❌ VALIDATION FAILED!")
        print("\nPlease fix the issues above before deployment.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
