"""add stores table

Revision ID: a86ce123173a
Revises: 192b914e7f19
Create Date: 2023-06-17 14:04:05.472483

"""
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'a86ce123173a'
down_revision = '192b914e7f19'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'stores',
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
        sa.Column("name", sa.String(256), nullable=False, index=True, unique=True),
        sa.Column("owner", sa.String(64), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("radius", sa.Float(), nullable=False),

        sa.Column("tenant_id", sa.UUID() ,sa.ForeignKey("public.tenants.id"), nullable=False),

        schema=None,
    )

def downgrade():
    op.drop_table('stores', schema=None)
