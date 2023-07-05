"""add extra json col to events

Revision ID: 0c987e7a1c6f
Revises: b4889af110bd
Create Date: 2023-06-20 13:26:40.452713

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '0c987e7a1c6f'
down_revision = 'b4889af110bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("extra_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("events", "extra_json")
