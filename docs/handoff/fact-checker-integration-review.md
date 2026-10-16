# BÁO CÁO ĐÁNH GIÁ & NGHIỆM THU ĐỘC LẬP: FACT-CHECKER NEURAL INTEGRATION
**Independent Senior Quality & Security Review Report — VeriScholar**

- **Dự án:** VeriScholar Core Engine & API  
- **Mã Task Contract:** `TASK-BE-FACT-CHECKER-NEURAL-INTEGRATION`  
- **Tệp Contract:** `.agents/teamwork/backend_contract_safe_fact_checker.md`  
- **Reviewer:** Independent Senior Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
- **Tác giả bản vá (Author):** Senior Backend & AI Specialist (`backend` @ pane `w2:p3`)  
- **Nhánh (Branch):** `feat/vps-module2-remediation`  
- **Commit thẩm định:**  
  - Vòng 1: [`df7c5217bef283b06b62fd594ecb14526d43ad83`](file:///home/VeriScholar/Workspace/VeriScholar) (`[VERDICT: FAIL/REWORK]`)  
  - Vòng 2 (Bản vá khắc phục): [`83b6505942fd012ea60708622316baa9832bb2c0`](file:///home/VeriScholar/Workspace/VeriScholar)  
- **Ngày hoàn tất kiểm định:** 16/10/2026  

---

## 1. KẾT LUẬN NGHIỆM THU CUỐI CÙNG (FINAL VERDICT)

# ✅ **[VERDICT: PASS (OFFICIALLY ACCEPTED & CLOSED)]**

> [!NOTE]
> **TỔNG KẾT RE-REVIEW VÒNG 2:**
> Bản vá tại commit [`83b6505`](file:///home/VeriScholar/Workspace/VeriScholar) của Senior Backend & AI Specialist đã xử lý dứt điểm, chuẩn xác và an toàn cả 2 findings được chỉ ra ở Vòng 1:
> 1. `FINDING-SAFE-FC-01` (Thiếu fallback khi adapter ném ngoại lệ): **ĐÃ KHẮC PHỤC (CLOSED)** qua khối `try...except` và fallback tự động sang bộ luật heuristic `self._verify_single_claim`. Đã có bài test hồi quy xác minh độc lập `test_verify_text_with_adapter_exception_fallback_to_heuristic`.
> 2. `FINDING-SAFE-FC-02` (Đo đạc nhiều candidate passages gây vượt ngưỡng SLA): **ĐÃ KHẮC PHỤC (CLOSED)** nhờ cơ chế early-return ngay khi tìm thấy kết luận dứt khoát trên passage có điểm căn chỉnh cao nhất, đồng thời đồng bộ ngưỡng assert theo đúng chỉ tiêu PRD §3.2 (`< 100ms`).
>
> Toàn bộ 28 bài kiểm thử độc lập (`test_safe_fact_checker.py`: 10/10, `test_safe_nli_neural.py`: 7/7, `test_drafts_lifecycle.py`: 11/11) cùng linter và format (`ruff`) đều đạt **100% PASS** (0 failed, 0 skipped). Nhiệm vụ tích hợp Fact-Checker Neural Engine chính thức đủ điều kiện nghiệm thu đóng.

---

## 2. MA TRẬN ĐỐI CHIẾU TIÊU CHÍ VÒNG 1 VS VÒNG 2

| STT | Tiêu chí kiểm định (`TASK-BE-FACT-CHECKER-NEURAL-INTEGRATION`) | Vòng 1 (df7c521) | Vòng 2 (83b6505) | Kết luận Vòng 2 |
| :---: | :--- | :---: | :---: | :---: |
| **1** | **Kiến trúc Hexagonal & Loose-Coupling:** `SafeFactChecker` phụ thuộc `ISafeNliPort`, `DraftService` tiêm `SafeNliEngineAdapter()` qua DI | PASS | PASS | ✅ **PASS** |
| **2.1** | **Bất biến Option A — Giới hạn $\le 2$ câu:** Zero CoT, validator cắt ngắn $\le 2$ câu, `extra="forbid"` | PASS | PASS | ✅ **PASS** |
| **2.2** | **Bất biến Option A — Ánh xạ Bounding Box & Page:** Ánh xạ chuẩn xác từ chunks sang `AtomicClaim`, không bịa đặt tọa độ | PASS | PASS | ✅ **PASS** |
| **2.3** | **Bất biến Option A — Dự phòng an toàn (Fallback):** Fallback khi `nli_adapter is None` HOẶC khi adapter ném ngoại lệ | ❌ FAIL *(Sập unhandled khi adapter crash)* | PASS *(try-except fallback về heuristic)* | ✅ **PASS** |
| **3.1** | **Kiểm thử Fact Checker:** `packages/core/tests/domain/test_safe_fact_checker.py` | PASS (9/9) | PASS (10/10 tests) | ✅ **PASS** |
| **3.2** | **Kiểm thử API Vòng đời Drafts:** `apps/api/tests/test_drafts_lifecycle.py` | PASS (11/11) | PASS (11/11 tests) | ✅ **PASS** |
| **3.3** | **Kiểm thử Neural NLI Model Suite:** `packages/core/tests/domain/test_safe_nli_neural.py` | ❌ FAIL *(Latency assert fail)* | PASS (7/7 tests) | ✅ **PASS** |
| **4** | **Bảo mật & Quyền riêng tư:** Không rò rỉ CoT, Regex $O(n)$ an toàn, cách ly đa người dùng | PASS | PASS | ✅ **PASS** |

---

## 3. KẾT QUẢ THẨM ĐỊNH LẠI CHI TIẾT THEO 2 FINDINGS

### 3.1. FINDING-SAFE-FC-01: Bổ sung khối try...except và Graceful Fallback khi Adapter ném ngoại lệ
- **Trạng thái:** ✅ **ĐÃ KHẮC PHỤC (CLOSED)**
- **Kiểm tra mã nguồn:**
  Tại [`packages/core/src/core/services/safe_fact_checker.py#L328-L345`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/src/core/services/safe_fact_checker.py#L328-L345):
  ```python
  async def _verify_claim_with_adapter(raw_claim: str) -> AtomicClaim:
      normalized_claim, entities = self.normalize_entities(raw_claim)
      try:
          assert self.nli_adapter is not None
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
- **Phân tích kỹ thuật:**
  Nếu `nli_adapter` gặp bất kỳ ngoại lệ nào trong quá trình suy diễn (như ONNX runtime crash, tokenizer error, OOM hoặc mạng/I/O), hệ thống không còn để lọt lỗi làm sập API (HTTP 500). Thay vào đó, nó ghi log cảnh báo và chuyển giao ngay lập tức cho bộ luật heuristic `self._verify_single_claim` thực thi trong thread pool executor, bảo đảm tính sẵn sàng cao và trải nghiệm người dùng không bị gián đoạn.
- **Bằng chứng kiểm thử hồi quy:**
  Bài test [`test_verify_text_with_adapter_exception_fallback_to_heuristic`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/tests/domain/test_safe_fact_checker.py#L272-L300) giả lập một `CrashingNliAdapter` ném `RuntimeError`. Test case đã xác minh thành công:
  - Khối try-except bắt được lỗi.
  - Phân hệ fallback heuristic tiếp quản và trả về `FactVerificationStatus.SUPPORTED` với metadata tài liệu đầy đủ.

---

### 3.2. FINDING-SAFE-FC-02: Tối ưu Early-Return và Chuẩn hóa Ngưỡng Latency SLA
- **Trạng thái:** ✅ **ĐÃ KHẮC PHỤC (CLOSED)**
- **Kiểm tra mã nguồn:**
  Tại [`packages/core/src/core/services/safe_nli_adapter.py#L392-L418`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/src/core/services/safe_nli_adapter.py#L392-L418):
  ```python
  # 3. Targeted Neural Inference with early exit on decisive match
  for cand_chunk, cand_passage, _, cand_overlap in top_candidates:
      preds = self._predict_neural_batch([(cand_passage, claim_clean)])
      if not preds:
          continue
      p_contra, p_entail, _ = preds[0]
      if p_contra >= 0.5 and p_contra > p_entail:
          return SafeNliVerdict(
              label="contradicted",
              evidence=self._build_evidence(cand_chunk),
              explanation=self._format_explanation(
                  f"Bằng chứng tại trang {cand_chunk.page_number} trái ngược với khẳng định",
                  f"Độ tin cậy suy luận: {p_contra:.1%}",
              ),
          )
      if p_entail >= self.min_support_threshold:
          return SafeNliVerdict(
              label="supported",
              evidence=self._build_evidence(cand_chunk),
              explanation=self._format_explanation(
                  f"Bằng chứng tại trang {cand_chunk.page_number} xác nhận khẳng định",
                  f"Đoạn đối chiếu trùng khớp {len(cand_overlap)} thuật ngữ trọng tâm",
              ),
          )
  ```
- **Phân tích kỹ thuật:**
  Vì danh sách `top_candidates` đã được sắp xếp giảm dần theo điểm căn chỉnh từ vựng, đoạn trích có khả năng chứng minh cao nhất được đưa vào mạng nơ-ron trước tiên. Khi đoạn trích này cho kết quả khẳng định dứt khoát (`p_entail >= threshold` hoặc `p_contra >= 0.5`), hàm trả về kết quả ngay lập tức (`return SafeNliVerdict(...)`), triệt tiêu việc chạy thêm các lượt ONNX inference lãng phí trên các đoạn trích phía sau.
- **Bằng chứng kiểm thử & Latency:**
  Trong [`test_safe_nli_neural.py#L162-L179`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/tests/domain/test_safe_nli_neural.py#L162-L179), ngưỡng assert được đồng bộ chuẩn hóa theo đúng cam kết PRD §3.2 (`assert mean_latency < 100.0`). Cùng với bước warmup, toàn bộ suite `test_safe_nli_neural.py` đã vượt qua 100% (7/7 tests passed trong 9.84s).

---

## 4. KẾT QUẢ KIỂM THỬ XÁC MINH ĐỘC LẬP VÒNG 2 (EMPIRICAL VERIFICATION EVIDENCE)

### 4.1. Suite 1: Fact Checker Domain Suite
**Lệnh thực thi:**
```bash
uv run pytest packages/core/tests/domain/test_safe_fact_checker.py -v
```
**Stdout ghi nhận:**
```text
============================= test session starts ==============================
packages/core/tests/domain/test_safe_fact_checker.py::test_decompose_claims PASSED [ 10%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_supported_claim PASSED [ 20%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_contradicted_claim PASSED [ 30%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_not_enough_info_claim PASSED [ 40%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_supported PASSED [ 50%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_contradicted_numerical PASSED [ 60%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_contradicted_lexical PASSED [ 70%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_neural_adapter_not_enough_info PASSED [ 80%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_hexagonal_di_mock_port PASSED [ 90%]
packages/core/tests/domain/test_safe_fact_checker.py::test_verify_text_with_adapter_exception_fallback_to_heuristic PASSED [100%]
============================== 10 passed in 7.62s ==============================
```

### 4.2. Suite 2: Neural NLI Model Suite
**Lệnh thực thi:**
```bash
uv run pytest packages/core/tests/domain/test_safe_nli_neural.py -v
```
**Stdout ghi nhận:**
```text
============================= test session starts ==============================
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_initialization PASSED [ 14%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_direct_batch_prediction PASSED [ 28%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_classify_verdicts PASSED [ 42%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_fallback_when_disabled PASSED [ 57%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_model_fallback_on_invalid_path PASSED [ 71%]
packages/core/tests/domain/test_safe_nli_neural.py::test_neural_inference_latency_sla PASSED [ 85%]
packages/core/tests/domain/test_safe_nli_neural.py::test_scifact_sample_evaluation_pipeline PASSED [100%]
============================== 7 passed in 9.84s ===============================
```

### 4.3. Suite 3: Integration Drafts API Lifecycle
**Lệnh thực thi:**
```bash
uv run pytest apps/api/tests/test_drafts_lifecycle.py -v
```
**Stdout ghi nhận:**
```text
============================= test session starts ==============================
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
============================== 11 passed in 9.61s ==============================
```

### 4.4. Kiểm tra Linter & Formatter Chất lượng Mã nguồn
**Lệnh thực thi:**
```bash
uv run ruff check . && uv run ruff format --check .
```
**Stdout ghi nhận:**
```text
All checks passed!
255 files already formatted
```

---

## 5. RÀ SOÁT BẢO MẬT & QUYỀN RIÊNG TƯ (SECURITY & PRIVACY RE-AUDIT)

- **Zero CoT & Prompt Leakage:** Cờ `extra="forbid"` trên `SafeNliVerdict` và `validate_explanation_length` giới hạn $\le 2$ câu bảo đảm không phát sinh bất kỳ rò rỉ nào về prompt hay suy luận nội bộ.
- **An toàn Regex:** Toàn bộ regex trong `SafeFactChecker` và `SafeNliEngineAdapter` đều có cấu trúc đơn giản, tránh hoàn toàn nguy cơ ReDoS.
- **Multi-Tenant Isolation:** Kiểm thử tích hợp xác nhận người dùng chỉ có thể kích hoạt fact-checking trên bản thảo của chính mình hoặc bản thảo được chia sẻ với quyền hợp lệ (`test_collaborator_rbac_and_privacy_isolation`).

---

## 6. KẾT LUẬN & ĐỀ XUẤT CHO CTO

1. Nhiệm vụ **TASK-BE-FACT-CHECKER-NEURAL-INTEGRATION** đã hoàn thành toàn diện, bảo đảm chất lượng cao nhất theo chuẩn PRD §3.2.
2. Cả 2 findings ở Vòng 1 đã được giải quyết dứt điểm. Toàn bộ 28 bài kiểm thử độc lập đều đạt 100% PASS.
3. Reviewer chính thức ban hành phán quyết: **`[VERDICT: PASS]`**.
4. Đề xuất CTO nghiệm thu đóng nhiệm vụ và hợp nhất commit [`83b6505`](file:///home/VeriScholar/Workspace/VeriScholar) vào nhánh tích hợp chung của Module 2.
