# BÁO CÁO TRIỂN KHAI CHỈNH SỬA TOÀN DIỆN CHƯƠNG 1 (CHAPTER 1 IMPLEMENTATION REPORT)
**Chuyên đề:** Triển khai chỉnh sửa nội dung, số liệu, tính chân thực, format và trích dẫn học thuật tại Chương 1  
**Đề tài:** *Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn*  
**Sinh viên thực hiện:** Đàm Mạnh Dũng — MSSV: `2221050359` — Lớp: `DCCTCT67_09B`  
**Giảng viên hướng dẫn:** ThS. Vũ Lan Phương — Bộ môn Hệ thống thông tin và Tri thức, Khoa CNTT, Trường Đại học Mỏ - Địa chất (HUMG)  
**Thời điểm thực hiện:** 2026-11-02  
**Tác tử thực hiện:** Tác tử Triển khai Chương 1 (Chapter 1 Implementer — `worker_ch1_impl`)  
**Tài liệu căn cứ:**  
- `report-datn/review_reports/SUMMARY_REVIEW.md`  
- `report-datn/review_reports/chapter_1_review.md`  
- `report-datn/INFORMATION.md` (SSOT)  
- `report-datn/AGENTS.md`  
- `report-datn/ROADMAP.md`  

---

## 1. TỔNG QUAN KẾT QUẢ TRIỂN KHAI

Tác tử đã rà soát và thực hiện chỉnh sửa toàn diện trên toàn bộ các tệp nguồn cấu thành Chương 1 ("Tổng quan về đề tài"), bao gồm tệp điều phối `chapters/ch1_tong_quan.tex` và 6 tệp vi mô từ `chapters/ch1/1_1_gioi_thieu.tex` đến `chapters/ch1/1_6_bo_cuc.tex`. 

Toàn bộ các vi phạm được chỉ ra trong báo cáo đánh giá độc lập `chapter_1_review.md` (26 điểm khuyến nghị) và `ORIGINAL_REQUEST.md` (yêu cầu R2) đã được xử lý triệt để 100%:
1. **Khóa cứng chỉ số IoU Bounding Box:** Đồng bộ ngưỡng kỹ thuật $\text{IoU} \ge 0{,}85$ và số liệu đo đạc thực tế trung bình $0{,}88$ theo đúng SSOT `INFORMATION.md`.
2. **Bảo toàn liêm chính học thuật trong Mục tiêu nghiên cứu:** Loại bỏ hoàn toàn việc đưa trước các kết quả đo đạc thực nghiệm cục bộ ($0{,}9266$ và $96\%$) vào Mục 1.3; xóa bỏ hoàn toàn số liệu phỏng đoán lý thuyết 98% CAS không có cơ sở kiểm chứng.
3. **Hiệu chỉnh chuẩn xác bản chất kỹ thuật PostgreSQL FTS:** Khẳng định chính xác PostgreSQL Full-Text Search sử dụng hàm chấm điểm mật độ bao phủ `ts_rank_cd` trên chỉ mục GIN `tsvector`, còn mô hình Okapi BM25 được tích hợp bổ trợ.
4. **Chuẩn hóa thể thức chế bản XeLaTeX và Typography:** Sửa lỗi dấu nháy kép mở đầu thành ``...'' chuẩn XeLaTeX; loại bỏ toàn bộ dấu gạch chéo thoát cách sau macro `\VS\ ` thành `\VS ` nhằm chống lỗi nhân đôi khoảng trắng.
5. **Chuẩn hóa bảng biểu:** Bảng 1-1 được duy trì trong môi trường `tabularx \textwidth`, tiêu đề `\caption` đặt ở PHÍA TRÊN bảng, bổ sung tham số float bắt buộc `[!htbp]` chống khoảng trống chân trang (Anti-Bottom-Gap).
6. **Triệt tiêu toàn diện vấn nạn Zero Citations:** Bổ sung đầy đủ 13 lượt trích dẫn học thuật `\cite{...}` cho các thuật toán, kiến trúc và tiêu chuẩn nền tảng (`edge2024`, `lewis2020`, `asai2023selfrag`, `yan2024crag`, `cockburn2005`, `cormack2009`, `malkov2018`, `robertson1995`, `yao2022`, `agache2020firecracker`, `dworkin2007`).
7. **Rút gọn tiêu đề và bổ sung đoạn chuyển tiếp:** Rút gọn tiêu đề Mục 1.6 thành `Bố cục báo cáo đồ án` (5 từ, đạt chuẩn 3--7 từ của HUMG); bổ sung đoạn mở đầu chương (bridging paragraph) tại `ch1_tong_quan.tex`.

---

## 2. BẢNG TỔNG HỢP CHI TIẾT CÁC THAY ĐỔI THEO TỪNG TỆP NGUỒN

| TT | Tệp Nguồn | Vị Trí Dòng | Nội Dung Trước Khi Sửa | Nội Dung Sau Khi Sửa | Lý Do Kỹ Thuật & Căn Cứ Học Thuật |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **1** | `chapters/ch1_tong_quan.tex` | 6--8 | Nhảy ngay vào `\input{chapters/ch1/1_1_gioi_thieu}` sau `\label{ch:tong_quan}` | Bổ sung đoạn văn chuyển tiếp 3 câu giới thiệu bối cảnh, tính cấp thiết, mục tiêu và 4 không gian học thuật của \VS. | Khắc phục lỗi thiếu đoạn mở đầu chương, hoàn thiện cấu trúc Minto Pyramid theo hướng dẫn của Khoa CNTT — HUMG. |
| **2** | `chapters/ch1/1_1_gioi_thieu.tex` | 4 | `\textit{''Xây dựng nền tảng...''}` | `\textit{``Xây dựng nền tảng...''}` | Sửa lỗi dấu nháy kép đóng đặt ở đầu cụm từ trong XeLaTeX gây hiển thị sai hướng trích dẫn. |
| **3** | `chapters/ch1/1_1_gioi_thieu.tex` | 6 | `...kiến trúc Agentic RAG...` | `...kiến trúc tác nhân tạo sinh tăng cường truy xuất (Agentic RAG -- \textit{Retrieval-Augmented Generation})...` | Giải nghĩa rõ ràng từ viết tắt ngay tại lần xuất hiện đầu tiên trong toàn văn đồ án (`AGENTS.md` Mục 2.6.1). |
| **4** | `chapters/ch1/1_1_gioi_thieu.tex` | 6 | `...GraphRAG...` | `...GraphRAG \cite{edge2024}...` | Bổ sung trích dẫn học thuật cho công trình GraphRAG của Microsoft Research (Edge et al., 2024). |
| **5** | `chapters/ch1/1_1_gioi_thieu.tex` | 8 | `Hệ thống \VS\ tập trung...` | `Hệ thống \VS tập trung...` | Loại bỏ dấu gạch chéo thoát khoảng trắng sau macro `\VS` (vốn đã dùng gói `xspace`), chống lỗi nhân đôi khoảng cách (*double spaces*). |
| **6** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 6 | `...kiến trúc tạo sinh tăng cường truy xuất (RAG -- \textit{Retrieval-Augmented Generation})... \cite{lewis2020}` | `...kiến trúc tạo sinh tăng cường truy xuất (RAG \cite{lewis2020})...` | Tinh gọn cụm từ tiếng Anh lặp lại vì đã được định nghĩa đầy đủ tại Mục 1.1. |
| **7** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 14 | `...với hệ thống \VS\ theo năm tiêu chí...` | `...với hệ thống \VS theo năm tiêu chí...` | Loại bỏ dấu gạch chéo thoát cách gây lặp khoảng trắng. |
| **8** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 16 | `\begin{table}[htbp]` | `\begin{table}[!htbp]` | Bổ sung tham số float bắt buộc `!` theo quy chuẩn Anti-Bottom-Gap (`AGENTS.md` Mục 2.2.4 và 2.5). |
| **9** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 25 | `\textbf{Truy xuất lai Hybrid RRF và Cross-Encoder}` | `\textbf{Truy xuất lai RRF và Cổng kiểm định CRAG}` | Tiêu đề Bảng 1-1 làm nổi bật đóng góp cốt lõi số 1 của đề tài là Cổng kiểm định CRAG thay vì thư viện phụ Cross-Encoder. |
| **10** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `\VS\ (Đề tài)` | `\VS (Đề tài)` | Loại bỏ dấu gạch chéo thoát cách gây lặp khoảng trắng trong ô bảng. |
| **11** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `...($\text{IoU} = 0{,}9266$)...` | `...($\text{IoU} \ge 0{,}85$, thực tế $0{,}88$)...` | Đồng bộ 100% với SSOT trong `INFORMATION.md` (Mục 2.4 & 5.1). Con số $0{,}9266$ chỉ là kết quả cục bộ của riêng nhóm thí nghiệm bóc tách tại Ch4. |
| **12** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `...Hybrid RRF ($k=60$) kết hợp Cross-Encoder...` | `...Hybrid RRF ($k=60$) kết hợp cổng kiểm chứng CRAG và FlashRank...` | Đồng bộ chính xác thuật toán lõi theo đúng thiết kế mã nguồn thực tế. |
| **13** | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `...($96\%$)` | `...($96{,}0\%$)` | Chuẩn hóa số liệu thực nghiệm có một chữ số phần thập phân theo chuẩn báo cáo khoa học. |
| **14** | `chapters/ch1/1_3_muc_tieu.tex` | 7 | `...phần mềm \VS\ đóng vai trò...` | `...phần mềm \VS đóng vai trò...` kèm `\cite{cockburn2005}` | Loại bỏ dấu gạch chéo thoát cách và bổ sung trích dẫn cho Kiến trúc Lục giác (Cockburn, 2005). |
| **15** | `chapters/ch1/1_3_muc_tieu.tex` | 13 | `(tiết kiệm tới 98\% dung lượng lưu trữ tệp nhị phân trên máy chủ trong kịch bản 50 học giả cùng nạp một bài báo kinh điển)` | Loại bỏ hoàn toàn mệnh đề phỏng đoán lý thuyết này | Triệt tiêu số liệu phỏng đoán chưa qua thực chứng, bảo đảm tính liêm chính học thuật (AP-04). |
| **16** | `chapters/ch1/1_3_muc_tieu.tex` | 14 | `...HNSW Cosine 1536 chiều...` | `...HNSW Cosine 1536 chiều \cite{malkov2018}...` | Bổ sung trích dẫn công trình chỉ mục xấp xỉ lân cận gần nhất HNSW (Malkov & Yashunin, 2018). |
| **17** | `chapters/ch1/1_3_muc_tieu.tex` | 14 | `...thuật toán hợp nhất xếp hạng đảo ngược RRF...` | `...thuật toán hợp nhất xếp hạng đảo ngược RRF (\textit{Reciprocal Rank Fusion} \cite{cormack2009}, $k=60$)...` | Bổ sung trích dẫn công trình RRF (Cormack et al., 2009). |
| **18** | `chapters/ch1/1_3_muc_tieu.tex` | 14 | `...chỉ mục GIN \texttt{tsvector} kết hợp tái chấm điểm Okapi BM25...` | `...chỉ mục GIN \texttt{tsvector} với hàm xếp hạng mật độ bao phủ \texttt{ts\_rank\_cd}, kết hợp bổ trợ mô hình Okapi BM25 \cite{robertson1995}...` | Sửa đúng bản chất kỹ thuật cài đặt FTS của PostgreSQL trong mã nguồn thực tế và bổ sung trích dẫn Robertson et al. (1995). |
| **19** | `chapters/ch1/1_3_muc_tieu.tex` | 14 | `...$\text{IoU} \ge 0{,}85$ (thực nghiệm đạt $0{,}9266 \pm 0{,}0126$)...` | `...với ngưỡng độ trùng khớp $\text{IoU} \ge 0{,}85$...` | Xóa bỏ kết quả đo đạc thực nghiệm cục bộ ra khỏi mục tiêu nghiên cứu (để dành dữ liệu đo đạc cho Chương 4). |
| **20** | `chapters/ch1/1_3_muc_tieu.tex` | 15 | `...GraphRAG...` | `...GraphRAG \cite{edge2024}...` | Bổ sung trích dẫn học thuật cho GraphRAG (Edge et al., 2024). |
| **21** | `chapters/ch1/1_3_muc_tieu.tex` | 16 | `...trên 90\% (thực nghiệm đạt $96\%$ trên tập 25 ca kiểm thử lỗi chuẩn)...` | `...với ngưỡng tỷ lệ tự phục hồi thành công trên 90\%...` | Xóa bỏ kết quả đo lường thực nghiệm ra khỏi phần mục tiêu nghiên cứu. |
| **22** | `chapters/ch1/1_3_muc_tieu.tex` | 16 | `...LangGraph ReAct...` và `...E2B Sandbox MicroVM...` | `...LangGraph ReAct \cite{yao2022}...` và `...E2B Sandbox MicroVM \cite{agache2020firecracker}...` | Bổ sung trích dẫn mẫu tác nhân ReAct (Yao et al., 2022) và nền tảng máy ảo siêu nhẹ Firecracker (Agache et al., 2020). |
| **23** | `chapters/ch1/1_4_noi_dung.tex` | 9 | `...nguyên lý kiến trúc lục giác...` | `...nguyên lý kiến trúc lục giác (\textit{Hexagonal Architecture / Ports and Adapters} \cite{cockburn2005})...` | Bổ sung trích dẫn Alistair Cockburn (2005). |
| **24** | `chapters/ch1/1_4_noi_dung.tex` | 10 | `...giải thuật hợp nhất xếp hạng đảo ngược RRF...` | `...giải thuật hợp nhất xếp hạng đảo ngược RRF \cite{cormack2009}...` | Bổ sung trích dẫn Cormack et al. (2009). |
| **25** | `chapters/ch1/1_4_noi_dung.tex` | 12 | `...chu trình tác nhân ReAct...` | `...chu trình tác nhân ReAct \cite{yao2022}...` | Bổ sung trích dẫn Yao et al. (2022). |
| **26** | `chapters/ch1/1_4_noi_dung.tex` | 13 | `...thuật toán AES-256-GCM với nguyên tắc Zero-Retention trên bộ nhớ RAM` | `...thuật toán AES-256-GCM \cite{dworkin2007}, không lưu trữ khóa bản rõ và chỉ giải mã tạm thời trong bộ nhớ tiến trình` | Loại bỏ buzzword thương mại "Zero-Retention", diễn đạt chuẩn xác cơ chế kỹ thuật và bổ sung trích dẫn tiêu chuẩn NIST SP 800-38D (Dworkin, 2007). |
| **27** | `chapters/ch1/1_4_noi_dung.tex` | 18 | `...duy trì tỷ lệ kiểm thử thành công 100\% qua 4 cổng kiểm định tự động bắt buộc trước khi phát hành` | `...duy trì tỷ lệ kiểm thử thành công 100\% thông qua hệ thống kiểm thử tự động toàn diện từ kiểm định tĩnh mã nguồn, kiểm thử đơn vị, kiểm thử tích hợp đến kiểm thử hồi quy kiến trúc` | Loại bỏ thuật ngữ nội bộ harness ("4 cổng kiểm định"), thay bằng ngôn từ học thuật đại học phổ quát. |
| **28** | `chapters/ch1/1_5_pham_vi.tex` | 8 | `...đồ thị tri thức (GraphRAG)...` | `...đồ thị tri thức (GraphRAG \cite{edge2024})...` | Bổ sung trích dẫn học thuật cho công nghệ GraphRAG. |
| **29** | `chapters/ch1/1_5_pham_vi.tex` | 9 | `...môi trường Sandbox E2B...` | `...môi trường Sandbox E2B \cite{agache2020firecracker}...` | Bổ sung trích dẫn công nghệ máy ảo Firecracker ảo hóa cho Sandbox E2B. |
| **30** | `chapters/ch1/1_6_bo_cuc.tex` | 2 | `\section{Bố cục của báo cáo đồ án tốt nghiệp}` | `\section{Bố cục báo cáo đồ án}` | Rút gọn tiêu đề mục từ 8 từ xuống đúng 5 từ (tuân thủ giới hạn 3--7 từ của `AGENTS.md` Mục 2.4.3). |
| **31** | `chapters/ch1/1_6_bo_cuc.tex` | 6--10 | Mô tả liệt kê dày đặc các tên thư viện và công cụ phụ trợ | Tinh gọn mô tả Chương 2 tập trung vào 4 trụ cột kiến trúc cốt lõi; đồng bộ số liệu kiểm thử Chương 4 (580 kịch bản, 100% pass). | Nâng cao tính cô đọng của phần tóm tắt cấu trúc đồ án, tránh làm loãng nội dung. |

---

## 3. ĐỐI CHIẾU SỐ TRANG VÀ THỐNG KÊ NGÂN SÁCH TRANG IN

- **Trước khi tinh gọn:** Toàn văn Chương 1 chiếm 7 trang in (trang 3 đến trang 9 trong `main.pdf`).
- **Sau khi triển khai:** Toàn văn Chương 1 tiếp tục duy trì đúng **7 trang in** (từ trang 3 đến trang 9). Cụ thể:
  - Trang 3: Tiêu đề Chương 1, Đoạn mở đầu chuyển ý, Mục 1.1 (Giới thiệu đề tài).
  - Trang 4: Mục 1.2 (Tính cấp thiết của đề tài và 4 rào cản).
  - Trang 5: Bảng 1-1 (Đối chiếu năng lực kỹ thuật các công cụ hiện hành so với VeriScholar) và đoạn văn chuyển tiếp.
  - Trang 6: Mục 1.3 (Mục tiêu tổng quát và 4 mục tiêu kỹ thuật cụ thể).
  - Trang 7: Mục 1.4 (Nội dung nghiên cứu và phương pháp tiếp cận) & Mục 1.5 (Phạm vi và đối tượng nghiên cứu).
  - Trang 8 -- 9: Mục 1.6 (Bố cục báo cáo đồ án, phân tích tóm lược 4 chương và kết luận).
  - Trang 10: Chuyển tiếp sang Chương 2 (`ch2_co_so_ly_thuyet.tex`).
- **Đánh giá chuẩn mực:** Dung lượng 7 trang chiếm $\approx 8{,}5\%$ thân bài chính ($7/82$ trang mục tiêu), nằm trọn vẹn trong **ngân sách vàng** ($6 \text{ -- } 8$ trang, tối đa $10\%$) theo Quy chế và Hướng dẫn thực hiện ĐATN của Khoa Công nghệ Thông tin — Trường Đại học Mỏ - Địa chất (HUMG).

---

## 4. KẾT QUẢ KIỂM CHỨNG VÀ XÁC MINH BIÊN DỊCH

1. **Biên dịch XeLaTeX toàn văn (`latexmk -xelatex main.tex` / `xelatex main.tex`):**
   - **Exit code:** `0` (Thành công tuyệt đối).
   - **Lỗi biên dịch nghiêm trọng (Fatal Errors):** `0`.
   - **Tham chiếu hoặc trích dẫn chưa định nghĩa (Undefined citations/references):** `0` (Không có bất kỳ cảnh báo undefined citation hoặc undefined reference nào liên quan đến Chương 1).
   - **Cảnh báo tràn lề (Overfull `\hbox`):** `0` cảnh báo trong toàn bộ Chương 1. Bảng 1-1 vừa khít lề ngang $15{,}0\,\text{cm}$ nhờ môi trường `tabularx{\textwidth}`.
2. **Kiểm thử tự động bằng Pytest (`tests/test_thesis_structure_and_compile.py`):**
   - `test_thesis_files_exist`: **PASSED** (100% các tệp vi mô của Chương 1 tồn tại theo đúng hợp đồng cấu trúc).
   - `test_thesis_compilation`: **PASSED** (Biên dịch XeLaTeX thành công hai lượt liên tiếp).
   - `test_thesis_vietnamese_accented_characters_support`: **PASSED** (144/144 biến thể nguyên âm tiếng Việt hiển thị hoàn hảo, không có ký tự bị thiếu).
   - `test_thesis_no_undefined_references`: **PASSED** (Không có trích dẫn hoặc nhãn tham chiếu nào bị thiếu).
3. **Liêm chính học thuật và Đối soát SSOT:**
   - 100% số liệu đo lường Bounding Box IoU được quy về $\text{IoU} \ge 0{,}85$ (thực tế $0{,}88$) theo đúng `INFORMATION.md`.
   - Toàn bộ kết quả thực nghiệm đo đạc định lượng cục bộ ($0{,}9266$ và $96\%$) cùng số liệu suy diễn lý thuyết 98% đã được bóc tách hoàn toàn khỏi Mục tiêu nghiên cứu.
   - Cơ chế tìm kiếm toàn văn FTS trong PostgreSQL được giải thích trung thực: hàm xếp hạng `ts_rank_cd` trên chỉ mục GIN `tsvector` kết hợp bổ trợ mô hình Okapi BM25.

---

## 5. KẾT LUẬN VÀ BÀN GIAO

Gói công việc hiệu chỉnh Chương 1 đã hoàn tất 100% các tiêu chí chất lượng, tuân thủ nghiêm ngặt ranh giới phạm vi phân công, không sửa đổi bất kỳ tệp tin nào ngoài phạm vi Chương 1, sẵn sàng để Tác tử Tích hợp và Nghiệm thu Toàn văn (`integrator_agent`) tiến hành kiểm chứng chéo và đóng gói nghiệm thu.
