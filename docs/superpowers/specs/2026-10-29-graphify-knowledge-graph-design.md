# Design Specification: Graphify-Style Force-Directed Knowledge Graph & Dual-Level GraphRAG Assistant

- **Date:** 2026-10-29
- **Author:** VeriScholar Engineering & AI Agent Pair
- **Status:** Proposed (Under Review)
- **Target Components:** `apps/api` (Leiden Community Partitioning & GraphRAG Agent Tool), `apps/web` (Interactive HTML5 Canvas Force-Directed Knowledge Graph Viewer)

---

## 1. Intent & The Why

VeriScholar's primary mission is to serve as an intelligent, high-integrity scientific research assistant. While the platform has an underlying graph database storing papers, citations (`CITES`), and concept entities (`Method`, `Dataset`, `MetricResult`), the user experience was impaired by two critical gaps:
1. **Visualization Gap:** The previous Knowledge Graph rendered papers in a hardcoded, rigid static SVG ellipse. It lacked physics, interactive node dragging, cluster detection, and fluid 60fps exploration.
2. **AI Synergy Gap:** The graph existed largely in isolation from the chat assistant; users could not ask the AI assistant to perform structured synthesis queries across topical clusters of their library.

By adopting the proven open-source architecture of **Graphify** (`Graphify-Labs`) and **Karpathy's LLM Wiki / Microsoft GraphRAG**, VeriScholar will unite:
- **Topological Community Detection (Leiden / Louvain):** Partitioning the literature graph into coherent scientific clusters (e.g., *Transformer Architectures*, *Retrieval-Augmented Generation*, *Alignment & Preference Optimization*).
- **Interactive 60fps HTML5 Canvas (d3-force):** A tactile, responsive graph with spring physics, community color halos, drag-and-drop, zoom/pan, and instant paper inspection.
- **Dual-Level GraphRAG Assistant Tool:** Allowing the conversational assistant to query specific literature communities (`query_graph_community`) to answer cross-paper comparative questions with zero hallucination.

---

## 2. Goals, Non-Goals & Anti-Goals

### 2.1 Goals
- **G1: High-Performance 60fps Canvas Rendering:** Replace the rigid SVG with an HTML5 Canvas simulation driven by `d3-force` (link springs, charge repulsion, center force, collision avoidance).
- **G2: Deterministic Community Detection:** Implement Louvain / Leiden modularity partitioning on graph relations (`CITES`, `USES_METHOD`, `EVALUATED_ON`) in backend Python without external heavy dependencies.
- **G3: Semantic Community Halos & Color Coding:** Visually group papers belonging to the same cluster using an elegant academic palette (Coral, Indigo, Emerald, Amber, Rose, Teal) with soft translucent community halos.
- **G4: Tactile Drag & Drill-down Drawer:** Users can drag nodes with spring physics, hover to highlight 1st-degree citation neighbors, click a node to open an inspection drawer (Title, Abstract, Citations, Deep Reader jump), and click a community to see an AI cluster summary.
- **G5: GraphRAG Chat Tool:** Expose `query_graph_community` to the AI Assistant so scholars can prompt: *"Summarize key distinctions between RAG and GraphRAG papers in my library"*.

### 2.2 Non-Goals
- Real-time WebGL 3D rendering (2D Canvas provides superior clarity, text legibility, and mobile/desktop performance for academic paper graphs < 2,000 nodes).
- Manual edge editing by scholars (citations and relations are auto-extracted from PDFs and reference lists).

### 2.3 Anti-Goals
- **No Heavy Parquet/Batch Bloat:** Avoid the sluggish, expensive offline batch indexing pipeline of Microsoft GraphRAG. Graph updates must be instant on paper upload.
- **No Vector-Only Illusion:** Do not rely merely on embedding cosine distances; topology and real citation links (`reference_items` / `GraphEdgeModel`) must form the primary ground truth.
- **No Technical Jargon on UI:** The UI must adhere to Radical Minimalism (Rule 6). No raw math formulas, modularity Q-scores, or database IDs displayed on the canvas.

---

## 3. Constraints & Architecture Rules
- **Rule 1 (TDD Mandatory):** Backend and frontend unit tests must prove community partitioning and canvas component state transitions before production deployment.
- **Rule 2 (Hexagonal Isolation):** Core domain graph logic resides in `packages/core` or pure services in `apps/api/src/api/services/`. No ORM or HTTP logic leaked into core.
- **Rule 4 (The 4 Verification Gates):** Ruff lint/format, pytest (282+ tests), vitest (55+ suites), and vite build must pass with exit code 0.
- **Rule 6 (Radical Minimalism):** Clean Anthropic paper theme (`#fbf9f5` / `#181715`), crisp typography, minimal clutter.
- **Rule 9 (VPS Sync Protocol):** Auto-run `bash scripts/deploy_to_vps.sh --fast` after commit.

---

## 4. Approaches Considered & Trade-offs

| Criterion | Approach 1: Microsoft GraphRAG Core | Approach 2: Graphify-Style Canvas & Native Leiden (Selected) | Approach 3: Custom SVG Hooke Physics from Scratch |
| :--- | :--- | :--- | :--- |
| **Rendering Tech** | None (CLI & Parquet only) | **HTML5 Canvas + `d3-force` (60fps)** | Custom SVG / React state loops |
| **Performance** | N/A | **Fluid 60fps up to 2,000+ nodes** | Lags noticeably > 50 nodes |
| **Community Detection** | Hierarchical Leiden (heavy batch) | **Native NetworkX Louvain/Leiden** | Manual heuristic grouping |
| **Indexing Latency** | 5–15 minutes per document | **< 100ms instant topological update** | Instant |
| **Operational Cost** | High (dozens of LLM calls per doc) | **Zero additional LLM cost on ingestion** | Zero |
| **Integration Complexity** | Severe architectural mismatch | **Natural fit with existing PostgreSQL models** | High maintenance burden |

**Selected Approach:** **Approach 2 (Graphify-Style Canvas & Native Leiden)**. It delivers the best visual and interactive standard without adding system bloat or operational costs.

---

## 5. Technical Specifications & Architecture

### 5.1 Backend: Community Detection & Topological Partitioning

1. **Service (`apps/api/src/api/services/graph_community_service.py`):**
   - Builds an in-memory graph from the user's `graph_nodes`, `graph_edges`, and `reference_items` (CITES links).
   - Applies deterministic `networkx.algorithms.community.louvain_communities(G, seed=42, resolution=1.0)` on canonically sorted node IDs to ensure zero community ID drift across calls.
   - Assigns a numeric `community_id` (0, 1, 2, ...) and generates a descriptive label based on the most prominent paper titles / keywords in that community.
2. **API Contract Update (`GET /api/v1/library/graph`):**
   - Augments `node.metadata` with `abstract`, `publication_year`, and `authors` from `DocumentModel`.
   - `LibraryGraphNode` schema augmented with:
     - `community_id: int`
     - `community_label: str`
     - `citation_count: int` (in-degree from `reference_items` + `graph_edges`)
   - `LibraryGraphResponseData` (and `LibraryGraphResponseEnvelope`) includes:
     ```python
     class LibraryCommunity(BaseModel):
         id: int
         label: str
         paper_count: int
         node_ids: list[str]
     ```
   - Located inside `LibraryGraphResponseData.communities` so `apiClient` delivers it cleanly to frontend components.

### 5.2 Frontend: HTML5 Canvas Force-Directed Engine (`d3-force`)

1. **Component Replacement (`apps/web/src/features/library/components/KnowledgeGraphCanvas.tsx`):**
   - Employs an HTML5 `<canvas>` element with high-DPI scaling (`window.devicePixelRatio`).
   - Uses `d3-force` (or standalone force engine):
     - `forceSimulation(nodes)`
     - `forceLink(edges).id(d => d.id).distance(80).strength(0.6)`
     - `forceManyBody().strength(-280)`
     - `forceCenter(width / 2, height / 2).strength(0.05)`
     - `forceCollide().radius(d => d.radius + 6)`
   - **Visual Elements:**
     - **Community Halos:** Subtle translucent soft convex boundaries grouping nodes of the same `community_id` with academic palette colors (Coral, Indigo, Emerald, Amber, Rose, Cyan).
     - **Node Sizing:** Seminal papers with higher citation counts receive larger radii ($r \in [10px, 26px]$).
     - **Spring Interactions:** Pointer drag gently pulls adjacent nodes with elastic spring dynamics.
     - **Hover Spotlight:** Hovering over a paper highlights its 1st-degree citation links and dims unrelated nodes.
2. **Academic Details Drawer (`PaperInspectionDrawer.tsx`):**
   - **Instantaneous client-side resolution:** Paper Title, Year, Abstract, Primary Entities, and 1st-degree Prior/Derivative works are resolved directly from `node.metadata` and graph `edges` without extra API roundtrips.
   - Action Buttons: `[Open in Deep Reader]` (binds to active session) and `[Ask AI About This Paper]`.
3. **Community Filter Ribbon & AI Summarization:**
   - Pill buttons along the top allowing scholars to filter by cluster: `[All]`, `[Community 0: ...]`, `[Community 1: ...]`.
   - Clicking `[Summarize Community]` opens the existing `GraphRagAssistantFab` / Chat Drawer pre-seeded with: *"Provide an executive academic synthesis of the [Community Label] cluster in my library"*, leveraging the existing streaming SSE pipeline with 0 extra ingestion cost.

### 5.3 AI Assistant: GraphRAG Query Tool Integration

1. **Tool Definition (`apps/api/src/api/services/graph_rag_tools.py`):**
   - Function `query_library_knowledge_graph(query: str, community_id: int | None = None)`.
   - Resolves `community_id` into member document IDs from the deterministic Louvain partition and passes them to `GraphRAGService.query_graph()`.
   - Integrated as an active LangGraph tool in `latex_agent.py` (`/writing`), and accessible in `/dashboard` via the GraphRAG FAB and query routing.

---

## 6. What's Left to the Builder
- Selection of the specific palette hues to match Anthropic dark/light themes.
- Canvas animation dampening factors (`alphaDecay = 0.028`, `velocityDecay = 0.35`) for silky settling behavior.
- Graceful fallback when the library contains fewer than 2 documents.
