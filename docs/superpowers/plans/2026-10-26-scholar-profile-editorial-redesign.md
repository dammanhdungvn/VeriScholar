# Scholar Profile Editorial Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển đổi toàn diện giao diện Hồ sơ & Cài đặt Học giả (/profile, /settings, UserProfileModal) sang phong cách Editorial Academic Luxury (Anthropic Claude & Linear), xóa bỏ hoàn toàn anti-pattern Modal-đè-Trang và banner thừa.

**Architecture:** Tạo component hợp nhất `ScholarSettingsView` chuẩn hóa 3 tab học thuật (`Hồ sơ Học thuật`, `Bảo mật & Khóa BYOK`, `Giao diện`), hỗ trợ 2 chế độ `variant="page"` (cho ProfilePage, SettingsPage) và `variant="dialog"` (cho UserProfileModal). Bảng màu sử dụng Obsidian Warm Paper (`#181715`), Terracotta (`#cc785c`), viền siêu mỏng hairline (`#2e2b26`) và typography Serif/Sans cao cấp.

**Tech Stack:** React 19, Tailwind CSS, Lucide Icons, Zustand (`useAuthStore`), Vitest, Testing Library.

**Spec:** `docs/superpowers/specs/2026-10-26-scholar-profile-editorial-redesign.md`

## Global Constraints

- Python linter & formatter: `uv run ruff check . && uv run ruff format --check .` exit code 0
- Backend tests: `uv run pytest` exit code 0
- Frontend tests: `npm --prefix apps/web run test` exit code 0
- Frontend build: `npm --prefix apps/web run build` exit code 0
- Không sửa đổi schema PostgreSQL hay API endpoints backend (Non-Goals)
- Tương thích 100% với `UserProfileModal.test.tsx` (3 tests passing)
- Bảng màu: `--color-canvas: #181715`, `--color-surface: #201e1b`, `--color-primary: #cc785c`, hairline border

## Review Focus

- Input ORCID sai định dạng (ví dụ thiếu dấu gạch nối): Hiển thị cảnh báo đỏ và chặn submit.
- Nhập BYOK không bắt đầu bằng `sk-`: Hiển thị thông báo yêu cầu khóa OpenAI API hợp lệ.
- Học giả chưa có khóa BYOK: Hiển thị form nhập khóa có toggle ẩn/hiện và nút `Lưu & Xác thực khóa`.
- Học giả đã lưu khóa BYOK: Hiển thị chuỗi mask `byok-masked-badge` kèm nút "Đổi khóa mới" và "Xóa khóa".
- Chuyển đổi Theme Sáng/Tối: Đồng bộ tức thì class `dark` trên `document.documentElement` và lưu vào `useAuthStore`.

---

### Task 1: Tạo Component Lõi `ScholarSettingsView`

**Files:**
- Create: `apps/web/src/features/auth/components/ScholarSettingsView.tsx`
- Test: `apps/web/src/features/auth/__tests__/UserProfileModal.test.tsx`

**Interfaces:**
- Consumes: `useAuthStore`, `authApi`, `useTheme`, `getScholarInitials`, `validateOrcidId`, `maskClientApiKey`
- Produces: `ScholarSettingsView` component with props `{ variant?: "page" | "dialog", defaultTab?: "profile" | "security" | "appearance", onClose?: () => void, user?: UserProfileModalUser | null, onUpdated?: (user: any) => void }`

- [ ] **Step 1: Khởi tạo khung component `ScholarSettingsView.tsx`**

Tạo component `ScholarSettingsView.tsx` chứa state 3 tabs: `profile` ("Hồ sơ Học thuật"), `security` ("Bảo mật & Khóa BYOK"), `appearance` ("Giao diện").
Tích hợp giao diện Editorial Academic Luxury: Card nền `#201e1b`, viền hairline `#2e2b26`, nút Terracotta `#cc785c`, avatar tròn với initials gradient.

- [ ] **Step 2: Triển khai Tab 1 - Hồ sơ Học thuật**

Bao gồm: Avatar Showcase tròn tinh tế + nút đổi ảnh; Badge `Học giả đã xác thực (ISO 32000-1 / DOI Ready)` xanh lục bảo; Họ và tên; Đơn vị công tác & Khoa/Phòng thí nghiệm; Học hàm/Học vị; Mã ORCID iD có icon chuẩn và validate regex; Link Google Scholar; Hướng nghiên cứu & Bio; Nút "Lưu hồ sơ".

- [ ] **Step 3: Triển khai Tab 2 - Bảo mật & Khóa BYOK**

Bao gồm:
1. Thẻ Két sắt Khóa AI (BYOK AES-256-GCM Vault) với badge `data-testid="byok-masked-badge"`, toggle hiện form đổi khóa, nút "Lưu & Xác thực khóa" với `Loader2`, nút "Xóa khóa".
2. Thẻ Đổi mật khẩu dự phòng (Mật khẩu hiện tại, mật khẩu mới, xác nhận mật khẩu, nút "Cập nhật mật khẩu").
3. Thẻ Phiên làm việc (Active Sessions: Thông tin thiết bị, thời hạn 30 ngày, nút "Đăng xuất thiết bị").
4. Thẻ Tài khoản liên kết (Google OAuth Connected).

- [ ] **Step 4: Triển khai Tab 3 - Giao diện**

Bao gồm 3 lựa chọn trực quan: `☀️ Sáng`, `🌙 Tối`, `💻 Tự động`. Tương tác trực tiếp với `useTheme` và `authApi.updateProfile({ theme_preference })`.

- [ ] **Step 5: Kiểm tra type check và lint**

Run: `npm --prefix apps/web run build`
Expected: Build thành công hoặc không có lỗi cú pháp trong `ScholarSettingsView.tsx`.

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/features/auth/components/ScholarSettingsView.tsx
git commit -m "feat(auth): create unified ScholarSettingsView component with editorial aesthetic"
```

---

### Task 2: Tích hợp `ScholarSettingsView` vào `UserProfileModal` và Xác nhận Vitest Green

**Files:**
- Modify: `apps/web/src/components/profile/UserProfileModal.tsx`
- Test: `apps/web/src/features/auth/__tests__/UserProfileModal.test.tsx`

**Interfaces:**
- Consumes: `ScholarSettingsView` từ Task 1
- Produces: `UserProfileModal` xuất khẩu giữ nguyên API và các hàm tiện ích `validateOrcidId`, `maskClientApiKey`, `ORCID_REGEX`.

- [ ] **Step 1: Cập nhật `UserProfileModal.tsx` để render `ScholarSettingsView variant="dialog"`**

Giữ nguyên các export: `validateOrcidId`, `maskClientApiKey`, `ORCID_REGEX`, `UserProfileModalProps`, `UserProfileModalUser`.
Bọc `ScholarSettingsView variant="dialog" onClose={onClose} user={user} onUpdated={onUpdated}` trong `Dialog` và container modal thanh lịch.

- [ ] **Step 2: Chạy kiểm thử vitest để đảm bảo 3 test suite pass 100%**

Run: `npm --prefix apps/web run test`
Expected: PASS (3/3 tests passed in `UserProfileModal.test.tsx`).

- [ ] **Step 3: Commit**

```bash
git add apps/web/src/components/profile/UserProfileModal.tsx
git commit -m "refactor(auth): integrate ScholarSettingsView into UserProfileModal with backward compatibility"
```

---

### Task 3: Tái cấu trúc `ProfilePage.tsx` và `SettingsPage.tsx` (Xóa bỏ Banner & Modal đè Trang)

**Files:**
- Modify: `apps/web/src/features/auth/components/ProfilePage.tsx`
- Modify: `apps/web/src/features/auth/components/SettingsPage.tsx`
- Modify: `apps/web/src/features/auth/components/AccountSettingsModal.tsx`

**Interfaces:**
- Consumes: `ScholarSettingsView` từ Task 1
- Produces: `ProfilePage` (mặc định tab `profile`) và `SettingsPage` (mặc định tab `security`) hiển thị toàn màn hình đồng bộ.

- [ ] **Step 1: Refactor `ProfilePage.tsx`**

Xóa bỏ hoàn toàn div banner màu vàng (`bg-amber-500/10`), nút bấm `Cấu hình BYOK & ORCID (3 Tabs)`, và state `isByokModalOpen`.
Render trực tiếp `<LandingNavbar />` và `<ScholarSettingsView variant="page" defaultTab="profile" onClose={() => navigate("/dashboard")} />`.

- [ ] **Step 2: Refactor `SettingsPage.tsx`**

Xóa bỏ banner và popup đè.
Render trực tiếp `<LandingNavbar />` và `<ScholarSettingsView variant="page" defaultTab="security" onClose={() => navigate("/dashboard")} />`.

- [ ] **Step 3: Cập nhật `AccountSettingsModal.tsx` để dùng chung `ScholarSettingsView`**

Đảm bảo bất kỳ nơi nào còn gọi `<AccountSettingsModal>` hoặc `<AccountSettingsContent>` đều hoạt động mượt mà bằng cách ủy quyền (delegate) sang `ScholarSettingsView`.

- [ ] **Step 4: Chạy kiểm thử toàn bộ frontend**

Run: `npm --prefix apps/web run test`
Expected: 3 tests pass 100%.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/auth/components/ProfilePage.tsx apps/web/src/features/auth/components/SettingsPage.tsx apps/web/src/features/auth/components/AccountSettingsModal.tsx
git commit -m "refactor(auth): eliminate modal-on-page banner and route to unified ScholarSettingsView"
```

---

### Task 4: Kiểm thử Toàn trình & 4 Cổng Xác Minh Bắt Buộc

**Files:**
- Test: Toàn bộ codebase backend & frontend

- [ ] **Step 1: Cổng 1 - Linter & Formatter Python**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: All checks passed.

- [ ] **Step 2: Cổng 2 - Backend & Boundary Tests**

Run: `uv run pytest`
Expected: 100% tests pass (49/49).

- [ ] **Step 3: Cổng 3 - Frontend Unit Tests**

Run: `npm --prefix apps/web run test`
Expected: 100% tests pass (3/3).

- [ ] **Step 4: Cổng 4 - Production Build Giao diện**

Run: `npm --prefix apps/web run build`
Expected: Build success with exit code 0.

- [ ] **Step 5: Commit kết thúc kế hoạch**

```bash
git commit --allow-empty -m "chore(release): complete scholar profile editorial redesign plan verification"
```
