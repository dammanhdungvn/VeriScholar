# Lựa Chọn Công Nghệ Backend & Đánh Đổi Kỹ Thuật (Module 1 - Deep Read)

Tài liệu này tổng hợp các quyết định lựa chọn công nghệ cốt lõi và đánh đổi kỹ thuật (Engineering Trade-offs) cho **Module 1: Đọc Sâu & Đối Thoại Kép Bài Báo Học Thuật** của nền tảng **VeriScholar** dựa trên [PRD.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md) và [design-architecture.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md).

---

## 1. BẢNG MA TRẬN LỰA CHỌN CÔNG NGHỆ & ĐÁNH ĐỔI

| Tầng chức năng | Công nghệ lựa chọn | Vai trò trong hệ thống Advanced RAG | Đánh đổi & Quyết định kỹ thuật |
| --- | --- | --- | --- |
| **Document Ingestion** | **PyMuPDF** *(Adapter chính)* | Bóc tách text, bảng biểu và trích xuất tọa độ chuẩn hóa (`BoundingBox`). | PyMuPDF cho tốc độ bóc tách cực nhanh (< 1s cho tài liệu 20 trang); trích xuất hình học và phông chữ chuẩn xác. Chuẩn hóa qua giao diện `IPDFParser` cổng ra. |
| **Relational & Vector DB** | **PostgreSQL 16** + **`pgvector`** | Lưu Document Metadata, Text Chunks và Vector Embeddings (HNSW Index `vector_cosine_ops`). | Hợp nhất dữ liệu quan hệ và vector trong 1 cơ sở dữ liệu duy nhất hỗ trợ ACID, loại bỏ rủi ro lệch đồng bộ dữ liệu so với việc dùng Vector DB chuyên biệt. |
| **Lexical Search (Sparse)** | **PostgreSQL Full-Text Search (`tsvector 'simple'`)** | Tìm kiếm từ khóa chính xác (mã công thức, thuật ngữ học thuật, từ viết tắt). | Thực thi Hybrid Search cùng `pgvector` ngay trong SQL qua thuật toán RRF, tránh phải vận hành thêm cụm Elasticsearch/OpenSearch cồng kềnh. |
| **Embedding Model** | **BGE-M3** (1024 chiều) | Chuyển đổi Chunk và Query thành Dense Vector chuẩn hóa. | Hỗ trợ đa ngữ vượt trội (Anh - Việt), xử lý hiệu quả ngữ cảnh học thuật và tương thích với không gian vector 1024-dim của `pgvector`. |
| **LLM Gateway** | **Docker Model Runner (DMR)** + **Cloud Reasoning LLMs** | Sinh câu trả lời có căn cứ (Grounded Generation) kèm mã trích dẫn tọa độ. | Sử dụng **Docker Model Runner** (`ai/smollm2`) tại tầng cục bộ (0 USD) và Cloud LLMs cho suy luận sâu, định tuyến thông minh qua `CostAwareLLMGatewayAdapter`. |
| **Task Queue & Workers** | **Redis Streams / ARQ Worker** | Hàng đợi tác vụ bất đồng bộ bền vững (Durable Task Queue). | Chống trôi dạt tác vụ (Task Evaporation) khi xử lý các tài liệu PDF lớn; hỗ trợ Explicit ACK và Dead-Letter Queue (DLQ). |
| **Backend Framework** | **FastAPI** + **Python 3.12** + **`uv`** | Cung cấp REST API (AIP-136) và Server-Sent Events (SSE) để stream phản hồi. | Xử lý bất đồng bộ (asyncio), quản lý phụ thuộc monorepo xác định thông qua `uv workspace`. |
| **Frontend & UI** | **React 19 (TSX)** + **Vite** + **PDF.js** | Hiển thị tài liệu PDF và vẽ bounding box highlight trực quan lên trang. | Đồng bộ vị trí trích dẫn giữa câu trả lời AI và đoạn văn bản gốc trên giao diện chia đôi, bất biến với zoom/pan/rotation. |
| **Local Infrastructure** | **Docker Compose** | Đóng gói dịch vụ PostgreSQL (`pgvector`), Redis 7 và kết nối với Docker Model Runner. | Tối ưu trải nghiệm cài đặt ban đầu cho dự án mã nguồn mở chỉ bằng một câu lệnh khởi chạy. |
