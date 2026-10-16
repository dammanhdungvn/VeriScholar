## 2026-10-15T02:26:55Z
From: a2173842-299f-4803-8153-e166837e5cde (parent)
Mission: Survey PDF corpus & 25 test cases Regression Set, and Playwright E2E Auth Fixture in apps/web.
1. Corpus & Regression Set:
   - Investigate repository for PDF files or assets representing: "Attention Is All You Need" (Vaswani et al.), "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al.), and "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al.).
   - Where are documents stored or ingested? If actual PDFs are present or need to be stored in an assets / fixture directory (e.g. packages/core/tests/fixtures/corpus or apps/api/tests/fixtures).
   - Design the 25 deep test cases for the Project Regression Set across the 3 papers:
     * Complex multi-column layout & figures/tables
     * Mathematical formulas (e.g. Attention equation, LoRA rank decomposition equation)
     * Cross-reference grounding & normalized BoundingBox validation
     * Semantic queries vs keyword queries (hybrid retrieval)
     * Negative queries / out-of-document claims
2. Playwright E2E Auth Fixture in apps/web:
   - Examine apps/web structure (Next.js / Vite / React, Playwright config, existing e2e tests).
   - How authentication is implemented in apps/web and apps/api (session, JWT, Supabase, OAuth, or mock auth).
   - How to create a reusable Playwright E2E Auth fixture (page fixture or worker fixture) that allows authenticated E2E tests without manual UI login on every run.
   - How the web UI interacts with SSE streaming and Deep Reader (verifying X-Request-ID propagation and bounding box highlight rendering).
