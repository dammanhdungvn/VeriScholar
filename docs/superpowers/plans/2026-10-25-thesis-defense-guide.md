# Centralized Thesis Defense Guide (Plan 00 & Plan 01) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng cuốn Sổ tay Đồ án Tốt nghiệp tập trung (`docs/THESIS_DEFENSE_GUIDE.md`) chuyển hóa toàn bộ kiến trúc, use case và kết quả thực nghiệm của Plan 00 và Plan 01 sang ngôn ngữ trực quan, dễ hiểu kèm bộ câu hỏi phản biện Hội đồng và mã Trace ID đối chiếu trên Langfuse Cloud, đồng thời thiết lập liên kết hai chiều từ `docs/PRD/`.

**Architecture:** Tài liệu hóa tập trung theo cấu trúc lũy tiến (Chương 0, Chương 1 và sẵn sàng mở rộng tiếp cho các Plan sau) kết hợp kiểm thử tự động tính toàn vẹn tài liệu (`apps/api/tests/test_thesis_defense_guide_docs.py`), đảm bảo 100% đường dẫn tương đối theo Quy tắc số 5 trong `AGENTS.md`.

**Tech Stack:** Markdown, Python pytest, Langfuse Cloud API v2 evidence, Git.

**Spec:** [`docs/superpowers/specs/2026-10-25-thesis-defense-guide-design.md`](../specs/2026-10-25-thesis-defense-guide-design.md).

---

## Global Constraints

- Toàn bộ liên kết trong tài liệu Markdown (`docs/`) bắt buộc sử dụng đường dẫn tương đối (`./...`, `../...`), tuyệt đối cấm dùng `file://` (Quy tắc 5 `AGENTS.md`).
- Mỗi chương trong `docs/THESIS_DEFENSE_GUIDE.md` phải tuân thủ nghiêm ngặt 4 mục: (1) Giải thích bình dân & Ẩn dụ thực tế; (2) Phân tích Tại sao bắt buộc & Phân loại Cốt lõi / Mở rộng; (3) Bộ câu hỏi & Câu trả lời Phản biện Hội đồng (Defense Q&A); (4) Bằng chứng Thực nghiệm Đã Chạy (Empirical Evidence).
- Bốn Cổng Xác Minh Bắt Buộc (`bash scripts/dev/verify.sh` gồm `ruff`, `pytest`, `vitest`, `vite build`) phải đạt 100% exit code 0.

---

## Review Focus

1. **Relative Link Validity:** Mọi đường dẫn tương đối trỏ từ `docs/THESIS_DEFENSE_GUIDE.md` sang `docs/PRD/`, `docs/specs/` và ngược lại phải tồn tại thực tế trên hệ thống tệp.
2. **No Secret Leakage:** Tuyệt đối không ghi khóa API thô (raw key) vào tài liệu, chỉ sử dụng định dạng đã che (`sk-proj-...rwoA`, `sk-lf-...df4d`).
3. **Empirical Verifiability:** Các mã Trace ID và số liệu token phải khớp chính xác với dữ liệu thực tế đã đo đạc trên Langfuse Cloud và bài kiểm thử tự động.
4. **Defense Q&A Accuracy:** Các câu trả lời kỹ thuật cho câu hỏi của Hội đồng phải bám sát 100% kiến trúc lục giác, chuẩn mật mã AES-256-GCM và cơ chế CAS.
5. **Bidirectional Navigation:** Người đọc xem `docs/PRD/00-...` hoặc `docs/PRD/01-...` có thể chuyển nhanh sang đúng chương tương ứng trong sổ tay chỉ bằng 1 cú nhấp chuột.

---

## Task Structure

### Task 1: Documentation Integrity & Structure Test (`apps/api/tests`)

**Files:**
- Create: `apps/api/tests/test_thesis_defense_guide_docs.py`
- Test: `apps/api/tests/test_thesis_defense_guide_docs.py`

**Interfaces:**
- Consumes: Python Standard Library (`pathlib`, `re`), `pytest`.
- Produces: 3 test cases xác thực cấu trúc tài liệu, tính hợp lệ của đường dẫn tương đối và các liên kết chéo từ PRD.

- [ ] **Step 1: Write the failing test**

Tạo file `apps/api/tests/test_thesis_defense_guide_docs.py`:
```python
import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = REPO_ROOT / "docs"
GUIDE_FILE = DOCS_DIR / "THESIS_DEFENSE_GUIDE.md"
PRD_00 = DOCS_DIR / "PRD" / "00-overview-and-cleanup.md"
PRD_01 = DOCS_DIR / "PRD" / "01-auth-and-user.md"


def test_thesis_defense_guide_exists_and_contains_required_chapters():
    assert GUIDE_FILE.exists(), "docs/THESIS_DEFENSE_GUIDE.md must exist"
    content = GUIDE_FILE.read_text(encoding="utf-8")

    # Verify Chapter 0 and Chapter 1 headers
    assert "## Chương 0: Nền Tảng Kiến Trúc 18 Bảng CSDL & Kho Lưu Trữ CAS" in content
    assert "## Chương 1: Định Danh Học Giả, Mã ORCID & Két Sắt Khóa BYOK" in content

    # Verify 4 required sections in each chapter
    for ch_title in ["Chương 0", "Chương 1"]:
        assert f"1. Giải Thích Bình Dân & Ẩn Dụ Thực Tế ({ch_title})" in content or "1. Giải Thích Bình Dân" in content
        assert "Tại Sao Bắt Buộc Phải Có" in content
        assert "Bộ Câu Hỏi & Câu Trả Lời Phản Biện Hội Đồng" in content
        assert "Bằng Chứng Thực Nghiệm Đã Chạy" in content


def test_docs_contain_no_absolute_file_links():
    md_files = [GUIDE_FILE, PRD_00, PRD_01]
    for md_file in md_files:
        if not md_file.exists():
            continue
        text = md_file.read_text(encoding="utf-8")
        assert "file://" not in text, f"{md_file} contains prohibited file:// absolute link"


def test_prd_files_cross_reference_thesis_guide():
    assert PRD_00.exists()
    assert PRD_01.exists()
    text_00 = PRD_00.read_text(encoding="utf-8")
    text_01 = PRD_01.read_text(encoding="utf-8")

    assert "../THESIS_DEFENSE_GUIDE.md" in text_00, "PRD-00 must link to THESIS_DEFENSE_GUIDE.md"
    assert "../THESIS_DEFENSE_GUIDE.md" in text_01, "PRD-01 must link to THESIS_DEFENSE_GUIDE.md"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_thesis_defense_guide_docs.py -v`  
Expected: FAIL (vì `docs/THESIS_DEFENSE_GUIDE.md` chưa được tạo và 2 file PRD chưa có liên kết).

- [ ] **Step 3: Commit the failing test**

```bash
git add apps/api/tests/test_thesis_defense_guide_docs.py
git commit -m "test(docs): add automated integrity test for thesis defense guide"
```

---

### Task 2: Create Centralized Thesis Defense Guide (`docs/THESIS_DEFENSE_GUIDE.md`)

**Files:**
- Create: `docs/THESIS_DEFENSE_GUIDE.md`
- Test: `apps/api/tests/test_thesis_defense_guide_docs.py::test_thesis_defense_guide_exists_and_contains_required_chapters`

**Interfaces:**
- Consumes: Đặc tả kiến trúc Plan 00, Plan 01, kết quả chạy thực nghiệm Langfuse và PostgreSQL 16.
- Produces: `docs/THESIS_DEFENSE_GUIDE.md` hoàn chỉnh gồm Lời mở đầu, Chương 0 và Chương 1.

- [ ] **Step 1: Write `docs/THESIS_DEFENSE_GUIDE.md`**

Nội dung bao gồm:
1. **Lời mở đầu:** Hướng dẫn cách sinh viên sử dụng tài liệu này khi viết Thuyết minh Đồ án Tốt nghiệp (Chương Tổng quan & Chương Kiến trúc) và slide bảo vệ trước Hội đồng.
2. **Chương 0 (Plan 00 — Nền Tảng Kiến Trúc 18 Bảng & Kho CAS):**
   - *1. Giải thích bình dân & Ẩn dụ thực tế:* Ẩn dụ "Nền móng tòa nhà 18 phòng chức năng" và "Kho thư viện thông minh nhận diện vân tay số". Ví dụ thực tế: 50 sinh viên tải cùng 1 file PDF 20MB chỉ tốn 20MB dung lượng máy chủ thay vì 1.000MB; bảng `document_chunks` lưu tọa độ hộp `0..1000` để AI tô sáng đúng chỗ.
   - *2. Tại sao bắt buộc phải có & Bảng phân loại:* Cốt lõi (CSDL quan hệ phân vùng `user_id`, CAS băm SHA-256) vs. Mở rộng (các tham số cache).
   - *3. Bộ câu hỏi & câu trả lời phản biện Hội đồng (Defense Q&A):* 4 câu hỏi trọng tâm (Tại sao dùng CAS thay vì lưu binary trực tiếp vào DB? Tại sao dùng PostgreSQL + pgvector thay vì hệ thống Vector DB rời như Pinecone/Milvus? Cơ chế Zero-Retention xóa vật lý hoạt động thế nào để không xóa nhầm file của người khác? Tại sao chọn Kiến trúc Lục giác Hexagonal?).
   - *4. Bằng chứng thực nghiệm đã chạy:* 18 bảng CSDL, script kiểm tra tự động `bash scripts/dev/verify.sh` đạt 46/46 test Python, 3/3 test Frontend.
3. **Chương 1 (Plan 01 — Định Danh Học Giả, ORCID & Két Sắt BYOK AES-256-GCM):**
   - *1. Giải thích bình dân & Ẩn dụ thực tế:* Ẩn dụ "Thẻ căn cước nghiên cứu viên" và "Két sắt số cá nhân". Ví dụ thực tế: Học giả đọc bài trên laptop ở trường rồi về máy tính bàn ở nhà vẫn mở đúng trang PDF đang đọc dở (nhờ refresh token tự động); học giả nhập mã OpenAI cá nhân để chạy mô hình mạnh nhất mà không sợ lộ khóa hay bị trừ tiền vô cớ.
   - *2. Tại sao bắt buộc phải có & Cơ chế Hybrid thông minh:* Tại sao phân quyền là bắt buộc (cô lập tài sản học thuật, chống rò rỉ đề tài giữa các nhóm nghiên cứu); tại sao BYOK là cơ chế linh hoạt (người dùng không cần nhập key vẫn dùng được nhờ khóa hệ thống `.env`, người dùng nâng cao tự gắn key riêng thì hệ thống ưu tiên dùng key cá nhân).
   - *3. Bộ câu hỏi & câu trả lời phản biện Hội đồng (Defense Q&A):* 4 câu hỏi trọng tâm (Tại sao dùng AES-256-GCM thay vì AES-CBC hay RSA? Khóa master key server quản lý thế nào, nếu hacker chiếm được DB có giải mã được key không? Tại sao mã ORCID lại quan trọng trong nghiên cứu học thuật? Cơ chế Single-Flight Refresh Token chống race condition thế nào khi mở nhiều tab?).
   - *4. Bằng chứng thực nghiệm đã chạy:* Số liệu thực nghiệm gọi OpenAI `gpt-5.4-mini` thành công (33 input tokens, 66 output tokens, latency 3.32s), Trace ID trên Langfuse Cloud (`f8d087c559790eafd0812e6293d23a34`, `68a38d9b98d145df18aa995ce39e901a`, `9423ed4e264360d619c4e0494900f4f5`), và tính năng ẩn danh băm HMAC-SHA256 user ID.

- [ ] **Step 2: Run test to verify Chapter 0 & Chapter 1 pass**

Run: `uv run pytest apps/api/tests/test_thesis_defense_guide_docs.py::test_thesis_defense_guide_exists_and_contains_required_chapters -v`  
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add docs/THESIS_DEFENSE_GUIDE.md
git commit -m "docs(thesis): add Chapter 0 and Chapter 1 in THESIS_DEFENSE_GUIDE.md"
```

---

### Task 3: Establish Cross-References in PRD Documents (`docs/PRD`)

**Files:**
- Modify: `docs/PRD/00-overview-and-cleanup.md`
- Modify: `docs/PRD/01-auth-and-user.md`
- Test: `apps/api/tests/test_thesis_defense_guide_docs.py`

**Interfaces:**
- Consumes: `docs/THESIS_DEFENSE_GUIDE.md` anchor links.
- Produces: Mục "7. Tài Liệu Tham Chiếu Báo Cáo & Bảo Vệ Đồ Án Tốt Nghiệp" tại cuối mỗi file PRD.

- [ ] **Step 1: Add cross-reference section to `docs/PRD/00-overview-and-cleanup.md`**

Thêm vào cuối file `00-overview-and-cleanup.md`:
```markdown
---

## 7. Tài Liệu Tham Chiếu Báo Cáo & Bảo Vệ Đồ Án Tốt Nghiệp

Dành cho tác giả khi biên soạn Thuyết minh Đồ án Tốt nghiệp và chuẩn bị slide bảo vệ trước Hội đồng:
* **Giải thích bình dân, ẩn dụ thực tế & Use case:** Xem mục 1 trong [Sổ Tay Bảo Vệ Đồ Án Tốt Nghiệp — Chương 0](../THESIS_DEFENSE_GUIDE.md#chương-0-nền-tảng-kiến-trúc-18-bảng-csdl--kho-lưu-trữ-cas).
* **Phân tích Tại sao bắt buộc & Có thể giản lược không:** Xem mục 2 trong [Sổ Tay Bảo Vệ Đồ Án — Chương 0](../THESIS_DEFENSE_GUIDE.md#chương-0-nền-tảng-kiến-trúc-18-bảng-csdl--kho-lưu-trữ-cas).
* **Bộ câu hỏi & câu trả lời phản biện Hội đồng (Q&A):** Xem mục 3 trong [Sổ Tay Bảo Vệ Đồ Án — Chương 0](../THESIS_DEFENSE_GUIDE.md#chương-0-nền-tảng-kiến-trúc-18-bảng-csdl--kho-lưu-trữ-cas).
* **Số liệu thực chứng kiểm thử:** Xem mục 4 trong [Sổ Tay Bảo Vệ Đồ Án — Chương 0](../THESIS_DEFENSE_GUIDE.md#chương-0-nền-tảng-kiến-trúc-18-bảng-csdl--kho-lưu-trữ-cas).
```

- [ ] **Step 2: Add cross-reference section to `docs/PRD/01-auth-and-user.md`**

Thêm vào cuối file `01-auth-and-user.md`:
```markdown
---

## 7. Tài Liệu Tham Chiếu Báo Cáo & Bảo Vệ Đồ Án Tốt Nghiệp

Dành cho tác giả khi biên soạn Thuyết minh Đồ án Tốt nghiệp và chuẩn bị slide bảo vệ trước Hội đồng:
* **Giải thích bình dân, ẩn dụ thực tế & Use case BYOK:** Xem mục 1 trong [Sổ Tay Bảo Vệ Đồ Án Tốt Nghiệp — Chương 1](../THESIS_DEFENSE_GUIDE.md#chương-1-định-danh-học-giả-mã-orcid--két-sắt-khóa-byok).
* **Phân tích Tại sao bắt buộc & Cơ chế Hybrid thông minh:** Xem mục 2 trong [Sổ Tay Bảo Vệ Đồ Án — Chương 1](../THESIS_DEFENSE_GUIDE.md#chương-1-định-danh-học-giả-mã-orcid--két-sắt-khóa-byok).
* **Bộ câu hỏi & câu trả lời phản biện Hội đồng (Q&A):** Xem mục 3 trong [Sổ Tay Bảo Vệ Đồ Án — Chương 1](../THESIS_DEFENSE_GUIDE.md#chương-1-định-danh-học-giả-mã-orcid--két-sắt-khóa-byok).
* **Bằng chứng thực nghiệm Langfuse Cloud & OpenAI:** Xem mục 4 trong [Sổ Tay Bảo Vệ Đồ Án — Chương 1](../THESIS_DEFENSE_GUIDE.md#chương-1-định-danh-học-giả-mã-orcid--két-sắt-khóa-byok).
```

- [ ] **Step 3: Run all doc integrity tests to verify 100% pass**

Run: `uv run pytest apps/api/tests/test_thesis_defense_guide_docs.py -v`  
Expected: 3 passed in 0.05s

- [ ] **Step 4: Commit**

```bash
git add docs/PRD/00-overview-and-cleanup.md docs/PRD/01-auth-and-user.md
git commit -m "docs(prd): add cross-reference navigation to THESIS_DEFENSE_GUIDE.md"
```

---

### Task 4: Full 4-Gate System Verification

**Files:**
- Entire repository verification

- [ ] **Step 1: Run 4 Mandatory Verification Gates**

Run: `bash scripts/dev/verify.sh`  
Expected output:
- Gate 1 (Ruff): All checks passed!
- Gate 2 (Pytest): 49 passed (bao gồm 3 test tài liệu mới)
- Gate 3 (Vitest): 3 passed (100%)
- Gate 4 (Vite Build): built successfully
- Overall: `✅ All 4 Verification Gates PASSED (100% Exit Code 0)!`

- [ ] **Step 2: Final Commit (if any cleanups needed)**
