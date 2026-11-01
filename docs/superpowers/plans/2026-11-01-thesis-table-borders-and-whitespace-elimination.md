# Kế hoạch Thực hiện Chuẩn hóa Khung viền Bảng biểu và Khắc phục Khoảng trắng thừa

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển đổi toàn bộ bảng biểu trong đồ án sang dạng khung lưới ô khép kín 4 góc (`|...|` và `\hline`), đồng thời loại bỏ triệt để các khoảng trắng thừa lớn giữa văn bản và hình ảnh bằng cách dỡ bỏ 28 lệnh `\clearpage` cưỡng bức và tối ưu hóa tỷ lệ float hình ảnh.

**Architecture:** Sử dụng `tabularx` có vạch biên đứng `|` và `\hline` phân cách từng dòng cho các bảng rộng; loại bỏ các lệnh ngắt trang cứng `\clearpage` trong thân các tiểu mục; chuyển đổi thuộc tính float hình ảnh từ `[H]` sang `[htbp]` kết hợp tinh chỉnh tỷ lệ `width=0.78\textwidth` để dòng chảy văn bản tự nhiên điền đầy các trang trống.

**Tech Stack:** XeLaTeX, LaTeX (`tabularx`, `graphicx`, `needspace`), Python 3.12 (kiểm thử định dạng tự động với `pytest`).

**Spec:** `docs/superpowers/specs/2026-11-01-thesis-table-borders-and-whitespace-elimination-design.md`

## Global Constraints

- Phông chữ chuẩn: Times New Roman 13pt (`fontspec` + `scrextend`).
- Dãn dòng: 1,5 lines (`\onehalfspacing` trong `setspace`).
- Lề trang: Top 2.5cm, Bottom 2.5cm, Left 3.5cm, Right 2.5cm (`geometry`).
- Số trang: Đánh ở chân trang góc phải (`\fancyfoot[R]`), không in nghiêng (`\thepage`).
- Bảng biểu: Khung viền khép kín 4 góc ngoài và các vạch kẻ ô ngang/dọc bên trong, không dùng `booktabs` hở cạnh (`\toprule`, `\midrule`, `\bottomrule`).

## Review Focus

- Bảng 1-1 không còn bất kỳ lệnh `\toprule`, `\midrule`, `\bottomrule` nào, các ô đều có vạch ngăn cách.
- Các tiểu mục trong `chapters/ch4/4_2_giao_dien.tex` không còn `\clearpage`, chữ và hình ảnh chảy liền mạch.
- Trang 98 (Hình 4-6) không còn khoảng trắng khổng lồ; tiểu mục 4.2.1.6 hoặc nội dung tiếp nối lập tức xuất hiện ngay dưới hình nếu đủ không gian.
- Các chương 2 và 3 được dỡ bỏ các `\clearpage` dư thừa không có lý do sư phạm hay ngắt chương.
- Quá trình biên dịch XeLaTeX kết thúc với Exit code 0, không có trang nào bị lỗi chồng chữ hay tràn lề nghiêm trọng.

---

### Task 1: Xây dựng Kịch bản Kiểm thử Định dạng Bảng và Khoảng trắng (TDD)

**Files:**
- Create: `report-datn/scripts/test_tables_and_spacing.py`

**Interfaces:**
- Consumes: Toàn bộ mã nguồn `.tex` trong `report-datn/chapters/`.
- Produces: Test suite tự động kiểm tra cú pháp bảng viền 4 góc và việc loại bỏ `\clearpage` bất hợp lý.

- [ ] **Step 1: Viết test kiểm tra Bảng không dùng `booktabs` hở cạnh và không còn `\clearpage` trong các tiểu mục giao diện**

```python
import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "chapters"

def test_no_booktabs_rules():
    """Đảm bảo không còn \\toprule, \\midrule, \\bottomrule trong các file chương."""
    for tex_file in CHAPTERS_DIR.glob("**/*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        assert "\\toprule" not in content, f"Phát hiện \\toprule trong {tex_file.name}"
        assert "\\midrule" not in content, f"Phát hiện \\midrule trong {tex_file.name}"
        assert "\\bottomrule" not in content, f"Phát hiện \\bottomrule trong {tex_file.name}"

def test_ch4_ui_no_unnecessary_clearpage():
    """Đảm bảo không còn \\clearpage cưỡng bức giữa các tiểu mục giao diện trong 4_2_giao_dien.tex."""
    ui_tex = CHAPTERS_DIR / "ch4" / "4_2_giao_dien.tex"
    content = ui_tex.read_text(encoding="utf-8")
    clearpage_count = len(re.findall(r"\\clearpage", content))
    assert clearpage_count == 0, f"4_2_giao_dien.tex vẫn còn {clearpage_count} lệnh \\clearpage"
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (Red)**

Run: `pytest report-datn/scripts/test_tables_and_spacing.py -v`
Expected: FAIL với phát hiện `\toprule` trong `1_2_tinh_cap_thiet.tex` và 11 lệnh `\clearpage` trong `4_2_giao_dien.tex`.

- [ ] **Step 3: Commit kịch bản kiểm thử TDD ban đầu**

```bash
git add report-datn/scripts/test_tables_and_spacing.py
git commit -m "test(datn): add failing test for table borders and clearpage spacing"
```

---

### Task 2: Chuẩn hóa Khung viền Toàn diện cho Bảng 1-1 và Rà soát Bảng toàn Đồ án

**Files:**
- Modify: `report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex:16-41`
- Test: `report-datn/scripts/test_tables_and_spacing.py`

**Interfaces:**
- Consumes: Cấu hình `tabularx` trong `preamble.tex`.
- Produces: `Bảng 1-1` có khung viền 4 cạnh khép kín (`|...|`) và các đường `\hline` giữa tất cả các hàng.

- [ ] **Step 1: Cập nhật Bảng 1-1 trong `1_2_tinh_cap_thiet.tex` sang định dạng lưới khép kín**

Thay thế `\toprule`, `\midrule`, `\bottomrule`, `\addlinespace` bằng vạch biên dọc `|` và `\hline`:
```latex
\begin{table}[htbp]
\centering
\caption{Đối chiếu năng lực kỹ thuật giữa các công cụ hỗ trợ nghiên cứu học thuật hiện có và hệ thống VeriScholar}
\label{tab:related_systems_comparison}
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\renewcommand{\arraystretch}{1.22}
\begin{tabularx}{\textwidth}{|>{\bfseries\raggedright\arraybackslash}p{2.3cm}|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|}
\hline
\textbf{Nền tảng} & \textbf{Định vị tọa độ PDF 2 cột} & \textbf{Truy xuất lai Hybrid RRF \& Cross-Encoder} & \textbf{Đồ thị tri thức 4 thực thể \& Wiki} & \textbf{Tự sửa lỗi biên dịch LaTeX (ReAct)} & \textbf{Quản lý khóa BYOK AES-256-GCM} \tabularnewline \hline
ChatPDF & Chỉ dẫn chiếu mức số trang, mất cấu trúc 2 cột & Chỉ dùng tìm kiếm vector đơn luồng & Không hỗ trợ & Không hỗ trợ soạn thảo LaTeX & Không hỗ trợ khóa riêng \tabularnewline \hline
NotebookLM & Trích dẫn đoạn văn bản phẳng, không tô sáng hộp tọa độ PDF & Truy xuất ngữ cảnh dài độc quyền (đóng) & Bản đồ khái niệm tóm tắt cơ bản & Không hỗ trợ biên dịch LaTeX & Không hỗ trợ khóa riêng \tabularnewline \hline
Elicit & Trích xuất bảng tóm tắt, thiếu khung tọa độ hình học trên trang & Tìm kiếm ngữ nghĩa kết hợp lọc siêu dữ liệu & Ma trận khái niệm theo cột, không có đồ thị liên kết & Không hỗ trợ soạn thảo LaTeX & Không hỗ trợ khóa riêng \tabularnewline \hline
SciSpace & Hỗ trợ quét vùng chọn thủ công trên trang PDF & Tìm kiếm lai cơ bản trên kho công khai & Liên kết trích dẫn bài báo, chưa tách 4 thực thể & Có mẫu văn bản, không tự sửa lỗi biên dịch & Không hỗ trợ khóa riêng \tabularnewline \hline
Overleaf & Không tích hợp trình đọc hỏi đáp tài liệu RAG & Không có phân hệ truy xuất tri thức học thuật & Không hỗ trợ đồ thị tri thức & Báo lỗi dòng nhật ký thô, gợi ý thủ công & Không hỗ trợ BYOK \tabularnewline \hline
\VS\ (Đề tài) & Ánh xạ tọa độ chuẩn hóa trên PDF 2 cột ($\text{IoU} = 0{,}9266$) & Hybrid RRF ($k=60$) kết hợp Cross-Encoder & Đồ thị 4 thực thể trên PostgreSQL \& Wiki cộng đồng & Agentic ReAct tự sửa lỗi trong E2B Sandbox ($96\%$) & Mã hóa AES-256-GCM, giải mã tạm thời trên RAM \tabularnewline \hline
\end{tabularx}
\end{table}
```

- [ ] **Step 2: Chạy kiểm tra test `test_no_booktabs_rules`**

Run: `pytest report-datn/scripts/test_tables_and_spacing.py -k test_no_booktabs_rules -v`
Expected: PASS

- [ ] **Step 3: Commit thay đổi chuẩn hóa viền Bảng 1-1**

```bash
git add report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex
git commit -m "fix(datn): enforce full grid border with hline on table 1-1"
```

---

### Task 3: Xóa bỏ `\clearpage` Cưỡng bức và Tối ưu Hình ảnh trong Mục Giao diện Chương 4

**Files:**
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex`
- Test: `report-datn/scripts/test_tables_and_spacing.py`

**Interfaces:**
- Consumes: Cấu hình float và hình ảnh trong `report-datn`.
- Produces: Dòng chảy văn bản liền mạch trong toàn bộ mục 4.2 Giao diện, loại bỏ khoảng trắng trang 98.

- [ ] **Step 1: Gỡ bỏ 11 lệnh `\clearpage` trong `4_2_giao_dien.tex`**

Xóa bỏ các lệnh `\clearpage` tại các dòng 115, 128, 141, 160, 179, 192, 210, 228, 241, 258, 275.
Thêm `\Needspace{5\baselineskip}` trước các tiêu đề `\subsubsection` khi cần thiết để chống mồ côi tiêu đề sát đáy trang mà không ngắt trang sớm.

- [ ] **Step 2: Điều chỉnh float và kích thước hình ảnh UI**

Chuyển đổi các khối `\begin{figure}[H]` thành `\begin{figure}[htbp]`, và chỉnh `width=0.90\textwidth` thành `width=0.78\textwidth` (hoặc `width=0.80\textwidth`) cho các hình giao diện từ Hình 4-2 đến Hình 4-11.

- [ ] **Step 3: Chạy test `test_ch4_ui_no_unnecessary_clearpage`**

Run: `pytest report-datn/scripts/test_tables_and_spacing.py -k test_ch4_ui_no_unnecessary_clearpage -v`
Expected: PASS

- [ ] **Step 4: Commit thay đổi mục giao diện Chương 4**

```bash
git add report-datn/chapters/ch4/4_2_giao_dien.tex
git commit -m "fix(datn): eliminate clearpage and optimize figure widths in ch4 UI"
```

---

### Task 4: Dỡ bỏ `\clearpage` Dư thừa trong Chương 2 và Chương 3

**Files:**
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex`
- Modify: `report-datn/chapters/ch2/2_3_advanced_rag.tex`
- Modify: `report-datn/chapters/ch2/2_4_knowledge_graph_wiki.tex`
- Modify: `report-datn/chapters/ch3/3_3_tac_nhan_usecase.tex`
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`
- Modify: `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`
- Test: `report-datn/scripts/test_tables_and_spacing.py`

**Interfaces:**
- Consumes: Cấu trúc văn bản và hình vẽ Chương 2 và 3.
- Produces: Dòng chảy văn bản liền mạch không bị ngắt quãng giữa các bảng/hình và văn bản phân tích.

- [ ] **Step 1: Bổ sung test kiểm tra các `\clearpage` dư thừa ở Chương 2 và Chương 3 vào `test_tables_and_spacing.py`**

Thêm hàm kiểm tra bảo đảm không còn `\clearpage` nội bộ trong `ch2/2_5_agentic_react.tex` và `ch3/3_5_bieu_do_tuan_tu.tex`.

- [ ] **Step 2: Dỡ bỏ các lệnh `\clearpage` không cần thiết trong Chương 2 và Chương 3**

Gỡ bỏ 7 `\clearpage` trong `2_5_agentic_react.tex`, 3 `\clearpage` trong `3_5_bieu_do_tuan_tu.tex`, và các `\clearpage` sau các bảng trong `3_3_tac_nhan_usecase.tex`, `3_4_phan_tich_usecase.tex`, `3_6_thiet_ke_csdl.tex`.

- [ ] **Step 3: Chạy test toàn diện**

Run: `pytest report-datn/scripts/test_tables_and_spacing.py -v`
Expected: PASS 100%

- [ ] **Step 4: Commit thay đổi Chương 2 và Chương 3**

```bash
git add report-datn/chapters/ch2/ report-datn/chapters/ch3/ report-datn/scripts/test_tables_and_spacing.py
git commit -m "fix(datn): remove extraneous clearpage calls in ch2 and ch3"
```

---

### Task 5: Biên dịch XeLaTeX, Kiểm chứng Bố cục Trang in và Hồi quy Định dạng

**Files:**
- Test: `report-datn/main.pdf`
- Test: `report-datn/scripts/test_preamble_config.py`
- Test: `report-datn/scripts/verify_thesis_format.py`

**Interfaces:**
- Consumes: Mã nguồn hoàn chỉnh sau khi chỉnh sửa Bảng 1-1 và gỡ bỏ `\clearpage`.
- Produces: Bản PDF đồ án `main.pdf` hoàn chỉnh, không còn khoảng trống lớn, bố cục chặt chẽ.

- [ ] **Step 1: Biên dịch toàn bộ đồ án bằng XeLaTeX**

Run: `cd report-datn && latexmk -xelatex -interaction=nonstopmode main.tex`
Expected: Exit code 0, sinh ra `main.pdf`.

- [ ] **Step 2: Kiểm tra bố cục trang 98 (và các trang lân cận) bằng `pdftotext`**

Run: `pdftotext -f 95 -l 105 report-datn/main.pdf - | grep -E "Hình 4-6|4.2.1.6"`
Expected: Xác nhận `Hình 4-6` và tiêu đề mục `4.2.1.6` được bố trí liền mạch, không còn bị ngắt trang bỏ trống nửa trang như bản in cũ.

- [ ] **Step 3: Chạy toàn bộ bộ test kiểm thử hồi quy**

Run: `pytest report-datn/scripts/ -v`
Expected: Toàn bộ các test (Preamble, Format, Tables & Spacing) đạt 100% PASS.

- [ ] **Step 4: Commit và hoàn tất nhánh**

```bash
git add report-datn/
git commit -m "chore(datn): verify thesis compilation and natural page flow"
```
