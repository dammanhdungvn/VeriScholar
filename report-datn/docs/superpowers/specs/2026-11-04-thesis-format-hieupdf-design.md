# Tài liệu Thiết kế: Chuẩn hóa 100% Định dạng Đồ án Tốt nghiệp theo guide/HIeu.pdf

- **Dự án:** Báo cáo Đồ án Tốt nghiệp VeriScholar (`report-datn`)
- **Tác giả:** Antigravity Engineering
- **Ngày:** 04/11/2026
- **Trạng thái:** Chờ phê duyệt (Pending Approval)

---

## 1. Bối cảnh và Mục đích (Intent & Why)

Báo cáo ĐATN của sinh viên Đàm Mạnh Dũng (Khoa CNTT - Đại học Mỏ - Địa chất) cần được chuẩn hóa thể thức tuyệt đối theo đúng khuôn mẫu thực tế của tài liệu mẫu `guide/HIeu.pdf` và quy định tại `guide/Huong-dan-viet-DATN.md`. 

Mục đích thiết kế là khắc phục triệt để 11 sai lệch và phản hồi từ Giảng viên hướng dẫn (GVHD), chấm dứt mọi hành vi tự ý sáng tạo hay "tiết kiệm giấy" làm sai quy cách (như tự giảm dãn dòng, ép cỡ chữ bảng biểu, tự ý in đậm/in nghiêng trong đoạn văn), đưa báo cáo về chuẩn in ấn photo A4 hoàn hảo.

---

## 2. Mục tiêu, Phi mục tiêu và Điều cấm (Goals, Non-Goals, Anti-Goals)

### 2.1 Mục tiêu (Goals)
1. **Hình ảnh (R1):** 100% hình ảnh trong báo cáo phải là định dạng `.png` lưu trong repo (`report-datn/figures/`), độ rộng vừa vặn khổ A4 (`width=0.90\textwidth` đến `0.95\textwidth`), hiển thị rõ nét, không bị co nhỏ quá mức.
2. **Trang iv (R2):** Xóa bỏ hoàn toàn chức danh "Trưởng Bộ môn" trong Phiếu giao đề tài tốt nghiệp; chỉ giữ 2 chữ ký: Giảng viên hướng dẫn và Sinh viên thực hiện.
3. **Thời gian và Chức danh (R3):** Cố định ngày nộp chính thức `06/11/2026` ("Hà Nội, ngày 06 tháng 11 năm 2026") trên toàn bộ biểu mẫu hành chính; các chức danh ký tên viết thường Title Case ("Giảng viên hướng dẫn", "Sinh viên thực hiện").
4. **Dãn dòng (R4):** Đạt chuẩn giãn dòng 1.5 lines giống Microsoft Word trong toàn bài (`\setstretch{1.45}` đồng nhất), không bị co hẹp.
5. **Cỡ chữ nội dung và bảng biểu (R5):** Cỡ chữ toàn văn và mọi bảng biểu phải đạt 13pt Times New Roman đồng nhất (trừ các Header cấp 1, 2, 3 và bìa theo quy chuẩn). Loại bỏ toàn bộ `\small`, `\footnotesize`, `\fontsize{9pt}` trong các bảng.
6. **Mục lục (R6):** Tuyệt đối không in đậm nội dung trong Mục lục (dùng `\normalfont` cho tất cả các dòng mục, bao gồm Chương và Mục).
7. **Sườn bìa ngoài (R7):** Trang bìa ngoài (Bìa 1) có dải sườn/gáy dọc mép lề trái theo đúng trang bìa đầu tiên của `guide/HIeu.pdf`, gồm 3 khối chữ xoay 90°: `ĐÀM MẠNH DŨNG`, `HỆ THỐNG THÔNG TIN`, `KHOÁ 67` với font đứng bình thường (`\normalfont`, không in đậm).
8. **Đánh số trang (R8):** Số trang Ả Rập (Trang 1) bắt đầu chính xác từ phần MỤC LỤC. Các trang hồ sơ trước Mục lục (Bìa, Phiếu giao đề tài, Đề cương, Lời cảm ơn) không in số trang ở chân trang (để trống footer theo `adminform`), nhưng Mục lục hiển thị số La Mã `iii`, `v`, `viii` cho các trang hồ sơ và hiển thị chính dòng `MỤC LỤC ............... 1`.
9. **In đậm / In nghiêng & Tham chiếu (R9):**
   - Bỏ toàn bộ chữ in đậm (`\textbf`) và in nghiêng (`\textit`) tùy tiện trong các đoạn văn xuôi và danh sách liệt kê.
   - CHỈ DUY NHẤT tiêu đề tiểu mục cấp 3 (như `2.1.1` hoặc `4.2.1`) mới được in nghiêng (`\bfseries\itshape` theo mẫu Hieu.pdf).
   - Tinh giản triệt để các tham chiếu trích dẫn `\cite`: gỡ bỏ các trích dẫn rải rác không cần thiết ở Chương 1, Chương 3 và Chương 4; chỉ giữ lại các trích dẫn lý thuyết cốt lõi ở Chương 2.
10. **Khớp 100% HIeu.pdf (R10):** Tái tạo trọn vẹn thể thức và tinh thần của file `guide/HIeu.pdf`.
11. **Cấm tiết kiệm giấy (R11):** Tuyệt đối cấm giảm `\setstretch` hay ép font để giảm số trang. Báo cáo để trang phân bố tự nhiên theo đúng cỡ chữ 13pt và dãn dòng 1.5.
12. **Cập nhật AGENTS.md:** Bổ sung đầy đủ các bài học và bộ quy tắc kiểm định bắt buộc vào `report-datn/AGENTS.md`.

### 2.2 Phi mục tiêu (Non-Goals)
- Thay đổi nội dung học thuật, kết quả thực nghiệm hay mô hình kỹ thuật của hệ thống VeriScholar.
- Thêm thắt các gói LaTeX đồ họa màu mè không có trong `HIeu.pdf`.

### 2.3 Điều cấm (Anti-Goals)
- Không dùng `\setstretch{1.241}` hoặc bất kỳ lệnh co giãn dòng nhân tạo nào trong các tệp frontmatter hay chapters.
- Không in đậm các từ khóa kỹ thuật ngẫu nhiên trong thân bài (ví dụ `\textbf{FastAPI}`, `\textbf{ACID}`).
- Không để xảy ra lệch số trang giữa Mục lục và trang in thực tế.

---

## 3. Ràng buộc Kỹ thuật (Constraints)

- **Trình biên dịch:** XeLaTeX (hỗ trợ native font Times New Roman Unicode qua `fontspec`).
- **Phông chữ:** `Times New Roman` (đủ 4 biến thể: regular `times.ttf`, bold `timesbd.ttf`, italic `timesi.ttf`, bold-italic `timesbi.ttf`).
- **Căn lề chuẩn Khoa CNTT HUMG:**
  - Lề trên (top): 2.5 cm
  - Lề dưới (bottom): 2.5 cm
  - Lề trái (left): 3.5 cm
  - Lề phải (right): 2.5 cm
- **Chiều rộng văn bản khả dụng:** $21.0\,\text{cm} - (3.5\,\text{cm} + 2.5\,\text{cm}) = 15.0\,\text{cm}$.
- **Biên dịch TikZ:** Bìa 1 dùng TikZ overlay cho sườn bìa, bắt buộc chạy 2 lượt biên dịch để ghi nhận tọa độ chính xác.

---

## 4. Các Phương án đã Xem xét (Approaches Considered)

1. **Phương án 1 (Được chọn): Hiệu chỉnh toàn diện trực tiếp trên bộ mã nguồn LaTeX hiện tại**
   - Tinh chỉnh `preamble.tex`, `main.tex`, các file `frontmatter/*.tex` và `chapters/*.tex`.
   - Giữ nguyên kiến trúc module hóa sạch sẽ, kiểm soát kích thước font, dãn dòng và bảng biểu ở mức pixel và point.
   - Lý do chọn: Đáp ứng 100% yêu cầu khắt khe của người dùng, không làm mất mã nguồn, xuất bản PDF chất lượng cao nhất.

2. **Phương án 2 (Bị loại): Chuyển đổi toàn bộ sang Microsoft Word (.docx)**
   - Nhập lại nội dung vào file Word mẫu của `HIeu.pdf`.
   - Lý do loại: Khó đồng bộ mã nguồn Git, dễ lỗi công thức toán và sơ đồ kỹ thuật, mất công sức bảo trì.

---

## 5. Thiết kế Chi tiết Từng Thành phần

### 5.1 Cấu hình Hệ thống (`config/preamble.tex` & `main.tex`)
- **Dãn dòng:**
  ```latex
  \usepackage{setspace}
  \setstretch{1.45}
  \renewcommand{\onehalfspacing}{\setstretch{1.45}}
  ```
- **Cỡ chữ toàn văn:** `\usepackage[fontsize=13pt]{scrextend}`.
- **Định dạng Tiêu đề (Headings):**
  - Chương (`\chapter`): 14pt Đậm, IN HOA, căn giữa (hoặc theo mẫu Word: 14pt Đậm).
  - Mục (`\section`): 13pt Đậm, căn trái.
  - Tiểu mục (`\subsection`): 13pt Đậm nghiêng (`\bfseries\itshape`), căn trái theo mẫu `2.1.1` của `HIeu.pdf`.
  - Tiểu mục cấp 3 (`\subsubsection`): 13pt In nghiêng thường (`\itshape`), căn trái.
- **Mục lục (`tocloft`):**
  - Toàn bộ font tiêu đề và số trang trong Mục lục đổi thành `\normalfont` (không in đậm `\bfseries`).
  - Dấu chấm dẫn trang thanh thoát (`\cftdotfill{\cftdotsep}`).
  - Bổ sung `\addcontentsline{toc}{chapter}{MỤC LỤC}` ngay tại trang bắt đầu Mục lục (trang Ả Rập 1).

### 5.2 Trang Bìa và Hồ sơ ĐATN (`frontmatter/`)
1. **`frontmatter/bia_chinh.tex`:**
   - Sườn bìa mép trái: Đặt tại `xshift=1.4cm` từ mép trái trang, xoay `-90` độ, font `\fontsize{13pt}{16pt}\selectfont\normalfont` (chữ đứng thường, IN HOA):
     - `ĐÀM MẠNH DŨNG` (phía trên)
     - `HỆ THỐNG THÔNG TIN` (ở giữa)
     - `KHOÁ 67` (phía dưới)
   - Nội dung chính: Tên trường, gạch ngang, logo MDC, Họ tên tác giả, ĐỒ ÁN TỐT NGHIỆP, Ngành CNTT, Tên đề tài, KHOÁ 67, Hà Nội - Năm 2026.
2. **`frontmatter/bia_phu.tex`:**
   - Khớp 100% trang 2 của `HIeu.pdf` và Phụ lục 2 HUMG: Tiêu ngữ, Tên trường, gạch ngang, ĐỒ ÁN TỐT NGHIỆP, CHUYÊN NGÀNH: HỆ THỐNG THÔNG TIN.
   - Hoàn toàn KHÔNG in khối Tên đề tài (khớp 100% bản mẫu `HIeu.pdf`).
   - Chữ ký: `Giảng viên hướng dẫn` và `Sinh viên thực hiện` (Title Case), `(Chữ ký)`, họ tên `Vũ Lan Phương` và `Đàm Mạnh Dũng`, `Hà Nội – Năm 2026`.
3. **`frontmatter/phieu_giao_de_tai.tex`:**
   - Xóa bỏ hoàn toàn chức danh "Trưởng Bộ môn".
   - Bảng ký tên chỉ có 2 bên: "Giảng viên hướng dẫn" và "Sinh viên thực hiện" (Title Case).
   - Ngày tháng: `Hà Nội, ngày 06 tháng 11 năm 2026`.
   - Bỏ toàn bộ `\setstretch{1.241}`, để dãn dòng 1.5 tự nhiên.
4. **`frontmatter/de_cuong_datn.tex`:**
   - Bỏ `\fontsize{9.5pt}{11.5pt}` và `\setstretch{1.241}`. Toàn bộ chữ trong bảng thông tin và kế hoạch 10 tuần đạt chuẩn 13pt.
   - Bảng ký cuối: "Giảng viên hướng dẫn" và "Sinh viên thực hiện", ngày `06/11/2026`.
5. **`frontmatter/loi_cam_on.tex`:**
   - Bỏ các đoạn in nghiêng trong văn xuôi, đưa về font thường đứng.
   - Ngày tháng: `06/11/2026`.

### 5.3 Phần Thân bài (`chapters/`)
1. **Chuẩn hóa Typography đoạn văn:**
   - Quét qua toàn bộ các tệp `.tex` trong `chapters/ch1/`, `ch2/`, `ch3/`, `ch4/`, `ket_luan.tex`:
   - Gỡ bỏ toàn bộ `\textbf{...}` bôi đậm từ ngữ trong các câu văn xuôi và danh sách liệt kê.
   - Gỡ bỏ toàn bộ `\textit{...}` trong thân bài (chỉ giữ lại ký hiệu toán học $k=60$ nếu có).
2. **Tinh giản Tham chiếu Trích dẫn (`\cite`):**
   - Bóc bỏ toàn bộ các thẻ trích dẫn `\cite{...}` rải rác ở Chương 1, Chương 3 và Chương 4.
   - Giữ lại các trích dẫn mang tính cơ sở lý thuyết chuẩn mực ở Chương 2 (`chapters/ch2/`).
3. **Chuẩn hóa Bảng biểu (Tables):**
   - Loại bỏ toàn bộ `\singlespacing` và các lệnh co font (`\small`, `\footnotesize`) đặt trước các bảng.
   - Cỡ chữ trong tất cả các ô bảng biểu đạt 13pt Times New Roman đồng nhất.
   - Tiêu đề bảng biểu đặt ở TRÊN bảng, in nghiêng: `\textit{Bảng X-Y Tên bảng}`.
4. **Chuẩn hóa Hình ảnh (Figures):**
   - Xác nhận 100% hình ảnh là file `.png` tại `figures/`.
   - Thiết lập `width=0.92\textwidth` đến `0.95\textwidth` để ảnh to rõ ràng khi photo ra khổ giấy A4, không co nhỏ.
   - Tiêu đề hình ảnh đặt ở DƯỚI hình, in nghiêng: `\textit{Hình X- Y Tên hình}`.

### 5.4 Đồng bộ Quy chế vào `report-datn/AGENTS.md`
- Cập nhật mục "Danh mục các sai lầm phổ biến và biện pháp khắc phục triệt để".
- Bổ sung 11 nguyên tắc bất di bất dịch vừa được chuẩn hóa vào Pre-Commit Checklist để toàn bộ các agent sau này tuân thủ 100%.

---

## 6. Các Quyết định Kỹ thuật của Builder (Builder Calls)

1. **Phạm vi chuẩn hóa ảnh PNG (R1):**
   - Áp dụng triệt để cho 100% hình ảnh chèn ngoài qua `\includegraphics` (ảnh giao diện, dashboard tại `figures/frontend/`). Chuyển đổi toàn bộ sang `.png` lưu trong repo, kích thước `0.92\textwidth - 0.95\textwidth`.
   - Các sơ đồ kỹ thuật vẽ bằng mã nguồn vector TikZ bản địa (kiến trúc lục giác, use case stick figure, biểu đồ tuần tự) được giữ nguyên mã TikZ để bảo đảm độ nét vô hạn (không bị vỡ hạt hay pixelated) khi in ấn/photo ra A4, đúng tinh thần "hình ảnh nhìn rõ ràng và chi tiết không được phép quá bé".
2. **Quản lý trang và dãn dòng Frontmatter (R4, R5, R8, R11):**
   - Loại bỏ hoàn toàn các lệnh ép dòng nhân tạo (`\setstretch{1.241}`) và font chữ nhỏ (`\fontsize{9pt}`, `\fontsize{9.5pt}`) trong Phiếu giao đề tài và Đề cương. Áp dụng chuẩn dãn dòng 1.5 (`\setstretch{1.45}`) và font 13pt thống nhất.
   - Các trang trước Mục lục sử dụng `\pagestyle{adminform}` (để trống footer, không in số trang vật lý, khớp 100% các trang 1--8 của `HIeu.pdf`).
   - Mục lục tự động phản ánh chính xác số trang thực tế của hồ sơ bằng số La Mã thường, và đánh số Ả Rập 1 bắt đầu chính xác từ trang MỤC LỤC.
3. **Tinh giản tham chiếu và bảo toàn danh mục TLTK (R9):**
   - Bóc bỏ toàn bộ các thẻ trích dẫn `\cite` rải rác ở Chương 1, Chương 3 và Chương 4 để văn phong trong sáng, thuần túy kỹ thuật thực nghiệm.
   - Giữ lại các trích dẫn lý thuyết nền tảng tại Chương 2. Tích hợp trích dẫn tài liệu quy chế HUMG (`humg2022hd`) và kiến trúc lục giác (`cockburn2005`) vào các mục lý thuyết tương ứng ở Chương 2, bảo đảm 100% mục trong `tai_lieu_tham_khao.tex` đều được dẫn chiếu, không có tài liệu mồ côi.
4. **Hệ thống phân cấp tiêu đề (Headings Hierarchy):**
   - Chương (`\chapter`): 14pt Đậm IN HOA, căn giữa.
   - Mục cấp 1 (`\section`): 13pt Đậm đứng (`\bfseries`), căn trái.
   - Tiểu mục cấp 2 (`\subsection`, ví dụ `2.1.1`): 13pt Đậm nghiêng (`\bfseries\itshape`), căn trái theo đúng mẫu `HIeu.pdf`.
   - Tiểu mục cấp 3 (`\subsubsection`, ví dụ `2.1.1.1` nếu có): 13pt In nghiêng (`\itshape`), căn trái.
   - Tuyệt đối cấm in đậm hoặc in nghiêng tùy tiện trong các đoạn văn xuôi thân bài.

## 7. Những phần dành cho Người thực thi (Left to the Builder)

- Tinh chỉnh bề rộng các cột trong bảng CSDL ở Chương 3 để khi hiển thị font 13pt không bị tràn lề.
- Chạy biên dịch 2 lượt XeLaTeX để đồng bộ toàn bộ tọa độ TikZ sườn bìa và chỉ số trang Mục lục.

