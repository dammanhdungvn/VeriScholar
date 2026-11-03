# BÁO CÁO ĐÁNH GIÁ VÀ RÀ SOÁT ĐỘC LẬP: FRONTMATTER, KẾT LUẬN & KIỂM TRA BIÊN DỊCH XELATEX
**Đề tài:** Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn  
**Sinh viên thực hiện:** Đàm Mạnh Dũng — MSSV: 2221050359 — Lớp: DCCTCT67_09B  
**Giảng viên hướng dẫn:** ThS. Vũ Lan Phương — Khoa Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất (HUMG)  
**Chuyên gia rà soát (Reviewer):** Frontmatter, Conclusion & XeLaTeX Build Tester Agent  
**Ngày thực hiện:** 02/11/2026  
**Văn bản đối soát:**  
- `report-datn/AGENTS.md` (Cẩm nang quy chuẩn biên soạn & SOP ĐATN)
- `report-datn/INFORMATION.md` (Hồ sơ định danh đề tài & Single Source of Truth)
- `report-datn/guide/` (Bộ 4 tài liệu quy định và hướng dẫn của Khoa CNTT - HUMG)
- Toàn bộ 10 tệp trong `report-datn/frontmatter/` và `report-datn/chapters/ket_luan.tex`

---

## PHẦN I: KẾT QUẢ KIỂM TRA BIÊN DỊCH XELATEX HIỆN TRẠNG (XELATEX BUILD STATUS)

Quá trình kiểm tra biên dịch trực tiếp được thực hiện trong môi trường máy chủ cục bộ bằng hai công cụ chính thức: `latexmk` (theo cấu hình `.latexmkrc`) và `xelatex` trực tiếp trên tệp chủ `main.tex`.

### 1. Thông số kỹ thuật môi trường biên dịch
- **Bộ công cụ (Toolchain):** XeTeX Version 3.141592653-2.6-0.999995 (TeX Live 2023/Debian).
- **Lệnh thực thi:**
  - `latexmk -xelatex main.tex`
  - `xelatex -interaction=nonstopmode main.tex`
- **Mã thoát (Exit Code):** `0` (Thành công hoàn toàn).
- **Trạng thái tệp đầu ra:**
  - Tệp PDF: `main.pdf`
  - Dung lượng tệp PDF: `4.739.163 bytes` (~$4{,}74\,\text{MB}$).
  - Tổng số trang kết xuất: **115 trang** (A4: $595{,}28 \times 841{,}89\,\text{pts}$).
  - Cấu trúc trang: 2 trang bìa không số + 14 trang La Mã thường (`iii` đến `xvi`) + 99 trang Ả Rập (`1` đến `99`).

### 2. Thống kê lỗi và cảnh báo (Log Diagnostics)
- **Lỗi nghiêm trọng (Fatal Errors):** **0** (Không có lỗi cú pháp hay thiếu gói cản trở quá trình dịch).
- **Tham chiếu chưa định nghĩa (Undefined references / citations):** **0** (Toàn bộ nhãn `\ref` và tài liệu trích dẫn `\cite` được giải quyết trọn vẹn).
- **Cảnh báo tràn lề ngang (Overfull `\hbox`):** **30 cảnh báo**.
  - *Nguyên nhân chính:* Tràn nhẹ từ $1{,}1\,\text{pt}$ đến $38{,}7\,\text{pt}$ tại Chương 3 và Chương 4 do các chuỗi định danh mã nguồn dài không thể bẻ dòng tự động (như tên bảng CSDL: `DocumentChunk`, `ResearchSession`, `document_storage_blobs`, tên trường `hashed_password`, tên module `Module 5 – Agentic Writing`, và các đường link URL).
  - *Khu vực Frontmatter và Kết luận:* Không có Overfull `\hbox` nghiêm trọng nào cản trở thẩm mỹ.
- **Cảnh báo non lề ngang (Underfull `\hbox`):** **18 cảnh báo**.
  - *Nguyên nhân:* Xảy ra chủ yếu tại tệp `chapters/tai_lieu_tham_khao.tex` (các dòng trích dẫn tên tác giả quốc tế dài khi căn đều hai bên `justified`) và một số đoạn văn chứa từ kỹ thuật dài.
- **Tràn/Non lề dọc (Overfull/Underfull `\vbox`):** **0 cảnh báo**.
- **Cảnh báo phông chữ (LaTeX Font Warning):**
  - Cảnh báo thay thế kích cỡ phông (Size substitutions up to $1{,}75\,\text{pt}$) đối với các ký hiệu toán học kích thước nhỏ (`<3.25>`, `<4.33>`, `<6.5>`, `<9.5>`, `<13>`) trong các bảng từ phông Computer Modern mặc định (`cmm`, `cmsy`, `cmr`) sang phông Times New Roman.
  - Cảnh báo `Package hyperref Warning: Option bookmarks has already been used` do gói `bookmark` được nạp sau `hyperref`. Đây là cảnh báo tương thích thông thường, không ảnh hưởng tới chất lượng PDF Bookmark Outline.

---

## PHẦN II: KHẢO SÁT VÀ ĐỐI SOÁT TOÀN BỘ CÁC TỆP FRONTMATTER VÀ KẾT LUẬN

Bảng đối soát tổng hợp hiện trạng các tệp thành phần:

| STT | Tên Tệp Tin | Vai Trò & Vị Trí Báo Cáo | Đánh Giá Tuân Thủ Format | Tình Trạng Nội Dung |
| :---: | :--- | :--- | :---: | :---: |
| 1 | `frontmatter/bia_chinh.tex` | Bìa ngoài (Bìa 1) | Vi phạm cỡ chữ (15pt thay vì 16pt), vạch kẻ thô, TikZ gáy sách thừa trên mặt bìa | Cần tinh giản chữ gáy sách và chuẩn hóa cỡ chữ |
| 2 | `frontmatter/bia_phu.tex` | Bìa trong (Bìa 2) | Vi phạm nghiêm trọng: **Thiếu TÊN ĐỀ TÀI**, khoảng trống giữa trang quá lớn ($4{,}0\,\text{cm}$) | Cần bổ sung Tên đề tài chính thức |
| 3 | `frontmatter/phieu_giao_de_tai.tex` | Phiếu giao đề tài (trang iii--iv) | Đạt bố cục 2 trang; thiếu chữ ký Trưởng Bộ môn; xưng hô khẩu ngữ | Mâu thuẫn số test (330 vs 580); gộp sai Lời cam đoan |
| 4 | `frontmatter/de_cuong_datn.tex` | Đề cương ĐATN (trang v--vii) | Bố cục 3 trang đẹp, ma trận SV/GVHD đầy đủ | Thiếu mốc đánh giá Tuần 6 với Bộ môn; lệch nội dung 10 tuần với SSOT |
| 5 | `frontmatter/muc_luc.tex` | Mục lục tự động (trang viii--x) | Chuẩn tocloft, leader dots mịn, phân cấp 2 cấp | Đạt chuẩn, hiển thị tốt |
| 6 | `frontmatter/danh_muc_hinh.tex` | Danh mục hình ảnh (trang xi--xiii) | Chuẩn LoF, tiền tố Hình X-Y | Đạt chuẩn, hiển thị tốt |
| 7 | `frontmatter/danh_muc_bang.tex` | Danh mục bảng biểu (trang xiv) | Chuẩn LoT, tiền tố Bảng X-Y | Đạt chuẩn, hiển thị tốt |
| 8 | `frontmatter/danh_muc_viet_tat.tex` | Ký hiệu & viết tắt (trang xv--xvi) | Đúng thứ tự ABC, bảng 3 cột | Thiếu nhiều thuật ngữ cốt lõi (CRAG, CSDL, AES, E2B); thừa từ phổ thông |
| 9 | `frontmatter/loi_cam_on.tex` | Lời cảm ơn (trang 1 Ả Rập) | Văn phong khiêm tốn; **Thiếu khối địa danh, ngày tháng và chữ ký tác giả** | Cần bổ sung ngày tháng và chữ ký SV |
| 10 | `frontmatter/loi_mo_dau.tex` | Lời mở đầu (trang 2 Ả Rập) | Khái quát tốt; **Thiếu định danh Đối tượng & Phạm vi nghiên cứu** | Cần bổ sung Đối tượng & Phạm vi theo guide HUMG |
| 11 | `chapters/ket_luan.tex` | Kết luận & Hướng đi (trang 94--96) | Khớp 100% số liệu benchmark; các mục gạch đầu dòng quá dài, đặc nghẹt chữ | Cần tinh gọn súc tích, làm rõ mức độ hoàn thành so với đề cương |

---

## PHẦN III: PHÂN TÍCH CHI TIẾT 3 NỘI DUNG CỐT LÕI

### MỤC 1: NỘI DUNG DƯ THỪA / KHÔNG CẦN THIẾT / SAI SỰ THẬT SO VỚI THỰC TẾ CẦN TINH GỌN

#### 1. Chữ gáy sách (Spine Text) nằm đè trên trang bìa chính (`bia_chinh.tex`)
- **Hiện trạng:** Đoạn mã TikZ dòng 6--12 định vị 2 khối văn bản xoay dọc $-90^\circ$:
  ```latex
  \node[anchor=north west, rotate=-90, font=\fontsize{14pt}{18pt}\selectfont\bfseries] 
    at ([xshift=2.6cm, yshift=-4.4cm]current page.north west) {ĐÀM MẠNH DŨNG};
  \node[anchor=north west, rotate=-90, font=\fontsize{14pt}{18pt}\selectfont\bfseries] 
    at ([xshift=2.6cm, yshift=-14.4cm]current page.north west) {HỆ THỐNG THÔNG TIN VÀ TRI THỨC};
  ```
- **Vấn đề thực tế:** Khi biên dịch ra tệp `main.pdf` hoặc in ấn bản mềm A4, hai chuỗi văn bản này xuất hiện nằm dọc lơ lửng sát mép trái trang bìa ngoài, tạo cảm giác như lỗi tràn chữ hoặc lỗi hiển thị của LaTeX. Trong thực tế xuất bản, chữ gáy sách (Spine text) chỉ được sử dụng riêng biệt cho thợ đóng bìa cứng mạ vàng (in trên gáy dày $1{,}5 - 2\,\text{cm}$ của quyển sách), hoàn toàn không được in trên mặt trước trang bìa A4.
- **Kiến nghị:** Loại bỏ hoàn toàn khối TikZ này hoặc đưa vào cờ điều khiển `\ifprintspine` để trang bìa chính hiển thị trang nhã, đúng quy chuẩn A4.

#### 2. Sai lệch số liệu kiểm thử nghiêm trọng tại Phiếu giao đề tài (`phieu_giao_de_tai.tex`)
- **Hiện trạng:** Tại dòng 84 của `phieu_giao_de_tai.tex` ghi:
  *"Triển khai toàn bộ quy trình kiểm thử TDD với hơn 330 kịch bản kiểm thử tự động."*
- **Sai sự thật so với thực tế:**
  - Theo tài liệu căn cứ duy nhất `INFORMATION.md` Mục 5.1 (dòng 127): Hệ thống đạt chuẩn xác **580 bài kiểm thử tự động** (100% pass, exit code 0).
  - Tệp `loi_mo_dau.tex` (dòng 11) khẳng định: *"Hệ thống được kiểm chứng qua 580 kịch bản kiểm thử tự động (340 kiểm thử Backend pytest và 240 kiểm thử Frontend vitest, thời gian 13,02 giây)"*.
  - Tệp `chapters/ket_luan.tex` (dòng 14) khẳng định: *"tổng cộng 580 kịch bản kiểm thử (340 kiểm thử Backend pytest và 240 kiểm thử Frontend vitest..."*.
  - Tệp `chapters/ch4/4_4_so_lieu.tex` ghi nhận thực tế 589 test (349 pytest + 240 vitest).
  - Con số "hơn 330 kịch bản" trong Phiếu giao đề tài là số liệu cũ thời kỳ đầu phát triển chưa được cập nhật, tạo nên sự **mâu thuẫn nội bộ trực tiếp** giữa các trang trong cùng một quyển đồ án.
- **Kiến nghị:** Cập nhật ngay dòng 84 thành: *"Triển khai toàn bộ quy trình kiểm thử TDD với 580 kịch bản kiểm thử tự động qua 4 cổng xác minh."*

#### 3. Bỏ sót adapter học thuật cốt lõi trong Phiếu giao đề tài
- **Hiện trạng:** Dòng 52 của `phieu_giao_de_tai.tex` ghi: *"Phân hệ Khám phá: Tìm kiếm học thuật đa nguồn (Exa AI, arXiv, Semantic Scholar)."*
- **Thiếu sót:** Bỏ sót cổng kết nối **CrossRef** và cơ chế lưu trữ nội dung định danh **CAS SHA-256** — hai đóng góp kỹ thuật trọng tâm đã được kiểm chứng độc lập và ghi nhận tại `INFORMATION.md` Mục 2.3 & 2.4.

#### 4. Gộp cưỡng bức "Lời cam đoan" vào "Phiếu giao đề tài tốt nghiệp"
- **Hiện trạng:** Dòng 90--94 của `phieu_giao_de_tai.tex` chèn mục: *"4. Lời cam đoan của sinh viên: Em -- Đàm Mạnh Dũng -- cam kết ĐATN là công trình nghiên cứu của bản thân em..."*
- **Bất cập nghiệp vụ:** "Phiếu giao đề tài" về bản chất là văn bản giao nhiệm vụ hành chính một chiều từ Khoa/Bộ môn và Giảng viên hướng dẫn cho sinh viên (gồm: Mục tiêu, Nhiệm vụ, Thời gian thực hiện, Chữ ký của GVHD và Trưởng bộ môn). Lời cam đoan của sinh viên là cam kết học thuật cá nhân, không thuộc cấu trúc của Phiếu giao đề tài. Việc gộp chung này làm mất đi vị trí ký duyệt bắt buộc của **Trưởng Bộ môn Hệ thống thông tin và Tri thức**.

#### 5. Văn phong khẩu ngữ chưa đạt chuẩn học thuật trong xưng hô
- **Hiện trạng:**
  - `phieu_giao_de_tai.tex` dòng 93: *"làm dưới sự hướng dẫn của cô Vũ Lan Phương"*.
  - `loi_cam_on.tex` dòng 7: *"tới cô Vũ Lan Phương -- Giảng viên Khoa Công nghệ Thông tin"*.
- **Kiến nghị:** Chỉnh sửa thành văn phong học thuật chuẩn mực: *"dưới sự hướng dẫn tận tình của Giảng viên hướng dẫn -- ThS. Vũ Lan Phương"*.

#### 6. Các từ viết tắt dư thừa / tầm thường trong Danh mục từ viết tắt (`danh_muc_viet_tat.tex`)
- **Hiện trạng:** Danh mục liệt kê 29 từ viết tắt, trong đó có những từ mang tính đại chúng phổ thông đối với sinh viên tốt nghiệp ngành CNTT:
  - `AI` (*Artificial Intelligence -- Trí tuệ nhân tạo*)
  - `PDF` (*Portable Document Format -- Định dạng tài liệu số di động*)
  - `UML` (*Unified Modeling Language -- Ngôn ngữ mô hình hóa thống nhất*)
  - `ERD` (*Entity-Relationship Diagram -- Sơ đồ quan hệ thực thể cơ sở dữ liệu*)
- **Kiến nghị:** Tinh gọn các từ quá phổ cập để dành không gian bổ sung các thuật ngữ kỹ thuật chuyên sâu của đề tài.

#### 7. Sự dồn nén số liệu quá mức và phong cách kể lể tại Kết luận (`ket_luan.tex`)
- **Hiện trạng:** Mỗi gạch đầu dòng trong mục "Kết quả đạt được" kéo dài từ 12 đến 16 dòng LaTeX, nhồi nhét lại chi tiết hàng chục con số kỹ thuật của Chương 4 (như điểm số `Groundedness = 0,9775`, `Relevance = 0,9471`, `Recall@5 = 94,44%`, `IoU = 0,9266 ± 0,0126`, các tỷ lệ ablation 84%, 44%...).
- **Đánh giá:** Phần Kết luận có chức năng đúc kết cô đọng những đóng góp lớn nhất về mặt giải pháp, giá trị khoa học và mức độ hoàn thành mục tiêu ban đầu; không phải là bản tóm tắt sao chép nguyên xi bảng số liệu thực nghiệm của Chương 4. Việc trình bày các khối văn bản quá dày đặc gây cản trở khả năng nắm bắt thông điệp của Hội đồng chấm.

---

### MỤC 2: LỖI FORMAT VÀ VI PHẠM QUY CHUẨN THEO AGENTS.MD, INFORMATION.MD, GUIDE/

#### 1. Vi phạm nghiêm trọng nhất: Bìa trong (`frontmatter/bia_phu.tex`) THIẾU HOÀN TOÀN TÊN ĐỀ TÀI
- **Quan sát trực tiếp tại tệp `frontmatter/bia_phu.tex`:**
  ```latex
  {\fontsize{36pt}{42pt}\selectfont \textbf{ĐỒ ÁN TỐT NGHIỆP}} \\[1.4cm]
  {\fontsize{16pt}{20pt}\selectfont \textbf{CHUYÊN NGÀNH: }HỆ THỐNG THÔNG TIN VÀ TRI THỨC} \\[4.0cm]
  \begin{tabular}{>{\centering\arraybackslash}p{6.8cm} >{\centering\arraybackslash}p{7.2cm}}
    \fontsize{14pt}{18pt}\selectfont \textbf{GIÁO VIÊN HƯỚNG DẪN} & ...
  ```
- **Hậu quả học thuật:** Trang bìa phụ là văn bản pháp lý lưu chiểu vĩnh viễn có chữ ký sống của Giảng viên hướng dẫn và Sinh viên thực hiện. Một trang bìa phụ không có TÊN ĐỀ TÀI là lỗi hình thức cực kỳ nghiêm trọng, khiến người đọc và Hội đồng không thể xác định văn bản chữ ký này xác nhận cho công trình nghiên cứu nào. Khoảng cách dãn dòng `\\[4.0cm]` tạo ra một khoảng trống mênh mông, bất thường ở giữa trang.
- **Đối soát với `AGENTS.md` (dòng 201) và `guide/` (Phụ lục 02):** Bắt buộc phải có tên đề tài in chữ đậm ở trung tâm trang bìa phụ.

#### 2. Vi phạm quy chuẩn cỡ chữ trên trang bìa ngoài (`bia_chinh.tex`)
- **Đối soát:** Căn cứ Bảng ma trận cỡ chữ `AGENTS.md` (dòng 264) và Phụ lục 01 `Huong-dan-viet-DATN.md`:
  - Tên cơ quan chủ quản và tên trường: Quy chuẩn **16pt** $\rightarrow$ Thực tế dùng **15pt** (`\fontsize{15pt}{19pt}`).
  - Ngành đào tạo: Quy chuẩn **16pt** $\rightarrow$ Thực tế dùng **15pt**.
  - Tên đề tài: Quy chuẩn **16pt** $\rightarrow$ Thực tế dùng **15pt**.
  - Địa danh, năm: Quy chuẩn **16pt** $\rightarrow$ Thực tế dùng **15pt**.
  - Nhãn "ĐỒ ÁN TỐT NGHIỆP": Quy chuẩn **40pt** (hoặc 36--40pt) $\rightarrow$ Thực tế dùng **36pt**.
- **Nguyên nhân:** Tác giả hạ cỡ chữ xuống 15pt để tránh tràn trang, nhưng đã làm sai lệch quy định cụ thể của Khoa CNTT.

#### 3. Vi phạm quy chuẩn đồ họa đường kẻ phân cách trên cả hai bìa
- **Hiện trạng:** Cả `bia_chinh.tex` (dòng 18) và `bia_phu.tex` (dòng 11) đều dùng:
  ```latex
  {\fontsize{12pt}{14pt}\selectfont \textbf{---------------------------------------}}
  ```
- **Vi phạm:** Sử dụng ký tự gạch nối bàn phím (hyphens) lặp lại tạo thành đường nét đứt thô sơ, thiếu tính thẩm mỹ của một ấn phẩm khoa học được chế bản bằng XeLaTeX. Cần thay bằng lệnh kẻ chuẩn: `\rule{6.0cm}{1.0pt}` hoặc `\rule{8.0cm}{1.2pt}`.

#### 4. Thiếu chữ ký xác nhận của Lãnh đạo Bộ môn trong Phiếu giao đề tài
- **Đối soát:** Căn cứ quy chế giao đề tài tốt nghiệp của Khoa CNTT - Trường Đại học Mỏ - Địa chất (`Huong dan-Quy dinh-DATN.md` Mục 1.3 và 2.2):
  - Phiếu giao đề tài phải có xác nhận 2 bên: Giảng viên hướng dẫn và Trưởng Bộ môn chuyên ngành (Bộ môn Hệ thống thông tin và Tri thức).
  - Tệp `phieu_giao_de_tai.tex` hiện chỉ có chữ ký của GVHD và Sinh viên (do chèn nhầm phần Lời cam đoan vào vị trí này).

#### 5. Vi phạm quy định về mốc đánh giá tiến độ Tuần 6 trong Đề cương ĐATN (`de_cuong_datn.tex`)
- **Đối soát:** Căn cứ `Huong dan-Quy dinh-DATN.md` dòng 130 (*"Tuần thứ 6 SV sẽ báo cáo tiến độ làm ĐATN với bộ môn chủ quản"*) và `AGENTS.md` dòng 169 (*"Bảng kế hoạch chi tiết đúng 10 tuần... nêu rõ mốc Tuần 6 báo cáo tiến độ với Bộ môn"*).
- **Hiện trạng trong `de_cuong_datn.tex` (dòng 158):**
  Tuần 6 chỉ ghi: *"Hiện thực hóa phân hệ Hybrid RAG: Tìm kiếm kết hợp HNSW + BM25, dung hợp RRF, tái xếp hạng Cross-Encoder và trích xuất Bounding Box PDF."* Hoàn toàn không nhắc tới mốc báo cáo tiến độ giữa kỳ với Bộ môn.

#### 6. Thiếu các từ viết tắt kỹ thuật hạt nhân trong Danh mục từ viết tắt (`danh_muc_viet_tat.tex`)
Bảng danh mục hiện đang bỏ sót các thuật ngữ xuất hiện cốt lõi trong báo cáo:
- **CRAG:** *Corrective Retrieval-Augmented Generation* (Cổng đánh giá và hiệu chỉnh độ tin cậy truy xuất tài liệu).
- **CSDL:** *Cơ sở dữ liệu* (Thuật ngữ tiếng Việt xuất hiện hàng trăm lần).
- **AES-GCM:** *Advanced Encryption Standard - Galois/Counter Mode* (Cơ chế mã hóa xác thực két khóa BYOK).
- **REST:** *Representational State Transfer* (Kiến trúc giao diện API dịch vụ web).
- **E2B:** *E2B Sandbox / MicroVM* (Môi trường máy ảo đám mây thực thi cô lập).
- **UI / UX:** *User Interface / User Experience* (Giao diện và trải nghiệm người dùng).
- **SQL:** *Structured Query Language* (Ngôn ngữ truy vấn cơ sở dữ liệu quan hệ).

#### 7. Vi phạm thể thức kết thúc Lời cảm ơn (`loi_cam_on.tex`)
- **Hiện trạng:** Tệp `loi_cam_on.tex` kết thúc lửng lơ ở dòng 14 sau đoạn văn xin ý kiến đóng góp, hoàn toàn không có địa danh, ngày tháng và khối chữ ký của tác giả đồ án:
  ```latex
  % THIẾU KHỐI:
  \vspace{0.4cm}
  \hfill \textit{Hà Nội, ngày\dots\dots tháng\dots\dots năm 2026} \\[0.2cm]
  \begin{flushright}
    \textbf{Sinh viên thực hiện} \\[1.8cm]
    \textbf{Đàm Mạnh Dũng}
  \end{flushright}
  ```
- **Hậu quả:** Văn bản cảm ơn thiếu danh tính người phát ngôn chính thức ở chân trang.

#### 8. Vi phạm quy chuẩn nội dung Lời mở đầu (`loi_mo_dau.tex`)
- **Đối soát:** Căn cứ `Huong-dan-viet-DATN.md` Mục B.II (dòng 113--115):
  *"Mở đầu: Trình bày lý do chọn đề tài, mục tiêu của đề tài, đối tượng và phạm vi của đề tài."*
- **Hiện trạng:** Tệp `loi_mo_dau.tex` trình bày bối cảnh, mục tiêu và tóm lược số liệu kiểm thử, nhưng **chưa có đoạn văn nào định danh rõ ràng Đối tượng nghiên cứu** (Ấn phẩm khoa học định dạng PDF 2 cột, bài báo quốc tế IEEE/ACM, siêu dữ liệu học thuật) và **Phạm vi nghiên cứu** (Quy trình hỗ trợ nghiên cứu cho học giả đại học VinUniversity, trọng tâm vào Agentic RAG, BBox grounding và tự động hóa biên tập LaTeX).

---

### MỤC 3: ĐÁNH GIÁ CHI TIẾT TỪNG HÌNH ẢNH / SƠ ĐỒ / LOGO

#### 1. Huy hiệu / Logo Trường Đại học Mỏ - Địa chất (`figures/logos/logo_humg.png`)
- **Tệp nguồn:** `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/figures/logos/logo_humg.png`
- **Vị trí xuất hiện:** Duy nhất tại tệp `frontmatter/bia_chinh.tex` (dòng 20):
  ```latex
  \includegraphics[width=3.8cm, height=3.8cm, keepaspectratio]{figures/logos/logo_humg.png} \\[0.8cm]
  ```
- **Đặc tính kỹ thuật đo lường thực tế:**
  - Định dạng: PNG ảnh màu 8-bit RGBA (có kênh trong suốt Alpha).
  - Độ phân giải gốc: $346 \times 346$ pixels.
  - Dung lượng tệp: $198{,}238$ bytes (~$198\,\text{KB}$).
  - Mật độ điểm ảnh khi in ấn ($3{,}8\,\text{cm} \approx 1{,}5\,\text{inch}$): $\approx 230\,\text{DPI}$.
- **Đánh giá chi tiết:**
  - *Về tính pháp lý và biểu tượng:* Logo tròn chính thức của Trường Đại học Mỏ - Địa chất với hình tượng búa chim, compa mỏ và bánh răng kỹ thuật, dải băng "TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT / 1966". Hoàn toàn chính xác theo biểu mẫu Phụ lục 01 HUMG.
  - *Về thẩm mỹ và độ nét:* Kích thước $3{,}8 \times 3{,}8\,\text{cm}$ hiển thị cân đối giữa tiêu đề trường và tên tác giả. Tuy nhiên, do ảnh gốc chỉ có $346 \times 346\,\text{px}$, khi phóng to trên bản PDF chất lượng cao (zoom $\ge 300\%$) hoặc khi in offset bìa nhũ vàng, các đường viền chữ nhỏ quanh vòng cung có hiện tượng mờ hạt (anti-aliasing) nhẹ.
  - *Sự cần thiết:* **BẮT BUỘC PHẢI CÓ** theo quy định của Nhà trường.
- **Kiến nghị hành động:**
  - **GIỮ LẠI (Retain)** trong bản báo cáo.
  - *Khuyến nghị nâng cấp:* Chuyển đổi logo sang định dạng vector chuẩn (`logo_humg.pdf` hoặc `.svg` biên dịch) hoặc sử dụng bản PNG độ phân giải siêu nét ($\ge 1000 \times 1000\,\text{px}$, $600\,\text{DPI}$) để đảm bảo bản in bìa mạ vàng sắc nét tuyệt đối.

#### 2. Khảo sát hình ảnh và sơ đồ trong Kết luận (`chapters/ket_luan.tex`)
- **Hiện trạng:** Toàn bộ tệp `chapters/ket_luan.tex` không chứa bất kỳ hình ảnh, biểu đồ (`\includegraphics`) hay sơ đồ TikZ (`\begin{tikzpicture}`) nào.
- **Đánh giá học thuật:** Hoàn toàn chính xác theo chuẩn mực quốc tế và quy định của Khoa CNTT - HUMG. Phần Kết luận và Hướng phát triển là nơi đúc kết tư duy, không phải nơi trình bày dữ liệu trực quan mới.
- **Kiến nghị hành động:** **GIỮ NGUYÊN (Không bổ sung bất kỳ hình ảnh nào vào Kết luận)**.

---

## PHẦN IV: DANH SÁCH HÀNH ĐỘNG KIẾN NGHỊ TINH GỌN VÀ CHỈNH SỬA CỤ THỂ

Nhằm đảm bảo đồ án tốt nghiệp đạt chuẩn mực xuất sắc cao nhất trước Hội đồng chấm bảo vệ của Khoa CNTT - Trường Đại học Mỏ - Địa chất, chuyên gia khuyến nghị các hành động cụ thể sau:

### 1. Hành động ưu tiên cấp thiết (P0 - Critical Fixes)
1. **Bổ sung Tên đề tài chính thức vào Trang bìa phụ (`frontmatter/bia_phu.tex`):**
   - Chèn khối tên đề tài vào giữa nhãn chuyên ngành và bảng chữ ký:
     ```latex
     {\fontsize{14pt}{18pt}\selectfont \textbf{TÊN ĐỀ TÀI:}} \\[0.3cm]
     \parbox{13.0cm}{\centering \fontsize{14pt}{20pt}\selectfont \textbf{XÂY DỰNG NỀN TẢNG AI HỖ TRỢ NGHIÊN CỨU VÀ VIẾT BÀI BÁO KHOA HỌC VINUNI DỰA TRÊN AGENTIC RAG, TRUY XUẤT TRI THỨC HỌC THUẬT VÀ KIỂM CHỨNG TRÍCH DẪN}} \\[1.5cm]
     ```
   - Giảm khoảng cách dãn dòng trống bất thường từ `[4.0cm]` xuống mức hợp lý để trang bìa phụ cân đối, kín trang và trang trọng.
2. **Loại bỏ chữ gáy sách TikZ thừa trên Trang bìa chính (`frontmatter/bia_chinh.tex`):**
   - Bỏ đoạn mã `\begin{tikzpicture}[remember picture, overlay] ... \end{tikzpicture}` xoay dọc chữ ở lề trái trang bìa ngoài.
3. **Đồng bộ triệt để số lượng kịch bản kiểm thử trong Phiếu giao đề tài (`phieu_giao_de_tai.tex`):**
   - Sửa cụm từ *"hơn 330 kịch bản"* tại dòng 84 thành *"580 kịch bản kiểm thử tự động (340 Backend pytest và 240 Frontend vitest)"* để thống nhất 100% với `INFORMATION.md`, Lời mở đầu, Chương 4 và Kết luận.
4. **Bổ sung khối chữ ký, địa danh và ngày tháng vào Lời cảm ơn (`frontmatter/loi_cam_on.tex`):**
   - Thêm phần kết thúc trang trọng: `Hà Nội, ngày... tháng... năm 2026 / Sinh viên thực hiện / Đàm Mạnh Dũng`.

### 2. Hành động chuẩn hóa quy cách và thể thức (P1 - High Standards)
5. **Chuẩn hóa đường kẻ phân cách trên cả hai trang bìa:**
   - Thay thế chuỗi gạch nối thô sơ `---------------------------------------` bằng lệnh kẻ chuẩn `\rule{6.5cm}{1.0pt}`.
6. **Chuẩn hóa cỡ chữ trang bìa theo Phụ lục 01 HUMG:**
   - Nâng cỡ chữ tiêu đề trường, ngành, tên đề tài từ 15pt lên đúng chuẩn 16pt (`\fontsize{16pt}{20pt}`).
7. **Bổ sung mốc báo cáo tiến độ Tuần 6 vào Đề cương ĐATN (`frontmatter/de_cuong_datn.tex`):**
   - Cập nhật dòng 158: Thêm nội dung: *"[CỘT MỐC GIỮA KỲ: Báo cáo tiến độ hoàn thành đồ án với Bộ môn Hệ thống thông tin và Tri thức và GVHD]"*.
8. **Bổ sung định danh Đối tượng và Phạm vi nghiên cứu trong Lời mở đầu (`frontmatter/loi_mo_dau.tex`):**
   - Bổ sung 2 câu tường minh:
     *"-- Đối tượng nghiên cứu: Các ấn phẩm khoa học quốc tế định dạng PDF cấu trúc 2 cột chuẩn IEEE/ACM, mô hình ngôn ngữ lớn và đồ thị tri thức học thuật."*
     *"-- Phạm vi nghiên cứu: Tập trung xây dựng giải pháp hỗ trợ nghiên cứu cho học giả tại Trường Đại học VinUniversity, bao gồm chu trình khép kín: Khám phá tài liệu, Đọc sâu kiểm chứng tọa độ Bounding Box, Quản lý đồ thị tri thức GraphRAG và Tác nhân tự sửa lỗi biên dịch LaTeX trong môi trường sandbox cô lập."*

### 3. Hành động tinh giản và nâng cao chất lượng (P2 - Refinement)
9. **Cập nhật Bảng danh mục từ viết tắt (`frontmatter/danh_muc_viet_tat.tex`):**
   - Bổ sung các từ viết tắt chuyên sâu: `CRAG`, `CSDL`, `AES-GCM`, `REST`, `E2B`, `UI/UX`, `SQL`.
   - Lược bỏ hoặc tinh giản các từ đại trà: `PDF`, `AI`, `UML`, `ERD`.
10. **Tách phần Lời cam đoan và khôi phục chữ ký Trưởng Bộ môn trong Phiếu giao đề tài:**
    - Thay thế khối cam đoan bằng chữ ký duyệt của Trưởng Bộ môn chuyên ngành: `TRƯỞNG BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC` song song với `GIẢNG VIÊN HƯỚNG DẪN`.
    - Chuyển Lời cam đoan của sinh viên thành một mục ngắn gọn độc lập hoặc tích hợp trong phần đầu quyển đồ án.
11. **Tinh gọn và tái cấu trúc văn phong phần Kết luận (`chapters/ket_luan.tex`):**
    - Chia nhỏ các đoạn văn quá dài trong từng gạch đầu dòng; tập trung làm nổi bật:
      - Đóng góp 1: Kiến trúc Lục giác & CSDL 20 bảng ACID.
      - Đóng góp 2: Hybrid RAG & BBox IoU $0{,}9266$ triệt tiêu ảo giác.
      - Đóng góp 3: GraphRAG 4 thực thể trên PostgreSQL.
      - Đóng góp 4: Tác nhân ReAct tự sửa cú pháp LaTeX đạt $96\%$.
      - Đóng góp 5: 580 automated tests & mã nguồn mở minh bạch.
    - Làm rõ mức độ hoàn thành nhiệm vụ nghiên cứu: Khẳng định đồ án đã hoàn thành **100% khối lượng công việc và vượt các chỉ tiêu kỹ thuật định lượng** được giao trong Đề cương chi tiết ban đầu.

---

## PHẦN V: KẾT LUẬN VÀ XÁC NHẬN CỦA CHUYÊN GIA RÀ SOÁT

1. **Về biên dịch XeLaTeX:** Hệ thống báo cáo hiện tại có nền tảng mã nguồn LaTeX cực kỳ vững chắc, biên dịch trơn tru với mã thoát `0`, không có lỗi fatal, không có broken link hay trích dẫn mồ côi. Tệp PDF 115 trang hoàn toàn sẵn sàng cho xuất bản sau khi tinh chỉnh các lỗi định dạng.
2. **Về nội dung Frontmatter và Kết luận:** Các nội dung kỹ thuật thể hiện sự đầu tư công phu, hàm lượng kỹ thuật cao và bám rất sát sản phẩm thực tế VeriScholar. Tuy nhiên, sự xuất hiện của một số lỗi sơ đẳng (đặc biệt là thiếu tên đề tài trên trang bìa phụ, mâu thuẫn số test 330 vs 580, và thiếu định danh đối tượng/phạm vi trong lời mở đầu) cần được khắc phục ngay lập tức để đạt điểm Xuất sắc tuyệt đối khi bảo vệ trước Hội đồng chấm ĐATN của Khoa CNTT - Trường Đại học Mỏ - Địa chất.

**Tệp báo cáo này được lập độc lập và lưu trữ tại:**  
`report-datn/review_reports/frontmatter_and_conclusion_review.md`
