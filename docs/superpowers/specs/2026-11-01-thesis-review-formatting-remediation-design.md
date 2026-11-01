# Thiết kế Chuẩn hóa Định dạng Báo cáo Đồ án Tốt nghiệp theo Review của GVHD

## 1. Mục đích và Bối cảnh (Intent & Why)
Sau khi nộp bản thảo đồ án tốt nghiệp VeriScholar, Giảng viên Hướng dẫn (ThS. Vũ Lan Phương) đã phản hồi 8 điểm cần điều chỉnh về quy cách định dạng và hình thức văn bản:
1. Dãn dòng và ngắt dòng không đúng quy định (Ảnh số 1).
2. Không tự ý cách dòng và chèn khoảng cách thủ công (Ảnh số 1).
3. Đổi danh sách nhiệm vụ của sinh viên tại Phiếu giao đề tài từ đánh số (`1, 2...`) sang gạch đầu dòng (bullet).
4. Số trang không in nghiêng (kể cả số La Mã `iii, iv` hay Ả Rập), đặt ở góc dưới bên phải trang.
5. Chuẩn hóa tên đơn vị: "Bộ môn Hệ thống thông tin và Tri thức" (hoặc "BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC" ở nơi cần in hoa toàn bộ).
6. Bỏ toàn bộ header ("Đồ án tốt nghiệp ngành Công nghệ thông tin") và footer bên trái ("SVTH: Đàm Mạnh Dũng..."), xóa các đường kẻ đôi; chỉ giữ số trang.
7. Mục lục: Tối đa 3 mức (bỏ mức 4 như `4.2.1.1`), bỏ dấu chấm sau số thứ tự đề mục (`2.1 Tổng quan` thay vì `2.1. Tổng quan`), bỏ dấu hai chấm sau số chương (`CHƯƠNG 1 ` thay vì `CHƯƠNG 1:`); Danh mục hình/bảng không in đậm chữ "Hình", "Bảng" và số thứ tự, bỏ dấu hai chấm.
8. Rà soát và loại bỏ việc in đậm tùy tiện trong phần thân văn bản (Lời cảm ơn, Lời mở đầu và các chương nội dung, ví dụ như Ảnh số 3 và Ảnh số 4).

Tài liệu thiết kế này định rõ phương án kỹ thuật để khắc phục triệt để và đồng bộ toàn bộ 8 điểm trên trên hệ thống tài liệu LaTeX (`report-datn`).

---

## 2. Mục tiêu, Phi mục tiêu và Rủi ro cần tránh (Goals, Non-goals, Anti-goals)

### Goals
- **Chuẩn hóa dãn dòng & khoảng cách:** Áp dụng thống nhất `\onehalfspacing` (1.5 lines chuẩn Word cỡ 13pt) toàn bộ tài liệu. Bỏ hoàn toàn các lệnh ép dãn dòng cục bộ (`\setstretch{1.10}`, `\setstretch{1.05}`) và các lệnh nhảy khoảng cách thủ công (`\vspace{...}`) gây gián đoạn dòng văn bản.
- **Biểu mẫu hành chính vừa vặn:** Chuyển các nhiệm vụ trong `phieu_giao_de_tai.tex` sang `\begin{itemize}` (bullet); tinh chỉnh câu chữ gọn gàng để Phiếu giao đề tài (3 trang: iii, iv, v) và Đề cương (3 trang: vi, vii, viii) vừa khít, cân đối tự nhiên mà không cần ép dãn dòng hay co chữ.
- **Số trang không in nghiêng:** Chân trang chỉ giữ lại số trang định dạng đứng (`\thepage` thay vì `\textit{\thepage}`), căn lề phải ở mọi trang (cả trang La Mã thường và trang nội dung Ả Rập).
- **Chuẩn hóa danh xưng Bộ môn:** Thống nhất tên gọi "Bộ môn Hệ thống thông tin và Tri thức" trên toàn bộ báo cáo; các vị trí bìa/tiêu ngữ in hoa chuẩn "BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC".
- **Gỡ bỏ Header/Footer trang trí:** Xóa tiêu đề đầu trang `\fancyhead[L]`, xóa thông tin sinh viên chân trang trái `\fancyfoot[L]`, xóa bỏ hoàn toàn đường kẻ đôi `\headrule` và `\footrule`. Chân trang duy nhất còn lại là số trang ở `\fancyfoot[R]`.
- **Chuẩn hóa Mục lục & Danh mục Hình/Bảng:**
  - Thiết lập `\setcounter{tocdepth}{2}` để Mục lục chỉ chứa Chương, Mục (1.1) và Tiểu mục (1.1.1); không hiển thị mức 4 (1.1.1.1).
  - Cấu hình `\cftsecaftersnum{ }`, `\cftsubsecaftersnum{ }`, `\cftchapaftersnum{\ }` trong `preamble.tex` để xóa triệt để dấu chấm và dấu hai chấm trong Mục lục.
  - Cấu hình `\cftfigpresnum{Hình~}`, `\cftfigaftersnum{\ }`, `\cfttabpresnum{Bảng~}`, `\cfttabaftersnum{\ }` với font chữ thường (không `\bfseries`, không dấu `:`).
- **Làm sạch chữ in đậm tùy tiện:** Rà soát và loại bỏ việc in đậm cụm từ nội dòng trong câu (như `\textbf{Vũ Lan Phương}`, `\textbf{VeriScholar}`, `\textbf{hiện tượng ảo giác trích dẫn}`) trong `loi_cam_on.tex`, `loi_mo_dau.tex` và xuyên suốt 4 chương chính. Chỉ giữ `\textbf` cho các tiêu đề mục, tiêu đề bảng/hình hoặc các thẻ phân loại đầu dòng (`\item \textbf{Tiêu chí:}`).
- **Biên dịch hoàn hảo:** Biên dịch XeLaTeX thành công ra `main.pdf` không phát sinh lỗi cú pháp hay cảnh báo đè trang.

### Non-goals
- Không can thiệp thay đổi các nội dung học thuật cốt lõi (thuật toán, mô hình kiến trúc, số liệu thực nghiệm benchmark 349 test cases).
- Không thay đổi cấu trúc trang bìa chính và bìa phụ ngoài việc đảm bảo đúng chính tả tên Bộ môn.

### Anti-goals
- Không dùng lại các thủ thuật ép co dãn dòng (`\setstretch` nhỏ hơn 1.3) để đối phó với việc tràn trang biểu mẫu.
- Không làm gián đoạn chuỗi đánh số trang (La Mã thường cho frontmatter, Ả Rập bắt đầu từ trang 1 Lời cảm ơn).
- Không xóa nhầm các `\textbf` cần thiết cho ngữ cảnh bảng biểu hoặc danh sách có cấu trúc.

---

## 3. Ràng buộc kỹ thuật (Constraints)
- Môi trường biên dịch: XeLaTeX (`latexmk -xelatex`), phông chữ Times New Roman Unicode qua `fontspec`.
- Khổ giấy A4, căn lề chuẩn HUMG: Trên 2.5cm, Dưới 2.5cm, Trái 3.5cm, Phải 2.5cm.
- Cỡ chữ nội dung 13pt, dãn dòng 1.5 lines (`\onehalfspacing` trong `setspace`).

---

## 4. Các phương án đã cân nhắc (Approaches)

### Phương án 1: Chuẩn hóa toàn diện và cô đọng nội dung biểu mẫu (ĐÃ CHỌN)
- **Mô tả:** Đồng bộ dãn dòng 1.5 lines cho toàn bộ báo cáo; biên tập cô đọng nhẹ nhàng câu chữ ở Phiếu giao đề tài và Đề cương để vừa vặn đúng khuôn 3 trang hành chính truyền thống; cập nhật triệt để cấu hình header, footer, mục lục, LoF/LoT; rà soát làm sạch in đậm tùy tiện trên toàn bộ tài liệu.
- **Đánh giá:** Đáp ứng 100% yêu cầu của cô hướng dẫn và quy chế HUMG, vừa chuẩn mực học thuật vừa đảm bảo tính thẩm mỹ cao nhất khi in nộp.

### Phương án 2: Chuẩn hóa dãn dòng thuần túy và để biểu mẫu tự do nhảy trang (LOẠI BỎ)
- **Mô tả:** Áp dụng 1.5 lines nhưng giữ nguyên văn bản dài của Phiếu giao đề tài và Đề cương, chấp nhận mỗi biểu mẫu nhảy sang trang thứ 4 với vài dòng chữ ký cọc cạch.
- **Lý do loại:** Gây mất cân đối nghiêm trọng cho phần hồ sơ đầu khóa, vi phạm quy cách biểu mẫu thông lệ của Bộ môn.

### Phương án 3: Sửa cục bộ cấu hình và chỉ chỉnh vài trang cô chụp ảnh (LOẠI BỎ)
- **Mô tả:** Chỉ sửa `preamble.tex` và 4 trang trong ảnh chụp của cô, bỏ qua các chương sau.
- **Lý do loại:** Thiếu nhất quán, các chương sau vẫn còn lỗi in đậm tùy tiện và dãn dòng không đồng bộ, dễ bị Hội đồng tiếp tục trừ điểm khi bảo vệ.

---

## 5. Quyết định kỹ thuật chi tiết (Decisions)

### 5.1. Cấu hình Preamble (`report-datn/config/preamble.tex`)
- **Dãn dòng:** Duy trì `\usepackage{setspace}` và `\onehalfspacing`.
- **Header & Footer:**
  ```latex
  \newcommand{\setupdatnheaders}{%
      \fancyhf{}%
      \fancyfoot[R]{\fontsize{10}{12}\selectfont\thepage}%
      \renewcommand{\headrulewidth}{0pt}%
      \renewcommand{\footrulewidth}{0pt}%
      \renewcommand{\headrule}{}%
      \renewcommand{\footrule}{}%
  }
  ```
  Áp dụng tương tự cho `adminform` và `plain` pagestyles: số trang `\thepage` dạng đứng (bỏ `\textit`), không kẻ đường.
- **Mục lục (ToC):**
  - `\setcounter{tocdepth}{2}` (chỉ hiện đến cấp Subsection `x.y.z`, bỏ Subsubsection `x.y.z.w`).
  - `\renewcommand{\cftchapaftersnum}{\ }` (bỏ dấu hai chấm sau số chương).
  - `\settowidth{\cftchaplen}{\bfseries CHƯƠNG 1\ }`.
  - `\renewcommand{\cftsecaftersnum}{}` (bỏ dấu chấm sau số mục `1.1`).
  - `\renewcommand{\cftsubsecaftersnum}{}` (bỏ dấu chấm sau tiểu mục `1.1.1`).
- **Danh mục Bảng & Hình (LoT & LoF):**
  - `\renewcommand{\cfttabpresnum}{Bảng~}` (bỏ `\bfseries`).
  - `\renewcommand{\cfttabaftersnum}{\ }` (bỏ dấu `:`).
  - `\settowidth{\cfttablen}{Bảng~9-99\ }`.
  - `\renewcommand{\cftfigpresnum}{Hình~}` (bỏ `\bfseries`).
  - `\renewcommand{\cftfigaftersnum}{\ }` (bỏ dấu `:`).
  - `\settowidth{\cftfiglen}{Hình~9-99\ }`.

### 5.2. Hồ sơ hành chính đầu khóa (`frontmatter/`)
- **`phieu_giao_de_tai.tex`:**
  - Bỏ `\setstretch{1.10}` và các `\vspace` thủ công.
  - Mục 3 "Các nhiệm vụ cụ thể của ĐATN": Đổi từ `\begin{enumerate}` sang `\begin{itemize}` (bullet `--` hoặc `\item`), biên tập súc tích 8 nhiệm vụ.
  - Tinh chỉnh khoảng cách giữa các mục để vừa khít đẹp mắt trên đúng 3 trang (iii, iv, v).
  - Đảm bảo tên "Bộ môn Hệ thống thông tin và Tri thức" xuất sắc, chính xác.
- **`de_cuong_datn.tex`:**
  - Bỏ `\setstretch{1.06}`, `\setstretch{1.05}`, `\setstretch{1.12}` và font co nhỏ không cần thiết.
  - Chuẩn hóa tên "BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC" ở góc trái tiêu ngữ.
  - Tinh chỉnh nội dung mục tiêu, nhiệm vụ và bảng kế hoạch 10 tuần để bố cục 3 trang (vi, vii, viii) cân đối, tự nhiên.
- **`bia_chinh.tex` & `bia_phu.tex`:**
  - Rà soát khớp tên Bộ môn/Chuyên ngành: "HỆ THỐNG THÔNG TIN VÀ TRI THỨC".

### 5.3. Rà soát làm sạch chữ in đậm tùy tiện trong phần thân
- `frontmatter/loi_cam_on.tex`:
  - `\textbf{Vũ Lan Phương}` $\rightarrow$ `Vũ Lan Phương`.
  - `\textbf{VeriScholar}` $\rightarrow$ `VeriScholar`.
  - Cập nhật đúng tên "Bộ môn Hệ thống thông tin và Tri thức".
- `frontmatter/loi_mo_dau.tex`:
  - `\textbf{hiện tượng ảo giác trích dẫn (Citation Hallucination)}` $\rightarrow$ `hiện tượng ảo giác trích dẫn (\textit{Citation Hallucination})`.
- Các chương `chapters/ch1/`, `chapters/ch2/`, `chapters/ch3/`, `chapters/ch4/`, `chapters/ket_luan.tex`:
  - Quét các đoạn văn thông thường có gắn `\textbf` nội dòng cho từ khóa/thuật ngữ và chuyển về dạng chữ thường hoặc in nghiêng thuật ngữ tiếng Anh theo đúng văn phong học thuật.

---

## 6. Nhiệm vụ cho khâu thực thi (Left to Builder)
1. Cập nhật `report-datn/config/preamble.tex` theo các quyết định cấu hình nêu trên.
2. Cập nhật `report-datn/frontmatter/phieu_giao_de_tai.tex` và `report-datn/frontmatter/de_cuong_datn.tex`.
3. Cập nhật `frontmatter/loi_cam_on.tex`, `frontmatter/loi_mo_dau.tex`.
4. Rà soát và làm sạch `\textbf` tùy tiện trong 4 chương chính và kết luận.
5. Biên dịch lại toàn bộ `main.tex` bằng XeLaTeX, kiểm tra file PDF đầu ra (`main.pdf`), xác nhận:
   - Header/Footer hoàn toàn sạch sẽ, chỉ có số trang đứng ở góc phải.
   - Mục lục tối đa 3 cấp, không dấu chấm/hai chấm sau số.
   - Danh mục hình và bảng không in đậm chữ/số, không dấu hai chấm.
   - Phiếu giao đề tài và Đề cương dãn dòng tự nhiên, chuẩn 1.5 lines, bố cục trang nghiêm chỉnh.
   - Không còn chữ in đậm tùy tiện trong thân bài.
