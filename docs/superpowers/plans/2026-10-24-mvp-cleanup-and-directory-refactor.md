# VeriScholar MVP Cleanup & Directory Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Purge all out-of-scope 5-Pillar/Enterprise bloat, unused ~530MB ONNX weights, root junk files, dead scripts, obsolete docs, and out-of-scope Backend/Core/Frontend features so the repository strictly matches the VeriScholar MVP PRD (`docs/PRD/00..07`).

**Architecture:** We partition the cleanup into two non-overlapping execution tracks coordinated via `herdr`: **Track A (Tasks 1–3, assigned to Member 2 `w1:p2`)** cleans Root, `models/`, `.env*`, `deploy/`, `scripts/`, `packages/core/`, and `apps/api/`; **Track B (Tasks 4–6, assigned to Member 3 `w1:p4`)** cleans `apps/web/` (Navigation, Routes, Dashboard, Reader, Notes, Library, Writing) and `docs/`. Each task removes dead files, updates barrel exports and callers, and verifies with automated tests (`pytest`, `tsc -b`, `vitest run`) before committing.

**Tech Stack:** Python 3.12+, FastAPI, SQLAlchemy 2.0 (asyncpg + pgvector), Pydantic v2, Pytest, React 19, TypeScript, Vite, Zustand, TanStack Query, Vitest.

**Spec:** `docs/PRD/00-overview-and-cleanup.md` (with module specs `docs/PRD/01-auth-and-user.md` through `docs/PRD/07-monitoring-and-langfuse.md` and audit reports `docs/PRD/audit-backend-member2.md`, `docs/PRD/audit-frontend-member3.md`).

## Global Constraints

- Only 2 deployment environments are permitted: `development` (`LANGFUSE_ENVIRONMENT=verischolar-dev`) and `production` (`LANGFUSE_ENVIRONMENT=verischolar-prod`), plus internal `test` mode for `pytest`. Remove `uat`, `staging`, `sit`, and `enterprise`.
- Database architecture strictly uses **PostgreSQL + `pgvector`** for relational data, vector embeddings, and the 4-Entity Knowledge Graph (`Paper`, `Method`, `Dataset`, `MetricResult`). **Never reference or introduce Neo4j.**
- Global Left Sidebar (`DashboardTaskbar.tsx`) must contain **only 4 navigation items**: `🔍 Khám phá & Phiên đọc`, `⭐ Kho Yêu thích`, `✍️ Soạn thảo LaTeX`, and `👤 Tài khoản & Giao diện`.
- All 18 out-of-scope Backend API endpoints (`verify-facts`, `share`, `comments`, `export-overleaf`/`overleaf`/`overleaf-launch`, `associative-suggestions`, `comparison-matrix`, `export-pdf`, `export-bundle`, `citation-graph`, `notes:synthesize`, `/events`) must return `404 Not Found` (or `405 Method Not Allowed`).
- All LLM prompts live inline as Python constants in source code (`packages/core` / `apps/api`), not external `.prompt.md` Jinja2 files.

## Review Focus

1. **Broken Python barrel imports after deleting `packages/core` modules:** Importing `core.domain.entities`, `core.ports`, or `core.services` must not raise `ModuleNotFoundError` for `safe_claim`, `safe_verifier`, `safe_fact_checker`, `safe_nli_adapter`, `pdf_annotation`, `pdf_annotator`, `note_synthesis`, or `eval` (pinned in Task 2 Step 1 & Step 4).
2. **`init_db.py` and `models/__init__.py` referencing deleted SQLAlchemy models:** Starting FastAPI or running `init_db()` must not reference `DraftCommentModel`, `NoteSynthesisModel`, or `CitationEdgeModel` (pinned in Task 3 Step 1 & Step 4).
3. **`Settings.ENVIRONMENT` rejecting `test` during `pytest` runs when removing `uat`/`staging`:** `ENVIRONMENT` literal must narrow to `Literal["development", "production", "test"]` so `pytest` continues to run while rejecting `"uat"` and `"staging"` with `ValidationError` (pinned in Task 1 Step 1 & Step 4).
4. **Dangling Frontend imports or route links to deleted pages/modals:** Running `npm --prefix apps/web run build` (`tsc -b && vite build`) and navigating via `routes.tsx` or `DashboardTaskbar.tsx` must have zero references to `/matrix`, `/library/matrix`, `/projects`, `/notes` (standalone route), `/citations`, or any of the 17 deleted components (pinned in Task 4 Step 1 & Task 5 Step 1).
5. **Documentation regression introducing Neo4j or deleted 5-Pillar features:** `docs/` outside `docs/PRD/` must have zero files in `docs/02-modules-and-features/` and zero mentions of `Neo4j`, `DeBERTa`, `Comparison Matrix`, or `docker-compose.enterprise.yml` (pinned in Task 6 Step 1 & Step 4).

---

### Task 1 (Member 2 — `w1:p2`): Root Junk, Heavy ONNX Model (`models/`), `.env*`, `deploy/`, `storage/`, & `scripts/` Cleanup

**Files:**
- Delete: `AUDIT_CERTIFICATION_REPORT_FULL_SYSTEM.md`, `QUALITY_GATE_CERTIFICATION_4BUGS_PASS.md`, `QUALITY_GATE_FE_BE_TASKS_PASS.md`, `QUALITY_GATE_READER_OVERFLOW_PASS.md`, `QUALITY_GATE_RESPONSIVE_DEVICE_MATRIX_PASS.md`, `QUALITY_GATE_SCHOLAR_PROFILE_AUDIT.md`, `QUALITY_GATE_TEST_HARDENING_AUDIT.md`, `verischolar_runtime_data.tar.gz`, `verischolar_runtime_data.tar.gz.sha256`, `.coverage`, `test-results.xml`, `DESIGN.md`, `PROJECT.md`, `PROJECT_ENGINEERING_STANDARDS.md`, `temp/`, `tests/`
- Delete: `models/` (`models/nli/cross-encoder-nli-deberta-v3-small/`, `models/README.md`)
- Delete: `storage/verischolar.db`, `storage/verischolar.db-shm`, `storage/verischolar.db-wal`, `storage/blobs/`, `storage/logs/`
- Delete: `apps/api/.env.uat`, `deploy/.env.enterprise.example`, `deploy/docker-compose.enterprise.yml`, `deploy/pgbouncer/`
- Delete: `scripts/bootstrap_enterprise.sh`, `scripts/mcp_runtime_server.py`, `scripts/github_mcp_wrapper.sh`, `scripts/auto_beta_cohort_runner.py`, `scripts/benchmark_multi_agent_stress.py`, `scripts/test_load_concurrency.py`, `scripts/e2e-playwright-manual-audit.mjs`, `scripts/eval_api.py`, `scripts/eval_chat_roadmap.py`, `scripts/eval_chunking_quality.py`, `scripts/eval_module_01_ai_quality.py`, `scripts/eval_module_01_matrix.py`, `scripts/eval_post_sessions_chat.py`, `scripts/eval/` (after moving `scripts/eval/purge_all.py` to `scripts/purge_all.py`)
- Modify: `pyproject.toml`, `packages/core/pyproject.toml`, `.env.example`, `apps/api/.env.example`, `apps/api/.env.development`, `apps/api/.env.production`, `apps/api/src/api/core/config.py`, `deploy/systemd/verischolar-api.service`, `scripts/README.md`
- Test: `apps/api/tests/test_config_environments.py`

**Interfaces:**
- Consumes: `docs/PRD/00-overview-and-cleanup.md` (§5.1), `docs/PRD/07-monitoring-and-langfuse.md` (§2)
- Produces: `Settings.ENVIRONMENT: Literal["development", "production", "test"]`, `Settings.OPENAI_MODEL: str = "gpt-5.4-mini"`, `Settings.LANGFUSE_MASK_INPUT_OUTPUT: bool = False`, and `Settings.resolved_langfuse_environment -> Literal["verischolar-dev", "verischolar-prod", "test"]` in `apps/api/src/api/core/config.py`

- [ ] **Step 1: Write the failing test in `apps/api/tests/test_config_environments.py`**

```python
from pathlib import Path
import pytest
from pydantic import ValidationError
from api.core.config import Settings

REPO_ROOT = Path(__file__).resolve().parents[3]

def test_only_dev_prod_test_environments_allowed():
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="uat")  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="staging")  # type: ignore[arg-type]

def test_default_model_and_langfuse_env_mapping():
    dev_settings = Settings(ENVIRONMENT="development", LANGFUSE_ENVIRONMENT="")
    prod_settings = Settings(ENVIRONMENT="production", LANGFUSE_ENVIRONMENT="")
    assert dev_settings.OPENAI_MODEL == "gpt-5.4-mini"
    assert dev_settings.LANGFUSE_MASK_INPUT_OUTPUT is False
    assert prod_settings.LANGFUSE_MASK_INPUT_OUTPUT is False

def test_bloat_files_and_models_removed():
    assert not (REPO_ROOT / "models").exists()
    assert not (REPO_ROOT / "apps/api/.env.uat").exists()
    assert not (REPO_ROOT / "deploy/docker-compose.enterprise.yml").exists()
    assert not (REPO_ROOT / "deploy/pgbouncer").exists()
    assert not (REPO_ROOT / "scripts/github_mcp_wrapper.sh").exists()
    assert not (REPO_ROOT / "temp").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_config_environments.py -v`
Expected: FAIL (`Settings(ENVIRONMENT="uat")` does not raise `ValidationError`, and `models/`, `apps/api/.env.uat`, etc. still exist).

- [ ] **Step 3: Delete root junk files, `models/`, enterprise deploy files, and obsolete scripts; update `config.py`, `pyproject.toml`, and `.env*` files**

1. Delete all files listed under `Delete:` for Task 1.
2. In `pyproject.toml` and `packages/core/pyproject.toml`, remove `onnxruntime`, `arq`, `mcp`, and `jinja2` dependencies.
3. In `apps/api/src/api/core/config.py`:
   - Change `ENVIRONMENT: Literal["development", "production", "test"] = "development"`
   - Change `OPENAI_MODEL: str = "gpt-5.4-mini"`
   - Change `LANGFUSE_MASK_INPUT_OUTPUT: bool = False` (do not force `True` in production validator; map default `LANGFUSE_ENVIRONMENT` to `"verischolar-dev"` for `development` and `"verischolar-prod"` for `production`)
   - Add `SENTRY_DSN: str | None = None` and `ALERT_WEBHOOK_URL: str | None = None`
4. Update `.env.example`, `apps/api/.env.example`, `apps/api/.env.development`, `apps/api/.env.production`, and `deploy/systemd/verischolar-api.service` to match.
5. Remove deleted runner imports (`get_documents_export_pdf`, `post_session_export_bundle`, `notes_and_synthesis_runner`) from `scripts/eval_api.py`, `scripts/eval/run_eval.py`, `scripts/eval/runners/__init__.py`, and `scripts/README.md`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_config_environments.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore(cleanup): remove root junk, 530MB ONNX model, uat/enterprise configs, and dead scripts"
```

---

### Task 2 (Member 2 — `w1:p2`): `packages/core` Out-of-Scope Domain, Ports, Services, MCP, Prompts & Eval Removal

**Files:**
- Delete:
  - `packages/core/src/core/domain/entities/safe_claim.py`
  - `packages/core/src/core/domain/entities/note_synthesis.py`
  - `packages/core/src/core/domain/value_objects/pdf_annotation.py`
  - `packages/core/src/core/ports/safe_verifier.py`
  - `packages/core/src/core/ports/pdf_annotator.py`
  - `packages/core/src/core/ports/eval.py`
  - `packages/core/src/core/services/safe_fact_checker.py`
  - `packages/core/src/core/services/safe_nli_adapter.py`
  - `packages/core/src/core/mcp/` (`__init__.py`, `runtime_server.py`)
  - `packages/core/src/core/prompts/` (`__init__.py`, `template.py`, `documents/summary_grounded.v1.prompt.md`)
  - `packages/core/src/core/eval/` (all 20 files in `eval/`, `eval/adapters/`, `eval/evaluators/`, `eval/metrics/`)
  - `packages/core/tests/domain/test_safe_fact_checker.py`
  - `packages/core/tests/domain/test_safe_nli_adapter.py`
  - `packages/core/tests/domain/test_safe_nli_neural.py`
  - `packages/core/tests/domain/test_pdf_annotation.py`
  - `packages/core/tests/domain/test_mcp_runtime_server.py`
  - `packages/core/tests/eval/` (all 14 test files + fixtures)
  - `tests/evals/` (`test_eval_metrics.py`, `test_two_tier_eval.py`, `test_parse_chunking_eval.py`)
- Modify:
  - `packages/core/src/core/domain/entities/__init__.py`
  - `packages/core/src/core/domain/entities/reference.py`
  - `packages/core/src/core/ports/__init__.py`
  - `packages/core/src/core/ports/note.py`
  - `packages/core/src/core/services/__init__.py`
  - `packages/core/tests/domain/test_hexagonal_invariants.py`
- Test: `packages/core/tests/domain/test_hexagonal_invariants.py`

**Interfaces:**
- Consumes: Clean `packages/core/pyproject.toml` from Task 1
- Produces: Clean barrel exports in `core.domain.entities`, `core.ports`, and `core.services` with zero references to SAFE NLI, PDF annotation, Note synthesis, CitationEdge, MCP, or offline Eval adapters.

- [ ] **Step 1: Update `packages/core/tests/domain/test_hexagonal_invariants.py` with assertions that out-of-scope modules are absent and barrel imports succeed**

```python
import importlib
from pathlib import Path
import pytest

CORE_ROOT = Path(__file__).resolve().parents[2] / "src" / "core"

@pytest.mark.parametrize(
    "removed_module",
    [
        "core.domain.entities.safe_claim",
        "core.domain.entities.note_synthesis",
        "core.domain.value_objects.pdf_annotation",
        "core.ports.safe_verifier",
        "core.ports.pdf_annotator",
        "core.ports.eval",
        "core.services.safe_fact_checker",
        "core.services.safe_nli_adapter",
        "core.mcp.runtime_server",
        "core.eval",
        "core.prompts.template",
    ],
)
def test_out_of_scope_core_modules_removed(removed_module: str):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(removed_module)

def test_core_barrel_imports_clean():
    entities = importlib.import_module("core.domain.entities")
    ports = importlib.import_module("core.ports")
    services = importlib.import_module("core.services")
    assert not hasattr(entities, "AtomicClaim")
    assert not hasattr(entities, "NoteSynthesis")
    assert not hasattr(entities, "CitationEdge")
    assert not hasattr(ports, "INLIVerifierPort")
    assert not hasattr(ports, "IPdfAnnotatorPort")
    assert not hasattr(services, "SAFEFactChecker")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/domain/test_hexagonal_invariants.py -v`
Expected: FAIL (`ModuleNotFoundError` not raised because the out-of-scope modules still exist).

- [ ] **Step 3: Delete the 31 `packages/core` files + 22 obsolete test files and clean barrel exports**

1. Delete all files listed under `Delete:` for Task 2.
2. In `packages/core/src/core/domain/entities/reference.py`, remove `CitationRelation`, `CitationGraphScope`, and `CitationEdge` (keep `ExtractedReference`, `ParsedReferenceInfo`, `ResolvedAcademicReference`).
3. In `packages/core/src/core/domain/entities/__init__.py`, remove imports and `__all__` entries for `AtomicClaim`, `ClaimVerificationResult`, `DraftFactCheckReport`, `EvidencePassage`, `VerificationLabel`, `InteractiveCitationBadge`, `NoteSynthesis`, `SynthesisLanguage`, `SynthesisMode`, `CitationEdge`, `CitationGraphScope`, `CitationRelation`.
4. In `packages/core/src/core/ports/note.py`, remove `INoteSynthesisRepositoryPort`.
5. In `packages/core/src/core/ports/__init__.py`, remove imports and `__all__` entries for `IPdfAnnotatorPort`, `IClaimDecomposerPort`, `INLIVerifierPort`, `INoteSynthesisRepositoryPort`, `IDatasetAdapterPort`, `IEvaluatorPort`.
6. In `packages/core/src/core/services/__init__.py`, remove imports and `__all__` entries for `SAFEFactChecker`, `RegexClaimDecomposer`, `HeuristicNLIVerifier`, `DeBERTaNLIAdapter`.

- [ ] **Step 4: Run all `packages/core` tests to verify they pass**

Run: `uv run pytest packages/core/tests -v`
Expected: PASS (100% of remaining `packages/core/tests` pass).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(core): remove SAFE NLI, PDF annotator, note synthesis, MCP, and eval bloat"
```

---

### Task 3 (Member 2 — `w1:p2`): `apps/api` Out-of-Scope DB Models, Services, Schemas & 18 Endpoints Removal

**Files:**
- Delete:
  - `apps/api/src/api/services/associative_memory_service.py`
  - `apps/api/src/api/services/note_synthesis_service.py`
  - `apps/api/src/api/adapters/pdf_annotator.py`
  - `apps/api/src/api/utils/email_validator.py`
  - `apps/api/src/api/workers/arq_worker.py`
  - `apps/api/tests/test_documents_export_pdf.py`
  - `apps/api/tests/test_draft_comments.py`
  - `apps/api/tests/test_notes_synthesize.py`
  - `apps/api/tests/test_golden_papers_matrix.py`
  - `apps/api/tests/test_backend_pillars_completion.py`
  - `apps/api/tests/test_m1_pillars_empirical_stress.py`
  - `apps/api/tests/run_all_api_tests.py`
- Modify:
  - `apps/api/src/api/__init__.py`
  - `apps/api/src/api/v1/endpoints/auth.py`
  - `apps/api/src/api/v1/endpoints/drafts.py`
  - `apps/api/src/api/v1/endpoints/folders.py`
  - `apps/api/src/api/v1/endpoints/documents.py`
  - `apps/api/src/api/v1/endpoints/sessions.py`
  - `apps/api/src/api/v1/endpoints/notes.py`
  - `apps/api/src/api/db/models/draft.py`
  - `apps/api/src/api/db/models/note.py`
  - `apps/api/src/api/db/models/reference.py`
  - `apps/api/src/api/db/models/__init__.py`
  - `apps/api/src/api/db/init_db.py`
  - `apps/api/src/api/services/draft_service.py`
  - `apps/api/src/api/services/library_synthesis_service.py`
  - `apps/api/src/api/services/document_service.py`
  - `apps/api/src/api/services/session_service.py`
  - `apps/api/src/api/schemas/draft.py`
  - `apps/api/src/api/schemas/folder.py`
  - `apps/api/src/api/schemas/note.py`
  - `apps/api/src/api/schemas/session.py`
  - `apps/api/tests/test_drafts_lifecycle.py`
  - `apps/api/tests/test_module4_folders.py`
  - `apps/api/tests/test_sessions_lifecycle.py`
  - `apps/api/tests/test_reference_ingestion.py`
- Test: `apps/api/tests/test_out_of_scope_endpoints_removed.py`

**Interfaces:**
- Consumes: Clean `packages/core` exports from Task 2
- Produces: Clean FastAPI `app` without the 18 out-of-scope routes and without `DraftCommentModel`, `NoteSynthesisModel`, `CitationEdgeModel` in `api.db.models`.

- [ ] **Step 1: Write the failing test in `apps/api/tests/test_out_of_scope_endpoints_removed.py`**

```python
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from api import create_app
import api.db.models as db_models

@pytest.mark.asyncio
async def test_removed_endpoints_not_registered():
    app = create_app()
    fake_id = str(uuid.uuid4())
    removed_routes = [
        ("POST", f"/api/v1/drafts/{fake_id}/verify-facts"),
        ("POST", f"/api/v1/drafts/{fake_id}/share"),
        ("GET", f"/api/v1/drafts/{fake_id}/share"),
        ("POST", f"/api/v1/drafts/{fake_id}/comments"),
        ("GET", f"/api/v1/drafts/{fake_id}/comments"),
        ("POST", f"/api/v1/drafts/{fake_id}:export-overleaf"),
        ("POST", f"/api/v1/drafts/{fake_id}/overleaf"),
        ("GET", f"/api/v1/drafts/{fake_id}/overleaf-launch"),
        ("POST", f"/api/v1/drafts/{fake_id}/associative-suggestions"),
        ("POST", "/api/v1/folders/comparison-matrix"),
        ("POST", f"/api/v1/folders/{fake_id}/comparison-matrix"),
        ("GET", f"/api/v1/documents/{fake_id}/export-pdf"),
        ("POST", f"/api/v1/sessions/{fake_id}:export-bundle"),
        ("GET", f"/api/v1/sessions/{fake_id}/citation-graph"),
        ("POST", "/api/v1/notes:synthesize"),
        ("GET", "/events"),
    ]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for method, path in removed_routes:
            resp = await client.request(method, path)
            assert resp.status_code in (404, 405), f"Expected 404/405 for {method} {path}, got {resp.status_code}"

def test_removed_db_models_absent():
    assert not hasattr(db_models, "DraftCommentModel")
    assert not hasattr(db_models, "NoteSynthesisModel")
    assert not hasattr(db_models, "CitationEdgeModel")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_out_of_scope_endpoints_removed.py -v`
Expected: FAIL (endpoints return 401/422 instead of 404/405, and deleted ORM models still exist on `api.db.models`).

- [ ] **Step 3: Delete the 5 `apps/api` files, 3 DB models, 18 endpoints, unused schemas/service methods, and obsolete test cases**

1. Delete all files listed under `Delete:` for Task 3 (`associative_memory_service.py`, `note_synthesis_service.py`, `adapters/pdf_annotator.py`, `utils/email_validator.py`, `workers/arq_worker.py`, and the 4 deleted test files).
2. Remove `DraftCommentModel` (`db/models/draft.py`), `NoteSynthesisModel` (`db/models/note.py`), and `CitationEdgeModel` (`db/models/reference.py`), and remove their registrations in `db/models/__init__.py` and `db/init_db.py`.
3. Remove the 18 endpoints from `drafts.py`, `folders.py`, `documents.py`, `sessions.py`, `notes.py`, and `src/api/__init__.py` (`GET /events`). In `auth.py`, remove `"uat"` from `is_dev_or_uat`.
4. Remove the corresponding methods and imports in `draft_service.py` (`verify_draft_facts`, `get_overleaf_export_data`, `_fact_checker`, `_nli_adapter`, `_draft_shares_cache`), `library_synthesis_service.py` (`generate_comparison_matrix` and helpers), `document_service.py` (`export_annotated_pdf` and `PyMuPdfAnnotator` imports), and `session_service.py` (`export_bundle`, `get_citation_graph`, `_infer_citation_relation`, `CitationEdgeModel` writes).
5. Clean the corresponding schemas from `schemas/draft.py`, `schemas/folder.py`, `schemas/note.py`, and `schemas/session.py`.
6. Remove test cases calling deleted endpoints/models in `test_drafts_lifecycle.py`, `test_module4_folders.py`, `test_sessions_lifecycle.py`, `test_reference_ingestion.py`, `test_backend_pillars_completion.py`, and `test_m1_pillars_empirical_stress.py`.

- [ ] **Step 4: Run full Backend & Core test suite to verify everything passes**

Run: `uv run pytest apps/api/tests packages/core/tests -v`
Expected: PASS (0 failures, 0 errors).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(api): remove 18 out-of-scope endpoints, 3 DB models, and unused services"
```

---

### Task 4 (Member 3 — `w1:p4`): Frontend Routes, Global 4-Item Taskbar, & Dashboard/Reader/Notes Out-of-Scope UI Removal

**Files:**
- Delete:
  - `apps/web/playwright-screenshots/`
  - `apps/web/scripts/`
  - `apps/web/test-results.xml`
  - `apps/web/dist/`
  - `apps/web/src/features/auth/data/mock-auth.ts`
  - `apps/web/src/features/auth/data/mock-users.ts`
  - `apps/web/src/features/dashboard/components/ProjectsPage.tsx`
  - `apps/web/src/features/dashboard/components/DashboardCoworkView.tsx`
  - `apps/web/src/features/dashboard/components/DashboardCoworkView.test.tsx`
  - `apps/web/src/features/dashboard/components/DashboardProjectView.tsx`
  - `apps/web/src/features/dashboard/components/ModelSelectorModal.tsx`
  - `apps/web/src/features/dashboard/components/QuickUploadDocModal.tsx`
  - `apps/web/src/features/dashboard/api/sessionsApi.ts`
  - `apps/web/src/features/sessions/components/ExportBundleDialog.tsx`
  - `apps/web/src/features/notes/components/NotesPage.tsx`
  - `apps/web/src/features/notes/components/NoteSynthesisModal.tsx`
  - `apps/web/src/features/notes/components/SynthesizedLessonCard.tsx`
- Modify:
  - `apps/web/src/app/routes.tsx`
  - `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`
  - `apps/web/src/features/dashboard/components/DashboardTaskbar.test.tsx`
  - `apps/web/src/features/dashboard/components/ModularRoutesNavigation.test.tsx`
  - `apps/web/src/features/dashboard/components/DashboardContainer.tsx`
  - `apps/web/src/features/dashboard/components/DashboardHeroSection.tsx`
  - `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`
  - `apps/web/src/features/dashboard/components/DashboardWorkspace.test.tsx`
  - `apps/web/src/features/dashboard/components/WorkspaceToolsMenu.tsx`
  - `apps/web/src/features/dashboard/components/WorkspaceToolsMenu.test.tsx`
  - `apps/web/src/features/dashboard/data/mockDashboardData.ts`
  - `apps/web/src/features/dashboard/stores/useDashboardStore.ts`
  - `apps/web/src/features/dashboard/stores/useDashboardStore.test.ts`
  - `apps/web/src/features/dashboard/hooks/useDashboardQueries.ts`
  - `apps/web/src/features/dashboard/hooks/useDashboardSessions.ts`
  - `apps/web/src/features/discovery/components/DiscoveryPage.tsx`
  - `apps/web/src/features/discovery/components/DiscoveryPage.test.tsx`
  - `apps/web/src/features/reader/components/ViewportOverflowMenu.tsx`
  - `apps/web/src/features/reader/components/ViewportOverflowMenu.test.tsx`
  - `apps/web/src/features/reader/components/ViewportControls.test.tsx`
  - `apps/web/src/features/reader/stores/useReaderStore.ts`
  - `apps/web/src/features/reader/stores/useReaderStore.test.ts`
  - `apps/web/src/features/documents/api/documentsApi.ts`
  - `apps/web/src/features/documents/api/documentsApi.test.ts`
  - `apps/web/src/features/sessions/api/sessionsApi.ts`
  - `apps/web/src/features/sessions/api/sessionsApi.test.ts`
  - `apps/web/src/features/sessions/hooks/useSessionsQuery.ts`
  - `apps/web/src/features/notes/components/NotesPanelContainer.tsx`
  - `apps/web/src/features/notes/api/notesApi.ts`
  - `apps/web/src/features/notes/api/notesApi.test.ts`
  - `apps/web/src/features/notes/hooks/useNotesQuery.ts`
  - `apps/web/src/features/auth/components/AccountSettingsModal.tsx`
  - `apps/web/src/types/dashboard.ts`
- Test: `apps/web/src/features/dashboard/components/DashboardTaskbar.test.tsx`, `apps/web/src/features/dashboard/components/ModularRoutesNavigation.test.tsx`

**Interfaces:**
- Consumes: `docs/PRD/00-overview-and-cleanup.md` (§4 & §5)
- Produces:
  - `routes.tsx` without `/matrix`, `/library/matrix`, `/projects`, `/notes`, `/citations`
  - `DashboardTaskbar.tsx` rendering strictly the 4 MVP navigation items (`🔍 Khám phá & Phiên đọc`, `⭐ Kho Yêu thích`, `✍️ Soạn thảo LaTeX`, `👤 Tài khoản & Giao diện`)
  - Single consolidated `apps/web/src/features/sessions/api/sessionsApi.ts` without `exportSessionBundle` or `getCitationGraph`

- [ ] **Step 1: Update `DashboardTaskbar.test.tsx` and `ModularRoutesNavigation.test.tsx` to assert strictly 4 taskbar items and absence of removed routes**

```tsx
// In DashboardTaskbar.test.tsx:
it("renders only the 4 MVP global navigation items and excludes Matrix, Projects, and standalone Notes", () => {
  render(<MemoryRouter><DashboardTaskbar /></MemoryRouter>);
  expect(screen.queryByText(/matrix|ma trận/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/projects|dự án/i)).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- src/features/dashboard/components/DashboardTaskbar.test.tsx src/features/dashboard/components/ModularRoutesNavigation.test.tsx`
Expected: FAIL (`DashboardTaskbar` still renders 7 items including Matrix/Projects/Notes).

- [ ] **Step 3: Delete the 13 out-of-scope Dashboard/Reader/Notes/Auth files and refactor callers**

1. Delete all 13 files listed under `Delete:` for Task 4.
2. In `apps/web/src/app/routes.tsx`, remove `/library/matrix`, `/matrix`, `/projects`, `/notes`, and `/citations` routes and their dead imports.
3. In `DashboardTaskbar.tsx`, reduce navigation items to the 4 MVP items (`research`/`discovery`, `library`, `writing`, and `account`/theme toggle at bottom).
4. In `DashboardContainer.tsx`, `DashboardHeroSection.tsx`, `useDashboardStore.ts`, `mockDashboardData.ts`, and `types/dashboard.ts`, remove `cowork` and `project` modes, `COWORK_SAMPLE_TASKS`, `AVAILABLE_MODELS`, and `ModelSelectorModal` — and ensure `DashboardContainer` renders both `DashboardHeroSection` and `HeroUploadDropzone` on the standby screen.
5. In `DashboardWorkspace.tsx`, `WorkspaceToolsMenu.tsx`, `ViewportOverflowMenu.tsx`, `documentsApi.ts`, `sessionsApi.ts`, and `useSessionsQuery.ts`, remove `ExportBundleDialog`, `exportSessionBundle`, `exportAnnotatedPdf`, and `getCitationGraph`. Point any imports of `features/dashboard/api/sessionsApi` to `features/sessions/api/sessionsApi`.
6. In `DiscoveryPage.tsx`, remove the 2-hop SVG citation graph (`getCitationGraph`).
7. In `NotesPanelContainer.tsx`, `notesApi.ts`, and `useNotesQuery.ts`, remove `NoteSynthesisModal`, `SynthesizedLessonCard`, and `synthesizeNotes` (`POST /notes:synthesize`).
8. In `AccountSettingsModal.tsx`, remove the Overleaf Cloud Bridge card from Connected Accounts.
9. In `useReaderStore.ts`, stop silently shifting out the oldest tab when `openDocumentIds.length >= 5` (enforce the 5-document cap without silent eviction).
10. Update the corresponding `.test.ts` / `.test.tsx` files listed under `Modify:`.

- [ ] **Step 4: Run Vitest on all modified Dashboard/Reader/Notes/Sessions/Documents test suites**

Run: `npm --prefix apps/web run test -- src/features/dashboard src/features/reader src/features/notes src/features/sessions src/features/documents src/features/discovery src/features/auth`
Expected: PASS (0 failures).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(web): standardize 4-item taskbar and remove cowork, projects, export-pdf/bundle, and note synthesis UI"
```

---

### Task 5 (Member 3 — `w1:p4`): Frontend Library Matrix & Writing Workspace (SAFE, Sharing, Comments, Overleaf, Associative Memory) Removal

**Files:**
- Delete:
  - `apps/web/src/features/library/components/ComparisonMatrixPage.tsx`
  - `apps/web/src/features/library/components/ComparisonMatrixModal.tsx`
  - `apps/web/src/features/library/components/ComparisonMatrixModal.test.tsx`
  - `apps/web/src/features/library/api/synthesisApi.ts`
  - `apps/web/src/features/library/api/synthesisApi.test.ts`
  - `apps/web/src/features/writing/components/DraftSharingModal.tsx`
  - `apps/web/src/features/writing/components/DraftSharingModal.test.tsx`
  - `apps/web/src/features/writing/components/DraftCommentsPane.tsx`
  - `apps/web/src/features/writing/components/DraftCommentsPane.test.tsx`
  - `apps/web/src/features/writing/components/AssociativeMemoryCard.tsx`
  - `apps/web/src/features/writing/components/AssociativeMemoryCard.test.tsx`
  - `apps/web/src/features/writing/components/SourceEvidenceModal.tsx`
  - `apps/web/src/features/writing/components/SourceEvidenceModal.test.tsx`
  - `apps/web/src/features/writing/components/SuggestionReviewPanel.tsx`
  - `apps/web/src/features/writing/components/SuggestionReviewPanel.test.tsx`
  - `apps/web/src/features/writing/components/WritingIconRail.tsx`
  - `apps/web/src/features/writing/components/WritingIconRail.test.tsx`
- Modify:
  - `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
  - `apps/web/src/features/library/api/foldersApi.ts`
  - `apps/web/src/features/library/api/foldersApi.test.ts`
  - `apps/web/src/features/library/hooks/useFolderQueries.ts`
  - `apps/web/src/features/library/types/index.ts`
  - `apps/web/src/features/documents/components/DocumentLibraryModal.tsx`
  - `apps/web/src/features/documents/components/DocumentLibraryModal.test.tsx`
  - `apps/web/src/features/writing/components/WritingWorkspace.tsx`
  - `apps/web/src/features/writing/components/WritingWorkspace.test.tsx`
  - `apps/web/src/features/writing/components/WritingHeaderBar.tsx`
  - `apps/web/src/features/writing/components/WritingHeaderBar.test.tsx`
  - `apps/web/src/features/writing/components/WritingSidebar.tsx`
  - `apps/web/src/features/writing/components/WritingSidebar.test.tsx`
  - `apps/web/src/features/writing/components/WritingEditorPane.tsx`
  - `apps/web/src/features/writing/components/WritingEditorPane.test.tsx`
  - `apps/web/src/features/writing/components/WritingAssistantPane.tsx`
  - `apps/web/src/features/writing/components/WritingAssistantPane.test.tsx`
  - `apps/web/src/features/writing/api/draftsApi.ts`
  - `apps/web/src/features/writing/api/draftsApi.test.ts`
  - `apps/web/src/features/writing/stores/useWritingStore.ts`
  - `apps/web/src/features/writing/stores/useWritingStore.test.ts`
  - `apps/web/src/features/writing/types/index.ts`
- Test: `apps/web/src/features/writing/api/draftsApi.test.ts`, `apps/web/src/features/writing/components/WritingHeaderBar.test.tsx`, `apps/web/src/features/library/api/foldersApi.test.ts`

**Interfaces:**
- Consumes: `docs/PRD/05-favorite-library-and-graphrag.md`, `docs/PRD/06-agentic-overleaf-writing.md`
- Produces:
  - `foldersApi.ts` without `generateComparisonMatrix`
  - `draftsApi.ts` without `verifyFacts`, `exportToOverleaf`, `getShareSettings`, `shareDraft`, `getComments`, `createComment`, `updateComment`, `deleteComment`, `getAssociativeSuggestions`
  - `useWritingStore.ts` and `WritingWorkspace.tsx` free of Share, Comments, SAFE Verify, Overleaf Sync, and Associative Memory state/UI

- [ ] **Step 1: Update `draftsApi.test.ts`, `foldersApi.test.ts`, and `WritingHeaderBar.test.tsx` to assert out-of-scope methods and buttons are gone**

```ts
// In draftsApi.test.ts:
it("does not expose removed out-of-scope draft API methods", () => {
  expect("verifyFacts" in draftsApi).toBe(false);
  expect("exportToOverleaf" in draftsApi).toBe(false);
  expect("shareDraft" in draftsApi).toBe(false);
  expect("getComments" in draftsApi).toBe(false);
  expect("getAssociativeSuggestions" in draftsApi).toBe(false);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- src/features/writing/api/draftsApi.test.ts src/features/library/api/foldersApi.test.ts src/features/writing/components/WritingHeaderBar.test.tsx`
Expected: FAIL (`verifyFacts`, `exportToOverleaf`, `generateComparisonMatrix`, and Share/Comments/Overleaf buttons still exist).

- [ ] **Step 3: Delete the 17 Library/Writing files and clean `LibraryWorkspaceView`, `DocumentLibraryModal`, `WritingWorkspace`, `WritingHeaderBar`, `WritingEditorPane`, `WritingAssistantPane`, `useWritingStore`, `draftsApi`, and `foldersApi`**

1. Delete all 17 files listed under `Delete:` for Task 5.
2. In `LibraryWorkspaceView.tsx`, `DocumentLibraryModal.tsx`, `foldersApi.ts`, `useFolderQueries.ts`, and `features/library/types/index.ts`, remove `ComparisonMatrixModal`, `generateComparisonMatrix`, and `ComparisonMatrix*` types.
3. In `draftsApi.ts`, `useWritingStore.ts`, and `features/writing/types/index.ts`, remove all functions, state slices, and types for SAFE fact-checking (`verifyFacts`, `lastVerifyResult`, `AtomicClaim`), Multi-user Sharing (`shareDraft`, `isShareModalOpen`), Inline Comments (`getComments`, `comments`, `isCommentsPaneOpen`), Overleaf external sync (`exportToOverleaf`), Associative Memory (`getAssociativeSuggestions`), and `SuggestionReviewPanel`.
4. In `WritingWorkspace.tsx`, `WritingHeaderBar.tsx`, `WritingEditorPane.tsx`, `WritingSidebar.tsx`, and `WritingAssistantPane.tsx`, remove all props, buttons, and modals for Share, Comments, Overleaf sync, Selection Verify/Comment, and static SAFE claim lists; standardize `WritingSidebar` around `main.tex`, `references.bib`, and `figures/`.
5. Update the corresponding unit tests in `features/writing/` and `features/library/`.

- [ ] **Step 4: Run full Frontend typecheck, test suite, and production build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS (all Vitest suites pass and `tsc -b && vite build` succeeds with 0 errors).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(web): remove comparison matrix, SAFE fact-check, draft sharing/comments, overleaf sync, and associative memory"
```

---

### Task 6 (Member 3 — `w1:p4`): Documentation Directory (`docs/`) Cleanup & Alignment with `docs/PRD/`

**Files:**
- Delete:
  - `docs/02-modules-and-features/README.md`
  - `docs/02-modules-and-features/prd.md`
  - `docs/02-modules-and-features/pillar-1-deep-reading.md`
  - `docs/02-modules-and-features/pillar-2-latex-writing.md` (or `pillar-2-collaborative-writing.md`)
  - `docs/02-modules-and-features/pillar-3-knowledge-capital.md` (or `pillar-3-knowledge-digest.md`)
  - `docs/02-modules-and-features/pillar-4-literature-matrix.md` (or `pillar-4-library-synthesis.md`)
  - `docs/02-modules-and-features/pillar-5-enterprise-stack.md`
  - `docs/04-operations-and-cicd/docker-enterprise-guide.md`
- Modify:
  - `README.md`
  - `docs/README.md`
  - `docs/01-architecture/README.md`
  - `docs/01-architecture/architecture-overview.md`
  - `docs/01-architecture/backend-techstack.md`
  - `docs/01-architecture/database-design.md`
  - `docs/01-architecture/api-specification.md`
  - `docs/01-architecture/ai-guardrails-and-rag.md`
  - `docs/01-architecture/prompt-management.md`
  - `docs/01-architecture/scholar-profile-and-identity.md`
  - `docs/01-architecture/directory-structure.md`
  - `docs/01-architecture/swagger-offline.md`
  - `docs/03-frontend-engineering/README.md`
  - `docs/03-frontend-engineering/frontend-architecture-and-standards.md`
  - `docs/03-frontend-engineering/directory-structure.md`
  - `docs/04-operations-and-cicd/README.md`
  - `docs/04-operations-and-cicd/logging-and-observability.md`
  - `docs/05-testing-and-qa/README.md`
  - `docs/05-testing-and-qa/testing-strategy.md`

**Interfaces:**
- Consumes: `docs/PRD/00-overview-and-cleanup.md` through `docs/PRD/07-monitoring-and-langfuse.md`
- Produces: Clean `docs/` hierarchy pointing to `docs/PRD/` as the Single Source of Truth, with `docs/02-modules-and-features/` and `docker-enterprise-guide.md` completely removed and **PostgreSQL + `pgvector`** (never Neo4j) documented everywhere.

- [ ] **Step 1: Verify current `docs/` violations via shell check**

Run: `test ! -d docs/02-modules-and-features && test ! -f docs/04-operations-and-cicd/docker-enterprise-guide.md`
Expected: FAIL (exit code 1 because `docs/02-modules-and-features` and `docker-enterprise-guide.md` still exist).

- [ ] **Step 2: Delete `docs/02-modules-and-features/` and `docs/04-operations-and-cicd/docker-enterprise-guide.md`**

Run: `rm -rf docs/02-modules-and-features docs/04-operations-and-cicd/docker-enterprise-guide.md`
Expected: Directories/files removed.

- [ ] **Step 3: Update `README.md`, `docs/README.md`, and `docs/01-architecture/*`, `docs/03-frontend-engineering/*`, `docs/04-operations-and-cicd/*`, `docs/05-testing-and-qa/*`**

1. Point `README.md` and `docs/README.md` to `docs/PRD/00-overview-and-cleanup.md` .. `07-monitoring-and-langfuse.md` as the Single Source of Truth, removing all links to `02-modules-and-features/` and `docker-enterprise-guide.md`.
2. In `docs/01-architecture/*`, remove all references to SAFE NLI DeBERTa, 100+ Paper Comparison Matrix, Overleaf Git sync, Draft comments/sharing, PgBouncer/Enterprise Docker, and **ensure GraphRAG is documented strictly on PostgreSQL + `pgvector` (`graph_nodes` and `graph_edges` tables), with zero mentions of Neo4j**.
3. In `docs/03-frontend-engineering/*`, `docs/04-operations-and-cicd/*`, and `docs/05-testing-and-qa/*`, remove references to deleted components/modals/tests and align observability docs with `docs/PRD/07-monitoring-and-langfuse.md` (`verischolar-dev`, `verischolar-prod`, `trace_id`, Langfuse + Sentry + Webhook).

- [ ] **Step 4: Verify `docs/` cleanliness and absence of forbidden terms**

Run: `test ! -d docs/02-modules-and-features && test ! -f docs/04-operations-and-cicd/docker-enterprise-guide.md && ! grep -rn -i "neo4j\|docker-enterprise-guide\|02-modules-and-features" README.md docs/01-architecture docs/03-frontend-engineering docs/04-operations-and-cicd docs/05-testing-and-qa docs/README.md`
Expected: PASS (exit code 0, zero matches).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs: remove obsolete 5-pillar docs and align architecture docs with MVP PRD"
```
