# Universal Agent Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng hệ thống Universal Repo-Owned Agent Harness và bộ công cụ công thái học hoàn chỉnh cho VeriScholar MVP, tối ưu hóa cửa sổ ngữ cảnh qua Progressive Disclosure và gác cổng kiến trúc tự động bằng 5 bài test AST/Regex cơ học.

**Architecture:** Sử dụng mô hình Repo-Owned Harness lấy cảm hứng từ Langfuse: Tách bạch Hiến pháp tối cao (`AGENTS.md` < 150 dòng) với Thư viện kỹ năng chuyên biệt (`.agents/skills/`), cung cấp công cụ kiểm chuẩn môi trường (`scripts/dev/setup.sh`) và seeder ngoại tuyến xác định (`scripts/dev/seed.py`), đồng thời thiết lập rào chắn kiểm thử cơ học (`apps/api/tests/test_architecture_boundary.py`) kiểm tra ranh giới Lục giác bằng AST, quét từ khóa di sản cấm và chặn liên kết tuyệt đối máy chủ (`file://` scheme).

**Tech Stack:** Python 3.12, AST (`ast` module), Pytest, FastAPI, PostgreSQL 16+ (`pgvector`), Redis 7, CAS storage (`storage/blobs/`), Docker Compose, React 19, Vite, Tailwind CSS.

**Spec:** [`08-universal-agent-harness-spec.md`](../../specs/08-universal-agent-harness-spec.md) (kèm thiết kế tại [`2026-10-25-universal-agent-harness-design.md`](../specs/2026-10-25-universal-agent-harness-design.md)).

## Global Constraints

- **Python Runtime:** Python 3.12+ quản lý qua `uv workspace` (`apps/api` và `packages/core`).
- **Database & Cache:** Thuần PostgreSQL 16+ với `pgvector` và Redis 7. Tuyệt đối không SQLite, không Neo4j.
- **Ranh giới Lục giác:** `packages/core/src/core/domain/` và `ports/` chỉ được dùng Standard Library và `pydantic`. Cấm tuyệt đối import từ framework I/O, database hoặc `apps.api`.
- **Dung lượng Hiến pháp:** `AGENTS.md` bắt buộc $< 150$ dòng (giới hạn cứng rào chắn $< 200$ dòng).
- **Quy chuẩn Liên kết Markdown:** Tuyệt đối cấm sử dụng liên kết tuyệt đối máy chủ (`file://` scheme) trong toàn bộ các tệp `.md` của kho mã nguồn (`docs/`, `.agents/`, `README.md`).
- **Lưu trữ CAS:** File PDF vật lý lưu trữ theo mã băm SHA-256 tại `storage/blobs/{hash[:2]}/{hash[2:4]}/{hash}` với cam kết tiêu hủy khi `ref_count <= 0`.
- **Bảo toàn Kỹ năng Giao diện:** Giữ nguyên vẹn 8 skills thiết kế UI/UX hiện có trong `.agents/skills/`.

## Review Focus

1. **AST Checker bỏ sót lazy import hoặc submodule `apps.api`:** Import nằm bên trong hàm/method hoặc `from apps.api.db import session` phải bị phát hiện; test phải duyệt toàn bộ cây cú pháp qua `ast.walk()`.
2. **AST Checker nhầm lẫn relative import trong core:** Các import nội bộ như `from .entities import ...` hoặc `from core.domain...` phải được chấp thuận hợp lệ.
3. **Seeder gây lỗi thiếu thư mục CAS:** `seed.py` phải tự động gọi `os.makedirs(..., exist_ok=True)` trước khi ghi physical PDF blobs vào `storage/blobs/`.
4. **Từ khóa cấm và liên kết Markdown:** Bộ quét từ khóa cấm giới hạn trong mã nguồn Python production (`apps/api/src/` và `packages/core/src/`), trong khi bộ quét liên kết Markdown kiểm tra toàn bộ `docs/**/*.md` và `.agents/**/*.md`.
5. **Cổng kiểm tra CI:** Bắt buộc duy trì 100% exit code 0 cho cả 4 cổng: `ruff check .`, `pytest`, `npm test`, `npm build`.

---

### Task 1: Dọn Dẹp Mã Nguồn Di Sản & Working Tree (Legacy Cleanup)

**Files:**
- Modify: `apps/api/src/api/db/session.py:1-40`
- Modify: `apps/api/src/api/__init__.py:1-20`
- Modify: `packages/core/src/core/domain/entities/folder.py:1-35`

**Interfaces:**
- Consumes: Cấu trúc hiện tại của `session.py`, `__init__.py`, `folder.py`.
- Produces: Mã nguồn production sạch 100%, không còn chứa `init_sqlite_fallback()` hay `ComparisonMatrixRow`/`ComparisonMatrixResult`.

- [ ] **Step 1: Viết test khẳng định không còn tàn dư SQLite trong `session.py`**

Thêm test kiểm tra vào `apps/api/tests/test_session_clean.py`:
```python
def test_no_sqlite_fallback_in_session():
    from api.db import session
    assert not hasattr(session, "init_sqlite_fallback")
```

- [ ] **Step 2: Chạy test để xác nhận test FAIL đỏ**

Run: `uv run pytest apps/api/tests/test_session_clean.py`  
Expected: FAIL với `AssertionError: assert not hasattr(session, 'init_sqlite_fallback')`

- [ ] **Step 3: Xóa bỏ `init_sqlite_fallback()` và `ComparisonMatrix`**

- Trong `apps/api/src/api/db/session.py`: Xóa hàm `init_sqlite_fallback()` và import `aiosqlite`.
- Trong `apps/api/src/api/__init__.py`: Xóa lệnh gọi `init_sqlite_fallback()`.
- Trong `packages/core/src/core/domain/entities/folder.py`: Xóa `ComparisonMatrixRow` và `ComparisonMatrixResult`.
- Xóa test tạm `apps/api/tests/test_session_clean.py`.

- [ ] **Step 4: Chạy lại toàn bộ test suite hiện có để xác nhận PASS xanh**

Run: `uv run ruff check . && uv run pytest`  
Expected: PASS toàn bộ test suite.

- [ ] **Step 5: Dọn dẹp working tree và Commit**

```bash
git add -u
git commit -m "refactor(cleanup): purge legacy sqlite fallback and obsolete comparison matrix entities"
```

---

### Task 2: Thiết Lập Cấu Trúc Khung Tác Nhân & Hiến Pháp (`AGENTS.md`)

**Files:**
- Create: `.agents/AGENTS.md`
- Create: `AGENTS.md` (Symlink trỏ tới `.agents/AGENTS.md`)
- Create: `.agents/ARCHITECTURE_PRINCIPLES.md`

**Interfaces:**
- Consumes: Yêu cầu từ Section 3.A và 3.B của Spec 08.
- Produces: File hiến pháp `< 150` dòng, symlink chuẩn mở và tài liệu 5 bất biến kiến trúc.

- [ ] **Step 1: Viết test kiểm tra tính hợp lệ của symlink và số dòng `AGENTS.md`**

Tạo test tạm `tests_harness_check.py`:
```python
import os
from pathlib import Path

def test_agents_symlink_and_length():
    root = Path(".")
    symlink = root / "AGENTS.md"
    target = root / ".agents" / "AGENTS.md"
    assert symlink.is_symlink(), "AGENTS.md must be a symlink"
    assert os.readlink(symlink) in [".agents/AGENTS.md", str(target)]
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 150, f"AGENTS.md is too long: {len(lines)} lines"
```

- [ ] **Step 2: Chạy test để xác nhận test FAIL đỏ**

Run: `uv run python -m pytest tests_harness_check.py`  
Expected: FAIL vì file `.agents/AGENTS.md` chưa tồn tại.

- [ ] **Step 3: Khởi tạo `.agents/AGENTS.md`, symlink và `ARCHITECTURE_PRINCIPLES.md`**

- Soạn `.agents/AGENTS.md`: Tinh gọn dưới 140 dòng, bao gồm Scope VeriScholar MVP, Operating Rules, 4 Cổng Kiểm Tra và Skill Router.
- Tạo symlink ở thư mục gốc: `ln -sf .agents/AGENTS.md AGENTS.md`.
- Soạn `.agents/ARCHITECTURE_PRINCIPLES.md`: Chi tiết 5 Bất biến kiến trúc (PostgreSQL `pgvector` + Redis 7, Hexagonal core, CAS SHA-256, E2B MicroVM, 3-tier monitoring).
- Xóa test tạm `tests_harness_check.py`.

- [ ] **Step 4: Xác minh symlink và đếm dòng**

Run: `readlink AGENTS.md && wc -l .agents/AGENTS.md`  
Expected: `.agents/AGENTS.md` và số dòng $< 150$.

- [ ] **Step 5: Commit**

```bash
git add .agents/AGENTS.md AGENTS.md .agents/ARCHITECTURE_PRINCIPLES.md
git commit -m "feat(harness): create repo-owned AGENTS.md router and architecture principles"
```

---

### Task 3: Xây Dựng 4 Core Skills Nghiệp Vụ VeriScholar

**Files:**
- Create: `.agents/skills/verischolar-backend/SKILL.md`
- Create: `.agents/skills/verischolar-frontend/SKILL.md`
- Create: `.agents/skills/verischolar-tdd/SKILL.md`
- Create: `.agents/skills/agent-maintenance/SKILL.md`

**Interfaces:**
- Consumes: Hướng dẫn kỹ thuật từ Spec 00 đến Spec 07.
- Produces: 4 kỹ năng nghiệp vụ chuyên biệt hỗ trợ Progressive Disclosure.

- [ ] **Step 1: Viết test kiểm tra sự tồn tại và cú pháp frontmatter của 4 skills**

Tạo test tạm `tests_skills_check.py`:
```python
from pathlib import Path

def test_core_skills_exist():
    core_skills = [
        "verischolar-backend",
        "verischolar-frontend",
        "verischolar-tdd",
        "agent-maintenance",
    ]
    for skill in core_skills:
        skill_file = Path(f".agents/skills/{skill}/SKILL.md")
        assert skill_file.exists(), f"Skill {skill} missing"
        content = skill_file.read_text(encoding="utf-8")
        assert content.startswith("---"), f"Skill {skill} missing frontmatter"
        assert "name:" in content and "description:" in content
```

- [ ] **Step 2: Chạy test để xác nhận test FAIL đỏ**

Run: `uv run python -m pytest tests_skills_check.py`  
Expected: FAIL vì 4 file skill chưa tồn tại.

- [ ] **Step 3: Soạn thảo nội dung chuẩn mực cho 4 Core Skills**

- Tạo `.agents/skills/verischolar-backend/SKILL.md`: FastAPI async, SQLAlchemy 2.0, dependency injection, session per request, `AsyncSessionLocal` cho background tasks, pgvector hybrid search RRF.
- Tạo `.agents/skills/verischolar-frontend/SKILL.md`: React 19, Zustand stores, `PdfCanvasViewer` với Bbox highlight `[x0, y0, x1, y1]`, KaTeX formatting, SSE unbuffered stream qua `@microsoft/fetch-event-source`.
- Tạo `.agents/skills/verischolar-tdd/SKILL.md`: TDD workflow, transaction rollback fixtures, mocks cho E2B và OpenAI, kiểm thử cô lập đa người dùng.
- Tạo `.agents/skills/agent-maintenance/SKILL.md`: Co-location commit rule, tháp thẩm quyền, hướng dẫn audit và đào thải rule mồ côi.
- Xóa test tạm `tests_skills_check.py`.

- [ ] **Step 4: Chạy kiểm tra tồn tại và bảo toàn 8 UI skills**

Run: `ls -d .agents/skills/*/`  
Expected: Hiển thị đủ 12 skills (4 core mới + 8 UI skills đã có).

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/verischolar-backend/ .agents/skills/verischolar-frontend/ .agents/skills/verischolar-tdd/ .agents/skills/agent-maintenance/
git commit -m "feat(harness): author 4 core domain skills with progressive disclosure"
```

---

### Task 4: Xây Dựng Bộ Công Cụ Developer Xác Định (`setup.sh`, `seed.py`, `docker-compose.yml`)

**Files:**
- Modify: `docker-compose.yml` (Bổ sung service `redis:7-alpine`)
- Create: `scripts/dev/setup.sh` (chmod +x)
- Create: `scripts/dev/seed.py`

**Interfaces:**
- Consumes: CSDL PostgreSQL 16+ `pgvector`, Redis 7, các models `UserModel`, `DocumentModel`, `DocumentChunkModel`, `DraftModel` hiện có.
- Produces: Môi trường dev có thể kiểm tra sức khỏe tự động và nạp dữ liệu offline 100% kèm physical PDF blobs.

- [ ] **Step 1: Viết test kiểm tra tính hợp lệ cú pháp của `seed.py` và service Redis trong `docker-compose.yml`**

Tạo test tạm `tests_tools_check.py`:
```python
import yaml
from pathlib import Path

def test_docker_compose_has_redis():
    data = yaml.safe_load(Path("docker-compose.yml").read_text())
    assert "redis" in data.get("services", {})
    assert "redis:7-alpine" in data["services"]["redis"]["image"]

def test_setup_and_seed_exist():
    assert Path("scripts/dev/setup.sh").exists()
    assert Path("scripts/dev/seed.py").exists()
```

- [ ] **Step 2: Chạy test để xác nhận test FAIL đỏ**

Run: `uv run python -m pytest tests_tools_check.py`  
Expected: FAIL vì `docker-compose.yml` chưa có redis và scripts chưa tạo.

- [ ] **Step 3: Cập nhật `docker-compose.yml` và cài đặt `setup.sh`, `seed.py`**

- Cập nhật `docker-compose.yml`: Bổ sung service `redis:7-alpine` với port `6379:6379`.
- Tạo `scripts/dev/setup.sh`: Script kiểm tra `docker compose`, ping `pgvector`, ping `redis`, kiểm tra Python, Node, uv, pnpm. Phân quyền `chmod +x scripts/dev/setup.sh`.
- Tạo `scripts/dev/seed.py`:
  - Khởi tạo User mặc định: `dev@verischolar.edu.vn / ScholarDev@123456`.
  - Copy file `data/papers/Attention Is All You Need.pdf` vào `storage/blobs/` theo đúng mã băm SHA-256 CAS; sinh 2 dummy PDF hợp lệ cho ResNet và BERT vào `storage/blobs/`.
  - Nạp các bản ghi tương ứng vào bảng `documents`, `document_chunks` (kèm vector giả lập và Bbox `[x0, y0, x1, y1]`), `research_sessions` và `drafts`.
- Xóa test tạm `tests_tools_check.py`.

- [ ] **Step 4: Chạy xác minh cú pháp và chạy thử nghiệm**

Run: `uv run python -m py_compile scripts/dev/seed.py && bash -n scripts/dev/setup.sh`  
Expected: Cú pháp hợp lệ không có lỗi (Exit code 0).

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml scripts/dev/setup.sh scripts/dev/seed.py
git commit -m "feat(dev-tools): add redis service, setup healthcheck and deterministic offline seeder"
```

---

### Task 5: Hiện Thực Hóa Rào Chắn Kiểm Thử Tự Động (`test_architecture_boundary.py`) & Nghiệm Thu Toàn Trình

**Files:**
- Create/Modify: `apps/api/tests/test_architecture_boundary.py`

**Interfaces:**
- Consumes: Mã nguồn Python trong `packages/core` và `apps/api`, thư mục `.agents/`, `docs/`.
- Produces: Bộ kiểm tra tự động 5 chốt chặn:
  1. `test_hexagonal_boundary_pure_domain()`
  2. `test_hexagonal_checker_catches_apps_api_submodules()`
  3. `test_banned_legacy_artifacts()`
  4. `test_no_absolute_file_urls_in_markdown()`
  5. `test_agent_harness_integrity()`

- [ ] **Step 1: Viết file kiểm thử `apps/api/tests/test_architecture_boundary.py`**

Cài đặt đủ 5 bài test gác cổng cơ học:
1. `test_hexagonal_boundary_pure_domain()`: Duyệt `ast.walk()` mọi file trong `packages/core/src/core/domain/` và `ports/`, báo lỗi nếu import `fastapi`, `sqlalchemy`, `redis`, `fitz`, `httpx`, `aiofiles`, hoặc `apps.api`.
2. `test_hexagonal_checker_catches_apps_api_submodules()`: Kiểm thử khẳng định bộ quét AST bắt được cả import submodule `from apps.api.db import session`.
3. `test_banned_legacy_artifacts()`: Quét nội dung các file `.py` trong `apps/api/src/` và `packages/core/src/`, báo lỗi nếu chứa `aiosqlite`, `sqlite3`, `neo4j`, `ComparisonMatrix`, `DeBERTa`.
4. `test_no_absolute_file_urls_in_markdown()`: Quét toàn bộ các file `.md` trong `docs/`, `.agents/`, `README.md` để chặn đứng liên kết tuyệt đối máy chủ (`file://` scheme).
5. `test_agent_harness_integrity()`: Kiểm tra root `AGENTS.md` là symlink trỏ tới `.agents/AGENTS.md`, sự tồn tại của 4 core skills, `setup.sh`, `seed.py` và số dòng `AGENTS.md <= 200`.

- [ ] **Step 2: Chạy kiểm thử ranh giới kiến trúc**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py -v`  
Expected: PASS cả 5 bài test với 100% exit code 0.

- [ ] **Step 3: Chạy toàn bộ 4 Cổng Xác Minh Bắt Buộc**

```bash
uv run ruff check .
uv run pytest
npm --prefix apps/web run test
npm --prefix apps/web run build
```
Expected: Cả 4 cổng đều trả về Exit code 0.

- [ ] **Step 4: Commit**

```bash
git add apps/api/tests/test_architecture_boundary.py
git commit -m "test(architecture): enforce hexagonal boundary, banned keywords, relative markdown links and harness integrity"
```
