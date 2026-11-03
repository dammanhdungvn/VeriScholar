# Kế Hoạch Triển Khai: Tinh Gọn Cơ Sở Dữ Liệu, Xóa Phụ Lục A và Chuẩn Hóa Đồ Họa Báo Cáo Đồ Án Tốt Nghiệp

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tinh gọn triệt để phần Cơ sở Dữ liệu Mục 3.6 theo nguyên tắc 80/20, xóa bỏ 2 sơ đồ ERD và bảng gộp 20 bảng, trình bày tách bạch 4 bảng CSDL cốt lõi theo từng phân hệ; xóa bỏ hoàn toàn Phụ lục A để báo cáo kết thúc ngay sau Tài liệu tham khảo; chuẩn hóa căn giữa nội dung các bảng và sửa triệt để các lỗi hiển thị trên sơ đồ đồ họa (Hình 2-4, 3-2, 3-5, 3-12).

**Architecture:** Sử dụng kiến trúc tài liệu học thuật XeLaTeX phân tầng: tách bạch các phân hệ nghiệp vụ trong thân bài Chương 3 mà không nhồi nhét sơ đồ ERD phức tạp; cấu hình bảng biểu với `tabularx` kết hợp cột `m{...}` căn giữa cho dữ liệu ngắn và `X` cho nội dung văn xuôi; hiệu chỉnh thông số tọa độ và nhãn node trong môi trường TikZ vector để triệt tiêu hiện tượng dính chùm hoặc đè chữ.

**Tech Stack:** XeLaTeX, TikZ / PGF, TeX Live 2023, Python 3.12 (`pytest`, `verify_thesis_format.py`), Git.

**Spec:** `docs/specs/2026-11-03-thesis-visual-and-database-refinement-design.md`

## Global Constraints

- XeLaTeX biên dịch thành công 100% với exit code 0, không có lỗi "Fatal error" hay "Undefined reference".
- Tuyệt đối cấm sử dụng ký tự `&` trong văn bản tiếng Việt thường (dùng từ `và`).
- Báo cáo kết thúc ngay sau phần Tài liệu tham khảo, tuyệt đối không có Phụ lục A ở phía sau.
- Các bảng biểu dữ liệu ngắn (STT, Tên cột, Kiểu dữ liệu, Ràng buộc, Bản số) bắt buộc căn giữa theo cả chiều ngang và dọc.
- Giữ vững ngân sách tổng số trang báo cáo trong khoảng 74–78 trang in (không vượt quá 80 trang).

## Review Focus

1. **Undefined references:** Khi xóa Phụ lục A và 2 sơ đồ ERD, các lệnh `\ref{tab:spec_...}` và `\ref{fig:erd_...}` nếu chưa được dọn sạch sẽ gây cảnh báo hoặc in ra chữ đậm `??` trên bản PDF. Pin test tại Task 1 và Task 5.
2. **Adversarial tests mismatch:** `tests/test_thesis_rules_adversarial.py` kiểm tra `fig:erd_model` và thứ tự Class Diagram. Cần cập nhật test song hành theo Co-Location Commit Rule để test suite không bị gãy. Pin test tại Task 2 và Task 5.
3. **Table column overflow:** Khi đổi cột sang căn giữa `>{\centering\arraybackslash}m{...}`, nếu đặt chiều rộng quá hẹp có thể gây lỗi `Overfull \hbox`. Cần gán độ rộng chính xác tỷ lệ `\textwidth`. Pin test tại Task 2 và Task 4.
4. **TikZ node collision in Figure 3-5:** Các oval Use Case con nếu không đủ giãn cách dọc ($\Delta y \ge 1{,}15\text{cm}$) sẽ lại bị dính chùm viền vào nhau. Pin test tại Task 3.
5. **Page budget drift:** Việc xóa Phụ lục A giải phóng 5 trang in, nhưng cần bảo đảm các trang trước Mục lục và trang bắt đầu Chương 1 không bị xê dịch. Pin test tại Task 5.

---

### Task 1: Loại bỏ Phụ lục A và Dọn sạch Toàn bộ Liên kết Tham chiếu

**Files:**
- Modify: `report-datn/main.tex:105-111`
- Delete: `report-datn/chapters/phu_luc.tex`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:650-655`

**Interfaces:**
- Consumes: `report-datn/main.tex`, `report-datn/chapters/phu_luc.tex`
- Produces: Bản thảo không còn Phụ lục A sau Tài liệu tham khảo; không còn liên kết gãy.

- [ ] **Step 1: Viết test kiểm tra không còn Phụ lục A trong báo cáo và không còn tệp `phu_luc.tex`**

```python
# tests/test_thesis_no_appendix.py
from pathlib import Path


def test_no_appendix_in_main_and_filesystem():
    main_tex = Path("report-datn/main.tex").read_text(encoding="utf-8")
    assert "\\input{chapters/phu_luc}" not in main_tex
    assert "PHỤ LỤC" not in main_tex
    assert not Path("report-datn/chapters/phu_luc.tex").exists()


def test_no_broken_appendix_references():
    csdl_tex = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex").read_text(encoding="utf-8")
    assert "Phụ lục A" not in csdl_tex
    assert "Phụ lục~A" not in csdl_tex
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại**

Run: `uv run pytest tests/test_thesis_no_appendix.py -v`  
Expected: FAIL (Do `main.tex` vẫn còn `\input{chapters/phu_luc}` và file vẫn tồn tại).

- [ ] **Step 3: Thực hiện gỡ bỏ Phụ lục A**

1. Trong `report-datn/main.tex`: Xóa dòng `\input{chapters/phu_luc}` và khối chú thích Phụ lục A.
2. Xóa tệp `report-datn/chapters/phu_luc.tex`.
3. Trong `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`: Thay thế đoạn văn viện dẫn "cùng 11 bảng cơ sở dữ liệu còn lại được trình bày đầy đủ tại Phụ lục A" bằng câu văn đúc kết kiến trúc lưu trữ hạt nhân.

- [ ] **Step 4: Chạy test xác nhận pass**

Run: `uv run pytest tests/test_thesis_no_appendix.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/main.tex report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex tests/test_thesis_no_appendix.py
git rm report-datn/chapters/phu_luc.tex
git commit -m "docs(datn): remove appendix a and eliminate all trailing appendix references"
```

---

### Task 2: Tái cấu trúc Mục 3.6 (Bỏ Sơ đồ ERD, Bỏ Bảng Gộp 20 Bảng, Tinh Gọn 4 Bảng Cốt Lõi)

**Files:**
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`
- Modify: `tests/test_thesis_rules_adversarial.py:80-100`

**Interfaces:**
- Consumes: Cấu trúc thực thể trong `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`
- Produces: Bảng quan hệ thực thể miền sạch sẽ, 4 bảng đặc tả CSDL hạt nhân phân theo từng phân hệ rõ ràng; loại bỏ hoàn toàn 2 sơ đồ ERD và bảng gộp 20 bảng.

- [ ] **Step 1: Viết test kiểm tra cấu trúc Mục 3.6 mới không còn ERD và bảng gộp 20 bảng**

```python
# Thêm vào tests/test_thesis_no_appendix.py
def test_csdl_structure_streamlined():
    csdl_tex = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex").read_text(encoding="utf-8")
    # Không còn 2 sơ đồ ERD
    assert "\\label{fig:erd_auth_storage_session}" not in csdl_tex
    assert "\\label{fig:erd_graph_draft}" not in csdl_tex
    assert "\\label{fig:erd_model}" not in csdl_tex
    # Không còn bảng gộp 20 bảng
    assert "\\label{tab:db_tables_summary}" not in csdl_tex
    # Vẫn giữ 4 bảng đặc tả hạt nhân đại diện
    assert "\\label{tab:spec_documents}" in csdl_tex
    assert "\\label{tab:spec_chunks}" in csdl_tex
    assert "\\label{tab:spec_graph_nodes}" in csdl_tex
    assert "\\label{tab:spec_drafts}" in csdl_tex
    # Giữ các chuỗi bắt buộc
    assert "FK $\\to$ research_sessions(id)" in csdl_tex
    assert "FK $\\to$ document_storage_blobs(id)" in csdl_tex
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại**

Run: `uv run pytest tests/test_thesis_no_appendix.py::test_csdl_structure_streamlined -v`  
Expected: FAIL

- [ ] **Step 3: Cập nhật `3_6_thiet_ke_csdl.tex` và `tests/test_thesis_rules_adversarial.py`**

1. Trong `3_6_thiet_ke_csdl.tex`:
   * Xóa bỏ hoàn toàn phần `\subsection{Lược đồ quan hệ giữa các bảng trong cơ sở dữ liệu (ERD)}` cùng 2 khối TikZ `Hình 3-13` và `Hình 3-14`.
   * Xóa bỏ `\begin{table}[!htbp] ... \label{tab:db_tables_summary} ... \end{table}` (Bảng gộp 20 bảng). Thay thế bằng 1 tiểu mục tóm lược súc tích 5 phân hệ dữ liệu.
   * Cập nhật `Bảng 3-6: Phân tích các lớp thực thể miền và mối quan hệ cấu trúc`: Đổi kiểu cột thành căn giữa các cột Lớp A, Lớp B, Kiểu quan hệ, Bản số ($1-1$, $1-N$, $N-N$).
   * Tách rõ ràng 4 tiểu mục đặc tả bảng dữ liệu hạt nhân:
     - `3.6.3.1 Đặc tả bảng documents (Phân hệ Thư viện và Lưu trữ CAS)`
     - `3.6.3.2 Đặc tả bảng document_chunks (Phân hệ Đọc sâu và Kiểm chứng Bounding Box)`
     - `3.6.3.3 Đặc tả bảng graph_nodes (Phân hệ Đồ thị Tri thức GraphRAG)`
     - `3.6.3.4 Đặc tả bảng drafts (Phân hệ Soạn thảo Học thuật và Đồng tác giả AI)`
   * Căn giữa các cột `STT`, `Tên cột`, `Kiểu dữ liệu`, `Ràng buộc` trong cả 4 bảng bằng `>{\centering\arraybackslash}m{...}`.
2. Cập nhật `tests/test_thesis_rules_adversarial.py`: Điều chỉnh assertion để kiểm tra Class Diagram đứng trước các bảng dữ liệu thay vì tìm `fig:erd_model`.

- [ ] **Step 4: Chạy test xác nhận pass**

Run: `uv run pytest tests/test_thesis_no_appendix.py tests/test_thesis_rules_adversarial.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex tests/test_thesis_rules_adversarial.py tests/test_thesis_no_appendix.py
git commit -m "refactor(datn): streamline database section by dropping erds and modularizing 4 core tables"
```

---

### Task 3: Sửa Lỗi Hiển Thị Các Sơ Đồ Đồ Họa (Hình 2-4, Hình 3-2, Hình 3-5, Hình 3-12)

**Files:**
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex:50-125`
- Modify: `report-datn/chapters/ch3/3_3_kien_truc.tex:40-165`
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex:200-245`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:15-120`

**Interfaces:**
- Consumes: Môi trường TikZ của các hình vẽ
- Produces: Sơ đồ trực quan, không đè chữ, chữ to rõ nét, không bị dính chùm.

- [ ] **Step 1: Viết test kiểm tra các tham số hình học của TikZ đã được nới rộng**

```python
# Thêm vào tests/test_thesis_no_appendix.py
def test_tikz_diagram_spacing_refinements():
    # 1. Hình 3-5 Use Case con: khoảng cách dọc không được hẹp 0.75
    uc_tex = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex").read_text(
        encoding="utf-8"
    )
    assert "(11.5, 0.75)" not in uc_tex  # khoảng cách cũ bị dính chùm

    # 2. Hình 2-4 ReAct: nhãn Yes không được đặt đè sát mũi tên nhọn
    react_tex = Path("report-datn/chapters/ch2/2_5_agentic_react.tex").read_text(encoding="utf-8")
    assert "node[midway, right=6pt" not in react_tex

    # 3. Hình 3-2 Lục giác: scale không được quá bé 0.58
    arch_tex = Path("report-datn/chapters/ch3/3_3_kien_truc.tex").read_text(encoding="utf-8")
    assert "scale=0.58" not in arch_tex
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại**

Run: `uv run pytest tests/test_thesis_no_appendix.py::test_tikz_diagram_spacing_refinements -v`  
Expected: FAIL

- [ ] **Step 3: Chỉnh sửa mã nguồn TikZ**

1. **Hình 2-4 (`2_5_agentic_react.tex`):**
   * Tăng khoảng cách từ `cond` (-1.5) xuống `final` (-3.8). Dịch nhãn `Yes (Exit 0)` sang `node[midway, right=10pt]`.
   * Nới rộng bán kính cong của `looparrow`: `to[out=120, in=240] node[midway, left=8pt]`.
2. **Hình 3-2 (`3_3_kien_truc.tex`):**
   * Tăng `scale` từ `0.58` lên `0.70`, tăng cỡ chữ các nhãn từ `\tiny` lên `\scriptsize` hoặc `\footnotesize`.
   * Hạ vị trí tiêu đề `LÕI MIỀN NGHIỆP VỤ THUẦN KHIẾT` vào bên trong (y=3.4 thay vì y=3.65), tránh chạm viền trên.
3. **Hình 3-5 (`3_4_phan_tich_usecase.tex`):**
   * Tăng chiều cao khung hệ thống `sysbox` và giãn cách trục y giữa các oval con lên $\Delta y = 1{,}15$: ví dụ tại $y = 2{,}3; 1{,}15; 0{,}0; -1{,}15; -2{,}3$.
   * Tách điểm xuất phát của các đường mũi tên `<<include>>` để nhãn không đè lên nhau.
4. **Hình 3-12 (`3_6_thiet_ke_csdl.tex`):**
   * Nới rộng khoảng cách các cột lớp thực thể, định vị nhãn bản số có khoảng đệm `inner sep=1.8pt, fill=white` để không bị đè lên đường nối.

- [ ] **Step 4: Chạy test xác nhận pass**

Run: `uv run pytest tests/test_thesis_no_appendix.py::test_tikz_diagram_spacing_refinements -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch2/2_5_agentic_react.tex report-datn/chapters/ch3/3_3_kien_truc.tex report-datn/chapters/ch3/3_4_phan_tich_usecase.tex report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex tests/test_thesis_no_appendix.py
git commit -m "fix(datn): resolve label overlap, tiny text, and squashed ovals in tikz figures"
```

---

### Task 4: Chuẩn Hóa Căn Giữa (Center Alignment) Toàn Bộ Các Bảng Trong Đồ Án

**Files:**
- Modify: `report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex` (Bảng 1-1)
- Modify: `report-datn/chapters/ch2/2_1_postgresql_redis.tex` (Bảng 2-1)
- Modify: `report-datn/chapters/ch2/2_2_hybrid_rag.tex` (Bảng 2-2)
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex` (Bảng 3-1 đến 3-5)
- Modify: `report-datn/chapters/ch4/4_1_moi_truong.tex` (Bảng 4-1)
- Modify: `report-datn/chapters/ch4/4_3_kiem_thu.tex` (Bảng 4-2)
- Modify: `report-datn/chapters/ch4/4_4_so_lieu.tex` (Bảng 4-3, 4-4)

**Interfaces:**
- Consumes: Cột bảng biểu hiện tại
- Produces: Các cột định danh, STT, kiểu dữ liệu, ràng buộc, kết quả căn giữa chuẩn mực.

- [ ] **Step 1: Viết test kiểm tra các bảng không còn dùng `>{\raggedright\arraybackslash}` cho cột STT và Kiểu dữ liệu**

```python
# Thêm vào tests/test_thesis_no_appendix.py
def test_tables_center_aligned():
    files = [
        "report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex",
        "report-datn/chapters/ch4/4_1_moi_truong.tex",
        "report-datn/chapters/ch4/4_3_kiem_thu.tex",
        "report-datn/chapters/ch4/4_4_so_lieu.tex",
    ]
    for f in files:
        content = Path(f).read_text(encoding="utf-8")
        # Kiểm tra bảng có chứa môi trường căn giữa cột
        assert (
            ">{\\centering\\arraybackslash}" in content
            or "|c|" in content
            or "|>{\\centering\\arraybackslash}m{" in content
        )
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại hoặc cảnh báo bảng chưa đồng bộ**

Run: `uv run pytest tests/test_thesis_no_appendix.py::test_tables_center_aligned -v`

- [ ] **Step 3: Cập nhật định dạng cột của các bảng**

Áp dụng quy chuẩn:
- Cột `STT`: `|c|` hoặc `|>{\centering\arraybackslash}m{1.0cm}|`.
- Cột thông số, phiên bản, vai trò, tác nhân, độ trễ, bản số: `|>{\centering\arraybackslash}m{...}|`.
- Cột mô tả, diễn giải văn bản: `|>{\raggedright\arraybackslash}X|`.
- Đảm bảo `\arraystretch` đạt tối thiểu 1.15 để các dòng không bị dính sát đường kẻ ngang `\hline`.

- [ ] **Step 4: Chạy test xác nhận pass**

Run: `uv run pytest tests/test_thesis_no_appendix.py::test_tables_center_aligned -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex report-datn/chapters/ch2/ report-datn/chapters/ch3/3_4_phan_tich_usecase.tex report-datn/chapters/ch4/ tests/test_thesis_no_appendix.py
git commit -m "style(datn): enforce horizontal and vertical center alignment across all thesis tables"
```

---

### Task 5: Biên Dịch Toàn Diện XeLaTeX, Xác Minh 4 Gates và Kiểm Tra Ngân Sách Trang

**Files:**
- Modify: `report-datn/main.pdf`
- Verify: `scripts/verify_thesis_format.py`
- Verify: `scripts/test_preamble_config.py`
- Verify: `scripts/dev/verify.sh`

**Interfaces:**
- Consumes: Toàn bộ mã nguồn tài liệu
- Produces: `main.pdf` hoàn chỉnh, trang đẹp, 0 lỗi, ngân sách 74-78 trang, 4 Gates Pass 100%.

- [ ] **Step 1: Biên dịch 2 lượt XeLaTeX để cập nhật toàn bộ Mục lục và Danh mục bảng/hình**

```bash
cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
```
Expected: Exit code 0, không có lỗi Fatal error, không có undefined references.

- [ ] **Step 2: Chạy script kiểm định quy chuẩn định dạng**

```bash
python3 scripts/verify_thesis_format.py
python3 scripts/test_preamble_config.py
```
Expected: 100% checks PASSED (Phiếu giao: iii-iv; Đề cương: v-vii; Lời cảm ơn: viii; Mục lục: ix; Chương 1 bắt đầu trang 1).

- [ ] **Step 3: Kiểm tra tổng số trang in thực tế**

```bash
pdfinfo report-datn/main.pdf | grep "Pages:"
```
Expected: Tổng số trang nằm trong khoảng 74–78 trang (đúng mục tiêu của người dùng: 75–85 trang, không bị quá tải).

- [ ] **Step 4: Chạy toàn bộ 4 Verification Gates**

```bash
bash scripts/dev/verify.sh
```
Expected: 100% Exit Code 0 (Ruff, Pytest, Vitest, Web build).

- [ ] **Step 5: Commit và đẩy lên GitHub**

```bash
git add report-datn/main.pdf tests/
git commit -m "docs(datn): finalize thesis report with streamlined database and centered tables"
git push origin main
bash scripts/deploy_to_vps.sh --fast
```
