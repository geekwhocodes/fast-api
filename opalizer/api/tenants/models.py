from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.sql import func

from opalizer.shared_models import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = sa.Column(
        "id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    name = sa.Column("name", sa.String(256), nullable=False, index=True, unique=True)
    schema = sa.Column("schema", sa.String(64), nullable=False, unique=True)
    slug = sa.Column("slug", sa.String(32), nullable=False, unique=True)
    api_key = sa.Column(
        "api_key", sa.String(256), nullable=True, index=True, unique=True
    )

    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = sa.Column(
        sa.TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )

    __table_args__ = {"schema": "public"}
