"""
HTTP routes for the symbology service.

This module handles request/response translation only.
"""

from datetime import date as DateType
from typing import List
from fastapi import APIRouter, HTTPException, Query
from src.domain import SymbologyServer
from src.exceptions import ConflictError, NotFoundError
from src.schemas import MappingCreate, MappingTerminate, MappingResponse


def create_router(domain: SymbologyServer) -> APIRouter:
    router = APIRouter()

    @router.post("/mapping")
    def add_mapping(request: MappingCreate):
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
    def get_identifier(symbol: str, date: DateType = Query(...)):
        try:
            return domain.get_identifier(symbol, date)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/identifier/{identifier}", response_model=str)
    def get_symbol(identifier: int, date: DateType = Query(...)):
        try:
            return domain.get_symbol(identifier, date)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/mappings", response_model=List[MappingResponse])
    def get_mappings(begin: DateType = Query(...), end: DateType = Query(...)):
        return domain.get_mappings_between(begin, end)

    return router
