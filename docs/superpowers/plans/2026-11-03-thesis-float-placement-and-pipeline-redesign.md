# Bố Cục Float Không Ngắt Câu, Mũi Tên Hình 3-2 và Sơ Đồ Tuần Tự Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khắc phục triệt để lỗi chèn hình cắt ngang câu văn trên toàn bộ luận văn, kéo dài thân mũi tên Hình 3-2 tạo khoảng cách thoáng đãng, và thiết kế lại 4 sơ đồ tuần tự (Hình 3-8, 3-9, 3-10, 3-11) thành Horizontal Stage Cards Pipeline hiện đại, trực quan và không bị lỗi bố cục.

**Architecture:** Sử dụng gói `float` (`[H]`) và `placeins` (`\FloatBarrier`) để khóa vị trí hình ảnh sau đoạn văn hoàn chỉnh; điều chỉnh kích thước hình học TikZ để tạo khe hở $6.0-6.5\,\text{mm}$ cho mũi tên Hình 3-2; chuyển đổi các sơ đồ tuần tự lifeline thành chuỗi thẻ ngang pipeline cao $3.5-4.5\,\text{cm}$ nối tiếp bằng mũi tên dày.

**Tech Stack:** XeLaTeX, TikZ, PGF, Python 3.12, Pytest, pypdf, pdftotext.

**Spec:** `docs/superpowers/specs/2026-11-03-thesis-float-placement-and-pipeline-redesign-design.md`

## Global Constraints

- Không dùng đường dẫn tuyệt đối `file://` trong Markdown (Rule 5).
- Phong cách tối giản 80/20, chuẩn ngôn từ học thuật Bách khoa (Rule 6).
- Chạy `bash scripts/deploy_to_vps.sh --fast` tự động sau mỗi git commit (Rule 7).
- Vượt qua 100% 4 Cổng Kiểm Định trước khi hoàn thành: Ruff, Pytest (373 tests), Vitest (240 tests), Web build.
- Giữ vững tổng số trang và ngân sách trang chuẩn của Đại học Bách khoa Hà Nội.

## Review Focus

- Không có bất kỳ câu văn nào bị chèn ngắt đôi giữa trang trước và trang sau bởi hình ảnh nổi ở đầu trang.
- Mũi tên Hình 3-2 phải có thân đường thẳng dài tối thiểu $3.5\,\text{mm}$ hiển thị rõ `-->`, không bị cụt chỉ có đầu tam giác.
- Sơ đồ tuần tự Hình 3-8, 3-9, 3-10, 3-11 hiển thị trọn vẹn, không tràn lề và không bị dính chữ.
- Không để lại khoảng trống lớn bất thường ở đáy trang in do float bị đẩy sang trang sau.
- Quy chuẩn định dạng luận văn `scripts/verify_thesis_format.py` đạt 100%.

---

### Task 1: Cấu hình `[H]` + `placeins` và khắc phục ngắt câu tại Hình 2-4 (Chương 2)

**Files:**
- Modify: `report-datn/config/preamble.tex`
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex`
- Modify: `tests/report_datn/test_diagram_bounds.py`
- Test: `tests/report_datn/test_layout_spacing.py`

**Interfaces:**
- Consumes: Gói `float` và `placeins` trong LaTeX.
- Produces: `\begin{figure}[H]` và `\FloatBarrier` trước các `\subsection`, bảo đảm Hình 2-4 không cắt đứt câu dẫn về khóa BYOK giữa trang 16 và 17.

- [ ] **Step 1: Write the failing test**

Thêm test `test_fig2_4_no_sentence_break()` vào `tests/report_datn/test_layout_spacing.py` kiểm tra:
1. `preamble.tex` có nạp `\usepackage{float}` và `\usepackage{placeins}`.
2. `2_5_agentic_react.tex` sử dụng `[H]` cho Hình 2-4 hoặc có `\FloatBarrier` trước `\subsection{2.5.4}`.
3. Trong PDF, câu văn *"Người dùng trực tiếp cung cấp khóa API từ các nhà cung cấp (như \texttt{gpt-4o-mini}..."* không bị cắt đôi bởi Hình 2-4.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -k test_fig2_4_no_sentence_break -v`  
Expected: FAIL (do chưa nạp `placeins` / `float` và văn bản trong PDF vẫn đang bị cắt).

- [ ] **Step 3: Implement changes in `preamble.tex` and `2_5_agentic_react.tex`**

1. Nạp `\usepackage{float}` và `\usepackage[section]{placeins}` vào `preamble.tex`.
2. Trong `2_5_agentic_react.tex`: Đổi `\begin{figure}[!htbp]` thành `\begin{figure}[H]`, bổ sung `\FloatBarrier` trước `\subsection{Mô hình quản lý khóa...}`.
3. Đặt vị trí Hình 2-4 sau đoạn mô tả của Mục 2.5.3, hoàn thành các chỉnh sửa nới rộng mũi tên thẳng đứng và nhãn `right=10pt`.
4. Biên dịch lại XeLaTeX: `cd report-datn && latexmk -xelatex -interaction=nonstopmode main.tex`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -k test_fig2_4_no_sentence_break -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/config/preamble.tex report-datn/chapters/ch2/2_5_agentic_react.tex report-datn/main.pdf tests/report_datn/test_layout_spacing.py tests/report_datn/test_diagram_bounds.py
git commit -m "fix(thesis): resolve mid-sentence float break for Fig 2-4 and add placeins"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Kéo dài thân mũi tên liên kết giữa các tầng trong Hình 3-2 (Kiến trúc Lục giác)

**Files:**
- Modify: `report-datn/chapters/ch3/3_3_kien_truc.tex`
- Test: `tests/report_datn/test_diagram_bounds.py`

**Interfaces:**
- Consumes: TikZ node styling và coordinates trong `3_3_kien_truc.tex`.
- Produces: Khe hở $\ge 5.5\,\text{mm}$ giữa Core, Ports và Adapters; thân mũi tên dài $\ge 3.5\,\text{mm}$.

- [ ] **Step 1: Write the failing test**

Cập nhật test `test_fig3_2_coordinates_within_safe_margins()` trong `tests/report_datn/test_diagram_bounds.py`:
1. Kiểm tra `portbox` có `minimum width` $\le 2.2\,\text{cm}$ (thu hẹp từ 2.4cm).
2. Kiểm tra tọa độ Port tại $x = \pm 6.1$ và Adapter tại $x = \pm 9.2$.
3. Kiểm tra khoảng cách giữa mép ngoài Port và Core $\ge 5.0\,\text{mm}$, mép ngoài Adapter và Port $\ge 5.0\,\text{mm}$.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig3_2_coordinates_within_safe_margins -v`  
Expected: FAIL (do tọa độ cũ vẫn là $x=\pm 5.85$ và $x=\pm 8.8$).

- [ ] **Step 3: Implement updated TikZ coordinates in `3_3_kien_truc.tex`**

1. Điều chỉnh `portbox` style: `minimum width=2.1cm`.
2. Khung Core domain: `(-4.4, -3.8) rectangle (4.4, 4.3)`.
3. Driving Ports: `x = -6.1`, Driven Ports: `x = 6.1`.
4. Driving Adapters: `x = -9.2`, Driven Adapters: `x = 9.2`.
5. External Actor: `x = -9.2`.
6. Cập nhật các điểm neo của mũi tên kết nối tương ứng:
   `\draw[arrow_flow] (p_drive_api.east) -- (-4.4, 2.0);`
   `\draw[arrow_flow] (4.4, 2.5) -- (p_driven_db.west);` ...
7. Đổi `\begin{figure}[!htbp]` thành `\begin{figure}[H]` kèm `\FloatBarrier` để định vị chắc chắn.
8. Biên dịch lại XeLaTeX: `cd report-datn && latexmk -xelatex -interaction=nonstopmode main.tex`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_fig3_2_coordinates_within_safe_margins -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch3/3_3_kien_truc.tex report-datn/main.pdf tests/report_datn/test_diagram_bounds.py
git commit -m "fix(thesis): widen arrow gap and lengthen arrow stem in Fig 3-2 hexagonal architecture"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Thiết kế lại Hình 3-8, 3-9, 3-10, 3-11 theo Horizontal Stage Cards Pipeline

**Files:**
- Modify: `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex`
- Test: `tests/report_datn/test_diagram_bounds.py`
- Test: `tests/report_datn/test_layout_spacing.py`

**Interfaces:**
- Consumes: Tiêu đề và nội dung 4 Use Case trong Mục 3.5.
- Produces: 4 sơ đồ dạng Horizontal Stage Cards Pipeline (cao $3.5-4.5\,\text{cm}$), dùng `[H]`, triệt tiêu hoàn toàn rối rắm, nét đứt và khoảng trắng thừa.

- [ ] **Step 1: Write the failing test**

Cập nhật `test_sequence_diagrams_spacing_and_float_padding()` trong `tests/report_datn/test_diagram_bounds.py`:
1. Kiểm tra 4 hình trong `3_5_bieu_do_tuan_tu.tex` sử dụng cấu trúc Stage Cards Pipeline (có các node `stage_card`, mũi tên `stage_arrow`).
2. Kiểm tra không còn lifeline thẳng đứng kéo dài quá $-10\,\text{cm}$ gây choán chỗ.
3. Kiểm tra cả 4 hình đều sử dụng `[H]`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_sequence_diagrams -v`  
Expected: FAIL (do các sơ đồ cũ vẫn là lifeline kéo dài).

- [ ] **Step 3: Implement Horizontal Stage Cards Pipeline for Figs 3-8, 3-9, 3-10, 3-11**

1. Định nghĩa phong cách thẻ chuẩn TikZ trong `3_5_bieu_do_tuan_tu.tex`:
   - `stage_card`: `minimum width=2.7cm, minimum height=1.6cm, rounded corners=4pt, line width=0.85pt, align=center, inner sep=3pt, font=\linespread{0.95}\selectfont\fontsize{7.5pt}{9pt}\selectfont`
   - `stage_arrow`: `-{Stealth[length=2.5mm]}, line width=1.1pt`
2. **Hình 3-8 (Tra cứu và Tải tài liệu CAS):** 5 thẻ ngang kết nối tuần tự từ Học giả $\to$ Đa nguồn Scholarly $\to$ Deduplication CAS SHA-256 $\to$ Lưu trữ CSDL $\to$ Thư viện cá nhân.
3. **Hình 3-9 (Hỏi đáp Đọc sâu & BBox):** 4 thẻ ngang: Nhập câu hỏi $\to$ Hybrid RAG (HNSW + BM25) $\to$ Cổng CRAG & Re-ranking $\to$ Stream SSE & Tô sáng BBox $1\,\text{s}$.
4. **Hình 3-10 (GraphRAG & Truy vấn 2-hop):** 4 thẻ ngang: Trích xuất 4 Thực thể $\to$ Khử trùng Cosine $\ge 0{,}90 \to$ Phân cụm Louvain $\to$ Truy vấn Wiki 2-hop CTE.
5. **Hình 3-11 (Biên soạn Monaco & Tự sửa lỗi):** 5 thẻ ngang: Monaco Editor $\to$ E2B MicroVM Sandbox $\to$ Phân tích Log lỗi $\to$ ReAct Agent vá mã ($N \le 3$) $\to$ PDF Hoàn chỉnh.
6. Sử dụng `[H]` cho cả 4 hình, loại bỏ các lệnh `\clearpage` cưỡng bức gây khoảng trống đáy trang lớn.
7. Biên dịch XeLaTeX: `cd report-datn && latexmk -xelatex -interaction=nonstopmode main.tex`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/report_datn/test_diagram_bounds.py tests/report_datn/test_layout_spacing.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex report-datn/main.pdf tests/report_datn/test_diagram_bounds.py
git commit -m "feat(thesis): redesign sequence diagrams into horizontal stage cards pipeline"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Rà soát và chuẩn hóa vị trí Float `[H]` cho các hình còn lại (Chương 3 & Chương 4)

**Files:**
- Modify: `report-datn/chapters/ch3/3_2_khao_sat_nghiep_vu.tex`
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex`
- Modify: `report-datn/chapters/ch4/4_4_so_lieu.tex`
- Test: `tests/report_datn/test_layout_spacing.py`

**Interfaces:**
- Consumes: Các khối figure trong Chương 3 và Chương 4.
- Produces: 100% các figure không cắt đứt câu văn giữa các trang.

- [ ] **Step 1: Write the failing test**

Thêm test `test_all_figures_no_broken_sentences()` vào `tests/report_datn/test_layout_spacing.py` tự động quét toàn bộ `main.pdf` bằng `pdftotext` và assert rằng: Không có bất kỳ trang nào chứa caption hình ở đầu trang mà dòng văn bản ngay sau caption lại tiếp tục một câu chưa hoàn chỉnh từ trang trước.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -k test_all_figures_no_broken_sentences -v`  
Expected: FAIL (phát hiện các điểm ngắt câu tại Hình 3-1, 4-4, 4-7, 4-9, 4-10).

- [ ] **Step 3: Standardize float placement with `[H]` and `\FloatBarrier`**

1. Cập nhật Hình 3-1 trong `3_2_khao_sat_nghiep_vu.tex`: Sử dụng `[H]`, đặt sau đoạn văn mô tả trọn vẹn.
2. Cập nhật Hình 4-4, Hình 4-7, Hình 4-9, Hình 4-10 trong `4_2_giao_dien.tex` và `4_4_so_lieu.tex`: Sử dụng `[H]`, bổ sung `\FloatBarrier` trước các tiểu mục giao diện.
3. Biên dịch XeLaTeX: `cd report-datn && latexmk -xelatex -interaction=nonstopmode main.tex`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -k test_all_figures_no_broken_sentences -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch3/3_2_khao_sat_nghiep_vu.tex report-datn/chapters/ch4/4_2_giao_dien.tex report-datn/chapters/ch4/4_4_so_lieu.tex report-datn/main.pdf tests/report_datn/test_layout_spacing.py
git commit -m "fix(thesis): eliminate mid-sentence float breaks across all chapters"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: Xác minh Toàn diện 4 Cổng Kiểm Định và Render Ảnh Kiểm Chứng

**Files:**
- Test: Toàn bộ test suite (`pytest`, `vitest`, `ruff`, `verify_thesis_format.py`)
- Artifacts: Render ảnh PNG kiểm chứng chất lượng Hình 3-2, Hình 3-8, Hình 3-9, Hình 3-10, Hình 3-11.

- [x] **Step 1: Run format verification script**

Run: `uv run python scripts/verify_thesis_format.py`  
Expected: 100% Pass (trang, lề, bảng, hình).

- [x] **Step 2: Render verification images**

Chạy `pdftoppm` render các trang chứa Hình 3-2, 3-8, 3-9, 3-10, 3-11 và crop các vùng hình ảnh để trực tiếp kiểm tra bằng thị giác.

- [x] **Step 3: Run the 4 Verification Gates**

1. Cổng 1: `uv run ruff check . && uv run ruff format --check .`
2. Cổng 2: `uv run pytest`
3. Cổng 3: `npm --prefix apps/web run test`
4. Cổng 4: `npm --prefix apps/web run build`

- [x] **Step 4: Commit and VPS Sync**

```bash
git add report-datn/main.pdf
git commit -m "chore(thesis): finalize visual polish, float placement and compiled pdf"
bash scripts/deploy_to_vps.sh --fast
```
