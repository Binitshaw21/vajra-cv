import hashlib
import hmac
import os
from dataclasses import dataclass


@dataclass
class KMSProvider:
    kms_key_id: str = "local-kms-key"
    secret: str | None = None

    def __post_init__(self):
        self.secret = self.secret or os.getenv("VAJRA_KMS_MASTER_SECRET")
        if not self.secret:
            raise RuntimeError("VAJRA_KMS_MASTER_SECRET is required")

    @property
    def key_id(self) -> str:
        return self.kms_key_id

    def sign(self, payload: bytes) -> str:
        signing_key = hashlib.sha256(f"{self.kms_key_id}:{self.secret}".encode("utf-8")).digest()
        return hmac.new(signing_key, payload, hashlib.sha256).hexdigest()

    def verify(self, payload: bytes, signature: str) -> bool:
        return hmac.compare_digest(self.sign(payload), signature)
