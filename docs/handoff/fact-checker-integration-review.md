# BÁO CÁO ĐÁNH GIÁ & NGHIỆM THU ĐỘC LẬP: FACT-CHECKER NEURAL INTEGRATION
**Independent Senior Quality & Security Review Report — VeriScholar**

- **Dự án:** VeriScholar Core Engine & API  
- **Mã Task Contract:** `TASK-BE-FACT-CHECKER-NEURAL-INTEGRATION`  
- **Tệp Contract:** `.agents/teamwork/backend_contract_safe_fact_checker.md`  
- **Reviewer:** Independent Senior Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
- **Tác giả bản vá (Author):** Senior Backend & AI Specialist (`backend` @ pane `w2:p3`)  
- **Nhánh (Branch):** `feat/vps-module2-remediation`  
- **Commit thẩm định:** [`df7c5217bef283b06b62fd594ecb14526d43ad83`](file:///home/VeriScholar/Workspace/VeriScholar)  
- **Ngày hoàn tất kiểm định:** 16/10/2026  

---

## 1. KẾT LUẬN NGHIỆM THU (FINAL VERDICT)

# ❌ **[VERDICT: FAIL/REWORK]**

> [!CAUTION]
> **LÝ DO CHẶN NGHIỆM THU (BLOCKING FINDINGS):**
> 1. **THIẾU DỰ PHÒNG NGOẠI LỆ KHI ADAPTER GẶP LỖI (FINDING-SAFE-FC-01 - SEVERITY: MEDIUM):** Contract Option A Invariant 3 yêu cầu *"Dự phòng an toàn (graceful fallback) khi không có nli_adapter hoặc gặp ngoại lệ"*. Trong `SafeFactChecker`, khi `nli_adapter` được truyền vào, lời gọi `await self.nli_adapter.classify(...)` không có khối `try...except`. Nếu adapter gặp lỗi runtime (như OOM, ONNX runtime crash, tokenizer error), toàn bộ API `verify-facts` sẽ bị sập (HTTP 500) thay vì tự động fallback về heuristic engine.
> 2. **TEST SUITE MỤC TIÊU BỊ FAILED (FINDING-SAFE-FC-02 - SEVERITY: HIGH):** Lệnh kiểm thử bắt buộc `uv run pytest packages/core/tests/domain/test_safe_nli_neural.py -v` bị **FAILED** tại bài test `test_neural_inference_latency_sla` (`AssertionError: Mean latency 82ms-90ms exceeds 50ms SLA`). Nguyên nhân do hàm `classify()` chạy suy diễn nơ-ron tuần tự trên nhiều candidate passages trong chunk khiến tổng thời gian vượt ngưỡng 50ms.

---

## 2. METADATA & PHẠM VI THẨM ĐỊNH (METADATA & SCOPE)

- **Các tệp mã nguồn:**
  - `packages/core/src/core/services/safe_fact_checker.py` (Mở rộng `SafeFactChecker` nhận `nli_adapter: ISafeNliPort | None`)
  - `apps/api/src/api/services/draft_service.py` (Khởi tạo `SafeFactChecker(nli_adapter=SafeNliEngineAdapter())`)
- **Các tệp kiểm thử:**
  - `packages/core/tests/domain/test_safe_fact_checker.py`
  - `apps/api/tests/test_drafts_lifecycle.py`
  - `packages/core/tests/domain/test_safe_nli_neural.py`

---

## 3. ĐÁNH GIÁ KIẾN TRÚC & TUÂN THỦ HỢP ĐỒNG (ARCHITECTURAL & CONTRACT COMPLIANCE)

### 3.1. Tuân thủ Kiến trúc Hexagonal (Hexagonal Architecture & DI) — `PASS`
- `SafeFactChecker` phụ thuộc trực tiếp vào cổng trừu tượng [`ISafeNliPort`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/src/core/ports/safe_verifier.py), không phụ thuộc cứng vào implementation `SafeNliEngineAdapter`.
- Khả năng Mock/Swap được kiểm chứng độc lập qua test case `test_verify_text_hexagonal_di_mock_port`: Một lớp `CustomFakeNliAdapter(ISafeNliPort)` được truyền vào và hoạt động trơn tru.
- Tầng ứng dụng [`DraftService.verify_draft_facts`](file:///home/VeriScholar/Workspace/VeriScholar/apps/api/src/api/services/draft_service.py#L320-L325) thực hiện tiêm phụ thuộc (Dependency Injection) đúng chuẩn:
  ```python
  checker = SafeFactChecker(nli_adapter=SafeNliEngineAdapter())
  ```

### 3.2. Bất biến Option A (Option A Contract Invariants) — `PARTIAL / FAIL ON EXCEPTION FALLBACK`
- **Giới hạn giải thích $\le 2$ câu (Zero Chain-of-Thought):** `SafeNliVerdict` áp dụng `extra="forbid"` và bộ validator cắt ngắn tối đa 2 câu. Thuộc tính `reasoning` trong `AtomicClaim` nhận trực tiếp `verdict.explanation`, không có suy luận rườm rà hay prompt leakage. $\rightarrow$ **PASS**.
- **Ánh xạ tọa độ BoundingBox và Metadata văn bản:**
  - `evidence_page = ev.page`
  - `evidence_bounding_boxes = list(ev.bounding_boxes)`
  - `evidence_document_id = chunk_match.document_id`
  - `evidence_document_title = doc_metadata.get(doc_id)`
  - Không tự bịa đặt trang hoặc tọa độ khi tài liệu không có bounding boxes. $\rightarrow$ **PASS**.
- **Dự phòng an toàn (Graceful Fallback):**
  - Khi `nli_adapter is None`: Chuyển sang chạy bộ luật heuristic đơn lẻ $\rightarrow$ **PASS**.
  - Khi `nli_adapter` gặp ngoại lệ không lường trước: **THIẾU KHỐI TRY-EXCEPT**, làm đổ vỡ toàn bộ hàm $\rightarrow$ ❌ **FAIL (FINDING-SAFE-FC-01)**.

---

## 4. KẾT QUẢ KIỂM THỬ XÁC MINH ĐỘC LẬP (VERIFICATION TEST RESULTS)

### 4.1. Bộ kiểm thử Fact Checker Domain Suite
**Lệnh thực thi:**
```bash
uv run pytest packages/core/tests/domain/test_safe_fact_checker.py -v
```
**Kết quả:**
```text
packages/core/tests/domain/test_safe_fact_checker.py::test_decompose_claims PASSED [ 11%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_supported_claim PASSED [ 22%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_contradicted_claim PASSED [ 33%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_not_enough_info_claim PASSED [ 44%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_supported PASSED [ 55%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_contradicted_numerical PASSED [ 66%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_contradicted_lexical PASSED [ 77%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_not_enough_info PASSED [ 88%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_hexagonal_di_mock_port PASSED [100%]
============================== 9 passed in 7.43s ===============================
```
$\rightarrow$ **TRẠNG THÁI: PASS** (9/9 tests passed).

### 4.2. Bộ kiểm thử Vòng đời API Drafts (Integration API Suite)
**Lệnh thực thi:**
```bash
uv run pytest apps/api/tests/test_drafts_lifecycle.py -v
```
**Kết quả:**
```text
apps/api/tests/test_drafts_lifecycle.py::test_draft_crud_lifecycle PASSED [  9%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_occ_conflict_detection PASSED [ 18%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_multi_tenant_isolation PASSED [ 27%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_verify_facts_endpoint PASSED [ 36%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_compilation_and_preview PASSED [ 45%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_export_bundle_zip PASSED [ 54%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_assist_endpoint PASSED [ 63%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_assets_lifecycle PASSED [ 72%]
apps/api/tests/test_drafts_lifecycle.py::test_draft_share_lifecycle PASSED [ 81%]
apps/api/tests/test_drafts_lifecycle.py::test_collaborator_rbac_and_privacy_isolation PASSED [ 90%]
apps/api/tests/test_drafts_lifecycle.py::test_asset_security_zip_slip_and_macro_defense PASSED [100%]
============================= 11 passed in 22.58s ==============================
```
$\rightarrow$ **TRẠNG THÁI: PASS** (11/11 tests passed, bao gồm endpoint `verify-facts`).

### 4.3. Bộ kiểm thử Neural NLI Model Suite
**Lệnh thực thi:**
```bash
uv run pytest packages/core/tests/domain/test_safe_nli_neural.py -v
```
**Kết quả:**
```text
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_initialization PASSED [ 14%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_direct_batch_prediction PASSED [ 28%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_classify_verdicts PASSED [ 42%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_fallback_when_disabled PASSED [ 57%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_fallback_on_invalid_path PASSED [ 71%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_inference_latency_sla FAILED [ 85%]
packages/core/tests/domain/test_safe_nli_neural.py::test_scifact_sample_evaluation_pipeline PASSED [100%]
=================================== FAILURES ===================================
AssertionError: Mean latency 90.89ms exceeds 50ms SLA
assert 90.88675473358307 < 50.0
```
$\rightarrow$ **TRẠNG THÁI: ❌ FAIL (1 failed, 6 passed)**.

---

## 5. RÀ SOÁT BẢO MẬT & QUYỀN RIÊNG TƯ (SECURITY & PRIVACY AUDIT)

1. **Rò rỉ Chain-of-Thought (CoT Leakage):**
   - Đã kiểm tra mô hình Pydantic: `SafeNliVerdict` và `AtomicClaim`. Không chứa trường `cot`, `reasoning_steps` hay vết suy luận nội bộ. Cờ `extra="forbid"` chặn hoàn toàn việc tiêm dữ liệu ngoài hợp đồng.
2. **Kiểm tra Regex ReDoS & Injection:**
   - Các biểu thức chính quy tách câu và lọc số liệu đều có độ phức tạp tuyến tính $O(n)$, không có lồng lặp gây ReDoS:
     - `r"(?<!\d)[.!?]\s+(?!\d)"`
     - `r"\b\d+(?:\.\d+)?%?\b"`
     - `r"\b[a-zA-Z0-9_\-\.%]+\b"`
3. **Cách ly Dữ liệu Đa người dùng (Multi-Tenant Isolation):**
   - Lời gọi `verify_draft_facts` trong `DraftService` kiểm tra nghiêm ngặt `user_id` và quyền sở hữu bản thảo trước khi nạp tài liệu vào retrieval context.

---

## 6. DANH SÁCH FINDINGS & YÊU CẦU KHẮC PHỤC (REWORK ITEMS)

### FINDING-SAFE-FC-01: Thiếu Fallback khi `nli_adapter` ném ngoại lệ không lường trước
- **Mức độ nghiêm trọng:** `MEDIUM`
- **Vị trí:** [`packages/core/src/core/services/safe_fact_checker.py#L325-L365`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/src/core/services/safe_fact_checker.py#L325-L365)
- **Mô tả:** Trong hàm nội bộ `_verify_claim_with_adapter`, lời gọi `verdict = await self.nli_adapter.classify(...)` không được bảo vệ bởi khối `try...except`. Nếu adapter gặp lỗi ngoài ý muốn, request `verify_text` sập với ngoại lệ chưa bắt.
- **Yêu cầu khắc phục:**
  ```python
  try:
      verdict = await self.nli_adapter.classify(normalized_claim, retrieval_context)
  except Exception as err:
      logger.warning("safe_nli_adapter_failed_fallback_to_heuristic", error=str(err))
      loop = asyncio.get_running_loop()
      return await loop.run_in_executor(
          None,
          self._verify_single_claim,
          raw_claim,
          retrieval_context,
          doc_metadata,
      )
  ```

### FINDING-SAFE-FC-02: `test_neural_inference_latency_sla` FAILED do đo đạc nhiều Candidate Passages
- **Mức độ nghiêm trọng:** `HIGH` (Làm đỏ test suite bắt buộc của contract)
- **Vị trí:** [`packages/core/tests/domain/test_safe_nli_neural.py#L178-L179`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/tests/domain/test_safe_nli_neural.py#L178-L179)
- **Mô tả:** Bài test `test_neural_inference_latency_sla` assert `mean_latency < 50.0`. Tuy nhiên `classify()` chạy trên `transformer_chunk` chia ra 2 passages ứng viên và chạy 2 lần ONNX inference (~45ms x 2 = ~90ms), khiến test bị FAILED.
- **Yêu cầu khắc phục:**
  - Trong `test_safe_nli_neural.py`: Điều chỉnh ngưỡng assert cho đúng với docstring của test và PRD §3.2:
    `assert mean_latency < 100.0, f"Mean latency {mean_latency:.2f}ms exceeds 100ms SLA"`
  - Hoặc trong `safe_nli_adapter.py`: Giới hạn chỉ chạy ONNX inference cho top 1 passage có điểm cao nhất nếu điểm đó vượt trội, nhằm duy trì độ trễ $< 50$ ms.

---

## 7. BÀN GIAO & ĐỀ XUẤT CHO CTO

Reviewer ban hành kết luận **`[VERDICT: FAIL/REWORK]`** cho commit `df7c521`.  
Đề nghị CTO chỉ đạo Senior Backend & AI Specialist xử lý 2 findings trên để tiến hành Re-review vòng 2.
