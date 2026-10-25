# Phân Hệ 04: Vận Hành Sản Xuất, CI/CD & Quan Sát (Operations, CI/CD & Observability)

Phân hệ này chứa toàn bộ các hướng dẫn kỹ thuật về đường ống Tích hợp Liên tục (CI), Triển khai Liên tục (CD), máy chủ web Nginx, dịch vụ hệ thống Systemd, và hệ thống nhật ký quan sát 3 tầng (Structlog + Langfuse + Sentry/Webhook) của nền tảng **VeriScholar**, đồng bộ với **[`docs/PRD/07-monitoring-and-langfuse.md`](../PRD/07-monitoring-and-langfuse.md)**.

---

## 📑 DANH MỤC TÀI LIỆU TRONG PHÂN HỆ

1. **[Đường Ống Tích Hợp Liên Tục CI & Cổng Chất Lượng (ci-quality-gates-guide.md)](ci-quality-gates-guide.md):**  
   Cấu hình `.github/workflows/ci.yml`, kiểm soát ranh giới lục giác, quét rò rỉ mã khóa Gitleaks, kiểm tra cú pháp Ruff/Oxlint, kiểm thử độ phủ Pytest, kiểm thử giao diện Vitest và xác thực hạ tầng Docker.

2. **[Đường Ống Triển Khai Liên Tục CD & Vận Hành Zero-Downtime (cd-and-production-operations.md)](cd-and-production-operations.md):**  
   Quy trình triển khai tự động, di trú CSDL an toàn `init_db.py`, cấu hình máy chủ Nginx SSL, quản lý dịch vụ `verischolar-api.service` qua Systemd, thăm dò sức khỏe tự động và cơ chế Auto-Rollback khi gặp sự cố.

3. **[Hệ Thống Nhật Ký Có Cấu Trúc & Đo Lường AI (logging-and-observability.md)](logging-and-observability.md):**  
   Chuẩn Structlog JSON, `PureASGITracingMiddleware`, theo dõi `trace_id` (`x-request-id`), bọc lọc PII nhạy cảm, đo lường chi phí suy luận LLM qua Langfuse Cloud (`verischolar-dev` & `verischolar-prod`), và cảnh báo sự cố tức thời qua Sentry / Alert Webhook.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar MVP.*
