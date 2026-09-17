# Kế Hoạch Kỹ Thuật: Khởi Tạo Phiên Nghiên Cứu Đa Bài Báo (POST /api/v1/sessions)

> **Mã tài liệu:** `FEAT-M1-API-45`  
> **Trạng thái:** `PLANNING / CHỜ PHÊ DUYỆT (CHƯA VIẾT CODE TRIỂN KHAI)`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 17/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-api-post-sessions`  
> **API Canonical:** `POST /api/v1/sessions` (#45 trong danh mục API VeriScholar)  
> **Chuẩn thiết kế:** RFC 9110 / RFC 7232 (HTTP Semantics & Conditional Requests, ETag, Location), RFC 7807 (Problem Details), Google AIP-136, Hexagonal Clean Architecture.

---

## 1. Khảo Sát Nghiên Cứu Thế Giới & Tùy Biến Cho VeriScholar (State of the Art & Customization)

### 1.1. Cách Các Nền Tảng Hàng Đầu Thế Giới Quản Trị Phiên Nghiên Cứu Đa Tài Liệu
Để xây dựng một hệ thống học thuật chuyên nghiệp, chúng tôi đã khảo sát cơ chế quản lý phiên làm việc của các nền tảng AI nghiên cứu hàng đầu hiện nay:

1. **Google NotebookLM (Source-Centric Notebook Workspace):**
   - **Cơ chế:** Coi "Notebook" là một không gian gom cụm (cluster) từ 1 đến nhiều tài liệu nguồn (PDF, Docs, Web links). Khi người dùng khởi tạo notebook, hệ thống tạo một phiên làm việc độc lập chứa danh mục nguồn (Sources manifest), con trỏ trỏ tới tài liệu đang xem (Active Source), và luồng chat tổng hợp.
   - **Điểm mạnh:** Giúp người nghiên cứu không bị phân tán; AI có thể vừa trả lời cục bộ trên 1 tài liệu, vừa tổng hợp liên tài liệu (cross-source synthesis).
   - **Hạn chế:** NotebookLM cho phép nạp tới 50 nguồn, dẫn đến nguy cơ loãng ngữ cảnh nghiêm trọng khi thực hiện trích dẫn vi mô (micro-grounding).

2. **Perplexity Pro & Elicit (Research Collections / Threads):**
   - **Cơ chế:** Khởi tạo Thread hoặc Collection gắn với một tập tài liệu cụ thể. Áp dụng cơ chế idempotency cao cấp để ngăn chặn người dùng vô tình bấm tạo 2 lần khi mạng lag.
   - **Điểm mạnh:** Quản lý lịch sử trực quan (Sidebar History), hỗ trợ khôi phục tức thì toàn bộ trạng thái phiên làm việc.

3. **Open-WebUI & LibreChat (Production Open-Source Workspace Pattern):**
   - **Cơ chế:** Tách rời hoàn toàn thực thể Phiên (`sessions`) và thực thể Tài liệu (`files`/`documents`) thông qua bảng liên kết trung gian N-N (`session_documents`) có lưu thứ tự hiển thị (`display_order`).
   - **Điểm mạnh:** Xóa phiên không làm mất tài liệu gốc; xóa tài liệu gốc sẽ tự động cập nhật hoặc ngắt kết nối an toàn mà không để lại khóa ngoại mồ côi (Orphan FKs).

### 1.2. Giải Pháp Tùy Biến Chuyên Biệt Cho VeriScholar (Tailored Customization)
Kế thừa tinh hoa từ các giải pháp trên, VeriScholar đưa ra thiết kế tùy biến sâu cho bài toán đọc sâu học thuật:

```text
               YÊU CẦU NGƯỜI DÙNG (POST /api/v1/sessions)
                                  │
                                  ▼
        ┌───────────────────────────────────────────────────┐
        │  1. Kiểm tra Giới hạn Dung lượng (Cap = 5 Papers)  │
        │     - Ngăn ngừa hiện tượng "Lost in the Middle"   │
        │     - Duy trì SLA trích dẫn Bounding Box < 5s     │
        └───────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌───────────────────────────────────────────────────┐
        │  2. Xác minh Đa người dùng & Phân quyền (Tenant) │
        │     - Tất cả initial_document_ids phải thuộc về   │
        │       chính user_id đang gửi yêu cầu              │
        └───────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌───────────────────────────────────────────────────┐
        │  3. Khởi tạo Trạng thái Không gian Làm việc       │
        │     - active_document_id = doc_ids[0] (nếu có)    │
        │     - active_tab = "chat"                         │
        │     - viewport_state = {page: 1, zoom: 1.0, ...}  │
        │     - version = 1 (Chuẩn hóa cho khóa lạc quan OCC)│
        └───────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌───────────────────────────────────────────────────┐
        │  4. Phản hồi Chuẩn RFC 9110 / RESTful             │
        │     - HTTP Status: 201 Created                    │
        │     - Header Location: /api/v1/sessions/{id}      │
        │     - Header ETag: "v1" (Weak/Strong ETag OCC)    │
        └───────────────────────────────────────────────────┘
```

* **Giới hạn Cứng 1 - 5 Bài Báo (Capacity Constraint):** Theo đúng PRD Module 1, một phiên nghiên cứu chỉ cho phép tối đa 5 bài báo. Giới hạn này nhằm bảo toàn khả năng tập trung cao độ của nhà nghiên cứu, bảo vệ ngân sách ngữ cảnh (Token Budgeting <= 3.500 tokens) và giúp Cross-Encoder Reranker đạt độ chính xác cao nhất mà không bị pha loãng.
* **Gắn Active Document Tự Động:** Nếu người dùng truyền danh sách tài liệu ban đầu, tài liệu đầu tiên trong danh sách sẽ tự động được chọn làm `active_document_id` để Canvas PDF.js bên trái mở ngay tức khắc mà không cần thêm một round-trip API.
* **Bảo Vệ Độc Lập Trạng Thái Đọc (Viewport State Invariant):** Khởi tạo mặc định `{"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0}` và `active_tab = "chat"` để đảm bảo khi frontend load xong sẽ có ngay trạng thái hiển thị nhất quán.

---

## 2. Hiện Trạng & Đánh Giá Mức Độ Sẵn Sàng (Gap Analysis)

### 2.1. Những Thành Phần ĐÃ CÓ Trong Codebase:
1. **Model ORM Cơ Bản:**
   - Trong [`apps/api/src/api/db/models/session.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/session.py) đã có khai báo sơ khởi `ResearchSessionModel` và `SessionDocumentModel`.
   - Bảng liên kết `session_documents` đã có khai báo `session_id`, `document_id`, `added_at`.
2. **Domain Entity SessionTurn:**
   - [`packages/core/src/core/domain/entities/session_turn.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/packages/core/src/core/domain/entities/session_turn.py) đã được định nghĩa độc lập không dính I/O.
3. **Cơ Chế Phân Quyền & Multi-Tenant:**
   - Dependency `get_current_user` trong [`apps/api/src/api/deps.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/deps.py) đã sẵn sàng trích xuất `UserModel` an toàn.
4. **Hạ Tầng API Response Envelope:**
   - [`SingleResponseEnvelope`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/schemas/envelope.py) đã chuẩn hóa cấu trúc phản hồi `{success, data, meta}`.

### 2.2. Những Thành Phần CHƯA CÓ (Cần Xây Dựng):
1. **Thiếu Trường DDL Trong Model ORM (`ResearchSessionModel` & `SessionDocumentModel`):**
   - `ResearchSessionModel` hiện tại thiếu:
     - `active_document_id`: Khóa ngoại `UUID NULL REFERENCES documents(id) ON DELETE SET NULL`.
     - `viewport_state`: Cột `JSONB NOT NULL DEFAULT '{"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0}'`.
     - `active_tab`: Cột `VARCHAR(30) NOT NULL DEFAULT 'chat'`.
     - `is_archived`: Cột `BOOLEAN NOT NULL DEFAULT FALSE`.
     - `archived_at`: Cột `TIMESTAMPTZ NULL`.
     - Index tổng hợp: `idx_sessions_user_archived` trên `(user_id, is_archived, updated_at DESC)`.
   - `SessionDocumentModel` thiếu:
     - `display_order`: Cột `INT NOT NULL DEFAULT 0`.
     - Index: `idx_session_docs_doc` trên `(document_id)`.
2. **Core Domain & Ports (Tầng packages/core):**
   - Chưa có Domain Entity `ResearchSession` trong `packages/core/src/core/domain/entities/session.py`.
   - Chưa có Value Object `ViewportState` và Enum `SessionActiveTab` trong `packages/core/src/core/domain/value_objects/`.
   - Chưa có Port Interface `ISessionRepositoryPort` trong `packages/core/src/core/ports/session.py`.
3. **Application Service (`apps/api/src/api/services/session_service.py`):**
   - Chưa có `SessionService` quản lý giao dịch ACID tạo phiên, gán documents, kiểm tra dung lượng tối đa 5 bài, kiểm tra quyền sở hữu multi-tenant.
4. **Driving Router Endpoint (`POST /api/v1/sessions`):**
   - Chưa có router file `apps/api/src/api/v1/endpoints/sessions.py`.
   - Chưa có schema request/response: `SessionCreateRequest`, `SessionResponseData`.
   - Chưa đăng ký router vào `apps/api/src/api/v1/router.py`.
5. **Hệ Thống Kiểm Thử 2 Cấp Độ & Eval Harness:**
   - Chưa có bộ unit/integration test: `apps/api/tests/test_sessions_create.py`.
   - Chưa có snapshot evaluator runner: `scripts/eval/runners/post_sessions_create.py`.
   - Chưa đăng ký alias `create-session` vào `scripts/eval_api.py`.
   - Chưa cập nhật `docs/vi/swagger.md` và `docs/vi/design-api-eval-snapshots.md`.

---

## 3. Rà Soát Biến Môi Trường (.env.example)

- **Nguyên tắc an toàn tuyệt đối:** KHÔNG đọc tệp `.env`.
- **Rà soát `.env.example`:**
  - `POST /api/v1/sessions` là tác vụ quản trị cơ sở dữ liệu quan hệ (PostgreSQL 18) thuần túy.
  - Tác vụ sử dụng trực tiếp kết nối cơ sở dữ liệu `DATABASE_URL` đã có sẵn.
  - **Không yêu cầu bất kỳ API key bên ngoài hay biến môi trường mới nào.** Không cần cập nhật `.env.example`.

---

## 4. Thiết Kế Kiến Trúc Lục Giác Chi Tiết (Hexagonal Architecture Breakdown)

### 4.1. Tầng Database & Persistence (DDL & ORM Models)
Cập nhật tệp [`apps/api/src/api/db/models/session.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/session.py) để đồng bộ 100% với đặc tả [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md):

```python
class ResearchSessionModel(IdentifiableTimestampedModel):
    """Represents a research inquiry and multi-paper reading session (1 - 5 papers)."""

    __tablename__ = "research_sessions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    active_document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    viewport_state: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
    )
    active_tab: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="chat",
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        Index("idx_sessions_user_archived", "user_id", "is_archived", "updated_at"),
    )


class SessionDocumentModel(Base):
    """Many-to-many junction linking documents to research sessions (max 5)."""

    __tablename__ = "session_documents"

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("research_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
```

### 4.2. Tầng Core Domain & Value Objects (packages/core)
Tuân thủ nghiêm ngặt tính độc lập công nghệ, không import FastAPI, SQLAlchemy hay bất kỳ thư viện I/O nào:

1. **Value Object ViewportState & Enums (`packages/core/src/core/domain/value_objects/`):**
   - `SessionActiveTab(StrEnum)`: `CHAT = "chat"`, `NOTES = "notes"`, `SUMMARY = "summary"`, `GRAPH = "graph"`, `DRAFT = "draft"`.
   - `ViewportState(BaseModel)`:
     - `page: int` (ràng buộc `ge=1`)
     - `zoom_ratio: float` (ràng buộc `gt=0.0`, mặc định `1.0`)
     - `scroll_top: float` (ràng buộc `ge=0.0`, mặc định `0.0`)
2. **Domain Entity ResearchSession (`packages/core/src/core/domain/entities/session.py`):**
   - Các trường thuộc tính: `id`, `user_id`, `title`, `active_document_id`, `document_ids: list[UUID]`, `viewport_state: ViewportState`, `active_tab: SessionActiveTab`, `is_archived: bool`, `archived_at: datetime | None`, `version: int`, `created_at`, `updated_at`.
   - **Bất biến miền nghiệp vụ (Domain Invariants):**
     - Tiêu đề phải được strip, độ dài từ 1 đến 255 ký tự.
     - Dung lượng tài liệu: `len(document_ids) <= 5`. Nếu lớn hơn 5, ném `DomainException("SESSION_CAPACITY_EXCEEDED")`.
     - Nếu `document_ids` có phần tử, `active_document_id` hợp lệ phải nằm trong tập `document_ids`.

3. **Port Interface (`packages/core/src/core/ports/session.py`):**
   - Khai báo giao diện trừu tượng `ISessionRepositoryPort`:
     ```python
     class ISessionRepositoryPort(ABC):
         @abstractmethod
         async def create_session(
             self,
             user_id: UUID,
             title: str,
             initial_document_ids: list[UUID],
         ) -> ResearchSession:
             """Create a new research session within an ACID boundary."""
             pass
     ```

### 4.3. Tầng Application Use Cases (`apps/api/src/api/services/session_service.py`)
Xây dựng `SessionService` phụ trách điều phối nghiệp vụ:
1. **Làm sạch dữ liệu đầu vào:**
   - Loại bỏ trùng lặp trong mảng `initial_document_ids` mà vẫn bảo toàn thứ tự ban đầu (`list(dict.fromkeys(initial_document_ids))`).
   - Kiểm tra số lượng: Nếu `len(cleaned_doc_ids) > 5`, ném `HTTPException(400, detail="SESSION_CAPACITY_EXCEEDED")`.
2. **Xác minh quyền sở hữu tài liệu (Multi-Tenant Document Guard):**
   - Nếu `initial_document_ids` không rỗng, thực thi truy vấn kiểm tra tập tài liệu:
     ```sql
     SELECT id FROM documents WHERE id = ANY(:doc_ids) AND user_id = :user_id;
     ```
   - So sánh số lượng tìm thấy với danh sách yêu cầu. Nếu thiếu bất kỳ ID nào $\rightarrow$ lập tức ném lỗi `HTTPException(404, detail="DOCUMENT_NOT_FOUND")` nhằm bảo mật tuyệt đối, ngăn chặn kỹ thuật rò rỉ thông tin (ID Enumeration).
3. **Thực thi giao dịch ACID:**
   - Tạo bản ghi `ResearchSessionModel` với `version = 1`, `active_tab = "chat"`, `viewport_state = {"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0}`.
   - Gán `active_document_id = cleaned_doc_ids[0]` nếu có ít nhất 1 tài liệu; ngược lại để `None`.
   - Bulk insert các bản ghi `SessionDocumentModel` tương ứng với `display_order = 0, 1, 2...`.
   - Commit giao dịch và trả về đối tượng `SessionResponseData`.

### 4.4. Tầng Driving Adapter (Router & Schemas trong `apps/api`)

1. **Pydantic Schemas (`apps/api/src/api/schemas/session.py`):**
   ```python
   class SessionCreateRequest(BaseModel):
       title: str = Field(
           ...,
           min_length=1,
           max_length=255,
           description="Tiêu đề phiên nghiên cứu",
           examples=["Nghiên cứu Kiến trúc Attention & Transformer"],
       )
       initial_document_ids: list[UUID] = Field(
           default_factory=list,
           description="Danh sách tài liệu ban đầu nạp vào phiên (tối đa 5 bài)",
           examples=[["c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"]],
       )

   class ViewportStateSchema(BaseModel):
       page: int = Field(default=1, ge=1)
       zoom_ratio: float = Field(default=1.0, gt=0.0)
       scroll_top: float = Field(default=0.0, ge=0.0)

   class SessionResponseData(BaseModel):
       id: UUID
       title: str
       document_ids: list[UUID]
       active_document_id: UUID | None
       viewport_state: ViewportStateSchema
       active_tab: str
       is_archived: bool
       version: int
       created_at: datetime
       updated_at: datetime

   class SessionSingleEnvelope(SingleResponseEnvelope[SessionResponseData]):
       pass
   ```

2. **Endpoint Router (`apps/api/src/api/v1/endpoints/sessions.py`):**
   - **Method:** `POST /api/v1/sessions`
   - **Status Code:** `201 Created`
   - **Headers Phản hồi:**
     - `Location: /api/v1/sessions/{session.id}` (Tuân thủ chuẩn RFC 9110 cho tài nguyên vừa được tạo)
     - `ETag: "v1"` (Phục vụ cho các thao tác cập nhật đồng thời OCC sau này)
   - **Mã lỗi chuẩn hóa:**
     - `400 Bad Request`: `SESSION_CAPACITY_EXCEEDED` (vượt quá 5 tài liệu).
     - `404 Not Found`: `DOCUMENT_NOT_FOUND` (tài liệu không tồn tại hoặc không thuộc quyền sở hữu).
     - `422 Unprocessable Entity`: Tiêu đề rỗng, UUID không hợp lệ.

---

## 5. Phân Tích Rủi Ro & Đánh Đổi Kỹ Thuật (Risk Analysis & Trade-offs)

| Rủi ro kỹ thuật | Mức độ | Đánh đổi & Giải pháp kỹ thuật xử lý triệt để |
| :--- | :---: | :--- |
| **Race condition khi nạp tài liệu đồng thời (Write Skew / Capacity Breach)** | **TRUNG BÌNH** | Tầng ứng dụng kiểm tra `len <= 5` trước khi ghi. Đồng thời ở tầng Database, trigger `enforce_session_capacity()` sử dụng `PERFORM ... FOR UPDATE` trên bảng cha `research_sessions` để tuần tự hóa các thao tác nạp tài liệu, bảo đảm không bao giờ có quá 5 tài liệu lọt vào một phiên. |
| **Rò rỉ thông tin phân quyền đa người dùng (Multi-Tenant ID Enumeration)** | **CAO** | Khi người dùng gửi một `document_id` của người khác hoặc ID ngẫu nhiên, hệ thống trả về đồng nhất `404 DOCUMENT_NOT_FOUND` kèm thông báo chung, ngăn chặn kẻ xấu dò quét ID tài liệu của người khác. |
| **Yêu cầu gửi trùng lặp do mạng chập chờn (Network Retry Duplicate Sessions)** | **TRUNG BÌNH** | Chuẩn bị sẵn cơ chế tiếp nhận header `Idempotency-Key` tùy chọn qua cổng `IIdempotencyPort`. Nếu trùng lặp key, hệ thống trả về phiên đã tạo trước đó thay vì tạo phiên mới. |
| **Tài liệu nạp ban đầu bị xóa sau đó (Cascading vs Orphan Reference)** | **THẤP** | Cấu hình khóa ngoại `session_documents.document_id ON DELETE CASCADE` và `research_sessions.active_document_id ON DELETE SET NULL`. Khi bài báo bị xóa, liên kết tự động gỡ bỏ sạch sẽ mà không làm hỏng phiên nghiên cứu. |

---

## 6. Kế Hoạch Kiểm Thử 2 Cấp Độ (Unit Tests & Autotest Snapshot Runner)

> **Nguyên tắc bất di bất dịch:** Tuyệt đối KHÔNG thiết kế endpoint backdoor `/api/v1/testing/...`. Mọi kiểm thử đều đi qua luồng REST công khai.

### 6.1. Cấp Độ 1: Integration & Unit Tests (`apps/api/tests/test_sessions_create.py`)
Viết tối thiểu 8 kịch bản kiểm thử bao phủ toàn bộ luồng nghiệp vụ:
1. `test_create_empty_session_success`: Tạo phiên trống không có tài liệu $\rightarrow$ kiểm tra `201 Created`, `active_document_id = None`, `document_ids = []`, `Location` header, `ETag = "v1"`.
2. `test_create_session_with_valid_documents_success`: Tạo phiên với 1 - 3 tài liệu hợp lệ $\rightarrow$ kiểm tra `201 Created`, `active_document_id = doc_1`, `document_ids = [doc_1, doc_2, doc_3]`, `display_order` được lưu tuần tự.
3. `test_create_session_exceeds_capacity_failure`: Truyền 6 tài liệu $\rightarrow$ kiểm tra `400 Bad Request` với mã `SESSION_CAPACITY_EXCEEDED`.
4. `test_create_session_with_duplicate_documents`: Truyền danh sách có ID trùng lặp `[doc_1, doc_1, doc_2]` $\rightarrow$ hệ thống tự khử trùng thành `[doc_1, doc_2]` và tạo thành công.
5. `test_create_session_with_nonexistent_document`: Truyền UUID tài liệu không tồn tại $\rightarrow$ kiểm tra `404 Not Found`.
6. `test_create_session_multi_tenant_isolation`: User A cố tình truyền `document_id` của User B $\rightarrow$ kiểm tra `404 Not Found`, tuyệt đối không cho phép User A gắn tài liệu của User B vào phiên.
7. `test_create_session_invalid_title`: Tiêu đề rỗng `""` hoặc toàn khoảng trắng $\rightarrow$ kiểm tra `422 Unprocessable Entity`.
8. `test_create_session_title_too_long`: Tiêu đề vượt quá 255 ký tự $\rightarrow$ kiểm tra `422 Unprocessable Entity`.

### 6.2. Cấp Độ 2: Autotest Snapshot Evaluator Độc Lập (`scripts/eval/runners/post_sessions_create.py`)
Xây dựng runner độc lập kế thừa `BaseAPIRunner`:
- **Kịch bản thực tế:**
  - Case 1: Tạo phiên nghiên cứu đa bài kèm 2 tài liệu benchmark chuẩn (Attention Paper + Chunking Paper).
  - Case 2: Kiểm tra Headers (`Location`, `ETag: "v1"`).
  - Case 3: Kiểm tra cấu trúc trạng thái (`active_document_id`, `viewport_state`, `active_tab`).
  - Case 4: Kiểm chứng rào chắn dung lượng (Capacity Guard > 5 bài).
  - Case 5: Kiểm chứng rào chắn phân quyền đa người dùng (Multi-tenant Guard).
  - Case 6: Kiểm chứng từ chối tiêu đề sai chuẩn (Validation Guard 422).
- **Tự động xuất báo cáo snapshot:** Ghi nhận đầy đủ chi tiết Request/Response và thời gian phản hồi vào `temp/output/test/post_sessions_create.md`.
- **Dọn dẹp sạch sẽ (Zero-Retention):** Xóa phiên và tài liệu thử nghiệm ngay sau khi chạy xong.

### 6.3. Tích Hợp Test Runner Tổng Hệ Thống (`scripts/eval_api.py`)
- Khai báo runner mới trong [`scripts/eval/runners/__init__.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/scripts/eval/runners/__init__.py) với alias `create-session`.
- Thêm vào danh mục thực thi của Module 1 để khi chạy `uv run python scripts/eval_api.py --all --ci-gate`, hệ thống tự động kiểm thử liên hoàn toàn bộ API mà không cần can thiệp thủ công.

### 6.4. Cập Nhật Tài Liệu Kèm Theo
- **Swagger Documentation:** Bổ sung đặc tả Endpoint #45 vào [`docs/vi/swagger.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/swagger.md) với schema Request, Response, Headers và Status Codes.
- **Snapshot Specification:** Bổ sung cấu trúc dữ liệu kiểm chuẩn của `POST /api/v1/sessions` vào [`docs/vi/design-api-eval-snapshots.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api-eval-snapshots.md).
- **Hướng Dẫn Vận Hành:** Cập nhật mục hướng dẫn chạy lệnh trong [`scripts/README.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/scripts/README.md).

---

## 7. Kế Hoạch Phân Kỳ Thực Thi Chi Tiết (Execution Roadmap)

```text
[BƯỚC 1: CẬP NHẬT DATABASE DDL & ORM MODELS]
├── Bổ sung các trường active_document_id, viewport_state, active_tab, is_archived vào ResearchSessionModel
├── Bổ sung display_order và index idx_session_docs_doc vào SessionDocumentModel
└── Kiểm tra Base.metadata.create_all hoạt động mượt mà với SQLite/PostgreSQL

[BƯỚC 2: XÂY DỰNG CORE DOMAIN & PORTS (PACKAGES/CORE)]
├── Tạo Enum SessionActiveTab và Value Object ViewportState trong packages/core
├── Tạo Domain Entity ResearchSession với các bất biến kiểm tra capacity
└── Tạo Port Interface ISessionRepositoryPort

[BƯỚC 3: XÂY DỰNG APPLICATION SERVICE (APPS/API)]
├── Tạo SessionService xử lý logic khởi tạo phiên, gán documents và multi-tenant guard
└── Đăng ký get_session_service() dependency vào apps/api/src/api/deps.py

[BƯỚC 4: XÂY DỰNG DRIVING ADAPTER (ROUTER & SCHEMAS)]
├── Tạo Schemas: SessionCreateRequest, SessionResponseData, SessionSingleEnvelope
├── Tạo Router: POST /api/v1/sessions với các headers Location và ETag
└── Đăng ký sessions.router vào api_v1_router trong apps/api/src/api/v1/router.py

[BƯỚC 5: XÂY DỰNG HỆ THỐNG KIỂM THỬ 2 CẤP ĐỘ]
├── Viết 8 test cases integration trong apps/api/tests/test_sessions_create.py
├── Tạo Snapshot Runner scripts/eval/runners/post_sessions_create.py
└── Đăng ký alias create-session vào scripts/eval_api.py và kiểm tra zero-retention purge

[BƯỚC 6: TÀI LIỆU HÓA & KIỂM TRA CHẤT LƯỢNG TOÀN DIỆN]
├── Cập nhật docs/vi/swagger.md, docs/vi/design-api-eval-snapshots.md, scripts/README.md
├── Chạy toàn bộ pytest suite (bảo đảm 220+ tests PASS)
└── Chạy ruff check . và ruff format --check . đạt chuẩn 100% clean
```

---

## 8. Kết Luận & Điểm Dừng Phê Duyệt (Checkpoint Approval)

Toàn bộ bản kế hoạch kỹ thuật trên đã bám sát 100% kiến trúc Lục giác, chuẩn thiết kế RFC/Google AIP-136, tài liệu PRD, Database DDL và API design của VeriScholar.

> [!IMPORTANT]
> **Tuân thủ quy trình an toàn:** Hiện tại tôi **CHỈ DỪNG LẠI Ở BƯỚC LẬP KẾ HOẠCH**, hoàn toàn **CHƯA THAY ĐỔI HAY VIẾT MÃ NGUỒN CODING** của ứng dụng.
> Khi nhận được sự đồng ý và lệnh trực tiếp từ bạn, tôi sẽ tạo nhánh Git `feat/m1-api-post-sessions` và bắt đầu triển khai lần lượt từng bước theo đúng lộ trình đã đề ra.


---

## 9. Quyết Định Nâng Cấp Sản Phẩm (Production ADR & Enhancements)

Theo phản hồi từ yêu cầu nâng cấp sản phẩm chuẩn production, API `POST /api/v1/sessions` được bổ sung 3 năng lực trọng yếu:

### 9.1. Cơ chế Idempotency chống gửi trùng lặp (`Idempotency-Key`)
- **Vấn đề:** Double-click từ người dùng hoặc mạng giật lag gửi 2 request liên tiếp tạo 2 phiên làm việc dư thừa.
- **Giải pháp:** Tiếp nhận header `Idempotency-Key` (hoặc `X-Idempotency-Key`).
  - Cache key: `idempotency:session_create:{user_id}:{idempotency_key}` (TTL 24 giờ).
  - Khi trùng lặp: Trả về HTTP `200 OK` (hoặc `201`) kèm header `X-Cache: Idempotent-Hit` và payload nguyên vẹn của phiên đã tạo.

### 9.2. Cơ chế Auto-naming Fallback cho tiêu đề phiên (`title`)
- **Vấn đề:** Bắt buộc người dùng phải nhập tiêu đề gây ma sát trải nghiệm (friction) khi muốn mở nhanh nhiều tài liệu để đọc.
- **Giải pháp:** Trường `title` là tùy chọn (`None`).
  - Nếu có truyền tài liệu: Tự động đặt tên `"Nghiên cứu: {first_doc.title}"` (rút gọn tối đa 255 ký tự).
  - Nếu phiên rỗng: Tự động đặt tên `"Phiên nghiên cứu {DD/MM/YYYY HH:mm}"`.
  - Nếu truyền chuỗi rỗng hoặc chỉ có khoảng trắng: Tiếp tục chặn bằng HTTP `422 Unprocessable Entity` để bảo vệ tính toàn vẹn dữ liệu.

### 9.3. Nhúng Metadata Bài Báo (`include_documents=true`) và Cảnh báo Trạng thái (`warnings`)
- **Vấn đề:** Sau khi tạo phiên, frontend cần tiêu đề, tên file và trạng thái của từng bài báo để render ngay các tab tài liệu mà không phải gửi thêm 5 request `GET /api/v1/documents/{id}`.
- **Giải pháp:**
  - Query parameter `include_documents=true` nhúng danh sách `documents: list[SessionDocumentItem]` theo đúng thứ tự `display_order`.
  - Tự động kiểm tra và thêm cảnh báo vào mảng `warnings` nếu có tài liệu đang ở trạng thái chưa hoàn tất (`processing` hoặc `failed`), giúp UI hiển thị thông báo kịp thời cho người dùng.
