from abc import ABCMeta, abstractmethod

from pydantic import BaseModel, Field as f

from .unique import make_unique_id


class User(BaseModel):
    user_id: str = f(default_factory=make_unique_id)
    email: str = f(default=None)
    first_name: str = f(default=None)
    last_name: str = f(default=None)
    age: int = f(default=None)
    bio: str | None = f(default=None)
    city: str = f(default=None)
    pwd_hash: str = f(default=None)


class Repository(metaclass=ABCMeta):
    @abstractmethod
    async def get(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_multi(
        self,
        first_name: str = None,
        last_name: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]: ...

    @abstractmethod
    async def put(self, user: User) -> User: ...

    @abstractmethod
    async def put_multi(self, users: list[User]) -> None: ...
