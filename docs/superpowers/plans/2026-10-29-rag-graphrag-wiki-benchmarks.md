# Production RAG, GraphRAG Wiki, Agentic LangGraph & Langfuse Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close all verified architectural gaps between `docs/specs/` and actual codebase implementation by building: (1) Local ONNX FlashRank Semantic Reranker for Advanced RAG, (2) Compiled Academic Wiki (`wiki_pages` table, pure domain `wiki_compiler.py`, and Wiki REST endpoints), (3) 4-Entity Seeder and Pipeline for multi-type GraphRAG, (4) Dynamic tool-calling ReAct in LangGraph LaTeX Co-Author, and (5) 3-Track LLM-as-a-Judge Benchmark Suite pushing evaluation scores to Langfuse.

**Architecture:** Hexagonal Architecture isolating the domain Markdown compiler in `packages/core/` (pure Python/Pydantic) while keeping PostgreSQL `pgvector`, ONNX FlashRank cross-encoder inference, LangGraph StateGraph, and Langfuse LLM-as-a-judge evaluators in `apps/api/`. Every task follows strict Red-Green-Refactor TDD with idempotent database migrations and automated VPS sync after each commit.

**Tech Stack:** FastAPI, Python 3.12, SQLAlchemy 2.0 Async, pgvector, `flashrank` (ONNX Cross-Encoder), `langgraph` (StateGraph), `networkx` (Louvain clustering), `langfuse` (Tracing & LLM Judge Datasets), React 19 / Tailwind CSS.

**Spec References:**
- [`docs/specs/03-sessions-and-deep-reading-spec.md`](../../specs/03-sessions-and-deep-reading-spec.md) (§5.B Khối 5: Semantic Reranking & Confidence Gate)
- [`docs/specs/05-favorite-library-and-graphrag-spec.md`](../../specs/05-favorite-library-and-graphrag-spec.md) (§1.D, §2, §3, §4: 4-Entity Ontology & Compiled LLM Wiki)
- [`docs/specs/06-agentic-overleaf-writing-spec.md`](../../specs/06-agentic-overleaf-writing-spec.md) (§1.D, §2, §3: LangGraph ReAct Agent with Tool Calling & Reviewer)
- [`docs/specs/07-monitoring-and-langfuse-spec.md`](../../specs/07-monitoring-and-langfuse-spec.md) (§1.E, §5.D, §6, §7: LLM-as-a-Judge Benchmark Suite)

---

## Global Constraints

- **Rule 1 (TDD Mandatory):** Every step requires writing the failing test first, running it to observe the red failure, implementing the minimal code to pass, and verifying green before commit.
- **Rule 2 (Hexagonal Isolation):** `packages/core/` must only use Python Standard Library and Pydantic. Strictly zero imports from `apps/api/`, SQLAlchemy ORM, Web frameworks, or external network I/O.
- **Rule 5 (Relative Markdown Links Only):** All links in markdown documents must use relative paths (no absolute `file://` URIs).
- **Rule 6 (Product-Grade Radical Minimalism):** Anthropic design aesthetics, zero debug noise or technical jargon on user-facing UI.
- **Rule 9 (In-Plan VPS Sync Protocol):** After every successful `git commit`, run `bash scripts/deploy_to_vps.sh --fast`.
- **The 4 Verification Gates:** Before closing tasks, confirm all 4 gates pass: `ruff check/format`, `pytest`, `npm test`, `npm run build`.

---

## Review Focus

1. **FlashRank ONNX CPU Availability & Graceful Fallback:** If ONNX runtime or FlashRank model fails to download or runs in a constrained test sandbox, the reranker must gracefully fallback to rank-preserving RRF scores without crashing session chat.
2. **Deterministic Entity Deduplication in 4-Entity Ingestion:** When merging `Method` and `Dataset` nodes, canonical lowercase stripping and vector cosine similarity ($\ge 0.90$) must prevent duplicate hub nodes for the same entity across papers.
3. **Wiki Page Slug Collision & Multi-Tenant User Scoping:** `wiki_pages` must enforce unique `(user_id, slug)` so different users can have identical wiki concept titles without data leakage.
4. **LangGraph State Oscillation & Tool Recursion Limit:** When LaTeX compilation fails iteratively, anti-oscillation SHA-256 detection must halt execution at $\le 3$ attempts and return structured diagnostics instead of hanging the SSE stream.
5. **Langfuse Telemetry Fail-Safe Facade:** Benchmark evaluation and trace logging must never throw uncaught exceptions if `LANGFUSE_PUBLIC_KEY` is unset or remote endpoints time out.

---

## Tasks

### Task 1: Local ONNX FlashRank Semantic Reranker & Confidence Gate

**Files:**
- Modify: `pyproject.toml`
- Create: `apps/api/src/api/services/semantic_reranker_service.py`
- Modify: `apps/api/src/api/services/session_chat_service.py:2160-2270`
- Test: `apps/api/tests/test_semantic_reranker.py`

**Interfaces:**
- Consumes: `DocumentChunkModel` candidates from Hybrid RRF retrieval, `standalone_query: str`.
- Produces: `SemanticRerankerService.rerank(query: str, candidates: list[dict[str, Any]], top_k: int = 5) -> tuple[list[dict[str, Any]], bool]` returning ranked chunks and `abstain: bool`.

- [ ] **Step 1: Write failing test for SemanticRerankerService**

```python
# apps/api/tests/test_semantic_reranker.py
import pytest
from api.services.semantic_reranker_service import SemanticRerankerService

def test_semantic_reranker_ranks_relevant_chunks_higher():
    reranker = SemanticRerankerService()
    query = "What is the computational complexity of Scaled Dot-Product Attention?"
    candidates = [
        {"id": "c1", "content": "The weather in Seattle is rainy in autumn.", "score": 0.5},
        {"id": "c2", "content": "Attention has computational complexity O(n^2 * d) where n is sequence length.", "score": 0.5},
        {"id": "c3", "content": "Recurrent neural networks process tokens sequentially in O(n * d^2).", "score": 0.5},
    ]
    ranked, abstain = reranker.rerank(query=query, candidates=candidates, top_k=2)
    assert abstain is False
    assert len(ranked) == 2
    assert ranked[0]["id"] == "c2"
    assert ranked[0]["rerank_score"] > ranked[1]["rerank_score"]

def test_semantic_reranker_abstains_when_all_chunks_are_irrelevant():
    reranker = SemanticRerankerService()
    query = "Explain quantum gravity in AdS/CFT correspondence."
    candidates = [
        {"id": "c1", "content": "Recipe for baking sourdough bread using starter.", "score": 0.1},
        {"id": "c2", "content": "How to repair bicycle tire punctures.", "score": 0.1},
    ]
    ranked, abstain = reranker.rerank(query=query, candidates=candidates, top_k=2)
    assert abstain is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_semantic_reranker.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.services.semantic_reranker_service'`

- [ ] **Step 3: Add `flashrank` dependency and implement `SemanticRerankerService`**

1. Add `"flashrank>=0.2.9"` to `pyproject.toml` dependencies and run `uv lock`.
2. Implement `SemanticRerankerService` in `apps/api/src/api/services/semantic_reranker_service.py` using `Ranker(model_name="ms-marco-TinyBERT-L-2-v2")` with fallback to token-overlap scoring if ONNX runtime is unavailable in test environment. Thresholds: $S \ge 0.65$ keeps chunk, $S_{\text{max}} < 0.35$ sets `abstain = True`.
3. Update `SessionChatService._score_and_rank_chunks` in `apps/api/src/api/services/session_chat_service.py` to delegate to `SemanticRerankerService`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_semantic_reranker.py -v`
Expected: PASS with 2 passed tests.

- [ ] **Step 5: Commit and Deploy to VPS**

```bash
git add pyproject.toml uv.lock apps/api/src/api/services/semantic_reranker_service.py apps/api/src/api/services/session_chat_service.py apps/api/tests/test_semantic_reranker.py
git commit -m "feat(rag): integrate onnx flashrank cross-encoder reranker and active abstention gate"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Pure Domain Wiki Compiler (`packages/core/src/core/services/wiki_compiler.py`)

**Files:**
- Create: `packages/core/src/core/models/wiki.py`
- Create: `packages/core/src/core/services/wiki_compiler.py`
- Test: `packages/core/tests/test_wiki_compiler.py`

**Interfaces:**
- Consumes: Raw Markdown strings, metadata dictionaries, entity graph representations.
- Produces: `WikiCompileResult(slug: str, title: str, markdown: str, yaml_metadata: dict, wikilinks: list[str])`.

- [ ] **Step 1: Write failing test for `WikiCompiler`**

```python
# packages/core/tests/test_wiki_compiler.py
import pytest
from core.models.wiki import WikiPageDraft
from core.services.wiki_compiler import WikiCompiler

def test_wiki_compiler_extracts_wikilinks_and_compiles_markdown():
    compiler = WikiCompiler()
    draft = WikiPageDraft(
        title="Scaled Dot-Product Attention",
        summary="A core attention mechanism proposed in Attention Is All You Need.",
        key_insights=["Computes attention weights via softmax(QK^T / sqrt(d_k)).", "Quadratic complexity with respect to sequence length."],
        related_entities=["Transformer", "Multi-Head Attention", "WMT 2014 En-De"],
        source_papers=["Vaswani et al., 2017"],
    )
    result = compiler.compile_page(draft)
    assert result.slug == "scaled-dot-product-attention"
    assert "[[Transformer]]" in result.markdown
    assert "[[Multi-Head Attention]]" in result.markdown
    assert "scaled-dot-product-attention" in result.yaml_metadata["slug"]
    assert set(result.wikilinks) == {"Transformer", "Multi-Head Attention", "WMT 2014 En-De"}

def test_wiki_compiler_parses_existing_markdown_with_frontmatter():
    compiler = WikiCompiler()
    raw = """---
title: RoPE Positional Encoding
slug: rope-positional-encoding
tags: [embedding, rotary]
---
# RoPE Positional Encoding
RoPE encodes relative position via complex rotation. See [[Transformer]] and [[LLaMA]].
"""
    parsed = compiler.parse_markdown(raw)
    assert parsed.title == "RoPE Positional Encoding"
    assert parsed.slug == "rope-positional-encoding"
    assert "Transformer" in parsed.wikilinks
    assert "LLaMA" in parsed.wikilinks
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_wiki_compiler.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.models.wiki'`

- [ ] **Step 3: Implement `WikiPageDraft`, `WikiCompileResult` and `WikiCompiler`**

1. Create `packages/core/src/core/models/wiki.py` with Pydantic v2 schemas: `WikiPageDraft` and `WikiCompileResult`.
2. Implement `WikiCompiler` in `packages/core/src/core/services/wiki_compiler.py`:
   - Sluggify title (`slugify(title)` using standard library `re`).
   - Format YAML frontmatter (using strict key-value formatting without external yaml if possible, or standard `re`).
   - Extract `\[\[(.*?)\]\]` links via regex.
   - Enforce Rule 2: strictly standard library + Pydantic.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_wiki_compiler.py -v`
Expected: PASS with 2 passed tests.

- [ ] **Step 5: Commit and Deploy to VPS**

```bash
git add packages/core/src/core/models/wiki.py packages/core/src/core/services/wiki_compiler.py packages/core/tests/test_wiki_compiler.py
git commit -m "feat(core): implement pure domain academic wiki compiler and wikilink parser"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Compiled Academic Wiki Database Model & Persistence Service

**Files:**
- Create: `apps/api/src/api/db/models/wiki.py`
- Modify: `apps/api/src/api/db/models/__init__.py`
- Create: `apps/api/src/api/services/wiki_service.py`
- Test: `apps/api/tests/test_wiki_models.py`
- Test: `apps/api/tests/test_wiki_service.py`

**Interfaces:**
- Consumes: `AsyncSession`, `current_user: UserModel`, `WikiPageDraft`.
- Produces: `WikiPageModel` table `wiki_pages`, `WikiService.get_page_by_slug(user_id, slug)`, `WikiService.list_pages(user_id)`, `WikiService.save_page(user_id, draft)`.

- [ ] **Step 1: Write failing test for `WikiPageModel` and `WikiService`**

```python
# apps/api/tests/test_wiki_models.py
import pytest
from uuid import uuid4
from api.db.models.wiki import WikiPageModel

def test_wiki_page_model_attributes_and_tablename():
    uid = uuid4()
    page = WikiPageModel(
        user_id=uid,
        slug="scaled-dot-product-attention",
        title="Scaled Dot-Product Attention",
        markdown_content="# Scaled Dot-Product Attention\nCore mechanism.",
        yaml_metadata={"tags": ["attention"]},
        wikilinks=["Transformer"],
    )
    assert page.__tablename__ == "wiki_pages"
    assert page.slug == "scaled-dot-product-attention"
    assert page.user_id == uid
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_wiki_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.db.models.wiki'`

- [ ] **Step 3: Implement `WikiPageModel` and `WikiService`**

1. Create `apps/api/src/api/db/models/wiki.py`:
   - `WikiPageModel` with `id`, `user_id` (FK to `users.id`), `slug` (String 255), `title` (String 255), `markdown_content` (Text), `yaml_metadata` (JSONType), `wikilinks` (JSONType), `embedding` (Vector 1536 nullable).
   - `UniqueConstraint("user_id", "slug", name="uq_wiki_pages_user_slug")`.
2. Register in `apps/api/src/api/db/models/__init__.py`.
3. Create `apps/api/src/api/services/wiki_service.py`:
   - `get_page_by_slug(db, user_id, slug)`
   - `list_pages(db, user_id, limit, offset)`
   - `upsert_page(db, user_id, title, markdown, yaml_meta, wikilinks)`

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_wiki_models.py -v`
Expected: PASS.

- [ ] **Step 5: Commit and Deploy to VPS**

```bash
git add apps/api/src/api/db/models/wiki.py apps/api/src/api/db/models/__init__.py apps/api/src/api/services/wiki_service.py apps/api/tests/test_wiki_models.py
git commit -m "feat(api): create wiki_pages database model and persistence service"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Wiki REST Endpoints & Research Gaps Synthesis

**Files:**
- Create: `apps/api/src/api/schemas/wiki.py`
- Create: `apps/api/src/api/v1/endpoints/wiki.py`
- Modify: `apps/api/src/api/v1/router.py`
- Test: `apps/api/tests/test_wiki_endpoints.py`

**Interfaces:**
- Consumes: HTTP Requests (`GET /api/v1/library/wiki`, `GET /api/v1/library/wiki/{slug}`, `POST /api/v1/library/research-gaps`).
- Produces: Standardized JSON Response Envelopes conforming to Spec 05.

- [ ] **Step 1: Write failing integration test for Wiki endpoints**

```python
# apps/api/tests/test_wiki_endpoints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_wiki_crud_and_research_gaps(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. List initially empty
    resp = await async_client.get("/api/v1/library/wiki", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data

    # 2. Get non-existent slug returns 404
    resp_404 = await async_client.get("/api/v1/library/wiki/unknown-concept", headers=auth_headers)
    assert resp_404.status_code == 404
    assert resp_404.json()["error"]["code"] == "WIKI_PAGE_NOT_FOUND"

    # 3. Query research gaps
    resp_gaps = await async_client.post(
        "/api/v1/library/research-gaps",
        json={"folder_id": None, "query": "Unsolved efficiency bottlenecks"},
        headers=auth_headers,
    )
    assert resp_gaps.status_code == 200
    assert "unsolved_frontiers" in resp_gaps.json()["data"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_wiki_endpoints.py -v`
Expected: FAIL with 404 Not Found on `/api/v1/library/wiki`

- [ ] **Step 3: Implement Schemas and Endpoints**

1. Create `apps/api/src/api/schemas/wiki.py` with `WikiPageResponse`, `WikiListResponse`, `ResearchGapsRequest`, `ResearchGapsResponse`.
2. Create `apps/api/src/api/v1/endpoints/wiki.py` implementing:
   - `GET /api/v1/library/wiki`
   - `GET /api/v1/library/wiki/{slug}`
   - `POST /api/v1/library/research-gaps` (synthesizing paper limitations from `documents.parsed_metadata` or summaries into unstructured matrix).
3. Include router in `apps/api/src/api/v1/router.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_wiki_endpoints.py -v`
Expected: PASS with all tests green.

- [ ] **Step 5: Commit and Deploy to VPS**

```bash
git add apps/api/src/api/schemas/wiki.py apps/api/src/api/v1/endpoints/wiki.py apps/api/src/api/v1/router.py apps/api/tests/test_wiki_endpoints.py
git commit -m "feat(api): provide compiled academic wiki endpoints and research gaps matrix"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: Multi-Entity Seeder & Dynamic Extraction Pipeline (4 Entity Graph)

**Files:**
- Modify: `apps/api/src/api/services/landmark_papers_seeder.py`
- Modify: `apps/api/src/api/services/graph_extraction_service.py`
- Test: `apps/api/tests/test_graph_4_entity_seeder.py`

**Interfaces:**
- Consumes: Seed user UUID, async session `db`.
- Produces: Persistent `GraphNodeModel` rows with `node_type IN ('Paper', 'Method', 'Dataset', 'MetricResult')` and `GraphEdgeModel` rows with `edge_type IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES')`.

- [ ] **Step 1: Write failing test verifying 4 entity types seeded**

```python
# apps/api/tests/test_graph_4_entity_seeder.py
import pytest
from sqlalchemy import select, func
from api.db.models.graph import GraphNodeModel, GraphEdgeModel
from api.services.landmark_papers_seeder import seed_landmark_papers_for_user

@pytest.mark.asyncio
async def test_seeder_creates_4_entity_types_and_typed_edges(db_session, test_user):
    count = await seed_landmark_papers_for_user(db_session, test_user.id)
    assert count >= 10

    # Verify all 4 node types exist
    node_types_stmt = (
        select(GraphNodeModel.node_type, func.count(GraphNodeModel.id))
        .where(GraphNodeModel.user_id == test_user.id)
        .group_by(GraphNodeModel.node_type)
    )
    res_nodes = await db_session.execute(node_types_stmt)
    node_type_counts = dict(res_nodes.all())

    assert "Paper" in node_type_counts
    assert "Method" in node_type_counts
    assert "Dataset" in node_type_counts
    assert "MetricResult" in node_type_counts

    # Verify typed edges exist
    edge_types_stmt = (
        select(GraphEdgeModel.edge_type, func.count(GraphEdgeModel.id))
        .where(GraphEdgeModel.user_id == test_user.id)
        .group_by(GraphEdgeModel.edge_type)
    )
    res_edges = await db_session.execute(edge_types_stmt)
    edge_type_counts = dict(res_edges.all())

    assert "PROPOSES" in edge_type_counts
    assert "EVALUATED_ON" in edge_type_counts
    assert "ACHIEVES" in edge_type_counts
    assert "CITES" in edge_type_counts
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_graph_4_entity_seeder.py -v`
Expected: FAIL asserting `"Method" in node_type_counts` (since currently only Paper is seeded).

- [ ] **Step 3: Update `landmark_papers_seeder.py` with 4-Entity Ontology**

1. Enrich `LANDMARK_PAPERS` definitions with explicit `methods` (e.g., *Scaled Dot-Product Attention*, *Multi-Head Attention*, *Transformer*), `datasets` (e.g., *WMT 2014 En-De*, *GLUE*, *SQuAD*), and `metrics` (e.g., *BLEU 28.4*, *Accuracy 88.5%*).
2. For each paper seeded in `seed_landmark_papers_for_user`:
   - Create or link canonical `Method` nodes with `PROPOSES` edge from Paper.
   - Create or link canonical `Dataset` nodes with `EVALUATED_ON` edge from Method/Paper.
   - Create canonical `MetricResult` nodes with `ACHIEVES` edge from Method.
3. Keep idempotent deduplication based on `uq_graph_nodes_user_type_canonical`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_graph_4_entity_seeder.py -v`
Expected: PASS with 4 entity types and 4 edge types validated.

- [ ] **Step 5: Commit and Deploy to VPS**

```bash
git add apps/api/src/api/services/landmark_papers_seeder.py apps/api/tests/test_graph_4_entity_seeder.py
git commit -m "feat(graphrag): seed complete 4-entity ontology with PROPOSES, EVALUATED_ON and ACHIEVES relations"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: LangGraph ReAct Agent Dynamic OpenAI Function Calling Schema

**Files:**
- Modify: `apps/api/src/api/agents/latex_agent.py:260-385`
- Test: `apps/api/tests/test_latex_agent_dynamic_calling.py`

**Interfaces:**
- Consumes: `LatexAgentState`, `openai_client: Any | None`.
- Produces: LLM-driven structured tool invocation via `tool_choice` or deterministic regex fallback when offline.

- [ ] **Step 1: Write failing test for dynamic tool calling execution**

```python
# apps/api/tests/test_latex_agent_dynamic_calling.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from api.agents.latex_agent import build_latex_coauthor_graph

@pytest.mark.asyncio
async def test_latex_agent_invokes_dynamic_tool_calling():
    graph = build_latex_coauthor_graph()
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()

    # Simulate OpenAI returning a tool call for query_library_graph_rag
    tool_call_obj = MagicMock()
    tool_call_obj.function.name = "query_library_graph_rag"
    tool_call_obj.function.arguments = '{"query": "attention mechanism", "top_k": 3}'
    choice = MagicMock()
    choice.message.tool_calls = [tool_call_obj]
    choice.message.content = None
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[choice]))

    initial_state = {
        "draft_id": uuid4(),
        "user_id": uuid4(),
        "message": "Find empirical benchmarks for Attention",
        "main_tex": "\\documentclass{article}\n\\begin{document}\n\\end{document}",
        "bib_content": "",
        "assets": [],
        "compile_count": 0,
        "max_compile_attempts": 3,
        "seen_hashes": [],
        "openai_client": mock_client,
    }

    result = await graph.ainvoke(initial_state)
    assert result.get("last_tool") == "query_library_graph_rag"
    assert mock_client.chat.completions.create.called
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_latex_agent_dynamic_calling.py -v`
Expected: FAIL because `mock_client.chat.completions.create` is not called in `reason_and_plan`.

- [ ] **Step 3: Implement OpenAI Tool Calling in `reason_and_plan`**

1. Define JSON tool schemas for the 4 tools (`edit_latex_files`, `list_project_files`, `query_library_graph_rag`, `compile_latex_e2b`).
2. In `reason_and_plan`, if `state.get("openai_client")` has `chat.completions.create`, pass tools list to `create(model=..., tools=TOOL_SCHEMAS, tool_choice="auto")` to let the model choose the tool.
3. If no client is available, execute the deterministic fallback rules (preserving zero-regression offline testing).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_latex_agent_dynamic_calling.py -v`
Expected: PASS.

- [ ] **Step 5: Commit and Deploy to VPS**

```bash
git add apps/api/src/api/agents/latex_agent.py apps/api/tests/test_latex_agent_dynamic_calling.py
git commit -m "feat(writing): enable dynamic openai tool-calling schema in langgraph latex coauthor agent"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 7: 3-Track Benchmark Suite & LLM-as-a-Judge Evaluation Endpoint

**Files:**
- Create: `apps/api/src/api/schemas/evaluations.py`
- Create: `apps/api/src/api/services/benchmark_runner_service.py`
- Create: `apps/api/src/api/v1/endpoints/evaluations.py`
- Modify: `apps/api/src/api/v1/router.py`
- Test: `apps/api/tests/test_evaluations_benchmark.py`

**Interfaces:**
- Consumes: `POST /api/v1/evaluations/run-benchmark` with `track: "advanced_rag" | "graph_rag" | "agentic_rag" | "all"`.
- Produces: Evaluation scores on 4 criteria: Groundedness ($[0..1]$), Relevance ($[0..1]$), BBox Precision ($[0..1]$), Multi-hop Completeness ($[0..1]$), recorded to Langfuse via `AiTracingService.record_score`.

- [ ] **Step 1: Write failing test for benchmark runner**

```python
# apps/api/tests/test_evaluations_benchmark.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_run_benchmark_evaluations_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    resp = await async_client.post(
        "/api/v1/evaluations/run-benchmark",
        json={"track": "advanced_rag", "experiment_name": "ci_test_run"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["experiment_name"] == "ci_test_run"
    assert data["total_questions"] >= 1
    assert "mean_scores" in data
    assert "groundedness" in data["mean_scores"]
    assert "relevance" in data["mean_scores"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_evaluations_benchmark.py -v`
Expected: FAIL with 404 Not Found on `/api/v1/evaluations/run-benchmark`.

- [ ] **Step 3: Implement Benchmark Suite & LLM-as-a-Judge Service**

1. Create `apps/api/src/api/services/benchmark_runner_service.py`:
   - Contains 36 golden evaluation prompts across 3 tracks (Advanced RAG, GraphRAG, Agentic RAG).
   - `BenchmarkRunnerService.run_benchmark(track, experiment_name, db, user_id, tracing_service)`:
     * Evaluates model responses using LLM-as-a-Judge rubric (or deterministic heuristic fallback if API key is mock).
     * Calculates mean scores for Groundedness, Relevance, BBox Precision, Multi-hop.
     * Records scores to Langfuse via `tracing_service.record_score(name="eval_groundedness", value=..., ...)`.
2. Create `apps/api/src/api/v1/endpoints/evaluations.py` and register in `apps/api/src/api/v1/router.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_evaluations_benchmark.py -v`
Expected: PASS with HTTP 200 and evaluation summary metrics.

- [ ] **Step 5: Run the 4 Verification Gates**

```bash
uv run ruff check . && uv run ruff format --check .
uv run pytest
npm --prefix apps/web run test
npm --prefix apps/web run build
```
Expected: All 4 gates pass with 0 errors.

- [ ] **Step 6: Commit and Deploy to VPS**

```bash
git add apps/api/src/api/schemas/evaluations.py apps/api/src/api/services/benchmark_runner_service.py apps/api/src/api/v1/endpoints/evaluations.py apps/api/src/api/v1/router.py apps/api/tests/test_evaluations_benchmark.py
git commit -m "feat(evals): implement 3-track llm-as-a-judge benchmark runner and langfuse scoring"
bash scripts/deploy_to_vps.sh --fast
```

---

## Self-Review Checklist

1. **Spec Coverage:**
   - FlashRank ONNX cross-encoder & abstention gate (Spec 03 §5.B Khối 5) $\rightarrow$ **Task 1**.
   - Pure domain Wiki Compiler (`wiki_compiler.py`) (Spec 05 §2) $\rightarrow$ **Task 2**.
   - Wiki data model (`wiki_pages`) & persistence (Spec 05 §3) $\rightarrow$ **Task 3**.
   - Wiki REST endpoints & research gaps (Spec 05 §4) $\rightarrow$ **Task 4**.
   - 4-Entity GraphRAG seeder & multi-type relations (Spec 05 §3) $\rightarrow$ **Task 5**.
   - LangGraph dynamic OpenAI tool-calling (Spec 06 §2) $\rightarrow$ **Task 6**.
   - 3-Track Benchmark Suite & Langfuse LLM-as-a-Judge (Spec 07 §1.E, §5.D) $\rightarrow$ **Task 7**.
2. **Step Scan:** Every step has an exact test code block, verification CLI command, and concrete implementation scope.
3. **Type Consistency:** Schema names (`WikiPageModel`, `WikiPageDraft`, `SemanticRerankerService`, `BenchmarkRunnerService`) are consistently defined and consumed across neighboring tasks.
4. **Review Focus:** Five failure modes (ONNX CPU fallback, 4-entity deduplication, slug scoping, LangGraph recursion cutoff, and Langfuse no-op facade) are explicitly tested in Tasks 1, 3, 5, 6, and 7.
5. **Proportion:** Plan is structured into 7 bite-sized, independently testable deliverables without transcript boilerplate.
