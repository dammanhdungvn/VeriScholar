# Kế Hoạch Triển Khai Kiến Trúc Báo Cáo ĐATN LaTeX & Bộ Quy Tắc VeriScholar

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khởi tạo toàn bộ bộ quy tắc bất biến `report-datn/RULES.md`, khung mã nguồn LaTeX mô-đun hóa hỗ trợ 100% XeLaTeX tiếng Việt, cấu hình phím tắt VSCode (`Ctrl+Alt+B`), và bài kiểm thử tự động toàn vẹn tài liệu cho đồ án tốt nghiệp: "Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn".

**Architecture:** Sử dụng kiến trúc đa tệp mô-đun hóa tách biệt rõ ràng giữa tệp điều phối `main.tex`, cấu hình trình bày `config/preamble.tex`, các trang sơ bộ `frontmatter/`, khung sườn 4 chương học thuật `chapters/`, sơ đồ `figures/` và tài liệu tham khảo theo Phụ lục 03 HUMG. Toàn bộ quy chuẩn và chiến lược chắt lọc tài liệu được hợp nhất vào một tệp kim chỉ nam duy nhất `report-datn/RULES.md`.

**Tech Stack:** XeLaTeX (`fontspec`, `Liberation Serif`), `babel` Vietnamese, `geometry` (margins 2.5/2.5/3.5/2.5cm), `scrextend` (13pt), `setspace` (1.5 lines), `fancyhdr`, VSCode LaTeX Workshop, Python AST & Pytest.

**Spec:** [`docs/superpowers/specs/2026-10-26-thesis-latex-architecture-design.md`](../specs/2026-10-26-thesis-latex-architecture-design.md)

## Global Constraints

* Phông chữ: Chuẩn tương đương Microsoft Times New Roman (`Liberation Serif` trên Linux), cỡ chữ `13pt`, mật độ bình thường.
* Căn lề trang: Lề trên `2.5cm`, lề dưới `2.5cm`, lề trái `3.5cm` (đóng gáy), lề phải `2.5cm`.
* Dãn dòng: Đặt ở chế độ `1.5 lines` (`\onehalfspacing`).
* Đánh số trang: Phần đầu đánh số La Mã in thường (`i`, `ii`...), phần thân bài đánh số Ả Rập (`1`, `2`...) ở góc dưới bên phải trang. Chân trang bên trái ghi `SVTH: Đàm Mạnh Dũng -- Ngành Công nghệ thông tin`.
* Cấm tuyệt đối: Lỗi font tiếng Việt có dấu, tiểu mục mồ côi (có x.y.1 phải có x.y.2), tham chiếu tương đối ("hình dưới", "bảng sau"), ngôi thứ nhất ("tôi", "em", "chúng tôi").
* Quy tắc liên kết Markdown: 100% liên kết trong tài liệu markdown phải là đường dẫn tương đối (Relative links only theo AGENTS.md Quy tắc 5).

## Review Focus

* Lỗi font hoặc thiếu ký tự tiếng Việt có dấu: Kiểm thử toàn bộ 134 nguyên âm có dấu trong tiếng Việt (`ắ, ằ, ẳ, ẵ, ặ, ế, ề, ể, ễ, ệ, ố, ồ, ổ, ỗ, ộ, ứ, ừ, ử, ữ, ự, ỳ, ỷ, ỹ, ỵ...`) khi xuất ra file PDF.
* Lỗi biên dịch multi-pass tài liệu tham khảo: Khối `thebibliography` phân tách rõ 2 mục Tiếng Việt và Tiếng Anh đúng Phụ lục 03, giải quyết bằng 1 pass `xelatex` không sinh lỗi `[?]`.
* Lỗi cấu hình lề và cỡ chữ trong `report.cls`: Đảm bảo `scrextend` nạp cỡ 13pt chính xác mà không xung đột lớp văn bản.
* Lỗi đường dẫn tương đối trong VSCode LaTeX Workshop: Đặt cờ `% !TEX root = ../main.tex` ở tất cả các tệp con để người dùng mở bất kỳ tệp nào gõ `Ctrl+Alt+B` đều biên dịch tệp gốc.
* 4 Cổng Xác Minh Bắt Buộc (scripts/dev/verify.sh): Đảm bảo 100% exit code 0 sau khi hoàn thành.

---

### Task 1: Khởi Tạo Bộ Quy Tắc Kim Chỉ Nam `report-datn/RULES.md`

**Files:**
- Create: `report-datn/RULES.md`
- Test: `tests/test_thesis_rules.py`

**Interfaces:**
- Consumes: Hướng dẫn HUMG `report-datn/guide/Huong-dan-viet-DATN.md`, 2 đồ án mẫu của Hiếu và Bắc, bản thiết kế `docs/superpowers/specs/2026-10-26-thesis-latex-architecture-design.md`.
- Produces: Tệp kim chỉ nam duy nhất `report-datn/RULES.md` chứa trọn vẹn 3 phần: Kiến trúc kỹ thuật, Quy chuẩn hành văn bất biến, Ma trận lọc tài liệu (Keep vs. Omit).

- [ ] **Step 1: Viết test kiểm tra tính toàn vẹn của tệp `report-datn/RULES.md`**

Tạo bài kiểm thử trong `tests/test_thesis_rules.py`:
```python
from pathlib import Path


def test_thesis_rules_file_exists_and_valid():
    rules_path = Path("report-datn/RULES.md")
    assert rules_path.exists(), "report-datn/RULES.md must exist"
    content = rules_path.read_text(encoding="utf-8")

    # Kiểm tra các phần cốt lõi bắt buộc
    required_sections = [
        "KIẾN TRÚC & CẤU HÌNH KỸ THUẬT XELATEX",
        "QUY CHUẨN ĐỊNH DẠNG TRANG & HÌNH THỨC",
        "VĂN PHONG & QUY TẮC HÀNH VĂN BẤT BIẾN",
        "QUY TẮC BẢNG BIỂU, HÌNH VẼ & DẪN CHIẾU CHÉO",
        "CHIẾN LƯỢC CHẮT LỌC NỘI DUNG TỪ DOCS",
    ]
    for section in required_sections:
        assert section in content, f"Missing required section: {section}"

    # Kiểm tra không chứa URL tuyệt đối (Quy tắc 5 AGENTS.md)
    assert "file://" not in content, "RULES.md must not contain file:// links"
```

- [ ] **Step 2: Chạy kiểm thử để xác nhận test đỏ (FAIL)**

Run: `uv run pytest tests/test_thesis_rules.py -v`
Expected: FAIL vì `report-datn/RULES.md` chưa tồn tại.

- [ ] **Step 3: Soạn thảo tệp `report-datn/RULES.md` toàn diện**

Tạo `report-datn/RULES.md` hợp nhất đầy đủ:
1. Thông tin tác giả: Đàm Mạnh Dũng, Ngành CNTT, Trường Đại học Mỏ - Địa chất.
2. Quy định khổ giấy A4, lề trên 2.5cm, dưới 2.5cm, trái 3.5cm, phải 2.5cm, font 13pt, dãn dòng 1.5 lines.
3. Nguyên tắc đánh số trang và chân trang.
4. 4 nguyên tắc văn phong học thuật (ngôi thứ 3 khách quan, lập luận tại sao chọn công nghệ, đặc tả BA chuẩn, số liệu thực chứng).
5. Luật cấm tiểu mục mồ côi ($\ge 2$ mục con).
6. Luật đặt caption: Bảng ở TRÊN, hình ở DƯỚI. Cấm dẫn chiếu mơ hồ.
7. Ma trận chắt lọc nội dung từ `docs/` (Keep vs. Omit).

- [ ] **Step 4: Chạy lại kiểm thử để xác nhận test xanh (PASS)**

Run: `uv run pytest tests/test_thesis_rules.py -v`
Expected: PASS (Exit code 0).

- [ ] **Step 5: Git commit**

```bash
git add report-datn/RULES.md tests/test_thesis_rules.py
git commit -m "docs(report): create comprehensive RULES.md for thesis writing"
```

---

### Task 2: Cấu Hình Môi Trường VSCode LaTeX Workshop & Latexmk

**Files:**
- Modify: `.vscode/settings.json`
- Create: `report-datn/.latexmkrc`
- Test: `tests/test_thesis_vscode_config.py`

**Interfaces:**
- Consumes: Môi trường VSCode và LaTeX Workshop của James Yu.
- Produces: Cấu hình build tự động XeLaTeX khi ấn `Ctrl+Alt+B` và cấu hình xem PDF qua `Ctrl+Alt+V`.

- [ ] **Step 1: Viết test kiểm tra cấu hình LaTeX Workshop**

Tạo bài kiểm thử trong `tests/test_thesis_vscode_config.py`:
```python
import json
from pathlib import Path


def test_vscode_latex_settings():
    settings_path = Path(".vscode/settings.json")
    assert settings_path.exists()
    settings = json.loads(settings_path.read_text(encoding="utf-8"))

    # Đảm bảo cấu hình XeLaTeX tool và recipe
    assert "latex-workshop.latex.tools" in settings
    tools = {t["name"]: t for t in settings["latex-workshop.latex.tools"]}
    assert "xelatex" in tools
    assert tools["xelatex"]["command"] == "xelatex"

    assert "latex-workshop.latex.recipes" in settings
    recipes = {r["name"]: r for r in settings["latex-workshop.latex.recipes"]}
    assert "xelatex" in recipes
```

- [ ] **Step 2: Chạy kiểm thử để xác nhận test đỏ (FAIL)**

Run: `uv run pytest tests/test_thesis_vscode_config.py -v`
Expected: FAIL vì `.vscode/settings.json` chưa có cấu hình LaTeX Workshop.

- [ ] **Step 3: Cập nhật cấu hình trong `.vscode/settings.json` và tạo `report-datn/.latexmkrc`**

Thêm vào `.vscode/settings.json`:
* `latex-workshop.latex.tools`: Thêm tool `xelatex` với args `["-synctex=1", "-interaction=nonstopmode", "-file-line-error", "%DOC%"]`.
* `latex-workshop.latex.recipes`: Thêm recipe `xelatex` sử dụng tool `xelatex`.
* `latex-workshop.view.pdf.viewer`: `"tab"`.
* `latex-workshop.latex.autoBuild.run`: `"never"` (tránh tự build ngầm khi đang gõ dở, chỉ build khi ấn `Ctrl+Alt+B`).

Tạo `report-datn/.latexmkrc`:
```perl
$pdf_mode = 5; # 5 = xelatex
$xelatex = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
```

- [ ] **Step 4: Chạy lại kiểm thử để xác nhận test xanh (PASS)**

Run: `uv run pytest tests/test_thesis_vscode_config.py -v`
Expected: PASS (Exit code 0).

- [ ] **Step 5: Git commit**

```bash
git add .vscode/settings.json report-datn/.latexmkrc tests/test_thesis_vscode_config.py
git commit -m "chore(report): configure vscode latex workshop and latexmk for xelatex"
```

---

### Task 3: Thiết Lập Cấu Hình LaTeX `config/preamble.tex` & `config/commands.tex`

**Files:**
- Create: `report-datn/config/preamble.tex`
- Create: `report-datn/config/commands.tex`
- Test: `tests/test_thesis_preamble.py`

**Interfaces:**
- Consumes: Bộ gói lệnh XeLaTeX, phông `Liberation Serif`, gói `geometry`, `scrextend`, `fancyhdr`.
- Produces: Hệ thống macro và định dạng hiển thị sẵn sàng cho toàn bộ các chương.

- [ ] **Step 1: Viết test kiểm tra tệp cấu hình LaTeX**

Tạo bài kiểm thử trong `tests/test_thesis_preamble.py`:
```python
from pathlib import Path


def test_preamble_configuration():
    preamble_path = Path("report-datn/config/preamble.tex")
    assert preamble_path.exists()
    content = preamble_path.read_text(encoding="utf-8")

    # Kiểm tra các thông số quy chuẩn HUMG
    assert "top=2.5cm" in content
    assert "bottom=2.5cm" in content
    assert "left=3.5cm" in content
    assert "right=2.5cm" in content
    assert "fontsize=13pt" in content
    assert "Liberation Serif" in content
    assert "Đàm Mạnh Dũng" in content
```

- [ ] **Step 2: Chạy kiểm thử để xác nhận test đỏ (FAIL)**

Run: `uv run pytest tests/test_thesis_preamble.py -v`
Expected: FAIL vì `report-datn/config/preamble.tex` chưa tồn tại.

- [ ] **Step 3: Khởi tạo `config/preamble.tex` và `config/commands.tex`**

Viết `report-datn/config/preamble.tex` đầy đủ các gói:
* `geometry`: lề 2.5/2.5/3.5/2.5cm.
* `scrextend`: `fontsize=13pt`.
* `fontspec` + `babel`: phông `Liberation Serif`, ngôn ngữ tiếng Việt.
* `setspace`: `\onehalfspacing`.
* `fancyhdr`: chân trang bên trái in nghiêng tên tác giả và ngành, bên phải in số trang.
* `caption`: `\captionsetup[table]{position=top}`, `\captionsetup[figure]{position=bottom}`.
* `hyperref`: cấu hình màu liên kết học thuật (`linkcolor=black`, `citecolor=blue`, `urlcolor=blue`).

Viết `report-datn/config/commands.tex`: các lệnh tiện ích viết tắt (`\VS` cho VeriScholar, `\RRF`, định nghĩa môi trường trích dẫn).

- [ ] **Step 4: Chạy lại kiểm thử để xác nhận test xanh (PASS)**

Run: `uv run pytest tests/test_thesis_preamble.py -v`
Expected: PASS (Exit code 0).

- [ ] **Step 5: Git commit**

```bash
git add report-datn/config/preamble.tex report-datn/config/commands.tex tests/test_thesis_preamble.py
git commit -m "feat(report): add latex preamble and commands with HUMG geometry standards"
```

---

### Task 4: Khởi Tạo Cấu Trúc Đa Tệp `frontmatter/`, `chapters/`, `figures/` & `main.tex`

**Files:**
- Create: `report-datn/frontmatter/loi_cam_on.tex`
- Create: `report-datn/frontmatter/loi_mo_dau.tex`
- Create: `report-datn/frontmatter/danh_muc_viet_tat.tex`
- Create: `report-datn/frontmatter/danh_muc_bang.tex`
- Create: `report-datn/frontmatter/danh_muc_hinh.tex`
- Create: `report-datn/frontmatter/bia_phu.tex`
- Create: `report-datn/chapters/ch1_tong_quan.tex`
- Create: `report-datn/chapters/ch2_co_so_ly_thuyet.tex`
- Create: `report-datn/chapters/ch3_thiet_ke_he_thong.tex`
- Create: `report-datn/chapters/ch4_thuc_nghiem.tex`
- Create: `report-datn/chapters/ket_luan.tex`
- Create: `report-datn/chapters/tai_lieu_tham_khao.tex`
- Create: `report-datn/figures/.gitkeep`
- Replace: `report-datn/main.tex` (thay thế CV cũ bằng tệp điều phối trung tâm chuẩn)
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Cấu hình từ `config/preamble.tex` và `config/commands.tex`.
- Produces: Bản nháp khung sườn hoàn chỉnh của đồ án biên dịch thành công sang `main.pdf`.

- [ ] **Step 1: Viết test kiểm tra cấu trúc thư mục và biên dịch XeLaTeX thực tế**

Tạo bài kiểm thử trong `tests/test_thesis_structure_and_compile.py`:
```python
from pathlib import Path
import subprocess


def test_thesis_files_exist():
    required_files = [
        "report-datn/main.tex",
        "report-datn/frontmatter/loi_cam_on.tex",
        "report-datn/frontmatter/loi_mo_dau.tex",
        "report-datn/frontmatter/danh_muc_viet_tat.tex",
        "report-datn/chapters/ch1_tong_quan.tex",
        "report-datn/chapters/ch2_co_so_ly_thuyet.tex",
        "report-datn/chapters/ch3_thiet_ke_he_thong.tex",
        "report-datn/chapters/ch4_thuc_nghiem.tex",
        "report-datn/chapters/ket_luan.tex",
        "report-datn/chapters/tai_lieu_tham_khao.tex",
    ]
    for file_path in required_files:
        assert Path(file_path).exists(), f"File must exist: {file_path}"


def test_thesis_compilation():
    res = subprocess.run(
        [
            "xelatex",
            "-interaction=nonstopmode",
            "-file-line-error",
            "main.tex",
        ],
        cwd="report-datn",
        capture_output=True,
        text=True,
    )
    assert (
        res.returncode == 0
    ), f"XeLaTeX compilation failed with log:\n{res.stdout[-1500:]}"
    assert Path("report-datn/main.pdf").exists()
```

- [ ] **Step 2: Chạy kiểm thử để xác nhận test đỏ (FAIL)**

Run: `uv run pytest tests/test_thesis_structure_and_compile.py -v`
Expected: FAIL vì các file chương và frontmatter chưa được tạo.

- [ ] **Step 3: Khởi tạo đầy đủ các tệp frontmatter, chapters và tệp điều phối `main.tex`**

* Thêm cờ `% !TEX root = ../main.tex` vào đầu mỗi tệp con.
* Soạn thảo `frontmatter/`:
  * `loi_cam_on.tex`: Lời cảm ơn thầy cô Bộ môn CNTT HUMG.
  * `loi_mo_dau.tex`: Dẫn nhập tổng quan (1 trang).
  * `danh_muc_viet_tat.tex`: Bảng từ viết tắt học thuật (AI, RAG, GraphRAG, CAS, SSE, LLM, BYOK).
  * `danh_muc_bang.tex`: `\listoftables`.
  * `danh_muc_hinh.tex`: `\listoffigures`.
  * `bia_phu.tex`: Trang bìa phụ theo mẫu Phụ lục 02.
* Soạn thảo `chapters/`:
  * `ch1_tong_quan.tex`: Khung 6 mục (1.1 đến 1.6) theo đúng đề cương chuẩn.
  * `ch2_co_so_ly_thuyet.tex`: Khung lý thuyết và luận giải "Tại sao chọn".
  * `ch3_thiet_ke_he_thong.tex`: Khung Use Case, Sequence Diagram và CSDL.
  * `ch4_thuc_nghiem.tex`: Khung môi trường, giao diện, kiểm thử 4 Cổng, số liệu thực nghiệm.
  * `ket_luan.tex`: Kết quả đạt được, hạn chế và hướng phát triển.
  * `tai_lieu_tham_khao.tex`: Môi trường `thebibliography` phân tách rõ *Tài liệu tiếng Việt* và *Tài liệu tiếng Anh*.
* Cập nhật `main.tex`:
  * `% !TEX program = xelatex`
  * Khai báo lớp `\documentclass[12pt,a4paper,oneside]{report}`
  * Điều phối đánh số trang La Mã (`\pagenumbering{roman}`) cho phần mở đầu và Ả Rập (`\pagenumbering{arabic}`) cho thân bài.

- [ ] **Step 4: Chạy biên dịch và kiểm thử để xác nhận test xanh (PASS)**

Run: `uv run pytest tests/test_thesis_structure_and_compile.py -v`
Expected: PASS (Exit code 0), tệp `report-datn/main.pdf` được tạo ra thành công.

- [ ] **Step 5: Git commit**

```bash
git add report-datn/ tests/test_thesis_structure_and_compile.py
git commit -m "feat(report): build full modular latex structure and compile main.pdf cleanly"
```

---

### Task 5: Xác Minh Toàn Diện Qua 4 Cổng (The 4 Verification Gates)

**Files:**
- Test: Chạy toàn bộ test suite dự án

**Interfaces:**
- Consumes: Toàn bộ codebase backend, frontend và report.
- Produces: Báo cáo xác minh 100% exit code 0 theo đúng AGENTS.md.

- [ ] **Step 1: Chạy Cổng 1 (Linter & Formatter)**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: Exit code 0 (All checks passed).

- [ ] **Step 2: Chạy Cổng 2 (Backend & Thesis Integrity Tests)**

Run: `uv run pytest`
Expected: 100% tests passed (Exit code 0).

- [ ] **Step 3: Chạy Cổng 3 (Frontend Unit Tests)**

Run: `npm --prefix apps/web run test`
Expected: Exit code 0.

- [ ] **Step 4: Chạy Cổng 4 (Frontend Production Build)**

Run: `npm --prefix apps/web run build`
Expected: Exit code 0.

- [ ] **Step 5: Git commit hoàn thiện**

```bash
git add .
git commit -m "chore(report): verify all 4 verification gates pass cleanly"
```
