# Task Assignment: Worker M1 (Frontend Vitest CI Quality Gate)

## Identity
- Role: Worker (Frontend CI Implementation)
- Working directory: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1
- Exclusive Write Ownership: `apps/web/vite.config.ts`, `.github/workflows/ci.yml` (frontend-checks and detect-changes jobs)

## Mandatory Reading
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1/survey_report.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1/handoff.md`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Objective
Implement Requirement R1:
1. In `apps/web/vite.config.ts`:
   - Set `pool: 'vmThreads'` in the Vitest `test` configuration to eliminate the 278s JSDOM re-creation overhead and achieve the ~34s runtime benchmark.
   - Configure reporters: support JUnit XML reporting (`default` + `junit`, `outputFile: 'test-results.xml'`).
2. In `.github/workflows/ci.yml`:
   - Update `detect-changes` paths-filter so changes to `.github/workflows/ci.yml` trigger `frontend-checks`.
   - In `frontend-checks` job:
     - Update the Vitest test step to: `pnpm test:run --reporter=default --reporter=junit --outputFile=test-results.xml`.
     - Add `actions/upload-artifact@v4` step with `name: frontend-test-results`, `path: apps/web/test-results.xml`, and `if: always()`.
     - Ensure any test failure returns exit code 1, which fails the job and blocks PR merge.
3. Verification:
   - Run `pnpm test:run --reporter=default --reporter=junit --outputFile=test-results.xml` in `apps/web`. Verify 378/378 tests pass and `apps/web/test-results.xml` is valid XML.
   - Run `pnpm build` in `apps/web`.
   - Validate YAML syntax of `.github/workflows/ci.yml`.
4. Document all changes and test outputs in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1/handoff.md`.


## 2026-10-17T04:11:42Z
[Message] timestamp=2026-10-17T04:11:42Z sender=037f66b3-4056-4a88-a7ee-29473f69a483 priority=MESSAGE_PRIORITY_HIGH content=You are worker_m1.
Your working directory is /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1.
Your task assignment is in /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1/DISPATCH.md.

MANDATORY READING:
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1/survey_report.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Task:
Implement Requirement R1 (Frontend Vitest Quality Gate in CI):
1. In `apps/web/vite.config.ts`:
   - Configure `pool: 'vmThreads'` in the Vitest `test` config to enable fast execution (~34s instead of 278s).
   - Configure reporters to support JUnit XML (`test-results.xml`).
2. In `.github/workflows/ci.yml`:
   - Ensure changes to `.github/workflows/ci.yml` trigger `frontend-checks` under `detect-changes`.
   - Update `pnpm test:run` step in `frontend-checks` to run with `--reporter=default --reporter=junit --outputFile=test-results.xml`.
   - Add artifact upload step (`actions/upload-artifact@v4`) with `name: frontend-test-results`, `path: apps/web/test-results.xml`, and `if: always()`.
3. Run verification:
   - Run `pnpm test:run --reporter=default --reporter=junit --outputFile=test-results.xml` in `apps/web`.
   - Run `pnpm build` in `apps/web`.
   - Validate `.github/workflows/ci.yml` YAML syntax.
4. Write your full report in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1/handoff.md` and send a completion message back.
