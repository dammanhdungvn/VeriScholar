# BỘ QUY TẮC BẤT BIẾN BIÊN SOẠN BÁO CÁO ĐỒ ÁN TỐT NGHIỆP VERISCHOLAR (RULES.md)

> **Cơ sở pháp lý & Học thuật:** Tuân thủ 100% tài liệu hướng dẫn [`Huong-dan-viet-DATN.md`](./guide/Huong-dan-viet-DATN.md) của Trường Đại học Mỏ - Địa chất (HUMG) và kế thừa chuẩn mực văn phong từ 2 đồ án mẫu xuất sắc ([`Nguyễn Trung Hiếu`](./guide/2121050196_NguyenTrungHieu_BaoCaoDATN.md) và [`Nguyễn Quang Bắc`](./guide/NguyenQuangBac_Báo%20cáo%20DATN_final.md)).
> **Đề tài chính thức:** *Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn*
> **Tác giả:** Đàm Mạnh Dũng - 2221050359 – Lớp: DCCTCT67_09B, Khoa Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất
> **Quy chuẩn kỹ thuật:** Mọi AI Agent hoặc tác giả trước khi chỉnh sửa/viết nội dung vào thư mục `report-datn/` bắt buộc phải đọc và tuân thủ tuyệt đối các điều luật trong văn bản này.

---

## PHẦN 1: KIẾN TRÚC & CẤU HÌNH KỸ THUẬT XELATEX

### 1.1. Trình Biên Dịch Tiêu Chuẩn
* **Trình biên dịch duy nhất:** Bắt buộc sử dụng **XeLaTeX** (gọi lệnh qua `latexmk -xelatex` hoặc phím tắt `Ctrl+Alt+B` trong VSCode).
* **Tuyệt đối cấm pdfLaTeX:** Hệ thống Linux không hỗ trợ bộ mã hóa font 8-bit `T5` của pdfLaTeX, gây lỗi vỡ dấu tiếng Việt. XeLaTeX sử dụng Unicode UTF-8 bản địa kết hợp `fontspec`.
* **Cờ khai báo tệp gốc:**
  * Dòng 1 của `main.tex`: `% !TEX program = xelatex`
  * Dòng 1 của mọi tệp con (`chapters/*.tex`, `frontmatter/*.tex`): `% !TEX root = ../main.tex`

### 1.2. Kiến Trúc Cây Thư Mục Mô-Đun Hóa
Mọi tệp nguồn phải đặt đúng vị trí trách nhiệm:
* `main.tex`: Tệp điều phối trung tâm (< 60 dòng), chỉ nạp gói và gọi lệnh `\include{...}`.
* `config/preamble.tex`: Chứa toàn bộ cấu hình gói lệnh, lề trang, cỡ chữ, phông nền, header/footer.
* `config/commands.tex`: Khai báo các macro ký hiệu toán học, thuật ngữ viết tắt.
* `frontmatter/`: Các tệp phần mở đầu: `loi_cam_on.tex`, `loi_mo_dau.tex`, `danh_muc_viet_tat.tex`, `danh_muc_bang.tex`, `danh_muc_hinh.tex`, `bia_phu.tex`.
* `chapters/`: Thân bài gồm 4 chương: `ch1_tong_quan.tex`, `ch2_co_so_ly_thuyet.tex`, `ch3_thiet_ke_he_thong.tex`, `ch4_thuc_nghiem.tex`, `ket_luan.tex`, và `tai_lieu_tham_khao.tex`.
* `figures/`: Lưu trữ tập trung các sơ đồ, hình ảnh kiến trúc chuẩn bài báo khoa học.

### 1.3. Cơ Chế In Ấn Thực Tế & Cờ Bìa Mềm
* **Bản in đóng gáy (Hard Copy):** Tác giả đã làm riêng 2 trang bìa cứng mạ nhũ vàng bên ngoài. Bản in PDF xuất ra từ LaTeX là phần ruột nội dung để tiệm in kẹp vào giữa. Do đó, cờ `\showcoverfalse` được kích hoạt mặc định để trang đầu tiên của PDF bắt đầu từ phần ruột (không in lại bìa tránh lệch gáy).
* **Bản mềm nộp lưu trữ (Soft Copy):** Khi cần nộp file PDF lưu trữ cho Bộ môn CNTT theo Quy chế, chỉ cần đổi thành `\showcovertrue` trong `main.tex` để tự động kích hoạt trang bìa phụ (`frontmatter/bia_phu.tex` theo Phụ lục 02).

### 1.4. Kiến Trúc Phân Rã Sâu Từng Mục (Micro-Modular Structure)
* **Tách tệp vi mô (Section-level files):** Để tối ưu hóa triệt để cửa sổ ngữ cảnh (Context Window) và tiết kiệm quota token cho AI, mỗi chương được phân rã thành các thư mục con chuyên biệt (`chapters/ch1/`, `chapters/ch2/`, `chapters/ch3/`, `chapters/ch4/`). Mỗi phần lớn là một tệp `.tex` độc lập (ví dụ `chapters/ch3/3_1_khao_sat.tex`, `chapters/ch3/3_2_usecase.tex`...).
* **Tệp điều phối chương:** Mỗi tệp `chapters/chX_ten_chuong.tex` đóng vai trò điều phối, chỉ chứa tiêu đề chương và các lệnh `\input{chapters/chX/...}` nạp tuần tự các tệp con.
* **Nguyên tắc nạp ngữ cảnh tối thiểu:** Khi AI viết, sửa chữa hoặc bổ sung một mục cụ thể, AI chỉ nạp duy nhất tệp con tương ứng và tệp bản đồ mục lục `ROADMAP.md`, tuyệt đối không đọc toàn bộ báo cáo để tránh lãng phí token và ngăn ngừa lỗi vô tình sửa lan sang các phần khác.

### 1.5. Quy Chuẩn Phòng Ngừa Lỗi Biên Dịch & Thoát Ký Tự Đặc Biệt (Defensive XeLaTeX Compilation)
Để triệt tiêu tận gốc 100% lỗi dừng đột ngột khi biên dịch XeLaTeX:
* **Bắt buộc thoát ký tự đặc biệt:** Mọi ký tự nhạy cảm của LaTeX trong văn bản thân bài bắt buộc phải thêm dấu gạch chéo ngược: `\_`, `\%`, `\&`, `\#`, `\$`, `\{`, `\}`.
  * *Đặc biệt lưu ý:* Tên biến, trường cơ sở dữ liệu và định danh mã nguồn (như `user_id`, `paper_id`, `created_at`) rất dễ bị sót dấu `_`, khiến XeLaTeX chuyển sang chế độ toán và báo lỗi `Missing $ inserted`. Bắt buộc phải viết `user\_id` hoặc bọc trong khối định danh `\texttt{user\_id}`.
* **Bảo toàn Nhãn Tham chiếu Chéo (`\label{...}` Invariance):** Tuyệt đối không xóa, đổi tên hoặc sửa nhãn của các Hình (`fig:...`) và Bảng (`tab:...`) đã được xác lập trong hệ thống kiểm thử tự động (ví dụ `tab:uc_01_spec`, `fig:hexagonal_arch`, `fig:hybrid_rag_flow`, `fig:e2e_pipeline_arch`).
* **Trích đoạn Mã nguồn & Thuật toán:** Cấm dán mã nguồn thô hàng trăm dòng làm loãng nội dung học thuật của đồ án. Chỉ trích dẫn các khối hàm logic hạt nhân tối đa 15-20 dòng bằng môi trường định dạng code chuẩn (`\begin{lstlisting}`) hoặc mã giả giải thuật (`algorithm2e`).

---

## PHẦN 2: QUY CHUẨN ĐỊNH DẠNG TRANG & HÌNH THỨC

### 2.1. Khổ Giấy & Căn Lề Trang (Page Geometry)
* **Khổ giấy:** A4 chuẩn (210 x 297 mm), in một mặt.
* **Căn lề bắt buộc (Quy định trang 3 Huong-dan-viet-DATN):**
  * Lề trên (Top): **2.5 cm**
  * Lề dưới (Bottom): **2.5 cm**
  * Lề trái (Left - gáy sách): **3.5 cm** (chừa khoảng đóng gáy lò xo/bìa cứng)
  * Lề phải (Right): **2.5 cm**

### 2.2. Phông Chữ, Dãn Dòng & Ma Trận Phân Cấp Cỡ Chữ (Font Size Matrix)
* **Phông chữ:** `Liberation Serif` (tương đương chuẩn Microsoft Times New Roman bản địa Unicode).
* **Dãn dòng (Line spacing):** Đặt ở chế độ **1.5 lines** (`\onehalfspacing` qua gói `setspace`).
* **Thụt lề đoạn văn (First-line Indent):** Đúng chuẩn **1.0 cm** (`\setlength{\parindent}{1.0cm}`).

#### Bảng Quy Chuẩn Phân Cấp Cỡ Chữ Báo Cáo Đồ Án Tốt Nghiệp:

| Cấp bậc | Thành phần trong đồ án | Cỡ chữ (Size) | Định dạng (Style) | Căn lề | Khoảng cách (Spacing) | Cấu hình kỹ thuật |
| :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| **Bìa chính / Bìa phụ** | Tên trường, Tác giả, Tên đề tài | **16pt** | In hoa, Đậm | Giữa | Theo mẫu phụ lục | `\fontsize{16}{20}\selectfont` |
| | Nhãn "ĐỒ ÁN TỐT NGHIỆP" | **32pt – 40pt** | In hoa, Đậm | Giữa | Theo mẫu phụ lục | `\fontsize{28}{34}\selectfont` đến `40pt` |
| **Tiêu đề Chương** | `CHƯƠNG 1: TÊN CHƯƠNG`, `MỤC LỤC`... | **16pt** | In hoa, Đậm | Giữa | Before 0pt, After 18pt | `\titleformat{\chapter}[block]` |
| **Mục cấp 1** | `1.1`, `2.1`, `3.1`... | **14pt** | Đậm | Trái | Before 12pt, After 6pt | `\titleformat{\section}` |
| **Tiểu mục cấp 2** | `1.1.1`, `2.1.1`... | **13pt** | Đậm | Trái | Before 9pt, After 4pt | `\titleformat{\subsection}` |
| **Tiểu mục cấp 3** | `1.1.1.1`, `2.1.1.1`... | **13pt** | Đậm nghiêng | Trái | Before 6pt, After 3pt | `\titleformat{\subsubsection}` |
| **Thân bài (Body text)** | Đoạn văn nội dung toàn bài | **13pt** | Thường, dãn dòng 1.5 | Đều 2 bên | Thụt lề đầu dòng 1.0cm | `\usepackage[fontsize=13pt]{scrextend}` |
| **Tiêu đề Bảng / Hình** | `Bảng 3-1:`, `Hình 3-1:` | **12pt** | Nhãn Đậm, Tên Nghiêng | Giữa | Bảng: trên 6pt; Hình: dưới 6pt | `\captionsetup{font=size12}` |
| **Header & Footer** | Tên đồ án / Họ tên SV, Số trang | **10pt** | Header Đậm, Footer Nghiêng | Trái / Phải | Cách mép giấy 1.5cm – 2.0cm | `\fontsize{10}{12}\selectfont` |
| **Chú thích (Footnote)** | Giải thích từ ngữ chân trang | **10pt** | Thường | Đều 2 bên | Dãn dòng đơn | `\fontsize{10}{13}\selectfont` |

### 2.3. Quy Chuẩn Đánh Số Trang & Tiêu Đề Đầu/Chân Trang (Header & Footer)
* **Phần mở đầu (Frontmatter - Đánh số La Mã thường `i, ii...`):** Dành riêng cho `MỤC LỤC` (bắt đầu từ trang `i`), `DANH MỤC HÌNH ẢNH`, `DANH MỤC BẢNG BIỂU`, `DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT`.
* **Phần nội dung (Main Body - Đánh số Ả Rập `1, 2, 3...`):** Bắt đầu đánh số 1 từ `LỜI CẢM ƠN` (trang 1), `LỜI MỞ ĐẦU` (trang 2), `CHƯƠNG 1` (trang 3 trở đi) đến hết Kết luận, Tài liệu tham khảo và Phụ lục.
* **Tiêu đề đầu trang (Header):**
  * Bên trái: In đậm `Đồ án tốt nghiệp ngành Công nghệ thông tin`.
  * Có đường kẻ ngang phân cách đầu trang (`\headrulewidth = 0.5pt`).
* **Tiêu đề chân trang (Footer):**
  * Bên trái: Ghi dòng chữ in nghiêng `SVTH: Đàm Mạnh Dũng - 2221050359 – Lớp: DCCTCT67_09B`.
  * Bên phải: Số trang in nghiêng `\textit{\thepage}`.
  * Có đường kẻ ngang phân cách chân trang (`\footrulewidth = 0.5pt`).

### 2.4. Quy Chuẩn Cân Đối Bố Cục Trang & Phân Bổ Dung Lượng (Page Budget & Pagination Invariant)
* **Quy tắc Triệt tiêu Trang trắng Mồ côi (Zero Orphan Blank Pages):** Mọi văn bản phải được bố trí liên tục, chặt chẽ. Cấm ngắt trang tùy tiện (`\newpage`) tạo ra các trang trống chỉ có 1-2 dòng văn bản thừa. Lệnh `\clearpage` chỉ được phép sử dụng ở ranh giới giữa các chương chính.
* **Chống Tiêu đề Mồ côi (No Orphan Headings):** Tuyệt đối cấm để tiêu đề mục (`\section`, `\subsection`) nằm lẻ loi ở dòng cuối cùng của trang mà không có ít nhất 2-3 dòng thân bài bên dưới (sử dụng cơ chế `\nopagebreak` hoặc điều chỉnh dãn cách đoạn văn).
* **Ma trận Phân bổ Số trang Cân đối Chuẩn mực:**
  * **Chương 1 (Tổng quan & Bài toán):** 6 – 8 trang (Bối cảnh, tính cấp thiết, mục tiêu, phạm vi).
  * **Chương 2 (Cơ sở lý thuyết & Công nghệ):** 10 – 14 trang (Nguyên lý toán học, kiến trúc tổng quát, luận giải tại sao chọn).
  * **Chương 3 (Phân tích & Thiết kế hệ thống):** 16 – 22 trang (Khảo sát, đặc tả Use Case, kiến trúc đa tầng, thiết kế CSDL).
  * **Chương 4 (Cài đặt & Thực nghiệm):** 10 – 14 trang (Môi trường, giao diện 4 phân hệ, kết quả kiểm thử, số liệu đo lường).
  * **Kết luận & Hướng phát triển:** 2 – 3 trang.
  * **Tổng quy mô báo cáo ruột:** Nằm trong khoảng **50 – 65 trang** (chuẩn mực đồ án xuất sắc của Bộ môn CNTT).

---

## PHẦN 3: VĂN PHONG & QUY TẮC HÀNH VĂN BẤT BIẾN

### 3.1. Ngôi Văn Khách Quan Chuẩn Mực
* **Tuyệt đối cấm xưng hô cảm tính:** Không dùng các đại từ nhân xưng ngôi thứ nhất như *"tôi"*, *"em"*, *"chúng tôi"*, *"chúng em"*.
* **Sử dụng danh xưng khoa học:** Dùng ngôi thứ ba chuẩn mực: *"tác giả"*, *"đề tài"*, *"nghiên cứu này"*, *"hệ thống VeriScholar"*.

### 3.2. Cấu Trúc Lập Luận "Tại Sao Chọn" (Justification-Driven)
Giống như cách lập luận của 2 đồ án mẫu xuất sắc, khi giới thiệu bất kỳ công nghệ hoặc giải pháp nào ở Chương 2, tác giả phải nêu rõ:
1. Bản chất lý thuyết & nguyên lý hoạt động.
2. Ưu điểm và nhược điểm so với các công nghệ tương đương.
3. **Đoạn văn khẳng định lý do lựa chọn:** Trả lời trực diện câu hỏi của Hội đồng phản biện: *"Tại sao đề tài chọn giải pháp này mà không chọn giải pháp khác?"*.
   * *Ví dụ:* Chọn PostgreSQL 16 + `pgvector` thay vì Pinecone/Milvus để bảo toàn tính nhất quán ACID (xóa bài báo xóa luôn embedding trong 1 transaction) và tiết kiệm chi phí hạ tầng.
   * *Ví dụ:* Chọn Hybrid RAG kết hợp RRF $k=60$ thay vì Dense Search đơn thuần để xử lý tốt cả từ khóa chuyên ngành hiếm gặp lẫn ngữ nghĩa khái quát.

### 3.3. Đặc Tả Nghiệp Vụ Chuẩn BA & Biểu Đồ UML
Ở Chương 3, khi trình bày các ca sử dụng (Use Case):
* Bắt buộc có bảng đặc tả chi tiết: Mã UC, Tác nhân, Tiền điều kiện, Hậu điều kiện, Luồng sự kiện chính, Luồng ngoại lệ.
* Mỗi phân hệ lớn phải có biểu đồ tuần tự UML (Sequence Diagram) thể hiện rõ luồng tương tác giữa Người dùng $\rightarrow$ Frontend $\rightarrow$ Backend API $\rightarrow$ Database / AI Service.
* Thiết kế CSDL vật lý phải đi kèm bảng Từ điển dữ liệu (Data Dictionary): Tên trường, Kiểu dữ liệu, Khóa, Mô tả ràng buộc.

### 3.4. Minh Chứng Định Lượng (Empirical Proof)
Ở Chương 4, không mô tả tính năng chung chung; phải đưa ra các bằng chứng số liệu đo đạc thực tế:
* Cấu hình môi trường cài đặt phần cứng và monorepo.
* Ảnh chụp giao diện thực tế của hệ thống.
* Kết quả chạy 4 Cổng kiểm thử tự động (số lượng test pass, thời gian chạy).
* Bảng số liệu thực nghiệm: Độ trễ phản hồi (TTFT < 1.5s), độ chính xác tọa độ Bounding Box (IoU $\ge$ 0.85), tỷ lệ tự sửa lỗi biên dịch LaTeX ($\ge$ 90%), chi phí token từ Langfuse Cloud.

### 3.5. Quy Chuẩn Danh Ngữ Hóa Tiêu Đề & Chống Trần Thuật Kể Lể (Academic Nominalization)
Để khắc phục triệt để lỗi văn phong trần thuật kể lể (Narrative Rambling) và đảm bảo tính trong sáng, đanh thép của một đồ án tốt nghiệp xuất sắc:
* **Tuyệt đối cấm tiêu đề dạng mệnh đề kể lể, dài dòng:** Cấm mở đầu tiêu đề bằng các động từ hành động hoặc cụm từ trần thuật như *"Nghiên cứu giải pháp..."*, *"Tìm hiểu về..."*, *"Khảo sát về..."*, *"Hiện thực hóa..."*, *"Thiết kế luồng..."*, cùng các liên từ độn từ dài lê thê (*"kết hợp... dựa trên... trên nền..."*).
* **Độ dài tiêu đề mục chuẩn mực:** Mỗi tiêu đề mục chỉ dài từ **3 đến 7 từ**, định danh trực diện khái niệm, đối tượng kỹ thuật, thuật toán hoặc quy trình cốt lõi.
  * *Ví dụ vi phạm (Kể lể):* *"Nghiên cứu giải pháp truy xuất lai Agentic Hybrid RAG kết hợp thuật toán xếp hạng đảo ngược RRF"* (18 từ).
  * *Ví dụ chuẩn (Chuyên gia):* **"Kỹ thuật truy xuất lai (Hybrid RAG) và thuật toán RRF"** (8 từ).
  * *Ví dụ vi phạm (Kể lể):* *"Khảo sát quy trình nghiên cứu khoa học và bài toán hỗ trợ xuất bản quốc tế tại VinUniversity"* (16 từ).
  * *Ví dụ chuẩn (Chuyên gia):* **"Khảo sát bài toán nghiên cứu tại VinUniversity"** (7 từ).
* **Cấu trúc đoạn văn kim tự tháp (Minto Pyramid Principle):**
  * Câu đầu đoạn (Topic sentence) nêu trực diện luận điểm hoặc kết luận chính.
  * Các câu tiếp theo trình bày ngay số liệu thực nghiệm, công thức toán học và bảng đối chiếu logic.
  * Câu cuối chốt ý nghĩa hoặc dẫn chiếu tới Bảng/Hình (`Bảng~\ref{...}`, `Hình~\ref{...}`).
  * Tuyệt đối không dùng văn trần thuật ngôi kể nhật ký (*"Sau khi làm xong A thì ta tiếp tục chuyển sang làm B..."*).

### 3.6. Quy Chuẩn Liêm Chính Học Thuật Giữa Các Chương (Academic Chapter Isolation)
Để bảo đảm tính chuyên nghiệp đỉnh cao và phương pháp luận khoa học:
* **Chương 2 (Cơ sở lý thuyết & Công nghệ):** Chỉ trình bày nguyên lý khoa học, mô hình lý thuyết, công thức toán học và kiến trúc tổng quát. Tuyệt đối cấm xuất hiện đường dẫn thư mục mã nguồn (`packages/`, `apps/`, `src/`), tên tệp (`.tsx`, `.py`), tên interface/class cụ thể trong code.
  * *Sai:* "Trong thư mục `packages/core/ports/`, hệ thống định nghĩa interface `IAcademicSearchResolverPort`."
  * *Đúng:* "Tầng lõi nghiệp vụ định nghĩa các cổng giao tiếp trừu tượng (*Ports*) như cổng phân giải ấn phẩm học thuật để phục vụ việc truy xuất tài liệu."
* **Chương 3 (Thiết kế hệ thống):** Nơi chính thức công bố sơ đồ kiến trúc Monorepo, thiết kế CSDL, các ca sử dụng và các thành phần phần mềm.
* **Chương 4 (Cài đặt và thực nghiệm):** Nơi trình bày chi tiết môi trường mã nguồn, kết quả kiểm thử tự động và số liệu đo đạc thực tế.
* **Quy chuẩn trích dẫn trong bản thảo xem trước:** Trong mọi bản nháp gửi người dùng duyệt, trích dẫn phải viết ở định dạng học thuật tự nhiên `[1]`, `[2]` hoặc `(Tác giả, Năm)`, không được để lộ cú pháp mã nguồn thô của LaTeX như `\cite{...}. T`.

---

### 3.7. Quy Chuẩn Biểu Diễn Sơ Đồ Kiến Trúc Hệ Thống Chuẩn Paper Khoa Học Quốc Tế (Academic Paper Architecture Paradigm)

Khi xây dựng các sơ đồ phân tích và thiết kế hệ thống (đặc biệt tại Chương 2 và Chương 3):

#### 1. Triết lý Thiết kế Hướng Người Đọc (Human-Centric):
* *Mục tiêu:* Phục vụ Hội đồng chấm luận án, giảng viên hướng dẫn và học giả nghiên cứu đọc hiểu trọn vẹn bản chất phương pháp luận và đóng góp khoa học.
* *Đặc trưng:* Tương tự sơ đồ Transformer trong bài báo *"Attention Is All You Need"* [Vaswani et al., 2017] hay sơ đồ RAG [Lewis et al., 2020], kiến trúc chỉ bao gồm các khối chức năng toán học và dòng chảy biến đổi thông tin logic.

#### 2. Bốn Tiêu Chuẩn Vàng Của Sơ Đồ Kiến Trúc Đồ Án:
* **Tiêu chuẩn 1 — Danh xưng khoa học:** Mọi thành phần trong sơ đồ phải được định danh bằng thuật ngữ khoa học chuyên ngành (ví dụ: *Tầng Phân giải Ấn phẩm, Động cơ Hợp nhất Thứ hạng RRF, Bộ Kiểm chứng Tọa độ Trực quan, Không gian Sandbox MicroVM*). Tuyệt đối không dùng tên file code (`.ts`, `.py`), endpoint URL (`/api/v1/...`) hay tên biến.
* **Tiêu chuẩn 2 — Trực quan hóa Dòng chảy Tri thức (Dataflow Transformation):** Sơ đồ phải làm rõ: Dữ liệu bài báo thô đi qua quá trình phân tách cấu trúc 2 cột như thế nào $\rightarrow$ lập chỉ mục kép (Dense + Sparse) ra sao $\rightarrow$ tác nhân Agentic điều phối chu trình suy luận thế nào $\rightarrow$ trả về trích dẫn có minh chứng tọa độ Bounding Box ra sao.
* **Tiêu chuẩn 3 — Tôn vinh Tính Đổi mới (Highlighting Novelty):** Làm nổi bật các điểm sáng tạo của đề tài (Agentic Hybrid RAG, GraphRAG 4 thực thể trên PostgreSQL ACID, E2B MicroVM triệt tiêu lỗ hổng `\write18`).
* **Tiêu chuẩn 4 — Nghiêm cấm Sơ đồ "Máy đọc":** Cấm tuyệt đối các biểu đồ lớp (Class Diagram) vụn vặt kiểu CRUD với danh sách thuộc tính và hàm getter/setter của lập trình viên phần mềm.

---

### 3.8. Quy Chuẩn Kỹ Nghệ Sơ Đồ TikZ Chống Chồng Đè & Ríu Rít (TikZ Visual Clarity & Anti-Crowding Standard)

Để đảm bảo mọi sơ đồ TikZ xuất bản trong đồ án đạt độ trong trẻo, thoáng đãng, sắc nét và đẳng cấp như các bài báo khoa học quốc tế, AI bắt buộc phải tuân thủ nghiêm ngặt **7 Nguyên Tắc Vàng Kỹ Nghệ TikZ**:

```
+-----------------------------------------------------------------------------------------+
|                  7 NGUYÊN TẮC VÀNG VẼ SƠ ĐỒ TIKZ CHUẨN PAPER QUỐC TẾ                    |
+-----------------------------------------------------------------------------------------+
| 1. Luật Tối giản Ruột Node (Max 2 Lines): Cấm nhồi nhét text dài vào bên trong node.    |
| 2. Kích thước Node Cố định (Explicit Dimensions): Luôn có text width và minimum height. |
| 3. Bố cục Phân dải Màu (Banded Architecture): Khung bao pastel bo tròn rounded corners. |
| 4. Định tuyến Trực giao (Orthogonal Routing): Mũi tên góc vuông (|- hoặc -|), cấm đâm xéo.|
| 5. Hành lang Độc lập (Independent Corridors): Phân tách cao độ y hoặc hoành độ x riêng biệt.|
| 6. Nhãn Mũi tên Cách ly (Isolated Edge Badges): Bắt buộc fill=white hoặc bọc badge bo góc. |
| 7. Khổ giấy & Thu phóng (Scale & Bounding Box): scale=0.74 - 0.80, bề ngang <= 15cm text. |
+-----------------------------------------------------------------------------------------+
```

#### Nguyên Tắc 1: Luật Tối Giản Ruột Node (Max 2-line Content Rule)
* **Quy định số dòng:** Mỗi node chức năng trong sơ đồ CHỈ ĐƯỢC PHÉP CHỨA TỐI ĐA **2 DÒNG**:
  * **Dòng 1:** Tên khối chức năng in đậm (`\textbf{Tên Chức Năng}`).
  * **Dòng 2:** Ký hiệu toán học hoặc thuật ngữ chuẩn hóa trong ngoặc đơn (`\scriptsize (\textit{Thuật ngữ / Ký hiệu})`).
* **Điều cấm tuyệt đối:** Tuyệt đối cấm nhồi nhét câu diễn giải dài dòng, đoạn văn mô tả 3-4 dòng, hoặc các thông số đo lường chi tiết (`IoU >= 0.85`, `ExitCode = 0`, danh sách các bước con) vào trong lòng node. Toàn bộ chi tiết kỹ thuật này phải được trình bày trong đoạn văn phân tích ở thân bài đi kèm ngay sau sơ đồ.

#### Nguyên Tắc 2: Kích Thước Node Cố Định & Phân Định Rõ Ràng (Explicit Dimensioning)
* Mọi node phải được khai báo kích thước tường minh qua style:
  * Chiều rộng văn bản cố định: `text width=2.2cm` đến `2.6cm` (đối với node chức năng thông thường) hoặc `text width=3.6cm` đến `4.8cm` (đối với khối tổng hợp trung tâm).
  * Chiều cao tối thiểu đồng đều: `minimum height=1.35cm` (đảm bảo các node nằm cùng hàng ngang có chiều cao bằng nhau tuyệt đối, không bị lồi lõm zíc-zắc).
  * Đệm lề bên trong: `inner sep=4pt` (cấm để mặc định khiến box phình to đè vào nhau).
  * Căn lề và dãn dòng cục bộ: `align=center, font=\linespread{1.0}\selectfont\footnotesize` (ngắt hiệu lực của dãn dòng 1.5 toàn bài để chữ trong node không bị dãn thưa bất thường).

#### Nguyên Tắc 3: Bố Cục Phân Tầng Dải Màu (Banded Architecture Paradigm)
* Hệ thống phức tạp phải được gom nhóm thành các dải (Bands) hoặc thẻ (Cards) bao quanh:
  * **Khung bao dải màu:** Dùng màu pastel dịu nhẹ (`fill=blue!3`, `fill=orange!3`, `fill=teal!3`, `fill=purple!3`), đường viền sắc nét (`draw=color!75!black, line width=1.1pt, rounded corners=8pt`).
  * **Tiêu đề định danh dải:** Gắn thẻ badge nổi bật ở góc trên bên trái khung bao:
    `\node[anchor=north west, fill=color!12, draw=color!70!black, rounded corners=3pt, font=\bfseries\scriptsize, text=color!90!black, inner sep=3pt] at (...) {DẢI 1: TÊN DẢI};`
  * Khung bao giúp người đọc phân biệt ngay lập tức ranh giới giữa các tầng kiến trúc (ví dụ: *Tầng Thực thi ReAct vs Tầng Phản tư Reflexion*, hoặc *Tầng Tiếp nhận vs Kho Chỉ mục vs Tầng Truy vấn*).

#### Nguyên Tắc 4: Định Tuyến Mũi Tên Trực Giao (Orthogonal Manhattan Routing)
* **Tuyệt đối cấm mũi tên đâm xiên chéo:** Không bao giờ vẽ đường mũi tên chéo góc cắt ngang qua mặt các node khác hoặc cắt chéo dải màu, gây ra hiện tượng mắt người bị rối loạn thị giác.
* **Luôn sử dụng đường dẫn góc vuông trực giao:**
  * Dùng cú pháp `|-` (đi dọc trước, đi ngang sau) hoặc `-|` (đi ngang trước, đi dọc sau).
  * Dùng điểm bẻ góc cục bộ: `\draw[arrow] (nodeA.east) -- ++(0.4, 0) |- (nodeB.west);`
  * Đảm bảo mọi đường nối chỉ bao gồm các đoạn thẳng song song với trục hoành ($Ox$) hoặc trục tung ($Oy$).

#### Nguyên Tắc 5: Tách Biệt Hành Lang Định Tuyến Độc Lập (Independent Routing Corridors)
* Khi có từ 2 luồng dữ liệu song song hoặc ngược chiều trở lên:
  * **Phân định cao độ riêng biệt:** Mỗi luồng phải được phân bổ một cao độ trục $y$ độc lập, cách nhau tối thiểu $\ge 0.6\,\text{cm}$.
  * *Ví dụ chuẩn mực trong Hybrid RAG:* Luồng từ khóa $Q$ đi qua hành lang trên $y = -1.2$; luồng trả về kết quả xếp hạng $r_{\text{dense}}$ và $r_{\text{bm25}}$ đi qua hành lang dưới $y = -1.8$. Hai luồng vận hành song song mà không bao giờ đè lên nhau.
  * *Trục hồi quy phản tư (Feedback Loop):* Vòng lặp hồi quy đi ngược chiều phải chạy trên một trục tọa độ dọc thẳng tắp riêng, không đi chung trục với luồng tiến.

#### Nguyên Tắc 6: Nhãn Mũi Tên Cách Ly (Isolated Edge Badge Labels)
* Mọi nhãn chữ đặt trên đường kết nối (`\draw ... node[...] {Nhãn};`) BẮT BUỘC phải có:
  * Nền trắng xóa đường kẻ: `fill=white, inner sep=1.5pt, font=\tiny\bfseries` hoặc `\scriptsize\bfseries`.
  * Hoặc đóng khung badge bo góc: `fill=color!15, draw=color!50, rounded corners=3pt, inner sep=2.5pt`.
  * Tuyệt đối cấm để nhãn chữ trong suốt, vì đường kẻ mũi tên sẽ cắt ngang qua mặt chữ làm cho văn bản bị nát và không thể đọc được.

#### Nguyên Tắc 7: Giới Hạn Khổ Giấy & Tỷ Lệ Thu Phóng (Scale & Page Boundary Invariant)
* Khổ giấy A4 trừ lề trái 3.5cm và lề phải 2.5cm $\rightarrow$ Chiều rộng khả dụng của thân bài là đúng **$15.0\,\text{cm}$**.
* Mọi môi trường `tikzpicture` bắt buộc phải khai báo tỷ lệ thu phóng an toàn:
  `\begin{tikzpicture}[scale=0.74, transform shape, ...]` (hoặc `scale=0.78` đến `scale=0.80`).
* **Kích thước bao ngoài tuyệt đối:** Tổng chiều rộng của sơ đồ trước khi scale (từ tọa độ $x_{\min}$ đến $x_{\max}$) không được vượt quá **$17.5\,\text{cm}$**. Khi áp dụng `scale=0.78`, bề rộng thực tế xuất ra PDF sẽ là $17.5 \times 0.78 \approx 13.65\,\text{cm} \le 15.0\,\text{cm}$, hoàn toàn nằm trọn vẹn trong lề trang, không bao giờ bị đâm thủng lề phải.

---

## PHẦN 4: QUY TẮC BẢNG BIỂU, HÌNH VẼ & DẪN CHIẾU CHÉO

### 4.1. Quy Tắc Đánh Số Phân Cấp (Đánh Số Mục)
* Tối đa gồm 4 chữ số: `Chương.Mục.TiểuMục.Nhóm` (ví dụ: `4.1.2.1`).
* **LUẬT BẤT BIẾN CẤM TIỂU MỤC MỒ CÔI:** Tại mỗi nhóm tiểu mục phải có **ít nhất 2 tiểu mục**. Tuyệt đối không được có mục `2.1.1` mà không có mục `2.1.2` tiếp theo.

### 4.2. Đánh Số Bảng Biểu, Hình Vẽ & Công Thức
* Phải gắn liền với số chương: `Hình X.Y`, `Bảng X.Y`, `Công thức (X.Y)`.
  * *Ví dụ:* `Hình 3.4` là hình thứ 4 trong Chương 3.
* **Vị trí tiêu đề (Caption Placement):**
  * **Đầu đề BẢNG BIỂU: Ghi PHÍA TRÊN bảng** (`\caption` đặt trước `\begin{tabular}` hoặc `\begin{tabularx}`).
  * **Đầu đề HÌNH VẼ: Ghi PHÍA DƯỚI hình** (`\caption` đặt sau `\includegraphics` hoặc `\end{tikzpicture}`).

### 4.3. Luật Cấm Tham Chiếu Tương Đối
* **Tuyệt đối cấm:** *"xem hình dưới đây"*, *"được nêu ở bảng sau"*, *"trong đồ thị trên"*.
* **Bắt buộc dùng tham chiếu mã định danh chuẩn xác:**
  * Dẫn bảng: `... được tổng hợp chi tiết trong Bảng~\ref{tab:...}`.
  * Dẫn hình: `... quy trình xử lý được minh họa tại Hình~\ref{fig:...}`.
  * Dẫn công thức: `... tính toán theo Công thức~(\ref{eq:...})`.

### 4.4. Quy Tắc Từ Viết Tắt & Thuật Ngữ
* Lần đầu xuất hiện trong bài phải viết đầy đủ kèm từ viết tắt trong ngoặc đơn. Ví dụ: *"Trí tuệ nhân tạo (AI - Artificial Intelligence)"*.
* Tuyệt đối không viết tắt trong tiêu đề chương hoặc tiêu đề mục chính.
* Mọi từ viết tắt xuất hiện trong bài phải được tổng hợp tại trang *Danh mục ký hiệu và chữ viết tắt* theo thứ tự bảng chữ cái ABC.

### 4.5. Quy Chuẩn Tài Liệu Tham Khảo (Bibliography)
* **Giới hạn số lượng tài liệu tham khảo ($\le 20$):** Toàn bộ danh mục tài liệu tham khảo của báo cáo đồ án tốt nghiệp bắt buộc phải có số lượng **nhỏ hơn hoặc bằng 20 tài liệu** ($N_{\text{refs}} \le 20$). Ưu tiên các ấn phẩm nền tảng, hội nghị/tạp chí uy tín hàng đầu và quy chế học thuật chính thống; tuyệt đối không đưa vào các trích dẫn mang tính lấp chỗ trống.
* Phân tách rõ ràng thành 2 nhóm: **Tài liệu tiếng Việt** trước, **Tài liệu tiếng Anh** sau.
* Xếp thứ tự ABC:
  * Tác giả nước ngoài: Xếp ABC theo Họ.
  * Tác giả Việt Nam: Xếp ABC theo Tên (giữ nguyên thứ tự thông thường Họ Tên).
* Định dạng trích dẫn theo số ngoặc vuông liên tục: `[1]`, `[2]`, `[3]...`.
* Mọi tài liệu liệt kê ở cuối sách đều phải được trích dẫn ít nhất 1 lần trong nội dung bằng lệnh `\cite{...}` (không trích dẫn mồ côi).

### 4.6. Quy Chuẩn Kỹ Nghệ Bảng Biểu Nâng Cao (Advanced Tabular Engineering)
Để ngăn chặn hoàn toàn lỗi bảng đâm thủng lề trang và đảm bảo tính thẩm mỹ chuẩn mực:
* **Bắt buộc dùng `tabularx` cho văn bản dài:** Mọi bảng có chứa nội dung mô tả, luồng nghiệp vụ hoặc từ điển dữ liệu bắt buộc phải dùng môi trường `tabularx` với độ rộng `\textwidth` (`\begin{tabularx}{\textwidth}{...}`). Sử dụng cột loại `X` (hoặc `>{\raggedright\arraybackslash}X`) để bảng tự động tính toán ngắt dòng chữ, tuyệt đối không dùng `tabular` với toàn cột `l` hay `c` khiến dòng chữ kéo dài vô tận qua mép giấy bên phải.
* **Quy cách kẻ bảng chuẩn mực học thuật (`booktabs`):**
  * Sử dụng đường kẻ ngang dày ở mép trên: `\toprule`.
  * Sử dụng đường kẻ ngang phân cách tiêu đề cột: `\midrule`.
  * Sử dụng đường kẻ ngang dày ở đáy bảng: `\bottomrule`.
  * **Nghiêm cấm lạm dụng đường kẻ dọc (`|c|l|`):** Trong các ấn phẩm khoa học quốc tế, các đường kẻ dọc làm rối mắt và cản trở luồng đọc ngang của mắt; chỉ sử dụng đường kẻ dọc khi thực sự cần thiết trong bảng phân tách Use Case 2 cột (`|p{3.5cm}|X|`).
* **Bảng Đặc tả Ca Sử dụng Chuẩn BA:** Cấu trúc bảng Use Case bắt buộc gồm 2 cột cố định: Cột trái `p{3.5cm}` in đậm danh mục (Mã UC, Tên ca sử dụng, Tác nhân, Tiền điều kiện, Hậu điều kiện, Luồng chính, Luồng ngoại lệ), Cột phải `X` ghi nội dung chi tiết dạng danh sách gạch đầu dòng có thứ tự.

### 4.7. Quy Chuẩn Ký Hiệu Toán Học & Trình Bày Độ Đo (Mathematical Rigor & Typography)
* **Ký hiệu biến và hàm mục tiêu:** Biến số đơn ký tự in nghiêng trong môi trường toán `$q$, $d$, $k$`. Vector hoặc ma trận in đậm $\mathbf{u}$.
* **Quy chuẩn độ đo và tên thuật ngữ nhiều ký tự:** Mọi độ đo, chỉ số đánh giá, hoặc thuật toán viết tắt bắt buộc phải bọc trong lệnh `\text{...}` hoặc `\operatorname{...}`:
  * *Đúng:* $\text{IoU} \ge 0{,}85$, $\text{RRF}(d) = \sum \frac{1}{60 + r_m(d)}$, $\text{Top-1}$, $\text{BLEU}$, $\text{F1-score}$.
  * *Sai:* $IoU \ge 0.85$ (vì LaTeX sẽ hiểu là tích của 3 biến số $I \times o \times U$).
* **Dấu phẩy thập phân tiếng Việt:** Trong toàn bộ các công thức toán và số liệu đo lường tiếng Việt, số thập phân phải bọc dấu phẩy trong cặp ngoặc nhọn: `$0{,}85$`, `$1{,}5\,\text{s}$`, `$1{,}66\,\text{ms}$` để LaTeX không tự chèn khoảng trắng toán học sau dấu phẩy.
* **Đơn vị đo lường:** Luôn có khoảng cách nhỏ ngăn cách giữa số và đơn vị: `$1{,}5\,\text{s}$`, `$1000\,\text{tokens}$`, `$1630\,\text{video}$`.

---

## PHẦN 5: CHIẾN LƯỢC CHẮT LỌC NỘI DUNG TỪ DOCS

Khi chuyển đổi tài liệu từ thư mục `docs/` vào các chương báo cáo, AI phải tuân thủ nghiêm ngặt nguyên tắc **Chắt lọc & Nâng tầm học thuật**, tuyệt đối không sao chép máy móc:

| Chương ĐATN | Nội Dung Cần Chắt Lọc & Diễn Giải Sâu Sắc (KEEP & ELEVATE) | Nội Dung Lược Bỏ Tuyệt Đối (OMIT) |
| :--- | :--- | :--- |
| **Chương 1: Tổng quan về đề tài** | • Bối cảnh bùng nổ nghiên cứu khoa học và hiện tượng ảo giác trích dẫn của LLM.<br>• Hạn chế của ChatPDF (mất bố cục 2 cột, không tọa độ) và Overleaf (không tự sửa lỗi).<br>• Mục tiêu 4 không gian khép kín: Khám phá $\rightarrow$ Đọc sâu $\rightarrow$ GraphRAG $\rightarrow$ Soạn thảo LaTeX.<br>• 4 đóng góp kỹ thuật cốt lõi của đề tài VeriScholar.<br>• Bố cục tổng thể 4 chương của quyển đồ án. | • Ghi chú họp nhóm hoặc phân công task vụn vặt.<br>• Lịch sử dọn dẹp thư mục monorepo.<br>• Các hướng dẫn lệnh git workflow nội bộ. |
| **Chương 2: Cơ sở lý thuyết & Công nghệ** | • Kiến trúc Lục giác (Hexagonal Architecture): Nguyên lý cô lập miền nghiệp vụ thuần khiết.<br>• Tìm kiếm Lai & Thuật toán RRF: Công thức $\text{RRF}(d) = \sum \frac{1}{k + \text{rank}_i(d)}$ ($k=60$), vector HNSW Cosine 1536 chiều và BM25 toàn văn.<br>• Mạng Tri thức Học thuật 4-Thực thể (GraphRAG): Mô hình hóa `Paper`, `Method`, `Dataset`, `MetricResult` trên PostgreSQL `pgvector`.<br>• Tác nhân ReAct LangGraph StateGraph & E2B Sandbox: Vòng lặp 3 bước tự động đọc log và vá lỗi cú pháp LaTeX.<br>• Truyền tải SSE HTTP/1.1 và Phép chuẩn hóa tọa độ hộp chữ PDF `[0..1000]`.<br>• Luận giải khoa học "Tại sao chọn" cho từng công nghệ. | • Mã nguồn cấu hình chi tiết `Dockerfile` hay `docker-compose.yml`.<br>• Danh sách dependencies dài dòng trong `pyproject.toml`.<br>• Cấu hình chi tiết của linter/formatter. |
| **Chương 3: Phân tích & Thiết kế hệ thống** | • Khảo sát nghiệp vụ: Quy trình nghiên cứu tài liệu thực tế của học giả.<br>• 30 Ca sử dụng chuẩn hóa BA: Bảng đặc tả chi tiết tiền/hậu điều kiện, luồng chính, luồng phụ.<br>• Biểu đồ ca sử dụng tổng quan và phân hệ.<br>• Biểu đồ tuần tự UML: Đăng nhập JWT/OTP, Nạp tài liệu 2 tầng CAS, Hỏi đáp Hybrid RAG nhảy trang, Sửa lỗi LaTeX tự động.<br>• Biểu đồ lớp (Class Diagram) và Biểu đồ thành phần.<br>• Thiết kế CSDL 16 bảng PostgreSQL 16: Sơ đồ ERD và bảng Từ điển dữ liệu (Data Dictionary) chi tiết. | • Tên tệp mã nguồn cụ thể (`.py`, `.tsx`) trong sơ đồ khái niệm.<br>• Code test mocks hoặc fixtures kỹ thuật.<br>• Dữ liệu JSON thô chưa qua giải thích. |
| **Chương 4: Cài đặt & Kết quả thực nghiệm** | • Môi trường cài đặt: Cụm máy chủ Azure Ubuntu VM, phần mềm công cụ.<br>• Hình ảnh giao diện người dùng thực tế của 4 phân hệ chính kèm phân tích thao tác nghiệp vụ.<br>• Kết quả thực nghiệm kiểm thử tự động 4 Cổng (Pytest, Vitest, Linter, Build).<br>• Số liệu định lượng đo lường thực tế: Độ trễ kết nối DB 1.66ms, TTFT < 1.5s, IoU khung viền vàng $\ge 0.85$, tỷ lệ tự sửa lỗi LaTeX $\ge 90\%$.<br>• Bằng chứng nhật ký giám sát từ Langfuse Cloud (Trace ID, Tokens, Chi phí). | • Nhật ký lỗi tạm thời trong quá trình phát triển (debug logs).<br>• Khóa bí mật (`OPENAI_API_KEY`, `JWT_SECRET`).<br>• Toàn bộ mã nguồn hàng nghìn dòng (chỉ đưa đoạn thuật toán mẫu vào phụ lục). |
| **Kết luận & Hướng phát triển** | • Tổng kết kết quả đã hoàn thành đối chiếu với 4 đóng góp ban đầu.<br>• Đánh giá khách quan các mặt hạn chế của đề tài (giới hạn 5 bài báo đồng thời, phụ thuộc kết nối E2B Sandbox).<br>• 3 hướng phát triển tiếp theo: Cộng tác thời gian thực CRDT/Yjs, mô hình đa phương thức cho đồ thị ảnh, cụm worker phân tán. | • Nhận định chủ quan không có số liệu chứng minh. |
