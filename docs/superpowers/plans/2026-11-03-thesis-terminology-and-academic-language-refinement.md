# Kế Hoạch Thực Hiện: Chuẩn Hóa Ngôn Từ Kỹ Thuật Học Thuật & Thuật Ngữ BYOK Trong Luận Văn (Academic Terminology Radical Polish)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuẩn hóa toàn bộ thuật ngữ chuyên ngành trong luận văn tốt nghiệp VeriScholar, loại bỏ triệt để các cụm từ dịch gượng gạo ("Két an toàn khóa cá nhân", "cô lập hạt nhân"), diễn giải chuẩn mực quốc tế cho Bring Your Own Key (BYOK), bảo đảm văn phong khoa học máy tính chuẩn mực trên Mục lục và toàn văn báo cáo.

**Architecture:** Sử dụng phương pháp kiểm thử hồi quy hướng kiểm thử (TDD) để khóa cứng bộ từ khóa cấm ("Két an toàn", "két khóa", "cô lập hạt nhân"), cập nhật đồng bộ từ định nghĩa từ viết tắt, tiêu đề phân mục, nội dung phân tích bảo mật đến nhãn sơ đồ kiến trúc, sau đó biên dịch XeLaTeX tái tạo toàn bộ tệp Mục lục (`main.toc`) và xác minh bằng 4 Verification Gates.

**Tech Stack:** XeLaTeX, Python 3.12, Pytest, Pydantic, FastAPI, React 19.

**Spec:** [`../specs/2026-11-03-thesis-terminology-and-academic-language-refinement-design.md`](../specs/2026-11-03-thesis-terminology-and-academic-language-refinement-design.md)

---

## Global Constraints

- **Quy chuẩn Markdown & Liên kết tương đối (Rule 5):** Tuyệt đối cấm sử dụng URL tuyệt đối `file://` trong toàn bộ tài liệu Markdown. Mọi liên kết tham chiếu phải dùng đường dẫn tương đối.
- **Quy chuẩn ngôn từ tối giản & chuẩn học thuật (Rule 6):** Tuyệt đối cấm sử dụng các từ ngữ dịch máy thô ráp, đồ vật gia dụng/ngân hàng ("két an toàn", "két khóa") hoặc nhầm lẫn vật lý nguyên tử ("cô lập hạt nhân" thay vì "cô lập mức nhân hệ điều hành").
- **Thuật ngữ viết tắt quốc tế:** Đối với BYOK, phải diễn giải rõ ràng tiếng Anh `Bring Your Own Key` cùng khái niệm tiếng Việt học thuật `Mô hình quản lý khóa người dùng tự cấp`, sau đó đính kèm ký hiệu `(BYOK)` trên Mục lục và tiêu đề bài.
- **Bốn Cổng Xác Minh Bắt Buộc (The 4 Verification Gates):** Trước khi hoàn thành kế hoạch, bắt buộc 100% exit code 0 cho `ruff`, `pytest`, `npm test`, `npm build`.
- **Đồng bộ VPS tự động sau mỗi commit (Rule 7):** Sau mỗi commit git thành công, chạy `bash scripts/deploy_to_vps.sh --fast`.

---

## Review Focus

1. **Triệt tiêu lỗi "Két an toàn" trên Mục lục và văn bản:** Xác nhận tiêu đề Mục 2.5.4 hiển thị chuẩn xác `2.5.4 Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK) và chuẩn mã hóa AES-256-GCM`.
2. **Triệt tiêu lỗi "Cô lập hạt nhân":** Xác nhận Mục 2.5.3 và Hình 2-4 không còn bất kỳ chữ "hạt nhân" nào, chuyển thành "cô lập cấp hệ điều hành" và "cô lập cấp nhân".
3. **Đồng bộ toàn bộ các chương:** Quét tự động xác nhận số lượng từ cấm xuất hiện trong `report-datn/chapters/` đạt chính xác bằng **0**.
4. **Tính nhất quán Danh mục viết tắt:** Bổ sung mục từ `BYOK` và chuẩn hóa giải nghĩa `AES-GCM` trong `danh_muc_viet_tat.tex`.
5. **Độ ổn định biên dịch XeLaTeX:** Biên dịch tài liệu không làm thay đổi ngân sách số trang (chương 1 bắt đầu tại trang 1, ngân sách trang chuẩn mực).

---

## Task 1: Thiết Lập Test Hồi Quy TDD Khóa Cứng Thuật Ngữ Học Thuật

**Files:**
- Create: `tests/test_thesis_academic_terminology.py`

**Interfaces:**
- Consumes: Toàn bộ các tệp `.tex` trong `report-datn/chapters/` và `report-datn/frontmatter/`.
- Produces: Test tự động kiểm tra sự vắng mặt của các từ khóa cấm và sự hiện diện của các tiêu đề học thuật chuẩn hóa.

- [ ] **Step 1: Viết test đỏ `test_thesis_academic_terminology.py`**
  ```python
  from pathlib import Path
  import pytest

  def test_no_clunky_terminology_in_chapters():
      chapters_dir = Path("report-datn/chapters")
      forbidden_phrases = [
          "két an toàn",
          "Két an toàn",
          "két khóa",
          "Két khóa",
          "cô lập hạt nhân",
          "ranh giới hạt nhân",
      ]
      violations = []
      for tex_file in chapters_dir.rglob("*.tex"):
          content = tex_file.read_text(encoding="utf-8")
          for phrase in forbidden_phrases:
              if phrase in content:
                  violations.append(f"{tex_file}: contains forbidden phrase '{phrase}'")
      assert not violations, "Found forbidden clunky terminology:\n" + "\n".join(violations)

  def test_byok_terminology_standards():
      sec_2_5 = Path("report-datn/chapters/ch2/2_5_agentic_react.tex").read_text(encoding="utf-8")
      assert "Bring Your Own Key (BYOK)" in sec_2_5
      assert "\\subsection{Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK)" in sec_2_5
      assert "cô lập hạt nhân" not in sec_2_5
      assert "Môi trường máy ảo MicroVM E2B cô lập cấp hệ điều hành" in sec_2_5

  def test_byok_in_abbreviations_table():
      abbr = Path("report-datn/frontmatter/danh_muc_viet_tat.tex").read_text(encoding="utf-8")
      assert "BYOK" in abbr
      assert "Bring Your Own Key" in abbr
  ```

- [ ] **Step 2: Chạy test để xác nhận test đỏ (RED)**
  ```bash
  uv run pytest tests/test_thesis_academic_terminology.py
  ```
  Xác nhận: Test thất bại do các từ "Két an toàn", "két khóa", "cô lập hạt nhân" đang tồn tại trong mã nguồn.

---

## Task 2: Chuẩn Hóa Ngôn Từ Học Thuật Chương 2 (`2_5_agentic_react.tex`)

**Files:**
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex:35-140`

**Interfaces:**
- Consumes: Tiêu đề Mục 2.5.3, Mục 2.5.4, nhãn Hình 2-4.
- Produces: Ngôn từ học thuật chuẩn xác, thay "cô lập hạt nhân" bằng "cô lập cấp hệ điều hành / cấp nhân", thay "Két an toàn khóa cá nhân BYOK" bằng "Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK)".

- [ ] **Step 1: Cập nhật Mục 2.5.3**
  - Sửa `\subsection{Môi trường MicroVM cô lập hạt nhân E2B và vòng lặp tự sửa lỗi LaTeX}`  
    $\to$ `\subsection{Môi trường máy ảo MicroVM E2B cô lập cấp hệ điều hành và vòng lặp tự sửa lỗi LaTeX}`
  - Dòng 44: Sửa `Cô lập ranh giới hạt nhân (\textit{Kernel-level Isolation})`  
    $\to$ `Cô lập mức nhân hệ điều hành (\textit{Kernel-level Isolation})`
  - Hình 2-4 dòng 86: Sửa `Môi trường Linux cô lập hạt nhân`  
    $\to$ `Môi trường Linux cô lập cấp nhân`

- [ ] **Step 2: Cập nhật Mục 2.5.4**
  - Sửa `\subsection{Két an toàn khóa cá nhân BYOK và chuẩn mã hóa xác thực AES-256-GCM}`  
    $\to$ `\subsection{Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK) và chuẩn mã hóa AES-256-GCM}`
  - Dòng 128: Sửa `mô hình két an toàn khóa cá nhân (BYOK...`  
    $\to$ `mô hình quản lý khóa người dùng tự cấp (BYOK -- \textit{Bring Your Own Key})`
  - Dòng 130: Sửa `kho lưu trữ két khóa bảo mật`  
    $\to$ `kho lưu trữ khóa mã hóa cá nhân`

- [ ] **Step 3: Chạy test kiểm tra tiến độ**
  ```bash
  uv run pytest tests/test_thesis_academic_terminology.py -k "test_byok_terminology_standards"
  ```
  Xác nhận: Pass test riêng phần Chương 2.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch2/2_5_agentic_react.tex
  git commit -m "style(thesis): standardize academic terminology in chapter 2 for byok and kernel isolation"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 3: Chuẩn Hóa Đồng Bộ Toàn Bộ Các Chương 1, 3, Kết Luận & Bổ Sung Danh Mục Viết Tắt

**Files:**
- Modify: `report-datn/chapters/ch1/1_3_muc_tieu.tex:17`
- Modify: `report-datn/chapters/ch3/3_3_kien_truc.tex:83`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:291`
- Modify: `report-datn/chapters/ket_luan.tex:13`
- Modify: `report-datn/frontmatter/danh_muc_viet_tat.tex:10-35`

**Interfaces:**
- Consumes: Toàn bộ các vị trí còn tồn đọng chữ "két khóa", "két an toàn".
- Produces: Tài liệu thuần nhất ngôn ngữ học thuật, bổ sung mục từ viết tắt BYOK.

- [ ] **Step 1: Cập nhật Chương 1 (`1_3_muc_tieu.tex:17`)**
  - Đổi `Thiết lập cơ chế két khóa bảo mật cá nhân (BYOK...`  
    $\to$ `Thiết lập cơ chế quản lý khóa người dùng tự cấp theo mô hình Bring Your Own Key (BYOK) mã hóa bằng chuẩn AES-256-GCM...`

- [ ] **Step 2: Cập nhật Chương 3 (`3_3_kien_truc.tex:83` & `3_6_thiet_ke_csdl.tex:291`)**
  - Trong Hình 3-2: `Quy tắc nghiệp vụ miền $\bullet$ Quản trị phiên $\bullet$ Két khóa BYOK Envelope`  
    $\to$ `Quy tắc nghiệp vụ miền $\bullet$ Quản trị phiên $\bullet$ Quản lý khóa BYOK Envelope`
  - Trong Mục 3.6: `két khóa API cá nhân (\texttt{users}...`  
    $\to$ `kho lưu trữ khóa API cá nhân theo mô hình BYOK (\texttt{users}...`

- [ ] **Step 3: Cập nhật Chương Kết luận (`ket_luan.tex:13`)**
  - Sửa `Bảo mật két khóa BYOK` $\to$ `Bảo mật khóa API theo mô hình BYOK`
  - Sửa `đi kèm cơ chế két khóa cá nhân BYOK` $\to$ `đi kèm cơ chế quản lý khóa người dùng tự cấp BYOK`

- [ ] **Step 4: Cập nhật Danh mục từ viết tắt (`danh_muc_viet_tat.tex`)**
  - Bổ sung dòng mục từ cho `BYOK`:
    ```latex
    BYOK & Bring Your Own Key -- Mô hình quản lý khóa bảo mật do người dùng tự cung cấp \\ \hline
    ```
  - Chuẩn hóa dòng `AES-GCM`:
    ```latex
    AES-GCM & Advanced Encryption Standard -- Galois/Counter Mode -- Chuẩn mã hóa xác thực khóa API BYOK \\ \hline
    ```

- [ ] **Step 5: Chạy test TDD xác nhận GREEN 100%**
  ```bash
  uv run pytest tests/test_thesis_academic_terminology.py
  ```
  Xác nhận: 3/3 test passed, không còn bất kỳ vi phạm từ ngữ thô nào.

- [ ] **Step 6: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ report-datn/frontmatter/ tests/test_thesis_academic_terminology.py
  git commit -m "style(thesis): eliminate clunky terms across all chapters and add byok to abbreviations"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 4: Biên Dịch XeLaTeX Tái Tạo Mục Lục, Kiểm Định Bốn Cổng & Xuất Bản

**Files:**
- Modify: `report-datn/main.toc` (sinh tự động)
- Modify: `report-datn/main.pdf` (sinh tự động)

**Interfaces:**
- Consumes: Toàn bộ mã nguồn LaTeX đã chuẩn hóa.
- Produces: `report-datn/main.pdf` với Mục lục hoàn chỉnh, hiển thị chuẩn `2.5.4 Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK)...`, 100% test xanh.

- [ ] **Step 1: Biên dịch XeLaTeX 2 lần trong thư mục `report-datn`**
  ```bash
  cd report-datn && xelatex -interaction=nonstopmode -file-line-error main.tex && xelatex -interaction=nonstopmode -file-line-error main.tex && cd ..
  ```
  Xác nhận: Exit code 0, tạo `main.pdf` 74 trang.

- [ ] **Step 2: Kiểm tra trực quan nội dung Mục lục trong PDF**
  ```bash
  pdftotext -f 10 -l 11 report-datn/main.pdf - | grep "2.5.4"
  ```
  Xác nhận: Dòng 2.5.4 hiển thị `Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK) và chuẩn mã hóa AES-256-GCM`.

- [ ] **Step 3: Chạy toàn bộ 4 Verification Gates**
  ```bash
  uv run ruff check . && uv run ruff format --check .
  uv run pytest
  npm --prefix apps/web run test
  npm --prefix apps/web run build
  python3 scripts/verify_thesis_format.py
  ```
  Xác nhận: 100% Exit Code 0.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/main.pdf report-datn/main.toc
  git commit -m "build(thesis): update compiled pdf with professional academic terminology in toc and body"
  bash scripts/deploy_to_vps.sh --fast
  ```
