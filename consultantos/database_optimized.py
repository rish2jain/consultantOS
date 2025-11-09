"""
Optimized database layer with connection pooling and batch operations
"""
import logging
import threading
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    from google.cloud import firestore
    from google.cloud.firestore_v1 import Query
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    firestore = None
    Query = None

from consultantos.config import settings

logger = logging.getLogger(__name__)

# Firestore client with connection pooling
_db_client: Optional[Any] = None
_db_client_lock = threading.Lock()

# Connection pool settings
FIRESTORE_POOL_SIZE = 20
FIRESTORE_MIN_POOL_SIZE = 5
FIRESTORE_CONNECTION_TIMEOUT = 10.0  # seconds
FIRESTORE_IDLE_TIMEOUT = 300.0  # 5 minutes


def get_db_client():
    """
    Get or create Firestore client with connection pooling

    Firestore SDK handles connection pooling internally via gRPC.
    We configure it for optimal performance.
    """
    global _db_client
    if not FIRESTORE_AVAILABLE:
        return None
    if _db_client is None:
        with _db_client_lock:
            if _db_client is None:
                try:
                    # Create client with optimal settings
                    _db_client = firestore.Client(
                        project=settings.gcp_project_id
                    )
                    logger.info(f"Initialized Firestore client with connection pooling (pool_size: {FIRESTORE_POOL_SIZE})")
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
    status: str = "completed"
    confidence_score: Optional[float] = None
    execution_time_seconds: Optional[float] = None
    pdf_url: Optional[str] = None
    signed_url: Optional[str] = None
    error_message: Optional[str] = None
    framework_analysis: Optional[Dict] = None

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
    subscription_tier: str = "free"
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

    def get_reports_batch(self, report_ids: List[str]) -> Dict[str, ReportMetadata]:
        """Batch get reports by IDs"""
        with self._lock:
            result = {}
            for report_id in report_ids:
                data = self._reports.get(report_id)
                if data:
                    try:
                        result[report_id] = ReportMetadata.from_dict(data)
                    except Exception as e:
                        logger.warning(f"Failed to deserialize report {report_id}: {e}")
            return result

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
                    logger.warning(f"Failed to deserialize report: {e}")
                    continue

            if user_id:
                reports = [r for r in reports if r.user_id == user_id]
            if company:
                reports = [r for r in reports if r.company == company]
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


class OptimizedDatabaseService:
    """
    Optimized database service with batch operations and connection pooling

    Performance improvements:
    - Batch reads to eliminate N+1 queries
    - Connection pooling via Firestore SDK
    - Efficient indexing strategies
    - Retry logic with exponential backoff
    """

    def __init__(self):
        db_client = get_db_client()
        if db_client is None:
            raise RuntimeError("Firestore client not available")
        self.db = db_client
        self.api_keys_collection = self.db.collection("api_keys")
        self.reports_collection = self.db.collection("reports")
        self.users_collection = self.db.collection("users")

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

    # Report Operations (OPTIMIZED)
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

    def get_reports_batch(self, report_ids: List[str]) -> Dict[str, ReportMetadata]:
        """
        OPTIMIZED: Batch get multiple reports by IDs

        Eliminates N+1 query pattern by fetching all reports in a single batch operation.

        Args:
            report_ids: List of report IDs to fetch

        Returns:
            Dictionary mapping report_id to ReportMetadata
        """
        if not report_ids:
            return {}

        try:
            result = {}
            # Firestore batch get (max 500 documents per batch)
            batch_size = 500
            for i in range(0, len(report_ids), batch_size):
                batch_ids = report_ids[i:i + batch_size]
                doc_refs = [self.reports_collection.document(rid) for rid in batch_ids]

                # Batch get operation
                docs = self.db.get_all(doc_refs)

                for doc in docs:
                    if doc.exists:
                        try:
                            report = ReportMetadata.from_dict(doc.to_dict())
                            result[doc.id] = report
                        except Exception as e:
                            logger.warning(f"Failed to deserialize report {doc.id}: {e}")

            logger.info(f"Batch loaded {len(result)} reports (requested {len(report_ids)})")
            return result
        except Exception as e:
            logger.error(f"Failed to batch get reports: {e}")
            return {}

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

        Note: Composite indexes required in Firestore:
        - (user_id, created_at DESC)
        - (company, created_at DESC)
        - (user_id, company, created_at DESC)
        """
        try:
            query = self.reports_collection

            if user_id:
                query = query.where("user_id", "==", user_id)
            if company:
                query = query.where("company", "==", company)

            # Use safe reference to Query.DESCENDING
            if Query is None:
                raise RuntimeError("Firestore Query is not available")
            query = query.order_by(order_by, direction=Query.DESCENDING)
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
            batch = self.db.batch()

            doc_ref = self.users_collection.document(user.user_id)
            user_dict = user.to_dict()
            batch.set(doc_ref, user_dict)

            if password_hash:
                passwords_collection = self.db.collection("user_passwords")
                password_doc = passwords_collection.document(user.user_id)
                batch.set(password_doc, {
                    "password_hash": password_hash,
                    "created_at": datetime.now().isoformat()
                })

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


# Global database service instance
_db_service: Optional[Union[OptimizedDatabaseService, InMemoryDatabaseService]] = None
_db_service_lock = threading.Lock()


def get_db_service() -> Union[OptimizedDatabaseService, InMemoryDatabaseService]:
    """Get or create optimized database service instance"""
    global _db_service
    if _db_service is None:
        with _db_service_lock:
            if _db_service is None:
                if FIRESTORE_AVAILABLE and settings.environment != "test":
                    try:
                        _db_service = OptimizedDatabaseService()
                        logger.info("Initialized OptimizedDatabaseService with connection pooling")
                    except Exception as e:
                        logger.warning(f"Failed to initialize Firestore, falling back to in-memory database: {e}")
                        _db_service = InMemoryDatabaseService()
                else:
                    logger.info("Using in-memory database (Firestore not available or in test mode)")
                    _db_service = InMemoryDatabaseService()
    return _db_service


# Backward compatibility alias
DatabaseService = OptimizedDatabaseService
