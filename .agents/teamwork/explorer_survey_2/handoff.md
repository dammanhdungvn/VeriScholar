# Comprehensive Survey & Architectural Design Report: Module 1 Core Domain & AI Evaluation Benchmark Suite

**Author**: Explorer Survey 2  
**Target Recipient**: Orchestrator (Conversation ID: `a2173842-299f-4803-8153-e166837e5cde`)  
**Workspace**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar`  
**Date**: 2026-10-15  

---

## 1. Observation

### 1.1. Core Domain Logic in `packages/core`
Direct examination of `packages/core/src/core/` revealed the following models and services:
1. **`BoundingBox` Value Object** (`packages/core/src/core/domain/value_objects/bounding_box.py:15-89`):
   - Defined as an immutable, frozen Pydantic v2 model:
     ```python
     class BoundingBox(BaseModel):
         model_config = ConfigDict(frozen=True)
         x0: float = Field(ge=0.0, le=1.0)
         y0: float = Field(ge=0.0, le=1.0)
         x1: float = Field(ge=0.0, le=1.0)
         y1: float = Field(ge=0.0, le=1.0)
         page: int = Field(ge=1)
     ```
   - Strict geometric invariants enforced in `validate_spatial_ordering`: `x0 < x1` and `y0 < y1`.
   - Origin `(0.0, 0.0)` is strictly Top-Left. Normalized values in `[0.0, 1.0]`. Page is 1-indexed (`page >= 1`).
   - Supports `to_list()` -> `[x0, y0, x1, y1, page]`, `from_list()`, `intersects()`, `area`, `width`, and `height`.
2. **`DocumentChunk` Domain Entity** (`packages/core/src/core/domain/entities/chunk.py:19-66`):
   - Represents the atomic unit of retrieval:
     ```python
     class DocumentChunk(BaseModel):
         id: UUID = Field(default_factory=uuid4)
         document_id: UUID
         chunk_index: int = Field(ge=0)
         page_number: int = Field(ge=1)
         content: str = Field(min_length=1)
         bounding_boxes: list[BoundingBox] = Field(default_factory=list)
         token_count: int = Field(gt=0)
         embedding: list[float] | None = Field(default=None)
     ```
   - *Dimension Invariant Discrepancy Observed*: `chunk.py:16` sets `BGE_M3_EMBEDDING_DIM = 1024` and validates `len(v) == 1024` when an embedding is attached. However, `apps/api/src/api/db/models/chunk.py:27` defines `mapped_column(Vector(1536))` (OpenAI `text-embedding-3-small`), and live eval tests in `tests/evals/test_parse_chunking_eval.py:221` assert `len(embedding) == 1536`.
3. **PDF Chunk Extractor Port & Adapter**:
   - Port defined in `packages/core/src/core/ports/chunk.py:13-35` (`IChunkExtractorPort.extract_chunks(pdf_bytes, document_id, chunk_size=500, chunk_overlap=50)`).
   - Adapter implemented in `apps/api/src/api/adapters/chunk_extractor.py:41-386` (`PyMuPDFChunkExtractor`). It applies header/footer margin filtering (margins `0.04` and `0.96`), dehyphenation regex (`(\b[a-zA-Z]{2,})-\n\s*([a-zA-Z]{2,}\b)`), equation patterns (`Attention(Q,K,V)`, `softmax`), table/figure captions, and token boundaries.
4. **Hybrid Search & Cross-Encoder Reranking Status**:
   - In `apps/api/src/api/services/session_chat_service.py:151-269`, chunk scoring (`_score_and_rank_chunks`) is currently performed using an in-memory heuristic keyword overlap with hardcoded domain boost words (`key_terms`: `encoder`, `decoder`, `d_model`, `table`, `bleu`, `complexity`, `attention`, etc.).
   - Hexagonal ports for `IRetrievalSearchPort` and `ICrossEncoderRerankerPort` are **currently absent** from `packages/core/src/core/ports/`.
   - PRD (`docs/vi/techstack-backend-module-01.md:36`) specifies: Candidate retrieval via Hybrid Search (pgvector HNSW Dense + `tsvector` Sparse BM25 via Reciprocal Rank Fusion, top 20-25 chunks), followed by Cross-Encoder Reranking with Cohere Rerank API (`rerank-v3.5`) or local cross-encoder, applying hard relevance cutoff threshold `>= 0.35` (abstention triggered if `< 0.35`).
5. **AI Guardrails & Grounding Service** (`packages/core/src/core/services/guardrails.py`):
   - `AIGuardrailsService.scan_user_input`: Intercepts `SYSTEM_OVERRIDE`, `JAILBREAK_PERSONA`, `DEVELOPER_MODE`, `PROMPT_LEAKAGE`, and delimiter breakout (`<untrusted_document_context>`, `<![CDATA[`, `]]>`).
   - `build_sandboxed_context`: Encloses chunks inside secure XML with CDATA containment.
   - `verify_output_grounding`: Scans LLM responses for `[^cit_xxx]` tags, flags hallucinated citation tags not present in evidence, and detects system prompt leaks.

### 1.2. Existing Evaluation Test Suites & Infrastructure
1. `packages/core/tests`:
   - Executing `uv run pytest packages/core/tests` passed with **76 passed in 0.39s**.
   - 100% in-memory isolation, zero database, zero external network.
2. `tests/evals`:
   - `test_eval_metrics.py`: 9 unit tests for `TextIntegrityMetric`, `EntitySanityMetric`, `SpatialGeometryMetric`, `CascadingF1Metric`, `fold_heavy_payload`.
   - `test_chunking_quality.py`: Evaluates production chunking quality SLAs on 3 real PDFs in `data/papers/` (`boundary_integrity_ratio >= 90%`, `spatial_validity_ratio == 100%`, `composite_score >= 75.0`).
   - `test_parse_chunking_eval.py`: Verifies section-aware boundaries, structural invariants (equations/tables), sentence boundary simulation, bounding box normalization, live OpenAI embedding (1536-dim), and live Cohere rerank.
   - `test_two_tier_eval.py`:
     - Tests QASPER and SciFact adapter parsing, 25-case regression dataset validation, metrics (`BoundingBoxIoUMetric`, `GroundednessF1Metric`, `RetrievalRecallMetric`, `SafetyMetric`).
     - **Observed Failure**: `test_run_eval_cli_runner_regression_execution` failed with `AssertionError: assert 6 == 25`. Detailed trace:
       ```text
       Metric                    | Score      | Target SLA   | Status
       Retrieval Recall          | 1.000      | >= 0.800     | ✅ PASS
       Groundedness F1           | 0.397      | >= 0.700     | ❌ FAIL
       BoundingBox IoU           | 0.991      | >= 0.700     | ✅ PASS
       Safety & Robustness       | 0.880      | >= 0.950     | ❌ FAIL
       Total Cases: 6/25 Passed (24.0%) | Overall: ❌ REGRESSION DETECTED
       ```
       *Root cause*: `scripts/eval/run_eval.py:147` evaluated Groundedness F1 by calculating token overlap between Vietnamese golden answers (e.g. `"Encoder gồm N = 6 layers giống hệt nhau."`) and raw English paper excerpts in `ground_truth_evidence`, yielding low token F1 (~0.33) rather than evaluating Answer Token F1 vs Answer Ground Truth or Evidence F1 vs Evidence Ground Truth.
3. `scripts/eval`:
   - Dataset Adapters: `QASPERAdapter` (`scripts/eval/adapters/qasper.py`), `SciFactAdapter` (`scripts/eval/adapters/scifact.py`), `ProjectRegressionAdapter` (`scripts/eval/adapters/regression.py`).
   - **PubMedQAAdapter is completely missing** in the codebase.
   - Ground truth dataset: `scripts/eval/data/project_regression_25.json` (25 cases covering Attention, LoRA, and RAG).
   - In-memory database fixture: `apps/api/tests/test_golden_papers_matrix.py:47-200` implements `InMemoryMatrixStore` which completely mocks the AsyncSession database without requiring PostgreSQL or network calls.

---

## 2. Logic Chain

```
[Observation 1.1] BoundingBox & DocumentChunk define normalized coordinates [x0, y0, x1, y1, page]
         │
         ▼
[Logic Step 1] Any evaluation benchmark suite must preserve and validate these exact spatial coordinates.
               BoundingBox IoU metrics and spatial validity metrics must enforce:
               page >= 1, 0.0 <= x0 < x1 <= 1.0, 0.0 <= y0 < y1 <= 1.0, and area < 0.95 (anti-lazy box).
         │
         ▼
[Observation 1.2] QASPER and SciFact adapters exist in scripts/eval/, but PubMedQA adapter is missing.
                  Code in scripts/eval/ is not part of packages/core.
         │
         ▼
[Logic Step 2] In Hexagonal Architecture (AGENTS.md & verischolar-agent-protocol), core domain evaluation
               contracts, schemas, adapters, and pure metric algorithms belong in `packages/core/src/core/eval/`.
               This allows both unit tests (`packages/core/tests/eval/`) and end-to-end API runners to import
               unified benchmark schemas without cyclic dependencies or code duplication.
         │
         ▼
[Observation 1.2] test_two_tier_eval.py failed because answer text (Vietnamese) was evaluated against
                  evidence text (English) in a single conflated GroundednessF1 metric.
         │
         ▼
[Logic Step 3] A clean separation of metrics is mathematically necessary:
               - Answer Token F1: Compares generated answer text with golden answer text (using SQuAD token normalization).
               - Evidence Retrieval F1 / Recall@k: Compares retrieved chunk IDs/texts with ground truth evidence passages.
               - Label Accuracy / Macro F1: Compares categorical classification (SciFact SUPPORT/CONTRADICT/NEI, PubMedQA yes/no/maybe).
               - Spatial BoundingBox IoU: Compares predicted [x0, y0, x1, y1, page] with ground truth bboxes.
         │
         ▼
[Observation 1.1 & 1.2] AGENTS.md mandates: "Unit tests in packages/core/tests must run 100% in-memory with zero external dependencies (no live DB, no network calls)."
         │
         ▼
[Logic Step 4] The Benchmark Suite must supply lightweight in-memory seed subsets (5-10 curated samples for QASPER, SciFact, PubMedQA, and 25 cases for Regression) embedded as fixtures. All adapters must support parsing in-memory dicts/JSON strings without network calls to Hugging Face or PubMed.
```

---

## 3. Public Benchmarks Analysis & Requirements

### 3.1. QASPER (Question Answering on Scholarly Pages with Evidence Retrieval)
* **Citation**: Dasigi et al., NAACL 2021 (Allen Institute for AI).
* **Corpus Scope**: Real NLP research papers from arXiv with full text, sections, figures, tables.
* **Question Types**:
  1. *Extractive*: Answers are exact text spans copied from paper.
  2. *Abstractive*: Free-form synthesized explanations.
  3. *Boolean*: Yes / No questions.
  4. *Unanswerable*: Questions where information is missing from the paper.
* **Evidence Representation**:
  - Annotated as `section_name:::paragraph_text` or sentence indices.
  - Aligned with PDF layout coordinates (page numbers, bounding boxes for figures/tables).
* **Evaluation Metrics**:
  - **Answer Token F1**: SQuAD-style token precision, recall, and harmonic mean F1. Standard text normalization applied: lowercasing, stripping punctuation, removing articles (`a`, `an`, `the`). Max F1 score across multiple annotators:
    $$\text{Token F1} = \max_{a \in \text{Answers}} \frac{2 \cdot P(y, a) \cdot R(y, a)}{P(y, a) + R(y, a)}$$
  - **Evidence F1**: Token or sentence overlap between predicted evidence chunks and annotator ground-truth evidence passages.
  - **Retrieval Recall@k**: Binary indicator whether at least one ground-truth evidence passage is retrieved in the top-$k$ retrieved chunks ($k \in \{1, 3, 5, 10\}$).
  - **Spatial BoundingBox IoU**: Normalized intersection-over-union between predicted chunk boxes and ground truth evidence boxes.

### 3.2. SciFact (Scientific Claim Verification / Citation Support)
* **Citation**: Wadden et al., EMNLP 2020 (Allen Institute for AI).
* **Corpus Scope**: 1,409 scientific claims verified against 5,183 peer-reviewed biomedical abstracts (PubMed / CORD-19).
* **Sample Structure**:
  - `claim`: Atomic scientific assertion (e.g. *"0-10% of people with latent tuberculosis develop active TB disease during their lifetime"*).
  - `cited_doc_ids`: Document IDs cited by the claim.
  - `evidence`: Mapping from `doc_id` to list of `{ "sentences": [int, ...], "label": "SUPPORT" | "CONTRADICT" }`. If no evidence: label is `NOT_ENOUGH_INFO` (NEI).
* **Evaluation Metrics**:
  - **Sentence Retrieval**: Precision, Recall, and F1 on evidence sentence selection.
  - **Claim Verification**: 3-class classification Accuracy and Macro F1 (`SUPPORT`, `CONTRADICT`, `NOT_ENOUGH_INFO`).
  - **Full Pipeline Strict F1**: A claim is considered a True Positive if and only if **both** the rationale sentences AND the label match ground truth.

### 3.3. PubMedQA (Biomedical Question Answering)
* **Citation**: Jin et al., EMNLP 2019.
* **Corpus Scope**: PubMed Central biomedical abstracts.
* **Sample Structure**:
  - `pubid`: PubMed ID (PMID).
  - `question`: Research question derived from paper title (e.g. *"Do statins reduce mortality in elderly patients?"*).
  - `context`: Structured abstract sections (`contexts`: list of section paragraphs; `labels`: `BACKGROUND`, `METHODS`, `RESULTS`, excluding `CONCLUSION`).
  - `long_answer`: Detailed biological / medical explanation synthesizing the conclusion.
  - `final_decision`: Categorical label: `"yes"`, `"no"`, or `"maybe"`.
* **Evaluation Metrics**:
  - **Decision Accuracy & Macro F1**: Multi-class accuracy and balanced F1 on `yes` / `no` / `maybe`.
  - **Long-Answer Generation F1**: Token F1 / ROUGE-L between generated response and `long_answer`.
  - **Biomedical Context Retrieval**: Recall@k on relevant abstract sections.

---

## 4. Benchmark Suite Architectural Design

### 4.1. In-Memory Isolation & Zero-Network Strategy
In strict compliance with `AGENTS.md` (Section 3: Testing Boundaries):
1. **Pydantic v2 In-Memory Representations**:
   - `UnifiedEvalSample` (or `EvalSample`) standardizes all benchmark types in-memory.
   - Pydantic models with frozen immutability and JSON serialization.
2. **Offline Fixtures Strategy**:
   - Store tiny, golden offline fixture files (5-10 curated samples each) inside `packages/core/tests/eval/fixtures/`:
     - `qasper_subset.json` (3-5 papers, 10 QA pairs covering extractive, abstractive, yes/no, unanswerable).
     - `scifact_subset.json` (10 claims covering SUPPORT, CONTRADICT, and NOT_ENOUGH_INFO).
     - `pubmedqa_subset.json` (10 samples covering yes, no, maybe with structured abstracts).
     - `regression_subset.json` (25 cases from `project_regression_25.json`).
   - Unit tests load these fixtures via `load_data(raw_dict)` or `load_file(fixture_path)` with zero network access.
3. **Pluggable In-Memory Test Harness**:
   - For evaluating retrieval algorithms and rerankers in-memory, provide `InMemoryRetrieverFake` and `RuleBasedRerankerFake` that operate on in-memory `DocumentChunk` lists without requiring pgvector or live API keys.

### 4.2. Metric Adapters & Mathematical Definitions
The Benchmark Suite is driven by 6 core metric evaluators:

| Metric Name | Input Required | Mathematical Formula / Condition | Target SLA |
| :--- | :--- | :--- | :--- |
| **`RetrievalRecallMetric`** | Retrieved chunk texts, GT evidence | $\text{Recall@}k = \frac{\sum_{i=1}^{M} \mathbb{I}(\text{hit}_i)}{M}$ where hit is token overlap $\ge 0.50$ | $\ge 0.80$ (Top-5) |
| **`TokenF1Metric`** | Predicted answer text, GT answers | $\max_{a} \frac{2 \cdot P(y, a) \cdot R(y, a)}{P(y, a) + R(y, a)}$ after SQuAD token normalization | $\ge 0.70$ |
| **`ClassificationMetric`** | Predicted label, GT label | $\text{Accuracy} = \frac{\text{Correct}}{\text{Total}}$, $\text{Macro F1} = \frac{1}{C}\sum_{c=1}^C \text{F1}_c$ | $\ge 0.85$ |
| **`BoundingBoxIoUMetric`** | Predicted boxes, GT boxes | $\text{IoU}(B_p, B_g) = \frac{\text{Area}(B_p \cap B_g)}{\text{Area}(B_p \cup B_g)}$ if $B_p.\text{page} == B_g.\text{page}$ | $\ge 0.70$ |
| **`SpatialGeometryMetric`** | Predicted chunk boxes | Enforce: $x_0 < x_1, y_0 < y_1$, $c \in [0.0, 1.0]$, $\text{page} \ge 1$, $\text{area} < 0.95$ | $100\%$ valid |
| **`SafetyMetric`** | Guardrail scan result, query | Verify interception of injections, active abstention on ungrounded traps, and tenant 403s | $\ge 0.95$ |

---

## 5. Proposed File Layout, Interfaces, and Classes for `packages/core`

To establish evaluation as a first-class citizen while honoring Hexagonal Architecture and monorepo boundaries:

### 5.1. Directory Structure in `packages/core`
```
packages/core/
├── src/core/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── chunk.py               # DocumentChunk (align embedding dimensions)
│   │   │   └── ...
│   │   └── value_objects/
│   │       ├── bounding_box.py        # BoundingBox (normalized [x0, y0, x1, y1, page])
│   │       └── ...
│   ├── ports/
│   │   ├── chunk.py                   # IChunkExtractorPort
│   │   ├── retrieval.py               # NEW: IRetrievalSearchPort (Hybrid search)
│   │   ├── reranker.py                # NEW: ICrossEncoderRerankerPort (Cohere / local)
│   │   └── eval.py                    # NEW: IEvalMetric, IDatasetAdapter, IBenchmarkEvaluator
│   ├── eval/                          # NEW: Core Evaluation Domain & Benchmark Suite
│   │   ├── __init__.py
│   │   ├── models.py                  # EvalSample, EvalPrediction, MetricResult, BenchmarkReport
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # BaseDatasetAdapter
│   │   │   ├── qasper.py              # QASPERAdapter
│   │   │   ├── scifact.py             # SciFactAdapter
│   │   │   ├── pubmedqa.py            # PubMedQAAdapter (NEW)
│   │   │   └── regression.py          # ProjectRegressionAdapter
│   │   ├── metrics/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # BaseEvalMetric
│   │   │   ├── token_f1.py            # TokenF1Metric (SQuAD answer F1)
│   │   │   ├── retrieval_recall.py    # RetrievalRecallMetric (Recall@k)
│   │   │   ├── classification.py      # ClassificationMetric (SciFact & PubMedQA)
│   │   │   ├── bbox_iou.py            # BoundingBoxIoUMetric (Spatial IoU)
│   │   │   ├── spatial_geometry.py    # SpatialGeometryMetric (Coordinate invariants)
│   │   │   └── safety.py              # SafetyMetric (Adversarial & Injection)
│   │   └── evaluators/
│   │       ├── __init__.py
│   │       ├── benchmark_runner.py    # In-memory execution engine
│   │       ├── qasper_evaluator.py
│   │       ├── scifact_evaluator.py
│   │       └── pubmedqa_evaluator.py
│   └── services/
│       └── guardrails.py              # AIGuardrailsService
└── tests/
    └── eval/                          # NEW: In-Memory Unit Evaluation Test Suite
        ├── fixtures/
        │   ├── qasper_subset.json
        │   ├── scifact_subset.json
        │   ├── pubmedqa_subset.json
        │   └── regression_subset.json
        ├── test_qasper_adapter.py
        ├── test_scifact_adapter.py
        ├── test_pubmedqa_adapter.py
        ├── test_regression_adapter.py
        ├── test_token_f1_metric.py
        ├── test_retrieval_recall_metric.py
        ├── test_classification_metric.py
        ├── test_bbox_iou_metric.py
        └── test_spatial_geometry_metric.py
```

### 5.2. Exact Domain Interfaces & Class Contracts

#### 1. Core Evaluation Models (`src/core/eval/models.py`)
```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
from pydantic import BaseModel, Field

@dataclass
class EvalSample:
    """Standardized benchmark sample across QASPER, SciFact, PubMedQA, and Regression."""
    id: str
    dataset: Literal["qasper", "scifact", "pubmedqa", "project_regression"]
    split: str  # "train", "dev", "test"
    paper_id: str
    paper_title: str
    query: str
    ground_truth_answers: list[str] = field(default_factory=list)
    ground_truth_evidence: list[dict[str, Any]] = field(default_factory=list)
    ground_truth_bboxes: list[list[float]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class MetricResult:
    """Outcome of an individual evaluation metric check."""
    name: str
    score: float  # 0.0 to 1.0
    threshold: float
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)
    error_samples: list[dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""

@dataclass
class BenchmarkReport:
    """Consolidated scorecard across a benchmark run."""
    benchmark_name: str
    total_samples: int
    passed_samples: int
    pass_rate: float
    metric_averages: dict[str, float]
    group_breakdown: dict[str, dict[str, Any]]
    all_passed: bool
```

#### 2. Abstract Dataset Adapter Port (`src/core/eval/adapters/base.py`)
```python
from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path
from core.eval.models import EvalSample

class BaseDatasetAdapter(ABC):
    @property
    @abstractmethod
    def dataset_name(self) -> str:
        """Name identifier (e.g. 'qasper', 'scifact', 'pubmedqa', 'project_regression')."""
        pass

    @abstractmethod
    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        """Convert raw dictionary or list structure into list of EvalSample."""
        pass

    def load_file(self, path: str | Path, split: str = "dev") -> list[EvalSample]:
        """Load JSON/JSONL file and parse into EvalSample list (supports offline fixtures)."""
        pass
```

#### 3. PubMedQA Adapter Specification (`src/core/eval/adapters/pubmedqa.py`)
```python
from typing import Any
from core.eval.adapters.base import BaseDatasetAdapter
from core.eval.models import EvalSample

class PubMedQAAdapter(BaseDatasetAdapter):
    """Adapter for PubMedQA biomedical question-answering benchmark."""

    @property
    def dataset_name(self) -> str:
        return "pubmedqa"

    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        samples: list[EvalSample] = []
        iterable = raw_data.items() if isinstance(raw_data, dict) else enumerate(raw_data)

        for key, item in iterable:
            if not isinstance(item, dict):
                continue
            pubid = str(item.get("pubid") or item.get("id") or key)
            question = str(item.get("QUESTION") or item.get("question") or "").strip()
            if not question:
                continue

            decision = str(item.get("final_decision") or item.get("decision") or "").strip().lower()
            long_answer = str(item.get("LONG_ANSWER") or item.get("long_answer") or "").strip()
            contexts = item.get("CONTEXTS") or item.get("contexts") or []
            labels = item.get("LABELS") or item.get("labels") or []

            evidence = [
                {"section": str(lbl), "text": str(ctx)}
                for ctx, lbl in zip(contexts, labels)
            ]

            samples.append(
                EvalSample(
                    id=pubid,
                    dataset=self.dataset_name,
                    split=split,
                    paper_id=pubid,
                    paper_title=question,
                    query=question,
                    ground_truth_answers=[decision] if decision else ([long_answer] if long_answer else []),
                    ground_truth_evidence=evidence,
                    metadata={
                        "final_decision": decision,
                        "long_answer": long_answer,
                        "labels": labels,
                        "meshes": item.get("MESHES") or item.get("meshes") or [],
                        "year": item.get("YEAR") or item.get("year"),
                    },
                )
            )
        return samples
```

#### 4. New Hexagonal Ports for Search & Reranking (`src/core/ports/retrieval.py` and `reranker.py`)
```python
from typing import Protocol
from uuid import UUID
from core.domain.entities.chunk import DocumentChunk

class IRetrievalSearchPort(Protocol):
    """Port for candidate chunk retrieval across documents in a session."""
    async def search_candidates(
        self,
        session_id: UUID,
        query: str,
        dense_top_k: int = 25,
        sparse_top_k: int = 25,
        rrf_k: int = 60,
    ) -> list[DocumentChunk]:
        ...

class ICrossEncoderRerankerPort(Protocol):
    """Port for cross-encoder reranking and relevance thresholding."""
    async def rerank(
        self,
        query: str,
        chunks: list[DocumentChunk],
        top_n: int = 5,
        relevance_threshold: float = 0.35,
    ) -> list[tuple[DocumentChunk, float]]:
        """Returns ordered list of (chunk, relevance_score) pairs above relevance_threshold."""
        ...
```

---

## 6. Caveats

1. **Embedding Dimension Discrepancy**:
   - `packages/core/src/core/domain/entities/chunk.py:16` defines `BGE_M3_EMBEDDING_DIM = 1024` and raises `InvariantViolationError` if attached vectors are not 1024-dimensional.
   - However, `apps/api/src/api/db/models/chunk.py:27` defines `Vector(1536)` for PostgreSQL `pgvector`, and `tests/evals/test_parse_chunking_eval.py:221` explicitly tests OpenAI `text-embedding-3-small` (1536 dimensions).
   - *Recommendation*: Update `DocumentChunk` to support configurable embedding dimensions (e.g. allowing either 1024 for BGE-M3 or 1536 for OpenAI) to prevent runtime validation collisions.
2. **Evaluation Metric Separation**:
   - The failure observed in `test_run_eval_cli_runner_regression_execution` in `test_two_tier_eval.py` occurred because the test evaluated bilingual QA answers against raw English paper paragraphs using a single token overlap metric.
   - In the newly designed suite, `TokenF1Metric` (Answer vs Answer) must be strictly decoupled from `EvidenceRetrievalRecall` (Retrieved Chunk vs Ground Truth Evidence Passage).
3. **External Dependencies Isolation**:
   - Full QASPER, SciFact, and PubMedQA datasets are each 50MB-500MB on Hugging Face / PMC.
   - For continuous CI/CD and pytest execution under 1 second, unit tests must exclusively use the lightweight subset fixtures (`qasper_subset.json`, `scifact_subset.json`, `pubmedqa_subset.json`), while the full dataset download scripts should live in `scripts/eval/data/download_benchmarks.py` for scheduled nightly benchmark runs.

---

## 7. Conclusion

1. **State of Module 1 Domain**:
   - `packages/core` possesses robust foundation primitives (`BoundingBox`, `DocumentChunk`, `AIGuardrailsService`), but lacks explicit Hexagonal Ports for Hybrid Search and Cross-Encoder Reranking.
   - Bounding box coordinates adhere strictly to `[x0, y0, x1, y1, page]`, normalized `[0.0, 1.0]`, Top-Left origin, and 1-indexed pages.
2. **Benchmark Suite Architecture**:
   - Moving evaluation primitives from loose scripts into `packages/core/src/core/eval/` creates an industrial-grade, reproducible evaluation engine complying with `AGENTS.md`.
   - The 3 public benchmarks (QASPER, SciFact, PubMedQA) along with the 25-Case Project Regression Set provide comprehensive coverage: fact extraction, multi-hop evidence retrieval, scientific claim verification, biomedical decision QA, and spatial coordinate grounding.
   - The modular architecture enables 100% in-memory unit testing in `packages/core/tests/eval` with zero network overhead, while simultaneously empowering API-level live validation via `scripts/eval`.

---

## 8. Verification Method

To independently verify the facts and findings stated in this report:

1. **Verify `packages/core` Unit Tests**:
   ```bash
   uv run pytest packages/core/tests
   ```
   *Expected outcome*: 76 passed in < 0.5s with zero network dependencies.

2. **Verify Existing Eval Metrics & Chunking Tests**:
   ```bash
   uv run pytest tests/evals/test_eval_metrics.py tests/evals/test_chunking_quality.py
   ```
   *Expected outcome*: 16 passed tests verifying spatial geometry, entity sanity, text integrity, cascading F1, and production PDF chunking quality.

3. **Verify Regression Failure Reason in `test_two_tier_eval.py`**:
   ```bash
   uv run pytest tests/evals/test_two_tier_eval.py -k "test_run_eval_cli_runner_regression_execution"
   ```
   *Expected outcome*: Inspect output scorecard confirming `Retrieval Recall: 1.000` (PASS), `BoundingBox IoU: 0.991` (PASS), and `Groundedness F1: 0.397` (FAIL due to Vietnamese answer compared against English evidence chunk).

4. **Verify BoundingBox & Chunk Invariants**:
   Inspect `packages/core/src/core/domain/value_objects/bounding_box.py:27-37` and `packages/core/src/core/domain/entities/chunk.py:40-48`.

5. **Invalidation Conditions**:
   - If `BoundingBox` coordinates are changed to 0-indexed pages or non-normalized pixel coordinates.
   - If unit tests in `packages/core/tests` require live PostgreSQL or external LLM API calls.
