import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, JSON, Enum as SAEnum, TypeDecorator, CHAR
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class GUID(TypeDecorator):
    """Portable UUID: Postgres NATIVE UUID, SQLite CHAR(36) string.
    Stores str(uuid) everywhere so `str(obj.id)` and `id == 'str'` work on both DBs."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return str(value)


def new_uuid() -> str:
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # null for OAuth users
    role = Column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    google_id = Column(String(255), unique=True, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    analyses_this_month = Column(Integer, default=0)
    analyses_month_reset = Column(DateTime, nullable=True)
    dark_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    email_verifications = relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(GUID(), primary_key=True, default=new_uuid)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(GUID(), primary_key=True, default=new_uuid)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="email_verifications")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(GUID(), primary_key=True, default=new_uuid)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="password_resets")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(GUID(), primary_key=True, default=new_uuid)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Input
    resume_filename = Column(String(500), nullable=True)
    resume_s3_key = Column(String(500), nullable=True)
    resume_text = Column(Text, nullable=True)
    job_description = Column(Text, nullable=False)
    job_title = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)

    # Results
    status = Column(SAEnum(AnalysisStatus), default=AnalysisStatus.pending, nullable=False)
    match_score = Column(Float, nullable=True)
    ats_score = Column(Float, nullable=True)
    matched_skills = Column(JSON, nullable=True)  # List[str]
    missing_skills = Column(JSON, nullable=True)   # List[str]
    extracted_entities = Column(JSON, nullable=True)  # Dict
    feedback = Column(JSON, nullable=True)  # Dict with strengths, weaknesses, suggestions
    skill_roadmap = Column(JSON, nullable=True)  # List[Dict]

    # Report
    report_s3_key = Column(String(500), nullable=True)
    report_url = Column(String(1000), nullable=True)
    report_emailed = Column(Boolean, default=False)

    # Error tracking
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="analyses")


class Resume(Base):
    """CareerLens AI — multi-resume store with versions & target role."""
    __tablename__ = "resumes"

    id = Column(GUID(), primary_key=True, default=new_uuid)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)          # resume name/label
    version = Column(Integer, default=1, nullable=False)
    target_role = Column(String(255), nullable=True)
    filename = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)               # parsed text
    entities = Column(JSON, nullable=True)
    resume_score = Column(JSON, nullable=True)          # 100-pt breakdown
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
