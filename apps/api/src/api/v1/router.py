"""API Version 1 Router Aggregator."""

from api.v1.endpoints import (
    auth,
    discovery,
    documents,
    drafts,
    folders,
    library,
    notes,
    sessions,
)
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth.router)
api_v1_router.include_router(discovery.router)
api_v1_router.include_router(documents.router)
api_v1_router.include_router(sessions.router)
api_v1_router.include_router(notes.router)
api_v1_router.include_router(drafts.router)
api_v1_router.include_router(folders.router)
api_v1_router.include_router(library.router)
