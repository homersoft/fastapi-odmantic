from typing import Any

import pytest
from fastapi import FastAPI
from odmantic import AIOEngine
from yarl import URL

from fastapi_odmantic.main import AIOEngineMiddleware, db


@pytest.mark.asyncio
async def test_middleware_access_from_within_route():
    app = FastAPI()

    mock_engine = object()
    middleware = AIOEngineMiddleware(
        app,
        URL("mongodb://localhost:27017"),
        engines={"test": mock_engine},  # type: ignore
    )

    async def handler(_: Any) -> None:
        with db("test") as engine:
            assert engine is mock_engine

    await middleware.dispatch(None, handler)  # type: ignore


def test_middleware_creates_aioengine():
    app = FastAPI()

    middleware = AIOEngineMiddleware(app, URL("mongodb://localhost"))

    assert isinstance(middleware.engine("test"), AIOEngine)
