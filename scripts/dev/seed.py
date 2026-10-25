#!/usr/bin/env -S uv run python3
"""Deterministic Seed Script for VeriScholar Local Development & Sandboxing.

Seeds:
1. Default scholar user (dev@verischolar.edu.vn / ScholarDev@123456)
2. 3 classic academic papers (Attention, ResNet, BERT) with physical CAS blobs in storage/blobs/
3. Sample text chunks with spatial bounding boxes [x0, y0, x1, y1]
4. Sample reading session and LaTeX draft
"""

from __future__ import annotations

import asyncio
import hashlib
import sys
from pathlib import Path
from uuid import UUID, uuid4

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "api" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "core" / "src"))

from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.draft import DraftModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.db.session import AsyncSessionLocal
from api.services.auth_service import AuthService
from sqlalchemy import select

# Minimal valid 1-page PDF template for testing
MINIMAL_PDF_1 = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000102 00000 n \n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n"
)

MINIMAL_PDF_2 = (
    b"%PDF-1.4\n%BERT\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000016 00000 n \n0000000059 00000 n \n0000000108 00000 n \n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n184\n%%EOF\n"
)


def ensure_cas_blob(content_bytes: bytes, blobs_dir: Path) -> tuple[str, str, int]:
    """Saves physical binary bytes into storage/blobs/{hash[:2]}/{hash[2:4]}/{hash}."""
    content_hash = hashlib.sha256(content_bytes).hexdigest()
    storage_subpath = Path(content_hash[:2]) / content_hash[2:4] / content_hash
    target_path = blobs_dir / storage_subpath
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.exists():
        target_path.write_bytes(content_bytes)
    return content_hash, str(storage_subpath), len(content_bytes)


async def seed_database() -> None:
    blobs_dir = ROOT_DIR / "storage" / "blobs"
    blobs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Prepare Physical PDF Blobs
    print("Preparing physical CAS PDF blobs in storage/blobs/...")
    attention_src = ROOT_DIR / "data" / "papers" / "Attention Is All You Need.pdf"
    if attention_src.exists():
        attention_bytes = attention_src.read_bytes()
    else:
        attention_bytes = MINIMAL_PDF_1

    h_attn, p_attn, s_attn = ensure_cas_blob(attention_bytes, blobs_dir)
    h_resnet, p_resnet, s_resnet = ensure_cas_blob(MINIMAL_PDF_1, blobs_dir)
    h_bert, p_bert, s_bert = ensure_cas_blob(MINIMAL_PDF_2, blobs_dir)
    print(f"  - Attention: {h_attn[:12]}... ({s_attn} bytes)")
    print(f"  - ResNet:    {h_resnet[:12]}... ({s_resnet} bytes)")
    print(f"  - BERT:      {h_bert[:12]}... ({s_bert} bytes)")

    try:
        async with AsyncSessionLocal() as session:
            # 2. Seed Default User
            user_stmt = select(UserModel).where(UserModel.email == "dev@verischolar.edu.vn")
            res = await session.execute(user_stmt)
            dev_user = res.scalar_one_or_none()

            if not dev_user:
                print("Seeding default scholar user: dev@verischolar.edu.vn...")
                dev_user = UserModel(
                    id=uuid4(),
                    email="dev@verischolar.edu.vn",
                    full_name="Scholar Dev",
                    hashed_password=AuthService.hash_password("ScholarDev@123456"),
                    is_active=True,
                    is_verified=True,
                    role="researcher",
                    institution="VeriScholar Research Lab",
                    academic_rank="Senior Researcher",
                    bio="Standard offline dev user for deterministic evaluation.",
                )
                session.add(dev_user)
                await session.flush()
            else:
                print("Default user already exists.")

            # 3. Seed Blobs in DB
            papers_data = [
                (h_attn, p_attn, s_attn, "Attention Is All You Need.pdf", "Attention Is All You Need", ["Vaswani et al."], 2017),
                (h_resnet, p_resnet, s_resnet, "Deep Residual Learning for Image Recognition.pdf", "Deep Residual Learning for Image Recognition", ["He et al."], 2016),
                (h_bert, p_bert, s_bert, "BERT: Pre-training of Deep Bidirectional Transformers.pdf", "BERT: Pre-training of Deep Bidirectional Transformers", ["Devlin et al."], 2018),
            ]

            seeded_doc_ids: list[UUID] = []

            for chash, spath, fsize, fname, title, authors, year in papers_data:
                blob_stmt = select(DocumentStorageBlobModel).where(DocumentStorageBlobModel.content_hash == chash)
                blob_res = await session.execute(blob_stmt)
                blob = blob_res.scalar_one_or_none()
                if not blob:
                    blob = DocumentStorageBlobModel(
                        id=uuid4(),
                        content_hash=chash,
                        storage_path=spath,
                        file_size_bytes=fsize,
                        ref_count=1,
                        status="ready",
                    )
                    session.add(blob)
                    await session.flush()

                doc_stmt = select(DocumentModel).where(
                    DocumentModel.user_id == dev_user.id,
                    DocumentModel.content_hash == chash,
                )
                doc_res = await session.execute(doc_stmt)
                doc = doc_res.scalar_one_or_none()
                if not doc:
                    doc = DocumentModel(
                        id=uuid4(),
                        user_id=dev_user.id,
                        blob_id=blob.id,
                        filename=fname,
                        title=title,
                        authors=authors,
                        publication_year=year,
                        content_hash=chash,
                        file_size_bytes=fsize,
                        page_count=15 if "Attention" in fname else 10,
                        chunk_count=10 if "Attention" in fname else 1,
                        status="ready",
                        stage="completed",
                        progress=100,
                        is_persistent=True,
                    )
                    session.add(doc)
                    await session.flush()

                seeded_doc_ids.append(doc.id)

                # Seed sample chunks with bounding boxes for Attention
                if "Attention" in fname:
                    chunk_stmt = select(DocumentChunkModel).where(DocumentChunkModel.document_id == doc.id)
                    chunk_res = await session.execute(chunk_stmt)
                    if not chunk_res.first():
                        sample_chunks = [
                            ("The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.", 1, [0.1, 0.2, 0.9, 0.25]),
                            ("The Transformer is the first transduction model relying entirely on self-attention to compute representations.", 1, [0.1, 0.26, 0.9, 0.32]),
                            ("Recurrent models typically factor computation along the symbol positions of the input and output sequences.", 2, [0.12, 0.15, 0.88, 0.22]),
                            ("Attention mechanisms have become an integral part of compelling sequence modeling and transduction models.", 2, [0.12, 0.23, 0.88, 0.30]),
                            ("An attention function can be described as mapping a query and a set of key-value pairs to an output.", 3, [0.15, 0.1, 0.85, 0.18]),
                        ]
                        for idx, (text_content, page_num, bbox) in enumerate(sample_chunks):
                            chunk = DocumentChunkModel(
                                id=uuid4(),
                                document_id=doc.id,
                                chunk_index=idx,
                                page_number=page_num,
                                content=text_content,
                                bounding_boxes=[bbox],
                                token_count=len(text_content.split()),
                                embedding=[0.0] * 1536,
                            )
                            session.add(chunk)
                        await session.flush()

            # 4. Seed Reading Session
            session_stmt = select(ResearchSessionModel).where(ResearchSessionModel.user_id == dev_user.id)
            session_res = await session.execute(session_stmt)
            r_session = session_res.scalar_one_or_none()
            if not r_session and seeded_doc_ids:
                primary_doc_id = seeded_doc_ids[0]
                r_session = ResearchSessionModel(
                    id=uuid4(),
                    user_id=dev_user.id,
                    title="Deep Reading: Attention Mechanism & Transformers",
                    active_document_id=primary_doc_id,
                    viewport_state={"page": 1, "zoom_ratio": 1.25, "scroll_top": 0.0},
                    active_tab="chat",
                )
                session.add(r_session)
                await session.flush()

                session_doc = SessionDocumentModel(
                    session_id=r_session.id,
                    document_id=primary_doc_id,
                    document_order=0,
                )
                session.add(session_doc)
                await session.flush()

            # 5. Seed LaTeX Draft
            draft_stmt = select(DraftModel).where(DraftModel.user_id == dev_user.id)
            draft_res = await session.execute(draft_stmt)
            draft = draft_res.scalar_one_or_none()
            if not draft:
                draft = DraftModel(
                    id=uuid4(),
                    user_id=dev_user.id,
                    title="A Comparative Survey on Modern Attention Architectures",
                    content=(
                        "\\documentclass{article}\n"
                        "\\usepackage{amsmath}\n"
                        "\\title{A Comparative Survey on Modern Attention Architectures}\n"
                        "\\author{Scholar Dev}\n"
                        "\\begin{document}\n"
                        "\\maketitle\n"
                        "\\section{Introduction}\n"
                        "The Transformer architecture \\cite{vaswani2017attention} has revolutionized natural language processing.\n"
                        "\\end{document}\n"
                    ),
                    format="latex",
                    template="blank",
                    version=1,
                )
                session.add(draft)
                await session.flush()

            await session.commit()
            print("Deterministic seeding completed successfully in database.")
    except Exception as exc:
        print(f"Database unavailable or offline ({exc}). Physical CAS blobs are prepared for offline testing.")


def main():
    print("=== VeriScholar Offline Seeder ===")
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
