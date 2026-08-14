import pytest

from app.core.security import PasswordHasher, TokenIssuer
from app.services.auth import AuthService

USERNAME = "boss"
PASSWORD = "correct horse battery staple"


@pytest.fixture
def auth() -> AuthService:
    return AuthService(
        username=USERNAME,
        password_hash=PasswordHasher.hash(PASSWORD),
        issuer=TokenIssuer("secret", ttl_minutes=60),
    )


def test_login_returns_token_for_valid_credentials(auth: AuthService) -> None:
    token = auth.login(USERNAME, PASSWORD)
    assert token is not None
    assert auth.identify(token) == USERNAME


@pytest.mark.parametrize(
    ("username", "password"),
    [
        (USERNAME, "wrong"),
        ("intruder", PASSWORD),
        ("", ""),
    ],
)
def test_login_rejects_invalid_credentials(
    auth: AuthService, username: str, password: str
) -> None:
    assert auth.login(username, password) is None


def test_identify_rejects_missing_and_broken_tokens(auth: AuthService) -> None:
    assert auth.identify(None) is None
    assert auth.identify("") is None
    assert auth.identify("not-a-token") is None


def test_identify_rejects_a_token_signed_with_another_secret(
    auth: AuthService,
) -> None:
    foreign = TokenIssuer("other-secret", ttl_minutes=60).issue(USERNAME)
    assert auth.identify(foreign) is None


def test_identify_rejects_an_expired_token(auth: AuthService) -> None:
    expired = TokenIssuer("secret", ttl_minutes=-1).issue(USERNAME)
    assert auth.identify(expired) is None


def test_password_hash_is_salted() -> None:
    first = PasswordHasher.hash(PASSWORD)
    second = PasswordHasher.hash(PASSWORD)
    assert first != second
    assert PasswordHasher.verify(PASSWORD, first)
    assert not PasswordHasher.verify("other", first)


def test_verify_rejects_a_malformed_hash() -> None:
    assert not PasswordHasher.verify(PASSWORD, "garbage")
