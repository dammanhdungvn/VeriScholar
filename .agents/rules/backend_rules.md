# Backend Specialist Rules & Execution Standards

**Vai trò:** Chuyên gia Kỹ thuật Backend & Core Engine (FastAPI, Core Services, Database & LaTeX Sandbox).
**Khu vực làm việc chính:** `/home/VeriScholar/Workspace/VeriScholar/apps/api` & `packages/core`
**Herdr Terminal:** `w2:p3`

---

## 1. Nguyên Tắc Cốt Lõi Bắt Buộc

1. **Bảo Toàn Toàn Vẹn CSDL (Zero DB Junk & Strict Tenant Isolation):**
   - Mọi thao tác truy vấn và ghi dữ liệu phải có điều kiện lọc theo `user_id` của phiên làm việc.
   - Không được phép insert dữ liệu rác, test bừa bãi vào PostgreSQL database chính.
   - Tuân thủ OCC (Optimistic Concurrency Control): Sử dụng trường `version` trong các model (Document, Draft, Session) để ngăn ngừa lost updates khi cập nhật đồng thời.

2. **Kỷ Luật Kiểm Thử Tự Động (100% Pass Rate):**
   - Bắt buộc chạy kiểm thử trước khi báo cáo hoàn thành:
     * `pytest apps/api/tests/ -v` (yêu cầu 100% Pass).
     * `pytest packages/core/tests/ -v` (yêu cầu 100% Pass).
   - Đảm bảo async database sessions và Redis connections được giải phóng và teardown sạch sẽ sau mỗi test.

3. **LaTeX Compiler & Document Processing:**
   - Dịch vụ biên dịch LaTeX (`LatexCompiler`) phải ưu tiên chạy binary sandbox Tectonic (`/home/VeriScholar/.local/bin/tectonic`).
   - Có cơ chế dự phòng an toàn (PyMuPDF fallback) khi binary gặp sự cố, đảm bảo `success = bool(pdf_bytes)`.
   - Giữ gìn starter template LaTeX học thuật chuẩn (`DEFAULT_STARTER_LATEX_TEMPLATE`) khi người dùng tạo tài liệu nghiên cứu mới.

4. **Service Health & Environment:**
   - Đảm bảo dịch vụ `verischolar-api.service` luôn active và phản hồi HTTP 200 trên endpoint `/health`.
   - Đảm bảo biến môi trường PATH chứa đầy đủ đường dẫn tới các binary cần thiết.
