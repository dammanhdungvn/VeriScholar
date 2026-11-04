# Chuẩn hóa Văn phong Kỹ thuật, Tối ưu Bố cục Mật độ và Tinh gọn Tài liệu tham khảo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuẩn hóa toàn diện văn phong học thuật thuần kỹ thuật (loại bỏ 100% `\cite` và tên tác giả kể lể), khử khoảng trắng thừa trang 54 bằng dòng chảy tự nhiên, tinh gọn danh mục tài liệu tham khảo thành 10 bài báo kinh điển A--Z không phân nhóm La Mã, và đồng bộ SSOT vào `AGENTS.md` / `INFORMATION.md`.

**Architecture:** Tái cấu trúc văn bản LaTeX bám sát 100% chuẩn mực `guide/HIeu.pdf`. Thay thế các đoạn văn dẫn chiếu tên tác giả bằng các câu khẳng định cơ chế kỹ thuật khách quan; gỡ bỏ các chỉ thị ngắt trang cưỡng bức (`\clearpage`) để văn bản và biểu đồ tuần tự chảy liên tục lấp kín trang 54; cấu trúc lại `tai_lieu_tham_khao.tex` thành danh mục phẳng 10 công trình khoa học quốc tế đầy đủ siêu dữ liệu xuất bản.

**Tech Stack:** XeLaTeX, TeX Live 2023, Python 3.12, Pytest, PyPDF.

**Spec:** `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/superpowers/specs/2026-11-04-thesis-technical-prose-and-layout-density-design.md`

## Global Constraints

- Phông chữ toàn văn bản là Times New Roman 13pt (`\fontsize{13pt}{16pt}\selectfont`).
- Khoảng cách dòng chuẩn 1.5 Word (`\setstretch{1.45}` hoặc `\onehalfspacing`), tuyệt đối không dùng `\singlespacing` để nén ép dòng trong các đoạn thân bài.
- Tuyệt đối cấm xuất hiện ký hiệu tham chiếu số `[N]` (dạng `[1]`, `[14]`) hoặc lệnh `\cite{...}` trong các chương nội dung (từ Chương 1 đến Chương 4).
- Cấm chèn `\clearpage` hoặc `\newpage` giữa các tiểu mục nhỏ trong cùng một chương; chỉ dùng `\chapter{}` để sang trang ở đầu chương mới.
- Danh mục tài liệu tham khảo phẳng, không chia tiêu đề La Mã, đúng 10 bài báo kinh điển quốc tế, sắp xếp thứ tự bảng chữ cái A--Z theo họ tác giả đầu tiên.
- 100% các cổng kiểm thử tự động và biên dịch XeLaTeX phải đạt mã thoát 0 (`bash scripts/dev/verify.sh`).

## Review Focus

1. **Lệnh `\cite` hoặc tên tác giả bị sót trong các file con:** Rà soát đệ quy toàn bộ thư mục `report-datn/chapters/` để chắc chắn không còn bất kỳ lệnh `\cite{` nào và không còn các cụm từ *"do ... và cộng sự đề xuất/giới thiệu"*.
2. **Hình ảnh hoặc bảng biểu bị đẩy nhảy trang tạo khoảng trống:** Sau khi gỡ bỏ `\clearpage` tại tiểu mục 3.4.5, kiểm tra trang 54 phải chứa $\ge 20$ dòng text và hình ảnh biểu đồ tuần tự đầu tiên (Hình 3-8) nối tiếp mượt mà.
3. **Mất thông tin siêu dữ liệu bài báo trong Tài liệu tham khảo:** Đảm bảo 10 bài báo giữ đầy đủ tên kỷ yếu/tạp chí, tập, số trang (ví dụ: `pp. 758--759` cho RRF), năm xuất bản.
4. **Xung đột kiểm thử định dạng cũ:** Bài kiểm tra `test_sequence_diagrams_no_newpage_and_flow` trong `test_layout_spacing.py` cần được cập nhật để không ép cứng `p_fig_3_8 == p_fig_3_9` của cấu trúc cũ.
5. **Tính nhất quán giữa SSOT và mã nguồn:** `INFORMATION.md` (Phần 6) và `AGENTS.md` phải khớp hoàn toàn danh mục 10 tài liệu tham khảo với `tai_lieu_tham_khao.tex`.

---

### Task 1: Loại bỏ toàn bộ `\cite` và Tái cấu trúc văn phong thuần kỹ thuật trong các chương

**Files:**
- Modify: `report-datn/chapters/ch2_co_so_ly_thuyet.tex`
- Modify: `report-datn/chapters/ch2/2_1_postgresql_redis.tex`
- Modify: `report-datn/chapters/ch2/2_2_hybrid_rag.tex`
- Modify: `report-datn/chapters/ch2/2_3_advanced_rag.tex`
- Modify: `report-datn/chapters/ch2/2_4_knowledge_graph_wiki.tex`
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex`
- Modify: `report-datn/chapters/ch2/2_7_azure_e2b_byok.tex`
- Create: `tests/report_datn/test_thesis_no_cite_in_body.py`

**Interfaces:**
- Consumes: Bản thảo hiện tại của Chương 2.
- Produces: Nội dung Chương 2 hoàn toàn không chứa `\cite{...}` hay tên tác giả kể lể; diễn đạt thuần túy cơ chế kỹ thuật.

- [ ] **Step 1: Viết test kiểm tra không còn `\cite` và tên tác giả trong thân bài**

Tạo `tests/report_datn/test_thesis_no_cite_in_body.py`:
```python
import re
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parents[2] / "report-datn"

def test_no_cite_commands_in_chapters():
    chapter_files = list((REPORT_DIR / "chapters").glob("**/*.tex"))
    # Exclude tai_lieu_tham_khao.tex which defines bibitems
    body_files = [f for f in chapter_files if f.name != "tai_lieu_tham_khao.tex"]
    
    violations = []
    for f in body_files:
        content = f.read_text(encoding="utf-8")
        matches = re.findall(r"\\cite\{[^}]+\}", content)
        if matches:
            violations.append(f"{f.name}: {matches}")
    
    assert not violations, f"Phát hiện lệnh \\cite trong thân bài: {violations}"

def test_no_conversational_author_phrases():
    chapter_files = list((REPORT_DIR / "chapters").glob("**/*.tex"))
    body_files = [f for f in chapter_files if f.name != "tai_lieu_tham_khao.tex"]
    
    forbidden_phrases = [
        "và cộng sự",
        "do Lewis",
        "theo khảo sát của Gao",
        "do Asai",
        "do Yan",
        "của Cockburn",
        "do Yao",
        "của Shinn",
        "của Weng",
    ]
    violations = []
    for f in body_files:
        content = f.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            if phrase in content:
                violations.append(f"{f.name}: chứa '{phrase}'")
    assert not violations, f"Phát hiện tên tác giả kể lể trong thân bài: {violations}"
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_thesis_no_cite_in_body.py -v`  
Expected: FAIL với danh sách các vi phạm `\cite` và cụm từ tác giả.

- [ ] **Step 3: Biên tập lại các đoạn văn trong Chương 2 sang văn phong thuần kỹ thuật**

Sửa đổi các file trong `report-datn/chapters/`:
- `ch2_co_so_ly_thuyet.tex`: Bỏ `~\cite{humg2022hd}`, `~\cite{cockburn2005}`, `~\cite{tiangolo2024fastapi}` và viết lại thành câu văn mô tả nguyên lý kiến trúc Lục giác, dịch vụ FastAPI và tiêu chuẩn đào tạo.
- `ch2/2_1_postgresql_redis.tex`: Bỏ các tham chiếu tác giả và `\cite{malkov2018}`, diễn đạt trực tiếp về thuật toán chỉ mục HNSW và độ phức tạp truy vấn $O(\log N)$.
- `ch2/2_2_hybrid_rag.tex`: Bỏ `\cite{robertson1995}`, `\cite{cormack2009}`, mô tả khách quan công thức Okapi BM25 và thuật toán Reciprocal Rank Fusion.
- `ch2/2_3_advanced_rag.tex`: Tái cấu trúc các đoạn văn mở đầu RAG, Advanced RAG, Self-RAG, CRAG thành câu văn kỹ thuật không chứa tên tác giả và mã `\cite`.
- `ch2/2_4_knowledge_graph_wiki.tex`: Bỏ `\cite{hogan2021kg}`, `~\cite{vaswani2017}`, `\cite{edge2024}`, `\cite{blondel2008louvain}`, `\cite{traag2019leiden}`.
- `ch2/2_5_agentic_react.tex`: Bỏ `\cite{wei2022cot}`, `\cite{schick2023toolformer}`, `\cite{yao2022}`, `\cite{shinn2023}`, `\cite{weng2023agent}`, `\cite{agache2020firecracker}`, `\cite{dworkin2007}`.
- `ch2/2_7_azure_e2b_byok.tex`: Bỏ `\cite{agache2020firecracker}`, `\cite{dworkin2007}`.

- [ ] **Step 4: Chạy test để xác nhận test vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_thesis_no_cite_in_body.py -v`  
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add tests/report_datn/test_thesis_no_cite_in_body.py report-datn/chapters/
git commit -m "style(thesis): eliminate cite commands and convert prose to purely technical style"
```

---

### Task 2: Khử khoảng trắng thừa Trang 54 và Tối ưu dòng chảy Biểu đồ tuần tự Mục 3.5

**Files:**
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex:440-456`
- Modify: `tests/report_datn/test_layout_spacing.py:191-220`

**Interfaces:**
- Consumes: Bố cục Mục 3.4 và Mục 3.5.
- Produces: Dòng chảy văn bản liền mạch không bị ngắt trang cưỡng bức giữa 3.4.5 và 3.5.

- [ ] **Step 1: Viết test kiểm tra mật độ dòng văn bản trang 54 và cấm `\clearpage` giữa tiểu mục**

Cập nhật `tests/report_datn/test_layout_spacing.py`:
- Thêm hàm kiểm tra trang 54 không bị rỗng:
```python
def test_page_54_density_and_no_clearpage_gap():
    pdf_path = Path("report-datn/main.pdf")
    if pdf_path.exists():
        res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
        pages = res.stdout.split("\x0c")
        assert len(pages) > 54
        page_54_lines = [l.strip() for l in pages[53].split("\n") if l.strip()]
        # Trang 54 phải chứa ít nhất 18 dòng nội dung (không bị hổng nửa trang)
        assert len(page_54_lines) >= 18, (
            f"Trang 54 quá thưa ({len(page_54_lines)} dòng). Phải đưa Mục 3.5 lên để khít đều!"
        )
```
- Điều chỉnh hàm `test_sequence_diagrams_no_newpage_and_flow`:
Xóa bỏ assertion ép cứng cũ `assert p_fig_3_8 == p_fig_3_9`, giữ nguyên kiểm tra không chứa `\newpage` cưỡng bức và đảm bảo cả 4 biểu đồ tuần tự xuất hiện đầy đủ trong các trang kế tiếp.

- [ ] **Step 2: Chạy test để xác nhận thất bại trước khi sửa file LaTeX (RED)**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -k "test_page_54_density" -v`  
Expected: FAIL (trang 54 hiện chỉ có ~12 dòng).

- [ ] **Step 3: Gỡ bỏ `\clearpage` cưỡng bức tại tiểu mục 3.4.5**

Trong `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`:
- Xóa bỏ `\FloatBarrier \clearpage` trước `\subsection{Cơ chế bảo mật và vận hành hệ thống phía Quản trị viên}`.
- Xóa bỏ `\clearpage` sau khi kết thúc danh sách `\begin{itemize} ... \end{itemize}` của tiểu mục 3.4.5.
- Biên dịch lại tài liệu bằng XeLaTeX (`cd report-datn && xelatex -interaction=nonstopmode main.tex`).

- [ ] **Step 4: Chạy test để xác nhận vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_layout_spacing.py -v`  
Expected: PASS toàn bộ các bài kiểm tra bố cục.

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/ch3/3_4_phan_tich_usecase.tex tests/report_datn/test_layout_spacing.py
git commit -m "fix(layout): eliminate clearpage gap on page 54 and allow continuous flow into section 3.5"
```

---

### Task 3: Tinh gọn Danh mục Tài liệu tham khảo thành 10 Bài báo kinh điển A--Z

**Files:**
- Modify: `report-datn/chapters/tai_lieu_tham_khao.tex`
- Modify: `tests/test_thesis_rules.py:113-136`
- Modify: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: 10 công trình khoa học quốc tế hạt nhân của đề tài.
- Produces: Danh mục phẳng 10 bài báo không phân nhóm La Mã, xếp theo thứ tự A--Z tác giả đầu tiên.

- [ ] **Step 1: Viết test xác thực danh mục 10 bài báo phẳng và sắp xếp A--Z**

Cập nhật `tests/report_datn/test_thesis_format_hieu.py`:
```python
def test_bibliography_10_milestone_papers_flat_alphabetical():
    ref_file = REPORT_DIR / "chapters/tai_lieu_tham_khao.tex"
    content = ref_file.read_text(encoding="utf-8")
    
    # Không chứa phân nhóm La Mã và không chứa quy chế HUMG
    assert "Tài liệu tiếng Việt" not in content, "Không được chứa tiêu đề 'Tài liệu tiếng Việt'"
    assert "Tài liệu tiếng Anh" not in content, "Không được chứa tiêu đề 'Tài liệu tiếng Anh'"
    assert "Khoa Công nghệ Thông tin" not in content, "Phải xóa bỏ tài liệu quy chế HUMG 2022"
    
    bibitems = re.findall(r"\\bibitem\{([^}]+)\}", content)
    assert len(bibitems) == 10, f"Danh mục phải có chính xác 10 bài báo, tìm thấy {len(bibitems)}"
    
    # Thứ tự A-Z chuẩn xác theo họ tác giả đầu tiên
    expected_order = [
        "asai2023selfrag",
        "cormack2009",
        "edge2024",
        "gao2023rag",
        "lewis2020",
        "malkov2018",
        "robertson1995",
        "shinn2023",
        "yan2024crag",
        "yao2022",
    ]
    assert bibitems == expected_order, f"Thứ tự tài liệu chưa đúng chuẩn A-Z: {bibitems}"
    
    # Đảm bảo đầy đủ siêu dữ liệu số trang và năm
    assert "758--759" in content
    assert "824--836" in content
    assert "9459--9474" in content
```

- [ ] **Step 2: Chạy test để xác nhận thất bại (RED)**

Run: `uv run pytest tests/report_datn/test_thesis_format_hieu.py -k "test_bibliography" -v`  
Expected: FAIL (danh mục cũ có phân nhóm và 20 tài liệu).

- [ ] **Step 3: Cập nhật `report-datn/chapters/tai_lieu_tham_khao.tex`**

Thay thế toàn bộ nội dung trong `\begin{thebibliography}{99} ... \end{thebibliography}` bằng đúng 10 mục chuẩn A--Z:
1. `\bibitem{asai2023selfrag} Asai, Akari, et al. (2023)...`
2. `\bibitem{cormack2009} Cormack, Gordon V., Clarke, Charles L., and Buettcher, Stefan (2009)...`
3. `\bibitem{edge2024} Edge, Darren, et al. (2024)...`
4. `\bibitem{gao2023rag} Gao, Yunfan, et al. (2023)...`
5. `\bibitem{lewis2020} Lewis, Patrick, et al. (2020)...`
6. `\bibitem{malkov2018} Malkov, Yury A., and Yashunin, Dmitry A. (2018)...`
7. `\bibitem{robertson1995} Robertson, Stephen E., et al. (1995)...`
8. `\bibitem{shinn2023} Shinn, Noah, et al. (2023)...`
9. `\bibitem{yan2024crag} Yan, Shi-Qi, et al. (2024)...`
10. `\bibitem{yao2022} Yao, Shunyu, et al. (2022)...`

- [ ] **Step 4: Chạy test để xác nhận vượt qua (GREEN)**

Run: `uv run pytest tests/report_datn/test_thesis_format_hieu.py -k "test_bibliography" -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add report-datn/chapters/tai_lieu_tham_khao.tex tests/report_datn/test_thesis_format_hieu.py
git commit -m "refactor(references): curate bibliography to 10 milestone papers in flat alphabetical order"
```

---

### Task 4: Đồng bộ SSOT `INFORMATION.md` và Cập nhật Quy tắc Bất biến vào `AGENTS.md`

**Files:**
- Modify: `report-datn/INFORMATION.md:161-188`
- Modify: `report-datn/AGENTS.md`
- Modify: `tests/test_thesis_rules.py:113-136`

**Interfaces:**
- Consumes: Danh mục 10 tài liệu tham khảo và các quy tắc cấm mới.
- Produces: Tài liệu SSOT và AGENTS.md đồng bộ 100% không còn mẫu thuẫn.

- [ ] **Step 1: Viết test kiểm tra sự đồng bộ trong `INFORMATION.md` và `AGENTS.md`**

Cập nhật `tests/test_thesis_rules.py`:
```python
def test_ssot_and_agents_reference_invariants():
    info = Path("report-datn/INFORMATION.md").read_text(encoding="utf-8")
    agents = Path("report-datn/AGENTS.md").read_text(encoding="utf-8")
    
    assert "10 tài liệu tham khảo" in info or "10 TÀI LIỆU THAM KHẢO" in info
    assert "I. Tài liệu tiếng Việt" not in info
    assert "II. Tài liệu tiếng Anh" not in info
    assert "cấm sử dụng các ký hiệu trích dẫn" in agents or "Tuyệt đối không sử dụng" in agents
```

- [ ] **Step 2: Chạy test để xác nhận thất bại (RED)**

Run: `uv run pytest tests/test_thesis_rules.py -k "test_ssot_and_agents" -v`  
Expected: FAIL

- [ ] **Step 3: Cập nhật `INFORMATION.md` và `AGENTS.md`**

- Trong `report-datn/INFORMATION.md`:
  Sửa tiêu đề Phần 6 thành: `## PHẦN 6: DANH MỤC 10 TÀI LIỆU THAM KHẢO CHÍNH THỨC CỦA ĐỀ TÀI (GIỚI HẠN TỐI ĐA <= 20)`.
  Liệt kê đúng 10 bài báo khoa học quốc tế, xóa bỏ toàn bộ mục I tiếng Việt và mục II tiếng Anh.
- Trong `report-datn/AGENTS.md`:
  Thêm mục quy tắc:
  - **Quy tắc cấm trích dẫn số trong thân bài:** Nghiêm cấm đặt `\cite{...}` hoặc `[1]`, `[14]` trong các chương nội dung. Câu văn phải diễn đạt khách quan, thuần kỹ thuật, không kể lể tên tác giả.
  - **Quy tắc dòng chảy liên tục:** Cấm chèn `\clearpage` giữa các tiểu mục nhỏ trong chương; nội dung phải khít khao tự nhiên.
  - **Quy tắc Tài liệu tham khảo:** Đúng 10 bài báo kinh điển A--Z phẳng, không phân nhóm La Mã.

- [ ] **Step 4: Chạy test để xác nhận vượt qua (GREEN)**

Run: `uv run pytest tests/test_thesis_rules.py -v`  
Expected: PASS toàn bộ các test quy tắc.

- [ ] **Step 5: Commit**

```bash
git add report-datn/INFORMATION.md report-datn/AGENTS.md tests/test_thesis_rules.py
git commit -m "docs(rules): synchronize SSOT INFORMATION.md and codify reference and layout rules in AGENTS.md"
```

---

### Task 5: Biên dịch Toàn diện và Xác thực 4 Cổng Kiểm soát Chất lượng (`verify.sh`)

**Files:**
- Output: `report-datn/main.pdf`
- Output: `report-datn/main.log`
- Script: `scripts/dev/verify.sh`

**Interfaces:**
- Consumes: Toàn bộ mã nguồn báo cáo và bài test đã cập nhật.
- Produces: Bản PDF hoàn thiện 100%, 0 lỗi, toàn bộ 4 Cổng kiểm soát chất lượng đạt Exit Code 0.

- [ ] **Step 1: Biên dịch XeLaTeX 2 lần để cập nhật số trang và Mục lục**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```
Xác nhận trong `main.log`: 0 lỗi biên dịch, không có overfull hbox trong các phần chỉnh sửa.

- [ ] **Step 2: Chạy kiểm tra định dạng báo cáo nghiệm thu**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar
uv run python scripts/verify_thesis_format.py
```
Expected: `ALL 4 CRITICAL ACCEPTANCE CHECKS PASSED 100%!`

- [ ] **Step 3: Chạy toàn bộ 4 Cổng Kiểm soát Chất lượng (`verify.sh`)**

```bash
bash scripts/dev/verify.sh
```
Expected: Cả 4 Gate (Ruff, Pytest backend + report tests, XeLaTeX build, Vite build) đều PASSED (100% Exit Code 0).

- [ ] **Step 4: Kiểm tra trực quan trang 54 bằng ảnh chụp PNG**

```bash
pdftoppm -png -r 150 -f 54 -l 54 report-datn/main.pdf /tmp/page54_check
```
Xác nhận trang 54 đầy đặn, không có khoảng trắng thừa nửa trang, Mục 3.5 tiếp nối liền mạch.

- [ ] **Step 5: Commit và đẩy lên remote**

```bash
git add report-datn/main.pdf
git commit -m "build(report): recompile final thesis PDF with dense continuous layout and clean references"
git push origin main
```
