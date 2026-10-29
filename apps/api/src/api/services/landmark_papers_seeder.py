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
from core.services.graph_extractor import normalize_canonical_name
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
        "methods": [
            {
                "name": "Transformer",
                "description": (
                    "Sequence transduction model architecture based entirely on self-attention "
                    "mechanisms, dispensing with recurrence and convolutions entirely."
                ),
            },
            {
                "name": "Scaled Dot-Product Attention",
                "description": (
                    "Attention mechanism computing dot products of queries and keys scaled by "
                    "the square root of the head dimension followed by softmax."
                ),
            },
            {
                "name": "Multi-Head Attention",
                "description": (
                    "Mechanism projecting queries, keys, and values into multiple representation "
                    "subspaces to attend jointly to information from different positions."
                ),
            },
        ],
        "datasets": [
            {
                "name": "WMT 2014 English-to-German",
                "description": (
                    "Standard machine translation benchmark dataset consisting of 4.5 million "
                    "sentence pairs."
                ),
            },
            {
                "name": "WMT 2014 English-to-French",
                "description": (
                    "Large-scale machine translation benchmark consisting of 36 million sentence "
                    "pairs."
                ),
            },
        ],
        "metrics": [
            {
                "name": "BLEU 28.4 (WMT 2014 En-De)",
                "method": "Transformer",
                "dataset": "WMT 2014 English-to-German",
                "metric_name": "BLEU",
                "value": 28.4,
                "unit": "BLEU",
            },
            {
                "name": "BLEU 41.8 (WMT 2014 En-Fr)",
                "method": "Transformer",
                "dataset": "WMT 2014 English-to-French",
                "metric_name": "BLEU",
                "value": 41.8,
                "unit": "BLEU",
            },
        ],
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
        "methods": [
            {
                "name": "BERT",
                "description": (
                    "Bidirectional Encoder Representations from Transformers pre-trained on "
                    "masked language modeling and next sentence prediction objectives."
                ),
            },
            {
                "name": "Masked Language Modeling",
                "description": (
                    "Pre-training objective masking random input tokens and predicting them "
                    "bidirectionally using deep Transformer encoder representations."
                ),
            },
        ],
        "datasets": [
            {
                "name": "GLUE",
                "description": (
                    "General Language Understanding Evaluation benchmark collection of nine "
                    "diverse natural language understanding tasks."
                ),
            },
            {
                "name": "SQuAD 1.1",
                "description": (
                    "Stanford Question Answering Dataset consisting of reading comprehension "
                    "questions posed over Wikipedia passages."
                ),
            },
        ],
        "metrics": [
            {
                "name": "GLUE Score 80.5",
                "method": "BERT",
                "dataset": "GLUE",
                "metric_name": "Average Score",
                "value": 80.5,
                "unit": "Score",
            },
            {
                "name": "SQuAD F1 93.2",
                "method": "BERT",
                "dataset": "SQuAD 1.1",
                "metric_name": "F1",
                "value": 93.2,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "GPT-3",
                "description": (
                    "Autoregressive foundation language model with 175 billion parameters "
                    "evaluated across zero-shot, one-shot, and few-shot settings."
                ),
            },
            {
                "name": "In-Context Learning",
                "description": (
                    "Prompt conditioning on task demonstrations during inference without "
                    "updating model gradient weights."
                ),
            },
        ],
        "datasets": [
            {
                "name": "SuperGLUE",
                "description": (
                    "Challenging benchmark suite designed to succeed GLUE with more rigorous "
                    "linguistic and reasoning tasks."
                ),
            },
            {
                "name": "LAMBADA",
                "description": (
                    "Broad-context word prediction benchmark evaluating long-range narrative "
                    "modeling and discourse understanding."
                ),
            },
        ],
        "metrics": [
            {
                "name": "LAMBADA Accuracy 76.2%",
                "method": "GPT-3",
                "dataset": "LAMBADA",
                "metric_name": "Accuracy",
                "value": 76.2,
                "unit": "%",
            },
            {
                "name": "SuperGLUE Few-Shot 71.8",
                "method": "GPT-3",
                "dataset": "SuperGLUE",
                "metric_name": "Score",
                "value": 71.8,
                "unit": "Score",
            },
        ],
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
        "methods": [
            {
                "name": "LoRA",
                "description": (
                    "Parameter-efficient fine-tuning freezing pre-trained model weights and "
                    "injecting trainable rank decomposition matrices into Transformer layers."
                ),
            },
        ],
        "datasets": [
            {
                "name": "GLUE",
                "description": (
                    "General Language Understanding Evaluation benchmark collection of nine "
                    "diverse natural language understanding tasks."
                ),
            },
        ],
        "metrics": [
            {
                "name": "GLUE LoRA Average 88.5%",
                "method": "LoRA",
                "dataset": "GLUE",
                "metric_name": "Accuracy",
                "value": 88.5,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "Chain-of-Thought Prompting",
                "description": (
                    "Prompting strategy prompting language models to generate step-by-step "
                    "intermediate reasoning chains prior to answering complex questions."
                ),
            },
        ],
        "datasets": [
            {
                "name": "GSM8K",
                "description": (
                    "Grade school math benchmark consisting of 8,500 diverse multi-step "
                    "mathematical word reasoning problems."
                ),
            },
        ],
        "metrics": [
            {
                "name": "GSM8K Accuracy 60.1%",
                "method": "Chain-of-Thought Prompting",
                "dataset": "GSM8K",
                "metric_name": "Accuracy",
                "value": 60.1,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "ReAct",
                "description": (
                    "Paradigm synergizing reasoning traces and task-specific external actions "
                    "in an interleaved loop for interactive decision making."
                ),
            },
        ],
        "datasets": [
            {
                "name": "HotpotQA",
                "description": (
                    "Multi-hop question answering benchmark requiring reasoning over multiple "
                    "supporting Wikipedia articles."
                ),
            },
        ],
        "metrics": [
            {
                "name": "HotpotQA Success Rate 34.0%",
                "method": "ReAct",
                "dataset": "HotpotQA",
                "metric_name": "Success Rate",
                "value": 34.0,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "RAG",
                "description": (
                    "General-purpose fine-tuning recipe combining pre-trained parametric "
                    "generator with non-parametric dense vector retriever."
                ),
            },
            {
                "name": "DPR Dense Retrieval",
                "description": (
                    "Dense passage retrieval architecture encoding passages and questions into "
                    "dense vector embeddings for semantic similarity lookup."
                ),
            },
        ],
        "datasets": [
            {
                "name": "Natural Questions",
                "description": (
                    "Benchmark based on real Google search queries paired with human-annotated "
                    "Wikipedia answer paragraphs."
                ),
            },
        ],
        "metrics": [
            {
                "name": "Natural Questions Exact Match 44.5%",
                "method": "RAG",
                "dataset": "Natural Questions",
                "metric_name": "Exact Match",
                "value": 44.5,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "Graph RAG",
                "description": (
                    "Holistic framework combining knowledge graph generation, community "
                    "detection, and hierarchic summarization for global sensemaking queries."
                ),
            },
            {
                "name": "Hierarchical Community Summarization",
                "description": (
                    "Summarizing clustered graph communities at varying modularity levels to "
                    "support global query-focused corpus summarization."
                ),
            },
        ],
        "datasets": [
            {
                "name": "MultiHop-RAG Benchmark",
                "description": (
                    "Multi-hop question answering and synthesis benchmark across extensive "
                    "unstructured document corpora."
                ),
            },
        ],
        "metrics": [
            {
                "name": "Comprehensiveness Win Rate 72.0%",
                "method": "Graph RAG",
                "dataset": "MultiHop-RAG Benchmark",
                "metric_name": "Win Rate",
                "value": 72.0,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "Toolformer",
                "description": (
                    "Self-supervised model learning to decide which external tools to call, "
                    "when to call them, and how to incorporate tool execution outputs."
                ),
            },
        ],
        "datasets": [
            {
                "name": "GSM8K",
                "description": (
                    "Grade school math benchmark consisting of 8,500 diverse multi-step "
                    "mathematical word reasoning problems."
                ),
            },
        ],
        "metrics": [
            {
                "name": "GSM8K Toolformer Accuracy 54.7%",
                "method": "Toolformer",
                "dataset": "GSM8K",
                "metric_name": "Accuracy",
                "value": 54.7,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "LLaMA",
                "description": (
                    "Collection of open foundation language models from 7B to 65B parameters "
                    "trained exclusively on publicly available data tokens."
                ),
            },
        ],
        "datasets": [
            {
                "name": "MMLU",
                "description": (
                    "Massive Multitask Language Understanding benchmark covering 57 subjects "
                    "across STEM, humanities, and social sciences."
                ),
            },
        ],
        "metrics": [
            {
                "name": "MMLU 65B Accuracy 63.4%",
                "method": "LLaMA",
                "dataset": "MMLU",
                "metric_name": "Accuracy",
                "value": 63.4,
                "unit": "%",
            },
        ],
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
        "methods": [
            {
                "name": "RAGAS",
                "description": (
                    "Reference-free automated evaluation framework assessing RAG pipelines along "
                    "faithfulness, answer relevance, context precision, and recall."
                ),
            },
        ],
        "datasets": [
            {
                "name": "WikiEval",
                "description": (
                    "Evaluation dataset for RAG pipelines comprising question-context-answer "
                    "triplets annotated for factual consistency."
                ),
            },
        ],
        "metrics": [
            {
                "name": "Faithfulness Harmonic Mean 0.88",
                "method": "RAGAS",
                "dataset": "WikiEval",
                "metric_name": "F1 Score",
                "value": 0.88,
                "unit": "F1",
            },
        ],
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
        "methods": [
            {
                "name": "Direct Preference Optimization",
                "description": (
                    "Direct policy optimization algorithm implicitly satisfying Bradley-Terry "
                    "preference models via binary cross-entropy loss without reward modeling."
                ),
            },
        ],
        "datasets": [
            {
                "name": "Anthropic HH-RLHF",
                "description": (
                    "Helpful and Harmless human preference conversation dataset evaluating "
                    "AI safety and alignment."
                ),
            },
        ],
        "metrics": [
            {
                "name": "HH-RLHF Win Rate 61.2%",
                "method": "Direct Preference Optimization",
                "dataset": "Anthropic HH-RLHF",
                "metric_name": "Win Rate",
                "value": 61.2,
                "unit": "%",
            },
        ],
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


async def _get_or_create_node(
    db: AsyncSession,
    user_id: UUID,
    doc_id: UUID | None,
    node_type: str,
    name: str,
    description: str | None = None,
    metadata_json: dict[str, Any] | None = None,
    cache: dict[tuple[str, str], UUID] | None = None,
) -> UUID:
    """Retrieve existing canonical node or create a new node.

    Maintains user-type deduplication based on uq_graph_nodes_user_type_canonical.
    """
    canonical_name = normalize_canonical_name(name)
    cache_key = (node_type, canonical_name)
    if cache is not None and cache_key in cache:
        return cache[cache_key]

    stmt = select(GraphNodeModel).where(
        GraphNodeModel.user_id == user_id,
        GraphNodeModel.node_type == node_type,
        GraphNodeModel.canonical_name == canonical_name,
    )
    res = await db.execute(stmt)
    node = res.scalars().first()
    if not node:
        node = GraphNodeModel(
            id=uuid4(),
            user_id=user_id,
            document_id=doc_id,
            node_type=node_type,
            canonical_name=canonical_name,
            display_name=name,
            description=description,
            metadata_json=metadata_json or {},
        )
        db.add(node)
        await db.flush()

    if cache is not None:
        cache[cache_key] = node.id
    return node.id


async def _ensure_edge(
    db: AsyncSession,
    user_id: UUID,
    doc_id: UUID | None,
    source_id: UUID,
    target_id: UUID,
    edge_type: str,
    metadata_json: dict[str, Any] | None = None,
) -> None:
    """Ensure a typed directed edge exists between source and target nodes."""
    edge_stmt = select(GraphEdgeModel).where(
        GraphEdgeModel.user_id == user_id,
        GraphEdgeModel.source_node_id == source_id,
        GraphEdgeModel.target_node_id == target_id,
        GraphEdgeModel.edge_type == edge_type,
    )
    res = await db.execute(edge_stmt)
    if not res.scalars().first():
        edge = GraphEdgeModel(
            id=uuid4(),
            user_id=user_id,
            document_id=doc_id,
            source_node_id=source_id,
            target_node_id=target_id,
            edge_type=edge_type,
            weight=1.0,
            metadata_json=metadata_json or {"label": edge_type.lower()},
        )
        db.add(edge)
        await db.flush()


async def seed_landmark_papers_for_user(
    db: AsyncSession,
    user_id: UUID,
    blobs_dir: Path | None = None,
) -> int:
    """Seed the 12 landmark LLM papers and interconnected 4-entity knowledge graph for a user."""
    if blobs_dir is None:
        root = Path(__file__).resolve().parent.parent.parent.parent.parent
        blobs_dir = root / "storage" / "blobs"
    blobs_dir.mkdir(parents=True, exist_ok=True)

    key_to_doc_id: dict[str, UUID] = {}
    key_to_doc: dict[str, DocumentModel] = {}
    key_to_gnode_id: dict[str, UUID] = {}
    node_cache: dict[tuple[str, str], UUID] = {}

    # 1. Seed or retrieve each landmark paper and its ontology
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

        # Check or create GraphNodeModel for Paper
        paper_gnode_id = await _get_or_create_node(
            db=db,
            user_id=user_id,
            doc_id=doc.id,
            node_type="Paper",
            name=title,
            description=paper["abstract"],
            metadata_json={"year": paper["publication_year"]},
            cache=node_cache,
        )

        key_to_doc_id[key] = doc.id
        key_to_doc[key] = doc
        key_to_gnode_id[key] = paper_gnode_id

        # Seed Method entities and PROPOSES edges
        method_name_to_id: dict[str, UUID] = {}
        for method_info in paper.get("methods", []):
            method_id = await _get_or_create_node(
                db=db,
                user_id=user_id,
                doc_id=doc.id,
                node_type="Method",
                name=method_info["name"],
                description=method_info.get("description"),
                metadata_json={"proposed_by": title},
                cache=node_cache,
            )
            method_name_to_id[method_info["name"]] = method_id
            method_name_to_id[normalize_canonical_name(method_info["name"])] = method_id

            await _ensure_edge(
                db=db,
                user_id=user_id,
                doc_id=doc.id,
                source_id=paper_gnode_id,
                target_id=method_id,
                edge_type="PROPOSES",
                metadata_json={"label": "proposes"},
            )

        primary_method_id = list(method_name_to_id.values())[0] if method_name_to_id else None

        # Seed Dataset entities and EVALUATED_ON edges
        for dataset_info in paper.get("datasets", []):
            dataset_id = await _get_or_create_node(
                db=db,
                user_id=user_id,
                doc_id=doc.id,
                node_type="Dataset",
                name=dataset_info["name"],
                description=dataset_info.get("description"),
                metadata_json={"introduced_in": title},
                cache=node_cache,
            )

            # Connect Method -> Dataset
            if primary_method_id:
                await _ensure_edge(
                    db=db,
                    user_id=user_id,
                    doc_id=doc.id,
                    source_id=primary_method_id,
                    target_id=dataset_id,
                    edge_type="EVALUATED_ON",
                    metadata_json={"label": "evaluated_on"},
                )

            # Also connect Paper -> Dataset
            await _ensure_edge(
                db=db,
                user_id=user_id,
                doc_id=doc.id,
                source_id=paper_gnode_id,
                target_id=dataset_id,
                edge_type="EVALUATED_ON",
                metadata_json={"label": "evaluated_on"},
            )

        # Seed MetricResult entities and ACHIEVES edges
        for metric_info in paper.get("metrics", []):
            metric_meta = {
                "metric_name": metric_info.get("metric_name"),
                "value": metric_info.get("value"),
                "unit": metric_info.get("unit"),
                "dataset": metric_info.get("dataset"),
            }
            metric_id = await _get_or_create_node(
                db=db,
                user_id=user_id,
                doc_id=doc.id,
                node_type="MetricResult",
                name=metric_info["name"],
                description=metric_info.get(
                    "description", f"{metric_info['name']} benchmark result"
                ),
                metadata_json=metric_meta,
                cache=node_cache,
            )

            target_method = metric_info.get("method")
            method_source_id = (
                method_name_to_id.get(target_method or "")
                or method_name_to_id.get(normalize_canonical_name(target_method or ""))
                or primary_method_id
                or paper_gnode_id
            )

            await _ensure_edge(
                db=db,
                user_id=user_id,
                doc_id=doc.id,
                source_id=method_source_id,
                target_id=metric_id,
                edge_type="ACHIEVES",
                metadata_json={
                    "label": "achieves",
                    "value": metric_info.get("value"),
                    "unit": metric_info.get("unit"),
                },
            )

    # 2. Seed cross-paper citations in reference_items and graph_edges (CITES)
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
            await _ensure_edge(
                db=db,
                user_id=user_id,
                doc_id=src_doc.id,
                source_id=src_gnode_id,
                target_id=target_gnode_id,
                edge_type="CITES",
                metadata_json={"label": "cites"},
            )

    await db.commit()
    logger.info(
        "Successfully seeded landmark LLM papers and 4-entity graph",
        user_id=str(user_id),
        count=len(LANDMARK_PAPERS),
    )
    return len(LANDMARK_PAPERS)
