# NGUYÊN TẮC KIẾN TRÚC BẤT BIẾN CỦA VERISCHOLAR MVP
# (THE 5 ARCHITECTURAL INVARIANTS)

Tài liệu này định nghĩa 5 bất biến kiến trúc tối thượng của VeriScholar MVP. Mọi quyết định thiết kế hoặc bổ sung tính năng vi phạm các nguyên tắc dưới đây đều bị coi là lỗi nghiêm trọng và bị chặn bởi hệ thống kiểm thử tự động.

---

## 1. Thuần PostgreSQL 16+ Với `pgvector` & Redis 7
* **Không Cơ Sở Dữ Liệu Đồ Thị Rời (No Neo4j):** Đồ thị tri thức học thuật 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) và các cạnh quan hệ được mô hình hóa và truy vấn trực tiếp trên PostgreSQL qua 2 bảng `graph_nodes` và `graph_edges`.
* **Không SQLite Fallback:** Tuyệt đối không sử dụng `aiosqlite` hay `sqlite3`. Mọi môi trường phát triển cục bộ và kiểm thử tích hợp đều chạy trên PostgreSQL 16+ thật (hỗ trợ extension `vector`).
* **Redis 7:** Chịu trách nhiệm lưu trữ mã xác thực OTP, rate-limiting, khóa hàng đợi tác vụ và trạng thái phiên tạm.

---

## 2. Kiến Trúc Lục Giác Độc Lập (Hexagonal Core Isolation)
* **Lõi miền nghiệp vụ thuần khiết:** Thư mục `packages/core/src/core/domain/` và `ports/` chỉ được phép import từ Thư viện Chuẩn Python (Standard Library) và `pydantic`.
* **Cấm phụ thuộc framework/adapter:** Tuyệt đối cấm import `fastapi`, `sqlalchemy`, `redis`, `fitz` (`pymupdf`), `httpx`, `aiofiles`, `e2b`, `langfuse`.
* **Quan hệ phụ thuộc một chiều:** `apps/api` cài đặt các cổng (ports) trừu tượng của `packages/core`. Cấm tuyệt đối chiều ngược lại (không bao giờ import `apps.api` vào `packages/core`).

---

## 3. Lưu Trữ CAS SHA-256 Với Cam Kết Tiêu Hủy Tức Thì (Zero-Retention)
* **Content-Addressable Storage (CAS):** Toàn bộ tệp PDF tài liệu và hình ảnh figure trích xuất được định danh theo chuỗi băm SHA-256 nhị phân và lưu trữ phân cấp tại `storage/blobs/{hash[:2]}/{hash[2:4]}/{hash}`.
* **Bộ đếm tham chiếu (`ref_count`):** Nhiều tài liệu trùng lặp cùng chia sẻ 1 blob vật lý.
* **Tiêu hủy vật lý tức thì:** Khi người dùng xóa tài liệu và `ref_count <= 0`, lệnh `os.unlink()` xóa vĩnh viễn file nhị phân khỏi đĩa cứng ngay trong chu kỳ request. Không lưu trữ file mồ côi.

---

## 4. Cô Lập Tuyệt Đối Qua E2B MicroVM Sandbox
* **Môi trường biên dịch LaTeX:** Mọi lệnh biên dịch tài liệu LaTeX (`pdflatex`, `xelatex`, `bibtex`) và xuất PDF chạy hoàn toàn cô lập trong E2B Firecracker MicroVM container.
* **Giới hạn an toàn:** Luôn bật cờ `--no-shell-escape` và timeout tối đa 15 giây.
* **Cấm thực thi trên máy chủ host:** Tuyệt đối cấm gọi subprocess hệ thống hoặc thực thi script shell của người dùng trực tiếp trên máy chủ backend.

---

## 5. Giám Sát 3 Tầng Nhẹ Nhàng & Đồng Nhất (3-Tier Observability)
* **Trace ID thống nhất:** Mã định danh `trace_id` khởi tạo từ client frontend (`X-Trace-ID`), truyền qua middleware backend và gắn vào mọi span giám sát.
* **Langfuse Tracing:** Ghi nhận chi phí token LLM, độ trễ RAG và đánh giá phản hồi học thuật không đồng bộ.
* **Báo lỗi Webhook bất đồng bộ:** Lỗi hệ thống cấp độ ERROR được gửi tới Telegram/Discord Webhook qua `BackgroundTasks`, không làm nghẽn luồng xử lý HTTP chính.
