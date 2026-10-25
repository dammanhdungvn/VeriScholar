# Azure Ubuntu Deployment, CI/CD & Graduation Thesis Evaluation (`PRD-08`, `Spec-09`, `THESIS_OUTLINE_MAPPING`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the complete Azure Ubuntu VM deployment & thesis evaluation specification suite (`PRD-08`, `Spec-09`, `docs/THESIS_OUTLINE_MAPPING.md`) and synchronize all production Nginx SSE routes, `Dockerfile.api`, and CD deployment scripts (`scripts/deploy_production.sh`, `scripts/deploy_web.sh`).

**Architecture:** Extends the two-tier VeriScholar documentation taxonomy (`docs/PRD/` and `docs/specs/`) with a dedicated Deployment & Quantitative Evaluation module (`08`/`09`) and a 5-chapter Graduation Thesis mapping guide (`docs/THESIS_OUTLINE_MAPPING.md`). Updates `deploy/nginx/production-host.conf` and `deploy/nginx/verischolar.conf` so all 5 MVP SSE endpoints bypass proxy buffering on Azure Ubuntu, upgrades `deploy/Dockerfile.api` to use deterministic `uv sync --frozen` with a persistent `/app/data/cas` volume, and restores executable deployment scripts invoked by `.github/workflows/cd.yml`.

**Tech Stack:** Nginx (Reverse Proxy + TLS 1.3 + Unbuffered SSE), Docker Compose (`pgvector/pgvector:0.8.6-pg18`, `redis:7-alpine`), Systemd (`uvicorn`), `uv` (Python 3.12), `pnpm` (Node 22 / Vite 8), GitHub Actions CI/CD, Pytest AST & Regex Boundary Tests.

**Spec:** [`../specs/2026-10-25-deployment-and-thesis-evaluation-design.md`](../specs/2026-10-25-deployment-and-thesis-evaluation-design.md)

## Global Constraints

- Relative markdown links only across all repository `.md` files (`docs/`, `.agents/`, `README.md`); zero `file://` URLs and zero broken relative links.
- Every file in `docs/PRD/0*.md` must strictly stay within `[120, 210]` lines and include all 4 standard BA sections (`## 1.`, `## 2.`, `## 3.`, `## 4.`).
- Nginx unbuffered SSE regex in both `deploy/nginx/production-host.conf` and `deploy/nginx/verischolar.conf` must match all 5 SSE routes: `sessions/.*/(chat|messages|messages:stream|context-table:stream)`, `documents/.*/summary:stream`, `library/graph:query`, and `drafts/.*/chat:stream`.
- `scripts/deploy_production.sh` and `scripts/deploy_web.sh` must be executable (`chmod +x`) and pass `bash -n` syntax validation required by `.github/workflows/cd.yml`.

## Review Focus

- Nginx buffering newly added MVP SSE routes (`context-table:stream`, `library/graph:query`, `drafts/{id}/chat:stream`) on Azure Ubuntu, causing token streams to stall in the browser until completion.
- `.github/workflows/cd.yml` failing on `main` push because `scripts/deploy_production.sh` or `scripts/deploy_web.sh` is missing or lacks executable permissions.
- Container restarts wiping uploaded PDFs and compiled LaTeX outputs when `/app/data/cas` is not declared as a persistent volume in `deploy/Dockerfile.api`.
- Adding `docs/PRD/08-deployment-and-system-evaluation.md` without updating the PRD count assertion in `test_prd_conciseness_and_structure_invariants()`, breaking Gate 2 (`uv run pytest`).
- Broken relative links between `docs/THESIS_OUTLINE_MAPPING.md`, `docs/README.md`, `README.md`, and the numbered `PRD`/`specs` files.

---

### Task 1: Author `PRD-08` (Deployment & System Evaluation) and `Spec-09` (Azure Ubuntu Deployment, CI/CD & Quantitative Benchmarks)

**Files:**
- Create: `docs/PRD/08-deployment-and-system-evaluation.md`
- Create: `docs/specs/09-deployment-cicd-and-evaluation-spec.md`
- Modify: `docs/README.md`
- Modify: `README.md`
- Test: `apps/api/tests/test_architecture_boundary.py`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-10-25-deployment-and-thesis-evaluation-design.md`
- Produces: `docs/PRD/08-deployment-and-system-evaluation.md` (140–195 lines), `docs/specs/09-deployment-cicd-and-evaluation-spec.md`, updated PRD count (`9`) in `test_prd_conciseness_and_structure_invariants()`

- [ ] **Step 1: Write the failing test in `apps/api/tests/test_architecture_boundary.py`**

Update `test_prd_conciseness_and_structure_invariants()` in `apps/api/tests/test_architecture_boundary.py` to expect `9` PRD files (`00..08`) and verify `docs/specs/09-deployment-cicd-and-evaluation-spec.md` exists with Quantitative Evaluation Benchmarks (`E1`, `E2`, `E3`):

```python
def test_prd_conciseness_and_structure_invariants():
    """Prevents PRD bloat and scope creep by enforcing line limits and required BA sections."""
    prd_dir = ROOT_DIR / "docs" / "PRD"
    prd_files = sorted(prd_dir.glob("0*.md"))
    assert len(prd_files) == 9, f"Expected 9 PRD files in docs/PRD/, found {len(prd_files)}"

    violations: list[str] = []
    for prd_file in prd_files:
        text = prd_file.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not (120 <= len(lines) <= 210):
            violations.append(
                f"{prd_file.name}: line count {len(lines)} outside allowed [120, 210] range"
            )
        for sec in ("## 1.", "## 2.", "## 3.", "## 4."):
            if sec not in text:
                violations.append(f"{prd_file.name}: missing required section prefix '{sec}'")

    assert not violations, "PRD structure or conciseness invariant violated:\n" + "\n".join(violations)

    spec_09 = ROOT_DIR / "docs" / "specs" / "09-deployment-cicd-and-evaluation-spec.md"
    assert spec_09.exists(), "docs/specs/09-deployment-cicd-and-evaluation-spec.md is missing"
    spec_09_text = spec_09.read_text(encoding="utf-8")
    for marker in ("Azure Ubuntu", "proxy_buffering off", "Thực Nghiệm 1", "Thực Nghiệm 2", "Thực Nghiệm 3"):
        assert marker in spec_09_text, f"Spec-09 missing required section marker: {marker}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py::test_prd_conciseness_and_structure_invariants -v`
Expected: FAIL with `AssertionError: Expected 9 PRD files in docs/PRD/, found 8`

- [ ] **Step 3: Create `docs/PRD/08-deployment-and-system-evaluation.md`, `docs/specs/09-deployment-cicd-and-evaluation-spec.md`, and update `docs/README.md` & `README.md`**

1. Write `docs/PRD/08-deployment-and-system-evaluation.md` (145–185 lines, `Phiên bản: 2.0-OFFICIAL`) containing:
   - `## 1. Bối Cảnh, Nỗi Đau & Giá Trị Cốt Lõi (Problem Statement & Value Proposition)` with `Before vs. After Value Matrix` for deploying AI research workloads on an Azure Ubuntu VM and defending the Graduation Thesis.
   - `## 2. Phân Loại Tác Nhân & Bảng Tổng Hợp Use Case (Actors & Use Case Summary)` with `UC-08.1` (Triển khai Tự động CI/CD lên Azure Ubuntu VM), `UC-08.2` (Vận hành Reverse Proxy Nginx TLS 1.3 & Unbuffered SSE), `UC-08.3` (Thực thi Bộ Thực nghiệm Định lượng E1/E2/E3 phục vụ Đồ án Tốt nghiệp).
   - `## 3. Đặc Tả Chi Tiết Các Ca Sử Dụng (Detailed Use Case Specifications)` following the strict 6-field BA template (`Tác nhân`, `Điều kiện tiên quyết`, `Sự kiện kích hoạt`, `Luồng chuẩn`, `Kết quả đầu ra`, `Luồng ngoại lệ`).
   - `## 4. Quy Tắc Nghiệp Vụ & Ràng Buộc Phi Chức Năng (Business Rules & NFRs)` (`BR-DEP-01..04`).
2. Write `docs/specs/09-deployment-cicd-and-evaluation-spec.md` covering:
   - Azure Ubuntu VM Deployment Architecture (Mermaid diagram + Hybrid Host-Nginx/Systemd/Docker Compose & Full Container modes).
   - Complete Nginx TLS 1.3 & 5-Route Unbuffered SSE contract.
   - CI/CD GitHub Actions (`ci.yml` + `cd.yml`), `.env.production` variable matrix, and CAS `/var/lib/verischolar/cas` + `pg_dump` backup protocol.
   - Quantitative System Evaluation Framework (`Thực Nghiệm 1: Hiệu Năng & Độ Trễ Streaming`, `Thực Nghiệm 2: Độ Chính Xác Truy Xuất AI & Grounding`, `Thực Nghiệm 3: Ma Trận Kiểm Thử Tự Động & Ranh Giới Kiến Trúc`).
3. Add `08-deployment-and-system-evaluation.md` and `09-deployment-cicd-and-evaluation-spec.md` to `docs/README.md` and `README.md`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/PRD/08-deployment-and-system-evaluation.md docs/specs/09-deployment-cicd-and-evaluation-spec.md docs/README.md README.md apps/api/tests/test_architecture_boundary.py
git commit -m "docs(prd,spec): add PRD-08 and Spec-09 for Azure Ubuntu deployment and thesis evaluation"
```

---

### Task 2: Author `docs/THESIS_OUTLINE_MAPPING.md` (5-Chapter Graduation Thesis Blueprint)

**Files:**
- Create: `docs/THESIS_OUTLINE_MAPPING.md`
- Modify: `docs/README.md`
- Test: `apps/api/tests/test_architecture_boundary.py`

**Interfaces:**
- Consumes: `docs/PRD/00..08`, `docs/specs/00..09`
- Produces: `docs/THESIS_OUTLINE_MAPPING.md` tested by `test_thesis_outline_mapping_integrity()`

- [ ] **Step 1: Write the failing test in `apps/api/tests/test_architecture_boundary.py`**

Add `test_thesis_outline_mapping_integrity()` to `apps/api/tests/test_architecture_boundary.py`:

```python
def test_thesis_outline_mapping_integrity():
    """Validates that docs/THESIS_OUTLINE_MAPPING.md exists and maps all 5 graduation thesis chapters."""
    thesis_doc = ROOT_DIR / "docs" / "THESIS_OUTLINE_MAPPING.md"
    assert thesis_doc.exists(), "docs/THESIS_OUTLINE_MAPPING.md is missing"
    content = thesis_doc.read_text(encoding="utf-8")
    for chapter in ("Chương 1", "Chương 2", "Chương 3", "Chương 4", "Chương 5"):
        assert chapter in content, f"THESIS_OUTLINE_MAPPING.md is missing '{chapter}'"
    assert "08-deployment-and-system-evaluation.md" in content
    assert "09-deployment-cicd-and-evaluation-spec.md" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py::test_thesis_outline_mapping_integrity -v`
Expected: FAIL with `AssertionError: docs/THESIS_OUTLINE_MAPPING.md is missing`

- [ ] **Step 3: Create `docs/THESIS_OUTLINE_MAPPING.md` and link it in `docs/README.md`**

Write `docs/THESIS_OUTLINE_MAPPING.md` with:
- Complete 5-Chapter Vietnamese Computer Science Graduation Thesis Outline (`Chương 1: Giới thiệu đề tài & Bài toán thực tế`, `Chương 2: Cơ sở lý thuyết & Công nghệ nền tảng`, `Chương 3: Phân tích & Thiết kế hệ thống`, `Chương 4: Cài đặt, Triển khai & Thực nghiệm Đánh giá`, `Chương 5: Kết luận & Hướng phát triển`).
- Direct relative markdown links mapping each thesis sub-section to the corresponding `PRD/00..08`, `specs/00..09`, and `superpowers/plans/2026-10-25-00..09` files.
- Parallel Coding + Thesis Writing Schedule table showing which thesis section to write immediately after completing each coding module (`Module 00` $\rightarrow$ `Module 09`).
- Reference link in `docs/README.md`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/THESIS_OUTLINE_MAPPING.md docs/README.md apps/api/tests/test_architecture_boundary.py
git commit -m "docs(thesis): add 5-chapter graduation thesis outline mapping guide"
```

---

### Task 3: Synchronize Azure Ubuntu Nginx SSE Routes, `Dockerfile.api`, 2-Tier Fast-Fail `ci.yml`, and CD Deployment Scripts (`scripts/deploy_*.sh`)

**Files:**
- Modify: `deploy/nginx/production-host.conf`
- Modify: `deploy/nginx/verischolar.conf`
- Modify: `deploy/Dockerfile.api`
- Modify: `.github/workflows/ci.yml`
- Create: `scripts/deploy_web.sh`
- Create: `scripts/deploy_production.sh`
- Test: `apps/api/tests/test_architecture_boundary.py`

**Interfaces:**
- Consumes: `docs/specs/09-deployment-cicd-and-evaluation-spec.md`, `.github/workflows/cd.yml`
- Produces: Synchronized `deploy/` configs, 2-tier `.github/workflows/ci.yml` with `pgvector` + `redis` services, and executable `scripts/deploy_production.sh` & `scripts/deploy_web.sh` verified by `test_deployment_configs_and_nginx_sse_routes()`

- [ ] **Step 1: Write the failing test in `apps/api/tests/test_architecture_boundary.py`**

Add `test_deployment_configs_and_nginx_sse_routes()` to `apps/api/tests/test_architecture_boundary.py`:

```python
def test_deployment_configs_and_nginx_sse_routes():
    """Validates Nginx SSE unbuffered routing, Dockerfile.api uv sync/CAS volume, 2-tier CI, and CD deploy scripts."""
    nginx_files = [
        ROOT_DIR / "deploy" / "nginx" / "production-host.conf",
        ROOT_DIR / "deploy" / "nginx" / "verischolar.conf",
    ]
    required_sse_fragments = [
        "context-table:stream",
        "library/graph:query",
        "drafts/.*/chat:stream",
        "summary:stream",
        "proxy_buffering off;",
    ]
    for nf in nginx_files:
        assert nf.exists(), f"Missing Nginx config: {nf}"
        content = nf.read_text(encoding="utf-8")
        for frag in required_sse_fragments:
            assert frag in content, f"{nf.relative_to(ROOT_DIR)} missing required SSE fragment '{frag}'"

    dockerfile_api = ROOT_DIR / "deploy" / "Dockerfile.api"
    assert dockerfile_api.exists(), "deploy/Dockerfile.api is missing"
    df_text = dockerfile_api.read_text(encoding="utf-8")
    assert "uv sync" in df_text, "deploy/Dockerfile.api must use 'uv sync' for deterministic builds"
    assert "/app/data/cas" in df_text, "deploy/Dockerfile.api must declare /app/data/cas volume"

    ci_yml = ROOT_DIR / ".github" / "workflows" / "ci.yml"
    ci_text = ci_yml.read_text(encoding="utf-8")
    assert "pgvector/pgvector:0.8.6-pg18" in ci_text, "ci.yml must include pgvector service container"
    assert "redis:7-alpine" in ci_text, "ci.yml must include redis:7-alpine service container"
    assert "tectonic" not in ci_text.lower(), "ci.yml must not install legacy Tectonic compiler"

    for script_name in ("deploy_production.sh", "deploy_web.sh"):
        script_path = ROOT_DIR / "scripts" / script_name
        assert script_path.exists(), f"Missing deployment script: scripts/{script_name}"
        assert os.access(script_path, os.X_OK), f"scripts/{script_name} must be executable (chmod +x)"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py::test_deployment_configs_and_nginx_sse_routes -v`
Expected: FAIL with `AssertionError: deploy/nginx/production-host.conf missing required SSE fragment 'context-table:stream'`

- [ ] **Step 3: Update `deploy/nginx/*.conf`, `deploy/Dockerfile.api`, `.github/workflows/ci.yml`, and create executable `scripts/deploy_web.sh` & `scripts/deploy_production.sh`**

1. In `deploy/nginx/production-host.conf` (both HTTPS port 443 and HTTP port 80 server blocks) and `deploy/nginx/verischolar.conf`, update the SSE location block regex to:
   `location ~* ^/api/v1/(sessions/.*/(chat|messages|messages:stream|context-table:stream)|documents/.*/summary:stream|library/graph:query|drafts/.*/chat:stream)`
   with `proxy_buffering off;`, `proxy_cache off;`, and `add_header X-Accel-Buffering "no" always;`.
2. In `deploy/Dockerfile.api`, use `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, run `uv sync --all-packages --frozen --no-dev`, create `/app/data/cas`, declare `VOLUME ["/app/data/cas"]`, and start `uv run uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2`.
3. In `.github/workflows/ci.yml`, implement the 2-Tier Fast-Fail pipeline (`backend-quality-gates` with `services: postgres` (`pgvector/pgvector:0.8.6-pg18`) + `redis` (`redis:7-alpine`), `frontend-quality-gates` without `pnpm audit --prod`, `security-scan` with `gitleaks`, and `docker-validation` gated by `needs: [backend-quality-gates, frontend-quality-gates]`), and format all Python files with `uv run ruff format .`.
4. Create `scripts/deploy_web.sh` and `scripts/deploy_production.sh` with `set -euo pipefail`, mark both `chmod +x`, and verify with `bash -n scripts/deploy_production.sh scripts/deploy_web.sh`.

- [ ] **Step 4: Run all Mandatory Verification Gates + `ruff format --check .`**

Run:
```bash
bash -n scripts/deploy_production.sh scripts/deploy_web.sh
uv run ruff check .
uv run ruff format --check .
uv run pytest -v
npm --prefix apps/web run test
npm --prefix apps/web run build
```
Expected: 100% PASS (exit code 0 across all commands)

- [ ] **Step 5: Commit**

```bash
git add deploy/ .github/workflows/ci.yml scripts/ apps/api/tests/test_architecture_boundary.py
git commit -m "feat(deploy,ci): align Azure Ubuntu Nginx SSE routes, 2-tier CI with pgvector/redis, and CD deploy scripts"
```
