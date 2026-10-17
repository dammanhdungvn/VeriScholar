# Phân Hệ 04: Vận Hành Sản Xuất, CI/CD & Hạ Tầng (Operations, CI/CD & Infrastructure)

Phân hệ này chứa toàn bộ các hướng dẫn kỹ thuật về đường ống Tích hợp Liên tục (CI), Triển khai Liên tục (CD), cấu hình hạ tầng Docker Enterprise On-Premise, máy chủ web Nginx, dịch vụ hệ thống Systemd, và hệ thống nhật ký quan sát của nền tảng **VeriScholar**.

---

## 📑 DANH MỤC TÀI LIỆU TRONG PHÂN HỆ

1. **[Đường Ống Tích Hợp Liên Tục CI & 9 Chốt Chặn Chất Lượng (ci-quality-gates-guide.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/04-operations-and-cicd/ci-quality-gates-guide.md):**  
   Cấu hình `.github/workflows/ci.yml`, kiểm soát ranh giới lục giác, quét rò rỉ mã khóa Gitleaks, kiểm tra cú pháp Ruff/Oxlint, kiểm thử độ phủ Pytest, kiểm thử giao diện Vitest (378 tests) và xác thực hạ tầng Docker Buildx.

2. **[Đường Ống Triển Khai Liên Tục CD & Vận Hành Zero-Downtime (cd-and-production-operations.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/04-operations-and-cicd/cd-and-production-operations.md):**  
   Kịch bản triển khai tự động `scripts/deploy_production.sh`, di trú CSDL an toàn `init_db.py`, cấu hình máy chủ Nginx SSL, quản lý dịch vụ `verischolar-api.service` qua Systemd, thăm dò sức khỏe tự động và cơ chế Auto-Rollback khi gặp sự cố.

3. **[Hướng Dẫn Hạ Tầng Docker Enterprise On-Premise (docker-enterprise-guide.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/04-operations-and-cicd/docker-enterprise-guide.md):**  
   Cấu hình cụm dịch vụ cô lập `deploy/docker-compose.enterprise.yml`, bộ cài đặt tự động `scripts/bootstrap_enterprise.sh`, tối ưu hóa bể kết nối PgBouncer, và quản trị dữ liệu vector trong PostgreSQL 16.

4. **[Hệ Thống Nhật Ký Có Cấu Trúc & Đo Lường AI (logging-and-observability.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/04-operations-and-cicd/logging-and-observability.md):**  
   Chuẩn Structlog JSON, PureASGITracingMiddleware, theo dõi `x-request-id`, bọc lọc PII nhạy cảm, và đo lường chi phí suy luận LLM qua Langfuse SDK.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar Enterprise.*
