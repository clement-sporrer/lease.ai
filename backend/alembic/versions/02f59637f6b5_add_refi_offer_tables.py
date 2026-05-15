"""add_refi_offer_tables

Revision ID: 02f59637f6b5
Revises: 003
Create Date: 2026-05-15 15:24:58.592363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02f59637f6b5'
down_revision: Union[str, Sequence[str], None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # CREATE TABLE offers
    op.create_table(
        'offers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('deal_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('amount_cents', sa.BigInteger(), nullable=True),
        sa.Column('duration_months', sa.Integer(), nullable=True),
        sa.Column('monthly_payment_cents', sa.BigInteger(), nullable=True),
        sa.Column('risk_band', sa.String(length=20), nullable=True),
        sa.Column('currency', sa.String(length=3), server_default='EUR', nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_offers_deal_id'), 'offers', ['deal_id'], unique=False)

    # CREATE TABLE refi_packages
    op.create_table(
        'refi_packages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('deal_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='draft', nullable=False),
        sa.Column('financier_org_id', sa.UUID(), nullable=True),
        sa.Column('amount_cents', sa.BigInteger(), nullable=True),
        sa.Column('duration_months', sa.Integer(), nullable=True),
        sa.Column('monthly_payment_cents', sa.BigInteger(), nullable=True),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('risk_band', sa.String(length=20), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['financier_org_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_refi_packages_deal_id'), 'refi_packages', ['deal_id'], unique=False)

    # CREATE TABLE financier_decisions
    op.create_table(
        'financier_decisions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('refi_package_id', sa.UUID(), nullable=False),
        sa.Column('decision', sa.String(length=20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('decided_by_user_id', sa.UUID(), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("decision IN ('approved', 'rejected')", name='ck_financier_decision_value'),
        sa.ForeignKeyConstraint(['decided_by_user_id'], ['profiles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['refi_package_id'], ['refi_packages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('refi_package_id'),
    )

    # ALTER TABLE quotes ADD COLUMN extraction_source
    op.add_column('quotes', sa.Column('extraction_source', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('quotes', 'extraction_source')
    op.drop_table('financier_decisions')
    op.drop_index(op.f('ix_refi_packages_deal_id'), table_name='refi_packages')
    op.drop_table('refi_packages')
    op.drop_index(op.f('ix_offers_deal_id'), table_name='offers')
    op.drop_table('offers')
