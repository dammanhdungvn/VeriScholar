# Kế Hoạch Thực Hiện: Chuẩn Hóa Ngôn Từ Kỹ Thuật Học Thuật & Thuật Ngữ BYOK Trong Luận Văn (Academic Terminology Radical Polish)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuẩn hóa toàn bộ thuật ngữ chuyên ngành trong luận văn tốt nghiệp VeriScholar, loại bỏ triệt để các cụm từ dịch gượng gạo ("Két an toàn khóa cá nhân", "cô lập hạt nhân"), diễn giải chuẩn mực quốc tế cho Bring Your Own Key (BYOK), bảo đảm văn phong khoa học máy tính chuẩn mực trên Mục lục và toàn văn báo cáo.

**Architecture:** Sử dụng phương pháp kiểm thử hồi quy hướng kiểm thử (TDD) để khóa cứng bộ từ khóa cấm ("Két an toàn", "két khóa", "cô lập hạt nhân"), cập nhật đồng bộ từ định nghĩa từ viết tắt, tiêu đề phân mục, nội dung phân tích bảo mật đến nhãn sơ đồ kiến trúc, sau đó biên dịch XeLaTeX tái tạo toàn bộ tệp Mục lục (`main.toc`) và xác minh bằng 4 Verification Gates.

**Tech Stack:** XeLaTeX, Python 3.12, Pytest, Pydantic, FastAPI, React 19.

**Spec:** [`../specs/2026-11-03-thesis-terminology-and-academic-language-refinement-design.md`](../specs/2026-11-03-thesis-terminology-and-academic-language-refinement-design.md)

---

## Global Constraints

- **Quy chuẩn Markdown & Liên kết tương đối (Rule 5):** Tuyệt đối cấm sử dụng URL tuyệt đối `file://` trong toàn bộ tài liệu Markdown. Mọi liên kết tham chiếu phải dùng đường dẫn tương đối.
- **Quy chuẩn ngôn từ tối giản & chuẩn học thuật (Rule 6):** Tuyệt đối cấm sử dụng các từ ngữ dịch máy thô ráp, đồ vật gia dụng/ngân hàng ("két an toàn", "két khóa") hoặc nhầm lẫn vật lý nguyên tử ("cô lập hạt nhân" thay vì "cô lập mức nhân hệ điều hành").
- **Thuật ngữ viết tắt quốc tế:** Đối với BYOK, phải diễn giải rõ ràng tiếng Anh `Bring Your Own Key` cùng khái niệm tiếng Việt học thuật `Mô hình quản lý khóa người dùng tự cấp`, sau đó đính kèm ký hiệu `(BYOK)` trên Mục lục và tiêu đề bài.
- **Bốn Cổng Xác Minh Bắt Buộc (The 4 Verification Gates):** Trước khi hoàn thành kế hoạch, bắt buộc 100% exit code 0 cho `ruff`, `pytest`, `npm test`, `npm build`.
- **Đồng bộ VPS tự động sau mỗi commit (Rule 7):** Sau mỗi commit git thành công, chạy `bash scripts/deploy_to_vps.sh --fast`.

---

## Review Focus

1. **Triệt tiêu lỗi "Két an toàn" trên Mục lục và văn bản:** Xác nhận tiêu đề Mục 2.5.4 hiển thị chuẩn xác `2.5.4 Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK) và chuẩn mã hóa AES-256-GCM`.
2. **Triệt tiêu lỗi "Cô lập hạt nhân":** Xác nhận Mục 2.5.3 và Hình 2-4 không còn bất kỳ chữ "hạt nhân" nào, chuyển thành "cô lập cấp hệ điều hành" và "cô lập cấp nhân".
3. **Đồng bộ toàn bộ các chương:** Quét tự động xác nhận số lượng từ cấm xuất hiện trong `report-datn/chapters/` đạt chính xác bằng **0**.
4. **Tính nhất quán Danh mục viết tắt:** Bổ sung mục từ `BYOK` và chuẩn hóa giải nghĩa `AES-GCM` trong `danh_muc_viet_tat.tex`.
5. **Độ ổn định biên dịch XeLaTeX:** Biên dịch tài liệu không làm thay đổi ngân sách số trang (chương 1 bắt đầu tại trang 1, ngân sách trang chuẩn mực).

---

## Task 1: Thiết Lập Test Hồi Quy TDD Khóa Cứng Thuật Ngữ Học Thuật

**Files:**
- Create: `tests/test_thesis_academic_terminology.py`

**Interfaces:**
- Consumes: Toàn bộ các tệp `.tex` trong `report-datn/chapters/` và `report-datn/frontmatter/`.
- Produces: Test tự động kiểm tra sự vắng mặt của các từ khóa cấm và sự hiện diện của các tiêu đề học thuật chuẩn hóa.

- [x] **Step 1: Viết test đỏ `test_thesis_academic_terminology.py`**
- [x] **Step 2: Chạy test để xác nhận test đỏ (RED)**

---

## Task 2: Chuẩn Hóa Ngôn Từ Học Thuật Chương 2 (`2_5_agentic_react.tex`)

**Files:**
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex:35-140`

**Interfaces:**
- Consumes: Tiêu đề Mục 2.5.3, Mục 2.5.4, nhãn Hình 2-4.
- Produces: Ngôn từ học thuật chuẩn xác, thay "cô lập hạt nhân" bằng "cô lập cấp hệ điều hành / cấp nhân", thay "Két an toàn khóa cá nhân BYOK" bằng "Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK)".

- [x] **Step 1: Cập nhật Mục 2.5.3**
- [x] **Step 2: Cập nhật Mục 2.5.4**
- [x] **Step 3: Chạy test kiểm tra tiến độ**
- [x] **Step 4: Commit và đồng bộ VPS**

---

## Task 3: Chuẩn Hóa Đồng Bộ Toàn Bộ Các Chương 1, 3, Kết Luận & Bổ Sung Danh Mục Viết Tắt

**Files:**
- Modify: `report-datn/chapters/ch1/1_3_muc_tieu.tex:17`
- Modify: `report-datn/chapters/ch3/3_3_kien_truc.tex:83`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:291`
- Modify: `report-datn/chapters/ket_luan.tex:13`
- Modify: `report-datn/frontmatter/danh_muc_viet_tat.tex:10-35`

**Interfaces:**
- Consumes: Toàn bộ các vị trí còn tồn đọng chữ "két khóa", "két an toàn".
- Produces: Tài liệu thuần nhất ngôn ngữ học thuật, bổ sung mục từ viết tắt BYOK.

- [x] **Step 1: Cập nhật Chương 1 (`1_3_muc_tieu.tex:17`)**
- [x] **Step 2: Cập nhật Chương 3 (`3_3_kien_truc.tex:83` & `3_6_thiet_ke_csdl.tex:291`)**
- [x] **Step 3: Cập nhật Chương Kết luận (`ket_luan.tex:13`)**
- [x] **Step 4: Cập nhật Danh mục từ viết tắt (`danh_muc_viet_tat.tex`)**
- [x] **Step 5: Chạy test TDD xác nhận GREEN 100%**
- [x] **Step 6: Commit và đồng bộ VPS**

---

## Task 4: Biên Dịch XeLaTeX Tái Tạo Mục Lục, Kiểm Định Bốn Cổng & Xuất Bản

**Files:**
- Modify: `report-datn/main.toc` (sinh tự động)
- Modify: `report-datn/main.pdf` (sinh tự động)

**Interfaces:**
- Consumes: Toàn bộ mã nguồn LaTeX đã chuẩn hóa.
- Produces: `report-datn/main.pdf` với Mục lục hoàn chỉnh, hiển thị chuẩn `2.5.4 Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK)...`, 100% test xanh.

- [x] **Step 1: Biên dịch XeLaTeX 2 lần trong thư mục `report-datn`**
- [x] **Step 2: Kiểm tra trực quan nội dung Mục lục trong PDF**
- [x] **Step 3: Chạy toàn bộ 4 Verification Gates**
- [x] **Step 4: Commit và đồng bộ VPS**
