"""
Application entry point for the Symbology Server.
"""

from fastapi import FastAPI
from .domain import SymbologyServer
from .routes import create_router
from .storage import MappingStorage


def create_app() -> FastAPI:
    """
    Application factory.

    This makes the app easy to test and avoids global state.
    """
    storage = MappingStorage()
    domain = SymbologyServer(storage)
    app = FastAPI(title="Symbology Server")
    app.include_router(create_router(domain))
    return app


app = create_app()
