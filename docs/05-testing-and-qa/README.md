# Phân Hệ 05: Chiến Lược Kiểm Thử & Đảm Bảo Chất Lượng (Testing & QA)

Phân hệ này tập hợp toàn bộ các tài liệu về chiến lược kiểm thử đa tầng, quy chuẩn phòng ngừa hồi quy lỗi, phương pháp luận Eval-Driven Development (EDD), và các chứng chỉ kiểm toán Cổng chất lượng (Quality Gate Sign-Off) của nền tảng **VeriScholar**.

---

## 📑 DANH MỤC TÀI LIỆU TRONG PHÂN HỆ

1. **[Chiến Lược Kiểm Thử Toàn Diện Đạt Chuẩn Enterprise (testing-strategy.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/05-testing-and-qa/testing-strategy.md):**  
   Chiến lược kiểm thử đa tầng bao phủ toàn diện:
   - **Backend Pytest Suite:** 27 bài test tích hợp và kiểm thử bảo mật chuyên sâu (Chống SQL Injection, XSS Sanitization, Privilege Escalation Block, JWT Tampering Rejection, Auth Isolation, Concurrency SSE Stress).
   - **Frontend Vitest Suite:** 63 tệp kiểm thử, 378 bài test đỗ 100% bao phủ React Components, Hooks (`useGoogleAuth`), Stores, Modals (`ComparisonMatrixModal` 120 papers, `ScholarProfileModal`).
   - **Playwright E2E Testing:** Kịch bản kiểm thử giao diện thực tế đầu-cuối.
   - **CI/CD Quality Gates:** Chặn đứng tự động mọi Pull Request không đạt chuẩn.

2. **[Chứng Chỉ Thẩm Định Quality Gate Mới Nhất (quality-gates-certification.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/05-testing-and-qa/quality-gates-certification.md):**  
   Văn kiện kiểm toán độc lập chính thức từ Lead Architecture & Quality Gatekeeper chứng nhận 100/100 chuẩn Production cho toàn bộ hệ sinh thái CI/CD và Tài liệu Kỹ thuật.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar Enterprise.*
