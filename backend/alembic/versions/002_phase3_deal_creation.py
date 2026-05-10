# backend/alembic/versions/002_phase3_deal_creation.py
"""phase3_deal_creation

Revision ID: 002
Revises: 001
Create Date: 2026-05-10
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending_upload", nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("validated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("supplier_name", sa.String(255), nullable=True),
        sa.Column("quote_number", sa.String(100), nullable=True),
        sa.Column("amount_excl_tax_cents", sa.BigInteger(), nullable=True),
        sa.Column("amount_incl_tax_cents", sa.BigInteger(), nullable=True),
        sa.Column("currency", sa.String(3), server_default="EUR", nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("extraction_status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("extraction_payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quote_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("unit_price_cents", sa.BigInteger(), nullable=True),
        sa.Column("total_price_cents", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "risk_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("band", sa.String(20), nullable=False),
        sa.Column("flags", postgresql.JSONB(), nullable=True),
        sa.Column("rules_applied", postgresql.JSONB(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pricing_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(20), server_default="indicative", nullable=False),
        sa.Column("amount_financed_cents", sa.BigInteger(), nullable=False),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("monthly_payment_cents", sa.BigInteger(), nullable=False),
        sa.Column("residual_value_cents", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("refi_rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("margin_rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("fees_cents", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("assumptions", postgresql.JSONB(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


    # FK indexes
    op.create_index("ix_documents_deal_id", "documents", ["deal_id"])
    op.create_index("ix_quotes_deal_id", "quotes", ["deal_id"])
    op.create_index("ix_quote_items_quote_id", "quote_items", ["quote_id"])
    op.create_index("ix_risk_assessments_deal_id", "risk_assessments", ["deal_id"])
    op.create_index("ix_pricing_proposals_deal_id", "pricing_proposals", ["deal_id"])

    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN NEW.updated_at = now(); RETURN NEW; END;
        $$;
        CREATE TRIGGER quotes_set_updated_at
            BEFORE UPDATE ON quotes
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS quotes_set_updated_at ON quotes;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at;")

    op.drop_index("ix_pricing_proposals_deal_id", table_name="pricing_proposals")
    op.drop_index("ix_risk_assessments_deal_id", table_name="risk_assessments")
    op.drop_index("ix_quote_items_quote_id", table_name="quote_items")
    op.drop_index("ix_quotes_deal_id", table_name="quotes")
    op.drop_index("ix_documents_deal_id", table_name="documents")

    op.drop_table("pricing_proposals")
    op.drop_table("risk_assessments")
    op.drop_table("quote_items")
    op.drop_table("quotes")
    op.drop_table("documents")
