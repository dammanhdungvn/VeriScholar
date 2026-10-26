# 🛠️ VeriScholar Operations & Maintenance Scripts

Thư mục `scripts/` chứa các kịch bản khởi tạo môi trường phát triển, kiểm định chất lượng và triển khai vận hành cho hệ thống **VeriScholar MVP**:

| Kịch bản | Mục đích | Cách chạy |
| :--- | :--- | :--- |
| [`scripts/dev/setup.sh`](./dev/setup.sh) | Thiết lập toàn diện môi trường sau khi `git clone`/`git pull` (tạo `.env` + symlink `apps/api/.env`, cài `uv`/`pnpm`, bật Docker `postgres`/`redis`, khởi tạo 18 bảng DB, gắn Git `pre-push` hook; thêm `--start` để chạy luôn Web & API). | `make setup` hoặc `make dev` |
| [`scripts/dev/verify.sh`](./dev/verify.sh) | Chạy tuần tự 4 Cổng xác minh bắt buộc (`ruff`, `pytest`, `vitest`, `vite build`) trước khi commit/push. | `make verify` |
| [`scripts/deploy_production.sh`](./deploy_production.sh) | Triển khai tự động Zero-Downtime lên máy chủ Production (chạy DB migration, build Web UI, reload Nginx & `verischolar-api.service`, kiểm tra `/health`). | `bash scripts/deploy_production.sh` |
| [`scripts/deploy_web.sh`](./deploy_web.sh) | Build và đồng bộ nhanh gói giao diện tĩnh `apps/web/dist` sang `/var/www/verischolar/web` và reload Nginx. | `bash scripts/deploy_web.sh` |
| [`scripts/purge_all.py`](./purge_all.py) | Dọn dẹp toàn bộ tài liệu thử nghiệm trên cơ sở dữ liệu và CAS Storage thông qua REST API (`DELETE /api/v1/documents/{id}`). | `uv run python scripts/purge_all.py` |
