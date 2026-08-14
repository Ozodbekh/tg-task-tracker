import secrets

from app.core.security import PasswordHasher, TokenIssuer


class AuthService:
    def __init__(self, username: str, password_hash: str, issuer: TokenIssuer) -> None:
        self._username = username
        self._password_hash = password_hash
        self._issuer = issuer

    def login(self, username: str, password: str) -> str | None:
        matches_user = secrets.compare_digest(username, self._username)
        matches_password = PasswordHasher.verify(password, self._password_hash)
        if not (matches_user and matches_password):
            return None
        return self._issuer.issue(self._username)

    def identify(self, token: str | None) -> str | None:
        if not token:
            return None
        return self._issuer.subject(token)
