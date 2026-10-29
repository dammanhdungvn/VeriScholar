# Unified Advanced RAG & Graph Reasoning Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul VeriScholar's RAG into a unified, high-precision academic research assistant combining table-aware PDF parsing, hierarchical parent-child context expansion, cross-encoder semantic reranking, and a LangGraph corrective reasoning state machine (CRAG).

**Architecture:** PyMuPDF's table finder extracts pristine Markdown tables with exact bounding boxes. Document chunks are indexed with parent section headers. Retrieval runs in two stages: HNSW coarse vector recall (top-20) filtered by a Cross-Encoder Reranker (top-5). A LangGraph state machine evaluates relevance: if confident ($\ge 0.65$), it expands to parent context; if ambiguous, it expands along knowledge graph citation edges; if ungrounded ($< 0.25$), it triggers Active Abstention with Socratic guidance.

**Tech Stack:** Python 3.12, FastAPI, PyMuPDF 1.28 (`page.find_tables`), LangGraph 1.2, SQLAlchemy 2.0 Async, pgvector, Cross-Encoder / Cohere API Reranker adapter, pytest.

**Spec:** [`docs/superpowers/specs/2026-10-29-advanced-rag-reasoning-architecture-design.md`](../specs/2026-10-29-advanced-rag-reasoning-architecture-design.md)

---

## Global Constraints

- **Rule 1 (TDD Mandatory):** Every task must write failing tests first, verify failure, write minimal code to pass, verify green, and commit.
- **Rule 2 (Hexagonal Isolation):** Document parser adapter lives in `apps/api/src/api/adapters/`, RAG reasoning services live in `apps/api/src/api/services/`. Core domain entities remain pure in `packages/core/`.
- **Rule 4 (The 4 Verification Gates):** Before task completion, confirm exit code 0 for: Ruff check/format (Gate 1), Pytest (Gate 2), Vitest (Gate 3), Vite build (Gate 4).
- **Rule 6 (Radical Minimalism):** No raw technical scores, regex formulas, or internal IDs exposed to scholars.
- **Rule 9 (VPS Sync Protocol):** After commit, execute `bash scripts/deploy_to_vps.sh --fast`.

## Review Focus

1. **Table Bounding Box Exactness:** Tables extracted into Markdown must retain their spatial bounding box `[x0, y0, x1, y1, page]` so clicking citations highlights the real table on the PDF viewer.
   *Tested in Task 1, Step 1.*
2. **Double-Column Interleaved Sentence Prevention:** Multi-column text flow must not interleave left and right columns across tables.
   *Tested in Task 1, Step 1.*
3. **Cross-Encoder Score Normalization:** Reranker scores must normalize deterministically between 0.0 and 1.0 to ensure LangGraph branching thresholds ($\ge 0.65$, $< 0.25$) behave reliably across models.
   *Tested in Task 3, Step 1.*
4. **LangGraph State Loop Termination Guarantee:** The CRAG state machine must strictly terminate within 2 iterations (Retrieve $\rightarrow$ Evaluate $\rightarrow$ [Optional 1-hop Graph Expand] $\rightarrow$ Generate / Abstain) with zero infinite loops.
   *Tested in Task 4, Step 1.*
5. **Zero-Hallucination Active Abstention:** When evidence confidence is $< 0.25$, the system must return `abstain=True` with Socratic suggestions instead of inventing speculative answers.
   *Tested in Task 4, Step 1 and Task 5, Step 1.*

---

## Task Decomposition

### Task 1: Table & Structure-Preserving Document Layout Extractor

**Files:**
- Modify: `apps/api/src/api/adapters/chunk_extractor.py:80-220`
- Test: `apps/api/tests/test_table_structure_chunk_extractor.py`

**Interfaces:**
- Consumes: Raw PDF bytes.
- Produces: `PyMuPDFChunkExtractor.extract_chunks(pdf_bytes, document_id, chunk_size, chunk_overlap) -> list[DocumentChunk]` with tables formatted as Markdown tables (`| Col 1 | Col 2 |`) and their exact `bounding_boxes`.

- [ ] **Step 1: Write failing test in `apps/api/tests/test_table_structure_chunk_extractor.py`**

```python
import pymupdf
import pytest
from uuid import uuid4
from api.adapters.chunk_extractor import PyMuPDFChunkExtractor


@pytest.fixture
def sample_pdf_with_table_and_columns() -> bytes:
    """Generate in-memory PDF with a 2-column layout and a structured table."""
    doc = pymupdf.open()
    page = doc.new_page(width=600, height=800)
    
    # Left column text
    page.insert_text((50, 80), "Left column: The Transformer architecture relies on self-attention.", fontsize=11)
    # Right column text
    page.insert_text((320, 80), "Right column: Multi-head attention allows joint attending to information.", fontsize=11)
    
    # Draw table grid and insert cell text
    page.draw_rect(pymupdf.Rect(50, 200, 550, 300), color=(0, 0, 0), width=1)
    page.draw_line((50, 240), (550, 240), color=(0, 0, 0), width=1)
    page.draw_line((300, 200), (300, 300), color=(0, 0, 0), width=1)
    page.insert_text((60, 225), "Model Architecture", fontsize=10)
    page.insert_text((320, 225), "BLEU Score (EN-DE)", fontsize=10)
    page.insert_text((60, 275), "Transformer Base", fontsize=10)
    page.insert_text((320, 275), "27.3", fontsize=10)
    
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_extract_chunks_detects_tables_and_preserves_markdown_grid(sample_pdf_with_table_and_columns):
    extractor = PyMuPDFChunkExtractor()
    doc_id = uuid4()
    chunks = extractor.extract_chunks(sample_pdf_with_table_and_columns, doc_id)

    assert len(chunks) > 0
    # At least one chunk must contain the markdown table syntax
    table_chunks = [c for c in chunks if "|" in c.content and "BLEU Score" in c.content]
    assert len(table_chunks) >= 1, "Failed to extract table as markdown"
    
    tbl_chunk = table_chunks[0]
    assert "Model Architecture" in tbl_chunk.content
    assert "27.3" in tbl_chunk.content
    assert tbl_chunk.bounding_boxes is not None
    assert len(tbl_chunk.bounding_boxes) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_table_structure_chunk_extractor.py`
Expected: FAIL with `AssertionError: Failed to extract table as markdown`.

- [ ] **Step 3: Implement table extraction in `PyMuPDFChunkExtractor`**

In `apps/api/src/api/adapters/chunk_extractor.py`:
1. Use `page.find_tables()` to detect table structures, extract cell text, headers, and compute Markdown table format.
2. Replace raw table text blocks with the structured Markdown table and assign `table.bbox` normalized coordinates.
3. Keep non-table paragraphs in sorted reading order.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_table_structure_chunk_extractor.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/adapters/chunk_extractor.py apps/api/tests/test_table_structure_chunk_extractor.py
git commit -m "feat(api): add table extraction and markdown formatting to chunk extractor"
```

---

### Task 2: Hierarchical Parent-Child Indexer & Context Store

**Files:**
- Modify: `apps/api/src/api/db/models/chunk.py`
- Modify: `packages/core/src/core/domain/entities/chunk.py`
- Modify: `apps/api/src/api/adapters/chunk_extractor.py:220-300`
- Test: `apps/api/tests/test_hierarchical_chunk_storage.py`

**Interfaces:**
- Consumes: Document chunks from Task 1.
- Produces: `DocumentChunk` entity with `parent_section_heading: str | None` and `parent_section_content: str | None` for contextual expansion.

- [ ] **Step 1: Write failing test in `apps/api/tests/test_hierarchical_chunk_storage.py`**

```python
import pytest
from uuid import uuid4
from api.adapters.chunk_extractor import PyMuPDFChunkExtractor
from api.db.models.chunk import DocumentChunkModel


def test_chunk_entity_and_model_supports_parent_section_context():
    doc_id = uuid4()
    user_id = uuid4()

    model = DocumentChunkModel(
        user_id=user_id,
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="Sub-section: Self-attention computes key-value projections.",
        parent_section_heading="3.2 Attention Mechanism",
        parent_section_content="3.2 Attention Mechanism\nAn attention function can be described as mapping a query and a set of key-value pairs...",
        bounding_boxes=[[50.0, 100.0, 500.0, 200.0]],
        token_count=18,
    )

    assert model.parent_section_heading == "3.2 Attention Mechanism"
    assert "query and a set of key-value pairs" in model.parent_section_content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_hierarchical_chunk_storage.py`
Expected: FAIL with `TypeError: unexpected keyword argument 'parent_section_heading'`.

- [ ] **Step 3: Implement parent section fields in model and extractor**

1. In `packages/core/src/core/domain/entities/chunk.py`: add optional `parent_section_heading: str | None = None` and `parent_section_content: str | None = None`.
2. In `apps/api/src/api/db/models/chunk.py`: add `parent_section_heading: Mapped[str | None]` and `parent_section_content: Mapped[str | None]`.
3. In `chunk_extractor.py`: assemble chunks with section headers (e.g. `1. Introduction`, `3. Model Architecture`) so child chunks know their parent section context.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_hierarchical_chunk_storage.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/domain/entities/chunk.py apps/api/src/api/db/models/chunk.py apps/api/src/api/adapters/chunk_extractor.py apps/api/tests/test_hierarchical_chunk_storage.py
git commit -m "feat(api): add hierarchical parent-child context to chunk model"
```

---

### Task 3: Cross-Encoder Semantic Reranker Service

**Files:**
- Create: `apps/api/src/api/services/reranker_service.py`
- Test: `apps/api/tests/test_reranker_service.py`

**Interfaces:**
- Consumes: Query string `q` and list of candidate chunks `list[DocumentChunkModel]`.
- Produces: `RerankerService.rerank(query: str, candidates: list[Any], top_k: int = 5) -> list[tuple[Any, float]]` with normalized scores $[0.0, 1.0]$.

- [ ] **Step 1: Write failing test in `apps/api/tests/test_reranker_service.py`**

```python
import pytest
from api.services.reranker_service import RerankerService


@pytest.mark.asyncio
async def test_reranker_prioritizes_semantic_depth_over_keyword_stuffing():
    service = RerankerService()
    query = "What is the computational complexity per layer of self-attention?"
    
    # Chunk A: repetitive keywords but low informational density
    chunk_a = {"id": "c1", "content": "attention attention self-attention layer complexity per layer self-attention"}
    # Chunk B: substantive scientific explanation with exact formula
    chunk_b = {"id": "c2", "content": "Self-attention layer connects all positions with O(1) sequential operations and O(n^2 * d) complexity per layer."}
    # Chunk C: completely irrelevant
    chunk_c = {"id": "c3", "content": "We trained on standard 8 P100 GPUs for 3.5 days using Adam optimizer."}

    ranked = await service.rerank(query, [chunk_a, chunk_b, chunk_c], top_k=2)
    assert len(ranked) == 2
    # Chunk B must rank first despite Chunk A having more keyword repetitions
    top_chunk, score = ranked[0]
    assert top_chunk["id"] == "c2"
    assert 0.0 <= score <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_reranker_service.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.services.reranker_service'`.

- [ ] **Step 3: Implement `RerankerService` in `apps/api/src/api/services/reranker_service.py`**

Implement `RerankerService` supporting:
- Normalized Cross-Encoder scoring.
- Pluggable provider (Cohere Rerank API / SiliconFlow BGE API when API keys are configured, with deterministic cross-attention token-overlap fallback for local/offline testing).
- Score clipping and normalization to $[0.0, 1.0]$.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_reranker_service.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/reranker_service.py apps/api/tests/test_reranker_service.py
git commit -m "feat(api): implement cross-encoder semantic reranker service"
```

---

### Task 4: LangGraph Corrective Reasoning State Machine (CRAG Subgraph)

**Files:**
- Create: `apps/api/src/api/services/rag_reasoning_graph.py`
- Test: `apps/api/tests/test_rag_reasoning_graph.py`

**Interfaces:**
- Consumes: User query, target documents, DB session, `RerankerService`, and `GraphRAGService`.
- Produces: `RAGReasoningGraph.execute(query: str, target_doc_ids: list[UUID], scope: str) -> dict[str, Any]` returning `{"evidence_blocks": list, "citations": list, "abstain": bool}`.

- [ ] **Step 1: Write failing test in `apps/api/tests/test_rag_reasoning_graph.py`**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from api.services.rag_reasoning_graph import RAGReasoningGraph


@pytest.mark.asyncio
async def test_rag_reasoning_graph_evaluates_and_branches():
    mock_db = AsyncMock()
    mock_reranker = MagicMock()
    mock_graph_rag = MagicMock()

    # Case 1: High quality score >= 0.65 -> packs context without graph expansion
    mock_reranker.rerank = AsyncMock(return_value=[
        ({"id": "chk-1", "content": "Transformer base achieves 27.3 BLEU on EN-DE.", "page_number": 5, "bounding_boxes": [[0,0,1,1]]}, 0.88)
    ])

    graph = RAGReasoningGraph(db=mock_db, reranker=mock_reranker, graph_rag_service=mock_graph_rag)
    result = await graph.execute(
        query="What is the BLEU score of Transformer base?",
        target_doc_ids=[uuid4()],
        scope="single_paper"
    )

    assert result["abstain"] is False
    assert len(result["citations"]) == 1
    mock_graph_rag.query_graph.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_rag_reasoning_graph.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.services.rag_reasoning_graph'`.

- [ ] **Step 3: Implement `RAGReasoningGraph` using LangGraph `StateGraph`**

In `apps/api/src/api/services/rag_reasoning_graph.py`:
1. Define `RAGGraphState` typed dictionary (`query`, `candidates`, `graded_chunks`, `expanded_graph_chunks`, `citations`, `abstain`, `scope`).
2. Define nodes: `retrieve_coarse`, `rerank_and_grade`, `expand_graph_knowledge`, `pack_context`.
3. Conditional edge from `rerank_and_grade`:
   - If max score $\ge 0.65 \rightarrow$ `pack_context`.
   - If max score $< 0.65 \rightarrow$ `expand_graph_knowledge` (queries `GraphRAGService` along `CITES` edges).
4. From `expand_graph_knowledge`:
   - If still $< 0.25 \rightarrow$ mark `abstain=True`.
   - Else $\rightarrow$ `pack_context`.
5. Compile LangGraph workflow into an async runnable.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_rag_reasoning_graph.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/rag_reasoning_graph.py apps/api/tests/test_rag_reasoning_graph.py
git commit -m "feat(api): implement langgraph corrective reasoning state machine (crag)"
```

---

### Task 5: Integration into `SessionChatService` & Visual Citation Grounding

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:1920-2050`
- Test: `apps/api/tests/test_session_hybrid_rag_chat.py`

**Interfaces:**
- Consumes: `RAGReasoningGraph` from Task 4.
- Produces: `SessionChatService.retrieve_and_prepare_context` powered by the LangGraph engine with parent-child context and pixel-perfect citation bounding boxes.

- [ ] **Step 1: Write failing test in `apps/api/tests/test_session_hybrid_rag_chat.py`**

Assert that `retrieve_and_prepare_context` delegates to `RAGReasoningGraph` and returns parent section text in `evidence_blocks` while preserving individual child chunk bounding boxes in `citations`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_session_hybrid_rag_chat.py`
Expected: FAIL.

- [ ] **Step 3: Wire `RAGReasoningGraph` into `SessionChatService`**

In `apps/api/src/api/services/session_chat_service.py`:
1. In `__init__`, instantiate `RAGReasoningGraph(db=self.db)`.
2. In `retrieve_and_prepare_context`, call `await self.rag_graph.execute(question, target_doc_ids, scope)`.
3. Eliminate legacy regex keyword counting (`_score_and_rank_chunks`).
4. Ensure `citations` contain exact `bounding_boxes` for PDF Canvas viewer highlight.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_session_hybrid_rag_chat.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_session_hybrid_rag_chat.py
git commit -m "feat(api): wire langgraph crag engine into session chat service"
```

---

### Task 6: The 4 Verification Gates & Remote VPS Rollout

**Files:**
- Ledger: `docs/superpowers/plans/2026-10-29-advanced-rag-reasoning-pipeline.ledger.md`

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: 0 errors, 100% formatted.

- [ ] **Step 2: Gate 2 - Backend & Boundary Tests**

Run: `uv run pytest`
Expected: 100% passed (285+ tests).

- [ ] **Step 3: Gate 3 - Frontend Vitest Suite**

Run: `npm --prefix apps/web run test`
Expected: 100% passed (55+ test files, 224+ tests).

- [ ] **Step 4: Gate 4 - Frontend Production Build**

Run: `npm --prefix apps/web run build`
Expected: Exit code 0, cleanly bundled.

- [ ] **Step 5: Remote VPS Fast Rollout (Rule 9)**

Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Exit code 0, live health probe HTTP 200 OK at `https://verischolar.duckdns.org`.

- [ ] **Step 6: Commit ledger and complete plan**

```bash
git add docs/superpowers/plans/2026-10-29-advanced-rag-reasoning-pipeline.ledger.md
git commit -m "docs: complete ledger for advanced rag reasoning pipeline"
```
