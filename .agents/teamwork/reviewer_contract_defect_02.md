# TASK CONTRACT: REVIEW-DEFECT-02-NLI-MODEL
## Thẩm Định Độc Lập DEFECT-02: Offline Neural NLI Model Weights & Inference SLA

> **Contract Version:** 1.0  
> **Task ID:** `REVIEW-DEFECT-02-NLI-MODEL`  
> **Assignee:** Lead Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
> **Author/Owner of Fix:** Senior Backend & AI Specialist (`backend` @ pane `w2:p3`)  
> **Repository:** `/home/VeriScholar/Workspace/VeriScholar`  
> **Branch:** `feat/vps-module2-remediation`  
> **Commit Revision:** `4968e95` (`[core] fix: resolve DEFECT-02 offline ONNX NLI model weights integration and latency optimization`)  
> **Báo cáo thẩm định bàn giao tại:** `docs/handoff/defect-02-review.md`

---

### 1. Mục Tiêu & Bối Cảnh Thẩm Định
Giải quyết dứt điểm **DEFECT-02** (đã được ghi nhận trong PRD §3.2 và Handover Dossier):
- **Hiện trạng trước bản vá:** Checkpoint trọng số mô hình `cross-encoder/nli-deberta-v3-small` chưa có trên đĩa; 5 test cases nơ-ron trọng yếu trong `test_safe_nli_neural.py` bị `skip`; latency và accuracy SLA ở trạng thái `NOT_MEASURED`.
- **Bản vá của Backend (Commit `4968e95`):**
  - Tải và cấu hình offline model weights quantized INT8 AVX2 (`model_quint8_avx2.onnx`, ~164.5 MB) cùng bộ tokenizer chuẩn vào `models/nli/cross-encoder-nli-deberta-v3-small/`.
  - Tối ưu hóa số luồng CPU (`intra_op_num_threads = 1` trên host 2 vCPUs) để triệt tiêu overhead context-switching.
  - Bổ sung session warmup và tối ưu hoá tiền xử lý câu khoa học.
  - Tự kiểm thử ghi nhận 15/15 tests PASS, latency p50 ~47.7ms.

Reviewer chịu trách nhiệm kiểm chứng độc lập toàn bộ các kết quả trên, phát hiện sai sót, kiểm tra an toàn Git/bộ nhớ và đưa ra phán quyết chính thức.

---

### 2. Phạm Vi Thẩm Định (Scope)
- **Mã nguồn lõi:**
  - `packages/core/src/core/services/safe_nli_adapter.py`
  - `.agents/teamwork/backend_contract_defect_02.md`
- **Bộ kiểm thử độc lập:**
  - `packages/core/tests/domain/test_safe_nli_neural.py`
  - `packages/core/tests/domain/test_safe_nli_adapter.py`
  - Toàn bộ suite `packages/core/tests/domain/`
- **Tệp trọng số & bảo mật đĩa:**
  - `models/nli/cross-encoder-nli-deberta-v3-small/`
  - Quy tắc `.gitignore` bảo vệ file `.onnx`.
- **Ranh giới:** Reviewer độc lập thẩm định và chạy test, không trực tiếp sửa code của tác giả.

---

### 3. Tiêu Chí Nghiệm Thu (Acceptance Criteria)
1. **Kiểm tra an toàn Repo & Git Tracking:**
   - Xác minh thư mục `models/` không bị track các tệp nhị phân lớn (.onnx) vào Git commit (`git status`, `git check-ignore`).
   - Kiểm tra SHA-256 / kích thước tệp trọng số `model_quint8_avx2.onnx`.
2. **Xác thực Neural Engine State & Fallback:**
   - `SafeNliEngineAdapter().is_neural_active == True`.
   - `SafeNliEngineAdapter().model_name == "cross-encoder/nli-deberta-v3-small"`.
   - Fallback `use_neural=False` và invalid path hoạt động mượt mà, không throw exception chưa xử lý.
3. **Thực thi Kiểm Thử Độc Lập (100% PASS, 0 Skipped):**
   - Chạy lệnh độc lập:
     ```bash
     uv run pytest packages/core/tests/domain/test_safe_nli_neural.py packages/core/tests/domain/test_safe_nli_adapter.py -v
     ```
   - Xác nhận cả 15 test cases đều **PASSED**, 0 skipped, 0 failed.
4. **Kiểm định SLA Độ Trễ (Latency SLA) & Benchmark SciFact:**
   - Thực thi độc lập phép đo độ trễ suy diễn trên CPU (`test_neural_inference_latency_sla`).
   - Ghi nhận chỉ số latency thực tế (Mean, Median, p95).
   - Kiểm chứng tính đúng đắn của pipeline SciFact adapter (`test_scifact_sample_evaluation_pipeline`).
5. **Đảm bảo không gây Hồi quy (Regression & Code Quality):**
   - Chạy toàn bộ domain tests:
     ```bash
     uv run pytest packages/core/tests/domain/
     ```
   - Chạy linter & format:
     ```bash
     uv run ruff check .
     uv run ruff format --check .
     ```
   - 0 error, 0 violation.

---

### 4. Bàn Giao & Định Dạng Báo Cáo
Ghi toàn bộ phát hiện, số liệu đo đạc khách quan và kết luận vào tệp:  
📁 `/home/VeriScholar/Workspace/VeriScholar/docs/handoff/defect-02-review.md`

Báo cáo phải kết luận rõ ràng:
- `VERDICT: PASS` — Khiếp khuyết DEFECT-02 chính thức được đóng và nghiệm thu.
- HOẶC `VERDICT: FAIL` — Danh sách các findings cụ thể kèm mức độ nghiêm trọng và yêu cầu sửa lỗi.
