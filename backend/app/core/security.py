from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import utcnow_naive
from app.models.models import User, RefreshToken


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain-text password against the stored password hash.
    """

    if not plain_password or not hashed_password:
        return False

    try:
        return pwd_context.verify(
            plain_password,
            hashed_password
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Convert a plain-text password into a secure bcrypt hash.
    """

    if not password:
        raise ValueError("Password cannot be empty")

    return pwd_context.hash(password)


# ============================================================
# ACCESS TOKEN
# ============================================================

def create_access_token(
    subject: str,
    role: str = "user"
) -> str:
    """
    Create JWT access token.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(
    token: str
) -> Optional[dict]:
    """
    Decode and validate an access token.
    """

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Make sure this is an access token
        if payload.get("type") != "access":
            return None

        # Make sure subject exists
        if not payload.get("sub"):
            return None

        return payload

    except JWTError:
        return None


# ============================================================
# CURRENT USER
# ============================================================

async def get_current_user(
    token: str,
    db: AsyncSession
) -> Optional[User]:
    """
    Get the currently authenticated user from JWT token.
    """

    payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if not user:
        return None

    # Don't allow inactive users
    if hasattr(user, "is_active") and not user.is_active:
        return None

    return user


# ============================================================
# REFRESH TOKEN
# ============================================================

def create_refresh_token() -> tuple[str, str]:
    """
    Create a secure refresh token.

    Returns:
        raw_token
        hashed_token
    """

    raw_token = secrets.token_urlsafe(64)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    return raw_token, token_hash


def hash_token(token: str) -> str:
    """
    Hash refresh token before comparing/storing it.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


async def store_refresh_token(
    user_id: str,
    token_hash: str,
    db: AsyncSession
) -> RefreshToken:
    """
    Store hashed refresh token in database.
    """

    expires_at = (
        utcnow_naive()
        + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        is_revoked=False,
    )

    db.add(refresh_token)

    await db.flush()

    return refresh_token


async def validate_refresh_token(
    token_hash: str,
    db: AsyncSession
) -> Optional[RefreshToken]:
    """
    Validate refresh token.

    Checks:
    - Token exists
    - Token isn't revoked
    - Token isn't expired
    """

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
        )
    )

    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        return None

    # Handle timezone-aware and naive database datetimes
    expires_at = refresh_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at < datetime.now(timezone.utc):

        refresh_token.is_revoked = True

        await db.flush()

        return None

    return refresh_token


async def revoke_refresh_token(
    token_hash: str,
    db: AsyncSession
) -> bool:
    """
    Revoke a refresh token.
    """

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
        )
    )

    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        return False

    refresh_token.is_revoked = True

    await db.flush()

    return True

