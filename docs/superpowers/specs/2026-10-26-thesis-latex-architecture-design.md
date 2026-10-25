# Thiết Kế Kiến Trúc Báo Cáo Đồ Án Tốt Nghiệp LaTeX & Quy Tắc Viết Báo Cáo VeriScholar

> **Tài liệu:** Bản thiết kế kiến trúc hệ thống tài liệu LaTeX và bộ quy tắc biên soạn đồ án tốt nghiệp  
> **Đề tài:** *Nghiên cứu và Xây dựng Nền tảng Trợ lý AI Nghiên cứu Khoa học Toàn trình Kết hợp Hybrid RAG Minh chứng Tọa độ, Mạng Tri thức 4-Thực thể (GraphRAG) và Tác nhân Tự sửa lỗi LaTeX (VeriScholar)*  
> **Tác giả:** Đàm Mạnh Dũng — Ngành Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất (HUMG)  
> **Trạng thái:** Chờ phê duyệt (Pending Approval)  
> **Đường dẫn lưu trữ:** `docs/superpowers/specs/2026-10-26-thesis-latex-architecture-design.md`  

---

## 1. Mục Đích & Bối Cảnh (Intent & The Why)

### 1.1. Bối cảnh
Tác giả đang chuẩn bị bảo vệ Đồ án Tốt nghiệp ngành Công nghệ Thông tin tại Trường Đại học Mỏ - Địa chất (HUMG). Nền tảng phát triển là VeriScholar — hệ thống Trợ lý AI nghiên cứu khoa học toàn trình với kiến trúc hiện đại (FastAPI, React 19, PostgreSQL 16 `pgvector`, CAS SHA-256, Hybrid RAG RRF $k=60$, GraphRAG 4 thực thể, LangGraph ReAct và E2B Cloud Sandbox).

### 1.2. Mục đích
Thiết lập toàn bộ khung làm việc, cấu trúc mã nguồn LaTeX và bộ quy chuẩn biên soạn bất biến trong thư mục `report-datn/` nhằm:
1. Đảm bảo việc biên dịch mượt mà trên môi trường **VSCode kết hợp tiện ích LaTeX Workshop của James Yu** (sử dụng phím tắt `Ctrl+Alt+B` để build sang PDF và `Ctrl+Alt+V` để xem trực tiếp).
2. Xóa bỏ hoàn toàn nguy cơ lỗi phông chữ tiếng Việt có dấu, lỗi tràn lề, lỗi đánh số mục mồ côi hoặc sai lệch chuẩn mực học thuật.
3. Chắt lọc và chuyển hóa tri thức khoa học từ `docs/` (PRD, Specs, Sổ tay phản biện, Lộ trình song song) thành văn phong học thuật chuẩn mực của một bản ĐATN đạt điểm xuất sắc, thay vì sao chép máy móc mã nguồn hay nhật ký nhà phát triển.
4. Phù hợp hoàn hảo với quy trình in ấn thực tế: Bìa cứng mạ vàng và bìa lót màu được tiệm in đóng riêng; tệp PDF xuất ra từ LaTeX là toàn bộ phần ruột (bắt đầu từ Lời cảm ơn, Mục lục đến hết Tài liệu tham khảo) để kẹp vào đóng gáy.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Chống Mục Tiêu (Goals, Non-Goals & Anti-Goals)

### 2.1. Mục tiêu (Goals)
* **G1 — Bộ quy tắc bất biến `report-datn/RULES.md`:** Tổng hợp đầy đủ các quy định ngặt nghèo từ `Huong-dan-viet-DATN.md` của HUMG và 4 chuẩn mực văn phong đúc rút từ 2 đồ án mẫu đạt điểm cao (Nguyễn Trung Hiếu và Nguyễn Quang Bắc).
* **G2 — Kiến trúc Đa tệp Mô-đun Hóa:** Phân tách rõ ràng giữa tệp điều phối `main.tex`, thư mục cấu hình `config/`, phần sơ bộ `frontmatter/`, các chương nội dung `chapters/`, thư mục sơ đồ `figures/`, và tệp trích dẫn `references.bib`.
* **G3 — Trình biên dịch XeLaTeX tiêu chuẩn:** Cấu hình phông chữ hệ thống `Liberation Serif` (tương đương Microsoft Times New Roman), cỡ chữ 13pt, dãn dòng 1.5 lines, lề trang chuẩn xác (trên 2.5cm, dưới 2.5cm, trái 3.5cm, phải 2.5cm), chân trang bên trái ghi thông tin tác giả, chân trang bên phải đánh số trang.
* **G4 — Cấu trúc 4 Chương chuẩn HUMG:**
  * Phần sơ bộ: Lời cảm ơn, Lời mở đầu, Mục lục, Danh mục ký hiệu và chữ viết tắt, Danh mục bảng biểu, Danh mục hình vẽ.
  * Chương 1: Tổng quan về đề tài (Lý do chọn đề tài, Mục tiêu, Nhiệm vụ, Đối tượng & Phạm vi, Đóng góp mới, Bố cục).
  * Chương 2: Cơ sở lý thuyết & Công nghệ liên quan (Kiến trúc Lục giác, Hybrid RAG RRF $k=60$, GraphRAG 4 thực thể, LangGraph ReAct StateGraph + E2B Sandbox, SSE & Bounding Box) kèm phân tích sâu sắc "Tại sao chọn".
  * Chương 3: Phân tích & Thiết kế hệ thống (Khảo sát nghiệp vụ, Actor, Danh mục Use Case, Biểu đồ tuần tự Sequence, Biểu đồ lớp Class Diagram, Biểu đồ thành phần & Triển khai, Thiết kế CSDL 16 bảng kèm Từ điển dữ liệu Data Dictionary).
  * Chương 4: Cài đặt và Kết quả thực nghiệm (Môi trường Monorepo, Ảnh chụp màn hình luồng chức năng chính, Kết quả 4 Cổng kiểm thử tự động, Số liệu đo lường định lượng E1/E2/E3 và giám sát Langfuse Cloud).
  * Kết luận và Hướng phát triển (Kết quả đạt được, Hạn chế, 3 hướng mở rộng tương lai).
  * Danh mục tài liệu tham khảo: Phân nhóm Tiếng Việt và Tiếng Anh theo thứ tự ABC.
* **G5 — Cơ chế chắt lọc nội dung thông minh:** Bổ sung các phân tích nghiệp vụ, luận giải kiến trúc; lược bỏ các file mã nguồn thô sơ, log hệ thống hay các prompt điều phối nội bộ của AI.

### 2.2. Phi mục tiêu (Non-Goals)
* **NG1:** Không tạo các trang bìa cứng in chữ nhũ hoặc bìa phụ bằng TikZ vì tác giả đã làm riêng bìa cứng bên ngoài để tiệm in kẹp gáy.
* **NG2:** Không dồn toàn bộ báo cáo vào một tệp `main.tex` đơn lẻ.
* **NG3:** Không nhúng toàn bộ mã nguồn chương trình vào thân báo cáo (chỉ đưa các đoạn thuật toán then chốt hoặc mô hình dữ liệu vào phụ lục/chương thiết kế).

### 2.3. Chống mục tiêu (Anti-Goals)
* **AG1 — Cấm tuyệt đối lỗi phông tiếng Việt:** Tuyệt đối không dùng pdfLaTeX gây lỗi `T5 unknown` và vỡ font. Bắt buộc 100% biên dịch xanh với XeLaTeX.
* **AG2 — Cấm tiểu mục mồ côi (Orphaned Subsections):** Tuyệt đối không được tạo mục `x.y.1` mà không có mục `x.y.2`.
* **AG3 — Cấm tham chiếu mơ hồ:** Cấm các cụm từ *"bảng dưới đây"*, *"hình trên"*, *"đồ thị sau"*. Bắt buộc dùng `\ref{...}` định danh số cụ thể.
* **AG4 — Cấm văn phong cảm tính:** Không dùng đại từ nhân xưng ngôi thứ nhất (*"tôi"*, *"chúng tôi"*, *"em"*).
* **AG5 — Cấm sao chép nguyên si thiếu chọn lọc (No Brainless Copy-Paste):** Không bê nguyên văn các tệp `PRD/` hay `specs/` dạng bullet list ngắn cũn cỡn của tài liệu kỹ thuật vào báo cáo; bắt buộc phải diễn giải thành các đoạn văn học thuật mạch lạc, có phân tích nguyên nhân - kết quả.

---

## 3. Các Hướng Tiếp Cận Đã Cân Nhắc (Approaches Considered)

### Hướng 1: Kiến Trúc Đa Tệp Mô-đun Hóa Chuẩn Học Thuật (ĐÃ CHỌN)
* **Mô tả:** Tách nhỏ toàn bộ đồ án thành các tệp chuyên biệt theo cấu trúc: `config/`, `frontmatter/`, `chapters/`, `figures/`, `references.bib`, được liên kết thông qua lệnh `\include{...}` trong `main.tex`.
* **Ưu điểm:**
  * Rõ ràng, tính độc lập cao, dễ tìm kiếm và chỉnh sửa.
  * Hỗ trợ lệnh `\includeonly{chapters/...}` giúp tác giả khi tập trung viết một chương cụ thể có thể chỉ biên dịch chương đó trong 1 giây, tiết kiệm thời gian và tài nguyên máy tính.
  * Dễ dàng tích hợp với Member 1 qua Herdr: khi một Plan hoàn thành, chỉ cập nhật tệp chương tương ứng.
* **Đánh đổi:** Cần thêm chú thích `% !TEX root = ../main.tex` ở đầu mỗi tệp con để VSCode LaTeX Workshop tự động nhận diện tệp gốc.
* **Lý do chọn:** Tác giả đã đồng thuận lựa chọn Hướng 1 vì đây là chuẩn mực cao nhất cho các bản đồ án tốt nghiệp quy mô lớn (> 100 trang).

### Hướng 2: Cấu Trúc Bán Tập Trung (ĐÃ LOẠI BỎ)
* **Mô tả:** Gom toàn bộ khai báo gói, định nghĩa và phần sơ bộ vào `main.tex`, chỉ tách 4 file chương nằm phẳng ở thư mục gốc `report-datn/`.
* **Lý do loại bỏ:** File `main.tex` dài hàng trăm dòng gây rối mắt, khó quản lý tài nguyên ảnh và không tận dụng được tối đa tính năng biên dịch từng phần của LaTeX.

---

## 4. Đặc Tả Chi Tiết Kiến Trúc & Cấu Trúc Thư Mục (Detailed Design)

### 4.1. Cây thư mục hoàn chỉnh trong `report-datn/`

```text
report-datn/
├── RULES.md                        # Bộ quy tắc bất biến cho AI biên soạn báo cáo
├── main.tex                        # Tệp điều phối trung tâm (gọi \include các phần)
├── main.pdf                        # Tệp PDF thành phẩm sau khi biên dịch (Ctrl+Alt+B)
├── references.bib                  # Danh mục tài liệu tham khảo BibTeX (Tiếng Việt & Tiếng Anh)
├── config/
│   ├── preamble.tex                # Cấu hình gói XeLaTeX, canh lề geometry, font 13pt, linespread 1.5
│   └── commands.tex                # Định nghĩa các macro tiện ích (ký hiệu, bảng, hộp ghi chú)
├── frontmatter/
│   ├── loi_cam_on.tex              # Lời cảm ơn (đánh số trang i)
│   ├── loi_mo_dau.tex              # Lời mở đầu (đánh số trang ii)
│   ├── danh_muc_viet_tat.tex       # Danh mục các ký hiệu và chữ viết tắt (xếp theo thứ tự ABC)
│   ├── danh_muc_bang.tex           # Danh mục bảng biểu (\listoftables)
│   └── danh_muc_hinh.tex           # Danh mục hình vẽ, đồ thị (\listoffigures)
├── chapters/
│   ├── ch1_tong_quan.tex           # Chương 1: Tổng quan về đề tài
│   ├── ch2_co_so_ly_thuyet.tex     # Chương 2: Cơ sở lý thuyết và công nghệ sử dụng
│   ├── ch3_thiet_ke_he_thong.tex   # Chương 3: Phân tích và thiết kế hệ thống
│   ├── ch4_thuc_nghiem.tex         # Chương 4: Cài đặt và Kết quả thực nghiệm
│   └── ket_luan.tex                # Kết luận và Hướng phát triển
├── figures/                        # Thư mục chứa hình vẽ, sơ đồ kiến trúc chuẩn bài báo
│   └── chX_...                     # Các sơ đồ trích xuất từ docs/ (PNG / PDF vector)
└── guide/                          # Thư mục chứa tài liệu hướng dẫn và đồ án mẫu của HUMG
```

### 4.2. Đặc tả Tệp Điều Phối `main.tex`
* Khai báo chương trình biên dịch: `% !TEX program = xelatex` (ở dòng đầu tiên).
* Lớp văn bản: `\documentclass[12pt,a4paper,oneside]{report}` kết hợp `\usepackage[fontsize=13pt]{scrextend}` để thiết lập chuẩn xác cỡ chữ 13pt mà không gây xung đột với `report.cls`.
* Tùy chọn trang bìa mềm phục vụ nộp lưu trữ bản mềm: Thiết lập cờ điều kiện `\newif\ifshowcover \showcoverfalse`. Mặc định tắt để xuất file PDF in ấn từ Mục lục/Lời cảm ơn; khi cần nộp file mềm cho bộ môn chỉ cần đổi thành `\showcovertrue` để nạp `frontmatter/bia_phu.tex` (chuẩn Phụ lục 02).
* Nạp cấu hình: `\input{config/preamble}` và `\input{config/commands}`.
* Trình tự các trang đầu (Frontmatter):
  * Đặt đánh số trang La Mã: `\pagenumbering{roman}` và `\setcounter{page}{1}`.
  * Tùy chọn thứ tự hiển thị: `frontmatter/loi_cam_on.tex` $\rightarrow$ `\tableofcontents` $\rightarrow$ `frontmatter/danh_muc_viet_tat.tex` $\rightarrow$ `\listoftables` $\rightarrow$ `\listoffigures`.
  * `frontmatter/loi_mo_dau.tex`: Đóng vai trò bài dẫn nhập ngắn (1 trang) nêu bối cảnh ra đời đề tài.
* Phần thân bài (Main Body):
  * Chuyển sang đánh số Ả Rập: `\cleardoublepage`, `\pagenumbering{arabic}`, `\setcounter{page}{1}`.
  * Nạp lần lượt 4 chương: `chapters/ch1_tong_quan`, `chapters/ch2_co_so_ly_thuyet`, `chapters/ch3_thiet_ke_he_thong`, `chapters/ch4_thuc_nghiem`. Trong đó, `ch1_tong_quan.tex` đi sâu vào đặc tả bài toán, mục tiêu nghiên cứu, đóng góp mới và bố cục đồ án, không bị trùng lặp với Lời mở đầu.
  * Nạp `chapters/ket_luan`.
* Phần kết thúc & Tài liệu tham khảo:
  * Do hệ thống môi trường máy tính không cài đặt `biber` mà chỉ có `bibtex`, tài liệu tham khảo được quản lý qua khối môi trường chuẩn phân nhóm `frontmatter/tai_lieu_tham_khao.tex` (hoặc `bibtex` tương thích) chia tách rõ ràng 2 mục *"Tài liệu tiếng Việt"* và *"Tài liệu tiếng Anh"* đánh số liên tục `[1]`, `[2]`, `[3]...` tuân thủ 100% quy định Phụ lục 03. Cơ chế này đảm bảo biên dịch 1 pass qua `xelatex` là ra kết quả ngay lập tức, không bao giờ bị lỗi `[?]` chưa giải quyết.

### 4.3. Đặc tả Cấu Hình Giao Diện Trong `config/preamble.tex`
1. **Canh lề trang (Geometry):**
   ```latex
   \usepackage[a4paper, top=2.5cm, bottom=2.5cm, left=3.5cm, right=2.5cm]{geometry}
   ```
2. **Phông chữ & Dãn dòng (XeLaTeX & fontspec):**
   ```latex
   \usepackage{fontspec}
   \setmainfont{Liberation Serif}[
       Path = /usr/share/fonts/truetype/liberation/,
       UprightFont = LiberationSerif-Regular.ttf,
       BoldFont = LiberationSerif-Bold.ttf,
       ItalicFont = LiberationSerif-Italic.ttf,
       BoldItalicFont = LiberationSerif-BoldItalic.ttf
   ]
   \usepackage[provide=*,vietnamese]{babel}
   \usepackage{setspace}
   \onehalfspacing % Hoặc \setstretch{1.3} tương ứng 1.5 lines trong Word
   ```
3. **Tiêu đề đầu trang & chân trang (fancyhdr):**
   ```latex
   \usepackage{fancyhdr}
   \pagestyle{fancy}
   \fancyhf{}
   \renewcommand{\headrulewidth}{0pt} % Không kẻ đường ngang ở đầu trang
   \fancyfoot[L]{\fontsize{10}{12}\selectfont\textit{SVTH: Đàm Mạnh Dũng -- Ngành Công nghệ thông tin}}
   \fancyfoot[R]{\fontsize{10}{12}\selectfont\thepage}
   ```
4. **Định dạng tiêu đề mục và cấm mồ côi (titlesec):**
   * Định dạng tiêu đề chương, mục, tiểu mục rõ ràng, đậm nét.
   * Giới hạn đánh số đến 4 cấp (`\setcounter{secnumdepth}{4}` và `\setcounter{tocdepth}{3}`).
5. **Định dạng bảng biểu & hình vẽ (caption):**
   ```latex
   \usepackage{caption}
   \captionsetup[table]{position=top, labelfont=bf, textfont=it, skip=6pt}
   \captionsetup[figure]{position=bottom, labelfont=bf, textfont=it, skip=6pt}
   ```

---

## 5. Chiến Lược Chắt Lọc Nội Dung Từ `docs/` (Knowledge Distillation Strategy)

Bảng phân loại nội dung: **GIỮ LẠI & PHÁT TRIỂN (KEEP & ELEVATE)** vs. **LƯỢC BỎ (OMIT)** khi đưa từ kho tài liệu `docs/` vào Báo cáo Đồ án:

| Chương ĐATN | Nội Dung Giữ Lại & Diễn Giải Học Thuật (KEEP & ELEVATE) | Nội Dung Lược Bỏ Tuyệt Đối (OMIT) |
| :--- | :--- | :--- |
| **Chương 1: Tổng quan** | • Bối cảnh bùng nổ bài báo khoa học và hiện tượng ảo giác (Hallucination).<br>• Phân tích hạn chế của ChatPDF thông thường và Overleaf truyền thống.<br>• Mục tiêu 4 không gian khép kín (Khám phá, Đọc sâu, Thư viện GraphRAG, Soạn thảo LaTeX).<br>• 4 đóng góp kỹ thuật cốt lõi của đề tài. | • Lược bỏ nhật ký dọn dẹp thư mục monorepo.<br>• Lược bỏ các ghi chú về quy trình git workflow cá nhân. |
| **Chương 2: Cơ sở lý thuyết** | • Nguyên lý Kiến trúc Lục giác (Hexagonal Architecture) và tính cô lập miền.<br>• Toán học tìm kiếm lai: Vector HNSW Cosine, BM25 toàn văn, Công thức Hợp nhất Xếp hạng Đảo ngược $\text{RRF}(d) = \sum \frac{1}{k + \text{rank}_i(d)}$ ($k=60$).<br>• Mô hình đồ thị tri thức 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) trên PostgreSQL `pgvector`.<br>• Chu trình Tác nhân ReAct LangGraph StateGraph và Cloud Sandbox E2B.<br>• Phép biến đổi tọa độ Bounding Box trực quan $[0..1000]$ trên trang PDF.<br>• **Đặc biệt:** Đoạn văn luận giải "Tại sao chọn" công nghệ đối ứng theo mẫu của 2 đồ án xuất sắc. | • Lược bỏ cú pháp cấu hình docker-compose chi tiết.<br>• Lược bỏ mã cấu hình linter/formatter Python/TypeScript. |
| **Chương 3: Phân tích & Thiết kế** | • 30 Ca sử dụng (Use Case) chuẩn hóa BA: Tác nhân, Tiền/Hậu điều kiện, Luồng chính, Ngoại lệ.<br>• Sơ đồ kiến trúc tổng thể Paper-grade và Biểu đồ lớp (Class Diagram).<br>• Các biểu đồ tuần tự UML (Sequence Diagram) cho luồng đăng nhập, nạp PDF 2 tầng, hỏi đáp Hybrid RAG nhảy trang, và sửa lỗi LaTeX tự động.<br>• Thiết kế CSDL 16 bảng vật lý kèm Từ điển dữ liệu (Data Dictionary) chi tiết (Tên cột, Kiểu dữ liệu, Khóa, Ràng buộc). | • Lược bỏ các file test fixture, mock service.<br>• Lược bỏ tên các file mã nguồn `.tsx` hay `.py` trong sơ đồ thiết kế kiến trúc khái niệm. |
| **Chương 4: Thực nghiệm & Đánh giá** | • Môi trường triển khai máy chủ Azure Ubuntu VM, phần cứng, phần mềm.<br>• Ảnh chụp màn hình các giao diện phân hệ chính đang hoạt động.<br>• Kết quả kiểm thử tự động 4 Cổng (Pytest, Vitest, Linter, Production Build).<br>• Số liệu thực nghiệm định lượng đo đạc từ hệ thống: Độ trễ TTFT, Bounding Box IoU, Tỷ lệ tự sửa lỗi biên dịch LaTeX $\ge 90\%$, Bằng chứng truy vết Langfuse Cloud. | • Lược bỏ các thông báo lỗi console tạm thời trong quá trình debug.<br>• Lược bỏ các biến môi trường nhạy cảm (`SECRET_KEY`, `OPENAI_API_KEY`). |

---

## 6. Phân Bổ Công Việc Cho Người Thực Thi (What's Left to the Builder)

Sau khi bản thiết kế được phê duyệt, người thực thi (kế hoạch TDD) sẽ tiến hành:
1. Soạn thảo tệp `report-datn/RULES.md` phản ánh nguyên vẹn toàn bộ các quy chuẩn bất biến trên.
2. Khởi tạo cấu trúc thư mục và các tệp mẫu `.tex` trong `report-datn/` (`main.tex`, `config/`, `frontmatter/`, `chapters/`, `references.bib`).
3. Cấu hình tệp `.vscode/settings.json` trong workspace đảm bảo LaTeX Workshop gọi đúng `xelatex` khi gõ `Ctrl+Alt+B`.
4. Chạy lệnh biên dịch thử nghiệm bản khung sườn rỗng sang `main.pdf` và xác nhận không có lỗi cú pháp (Exit code 0).
5. Phối hợp với Member 1 qua Herdr để lần lượt đưa dữ liệu kỹ thuật từ các Plan đã nghiệm thu vào từng chương tương ứng.
