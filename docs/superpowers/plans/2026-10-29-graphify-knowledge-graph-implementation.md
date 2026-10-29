# Graphify-Style Force-Directed Knowledge Graph & Dual-Level GraphRAG Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform VeriScholar's Knowledge Graph into an interactive 60fps HTML5 Canvas with `d3-force` physics, deterministic Louvain/Leiden community clustering, an instant paper inspection drawer, and a dual-level GraphRAG query tool for the AI Assistant.

**Architecture:** A Python Louvain partitioning service in `apps/api` statically assigns deterministic `community_id` values and labels to nodes based on network topology. The frontend renders the graph on an HTML5 `<canvas>` via `d3-force` simulation with elastic spring links, community color halos, and node dragging. Scholars can click nodes to view an instant zero-latency inspection drawer or trigger AI community synthesis via GraphRAG.

**Tech Stack:** Python 3.12, FastAPI, NetworkX 3.4 (`louvain_communities`), React 19, HTML5 Canvas 2D, `d3-force` 3.0, Tailwind CSS 4, Zustand, Vitest, pytest.

**Spec:** [`docs/superpowers/specs/2026-10-29-graphify-knowledge-graph-design.md`](../specs/2026-10-29-graphify-knowledge-graph-design.md)

---

## Global Constraints

- **Rule 1 (TDD Mandatory):** Every task must write failing tests first, run to verify failure, implement minimal code to pass, verify green, and commit.
- **Rule 2 (Hexagonal Isolation):** Core graph models and algorithms live in `apps/api/src/api/services/` and `packages/core/`. No DB ORM leaked into core.
- **Rule 4 (The 4 Verification Gates):** Before task completion, verify: Ruff check/format (Gate 1), pytest 100% (Gate 2), Vitest 100% (Gate 3), Vite build 100% (Gate 4).
- **Rule 6 (Radical Minimalism):** UI strictly adheres to Anthropic paper tones (`#fbf9f5` / `#1c1b18`), hairline borders, and zero technical clutter (no raw Q-scores or DB IDs).
- **Rule 9 (VPS Sync Protocol):** After commit, execute `bash scripts/deploy_to_vps.sh --fast`.

## Review Focus

1. **Empty / Disconnected Graph Graceful Fallback:** When a library has 0 papers, or 5 disconnected papers with 0 edges, Louvain community detection and Canvas physics must not crash or divide by zero.
   *Tested in Task 1, Step 1 and Task 4, Step 1.*
2. **Deterministic Community ID Stability:** Partitioning the same graph multiple times must always return identical `community_id` numbers and node assignments (enforced via `seed=42` and canonical node sorting).
   *Tested in Task 1, Step 1.*
3. **High-DPI Canvas Sharpness on Retina Displays:** Canvas must scale its internal buffer by `window.devicePixelRatio` while keeping CSS display dimensions intact to prevent blurry text and halos.
   *Tested in Task 4, Step 1.*
4. **Instant Drawer Zero-Latency Resolution:** Clicking a node must display paper title, abstract, year, and prior/derivative works without firing any secondary network requests.
   *Tested in Task 5, Step 1.*
5. **Community Synthesis FAB Triggering:** Clicking "Summarize Community" must open the GraphRAG chat drawer with the pre-seeded executive prompt and avoid redundant batch indexing.
   *Tested in Task 5, Step 1.*

---

## Task Decomposition

### Task 1: Backend Deterministic Louvain Community Service

**Files:**
- Modify: `pyproject.toml`
- Modify: `apps/api/pyproject.toml`
- Create: `apps/api/src/api/services/graph_community_service.py`
- Test: `apps/api/tests/test_graph_community_service.py`

**Interfaces:**
- Consumes: Raw node dictionaries `[{"id": str, "label": str, "type": str}]` and edge dictionaries `[{"source": str, "target": str, "weight": float}]`.
- Produces: `GraphCommunityService.partition_communities(nodes: list[dict], edges: list[dict], seed: int = 42) -> tuple[dict[str, int], list[dict]]` returning `(node_to_community, communities_list)`.

- [x] **Step 1: Write failing test in `apps/api/tests/test_graph_community_service.py`**

```python
import pytest
from api.services.graph_community_service import GraphCommunityService


def test_partition_communities_deterministic_and_clustered():
    nodes = [
        {"id": "p1", "label": "Attention Is All You Need", "type": "Paper"},
        {"id": "p2", "label": "BERT: Pre-training", "type": "Paper"},
        {"id": "p3", "label": "GPT-3 Few-Shot", "type": "Paper"},
        {"id": "r1", "label": "Retrieval-Augmented Generation", "type": "Paper"},
        {"id": "r2", "label": "GraphRAG: Knowledge Graphs", "type": "Paper"},
    ]
    edges = [
        {"source": "p2", "target": "p1", "weight": 1.0},
        {"source": "p3", "target": "p1", "weight": 1.0},
        {"source": "r2", "target": "r1", "weight": 1.0},
    ]

    service = GraphCommunityService()
    node_to_comm1, comms1 = service.partition_communities(nodes, edges, seed=42)
    node_to_comm2, comms2 = service.partition_communities(nodes, edges, seed=42)

    assert node_to_comm1 == node_to_comm2
    assert len(comms1) >= 2
    # p1, p2, p3 must share the same community
    assert node_to_comm1["p1"] == node_to_comm1["p2"] == node_to_comm1["p3"]
    # r1, r2 must share a distinct community
    assert node_to_comm1["r1"] == node_to_comm1["r2"]
    assert node_to_comm1["p1"] != node_to_comm1["r1"]


def test_partition_communities_handles_empty_and_single_node():
    service = GraphCommunityService()
    node_to_comm, comms = service.partition_communities([], [])
    assert node_to_comm == {}
    assert comms == []

    node_to_comm_single, comms_single = service.partition_communities(
        [{"id": "single", "label": "Lone Paper", "type": "Paper"}], []
    )
    assert node_to_comm_single["single"] == 0
    assert len(comms_single) == 1
    assert comms_single[0]["paper_count"] == 1
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_graph_community_service.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'networkx'` or `cannot import name 'GraphCommunityService'`.

- [x] **Step 3: Add `networkx>=3.4` and implement `GraphCommunityService` in `apps/api/src/api/services/graph_community_service.py`**

Add `networkx>=3.4.0` in `pyproject.toml` and `apps/api/pyproject.toml`. Implement `GraphCommunityService.partition_communities` using `networkx.Graph()`, canonical node sorting, `networkx.algorithms.community.louvain_communities(G, seed=seed, resolution=1.0)`, and generate human-readable labels from top in-degree node labels.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_graph_community_service.py`
Expected: PASS with 2 passed tests.

- [x] **Step 5: Commit**

```bash
git add pyproject.toml apps/api/pyproject.toml apps/api/src/api/services/graph_community_service.py apps/api/tests/test_graph_community_service.py
git commit -m "feat(api): add deterministic louvain community graph service"
```

---

### Task 2: API Contract Enhancement (`GET /api/v1/library/graph` & Schemas)

**Files:**
- Modify: `apps/api/src/api/schemas/library.py:100-160`
- Modify: `apps/api/src/api/v1/endpoints/library.py:125-270`
- Test: `apps/api/tests/test_library_endpoints.py`

**Interfaces:**
- Consumes: `GraphCommunityService` from Task 1.
- Produces: Enhanced `LibraryGraphNode` (`community_id: int`, `community_label: str`, `citation_count: int`, `metadata.abstract`, `metadata.publication_year`) and `LibraryGraphResponseData.communities: list[LibraryCommunity]`.

- [x] **Step 1: Write failing test in `apps/api/tests/test_library_endpoints.py`**

Extend `test_get_library_graph_returns_nodes_and_edges` to assert:
```python
response = await client.get("/api/v1/library/graph", headers=auth_headers)
assert response.status_code == 200
data = response.json()["data"]

assert "communities" in data
assert isinstance(data["communities"], list)
for node in data["nodes"]:
    assert "community_id" in node
    assert "community_label" in node
    assert "citation_count" in node
    assert "metadata" in node
    assert "publication_year" in node["metadata"]
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_library_endpoints.py -k test_get_library_graph`
Expected: FAIL with `KeyError: 'communities'` or assertion failure on `community_id`.

- [x] **Step 3: Update `apps/api/src/api/schemas/library.py` and `apps/api/src/api/v1/endpoints/library.py`**

1. Define `LibraryCommunity(BaseModel)` with `id: int`, `label: str`, `paper_count: int`, `node_ids: list[str]`.
2. Add `communities: list[LibraryCommunity] = Field(default_factory=list)` to `LibraryGraphResponseData`.
3. In `library.py::get_library_graph`:
   - Store `abstract` and `publication_year` in `node.metadata`.
   - Compute in-degree citation count.
   - Run `GraphCommunityService.partition_communities(raw_nodes, raw_edges, seed=42)`.
   - Stamp `community_id` and `community_label` onto each node.
   - Return populated `communities` in `LibraryGraphResponseData`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_library_endpoints.py -k test_get_library_graph`
Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add apps/api/src/api/schemas/library.py apps/api/src/api/v1/endpoints/library.py apps/api/tests/test_library_endpoints.py
git commit -m "feat(api): augment library graph response with communities and node citations"
```

---

### Task 3: AI Assistant GraphRAG Community Tool Integration

**Files:**
- Create: `apps/api/src/api/services/graph_rag_tools.py`
- Modify: `apps/api/src/api/services/latex_agent.py:180-220`
- Test: `apps/api/tests/test_graph_rag_tools.py`

**Interfaces:**
- Consumes: `GraphRAGService.query_graph()` and `GraphCommunityService`.
- Produces: `async def query_library_knowledge_graph(db: AsyncSession, user_id: UUID, query: str, community_id: int | None = None) -> dict[str, Any]` and LangGraph tool wrapper.

- [ ] **Step 1: Write failing test in `apps/api/tests/test_graph_rag_tools.py`**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from api.services.graph_rag_tools import query_library_knowledge_graph


@pytest.mark.asyncio
async def test_query_library_knowledge_graph_tool_delegates_to_service():
    mock_db = AsyncMock()
    user_id = uuid4()
    mock_graph_rag_service = MagicMock()
    mock_graph_rag_service.query_graph = AsyncMock(
        return_value={"answer": "Synthesized insight across community.", "citations": []}
    )

    result = await query_library_knowledge_graph(
        db=mock_db,
        user_id=user_id,
        query="Compare attention architectures",
        community_id=1,
        graph_rag_service=mock_graph_rag_service,
    )

    assert result["answer"] == "Synthesized insight across community."
    mock_graph_rag_service.query_graph.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_graph_rag_tools.py`
Expected: FAIL with `cannot import name 'query_library_knowledge_graph'`.

- [ ] **Step 3: Implement `graph_rag_tools.py` and register in `latex_agent.py`**

Implement `query_library_knowledge_graph` with optional `community_id` filtering, and wire the structured tool definition into the LangGraph tool binding in `latex_agent.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_graph_rag_tools.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/graph_rag_tools.py apps/api/src/api/services/latex_agent.py apps/api/tests/test_graph_rag_tools.py
git commit -m "feat(api): add query_library_knowledge_graph tool for ai agent"
```

---

### Task 4: Frontend HTML5 Canvas Force-Directed Engine (`d3-force`)

**Files:**
- Modify: `apps/web/package.json` (add `"d3-force": "^3.0.0"`, `"@types/d3-force": "^3.0.10"`)
- Create: `apps/web/src/features/library/components/KnowledgeGraphCanvas.tsx`
- Modify: `apps/web/src/features/library/types.ts`
- Test: `apps/web/src/features/library/__tests__/KnowledgeGraphCanvas.test.tsx`

**Interfaces:**
- Consumes: `graphData: LibraryGraphResponseData` (with `nodes`, `edges`, `communities`).
- Produces: Interactive `<canvas>` with `d3-force` physics, `onSelectNode: (node: LibraryGraphNode) => void`, `onSummarizeCommunity: (community: LibraryCommunity) => void`.

- [ ] **Step 1: Write failing test in `apps/web/src/features/library/__tests__/KnowledgeGraphCanvas.test.tsx`**

```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KnowledgeGraphCanvas } from "../components/KnowledgeGraphCanvas";

const mockGraphData = {
  nodes: [
    {
      id: "doc-1",
      label: "Attention Is All You Need",
      type: "Paper",
      degree: 12,
      citation_count: 12,
      community_id: 0,
      community_label: "Transformer Architectures",
      metadata: { publication_year: 2017, abstract: "Transformer model based solely on attention." },
    },
    {
      id: "doc-2",
      label: "BERT: Pre-training",
      type: "Paper",
      degree: 8,
      citation_count: 8,
      community_id: 0,
      community_label: "Transformer Architectures",
      metadata: { publication_year: 2018, abstract: "Bidirectional transformers." },
    },
  ],
  edges: [
    { source: "doc-2", target: "doc-1", relation: "CITES", label: "cites", weight: 1.0 },
  ],
  communities: [
    { id: 0, label: "Transformer Architectures", paper_count: 2, node_ids: ["doc-1", "doc-2"] },
  ],
};

describe("KnowledgeGraphCanvas HTML5 Force Simulation", () => {
  it("renders canvas element with 60fps simulation container", () => {
    const handleSelect = vi.fn();
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData as any}
        onSelectDocument={handleSelect}
      />
    );

    const canvas = screen.getByTestId("knowledge-graph-canvas");
    expect(canvas).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `(cd apps/web && npx vitest run src/features/library/__tests__/KnowledgeGraphCanvas.test.tsx)`
Expected: FAIL with missing `data-testid="knowledge-graph-canvas"` or compilation error.

- [ ] **Step 3: Implement `KnowledgeGraphCanvas.tsx` using `d3-force` on HTML5 Canvas**

1. Setup canvas with `requestAnimationFrame` loop and `d3-force` simulation (`forceSimulation`, `forceLink`, `forceManyBody`, `forceCenter`, `forceCollide`).
2. Implement High-DPI scaling: `canvas.width = rect.width * dpr`, `ctx.scale(dpr, dpr)`.
3. Draw community soft halos behind node clusters using distinct academic palette hues (Coral `#c15f3e`, Indigo `#4f46e5`, Emerald `#059669`, Amber `#d97706`, Rose `#e11d48`, Cyan `#0891b2`).
4. Calculate node radius: $r = \max(10, \min(26, 10 + \text{citation\_count} \times 1.2))$.
5. Add pointer interactions: Pan, Zoom (`wheel`), Drag nodes with spring physics, Hover spotlight (1st-degree citation links glowing, unrelated nodes dimmed).
6. Emit `onSelectDocument` and `onSelectCommunity`.

- [ ] **Step 4: Run test to verify it passes**

Run: `(cd apps/web && npx vitest run src/features/library/__tests__/KnowledgeGraphCanvas.test.tsx)`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/package.json apps/web/src/features/library/components/KnowledgeGraphCanvas.tsx apps/web/src/features/library/types.ts apps/web/src/features/library/__tests__/KnowledgeGraphCanvas.test.tsx
git commit -m "feat(web): implement 60fps html5 canvas force-directed graph with d3-force"
```

---

### Task 5: Frontend Interactive Wiki Graph Right Sidebar, Local Focus & Paper Inspection

**Files:**
- Create: `apps/web/src/features/library/components/PaperInspectionDrawer.tsx`
- Create: `apps/web/src/features/library/components/LibraryGraphSidebar.tsx`
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
- Test: `apps/web/src/features/library/__tests__/PaperInspectionDrawer.test.tsx`
- Test: `apps/web/src/features/library/__tests__/LibraryGraphSidebar.test.tsx`
- Test: `apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx`

**Interfaces:**
- `LibraryGraphSidebar`: A collapsible right panel (380px) hosted in `LibraryWorkspaceView.tsx`, toggled via a `[🕸️ Wiki Graph]` button in the top header.
- Local Subgraph Focus: When a paper is selected from the library table, the sidebar graph centers on that paper and highlights its 1–2 hop connected entities (`Method`, `Dataset`, `MetricResult`, citations) while dimming unrelated nodes.
- Wiki Peek Sheet (`PaperInspectionDrawer`): Slides over the sidebar on node click, rendering paper title, abstract, year, connected entities, KaTeX formulas, and action buttons `[Open in Deep Reader]` and `[Ask AI About This Paper]`.
- Main view retains 100% visibility of the papers table and folders hierarchy on the left.

- [ ] **Step 1: Write failing test in `apps/web/src/features/library/__tests__/PaperInspectionDrawer.test.tsx` and `LibraryGraphSidebar.test.tsx`**

```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PaperInspectionDrawer } from "../components/PaperInspectionDrawer";

describe("PaperInspectionDrawer Component", () => {
  const dummyNode = {
    id: "doc-attention",
    label: "Attention Is All You Need",
    type: "Paper",
    degree: 15,
    citation_count: 15,
    community_id: 0,
    community_label: "Transformer Architectures",
    metadata: {
      publication_year: 2017,
      abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
      filename: "attention.pdf",
    },
  };

  it("renders paper details instantly without loading spinners", () => {
    const handleClose = vi.fn();
    const handleOpenReader = vi.fn();

    render(
      <PaperInspectionDrawer
        isOpen={true}
        node={dummyNode as any}
        allNodes={[dummyNode] as any}
        allEdges={[]}
        onClose={handleClose}
        onOpenReader={handleOpenReader}
      />
    );

    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText("2017")).toBeInTheDocument();
    expect(screen.getByText(/sequence transduction models/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Open in Deep Reader/i })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `(cd apps/web && npx vitest run src/features/library/__tests__/PaperInspectionDrawer.test.tsx)`
Expected: FAIL with `cannot find module PaperInspectionDrawer`.

- [ ] **Step 3: Implement `PaperInspectionDrawer.tsx`, `LibraryGraphSidebar.tsx`, and integrate into `LibraryWorkspaceView.tsx`**

1. Implement `PaperInspectionDrawer` with pure client-side prior/derivative derivation from `allEdges` and Markdown/KaTeX preview.
2. Implement `LibraryGraphSidebar` wrapping `KnowledgeGraphCanvas` in a clean 380px collapsible panel with search filter and community pills.
3. In `LibraryWorkspaceView.tsx`:
   - Add a `[🕸️ Wiki Graph]` toggle button on the header toolbar.
   - Maintain the documents list and folders hierarchy in the main panel.
   - When the graph sidebar is open, render `LibraryGraphSidebar` on the right side.
   - Clicking a paper in the table sets `focusedNodeId`, centering and highlighting its local subgraph in the sidebar.
4. Clicking `[Summarize Community]` or `[Ask AI About This Paper]` triggers the floating GraphRAG assistant with a pre-seeded prompt.

- [ ] **Step 4: Run test to verify it passes**

Run: `(cd apps/web && npx vitest run src/features/library/__tests__/PaperInspectionDrawer.test.tsx src/features/library/__tests__/LibraryWorkspaceView.test.tsx)`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/library/components/PaperInspectionDrawer.tsx apps/web/src/features/library/components/LibraryGraphSidebar.tsx apps/web/src/features/library/components/LibraryWorkspaceView.tsx apps/web/src/features/library/__tests__/PaperInspectionDrawer.test.tsx apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx
git commit -m "feat(web): add interactive wiki graph right sidebar, local focus and inspection drawer"
```

---

### Task 6: The 4 Verification Gates & Remote VPS Fast Rollout

**Files:**
- Ledger: `docs/superpowers/plans/2026-10-29-graphify-knowledge-graph-implementation.ledger.md`

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: 0 errors, 100% formatted.

- [ ] **Step 2: Gate 2 - Backend & Boundary Tests**

Run: `uv run pytest`
Expected: 100% passed (285+ tests).

- [ ] **Step 3: Gate 3 - Frontend Vitest Suite**

Run: `npm --prefix apps/web run test`
Expected: 100% passed (55+ test files, 226+ tests).

- [ ] **Step 4: Gate 4 - Frontend Production Build**

Run: `npm --prefix apps/web run build`
Expected: Exit code 0, cleanly bundled.

- [ ] **Step 5: Remote VPS Fast Rollout (Rule 9)**

Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Exit code 0, live health probe HTTP 200 OK at `https://verischolar.duckdns.org`.

- [ ] **Step 6: Commit ledger and complete plan**

```bash
git add docs/superpowers/plans/2026-10-29-graphify-knowledge-graph-implementation.ledger.md
git commit -m "docs: complete ledger for graphify knowledge graph implementation"
```
