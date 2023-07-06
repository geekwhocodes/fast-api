"""add impressions table

Revision ID: f006eaa3d35b
Revises: 8f622b7e3991
Create Date: 2023-06-20 21:27:11.142595

"""
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'f006eaa3d35b'
down_revision = '8f622b7e3991'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "impressions",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
        sa.Column("user_id", sa.String(256), nullable=False, index=True, unique=True),
        sa.Column("count", sa.Integer(), nullable=True),

        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), default=None, onupdate=sa.func.now()),

        schema=None,
    )

def downgrade() -> None:
    op.drop_table("impressions")

