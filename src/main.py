"""
Application entry point for the Symbology Server.
"""

from fastapi import FastAPI
from .storage import MappingStorage
from .domain import SymbologyServer
from .routes import create_router


def create_app(storage: MappingStorage | None = None) -> FastAPI:
    if storage is None:
        storage = MappingStorage()
    app = FastAPI()
    domain = SymbologyServer(storage)
    create_router(app, domain)
    return app


app = create_app()
