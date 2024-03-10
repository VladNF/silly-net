import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models.users import User
from app.services.users import create_user, make_password_hash
from app.views.auth import make_new_token
from app.views.main import app

pytest_plugins = ("tests.fixtures.db", "tests.fixtures.repo")


@pytest_asyncio.fixture
async def web_app():
    c = AsyncClient(app=app, base_url="http://test")
    yield c
    await c.aclose()


@pytest.mark.in_mem_repo
@pytest_asyncio.fixture
async def user_1() -> User:
    return await create_user(
        email="j@VladNF.ru",
        first_name="Vlad",
        last_name="NF",
        age=42,
        bio="somewhere in the deep space",
        city="NF",
        pwd_hash=make_password_hash("424242"),
    )


@pytest.mark.in_mem_repo
@pytest_asyncio.fixture
async def user_2() -> User:
    return await create_user(
        email="k@KenMS.ru",
        first_name="Ken",
        last_name="MS",
        age=43,
        bio="somewhere in the deep space",
        city="MS",
        pwd_hash=make_password_hash("424242"),
    )


@pytest.mark.in_mem_repo
@pytest_asyncio.fixture
async def user_3() -> User:
    return await create_user(
        email="l@LiamVG.ru",
        first_name="Liam",
        last_name="VG",
        age=42,
        bio="somewhere in the deep space",
        city="VG",
        pwd_hash=make_password_hash("424242"),
    )


@pytest_asyncio.fixture
async def users(user_1, user_2, user_3) -> list[User]:
    return [user_1, user_2, user_3]


@pytest_asyncio.fixture
async def valid_token(user_1) -> str:
    return make_new_token(user_1.user_id)

