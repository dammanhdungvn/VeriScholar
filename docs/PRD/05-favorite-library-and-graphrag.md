# MODULE 05: KHO PAPER YÊU THÍCH (FOLDERS & STAR CRUD) & HỆ THỐNG GRAPHRAG 4 THỰC THỂ
# (FILE 05: FAVORITE PAPERS LIBRARY CRUD & POSTGRESQL GRAPHRAG)

---

## 1. Mục Tiêu Module
Giúp người dùng lưu trữ các bài báo tâm đắc vào **Kho Paper Yêu Thích** được phân loại theo cây thư mục đề tài cá nhân, đồng thời tự động bóc tách mỗi bài báo được đánh dấu yêu thích (`Star`) thành **Đồ thị Tri thức 4 Thực thể cố định trên PostgreSQL + `pgvector`**. Nhờ đó, khi kho tài liệu lên tới hàng chục, hàng trăm bài, người dùng (hoặc Agent viết bài ở Module 06) có thể tìm lại chính xác bài báo nào dùng phương pháp gì, chạy trên tập dữ liệu nào và đạt kết quả bao nhiêu chỉ trong tích tắc.

---

## 2. Quản Lý Kho Yêu Thích & Thư Mục Đề Tài — Đầy Đủ Thao Tác CRUD (`folders` & `star`)

### A. Đánh dấu Yêu thích Bài báo (`Star / Unstar CRUD`)
1. **Bấm Star lưu bài báo vào Kho (`POST /api/v1/documents/{document_id}:star`, `:toggle-star`):**
   * Trên thanh công cụ đọc PDF hoặc trong danh sách tài liệu đều có nút ngôi sao **`[⭐ Lưu vào Kho Yêu thích]`**.
   * Khi bấm vào, người dùng có thể chọn lưu vào một Thư mục đề tài cụ thể (`folder_id`) hoặc lưu chung vào mục Yêu thích.
   * **Kích hoạt ngầm GraphRAG:** Ngay khi bài báo được gắn Star, hệ thống tự động kích hoạt tác vụ chạy ngầm bóc tách thực thể GraphRAG cho bài báo đó (nếu chưa bóc tách).
2. **Bỏ đánh dấu Star (`Unstar`):**
   * Bấm lại vào ngôi sao để gỡ bài báo khỏi danh sách Yêu thích.
   * **Đồng bộ GraphRAG khi Bỏ Star:** Khi một bài báo bị gỡ khỏi Kho Yêu thích (`is_starred = False` và `folder_id = NULL`), hệ thống tự động loại bài báo đó (hoặc xóa các `graph_nodes`/`graph_edges` của bài đó) ra khỏi phạm vi truy vấn của GraphRAG để đảm bảo người dùng và Agent viết bài không bao giờ trích dẫn nhầm bài báo đã bị loại bỏ khỏi kho.

### B. Quản lý Cây Thư mục Đề tài (`Folders CRUD`)
1. **Tạo thư mục mới (`POST /api/v1/folders`):**
   * Nhập tên thư mục (`name`, ví dụ: *"Đồ án tốt nghiệp - GNN"*, *"Các bài về Transformer"*), màu sắc nhận diện (`color`), mô tả (`description`) và thư mục cha (`parent_id` nếu muốn tạo thư mục con).
2. **Xem danh sách & Cây thư mục (`GET /api/v1/folders`, `GET /api/v1/folders/tree`, `GET /api/v1/folders/{id}`):**
   * Hiển thị cây thư mục kèm số lượng bài báo bên trong mỗi thư mục trên giao diện `LibraryWorkspaceView.tsx`.
3. **Sửa thông tin thư mục (`PATCH /api/v1/folders/{id}`):**
   * Đổi tên thư mục, đổi màu nhãn hoặc cập nhật mô tả.
4. **Thêm / Gỡ bài báo khỏi thư mục (`POST /api/v1/folders/{id}/documents`, `DELETE /api/v1/folders/{id}/documents`):**
   * Cho phép gán một hoặc nhiều bài báo vào thư mục hoặc chuyển sang thư mục khác.
5. **Xóa thư mục (`DELETE /api/v1/folders/{id}`):**
   * Xóa thư mục khỏi cây phân loại (các bài báo bên trong không bị mất file PDF mà chỉ được gỡ `folder_id = NULL`).

---

## 3. Kiến Trúc GraphRAG 4 Thực Thể Cố Định Trên PostgreSQL + `pgvector`

### A. Tại sao dùng 4 Thực thể cố định trên PostgreSQL?
* Không cài đặt thêm cơ sở dữ liệu đồ thị rời (như Neo4j) để tránh nặng máy và phức tạp hóa việc triển khai.
* Không cho AI tự sinh nhãn thực thể tự do (tránh việc cùng một khái niệm lúc thì AI đặt là `Model`, lúc lại đặt là `Algorithm` gây lệch truy vấn).
* Sử dụng bảng quan hệ chuẩn trên **PostgreSQL + `pgvector`** (`graph_nodes` và `graph_edges` với chỉ mục `HNSW` và `GIN`), đảm bảo tốc độ truy vấn cao và không sử dụng SQLite fallback.

### B. Cấu trúc 4 Loại Đỉnh (`graph_nodes`) và 4 Loại Cạnh (`graph_edges`)

| Loại Đỉnh (`node_type`) | Ý nghĩa học thuật | Ví dụ cụ thể được trích xuất từ bài báo |
| :--- | :--- | :--- |
| **1. `Paper`** | Bài báo khoa học gốc | *Attention Is All You Need (Vaswani et al., 2017)* |
| **2. `Method`** | Phương pháp / Mô hình / Thuật toán | *Transformer*, *Scaled Dot-Product Attention*, *ResNet-50* |
| **3. `Dataset`** | Tập dữ liệu thực nghiệm / Benchmark | *WMT 2014 English-to-German*, *ImageNet-1K*, *COCO* |
| **4. `MetricResult`** | Chỉ số đánh giá & Con số đạt được | *BLEU: 28.4*, *Top-1 Accuracy: 89.2%*, *F1-Score: 94.1%* |

**4 Loại Cạnh Quan Hệ (`edge_type`):**
1. `PROPOSES`: `Paper` $\rightarrow$ `Method` (Bài báo đề xuất hoặc sử dụng phương pháp nào).
2. `EVALUATED_ON`: `Paper` / `Method` $\rightarrow$ `Dataset` (Được thử nghiệm trên bộ dữ liệu nào).
3. `ACHIEVES`: `Paper` / `Method` $\rightarrow$ `MetricResult` (Đạt được kết quả đo lường bao nhiêu, kèm `chunk_id` và `page_number` chứng minh).
4. `CITES`: `Paper` $\rightarrow$ `Paper` (Quan hệ trích dẫn giữa các bài báo trong kho).

---

## 4. Truy Vấn Tìm Lại Tri Thức Trong Kho (`POST /api/v1/folders/synthesis`)

Khi người dùng vào màn hình **Kho Tài Liệu (`LibraryWorkspaceView.tsx`)** và đặt câu hỏi tra cứu (hoặc khi LangGraph Agent ở Module 06 gọi công cụ `query_library_graph_rag`):
* Ví dụ câu hỏi: *"Trong kho yêu thích của tôi, những bài báo nào xử lý bài toán dịch máy trên tập dữ liệu WMT-14 và đạt điểm BLEU cao nhất?"*
* **Luồng truy vấn kết hợp (Hybrid Graph + Vector Search):**
  1. Tìm kiếm ngữ nghĩa trên vector (`embedding`) kết hợp khớp tên thực thể trong bảng `graph_nodes` (`Dataset = WMT-14`, `Method`, `MetricResult = BLEU`).
  2. Thực hiện phép nối (`JOIN` 1–2 bước) qua bảng `graph_edges` để gom toàn bộ các `Paper` thỏa mãn điều kiện cùng các `document_chunks` chứa bằng chứng.
  3. Tổng hợp câu trả lời rõ ràng kèm trích dẫn tên bài báo, số trang và con số thực nghiệm chính xác.
