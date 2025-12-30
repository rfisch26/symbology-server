"""
Application entry point for the Symbology Server.
"""

from fastapi import FastAPI
from src.domain import SymbologyServer
from src.storage import MappingStorage
from src.routes import create_router


def create_app(storage: MappingStorage | None = None) -> FastAPI:
    """
    Create FastAPI app with optional storage injection.
    If no storage is provided, use default in-memory storage.
    """
    if storage is None:
        storage = MappingStorage()
    app = FastAPI()
    domain = SymbologyServer(storage)
    router = create_router(domain)
    app.include_router(router)

    return app


app = create_app()
