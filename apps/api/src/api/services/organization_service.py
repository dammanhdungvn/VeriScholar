"""Service implementing research lab and organization collaboration logic."""

from uuid import UUID

import structlog
from api.db.models.organization import OrganizationMemberModel, OrganizationModel
from api.db.models.user import UserModel
from api.schemas.organization import (
    AddOrganizationMemberRequest,
    CreateOrganizationRequest,
    OrganizationDetailResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    UpdateMemberRoleRequest,
    UpdateOrganizationRequest,
)
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.organization")


class OrganizationService:
    """Manages collaborative research labs, members, and shared quotas."""

    async def create_organization(
        self,
        db: AsyncSession,
        user: UserModel,
        request: CreateOrganizationRequest,
    ) -> OrganizationResponse:
        """Create new research lab and assign creator as owner."""
        # Check slug uniqueness
        clean_slug = request.slug.lower().strip()
        stmt = select(OrganizationModel).where(OrganizationModel.slug == clean_slug)
        res = await db.execute(stmt)

        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "SLUG_ALREADY_EXISTS",
                    "message": f"Organization slug '{request.slug}' is already taken.",
                    "field": "slug",
                    "action": "Choose a different slug identifier.",
                },
            )

        org = OrganizationModel(
            name=request.name.strip(),
            slug=request.slug.lower().strip(),
            description=request.description.strip() if request.description else None,
            storage_quota_bytes=10737418240,  # 10 GB
            storage_used_bytes=0,
            token_quota=1000000,  # 1M tokens
            tokens_used=0,
        )
        db.add(org)
        await db.flush()

        member = OrganizationMemberModel(
            organization_id=org.id,
            user_id=user.id,
            role="owner",
        )
        db.add(member)
        await db.commit()
        await db.refresh(org)

        logger.info("organization_created", org_id=str(org.id), creator_id=str(user.id))
        return self._to_response(org, members_count=1, user_role="owner")

    async def list_user_organizations(
        self,
        db: AsyncSession,
        user: UserModel,
    ) -> list[OrganizationResponse]:
        """List all research labs that user is a member of."""
        stmt = (
            select(OrganizationModel, OrganizationMemberModel.role)
            .join(
                OrganizationMemberModel,
                OrganizationMemberModel.organization_id == OrganizationModel.id,
            )
            .where(OrganizationMemberModel.user_id == user.id)
            .order_by(OrganizationModel.created_at.desc())
        )
        results = (await db.execute(stmt)).all()

        org_list: list[OrganizationResponse] = []
        for org, role in results:
            # Count members
            count_stmt = select(func.count(OrganizationMemberModel.id)).where(
                OrganizationMemberModel.organization_id == org.id
            )
            count = (await db.execute(count_stmt)).scalar() or 1
            org_list.append(self._to_response(org, members_count=count, user_role=role))

        return org_list

    async def get_organization_detail(
        self,
        db: AsyncSession,
        user: UserModel,
        org_id: UUID,
    ) -> OrganizationDetailResponse:
        """Fetch full details of a research lab including member roster."""
        membership = await self._get_membership(db, org_id, user.id)
        if not membership and getattr(user, "role", "researcher") != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "ORGANIZATION_NOT_FOUND",
                    "message": "Research lab not found or you lack membership access.",
                    "field": "id",
                    "action": "Verify lab identifier or request an invitation.",
                },
            )

        org_stmt = select(OrganizationModel).where(OrganizationModel.id == org_id)
        org = (await db.execute(org_stmt)).scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "ORGANIZATION_NOT_FOUND",
                    "message": "Research lab not found.",
                    "field": "id",
                    "action": "Check organization ID.",
                },
            )

        # Get members with user profiles
        members_stmt = (
            select(OrganizationMemberModel, UserModel.email, UserModel.full_name)
            .join(UserModel, UserModel.id == OrganizationMemberModel.user_id)
            .where(OrganizationMemberModel.organization_id == org_id)
            .order_by(OrganizationMemberModel.created_at.asc())
        )
        member_rows = (await db.execute(members_stmt)).all()

        members: list[OrganizationMemberResponse] = [
            OrganizationMemberResponse(
                id=m.id,
                user_id=m.user_id,
                email=email,
                full_name=full_name,
                role=m.role,
                created_at=m.created_at,
            )
            for m, email, full_name in member_rows
        ]

        user_role = membership.role if membership else "admin"
        return OrganizationDetailResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            description=org.description,
            storage_quota_bytes=org.storage_quota_bytes,
            storage_used_bytes=org.storage_used_bytes,
            token_quota=org.token_quota,
            tokens_used=org.tokens_used,
            members_count=len(members),
            user_role=user_role,
            created_at=org.created_at,
            members=members,
        )

    async def update_organization(
        self,
        db: AsyncSession,
        user: UserModel,
        org_id: UUID,
        request: UpdateOrganizationRequest,
    ) -> OrganizationResponse:
        """Update research lab metadata (owner/admin only)."""
        membership = await self._get_membership(db, org_id, user.id)
        if not membership or membership.role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Only lab owners or admins can update settings.",
                    "field": "role",
                    "action": "Request permission from the lab owner.",
                },
            )

        org_stmt = select(OrganizationModel).where(OrganizationModel.id == org_id)
        org = (await db.execute(org_stmt)).scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab not found.")

        if request.name is not None:
            org.name = request.name.strip()
        if request.description is not None:
            org.description = request.description.strip()
        if request.token_quota is not None:
            org.token_quota = request.token_quota
        if request.storage_quota_bytes is not None:
            org.storage_quota_bytes = request.storage_quota_bytes

        await db.commit()
        await db.refresh(org)
        return self._to_response(org, members_count=1, user_role=membership.role)

    async def add_member(
        self,
        db: AsyncSession,
        user: UserModel,
        org_id: UUID,
        request: AddOrganizationMemberRequest,
    ) -> OrganizationMemberResponse:
        """Invite and register an existing user as a member in the lab."""
        membership = await self._get_membership(db, org_id, user.id)
        if not membership or membership.role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Only lab owners or admins can invite new members.",
                    "field": "role",
                    "action": "Ask a lab administrator to send the invite.",
                },
            )

        # Lookup user by email
        user_stmt = select(UserModel).where(UserModel.email == request.email.lower().strip())
        target_user = (await db.execute(user_stmt)).scalar_one_or_none()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": f"No user registered with email '{request.email}'.",
                    "field": "email",
                    "action": "Ensure the user has created an account first.",
                },
            )

        # Check if already a member
        existing_stmt = select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == org_id,
            OrganizationMemberModel.user_id == target_user.id,
        )
        if (await db.execute(existing_stmt)).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "MEMBER_ALREADY_EXISTS",
                    "message": "User is already a member of this lab.",
                    "field": "email",
                    "action": "Modify their existing role if needed.",
                },
            )

        new_member = OrganizationMemberModel(
            organization_id=org_id,
            user_id=target_user.id,
            role=request.role,
        )
        db.add(new_member)
        await db.commit()
        await db.refresh(new_member)

        logger.info(
            "member_added_to_lab",
            org_id=str(org_id),
            user_id=str(target_user.id),
            role=request.role,
        )
        return OrganizationMemberResponse(
            id=new_member.id,
            user_id=target_user.id,
            email=target_user.email,
            full_name=target_user.full_name,
            role=new_member.role,
            created_at=new_member.created_at,
        )

    async def update_member_role(
        self,
        db: AsyncSession,
        user: UserModel,
        org_id: UUID,
        target_user_id: UUID,
        request: UpdateMemberRoleRequest,
    ) -> OrganizationMemberResponse:
        """Update role of a member in the lab."""
        membership = await self._get_membership(db, org_id, user.id)
        if not membership or membership.role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Only owner or admin can change roles."},
            )

        target_member_stmt = select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == org_id,
            OrganizationMemberModel.user_id == target_user_id,
        )
        target_member = (await db.execute(target_member_stmt)).scalar_one_or_none()
        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "MEMBER_NOT_FOUND", "message": "Target member not found in lab."},
            )

        target_member.role = request.role
        await db.commit()
        await db.refresh(target_member)

        u_stmt = select(UserModel).where(UserModel.id == target_user_id)
        u = (await db.execute(u_stmt)).scalar_one_or_none()

        return OrganizationMemberResponse(
            id=target_member.id,
            user_id=target_user_id,
            email=u.email if u else "unknown@user",
            full_name=u.full_name if u else "Unknown",
            role=target_member.role,
            created_at=target_member.created_at,
        )

    async def remove_member(
        self,
        db: AsyncSession,
        user: UserModel,
        org_id: UUID,
        target_user_id: UUID,
    ) -> None:
        """Remove a member from the lab, or leave the lab."""
        membership = await self._get_membership(db, org_id, user.id)
        is_self_removal = user.id == target_user_id
        is_admin_or_owner = membership and membership.role in ("owner", "admin")

        if not (is_self_removal or is_admin_or_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Cannot remove member without permission."},
            )

        target_member_stmt = select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == org_id,
            OrganizationMemberModel.user_id == target_user_id,
        )
        target_member = (await db.execute(target_member_stmt)).scalar_one_or_none()
        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "MEMBER_NOT_FOUND", "message": "Member not in this lab."},
            )

        await db.delete(target_member)
        await db.commit()
        logger.info("member_removed_from_lab", org_id=str(org_id), user_id=str(target_user_id))

    async def _get_membership(
        self, db: AsyncSession, org_id: UUID, user_id: UUID
    ) -> OrganizationMemberModel | None:
        stmt = select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == org_id,
            OrganizationMemberModel.user_id == user_id,
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @staticmethod
    def _to_response(
        org: OrganizationModel, members_count: int, user_role: str
    ) -> OrganizationResponse:
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            description=org.description,
            storage_quota_bytes=org.storage_quota_bytes,
            storage_used_bytes=org.storage_used_bytes,
            token_quota=org.token_quota,
            tokens_used=org.tokens_used,
            members_count=members_count,
            user_role=user_role,
            created_at=org.created_at,
        )
