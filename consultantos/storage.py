"""
Cloud Storage integration for ConsultantOS
"""
import logging
import threading
import os
from typing import Optional, Union
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from google.cloud import storage
    from google.api_core import exceptions as google_exceptions
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    storage = None
    google_exceptions = None

from consultantos.config import settings

logger = logging.getLogger(__name__)


if STORAGE_AVAILABLE:
    class StorageService:
        """Service for managing PDF reports in Cloud Storage"""
        
        def __init__(self, bucket_name: str = "consultantos-reports"):
            self.bucket_name = bucket_name
            self._client: Optional[storage.Client] = None
            self._bucket: Optional[storage.Bucket] = None
        
        def _get_client(self) -> storage.Client:
            """Get or create storage client"""
            if self._client is None:
                try:
                    self._client = storage.Client(project=settings.gcp_project_id)
                except Exception as e:
                    logger.warning(f"Failed to initialize storage client: {e}")
                    raise
            return self._client
        
        def _get_bucket(self) -> storage.Bucket:
            """Get or create bucket"""
            if self._bucket is None:
                client = self._get_client()
                try:
                    self._bucket = client.bucket(self.bucket_name)
                    # Check if bucket exists, create if it doesn't
                    if not self._bucket.exists():
                        try:
                            # Attempt to create bucket (requires proper GCP permissions)
                            self._bucket.create()
                            logger.info(f"Created bucket: {self.bucket_name}")
                        except google_exceptions.Conflict:
                            # Bucket was created by another process
                            logger.debug(f"Bucket {self.bucket_name} already exists")
                        except Exception as create_error:
                            # If bucket creation fails (e.g., no permissions, bucket doesn't exist in project)
                            # This will be caught by the calling code and fall back to local storage
                            logger.warning(f"Failed to create bucket {self.bucket_name}: {create_error}")
                            raise
                    else:
                        logger.debug(f"Bucket {self.bucket_name} exists")
                except Exception as e:
                    logger.error(f"Failed to access bucket {self.bucket_name}: {e}")
                    raise
            return self._bucket
        
        def upload_pdf(self, report_id: str, pdf_bytes: bytes, content_type: str = "application/pdf") -> str:
            """
            Upload PDF to Cloud Storage
            
            Args:
                report_id: Unique report identifier
                pdf_bytes: PDF file bytes
                content_type: Content type (default: application/pdf)
            
            Returns:
                Public URL of uploaded file
            """
            try:
                bucket = self._get_bucket()
                blob = bucket.blob(f"{report_id}.pdf")
                
                # Set metadata
                blob.metadata = {
                    "report_id": report_id,
                    "uploaded_at": datetime.now(timezone.utc).isoformat(),
                    "content_type": content_type
                }
                
                # Upload (files are private by default)
                blob.upload_from_string(pdf_bytes, content_type=content_type)
                
                # Generate signed URL for access (files are private, access via signed URLs)
                signed_url = self.generate_signed_url(report_id)
                logger.info(f"Uploaded PDF: {report_id} (private, access via signed URL)")
                
                return signed_url
            
            except Exception as e:
                logger.error(f"Failed to upload PDF {report_id}: {e}", exc_info=True)
                raise
        
        def generate_signed_url(
            self,
            report_id: str,
            expiration_hours: int = 24,
            method: str = "GET"
        ) -> str:
            """
            Generate signed URL for secure access
            
            Args:
                report_id: Report identifier
                expiration_hours: URL expiration time in hours
                method: HTTP method (GET, PUT, etc.)
            
            Returns:
                Signed URL
            """
            try:
                bucket = self._get_bucket()
                blob = bucket.blob(f"{report_id}.pdf")
                
                expiration = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
                
                signed_url = blob.generate_signed_url(
                    expiration=expiration,
                    method=method,
                    version="v4"
                )
                
                logger.info(f"Generated signed URL for {report_id} (expires in {expiration_hours}h)")
                
                return signed_url
            
            except Exception as e:
                logger.error(f"Failed to generate signed URL for {report_id}: {e}", exc_info=True)
                raise
        
        def get_report_url(self, report_id: str, use_signed_url: bool = False) -> Optional[str]:
            """
            Get URL for a report
            
            Args:
                report_id: Report identifier
                use_signed_url: Whether to use signed URL (more secure).
                    If False, returns public URL (requires blob to be publicly accessible).
                    If True, returns signed URL (works even for private blobs).
            
            Returns:
                Report URL or None if not found
            """
            bucket = self._get_bucket()
            blob = bucket.blob(f"{report_id}.pdf")
            
            if not blob.exists():
                return None
            
            if use_signed_url:
                return self.generate_signed_url(report_id)
            else:
                # Return public URL (requires blob to be publicly accessible)
                return blob.public_url
        
        def delete_report(self, report_id: str) -> bool:
            """
            Delete a report from storage
            
            Args:
                report_id: Report identifier
            
            Returns:
                True if deleted, False if not found
            """
            try:
                bucket = self._get_bucket()
                blob = bucket.blob(f"{report_id}.pdf")
                
                if blob.exists():
                    blob.delete()
                    logger.info(f"Deleted report: {report_id}")
                    return True
                else:
                    logger.warning(f"Report not found: {report_id}")
                    return False
            
            except Exception as e:
                logger.error(f"Failed to delete report {report_id}: {e}", exc_info=True)
                return False
        
        def report_exists(self, report_id: str) -> bool:
            """Check if report exists in storage"""
            try:
                bucket = self._get_bucket()
                blob = bucket.blob(f"{report_id}.pdf")
                return blob.exists()
            except Exception as e:
                logger.error(f"Failed to check report existence {report_id}: {e}")
                return False
else:
    # Dummy class when storage is not available
    class StorageService:
        """Dummy storage service when Google Cloud Storage is not available"""
        pass


class LocalFileStorageService:
    """Local file-based storage service for development/testing"""
    
    def __init__(self, storage_dir: str = "Temp/reports"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using local file storage at {self.storage_dir.absolute()}")
    
    def upload_pdf(self, report_id: str, pdf_bytes: bytes, content_type: str = "application/pdf") -> str:
        """Save PDF to local file system"""
        file_path = self.storage_dir / f"{report_id}.pdf"
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        logger.info(f"Saved PDF locally: {file_path}")
        # Return file:// URL for local access
        return f"file://{file_path.absolute()}"
    
    def generate_signed_url(self, report_id: str, expiration_hours: int = 24, method: str = "GET") -> str:
        """Generate local file URL (no signing needed for local files)"""
        file_path = self.storage_dir / f"{report_id}.pdf"
        return f"file://{file_path.absolute()}"
    
    def get_report_url(self, report_id: str, use_signed_url: bool = False) -> Optional[str]:
        """Get local file URL"""
        file_path = self.storage_dir / f"{report_id}.pdf"
        if file_path.exists():
            return f"file://{file_path.absolute()}"
        return None
    
    def delete_report(self, report_id: str) -> bool:
        """Delete local file"""
        file_path = self.storage_dir / f"{report_id}.pdf"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted local report: {report_id}")
            return True
        return False
    
    def report_exists(self, report_id: str) -> bool:
        """Check if local file exists"""
        file_path = self.storage_dir / f"{report_id}.pdf"
        return file_path.exists()


# Global storage service instance
_storage_service: Optional[Union[StorageService, LocalFileStorageService]] = None
_storage_service_lock = threading.Lock()

def get_storage_service() -> Union[StorageService, LocalFileStorageService]:
    """Get or create storage service instance (thread-safe)"""
    global _storage_service
    if _storage_service is None:
        with _storage_service_lock:
            # Double-checked locking pattern
            if _storage_service is None:
                if STORAGE_AVAILABLE and settings.environment != "test":
                    try:
                        # Try to initialize Cloud Storage
                        service = StorageService()
                        # Test bucket access by trying to get the bucket (this will fail if bucket doesn't exist or no permissions)
                        try:
                            service._get_bucket()
                            _storage_service = service
                            logger.info(f"Using Cloud Storage with bucket: {service.bucket_name}")
                        except Exception as bucket_error:
                            # Bucket access failed, fall back to local storage
                            logger.warning(f"Cloud Storage bucket access failed, falling back to local storage: {bucket_error}")
                            _storage_service = LocalFileStorageService()
                    except Exception as e:
                        logger.warning(f"Failed to initialize Cloud Storage, falling back to local storage: {e}")
                        _storage_service = LocalFileStorageService()
                else:
                    logger.info("Using local file storage (Cloud Storage not available or in test mode)")
                    _storage_service = LocalFileStorageService()
    return _storage_service

