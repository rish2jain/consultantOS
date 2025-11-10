"""
Encryption and Security Module
Provides encryption for credentials and sensitive data storage
"""
import logging
import base64
import os
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Encryption service for credentials and sensitive data

    Uses Fernet (symmetric encryption) with key derivation for secure storage.
    Keys should be stored in Secret Manager in production.
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize encryption service

        Args:
            encryption_key: Encryption key (32-byte URL-safe base64-encoded).
                           If not provided, will attempt to load from environment.
        """
        if encryption_key:
            self.key = encryption_key
        else:
            # Load from environment or generate
            key_b64 = os.getenv('ENCRYPTION_KEY')
            if key_b64:
                self.key = base64.urlsafe_b64decode(key_b64)
            else:
                # Generate new key (for development only!)
                logger.warning(
                    "No ENCRYPTION_KEY found in environment. "
                    "Generating new key - DO NOT USE IN PRODUCTION!"
                )
                self.key = Fernet.generate_key()

        self.cipher = Fernet(self.key)

    @classmethod
    def generate_key(cls) -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key()

    @classmethod
    def derive_key_from_password(cls, password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2

        Args:
            password: Password to derive key from
            salt: Optional salt (will generate if not provided)

        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        return key, salt

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string

        Args:
            ciphertext: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string
        """
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def encrypt_dict(self, data: dict) -> str:
        """
        Encrypt dictionary as JSON

        Args:
            data: Dictionary to encrypt

        Returns:
            Encrypted JSON string
        """
        import json
        json_str = json.dumps(data)
        return self.encrypt(json_str)

    def decrypt_dict(self, encrypted_json: str) -> dict:
        """
        Decrypt JSON dictionary

        Args:
            encrypted_json: Encrypted JSON string

        Returns:
            Decrypted dictionary
        """
        import json
        json_str = self.decrypt(encrypted_json)
        return json.loads(json_str)


# Singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create encryption service singleton"""
    global _encryption_service

    if _encryption_service is None:
        _encryption_service = EncryptionService()

    return _encryption_service


def encrypt_credentials(credentials_json: str) -> str:
    """
    Convenience function to encrypt credentials

    Args:
        credentials_json: JSON string of credentials

    Returns:
        Encrypted credentials string
    """
    service = get_encryption_service()
    return service.encrypt(credentials_json)


def decrypt_credentials(encrypted_credentials: str) -> str:
    """
    Convenience function to decrypt credentials

    Args:
        encrypted_credentials: Encrypted credentials string

    Returns:
        Decrypted JSON credentials string
    """
    service = get_encryption_service()
    return service.decrypt(encrypted_credentials)
