"""
GDPR and CCPA Compliance Module
Implements data retention, deletion, and user rights management
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from consultantos.database import get_db_service

logger = logging.getLogger(__name__)


class GDPRComplianceService:
    """
    GDPR/CCPA compliance service

    Implements:
    - Right to erasure (Article 17)
    - Right to data portability (Article 20)
    - Data retention policies
    - Consent management
    - Breach notification
    """

    # Data retention periods (days)
    RETENTION_PERIODS = {
        'email_analysis': 30,  # Dark data analyses
        'audit_logs': 365,     # Audit logs (legal requirement)
        'credentials': 90,     # Inactive credentials
        'user_data': 730,      # General user data (2 years)
    }

    def __init__(self):
        """Initialize GDPR compliance service"""
        self.db = get_db_service()

    async def delete_user_data(self, user_id: str) -> Dict[str, int]:
        """
        Delete all user data (Right to Erasure - GDPR Article 17)

        Args:
            user_id: User ID to delete data for

        Returns:
            Dictionary with counts of deleted items
        """
        logger.info(f"Starting complete data deletion for user {user_id}")

        deleted_counts = {
            'email_sources': 0,
            'credentials': 0,
            'analyses': 0,
            'audit_logs': 0,
        }

        try:
            # 1. Delete email sources
            email_sources = await self.db.query_documents(
                collection=f"users/{user_id}/email_sources"
            )

            for source in email_sources:
                # Delete credentials
                creds_id = source.get('credentials_id')
                if creds_id:
                    await self.db.delete_document(
                        collection=f"credentials/{creds_id}",
                        document_id=creds_id
                    )
                    deleted_counts['credentials'] += 1

                # Delete source
                await self.db.delete_document(
                    collection=f"users/{user_id}/email_sources",
                    document_id=source.id
                )
                deleted_counts['email_sources'] += 1

            # 2. Delete analyses
            analyses = await self.db.query_documents(
                collection=f"users/{user_id}/dark_data_analyses"
            )

            for analysis in analyses:
                await self.db.delete_document(
                    collection=f"users/{user_id}/dark_data_analyses",
                    document_id=analysis.id
                )
                deleted_counts['analyses'] += 1

            # 3. Delete audit logs
            audit_logs = await self.db.query_documents(
                collection="audit_logs",
                filters={'user_id': user_id}
            )

            for log in audit_logs:
                await self.db.delete_document(
                    collection="audit_logs",
                    document_id=log.id
                )
                deleted_counts['audit_logs'] += 1

            # 4. Delete user profile
            await self.db.delete_document(
                collection="users",
                document_id=user_id
            )

            logger.info(
                f"User data deletion complete for {user_id}: {deleted_counts}"
            )

            return deleted_counts

        except Exception as e:
            logger.error(f"Failed to delete user data: {e}")
            raise

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data (Right to Data Portability - GDPR Article 20)

        Args:
            user_id: User ID to export data for

        Returns:
            Dictionary containing all user data
        """
        logger.info(f"Exporting data for user {user_id}")

        try:
            export_data = {
                'user_id': user_id,
                'export_timestamp': datetime.utcnow().isoformat(),
                'email_sources': [],
                'analyses': [],
                'audit_logs': [],
            }

            # Export email sources (without credentials for security)
            email_sources = await self.db.query_documents(
                collection=f"users/{user_id}/email_sources"
            )

            export_data['email_sources'] = [
                {
                    'provider': source['provider'],
                    'user_email': source['user_email'],
                    'created_at': source['created_at'],
                    'last_synced': source.get('last_synced'),
                    'filters': source.get('filters', {})
                }
                for source in email_sources
            ]

            # Export analyses
            analyses = await self.db.query_documents(
                collection=f"users/{user_id}/dark_data_analyses"
            )

            export_data['analyses'] = [
                {
                    'analysis_id': analysis.id,
                    'created_at': analysis.get('created_at'),
                    'emails_analyzed': analysis.get('emails_analyzed'),
                    'pii_detected': analysis.get('pii_detected'),
                    'anonymized_content': analysis.get('anonymized_content'),
                }
                for analysis in analyses
            ]

            # Export audit logs
            audit_logs = await self.db.query_documents(
                collection="audit_logs",
                filters={'user_id': user_id}
            )

            export_data['audit_logs'] = [
                {
                    'timestamp': log.get('timestamp'),
                    'action': log.get('action'),
                    'resource_type': log.get('resource_type'),
                }
                for log in audit_logs
            ]

            logger.info(f"Data export complete for user {user_id}")

            return export_data

        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            raise

    async def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired data based on retention policies

        Should be run periodically (e.g., daily cron job)

        Returns:
            Dictionary with counts of deleted items
        """
        logger.info("Starting expired data cleanup")

        deleted_counts = {
            'analyses': 0,
            'credentials': 0,
            'audit_logs': 0,
        }

        try:
            now = datetime.utcnow()

            # Clean up old analyses (30 days)
            cutoff_date = now - timedelta(days=self.RETENTION_PERIODS['email_analysis'])

            # Query all users
            users = await self.db.query_documents(collection="users")

            for user in users:
                user_id = user.id

                # Delete old analyses
                analyses = await self.db.query_documents(
                    collection=f"users/{user_id}/dark_data_analyses"
                )

                for analysis in analyses:
                    created_at = datetime.fromisoformat(analysis.get('created_at', now.isoformat()))

                    if created_at < cutoff_date:
                        await self.db.delete_document(
                            collection=f"users/{user_id}/dark_data_analyses",
                            document_id=analysis.id
                        )
                        deleted_counts['analyses'] += 1

            # Clean up old audit logs (365 days)
            audit_cutoff = now - timedelta(days=self.RETENTION_PERIODS['audit_logs'])

            audit_logs = await self.db.query_documents(collection="audit_logs")

            for log in audit_logs:
                timestamp = datetime.fromisoformat(log.get('timestamp', now.isoformat()))

                if timestamp < audit_cutoff:
                    await self.db.delete_document(
                        collection="audit_logs",
                        document_id=log.id
                    )
                    deleted_counts['audit_logs'] += 1

            logger.info(f"Expired data cleanup complete: {deleted_counts}")

            return deleted_counts

        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            raise

    async def record_consent(
        self,
        user_id: str,
        consent_type: str,
        granted: bool,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Record user consent for data processing

        Args:
            user_id: User ID
            consent_type: Type of consent (e.g., 'email_analysis', 'pii_processing')
            granted: Whether consent was granted or revoked
            ip_address: User's IP address for audit trail

        Returns:
            Consent record ID
        """
        try:
            consent_record = {
                'user_id': user_id,
                'consent_type': consent_type,
                'granted': granted,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': ip_address,
            }

            doc = await self.db.create_document(
                collection=f"users/{user_id}/consent_records",
                data=consent_record
            )

            logger.info(
                f"Consent recorded: user={user_id}, type={consent_type}, "
                f"granted={granted}"
            )

            return doc.id

        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            raise

    async def check_consent(
        self,
        user_id: str,
        consent_type: str
    ) -> bool:
        """
        Check if user has granted specific consent

        Args:
            user_id: User ID
            consent_type: Type of consent to check

        Returns:
            True if consent granted, False otherwise
        """
        try:
            # Get latest consent record for this type
            consents = await self.db.query_documents(
                collection=f"users/{user_id}/consent_records",
                filters={'consent_type': consent_type},
                order_by=[('timestamp', 'desc')],
                limit=1
            )

            if not consents:
                return False

            return consents[0].get('granted', False)

        except Exception as e:
            logger.error(f"Failed to check consent: {e}")
            return False

    async def log_data_breach(
        self,
        breach_type: str,
        affected_users: List[str],
        description: str,
        severity: str = 'medium'
    ) -> str:
        """
        Log data breach for compliance reporting

        GDPR requires notification within 72 hours of breach discovery

        Args:
            breach_type: Type of breach (e.g., 'unauthorized_access', 'data_leak')
            affected_users: List of affected user IDs
            description: Breach description
            severity: Severity level (low, medium, high, critical)

        Returns:
            Breach record ID
        """
        try:
            breach_record = {
                'breach_type': breach_type,
                'affected_user_count': len(affected_users),
                'affected_users': affected_users,
                'description': description,
                'severity': severity,
                'discovered_at': datetime.utcnow().isoformat(),
                'status': 'discovered',  # discovered, investigating, resolved
            }

            doc = await self.db.create_document(
                collection="security/data_breaches",
                data=breach_record
            )

            logger.critical(
                f"DATA BREACH LOGGED: {breach_type}, severity={severity}, "
                f"affected_users={len(affected_users)}, record_id={doc.id}"
            )

            # In production: Send immediate alerts to security team
            # and prepare for regulatory notification

            return doc.id

        except Exception as e:
            logger.error(f"Failed to log data breach: {e}")
            raise


# Singleton instance
_gdpr_service: Optional[GDPRComplianceService] = None


def get_gdpr_service() -> GDPRComplianceService:
    """Get or create GDPR compliance service singleton"""
    global _gdpr_service

    if _gdpr_service is None:
        _gdpr_service = GDPRComplianceService()

    return _gdpr_service
