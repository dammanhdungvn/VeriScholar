"""Ports defining abstract contracts for inbound and outbound adapters."""

from core.ports.idempotency import IIdempotencyPort
from core.ports.storage import IBlobStoragePort

__all__ = ["IBlobStoragePort", "IIdempotencyPort"]
