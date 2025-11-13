#!/usr/bin/env python3
"""
Script to delete all failed reports from the database and storage.

This script:
1. Queries Firestore for all reports with status="failed"
2. Deletes each failed report's metadata from the database
3. Deletes associated PDF files from storage (if they exist)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import consultantos modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from consultantos.database import get_db_service, get_db_client
from consultantos.storage import get_storage_service
from consultantos.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def delete_failed_reports(dry_run: bool = False):
    """
    Delete all failed reports from database and storage.
    
    Args:
        dry_run: If True, only show what would be deleted without actually deleting
    """
    try:
        # Get database service
        db_service = get_db_service()
        if db_service is None:
            logger.error("Database service not available")
            return
        
        # Get storage service
        storage_service = get_storage_service()
        
        # Query Firestore directly for failed reports
        db_client = get_db_client()
        if db_client is None:
            logger.error("Firestore client not available")
            return
        
        reports_collection = db_client.collection("reports")
        
        # Query for failed reports
        logger.info("Querying for failed reports...")
        failed_reports_query = reports_collection.where("status", "==", "failed")
        failed_docs = failed_reports_query.stream()
        
        failed_reports = []
        for doc in failed_docs:
            try:
                data = doc.to_dict()
                if data:
                    failed_reports.append({
                        "report_id": doc.id,
                        "data": data
                    })
            except Exception as e:
                logger.warning(f"Failed to parse document {doc.id}: {e}")
        
        logger.info(f"Found {len(failed_reports)} failed reports")
        
        if len(failed_reports) == 0:
            logger.info("No failed reports found. Nothing to delete.")
            return
        
        # Show summary
        logger.info("\nFailed reports to delete:")
        for i, report in enumerate(failed_reports, 1):
            report_id = report["report_id"]
            data = report["data"]
            company = data.get("company", "Unknown")
            created_at = data.get("created_at", "Unknown")
            error_message = data.get("error_message", "No error message")
            logger.info(f"  {i}. {report_id} - {company} (created: {created_at})")
            if error_message:
                logger.info(f"     Error: {error_message[:100]}...")
        
        if dry_run:
            logger.info("\n[DRY RUN] Would delete the above reports. Run without --dry-run to actually delete.")
            return
        
        # Confirm deletion
        logger.info(f"\nAbout to delete {len(failed_reports)} failed reports.")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Deletion cancelled.")
            return
        
        # Delete each failed report
        deleted_count = 0
        failed_count = 0
        
        for report in failed_reports:
            report_id = report["report_id"]
            try:
                # Delete from database
                success = db_service.delete_report_metadata(report_id)
                if not success:
                    logger.warning(f"Failed to delete metadata for {report_id}")
                    failed_count += 1
                    continue
                
                # Delete from storage (if exists)
                try:
                    if hasattr(storage_service, 'delete_report'):
                        storage_service.delete_report(report_id)
                        logger.info(f"Deleted storage file for {report_id}")
                except Exception as storage_error:
                    # Log but don't fail - storage deletion is optional
                    logger.warning(f"Failed to delete storage file for {report_id}: {storage_error}")
                
                deleted_count += 1
                logger.info(f"✓ Deleted report: {report_id}")
                
            except Exception as e:
                logger.error(f"Failed to delete report {report_id}: {e}")
                failed_count += 1
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("Deletion Summary:")
        logger.info(f"  Successfully deleted: {deleted_count}")
        logger.info(f"  Failed to delete: {failed_count}")
        logger.info(f"  Total processed: {len(failed_reports)}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Error deleting failed reports: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Delete all failed reports")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    
    args = parser.parse_args()
    
    delete_failed_reports(dry_run=args.dry_run)

