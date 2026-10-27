# ĐẶC TẢ KỸ THUẬT: PHÂN HỆ PHIÊN ĐỌC SÂU, QUẢN LÝ ĐA TAB & HYBRID RAG CHAT CÓ BOUNDING BOX
# (DEEP READING SESSIONS, MULTI-TAB PDF, RAG GROUNDING & SCHOLAR NOTES SPECIFICATION)

**Trạng thái:** DỰ THẢO CHÍNH THỨC (TECHNICAL SPECIFICATION V1)  
**Nguồn tham chiếu PRD:** [`03-sessions-and-deep-reading-crud.md`](../PRD/03-sessions-and-deep-reading-crud.md)  
**Phân hệ kỹ thuật:** Phân Hệ Đọc Sâu & Đối Thoại Minh Chứng (Deep Reading & Grounded Chat)  
**File nền tảng liên đới:** [`00-foundation-architecture-and-db.md`](./00-foundation-architecture-and-db.md)

---

## 1. Usecase & Bối Cảnh Người Dùng (Real-World User Journey & Value)

### A. Usecase 1: Đọc Sâu & Đối Chiếu Song Song Nhiều Bài Báo (Multi-Paper Comparative Reading)
- **Bối cảnh & Vấn đề thực tế:** Khi nghiên cứu một chủ đề (ví dụ: *Cơ chế Attention trong NLP*), người dùng hiếm khi chỉ đọc 1 bài báo duy nhất mà cần mở bài báo gốc (Vaswani et al., 2017) cùng với 2-3 bài báo cải tiến (BERT, RoBERTa) để đối chiếu sự khác biệt. Nếu phải liên tục mở nhiều tab trình duyệt riêng biệt rồi copy paste qua lại, họ sẽ mất mạch tập trung và không thể hỏi AI so sánh đồng thời giữa các tài liệu.
- **Giải pháp của phân hệ:**
  - Cung cấp thanh quản lý đa tab học thuật (`DocumentTabBar.tsx`) cho phép mở đồng thời từ 1 đến 5 bài báo trong cùng một phiên nghiên cứu.
  - Người dùng dễ dàng chuyển đổi tab xem PDF, đóng bớt tài liệu bằng nút `[✕]` mà không xóa mất file, và AI có thể truy xuất ngữ cảnh chéo giữa các bài báo đang mở trong tab để trả lời câu hỏi so sánh.

### B. Usecase 2: Đối Thoại Minh Chứng Tuyệt Đối Chống Ảo Giác Với Bounding Box Vàng (Zero-Hallucination Grounded Chat)
- **Bối cảnh & Vấn đề thực tế:** Nỗi sợ lớn nhất của các nhà khoa học khi sử dụng AI là hiện tượng ảo giác (Hallucination) — AI tự bịa ra công thức toán hoặc trích dẫn sai số trang. Trong các bài báo khoa học, một câu khẳng định sai có thể làm hỏng toàn bộ luận án.
- **Giải pháp của phân hệ:**
  - Mọi câu trả lời của Trợ lý Socratic bắt buộc phải kèm huy hiệu bảo chứng nguồn gốc `[📄 Tên bài • Trang X]`.
  - Khi người dùng nhấp chuột vào huy hiệu: giao diện tự động chuyển tab (nếu tài liệu ở tab khác), cuộn mượt mà đến đúng trang PDF và vẽ một khung chữ nhật màu vàng nhấp nháy (**Golden Bounding Box**) bao quanh chính xác đoạn văn gốc làm bằng chứng, mang lại niềm tin tuyệt đối cho học giả.

### C. Usecase 3: Trích Xuất & Lưu Trữ Ghi Chú Học Thuật Tại Chỗ (In-Context Scholar Notes)
- **Bối cảnh & Vấn đề thực tế:** Trong lúc đọc tài liệu, người dùng phát hiện một định lý hoặc công thức hay và muốn ghi chú lại kèm suy nghĩ cá nhân để dùng cho bài viết sau này mà không muốn mở thêm ứng dụng Notion hay Google Docs bên ngoài.
- **Giải pháp của phân hệ:**
  - Khi bôi đen bất kỳ đoạn văn bản nào trên trang PDF, menu ngữ cảnh nổi `ScholarSelectionMenu.tsx` xuất hiện với các nút hành động 1 chạm: `[💬 Đưa vào Chat để hỏi thêm]` hoặc `[📝 Lưu vào Sổ tay Ghi chú]`.
  - Toàn bộ ghi chú được lưu vào bảng `research_notes` kèm số trang và trích dẫn gốc, sẵn sàng chuyển giao sang không gian viết bài.

---

## 2. Phạm Vi & Bảng Đối Chiếu Hiện Trạng (`As-Is` vs `Delta`)

Phân hệ này là không gian làm việc trung tâm nhất của VeriScholar (`/dashboard/:sessionId`):
- **Cột trái:** Trình đọc `PdfCanvasViewer.tsx` render PDF gốc sắc nét, hỗ trợ lớp phủ Bounding Box vàng nhấp nháy khi bấm trích dẫn, và menu nổi khi bôi đen văn bản (`ScholarSelectionMenu.tsx`). Khi bài báo ở trạng thái `status='abstract_only'`, cột trái tự động chuyển sang `AbstractCardViewer.tsx`.
- **Cột phải:** Trợ lý Socratic Chat Tiếng Việt streaming SSE unbuffered, hiển thị công thức toán KaTeX và các huy hiệu bảo chứng `[📄 Tên bài • Trang X]` bấm vào là cuộn PDF bên trái.
- **Thanh Tab trên:** Quản lý 1–5 bài báo mở đồng thời trong phiên đọc (`DocumentTabBar.tsx`).
- **Ngăn trượt:** Sổ tay ghi chú (`NotesPanelContainer.tsx`) bám sát tài liệu gốc.

### A. Kiến Trúc Tổng Thể 2 Tầng (2-Tier Architecture Visualization)

Phân hệ Deep Reading vận hành theo mô hình **Agentic Dual-Index Advanced RAG** tách biệt tường minh 2 giai đoạn:

#### 1. Sơ Đồ Tầng 1: Quy Trình Nạp Bài Báo & Đánh Chỉ Mục Kép (Offline Ingestion Pipeline)
*(Kích hoạt 1 lần duy nhất khi người dùng tải PDF lên hoặc chọn "Mở Đọc Sâu", xử lý bất đồng bộ qua BackgroundTasks)*

```mermaid
flowchart TD
    PDF["1. File PDF Bài Báo Khoa Học (<= 50MB)"] --> Parser["2. PyMuPDF Layout Engine: Nhận diện 2 cột & BBox [0..1000]"]
    
    Parser --> Branch{"3. Phân Rã Dữ Liệu 2 Tầng"}
    
    %% Nhánh Macro (Summary)
    Branch -->|"Nhánh Vĩ mô (Macro)"| SumExtract["4A. Summary Extractor: Trích xuất Title, Abstract, Headings, Kết luận"]
    SumExtract --> SumStore[("Summary Index: Bảng documents.summary_metadata")]
    
    %% Nhánh Micro (Chunks)
    Branch -->|"Nhánh Vi mô (Micro)"| Chunker["4B. Fine Chunking Engine: Đoạn 512 tokens + Overlap 50 tokens"]
    Chunker --> EmbedWorker["5. OpenAI text-embedding-3-small: Sinh Vector Dense 1536 chiều"]
    Chunker --> LexicalWorker["6. PostgreSQL Full-Text Parser: Tạo to_tsvector english content"]
    
    EmbedWorker --> VecStore[("Vector Store Index: PostgreSQL pgvector HNSW")]
    LexicalWorker --> FTSStore[("Inverted Index: PostgreSQL GIN tsvector")]
    Chunker --> BBoxStore[("Evidence Store: Bảng document_chunks kèm JSONB BBoxes")]

    classDef proc fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    classDef store fill:#f8fafc,stroke:#1d4ed8,stroke-width:2px;
    class Parser,SumExtract,Chunker,EmbedWorker,LexicalWorker proc;
    class SumStore,VecStore,FTSStore,BBoxStore store;
```

#### 2. Sơ Đồ Tầng 2: Trợ Lý Hỏi Đáp & Suy Luận Đọc Sâu (Online Agentic Inference Runtime)
*(Kích hoạt thời gian thực mỗi khi học giả đặt câu hỏi trong phiên đọc PDF)*

```mermaid
flowchart TD
    UserQuery(["Query Học Giả (VD: 'Công thức AR tính thế nào?')"]) --> AgentBox

    subgraph AgentBox ["Agents (Lõi Điều Phối)"]
        Condense["1. Condense History (Type II): Ghép 5 lượt chat gần nhất"] --> HyDE["2. HyDE Generator: Sinh Virtual Document Tiếng Anh"]
        HyDE --> Router{"3. Query Router: Phân loại ý định"}
    end

    %% Định tuyến
    Router -->|"Hỏi tổng quan bài báo"| ReadSummary["Đọc Summary Index"]
    Router -->|"Truy vết công thức / số liệu"| HybridRetriever["Dual-Stream Retrieval"]

    %% Đọc từ kho dữ liệu đã được Tầng 1 chuẩn bị
    ReadSummary -.-> SumStore[("Summary Index")]
    HybridRetriever -.->|"HNSW Cosine <=>"| VecStore[("Vector Store Index")]
    HybridRetriever -.->|"BM25 ts_rank_cd"| FTSStore[("Inverted Index GIN")]

    %% Reranking & CRAG
    VecStore & FTSStore --> RRF["4. Reciprocal Rank Fusion (k=60)"]
    RRF --> CRAG{"5. CRAG Evaluator (Ngưỡng tau = 0.35)"}
    
    CRAG -->|"Tin cậy cao (tau >= 0.35)"| EvidencePack["Top Evidence Chunks + Bounding Boxes"]
    CRAG -->|"Công thức bị đứt đoạn / Mơ hồ"| Expand["Window Expansion [i-1, i+1]"] --> EvidencePack
    CRAG -->|"Không liên quan (tau < 0.20)"| Abstain["Chủ động từ chối (Active Abstention)"]

    %% Sinh câu trả lời & Thị giác
    EvidencePack --> LLM["6. LLM Reasoner Engine"]
    UserQuery --> LLM
    LLM -.->|"Tool Choice (Yêu cầu mở rộng ngữ cảnh)"| Router
    
    LLM --> StreamOut["7. SSE Streaming & Markdown KaTeX"]
    StreamOut --> Canvas["8. PDF Canvas Highlight (Golden Bounding Box)"]

    classDef agentStyle fill:#eff6ff,stroke:#2563eb,stroke-width:2px;
    classDef storageStyle fill:#f8fafc,stroke:#1d4ed8,stroke-width:2px;
    classDef viewStyle fill:#f0fdf4,stroke:#16a34a,stroke-width:2px;
    class AgentBox,RRF agentStyle;
    class SumStore,VecStore,FTSStore storageStyle;
    class Canvas,StreamOut viewStyle;
```

### B. Bảng Kiểm Kê Thành Phần Mã Nguồn
| Thành phần | Đường dẫn File | Trạng thái | Nội dung chi tiết |
|---|---|---|---|
| **Sessions API** | [`apps/api/src/api/v1/endpoints/sessions.py`](../../apps/api/src/api/v1/endpoints/sessions.py) | **MODIFY** | Đã có Session CRUD. Cần bổ sung `DELETE /api/v1/sessions/{id}/documents/{doc_id}` để đóng 1 bài báo khỏi thanh Tab (giải phóng slot 5 bài). |
| **Chat SSE Endpoint** | `POST /api/v1/sessions/{id}/messages` trong `sessions.py` | **MODIFY** | Chuẩn hóa sự kiện SSE unbuffered: `token`, `citation`, `bridge_hint`, `done`, `error`; bổ sung `DELETE /api/v1/sessions/{id}/messages` (Reset Chat). |
| **Notes API** | [`apps/api/src/api/v1/endpoints/notes.py`](../../apps/api/src/api/v1/endpoints/notes.py) | **KEEP** | Giữ nguyên CRUD ghi chú: `POST /`, `GET /`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`. |
| **Embedding Service** | `apps/api/src/api/services/embedding_service.py` | **CREATE** | Động cơ sinh vector Dense 1536 chiều bằng OpenAI `text-embedding-3-small` với cơ chế batching ($\le 128$ chunks/call). |
| **Chat Service** | [`apps/api/src/api/services/session_chat_service.py`](../../apps/api/src/api/services/session_chat_service.py) | **MODIFY** | Tích hợp Agent Query Transformation (Condense + HyDE), Dual-Stream HNSW Cosine + BM25 tsvector qua RRF $k=60$, CRAG thresholding và Window Expansion. |
| **PDF Canvas** | `apps/web/src/features/reader/components/PdfCanvasViewer.tsx` | **KEEP** | Render canvas PDF, lớp vẽ `BboxHighlightLayer.tsx`, sự kiện lắng nghe cuộn trang. |
| **Abstract Viewer** | `apps/web/src/features/reader/components/AbstractCardViewer.tsx` | **CREATE** | Tạo mới component hiển thị thẻ tóm tắt học thuật khi bài báo ở trạng thái `abstract_only`. |
| **Selection Menu** | `apps/web/src/features/reader/components/ScholarSelectionMenu.tsx` | **KEEP** | Menu nổi khi bôi đen văn bản: `[💬 Đưa vào Chat]`, `[📝 Vào sổ tay]`, `[📋 Trích dẫn]`. |

---

## 3. Mô Hình Dữ Liệu & Ràng Buộc Phiên Đọc (`Database Invariants`)

### A. Ràng Buộc Tối Đa 5 Bài Báo Mỗi Phiên (`session_documents`)
- Khóa chính: `PRIMARY KEY (session_id, document_id)`.
- Ràng buộc số lượng: Trước khi thực hiện `INSERT INTO session_documents`, Backend bắt buộc đếm số bài hiện có:
  $$\text{SELECT COUNT(*) FROM session_documents WHERE session\_id = :session\_id}$$
  Nếu `count >= 5`, ném lỗi `HTTP 409 CONFLICT` với mã `MAX_SESSION_DOCUMENTS_REACHED` kèm thông báo: *"Phiên đọc đã đạt giới hạn tối đa 5 tab bài báo để bảo toàn chất lượng hội thoại của AI."*
- **Xử lý UX Thân Thiện (Tab Eviction Dialog):** Khi nhận mã lỗi này (từ Bảng Tham Khảo & Lộ Trình Socratic hoặc Gợi ý Bắc cầu), giao diện Frontend hiển thị hộp thoại chọn nhanh: *"Bạn muốn đóng bớt tab bài báo nào để mở bài mới?"* liệt kê danh sách 5 bài đang mở. Khi người dùng chọn 1 bài, Frontend tự động gọi `DELETE /api/v1/sessions/{id}/documents/{doc_id}` rồi thực hiện nạp bài mới ngay lập tức mà không làm đứt mạch làm việc.

### B. Lưu Trữ Trạng Thái Viewport (`research_sessions.viewport_state`)
Mỗi khi người dùng cuộn trang PDF hoặc đổi tỷ lệ zoom trên giao diện, Frontend gọi debounce (500ms) tới `PATCH /api/v1/sessions/{id}/viewport` để lưu:
```json
{
  "active_document_id": "1a2b3c4d-...",
  "page": 4,
  "zoom_ratio": 1.25,
  "scroll_top": 350.5
}
```
Khi người dùng mở lại phiên đọc, giao diện khôi phục chính xác trang và vị trí đang đọc dở.

---

## 4. Hợp Đồng API REST & Luồng Streaming SSE (API & SSE Contracts)

### A. Quản Lý Phiên Đọc & Tab Bài Báo (`sessions.py`)

#### 1. Đóng một bài báo khỏi phiên (`DELETE /api/v1/sessions/{id}/documents/{document_id}`)
- **Mục đích:** Gỡ bài báo ra khỏi phiên đọc hiện tại (giải phóng slot trong giới hạn 5 bài). Không xóa file PDF gốc trong CSDL.
- **Headers:** `Authorization: Bearer <token>`
- **Response (HTTP 204 No Content):** Không có nội dung.
- **Xử lý:** Xóa bản ghi trong `session_documents`. Nếu `document_id` đang là `active_document_id`, tự động chuyển `active_document_id` sang một bài báo còn lại trong phiên.

#### 2. Cập nhật viewport (`PATCH /api/v1/sessions/{id}/viewport`)
- **Request Body:**
  ```json
  {
    "active_document_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "page": 3,
    "zoom_ratio": 1.5,
    "scroll_top": 210.0
  }
  ```
- **Response (HTTP 200 OK):** Trả về phiên đọc đã cập nhật.

---

### B. Luồng Streaming Hỏi Đáp RAG (`POST /api/v1/sessions/{id}/messages`)

- **Headers:** `Authorization: Bearer <token>`, `Content-Type: application/json`, `Accept: text/event-stream`
- **Request Body:**
  ```json
  {
    "content": "Giải thích trực quan ý nghĩa toán học của công thức Attention trong bài?",
    "document_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "selected_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V",
    "selected_page": 4
  }
  ```
- **Luồng Sự Kiện SSE (Unbuffered Server-Sent Events):**

1. **Sự kiện `citation` (Bắn ra ngay khi trích xuất được chunk liên quan):**
   ```text
   event: citation
   data: {"citation_id": 1, "document_id": "1a2b...", "paper_title": "Attention Is All You Need", "page_number": 4, "bounding_boxes": [[120, 340, 480, 390]], "snippet": "Attention(Q, K, V) = softmax..."}
   ```
2. **Sự kiện `token` (Nội dung câu trả lời Markdown streaming thời gian thực):**
   ```text
   event: token
   data: {"delta": "Công "}

   event: token
   data: {"delta": "thức này biểu diễn..."}
   ```
3. **Sự kiện `bridge_hint` (Gợi ý Lộ trình Học Tuần tự nếu câu hỏi chạm vào khái niệm nền tảng):**
   ```text
   event: bridge_hint
   data: {"ref_index": 14, "concept_name": "Bahdanau Attention", "paper_title": "Neural Machine Translation by Jointly Learning to Align and Translate", "authors": "Bahdanau et al.", "year": 2014, "can_ingest": true}
   ```
4. **Sự kiện `done` (Kết thúc lượt trả lời):**
   ```text
   event: done
   data: {"turn_id": "9f8e7d6c-...", "trace_id": "trace-chat-89a1", "prompt_tokens": 820, "completion_tokens": 340}
   ```

#### 3. Xóa sạch lịch sử chat để hỏi lại từ đầu (`DELETE /api/v1/sessions/{id}/messages`)
- **Mục đích:** Xóa toàn bộ bản ghi `session_turns` thuộc `session_id` đó.
- **Response (HTTP 204 No Content).**

### C. Ma Trận Mã Lỗi Chuẩn Hóa Phiên Đọc Sâu (Deterministic Deep Reading Error Codes Matrix)

| HTTP Status / SSE Event | Mã lỗi chuẩn (`error.code`) | Điều kiện kích hoạt (Trigger Condition) | Cấu trúc Payload JSON / SSE trả về | Hành vi xử lý tại Frontend / Hệ thống |
| :--- | :--- | :--- | :--- | :--- |
| `404 Not Found` | `SESSION_OR_DOCUMENT_NOT_FOUND` | Truy cập `session_id`, `document_id` hoặc `note_id` không tồn tại hoặc thuộc quyền sở hữu của `user_id` khác. | `{"error": {"code": "SESSION_OR_DOCUMENT_NOT_FOUND", "message": "Không tìm thấy phiên đọc hoặc tài liệu yêu cầu.", "trace_id": "..."}}` | Chuyển hướng người dùng về trang danh sách phiên đọc `/dashboard`. |
| `409 Conflict` | `MAX_SESSION_DOCUMENTS_REACHED` | Thêm bài báo mới vào `session_documents` khi phiên đọc đã mở đủ 5/5 bài báo. | `{"error": {"code": "MAX_SESSION_DOCUMENTS_REACHED", "message": "Phiên đọc đã đạt giới hạn tối đa 5 tab bài báo.", "current_count": 5, "max_limit": 5, "trace_id": "..."}}` | Mở hộp thoại **Tab Eviction Dialog** cho phép học giả chọn đóng nhanh 1 bài báo đang mở rồi tự động nạp bài mới. |
| `422 Unprocessable Entity` | `SESSION_NO_ACTIVE_DOCUMENTS` | Gửi tin nhắn hỏi đáp `POST /api/v1/sessions/{id}/messages` khi phiên đọc chưa có bài báo nào được gắn vào (`count == 0`). | `{"error": {"code": "SESSION_NO_ACTIVE_DOCUMENTS", "message": "Vui lòng thêm ít nhất 1 bài báo vào phiên trước khi đặt câu hỏi.", "trace_id": "..."}}` | Hiển thị thông báo nhắc chọn bài báo trên khung Chat và mở modal chọn tài liệu. |
| `SSE event: error` | `GROUNDED_CITATIONS_NOT_FOUND` | Truy vấn Hybrid RAG không tìm thấy đoạn trích nào vượt ngưỡng liên quan tối thiểu đối với câu hỏi số liệu cụ thể. | `event: error\ndata: {"code": "GROUNDED_CITATIONS_NOT_FOUND", "message": "Thông tin này không được đề cập trong các tài liệu đang mở."}` | Hiển thị bong bóng phản hồi trung thực báo rõ tài liệu không đề cập, tuyệt đối không sinh huy hiệu trích dẫn giả. |
| `SSE event: error` | `LLM_STREAM_INTERRUPTED` | Kết nối tới nhà cung cấp LLM bị đứt giữa chừng hoặc khóa BYOK của người dùng hết hạn mức khi đang truyền luồng SSE. | `event: error\ndata: {"code": "LLM_STREAM_INTERRUPTED", "message": "Luồng phản hồi AI bị gián đoạn. Vui lòng thử lại.", "trace_id": "..."}` | Giữ lại phần văn bản đã hiển thị, đính kèm nút `[🔄 Thử gửi lại câu hỏi]` ngay dưới tin nhắn. |

---

## 5. Thiết Kế Thuật Toán Advanced RAG & Hàng Rào Chống Ảo Giác (Academic Advanced RAG Engine)

### A. Mô Hình Phân Tách Hai Tầng (Two-Tier Architectural Decoupling)

Để bảo đảm tính ổn định và triệt tiêu toàn bộ điểm mù kỹ thuật, hệ thống phân định rõ ràng giữa hai giai đoạn:

1. **Tầng 1 (Offline Ingestion & Dual Indexing Pipeline):**
   - Xảy ra khi tài liệu được tải lên hoặc khi người dùng bấm "Mở Đọc Sâu" từ kết quả tìm kiếm.
   - Chạy bất đồng bộ qua `BackgroundTasks` trong FastAPI, đảm bảo không khóa luồng I/O người dùng.
   - **Bất biến kỹ thuật bắt buộc:** 100% chunks phải được sinh vector Dense 1536 chiều qua model `text-embedding-3-small`, tuyệt đối cấm lưu `embedding = NULL`.
   - Sinh đồng thời **Summary Index** (Abstract, đề mục, kết luận) và **Vector Store Index** (512-token chunks kèm mảng Bounding Box chuẩn hóa $[0..1000]$).

2. **Tầng 2 (Online Agentic Inference & Visual Grounding Runtime):**
   - Kích hoạt mỗi khi học giả gửi câu hỏi trong phiên đọc.
   - Vận hành theo mô hình Agentic RAG với vòng lặp phản hồi (`Tool Choice`), xóa bỏ rào cản đa ngôn ngữ bằng `HyDE` và bảo toàn công thức toán học đa dòng qua cơ chế `CRAG Window Expansion`.

---

### B. Đặc Tả 7 Khối Chức Năng Tiền Định (Deterministic Component I/O Contracts)

Mọi kỹ sư và mô hình AI thực thi bắt buộc phải tuân thủ nghiêm ngặt hợp đồng đầu vào (Input) và đầu ra kỳ vọng (Expected Output) của từng khối:

```
+-----------------------------------------------------------------------------------+
| 1. INDEXING (PyMuPDF Layout-Aware Chunking + text-embedding-3-small + tsvector)    |
| Input: File PDF gốc (<= 50MB, <= 100 trang)                                       |
| Output: Bảng document_chunks có embedding vector(1536) & bounding_boxes JSONB      |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. QUERY IMPROVEMENT (Condense History Type II + HyDE English Virtual Document)   |
| Input: user_query (Tiếng Việt/Anh) + 5 turns chat_history                         |
| Output: standalone_query (text) + hyde_vector (1536-dim float array)              |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. QUERY ROUTING (Semantic Scope Router)                                          |
| Input: standalone_query + session_scope                                            |
| Output: ROUTE_TYPE ("SUMMARY_INDEX" hoặc "DEEP_CHUNKS")                            |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 4. RETRIEVE & RANKING (Dual-Stream Hybrid Search + RRF k=60)                      |
| Input: hyde_vector (Dense) + standalone_query (Sparse) + active_doc_ids           |
| Output: Top 5 candidate chunks kèm rrf_score & cosine_similarity                  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 5. CRAG EVALUATION & WINDOW EXPANSION (Confidence Gate & Multiline Expansion)     |
| Input: Top candidate chunks + max cosine_similarity (tau)                         |
| Process: tau >= 0.35 (Correct) | 0.20 <= tau < 0.35 (Ambiguous) -> [i-1, i+1]     |
| Output: final_evidence_chunks (đã bao trọn công thức) HOẶC cờ ABSTAIN              |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 6. PROMPT AUGMENTATION (Evidence Packager & Citation Anchors)                     |
| Input: final_evidence_chunks + standalone_query                                    |
| Output: Augmented System Prompt cô lập với chỉ thị gắn thẻ [cite:chunk_id:page]   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 7. GENERATION & VISUAL PROOF (Streaming Reasoner & Golden BBox Canvas)            |
| Input: Augmented Prompt gửi tới LLM (GPT-4o / Claude 3.5 Sonnet)                  |
| Output: SSE Stream (Markdown KaTeX) + Trích xuất tọa độ BBox vẽ khung vàng        |
+-----------------------------------------------------------------------------------+
```

#### Chi tiết Hợp đồng Dữ liệu từng Khối:

1. **Khối 1: INDEXING & DUAL STORE PIPELINE**
   * **Input:** File PDF nhị phân (`bytes`), `document_id` (UUID), `user_id` (UUID).
   * **Process:** 
     - PyMuPDF chia cột đọc (Gutter Detection). Cắt lát: 512 tokens, bước trượt 50 tokens.
     - Chuẩn hóa tọa độ Bounding Box về $[0..1000]$: `{"x": float, "y": float, "width": float, "height": float}`.
     - Gọi `OpenAI text-embedding-3-small` theo batch $\le 128$ chunks để tính vector dense 1536 chiều.
     - Phân tích từ khóa toàn văn tạo cột `content_tsv` bằng `to_tsvector('english', content)`.
   * **Expected Output:**
     ```json
     {
       "document_id": "6439868d-b7e0-4bd4-9db5-ff94f1ff3adc",
       "chunk_index": 19,
       "page_number": 3,
       "content": "Answer Relevance (AR) is defined as...",
       "embedding": [0.0124, -0.0451, ..., 0.0892],
       "bounding_boxes": [{"x": 120.5, "y": 450.2, "width": 410.0, "height": 85.4}]
     }
     ```

2. **Khối 2: QUERY IMPROVEMENT (Chat Engine Type II & HyDE)**
   * **Input:** `raw_query` (string), `chat_history` (list 5 turns gần nhất).
   * **Process:**
     - LLM tạo `condensed_query` độc lập ngữ cảnh.
     - HyDE Prompt sinh đoạn văn giả định học thuật Tiếng Anh (Virtual Document) dài 100-150 từ chứa các thuật ngữ toán học kỳ vọng.
     - Gọi `embedding_service` để vector hóa Virtual Document thành $\mathbf{u}_{\text{hyde}} \in \mathbb{R}^{1536}$.
   * **Expected Output:**
     ```json
     {
       "condensed_query": "Công thức tính Answer Relevance (AR) trong Ragas",
       "hyde_text": "Answer Relevance (AR) in Ragas is calculated by generating synthetic questions...",
       "hyde_vector": [0.0115, -0.0389, ..., 0.0711]
     }
     ```

3. **Khối 3: QUERY ROUTING (Semantic Scope Router)**
   * **Input:** `condensed_query`, `active_document_ids`.
   * **Process:** Phân loại ý định người dùng (Ý định vĩ mô như Tóm tắt/Đóng góp $\rightarrow$ `SUMMARY_INDEX`; Ý định vi mô như Công thức/Thực nghiệm/Số liệu $\rightarrow$ `DEEP_CHUNKS`).
   * **Expected Output:** `{"route": "DEEP_CHUNKS", "target_doc_ids": ["6439868d-..."]}`.

4. **Khối 4: RETRIEVE & RANKING (Dual-Stream Hybrid Search + RRF)**
   * **Input:** `hyde_vector`, `condensed_query`, `active_doc_ids`, `user_id`.
   * **Process:** Thực thi câu lệnh SQL CTE kết hợp HNSW Cosine distance và Full-Text Search ts_rank_cd qua thuật toán Reciprocal Rank Fusion ($k=60$).
   * **Expected Output:** Danh sách Top 5 candidate chunks có điểm RRF cao nhất.

5. **Khối 5: CRAG EVALUATION & WINDOW EXPANSION**
   * **Input:** Top candidate chunks, điểm tương đồng cao nhất $\tau = \max(\text{cosine\_similarity})$.
   * **Process:**
     - **$\tau \ge 0.35$ (Correct):** Giữ nguyên Top chunks.
     - **$0.20 \le \tau < 0.35$ (Ambiguous / Multiline Formula Split):** Tự động truy vấn bổ sung các chunk lân cận $[i-1, i+1]$ trên cùng trang để gom trọn vẹn công thức hoặc định lý.
     - **$\tau < 0.20$ (Incorrect):** Bật cờ `abstain = True`, không gửi context rác cho LLM.
   * **Expected Output:**
     ```json
     {
       "crag_verdict": "AMBIGUOUS_EXPANDED",
       "final_chunks": [
         {"chunk_index": 18, "page": 3, "content": "..."},
         {"chunk_index": 19, "page": 3, "content": "AR = (1/n) * sum(cos(q, q_i))..."},
         {"chunk_index": 20, "page": 3, "content": "where q is the query vector..."}
       ],
       "abstain": false
     }
     ```

6. **Khối 6: PROMPT AUGMENTATION**
   * **Input:** `final_chunks`, `condensed_query`.
   * **Process:** Ghép các chunk vào khối `[CONTEXT]` với chỉ thị: Mỗi câu khẳng định hoặc công thức toán học bắt buộc phải gắn thẻ neo `[cite:chunk_id:page]`.
   * **Expected Output:** Chuỗi Prompt được kiểm duyệt sạch sẽ.

7. **Khối 7: GENERATION & VISUAL PROOF (Streaming & Golden Bounding Box)**
   * **Input:** Augmented Prompt.
   * **Process:** LLM sinh streaming token; Backend regex tách thẻ `[cite:chunk_id:page]` và đẩy event SSE `citation` chứa mảng `bounding_boxes`. Frontend React Canvas nhận sự kiện, tự động cuộn trang và vẽ **Khung viền vàng nhấp nháy** bao quanh công thức.
   * **Expected Output:** Phản hồi hiển thị chuẩn KaTeX kèm Bounding Box vàng chính xác $\text{IoU} \ge 0.85$.

---

### C. Truy Vấn Hybrid Search Trực Tiếp Trong PostgreSQL (RRF k=60)

`SessionChatService` thực thi truy vấn trực tiếp trong PostgreSQL kết hợp **Vector Cosine (`pgvector`)** qua vector HyDE và **Full-Text Search (`tsvector`)** qua thuật toán Reciprocal Rank Fusion ($k=60$):

```sql
WITH vector_ranks AS (
    SELECT id, document_id, chunk_index, page_number, content, bounding_boxes,
           (1.0 - (embedding <=> :hyde_vector)) AS cosine_sim,
           ROW_NUMBER() OVER (ORDER BY embedding <=> :hyde_vector) AS rank_vec
    FROM document_chunks
    WHERE document_id IN (:active_doc_ids) AND user_id = :user_id
      AND embedding IS NOT NULL
    LIMIT 25
),
fts_ranks AS (
    SELECT id, document_id, chunk_index, page_number, content, bounding_boxes,
           ts_rank_cd(content_tsv, plainto_tsquery('english', :fts_query)) AS fts_score,
           ROW_NUMBER() OVER (ORDER BY ts_rank_cd(content_tsv, plainto_tsquery('english', :fts_query)) DESC) AS rank_fts
    FROM document_chunks
    WHERE document_id IN (:active_doc_ids) AND user_id = :user_id
      AND content_tsv @@ plainto_tsquery('english', :fts_query)
    LIMIT 25
)
SELECT COALESCE(v.id, f.id) AS chunk_id,
       COALESCE(v.document_id, f.document_id) AS document_id,
       COALESCE(v.chunk_index, f.chunk_index) AS chunk_index,
       COALESCE(v.page_number, f.page_number) AS page_number,
       COALESCE(v.content, f.content) AS text_content,
       COALESCE(v.bounding_boxes, f.bounding_boxes) AS bounding_boxes,
       COALESCE(v.cosine_sim, 0.0) AS max_cosine_sim,
       (COALESCE(1.0 / (60 + v.rank_vec), 0.0) + COALESCE(1.0 / (60 + f.rank_fts), 0.0)) AS rrf_score
FROM vector_ranks v
FULL OUTER JOIN fts_ranks f ON v.id = f.id
ORDER BY rrf_score DESC
LIMIT 5;
```

---

### D. Hàng Rào Bảo Vệ & Cơ Chế Agent Feedback Loop (Tool Choice)

1. **Vòng lặp Phản hồi của Agent (Feedback Loop):**
   - Khi LLM nhận thấy `Retrieval Context` bị ngắt quãng giữa công thức hoặc thiếu định nghĩa biến số, LLM kích hoạt sự kiện gọi công cụ ngầm (`Tool Choice: expand_context(document_id, page_number, chunk_index, direction="both")`).
   - Service tự động nạp bổ sung chunk $[i-1, i+1]$ và tái kích hoạt lượt suy luận trước khi gửi token ra giao diện.

2. **Hàng rào Bảo vệ theo Trạng thái Tài liệu (Guardrail Rules):**
   - **Tài liệu đang xử lý (`status='parsing'`):** Chỉ nạp bản tóm tắt từ `documents.summary_metadata` vào ngữ cảnh; kèm thông báo tiến trình bóc tách ngầm cho học giả.
   - **Tài liệu chỉ có Tóm tắt (`status='abstract_only'`):** Tuyệt đối cấm suy diễn số liệu thực nghiệm chi tiết; hướng dẫn học giả tải file PDF cá nhân lên để đọc sâu.
   - **Chủ động từ chối (Active Abstention):** Khi điểm $\tau < 0.20$, hệ thống trả về thông báo trung thực: *"Tài liệu không đề cập đến công thức hoặc dữ liệu này"*, triệt tiêu 100% ảo giác.

---

### E. Bảng Phân Tích Khắc Phục Triệt Để 2 Lỗi Kỹ Thuật Đã Chứng Minh

| Lỗi phát hiện trên thực tế | Nguyên nhân gốc rễ trong mã nguồn | Giải pháp Advanced RAG chuẩn hóa trong Spec |
| :--- | :--- | :--- |
| **"AI bảo không có công thức $AR$ trong bài báo Ragas"** | 1. `document_service.py` lưu `embedding = None` khi nạp file.<br/>2. `session_chat_service.py` gọi hàm tìm kiếm nhưng truyền `query_embedding = None`.<br/>3. Tìm kiếm từ khóa Tiếng Việt *"Công thức AR"* trên bài báo Tiếng Anh trả về 0 kết quả. | **Khối 1 (Indexing):** Ép buộc gọi `embedding_service` sinh vector 1536 chiều.<br/>**Khối 2 (HyDE):** Tự động sinh Virtual Document Tiếng Anh và đối soát qua chỉ mục HNSW vector, khớp trúng Chunk 19/20 trên Trang 3. |
| **"Khung viền vàng Bounding Box bị lệch trang hoặc biến mất"** | 1. Do truy vấn rỗng, hệ thống lấy nhầm chunk Trang 1 (Abstract) hoặc không có tọa độ.<br/>2. Các bài báo "Mở Đọc Sâu" bị kẹt ở `status='processing'` với 0 chunks do quên gọi background worker. | **Khối 4 & 5 (RRF & CRAG):** RRF đưa đúng chunk Trang 3 lên đầu bảng; CRAG mở rộng cửa sổ bao trọn công thức. Sửa `open_reading_session` kích hoạt background ingestion tự động. |

---

## 6. Thiết Kế Giao Diện & Tương Tác Frontend (`apps/web`)

### A. Tương Tác Hai Chiều: Chat Huy Hiệu $\leftrightarrow$ PDF Bounding Box
1. **Từ Chat sang PDF:**
   - Người dùng bấm vào huy hiệu `[📄 Attention Is All You Need • Trang 4]`.
   - Global Event Bus phát sự kiện `NAVIGATE_TO_CITATION`:
     ```typescript
     window.dispatchEvent(new CustomEvent("scholar:focus-bbox", {
       detail: { documentId, pageNumber: 4, boundingBoxes: [[120, 340, 480, 390]] }
     }));
     ```
   - `PdfCanvasViewer.tsx` tự động chuyển Tab nếu bài báo khác đang active, cuộn trang mượt đến trang 4 và kích hoạt `BboxHighlightLayer.tsx` vẽ khung viền vàng nhấp nháy trong 3 giây.
2. **Từ PDF sang Chat:**
   - Người dùng dùng chuột bôi đen đoạn văn trên PDF.
   - `ScholarSelectionMenu.tsx` hiện ra ngay phía trên con trỏ chuột.
   - Bấm `[💬 Đưa vào Chat]`: Tự động chèn nội dung bôi đen vào ô nhập chat bên phải kèm chip hiển thị: `Đoạn trích từ Trang 4 [✕]`.

### B. Nút Dừng Trả Lời & Reset Chat
1. **Nút `[⏹️ Dừng trả lời]`:** Khi luồng SSE đang nhận dữ liệu, nút Gửi chuyển thành nút Dừng màu đỏ. Bấm nút sẽ gọi `AbortController.abort()`, ngắt ngay kết nối stream và giữ lại các đoạn chữ đã in ra.
2. **Nút `[🔄 Reset Chat]`:** Trên thanh tiêu đề chat, nút Reset mở modal xác nhận: *"Bạn có muốn xóa toàn bộ lịch sử hỏi đáp của phiên đọc này để bắt đầu lại không?"*. Xác nhận sẽ gọi `DELETE /api/v1/sessions/{id}/messages`.

### C. Thanh Nhập Liệu Tối Giản & Popover Tinh Chỉnh Suy Luận Đa Nhà Cung Cấp (Vendor-Agnostic Reasoning Popover)

Theo định hướng giao diện tối giản 80/20 và loại bỏ hoàn toàn các thành phần dư thừa (như icon bàn tay), thanh nhập liệu được chuẩn hóa thành một khối Pill thống nhất (`DashboardChatInputBox.tsx`) với cơ chế điều khiển suy luận sâu tách lớp độc lập với nhà cung cấp:

```
+-------------------------------------------------------------------------+
|                               [ High ] (↺)                             |
|                                5.6 Luna >                               |
|                     (•)-------(•)-------(•)=======●                     |
|                     Off       Low       Med      High                   |
+-------------------------------------------------------------------------+
| [+] Đính kèm PDF... | Đặt câu hỏi về tài liệu...        | [🧠]  [↑]     |
+-------------------------------------------------------------------------+
```

1. **Thanh Nhập Liệu Chuẩn Hóa (Chat Input Pill):**
   - **Bên trái:** Nút `+` (`+ Do anything` / Đính kèm bài báo PDF hoặc thêm ngữ cảnh).
   - **Trung tâm:** `textarea` tự động co giãn độ cao theo độ dài văn bản (tối đa 240px).
   - **Bên phải:**
     - Nút **Bộ não (Reasoning Control)**: Kích hoạt Popover tinh chỉnh mức độ tư duy. Khi đang bật (`low`/`medium`/`high`), icon có viền sáng xanh dương nhạt.
     - Nút **Gửi (ArrowUp)**: Nút tròn mũi tên gửi câu hỏi.
     - *(Tuyệt đối không hiển thị icon Bàn tay hay các icon tính năng chưa hoàn thiện)*.

2. **Popover Tinh Chỉnh Suy Luận (Reasoning Popover):**
   - **Vị trí hiển thị:** Nổi ngay phía trên icon Bộ não, tự động đóng khi nhấp ra ngoài (click-outside).
   - **Tiêu đề trạng thái:** Hiển thị mức độ hiện tại bằng chữ lớn màu xanh dương (ví dụ: `High` với mã màu `#38bdf8`), kèm icon reset/hoàn tác ở góc phải để trở về mức mặc định `High`.
   - **Định danh mô hình:** Ghi rõ `5.6 Luna >` (cho phép người dùng nhận diện mô hình đang tương tác).
   - **Thanh trượt 4 nấc (Stepped Slider):** Gồm 4 điểm dừng định lượng:
     - `Off`: Tắt suy luận, mô hình trả lời trực tiếp tốc độ cao.
     - `Low`: Suy luận ngắn gọn, tập trung trả lời câu hỏi trực tiếp.
     - `Medium`: Suy luận cân bằng, rà soát logic trước khi phản hồi.
     - `High`: Suy luận chuyên sâu (Socratic Deep Reasoning), mổ xẻ đa chiều các bằng chứng khoa học.

3. **Kiến Trúc Lục Giác & Ánh Xạ Adapter Độc Lập Nhà Cung Cấp (Vendor-Agnostic Mapping):**
   Để bảo đảm hệ thống không bị "khóa cứng" vào OpenAI (Vendor Lock-in), tầng Domain và UI chỉ giao tiếp qua Value Object trung lập:
   $$\text{ReasoningEffortLevel} \in \{\text{'off'},\ \text{'low'},\ \text{'medium'},\ \text{'high'}\}$$
   Tầng Adapter (`apps/api/src/api/adapters/`) chịu trách nhiệm ánh xạ tương thích với từng SDK được cấu hình:

| Nhà cung cấp / Model | Nấc `Off` | Nấc `Low` | Nấc `Medium` | Nấc `High` |
| :--- | :--- | :--- | :--- | :--- |
| **OpenAI (`5.6-luna`, `o3`)** | Bỏ qua hoặc `null` | `reasoning_effort="low"` | `reasoning_effort="medium"` | `reasoning_effort="high"` |
| **Google Gemini (Thinking)** | `thinking_budget=0` | `thinking_budget=1024` | `thinking_budget=4096` | `thinking_budget=16384` |
| **Anthropic Claude (Thinking)** | `type="disabled"` | `budget_tokens=2048` | `budget_tokens=8192` | `budget_tokens=32768` |
| **Local / DMR (DeepSeek R1)** | Thêm chỉ thị trả lời nhanh | Kích hoạt nấc CoT ngắn | Kích hoạt CoT tiêu chuẩn | Kích hoạt CoT chuyên sâu |

---

## 7. Tập Tin Neo Tham Chiếu Trong Codebase (Codebase Anchors)

Mọi thay đổi kỹ thuật của phân hệ Phiên đọc sâu và Hỏi đáp Bounding Box phải tuân thủ và tham chiếu từ các tệp sau:

| Vai trò kiến trúc | Tệp neo chuẩn mực trong repo | Nguyên tắc bắt chước |
| :--- | :--- | :--- |
| **Session Endpoints Pattern** | [`apps/api/src/api/v1/endpoints/sessions.py`](../../apps/api/src/api/v1/endpoints/sessions.py) | Tham chiếu cách xử lý Session CRUD, gán/gỡ Tab PDF, và lưu trạng thái viewport. |
| **Chat & RAG Streaming Service** | [`apps/api/src/api/services/session_chat_service.py`](../../apps/api/src/api/services/session_chat_service.py) | Tham chiếu cách sinh SSE stream unbuffered, hybrid RAG và format citation tags. |
| **In-Session Notes API** | [`apps/api/src/api/v1/endpoints/notes.py`](../../apps/api/src/api/v1/endpoints/notes.py) | Tham chiếu CRUD ghi chú gắn Bounding Box và trích dẫn bài báo. |
| **Frontend Reader & Canvas** | `apps/web/src/features/reader/components/PdfCanvasViewer.tsx` | Tham chiếu cách render PDF canvas, đồng bộ zoom và vẽ lớp phủ `BboxHighlightLayer`. |
| **Selection Toolbar** | `apps/web/src/features/reader/components/ScholarSelectionMenu.tsx` | Menu nổi khi bôi đen text: `[💬 Đưa vào Chat]`, `[📝 Vào sổ tay]`, `[📋 Trích dẫn]`. |
| **In-Session Notes Panel** | `apps/web/src/features/notes/components/NotesPanelContainer.tsx` | Ngăn trượt phụ bên phải quản lý các đoạn trích đã ghim. |

---

## 8. Ma Trận Kiểm Thử TDD Bắt Buộc (Deep Reading TDD Matrix)

```mermaid
sequenceDiagram
    autonumber
    actor Scholar as Học Giả
    participant Reader as Không Gian Đọc Sâu
    participant RAG as Động Cơ Hybrid RAG
    participant PG as PostgreSQL (HNSW + FTS)
    participant LLM as Cổng Suy Luận LLM

    Scholar->>Reader: Bôi đen đoạn văn & đặt câu hỏi chuyên sâu
    Reader->>RAG: POST /api/v1/sessions/{id}/messages:stream (SSE)
    RAG->>PG: Truy vấn song song HNSW Cosine + GIN Full-Text Search
    PG-->>RAG: Top-K đoạn văn hợp nhất điểm RRF (k=60) kèm BBox [0..1000]
    RAG->>LLM: Truyền Prompt neo bằng chứng (Grounded Context)
    loop Luồng SSE Không Đệm (Unbuffered Stream)
        LLM-->>Reader: event: token (Văn bản & công thức KaTeX)
        RAG-->>Reader: event: citation (chunk_id, page_number, bbox)
    end
    Scholar->>Reader: Nhấp vào Huy hiệu Trích dẫn [Trang X]
    Reader->>Reader: Tự động chuyển tab, cuộn PDF & tô sáng khung BBox
```

| Tên Test Case | File Kiểm Thử | Mục tiêu kiểm chứng | Kỳ vọng nghiệm thu |
|---|---|---|---|
| `test_session_max_5_documents_limit` | `apps/api/tests/test_session_tabs.py` | Thêm bài báo thứ 6 vào phiên đọc | Trả về `409 Conflict` với mã lỗi `MAX_SESSION_DOCUMENTS_REACHED`. |
| `test_close_document_tab_reassigns_active` | `apps/api/tests/test_session_tabs.py` | Đóng tab bài báo đang active qua `DELETE .../documents/{id}` | Xóa junction row, `active_document_id` tự chuyển sang bài còn lại. |
| `test_hybrid_rag_search_rrf_scoring` | `apps/api/tests/test_session_chat.py` | Thực thi truy vấn Hybrid RAG với mock embedding | Trả về top 5 chunks có `rrf_score` cao nhất từ cả 2 nguồn. |
| `test_chat_sse_stream_event_sequence` | `apps/api/tests/test_session_chat.py` | Gửi câu hỏi và đọc stream response | Nhận đủ các events: `citation`, `token`, `done`. |
| `test_reset_chat_purges_messages_only` | `apps/api/tests/test_session_chat.py` | Gọi `DELETE /api/v1/sessions/{id}/messages` | Bảng `session_turns` bị xóa hết, `research_sessions` vẫn nguyên vẹn. |
| `test_save_and_restore_viewport_state` | `apps/api/tests/test_session_viewport.py` | Gọi `PATCH .../viewport` với `page=4`, lấy lại `GET` | Dữ liệu `viewport_state` trả về đúng `page=4`, `zoom_ratio=1.25`. |

---

## 9. Tiêu Chí Nghiệm Thu Kỹ Thuật (Definition of Done)

- [ ] Giới hạn tối đa 5 bài báo / phiên đọc được thực thi nghiêm ngặt cả ở Frontend lẫn Backend API.
- [ ] Endpoint `DELETE /api/v1/sessions/{id}/documents/{document_id}` cho phép đóng tab an toàn không xóa file gốc.
- [ ] Giao diện hỗ trợ chuyển đổi linh hoạt: hiển thị `PdfCanvasViewer.tsx` khi có PDF và `AbstractCardViewer.tsx` khi bài báo ở dạng tóm tắt.
- [ ] Luồng SSE phát đúng các sự kiện và huy hiệu citation bấm vào là cuộn trang PDF và tô viền vàng Bounding Box.
- [ ] Toàn bộ kịch bản kiểm thử trong Ma trận Kiểm thử Mục 8 đạt `100% PASS`.
