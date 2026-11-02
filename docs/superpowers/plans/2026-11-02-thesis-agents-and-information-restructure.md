# Tái Cấu Trúc Hệ Thống AGENTS.md Và INFORMATION.md Báo Cáo ĐATN Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển đổi `report-datn/RULES.md` thành `report-datn/INFORMATION.md` (chứa hồ sơ đề tài và mục lục phân loại đặc tả coding `docs/`), hoàn thiện `report-datn/AGENTS.md` thành cẩm nang nguyên tắc chuẩn mực theo 4 tệp hướng dẫn trong `report-datn/guide/` (loại bỏ duplicate), và đồng bộ bộ kiểm thử tự động để vượt qua 100% 4 Cổng xác minh.

**Architecture:** Áp dụng nguyên tắc Một nguồn chân lý duy nhất (SSOT) và Phân tách trách nhiệm (Separation of Concerns): `AGENTS.md` chịu trách nhiệm độc quyền về quy chế, thể thức XeLaTeX, phong cách hành văn và cẩm nang tác tử; `INFORMATION.md` chịu trách nhiệm độc quyền về hồ sơ định danh sinh viên/GVHD, mốc đề tài, danh mục specs `docs/`, số liệu thực nghiệm khóa cứng và 20 TLTK; bộ test `tests/test_thesis_rules*.py` phân định kiểm tra chính xác từng tệp.

**Tech Stack:** Markdown, Python (pytest, ruff), XeLaTeX (`report-datn`), Node.js/Next.js/React (`apps/web`).

**Spec:** [`docs/superpowers/specs/2026-11-02-thesis-agents-and-information-restructure-design.md`](../specs/2026-11-02-thesis-agents-and-information-restructure-design.md)

## Global Constraints

- Không chứa URL tuyệt đối `file://` trong bất kỳ tệp Markdown nào (tuân thủ Rule 5 root `AGENTS.md`).
- `INFORMATION.md` phải chứa Mục lục phân loại có cấu trúc dẫn hướng sang các file specs trong `docs/` (`docs/specs/`, `docs/PRD/`, `docs/DATABASE_ERD.md`, `docs/benchmarks/`).
- `AGENTS.md` và `INFORMATION.md` tuyệt đối không duplicate nội dung của nhau (Zero Duplication).
- Không sửa đổi mã nguồn XeLaTeX các chương hay cấu trúc trang của `report-datn/main.tex` (Non-goal).
- Mọi commit đều phải kích hoạt đồng bộ VPS tự động qua `bash scripts/deploy_to_vps.sh --fast` (Rule 7 root `AGENTS.md`).
- Vượt qua 100% 4 Cổng kiểm định chất lượng: ruff check/format, pytest, npm test, npm build.

## Review Focus

1. **Gãy liên kết tệp cũ (`RULES.md` -> `INFORMATION.md`):** Các script kiểm định hoặc test tự động vẫn tìm kiếm `report-datn/RULES.md` dẫn đến lỗi FileNotFoundError. Cần kiểm chứng mọi đường dẫn được cập nhật đồng bộ.
2. **Trùng lặp dữ liệu (Duplication Leakage):** Thông tin sinh viên, GVHD hoặc bảng CSDL vô tình vẫn còn sót lại trong `AGENTS.md`, vi phạm chỉ thị Zero Duplication.
3. **Mục lục docs không đầy đủ:** Mục lục đặc tả kỹ thuật trong `INFORMATION.md` bỏ sót các spec quan trọng (như CSDL 20 bảng, Langfuse tracing, hay benchmark results).
4. **Sai lệch thể thức so với `./guide`:** Các thông số thể thức (13pt, dãn dòng 1.5, lề 2.5/2.5/3.5/2.5, số trang góc dưới phải, phân cấp mục tối đa 4 cấp) bị diễn đạt mâu thuẫn giữa cẩm nang và test suite.
5. **Test suite adversarial trượt:** Các assertions kiểm tra từ khóa định dạng và quy chế khoa bị xung đột do phân tách tệp.

---

### Task 1: Cập nhật và Tách bạch Bộ Kiểm Thử `test_thesis_rules*.py` (TDD Red)

**Files:**
- Modify: `tests/test_thesis_rules.py`
- Modify: `tests/test_thesis_rules_adversarial.py`

**Interfaces:**
- Consumes: Yêu cầu phân định thẩm quyền trong Spec (Mục 4.3).
- Produces: Bộ test định nghĩa chính xác hành vi mong đợi của `INFORMATION.md` và `AGENTS.md`.

- [ ] **Step 1: Cập nhật `tests/test_thesis_rules.py` để trỏ vào `INFORMATION.md` và phân định thẩm quyền**

Đổi `rules_path = Path("report-datn/RULES.md")` thành `info_path = Path("report-datn/INFORMATION.md")`.  
Cập nhật các assertion:
- Kiểm tra `report-datn/INFORMATION.md` tồn tại.
- Kiểm tra các phần cốt lõi của `INFORMATION.md`: Hồ sơ sinh viên, GVHD, Đề tài, Kế hoạch 10 tuần, Mục lục đặc tả kỹ thuật `docs/`, Bảng tham số định lượng hạt nhân, Danh mục 20 tài liệu tham khảo.
- Kiểm tra liên kết hai chiều giữa `AGENTS.md` và `INFORMATION.md`.
- Kiểm tra `AGENTS.md` chứa Bảng ma trận chiến lược chắt lọc nội dung từ docs (Keep/Omit).

- [ ] **Step 2: Cập nhật `tests/test_thesis_rules_adversarial.py` để tách bạch thể thức và dữ liệu đề tài**

- Trong `test_adversarial_actor_boxes_no_rectangular_exceptions`: Assert "stick figure" trên `AGENTS.md` (nơi quy định quy chuẩn vẽ sơ đồ Use Case).
- Trong `test_adversarial_faculty_regulations_accuracy`: Assert 4 điều kiện đình chỉ và 3 câu hỏi học thuật cốt lõi trên `AGENTS.md`; assert định dạng nộp thư mục `MãSinhViên_HọTên_Khóa` và mốc Tuần 6 trên `INFORMATION.md`.
- Trong `test_adversarial_rules_agents_no_conflicts`: Assert các thông số hình học (13pt, Times New Roman, 1.5, 2.5, 3.5, 15{,}0, 50, 65) trên `AGENTS.md`; assert các số liệu thực nghiệm khóa cứng (580, 13.02, 1.66, 0{,}85, 20) trên `INFORMATION.md`.
- Trong `test_adversarial_table_borders_and_tabularx`: Assert `tabularx` và cấm `booktabs` trên `AGENTS.md`.

- [ ] **Step 3: Chạy test để xác nhận trạng thái Red (thất bại có kiểm soát)**

Run: `uv run pytest tests/test_thesis_rules.py tests/test_thesis_rules_adversarial.py`  
Expected: FAIL vì `report-datn/INFORMATION.md` chưa được tạo và `RULES.md` chưa chuyển đổi.

- [ ] **Step 4: Commit thay đổi của bộ kiểm thử**

```bash
git add tests/test_thesis_rules.py tests/test_thesis_rules_adversarial.py
git commit -m "test: align thesis rules test suite with INFORMATION.md and AGENTS.md separation"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Tạo Tệp `report-datn/INFORMATION.md` Và Xóa Bỏ `report-datn/RULES.md` (TDD Green 1)

**Files:**
- Create: `report-datn/INFORMATION.md`
- Delete: `report-datn/RULES.md`

**Interfaces:**
- Consumes: Toàn bộ thông tin định danh sinh viên, cán bộ hướng dẫn, đề tài, số liệu thực nghiệm, kế hoạch 10 tuần, 20 TLTK từ `RULES.md` cũ và cấu trúc thư mục `docs/`.
- Produces: `report-datn/INFORMATION.md` đóng vai trò Hồ sơ Đề tài và Bản đồ Mục lục Spec `docs/`.

- [ ] **Step 1: Khởi tạo `report-datn/INFORMATION.md` chuẩn 6 phần**

Biên soạn đầy đủ nội dung:
1. **Phần 1: Hồ sơ định danh sinh viên và cán bộ hướng dẫn:**
   - SV: Đàm Mạnh Dũng, MSSV `2221050359`, Lớp `DCCTCT67_09B`, Ngành CNTT (`7480201`), Chuyên ngành HTTT & Tri thức, Khoa CNTT — HUMG, SĐT `0978461865`, Email `dammanhdungvn@gmail.com`.
   - GVHD: ThS. Vũ Lan Phương, Mã CB `0802-09`, Bộ môn CNTT, Khoa CNTT — HUMG, SĐT `0984223379`, Email `vulanphuong@humg.edu.vn`.
   - Cơ quan chủ quản: Bộ GD&ĐT; Cơ sở đào tạo: Trường Đại học Mỏ - Địa chất (Số 18 Phố Viên, Đức Thắng, Bắc Từ Liêm, Hà Nội).
2. **Phần 2: Đặc tả đề tài tốt nghiệp, tính cấp thiết và mục tiêu:**
   - Tên tiếng Việt và tiếng Anh chính thức.
   - Bối cảnh VinUni, vấn nạn ảo giác, Mô hình 4 Không gian khép kín, 4 đóng góp kỹ thuật cốt lõi.
3. **Phần 3: Kế hoạch thực hiện 10 tuần chi tiết (Đề cương ĐATN):**
   - 10 tuần (24/08/2026 đến 02/11/2026), mốc Tuần 6 báo cáo tiến độ với Bộ môn và GVHD; định dạng thư mục nộp bản mềm `MãSinhViên_HọTên_Khóa`.
4. **Phần 4: Mục lục và Bản đồ tra cứu đặc tả kỹ thuật coding (`./docs`):**
   - Bảng ánh xạ có cấu trúc dẫn hướng sang toàn bộ tài liệu kỹ thuật:
     - `docs/specs/00-foundation-architecture-and-db.md` & `docs/DATABASE_ERD.md`: Kiến trúc Lục giác và CSDL 20 bảng chuẩn.
     - `docs/specs/01-auth-and-user-spec.md` & `docs/PRD/01-auth-and-user.md`: Xác thực JWT, két BYOK AES-256-GCM.
     - `docs/specs/02-discovery-and-documents-spec.md` & `docs/PRD/02-discovery-and-documents-crud.md`: Tra cứu arXiv, Semantic Scholar, CrossRef, CAS SHA-256 deduplication.
     - `docs/specs/03-sessions-and-deep-reading-spec.md` & `docs/PRD/03-sessions-and-deep-reading-crud.md`: Hybrid RAG, CRAG gating, BBox IoU >= 0.85 grounding.
     - `docs/specs/04-context-table-and-roadmap-spec.md` & `docs/PRD/04-context-table-and-roadmap.md`: Bảng ngữ cảnh nghiên cứu & tiến trình học thuật.
     - `docs/specs/05-favorite-library-and-graphrag-spec.md` & `docs/PRD/05-favorite-library-and-graphrag.md`: GraphRAG 4 thực thể trên PostgreSQL ACID kết hợp Louvain clustering.
     - `docs/specs/06-agentic-overleaf-writing-spec.md` & `docs/PRD/06-agentic-overleaf-writing.md`: Tác nhân ReAct và máy ảo E2B MicroVM tự sửa lỗi cú pháp LaTeX.
     - `docs/specs/07-monitoring-and-langfuse-spec.md` & `docs/PRD/07-monitoring-and-langfuse.md`: Giám sát Trace ID, Token usage, chi phí.
     - `docs/specs/08-universal-agent-harness-spec.md`: Cấu trúc tác tử tự hành Universal Agent Harness.
     - `docs/specs/09-deployment-cicd-and-evaluation-spec.md` & `docs/PRD/08-deployment-and-system-evaluation.md`: Đánh giá hệ thống và CI/CD.
     - `docs/benchmarks/thesis_benchmark_results.json`: Tập số liệu thực nghiệm gốc đã thẩm định.
     - `docs/THESIS_DEFENSE_GUIDE.md` & `docs/THESIS_OUTLINE_MAPPING.md`: Hướng dẫn bảo vệ và ánh xạ đề cương.
5. **Phần 5: Bảng tham số định lượng và benchmarks khóa cứng:**
   - 20 bảng CSDL thực tế (loại bỏ 4 bảng ảo), 580 unit/integration tests pass, thời gian chạy 13.02s, độ trễ CSDL 1.66ms, TTFT < 1.5s, IoU $\ge 0{,}85$.
6. **Phần 6: Danh mục 20 tài liệu tham khảo chính thức của đề tài:**
   - Phân nhóm 2 tài liệu tiếng Việt (Quy định & Hướng dẫn HUMG 2022) và 18 tài liệu quốc tế.
- Viện dẫn sang `report-datn/AGENTS.md` làm cẩm nang chuẩn mực thể thức và quy tắc tác tử.

- [ ] **Step 2: Xóa bỏ tệp `report-datn/RULES.md`**

Xóa tệp cũ bằng lệnh `git rm report-datn/RULES.md` để loại bỏ trạng thái trùng lặp tệp.

- [ ] **Step 3: Kiểm tra tệp `INFORMATION.md` và xác nhận không có link tuyệt đối `file://`**

Run: `grep "file://" report-datn/INFORMATION.md`  
Expected: Không có kết quả nào xuất hiện.

- [ ] **Step 4: Commit tệp `INFORMATION.md` mới và xóa `RULES.md`**

```bash
git add report-datn/INFORMATION.md
git rm -f report-datn/RULES.md
git commit -m "docs(datn): create INFORMATION.md with docs catalog and remove obsolete RULES.md"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Rà Soát, Chuẩn Hóa `report-datn/AGENTS.md` Theo `./guide` Và Tích Hợp Ma Trận Keep/Omit (TDD Green 2)

**Files:**
- Modify: `report-datn/AGENTS.md`

**Interfaces:**
- Consumes: 4 tài liệu trong `report-datn/guide/`, Ma trận Keep/Omit từ `RULES.md` cũ, liên kết `report-datn/INFORMATION.md`.
- Produces: `report-datn/AGENTS.md` đạt chuẩn 100% hướng dẫn của Khoa, sạch duplicate, đồng bộ toàn diện.

- [ ] **Step 1: Thay thế toàn bộ tham chiếu `RULES.md` thành `INFORMATION.md` trong `AGENTS.md`**

Rà soát và thay thế mọi vị trí xuất hiện của `report-datn/RULES.md` (bao gồm: Header thẩm quyền dòng 13, Tôn chỉ học thuật dòng 23, Tháp thẩm quyền dòng 415, các hàng rào AP-01, AP-04, AP-05, AP-06, vai trò persona `thesis-architect`, `thesis-reviewer`, và checklist pre-commit).

- [ ] **Step 2: Cập nhật các quy định từ 4 tệp trong `./guide` vào `AGENTS.md`**

1. **Bản nhận xét của GVHD (`Mẫu_HD_DATN.md`):** Khẳng định rõ đây là văn bản độc lập lưu trong hồ sơ tốt nghiệp đại học của Nhà trường, có chữ ký xác nhận của GVHD (Đề nghị Được bảo vệ / Không được bảo vệ), không đóng gộp vào thân bài luận văn.
2. **Quy định lưu trữ bản cứng và bản mềm (`Huong dan-Quy dinh-DATN.md` & `Huong-dan-viet-DATN.md`):**
   - 03 quyển bìa mềm nộp trước bảo vệ (02 quyển nộp Bộ môn cho HĐ và GVPB, 01 quyển cho GVHD).
   - 01 quyển bìa cứng in chữ nhũ nộp cho Bộ môn lưu trữ trong vòng 10 ngày sau bảo vệ.
   - Bản mềm: nộp thư mục định dạng `MãSinhViên_HọTên_Khóa` chứa báo cáo, mã nguồn, bản vẽ.
3. **Quy chế kỷ luật & 3 câu hỏi lớn:**
   - 4 điều kiện đình chỉ bảo vệ tốt nghiệp (nợ trường, không gặp/báo cáo GVHD hàng tuần, không nộp báo cáo đúng hạn, GVHD đánh giá không đạt).
   - 3 câu hỏi lớn: "Làm gì? Cho đối tượng nào?", "Làm như thế nào?", "Kết quả ra sao?".
4. **Trật tự bố cục và Thể thức Typography:**
   - Trật tự phân đoạn: Bìa ngoài (chữ nhũ) $\rightarrow$ Bìa trong $\rightarrow$ Phiếu giao đề tài $\rightarrow$ Đề cương ĐATN $\rightarrow$ Mục lục $\rightarrow$ Danh mục chữ viết tắt $\rightarrow$ Danh mục bảng biểu (LoT) $\rightarrow$ Danh mục hình vẽ (LoF) $\rightarrow$ Lời cảm ơn (trang 1 Ả Rập XeLaTeX) $\rightarrow$ Lời mở đầu $\rightarrow$ Chương 1 (Mô tả bài toán: Làm gì? Cho đối tượng nào?) $\rightarrow$ Chương 2 (Cơ sở lý thuyết & Luận giải Tại sao chọn công nghệ) $\rightarrow$ Chương 3 (Quy trình 5 bước kỹ nghệ: Phân tích, Thiết kế, Cài đặt, Kiểm thử, Hiệu chỉnh) $\rightarrow$ Chương 4 (Kết quả thực nghiệm) $\rightarrow$ Kết luận $\rightarrow$ Danh mục TLTK $\rightarrow$ Phụ lục.
   - Cỡ chữ 13 Times New Roman, dãn dòng 1.5 lines, lề trên 2.5cm, dưới 2.5cm, trái 3.5cm, phải 2.5cm, chiều rộng khả dụng đúng 15.0cm. Số trang ở dưới, phía bên phải mỗi trang giấy, in đứng thường (không in nghiêng).
   - Phân cấp đề mục: Tối đa 4 cấp (4.1.2.1), cấm tiểu mục đơn lẻ (ít nhất 2 tiểu mục con).
   - Bảng biểu/hình vẽ: Gắn liền với số chương, tiêu đề bảng ở trên, tiêu đề hình ở dưới, bắt buộc `tabularx` với cột `X`, cấm `booktabs` (`\toprule, \midrule, \bottomrule`), cấm dẫn chiếu tương đối.
   - Tài liệu tham khảo: Tiếng Việt trước (xếp ABC theo tên), Tiếng Anh sau (xếp ABC theo họ), lùi đầu dòng 1cm từ dòng thứ hai, trần $N_{\text{refs}} \le 20$.
   - Sơ đồ Use Case: Vẽ tác nhân (Actor) bằng hình người UML (Stick Figure), tuyệt đối không dùng hình hộp chữ nhật (Box).

- [ ] **Step 3: Nạp Bảng ma trận chiến lược chắt lọc nội dung từ Docs (Keep & Elevate vs. Omit)**

Chèn Bảng ma trận chắt lọc nội dung từng chương (từ `RULES.md` cũ) vào Mục 3.2 của `AGENTS.md` (dưới mục phòng ngừa Anti-Pattern AP-01).

- [ ] **Step 4: Kiểm tra không chứa thông tin cá nhân trùng lặp và không chứa `file://`**

Xóa bỏ bất kỳ dòng nào nhắc đến họ tên cụ thể của sinh viên hay GVHD trong `AGENTS.md` (tham chiếu sang `INFORMATION.md`).  
Run: `grep "file://" report-datn/AGENTS.md`  
Expected: Không có kết quả nào.

- [ ] **Step 5: Chạy bộ kiểm thử để xác nhận trạng thái Green (vượt qua 100%)**

Run: `uv run pytest tests/test_thesis_rules.py tests/test_thesis_rules_adversarial.py`  
Expected: Toàn bộ 19 test đều PASS (100% exit code 0).

- [ ] **Step 6: Commit thay đổi `AGENTS.md`**

```bash
git add report-datn/AGENTS.md
git commit -m "docs(datn): update AGENTS.md with faculty guidelines, keep-omit matrix and link to INFORMATION.md"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Quét Sạch Liên Kết Cũ Và Thực Thi 4 Cổng Kiểm Định Chất Lượng

**Files:**
- Modify: Bất kỳ tệp tài liệu nào còn chứa tham chiếu đến `report-datn/RULES.md` (nếu có trong `docs/` hoặc `.agents/`).

**Interfaces:**
- Consumes: Toàn bộ repo sau Task 1-3.
- Produces: 100% pass 4 Cổng kiểm định chất lượng bắt buộc.

- [ ] **Step 1: Quét tìm các liên kết cũ `RULES.md` trong toàn bộ repo**

Run: `grep -rn "report-datn/RULES.md" . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv`  
Nếu còn tệp nào trỏ đến `report-datn/RULES.md`, cập nhật sang `report-datn/INFORMATION.md`.

- [ ] **Step 2: Thực thi Cổng 1 — Linter & Formatter Python**

Run: `uv run ruff check . && uv run ruff format --check .`  
Expected: Exit code 0 (All checks passed).

- [ ] **Step 3: Thực thi Cổng 2 — Toàn bộ Backend & Boundary Tests**

Run: `uv run pytest`  
Expected: Toàn bộ test suite (>580 tests) đều PASS với exit code 0.

- [ ] **Step 4: Thực thi Cổng 3 — Frontend Unit Tests**

Run: `npm --prefix apps/web run test`  
Expected: Exit code 0.

- [ ] **Step 5: Thực thi Cổng 4 — Production Build Giao Diện**

Run: `npm --prefix apps/web run build`  
Expected: Build thành công với exit code 0.

- [ ] **Step 6: Commit dọn dẹp cuối cùng và kích hoạt đồng bộ VPS**

```bash
git add -A
git commit -m "chore(datn): finalize migration from RULES.md to INFORMATION.md across codebase"
bash scripts/deploy_to_vps.sh --fast
```
