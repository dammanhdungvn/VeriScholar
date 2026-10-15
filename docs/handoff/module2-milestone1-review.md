# BÁO CÁO ĐÁNH GIÁ & NGHIỆM THU ĐỘC LẬP: MILESTONE 1 MODULE 2
**Lead Quality Reviewer Evaluation & Audit Report**  
**Dự án:** VeriScholar | **Tiêu chuẩn:** PRD §3.2 & Chỉ đạo Kỹ thuật Điều phối viên  
**Snapshot Commit Cơ Sở (origin/main):** [`fca342cd3f34129560d101b89a95d764561f264b`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar)  
**Mã Nguồn Kiểm Tra Thực Tế:** Dirty working tree snapshot trên nền `fca342c` (chứa toàn bộ mã nguồn Module 2 đang phát triển dang dở, sau đó được gom nguyên trạng vào commit [`6156c91eef3550b07b3beba43fa0f4fe617da9fe`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar))  
**Trạng Thái Đối Chiếu Sau Đóng Gói:** **`PENDING`** (cần xác minh độc lập lại trên máy chủ VPS mới)  
**Mã Task:** `task_d04b33625636` | **Dispatch Context:** `ctx_bbf803c0c9d1`  
**Terminal Reviewer:** `term_c3228535-a7c3-4ab2-8434-4e8052aa5f56` | **Coordinator:** `term_ecd5fad9-728e-49fa-9be9-63f9af44a20a`  
**Ngày kiểm định:** 15/10/2026  

---

## 1. TỔNG QUAN PHÂN HẠNG TRẠNG THÁI (GATE 1 STATUS MATRIX)

Hệ thống đánh giá độc lập phân tách minh bạch giữa **Logic kiến trúc (Mock/Heuristic)** và **Thực thi hạ tầng/mô hình thực tế (Real/Infrastructure)**. Không suy diễn trạng thái PASS của toàn hệ thống chỉ từ kết quả unit test mock.

| STT | Tiêu chí kiểm định (PRD §3.2 & Chỉ đạo) | Module thực thi | Phương thức kiểm tra | Trạng thái (Status) |
| :---: | :--- | :--- | :--- | :---: |
| **1.1** | **Sandbox Capability Probe (Fail-Closed):** Phát hiện thiếu container privileges, chặn âm thầm fallback sang host, sanitize env, nâng `SandboxInfrastructureUnavailableError` | `core.services.sandbox_probe`<br>`core.services.latex_compiler` | Thực thi probe trực tiếp trên máy chủ Linux host | **PASS** |
| **1.2** | **Containerized LaTeX Compilation & SLA:** Khởi tạo container cách ly an toàn, biên dịch pdflatex/xelatex không đặc quyền trong $\le 2s$ | `core.services.latex_compiler` | Hạ tầng Docker/User namespace thực tế | **BLOCKED**<br>*(SLA: `NOT_MEASURED`)* |
| **2.1** | **SAFE NLI Contract Compliance:** Chuẩn Option A 3 nhãn (`supported`, `contradicted`, `not_enough_info`), `premise=evidence`, `hypothesis=claim`, giải thích $\le 2$ câu, cấm CoT | `core.services.safe_nli_adapter` | Unit tests kiểm chứng hợp đồng I/O & regex | **PASS** |
| **2.2** | **SAFE NLI Real Neural Inference & Accuracy:** Tải trọng số DeBERTa-v3 thực tế, suy diễn NLI trên PyTorch/ONNX, đo lường F1/Accuracy và Latency SLA | `core.services.safe_nli_adapter` | Nạp weights thực từ HuggingFace/Local Cache | **PENDING**<br>*(SLA/Acc: `NOT_MEASURED`)* |
| **3.1** | **Non-destructive AI Staging:** Streaming/Assist đưa vào `PendingSuggestion` modal, không ghi đè trực tiếp buffer biên tập | `apps/web/src/features/writing/components/SuggestionReviewPanel.tsx` | Vitest Component & Workspace Integration | **PASS** |
| **3.2** | **OCC & Local Unpersisted Edits:** Bảo vệ ghi đè server bằng ETag (`If-Match: "v{version}"`), xử lý trôi lệch offset khi người dùng tiếp tục gõ chưa autosave | `apps/web/src/features/writing/components/WritingWorkspace.tsx` | Phân tích mã nguồn, kiểm thử kịch bản trôi offset | **FAIL / DEFECT** |
| **4.1** | **Toàn vẹn Bộ kiểm thử Đơn vị & Tích hợp:** Chạy trọn vẹn test suite core domain & frontend writing | `packages/core/tests/domain/`<br>`apps/web/src/features/writing/` | `pytest` (21 tests) & `vitest` (74 tests) | **PASS** |
| **4.2** | **Biên dịch Frontend TypeScript:** Kiểm tra chặt chẽ typecheck toàn bộ workspace web | `apps/web` | `pnpm --prefix apps/web exec tsc -b` | **PASS** |

> [!WARNING]
> **Kết luận Gate 1:** **`CHƯA CÔNG BỐ GATE 1 PASS HOÀN TOÀN`**. Các phân hệ kiến trúc nền tảng và UI staging đạt tiêu chuẩn xuất sắc (**PASS**), nhưng xuất hiện 1 khiếm khuyết xử lý đồng thời tại client (**DEFECT OCC Local Edits**), hạ tầng container bị chặn bởi quyền host (**BLOCKED**), và mô hình suy diễn NLI thực tế cần đóng gói weights trước khi nghiệm thu chất lượng (**PENDING**).

---

## 2. PHÂN TÍCH CHUYÊN SÂU THEO 5 CHỈ ĐẠO CỦA ĐIỀU PHỐI VIÊN

### 2.1. Yêu cầu 1: Phân tích Lỗi OCC & Local Unpersisted Edits

#### Bản chất kỹ thuật & Sự khác biệt giữa Server ETag và Local Dirty State:
- **Nguyên lý của HTTP `If-Match: "v{version}"`:** Header `If-Match` chỉ kiểm tra phiên bản dữ liệu lưu trữ tại cơ sở dữ liệu backend (`draft.version`). Nếu server draft chưa bị ai lưu đè, server vẫn giữ nguyên phiên bản (ví dụ `version: 1`).
- **Sự nhầm lẫn trước đây:** Nhận định *"người dùng gõ thêm trong lúc xem xét đề xuất sẽ gặp lỗi HTTP 412"* là **KHÔNG ĐÚNG VỚI THỰC TẾ**.
  - Việc người dùng gõ thêm trên trình duyệt chỉ làm thay đổi biến `editorContent` trong Zustand store (client memory) và đánh dấu `isDirty: true`.
  - Nếu tính năng autosave chưa kịp kích hoạt hoặc đang chờ debounce, `draft.version` trên server **vẫn là 1**.
  - Khi người dùng bấm **"Chấp nhận & Chèn"** cho một đề xuất đã được sinh ra trước đó, client gửi request `updateDraft` kèm `If-Match: "v1"`. Server so sánh thấy phiên bản khớp hoàn toàn và trả về **HTTP 200 OK**!
  
#### Lỗ hổng Trôi lệch Vùng chọn (Offset Drift) & Mất mát Dữ liệu cục bộ:
Trong [`WritingWorkspace.tsx`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/web/src/features/writing/components/WritingWorkspace.tsx#L212-L248):
```typescript
const handleAcceptSuggestion = useCallback(
  async (suggestion: PendingSuggestion) => {
    if (!activeDraftId || !draft) return;
    try {
      setSaving(true);
      const currentContent = useWritingStore.getState().editorContent;
      const currentRange = useWritingStore.getState().selectionRange;

      // Determine insertion position based on current cursor/selection
      let insertStart = suggestion.cursor_start;
      let insertEnd = suggestion.cursor_end;
      if (currentRange && currentRange.start !== undefined) {
        insertStart = currentRange.start;
        insertEnd = currentRange.end;
      }

      const safeStart = Math.min(Math.max(0, insertStart), currentContent.length);
      const safeEnd = Math.min(Math.max(safeStart, insertEnd), currentContent.length);

      const newContent =
        currentContent.slice(0, safeStart) +
        suggestion.suggested_text +
        currentContent.slice(safeEnd);

      const updated = await draftsApi.updateDraft(
        activeDraftId,
        {
          title: editorTitle,
          content: newContent,
          format: draft.format,
          version: draft.version,
        },
        `v${draft.version}`
      );
      markSaved(updated);
      closeSuggestionPanel();
    } finally {
      setSaving(false);
    }
  },
  [activeDraftId, draft, editorTitle, markSaved, closeSuggestionPanel, setSaving]
);
```

#### Ma trận Hành vi Kịch bản Kiểm thử Thực tế:
1. **Kịch bản A (Người dùng gõ trước vị trí đề xuất khi panel đang mở):**
   - Đề xuất được sinh tại vị trí ký tự $[100, 150]$.
   - Người dùng gõ thêm 20 ký tự ở đầu văn bản (tại vị trí $0$). Lúc này `editorContent` bị dời đi 20 ký tự.
   - Nếu `currentRange` bị mất focus hoặc bằng null, hàm sử dụng fallback `insertStart = 100`.
   - Chuỗi đề xuất sẽ bị chèn cắt ngang vị trí $[100, 150]$ cũ, làm **hỏng 20 ký tự** của nội dung ban đầu (sai lệch vị trí ngữ nghĩa nghiêm trọng).
   - Server vẫn trả về **HTTP 200** vì ETag server vẫn là `v1`.
2. **Kịch bản B (Autosave chạy ngầm trong khi đang xem đề xuất):**
   - Nếu autosave kích hoạt ngầm thành công, server nhảy lên `v2`.
   - Lúc này người dùng bấm Chấp nhận với đề xuất cũ mang `expected_version: 1`, header gửi `If-Match: "v1"` $\rightarrow$ Server trả về **HTTP 412 Precondition Failed**.
   - Khối `catch` hiện tại chỉ ghi log console `console.error("Accept suggestion failed:", err)` mà **không có cơ chế rebase nội dung**, khiến thao tác chấp nhận bị treo vô hiệu.
3. **Kịch bản C (Chấp nhận lặp lại - Double Click):**
   - Người dùng bấm đúp nhanh vào nút "Chấp nhận". Cờ `isSaving` chặn ở cấp component, nhưng nếu không có optimistic locking tại UI store, có thể phát sinh 2 lời gọi đồng thời.

---

### 2.2. Yêu cầu 2: Bóc tách NLI Test Adapter (Mock/Stub vs Real Inference)

#### Phân định Bản chất Test Suite:
Khi rà soát mã nguồn [`packages/core/src/core/services/safe_nli_adapter.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/packages/core/src/core/services/safe_nli_adapter.py) và bộ test [`test_safe_nli_adapter.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/packages/core/tests/domain/test_safe_nli_adapter.py):

1. **Thực tế mã nguồn trong `SafeNliEngineAdapter`:**
   - Thuộc tính `model_name` mặc định là `"cross-encoder/nli-deberta-v3-small"` và fallback `"MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"`.
   - Tuy nhiên, phương thức `classify()` hiện tại hoàn toàn là **Bộ luật suy nghiệm (Heuristic Rule-Engine)** viết bằng Python:
     - Dùng regex tách token và tính điểm giao thoa `alignment_score = (0.75 * recall) + (0.25 * precision)`.
     - Dùng regex phát hiện mâu thuẫn số học (`claim_numbers` vs `chunk_numbers`).
     - Dùng danh sách từ vựng mâu thuẫn đối nghịch (`CONTRADICTION_PAIRS`: `"outperform"` vs `"underperform"`, `"increase"` vs `"decrease"`).
2. **Thực tế trong `test_safe_nli_adapter.py`:**
   - Cả 8 test cases đều là **In-Memory Heuristic / Mock Tests**.
   - **HOÀN TOÀN KHÔNG CÓ** bước nạp mô hình mạng nơ-ron thực tế, không gọi `transformers.AutoModelForSequenceClassification`, không dùng ONNX runtime, không có tokenizer `DeBERTa-v3`.
3. **Smoke Test Thực tế & Rào cản Blocker:**
   - Khi chạy thử nghiệm nạp mô hình thực trong môi trường offline:
     ```python
     from transformers import AutoModelForSequenceClassification, AutoTokenizer
     tokenizer = AutoTokenizer.from_pretrained("cross-encoder/nli-deberta-v3-small")
     model = AutoModelForSequenceClassification.from_pretrained("cross-encoder/nli-deberta-v3-small")
     ```
   - **Lỗi phát sinh (Blocker / DEFECT-02):** Máy chủ đang chạy không có kết nối internet để tải checkpoint từ HuggingFace Hub, và thư mục cache cục bộ chưa đóng gói sẵn trọng số (`weights/`).
   - **Quy tắc phân loại:** Mặc dù adapter đã tuân thủ chuẩn giao diện Option A (`supported`, `contradicted`, `not_enough_info`), việc **suy diễn thực tế bằng mô hình nơ-ron qua ONNX offline hoàn toàn chưa được kiểm chứng** do chưa tải weights. Toàn bộ tiêu chí chất lượng NLI (độ chính xác nhận diện suy luận logic, F1-score, độ trễ suy diễn) thuộc Gate 1 phải ghi nhận trạng thái **`PENDING / DEFECT-02 OPEN`** và SLA/Accuracy ghi nhận **`NOT_MEASURED`**. Tuyệt đối không được phép suy diễn "NLI đạt chuẩn PRD" chỉ vì 8 bài test luật suy nghiệm pass.

---

### 2.3. Yêu cầu 3: Phạm vi Phân định Giữa VERIFIED, BLOCKED và NOT_MEASURED

Để đảm bảo tính khách quan của kỹ sư Lead Quality Reviewer, các phân hệ được phân loại rạch ròi:

1. **Cơ chế An toàn Fail-Closed (VERIFIED / PASS):**
   - Đã kiểm chứng trực tiếp: Khi môi trường thiếu quyền namespace hoặc socket Docker, `SandboxRuntimeCapabilityProbe` xác định `BLOCKED_INFRASTRUCTURE` và `SandboxedLatexCompiler` lập tức nâng ngoại lệ `SandboxInfrastructureUnavailableError`. Hệ thống kiên quyết không tự ý hạ cấp thực thi thô trên máy host.
2. **Biên dịch Container Thực tế & SLA (BLOCKED / NOT_MEASURED):**
   - Trạng thái: **`BLOCKED`**. Nguyên nhân: Máy chủ host kích hoạt chính sách bảo mật hạt nhân `apparmor_restrict_unprivileged_userns=1` và không cấp quyền socket `/var/run/docker.sock`.
   - SLA biên dịch: **`NOT_MEASURED`** (do không thể tạo container cô lập trên môi trường này).
3. **Chất lượng Mô hình NLI Thực tế (PENDING / NOT_MEASURED):**
   - Trạng thái: **`PENDING`** (chờ đóng gói weights ONNX/PyTorch vào repository/artifact storage).
   - Accuracy & Inference Latency SLA: **`NOT_MEASURED`**.
4. **Hiển thị Bounding Box & PDF Preview:**
   - Mã nguồn component [`WritingPreviewPane.tsx`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/web/src/features/writing/components/WritingPreviewPane.tsx) và [`SourceEvidenceModal.tsx`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/web/src/features/writing/components/SourceEvidenceModal.tsx) tuân thủ đúng tọa độ chuẩn hóa Top-Left `[0.0, 1.0]` và trang 1-indexed. Đã kiểm thử qua Vitest với Mock Blob URL.

---

### 2.4. Yêu cầu 4: Bối Cảnh Snapshot Commit & Đối Chiếu Mã Nguồn Đóng Gói

- **Commit Cơ sở tại thời điểm thẩm định:** [`fca342cd3f34129560d101b89a95d764561f264b`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar) (`[core/api/docs] feat: implement 3-tier AI Guardrails safety system and design documentation (#42)`).
- **Đối tượng kiểm định thực tế:** Reviewer `gg16` thực hiện kiểm định độc lập trên **dirty working tree snapshot** (các thay đổi chưa commit của Backend và Frontend trên nền `fca342c`).
- **Mã nguồn đóng gói (Packaged Commit):** Sau khi quá trình kiểm định độc lập hoàn tất và phát hiện các defect, Điều phối viên đã gom và đóng gói nguyên vẹn toàn bộ 155 tệp mã nguồn Module 2 này vào commit [`6156c91eef3550b07b3beba43fa0f4fe617da9fe`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar) (`[core/api/web] feat(m2-wip): implement Module 2 writing assistant, sandbox probe, safe NLI adapter, and assets`).
- **Trạng thái đối chiếu sau đóng gói:** Vì Reviewer thực hiện đánh giá trước thời điểm commit `6156c91` được tạo ra, phạm vi mã nguồn được kiểm tra trùng khớp với nội dung commit `6156c91`, nhưng việc đối chiếu chéo sau đóng gói được ghi nhận là **`PENDING`** và bắt buộc phải được chạy xác minh lại trên máy chủ VPS mới. Tuyệt đối không tự ý gán nhãn PASS cho commit `6156c91` trước khi hoàn tất kiểm thử hồi quy trên VPS.

---

## 3. DANH SÁCH LỖI VÀ TỒN ĐỌNG KỸ THUẬT (DEFECT LIST - DUY TRÌ MỞ)

### DEFECT-01: Lỗ hổng Trôi lệch Vùng chọn khi Chấp nhận Đề xuất (OCC Local Drift) — TRẠNG THÁI: OPEN
- **Mức độ nghiêm trọng:** `HIGH`
- **Vị trí:** [`apps/web/src/features/writing/components/WritingWorkspace.tsx`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/web/src/features/writing/components/WritingWorkspace.tsx#L212-L257)
- **Mô tả:** Header `If-Match: "v{version}"` chỉ chặn được xung đột khi phiên bản server đã tăng. Nếu người dùng gõ thêm ký tự cục bộ (`isDirty: true`) mà chưa lưu lên server, server vẫn chấp nhận phiên bản cũ với HTTP 200 OK. Đoạn code chèn chuỗi đề xuất dựa vào `cursor_start` cũ sẽ cắt đè hoặc chèn lệch vào phần nội dung người dùng vừa gõ mới.
- **Biện pháp khắc phục kiến nghị:**
  1. Kiểm tra trạng thái `isDirty`: Nếu có thay đổi cục bộ chưa lưu, yêu cầu thực hiện rebase offset trước khi chèn, hoặc kích hoạt lưu tự động đồng bộ trước khi mở panel đề xuất.
  2. Bắt lỗi HTTP 412: Hiển thị thông báo xung đột phiên bản và cho phép người dùng xem diff 3 bên (3-way merge) thay vì nuốt lỗi trong `console.error`.

### DEFECT-02: Thiếu Trọng số Mô hình NLI Thực tế & Inference Ngoại Tuyến Chưa Kiểm Chứng — TRẠNG THÁI: OPEN
- **Mức độ nghiêm trọng:** `MEDIUM`
- **Vị trí:** [`packages/core/src/core/services/safe_nli_adapter.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/packages/core/src/core/services/safe_nli_adapter.py)
- **Mô tả:** Lớp `SafeNliEngineAdapter` đã hoàn thành tầng hợp đồng Option A (3 nhãn `supported`, `contradicted`, `not_enough_info`, `premise=evidence`, `hypothesis=claim`) và bộ luật suy nghiệm heuristic regex. Tuy nhiên, việc **suy diễn thực tế bằng mô hình nơ-ron ngoại tuyến qua ONNX hoàn toàn chưa được kiểm chứng** do máy chủ chưa tải và đóng gói trọng số (`weights/`). Toàn bộ SLA và Accuracy/F1 thực tế là `NOT_MEASURED`.
- **Biện pháp khắc phục kiến nghị:**
  1. Tải và đóng gói mô hình `nli-deberta-v3-small` dưới dạng mô hình ONNX lượng tử hóa (quantized ONNX model) trong thư mục `models/nli/` trên VPS.
  2. Cung cấp 1 test suite suy diễn khói (smoke test) với trọng số thực tế khi chạy ở môi trường đầy đủ tài nguyên trên VPS.

### DEFECT-03: Rào cản Hạ tầng Thực thi Sandbox Cục bộ — TRẠNG THÁI: BLOCKED (Hạ tầng)
- **Mức độ nghiêm trọng:** `LOW` (Thiết kế đã Fail-Closed an toàn, nhưng chặn tính năng biên dịch cách ly)
- **Vị trí:** Hệ điều hành máy chủ host / [`core.services.sandbox_probe`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/packages/core/src/core/services/sandbox_probe.py)
- **Mô tả:** Nhân Linux của môi trường kích hoạt `apparmor_restrict_unprivileged_userns=1` và không có quyền truy cập `/var/run/docker.sock`, khiến việc khởi tạo container biên dịch LaTeX an toàn bị chặn.

---

## 4. BẰNG CHỨNG THỰC NGHIỆM CHI TIẾT (EMPIRICAL RUN LOGS)

### 4.1. Thực nghiệm Sandbox Capability Probe
**Lệnh thực thi:**
```bash
uv run python -c "from core.services.sandbox_probe import SandboxRuntimeCapabilityProbe; p = SandboxRuntimeCapabilityProbe(); print(p.probe())"
```
**Stdout thu được:**
```text
ProbeResult(status='BLOCKED_INFRASTRUCTURE', is_fully_hardened=False, blocked_reasons=['AppArmor restricts unprivileged user namespaces (/proc/sys/kernel/apparmor_restrict_unprivileged_userns=1)', 'Docker daemon socket unavailable or inaccessible (/var/run/docker.sock)', 'cgroups v2 resource controllers (memory/cpu) unconfirmed or unmounted', 'Network isolation unconfirmed; unconfined network egress possible', 'Read-only root filesystem enforcement not detected'])
```

### 4.2. Bộ kiểm thử SAFE NLI Adapter (Mock / Contract)
**Lệnh thực thi:**
```bash
uv run pytest packages/core/tests/domain/test_safe_nli_adapter.py -v
```
**Stdout thu được:**
```text
============================= test session starts ==============================
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_supported PASSED [ 12%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_contradicted_numerical PASSED [ 25%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_contradicted_lexical PASSED [ 37%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_verdict_not_enough_info PASSED [ 50%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_option_a_contract_forbids_chain_of_thought PASSED [ 62%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_option_a_contract_truncates_long_explanation PASSED [ 75%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_nli_pair_ordering_and_model_selection PASSED [ 87%]
packages/core/tests/domain/test_safe_nli_adapter.py::test_evidence_without_coordinates_preserves_none_without_fabrication PASSED [100%]
============================== 8 passed in 0.37s ===============================
```

### 4.3. Bộ kiểm thử LaTeX Pipeline & Fail-Closed Guard
**Lệnh thực thi:**
```bash
uv run pytest packages/core/tests/domain/test_latex_pipeline.py -v
```
**Stdout thu được:**
```text
============================= test session starts ==============================
packages/core/tests/domain/test_latex_pipeline.py::test_fast_ast_linter_clean_code PASSED [  7%]
packages/core/tests/domain/test_latex_pipeline.py::test_fast_ast_linter_unclosed_environment PASSED [ 15%]
packages/core/tests/domain/test_latex_pipeline.py::test_fast_ast_linter_mismatched_environment PASSED [ 23%]
packages/core/tests/domain/test_latex_pipeline.py::test_fast_ast_linter_unclosed_brace PASSED [ 30%]
packages/core/tests/domain/test_latex_pipeline.py::test_fast_ast_linter_unescaped_underscore PASSED [ 38%]
packages/core/tests/domain/test_latex_pipeline.py::test_sandboxed_compiler_success PASSED [ 46%]
packages/core/tests/domain/test_agentic_latex_healer_auto_repair PASSED [ 53%]
packages/core/tests/domain/test_agentic_latex_healer_graceful_fallback PASSED [ 61%]
packages/core/tests/domain/test_sandboxed_compiler_pymupdf_fallback_returns_failure PASSED [ 69%]
packages/core/tests/domain/test_sandboxed_compiler_hardened_probe_mock PASSED [ 76%]
packages/core/tests/domain/test_sandboxed_compiler_require_hardened_raises_on_blocked_infra PASSED [ 84%]
packages/core/tests/domain/test_sandbox_capability_probe_host_detection PASSED [ 92%]
packages/core/tests/domain/test_sandbox_probe_env_sanitization PASSED [100%]
============================= 13 passed in 1.85s ===============================
```

### 4.4. Bộ kiểm thử Frontend Writing Feature Suites
**Lệnh thực thi:**
```bash
pnpm --prefix apps/web test src/features/writing
```
**Stdout thu được:**
```text
Test Files  12 passed (12)
Tests       74 passed (74)
Duration    4.98s
(Bao gồm: SuggestionReviewPanel: 8/8 passed, WritingWorkspace: 8/8 passed, SourceEvidenceModal: 6/6 passed, WritingPreviewPane: 3/3 passed, DraftAssetManagementModal: 8/8 passed, DraftSharingModal: 4/4 passed).
```

### 4.5. Kiểm tra Biên dịch Frontend TypeScript
**Lệnh thực thi:**
```bash
pnpm --prefix apps/web exec tsc -b
```
**Stdout thu được:**
```text
(Exit code: 0 - Found 0 errors)
```

---

## 5. KẾT LUẬN & ĐỀ XUẤT CHO ĐIỀU PHỐI VIÊN

1. **Về Gate 1 Acceptance:**  
   Không phê duyệt PASS vô điều kiện cho Gate 1. Đề xuất chuyển trạng thái Gate 1 thành **`CONDITIONAL ACCEPTANCE / PENDING REMEDIATION`**:
   - Chấp thuận hoàn thành phần kiến trúc giao diện, non-destructive staging và fail-closed security probe.
   - Yêu cầu vá **Defect 1 (OCC Local Drift)** trước khi đưa vào sản xuất để tránh nguy cơ mất mát dữ liệu của người dùng.
   - Yêu cầu lên kế hoạch đóng gói mô hình nơ-ron thực tế cho **Defect 2 (NLI Real Weights)**.
2. **Về Tiến trình Song song Milestone 2:**  
   Các phân hệ soạn thảo mở rộng (Assets, Sharing) có thể tiếp tục hoàn thiện trên nền tảng đã qua kiểm tra TypeScript và Vitest sạch sẽ.

---

## 6. RÀ SOÁT BẢO MẬT & XÁC MINH CÁC TỆP BỊ IGNORE

- **Kết quả rà soát Secrets:** Không phát hiện secrets trong phạm vi và bộ quy tắc đã quét (đã thực hiện quét regex đối với API keys, JWT secrets, private keys, certificates và tokens nhạy cảm trên toàn bộ git diff `fca342c..HEAD` và các file tài liệu). Không khẳng định an toàn tuyệt đối 100% ngoài phạm vi và bộ quy tắc đã quét.
- **Xác minh các tệp nhạy cảm và ignore không bị Git track đồng thời:**
  - Tệp cấu hình môi trường `.env`, `.env.*` (ngoại trừ `.env.example` đã khử toàn bộ giá trị bí mật): **Không bị Git track**.
  - Cơ sở dữ liệu SQLite/PostgreSQL `storage/verischolar.db`, `*.db`, `*.sqlite`, `*.sqlite3`: **Không bị Git track** (được bỏ qua bởi `.gitignore`).
  - Gói dữ liệu chuyển giao ngoài Git `verischolar_runtime_data.tar.gz` và `verischolar_runtime_data.tar.gz.sha256`: **Không bị Git track** (được bỏ qua bởi `.gitignore`).
  - Thư mục runtime agent `.agents/runtime/`: **Không bị Git track** (được bỏ qua bởi `.gitignore`).
  - Toàn bộ 29 kỹ năng (`.agents/skills/`) và tài liệu phân công (`.agents/teamwork/`): **Được Git track đầy đủ** theo đúng chỉ đạo.
  - Các tệp nhật ký `*.log`: **Không bị Git track**.
