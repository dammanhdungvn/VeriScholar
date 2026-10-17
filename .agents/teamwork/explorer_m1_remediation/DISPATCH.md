# Dispatch — Explorer M1 Remediation (Forensic Audit Remediation)

Target: Technical investigation and remediation strategy for Milestone 1 failures.

Input files:
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md` (read section ## 2026-10-16T12:03:58Z)
- `/home/VeriScholar/Workspace/VeriScholar/AGENTS.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md`
- Full Auditor Evidence Report: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/auditor_m1/handoff.md`
- Reviewer 1 Report: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/reviewer_1_m1/handoff.md`
- Reviewer 2 Report: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/reviewer_2_m1/handoff.md`
- Challenger 1 Report: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_1_m1/handoff.md`
- Challenger 2 Report: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_2_m1/handoff.md`

Output file:
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_m1_remediation/handoff.md`
## 2026-10-16T12:50:29Z
You are the Explorer for Milestone 1 Remediation.
Your working directory is: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_m1_remediation.

You are investigating the failure of Milestone 1 following an INTEGRITY VIOLATION verdict from the Forensic Auditor and REQUEST_CHANGES from Reviewers.
You MUST read the full evidence report from the Forensic Auditor and the other reviewers:
- Full Auditor Evidence Report: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/auditor_m1/handoff.md
- Reviewer 1 Report: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/reviewer_1_m1/handoff.md
- Reviewer 2 Report: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/reviewer_2_m1/handoff.md
- Challenger 1 Report: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_1_m1/handoff.md
- Challenger 2 Report: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_2_m1/handoff.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md (specifically section ## 2026-10-16T12:03:58Z)
- /home/VeriScholar/Workspace/VeriScholar/AGENTS.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md

Your mission:
Formulate a precise, surgical fix strategy addressing the exact defects identified:
1. `apps/api/src/api/services/draft_service.py:598-602`: Update `export_overleaf` to enforce role checking (`if not draft or not role: raise KeyError(...)`) so cross-tenant draft export is blocked with HTTP 404.
2. `apps/api/src/api/services/ai_tracing_service.py:558`: Fix the undefined name `version` in `AITracingService.trace()` to eliminate the runtime crash when Langfuse tracing is active.
3. `apps/api/src/api/services/associative_memory_service.py:161`: Scope the draft lookup by `user_id` (`where((DraftModel.id == draft_id) & (DraftModel.user_id == user_id))`).
4. `apps/api/src/api/services/library_synthesis_service.py`: Fix Ruff errors `I001` (import sorting) and `E501` (line length).
5. `apps/web/src/features/writing/components/WritingWorkspace.tsx:176`: Initialize `activeMemorySuggestion` to `null` instead of hardcoded mock state.
6. Check all affected tests including `apps/api/tests/test_m1_pillars_empirical_stress.py` to ensure 100% pass rate.

DO NOT recommend strategies that circumvent the audit or use dummy facades.
Write your complete remediation strategy to:
/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_m1_remediation/handoff.md
Report via send_message to your caller.
