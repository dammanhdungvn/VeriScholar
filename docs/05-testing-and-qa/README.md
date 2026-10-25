# Phân Hệ 05: Chiến Lược Kiểm Thử & Đảm Bảo Chất Lượng (Testing & QA)

Phân hệ này tập hợp toàn bộ các tài liệu về chiến lược kiểm thử đa tầng, quy chuẩn phòng ngừa hồi quy lỗi, và các chứng chỉ kiểm toán Cổng chất lượng (Quality Gate Sign-Off) của nền tảng **VeriScholar**, đồng bộ với **[`docs/PRD/`](../PRD/00-overview-and-cleanup.md)**.

---

## 📑 DANH MỤC TÀI LIỆU TRONG PHÂN HỆ

1. **[Chiến Lược Kiểm Thử Toàn Diện (testing-strategy.md)](testing-strategy.md):**  
   Chiến lược kiểm thử đa tầng bao phủ toàn diện:
   - **Backend Pytest Suite:** Kiểm thử đơn vị và tích hợp, kiểm thử bảo mật chuyên sâu (Chống SQL Injection, XSS Sanitization, Privilege Escalation Block, JWT Tampering Rejection, Auth Isolation, Concurrency SSE Stress).
   - **Frontend Vitest Suite:** 71 tệp kiểm thử đỗ 100% bao phủ React Components, Hooks (`useGoogleAuth`), Stores (`useDashboardStore`, `useReaderStore`, `useWritingStore`), và Modals (`AccountSettingsModal`, `DocumentLibraryModal`, `CitationGraphModal`).
   - **CI/CD Quality Gates:** Chặn đứng tự động mọi Pull Request không đạt chuẩn.

2. **[Chứng Chỉ Thẩm Định Quality Gate Mới Nhất (quality-gates-certification.md)](quality-gates-certification.md):**  
   Văn kiện kiểm toán độc lập chính thức từ Lead Architecture & Quality Gatekeeper chứng nhận chuẩn Production cho hệ sinh thái CI/CD và Tài liệu Kỹ thuật.

3. **[Bộ Ảnh Chụp Kiểm Thử AI & Đánh Giá API Ngoại Tuyến (api-eval-snapshots.md)](api-eval-snapshots.md):**  
   Tập hợp các bộ dữ liệu đánh giá chất lượng phản hồi LLM, độ chính xác Hybrid RAG + GraphRAG và các bộ mock response phục vụ kiểm thử snapshot tự động.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar MVP.*
