import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt

ALGORITHM = "HS256"
SCHEME = "scrypt"
SALT_BYTES = 16
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


class PasswordHasher:
    @classmethod
    def hash(cls, password: str) -> str:
        salt = secrets.token_bytes(SALT_BYTES)
        return f"{SCHEME}${salt.hex()}${cls._derive(password, salt).hex()}"

    @classmethod
    def verify(cls, password: str, encoded: str) -> bool:
        try:
            scheme, salt_hex, digest_hex = encoded.split("$")
        except ValueError:
            return False
        if scheme != SCHEME:
            return False
        expected = cls._derive(password, bytes.fromhex(salt_hex))
        return secrets.compare_digest(expected, bytes.fromhex(digest_hex))

    @staticmethod
    def _derive(password: str, salt: bytes) -> bytes:
        return hashlib.scrypt(
            password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P
        )


class TokenIssuer:
    def __init__(self, secret: str, ttl_minutes: int) -> None:
        self._secret = secret
        self._ttl = timedelta(minutes=ttl_minutes)

    def issue(self, subject: str) -> str:
        now = datetime.now(UTC)
        payload = {"sub": subject, "iat": now, "exp": now + self._ttl}
        return jwt.encode(payload, self._secret, algorithm=ALGORITHM)

    def subject(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            return None
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None
