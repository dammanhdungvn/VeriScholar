# QUY CHUẨN KỸ THUẬT & NGUYÊN TẮC PHÁT TRIỂN DỰ ÁN VERISCHOLAR
### (VeriScholar Project & Engineering Standards Charter)

---

## 1. TỔNG QUAN & TRIẾT LÝ PHÁT TRIỂN

Tài liệu này xác lập bộ quy chuẩn kỹ thuật toàn diện, bắt buộc tuân thủ đối với toàn bộ các thành viên kỹ thuật và AI Agents tham gia phát triển hệ thống **VeriScholar**.

Mọi dòng mã nguồn, kiến trúc và tương tác trong hệ thống phải phản ánh 3 trụ cột:
1. **Độ tin cậy học thuật tối cao (Scholarly Precision & Verifiability)**: Mọi khẳng định khoa học phải có căn cứ rõ ràng, truy vết trực tiếp tới Bounding Box trong tài liệu nguồn.
2. **Triết lý giao diện "Ngăn tủ / Chiếc túi gọn gàng" (Clean Drawers Principle)**: Tối giản thị giác, phân loại công cụ ngăn nắp, giải phóng không gian nghiên cứu cho người dùng.
3. **Kỷ luật kỹ thuật không khoan nhượng (Zero Regression & Strict Quality Gate)**: 100% tests pass, 0 lỗi kiểu, không giả lập kết quả.

---

## 2. NGUYÊN TẮC KIẾN TRÚC PHẦN MỀM (CLEAN & HEXAGONAL ARCHITECTURE)

Hệ thống được tổ chức theo mô hình **Hexagonal Architecture (Ports and Adapters)** trong cấu trúc monorepo:
- `packages/core`: Lõi nghiệp vụ (Domain Entities, Port Interfaces, Mathematical Models, NLI Verification Logic).
- `apps/api`: Tầng điều khiển máy chủ (FastAPI, Controllers, SQLModel ORM, Alembic Migrations, SSE Streaming).
- `apps/web`: Tầng giao diện người dùng (React 19, TypeScript, Tailwind CSS, State Stores, UI Components).

### Các bất biến kiến trúc (Invariants):
1. **Độc lập tầng Domain (Domain Independence):** `packages/core` là hạt nhân tinh khiết, tuyệt đối KHÔNG phụ thuộc vào FastAPI, HTTP framework, hay React.
2. **Nghịch đảo phụ thuộc (Dependency Inversion):** Các dịch vụ bên ngoài (PostgreSQL, Redis, Exa API, PyMuPDF, Tectonic) phải cắm vào Core thông qua các cổng giao tiếp (Adapters implementing Ports).
3. **Tính đơn nguyên Monorepo (Monorepo Atomicity):** Khi thay đổi schema hoặc model tại `packages/core`, bắt buộc cập nhật đồng bộ các tầng phụ thuộc (`apps/api`, `apps/web`) trong cùng một commit. Tuyệt đối không để downstream package bị gãy.

---

## 3. NGUYÊN TẮC HỆ THỐNG DỮ LIỆU CHUYÊN SÂU (DDIA PRINCIPLES)

Áp dụng các chuẩn mực từ cuốn cẩm nang *"Designing Data-Intensive Applications"* (Martin Kleppmann):

### 3.1. Độ Tin Cậy (Reliability & Fault Tolerance)
- **Zero DB Junk Invariant:** Cấm tuyệt đối việc tạo dữ liệu rác, bản ghi thử nghiệm bừa bãi vào CSDL PostgreSQL chính.
- **Tenant Isolation:** Mọi câu truy vấn dữ liệu (SELECT, INSERT, UPDATE, DELETE) bắt buộc phải gắn với định danh `user_id` của phiên làm việc.
- **Graceful Degradation:** Khi các dịch vụ bên ngoài (LLM provider, Tectonic binary) gặp sự cố, hệ thống phải kích hoạt fallback an toàn (PyMuPDF preview, cache offline) mà không làm sập ứng dụng.

### 3.2. Tính Nhất Quán & Đồng Thời (Concurrency & Consistency)
- **Optimistic Concurrency Control (OCC):** Mọi bảng dữ liệu có tính biến đổi cao (`documents`, `drafts`, `research_sessions`) bắt buộc duy trì trường số nguyên `version`. Mọi thao tác cập nhật phải kiểm tra `WHERE id = :id AND version = :current_version` và tăng version lên 1 để triệt tiêu lỗi mất mát dữ liệu (Lost Updates).
- **Tính lũy kế & Idempotency:** Mọi API mutation phải an toàn khi gọi lại nhiều lần bằng `idempotency_key` hoặc khóa duy nhất.

### 3.3. Khả Năng Mở Rộng & Bảo Trì (Scalability & Maintainability)
- **Asynchronous Non-blocking I/O:** Sử dụng async/await toàn diện trong FastAPI và React Query để đảm bảo thông lượng cao.
- **Cache-Aside & Thundering Herd Prevention:** Quản lý bộ đệm Redis với TTL hợp lý và distributed lock cho các tác vụ nặng (như băm vector, sinh embedding).

---

## 4. QUY CHUẨN VIẾT CODE SẠCH (CLEAN CODE & DESIGN PATTERNS)

### 4.1. Clean Code Standards
- **Quy tắc giới hạn chiều dài dòng (Line Length):** Chiều dài tối đa 100 ký tự cho Python (tuân thủ Ruff `line-length = 100`) và TypeScript/Tailwind.
- **Single Responsibility (SRP):** Mỗi hàm/component chỉ làm một việc duy nhất và làm thật tốt. Hàm dài quá 40 dòng phải cân nhắc phân rã.
- **DRY (Don't Repeat Yourself):** Không lặp lại logic. Trích xuất các logic dùng chung thành hooks (`useStreamingChat`, `useWorkspaceStore`) hoặc domain services.
- **Tên biến có ý nghĩa sư phạm:** Đặt tên rõ ràng bằng tiếng Anh chuẩn ngành kỹ thuật, không dùng tên viết tắt vô nghĩa (`temp`, `data2`, `x`).
- **Bảo toàn chú thích & tài liệu:** Giữ nguyên các docstrings, comment nghiệp vụ hiện có; giải thích "LÝ DO TẠI SAO" (Why) chứ không chỉ mô tả "LÀM CÁI GÌ" (What).

### 4.2. Mẫu Thiết Kế Được Áp Dụng (Design Patterns)
- **Factory Pattern:** Tạo instance tài liệu (`DocumentFactory`), starter templates LaTeX.
- **Adapter Pattern:** Chuyển đổi linh hoạt giữa các LLM backend, LaTeX compilers (Tectonic vs PyMuPDF).
- **Repository Pattern:** Trừu tượng hóa việc truy xuất dữ liệu trong `apps/api/src/api/services/`.
- **State Machine Pattern:** Quản lý vòng đời hội thoại Socratic Copilot (`idle` -> `reasoning` -> `streaming` -> `complete` -> `idle`) đảm bảo giải phóng input ngay khi kết thúc.
- **Observer Pattern:** Đồng bộ hóa realtime qua Server-Sent Events (SSE) và Zustand state stores.

---

## 5. TRIẾT LÝ THIẾT KẾ GIAO DIỆN CỦA FOUNDER (FOUNDER DESIGN PRINCIPLES)

1. **Triết Lý "Ngăn Tủ / Chiếc Túi Gọn Gàng":**
   - Màn hình chính tối giản tối đa, không dàn trải các nút bấm và tùy chọn thừa.
   - Gom nhóm các công cụ phụ thành các "ngăn tủ" (dropdown/popover/drawer) - khi bấm vào nút mới mở ra để chọn.
2. **Thanh Ribbon Phụ Tự Động Ẩn Sau 5 Giây:**
   - Dải công cụ phụ (secondary toolbar/ribbon) tự động ẩn sau 5 giây nếu không tương tác, và hiện lại mượt mà khi hover.
3. **Chuẩn Mực Trích Dẫn & Bounding Box:**
   - Gắn thẻ inline citation `[^cit_x]` tại chính xác câu trích dẫn; click vào lập tức cuộn và highlight Bounding Box trên PDF canvas.
4. **Học Thuật Sắc Nét:**
   - Hỗ trợ công thức toán KaTeX chuẩn mực.
   - Trực quan hóa mindmap, sơ đồ kiến trúc, flowchart thông qua Mermaid.js tự động.

---

## 6. KỶ LUẬT KIỂM THỬ & CỔNG CHẤT LƯỢNG (TESTING & QUALITY GATES)

Mọi công việc chỉ được xem là hoàn tất khi vượt qua 100% Quality Gates:
- **Backend Quality Gate:**
  * `pytest packages/core/tests/` -> **100% PASS**
  * `pytest apps/api/tests/` -> **100% PASS**
  * `uv run ruff check .` & `uv run ruff format --check .` -> **0 lỗi**
- **Frontend Quality Gate:**
  * `pnpm --prefix apps/web exec tsc -b` -> **0 lỗi (Zero Errors)**
  * `pnpm --prefix apps/web test:run` -> **100% PASS**
  * `pnpm --prefix apps/web build` -> **Build thành công**
- **Runtime Introspection Gate:**
  * Kiểm tra thực tế dịch vụ `systemctl is-active verischolar-api.service` -> `active`.
  * Probe HTTP 200 OK trên các endpoints live: `/health`, `/dashboard`, `/writing`.

---

## 7. GIAO THỨC PHỐI HỢP ĐA TÁC TỬ (MULTI-AGENT PROTOCOL)

1. **Zero Solo-Work Invariant:** Tuyệt đối không làm việc đơn độc hoặc tự phê duyệt code của chính mình.
2. **Phân Định Trách Nhiệm Rõ Ràng:**
   - **Coordinator (`w2:p1`):** Điều phối tổng thể, giao việc, kiểm soát kiến trúc và kết nối Founder.
   - **Lead Reviewer (`w2:p2`):** Trưởng ban chất lượng độc lập, kiểm tra chéo, chạy eval và cấp chứng chỉ Quality Gate Pass.
   - **Backend Specialist (`w2:p3`):** Chịu trách nhiệm toàn bộ API, Database, OCC, Sandbox Compiler và Core Services.
   - **Frontend Specialist (`w2:p4`):** Chịu trách nhiệm toàn bộ UI/UX, Component, Tailwind CSS, Responsive và State Management.
3. **Giao tiếp minh bạch:** Luôn báo cáo bằng chứng khách quan (lệnh chạy thực tế, mã lỗi, thời gian thực thi) trong mọi phản hồi.
