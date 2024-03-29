import time
from contextlib import asynccontextmanager

import asyncpg as pg
from prometheus_client import Counter, Gauge, Histogram

from app import settings as s
from app.models.users import Repository, User
from app.repo.query import InsertBuilder, WhereBuilder

# Metrics
req_conn_count_metric = Gauge("snet_db_connections", "DB Connections", ["dsn"])
req_count_metric = Counter("snet_db_requests", "DB Requests", ["method", "dsn"])
req_failed_metric = Counter("snet_db_requests_failed", "DB Requests Failed", ["method", "dsn"])
req_time_metric = Histogram("snet_db_request_time", "DB Requests Timing", ["method", "dsn"])


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


def as_db_model(u: User) -> tuple:
    return (
        u.user_id,
        u.email,
        u.first_name,
        u.last_name,
        u.age,
        u.bio,
        u.city,
        u.pwd_hash,
    )


class UsersRepo(Repository):
    GET_QUERY = """SELECT * FROM users u {where_cond}"""
    GET_MULTI_QUERY = """SELECT * FROM users u {where_cond} LIMIT $1 OFFSET $2"""
    PUT_QUERY = """
    INSERT INTO 
        users(user_id, email, first_name, last_name, age, bio, city, pwd_hash)
    VALUES {values_expression}
    """

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        _, self.dsn_host = dsn.split("@")
        self.pool = None

    async def get_pg_pool(self) -> pg.Pool:
        if not self.pool:
            self.pool = await pg.create_pool(self.dsn, min_size=0, max_size=100, command_timeout=5)
        return self.pool
    
    @asynccontextmanager
    async def query(self, **labels):
        start_ts = time.time()
        pool = await self.get_pg_pool()
        try:
            async with pool.acquire() as c:
                req_conn_count_metric.labels(dsn=labels["dsn"]).set(pool.get_size())
                yield c
        except Exception:
            req_failed_metric.labels(**labels).inc()
            raise
        finally:
            elapsed_sec = time.time() - start_ts
            req_time_metric.labels(**labels).observe(elapsed_sec)
            req_count_metric.labels(**labels).inc()

    async def get(self, user_id: str) -> User:
        where_builder = WhereBuilder()
        where_builder.with_fields_eq(user_id=user_id)
        query = self.GET_QUERY.format(where_cond=where_builder.build())
        async with self.query(dsn=self.dsn_host, method="get") as c:
            r = await c.fetchrow(query, user_id)
            return from_db_model(r)

    async def get_by_email(self, email: str) -> User:
        where_builder = WhereBuilder()
        where_builder.with_fields_eq(email=email)
        query = self.GET_QUERY.format(where_cond=where_builder.build())
        async with self.query(dsn=self.dsn_host, method="get_by_email") as c:
            r = await c.fetchrow(query, email)
            return from_db_model(r)

    async def get_multi(
        self,
        first_name: str = None,
        last_name: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]:
        where_builder = WhereBuilder(var_index=3)
        where_builder.with_fields_prefix(first_name=first_name, last_name=last_name)
        query = self.GET_MULTI_QUERY.format(where_cond=where_builder.build())
        async with self.query(dsn=self.dsn_host, method="get_multi") as c:
            r = await c.fetch(query, limit, offset, *where_builder.variables)
            return list(map(from_db_model, r))

    async def put(self, user: User):
        expr_builder = InsertBuilder(map_func=as_db_model)
        expr_builder.with_object(user)
        async with self.query(dsn=self.dsn_host, method="put") as c:
            query = self.PUT_QUERY.format(values_expression=expr_builder.build())
            _ = await c.execute(query, *expr_builder.variables)
            return user

    async def put_multi(self, users: list[User]):
        expr_builder = InsertBuilder(map_func=as_db_model)
        expr_builder.with_object_multi(users)
        async with self.query(dsn=self.dsn_host, method="put_multi") as c:
            query = self.PUT_QUERY.format(values_expression=expr_builder.build())
            _ = await c.execute(query, *expr_builder.variables)
            return users


def make_new_repo(db_dsn: str) -> Repository:
    return UsersRepo(db_dsn)


users_repo = make_new_repo(s.db_dsn_rw)
users_repo_ro = make_new_repo(s.db_dsn_ro)
