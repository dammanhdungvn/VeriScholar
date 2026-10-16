# E2E Test Infra: VeriScholar Module 1 AI Evaluation Benchmark

## Test Philosophy
- Opaque-box, requirement-driven. Derived from user request and domain invariants in AGENTS.md.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | F1: ASGI Tracing & Request ID State | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 2 | F2: SSE Streaming Headers & Event Trace | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 3 | F3: Hexagonal Evaluation Domain | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 4 | F4: Public Benchmarks (QASPER, SciFact, PubMedQA) | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 5 | F5: Project Regression Set (25 Cases) | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 6 | F6: Playwright E2E Auth Fixture | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 7 | F7: Web E2E Verification Tests | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 8 | F8: Dual-Track Benchmark Runner & CLI | ORIGINAL_REQUEST | 5 | 5 | ✓ |

## Test Architecture
- Test runner:
  - Backend and core eval tests: `uv run pytest`
  - Target eval suites: `uv run pytest packages/core/tests/eval/`, `uv run pytest tests/evals/`
  - Playwright E2E: `pnpm --prefix apps/web exec playwright test`
- Test case format:
  - Offline in-memory JSON fixtures (`packages/core/tests/eval/fixtures/`)
  - Standardized `EvalSample` Pydantic models
  - Golden paper regression matrix (`scripts/eval/data/project_regression_25.json`)
  - Playwright TypeScript spec files (`apps/web/tests/e2e/`)
- Directory layout:
  - `packages/core/tests/eval/`: 100% in-memory unit tests with zero network/DB dependencies.
  - `apps/api/tests/`: API integration tests for tracing, SSE streaming, and auth isolation.
  - `apps/web/tests/e2e/`: Browser E2E tests for authenticated UI, reader highlights, and SSE chat.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full QASPER PDF Question Answering with BBox Highlight | F3, F4, F6, F7 | High |
| 2 | SciFact Claim Verification with SUPPORT/CONTRADICT Rationale | F3, F4 | High |
| 3 | PubMedQA Biomedical Structured Abstract Decision | F3, F4 | High |
| 4 | Deep Regression on Attention Is All You Need (Equations + Multi-column) | F1, F2, F5, F7 | High |
| 5 | Deep Regression on LoRA (Matrix Decomposition + Zero Extra Latency) | F2, F5, F7 | High |
| 6 | Deep Regression on RAG (Dual Memory + DPR vs BART) | F2, F5, F7 | High |
| 7 | End-to-End Authenticated Web Session with SSE Streaming & Grounding Overlay | F1, F2, F6, F7 | High |

## Coverage Thresholds
- Tier 1: >=5 per feature (40 tests minimum across 8 features)
- Tier 2: >=5 boundary/corner tests per feature (40 tests minimum)
- Tier 3: Pairwise coverage across feature interactions (>=8 integration tests)
- Tier 4: >=7 realistic application scenarios
- **Total Minimum Threshold**: >=95 test cases across the system.
