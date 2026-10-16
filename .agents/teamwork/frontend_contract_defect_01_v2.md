# TASK CONTRACT: TASK-FE-FIX-DEFECT-01-V2
## Khắc Phục Triệt Để 4 Findings Của Reviewer Về DEFECT-01

> **Contract Version:** 2.0  
> **Task ID:** `TASK-FE-FIX-DEFECT-01-V2`  
> **Assignee:** Senior Frontend Engineer (`frontend` @ pane `w2:p4`)  
> **Reviewer:** Lead Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
> **Tài liệu thẩm định gốc:** [`docs/handoff/defect-01-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/defect-01-review.md)  
> **Repository:** `/home/VeriScholar/Workspace/VeriScholar`  
> **Nhánh công tác:** `feat/vps-module2-remediation`

---

### 1. Mục Tiêu
Khắc phục 4 findings nghiêm trọng được phát hiện bởi Independent Reviewer trong báo cáo `docs/handoff/defect-01-review.md`:
1. **FINDING-DEFECT-01-01 (HIGH - Data Loss):** Khi gặp HTTP 412, `setDraft(freshDraft)` ghi đè xóa sạch `editorContent` người dùng đang gõ chưa lưu.
2. **FINDING-DEFECT-01-02 (HIGH - Text Corruption):** Bỏ qua cờ `hasConflict` từ `calculateRebasedRange`, tiếp tục cắt xén làm nuốt mất các ký tự xung quanh khi văn bản gốc bị xóa/sửa.
3. **FINDING-DEFECT-01-03 (MEDIUM):** Không có ngưỡng khoảng cách (`proximity threshold`) trong `diffUtils.ts`, khiến từ khóa ngắn nhảy sang vị trí xa xôi ngẫu nhiên.
4. **FINDING-DEFECT-01-04 (LOW):** Test case HTTP 412 trong `WritingWorkspace.test.tsx` thiếu assertion kiểm tra `editorContent` được bảo toàn.

---

### 2. Yêu Cầu Kỹ Thuật Chi Tiết

#### 2.1. Sửa `WritingWorkspace.tsx`
- **Khối catch HTTP 412 (FINDING-DEFECT-01-01):**
  Không gọi `setDraft(freshDraft)` vì nó đặt lại `editorContent = freshDraft.content` và `isDirty = false`.
  Thay vào đó: Chỉ cập nhật `draft` metadata (để cập nhật version mới nhất từ server) mà giữ nguyên vẹn `editorContent` và cờ `isDirty` hiện tại của người dùng:
  ```typescript
  if (isPreconditionFailed) {
    try {
      const freshDraft = await draftsApi.getDraft(activeDraftId);
      useWritingStore.setState({ draft: freshDraft });
    } catch {
      // Keep draft state if fetch fails
    }
    setConflictMessage(
      "Bản thảo trên máy chủ đã thay đổi phiên bản (HTTP 412). Phiên bản cơ sở đã được cập nhật, vui lòng xác nhận áp dụng lại đề xuất."
    );
  }
  ```
- **Xử lý cờ `hasConflict` (FINDING-DEFECT-01-02):**
  Bóc tách `hasConflict` từ kết quả `calculateRebasedRange`:
  ```typescript
  const { start: rebasedStart, end: rebasedEnd, hasConflict } = calculateRebasedRange(
    baseContent,
    currentContent,
    suggestion.cursor_start,
    suggestion.cursor_end,
    suggestion.original_text
  );

  if (hasConflict) {
    setConflictMessage(
      "Văn bản gốc của đề xuất đã bị thay đổi hoặc không còn khớp trên trình soạn thảo. Vui lòng kiểm tra lại trước khi áp dụng."
    );
    return;
  }
  ```

#### 2.2. Sửa `diffUtils.ts` (FINDING-DEFECT-01-03)
- Trong Bước 4 của `calculateRebasedRange`: Khi tìm kiếm `allOccurrences` cho `targetText`:
  Nếu khoảng cách `minDiff > 120` ký tự so với `shiftedStart`, hoặc nếu `targetText.length <= 4` mà khoảng cách `minDiff > 40`, coi là không tìm thấy vị trí tương đồng an toàn $\rightarrow$ trả về `hasConflict: true`.

#### 2.3. Bổ Sung Kiểm Thử trong `WritingWorkspace.test.tsx` & `diffUtils.test.ts` (FINDING-DEFECT-01-04)
- Viết test case: Khi gặp HTTP 412, assert rằng `useWritingStore.getState().editorContent` giữ nguyên chuỗi người dùng đã gõ dở cục bộ.
- Viết test case: Khi `original_text` bị xóa trong editor, bấm Accept thì hiển thị conflict banner và dừng chèn, không cắt chuỗi làm hỏng văn bản.
- Viết test case cho `diffUtils.test.ts` kiểm tra proximity threshold cho từ khóa ngắn.

---

### 3. Tiêu Chí Nghiệm Thu Tự Động (Quality Gates)
Trước khi báo cáo hoàn thành:
1. `pnpm --prefix apps/web test src/features/writing/components/WritingWorkspace.test.tsx src/features/writing/lib/diffUtils.test.ts` $\rightarrow$ 100% PASS.
2. `pnpm --prefix apps/web test src/features/writing` $\rightarrow$ 100% PASS (zero regressions).
3. `pnpm --prefix apps/web exec tsc -b` $\rightarrow$ 0 errors.
4. `pnpm --prefix apps/web lint` $\rightarrow$ 0 errors, 0 warnings.
