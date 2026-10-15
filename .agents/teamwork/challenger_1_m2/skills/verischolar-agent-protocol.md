# VeriScholar Agent Protocol Summary
Source: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/verischolar-agent-protocol/SKILL.md

Core Methodology:
- BoundingBox: [x0, y0, x1, y1, page] where page is 1-indexed (page >= 1), coordinates are normalized [0.0, 1.0] with (0,0) Top-Left. 0.0 <= x0 < x1 <= 1.0, 0.0 <= y0 < y1 <= 1.0.
- DocumentChunk: unit of retrieval, preserves bounding boxes.
- Idempotency & SHA-256 for documents.
- In-memory isolation for unit tests (no network, no live DB).
- Dependency rule: core does not import api/web.
- Production quality gates: No swallowed exceptions, ruff clean, zero lint.
