from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from opalizer.api.geomap.models import GeoMap
from opalizer.api.tenants.models import Tenant
from opalizer.database import Base


class Event(Base):
    __tablename__ = "events"
    # REGEXP_MATCHES('', '.*[&?]zzz=([^&]+).*')
    id = sa.Column(
        "id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    latitude = sa.Column("latitude", sa.Float(), nullable=False)
    longitude = sa.Column("longitude", sa.Float(), nullable=False)
    accuracy = sa.Column("accuracy", sa.Float(), nullable=True)
    ip_addr = sa.Column("ip_addr", sa.String(64), nullable=True)
    ga_user_id = sa.Column("ga_user_id", sa.String(256), nullable=True)

    utm_source = sa.Column("utm_source", sa.String(512), nullable=True)
    utm_medium = sa.Column("utm_medium", sa.String(512), nullable=True)
    utm_campaign = sa.Column("utm_campaign", sa.String(512), nullable=True)
    utm_term = sa.Column("utm_term", sa.String(512), nullable=True)
    utm_content = sa.Column("utm_content", sa.String(512), nullable=True)

    window_location_json = sa.Column("window_location_json", sa.JSON(), nullable=True)
    browser_json = sa.Column("browser_json", sa.JSON(), nullable=True)
    address_json = sa.Column("address_json", sa.JSON(), nullable=True)

    extra_json = sa.Column("extra_json", sa.JSON(), nullable=True)

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
    # created_date = sa.Column(sa.Date(), sa.Computed("date(created_at)"))

    # __table_args__ = {
    #     'postgresql_partition_by': 'RANGE(created_date)',
    # }


class Address(Base):
    __tablename__ = "addresses"

    id = sa.Column(
        "id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    geohash = sa.Column(
        "geohash", sa.String(16), nullable=False, index=True, unique=True
    )
    geomap_id = sa.Column(
        "geomap_id", sa.UUID(), sa.ForeignKey(GeoMap.id), nullable=False
    )

    geomap = relationship(GeoMap)

    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        sa.TIMESTAMP(timezone=True), default=None, onupdate=sa.func.now()
    )


class Impression(Base):
    __tablename__ = "impressions"

    id = sa.Column(
        "id", sa.UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id = sa.Column(
        "user_id", sa.String(256), nullable=False, index=True, unique=True
    )
    count = sa.Column("count", sa.Integer(), nullable=True, default=1)

    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        sa.TIMESTAMP(timezone=True), default=None, onupdate=sa.func.now()
    )
