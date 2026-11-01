# Thiết kế Chuẩn hóa Khung viền Bảng biểu và Khắc phục Khoảng trắng thừa trong Đồ án Tốt nghiệp

## 1. Mục đích và Bối cảnh (Intent & Why)
Sau đợt hiệu chỉnh các yêu cầu hành chính và quy cách đầu mục, Giảng viên Hướng dẫn (ThS. Vũ Lan Phương) đã tiếp tục rà soát và yêu cầu chỉnh sửa 2 điểm quan trọng về mỹ thuật và bố cục trang in của báo cáo:
1. **Khung viền bảng biểu:** Toàn bộ bảng biểu trong đồ án yêu cầu phải có khung viền đầy đủ 4 góc khép kín và có đường kẻ ngang/dọc giữa các ô (theo chuẩn bảng biểu đại học/Word), không được dùng bảng hở cạnh hay chỉ có đường viền trên và dưới như Bảng 1-1 (Ảnh số 1).
2. **Khoảng trắng thừa lớn giữa chữ và hình:** Khắc phục triệt để tình trạng các hình ảnh và các dòng chữ bị cách nhau những khoảng trắng quá lớn (điển hình như trang 98 quanh Hình 4-6 và Mục 4.2.1.6 trong Ảnh số 2). Yêu cầu đẩy các nội dung gần lại với nhau, dòng chảy văn bản điền đầy tự nhiên nhưng vẫn tuân thủ nghiêm ngặt quy định định dạng: cỡ chữ Times New Roman 13pt, dãn dòng 1,5 lines, và lề trang HUMG (trên 2.5cm, dưới 2.5cm, trái 3.5cm, phải 2.5cm).

---

## 2. Mục tiêu, Phi mục tiêu và Rủi ro cần tránh (Goals, Non-goals, Anti-goals)

### Goals
- **100% Bảng có khung viền lưới khép kín:**
  - Chuyển đổi Bảng 1-1 trong `chapters/ch1/1_2_tinh_cap_thiet.tex` từ dạng `booktabs` (`\toprule`, `\midrule`, `\bottomrule`, không có vạch đứng) sang bảng có viền ngoài 4 cạnh khép kín (`|...|`) và đường kẻ ngang `\hline` phân cách từng dòng.
  - Rà soát toàn bộ các bảng trong Chương 2, 3, 4 để bảo đảm sự đồng nhất về định dạng bảng lưới chuẩn (đầy đủ viền ngoài và vạch phân cách ô).
- **Loại bỏ triệt để các khoảng trắng thừa bất thường:**
  - Xóa bỏ toàn bộ 28 lệnh `\clearpage` ngắt trang cưỡng bức nằm rải rác giữa các tiểu mục nội bộ trong các chương (đặc biệt là 11 lệnh trong `chapters/ch4/4_2_giao_dien.tex`, 7 lệnh trong `chapters/ch2/2_5_agentic_react.tex`, và các lệnh trong `ch3`).
  - Chuyển đổi định vị hình ảnh float từ ép cứng `[H]` (float barrier) sang cơ chế float linh hoạt `[htbp]` hoặc tinh chỉnh kích thước hình vẽ (từ `0.90\textwidth` sang `0.78\textwidth`--`0.80\textwidth` đối với các ảnh chụp màn hình UI) để văn bản và hình ảnh điền đầy tự nhiên, không làm gãy trang sớm khi trang còn trống nhiều diện tích.
- **Tuân thủ quy chuẩn định dạng đồ án tốt nghiệp:**
  - Giữ nguyên thiết lập phông chữ Times New Roman 13pt.
  - Giữ nguyên chế độ dãn dòng 1,5 lines (`\onehalfspacing` trong `setspace`).
  - Giữ nguyên căn lề trang chuẩn HUMG (Top 2.5cm, Bottom 2.5cm, Left 3.5cm, Right 2.5cm).
  - Giữ nguyên số trang ở góc dưới bên phải, không in nghiêng.
- **Biên dịch XeLaTeX thành công:** Biên dịch `main.tex` sạch sẽ không phát sinh lỗi hoặc cảnh báo đè trang.

### Non-goals
- Không viết lại nội dung học thuật hoặc làm thay đổi logic các thuật toán và phân hệ.
- Không thu nhỏ phông chữ văn bản hay nén co dãn chữ để lấp khoảng trống.

### Anti-goals
- Không giải quyết khoảng trắng bằng cách ép cứng thêm các lệnh `\vspace*{-...}` tiêu cực làm đè chữ lên hình ảnh.
- Không để xảy ra tình trạng hình bị trôi sang tận chương tiếp theo (sử dụng gói `placeins` hoặc `\FloatBarrier` ở ranh giới các mục lớn nếu cần).
- Không để sót lại bảng nào dùng kiểu hở viền dọc.

---

## 3. Các phương án đã cân nhắc (Approaches Considered)

1. **Phương án 1 (Đã chọn): Quy chuẩn khung viền lưới bảng toàn diện + Dỡ bỏ `\clearpage` cưỡng bức, tối ưu dòng chảy văn bản**
   - *Cách làm:* Chuyển đổi Bảng 1-1 sang bảng lưới khép kín 4 góc; xóa bỏ toàn bộ `\clearpage` dư thừa nội bộ mục; chuyển hình ảnh sang `[htbp]` và căn chỉnh tỷ lệ hình hợp lý (`0.78\textwidth`) để chữ và hình chảy liên tục, lấp đầy các khoảng trống.
   - *Lý do chọn:* Khắc phục triệt để căn nguyên gốc rễ lỗi dàn trang LaTeX, xử lý đồng bộ toàn bộ đồ án, bảo đảm mỹ quan chuyên nghiệp và đáp ứng trọn vẹn yêu cầu của GVHD.
2. **Phương án 2: Chỉ sửa cục bộ Bảng 1-1 và trang 98 (Hình 4-6)**
   - *Đánh đổi:* Thời gian sửa nhanh nhưng mang tính đối phó; khi GVHD lật sang các trang khác (như trang 99, 100 ở Chương 4 hay các trang ở Chương 2, 3) vẫn còn đầy rẫy các trang bị trống một nửa do `\clearpage`.
3. **Phương án 3: Giữ nguyên `[H]` và `\clearpage` nhưng viết thêm văn bản dài dòng để lấp chỗ trống**
   - *Đánh đổi:* Làm loãng nội dung, mất cân đối bố cục học thuật và không giải quyết được vấn đề kỹ thuật của LaTeX.

---

## 4. Đặc tả kỹ thuật chi tiết (Detailed Technical Specifications)

### 4.1. Quy chuẩn Khung viền Bảng biểu (Full Grid Table Borders)
- **Tệp `chapters/ch1/1_2_tinh_cap_thiet.tex` (Bảng 1-1):**
  - Chuyển `tabularx` không viền thành:
    ```latex
    \begin{tabular}{|>{\bfseries\raggedright\arraybackslash}p{2.3cm}|>{\raggedright\arraybackslash}p{2.8cm}|>{\raggedright\arraybackslash}p{2.7cm}|>{\raggedright\arraybackslash}p{2.4cm}|>{\raggedright\arraybackslash}p{2.4cm}|>{\raggedright\arraybackslash}p{2.6cm}|}
    \hline
    \textbf{Nền tảng} & \textbf{Định vị tọa độ PDF 2 cột} & \textbf{Truy xuất lai Hybrid RRF \& Cross-Encoder} & \textbf{Đồ thị tri thức 4 thực thể \& Wiki} & \textbf{Tự sửa lỗi biên dịch LaTeX (ReAct)} & \textbf{Quản lý khóa BYOK AES-256-GCM} \tabularnewline \hline
    ...
    \hline
    \end{tabular}
    ```
  - Thay thế các lệnh `\toprule`, `\midrule`, `\bottomrule` và `\addlinespace` bằng `\hline` và `\tabularnewline \hline` khép kín.
- **Rà soát tất cả các bảng khác:**
  - Đảm bảo toàn bộ các bảng trong `ch2`, `ch3`, `ch4` đều có cấu trúc cột bắt đầu và kết thúc bằng `|` (ví dụ `|c|p{...}|...|`) và các hàng phân tách bằng `\hline`.

### 4.2. Khắc phục Khoảng trắng thừa và Dồn dòng chảy Văn bản
- **Loại bỏ lệnh ngắt trang cưỡng bức:**
  - `chapters/ch4/4_2_giao_dien.tex`: Xóa bỏ 11 lệnh `\clearpage` trước các `\subsubsection` giao diện (từ Giao diện Đăng ký đến Giao diện Đồng tác giả).
  - `chapters/ch2/2_5_agentic_react.tex`: Xóa bỏ 7 lệnh `\clearpage` trước các tác tử phụ.
  - `chapters/ch3/3_5_bieu_do_tuan_tu.tex`: Xóa bỏ 3 lệnh `\clearpage` ngắt dòng vô lý.
  - `chapters/ch2/2_3_advanced_rag.tex`: Rà soát và gỡ các `\clearpage` dư thừa.
- **Tối ưu hóa vị trí và kích thước hình ảnh:**
  - Trong `4_2_giao_dien.tex`: Chuyển định vị hình từ `\begin{figure}[H]` sang `\begin{figure}[htbp]`, điều chỉnh kích thước từ `width=0.90\textwidth` sang `width=0.78\textwidth` (hoặc `width=0.80\textwidth`). Tỷ lệ này vừa hiển thị hình ảnh giao diện rõ nét, vừa tiết kiệm 3--4 cm chiều dọc mỗi trang, giúp văn bản giới thiệu của mục tiếp theo có thể lập tức nằm ngay phía dưới hình ảnh nếu còn chỗ trên trang giấy.
  - Sử dụng lệnh `\Needspace{4\baselineskip}` ở đầu các tiêu đề mục con để chống hiện tượng mồ côi tiêu đề (*orphan heading*) ở cuối trang mà không gây ngắt trang giả tạo khi còn nhiều chỗ.

---

## 5. Kế hoạch Kiểm chứng và Đo kiểm (Verification Plan)
1. **Kiểm tra tự động bằng mã nguồn (Script Verification):**
   - Xây dựng kịch bản kiểm thử `scripts/verify_table_borders_and_spacing.py`:
     - Kiểm tra toàn bộ các tệp `.tex` trong `chapters/` không còn sử dụng `\toprule`, `\midrule`, `\bottomrule` trong môi trường bảng.
     - Kiểm tra không còn các lệnh `\clearpage` nằm bên trong các tiểu mục của `4_2_giao_dien.tex` và `2_5_agentic_react.tex`.
2. **Biên dịch và kiểm tra trang in:**
   - Thực thi `latexmk -xelatex main.tex` trong `report-datn/`.
   - Biên dịch thành công với mã thoát 0.
   - Dùng công cụ phân tích hoặc trích xuất để kiểm tra trang 98 (và các trang lân cận): xác nhận nội dung của `4.2.1.6 Giao diện quản lý thư viện nghiên cứu cá nhân` chảy mượt mà ngay sau Hình 4-6 mà không bị đẩy sang trang mới để lại khoảng trống lớn.
