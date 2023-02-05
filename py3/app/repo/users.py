import asyncpg as pg

from app import settings as s
from app.models.users import Repository, User


def from_db_model(r: pg.Record) -> User | None:
    if not r:
        return None

    return User(
        user_id=r["user_id"],
        email=r["email"],
        first_name=r["first_name"],
        last_name=r["last_name"],
        age=r["age"],
        bio=r["bio"],
        city=r["city"],
        pwd_hash=r["pwd_hash"],
    )


class WhereBuilder:
    def __init__(self, var_index=1) -> None:
        self.conditions = []
        self.variables = []
        self.var_index = var_index

    def with_fields_eq(self, **kwargs):
        for field_name, field_value in kwargs.items():
            self.conditions += [f"{field_name} = ${self.var_index}"]
            self.variables += [field_value]
            self.var_index += 1

    def with_fields_like(self, **kwargs):
        for field_name, field_value in kwargs.items():
            if not field_value:
                continue

            self.conditions += [f"{field_name} ILIKE ${self.var_index}"]
            self.variables += [f"%{field_value}%"]
            self.var_index += 1

    def build(self):
        if not self.conditions:
            return ""

        return f"WHERE {' AND '.join(self.conditions)}"


class UsersRepo(Repository):
    GET_QUERY = """SELECT * FROM users u {where_cond}"""
    GET_MULTI_QUERY = """SELECT * FROM users u {where_cond} LIMIT $1 OFFSET $2"""
    PUT_QUERY = """INSERT INTO 
        users(
        user_id,
        email,
        first_name,
        last_name,
        age,
        bio,
        city,
        pwd_hash
        )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """

    def __init__(self) -> None:
        self.pool = None

    async def get_pg_pool(self) -> pg.Pool:
        if not self.pool:
            self.pool = await pg.create_pool(
                f"postgresql://{s.db_user}:{s.db_password}@{s.db_host}/{s.db_name}?port={s.db_port}"
            )
        return self.pool

    async def get(self, user_id: str) -> User:
        where_builder = WhereBuilder(var_index=1)
        where_builder.with_fields_eq(user_id=user_id)
        query = self.GET_QUERY.format(where_cond=where_builder.build())
        pool = await self.get_pg_pool()
        async with pool.acquire() as c:
            r = await c.fetchrow(query, user_id)
            return from_db_model(r)

    async def get_by_email(self, email: str) -> User:
        where_builder = WhereBuilder(var_index=1)
        where_builder.with_fields_eq(email=email)
        query = self.GET_QUERY.format(where_cond=where_builder.build())
        pool = await self.get_pg_pool()
        async with pool.acquire() as c:
            r = await c.fetchrow(query, email)
            return from_db_model(r)

    async def get_multi(
        self,
        first_name: str = None,
        last_name: str = None,
        limit: int = 0,
        offset: int = 20,
    ) -> list[User]:
        where_builder = WhereBuilder(var_index=3)
        where_builder.with_fields_like(first_name=first_name, last_name=last_name)
        query = self.GET_MULTI_QUERY.format(where_cond=where_builder.build())
        pool = await self.get_pg_pool()
        async with pool.acquire() as c:
            r = await c.fetch(query, limit, offset, *where_builder.variables)
            return list(map(from_db_model, r))

    async def put(self, user: User):
        pool = await self.get_pg_pool()
        async with pool.acquire() as c:
            _ = await c.execute(
                self.PUT_QUERY,
                user.user_id,
                user.email,
                user.first_name,
                user.last_name,
                user.age,
                user.bio,
                user.city,
                user.pwd_hash,
            )
            return user


def make_new_repo() -> Repository:
    return UsersRepo()


users_repo = make_new_repo()
