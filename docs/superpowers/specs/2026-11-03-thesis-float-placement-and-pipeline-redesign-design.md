# Đặc Tả Kỹ Thuật: Chuẩn Hóa Bố Cục Float Không Ngắt Câu, Nới Dài Thân Mũi Tên Hình 3-2 và Thiết Kế Lại Sơ Đồ Tuần Tự Thành Stage Cards Pipeline

> **Tài liệu tham chiếu:** `AGENTS.md`, `report-datn/AGENTS.md`  
> **Ngày lập:** 03/11/2026  
> **Trạng thái:** Approved by User  

---

## 1. Bối Cảnh & Mục Tiêu

Qua rà soát thực tế bản in PDF luận văn tốt nghiệp VeriScholar (`report-datn/main.pdf`), người dùng đã chỉ ra 3 vấn đề thị giác và bố cục cốt lõi:

1. **Vấn đề 1 (Float chèn cắt ngang câu văn):** Môi trường `figure[!htbp]` mặc định của LaTeX tự động đẩy float sang đầu trang tiếp theo khi trang hiện tại không đủ chỗ, trong khi dòng văn bản đang chảy ở trang trước bị cắt đôi giữa chừng (ví dụ: câu dẫn về khóa API của Tiểu mục 2.5.4 bị đứt ngang chữ *"như"*, Hình 2-4 chèn vào đầu trang 17, rồi câu văn viết tiếp *"gpt-4o-mini trên Microsoft Azure..."* ở đáy trang). Hiện tượng này xuất hiện tại nhiều hình trong toàn bộ 4 chương.
2. **Vấn đề 2 (Mũi tên Hình 3-2 bị cụt chỉ có đầu tam giác):** Khoảng cách giữa Core Domain ($x=\pm 4.5$), Ports ($x=\pm 5.85$) và Adapters ($x=\pm 8.8$) quá hẹp (chỉ hở $1.5\,\text{mm} - 2.5\,\text{mm}$), trong khi đầu mũi tên `Stealth` dài $2.2\,\text{mm}$, khiến toàn bộ các liên kết chỉ có đầu tam giác dính sát mép hộp mà không có thân đường thẳng (`-->`).
3. **Vấn đề 3 (Sơ đồ tuần tự Hình 3-9, 3-10, 3-11 quá rối và nhiều chữ):** Các biểu đồ tuần tự truyền thống có quá nhiều lifeline, nét đứt, hộp kích hoạt và nhãn tiếng Việt dài dòng, gây rối mắt và chiều cao quá lớn ($11 - 12\,\text{cm}$) dẫn đến việc nhảy trang và tạo khoảng trống đáy trang lớn. Người dùng yêu cầu thiết kế lại theo phương án trực quan, hiện đại, ít chữ, rõ ràng và không bị lỗi.

---

## 2. Giải Pháp Kỹ Thuật Chi Tiết

### 2.1. Giải pháp Vấn đề 1: Chuẩn hóa Định vị Float và Triệt tiêu 100% Cắt ngang câu
- Nạp gói `float` và `placeins` vào `report-datn/config/preamble.tex`:
  - `\usepackage{float}` cung cấp chỉ thị `[H]` (Here, strictly in-place), biến môi trường `figure` thành khối tĩnh không trôi dạt (non-floating block).
  - `\usepackage[section]{placeins}` và bổ sung chốt chặn `\FloatBarrier` trước các `\subsection` trọng yếu để ngăn chặn triệt để hiện tượng float nhảy cóc qua tiểu mục tiếp theo.
- Di dời khai báo `\begin{figure}` trong mã nguồn `.tex` luôn nằm sau đoạn văn hoàn chỉnh (kết thúc bằng dấu chấm câu `.`):
  - Hình 2-4 di dời về sau đoạn mô tả trọn vẹn của Mục 2.5.3, đứng trước `\FloatBarrier` và `\subsection{2.5.4}`.
  - Hình 3-1, Hình 3-2, Hình 3-3, Hình 4-4, Hình 4-7, Hình 4-9, Hình 4-10 được rà soát và cấu hình `[H]` / `\FloatBarrier` để văn bản trang trước luôn kết thúc bằng câu hoàn chỉnh.

### 2.2. Giải pháp Vấn đề 2: Nới rộng hình học và kéo dài thân mũi tên Hình 3-2
- Thu hẹp `minimum width` của `portbox` từ $2.4\,\text{cm}$ xuống $2.1\,\text{cm}$.
- Tinh chỉnh tọa độ:
  - Khung Core Domain: $x \in [-4.4, 4.4]$ (bề rộng $8.8\,\text{cm}$).
  - Driving Ports (Trái): $x = -6.1$ (mép phải tại $-5.05$, mép trái tại $-7.15$). Khoảng hở đến Core là $6.5\,\text{mm}$.
  - Driving Adapters (Trái): $x = -9.2$ (mép phải tại $-7.75$). Khoảng hở đến Port là $6.0\,\text{mm}$.
  - Driven Ports (Phải): $x = +6.1$ (mép trái tại $+5.05$, mép phải tại $+7.15$). Khoảng hở đến Core là $6.5\,\text{mm}$.
  - Driven Adapters (Phải): $x = +9.2$ (mép trái tại $+7.75$). Khoảng hở đến Port là $6.0\,\text{mm}$.
- Khoảng hở $6.0 - 6.5\,\text{mm}$ với đầu mũi tên $2.2\,\text{mm}$ bảo đảm tạo ra thân mũi tên thẳng dài $\ge 4.0\,\text{mm}$, hiển thị dạng `-->` sắc nét, tách biệt hoàn toàn giữa các tầng kiến trúc.

### 2.3. Giải pháp Vấn đề 3: Thiết kế lại Sơ đồ tuần tự sang Horizontal Stage Cards Pipeline
Thay thế mô hình tuần tự lifeline truyền thống bằng **Horizontal Stage Cards Pipeline** gồm các thẻ ngang trực quan nối tiếp:
- **Hình 3-8 (Tra cứu và Tải tài liệu CAS):**
  - Thẻ 1: Học giả nhập từ khóa/DOI $\to$ Thẻ 2: Đa nguồn arXiv/CrossRef $\to$ Thẻ 3: Deduplication SHA-256 CAS $\to$ Thẻ 4: Lưu trữ & Chỉ mục CSDL $\to$ Thẻ 5: Thư viện nghiên cứu.
- **Hình 3-9 (Hỏi đáp Đọc sâu & Minh chứng BBox):**
  - Thẻ 1: Truy vấn nghiên cứu $\to$ Thẻ 2: Hybrid RAG (HNSW + BM25) $\to$ Thẻ 3: Cổng CRAG & Re-ranking $\to$ Thẻ 4: Luồng SSE & BBox $1\,\text{s}$.
- **Hình 3-10 (Đồ thị tri thức GraphRAG & Truy vấn 2-hop):**
  - Thẻ 1: Trích xuất 4 Thực thể $\to$ Thẻ 2: Khử trùng Cosine $\ge 0{,}90 \to$ Thẻ 3: Phân cụm Louvain $\to$ Thẻ 4: Truy vấn Wiki 2-hop CTE.
- **Hình 3-11 (Biên soạn Monaco & Tự sửa lỗi LaTeX):**
  - Thẻ 1: Bản thảo Monaco $\to$ Thẻ 2: Sandbox E2B MicroVM $\to$ Thẻ 3: Phân tích Log lỗi $\to$ Thẻ 4: ReAct Agent vá mã ($N \le 3$) $\to$ Thẻ 5: PDF Hoàn chỉnh.
- Mỗi sơ đồ có chiều cao chỉ $3.5 - 4.5\,\text{cm}$, sử dụng các khối màu học thuật chuẩn (`blue!10`, `teal!10`, `purple!10`, `orange!10`), phông chữ $7-8\,\text{pt}$ cô đọng, mũi tên ngang dày `-{Stealth[length=2.5mm]}` rõ ràng. Chiều cao nhỏ giúp sơ đồ nằm gọn gàng ngay dưới tiêu đề tiểu mục, triệt tiêu 100% hiện tượng nhảy trang hay khoảng trống đáy trang.

---

## 3. Tiêu Chuẩn Nghiệm Thu (Acceptance Criteria)
1. **Pytest:** `uv run pytest` vượt qua 100% các bài test (bao gồm các assertion mới trong `tests/report_datn/test_diagram_bounds.py` và `test_layout_spacing.py`).
2. **XeLaTeX:** `latexmk -xelatex -interaction=nonstopmode main.tex` biên dịch thành công exit code 0, không có overfull hbox nghiêm trọng.
3. **Format Checker:** `python scripts/verify_thesis_format.py` đạt 100% chuẩn định dạng.
4. **Không ngắt câu:** Quét toàn bộ PDF xác nhận không còn bất kỳ câu văn nào bị ngắt đôi bởi hình chèn ở đầu trang.
5. **Trực quan:** Render ảnh PNG kiểm chứng chất lượng Hình 3-2, 3-8, 3-9, 3-10, 3-11.
