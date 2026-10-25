# 🔍 Báo Cáo Kiểm Toán Kỹ Thuật (Read-Only Audit) — Member 2
**Phụ trách:** Backend (`apps/api/`), Core (`packages/core/`), Scripts (`scripts/`), Tests (`tests/`, `apps/api/tests/`, `packages/core/tests/`), Deploy (`deploy/`, `infra/`) & Root Files (`.env*`, `models/`, `docs/`, `temp/`, `pyproject.toml`)  
**Đối chiếu chuẩn:** Bộ tài liệu PRD MVP chính thức tại `./docs/PRD/00-overview-and-cleanup.md` đến `./docs/PRD/07-monitoring-and-langfuse.md`  
**Trạng thái kiểm toán:** **READ-ONLY AUDIT** (Tuyệt đối chưa xóa hoặc sửa bất kỳ dòng code nào)

---

## 1. Tổng Quan Kết Quả Rà Soát (Executive Summary)

Qua quá trình rà soát toàn diện mã nguồn hiện tại so với bộ đặc tả PRD MVP (`00` $\rightarrow$ `07`), hệ thống Backend & Core đang tồn tại **khối lượng lớn tính năng ngoài phạm vi MVP (Out-of-Scope Bloat)** từ thiết kế "5 Pillars / Enterprise" cũ, đồng thời còn **thiếu một số thành phần cốt lõi** của kiến trúc MVP mới:

| Nhóm Thành Phần | Số Lượng Cần XÓA (DELETE) | Số Lượng Cần SỬA (MODIFY) | Số Lượng Cần THÊM MỚI (ADD) |
| :--- | :---: | :---: | :---: |
| **Root Files, `.env*`, `models/`, `docs/` cũ, `temp/`** | **21** file / thư mục | **6** file cấu hình | **0** |
| **API Endpoints (`apps/api/src/api/`)** | **15** endpoints | **10** endpoints | **9** endpoints mới |
| **DB Models & Tables (`apps/api/src/api/db/`)** | **3** bảng / ORM models | **4** bảng / ORM models | **4** bảng / ORM models mới |
| **Schemas, Services, Adapters, Workers (`apps/api/`)** | **5** file + **18** classes/methods | **9** file | **3** services mới |
| **Domain, Ports, Services, Eval (`packages/core/`)** | **31** file (gồm NLI, PDF Annotator, Eval, MCP) | **6** file | **2** modules mới (LangGraph Agent, GraphRAG) |
| **Deploy & Infra (`deploy/`, `infra/`)** | **4** file Enterprise/PgBouncer | **4** file | **0** |
| **Scripts (`scripts/`)** | **13** scripts | **4** scripts | **0** |
| **Tests (`apps/api/tests`, `packages/core/tests`, `tests`)** | **26** file test | **9** file test | **5** bộ test MVP mới |

---

## 2. Rà Soát Thư Mục Gốc (Root), `.env*`, `models/`, `docs/` & `temp/`

### 2.1. Tập tin Môi trường (`.env*`) — *Đối chiếu PRD 00 §5.1 & PRD 07 §2*
PRD quy định rõ: **Chỉ duy trì duy nhất 2 môi trường chuẩn là `development` và `production`** (cùng chế độ `test` nội bộ khi chạy Pytest). Xóa bỏ hoàn toàn `uat`, `staging`, `enterprise`.

| Trạng Thái | Đường Dẫn File | Lý Do & Chi Tiết Xử Lý |
| :---: | :--- | :--- |
| 🔴 **XÓA** | `apps/api/.env.uat` | Chứa `ENVIRONMENT=uat` và `LANGFUSE_ENVIRONMENT=uat`. Trái với PRD 00 §5.1 & PRD 07 §2. |
| 🔴 **XÓA** | `deploy/.env.enterprise.example` | File mẫu cho kiến trúc Enterprise Pillar 5 cũ (`REDIS_URL`, `PgBouncer`), không nằm trong MVP. |
| 🟡 **SỬA** | `.env` & `.env.example` | Chuẩn hóa theo PRD 07 §2: loại bỏ biến thừa (`DMR_BASE_URL`, `DMR_MODEL`, `AZURE_DOCUMENT_INTELLIGENCE_*` nếu không dùng), cập nhật `OPENAI_MODEL=gpt-5.4-mini`, `LANGFUSE_ENVIRONMENT=verischolar-dev`, `LANGFUSE_MASK_INPUT_OUTPUT=false`, bổ sung `EXA_API_KEY`, `SENTRY_DSN`, `ALERT_WEBHOOK_URL`, `E2B_LATEX_TEMPLATE=base`. |
| 🟡 **SỬA** | `apps/api/.env.development` | Đổi `OPENAI_MODEL=gpt-5.6-luna` $\rightarrow$ `gpt-5.4-mini`, thêm `LANGFUSE_ENVIRONMENT=verischolar-dev`, `SENTRY_DSN=`, `ALERT_WEBHOOK_URL=`. *(Lưu ý bảo mật: Cần gỡ các live API key đang hardcode trong file tracked nếu commit lên git).* |
| 🟡 **SỬA** | `apps/api/.env.production` | Đổi `OPENAI_MODEL=gpt-5.6-luna` $\rightarrow$ `gpt-5.4-mini`; đổi `LANGFUSE_ENVIRONMENT=production` $\rightarrow$ `verischolar-prod`; đổi `LANGFUSE_MASK_INPUT_OUTPUT=true` $\rightarrow$ `false` (PRD 07 §2 quy định tắt mask cho cả dev & prod vì dữ liệu là bài báo học thuật, chỉ scrub PII/API keys qua `scrub_sensitive_text`); bổ sung `E2B_API_KEY`, `SENTRY_DSN`, `ALERT_WEBHOOK_URL`. |
| 🟡 **SỬA** | `apps/api/.env.example` | Đồng bộ danh sách biến chuẩn với `.env.example` gốc, bỏ comment `(development \| staging \| production \| test)` $\rightarrow$ `(development \| production)`. |

### 2.2. Trọng số Mô hình Offline (`models/`) & Dependencies (`pyproject.toml`)
| Trạng Thái | Đường Dẫn File / Thư Mục | Lý Do & Chi Tiết Xử Lý |
| :---: | :--- | :--- |
| 🔴 **XÓA** | `models/nli/cross-encoder-nli-deberta-v3-small/` (`model.onnx` ~530MB, `tokenizer.json`, `config.json`, ...) | Mô hình DeBERTa-v3 ONNX **chỉ được gọi duy nhất** bởi `safe_nli_adapter.py` để phục vụ tính năng SAFE Fact-Checking (`/drafts/{id}/verify-facts`). Theo PRD 00 §5.5, tính năng SAFE Fact-Checking đã bị xóa bỏ hoàn toàn. |
| 🔴 **XÓA** | `models/README.md` & thư mục `models/` | Tài liệu hướng dẫn tải model ONNX DeBERTa cho SAFE Fact-Checking. |
| 🟡 **SỬA** | `pyproject.toml` (Root) | Gỡ bỏ các thư viện không còn dùng trong MVP: `onnxruntime>=1.31.0`, `arq>=0.26.0`, `jinja2>=3.1.6` (nếu xóa `.prompt.md` template). Bổ sung `langgraph`, `langchain-openai` (hoặc SDK phục vụ LangGraph Agent ở Module 5 - PRD 06) và `sentry-sdk[fastapi]` (nếu dùng SDK hoặc giữ HTTP/structlog hook theo PRD 07). |
| 🟡 **SỬA** | `packages/core/pyproject.toml` | Gỡ bỏ `onnxruntime>=1.31.0`, `mcp>=2.3.0`, `jinja2>=3.1.6`. |

### 2.3. Tài liệu Cũ (`docs/`) & File Rác Thư Mục Gốc (Root Junk Files)
| Trạng Thái | Đường Dẫn File / Thư Mục | Lý Do & Chi Tiết Xử Lý |
| :---: | :--- | :--- |
| 🔴 **XÓA** | `docs/02-modules-and-features/pillar-1-deep-reading.md` | **PRD 00 §5.8 yêu cầu xóa đích danh.** |
| 🔴 **XÓA** | `docs/02-modules-and-features/pillar-2-collaborative-writing.md` | **PRD 00 §5.8 yêu cầu xóa đích danh.** |
| 🔴 **XÓA** | `docs/02-modules-and-features/pillar-3-knowledge-digest.md` | **PRD 00 §5.8 yêu cầu xóa đích danh.** |
| 🔴 **XÓA** | `docs/02-modules-and-features/pillar-4-library-synthesis.md` | **PRD 00 §5.8 yêu cầu xóa đích danh.** |
| 🔴 **XÓA** | `docs/02-modules-and-features/pillar-5-enterprise-stack.md` | **PRD 00 §5.8 yêu cầu xóa đích danh.** |
| 🔴 **XÓA** | `docs/02-modules-and-features/prd.md` | Bản PRD tổng hợp của 5 Pillars cũ, mâu thuẫn trực tiếp với `./docs/PRD/00..07`. |
| 🔴 **XÓA** | `AUDIT_CERTIFICATION_REPORT_FULL_SYSTEM.md` | Báo cáo audit cũ ở thư mục gốc. |
| 🔴 **XÓA** | `QUALITY_GATE_CERTIFICATION_4BUGS_PASS.md` | Báo cáo quality gate cũ ở thư mục gốc. |
| 🔴 **XÓA** | `QUALITY_GATE_FE_BE_TASKS_PASS.md` | Báo cáo quality gate cũ ở thư mục gốc. |
| 🔴 **XÓA** | `QUALITY_GATE_READER_OVERFLOW_PASS.md` | Báo cáo quality gate cũ ở thư mục gốc. |
| 🔴 **XÓA** | `QUALITY_GATE_RESPONSIVE_DEVICE_MATRIX_PASS.md` | Báo cáo quality gate cũ ở thư mục gốc. |
| 🔴 **XÓA** | `QUALITY_GATE_SCHOLAR_PROFILE_AUDIT.md` | Báo cáo quality gate cũ ở thư mục gốc. |
| 🔴 **XÓA** | `QUALITY_GATE_TEST_HARDENING_AUDIT.md` | Báo cáo quality gate cũ ở thư mục gốc. |
| 🔴 **XÓA** | `verischolar_runtime_data.tar.gz` & `verischolar_runtime_data.tar.gz.sha256` | File nén dữ liệu runtime đóng gói thừa tại thư mục gốc. |
| 🔴 **XÓA** | `.coverage` & `test-results.xml` | Artifacts sinh ra từ lần chạy test trước nằm ở root. |
| 🔴 **XÓA** | `temp/` (`temp/output/test/*.md`, `temp/audit_26_apis.py`, `temp/test_all_26_apis.py`) | Thư mục chứa file script nháp và log báo cáo test tạm thời (bao gồm cả báo cáo `get_documents_export_pdf.md`). |
| 🟡 **RÀ SOÁT** | `docs/01-architecture/`, `docs/03-Testing/`, `docs/04-operations/`, `docs/vi/` | Nhiều tài liệu trong các thư mục này vẫn mô tả 5 Pillars, SAFE DeBERTa, Export Annotated PDF và UAT. Cần cập nhật hoặc dọn dẹp để `./docs/PRD/` là Single Source of Truth duy nhất (PRD 00 §5.8). |

---

## 3. Rà Soát Chi Tiết `apps/api/` (Backend FastAPI)

### 3.1. Danh Sách API Endpoints Cần XÓA BỎ (DELETE)
Dưới đây là toàn bộ **15 API endpoints** hiện có trong code nhưng **bị loại bỏ theo PRD 00 §5.2 – §5.7**:

| STT | HTTP Method & Path | File & Vị Trí Dòng Code | Đối Chiếu PRD & Lý Do Xóa |
| :---: | :--- | :--- | :--- |
| **1** | `POST /api/v1/drafts/{id}/verify-facts` | `apps/api/src/api/v1/endpoints/drafts.py` (L407–481) | **PRD 00 §5.5**: Xóa bỏ hoàn toàn hệ thống SAFE Fact-Checking độc lập (tách câu + NLI DeBERTa). Thay bằng trò chuyện trực tiếp với LangGraph Agent ở Cột 3. |
| **2** | `POST /api/v1/drafts/{id}/share` | `apps/api/src/api/v1/endpoints/drafts.py` (L878–916) | **PRD 00 §5.2**: Xóa tính năng chia sẻ bản thảo đa người dùng (Multi-user Sharing). |
| **3** | `GET /api/v1/drafts/{id}/share` | `apps/api/src/api/v1/endpoints/drafts.py` (L919–952) | **PRD 00 §5.2**: Xóa tính năng lấy danh sách quyền chia sẻ bản thảo. |
| **4** | `POST /api/v1/drafts/{id}/comments` | `apps/api/src/api/v1/endpoints/drafts.py` (L960–1014) | **PRD 00 §5.2**: Xóa tính năng bình luận phản biện (Peer-review Comments). |
| **5** | `GET /api/v1/drafts/{id}/comments` | `apps/api/src/api/v1/endpoints/drafts.py` (L1017–1053) | **PRD 00 §5.2**: Xóa tính năng liệt kê bình luận bản thảo. |
| **6** | `PATCH /api/v1/drafts/{id}/comments/{comment_id}` | `apps/api/src/api/v1/endpoints/drafts.py` (L1056–1105) | **PRD 00 §5.2**: Xóa tính năng cập nhật/resolve bình luận bản thảo. |
| **7** | `DELETE /api/v1/drafts/{id}/comments/{comment_id}` | `apps/api/src/api/v1/endpoints/drafts.py` (L1108–1145) | **PRD 00 §5.2**: Xóa tính năng xóa bình luận bản thảo. |
| **8** | `POST /api/v1/drafts/{id}:export-overleaf` | `apps/api/src/api/v1/endpoints/drafts.py` (L1148–1160) | **PRD 00 §5.3**: Xóa tính năng xuất gói sang Overleaf.com bên ngoài (VeriScholar tự cung cấp trình soạn thảo + E2B/Tectonic nội bộ và nút tải `.zip` cục bộ). |
| **9** | `POST /api/v1/drafts/{id}/overleaf` | `apps/api/src/api/v1/endpoints/drafts.py` (L1163–1173) | **PRD 00 §5.3**: Alias của `:export-overleaf`, cần xóa bỏ. |
| **10** | `GET /api/v1/drafts/{id}/overleaf-launch` | `apps/api/src/api/v1/endpoints/drafts.py` (L1176–1187) | **PRD 00 §5.3**: Trang HTML auto-submit form sang `overleaf.com/docs`, cần xóa bỏ. |
| **11** | `POST /api/v1/drafts/{id}/associative-suggestions` | `apps/api/src/api/v1/endpoints/drafts.py` (L1190–1213) | **PRD 00 §5.4**: Xóa bỏ hoàn toàn tính năng Gợi ý Liên tưởng Tự động (Proactive Associative Memory). Thay bằng tool `query_library_graph_rag` của LangGraph Agent. |
| **12** | `POST /api/v1/folders/comparison-matrix` | `apps/api/src/api/v1/endpoints/folders.py` (L116–144) | **PRD 00 §5.6**: Xóa bỏ API tạo Bảng Ma trận Đối chiếu Cứng (Hardcoded Comparison Matrix). |
| **13** | `POST /api/v1/folders/{folder_id}/comparison-matrix` | `apps/api/src/api/v1/endpoints/folders.py` (L313–341) | **PRD 00 §5.6**: Alias theo thư mục của Comparison Matrix, cần xóa bỏ. |
| **14** | `GET & HEAD /api/v1/documents/{document_id}/export-pdf` | `apps/api/src/api/v1/endpoints/documents.py` (L1144–1205) | **PRD 00 §5.7**: Xóa bỏ tính năng kết xuất PDF có nhúng Highlight (Export Annotated PDF). |
| **15** | `POST /api/v1/sessions/{id}:export-bundle` | `apps/api/src/api/v1/endpoints/sessions.py` (L871–899) | **PRD 00 §5.7**: Xóa bỏ tính năng đóng gói ZIP phiên đọc sâu (`export-bundle`). |

> **Các Endpoint ngoài PRD cần XÓA thêm để làm sạch API Surface:**
> - **16.** `POST /api/v1/notes:synthesize` (`apps/api/src/api/v1/endpoints/notes.py` L550–613): Thuộc tính năng Pillar 3 cũ (AI Note Synthesis / Active Recall Flashcards Quiz). Trong **PRD 03 §6**, Sổ tay Nghiên cứu chỉ bao gồm 5 API CRUD chuẩn (`POST /notes`, `GET /notes`, `GET /notes/{id}`, `PATCH /notes/{id}`, `DELETE /notes/{id}`).
> - **17.** `GET /api/v1/sessions/{id}/citation-graph` (`apps/api/src/api/v1/endpoints/sessions.py` L946–975): Đồ thị trích dẫn theo phiên kiểu cũ (`CITES, EXTENDS, BENCHMARKS_ON` trên bảng `citation_edges`). Không có trong PRD 03 hay PRD 04; đồ thị tri thức trong MVP được chuẩn hóa thành **GraphRAG 4 Thực thể Cố định** tại Thư viện Yêu thích (PRD 05 §3).
> - **18.** `GET /events` (`apps/api/src/api/__init__.py` L396–406): Endpoint `demo_sse_events` trả dữ liệu giả lập `chunk 0, 1, 2`, không thuộc PRD.

---

### 3.2. Danh Sách API Endpoints Cần CHỈNH SỬA (MODIFY) & BỔ SUNG MỚI (ADD)

#### A. Nhóm Hệ Thống & Giám Sát (`apps/api/src/api/__init__.py`) — *PRD 07 §4 Tầng 3*
- 🟡 **SỬA `GET /health/ready`** (`__init__.py` L314–393):
  - Bổ sung kiểm tra dung lượng ổ cứng lưu trữ PDF (`storage` directory size MB / free space).
  - Bổ sung trạng thái cấu hình các dịch vụ tích hợp ngoài (External Services Configuration Check): `openai`, `exa`, `e2b`, `langfuse`, `sentry` (`configured` vs `missing`).
- 🟢 **THÊM MỚI `GET /api/v1/system/status`** (PRD 07 §4 Tầng 3.2):
  - Trả về bức tranh tổng quan vận hành hệ thống: `uptime_seconds`, tổng số request, tỷ lệ phản hồi thành công/lỗi (`2xx`, `4xx`, `5xx`), độ trễ trung bình (`avg_duration_ms`), thời gian phản hồi token đầu tiên trung bình (`avg_ttfb_ms`), và danh sách **20 lỗi gần nhất (Recent Errors)** gồm `timestamp`, `trace_id`, `path`, `status_code`, `error_message`.

#### B. Nhóm Auth (`apps/api/src/api/v1/endpoints/auth.py`) — *PRD 01*
- 🟡 **SỬA `auth.py` (L60)**:
  - Đổi `is_dev_or_uat = settings.ENVIRONMENT in ("development", "uat", "test")` $\rightarrow$ bỏ `"uat"` (chỉ giữ `"development"`, `"test"`).

#### C. Nhóm Khám Phá & Tài Liệu (`apps/api/src/api/v1/endpoints/documents.py`) — *PRD 02, PRD 04, PRD 05*
- 🟢 **THÊM MỚI Endpoint Khám Phá Bài Báo theo Chủ đề (Topic Search)** (PRD 02 §2.1):
  - Ví dụ: `POST /api/v1/documents:discover` hoặc `GET /api/v1/discovery/search`: Kết hợp **Exa AI Neural Search + Semantic Scholar / arXiv API** trả về danh sách bài báo sát nghĩa kèm liên kết PDF Open-Access và nút **"Đọc ngay" (1-Click Open to Session)**.
- 🟡 **SỬA `GET /api/v1/documents` (`list_documents` tại `documents.py` L214–325 & `document_service.py` L320–426)**:
  - **PRD 02 §3.B.1** yêu cầu hỗ trợ lọc theo `folder_id` (ngoài `is_starred`/`star` và `search`). Hiện tại `list_documents` đang thiếu query param `folder_id: UUID | None = Query(None)`.
- 🟡 **SỬA `POST /api/v1/documents/{document_id}:star` & `:toggle-star` (`documents.py` L525–627 & `document_service.py` L837–938)**:
  - **PRD 05 §2.A** quy định: Khi bài báo được gắn sao (`is_starred = True`), hệ thống kích hoạt tiến trình ngầm (Background Task) trích xuất **GraphRAG 4 thực thể cố định (`Paper`, `Method`, `Dataset`, `MetricResult`)**. Khi bỏ gắn sao và không thuộc thư mục nào (`is_starred = False` và `folder_id = NULL`), gỡ bỏ các đỉnh/cạnh thuộc riêng bài báo đó khỏi Đồ thị Tri thức.
- 🟢 **THÊM MỚI `GET /api/v1/documents/{document_id}/references`** (PRD 04 §3.A.1):
  - Lấy danh sách tài liệu tham khảo đã bóc tách và làm giàu (3 cột: Trích dẫn gốc, Tóm tắt ngữ cảnh Exa AI, Trạng thái PDF & Nút nạp).

#### D. Nhóm Phiên Đọc Sâu (`apps/api/src/api/v1/endpoints/sessions.py`) — *PRD 03, PRD 04, PRD 07*
- 🟢 **THÊM MỚI `DELETE /api/v1/sessions/{session_id}/documents/{document_id}`** (PRD 03 §3.3):
  - Đóng bớt 1 tab bài báo khỏi phiên đọc để giải phóng vị trí (trong giới hạn 5 bài/phiên) mà không làm mất lịch sử chat chung của phiên. Hiện tại `sessions.py` mới có `POST /sessions/{id}/documents` chứ chưa có `DELETE`!
- 🟡 **SỬA `POST /api/v1/sessions/{session_id}/ingest-references` (`sessions.py` L902–943 & `session_service.py` L825–1076)**:
  - **PRD 04 §4** yêu cầu **Cơ chế Nạp 2 Tầng (Two-Tier Ingestion)**:
    - **Tầng 1 (Full-Text PDF):** Nếu có `open_access_pdf_url` (arXiv / Open Access), tải PDF, bóc tách PyMuPDF + băm chunk + nhúng vector đầy đủ để đọc và highlight.
    - **Tầng 2 (Abstract & Metadata Fallback):** Nếu bài báo bị khóa Paywall, **không báo lỗi chặn đứng** (hiện tại `session_service.py` L964 đang raise `422 ACADEMIC_ENTITY_UNRESOLVED` nếu thiếu DOI/arXiv và không tạo chunk nào cho `metadata_only`!). Thay vào đó, khởi tạo một `DocumentChunkModel` chứa Tiêu đề + Tác giả + Năm + Tóm tắt/Highlights thu được từ Exa AI, nhúng vector để Socratic AI vẫn đối sánh ngữ nghĩa được trong phiên đọc (kèm nhãn `[Chỉ có Tóm tắt - Bài gốc khóa Paywall]`).
  - Đồng thời loại bỏ đoạn code ghi vào `CitationEdgeModel` cũ (L1026–1053).
- 🟢 **THÊM MỚI `POST /api/v1/sessions/{session_id}/messages/{message_id}/feedback`** (PRD 07 §4 Tầng 1.3):
  - Nhận đánh giá 👍 (`1.0`) / 👎 (`0.0`) và `comment` từ người dùng trên từng câu trả lời AI, đẩy điểm `user_feedback` trực tiếp lên Langfuse gắn với `trace_id` của lượt chat đó.

#### E. Nhóm Thư Viện Yêu Thích & GraphRAG (`apps/api/src/api/v1/endpoints/folders.py`) — *PRD 05*
- 🟡 **SỬA `POST /api/v1/folders/synthesis` & `POST /api/v1/folders/{folder_id}/synthesis` (`folders.py` L69–113, L273–310)**:
  - Thay thế thuật toán tổng hợp heuristic 2-Tier (Notes + Chunks) hiện tại trong `library_synthesis_service.py` bằng **Truy vấn Lai (Hybrid GraphRAG + `pgvector` Search)** trên 4 thực thể cố định (`Paper`, `Method`, `Dataset`, `MetricResult`) và các đoạn văn bản gốc của các bài báo đã gắn sao (PRD 05 §3 & §4).
- 🟢 **THÊM MỚI `GET /api/v1/folders/{folder_id}/graph` & `GET /api/v1/folders/graph`** (PRD 05 §3):
  - Trả về các đỉnh (`nodes`) và cạnh (`edges`) của Đồ thị Tri thức 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) trong thư viện hoặc thư mục được chọn để hiển thị trực quan và kiểm chứng.

#### F. Nhóm Soạn Thảo LaTeX & LangGraph Agent (`apps/api/src/api/v1/endpoints/drafts.py`) — *PRD 06*
- 🟡 **SỬA `POST /api/v1/drafts`, `GET /api/v1/drafts/{id}`, `PUT /api/v1/drafts/{id}`**:
  - Hỗ trợ trường `bib_content` (nội dung file `references.bib`) và `session_id` (liên kết Phiên đọc sâu sang Bản thảo — Cầu nối Đọc sang Viết theo PRD 06 §4).
- 🟢 **THÊM MỚI `DELETE /api/v1/drafts/{id}/assets/{asset_id}`** (PRD 06 §2.B.1):
  - Hiện tại `drafts.py` chỉ có `POST /{id}/assets` và `GET /{id}/assets`, thiếu API xóa tệp đính kèm (`DELETE /api/v1/drafts/{id}/assets/{asset_id}`).
- 🟢 **THÊM MỚI / NÂNG CẤP Bộ API Lịch Sử Trò Chuyện LangGraph Agent (`draft_messages`)** (PRD 06 §3.C):
  - `GET /api/v1/drafts/{id}/messages`: Tải lịch sử hội thoại giữa người dùng và LangGraph Agent của bản thảo.
  - `POST /api/v1/drafts/{id}/messages` (hoặc nâng cấp `/api/v1/drafts/{id}/assist`): Thực thi **LangGraph Agentic Loop** có khả năng tự động chọn trong **4 Tools chuyên biệt** (`search_session_and_library_papers`, `query_library_graph_rag`, `manage_bibtex_citation`, `edit_and_compile_latex`), lưu tin nhắn vào `draft_messages` và trả về bản cập nhật `content` (`main.tex`), `bib_content` (`references.bib`), trạng thái biên dịch PDF và trích dẫn.
  - `DELETE /api/v1/drafts/{id}/messages`: Làm mới (xóa) lịch sử hội thoại của bản thảo.

---

### 3.3. Rà Soát Database Models & Khởi Tạo Schema (`apps/api/src/api/db/`)

| Trạng Thái | Bảng / Model ORM | File Định Nghĩa | Chi Tiết Xử Lý Theo PRD |
| :---: | :--- | :--- | :--- |
| 🔴 **XÓA** | `DraftCommentModel` (`draft_comments`) | `apps/api/src/api/db/models/draft.py` (L51–91), `models/__init__.py`, `init_db.py` (L234–253) | **PRD 00 §5.2**: Xóa bảng bình luận phản biện bản thảo. |
| 🔴 **XÓA** | `NoteSynthesisModel` (`note_syntheses`) | `apps/api/src/api/db/models/note.py` (L93–138), `models/__init__.py`, `init_db.py` | Thuộc tính năng Note Synthesis (Pillar 3 cũ), không nằm trong PRD 03 §6. |
| 🔴 **XÓA** | `CitationEdgeModel` (`citation_edges`) | `apps/api/src/api/db/models/reference.py` (L74–128), `models/__init__.py`, `init_db.py` | Đồ thị trích dẫn theo phiên cũ (`CITES, EXTENDS, BENCHMARKS_ON`). Thay thế bằng `graph_nodes` và `graph_edges` chuẩn 4 thực thể của PRD 05 §3. |
| 🟢 **THÊM MỚI** | `GraphNodeModel` (`graph_nodes`) | Tạo mới `apps/api/src/api/db/models/graph.py` & đăng ký vào `init_db.py` | **PRD 01 §3 & PRD 05 §3**: Lưu 4 loại thực thể cố định (`Paper`, `Method`, `Dataset`, `MetricResult`), có `user_id` (Multi-tenant isolation), `document_id`, `entity_type`, `name`, `metadata_json`, `embedding`. |
| 🟢 **THÊM MỚI** | `GraphEdgeModel` (`graph_edges`) | Tạo mới `apps/api/src/api/db/models/graph.py` & đăng ký vào `init_db.py` | **PRD 01 §3 & PRD 05 §3**: Lưu 4 loại quan hệ cố định (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`), có `user_id`, `document_id`, `source_node_id`, `target_node_id`, `relation_type`, `properties`. |
| 🟢 **THÊM MỚI** | `DraftAssetModel` (`draft_assets`) | `apps/api/src/api/db/models/draft.py` & `init_db.py` | **PRD 06 §2.B.1**: Lưu bền vững danh sách tệp hình ảnh/bảng biểu đính kèm của bản thảo trong DB (thay vì lưu biến tạm `_draft_assets_cache` trên RAM trong `draft_service.py` L49 làm mất dữ liệu khi restart!). |
| 🟢 **THÊM MỚI** | `DraftMessageModel` (`draft_messages`) | `apps/api/src/api/db/models/draft.py` & `init_db.py` | **PRD 06 §3.C**: Lưu lịch sử hội thoại giữa người dùng và LangGraph Writing Agent gắn với `draft_id` và `user_id` (CASCADE khi xóa bản thảo). |
| 🟡 **SỬA** | `DraftModel` (`drafts`) | `apps/api/src/api/db/models/draft.py` (L19–48) & `init_db.py` | Bổ sung cột `bib_content: Mapped[str]` (mặc định `""`, lưu `references.bib`) và `session_id: Mapped[UUID \| None]` (FK tới `research_sessions.id ON DELETE SET NULL`). |
| 🟡 **SỬA** | `ReferenceItemModel` (`reference_items`) | `apps/api/src/api/db/models/reference.py` (L24–71) & `init_db.py` | Bổ sung lưu trữ đầy đủ kết quả làm giàu từ Exa AI (`abstract`, `open_access_pdf_url`, `landing_url`, `sources`, `is_ingested`) để Bảng Ngữ cảnh 3 Cột (`GET /documents/{id}/references`) hiển thị tức thì không cần gọi lại Exa API nhiều lần. |
| 🟡 **SỬA** | `SessionTurnModel` (`session_turns`) | `apps/api/src/api/db/models/session.py` (L114–153) & `init_db.py` | Bổ sung cột `trace_id: Mapped[str \| None]` (và `feedback_score: Mapped[float \| None]`) để nối kết chính xác nút 👍/👎 (`POST /sessions/{id}/messages/{message_id}/feedback`) với `trace_id` trên Langfuse Cloud theo PRD 07 §4 Tầng 1.3. |

---

### 3.4. Rà Soát Services, Adapters, Schemas, Core & Workers (`apps/api/src/api/`)

#### A. Các File Cần XÓA BỎ Hoàn Toàn trong `apps/api/src/api/`
1. 🔴 **`apps/api/src/api/services/associative_memory_service.py`**:
   - Chứa `AssociativeMemoryService` phục vụ `/drafts/{id}/associative-suggestions`. Xóa theo **PRD 00 §5.4**.
2. 🔴 **`apps/api/src/api/services/note_synthesis_service.py`**:
   - Chứa `NoteSynthesisService` phục vụ `/notes:synthesize` (Pillar 3 cũ). Không nằm trong PRD 03 §6.
3. 🔴 **`apps/api/src/api/adapters/pdf_annotator.py`**:
   - Chứa `PyMuPdfAnnotator` chỉ phục vụ tính năng kết xuất PDF có nhúng Highlight (`/documents/{id}/export-pdf` và `/sessions/{id}:export-bundle`). Xóa theo **PRD 00 §5.7**.
4. 🔴 **`apps/api/src/api/utils/email_validator.py`** (và thư mục `apps/api/src/api/utils/`):
   - File re-export trùng lặp (`from api.core.email_validator import ...`), không được import ở bất kỳ đâu trong codebase.
5. 🔴 **`apps/api/src/api/workers/arq_worker.py`** (và thư mục `apps/api/src/api/workers/`):
   - Chứa các hàm giả lập `asyncio.sleep()` cho DeBERTa NLI (`run_safe_fact_check_task`), Comparison Matrix (`generate_comparison_matrix_task`) và ARQ Redis worker của kiến trúc Enterprise Pillar 5 cũ.

#### B. Các File Cần CHỈNH SỬA trong `apps/api/src/api/`
1. 🟡 **`apps/api/src/api/core/config.py`**:
   - Dòng 26: Đổi `ENVIRONMENT: Literal["development", "uat", "staging", "production", "test"]` $\rightarrow$ `Literal["development", "production", "test"]` (Xóa `"uat"`, `"staging"` theo PRD 00 §5.1 & PRD 07 §2).
   - Dòng 54: Đổi default `OPENAI_MODEL: str = "gpt-5.6-luna"` $\rightarrow$ `"gpt-5.4-mini"` (PRD 07 §2).
   - Dòng 85–90, 134–140: Cập nhật `LANGFUSE_ENVIRONMENT` tự động map `"development"` $\rightarrow$ `"verischolar-dev"`, `"production"` $\rightarrow$ `"verischolar-prod"`, và đặt `LANGFUSE_MASK_INPUT_OUTPUT: bool = False` mặc định cho cả 2 môi trường (PRD 07 §2).
   - Bổ sung `SENTRY_DSN: str | None = None`, `ALERT_WEBHOOK_URL: str | None = None`, `E2B_LATEX_TEMPLATE: str = "base"`.
2. 🟡 **`apps/api/src/api/middleware/tracing.py`**:
   - Đã có `RequestTracingMiddleware` tạo `trace_id`, gắn header `X-Trace-Id`, đo `duration_ms` và ghi audit log.
   - **Cần bổ sung theo PRD 07 §4 Tầng 2 & Tầng 3**:
     - Bộ đếm Metrics trong bộ nhớ (In-Memory System Telemetry Store) theo dõi tổng số request, tỷ lệ `2xx`/`4xx`/`5xx`, `avg_duration_ms`, `avg_ttfb_ms`, và hàng đợi vòng (ring buffer `deque(maxlen=20)`) lưu **20 lỗi gần nhất** để phục vụ `GET /api/v1/system/status`.
     - Khi xảy ra Unhandled Exception (`500`) hoặc lỗi nghiêm trọng (OpenAI/Exa/E2B/DB sập), tự động kích hoạt **Discord/Telegram Alert Webhook (`ALERT_WEBHOOK_URL`)** và đẩy sự kiện lên **Sentry (`SENTRY_DSN`)** kèm `trace_id`, `user_id`, `environment` (PRD 07 §4 Tầng 2.2 & 2.3).
3. 🟡 **`apps/api/src/api/services/ai_tracing_service.py`**:
   - Kiểm tra tên môi trường Langfuse (`verischolar-dev` / `verischolar-prod`) và bổ sung hàm `score_trace(trace_id: str, name: str, value: float, comment: str | None = None)` để endpoint `POST /api/v1/sessions/{session_id}/messages/{message_id}/feedback` gửi điểm `user_feedback` lên Langfuse Cloud (PRD 07 §4 Tầng 1.3).
4. 🟡 **`apps/api/src/api/services/draft_service.py`**:
   - **XÓA**: `_fact_checker` (`SAFEFactChecker`), `_nli_adapter` (`DeBERTaNLIAdapter`), `_draft_shares_cache`, `_draft_assets_cache` (thay bằng DB table `draft_assets`), method `verify_draft_facts()` (L292–425), method `get_overleaf_export_data()` (L926–971).
   - **SỬA & BỔ SUNG**:
     - Lưu/đọc `bib_content` (`references.bib`) và `session_id` trong `DraftModel`.
     - Khi xuất `.zip` (`export_submission_bundle`), đóng gói đầy đủ `main.tex`, `references.bib`, `preview.pdf` và toàn bộ các file ảnh trong `draft_assets`.
     - Tích hợp **LangGraph Writing Agent** (4 tools: `search_session_and_library_papers`, `query_library_graph_rag`, `manage_bibtex_citation`, `edit_and_compile_latex`) và CRUD lịch sử chat `draft_messages` (PRD 06 §3).
5. 🟡 **`apps/api/src/api/services/library_synthesis_service.py`**:
   - **XÓA**: Method `generate_comparison_matrix()` (L297–478) và các hàm helper `_extract_methodology()`, `_extract_datasets_and_metrics()`, `_extract_key_findings()`, `_extract_limitations()` chỉ phục vụ Comparison Matrix.
   - **SỬA**: Nâng cấp `synthesize_literature_review()` để thực thi **Hybrid GraphRAG (4 thực thể `Paper`, `Method`, `Dataset`, `MetricResult`) + `pgvector` Search** theo PRD 05 §3 & §4.
6. 🟡 **`apps/api/src/api/services/document_service.py`**:
   - **XÓA**: Import `PyMuPdfAnnotator`, `IPdfAnnotatorPort`, `PdfAnnotation`, `AnnotationCategory` và toàn bộ method `export_annotated_pdf()` (L2341–2496).
   - **SỬA**:
     - Thêm filter `folder_id` vào `list_documents()`.
     - Trong `star_document()` / `toggle_star()`, kích hoạt trích xuất/dọn dẹp GraphRAG 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) theo PRD 05 §2.A.
     - Hỗ trợ lưu và truy xuất danh sách tham khảo 3 cột (`GET /documents/{id}/references`) và tìm kiếm bài báo theo chủ đề (Discovery).
7. 🟡 **`apps/api/src/api/services/session_service.py`**:
   - **XÓA**: Method `export_bundle()` (L714–823), method `get_citation_graph()` (L1090–1297), method `_infer_citation_relation()` (L1079–1088), và import `CitationEdgeModel`.
   - **SỬA & BỔ SUNG**:
     - Thêm method `remove_document_from_session(session_id, document_id, user_id)` cho `DELETE /api/v1/sessions/{id}/documents/{doc_id}` (PRD 03 §3.3).
     - Cập nhật `ingest_references()` để hỗ trợ **Cơ chế Nạp 2 Tầng (Two-Tier Ingestion)**: Tầng 1 nạp Full-Text PDF nếu có `open_access_pdf_url`; Tầng 2 nạp Abstract & Metadata từ Exa AI thành chunk có vector embedding nếu bài báo bị khóa Paywall (PRD 04 §4).
8. 🟡 **`apps/api/src/api/schemas/` (`draft.py`, `folder.py`, `note.py`, `session.py`, `document.py`)**:
   - **`schemas/draft.py`**:
     - **XÓA**: `VerifyFactsRequest`, `ClaimVerificationSchema`, `VerifyFactsResponse`, `ShareCollaboratorItem`, `ShareDraftRequest`, `ShareDraftResponse`, `DraftAccessListResponse`, `CreateDraftCommentRequest`, `UpdateDraftCommentRequest`, `DraftCommentResponse`, `DraftCommentListResponse`, `AssociativeSuggestionRequest`, `AssociativeSuggestionItem`, `AssociativeSuggestionResponse`, `OverleafExportResponse`.
     - **THÊM**: `bib_content` và `session_id` vào `CreateDraftRequest`, `UpdateDraftRequest`, `DraftResponse`; thêm `DraftMessageRequest`, `DraftMessageResponse`, `DraftMessageListResponse`.
   - **`schemas/folder.py`**:
     - **XÓA**: `ComparisonMatrixRequest`, `PaperMatrixRow`, `ComparisonMatrixPaginationMeta`, `ComparisonMatrixResponseData`, `ComparisonMatrixEnvelope`.
     - **THÊM**: Schema cho Đồ thị Tri thức 4 thực thể (`GraphNodeSchema`, `GraphEdgeSchema`, `KnowledgeGraphResponseData`).
   - **`schemas/note.py`**:
     - **XÓA**: `SynthesizeNotesRequest`, `InteractiveBadgeResponse`, `NoteSynthesisResponse`, `NoteSynthesisEnvelope`.
   - **`schemas/session.py`**:
     - **XÓA**: `CitationGraphNode`, `CitationGraphEdge`, `CitationGraphResponseData`, `CitationGraphEnvelope`.
     - **THÊM**: `MessageFeedbackRequest` (`score: Literal[0, 1]` hoặc `bool`, `comment: str | None = None`), `MessageFeedbackResponse`.

---

## 4. Rà Soát Chi Tiết `packages/core/` (Domain, Ports, Services, Eval, MCP)

### 4.1. Danh Sách Các File Cần XÓA BỎ Hoàn Toàn trong `packages/core/` (31 Files)

| STT | Đường Dẫn File Trong `packages/core/src/core/` | Lý Do Xóa (Đối Chiếu PRD) |
| :---: | :--- | :--- |
| **1** | `domain/entities/safe_claim.py` | Thực thể `AtomicClaim`, `EvidencePassage`, `ClaimVerificationResult`, `DraftFactCheckReport` của SAFE Fact-Checking. **Xóa theo PRD 00 §5.5.** |
| **2** | `ports/safe_verifier.py` | Giao diện `IClaimDecomposerPort`, `INLIVerifierPort` của SAFE Fact-Checking. **Xóa theo PRD 00 §5.5.** |
| **3** | `services/safe_fact_checker.py` | Dịch vụ `RegexClaimDecomposer`, `HeuristicNLIVerifier`, `SAFEFactChecker`. **Xóa theo PRD 00 §5.5.** |
| **4** | `services/safe_nli_adapter.py` | Adapter `DeBERTaNLIAdapter` nạp model ONNX `cross-encoder-nli-deberta-v3-small` (~530MB). **Xóa theo PRD 00 §5.5.** |
| **5** | `domain/value_objects/pdf_annotation.py` | Value Object `PdfAnnotation`, `AnnotationCategory` chỉ phục vụ Export Annotated PDF. **Xóa theo PRD 00 §5.7.** |
| **6** | `ports/pdf_annotator.py` | Giao diện `IPdfAnnotatorPort` chỉ phục vụ Export Annotated PDF. **Xóa theo PRD 00 §5.7.** |
| **7** | `domain/entities/note_synthesis.py` | Thực thể `NoteSynthesis`, `InteractiveCitationBadge`, `SynthesisMode` của tính năng Note Synthesis cũ (ngoài PRD 03 §6). |
| **8** | `mcp/runtime_server.py` (và `mcp/__init__.py`) | MCP Server nội bộ chứa đường dẫn cứng `/home/VeriScholar/Workspace/VeriScholar` và kiểm tra `pgbouncer`/`enterprise`. Không nằm trong PRD MVP. |
| **9** | `prompts/documents/summary_grounded.v1.prompt.md` | **PRD 00 §3.B.2 & PRD 07 §4**: Toàn bộ Prompts được lưu trực tiếp trong mã nguồn Python của dự án (inline Python constants), không dùng hệ thống file template `.prompt.md` + Jinja2 bên ngoài. |
| **10** | `prompts/template.py` (và `prompts/__init__.py`) | Trình nạp Jinja2 + YAML frontmatter cho `.prompt.md` (chỉ có 1 file `.prompt.md` duy nhất nhưng thậm chí `llm_summarizer.py` cũng không gọi `PromptTemplate` mà tự định nghĩa prompt bằng Python!). |
| **11–31** | Toàn bộ thư mục `packages/core/src/core/eval/` (**20 files**) + `ports/eval.py` (**1 file**):<br>- `eval/__init__.py`, `eval/models.py`<br>- `eval/adapters/` (`__init__.py`, `base.py`, `pubmedqa.py`, `qasper.py`, `regression.py`, `scifact.py`)<br>- `eval/evaluators/` (`__init__.py`, `adversarial.py`, `benchmark_runner.py`, `classification.py`, `span_f1.py`)<br>- `eval/metrics/` (`__init__.py`, `bbox_iou.py`, `chunk_dimensions.py`, `retrieval_recall.py`, `safety.py`, `spatial_geometry.py`, `token_f1.py`)<br>- `ports/eval.py` | Bộ khung đánh giá học thuật hàn lâm (PubMedQA, QASPER, SciFact) nằm trong `core` không được sử dụng bởi bất kỳ API hay luồng nghiệp vụ nào của ứng dụng. Việc giám sát chất lượng AI trong MVP đã được chuyển sang **Langfuse Tracing & Online Scoring (`groundedness`, `input_safety`, `user_feedback`)** theo **PRD 07**. |

### 4.2. Các File Trong `packages/core/` Cần CHỈNH SỬA (MODIFY)
1. 🟡 **`packages/core/src/core/domain/entities/__init__.py`**:
   - Xóa export `AtomicClaim`, `ClaimVerificationResult`, `DraftFactCheckReport`, `EvidencePassage`, `VerificationLabel`, `InteractiveCitationBadge`, `NoteSynthesis`, `SynthesisLanguage`, `SynthesisMode`, `CitationEdge`, `CitationGraphScope`, `CitationRelation`.
2. 🟡 **`packages/core/src/core/domain/entities/reference.py`**:
   - Xóa `CitationRelation`, `CitationGraphScope`, `CitationEdge` (của đồ thị phiên cũ). Giữ lại `ExtractedReference`, `ParsedReferenceInfo`, `ResolvedAcademicReference` và logic bóc tách danh mục tham khảo.
3. 🟡 **`packages/core/src/core/domain/entities/draft.py`**:
   - Bổ sung trường `bib_content: str = ""` và `session_id: UUID | None = None` vào `Draft`.
4. 🟡 **`packages/core/src/core/ports/__init__.py` & `ports/note.py`**:
   - Trong `ports/__init__.py`: Xóa export `IPdfAnnotatorPort`, `IClaimDecomposerPort`, `INLIVerifierPort`, `INoteSynthesisRepositoryPort`, `IDatasetAdapterPort`, `IEvaluatorPort`.
   - Trong `ports/note.py`: Xóa `INoteSynthesisRepositoryPort` (chỉ giữ `INoteRepositoryPort`).
5. 🟡 **`packages/core/src/core/services/__init__.py`**:
   - Xóa export `SAFEFactChecker`, `RegexClaimDecomposer`, `HeuristicNLIVerifier`, `DeBERTaNLIAdapter`.
6. 🟡 **`packages/core/src/core/services/latex_compiler.py`**:
   - Cập nhật `E2BSandboxLatexCompiler` và `LocalLatexCompiler` nhận thêm `bib_content: str | None = None` và `assets: dict[str, bytes] | None = None` để khi biên dịch dự án LaTeX có trích dẫn `\cite{...}` (`references.bib`) và hình ảnh `\includegraphics{...}`, trình biên dịch ghi cả `references.bib` và các file ảnh vào thư mục/sandbox trước khi chạy `tectonic` / `pdflatex + bibtex` (PRD 06 §2.B & §3.B.3).

---

## 5. Rà Soát `deploy/` & `infra/` (Hạ Tầng & Triển Khai)

| Trạng Thái | Đường Dẫn File | Lý Do & Chi Tiết Xử Lý |
| :---: | :--- | :--- |
| 🔴 **XÓA** | `deploy/docker-compose.enterprise.yml` | Stack Enterprise Pillar 5 cũ (PgBouncer 5.000 connections, Redis, ARQ Worker cho DeBERTa NLI). Không thuộc phạm vi MVP. |
| 🔴 **XÓA** | `deploy/pgbouncer/pgbouncer.ini` (và thư mục `deploy/pgbouncer/`) | Cấu hình PgBouncer cho 100.000 concurrent users thuộc Pillar 5 Enterprise cũ. |
| 🔴 **XÓA** | `deploy/.env.enterprise.example` | Đã nêu ở Mục 2.1. |
| 🟡 **SỬA** | `deploy/systemd/verischolar-api.service` | Dòng 2 & 10 đang cấu hình `Description=VeriScholar Backend FastAPI Service (UAT)` và `Environment="APP_ENV=uat"` cùng đường dẫn cứng `/home/VeriScholar/Workspace/VeriScholar`. Cần đổi sang `ENVIRONMENT=production` và chuẩn hóa đường dẫn theo PRD 00 §5.1 & PRD 07 §2. |
| 🟡 **SỬA** | `deploy/Dockerfile.api` | Dòng 28 dùng `--workers 4`; cần lưu ý nếu dùng In-Memory Metrics cho `/api/v1/system/status` hoặc đảm bảo cài đặt dependencies qua `uv` đồng bộ với `pyproject.toml` mới (đã gỡ `onnxruntime` và `arq`). |
| 🟡 **SỬA** | `deploy/nginx/verischolar.conf` & `deploy/nginx/production-host.conf` | Bổ sung đường dẫn SSE/Agent của bản thảo (`/api/v1/drafts/.*/(messages|assist)`) vào block `proxy_buffering off; proxy_read_timeout 600s;` để không bị Nginx ngắt kết nối khi LangGraph Agent chạy vòng lặp tự sửa lỗi LaTeX trên E2B Sandbox. |
| 🟢 **GIỮ NGUYÊN** | `docker-compose.yml` & `infra/postgres/init.sql` | Khởi tạo PostgreSQL 18 + `pgvector` (`vector` & `uuid-ossp` extensions) sạch sẽ, đúng chuẩn MVP. |

---

## 6. Rà Soát `scripts/` (Kịch Bản Tự Động Hóa & Đánh Giá)

| Trạng Thái | Đường Dẫn File Trong `scripts/` | Lý Do & Chi Tiết Xử Lý |
| :---: | :--- | :--- |
| 🔴 **XÓA** | `scripts/bootstrap_enterprise.sh` | Script cài đặt Pillar 5 Enterprise (`docker-compose.enterprise.yml`, PgBouncer, ARQ DeBERTa Worker). |
| 🔴 **XÓA** | `scripts/mcp_runtime_server.py` | Wrapper chạy `core.mcp.runtime_server` đã bị loại bỏ. |
| 🔴 **XÓA** | `scripts/github_mcp_wrapper.sh` | Chứa **GitHub Personal Access Token (`github_pat_...`) hardcode trực tiếp** và đường dẫn máy cá nhân `/home/VeriScholar/...` — rủi ro lộ lọt bảo mật nghiêm trọng! |
| 🔴 **XÓA** | `scripts/auto_beta_cohort_runner.py` | Kịch bản mô phỏng Closed Beta gọi các tính năng cũ (`verify-facts`, `comments`, `citation-graph`, `notes:synthesize`). |
| 🔴 **XÓA** | `scripts/benchmark_multi_agent_stress.py` | Kịch bản stress test gọi `/associative-suggestions`, `/overleaf`, `/comparison-matrix`. |
| 🔴 **XÓA** | `scripts/test_load_concurrency.py` | Kịch bản đo tải môi trường UAT gọi `POST /api/v1/drafts/{id}/verify-facts` (đã xóa). |
| 🔴 **XÓA** | `scripts/eval/runners/get_documents_export_pdf.py` | Runner kiểm thử API `/documents/{id}/export-pdf` (đã xóa theo PRD 00 §5.7). |
| 🔴 **XÓA** | `scripts/eval/runners/post_session_export_bundle.py` | Runner kiểm thử API `/sessions/{id}:export-bundle` (đã xóa theo PRD 00 §5.7). |
| 🔴 **XÓA** | `scripts/eval/runners/notes_and_synthesis_runner.py` | Runner kiểm thử API `/notes:synthesize` (đã xóa). |
| 🔴 **XÓA** | `scripts/eval/eval_academic_benchmarks.py` & `scripts/eval/adapters/` (`pubmedqa.py`, `qasper.py`, `scifact.py`, `regression.py`) | Bộ chạy benchmark học thuật phụ thuộc vào `packages/core/src/core/eval/` (đã xóa). |
| 🟡 **SỬA** | `scripts/eval_api.py`, `scripts/eval/run_eval.py`, `scripts/eval/runners/__init__.py`, `scripts/README.md` | Gỡ bỏ đăng ký các runner đã xóa (`export-pdf`, `export-bundle`, `notes_and_synthesis_runner`). |
| 🟢 **GIỮ NGUYÊN** | `scripts/deploy_production.sh`, `scripts/deploy_web.sh`, `scripts/eval/purge_all.py` | Phục vụ triển khai thực tế và dọn dẹp dữ liệu DB. |

---

## 7. Rà Soát Toàn Bộ Hệ Thống Kiểm Thử (`apps/api/tests/`, `packages/core/tests/`, `tests/`)

### 7.1. Các File Test Cần XÓA BỎ Hoàn Toàn (26 Files)

| STT | Đường Dẫn File Test | Lý Do Xóa |
| :---: | :--- | :--- |
| **1** | `apps/api/tests/test_documents_export_pdf.py` | Test riêng cho API `GET /api/v1/documents/{id}/export-pdf` (đã xóa theo PRD 00 §5.7). |
| **2** | `apps/api/tests/test_draft_comments.py` | Test riêng cho bộ API `/api/v1/drafts/{id}/comments` (đã xóa theo PRD 00 §5.2). |
| **3** | `apps/api/tests/test_notes_synthesize.py` | Test riêng cho API `POST /api/v1/notes:synthesize` (ngoài phạm vi PRD 03 §6). |
| **4** | `packages/core/tests/domain/test_safe_fact_checker.py` | Test cho `SAFEFactChecker` (đã xóa theo PRD 00 §5.5). |
| **5** | `packages/core/tests/domain/test_safe_nli_adapter.py` | Test cho `DeBERTaNLIAdapter` (đã xóa theo PRD 00 §5.5). |
| **6** | `packages/core/tests/domain/test_safe_nli_neural.py` | Test neural ONNX cho `DeBERTaNLIAdapter` (đã xóa theo PRD 00 §5.5). |
| **7** | `packages/core/tests/domain/test_pdf_annotation.py` | Test cho `PdfAnnotation` & `PyMuPdfAnnotator` (đã xóa theo PRD 00 §5.7). |
| **8** | `packages/core/tests/domain/test_mcp_runtime_server.py` | Test cho `core.mcp.runtime_server` (đã xóa). |
| **9–22** | Toàn bộ thư mục `packages/core/tests/eval/` (**14 file test** + 4 file JSON fixtures):<br>- `test_adversarial_adapters.py`<br>- `test_adversarial_metrics_runner.py`<br>- `test_bbox_iou_metric.py`<br>- `test_benchmark_runner.py`<br>- `test_chunk_dimensions.py`<br>- `test_classification_metric.py`<br>- `test_pubmedqa_adapter.py`<br>- `test_qasper_adapter.py`<br>- `test_regression_adapter.py`<br>- `test_retrieval_recall_metric.py`<br>- `test_safety_metric.py`<br>- `test_scifact_adapter.py`<br>- `test_spatial_geometry_metric.py`<br>- `test_token_f1_metric.py` | Test cho gói `core.eval` đã bị loại bỏ. |
| **23–25** | Các file trong `tests/evals/`:<br>- `tests/evals/test_eval_metrics.py`<br>- `tests/evals/test_two_tier_eval.py`<br>- `tests/evals/test_parse_chunking_eval.py` | Phụ thuộc trực tiếp vào `scripts/eval/eval_academic_benchmarks.py` và `core.eval`. |
| **26** | `tests/api/test_module4_folders.py` | File bản sao dư thừa của `apps/api/tests/test_module4_folders.py` (trong `apps/api/tests/` đã có file chính thức mới hơn). |

### 7.2. Các File Test Cần CHỈNH SỬA (MODIFY) Để Bám Sát PRD MVP
1. 🟡 **`apps/api/tests/test_drafts_lifecycle.py`**:
   - Xóa các test case gọi `/verify-facts`, `/share`, `/overleaf`, `/overleaf-launch`, `/associative-suggestions`.
   - Bổ sung test cho `bib_content`, `DELETE /drafts/{id}/assets/{asset_id}`, và CRUD `/drafts/{id}/messages` (LangGraph Agent).
2. 🟡 **`apps/api/tests/test_module4_folders.py`**:
   - Xóa các test case gọi `/folders/comparison-matrix` và `/folders/{id}/comparison-matrix`.
   - Cập nhật test `/folders/synthesis` kiểm chứng Hybrid GraphRAG 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`).
3. 🟡 **`apps/api/tests/test_sessions_lifecycle.py` & `apps/api/tests/test_reference_ingestion.py`**:
   - Xóa các test case gọi `/sessions/{id}:export-bundle` và `/sessions/{id}/citation-graph`.
   - Cập nhật test `ingest-references` theo đúng **Cơ chế Nạp 2 Tầng (Two-Tier Ingestion)** (Tầng 1 Full PDF, Tầng 2 Abstract Fallback).
   - Bổ sung test cho `DELETE /api/v1/sessions/{id}/documents/{doc_id}`.
4. 🟡 **`apps/api/tests/test_backend_pillars_completion.py` & `apps/api/tests/test_m1_pillars_empirical_stress.py`**:
   - Gỡ bỏ các bài test kiểm tra Pillar 5 (`docker-compose.enterprise.yml`, `arq_worker.py`), SAFE Fact-Checking (`verify-facts`), Overleaf Launch, Associative Memory, Comparison Matrix.
5. 🟡 **`apps/api/tests/test_ai_tracing.py` & `apps/api/tests/test_logging.py`**:
   - Cập nhật kiểm chứng `LANGFUSE_ENVIRONMENT` (`verischolar-dev` / `verischolar-prod`), endpoint `POST /sessions/{id}/messages/{msg_id}/feedback` và `GET /api/v1/system/status` theo PRD 07.
6. 🟡 **`packages/core/tests/domain/test_hexagonal_invariants.py`**:
   - Gỡ bỏ kiểm tra các port/entity đã xóa (`safe_verifier`, `pdf_annotator`, `note_synthesis`).

---

## 8. Bảng Tổng Hợp Các Tính Năng Backend MVP Còn Thiếu Cần Bổ Sung (Implementation Checklist)

Để Backend và Core đạt chuẩn 100% với bộ PRD `00` $\rightarrow$ `07` sau khi dọn dẹp code thừa, dưới đây là danh sách các hạng mục kỹ thuật cần triển khai:

1. **Module 1 (PRD 02 — Discovery & Documents CRUD):**
   - [ ] Bổ sung API Khám phá bài báo theo chủ đề (Topic Search kết hợp Exa AI + Semantic Scholar / arXiv) và luồng nạp 1-Click vào phiên đọc.
   - [ ] Bổ sung tham số lọc `folder_id` cho `GET /api/v1/documents`.
2. **Module 2 (PRD 03 — Sessions & Deep Reading):**
   - [ ] Bổ sung API `DELETE /api/v1/sessions/{session_id}/documents/{document_id}` để đóng tab bài báo trong phiên.
3. **Module 3 (PRD 04 — Context Table & Roadmap):**
   - [ ] Bổ sung API `GET /api/v1/documents/{document_id}/references` trả về dữ liệu Bảng Ngữ cảnh 3 Cột đã lưu.
   - [ ] Nâng cấp `POST /api/v1/sessions/{session_id}/ingest-references` thực thi trọn vẹn **Two-Tier Ingestion** (Tầng 1: Tải & bóc tách PDF Open-Access; Tầng 2: Tạo chunk chứa Tiêu đề + Tác giả + Năm + Tóm tắt Exa AI kèm vector embedding khi bài báo bị khóa Paywall).
4. **Module 4 (PRD 05 — Favorite Library & Hybrid GraphRAG):**
   - [ ] Thiết kế 2 bảng `graph_nodes` và `graph_edges` cho **4 loại thực thể cố định (`Paper`, `Method`, `Dataset`, `MetricResult`)** và **4 loại cạnh (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`)** có phân tách `user_id`.
   - [ ] Viết `GraphRAGService` tự động trích xuất thực thể bằng Structured Output (`gpt-5.4-mini`) khi bài báo được gắn sao (`is_starred = True`) và xóa thực thể khi bỏ gắn sao.
   - [ ] Nâng cấp `LibrarySynthesisService` kết hợp truy vấn Đồ thị 4 thực thể + tìm kiếm vector `pgvector` trên `document_chunks`.
5. **Module 5 (PRD 06 — Agentic Overleaf Writing):**
   - [ ] Bổ sung cột `bib_content`, `session_id` vào bảng `drafts`, tạo bảng `draft_assets` và `draft_messages`.
   - [ ] Bổ sung API `DELETE /api/v1/drafts/{id}/assets/{asset_id}` và bộ 3 API `GET/POST/DELETE /api/v1/drafts/{id}/messages`.
   - [ ] Xây dựng **LangGraph Writing Agent** với 4 Tools chuyên biệt (`search_session_and_library_papers`, `query_library_graph_rag`, `manage_bibtex_citation`, `edit_and_compile_latex`) có vòng lặp tự sửa lỗi LaTeX tối đa 2 lần qua E2B Sandbox / Tectonic.
6. **Module 6 (PRD 07 — Monitoring & Langfuse):**
   - [ ] Chuẩn hóa 2 môi trường `development` (`verischolar-dev`) và `production` (`verischolar-prod`), tắt `LANGFUSE_MASK_INPUT_OUTPUT=false`.
   - [ ] Bổ sung API `POST /api/v1/sessions/{session_id}/messages/{message_id}/feedback` gửi điểm `user_feedback` (👍/👎) lên Langfuse theo `trace_id`.
   - [ ] Bổ sung kích hoạt cảnh báo Webhook (`ALERT_WEBHOOK_URL`) và Sentry (`SENTRY_DSN`) khi có lỗi 500 hoặc sập kết nối dịch vụ ngoài.
   - [ ] Nâng cấp `GET /health/ready` và thêm mới `GET /api/v1/system/status` (uptime, request rates, avg latency/TTFB, 20 lỗi gần nhất).
