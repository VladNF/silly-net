from app.models.users import Repository, User


class UsersRepo(Repository):
    def get(self, user_id: str) -> User:
        pass

    def get_multi(
        self,
        first_name: str = None,
        last_name: str = None,
        limit: int = 0,
        offset: int = 20,
    ) -> list[User]:
        pass

    def put(self, user: User):
        pass


def make_new_repo() -> Repository:
    return UsersRepo()
