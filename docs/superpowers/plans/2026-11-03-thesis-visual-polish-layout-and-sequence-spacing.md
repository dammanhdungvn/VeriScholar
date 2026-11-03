# Thesis Visual Polish, Use Case Ordering & Layout Spacing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khắc phục triệt để khiếm khuyết đồ họa trên Hình 3-2 (tràn lề phải), Hình 2-4 (cắt cụt đỉnh vòng lặp đỏ và nhãn dính hình thoi), Hình 3-12 (nhãn bản số đè chữ và đường đâm xuyên hộp); đảo vị trí Hình 3-3 lên trước Bảng 3-1 trong Mục 3.4; triệt tiêu khoảng trắng hoang vu Trang 30 bằng cách chuyển Mục 3.5 sang đầu Trang 31; và nới khoảng cách dòng trong Hình 3-9, 3-10, 3-11 cùng khoảng đệm văn bản 0.5 dòng toàn hệ thống.

**Architecture:** Sử dụng kiến trúc Dynamic A4 Compact & Orthogonal Padding: thu hẹp tọa độ ngang TikZ của các Adapter từ $x = \pm 10.4$ về $\pm 8.8$ (scale 0.68); tái định vị cung tròn vòng lặp `to[out=110, in=250]` với nhãn có padding nền trắng; chuyển vị trí tiểu mục biểu đồ Use Case tổng quan lên 3.4.1 trước bảng đặc tả 3.4.2; ngắt trang sạch bằng `\clearpage` trước Section 3.5; tối ưu chiều cao hộp lớp UML bằng cách giảm inner sep và tinh chỉnh anchor bản số lệch sườn; nới bước dòng thông điệp tuần tự thêm $1.5\,\text{mm}$ và tăng khoảng đệm float đồng bộ trong `main.tex` và `preamble.tex`.

**Tech Stack:** XeLaTeX, TikZ / PGF, Python 3.12 (`pypdf`, `pdfplumber`, `pdftoppm`, `pdftotext`), pytest, Ruff.

**Spec:** [`../specs/2026-11-03-thesis-visual-polish-layout-and-sequence-spacing-design.md`](../specs/2026-11-03-thesis-visual-polish-layout-and-sequence-spacing-design.md)

## Global Constraints

- Chiều rộng bản in văn bản giới hạn nghiêm ngặt ở `\textwidth = 16.0cm` (A4 lề trái 3.0cm, lề phải 2.0cm).
- Tổng số trang toàn văn bản và số thứ tự trang mở đầu các chương phải bảo tồn chính xác theo quy chuẩn (`scripts/verify_thesis_format.py` exit code 0).
- Quy chuẩn Markdown Rule 5: Tuyệt đối dùng liên kết tương đối (`../...`, `./...`), cấm dùng URL tuyệt đối `file://`.
- Quy chuẩn Rule 6: Ngôn từ tối giản 80/20, chuẩn phong cách học thuật, không văn mẫu sáo rỗng.
- Quy chuẩn Rule 7: Tự động chạy `bash scripts/deploy_to_vps.sh --fast` sau mỗi commit.

## Review Focus

1. **Tràn lề phải Hình 3-2:** Sau khi thu hẹp tọa độ $x$, mép phải hộp Adapter xa nhất phải cách biên phải văn bản $\ge 5\,\text{mm}$.
2. **Cắt cụt đỉnh vòng lặp Hình 2-4:** Cung cong đỏ và chữ "Phản hồi vòng lặp" phải nằm trọn trong bounding box, nhãn rẽ nhánh không dính nét hình thoi.
3. **Thứ tự Use Case Mục 3.4:** Hình 3-3 (Biểu đồ) đứng trước Bảng 3-1 (Đặc tả danh mục), số thứ tự đề mục là 3.4.1 và 3.4.2 tương ứng.
4. **Khoảng trắng hoang vu Trang 30:** Mục 3.5 và Hình 3-8 bắt đầu ở đầu Trang 31, Trang 30 không còn hiện tượng tiêu đề mục nằm trơ trọi một nơi và hình ở một nẻo.
5. **Chồng đè nhãn bản số Hình 3-12:** Toàn bộ nhãn `{1}`, `{N}` và đầu mũi tên hình thoi không được đè lên bất kỳ ký tự tên lớp hay thuộc tính nào.

---

### Task 1: Tinh Chỉnh Hình 3-2 (Kiến Trúc Lục Giác Tổng Thể)

**Files:**
- Modify: `report-datn/chapters/ch3/3_3_kien_truc.tex:39-165`
- Test: `tests/report_datn/test_diagram_bounds.py`

**Interfaces:**
- Consumes: Cấu trúc 4 Không gian và các Port/Adapter hiện có trong `3_3_kien_truc.tex`.
- Produces: Sơ đồ TikZ Hình 3-2 thu gọn bề ngang từ $17.8\,\text{cm}$ xuống $15.2\,\text{cm}$, scale 0.68, căn lề trung tâm.

- [ ] **Step 1: Viết test kiểm tra kích thước và giới hạn biên lề của Hình 3-2**

Tạo file test `tests/report_datn/test_diagram_bounds.py`:
```python
from pathlib import Path


def test_fig3_2_coordinates_within_safe_margins():
    tex_path = Path("report-datn/chapters/ch3/3_3_kien_truc.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra scale đã giảm về 0.68
    assert "scale=0.68" in content, (
        "Hình 3-2 phải sử dụng scale=0.68 để vừa vặn lề in textwidth=16cm"
    )

    # Kiểm tra tọa độ Adapter không vượt quá +- 8.8 (trước đây là 10.4)
    assert "(10.4," not in content, (
        "Tọa độ x của Driven Adapter vẫn còn 10.4 gây tràn lề phải!"
    )
    assert "(-10.4," not in content, (
        "Tọa độ x của Driving Adapter vẫn còn -10.4!"
    )
    assert "(8.8," in content or "(8.80," in content, (
        "Thiếu tọa độ x=8.8 cho Driven Adapter"
    )
    assert "(-8.8," in content or "(-8.80," in content, (
        "Thiếu tọa độ x=-8.8 cho Driving Adapter"
    )
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig3_2_coordinates_within_safe_margins`
Expected: FAIL với AssertionError "Hình 3-2 phải sử dụng scale=0.68..."

- [ ] **Step 3: Cập nhật tọa độ và tỷ lệ scale cho Hình 3-2 trong `report-datn/chapters/ch3/3_3_kien_truc.tex`**

Thực hiện:
1. Đổi `scale=0.74` thành `scale=0.68`.
2. Đổi tọa độ Driving Ports từ `x = -6.8` về `x = -6.3`.
3. Đổi tọa độ Driven Ports từ `x = 6.8` về `x = 6.3`.
4. Đổi tọa độ Driving Adapters và actor từ `x = -10.4` về `x = -8.8`.
5. Đổi tọa độ Driven Adapters từ `x = 10.4` về `x = 8.8`.
6. Cập nhật nhãn Driving / Driven tại `x = \pm 6.3, y = 3.8`.
7. Đổi tọa độ mũi tên liên kết tương ứng nối giữa Core, Ports và Adapters.

- [ ] **Step 4: Chạy lại test để xác nhận test vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig3_2_coordinates_within_safe_margins`
Expected: PASS (1 passed).

- [ ] **Step 5: Biên dịch XeLaTeX kiểm tra không lỗi và render PNG kiểm chứng**

Run: `cd report-datn && xelatex -interaction=nonstopmode -file-line-error main.tex && cd .. && pdftoppm -png -r 150 -f 38 -l 38 report-datn/main.pdf /tmp/verify_fig3_2`
Expected: XeLaTeX exit 0; ảnh `/tmp/verify_fig3_2-38.png` hiển thị mép phải các khối Adapter cách lề phải $\ge 5\,\text{mm}$.

- [ ] **Step 6: Commit và đồng bộ VPS**

```bash
git add report-datn/chapters/ch3/3_3_kien_truc.tex tests/report_datn/test_diagram_bounds.py
git commit -m "fix(thesis): compact Fig 3-2 coordinates to eliminate right margin overflow"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Tinh Chỉnh Hình 2-4 (Vòng Lặp ReAct và MicroVM Sandbox)

**Files:**
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex:60-125`
- Test: `tests/report_datn/test_diagram_bounds.py`

**Interfaces:**
- Consumes: Cấu trúc sơ đồ ReAct trong `2_5_agentic_react.tex`.
- Produces: Hình 2-4 với cung tròn vòng lặp hạ đỉnh không vượt đỉnh bounding box, nhãn rẽ nhánh có nền trắng không dính nét hình thoi, đáy hình có đệm `\vspace{4pt}` trước caption.

- [ ] **Step 1: Bổ sung test kiểm tra các thông số hình học của Hình 2-4**

Thêm vào `tests/report_datn/test_diagram_bounds.py`:
```python
def test_fig2_4_loop_and_label_styling():
    tex_path = Path("report-datn/chapters/ch2/2_5_agentic_react.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra cung tròn vòng lặp đỏ không vồng quá cao
    assert "to[out=110, in=250]" in content or "to[out=115, in=245]" in content, (
        "Cung lặp đỏ cần dùng out=110, in=250 để không vượt quá đỉnh hộp agent"
    )

    # Kiểm tra nhãn rẽ nhánh có padding và fill=white
    assert "inner sep=2pt" in content, (
        "Nhãn rẽ nhánh hình thoi cần inner sep=2pt để không dính nét vẽ hình thoi"
    )

    # Kiểm tra có đệm vspace trước caption
    assert "\\vspace{4pt}" in content or "\\vspace{6pt}" in content, (
        "Cần vspace trước caption để tránh đáy hộp PDF dính sát caption"
    )
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig2_4_loop_and_label_styling`
Expected: FAIL với AssertionError.

- [ ] **Step 3: Cập nhật đường lặp, nhãn rẽ nhánh và đệm caption cho Hình 2-4 trong `report-datn/chapters/ch2/2_5_agentic_react.tex`**

Thực hiện:
1. Đổi cung lặp:
   `\draw[looparrow] (obs.north) to[out=110, in=250] node[midway, left=6pt, align=right, font=\scriptsize\bfseries, text=red!85!black, fill=white, inner sep=2pt] {Phản hồi vòng lặp\\sửa cú pháp} (agent.south);`
2. Đổi nhãn nhánh `No (Lỗi)`: thêm `fill=white, inner sep=2pt`.
3. Đổi nhãn `Trả kết quả`: thêm `fill=white, inner sep=2pt`.
4. Đổi nhãn nhánh `Yes (Exit 0)`: thêm `fill=white, inner sep=2pt`.
5. Thêm `\vspace{4pt}` ngay trước `\caption{...}`.

- [ ] **Step 4: Chạy lại test để xác nhận test vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig2_4_loop_and_label_styling`
Expected: PASS (1 passed).

- [ ] **Step 5: Biên dịch XeLaTeX và render PNG kiểm chứng**

Run: `cd report-datn && xelatex -interaction=nonstopmode -file-line-error main.tex && cd .. && pdftoppm -png -r 150 -f 32 -l 32 report-datn/main.pdf /tmp/verify_fig2_4`
Expected: XeLaTeX exit 0; ảnh `/tmp/verify_fig2_4-32.png` hiển thị cung đỏ nguyên vẹn đỉnh, các nhãn nhánh thoáng đãng.

- [ ] **Step 6: Commit và đồng bộ VPS**

```bash
git add report-datn/chapters/ch2/2_5_agentic_react.tex tests/report_datn/test_diagram_bounds.py
git commit -m "fix(thesis): polish Fig 2-4 loop arrow arc, decision labels and caption spacing"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Đảo Vị Trí Hình 3-3 (Use Case Diagram) Lên Trước Bảng 3-1 Trong Mục 3.4

**Files:**
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex:1-110`
- Test: `tests/report_datn/test_section_order.py`

**Interfaces:**
- Consumes: Cấu trúc 2 tiểu mục và các bảng/hình trong `3_4_phan_tich_usecase.tex`.
- Produces: Thứ tự chuẩn công nghệ phần mềm: Hình 3-3 đứng trước ở 3.4.1, Bảng 3-1 đứng sau ở 3.4.2.

- [ ] **Step 1: Viết test kiểm tra thứ tự tiểu mục và bảng/hình trong Mục 3.4**

Tạo file test `tests/report_datn/test_section_order.py`:
```python
from pathlib import Path


def test_usecase_diagram_precedes_table():
    tex_path = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Vị trí của biểu đồ Use Case tổng quan phải xuất hiện trước bảng đặc tả tác nhân
    fig_pos = content.find(
        "\\subsection{Biểu đồ Use Case tổng quan của hệ thống}"
    )
    tab_pos = content.find(
        "\\subsection{Các tác nhân và danh mục ca sử dụng của hệ thống}"
    )

    assert fig_pos != -1, "Không tìm thấy tiểu mục Biểu đồ Use Case tổng quan"
    assert tab_pos != -1, (
        "Không tìm thấy tiểu mục Các tác nhân và danh mục ca sử dụng"
    )
    assert fig_pos < tab_pos, (
        f"Biểu đồ Use Case (pos {fig_pos}) phải đứng trước Bảng tác nhân (pos {tab_pos})!"
    )

    # Nhắc đến Hình 3-3 trước Bảng 3-1 trong văn bản dẫn
    ref_fig_pos = content.find("\\ref{fig:usecase_overview}")
    ref_tab_pos = content.find("\\ref{tab:actors_usecases}")
    assert ref_fig_pos < ref_tab_pos, (
        "Tham chiếu Hình 3-3 phải xuất hiện trước tham chiếu Bảng 3-1"
    )
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_section_order.py`
Expected: FAIL với AssertionError.

- [ ] **Step 3: Đảo thứ tự hai tiểu mục trong `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`**

Thực hiện:
1. Đưa `\subsection{Biểu đồ Use Case tổng quan của hệ thống}` và Hình 3-3 lên vị trí 3.4.1.
2. Đặt `\subsection{Các tác nhân và danh mục ca sử dụng của hệ thống}` và Bảng 3-1 xuống vị trí 3.4.2.
3. Cập nhật đoạn văn dẫn đầu Section 3.4: giới thiệu tổng quan hệ thống và biểu đồ Use Case tổng quan trước, sau đó dẫn dắt sang bảng phân loại ca sử dụng.

- [ ] **Step 4: Chạy lại test để xác nhận test vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_section_order.py`
Expected: PASS (1 passed).

- [ ] **Step 5: Biên dịch XeLaTeX và xác nhận verify_thesis_format**

Run: `cd report-datn && xelatex -interaction=nonstopmode -file-line-error main.tex && cd .. && python3 scripts/verify_thesis_format.py`
Expected: XeLaTeX exit 0; `verify_thesis_format.py` exit 0 (LoF, LoT, ToC hợp lệ 100%).

- [ ] **Step 6: Commit và đồng bộ VPS**

```bash
git add report-datn/chapters/ch3/3_4_phan_tich_usecase.tex tests/report_datn/test_section_order.py
git commit -m "fix(thesis): place Use Case overview diagram before actors table in Sec 3.4"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Triệt Tiêu Khoảng Trắng Hoang Vu Trang 30 Bằng `\clearpage` Trước Mục 3.5

**Files:**
- Modify: `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex:1-70`
- Test: `tests/report_datn/test_layout_spacing.py`

**Interfaces:**
- Consumes: Phân bố trang của Mục 3.4.4, Section 3.5 và Hình 3-8.
- Produces: Mục 3.4.4 trọn vẹn ở Trang 30; Mục 3.5, 3.5.1 và Hình 3-8 bắt đầu ở đầu Trang 31.

- [ ] **Step 1: Viết test kiểm tra phân bố trang và ngắt trang trước Mục 3.5**

Tạo file `tests/report_datn/test_layout_spacing.py`:
```python
import subprocess
from pathlib import Path


def test_clearpage_before_section_3_5():
    tex_path = Path("report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra có \clearpage trước \section{Phân tích một số biểu đồ tuần tự chính của hệ thống}
    sec_pos = content.find(
        "\\section{Phân tích một số biểu đồ tuần tự chính của hệ thống}"
    )
    clearpage_pos = content.find("\\clearpage")
    assert clearpage_pos != -1 and clearpage_pos < sec_pos, (
        "Bắt buộc có \\clearpage trước Section 3.5 để chuyển toàn bộ Mục 3.5 sang đầu trang mới"
    )


def test_section_3_5_and_fig3_8_on_same_page():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    # Tìm trang chứa Section 3.5 và trang chứa Hình 3-8
    res = subprocess.run(
        ["pdftotext", str(pdf_path), "-"], capture_output=True, text=True
    )
    pages = res.stdout.split("\x0c")

    p_sec_3_5 = next(
        (
            i + 1
            for i, p in enumerate(pages)
            if "3.5 Phân tích một số biểu đồ tuần tự" in p
        ),
        None,
    )
    p_fig_3_8 = next(
        (i + 1 for i, p in enumerate(pages) if "Hình 3-8" in p), None
    )

    assert p_sec_3_5 is not None, "Không tìm thấy Section 3.5 trong PDF"
    assert p_fig_3_8 is not None, "Không tìm thấy Hình 3-8 trong PDF"
    assert p_sec_3_5 == p_fig_3_8, (
        f"Section 3.5 (trang {p_sec_3_5}) và Hình 3-8 (trang {p_fig_3_8}) phải cùng nằm trên 1 trang!"
    )
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -k test_clearpage_before_section_3_5`
Expected: FAIL với AssertionError.

- [ ] **Step 3: Chèn `\clearpage` trước Section 3.5 trong `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex`**

Thực hiện:
1. Thêm `\clearpage` ngay trước `\section{Phân tích một số biểu đồ tuần tự chính của hệ thống}`.
2. Giữ nguyên cấu trúc phân tách giữa các biểu đồ tuần tự.

- [ ] **Step 4: Chạy lại test để xác nhận test vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -k test_clearpage_before_section_3_5`
Expected: PASS (1 passed).

- [ ] **Step 5: Biên dịch XeLaTeX 2 lần và kiểm tra kiểm định cùng trang**

Run: `cd report-datn && xelatex -interaction=nonstopmode -file-line-error main.tex && xelatex -interaction=nonstopmode -file-line-error main.tex && cd .. && uv run pytest tests/report_datn/test_layout_spacing.py -k test_section_3_5_and_fig3_8_on_same_page`
Expected: PASS (Section 3.5 và Hình 3-8 cùng nằm trên Trang 31).

- [ ] **Step 6: Commit và đồng bộ VPS**

```bash
git add report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex tests/report_datn/test_layout_spacing.py
git commit -m "fix(thesis): place clearpage before Sec 3.5 to eliminate page 30 orphan whitespace"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: Tinh Chỉnh Hình 3-12 (Khử Chồng Đè Nhãn Bản Số Biểu Đồ Lớp)

**Files:**
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:20-256`
- Test: `tests/report_datn/test_diagram_bounds.py`

**Interfaces:**
- Consumes: 11 lớp UML và các mối quan hệ cấu trúc miền trong `3_6_thiet_ke_csdl.tex`.
- Produces: Hình 3-12 với kích thước hộp lớp tinh gọn (`inner sep=2.0pt`), khoảng hở giữa các hộp lớp $\ge 6\,\text{mm}$, đầu mũi tên hình thoi nằm hoàn toàn ngoài thân hộp, nhãn `{1}` và `{N}` dời sang sườn ngoài không đè lên bất kỳ tên lớp hay phương thức nào.

- [ ] **Step 1: Bổ sung test kiểm tra các thông số hình học của Hình 3-12**

Thêm vào `tests/report_datn/test_diagram_bounds.py`:
```python
def test_fig3_12_class_diagram_styling():
    tex_path = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra inner sep đã được tinh gọn để tạo khoảng hở giữa các hộp lớp
    assert "inner sep=2.0pt" in content or "inner sep=2.2pt" in content, (
        "Cần giảm inner sep của umlclass để thu hẹp chiều cao hộp lớp"
    )

    # Kiểm tra không còn nhãn đè vào điểm neo south/north không có khoảng lùi an toàn
    assert "yshift=-3.5pt" not in content, (
        "Khoảng lệch yshift=-3.5pt quá nhỏ khiến nhãn đè vào đường phân cách hoặc thân hộp"
    )
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig3_12_class_diagram_styling`
Expected: FAIL với AssertionError.

- [ ] **Step 3: Tinh gọn kích thước hộp lớp và tái định tuyến điểm neo nhãn trong `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`**

Thực hiện:
1. Đổi `inner sep=3.0pt` thành `inner sep=2.0pt` trong style `umlclass`.
2. Đổi khoảng cách giữa các khối:
   - Cột 1: `user` ($y=3.8$), `profile` ($y=1.35$), `apikey` ($y=-1.15$), `session` ($y=-3.65$), `turn` ($y=-6.15$).
   - Nhờ giảm `inner sep`, khoảng trống giữa 2 hộp lớp tăng lên $\approx 7\,\text{mm}$.
3. Cập nhật vị trí nhãn `{1}` và `{N}`:
   - Dùng anchor sườn lệch: `node[card, anchor=south east] at ([xshift=-4pt, yshift=2pt]profile.north) {1}` hoặc `node[card, anchor=north east] at ([xshift=-4pt, yshift=-2pt]user.south) {1}`.
   - Các nhãn trên đường liên kết ngang (user $\to$ doc, doc $\to$ node, session $\to$ doc) đặt ở sườn ngoài cách biên $\ge 4\,\text{pt}$.
   - Đường comp từ `draft` đến `draftmsg` đặt nhãn bên sườn trái đường nối, không đè lên chữ `DraftMessage` hay `update_content`.

- [ ] **Step 4: Chạy lại test để xác nhận test vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig3_12_class_diagram_styling`
Expected: PASS (1 passed).

- [ ] **Step 5: Biên dịch XeLaTeX và render PNG kiểm chứng**

Run: `cd report-datn && xelatex -interaction=nonstopmode -file-line-error main.tex && cd .. && pdftoppm -png -r 150 -f 51 -l 51 report-datn/main.pdf /tmp/verify_fig3_12`
Expected: XeLaTeX exit 0; ảnh `/tmp/verify_fig3_12-51.png` hiển thị toàn bộ 11 hộp lớp sắc nét, không có bất kỳ nhãn nào đè chữ hay mũi tên đâm xuyên hộp.

- [ ] **Step 6: Commit và đồng bộ VPS**

```bash
git add report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex tests/report_datn/test_diagram_bounds.py
git commit -m "fix(thesis): polish Fig 3-12 class diagram spacing, bounds and label anchors"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: Nới Khoảng Cách Dòng Trong Biểu Đồ Tuần Tự (Hình 3-9, 3-10, 3-11), Đệm Sơ Đồ Toàn Bài Và Xác Minh 4 Cổng Kiểm Định

**Files:**
- Modify: `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex:70-255`
- Modify: `report-datn/main.tex:84-86`
- Modify: `report-datn/config/preamble.tex:60-70`
- Test: `tests/report_datn/test_diagram_bounds.py`

**Interfaces:**
- Consumes: Cấu trúc tọa độ các thông điệp tuần tự trong Hình 3-9, 3-10, 3-11 và tham số float spacing toàn cục.
- Produces: 3 biểu đồ tuần tự thoáng mắt với bước dòng giãn thêm $1.5\,\text{mm}$; khoảng cách đệm trên/dưới sơ đồ với text tăng thêm $0.5$ dòng (`\intextsep` và `\textfloatsep`); biên dịch sạch; vượt qua 100% 4 Cổng Kiểm Định.

- [ ] **Step 1: Viết test kiểm tra bước giãn dòng trong Hình 3-9, 3-10, 3-11 và float spacing**

Thêm vào `tests/report_datn/test_diagram_bounds.py`:
```python
def test_sequence_diagrams_spacing_and_float_padding():
    seq_path = Path("report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex")
    seq_content = seq_path.read_text(encoding="utf-8")

    # Kiểm tra Hình 3-9, 3-10, 3-11 có lifeline mở rộng để chứa các thông điệp giãn dòng
    assert "-- (0, -10.5)" in seq_content or "-- (0, -10.2)" in seq_content, (
        "Lifeline trong biểu đồ tuần tự cần kéo dài đến y <= -10.2cm để chứa các bước giãn dòng"
    )

    # Kiểm tra float spacing trong main.tex được tăng thêm 0.5 dòng (~10pt)
    main_path = Path("report-datn/main.tex")
    main_content = main_path.read_text(encoding="utf-8")
    assert (
        "\\setlength{\\intextsep}{10pt" in main_content
        or "\\setlength{\\intextsep}{11pt" in main_content
        or "\\setlength{\\intextsep}{12pt" in main_content
    ), "Cần tăng \\intextsep lên khoảng 10-12pt để có đệm 0.5 dòng với text"
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_sequence_diagrams_spacing_and_float_padding`
Expected: FAIL với AssertionError.

- [ ] **Step 3: Cập nhật bước dọc thông điệp trong `3_5_bieu_do_tuan_tu.tex` và float spacing trong `main.tex` & `preamble.tex`**

Thực hiện:
1. Trong Hình 3-9: nới khoảng cách giữa các thông điệp tuần tự thêm $1.5\,\text{mm}$ (từ bước $0.7\,\text{cm}$ lên bước $0.85\,\text{cm}$); kéo dài lifeline từ $-9.6$ đến $-10.4$; cập nhật các hộp kích hoạt tương ứng.
2. Trong Hình 3-10: nới khoảng cách giữa các thông điệp thêm $1.5\,\text{mm}$; kéo dài lifeline từ $-9.2$ đến $-10.2$.
3. Trong Hình 3-11: nới khoảng cách giữa các thông điệp thêm $1.5\,\text{mm}$; kéo dài lifeline từ $-9.0$ đến $-10.2$.
4. Trong `report-datn/main.tex`:
   - `\setlength{\floatsep}{8pt plus 2pt minus 1pt}`
   - `\setlength{\textfloatsep}{12pt plus 2pt minus 2pt}`
   - `\setlength{\intextsep}{10pt plus 2pt minus 2pt}`
5. Trong `report-datn/config/preamble.tex`: cập nhật đồng bộ các giá trị float spacing.

- [ ] **Step 4: Chạy lại test để xác nhận test vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_sequence_diagrams_spacing_and_float_padding`
Expected: PASS (1 passed).

- [ ] **Step 5: Biên dịch XeLaTeX 2 lần và kiểm định 4 Verification Gates**

Run các lệnh xác minh:
```bash
cd report-datn && xelatex -interaction=nonstopmode -file-line-error main.tex && xelatex -interaction=nonstopmode -file-line-error main.tex && cd ..
python3 scripts/verify_thesis_format.py
uv run ruff check . && uv run ruff format --check .
uv run pytest
npm --prefix apps/web run test
npm --prefix apps/web run build
```
Expected: 100% exit code 0.

- [ ] **Step 6: Render PNG toàn bộ các trang đã sửa đổi và kiểm tra trực quan**

Run:
```bash
pdftoppm -png -r 150 -f 32 -l 32 report-datn/main.pdf /tmp/final_fig2_4
pdftoppm -png -r 150 -f 38 -l 38 report-datn/main.pdf /tmp/final_fig3_2
pdftoppm -png -r 150 -f 40 -l 41 report-datn/main.pdf /tmp/final_sec3_4
pdftoppm -png -r 150 -f 47 -l 47 report-datn/main.pdf /tmp/final_fig3_8
pdftoppm -png -r 150 -f 48 -l 50 report-datn/main.pdf /tmp/final_seq_diagrams
pdftoppm -png -r 150 -f 51 -l 51 report-datn/main.pdf /tmp/final_fig3_12
```
Kiểm tra trực quan xác nhận 6 khiếm khuyết được giải quyết triệt để.

- [ ] **Step 7: Commit và đồng bộ VPS**

```bash
git add report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex report-datn/main.tex report-datn/config/preamble.tex report-datn/main.pdf tests/report_datn/test_diagram_bounds.py
git commit -m "fix(thesis): expand sequence diagrams message spacing and float padding by 0.5 lines"
bash scripts/deploy_to_vps.sh --fast
```
