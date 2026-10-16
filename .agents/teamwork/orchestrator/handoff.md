# Soft Handoff: Project Orchestrator (Succession to Generation 1)

## Milestone State
| Milestone | Status | Details |
|---|---|---|
| Phase 0: Survey | DONE | 3 Explorers mapped SSE/API, Core Eval domain, and Regression/Playwright. |
| Phase 1: Architecture | DONE | Published `PROJECT.md` and `TEST_INFRA.md`. |
| M1: M1_SSE_TRACING | DONE | Gate PASSED. All SSE endpoints emit `X-Request-ID` header and event payload. Full API suite (239 tests) passing. Forensic audit CLEAN. |
| M2: M2_PUBLIC_BENCHMARKS | IN_PROGRESS (NEEDS REMEDIATION) | Worker implemented domain models, adapters, decoupled metrics, and unit tests (182 core tests pass). Reviewer 1 & 2 delivered REQUEST_CHANGES with concrete remediation requirements. |
| M3: M3_REGRESSION_CORPUS | PLANNED | 25-case matrix designed across Attention, LoRA, and RAG. |
| M4: M4_PLAYWRIGHT_AUTH | PLANNED | Playwright config and two-tier `auth.fixture.ts` ready to implement in `apps/web`. |
| M5: M5_FINAL_ACCEPTANCE | PLANNED | Monorepo integration, CLI runner, and final adversarial audit. |

## Active Subagents
- All 15 spawned subagents from previous rounds are complete/idle. Clean slate for successor.

## Pending Decisions & Immediate Remediation Items for Successor (Milestone 2 Iteration 2)
The successor must immediately dispatch a Worker to apply these 4 critical fixes in `packages/core`:
1. **BenchmarkRunner** (`packages/core/src/core/eval/evaluators/benchmark_runner.py`):
   - Remove lines 178-207 that fabricated synthetic regression predictions with hardcoded strings. If `predictions` is omitted, raise ValueError or require predictions.
   - Remove line 146 that silently fell back to `sample.ground_truth_bboxes` when `pred_bboxes` was empty (`[]`). Empty prediction bboxes must remain empty so missing detections are truthfully penalized.
2. **SafetyMetric** (`packages/core/src/core/eval/metrics/safety.py`):
   - Remove line 105 that hardcoded `"28.4"` into general `refute_markers`. Refutation detection must rely on generic linguistic markers (`"không đúng"`, `"bác bỏ"`, `"sai"`, `"incorrect"`, `"refute"`, etc.).
3. **SpatialGeometryMetric** (`packages/core/src/core/eval/metrics/spatial_geometry.py`):
   - Add coordinate bounds check: `coord <= 1.0` (in addition to `coord >= 0.0`) for `x0`, `y0`, `x1`, `y1`. Unnormalized pixel coordinates (> 1.0) must trigger an anomaly.
4. **ClassificationMetric** (`packages/core/src/core/eval/metrics/classification.py`) & **PubMedQAAdapter** (`packages/core/src/core/eval/adapters/pubmedqa.py`):
   - In `ClassificationMetric.measure`: Reject empty predictions `""` (score 0.0). Enforce exact matching or strict normalized word-level match instead of loose substring matching.
   - In `PubMedQAAdapter`: `ground_truth_answers` must contain ONLY the categorical decision (`"yes"`, `"no"`, or `"maybe"`). The long answer explanation must reside strictly in `metadata["long_answer"]`.

After applying these 4 fixes, the successor must run the M2 Gate: Reviewers (2), Challengers (2), Auditor (1). When Gate passes -> mark M2 DONE and proceed to M3.

## Key Artifacts
- `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md` — Authoritative user intent
- `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/PROJECT.md` — Master project plan & feature inventory
- `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/TEST_INFRA.md` — E2E test infra & methodology
- `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/orchestrator/GATE_STATUS.md` — Gate history
- `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/reviewer_1_m2/handoff.md` — Detailed review findings
- `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/reviewer_2_m2/handoff.md` — Detailed review findings
