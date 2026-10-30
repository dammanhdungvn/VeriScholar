"""Evaluations & Benchmark Suite REST Endpoints (Spec 07 §1.E, §5.D).

Provides:
- POST /api/v1/evaluations/run-benchmark: Execute 3-track golden benchmark evaluation
"""

from __future__ import annotations

import structlog
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import (
    get_ai_tracing_service,
    get_benchmark_runner_service,
    get_current_active_user,
)
from api.schemas.envelope import ResponseMeta
from api.schemas.error import ErrorResponse
from api.schemas.evaluations import (
    BenchmarkRunRequest,
    BenchmarkRunResponseEnvelope,
)
from api.services.ai_tracing_service import AITracingService
from api.services.benchmark_runner_service import BenchmarkRunnerService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.endpoints.evaluations")

router = APIRouter()


@router.post(
    "/run-benchmark",
    response_model=BenchmarkRunResponseEnvelope,
    summary="Chạy đánh giá bộ Benchmark 3-Track khoa học",
    description=(
        "Thực thi đánh giá benchmark định lượng trên 3 track học thuật: "
        "Advanced RAG, GraphRAG & Wiki, và Agentic RAG / Overleaf, "
        "tính toán 4 chỉ số cốt lõi và ghi nhận telemetry vào Langfuse."
    ),
    responses={
        200: {"description": "Kết quả đánh giá benchmark thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
        422: {"description": "Tham số track không hợp lệ."},
    },
)
async def run_benchmark(
    request_data: BenchmarkRunRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    benchmark_runner: BenchmarkRunnerService = Depends(get_benchmark_runner_service),
    tracing_service: AITracingService = Depends(get_ai_tracing_service),
) -> BenchmarkRunResponseEnvelope:
    """Run golden benchmark suite for specified track."""
    logger.info(
        "run_benchmark_requested",
        user_id=str(current_user.id),
        track=request_data.track,
        experiment_name=request_data.experiment_name,
    )

    result = await benchmark_runner.run_benchmark(
        track=request_data.track,
        experiment_name=request_data.experiment_name,
        db=db,
        user_id=current_user.id,
        tracing_service=tracing_service,
    )

    return BenchmarkRunResponseEnvelope(
        data=result,
        meta=ResponseMeta(),
        links={"self": "/api/v1/evaluations/run-benchmark"},
    )
