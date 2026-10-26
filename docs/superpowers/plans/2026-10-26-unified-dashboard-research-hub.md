# Unified Dashboard Research Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa Trạm Nghiên Cứu Hợp Nhất tại `/dashboard` (chuẩn Claude / Perplexity): giao diện căn giữa hoàn hảo không khoảng trống thừa, tích hợp thanh nhập liệu đa năng với bộ tinh chỉnh suy luận 5.6 Luna, 2 lối vào song song (Tải PDF + Thẻ gợi ý chủ đề) và kết quả tìm kiếm học thuật hiển thị tức thì tại chỗ.

**Architecture:** Tạo component `UnifiedHeroWorkspace` tích hợp `DashboardChatInputBox` (Reasoning Effort 5.6 Luna), bộ chọn chế độ (`[🔍 Tìm bài báo]` / `[💬 Đối thoại AI]`), vùng nạp PDF nhẹ nhàng, 4 chip gợi ý chủ đề nghiên cứu tiêu biểu, và danh sách thẻ bài báo `ScholarlyResultCard` hiển thị tại chỗ kết nối trực tiếp với `discoveryApi`. Thay thế màn hình chờ đơn điệu trong `DashboardContainer.tsx`.

**Tech Stack:** React 19, TypeScript, Tailwind CSS, Lucide Icons, Zustand v5.

**Spec:** [Unified Dashboard Research Hub Design Spec](../specs/2026-10-26-unified-dashboard-research-hub-design.md)

## Global Constraints

- **AGENTS.md Rule 5 Compliance:** All documentation Markdown links must be relative (`./...`, `../...`); never use absolute server URLs.
- **AGENTS.md Rule 6 Compliance:** Product-grade radical minimalism (no engineering boast, no raw hex codes on UI, pristine typography).
- **Responsive Layout:** Phải hiển thị cân đối trên mọi độ phân giải (từ màn hình di động 375px đến màn hình máy tính 1920px và ultrawide); loại bỏ hoàn toàn hiện tượng dồn nội dung lên đỉnh và khoảng trống đen khổng lồ bên dưới.
- **Four Verification Gates:** Phải pass 100% `ruff`, `pytest`, `npm test`, `npm build` trước khi deploy lên VPS.

## Review Focus

1. **Seamless Mode Switching:** Chuyển đổi giữa chế độ Tìm bài báo (Discovery) và Đối thoại AI (Chat) giữ nguyên nội dung ô nhập liệu mà không giật layout.
2. **Instant Discovery In-Place:** Khi gõ tìm kiếm hoặc bấm chip chủ đề, danh sách thẻ bài báo hiển thị ngay bên dưới mà không chuyển trang, bấm "Mở Đọc Sâu" kích hoạt mở phiên đọc PDF tức thì.
3. **Graceful PDF Drag-and-Drop:** Vùng kéo thả tệp PDF tích hợp gọn gàng, hỗ trợ cả kéo thả trực tiếp và bấm để duyệt tệp, hiển thị thanh tiến độ chuẩn xác.
4. **5.6-Luna Reasoning Slider Integrity:** Nút bấm bộ não kích hoạt popover 4 mức suy luận (`Off`, `Low`, `Medium`, `High`) hoạt động mượt mà trong chế độ Chat.
5. **Ultra-Wide Screen Adaptability:** Trên màn hình lớn, nội dung căn giữa tuyệt đối theo chiều dọc và chiều ngang, giới hạn chiều rộng tối đa `max-w-4xl` để mắt người đọc thoải mái nhất.

---

### Task 1: Create `UnifiedHeroWorkspace` Component (`apps/web`)

**Files:**
- Create: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`

**Interfaces:**
- Consumes:
  - `DashboardChatInputBox` (input box with 5.6-Luna popover)
  - `ScholarlyResultCard` (paper cards)
  - `discoveryApi.search`, `discoveryApi.openReading`
- Produces:
  - Props:
    - `inputText: string`
    - `onChangeText: (text: string) => void`
    - `onSendChat: (text: string, reasoningEffort?: ReasoningEffortLevel) => void`
    - `onIngestFile: (file: File) => void | Promise<void>`
    - `onOpenPaper: (paper: ScholarlyPaper) => void | Promise<void>`
    - `isGenerating?: boolean`

- [x] **Step 1: Write the failing test for `UnifiedHeroWorkspace`**

```tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { UnifiedHeroWorkspace } from "../components/UnifiedHeroWorkspace";

describe("UnifiedHeroWorkspace Component", () => {
  it("renders centered heading, mode switchers, topic chips, and upload trigger", () => {
    render(
      <UnifiedHeroWorkspace
        inputText=""
        onChangeText={vi.fn()}
        onSendChat={vi.fn()}
        onIngestFile={vi.fn()}
        onOpenPaper={vi.fn()}
      />
    );

    expect(screen.getByText(/Không gian nghiên cứu/i)).toBeInTheDocument();
    expect(screen.getByText(/Tìm bài báo/i)).toBeInTheDocument();
    expect(screen.getByText(/Đối thoại AI/i)).toBeInTheDocument();
    expect(screen.getByText(/Attention Mechanism/i)).toBeInTheDocument();
  });
});
```

- [x] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- UnifiedHeroWorkspace.test.tsx`
Expected: FAIL (component not found).

- [x] **Step 3: Implement `UnifiedHeroWorkspace.tsx`**

Implement the component with:
- Centered container (`min-h-full flex-1 flex flex-col items-center justify-center p-6 w-full max-w-4xl mx-auto`)
- Elegant greeting and Academic Logo
- Mode switcher tabs: `[🔍 Tìm bài báo]` / `[💬 Đối thoại AI]`
- Search handling with `discoveryApi.search` and result list rendering
- 4 Topic chips that trigger search
- Compact PDF upload dropzone
- In-place `ScholarlyResultCard` list with `onOpenPaper` trigger

- [x] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- UnifiedHeroWorkspace.test.tsx`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx
git commit -m "feat(web): implement UnifiedHeroWorkspace with dual search and chat hub"
```

---

### Task 2: Wire `UnifiedHeroWorkspace` into `DashboardContainer`

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardContainer.tsx`

**Interfaces:**
- Consumes: `UnifiedHeroWorkspace`
- Replaces: Lone `<HeroUploadDropzone />` in standby state.
- Wires:
  - `handleFileUpload` -> `onIngestFile`
  - `sendMessage` -> `onSendChat`
  - `discoveryApi.openReading` -> `onOpenPaper`

- [x] **Step 1: Update `DashboardContainer.tsx`**

Replace `HeroUploadDropzone` with `UnifiedHeroWorkspace` when `showStandbyHero` is true, providing `onOpenPaper` handler that calls `discoveryApi.openReading` and redirects to `/dashboard/:sessionId`.

- [x] **Step 2: Run all frontend unit tests**

Run: `npm --prefix apps/web run test`
Expected: All tests pass.

- [x] **Step 3: Commit**

```bash
git add apps/web/src/features/dashboard/components/DashboardContainer.tsx
git commit -m "feat(web): wire UnifiedHeroWorkspace into DashboardContainer standby state"
```

---

### Task 3: Verify All 4 Verification Gates & Deploy to VPS

**Files:**
- Run: `./scripts/deploy_to_vps.sh`

**Interfaces:**
- Target URL: `https://verischolar.duckdns.org`

- [x] **Step 1: Run 4 Verification Gates locally**

Run:
- Gate 1: `uv run ruff check . && uv run ruff format --check .`
- Gate 2: `uv run pytest`
- Gate 3: `npm --prefix apps/web run test`
- Gate 4: `npm --prefix apps/web run build`

- [x] **Step 2: Execute live deployment script**

Run: `./scripts/deploy_to_vps.sh`
Expected: Successfully synced, service restarted, health check 200 OK.

- [x] **Step 3: Verify live deployment via HTTPS**

Run: `curl -fsS https://verischolar.duckdns.org/health`
Expected: `{"status":"ok","service":"verischolar-api"}`.

- [x] **Step 4: Commit and finalize**

```bash
git add -A
git commit -m "chore(deploy): roll out Unified Dashboard Research Hub to production VPS"
```
