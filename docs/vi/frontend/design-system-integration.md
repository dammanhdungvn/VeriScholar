# Hướng Dẫn Tích Hợp Hệ Thống Thiết Kế (Design System Integration)

Tài liệu này xác lập quy chuẩn chuyển giao và triển khai thực tế 100% từ hồ sơ đặc tả thiết kế [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md) vào kiến trúc mã nguồn Frontend (`apps/web/`) của nền tảng **VeriScholar**.

---

## 1. TRIẾT LÝ THIẾT KẾ HỌC THUẬT (EDITORIAL HUMANIST PHILOSOPHY)

Khác biệt hoàn toàn với phong cách giao diện SaaS đại trà dùng nền trắng tinh lạnh lẽo và màu xanh công nghệ (Cool Slate / Blue), VeriScholar tuân thủ triệt để ngôn ngữ thiết kế **Warm-Canvas Editorial Interface** từ [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md):
1. **Nền giấy kem ấm áp (Tinted Cream Canvas `#faf9f5`):** Mang lại trải nghiệm đọc bài báo khoa học như trên các tạp chí học thuật danh tiếng, chống lóa và chống mỏi mắt cho nhà nghiên cứu khi làm việc nhiều giờ liền.
2. **Điểm nhấn màu San hô ấm (Coral Accent `#cc785c`):** Điểm xuyết trên các nút bấm hành động chính (Primary CTA), huy hiệu trích dẫn quan trọng và các khối kêu gọi hành động nổi bật.
3. **Mặt sàn công nghệ tối màu (Dark Navy Surfaces `#181715`):** Sử dụng tương phản mạnh mẽ cho các khối hiển thị mã nguồn (Code blocks), cửa sổ dòng lệnh (Terminal mockups) và đồ thị suy luận sâu của AI.
4. **Cặp phông chữ đối xứng Editorial:** 
   - Tiêu đề: **Slab-Serif Display** (`Copernicus` / `Tiempos Headline`, mở rộng mã nguồn mở với `Cormorant Garamond` hoặc `EB Garamond` tại weight 400 và negative tracking).
   - Nội dung và nhãn giao diện: **Humanist Sans** (`StyreneB`, mở rộng mã nguồn mở chuẩn xác với `Inter`).
   - Mã nguồn và công thức giải thuật: **`JetBrains Mono`**.

---

## 2. BẢNG MÃ HÓA BIẾN TOÀN CỤC (DESIGN TOKENS TO CSS VARIABLES)

Toàn bộ các giá trị từ [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md) được khai báo thành biến CSS tại `src/index.css` để Tailwind CSS v4 và các component sử dụng trực tiếp:

```css
:root {
  /* --- Colors: Brand & Accent --- */
  --color-primary: #cc785c;
  --color-primary-active: #a9583e;
  --color-primary-disabled: #e6dfd8;
  --color-accent-teal: #5db8a6;
  --color-accent-amber: #e8a55a;

  /* --- Colors: Ink & Text --- */
  --color-ink: #141413;
  --color-body-strong: #252523;
  --color-body: #3d3d3a;
  --color-muted: #6c6a64;
  --color-muted-soft: #8e8b82;
  --color-on-primary: #ffffff;
  --color-on-dark: #faf9f5;
  --color-on-dark-soft: #a09d96;

  /* --- Colors: Surfaces --- */
  --color-canvas: #faf9f5;
  --color-surface-soft: #f5f0e8;
  --color-surface-card: #efe9de;
  --color-surface-cream-strong: #e8e0d2;
  --color-surface-dark: #181715;
  --color-surface-dark-elevated: #252320;
  --color-surface-dark-soft: #1f1e1b;

  /* --- Colors: Hairlines & Borders --- */
  --color-hairline: #e6dfd8;
  --color-hairline-soft: #ebe6df;

  /* --- Colors: Semantic Status --- */
  --color-success: #5db872;
  --color-warning: #d4a017;
  --color-error: #c64545;

  /* --- Typography Families --- */
  --font-display: "Copernicus", "Tiempos Headline", "Cormorant Garamond", Georgia, serif;
  --font-sans: "StyreneB", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;

  /* --- Border Radius Scale --- */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;     /* Nút bấm, input */
  --radius-lg: 12px;    /* Khung thẻ, card nội dung */
  --radius-xl: 16px;    /* Card minh họa lớn */
  --radius-pill: 9999px;/* Badges, category pills */
}
```

---

## 3. MẪU THIẾT KẾ COMPONENT HỌC THUẬT (ACADEMIC COMPONENT PATTERNS)

### 3.1. Nút Bấm Chính & Phụ (Button Variants)
* **`button-primary` (Hành động then chốt: Tạo phiên, Tải PDF, Gửi câu hỏi):**
  - Nền: `var(--color-primary)` (`#cc785c`).
  - Chữ: `var(--color-on-primary)` (`#ffffff`), phông `font-sans`, cỡ `14px`, trọng số `500` (`font-medium`).
  - Bo góc: `var(--radius-md)` (`8px`), chiều cao cố định `40px`, padding ngang `20px`.
  - Hiệu ứng tương tác: Hover chuyển sang `var(--color-primary-active)` (`#a9583e`). Trạng thái vô hiệu hóa dùng nền `var(--color-primary-disabled)` (`#e6dfd8`).
* **`button-secondary` (Hành động phụ: Hủy, Đóng, Lọc):**
  - Nền: `var(--color-surface-soft)` (`#f5f0e8`), viền 1px `var(--color-hairline)` (`#e6dfd8`).
  - Chữ: `var(--color-ink)` (`#141413`).
* **`button-icon-circular` (Thu phóng PDF, Xoay trang, Đóng tab):**
  - Kích thước: `36px x 36px`, bo tròn hoàn toàn (`rounded-full`), nền trong suốt hoặc `var(--color-surface-soft)`.

---

### 3.2. Không Gian Đọc PDF (PDF Workspace Viewport)
* **Thanh Tab Tài Liệu (DocumentTabBar):**
  - Chiều cao: `48px`, viền đáy 1px `var(--color-hairline)`.
  - Tab không chọn: Nền trong suốt, chữ `var(--color-muted)` (`#6c6a64`).
  - Tab đang chọn: Nền `var(--color-surface-cream-strong)` (`#e8e0d2`), chữ `var(--color-ink)`, bo góc `var(--radius-sm)` (`6px`).
* **Lớp Phủ Bounding Box (BoundingBoxOverlay):**
  - Viền khung: 1.5px solid `var(--color-accent-amber)` (`#e8a55a`).
  - Nền mờ: `rgba(232, 165, 90, 0.18)` (hòa quyện tuyệt đối trên nền giấy kem).
  - Khi hover hoặc active: Chuyển viền sang `var(--color-primary)` (`#cc785c`) kèm hiệu ứng sáng viền nhẹ.

---

### 3.3. Khung Đối Thoại Trợ Lý AI (Socratic Mentor Chat Panel)
* **Khung Tin Nhắn (Turn Cards):**
  - Lượt hỏi của người dùng: Thẻ nền `var(--color-surface-soft)` (`#f5f0e8`), bo góc `var(--radius-lg)` (`12px`), padding `16px 20px`.
  - Lượt trả lời của AI: Nền `var(--color-canvas)` (`#faf9f5`), chữ `var(--color-body)` (`#3d3d3a`), tiêu đề h3/h4 dùng phông `font-display` serif trang nhã.
* **Khối Mã Nguồn & Công Thức Toán (Code & Formula Blocks):**
  - Tuân thủ mặt sàn tối: Nền `var(--color-surface-dark)` (`#181715`), viền 1px `var(--color-surface-dark-elevated)` (`#252320`), bo góc `var(--radius-md)`.
  - Chữ mã nguồn: Phông `var(--font-mono)` (`JetBrains Mono`), cỡ `14px`, chữ màu sáng `var(--color-on-dark)` (`#faf9f5`).
* **Huy Hiệu Trích Dẫn (Citation Badge):**
  - Kiểu dáng: `badge-pill` bo tròn 9999px, padding `4px 10px`.
  - Nền: `var(--color-surface-card)` (`#efe9de`), viền 1px `var(--color-hairline)`.
  - Chữ: `var(--color-primary)` (`#cc785c`), phông `caption-uppercase` cỡ `12px` đậm `font-medium`, letter-spacing `0.5px`.

---

### 3.4. Cửa Sổ Nhập Liệu & Soạn Thảo (Text Input Box)
* Nền ô nhập: `var(--color-canvas)` (`#faf9f5`) hoặc `var(--color-surface-soft)`.
* Viền tĩnh: 1px `var(--color-hairline)` (`#e6dfd8`), bo góc `var(--radius-md)` (`8px`).
* Viền Focus: 1.5px `var(--color-primary)` (`#cc785c`), không dùng viền xanh blue của trình duyệt mặc định (`outline: none`).
* Chữ placeholder: `var(--color-muted-soft)` (`#8e8b82`).

---

## 4. QUY TẮC "NÊN LÀM" VÀ "KHÔNG ĐƯỢC LÀM" (DO'S AND DON'TS)

### Do (Bắt Buộc Thực Hiện):
1. **Luôn dùng nền giấy kem `--color-canvas` (`#faf9f5`)** làm nền chính cho toàn bộ ứng dụng đọc sách và dashboard.
2. **Áp dụng tỷ lệ chia phân cấp Typography:** Tiêu đề lớn (h1, h2, tiêu đề modal, tên bài báo) dùng phông Serif (`Copernicus` / `Tiempos` / `Cormorant Garamond`) với trọng số mảnh vừa phải (weight 400-500) và khoảng cách chữ âm (`tracking-tight`).
3. **Giữ độ cao bo góc phân tầng nhất quán:** 8px cho thành phần tương tác (nút bấm, ô nhập), 12px cho các thẻ nội dung (Card, Modal), 9999px cho huy hiệu trích dẫn (Badges).
4. **Dùng hairline mỏng 1px (`#e6dfd8`)** để phân tách các khu vực thay vì dùng bóng đổ rực rỡ (Drop Shadows).

### Don't (Tuyệt Đối Cấm):
1. **Không sử dụng nền trắng tinh `#ffffff` toàn trang** hoặc màu xám công nghệ lạnh (`slate-100`, `gray-100`).
2. **Không sử dụng màu xanh dương chuẩn (Blue `#2563eb` hoặc Cyan)** cho các nút bấm hành động chính (Primary CTA bắt buộc dùng San hô Coral `#cc785c`).
3. **Không in đậm quá mức (Bold 700/800/900)** trên các tiêu đề phông Serif, làm mất đi tính trang nhã và nét thanh mảnh học thuật.
4. **Không dùng bóng đổ nổi khối nặng nề (Heavy Drop Shadows):** Chiều sâu giao diện được tạo ra từ sự tương phản giữa các mảng màu phẳng (Color-blocking), không lạm dụng shadow nhiều tầng.
