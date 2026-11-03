# BÁO CÁO RÀ SOÁT VÀ ĐÁNH GIÁ ĐỘC LẬP CHƯƠNG 4
# CÀI ĐẶT VÀ KẾT QUẢ THỰC NGHIỆM (CHAPTER 4 REVIEW REPORT)

> **Dự án:** Nền tảng Trợ lý AI Nghiên cứu Khoa học VeriScholar  
> **Người thực hiện rà soát:** Chuyên gia Đánh giá Báo cáo Đồ án Tốt nghiệp (Chapter 4 Independent Reviewer)  
> **Tài liệu đối soát quy chuẩn:**  
> - `report-datn/AGENTS.md` (Cẩm nang quy chuẩn biên soạn & SOP học thuật)  
> - `report-datn/INFORMATION.md` (Hồ sơ đề tài, tham số định lượng & Benchmarks khóa cứng)  
> - `report-datn/guide/` (4 tài liệu hướng dẫn và quy định của Khoa CNTT — Trường Đại học Mỏ - Địa chất)  
> - Thực tế mã nguồn: `apps/web/`, `apps/api/`, `packages/core/`, `tests/`, `docs/benchmarks/thesis_benchmark_results.json`  
> **Phạm vi rà soát:** Toàn bộ các tệp nguồn tại `report-datn/chapters/ch4/` (`4_1_moi_truong.tex`, `4_2_giao_dien.tex`, `4_3_kiem_thu.tex`, `4_4_so_lieu.tex`) và tệp điều phối `report-datn/chapters/ch4_thuc_nghiem.tex`.

---

## TỔNG QUAN HIỆN TRẠNG CHƯƠNG 4

| Tiêu chí | Quy định chuẩn (AGENTS.md & HUMG) | Hiện trạng thực tế tại Chương 4 | Đánh giá |
| :--- | :--- | :--- | :--- |
| **Quy mô số trang (Page Budget)** | **12 -- 16 trang** (chiếm ~26% thân bài) | **23 trang** (từ trang 71 đến trang 93 trong `main.pdf`) | ❌ **VƯỢT NGÂN SÁCH 43%** (quá tải do nhồi nhét 16 hình ảnh) |
| **Số lượng đề mục Section cấp 1** | Đúng 4 mục: 4.1, 4.2, 4.3, 4.4 (theo `ROADMAP.md`) | Chỉ có 2 mục cấp 1: `4.1` và `4.2` (4.3 và 4.4 bị biến thành `4.2.2`, `4.2.3`, `4.2.4`) | ❌ **SAI CẤU TRÚC PHÂN CẤP** |
| **Độ sâu phân cấp tối đa** | Tối đa 4 cấp (`X.Y.Z.W`) | Tồn tại cấp 5: `\paragraph` sinh ra `4.1.3.0.1` đến `4.1.3.0.4` | ❌ **VI PHẠM QUY CHẾ HUMG** |
| **Số lượng hình ảnh/sơ đồ** | 6 -- 8 hình ảnh chọn lọc chất lượng cao | 16 hình ảnh (1 sơ đồ TikZ + 10 ảnh UI + 5 ảnh monitoring) | ❌ **DƯ THỪA 100% HÌNH ẢNH** |
| **Số lượng bảng biểu** | 3 -- 4 bảng theo chuẩn `tabularx` | 4 bảng (`tab:monorepo_structure`, `tab:gate_results`, `tab:ablation_retrieval`, `tab:ablation_latex_healing`) | ⚠️ **CẢ 4 BẢNG DÙNG `tabular` CỐ ĐỊNH, DÙNG `[H]`** |
| **Trích dẫn khoa học (`\cite`)** | Phải trích dẫn các công trình/công nghệ nền tảng | **0 trích dẫn** trong toàn bộ 4 tệp của Chương 4 | ❌ **THIẾU SÓT LIÊN KẾT HỌC THUẬT** |
| **Tính xác thực của hình ảnh** | Khớp 100% với mô tả và tính năng hệ thống | • `deep_read_paper.png` KHÔNG CÓ Bounding Box viền vàng.<br>• `azure_monitor.png` dính popup lỗi "No data returned". | ❌ **SAI SỰ THẬT / ẢO GIÁC HÌNH ẢNH** |

---

## PHẦN 1: NỘI DUNG DƯ THỪA, KHÔNG CẦN THIẾT VÀ SAI SỰ THẬT CẦN TINH GỌN

### 1.1. Nội dung hướng dẫn cài đặt mang tính cẩm nang kỹ thuật (Manual/Tutorial Filler)
- **Vị trí vi phạm:** `report-datn/chapters/ch4/4_1_moi_truong.tex`, dòng 7--25 (`\subsection{Cài đặt Visual Studio Code và môi trường phát triển}`).
- **Chi tiết nội dung vi phạm:** Đoạn văn dành gần 1 trang để mô tả:
  + Cách *"Tải và cài đặt phiên bản Visual Studio Code mới nhất từ trang chủ chính thức https://code.visualstudio.com/"*.
  + Cách cài đặt công cụ Python `uv venv`, `uv sync`.
  + Cách cài đặt Node.js 22 LTS và chạy `npm install`.
  + Liệt kê các extension VS Code: Ruff, Tailwind CSS IntelliSense, ESLint, Python Test Explorer, LaTeX Workshop.
- **Hệ quả học thuật:** Đây là vi phạm nghiêm trọng Anti-Pattern **AP-01** (Wikipedia / Textbook Dump) được quy định rõ tại Mục 3.2 và 3.3 của `AGENTS.md`: *Chương 4 cấm đưa hướng dẫn cài đặt môi trường lập trình kiểu cẩm nang người dùng (`uv run dev`, `.env`, `npm install`)*. Đồ án đại học ngành CNTT không phải là tài liệu hướng dẫn cài đặt phần mềm cho người mới bắt đầu.
- **Kiến nghị tinh gọn:**
  + Loại bỏ hoàn toàn đoạn văn hướng dẫn tải VS Code từ trang web, các lệnh `uv venv`, `npm install`.
  + Gộp và nâng tầm thành 1 đoạn văn súc tích (khoảng 15 dòng) định danh kiến trúc môi trường thực nghiệm: Công nghệ ngôn ngữ (Python 3.12, TypeScript), các thành phần dịch vụ chính, và liên kết kho mã nguồn.

### 1.2. Trùng lặp cấu trúc Monorepo và Kiến trúc Lục giác giữa Chương 4 và Chương 3
- **Vị trí vi phạm:** `report-datn/chapters/ch4/4_1_moi_truong.tex`, dòng 37--54 (Bảng 4.1: `\label{tab:monorepo_structure}`).
- **Chi tiết nội dung vi phạm:** Bảng 4.1 mô tả 3 phân vùng Monorepo (`packages/core`, `apps/api`, `apps/web`) và quy tắc ranh giới Ports/Adapters. Toàn bộ nội dung này đã được trình bày chi tiết tại Chương 2 (Mục 2.2 về Kiến trúc Lục giác) và Chương 3 (Mục 3.3 về Thiết kế Kiến trúc hệ thống).
- **Hệ quả học thuật:** Tạo sự trùng lặp vô ích trong báo cáo, làm phân tán trọng tâm của Chương 4 (vốn phải tập trung vào kết quả đo lường và triển khai).
- **Kiến nghị tinh gọn:** Tinh giản Bảng 4.1, chỉ giữ lại bảng ma trận cấu hình môi trường máy chủ và dịch vụ triển khai thực tế (PostgreSQL 16, pgvector, Redis, E2B, VPS Azure).

### 1.3. Lặp lại đường dẫn URL kho lưu trữ GitHub nhiều lần
- **Vị trí vi phạm:**
  + `4_1_moi_truong.tex` dòng 15: `\url{https://github.com/dammanhdungvn/VeriScholar}`
  + `4_1_moi_truong.tex` dòng 81: `\url{https://github.com/dammanhdungvn/VeriScholar}`
  + `4_4_so_lieu.tex` dòng 181: `\url{https://github.com/dammanhdungvn/VeriScholar}`
- **Kiến nghị tinh gọn:** Chỉ giữ lại 1 lần duy nhất tại mục Giới thiệu môi trường hoặc Thông tin triển khai.

### 1.4. Nhồi nhét ảnh chụp màn hình các trang phụ không mang giá trị khoa học
- **Vị trí vi phạm:** `report-datn/chapters/ch4/4_2_giao_dien.tex`:
  + Mục 4.2.1.1 & Hình 4.2 (`fig:ui_register`, `register.png`): Giao diện Đăng ký tài khoản (chiếm trọn trang 77).
  + Mục 4.2.1.2 & Hình 4.3 (`fig:ui_login`, `login.png`): Giao diện Đăng nhập hệ thống (chiếm trọn trang 78).
  + Mục 4.2.1.3 & Hình 4.4 (`fig:ui_dashboard`, `dashboard.png`): Bảng điều khiển trung tâm (chiếm trọn trang 79).
- **Phân tích kỹ thuật:**
  + Cả hai hình `register.png` và `login.png` là biểu mẫu xác thực tiêu chuẩn (form nhỏ ở giữa màn hình đen 1920x964, chiếm tới 80% diện tích là nền tối trống trơn). Màn hình đăng nhập/đăng ký không mang bất kỳ giá trị nghiên cứu hay đóng góp khoa học nào của đề tài về Agentic RAG và Bounding Box.
  + Hình `dashboard.png` là một màn hình làm việc trống chỉ có thanh tìm kiếm, hoàn toàn trùng lặp với Hình 4.5 (`search_paper.png`).
  + Việc đưa 3 màn hình phụ này tiêu tốn tới **4 trang in** trong báo cáo!
- **Kiến nghị tinh gọn:** **LOẠI BỎ HOÀN TOÀN** 3 hình `fig:ui_register`, `fig:ui_login`, `fig:ui_dashboard` (và các tiểu mục tương ứng). Nếu muốn thể hiện luồng xác thực, chỉ cần 1 câu văn nêu rõ hệ thống xác thực phân tán qua JWT cookie an toàn.

### 1.5. Sai sự thật và Mâu thuẫn giữa Hình ảnh và Lời văn (Visual Discrepancy & Hallucination)
- **Vấn đề 1 — Mâu thuẫn nghiêm trọng tại Hình 4.8 (`deep_read_paper.png`):**
  + *Lời văn và Caption khẳng định (dòng 211--224):* "Giao diện đọc sâu tài liệu PDF hai cột và Bounding Box viền vàng", "kích hoạt lớp phủ đồ họa vẽ khung viền vàng bao quanh đoạn trích gốc", "đạt chỉ số chồng lấn thực nghiệm trung bình IoU = 0,9266".
  + *Thực tế hình ảnh `figures/frontend/deep_read_paper.png`:* Khung PDF Canvas bên trái hiển thị trang 2 của bài báo *Attention Is All You Need* **HOÀN TOÀN KHÔNG CÓ BẤT KỲ KHUNG VIỀN VÀNG HAY BOUNDING BOX NÀO!**
  + *Hệ quả:* Đây là lỗi sai sự thật mang tính liêm chính học thuật. Khi Hội đồng phản biện lật đến trang này, họ sẽ lập tức nhận ra hình ảnh không hề có Bounding Box như tác giả mô tả trong văn bản.
  + *Kiến nghị:* Bắt buộc phải **CHỤP LẠI HÌNH ẢNH MỚI** cho `deep_read_paper.png` khi hệ thống đang kích hoạt Bounding Box màu vàng viền quanh đoạn trích trên canvas PDF (hoặc nếu chưa chụp lại được, phải sửa caption và giải trình rõ là hình ảnh trạng thái chờ kích hoạt).
- **Vấn đề 2 — Ảnh chụp lỗi kỹ thuật tại Hình 4.13 (`monitor_azure.png`):**
  + *Lời văn khẳng định (dòng 111--117):* "Chỉ số sẵn sàng vận hành (Availability): Đạt mức 100% liên tục... CPU Utilization dao động ổn định ở mức dưới 1%... Top 5 processes...".
  + *Thực tế hình ảnh `figures/frontend/azure_monitor.png`:* Ngay chính giữa biểu đồ CPU và Top 5 processes dính một popup cảnh báo màu xanh của Azure: **"No data returned matching the selected filters"**! Đường biểu đồ Availability bị đứt gãy và chỉ vọt lên ở góc cuối.
  + *Hệ quả:* Thể hiện việc thu thập số liệu thực nghiệm chưa cẩn trọng; ảnh chụp màn hình ghi nhận trạng thái lỗi bộ lọc dữ liệu nhưng lại được dán vào báo cáo chính thức.
  + *Kiến nghị:* Loại bỏ hình này hoặc chụp lại biểu đồ Azure Monitor khi đã chọn đúng phạm vi thời gian có dữ liệu đo lường liên tục.
- **Vấn đề 3 — Chênh lệch gây hiểu lầm giữa OpenAI Usage và Langfuse Dashboard:**
  + Hình 4.15 (`openai_usage.png`) báo cáo tổng chi phí **$3.76** cho 78,25 triệu tokens trong cả tháng 10/2026.
  + Hình 4.16 (`langfuse_dashboard.jpg`) báo cáo chi phí **$0.00104** cho 110 traces trong 24 giờ.
  + Mặc dù văn bản có giải thích sự khác biệt giữa lũy kế tháng và phiên 24h, nhưng việc dành tới 4 hình ảnh giám sát (`langfuse_tracing.jpg`, `azure_monitor.png`, `exa_usage.png`, `openai_usage.png`, `langfuse_dashboard.jpg`) chiếm tới 5 trang in ở cuối Chương 4 là quá nặng nề và làm loãng phần số liệu thuật toán RAG/LaTeX healing.

### 1.6. Sự không nhất quán về số lượng bài kiểm thử tự động
- **Đối soát giữa các nguồn:**
  + `INFORMATION.md` (Mục 5.1): *"Tổng số bài kiểm thử tự động đã vượt qua: Đúng 580 unit & integration tests"*.
  + `tests/test_thesis_structure_and_compile.py` (dòng 220): *"340 pytest, 240 vitest (tổng 580 test)"*.
  + `4_3_kiem_thu.tex` (dòng 8, 9, 27, 28, 33): *"349 bài kiểm thử pytest và 240 bài vitest, tổng cộng 589 bài kiểm thử tự động, vượt mục tiêu cam kết >= 580 bài"*.
  + Kiểm tra thực tế trong repository:
    * `uv run pytest --collect-only`: Thu thập được **358 tests**.
    * `npm --prefix apps/web run test`: Thu thập được **240 tests**.
    * Tổng số test thực tế hiện tại là: **598 tests**!
- **Hệ quả:** Báo cáo ghi 589 tests, INFORMATION.md ghi 580 tests, test hồi quy ghi 580 (340+240), trong khi thực tế code hiện tại là 598 tests.
- **Kiến nghị:** Thống nhất cách diễn đạt chuẩn xác: *"Hệ thống xây dựng bộ kiểm thử vượt chỉ tiêu cam kết ban đầu (đạt 589/580 bài kiểm thử tại thời điểm đóng băng số liệu báo cáo, và hiện đạt 598 bài kiểm thử toàn diện trên Monorepo)"*, đồng thời cập nhật đồng bộ số liệu vào `INFORMATION.md` và `tests/test_thesis_structure_and_compile.py`.

---

## PHẦN 2: LỖI FORMAT VÀ VI PHẠM QUY CHUẨN (AGENTS.MD, INFORMATION.MD, GUIDE/)

### 2.1. Lỗi phân cấp cấu trúc đề mục (Severe Heading Hierarchy Flaws)

#### Lỗi 1: Tệp `4_3_kiem_thu.tex` và `4_4_so_lieu.tex` bị mất cấp `\section`
- **Thực trạng:** 
  + Trong `report-datn/chapters/ch4_thuc_nghiem.tex`, 4 tệp vi mô được include tuần tự:
    ```latex
    \input{chapters/ch4/4_1_moi_truong}
    \input{chapters/ch4/4_2_giao_dien}
    \input{chapters/ch4/4_3_kiem_thu}
    \input{chapters/ch4/4_4_so_lieu}
    ```
  + `4_1_moi_truong.tex` mở đầu bằng: `\section{Môi trường thực nghiệm}` $\rightarrow$ Trở thành **Mục 4.1**.
  + `4_2_giao_dien.tex` mở đầu bằng: `\section{Kết quả thực nghiệm}` $\rightarrow$ Trở thành **Mục 4.2**.
  + **Tuy nhiên, `4_3_kiem_thu.tex` KHÔNG CÓ LỆNH `\section`!** Tệp này mở đầu ngay bằng:
    `\subsection{Xây dựng kịch bản kiểm thử tự động hệ thống qua 4 cổng xác minh}`. Do đó, trong XeLaTeX, nó bị đánh số thành **Mục 4.2.2** (nằm dưới Mục 4.2 của file giao diện)!
  + **Tương tự, `4_4_so_lieu.tex` KHÔNG CÓ LỆNH `\section`!** Tệp này mở đầu bằng:
    `\subsection{Đánh giá số liệu thực nghiệm định lượng...}` $\rightarrow$ Bị đánh số thành **Mục 4.2.3**! Và `\subsection{Hệ thống giám sát vận hành...}` bị đánh số thành **Mục 4.2.4**!
- **Hệ quả nghiêm trọng:** 
  + Trong Mục lục (`main.toc`), **HOÀN TOÀN KHÔNG CÓ MỤC 4.3 VÀ MỤC 4.4!**
  + Toàn bộ nội dung Kiểm thử tự động, Số liệu đo lường định lượng và Giám sát hệ thống đều bị biến thành các mục con của "Mục 4.2: Kết quả thực nghiệm"!
  + Điều này mâu thuẫn trực tiếp với `report-datn/ROADMAP.md` (Mục 2, dòng 77--80 quy định 4 mục độc lập: 4.1 Môi trường, 4.2 Giao diện, 4.3 Kiểm thử, 4.4 Số liệu).
- **Kiến nghị sửa đổi:**
  + Sửa tiêu đề `4_2_giao_dien.tex` thành: `\section{Giao diện các phân hệ chính của hệ thống}` (Mục 4.2).
  + Thêm `\section{Kết quả kiểm thử tự động qua bốn cổng xác minh}` vào đầu `4_3_kiem_thu.tex` (Mục 4.3).
  + Thêm `\section{Đánh giá thực nghiệm định lượng và hiệu năng hệ thống}` vào đầu `4_4_so_lieu.tex` (Mục 4.4).

#### Lỗi 2: Sinh đề mục cấp 5 vi phạm quy chế HUMG
- **Thực trạng:** Tại `4_1_moi_truong.tex` (dòng 61, 68, 74, 79), tác giả sử dụng lệnh:
  ```latex
  \paragraph{Cấu hình máy chủ ảo VPS và tên miền công cộng:}
  \paragraph{Môi trường thực thi Sandbox đám mây E2B MicroVM:}
  \paragraph{Nền tảng quan sát và kiểm chứng thực nghiệm Langfuse Cloud:}
  \paragraph{Kho lưu trữ mã nguồn mở dự án trên GitHub:}
  ```
- **Hệ quả trong XeLaTeX:** Do `\paragraph` nằm dưới `\subsection{4.1.3}`, trình biên dịch đã đánh số đề mục thành **5 cấp số**: `4.1.3.0.1`, `4.1.3.0.2`, `4.1.3.0.3`, `4.1.3.0.4` (ghi nhận rõ trong `main.toc` dòng 108--111).
- **Quy chuẩn đối soát:** 
  + `Huong-dan-viet-DATN.md` (Mục III.2): *"Các tiểu mục của đồ án được trình bày và đánh số thành nhóm số, nhiều nhất gồm bốn chữ số với số thứ nhất chỉ số chương (ví dụ 4.1.2.1...)"*.
  + `AGENTS.md` (Mục 2.4.1): *"Độ sâu phân cấp tối đa 4 cấp... Tuyệt đối không đánh số cấp thứ 5 (như 3.1.2.1.1)"*.
- **Kiến nghị sửa đổi:** Chuyển đổi toàn bộ các `\paragraph` này thành danh sách `\begin{itemize}` gạch đầu dòng, hoặc in nghiêng đầu đoạn không đánh số, bỏ dấu hai chấm `:` ở tiêu đề.

#### Lỗi 3: Tiêu đề không chuẩn học thuật và Lỗi Singleton Subsection
- **Tiêu đề `4.2.1: Một số giao diện của hệ thống`:** Vi phạm quy chuẩn danh ngữ hóa cô đọng (3-7 từ). Từ "Một số..." mang tính liệt kê đại khái, không đạt chuẩn học thuật.
- **Lỗi Singleton Subsection:** Trong `4_2_giao_dien.tex`, sau `\subsection{4.2.1}` không có `\subsection{4.2.2}` nào khác trong cùng tệp. Theo quy tắc *No Singleton Subsection* (`AGENTS.md` Mục 2.4.2), không thể có `4.2.1` mà không có `4.2.2`. (Thực tế `4.2.2` hiện tại chỉ xuất hiện do file `4_3_kiem_thu.tex` bị mất `\section` ghép vào).
- **Mục `Nhận xét` ở cuối chương (dòng 176 `4_4_so_lieu.tex`):** Sử dụng `\subsection*{Nhận xét:}` kèm `\addcontentsline{toc}{subsection}{Nhận xét}` có dấu hai chấm `:`, khiến anchor trong mục lục nhảy vào `figure.caption.94`. Cần chuẩn hóa thành một mục thảo luận/đánh giá chuẩn.

### 2.2. Lỗi cấu hình đối tượng trôi nổi (Floats Placement Invariant)
- **Quy chuẩn đối soát:** `AGENTS.md` (Mục 2.2.4 & Checklist #8):
  *"Tất cả các đối tượng trôi nổi (Floats: Bảng biểu và Hình vẽ) bắt buộc phải khai báo tham số vị trí linh hoạt: `\begin{table}[!htbp]` và `\begin{figure}[!htbp]`. Tuyệt đối không dùng `[H]` cưỡng bức gây khoảng trống lớn đáy trang."*
- **Thực tế vi phạm trong Chương 4:**
  + `4_1_moi_truong.tex` dòng 39: `\begin{table}[H]` $\rightarrow$ **SAI**.
  + `4_2_giao_dien.tex` dòng 17: `\begin{figure}[H]` $\rightarrow$ **SAI**.
  + `4_2_giao_dien.tex` dòng 121, 134, 153, 172, 185, 203, 221, 234, 251, 269: Dùng `\begin{figure}[htbp]` (thiếu dấu than `!`).
  + `4_3_kiem_thu.tex` dòng 15: `\begin{table}[H]` $\rightarrow$ **SAI**.
  + `4_4_so_lieu.tex` dòng 27: `\begin{table}[H]` $\rightarrow$ **SAI**.
  + `4_4_so_lieu.tex` dòng 46: `\begin{table}[H]` $\rightarrow$ **SAI**.
  + `4_4_so_lieu.tex` dòng 87, 104, 124, 143, 162: `\begin{figure}[H]` $\rightarrow$ **SAI**.
- **Hệ quả:** Dùng `[H]` khiến XeLaTeX không thể linh hoạt đẩy nội dung lấp đầy trang, tạo ra các khoảng trống lớn bất thường (Bottom Gaps) ở chân trang giấy, đặc biệt tại các trang có hình ảnh lớn 1024x558.

### 2.3. Lỗi kỹ nghệ bảng biểu (Tabular vs Tabularx Invariant)
- **Quy chuẩn đối soát:** `AGENTS.md` (Mục 2.5.4 & AP-07):
  *"Mọi bảng có chứa nội dung văn bản dài... bắt buộc phải sử dụng môi trường `tabularx` với độ rộng đúng bằng `\textwidth` (`\begin{tabularx}{\textwidth}{|...|}`). Sử dụng cột loại `X` để bảng tự động ngắt dòng chữ, tuyệt đối không dùng cột `l` hay `p{...}` cố định khiến bảng bị lệch hoặc đâm thủng lề 15,0cm."*
- **Thực tế vi phạm:** Cả 4 bảng biểu trong Chương 4 đều sử dụng `tabular` với cột `p{...}` thủ công:
  + Bảng 4.1 (`tab:monorepo_structure`): `\begin{tabular}{|c|>{\raggedright\arraybackslash}p{2.9cm}|...}`
  + Bảng 4.2 (`tab:gate_results`): `\begin{tabular}{|c|>{\raggedright\arraybackslash}p{2.2cm}|...}`
  + Bảng 4.3 (`tab:ablation_retrieval`): `\begin{tabular}{|>{\raggedright\arraybackslash}p{3.4cm}|c|c|c|c|c|}`
  + Bảng 4.4 (`tab:ablation_latex_healing`): `\begin{tabular}{|>{\raggedright\arraybackslash}p{4.8cm}|c|c|c|}`
- **Kiến nghị sửa đổi:** Chuyển toàn bộ 4 bảng sang `\begin{tabularx}{\textwidth}{|...|}` kết hợp cột `X` hoặc `>{\raggedright\arraybackslash}X`.

### 2.4. Lỗi tràn lề văn bản (Overfull \hbox)
Khi biên dịch XeLaTeX, Chương 4 ghi nhận 5 cảnh báo Overfull \hbox (vượt quá lề phải khả dụng 15,0cm):
1. `4_1_moi_truong.tex` dòng 13--14: `Overfull \hbox (5.38562pt too wide)` do chuỗi mã `(packages/core, apps/api, apps/web)`.
2. `4_1_moi_truong.tex` dòng 32--33: `Overfull \hbox (15.59056pt too wide)` do không thể ngắt dòng ở cụm từ kỹ thuật dài.
3. `4_1_moi_truong.tex` dòng 64--65: `Overfull \hbox (5.76437pt too wide)` do liên kết URL dài `https://verischolar.duckdns.org`.
4. `4_1_moi_truong.tex` dòng 65--66: `Overfull \hbox (8.88531pt too wide)` do cụm từ gạch nối dài `đầu–cuối bằng chứng chỉ số SSL/TLS`.
5. `4_2_giao_dien.tex` dòng 167--168: `Overfull \hbox (9.69147pt too wide)` do cụm từ in nghiêng `Đã bình duyệt (Peer-Reviewed)`.
- **Kiến nghị:** Thêm lệnh `\allowbreak` hoặc bọc trong `\sloppy` để ngắt dòng mềm mại.

### 2.5. Hoàn toàn vắng bóng trích dẫn học thuật (`\cite`)
- **Thực trạng:** Trong toàn bộ 4 tệp của Chương 4, số lượng lệnh `\cite` bằng **0**.
- **Quy chuẩn đối soát:** `AGENTS.md` Mục 2.6 và Mục 3.1: Mọi công trình và công nghệ có trong danh mục 20 tài liệu tham khảo chính thức tại `INFORMATION.md` phải được trích dẫn phù hợp khi nhắc đến.
- **Các vị trí cần bổ sung `\cite`:**
  + Khi nhắc đến nền tảng MicroVM Firecracker / E2B: Cần trích dẫn `\cite{agache2020firecracker}` (Agache et al., NSDI '20).
  + Khi nhắc đến thuật toán RRF ($k=60$): Cần trích dẫn `\cite{cormack2009reciprocal}` (Cormack et al., SIGIR '09).
  + Khi nhắc đến chỉ mục HNSW trên pgvector: Cần trích dẫn `\cite{malkov2018hnsw}` (Malkov & Yashunin, IEEE TPAMI '18).
  + Khi nhắc đến bộ xếp hạng Okapi BM25: Cần trích dẫn `\cite{robertson1995okapi}` (Robertson et al., TREC-3).
  + Khi nhắc đến chu trình ReAct / Reflexion: Cần trích dẫn `\cite{shinn2023reflexion}` và công trình ReAct của Yao et al.
  + Khi nhắc đến phân cụm cộng đồng Louvain: Cần trích dẫn `\cite{blondel2008louvain}` (Blondel et al., 2008).
  + Khi nhắc đến GraphRAG: Cần trích dẫn `\cite{edge2024graphrag}` (Edge et al., 2024).
  + Khi nhắc đến mã hóa xác thực AES-256-GCM: Cần trích dẫn `\cite{dworkin2007gcm}` (NIST SP 800-38D).

---

## PHẦN 3: ĐÁNH GIÁ CHI TIẾT TỪNG HÌNH ẢNH / SƠ ĐỒ TRONG CHƯƠNG 4

Dưới đây là Bảng danh mục và phân tích chuyên sâu toàn bộ 16 hình ảnh, sơ đồ trong Chương 4:

| STT | Mã Nhãn (`\label`) | Tệp nguồn hình ảnh | Độ phân giải & Tỷ lệ | Vị trí trang hiện tại | Đánh giá giá trị kỹ thuật & Tính xác thực | Kiến nghị cụ thể |
| :---: | :--- | :--- | :---: | :---: | :--- | :---: |
| 1 | `fig:ui_layout_architecture` | TikZ vector code | Vector tỷ lệ linh hoạt | Trang 76 | **Giá trị khoa học rất cao.** Sơ đồ TikZ mô hình hóa mạch lạc 4 phân hệ tương tác, luồng dữ liệu hai chiều và các cơ chế cốt lõi (CAS, BBox, ReAct, BYOK). Tuân thủ 7 nguyên tắc vàng TikZ. | **GIỮ NGUYÊN** |
| 2 | `fig:ui_register` | `figures/frontend/register.png` | 1920x964 (~2:1) | Trang 77 | **Không có giá trị khoa học.** Màn hình form đăng ký chuẩn, 80% là khoảng tối trống trơn. Chiếm trọn 1 trang in vô ích. | **LOẠI BỎ (BỎ)** |
| 3 | `fig:ui_login` | `figures/frontend/login.png` | 1920x964 (~2:1) | Trang 78 | **Không có giá trị khoa học.** Form đăng nhập chuẩn, hoàn toàn tương tự form đăng ký, chiếm thêm 1 trang in. | **LOẠI BỎ (BỎ)** |
| 4 | `fig:ui_dashboard` | `figures/frontend/dashboard.png` | 1920x964 (~2:1) | Trang 79 | **Trùng lặp.** Màn hình dashboard rỗng chỉ có thanh tìm kiếm, không thể hiện thêm tính năng nghiệp vụ nào ngoài việc làm nền cho tìm kiếm. | **LOẠI BỎ (BỎ)** |
| 5 | `fig:ui_search_paper` | `figures/frontend/search_paper.png` | 1920x964 (~2:1) | Trang 80 | **Giá trị thực tiễn tốt.** Thể hiện kết quả tìm kiếm đa nguồn, nút lọc "Đã bình duyệt", thẻ bài báo chống tràn và nút "Mở Đọc Sâu". | **GIỮ** (Thu hẹp crop vừa khít khung thẻ) |
| 6 | `fig:ui_reference_search` | `figures/frontend/reference_search.png` | 1920x964 (~2:1) | Trang 81 | **Giá trị học thuật tốt.** Thể hiện tính năng phân giải và đối chiếu 40 tài liệu tham khảo trích xuất từ PDF qua DOI/CrossRef. | **GIỮ** |
| 7 | `fig:ui_my_library` | `figures/frontend/my_library.png` | 1920x964 (~2:1) | Trang 81 | **Giá trị thực tiễn tốt.** Minh chứng tính năng quản lý thư mục, lưu trữ CAS SHA-256 khử trùng lặp và danh sách bài báo cá nhân. | **GIỮ** |
| 8 | `fig:ui_deep_read_paper` | `figures/frontend/deep_read_paper.png` | 1920x964 (~2:1) | Trang 82 | **Trọng tâm đề tài nhưng ẢNH BỊ SAI SỰ THẬT:** Phần PDF bên trái không hề có Bounding Box viền vàng như lời văn và caption khẳng định. Cần thiết phải có Bounding Box trực quan. | **SỬA (BẮT BUỘC CHỤP LẠI)** |
| 9 | `fig:ui_graph` | `figures/frontend/graph.png` | 1920x964 (~2:1) | Trang 83 | **Giá trị khoa học xuất sắc.** Trực quan hóa mạng đồ thị tri thức 4 thực thể (58 đỉnh, 111 liên kết) và phân cụm Louvain. | **GIỮ NGUYÊN** |
| 10 | `fig:ui_byok` | `figures/frontend/byok.png` | 1920x964 (~2:1) | Trang 84 | **Giá trị thực tiễn tốt.** Minh chứng tính năng bảo mật két sắt BYOK AES-256-GCM và liên kết ORCID tích xanh. | **GIỮ** |
| 11 | `fig:ui_writing_paper` | `figures/frontend/writing_paper.png` | 1920x964 (~2:1) | Trang 85 | **Giá trị khoa học xuất sắc.** Trực quan hóa Writing Studio với Monaco Editor, cây thư mục LaTeX và bản PDF biên dịch thời gian thực. | **GIỮ NGUYÊN** |
| 12 | `fig:langfuse_tracing` | `figures/frontend/langfuse_tracing.jpg` | 1024x558 (~16:9) | Trang 88 | **Giá trị thực nghiệm định lượng cao.** Bảng vết quan sát 110 traces Langfuse, minh chứng tính minh bạch khi gọi LLM và đo độ trễ. | **GIỮ NGUYÊN** |
| 13 | `fig:monitor_azure` | `figures/frontend/azure_monitor.png` | 1024x558 (~16:9) | Trang 90 | **Chất lượng kém & Dính lỗi giao diện:** Dính popup "No data returned matching the selected filters" che mất đồ thị CPU. Không có giá trị khoa học nếu để nguyên lỗi. | **LOẠI BỎ (BỎ)** (hoặc Sửa nếu chụp lại được) |
| 14 | `fig:monitor_exa` | `figures/frontend/exa_usage.png` | 1024x558 (~16:9) | Trang 91 | **Dư thừa.** Biểu đồ dashboard Exa AI chỉ ghi 828 requests, thông tin này trình bày bằng văn bản là đủ, không cần chiếm trọn 1 trang in. | **LOẠI BỎ (BỎ)** |
| 15 | `fig:monitor_openai` | `figures/frontend/openai_usage.png` | 1024x558 (~16:9) | Trang 92 | **Giá trị kiểm chứng chi phí thực tế.** Báo cáo mức tiêu thụ token và $3.76 thực tế từ cổng quản trị OpenAI. | **GIỮ HOẶC GỘP** |
| 16 | `fig:monitor_langfuse_dashboard` | `figures/frontend/langfuse_dashboard.jpg` | 1024x558 (~16:9) | Trang 93 | **Trùng lặp với Hình 12 & 15.** Bảng điều khiển chi phí 24h của Langfuse có thể gộp chung hoặc chỉ trình bày số liệu bảng biểu. | **LOẠI BỎ (BỎ)** |

---

## PHẦN 4: ĐỐI SOÁT TÍNH XÁC THỰC VỚI HIỆN TRẠNG MÃ NGUỒN VÀ DỮ LIỆU VERISCHOLAR

### 4.1. Đối soát số liệu thực nghiệm định lượng (Ablation Study)
- **Tập tin chuẩn:** `docs/benchmarks/thesis_benchmark_results.json`
- **Kết quả đối soát:**
  + Bộ 3-Track Golden Benchmark gồm 36 câu hỏi chia đều 3 nhánh: 12 câu `advanced_rag`, 12 câu `graph_rag`, 12 câu `agentic_rag`.
  + Tỷ lệ pass: 36/36 câu (100%).
  + Điểm số trung bình toàn hệ thống:
    * Groundedness: `0.9775` (Khớp 100% với báo cáo: $0{,}9775$)
    * Relevance: `0.9471` (Khớp 100% với báo cáo: $0{,}9471$)
    * Citation BBox Precision: `0.9332` (Khớp 100% với báo cáo: $0{,}9332$)
    * Multi-hop Completeness: `0.9208` (Khớp 100% với báo cáo: $0{,}9208$)
  + Bảng đối chứng truy xuất (Retrieval Ablation):
    * Dense-only: Recall@5 = `0.8056`, MRR@10 = `0.7882`, nDCG@10 = `0.7985`, IoU = `0.7865`, $P_{50} = 65.12$, $P_{95} = 80.24$.
    * Sparse-only: Recall@5 = `0.8333`, MRR@10 = `0.7964`, nDCG@10 = `0.8241`, IoU = `0.8210`, $P_{50} = 46.21$, $P_{95} = 56.73$.
    * Hybrid RRF ($k=60$): Recall@5 = `0.9444`, MRR@10 = `0.9444`, nDCG@10 = `0.9444`, IoU = `0.9266`, $P_{50} = 93.95$, $P_{95} = 116.50$.
    * $\rightarrow$ **Khớp 100% với Bảng 4.3 trong báo cáo!**
  + Bảng đối chứng tự sửa lỗi LaTeX (LaTeX Self-Healing Ablation):
    * AST/Regex: 11/25 ($44{,}0\%$), 1.00 vòng.
    * Heuristic: 21/25 ($84{,}0\%$), 1.00 vòng.
    * Agentic ReAct: 24/25 ($96{,}0\%$), 1.16 vòng.
    * $\rightarrow$ **Khớp 100% với Bảng 4.4 trong báo cáo!**

### 4.2. Đối soát độ trễ hệ thống và cấu hình phần cứng
- Độ trễ DB trung bình $1{,}66\,\text{ms}$ được đo đạc thực tế qua điểm kiểm tra sức khỏe `/health/ready` kết nối PostgreSQL pgvector.
- Thời gian trả token đầu tiên qua SSE: $\text{TTFT} = 1{,}15\,\text{s}$ (đạt cam kết $< 1{,}5\,\text{s}$).
- Cấu hình máy chủ Azure: Ubuntu 24.04 LTS, 4 vCPU, 16GB RAM khớp với kịch bản triển khai tại `scripts/deploy_to_vps.sh`.
- Tên miền chính thức `https://verischolar.duckdns.org` đang hoạt động thực tế.

---

## PHẦN 5: KẾ HOẠCH HÀNH ĐỘNG KIẾN NGHỊ TINH GỌN CHƯƠNG 4

Dưới đây là lộ trình hành động cụ thể để đưa Chương 4 về chuẩn mực học thuật xuất sắc và thỏa mãn ngân sách trang (12 -- 16 trang):

### Ưu tiên 1 (P0: Cấp bách — Sửa lỗi cấu trúc đề mục và Sai sự thật)
1. **Khôi phục cấu trúc phân cấp chuẩn 4 Mục cấp 1:**
   - Đặt `\section{Giao diện các phân hệ chính của hệ thống}` cho tệp `4_2_giao_dien.tex` (Mục 4.2).
   - Đặt `\section{Kết quả kiểm thử tự động hệ thống qua bốn cổng xác minh}` cho tệp `4_3_kiem_thu.tex` (Mục 4.3).
   - Đặt `\section{Đánh giá thực nghiệm định lượng và hiệu năng hệ thống}` cho tệp `4_4_so_lieu.tex` (Mục 4.4).
   - Đảm bảo Mục lục hiển thị chuẩn xác: `4.1`, `4.2`, `4.3`, `4.4`.
2. **Khắc phục đề mục cấp 5 vi phạm quy chế:**
   - Xóa bỏ 4 lệnh `\paragraph` tại `4_1_moi_truong.tex`.
   - Chuyển thành danh sách `\begin{itemize}` gạch đầu dòng, triệt tiêu mã `4.1.3.0.1` -- `4.1.3.0.4` trong `main.toc`.
3. **Xử lý sai sự thật tại Hình `deep_read_paper.png`:**
   - Chụp lại ảnh màn hình thực tế có khung viền vàng Bounding Box nổi bật trên canvas PDF.
4. **Loại bỏ hình ảnh lỗi `azure_monitor.png`:**
   - Xóa bỏ hình ảnh dính popup lỗi "No data returned", chuyển các chỉ số CPU/RAM vào đoạn văn phân tích.

### Ưu tiên 2 (P1: Quan trọng — Cắt giảm hình ảnh dư thừa và Tinh gọn dung lượng trang)
5. **Cắt giảm 5 hình ảnh dư thừa:**
   - Loại bỏ `fig:ui_register` (`register.png`) $\rightarrow$ Tiết kiệm 1 trang.
   - Loại bỏ `fig:ui_login` (`login.png`) $\rightarrow$ Tiết kiệm 1 trang.
   - Loại bỏ `fig:ui_dashboard` (`dashboard.png`) $\rightarrow$ Tiết kiệm 1 trang.
   - Loại bỏ `fig:monitor_exa` (`exa_usage.png`) $\rightarrow$ Tiết kiệm 1 trang.
   - Loại bỏ `fig:monitor_langfuse_dashboard` (`langfuse_dashboard.jpg`) $\rightarrow$ Tiết kiệm 1 trang.
   - $\rightarrow$ **Tổng cộng tiết kiệm ngay 5 trang in!**
6. **Tinh gọn hướng dẫn cài đặt VS Code:**
   - Cắt bỏ 2 đoạn văn hướng dẫn tải VS Code, `uv sync`, `npm install` tại Mục 4.1.1.
   - Tinh gọn Bảng 4.1 (cấu trúc Monorepo đã có ở Chương 3) $\rightarrow$ Tiết kiệm thêm 1 trang.
7. **Dự báo sau tinh giản:**
   - Dung lượng Chương 4 giảm từ **23 trang** xuống còn **14 -- 15 trang**, hoàn toàn nằm trong Ngân sách Vàng (**12 -- 16 trang**) theo quy định tại `AGENTS.md`.

### Ưu tiên 3 (P2: Hoàn thiện — Chuẩn hóa định dạng và Trích dẫn học thuật)
8. **Chuyển đổi 100% bảng biểu sang `tabularx`:**
   - Chuyển Bảng 4.1, 4.2, 4.3, 4.4 sang `\begin{tabularx}{\textwidth}{|...|}` có viền khép kín, chống vỡ layout.
9. **Sửa đổi tham số Floats:**
   - Đổi toàn bộ `[H]` và `[htbp]` thành `[!htbp]` linh hoạt.
10. **Bổ sung trích dẫn `\cite`:**
    - Bổ sung 8 trích dẫn then chốt (`agache2020firecracker`, `cormack2009reciprocal`, `malkov2018hnsw`, `robertson1995okapi`, `shinn2023reflexion`, `blondel2008louvain`, `edge2024graphrag`, `dworkin2007gcm`).
11. **Khắc phục triệt để 5 vị trí Overfull \hbox:**
    - Thêm `\allowbreak` và căn chỉnh văn bản để không còn bất kỳ dòng nào đâm thủng lề 15,0cm.

---

## KẾT LUẬN VÀ XÁC NHẬN CỦA CHAPTER 4 REVIEWER

Chương 4 chứa đựng những số liệu thực nghiệm định lượng có giá trị khoa học rất cao và hoàn toàn chân thực (bộ benchmark 36 câu hỏi, kết quả Ablation Study về Hybrid RAG và Tác tử ReAct tự sửa lỗi LaTeX khớp 100% với dữ liệu gốc). Hệ thống đã được triển khai thực tế trên VPS công cộng với độ trễ thấp và độ tin cậy kiểm thử tự động 100%.

Tuy nhiên, Chương 4 hiện đang bị tổn hại nặng nề về mặt học thuật do:
1. **Lỗi cấu trúc phân cấp nghiêm trọng** làm mất hẳn Mục 4.3 và 4.4 trong Mục lục, đồng thời sinh ra đề mục cấp 5 vi phạm quy chế HUMG.
2. **Lạm phát hình ảnh** (16 hình ảnh) dẫn đến số trang phình to lên 23 trang (vượt ngân sách 43%), trong đó có nhiều hình ảnh dư thừa (form login/register, dashboard rỗng) và hình ảnh lỗi/sai sự thật (`deep_read_paper.png` không có Bounding Box, `azure_monitor.png` dính popup lỗi).
3. **Format bảng biểu chưa chuẩn** (`tabular` thay vì `tabularx`, dùng `[H]` cưỡng bức) và **hoàn toàn thiếu vắng trích dẫn học thuật**.

Việc thực thi nghiêm túc Bản kiến nghị tinh gọn này sẽ khôi phục trọn vẹn diện mạo học thuật chuẩn mực, giúp Chương 4 trở thành điểm sáng kỹ nghệ thực chứng thuyết phục nhất trước Hội đồng chấm Đồ án Tốt nghiệp.
