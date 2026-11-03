# BÁO CÁO KẾT QUẢ TRIỂN KHAI CHUẨN HÓA VÀ TINH GỌN: FRONTMATTER VÀ KẾT LUẬN

**Đề tài:** Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn  
**Hệ thống:** Nền tảng Trợ lý Nghiên cứu Khoa học VeriScholar (*VeriScholar Academic AI Platform*)  
**Sinh viên thực hiện:** Đàm Mạnh Dũng — MSSV: 2221050359 — Lớp: DCCTCT67_09B  
**Giảng viên hướng dẫn:** ThS. Vũ Lan Phương — Khoa Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất (HUMG)  
**Đơn vị thực hiện:** Subagent Worker Frontmatter & Kết luận (`worker_frontmatter_impl`)  
**Ngày hoàn thành:** 02/11/2026  
**Văn bản căn cứ và đối soát:**  
- `report-datn/AGENTS.md` (Cẩm nang quy chuẩn biên soạn & SOP ĐATN)
- `report-datn/INFORMATION.md` (Hồ sơ định danh đề tài & Single Source of Truth — SSOT)
- `report-datn/guide/` (Bộ 4 tài liệu quy định và hướng dẫn của Khoa CNTT - HUMG)
- `report-datn/review_reports/frontmatter_and_conclusion_review.md` (Báo cáo đánh giá hiện trạng)
- `report-datn/review_reports/SUMMARY_REVIEW.md` (Bản kế hoạch triển khai tổng thể)

---

## I. TỔNG QUAN PHẠM VI TRIỂN KHAI VÀ KẾT QUẢ BIÊN DỊCH

### 1. Phạm vi tệp tin đã chỉnh sửa
Tuân thủ nghiêm ngặt ranh giới thẩm quyền (Scope Boundary), subagent chỉ thực hiện hiệu chỉnh đúng 8 tệp tin được phân công và tạo 01 tệp báo cáo kết quả:
1. `report-datn/frontmatter/bia_phu.tex` (Trang bìa trong / Bìa 2)
2. `report-datn/frontmatter/bia_chinh.tex` (Trang bìa ngoài / Bìa 1)
3. `report-datn/frontmatter/phieu_giao_de_tai.tex` (Phiếu giao đề tài tốt nghiệp)
4. `report-datn/frontmatter/de_cuong_datn.tex` (Đề cương 10 tuần thực hiện ĐATN)
5. `report-datn/frontmatter/danh_muc_viet_tat.tex` (Danh mục ký hiệu và chữ viết tắt)
6. `report-datn/frontmatter/loi_cam_on.tex` (Lời cảm ơn)
7. `report-datn/frontmatter/loi_mo_dau.tex` (Lời mở đầu)
8. `report-datn/chapters/ket_luan.tex` (Kết luận và Hướng phát triển)

### 2. Kết quả kiểm chứng biên dịch XeLaTeX
- **Bộ công cụ (Toolchain):** XeTeX Version 3.141592653-2.6-0.999995 (TeX Live 2023/Debian).
- **Lệnh thực thi:** `cd report-datn && xelatex -interaction=nonstopmode main.tex`
- **Mã thoát (Exit Code):** `0` (Thành công tuyệt đối).
- **Lỗi nghiêm trọng (Fatal Errors):** `0`.
- **Cảnh báo tràn lề (Overfull \hbox) tại các tệp thuộc phạm vi:** **0 cảnh báo** (Lỗi tràn 12.3pt ban đầu tại `ket_luan.tex` đã được xử lý triệt để).
- **Tham chiếu chưa định nghĩa (Undefined references / citations):** `0`.
- **Trạng thái bố cục trang:** Toàn bộ phần Frontmatter và Kết luận giữ đúng phân trang, không phát sinh trang trắng thừa, số trang La Mã thường và Ả Rập chuyển tiếp mượt mà.

---

## II. CHI TIẾT CÁC THAY ĐỔI THEO TỪNG TỆP TIN

### 1. Trang bìa phụ (`report-datn/frontmatter/bia_phu.tex`)

#### 1.1. Hiện trạng trước khi sửa
- **Lỗi nghiêm trọng nhất:** Hoàn toàn thiếu TÊN ĐỀ TÀI nghiên cứu ở trung tâm trang bìa phụ.
- Khoảng cách dãn dòng `\\[4.0cm]` tạo khoảng trống bất thường, trống trải ở giữa trang.
- Đường kẻ phân cách sử dụng chuỗi ký tự gạch nối bàn phím thô sơ: `---------------------------------------`.
- Cỡ chữ dòng cơ quan chủ quản và trường dùng 15pt thay vì chuẩn 16pt theo Phụ lục 02 HUMG.

#### 1.2. Nội dung đã thực hiện
- Bổ sung khối TÊN ĐỀ TÀI chính thức in hoa đậm, căn giữa cân đối theo đúng Phụ lục 02 HUMG:
  ```latex
  {\fontsize{14pt}{18pt}\selectfont \textbf{TÊN ĐỀ TÀI:}} \\[0.35cm]
  \parbox{13.2cm}{\centering \fontsize{14pt}{20pt}\selectfont \textbf{XÂY DỰNG NỀN TẢNG AI HỖ TRỢ NGHIÊN CỨU VÀ VIẾT BÀI BÁO KHOA HỌC VINUNI DỰA TRÊN AGENTIC RAG, TRUY XUẤT TRI THỨC HỌC THUẬT VÀ KIỂM CHỨNG TRÍCH DẪN}} \\[1.8cm]
  ```
- Nâng cỡ chữ tiêu đề trường và chuyên ngành lên 16pt (`\fontsize{16pt}{20pt}`).
- Thay thế chuỗi gạch nối bằng lệnh kẻ chuẩn học thuật: `\rule{6.5cm}{1.0pt}`.
- Tinh chỉnh khoảng cách giữa các khối (`\\[1.8cm]`, `\\[1.0cm]`, `\\[1.2cm]`) để trang bìa phụ kín trang, trang trọng và cân đối.

---

### 2. Trang bìa chính (`report-datn/frontmatter/bia_chinh.tex`)

#### 2.1. Hiện trạng trước khi sửa
- Mã TikZ định vị chữ gáy sách (Spine Text: "ĐÀM MẠNH DŨNG", "HỆ THỐNG THÔNG TIN VÀ TRI THỨC") xoay $-90^\circ$ nằm đè sát mép trái trang bìa ngoài A4, gây mất thẩm mỹ khi xem PDF hoặc in ấn.
- Chuỗi gạch nối bàn phím thô `---------------------------------------`.
- Tiêu đề cơ quan, trường, ngành và tên đề tài dùng cỡ chữ 15pt, chưa chuẩn 16pt theo Phụ lục 01 HUMG.

#### 2.2. Nội dung đã thực hiện
- Loại bỏ hoàn toàn khối mã TikZ xoay gáy sách đè lề trái.
- Thay chuỗi gạch nối bằng lệnh `\rule{6.5cm}{1.0pt}`.
- Chuẩn hóa toàn bộ cỡ chữ lên 16pt (`\fontsize{16pt}{20pt}`):
  - `BỘ GIÁO DỤC VÀ ĐÀO TẠO` (16pt)
  - `TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT` (16pt)
  - `NGÀNH CÔNG NGHỆ THÔNG TIN` (16pt)
  - `TÊN ĐỀ TÀI:` (16pt)
  - Tên đề tài: `\parbox{13.2cm}{\centering \fontsize{16pt}{22pt}\selectfont \textbf{...}}`
  - `Hà Nội -- Năm 2026` (16pt)
- Giữ nguyên logo Trường ĐH Mỏ - Địa chất (`logo_humg.png`, $3{,}8 \times 3{,}8\,\text{cm}$).
- Cân đối các khoảng trống dọc đảm bảo bìa chính nằm trọn vẹn trong đúng 1 trang A4.

---

### 3. Phiếu giao đề tài tốt nghiệp (`report-datn/frontmatter/phieu_giao_de_tai.tex`)

#### 3.1. Hiện trạng trước khi sửa
- Mâu thuẫn số liệu kiểm thử: dòng 84 ghi *"hơn 330 kịch bản kiểm thử tự động"*, trong khi SSOT (`INFORMATION.md`), Lời mở đầu, Chương 4 và Kết luận đều khẳng định chuẩn xác 580 test.
- Phân hệ Khám phá (dòng 52) bỏ sót bộ điều hợp học thuật cốt lõi **CrossRef** và kho lưu trữ định danh **CAS SHA-256**.
- Gộp Lời cam đoan của sinh viên vào phiếu giao đề tài với văn phong khẩu ngữ: *"làm dưới sự hướng dẫn của cô Vũ Lan Phương"*.
- Bảng chữ ký chỉ có GVHD và Sinh viên, thiếu chữ ký pháp lý bắt buộc của **Trưởng Bộ môn Hệ thống thông tin và Tri thức**.

#### 3.2. Nội dung đã thực hiện
- Bổ sung bộ điều hợp học thuật: *"Phân hệ Khám phá: Tìm kiếm học thuật đa nguồn (arXiv, Semantic Scholar, CrossRef) và lưu trữ CAS SHA-256."*
- Đồng bộ số liệu kiểm thử: *"Triển khai toàn bộ quy trình kiểm thử TDD với 580 kịch bản kiểm thử tự động (340 Backend pytest và 240 Frontend vitest, 100\% pass)."*
- Chuẩn hóa Mục 4 thành cam kết độc lập với ngôn từ học thuật chuẩn mực:
  *"Tôi -- Đàm Mạnh Dũng -- cam đoan ĐATN là công trình nghiên cứu độc lập của bản thân, được thực hiện dưới sự hướng dẫn của ThS. Vũ Lan Phương. Mọi kết quả, số liệu và mã nguồn trình bày trong đồ án hoàn toàn trung thực, không sao chép nguyên văn bất kỳ công trình nào khác."*
- Tái cấu trúc bảng chữ ký thành bảng 3 vị trí trang trọng:
  - Cột 1: `\textbf{TRƯỞNG BỘ MÔN}`
  - Cột 2: `\textbf{GIẢNG VIÊN HƯỚNG DẪN}` (`\textbf{ThS. Vũ Lan Phương}`)
  - Cột 3: `\textbf{SINH VIÊN THỰC HIỆN}` (`\textbf{Đàm Mạnh Dũng}`)
- Đảm bảo Phiếu giao đề tài giữ đúng định dạng 2 trang (trang iii và iv).

---

### 4. Đề cương ĐATN 10 tuần (`report-datn/frontmatter/de_cuong_datn.tex`)

#### 4.1. Hiện trạng trước khi sửa
- Bảng kế hoạch 10 tuần tại Tuần 6 chỉ ghi nhận công việc kỹ thuật Hybrid RAG, hoàn toàn bỏ sót cột mốc hành chính bắt buộc theo quy chế Khoa CNTT - HUMG: Báo cáo tiến độ giữa kỳ với Bộ môn và GVHD.

#### 4.2. Nội dung đã thực hiện
- Cập nhật dòng mô tả Tuần 6 (28/09/2026 -- 04/10/2026):
  *"Báo cáo tiến độ giữa kỳ với Bộ môn và GVHD. Hiện thực hóa phân hệ Hybrid RAG: Tìm kiếm kết hợp HNSW + BM25, dung hợp RRF, tái xếp hạng Cross-Encoder và trích xuất Bounding Box PDF."*
- Điều chỉnh `\arraystretch` bảng từ `1.10` thành `1.08` và dãn cách chữ ký từ `2.2cm` thành `1.8cm` để toàn bộ trang 3 của đề cương vừa vặn trên đúng 1 trang in (trang vii), không tràn trang.

---

### 5. Danh mục các ký hiệu và chữ viết tắt (`report-datn/frontmatter/danh_muc_viet_tat.tex`)

#### 5.1. Hiện trạng trước khi sửa
- Sử dụng môi trường `longtable` chưa ép buộc chiều rộng toàn phần `\textwidth`.
- Liệt kê các từ phổ thông đại trà không cần thiết trong ĐATN ngành CNTT: `AI`, `ERD`, `PDF`, `UML`.
- Bỏ sót các từ viết tắt chuyên sâu mang tính hạt nhân của hệ thống VeriScholar: `CRAG`, `CSDL`, `AES-GCM`, `REST`, `E2B`, `UI/UX`, `SQL`.

#### 5.2. Nội dung đã thực hiện
- Chuyển đổi toàn bộ sang môi trường `tabularx \textwidth` với cấu trúc cột: `{|>{\centering\arraybackslash}p{1.0cm}|>{\centering\arraybackslash}p{3.2cm}|X|}`.
- Loại bỏ 4 từ phổ thông: `AI`, `ERD`, `PDF`, `UML`.
- Bổ sung 7 thuật ngữ chuyên sâu:
  - `AES-GCM`: *Advanced Encryption Standard -- Galois/Counter Mode -- Chuẩn mã hóa khối nâng cao xác thực két khóa BYOK*
  - `CRAG`: *Corrective Retrieval-Augmented Generation -- Sinh văn bản tăng cường truy xuất có cơ chế hiệu chỉnh*
  - `CSDL`: *Cơ sở dữ liệu -- Hệ thống lưu trữ và quản trị dữ liệu có cấu trúc*
  - `E2B`: *E2B Sandbox / MicroVM -- Môi trường máy ảo đám mây thực thi và biên dịch cô lập an toàn*
  - `REST`: *Representational State Transfer -- Kiến trúc dịch vụ web truyền trạng thái đại diện*
  - `SQL`: *Structured Query Language -- Ngôn ngữ truy vấn cơ sở dữ liệu quan hệ*
  - `UI/UX`: *User Interface / User Experience -- Giao diện và trải nghiệm người dùng*
- Sắp xếp toàn bộ **32 thuật ngữ** theo thứ tự bảng chữ cái nghiêm ngặt (A-Z).
- Chia đều thành 2 trang (16 mục/trang) với lệnh `\newpage`, giữ cho bảng không bị trôi và hiển thị thẩm mỹ tuyệt đối trên trang xv và xvi.

---

### 6. Lời cảm ơn (`report-datn/frontmatter/loi_cam_on.tex`)

#### 6.1. Hiện trạng trước khi sửa
- Xưng hô khẩu ngữ: *"cô Vũ Lan Phương -- Giảng viên Khoa Công nghệ Thông tin"*.
- Kết thúc lửng lơ ở cuối trang, hoàn toàn thiếu khối địa danh, ngày tháng và chữ ký của sinh viên thực hiện.

#### 6.2. Nội dung đã thực hiện
- Chuẩn hóa học vị: *"ThS. Vũ Lan Phương -- Giảng viên Khoa Công nghệ Thông tin"*.
- Sửa macro `\VS` đảm bảo chuẩn khoảng trắng học thuật.
- Bổ sung khối địa danh, ngày tháng và chữ ký trang trọng ở chân trang 1 Ả Rập:
  ```latex
  \vspace{0.6cm}
  \hfill \textit{Hà Nội, ngày 02 tháng 11 năm 2026} \\[0.3cm]
  \begin{flushright}
    \textbf{Sinh viên thực hiện} \\[2.0cm]
    \textbf{Đàm Mạnh Dũng}
  \end{flushright}
  ```

---

### 7. Lời mở đầu (`report-datn/frontmatter/loi_mo_dau.tex`)

#### 7.1. Hiện trạng trước khi sửa
- Lỗi cú pháp dấu ngoặc kép XeLaTeX: `\textit{''Xây dựng...''}`.
- Thiếu định danh rõ ràng hai yếu tố bắt buộc theo quy định HUMG: **Đối tượng nghiên cứu** và **Phạm vi nghiên cứu**.
- Chưa đồng bộ chi tiết trạng thái 100% pass và chỉ số IoU benchmark.

#### 7.2. Nội dung đã thực hiện
- Sửa dấu ngoặc kép: `\textit{``Xây dựng...''}`.
- Bổ sung tường minh hai đoạn văn học thuật:
  - `-- \textbf{Đối tượng nghiên cứu:}` *Các ấn phẩm khoa học quốc tế định dạng PDF cấu trúc 2 cột chuẩn IEEE/ACM, mô hình ngôn ngữ lớn, cơ chế kiểm chứng tọa độ hộp viền Bounding Box và đồ thị tri thức học thuật.*
  - `-- \textbf{Phạm vi nghiên cứu:}` *Xây dựng giải pháp hỗ trợ nghiên cứu cho học giả tại Trường Đại học VinUniversity (VinUni), bao gồm quy trình khép kín: Khám phá tài liệu đa nguồn (arXiv, Semantic Scholar, CrossRef), Đọc sâu kiểm chứng tọa độ Bounding Box, Quản lý đồ thị tri thức GraphRAG trên PostgreSQL và Tác nhân ReAct tự động sửa lỗi biên dịch LaTeX trong sandbox E2B cô lập.*
- Đồng bộ chỉ số kiểm thử: 580 test tự động (340 pytest, 240 vitest, 100% pass trong 13.02s), $\text{Recall@5} = 94{,}44\%$, $\text{IoU} \ge 0{,}85$ (thực tế $0{,}88$), tỷ lệ tự sửa lỗi LaTeX $96{,}0\%$.
- Đảm bảo Lời mở đầu nằm gọn gàng trên trang 2 Ả Rập.

---

### 8. Phần Kết luận và Hướng phát triển (`report-datn/chapters/ket_luan.tex`)

#### 8.1. Hiện trạng trước khi sửa
- Các đoạn văn trong mục "Kết quả đạt được" kéo dài từ 12 đến 16 dòng, nhồi nhét lại chi tiết hàng chục con số kỹ thuật của Chương 4 gây cảm giác nặng nề, thiếu tính tổng kết.
- Mục Hướng phát triển đề xuất dàn trải 4 hướng chưa cô đọng.
- Xuất hiện lỗi tràn lề `Overfull \hbox` do cụm từ tiếng Anh `Hexagonal Architecture`.

#### 8.2. Nội dung đã thực hiện
- Tinh gọn mục "Kết quả đạt được" đúc kết sắc sảo đúng **4 đóng góp kỹ thuật cốt lõi**:
  1. *Kiến trúc Lục giác và Cơ sở dữ liệu ACID:* Phân tách ranh giới nghiệp vụ thuần khiết, 20 bảng PostgreSQL 16 + pgvector, toàn vẹn giao dịch ACID giữa siêu dữ liệu, vector 1536 chiều và đồ thị tri thức.
  2. *Truy xuất thông tin lai và Kiểm chứng tọa độ Bounding Box:* Agentic Hybrid RAG dung hợp HNSW và từ khóa toàn văn qua RRF ($k=60$), cổng CRAG, $\text{Recall@5} = 94{,}44\%$, $\text{IoU} \ge 0{,}85$ (thực tế $0{,}88$), triệt tiêu ảo giác trích dẫn.
  3. *Đồ thị tri thức học thuật GraphRAG và Bách khoa toàn thư tri thức:* Mô hình hóa 4 thực thể (\textit{Paper}, \textit{Method}, \textit{Dataset}, \textit{MetricResult}), phân cụm Louvain, sinh trang tổng hợp tri thức cộng đồng (\textit{Graph Wiki}) đạt điểm hoàn chỉnh $0{,}9442$.
  4. *Soạn thảo học thuật tự phục hồi lỗi và Bảo mật két khóa BYOK:* Tác nhân LangGraph ReAct phối hợp E2B Sandbox tự sửa lỗi LaTeX đạt $96{,}0\%$ ($24/25$ ca), két khóa BYOK mã hóa AES-256-GCM.
- Bổ sung khẳng định đanh thép: Đồ án hoàn thành **100% mục tiêu khoa học và kỹ thuật** trong đề cương, vượt qua 580 test tự động (100% pass trong 13.02s), công bố mã nguồn mở tại GitHub.
- Tinh gọn 4 mục Hạn chế hiện tại (phụ thuộc đám mây, phạm vi khử trùng lặp CAS, quy mô benchmark, giới hạn phiên đọc).
- Đúc kết súc tích **3 hướng phát triển tiếp theo**:
  1. *Mô hình ngôn ngữ cục bộ và Biên dịch TeX Live nội bộ:* vLLM/Ollama kết hợp container TeX Live cô lập bằng \texttt{gVisor} cho môi trường air-gapped.
  2. *Chia sẻ chỉ mục vector công khai qua CAS:* Tối ưu chỉ mục vector dùng chung Canonical Public Paper Index dựa trên mã băm CAS SHA-256.
  3. *GraphRAG đa phương thức và Cộng tác soạn thảo thời gian thực:* Trích xuất biểu đồ/công thức từ PDF và tích hợp CRDT (Yjs) cộng tác thời gian thực.
- Triệt tiêu hoàn toàn cảnh báo `Overfull \hbox`, văn bản căn đều hai bên hoàn hảo.

---

## III. BẢNG TỔNG HỢP TRƯỚC VÀ SAU KHI THỰC HIỆN

| Tệp tin | Trạng thái trước khi sửa | Trạng thái sau khi hoàn thiện | Đánh giá tuân thủ |
| :--- | :--- | :--- | :---: |
| `frontmatter/bia_phu.tex` | Thiếu tên đề tài; khoảng trống 4.0cm; gạch nối thô; font 15pt | Bổ sung TÊN ĐỀ TÀI in hoa đậm; rule 6.5cm; font 16pt; bố cục cân đối | Đạt 100% Phụ lục 02 HUMG |
| `frontmatter/bia_chinh.tex` | TikZ gáy sách xoay $-90^\circ$ đè mép bìa; font 15pt; gạch nối thô | Xóa TikZ gáy sách; rule 6.5cm; font 16pt; giữ logo HUMG chuẩn | Đạt 100% Phụ lục 01 HUMG |
| `frontmatter/phieu_giao_de_tai.tex` | 330 tests; thiếu CrossRef/CAS; gộp cam đoan khẩu ngữ; thiếu ký Trưởng bộ môn | 580 tests (100% pass); có CrossRef/CAS; cam đoan chuẩn mực; 3 chữ ký đầy đủ | Đạt 100% Quy chế Khoa CNTT |
| `frontmatter/de_cuong_datn.tex` | Tuần 6 thiếu mốc báo cáo tiến độ giữa kỳ với Bộ môn và GVHD | Bổ sung rõ mốc báo cáo tiến độ giữa kỳ Tuần 6; giữ nguyên 3 trang | Đạt 100% Mau-De-cuong-DATN |
| `frontmatter/danh_muc_viet_tat.tex` | Dùng `longtable`; thừa AI, ERD, PDF, UML; thiếu 7 từ lõi | Dùng `tabularx \textwidth`; 32 từ xếp A-Z; bổ sung CRAG, CSDL, AES, E2B... | Đạt 100% AGENTS.md |
| `frontmatter/loi_cam_on.tex` | "cô Vũ Lan Phương"; thiếu ngày tháng và chữ ký sinh viên | "ThS. Vũ Lan Phương"; có Hà Nội 02/11/2026 và chữ ký Đàm Mạnh Dũng | Đạt chuẩn học thuật |
| `frontmatter/loi_mo_dau.tex` | Lỗi ngoặc kép; thiếu Đối tượng và Phạm vi nghiên cứu | Sửa ngoặc kép; bổ sung tường minh Đối tượng & Phạm vi; đồng bộ 580 tests | Đạt 100% Huong-dan-viet-DATN |
| `chapters/ket_luan.tex` | Kể lể số liệu dài dòng; 4 hướng mở rộng; overfull hbox 12.3pt | Đúc kết 4 đóng góp cốt lõi; 3 hướng mở rộng; 0 overfull hbox | Chuẩn văn phong quốc tế |

---

## IV. KẾT LUẬN VÀ KIẾN NGHỊ

1. Toàn bộ 8 nhiệm vụ cụ thể phân công cho Subagent Worker Frontmatter & Kết luận đã được hoàn thành trọn vẹn, chính xác và trung thực 100%.
2. Không có bất kỳ tệp tin nào ngoài danh sách 8 tệp phân công bị can thiệp.
3. Bản báo cáo sau khi hoàn thiện biên dịch XeLaTeX mượt mà với mã thoát `0`, không có lỗi fatal, không có cảnh báo tràn lề trong phạm vi, số trang được tối ưu hóa cân đối và sẵn sàng bàn giao cho Mentor Master Integrator tiến hành nghiệm thu toàn văn.
