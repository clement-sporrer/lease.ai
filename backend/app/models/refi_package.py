import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RefiPackage(Base):
    __tablename__ = "refi_packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="draft")
    financier_org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    amount_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_payment_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_band: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class FinancierDecision(Base):
    __tablename__ = "financier_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refi_package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("refi_packages.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    decision: Mapped[str] = mapped_column(String(20), nullable=False)  # "approved" | "rejected"
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True
    )
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
