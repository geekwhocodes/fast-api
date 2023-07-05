import argparse
import logging
import os
import sys
from typing import List, Union

import asyncpg.exceptions as pgexec
import sqlalchemy as sa
from sqlalchemy import UUID, select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from alembic import command
from alembic.config import Config
from opalizer.api.tenants.models import Tenant
from opalizer.api.tenants.schemas import TenantSchema
from opalizer.api.tenants.utils import generate_tenant_schema_name, slugify
from opalizer.auth.utils import generate_api_key
from opalizer.config import get_root_dir, settings
from opalizer.database import async_engine, with_async_db
from opalizer.exceptions import TenantNameNotAvailableError, UpgradeAlembicHeadError

root_dir = get_root_dir()


def get_alembic_config() -> Config:
    alembic_cfg = Config(os.path.join(root_dir, "alembic.ini"))
    return alembic_cfg


alembic_cfg = get_alembic_config()


def add_args(schema, dry_run, config):
    config.cmd_opts = argparse.Namespace()
    config.cmd_opts.x = []
    cmd_opts = []
    cmd_opts.append(f"tenant={schema}")
    cmd_opts.append(f"dry_run={dry_run}")
    config.cmd_opts.x = cmd_opts


async def upgrade_head(
    tenant_name: str, revision: str = "head", url: str = settings.db.url, dry_run=False
):
    try:
        config = Config(os.path.join(root_dir, "alembic.ini"))
        config.set_main_option("script_location", os.path.join(root_dir, "alembic"))
        config.set_main_option("sqlalchemy.url", url)
        add_args(tenant_name, dry_run, config)

        def run_upgrade(connection, config: Config, revision: str, sql=False, tag=None):
            config.attributes["connection"] = connection
            command.upgrade(config=config, revision=revision, sql=sql, tag=tag)

        # Using direct async_engine here to avoid bubbling an exception from with_async_db
        async with async_engine.begin() as connection:
            await connection.run_sync(run_upgrade, config, revision)
    except Exception:
        _, value, _ = sys.exc_info()
        logging.error(
            f"Error occurred while running alembic upgrade head for schema '{tenant_name}'"
        )
        raise UpgradeAlembicHeadError(value)


async def provision_tenant(schema: str) -> dict:
    """Creates a new schema and upgrade to current head
    :param schema: schema name
    """
    try:
        if schema == "public":
            raise TenantNameNotAvailableError(schema=schema)

        async with with_async_db("public") as session:
            await session.execute(sa.schema.CreateSchema(schema))
            await session.commit()
        await upgrade_head(tenant_name=schema)
        return {"schema": schema}
    except ProgrammingError as e:
        if e.orig and e.orig.sqlstate:
            if e.orig.sqlstate == pgexec.DuplicateSchemaError.sqlstate:
                logging.warning(f"Schema '{schema} already exists!")
                raise TenantNameNotAvailableError(schema=schema)
    except UpgradeAlembicHeadError:
        async with with_async_db("public") as session:
            await session.execute(sa.text(f"DROP SCHEMA IF EXISTS {str(schema)}"))
            await session.commit()
        raise
    except Exception as e:
        logging.fatal(e)
        raise


async def delete_tenant(schema: str, cascade: bool = False) -> dict:
    """Delete's schema depending on the provided cascade flag.
    :param schema: schema name
    :param cascade: cascade delete
    """
    try:
        async with with_async_db("public") as session:
            if cascade:
                await session.execute(
                    sa.text(f"DROP SCHEMA IF EXISTS {str(schema)} CASCADE")
                )
            else:
                await session.execute(sa.text(f"DROP SCHEMA IF EXISTS {str(schema)}"))
            await session.commit()
        return {"schema": schema}
    except Exception as e:
        logging.fatal(e)
        raise e


async def create_tenant(session: AsyncSession, payload: TenantSchema) -> Tenant:
    if payload.name == "public":
        raise TenantNameNotAvailableError(schema=payload.name)
    new_tenant = Tenant(**payload.dict())
    new_tenant.schema = generate_tenant_schema_name(payload.name)
    new_tenant.slug = slugify(payload.name)
    # new_tenant.api_key = generate_api_key(suffix=payload.name)
    session.add(new_tenant)
    await provision_tenant(schema=new_tenant.schema)
    await session.commit()
    await session.refresh(new_tenant)
    # create api key
    new_tenant.api_key = generate_api_key(tenant_id=new_tenant.id)
    await session.merge(new_tenant)
    await session.commit()
    await session.refresh(new_tenant)
    return new_tenant


async def get_all(session: AsyncSession) -> Union[None, List[Tenant]]:
    result = await session.execute(select(Tenant).order_by(Tenant.name))
    return result.scalars().all()


async def get_by_name(session: AsyncSession, tenant_name: str) -> Union[None, Tenant]:
    result = await session.execute(
        select(Tenant).where(Tenant.name == tenant_name).order_by(Tenant.name).limit(1)
    )
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, id: UUID) -> Union[None, Tenant]:
    result = await session.execute(select(Tenant).where(Tenant.id == id).limit(1))
    return result.scalar_one_or_none()
