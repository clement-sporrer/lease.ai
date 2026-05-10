import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PricingProposal(Base):
    __tablename__ = "pricing_proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="indicative")
    amount_financed_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_payment_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    residual_value_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    refi_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    margin_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    fees_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    assumptions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
