# KẾ HOẠCH THỰC THI: HOÀN THIỆN CHƯƠNG 4 VÀ ĐỒNG BỘ ĐẶC TẢ CA SỬ DỤNG CHƯƠNG 3
# (THESIS CHAPTER 4 COMPLETION & CHAPTER 3 SYNCHRONIZATION IMPLEMENTATION PLAN)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện 100% Chương 4 (Cài đặt và Kết quả thực nghiệm) với số liệu thực tế và sơ đồ bố cục TikZ chuẩn paper khoa học, đồng thời đồng bộ Bảng đặc tả ca sử dụng UC-01 vào Chương 3, bảo đảm biên dịch XeLaTeX đạt 0 Overfull/Underfull \hbox và vượt qua 4 Cổng xác minh.

**Architecture:** Sử dụng kiến trúc tài liệu phân rã vi mô (*Micro-Modular LaTeX Structure*). Chương 3 được bổ sung đặc tả UC-01 theo chuẩn BA với cơ chế lọc 2 lớp (Lớp 1 Backend Jaccard Overlap $\ge 0.2$, Lớp 2 Frontend nút gạt bình duyệt). Chương 4 được xây dựng hoàn chỉnh gồm 4 tiểu mục: 4.1 Môi trường đám mây & Monorepo, 4.2 Giao diện 4 phân hệ với sơ đồ vector TikZ, 4.3 Kết quả 4 Cổng kiểm định thực tế (84 backend / 24 frontend tests), 4.4 Số liệu định lượng và vết thực thi Langfuse Cloud.

**Tech Stack:** XeLaTeX, TikZ PGF, BibLaTeX, Python 3.12, Pytest, FastAPI, React 19, Vitest, Vite, Langfuse Cloud.

**Spec:** [`docs/superpowers/specs/2026-10-26-thesis-chapter-4-and-sync-ch3-design.md`](../specs/2026-10-26-thesis-chapter-4-and-sync-ch3-design.md)

---

## Global Constraints

* **AGENTS.md Rule 5:** Toàn bộ liên kết Markdown phải dùng đường dẫn tương đối (`./...`, `../...`), tuyệt đối cấm URL tuyệt đối máy chủ (`file://`).
* **AGENTS.md Rule 6:** Chủ nghĩa tối giản triệt để (Radical Minimalism): không văn mẫu sáo rỗng, không mã màu `#hex` thô hoặc danh xưng rườm rà.
* **AGENTS.md Rule 7 (Academic Purity & Thesis Invariants):**
  - Không lộ mã LaTeX thô trong văn bản xuất bản (`[1]`, `[2]` thay vì `\cite{...}`).
  - Khống chế danh mục tham khảo: $N_{\text{refs}} \le 20$, không có trích dẫn mồ côi.
  - Bắt buộc kiểm soát độ rộng lề: **0 Overfull \hbox** và **0 Underfull \hbox** trên toàn bộ các chương.
* **AGENTS.md Rule 8 (Human-Centric Paper Architecture):** Sơ đồ TikZ phải đóng vai trò là một mô hình tư duy học thuật trực quan, thể hiện rõ dòng chảy tri thức và khối chức năng cấp cao.
* **The 4 Verification Gates:** Mọi task khi hoàn thành phải bảo đảm 4 Cổng đạt 100% exit code 0 (`ruff`, `pytest`, `npm test`, `npm run build`).

---

## Review Focus

1. **Lỗi tràn lề bảng biểu trong LaTeX (`Overfull \hbox`):** Các bảng biểu mới (`tab:uc_01_spec`, `tab:gate_results`, `tab:thuc_nghiem_dinh_luong`) phải sử dụng cột `p{...}` kết hợp `\raggedright\arraybackslash` để không bao giờ bị vượt quá chiều rộng trang in.
2. **Ngắt dòng các chuỗi hash và Trace ID:** Các chuỗi dài như mã Langfuse Trace ID (`f8d087c559790eafd0812e6293d23a34`) phải được bao trong `\texttt{\small ...}` và ngắt nhịp an toàn để tránh đẩy lề.
3. **Tính nhất quán giữa Bảng kiểm thử và Mã nguồn:** Số lượng bài kiểm thử tại Bảng 4.1 phải khớp chính xác 100% với đầu ra thực tế của `pytest` (84 bài) và `vitest` (24 bài).
4. **Trần tài liệu tham khảo:** Tuyệt đối không bổ sung thêm tài liệu tham khảo vượt quá giới hạn 20 mục ($N_{\text{refs}} \le 20$).
5. **Đồng bộ nhãn tham chiếu chéo (`\label` và `\ref`):** Tất cả các bảng biểu và hình vẽ mới phải có `\label` duy nhất và được dẫn chiếu tường minh trong lời văn.

---

## Các Nhiệm Vụ Triển Khai (Task Breakdown)

### Task 1: Đồng bộ Bảng đặc tả ca sử dụng UC-01 vào Chương 3 (`report-datn/chapters/ch3/3_2_usecase.tex`)

**Files:**
- Modify: `report-datn/chapters/ch3/3_2_usecase.tex`
- Test: `tests/test_thesis_rules.py`, `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Đặc tả `UC-DISC-01` từ [`docs/PRD/02-discovery-and-documents-crud.md`](../../PRD/02-discovery-and-documents-crud.md) và thuật toán Precision Engine từ [`docs/specs/02-discovery-and-documents-spec.md`](../../specs/02-discovery-and-documents-spec.md).
- Produces: Bảng `tab:uc_01_spec` (Đặc tả chi tiết ca sử dụng UC-01: Khám phá bài báo học thuật theo chủ đề có kiểm soát độ tin cậy và phân tầng bình duyệt) đặt trước `tab:uc_03_spec`.

- [ ] **Step 1: Viết test kiểm tra sự hiện diện của UC-01 trong Chương 3**
  Bổ sung assertion vào `tests/test_thesis_rules.py` kiểm tra file `report-datn/chapters/ch3/3_2_usecase.tex` có chứa nhãn `tab:uc_01_spec` và thuật toán Jaccard.
- [ ] **Step 2: Chạy test để xác nhận test đỏ (FAIL)**
  Run: `uv run pytest tests/test_thesis_rules.py -k "test_ch3_uc01" -v`
  Expected: FAIL (chưa có nội dung UC-01).
- [ ] **Step 3: Soạn thảo Bảng đặc tả `tab:uc_01_spec` trong `3_2_usecase.tex`**
  Thêm đoạn dẫn nhập và Bảng `tab:uc_01_spec` với đầy đủ thuộc tính: Mã use case, Tác nhân, Mục đích, Tiền/Hậu điều kiện, Luồng sự kiện chính (6 bước: Query $\rightarrow$ Skeleton tức thì $\rightarrow$ Truy vấn trường $\rightarrow$ Lọc Jaccard $\ge 0.2$ $\rightarrow$ Phân loại bình duyệt $\rightarrow$ Thẻ chống tràn) và Luồng ngoại lệ.
- [ ] **Step 4: Chạy test để xác nhận test xanh (PASS)**
  Run: `uv run pytest tests/test_thesis_rules.py -v`
  Expected: PASS 85/85 tests.
- [ ] **Step 5: Commit task**
  ```bash
  git add report-datn/chapters/ch3/3_2_usecase.tex tests/test_thesis_rules.py
  git commit -m "feat(thesis): add UC-01 two-tier discovery usecase specification to chapter 3"
  ```

---

### Task 2: Hoàn thiện Mục 4.1 Môi trường cài đặt và Kiến trúc Monorepo (`report-datn/chapters/ch4/4_1_moi_truong.tex`)

**Files:**
- Modify: `report-datn/chapters/ch4/4_1_moi_truong.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Cấu hình hạ tầng thực tế từ `docker-compose.yml`, `pyproject.toml`, `apps/web/package.json`.
- Produces: Bản thảo học thuật Mục 4.1 hoàn chỉnh gồm 2 tiểu mục: 4.1.1 Cấu hình hạ tầng đám mây & phần mềm nền tảng; 4.1.2 Phân tách kiến trúc Monorepo 3 phân vùng (`packages/core`, `apps/api`, `apps/web`) và rào chắn kiểm thử ranh giới AST tự động.

- [ ] **Step 1: Viết test kiểm tra nội dung và cấu trúc Mục 4.1**
  Kiểm tra Mục 4.1 có đầy đủ các thông số hạ tầng (Azure Ubuntu 24.04 LTS, 4 vCPU, 16GB RAM, PostgreSQL 16.2 pgvector, Python 3.12 uv, React 19, E2B MicroVM, Langfuse Cloud).
- [ ] **Step 2: Chạy test xác nhận đỏ**
- [ ] **Step 3: Soạn thảo nội dung học thuật chi tiết cho `4_1_moi_truong.tex`**
  Viết lại toàn diện Mục 4.1 với lập luận sắc sảo, cấu trúc bảng phân tách Monorepo và rào chắn AST `test_architecture_boundary.py`.
- [ ] **Step 4: Chạy test xác nhận xanh**
  Run: `uv run pytest tests/test_thesis_structure_and_compile.py -v`
- [ ] **Step 5: Commit task**
  ```bash
  git add report-datn/chapters/ch4/4_1_moi_truong.tex tests/test_thesis_structure_and_compile.py
  git commit -m "feat(thesis): expand section 4.1 environment and monorepo architecture"
  ```

---

### Task 3: Thiết kế và Hoàn thiện Mục 4.2 Giao diện 4 Phân hệ với Sơ đồ TikZ (`report-datn/chapters/ch4/4_2_giao_dien.tex`)

**Files:**
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Đặc tả UI từ PRD-02, Spec-02, `ScholarlyResultCard.tsx`, `UnifiedHeroWorkspace.tsx`.
- Produces:
  * Sơ đồ vector TikZ `fig:ui_layout_architecture` mô hình hóa không gian tương tác người-máy của 4 phân hệ chính.
  * 4 tiểu mục học thuật chi tiết: 4.2.1 Phân hệ Khám phá tài liệu; 4.2.2 Phân hệ Đọc sâu & Bounding Box; 4.2.3 Phân hệ Quản lý tài liệu & Hồ sơ học giả BYOK; 4.2.4 Phân hệ Soạn thảo & Tự sửa lỗi \LaTeX.

- [ ] **Step 1: Viết test kiểm tra 4 phân hệ và sơ đồ TikZ trong `4_2_giao_dien.tex`**
  Assertion kiểm tra sự hiện diện của `fig:ui_layout_architecture`, 4 tiểu mục `subsec:ui_discovery`, `subsec:ui_deep_reading`, `subsec:ui_profile`, `subsec:ui_writing`.
- [ ] **Step 2: Chạy test xác nhận đỏ**
- [ ] **Step 3: Dựng sơ đồ TikZ `fig:ui_layout_architecture` và viết nội dung 4 phân hệ**
  Soạn thảo sơ đồ TikZ 4 khối không gian tương tác cân đối, thanh lịch. Viết sâu về: thẻ chống tràn, skeleton 3 thẻ, nút gạt Đã bình duyệt, BBox vàng 1s, Két sắt BYOK AES-GCM, chu trình ReAct trong E2B MicroVM.
- [ ] **Step 4: Chạy test xác nhận xanh**
- [ ] **Step 5: Commit task**
  ```bash
  git add report-datn/chapters/ch4/4_2_giao_dien.tex tests/test_thesis_structure_and_compile.py
  git commit -m "feat(thesis): implement 4-subsystem ui layout with tikz architecture diagram"
  ```

---

### Task 4: Cập nhật Mục 4.3 Kết quả kiểm thử tự động 4 Cổng xác minh (`report-datn/chapters/ch4/4_3_kiem_thu.tex`)

**Files:**
- Modify: `report-datn/chapters/ch4/4_3_kiem_thu.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Số liệu kiểm thử thực tế từ 4 Cổng xác minh: 152 tệp Python, 84 bài kiểm thử Pytest, 24 bài kiểm thử Vitest, Vite build 1.70s.
- Produces: Bảng `tab:gate_results` cập nhật số liệu chính xác 100%, phân tích rào chắn kiến trúc Lục giác AST và kiểm tra triệt tiêu liên kết `file://`.

- [ ] **Step 1: Viết test kiểm tra số liệu kiểm thử thực tế trong `4_3_kiem_thu.tex`**
  Assertion kiểm tra số lượng 84 bài backend, 24 bài frontend, 152 tệp nguồn.
- [ ] **Step 2: Chạy test xác nhận đỏ**
- [ ] **Step 3: Cập nhật Bảng `tab:gate_results` và lời văn biện luận**
  Cập nhật bảng và trình bày phương pháp luận kiểm thử cơ học (Mechanical Enforcement) ngăn ngừa suy thoái chất lượng phần mềm.
- [ ] **Step 4: Chạy test xác nhận xanh**
- [ ] **Step 5: Commit task**
  ```bash
  git add report-datn/chapters/ch4/4_3_kiem_thu.tex tests/test_thesis_structure_and_compile.py
  git commit -m "feat(thesis): update section 4.3 with real 4-gate verification test metrics"
  ```

---

### Task 5: Hoàn thiện Mục 4.4 Số liệu thực nghiệm định lượng và Đối chiếu Langfuse Cloud (`report-datn/chapters/ch4/4_4_so_lieu.tex`)

**Files:**
- Modify: `report-datn/chapters/ch4/4_4_so_lieu.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Số liệu đo lường định lượng và 3 Trace ID từ Langfuse Cloud (`f8d087c559790eafd0812e6293d23a34`, `9423ed4e264360d619c4e0494900f4f5`, `c308e29caa04f439ca0ff1b851412f8b`).
- Produces: Bảng `tab:thuc_nghiem_dinh_luong` và các đoạn lập luận kim tự tháp Minto Pyramid đối chiếu các chỉ số kỹ thuật với mục tiêu đồ án.

- [ ] **Step 1: Viết test kiểm tra số liệu định lượng và Langfuse Trace ID trong `4_4_so_lieu.tex`**
  Assertion kiểm tra bảng `tab:thuc_nghiem_dinh_luong`, các chỉ số 1.66ms, 1.15s, 0.88 IoU, 92% LaTeX, 100% Jaccard và 3 Trace IDs.
- [ ] **Step 2: Chạy test xác nhận đỏ**
- [ ] **Step 3: Soạn thảo Bảng 4.2 và phân tích thực nghiệm trong `4_4_so_lieu.tex`**
  Xây dựng bảng tổng hợp đo lường định lượng, viết phân tích sâu về hiệu năng và chi phí token.
- [ ] **Step 4: Chạy test xác nhận xanh**
- [ ] **Step 5: Commit task**
  ```bash
  git add report-datn/chapters/ch4/4_4_so_lieu.tex tests/test_thesis_structure_and_compile.py
  git commit -m "feat(thesis): expand section 4.4 quantitative metrics and langfuse trace logs"
  ```

---

### Task 6: Biên dịch toàn trình XeLaTeX, kiểm tra 0 Overfull/Underfull \hbox và xác nhận 4 Cổng kiểm định

**Files:**
- Verify: `report-datn/main.pdf`, `report-datn/main.log`
- Test: 4 Verification Gates

**Interfaces:**
- Consumes: Toàn bộ các chương từ Chương 1 đến Chương 4 và Phần Kết luận.
- Produces: Tệp `report-datn/main.pdf` hoàn hảo, báo cáo log không có bất kỳ cảnh báo Overfull hay Underfull \hbox nào trên các chương nội dung chính, 100% 4 Gates exit code 0.

- [ ] **Step 1: Biên dịch XeLaTeX toàn trình và kiểm tra log cảnh báo**
  Run: `cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex`
  Verify: Không có lỗi cú pháp, quét tìm Overfull \hbox trong `main.log`.
- [ ] **Step 2: Chạy kiểm thử tự động toàn bộ quy chuẩn đồ án**
  Run: `uv run pytest tests/test_thesis_rules.py tests/test_thesis_structure_and_compile.py -v`
  Verify: Pass 100%, $N_{\text{refs}} \le 20$.
- [ ] **Step 3: Chạy toàn bộ 4 Cổng xác minh bắt buộc**
  - Cổng 1: `uv run ruff check . && uv run ruff format --check .`
  - Cổng 2: `uv run pytest`
  - Cổng 3: `npm --prefix apps/web run test`
  - Cổng 4: `npm --prefix apps/web run build`
- [ ] **Step 4: Commit và hoàn tất**
  ```bash
  git add report-datn/main.pdf report-datn/main.log
  git commit -m "chore(thesis): compile final thesis pdf with 0 overfull hbox and verify 4 gates"
  ```
