from typing import Callable

import pytest_asyncio

from app.models.users import User, Repository


class UsersMockRepo(Repository):
    def __init__(self) -> None:
        self.storage: list[User] = list()

    def find_users(self, filter_func: Callable[[User], bool]) -> list[User]:
        return list(filter(filter_func, self.storage))

    async def get(self, user_id: str) -> User | None:
        r = self.find_users(lambda u: u.user_id == user_id)
        return r[0] if r else None

    async def get_by_email(self, email: str) -> User | None:
        r = self.find_users(lambda u: u.email == email)
        return r[0] if r else None

    async def get_multi(
        self,
        first_name: str = None,
        last_name: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]:
        r = self.find_users(
            lambda u: first_name in u.first_name or last_name in u.last_name
        )
        return r[offset : offset + limit]

    async def put(self, user: User):
        self.storage.append(user)
        return user

    async def put_multi(self, users: list[User]):
        self.storage += users


@pytest_asyncio.fixture(autouse=True)
async def _in_mem_repo(request, mocker):
    """Implement the in_mem_repo marker"""
    marker = request.node.get_closest_marker("in_mem_repo")
    if not marker:
        return

    repo = UsersMockRepo()
    mocker.patch("app.services.users.users_repo", repo)
    mocker.patch("app.services.users.users_repo_ro", repo)


def pytest_configure(config):
    config.addinivalue_line("markers", "in_mem_repo: marks the test as not using db access, but in-memory repo")
