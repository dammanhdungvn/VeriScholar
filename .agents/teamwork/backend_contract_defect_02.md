# TASK CONTRACT: TASK-BE-NLI-MODEL-INTEGRATION
## Tích Hợp Mô Hình Nơ-ron SAFE NLI & Giải Quyết DEFECT-02

> **Contract Version:** 1.0  
> **Task ID:** `TASK-BE-NLI-MODEL-INTEGRATION`  
> **Assignee:** Senior Backend & AI Specialist (`backend` @ pane `w2:p3`)  
> **Reviewer:** Lead Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
> **Repository:** `/home/VeriScholar/Workspace/VeriScholar`  
> **Nhánh công tác:** `feat/vps-module2-remediation`

---

### 1. Mục Tiêu & Giá Trị
Khắc phục khiếm khuyết **DEFECT-02** (ghi nhận trong PRD §3.2 và Handover Dossier):
- `SafeNliEngineAdapter` hiện đã hoàn thành hợp đồng Option A (3 nhãn: `supported`, `contradicted`, `not_enough_info`), nhưng 5 bài test suy diễn nơ-ron thực tế trong `test_safe_nli_neural.py` đang bị skip do thiếu checkpoint trọng số ONNX trên đĩa.
- Nhiệm vụ: Đóng gói trọng số quantized INT8 AVX2 của `cross-encoder/nli-deberta-v3-small` vào `models/nli/cross-encoder-nli-deberta-v3-small/`, kích hoạt chế độ suy diễn nơ-ron ngoại tuyến, đo đạc latency SLA (< 50ms trên CPU) và chạy eval benchmark SciFact.

---

### 2. Phạm Vi Thực Thi (Scope)
- **Tệp nguồn liên quan:**
  - `packages/core/src/core/services/safe_nli_adapter.py`
  - `models/README.md`
- **Tệp kiểm thử:**
  - `packages/core/tests/domain/test_safe_nli_neural.py`
  - `packages/core/tests/domain/test_safe_nli_adapter.py`
- **Thư mục lưu trữ trọng số:**
  - `models/nli/cross-encoder-nli-deberta-v3-small/`
  - Yêu cầu cấu trúc thư mục:
    ```text
    models/nli/cross-encoder-nli-deberta-v3-small/
    ├── config.json
    ├── tokenizer.json
    ├── tokenizer_config.json
    ├── special_tokens_map.json
    ├── spm.model
    └── onnx/
        └── model_quint8_avx2.onnx
    ```
- **Lưu ý bảo mật & Git:** Thư mục `models/*` (ngoại trừ `models/README.md`) đã được `.gitignore` bảo vệ, tuyệt đối không commit file nhị phân `.onnx` dung lượng lớn vào Git.

---

### 3. Tiêu Chí Nghiệm Thu (Acceptance Criteria)
1. **Khởi tạo Neural Engine thành công:**
   - `SafeNliEngineAdapter().is_neural_active` trả về `True`.
   - `SafeNliEngineAdapter().model_name` trả về `"cross-encoder/nli-deberta-v3-small"`.
2. **Giải phóng 100% test skipped trong `test_safe_nli_neural.py`:**
   - Chạy lệnh:
     ```bash
     uv run pytest packages/core/tests/domain/test_safe_nli_neural.py packages/core/tests/domain/test_safe_nli_adapter.py
     ```
   - **Tất cả 15/15 test cases phải PASSED** (0 skipped, 0 failed).
3. **Đạt chuẩn SLA độ trễ suy diễn:**
   - Test `test_neural_inference_latency_sla` đo đạc 15 lượt suy diễn trên CPU đạt trung bình `< 50ms`.
4. **Kiểm chuẩn SciFact Benchmark:**
   - Test `test_scifact_sample_evaluation_pipeline` chạy thông suốt với `SciFactAdapter`.
5. **Kiểm tra hồi quy Backend:**
   - Chạy kiểm thử toàn bộ `packages/core/tests/domain`:
     ```bash
     uv run pytest packages/core/tests/domain/
     ```
   - Chạy linter:
     ```bash
     uv run ruff check .
     uv run ruff format --check .
     ```
   - Không gây regression trên các test domain khác.

---

### 4. Bàn Giao & Báo Cáo
Ghi nhận kết quả thực nghiệm và latency đo được vào artifact hoặc báo cáo bàn giao cho CTO và Reviewer để chuẩn bị nghiệm thu đóng DEFECT-02.
