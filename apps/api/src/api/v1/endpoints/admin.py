"""Admin Console endpoints for system metrics, quotas, and audit logs (BỔ SUNG 2)."""

import math
from uuid import UUID

from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_admin_service, require_admin_user
from api.schemas.admin import (
    AdminDashboardEnvelope,
    AdminHealthEnvelope,
    AdminUpdateUserQuotaRequest,
    AdminUsageListEnvelope,
    AdminUserEnvelope,
    AdminUserListEnvelope,
)
from api.schemas.envelope import ResponseMeta
from api.services.admin_service import AdminService
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/dashboard",
    response_model=AdminDashboardEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Dashboard chỉ số hệ thống toàn diện (BỔ SUNG 2)",
    description=(
        "Thống kê tổng số người dùng, tài liệu CAS, dung lượng ổ đĩa, "
        "tổng LLM tokens đã tiêu thụ và ước tính chi phí."
    ),
)
async def get_dashboard(
    admin: UserModel = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminDashboardEnvelope:
    """Return system-wide telemetry and resource consumption aggregates."""
    del admin
    metrics = await admin_service.get_dashboard_metrics(db=db)
    return AdminDashboardEnvelope(success=True, data=metrics, meta=ResponseMeta())


@router.get(
    "/users",
    response_model=AdminUserListEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Quản lý danh sách người dùng & Hạn mức Token",
    description="Liệt kê danh sách tài khoản kèm số lượng token đã dùng, hạn mức và vai trò.",
)
async def list_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    admin: UserModel = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminUserListEnvelope:
    """List all user accounts with quota allocations."""
    del admin
    users, total = await admin_service.list_users(
        db=db, page=page, per_page=per_page, search=search
    )
    total_pages = max(1, math.ceil(total / per_page))
    return AdminUserListEnvelope(
        success=True,
        data=users,
        meta={
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "request_id": ResponseMeta().request_id,
            "timestamp": ResponseMeta().timestamp,
        },
    )


@router.patch(
    "/users/{id}/quota",
    response_model=AdminUserEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Điều chỉnh hạn mức Token & Phân quyền người dùng",
    description=(
        "Cho phép Admin tăng/giảm hạn mức LLM Token, dung lượng lưu trữ hoặc thay đổi vai trò."
    ),
)
async def update_user_quota(
    id: UUID,
    request: AdminUpdateUserQuotaRequest,
    admin: UserModel = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminUserEnvelope:
    """Update quota allocations or role for a user."""
    del admin
    user = await admin_service.update_user_quota(db=db, target_user_id=id, request=request)
    return AdminUserEnvelope(success=True, data=user, meta=ResponseMeta())


@router.get(
    "/usage",
    response_model=AdminUsageListEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Nhật ký kiểm toán tiêu thụ tài nguyên thời gian thực",
    description=(
        "Xem toàn bộ các sự kiện gọi LLM, tính toán chi phí và phân bổ token theo tài khoản."
    ),
)
async def list_usage(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    activity_type: str | None = Query(default=None),
    admin: UserModel = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminUsageListEnvelope:
    """List usage audit logs."""
    del admin
    records, total = await admin_service.list_usage_records(
        db=db, page=page, per_page=per_page, activity_type=activity_type
    )
    total_pages = max(1, math.ceil(total / per_page))
    return AdminUsageListEnvelope(
        success=True,
        data=records,
        meta={
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "request_id": ResponseMeta().request_id,
            "timestamp": ResponseMeta().timestamp,
        },
    )


@router.get(
    "/system-health",
    response_model=AdminHealthEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra trạng thái sức khỏe hạ tầng hệ thống",
    description="Kiểm tra kết nối PostgreSQL, phân vùng lưu trữ CAS và độ trễ phản hồi.",
)
async def get_system_health(
    admin: UserModel = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminHealthEnvelope:
    """Check physical storage health and database connectivity."""
    del admin
    health = await admin_service.get_system_health(db=db)
    return AdminHealthEnvelope(success=True, data=health, meta=ResponseMeta())
