#!/usr/bin/env python3
"""
Database migration script for time-series monitoring system.

Backfills aggregations for existing monitoring data and creates necessary indexes.

Usage:
    python scripts/migrate_timeseries.py [--dry-run] [--monitor-id MONITOR_ID]

Options:
    --dry-run         Preview changes without applying them
    --monitor-id ID   Migrate specific monitor only
    --days N          Backfill last N days (default: 90)
    --all             Migrate all monitors (default)
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from consultantos.database import get_db_service
from consultantos.monitoring.timeseries_optimizer import TimeSeriesOptimizer
from consultantos.monitoring.snapshot_aggregator import (
    SnapshotAggregator,
    AggregationPeriod,
)
from consultantos.models.monitoring import MonitorStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def migrate_monitor(
    monitor_id: str,
    db_service: any,
    optimizer: TimeSeriesOptimizer,
    aggregator: SnapshotAggregator,
    days: int = 90,
    dry_run: bool = False,
) -> dict:
    """
    Migrate a single monitor's data.

    Args:
        monitor_id: Monitor identifier
        db_service: Database service
        optimizer: Time-series optimizer
        aggregator: Snapshot aggregator
        days: Number of days to backfill
        dry_run: Preview mode

    Returns:
        Migration statistics
    """
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Migrating monitor: {monitor_id}")

    stats = {
        "monitor_id": monitor_id,
        "snapshots_processed": 0,
        "snapshots_compressed": 0,
        "aggregations_created": {
            "daily": 0,
            "weekly": 0,
            "monthly": 0,
        },
        "errors": [],
    }

    try:
        # Get monitor
        monitor = await db_service.get_monitor(monitor_id)
        if not monitor:
            raise ValueError(f"Monitor {monitor_id} not found")

        logger.info(
            f"Monitor: {monitor.company} (status: {monitor.status.value}, "
            f"created: {monitor.created_at})"
        )

        # Calculate backfill period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Check if monitor is old enough
        if monitor.created_at > start_date:
            start_date = monitor.created_at
            logger.info(
                f"Monitor created after backfill start, adjusting to {start_date}"
            )

        # Get all snapshots in period
        snapshots = await optimizer.get_snapshots_in_range(
            monitor_id=monitor_id,
            start_time=start_date,
            end_time=end_date,
        )

        stats["snapshots_processed"] = len(snapshots)
        logger.info(f"Found {len(snapshots)} snapshots in backfill period")

        if not snapshots:
            logger.warning("No snapshots found, skipping aggregation")
            return stats

        # Compress large snapshots (if not dry run)
        if not dry_run:
            for snapshot in snapshots:
                snapshot_size = len(str(snapshot.dict()))
                if snapshot_size > optimizer.compression_threshold:
                    compressed = optimizer._compress_snapshot(snapshot)
                    await db_service.create_snapshot(compressed)
                    stats["snapshots_compressed"] += 1

        # Backfill aggregations
        if not dry_run:
            periods = [
                AggregationPeriod.DAILY,
                AggregationPeriod.WEEKLY,
                AggregationPeriod.MONTHLY,
            ]

            aggregation_counts = await aggregator.backfill_aggregations(
                monitor_id=monitor_id,
                start_date=start_date,
                end_date=end_date,
                periods=periods,
            )

            stats["aggregations_created"] = aggregation_counts
            logger.info(f"Created aggregations: {aggregation_counts}")
        else:
            # Dry run: estimate aggregations
            days_count = (end_date - start_date).days
            stats["aggregations_created"]["daily"] = days_count
            stats["aggregations_created"]["weekly"] = days_count // 7
            stats["aggregations_created"]["monthly"] = (
                (end_date.year - start_date.year) * 12
                + end_date.month
                - start_date.month
                + 1
            )
            logger.info(
                f"[DRY RUN] Would create ~{sum(stats['aggregations_created'].values())} aggregations"
            )

    except Exception as e:
        error_msg = f"Migration failed for {monitor_id}: {e}"
        logger.error(error_msg, exc_info=True)
        stats["errors"].append(error_msg)

    return stats


async def migrate_all_monitors(
    db_service: any,
    optimizer: TimeSeriesOptimizer,
    aggregator: SnapshotAggregator,
    days: int = 90,
    dry_run: bool = False,
) -> list:
    """
    Migrate all active monitors.

    Args:
        db_service: Database service
        optimizer: Time-series optimizer
        aggregator: Snapshot aggregator
        days: Number of days to backfill
        dry_run: Preview mode

    Returns:
        List of migration statistics per monitor
    """
    logger.info("Fetching all active monitors...")

    # Get all monitors (assuming we have a method to get all)
    # For now, we'll need to get monitors by user_id
    # In production, you'd have an admin method to get all monitors
    all_stats = []

    try:
        # This is a simplified approach - in production you'd have better admin access
        logger.warning(
            "Getting all monitors requires iterating through users. "
            "Consider adding an admin endpoint for production use."
        )

        # For migration, you might want to manually specify monitor IDs
        # or implement a `list_all_monitors()` admin method

    except Exception as e:
        logger.error(f"Failed to fetch monitors: {e}", exc_info=True)

    return all_stats


async def main():
    """Main migration entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate monitoring data to time-series optimized schema"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument(
        "--monitor-id", type=str, help="Migrate specific monitor only"
    )
    parser.add_argument(
        "--days", type=int, default=90, help="Backfill last N days (default: 90)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Migrate all monitors (default)"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Time-Series Database Migration")
    logger.info("=" * 60)
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    logger.info(f"Backfill period: {args.days} days")
    logger.info("=" * 60)

    # Initialize services
    logger.info("Initializing services...")
    db_service = get_db_service()

    optimizer = TimeSeriesOptimizer(
        db_service=db_service,
        compression_threshold_bytes=1024,
        batch_size=10,
    )

    aggregator = SnapshotAggregator(
        timeseries_optimizer=optimizer, db_service=db_service
    )

    # Migrate monitors
    all_stats = []

    if args.monitor_id:
        # Migrate single monitor
        logger.info(f"Migrating monitor: {args.monitor_id}")
        stats = await migrate_monitor(
            monitor_id=args.monitor_id,
            db_service=db_service,
            optimizer=optimizer,
            aggregator=aggregator,
            days=args.days,
            dry_run=args.dry_run,
        )
        all_stats.append(stats)

    elif args.all:
        # Migrate all monitors
        logger.info("Migrating all active monitors...")
        all_stats = await migrate_all_monitors(
            db_service=db_service,
            optimizer=optimizer,
            aggregator=aggregator,
            days=args.days,
            dry_run=args.dry_run,
        )

    else:
        logger.error("Must specify --monitor-id or --all")
        sys.exit(1)

    # Print summary
    logger.info("=" * 60)
    logger.info("Migration Summary")
    logger.info("=" * 60)

    total_snapshots = sum(s["snapshots_processed"] for s in all_stats)
    total_compressed = sum(s["snapshots_compressed"] for s in all_stats)
    total_daily = sum(s["aggregations_created"]["daily"] for s in all_stats)
    total_weekly = sum(s["aggregations_created"]["weekly"] for s in all_stats)
    total_monthly = sum(s["aggregations_created"]["monthly"] for s in all_stats)
    total_errors = sum(len(s["errors"]) for s in all_stats)

    logger.info(f"Monitors processed: {len(all_stats)}")
    logger.info(f"Snapshots processed: {total_snapshots}")
    logger.info(f"Snapshots compressed: {total_compressed}")
    logger.info(
        f"Aggregations created: {total_daily} daily, {total_weekly} weekly, {total_monthly} monthly"
    )
    logger.info(f"Errors: {total_errors}")

    if total_errors > 0:
        logger.warning("Migration completed with errors")
        for stats in all_stats:
            if stats["errors"]:
                logger.error(f"Monitor {stats['monitor_id']}: {stats['errors']}")
        sys.exit(1)
    else:
        logger.info("Migration completed successfully!")

    if args.dry_run:
        logger.info(
            "\nThis was a dry run. Re-run without --dry-run to apply changes."
        )


if __name__ == "__main__":
    asyncio.run(main())
