"""
Database layer for ConsultantOS using Firestore
"""
import logging
import threading
from typing import Optional, Dict, List, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    firestore = None

from consultantos.config import settings

logger = logging.getLogger(__name__)

# Firestore client
_db_client: Optional[Any] = None


def get_db_client():
    """Get or create Firestore client"""
    global _db_client
    if not FIRESTORE_AVAILABLE:
        return None
    if _db_client is None:
        try:
            _db_client = firestore.Client(project=settings.gcp_project_id)
            logger.info("Initialized Firestore client")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise
    return _db_client


@dataclass
class APIKeyRecord:
    """API Key database record"""
    key_hash: str
    user_id: str
    description: Optional[str] = None
    created_at: str = None
    last_used: Optional[str] = None
    usage_count: int = 0
    active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for Firestore"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'APIKeyRecord':
        """Create from Firestore document"""
        return cls(**data)


@dataclass
class ReportMetadata:
    """Report metadata database record"""
    report_id: str
    user_id: Optional[str] = None
    company: str = None
    industry: Optional[str] = None
    frameworks: List[str] = None
    created_at: str = None
    status: str = "completed"  # completed, failed, processing
    confidence_score: Optional[float] = None
    execution_time_seconds: Optional[float] = None
    pdf_url: Optional[str] = None
    signed_url: Optional[str] = None
    error_message: Optional[str] = None
    framework_analysis: Optional[Dict] = None  # Store framework analysis for visualizations
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.frameworks is None:
            self.frameworks = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for Firestore"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportMetadata':
        """Create from Firestore document"""
        if not data:
            raise ValueError("Cannot create ReportMetadata from empty data")
        # Only use fields that exist in the dataclass
        field_names = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)


@dataclass
class UserAccount:
    """User account database record"""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    created_at: str = None
    last_login: Optional[str] = None
    subscription_tier: str = "free"  # free, basic, pro
    active: bool = True
    email_verified: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for Firestore"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserAccount':
        """Create from Firestore document"""
        return cls(**data)


class InMemoryDatabaseService:
    """In-memory database service for development/testing"""

    def __init__(self):
        self._api_keys: Dict[str, Dict] = {}
        self._reports: Dict[str, Dict] = {}
        self._users: Dict[str, Dict] = {}
        self._passwords: Dict[str, str] = {}
        self._subscriptions: Dict[str, Dict] = {}
        self._promo_codes: Dict[str, Dict] = {}
        self._billing_events: Dict[str, Dict] = {}
        self._monitors: Dict[str, Dict] = {}
        self._alerts: Dict[str, Dict] = {}
        self._snapshots: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        logger.info("Using in-memory database (Firestore not available)")
    
    def create_api_key(self, key_record: APIKeyRecord) -> bool:
        with self._lock:
            self._api_keys[key_record.key_hash] = key_record.to_dict()
        return True
    
    def get_api_key(self, key_hash: str) -> Optional[APIKeyRecord]:
        with self._lock:
            data = self._api_keys.get(key_hash)
            return APIKeyRecord.from_dict(data) if data else None
    
    def update_api_key(self, key_hash: str, updates: Dict) -> bool:
        with self._lock:
            if key_hash in self._api_keys:
                self._api_keys[key_hash].update(updates)
                return True
        return False
    
    def list_api_keys(self, user_id: str) -> List[APIKeyRecord]:
        with self._lock:
            return [APIKeyRecord.from_dict(v) for v in self._api_keys.values() if v.get("user_id") == user_id]
    
    def create_report_metadata(self, report: ReportMetadata) -> bool:
        with self._lock:
            self._reports[report.report_id] = report.to_dict()
        return True
    
    def get_report_metadata(self, report_id: str) -> Optional[ReportMetadata]:
        with self._lock:
            data = self._reports.get(report_id)
            return ReportMetadata.from_dict(data) if data else None
    
    def list_reports(
        self,
        user_id: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 100
    ) -> List[ReportMetadata]:
        with self._lock:
            reports = []
            for v in self._reports.values():
                try:
                    report = ReportMetadata.from_dict(v)
                    reports.append(report)
                except Exception as e:
                    # Skip invalid reports
                    logger.warning(f"Failed to deserialize report: {e}")
                    continue
            
            if user_id:
                reports = [r for r in reports if r.user_id == user_id]
            if company:
                reports = [r for r in reports if r.company == company]
            # Sort by created_at descending (most recent first)
            # Handle None values by using empty string for comparison
            reports.sort(key=lambda r: r.created_at if r.created_at else "", reverse=True)
            return reports[:limit]
    
    def create_user(self, user: UserAccount, password_hash: Optional[str] = None) -> bool:
        with self._lock:
            self._users[user.user_id] = user.to_dict()
            if password_hash:
                self._passwords[user.user_id] = password_hash
        return True
    
    def get_user(self, user_id: str) -> Optional[UserAccount]:
        with self._lock:
            data = self._users.get(user_id)
            return UserAccount.from_dict(data) if data else None
    
    def get_user_by_email(self, email: str) -> Optional[UserAccount]:
        with self._lock:
            for data in self._users.values():
                if data.get("email") == email:
                    return UserAccount.from_dict(data)
        return None
    
    def get_user_password_hash(self, user_id: str) -> Optional[str]:
        with self._lock:
            return self._passwords.get(user_id)
    
    def update_user_password(self, user_id: str, password_hash: str) -> bool:
        with self._lock:
            self._passwords[user_id] = password_hash
        return True
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        with self._lock:
            if user_id in self._users:
                self._users[user_id].update(updates)
                return True
        return False

    # Subscription Operations
    async def create_subscription(self, subscription) -> bool:
        """Create subscription record"""
        with self._lock:
            self._subscriptions[subscription.user_id] = subscription.dict()
        return True

    async def get_subscription(self, user_id: str):
        """Get subscription for user"""
        from consultantos.models.subscription import Subscription
        with self._lock:
            data = self._subscriptions.get(user_id)
            return Subscription(**data) if data else None

    async def update_subscription(self, subscription) -> bool:
        """Update subscription"""
        with self._lock:
            if subscription.user_id in self._subscriptions:
                self._subscriptions[subscription.user_id] = subscription.dict()
                return True
        return False

    async def delete_subscription(self, user_id: str) -> bool:
        """Delete subscription"""
        with self._lock:
            if user_id in self._subscriptions:
                del self._subscriptions[user_id]
                return True
        return False

    # Promo Code Operations
    async def create_promo_code(self, promo_code) -> bool:
        """Create promo code"""
        with self._lock:
            self._promo_codes[promo_code.code] = promo_code.dict()
        return True

    async def get_promo_code(self, code: str):
        """Get promo code"""
        from consultantos.models.subscription import PromoCode
        with self._lock:
            data = self._promo_codes.get(code)
            return PromoCode(**data) if data else None

    async def update_promo_code(self, promo_code) -> bool:
        """Update promo code"""
        with self._lock:
            if promo_code.code in self._promo_codes:
                self._promo_codes[promo_code.code] = promo_code.dict()
                return True
        return False

    # Billing Event Operations
    async def create_billing_event(self, event) -> bool:
        """Create billing event"""
        with self._lock:
            self._billing_events[event.id] = event.dict()
        return True

    async def list_billing_events(self, subscription_id: str, limit: int = 50):
        """List billing events for subscription"""
        from consultantos.models.subscription import BillingEvent
        with self._lock:
            events = [
                BillingEvent(**v) for v in self._billing_events.values()
                if v.get("subscription_id") == subscription_id
            ]
            events.sort(key=lambda e: e.created_at, reverse=True)
            return events[:limit]

    # Feedback Operations
    async def store_rating(self, rating) -> bool:
        """Store insight rating"""
        with self._lock:
            if not hasattr(self, '_ratings'):
                self._ratings = {}
            self._ratings[rating.id] = rating.dict()
        return True

    async def get_ratings_for_report(self, report_id: str):
        """Get all ratings for a report"""
        from consultantos.models.feedback import InsightRating
        with self._lock:
            if not hasattr(self, '_ratings'):
                return []
            return [
                InsightRating(**v) for v in self._ratings.values()
                if v.get("report_id") == report_id
            ]

    async def get_ratings_since(self, start_date: datetime):
        """Get all ratings since a date"""
        from consultantos.models.feedback import InsightRating
        with self._lock:
            if not hasattr(self, '_ratings'):
                return []
            return [
                InsightRating(**v) for v in self._ratings.values()
                if datetime.fromisoformat(v.get("created_at", "1970-01-01")) >= start_date
            ]

    async def store_correction(self, correction) -> bool:
        """Store insight correction"""
        with self._lock:
            if not hasattr(self, '_corrections'):
                self._corrections = {}
            self._corrections[correction.id] = correction.dict()
        return True

    async def get_corrections_for_report(self, report_id: str):
        """Get all corrections for a report"""
        from consultantos.models.feedback import InsightCorrection
        with self._lock:
            if not hasattr(self, '_corrections'):
                return []
            return [
                InsightCorrection(**v) for v in self._corrections.values()
                if v.get("report_id") == report_id
            ]

    async def get_corrections_since(self, start_date: datetime):
        """Get all corrections since a date"""
        from consultantos.models.feedback import InsightCorrection
        with self._lock:
            if not hasattr(self, '_corrections'):
                return []
            return [
                InsightCorrection(**v) for v in self._corrections.values()
                if datetime.fromisoformat(v.get("created_at", "1970-01-01")) >= start_date
            ]

    async def get_pending_corrections(self, limit: int = 50):
        """Get pending corrections awaiting validation"""
        from consultantos.models.feedback import InsightCorrection
        with self._lock:
            if not hasattr(self, '_corrections'):
                return []
            corrections = [
                InsightCorrection(**v) for v in self._corrections.values()
                if not v.get("validated", False)
            ]
            corrections.sort(key=lambda c: c.created_at, reverse=True)
            return corrections[:limit]

    async def get_validated_corrections(self, framework: Optional[str] = None, limit: int = 100):
        """Get validated corrections, optionally filtered by framework"""
        from consultantos.models.feedback import InsightCorrection
        with self._lock:
            if not hasattr(self, '_corrections'):
                return []
            corrections = [
                InsightCorrection(**v) for v in self._corrections.values()
                if v.get("validated", False)
            ]
            if framework:
                corrections = [c for c in corrections if c.section == framework]
            corrections.sort(key=lambda c: c.created_at, reverse=True)
            return corrections[:limit]

    async def update_correction(self, correction_id: str, **updates) -> bool:
        """Update correction fields"""
        with self._lock:
            if not hasattr(self, '_corrections'):
                return False
            if correction_id in self._corrections:
                self._corrections[correction_id].update(updates)
                return True
        return False

    async def get_high_rated_insights(self, framework: Optional[str] = None, min_rating: float = 4.5, limit: int = 20):
        """Get high-rated insights for positive examples"""
        from consultantos.models.feedback import InsightRating
        with self._lock:
            if not hasattr(self, '_ratings'):
                return []
            ratings = [
                InsightRating(**v) for v in self._ratings.values()
                if v.get("rating", 0) >= min_rating
            ]
            if framework:
                ratings = [
                    r for r in ratings
                    if "_" in r.insight_id and r.insight_id.split("_")[1] == framework
                ]
            ratings.sort(key=lambda r: r.rating, reverse=True)
            return ratings[:limit]

    async def store_learning_pattern(self, pattern) -> bool:
        """Store learning pattern"""
        with self._lock:
            if not hasattr(self, '_learning_patterns'):
                self._learning_patterns = {}
            self._learning_patterns[pattern.pattern_id] = pattern.dict()
        return True

    async def update_learning_pattern(self, pattern) -> bool:
        """Update learning pattern"""
        with self._lock:
            if not hasattr(self, '_learning_patterns'):
                return False
            if pattern.pattern_id in self._learning_patterns:
                self._learning_patterns[pattern.pattern_id] = pattern.dict()
                return True
        return False

    async def get_learning_patterns(self, framework: Optional[str] = None, min_confidence: float = 0.0):
        """Get learning patterns"""
        from consultantos.models.feedback import LearningPattern
        with self._lock:
            if not hasattr(self, '_learning_patterns'):
                return []
            patterns = [
                LearningPattern(**v) for v in self._learning_patterns.values()
                if v.get("confidence", 0) >= min_confidence
            ]
            if framework:
                patterns = [p for p in patterns if p.framework == framework]
            return patterns

    # Monitor Operations
    async def create_monitor(self, monitor) -> bool:
        """Create monitor record"""
        with self._lock:
            self._monitors[monitor.id] = monitor.dict() if hasattr(monitor, 'dict') else monitor.model_dump()
        return True

    async def get_monitor(self, monitor_id: str):
        """Get monitor by ID"""
        from consultantos.models.monitoring import Monitor
        with self._lock:
            data = self._monitors.get(monitor_id)
            return Monitor(**data) if data else None

    async def get_monitor_by_company(self, user_id: str, company: str):
        """Get monitor by user_id and company"""
        from consultantos.models.monitoring import Monitor
        with self._lock:
            for data in self._monitors.values():
                if data.get("user_id") == user_id and data.get("company") == company:
                    return Monitor(**data)
        return None

    async def get_user_monitors(self, user_id: str, status=None):
        """Get all monitors for a user, optionally filtered by status"""
        from consultantos.models.monitoring import Monitor
        with self._lock:
            monitors = []
            for data in self._monitors.values():
                if data.get("user_id") == user_id:
                    if status is None or data.get("status") == (status.value if hasattr(status, 'value') else str(status)):
                        monitors.append(Monitor(**data))
            return monitors

    async def update_monitor(self, monitor) -> bool:
        """Update monitor record"""
        with self._lock:
            if monitor.id in self._monitors:
                self._monitors[monitor.id] = monitor.dict() if hasattr(monitor, 'dict') else monitor.model_dump()
                return True
        return False

    async def create_alert(self, alert) -> bool:
        """Create alert record"""
        with self._lock:
            self._alerts[alert.id] = alert.dict() if hasattr(alert, 'dict') else alert.model_dump()
        return True

    async def get_monitor_alerts(self, monitor_id: str, limit: int = 50):
        """Get alerts for a monitor"""
        from consultantos.models.monitoring import Alert
        with self._lock:
            alerts = []
            for data in self._alerts.values():
                if data.get("monitor_id") == monitor_id:
                    alerts.append(Alert(**data))
            # Sort by created_at descending
            alerts.sort(key=lambda a: a.created_at if hasattr(a, 'created_at') else "", reverse=True)
            return alerts[:limit]

    async def create_snapshot(self, snapshot) -> bool:
        """Create snapshot record"""
        with self._lock:
            snapshot_id = f"{snapshot.monitor_id}_{snapshot.timestamp.isoformat()}"
            self._snapshots[snapshot_id] = snapshot.dict() if hasattr(snapshot, 'dict') else snapshot.model_dump()
        return True

    async def get_latest_snapshot(self, monitor_id: str):
        """Get latest snapshot for a monitor"""
        from consultantos.models.monitoring import MonitorAnalysisSnapshot
        with self._lock:
            snapshots = []
            for data in self._snapshots.values():
                if data.get("monitor_id") == monitor_id:
                    snapshots.append(MonitorAnalysisSnapshot(**data))
            if snapshots:
                snapshots.sort(key=lambda s: s.timestamp if hasattr(s, 'timestamp') else "", reverse=True)
                return snapshots[0]
        return None

    async def get_monitoring_stats(self, user_id: str):
        """Get monitoring statistics for a user"""
        from consultantos.models.monitoring import MonitoringStats
        monitors = await self.get_user_monitors(user_id)
        with self._lock:
            active_monitors = sum(1 for m in monitors if m.status.value == "active")
            paused_monitors = sum(1 for m in monitors if m.status.value == "paused")
            # Count alerts
            alerts_24h = []
            unread_count = 0
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            for data in self._alerts.values():
                alert_time = None
                created_at = data.get("created_at")
                if created_at:
                    try:
                        if isinstance(created_at, str):
                            alert_time = datetime.fromisoformat(created_at)
                        elif isinstance(created_at, datetime):
                            alert_time = created_at
                        else:
                            continue
                        # Normalize to UTC if naive
                        if alert_time.tzinfo is None:
                            alert_time = alert_time.replace(tzinfo=timezone.utc)
                        else:
                            alert_time = alert_time.astimezone(timezone.utc)
                    except (ValueError, TypeError):
                        # Skip alerts with invalid timestamps
                        continue
                if alert_time and alert_time >= yesterday:
                    alerts_24h.append(data)
                if not data.get("read", False):
                    unread_count += 1
            avg_confidence = sum(float(a.get("confidence", 0)) for a in alerts_24h) / len(alerts_24h) if alerts_24h else 0.0
            return MonitoringStats(
                total_monitors=len(monitors),
                active_monitors=active_monitors,
                paused_monitors=paused_monitors,
                total_alerts_24h=len(alerts_24h),
                unread_alerts=unread_count,
                avg_alert_confidence=avg_confidence,
                top_change_types=[]
            )


class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        db_client = get_db_client()
        if db_client is None:
            raise RuntimeError("Firestore client not available")
        self.db = db_client
        self.api_keys_collection = self.db.collection("api_keys")
        self.reports_collection = self.db.collection("reports")
        self.users_collection = self.db.collection("users")
        self.subscriptions_collection = self.db.collection("subscriptions")
        self.promo_codes_collection = self.db.collection("promo_codes")
        self.billing_events_collection = self.db.collection("billing_events")
    
    # API Key Operations
    def create_api_key(self, key_record: APIKeyRecord) -> bool:
        """Create API key record"""
        try:
            doc_ref = self.api_keys_collection.document(key_record.key_hash)
            doc_ref.set(key_record.to_dict())
            logger.info(f"Created API key record: {key_record.key_hash[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            return False
    
    def get_api_key(self, key_hash: str) -> Optional[APIKeyRecord]:
        """Get API key record"""
        try:
            doc_ref = self.api_keys_collection.document(key_hash)
            doc = doc_ref.get()
            if doc.exists:
                return APIKeyRecord.from_dict(doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get API key: {e}")
            return None
    
    def update_api_key(self, key_hash: str, updates: Dict) -> bool:
        """Update API key record"""
        try:
            doc_ref = self.api_keys_collection.document(key_hash)
            doc_ref.update(updates)
            logger.info(f"Updated API key: {key_hash[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to update API key: {e}")
            return False
    
    def list_api_keys(self, user_id: str) -> List[APIKeyRecord]:
        """List all API keys for a user"""
        try:
            query = self.api_keys_collection.where("user_id", "==", user_id)
            docs = query.stream()
            return [APIKeyRecord.from_dict(doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            return []
    
    # Report Operations
    def create_report_metadata(self, report: ReportMetadata) -> bool:
        """Create report metadata record"""
        try:
            doc_ref = self.reports_collection.document(report.report_id)
            doc_ref.set(report.to_dict())
            logger.info(f"Created report metadata: {report.report_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create report metadata: {e}")
            return False
    
    def get_report_metadata(self, report_id: str) -> Optional[ReportMetadata]:
        """Get report metadata"""
        try:
            doc_ref = self.reports_collection.document(report_id)
            doc = doc_ref.get()
            if doc.exists:
                return ReportMetadata.from_dict(doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get report metadata: {e}")
            return None
    
    def update_report_metadata(self, report_id: str, updates: Dict) -> bool:
        """Update report metadata"""
        try:
            doc_ref = self.reports_collection.document(report_id)
            doc_ref.update(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update report metadata: {e}")
            return False
    
    def list_reports(
        self,
        user_id: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50,
        order_by: str = "created_at"
    ) -> List[ReportMetadata]:
        """
        List reports with optional filters
        
        Note: This query requires composite indexes in Firestore:
        - (user_id, created_at DESC)
        - (company, created_at DESC)
        - (user_id, company, created_at DESC)
        
        Create these indexes in firestore.indexes.json or Firebase Console.
        """
        try:
            query = self.reports_collection
            
            if user_id:
                query = query.where("user_id", "==", user_id)
            if company:
                query = query.where("company", "==", company)
            
            # Order by created_at descending (most recent first)
            query = query.order_by(order_by, direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            
            docs = query.stream()
            return [ReportMetadata.from_dict(doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return []
    
    def delete_report_metadata(self, report_id: str) -> bool:
        """Delete report metadata"""
        try:
            doc_ref = self.reports_collection.document(report_id)
            doc_ref.delete()
            logger.info(f"Deleted report metadata: {report_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete report metadata: {e}")
            return False
    
    # User Operations
    def create_user(self, user: UserAccount, password_hash: Optional[str] = None) -> bool:
        """Create user account with optional password hash (transactional)"""
        try:
            # Use batched write to ensure both writes succeed or both fail
            batch = self.db.batch()
            
            # Add user document
            doc_ref = self.users_collection.document(user.user_id)
            user_dict = user.to_dict()
            batch.set(doc_ref, user_dict)
            
            # Store password hash in separate collection for security
            if password_hash:
                passwords_collection = self.db.collection("user_passwords")
                password_doc = passwords_collection.document(user.user_id)
                batch.set(password_doc, {
                    "password_hash": password_hash,
                    "created_at": datetime.now().isoformat()
                })
            
            # Commit batch (both writes succeed or both fail)
            batch.commit()
            logger.info(f"Created user account: {user.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            return False
    
    def get_user(self, user_id: str) -> Optional[UserAccount]:
        """Get user account"""
        try:
            doc_ref = self.users_collection.document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return UserAccount.from_dict(doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserAccount]:
        """Get user account by email"""
        try:
            query = self.users_collection.where("email", "==", email).limit(1)
            docs = list(query.stream())
            if docs:
                return UserAccount.from_dict(docs[0].to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    def get_user_password_hash(self, user_id: str) -> Optional[str]:
        """Get password hash for user"""
        try:
            passwords_collection = self.db.collection("user_passwords")
            doc_ref = passwords_collection.document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get("password_hash")
            return None
        except Exception as e:
            logger.error(f"Failed to get password hash: {e}")
            return None
    
    def update_user_password(self, user_id: str, password_hash: str) -> bool:
        """Update user password hash"""
        try:
            passwords_collection = self.db.collection("user_passwords")
            doc_ref = passwords_collection.document(user_id)
            doc_ref.set({
                "password_hash": password_hash,
                "updated_at": datetime.now().isoformat()
            }, merge=True)
            return True
        except Exception as e:
            logger.error(f"Failed to update password: {e}")
            return False
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user account"""
        try:
            doc_ref = self.users_collection.document(user_id)
            doc_ref.update(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False

    # Subscription Operations
    async def create_subscription(self, subscription) -> bool:
        """Create subscription record"""
        try:
            doc_ref = self.subscriptions_collection.document(subscription.user_id)
            doc_ref.set(subscription.dict())
            logger.info(f"Created subscription for user: {subscription.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return False

    async def get_subscription(self, user_id: str):
        """Get subscription for user"""
        from consultantos.models.subscription import Subscription
        try:
            doc_ref = self.subscriptions_collection.document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return Subscription(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            return None

    async def update_subscription(self, subscription) -> bool:
        """Update subscription"""
        try:
            doc_ref = self.subscriptions_collection.document(subscription.user_id)
            doc_ref.update(subscription.dict())
            logger.info(f"Updated subscription for user: {subscription.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update subscription: {e}")
            return False

    async def delete_subscription(self, user_id: str) -> bool:
        """Delete subscription"""
        try:
            doc_ref = self.subscriptions_collection.document(user_id)
            doc_ref.delete()
            logger.info(f"Deleted subscription for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete subscription: {e}")
            return False

    # Promo Code Operations
    async def create_promo_code(self, promo_code) -> bool:
        """Create promo code"""
        try:
            doc_ref = self.promo_codes_collection.document(promo_code.code)
            doc_ref.set(promo_code.dict())
            logger.info(f"Created promo code: {promo_code.code}")
            return True
        except Exception as e:
            logger.error(f"Failed to create promo code: {e}")
            return False

    async def get_promo_code(self, code: str):
        """Get promo code"""
        from consultantos.models.subscription import PromoCode
        try:
            doc_ref = self.promo_codes_collection.document(code)
            doc = doc_ref.get()
            if doc.exists:
                return PromoCode(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get promo code: {e}")
            return None

    async def update_promo_code(self, promo_code) -> bool:
        """Update promo code"""
        try:
            doc_ref = self.promo_codes_collection.document(promo_code.code)
            doc_ref.update(promo_code.dict())
            logger.info(f"Updated promo code: {promo_code.code}")
            return True
        except Exception as e:
            logger.error(f"Failed to update promo code: {e}")
            return False

    # Billing Event Operations
    async def create_billing_event(self, event) -> bool:
        """Create billing event"""
        try:
            doc_ref = self.billing_events_collection.document(event.id)
            doc_ref.set(event.dict())
            logger.info(f"Created billing event: {event.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create billing event: {e}")
            return False

    async def list_billing_events(self, subscription_id: str, limit: int = 50):
        """List billing events for subscription"""
        from consultantos.models.subscription import BillingEvent
        try:
            query = self.billing_events_collection.where("subscription_id", "==", subscription_id)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            docs = query.stream()
            return [BillingEvent(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to list billing events: {e}")
            return []

    # Feedback Operations
    async def store_rating(self, rating) -> bool:
        """Store insight rating"""
        try:
            ratings_collection = self.db.collection("insight_ratings")
            doc_ref = ratings_collection.document(rating.id)
            doc_ref.set(rating.dict())
            logger.info(f"Stored insight rating: {rating.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store rating: {e}")
            return False

    async def get_ratings_for_report(self, report_id: str):
        """Get all ratings for a report"""
        from consultantos.models.feedback import InsightRating
        try:
            ratings_collection = self.db.collection("insight_ratings")
            query = ratings_collection.where("report_id", "==", report_id)
            docs = query.stream()
            return [InsightRating(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get ratings for report: {e}")
            return []

    async def get_ratings_since(self, start_date: datetime):
        """Get all ratings since a date"""
        from consultantos.models.feedback import InsightRating
        try:
            ratings_collection = self.db.collection("insight_ratings")
            query = ratings_collection.where("created_at", ">=", start_date.isoformat())
            docs = query.stream()
            return [InsightRating(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get ratings since date: {e}")
            return []

    async def store_correction(self, correction) -> bool:
        """Store insight correction"""
        try:
            corrections_collection = self.db.collection("insight_corrections")
            doc_ref = corrections_collection.document(correction.id)
            doc_ref.set(correction.dict())
            logger.info(f"Stored insight correction: {correction.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store correction: {e}")
            return False

    async def get_corrections_for_report(self, report_id: str):
        """Get all corrections for a report"""
        from consultantos.models.feedback import InsightCorrection
        try:
            corrections_collection = self.db.collection("insight_corrections")
            query = corrections_collection.where("report_id", "==", report_id)
            docs = query.stream()
            return [InsightCorrection(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get corrections for report: {e}")
            return []

    async def get_corrections_since(self, start_date: datetime):
        """Get all corrections since a date"""
        from consultantos.models.feedback import InsightCorrection
        try:
            corrections_collection = self.db.collection("insight_corrections")
            query = corrections_collection.where("created_at", ">=", start_date.isoformat())
            docs = query.stream()
            return [InsightCorrection(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get corrections since date: {e}")
            return []

    async def get_pending_corrections(self, limit: int = 50):
        """Get pending corrections awaiting validation"""
        from consultantos.models.feedback import InsightCorrection
        try:
            corrections_collection = self.db.collection("insight_corrections")
            query = corrections_collection.where("validated", "==", False)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            docs = query.stream()
            return [InsightCorrection(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get pending corrections: {e}")
            return []

    async def get_validated_corrections(self, framework: Optional[str] = None, limit: int = 100):
        """Get validated corrections, optionally filtered by framework"""
        from consultantos.models.feedback import InsightCorrection
        try:
            corrections_collection = self.db.collection("insight_corrections")
            query = corrections_collection.where("validated", "==", True)
            if framework:
                query = query.where("section", "==", framework)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            docs = query.stream()
            return [InsightCorrection(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get validated corrections: {e}")
            return []

    async def update_correction(self, correction_id: str, **updates) -> bool:
        """Update correction fields"""
        try:
            corrections_collection = self.db.collection("insight_corrections")
            doc_ref = corrections_collection.document(correction_id)
            doc_ref.update(updates)
            logger.info(f"Updated correction: {correction_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update correction: {e}")
            return False

    async def get_high_rated_insights(self, framework: Optional[str] = None, min_rating: float = 4.5, limit: int = 20):
        """Get high-rated insights for positive examples"""
        from consultantos.models.feedback import InsightRating
        try:
            ratings_collection = self.db.collection("insight_ratings")
            query = ratings_collection.where("rating", ">=", int(min_rating))
            query = query.order_by("rating", direction=firestore.Query.DESCENDING)
            query = query.limit(limit * 2)  # Get extra in case of filtering
            docs = query.stream()
            ratings = [InsightRating(**doc.to_dict()) for doc in docs]
            
            # Filter by framework if specified
            if framework:
                ratings = [
                    r for r in ratings
                    if "_" in r.insight_id and r.insight_id.split("_")[1] == framework
                ]
            
            return ratings[:limit]
        except Exception as e:
            logger.error(f"Failed to get high-rated insights: {e}")
            return []

    async def store_learning_pattern(self, pattern) -> bool:
        """Store learning pattern"""
        try:
            patterns_collection = self.db.collection("learning_patterns")
            doc_ref = patterns_collection.document(pattern.pattern_id)
            doc_ref.set(pattern.dict())
            logger.info(f"Stored learning pattern: {pattern.pattern_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store learning pattern: {e}")
            return False

    async def update_learning_pattern(self, pattern) -> bool:
        """Update learning pattern"""
        try:
            patterns_collection = self.db.collection("learning_patterns")
            doc_ref = patterns_collection.document(pattern.pattern_id)
            doc_ref.update(pattern.dict())
            logger.info(f"Updated learning pattern: {pattern.pattern_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update learning pattern: {e}")
            return False

    async def get_learning_patterns(self, framework: Optional[str] = None, min_confidence: float = 0.0):
        """Get learning patterns"""
        from consultantos.models.feedback import LearningPattern
        try:
            patterns_collection = self.db.collection("learning_patterns")
            query = patterns_collection.where("confidence", ">=", min_confidence)
            if framework:
                query = query.where("framework", "==", framework)
            docs = query.stream()
            return [LearningPattern(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get learning patterns: {e}")
            return []

    # Monitor Operations
    async def create_monitor(self, monitor) -> bool:
        """Create monitor record"""
        from consultantos.models.monitoring import Monitor
        try:
            monitors_collection = self.db.collection("monitors")
            doc_ref = monitors_collection.document(monitor.id)
            # Convert Pydantic model to dict
            monitor_dict = monitor.dict() if hasattr(monitor, 'dict') else monitor.model_dump()
            # Convert datetime objects to ISO strings
            for key, value in monitor_dict.items():
                if isinstance(value, datetime):
                    monitor_dict[key] = value.isoformat()
            doc_ref.set(monitor_dict)
            logger.info(f"Created monitor: {monitor.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create monitor: {e}")
            return False

    async def get_monitor(self, monitor_id: str):
        """Get monitor by ID"""
        from consultantos.models.monitoring import Monitor
        try:
            monitors_collection = self.db.collection("monitors")
            doc_ref = monitors_collection.document(monitor_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return Monitor(**data)
            return None
        except Exception as e:
            logger.error(f"Failed to get monitor: {e}")
            return None

    async def get_monitor_by_company(self, user_id: str, company: str):
        """Get monitor by user_id and company"""
        from consultantos.models.monitoring import Monitor
        try:
            monitors_collection = self.db.collection("monitors")
            query = monitors_collection.where("user_id", "==", user_id).where("company", "==", company).limit(1)
            docs = list(query.stream())
            if docs:
                return Monitor(**docs[0].to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get monitor by company: {e}")
            return None

    async def get_user_monitors(self, user_id: str, status=None):
        """Get all monitors for a user, optionally filtered by status"""
        from consultantos.models.monitoring import Monitor, MonitorStatus
        try:
            monitors_collection = self.db.collection("monitors")
            query = monitors_collection.where("user_id", "==", user_id)
            if status:
                query = query.where("status", "==", status.value if hasattr(status, 'value') else str(status))
            docs = query.stream()
            return [Monitor(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get user monitors: {e}")
            return []

    async def update_monitor(self, monitor) -> bool:
        """Update monitor record"""
        try:
            monitors_collection = self.db.collection("monitors")
            doc_ref = monitors_collection.document(monitor.id)
            # Convert Pydantic model to dict
            monitor_dict = monitor.dict() if hasattr(monitor, 'dict') else monitor.model_dump()
            # Convert datetime objects to ISO strings
            for key, value in monitor_dict.items():
                if isinstance(value, datetime):
                    monitor_dict[key] = value.isoformat()
            doc_ref.set(monitor_dict, merge=True)
            logger.info(f"Updated monitor: {monitor.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update monitor: {e}")
            return False

    async def create_alert(self, alert) -> bool:
        """Create alert record"""
        from consultantos.models.monitoring import Alert
        try:
            alerts_collection = self.db.collection("alerts")
            doc_ref = alerts_collection.document(alert.id)
            alert_dict = alert.dict() if hasattr(alert, 'dict') else alert.model_dump()
            # Convert datetime objects to ISO strings
            for key, value in alert_dict.items():
                if isinstance(value, datetime):
                    alert_dict[key] = value.isoformat()
            doc_ref.set(alert_dict)
            logger.info(f"Created alert: {alert.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return False

    async def get_monitor_alerts(self, monitor_id: str, limit: int = 50):
        """Get alerts for a monitor"""
        from consultantos.models.monitoring import Alert
        try:
            alerts_collection = self.db.collection("alerts")
            query = alerts_collection.where("monitor_id", "==", monitor_id)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            docs = query.stream()
            return [Alert(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get monitor alerts: {e}")
            return []

    async def create_snapshot(self, snapshot) -> bool:
        """Create snapshot record"""
        from consultantos.models.monitoring import MonitorAnalysisSnapshot
        try:
            snapshots_collection = self.db.collection("snapshots")
            snapshot_id = f"{snapshot.monitor_id}_{snapshot.timestamp.isoformat()}"
            doc_ref = snapshots_collection.document(snapshot_id)
            snapshot_dict = snapshot.dict() if hasattr(snapshot, 'dict') else snapshot.model_dump()
            # Convert datetime objects to ISO strings
            for key, value in snapshot_dict.items():
                if isinstance(value, datetime):
                    snapshot_dict[key] = value.isoformat()
            doc_ref.set(snapshot_dict)
            return True
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            return False

    async def get_latest_snapshot(self, monitor_id: str):
        """Get latest snapshot for a monitor"""
        from consultantos.models.monitoring import MonitorAnalysisSnapshot
        try:
            snapshots_collection = self.db.collection("snapshots")
            query = snapshots_collection.where("monitor_id", "==", monitor_id)
            query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
            query = query.limit(1)
            docs = list(query.stream())
            if docs:
                return MonitorAnalysisSnapshot(**docs[0].to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get latest snapshot: {e}")
            return None

    async def get_monitoring_stats(self, user_id: str):
        """Get monitoring statistics for a user"""
        from consultantos.models.monitoring import MonitoringStats
        try:
            monitors = await self.get_user_monitors(user_id)
            alerts_collection = self.db.collection("alerts")
            
            # Count monitors by status
            total_monitors = len(monitors)
            active_monitors = sum(1 for m in monitors if m.status.value == "active")
            paused_monitors = sum(1 for m in monitors if m.status.value == "paused")
            
            # Get alerts from last 24 hours
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            alerts_query = alerts_collection.where("created_at", ">=", yesterday.isoformat())
            recent_alerts = list(alerts_query.stream())
            total_alerts_24h = len(recent_alerts)
            
            # Count unread alerts
            unread_query = alerts_collection.where("read", "==", False)
            unread_alerts = list(unread_query.stream())
            unread_count = len(unread_alerts)
            
            # Calculate average confidence
            if recent_alerts:
                avg_confidence = sum(float(a.to_dict().get("confidence", 0)) for a in recent_alerts) / len(recent_alerts)
            else:
                avg_confidence = 0.0
            
            # Get top change types (simplified)
            top_change_types = []
            
            return MonitoringStats(
                total_monitors=total_monitors,
                active_monitors=active_monitors,
                paused_monitors=paused_monitors,
                total_alerts_24h=total_alerts_24h,
                unread_alerts=unread_count,
                avg_alert_confidence=avg_confidence,
                top_change_types=top_change_types
            )
        except Exception as e:
            logger.error(f"Failed to get monitoring stats: {e}")
            # Return default stats on error
            return MonitoringStats(
                total_monitors=0,
                active_monitors=0,
                paused_monitors=0,
                total_alerts_24h=0,
                unread_alerts=0,
                avg_alert_confidence=0.0,
                top_change_types=[]
            )


# Global database service instance
_db_service: Optional[Union[DatabaseService, InMemoryDatabaseService]] = None
_db_service_lock = threading.Lock()


def get_db_service() -> Union[DatabaseService, InMemoryDatabaseService]:
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        with _db_service_lock:
            if _db_service is None:
                if FIRESTORE_AVAILABLE and settings.environment != "test":
                    try:
                        _db_service = DatabaseService()
                    except Exception as e:
                        logger.warning(f"Failed to initialize Firestore, falling back to in-memory database: {e}")
                        _db_service = InMemoryDatabaseService()
                else:
                    logger.info("Using in-memory database (Firestore not available or in test mode)")
                    _db_service = InMemoryDatabaseService()
    return _db_service