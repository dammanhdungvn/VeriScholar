# Đặc tả Thiết kế: Tái cấu trúc Giao diện Hồ sơ & Cài đặt Học giả (Editorial Academic Luxury)

- **Ngày tạo:** 2026-10-26
- **Tác giả:** VeriScholar Agent & Dam Manh Dung
- **Trạng thái:** Chờ phê duyệt (Pending Approval)
- **Phạm vi:** `apps/web/src/features/auth/`, `apps/web/src/components/profile/`, Design Tokens & UI Styles

---

## 1. Bối cảnh & Mục đích (Intent & The Why)
Trong quá trình kiểm thử trải nghiệm người dùng tại màn hình `/profile` và `/settings`, giao diện hiện tại bộc lộ nhiều điểm nghẽn nghiêm trọng về thị giác và cấu trúc điều hướng:
1. **Lỗi Modal đè Trang (Modal-on-Page Anti-pattern):** Trang `/profile` render một thẻ cài đặt tài khoản kích thước lớn, nhưng trên đỉnh lại có banner màu vàng cam chứa nút *"Cấu hình BYOK & ORCID (3 Tabs)"*. Khi bấm vào, một modal phụ (`UserProfileModal`) bật lên che phủ gần như toàn bộ nội dung phía dưới, gây trùng lặp thông tin (Avatar, họ tên, email, tab điều hướng).
2. **Màu sắc chói gắt & lệch tông học thuật:** Nền tối hiện tại có màu nâu đen mờ đục, các nút bấm và viền dùng màu cam neon (`#ea580c` / `#f59e0b`) chói lọi, không phù hợp với các học giả, giáo sư nghiên cứu tài liệu đêm khuya.
3. **Typography & Bố cục phân mảnh:** Avatar dạng hình chữ nhật thô kèm nút máy ảnh thô sơ; các ô nhập liệu (Input) phẳng, thiếu chiều sâu; các badge thông tin dài dòng, mất thẩm mỹ.

Mục tiêu của tài liệu này là xác lập đặc tả thiết kế toàn diện để đưa màn hình Hồ sơ & Cài đặt về phong cách chuẩn mực: **Editorial Academic Luxury** (lấy cảm hứng từ Anthropic Claude và Linear), thanh lịch, tinh tế và tối ưu cho nghiên cứu khoa học dài giờ.

---

## 2. Mục tiêu, Phi mục tiêu & Phản mục tiêu (Goals, Non-Goals, Anti-Goals)

### Mục tiêu (Goals)
- **Hợp nhất trải nghiệm (Single Unified Experience):** Xóa bỏ hoàn toàn thanh banner thừa và hiện tượng modal đè modal. Gộp toàn bộ tính năng quản trị học giả vào một trang Dashboard Cài đặt duy nhất (`ScholarSettingsView`) có thể dùng ở cả chế độ trang toàn màn hình (`/profile`, `/settings`) lẫn modal bật nhanh (`UserProfileModal`).
- **Chuẩn hóa thị giác Editorial Academic Luxury:**
  - Nền Obsidian giấy ấm tối (`#181715` / `#201e1b`) và Giấy ngà sáng (`#faf8f5`).
  - Điểm nhấn Terracotta đất nung ấm áp (`#cc785c`), thay thế toàn bộ cam neon chói gắt (`#ea580c`).
  - Viền siêu mảnh hairline (`#2e2b26` / `#e5e0d8`), bo góc mềm mại `rounded-xl` / `rounded-2xl`.
  - Font chữ kết hợp: Serif học thuật cao cấp (*Newsreader / Lora*) cho tiêu đề & đại diện, Sans kỹ thuật (*Inter / Plus Jakarta Sans*) cho nhãn và dữ liệu.
- **Bảo toàn 100% tính năng & API backend:** Giữ nguyên các luồng API đã kiểm chứng (BYOK AES-256-GCM, cập nhật ORCID, đổi mật khẩu dự phòng, thu hồi phiên làm việc, chuyển đổi theme sáng/tối).
- **Vượt qua 4 Cổng kiểm định:** 100% pass linter (`ruff`), pytest backend, vitest frontend (`UserProfileModal.test.tsx`), và `vite build`.

### Phi mục tiêu (Non-Goals)
- Không thay đổi cấu trúc bảng cơ sở dữ liệu PostgreSQL hoặc schema Pydantic ở backend.
- Không thay đổi cơ chế mã hóa AES-256-GCM hoặc khóa master key `ENCRYPTION_MASTER_KEY`.
- Không gọi thêm endpoint kiểm tra key backend mới; sử dụng đúng flow `authApi.updateProfile` và `authApi.deleteByokKey` hiện có.
- Không can thiệp vào các trang khác (như `/writing`, `/dashboard`, `/library`) ngoài việc đảm bảo các liên kết điều hướng trỏ về trang cài đặt hoạt động mượt mà.

### Phản mục tiêu (Anti-Goals)
- **Tuyệt đối cấm:** Đặt một modal bật lên ngay trên một trang cài đặt đã có sẵn các trường dữ liệu tương tự.
- **Tuyệt đối cấm:** Sử dụng các màu neon bão hòa cao (như cam chói, xanh nõn chuối) làm điểm nhấn chính.
- **Tuyệt đối cấm:** Gây vỡ các test unit và E2E hiện có trong `apps/web/src/features/auth/__tests__/UserProfileModal.test.tsx`.

---

## 3. Các Phương án Đã Xem xét (Approaches Considered)

### Phương án 1: Editorial Academic Luxury (Anthropic Claude & Linear) — *Đã chọn*
- **Kiến trúc:** Bố cục dạng Trang Cài đặt chuẩn mực với 3 tab kinh điển đồng bộ (tương thích 100% test suite hiện hành):
  1. 🎓 **Hồ sơ Học thuật** (*Scholar Profile & Identifiers*): Thông tin định danh, viện nghiên cứu, mã ORCID, Google Scholar, ảnh đại diện tròn tinh tế.
  2. 🛡️ **Bảo mật & Khóa BYOK** (*Security & BYOK Vault*): Quản lý Két sắt mã hóa AES-256-GCM, đổi mật khẩu dự phòng, quản lý phiên làm việc (Active Sessions).
  3. 🎨 **Giao diện** (*Appearance & Theme*): Tùy chọn Sáng ngà / Tối Obsidian / Tự động.
- **Thẩm mỹ:** Nền giấy Obsidian `#181715`, bề mặt thẻ `#201e1b`, viền hairline `#2e2b26`, màu nhấn Terracotta `#cc785c`.
- **Đánh đổi:** Gom toàn bộ logic vào component dùng chung `ScholarSettingsView.tsx`, xóa bỏ `AccountSettingsModal` cũ và thanh banner thừa, mang lại trải nghiệm đẳng cấp quốc tế, đồng nhất và thư giãn cho mắt học giả.

### Phương án 2: Minimalist Tech (Vercel / Raycast Dark Glassmorphism)
- **Đặc trưng:** Nền đen tuyệt đối OLED `#000000`, viền xám lạnh sắc cạnh, màu nhấn Cyan/Emerald.
- **Lý do loại bỏ:** Đẹp cho developer tools, nhưng tạo cảm giác lạnh lẽo, đậm chất hacker/DevOps, không toát lên được tinh thần học thuật và chiều sâu của một trợ lý nghiên cứu khoa học.

### Phương án 3: Classic University Portal
- **Đặc trưng:** Nền trắng/xám công sở, màu xanh navy, bảng biểu truyền thống kiểu cổng thông tin đại học cũ.
- **Lý do loại bỏ:** Già cỗi, thiếu linh hồn hiện đại của một AI Copilot tiên tiến.

---

## 4. Đặc tả Chi tiết Thành phần Giao diện (Detailed UI Component Spec)

### 4.1. Cấu trúc Hợp nhất (Unified Component Architecture)
Tách biệt rõ ràng:
- **`ScholarSettingsView` (`apps/web/src/features/auth/components/ScholarSettingsView.tsx`):**
  - Component lõi chịu trách nhiệm render toàn bộ nội dung cài đặt theo 3 Tabs học thuật chuẩn (`Hồ sơ Học thuật`, `Bảo mật & Khóa BYOK`, `Giao diện`).
  - Hỗ trợ prop `variant="page"` (khi mount trong `ProfilePage` hoặc `SettingsPage`) và `variant="dialog"` (khi mount bên trong `Dialog` của `UserProfileModal`).
- **`ProfilePage.tsx` & `SettingsPage.tsx`:**
  - Render trực tiếp `<LandingNavbar />` và `<ScholarSettingsView variant="page" defaultTab="..." />`.
  - **Xóa bỏ hoàn toàn** thanh banner cảnh báo màu vàng trên cùng (`bg-amber-500/10`) và nút bấm kích hoạt modal đè lên trang.
- **`UserProfileModal.tsx`:**
  - Giữ nguyên API contract (`isOpen`, `onClose`, `user`, `onUpdated`), bên trong render `<ScholarSettingsView variant="dialog" onClose={onClose} />`.

### 4.2. Chi tiết 3 Phân hệ Tabs Chuẩn hóa

#### Tab 1: Hồ sơ Học thuật (Scholar Profile & Identifiers)
- **Avatar Showcase:** Khung tròn mềm mại `rounded-full`, viền mảnh `ring-1 ring-border/50`, chữ viết tắt với gradient Terracotta sang trọng. Nút đổi ảnh nhỏ gọn dạng icon overlay tinh tế ở góc dưới avatar.
- **Huy hiệu Xác thực Học giả:** Badge thanh lịch `Học giả đã xác thực (ISO 32000-1 / DOI Ready)` với tông màu xanh lục bảo dịu nhẹ (`emerald-500/10`, viền `emerald-500/20`, chữ `emerald-400`).
- **Các trường thông tin:**
  - Họ và tên (bắt buộc).
  - Đơn vị công tác (Viện / Trường đại học) & Khoa / Phòng thí nghiệm (Grid 2 cột).
  - Học hàm / Học vị (GS, PGS, TS, ThS, Nghiên cứu sinh).
  - Mã định danh ORCID iD: Tích hợp icon ORCID xanh chuẩn quốc tế `#a6ce39`, tự động validate định dạng `0000-0000-0000-0000`.
  - Liên kết Google Scholar, Hướng nghiên cứu chính & Giới thiệu học thuật ngắn (Bio).
- **Nút hành động:** Nút "Lưu hồ sơ" với tông Terracotta ấm (`bg-primary hover:bg-primary/90 text-white`).

#### Tab 2: Bảo mật & Khóa BYOK (Security & BYOK Vault)
- **Phần 1 - Két sắt Khóa AI Cá nhân (BYOK AES-256-GCM Vault):**
  - Trạng thái Khóa:
    - Khi đã có khóa: Hiển thị badge `data-testid="byok-masked-badge"` với chuỗi mask (ví dụ `sk-proj-...4f8A`), huy hiệu "Đã mã hóa AES-256-GCM", nút "Đổi khóa mới" và nút "Xóa khóa".
    - Khi nhập/đổi khóa: Ô nhập liệu bảo mật (input password có toggle xem/ẩn `sk-proj-...`), nút submit **"Lưu & Xác thực khóa"** với hiệu ứng spinner `Loader2` khi đang mã hóa.
  - Ghi chú minh bạch (Scholarly Transparency): Khẳng định nguyên tắc Zero-retention: Khóa API cá nhân chỉ được giải mã trên RAM khi thực hiện inference và không bao giờ lưu trữ dạng plain-text.
- **Phần 2 - Thiết lập / Đổi mật khẩu dự phòng:**
  - Ô nhập mật khẩu hiện tại, mật khẩu mới (có thanh đo độ mạnh mật khẩu chuẩn học thuật), xác nhận mật khẩu và nút "Cập nhật mật khẩu".
- **Phần 3 - Phiên làm việc hiện tại (Active Sessions):**
  - Card thông tin thiết bị đang đăng nhập, hiển thị trình duyệt, thời gian còn lại (Remember Me 30 ngày), nút "Đăng xuất thiết bị" màu rose trang nhã.
- **Phần 4 - Tài khoản liên kết (Connected Accounts):**
  - Thẻ kết nối Google OAuth với trạng thái `Đã kết nối` và email hiển thị rõ ràng.

#### Tab 3: Giao diện (Appearance & Theme)
- **3 Tùy chọn Theme:**
  - ☀️ `☀️ Sáng`: Tông giấy ngà ấm (Scholarly Parchment), dịu mắt khi đọc ban ngày.
  - 🌙 `🌙 Tối`: Nền đen giấy ấm Obsidian (`#181715`), thư giãn thị giác ban đêm.
  - 💻 `💻 Tự động`: Tự động thích ứng theo hệ điều hành.
- Thẻ chọn với hiệu ứng viền sáng rõ nét khi active (`border-primary bg-primary/5`).

---

## 5. Quy chuẩn Thiết kế (Design Tokens & Styling Rules)
1. **Bảng màu:**
   - `--canvas`: `#181715` (Nền chính tối), `#faf8f5` (Nền sáng).
   - `--surface`: `#201e1b` (Bề mặt thẻ tối), `#ffffff` (Bề mặt thẻ sáng).
   - `--surface-soft`: `#282521` (Hover state tối), `#f4efe6` (Hover state sáng).
   - `--primary`: `#cc785c` (Terracotta ấm), hover `#b8674c`.
   - `--hairline`: `#2e2b26` (Viền hairline tối), `#e7e2da` (Viền sáng).
2. **Typography:**
   - Tiêu đề & Tên học giả: `font-serif` (Anthropic Serif / Newsreader / Lora).
   - Nội dung, ô nhập liệu & nhãn: `font-sans` (Inter / Plus Jakarta Sans).
   - Mã ORCID, Key mask, Token: `font-mono`.
3. **Hiệu ứng & Viền:**
   - Sử dụng `border border-hairline` siêu mảnh thay vì viền dày thô.
   - Bo góc `rounded-xl` cho input/button, `rounded-2xl` cho các container thẻ.
   - Focus ring: `focus:ring-2 focus:ring-primary/30 focus:border-primary`.

---

## 6. Việc giao lại cho Người thực thi (Left to the Builder)
1. **Refactor cấu trúc file:**
   - Tạo component `apps/web/src/features/auth/components/ScholarSettingsView.tsx`.
   - Cập nhật `ProfilePage.tsx` và `SettingsPage.tsx` để render `ScholarSettingsView` với tab mặc định tương ứng (`profile` cho ProfilePage, `security` cho SettingsPage).
   - Cập nhật `UserProfileModal.tsx` để render `ScholarSettingsView` trong `Dialog` khi cần hiển thị dạng modal độc lập.
   - Dọn dẹp mã nguồn cũ không còn sử dụng trong `AccountSettingsModal.tsx`.
2. **Bảo đảm 100% test pass:**
   - Đảm bảo các query text và testid trong `apps/web/src/features/auth/__tests__/UserProfileModal.test.tsx` (`Hồ sơ Học thuật`, `Bảo mật & Khóa BYOK`, `Giao diện`, `Lưu & Xác thực khóa`, `byok-masked-badge`) pass 100%.
3. **Chạy đầy đủ 4 Cổng kiểm định:**
   - `uv run ruff check . && uv run ruff format --check .`
   - `uv run pytest`
   - `npm --prefix apps/web run test`
   - `npm --prefix apps/web run build`
