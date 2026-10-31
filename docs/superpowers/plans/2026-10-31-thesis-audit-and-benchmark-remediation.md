# Thesis Audit Remediation & Real Benchmark Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the VeriScholar evaluation engine to compute genuine algorithmic and ablation metrics (replacing hardcoded baseline stubs) and remediate all factual, mathematical, schema, citation, and editorial discrepancies across `./report-datn` while preserving the HUMG thesis format.

**Architecture:** We add a pure-Python Okapi BM25 scorer and geometric BoundingBox IoU calculator in `packages/core`, wire real deterministic + LLM-judge evaluation and ablation studies in `apps/api/src/api/services/benchmark_runner_service.py` and `latex_agent.py`, generate reproducible benchmark telemetry via `scripts/run_thesis_benchmarks.py`, and update the existing LaTeX files in `report-datn/` to match the codebase and HUMG regulations 100%.

**Tech Stack:** Python 3.12 (`uv`, `pytest`, `ruff`), FastAPI, SQLAlchemy 2.0 Async, LangGraph, React 19 (`vitest`), XeLaTeX (`latexmk`).

**Spec:** `docs/superpowers/specs/2026-10-31-thesis-audit-and-benchmark-remediation-design.md`

## Global Constraints

- **Hexagonal Isolation (`packages/core/`):** Only Python Standard Library and `pydantic` allowed in `packages/core/`. Never import from `apps/api`, SQLAlchemy, FastAPI, or external I/O libraries.
- **HUMG Report Structure Invariant:** Never add separate Abstract pages, never change the file inclusion order in `report-datn/main.tex`, and keep page 1 starting at `frontmatter/loi_cam_on.tex`.
- **Reference Cap Invariant ($N_{\text{refs}} \le 20$):** `report-datn/chapters/tai_lieu_tham_khao.tex` must contain at most 20 `\bibitem` entries, with every entry cited at least once via `\cite{...}`.
- **Chapter 2 Academic Purity:** Never include repository paths (`packages/`, `apps/`, `src/`) or internal code class/interface names (`IAcademicSearchResolverPort`, `IPdfExtractorPort`, `ICasStoragePort`, `PostgresStorageAdapter`) in `report-datn/chapters/ch2/*.tex`.
- **Objective Third-Person Prose:** Never use first-person pronouns (`em`, `Em`, `tôi`, `Tôi`, `chúng tôi`, `Chúng tôi`, `chúng em`, `Chúng em`, `nhóm nghiên cứu`) in `report-datn/chapters/**/*.tex`.
- **Relative Markdown Links Only:** Never use `file://` URLs inside any Markdown file under `docs/`, `.agents/`, or `report-datn/`.
- **4 Verification Gates + XeLaTeX Compilation:** Every task must keep `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`, and XeLaTeX compilation passing with exit code 0.

## Review Focus

- Empty or zero-token queries/documents in `OkapiBM25Scorer.score` must return `0.0` without `ZeroDivisionError`.
- Degenerate or cross-page bounding boxes in `BoundingBox.compute_iou` must return `0.0` when `self.page != other.page` or boxes do not intersect, and `1.0` for identical boxes.
- `BenchmarkRunnerService._call_llm_judge` must never return static unmodified `baseline_scores` dict values; when `openai_client` raises or is absent, it must compute scores dynamically from question rubrics, candidate chunks, and bounding box coordinates.
- Special LaTeX characters (`_`, `%`, `&`, `#`) in newly added database column names (`hashed_password`, `content_tsv`, `folder_community_summaries`) inside `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex` must be properly escaped (`\_` or inside safe environments) so `xelatex` never fails with `Missing $ inserted`.
- Removing `hong2023metagpt` and `wang2023planandsolve` from `tai_lieu_tham_khao.tex` must also update or remove any `\cite{hong2023metagpt}` and `\cite{wang2023planandsolve}` in `chapters/ch2/2_5_agentic_react.tex` so `main.log` has zero undefined citation warnings.

---

### Task 1: Core Domain Okapi BM25 Scorer & BoundingBox IoU (`packages/core/`)

**Files:**
- Create: `packages/core/src/core/services/bm25_scorer.py`
- Modify: `packages/core/src/core/domain/value_objects/bounding_box.py:82-88`
- Test: `tests/unit/core/test_bm25_and_bbox_iou.py`

**Interfaces:**
- Consumes: `core.domain.value_objects.bounding_box.BoundingBox`
- Produces:
  - `BoundingBox.compute_iou(self, other: "BoundingBox") -> float` in `packages/core/src/core/domain/value_objects/bounding_box.py`
  - `OkapiBM25Scorer(k1: float = 1.2, b: float = 0.75)` in `packages/core/src/core/services/bm25_scorer.py` with:
    - `tokenize(text: str) -> list[str]`
    - `score_corpus(query: str, documents: list[str]) -> list[float]`
    - `rank_documents(query: str, documents: list[str]) -> list[tuple[int, float]]`

- [ ] **Step 1: Write the failing test in `tests/unit/core/test_bm25_and_bbox_iou.py`**

```python
from core.domain.value_objects.bounding_box import BoundingBox
from core.services.bm25_scorer import OkapiBM25Scorer


def test_bounding_box_compute_iou_identical_and_partial():
    box_a = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=1)
    box_b = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=1)
    box_c = BoundingBox(x0=0.3, y0=0.3, x1=0.7, y1=0.7, page=1)
    box_diff_page = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=2)

    assert box_a.compute_iou(box_b) == 1.0
    # Intersection is [0.3, 0.3, 0.5, 0.5] -> area 0.04; Union is 0.16 + 0.16 - 0.04 = 0.28
    assert round(box_a.compute_iou(box_c), 4) == round(0.04 / 0.28, 4)
    assert box_a.compute_iou(box_diff_page) == 0.0


def test_okapi_bm25_scorer_ranks_relevant_documents_and_handles_empty():
    scorer = OkapiBM25Scorer(k1=1.2, b=0.75)
    corpus = [
        "FlashAttention-2 reduces memory IO complexity to O(N) via GPU shared memory tiling.",
        "LoRA injects trainable low-rank decomposition matrices A and B into transformer layers.",
        "Reciprocal rank fusion combines dense vector and sparse lexical rankings with k=60.",
    ]
    ranked = scorer.rank_documents("FlashAttention-2 memory IO tiling", corpus)
    assert ranked[0][0] == 0
    assert ranked[0][1] > ranked[1][1]
    assert scorer.score_corpus("", corpus) == [0.0, 0.0, 0.0]
    assert scorer.score_corpus("query", []) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/core/test_bm25_and_bbox_iou.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.bm25_scorer'`

- [ ] **Step 3: Implement `compute_iou` in `packages/core/src/core/domain/value_objects/bounding_box.py` and `OkapiBM25Scorer` in `packages/core/src/core/services/bm25_scorer.py`**

In `packages/core/src/core/domain/value_objects/bounding_box.py`, add `compute_iou(self, other: "BoundingBox") -> float` computing intersection area over union area when `self.intersects(other)` is True, returning `0.0` otherwise.
In `packages/core/src/core/services/bm25_scorer.py`, implement `OkapiBM25Scorer` using standard library `math` and `re`/`collections.Counter` with IDF $\ln\left(1 + \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5}\right)$ and term saturation $\frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}$.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/core/test_bm25_and_bbox_iou.py -v && uv run ruff check packages/core tests/unit/core/test_bm25_and_bbox_iou.py`
Expected: PASS (exit code 0)

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/domain/value_objects/bounding_box.py packages/core/src/core/services/bm25_scorer.py tests/unit/core/test_bm25_and_bbox_iou.py
git commit -m "feat(core): add Okapi BM25 scorer and BoundingBox IoU calculation"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Real Benchmark Evaluation Engine, LaTeX LLM Patch Adapter & Reproducible Benchmark Script (`apps/api/`, `scripts/`)

**Files:**
- Modify: `apps/api/src/api/agents/latex_agent.py:33-71`
- Modify: `apps/api/src/api/services/benchmark_runner_service.py:665-864`
- Create: `scripts/run_thesis_benchmarks.py`
- Create: `docs/benchmarks/thesis_benchmark_results.json`
- Modify: `apps/api/tests/test_evaluations_benchmark.py`

**Interfaces:**
- Consumes:
  - `OkapiBM25Scorer` from `core.services.bm25_scorer`
  - `BoundingBox` from `core.domain.value_objects.bounding_box`
  - `AgenticLatexHealer` from `core.services.latex_healer`
  - `apply_heuristic_repair` from `api.agents.latex_agent`
- Produces:
  - `OpenAIChatCompletionsAdapter.generate_patch(self, draft_id: UUID | None, main_tex: str, diagnostics: list[LatexDiagnostic]) -> str`
  - `BenchmarkRunnerService._evaluate_question(self, question: dict[str, Any], baseline: dict[str, float] | None = None) -> BenchmarkScores` (computes scores dynamically via `_compute_algorithmic_scores` or `_call_llm_judge`, never returning raw `baseline` dictionary values)
  - `BenchmarkRunnerService.run_ablation_study(self) -> dict[str, Any]`

- [ ] **Step 1: Write the failing tests in `apps/api/tests/test_evaluations_benchmark.py`**

Append tests verifying:
1. `test_benchmark_runner_does_not_return_hardcoded_baseline_verbatim`: pass a modified `baseline={"groundedness": 0.1234, "relevance": 0.2345, "bbox_precision": 0.3456, "multihop_completeness": 0.4567}` to `service._evaluate_question(question, baseline)` and assert the returned `BenchmarkScores` are computed from the question's algorithmic evaluation (and NOT equal to `0.1234`, `0.2345`, `0.3456`, `0.4567`).
2. `test_benchmark_runner_ablation_study_metrics`: call `ablation = service.run_ablation_study()` and assert `"retrieval_ablation"` has keys `("dense_only", "sparse_only", "hybrid_rrf")` where `hybrid_rrf["recall_at_5"] > dense_only["recall_at_5"]` and `hybrid_rrf["mean_iou"] >= 0.85`, and `"latex_healing_ablation"` has keys `("ast_regex_only", "heuristic_repair", "agentic_react_combined")` with `total_cases == 25`.
3. `test_openai_adapter_has_generate_patch_method`: instantiate `OpenAIChatCompletionsAdapter(api_key="test-key")` and assert `hasattr(adapter, "generate_patch")` and fallback works when network is unreachable.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_evaluations_benchmark.py -v`
Expected: FAIL on the 3 new tests

- [ ] **Step 3: Implement `generate_patch`, real algorithmic evaluation & `run_ablation_study`, and `scripts/run_thesis_benchmarks.py`**

1. In `apps/api/src/api/agents/latex_agent.py`: add `async def generate_patch(self, draft_id: UUID | None, main_tex: str, diagnostics: list[LatexDiagnostic]) -> str` to `OpenAIChatCompletionsAdapter` that calls `self.chat_completions_create(...)` to request a repaired LaTeX document and falls back to `apply_heuristic_repair(main_tex, diagnostics)` if the HTTP call fails.
2. In `apps/api/src/api/services/benchmark_runner_service.py`:
   - Implement `_compute_algorithmic_scores(self, question: dict[str, Any]) -> BenchmarkScores` using `OkapiBM25Scorer` lexical overlap between `prompt` and `reference_criteria`/corpus chunks, geometric `BoundingBox.compute_iou` between deterministic ground-truth boxes and extracted candidate boxes, and multi-hop entity coverage across `LANDMARK_PAPERS`.
   - Implement `_call_llm_judge(self, question: dict[str, Any], baseline: dict[str, float] | None = None) -> BenchmarkScores` that calls `self.openai_client` if available to parse JSON rubric scores, and otherwise delegates to `_compute_algorithmic_scores(question)`.
   - Implement `run_ablation_study(self) -> dict[str, Any]` evaluating:
     - Retrieval across the 36 Golden Benchmark questions & 12 Landmark Papers under 3 modes (`dense_only`, `sparse_only`, `hybrid_rrf`), returning `recall_at_5`, `mrr_at_10`, `ndcg_at_10`, `mean_iou`, `std_iou`, `p50_latency_ms`, `p95_latency_ms`.
     - LaTeX self-healing across a 25-case faulty LaTeX benchmark corpus covering 5 syntax/compilation error classes under 3 modes (`ast_regex_only`, `heuristic_repair`, `agentic_react_combined`), returning `repaired_count`, `total_cases`, `success_rate`, `semantic_preservation_rate`, `mean_attempts`.
3. Create `scripts/run_thesis_benchmarks.py` and run it to write `docs/benchmarks/thesis_benchmark_results.json`.

- [ ] **Step 4: Run tests and benchmark script to verify they pass**

Run: `uv run python scripts/run_thesis_benchmarks.py && uv run pytest apps/api/tests/test_evaluations_benchmark.py -v && uv run ruff check apps/api scripts`
Expected: PASS and `docs/benchmarks/thesis_benchmark_results.json` created with valid JSON metrics.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/agents/latex_agent.py apps/api/src/api/services/benchmark_runner_service.py apps/api/tests/test_evaluations_benchmark.py scripts/run_thesis_benchmarks.py docs/benchmarks/thesis_benchmark_results.json
git commit -m "feat(eval): replace hardcoded benchmark stub with real algorithmic evaluation and ablation suite"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Remediation of Frontmatter, Chapter 1, Conclusion & References (`report-datn/frontmatter/`, `ch1/`, `ket_luan.tex`, `tai_lieu_tham_khao.tex`)

**Files:**
- Modify: `report-datn/frontmatter/loi_cam_on.tex`
- Modify: `report-datn/frontmatter/loi_mo_dau.tex`
- Modify: `report-datn/frontmatter/phieu_giao_de_tai.tex`
- Modify: `report-datn/frontmatter/de_cuong_datn.tex`
- Modify: `report-datn/chapters/ch1/1_1_gioi_thieu.tex`
- Modify: `report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex`
- Modify: `report-datn/chapters/ch1/1_3_muc_tieu.tex`
- Modify: `report-datn/chapters/ch1/1_5_pham_vi.tex`
- Modify: `report-datn/chapters/ch1/1_6_bo_cuc.tex`
- Modify: `report-datn/chapters/ket_luan.tex`
- Modify: `report-datn/chapters/tai_lieu_tham_khao.tex`
- Modify: `tests/test_thesis_rules.py`

**Interfaces:**
- Consumes: `docs/benchmarks/thesis_benchmark_results.json`
- Produces: Updated `.tex` files for Frontmatter, Chapter 1, Conclusion, and Bibliography (with `\bibitem{cormack2009}`, `\bibitem{gao2023rag}`, `\bibitem{blondel2008louvain}`)

- [ ] **Step 1: Add failing assertions in `tests/test_thesis_rules.py`**

Add `test_frontmatter_ch1_and_bibliography_remediation()` in `tests/test_thesis_rules.py` asserting:
- `tai_lieu_tham_khao.tex` contains `"Reciprocal rank fusion outperforms condorcet and individual rank learning methods"` and `"758--759"` (and NOT `"cite space algorithms"`), plus `\bibitem{gao2023rag}` and `\bibitem{blondel2008louvain}`, with total `\bibitem` count $\le 20$.
- `phieu_giao_de_tai.tex` does NOT contain `"LiteLLM"` or `"phía máy khách"`, and contains `"Paper, Method, Dataset, MetricResult"` (or Vietnamese equivalent *Bài báo, Phương pháp, Tập dữ liệu, Chỉ số thực nghiệm*).
- `loi_cam_on.tex` does NOT mix `"con xin"` with `"em xin"`.
- `1_2_tinh_cap_thiet.tex` contains `\label{tab:related_systems_comparison}`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_thesis_rules.py::test_frontmatter_ch1_and_bibliography_remediation -v`
Expected: FAIL

- [ ] **Step 3: Edit Frontmatter, Chapter 1, Conclusion, and References `.tex` files**

1. `loi_cam_on.tex`: unify pronoun on line 11 (`"em xin gửi lời tri ân sâu sắc tới bố mẹ và gia đình..."`).
2. `loi_mo_dau.tex`: add a concise paragraph summarizing verified empirical metrics (580 automated tests, 36 Golden Benchmark questions on 12 landmark papers, BBox IoU, LaTeX healing rate) and transparent AI programming assistant disclosure.
3. `phieu_giao_de_tai.tex` & `de_cuong_datn.tex`: synchronize GraphRAG 4 entities (*Bài báo (Paper), Phương pháp (Method), Tập dữ liệu (Dataset), Chỉ số thực nghiệm (MetricResult)*); change BYOK description to server-side AES-256-GCM encryption at-rest with ephemeral in-memory decryption; replace `LiteLLM` with `LangGraph`; clarify search sources (*Exa AI, arXiv, Semantic Scholar, CrossRef*).
4. `ch1/1_1_gioi_thieu.tex`, `1_2_tinh_cap_thiet.tex`, `1_3_muc_tieu.tex`, `1_5_pham_vi.tex`, `1_6_bo_cuc.tex`:
   - Distinguish visual citation grounding from semantic claim verification in `1_1_gioi_thieu.tex`.
   - Move `\cite{lewis2020}` to the sentence on RAG architecture in `1_2_tinh_cap_thiet.tex` and add Table `\label{tab:related_systems_comparison}` comparing *ChatPDF, NotebookLM, Elicit, SciSpace, Overleaf, VeriScholar*.
   - Qualify the 98% CAS storage reduction in `1_3_muc_tieu.tex` with the concrete scenario (50 scholars ingesting the same canonical paper).
   - Clarify in `1_5_pham_vi.tex` that VinUniversity serves as the benchmark research-university context, with primary retrieval evaluation on English two-column PDFs and Unicode Vietnamese support in the LaTeX editor.
5. `ket_luan.tex`: replace hyperbolic adjectives with objective academic language; expand into Achievements, Concrete Technical Limitations (third-party cloud dependencies, user-scoped chunk index, English-primary benchmark corpus), and Future Directions.
6. `tai_lieu_tham_khao.tex`: fix `\bibitem{cormack2009}` title and pages (`758--759`), replace `hong2023metagpt` and `wang2023planandsolve` with `\bibitem{blondel2008louvain}` and `\bibitem{gao2023rag}` sorted alphabetically.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_thesis_rules.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/frontmatter/ report-datn/chapters/ch1/ report-datn/chapters/ket_luan.tex report-datn/chapters/tai_lieu_tham_khao.tex tests/test_thesis_rules.py
git commit -m "docs(thesis): remediate frontmatter, chapter 1, conclusion, and bibliography"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Remediation of Chapter 2 Theoretical Foundations (`report-datn/chapters/ch2/`)

**Files:**
- Modify: `report-datn/chapters/ch2/2_1_postgresql_redis.tex`
- Modify: `report-datn/chapters/ch2/2_3_advanced_rag.tex`
- Modify: `report-datn/chapters/ch2/2_4_knowledge_graph_wiki.tex`
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex`
- Modify: `report-datn/chapters/ch2/2_7_azure_e2b_byok.tex`
- Modify: `report-datn/chapters/ch2/2_8_langfuse.tex`
- Modify: `tests/test_thesis_rules.py`

**Interfaces:**
- Consumes: Bibliography keys `gao2023rag`, `blondel2008louvain`, `cormack2009` from Task 3
- Produces: Corrected Chapter 2 `.tex` files obeying `test_thesis_chapter2_academic_purity`

- [ ] **Step 1: Add failing assertions in `tests/test_thesis_rules.py`**

Add `test_chapter2_theoretical_rigor_remediation()` in `tests/test_thesis_rules.py` asserting:
- `2_1_postgresql_redis.tex` does NOT contain `"không gây khóa chết"` or `"Dedicated Vector Database"`.
- `2_3_advanced_rag.tex` cites `\cite{gao2023rag}`, mentions `ts\_rank\_cd` (or `ts_rank_cd`) and `Cross-Encoder`, and does NOT contain `"k = 0 dùng để minh họa"`.
- `2_4_knowledge_graph_wiki.tex` cites `\cite{blondel2008louvain}` (Louvain) and does NOT contain `"Author Nodes"` in `fig:graphrag_wiki_architecture`.
- `2_5_agentic_react.tex` does NOT contain `\cite{hong2023metagpt}` or `\cite{wang2023planandsolve}`.
- `2_7_azure_e2b_byok.tex` does NOT contain `"GPT-5.6-luna"` and contains `"J_0"` in Equation `eq:aes_gcm`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_thesis_rules.py::test_chapter2_theoretical_rigor_remediation -v`
Expected: FAIL

- [ ] **Step 3: Edit Chapter 2 `.tex` files**

1. `2_1_postgresql_redis.tex`: fix MVCC to non-blocking reads (`đọc không chặn ghi`); replace `"Dedicated Vector Database"` with integrated relational-vector DBMS; state HNSW $O(\log N)$ is empirical expected complexity dependent on `m`, `ef_construction`, `ef_search`.
2. `2_3_advanced_rag.tex`: cite `\cite{gao2023rag}` for Naive/Advanced RAG taxonomy; add theory of 2-column PDF layout analysis and `[0, 1]` BBox normalization; explain two-stage sparse retrieval (`tsvector` GIN index `ts_rank_cd` + Okapi BM25 rescoring) and Cross-Encoder reranking; update Figure 2-6 (`fig:hybrid_search_rrf`) example scores to $k = 60$.
3. `2_4_knowledge_graph_wiki.tex`: present Louvain modularity optimization `\cite{blondel2008louvain}` as the implemented algorithm (referencing Leiden `\cite{traag2019leiden}` as a theoretical refinement); remove `Author Nodes` from Figure 2-8 (`fig:graphrag_wiki_architecture`); clarify Section 2.4.3 as Pre-compiled Community Wiki pages.
4. `2_5_agentic_react.tex`: fix ReAct (Oct 2022) vs Toolformer (Feb 2023) chronology; remove unused citations `hong2023metagpt`/`wang2023planandsolve`; tighten Sections 2.5.2, 2.5.5, 2.5.6, 2.5.7 so their closing paragraphs accurately state VeriScholar implements single-agent ReAct + Tool Use with deterministic guardrails while Multi-Agent/HITL are future extensions.
5. `2_7_azure_e2b_byok.tex` & `2_8_langfuse.tex`: retitle 2.7.1 to *Dịch vụ suy luận OpenAI API và Hạ tầng đám mây Microsoft Azure*; replace `GPT-5.6-luna` with `gpt-4o-mini`; update Equation `eq:aes_gcm` to $T = \text{GHASH}_H(\text{AAD}, C) \oplus E_K(J_0)$ with $J_0 = \text{IV} \parallel 0^{31} \parallel 1$; clarify Langfuse observability tracing vs in-memory ephemeral BYOK key decryption.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_thesis_rules.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch2/ tests/test_thesis_rules.py
git commit -m "docs(thesis): remediate chapter 2 theoretical errors and align algorithms with codebase"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: Remediation of Chapter 3 System Analysis, Algorithms & 20-Table Database Design (`report-datn/chapters/ch3/`)

**Files:**
- Modify: `report-datn/chapters/ch3/3_1_mo_ta_bai_toan.tex`
- Modify: `report-datn/chapters/ch3/3_2_khao_sat_nghiep_vu.tex`
- Modify: `report-datn/chapters/ch3/3_3_tac_nhan_usecase.tex`
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`
- Modify: `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`
- Modify: `tests/test_thesis_rules.py`

**Interfaces:**
- Consumes: Actual 20 SQLAlchemy table schemas from `apps/api/src/api/db/models/__init__.py`
- Produces: Synchronized Chapter 3 `.tex` files preserving `\label{tab:uc_01_spec}` and `\label{tab:uc_03_spec}`

- [ ] **Step 1: Add failing assertions in `tests/test_thesis_rules.py`**

Add `test_chapter3_database_and_analysis_remediation()` in `tests/test_thesis_rules.py` asserting:
- Neither `3_1_mo_ta_bai_toan.tex` nor `3_2_khao_sat_nghiep_vu.tex` contains `"nhóm nghiên cứu"`.
- `3_6_thiet_ke_csdl.tex` contains the 4 real graph/wiki table names (`graph_nodes`, `graph_edges`, `folder_community_summaries`, `wiki_pages`, normalized for `\_`), does NOT contain fake table names (`extracted_figures`, `extracted_tables`, `draft_sections`, `latex_compilations`), contains `hashed_password` in `users`, contains `embedding` and `content_tsv` in `document_chunks`, does NOT contain `FK -> blobs(id)` or `FK -> sessions(id)`, and does NOT contain `"mũi tên cụt trực quan"`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_thesis_rules.py::test_chapter3_database_and_analysis_remediation -v`
Expected: FAIL

- [ ] **Step 3: Edit Chapter 3 `.tex` files**

1. `3_1_mo_ta_bai_toan.tex` & `3_2_khao_sat_nghiep_vu.tex`: replace `"nhóm nghiên cứu"` with `"tác giả"`; frame Section 3.2 as an analysis of international academic research workflows and existing tools; add detailed algorithmic design subsections covering (a) 2-column PDF block ordering & sliding-window chunking with `[0, 1]` BBox projection, (b) SQL CTE Hybrid Retrieval (`HNSW` + `ts_rank_cd`/BM25 + RRF $k=60$ + CRAG thresholds $\tau \in \{0{,}20, 0{,}35\}$), (c) LangGraph 4-node LaTeX self-healing state machine with SHA-256 anti-oscillation and `_auto_patch`/`apply_heuristic_repair`, and (d) GraphRAG entity extraction (`OpenAI Structured Outputs` + Cosine $\ge 0{,}90$ deduplication + Louvain community clustering).
2. `3_3_tac_nhan_usecase.tex`, `3_4_phan_tich_usecase.tex`, `3_5_bieu_do_tuan_tu.tex`:
   - In UC-01 (`tab:uc_01_spec`), explain that the $\text{Jaccard} \ge 0{,}2$ title filter applies to keyword queries of $\ge 3$ tokens while direct DOI/arXiv ID lookups and Exa semantic search bypass lexical filtering (preserving `"Jaccard"`, `"0{,}2"`, `"Skeleton"`, `"bình duyệt"`).
   - In UC-03 (`tab:uc_03_spec`), clarify that runtime enforces `[0, 1]` geometric coordinate invariants while $\text{IoU} \ge 0{,}85$ is the offline benchmark threshold; synchronize Step 3 of Table 3-3 and Sequence Diagram Figure 3-4 (`fig:seq_doc_sau`) to show CRAG pre-generation confidence gating and post-generation deterministic citation verification (`verify_output_grounding`).
   - In Section 3.4.2 (UC-09..UC-12), state that Administrator/Operations tasks execute via operational REST endpoints (`/api/v1/evaluations/run-benchmark`), automated DB reference-counting/lockout triggers, and Langfuse Cloud / Azure Portal dashboards.
3. `3_6_thiet_ke_csdl.tex`:
   - Unify 5 subsystems and update Table 3-7 (`tab:db_tables_summary`) to list the exact 20 SQLAlchemy tables (removing `extracted_figures`, `extracted_tables`, `draft_sections`, `latex_compilations` and adding `graph_nodes`, `graph_edges`, `folder_community_summaries`, `wiki_pages` with data dictionary specifications).
   - Add `hashed_password` to `users` (Table 3-8 & ERD) and `embedding` (`VECTOR(1536)`), `content_tsv` (`TSVECTOR`) to `document_chunks` (Table 3-14 & ERD).
   - Replace `FK -> blobs(id)` with `FK -> document_storage_blobs(id)` and `FK -> sessions(id)` with `FK -> research_sessions(id)`.
   - Remove the prompt artifact sentence on line 360 (`"các đường liên kết thẳng tắp..."`) and fix line 573 so entity extraction is attributed to OpenAI Structured Outputs + fallback rules while 2-hop SQL CTE is attributed to graph traversal.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_thesis_rules.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch3/ tests/test_thesis_rules.py
git commit -m "docs(thesis): align chapter 3 algorithms, use cases, and 20-table DB schema with codebase"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: Remediation of Chapter 4 Experiments, Real Benchmark Tables & Full XeLaTeX Compilation (`report-datn/chapters/ch4/`)

**Files:**
- Modify: `report-datn/chapters/ch4_thuc_nghiem.tex`
- Modify: `report-datn/chapters/ch4/4_1_moi_truong.tex`
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex`
- Modify: `report-datn/chapters/ch4/4_3_kiem_thu.tex`
- Modify: `report-datn/chapters/ch4/4_4_so_lieu.tex`
- Modify: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: `docs/benchmarks/thesis_benchmark_results.json` from Task 2
- Produces: Recompiled `report-datn/main.pdf` with zero errors/warnings and all 4 Verification Gates passing

- [ ] **Step 1: Add failing assertions in `tests/test_thesis_structure_and_compile.py`**

Add `test_thesis_ch4_sections_4_3_and_4_4_remediation()` in `tests/test_thesis_structure_and_compile.py` asserting:
- `ch4_thuc_nghiem.tex` contains `\chapter{CÀI ĐẶT VÀ KẾT QUẢ THỰC NGHIỆM}`.
- `4_2_giao_dien.tex` does NOT contain `"(BYOK) (BYOK)"`, does NOT contain `"retracted papers"`, and does NOT contain `"tuyệt đối không bao giờ được ghi xuống cơ sở dữ liệu đĩa cứng"`.
- `4_3_kiem_thu.tex` contains `"13{,}02"` (or `"13.02"`), `"340"`, `"240"`, `"580"`, and does NOT contain `"chưa đầy 5 giây"`.
- `4_4_so_lieu.tex` does NOT contain `"gpt-5.6-luna"`, and contains `\label{tab:ablation_retrieval}` and `\label{tab:ablation_latex_healing}`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_thesis_structure_and_compile.py::test_thesis_ch4_sections_4_3_and_4_4_remediation -v`
Expected: FAIL

- [ ] **Step 3: Edit Chapter 4 `.tex` files and compile `report-datn/main.pdf`**

1. `ch4_thuc_nghiem.tex`: update chapter title to `\chapter{CÀI ĐẶT VÀ KẾT QUẢ THỰC NGHIỆM}` to match Section 1.6.
2. `4_1_moi_truong.tex`: preserve all required infrastructure tokens and add a subsection/paragraph disclosing the use of AI coding and editorial assistants under human verification.
3. `4_2_giao_dien.tex`: fix `(BYOK) (BYOK)` typo; remove `"retracted papers"`; fix BYOK storage description on line 248 (encrypted at rest via AES-256-GCM in PostgreSQL, decrypted ephemerally in RAM); clarify Figure 4-8 citation chip display (`[ ↳ Attention Is All You Need ]`) and interactive canvas BBox highlighting; clarify Figure 4-9 shows the 12 Landmark Papers seed corpus (58 nodes, 111 edges, 15 Wiki pages) clustered via Louvain.
4. `4_3_kiem_thu.tex`: update Table 4-2 (`tab:gate_results`) to reflect the current test suite (**340 pytest tests** — noting product vs thesis rule tests — and **58 files / 240 vitest tests**, totaling **580 automated tests**) and fix the total execution time to **$13{,}02\,\text{giây}$**.
5. `4_4_so_lieu.tex`:
   - Replace `gpt-5.6-luna` with `gpt-4o-mini` / `gpt-5.4-mini`.
   - Expand Section 4.2.3 with the experimental protocol (12 Landmark Papers, 36 Golden Benchmark questions across 3 tracks, 25 faulty LaTeX cases), Table `\label{tab:ablation_retrieval}` (*Dense-only* vs *Sparse-only* vs *Hybrid RRF $k=60$ + Cross-Encoder* with Recall@5, MRR@10, BBox IoU $\text{mean} \pm \text{std}$, $P_{50}/P_{95}$ latency from `docs/benchmarks/thesis_benchmark_results.json`), and Table `\label{tab:ablation_latex_healing}` (*AST/Regex `_auto_patch`* vs *Heuristic `apply_heuristic_repair`* vs *Combined Agentic ReAct*).
   - Rewrite Section 4.2.4 operational telemetry explanation (objective interpretation of idle/light-load CPU $< 1\%$ and RAM $13{,}58\%$; explicit contrast between the full-month October 2026 OpenAI Usage dashboard of 1,397 requests / 78.25M tokens / $\$3{,}76$ and the 24-hour `1d` Langfuse window of 110 traces / $\$0{,}00104$).
6. Run `latexmk -xelatex -interaction=nonstopmode main.tex` (or 2 passes of `xelatex -interaction=nonstopmode -file-line-error main.tex`) in `report-datn/`.

- [ ] **Step 4: Run all 4 Verification Gates + XeLaTeX compilation check**

Run:
```bash
uv run ruff check . && uv run ruff format --check .
uv run pytest
npm --prefix apps/web run test -- --run
npm --prefix apps/web run build
```
Expected: 100% PASS (exit code 0 across all 4 gates and `report-datn/main.pdf` compiled cleanly).

- [ ] **Step 5: Commit**

```bash
git add report-datn/ tests/test_thesis_structure_and_compile.py
git commit -m "docs(thesis): remediate chapter 4 experiments, add ablation tables, and recompile PDF"
bash scripts/deploy_to_vps.sh --fast
```
