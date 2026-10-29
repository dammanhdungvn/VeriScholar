"""Service for seeding landmark LLM papers and citation graph edges into user libraries."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import structlog
from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.graph import GraphEdgeModel, GraphNodeModel
from api.db.models.reference import ReferenceItemModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.landmark_papers_seeder")


def generate_minimal_pdf(title: str) -> bytes:
    """Generate minimal valid 1-page PDF binary with text stream."""
    escaped = title.replace("(", "").replace(")", "").replace("\\", "")
    stream_content = f"BT /F1 12 Tf 72 712 Td ({escaped}) Tj ET\n".encode("ascii", errors="replace")
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
        b"/Contents 4 0 R/Resources<<>>>>endobj\n"
        b"4 0 obj<</Length "
        + str(len(stream_content)).encode("ascii")
        + b">>stream\n"
        + stream_content
        + b"endstream\nendobj\n"
        b"xref\n0 5\n"
        b"0000000000 65535 f \n"
        b"0000000010 00000 n \n"
        b"0000000053 00000 n \n"
        b"0000000102 00000 n \n"
        b"0000000195 00000 n \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n320\n%%EOF\n"
    )


LANDMARK_PAPERS: list[dict[str, Any]] = [
    {
        "id_key": "attention",
        "title": "Attention Is All You Need",
        "filename": "Attention Is All You Need.pdf",
        "authors": [
            "Ashish Vaswani",
            "Noam Shazeer",
            "Niki Parmar",
            "Jakob Uszkoreit",
            "Llion Jones",
            "Aidan N. Gomez",
            "Lukasz Kaiser",
            "Illia Polosukhin",
        ],
        "publication_year": 2017,
        "doi": "10.48550/arXiv.1706.03762",
        "page_count": 15,
        "abstract": (
            "We propose a new simple network architecture, the Transformer, "
            "based solely on attention mechanisms, dispensing with recurrence "
            "and convolutions entirely."
        ),
        "cites": [],
    },
    {
        "id_key": "bert",
        "title": (
            "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
        ),
        "filename": "BERT Pre-training of Deep Bidirectional Transformers.pdf",
        "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        "publication_year": 2018,
        "doi": "10.48550/arXiv.1810.04805",
        "page_count": 16,
        "abstract": (
            "We introduce a new language representation model called BERT, "
            "which stands for Bidirectional Encoder Representations from Transformers."
        ),
        "cites": ["attention"],
    },
    {
        "id_key": "gpt3",
        "title": "Language Models are Few-Shot Learners",
        "filename": "Language Models are Few-Shot Learners GPT-3.pdf",
        "authors": [
            "Tom B. Brown",
            "Benjamin Mann",
            "Nick Ryder",
            "Melanie Subbiah",
            "Dario Amodei",
        ],
        "publication_year": 2020,
        "doi": "10.48550/arXiv.2005.14165",
        "page_count": 75,
        "abstract": (
            "Here we show that scaling up language models greatly improves "
            "task-agnostic, few-shot performance on diverse NLP benchmarks."
        ),
        "cites": ["attention"],
    },
    {
        "id_key": "lora",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "filename": "LoRA Low-Rank Adaptation of Large Language Models.pdf",
        "authors": [
            "Edward J. Hu",
            "Yelong Shen",
            "Phillip Wallis",
            "Zeyuan Allen-Zhu",
            "Weizhu Chen",
        ],
        "publication_year": 2021,
        "doi": "10.48550/arXiv.2106.09685",
        "page_count": 26,
        "abstract": (
            "We propose Low-Rank Adaptation, or LoRA, which freezes the pre-trained "
            "model weights and injects trainable rank decomposition matrices."
        ),
        "cites": ["attention", "gpt3"],
    },
    {
        "id_key": "cot",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "filename": "Chain-of-Thought Prompting Elicits Reasoning.pdf",
        "authors": ["Jason Wei", "Xuezhi Wang", "Dale Schuurmans", "Maarten Bosma", "Denny Zhou"],
        "publication_year": 2022,
        "doi": "10.48550/arXiv.2201.11903",
        "page_count": 43,
        "abstract": (
            "We explore how generating a chain of thought significantly improves "
            "the ability of large language models to perform complex reasoning."
        ),
        "cites": ["attention", "gpt3"],
    },
    {
        "id_key": "react",
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "filename": "ReAct Synergizing Reasoning and Acting.pdf",
        "authors": [
            "Shunyu Yao",
            "Jeffrey Zhao",
            "Dian Yu",
            "Nan Du",
            "Karthik Narasimhan",
            "Yuan Cao",
        ],
        "publication_year": 2022,
        "doi": "10.48550/arXiv.2210.03629",
        "page_count": 33,
        "abstract": (
            "We explore using LLMs to generate both reasoning traces and "
            "task-specific actions in an interleaved manner."
        ),
        "cites": ["gpt3", "cot"],
    },
    {
        "id_key": "rag",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "filename": "Retrieval-Augmented Generation for Knowledge-Intensive NLP.pdf",
        "authors": [
            "Patrick Lewis",
            "Ethan Perez",
            "Aleksandra Piktus",
            "Fabio Petroni",
            "Douwe Kiela",
        ],
        "publication_year": 2020,
        "doi": "10.48550/arXiv.2005.11401",
        "page_count": 19,
        "abstract": (
            "We explore a general-purpose fine-tuning recipe for retrieval-augmented "
            "generation (RAG) combining parametric memory with non-parametric retrieval."
        ),
        "cites": ["attention", "bert"],
    },
    {
        "id_key": "graphrag",
        "title": "From Local to Global: A Graph RAG Approach to Query-Focused Summarization",
        "filename": "From Local to Global A Graph RAG Approach.pdf",
        "authors": [
            "Darren Edge",
            "Ha Trinh",
            "Newman Cheng",
            "Joshua Bradley",
            "Jonathan Larson",
        ],
        "publication_year": 2024,
        "doi": "10.48550/arXiv.2404.16130",
        "page_count": 22,
        "abstract": (
            "We present Graph RAG, which combines knowledge graph generation, "
            "community detection, and summarization to answer global queries over corpora."
        ),
        "cites": ["attention", "gpt3", "rag"],
    },
    {
        "id_key": "toolformer",
        "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
        "filename": "Toolformer Language Models Can Teach Themselves to Use Tools.pdf",
        "authors": ["Timo Schick", "Jane Dwivedi-Yu", "Roberto Dessì", "Thomas Scialom"],
        "publication_year": 2023,
        "doi": "10.48550/arXiv.2302.04761",
        "page_count": 18,
        "abstract": (
            "We show that LMs can teach themselves to use external tools via "
            "simple APIs, achieving the best of both worlds."
        ),
        "cites": ["attention", "gpt3", "react"],
    },
    {
        "id_key": "llama",
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "filename": "LLaMA Open and Efficient Foundation Language Models.pdf",
        "authors": ["Hugo Touvron", "Thibaut Lavril", "Gautier Izacard", "Guillaume Lample"],
        "publication_year": 2023,
        "doi": "10.48550/arXiv.2302.13971",
        "page_count": 27,
        "abstract": (
            "We introduce LLaMA, a collection of foundation language models ranging "
            "from 7B to 65B parameters trained on trillions of tokens."
        ),
        "cites": ["attention", "gpt3", "lora"],
    },
    {
        "id_key": "ragas",
        "title": "RAGAS: Automated Evaluation of Retrieval Augmented Generation",
        "filename": "RAGAS Automated Evaluation of Retrieval Augmented Generation.pdf",
        "authors": ["Shahul Es", "Jithin James", "Luis Espinosa-Anke", "Steven Schockaert"],
        "publication_year": 2023,
        "doi": "10.48550/arXiv.2309.15217",
        "page_count": 12,
        "abstract": (
            "We propose RAGAS, an automated evaluation framework for RAG systems "
            "based on faithfulness, answer relevance, and context precision."
        ),
        "cites": ["attention", "rag"],
    },
    {
        "id_key": "dpo",
        "title": ("Direct Preference Optimization: Your Language Model is Secretly a Reward Model"),
        "filename": "Direct Preference Optimization.pdf",
        "authors": [
            "Rafael Rafailov",
            "Archit Sharma",
            "Eric Mitchell",
            "Christopher D. Manning",
            "Chelsea Finn",
        ],
        "publication_year": 2023,
        "doi": "10.48550/arXiv.2305.18290",
        "page_count": 24,
        "abstract": (
            "We propose Direct Preference Optimization (DPO), a simple algorithm that "
            "implicitly optimizes the same objective as RLHF without training a reward model."
        ),
        "cites": ["attention", "gpt3", "llama"],
    },
]


def _ensure_cas_blob(content_bytes: bytes, blobs_dir: Path) -> tuple[str, str, int]:
    content_hash = hashlib.sha256(content_bytes).hexdigest()
    storage_subpath = Path(content_hash[:2]) / content_hash[2:4] / content_hash
    target_path = blobs_dir / storage_subpath
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.exists():
        target_path.write_bytes(content_bytes)
    return content_hash, str(storage_subpath), len(content_bytes)


async def seed_landmark_papers_for_user(
    db: AsyncSession,
    user_id: UUID,
    blobs_dir: Path | None = None,
) -> int:
    """Seed the 12 landmark LLM papers and interconnected citation graph for a user."""
    if blobs_dir is None:
        root = Path(__file__).resolve().parent.parent.parent.parent.parent
        blobs_dir = root / "storage" / "blobs"
    blobs_dir.mkdir(parents=True, exist_ok=True)

    key_to_doc_id: dict[str, UUID] = {}
    key_to_doc: dict[str, DocumentModel] = {}
    key_to_gnode_id: dict[str, UUID] = {}

    # 1. Seed or retrieve each landmark paper
    for paper in LANDMARK_PAPERS:
        key = paper["id_key"]
        title = paper["title"]
        pdf_bytes = generate_minimal_pdf(title)

        chash, spath, fsize = _ensure_cas_blob(pdf_bytes, blobs_dir)

        # Blob record
        blob_stmt = select(DocumentStorageBlobModel).where(
            DocumentStorageBlobModel.content_hash == chash
        )
        blob_res = await db.execute(blob_stmt)
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
            db.add(blob)
            await db.flush()

        # Document record
        doc_stmt = select(DocumentModel).where(
            DocumentModel.user_id == user_id,
            DocumentModel.title == title,
        )
        doc_res = await db.execute(doc_stmt)
        doc = doc_res.scalars().first()

        if not doc:
            doc = DocumentModel(
                id=uuid4(),
                user_id=user_id,
                blob_id=blob.id,
                filename=paper["filename"],
                title=title,
                authors=paper["authors"],
                publication_year=paper["publication_year"],
                content_hash=chash,
                file_size_bytes=fsize,
                page_count=paper["page_count"],
                chunk_count=1,
                status="completed",
                stage="completed",
                progress=100,
                is_persistent=True,
            )
            db.add(doc)
            await db.flush()

            # Create primary abstract chunk for RAG/grounding
            chunk = DocumentChunkModel(
                id=uuid4(),
                user_id=user_id,
                document_id=doc.id,
                chunk_index=0,
                page_number=1,
                content=paper["abstract"],
                bounding_boxes=[[72.0, 712.0, 540.0, 760.0]],
                token_count=len(paper["abstract"].split()),
            )
            db.add(chunk)
            await db.flush()
        else:
            # Ensure it is marked persistent & completed
            doc.is_persistent = True
            doc.status = "completed"
            doc.stage = "completed"
            await db.flush()

        # Check or create GraphNodeModel for paper
        node_stmt = select(GraphNodeModel).where(
            GraphNodeModel.user_id == user_id,
            GraphNodeModel.node_type == "Paper",
            GraphNodeModel.canonical_name == title.lower(),
        )
        node_res = await db.execute(node_stmt)
        gnode = node_res.scalars().first()
        if not gnode:
            gnode = GraphNodeModel(
                id=uuid4(),
                user_id=user_id,
                document_id=doc.id,
                node_type="Paper",
                canonical_name=title.lower(),
                display_name=title,
                description=paper["abstract"],
                metadata_json={"year": paper["publication_year"]},
            )
            db.add(gnode)
            await db.flush()

        key_to_doc_id[key] = doc.id
        key_to_doc[key] = doc
        key_to_gnode_id[key] = gnode.id

    # 2. Seed cross-paper citations in reference_items and graph_edges
    for paper in LANDMARK_PAPERS:
        src_key = paper["id_key"]
        src_doc = key_to_doc[src_key]
        src_gnode_id = key_to_gnode_id[src_key]
        ref_idx = 0

        for target_key in paper["cites"]:
            target_doc = key_to_doc.get(target_key)
            target_gnode_id = key_to_gnode_id.get(target_key)
            if not target_doc or not target_gnode_id:
                continue

            ref_idx += 1
            # Check if reference item exists
            ref_stmt = select(ReferenceItemModel).where(
                ReferenceItemModel.document_id == src_doc.id,
                ReferenceItemModel.resolved_document_id == target_doc.id,
            )
            ref_res = await db.execute(ref_stmt)
            if not ref_res.scalars().first():
                ref_item = ReferenceItemModel(
                    id=uuid4(),
                    user_id=user_id,
                    document_id=src_doc.id,
                    ref_index=ref_idx,
                    raw_text=(
                        f"{target_doc.authors[0]} et al. "
                        f"({target_doc.publication_year}). {target_doc.title}."
                    ),
                    parsed_title=target_doc.title,
                    parsed_authors=target_doc.authors,
                    parsed_year=target_doc.publication_year,
                    resolved_document_id=target_doc.id,
                )
                db.add(ref_item)

            # Check graph edge
            edge_stmt = select(GraphEdgeModel).where(
                GraphEdgeModel.user_id == user_id,
                GraphEdgeModel.source_node_id == src_gnode_id,
                GraphEdgeModel.target_node_id == target_gnode_id,
            )
            edge_res = await db.execute(edge_stmt)
            if not edge_res.scalars().first():
                graph_edge = GraphEdgeModel(
                    id=uuid4(),
                    user_id=user_id,
                    document_id=src_doc.id,
                    source_node_id=src_gnode_id,
                    target_node_id=target_gnode_id,
                    edge_type="CITES",
                    weight=1.0,
                    metadata_json={"label": "cites"},
                )
                db.add(graph_edge)

    await db.commit()
    logger.info(
        "Successfully seeded landmark LLM papers",
        user_id=str(user_id),
        count=len(LANDMARK_PAPERS),
    )
    return len(LANDMARK_PAPERS)
