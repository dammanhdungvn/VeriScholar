"""Application service for Project Folders management (CRUD, hierarchy, cycle prevention)."""

from datetime import UTC, datetime
from uuid import UUID

from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.schemas.folder import (
    FolderCreateRequest,
    FolderItemResponseData,
    FolderUpdateRequest,
)
from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class FolderService:
    """Orchestrates hierarchical folder tree management and document categorization."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_folders(self, user_id: UUID) -> list[FolderItemResponseData]:
        """List all research project folders for the user with document counts."""
        # 1. Fetch all folders belonging to user
        folder_stmt = (
            select(FolderModel)
            .where(FolderModel.user_id == user_id)
            .order_by(FolderModel.name.asc())
        )
        folder_res = await self.db.execute(folder_stmt)
        folders = list(folder_res.scalars().all())

        if not folders:
            return []

        # 2. Aggregate document count per folder
        doc_count_stmt = (
            select(DocumentModel.folder_id, func.count(DocumentModel.id).label("doc_count"))
            .where(
                DocumentModel.user_id == user_id,
                DocumentModel.is_persistent.is_(True),
                DocumentModel.folder_id.is_not(None),
            )
            .group_by(DocumentModel.folder_id)
        )
        doc_res = await self.db.execute(doc_count_stmt)
        counts_map: dict[UUID, int] = {
            row[0]: row[1] for row in doc_res.all() if row[0] is not None
        }

        now = datetime.now(UTC)
        return [
            FolderItemResponseData(
                id=f.id,
                name=f.name,
                parent_id=f.parent_id,
                document_count=counts_map.get(f.id, 0),
                created_at=f.created_at or now,
                updated_at=f.updated_at or now,
            )
            for f in folders
        ]

    async def create_folder(
        self,
        user_id: UUID,
        req: FolderCreateRequest,
    ) -> FolderItemResponseData:
        """Create a new research topic folder, validating parent hierarchy and uniqueness."""
        clean_name = req.name.strip()
        if not clean_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_FOLDER_NAME",
                    "message": "Folder name cannot be empty.",
                    "field": "name",
                    "action": "Provide a non-empty name.",
                },
            )

        # 1. Validate parent folder if specified
        if req.parent_id is not None:
            parent_stmt = select(FolderModel).where(
                FolderModel.id == req.parent_id,
                FolderModel.user_id == user_id,
            )
            parent_res = await self.db.execute(parent_stmt)
            if parent_res.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PARENT_FOLDER_NOT_FOUND",
                        "message": f"Parent folder '{req.parent_id}' does not exist.",
                        "field": "parent_id",
                        "action": "Select an existing parent folder or omit parent_id for root.",
                    },
                )

        # 2. Check for duplicate name under same parent
        parent_cond = (
            FolderModel.parent_id == req.parent_id
            if req.parent_id is not None
            else FolderModel.parent_id.is_(None)
        )
        dup_stmt = select(FolderModel).where(
            FolderModel.user_id == user_id,
            parent_cond,
            FolderModel.name == clean_name,
        )
        dup_res = await self.db.execute(dup_stmt)
        if dup_res.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "DUPLICATE_FOLDER_NAME",
                    "message": f"A folder named '{clean_name}' already exists in this location.",
                    "field": "name",
                    "action": "Choose a different name or use the existing folder.",
                },
            )

        # 3. Insert and persist
        folder = FolderModel(
            user_id=user_id,
            name=clean_name,
            parent_id=req.parent_id,
        )
        self.db.add(folder)
        await self.db.commit()
        await self.db.refresh(folder)

        now = datetime.now(UTC)
        return FolderItemResponseData(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            document_count=0,
            created_at=folder.created_at or now,
            updated_at=folder.updated_at or now,
        )

    async def update_folder(
        self,
        user_id: UUID,
        folder_id: UUID,
        req: FolderUpdateRequest,
    ) -> FolderItemResponseData:
        """Update folder name and/or parent_id with cycle detection."""
        # 1. Fetch target folder
        stmt = select(FolderModel).where(
            FolderModel.id == folder_id,
            FolderModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        folder = res.scalar_one_or_none()
        if folder is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FOLDER_NOT_FOUND",
                    "message": f"Folder '{folder_id}' not found.",
                    "field": "folder_id",
                    "action": "Verify folder ID.",
                },
            )

        target_name = req.name.strip() if req.name is not None else folder.name
        if not target_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_FOLDER_NAME",
                    "message": "Folder name cannot be empty.",
                    "field": "name",
                    "action": "Provide a non-empty name.",
                },
            )

        target_parent_id = (
            req.parent_id if "parent_id" in req.model_fields_set else folder.parent_id
        )

        # 2. Cycle prevention & parent validation
        if target_parent_id is not None:
            if target_parent_id == folder_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "CYCLIC_PARENT_ERROR",
                        "message": "A folder cannot be its own parent.",
                        "field": "parent_id",
                        "action": "Select a distinct parent folder.",
                    },
                )

            # Verify parent exists
            parent_stmt = select(FolderModel).where(
                FolderModel.id == target_parent_id,
                FolderModel.user_id == user_id,
            )
            parent_res = await self.db.execute(parent_stmt)
            target_parent = parent_res.scalar_one_or_none()
            if target_parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PARENT_FOLDER_NOT_FOUND",
                        "message": f"Target parent folder '{target_parent_id}' not found.",
                        "field": "parent_id",
                        "action": "Select an existing parent folder.",
                    },
                )

            # Cycle detection: traverse ancestors of target_parent
            curr_ancestor_id = target_parent.parent_id
            visited: set[UUID] = {target_parent_id}
            while curr_ancestor_id is not None:
                if curr_ancestor_id == folder_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "code": "CYCLIC_HIERARCHY_ERROR",
                            "message": "Cannot move folder into one of its descendant folders.",
                            "field": "parent_id",
                            "action": "Choose a parent that is not inside this folder.",
                        },
                    )
                if curr_ancestor_id in visited:
                    break
                visited.add(curr_ancestor_id)
                ancestor_stmt = select(FolderModel).where(
                    FolderModel.id == curr_ancestor_id,
                    FolderModel.user_id == user_id,
                )
                ancestor_res = await self.db.execute(ancestor_stmt)
                anc = ancestor_res.scalar_one_or_none()
                curr_ancestor_id = anc.parent_id if anc else None

        # 3. Duplicate sibling check if name or parent changed
        if target_name != folder.name or target_parent_id != folder.parent_id:
            target_parent_cond = (
                FolderModel.parent_id == target_parent_id
                if target_parent_id is not None
                else FolderModel.parent_id.is_(None)
            )
            dup_stmt = select(FolderModel).where(
                FolderModel.user_id == user_id,
                FolderModel.id != folder_id,
                target_parent_cond,
                FolderModel.name == target_name,
            )
            dup_res = await self.db.execute(dup_stmt)
            if dup_res.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "DUPLICATE_FOLDER_NAME",
                        "message": (
                            f"A folder named '{target_name}' already exists in the target location."
                        ),
                        "field": "name",
                        "action": "Choose a different name or target parent.",
                    },
                )

        # 4. Apply changes
        folder.name = target_name
        folder.parent_id = target_parent_id
        folder.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(folder)

        # Count documents
        doc_count_stmt = select(func.count(DocumentModel.id)).where(
            DocumentModel.user_id == user_id,
            DocumentModel.is_persistent.is_(True),
            DocumentModel.folder_id == folder.id,
        )
        doc_count_res = await self.db.execute(doc_count_stmt)
        count = doc_count_res.scalar_one() or 0

        now = datetime.now(UTC)
        return FolderItemResponseData(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            document_count=count,
            created_at=folder.created_at or now,
            updated_at=folder.updated_at or now,
        )

    async def delete_folder(self, user_id: UUID, folder_id: UUID) -> bool:
        """Delete folder and cleanly uncategorize documents to prevent orphan data loss."""
        # 1. Fetch folder
        stmt = select(FolderModel).where(
            FolderModel.id == folder_id,
            FolderModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        folder = res.scalar_one_or_none()
        if folder is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FOLDER_NOT_FOUND",
                    "message": f"Folder '{folder_id}' not found.",
                    "field": "folder_id",
                    "action": "Verify folder ID.",
                },
            )

        # 2. Gather all descendant folders to uncategorize all contained documents
        all_user_folders_stmt = select(FolderModel).where(FolderModel.user_id == user_id)
        all_res = await self.db.execute(all_user_folders_stmt)
        all_folders = list(all_res.scalars().all())

        # Build parent -> children map
        children_map: dict[UUID, list[UUID]] = {}
        for f in all_folders:
            if f.parent_id:
                children_map.setdefault(f.parent_id, []).append(f.id)

        subtree_ids: set[UUID] = {folder_id}
        queue = [folder_id]
        while queue:
            curr = queue.pop(0)
            for child_id in children_map.get(curr, []):
                if child_id not in subtree_ids:
                    subtree_ids.add(child_id)
                    queue.append(child_id)

        # 3. Uncategorize documents in this folder subtree (Zero Data Loss for research papers)
        await self.db.execute(
            update(DocumentModel)
            .where(
                DocumentModel.user_id == user_id,
                DocumentModel.folder_id.in_(subtree_ids),
            )
            .values(folder_id=None)
        )

        # 4. Delete the folder (cascades to child folders via DB foreign key)
        await self.db.delete(folder)
        await self.db.commit()
        return True
