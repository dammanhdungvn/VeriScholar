# Đặc Tả Thiết Kế: Tối Ưu Bố Cục Đồ Họa, Thứ Tự Biểu Đồ Use Case & Khoảng Cách Sơ Đồ Luận Văn

> **Tài liệu tham chiếu:** [`../../../AGENTS.md`](../../../AGENTS.md) | [`../../../report-datn/AGENTS.md`](../../../report-datn/AGENTS.md)
> **Trạng thái:** Chờ phê duyệt (Pending Approval)

---

## 1. Mục Tiêu & Bối Cảnh (Context & Goals)

Quá trình rà soát trực quan toàn văn bản in đồ án tốt nghiệp VeriScholar phát hiện một số khiếm khuyết đồ họa và bố cục float LaTeX:
1. **Hình 3-2 (Kiến trúc Lục giác tổng thể):** Chiều rộng hình ($24\,\text{cm}$ ở `scale=0.74` $= 17{,}8\,\text{cm}$) vượt quá lề bản in (`\textwidth = 16\,\text{cm}$), dẫn đến mép phải của toàn bộ các khối Adapter bị xén cụt ký tự.
2. **Hình 2-4 (Vòng lặp ReAct và MicroVM Sandbox):** Đỉnh mũi tên vòng lặp nét đứt màu đỏ *"Phản hồi vòng lặp sửa cú pháp"* bị cắt cụt do vượt quá ranh giới đỉnh bounding box; các nhãn rẽ nhánh dính sát hình thoi quyết định; khoảng cách giữa đáy hình và caption bị chật.
3. **Mục 3.4 (Thứ tự Use Case):** Bảng 3-1 (Đặc tả danh mục Use Case) đang đứng trước Hình 3-3 (Biểu đồ Use Case tổng quan), đi ngược lại quy chuẩn công nghệ phần mềm và UML (Biểu đồ tổng quan phải đứng trước để cung cấp cái nhìn trực quan, sau đó mới đến bảng đặc tả chi tiết phía dưới).
4. **Trang 30 (Khoảng trắng hoang vu - Orphan Whitespace):** Sau 3 dòng text mở đầu Mục 3.5.1, Hình 3-8 quá cao (`scale=0.80`, chiều cao $\approx 8.5\,\text{cm}$) nên LaTeX không thể xếp vừa trang 30, đẩy toàn bộ hình sang đầu trang 31 và bỏ trống $80\%$ trang 30.
5. **Hình 3-12 (Biểu đồ lớp miền thực thể):** Nhãn bản số quan hệ (`{1}`, `{N}`) bị in đè trực tiếp lên tên lớp (`ScholarProfile`, `Document`, `DocumentChunk`, `GraphEdge`, `DraftMessage`) và tên phương thức (`update_weight`, `update_content`, `set_active_doc`).
6. **Hình 3-9, 3-10, 3-11 (Biểu đồ tuần tự) & Toàn bộ sơ đồ:** Khoảng cách giữa các dòng thông điệp tuần tự cần giãn thêm $\approx 0.5$ dòng ($1.5\,\text{mm}$ - $2\,\text{mm}$); toàn bộ các sơ đồ cần tăng khoảng cách đệm trên/dưới với văn bản thân bài thêm $0.5$ dòng (`0.5\baselineskip`).

---

## 2. Các Tiếp Cận Đã Cân Nhắc (Approaches)

### Phương án 1 (Đã chọn): Dynamic A4 Compact & Orthogonal Padding
- **Hình 3-2:** Thu hẹp tọa độ trục $x$ của các cột Adapter từ $\pm 10.4$ về $\pm 8.8$, giảm nhẹ `scale` từ 0.74 xuống 0.68. Đảm bảo toàn bộ sơ đồ rộng đúng $15.5\,\text{cm} < 16\,\text{cm}$, triệt tiêu $100\%$ hiện tượng xén mép phải.
- **Hình 2-4:** Căn chỉnh cung tròn vòng lặp đỏ (`out=115, in=245`, giảm độ vồng), hạ thấp tọa độ $y$ của các nhãn rẽ nhánh hình thoi với padding `fill=white, inner sep=2pt`, tăng khoảng cách giữa đáy hộp PDF và caption.
- **Mục 3.4:** Đảo vị trí: đưa tiểu mục Biểu đồ Use Case tổng quan (Hình 3-3) lên vị trí 3.4.1, chuyển Danh mục ca sử dụng (Bảng 3-1) xuống vị trí 3.4.2.
- **Trang 30:** Tối ưu hóa kích thước dọc của Hình 3-8 (giảm trục $y$ từ $-9.4$ về $-8.0$, scale 0.74) và tinh chỉnh đoạn văn dẫn để Hình 3-8 được kéo lên trang 30 ngay dưới văn bản dẫn, triệt tiêu hoàn toàn khoảng trắng thừa.
- **Hình 3-12:** Thiết kế lại toàn bộ điểm neo (anchor coordinates) của nhãn `{1}`, `{N}` sang sườn ngoài các hộp lớp (offset $\ge 8\,\text{pt}$ so với góc/cạnh), nắn đường liên kết theo đường bao trực giao cách biên lớp $\ge 10\,\text{pt}$.
- **Hình 3-9, 3-10, 3-11 & Spacing toàn hệ thống:** Nới khoảng cách bước thông điệp trong 3 biểu đồ tuần tự; bổ sung thiết lập `\intextsep`, `\abovecaptionskip`, `\belowcaptionskip` đồng bộ tăng thêm $0.5$ dòng trong `preamble.tex`.

### Phương án 2 (Bị loại): Fill Text Buffer
- Giữ nguyên kích cỡ lớn của Hình 3-8 sang trang 31 và viết thêm 2 đoạn văn dài lấp đầy trang 30.
- *Lý do loại:* Gây loãng nội dung chuyên môn, phá vỡ tỷ lệ trang chuẩn của đề cương và không giải quyết tận gốc tính co giãn đồ họa khi in ấn A4.

---

## 3. Đặc Tả Chi Tiết Thay Đổi (Detailed Technical Specifications)

### 3.1. Hình 3-2: Tinh Gọn Trục Ngang Kiến Trúc Lục Giác (`chapters/ch3/3_3_kien_truc.tex`)
- **Tọa độ mới:**
  - Core Domain: giữ nguyên $x \in [-4.5, 4.5]$.
  - Ports: đặt tại $x = \pm 6.3$ (trước đây là $\pm 6.8$).
  - Adapters: đặt tại $x = \pm 8.8$ (trước đây là $\pm 10.4$).
  - Nhãn Driving / Driven: đưa vào $x = \pm 6.3, y = 3.8$.
  - Tỷ lệ `scale`: đặt $0.68$, căn giữa trang với `\centering`.
- **Kết quả kỳ vọng:** Lề phải của các Adapter Database, AI Inference, Sandbox, External Scholar cách lề trang $\ge 5\,\text{mm}$, không còn mất chữ.

### 3.2. Hình 2-4: Tái Cấu Trúc Cung Tròn Vòng Lặp & Nhãn Hình Thoi (`chapters/ch2/2_5_agentic_react.tex`)
- Đổi đường cong: `(obs.north) to[out=110, in=250] node[midway, left=5pt, ...]` để cung cong không nhô cao hơn đỉnh của hộp `agent`.
- Thêm khoảng đệm `fill=white, inner sep=2pt` cho các nhãn `No (Lỗi)`, `Yes (Exit 0)`, `Trả kết quả`.
- Thêm `\vspace{4pt}` giữa đáy hình và `\caption`.

### 3.3. Mục 3.4: Đảo Vị Trí Hình 3-3 & Bảng 3-1 (`chapters/ch3/3_4_phan_tich_usecase.tex`)
- **Cấu trúc mới:**
  - Tiểu mục 3.4.1: *Biểu đồ Use Case tổng quan của hệ thống* (Hình 3-3).
  - Tiểu mục 3.4.2: *Danh mục các tác nhân và ca sử dụng chính của hệ thống* (Bảng 3-1).
  - Cập nhật các câu văn dẫn tham chiếu tương ứng (`Hình~\ref{fig:usecase_overview}` xuất hiện trước `Bảng~\ref{tab:actors_usecases}`).

### 3.4. Trang 30 & Hình 3-8: Triệt Tiêu Khoảng Trắng Hoang Vu (`chapters/ch3/3_5_bieu_do_tuan_tu.tex`)
- Rút gọn chiều cao TikZ của Hình 3-8:
  - Lifeline kết thúc tại $y = -7.8$ (trước đây là $-9.4$).
  - Khoảng cách giữa các thông điệp rút từ $0.7\,\text{cm}$ xuống $0.58\,\text{cm}$.
  - Đặt `scale=0.74, transform shape`.
  - Sử dụng định vị float `[!htbp]` cho phép hình bám dính ngay sau đoạn văn mở đầu trên trang 30.

### 3.5. Hình 3-12: Khử Chồng Đè Nhãn Bản Số Biểu Đồ Lớp (`chapters/ch3/3_6_thiet_ke_csdl.tex`)
- Dời toàn bộ nhãn `{1}` và `{N}` ra ngoài thân hộp lớp:
  - Dùng anchor lệch sườn: `node[card, anchor=south east] at ([xshift=-4pt, yshift=2pt]node.north)` hoặc `node[card, anchor=north east] at ([xshift=-4pt, yshift=-2pt]node.south)`.
  - Không đặt nhãn đè lên đường kẻ ngang ngăn cách giữa tên lớp và danh sách thuộc tính.
  - Các đường nối liên kết đa cột (giữa cột 1 và cột 2, cột 2 và cột 3) đi lùi ra ngoài biên ít nhất $0.5\,\text{cm}$ để không cắn vào góc hộp.

### 3.6. Hình 3-9, 3-10, 3-11 & Khoảng Cách Đệm 0.5 Dòng Toàn Hệ Thống
- Trong `3_5_bieu_do_tuan_tu.tex`: nới khoảng cách bước dọc giữa các thông điệp trong Hình 3-9, 3-10, 3-11 thêm $1.5\,\text{mm}$ mỗi thông điệp để tạo độ thoáng mắt khi đọc.
- Trong `config/preamble.tex`:
  - `\setlength{\intextsep}{1.2\baselineskip}` (tăng $0.5$ dòng so với mặc định).
  - `\setlength{\textfloatsep}{1.2\baselineskip}`.
  - `\setlength{\abovecaptionskip}{8pt}`.
  - `\setlength{\belowcaptionskip}{6pt}`.

---

## 4. Kế Hoạch Xác Minh (Verification Plan)

1. **Kiểm tra trực quan bằng ảnh xuất bản:**
   - Xuất PDF sang PNG các trang liên quan (trang chứa Hình 2-4, 3-2, 3-3, 3-8, 3-9, 3-10, 3-11, 3-12) và kiểm tra:
     - Hình 3-2 không còn tràn lề phải.
     - Vòng lặp Hình 2-4 nguyên vẹn đỉnh, các nhãn hình thoi không dính nét.
     - Hình 3-3 đứng trước Bảng 3-1.
     - Trang 30 chứa trọn vẹn Hình 3-8, không còn khoảng trắng hoang vu.
     - Hình 3-12 không còn bất kỳ nhãn `{1}`, `{N}` nào đè lên tên lớp hay hàm.
     - Khoảng cách trên/dưới các hình đều có đệm $0.5$ dòng thoáng đãng.
2. **Kiểm định 4 Cổng Bắt Buộc (The 4 Verification Gates):**
   - Cổng 1: `uv run ruff check . && uv run ruff format --check .`
   - Cổng 2: `uv run pytest` (366 tests pass 100%).
   - Cổng 3: `npm --prefix apps/web run test` (240 tests pass 100%).
   - Cổng 4: `npm --prefix apps/web run build && python3 scripts/verify_thesis_format.py` (Exit code 0, ngân sách trang chuẩn mực).
3. **Đồng bộ VPS tự động:**
   - Sau mỗi commit chạy `bash scripts/deploy_to_vps.sh --fast`.
