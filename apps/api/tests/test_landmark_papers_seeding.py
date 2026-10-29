"""Unit & Integration test for Landmark LLM Papers Seeding (Task 6)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.user import UserModel
from api.services.auth_service import AuthService
from api.services.landmark_papers_seeder import (
    LANDMARK_PAPERS,
    seed_landmark_papers_for_user,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_landmark_papers_seeding(db_session: AsyncSession) -> None:
    # 1. Create a clean test user
    test_user = UserModel(
        id=uuid4(),
        email=f"scholar.landmarks.{uuid4().hex[:6]}@verischolar.edu.vn",
        full_name="Prof. LLM Landmark",
        hashed_password=AuthService.hash_password("ScholarDev@123456"),
        is_active=True,
        is_verified=True,
        role="researcher",
    )
    db_session.add(test_user)
    await db_session.flush()

    # 2. Seed landmark papers for test user
    seeded_count = await seed_landmark_papers_for_user(db_session, test_user.id)
    assert seeded_count == len(LANDMARK_PAPERS)
    assert seeded_count >= 12

    # 3. Verify documents in DB are persistent and completed
    docs_res = await db_session.execute(
        select(DocumentModel).where(DocumentModel.user_id == test_user.id)
    )
    docs = docs_res.scalars().all()
    assert len(docs) == len(LANDMARK_PAPERS)

    for doc in docs:
        assert doc.is_persistent is True
        assert doc.status == "completed"
        assert doc.title is not None
        assert doc.authors is not None

    # 4. Verify cross-paper citation links in reference_items
    refs_res = await db_session.execute(
        select(ReferenceItemModel).where(ReferenceItemModel.document_id.in_([d.id for d in docs]))
    )
    refs = refs_res.scalars().all()
    assert len(refs) > 0

    # Ensure landmark papers like Attention are cited by others
    attention_doc = next(d for d in docs if "Attention Is All You Need" in (d.title or ""))
    attention_citations = [
        r
        for r in refs
        if r.resolved_document_id == attention_doc.id
        or (r.parsed_title and "Attention Is All You Need" in r.parsed_title)
    ]
    assert len(attention_citations) >= 3
