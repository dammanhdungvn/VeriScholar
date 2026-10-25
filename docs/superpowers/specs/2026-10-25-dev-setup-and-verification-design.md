# Thiết Kế Quy Trình Setup Tự Động & Cổng Kiểm Định Trước Commit/Push (Dev Setup & Pre-Push Verification)

> **Ngày tạo:** 2026-10-25
> **Phân loại quy mô:** Thay đổi nhỏ (Small Change — Short Design)
> **Trạng thái:** Chờ phê duyệt (Pending Approval)

---

## 1. Mục Đích & Lý Do (Intent & Why)
Giúp bất kỳ thành viên nào khi `git clone` hoặc `git pull` mã nguồn VeriScholar về máy mới chỉ cần chạy **1 lệnh duy nhất** là hoàn tất cài đặt thư viện, cấu hình môi trường, bật Docker (`postgres` + `redis`), khởi tạo đủ 18 bảng CSDL và chạy ứng dụng; đồng thời thiết lập chốt chặn tự động chạy 4 Cổng xác minh trước khi `git push` để đồng bộ 100% với pipeline CI trên GitHub Actions.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Phản Mục Tiêu (Goals, Non-Goals & Anti-Goals)
- **Goals (Mục tiêu):**
  - Tự động hóa trọn vẹn quy trình onboarding và cập nhật sau `git pull` qua [`scripts/dev/setup.sh`](../../../scripts/dev/setup.sh).
  - Cung cấp kịch bản kiểm định cục bộ `scripts/dev/verify.sh` và tự động gắn vào `.git/hooks/pre-push` để đảm bảo 4 Cổng kiểm định (`ruff`, `pytest`, `vitest`, `vite build`) đạt 100% trước khi đẩy code lên GitHub.
  - Cung cấp `Makefile` ở thư mục gốc với các lệnh trực quan: `make setup`, `make dev`, `make verify`.
- **Non-Goals (Phi mục tiêu):**
  - Không thay đổi cấu trúc 2-Tier hiện có của [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) (ngoài việc bổ sung kiểm tra cú pháp cho `scripts/dev/verify.sh`).
- **Anti-Goals (Phản mục tiêu):**
  - Không đóng gói cứng Backend và Frontend vào Docker trong môi trường dev gây chậm tốc độ hot-reload và TDD.
  - Không chặn thao tác `git commit` cục bộ bằng các bước build nặng gây gián đoạn nhịp làm việc TDD.

---

## 3. Ràng Buộc Kỹ Thuật (Constraints)
- Tuân thủ tuyệt đối quy tắc Single Source of Truth cho biến môi trường: chỉ giữ một file `.env` gốc và tạo relative symlink `apps/api/.env -> ../../.env` (theo [`AGENTS.md`](../../../AGENTS.md)).
- Tự động phát hiện quyền truy cập Docker socket (`/var/run/docker.sock`): nếu user hiện tại chưa thuộc nhóm `docker`, script tự động dùng `sudo docker compose up -d postgres redis`.
- Mọi liên kết trong tài liệu Markdown bắt buộc sử dụng đường dẫn tương đối (Zero `file:///` URLs).

---

## 4. Các Phương Án Đã Cân Nhắc (Approaches)

| Phương án | Mô tả | Đánh đổi (Trade-offs) | Quyết định |
| :--- | :--- | :--- | :--- |
| **Hướng 1: `scripts/dev/` + `Makefile` + Git `pre-push` hook** | Nâng cấp `setup.sh`, thêm `verify.sh` gắn vào `pre-push` hook và điều phối qua `Makefile`. | Chạy native cực nhanh, khớp sẵn với CI hiện có, không làm chậm `git commit`. | **Đã chọn** |
| **Hướng 2: Full Dockerized Dev** | Đưa cả `api` và `web` vào `docker-compose.yml`. | Nặng RAM, chậm hot-reload, bất tiện khi chạy `uv run pytest` trực tiếp. | Loại bỏ |
| **Hướng 3: `pre-commit` framework** | Chạy cả 4 cổng ở mỗi lần `git commit`. | Làm chậm mọi thao tác commit nhỏ trong chu trình Red-Green-Refactor TDD. | Loại bỏ |

---

## 5. Chi Tiết Thiết Kế Đã Chốt (Decided Architecture)

1. **Nâng cấp [`scripts/dev/setup.sh`](../../../scripts/dev/setup.sh):**
   - Kiểm tra Python 3.12+, Node.js 22+, `uv`, `pnpm`.
   - Khởi tạo `.env` từ `.env.example` (nếu chưa có) và đảm bảo relative symlink `apps/api/.env -> ../../.env`.
   - Cài đặt dependencies: `uv sync --all-packages` và `pnpm --prefix apps/web install`.
   - Khởi chạy hạ tầng CSDL: `docker compose up -d postgres redis` (tự động fallback sang `sudo docker compose` nếu thiếu quyền socket) và đợi healthcheck sẵn sàng.
   - Chạy миграция & bootstrap 18 bảng idempotent: `uv run python -m api.db.init_db`.
   - Cài đặt Git hook `.git/hooks/pre-push` trỏ vào `scripts/dev/verify.sh`.
   - Hỗ trợ cờ `--start` (hoặc qua `make dev`) để khởi chạy đồng thời Backend (`:8000`) và Frontend (`:5173`).

2. **Tạo mới `scripts/dev/verify.sh`:**
   - Thực thi tuần tự 4 Cổng xác minh bắt buộc:
     1. `uv run ruff check . && uv run ruff format --check .`
     2. `uv run pytest`
     3. `npm --prefix apps/web run test`
     4. `npm --prefix apps/web run build`
   - Trả về exit code `0` nếu toàn bộ vượt qua, hoặc dừng ngay lập tức (fail-fast) với thông báo rõ ràng.

3. **Tạo mới `Makefile` tại thư mục gốc:**
   - `make setup`: Chạy `bash scripts/dev/setup.sh`.
   - `make dev`: Chạy `bash scripts/dev/setup.sh --start`.
   - `make verify`: Chạy `bash scripts/dev/verify.sh`.

---

## 6. Phần Giao Cho Kỹ Sư Triển Khai (Left to the Builder)
- Xử lý tín hiệu `trap SIGINT SIGTERM` sạch sẽ khi chạy chế độ `--start` để khi bấm `Ctrl+C` sẽ tắt gọn cả tiến trình Backend lẫn Frontend.
- Đảm bảo [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) kiểm tra cú pháp `bash -n` cho cả `scripts/dev/setup.sh` và `scripts/dev/verify.sh`.
