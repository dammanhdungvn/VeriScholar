## 2026-10-16T12:24:33Z
You are Worker M1 for Milestone 1 (M1_WRITING_AND_SYNTHESIS).
Your working directory is: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1.

Read:
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md (specifically section ## 2026-10-16T12:03:58Z)
- /home/VeriScholar/Workspace/VeriScholar/AGENTS.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_survey_pillar2_3/handoff.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_survey_pillar4/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Tasks:
1. Pillar 2 (Overleaf 1-Click Sync):
   - Verify `POST /api/v1/drafts/{id}:export-overleaf` generates valid Overleaf launch URL and snippet form data.
   - Verify Frontend Writing Workspace provides "Đồng bộ Overleaf (1-Click)" button (`data-testid="header-overleaf-btn"` in `WritingHeaderBar.tsx`) opening draft directly in Overleaf.
2. Pillar 3 (Proactive Scholarly Associative Memory):
   - In `apps/web/src/features/writing/api/draftsApi.ts`:
     Add `getAssociativeSuggestions(id: string, payload: { content?: string; text?: string; limit?: number; min_similarity?: number })` calling `POST /drafts/${id}/associative-suggestions`.
   - In `apps/web/src/features/writing/components/WritingWorkspace.tsx`:
     Wire `getAssociativeSuggestions` so the floating `AssociativeMemoryCard` proactively suggests relevant historical notes and allows one-click citation insertion (`data-testid="insert-citation-btn"`).
3. Pillar 4 (Multi-Paper Synthesis & Comparison Matrix):
   - In `apps/api/src/api/core/config.py`:
     Expose `REDIS_URL: str = "redis://localhost:6379/0"` in `Settings`.
   - In `apps/api/src/api/deps.py`:
     Initialize `RedisIdempotencyAdapter(redis_url=settings.REDIS_URL)` with fallback to in-memory adapter.
   - In `apps/api/src/api/services/library_synthesis_service.py`:
     Implement Redis caching for extracted comparison matrix rows using Redis key `matrix:cache:{user_id}:{folder_id or 'global'}:{hash}` with TTL=3600s, returning cached rows on pagination and search requests without reparsing raw documents every time.
   - In `apps/web/src/features/library/types/index.ts`:
     Add `total_count?: number`, `limit?: number`, `offset?: number`, `search?: string` to `ComparisonMatrixRequest` and `ComparisonMatrixResponse`.
   - In `apps/web/src/features/library/components/ComparisonMatrixModal.tsx`:
     Pass `limit: 200` in matrix generation payload so 100+ papers are fully retrieved and rendered without truncation to default limit 50.

File Ownership:
- `apps/web/src/features/writing/api/draftsApi.ts`
- `apps/web/src/features/writing/components/WritingWorkspace.tsx`
- `apps/api/src/api/core/config.py`
- `apps/api/src/api/deps.py`
- `apps/api/src/api/services/library_synthesis_service.py`
- `apps/web/src/features/library/types/index.ts`
- `apps/web/src/features/library/components/ComparisonMatrixModal.tsx`

Required Verifications:
- `uv run pytest apps/api/tests/test_backend_pillars_completion.py -v`
- `pnpm --prefix apps/web test src/features/writing`
- `pnpm --prefix apps/web test src/features/library/components/ComparisonMatrixModal.test.tsx`
- `pnpm --prefix apps/web exec tsc -b`

Write a complete handoff report to:
`/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1/handoff.md`
Report your completion and summary to your caller via `send_message`.
