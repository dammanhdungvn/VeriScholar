# TÀI LIỆU THIẾT KẾ KIẾN TRÚC: HỆ THỐNG MỤC LỤC MASTER ROADMAP VÀ PHÂN RÃ VI MÔ (MICRO-MODULAR) BÁO CÁO ĐỒ ÁN TỐT NGHIỆP VERISCHOLAR

* **Ngày lập:** 2026-10-26 (Cập nhật chuẩn hóa theo mẫu thực tế HUMG)
* **Trạng thái:** Dự thảo hoàn chỉnh đã đồng bộ mẫu HUMG K66/K67
* **Tác giả:** Đàm Mạnh Dũng - 2221050359 – Lớp: DCCTCT67_09B, Khoa Công nghệ Thông tin, Đại học Mỏ - Địa chất (HUMG)
* **Đề tài:** *Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn*

---

## 1. Mục Đích & Bối Cảnh Nghiên Cứu (Intent & The Why)

### 1.1. Bối cảnh bài toán
Báo cáo Đồ án Tốt nghiệp Đại học tại Trường Đại học Mỏ - Địa chất (HUMG) là một công trình học thuật quy mô lớn (khoảng 80–120 trang), đòi hỏi tính chặt chẽ về phương pháp luận, tính toàn vẹn của thiết kế kỹ thuật phần mềm (UML, Database, Architecture) và bằng chứng thực nghiệm định lượng.

Trong kỷ nguyên phát triển phần mềm với sự hỗ trợ của các Tác nhân Trí tuệ Nhân tạo (Agentic AI), việc duy trì và biên soạn một tài liệu học thuật đồ sộ thường gặp phải hai rào cản nghiêm trọng:
1. **Quá tải Cửa sổ Ngữ cảnh (Context Window Bloat) và Lãng phí Token:** Nếu tổ chức báo cáo dưới dạng các tệp chương nguyên khối (`ch1.tex`, `ch2.tex`, `ch3.tex`, `ch4.tex` hàng nghìn dòng mã nguồn), mỗi khi AI cần cập nhật hoặc viết thêm một tiểu mục nhỏ, toàn bộ tệp chương dài phải được nạp vào bộ nhớ ngữ cảnh. Điều này gây hao tổn tài nguyên API token khổng lồ, tăng độ trễ xử lý và tiềm ẩn nguy cơ AI vô tình làm biến đổi các phần nội dung khác không liên quan.
2. **Hiện tượng mất phương hướng toàn cảnh (Architectural Drift):** Khi thiếu một "Bản đồ hoa tiêu tổng thể" (Master Roadmap), các lượt biên soạn của AI dễ bị phân mảnh, trùng lặp luận điểm giữa các chương, hoặc đặt tiêu đề theo văn phong trần thuật kể lể vi phạm chuẩn mực học thuật.

### 1.2. Mục đích thiết kế
Tài liệu này định hình kiến trúc **Phân rã Vi mô (Micro-Modular Structure)** và xuất bản **Bản đồ Mục lục Chuẩn Cấp 4 (Master TOC Roadmap)** cho toàn bộ thư mục `report-datn/`, thiết lập nền móng vững chắc giúp AI có thể độc lập tác nghiệp trên từng tệp vi mô mà không làm ảnh hưởng đến tổng thể quyển đồ án.

---

## 2. Mục Tiêu, Giới Hạn & Điều Cấm (Goals, Non-Goals, Anti-Goals)

### 2.1. Mục tiêu (Goals)
1. **Thiết lập cây thư mục Micro-Modular:** Tạo các thư mục con chuyên biệt `chapters/ch1/`, `chapters/ch2/`, `chapters/ch3/`, `chapters/ch4/`.
2. **Phân rã tệp cấp mục (Section-level granularity):** Mỗi mục lớn cấp 2 của chương là một tệp `.tex` độc lập (ví dụ: `chapters/ch3/3_1_khao_sat.tex`, `chapters/ch3/3_3_kien_truc.tex`...).
3. **Mô hình hóa tệp điều phối chương (Chapter Orchestrators):** Mỗi tệp `chapters/chX_ten_chuong.tex` đóng vai trò nhạc trưởng điều phối, chứa tiêu đề chương và các lệnh `\input{chapters/chX/...}` nạp tuần tự các tệp thành phần.
4. **Tạo lập Bản đồ Lộ trình Tra cứu Tức thì (`report-datn/ROADMAP.md`):** Đóng vai trò mục lục toàn cảnh, tóm tắt ý chính của từng file con và ánh xạ trực tiếp tới các tài liệu đặc tả kỹ thuật (`docs/specs/`). AI chỉ cần đọc file này là nắm trọn ngữ cảnh toàn đồ án.
5. **Đồng bộ hóa 100% với mã nguồn sản xuất:** Đảm bảo số lượng bảng CSDL (18 bảng ORM), 3 luồng tuần tự then chốt, 6 giao diện phân hệ và 6 chỉ số đo lường thực nghiệm khớp tuyệt đối giữa báo cáo và code.
6. **Tuân thủ tuyệt đối quy chuẩn HUMG & 4 Cổng Xác Minh:** Biên dịch sạch với XeLaTeX, không lỗi font tiếng Việt, không mục mồ côi, vượt qua 100% 4 Cổng kiểm định tự động.

### 2.2. Giới hạn ngoài phạm vi (Non-Goals)
* Chưa viết đầy đủ nội dung chi tiết 100 trang trong bước này. Giai đoạn này chỉ tập trung xây dựng bộ khung sườn cấu trúc, các tệp phân rã rỗng/khung và lộ trình tài liệu.
* Không can thiệp vào mã nguồn logic của backend (`apps/api`) hoặc frontend (`apps/web`).

### 2.3. Điều cấm tuyệt đối (Anti-Goals)
* Tuyệt đối không lưu trữ báo cáo dưới dạng tệp đơn khối (Monolithic `.tex`).
* Tuyệt đối không dùng văn phong kể lể, mở đầu tiêu đề bằng các động từ hành động (*"Nghiên cứu...", "Khảo sát...", "Tìm hiểu..."*).
* Tuyệt đối không dịch gượng gạo các thuật ngữ kỹ thuật chuẩn quốc tế (*Dense/Sparse Retrieval, Hybrid RAG, GraphRAG, ReAct Agent, Bounding Box, Sequence Diagram, ERD, Data Dictionary, CAS, BYOK, Monorepo, E2B Sandbox*).
* Tuyệt đối không để tồn tại tiểu mục "mồ côi" (mục cấp $N$ bắt buộc phải có từ 2 mục con cấp $N+1$ trở lên).
* Tuyệt đối không dùng đường dẫn tuyệt đối máy chủ (`file://`) trong tài liệu Markdown.

---

## 3. Các Ràng Buộc Kỹ Thuật (Constraints)

1. **Trình biên dịch:** Bắt buộc **XeLaTeX** (`latexmk -xelatex`). Tuyệt đối cấm `pdfLaTeX` do xung đột bảng mã font tiếng Việt trên môi trường Linux.
2. **Quy chuẩn trang in HUMG (Đồng bộ 100% mẫu đồ án Khoa CNTT):**
   * Khổ giấy: A4 (210 x 297 mm), in một mặt.
   * Căn lề: Trên 2.5 cm, Dưới 2.5 cm, Trái 3.5 cm (đóng gáy), Phải 2.5 cm.
   * Phông chữ: `Liberation Serif` (tương đương Times New Roman), cỡ chữ **13pt**, dãn dòng **1.5 lines** (`\onehalfspacing`).
   * Tiêu đề đầu trang (Header): Góc trên bên trái: `\textbf{Đồ án tốt nghiệp ngành Công nghệ thông tin}`, có đường kẻ ngang phân cách đầu trang (`\headrulewidth = 0.5pt`).
   * Tiêu đề chân trang (Footer): Góc dưới bên trái: `\textit{SVTH: Đàm Mạnh Dũng - 2221050359 – Lớp: DCCTCT67_09B}`, góc dưới bên phải: `\textit{\thepage}`, có đường kẻ ngang phân cách chân trang (`\footrulewidth = 0.5pt`).
   * Phân trang La Mã / Ả Rập:
     * Đánh số La Mã thường (`i, ii, iii...`): Dành cho `MỤC LỤC` (bắt đầu từ trang `i`), `DANH MỤC HÌNH ẢNH`, `DANH MỤC BẢNG BIỂU`, `DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT`.
     * Đánh số Ả Rập (`1, 2, 3...`): Bắt đầu từ `LỜI CẢM ƠN` (trang 1), `LỜI MỞ ĐẦU` (trang 2), `CHƯƠNG 1` (trang 3 trở đi).
3. **Quy chuẩn đặt tên bảng & hình:**
   * Bảng biểu: Tiêu đề đặt ở **TRÊN** bảng.
   * Hình ảnh: Tiêu đề đặt ở **DƯỚI** hình.
4. **4 Cổng Xác Minh Bắt Buộc:**
   * Cổng 1: `uv run ruff check . && uv run ruff format --check .` (0 error).
   * Cổng 2: `uv run pytest` (100% pass).
   * Cổng 3: `npm --prefix apps/web run test` (100% pass).
   * Cổng 4: `npm --prefix apps/web run build` (Build thành công).

---

## 4. Các Phương Án Đã Cân Nhắc & Luận Giải (Approaches & Trade-offs)

| Tiêu chí so sánh | Phương án 1: Micro-Modular (Được chọn) | Phương án 2: Chapter-Level Modular (Cũ) | Phương án 3: Deep Sub-modular (Tách cấp 3/4) |
| :--- | :--- | :--- | :--- |
| **Cơ chế tổ chức** | Mỗi mục lớn cấp 2 là một tệp `.tex` trong thư mục `chapters/chX/`. | Mỗi chương là một tệp `.tex` duy nhất (`ch1_*.tex`... `ch4_*.tex`). | Mỗi tiểu mục nhỏ cấp 3 và cấp 4 là một tệp riêng rẽ. |
| **Tiêu tốn Context Token của AI** | **Cực thấp (~1k - 3k tokens/lượt):** AI chỉ đọc duy nhất tệp đang cần sửa. | **Rất cao (~10k - 25k tokens/lượt):** AI phải nạp cả chương hàng nghìn dòng. | Thấp (~500 - 1k tokens), nhưng overhead nạp nhiều tệp quá lớn. |
| **Rủi ro sửa nhầm lan truyền** | **Không có:** Cô lập hoàn toàn phạm vi chỉnh sửa theo từng mục. | **Cao:** AI dễ vô tình làm thay đổi cú pháp các đoạn văn khác trong chương. | Rất thấp. |
| **Chi phí quản lý tệp (File Overhead)** | **Tối ưu:** ~23 tệp nội dung, cấu trúc gọn gàng, trực quan. | Thấp: Chỉ có 4 tệp chương. | Quá cao: Hơn 70 tệp vụn vặt, khó quản lý git và dễ vỡ liên kết. |
| **Khả năng cộng tác song song** | **Xuất sắc:** Nhiều tác nhân/con người có thể viết đồng thời các mục khác nhau. | Kém: Xung đột git merge conflict liên tục khi sửa chung một chương. | Tốt nhưng quá phân tán. |

**Quyết định:** Chọn **Phương án 1 (Micro-Modular)** kết hợp tệp chỉ dẫn `ROADMAP.md`. Đây là kiến trúc tối ưu nhất được bảo chứng bởi các dự án tài liệu kỹ thuật tiêu chuẩn cao.

---

## 5. Kiến Trúc Chi Tiết & Bản Đồ Mục Lục Master Roadmap

### 5.1. Cây thư mục hệ thống tài liệu `report-datn/`
```text
report-datn/
├── config/
│   ├── preamble.tex                 # Khai báo gói lệnh, lề trang, cỡ chữ 13pt, header/footer
│   └── commands.tex                 # Macro toán học, từ viết tắt, ký hiệu thuận tiện
├── frontmatter/
│   ├── bia_phu.tex                  # Trang bìa phụ tiếng Việt theo Phụ lục 02 HUMG
│   ├── danh_muc_hinh.tex            # Danh mục hình ảnh tự động (\listoffigures)
│   ├── danh_muc_bang.tex            # Danh mục bảng biểu tự động (\listoftables)
│   ├── danh_muc_viet_tat.tex        # Bảng thuật ngữ viết tắt xếp ABC
│   ├── loi_cam_on.tex               # Lời cảm ơn thầy cô hướng dẫn và gia đình (Trang 1)
│   └── loi_mo_dau.tex               # Lời mở đầu dẫn nhập bối cảnh nghiên cứu (Trang 2)
├── chapters/
│   ├── ch1/                         # [Micro-Modular] Thư mục chứa các mục con Chương 1
│   │   ├── 1_1_gioi_thieu.tex
│   │   ├── 1_2_tinh_cap_thiet.tex
│   │   ├── 1_3_muc_tieu.tex
│   │   ├── 1_4_noi_dung.tex
│   │   ├── 1_5_pham_vi.tex
│   │   └── 1_6_bo_cuc.tex
│   ├── ch1_tong_quan.tex            # Điều phối Chương 1 (nạp ch1/*.tex)
│   ├── ch2/                         # [Micro-Modular] Thư mục chứa các mục con Chương 2
│   │   ├── 2_1_hexagonal.tex
│   │   ├── 2_2_hybrid_rag.tex
│   │   ├── 2_3_pdf_bounding_box.tex
│   │   ├── 2_4_graph_rag.tex
│   │   ├── 2_5_react_agent.tex
│   │   └── 2_6_cas_byok.tex
│   ├── ch2_co_so_ly_thuyet.tex      # Điều phối Chương 2 (nạp ch2/*.tex)
│   ├── ch3/                         # [Micro-Modular] Thư mục chứa các mục con Chương 3
│   │   ├── 3_1_khao_sat.tex
│   │   ├── 3_2_use_cases.tex
│   │   ├── 3_3_kien_truc.tex
│   │   ├── 3_4_sequence_diagrams.tex
│   │   └── 3_5_co_so_du_lieu.tex
│   ├── ch3_thiet_ke_he_thong.tex    # Điều phối Chương 3 (nạp ch3/*.tex)
│   ├── ch4/                         # [Micro-Modular] Thư mục chứa các mục con Chương 4
│   │   ├── 4_1_moi_truong.tex
│   │   ├── 4_2_1_giao_dien.tex
│   │   ├── 4_2_2_kiem_thu.tex
│   │   └── 4_2_3_danh_gia_thuc_nghiem.tex
│   ├── ch4_thuc_nghiem.tex          # Điều phối Chương 4 (nạp ch4/*.tex)
│   ├── ket_luan.tex                 # Kết luận và Hướng phát triển
│   ├── tai_lieu_tham_khao.tex       # Tài liệu tham khảo chuẩn IEEE phân tách Việt - Anh
│   └── phu_luc.tex                  # Phụ lục 1 (Thuật toán RRF) & Phụ lục 2 (Bounding Box)
├── figures/                         # Thư mục chứa sơ đồ kiến trúc, biểu đồ, ảnh chụp
├── main.tex                         # Tệp điều phối trung tâm toàn bộ đồ án (< 70 dòng)
├── ROADMAP.md                       # Bản đồ định hướng chi tiết nội dung cho AI Agent
└── RULES.md                         # Bộ quy tắc bất biến về văn phong và kỹ thuật
```

### 5.2. Nội dung chi tiết Bản đồ Mục lục Master Roadmap (Đồng bộ 100% Hình 2 & 3 HUMG)

```text
MỤC LỤC ............................................................................................................... i
DANH MỤC HÌNH ẢNH ................................................................................... vii
DANH MỤC BẢNG BIỂU ................................................................................... x
DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT .......................................... xii
LỜI CẢM ƠN ........................................................................................................ 1
LỜI MỞ ĐẦU ........................................................................................................ 2
CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI ............................................................. 3
  1.1. Giới thiệu đề tài ........................................................................................... 3
  1.2. Tính cấp thiết của đề tài ............................................................................... 4
  1.3. Mục tiêu nghiên cứu .................................................................................... 4
    1.3.1. Mục tiêu tổng quát của đồ án
    1.3.2. Bốn mục tiêu kỹ thuật cụ thể
  1.4. Nội dung nghiên cứu.................................................................................... 5
    1.4.1. Nghiên cứu cơ sở lý thuyết và công nghệ
    1.4.2. Xây dựng và thực nghiệm hệ thống
  1.5. Phạm vi nghiên cứu ..................................................................................... 5
    1.5.1. Đối tượng nghiên cứu và đối tượng thụ hưởng
    1.5.2. Giới hạn phạm vi hệ thống
  1.6. Bố cục báo cáo đồ án tốt nghiệp .................................................................. 6

CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ....................................... 7
  2.1. Kiến trúc phần mềm lục giác (Hexagonal Architecture) ............................ 7
    2.1.1. Nguyên lý phân tách Ports and Adapters
    2.1.2. Quy tắc phụ thuộc bất biến mô hình miền
    2.1.3. Luận giải lựa chọn kiến trúc lục giác
  2.2. Kỹ thuật truy xuất lai (Hybrid RAG) ............................................................. 8
    2.2.1. Tìm kiếm Dense HNSW và Sparse BM25
    2.2.2. Thuật toán hợp nhất xếp hạng RRF
    2.2.3. Luận giải lựa chọn thuật toán RRF
  2.3. Xử lý tài liệu PDF và Bounding Box ............................................................ 9
    2.3.1. Cấu trúc tài liệu PDF đa cột
    2.3.2. Thuật toán chuẩn hóa tọa độ Bounding Box
    2.3.3. Luận giải chuẩn hóa tọa độ [0..1000]
  2.4. Mạng tri thức học thuật 4-thực thể (GraphRAG) ........................................ 10
    2.4.1. Nguyên lý mạng tri thức học thuật
    2.4.2. Mô hình hóa 4 thực thể cốt lõi
    2.4.3. Luận giải triển khai GraphRAG trên PostgreSQL
  2.5. Kiến trúc Agentic RAG và Tác nhân ReAct ................................................. 11
    2.5.1. Chu trình Suy luận - Hành động - Quan sát
    2.5.2. Cơ chế cách ly hộp cát đám mây
    2.5.3. Luận giải máy trạng thái LangGraph và E2B
  2.6. Lưu trữ định danh CAS và Két sắt BYOK .................................................. 12
    2.6.1. Nguyên lý lưu trữ định danh nội dung
    2.6.2. Mã hóa xác thực AEAD và mô hình BYOK
    2.6.3. Luận giải tối ưu lưu trữ và bảo mật

CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG ................................... 13
  3.1. Khảo sát nghiệp vụ và quy trình nghiên cứu .............................................. 13
    3.1.1. Khảo sát nghiệp vụ nghiên cứu tại VinUniversity
    3.1.2. Mô hình hóa quy trình nghiệp vụ tổng thể
  3.2. Xác định tác nhân và Biểu đồ Use Case ...................................................... 14
    3.2.1. Xác định các tác nhân hệ thống
    3.2.2. Biểu đồ ca sử dụng tổng quát (Use Case)
    3.2.3. Bảng đặc tả chi tiết ca sử dụng UC-03
  3.3. Thiết kế kiến trúc phần mềm hệ thống ........................................................ 15
    3.3.1. Kiến trúc phân tầng và Biểu đồ thành phần
    3.3.2. Biểu đồ lớp miền nghiệp vụ cốt lõi
    3.3.3. Biểu đồ triển khai hạ tầng hệ thống
  3.4. Thiết kế tương tác và Biểu đồ tuần tự ......................................................... 16
    3.4.1. Biểu đồ tuần tự luồng nạp bài báo
    3.4.2. Biểu đồ tuần tự luồng hỏi đáp Bounding Box
    3.4.3. Biểu đồ tuần tự chu trình ReAct tự sửa lỗi
  3.5. Thiết kế cơ sở dữ liệu và Từ điển dữ liệu .................................................... 17
    3.5.1. Lược đồ quan hệ thực thể (ERD 18 bảng)
    3.5.2. Cơ chế cô lập dữ liệu theo user_id
    3.5.3. Từ điển dữ liệu các bảng cơ sở dữ liệu

CHƯƠNG 4: THỰC NGHIỆM ........................................................................... 18
  4.1. Môi trường thực nghiệm ............................................................................ 18
    4.1.1. Cấu hình máy chủ Azure Ubuntu và gói phần mềm
    4.1.2. Cấu trúc Monorepo và quản lý cấu hình
    4.1.3. Triển khai các dịch vụ nền tảng hệ thống
  4.2. Kết quả thực nghiệm .................................................................................. 19
    4.2.1. Một số giao diện của hệ thống ............................................................ 19
      4.2.1.1. Giao diện khám phá bài báo đa nguồn
      4.2.1.2. Giao diện đọc sâu và tô sáng Bounding Box
      4.2.1.3. Giao diện bảng ngữ cảnh và ma trận nghiên cứu
      4.2.1.4. Giao diện thư viện tài liệu và GraphRAG
      4.2.1.5. Giao diện trợ lý soạn thảo biên dịch LaTeX
      4.2.1.6. Giao diện hồ sơ học giả và két sắt BYOK
    4.2.2. Xây dựng các ca kiểm thử tự động hệ thống ...................................... 20
      4.2.2.1. Chu trình kiểm thử tự động 4 Cổng xác minh
      4.2.2.2. Bảng kết quả kiểm định chất lượng phần mềm
    4.2.3. Kết quả thực nghiệm hệ thống ............................................................ 21
      4.2.3.1. Đo lường độ trễ CSDL và thời gian TTFT
      4.2.3.2. Đánh giá hiệu quả truy xuất Hybrid RAG
      4.2.3.3. Độ chính xác định vị Bounding Box (IoU)
      4.2.3.4. Tỷ lệ tự sửa lỗi biên dịch LaTeX
      4.2.3.5. Bằng chứng kiểm chứng thực tế trên Langfuse
      4.2.3.6. Hiệu quả tối ưu dung lượng lưu trữ CAS

KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN ......................................................... 22
TÀI LIỆU THAM KHẢO .................................................................................. 23

PHỤ LỤC
  Phụ lục 1: Thuật toán hợp nhất xếp hạng RRF (Reciprocal Rank Fusion)
  Phụ lục 2: Thuật toán chuẩn hóa hệ tọa độ Bounding Box [0..1000]
```

---

## 6. Công Việc Giao Cho Kỹ Sư Thực Thi (What's Left to the Builder)

Kỹ sư thực thi (Builder Agent) khi triển khai kế hoạch thực thi cần thực hiện các nhiệm vụ tuần tự:
1. **Khởi tạo cấu trúc thư mục vi mô:**
   * Tạo các thư mục `report-datn/chapters/ch1/`, `ch2/`, `ch3/`, `ch4/`.
2. **Phân rã nội dung và kiến tạo tệp con:**
   * Di chuyển nội dung đã viết từ các file nguyên khối cũ (`ch1_*.tex`... `ch4_*.tex`) sang các file con phân rã tương ứng.
   * Tạo khung sườn chuẩn xác cho các mục mới được bổ sung theo đúng tiêu đề trong Master TOC.
3. **Tái cấu trúc các tệp điều phối chương:**
   * Viết lại `ch1_tong_quan.tex`, `ch2_co_so_ly_thuyet.tex`, `ch3_thiet_ke_he_thong.tex`, `ch4_thuc_nghiem.tex` chứa cấu trúc `\chapter{...}` và danh sách lệnh `\input{...}` nạp tuần tự các tệp con.
4. **Tạo lập tệp phụ lục và nạp vào `main.tex`:**
   * Tạo `report-datn/chapters/phu_luc.tex` chứa Phụ lục 1 và Phụ lục 2.
   * Thêm `\input{chapters/phu_luc}` vào `main.tex`.
5. **Xuất bản Bản đồ Lộ trình `report-datn/ROADMAP.md`:**
   * Tạo tài liệu định hướng tra cứu nhanh tóm tắt nội dung cốt lõi của từng file con và liên kết chéo tới `docs/specs/`.
6. **Kiểm tra biên dịch và vượt qua 4 Cổng Xác Minh:**
   * Biên dịch tài liệu bằng XeLaTeX và xác minh tệp PDF kết quả không lỗi.
   * Chạy kiểm tra tự động 4 Cổng: Ruff Linter/Format, Pytest, Vitest, Vite Build.

---

## 7. Kết Quả Thẩm Định & Quyết Định Kỹ Thuật (Builder Check Resolutions)

Trong quá trình Builder Check độc lập bởi subagent LaTeX Architect, hai câu hỏi kỹ thuật đã được đặt ra và xử lý dứt khoát như sau:

1. **Phân định rạch ròi giữa Bảng viết tắt ở Frontmatter và Phụ lục:**
   * *Vấn đề:* Tránh trùng lặp giữa danh mục chữ viết tắt ở đầu sách và phụ lục ở cuối sách.
   * *Quyết định kỹ thuật:* Giữ nguyên `frontmatter/danh_muc_viet_tat.tex` theo đúng điều lệ bắt buộc của HUMG và bộ kiểm thử `tests/test_thesis_structure_and_compile.py`. Phần Phụ lục ở cuối đồ án (`chapters/phu_luc.tex`) được dành trọn vẹn cho việc công bố mã nguồn thuật toán cốt lõi:
     * **Phụ lục 1:** Thuật toán hợp nhất xếp hạng RRF (Reciprocal Rank Fusion).
     * **Phụ lục 2:** Thuật toán chuẩn hóa hệ tọa độ Bounding Box [0..1000].
2. **Thứ tự nạp các thành phần Frontmatter và phân trang (Đồng bộ 100% Hình 2 mẫu của Khoa):**
   * *Đánh số La Mã thường (i, ii...):* Bắt đầu từ `MỤC LỤC` (trang i) $\rightarrow$ `DANH MỤC HÌNH ẢNH` $\rightarrow$ `DANH MỤC BẢNG BIỂU` $\rightarrow$ `DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT`.
   * *Đánh số Ả Rập (1, 2, 3...):* Bắt đầu từ `LỜI CẢM ƠN` (trang 1) $\rightarrow$ `LỜI MỞ ĐẦU` (trang 2) $\rightarrow$ `CHƯƠNG 1` (trang 3 trở đi).
   * *Quyết định kỹ thuật:* Điều chỉnh cấu trúc `main.tex` khớp 100% với Hình 2 thực tế của Khoa CNTT HUMG. Section 5.1 và 5.2 đã được đồng bộ hóa hoàn toàn theo thứ tự này.

