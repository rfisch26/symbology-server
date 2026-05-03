"""
HTTP routes for the symbology service.

This module handles request/response translation only.
All business logic lives in the domain layer.
"""

from datetime import date as DateType
from fastapi import APIRouter, HTTPException, Query
from src.domain import SymbologyServer
from src.exceptions import ConflictError, NotFoundError
from src.schemas import MappingCreate, MappingTerminate, MappingResponse, MappingCreated, MappingTerminated


def create_router(domain: SymbologyServer) -> APIRouter:
    router = APIRouter()

    @router.post("/mapping", response_model=MappingCreated, status_code=201)
    def add_mapping(request: MappingCreate) -> MappingCreated:
        try:
            domain.add_mapping(request.symbol, request.identifier, request.start_date)
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc))
        return MappingCreated(
            symbol=request.symbol,
            identifier=request.identifier,
            start_date=request.start_date,
        )

    @router.post("/mapping/terminate", response_model=MappingTerminated)
    def terminate_mapping(request: MappingTerminate) -> MappingTerminated:
        try:
            domain.terminate_mapping(request.symbol, request.end_date)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return MappingTerminated(symbol=request.symbol, end_date=request.end_date)

    @router.get("/symbol/{symbol}", response_model=int)
    def get_identifier(symbol: str, date: DateType = Query(..., description="ISO date, e.g. 2024-01-15")) -> int:
        try:
            return domain.get_identifier(symbol, date)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/identifier/{identifier}", response_model=str)
    def get_symbol(identifier: int, date: DateType = Query(..., description="ISO date, e.g. 2024-01-15")) -> str:
        try:
            return domain.get_symbol(identifier, date)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/mappings", response_model=list[MappingResponse])
    def get_mappings(
        begin: DateType = Query(..., description="Range start (inclusive)"),
        end: DateType = Query(..., description="Range end (exclusive)"),
    ) -> list[MappingResponse]:
        return domain.get_mappings_between(begin, end)

    return router