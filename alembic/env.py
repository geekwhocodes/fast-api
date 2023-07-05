import asyncio
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.orm import Session

from alembic import context
from opalizer.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option("sqlalchemy.url", settings.db.url)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    try:
        # print(f"Connection {connection.dialect.default_schema_name}")
        current_tenant = context.get_x_argument(as_dictionary=True).get("tenant")
        print(f"Current tenant: {current_tenant}")
        connection.dialect.default_schema_name = current_tenant
        dry_run = context.get_x_argument(as_dictionary=True).get("dry_run")
        print(f"dry run? {dry_run}")
        if dry_run == "True":
            print("Running in dry run mode.")

        tenant_exists_query = text(
            f"SELECT schema_name FROM information_schema.schemata where schema_name = '{str(current_tenant)}'"
        )
        tenant_exists = connection.execute(tenant_exists_query).scalar()
        if not tenant_exists:
            print(f"Tenant '{current_tenant}' doesn't exists.")
            return
            # raise ValueError(f"Tenant '{current_tenant}' doesn't exists.")

        print("Binding connection to the session")
        session = Session(bind=connection)
        session.execute(text('set search_path to "%s"' % current_tenant))
        session.execute(text("set enable_parallel_hash=off;"))

        # https://alembic.sqlalchemy.org/en/latest/cookbook.html#rudimental-schema-level-multi-tenancy-for-postgresql-databases
        # in SQLAlchemy v2+ the search path change needs to be committed
        session.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=current_tenant,
        )

        with context.begin_transaction():
            context.run_migrations()
            if dry_run == "True":
                print("Dry-run succeeded; now rolling back transaction...")
                connection.rollback()
            session.execute(text("set enable_parallel_hash=on;"))
            session.commit()
            connection.commit()  # for cli to work
    except Exception as e:
        print(f"Error while applying mirations - {str(e)}")


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    current_tenant = context.get_x_argument(as_dictionary=True).get("tenant")

    async with connectable.connect() as connection:
        await connection.execute(text('set search_path to "%s"' % current_tenant))
        connection.dialect.default_schema_name = current_tenant

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    print("Running migrations online")
    connectable = config.attributes.get("connection", None)
    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
