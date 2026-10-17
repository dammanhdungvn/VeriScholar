## 2026-10-16T12:56:45Z
You are Worker M1 Remediation for Milestone 1.
Your working directory is: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1_remediation.

Read:
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md (specifically section ## 2026-10-16T12:03:58Z)
- /home/VeriScholar/Workspace/VeriScholar/AGENTS.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_m1_remediation/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Tasks:
1. In apps/api/src/api/services/associative_memory_service.py (around line 163):
   Scope draft query by user_id:
   `draft_stmt = select(DraftModel).where((DraftModel.id == draft_id) & (DraftModel.user_id == user_id))`
2. In apps/api/src/api/services/library_synthesis_service.py:
   Sort and format import blocks (standard library -> third-party -> local) so `uv run ruff check` exits with 0 errors (I001 resolved).
3. In apps/web/src/features/writing/components/WritingWorkspace.tsx (lines 168-183):
   Replace hardcoded mock initial state (`assoc-1`, "Attention Is All You Need", 0.94) with `null`:
   `const [activeMemorySuggestion, setActiveMemorySuggestion] = useState<... | null>(null);`
4. Confirm `apps/api/src/api/services/draft_service.py:602` checks `if not draft or not role: raise KeyError(...)` and `apps/api/src/api/services/ai_tracing_service.py` handles `version`.
5. Enhance `apps/api/tests/test_m1_pillars_empirical_stress.py` with cross-tenant isolation test for associative memory empty payload fallback.

File Ownership:
- `apps/api/src/api/services/associative_memory_service.py`
- `apps/api/src/api/services/library_synthesis_service.py`
- `apps/web/src/features/writing/components/WritingWorkspace.tsx`
- `apps/api/tests/test_m1_pillars_empirical_stress.py`

Required Verifications:
- `uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py -v` (10/10 must pass)
- `uv run pytest apps/api/tests/test_backend_pillars_completion.py -v` (4/4 must pass)
- `uv run ruff check apps/api/src/api/services/library_synthesis_service.py apps/api/src/api/services/associative_memory_service.py apps/api/src/api/services/ai_tracing_service.py` (0 errors)
- `pnpm --prefix apps/web test src/features/writing src/features/library --run`
- `pnpm --prefix apps/web exec tsc -b`

Write your complete handoff report to:
/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1_remediation/handoff.md
Report via send_message to your caller.
