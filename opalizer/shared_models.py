import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = sa.MetaData(
    naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION, schema="shared"
)
Base = declarative_base(metadata=metadata)
