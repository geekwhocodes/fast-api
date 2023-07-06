import os

import pytest_asyncio
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["FORCE_ENV_FOR_DYNACONF"] = "test"  # noqa

from opalizer.config import settings
from opalizer.database import get_async_db, get_public_async_db
from opalizer.main import app


@pytest_asyncio.fixture(name="session")
async def session_fixure():
    engine = create_async_engine(settings.db.url, echo=bool(settings.db.echo), pool_pre_ping=True, pool_recycle=240)
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    schema_translate_map = {"tenant": "test_tenant_00000000000000000000000000000000"}
    schema_engine = engine.execution_options(schema_translate_map=schema_translate_map)
    async with async_session(autocommit=False, autoflush=False, bind=schema_engine) as session:
        yield session



@pytest_asyncio.fixture
async def client(session: Session):
    application = app
    def get_session_override():
        return session

    application.dependency_overrides[get_async_db] = get_session_override
    application.dependency_overrides[get_public_async_db] = get_session_override

    async with TestClient(application=application) as c:
        yield c


