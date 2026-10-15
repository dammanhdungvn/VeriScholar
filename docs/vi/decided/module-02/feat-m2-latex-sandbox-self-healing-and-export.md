# Module 2: Linter Cú Pháp, Sandbox Tự Vá Lỗi & Xuất Gói Nộp Bài Học Thuật

## 1. Giới thiệu
Biên dịch tài liệu khoa học LaTeX đòi hỏi khả năng xử lý lỗi cú pháp tự động mà không làm treo tiến trình máy chủ hoặc rò rỉ mã thực thi độc hại. Module 2 triển khai mô hình phễu 2 tầng:
1. **Tầng 1 (Fast AST Linter):** Phát hiện lỗi tĩnh (ngoặc nhọn, môi trường, gạch dưới không escape) dưới 100ms.
2. **Tầng 2 (Hardened Sandbox Compiler):** Biên dịch với cờ `--no-shell-escape`, timeout 15s và PyMuPDF fallback.
3. **Agentic Self-Healing Loop:** Vòng lặp N=3 lần thử tự vá lỗi có bộ nhớ chống lặp vòng tròn (Anti-Oscillation Patching Memory).
4. **Camera-Ready Academic Submission Bundle:** Đóng gói 1-click ra tệp `.zip` đạt chuẩn nộp bài quốc tế (IEEE, ACM, Springer, arXiv).

---

## 2. Fast AST Linter (`FastLatexAstLinter`)
- Vị trí: `packages/core/src/core/services/latex_linter.py`
- Tốc độ thực thi: < 100ms trong bộ nhớ (pure Python AST scanning, không cần I/O tiến trình con).
- Quy tắc phát hiện:
  - `ENV_MISMATCH`: Khối `\begin{env}` và `\end{env}` không khớp hoặc mở mà không đóng.
  - `UNCLOSED_BRACE`: Ngoặc nhọn `{` mở mà thiếu `}` tương ứng hoặc ngược lại.
  - `UNESCAPED_UNDERSCORE`: Ký tự gạch dưới `_` nằm trong văn bản thường ngoài chế độ toán học `$..$`.

---

## 3. Sandboxed Compiler & Fallback (`SandboxedLatexCompiler`)
- Vị trí: `packages/core/src/core/services/latex_compiler.py`
- Rào chắn an ninh (Hardening):
  - Tham số thực thi bắt buộc: `--no-shell-escape`, `-interaction=nonstopmode`.
  - Cắt cứng tiến trình: Timeout 15 giây chống treo vô hạn (Denial of Service).
  - Tự động dọn dẹp thư mục tạm sau khi kết thúc.
- Fallback không phụ thuộc OS: Nếu môi trường chạy (ví dụ dev container) chưa cài đặt TeXLive/Tectonic, compiler tự động kích hoạt bộ sinh PDF vector dự phòng thông qua PyMuPDF (`fitz`), tạo ra luồng byte `%PDF-1.4` hợp lệ 100% để hiển thị mượt mà trên PDF canvas của trình duyệt.

---

## 4. Agentic Self-Healing Loop (`AgenticLatexHealer`)
- Vị trí: `packages/core/src/core/services/latex_healer.py`
- Giới hạn lặp: Tối đa $N = 3$ lần thử.
- **Bộ nhớ Chống Lặp Vòng Tròn (Anti-Oscillation Memory):**
  - Lưu trữ băm SHA-256 của từng phiên bản mã nguồn đã thử nghiệm (`patch_history`).
  - Nếu bản vá mới sinh ra mã nguồn trùng lặp với phiên bản đã gây lỗi ở các bước lặp trước, healer tự động kích hoạt No-Rollback Constraint và chuyển sang phương án vá thay thế.
- **Suy thoái êm dịu (Graceful Fallback):** Nếu sau 3 lần thử vẫn còn lỗi cú pháp phức tạp, hệ thống trả về danh sách lỗi kèm dòng, cột và `suggested_fix` để người dùng can thiệp thủ công trên trình soạn thảo.

---

## 5. Xuất Gói Nộp Bài Học Thuật (.zip Bundle)
- **Route:** `POST /api/v1/drafts/{id}:export-bundle` (hỗ trợ alias `POST /api/v1/drafts/{id}/export-bundle` và `GET /api/v1/drafts/{id}/export-bundle`)
- **Nội dung gói nén ZIP:**
  - `main.tex` (hoặc `main.md`): Mã nguồn tài liệu nghiên cứu hoàn chỉnh.
  - `references.bib`: Toàn bộ các trích dẫn `\cite{...}` được bóc tách và tạo mục BibTeX tự động chuẩn học thuật.
  - `preview.pdf`: File PDF đã biên dịch chất lượng in ấn.
  - `figures/`: Thư mục chứa hình ảnh minh họa (.gitkeep).
  - `README.txt`: Siêu dữ liệu tác giả, ngày giờ xuất bản và hướng dẫn dòng lệnh tái lập với `pdflatex` / `bibtex`.
- **Response Headers:**
  - `Content-Type: application/zip`
  - `Content-Disposition: attachment; filename="draft_{id[:8]}_bundle.zip"`
