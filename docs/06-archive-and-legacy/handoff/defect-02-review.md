# BÁO CÁO ĐÁNH GIÁ & NGHIỆM THU ĐỘC LẬP: DEFECT-02
## Offline Neural NLI Model Weights & Inference SLA Verification
**Independent Senior Quality & Security Review Report — VeriScholar**

- **Dự án:** VeriScholar Core Engine  
- **Mã Task Contract:** `REVIEW-DEFECT-02-NLI-MODEL` (Phiên bản: 1.0)  
- **Tệp Contract:** `.agents/teamwork/reviewer_contract_defect_02.md`  
- **Reviewer:** Independent Senior Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
- **Tác giả bản vá (Author):** Senior Backend & AI Specialist (`backend` @ pane `w2:p3`)  
- **Nhánh (Branch):** `feat/vps-module2-remediation`  
- **Commit thẩm định:** [`4968e95cf86cea3614f0439e06fced48b1841a75`](file:///home/VeriScholar/Workspace/VeriScholar)  
- **Ngày hoàn tất kiểm định:** 16/10/2026  

---

## 1. KẾT LUẬN NGHIỆM THU (OVERALL VERDICT)

# ✅ **VERDICT: PASS (DEFECT-02 OFFICIALLY CLOSED)**

> [!NOTE]
> **TỔNG QUAN KẾT QUẢ ĐÁNH GIÁ:**
> - Toàn bộ 5 tiêu chí nghiệm thu của Contract `REVIEW-DEFECT-02-NLI-MODEL` đều đạt kết quả xuất sắc (**PASS**).
> - Trọng số mô hình ONNX lượng tử hóa INT8 AVX2 (`model_quint8_avx2.onnx`, ~164.5 MB) và bộ tokenizer đã được đóng gói chuẩn xác, an toàn ngoại tuyến (100% offline, zero internet egress).
> - Tất cả 5 bài test nơ-ron trước đây bị `skip` trong `test_safe_nli_neural.py` đã được giải phóng và vượt qua 100% (15/15 tests PASS, 0 skipped, 0 failed).
> - Đo đạc độ trễ độc lập trên CPU đạt trung bình **47.83 ms** (p50: **47.83 ms**, p95: **49.37 ms**), đáp ứng nghiêm ngặt chỉ tiêu SLA $\le 50$ ms của PRD §3.2.
> - An toàn Git được bảo đảm tuyệt đối: tệp nhị phân `.onnx` không bị track vào commit Git; kiểm tra hồi quy domain suite (115 passed) và linter (`ruff`) đạt 0 lỗi.

---

## 2. MA TRẬN ĐÁNH GIÁ 5 TIÊU CHÍ HỢP ĐỒNG (ACCEPTANCE CRITERIA MATRIX)

| STT | Tiêu chí kiểm định (`REVIEW-DEFECT-02-NLI-MODEL`) | Yêu cầu kỹ thuật chi tiết | Phương pháp kiểm chứng độc lập | Kết quả thực tế | Trạng thái |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | **An toàn Repository & Git Tracking** | - Cấm commit file nhị phân `.onnx` vào Git<br>- File weights tồn tại đầy đủ trên đĩa cục bộ kèm SHA-256 xác thực | `git status`<br>`git check-ignore`<br>`git ls-files models/`<br>`sha256sum` | - `.gitignore` dòng 79 bảo vệ `models/*`<br>- Chỉ có `models/README.md` được Git track<br>- Weights 172,503,005 bytes (~164.5 MB) | ✅ **PASS** |
| **2** | **Trạng thái Neural Engine & Fallback** | - `is_neural_active == True`<br>- Model: `cross-encoder/nli-deberta-v3-small`<br>- Graceful fallback khi `use_neural=False` hoặc sai đường dẫn | Thực thi Python harness kiểm tra đối tượng `SafeNliEngineAdapter` | - Engine nạp ONNX INT8 thành công<br>- Fallback kích hoạt rule-engine mượt mà, zero unhandled exception | ✅ **PASS** |
| **3** | **Thực thi Kiểm Thử Độc Lập** | 100% test cases trong `test_safe_nli_neural.py` và `test_safe_nli_adapter.py` phải PASS, 0 skipped, 0 failed | Chạy lệnh độc lập:<br>`uv run pytest ... -v` | **15/15 passed** trong 17.45s (0 skipped, 0 failed) | ✅ **PASS** |
| **4** | **Kiểm định SLA Độ Trễ & SciFact Benchmark** | - Latency CPU trung bình $< 50$ ms<br>- SciFact evaluation pipeline hoạt động chính xác | Benchmark độc lập 30 runs<br>`test_scifact_sample_evaluation_pipeline` | - Mean: **47.83 ms**<br>- Median: **47.83 ms**<br>- p95: **49.37 ms**<br>- SciFact test PASSED | ✅ **PASS** |
| **5** | **Bảo đảm Không Gây Hồi Quy (Regression)** | - Toàn bộ domain test suites chạy sạch<br>- Ruff linter & format đạt 0 violation | `uv run pytest packages/core/tests/domain/`<br>`uv run ruff check .`<br>`uv run ruff format --check .` | - 115 passed (3 skipped sandbox)<br>- Ruff check: All checks passed<br>- Ruff format: 255 files formatted | ✅ **PASS** |

---

## 3. CHI TIẾT BẰNG CHỨNG THỰC NGHIỆM ĐỘC LẬP (EMPIRICAL AUDIT EVIDENCE)

### 3.1. Kiểm tra An toàn Tệp Trọng số & Ranh giới Git
**Lệnh thực thi:**
```bash
git check-ignore -v models/nli/cross-encoder-nli-deberta-v3-small/onnx/model_quint8_avx2.onnx
git ls-files models/
sha256sum models/nli/cross-encoder-nli-deberta-v3-small/onnx/model_quint8_avx2.onnx
```
**Ghi nhận đầu ra:**
- Quy tắc ignore: `.gitignore:79:models/*`
- Danh sách file tracked trong `models/`: duy nhất `models/README.md`.
- Kích thước tệp trọng số: **172,503,005 bytes** (164.5 MB).
- Checksum SHA-256:
  ```text
  03c2221313dc0c3eac9cec1f746d1319d33f2c2901fcce1c0f08f4daac9b6dae  models/nli/cross-encoder-nli-deberta-v3-small/onnx/model_quint8_avx2.onnx
  ```
- Cấu trúc thư mục tokenizer đầy đủ: `config.json`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `spm.model`.

### 3.2. Kiểm chứng Khởi tạo Session ONNX & Cơ chế Fallback An toàn
**Thực nghiệm:**
```python
from core.services.safe_nli_adapter import SafeNliEngineAdapter
from pathlib import Path

# 1. Kích hoạt bình thường
adapter = SafeNliEngineAdapter()
assert adapter.is_neural_active is True
assert adapter.model_name == "cross-encoder/nli-deberta-v3-small"

# 2. Fallback có chủ đích (use_neural=False)
fallback = SafeNliEngineAdapter(use_neural=False)
assert fallback.is_neural_active is False

# 3. Fallback khi đường dẫn hỏng (model_dir="/tmp/invalid")
invalid = SafeNliEngineAdapter(model_dir=Path("/tmp/invalid"))
assert invalid.is_neural_active is False
```
Ghi nhận log hệ thống:
```text
[info] safe_nli_neural_engine_ready model=cross-encoder/nli-deberta-v3-small weights=model_quint8_avx2.onnx
[info] safe_nli_custom_dir_not_found path=/tmp/invalid
```
Khẳng định: Adapter khởi tạo an toàn, không làm đổ vỡ runtime khi thiếu file hoặc khi cấu hình fallback.

### 3.3. Kết quả Chạy Bộ Test NLI (100% PASS, 0 Skipped)
**Lệnh thực thi:**
```bash
uv run pytest packages/core/tests/domain/test_safe_nli_neural.py packages/core/tests/domain/test_safe_nli_adapter.py -v
```
**Stdout ghi nhận:**
```text
============================= test session starts ==============================
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_initialization PASSED [  6%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_direct_batch_prediction PASSED [ 13%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_classify_verdicts PASSED [ 20%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_fallback_when_disabled PASSED [ 26%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_fallback_on_invalid_path PASSED [ 33%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_inference_latency_sla PASSED [ 40%]
packages/core/tests/domain/test_safe_nli_neural.py::test_scifact_sample_evaluation_pipeline PASSED [ 46%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_supported PASSED [ 53%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_contradicted_numerical PASSED [ 60%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_contradicted_lexical PASSED [ 66%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_not_enough_info PASSED [ 73%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_option_a_contract_forbids_chain_of_thought PASSED [ 80%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_option_a_contract_truncates_long_explanation PASSED [ 86%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_pair_ordering_and_model_selection PASSED [ 93%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_evidence_without_coordinates_preserves_none_without_fabrication PASSED [100%]
============================= 15 passed in 17.45s ==============================
```

### 3.4. Đo đạc Thống kê Độc lập Độ trễ Suy diễn (Latency SLA Benchmark)
Thực thi kiểm chứng 30 lượt suy diễn thực tế trên môi trường host CPU (2 vCPUs) sau bước warmup:
- **Thời gian khởi động lạnh (Cold Start):** `54.17 ms`
- **Số lượt đo (Warm Iterations):** `30`
- **Độ trễ trung bình (Mean Latency):** **`47.83 ms`** *(Chỉ tiêu SLA: $< 50.0$ ms $\rightarrow$ **ĐẠT**)*
- **Trung vị (Median / p50):** **`47.83 ms`**
- **Độ trễ tối thiểu (Min):** `46.31 ms`
- **Độ trễ tối đa (Max):** `50.05 ms`
- **Phân vị 90 (p90):** `49.14 ms`
- **Phân vị 95 (p95):** `49.37 ms`
- **Phân vị 99 (p99):** `49.86 ms`
- **Độ lệch chuẩn (Std Dev):** `0.99 ms` (phân phối độ trễ cực kỳ ổn định)

### 3.5. Kiểm tra Bộ nhớ & Tránh Rò rỉ (Memory Footprint)
- **Dung lượng RSS sau khi nạp ONNX Model:** `695.65 MB`
- **Dung lượng RSS sau 50 lượt batch inferences liên tục:** `696.46 MB` (mức tăng $\approx +0.81$ MB, hoàn toàn không xuất hiện rò rỉ bộ nhớ).

### 3.6. Kiểm tra Hồi quy Toàn bộ Phân hệ Domain & Code Quality
- **Chạy toàn bộ 118 domain tests:**
  ```text
  115 passed, 3 skipped (sandbox container probe tests) in 18.01s
  ```
  *(Không có bất kỳ test domain nào bị ảnh hưởng hoặc hồi quy lỗi).*
- **Ruff Linter:** `All checks passed!` (0 errors).
- **Ruff Formatter:** `255 files already formatted` (0 violations).

---

## 4. GHI CHÚ VẬN HÀNH & GIỚI HẠN PHẠM VI (OPERATIONAL BOUNDARY NOTES)

Reviewer ghi nhận các quan sát chuyên sâu để phục vụ lộ trình phát triển tiếp theo (không cấu thành blocker cho bản vá hiện tại):
1. **Phạm vi ngôn ngữ (Language Domain):** Mô hình `cross-encoder/nli-deberta-v3-small` được huấn luyện chủ yếu trên văn bản tiếng Anh (MNLI, FEVER, ANLI) và hàm tách từ `_extract_tokens` sử dụng regex ASCII chuẩn cho văn bản khoa học quốc tế. Với các bài báo hoàn toàn bằng tiếng Việt, hệ thống sẽ kích hoạt fallback hoặc dựa vào các thuật ngữ tiếng Anh/số liệu. Khuyến nghị đưa việc hỗ trợ mô hình NLI đa ngôn ngữ (Multilingual NLI) vào backlog giai đoạn tiếp theo.
2. **Cấu hình đa luồng (Threading):** Cấu hình `opts.intra_op_num_threads = 1 if cpu_count <= 2 else min(cpu_count, 4)` chứng minh hiệu quả vượt trội trong việc triệt tiêu tranh chấp CPU context-switch trên các máy chủ ảo hóa 2 vCPUs.

---

## 5. BÀN GIAO & ĐỀ XUẤT CHO CTO

1. Bản vá tại commit [`4968e95`](file:///home/VeriScholar/Workspace/VeriScholar) đã khắc phục toàn diện, chính xác và an toàn khiếm khuyết **DEFECT-02**.
2. Toàn bộ 5 tiêu chí nghiệm thu được thỏa mãn tuyệt đối với bằng chứng thực nghiệm đầy đủ.
3. **Phán quyết chính thức:** **`VERDICT: PASS (DEFECT-02 CLOSED)`**.
4. Reviewer đề xuất CTO hợp nhất commit `4968e95` vào nhánh chính và đóng trạng thái PENDING của DEFECT-02 trên Milestone 1 Dossier.
