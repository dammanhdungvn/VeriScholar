# Task Assignment: Survey Explorer 1 (CI & Frontend Vitest)

## Identity
- Role: Explorer (Frontend CI & Quality Gates)
- Working directory: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1

## Objective
Survey the VeriScholar codebase for Requirement R1:
- Inspect `.github/workflows/ci.yml` and any related CI workflows.
- Inspect frontend test setup in `apps/web` (or root): `package.json`, `vitest.config.ts`, test scripts (`pnpm test:run`, vitest reporters, junit options).
- Check the current 83 Vitest tests, test runner behavior, how junit XML is generated/configured, and how `frontend-checks` job is structured.
- Identify exact requirements, dependencies, and changes needed to satisfy R1 to Enterprise Production standard.
- Report all findings in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1/survey_report.md`.

## Mandatory Reading
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md`


## 2026-10-17T03:55:30Z
You are survey_explorer_1.
Your working directory is /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1.
Your task assignment is in /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1/DISPATCH.md.
MANDATORY: Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md first.

Survey the VeriScholar codebase focusing on Requirement R1:
1. Examine `.github/workflows/ci.yml` and related CI workflows.
2. Examine frontend setup in `apps/web/package.json`, test scripts, vitest config, Vitest test suite (83 tests), JUnit XML output reporter, and how `frontend-checks` job currently works.
3. Determine what exact changes are needed to integrate `pnpm test:run` with JUnit XML into `.github/workflows/ci.yml`, ensuring any failure fails PRs, and maintaining < 5 min CI run time with caching.
4. Document all findings and recommended architecture in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_1/survey_report.md`.
5. Write your handoff.md and send a completion message back with your report path.


## 2026-10-17T04:10:10Z
**Context**: Survey Phase - Requirement R1 (Frontend Vitest CI Quality Gate)
**Content**: Liveness check. Your progress.md was last updated at 03:56:00Z. Other survey agents (Docker CI and CD Spec Miner) have completed their surveys. Please update your current status and progress.
**Action**: Reply with your current status, update progress.md, and indicate remaining time to complete survey_report.md.
