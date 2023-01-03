from contextlib import contextmanager
from contextvars import ContextVar
from functools import cached_property
from typing import Callable, Generator, Mapping

import yarl
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

_get_engine_cvar: ContextVar[Callable[[str], AIOEngine] | None] = ContextVar(
    "__get_engine_cvar", default=None
)


class AIOEngineMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, instance_url: yarl.URL, engines: Mapping[str, AIOEngine] | None = None
    ) -> None:
        super().__init__(app)
        self.instance_url = instance_url
        self.__db_refs: dict[str, AIOEngine] = dict(**engines) if engines else dict()

    @cached_property
    def client(self) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(str(self.instance_url))

    def engine(self, name: str) -> AIOEngine:
        return self.__db_refs.setdefault(name, AIOEngine(motor_client=self.client, database=name))

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        global _get_engine_cvar
        token = None
        try:
            token = _get_engine_cvar.set(self.engine)
            return await call_next(request)
        finally:
            if token:
                _get_engine_cvar.reset(token)


@contextmanager
def db(name: str) -> Generator[AIOEngine, None, None]:
    global _get_engine_cvar
    if (get_engine := _get_engine_cvar.get()) is None:
        raise RuntimeError(f"Make sure f{AIOEngineMiddleware.__name__} is in use")
    yield get_engine(name)
