from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field as f

from .unique import UniqueId, make_unique_id


@dataclass
class User:
    user_id: UniqueId = f(default_factory=make_unique_id)
    email: str = f(default=None)
    first_name: str = f(default=None)
    last_name: str = f(default=None)
    age: int = f(default=None)
    bio: str = f(default=None)
    city: str = f(default=None)


class Repository(metaclass=ABCMeta):
    @abstractmethod
    def get(self, user_id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_multi(
        self,
        first_name: str = None,
        last_name: str = None,
        limit: int = 0,
        offset: int = 20,
    ) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def put(self, user: User):
        raise NotImplementedError
