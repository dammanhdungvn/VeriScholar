# VeriScholar PRD Modernization & Comprehensive Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synchronize and modernize VeriScholar's Product Requirements Documents (`PRD-00`, `PRD-04`, `PRD-05`, `PRD-06`) to incorporate the full 9-pain-point academic lifecycle, opt-in Socratic scaffolding, mathematical intuition and tensor grounding, the 4-entity scientific DNA with research gap extraction, and 4-class LaTeX error self-healing with simulated peer review.

**Architecture:** Documentation updates across `docs/PRD/` adhering to Hexagonal Architecture boundaries, Product-Grade Radical Minimalism (Rule 6), Relative Markdown Links (Rule 5), and Academic Purity (Rule 7).

**Tech Stack:** Markdown GFM, KaTeX, Mermaid diagrams.

**Spec:** [`docs/superpowers/specs/2026-10-29-prd-comprehensive-update-design.md`](../specs/2026-10-29-prd-comprehensive-update-design.md)

## Global Constraints

- **Relative Markdown Links Only (Rule 5):** Never use `file://` or absolute paths in markdown documents. All internal references must use relative links (e.g., `../specs/...`, `./...`).
- **Product-Grade Radical Minimalism (Rule 6):** Keep documentation crisp, high-signal, and free of fluff or developer jargon.
- **Academic Purity & Thesis Invariants (Rule 7 & 8):** Frame all architectural concepts as high-level scientific abstractions (Knowledge Transformation, Scaffolding, Topological Sorting) rather than mechanical CRUD.
- **The 4 Verification Gates (Rule 4):**
  1. `uv run ruff check . && uv run ruff format --check .`
  2. `uv run pytest`
  3. `npm --prefix apps/web run test`
  4. `npm --prefix apps/web run build`
- **In-Plan VPS Sync Protocol (Rule 9):** Run `bash scripts/deploy_to_vps.sh --fast || true` after every successful task commit.

---

### Task 1: Update `docs/PRD/00-overview-and-cleanup.md`

**Files:**
- Modify: `docs/PRD/00-overview-and-cleanup.md`

- [ ] **Step 1.1: Incorporate Modern Information Paradox & 9-Pain-Point Lifecycle**
  - Update Section 1.1 & 1.2 in `docs/PRD/00-overview-and-cleanup.md` to introduce the historical contrast (early research vs. modern AI information deluge).
  - Detail the 9 core quantifiable pain points: (1) Sốc ký hiệu & Rào cản trực giác toán học, (2) Bẫy học nhảy cóc $Bậc\ 1 \to 4$, (3) Mất tập trung khi tra cứu trích dẫn (15–23 phút Deep Flow), (4) Ảo giác số liệu bảng 2 cột (30%–40%), (5) Ảo tưởng năng lực (Illusion of Competence), (6) Hố sâu toán học sang code (Theory-to-Code gap), (7) Nghĩa địa PDF & 30–50h chép tay SOTA, (8) Đứt gãy Đọc $\to$ Viết & lỗi biên dịch LaTeX (6–10h), (9) Tê liệt tìm ý tưởng & điểm mù phản biện.
  - Update Section 1.3 (Before vs. After Value Matrix) and Section 4 (The 3 RAG Pillars & Knowledge Flywheel).

- [ ] **Step 1.2: Verify relative links and format**
  - Ensure all Markdown links use relative paths.

- [ ] **Step 1.3: Commit and VPS Sync**
  - Commit: `docs(prd): modernize PRD-00 with 9-pain-point lifecycle and information paradox`
  - Run: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 2: Update `docs/PRD/04-context-table-and-roadmap.md`

**Files:**
- Modify: `docs/PRD/04-context-table-and-roadmap.md`

- [ ] **Step 2.1: Modernize Socratic Scaffolding & Add Mathematical Intuition**
  - Update Section 1 and UC-ROAD-03 in `docs/PRD/04-context-table-and-roadmap.md`.
  - Replace authoritarian hint wording with opt-in, empathetic phrasing: `"💡 Bài báo bạn đang đọc thuộc Bậc 4 (Kiến trúc Transformer). Nếu bạn là người mới chưa có kiến thức vững vàng thì hãy tham khảo lộ trình dưới đây để hiểu bản chất của paper hơn nha:"`.
  - Add specifications for:
    1. **Mathematical Intuition Explainer:** Bóc tách trực giác hình học và bản chất biến số toán học.
    2. **Math-to-Tensor Grounding:** Ánh xạ công thức toán học sang kích thước Tensor `[batch, heads, seq, dim]` và đoạn code PyTorch 5 dòng tối thiểu.
    3. **Active Recall Probe:** Kiểm tra phản xạ hiểu bài chủ động để chống ảo tưởng năng lực.

- [ ] **Step 2.2: Verify Gherkin acceptance criteria**
  - Update Gherkin scenarios in Section 4 to validate opt-in hint rendering and mathematical grounding.

- [ ] **Step 2.3: Commit and VPS Sync**
  - Commit: `docs(prd): modernize PRD-04 with opt-in scaffolding and math-to-tensor grounding`
  - Run: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 3: Update `docs/PRD/05-favorite-library-and-graphrag.md`

**Files:**
- Modify: `docs/PRD/05-favorite-library-and-graphrag.md`

- [ ] **Step 3.1: Enrich 4-Entity DNA, Causal Lineage & Research Gap Extraction**
  - Update Section 1 of `docs/PRD/05-favorite-library-and-graphrag.md` explaining why `Paper`, `Method`, `Dataset`, `MetricResult` represent the immutable DNA of empirical scientific papers and why removing them destroys SOTA comparison.
  - Update UC-LIB-05 to cover **Phổ Hệ Nhân Quả (Causal Evolution Lineage)**: Explaining why previous methods failed, driving the creation of new levels ($Bậc\ 1 \to 4$).
  - Add **UC-LIB-06: Khai Phá Khoảng Trống Nghiên Cứu (Research Gap & Limitations Extractor)**: Scanning *Limitations & Future Work* across library papers to discover unsolved frontiers for new thesis topics.

- [ ] **Step 3.2: Verify Gherkin acceptance criteria**
  - Update Section 4 with Gherkin acceptance criteria for research gap extraction and causal lineage.

- [ ] **Step 3.3: Commit and VPS Sync**
  - Commit: `docs(prd): enrich PRD-05 with 4-entity DNA and research gap extraction`
  - Run: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 4: Update `docs/PRD/06-agentic-overleaf-writing.md`

**Files:**
- Modify: `docs/PRD/06-agentic-overleaf-writing.md`

- [x] **Step 4.1: Expand 4 LaTeX Error Classes & Add Simulated Peer Reviewer**
  - Update Section 1 and UC-WRITE-04 in `docs/PRD/06-agentic-overleaf-writing.md` to document the 4 real-world LaTeX error classes:
    1. `ERR_SPECIAL_CHAR` (unescaped `&`, `%`, `_`, `#`).
    2. `ERR_MISSING_PACKAGE` (missing packages like `amsmath`, `amssymb`).
    3. `ERR_TABLE_ALIGNMENT` (column count mismatch in `tabular`).
    4. `ERR_SYNTAX_BRACKET` (bracket/environment delimiters).
  - Add **UC-WRITE-06: Giả Lập Phản Biện Hội Đồng (Simulated Peer Reviewer - "Reviewer #2")**: Auditing manuscripts for unsupported claims, missing baseline comparisons, and missing statistical p-values.

- [x] **Step 4.2: Verify Gherkin acceptance criteria**
  - Update Section 4 with Gherkin scenarios for the 4 error classes and peer reviewer simulation.

- [x] **Step 4.3: Commit and VPS Sync**
  - Commit: `docs(prd): update PRD-06 with 4 latex error classes and simulated peer reviewer`
  - Run: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 5: Whole-Branch Verification & Documentation Consistency

**Files:**
- Verify: All files in `docs/PRD/` and `docs/specs/`

- [x] **Step 5.1: Run 4 Verification Gates**
  - `uv run ruff check . && uv run ruff format --check .`
  - `uv run pytest`
  - `npm --prefix apps/web run test`
  - `npm --prefix apps/web run build`

- [x] **Step 5.2: Final Commit and VPS Sync**
  - Commit: `docs: complete PRD modernization and architectural alignment`
  - Run: `bash scripts/deploy_to_vps.sh --fast || true`
