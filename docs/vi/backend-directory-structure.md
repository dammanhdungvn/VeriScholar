# Cấu Trúc Thư Mục Backend & Hạt Nhân Lục Giác (Monorepo Hexagonal Architecture)

Tài liệu này định nghĩa cấu trúc tổ chức mã nguồn backend của **VeriScholar** dựa trên kiến trúc lục giác (**Hexagonal / Ports & Adapters Architecture**) và cấu trúc monorepo chuẩn (`uv workspace`) đã được đóng băng trong [design-architecture.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md).

---

## 1. CẤU TRÚC MONOREPO TOÀN CỤC

```text
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/
├── apps/
│   ├── api/                                  # Driving Adapter: FastAPI Web & SSE Gateway
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── core/                     # Cấu hình Pydantic Settings, Structlog & Logging Engine
│   │   │   │   │   ├── config.py
│   │   │   │   │   └── logging.py
│   │   │   │   ├── middleware/               # Pure ASGI Tracing Middleware (TTFB, Client Disconnect 499)
│   │   │   │   │   └── tracing.py
│   │   │   │   ├── routes/                   # 59 RESTful Endpoints (Google Cloud AIP-136 Custom Verbs)
│   │   │   │   │   └── v1/
│   │   │   │   │       ├── documents.py      # Module 1: Upload, Chunks, Summaries, Notes
│   │   │   │   │       ├── drafts.py         # Module 2: Drafting, Sandbox Compile SSE, SAFE Fact-Check
│   │   │   │   │       ├── references.py     # Module 3: Reference Resolve, Citation Graph 2-hop
│   │   │   │   │       ├── library.py        # Module 4: Folders, Hierarchical RAG, Compare Matrix
│   │   │   │   │       ├── sessions.py       # Sessions: Viewport Sync, Turns, OCC, 30-day TTL
│   │   │   │   │       └── shares.py         # Sharing: Tokenized No-Auth Access, Revocation
│   │   │   │   ├── schemas/                  # Pydantic v2 Request / Response Envelopes
│   │   │   │   └── main.py                   # FastAPI Application Entrypoint & Lifespan
│   │   └── tests/                            # API Integration & E2E Test Suite
│   │
│   ├── worker/                               # Ingestion Worker Pool (Durable Task Queue Consumer)
│   │   ├── src/
│   │   │   ├── worker.py                     # Redis Streams Consumer Loop (Explicit ACK, DLQ)
│   │   │   └── tasks/                        # Layout Analysis, Chunking, BGE-M3 Dense Embedding
│   │   └── Dockerfile.worker
│   │
│   ├── sandbox-broker/                       # Dedicated Sandbox Microservice (Isolated Host / Node)
│   │   ├── src/
│   │   │   ├── server.py                     # gRPC / mTLS Server (Tách biệt với apps/api, cấm docker.sock)
│   │   │   ├── runner.py                     # gVisor (runsc) / Kata Containers Execution Engine
│   │   │   └── linter.py                     # AST Syntax Linter Pre-check Engine (Tier 1)
│   │   └── Dockerfile.sandbox
│   │
│   └── web/                                  # Driving Adapter: React 19 Frontend (Vite + Tailwind)
│
├── packages/
│   └── core/                                 # Pure Domain & Hexagonal Core Layer
│       └── src/
│           └── core/
│               ├── domain/                   # 100% Pure Python Entities & Value Objects (Zero I/O)
│               │   ├── models/               # Document, Chunk, Turn, Draft, Note, Edge, Folder, Share
│               │   ├── value_objects/        # BoundingBox [x0, y0, x1, y1, page], PageDimensions
│               │   └── exceptions/           # Domain Exceptions (Concurrency, Capacity, Validation)
│               │
│               ├── application/              # Inbound Ports & Use Cases (Business Workflows)
│               │   ├── ingestion/            # IngestDocumentUseCase, ParseDocumentUseCase
│               │   ├── qa/                   # AskSessionQuestionUseCase, EarlyConnectionReleaseStream
│               │   ├── drafting/             # CompileDraftSandboxUseCase, SelfHealingLoop, VerifySAFE
│               │   ├── citation/             # ResolveReferencesUseCase, QueryCitationGraphUseCase
│               │   ├── library/              # HierarchicalSynthesisUseCase, CompareMatrixUseCase
│               │   └── session/              # SyncViewportUseCase, RestoreArchivedUseCase
│               │
│               ├── ports/                    # Abstract Interfaces (Dependency Inversion)
│               │   ├── repositories.py       # IDocumentRepo, IChunkRepo, ISessionRepo, IDraftRepo
│               │   ├── queue.py              # ITaskQueueProducer (Redis Streams Interface)
│               │   ├── parsers.py            # IPDFParser, IStructureExtractor
│               │   ├── sandbox.py            # ISandboxBrokerClient (gRPC Interface)
│               │   ├── llm.py                # ILLMGateway, IEmbeddingEngine
│               │   └── storage.py            # IContentAddressableStorage (CAS Interface)
│               │
│               └── infrastructure/           # Driven Adapters (Concrete Implementations)
│                   ├── database/             # SQLAlchemy 2.0 Async Models, Repositories, Migrations
│                   ├── queue/                # Redis Streams Task Queue Producer Adapter
│                   ├── cache/                # Redis Idempotency & Leaky Bucket Limiter
│                   ├── parsers/              # PyMuPDF (fitz) Engine Adapter
│                   ├── sandbox/              # Sandbox Broker gRPC Client Adapter
│                   ├── llm/                  # Cost-Aware LLM Gateway Router (Local DMR / Cloud)
│                   └── storage/              # Local CAS File Storage with Ref-Counted Unlink
│
├── infra/                                    # Infrastructure as Code
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.sandbox
│   │   └── Dockerfile.web
│   ├── postgres/
│   │   └── init.sql                          # Database Extension Init (pgvector, uuid-ossp)
│   └── docker-compose.yml                    # Local Dev Stack (Postgres 16, Redis 7, DMR)
│
├── docs/                                     # Architecture & Engineering Specifications
│   └── vi/
│       ├── PRD.md                            # Product Requirements Document
│       ├── design-api.md                     # 59 Endpoints REST / SSE Specification
│       ├── design-database.md                # PostgreSQL 16 + pgvector DDL Schema
│       ├── design-architecture.md            # System & Software Architecture Blueprint
│       ├── guide-docker.md                   # Docker & PostgreSQL/pgvector Setup Guide
│       ├── guide-logging-system.md           # Structlog, Pure ASGI & Observability Guide
│       ├── backend-directory-structure.md    # Backend Monorepo Structure & Hexagonal Mapping
│       └── techstack-backend-module-01.md    # Technology Decisions & Trade-offs
│
├── pyproject.toml                            # uv Workspace Root Configuration
└── AGENTS.md                                 # Agent & Engineering Protocol
```

---

## 2. QUY TẮC PHÂN CHIA RANH GIỚI BẤT BIẾN (HEXAGONAL BOUNDARIES)

1. **`packages/core/src/core/domain`:** 
   - Tuyệt đối không import thư viện ngoài (chỉ dùng Python standard library và Pydantic v2 core).
   - Không phụ thuộc vào FastAPI, SQLAlchemy, Redis, hay bất kỳ adapter nào.
2. **`packages/core/src/core/application`:** 
   - Chỉ import từ `domain` và `ports`.
   - Điều phối nghiệp vụ qua các Inbound Ports (Use Cases).
3. **`packages/core/src/core/ports`:** 
   - Chứa các interface trừu tượng (`ABC`, `Protocol`) định nghĩa hợp đồng giao tiếp cho repositories, queue, sandbox broker, và LLM gateway.
4. **`packages/core/src/core/infrastructure`:** 
   - Hiện thực hóa các Driven Adapters kết nối với PostgreSQL (SQLAlchemy 2.0 Async), Redis, gRPC, PyMuPDF.
5. **`apps/api`:** 
   - Driving Adapter chỉ phụ thuộc vào `packages/core`. Chịu trách nhiệm routing, serialization, authentication, và response formatting.
