# VERISCHOLAR MVP — TỔNG QUAN KIẾN TRÚC, RÀNG BUỘC & DANH SÁCH DỌN DẸP CODEBASE
# (FILE 00: OVERVIEW, ARCHITECTURE & OUT-OF-SCOPE CLEANUP)

---

## 1. Mục Đích Thực Tiễn & Giá Trị Cốt Lõi (Intent & The Why)

**VeriScholar** là nền tảng trợ lý AI nghiên cứu khoa học toàn trình (Đồ án Tốt nghiệp Sinh viên Giỏi CNTT), giải quyết trực tiếp nỗi đau thực tế của sinh viên và người làm nghiên cứu khi phải ghép nối thủ công nhiều công cụ rời rạc:
* Khi mới bắt đầu đề tài chưa có sẵn file PDF, không biết tìm bài báo chuẩn ở đâu.
* Đọc bài báo tiếng Anh chuyên ngành nhiều công thức toán khó hiểu, hỏi ChatGPT thì sợ AI "bịa số liệu, bịa nguồn" (Hallucination) hoặc giải thích nhảy cóc từ kiến thức A xuống thẳng D.
* Đang đọc gặp trích dẫn `[14]` phải cuộn xuống cuối bài, mở tab mới đi tìm file PDF gây đứt mạch tư duy.
* Khi viết báo cáo/bài báo khoa học trên Overleaf thì không có AI hỗ trợ sâu, phải tự gõ từng lệnh LaTeX/BibTeX và tự dò sửa từng dòng lỗi biên dịch.

**Luồng giá trị khép kín của VeriScholar MVP:**
1. **Khởi đầu từ con số 0 (Discovery):** Gõ chủ đề nghiên cứu ngay tại màn hình chính hoặc trang Discovery $\rightarrow$ Tìm qua Exa AI / Semantic Scholar / arXiv và mở đọc ngay bài báo Open Access.
2. **Đọc sâu & Hỏi đáp Tiếng Việt có Bảo chứng Khung viền vàng (RAG + Bounding Box):** Đọc PDF gốc trên khung trái, hỏi đáp bằng Tiếng Việt ở khung phải; mọi số liệu/luận điểm đều gắn huy hiệu `[📄 Tên bài • Trang X]` bấm vào là tô sáng đúng đoạn gốc trên PDF, kết hợp **Gợi ý Lộ trình Học Tuần tự (A $\rightarrow$ B $\rightarrow$ C $\rightarrow$ D)**.
3. **Mở rộng Ngữ cảnh 3 Cột 2 Tầng (References + Exa Search):** Bóc tách References cuối bài theo mã DOI/arXiv ID, hiển thị Bảng 3 Cột, bấm 1-Click nạp tức thì Abstract (< 500ms) và tải ngầm PDF mở thêm Tab mới.
4. **Kho Paper Yêu thích & GraphRAG 4 Thực thể:** Bấm Star lưu bài báo vào thư mục đề tài $\rightarrow$ Tự động trích xuất đồ thị 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) trên PostgreSQL + `pgvector`.
5. **Không gian Soạn thảo Agentic Overleaf (LangGraph + E2B Sandbox):** Chuyển từ phiên đọc sang phiên viết 3 cột; Agent tự sửa `main.tex`/`references.bib`, tự truy vấn Kho GraphRAG và tự biên dịch/vá lỗi trên E2B Sandbox (tối đa 3 vòng lặp).
6. **Giám sát & Quản lý lỗi thực chiến (Monitoring 3 Tầng):** Đồng bộ mã `trace_id` xuyên suốt từ Giao diện $\rightarrow$ Backend $\rightarrow$ Langfuse (`verischolar-dev` / `verischolar-prod`) $\rightarrow$ Sentry & Telegram/Discord Webhook + API kiểm tra sức khỏe hệ thống.

---

## 2. Sơ Đồ Chỉ Mục Bộ Tài Liệu `./PRD/` (Đọc Đúng File Theo Từng Module)

Để tiết kiệm token và tránh nhiễu ngữ cảnh khi lập trình từng phần, toàn bộ PRD được chia thành **8 file độc lập** trong thư mục `./PRD/`:

| Thứ tự | Tên File | Khi nào AI / Kỹ sư cần đọc file này? |
| :--- | :--- | :--- |
| **00** | [`00-overview-and-cleanup.md`](./00-overview-and-cleanup.md) | Khi cần nắm tổng quan MVP, các ràng buộc cứng và **danh sách các phần dư thừa cần xóa khỏi dự án**. |
| **01** | [`01-auth-and-user.md`](./01-auth-and-user.md) | Khi làm việc với Đăng nhập, Đăng ký, OAuth, Hồ sơ người dùng và Phân quyền `user_id`. |
| **02** | [`02-discovery-and-documents-crud.md`](./02-discovery-and-documents-crud.md) | Khi làm việc với Tìm kiếm bài báo theo chủ đề (Exa/arXiv) và CRUD quản lý file PDF (`documents`). |
| **03** | [`03-sessions-and-deep-reading-crud.md`](./03-sessions-and-deep-reading-crud.md) | Khi làm việc với CRUD Phiên đọc (`sessions`), Tab PDF, Trình đọc `PdfCanvasViewer`, RAG Chat `Bounding Box` và Sổ tay (`notes`). |
| **04** | [`04-context-table-and-roadmap.md`](./04-context-table-and-roadmap.md) | Khi làm việc với Bảng References 3 Cột, Nạp Exa 2 Tầng và Gợi ý Lộ trình Học Tuần tự (A $\rightarrow$ B $\rightarrow$ C $\rightarrow$ D). |
| **05** | [`05-favorite-library-and-graphrag.md`](./05-favorite-library-and-graphrag.md) | Khi làm việc với Thư mục yêu thích (`folders`, `star`) và GraphRAG 4 thực thể trên PostgreSQL. |
| **06** | [`06-agentic-overleaf-writing.md`](./06-agentic-overleaf-writing.md) | Khi làm việc với Màn hình viết bài Overleaf 3 cột, CRUD Bản thảo (`drafts`, `figures/`), LangGraph Agent và E2B Sandbox. |
| **07** | [`07-monitoring-and-langfuse.md`](./07-monitoring-and-langfuse.md) | Khi làm việc với `.env` (`dev`/`prod`), Langfuse Tracing/Scores, Sentry/Telegram Alerting và System Health Monitoring. |

---

## 3. Mục Tiêu, Phi Mục Tiêu & Chống Mục Tiêu (Goals, Non-Goals & Anti-Goals)

### A. Mục tiêu cốt lõi (MVP Goals)
1. Hoàn thiện trọn vẹn luồng **Tìm bài $\rightarrow$ Đọc hiểu có Bounding Box & Lộ trình A–B–C–D $\rightarrow$ Mở rộng Context 2 tầng $\rightarrow$ Lưu Kho GraphRAG $\rightarrow$ Soạn thảo LaTeX tự động với LangGraph & E2B**.
2. Đảm bảo đầy đủ các thao tác **Thêm / Xem / Sửa / Xóa (CRUD)** cơ bản cho mọi tài nguyên: Tài khoản, Tài liệu PDF, Phiên đọc & Lịch sử Chat, Sổ tay ghi chú, Thư mục yêu thích, và Bản thảo LaTeX + Hình ảnh.
3. Quản lý lỗi và giám sát rõ ràng trên cả 2 môi trường `development` và `production` thông qua mã `trace_id` đồng nhất.

### B. Phi mục tiêu (Non-Goals — Không làm trong MVP)
1. **Không làm chế độ hiển thị toàn văn PDF/HTML Tiếng Việt ở khung đọc bên trái:** Để tập trung tối đa cho chất lượng MVP, khung bên trái chỉ hiển thị bản gốc PDF (`PdfCanvasViewer.tsx`). Việc dịch đoạn văn hoặc giải thích bằng Tiếng Việt được thực hiện trực tiếp qua khung Chat AI bên phải (khi người dùng hỏi hoặc bấm `[💬 Đưa vào Chat]` từ đoạn bôi đen).
2. **Không dùng Prompt Management đám mây của Langfuse:** Toàn bộ Prompts được lưu trực tiếp trong mã nguồn Python của dự án.
3. **Không cài đặt thêm Neo4j hoặc cụm Docker Prometheus/Grafana nặng nề:** GraphRAG chạy trực tiếp trên PostgreSQL + `pgvector`; Monitoring hệ thống tích hợp trực tiếp qua API `/health/ready`, `/api/v1/system/status`, Langfuse và Sentry/Webhook.
4. **Không duy trì các môi trường `.env` thừa (`uat`, `staging`, `sit`, `enterprise`):** Chỉ sử dụng duy nhất 2 môi trường là `development` và `production`.

### C. Chống mục tiêu (Anti-Goals — Nếu xảy ra coi như lỗi nghiêm trọng)
1. **AI tự bịa đặt công thức hoặc số liệu:** Tuyệt đối cấm AI đoán mò công thức ở cuối bài báo mới thêm khi tiến trình tải ngầm PDF (Tầng 2) chưa hoàn tất.
2. **Biên dịch LaTeX trực tiếp trên máy chủ chính (Host Server):** Mọi lệnh `pdflatex`/`bibtex` bắt buộc chạy cô lập trong E2B Sandbox với cờ `--no-shell-escape`.
3. **Agent ghi đè làm mất code người dùng vừa gõ tay:** Phải đồng bộ nội dung mới nhất trên trình soạn thảo trước khi Agent sửa và có nút Undo 1-Click.

---

## 4. Các Ràng Buộc Cứng & Cấu Trúc Điều Hướng Toàn Ứng Dụng (Hard Constraints & Global Navigation)

* **Giới hạn file PDF tải lên:** Dung lượng tối đa `50 MB`, tối đa `100 trang` / bài báo, định dạng Digital PDF có lớp văn bản.
* **Giới hạn phiên đọc sâu:** Tối đa `5 bài báo` mở đồng thời trong 1 phiên để giữ độ chính xác cao nhất cho ngữ cảnh RAG.
* **Giới hạn biên dịch E2B Sandbox:** Timeout cứng `15 giây` / lượt biên dịch; tối đa `3 vòng lặp` tự sửa lỗi liên tiếp.
* **Cơ sở dữ liệu:** Thuần **PostgreSQL 16+ kèm extension `pgvector`** (`Vector(1536)`) và **Redis 7** (OTP, rate-limiting, idempotency); không sử dụng SQLite fallback.
* **Thanh Menu Điều Hướng Chính của Ứng Dụng (Global Sidebar Navigation):**
  Sau khi dọn dẹp các trang thừa, toàn bộ ứng dụng thống nhất đúng **4 mục điều hướng chính**:
  1. **`🔍 Khám phá & Phiên đọc`** (`/` và `/discovery`): Tìm bài báo mới theo chủ đề, tải PDF lên và quản lý danh sách các Phiên đọc sâu (`Sessions`).
  2. **`⭐ Kho Yêu thích`** (`/library`): Quản lý cây thư mục đề tài cá nhân và tra cứu tổng hợp trên GraphRAG 4 Thực thể.
  3. **`✍️ Soạn thảo LaTeX`** (`/writing`): Quản lý danh sách Bản thảo (`Drafts`) và không gian soạn thảo Overleaf 3 cột tích hợp LangGraph Agent + E2B Sandbox.
  4. **`👤 Tài khoản & Giao diện`**: Xem/sửa hồ sơ cá nhân, đổi mật khẩu, chuyển đổi giao diện Sáng/Tối (`Light/Dark Mode`) và Đăng xuất.

---

## 5. Danh Sách Các Tính Năng & File Dư Thừa Cần XÓA BỎ Khỏi Codebase (Cleanup List)

Do trước đây hệ thống có một số tính năng phát triển tràn lan ngoài phạm vi MVP, các thành phần dưới đây **bắt buộc phải được dọn dẹp và xóa bỏ** để codebase gọn sạch, chuẩn mực:

| Nhóm cần xóa | Các API / File / Component cụ thể cần loại bỏ | Lý do xóa |
| :--- | :--- | :--- |
| **1. Các file cấu hình môi trường thừa** | `apps/api/.env.uat`, `deploy/.env.enterprise.example`, cấu hình `uat`/`staging` trong `config.py` | Dự án cá nhân chỉ dùng 2 môi trường `development` và `production`. |
| **2. Chia sẻ Draft đa người dùng & Bình luận Peer-Review** | API `/drafts/{id}/share`, `/drafts/{id}/comments`, bảng `DraftCommentModel`, `DraftSharingModal.tsx`, `DraftCommentsPane.tsx` | Không nằm trong luồng MVP cá nhân, gây phức tạp không cần thiết. |
| **3. Xuất nhảy sang web Overleaf bên ngoài** | API `/drafts/{id}:export-overleaf`, `/drafts/{id}/overleaf`, `/overleaf-launch` | Bản thân màn hình Writing 3 cột của VeriScholar đã là không gian Overleaf tích hợp E2B. |
| **4. Ký ức liên tưởng (Associative Memory Card)** | API `/drafts/{id}/associative-suggestions`, `associative_memory_service.py`, `AssociativeMemoryCard.tsx` | Thay thế bằng công cụ `query_library_graph_rag` trực tiếp trong LangGraph Agent. |
| **5. Giao diện Kiểm chứng SAFE tĩnh kiểu cũ** | API `/drafts/{id}/verify-facts`, `SourceEvidenceModal.tsx`, giao diện `WritingAssistantPane.tsx` kiểu danh sách claim cũ | Thay thế hoàn toàn Cột 3 bằng **Khung Chat Hội Thoại LangGraph Agent**. |
| **6. Ma trận So sánh 100+ bài báo kiểu cũ** | API `/folders/comparison-matrix`, `/folders/{id}/comparison-matrix`, `ComparisonMatrixModal.tsx`, `ComparisonMatrixPage.tsx` | Thay thế bằng Kho Yêu thích + Truy vấn GraphRAG 4 Thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`). |
| **7. Các màn hình phụ & API xuất gói thừa** | `DashboardCoworkView.tsx`, `DashboardProjectView.tsx`, `ProjectsPage.tsx`, API `/sessions/{id}:export-bundle`, `/documents/{id}/export-pdf` | Giao diện thừa không gắn với hành trình nghiên cứu cốt lõi. |
| **8. Các file tài liệu PRD cũ gây nhiễu** | `docs/02-modules-and-features/pillar-1..5.md` (hoặc cập nhật trỏ hết về `./PRD/`) | Tránh để AI đọc nhầm thiết kế cũ khi lập trình. |
