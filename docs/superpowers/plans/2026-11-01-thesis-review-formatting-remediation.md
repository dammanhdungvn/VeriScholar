# Chuẩn hóa Định dạng Báo cáo Đồ án Tốt nghiệp theo Review của GVHD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuẩn hóa toàn bộ định dạng và quy cách trình bày của báo cáo đồ án tốt nghiệp `report-datn/main.pdf` theo đúng 8 góp ý của Giảng viên hướng dẫn: dãn dòng 1.5 lines thống nhất; đổi nhiệm vụ sang bullet; số trang đứng góc dưới phải; bỏ toàn bộ header/footer; mục lục tối đa 3 mức không dấu chấm/hai chấm; LoF/LoT không in đậm chữ/số; chuẩn hóa tên "Bộ môn Hệ thống thông tin và Tri thức"; làm sạch chữ in đậm tùy tiện trong phần thân.

**Architecture:** Cấu hình tập trung trong `report-datn/config/preamble.tex` (`fancyhdr`, `tocloft`, `titlesec`, `setspace`). Tinh chỉnh hồ sơ hành chính `phieu_giao_de_tai.tex` và `de_cuong_datn.tex` để dãn dòng 1.5 lines tự nhiên mà vẫn vừa khít khuôn 3 trang truyền thống. Rà soát làm sạch `\textbf` nội dòng trong `frontmatter/` và `chapters/`.

**Tech Stack:** XeLaTeX, `setspace`, `tocloft`, `fancyhdr`, `geometry`, `latexmk`, Python verification scripts.

**Spec:** `docs/superpowers/specs/2026-11-01-thesis-review-formatting-remediation-design.md`

## Global Constraints

- Phông chữ Times New Roman 13pt (`scrextend`), dãn dòng 1.5 lines (`\onehalfspacing`), không dùng lệnh ép co dãn dòng cục bộ (`\setstretch` nhỏ hơn 1.3).
- Lề trang chuẩn HUMG: Trên 2.5cm, Dưới 2.5cm, Trái 3.5cm, Phải 2.5cm (`geometry`).
- Số trang đặt dưới cùng góc phải mỗi trang, kiểu chữ đứng thẳng (không `\textit`), La Mã thường cho hồ sơ trước Mục lục và Ả Rập bắt đầu từ Lời cảm ơn.
- Tên Bộ môn chính xác: "Bộ môn Hệ thống thông tin và Tri thức" (chữ hoa: "BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC").
- Biên dịch sạch không lỗi (`xelatex` / `latexmk -xelatex`).

## Review Focus

1. Mục lục (ToC): Chỉ chứa Chapter (CHƯƠNG), Section (1.1) và Subsection (1.1.1); không có cấp 4 (1.1.1.1). Không có dấu chấm sau số mục (`2.1 Tổng quan`) và không có dấu hai chấm sau tên chương (`CHƯƠNG 1 `).
2. Danh mục Hình & Bảng: Chữ "Hình", "Bảng" và số thứ tự không in đậm (`\normalfont`), không có dấu hai chấm (`Hình 1-1 ` thay vì `Hình 1-1:`).
3. Header & Footer: Không còn dòng "Đồ án tốt nghiệp...", không còn dòng "SVTH: Đàm Mạnh Dũng...", không còn đường kẻ đôi `\headrule` hay `\footrule`. Chân trang chỉ có số trang ở lề phải.
4. Phiếu giao đề tài & Đề cương: Trình bày đẹp mắt, chuẩn dãn dòng 1.5 lines, các nhiệm vụ dùng gạch đầu dòng bullet, không có hiện tượng "sau:" rớt dòng lẻ loi, bố cục vừa khít đúng 3 trang mỗi biểu mẫu.
5. In đậm phần thân: Không còn in đậm tùy tiện các từ khóa như `\textbf{VeriScholar}`, `\textbf{Vũ Lan Phương}`, `\textbf{hiện tượng ảo giác...}` trong các đoạn văn thông thường.

---

### Task 1: Chuẩn hóa cấu hình Preamble (`preamble.tex`)

**Files:**
- Modify: `report-datn/config/preamble.tex:101-215`

**Interfaces:**
- Consumes: Cấu hình `preamble.tex` hiện tại
- Produces: 
  - `fancyhdr`: Header rỗng, footer chỉ có `\thepage` (upright, no rule)
  - `tocdepth`: 2 (bỏ cấp 4)
  - `cftchapaftersnum`: `\ ` (bỏ `:`)
  - `cftsecaftersnum`: `{}` (bỏ `.`)
  - `cftsubsecaftersnum`: `{}` (bỏ `.`)
  - `cfttabpresnum` & `cftfigpresnum`: font thường (bỏ `\bfseries`)
  - `cfttabaftersnum` & `cftfigaftersnum`: `\ ` (bỏ `:`)

- [ ] **Step 1: Viết test kiểm tra cấu hình Preamble**

Tạo script `scripts/test_preamble_config.py` kiểm tra nội dung file `preamble.tex`:
```python
import re
from pathlib import Path

def test_preamble():
    content = Path("report-datn/config/preamble.tex").read_text(encoding="utf-8")
    assert "\\textit{\\thepage}" not in content, "Số trang vẫn còn in nghiêng"
    assert "cftsecaftersnum}{.}" not in content, "Mục lục section vẫn còn dấu chấm"
    assert "cftsubsecaftersnum}{.}" not in content, "Mục lục subsection vẫn còn dấu chấm"
    assert "cftchapaftersnum}{:\\" not in content, "Mục lục chapter vẫn còn dấu hai chấm"
    assert "cfttabpresnum}{\\bfseries" not in content, "LoT chữ Bảng vẫn còn in đậm"
    assert "cftfigpresnum}{\\bfseries" not in content, "LoF chữ Hình vẫn còn in đậm"
    assert "tocdepth}{2}" in content, "tocdepth phải là 2"
    assert "Đồ án tốt nghiệp ngành Công nghệ thông tin" not in content, "Header cũ vẫn tồn tại"
```

- [ ] **Step 2: Chạy test để xác nhận test FAIL với cấu hình cũ**

Run: `python3 scripts/test_preamble_config.py`
Expected: FAIL (nhiều assertion không thỏa mãn).

- [ ] **Step 3: Cập nhật `report-datn/config/preamble.tex`**

1. Cập nhật `\setupdatnheaders` và `adminform`:
   - Bỏ nội dung `\fancyhead[L]` và `\fancyfoot[L]`.
   - Đặt `\fancyfoot[R]{\fontsize{10}{12}\selectfont\thepage}`.
   - Đặt `\headrulewidth{0pt}`, `\footrulewidth{0pt}`, `\headrule` rỗng, `\footrule` rỗng.
2. Cập nhật Mục lục:
   - `\setcounter{tocdepth}{2}`.
   - `\renewcommand{\cftchapaftersnum}{\ }`.
   - `\settowidth{\cftchaplen}{\bfseries CHƯƠNG 1\ }`.
   - `\renewcommand{\cftsecaftersnum}{}`.
   - `\settowidth{\cftseclen}{1.1\ }`.
   - `\renewcommand{\cftsubsecaftersnum}{}`.
   - `\settowidth{\cftsubseclen}{2.1.1\ }`.
3. Cập nhật Danh mục Bảng & Hình:
   - `\renewcommand{\cfttabpresnum}{Bảng~}`.
   - `\renewcommand{\cfttabaftersnum}{\ }`.
   - `\settowidth{\cfttablen}{Bảng~9-99\ }`.
   - `\renewcommand{\cftfigpresnum}{Hình~}`.
   - `\renewcommand{\cftfigaftersnum}{\ }`.
   - `\settowidth{\cftfiglen}{Hình~9-99\ }`.

- [ ] **Step 4: Chạy lại test để xác nhận PASS**

Run: `python3 scripts/test_preamble_config.py`
Expected: PASS không báo lỗi nào.

- [ ] **Step 5: Commit thay đổi Task 1**

```bash
git add report-datn/config/preamble.tex scripts/test_preamble_config.py
git commit -m "style(datn): update preamble headers, footers, tocdepth and cft formats"
```

---

### Task 2: Chuẩn hóa Phiếu giao đề tài tốt nghiệp (`phieu_giao_de_tai.tex`)

**Files:**
- Modify: `report-datn/frontmatter/phieu_giao_de_tai.tex`

**Interfaces:**
- Consumes: `report-datn/frontmatter/phieu_giao_de_tai.tex`
- Produces: 
  - Đổi enumerate nhiệm vụ sang itemize (bullet `--`)
  - Bỏ `\setstretch{1.10}` và các `\vspace` thủ công gây ngắt chữ
  - Bố cục gọn gàng, súc tích vừa khít đúng 3 trang (iii, iv, v)
  - Tên Bộ môn chính xác "Bộ môn Hệ thống thông tin và Tri thức"

- [ ] **Step 1: Viết test kiểm tra nội dung `phieu_giao_de_tai.tex`**

Thêm hàm `test_phieu_giao_de_tai()` vào `scripts/test_preamble_config.py`:
- Kiểm tra không còn `\begin{enumerate}` trong mục 3 nhiệm vụ cụ thể.
- Kiểm tra có `\begin{itemize}` với `\item[--]`.
- Kiểm tra không còn `\setstretch{1.10}`.
- Kiểm tra không còn từ "sau:" đứng đơn độc một dòng.

- [ ] **Step 2: Chạy test để xác nhận FAIL**

Run: `python3 scripts/test_preamble_config.py`
Expected: FAIL.

- [ ] **Step 3: Biên tập và cập nhật `report-datn/frontmatter/phieu_giao_de_tai.tex`**

1. Bỏ bọc `{\setstretch{1.10} ... }`.
2. Thay thế `\begin{enumerate} ... \end{enumerate}` ở mục 3 bằng `\begin{itemize}[leftmargin=*, itemsep=2pt, topsep=2pt] \item[--] ... \end{itemize}`.
3. Ghép câu giới thiệu: "Để hoàn thành các mục tiêu đề ra, sinh viên thực hiện các nhiệm vụ cụ thể sau:" thành một khối không bị ngắt chữ "sau:" sang dòng mới.
4. Cô đọng 8 gạch đầu dòng nhiệm vụ và các mục tiêu để trang 1 (iii), trang 2 (iv), trang 3 (v) tự nhiên, vừa khít, chữ ký nằm trọn vẹn ở cuối trang v.

- [ ] **Step 4: Chạy test để xác nhận PASS**

Run: `python3 scripts/test_preamble_config.py`
Expected: PASS.

- [ ] **Step 5: Commit thay đổi Task 2**

```bash
git add report-datn/frontmatter/phieu_giao_de_tai.tex scripts/test_preamble_config.py
git commit -m "style(datn): modernize phieu giao de tai with bullets and clean 1.5 line spacing"
```

---

### Task 3: Chuẩn hóa Đề cương đồ án tốt nghiệp (`de_cuong_datn.tex`)

**Files:**
- Modify: `report-datn/frontmatter/de_cuong_datn.tex`

**Interfaces:**
- Consumes: `report-datn/frontmatter/de_cuong_datn.tex`
- Produces: 
  - Tiêu ngữ chuẩn: "BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC"
  - Bỏ toàn bộ `\setstretch` co ép (`1.06`, `1.05`, `1.12`)
  - Bố cục 3 trang (vi, vii, viii) cân đối, bảng 10 tuần nằm gọn trong trang viii

- [ ] **Step 1: Viết test kiểm tra nội dung `de_cuong_datn.tex`**

Thêm hàm `test_de_cuong_datn()` vào `scripts/test_preamble_config.py`:
- Kiểm tra tiêu ngữ có "BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC".
- Kiểm tra bảng kế hoạch tuần 10 có "Bộ môn Hệ thống thông tin và Tri thức" (hoặc Tri Thức).
- Kiểm tra không còn `\setstretch{1.06}`, `\setstretch{1.05}`, `\setstretch{1.12}`.

- [ ] **Step 2: Chạy test để xác nhận FAIL**

Run: `python3 scripts/test_preamble_config.py`
Expected: FAIL.

- [ ] **Step 3: Cập nhật `report-datn/frontmatter/de_cuong_datn.tex`**

1. Chỉnh tiêu ngữ:
   ```latex
   \textbf{KHOA CÔNG NGHỆ THÔNG TIN}\\[2pt]
   \textbf{BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC}
   ```
2. Bỏ các lệnh `\setstretch{...}` cục bộ.
3. Tinh chỉnh độ dài phần lý do chọn đề tài và các mục tiêu/nhiệm vụ để trang 1 (vi), trang 2 (vii) và bảng kế hoạch 10 tuần + chữ ký ở trang 3 (viii) hoàn hảo, không bị tràn.

- [ ] **Step 4: Chạy test để xác nhận PASS**

Run: `python3 scripts/test_preamble_config.py`
Expected: PASS.

- [ ] **Step 5: Commit thay đổi Task 3**

```bash
git add report-datn/frontmatter/de_cuong_datn.tex scripts/test_preamble_config.py
git commit -m "style(datn): standardize de cuong datn header and spacing"
```

---

### Task 4: Làm sạch in đậm và chuẩn hóa Bộ môn trong Lời cảm ơn & Lời mở đầu

**Files:**
- Modify: `report-datn/frontmatter/loi_cam_on.tex`
- Modify: `report-datn/frontmatter/loi_mo_dau.tex`

**Interfaces:**
- Consumes: `frontmatter/loi_cam_on.tex`, `frontmatter/loi_mo_dau.tex`
- Produces: 
  - `loi_cam_on.tex`: Tên GVHD "cô Vũ Lan Phương", tên hệ thống "VeriScholar" (không in đậm); tên Bộ môn: "Bộ môn Hệ thống thông tin và Tri thức"
  - `loi_mo_dau.tex`: "hiện tượng ảo giác trích dẫn (\textit{Citation Hallucination})" (không in đậm)

- [ ] **Step 1: Viết test kiểm tra `loi_cam_on.tex` và `loi_mo_dau.tex`**

Thêm hàm `test_frontmatter_bolds()` vào `scripts/test_preamble_config.py`:
- Kiểm tra không còn `\textbf{Vũ Lan Phương}` trong `loi_cam_on.tex`.
- Kiểm tra không còn `\textbf{VeriScholar}` hoặc `\textbf{\VS}` trong `loi_cam_on.tex`.
- Kiểm tra có "Bộ môn Hệ thống thông tin và Tri thức".
- Kiểm tra không còn `\textbf{hiện tượng ảo giác` trong `loi_mo_dau.tex`.

- [ ] **Step 2: Chạy test để xác nhận FAIL**

Run: `python3 scripts/test_preamble_config.py`
Expected: FAIL.

- [ ] **Step 3: Chỉnh sửa `loi_cam_on.tex` và `loi_mo_dau.tex`**

1. Trong `report-datn/frontmatter/loi_cam_on.tex`:
   - Đổi `cô \textbf{Vũ Lan Phương}` thành `cô Vũ Lan Phương`.
   - Đổi `nền tảng \VS` thành `nền tảng VeriScholar` (nét thường).
   - Đổi `Bộ môn Hệ thống Thông tin và Tri Thức` thành `Bộ môn Hệ thống thông tin và Tri thức`.
2. Trong `report-datn/frontmatter/loi_mo_dau.tex`:
   - Đổi `\textbf{hiện tượng ảo giác trích dẫn (Citation Hallucination)}` thành `hiện tượng ảo giác trích dẫn (\textit{Citation Hallucination})`.
   - Quét và chuyển các từ ngữ in đậm nhấn mạnh câu khác về chữ thường hoặc in nghiêng.

- [ ] **Step 4: Chạy test để xác nhận PASS**

Run: `python3 scripts/test_preamble_config.py`
Expected: PASS.

- [ ] **Step 5: Commit thay đổi Task 4**

```bash
git add report-datn/frontmatter/loi_cam_on.tex report-datn/frontmatter/loi_mo_dau.tex scripts/test_preamble_config.py
git commit -m "style(datn): remove informal bolding and update department name in loi cam on and loi mo dau"
```

---

### Task 5: Rà soát và loại bỏ chữ in đậm tùy tiện trong 4 chương chính

**Files:**
- Modify: `report-datn/chapters/ch1/`
- Modify: `report-datn/chapters/ch2/`
- Modify: `report-datn/chapters/ch3/`
- Modify: `report-datn/chapters/ch4/`
- Modify: `report-datn/chapters/ket_luan.tex`

**Interfaces:**
- Consumes: Các tệp nguồn chương 1 đến kết luận
- Produces: Văn bản thuần học thuật, không có `\textbf` nội dòng cho thuật ngữ thông thường trong câu, giữ nguyên `\textbf` cho nhãn danh sách (`\item \textbf{Tên:}`) và tiêu đề bảng/hình

- [ ] **Step 1: Viết script quét các mẫu `\textbf` nội dòng đáng ngờ**

Tạo script `scripts/scan_inline_bolds.py`:
- Tìm các cụm `\textbf{...}` nằm giữa câu (trước hoặc sau có từ thường, không phải đầu `\item` hay trong môi trường `tabular`).
- Báo cáo danh sách các vị trí cần chuẩn hóa (như `\textbf{hiện tượng ảo giác trích dẫn}`, `\textbf{VeriScholar}`, `\textbf{Agentic RAG}`, `\textbf{GraphRAG}` khi dùng làm danh từ nội dòng).

- [ ] **Step 2: Chạy script quét hiện trạng**

Run: `python3 scripts/scan_inline_bolds.py`
Expected: Liệt kê các vị trí cần làm sạch trong `ch1`, `ch2`, `ch3`, `ch4`, `ket_luan`.

- [ ] **Step 3: Chỉnh sửa làm sạch các tệp chương**

Chuyển các `\textbf{...}` nội dòng thành chữ thường hoặc `\textit{...}` theo ngữ cảnh học thuật chuẩn.
Giữ nguyên:
- Nhãn đầu dòng có cấu trúc (ví dụ: `\item \textbf{Độ chính xác:}`).
- Cột tiêu đề trong bảng (`\textbf{STT}`, `\textbf{Chỉ số}`).
- Tiêu đề mục (`\section`, `\subsection`, `\paragraph`).

- [ ] **Step 4: Chạy lại script quét để xác nhận đã làm sạch**

Run: `python3 scripts/scan_inline_bolds.py`
Expected: 0 phát hiện lỗi in đậm tùy tiện nội dòng.

- [ ] **Step 5: Commit thay đổi Task 5**

```bash
git add report-datn/chapters/ scripts/scan_inline_bolds.py
git commit -m "style(datn): clean up casual inline bolds across chapters 1-4 and conclusion"
```

---

### Task 6: Biên dịch tổng thể XeLaTeX và nghiệm thu toàn diện

**Files:**
- Modify: `report-datn/main.pdf`
- Test: `scripts/verify_thesis_format.py`

**Interfaces:**
- Consumes: Toàn bộ mã nguồn `report-datn/` sau khi cập nhật
- Produces: `main.pdf` hoàn thiện 100% tuân thủ 8 tiêu chí phản hồi của GVHD

- [ ] **Step 1: Viết script nghiệm thu toàn diện `scripts/verify_thesis_format.py`**

Kiểm tra trực tiếp trên file PDF sinh ra bằng `pypdf` hoặc `pdftotext`:
1. Kiểm tra không có chuỗi `Đồ án tốt nghiệp ngành Công nghệ thông tin` ở đầu trang nào.
2. Kiểm tra không có chuỗi `SVTH: Đàm Mạnh Dũng` ở chân trang nào.
3. Kiểm tra số trang ở chân trang có dạng số đứng (kiểm tra font embedding hoặc layout).
4. Kiểm tra Mục lục trong `main.toc` không chứa `subsubsection` (mức 4).
5. Kiểm tra Mục lục không chứa dấu chấm sau section và không chứa dấu hai chấm sau chapter.
6. Kiểm tra `main.lof` và `main.lot` không chứa `\bfseries` và dấu hai chấm.

- [ ] **Step 2: Biên dịch đồ án bằng `latexmk`**

Run: `cd report-datn && latexmk -xelatex -interaction=nonstopmode main.tex`
Expected: Exit code 0, tạo ra `main.pdf` mới.

- [ ] **Step 3: Chạy script nghiệm thu toàn diện**

Run: `python3 scripts/verify_thesis_format.py`
Expected: Tất cả các bài kiểm tra đều PASS.

- [ ] **Step 4: Kiểm tra trực quan số trang của Phiếu giao đề tài và Đề cương**

Xác nhận:
- Phiếu giao đề tài: trang iii đến v (đúng 3 trang).
- Đề cương: trang vi đến viii (đúng 3 trang).
- Mục lục: bắt đầu từ trang ix.
- Lời cảm ơn: bắt đầu từ trang 1 (Ả Rập).

- [ ] **Step 5: Commit kết quả nghiệm thu cuối cùng**

```bash
git add report-datn/ scripts/verify_thesis_format.py
git commit -m "docs(datn): compile finalized thesis report with verified formatting"
```
