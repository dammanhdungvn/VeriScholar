# Prompt Khởi Động Cho AI Assistant Tiếp Quản Trên VPS
## VPS Bootstrapping & Successor Prompt

> **Hướng dẫn:** Sao chép toàn bộ khối văn bản bên dưới và dán vào lượt trao đổi đầu tiên của AI Assistant trên máy chủ VPS mới để kích hoạt quy trình tiếp quản dự án tức thì.

---

```markdown
Chào bạn, bạn là Antigravity / AI Coding Assistant tiếp quản dự án **VeriScholar** trên môi trường máy chủ VPS mới.

Dự án vừa được chuyển giao từ máy phát triển cục bộ sang VPS này. Không khảo sát lại từ đầu, không lập lại kế hoạch, và không coi các Run/Terminal IDs cũ là các binding sống.

Hãy thực hiện tuần tự các bước tiếp quản sau:

### BƯỚC 1: ĐỌC TÀI LIỆU HỒ SƠ BÀN GIAO & PRD
1. Đọc tệp PRD tổng thể: `docs/vi/PRD.md`.
2. Đọc tệp hướng dẫn bàn giao chính: `docs/handoff/README.md`.
3. Đọc hướng dẫn môi trường: `docs/handoff/vps-environment-replication-guide.md`.
4. Đọc kế hoạch khắc phục Module 2: `docs/handoff/module2-remediation-backlog-and-plan.md`.
5. Đọc báo cáo review độc lập của Reviewer: `docs/handoff/module2-milestone1-review.md`.

### BƯỚC 2: XÁC MINH REPOSITORY & BASELINE TESTS
1. Xác minh Git HEAD commit: `git log -1 --oneline` (so khớp với commit bàn giao trong `docs/handoff/README.md`).
2. Xác minh môi trường Python: `uv sync --all-packages` và chạy baseline tests:
   `uv run pytest -q` (kỳ vọng: 570 passed, 9 skipped).
   `uv run ruff check .` và `uv run ruff format --check .` (kỳ vọng: sạch 0 lỗi).
3. Xác minh môi trường Frontend: `pnpm --prefix apps/web install` và chạy:
   `pnpm --prefix apps/web exec tsc -b` (kỳ vọng: 0 errors).
   `pnpm --prefix apps/web test src/features/writing` (kỳ vọng: 74/74 passed).

### BƯỚC 3: TIẾP TỤC CÔNG VIỆC DANG DỞ (KHÔNG MỞ RỘNG PHẠM VI)
1. **Ưu tiên số 1 - Sửa DEFECT-01 (OCC Local Offset Drift):**
   - Vị trí: `apps/web/src/features/writing/components/WritingWorkspace.tsx`.
   - Vấn đề: Khi người dùng gõ thêm ký tự trong lúc xem xét đề xuất AI mà chưa autosave, việc Accept đề xuất cũ làm trôi lệch offset ký tự (cắt đè văn bản mới gõ dù ETag server trả về HTTP 200).
   - Khắc phục: Xử lý rebase offset dựa trên `isDirty` / delta độ dài, và bắt lỗi HTTP 412 hiển thị giao diện giải quyết xung đột trực quan.
2. **Ưu tiên số 2 - Đóng gói weights cho DEFECT-02 (SAFE NLI Offline Weights):**
   - Vị trí: `packages/core/src/core/services/safe_nli_adapter.py`.
   - Tải và đóng gói mô hình `cross-encoder/nli-deberta-v3-small` ONNX INT8 vào `models/nli/` để phục vụ suy diễn logic 3 nhãn ngoại tuyến.
3. **Ưu tiên số 3 - Hoàn thiện Module 2 Milestone 2:**
   - Tiếp tục hoàn thiện kiểm thử cho Asset Management Safe Extraction và Sharing RBAC.
4. **Quy tắc bất biến:**
   - TUYỆT ĐỐI CHƯA bắt đầu Module 3.
   - Giữ nguyên cơ chế bảo vệ Fail-Closed của Sandbox Compiler: nếu VPS chưa có container privileges, probe phải nâng `SandboxInfrastructureUnavailableError` và trả về `BLOCKED_INFRASTRUCTURE`. Không tự ý chạy host subprocess.
   - Báo cáo ngắn gọn cho User kèm bằng chứng lệnh chạy thực tế.
```
