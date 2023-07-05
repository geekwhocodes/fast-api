"""add address json col to events

Revision ID: b4889af110bd
Revises: fe9f935ba177
Create Date: 2023-06-19 12:30:31.135266

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b4889af110bd'
down_revision = 'fe9f935ba177'
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column("events", sa.Column("address_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("events", "address_json")
