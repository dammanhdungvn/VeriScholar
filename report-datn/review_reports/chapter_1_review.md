# BÁO CÁO ĐÁNH GIÁ ĐỘC LẬP CHƯƠNG 1 (CHAPTER 1 INDEPENDENT REVIEW REPORT)
**Chuyên đề:** Đánh giá nội dung, format, số liệu, tính chân thực và hệ thống sơ đồ hình ảnh tại Chương 1  
**Đề tài:** *Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn*  
**Sinh viên thực hiện:** Đàm Mạnh Dũng — MSSV: `2221050359` — Lớp: `DCCTCT67_09B`  
**Giảng viên hướng dẫn:** ThS. Vũ Lan Phương — Bộ môn Hệ thống thông tin và Tri thức, Khoa CNTT, Trường Đại học Mỏ - Địa chất (HUMG)  
**Thời điểm thực hiện:** 2026-11-02  
**Đơn vị thẩm định:** Tác tử Đánh giá Độc lập Chương 1 (Chapter 1 Independent Reviewer — `worker_ch1_review`)

---

## TỔNG QUAN VÀ TÓM TẮT KẾT QUẢ ĐÁNH GIÁ (EXECUTIVE SUMMARY)

Chương 1 ("Tổng quan về đề tài", tương ứng "Mô tả bài toán" theo định hướng của Khoa CNTT — HUMG) giữ vai trò then chốt trong việc trả lời câu hỏi cốt tử đầu tiên của đồ án tốt nghiệp: **"LÀM GÌ? CHO ĐỐI TƯỢNG NÀO?"** (*What and For Whom*).

Qua khảo sát toàn diện 6 tệp mã nguồn vi mô (`1_1_gioi_thieu.tex` đến `1_6_bo_cuc.tex`) cùng tệp điều phối [`chapters/ch1_tong_quan.tex`](../chapters/ch1_tong_quan.tex), đối soát với Hồ sơ đề tài [`INFORMATION.md`](../INFORMATION.md), Cẩm nang quy chuẩn [`AGENTS.md`](../AGENTS.md), 4 tài liệu hướng dẫn của Khoa CNTT — HUMG ([`guide/`](../guide)) và thực tế mã nguồn tại Monorepo VeriScholar (`packages/core/`, `apps/api/`, `apps/web/`, `docs/`), kết quả đánh giá tổng thể được tóm lược như sau:

| Tiêu Chí Đánh Giá | Hiện Trạng | Đánh Giá Tóm Tắt | Mức Độ Nghiêm Trọng |
| :--- | :---: | :--- | :---: |
| **Bố cục & Ngân sách trang** | 5 -- 6 trang | Tuân thủ tốt ngân sách vàng ($\le 8$ trang, chiếm $\approx 10\%$ dung lượng toàn bài). | **ĐẠT** |
| **Tính xác thực & Số liệu** | 5 điểm sai lệch | Xuất hiện số liệu IoU mâu thuẫn giữa Ch1 và SSOT; đưa trước kết quả thực nghiệm vào mục tiêu; giả định suy diễn 98% chưa thực chứng; nhầm lẫn thuật toán FTS PostgreSQL với BM25. | **CẦN SỬA ĐỔI** |
| **Format & Quy chuẩn XeLaTeX** | 7 vi phạm | Lỗi dấu nháy kép `''...''`; lặp dấu cách sau macro `\VS\`; thiếu vị trí float `[!htbp]`; thiếu trích dẫn học thuật cho các thuật ngữ nền tảng; tiêu đề mục dài; thiếu đoạn mở đầu chương. | **CẦN SỬA ĐỔI** |
| **Hệ thống Hình ảnh & Sơ đồ** | 0 hình / 1 bảng | Hoàn toàn không có hình vẽ minh họa (0 hình ảnh); có 1 bảng đối sánh tính năng (Bảng 1-1). Thiếu sơ đồ ý niệm 4 Không gian nghiên cứu trực quan. | **CẦN BỔ SUNG / SỬA BẢNG** |

---

## MỤC 1: PHÂN TÍCH CHI TIẾT NỘI DUNG DƯ THỪA, KHÔNG CẦN THIẾT VÀ SAI SỰ THẬT SO VỚI THỰC TẾ DỰ ÁN VERISCHOLAR

### 1.1. Bất nhất số liệu IoU giữa Chương 1 và Hồ sơ đề tài chuẩn (`INFORMATION.md`)
- **Vị trí vi phạm:**
  - `report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex`, dòng 31 (Bảng 1-1): ghi `Ánh xạ tọa độ chuẩn hóa trên PDF 2 cột ($\text{IoU} = 0{,}9266$)`.
  - `report-datn/chapters/ch1/1_3_muc_tieu.tex`, dòng 14: ghi `đạt độ chính xác trung bình $\text{IoU} \ge 0{,}85$ (thực nghiệm đạt $0{,}9266 \pm 0{,}0126$)`.
- **Thực tế đối chiếu:**
  - Căn cứ Hồ sơ đề tài [`INFORMATION.md`](../INFORMATION.md) (Nguồn chân lý duy nhất — SSOT):
    - Mục 2.4 (Đóng góp 2): *"đối soát tọa độ khung viền vàng Bounding Box với ngưỡng $\text{IoU} \ge 0{,}85$"*.
    - Mục 5.1 (Chỉ số đo lường gốc): *"Độ trùng khớp tọa độ trích dẫn (IoU Bounding Box): Đạt ngưỡng $\text{IoU} \ge 0{,}85$ (thực tế trung bình $0{,}88$)"*.
  - Trong tệp kết quả benchmark gốc `docs/benchmarks/thesis_benchmark_results.json` (dòng 887-888), con số `0.9266` là điểm `mean_iou` cục bộ của riêng nhóm thí nghiệm bóc tách `hybrid_rrf` trên tập 36 câu hỏi đánh giá.
- **Hậu quả học thuật:** Việc tự ý đưa con số $0{,}9266$ vào Chương 1 gây mâu thuẫn trực tiếp với chỉ số thực tế trung bình $0{,}88$ đã được thẩm định và công bố tại SSOT. Khi Hội đồng phản biện đối chiếu giữa Chương 1 và Chương 4 / INFORMATION.md sẽ phát hiện sự không đồng nhất về dữ liệu thực nghiệm.
- **Kiến nghị tinh gọn:**
  - Tại Bảng 1-1 (`1_2_tinh_cap_thiet.tex`): Hiệu chỉnh thành `$\text{IoU} \ge 0{,}85$ (trung bình thực tế $0{,}88$)` hoặc chỉ ghi ngắn gọn tiêu chí đạt ngưỡng `$\text{IoU} \ge 0{,}85$`.
  - Tại Mục 1.3 (`1_3_muc_tieu.tex`): Loại bỏ số liệu kết quả đo đạc trong ngoặc đơn, chỉ giữ lại chỉ tiêu kỹ thuật cần đạt: `đạt độ chính xác trung bình $\text{IoU} \ge 0{,}85$`.

### 1.2. Lẫn lộn giữa "Mục tiêu nghiên cứu" (Objectives) và "Kết quả thực nghiệm" (Empirical Results)
- **Vị trí vi phạm:**
  - `report-datn/chapters/ch1/1_3_muc_tieu.tex`, dòng 14: `...đạt độ chính xác trung bình $\text{IoU} \ge 0{,}85$ (thực nghiệm đạt $0{,}9266 \pm 0{,}0126$)`.
  - `report-datn/chapters/ch1/1_3_muc_tieu.tex`, dòng 16: `...đạt tỷ lệ thành công trên 90\% (thực nghiệm đạt $96\%$ trên tập 25 ca kiểm thử lỗi chuẩn)`.
- **Thực tế đối chiếu:**
  - Theo cấu trúc chuẩn mực của một báo cáo khoa học (và hướng dẫn của Khoa CNTT — HUMG tại `guide/Huong-dan-viet-DATN.md` Mục II), phần **Mục tiêu nghiên cứu** ở Chương 1 chỉ xác định bài toán, phương hướng giải quyết và **chỉ tiêu kỹ thuật mong muốn** cần hướng tới khi bắt đầu đề tài.
  - Toàn bộ kết quả thực nghiệm đo đạc định lượng (số phần trăm thành công, giá trị trung bình $\pm$ độ lệch chuẩn trên bao nhiêu ca kiểm thử) thuộc về **Chương 4** (Cài đặt và kết quả thực nghiệm) và phần **Kết luận**.
- **Hậu quả học thuật:** Đưa trước kết quả đo lường vào phần mục tiêu khiến người đọc cảm thấy đồ án bị viết ngược quy trình (viết mục tiêu sau khi đã có kết quả), làm mất đi tính khách quan của tiến trình nghiên cứu khoa học.
- **Kiến nghị tinh gọn:** Xóa bỏ hoàn toàn các phần trong ngoặc đơn chứa kết quả thực nghiệm tại Mục 1.3. Viết lại mục tiêu rõ ràng, tập trung vào yêu cầu kỹ thuật cần chinh phục:
  - Chỉ tiêu IoU: `...đạt độ trùng khớp khung viền tọa độ chuẩn hóa trên bản PDF gốc với ngưỡng $\text{IoU} \ge 0{,}85$`.
  - Chỉ tiêu tự sửa lỗi LaTeX: `...đạt tỷ lệ tự động phục hồi cú pháp thành công trên 90\% đối với các lỗi biên dịch phổ biến`.

### 1.3. Đưa ra số liệu suy diễn lý thuyết chưa qua thực chứng (Phỏng đoán 98%)
- **Vị trí vi phạm:** `report-datn/chapters/ch1/1_3_muc_tieu.tex`, dòng 13: `...(tiết kiệm tới 98\% dung lượng lưu trữ tệp nhị phân trên máy chủ trong kịch bản 50 học giả cùng nạp một bài báo kinh điển)...`
- **Thực tế đối chiếu:**
  - Đây là phép toán số học suy diễn lý thuyết đơn thuần ($1 - 1/50 = 98\%$), hoàn toàn không phải là số liệu đo lường thực nghiệm trên hệ thống chạy thực tế (không có bài test hay benchmark nào đo kịch bản 50 học giả đồng thời tải lên).
  - Vi phạm nguyên tắc chống số liệu phỏng đoán (Academic Integrity & AP-04).
- **Kiến nghị tinh gọn:** Loại bỏ hoàn toàn mệnh đề phỏng đoán `(tiết kiệm tới 98\%...)`. Diễn đạt lại mục tiêu CAS chuẩn xác: *"Hiện thực hóa cơ chế nạp bài báo hai tầng kết hợp kho lưu trữ định danh theo nội dung CAS (Content-Addressable Storage) dựa trên mã băm SHA-256 nhằm loại bỏ việc lưu trữ trùng lặp các tệp nhị phân PDF giữa nhiều người dùng, đồng thời quản lý an toàn vòng đời tài liệu theo cơ chế đếm tham chiếu (\texttt{ref\_count})."*

### 1.4. Sai lệch kỹ thuật về cơ chế tìm kiếm toàn văn trong PostgreSQL
- **Vị trí vi phạm:** `report-datn/chapters/ch1/1_3_muc_tieu.tex`, dòng 14: `...tìm kiếm từ vựng (chỉ mục GIN \texttt{tsvector} kết hợp tái chấm điểm Okapi BM25)...`
- **Thực tế đối chiếu:**
  - Kiểm tra trực tiếp mã nguồn tầng cơ sở dữ liệu và dịch vụ tìm kiếm tại `apps/api/src/api/services/session_chat_service.py` (dòng 596-618, 726-732) và mô hình `apps/api/src/api/db/models/chunk.py`:
    Truy vấn toàn văn FTS trong PostgreSQL sử dụng hàm chấm điểm mật độ bao phủ `ts_rank_cd(content_tsv, plainto_tsquery('english', :fts_query))` kết hợp `websearch_to_tsquery`.
  - PostgreSQL mặc định không tích hợp thuật toán Okapi BM25 (trừ khi cài đặt extension bên thứ ba như ParadeDB/pg_search). Thuật toán Okapi BM25 được đề cập trong đồ án là kiến thức lý thuyết nền tảng (trích dẫn Robertson 1995), nhưng việc khẳng định PostgreSQL FTS trong hệ thống *kết hợp tái chấm điểm Okapi BM25* là không đúng sự thật về mặt kỹ thuật cài đặt.
- **Kiến nghị tinh gọn:** Sửa thành: `tìm kiếm từ vựng toàn văn (chỉ mục GIN \texttt{tsvector} với hàm xếp hạng mật độ bao phủ \texttt{ts\_rank\_cd})`.

### 1.5. Lệch trọng tâm kỹ thuật trong Bảng 1-1 (Cross-Encoder so với CRAG)
- **Vị trí vi phạm:** `report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex`, dòng 25 và 31 (Bảng 1-1).
- **Thực tế đối chiếu:**
  - Tiêu đề cột 3 ghi: `\textbf{Truy xuất lai Hybrid RRF và Cross-Encoder}`. Dòng VeriScholar ghi: `Hybrid RRF ($k=60$) kết hợp Cross-Encoder`.
  - Trong khi đó, theo Hồ sơ đề tài [`INFORMATION.md`](../INFORMATION.md) Mục 2.4 (Đóng góp 1) và câu chốt của chính Mục 1.2 (dòng 35), đóng góp cốt lõi của đề tài là kiến trúc **Hybrid RAG kết hợp thuật toán RRF ($k=60$) và cổng phân loại độ tin cậy CRAG** (*Corrective RAG* với cơ chế active abstention từ chối trả lời khi ngữ cảnh yếu).
  - Cross-Encoder chỉ là giải pháp kỹ thuật bổ trợ ở tầng reranking (FlashRank ONNX), trong khi điểm mới học thuật tự kiểm chứng của hệ thống là **Cổng đánh giá độ tin cậy CRAG** \cite{yan2024crag}.
- **Kiến nghị tinh gọn:**
  - Sửa tiêu đề cột 3 thành: `\textbf{Truy xuất lai RRF và Cổng kiểm định CRAG}`.
  - Sửa ô của VeriScholar thành: `Hybrid RRF ($k=60$) kết hợp cổng kiểm chứng CRAG và FlashRank`.

### 1.6. Dư thừa thuật ngữ tiếp thị (Buzzwords) và cơ chế nội bộ Monorepo
- **Vị trí vi phạm:**
  - `report-datn/chapters/ch1/1_4_noi_dung.tex`, dòng 13: `...với nguyên tắc Zero-Retention trên bộ nhớ RAM`.
  - `report-datn/chapters/ch1/1_4_noi_dung.tex`, dòng 18: `...duy trì tỷ lệ kiểm thử thành công 100\% qua 4 cổng kiểm định tự động bắt buộc trước khi phát hành`.
- **Thực tế đối chiếu:**
  - "Zero-Retention trên bộ nhớ RAM" là một cụm từ quảng bá thương mại; thực chất hệ thống sử dụng cơ chế két khóa mã hóa AES-256-GCM lưu trong CSDL, giải mã biến tạm thời trong tiến trình xử lý và được bộ thu gom rác tự động giải phóng.
  - "4 cổng kiểm định tự động" (4 Verification Gates) là thuật ngữ nội bộ của Agent Harness Monorepo (được quy định trong `AGENTS.md`). Đối với báo cáo khoa học đại học, thuật ngữ này mang tính nội bộ, không phổ quát.
- **Kiến nghị tinh gọn:**
  - Diễn đạt lại dòng 13: `...với cơ chế két khóa cá nhân bảo mật AES-256-GCM, không lưu trữ khóa bản rõ và chỉ giải mã tạm thời trong bộ nhớ tiến trình`.
  - Diễn đạt lại dòng 18: `...duy trì tỷ lệ kiểm thử thành công 100\% thông qua hệ thống kiểm thử tự động toàn diện (kiểm định mã nguồn, kiểm thử đơn vị, kiểm thử tích hợp và kiểm thử biên dịch)`.

---

## MỤC 2: PHÂN TÍCH CHI TIẾT LỖI FORMAT VÀ VI PHẠM QUY CHUẨN

### 2.1. Lỗi ký tự nháy kép mở đầu trong môi trường XeLaTeX
- **Vị trí vi phạm:** `report-datn/chapters/ch1/1_1_gioi_thieu.tex`, dòng 4:
  `Đề tài tốt nghiệp \textit{''Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn''}...`
- **Quy chuẩn đối chiếu:** Trong chế bản LaTeX / XeLaTeX, dấu nháy đơn kép đóng `''` nếu đặt ở đầu cụm từ sẽ hiển thị thành hai dấu phẩy trên quay sang phải, làm đảo ngược quy cách trích dẫn tiếng Việt và tiếng Anh.
- **Cách sửa chuẩn xác:** Sử dụng hai dấu nháy ngược ` `` ` ở đầu:
  `\textit{``Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn''}`.

### 2.2. Lỗi nhân đôi khoảng trắng do xung đột macro `\VS\`
- **Vị trí vi phạm:**
  - `1_1_gioi_thieu.tex`, dòng 8: `Hệ thống \VS\ tập trung...`
  - `1_2_tinh_cap_thiet.tex`, dòng 14: `...hệ thống \VS\ theo năm tiêu chí...`
  - `1_2_tinh_cap_thiet.tex`, dòng 31 (Bảng 1-1): `\VS\ (Đề tài)`
  - `1_3_muc_tieu.tex`, dòng 7: `...nền tảng phần mềm \VS\ đóng vai trò...`
- **Quy chuẩn đối chiếu:** Trong `report-datn/config/commands.tex`, lệnh `\VS` được định nghĩa: `\newcommand{\VS}{VeriScholar\xspace}`. Gói `xspace` đã tự động chèn khoảng trắng nếu ký tự tiếp theo là một từ. Khi tác giả viết thêm dấu gạch chéo thoát cách `\VS\ `, trình biên dịch sẽ tạo ra hai dấu cách liên tiếp (*double spaces*), vi phạm tiêu chuẩn in ấn sạch sẽ của Khoa CNTT — HUMG.
- **Cách sửa chuẩn xác:** Thay toàn bộ `\VS\` bằng `\VS ` (chỉ dùng một dấu cách thông thường sau `\VS`).

### 2.3. Thiếu tham số vị trí float bắt buộc `[!htbp]`
- **Vị trí vi phạm:** `report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex`, dòng 16: `\begin{table}[htbp]`.
- **Quy chuẩn đối chiếu:** `report-datn/AGENTS.md` Mục 2.2.4 và Mục 2.5 quy định: *"Tất cả các đối tượng trôi nổi (Floats: Bảng biểu và Hình vẽ) bắt buộc phải khai báo tham số vị trí linh hoạt: `\begin{table}[!htbp]` và `\begin{figure}[!htbp]`"*. Tham số `!` chỉ thị cho trình biên dịch ưu tiên tối đa việc điền đầy trang, chống hiện tượng ngắt trang sớm để lại khoảng trắng lớn ở đáy trang in (*Anti-Bottom-Gap Standard*).
- **Cách sửa chuẩn xác:** Sửa thành `\begin{table}[!htbp]`.

### 2.4. Thiếu trích dẫn học thuật (`\cite`) cho các thuật ngữ và công trình nền tảng
- **Vị trí vi phạm:**
  - `1_1_gioi_thieu.tex`, dòng 6 và `1_3_muc_tieu.tex`, dòng 15: Khái niệm GraphRAG không có trích dẫn công trình nền tảng `\cite{edge2024}`.
  - `1_3_muc_tieu.tex`, dòng 14: Thuật toán chỉ mục vector HNSW không có trích dẫn `\cite{malkov2018}`.
  - `1_4_noi_dung.tex`, dòng 9: Kiến trúc Lục giác (Hexagonal Architecture / Ports and Adapters) không có trích dẫn `\cite{cockburn2005}`.
  - `1_4_noi_dung.tex`, dòng 10: Thuật toán hợp nhất xếp hạng đảo ngược (RRF) không có trích dẫn `\cite{cormack2009}`.
  - `1_4_noi_dung.tex`, dòng 12: Mẫu tác nhân ReAct không có trích dẫn `\cite{yao2022}`.
  - `1_4_noi_dung.tex`, dòng 13: Thuật toán mã hóa Galois/Counter Mode (AES-256-GCM) không có trích dẫn tiêu chuẩn NIST `\cite{dworkin2007}`.
- **Quy chuẩn đối chiếu:** Căn cứ `AGENTS.md` Mục 2.6.2 (Luật chống trích dẫn mồ côi): 100% tài liệu trong danh mục 20 tài liệu tham khảo chính thức phải được viện dẫn trực tiếp trong thân bài. Việc nhắc đến các khái niệm cốt lõi tại Chương 1 mà không gắn mã trích dẫn tương ứng làm giảm tính hàn lâm và tính liên kết của đồ án.
- **Cách sửa chuẩn xác:** Bổ sung các mã trích dẫn `\cite{...}` tại đúng vị trí xuất hiện thuật ngữ lần đầu.

### 2.5. Quy cách viết tắt và giải nghĩa thuật ngữ lần đầu
- **Vị trí vi phạm:**
  - `1_1_gioi_thieu.tex`, dòng 6: Cụm từ "Agentic RAG" xuất hiện lần đầu tiên trong toàn văn báo cáo nhưng không được viết rõ nghĩa gốc tiếng Anh của RAG (*Retrieval-Augmented Generation*). Đến tận Mục 1.2 (dòng 6) mới được giải nghĩa.
  - `1_2_tinh_cap_thiet.tex`, dòng 6: Viết dạng `(RAG -- \textit{Retrieval-Augmented Generation})` là viết ngược.
- **Quy chuẩn đối chiếu:** `Huong-dan-viet-DATN.md` Mục B.III.4 và `AGENTS.md` Mục 2.6.1: *"Nếu cần viết tắt những từ, thuật ngữ... thì được viết tắt sau lần viết thứ nhất có kèm theo chữ viết tắt trong ngoặc đơn"*.
- **Cách sửa chuẩn xác:**
  - Tại Mục 1.1: Viết rõ: *...kết hợp kiến trúc tác nhân tạo sinh tăng cường truy xuất (Agentic RAG -- \textit{Retrieval-Augmented Generation})...*
  - Tại Mục 1.2: Sử dụng thẳng chữ viết tắt `RAG` vì đã được định nghĩa ở Mục 1.1.

### 2.6. Độ dài tiêu đề mục vượt quá giới hạn khuyến nghị
- **Vị trí vi phạm:** `report-datn/chapters/ch1/1_6_bo_cuc.tex`, dòng 2:
  `\section{Bố cục của báo cáo đồ án tốt nghiệp}` (8 từ).
- **Quy chuẩn đối chiếu:** `AGENTS.md` Mục 2.4.3: *"Mọi tiêu đề mục từ cấp 1 đến cấp 4 phải là một cụm danh từ cô đọng từ 3 đến 7 từ, định danh trực diện đối tượng khoa học/kỹ thuật"*.
- **Cách sửa chuẩn xác:** Rút gọn thành `\section{Bố cục báo cáo đồ án}` (5 từ).

### 2.7. Thiếu đoạn văn chuyển ý / mở đầu chương (Bridging Paragraph)
- **Vị trí vi phạm:** `report-datn/chapters/ch1_tong_quan.tex`.
- **Quy chuẩn đối chiếu:** Trong bố cục đồ án tốt nghiệp đại học, sau tiêu đề chương `\chapter{TỔNG QUAN VỀ ĐỀ TÀI}`, không nên nhảy ngay lập tức vào tiêu đề mục `\section{1.1 Giới thiệu đề tài}` mà cần có 1 đoạn văn ngắn (2--3 câu) tóm lược mục đích, phạm vi và cấu trúc phân bổ của Chương 1. Điều này giúp chương mở đầu liền mạch, tự nhiên và đúng chuẩn văn phong Minto Pyramid.
- **Cách sửa chuẩn xác:** Bổ sung một đoạn mở đầu ngắn gọn khoảng 40--50 từ ngay dưới `\label{ch:tong_quan}` trước khi gọi `\input{chapters/ch1/1_1_gioi_thieu}`.

---

## MỤC 3: ĐÁNH GIÁ CHI TIẾT TỪNG HÌNH ẢNH VÀ SƠ ĐỒ TRONG CHƯƠNG 1

### 3.1. Bảng danh mục hiện trạng toàn bộ đối tượng đồ họa trong Chương 1

Qua khảo sát toàn bộ các tệp vi mô trong `report-datn/chapters/ch1/` và đối chiếu với danh mục hình ảnh (`main.lof`) cùng danh mục bảng biểu (`main.lot`):

| STT | Mã Đối Tượng | Loại Đối Tượng | Tiêu Đề / Nội Dung Đối Tượng | Vị Trí Tệp Nguồn | Trang Trong PDF |
| :---: | :---: | :---: | :--- | :--- | :---: |
| 1 | **Bảng 1-1** | Bảng biểu (`table`) | Đối chiếu năng lực kỹ thuật giữa các công cụ hỗ trợ nghiên cứu học thuật hiện có và hệ thống VeriScholar | `chapters/ch1/1_2_tinh_cap_thiet.tex` (dòng 16--33) | Trang 5 |
| *2* | *(Chưa có)* | Sơ đồ (`figure`) | *Chương 1 hiện tại không có bất kỳ hình ảnh hoặc sơ đồ nào (0 hình).* | `chapters/ch1/` | — |

### 3.2. Đánh giá chi tiết Bảng 1-1 (`tab:related_systems_comparison`)
- **Vai trò học thuật:** Bảng 1-1 là cấu phần **bắt buộc và đắt giá nhất** của Chương 1. Bảng này trực tiếp chứng minh tính cấp thiết, phân tích hiện trạng và chỉ ra khoảng trống công nghệ (Research Gap) của 5 nền tảng phổ biến hiện nay (ChatPDF, NotebookLM, Elicit, SciSpace, Overleaf) so với đề tài VeriScholar theo 5 tiêu chuẩn khắt khe.
- **Đánh giá hình thức:**
  - Vị trí `\caption`: Đặt phía trên bảng $\rightarrow$ **ĐÚNG** quy chuẩn HUMG.
  - Cấu trúc bảng: Sử dụng `tabularx{\textwidth}` với các đường kẻ ngang dọc khép kín `|...|` $\rightarrow$ **ĐÚNG** quy cách bảng báo cáo truyền thống.
  - Phông chữ: Sử dụng `\footnotesize` kết hợp căn chỉnh lề cột hợp lý $\rightarrow$ Bảng vừa vặn trong khổ in $15{,}0\,\text{cm}$, không bị tràn lề.
- **Khuyết điểm nội dung:**
  - Ô VeriScholar chứa số liệu IoU mâu thuẫn ($0{,}9266$ so với $0{,}88$ trong `INFORMATION.md`).
  - Tiêu đề cột 3 nhấn mạnh Cross-Encoder thay vì Cổng kiểm chứng CRAG (đóng góp cốt lõi của đề tài).
  - Cách viết `$96\%$` thiếu phần thập phân `$96{,}0\%$`.
  - Macro `\VS\` gây lặp dấu cách.
- **Kiến nghị phân loại:** **GIỮ VÀ SỬA (KEEP & EDIT)**.
  - *Giải trình:* Giữ lại toàn bộ cấu trúc bảng, chỉ hiệu chỉnh văn bản trong 2 ô (tiêu đề cột 3 và ô dữ liệu dòng VeriScholar) để đồng bộ 100% với `INFORMATION.md` và mã nguồn thực tế.

### 3.3. Đánh giá về sự thiếu vắng hình ảnh/sơ đồ và Đề xuất Kiến nghị

#### Hiện trạng:
Toàn bộ Chương 1 dài gần 6 trang in nhưng **hoàn toàn không có hình ảnh hoặc sơ đồ minh họa nào**.

#### Phân tích hai luồng quan điểm:
1. **Quan điểm 1 — Giữ nguyên 0 hình ảnh:**
   - *Ưu điểm:* Tiết kiệm tối đa số trang, bảo đảm nguyên tắc phân bổ vàng (Lý thuyết Chương 1 + 2 $\le 30\%$, Thực hành Chương 3 + 4 $\ge 70\%$). Toàn bộ hình ảnh sơ đồ kiến trúc phức tạp được dồn sang Chương 3 và Chương 4.
   - *Nhược điểm:* Khiến Chương 1 trở thành một "bức tường chữ", người chấm đồ án khó hình dung ngay được tổng thể 4 Không gian làm việc nếu không đọc hết văn bản.
2. **Quan điểm 2 — Bổ sung 1 Sơ đồ ý niệm duy nhất (Conceptual Framework Diagram):**
   - Đề xuất bổ sung **Hình 1-1: Sơ đồ kiến trúc không gian nghiên cứu 4 phân hệ khép kín của VeriScholar** tại Mục 1.1 hoặc Mục 1.3.
   - Sơ đồ này vẽ bằng TikZ chuẩn mực ($\le 15{,}0\,\text{cm}$, scale 0.76, 4 khối hộp màu pastel bo tròn đại diện cho 4 Không gian: *Discovery Space*, *Deep Reading Space*, *Knowledge Library Space*, *Writing Studio Space* nối với nhau theo chu trình vòng đời bài báo).
   - *Ưu điểm:* Tạo ngay ấn tượng thị giác chuyên nghiệp, giải thích trực quan tuyên bố "Hệ thống liên kết xuyên suốt bốn không gian làm việc" ngay tại trang đầu tiên của đồ án.

#### Kết luận kiến nghị về Sơ đồ Hình ảnh cho Chương 1:
- **Đối với hiện trạng:** Không có hình ảnh nào dư thừa cần phải loại bỏ (vì hiện tại có 0 hình).
- **Kiến nghị hành động cụ thể:**
  - **Phương án Ưu tiên A (Bảo toàn số trang tối giản — Khuyến nghị):** Giữ nguyên Chương 1 không cần hình vẽ, tập trung trau chuốt câu từ súc tích và hoàn thiện nội dung Bảng 1-1. Toàn bộ hình ảnh thực tế của 4 Không gian đã được trình bày rất trực quan tại Chương 4 (từ Hình 4-5 đến Hình 4-11).
  - **Phương án B (Nếu GVHD yêu cầu có sơ đồ dẫn nhập):** Chỉ bổ sung duy nhất 1 sơ đồ TikZ khái niệm (Hình 1-1) về Vòng đời 4 Không gian tại Mục 1.1, tuyệt đối không chèn thêm các hình ảnh chụp màn hình hay logo công nghệ rác vào Chương 1.

---

## MỤC 4: KẾ HOẠCH HÀNH ĐỘNG KIẾN NGHỊ TINH GỌN CỤ THỂ CHO CHƯƠNG 1

Dưới đây là Bảng danh mục các hành động sửa đổi cụ thể đề xuất cho các tác tử chế bản (`thesis-writer`, `thesis-formatter`) triển khai:

| TT | Tệp Nguồn Mục Tiêu | Dòng | Nội Dung Hiện Tại | Nội Dung Kiến Nghị Sửa Đổi | Mục Đích / Giải Trình |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 1 | `chapters/ch1_tong_quan.tex` | 6--8 | Nhảy ngay vào `\input{...1_1...}` sau `\label{ch:tong_quan}` | Bổ sung 1 đoạn văn chuyển ý 3 câu dẫn dắt mục tiêu và 4 không gian của Chương 1 | Khắc phục lỗi thiếu đoạn mở đầu chương, hoàn thiện cấu trúc Minto Pyramid |
| 2 | `chapters/ch1/1_1_gioi_thieu.tex` | 4 | `\textit{''Xây dựng nền tảng...''}` | `\textit{``Xây dựng nền tảng...''}` | Sửa lỗi dấu nháy kép ngược trong XeLaTeX |
| 3 | `chapters/ch1/1_1_gioi_thieu.tex` | 6 | `...kiến trúc Agentic RAG...` | `...kiến trúc tác nhân tạo sinh tăng cường truy xuất (Agentic RAG -- \textit{Retrieval-Augmented Generation})...` | Giải nghĩa từ viết tắt lần đầu tiên xuất hiện |
| 4 | `chapters/ch1/1_1_gioi_thieu.tex` | 6 | `...GraphRAG...` | `...GraphRAG \cite{edge2024}...` | Bổ sung trích dẫn học thuật chính thức |
| 5 | `chapters/ch1/1_1_gioi_thieu.tex` | 8 | `Hệ thống \VS\ tập trung...` | `Hệ thống \VS tập trung...` | Loại bỏ dấu gạch chéo thoát cách gây lặp khoảng trắng |
| 6 | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 14 | `...hệ thống \VS\ theo năm...` | `...hệ thống \VS theo năm...` | Loại bỏ dấu gạch chéo thoát cách gây lặp khoảng trắng |
| 7 | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 16 | `\begin{table}[htbp]` | `\begin{table}[!htbp]` | Bổ sung dấu than vị trí float theo quy chuẩn `AGENTS.md` |
| 8 | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 25 | `\textbf{Truy xuất lai Hybrid RRF và Cross-Encoder}` | `\textbf{Truy xuất lai RRF và Cổng kiểm định CRAG}` | Đồng bộ với Đóng góp 1 tại `INFORMATION.md` Mục 2.4 |
| 9 | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `\VS\ (Đề tài)` | `\VS (Đề tài)` | Loại bỏ dấu gạch chéo thoát cách gây lặp khoảng trắng |
| 10 | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `...($\text{IoU} = 0{,}9266$)...` | `...($\text{IoU} \ge 0{,}85$, thực tế $0{,}88$)...` | Khắc phục mâu thuẫn số liệu với SSOT `INFORMATION.md` |
| 11 | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `...Hybrid RRF ($k=60$) kết hợp Cross-Encoder...` | `...Hybrid RRF ($k=60$) kết hợp cổng kiểm chứng CRAG và FlashRank...` | Đồng bộ thuật toán lõi với mã nguồn thực tế |
| 12 | `chapters/ch1/1_2_tinh_cap_thiet.tex` | 31 | `...($96\%$)` | `...($96{,}0\%$)` | Chuẩn hóa số liệu thực nghiệm có 1 chữ số thập phân |
| 13 | `chapters/ch1/1_3_muc_tieu.tex` | 7 | `...phần mềm \VS\ đóng vai trò...` | `...phần mềm \VS đóng vai trò...` | Loại bỏ dấu gạch chéo thoát cách gây lặp khoảng trắng |
| 14 | `chapters/ch1/1_3_muc_tieu.tex` | 13 | `(tiết kiệm tới 98\% dung lượng lưu trữ tệp nhị phân trên máy chủ trong kịch bản 50 học giả cùng nạp một bài báo kinh điển)` | Xóa bỏ cụm từ suy diễn này | Loại bỏ số liệu phỏng đoán lý thuyết chưa qua kiểm chứng thực nghiệm |
| 15 | `chapters/ch1/1_3_muc_tieu.tex` | 14 | `...HNSW Cosine 1536 chiều...` | `...HNSW Cosine 1536 chiều \cite{malkov2018}...` | Bổ sung trích dẫn công trình Malkov & Yashunin (2018) |
| 16 | `chapters/ch1/1_3_muc_tieu.tex` | 14 | `...kết hợp tái chấm điểm Okapi BM25...` | `...với hàm xếp hạng mật độ bao phủ \texttt{ts\_rank\_cd}...` | Sửa đúng thực tế cài đặt PostgreSQL FTS trong mã nguồn |
| 17 | `chapters/ch1/1_3_muc_tieu.tex` | 14 | `...$\text{IoU} \ge 0{,}85$ (thực nghiệm đạt $0{,}9266 \pm 0{,}0126$)...` | `...ngưỡng độ trùng khớp tọa độ $\text{IoU} \ge 0{,}85$...` | Đưa kết quả thực nghiệm ra khỏi phần mục tiêu |
| 18 | `chapters/ch1/1_3_muc_tieu.tex` | 15 | `...GraphRAG...` | `...GraphRAG \cite{edge2024}...` | Bổ sung trích dẫn công trình Edge et al. (2024) |
| 19 | `chapters/ch1/1_3_muc_tieu.tex` | 16 | `...trên 90\% (thực nghiệm đạt $96\%$ trên tập 25 ca kiểm thử lỗi chuẩn)...` | `...ngưỡng tỷ lệ tự phục hồi thành công trên 90\%...` | Đưa kết quả thực nghiệm ra khỏi phần mục tiêu |
| 20 | `chapters/ch1/1_4_noi_dung.tex` | 9 | `...kiến trúc lục giác...` | `...kiến trúc lục giác \cite{cockburn2005}...` | Bổ sung trích dẫn Alistair Cockburn (2005) |
| 21 | `chapters/ch1/1_4_noi_dung.tex` | 10 | `...hợp nhất xếp hạng đảo ngược RRF...` | `...hợp nhất xếp hạng đảo ngược RRF \cite{cormack2009}...` | Bổ sung trích dẫn Cormack et al. (2009) |
| 22 | `chapters/ch1/1_4_noi_dung.tex` | 12 | `...tác nhân ReAct...` | `...tác nhân ReAct \cite{yao2022}...` | Bổ sung trích dẫn Yao et al. (2022) |
| 23 | `chapters/ch1/1_4_noi_dung.tex` | 13 | `...AES-256-GCM với nguyên tắc Zero-Retention trên bộ nhớ RAM` | `...AES-256-GCM \cite{dworkin2007}, không lưu trữ khóa bản rõ và chỉ giải mã tạm thời trong bộ nhớ tiến trình` | Thay thế buzzword thương mại và bổ sung trích dẫn NIST SP 800-38D |
| 24 | `chapters/ch1/1_4_noi_dung.tex` | 18 | `...qua 4 cổng kiểm định tự động bắt buộc trước khi phát hành` | `...thông qua hệ thống kiểm thử tự động toàn diện từ kiểm tra tĩnh đến kiểm thử hồi quy` | Thay thế thuật ngữ nội bộ harness bằng ngôn từ học thuật |
| 25 | `chapters/ch1/1_6_bo_cuc.tex` | 2 | `\section{Bố cục của báo cáo đồ án tốt nghiệp}` | `\section{Bố cục báo cáo đồ án}` | Rút gọn tiêu đề đạt chuẩn 5 từ (khuyến nghị 3--7 từ) |
| 26 | `chapters/ch1/1_6_bo_cuc.tex` | 7 | Liệt kê dày đặc hàng chục công nghệ nền tảng | Tinh gọn bớt các tên thư viện phụ, tập trung vào 4 trụ cột kiến trúc cốt lõi | Tránh cảm giác loãng nội dung tóm tắt chương |

---

## KẾT LUẬN VÀ ĐÁNH GIÁ MỨC ĐỘ SẴN SÀNG

1. **Về mặt khối lượng và cấu trúc:** Chương 1 đã xây dựng được khung xương vững chắc, bao hàm đầy đủ 6 nội dung cơ bản theo đúng cấu trúc đề cương ĐATN của Khoa CNTT — HUMG (Giới thiệu, Tính cấp thiết, Mục tiêu, Nội dung, Phạm vi, Bố cục).
2. **Về mặt tính xác thực và khoa học:** Cần thực hiện ngay 26 điểm hiệu chỉnh nêu tại Mục 4, đặc biệt là **khóa cứng số liệu IoU ($0{,}88$)**, loại bỏ số liệu phỏng đoán 98%, xóa bỏ việc đưa trước kết quả đo lường vào mục tiêu, và bổ sung các mã trích dẫn nền tảng `\cite{...}`.
3. **Về mặt hình ảnh sơ đồ:** Chương 1 hiện tại sạch sẽ, không có hình rác. Khuyến nghị giữ nguyên giải pháp tập trung vào Bảng 1-1 tinh gọn chất lượng cao để bảo đảm tỷ lệ phân bổ nội dung vàng ($\le 8$ trang cho toàn bộ Chương 1).
