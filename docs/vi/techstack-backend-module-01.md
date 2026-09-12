# Lựa Chọn Công Nghệ Backend & Đánh Đổi Kỹ Thuật (Module 1 - Deep Read)

Tài liệu này tổng hợp các quyết định lựa chọn công nghệ cốt lõi và đánh đổi kỹ thuật (Engineering Trade-offs) cho **Module 1: Đọc Sâu & Đối Thoại Kép Bài Báo Học Thuật** của nền tảng **VeriScholar** dựa trên [PRD.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md) và [design-architecture.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md).

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
| **DMR** | Docker Model Runner | Tiện ích tích hợp sẵn của Docker giúp chạy các mô hình AI mã nguồn mở ngay trên máy tính của bạn mà không tốn phí bản quyền API và không cần kết nối Internet. |
| **Grounded Generation** | Hallucination-Free Generation | Sinh văn bản có căn cứ: Mọi câu trả lời của AI bắt buộc phải dựa trên bằng chứng có trong bài báo; nếu không có bằng chứng, AI phải từ chối trả lời thay vì tự bịa ra thông tin. |

---

## 1. BẢNG MA TRẬN LỰA CHỌN CÔNG NGHỆ & ĐÁNH ĐỔI KỸ THUẬT

| Tầng chức năng | Công nghệ lựa chọn | Vai trò trong hệ thống Advanced RAG | Đánh đổi & Quyết định kỹ thuật |
| --- | --- | --- | --- |
| **Document Ingestion** *(Bóc tách tài liệu)* | **PyMuPDF** *(Adapter chính)* | Bóc tách văn bản, bảng biểu và trích xuất tọa độ chuẩn hóa (`BoundingBox`). | PyMuPDF cho tốc độ bóc tách cực nhanh (< 1 giây cho tài liệu 20 trang); trích xuất hình học và phông chữ chuẩn xác. Chuẩn hóa qua giao diện `IPDFParser` (Cổng trừu tượng). |
| **Relational & Vector DB** *(CSDL quan hệ & vector)* | **PostgreSQL 18** + **`pgvector`** | Lưu siêu dữ liệu bài báo (Metadata), các đoạn văn bản (Chunks) và vector nhúng (HNSW Index `vector_cosine_ops`). | Hợp nhất dữ liệu quan hệ và dữ liệu vector trong 1 cơ sở dữ liệu duy nhất hỗ trợ giao dịch ACID, loại bỏ hoàn toàn rủi ro lệch dữ liệu so với việc dùng Vector DB chuyên biệt ngoài. |
| **Lexical Search** *(Tìm kiếm từ khóa)* | **PostgreSQL Full-Text Search (`tsvector 'simple'`)** | Tìm kiếm từ khóa chính xác nguyên bản (mã công thức hóa học, thuật ngữ học thuật, từ viết tắt). | Thực thi tìm kiếm lai (Hybrid Search) cùng `pgvector` ngay trong một câu lệnh SQL qua thuật toán RRF, tránh phải vận hành thêm cụm Elasticsearch/OpenSearch cồng kềnh. |
| **Embedding Model** *(Mô hình tạo vector)* | **BGE-M3** (1024 chiều) | Chuyển đổi đoạn văn bản (Chunk) và câu hỏi (Query) thành vector ngữ nghĩa 1024 chiều. | Hỗ trợ đa ngôn ngữ xuất sắc (tiếng Anh và tiếng Việt), hiểu sâu văn phong nghiên cứu khoa học và tương thích tối đa với bộ chỉ mục `pgvector`. |
| **LLM Gateway** *(Cổng giao tiếp mô hình AI)* | **Docker Model Runner (DMR)** + **Cloud Reasoning LLMs** | Sinh câu trả lời có căn cứ xác thực (Grounded Generation) kèm mã trích dẫn tọa độ trực quan. | Sử dụng **Docker Model Runner** (`ai/smollm2`) tại máy cục bộ (chi phí 0 USD) và Cloud LLMs cho các câu hỏi suy luận phức tạp, điều phối linh hoạt qua bộ định tuyến `CostAwareLLMGatewayAdapter`. |
| **Task Queue & Workers** *(Hàng đợi tác vụ ngầm)* | **Redis Streams / ARQ Worker** | Hàng đợi tác vụ bất đồng bộ bền vững (Durable Task Queue). | Chống trôi dạt hoặc mất tác vụ (Task Evaporation) khi xử lý các tài liệu PDF lớn (lên tới 50MB); hỗ trợ xác nhận hoàn thành tường minh (Explicit ACK) và hàng đợi thư chết (DLQ). |
| **Backend Framework** *(Nền tảng máy chủ)* | **FastAPI** + **Python 3.12** + **`uv`** | Cung cấp chuẩn REST API (AIP-136) và dòng dữ liệu Server-Sent Events (SSE) để truyền chữ thời gian thực. | Hỗ trợ xử lý bất đồng bộ (asyncio) với hiệu năng cao, quản lý các gói phần mềm trong monorepo chặt chẽ thông qua `uv workspace`. |
| **Frontend & UI** *(Giao diện người dùng)* | **React 19 (TSX)** + **Vite** + **PDF.js** | Hiển thị tài liệu PDF gốc và vẽ khung chữ nhật highlight trực quan lên trang. | Đồng bộ vị trí trích dẫn giữa câu trả lời của AI và đoạn văn bản gốc trên giao diện chia đôi màn hình, bất biến khi phóng to, thu nhỏ hay xoay trang. |
| **Local Infrastructure** *(Hạ tầng máy phát triển)* | **Docker Compose** | Đóng gói dịch vụ PostgreSQL (`pgvector`), Redis 7 và kết nối thông suốt với Docker Model Runner. | Tối ưu trải nghiệm cài đặt cho các kỹ sư mới tham gia dự án: chỉ cần một câu lệnh duy nhất (`docker compose up -d`) là sẵn sàng toàn bộ môi trường. |
