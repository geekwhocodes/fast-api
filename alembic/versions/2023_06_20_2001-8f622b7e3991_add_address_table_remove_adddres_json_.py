"""add address table remove adddres_json col

Revision ID: 8f622b7e3991
Revises: 0c987e7a1c6f
Create Date: 2023-06-20 20:01:57.374488

"""
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '8f622b7e3991'
down_revision = '0c987e7a1c6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "addresses",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
        sa.Column("geohash", sa.String(16), nullable=False, index=True, unique=True),
        sa.Column("geomap_id", sa.UUID(), sa.ForeignKey("public.geomaps.id"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), default=None, onupdate=sa.func.now()),

        schema=None,
    )

    op.drop_column("events", "address_json")

def downgrade() -> None:
    op.drop_table("addresses")
    op.add_column("events", sa.Column("address_json", sa.JSON(), nullable=True))

