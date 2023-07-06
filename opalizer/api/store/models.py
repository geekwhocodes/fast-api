from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from opalizer.api.tenants.models import Tenant
from opalizer.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = sa.Column(
        "id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    name = sa.Column("name", sa.String(256), nullable=False, index=True, unique=True)
    owner = sa.Column("owner", sa.String(64), nullable=False, unique=True)
    latitude = sa.Column("latitude", sa.Float(), nullable=False)
    longitude = sa.Column("longitude", sa.Float(), nullable=False)
    radius = sa.Column("radius", sa.Float(), nullable=False)
    tenant_id = sa.Column(
        "tenant_id", sa.UUID(), sa.ForeignKey(Tenant.id), nullable=False
    )

    tenant = relationship(Tenant)

    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        sa.TIMESTAMP(timezone=True), default=None, onupdate=sa.func.now()
    )
