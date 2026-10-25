# PRD 08: Triển Khai Hạ Tầng Azure Ubuntu, CI/CD & Thực Nghiệm Đánh Giá Hệ Thống (Deployment, CI/CD & System Evaluation)

**Phiên bản:** 2.0-OFFICIAL  
**Trạng thái:** Đã khóa phạm vi MVP (Scope-Locked)  
**Tác giả:** Business Analyst & Senior DevOps Architect  
**Tài liệu kỹ thuật đối ứng:** [`../specs/09-deployment-cicd-and-evaluation-spec.md`](../specs/09-deployment-cicd-and-evaluation-spec.md)

---

## 1. Bối Cảnh, Nỗi Đau & Giá Trị Cốt Lõi (Problem Statement & Value Proposition)

### 1.1. Bối cảnh nghiệp vụ
Một nền tảng AI Nghiên cứu Khoa học hoàn chỉnh không chỉ dừng lại ở việc chạy được trên máy lập trình viên (`localhost`), mà bắt buộc phải được triển khai ổn định trên môi trường máy chủ thực tế (**Azure Ubuntu VM**) để phục vụ người dùng thật và minh chứng trực tiếp trước Hội đồng Bảo vệ Đồ án Tốt nghiệp Đại học. Đồng thời, báo cáo khoa học cấp đại học đòi hỏi bộ số liệu thực nghiệm định lượng rõ ràng về độ trễ phản hồi, độ chính xác truy xuất tri thức và độ tin cậy của quy trình kiểm thử tự động.

### 1.2. Nỗi đau hiện tại (Key Pain Points)
1. **Đứt gãy luồng Streaming SSE khi đưa lên Reverse Proxy thực tế:** Các cấu hình máy chủ Nginx mặc định tự động gom bộ đệm (`proxy_buffering on`), khiến hiệu ứng trả lời từng từ (token-by-token SSE) của Hybrid RAG, Context Table, GraphRAG và Trợ lý LaTeX bị treo cứng cho tới khi LLM sinh xong toàn bộ văn bản.
2. **Pipeline CI/CD chậm chạp và thiếu môi trường CSDL thật:** Chạy kiểm thử trên GitHub Actions không kèm container PostgreSQL `pgvector` và Redis 7 khiến các bài kiểm thử tích hợp không thể xác minh thực tế trước khi gộp nhánh `main`, hoặc tốn thời gian build Docker vô ích khi mã nguồn còn lỗi cú pháp.
3. **Thiếu bộ chỉ tiêu Thực nghiệm Định lượng chuẩn hóa cho Đồ án Tốt nghiệp:** Nhiều dự án phần mềm chỉ trình bày tính năng giao diện mà thiếu kịch bản đo đạc định lượng (TTFT, Recall@K, Bounding Box IoU, tỷ lệ tự sửa lỗi LaTeX) khiến chương Thực nghiệm & Đánh giá thiếu sức thuyết phục khoa học.

### 1.3. Ma trận Giá trị Trước & Sau (Before vs. After Value Matrix)

| Tiêu chí vận hành & nghiệm thu | Trước khi có Phân hệ 08 (Ad-hoc Localhost) | Sau khi có Phân hệ 08 (VeriScholar Production & Thesis Standard) |
| :--- | :--- | :--- |
| **Luồng Streaming SSE qua Nginx** | Bị nghẽn bộ đệm ở tầng proxy làm giao diện đứng hình nhiều giây khi gọi AI. | Cấu hình Nginx TLS 1.3 tắt bộ đệm (`proxy_buffering off`, `X-Accel-Buffering: no`) cho toàn bộ 5 tuyến SSE. |
| **Kiểm thử Tự động GitHub Actions CI** | Thiếu container `pgvector`/`redis`, cài đặt công cụ thừa làm chậm pipeline. | Kiến trúc CI 2 tầng Fast-Fail gắn sẵn Service Containers `pgvector` + `redis`, chỉ build Docker khi 4 cổng kiểm thử đã xanh. |
| **Lưu trữ PDF & Triển khai Azure VM** | Dữ liệu PDF dễ mất khi khởi động lại container; cập nhật thủ công dễ sai sót. | Lưu trữ CAS bền vững (`/var/lib/verischolar/cas`), cô lập cổng DB nội bộ `127.0.0.1`, tự động hóa qua `deploy_production.sh`. |
| **Số liệu Thực nghiệm Đồ án (Chương 4)** | Cảm tính, thiếu kịch bản đo lặp lại được. | Chuẩn hóa 3 Bộ Thực nghiệm Định lượng (E1: Độ trễ, E2: Độ chính xác AI Grounding, E3: Ma trận Kiểm thử Tự động). |

---

## 2. Phân Loại Tác Nhân & Bảng Tổng Hợp Use Case (Actors & Use Case Summary)

### 2.1. Danh mục Tác nhân (Actors)
- **Kỹ sư Vận hành / Tác giả Đồ án (`DevOps Engineer / Thesis Author`):** Người cấu hình máy chủ Azure Ubuntu VM, theo dõi CI/CD và thu thập số liệu thực nghiệm đưa vào báo cáo.
- **Hệ thống GitHub Actions CI/CD (`Automated Pipeline`):** Tác nhân tự động thực thi kiểm tra chất lượng mã nguồn (4 Cổng Xác Minh) và đóng gói phát hành khi có thay đổi trên nhánh `main`.
- **Hội đồng Chấm Đồ án & Học giả Thử nghiệm (`Evaluation Reviewers`):** Người trực tiếp truy cập tên miền HTTPS chính thức để kiểm chứng tốc độ streaming, độ chuẩn xác của trích dẫn Bounding Box và khả năng biên dịch LaTeX.

### 2.2. Bảng Tổng hợp Use Case (Use Case Catalog)

| Mã UC | Tên Ca Sử Dụng | Tác Nhân Chính | Mục Tiêu Nghiệp Vụ & SLA |
| :--- | :--- | :--- | :--- |
| **UC-08.1** | Kiểm định Chất lượng Tự động qua CI 2 Tầng | Automated Pipeline | Chặn 100% mã lỗi hoặc vi phạm ranh giới kiến trúc trước khi gộp vào `main` trong `< 3 phút`. |
| **UC-08.2** | Triển khai & Vận hành Không Gián Đoạn trên Azure Ubuntu | DevOps Engineer | Cập nhật giao diện Vite tĩnh, chạy migration DB và khởi động lại dịch vụ API/SSE với downtime `< 5 giây`. |
| **UC-08.3** | Thực thi Bộ Thực nghiệm Định lượng (E1, E2, E3) | Thesis Author | Đo đạc và xuất bảng kết quả độ trễ TTFT, độ chính xác trích dẫn RAG/GraphRAG và tỷ lệ pass kiểm thử. |
| **UC-08.4** | Sao lưu & Phục hồi Dữ liệu Bền vững (CAS & PostgreSQL) | DevOps Engineer | Đảm bảo an toàn 100% cho cơ sở dữ liệu 16 bảng và kho bài báo PDF trước sự cố khởi động lại máy chủ. |

---

## 3. Đặc Tả Chi Tiết Các Ca Sử Dụng (Detailed Use Case Specifications)

### UC-08.1: Kiểm định Chất lượng Tự động qua CI 2 Tầng (2-Tier Fast-Fail CI Gatekeeping)
- **Tác nhân:** Hệ thống GitHub Actions CI (`ci.yml`) kích hoạt khi có sự kiện `push` hoặc `pull_request` vào nhánh `main`.
- **Điều kiện tiên quyết:** Kho mã nguồn chứa đầy đủ cấu hình `.github/workflows/ci.yml`, `pyproject.toml`, `uv.lock` và `apps/web/pnpm-lock.yaml`.
- **Sự kiện kích hoạt:** Lập trình viên đẩy commit mới lên nhánh làm việc hoặc nhánh `main`.
- **Luồng chuẩn (Main Success Scenario):**
  1. Hệ thống khởi chạy song song 3 tác vụ Tầng 1 gồm `security-scan` (Gitleaks), `backend-quality-gates` (kèm container `pgvector` và `redis:7-alpine`) và `frontend-quality-gates`.
  2. Tác vụ `backend-quality-gates` đồng bộ gói bằng `uv sync --all-packages --frozen`, kiểm tra định dạng `ruff check .` và `ruff format --check .`, sau đó chạy toàn bộ `pytest` (bao gồm kiểm thử ranh giới kiến trúc và kiểm thử tích hợp CSDL).
  3. Tác vụ `frontend-quality-gates` cài đặt gói qua `pnpm install --frozen-lockfile`, kiểm tra `pnpm lint` (Oxlint), kiểm tra kiểu `tsc -b`, chạy `vitest run` và biên dịch thử bản phân phối `pnpm build`.
  4. Khi cả hai tác vụ kiểm tra Backend và Frontend đều vượt qua 100%, hệ thống kích hoạt Tầng 2 (`docker-validation`) để đóng gói thử ảnh container `Dockerfile.api`, `Dockerfile.web` và kiểm tra cú pháp kịch bản triển khai.
- **Kết quả đầu ra (Postconditions):** Commit được gắn tích xanh xác nhận đạt chuẩn sản xuất và xuất tệp báo cáo kiểm thử JUnit XML.
- **Luồng ngoại lệ (Exception Flows):**
  - *3a. Lỗi định dạng, vi phạm kiến trúc Lục giác hoặc đứt liên kết tài liệu:* Tác vụ Tầng 1 dừng ngay lập tức với mã thoát khác `0`, hủy bỏ tác vụ Tầng 2 để tiết kiệm tài nguyên và thông báo dòng lỗi chi tiết.

---

### UC-08.2: Triển khai & Vận hành Không Gián Đoạn trên Azure Ubuntu (Zero-Downtime Azure Rollout)
- **Tác nhân:** Kỹ sư Vận hành hoặc quy trình CD (`cd.yml` / `scripts/deploy_production.sh`).
- **Điều kiện tiên quyết:** Máy chủ Azure Ubuntu VM đã mở cổng tường lửa `80`/`443` trên Azure NSG, cài đặt sẵn Docker Compose, Nginx, chứng chỉ SSL Let's Encrypt và tệp cấu hình `.env`.
- **Sự kiện kích hoạt:** Thực thi lệnh triển khai phiên bản mới từ nhánh `main` trên máy chủ Azure Ubuntu.
- **Luồng chuẩn (Main Success Scenario):**
  1. Kịch bản `scripts/deploy_production.sh` kiểm tra trạng thái sống (`healthcheck`) của hai container `verischolar-postgres-dev` (`127.0.0.1:5432`) và `verischolar-redis-dev` (`127.0.0.1:6379`).
  2. Hệ thống đồng bộ môi trường Python bằng `uv sync --all-packages --frozen` và thực thi kiểm tra/nâng cấp lược đồ 16 bảng PostgreSQL (`init_db`).
  3. Kịch bản `scripts/deploy_web.sh` biên dịch gói giao diện React 19 ra thư mục tĩnh `/var/www/verischolar/web` và kiểm tra tính hợp lệ của cấu hình Nginx (`nginx -t`) với toàn bộ 5 tuyến SSE đã tắt bộ đệm.
  4. Hệ thống khởi động lại dịch vụ `verischolar-api.service` (hoặc container API gắn ổ đĩa `/app/data/cas`) và gọi `GET /health` để xác nhận trạng thái `200 OK`.
- **Kết quả đầu ra (Postconditions):** Phiên bản mới phục vụ người dùng qua HTTPS mà không làm mất dữ liệu bài báo PDF trong kho CAS hoặc dữ liệu học giả trong PostgreSQL.
- **Luồng ngoại lệ (Exception Flows):**
  - *3a. Lỗi biên dịch giao diện hoặc cấu hình Nginx không hợp lệ:* Kịch bản dừng trước khi chép đè thư mục `/var/www/verischolar/web`, giữ nguyên phiên bản giao diện đang chạy ổn định.
  - *4a. API không phản hồi `/health` sau khi khởi động lại:* Hệ thống ghi nhật ký lỗi ra `journalctl -u verischolar-api` và kích hoạt cảnh báo tới quản trị viên theo cấu hình `PRD-07`.

---

### UC-08.3: Thực thi Bộ Thực nghiệm Định lượng phục vụ Đồ án Tốt nghiệp (Thesis Evaluation Benchmarking)
- **Tác nhân:** Tác giả Đồ án (`Thesis Author`).
- **Điều kiện tiên quyết:** Hệ thống đã nạp dữ liệu mẫu thông qua `scripts/dev/seed.py` và kết nối thành công với PostgreSQL `pgvector`, Redis 7 và Langfuse Cloud.
- **Sự kiện kích hoạt:** Tác giả chạy bộ kiểm thử và kịch bản đo đạc thực nghiệm để trích xuất bảng số liệu cho Chương 4 của Báo cáo Đồ án Tốt nghiệp.
- **Luồng chuẩn (Main Success Scenario):**
  1. **Thực nghiệm E1 (Độ trễ & Thông lượng):** Hệ thống đo thời gian phản hồi token đầu tiên (TTFT) trên luồng SSE, thời gian nạp bài báo 2 tầng (Tier-1 Metadata vs. Tier-2 Deep Parse), tốc độ duyệt đồ thị 2-hop CTE và thời gian biên dịch LaTeX trên E2B.
  2. **Thực nghiệm E2 (Chất lượng AI & Minh chứng):** Hệ thống đánh giá độ chính xác truy xuất Hybrid RRF (`Recall@5`), độ khớp tọa độ hộp giới hạn (`Bounding Box IoU`) trên trang PDF và tỷ lệ tự sửa lỗi biên dịch LaTeX thành công trong tối đa 3 vòng lặp.
  3. **Thực nghiệm E3 (Độ phủ Kiểm thử & Kỷ luật Kiến trúc):** Hệ thống tổng hợp kết quả vượt qua 4 Cổng Xác Minh Bắt Buộc (`ruff`, `pytest`, `vitest`, `vite build`) và bảng kiểm tra ranh giới Lục giác.
- **Kết quả đầu ra (Postconditions):** Thu được bộ bảng biểu số liệu thực nghiệm khách quan, đối chiếu trực tiếp với các mục tiêu SLA đã cam kết để đưa vào báo cáo và slide bảo vệ đồ án.
- **Luồng ngoại lệ (Exception Flows):**
  - *1a. Chỉ số độ trễ vượt ngưỡng SLA mục tiêu:* Hệ thống truy vết span tương ứng trên Langfuse (`PRD-07`) để xác định nút cổ chai (DB index, mạng ngoại vi hay LLM token) và ghi nhận phân tích nguyên nhân vào báo cáo.

---

### UC-08.4: Sao lưu & Phục hồi Dữ liệu Bền vững trên Azure Ubuntu (Persistent CAS & DB Snapshot)
- **Tác nhân:** Kỹ sư Vận hành (`DevOps Engineer`).
- **Điều kiện tiên quyết:** Container `verischolar-postgres-dev` đang hoạt động và thư mục lưu trữ PDF `/var/lib/verischolar/cas` đã được gắn kết trên ổ đĩa máy chủ Azure.
- **Sự kiện kích hoạt:** Trước mỗi đợt nâng cấp lớn hoặc trước buổi bảo vệ Đồ án Tốt nghiệp.
- **Luồng chuẩn (Main Success Scenario):**
  1. Kỹ sư thực thi lệnh kết xuất bản sao cơ sở dữ liệu `pg_dump -Fc` từ container PostgreSQL ra tệp nén `.dump` có gắn nhãn thời gian.
  2. Hệ thống đồng bộ và kiểm tra toàn vẹn mã băm SHA-256 của toàn bộ tệp PDF trong thư mục `/var/lib/verischolar/cas` đối chiếu với bảng `document_storage_blobs`.
  3. Khi cần khôi phục hoặc dựng môi trường demo ngoại tuyến nhanh, kỹ sư chạy `scripts/dev/seed.py` để nạp lại bộ 3 bài báo khoa học kinh điển, phiên đọc mẫu và mạng tri thức 4 thực thể trong `< 5 giây`.
- **Kết quả đầu ra (Postconditions):** Môi trường demo bảo vệ đồ án luôn có sẵn dữ liệu chuẩn xác 100% ngay cả khi mạng Internet hội trường chập chờn.
- **Luồng ngoại lệ (Exception Flows):**
  - *2a. Phát hiện tệp PDF trên đĩa bị thiếu so với bản ghi DB:* Kịch bản `seed.py` tự động tái tạo tệp từ thư mục `data/papers/` theo đúng mã băm SHA-256.

---

## 4. Quy Tắc Nghiệp Vụ & Ràng Buộc Phi Chức Năng (Business Rules & NFRs)

### 4.1. Quy tắc Nghiệp vụ & Bảo mật Hạ tầng
- **BR-DEP-01 (Cô lập Cổng Cơ sở dữ liệu Nội bộ):** Trên máy chủ Azure Ubuntu VM, cổng PostgreSQL (`5432`) và Redis (`6379`) bắt buộc chỉ lắng nghe trên giao diện loopback `127.0.0.1` hoặc mạng nội bộ Docker (`verischolar-net`); tuyệt đối cấm mở trực tiếp ra Internet công cộng.
- **BR-DEP-02 (Bất biến Không Bộ Đệm cho 5 Tuyến SSE):** Cấu hình Nginx bắt buộc tắt bộ đệm (`proxy_buffering off; proxy_cache off; X-Accel-Buffering: no`) cho cả 5 đường dẫn streaming: `sessions/.*/(chat|messages|messages:stream|context-table:stream)`, `documents/.*/summary:stream`, `library/graph:query`, và `drafts/.*/chat:stream`.
- **BR-DEP-03 (Bền vững Kho Lưu trữ CAS):** Thư mục lưu trữ tệp PDF định danh theo băm SHA-256 (`data/cas` hoặc `/var/lib/verischolar/cas`) phải được gắn kết (mount) trên ổ đĩa bền vững của máy chủ Azure, tách biệt khỏi vòng đời tạm thời của container.
- **BR-DEP-04 (Đồng bộ Kịch bản CD & Kiểm thử Cơ học):** Mọi kịch bản triển khai được tham chiếu trong `.github/workflows/cd.yml` (`scripts/deploy_production.sh`, `scripts/deploy_web.sh`) phải tồn tại thực tế, có quyền thực thi (`chmod +x`) và được kiểm tra tự động trong `test_architecture_boundary.py`.

### 4.2. Bảng Chỉ Tiêu Nghiệm Thu Thực Nghiệm Đồ Án (Thesis Acceptance SLA Matrix)

| Nhóm thực nghiệm | Chỉ số đo lường cốt lõi | Ngưỡng nghiệm thu bắt buộc | Phân hệ liên đới |
| :--- | :--- | :--- | :--- |
| **E1: Độ trễ Streaming & Xử lý** | Thời gian phản hồi token đầu tiên (SSE TTFT) | **P50 $< 800\text{ms}$, P95 $< 1500\text{ms}$** | `PRD-03`, `PRD-04`, `PRD-05`, `PRD-06` |
| **E1: Nạp dữ liệu 2 tầng** | Tier-1 Metadata vs. Tier-2 Full PDF Parse | **Tier-1 $< 500\text{ms}$; Tier-2 $< 15\text{s}$** | `PRD-02`, `PRD-04` |
| **E1: Truy vấn Đồ thị & Biên dịch** | 2-Hop GraphRAG CTE & E2B LaTeX Compile | **Graph CTE $< 50\text{ms}$; E2B $< 5.0\text{s}$** | `PRD-05`, `PRD-06` |
| **E2: Chất lượng Truy xuất & Minh chứng** | Hybrid RRF `Recall@5` & `Bounding Box IoU` | **`Recall@5 >= 0.85`; `IoU >= 0.85`** | `PRD-03`, `PRD-05` |
| **E2: Tự sửa lỗi Biên dịch LaTeX** | Tỷ lệ tự sửa lỗi thành công ($\le 3$ vòng lặp) | **$\ge 90\%$** trên tập lỗi cú pháp chuẩn | `PRD-06` |
| **E3: Kỷ luật Kiểm thử Tự động** | 4 Cổng Xác Minh (`ruff`, `pytest`, `vitest`, `build`) | **100% Pass (Exit Code `0`)** | Toàn bộ Monorepo |
