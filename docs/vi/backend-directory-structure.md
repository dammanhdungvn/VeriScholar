# Cấu Trúc Thư Mục Backend & Hạt Nhân Lục Giác (Monorepo Hexagonal Architecture)

Tài liệu này định nghĩa cấu trúc tổ chức mã nguồn backend của **VeriScholar** dựa trên kiến trúc lục giác (**Hexagonal / Ports & Adapters Architecture - Kiến trúc phân tách phần mềm thành các cổng giao tiếp và bộ chuyển đổi**) và cấu trúc monorepo chuẩn (`uv workspace` - công cụ quản lý nhiều dự án Python trong cùng một kho mã nguồn) đã được đóng băng trong [design-architecture.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md).

---

## 0. BẢNG THUẬT NGỮ KỸ THUẬT DÀNH CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

Để giúp các kỹ sư mới (Fresher / Junior) nhanh chóng nắm bắt bản thiết kế mà không bị bỡ ngỡ trước các thuật ngữ chuyên ngành, bảng dưới đây giải thích ngắn gọn và trực quan các khái niệm cốt lõi:

| Thuật ngữ chuyên ngành | Tên tiếng Anh đầy đủ | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Monorepo** | Monolithic Repository | Toàn bộ dự án (backend, frontend, worker, thư viện dùng chung) được đặt chung trong một kho mã nguồn duy nhất trên Git, giúp đồng bộ mã nguồn và chia sẻ kiểu dữ liệu cực kỳ dễ dàng. |
| **Hexagonal Architecture** | Ports & Adapters Architecture | Kiến trúc lục giác: Tách biệt triệt để mã nguồn logic nghiệp vụ cốt lõi (Domain) khỏi các công nghệ bên ngoài (cơ sở dữ liệu, giao diện web, thư viện bên thứ ba). Logic nghiệp vụ không được phép biết nó đang chạy trên FastAPI hay PostgreSQL. |
| **Domain Core** | Pure Domain Layer | Trái tim của ứng dụng, chỉ chứa các thực thể (Entities), đối tượng giá trị (Value Objects) và quy tắc nghiệp vụ thuần túy bằng Python chuẩn (Zero I/O - không thực hiện ghi đĩa hay gọi mạng). |
| **Driving Adapter** | Inbound / Driving Adapter | Bộ điều hợp cổng vào: Thành phần nhận yêu cầu từ bên ngoài đưa vào hệ thống (ví dụ: FastAPI nhận HTTP request từ người dùng rồi gọi Use Case xử lý). |
| **Driven Adapter** | Outbound / Driven Adapter | Bộ điều hợp cổng ra: Thành phần nhận lệnh từ Use Case để tương tác với thế giới bên ngoài (ví dụ: SQLAlchemy ghi dữ liệu vào PostgreSQL, Redis gửi tin nhắn vào hàng đợi). |
| **Ports (Cổng)** | Inbound & Outbound Interfaces | Các bản hợp đồng trừu tượng (Interface / Protocol trong Python) quy định các hàm mà tầng Domain cần để giao tiếp với bên ngoài, áp dụng nguyên lý Nghịch đảo phụ thuộc (Dependency Inversion). |
| **Use Case** | Application Use Case | Từng ca sử dụng cụ thể của người dùng (ví dụ: Tải bài báo lên, Đặt câu hỏi đối thoại, Biên dịch mã LaTeX sang PDF). |
| **Worker Pool** | Background Worker Pool | Tập hợp các tiến trình chạy ngầm độc lập chuyên xử lý các tác vụ nặng, tốn nhiều thời gian (bóc tách PDF 100 trang, tính vector nhúng) để máy chủ web không bị treo. |
| **Explicit ACK** | Explicit Acknowledgment | Xác nhận tường minh: Khi Worker hoàn thành xong tác vụ thì mới báo lại cho hàng đợi Redis biết để xóa tác vụ; nếu Worker bị sập giữa chừng thì tác vụ sẽ tự động được giao cho Worker khác xử lý lại. |
| **DLQ** | Dead-Letter Queue | Hàng đợi thư chết: Nơi chứa các tác vụ bị lỗi nhiều lần liên tiếp để kỹ sư kiểm tra nguyên nhân mà không làm nghẽn dòng chảy công việc chung. |
| **gVisor (`runsc`)** | Kernel-level Sandbox Runtime | Môi trường ảo hóa cách ly an toàn do Google phát triển: Chặn các lệnh nguy hiểm từ bên trong mã lạ (ví dụ mã LaTeX độc hại) không cho can thiệp vào nhân hệ điều hành máy chủ (Host Kernel). |
| **mTLS** | Mutual Transport Layer Security | Giao thức mã hóa đường truyền yêu cầu cả 2 đầu (Client và Server nội bộ) cùng xuất trình chứng chỉ bảo mật để nhận diện nhau, chống tấn công giả mạo mạng nội bộ. |

---

## 1. CẤU TRÚC MONOREPO TOÀN CỤC

```text
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/
├── apps/
│   ├── api/                                  # Driving Adapter (Cổng vào): FastAPI Web & SSE Gateway
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── core/                     # Cấu hình Pydantic Settings, Structlog & Logging Engine
│   │   │   │   │   ├── config.py
│   │   │   │   │   └── logging.py
│   │   │   │   ├── middleware/               # Pure ASGI Tracing Middleware (Đo TTFB, Bẫy hủy kết nối HTTP 499)
│   │   │   │   │   └── tracing.py
│   │   │   │   ├── routes/                   # 59 RESTful Endpoints (Chuẩn AIP-136 Custom Verbs)
│   │   │   │   │   └── v1/
│   │   │   │   │       ├── documents.py      # Module 1: Upload tài liệu, Quản lý Chunks, Tóm tắt, Ghi chú
│   │   │   │   │       ├── drafts.py         # Module 2: Soạn thảo bản thảo, Biên dịch Sandbox SSE, Kiểm chứng SAFE
│   │   │   │   │       ├── references.py     # Module 3: Định danh tài liệu tham khảo, Đồ thị trích dẫn 2-hop
│   │   │   │   │       ├── library.py        # Module 4: Quản lý thư mục, Tổng hợp phân tầng, Ma trận so sánh
│   │   │   │   │       ├── sessions.py       # Sessions: Đồng bộ góc nhìn Viewport, Lịch sử hội thoại, OCC, TTL 30 ngày
│   │   │   │   │       └── shares.py         # Sharing: Liên kết công khai không cần đăng nhập, Thu hồi quyền truy cập
│   │   │   │   ├── schemas/                  # Pydantic v2 Request / Response Envelopes (Bao thư dữ liệu chuẩn hóa)
│   │   │   │   └── main.py                   # FastAPI Application Entrypoint & Lifespan (Khởi động ứng dụng)
│   │   └── tests/                            # API Integration & E2E Test Suite (Kiểm thử tích hợp đầu cuối)
│   │
│   ├── worker/                               # Ingestion Worker Pool (Tiến trình xử lý ngầm bền vững)
│   │   ├── src/
│   │   │   ├── worker.py                     # Vòng lặp nhận việc từ Redis Streams (Explicit ACK, DLQ)
│   │   │   └── tasks/                        # Phân tích bố cục, Cắt đoạn văn bản, Tính vector nhúng BGE-M3
│   │   └── Dockerfile.worker
│   │
│   ├── sandbox-broker/                       # Microservice Biên Dịch Cô Lập (Chạy trên máy chủ độc lập)
│   │   ├── src/
│   │   │   ├── server.py                     # Máy chủ gRPC / mTLS nội bộ (Cách ly tuyệt đối, cấm socket docker)
│   │   │   ├── runner.py                     # Bộ thực thi cách ly gVisor (runsc) / Kata Containers
│   │   │   └── linter.py                     # Bộ tiền kiểm tra cú pháp mã lệnh (AST Syntax Linter tầng 1)
│   │   └── Dockerfile.sandbox
│   │
│   └── web/                                  # Driving Adapter (Giao diện): React 19 Frontend (Vite + Tailwind CSS)
│
├── packages/
│   └── core/                                 # Hạt Nhân Lục Giác Nghiệp Vụ (Pure Domain & Application Core)
│       └── src/
│           └── core/
│               ├── domain/                   # 100% Mã Python thuần túy: Thực thể & Giá trị bất biến (Zero I/O)
│               │   ├── models/               # Document, Chunk, Turn, Draft, Note, Edge, Folder, Share
│               │   ├── value_objects/        # BoundingBox [x0, y0, x1, y1, page], PageDimensions
│               │   └── exceptions/           # Ngoại lệ nghiệp vụ (Lỗi xung đột đồng thời, Vượt quá sức chứa)
│               │
│               ├── application/              # Inbound Ports (Ca sử dụng điều phối luồng nghiệp vụ)
│               │   ├── ingestion/            # IngestDocumentUseCase, ParseDocumentUseCase
│               │   ├── qa/                   # AskSessionQuestionUseCase, EarlyConnectionReleaseStream
│               │   ├── drafting/             # CompileDraftSandboxUseCase, SelfHealingLoop, VerifySAFE
│               │   ├── citation/             # ResolveReferencesUseCase, QueryCitationGraphUseCase
│               │   ├── library/              # HierarchicalSynthesisUseCase, CompareMatrixUseCase
│               │   └── session/              # SyncViewportUseCase, RestoreArchivedUseCase
│               │
│               ├── ports/                    # Abstract Interfaces (Hợp đồng cổng trừu tượng nghịch đảo phụ thuộc)
│               │   ├── repositories.py       # Giao diện kho lưu trữ: IDocumentRepo, IChunkRepo, ISessionRepo
│               │   ├── queue.py              # Giao diện hàng đợi: ITaskQueueProducer (Redis Streams)
│               │   ├── parsers.py            # Giao diện bóc tách: IPDFParser, IStructureExtractor
│               │   ├── sandbox.py            # Giao diện biên dịch: ISandboxBrokerClient (gRPC)
│               │   ├── llm.py                # Giao diện mô hình ngôn ngữ: ILLMGateway, IEmbeddingEngine
│               │   └── storage.py            # Giao diện lưu trữ: IContentAddressableStorage (CAS)
│               │
│               └── infrastructure/           # Driven Adapters (Bộ điều hợp hiện thực hóa kết nối công nghệ)
│                   ├── database/             # SQLAlchemy 2.0 Async Models, Repositories, Migrations
│                   ├── queue/                # Bộ điều hợp đẩy việc vào hàng đợi Redis Streams
│                   ├── cache/                # Bộ điều hợp khóa trùng lặp Idempotency & Giới hạn tần suất Leaky Bucket
│                   ├── parsers/              # Bộ điều hợp bóc tách PDF bằng thư viện PyMuPDF (fitz)
│                   ├── sandbox/              # Bộ điều hợp gọi gRPC sang dịch vụ Sandbox Broker
│                   ├── llm/                  # Bộ định tuyến mô hình AI tiết kiệm chi phí (Docker Model Runner / Cloud)
│                   └── storage/              # Bộ điều hợp lưu file vật lý CAS có đếm tham chiếu (ref_count)
│
├── infra/                                    # Mã Khởi Tạo Hạ Tầng (Infrastructure as Code)
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.sandbox
│   │   └── Dockerfile.web
│   ├── postgres/
│   │   └── init.sql                          # Khởi tạo extension CSDL (pgvector lưu vector, uuid-ossp sinh khóa)
│   └── docker-compose.yml                    # Ngăn xếp phát triển cục bộ (Postgres 16, Redis 7, DMR)
│
├── docs/                                     # Toàn Bộ Hồ Sơ Tài Liệu Kỹ Thuật Dự Án
│   └── vi/
│       ├── PRD.md                            # Tài liệu Yêu cầu Sản phẩm (Product Requirements Document)
│       ├── design-api.md                     # Đặc tả 59 Endpoints REST / SSE (Chuẩn AIP-136, RFC 9110)
│       ├── design-database.md                # Lược đồ cơ sở dữ liệu PostgreSQL 16 + pgvector DDL
│       ├── design-architecture.md            # Bản thiết kế kiến trúc hệ thống & phần mềm toàn diện
│       ├── guide-docker.md                   # Hướng dẫn thiết lập Docker & PostgreSQL/pgvector
│       ├── guide-logging-system.md           # Hướng dẫn hệ thống Structlog, Pure ASGI & Giám sát vận hành
│       ├── backend-directory-structure.md    # Cấu trúc thư mục Monorepo & Phân bổ kiến trúc lục giác
│       └── techstack-backend-module-01.md    # Quyết định công nghệ & Đánh đổi kỹ thuật Module 1
│
├── pyproject.toml                            # Cấu hình gốc Monorepo uv Workspace
└── AGENTS.md                                 # Quy chuẩn & Điều luật kỹ thuật bắt buộc cho kỹ sư / AI Agents
```

---

## 2. QUY TẮC PHÂN CHIA RANH GIỚI BẤT BIẾN (HEXAGONAL BOUNDARIES)

Để đảm bảo mã nguồn luôn trong sạch, dễ kiểm thử tự động (Unit Test) và không bị suy thoái kiến trúc theo thời gian, mọi kỹ sư bắt buộc phải tuân thủ 5 điều luật ranh giới sau:

1. **Ranh giới tầng Domain (`packages/core/src/core/domain`):** 
   - Tuyệt đối không import bất kỳ thư viện bên ngoài nào (chỉ sử dụng thư viện tiêu chuẩn của Python và thư viện Pydantic v2 core để khai báo kiểu dữ liệu).
   - Tuyệt đối không phụ thuộc vào FastAPI, SQLAlchemy, Redis, hay bất kỳ công nghệ kết nối nào.
   - Mã nguồn tại đây phải có khả năng chạy kiểm thử tự động 100% trên bộ nhớ RAM mà không cần bật database hay nối mạng.
2. **Ranh giới tầng Application (`packages/core/src/core/application`):** 
   - Chỉ được phép import từ thư mục con `domain` và `ports`.
   - Đóng vai trò là người nhạc trưởng điều phối luồng công việc của Use Case (ví dụ: lấy dữ liệu từ Port Repo, gọi Port Parser để bóc tách, rồi lưu kết quả qua Port Storage).
3. **Ranh giới tầng Ports (`packages/core/src/core/ports`):** 
   - Chứa các bản thiết kế trừu tượng (`ABC` - Abstract Base Class hoặc `Protocol` trong Python).
   - Chỉ định nghĩa tên hàm, kiểu dữ liệu đầu vào và đầu ra; tuyệt đối không chứa dòng mã cài đặt cụ thể nào liên quan đến SQL hay HTTP.
4. **Ranh giới tầng Infrastructure (`packages/core/src/core/infrastructure`):** 
   - Nơi duy nhất được phép import các thư viện bên ngoài như SQLAlchemy (thao tác cơ sở dữ liệu), Redis (hàng đợi và bộ nhớ đệm), gRPC (kết nối máy chủ từ xa), PyMuPDF (xử lý file PDF).
   - Cài đặt cụ thể các hành vi mà các Ports đã cam kết.
5. **Ranh giới tầng Giao tiếp API (`apps/api`):** 
   - Đóng vai trò là Driving Adapter (Cổng vào) chỉ phụ thuộc vào `packages/core`.
   - Chịu trách nhiệm định tuyến đường dẫn HTTP (`routes/`), xác thực tính hợp lệ của dữ liệu gửi lên từ người dùng (`schemas/`), bắt mã lỗi và định dạng câu trả lời chuẩn xác cho client.
