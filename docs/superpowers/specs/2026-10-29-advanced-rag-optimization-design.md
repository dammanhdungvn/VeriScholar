# Design Specification: High-Performance Production Advanced RAG Architecture

- **Document Type:** Technical & Architectural Specification
- **Date:** 2026-10-29
- **Status:** Final Proposed Design (Post-Builder Review)
- **Target Specification:** [`docs/specs/03-sessions-and-deep-reading-spec.md`](../../specs/03-sessions-and-deep-reading-spec.md)
- **Related PRDs:** [`docs/PRD/00-overview-and-cleanup.md`](../../PRD/00-overview-and-cleanup.md), [`docs/PRD/03-sessions-and-deep-reading-crud.md`](../../PRD/03-sessions-and-deep-reading-crud.md)

---

## 1. Intent & The Why

Trong quá trình sử dụng thực tế, các hệ thống RAG cơ bản (Naive RAG) thường bộc lộ sự thiếu hụt nghiêm trọng về chất lượng câu trả lời ("RAG bị ngô nghê"):
1. **Phân mảnh cấu trúc tài liệu:** Các bài báo khoa học (arXiv, IEEE, NeurIPS) có bố cục 2 cột (*two-column format*), chứa nhiều bảng biểu thực nghiệm và công thức toán học. Trình bóc tách văn bản thô (như PyMuPDF text blocks) làm đứt đoạn văn bản giữa 2 cột, biến các bảng số liệu thành các dòng ký tự vô nghĩa, và làm mất cấu trúc công thức. Khi đưa vào mô hình ngôn ngữ lớn (LLM), đầu vào bị hỏng khiến câu trả lời bị sai lệch, thiếu cơ sở, hoặc dẫn tới ảo giác (Hallucination).
2. **Nhiễu ngữ cảnh (Context Pollution):** Tìm kiếm vector thuần túy hoặc tìm kiếm từ khóa đơn lẻ thu về nhiều đoạn văn chứa từ khóa trùng khớp nhưng không có giá trị học thuật. Việc thiếu tầng **Tái xếp hạng (Reranker)** khiến ngữ cảnh gửi cho LLM bị loãng, đẩy các chi tiết mấu chốt ra khỏi tầm chú ý của mô hình.
3. **Thiếu tư duy suy luận khoa học (Lack of CoT Reasoning):** LLM trả lời theo kiểu tổng hợp chung chung thay vì suy luận từng bước (Chain-of-Thought) dựa trên dữ liệu bảng biểu và công thức toán học thực tế.

Mục tiêu của thiết kế này là **nâng cấp toàn diện lõi Advanced RAG của VeriScholar** đạt chuẩn thương mại (Production-ready), đảm bảo 3 tiêu chí: **Tốc độ xử lý nhanh (Build & Query Latency)**, **Chất lượng câu trả lời chuẩn xác vượt trội (SOTA Precision)**, và **Tối ưu hóa tài nguyên (Resource & Cost Efficiency)**, vận hành độc lập hoàn toàn chỉ với **OpenAI API (`OPENAI_API_KEY`)** sẵn có trong hệ thống và các thành phần xử lý nội bộ.

---

## 2. Goals, Non-Goals & Anti-Goals

### 2.1. Goals
- **G1: Bóc tách bảo toàn 100% cấu trúc Bảng biểu & Công thức Toán:** Tự động chuyển đổi bảng số liệu thành bảng Markdown hoàn chỉnh (rõ cột, hàng) và giữ nguyên cú pháp công thức LaTeX, đồng thời lưu trữ chính xác tọa độ hình học `bounding_boxes: [x0, y0, x1, y1, page]`.
- **G2: Tối ưu Tốc độ Nạp (Ingestion Speed < 5s / 10 trang):** Quy trình bóc tách và tạo embedding chạy ngầm bất đồng bộ qua `BackgroundTasks`, không làm nghẽn luồng xử lý của người dùng.
- **G3: Truy xuất 2 tầng (Two-Stage Retrieval) kèm Reranker linh hoạt:**
  - Tầng 1: Thu hồi nhanh (Coarse Retrieval) với HNSW Cosine Vector (`text-embedding-3-small`) + FTS RRF ($K = 20$).
  - Tầng 2: Tái xếp hạng ngữ nghĩa (Semantic Reranker) chọn lọc Top $K = 5$ đoạn văn chuẩn xác nhất thông qua Local ONNX Reranker (không tốn API) hoặc OpenAI Reranker fallback.
- **G4: Phân cấp Ngữ cảnh Mẹ-Con (Parent-Child Context Expansion):** Tìm kiếm trên các đoạn nhỏ (Child Chunks: 200–300 tokens) để bắt trúng ý, nhưng khi trả lời thì mở rộng sang đoạn lớn (Parent Sections: 800–1200 tokens) để LLM nắm trọn vẹn ngữ cảnh lập luận, có cơ chế khử trùng lặp và giới hạn trần `MAX_EVIDENCE_TOKENS = 3500`.
- **G5: Kỹ nghệ Prompt Suy luận Học thuật (Academic CoT Prompting):** Ép LLM suy luận tường minh, giải thích bản chất số liệu/công thức, gắn huy hiệu trích dẫn `[cit_x]` neo thẳng vào Bounding Box của Child Chunk trên PDF Canvas.
- **G6: Đạt chuẩn RAGAS:** Chỉ số *Faithfulness* $\ge 92\%$, *Answer Relevance* $\ge 90\%$.

### 2.2. Non-Goals
- Dựng các cụm máy chủ bên ngoài cồng kềnh (không chạy riêng cụm Elasticsearch, Milvus, hay dịch vụ RAG rời).
- Pre-train hoặc Fine-tune trọng số mô hình LLM nền tảng.
- Bắt buộc phải có thêm các API Key của bên thứ ba ngoài OpenAI (không phụ thuộc vào Cohere hay dịch vụ trả phí khác).

### 2.3. Anti-Goals
- **Không dùng kiến trúc chắp vá ("Frankenstein Architecture"):** Không nhúng toàn bộ cụm dịch vụ RAGFlow cồng kềnh vào máy chủ làm quá tải RAM/CPU.
- **Không làm mất tính năng Bounding Box vàng:** Bất kỳ cải tiến bóc tách nào cũng phải duy trì ánh xạ tọa độ hiển thị lên PDF Viewer gốc.
- **Không trả lời khi không có căn cứ (No Hallucinated Answers):** Tuyệt đối không sinh số liệu hoặc kết luận nếu không có bằng chứng trong tài liệu gốc (Active Abstention).

---

## 3. Architecture Constraints

- **Kiến trúc Lục giác (Hexagonal Architecture):** 
  - `packages/core/`: Định nghĩa thực thể, Value Objects, Port trừu tượng (`IChunkExtractorPort`, `IRerankerPort`, `IRetrievalPort`).
  - `apps/api/`: Cài đặt Adapter cụ thể (`PyMuPDF4LLMChunkExtractor`, `LocalOrOpenAIRerankerAdapter`, `PostgresVectorSearchAdapter`).
- **Kho lưu trữ duy nhất:** Toàn bộ dữ liệu Vector, Văn bản, Đồ thị và Metadata nằm trọn vẹn trong **PostgreSQL 16+ với extension `pgvector`**.
- **Tài nguyên phần cứng & API:** Vận hành mượt mà trên VPS tiêu chuẩn (2–4 vCPU, 8GB RAM). Chỉ yêu cầu `OPENAI_API_KEY` trong `.env`.
- **Quy chuẩn Liêm chính & Học thuật (Rules 5, 6, 7, 8):** Liên kết tương đối, văn phong súc tích, mô hình hóa luồng dữ liệu theo chuẩn bài báo khoa học.

---

## 4. Approaches Considered & Trade-offs

| Tiêu chí so sánh | Phương án 1: Dựng RAGFlow độc lập qua Docker | Phương án 2: Tích hợp Deep Parsing & Reranker nội bộ (ĐÃ CHỌN) | Phương án 3: Kết nối Dify.ai Knowledge Base qua API |
| :--- | :--- | :--- | :--- |
| **Bản chất kiến trúc** | Chạy toàn bộ server RAGFlow (Elasticsearch, Infinity, OCR, MySQL, MinIO). | Giữ nguyên kiến trúc FastAPI + Postgres 16; nâng cấp parser (`pymupdf4llm`), bổ sung Reranker (Local ONNX hoặc OpenAI) và Parent-Child Indexing. | Đẩy tài liệu lên Dify Cloud / Self-hosted, truy vấn qua REST API. |
| **Chất lượng bóc tách tài liệu** | Rất cao (DeepDoc phân tích layout thị giác). | Rất cao (bảo toàn cấu trúc bảng Markdown, công thức LaTeX và tọa độ BBox). | Trung bình (Dify bóc tách PDF văn bản tốt, nhưng yếu ở bảng 2 cột và công thức). |
| **Yêu cầu tài nguyên VPS** | Cực kỳ nặng (tối thiểu 16GB–32GB RAM). | Rất nhẹ (chạy trực tiếp trong process FastAPI hiện có, < 1GB RAM thêm). | Nhẹ (nhưng tốn chi phí thuê ngoài hoặc server riêng). |
| **Độ trễ truy vấn (Latency)** | Cao (qua nhiều chặng microservices mạng). | Thấp (< 800ms cho khâu retrieval + rerank). | Phụ thuộc độ trễ mạng ra server ngoài. |
| **Tương thích Bounding Box** | Không tương thích (RAGFlow không xuất BBox theo định dạng chuẩn của viewer). | Tương thích 100% (mỗi chunk/bảng đều có tọa độ chuẩn hóa $[0..1000]$). | Không hỗ trợ hiển thị Bounding Box trên PDF. |
| **Phụ thuộc API bên ngoài** | Cần server độc lập. | **Chỉ dùng duy nhất `OPENAI_API_KEY`** (kết hợp parser và reranker nội bộ). | Cần API Dify riêng. |
| **Giá trị Đồ án Tốt nghiệp** | Thấp (bị xem là đóng gói giải pháp của bên thứ ba). | Rất cao (thuật toán tự chủ, có cơ sở lý thuyết, đo lường thực nghiệm RAGAS). | Thấp (phụ thuộc nền tảng thương mại). |

**Lý do chọn Phương án 2:** Mang lại chất lượng câu trả lời tương đương RAGFlow nhờ kỹ thuật Deep Parsing và Reranking, nhưng giữ nguyên được sự tinh gọn, không phá vỡ hệ thống Bounding Box vàng, không đòi hỏi API bên ngoài phức tạp, và tạo điểm nhấn khoa học vượt trội cho đồ án tốt nghiệp.

---

## 5. Detailed Technical Design: SOTA 3-Stage Advanced RAG

### 5.1 Giai đoạn 1: Bóc tách Bố cục Nâng cao & Lập chỉ mục Phân cấp (Structure-Aware Ingestion)

1. **Bộ bóc tách nhận thức cấu trúc (Layout-Aware Parser):**
   - Sử dụng `pymupdf4llm` kết hợp engine phân tích bảng `page.find_tables()` có sẵn trong PyMuPDF.
   - **Bảng biểu thực nghiệm:** Nhận diện bảng tự động, chuyển đổi thành cú pháp Markdown Table chuẩn mực (giữ nguyên tiêu đề cột, dòng số liệu), tính toán tọa độ Bounding Box bao quanh toàn bộ bảng.
   - **Công thức Toán học (LaTeX):**
     - Mặc định: Dùng heuristic regex và bộ trích xuất khối văn bản có cấu trúc của `pymupdf4llm` để nhận diện các công thức toán học và bao bọc trong ký hiệu chuẩn `$$...$$` hoặc `\[...\]`.
     - Dự phòng (Fallback): Trong trường hợp khối công thức toán là hình ảnh quét không có text số hóa, hệ thống cắt ảnh bounding box và sử dụng OpenAI Vision (`gpt-4o-mini`) thông qua `OPENAI_API_KEY` đã có để chuyển đổi sang LaTeX chuẩn.
2. **Cơ chế Phân cấp Mẹ-Con (Parent-Child Chunking):**
   - **Child Chunks (200–300 tokens):** Phục vụ tìm kiếm chính xác cao. Mỗi Child Chunk mang `content`, `bounding_boxes: [x0, y0, x1, y1, page]`, vector embedding 1536 chiều (`text-embedding-3-small`), và chỉ mục GIN `content_tsv`.
   - **Parent Section (800–1200 tokens):** Đoạn ngữ cảnh bao quát (tương ứng với một tiêu đề phần/mục H1/H2 trong Markdown, fallback sang cửa sổ 1000 tokens nếu không có tiêu đề). Lưu tại cột `parent_content` của bảng `document_chunks`.

### 5.2 Giai đoạn 2: Truy xuất Hai Tầng & Tái Xếp Hạng Ngữ Nghĩa (Two-Stage Retrieval & Reranker)

1. **Tầng 1 — Coarse Retrieval (Thu hồi sơ bộ):**
   - Truy vấn đồng thời Vector HNSW Cosine (`embedding <=> query_vec`) và Full-Text Search PostgreSQL (`ts_rank_cd(content_tsv, ...)`).
   - Hợp nhất kết quả bằng **Reciprocal Rank Fusion (RRF)** với tham số $k = 60$.
   - Thu về $K_{\text{coarse}} = 20$ Child Chunks ứng viên tiềm năng nhất.
2. **Tầng 2 — Semantic Reranking (Tái xếp hạng ngữ nghĩa):**
   - Đưa $20$ ứng viên qua bộ Reranker với 2 chế độ tùy chọn:
     - **Chế độ A (Khuyến nghị - Thuần nội bộ 0 API cost):** Sử dụng thư viện `flashrank` (ONNX runtime cực nhẹ, model ~100MB, thời gian suy luận ~30-50ms trên CPU, không phụ thuộc internet hay API key ngoài).
     - **Chế độ B (OpenAI Structured Reranking):** Sử dụng `gpt-4o-mini` với structured outputs chấm điểm liên quan từ 0.0 đến 1.0 cho 20 đoạn văn dựa trên `OPENAI_API_KEY`.
   - Lọc các chunk có điểm liên quan $\mathcal{S}_{\text{rerank}} \ge 0.65$. Chọn tối đa $K_{\text{fine}} = 5$ Child Chunks xuất sắc nhất.
3. **Cơ chế Active Abstention & Gợi ý CITES:**
   - Tuân thủ nguyên tắc giới hạn 5 tab của phiên đọc (`03-sessions-and-deep-reading-spec.md`). Nếu điểm liên quan cao nhất $\mathcal{S}_{\text{max}} < 0.35$, hệ thống **không** truy vấn ngầm hay tự nạp các bài báo ngoài phiên.
   - Hệ thống thực hiện **Active Abstention**: Thông báo rõ ràng rằng tài liệu trong phiên hiện tại không đủ thông tin, đồng thời phát sự kiện SSE `bridge_hint` chứa danh sách bài báo liên quan trong đồ thị CITES để người dùng chủ động mở tab mới nếu quan tâm.

### 5.3 Giai đoạn 3: Suy luận Học thuật Đa bước & Bằng chứng Trực quan (Academic CoT Generation)

1. **Đóng gói Ngữ cảnh (Evidence Packing & Deduplication):**
   - Trích xuất `parent_content` của các Child Chunks chiến thắng.
   - **Khử trùng lặp (Deduplication):** Nếu nhiều Child Chunk thuộc cùng một Parent Section, Parent Section đó chỉ xuất hiện duy nhất 1 lần trong prompt.
   - **Trần ngân sách Token:** Giới hạn tối đa `MAX_EVIDENCE_TOKENS = 3500` để đảm bảo tốc độ phản hồi và chống loãng ngữ cảnh.
2. **Kỹ nghệ Prompt Suy luận Học thuật (Academic CoT Prompt):**
   - Ép LLM thực hiện suy luận từng bước (Chain-of-Thought): (1) Phân tích trực giác và bản chất vấn đề, (2) Đọc hiểu số liệu thực nghiệm từ bảng Markdown (cột, hàng) và biểu thức toán LaTeX, (3) Rút ra kết luận khoa học có căn cứ.
   - Gắn huy hiệu trích dẫn `[cit_x]` (ví dụ: `[1]`, `[2]`).
3. **Ánh xạ Tọa độ Bounding Box:**
   - Mỗi huy hiệu `[cit_x]` trong câu trả lời được ánh xạ trực tiếp 1:1 với tọa độ Bounding Box của **Child Chunk** tương ứng (không phải toàn bộ Parent Section), giúp việc nhấp vào trích dẫn trên giao diện tô sáng đúng đoạn văn/bảng số liệu trên PDF Canvas.
   - Tuyệt đối loại bỏ các mã ID nội bộ (`[target_id: uuid]`) khỏi câu trả lời của người dùng nhằm tuân thủ quy chuẩn Radical Minimalism (Rule 6).

---

## 6. What's Left to the Builder (Các quyết định cài đặt chi tiết)

1. **Lựa chọn bộ Reranker:** Builder kích hoạt `flashrank` làm mặc định (chạy local trên CPU, 0 cost), có fallback sang `gpt-4o-mini` nếu không cài đặt được thư viện ONNX.
2. **Di trú cơ sở dữ liệu (Migration):** Thêm trường `parent_content` (Text, nullable) vào bảng `document_chunks` để lưu trữ ngữ cảnh mẹ mà không cần sửa đổi cấu trúc bảng phức tạp.
3. **Cập nhật Đặc tả Kỹ thuật:** Đồng bộ toàn bộ các quy chuẩn này vào [`docs/specs/03-sessions-and-deep-reading-spec.md`](../../specs/03-sessions-and-deep-reading-spec.md).
