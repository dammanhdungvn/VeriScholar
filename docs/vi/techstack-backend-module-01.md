# Lựa Chọn Công Nghệ Backend & Đánh Đổi Kỹ Thuật (Module 1 - Deep Read)

Tài liệu này tổng hợp các quyết định lựa chọn công nghệ cốt lõi và đánh đổi kỹ thuật (Engineering Trade-offs) cho **Module 1: Đọc Sâu & Đối Thoại Kép Bài Báo Học Thuật** của nền tảng **VeriScholar** dựa trên [PRD.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md), [design-architecture.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md) và [design-database.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md).

---

## 0. BẢNG THUẬT NGỮ CÔNG NGHỆ DÀNH CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

| Thuật ngữ | Khái niệm tiếng Anh | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Advanced RAG** | Advanced Retrieval-Augmented Generation | Kỹ thuật tìm kiếm tăng cường nâng cao: Kết hợp tìm kiếm vector đa chiều, tìm kiếm từ khóa và chấm điểm chéo (Reranking) để AI trả lời chính xác, dẫn nguồn đúng trang tài liệu. |
| **Bounding Box** | Bounding Box Coordinate `[x0, y0, x1, y1, page]` | Khung chữ nhật bao quanh đoạn văn bản hoặc hình ảnh trên trang PDF; frontend dùng tọa độ này để vẽ khung viền vàng highlight nổi bật cho người dùng xem. |
| **Dense Vector** | Dense Vector Embedding | Mảng gồm 1024 con số thực biểu diễn ý nghĩa ngữ cảnh sâu sắc của một đoạn văn bản (ví dụ: mô hình BGE-M3 biến từ ngữ thành các con số trong không gian đa chiều). |
| **Sparse / Lexical Search** | Full-Text Search (`tsvector`) | Tìm kiếm từ khóa chính xác: So khớp từng chữ cái, số hiệu, mã công thức toán học hoặc tên riêng mà không làm thay đổi từ. |
| **HNSW** | Hierarchical Navigable Small World | Chỉ mục đồ thị đa tầng thông minh trên PostgreSQL; cho phép tìm kiếm các vector có ý nghĩa gần nhau nhất chỉ trong vài phần nghìn giây thay vì phải so sánh toàn bộ cơ sở dữ liệu. |
| **Cosine Distance (`<=>`)** | Cosine Distance Metric | Phép đo góc hình học giữa 2 vector: Góc càng nhỏ (khoảng cách càng gần 0) thì nghĩa của 2 câu văn càng tương đồng. |
| **RRF** | Reciprocal Rank Fusion | Công thức toán học kết hợp điểm số của tìm kiếm ngữ nghĩa và tìm kiếm từ khóa để tạo ra danh sách tài liệu gợi ý công bằng và chuẩn xác nhất. |
| **Cross-Encoder Reranker** | Cross-Encoder Reranker Model | Mô hình AI chuyên dụng (như `bge-reranker-v2-m3`) nhận vào cả câu hỏi và đoạn văn bản cùng lúc để chấm điểm xác suất tương quan thực tế (từ 0.0 đến 1.0), giúp lọc bỏ các đoạn gây nhiễu. |
| **ONNX Runtime INT8** | Open Neural Network Exchange Quantization | Định dạng mô hình nén và tối ưu hóa suy luận toán học 8-bit trên CPU máy chủ, giúp mô hình AI chạy nhanh gấp 3 đến 5 lần mà không cần card đồ họa GPU rời. |
| **Table Stitching** | Cross-Page Table Stitching | Kỹ thuật ghép nối bảng biểu vắt ngang nhiều trang PDF bằng thuật toán nhận diện tiêu đề cột (header) ở trang trước để nối liền các dòng dữ liệu ở trang tiếp theo. |
| **OpenAI Frontier Models** | OpenAI Frontier LLMs (`gpt-4o`, `gpt-4o-mini`, `o3-mini`) | Dòng mô hình trí tuệ nhân tạo đám mây hàng đầu của OpenAI có khả năng suy luận logic học thuật vượt trội, đọc hiểu ngữ cảnh phức tạp và tuân thủ định dạng JSON nghiêm ngặt. |
| **DMR** | Docker Model Runner | Tiện ích tích hợp sẵn của Docker giúp chạy các mô hình AI mã nguồn mở ngay trên máy tính cục bộ qua cổng 12434 với chi phí 0 USD bản quyền API và không phụ thuộc kết nối Internet bên ngoài. |
| **Grounded Generation** | Hallucination-Free Generation | Sinh văn bản có căn cứ: Mọi câu trả lời của AI bắt buộc phải dựa trên bằng chứng có trong bài báo; nếu không có bằng chứng, AI phải từ chối trả lời (Abstention) thay vì tự bịa ra thông tin. |

---

## 1. BẢNG MA TRẬN LỰA CHỌN CÔNG NGHỆ & ĐÁNH ĐỔI KỸ THUẬT (PRODUCTION-READY)

| Tầng chức năng | Công nghệ lựa chọn | Vai trò trong hệ thống Advanced RAG | Đánh đổi & Quyết định kỹ thuật |
| --- | --- | --- | --- |
| **Document Ingestion** *(Bóc tách tài liệu)* | **PyMuPDF (`fitz`)** + **Table Stitching Heuristics** | Bóc tách khối văn bản (text blocks), cấu trúc 2 cột, bảng biểu vắt trang và trích xuất tọa độ hình học chuẩn hóa `[x0, y0, x1, y1, page]`. | Tốc độ trích xuất cực nhanh (dưới 1 giây cho tài liệu 20 trang). Bổ sung thuật toán Rule-based khâu nối bảng (Table Stitching) và nhận diện font biểu thức toán học để bảo toàn dữ liệu cho RAG mà không cần kéo thêm pipeline OCR nặng nề. |
| **Relational & Vector DB** *(CSDL quan hệ & vector)* | **PostgreSQL 18** + **`pgvector 0.8.6`** | Lưu siêu dữ liệu bài báo (Metadata), các đoạn văn bản (Chunks) và vector nhúng 1024 chiều (`HNSW vector_cosine_ops`). | Hợp nhất dữ liệu quan hệ, dữ liệu JSONB và vector trong 1 CSDL duy nhất hỗ trợ giao dịch ACID; loại bỏ hoàn toàn rủi ro lệch dữ liệu phân tán. Cấu hình `ef_search = 100` và `iterative_scan = 'relaxed'`. Đã chuẩn hóa trên toàn bộ hệ thống (`docker-compose.yml`, tài liệu DDL). |
| **Lexical Search** *(Tìm kiếm từ khóa)* | **PostgreSQL Full-Text Search (`tsvector 'simple'`)** | Tìm kiếm từ khóa chính xác nguyên bản (ký hiệu toán học, thuật ngữ khoa học, mã hóa chất, tên riêng). | Sử dụng từ điển `'simple'` để hỗ trợ tìm kiếm đa ngữ Anh - Việt, thực thi Hybrid Search kết hợp RRF ngay trong một câu lệnh SQL nội bộ mà không cần vận hành thêm cụm Elasticsearch / OpenSearch cồng kềnh. |
| **Embedding Model** *(Mô hình tạo vector)* | **BGE-M3** (1024 chiều) | Nhúng đoạn văn bản (Chunks) và câu hỏi (Query) thành dense vector trong không gian ngữ nghĩa 1024 chiều. | Hỗ trợ đa ngữ Anh - Việt xuất sắc, cửa sổ ngữ cảnh rộng (8.192 tokens), độ tương thích và hiệu năng tối ưu trên bộ chỉ mục HNSW của `pgvector`. |
| **Reranking Engine** *(Chấm điểm tương quan chéo)* *(Mắt xích trọng yếu)* | **`bge-reranker-v2-m3-onnx-int8`** (Local ONNX Runtime) | Chấm điểm tương đồng chéo (Cross-Encoder) giữa Query và Top 20 - 25 chunks ứng viên từ Hybrid RRF. | **Mắt xích sống còn:** Cung cấp điểm số xác suất tương quan thực tế (Relevance Score) để áp dụng **Ngưỡng cắt >= 0.35**, loại trừ triệt để hiện tượng phân tâm (*The Distracting Effect*) và kích hoạt cơ chế từ chối trả lời (*Abstention Prompting*) khi không tìm thấy bằng chứng. Tối ưu hóa INT8 trên CPU giữ độ trễ từ 150 đến 250ms, bảo đảm SLA TTFT dưới 1 giây. |
| **LLM Gateway** *(Cổng mô hình AI)* | **OpenAI Cloud Models (`gpt-4o`, `gpt-4o-mini`)** + **Local DMR (`Qwen2.5-7B-Instruct`)** | Sinh câu trả lời có căn cứ xác thực (Grounded Generation) kèm mã trích dẫn tọa độ trực quan và phân tích tài liệu chuyên sâu. | Sử dụng **OpenAI `gpt-4o`** cho các câu hỏi suy luận đa tài liệu phức tạp; dùng **`gpt-4o-mini`** cho các câu hỏi tra cứu nhanh; dự phòng cục bộ bằng **Docker Model Runner (`Qwen2.5-7B-Instruct`)** khi cần chạy offline hoặc tiết kiệm chi phí; giữ **`ai/smollm2`** (1.7B) cho tác vụ phân tích siêu dữ liệu nhẹ. |
| **Task Queue & Workers** *(Hàng đợi tác vụ ngầm)* | **Redis Streams / ARQ Worker** | Hàng đợi tác vụ xử lý tài liệu bất đồng bộ bền vững (Durable Task Queue). | Chống trôi dạt hoặc mất tác vụ (Task Evaporation) khi bóc tách các tệp PDF lớn (lên tới 50MB); hỗ trợ xác nhận hoàn thành tường minh (Explicit ACK), Consumer Groups và hàng đợi thư chết (DLQ). |
| **Backend Framework** *(Nền tảng máy chủ)* | **FastAPI** + **Python 3.12** + **`uv`** | Cung cấp REST API chuẩn Google AIP-136 và dòng dữ liệu Server-Sent Events (SSE) để truyền chữ thời gian thực. | Hỗ trợ xử lý bất đồng bộ (asyncio) hiệu năng cao; áp dụng cơ chế *Early Connection Release* (giải phóng kết nối DB trước khi mở luồng stream SSE) nhằm không làm cạn kiệt connection pool. |
| **Frontend & UI** *(Giao diện người dùng)* | **React 19 (TSX)** + **Vite** + **PDF.js** | Hiển thị tài liệu PDF gốc đa tab và vẽ khung chữ nhật highlight trực quan lên Canvas. | Cơ chế *Dynamic Viewport Matrix Scaling* kết hợp `page_dimensions` và `rotation_deg`, đảm bảo khung highlight viền vàng không bị lệch trên mọi kích thước màn hình và góc xoay trang. |
| **Local Infrastructure** *(Hạ tầng cục bộ)* | **Docker Compose** | Đóng gói PostgreSQL 18 (`pgvector`), Redis 7 và kết nối thông suốt với Docker Model Runner. | Tối ưu trải nghiệm cài đặt cho các kỹ sư mới tham gia dự án: chỉ cần một câu lệnh duy nhất (`docker compose up -d`) là sẵn sàng toàn bộ môi trường. |

---

## 2. PHÂN TÍCH CHUYÊN SÂU CÁC QUYẾT ĐỊNH ĐÁNH ĐỔI KỸ THUẬT

### 2.1. Bổ sung Mô hình Reranker (`bge-reranker-v2-m3`): Giải quyết bài toán Distractor Mitigation
- **Nút thắt:** Phương pháp tìm kiếm lai (Hybrid Search) qua RRF kết hợp Dense Vector (BGE-M3) và Sparse Lexical (`tsvector`) chỉ thực hiện nhiệm vụ *thu thập ứng viên* (Candidate Retrieval, lấy Top 30 đến 40 chunks). RRF chỉ là phép cộng thứ hạng thô dựa trên vị trí danh sách chứ không đưa ra điểm số xác suất tương quan ngữ nghĩa thực tế.
- **Giải pháp kỹ thuật:** Đưa mô hình Cross-Encoder **`bge-reranker-v2-m3`** vào vị trí trung gian giữa Retrieval và LLM Gateway:
  1. Nhận vào cặp `(Query, Chunk)` và tính toán trực tiếp ma trận chú ý chéo (Cross-Attention).
  2. Xuất ra điểm số tương quan chuẩn hóa trong thang điểm từ 0.0 đến 1.0.
  3. Áp dụng **Ngưỡng cắt >= 0.35** (Relevance Threshold): Nếu tất cả các chunks đều có điểm dưới 0.35, hệ thống lập tức kích hoạt chỉ dẫn *Abstention Prompting* để LLM từ chối trả lời ("Tài liệu không cung cấp đủ bằng chứng để trả lời câu hỏi này"), triệt tiêu 100% hiện tượng ảo giác (Hallucination).

### 2.2. Tối ưu hóa Nút thắt Độ trễ Reranker trên CPU (SLA TTFT dưới 1 giây)
- **Nút thắt tiềm ẩn:** Mô hình Cross-Encoder thực hiện self-attention trên cặp `(Query + Chunk)`. Khi chạy PyTorch tiêu chuẩn trên CPU không có card đồ họa GPU, việc chấm điểm đồng thời 40 chunks có thể mất từ 1.2 đến 2.5 giây, vi phạm cam kết thời gian phản hồi token đầu tiên (Time-to-First-Token - TTFT dưới 1 giây) qua luồng SSE.
- **Giải pháp kỹ thuật:**
  1. **Cắt giảm phễu ứng viên thích ứng (Adaptive Candidate Pool):** Thay vì nạp toàn bộ 40 chunks, chỉ trích xuất **Top 20 đến 25 chunks** có điểm RRF cao nhất từ PostgreSQL đưa vào Reranker.
  2. **Tăng tốc suy luận CPU bằng ONNX Runtime / Optimum INT8:** Sử dụng bản phân phối lượng tử hóa INT8 (`bge-reranker-v2-m3-onnx-int8`). Cơ chế này giảm thời gian chấm điểm xuống còn **150 đến 250ms** trên CPU 4 lõi mà không làm suy giảm độ chính xác xếp hạng, bảo đảm duy trì trọn vẹn SLA TTFT dưới 1 giây.

### 2.3. Định vị Mô hình LLM: Chuẩn hóa OpenAI Frontier Models kết hợp Phân tầng Cục bộ
- **Định vị OpenAI Models làm Cloud Gateway:**
  - **`gpt-4o`:** Đóng vai trò mô hình suy luận đỉnh cao (Frontier Reasoning Model), chịu trách nhiệm sinh câu trả lời đối thoại kép, phân tích tổng hợp chéo nhiều bài báo học thuật và bảo đảm định dạng JSON chứa mảng Bounding Box `[x0, y0, x1, y1, page]` với độ chính xác tuyệt đối.
  - **`gpt-4o-mini`:** Đóng vai trò mô hình tra cứu tối ưu chi phí (Cost-Optimized Model) cho các câu hỏi đơn giản, truy vấn định nghĩa hoặc tóm tắt nhanh từng đoạn văn.
- **Định vị lại năng lực Docker Model Runner (DMR):**
  - Các mô hình siêu nhỏ dưới 3B tham số (như `ai/smollm2`) không đủ năng lực suy luận ngữ cảnh học thuật phức tạp và dễ bị lỗi cấu trúc khi xuất tọa độ hình học. Do đó, `smollm2` (1.7B) chỉ được dùng cho các tác vụ phân tích nhẹ: Chuẩn hóa tiêu đề (`title cleaning`), bóc tách danh sách tác giả, hoặc gán nhãn tags.
  - Khi người dùng cần chạy suy luận trả lời câu hỏi hoàn toàn cục bộ (Offline Grounded Q&A), hệ thống kích hoạt **`Qwen2.5-7B-Instruct`** hoặc **`Llama-3.1-8B-Instruct`** (lượng tử hóa 4-bit Q4_K_M) thông qua Docker Model Runner trên cổng 12434.

### 2.4. Giải pháp Bóc tách Tài liệu: PyMuPDF kết hợp Heuristics Khâu nối Bảng biểu (Table Stitching)
- **Nút thắt:** PyMuPDF (`fitz`) có ưu thế vượt trội về tốc độ (dưới 1 giây cho 20 trang tài liệu) và trích xuất tọa độ Bounding Box chính xác, nhưng mặc định không tự động ghép các bảng biểu vắt ngang 2 trang giấy và không tự chuyển công thức toán học thành mã ký hiệu chuẩn.
- **Giải pháp kỹ thuật:**
  - Áp dụng module **Table Stitching Rule-based**: Nhận diện cấu trúc header của bảng ở cuối trang trước và khâu nối các hàng dữ liệu tiếp theo ở đầu trang sau, giữ nguyên tính toàn vẹn ngữ nghĩa của bảng số liệu khoa học.
  - Áp dụng Heuristic font toán học (symbol / italic fonts) và tọa độ dòng chữ (baseline) để nhận diện biểu thức toán học và bao bọc bằng ký hiệu phân cách chuẩn, tránh hiện tượng công thức bị vỡ mảnh khi chia chunk.

### 2.5. Đồng bộ Phiên bản Cơ sở Dữ liệu: PostgreSQL 18 + `pgvector 0.8.6`
- **Thực tế hệ thống:** Toàn bộ hệ thống VeriScholar đã được nâng cấp đồng bộ lên **PostgreSQL 18** và `pgvector/pgvector:0.8.6-pg18` trên tất cả các tài liệu kỹ thuật ([`design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md), [`design-architecture.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md), [`guide-docker.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/guide-docker.md)) và cấu hình hạ tầng thực tế ([`docker-compose.yml`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docker-compose.yml)).
- **Lợi thế kỹ thuật:** PostgreSQL 18 kết hợp `pgvector 0.8.6` mang lại hiệu năng tối ưu với chỉ mục HNSW cải tiến, hỗ trợ `vector_cosine_ops`, cấu hình `iterative_scan = 'relaxed'` và truy vấn song song (Parallel Query Execution) vượt trội, đáp ứng tải tìm kiếm vector đa người dùng trong môi trường sản xuất.

---

## 3. ĐỊNH NGẠCH TÀI NGUYÊN & YÊU CẦU PHẦN CỨNG CỤC BỘ (LOCAL HARDWARE FOOTPRINT INVARIANT)

Để bảo đảm hệ thống chạy mượt mà trên máy tính cục bộ của các kỹ sư phát triển mà không gặp hiện tượng tràn bộ nhớ (Out-Of-Memory / OOM-Killed) khi kích hoạt đồng thời toàn bộ cụm dịch vụ, tài nguyên RAM được định ngạch như sau:

| Dịch vụ thành phần | Công nghệ / Mô hình | Mức chiếm dụng RAM ước tính |
| :--- | :--- | :---: |
| **Cơ sở dữ liệu & Cụm hàng đợi** | PostgreSQL 18 (`pgvector`) + Redis 7 | ~ 1.5 GB |
| **Mô hình Vector Embedding** | `BGE-M3` (FP16 / INT8) | ~ 1.2 GB |
| **Mô hình Chấm điểm chéo** | `bge-reranker-v2-m3` (ONNX INT8) | ~ 1.0 GB |
| **Mô hình AI Suy luận Cục bộ** | Docker Model Runner (`Qwen2.5-7B-Instruct` Q4_K_M) | ~ 4.8 GB |
| **Máy chủ Web Backend & Frontend** | FastAPI Worker + Vite/React Development Server | ~ 1.5 GB |
| **TỔNG DUNG LƯỢNG RAM CHIẾM DỤNG** | **Toàn bộ stack AI & Dịch vụ cục bộ** | **~ 10.0 GB** |

> [!IMPORTANT]
> **Yêu cầu phần cứng bắt buộc:**
> Máy trạm hoặc máy tính xách tay của kỹ sư phát triển bắt buộc phải có tối thiểu **16 GB RAM** (khuyến nghị **32 GB RAM**) để đảm bảo hệ điều hành và IDE (VS Code / JetBrains) hoạt động ổn định khi Docker chạy đầy đủ cụm dịch vụ AI cục bộ.

---

## 4. TRẠNG THÁI NGHIỆM THU & ĐÓNG BĂNG THIẾT KẾ (DESIGN FREEZE STATUS)

Tài liệu Lựa chọn Công nghệ Backend & Đánh đổi Kỹ thuật cho Module 1 đã đạt sự khớp nối hoàn chỉnh 100% với 5 trụ cột đặc tả của hệ thống:
1. Bản yêu cầu nghiệp vụ học thuật: [`PRD.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md).
2. Bản đặc tả 59 REST API Endpoints chuẩn Google AIP-136: [`design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md).
3. Bản lược đồ cơ sở dữ liệu quan hệ & vector: [`design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md).
4. Bản thiết kế kiến trúc phân tán Monorepo lục giác: [`design-architecture.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md).
5. Đường ống Tích hợp Liên tục 7 Chốt chặn: [`guide-ci.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/guide-ci.md).

**CHÍNH THỨC XÁC NHẬN: BẢN THIẾT KẾ ĐÃ ĐƯỢC ĐÓNG BĂNG (PRODUCTION-READY & FREEZE). DỰ ÁN ĐÃ SẴN SÀNG ĐỂ TIẾN HÀNH KHỞI TẠO VÀ TRIỂN KHAI MÃ NGUỒN CHO MODULE 1.**
