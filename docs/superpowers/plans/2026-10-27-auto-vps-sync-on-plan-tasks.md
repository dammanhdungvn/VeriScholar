# Auto VPS Sync on Plan Tasks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa cơ chế tự động đồng bộ lên máy chủ VPS (`https://verischolar.duckdns.org`) sau mỗi Task trong Implementation Plan để phục vụ review từ xa mà không phụ thuộc vào nhánh `main`, đồng thời hỗ trợ Fast-Failover nhận diện VPS tắt trong 1 giây (exit 0) để tiết kiệm chi phí điện toán đám mây.

**Architecture:** Tối ưu hóa pipeline triển khai `scripts/deploy_to_vps.sh` với cơ chế kiểm tra kết nối SSH tức thì ở Step 0 (`ConnectTimeout=1s`), bổ sung chế độ `--fast` (chỉ build frontend và đồng bộ file/DB, bỏ qua test trùng lặp để hoàn tất trong 5-7 giây), và chuẩn hóa quy tắc vận hành thường trực trong `AGENTS.md`.

**Tech Stack:** Bash, SSH/Rsync, Python 3.12, Pytest, Subprocess, AGENTS harness constitution.

**Spec:** `docs/specs/09-deployment-cicd-and-evaluation-spec.md`, `docs/PRD/08-deployment-and-system-evaluation.md`.

## Global Constraints
- Tuân thủ nghiêm ngặt 4 Verification Gates (`ruff`, `pytest`, `npm test`, `npm run build`).
- TDD bắt buộc: Viết test đỏ trước $\rightarrow$ Viết code xanh tối thiểu $\rightarrow$ Refactor.
- Zero-Wait & Zero-Failure: Khi VPS tắt, script tuyệt đối không được báo lỗi (phải trả về exit code 0) và không được chờ quá 1 giây.
- Dry-Run Safety: Chế độ `--dry-run` không được phép kết nối mạng thực tế với khóa giả (dummy key) để đảm bảo các unit test chạy offline độc lập.
- Không phụ thuộc vào branch `main`: Cho phép đồng bộ từ bất kỳ working branch nào.

## Review Focus
1. **Unreachable VPS Host Timeout:** VPS tắt làm script treo lâu $\rightarrow$ Khắc phục bằng cờ `-o ConnectTimeout=1 -o BatchMode=yes` ở Step 0 trước mọi bước build/test.
2. **Offline Unit Test Dry Run:** Chạy unit test với dummy SSH key bị fail do cố gắng kết nối SSH $\rightarrow$ Kiểm tra cờ `DRY_RUN` trước khi thực hiện probe mạng.
3. **Redundant Test Overhead:** Chạy toàn bộ 100+ pytest/vitest ở mỗi task làm chậm nhịp độ $\rightarrow$ Hỗ trợ cờ `--fast` chỉ build frontend và sync, dựa trên việc task vừa pass test riêng.
4. **Exit Code Semantics:** VPS offline trả về lỗi khiến CI/harness dừng việc $\rightarrow$ Quy định rõ VPS offline là trạng thái hợp lệ (tiết kiệm chi phí), trả về exit code 0.
5. **Operating Rule Alignment:** Agent quên deploy giữa các task $\rightarrow$ Bổ sung quy tắc bắt buộc vào `AGENTS.md` mục Operating Rules.

---

### Task 1: Add Unit Tests for `--fast` Flag and Instant VPS Offline Detection

**Files:**
- Modify: `tests/test_deploy_script.py`
- Consumes: `scripts/deploy_to_vps.sh`

**Interfaces:**
- Produces: 
  - `test_deploy_script_fast_flag_help()`: Chứng minh `--fast` xuất hiện trong `--help`.
  - `test_deploy_script_fast_flag_dry_run()`: Chứng minh `--fast` kết hợp `--dry-run` chạy thành công.
  - `test_deploy_script_offline_vps_exits_zero_fast()`: Chứng minh khi kết nối tới IP không khả dụng (ví dụ: `192.0.2.1` TEST-NET-1), script in thông báo bỏ qua và thoát exit code 0 trong $\le 2$ giây.

- [x] **Step 1: Write the failing tests in `tests/test_deploy_script.py`**
- [x] **Step 2: Run pytest to verify the tests fail**
Run: `uv run pytest tests/test_deploy_script.py -v`
Expected: FAIL (unknown argument `--fast`).

- [x] **Step 3: Commit test file**

```bash
git add tests/test_deploy_script.py
git commit -m "test(deploy): add unit tests for --fast flag and instant vps offline detection"
```

---

### Task 2: Implement Step 0 Instant Pre-flight Check and `--fast` Flag in `scripts/deploy_to_vps.sh`

**Files:**
- Modify: `scripts/deploy_to_vps.sh`
- Test: `tests/test_deploy_script.py`

**Interfaces:**
- Consumes: CLI args `--fast`, `--dry-run`, `--skip-gate`, `--no-sync-db`
- Produces: 
  - Thêm cờ `--fast` vào parser và trợ giúp (`usage`).
  - Khi `--fast` được bật, bỏ qua Gate 1-3 (Linter, Backend pytest, Vitest), chỉ chạy Gate 4 (`npm --prefix apps/web run build`).
  - Đưa khối Pre-flight Check lên Step 0 (ngay sau khi kiểm tra file SSH Key và sau kiểm tra `DRY_RUN`).
  - Thiết lập `-o ConnectTimeout=1` để thoát ngay lập tức trong 1s nếu VPS tắt.

- [x] **Step 1: Implement changes in `scripts/deploy_to_vps.sh`**
- [x] **Step 2: Run unit tests to verify they pass**
Run: `uv run pytest tests/test_deploy_script.py -v`
Expected: 100% tests pass.

- [x] **Step 3: Verify dry-run and fast execution directly**
Run: `bash scripts/deploy_to_vps.sh --help`
Run: `bash scripts/deploy_to_vps.sh --fast --dry-run`
Expected: Exit code 0, hiển thị thông tin rõ ràng.

- [x] **Step 4: Commit**

```bash
git add scripts/deploy_to_vps.sh
git commit -m "feat(deploy): add instant pre-flight check and --fast flag for task-level vps sync"
```

---

### Task 3: Standardize In-Plan Auto VPS Sync Operating Rule in `AGENTS.md`

**Files:**
- Modify: `AGENTS.md:30-40`

**Interfaces:**
- Consumes: Quy chuẩn vận hành cốt lõi của VeriScholar.
- Produces: Điều khoản quy định bất biến:
  - Tự động gọi `bash scripts/deploy_to_vps.sh --fast` sau mỗi task trong implementation plan.
  - Cho phép người dùng review từ xa mà không cần push lên `main`.
  - Tự động bỏ qua khi VPS tắt mà không gây gián đoạn luồng làm việc.

- [x] **Step 1: Update `AGENTS.md` with Rule Item 9**
- [x] **Step 2: Run linter and verification check**
Run: `uv run ruff check . && uv run ruff format --check .`
Run: `uv run pytest tests/test_thesis_rules.py`
Expected: Pass 100%.

- [x] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs(constitution): add rule for automatic task-level vps sync on plan execution"
```

---

### Task 4: Repository Verification across 4 Verification Gates

**Files:**
- Repository-wide verification across all 4 gates.

- [x] **Step 1: Run Gate 1 (Python Linter & Formatter)**
Run: `uv run ruff check . && uv run ruff format --check .`
Expected: 0 errors, 0 format warnings. (Status: PASSED - 158 files)

- [x] **Step 2: Run Gate 2 (Backend Unit & Integration Tests)**
Run: `uv run pytest`
Expected: 100% tests passed. (Status: PASSED - 105 passed in 16.42s)

- [x] **Step 3: Run Gate 3 (Frontend Unit Tests)**
Run: `npm --prefix apps/web run test`
Expected: 100% tests passed. (Status: PASSED - 16 files, 72 passed)

- [x] **Step 4: Run Gate 4 (Production Build Frontend)**
Run: `npm --prefix apps/web run build`
Expected: Exit code 0. (Status: PASSED - built in 1.70s)

- [x] **Step 5: Verify Live Remote Pre-flight with Real VPS**
Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Sync thành công lên `https://verischolar.duckdns.org` nếu VPS đang bật; hoặc bỏ qua trong 1s nếu VPS tắt. (Status: PASSED - synced & verified live)
