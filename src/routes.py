"""
HTTP routes for the symbology service.

This module handles request/response translation only.
"""

from datetime import date
from typing import List
from fastapi import APIRouter, HTTPException
from .domain import SymbologyServer
from .exceptions import ConflictError, NotFoundError
from .schemas import MappingCreate, MappingTerminate, MappingResponse


def create_router(domain: SymbologyServer) -> APIRouter:
    router = APIRouter()

    @router.post("/mapping")
    def add_mapping(request: MappingCreate):
        """Add a new symbology mapping."""
        try:
            domain.add_mapping(
                request.symbol,
                request.identifier,
                request.start_date,
            )
            return {
                "status": "ok",
                "symbol": request.symbol,
                "identifier": request.identifier,
                "start_date": request.start_date,
            }
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

    @router.post("/mapping/terminate")
    def terminate_mapping(request: MappingTerminate):
        """Terminate an active symbology mapping."""
        try:
            domain.terminate_mapping(request.symbol, request.end_date)
            return {
                "status": "terminated",
                "symbol": request.symbol,
                "end_date": request.end_date,
            }
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/symbol/{symbol}", response_model=int)
    def get_identifier(symbol: str, date: date):
        """Get the identifier for a symbol on a given date."""
        try:
            return domain.get_identifier(symbol, date)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/identifier/{identifier}", response_model=str)
    def get_symbol(identifier: int, date: date):
        """Get the symbol for an identifier on a given date."""
        try:
            return domain.get_symbol(identifier, date)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/mappings", response_model=List[MappingResponse])
    def get_mappings(begin: date, end: date):
        """Get all mappings overlapping the given date range [begin, end)."""
        return domain.get_mappings_between(begin, end)

    return router
