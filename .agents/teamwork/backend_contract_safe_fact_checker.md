# TASK CONTRACT: TASK-BE-FACT-CHECKER-NEURAL-INTEGRATION
## Tích Hợp SafeNliEngineAdapter Vào SafeFactChecker & DraftService

> **Contract Version:** 1.0  
> **Task ID:** `TASK-BE-FACT-CHECKER-NEURAL-INTEGRATION`  
> **Assignee:** Senior Backend & AI Specialist (`backend` @ pane `w2:p3`)  
> **Reviewer:** Lead Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
> **Repository:** `/home/VeriScholar/Workspace/VeriScholar`  
> **Branch:** `feat/vps-module2-remediation`  

---

### 1. Mục Tiêu & Giá Trị
- **Vấn đề kiến trúc:** `SafeFactChecker` (`packages/core/src/core/services/safe_fact_checker.py`) hiện tại vẫn chạy bộ luật suy nghiệm heuristic riêng mà chưa kích hoạt `SafeNliEngineAdapter` (mô hình ONNX offline INT8 đã thẩm định xong). Khi `POST /api/v1/drafts/{id}/verify-facts` được gọi qua `DraftService`, hệ thống chưa sử dụng mô hình nơ-ron chuyên dụng theo đúng PRD §3.2.
- **Mục tiêu:**
  1. Nâng cấp `SafeFactChecker` để nhận `nli_adapter: ISafeNliPort | None = None`. Khi `nli_adapter` được truyền vào, `SafeFactChecker` sử dụng `await self.nli_adapter.classify(claim, retrieval_context)` để suy diễn và gán nhãn Option A cho từng mệnh đề nguyên tử.
  2. Khi `nli_adapter is None`, giữ nguyên bộ luật heuristic làm fallback mặc định để đảm bảo 100% backward compatibility.
  3. Cập nhật `DraftService.verify_draft_facts` (`apps/api/src/api/services/draft_service.py`) để khởi tạo `SafeFactChecker(nli_adapter=SafeNliEngineAdapter())`.
  4. Bổ sung các bài test trong `packages/core/tests/domain/test_safe_fact_checker.py` kiểm chứng đường chạy nơ-ron thực tế khi nạp `SafeNliEngineAdapter`.

---

### 2. Tiêu Chí Nghiệm Thu (Acceptance Criteria)
1. **Tuân thủ Hexagonal Architecture:**
   - `SafeFactChecker` giao tiếp với `ISafeNliPort` qua contract trừu tượng (Dependency Injection).
   - Invariants: BoundingBox không bị bịa đặt, explanation $\le 2$ câu, tuyệt đối không rò rỉ chain-of-thought.
2. **Kiểm thử Đơn vị & Tích hợp:**
   - Thêm test trong `test_safe_fact_checker.py`:
     - Test `verify_text` với `SafeNliEngineAdapter`: xác nhận `SUPPORTED`, `CONTRADICTED`, `NOT_ENOUGH_INFO` với bounding boxes từ tài liệu nguồn.
   - Toàn bộ test cũ trong `test_safe_fact_checker.py`, `test_safe_nli_adapter.py`, `test_safe_nli_neural.py` và `test_drafts_lifecycle.py` phải **PASSED 100%** (0 failed).
3. **Chất lượng Code:**
   - `uv run ruff check .` và `uv run ruff format --check .` đạt 0 lỗi.
