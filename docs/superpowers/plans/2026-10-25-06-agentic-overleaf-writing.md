# Agentic Overleaf 3-Column Writing Workspace, LangGraph ReAct Co-Author & CLSI Sandbox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa Không Gian Soạn Thảo Học Thuật 3 Cột kiểu Overleaf (`/writing`), Cầu nối Đọc-sang-Viết khởi tạo Khung sườn LaTeX/BibTeX hợp lệ tức thì, Đồng tác giả AI tự trị dùng LangGraph ReAct (4 công cụ chuyên biệt + vòng lặp tự vá lỗi biên dịch tối đa 3 lần với bộ nhớ chống dao động SHA-256), Động cơ biên dịch `latexmk` chuẩn Overleaf CLSI với cờ `auxdir` bộ nhớ đệm tăng dần, điều hướng SyncTeX 2 chiều siêu tốc, cơ chế Hoàn tác 1-Click (`:undo`) và Xuất gói nộp bài `.zip` (`:export-bundle`).

**Architecture:** Tuân thủ nghiêm ngặt Kiến trúc Lục giác:
- `packages/core/`: Lõi miền nghiệp vụ thuần khiết Python Standard Library + `pydantic`. Chứa bộ sinh Khung sườn Học thuật `generate_academic_skeleton()`, bộ kiểm tra an toàn tên tệp chống Zip Slip `sanitize_and_validate_asset_filename()`, và Bộ Bóc Tách Nhật Ký Có Cấu Trúc `LatexLogParser` trích xuất danh sách `LatexDiagnostic` từ `output.log`. Tuyệt đối không import LangGraph hay I/O framework.
- `apps/api/`: Quản lý OCC (`version` / `412 Precondition Failed`), chụp ảnh toàn dự án `previous_snapshot` đúng 1 lần trước Attempt 1, điều phối LangGraph ReAct StateGraph tại `apps/api/src/api/agents/latex_agent.py`, động cơ biên dịch `latexmk` chuẩn Overleaf CLSI trong E2B Sandbox MicroVM (`timeout = 15s`, cờ `auxdir` kèm lưu trữ `cache.tar.gz`), điều hướng SyncTeX cục bộ trên host server ($< 20$ms), và phát luồng SSE không bộ đệm qua `POST /api/v1/drafts/{id}/chat:stream`.
- `apps/web/`: Cung cấp giao diện 3 cột (`WritingSidebar` + `MonacoEditor`, `WritingPreviewPane` với SyncTeX highlight, và `WritingAssistantPane` với streaming badges và nút `[↩️ Hoàn tác]`).

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 Async, LangGraph, E2B Sandbox SDK (`latexmk`, `xelatex`, `pdflatex`, TeX Live), React 19, TypeScript, Monaco Editor, PDF.js, Tailwind CSS.

**Spec:** [`docs/specs/06-agentic-overleaf-writing-spec.md`](../../specs/06-agentic-overleaf-writing-spec.md) & [`docs/PRD/06-agentic-overleaf-writing.md`](../../PRD/06-agentic-overleaf-writing.md).

---

## Global Constraints

- **Xóa bỏ vĩnh viễn** hàm tạo PDF giả lập bằng PyMuPDF `_generate_in_memory_pdf_preview()` trong `packages/core/src/core/services/latex_compiler.py`. Toàn bộ quá trình biên dịch PDF thực thi qua động cơ `latexmk` chuẩn Overleaf CLSI trên E2B Sandbox hoặc binary `tectonic` thật.
- `packages/core/` chỉ sử dụng Python Standard Library và `pydantic`. Agent LangGraph và các I/O adapters bắt buộc đặt trong `apps/api/src/api/agents/`.
- Vòng lặp tự động sửa lỗi cú pháp của LangGraph ReAct Agent bị giới hạn cứng ở mức tối đa **3 lần thử (`MAX_COMPILE_ATTEMPTS = 3`)** kèm bộ nhớ chống dao động lặp (`Anti-Oscillation Guard` kiểm tra mã băm SHA-256).
- Trước khi Agent thực hiện chỉnh sửa đầu tiên (Attempt 1), hệ thống bắt buộc chụp lại `previous_snapshot = {"content": ..., "bib_content": ..., "version": ...}` đúng 1 lần duy nhất để nút **`[↩️ Hoàn tác]`** (`POST /api/v1/drafts/{id}:undo`) khôi phục chính xác 100% trạng thái ban đầu của tác giả.
- Mọi cập nhật bản thảo (`PATCH /api/v1/drafts/{id}`) bắt buộc kiểm tra khóa đồng thời lạc quan (OCC `version`); nếu lệch phiên bản phải trả về `HTTP 412 PRECONDITION_FAILED` với mã `DRAFT_CONCURRENCY_CONFLICT`.
- Tên tệp ảnh tải lên thư mục `figures/` (`draft_assets`) bắt buộc lọc qua biểu thức `^[a-zA-Z0-9_\-\.]+$` để chặn đứng tấn công Path Traversal / Zip Slip (`<= 10MB/file`, tổng `<= 50MB/draft`).
- Endpoint xuất gói nộp bài (`POST /api/v1/drafts/{id}:export-bundle`) không bao giờ chặn quyền tải mã nguồn của học giả ngay cả khi bản thảo đang còn lỗi biên dịch (xuất đầy đủ `main.tex`, `references.bib`, `figures/` và `README.txt` ghi chú dòng lỗi).
- Bốn Cổng Xác Minh Bắt Buộc (`ruff`, `pytest`, `npm test`, `npm build`) phải đạt exit code 0 sau mỗi task.
- Chạy `bash scripts/deploy_to_vps.sh --fast` sau mỗi lần git commit thành công.

---

## Review Focus

1. **BibTeX Special Character Escaping in Reading-to-Writing Bridge:** Khi khởi tạo bản thảo từ phiên đọc chứa các bài báo có ký tự đặc biệt trong tiêu đề hoặc tên tác giả (`&`, `%`, `_`, `#`, dấu ngoặc nhọn), bộ sinh khung sườn phải escape hợp lệ để bản biên dịch đầu tiên thành công 100% trong `< 2s` mà không bị lỗi cú pháp BibTeX.
2. **Single Composite Snapshot Before Multi-Step Self-Healing:** Nếu Agent sửa code 3 lần liên tiếp trong vòng lặp tự vá lỗi (Attempt 1 $\rightarrow$ Attempt 2 $\rightarrow$ Attempt 3), `previous_snapshot` chỉ được ghi ở đầu Attempt 1 (tuyệt đối không ghi đè ở Attempt 2 hay 3), để khi người dùng bấm `[↩️ Hoàn tác]`, cả `main.tex` và `references.bib` quay về nguyên trạng trước khi gọi AI.
3. **Anti-Oscillation Guard in Self-Healing Loop:** Nếu bản vá lỗi của Agent tạo ra mã nguồn có mã băm SHA-256 trùng với một lần thử đã thất bại trước đó trong cùng lượt gọi, vòng lặp phải dừng ngay thay vì lặp lại vô ích.
4. **Fast Local SyncTeX Execution (< 20ms):** Thao tác click PDF hoặc Monaco Editor tuyệt đối không tạo container E2B mới; SyncTeX phải đọc trực tiếp file `output.synctex.gz` đã lưu cục bộ trên host server qua binary `/usr/bin/synctex`.
5. **Incremental Cache Persistence:** Thư mục đệm gia tăng `/tmp/drafts/{id}/cache/` được nén `cache.tar.gz` lưu trữ an toàn, đảm bảo lần biên dịch sau đạt tốc độ $< 1.5$s ngay cả khi E2B sandbox được làm mới.

---

## Implementation Tasks

### Task 1: Structured LaTeX Log Parser, Academic Skeleton Generator & Asset Security Guard (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/latex_log_parser.py`
- Create: `packages/core/src/core/services/draft_skeleton.py`
- Modify: `packages/core/src/core/services/latex_compiler.py`
- Test: `packages/core/tests/test_draft_skeleton_and_log_parser.py`

**Interfaces:**
- Consumes: Python Standard Library (`re`, `hashlib`, `dataclasses`, `typing.Literal`, `pydantic`).
- Produces:
  - `LatexDiagnostic` TypedDict / Pydantic Model (`file`, `line`, `column`, `severity`, `message`, `context`, `hint`).
  - `LatexLogParser.parse_log(raw_log: str) -> list[LatexDiagnostic]`: Bóc tách nhật ký biên dịch thành danh sách lỗi/cảnh báo có cấu trúc.
  - `generate_academic_skeleton(title: str, papers: list[dict], notes: list[dict]) -> tuple[str, str]`: Trả về `(main_tex, references_bib)` với ký tự đặc biệt đã được escape tất định.
  - `sanitize_and_validate_asset_filename(filename: str, byte_size: int) -> str`: Chặn Path Traversal / Zip Slip (`^[a-zA-Z0-9_\-\.]+$`).

- [x] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_draft_skeleton_and_log_parser.py`:
```python
import pytest
from core.services.latex_log_parser import LatexLogParser
from core.services.draft_skeleton import (
    generate_academic_skeleton,
    sanitize_and_validate_asset_filename,
)


def test_parse_latex_log_extracts_structured_diagnostics():
    sample_log = """
! Undefined control sequence.
l.42 \invalidcommand
                    {test}
The control sequence at the end of the top line
"""
    diagnostics = LatexLogParser.parse_log(sample_log)
    assert len(diagnostics) >= 1
    assert diagnostics[0]["line"] == 42
    assert diagnostics[0]["severity"] == "error"
    assert "Undefined control sequence" in diagnostics[0]["message"]


def test_skeleton_generator_escapes_bibtex_special_characters():
    papers = [{"title": "Deep Learning & Transformers: A 50% Speedup", "authors": ["Vaswani, A."], "year": 2017, "citation_key": "vaswani2017"}]
    main_tex, bib_content = generate_academic_skeleton("Test Project", papers, [])
    assert r"\&" in bib_content
    assert r"\%" in bib_content
    assert r"\cite{vaswani2017}" in main_tex


def test_sanitize_asset_filename_rejects_path_traversal():
    with pytest.raises(ValueError):
        sanitize_and_validate_asset_filename("../../evil.png", 1024)
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_draft_skeleton_and_log_parser.py -v`
Expected: FAIL

- [x] **Step 3: Implement `latex_log_parser.py` & `draft_skeleton.py`**

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_draft_skeleton_and_log_parser.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add packages/core/src/core/services/latex_log_parser.py packages/core/src/core/services/draft_skeleton.py packages/core/src/core/services/latex_compiler.py packages/core/tests/test_draft_skeleton_and_log_parser.py
git commit -m "feat(core): add structured LaTeX log parser, skeleton generator, and asset zip-slip guard"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Database Schema & SQLAlchemy Models (`drafts`, `draft_assets`, `draft_messages`) (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/db/models/draft.py`
- Create: `apps/api/src/api/db/models/draft_asset.py`
- Create: `apps/api/src/api/db/models/draft_message.py`
- Modify: `apps/api/src/api/db/session.py`
- Test: `apps/api/tests/test_draft_models.py`

**Interfaces:**
- Consumes: SQLAlchemy 2.0 Async, PostgreSQL JSONB.
- Produces:
  - `DraftModel` bổ sung: `bib_content`, `source_session_id`, `pdf_preview_storage_path`, `previous_snapshot`.
  - `DraftAssetModel`: Quản lý hình ảnh trong thư mục `figures/` trỏ tới CAS storage.
  - `DraftMessageModel`: Lưu lịch sử chat, tool calls và nhật ký biên dịch của LangGraph Agent.

- [x] **Step 1: Write the failing test**

Cập nhật `apps/api/tests/test_draft_models.py` kiểm tra khởi tạo `DraftModel` có `previous_snapshot` JSONB, `DraftAssetModel`, và `DraftMessageModel`.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_draft_models.py -v`
Expected: FAIL

- [x] **Step 3: Implement models & DDL in `session.py`**

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_draft_models.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/db/models/draft.py apps/api/src/api/db/models/draft_asset.py apps/api/src/api/db/models/draft_message.py apps/api/src/api/db/session.py apps/api/tests/test_draft_models.py
git commit -m "feat(api): add draft assets, draft messages, and composite previous snapshot models"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Overleaf CLSI `latexmk` Orchestrator, Incremental Cache Archive & Local SyncTeX Runner (`apps/api`)

**Files:**
- Create: `apps/api/src/api/services/clsi_latex_compiler.py`
- Test: `apps/api/tests/test_clsi_latex_compiler.py`

**Interfaces:**
- Consumes: E2B Sandbox SDK, `LatexLogParser`, `subprocess`.
- Produces:
  - `CLSILatexCompiler.compile(draft_id: UUID, main_tex: str, bib_content: str, assets: list[dict], clear_cache: bool = False)`:
    - Nhận diện engine tự động: chứa `\usepackage{fontspec}` $\rightarrow$ `-xelatex`, ngược lại `-pdf`.
    - Chạy lệnh `latexmk -cd -f -jobname=output -auxdir=/tmp/drafts/{id}/cache -outdir=/tmp/drafts/{id}/output -synctex=1 -interaction=batchmode {engine} main.tex`.
    - Quản lý nén/giải nén `cache.tar.gz` bảo toàn đệm gia tăng ($< 1.5$s cho lần dựng thứ hai).
    - Tải `output.pdf` và `output.synctex.gz` về server host.
  - `CLSILatexCompiler.synctex_forward(draft_id: UUID, file: str, line: int, column: int)`: Gọi `/usr/bin/synctex` cục bộ trả về `(page, h, v, width, height)` trong $< 20$ms.
  - `CLSILatexCompiler.synctex_inverse(draft_id: UUID, page: int, x: float, y: float)`: Gọi `/usr/bin/synctex` cục bộ trả về `(file, line, column)` trong $< 20$ms.

- [x] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_clsi_latex_compiler.py` kiểm thử nhận diện động cơ (`fontspec` $\rightarrow$ `-xelatex`), bóc tách log lỗi và giả lập gọi SyncTeX cục bộ.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_clsi_latex_compiler.py -v`
Expected: FAIL

- [x] **Step 3: Implement `apps/api/src/api/services/clsi_latex_compiler.py`**

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_clsi_latex_compiler.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/services/clsi_latex_compiler.py apps/api/tests/test_clsi_latex_compiler.py
git commit -m "feat(api): implement Overleaf CLSI latexmk compiler, incremental cache archive, and local synctex runner"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: LangGraph ReAct Co-Author Agent (`latex_agent.py`) with 4 Tools & Anti-Oscillation Memory (`apps/api`)

**Files:**
- Create: `apps/api/src/api/agents/latex_agent.py`
- Test: `apps/api/tests/test_latex_agent_react.py`

**Interfaces:**
- Consumes: `langgraph`, `langchain_core`, `CLSILatexCompiler`, `GraphRAGService`, `LatexLogParser`.
- Produces:
  - `build_latex_coauthor_graph()`: StateGraph ReAct với 4 Tools:
    1. `edit_latex_files(target_file, content)`
    2. `list_project_files()` (liệt kê `main.tex`, `references.bib`, và ảnh trong `figures/`)
    3. `query_library_graph_rag(query, top_k)`
    4. `compile_latex_e2b(clear_cache)`
  - Vòng lặp tự vá lỗi tối đa 3 lần (`MAX_COMPILE_ATTEMPTS = 3`).
  - `Anti-Oscillation Guard`: Tính SHA-256 mã nguồn qua từng lượt thử; nếu phát hiện mã băm trùng lặp thì lập tức dừng vòng lặp an toàn và phát cảnh báo.

- [x] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_latex_agent_react.py`.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_latex_agent_react.py -v`
Expected: FAIL

- [x] **Step 3: Implement `apps/api/src/api/agents/latex_agent.py`**

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_latex_agent_react.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/agents/latex_agent.py apps/api/tests/test_latex_agent_react.py
git commit -m "feat(api): implement LangGraph ReAct LaTeX co-author agent with anti-oscillation guard"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: REST Endpoints, Unbuffered SSE Streaming & Export Bundle (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/v1/endpoints/drafts.py`
- Modify: `apps/api/src/api/services/draft_service.py`
- Test: `apps/api/tests/test_drafts_endpoints.py`

**Interfaces:**
- Endpoints:
  - `POST /api/v1/drafts`: Khởi tạo từ `source_session_id` với skeleton chuẩn.
  - `POST /api/v1/drafts/{id}/chat:stream` (kèm route alias `/assist`): Phát luồng SSE unbuffered cho UI.
  - `POST /api/v1/drafts/{id}:undo`: Khôi phục `previous_snapshot` (cả `main.tex` và `references.bib`).
  - `POST /api/v1/drafts/{id}/compile`: Biên dịch đơn lẻ qua E2B.
  - `POST /api/v1/drafts/{id}/compile:clear-cache`: Xóa đệm `/tmp/drafts/{id}/cache/` và dựng lại sạch.
  - `POST /api/v1/drafts/{id}/synctex:forward` & `POST /api/v1/drafts/{id}/synctex:inverse`
  - `POST /api/v1/drafts/{id}:export-bundle`: Xuất file `.zip` Camera-Ready chuẩn nộp bài.

- [x] **Step 1: Write the failing test**

Cập nhật `apps/api/tests/test_drafts_endpoints.py`.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_drafts_endpoints.py -v`
Expected: FAIL

- [x] **Step 3: Implement endpoints in `drafts.py` and service methods in `draft_service.py`**

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_drafts_endpoints.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/v1/endpoints/drafts.py apps/api/src/api/services/draft_service.py apps/api/tests/test_drafts_endpoints.py
git commit -m "feat(api): implement draft chat stream, synctex, clear-cache, undo, and export-bundle endpoints"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: Frontend 3-Column Writing Workspace, Monaco Editor, PDF SyncTeX Jump & Assistant Chat (`apps/web`)

**Files:**
- Modify: `apps/web/src/features/writing/components/WritingWorkspace.tsx`
- Modify: `apps/web/src/features/writing/components/WritingEditorPane.tsx`
- Modify: `apps/web/src/features/writing/components/WritingPreviewPane.tsx`
- Modify: `apps/web/src/features/writing/components/WritingAssistantPane.tsx`
- Test: `apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx`

**Interfaces:**
- Consumes: `POST /api/v1/drafts/{id}/chat:stream`, `POST /api/v1/drafts/{id}/synctex:forward`, `POST /api/v1/drafts/{id}/synctex:inverse`, `POST :undo`, `POST :compile:clear-cache`.
- Produces:
  - Cột 1 (Trái): Cây file (`main.tex`, `references.bib`, thư mục ảnh `figures/`) và Monaco Editor có gắn OCC version check.
  - Cột 2 (Giữa): Trình xem PDF Canvas hỗ trợ highlight vàng khi nhận kết quả Forward Search và gửi tọa độ `(x, y)` khi nhấp đúp để Inverse Search. Nút `[🧹 Xóa đệm & Dựng lại]`.
  - Cột 3 (Phải): Khung trò chuyện trợ lý AI hiển thị execution badges theo thời gian thực (*🔍 Tra cứu GraphRAG* $\rightarrow$ *✍️ Cập nhật mã nguồn* $\rightarrow$ *⚙️ Biên dịch E2B*), kèm nút `[↩️ Hoàn tác]` trên thanh công cụ.

- [x] **Step 1: Write the failing test**

Tạo `apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx`.

- [x] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- WritingWorkspace`
Expected: FAIL

- [x] **Step 3: Implement components in `apps/web/src/features/writing/components/`**

- [x] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- WritingWorkspace`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/web/src/features/writing/
git commit -m "feat(web): build 3-column Overleaf-parity writing workspace with Monaco editor and SyncTeX two-way navigation"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 7: End-to-End Verification, 4 Mandatory Verification Gates & Rollout

- [x] **Step 1: Run Gate 1 (Python Linter & Formatter)**
  Run: `uv run ruff check . && uv run ruff format --check .`
  Expected: exit code 0

- [x] **Step 2: Run Gate 2 (Backend & Architecture Boundary Tests)**
  Run: `uv run pytest`
  Expected: exit code 0 (146+ tests passed)

- [x] **Step 3: Run Gate 3 (Frontend Unit Tests)**
  Run: `npm --prefix apps/web run test`
  Expected: exit code 0 (84+ tests passed)

- [x] **Step 4: Run Gate 4 (Production Build)**
  Run: `npm --prefix apps/web run build`
  Expected: exit code 0

- [x] **Step 5: Remote VPS Deployment Sync**
  Run: `bash scripts/deploy_to_vps.sh --fast`
  Expected: exit code 0
