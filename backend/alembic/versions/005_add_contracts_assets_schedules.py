# backend/alembic/versions/005_add_contracts_assets_schedules.py
"""add contracts assets payment_schedules

Revision ID: 005
Revises: 02f59637f6b5
Create Date: 2026-05-18
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "02f59637f6b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("deal_id", sa.UUID(), nullable=False),
        sa.Column("public_id", sa.String(20), nullable=False),
        sa.Column("status", sa.String(50), server_default="draft", nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_commitment_cents", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id"),
    )
    op.create_index("ix_contracts_deal_id", "contracts", ["deal_id"])

    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("contract_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("unit_value_cents", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_contract_id", "assets", ["contract_id"])

    op.create_table(
        "payment_schedules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("contract_id", sa.UUID(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payment_schedules_contract_id", "payment_schedules", ["contract_id"])


def downgrade() -> None:
    op.drop_index("ix_payment_schedules_contract_id", table_name="payment_schedules")
    op.drop_table("payment_schedules")
    op.drop_index("ix_assets_contract_id", table_name="assets")
    op.drop_table("assets")
    op.drop_index("ix_contracts_deal_id", table_name="contracts")
    op.drop_table("contracts")
