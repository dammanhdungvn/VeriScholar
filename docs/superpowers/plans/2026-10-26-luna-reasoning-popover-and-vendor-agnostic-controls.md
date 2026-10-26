# 5.6-Luna Vendor-Agnostic Reasoning Popover & Chat Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa thanh nhập liệu tối giản chuẩn hóa và Popover tinh chỉnh mức độ suy luận 4 nấc (`Off`, `Low`, `Medium`, `High`) của mô hình 5.6-Luna trên giao diện Trợ lý Nghiên cứu Khoa học, xây dựng tầng trừu tượng độc lập với nhà cung cấp (Vendor-Agnostic Adapter Pattern) loại bỏ hoàn toàn nguy cơ phụ thuộc vào một nhà cung cấp LLM cụ thể.

**Architecture:** Áp dụng Kiến trúc Lục giác (Hexagonal Architecture): Định nghĩa `ReasoningEffortLevel` thuần khiết trong `packages/core`; tầng Adapter `apps/api/src/api/adapters/` ánh xạ mức độ suy luận trung lập sang tham số kỹ thuật tương ứng của từng nhà cung cấp (OpenAI `reasoning_effort`, Gemini `thinking_budget`, Anthropic `budget_tokens`, Local DMR prompt); tầng giao diện `apps/web` cung cấp component `ReasoningPopover` gắn trên icon Bộ não của thanh `DashboardChatInputBox`, loại bỏ triệt để icon bàn tay và các chi tiết dư thừa theo chuẩn tối giản 80/20.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, React 19, TypeScript, Tailwind CSS, Zustand v5, Lucide React, Vitest.

**Spec:** [`docs/specs/03-sessions-and-deep-reading-spec.md`](../../specs/03-sessions-and-deep-reading-spec.md) (Mục 6.C) & [`docs/PRD/03-sessions-and-deep-reading-crud.md`](../../PRD/03-sessions-and-deep-reading-crud.md).

---

## Global Constraints

- 100% mã nguồn trong `packages/core/` chỉ dùng Python Standard Library và `pydantic`, cấm tuyệt đối import `fastapi`, `sqlalchemy`, `openai`, `httpx`.
- Tầng giao diện tuân thủ Quy chuẩn Ngôn từ & Bố cục Tối giản (Rule 6 in `AGENTS.md`): Tuyệt đối không hiển thị icon Bàn tay hay các icon tính năng chưa hoàn thiện; chỉ giữ lại nút `+`, ô văn bản, icon Bộ não và nút Gửi.
- Giá trị suy luận trung lập hỗ trợ chính xác 4 nấc: `off`, `low`, `medium`, `high`. Mặc định của mô hình 5.6-Luna là `high` (Socratic Deep Reasoning).
- Khi người dùng chọn nấc `off`, hệ thống chuyển mô hình sang chế độ phản hồi trực tiếp không tạo thẻ suy luận ngầm và icon Bộ não trên thanh chat chuyển sang màu xám mờ trung tính.
- Bốn Cổng Xác Minh Bắt Buộc (`uv run ruff check .`, `uv run pytest`, `npm --prefix apps/web run test`, `npm --prefix apps/web run build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **Vendor-Agnostic Fallback Safety:** Khi cấu hình chuyển từ OpenAI (`5.6-luna`) sang Gemini hoặc Anthropic, adapter phải tự động ánh xạ mức `off`/`low`/`medium`/`high` sang `thinking_budget` hoặc `budget_tokens` mà không gây lỗi tham số không hợp lệ.
2. **Click-Outside Popover Dismissal:** Khi Popover suy luận đang mở, nhấp chuột ra ngoài phạm vi hoặc bấm phím Escape phải đóng popover êm ái mà không làm mất trạng thái văn bản đang gõ dở trong textarea.
3. **Stepped Slider Discrete Snapping:** Thanh trượt 4 nấc trong Popover phải gắn kết chuẩn xác vào 4 điểm dừng (`Off`, `Low`, `Medium`, `High`), không bị lệch tỷ lệ phần trăm hiển thị hoặc trượt lửng lơ giữa các nấc.
4. **State Persistence Across Chat Turns:** Mức suy luận đã chọn phải được ghi nhớ trong `useDashboardStore` của phiên làm việc, không bị tự động reset về mặc định sau mỗi lượt gửi tin nhắn trừ khi người dùng chủ động bấm nút Hoàn tác (Reset).
5. **Session Chat SSE Compatibility:** Payload gửi tới `POST /api/v1/sessions/{id}/messages` phải mang theo trường `reasoning_effort: Optional[str]` và được ghi nhận đầy đủ vào Langfuse telemetry metadata.

---

## Implementation Tasks

### Task 1: Core Domain `ReasoningEffortLevel` Value Object & Adapter Mapping (`packages/core` & `apps/api`)

**Files:**
- Create: `packages/core/src/core/domain/value_objects/reasoning_effort.py`
- Modify: `apps/api/src/api/core/config.py`
- Test: `packages/core/tests/test_reasoning_effort_core.py`

**Interfaces:**
- Consumes: Python Standard Library (`enum.Enum`, `typing.Literal`).
- Produces:
  - `ReasoningEffortLevel = Literal["off", "low", "medium", "high"]`
  - `resolve_provider_reasoning_params(provider: str, level: ReasoningEffortLevel) -> dict[str, Any]` (chuyển đổi độc lập cho OpenAI, Gemini, Anthropic, DMR).

- [ ] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_reasoning_effort_core.py`:
```python
import pytest
from core.domain.value_objects.reasoning_effort import (
    ReasoningEffortLevel,
    map_reasoning_effort_to_provider,
)


def test_map_reasoning_effort_to_openai():
    # OpenAI mapping
    assert map_reasoning_effort_to_provider("openai", "off") == {}
    assert map_reasoning_effort_to_provider("openai", "low") == {"reasoning_effort": "low"}
    assert map_reasoning_effort_to_provider("openai", "medium") == {"reasoning_effort": "medium"}
    assert map_reasoning_effort_to_provider("openai", "high") == {"reasoning_effort": "high"}


def test_map_reasoning_effort_to_gemini():
    # Gemini thinking_config mapping
    assert map_reasoning_effort_to_provider("gemini", "off") == {"thinking_budget": 0}
    assert map_reasoning_effort_to_provider("gemini", "low") == {"thinking_budget": 1024}
    assert map_reasoning_effort_to_provider("gemini", "high") == {"thinking_budget": 16384}


def test_map_reasoning_effort_to_anthropic():
    # Anthropic thinking tokens mapping
    assert map_reasoning_effort_to_provider("anthropic", "off") == {"thinking": {"type": "disabled"}}
    assert map_reasoning_effort_to_provider("anthropic", "high") == {
        "thinking": {"type": "enabled", "budget_tokens": 32768}
    }


def test_invalid_effort_level_rejected():
    with pytest.raises(ValueError):
        map_reasoning_effort_to_provider("openai", "ultra_max")  # type: ignore
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_reasoning_effort_core.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'core.domain.value_objects.reasoning_effort'`.

- [ ] **Step 3: Implement `packages/core/src/core/domain/value_objects/reasoning_effort.py`**

Cài đặt kiểu `ReasoningEffortLevel` và hàm chuẩn hóa `map_reasoning_effort_to_provider(provider: str, level: str) -> dict[str, Any]` thuần Python Standard Library.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_reasoning_effort_core.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/domain/value_objects/reasoning_effort.py packages/core/tests/test_reasoning_effort_core.py
git commit -m "feat(core): add vendor-agnostic ReasoningEffortLevel VO and provider mapping function"
```

---

### Task 2: Backend Chat Message Schema & Reasoning Effort Injection (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/schemas/session.py`
- Modify: `apps/api/src/api/services/session_chat_service.py`
- Test: `apps/api/tests/test_reasoning_effort_endpoint.py`

**Interfaces:**
- Consumes: `ReasoningEffortLevel` từ `packages/core`, `SessionChatMessageRequest` từ `apps/api/src/api/schemas/session.py`.
- Produces:
  - Bổ sung trường `reasoning_effort: Optional[str] = "high"` vào `SessionChatMessageRequest`.
  - `SessionChatService` truyền `reasoning_effort` vào tầng gọi OpenAI/Luna SDK và lưu vết vào Langfuse span generation.

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_reasoning_effort_endpoint.py`:
```python
import pytest
from httpx import AsyncClient
from api.schemas.session import SessionChatMessageRequest


def test_session_chat_request_schema_supports_reasoning_effort():
    req_default = SessionChatMessageRequest(content="Phân tích mô hình")
    assert req_default.reasoning_effort in ("high", "medium")

    req_custom = SessionChatMessageRequest(content="Phân tích", reasoning_effort="low")
    assert req_custom.reasoning_effort == "low"

    req_off = SessionChatMessageRequest(content="Phân tích", reasoning_effort="off")
    assert req_off.reasoning_effort == "off"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_reasoning_effort_endpoint.py -v`  
Expected: FAIL (nếu trường `reasoning_effort` chưa tồn tại trong `SessionChatMessageRequest`).

- [ ] **Step 3: Update `SessionChatMessageRequest` and `SessionChatService`**

Thêm `reasoning_effort: Literal["off", "low", "medium", "high"] = "high"` vào schema và truyền vào `map_reasoning_effort_to_provider` khi khởi tạo request đến LLM client.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_reasoning_effort_endpoint.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/schemas/session.py apps/api/src/api/services/session_chat_service.py apps/api/tests/test_reasoning_effort_endpoint.py
git commit -m "feat(api): add reasoning_effort field to SessionChatMessageRequest and chat service"
```

---

### Task 3: Frontend Reasoning Popover Component, Stepped Slider & Chat Input Box Integration (`apps/web`)

**Files:**
- Create: `apps/web/src/features/dashboard/components/ReasoningPopover.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx`
- Modify: `apps/web/src/features/dashboard/stores/useDashboardStore.ts`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardChatInputBox.test.tsx`

**Interfaces:**
- Consumes: Lucide Icons (`Brain`, `RotateCcw`, `ArrowUp`, `Plus`, `Paperclip`, `X`).
- Produces:
  - `ReasoningPopover`:
    - Hiển thị mức độ: "High" (chữ màu `#38bdf8` / `text-sky-400`), kèm nút Hoàn tác `RotateCcw`.
    - Dòng thông tin mô hình: `5.6 Luna >`.
    - Thanh trượt 4 nấc (`Off`, `Low`, `Medium`, `High`) với track màu xanh nổi bật và nút tròn kéo/nhấp trực quan.
  - `DashboardChatInputBox`:
    - Gắn `ReasoningPopover` nổi phía trên icon Bộ não.
    - Tuyệt đối không hiển thị icon Bàn tay.
    - Truyền `reasoningEffort` vào callback `onSend(text, reasoningEffort)`.

- [ ] **Step 1: Write the failing test**

Tạo `apps/web/src/features/dashboard/__tests__/DashboardChatInputBox.test.tsx`:
```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { describe, it, expect, vi } from "vitest";
import { DashboardChatInputBox } from "../components/DashboardChatInputBox";

describe("DashboardChatInputBox Component", () => {
  it("renders pill input without hand icon, opens Reasoning Popover on Brain click, and selects 4-step effort", () => {
    const handleSend = vi.fn();
    const handleChangeText = vi.fn();

    render(
      <DashboardChatInputBox
        inputText="Explain attention mechanism"
        onChangeText={handleChangeText}
        onSend={handleSend}
      />
    );

    // Verify hand icon does NOT exist
    expect(screen.queryByTitle(/bàn tay/i)).not.toBeInTheDocument();
    expect(screen.queryByTestId("hand-tool-btn")).not.toBeInTheDocument();

    // Verify Brain toggle exists
    const brainBtn = screen.getByTestId("toggle-reasoning-btn");
    expect(brainBtn).toBeInTheDocument();

    // Click brain button to open Popover
    fireEvent.click(brainBtn);

    // Popover elements
    expect(screen.getByText(/5.6 Luna/i)).toBeInTheDocument();
    expect(screen.getByText(/High/i)).toBeInTheDocument();
    expect(screen.getByTestId("reasoning-slider")).toBeInTheDocument();

    // Select Medium effort
    const mediumStep = screen.getByTestId("reasoning-step-medium");
    fireEvent.click(mediumStep);
    expect(screen.getByText(/Medium/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- DashboardChatInputBox`  
Expected: FAIL (chưa có Popover và slider data-testid).

- [ ] **Step 3: Implement `ReasoningPopover.tsx` and integrate into `DashboardChatInputBox.tsx`**

1. Tạo `apps/web/src/features/dashboard/components/ReasoningPopover.tsx` với thiết kế pixel-perfect bám sát 2 ảnh người dùng cung cấp:
   - Header hiển thị nấc hiện tại: `High` / `Medium` / `Low` / `Off` với màu xanh sáng.
   - Nút reset nhỏ ở góc phải đặt lại về `High`.
   - Subtitle: `5.6 Luna >`.
   - Stepped slider: 4 nấc (`Off`, `Low`, `Medium`, `High`) với track active đổi màu xanh và thumb tròn mượt mà.
2. Cập nhật `useDashboardStore.ts` lưu `reasoningEffort: "off" | "low" | "medium" | "high"` (mặc định `"high"`).
3. Cập nhật `DashboardChatInputBox.tsx`:
   - Bấm icon Bộ não mở/đóng `ReasoningPopover`.
   - Khi `reasoningEffort === "off"`, icon Bộ não đổi màu xám mờ.
   - Không xuất hiện bất kỳ icon bàn tay nào.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- DashboardChatInputBox`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/dashboard/components/ReasoningPopover.tsx apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx apps/web/src/features/dashboard/stores/useDashboardStore.ts apps/web/src/features/dashboard/__tests__/DashboardChatInputBox.test.tsx
git commit -m "feat(web): add 5.6-Luna ReasoningPopover with 4-step slider and minimalist pill bar"
```

---

### Task 4: End-to-End Verification across All 4 Verification Gates

- [ ] **Step 1: Run Gate 1 (Python Linter & Formatter)**
  `uv run ruff check . && uv run ruff format --check .` (Exit code 0).

- [ ] **Step 2: Run Gate 2 (Backend & Core Pytest Suite)**
  `uv run pytest` (Exit code 0).

- [ ] **Step 3: Run Gate 3 (Frontend Vitest Suite)**
  `npm --prefix apps/web run test` (Exit code 0).

- [ ] **Step 4: Run Gate 4 (Frontend Production Build)**
  `npm --prefix apps/web run build` (Exit code 0).

- [ ] **Step 5: Commit & Finalize**
  Đánh dấu hoàn thành toàn bộ kịch bản và chuẩn bị thực thi.
