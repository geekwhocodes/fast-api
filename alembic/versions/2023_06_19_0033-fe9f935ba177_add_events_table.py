"""add events table

Revision ID: fe9f935ba177
Revises: 517037de8e5a
Create Date: 2023-06-19 00:33:38.768186

"""
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "fe9f935ba177"
down_revision = "517037de8e5a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("events",
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
    sa.Column("latitude", sa.Float(), nullable=False),
    sa.Column("longitude", sa.Float(), nullable=False),
    sa.Column("accuracy", sa.Float(), nullable=True),
    sa.Column("ip_addr", sa.String(length=64), nullable=True),
    sa.Column("ga_user_id", sa.String(length=256), nullable=True),
    sa.Column("utm_medium", sa.String(length=512), nullable=True),
    sa.Column("utm_source", sa.String(length=512), nullable=True),
    sa.Column("utm_campaign", sa.String(length=512), nullable=True),
    sa.Column("utm_term", sa.String(length=512), nullable=True),
    sa.Column("utm_content", sa.String(length=512), nullable=True),
    sa.Column("window_location_json", sa.JSON(), nullable=True),
    sa.Column("browser_json", sa.JSON(), nullable=True),
    sa.Column("tenant_id", sa.UUID(), nullable=False),
    sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
    #sa.Column('created_date', sa.Date(), sa.Computed('created_at::timestamp::date', ), nullable=True),

    sa.ForeignKeyConstraint(["tenant_id"], ["public.tenants.id"], name=op.f("events_tenant_id_fkey")),
    sa.PrimaryKeyConstraint("id", name=op.f("events_pkey")),
    schema=None,
    #postgresql_partition_by='RANGE(created_date)'
    )


def downgrade() -> None:
    op.drop_table("events")
