# PHÂN HỆ KHÔNG GIAN SOẠN THẢO AGENTIC OVERLEAF, LANGGRAPH AGENT & E2B SANDBOX
# (AGENTIC OVERLEAF WRITING WORKSPACE, DRAFTS CRUD, LANGGRAPH & E2B)

---

## 1. Mục Tiêu Phân Hệ
Biến quá trình viết báo cáo đồ án / bài báo khoa học bằng LaTeX trở nên tự động và liền mạch: người dùng chuyển thẳng từ phiên đọc sang không gian soạn thảo 3 cột kiểu Overleaf; tại đây **LangGraph Agent** có thể tự động viết và chỉnh sửa trực tiếp file `main.tex` / `references.bib`, tự động kéo kiến thức từ Kho Tri Thức GraphRAG, và tự động đóng gói kèm thư mục hình ảnh `figures/` đẩy lên **E2B Sandbox** để biên dịch ra PDF hoàn chỉnh (tự đọc log vá lỗi tối đa 3 lần nếu sai cú pháp).

---

## 2. Cầu Nối "Đọc Sang Viết" (Reading-to-Writing Bridge)

* Trên thanh công cụ của màn hình Phiên Đọc Sâu có nút **`[✍️ Bắt đầu viết bài từ phiên đọc này]`**.
* Khi người dùng bấm vào nút này:
  1. Hệ thống tự động tạo một Bản thảo mới (`Draft`) gắn với phiên đọc đó.
  2. Tự động khởi tạo sẵn nội dung file **`references.bib`** từ danh sách các bài báo đang có trong phiên đọc (kèm khóa trích dẫn chuẩn như `@article{vaswani2017attention, ...}`).
  3. Truyền danh sách `document_ids` của phiên đọc và các ghi chú (`notes`) người dùng đã lưu sang làm ngữ cảnh nền cho Agent Soạn thảo.

---

## 3. Quản Lý Bản Thảo & File Dự Án — Đầy Đủ Thao Tác CRUD (`drafts` & `draft_assets`)

### A. CRUD Bản thảo LaTeX (`drafts`)
1. **Tạo bản thảo mới (`POST /api/v1/drafts`):**
   * Tạo từ mẫu chuẩn (Template IEEE, ACM, Báo cáo Đồ án hoặc Bản trống) hoặc tạo từ nút Cầu nối Phiên đọc.
   * Mỗi bản thảo lưu trữ cả 2 nội dung văn bản cốt lõi: mã nguồn **`main.tex`** (`content`) và danh mục tài liệu tham khảo **`references.bib`** (`bib_content`).
2. **Xem danh sách & Chi tiết bản thảo (`GET /api/v1/drafts`, `GET /api/v1/drafts/{id}`):**
   * Liệt kê các bản thảo của người dùng kèm thời gian chỉnh sửa gần nhất.
3. **Lưu & Cập nhật bản thảo (`PUT /api/v1/drafts/{id}`, `PATCH /api/v1/drafts/{id}`):**
   * Cho phép đổi tên bản thảo (`title`), cập nhật nội dung `main.tex` và `references.bib` khi người dùng sửa tay hoặc khi Agent cập nhật.
4. **Xóa bản thảo (`DELETE /api/v1/drafts/{id}`):**
   * Xóa bản thảo và các file ảnh đính kèm của bản thảo đó (có xác nhận trước khi xóa).
5. **Biên dịch, Hoàn tác & Tải file kết quả (`POST /api/v1/drafts/{id}/compile`, `POST /api/v1/drafts/{id}:undo`, `GET /api/v1/drafts/{id}/preview.pdf`, `POST /api/v1/drafts/{id}:export-bundle`):**
   * Biên dịch tức thì bản thảo LaTeX trên E2B Sandbox, tự sửa lỗi tối đa 3 lần.
   * Hoàn tác 1-Click trạng thái mã nguồn về trước khi AI chỉnh sửa.
   * Xem trực tiếp hoặc tải file PDF đã biên dịch về máy.
   * Tải gói nén `.zip` chứa đầy đủ `main.tex`, `references.bib` và thư mục `figures/` để nộp bài.

### B. CRUD Thư mục Hình ảnh (`figures/` — `draft_assets`)
Để chèn sơ đồ kiến trúc, biểu đồ thực nghiệm vào bài báo thông qua lệnh `\includegraphics{figures/ten_anh.png}`:
1. **Tải ảnh lên thư mục `figures/` (`POST /api/v1/drafts/{id}/assets`):**
   * Hỗ trợ tải file ảnh `.png`, `.jpg`, `.jpeg`, `.pdf` (kiểm tra an toàn tên file và dung lượng).
2. **Xem danh sách file trong `figures/` (`GET /api/v1/drafts/{id}/assets`):**
   * Hiển thị danh sách các file ảnh đang có trong dự án ở thanh Quản lý File Cột 1; bấm vào tên ảnh có thể chèn nhanh đoạn mã `\begin{figure} ... \includegraphics{figures/...} \end{figure}` vào `main.tex`.
3. **Xóa ảnh khỏi `figures/` (`DELETE /api/v1/drafts/{id}/assets/{asset_id}`):**
   * Xóa ảnh tải nhầm hoặc không còn sử dụng khỏi bản thảo.

### C. CRUD Lịch sử Hội thoại với Agent Soạn thảo (`draft_messages`)
Để khi người dùng tải lại trang (`F5`) hoặc mở lại bản thảo vào ngày hôm sau không bị mất mạch làm việc với Agent ở Cột 3:
1. **Xem lịch sử chat của Bản thảo (`GET /api/v1/drafts/{id}/messages`):** Tải toàn bộ các lượt yêu cầu của người dùng và các bước phản hồi/gọi công cụ của LangGraph Agent gắn với `draft_id` đó.
2. **Gửi yêu cầu mới cho Agent (`POST /api/v1/drafts/{id}/messages` / `/assist`):** Lưu tin nhắn của người dùng và phản hồi của Agent vào cơ sở dữ liệu.
3. **Làm mới lịch sử chat của Bản thảo (`DELETE /api/v1/drafts/{id}/messages`):** Nút `[🔄 Làm mới đoạn chat]` trên Cột 3 giúp xóa lịch sử hội thoại cũ của bản thảo mà không làm ảnh hưởng đến code `main.tex` hay `references.bib`.

---

## 4. Bố Cục Không Gian Soạn Thảo 3 Cột (`WritingWorkspace.tsx`)

| Cột 1 (Trái): Quản lý File & Trình soạn thảo Code | Cột 2 (Giữa): Xem trước PDF trực tiếp | Cột 3 (Phải): Khung Chat Agentic AI |
| :--- | :--- | :--- |
| • Thanh cây thư mục dự án: chuyển đổi giữa **`main.tex`**, **`references.bib`** và thư mục **`figures/`** (có nút `[➕ Tải ảnh lên]`).<br>• Khung soạn thảo mã nguồn có đánh số dòng, tô màu cú pháp, hỗ trợ sửa tay bất kỳ lúc nào.<br>• Nút **`[⚙️ Biên dịch PDF]`** thủ công và nút **`[↩️ Hoàn tác (Undo) thay đổi của AI]`**. | • Hiển thị bản dựng PDF (`WritingPreviewPane.tsx`) trả về từ E2B Sandbox ngay sau mỗi lần biên dịch thành công.<br>• Hỗ trợ phóng to/thu nhỏ và tải file PDF về máy. | • Khung hội thoại trực tiếp với **LangGraph Agent**.<br>• Hiển thị trực quan từng bước Agent đang thực thi theo thời gian thực (*`🔍 Đang tra cứu Kho GraphRAG...` $\rightarrow$ `✍️ Đang cập nhật main.tex...` $\rightarrow$ `⚙️ Đang biên dịch trên E2B (Lần 1/3)...`*). |

### Cơ chế Chống Ghi Đè Khi Vừa Sửa Tay Vừa Dùng Agent (Anti-Overwrite & 1-Click Undo)
1. **Đồng bộ trước khi gọi Agent:** Mỗi khi người dùng bấm gửi yêu cầu trong khung Chat Cột 3, trình duyệt tự động gửi kèm nội dung mới nhất đang có trên ô soạn thảo (`main.tex` và `references.bib`) lên Backend để Agent luôn thao tác trên bản mới nhất của người dùng.
2. **Khóa tạm thời & Lưu Snapshot Undo:** Trong vài giây Agent đang gọi công cụ `edit_file`, khung code Cột 1 tạm thời chuyển sang chế độ chỉ đọc (`Đang chờ AI cập nhật code...`) và lưu lại bản chụp (`previous_snapshot`) trước khi sửa. Ngay khi AI sửa xong, nút **`[↩️ Hoàn tác (Undo) thay đổi của AI]`** sáng lên để người dùng có thể quay về bản trước đó chỉ với 1 cú nhấp chuột nếu chưa ưng ý.

---

## 5. Kiến Trúc LangGraph Agent & Vòng Lặp Tự Sửa Lỗi Biên Dịch Trên E2B Sandbox

### A. Bộ 4 Công Cụ (Tools) của LangGraph Agent
Agent viết bài được xây dựng bằng `StateGraph` của **LangGraph** với 4 công cụ chuyên biệt:
1. **`create_file` / `edit_file`**: Tạo mới hoặc chỉnh sửa trực tiếp nội dung file `main.tex` và bổ sung mã trích dẫn BibTeX vào `references.bib`.
2. **`list_project_files`**: Đọc danh sách các file và tên chính xác của các hình ảnh đang có trong thư mục `figures/` để viết lệnh `\includegraphics{figures/...}` không bị sai tên file.
3. **`query_library_graph_rag`**: Truy vấn vào Kho Paper Yêu Thích & GraphRAG khi người dùng yêu cầu viết tổng quan tài liệu hoặc lập bảng so sánh kết quả thực nghiệm với các bài báo đã lưu trong kho.
4. **`compile_latex_e2b`**:
   * Đóng gói trọn bộ **`main.tex` + `references.bib` + toàn bộ file ảnh trong `figures/`** đẩy lên thư mục làm việc `/tmp/verischolar-latex/` của **E2B Sandbox (Cloud MicroVM)**.
   * Chạy quy trình biên dịch đầy đủ (`pdflatex -> bibtex -> pdflatex -> pdflatex` hoặc `tectonic` với cờ bảo mật `--no-shell-escape` và giới hạn cứng `timeout = 15 giây`) để đảm bảo mọi trích dẫn `\cite{...}` hiển thị chuẩn xác (không bị lỗi dấu hỏi `[?]`) và lên đầy đủ hình ảnh.

### B. Vòng lặp Tự sửa lỗi biên dịch (Self-Healing Loop — Tối đa 3 lần)
```
[Agent sửa main.tex / references.bib]
                  │
                  ▼
     [Gọi tool compile_latex_e2b]
                  │
      ┌───────────┴───────────┐
      ▼ (Thành công)          ▼ (Lỗi biên dịch & Số lần thử < 3)
[Trả về PDF mới       [Node phân tích stderr từ E2B]
 lên Cột 2 Preview]           │
                              ▼
                      [Gọi edit_file tự vá lỗi cú pháp]
                              │
                              └──► [Quay lại compile_latex_e2b]
```
* Nếu sau **3 vòng lặp** mà vẫn còn lỗi biên dịch (ví dụ do người dùng chèn gói thư viện lạ không tồn tại), Agent tự động dừng vòng lặp, giữ nguyên mã nguồn và báo rõ **Số dòng bị lỗi + Nguyên nhân cụ thể + Cách khắc phục** trên khung Chat Cột 3.
