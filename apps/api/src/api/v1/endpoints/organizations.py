"""Endpoints for collaborative Research Labs and Organizations (BỔ SUNG 2)."""

from uuid import UUID

from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_organization_service
from api.schemas.envelope import ResponseMeta
from api.schemas.organization import (
    AddOrganizationMemberRequest,
    CreateOrganizationRequest,
    OrganizationDetailEnvelope,
    OrganizationEnvelope,
    OrganizationListEnvelope,
    OrganizationMemberResponse,
    UpdateMemberRoleRequest,
    UpdateOrganizationRequest,
)
from api.services.organization_service import OrganizationService
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    response_model=OrganizationEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo nhóm nghiên cứu / Lab mới",
    description="Khởi tạo Lab nghiên cứu mới và chỉ định người tạo làm Chủ sở hữu (Owner).",
)
async def create_organization(
    request: CreateOrganizationRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationEnvelope:
    """Create a new research lab."""
    org = await org_service.create_organization(db=db, user=current_user, request=request)
    return OrganizationEnvelope(success=True, data=org, meta=ResponseMeta())


@router.get(
    "",
    response_model=OrganizationListEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Danh sách các Lab mà người dùng tham gia",
    description="Liệt kê toàn bộ các Lab và nhóm cộng tác mà tài khoản hiện tại có quyền truy cập.",
)
async def list_organizations(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationListEnvelope:
    """List research labs for current user."""
    orgs = await org_service.list_user_organizations(db=db, user=current_user)
    return OrganizationListEnvelope(
        success=True,
        data=orgs,
        meta={
            "total": len(orgs),
            "page": 1,
            "per_page": max(1, len(orgs)),
            "total_pages": 1,
            "request_id": ResponseMeta().request_id,
            "timestamp": ResponseMeta().timestamp,
        },
    )


@router.get(
    "/{id}",
    response_model=OrganizationDetailEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Chi tiết Lab nghiên cứu & Danh sách thành viên",
    description="Xem toàn bộ hạn mức dung lượng, LLM token và danh sách thành viên trong Lab.",
)
async def get_organization(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationDetailEnvelope:
    """Get research lab details and roster."""
    detail = await org_service.get_organization_detail(db=db, user=current_user, org_id=id)
    return OrganizationDetailEnvelope(success=True, data=detail, meta=ResponseMeta())


@router.patch(
    "/{id}",
    response_model=OrganizationEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật cài đặt Lab nghiên cứu",
    description="Cập nhật tên, mô tả hoặc hạn mức Lab (chỉ dành cho Owner hoặc Admin).",
)
async def update_organization(
    id: UUID,
    request: UpdateOrganizationRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationEnvelope:
    """Update research lab settings."""
    org = await org_service.update_organization(
        db=db, user=current_user, org_id=id, request=request
    )
    return OrganizationEnvelope(success=True, data=org, meta=ResponseMeta())


@router.post(
    "/{id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên / cộng tác viên vào Lab",
    description="Mời người dùng hiện có vào Lab nghiên cứu với vai trò admin, member hoặc guest.",
)
async def add_member(
    id: UUID,
    request: AddOrganizationMemberRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationMemberResponse:
    """Add a member to the research lab."""
    return await org_service.add_member(db=db, user=current_user, org_id=id, request=request)


@router.patch(
    "/{id}/members/{user_id}",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Thay đổi vai trò thành viên trong Lab",
    description="Cập nhật quyền hạn của thành viên (admin, member, guest).",
)
async def update_member_role(
    id: UUID,
    user_id: UUID,
    request: UpdateMemberRoleRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationMemberResponse:
    """Update member role in lab."""
    return await org_service.update_member_role(
        db=db, user=current_user, org_id=id, target_user_id=user_id, request=request
    )


@router.delete(
    "/{id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa thành viên hoặc Rời khỏi Lab",
    description="Xóa thành viên khỏi nhóm hoặc tự nguyện rời khỏi Lab nghiên cứu.",
)
async def remove_member(
    id: UUID,
    user_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_service: OrganizationService = Depends(get_organization_service),
) -> None:
    """Remove member from lab."""
    await org_service.remove_member(db=db, user=current_user, org_id=id, target_user_id=user_id)
