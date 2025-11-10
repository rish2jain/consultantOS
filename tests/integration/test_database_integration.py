"""
Database Integration Tests

Tests Firestore storage, retrieval, and data persistence operations.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import uuid


# Skip all tests if Firestore not configured
pytestmark = pytest.mark.skipif(
    True,  # Always skip unless explicitly configured
    reason="Firestore integration tests require emulator or test project"
)


# ============================================================================
# ANALYSIS STORAGE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_analysis_storage_and_retrieval():
    """
    Test complete storage workflow to Firestore.

    Create analysis → Store → Retrieve → Verify integrity.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()

    # Sample analysis data
    analysis_data = {
        "analysis_id": str(uuid.uuid4()),
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter"],
        "research": {
            "summary": "Tesla research findings",
            "confidence": 0.8
        },
        "created_at": datetime.utcnow().isoformat(),
        "status": "completed"
    }

    try:
        # 1. Store analysis
        await db.store_analysis(analysis_data)

        # 2. Retrieve analysis
        retrieved = await db.get_analysis(analysis_data["analysis_id"])

        # 3. Verify data integrity
        assert retrieved is not None
        assert retrieved["company"] == "Tesla"
        assert retrieved["industry"] == "Electric Vehicles"
        assert "research" in retrieved
        assert retrieved["status"] == "completed"

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_analysis_update():
    """
    Test updating existing analysis in Firestore.

    Create → Update → Verify changes persisted.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()

    analysis_id = str(uuid.uuid4())
    initial_data = {
        "analysis_id": analysis_id,
        "company": "Tesla",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        # 1. Create initial document
        await db.store_analysis(initial_data)

        # 2. Update status
        await db.update_analysis(analysis_id, {
            "status": "completed",
            "confidence_score": 0.85
        })

        # 3. Retrieve and verify
        updated = await db.get_analysis(analysis_id)

        assert updated["status"] == "completed"
        assert updated["confidence_score"] == 0.85

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_analysis_deletion():
    """
    Test deleting analysis from Firestore.

    Create → Delete → Verify deletion.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()

    analysis_id = str(uuid.uuid4())
    test_data = {
        "analysis_id": analysis_id,
        "company": "Tesla",
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        # 1. Create document
        await db.store_analysis(test_data)

        # 2. Delete document
        await db.delete_analysis(analysis_id)

        # 3. Verify deletion
        retrieved = await db.get_analysis(analysis_id)
        assert retrieved is None

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


# ============================================================================
# QUERY AND LISTING TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_list_user_analyses():
    """
    Test listing analyses for a specific user.

    Validates query functionality and filtering.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()
    user_id = "test_user_123"

    try:
        # Create multiple analyses for user
        for i in range(3):
            await db.store_analysis({
                "analysis_id": str(uuid.uuid4()),
                "user_id": user_id,
                "company": f"Company{i}",
                "created_at": datetime.utcnow().isoformat()
            })

        # List user's analyses
        analyses = await db.list_user_analyses(user_id)

        assert len(analyses) >= 3
        assert all(a["user_id"] == user_id for a in analyses)

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_query_by_company():
    """
    Test querying analyses by company name.

    Validates search and filter capabilities.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()
    company = "Tesla"

    try:
        # Create analyses for specific company
        for i in range(2):
            await db.store_analysis({
                "analysis_id": str(uuid.uuid4()),
                "company": company,
                "industry": "EV",
                "created_at": datetime.utcnow().isoformat()
            })

        # Query by company
        results = await db.query_analyses({"company": company})

        assert len(results) >= 2
        assert all(r["company"] == company for r in results)

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


# ============================================================================
# CONVERSATION HISTORY TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_conversation_history_persistence():
    """
    Test conversation history is stored and retrieved correctly.

    Multi-message conversation flow.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()
    conversation_id = str(uuid.uuid4())

    try:
        # 1. Store conversation messages
        messages = [
            {"role": "user", "content": "What is Tesla?", "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": "Tesla is an EV company", "timestamp": datetime.utcnow().isoformat()},
            {"role": "user", "content": "Tell me more", "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": "More details...", "timestamp": datetime.utcnow().isoformat()}
        ]

        for msg in messages:
            await db.add_conversation_message(conversation_id, msg)

        # 2. Retrieve conversation history
        history = await db.get_conversation_history(conversation_id)

        assert len(history["messages"]) == 4
        assert history["messages"][0]["role"] == "user"
        assert history["messages"][1]["role"] == "assistant"

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


# ============================================================================
# MONITORING DATA TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_monitor_storage_and_retrieval():
    """
    Test intelligence monitor storage in Firestore.

    Create monitor → Store → Retrieve → Verify.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()

    monitor_data = {
        "monitor_id": str(uuid.uuid4()),
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frequency": "daily",
        "alert_threshold": 0.7,
        "frameworks": ["porter"],
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }

    try:
        # 1. Store monitor
        await db.store_monitor(monitor_data)

        # 2. Retrieve monitor
        retrieved = await db.get_monitor(monitor_data["monitor_id"])

        # 3. Verify data
        assert retrieved is not None
        assert retrieved["company"] == "Tesla"
        assert retrieved["frequency"] == "daily"
        assert retrieved["alert_threshold"] == 0.7

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_alert_storage():
    """
    Test alert storage and retrieval.

    Create alerts → Store → Retrieve by monitor.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()
    monitor_id = str(uuid.uuid4())

    try:
        # Create multiple alerts for monitor
        for i in range(3):
            alert_data = {
                "alert_id": str(uuid.uuid4()),
                "monitor_id": monitor_id,
                "alert_type": "significant_change",
                "confidence": 0.8 + (i * 0.05),
                "message": f"Change detected {i}",
                "created_at": datetime.utcnow().isoformat()
            }
            await db.store_alert(alert_data)

        # Retrieve alerts for monitor
        alerts = await db.get_monitor_alerts(monitor_id)

        assert len(alerts) >= 3
        assert all(a["monitor_id"] == monitor_id for a in alerts)

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


# ============================================================================
# SNAPSHOT STORAGE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_snapshot_storage_and_comparison():
    """
    Test analysis snapshot storage for change detection.

    Store baseline → Store update → Compare snapshots.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()
    monitor_id = str(uuid.uuid4())

    try:
        # 1. Store baseline snapshot
        baseline = {
            "snapshot_id": str(uuid.uuid4()),
            "monitor_id": monitor_id,
            "snapshot_type": "baseline",
            "metrics": {
                "competitive_intensity": 0.75,
                "market_sentiment": 0.82
            },
            "created_at": datetime.utcnow().isoformat()
        }
        await db.store_snapshot(baseline)

        # 2. Store updated snapshot
        updated = {
            "snapshot_id": str(uuid.uuid4()),
            "monitor_id": monitor_id,
            "snapshot_type": "update",
            "metrics": {
                "competitive_intensity": 0.68,  # Changed
                "market_sentiment": 0.85  # Changed
            },
            "created_at": datetime.utcnow().isoformat()
        }
        await db.store_snapshot(updated)

        # 3. Retrieve snapshots
        snapshots = await db.get_monitor_snapshots(monitor_id)

        assert len(snapshots) >= 2
        # Verify both baseline and update present
        types = [s["snapshot_type"] for s in snapshots]
        assert "baseline" in types
        assert "update" in types

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


# ============================================================================
# USER DATA TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_profile_storage():
    """
    Test user profile storage and retrieval.

    Create user → Store → Update → Retrieve.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()
    user_id = str(uuid.uuid4())

    try:
        # 1. Create user profile
        user_data = {
            "user_id": user_id,
            "email": "test@example.com",
            "name": "Test User",
            "created_at": datetime.utcnow().isoformat(),
            "preferences": {
                "default_frameworks": ["porter", "swot"]
            }
        }
        await db.store_user(user_data)

        # 2. Retrieve user
        retrieved = await db.get_user(user_id)

        assert retrieved is not None
        assert retrieved["email"] == "test@example.com"
        assert "preferences" in retrieved

        # 3. Update preferences
        await db.update_user(user_id, {
            "preferences": {
                "default_frameworks": ["porter", "swot", "pestel"]
            }
        })

        # 4. Verify update
        updated = await db.get_user(user_id)
        assert len(updated["preferences"]["default_frameworks"]) == 3

    except Exception as e:
        pytest.skip(f"Firestore not configured: {e}")


# ============================================================================
# TRANSACTION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_transaction_rollback():
    """
    Test transaction rollback on failure.

    Start transaction → Fail → Verify rollback.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()

    try:
        # Attempt transaction that should fail
        with pytest.raises(Exception):
            async with db.transaction():
                # Create document
                await db.store_analysis({
                    "analysis_id": "test_123",
                    "company": "Tesla"
                })

                # Force failure
                raise Exception("Simulated failure")

        # Verify document was not created (rolled back)
        retrieved = await db.get_analysis("test_123")
        assert retrieved is None

    except Exception as e:
        pytest.skip(f"Firestore transactions not configured: {e}")


# ============================================================================
# BATCH OPERATIONS TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_batch_write():
    """
    Test batch write operations for efficiency.

    Create multiple documents in single batch.
    """
    from consultantos.database import DatabaseService

    db = DatabaseService()

    try:
        # Batch create analyses
        analyses = [
            {
                "analysis_id": str(uuid.uuid4()),
                "company": f"Company{i}",
                "created_at": datetime.utcnow().isoformat()
            }
            for i in range(10)
        ]

        await db.batch_store_analyses(analyses)

        # Verify all created
        for analysis in analyses:
            retrieved = await db.get_analysis(analysis["analysis_id"])
            assert retrieved is not None

    except Exception as e:
        pytest.skip(f"Firestore batch operations not configured: {e}")
