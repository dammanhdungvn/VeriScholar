# THIẾT KẾ KIẾN TRÚC REPO-OWNED UNIVERSAL AGENT HARNESS CHO VERISCHOLAR MVP
# (UNIVERSAL AGENT HARNESS & ERGONOMICS SPECIFICATION)

**Ngày ban hành:** 2026-10-25  
**Trạng thái:** DỰ THẢO THIẾT KẾ (DESIGN DOCUMENT V1)  
**Nhánh triển khai:** `refactor/mvp-cleanup-and-directory`  
**Tham chiếu thực tiễn:** Kiến trúc Agent Harness của Langfuse ([`.agents/`](../../../.agents))  
**Cơ sở nghiệp vụ:** Bộ tài liệu [`docs/PRD/`](../../PRD) và [`docs/specs/`](../../specs) (Commit ``5706f11``)

---

## 1. Mục Đích & Bối Cảnh Thực Tế (Intent & The Why)

Khi lập trình dự án phức tạp cùng các Agent AI (như Antigravity CLI, Claude Code, Cursor, Codex), vấn đề lớn nhất không nằm ở khả năng viết code của mô hình ngôn ngữ lớn (LLM), mà nằm ở **Công thái học Tác nhân (Agent Ergonomics)** và **Kiểm soát Ngữ cảnh (Context Window Management)**:
1. **Ô nhiễm ngữ cảnh (Context Pollution / Token Bloat):** Nếu đưa toàn bộ hàng chục trang hướng dẫn backend, frontend, database, quy chuẩn bảo mật vào file prompt gốc (`AGENTS.md` hoặc `.cursorrules`), mỗi lượt prompt sẽ ngốn hàng chục ngàn tokens lãng phí, làm loãng sự chú ý của mô hình (Attention Dilution) và tăng tỷ lệ sinh lỗi/ảo giác.
2. **Quy tắc bị lỗi thời (Rule Rot & Agent Drift):** Khi dự án tiến hóa (như việc VeriScholar loại bỏ Neo4j và SQLite để chuẩn hóa sang PostgreSQL + `pgvector`), nếu các quy tắc cũ vẫn nằm rải rác trong các file hướng dẫn, AI sẽ bị "mắc kẹt" vào các giả định lỗi thời.
3. **Thiếu tính xác định khi chạy thử (Non-Deterministic Sandboxing):** Mỗi lần kiểm thử tính năng RAG hoặc GraphRAG, nếu AI phải gọi API OpenAI/Exa thật thì vừa tốn chi phí, vừa chậm, vừa dễ gãy do mạng; nếu để AI tự viết dữ liệu test ngẫu nhiên thì dữ liệu thiếu chuẩn mực học thuật (thiếu Bounding Box, sai schema 4 thực thể).

**Giải pháp:**  
Học hỏi từ kiến trúc xuất sắc của Langfuse ([`.agents/`](../../../.agents)), VeriScholar xây dựng một **Khung Điều Hướng Tác Nhân Đa Nền Tảng Thuần Dự Án (Repo-Owned Universal Agent Harness)** tinh gọn, hoạt động như một "hệ điều hành quy chuẩn" cho mọi Agent AI tham gia phát triển dự án.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Chống Mục Tiêu (Goals, Non-Goals & Anti-Goals)

### A. Mục tiêu cốt lõi (Goals)
1. Dọn sạch 100% các file di sản unstaged/deleted của hệ thống 5-pillar cũ trong working tree để có môi trường sạch sẽ tuyệt đối.
2. Thiết lập file gốc [`AGENTS.md`](../../../AGENTS.md) siêu tinh gọn (< 150 dòng) làm "Hiến pháp tối cao", liên kết symlink với `.agents/AGENTS.md`.
3. Thiết lập [`ARCHITECTURE_PRINCIPLES.md`](../../../.agents/ARCHITECTURE_PRINCIPLES.md) ghi nhận 5 bất biến kiến trúc tối thượng của VeriScholar MVP.
4. Xây dựng đúng **4 Skills nghiệp vụ trọng tâm** theo nguyên tắc Tiết lộ Ngữ cảnh Tuần tự (Progressive Disclosure):
   * `verischolar-backend`: FastAPI async, SQLAlchemy 2.0, pgvector SQL RRF, Hexagonal Architecture.
   * `verischolar-frontend`: React 19, Canvas PDF viewer, Bbox highlight layer, KaTeX, unbuffered SSE.
   * `verischolar-tdd`: Quy trình TDD (Test đỏ trước $\rightarrow$ Code xanh sau), transaction rollback, mock E2B & OpenAI.
   * `agent-maintenance`: Quy trình tự cập nhật, kiểm thử và đào thải skill khi codebase thay đổi.
5. Cung cấp bộ công cụ chạy thử xác định (Deterministic Developer Tools):
   * `scripts/dev/setup.sh`: Script kiểm tra và xác nhận môi trường dev (Python 3.12, Node 22, Docker PostgreSQL `pgvector`, Redis 7).
   * `scripts/dev/seed.py`: Script nạp sẵn 3 bài báo mẫu học thuật kinh điển (Transformer, ResNet, BERT) kèm đầy đủ Bounding Box và Đồ thị 4 thực thể để test offline 100%.

### B. Phi mục tiêu (Non-Goals)
1. Không sao chép máy móc 35+ skills của Langfuse (không tạo các skills cho Linear billing, Pylon support, Datadog cloud monitor... vì nằm ngoài nhu cầu của VeriScholar).
2. Không xây dựng hệ thống transpiler phức tạp nếu dự án hiện tại chỉ cần chạy mượt trên Antigravity CLI và Cursor/Claude Code.
3. **Không can thiệp sâu vào logic nghiệp vụ của các Feature tương lai** (như GraphRAG hay Overleaf MicroVM) — bộ harness này thiết lập khung quy chuẩn, dev tools và rào chắn kiểm thử cho toàn bộ dự án.
4. **Không xóa bỏ các UI Design Skills hữu ích đã có**: Giữ lại 8 kỹ năng giao diện hiện hữu (`ui-ux-pro-max`, `ui-styling`, `design`, `brand`, v.v.) trong `.agents/skills/` và chỉ bổ sung 4 core skills nghiệp vụ VeriScholar.

### C. Chống mục tiêu (Anti-Goals)
1. **Tuyệt đối cấm để lọt bất kỳ quy tắc cũ nào của hệ thống 5-pillar** (Neo4j, SQLite fallback, Comparison Matrix, DeBERTa, SAFE NLI, Enterprise docker). Dọn sạch tàn dư `init_sqlite_fallback()` và `ComparisonMatrix` khỏi mã nguồn.
2. **Không để `AGENTS.md` vượt quá 180 dòng:** Bất kỳ hướng dẫn chi tiết nào đều phải đẩy vào `skills/`.
3. **Không bao giờ viết văn xuôi cho những gì có thể kiểm tra bằng mã tự động:** Quy tắc kiến trúc phải được gác cổng bằng bài test tự động (`test_architecture_boundary.py`).

---

## 3. Các Phương Án Đã Cân Nhắc & Lựa Chọn (Approaches & Trade-offs)

### Phương Án A: Prompt Đơn Khối (Monolithic Prompt)
* *Mô tả:* Nhét toàn bộ hướng dẫn backend, frontend, database, quy chuẩn git vào 1 file duy nhất `AGENTS.md` (~1.200 dòng).
* *Ưu điểm:* Cài đặt nhanh trong 5 phút.
* *Nhược điểm:* Tốn token trên từng lượt hỏi đáp, AI dễ bỏ sót các quy tắc ở giữa file do hiện tượng "Lost in the Middle".
* *Đánh giá:* **LOẠI BỎ**.

### Phương Án B: Repo-Owned Universal Agent Harness (Mô hình Langfuse)
* *Mô tả:* Tách rời Hiến pháp tối cao (`AGENTS.md`), Nguyên tắc kiến trúc (`ARCHITECTURE_PRINCIPLES.md`), và Thư viện kỹ năng tải theo nhu cầu (`.agents/skills/`).
* *Ưu điểm:* Tối ưu hóa 90% lượng token tiêu thụ, kiểm soát ranh giới kiến trúc cực kỳ chặt chẽ, dễ bảo trì và mở rộng sau này.
* *Nhược điểm:* Cần một bước thiết lập bài bản ban đầu.
* *Đánh giá:* **ĐƯỢC CHỌN (RECOMMENDED)**.

### Phương Án C: Dựa Thuần Túy Vào `docs/specs/` (Zero Harness)
* *Mô tả:* Không tạo thư mục `.agents/`, yêu cầu AI mỗi lần làm việc phải tự đọc các file trong `docs/specs/`.
* *Ưu điểm:* Không phát sinh thêm file harness.
* *Nhược điểm:* AI thiếu các cẩm nang "cơ bắp" (code template cụ thể, cách viết test fixture, lệnh xác minh nhanh), dẫn đến code sinh ra không đồng nhất về phong cách.
* *Đánh giá:* **LOẠI BỎ**.

---

## 4. Bố Cục Thư Mục & Thiết Kế Chi Tiết Từng Thành Phần

```text
VeriScholar/
├── AGENTS.md -> .agents/AGENTS.md         # Symlink ở thư mục gốc để mọi công cụ AI tự nhận diện
├── .agents/
│   ├── AGENTS.md                          # Hiến pháp ngắn gọn: Scope, Luồng làm việc, Verification Gates
│   ├── ARCHITECTURE_PRINCIPLES.md         # 5 Bất biến kiến trúc của VeriScholar
│   └── skills/
│       ├── verischolar-backend/
│       │   └── SKILL.md                   # Cẩm nang FastAPI, SQLAlchemy Async, pgvector SQL RRF
│       ├── verischolar-frontend/
│       │   └── SKILL.md                   # Cẩm nang React 19, Canvas Viewer, Bbox Highlight, KaTeX
│       ├── verischolar-tdd/
│       │   └── SKILL.md                   # Quy trình TDD, Pytest Rollback Fixtures, Deterministic Mocks
│       └── agent-maintenance/
│           └── SKILL.md                   # Quy trình bảo trì harness, chống lỗi thời quy tắc (Rule Rot)
└── scripts/
    └── dev/
        ├── setup.sh                       # Kiểm tra môi trường cục bộ (Python, Node, Docker, DB)
        └── seed.py                        # Seeder nạp 3 bài báo mẫu học thuật offline
```

### A. Nội Dung [`AGENTS.md`](../../../AGENTS.md) (Hiến Pháp Tối Cao)
* **Scope:** Nền tảng Trợ lý AI Nghiên cứu Khoa học Toàn trình (VeriScholar MVP) bám sát 100% [`docs/PRD/`](../../PRD) và [`docs/specs/`](../../specs).
* **Quy tắc làm việc (How To Work):**
  1. Luôn đọc tối thiểu ngữ cảnh cần thiết; tra cứu kỹ thuật qua các skills chuyên biệt trong `.agents/skills/`.
  2. Bắt buộc theo phương pháp TDD: Viết test đỏ trước $\rightarrow$ Code xanh sau $\rightarrow$ Refactor.
  3. Cấm vi phạm quy tắc Kiến trúc Lục giác: `packages/core` là thuần Python, không bao giờ import từ `apps/api`.
  4. Trước khi tuyên bố hoàn thành bất kỳ nhiệm vụ nào, bắt buộc phải chạy bộ 4 cổng kiểm tra:
     * `uv run ruff check .`
     * `uv run pytest`
     * `npm --prefix apps/web run test`
     * `npm --prefix apps/web run build`
* **Cơ chế tải Skills:**
  * Làm API / Backend / Database $\rightarrow$ nạp `verischolar-backend`.
  * Làm Giao diện / PDF Viewer / KaTeX $\rightarrow$ nạp `verischolar-frontend`.
  * Viết Unit / Integration Test $\rightarrow$ nạp `verischolar-tdd`.
  * Cập nhật quy tắc / Đổi kiến trúc $\rightarrow$ nạp `agent-maintenance`.

### B. Nội Dung [`ARCHITECTURE_PRINCIPLES.md`](../../../.agents/ARCHITECTURE_PRINCIPLES.md) (5 Bất Biến Kiến Trúc)
1. **Thuần PostgreSQL 16+ với `pgvector` & Redis 7:** Không có cơ sở dữ liệu đồ thị rời (Neo4j) và tuyệt đối không có SQLite fallback.
2. **Kiến Trúc Lục Giác Độc Lập:** `packages/core` không phụ thuộc bất kỳ framework hay adapter nào.
3. **Lưu Trữ CAS SHA-256 Với Cam Kết Zero-Retention:** File PDF và figures được lưu theo băm; khi `ref_count <= 0` file vật lý bị xóa ngay lập tức.
4. **Cô Lập Tuyệt Đối Qua E2B MicroVM Sandbox:** Mọi tác vụ biên dịch LaTeX chạy cô lập trên E2B với cờ `--no-shell-escape` và timeout 15s; không bao giờ gọi `pdflatex` trực tiếp trên host.
5. **Giám Sát 3 Tầng Nhẹ Nhàng:** `trace_id` đồng nhất, Langfuse Cloud tracing, báo lỗi Telegram/Discord webhook bất đồng bộ, deep ping `/health/ready` và in-memory status `/api/v1/system/status`.

### C. Nội Dung 4 Skills Nghiệp Vụ Cốt Lõi
1. **`verischolar-backend`:** Hướng dẫn cấu trúc router `apps/api/src/api/v1/endpoints/`, Dependency Injection, Session per Request (và `AsyncSessionLocal` độc lập cho `BackgroundTasks`), truy vấn Hybrid RAG kết hợp Cosine Distance (`<->`) và GIN `to_tsvector('simple', content)`.
2. **`verischolar-frontend`:** Hướng dẫn cấu trúc React 19, Zustand stores (`useAuthStore`, `useSessionStore`, `useDraftStore`), tích hợp `PdfCanvasViewer` với lớp vẽ Bounding Box `[x0, y0, x1, y1]`, xử lý stream unbuffered SSE bằng `fetch-event-source`.
3. **`verischolar-tdd`:** Hướng dẫn setup fixture `db_session` tự động `rollback()` sau mỗi test case, mock E2B client và OpenAI API, cách viết test kiểm tra cô lập đa người dùng `user_id`.
4. **`agent-maintenance`:** Quy tắc bảo trì quy chuẩn:
   * Khi thêm bảng hoặc sửa logic endpoint: Phải cập nhật skill tương ứng trong cùng PR/commit.
   * Khi xóa bỏ một tính năng: Phải xóa sạch skill và test case liên quan.
   * Quy tắc phân xử thẩm quyền: `Code & Tests Hiện Tại > Technical Specs > Skills`.

### D. Bộ Công Cụ Developer Chạy Thử Xác Định (`scripts/dev/`)
1. **`scripts/dev/setup.sh`:**
   * Cập nhật `docker-compose.yml` bổ sung service `redis:7-alpine` (cùng mạng với `pgvector`).
   * Kiểm tra phiên bản Python (`>= 3.12`), Node (`>= 22`), Docker engine.
   * Ping thử PostgreSQL (kiểm tra extension `vector`), ping thử Redis.
   * Cài đặt dependencies qua `uv sync --all-packages` và `pnpm install`.
2. **`scripts/dev/seed.py`:**
   * Nạp 1 tài khoản học giả mặc định (`dev@verischolar.edu.vn / ScholarDev@123456`).
   * Nạp 3 bài báo kinh điển và tự động đảm bảo physical PDF blobs trong `storage/blobs/` (bằng cách copy `Attention Is All You Need.pdf` thực tế và sinh dummy PDF tối thiểu cho ResNet và BERT để tránh lỗi 404 khi test frontend reader):
     1. *Attention Is All You Need (Vaswani et al., 2017)* — Kèm 10 chunks và dữ liệu thực thể đồ thị mẫu (theo schema hiện hữu, tương thích trước khi Feature 05 ra mắt).
     2. *Deep Residual Learning for Image Recognition (He et al., 2016)* — Kèm tọa độ Bounding Box mẫu.
     3. *BERT: Pre-training of Deep Bidirectional Transformers (Devlin et al., 2018)*.
   * Nạp 1 phiên đọc sâu mẫu (`session`) và 1 bản thảo mẫu (`draft`).

---

## 5. Rào Chắn Kiểm Thử Tự Động (Architectural Assertion Test)

Để biến các quy tắc văn xuôi thành rào chắn kỹ thuật không thể xuyên thủng, chúng ta thiết lập bài test tự động:
* **Vị trí file:** `apps/api/tests/test_architecture_boundary.py`
* **Hành vi kiểm tra:**
  1. **Kiểm tra Lục giác (Hexagonal Isolation):** Quét AST cây thư mục `packages/core/src/core/domain/` và `ports/`: Cho phép Standard Library và `pydantic`. Báo lỗi nếu phát hiện import bất kỳ thư viện framework, database hoặc I/O nào (`fastapi`, `sqlalchemy`, `redis`, `fitz`, `httpx`, `aiofiles`) hoặc bất kỳ import nào từ `apps.api`.
  2. **Quét Mã Nguồn Production Chống Di Sản 5-Pillar:** Quét mã nguồn Python production trong `apps/api/src/` và `packages/core/src/`: Báo lỗi nếu phát hiện chuỗi ký tự cấm: `aiosqlite`, `sqlite3`, `neo4j`, `ComparisonMatrix`, `DeBERTa`. (Dọn sạch hàm `init_sqlite_fallback()` và class `ComparisonMatrix` đang tồn tại).
  3. **Kiểm tra Tính Toàn Vẹn Của Harness (`.agents/`):** Báo lỗi nếu thiếu các file cốt lõi (`AGENTS.md`, `ARCHITECTURE_PRINCIPLES.md`, và 4 core skills nghiệp vụ), hoặc nếu `AGENTS.md` vượt quá 200 dòng.

---

## 6. Phân Công & Trách Nhiệm Thực Thi (Builder Scope)

Sau khi tài liệu thiết kế này được phê duyệt:
1. Stage và commit việc dọn dẹp các tệp di sản 5-pillar đang deleted trên working tree.
2. Tạo thư mục `.agents/`, symlink `AGENTS.md`, và viết 2 file `AGENTS.md`, `ARCHITECTURE_PRINCIPLES.md`.
3. Tạo 4 thư mục skill trong `.agents/skills/`.
4. Tạo `scripts/dev/setup.sh` và `scripts/dev/seed.py`.
5. Tạo bài test `apps/api/tests/test_architecture_boundary.py` và chạy xác minh toàn bộ test suite.
