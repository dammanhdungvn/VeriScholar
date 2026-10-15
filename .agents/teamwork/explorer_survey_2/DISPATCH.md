# Dispatch for Explorer Survey 2 (Module 1 Core Domain & Eval Harness)
Path to original request: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Working directory: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_2
## 2026-10-15T02:26:55Z
From: a2173842-299f-4803-8153-e166837e5cde
Priority: MESSAGE_PRIORITY_HIGH

You are explorer_survey_2.
Your working directory is: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_2
Read the original user request at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Also read the engineering guidelines in /home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md.

YOUR MISSION: Survey and investigate Module 1 (Scholar Reading & Deep Reader) domain logic in packages/core and the AI Evaluation Benchmark Suite requirements.
Specifically:
1. Examine packages/core: DocumentChunk, BoundingBox, PDF parsers, chunkers, hybrid search (dense + sparse), cross-encoder reranking, grounding, citations, and LLM generation.
2. Check existing evaluation infrastructure, eval harness, or test suites in packages/core/tests (and apps/api/tests if any).
3. Investigate the requirements for Public Benchmarks:
   - QASPER (Question Answering on Scholarly Pages with Evidence Retrieval): format, question types, evidence spans/bounding boxes, evaluation metrics (Token F1, Evidence F1, Retrieval Recall).
   - SciFact (Scientific claim verification / citation support): format, claims, evidence sentence/chunk retrieval, classification (SUPPORT, CONTRADICT, NOT_ENOUGH_INFO).
   - PubMedQA (Biomedical QA): format, context, long/short answers, yes/no/maybe label evaluation.
4. Design the architecture for the Benchmark Suite:
   - How to represent benchmark samples in-memory (Pydantic models / dataclasses) in compliance with in-memory isolation (AGENTS.md: zero external dependencies, no live network calls during unit eval tests).
   - Mock/cached benchmark datasets vs synthetic / subset datasets.
   - Evaluator adapters, metrics computation (Recall@k, Precision, Grounding F1, BoundingBox coordinate validation [page >= 1, normalized 0.0-1.0]).
5. Detail the exact interfaces, classes, and file layout needed in packages/core (and/or an eval package or module) to support comprehensive AI evaluation.

Write your comprehensive findings and recommendations to:
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_2/handoff.md
Update your progress.md in your working directory.
When complete, notify parent (conversation ID: a2173842-299f-4803-8153-e166837e5cde) via send_message with a summary and path to your handoff.md.
