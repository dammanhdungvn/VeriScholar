# Cấu Trúc Thư Mục Backend & Hạt Nhân Lục Giác (Monorepo Hexagonal Architecture)

Tài liệu này định nghĩa cấu trúc tổ chức mã nguồn backend của **VeriScholar** dựa trên kiến trúc lục giác (**Hexagonal / Ports & Adapters Architecture**) và cấu trúc monorepo chuẩn (`uv workspace`) trong môi trường thực tế.

---

## 0. BẢNG THUẬT NGỮ KỸ THUẬT DÀNH CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

| Thuật ngữ chuyên ngành | Tên tiếng Anh đầy đủ | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Monorepo** | Monolithic Repository | Toàn bộ dự án (backend, frontend, thư viện dùng chung) được đặt chung trong một kho mã nguồn duy nhất trên Git, giúp đồng bộ mã nguồn và chia sẻ kiểu dữ liệu cực kỳ dễ dàng. |
| **Hexagonal Architecture** | Ports & Adapters Architecture | Kiến trúc lục giác: Tách biệt triệt để mã nguồn logic nghiệp vụ cốt lõi (Domain) khỏi các công nghệ bên ngoài (cơ sở dữ liệu, giao diện web, thư viện bên thứ ba). Logic nghiệp vụ không được phép biết nó đang chạy trên FastAPI hay PostgreSQL. |
| **Domain Core** | Pure Domain Layer | Trái tim của ứng dụng, chỉ chứa các thực thể (Entities), đối tượng giá trị (Value Objects) và quy tắc nghiệp vụ thuần túy bằng Python chuẩn (Zero I/O - không thực hiện ghi đĩa hay gọi mạng). |
| **Driving Adapter** | Inbound / Driving Adapter | Bộ điều hợp cổng vào: Thành phần nhận yêu cầu từ bên ngoài đưa vào hệ thống (ví dụ: FastAPI nhận HTTP request từ người dùng rồi gọi Service/Use Case xử lý). |
| **Driven Adapter** | Outbound / Driven Adapter | Bộ điều hợp cổng ra: Thành phần nhận lệnh từ Service để tương tác với thế giới bên ngoài (ví dụ: SQLAlchemy ghi dữ liệu vào PostgreSQL, Exa API tìm kiếm bài báo). |
| **Ports (Cổng)** | Inbound & Outbound Interfaces | Các bản hợp đồng trừu tượng (`ABC` trong Python) quy định các hàm mà tầng Domain cần để giao tiếp với bên ngoài, áp dụng nguyên lý Nghịch đảo phụ thuộc (Dependency Inversion). |
| **Safe Sandbox Isolation** | Kernel-level Sandbox Runtime | Cơ chế cách ly biên dịch mã lệnh: Kiểm tra hạ tầng an toàn trước khi thực thi, fail-closed khi thiếu quyền an toàn. |

---

## 1. CẤU TRÚC MONOREPO TOÀN CỤC THỰC TẾ

```text
/home/VeriScholar/Workspace/VeriScholar/
├── apps/
│   ├── api/                                  # Driving Adapter (Cổng vào): FastAPI Web & SSE Gateway
│   │   ├── src/
│   │   │   └── api/
│   │   │       ├── core/                     # Cấu hình Pydantic Settings, Structlog & Logging Engine
│   │   │       │   ├── config.py             # Quản lý biến môi trường (EXA_API_KEY, DATABASE_URL...)
│   │   │       │   └── logging.py            # Structlog JSON logging
│   │   │       ├── db/                       # SQLAlchemy 2.0 Async Session & ORM Models
│   │   │       │   ├── models/               # DocumentModel, SessionModel, DraftModel, ReferenceItemModel...
│   │   │       │   └── session.py            # Async engine & sessionmaker
│   │   │       ├── middleware/               # Pure ASGI Tracing Middleware (X-Request-ID, TTFB, HTTP 499 Disconnect)
│   │   │       │   └── tracing.py
│   │   │       ├── schemas/                  # Pydantic v2 Request / Response Envelopes
│   │   │       │   ├── document.py           # Schemas tài liệu, bóc tách reference
│   │   │       │   ├── draft.py              # Schemas bản thảo, peer review comments
│   │   │       │   ├── session.py            # Schemas phiên nghiên cứu, citation graph
│   │   │       │   └── envelope.py           # Single/Paginated Envelope chuẩn hóa
│   │   │       ├── services/                 # Application Services điều phối nghiệp vụ
│   │   │       │   ├── auth_service.py       # Quản trị xác thực & người dùng
│   │   │       │   ├── document_service.py   # Ingestion, Text extraction, Bounding boxes
│   │   │       │   ├── draft_service.py      # Lifecycle bản thảo, OCC, Peer Comments, SAFE Verification
│   │   │       │   ├── session_service.py    # Phiên đa bài báo, Ingestion <= 5 bài, Citation Graph
│   │   │       │   └── session_chat_service.py # Hỏi đáp đa bài báo streaming SSE
│   │   │       ├── v1/
│   │   │       │   └── endpoints/            # REST API Endpoints chuẩn AIP-136
│   │   │       │       ├── auth.py           # Đăng nhập, đăng ký
│   │   │       │       ├── documents.py      # Module 1: Upload, Chunks, Summary, Reference extraction
│   │   │       │       ├── drafts.py         # Module 2: Soạn thảo, OCC, Compile, SAFE Fact-checking, Comments
│   │   │       │       ├── notes.py          # Smart Notes & Highlight
│   │   │       │       └── sessions.py       # Module 3: Nạp bài phiên, Citation Graph, SSE Chat
│   │   │       ├── deps.py                   # Dependency Injection (CurrentUser, DB, Services)
│   │   │       └── main.py                   # FastAPI Application Entrypoint & Lifespan
│   │   └── tests/                            # API Integration & E2E Test Suite
│   │       ├── test_academic_resolver.py     # Module 3: Phân giải tham khảo qua API
│   │       ├── test_reference_ingestion.py   # Module 3: Nạp bài phiên & ngắt chu trình đồ thị
│   │       ├── test_draft_comments.py        # Module 2: Bình luận bản thảo ngang hàng
│   │       └── test_drafts_lifecycle.py      # Module 2: Vòng đời bản thảo & OCC
│   │
│   └── web/                                  # Driving Adapter (Giao diện): React 19 Frontend (Vite + Tailwind CSS)
│       ├── src/
│       │   ├── features/
│       │   │   ├── auth/                     # Quản lý đăng nhập & JWT tokens
│       │   │   ├── dashboard/                # Trang chủ phiên làm việc
│       │   │   ├── documents/                # API client & hooks quản trị tài liệu
│       │   │   ├── reader/                   # Module 1 & 3: PDF Canvas Viewer, SmartReferenceDrawer, Tabs
│       │   │   ├── sessions/                 # Quản trị phiên & citation graph API
│       │   │   └── writing/                  # Module 2: Soạn thảo tri-pane, OCC, Comments, SAFE Panel
│       │   ├── lib/                          # ApiClient, diffUtils, pdfRenderQueue
│       │   └── types/                        # TypeScript domain & API interfaces
│       └── package.json
│
├── packages/
│   └── core/                                 # Hạt Nhân Lục Giác Nghiệp Vụ (Pure Domain & Application Core)
│       ├── src/
│       │   └── core/
│       │       ├── domain/
│       │       │   └── entities/             # Pure Entities: Document, Chunk, Draft, Reference, Turn, Note
│       │       ├── ports/                    # Abstract Interfaces (Hợp đồng cổng trừu tượng)
│       │       │   ├── academic_resolver.py  # IAcademicSearchResolverPort (Module 3)
│       │       │   ├── safe_verifier.py      # ISafeVerifierPort & ISafeNliEnginePort (Module 2)
│       │       │   ├── latex.py              # ILatexCompilerPort & ILatexHealerPort (Module 2)
│       │       │   ├── retrieval.py          # IRetrievalPort & IRerankerPort (Module 1)
│       │       │   └── storage.py            # IStoragePort
│       │       └── services/                 # Adapters & Pure Domain Services
│       │           ├── academic_cache.py     # GlobalAcademicCache (SLA < 10ms, Public Cache Isolation)
│       │           ├── exa_resolver.py       # ExaAcademicResolverAdapter (Exa API + Fallback)
│       │           ├── safe_fact_checker.py  # SafeFactChecker engine
│       │           ├── safe_nli_adapter.py   # SafeNliEngineAdapter (Offline ONNX INT8 AVX2)
│       │           ├── latex_compiler.py     # Tectonic CLI Compiler
│       │           ├── latex_healer.py       # Agentic LaTeX Healer
│       │           ├── sandbox_probe.py      # SandboxRuntimeCapabilityProbe (Fail-Closed)
│       │           └── draft_asset_security.py # Asset extraction & Zip-slip defense
│       └── tests/                            # Unit test suite hạt nhân lục giác
│
├── models/
│   └── nli/                                  # Trọng số offline ONNX INT8 AVX2 (model_quint8_avx2.onnx)
│
├── docs/                                     # Toàn Bộ Hồ Sơ Tài Liệu Kỹ Thuật Dự Án
│   ├── vi/                                   # Đặc tả kỹ thuật, PRD, thiết kế API, kiến trúc
│   └── handoff/                              # Báo cáo nghiệm thu độc lập & hồ sơ bàn giao
│
├── pyproject.toml                            # Cấu hình gốc Monorepo uv Workspace
└── AGENTS.md                                 # Quy chuẩn & Điều luật kỹ thuật bắt buộc cho kỹ sư / AI Agents
```

---

## 2. QUY TẮC PHÂN CHIA RANH GIỚI BẤT BIẾN (HEXAGONAL BOUNDARIES)

1. **Ranh giới tầng Domain (`packages/core/src/core/domain`):** 
   - Tuyệt đối không import bất kỳ thư viện bên ngoài nào (chỉ dùng standard library và Pydantic v2 core).
   - Zero I/O: Không thực hiện ghi đĩa, gọi mạng hay phụ thuộc vào FastAPI/SQLAlchemy.
2. **Ranh giới tầng Ports (`packages/core/src/core/ports`):** 
   - Chứa các bản thiết kế trừu tượng (`ABC` - Abstract Base Class).
   - Chỉ định nghĩa tên hàm, kiểu dữ liệu đầu vào và đầu ra; tuyệt đối không chứa mã cài đặt cụ thể liên quan đến SQL hay HTTP.
3. **Ranh giới tầng Services / Adapters (`packages/core/src/core/services`):** 
   - Cài đặt cụ thể các hành vi mà các Ports đã cam kết (ví dụ `ExaAcademicResolverAdapter` gọi Exa, `SafeNliEngineAdapter` nạp ONNX runtime).
4. **Ranh giới tầng Giao tiếp API (`apps/api`):** 
   - Đóng vai trò là Driving Adapter (Cổng vào) phụ thuộc vào `packages/core`.
   - Chịu trách nhiệm định tuyến HTTP (`v1/endpoints/`), xác thực dữ liệu gửi lên từ người dùng (`schemas/`), kiểm soát phiên giao dịch DB (`db/`), và trả về Envelope chuẩn hóa.
