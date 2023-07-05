from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.sql import func

from opalizer.shared_models import Base


class GeoMap(Base):
    __tablename__ = "geomaps"

    id = sa.Column(
        "id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    geohash = sa.Column(
        "geohash", sa.String(16), nullable=False, index=True, unique=True
    )
    latitude = sa.Column("latitude", sa.Float(), nullable=False)
    longitude = sa.Column("longitude", sa.Float(), nullable=False)
    address = sa.Column("address", sa.JSON(), nullable=False)

    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = sa.Column(
        sa.TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )

    __table_args__ = {"schema": "public"}
