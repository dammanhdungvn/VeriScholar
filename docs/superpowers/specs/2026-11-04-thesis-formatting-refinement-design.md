# Design Document: Thesis Formatting Refinement & Strict Hieu.pdf Conformance

**Document Path:** `docs/superpowers/specs/2026-11-04-thesis-formatting-refinement-design.md`  
**Date:** 2026-11-04  
**Author:** Antigravity  
**Status:** In Review  

---

## 1. Intent & Context

### 1.1 Background
The user provided advisor-mandated feedback requiring the graduation thesis report (`report-datn`) to strictly match the reference thesis `guide/HIeu.pdf` (written by student **Phạm Quốc Bảo**, MSSV: 2221050555, Class: DCCTCT67-09B, Supervisor: ThS. Vũ Lan Phương).

### 1.2 Core Issues to Resolve
1. **Cover 1 (`bia_chinh.tex`):** Extraneous `"KHOÁ 67"` printed on the front cover face (above `"Hà Nội – Năm 2026"`). In `HIeu.pdf`, `"KHOÁ 67"` only belongs on the 90° rotated spine.
2. **Phiếu giao đề tài (`phieu_giao_de_tai.tex`):** Names `"ThS. Vũ Lan Phương"` and `"Đàm Mạnh Dũng"` were pre-printed in the signature block. In `HIeu.pdf` (page 4), names must not be pre-printed; only the role titles (`Giảng viên hướng dẫn`, `Sinh viên thực hiện`) and `(Ký và ghi rõ họ tên)` appear, leaving blank space for hand-signatures.
3. **Đề cương ĐATN table formatting (`de_cuong_datn.tex`):** Cell text in the Student and Supervisor info tables overlaps column boundaries (`DCCTCT67_098846186...`) and collides with vertical borders due to fixed narrow `p{...}` columns.
4. **Signatures in Đề cương & Lời cảm ơn:**
   - Đề cương ĐATN: Remove the signature table and date block at the end of section 8 ("Nơi thực hiện ĐATN"), conforming 100% to `HIeu.pdf` page 8.
   - Lời cảm ơn (`loi_cam_on.tex`): Remove date, role, and student signature name block at the bottom, matching `HIeu.pdf` page 8.
5. **Danh mục hình ảnh & Danh mục bảng biểu (`danh_muc_hinh.tex`, `danh_muc_bang.tex`):** Forced `singlespace` violates the 1.5 Word line spacing mandate. Must use standard `\setstretch{1.45}`.
6. **Table Border Padding & Vertical/Horizontal Centering:**
   - Table borders must not cling to content; enforce explicit horizontal padding (`\tabcolsep = 6pt`) and vertical padding (`\arraystretch = 1.20` to `1.25`).
   - Content columns that require centering must be centered horizontally and vertically (`>{\centering\arraybackslash}m{...}`).
   - Left/right-aligned columns must be vertically centered (`>{\raggedright\arraybackslash}m{...}` or `>{\raggedleft\arraybackslash}m{...}`).
7. **Keyword & Academic Terminology (No Wordy Descriptions):**
   - Table columns and technical headings must use concise, globally recognized keywords (e.g., *Retrieval*, *Chunking*, *Dense Vector*, *Sparse BM25*, *BYOK*, *IoU*) instead of verbose conversational descriptions.
   - Codify into `report-datn/AGENTS.md` and prune obsolete/conflicting rules.
8. **Optimized Per-Figure Sizing & Diagram Spacing:**
   - Determine specific, optimal dimensions for each individual figure (large 16:9 UI screenshots at `width=0.95\textwidth`, compact modals at `width=0.75\textwidth`).
   - TikZ diagrams: Ensure comfortable 3–4mm margins for arrows and clear node spacing with appropriate scaling (`0.72` to `0.85`).
9. **Table 3-1 STT Numbering:**
   - Bảng 3-1 (`tab:actors_usecases`): Column "STT" must only contain `1` for the "Học giả (Scholar)" group and `2` for the "Quản trị viên (Admin)" group.
10. **Table Content Bullet Formatting:**
    - Outside of the STT column, table cells must never use numbered lists (1, 2, 3...); only dashes (`-`) or bullets are permitted.
11. **UseCase Sub-diagrams Paired With Specifications:**
    - UseCase decomposition diagrams (Hình 3-4, 3-5, 3-6, 3-7) must be placed directly adjacent to their respective specification tables (Bảng 3-2, 3-3, 3-4, 3-5) using `\FloatBarrier` to prevent separation across unrelated sections.

---

## 2. Goals, Non-Goals & Anti-Goals

### 2.1 Goals
- 100% adherence to `HIeu.pdf` (Phạm Quốc Bảo's thesis) across all 11 user-specified points.
- 0 overfull or overlapping table cells.
- Clean 1.5 line spacing throughout all frontmatter lists.
- Strict pairing of diagrams and specification tables.
- All 4 verification gates (Ruff, Pytest 400 tests, Vitest 240 tests, Production Build) pass cleanly with exit code 0.

### 2.2 Non-Goals
- Altering the academic core content or research algorithms of the thesis.
- Modifying project dependencies or API architectures.
- Changing thesis page margin geometry from standard A4.

### 2.3 Anti-Goals
- Paper-saving shortcuts (reducing line spacing below 1.45, font sizes below 13pt in body text/tables).
- Arbitrary inline bolding/italics.
- Unnecessary clearpage commands that produce orphan widow lines.

---

## 3. Approaches Considered & Trade-offs

### Approach A: Local Ad-hoc Edits
- Manually edit lines in individual `.tex` files without overarching table environment wrappers.
- Set arbitrary hardcoded width percentages on graphics.
- *Trade-off:* Fast, but high risk of recurring cell overlaps, broken float order, and test regressions.

### Approach B: Systematic Modular Optimization (Selected)
- **Frontmatter Standardization:** Cleanly refactor `bia_chinh.tex`, `phieu_giao_de_tai.tex`, `de_cuong_datn.tex`, and `loi_cam_on.tex` to match `HIeu.pdf` page-by-page.
- **Robust Table Typographic Rules:** Replace fragile manual widths with `tabularx{\textwidth}` using `m{...}` columns, `\tabcolsep = 6pt`, and `\arraystretch = 1.25`.
- **Per-Figure Dimension Tuning:** Customize scaling per figure type (UI screenshots, system architecture TikZ, sequence diagrams).
- **Float Barriers & Section Integrity:** Lock Use Case diagrams and tables together with `\FloatBarrier`.
- **Codification in `AGENTS.md`:** Document the 11 refined commandments and explicitly state that `HIeu.pdf` (Phạm Quốc Bảo) is the ultimate reference standard.

---

## 4. Detailed Implementation Specifications

### 4.1 Frontmatter Admin Forms Conformance
1. **`report-datn/frontmatter/bia_chinh.tex`:**
   - Remove `{\fontsize{13pt}{16pt}\selectfont \textbf{KHOÁ 67}\par}` from front face.
   - Retain rotated spine text: `\rotatebox{90}{\textbf{ĐÀM MẠNH DŨNG \hspace{2cm} HỆ THỐNG THÔNG TIN \hspace{2cm} KHOÁ 67}}`.
2. **`report-datn/frontmatter/phieu_giao_de_tai.tex`:**
   - Signature table:
     ```latex
     \begin{tabularx}{\textwidth}{@{}>{\centering\arraybackslash}X >{\centering\arraybackslash}X@{}}
       \textbf{Giảng viên hướng dẫn} & \textbf{Sinh viên thực hiện} \\[0.08cm]
       \textit{(Ký và ghi rõ họ tên)} & \textit{(Ký và ghi rõ họ tên)} \\[2.2cm]
     \end{tabularx}
     ```
   - No printed names underneath.
3. **`report-datn/frontmatter/de_cuong_datn.tex`:**
   - Refactor Student & Supervisor tables using `tabularx{\textwidth}` with explicit column formatting:
     ```latex
     \begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}m{0.8cm}|>{\centering\arraybackslash}m{2.3cm}|>{\raggedright\arraybackslash}m{3.0cm}|>{\centering\arraybackslash}m{2.3cm}|>{\centering\arraybackslash}m{2.2cm}|>{\raggedright\arraybackslash}X|}
     ```
   - For student and supervisor records, enable hyphenation/line-breaks with `\allowbreak` where necessary.
   - Section 8: End with `\noindent \textbf{6. Nơi thực hiện đồ án:} Trường Đại học Mỏ -- Địa chất`. Remove date line and signature table.
4. **`report-datn/frontmatter/loi_cam_on.tex`:**
   - Remove date, "Sinh viên thực hiện", and "Đàm Mạnh Dũng" at the bottom.
5. **`report-datn/frontmatter/danh_muc_hinh.tex` & `danh_muc_bang.tex`:**
   - Remove `\begin{singlespace}` and `\end{singlespace}`.
   - Ensure `\setstretch{1.45}` is active, allowing natural expansion across multiple pages matching `HIeu.pdf`.
   - Update `test_layout_spacing.py` to allow multi-page LOF/LOT and exempt frontmatter list ending pages from the 15-line threshold.

### 4.2 Table Rules & Terminology
1. **Padding & Vertical Centering:**
   - Standard body tables (3–4 columns): `\tabcolsep = 6pt`, `\renewcommand{\arraystretch}{1.20}` (or 1.25), and `m{...}` column types so contents never touch borders and vertical alignment is always centered.
   - High-density administrative tables (6 columns in `de_cuong_datn.tex`): `\tabcolsep = 3.5pt`, `\arraystretch = 1.20`, with column widths: TT (0.7cm), Mã SV/Cán bộ (2.3cm), Họ và tên (2.8cm), Lớp/Đơn vị (2.2cm), Điện thoại (2.1cm), E-mail (`X`), ensuring email addresses never touch borders and wrap cleanly without overflowing.
2. **Bảng 3-1 (`tab:actors_usecases`):**
   - STT column contains row 1 (`1`) and row 2 (`2`).
   - Use Case items formatted with bullet/dash:
     - `\multirow{8}{=}{\centering\textbf{1}} & \multirow{8}{=}{\centering\textbf{Học giả\\(Scholar)}} & -- Đăng ký / Đăng nhập và xác thực JWT \\ ...`
     - `\multirow{4}{=}{\centering\textbf{2}} & \multirow{4}{=}{\centering\textbf{Quản trị viên\\(Admin)}} & -- Quản trị người dùng và phân quyền \\ ...`
3. **Keyword Regularization:**
   - In all table header columns and data cells: Replace verbose descriptions with precise terms:
     - `Retrieval` (instead of `Truy xuất thông tin`),
     - `Chunking` (instead of `Chia đoạn / phân mảnh`),
     - `Dense / Sparse` (instead of `Véc-tơ dày đặc / ma trận thưa`),
     - `BYOK` (instead of `Tự cung cấp khóa API cá nhân`),
     - `IoU` (instead of `Tỷ lệ chồng lấn bounding box`).
4. **Table Content Itemization Rules (Tùy tính chất nội dung):**
   - Đối với các bước thực hiện tuần tự (Steps / Luồng sự kiện chính trong Bảng 3-2 đến 3-5): Sử dụng tiền tố bước rõ ràng `Bước 1:`, `Bước 2:`, `Bước 3:`... (hoặc `B1:`, `B2:`... theo mẫu `HIeu.pdf` trang 36).
   - Đối với các ý / luồng thay thế / ngoại lệ: Sử dụng dấu gạch đầu dòng (`--`).
   - Đối với các mục liệt kê thành phần / đặc tính: Sử dụng bullet (`\textbullet`).
   - Tuyệt đối cấm sử dụng số tự do (`1.`, `2.`, `3.`) trong phần nội dung bảng ngoài cột STT.

### 4.3 Per-Figure Sizing & Diagram Placement
1. **Figure Size Matrix:**
   - **Full UI Screenshots (Ch4, landscape 16:9):** `width=0.95\textwidth` (Figures 4-1, 4-2, 4-3, 4-4, 4-6).
   - **Modal / Focused UI (Ch4):** `width=0.75\textwidth` (Figure 4-5).
   - **Langfuse Trace & Metrics (Ch4):** `width=0.92\textwidth` (Figure 4-7, 4-8, 4-9).
   - **Architecture & Conceptual TikZ (Ch2, Ch3):**
     - Figure 3-2 (Hexagonal Architecture): `scale=0.68` (retaining outer margin within `\textwidth = 16.0cm` and passing `test_diagram_bounds.py` while adjusting internal node arrows with 3–4mm margins).
     - Figure 3-3 (Overview Use Case): `scale=0.72`.
     - Figure 3-12 (Domain Class Diagram): `scale=0.70`, orthogonal routing, arrow length padding 3–4mm.
2. **Use Case Sub-diagram & Specification Pairing:**
   - In `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`:
     - Figure 3-4 directly followed by Table 3-2 (`\FloatBarrier`).
     - Figure 3-5 directly followed by Table 3-3 (`\FloatBarrier`).
     - Figure 3-6 directly followed by Table 3-4 (`\FloatBarrier`).
     - Figure 3-7 directly followed by Table 3-5 (`\FloatBarrier`).

### 4.4 Documentation & AGENTS.md Overhaul
- Update `report-datn/AGENTS.md`:
  - Explicitly mandate `HIeu.pdf` (Phạm Quốc Bảo) as the gold standard.
  - Codify the 11 refined commandments.
  - Delete contradictory legacy rules (such as page squeezing or singlespace in lists).

---

## 5. Verification Plan

1. **Compilation Test:** Two-pass XeLaTeX compilation clean with 0 fatal errors.
2. **Automated Unit Tests:**
   - Update tests in `tests/report_datn/` and `tests/test_thesis_rules.py` to match the refined frontmatter and table formatting.
   - Verify `uv run pytest` (400 tests) passes 100%.
3. **Full 4-Gate Verification:** Run `bash scripts/dev/verify.sh` (Ruff, Pytest, Vitest, Build).
4. **Visual PDF Inspection:** Confirm Cover 1, Phiếu giao đề tài, Đề cương tables, Lời cảm ơn, Danh mục hình/bảng 1.5 spacing, Table 3-1, and Use Case diagram pairings.
