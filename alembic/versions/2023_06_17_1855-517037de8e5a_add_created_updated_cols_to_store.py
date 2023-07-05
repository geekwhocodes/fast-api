"""add created updated cols to store

Revision ID: 517037de8e5a
Revises: a86ce123173a
Create Date: 2023-06-17 18:55:49.068289

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '517037de8e5a'
down_revision = 'a86ce123173a'
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column("stores",
                  sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                            nullable=False, server_default=sa.func.now()
    ))

    op.add_column("stores",
                  sa.Column("updated_at", sa.TIMESTAMP(timezone=True),
                                      default=None, onupdate=sa.func.now()))

def downgrade() -> None:
    op.drop_column("stores", "created_at")
    op.drop_column("stores", "updated_at")
