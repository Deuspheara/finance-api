import json
from cryptography.fernet import Fernet
from src.core.config import settings

class EncryptionService:
    def __init__(self):
        key = settings.ENCRYPTION_KEY
        # Ensure key is 32 bytes, base64 encoded
        if len(key) != 44:  # base64 encoded 32 bytes is 44 chars
            raise ValueError("ENCRYPTION_KEY must be a base64 encoded 32-byte key")
        self.fernet = Fernet(key.encode())

    def encrypt_data(self, data: dict) -> str:
        """Encrypt a dictionary by serializing to JSON and encrypting."""
        json_str = json.dumps(data)
        return self.fernet.encrypt(json_str.encode()).decode()

    def decrypt_data(self, encrypted_str: str) -> dict:
        """Decrypt an encrypted string and deserialize to dictionary."""
        decrypted_bytes = self.fernet.decrypt(encrypted_str.encode())
        json_str = decrypted_bytes.decode()
        return json.loads(json_str)