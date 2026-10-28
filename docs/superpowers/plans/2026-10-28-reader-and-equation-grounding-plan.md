# Reader UX Polish & Equation Grounding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve 5 critical reader UI/UX bugs (section fallback, scroll-snap trap, citation overflow, horizontal zoom scroll, premature streaming footer) and add equation-aware retrieval and visual grounding for mathematical formulas.

**Architecture:** 
1. Backend enhances `session_chat_service.py` with section/typo normalizer, math entity/equation intent extraction, symbolic matching boost in hybrid search, and equation LaTeX prompt formatting.
2. Frontend updates `PdfCanvasViewer.tsx` to remove scroll-snap traps, add dismissable bounding boxes (`Esc`, toggle click, `[✕]`), and enable `overflow-x-auto` for zoom > 100%.
3. Frontend updates `AcademicMarkdownRenderer.tsx` to gate the citation footer until streaming finishes (`!isStreaming`) and filter citation lists to only explicitly referenced citations (capped at Top 5).

**Tech Stack:** FastAPI, SQLAlchemy 2.0 Async, PyMuPDF, React 19, Tailwind CSS, Vite, Vitest, Pytest.

**Spec:** `docs/superpowers/specs/2026-10-28-reader-and-equation-grounding-design.md`

## Global Constraints
- Hexagonal Architecture: `packages/core/` remains pure domain; all DB and HTTP logic in `apps/api/` and `apps/web/`.
- Radical Minimalism 80/20: UI copy must be clean, concise, no hex codes, no engineering jargon.
- TDD Mandatory: Write failing test first, make it green, refactor, commit.
- 100% exit code 0 on all 4 Verification Gates before declaring completion.
- Run `bash scripts/deploy_to_vps.sh --fast` after each commit.

## Review Focus
1. Typo in section queries like "1. Instruction" or "Mục 1" must cleanly resolve to Introduction without falling back to Socratic refusal.
2. Math formula queries like "Công thức A(H)" or "Lấy công thức Attendsion" must retrieve the exact equation chunk (Eq. 3 or Eq. 8) and highlight the equation rather than adjacent paragraphs.
3. User scrolling on PDF viewer while a bounding box is active must never get forcefully snapped back to the page containing the bounding box.
4. Active bounding box must be dismissable by re-clicking the citation badge or pressing `Escape`.
5. Citation footer must never appear while AI is streaming text tokens (`isStreaming === true`).

---

### Task 1: Backend Section & Equation-Aware Retrieval Booster

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:270-380`
- Create: `apps/api/tests/test_equation_aware_retrieval.py`
- Modify: `apps/api/tests/test_section_aware_retrieval.py`

**Interfaces:**
- Consumes: `_detect_target_section(query_text: str) -> str | None`, `_hybrid_search(...)`
- Produces: 
  - `_detect_formula_query(query_text: str) -> dict[str, Any] | None`
  - `_extract_formula_symbols(query_text: str) -> list[str]`
  - Enhanced `_detect_target_section` supporting "Introduction", "Mục X", and typo correction ("1. Instruction" $\rightarrow$ "introduction").

- [ ] **Step 1: Write the failing tests in `apps/api/tests/test_equation_aware_retrieval.py`**

```python
import pytest
from api.services.session_chat_service import (
    _detect_formula_query,
    _detect_target_section,
    _extract_formula_symbols,
)

def test_detect_target_section_handles_typo_and_numbered_sections():
    assert _detect_target_section("1. Instruction") == "introduction"
    assert _detect_target_section("Dịch mục 1. Instruction sang tiếng việt") == "introduction"
    assert _detect_target_section("Tóm tắt Mục 1") == "introduction"
    assert _detect_target_section("Phần 2 nói về gì") == "section_2"

def test_detect_formula_query_and_symbol_extraction():
    res = _detect_formula_query("Công thức A(H) trong paper có ý nghĩa gì")
    assert res is not None
    assert "A(H)" in res["symbols"] or "A" in res["symbols"]

    res_typo = _detect_formula_query("Lấy công thức Attendsion ra cho tôi")
    assert res_typo is not None
    assert "Attention" in res_typo["normalized_names"]

    res_eq = _detect_formula_query("Giải thích công thức (3) trong bài")
    assert res_eq is not None
    assert "(3)" in res_eq["equation_numbers"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_equation_aware_retrieval.py -v`  
Expected: FAIL (ImportError / functions not defined or assertions fail).

- [ ] **Step 3: Implement `_detect_formula_query`, `_extract_formula_symbols`, and enhance `_detect_target_section` in `session_chat_service.py`**

Add section aliases, typo mapping (`instruction` $\rightarrow$ `introduction`), and formula entity extraction (symbols, equation numbers, typo normalizer `attendsion` $\rightarrow$ `attention`). In `_hybrid_search`, when a formula query is detected, perform symbolic text matching on `document_chunks.content` and boost matching chunks to the top.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest apps/api/tests/test_equation_aware_retrieval.py apps/api/tests/test_section_aware_retrieval.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit & Deploy**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_equation_aware_retrieval.py apps/api/tests/test_section_aware_retrieval.py
git commit -m "feat(rag): add section typo normalizer and equation-aware retrieval boost"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Backend Evidence Cap & Socratic Equation Prompt Synthesis

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:1080-1160`
- Modify: `apps/api/tests/test_session_hybrid_rag_chat.py`

**Interfaces:**
- Consumes: `_hybrid_search`, `_synthesize_answer`
- Produces: Evidence chunk pool capped at Top 5 for focused queries, Socratic system prompt with equation KaTeX rules.

- [ ] **Step 1: Write test for Top 5 evidence cap and equation formatting rule**

In `apps/api/tests/test_equation_aware_retrieval.py`:
Verify that evidence chunks injected into context for single-section/equation queries do not exceed 5 items.

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest apps/api/tests/test_equation_aware_retrieval.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement evidence capping and prompt instructions in `session_chat_service.py`**

- Cap evidence chunks to max 5 in `_synthesize_answer`.
- Update Socratic instructions: When asked for a formula/equation, extract the exact mathematical notation in LaTeX `$$...$$`, explain the symbols, and add citation tag `[1]` matching the formula chunk.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest apps/api/tests/test_equation_aware_retrieval.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit & Deploy**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_equation_aware_retrieval.py
git commit -m "feat(rag): cap evidence chunks to 5 and add socratic equation formatting rules"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Frontend Anti-Snap Scroll Trap Elimination & Dismissable Bounding Box

**Files:**
- Modify: `apps/web/src/components/viewer/PdfCanvasViewer.tsx`
- Create: `apps/web/src/features/reader/__tests__/PdfCanvasViewerScrollTrap.test.tsx`

**Interfaces:**
- Consumes: `activeBbox` from `useReaderStore`
- Produces:
  - Scroll-to-bbox only on programmatic user action (citation badge click).
  - Dismiss bounding box on `Escape` key, toggle citation re-click, or click on dismiss button `[✕]`.

- [ ] **Step 1: Write test in `apps/web/src/features/reader/__tests__/PdfCanvasViewerScrollTrap.test.tsx`**

Test that:
- User scrolling across pages does not reset the programmatic scroll flag or snap back to the previous active bounding box.
- Pressing `Escape` calls `setActiveBbox(null)`.

- [ ] **Step 2: Run test to verify failure**

Run: `npm --prefix apps/web run test PdfCanvasViewerScrollTrap`  
Expected: FAIL.

- [ ] **Step 3: Implement anti-trap scroll and dismiss controls in `PdfCanvasViewer.tsx`**

- In `PdfCanvasViewer.tsx:231`: Remove `lastScrolledBboxKeyRef.current = null`.
- Add `lastScrolledCitationIdRef` so programmatic scroll only triggers when the user explicitly clicks a citation.
- Add `Escape` key listener on window to clear `activeBbox`.
- Render a small dismiss icon `[✕]` in the active bounding box overlay so the user can easily close it.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test PdfCanvasViewerScrollTrap`  
Expected: PASS.

- [ ] **Step 5: Commit & Deploy**

```bash
git add apps/web/src/components/viewer/PdfCanvasViewer.tsx apps/web/src/features/reader/__tests__/PdfCanvasViewerScrollTrap.test.tsx
git commit -m "fix(viewer): eliminate pdf scroll-snap trap and add dismissable bbox"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Frontend Zoom > 100% Horizontal Scroll & Stream-Gated Citation Footer

**Files:**
- Modify: `apps/web/src/components/viewer/PdfCanvasViewer.tsx:654`
- Modify: `apps/web/src/components/chat/AcademicMarkdownRenderer.tsx:180-210, 500-515`
- Modify: `apps/web/src/components/shared/__tests__/AcademicMarkdownRenderer.test.tsx`

**Interfaces:**
- Consumes: `isStreaming: boolean`, `citations: CitationSource[]`
- Produces:
  - Container with `overflow-x-auto` for smooth horizontal panning when `scale > 1.0`.
  - Citation footer rendered only when `!isStreaming && referenceList.length > 0`.
  - Deduplicated reference list capped at Top 5, only showing citations actually present in markdown text.

- [ ] **Step 1: Write test in `AcademicMarkdownRenderer.test.tsx`**

Verify that:
- When `isStreaming === true`, `citation-sources-footer` is NOT rendered in the DOM.
- When `isStreaming === false`, citations actually referenced (e.g. `[1]`) are rendered, and empty inline citations do not dump 23 chunks.

- [ ] **Step 2: Run test to verify failure**

Run: `npm --prefix apps/web run test AcademicMarkdownRenderer.test.tsx`  
Expected: FAIL.

- [ ] **Step 3: Implement zoom scroll fix and stream-gated citations in `PdfCanvasViewer.tsx` and `AcademicMarkdownRenderer.tsx`**

- Change `overflow-x-hidden` to `overflow-x-auto` in `PdfCanvasViewer.tsx`.
- In `AcademicMarkdownRenderer.tsx`: Check `!isStreaming && referenceList.length > 0`.
- In `referenceList` extraction: when `hasInlineTokens === false`, do NOT dump all candidate chunks. Only show explicitly referenced items, capped at 5 items.

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix apps/web run test AcademicMarkdownRenderer.test.tsx`  
Expected: PASS.

- [ ] **Step 5: Commit & Deploy**

```bash
git add apps/web/src/components/viewer/PdfCanvasViewer.tsx apps/web/src/components/chat/AcademicMarkdownRenderer.tsx apps/web/src/components/shared/__tests__/AcademicMarkdownRenderer.test.tsx
git commit -m "fix(reader): enable horizontal scroll on zoom and gate citation footer during streaming"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: End-to-End System Integration & 4 Verification Gates + VPS Deployment

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**

Run: `uv run ruff check . && uv run ruff format --check .`  
Expected: 0 errors.

- [ ] **Step 2: Gate 2 - Backend Pytest Suite**

Run: `uv run pytest`  
Expected: 100% pass (251+ tests).

- [ ] **Step 3: Gate 3 - Frontend Unit Tests**

Run: `npm --prefix apps/web run test`  
Expected: 100% pass (117+ tests).

- [ ] **Step 4: Gate 4 - Frontend Production Build**

Run: `npm --prefix apps/web run build`  
Expected: 0 errors, build succeeds.

- [ ] **Step 5: Final Production VPS Deployment & Live Verification**

Run: `bash scripts/deploy_to_vps.sh --fast`  
Expected: Exit code 0, deployed to `https://verischolar.duckdns.org`.
