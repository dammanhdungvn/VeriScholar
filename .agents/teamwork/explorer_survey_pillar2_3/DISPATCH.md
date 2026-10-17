# Dispatch — Explorer Survey Pillar 2 & 3

Target: Survey Pillar 2 (Overleaf 1-Click Integration) and Pillar 3 (Proactive Scholarly Associative Memory).
Input files:
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md` (read section ## 2026-10-16T12:03:58Z)
- `/home/VeriScholar/Workspace/VeriScholar/AGENTS.md`
Output file:
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_survey_pillar2_3/handoff.md`
## 2026-10-16T12:08:20Z
Sender: 5237f63e-9b6a-4090-bcf4-69cfa8674802
Content:
You are Explorer 1 (Survey: Pillars 2 & 3).
Your working directory is: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_survey_pillar2_3.
Read:
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md (specifically section ## 2026-10-16T12:03:58Z)
- /home/VeriScholar/Workspace/VeriScholar/AGENTS.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_survey_pillar2_3/DISPATCH.md

Your mission:
Investigate the codebase for:
1. Pillar 2 (LaTeX Writing):
   - Current draft models, schemas, and endpoints in `apps/api` (e.g. `apps/api/src/api/v1/endpoints/drafts.py`, services, models).
   - How LaTeX generation or bibtex export currently functions.
   - Requirements for `POST /api/v1/drafts/{id}:export-overleaf` (generating valid Overleaf launch URL / snippet form data).
   - Frontend Writing Workspace in `apps/web` (where is the draft editor, buttons, toolbar, and where to add the 'Đồng bộ Overleaf (1-Click)' button).
2. Pillar 3 (Knowledge Capital & 2-Tier RAG):
   - User notes / annotations / research notes models and endpoints in `apps/api` and `packages/core`.
   - How semantic similarity or trigram similarity can be queried against user research notes.
   - Requirements for `POST /api/v1/drafts/{id}/associative-suggestions` returning relevant historical notes matching draft content.
   - Frontend Writing UI representation for the floating 'Spark of Insight' recommendation card with one-click citation insert.

Write your complete findings and verified evidence chains to /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_survey_pillar2_3/handoff.md.
Use `send_message` to report your completion and summary to your caller.
