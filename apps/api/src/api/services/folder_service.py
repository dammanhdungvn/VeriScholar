"""Folder management service for hierarchical research projects (Module 4)."""

from __future__ import annotations

from uuid import UUID

import structlog
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.schemas.folder import (
    FolderCreateRequest,
    FolderResponseData,
    FolderTreeItem,
    FolderUpdateRequest,
)
from core.services.graph_extractor import detect_folder_cycle
from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.folder_service")


class FolderService:
    """Service handling CRUD operations and hierarchical tree generation for research folders."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_folder(
        self, user_id: UUID, payload: FolderCreateRequest
    ) -> FolderResponseData:
        """Create a new folder under an optional parent folder."""
        # If parent_id specified, verify parent exists and belongs to user
        if payload.parent_id:
            parent = await self._get_user_folder(user_id, payload.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thư mục cha không tồn tại hoặc không thuộc quyền sở hữu của bạn.",
                )

        # Check unique constraint on (user_id, parent_id, name)
        stmt_check = select(FolderModel).where(
            FolderModel.user_id == user_id,
            FolderModel.parent_id == payload.parent_id,
            FolderModel.name == payload.name,
        )
        existing = (await self.db.execute(stmt_check)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Thư mục '{payload.name}' đã tồn tại trong cùng cấp thư mục.",
            )

        folder = FolderModel(
            user_id=user_id,
            name=payload.name,
            parent_id=payload.parent_id,
            color=payload.color or "#6366f1",
            description=payload.description,
        )
        self.db.add(folder)
        await self.db.commit()
        await self.db.refresh(folder)

        logger.info(
            "folder.created", folder_id=str(folder.id), user_id=str(user_id), name=folder.name
        )
        return FolderResponseData(
            id=folder.id,
            user_id=folder.user_id,
            name=folder.name,
            parent_id=folder.parent_id,
            color=folder.color,
            description=folder.description,
            document_count=0,
            subfolder_count=0,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
        )

    async def get_folder(self, user_id: UUID, folder_id: UUID) -> FolderResponseData:
        """Retrieve single folder details with document count and subfolder count."""
        folder = await self._get_user_folder(user_id, folder_id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FOLDER_NOT_FOUND",
                    "message": "Không tìm thấy thư mục đề tài yêu cầu.",
                    "field": "folder_id",
                    "action": "Chọn thư mục tồn tại trong cây thư mục cá nhân.",
                },
            )

        doc_count = await self._get_document_count(user_id, folder_id)
        sub_count = await self._get_subfolder_count(user_id, folder_id)

        return FolderResponseData(
            id=folder.id,
            user_id=folder.user_id,
            name=folder.name,
            parent_id=folder.parent_id,
            color=folder.color,
            description=folder.description,
            document_count=doc_count,
            subfolder_count=sub_count,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
        )

    async def list_folders(self, user_id: UUID) -> list[FolderResponseData]:
        """List all folders for user with document counts."""
        stmt = (
            select(FolderModel)
            .where(FolderModel.user_id == user_id)
            .order_by(FolderModel.name.asc())
        )
        folders = (await self.db.execute(stmt)).scalars().all()

        results: list[FolderResponseData] = []
        for f in folders:
            doc_count = await self._get_document_count(user_id, f.id)
            sub_count = await self._get_subfolder_count(user_id, f.id)
            results.append(
                FolderResponseData(
                    id=f.id,
                    user_id=f.user_id,
                    name=f.name,
                    parent_id=f.parent_id,
                    color=f.color,
                    description=f.description,
                    document_count=doc_count,
                    subfolder_count=sub_count,
                    created_at=f.created_at,
                    updated_at=f.updated_at,
                )
            )
        return results

    async def get_folder_tree(self, user_id: UUID) -> list[FolderTreeItem]:
        """Build hierarchical nested tree of all folders for the user."""
        stmt = (
            select(FolderModel)
            .where(FolderModel.user_id == user_id)
            .order_by(FolderModel.name.asc())
        )
        all_folders = (await self.db.execute(stmt)).scalars().all()

        # Pre-calculate doc counts
        doc_counts: dict[UUID, int] = {}
        for f in all_folders:
            doc_counts[f.id] = await self._get_document_count(user_id, f.id)

        # Build tree nodes
        nodes: dict[UUID, FolderTreeItem] = {}
        for f in all_folders:
            nodes[f.id] = FolderTreeItem(
                id=f.id,
                name=f.name,
                parent_id=f.parent_id,
                color=f.color,
                description=f.description,
                document_count=doc_counts.get(f.id, 0),
                subfolders=[],
            )

        root_items: list[FolderTreeItem] = []
        for f in all_folders:
            item = nodes[f.id]
            if f.parent_id and f.parent_id in nodes:
                nodes[f.parent_id].subfolders.append(item)
            else:
                root_items.append(item)

        return root_items

    async def update_folder(
        self, user_id: UUID, folder_id: UUID, payload: FolderUpdateRequest
    ) -> FolderResponseData:
        """Update folder name, parent (move), color, or description with cycle prevention."""
        folder = await self._get_user_folder(user_id, folder_id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FOLDER_NOT_FOUND",
                    "message": "Không tìm thấy thư mục đề tài yêu cầu.",
                    "field": "folder_id",
                    "action": "Chọn thư mục tồn tại trong cây thư mục cá nhân.",
                },
            )

        if payload.parent_id is not None:
            # Query all user folders to construct parent_map for cycle detection
            all_stmt = select(FolderModel).where(FolderModel.user_id == user_id)
            all_folders = (await self.db.execute(all_stmt)).scalars().all()
            parent_map = {f.id: f.parent_id for f in all_folders}

            if detect_folder_cycle(
                folder_id=folder_id,
                new_parent_id=payload.parent_id,
                parent_map=parent_map,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "CYCLIC_FOLDER_HIERARCHY",
                        "message": (
                            "Không thể di chuyển thư mục vào chính nó hoặc vào thư mục con của nó."
                        ),
                        "field": "parent_id",
                        "action": "Chọn thư mục cha hợp lệ không gây vòng lặp.",
                    },
                )
            parent = await self._get_user_folder(user_id, payload.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "FOLDER_NOT_FOUND",
                        "message": "Không tìm thấy thư mục đề tài yêu cầu.",
                        "field": "parent_id",
                        "action": "Chọn thư mục tồn tại trong cây thư mục cá nhân.",
                    },
                )
            folder.parent_id = payload.parent_id

        if payload.name:
            folder.name = payload.name.strip()
        if payload.color:
            folder.color = payload.color.strip()
        if payload.description is not None:
            folder.description = payload.description.strip() or None

        await self.db.commit()
        await self.db.refresh(folder)

        doc_count = await self._get_document_count(user_id, folder_id)
        sub_count = await self._get_subfolder_count(user_id, folder_id)

        return FolderResponseData(
            id=folder.id,
            user_id=folder.user_id,
            name=folder.name,
            parent_id=folder.parent_id,
            color=folder.color,
            description=folder.description,
            document_count=doc_count,
            subfolder_count=sub_count,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
        )

    async def delete_folder(self, user_id: UUID, folder_id: UUID) -> dict[str, str]:
        """Delete folder safely, re-assigning documents to root (folder_id=None)."""
        folder = await self._get_user_folder(user_id, folder_id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thư mục không tồn tại.",
            )

        # 1. Reassign documents to root
        await self.db.execute(
            update(DocumentModel)
            .where(DocumentModel.user_id == user_id, DocumentModel.folder_id == folder_id)
            .values(folder_id=None)
        )

        # 2. Reassign direct subfolders to parent
        await self.db.execute(
            update(FolderModel)
            .where(FolderModel.user_id == user_id, FolderModel.parent_id == folder_id)
            .values(parent_id=folder.parent_id)
        )

        # 3. Delete the folder
        await self.db.delete(folder)
        await self.db.commit()

        logger.info("folder.deleted", folder_id=str(folder_id), user_id=str(user_id))
        return {"status": "deleted", "message": f"Thư mục '{folder.name}' đã được xóa thành công."}

    async def assign_documents(
        self, user_id: UUID, folder_id: UUID, document_ids: list[UUID]
    ) -> dict[str, int]:
        """Assign documents to a folder."""
        folder = await self._get_user_folder(user_id, folder_id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thư mục không tồn tại.",
            )

        stmt = (
            update(DocumentModel)
            .where(DocumentModel.user_id == user_id, DocumentModel.id.in_(document_ids))
            .values(folder_id=folder_id)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()

        updated_count = res.rowcount or len(document_ids)
        return {"assigned_count": updated_count}

    async def remove_documents(
        self, user_id: UUID, folder_id: UUID, document_ids: list[UUID]
    ) -> dict[str, int]:
        """Remove documents from folder back to root library."""
        stmt = (
            update(DocumentModel)
            .where(
                DocumentModel.user_id == user_id,
                DocumentModel.folder_id == folder_id,
                DocumentModel.id.in_(document_ids),
            )
            .values(folder_id=None)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return {"removed_count": res.rowcount or len(document_ids)}

    # Helper methods
    async def _get_user_folder(self, user_id: UUID, folder_id: UUID) -> FolderModel | None:
        stmt = select(FolderModel).where(
            FolderModel.id == folder_id, FolderModel.user_id == user_id
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def _get_document_count(self, user_id: UUID, folder_id: UUID) -> int:
        stmt = select(func.count(DocumentModel.id)).where(
            DocumentModel.user_id == user_id, DocumentModel.folder_id == folder_id
        )
        return (await self.db.execute(stmt)).scalar_one() or 0

    async def _get_subfolder_count(self, user_id: UUID, folder_id: UUID) -> int:
        stmt = select(func.count(FolderModel.id)).where(
            FolderModel.user_id == user_id, FolderModel.parent_id == folder_id
        )
        return (await self.db.execute(stmt)).scalar_one() or 0

    async def _is_descendant(self, user_id: UUID, ancestor_id: UUID, target_id: UUID) -> bool:
        """Traverse up from target_id to see if ancestor_id is in its ancestry."""
        curr_id: UUID | None = target_id
        visited: set[UUID] = set()
        while curr_id:
            if curr_id in visited:
                break
            visited.add(curr_id)
            if curr_id == ancestor_id:
                return True
            parent_f = await self._get_user_folder(user_id, curr_id)
            if not parent_f:
                break
            curr_id = parent_f.parent_id
        return False
