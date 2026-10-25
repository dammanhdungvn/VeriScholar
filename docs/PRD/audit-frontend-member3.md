# Báo Cáo Kiểm Toán Độc Lập (Read-Only Audit) — Member 3: Frontend (`apps/web/`) & Hệ Thống Tài Liệu (`./docs/`)

> **Người thực hiện:** Member 3 (Frontend & Documentation Auditor)  
> **Phạm vi kiểm tra:** Toàn bộ mã nguồn `apps/web/src/` và toàn bộ hệ thống tài liệu `./docs/` (ngoài `./docs/PRD/`)  
> **Tài liệu đối chiếu chuẩn (Single Source of Truth):** `./docs/PRD/00-overview-and-cleanup.md` đến `./docs/PRD/07-monitoring-and-langfuse.md`  
> **Trạng thái thực thi:** **READ-ONLY AUDIT** — Tuyệt đối chưa xóa hoặc sửa bất kỳ file code/docs hiện hành nào.

---

## 1. Tóm Tắt Điều Hành (Executive Summary)

Qua quá trình rà soát đối chiếu 100% cây thư mục `apps/web/src/` và `./docs/` với bộ tài liệu chuẩn `./docs/PRD/` (`00` đến `07`), hệ thống hiện tại đang tồn tại sự lệch pha đáng kể giữa **kiến trúc cũ (5-Pillar Enterprise / Multi-user Collaboration / 100+ Paper Matrix / SAFE NLI / Local Docker)** và **kiến trúc MVP thực dụng mới (Single-User Deep Research & Agentic Overleaf Workspace)**:

1. **Điều hướng & Trang (Routes & Pages):** Thanh điều hướng trái (`DashboardTaskbar.tsx`) và bộ định tuyến (`routes.tsx`) đang hiển thị **7 mục** (bao gồm `Matrix`, `Projects`, `Notes` độc lập, `Cowork`), trong khi PRD `00` §4 quy định **chỉ giữ đúng 4 mục cốt lõi** (`🔍 Khám phá & Phiên đọc`, `⭐ Kho Yêu thích`, `✍️ Soạn thảo LaTeX`, `👤 Tài khoản & Giao diện`).
2. **Components & Modals dư thừa (Bắt buộc XÓA):** Có **15 component/modal** và **2 file mock data** thuộc các tính năng đã bị loại bỏ trong PRD `00` §5 (Ma trận 100+ bài báo, Chia sẻ bản thảo nhiều người, Bình luận nội tuyến Peer Review, SAFE Fact-Checking tĩnh, Associative Memory Card, Xuất gói ZIP ngoại tuyến, Xuất PDF kèm ghi chú, Đồng bộ Git Overleaf, Chế độ Cowork/Project giả lập, Chọn Model AI giả lập).
3. **Khoảng trống tính năng MVP (Bắt buộc REFACTOR / BỔ SUNG):**
   - **Module 02 (Discovery):** Cần hợp nhất luồng tìm kiếm chủ đề **Zero-to-Reading** (Exa AI / Semantic Scholar / arXiv) hiển thị thẻ bài báo kèm nhãn `[🟢 Có sẵn PDF Open Access]` / `[🟡 Chỉ có Tóm tắt]` và nút `[📖 Mở đọc ngay]` tự động tạo `ResearchSession`.
   - **Module 03 & 04 (Reading & Citation Bridge):** Cần gỡ bỏ đồ thị trích dẫn 2-hop SVG (`GET /sessions/{id}/citation-graph`), chuẩn hóa **Bảng Ngữ Cảnh Tài Liệu Tham Khảo 3 Cột** (`Name`, `URL`, `Action`), bổ sung **Thẻ gợi ý Socratic Bridge (A → B → C → D)** trong luồng chat, hỗ trợ xóa bài báo khỏi phiên đọc (`DELETE /api/v1/sessions/{id}/documents/{doc_id}`) để giải phóng giới hạn 5 bài, và thêm nút **Cầu nối Đọc → Viết** (`[✍️ Bắt đầu viết bài từ phiên đọc này]`).
   - **Module 05 (Favorite Library & 4-Entity GraphRAG):** Cần gỡ bỏ `ComparisonMatrixModal` và bổ sung giao diện truy vấn **GraphRAG 4 thực thể** (`Paper`, `Method`, `Dataset`, `MetricResult`) + **4 quan hệ** (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`) tại `/library`.
   - **Module 06 (Agentic Overleaf):** Cần thay thế hoàn toàn khung kiểm tra SAFE tĩnh (`WritingAssistantPane.tsx`) bằng **Khung Chat Đối Thoại LangGraph Agent** (`GET/POST/DELETE /api/v1/drafts/{id}/messages`) có hiển thị tiến trình công cụ (`🔍 Đang tra cứu Kho GraphRAG...` -> `✍️ Đang cập nhật main.tex...` -> `⚙️ Đang biên dịch trên E2B (Lần 1/3)...`), bổ sung quản lý `references.bib` (`bib_content`), nút **Hoàn tác 1 chạm (`[↩️ Hoàn tác (Undo)]`)**, và nút xóa tệp hình ảnh (`DELETE /api/v1/drafts/{id}/assets/{asset_id}`).
   - **Module 07 (Monitoring & Langfuse):** Cần kết nối nút `ThumbsUp` / `ThumbsDown` trên tin nhắn AI với API chấm điểm `user_feedback` (`1` / `0`) và hiển thị `meta.trace_id` (`Mã tra cứu: tr_...`) trên hộp thoại báo lỗi (`DashboardErrorBoundary.tsx`).
4. **Hệ thống Tài liệu (`./docs/` ngoài `./docs/PRD/`):** Toàn bộ thư mục `docs/02-modules-and-features/` (7 file) và `docs/04-operations-and-cicd/docker-enterprise-guide.md` đang mô tả kiến trúc 5-Pillar cũ (Ma trận 100+ bài, SAFE NLI, Đồng bộ Overleaf, Air-gapped Docker) — **mâu thuẫn trực tiếp** với `./docs/PRD/` và cần bị **XÓA**. Các file còn lại trong `01-architecture/`, `03-frontend-engineering/`, `04-operations-and-cicd/`, `05-testing-and-qa/` và `docs/README.md` cần được **REFACTOR** để trỏ về `./docs/PRD/` làm nguồn chân lý duy nhất.

---

## 2. Kiểm Toán Định Tuyến, Trang & Thanh Điều Hướng Toàn Cục (Pages, Routes & Navigation)

### 2.1. Đối chiếu Thanh Điều Hướng Toàn Cục (PRD `00` §4)

Theo `docs/PRD/00-overview-and-cleanup.md` (Mục 4), thanh điều hướng bên trái (Global Left Sidebar) **chỉ được phép có đúng 4 mục**:
1. `🔍 Khám phá & Phiên đọc (Discovery & Sessions)` — `/`, `/discovery`, `/dashboard`, `/dashboard/:sessionId`
2. `⭐ Kho Yêu thích (Favorite Library)` — `/library`
3. `✍️ Soạn thảo LaTeX (Agentic Overleaf)` — `/writing`, `/writing/:draftId`
4. `👤 Tài khoản & Giao diện (Profile, Settings & Theme Toggle)` — `/profile`, `/settings`, Đổi giao diện Sáng/Tối, Đăng xuất

### 2.2. Danh sách Định tuyến (`apps/web/src/app/routes.tsx`) & Trang (Pages) cần XÓA hoặc REFACTOR

| Đường dẫn / File | Thành phần (Component) | Hành động | Lý do đối chiếu theo PRD MVP |
| :--- | :--- | :---: | :--- |
| `/library/matrix`, `/matrix` trong `apps/web/src/app/routes.tsx` | `ComparisonMatrixPage` | **XÓA ROUTE** | Tính năng Ma trận đối sánh 100+ bài báo bị cắt bỏ hoàn toàn (PRD `00` §5, PRD `05` §2). |
| `/projects` trong `apps/web/src/app/routes.tsx` | `ProjectsPage` | **XÓA ROUTE** | Chế độ quản lý Project đa tầng bị loại bỏ để gom về `ResearchSession` và `Folder` (PRD `00` §4 & §5). |
| `/notes` trong `apps/web/src/app/routes.tsx` | `NotesPage` | **XÓA ROUTE ĐỘC LẬP** | Trong PRD `00` §4 & PRD `03` §3, Ghi chú nghiên cứu (Research Notes) nằm trong tab cột phải của Phiên đọc (`NotesPanelContainer.tsx`), không phải mục điều hướng độc lập trên thanh công cụ toàn cục. |
| `/citations` trong `apps/web/src/app/routes.tsx` | `DiscoveryPage` | **XÓA ROUTE TRÙNG** | Gom luồng khám phá bài báo về `/` và `/discovery`; đồ thị trích dẫn 2-hop đã bị loại bỏ (PRD `04` §1). |
| `apps/web/src/features/library/components/ComparisonMatrixPage.tsx` | `ComparisonMatrixPage` | **XÓA FILE** | Trang hiển thị Ma trận đối sánh 100+ bài báo (PRD `00` §5, PRD `05` §2). |
| `apps/web/src/features/dashboard/components/ProjectsPage.tsx` | `ProjectsPage` | **XÓA FILE** | Trang quản lý Project dư thừa (PRD `00` §5). |
| `apps/web/src/features/notes/components/NotesPage.tsx` | `NotesPage` | **XÓA FILE** | Trang `/notes` độc lập dư thừa (giữ lại `NotesPanelContainer.tsx` và các component con dùng trong `DashboardWorkspace.tsx`). |
| `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx` | `DashboardTaskbar` | **REFACTOR** | Hiện đang hiển thị 7 mục (`research`, `library`, `matrix`, `notes`, `writing`, `discovery`, `projects`). Cần rút gọn về đúng **4 mục chuẩn** của PRD `00` §4 và tích hợp nút chuyển đổi Sáng/Tối (Light/Dark Mode) + Tài khoản ở đáy thanh. |

---

## 3. Kiểm Toán Chi Tiết Components & Modals Theo Từng Module (`apps/web/src/features/`)

### 3.1. Module 01: Xác Thực, Hồ Sơ Học Giả & Quản Lý Tài Khoản (`features/auth/`, `features/landing/`)

| Đường dẫn File | Phân loại | Hành động | Chi tiết sai lệch & Yêu cầu xử lý theo PRD `01` |
| :--- | :--- | :---: | :--- |
| `apps/web/src/features/auth/data/mock-auth.ts` | Mock Data | **XÓA FILE** | Dữ liệu đăng nhập giả lập cũ, không còn sử dụng vì `authApi.ts` đã gọi API thật. |
| `apps/web/src/features/auth/data/mock-users.ts` | Mock Data | **XÓA FILE** | Dữ liệu người dùng giả lập cũ, không dùng trong MVP. |
| `apps/web/src/features/auth/components/AccountSettingsModal.tsx` | Modal | **REFACTOR** | **Dòng 623–646:** Đang hiển thị thẻ *"Overleaf / LaTeX Cloud Workspace (Institutional Cloud Bridge)"* trong tab `Connected Accounts`. Cần **xóa khối giao diện Overleaf Cloud Bridge này** vì PRD `00` §5 & PRD `06` §2 đã loại bỏ tính năng đồng bộ Git Overleaf bên ngoài. Các phần Hồ sơ, Đổi mật khẩu, Phiên đăng nhập (`GET/DELETE /api/v1/auth/sessions`), Khóa BYOK (`sk-...`), và giao diện Sáng/Tối giữ nguyên. |
| `apps/web/src/features/auth/components/LoginForm.tsx` | Component | **GIỮ NGUYÊN** | Đã khớp PRD `01` (`POST /api/v1/auth/login`). |
| `apps/web/src/features/auth/components/RegisterForm.tsx` | Component | **GIỮ NGUYÊN** | Đã khớp PRD `01` (`POST /api/v1/auth/register`). |
| `apps/web/src/features/auth/components/ProtectedRoute.tsx` | Component | **GIỮ NGUYÊN** | Đã khớp cơ chế bảo vệ route và kiểm tra phiên đăng nhập. |

---

### 3.2. Module 02, 03 & 04: Khám Phá (Discovery), Không Gian Đọc Sâu (Reading Session) & Cầu Nối Trích Dẫn (Citation Bridge) (`features/dashboard/`, `features/discovery/`, `features/sessions/`, `features/reader/`, `features/documents/`, `features/notes/`)

| Đường dẫn File | Phân loại | Hành động | Chi tiết sai lệch & Yêu cầu xử lý theo PRD `02`, `03`, `04`, `06`, `07` |
| :--- | :--- | :---: | :--- |
| `apps/web/src/features/dashboard/components/DashboardCoworkView.tsx` | Component | **XÓA FILE** | Giao diện tác vụ Cowork Agent giả lập bằng `setTimeout` và dữ liệu mẫu `COWORK_SAMPLE_TASKS` — không thuộc kiến trúc MVP (PRD `00` §5). |
| `apps/web/src/features/dashboard/components/DashboardProjectView.tsx` | Component | **XÓA FILE** | Giao diện Project View dư thừa (PRD `00` §5). |
| `apps/web/src/features/dashboard/components/ModelSelectorModal.tsx` | Modal | **XÓA FILE** | Hộp thoại chọn model AI giả lập (`AVAILABLE_MODELS` cứng ở client). Trong MVP, định tuyến model do Backend + BYOK (`AccountSettingsModal.tsx`) đảm nhiệm. |
| `apps/web/src/features/dashboard/components/QuickUploadDocModal.tsx` | Modal | **XÓA FILE** | Hộp thoại tải tài liệu giả lập dùng `setTimeout(..., 1500)` không gọi API thật (đã được thay thế bởi `HeroUploadDropzone.tsx` + `ParseConfigModal.tsx`). |
| `apps/web/src/features/sessions/components/ExportBundleDialog.tsx` | Modal | **XÓA FILE** | Hộp thoại xuất gói nghiên cứu ngoại tuyến `.zip` (`POST /sessions/{id}:export-bundle`) — bị loại bỏ rõ ràng trong PRD `00` §5 & PRD `03` §2. |
| `apps/web/src/features/dashboard/components/DashboardContainer.tsx` | Container | **REFACTOR** | 1. Xóa các nhánh render `appMode === "project"` (`DashboardProjectView`) và `appMode === "cowork"` (`DashboardCoworkView`).<br>2. **Sửa lỗi hiển thị Standby Hero:** Hiện tại biến `showStandbyHero` chỉ render `<HeroUploadDropzone />` mà làm ẩn mất `<DashboardHeroSection />` (chứa thanh tìm kiếm chủ đề). Cần hiển thị kết hợp cả **Thanh tìm kiếm chủ đề (Topic Search)** và **Khung kéo thả PDF (`HeroUploadDropzone`)** trên cùng màn hình chào mừng đúng theo PRD `02` §2. |
| `apps/web/src/features/dashboard/components/DashboardHeroSection.tsx` | Component | **REFACTOR** | Hiện tại khi nhấn tìm kiếm chỉ chuyển hướng sang `/discovery?q=...` và hiển thị các mẫu gợi ý Cowork (`COWORK_SAMPLE_TASKS`). Cần refactor để:<br>1. Xóa toàn bộ tham chiếu đến `COWORK_SAMPLE_TASKS` và nút chuyển đổi `appMode` (`chat` / `cowork` / `project`).<br>2. Kết nối trực tiếp với luồng tìm kiếm bài báo học thuật (**Zero-to-Reading** qua Exa AI / Semantic Scholar / arXiv) hiển thị danh sách kết quả gồm: Tiêu đề, Tác giả, Năm, Tóm tắt, nhãn trạng thái `[🟢 Có sẵn PDF Open Access]` / `[🟡 Chỉ có Tóm tắt (Abstract Only)]`, và nút **`[📖 Mở đọc ngay]`** (tự động tải PDF ngầm + tạo `ResearchSession` + chuyển thẳng vào giao diện đọc) hoặc **`[📤 Tự tải file PDF lên]`** nếu bài bị khóa Paywall (PRD `02` §2A). |
| `apps/web/src/features/discovery/components/DiscoveryPage.tsx` | Page / View | **REFACTOR** | 1. **Xóa phần hiển thị Đồ thị trích dẫn 2-hop SVG (`GET /api/v1/sessions/{id}/citation-graph`)** vì PRD `00` §5 & PRD `04` §1 đã loại bỏ hoàn toàn đồ thị mạng lưới trích dẫn.<br>2. Chuyển đổi thành giao diện **Tìm kiếm & Khám phá bài báo (Zero-to-Reading)** đồng bộ với `DashboardHeroSection.tsx` (hỗ trợ nút `[📖 Mở đọc ngay]` tạo phiên đọc từ URL PDF Open Access). |
| `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx` | Container | **REFACTOR** | 1. **Xóa:** `ExportBundleDialog`, `isExportDialogOpen`, `handleExportPdf` (`documentsApi.exportAnnotatedPdf`), và `ModelSelectorModal`.<br>2. **Bổ sung Cầu nối Đọc → Viết (PRD `06` §3):** Thêm nút **`[✍️ Bắt đầu viết bài từ phiên đọc này]`** trên thanh công cụ đầu phiên đọc. Khi bấm: gọi `POST /api/v1/drafts` kèm `session_id` và `document_ids` của phiên đọc (tự động trích xuất BibTeX vào `references.bib` và liên kết `notes`), sau đó điều hướng sang `/writing/{draft_id}`.<br>3. **Bổ sung Chấm điểm Phản hồi Langfuse (PRD `07` §4 Tier 1.3):** Kết nối sự kiện bấm nút `ThumbsUp` / `ThumbsDown` trên câu trả lời AI với API `POST /api/v1/sessions/{session_id}/messages/{message_id}/feedback` (`user_feedback: 1 | 0`). |
| `apps/web/src/features/dashboard/components/DashboardChatStreamView.tsx` | Component | **REFACTOR** | 1. Kết nối nút `ThumbsUp` / `ThumbsDown` (hiện đang là button tĩnh chưa có `onClick`) tới callback gửi `user_feedback` (`1` hoặc `0`) về Backend.<br>2. **Bổ sung Thẻ gợi ý Socratic Bridge (A → B → C → D) (PRD `04` §3):** Khi câu trả lời của AI hoặc người dùng nhắc đến một trích dẫn `[k]` có trong `reference_items` của bài báo đang đọc nhưng bài `[k]` chưa nằm trong phiên đọc, hiển thị thẻ gợi ý thông minh kèm nút 1 chạm **`[➕ Nạp bài [k] vào phiên chat]`** (gọi `POST /api/v1/sessions/{session_id}/references:ingest`). |
| `apps/web/src/features/reader/components/SmartReferenceDrawer.tsx` | Drawer | **REFACTOR** | Chuẩn hóa bảng danh mục tài liệu tham khảo ở cuối bài báo thành đúng **Bảng Ngữ Cảnh Tài Liệu Tham Khảo 3 Cột** theo PRD `04` §2:<br>- **Cột 1 (`Name`):** `[k] Tiêu đề bài báo — Tác giả (Năm)`<br>- **Cột 2 (`URL`):** Liên kết gốc (`[🔗 DOI / arXiv / Nguồn]`) mở tab mới<br>- **Cột 3 (`Action`):**<br>  + Nếu chưa có trong phiên chat: Nút **`[➕ Thêm vào đoạn chat này]`** (Kích hoạt nạp 2 tầng: Tầng 1 `< 500ms` nạp ngay Abstract vào ngữ cảnh RAG; Tầng 2 tải ngầm PDF Open Access và tự mở tab mới trên `DocumentTabBar`, hoặc gắn nhãn `[🟡 Chỉ có Tóm tắt — Bị khóa Paywall]` kèm nút `[📤 Tự tải PDF lên]`).<br>  + Nếu đã có trong phiên chat: Hiển thị **`[✅ Đang trong ngữ cảnh]`** kèm nút **`[🗑️ Xóa khỏi chat]`** (`DELETE /api/v1/sessions/{id}/documents/{document_id}`). |
| `apps/web/src/features/reader/components/ReferenceListModal.tsx` | Modal | **REFACTOR** | Đồng bộ giao diện 3 cột (`Name`, `URL`, `Action`) và luồng nạp 2 tầng / xóa khỏi phiên đọc giống `SmartReferenceDrawer.tsx` (hoặc hợp nhất vào chung một component để tránh trùng lặp). |
| `apps/web/src/features/reader/components/DocumentTabBar.tsx` | Component | **REFACTOR** | Khi người dùng đóng một tab bài báo (`onCloseDocument`) hoặc nhấn gỡ bài báo khỏi phiên đọc, cần hỗ trợ gọi `DELETE /api/v1/sessions/{id}/documents/{document_id}` để giải phóng slot trong giới hạn tối đa **5 bài báo / phiên đọc** (PRD `03` §3 & §5). |
| `apps/web/src/features/dashboard/components/WorkspaceToolsMenu.tsx` | Menu | **REFACTOR** | Xóa 2 mục menu: *"Xuất gói ngoại tuyến (.zip)"* (`onOpenExportDialog`) và *"Xuất PDF kèm ghi chú"* (`onExportPdf`) theo PRD `00` §5 & PRD `03` §2. |
| `apps/web/src/features/reader/components/ViewportOverflowMenu.tsx` | Menu | **REFACTOR** | Xóa các mục menu xuất gói ZIP ngoại tuyến và xuất PDF kèm ghi chú (`onOpenExportDialog`, `onExportPdf`). |

---

### 3.3. Module 05: Kho Tài Liệu Yêu Thích & Tổng Hợp Đa Tài Liệu GraphRAG (`features/library/`, `features/documents/`)

| Đường dẫn File | Phân loại | Hành động | Chi tiết sai lệch & Yêu cầu xử lý theo PRD `05` |
| :--- | :--- | :---: | :--- |
| `apps/web/src/features/library/components/ComparisonMatrixModal.tsx` | Modal | **XÓA FILE** | Hộp thoại Ma trận đối sánh 100+ bài báo (`ComparisonMatrixModal`) — bị loại bỏ hoàn toàn trong PRD `00` §5 & PRD `05` §2. |
| `apps/web/src/features/library/components/LibraryWorkspaceView.tsx` | View | **REFACTOR** | 1. **Xóa:** Toàn bộ nút bấm và luồng mở Ma trận đối sánh (`ComparisonMatrixModal`), cũng như tab đồ thị giả lập tĩnh.<br>2. **Bổ sung Giao diện Truy vấn & Tổng hợp GraphRAG 4 Thực thể (PRD `05` §3 & §4):** Cho phép người dùng chọn một Thư mục (`Folder`) trong Kho Yêu thích và đặt câu hỏi tổng hợp xuyên tài liệu (`POST /api/v1/folders/synthesis`), hiển thị câu trả lời có dẫn nguồn kèm trực quan hóa/danh sách **4 Thực thể chuẩn** (`Paper`, `Method`, `Dataset`, `MetricResult`) và **4 Quan hệ chuẩn** (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`).<br>3. Đảm bảo thao tác **Bỏ đánh dấu sao** (`POST /api/v1/documents/{id}:toggle-star` với `starred: false`) và **Di chuyển bài báo giữa các thư mục** hoạt động đầy đủ. |
| `apps/web/src/features/documents/components/DocumentLibraryModal.tsx` | Modal | **REFACTOR** | Xóa state `isMatrixOpen`, nút *"Ma trận đối sánh"*, và thẻ `<ComparisonMatrixModal />`. |
| `apps/web/src/features/library/components/StarDocumentModal.tsx` | Modal | **GIỮ NGUYÊN** | Đã hỗ trợ chọn thư mục hiện có hoặc tạo thư mục mới khi gắn sao (`⭐`) bài báo trong phiên đọc (PRD `02` §4 & PRD `05` §4). |
| `apps/web/src/features/library/components/FolderTreeView.tsx` | Component | **GIỮ NGUYÊN / KIỂM TRA** | Đảm bảo hỗ trợ đủ Tạo mới (`POST /api/v1/folders`), Đổi tên (`PATCH /api/v1/folders/{id}`), và Xóa thư mục (`DELETE /api/v1/folders/{id}`). |

---

### 3.4. Module 06: Không Gian Soạn Thảo LaTeX Tự Hành — Agentic Overleaf (`features/writing/`)

| Đường dẫn File | Phân loại | Hành động | Chi tiết sai lệch & Yêu cầu xử lý theo PRD `06` |
| :--- | :--- | :---: | :--- |
| `apps/web/src/features/writing/components/DraftSharingModal.tsx` | Modal | **XÓA FILE** | Hộp thoại chia sẻ bản thảo nhiều người dùng (`viewer`/`commenter`/`editor`) và đồng bộ Git Overleaf — bị cắt bỏ hoàn toàn trong PRD `00` §5 & PRD `06` §2. |
| `apps/web/src/features/writing/components/DraftCommentsPane.tsx` | Component | **XÓA FILE** | Khung bình luận phản biện nội tuyến nhiều người dùng (`DraftCommentsPane`) — bị cắt bỏ trong PRD `00` §5 & PRD `06` §2. |
| `apps/web/src/features/writing/components/AssociativeMemoryCard.tsx` | Component | **XÓA FILE** | Thẻ gợi ý trí nhớ liên tưởng tự động (`AssociativeMemoryCard`) — bị cắt bỏ trong PRD `00` §5 & PRD `06` §2. |
| `apps/web/src/features/writing/components/SourceEvidenceModal.tsx` | Modal | **XÓA FILE** | Hộp thoại kiểm chứng thực tế SAFE NLI tĩnh (`SourceEvidenceModal`) — bị cắt bỏ trong PRD `00` §5 & PRD `06` §2. |
| `apps/web/src/features/writing/components/SuggestionReviewPanel.tsx` | Modal / Panel | **XÓA FILE** | Bảng duyệt diff tĩnh một lần (`SuggestionReviewPanel`) — PRD `06` §4 thay thế bằng cơ chế **LangGraph Agent tự động cập nhật `main.tex` / `references.bib` + Biên dịch E2B + Nút Hoàn tác 1 chạm (`[↩️ Hoàn tác (Undo)]`)**. |
| `apps/web/src/features/writing/components/WritingIconRail.tsx` | Component | **XÓA FILE** | Thanh icon rail cũ không còn được sử dụng (có chứa nút `Briefcase` trỏ tới `/projects`); hiện tại `WritingWorkspace` đã dùng chung `DashboardTaskbar`. |
| `apps/web/src/features/writing/components/WritingWorkspace.tsx` | Container | **REFACTOR LỚN** | 1. **Xóa toàn bộ:** `DraftSharingModal`, `DraftCommentsPane`, `AssociativeMemoryCard`, `SourceEvidenceModal`, `SuggestionReviewPanel`, `handleVerifyFacts`, `handleSyncOverleaf`, `getAssociativeSuggestions`, `getComments`.<br>2. **Bổ sung quản lý `references.bib` (`bibContent`):** Đồng bộ `draft.bib_content` bên cạnh `draft.content` (`main.tex`) qua `PATCH /api/v1/drafts/{id}`.<br>3. **Bổ sung Snapshot Hoàn tác 1 chạm (`previousSnapshot`):** Trước mỗi lần LangGraph Agent cập nhật `main.tex` hoặc `references.bib`, lưu lại bản chụp trạng thái trước đó để người dùng có thể bấm **`[↩️ Hoàn tác (Undo)]`** khôi phục tức thì (PRD `06` §4.1).<br>4. **Kết nối Cột 3 với LangGraph Agent Chat:** Cho phép gửi yêu cầu kèm đoạn văn bản đang bôi đen (`selectedText`) vào cuộc hội thoại với Agent. |
| `apps/web/src/features/writing/components/WritingHeaderBar.tsx` | Component | **REFACTOR** | 1. **Xóa:** Nút `Share` (`onOpenShare`), nút `Comments` (`onToggleComments`), và nút `Overleaf` (`onSyncOverleaf`) trong menu công cụ.<br>2. **Bổ sung:** Nút **`[↩️ Hoàn tác (Undo)]`** hiển thị rõ ràng trên thanh công cụ khi có `previousSnapshot` sau thao tác chỉnh sửa của Agent (PRD `06` §4.1). |
| `apps/web/src/features/writing/components/WritingSidebar.tsx` | Component | **REFACTOR** | Hiện đang hardcode cây thư mục giả bằng `window.prompt`. Cần chuẩn hóa Cây thư mục Dự án (Cột 1) theo đúng **3 thành phần chuẩn** của PRD `06` §3:<br>1. `📄 main.tex` (tệp mã nguồn LaTeX chính)<br>2. `📚 references.bib` (tệp danh mục trích dẫn BibTeX)<br>3. `🖼️ Thư mục figures/` (danh sách các tệp ảnh/biểu đồ đã tải lên kèm nút tải lên và nút **`[🗑️ Xóa]`** gọi `DELETE /api/v1/drafts/{id}/assets/{asset_id}`). |
| `apps/web/src/features/writing/components/WritingEditorPane.tsx` | Component | **REFACTOR** | 1. **Thanh công cụ nổi khi bôi đen văn bản:** Xóa 2 nút `[Kiểm chứng]` (`onSelectionVerify`) và `[💬 Nhận xét]` (`onSelectionAddComment`); chỉ giữ lại nút **`[➕ Thêm vào Chat]`** (`onSelectionAddToChat`) để gửi đoạn mã LaTeX đang chọn làm ngữ cảnh cho LangGraph Agent.<br>2. **Chuyển đổi tab tệp tin:** Thay thế tab `sample.bib` giả lập (đang hardcode chuỗi tĩnh) bằng tab **`references.bib` thật** cho phép xem và chỉnh sửa trực tiếp `bibContent` (`draft.bib_content`). |
| `apps/web/src/features/writing/components/WritingAssistantPane.tsx` | Component | **REFACTOR TOÀN DIỆN** | Thay thế hoàn toàn giao diện kiểm tra SAFE Fact-Checking tĩnh hiện tại bằng **Khung Chat Đối Thoại LangGraph Agent** theo PRD `06` §3, §4, §5:<br>1. Tải và hiển thị lịch sử trò chuyện của bản thảo (`GET /api/v1/drafts/{id}/messages`).<br>2. Gửi tin nhắn yêu cầu Agent (`POST /api/v1/drafts/{id}/messages`) kèm đoạn văn bản được chọn (`selectedText`) hoặc ngữ cảnh phiên đọc/thư mục.<br>3. Hiển thị trực quan **Tiến trình Suy luận & Hành động của Agent (Agent Step Status)**:<br>   - `🔍 Đang tra cứu Kho GraphRAG & Ghi chú...`<br>   - `✍️ Đang cập nhật main.tex và references.bib...`<br>   - `⚙️ Đang biên dịch kiểm thử trên E2B Sandbox (Lần 1/3)...`<br>   - `✅ Biên dịch thành công — Đã làm mới bản xem trước PDF!`<br>4. Thêm nút **`[🔄 Làm mới đoạn chat]`** (`DELETE /api/v1/drafts/{id}/messages`) để xóa lịch sử hội thoại khi muốn bắt đầu chủ đề mới.<br>5. Thêm nút `ThumbsUp` / `ThumbsDown` trên phản hồi của Agent để chấm điểm Langfuse (`user_feedback`). |
| `apps/web/src/features/writing/components/DraftAssetManagementModal.tsx` | Modal | **REFACTOR** | Bổ sung nút **`[🗑️ Xóa]`** trên từng tệp hình ảnh/biểu đồ trong thư mục `figures/`, gọi API `DELETE /api/v1/drafts/{id}/assets/{asset_id}` (PRD `06` §5.3). |

---

### 3.5. Module 07: Giám Sát Hệ Thống, Xử Lý Lỗi & Langfuse (`components/ui/`)

| Đường dẫn File | Phân loại | Hành động | Chi tiết sai lệch & Yêu cầu xử lý theo PRD `07` |
| :--- | :--- | :---: | :--- |
| `apps/web/src/components/ui/DashboardErrorBoundary.tsx` | Component | **REFACTOR** | Theo PRD `07` §3.2, khi xảy ra lỗi từ hệ thống hoặc AI pipeline, thông báo lỗi hiển thị cho người dùng cần trích xuất `meta.trace_id` (hoặc `request_id`) và hiển thị kèm nút sao chép nhanh:<br>`⚠️ Đã xảy ra lỗi khi xử lý yêu cầu — Mã tra cứu: tr_8f92a1c4 [📋 Sao chép]` để phục vụ tra cứu vết lỗi tức thì trên Langfuse. |

---

## 4. Kiểm Toán Zustand Stores & Custom Hooks (`stores/` & `hooks/`)

### 4.1. Danh sách Zustand Stores cần REFACTOR

| Đường dẫn File | Hành động | Các State / Action cần XÓA | Các State / Action cần BỔ SUNG / SỬA |
| :--- | :---: | :--- | :--- |
| `apps/web/src/features/writing/stores/useWritingStore.ts` | **REFACTOR** | Xóa toàn bộ state/action của các tính năng bị cắt bỏ:<br>- **Sharing:** `isShareModalOpen`, `openShareModal`, `closeShareModal`<br>- **Comments:** `comments`, `activeCommentId`, `isCommentsPaneOpen`, `setComments`, `addComment`, `updateCommentInStore`, `removeCommentFromStore`, `setActiveCommentId`, `setCommentsPaneOpen`<br>- **SAFE Fact-Check:** `isVerifying`, `lastVerifyResult`, `selectedEvidenceClaim`, `isEvidenceModalOpen`, `openEvidenceModal`, `closeEvidenceModal`, `setVerifying`, `setVerifyResult`<br>- **Static Suggestion Panel:** `pendingSuggestion`, `isSuggestionPanelOpen`, `openSuggestionPanel`, `closeSuggestionPanel` | Bổ sung state phục vụ Agentic Overleaf (PRD `06`):<br>- `bibContent: string` & `setBibContent: (bib: string) => void`<br>- `activeFile: "main.tex" \| "references.bib"` & `setActiveFile`<br>- `previousSnapshot: { content: string; bibContent: string } \| null` & `saveSnapshot` / `undoLastAgentEdit` (phục vụ nút Hoàn tác 1 chạm)<br>- `messages: DraftMessage[]`, `agentStepStatus: string \| null` (phục vụ khung chat LangGraph Agent) |
| `apps/web/src/features/dashboard/stores/useDashboardStore.ts` | **REFACTOR** | - Xóa `"cowork"` và `"project"` khỏi kiểu `AppMode` (chỉ giữ chế độ đọc/chat chuẩn).<br>- Xóa `selectedModelId`, `setSelectedModelId` và hằng số `AVAILABLE_MODELS`.<br>- Xóa `coworkTasks`, `activeTaskIndex`, `isRunningTask` và các action điều khiển Cowork giả lập. | Giữ lại state quản lý phiên đọc hiện hành (`activeSessionId`), trạng thái đóng/mở các khung (`isSidebarCollapsed`, `isRightPaneOpen`), và danh sách tin nhắn phiên đọc. |
| `apps/web/src/features/reader/stores/useReaderStore.ts` | **REFACTOR** | Không có state thừa cần xóa. | **Sửa logic `addOpenDocument`:** Hiện tại khi `openDocumentIds.length >= 5`, hàm đang tự động xóa ngầm tab cũ nhất (`next.shift()`). Theo PRD `03` §3, khi phiên đọc đã chạm mốc **5 bài báo**, hệ thống **không được tự ý đuổi ngầm bài cũ** mà phải hiển thị thông báo rõ ràng yêu cầu người dùng gỡ bớt bài báo khỏi phiên đọc hoặc tạo phiên đọc mới. |

### 4.2. Danh sách Custom Hooks cần REFACTOR

| Đường dẫn File | Hành động | Chi tiết cần chỉnh sửa theo PRD MVP |
| :--- | :---: | :--- |
| `apps/web/src/features/library/hooks/useFolderQueries.ts` | **REFACTOR** | - **Xóa:** `useComparisonMatrixMutation` (gọi `foldersApi.generateComparisonMatrix`).<br>- **Giữ & Chuẩn hóa:** `useSynthesizeFolderMutation` (`POST /api/v1/folders/synthesis`) để trả về đầy đủ dữ liệu GraphRAG 4 thực thể + 4 quan hệ. |
| `apps/web/src/features/sessions/hooks/useSessionsQuery.ts` | **REFACTOR** | - **Xóa:** `useExportSessionBundleMutation` (gọi `exportSessionBundle`).<br>- **Bổ sung:**<br>  1. `useRemoveSessionDocumentMutation` (`DELETE /api/v1/sessions/{id}/documents/{document_id}` — PRD `03` §5 & PRD `04` §5).<br>  2. `useSessionMessageFeedbackMutation` (`POST /api/v1/sessions/{id}/messages/{message_id}/feedback` — PRD `07` §4 Tier 1.3). |
| `apps/web/src/features/dashboard/hooks/useDashboardQueries.ts` | **REFACTOR** | Xóa các đoạn fallback về dữ liệu giả lập `mockDashboardData.ts` / `COWORK_SAMPLE_TASKS`. |

---

## 5. Kiểm Toán Tầng Giao Tiếp API & Kiểu Dữ Liệu (`api/` & `types/`)

### 5.1. Danh sách Hàm Gọi API (API Client Functions) cần XÓA, HỢP NHẤT hoặc BỔ SUNG

| Đường dẫn File | Hàm cần XÓA (Tính năng đã cắt bỏ) | Hàm cần BỔ SUNG / CẬP NHẬT (Theo PRD MVP `01`–`07`) |
| :--- | :--- | :--- |
| `apps/web/src/features/writing/api/draftsApi.ts` | - `verifyFacts` (`POST /api/v1/drafts/{id}/verify-facts`)<br>- `exportToOverleaf` (`POST /api/v1/drafts/{id}:export-overleaf`)<br>- `getShareSettings` (`GET /api/v1/drafts/{id}/share`)<br>- `shareDraft` (`POST /api/v1/drafts/{id}/share`)<br>- `getComments` (`GET /api/v1/drafts/{id}/comments`)<br>- `createComment` (`POST /api/v1/drafts/{id}/comments`)<br>- `updateComment` (`PATCH /api/v1/drafts/{id}/comments/{cid}`)<br>- `deleteComment` (`DELETE /api/v1/drafts/{id}/comments/{cid}`)<br>- `getAssociativeSuggestions` (`GET /api/v1/drafts/{id}/associative-suggestions`) | - **Bổ sung API Chat với LangGraph Agent (PRD `06` §5.2):**<br>  + `listDraftMessages(draftId)` (`GET /api/v1/drafts/{id}/messages`)<br>  + `sendDraftMessage(draftId, payload)` (`POST /api/v1/drafts/{id}/messages` — hỗ trợ nhận tiến trình Agent & cập nhật `main.tex`, `references.bib`, PDF)<br>  + `clearDraftMessages(draftId)` (`DELETE /api/v1/drafts/{id}/messages`)<br>- **Bổ sung API xóa tệp ảnh (PRD `06` §5.3):**<br>  + `deleteAsset(draftId, assetId)` (`DELETE /api/v1/drafts/{id}/assets/{assetId}`) |
| `apps/web/src/features/library/api/foldersApi.ts` | - `generateComparisonMatrix` (`POST /api/v1/folders/comparison-matrix`) | - Cập nhật kiểu trả về của `synthesizeFolder` (`POST /api/v1/folders/synthesis`) bao gồm các nút thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) và cạnh quan hệ (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`) theo PRD `05` §3 & §5. |
| `apps/web/src/features/library/api/synthesisApi.ts` | - `generateComparisonMatrix` (`POST /api/v1/documents/comparison-matrix`)<br>- `generateFolderComparisonMatrix` (`POST /api/v1/folders/comparison-matrix`) | Có thể **XÓA FILE `synthesisApi.ts`** sau khi đã gom toàn bộ nghiệm vụ tổng hợp thư mục vào `foldersApi.synthesizeFolder`. |
| `apps/web/src/features/documents/api/documentsApi.ts` | - `exportAnnotatedPdf` (`GET /api/v1/documents/{id}/export-pdf`) | - **Bổ sung API Tìm kiếm Khám phá (PRD `02` §2A & §5):**<br>  + `searchAcademicPapers(query, filters)` (`POST /api/v1/discovery/search` hoặc `GET /api/v1/documents/search-external`) tích hợp Exa AI / Semantic Scholar / arXiv trả về `open_access_pdf_url` và trạng thái bài báo. |
| `apps/web/src/features/sessions/api/sessionsApi.ts` & `apps/web/src/features/dashboard/api/sessionsApi.ts` | - **Trùng lặp file:** Hiện đang có 2 file `sessionsApi.ts` ở 2 thư mục `features/sessions/api/` và `features/dashboard/api/`. Cần **hợp nhất làm 1 file duy nhất**.<br>- **Xóa hàm:**<br>  + `exportSessionBundle` (`POST /api/v1/sessions/{id}:export-bundle`)<br>  + `getCitationGraph` (`GET /api/v1/sessions/{id}/citation-graph`) | - **Bổ sung hàm:**<br>  + `removeDocumentFromSession(sessionId, documentId)` (`DELETE /api/v1/sessions/{id}/documents/{document_id}` — PRD `03` §5 & PRD `04` §5)<br>  + `submitMessageFeedback(sessionId, messageId, feedback)` (`POST /api/v1/sessions/{id}/messages/{message_id}/feedback` với `user_feedback: 1 \| 0` — PRD `07` §4 Tier 1.3) |
| `apps/web/src/lib/api-client.ts` | Không có hàm thừa. | - Cập nhật `ApiClientError` để lưu thêm trường `traceId?: string` trích xuất từ `envelope.meta?.trace_id` (PRD `07` §3.2) nhằm hiển thị trên `DashboardErrorBoundary`. |
| `apps/web/src/features/dashboard/data/mockDashboardData.ts` | **XÓA `COWORK_SAMPLE_TASKS`, `AVAILABLE_MODELS`, `MOCK_PROJECTS`** | Chỉ giữ lại hằng số cấu hình UI tĩnh nếu thật sự cần thiết, hoặc xóa toàn bộ file sau khi gỡ `DashboardCoworkView` và `ModelSelectorModal`. |

### 5.2. Danh sách File Kiểu Dữ Liệu (`types/`) cần REFACTOR

| Đường dẫn File | Các Interface / Type cần XÓA | Các Interface / Type cần BỔ SUNG |
| :--- | :--- | :--- |
| `apps/web/src/types/api.ts` | Không có. | Thêm `trace_id?: string` vào interface `ResponseMeta` (PRD `07` §3.2). |
| `apps/web/src/types/dashboard.ts` | - `CoworkTask`, `CoworkArtifact`, `ExecStep`, `ContextSource`<br>- `ModelOption`<br>- Xóa `"cowork" \| "project"` khỏi `AppMode` | Thêm kiểu `AcademicSearchResultItem` (chứa `title`, `authors`, `year`, `abstract`, `doi`, `arxiv_id`, `open_access_pdf_url`, `access_status: "open_access" \| "abstract_only"` — PRD `02` §2A). |
| `apps/web/src/features/writing/types/index.ts` | - `ClaimStatus`, `AtomicClaim`, `FactVerificationReport`, `VerifyFactsRequest`<br>- `PendingSuggestion`<br>- `OverleafExportResponse`<br>- `SharePermission`, `DraftShareRequest`, `DraftCollaborator`, `DraftShareResponse`<br>- `DraftComment`, `CreateDraftCommentRequest`, `UpdateDraftCommentRequest`<br>- `AssociativeSuggestionItem`, `AssociativeSuggestionsResponse`, `AssociativeMemorySuggestion` | - Thêm `bib_content?: string` vào `Draft`, `CreateDraftRequest`, `UpdateDraftRequest`.<br>- Thêm `DraftMessage`, `SendDraftMessageRequest`, `AgentStepEvent` (cho luồng LangGraph Agent — PRD `06` §4 & §5). |
| `apps/web/src/features/library/types/index.ts` | - `ComparisonMatrixRow`, `ComparisonMatrixResponse`, `ComparisonMatrixRequest` | Thêm `GraphEntityNode` (`type: "Paper" \| "Method" \| "Dataset" \| "MetricResult"`) và `GraphRelationEdge` (`type: "PROPOSES" \| "EVALUATED_ON" \| "ACHIEVES" \| "CITES"`) trong `FolderSynthesisResponse` (PRD `05` §3). |

---

## 6. Kiểm Toán Các File Kiểm Thử (`*.test.ts`, `*.test.tsx`)

### 6.1. Danh sách File Test cần XÓA (8 file test của các component đã bị cắt bỏ)

| STT | Đường dẫn File Test cần XÓA | Lý do |
| :-: | :--- | :--- |
| 1 | `apps/web/src/features/writing/components/__tests__/DraftSharingModal.test.tsx` | Test cho `DraftSharingModal.tsx` (tính năng chia sẻ đa người dùng & Overleaf đã bị xóa). |
| 2 | `apps/web/src/features/writing/components/__tests__/DraftCommentsPane.test.tsx` | Test cho `DraftCommentsPane.tsx` (tính năng bình luận nội tuyến đã bị xóa). |
| 3 | `apps/web/src/features/writing/components/__tests__/AssociativeMemoryCard.test.tsx` | Test cho `AssociativeMemoryCard.tsx` (tính năng gợi ý trí nhớ liên tưởng đã bị xóa). |
| 4 | `apps/web/src/features/writing/components/__tests__/SourceEvidenceModal.test.tsx` | Test cho `SourceEvidenceModal.tsx` (tính năng SAFE Fact-Checking tĩnh đã bị xóa). |
| 5 | `apps/web/src/features/writing/components/__tests__/SuggestionReviewPanel.test.tsx` | Test cho `SuggestionReviewPanel.tsx` (đã thay bằng cơ chế Agent cập nhật trực tiếp + Undo 1 chạm). |
| 6 | `apps/web/src/features/writing/components/__tests__/WritingIconRail.test.tsx` | Test cho `WritingIconRail.tsx` (thanh rail cũ không còn sử dụng). |
| 7 | `apps/web/src/features/library/components/__tests__/ComparisonMatrixModal.test.tsx` | Test cho `ComparisonMatrixModal.tsx` (tính năng Ma trận 100+ bài báo đã bị xóa). |
| 8 | `apps/web/src/features/dashboard/components/__tests__/DashboardCoworkView.test.tsx` | Test cho `DashboardCoworkView.tsx` (chế độ Cowork giả lập đã bị xóa). |

### 6.2. Danh sách File Test cần REFACTOR (Cập nhật theo hành vi MVP mới)

| Đường dẫn File Test | Nội dung cần cập nhật |
| :--- | :--- |
| `apps/web/src/features/writing/components/__tests__/WritingWorkspace.test.tsx` | Xóa các test case mở Share modal, Comments pane, SAFE verify facts, Overleaf sync; thêm test cho luồng LangGraph Agent cập nhật `main.tex` / `references.bib` và nút Hoàn tác `[↩️ Hoàn tác (Undo)]`. |
| `apps/web/src/features/writing/components/__tests__/WritingHeaderBar.test.tsx` | Xóa assert cho nút Share, Comments, Overleaf; thêm assert cho nút Undo. |
| `apps/web/src/features/writing/components/__tests__/WritingSidebar.test.tsx` | Cập nhật test kiểm tra cây thư mục 3 thành phần (`main.tex`, `references.bib`, `figures/`). |
| `apps/web/src/features/writing/components/__tests__/WritingEditorPane.test.tsx` | Xóa test cho nút `[Kiểm chứng]` và `[💬 Nhận xét]` khi bôi đen; thêm test chỉnh sửa tab `references.bib`. |
| `apps/web/src/features/writing/components/__tests__/WritingAssistantPane.test.tsx` | Viết lại test cho khung chat đối thoại LangGraph Agent, hiển thị trạng thái step, và nút `[🔄 Làm mới đoạn chat]`. |
| `apps/web/src/features/writing/components/__tests__/DraftAssetManagementModal.test.tsx` | Thêm test cho nút `[🗑️ Xóa]` tệp ảnh gọi `DELETE /api/v1/drafts/{id}/assets/{asset_id}`. |
| `apps/web/src/features/writing/api/__tests__/draftsApi.test.ts` | Xóa test của 9 hàm API đã cắt bỏ; thêm test cho `listDraftMessages`, `sendDraftMessage`, `clearDraftMessages`, `deleteAsset`. |
| `apps/web/src/features/writing/stores/__tests__/useWritingStore.test.ts` | Xóa test của các state Share/Comments/Verify/Suggestion; thêm test cho `bibContent`, `previousSnapshot` (Undo), và `messages`. |
| `apps/web/src/features/dashboard/components/__tests__/DashboardTaskbar.test.tsx` | Cập nhật test kiểm tra đúng **4 mục điều hướng toàn cục** thay vì 7 mục cũ. |
| `apps/web/src/features/dashboard/components/__tests__/DashboardWorkspace.test.tsx` | Xóa test xuất gói ZIP / xuất PDF; thêm test cho nút Cầu nối Đọc → Viết (`[✍️ Bắt đầu viết bài từ phiên đọc này]`). |
| `apps/web/src/features/dashboard/components/__tests__/DashboardChatStreamView.test.tsx` | Thêm test cho thẻ gợi ý Socratic Bridge (A → B → C → D) và sự kiện bấm `ThumbsUp` / `ThumbsDown` gửi `user_feedback`. |
| `apps/web/src/features/dashboard/components/__tests__/WorkspaceToolsMenu.test.tsx` | Xóa test cho 2 mục menu xuất ZIP và xuất PDF. |
| `apps/web/src/features/reader/components/__tests__/SmartReferenceDrawer.test.tsx` | Cập nhật test theo đúng Bảng Ngữ Cảnh Tài Liệu Tham Khảo 3 Cột (`Name`, `URL`, `Action`) và nút `[🗑️ Xóa khỏi chat]`. |
| `apps/web/src/features/reader/components/__tests__/ViewportOverflowMenu.test.tsx` & `ViewportControls.test.tsx` | Xóa test cho các tùy chọn xuất ZIP / PDF ngoại tuyến. |
| `apps/web/src/features/reader/stores/__tests__/useReaderStore.test.ts` | Cập nhật test giới hạn 5 bài báo/phiên đọc (hiển thị cảnh báo khi chạm trần 5 bài thay vì tự động xóa ngầm bài đầu tiên). |
| `apps/web/src/components/ui/__tests__/DashboardErrorBoundary.test.tsx` | Thêm test kiểm tra hiển thị `Mã tra cứu: tr_...` (`meta.trace_id`) và nút `[📋 Sao chép]`. |

---

## 7. Kiểm Toán Hệ Thống Tài Liệu Cũ Trong `./docs/` (Ngoài `./docs/PRD/`)

### 7.1. Danh sách các file tài liệu cũ cần XÓA HOÀN TOÀN (8 file mâu thuẫn trực tiếp với `./docs/PRD/`)

Toàn bộ thư mục `docs/02-modules-and-features/` và tài liệu Docker Enterprise cũ được viết cho kiến trúc 5-Pillar cũ, chứa đầy các tính năng đã bị cấm trong `docs/PRD/00-overview-and-cleanup.md` (Mục 5):

| STT | Đường dẫn File Docs cần XÓA | Lý do phải xóa (Đối chiếu `./docs/PRD/`) |
| :-: | :--- | :--- |
| 1 | `docs/02-modules-and-features/README.md` | Mục lục của kiến trúc "5-Pillar Product Specification" cũ; đã được thay thế hoàn toàn bởi bộ `./docs/PRD/00..07`. |
| 2 | `docs/02-modules-and-features/prd.md` | Bản PRD tổng hợp 5 trụ cột cũ (chứa Ma trận 100+ bài, SAFE Fact-Checker, Đồng bộ Git Overleaf, Air-gapped Docker); mâu thuẫn trực tiếp với `./docs/PRD/`. |
| 3 | `docs/02-modules-and-features/pillar-1-deep-reading.md` | Tài liệu Pillar 1 cũ (bao gồm xuất gói `.zip` ngoại tuyến và xuất PDF kèm ghi chú); đã được thay thế bởi `docs/PRD/02-discovery-and-upload.md` và `docs/PRD/03-reading-session.md`. |
| 4 | `docs/02-modules-and-features/pillar-2-latex-writing.md` | Tài liệu Pillar 2 cũ mô tả SAFE Fact-Verification NLI, 1-Click Overleaf Git Sync, và Inline Peer Comments; đã được thay thế hoàn toàn bởi `docs/PRD/06-agentic-overleaf-writing.md`. |
| 5 | `docs/02-modules-and-features/pillar-3-knowledge-capital.md` | Tài liệu Pillar 3 cũ mô tả Proactive Associative Memory Card và đồ thị trích dẫn 2-hop SVG; đã được thay thế bởi `docs/PRD/04-citation-and-reference-bridge.md` và `docs/PRD/05-favorite-library-and-graphrag.md`. |
| 6 | `docs/02-modules-and-features/pillar-4-literature-matrix.md` | Tài liệu Pillar 4 chuyên biệt cho tính năng **100+ Paper Comparison Matrix** — tính năng đã bị xóa bỏ hoàn toàn trong PRD `00` §5 & PRD `05` §2. |
| 7 | `docs/02-modules-and-features/pillar-5-enterprise-stack.md` | Tài liệu Pillar 5 mô tả kiến trúc On-Premise Air-Gapped Docker Enterprise Stack — đã bị loại bỏ trong PRD `00` §5 (MVP sử dụng Supabase + Upstash + E2B Cloud). |
| 8 | `docs/04-operations-and-cicd/docker-enterprise-guide.md` | Hướng dẫn vận hành cụm Docker On-Premise локал (với `verischolar-sandbox-broker` cục bộ, MinIO/Postgres/Neo4j/Redis tự host); mâu thuẫn với hạ tầng Cloud-Native MVP trong PRD `00` §5. |

### 7.2. Danh sách các file tài liệu trong `./docs/` cần REFACTOR / CẬP NHẬT (19 file)

| Đường dẫn File Docs | Hành động | Nội dung cụ thể cần chỉnh sửa để đồng bộ với `./docs/PRD/` |
| :--- | :---: | :--- |
| `docs/README.md` | **REFACTOR** | Cập nhật **Master Navigation Index**: Đưa `./docs/PRD/` (`00-overview-and-cleanup.md` đến `07-monitoring-and-langfuse.md`) lên làm **Nguồn Chân Lý Duy Nhất (Single Source of Truth)** cho đặc tả sản phẩm & kỹ thuật; xóa toàn bộ liên kết trỏ tới thư mục `02-modules-and-features/` (5-Pillar cũ) và `docker-enterprise-guide.md`. |
| `docs/01-architecture/README.md` | **REFACTOR** | Cập nhật tóm tắt kiến trúc theo mô hình Cloud-Native MVP (Supabase PostgreSQL + pgvector, Neo4j AuraDB 4-Entity GraphRAG, Upstash Redis/Celery, E2B Firecracker Sandbox, Langfuse Cloud). |
| `docs/01-architecture/architecture-overview.md` | **REFACTOR** | Xóa các sơ đồ/mô tả về `verischolar-sandbox-broker` cục bộ, SAFE NLI Fact-Checker, 100+ Paper Matrix, và Overleaf Git Bridge; thay bằng luồng **LangGraph Agent + E2B Firecracker Sandbox** (PRD `06`) và **4-Entity GraphRAG** (PRD `05`). |
| `docs/01-architecture/backend-techstack.md` | **REFACTOR** | Xóa tham chiếu tới mô hình local ONNX NLI (`DeBERTa-v3` cho SAFE Fact-Check) và local gVisor Docker Sandbox; cập nhật E2B SDK, LangGraph, Exa AI SDK, và Langfuse SDK v3. |
| `docs/01-architecture/database-design.md` | **REFACTOR** | - **Xóa các bảng đã bị cắt bỏ:** `shares` (chia sẻ bản thảo), `draft_comments` (bình luận phản biện), `draft_verifications` (kết quả SAFE Fact-Check), `citation_edges` (đồ thị trích dẫn 2-hop).<br>- **Cập nhật bảng `drafts`:** Thêm cột `bib_content TEXT` (`references.bib`), `session_id UUID` (liên kết phiên đọc).<br>- **Bổ sung bảng `draft_messages`:** Lưu lịch sử hội thoại với LangGraph Agent trong không gian viết bài (PRD `06` §5.2).<br>- **Cập nhật Neo4j Schema:** Chuẩn hóa đúng 4 nhãn thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) và 4 kiểu cạnh (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`) theo PRD `05` §3. |
| `docs/01-architecture/api-specification.md` | **REFACTOR** | - **Xóa 12+ endpoint đã bị cắt bỏ:** `POST /drafts/{id}:export-overleaf`, `GET/POST /drafts/{id}/share`, `GET/POST/PATCH/DELETE /drafts/{id}/comments`, `POST /drafts/{id}/verify-facts`, `GET /drafts/{id}/associative-suggestions`, `POST /folders/comparison-matrix`, `POST /documents/comparison-matrix`, `POST /sessions/{id}:export-bundle`, `GET /documents/{id}/export-pdf`, `GET /sessions/{id}/citation-graph`.<br>- **Bổ sung các endpoint MVP mới:** `POST /discovery/search`, `DELETE /sessions/{id}/documents/{doc_id}`, `POST /sessions/{id}/messages/{msg_id}/feedback`, `GET/POST/DELETE /drafts/{id}/messages`, `DELETE /drafts/{id}/assets/{asset_id}`.<br>- Bổ sung trường `meta.trace_id` trong chuẩn phong bì phản hồi (Response Envelope — PRD `07` §3.2). |
| `docs/01-architecture/ai-guardrails-and-rag.md` | **REFACTOR** | Xóa phần SAFE Atomic Claim Decomposition & NLI Verification tĩnh và 100+ Paper Matrix Map-Reduce; cập nhật theo kiến trúc Hybrid RAG (Dense + BM25 + Cross-Encoder Rerank), 4-Entity GraphRAG (PRD `05`), và vòng lặp tự sửa lỗi biên dịch tối đa 3 lần của LangGraph Agent trên E2B (PRD `06`). |
| `docs/01-architecture/prompt-management.md` | **REFACTOR** | Đồng bộ danh mục Prompt trên Langfuse với PRD `07` §4 (Socratic Reading RAG, Socratic Citation Bridge Hint, 4-Entity GraphRAG Extraction & Synthesis, LangGraph LaTeX Co-Author Agent, LLM-as-a-Judge Faithfulness/Relevance). Xóa prompt của SAFE Fact-Check và Comparison Matrix. |
| `docs/01-architecture/scholar-profile-and-identity.md` | **REFACTOR** | Xóa phần cấu hình liên kết tài khoản Overleaf Git Token; giữ lại chuẩn hồ sơ học giả, quản lý phiên đăng nhập, và khóa BYOK mã hóa AES-256-GCM (PRD `01`). |
| `docs/01-architecture/directory-structure.md` | **REFACTOR** | Cập nhật cây thư mục tổng thể của Monorepo sau khi dọn dẹp các module dư thừa. |
| `docs/01-architecture/swagger-offline.md` | **REFACTOR** | Cập nhật tài liệu đặc tả OpenAPI offline khớp với danh sách endpoint của `api-specification.md` sau khi dọn dẹp. |
| `docs/03-frontend-engineering/README.md` | **REFACTOR** | Cập nhật tổng quan kiến trúc Frontend theo 4 khu vực điều hướng chính của PRD `00` §4. |
| `docs/03-frontend-engineering/frontend-architecture-and-standards.md` | **REFACTOR** | Xóa các ví dụ và mô tả về `ComparisonMatrixModal`, `ExportBundleDialog`, `DraftSharingModal`, `DraftCommentsPane`, `SourceEvidenceModal`; cập nhật luồng trạng thái của Agentic Overleaf (`useWritingStore`) và Reading Session. |
| `docs/03-frontend-engineering/directory-structure.md` | **REFACTOR** | Cập nhật sơ đồ cây thư mục `apps/web/src/` phản ánh đúng các file giữ lại sau khi xóa 15 component/modal dư thừa. |
| `docs/03-frontend-engineering/academic-luxury-design-system.md` | **GIỮ / CẬP NHẬT NHẸ** | Đảm bảo hệ màu Light/Dark Mode và typography khớp với thanh điều hướng 4 mục mới. |
| `docs/04-operations-and-cicd/README.md`, `ci-quality-gates-guide.md`, `cd-and-production-operations.md`, `logging-and-observability.md` | **REFACTOR** | Xóa liên kết tới `docker-enterprise-guide.md`; cập nhật `logging-and-observability.md` để tích hợp đầy đủ chiến lược **Langfuse 3-Tier Observability & Evaluation** (`trace_id` propagation, `user_feedback`, LLM-as-a-Judge, E2B Sandbox metrics) theo `docs/PRD/07-monitoring-and-langfuse.md`. |
| `docs/05-testing-and-qa/README.md`, `testing-strategy.md`, `quality-gates-certification.md`, `api-eval-snapshots.md` | **REFACTOR** | Xóa các mục kiểm thử `ComparisonMatrixModal.test.tsx (120 papers)`, `DraftSharingModal.test.tsx`, và bước E2E `"1-Click Overleaf Export"`; cập nhật kịch bản E2E mới cho **Zero-to-Reading → Socratic Citation Ingest → Reading-to-Writing Bridge → LangGraph Agent E2B Compile**. |

---

## 8. Bảng Tổng Hợp Định Lượng Kết Quả Kiểm Toán (Audit Metrics Summary)

| Hạng mục kiểm toán | Số lượng cần XÓA (DELETE) | Số lượng cần REFACTOR / CẬP NHẬT | Số lượng API / Tính năng cần BỔ SUNG |
| :--- | :---: | :---: | :---: |
| **Routes (`routes.tsx`)** | **4 routes** (`/matrix`, `/library/matrix`, `/projects`, `/notes`, `/citations`) | **1 file** (`apps/web/src/app/routes.tsx`) | — |
| **Pages & Components & Modals (`apps/web/src/`)** | **15 files** (`ComparisonMatrixPage`, `ComparisonMatrixModal`, `ProjectsPage`, `NotesPage`, `DashboardCoworkView`, `DashboardProjectView`, `ModelSelectorModal`, `QuickUploadDocModal`, `ExportBundleDialog`, `DraftSharingModal`, `DraftCommentsPane`, `AssociativeMemoryCard`, `SourceEvidenceModal`, `SuggestionReviewPanel`, `WritingIconRail`) + **2 mock files** (`mock-auth.ts`, `mock-users.ts`) | **18 files** (`DashboardTaskbar`, `AccountSettingsModal`, `DashboardContainer`, `DashboardHeroSection`, `DiscoveryPage`, `DashboardWorkspace`, `DashboardChatStreamView`, `SmartReferenceDrawer`, `ReferenceListModal`, `DocumentTabBar`, `WorkspaceToolsMenu`, `ViewportOverflowMenu`, `LibraryWorkspaceView`, `DocumentLibraryModal`, `WritingWorkspace`, `WritingHeaderBar`, `WritingSidebar`, `WritingEditorPane`, `WritingAssistantPane`, `DraftAssetManagementModal`, `DashboardErrorBoundary`) | **6 luồng giao diện MVP:**<br>1. Zero-to-Reading Topic Search (`[📖 Mở đọc ngay]`)<br>2. Socratic Bridge Hint Card (A→B→C→D)<br>3. Bảng Tham khảo 3 cột + Xóa bài khỏi phiên<br>4. Cầu nối Đọc → Viết (`[✍️ Bắt đầu viết bài...]`)<br>5. Khung Chat LangGraph Agent + `references.bib` + Undo 1 chạm<br>6. Chấm điểm `ThumbsUp`/`ThumbsDown` & `trace_id` |
| **Zustand Stores & Hooks** | **0 files** (xóa các state/hook con bên trong) | **6 files** (`useWritingStore.ts`, `useDashboardStore.ts`, `useReaderStore.ts`, `useFolderQueries.ts`, `useSessionsQuery.ts`, `useDashboardQueries.ts`) | **2 mutations mới** (`useRemoveSessionDocumentMutation`, `useSessionMessageFeedbackMutation`) |
| **API Clients & Types** | **15 hàm API** bị cắt bỏ + **1 file API trùng lặp** (`dashboard/api/sessionsApi.ts`) | **8 files** (`draftsApi.ts`, `foldersApi.ts`, `documentsApi.ts`, `sessionsApi.ts`, `api-client.ts`, `api.ts`, `dashboard.ts`, `writing/types/index.ts`, `library/types/index.ts`) | **7 hàm API mới** (`searchAcademicPapers`, `removeDocumentFromSession`, `submitMessageFeedback`, `listDraftMessages`, `sendDraftMessage`, `clearDraftMessages`, `deleteAsset`) |
| **Unit / Component Test Files (`__tests__/`)** | **8 files test** của các component đã bị xóa | **16 files test** cần cập nhật theo hành vi MVP | — |
| **Hệ thống Tài liệu (`./docs/` ngoài `./docs/PRD/`)** | **8 files docs** (`docs/02-modules-and-features/*` [7 files] + `docs/04-operations-and-cicd/docker-enterprise-guide.md`) | **22 files docs** trong `docs/README.md`, `01-architecture/`, `03-frontend-engineering/`, `04-operations-and-cicd/`, `05-testing-and-qa/` | — |
