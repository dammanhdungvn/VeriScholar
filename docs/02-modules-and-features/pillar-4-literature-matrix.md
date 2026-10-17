# Trụ Cột 4: Tổng Hợp Tài Liệu Quy Mô Lớn & Ma Trận So Sánh (Literature Matrix & Library Synthesis)

Tài liệu này đặc tả chi tiết kiến trúc, luồng xử lý và tiêu chuẩn kỹ thuật của **Trụ Cột 4 (Module 4: Scalable 100+ Paper Comparison Matrix, Hierarchical RAG, Folders & Redis Caching)** của nền tảng **VeriScholar**.

---

## 1. TỔNG QUAN & NGUYÊN LÝ THIẾT KẾ (PILLAR OVERVIEW)

Trụ cột 4 giải quyết bài toán so sánh, đối chiếu và tổng hợp tài liệu trên quy mô thư viện lớn (từ 10 đến 100+ bài báo):
- **Ma Trận So Sánh Khoa Học 100+ Bài Báo (Scalable Comparison Matrix):** Phân tích và trích xuất đồng loạt các chiều kích so sánh: Phương pháp luận, Bộ dữ liệu thử nghiệm, Chỉ số đo lường và Hạn chế nghiên cứu.
- **Phân Trang Phía Máy Chủ (Server-Side Pagination):** Đảm bảo tốc độ hiển thị và kết xuất DOM ổn định, không gây giật lag khi thư viện mở rộng đến hàng trăm bài báo.
- **Bộ Nhớ Đệm Hiệu Năng Cao (Redis Matrix Cache):** Lưu trữ kết quả trích xuất ma trận với cơ chế vô hiệu hóa đệm thông minh khi có bài báo mới được thêm vào.
- **Cấu Trúc Thư Mục Phân Cấp (Folder Management):** Gom nhóm và tổ chức bài báo theo từng chủ đề hoặc đề tài nghiên cứu.

```mermaid
flowchart TD
    Client["Giao Diện Client (ComparisonMatrixModal)"] --> API["Matrix API: /api/v1/matrix/compare<br/>(limit, offset, search, filters)"]
    
    API --> CacheCheck{"Kiểm Tra Redis Cache?"}
    CacheCheck -->|Cache Hit (< 15ms)| ReturnData["Trả Ngay Kết Quả Ma Trận"]
    
    CacheCheck -->|Cache Miss| HierarchicalRAG["Hierarchical RAG Pipeline"]
    
    subgraph HIERARCHICAL_RETRIEVAL ["Truy Vấn Phân Tầng"]
        HierarchicalRAG --> Tier1["Tầng 1: Curated Knowledge (Smart Notes)"]
        Tier1 --> Tier2["Tầng 2: Metadata & Abstracts"]
        Tier2 --> Sufficiency{"Sufficiency Gate >= 0.80?"}
        Sufficiency -->|Đủ thông tin| Synth["LLM Matrix Synthesizer"]
        Sufficiency -->|Thiếu dữ kiện| Tier3["Tầng 3: Deep Raw Chunks (Hybrid Search)"]
        Tier3 --> Synth
    end

    Synth --> WriteCache["Ghi Đệm vào Redis (TTL 24h)"]
    WriteCache --> ReturnData
    ReturnData --> Client
```

---

## 2. CÁC TÍNH NĂNG KỸ THUẬT CỐT LÕI (CORE CAPABILITIES)

### 2.1. Phân Trang Server-Side & Bộ Lọc Đa Chiều
- **Endpoint:** `GET /api/v1/matrix/compare`
- **Tham số hỗ trợ:**
  - `limit: int` (Số dòng mỗi trang, ví dụ: 10, 25, 50, mặc định: 10).
  - `offset: int` (Vị trí bắt đầu).
  - `search: str` (Tìm kiếm từ khóa theo tên bài báo, tác giả, phương pháp).
  - `methodology: str` (Bộ lọc theo phương pháp, ví dụ: *Transformer*, *Diffusion*, *RLHF*).
  - `dataset: str` (Bộ lọc theo bộ dữ liệu, ví dụ: *ImageNet*, *SQuAD*, *MMLU*).
- **Hiệu năng:** Đã kiểm thử tải và kết xuất thành công danh sách **120 bài báo** với thời gian phản hồi trang dưới 50ms.

### 2.2. Xuất Dữ Liệu Chuẩn Quốc Tế (CSV / Excel Export)
- Chức năng xuất ma trận ra file định dạng `.csv` hỗ trợ mở trực tiếp trên Microsoft Excel và Google Sheets:
  - Tuân thủ tuyệt đối quy chuẩn **RFC 4180** (bọc chuỗi bằng dấu ngoặc kép `""` và nhân đôi dấu nháy khi có ký tự đặc biệt).
  - Mã hóa tiền tố **UTF-8 BOM (`\uFEFF`)**: Khắc phục triệt để lỗi hiển thị tiếng Việt và các ký hiệu toán học trên Windows Excel.

### 2.3. Quản Lý Thư Mục & Phân Cấp Bài Báo (Folder Management)
- Bảng `folders` trong PostgreSQL lưu trữ cấu trúc thư mục với các thuộc tính: `name`, `color` (mã màu HEX phân loại, mặc định `#6366f1`), và `description`.
- Hỗ trợ di chuyển bài báo giữa các thư mục, đếm số lượng tài liệu trong từng thư mục và chia sẻ toàn bộ thư mục cho nhóm nghiên cứu.

---

## 3. DANH MỤC API TRỤ CỘT 4 (API ENDPOINTS)

| Phương thức | Endpoint | Chức năng |
| :--- | :--- | :--- |
| `GET` | `/api/v1/folders` | Lấy danh sách thư mục của người dùng |
| `POST` | `/api/v1/folders` | Tạo thư mục nghiên cứu mới |
| `PATCH` | `/api/v1/folders/{id}` | Cập nhật tên, màu sắc, mô tả thư mục |
| `DELETE` | `/api/v1/folders/{id}` | Xóa thư mục |
| `POST` | `/api/v1/folders/{id}/documents` | Thêm bài báo vào thư mục |
| `GET` | `/api/v1/matrix/compare` | Truy vấn ma trận so sánh (phân trang, lọc, cache) |
| `POST` | `/api/v1/matrix/export-csv` | Xuất bảng ma trận ra file CSV chuẩn UTF-8 BOM |

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar Enterprise.*
