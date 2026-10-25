# Thiết Kế Kiến Trúc Triển Khai Azure Ubuntu, CI/CD & Khung Thực Nghiệm Đồ Án Tốt Nghiệp (`PRD-08`, `Spec-09`, `THESIS_OUTLINE_MAPPING`)

**Ngày thiết kế:** 2026-10-25  
**Trạng thái:** Chờ phê duyệt (Pending User Review)  
**Tài liệu tham chiếu:** [`../../PRD/00-overview-and-cleanup.md`](../../PRD/00-overview-and-cleanup.md), [`../../specs/00-foundation-architecture-and-db.md`](../../specs/00-foundation-architecture-and-db.md), [`../../specs/07-monitoring-and-langfuse-spec.md`](../../specs/07-monitoring-and-langfuse-spec.md)

---

## 1. Mục Đích & Lý Do Cốt Lõi (Intent & The Why)

Người dùng đang phát triển nền tảng **VeriScholar MVP** song song với việc viết **Báo cáo Đồ án Tốt nghiệp Đại học (Ngành CNTT / Khoa học Máy tính)** và triển khai hệ thống thực tế trên máy chủ **Azure Ubuntu VM** để phục vụ chạy thật và demo trước Hội đồng bảo vệ đồ án.

Qua rà soát toàn bộ kho mã nguồn hiện tại:
1. Bộ 8 PRD (`00..07`) và 9 Spec (`00..08`) đã phủ kín phần Phân tích nghiệp vụ và Thiết kế phần mềm (đáp ứng Chương 1, 2, 3 của Đồ án).
2. Tuy nhiên, kho tài liệu và cấu hình hạ tầng đang thiếu 3 mảnh ghép bắt buộc cho **Chương 4 (Triển khai, Kiểm thử & Thực nghiệm Đánh giá)** và **Chương 5 (Kết luận)**:
   - **Hạ tầng Nginx & Docker trên Azure Ubuntu chưa đồng bộ với các API SSE mới:** File [`../../../deploy/nginx/production-host.conf`](../../../deploy/nginx/production-host.conf) và [`../../../deploy/nginx/verischolar.conf`](../../../deploy/nginx/verischolar.conf) mới chỉ tắt buffering (`proxy_buffering off`) cho `sessions/.*/(chat|messages)` và `documents/.*/summary:stream`, bỏ sót 3 luồng SSE quan trọng của MVP là `sessions/.*/context-table:stream`, `library/graph:query` và `drafts/.*/chat:stream`.
   - **Pipeline CD bị đứt gãy:** File [`../../../.github/workflows/cd.yml`](../../../.github/workflows/cd.yml) đang gọi tới 2 script `scripts/deploy_production.sh` và `scripts/deploy_web.sh` đã bị xóa trong đợt dọn dẹp trước, đồng thời [`../../../deploy/Dockerfile.api`](../../../deploy/Dockerfile.api) chưa sử dụng `uv sync --frozen` và chưa khai báo ổ lưu trữ bền vững cho kho PDF CAS (`data/cas`).
   - **Thiếu Tài liệu Thực nghiệm Định lượng & Bản đồ Ánh xạ Đồ án:** Hội đồng chấm đồ án tốt nghiệp luôn yêu cầu bảng số liệu đánh giá định lượng (thời gian phản hồi TTFT, độ chính xác trích xuất Bounding Box & Hybrid RAG Recall@K, tỷ lệ biên dịch LaTeX tự sửa lỗi trên E2B) và sơ đồ ánh xạ từ tài liệu kỹ thuật sang bố cục báo cáo.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Phản Mục Tiêu (Goals, Non-Goals & Anti-Goals)

### 2.1. Mục Tiêu (Goals)
1. **Bổ sung `docs/PRD/08-deployment-and-system-evaluation.md` (140–195 dòng):** Đặc tả yêu cầu nghiệp vụ vận hành hệ thống trên Azure Ubuntu VM, quy trình CI/CD tự động hóa, và bộ chỉ tiêu nghiệm thu thực nghiệm phục vụ bảo vệ Đồ án Tốt nghiệp.
2. **Bổ sung `docs/specs/09-deployment-cicd-and-evaluation-spec.md`:** Đặc tả kỹ thuật chi tiết cấp Senior DevOps & QA gồm:
   - Sơ đồ kiến trúc triển khai vật lý (Deployment Diagram) trên **Azure Ubuntu VM** kết hợp Nginx Reverse Proxy (TLS 1.3 Let's Encrypt), Systemd / Docker Compose (`pgvector/pgvector:0.8.6-pg18`, `redis:7-alpine`), kho lưu trữ CAS trên đĩa (`data/cas`), và kết nối ra E2B Cloud / Langfuse Cloud.
   - Hợp đồng cấu hình Nginx tắt bộ đệm (`proxy_buffering off`) cho toàn bộ **5 luồng SSE** của hệ thống.
   - Quy trình CI/CD GitHub Actions (`ci.yml` & `cd.yml`) và kịch bản triển khai không gián đoạn (`scripts/deploy_production.sh`, `scripts/deploy_web.sh`).
   - **Khung Thực Nghiệm & Đánh Giá Định Lượng (Evaluation Benchmarks):** Quy định rõ 3 nhóm thực nghiệm có thể chạy lặp lại bằng script/pytest để lấy bảng số liệu đưa thẳng vào Chương Thực nghiệm của Đồ án:
     - *Thực nghiệm 1 (Hiệu năng & Độ trễ Streaming):* Đo TTFT ($< 1.5\text{s}$), Tier-1/Tier-2 Ingestion, truy vấn đệ quy 2-hop GraphRAG ($< 50\text{ms}$), và biên dịch E2B LaTeX ($< 5\text{s}$).
     - *Thực nghiệm 2 (Độ chính xác AI & Grounding):* Đo Recall@5 của Hybrid Search (`pgvector` HNSW + FTS RRF), độ khớp tọa độ Bounding Box (`IoU >= 0.85`), và tỷ lệ tự sửa lỗi biên dịch LaTeX thành công trong $\le 3$ vòng lặp ($\ge 90\%$).
     - *Thực nghiệm 3 (Ma trận Kiểm thử Tự động):* Tổng hợp kết quả 4 Cổng Xác Minh Bắt Buộc và kiểm thử ranh giới kiến trúc.
3. **Bổ sung `docs/THESIS_OUTLINE_MAPPING.md`:** Cẩm nang ánh xạ chi tiết từng chương/mục của Báo cáo Đồ án Tốt nghiệp (Chương 1 $\rightarrow$ Chương 5) sang đúng từng file PRD (`00..08`), Spec (`00..09`), biểu đồ Mermaid (Use Case, ERD 16 bảng, Sequence, Deployment) và thư mục code để sinh viên viết báo cáo song song với quá trình lập trình.
4. **Cập nhật [`../../README.md`](../../README.md) và đồng bộ hạ tầng [`../../../deploy/`](../../../deploy/Dockerfile.api), [`../../../.github/workflows/cd.yml`](../../../.github/workflows/cd.yml) kèm bài test cơ học trong [`../../../apps/api/tests/test_architecture_boundary.py`](../../../apps/api/tests/test_architecture_boundary.py).**

### 2.2. Phi Mục Tiêu (Non-Goals)
- Không triển khai cụm Kubernetes (K8s/EKS/AKS), Helm Charts hay kiến trúc Microservices đa máy chủ phức tạp vượt quá nhu cầu của 1 máy chủ Azure Ubuntu VM.
- Không dựng thêm hệ thống Prometheus/Grafana tự vận hành trên máy chủ (đã sử dụng Structlog + Langfuse Cloud + Sentry theo `PRD-07`/`Spec-07`).

### 2.3. Phản Mục Tiêu (Anti-Goals)
- Không làm phình đại hoặc phá vỡ giới hạn `120–210` dòng của các file PRD (`00..08`).
- Không để tồn tại bất kỳ script không tồn tại nào trong `.github/workflows/cd.yml` hoặc đường dẫn tương đối bị đứt trong `docs/`.

---

## 3. Các Phương Án Đã Cân Nhắc (Approaches Considered)

### Phương án 1 (Đã chọn): Tách Mô-đun Triển khai & Thực nghiệm Độc lập (`PRD-08`, `Spec-09`, `Plan-09`) + Bản đồ Đồ án (`docs/THESIS_OUTLINE_MAPPING.md`)
- **Mô tả:** Tạo mới `docs/PRD/08-deployment-and-system-evaluation.md`, `docs/specs/09-deployment-cicd-and-evaluation-spec.md`, `docs/THESIS_OUTLINE_MAPPING.md` và kế hoạch thực thi `docs/superpowers/plans/2026-10-25-09-deployment-cicd-and-evaluation.md`; đồng thời sửa trực tiếp các file cấu hình trong `deploy/`, `scripts/` và `.github/workflows/cd.yml`.
- **Đánh đổi:** Tăng thêm 1 cặp PRD/Spec (`08`/`09`), nhưng giữ nguyên tính cô đọng của toàn bộ các file hiện có và khớp 1-1 với Chương 4 (Triển khai & Thực nghiệm) của Đồ án Tốt nghiệp.

### Phương án 2 (Loại bỏ): Nhúng rải rác vào `Spec-00` và `Spec-07`
- **Mô tả:** Chèn mục triển khai Azure vào cuối `Spec-00` và mục thực nghiệm vào cuối `Spec-07`.
- **Lý do loại bỏ:** Làm `Spec-00` và `Spec-07` quá tải, gây khó khăn khi trích xuất tư liệu viết Chương Triển khai & Thực nghiệm của Đồ án.

---

## 4. Chi Tiết Kiến Trúc & Các Quyết Định Kỹ Thuật (How It Gets Built)

### 4.1. Quyết định từ Người dùng (User Decisions)
- **Môi trường máy chủ Production/Demo:** Sử dụng máy ảo **Azure Ubuntu VM** (Ubuntu 22.04/24.04 LTS).
- **Cấu trúc tài liệu:** Chọn **Phương án 1** (tách `PRD-08`, `Spec-09`, `Plan-09` và `docs/THESIS_OUTLINE_MAPPING.md`).
- **Quyền tự quyết chi tiết hạ tầng:** Giao cho Kiến trúc sư (Agent) quyết định cấu hình chuẩn cho Nginx, Docker, Systemd và CI/CD.

### 4.2. Quyết định Kỹ thuật Mặc định Hợp lý (Architect Calls)
1. **Mô hình Triển khai Lai (Hybrid Host-Nginx + Systemd API + Dockerized Data) và Toàn phần (Full Docker Compose) trên Azure Ubuntu:**
   - **Tầng Reverse Proxy & TLS (Host Nginx):** Sử dụng [`../../../deploy/nginx/production-host.conf`](../../../deploy/nginx/production-host.conf) lắng nghe cổng `80`/`443` (Let's Encrypt Certbot cho tên miền `verischolar.duckdns.org` hoặc IP/Domain tùy chỉnh qua biến môi trường), phục vụ trực tiếp gói tĩnh React 19 Vite (`apps/web/dist` tại `/var/www/verischolar/web`) và chuyển tiếp `/api/` về FastAPI (`127.0.0.1:8000`).
   - **Biểu thức chính quy Nginx Unbuffered SSE chuẩn hóa (áp dụng cho cả `production-host.conf` và `verischolar.conf`):**
     ```nginx
     location ~* ^/api/v1/(sessions/.*/(chat|messages|messages:stream|context-table:stream)|documents/.*/summary:stream|library/graph:query|drafts/.*/chat:stream) {
         proxy_pass http://127.0.0.1:8000; # hoặc http://api:8000 trong container
         proxy_http_version 1.1;
         proxy_buffering off;
         proxy_cache off;
         proxy_read_timeout 600s;
         add_header X-Accel-Buffering "no" always;
         proxy_set_header Connection "";
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto $scheme;
         chunked_transfer_encoding on;
     }
     ```
   - **Tầng Cơ sở dữ liệu & Cache:** Chạy qua [`../../../docker-compose.yml`](../../../docker-compose.yml) với `pgvector/pgvector:0.8.6-pg18` (ràng buộc `127.0.0.1:5432:5432`) và `redis:7-alpine` (`127.0.0.1:6379:6379`) để cô lập hoàn toàn cổng DB khỏi Internet công cộng trên Azure NSG.
   - **Tầng Ứng dụng FastAPI & Lưu trữ CAS:**
     - Cập nhật [`../../../deploy/Dockerfile.api`](../../../deploy/Dockerfile.api) sử dụng `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` và `uv sync --all-packages --frozen --no-dev` thay vì `pip install .`, khai báo `VOLUME ["/app/data/cas"]`.
     - Cung cấp đồng thời [`../../../deploy/systemd/verischolar-api.service`](../../../deploy/systemd/verischolar-api.service) để chạy trực tiếp bằng `.venv/bin/uvicorn` trên Azure Ubuntu VM (tiết kiệm RAM cho máy ảo sinh viên Azure for Students 4GB–8GB RAM).
2. **Khôi phục Kịch bản Triển khai Tự động (`scripts/deploy_production.sh` & `scripts/deploy_web.sh`):**
   - `scripts/deploy_web.sh`: Chạy `pnpm --dir apps/web install --frozen-lockfile && pnpm --dir apps/web build`, đồng bộ `apps/web/dist/` sang `/var/www/verischolar/web` (hoặc thư mục cấu hình qua `WEB_DEPLOY_ROOT`) và kiểm tra cú pháp `nginx -t`.
   - `scripts/deploy_production.sh`: Khởi động/kiểm tra container `postgres` & `redis`, chạy `uv sync --all-packages --frozen`, thực thi migration schema, gọi `scripts/deploy_web.sh`, khởi động lại `verischolar-api.service` và xác minh `curl -fsS http://127.0.0.1:8000/health`.
3. **Cấu trúc Bảng Ánh xạ Đồ án Tốt nghiệp (`docs/THESIS_OUTLINE_MAPPING.md`):**
   - Tổ chức theo chuẩn 5 Chương Đồ án Tốt nghiệp CNTT Việt Nam:
     - **Chương 1: Giới thiệu đề tài & Bài toán nghiên cứu** $\leftrightarrow$ `PRD-00`, `PRD-01..06` (Mục 1: Bối cảnh, Nỗi đau & Ma trận giá trị Before/After).
     - **Chương 2: Cơ sở lý thuyết & Công nghệ sử dụng** $\leftrightarrow$ `Spec-00` (Hexagonal, PostgreSQL `pgvector` HNSW), `Spec-03` (Hybrid RAG + RRF + SSE), `Spec-05` (4-Entity GraphRAG + Recursive CTE), `Spec-06` (LangGraph StateGraph + E2B Cloud Sandbox).
     - **Chương 3: Phân tích & Thiết kế hệ thống** $\leftrightarrow$ Bảng Tác nhân & Use Cases trong `PRD-01..07`, Lược đồ CSDL 16 bảng trong `Spec-00`, và các sơ đồ Sequence/State trong `Spec-01..07`.
     - **Chương 4: Cài đặt, Triển khai & Thực nghiệm Đánh giá** $\leftrightarrow$ `PRD-08`, `Spec-08` (Agent Harness), `Spec-09` (Triển khai Azure Ubuntu + Nginx + Bộ số liệu Thực nghiệm E1/E2/E3).
     - **Chương 5: Kết luận & Hướng phát triển** $\leftrightarrow$ Tổng kết đóng góp kỹ thuật và lộ trình mở rộng hậu MVP.

---

## 5. Phần Giao Cho Builder Trong Kế Hoạch Triển Khai (Left to the Builder)

1. Soạn thảo nội dung chi tiết cho `docs/PRD/08-deployment-and-system-evaluation.md` (tuân thủ nghiêm ngặt giới hạn `120–210` dòng và cấu trúc 4 mục chuẩn BA).
2. Soạn thảo nội dung chi tiết cho `docs/specs/09-deployment-cicd-and-evaluation-spec.md` và `docs/THESIS_OUTLINE_MAPPING.md`.
3. Cập nhật bảng điều hướng tại `docs/README.md` và `README.md`.
4. Cập nhật `deploy/nginx/production-host.conf`, `deploy/nginx/verischolar.conf`, `deploy/Dockerfile.api`, tạo `scripts/deploy_production.sh`, `scripts/deploy_web.sh`, và bổ sung bài kiểm thử cơ học trong `apps/api/tests/test_architecture_boundary.py`.
