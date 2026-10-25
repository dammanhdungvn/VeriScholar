# 🛠️ VeriScholar Operations & Maintenance Scripts

Thư mục `scripts/` chứa các kịch bản triển khai và bảo trì vận hành cho hệ thống **VeriScholar MVP**:

| Kịch bản | Mục đích | Cách chạy |
| :--- | :--- | :--- |
| `scripts/deploy_production.sh` | Triển khai tự động Zero-Downtime lên máy chủ Production (chạy DB migration, build Web UI, reload Nginx & `verischolar-api.service`, kiểm tra `/health`). | `bash scripts/deploy_production.sh` |
| `scripts/deploy_web.sh` | Build và đồng bộ nhanh gói giao diện tĩnh `apps/web/dist` sang `/var/www/verischolar/web` và reload Nginx. | `bash scripts/deploy_web.sh` |
| `scripts/purge_all.py` | Dọn dẹp toàn bộ tài liệu thử nghiệm trên cơ sở dữ liệu và CAS Storage thông qua REST API (`DELETE /api/v1/documents/{id}`). | `uv run python scripts/purge_all.py` |
