# Developer One-Command Setup & Pre-Push Verification Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tự động hóa quy trình thiết lập môi trường sau khi `git clone`/`git pull` chỉ bằng 1 lệnh (`make setup` / `make dev`) và thiết lập chốt chặn kiểm định 4 cổng bắt buộc (`make verify` & Git `pre-push` hook) trước khi đẩy code lên GitHub.

**Architecture:** Mở rộng hệ thống kịch bản vận hành trong `scripts/dev/` kết hợp `Makefile` điều phối tại thư mục gốc: `scripts/dev/setup.sh` đảm nhiệm đồng bộ `.env` symlink, cài đặt `uv`/`pnpm`, khởi chạy `postgres`/`redis` (tự động fallback `sudo` khi thiếu quyền Docker socket), chạy `api.db.init_db` tạo 18 bảng và gắn Git `pre-push` hook; `scripts/dev/verify.sh` thực thi tuần tự 4 Cổng xác minh theo cơ chế fail-fast.

**Tech Stack:** Bash (`set -euo pipefail`), GNU Make, Docker Compose (`pgvector/pgvector:0.8.6-pg18`, `redis:7-alpine`), `uv`, `pnpm`, `pytest`.

**Spec:** [`docs/superpowers/specs/2026-10-25-dev-setup-and-verification-design.md`](../specs/2026-10-25-dev-setup-and-verification-design.md)

---

## Global Constraints

- Tuân thủ quy tắc Single Source of Truth cho biến môi trường: giữ một file `.env` gốc duy nhất và tạo relative symlink `apps/api/.env -> ../../.env` (theo [`AGENTS.md`](../../../AGENTS.md)).
- Tự động phát hiện quyền truy cập Docker socket (`/var/run/docker.sock`): nếu user hiện tại chưa thuộc nhóm `docker`, script tự động dùng `sudo docker compose up -d postgres redis`.
- Toàn bộ kịch bản shell phải có quyền thực thi (`chmod +x`) và vượt qua kiểm tra cú pháp `bash -n`.
- Mọi liên kết trong tài liệu Markdown bắt buộc sử dụng đường dẫn tương đối (Zero `file:///` URLs).

---

## Review Focus

1. **Docker Socket Permission Denied on Linux Host:** Khi user chưa được thêm vào nhóm `docker`, lệnh `docker info` trả về lỗi quyền truy cập; `scripts/dev/setup.sh` phải tự động chuyển sang `sudo docker compose up -d postgres redis` thay vì bỏ qua khiến bước migrate DB phía sau bị lỗi kết nối.
2. **Broken or Missing `apps/api/.env` Symlink After Fresh Clone:** Khi mới clone repo chưa có `.env` hoặc `apps/api/.env` bị mất symlink, `setup.sh` phải tạo `.env` từ `.env.example` (nếu thiếu) và khôi phục đúng relative symlink `../../.env`.
3. **Skip-Subprocess Infinite Recursion in Pytest:** Khi `scripts/dev/verify.sh` chạy `uv run pytest`, bài test kiểm tra `verify.sh` chỉ được kiểm tra cú pháp (`bash -n`), quyền thực thi và nội dung lệnh trong file, tuyệt đối không gọi đệ quy lại `verify.sh` bên trong `pytest`.
4. **Orphan Background Processes on `Ctrl+C` (`--start` mode):** Khi chạy `bash scripts/dev/setup.sh --start` (hoặc `make dev`), việc bấm `Ctrl+C` (`SIGINT`/`SIGTERM`) phải dọn dẹp sạch cả hai tiến trình Backend (`uvicorn`) và Frontend (`vite`).
5. **Pre-Push Hook Idempotency:** Chạy `make setup` nhiều lần liên tiếp không được ghi đè hỏng hoặc nhân bản nội dung trong `.git/hooks/pre-push`.

---

## Implementation Tasks

### Task 1: Pre-Push 4-Gate Verification Script (`scripts/dev/verify.sh`) & Workflow Test Suite

**Files:**
- Create: `scripts/dev/verify.sh`
- Create: `apps/api/tests/test_dev_workflow_scripts.py`

**Interfaces:**
- Consumes: 4 Cổng xác minh từ [`AGENTS.md`](../../../AGENTS.md) (`uv run ruff`, `uv run pytest`, `npm --prefix apps/web run test`, `npm --prefix apps/web run build`).
- Produces: Kịch bản thực thi `scripts/dev/verify.sh` (hỗ trợ cờ `--syntax-only` hoặc chạy trọn vẹn 4 cổng) và bộ test kiểm định `apps/api/tests/test_dev_workflow_scripts.py`.

- [ ] **Step 1: Viết failing test kiểm tra sự tồn tại, quyền thực thi và nội dung 4 cổng của `scripts/dev/verify.sh`**

Tạo `apps/api/tests/test_dev_workflow_scripts.py`:
```python
import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]


def test_verify_script_exists_and_enforces_four_gates():
    verify_script = ROOT_DIR / "scripts" / "dev" / "verify.sh"
    assert verify_script.exists(), "scripts/dev/verify.sh must exist"
    assert os.access(verify_script, os.X_OK), "scripts/dev/verify.sh must be executable"

    # Syntax check via bash -n
    res = subprocess.run(["bash", "-n", str(verify_script)], capture_output=True, text=True)
    assert res.returncode == 0, f"bash -n failed: {res.stderr}"

    content = verify_script.read_text(encoding="utf-8")
    assert "uv run ruff check ." in content
    assert "uv run ruff format --check ." in content
    assert "uv run pytest" in content
    assert "npm --prefix apps/web run test" in content
    assert "npm --prefix apps/web run build" in content
```

- [ ] **Step 2: Chạy pytest để xác nhận test FAIL vì chưa có `scripts/dev/verify.sh`**

Run: `uv run pytest apps/api/tests/test_dev_workflow_scripts.py -v`
Expected: FAIL with `AssertionError: scripts/dev/verify.sh must exist`

- [ ] **Step 3: Tạo `scripts/dev/verify.sh` và cấp quyền thực thi (`chmod +x`)**

Tạo `scripts/dev/verify.sh`:
```bash
#!/usr/bin/env bash
# VeriScholar 4 Mandatory Verification Gates Runner (Local & Pre-Push Hook)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== VeriScholar: Running 4 Mandatory Verification Gates ===${NC}"

echo -e "\n${GREEN}[Gate 1/4] Python Linter & Formatter (Ruff)...${NC}"
uv run ruff check .
uv run ruff format --check .

echo -e "\n${GREEN}[Gate 2/4] Backend & Architecture Boundary Tests (Pytest)...${NC}"
uv run pytest

echo -e "\n${GREEN}[Gate 3/4] Frontend Unit Tests (Vitest)...${NC}"
npm --prefix apps/web run test

echo -e "\n${GREEN}[Gate 4/4] Frontend Production Build (TypeScript & Vite)...${NC}"
npm --prefix apps/web run build

echo -e "\n${GREEN}✅ All 4 Verification Gates PASSED (100% Exit Code 0)!${NC}"
```
Chạy lệnh: `chmod +x scripts/dev/verify.sh`

- [ ] **Step 4: Chạy lại pytest để xác nhận PASS**

Run: `uv run pytest apps/api/tests/test_dev_workflow_scripts.py -v`
Expected: PASS

---

### Task 2: One-Command Onboarding & DB Bootstrap (`scripts/dev/setup.sh`)

**Files:**
- Modify: [`scripts/dev/setup.sh`](../../../scripts/dev/setup.sh)
- Modify: `apps/api/tests/test_dev_workflow_scripts.py`

**Interfaces:**
- Consumes: `api.db.init_db`, `scripts/dev/verify.sh`, [`docker-compose.yml`](../../../docker-compose.yml).
- Produces: [`scripts/dev/setup.sh`](../../../scripts/dev/setup.sh) tự động tạo `.env` + symlink `apps/api/.env`, cài đặt `uv sync` & `pnpm install`, bật `postgres`/`redis` (kèm fallback `sudo`), chạy `uv run python -m api.db.init_db`, cài `.git/hooks/pre-push`, và hỗ trợ cờ `--start`.

- [ ] **Step 1: Bổ sung test kiểm tra các bước tự động hóa trong `scripts/dev/setup.sh`**

Thêm vào `apps/api/tests/test_dev_workflow_scripts.py`:
```python
def test_setup_script_automates_env_deps_db_and_pre_push_hook():
    setup_script = ROOT_DIR / "scripts" / "dev" / "setup.sh"
    assert setup_script.exists(), "scripts/dev/setup.sh must exist"
    assert os.access(setup_script, os.X_OK), "scripts/dev/setup.sh must be executable"

    res = subprocess.run(["bash", "-n", str(setup_script)], capture_output=True, text=True)
    assert res.returncode == 0, f"bash -n failed: {res.stderr}"

    content = setup_script.read_text(encoding="utf-8")
    assert "ln -sf ../../.env apps/api/.env" in content
    assert "uv sync --all-packages" in content
    assert "api.db.init_db" in content
    assert ".git/hooks/pre-push" in content
    assert "--start" in content
```

- [ ] **Step 2: Chạy pytest để xác nhận test mới FAIL**

Run: `uv run pytest apps/api/tests/test_dev_workflow_scripts.py -v`
Expected: FAIL with `AssertionError`

- [ ] **Step 3: Nâng cấp `scripts/dev/setup.sh`**

Cập nhật [`scripts/dev/setup.sh`](../../../scripts/dev/setup.sh) để thực hiện:
1. Kiểm tra Python >= 3.12, Node.js >= 22, `uv`, `pnpm`/`npm`.
2. Nếu chưa có `.env` ở thư mục gốc và có `.env.example`, copy `.env.example` sang `.env`; luôn đảm bảo `ln -sf ../../.env apps/api/.env`.
3. Chạy `uv sync --all-packages` và `pnpm --prefix apps/web install` (hoặc `npm --prefix apps/web install` nếu chưa có `pnpm`).
4. Kiểm tra `docker info`: nếu truy cập trực tiếp được thì chạy `docker compose up -d postgres redis`, nếu cần quyền root trên Linux thì dùng `sudo docker compose up -d postgres redis`.
5. Chạy `uv run python -m api.db.init_db` để khởi tạo idempotent đủ 18 bảng, triggers và HNSW/GIN indexes.
6. Cài đặt `.git/hooks/pre-push` gọi `bash scripts/dev/verify.sh` và cấp quyền `chmod +x .git/hooks/pre-push`.
7. Nếu truyền cờ `--start`, khởi chạy đồng thời Backend (`uv run --package api api`) và Frontend (`npm --prefix apps/web run dev -- --host 0.0.0.0`) kèm `trap` dọn tiến trình khi nhận `SIGINT`/`SIGTERM`.

- [ ] **Step 4: Chạy lại pytest để xác nhận PASS**

Run: `uv run pytest apps/api/tests/test_dev_workflow_scripts.py -v`
Expected: PASS

---

### Task 3: Root `Makefile`, Documentation & CI Validation Integration

**Files:**
- Create: `Makefile`
- Modify: [`scripts/README.md`](../../../scripts/README.md)
- Modify: [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)
- Modify: `apps/api/tests/test_dev_workflow_scripts.py`

**Interfaces:**
- Consumes: `scripts/dev/setup.sh`, `scripts/dev/verify.sh`.
- Produces: `Makefile` với các target `setup`, `dev`, `verify`, `test`, `lint`, `build`; cập nhật [`scripts/README.md`](../../../scripts/README.md) và [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml).

- [ ] **Step 1: Bổ sung test kiểm tra `Makefile` và CI syntax check**

Thêm vào `apps/api/tests/test_dev_workflow_scripts.py`:
```python
def test_makefile_and_ci_reference_dev_scripts():
    makefile = ROOT_DIR / "Makefile"
    assert makefile.exists(), "Root Makefile must exist"
    mk_content = makefile.read_text(encoding="utf-8")
    for target in ("setup:", "dev:", "verify:"):
        assert target in mk_content, f"Makefile missing target {target}"

    ci_yml = ROOT_DIR / ".github" / "workflows" / "ci.yml"
    ci_content = ci_yml.read_text(encoding="utf-8")
    assert "scripts/dev/verify.sh" in ci_content
```

- [ ] **Step 2: Chạy pytest để xác nhận test mới FAIL**

Run: `uv run pytest apps/api/tests/test_dev_workflow_scripts.py -v`
Expected: FAIL with `AssertionError: Root Makefile must exist`

- [ ] **Step 3: Tạo `Makefile`, cập nhật `scripts/README.md` và `.github/workflows/ci.yml`**

1. Tạo `Makefile` ở thư mục gốc:
```makefile
.PHONY: setup dev verify lint test build

setup:
	bash scripts/dev/setup.sh

dev:
	bash scripts/dev/setup.sh --start

verify:
	bash scripts/dev/verify.sh

lint:
	uv run ruff check . && uv run ruff format --check .

test:
	uv run pytest && npm --prefix apps/web run test

build:
	npm --prefix apps/web run build
```
2. Cập nhật [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) dòng `bash -n` để kiểm tra thêm `scripts/dev/verify.sh`.
3. Cập nhật bảng hướng dẫn trong [`scripts/README.md`](../../../scripts/README.md) bổ sung `scripts/dev/setup.sh` và `scripts/dev/verify.sh`.

- [ ] **Step 4: Chạy toàn bộ `bash scripts/dev/verify.sh` để xác nhận 4 Cổng kiểm định đạt 100% PASS**

Run: `bash scripts/dev/verify.sh`
Expected: Exit code 0 (`All 4 Verification Gates PASSED`)
