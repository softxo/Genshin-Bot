import secrets
import time
from dataclasses import dataclass


VERIFICATION_TIMEOUT = 5 * 60
WEB_SESSION_TIMEOUT = 30 * 24 * 60 * 60


@dataclass
class VerificationRequest:
    token: str
    code: str
    created_at: float
    user_id: int | None = None


@dataclass
class WebSession:
    token: str
    user_id: int
    created_at: float


_verifications: dict[str, VerificationRequest] = {}
_sessions: dict[str, WebSession] = {}


def _cleanup() -> None:
    now = time.time()

    expired_verifications = [
        token
        for token, verification in _verifications.items()
        if now - verification.created_at > VERIFICATION_TIMEOUT
    ]

    for token in expired_verifications:
        _verifications.pop(token, None)

    expired_sessions = [
        token
        for token, session in _sessions.items()
        if now - session.created_at > WEB_SESSION_TIMEOUT
    ]

    for token in expired_sessions:
        _sessions.pop(token, None)


def create_verification() -> VerificationRequest:
    _cleanup()

    token = secrets.token_urlsafe(32)

    code = (
        f"{secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
        f"{secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
        f"{secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
        f"{secrets.randbelow(10)}"
        f"{secrets.randbelow(10)}"
        f"{secrets.randbelow(10)}"
    )

    verification = VerificationRequest(
        token=token,
        code=code,
        created_at=time.time(),
    )

    _verifications[token] = verification

    return verification


def get_verification(
    token: str,
) -> VerificationRequest | None:
    _cleanup()

    return _verifications.get(token)


def claim_verification(
    code: str,
    user_id: int,
) -> bool:
    _cleanup()

    code = code.strip().upper()

    for verification in _verifications.values():

        if verification.code != code:
            continue

        if verification.user_id is not None:
            return False

        verification.user_id = user_id

        return True

    return False


def create_web_session(
    user_id: int,
) -> WebSession:
    _cleanup()

    token = secrets.token_urlsafe(48)

    session = WebSession(
        token=token,
        user_id=user_id,
        created_at=time.time(),
    )

    _sessions[token] = session

    return session


def get_web_session(
    token: str | None,
) -> WebSession | None:
    if not token:
        return None

    _cleanup()

    return _sessions.get(token)


def delete_web_session(
    token: str,
) -> None:
    _sessions.pop(token, None)