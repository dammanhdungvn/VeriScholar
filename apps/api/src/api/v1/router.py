"""API Version 1 Router Aggregator."""

from api.v1.endpoints import documents
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(documents.router)
