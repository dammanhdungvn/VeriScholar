# Agentic Overleaf 3-Column Writing Workspace, LangGraph ReAct Co-Author & E2B Sandbox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa Không Gian Soạn Thảo Học Thuật 3 Cột kiểu Overleaf (`/writing`), Cầu nối Đọc-sang-Viết khởi tạo Khung sườn LaTeX/BibTeX hợp lệ tức thì, Đồng tác giả AI tự trị dùng LangGraph ReAct (4 công cụ chuyên biệt + vòng lặp tự vá lỗi biên dịch tối đa 3 lần trên E2B Cloud Sandbox), cơ chế Hoàn tác 1-Click (`:undo`) và Xuất gói nộp bài `.zip` (`:export-bundle`).

**Architecture:** Tuân thủ Kiến trúc Lục giác: Bộ sinh Khung sườn Học thuật (`main.tex` + `references.bib`), bộ kiểm tra an toàn tên tệp chống Zip Slip, và đồ thị trạng thái `LatexCoAuthorAgent` (4 tools: `edit_latex_files`, `list_project_files`, `query_library_graph_rag`, `compile_latex_e2b`) nằm trong `packages/core`; tầng `apps/api` quản lý OCC (`version` / `412 Precondition Failed`), chụp `previous_snapshot` đúng 1 lần trước Attempt 1, biên dịch cô lập trên E2B Firecracker MicroVM (`timeout = 15s`, `--no-shell-escape`), và phát luồng SSE không bộ đệm; tầng `apps/web` cung cấp giao diện 3 cột (`WritingSidebar` + `MonacoEditor`, `WritingPreviewPane`, `WritingAssistantPane`).

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 Async, LangGraph, E2B Sandbox SDK (`tectonic` / TeX Live), React 19, TypeScript, Monaco Editor, Tailwind CSS.

**Spec:** [`docs/specs/06-agentic-overleaf-writing-spec.md`](../../specs/06-agentic-overleaf-writing-spec.md) & [`docs/PRD/06-agentic-overleaf-writing.md`](../../PRD/06-agentic-overleaf-writing.md).

---

## Global Constraints

- **Xóa bỏ vĩnh viễn** hàm tạo PDF giả lập bằng PyMuPDF `_generate_in_memory_pdf_preview()` trong `packages/core/src/core/services/latex_compiler.py`. Toàn bộ quá trình biên dịch PDF bắt buộc thực thi qua **E2B Cloud Sandbox** (`timeout = 15s`, `--no-shell-escape`).
- Vòng lặp tự động sửa lỗi cú pháp của LangGraph ReAct Agent bị giới hạn cứng ở mức tối đa **3 lần thử (`MAX_COMPILE_ATTEMPTS = 3`)** kèm bộ nhớ chống dao động lặp (`Anti-Oscillation Memory`).
- Trước khi Agent thực hiện chỉnh sửa đầu tiên (Attempt 1), hệ thống bắt buộc chụp lại `previous_snapshot = {"content": ..., "bib_content": ..., "version": ...}` đúng 1 lần duy nhất để đảm bảo nút **`[↩️ Hoàn tác]`** (`POST /api/v1/drafts/{id}:undo`) luôn khôi phục chính xác trạng thái của tác giả trước khi AI can thiệp.
- Mọi cập nhật bản thảo (`PATCH /api/v1/drafts/{id}`) bắt buộc kiểm tra khóa đồng thời lạc quan (OCC `version`); nếu lệch phiên bản phải trả về `HTTP 412 PRECONDITION_FAILED` với mã `DRAFT_VERSION_CONFLICT`.
- Tên tệp ảnh tải lên thư mục `figures/` (`draft_assets`) bắt buộc lọc qua biểu thức `^[a-zA-Z0-9_\-\.]+$` để chặn đứng tấn công Path Traversal / Zip Slip (`<= 10MB/file`, tổng `<= 50MB/draft`).
- Endpoint xuất gói nộp bài (`POST /api/v1/drafts/{id}:export-bundle`) không bao giờ chặn quyền tải mã nguồn của học giả ngay cả khi bản thảo đang còn lỗi biên dịch (xuất đầy đủ `main.tex`, `references.bib`, `figures/` và `README.txt` ghi chú dòng lỗi).
- Bốn Cổng Xác Minh Bắt Buộc (`ruff`, `pytest`, `npm test`, `npm build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **BibTeX Special Character Escaping in Reading-to-Writing Bridge:** Khi khởi tạo bản thảo từ phiên đọc chứa các bài báo có ký tự đặc biệt trong tiêu đề hoặc tên tác giả (`&`, `%`, `_`, `#`, dấu ngoặc nhọn), bộ sinh khung sườn phải escape hợp lệ để bản biên dịch đầu tiên thành công 100% trong `< 2s` mà không bị lỗi cú pháp BibTeX.
2. **Single Snapshot Before Multi-Step Self-Healing:** Nếu Agent sửa code 3 lần liên tiếp trong vòng lặp tự vá lỗi (Attempt 1 $\rightarrow$ Attempt 2 $\rightarrow$ Attempt 3), `previous_snapshot` chỉ được ghi ở đầu Attempt 1 (tuyệt đối không ghi đè ở Attempt 2 hay 3), để khi người dùng bấm `[↩️ Hoàn tác]`, bản thảo quay về nguyên trạng trước khi gọi AI.
3. **Anti-Oscillation Guard in Self-Healing Loop:** Nếu bản vá lỗi của Agent tạo ra mã nguồn có mã băm SHA-256 trùng với một lần thử đã thất bại trước đó trong cùng lượt gọi, vòng lặp phải dừng ngay thay vì lặp lại vô ích.
4. **15-Second E2B Sandbox Timeout & Draft Mode Fallback:** Khi bản thảo chứa hình ảnh nặng hoặc vòng lặp macro khiến quá trình biên dịch trên E2B vượt quá 15 giây, tiến trình phải ngắt an toàn và trả về mã lỗi/trạng thái hướng dẫn rõ ràng thay vì treo kết nối SSE.
5. **Zip Slip & Malicious LaTeX Command Prevention:** Kiểm tra chặt chẽ tên file trong `draft_assets` và chặn các lệnh đọc file hệ thống trái phép (`\input{/etc/...}`, `\write18`) trước khi gửi lên sandbox.

---

## Implementation Tasks

### Task 1: Academic Skeleton Generator, Asset Zip-Slip Guard & E2B Compiler Port (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/draft_skeleton.py`
- Modify: `packages/core/src/core/services/latex_compiler.py`
- Test: `packages/core/tests/test_draft_skeleton_and_security.py`

**Interfaces:**
- Consumes: Python Standard Library (`re`, `hashlib`, `dataclasses`).
- Produces:
  - `generate_academic_skeleton(title: str, papers: list[dict], notes: list[dict]) -> tuple[str, str]` (trả về `(main_tex, references_bib)` đã escape ký tự đặc biệt LaTeX/BibTeX và điền sẵn `\cite{citekey}`).
  - `sanitize_and_validate_asset_filename(filename: str, byte_size: int) -> str` (ném `AssetSecurityError` nếu chứa `..`, `/`, `\` hoặc `> 10MB`).
  - Xóa bỏ hàm `_generate_in_memory_pdf_preview()` trong `latex_compiler.py`; chuẩn hóa giao diện biên dịch qua E2B Sandbox (`timeout_seconds = 15`, `--no-shell-escape`).

- [ ] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_draft_skeleton_and_security.py`:
```python
import pytest
from core.services.draft_skeleton import (
    generate_academic_skeleton,
    sanitize_and_validate_asset_filename,
    AssetSecurityError,
)


def test_generate_academic_skeleton_creates_valid_tex_and_bib():
    papers = [
        {
            "title": "Attention & Transformers: A 100% Survey",
            "authors": ["Vaswani, Ashish"],
            "year": 2017,
            "doi": "10.48550/arXiv.1706.03762",
        }
    ]
    tex, bib = generate_academic_skeleton("Khóa luận AI", papers, notes=[])
    assert "\\documentclass" in tex
    assert "\\section{Related Work}" in tex
    assert "\\cite{" in tex
    assert "@article{" in bib
    assert "\\%" in tex or "\\%" in bib


def test_sanitize_asset_filename_blocks_zip_slip_and_oversize():
    with pytest.raises(AssetSecurityError):
        sanitize_and_validate_asset_filename("../../etc/passwd", 1024)
    with pytest.raises(AssetSecurityError):
        sanitize_and_validate_asset_filename("arch.png", 11 * 1024 * 1024)
    assert sanitize_and_validate_asset_filename("arch_v1.png", 2048) == "arch_v1.png"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_draft_skeleton_and_security.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.draft_skeleton'`

- [ ] **Step 3: Implement `draft_skeleton.py` and remove fake PyMuPDF preview from `latex_compiler.py`**

Cài đặt `generate_academic_skeleton`, `sanitize_and_validate_asset_filename` và làm sạch `latex_compiler.py` để chỉ sử dụng trình biên dịch thực thụ trên E2B Sandbox.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_draft_skeleton_and_security.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/services/draft_skeleton.py packages/core/src/core/services/latex_compiler.py packages/core/tests/test_draft_skeleton_and_security.py
git commit -m "feat(core): add academic LaTeX/BibTeX skeleton generator, asset security guard, and remove fake PDF preview"
```

---

### Task 2: LangGraph 4-Tool ReAct Agent with 3-Retry Self-Healing & Anti-Oscillation (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/latex_agent.py`
- Test: `packages/core/tests/test_latex_react_agent.py`

**Interfaces:**
- Consumes: `ICompilerPort`, GraphRAG query callback, `hashlib.sha256`.
- Produces:
  - `MAX_COMPILE_ATTEMPTS = 3`
  - `LatexCoAuthorAgent` thực thi luồng ReAct với 4 công cụ chuẩn (`edit_latex_files`, `list_project_files`, `query_library_graph_rag`, `compile_latex_e2b`), tự động phát chuỗi sự kiện (`thinking`, `tool_call`, `tool_result`, `content_update`, `compile_status`, `done`) và dừng ngay nếu phát hiện trạng thái mã nguồn lặp lại (`seen_content_hashes`).

- [ ] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_latex_react_agent.py` kiểm tra:
1. Khi lần biên dịch 1 báo lỗi `Missing $ inserted at line 42`, Agent tự động gọi `edit_latex_files` vá lỗi và gọi lại `compile_latex_e2b` thành công ở lần thử 2.
2. Khi cả 3 lần thử đều lỗi, Agent dừng đúng ở `attempt == 3` (`MAX_COMPILE_ATTEMPTS`) và trả về thông báo dòng lỗi chi tiết.
3. Khi Agent sinh lại đúng nội dung đã thất bại ở lần thử trước (oscillation), vòng lặp ngắt ngay lập tức.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_latex_react_agent.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.latex_agent'`

- [ ] **Step 3: Implement `packages/core/src/core/services/latex_agent.py`**

Cài đặt `LatexCoAuthorAgent` với 4 tools, ngân sách tối đa 3 lần thử và bộ nhớ `seen_content_hashes`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_latex_react_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/services/latex_agent.py packages/core/tests/test_latex_react_agent.py
git commit -m "feat(core): implement 4-tool LangGraph ReAct LaTeX co-author with 3-retry self-healing loop"
```

---

### Task 3: Drafts API: Reading-to-Writing Handover, OCC, 1-Click `:undo`, Assets & `:export-bundle` (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/services/draft_service.py`
- Modify: `apps/api/src/api/v1/endpoints/drafts.py`
- Test: `apps/api/tests/test_drafts_lifecycle_undo_export.py`

**Interfaces:**
- Consumes: `DraftModel`, `DraftAssetModel`, `DraftMessageModel`, `generate_academic_skeleton`, `sanitize_and_validate_asset_filename`, `LatexCoAuthorAgent`.
- Produces:
  - `POST /api/v1/drafts` (hỗ trợ `source_session_id` sinh khung sườn `main.tex` + `references.bib`).
  - `POST /api/v1/drafts/{id}:undo` (khôi phục `previous_snapshot`, tăng `version += 1`).
  - `POST /api/v1/drafts/{id}/assist` (SSE streaming unbuffered, lưu `previous_snapshot` đúng 1 lần trước Attempt 1, lưu lịch sử vào `draft_messages`).
  - `POST /api/v1/drafts/{id}/assets`, `GET /api/v1/drafts/{id}/assets`, `DELETE /api/v1/drafts/{id}/assets/{asset_id}`.
  - `POST /api/v1/drafts/{id}:export-bundle` (xuất gói `.zip` gồm `main.tex`, `references.bib`, `figures/*`, `preview.pdf` nếu có, và `README.txt` ngay cả khi bản thảo chưa biên dịch thành công).

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_drafts_lifecycle_undo_export.py` kiểm tra toàn bộ 5 kịch bản: cầu nối từ `source_session_id`, xung đột OCC `412 Precondition Failed`, hoàn tác `:undo` sau khi AI sửa nhiều bước, chặn Zip Slip khi tải ảnh `figures/`, và xuất gói `.zip` không chặn người dùng.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_drafts_lifecycle_undo_export.py -v`
Expected: FAIL

- [ ] **Step 3: Implement endpoints and service methods in `draft_service.py` & `drafts.py`**

Cập nhật `draft_service.py` và `drafts.py` tuân thủ đầy đủ Ma trận Mã lỗi Chuẩn hóa trong `SPEC-06`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_drafts_lifecycle_undo_export.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/draft_service.py apps/api/src/api/v1/endpoints/drafts.py apps/api/tests/test_drafts_lifecycle_undo_export.py
git commit -m "feat(api): add reading-to-writing handover, 1-click undo, figures CRUD, and camera-ready zip export"
```

---

### Task 4: Frontend 3-Column Overleaf Workspace, Live Execution Badges & 1-Click Undo (`apps/web`)

**Files:**
- Modify: `apps/web/src/features/writing/components/WritingWorkspace.tsx`
- Modify: `apps/web/src/features/writing/components/WritingAssistantPane.tsx`
- Test: `apps/web/src/features/writing/__tests__/WritingWorkspace3Col.test.tsx`

**Interfaces:**
- Consumes: `POST /api/v1/drafts/{id}/assist` (SSE), `POST /api/v1/drafts/{id}:undo`, `POST /api/v1/drafts/{id}/assets`, `POST /api/v1/drafts/{id}:export-bundle`.
- Produces:
  - Không gian 3 cột đồng bộ: Cột 1 (`main.tex`, `references.bib`, `figures/` kèm nút chèn nhanh `\includegraphics`), Cột 2 (PDF Preview + nút Xuất gói nộp bài `.zip`), Cột 3 (Khung chat AI hiển thị huy hiệu tiến trình tự vá lỗi `Lần 1/3..3/3` và nút `[↩️ Hoàn tác]`).

- [ ] **Step 1: Write the failing test**

Tạo `apps/web/src/features/writing/__tests__/WritingWorkspace3Col.test.tsx` kiểm tra chuyển đổi giữa `main.tex` và `references.bib`, hiển thị huy hiệu tiến trình tự sửa lỗi SSE và nút `[↩️ Hoàn tác]`.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- WritingWorkspace3Col`
Expected: FAIL

- [ ] **Step 3: Implement 3-column synchronization, undo button, and SSE badges in `WritingWorkspace.tsx` & `WritingAssistantPane.tsx`**

Hoàn thiện giao diện 3 cột theo đúng đặc tả Mục 6 của `SPEC-06`.

- [ ] **Step 4: Run all 4 verification gates to confirm 100% pass**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: 100% PASS (exit code 0)

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/writing/
git commit -m "feat(web): complete 3-column Overleaf writing workspace with self-healing SSE badges and 1-click undo"
```
