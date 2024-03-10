import asyncio
import contextlib

import asyncpg
import pytest
import pytest_asyncio
from yoyo import get_backend, read_migrations

from app import settings as s

TEST_DB_NAME = "test_{name}".format(name=s.db_name)
DSN_PG = f"postgresql://{s.db_user}:{s.db_password}@{s.db_host}:{s.db_port}/postgres"
DSN_TEST = f"postgresql://{s.db_user}:{s.db_password}@{s.db_host}:{s.db_port}/{TEST_DB_NAME}"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@contextlib.asynccontextmanager
async def connect(dsn):
    conn = await asyncpg.connect(dsn)
    try:
        yield conn
    finally:
        await conn.close()


@pytest.fixture(autouse=True, scope="session")
async def make_db():
    async with connect(DSN_PG) as conn:
        await conn.execute(f"drop database if exists {TEST_DB_NAME};")
        await conn.execute(f"drop database if exists {TEST_DB_NAME}_template;")
        await conn.execute(f"create database {TEST_DB_NAME};")

    backend = get_backend(DSN_TEST)
    skip_db_feed = lambda m: "20230203_01_data_feed" not in m.path
    migrations = read_migrations("services/db/migrations").filter(skip_db_feed)
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    del backend  # connection is not released otherwise

    async with connect(DSN_PG) as conn:
        await conn.execute(f"select pg_terminate_backend(pid) from pg_stat_activity where datname = '{TEST_DB_NAME}'")
        await conn.execute(f"create database {TEST_DB_NAME}_template template {TEST_DB_NAME};")

    try:
        s.db_name = TEST_DB_NAME
        yield
    finally:
        async with connect(DSN_PG) as conn:
            await conn.execute(f"drop database if exists {TEST_DB_NAME};")
            await conn.execute(f"drop database if exists {TEST_DB_NAME}_template;")


async def recreate_db():
    async with connect(DSN_PG) as conn:
        await conn.execute(f"drop database {TEST_DB_NAME} with (FORCE);")
        await conn.execute(f"create database {TEST_DB_NAME} template {TEST_DB_NAME}_template;")


async def truncate_db():
    async with connect(DSN_TEST) as conn:
        await conn.execute(
            "truncate users;"
        )


@pytest.fixture(autouse=True)
async def _use_db_marker(request):
    """Implement the use_db marker"""
    marker = request.node.get_closest_marker("use_db")
    if not marker:
        return

    try:
        yield
    except Exception:
        raise
    finally:
        await truncate_db()


def pytest_configure(config):
    config.addinivalue_line("markers", "use_db: marks the test as using db access")
