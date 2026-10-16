# Progress — Explorer Survey 2

Last visited: 2026-10-15T02:35:45Z
Status: COMPLETED

## Tasks
- [x] Initialized workspace and briefing
- [x] Read relevant skills: verischolar-agent-protocol, eval-harness, scholar-evaluation
- [x] Investigate `packages/core` architecture & existing domain logic:
  - DocumentChunk, BoundingBox
  - PDF parsers (PyMuPDF, Docling)
  - Chunkers (IChunkExtractorPort, PyMuPDFChunkExtractor)
  - Hybrid search (dense + sparse / BM25)
  - Cross-encoder reranker (Cohere API, abstention threshold >= 0.35)
  - Grounding, citations, and LLM generation (AIGuardrailsService)
- [x] Inspect existing tests and eval infrastructure in `packages/core/tests`, `apps/api/tests`, and `tests/evals`
- [x] Deep-dive Public Benchmarks: QASPER, SciFact, PubMedQA
- [x] Design Benchmark Suite architecture, in-memory data structures, mock/subset datasets, and evaluator adapters
- [x] Specify detailed interfaces, classes, and file layout for `packages/core` eval module
- [x] Write 5-component `handoff.md` and notify parent
