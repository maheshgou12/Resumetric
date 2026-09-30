# ============================================================
# Authentication API routes
# ============================================================

import secrets
from datetime import datetime, timedelta, timezone

import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db, utcnow_naive
from app.core.deps import get_current_user
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    hash_token,
    validate_refresh_token,
    revoke_refresh_token,
    store_refresh_token,
)
from app.models.models import (
    User,
    RefreshToken,
    EmailVerification,
    PasswordReset,
)
from app.services.email_service import (
    send_verification_email,
    send_password_reset_email,
    send_google_only_info_email,
    is_email_configured,
)
import logging
import time

log = logging.getLogger(__name__)


router = APIRouter()

REFRESH_COOKIE_NAME = "refresh_token"

# Simple in-memory throttle for forgot-password (per-email 60s) to stop email bombing.
# (Resets on restart — use Redis in production for multi-worker.)
_FORGOT_LAST_HIT: dict[str, float] = {}
_FORGOT_COOLDOWN_S = 60


async def _users_by_email(db: AsyncSession, email: str) -> list:
    """Case-insensitive email lookup — 'User@x.com' and 'user@x.com' are the same account."""
    result = await db.execute(
        select(User).where(func.lower(User.email) == (email or "").strip().lower())
    )
    return list(result.scalars().all())


@router.get("/email-status")
async def email_status():
    """Public: tells frontend whether real emails are configured (no user info)."""
    return {"resend_configured": is_email_configured()}


# ============================================================
# SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError(
                "Password must be at least 8 characters"
            )

        if not any(c.isupper() for c in v):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not any(c.isdigit() for c in v):
            raise ValueError(
                "Password must contain at least one digit"
            )

        return v

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Full name is required")

        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError(
                "Password must be at least 8 characters"
            )

        if not any(c.isupper() for c in v):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not any(c.isdigit() for c in v):
            raise ValueError(
                "Password must contain at least one digit"
            )

        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ============================================================
# HELPERS
# ============================================================

def set_refresh_cookie(
    response: Response,
    raw_token: str,
):
    """
    Store refresh token in an HttpOnly cookie.
    """

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )


def user_to_dict(user: User) -> dict:
    """
    Convert User model to JSON-safe dictionary.
    """

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_verified": user.is_verified,
        "avatar_url": user.avatar_url,
        "dark_mode": user.dark_mode,
        "analyses_this_month": user.analyses_this_month,
        "created_at": (
            user.created_at.isoformat()
            if user.created_at
            else None
        ),
    }


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    # --------------------------------------------------------
    # Check existing email (case-insensitive)
    # --------------------------------------------------------

    existing_users = await _users_by_email(db, body.email)

    if existing_users:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    user = User(
        email=body.email.strip(),
        full_name=body.full_name,
        hashed_password=get_password_hash(body.password),
        is_verified=False,
    )

    db.add(user)

    await db.flush()

    # --------------------------------------------------------
    # Email verification token
    # --------------------------------------------------------

    verification_token = secrets.token_urlsafe(32)

    email_verification = EmailVerification(
        user_id=user.id,
        token=verification_token,
        expires_at=(
            utcnow_naive()
            + timedelta(hours=24)
        ),
        is_used=False,
    )

    db.add(email_verification)

    await db.commit()

    # --------------------------------------------------------
    # Send verification email (real via Resend when configured)
    # --------------------------------------------------------

    sent = send_verification_email(
        body.email,
        body.full_name,
        verification_token,
    )
    if not sent:
        log.warning("Verification email NOT sent to %s (Resend unconfigured)", body.email)

    # --------------------------------------------------------
    # Local development link
    # --------------------------------------------------------

    if not is_email_configured():
        verify_url = (
            f"{settings.FRONTEND_URL}"
            f"/verify-email?token={verification_token}"
        )

        print("\n" + "=" * 70)
        print("[LOCAL EMAIL VERIFICATION — Resend not configured]")
        print(f"Email: {body.email}")
        print(f"Verify URL: {verify_url}")
        print("Expires in: 24 hours")
        print("To send REAL mail: set RESEND_API_KEY + EMAIL_FROM in backend/.env")
        print("=" * 70 + "\n")

    # --------------------------------------------------------
    # Login immediately after registration
    # --------------------------------------------------------

    access_token = create_access_token(
        str(user.id),
        user.role.value,
    )

    raw_refresh, hashed_refresh = (
        create_refresh_token()
    )

    await store_refresh_token(
        str(user.id),
        hashed_refresh,
        db,
    )

    await db.commit()

    set_refresh_cookie(
        response,
        raw_refresh,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Login using email and password.
    """

    # --------------------------------------------------------
    # Find user (case-insensitive — try every password match)
    # --------------------------------------------------------

    candidates = await _users_by_email(db, body.email)

    user = None
    for c in candidates:
        if not c.hashed_password:
            continue
        try:
            if verify_password(body.password, c.hashed_password):
                user = c
                break
        except Exception as e:
            print(f"[auth] Password verification error: {e}")

    # --------------------------------------------------------
    # No password matched
    # --------------------------------------------------------

    if not user:
        if any(not c.hashed_password for c in candidates):
            raise HTTPException(
                status_code=401,
                detail=(
                    "This account does not have a password. "
                    "Please use Google login."
                ),
            )
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # --------------------------------------------------------
    # Check active account
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated",
        )

    # --------------------------------------------------------
    # Create access token
    # --------------------------------------------------------

    access_token = create_access_token(
        str(user.id),
        user.role.value,
    )

    # --------------------------------------------------------
    # Create refresh token
    # --------------------------------------------------------

    raw_refresh, hashed_refresh = (
        create_refresh_token()
    )

    await store_refresh_token(
        str(user.id),
        hashed_refresh,
        db,
    )

    await db.commit()

    # --------------------------------------------------------
    # Set cookie
    # --------------------------------------------------------

    set_refresh_cookie(
        response,
        raw_refresh,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


# ============================================================
# GOOGLE LOGIN
# ============================================================

@router.post("/google")
async def google_login(
    body: GoogleLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify Google ID token and issue application JWT.
    """

    async with httpx.AsyncClient() as client:

        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={
                "id_token": body.id_token
            },
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token",
        )

    google_data = resp.json()

    # --------------------------------------------------------
    # Verify audience
    # --------------------------------------------------------

    if google_data.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=401,
            detail="Token audience mismatch",
        )

    google_id = google_data.get("sub")
    email = google_data.get("email")
    name = google_data.get("name", "")
    avatar = google_data.get("picture", "")

    if not google_id or not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google account information",
        )

    # --------------------------------------------------------
    # Find by Google ID
    # --------------------------------------------------------

    result = await db.execute(
        select(User).where(
            User.google_id == google_id
        )
    )

    user = result.scalar_one_or_none()

    # --------------------------------------------------------
    # If not found, try email
    # --------------------------------------------------------

    if not user:

        matches = await _users_by_email(db, email)

        user = matches[0] if matches else None

    # --------------------------------------------------------
    # Create new Google user
    # --------------------------------------------------------

    if not user:

        user = User(
            email=email.strip(),
            full_name=name,
            google_id=google_id,
            avatar_url=avatar,
            is_verified=True,
        )

        db.add(user)

        await db.flush()

    else:

        user.google_id = google_id
        user.avatar_url = avatar

        if not user.is_verified:
            user.is_verified = True

    # --------------------------------------------------------
    # Create tokens
    # --------------------------------------------------------

    access_token = create_access_token(
        str(user.id),
        user.role.value,
    )

    raw_refresh, hashed_refresh = (
        create_refresh_token()
    )

    await store_refresh_token(
        str(user.id),
        hashed_refresh,
        db,
    )

    await db.commit()

    set_refresh_cookie(
        response,
        raw_refresh,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get(
        REFRESH_COOKIE_NAME
    )

    if not raw_token:
        raise HTTPException(
            status_code=401,
            detail="No refresh token",
        )

    token_hash = hash_token(raw_token)

    rt = await validate_refresh_token(
        token_hash,
        db,
    )

    if not rt:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    result = await db.execute(
        select(User).where(
            User.id == rt.user_id
        )
    )

    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
        )

    # --------------------------------------------------------
    # Rotate refresh token
    # --------------------------------------------------------

    await revoke_refresh_token(
        token_hash,
        db,
    )

    new_access_token = create_access_token(
        str(user.id),
        user.role.value,
    )

    raw_refresh, hashed_refresh = (
        create_refresh_token()
    )

    await store_refresh_token(
        str(user.id),
        hashed_refresh,
        db,
    )

    await db.commit()

    set_refresh_cookie(
        response,
        raw_refresh,
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get(
        REFRESH_COOKIE_NAME
    )

    if raw_token:

        token_hash = hash_token(
            raw_token
        )

        await revoke_refresh_token(
            token_hash,
            db,
        )

        await db.commit()

    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path="/api/v1/auth",
    )

    return {
        "message": "Logged out successfully"
    }


# ============================================================
# VERIFY EMAIL
# ============================================================

@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailVerification).where(
            EmailVerification.token == token,
            EmailVerification.is_used == False,
        )
    )

    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification link",
        )

    expires_at = verification.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at < datetime.now(timezone.utc):

        verification.is_used = True

        await db.commit()

        raise HTTPException(
            status_code=400,
            detail="Verification link has expired",
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user_result = await db.execute(
        select(User).where(
            User.id == verification.user_id
        )
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="User account not found",
        )

    user.is_verified = True
    verification.is_used = True

    await db.commit()

    return {
        "message": "Email verified successfully"
    }


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a password reset link.

    Always returns 200 so attackers cannot discover
    whether an email exists.
    """

    # Throttle: max 1 request per email per 60s (anti email-bomb)
    key = body.email.strip().lower()
    now = time.monotonic()
    last = _FORGOT_LAST_HIT.get(key, 0)
    if now - last < _FORGOT_COOLDOWN_S:
        return {
            "message": (
                "If an account with that email exists, "
                "a reset link has been sent"
            )
        }
    _FORGOT_LAST_HIT[key] = now

    # Case-insensitive: ALL accounts with this email get mail —
    # password accounts get a reset link, Google-only accounts get
    # a "use Google login" info mail. Unknown emails stay silent (200).
    users = await _users_by_email(db, body.email)

    for user in users:
        if user.hashed_password:

            # ------------------------------------------------
            # Generate secure reset token
            # ------------------------------------------------

            token = secrets.token_urlsafe(32)

            expires_at = (
                utcnow_naive()
                + timedelta(minutes=15)
            )

            password_reset = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=expires_at,
                is_used=False,
            )

            db.add(password_reset)

            await db.commit()

            # ------------------------------------------------
            # Send REAL reset email via Resend (when configured)
            # ------------------------------------------------

            sent = send_password_reset_email(
                user.email,
                user.full_name,
                token,
            )
            if sent:
                log.info("Password reset email sent to %s", user.email)
            else:
                log.warning(
                    "Password reset email NOT sent to %s "
                    "(Resend unconfigured — see server log link below)",
                    user.email,
                )

            # ------------------------------------------------
            # Local fallback: print link to server log
            # ------------------------------------------------

            if not is_email_configured():

                reset_url = (
                    f"{settings.FRONTEND_URL}"
                    f"/reset-password?token={token}"
                )

                print("\n" + "=" * 70)
                print("[LOCAL PASSWORD RESET — Resend not configured]")
                print(f"Email: {user.email}")
                print(f"Reset URL: {reset_url}")
                print("Expires in: 15 minutes")
                print("To send REAL mail: set RESEND_API_KEY + EMAIL_FROM in backend/.env")
                print("=" * 70 + "\n")

        else:
            # Google-only account — tell them there is no password
            mailed = send_google_only_info_email(user.email, user.full_name)
            log.info(
                "Google-only reset info mail to %s: %s", user.email,
                "sent" if mailed else "skipped (Resend unconfigured)",
            )

    return {
        "message": (
            "If an account with that email exists, "
            "a reset link has been sent"
        )
    }


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using a valid reset token.
    """

    # --------------------------------------------------------
    # Find token
    # --------------------------------------------------------

    result = await db.execute(
        select(PasswordReset).where(
            PasswordReset.token == body.token,
            PasswordReset.is_used == False,
        )
    )

    password_reset = result.scalar_one_or_none()

    if not password_reset:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset link",
        )

    # --------------------------------------------------------
    # Check expiration
    # --------------------------------------------------------

    expires_at = password_reset.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at < datetime.now(timezone.utc):

        password_reset.is_used = True

        await db.commit()

        raise HTTPException(
            status_code=400,
            detail="Reset link has expired (15 min limit)",
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user_result = await db.execute(
        select(User).where(
            User.id == password_reset.user_id
        )
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="User account not found",
        )

    # --------------------------------------------------------
    # Password validation
    # --------------------------------------------------------

    if len(body.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters",
        )

    if not any(
        c.isupper()
        for c in body.new_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter",
        )

    if not any(
        c.isdigit()
        for c in body.new_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one digit",
        )

    # --------------------------------------------------------
    # HASH NEW PASSWORD
    # --------------------------------------------------------

    user.hashed_password = get_password_hash(
        body.new_password
    )

    # --------------------------------------------------------
    # Make reset token unusable
    # --------------------------------------------------------

    password_reset.is_used = True

    await db.commit()

    return {
        "message": "Password reset successfully"
    }


# ============================================================
# RESEND VERIFICATION
# ============================================================

@router.post("/resend-verification")
async def resend_verification(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send another email verification link.
    """

    if current_user.is_verified:
        return {
            "message": "Email already verified"
        }

    token = secrets.token_urlsafe(32)

    email_verification = EmailVerification(
        user_id=current_user.id,
        token=token,
        expires_at=(
            utcnow_naive()
            + timedelta(hours=24)
        ),
        is_used=False,
    )

    db.add(email_verification)

    await db.commit()

    sent = send_verification_email(
        current_user.email,
        current_user.full_name,
        token,
    )
    if not sent:
        log.warning("Verification email NOT sent to %s (Resend unconfigured)", current_user.email)

    if not is_email_configured():

        verify_url = (
            f"{settings.FRONTEND_URL}"
            f"/verify-email?token={token}"
        )

        print("\n" + "=" * 70)
        print("[LOCAL EMAIL VERIFICATION — Resend not configured]")
        print(f"Email: {current_user.email}")
        print(f"Verify URL: {verify_url}")
        print("Expires in: 24 hours")
        print("To send REAL mail: set RESEND_API_KEY + EMAIL_FROM in backend/.env")
        print("=" * 70 + "\n")

    return {
        "message": "Verification email sent"
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return user_to_dict(current_user)



