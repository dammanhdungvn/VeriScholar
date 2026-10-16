# Local copy of verischolar-agent-protocol skill
# Original: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/verischolar-agent-protocol/SKILL.md

Essential engineering protocols, architectural laws, and domain invariants for VeriScholar.
- Atomic Evidence Invariant & Coordinate Norms: BoundingBox [x0, y0, x1, y1, page] (page >= 1, Top-Left (0,0))
- Zero DB Junk & Standby Flow
- Ingestion Idempotency (SHA-256)
- Monorepo Dependency Rule: apps/api -> packages/core, core NEVER imports from api or web
- Quality Gates: uv run ruff check ., uv run ruff format --check ., uv run pytest
