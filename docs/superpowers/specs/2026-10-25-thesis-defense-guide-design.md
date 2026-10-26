# Thiết Kế Sổ Tay Báo Cáo & Bảo Vệ Đồ Án Tốt Nghiệp (`docs/THESIS_DEFENSE_GUIDE.md`)

**Ngày lập:** 2026-10-25  
**Quy mô công việc:** Thay đổi nhỏ (Small change — bổ sung tài liệu tổng hợp phục vụ báo cáo Đồ án & liên kết chéo từ `docs/PRD/`).

---

## 1. Mục Đích & Lý Do (Intent & Why)
Chuyển hóa các quyết định kiến trúc, nghiệp vụ và kết quả kiểm thử thực nghiệm (từ Plan 00, Plan 01 và các Plan tiếp theo) thành ngôn ngữ trực quan, dễ hiểu kèm ví dụ thực tế và bộ câu hỏi phản biện Hội đồng, giúp tác giả đưa trực tiếp vào quyển **Báo cáo Đồ án Tốt nghiệp** và slide thuyết trình bảo vệ.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Ràng Buộc (Goals, Non-Goals & Constraints)
- **Mục tiêu (Goals):**
  - Tạo file trung tâm [`docs/THESIS_DEFENSE_GUIDE.md`](../../THESIS_DEFENSE_GUIDE.md) gồm đầy đủ nội dung của **Plan 00** (Nền tảng 18 bảng PostgreSQL + `pgvector`, kho lưu trữ chống trùng lặp SHA-256 CAS, Kiến trúc Lục giác) và **Plan 01** (Định danh Học giả, ORCID, Két sắt BYOK AES-256-GCM giải mã trên RAM, cơ chế Hybrid `.env` + BYOK, và Automatic Tracing trên Langfuse Cloud).
  - Bổ sung mục tham chiếu ngắn ở cuối [`docs/PRD/00-overview-and-cleanup.md`](../../PRD/00-overview-and-cleanup.md) và [`docs/PRD/01-auth-and-user.md`](../../PRD/01-auth-and-user.md) trỏ sang sổ tay này.
- **Phi mục tiêu (Non-Goals):** Không sửa đổi logic code sản xuất hay thay đổi đặc tả kỹ thuật trong `docs/specs/`.
- **Ràng buộc (Constraints):** Tuân thủ 100% Quy tắc số 5 trong [`AGENTS.md`](../../../AGENTS.md) — chỉ sử dụng đường dẫn tương đối (`./...`, `../...`) trong toàn bộ file Markdown, tuyệt đối không dùng `file://`.

---

## 3. Các Hướng Tiếp Cận Đã Cân Nhắc (Approaches)
1. **Hướng 1 (Đã chọn):** Tạo sổ tay tập trung `docs/THESIS_DEFENSE_GUIDE.md` chia theo từng chương (Chương 0, Chương 1, và mở rộng dần ở các Plan 02–09) kèm liên kết từ `docs/PRD/`. Ưu điểm: Tập trung tại một nơi duy nhất khi viết báo cáo và ôn phản biện, không làm loãng đặc tả kỹ thuật.
2. **Hướng 2:** Viết rải rác vào cuối từng file trong `docs/PRD/` và `docs/specs/`. Nhược điểm: Phải mở tra cứu qua lại hơn 18 file khi viết báo cáo tổng hợp.

---

## 4. Cấu Trúc Chi Tiết Mỗi Chương Trong `docs/THESIS_DEFENSE_GUIDE.md`
Mỗi phân hệ (Plan 00, Plan 01...) được trình bày thống nhất gồm 4 phần:
1. **Giải thích bình dân & Ví dụ đời thực:** Ẩn dụ trực quan (ví dụ: *50 sinh viên tải cùng 1 file PDF 20MB chỉ tốn 20MB ổ cứng nhờ dấu vân tay SHA-256*; *Két sắt AES-256-GCM chỉ mở khóa trên RAM*).
2. **Tại sao bắt buộc phải có & Thành phần nào có thể giản lược:** Phân tách rõ **Core (Bắt buộc phải có — bỏ đi sẽ sập luồng nào)** và **Optional/Hybrid (Tùy chọn nâng cao — mặc định lấy `.env` để không gây phiền cho người dùng mới)**.
3. **Bộ Câu hỏi & Câu trả lời Phản biện Hội đồng (Defense Q&A):** Các câu hỏi xoáy thường gặp của giảng viên chấm Đồ án và câu trả lời chuẩn xác có dẫn chứng kiến trúc.
4. **Bằng chứng Thực nghiệm Đã Chạy (Empirical Evidence):** Số lượng bài test tự động (`46/46 pytest`, `3/3 vitest`), kết quả gọi thực tế `OPENAI_API_KEY` (`gpt-5.4-mini`) và mã `Trace ID` / `Observation ID` đối chiếu trên **Langfuse Cloud (`https://jp.cloud.langfuse.com`)**.
