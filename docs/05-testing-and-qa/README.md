# Phân Hệ 05: Chiến Lược Kiểm Thử & Đảm Bảo Chất Lượng (Testing & QA)

Phân hệ này định nghĩa khung kiểm thử và các cổng kiểm soát chất lượng tự động (Quality Gates) cho nền tảng **VeriScholar MVP**, đồng bộ trực tiếp với **[`docs/PRD/`](../PRD/00-overview-and-cleanup.md)**.

---

## 📑 DANH MỤC TÀI LIỆU TRONG PHÂN HỆ

1. **[Chiến Lược Kiểm Thử MVP (testing-strategy.md)](testing-strategy.md):**
   - **Backend & Core (`pytest`):** Khung kiểm thử chạy trên môi trường cô lập `ENVIRONMENT=test`, tắt telemetry mạng ngoài (`LANGFUSE_ENABLED=false`), hướng tới kiểm thử trên **PostgreSQL + `pgvector`** và bảo toàn ranh giới Hexagonal Architecture (`packages/core/src/core/domain`).
   - **Frontend (`vitest` + `jsdom`):** Khung kiểm thử React 19 + TypeScript sử dụng `apps/web/src/test/setup.ts` (polyfills cho `pdfjs-dist`, `matchMedia`, `ResizeObserver`).
   - **CI Quality Gates (`.github/workflows/ci.yml`):** Kiểm tra bảo mật Gitleaks, ranh giới Hexagonal, Ruff, Oxlint, TypeScript `tsc -b`, Vite Build và Docker Buildx.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar MVP.*
