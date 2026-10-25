# Repo-Owned Universal Agent Harness, Offline Deterministic Seeder & Mechanical AST Gatekeeper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Duy trì và củng cố Khung Điều Hướng Tác Nhân Đa Nền Tảng (`.agents/AGENTS.md` `< 150` dòng, 4 Core Skills theo cơ chế Progressive Disclosure), bộ công cụ khởi tạo & nạp dữ liệu mẫu ngoại tuyến 100% xác định (`scripts/dev/setup.sh`, `scripts/dev/seed.py`), và rào chắn kiểm thử kiến trúc cơ học bằng AST (`apps/api/tests/test_architecture_boundary.py`).

**Architecture:** Tách biệt Hiến pháp tối giản (`AGENTS.md` symlink $\rightarrow$ `.agents/AGENTS.md`) với kho kỹ năng chuyên sâu (`.agents/skills/`); cơ học hóa toàn bộ 5 bất biến kiến trúc thành bài kiểm thử tự động `test_architecture_boundary.py` chạy trong `< 0.1s` để chặn đứng mọi vi phạm import Lục giác, từ khóa di sản (`aiosqlite`, `sqlite3`, `neo4j`, `ComparisonMatrix`, `DeBERTa`), và liên kết tuyệt đối máy chủ (`file://` scheme).

**Tech Stack:** Python 3.12 (`ast`, `pathlib`, `hashlib`), Pytest, Bash, Docker Compose (`pgvector/pgvector:0.8.6-pg18`, `redis:7-alpine`).

**Spec:** [`docs/specs/08-universal-agent-harness-spec.md`](../../specs/08-universal-agent-harness-spec.md) & [`docs/superpowers/specs/2026-10-25-universal-agent-harness-design.md`](../specs/2026-10-25-universal-agent-harness-design.md).

---

## Global Constraints

- Tệp `.agents/AGENTS.md` bắt buộc giữ độ dài tinh gọn `< 150` dòng (cứng `<= 200` dòng được gác cổng bởi `test_agent_harness_integrity`).
- Tuyệt đối không sử dụng liên kết tuyệt đối máy chủ (`file://` scheme) trong bất kỳ tệp `.md` nào trong toàn bộ kho mã nguồn (`docs/`, `.agents/`, `README.md`).
- Tuân thủ **Co-Location Commit Rule**: mọi thay đổi về endpoint, schema CSDL hoặc quy tắc kiến trúc phải cập nhật đồng thời tệp `SKILL.md` tương ứng trong `.agents/skills/` trong cùng một commit.
- Mọi thay đổi phải vượt qua 100% cả 5 bài kiểm thử cơ học trong `apps/api/tests/test_architecture_boundary.py` và 4 Cổng Xác Minh Bắt Buộc.

---

## Review Focus

1. **Submodule Import Bypass in AST Checker:** Một tác nhân có thể viết `from apps.api.db import session` hoặc `import api.services` bên trong `packages/core/src/core/domain/`; bộ kiểm tra AST phải bắt được cả tên gói gốc lẫn đường dẫn submodule.
2. **Self-Referential False Positives in Markdown URL Scanner:** Khi tài liệu quy tắc giải thích về việc cấm dùng `file://`, cần diễn đạt bằng văn phạm mô tả (`(file:// scheme)`) để không vô tình chứa chuỗi mẫu kích hoạt lỗi giả.
3. **Offline Deterministic CAS Blob Seeding:** Khi chạy `scripts/dev/seed.py` trong môi trường không có internet, script phải tự sinh tệp PDF hợp lệ tối thiểu (`%PDF-1.4...`) khớp chính xác với mã băm SHA-256 lưu trong `document_storage_blobs` để trình đọc PDF Canvas hoạt động trơn tru.
4. **Idempotent Seeder Execution:** Chạy `uv run python scripts/dev/seed.py` nhiều lần liên tiếp không được gây lỗi trùng khóa `UniqueViolationError` mà phải cập nhật hoặc bỏ qua an toàn.
5. **Executable Permission Preservation on Dev Scripts:** Các tệp `scripts/dev/setup.sh` và `scripts/dev/seed.py` phải luôn bảo toàn cờ thực thi (`chmod +x`) trên hệ thống tệp Git.

---

## Implementation Tasks

### Task 1: Mechanical Architecture Boundary Gatekeeper Verification (`apps/api/tests/test_architecture_boundary.py`)

**Files:**
- Modify: `apps/api/tests/test_architecture_boundary.py`
- Test: `apps/api/tests/test_architecture_boundary.py`

**Interfaces:**
- Consumes: `ast`, `pathlib.Path`, `re`.
- Produces:
  - `test_hexagonal_boundary_pure_domain()`
  - `test_hexagonal_checker_catches_apps_api_submodules()`
  - `test_banned_legacy_artifacts()`
  - `test_no_absolute_file_urls_in_markdown()`
  - `test_agent_harness_integrity()`

- [ ] **Step 1: Run the boundary test suite across the entire repository including `docs/superpowers/plans/`**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py -v`
Expected: 5/5 PASS

- [ ] **Step 2: Verify `docs/superpowers/` markdown files are covered by `test_no_absolute_file_urls_in_markdown`**

Xác nhận hàm quét liên kết Markdown trong `apps/api/tests/test_architecture_boundary.py` quét toàn bộ `docs/**/*.md` (bao gồm cả `docs/PRD/`, `docs/specs/`, `docs/superpowers/specs/` và `docs/superpowers/plans/`).

- [ ] **Step 3: Run all 4 Verification Gates**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: 100% PASS (exit code 0)
