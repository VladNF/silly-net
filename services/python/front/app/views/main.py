import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends
from prometheus_client import make_asgi_app, Counter, Histogram

from . import services
from .auth import get_current_user
from .models import (
    ListUsersRequest,
    LoginRequest,
    LoginResponse,
    SignUpRequest,
    SignUpResponse,
    User,
)

app = FastAPI(
    title="SNet -- Social Network",
    version="0.1.0",
    servers=[
        {
            "url": "https://{hostname}/",
            "variables": {"hostname": {"default": "localhost"}},
        }
    ],
)

# Metrics
req_count_metric = Counter("snet_front_requests", "HTTP API Requests", ["method", "endpoint"])
req_failed_metric = Counter("snet_front_requests_failed", "HTTP API Requests Failed", ["method", "endpoint"])
req_time_metric = Histogram("snet_front_request_time", "HTTP API Requests Timing", ["method", "endpoint"])


@asynccontextmanager
async def request_metrics(**labels):
    start_ts = time.time()
    try:
        yield
    except Exception:
        req_failed_metric.labels(**labels).inc()
        raise
    finally:
        elapsed_sec = time.time() - start_ts
        req_time_metric.labels(**labels).observe(elapsed_sec)
        req_count_metric.labels(**labels).inc()


@app.get("/liveness")
async def liveness() -> str:
    return "ok"


@app.get("/readiness")
async def rediness() -> str:
    return "ok"


@app.post("/auth/login", response_model=LoginResponse)
async def user_login(body: LoginRequest = None) -> LoginResponse:
    async with request_metrics(method="POST", endpoint="/auth/login"):
        return await services.user_login(body)


@app.post("/auth/signup", response_model=SignUpResponse)
async def user_sign_up(body: SignUpRequest = None) -> SignUpResponse:
    async with request_metrics(method="POST", endpoint="/auth/signup"):
        return await services.user_sign_up(body)


@app.get("/users/", response_model=list[User])
async def list_users(filters: ListUsersRequest = Depends(), _: str = Depends(get_current_user)) -> list[User]:
    async with request_metrics(method="GET", endpoint="/users/"):
        return await services.list_users(filters)


@app.get("/users/{id}", response_model=User)
async def get_user(id: str, _: str = Depends(get_current_user)) -> User:
    async with request_metrics(method="GET", endpoint="/users/"):
        return await services.get_user(id)


# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
