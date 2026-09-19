# Kế Hoạch Kỹ Thuật Chi Tiết: Xây Dựng Landing Page Cho Dự Án VeriScholar

> **Target:** Landing Page cho Project VeriScholar  
> **Trạng thái:** Chờ phê duyệt (Pending Approval) — Tuyệt đối chưa viết mã nguồn  
> **Đề xuất Git Branch:** `feat/fe-landing-page`  
> **Tài liệu tham chiếu:** [PRD.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md), [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md), [techstack-frontend.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/techstack-frontend.md), [directory-structure.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/directory-structure.md), [coding-standards.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/coding-standards.md), [design-system-integration.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/design-system-integration.md), [design-api.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md), [swagger.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/swagger.md)

---

## 1. MỤC TIÊU & TỔNG QUAN TARGET (TARGET OVERVIEW)

### 1.1. Mục Tiêu Kỹ Thuật & Nghiệp Vụ
Landing Page của VeriScholar không đơn thuần là một trang giới thiệu tiếp thị (marketing brochure), mà là **cửa ngõ truyền tải triết lý học thuật nhân văn (Warm-Canvas Editorial)** và **chứng minh năng lực công nghệ độc bản** của VeriScholar:
1. **Truyền tải định vị sản phẩm:** Nền tảng Trợ lý AI Hỗ trợ Nghiên cứu và Soạn thảo Bài báo Khoa học hàng đầu, cam kết **Triệt tiêu 100% Ảo giác (Zero Hallucination)** thông qua Bounding Box trực quan và mô hình Socratic Mentor.
2. **Trải nghiệm tương tác sống động (Interactive In-Place Demo):** Người dùng có thể trực tiếp tương tác với một bài báo khoa học mẫu (mẫu bài chuẩn IEEE 2 cột), nhấp vào các huy hiệu trích dẫn `[Paper • Trang • BBox]` để chứng kiến khung highlight viền vàng nhảy chính xác đến đoạn bằng chứng ngay trên Landing Page mà chưa cần đăng ký/đăng nhập.
3. **Tuân thủ 100% Design System gốc (DESIGN.md):** Nền giấy kem Canvas (`#faf9f5`), nút San hô ấm Coral (`#cc785c`), mặt sàn sản phẩm công nghệ Dark Navy (`#181715`), đường viền tóc Hairline mỏng 1px (`#e6dfd8`), và cặp phông chữ đối xứng Display Serif (Copernicus / Cormorant Garamond) + Humanist Sans (StyreneB / Inter) + JetBrains Mono.
4. **Hiệu năng tải trang cực đại (FCP < 0.8s, LCP < 1.2s, 60fps Smooth Interaction):** Không tải toàn bộ thư viện PDF.js (nặng > 500KB) trên Landing Page; sử dụng kỹ thuật Lightweight Vector Canvas Mockup có ma trận tọa độ chuẩn xác để hiển thị demo PDF siêu tốc.

---

### 1.2. Đề Xuất Git Branch Quy Chuẩn
* **Tên nhánh đề xuất:** `feat/fe-landing-page`
* **Quy chuẩn commit:** `[web] feat: implement editorial landing page with interactive demo and design system`

---

### 1.3. Rà Soát Biến Môi Trường Vite Cần Thiết (`VITE_...`)
Qua rà soát tệp `.env.example` hiện tại của dự án (chỉ chứa cấu hình hạ tầng backend PostgreSQL & Redis), ứng dụng Frontend `apps/web` cần bổ sung các biến môi trường Vite sau để người dùng cập nhật vào `.env.example` và `.env` cục bộ:

```bash
# ==============================================================================
# VeriScholar Frontend Client Configuration (apps/web)
# ==============================================================================

# Địa chỉ máy chủ Backend API (FastAPI)
VITE_API_BASE_URL=http://localhost:8000

# Tiền tố đường dẫn API phiên bản 1
VITE_API_PREFIX=/api/v1

# Tên tiêu đề ứng dụng hiển thị trên trình duyệt
VITE_APP_TITLE="VeriScholar — Nền tảng AI Nghiên cứu & Soạn thảo Khoa học"

# Cờ bật/tắt chế độ Mock Demo nội bộ khi Backend chưa khởi chạy (Fallback an toàn)
VITE_ENABLE_MOCK_DEMO=true

# Giới hạn dung lượng tệp PDF tải lên trực tiếp từ Landing Page (Bytes, 50MB)
VITE_MAX_UPLOAD_SIZE_BYTES=52428800
```

---

### 1.4. Bảng Phân Tích Đánh Đổi Kỹ Thuật (Engineering Trade-offs)

| Hạng mục quyết định | Phương án A (Bị loại trừ) | Phương án B Lựa chọn (VeriScholar Production) | Lý do kỹ thuật & Đánh đổi (Trade-off Rationale) |
| :--- | :--- | :--- | :--- |
| **PDF Rendering trên Landing Demo** | Nạp toàn bộ `pdfjs-dist` + PDF Web Worker để tải PDF thật. | **Sử dụng Lightweight Scalable Vector/DOM Page Simulator** với ma trận tỷ lệ `[x0, y0, x1, y1, page]`. | **Đánh đổi:** Không render được file PDF bất kỳ ngoài demo.<br>**Lợi ích sống còn:** Giảm bundle size từ ~800KB xuống dưới 25KB, First Contentful Paint (FCP) giảm từ 2.4s xuống 0.6s, đạt chuẩn Google PageSpeed 98+. |
| **Styling Engine** | Tailwind CSS v3 hoặc MUI / Emotion runtime CSS-in-JS. | **Tailwind CSS v4** với cấu hình Semantic CSS Variables thuần khiết. | Triệt tiêu 100% JavaScript runtime overhead, biên dịch CSS siêu nhỏ (< 15KB gzipped), hỗ trợ native `@theme` directives trong Vite 8. |
| **State Quản lý Demo** | Nhúng toàn bộ Redux Toolkit hoặc React Context toàn trang. | **Zustand `useLandingStore`** với fine-grained selectors. | Dung lượng < 1.2KB, độc lập không gây re-render các section tĩnh lân cận (Hero, Matrix, Footer) khi người dùng đổi tab demo. |
| **Typography Display Font** | Sử dụng Google Fonts `Playfair Display` hoặc `Merriweather`. | **Cormorant Garamond / EB Garamond** (thay thế mã nguồn mở sát nhất cho Copernicus theo [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md)). | Giữ trọn vẹn nét thanh tao học thuật (weight 400, negative tracking -1px), không bị nặng nề hoặc "thương mại hóa" như các phông slab serif đại trà. |

---

## 2. TRỤ CỘT 1: ĐẶC TẢ UI/UX & DESIGN SYSTEM (DESIGN.MD SPECIFICATION)

### 2.1. Bản Đồ Mã Hóa Semantic Tokens Chuẩn Tuyệt Đối DESIGN.md

Toàn bộ giao diện Landing Page tuân thủ triệt để các biến CSS và Semantic Tokens đã chuẩn hóa:

```css
/* apps/web/src/index.css */
@import "tailwindcss";

@layer base {
  :root {
    /* Brand & Accent */
    --color-primary: #cc785c;             /* San hô ấm - Primary CTA */
    --color-primary-active: #a9583e;      /* San hô đậm khi bấm / active */
    --color-primary-disabled: #e6dfd8;    /* San hô nhạt trạng thái disabled */
    --color-accent-teal: #5db8a6;         /* Xanh ngọc - trạng thái kết nối */
    --color-accent-amber: #e8a55a;        /* Hổ phách ấm - Bounding Box Highlight */

    /* Canvas & Surfaces */
    --color-canvas: #faf9f5;              /* Nền giấy kem ấm áp (Page Floor) */
    --color-surface-soft: #f5f0e8;        /* Nền dải phân cách mềm */
    --color-surface-card: #efe9de;        /* Thẻ tính năng 3-up, card kem */
    --color-surface-cream-strong: #e8e0d2;/* Thẻ chọn active, viền tab */
    --color-surface-dark: #181715;        /* Mặt sàn sản phẩm tối (Code/Terminal/Mockup) */
    --color-surface-dark-elevated: #252320;/* Thẻ nổi trên mặt sàn tối */
    --color-surface-dark-soft: #1f1e1b;   /* Nền khối mã bên trong card tối */

    /* Typography Ink & Text */
    --color-ink: #141413;                 /* Tiêu đề chính, văn bản đậm */
    --color-body-strong: #252523;         /* Đoạn văn dẫn dắt (Lead text) */
    --color-body: #3d3d3a;                /* Văn bản nội dung mặc định */
    --color-muted: #6c6a64;               /* Phụ đề, nhãn phụ, liên kết mờ */
    --color-muted-soft: #8e8b82;          /* Chú thích bản quyền, fine-print */
    --color-on-primary: #ffffff;          /* Chữ trắng trên nền san hô */
    --color-on-dark: #faf9f5;             /* Chữ kem sáng trên mặt sàn tối */
    --color-on-dark-soft: #a09d96;        /* Chữ mờ trên nền tối */

    /* Hairline & Borders */
    --color-hairline: #e6dfd8;            /* Đường kẻ tóc 1px trên nền kem */
    --color-hairline-soft: #ebe6df;       /* Phân cách cực nhẹ */

    /* Status Semantics */
    --color-success: #5db872;
    --color-warning: #d4a017;
    --color-error: #c64545;

    /* Typography Families */
    --font-display: "Copernicus", "Tiempos Headline", "Cormorant Garamond", Georgia, serif;
    --font-sans: "StyreneB", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: "JetBrains Mono", ui-monospace, monospace;

    /* Border Radius */
    --radius-xs: 4px;
    --radius-sm: 6px;
    --radius-md: 8px;     /* Nút bấm, ô nhập */
    --radius-lg: 12px;    /* Card tính năng, mockup card */
    --radius-xl: 16px;    /* Hero container, marquee */
    --radius-pill: 9999px;/* Badges, category pills */
  }
}
```

---

### 2.2. Nhịp Điệu Dải Mặt Sàn Luân Chuyển (Alternating Surface Band Rhythm)

Theo đúng nguyên tắc bất biến tại mục 5.2 của [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md): *"Không bao giờ lặp lại cùng một surface mode ở hai band liên tiếp"*. Cấu trúc Landing Page được thiết lập theo nhịp điệu hoàn hảo:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ BAND 1: Cream Canvas (#faf9f5)                                              │
│ • Top Navigation (Logo radial-spike + Menu + Sign In + "Dùng thử ngay" CTA)  │
│ • Hero Section: Headline Serif display-xl + Lead Text + Dual CTAs           │
│ • Interactive In-Place Demo Preview (PDF Viewer bên trái + AI Chat bên phải)│
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ BAND 2: Light Cream Cards (#efe9de) trên Surface Soft (#f5f0e8)             │
│ • Grid 3 Tính Năng Cốt Lõi (3-Up Feature Cards):                             │
│   1. Đọc Sâu & Bounding Box Chuẩn Xác [x0, y0, x1, y1, page]                │
│   2. Socratic Pedagogical Mentorship (Chống nịnh hót, kiểm tra tiền đề)     │
│   3. SAFE Fact-Checking & Self-Healing LaTeX Sandbox                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ BAND 3: Dark Navy Product Surfaces (#181715)                                │
│ • Showcase Không Gian Làm Việc Thực Tế (Workspace Chrome Mockup):           │
│   - Split-Pane tương tác mượt mà giữa PDF Paper và Socratic Assistant       │
│   - Cửa sổ Code LaTeX & Công thức KaTeX render trên nền surface-dark-soft   │
│   - Bảng mạch suy luận thời gian thực (Real-time Reasoning Stream)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ BAND 4: Cream Canvas (#faf9f5)                                              │
│ • Ma Trận So Sánh Chuẩn Học Thuật (Academic Comparison Matrix):             │
│   VeriScholar vs Perplexity vs NotebookLM vs ChatPDF vs Elicit              │
│ • Quy Trình 4 Bước Nghiên Cứu Khép Kín (4-Step Workflow Pipeline)           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ BAND 5: Full-Bleed Coral Band (#cc785c)                                     │
│ • Pre-Footer CTA Band: Headline Serif display-sm trên nền San hô rực rỡ     │
│ • Nút bấm tương phản Canvas (#faf9f5) "Bắt đầu Nghiên cứu Ngay — Miễn phí"  │
│ • Cam kết Zero-Retention & Không dùng dữ liệu để huấn luyện mô hình         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ BAND 6: Dark Navy Footer (#181715)                                          │
│ • 4 Cột Điều Hướng: Sản Phẩm, Khoa Học & Nghiên Cứu, Tài Nguyên, Pháp Lý    │
│ • Biểu tượng Anthropic Radial-Spike + Wordmark VeriScholar                  │
│ • Chứng nhận Bảo mật & Quyền riêng tư bản thảo                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.3. Danh Mục Các Component UI & Feature Cần Xây Dựng Mới

```text
apps/web/src/
├── components/
│   ├── ui/                         # Atomic Headless Primitives (shadcn/Radix)
│   │   ├── button.tsx              # Variants: primary (coral), secondary (cream), outline, ghost
│   │   ├── badge.tsx               # Variants: default, coral, amber, pill (9999px)
│   │   ├── card.tsx                # Variants: canvas, card-cream (#efe9de), dark (#181715)
│   │   ├── dialog.tsx              # Radix Dialog cho Quick Start & Video Demo Modal
│   │   ├── tooltip.tsx             # Radix Tooltip cho giải thích thuật ngữ học thuật
│   │   ├── scroll-area.tsx         # Custom scrollbar cho demo transcript
│   │   └── separator.tsx           # Hairline divider 1px (#e6dfd8)
│   │
│   └── shared/
│       ├── AcademicLogo.tsx        # Biểu tượng 4-spoke radial-spike + chữ VeriScholar
│       └── BboxHighlight.tsx       # Khung viền Bounding Box tỷ lệ động [0.0, 1.0]
│
└── features/
    └── landing/                    # Module Feature Landing Page độc lập
        ├── components/
        │   ├── LandingNavbar.tsx       # Top Nav cao 64px, pinned sticky, backdrop-blur
        │   ├── HeroSection.tsx         # Headline display-xl, CTA buttons, Trust Badges
        │   ├── InteractiveDemo.tsx     # Bộ khung demo trực tiếp 2 nửa tương tác
        │   ├── DemoPaperViewer.tsx     # Trình mô phỏng bài báo IEEE 2 cột kèm Bounding Box
        │   ├── DemoChatPanel.tsx       # Khung đối thoại Socratic AI kèm Citation Badges
        │   ├── FeatureGridSection.tsx  # 3-up Cards với typography title-md
        │   ├── ProductChromeShowcase.tsx# Khung mô phỏng sản phẩm Dark Navy (#181715)
        │   ├── ComparisonMatrix.tsx    # Bảng đối sánh tính năng với các nền tảng AI khác
        │   ├── WorkflowSteps.tsx       # 4 bước: Nạp bài -> Đọc sâu -> Đúc kết -> Soạn thảo
        │   ├── CallToActionSection.tsx # Dải banner full-bleed San hô (#cc785c)
        │   ├── LandingFooter.tsx       # Footer tối màu (#181715) chuẩn editorial
        │   └── QuickUploadModal.tsx    # Modal kéo thả PDF nhanh trực tiếp từ Hero
        │
        ├── hooks/
        │   ├── useInteractiveDemo.ts   # Logic chuyển tab demo và kích hoạt highlight
        │   └── useDemoStream.ts        # Hiệu ứng typewriter mượt mà qua rAF cho câu trả lời
        │
        └── types/
            └── landing.ts              # Kiểu dữ liệu TypeScript cho bài mẫu, metrics, FAQ
```

---

### 2.4. Đặc Tả 5 Trạng Thái Giao Diện Chuẩn Mực (5 Interface States)

Mọi thành phần tương tác trên Landing Page đều được thiết kế đầy đủ 5 trạng thái theo tiêu chuẩn kỹ thuật:

1. **Default State (Mặc định):**
   - Nút San hô Primary: Nền `#cc785c`, chữ trắng, không đổ bóng dày, bo góc 8px.
   - Thẻ tính năng: Nền `#efe9de`, viền hairline 1px `#e6dfd8`, tiêu đề Serif weight 400.
   - Bounding Box trên bài báo mẫu: Viền mỏng 1.5px `#e8a55a`, nền mờ `rgba(232, 165, 90, 0.12)`.

2. **Loading / Skeleton State (Đang tải):**
   - Áp dụng hiệu ứng Shimmer trên dải màu kem ấm: Nền skeleton `#e8e0d2` chuyển sắc nhẹ nhàng sang `#f5f0e8` (tuyệt đối không dùng màu xám lạnh `bg-gray-200`).
   - Giữ nguyên kích thước khung hộp (Zero Cumulative Layout Shift - CLS = 0).

3. **Empty State (Rỗng):**
   - Áp dụng trong khung Demo khi người dùng xóa trắng câu hỏi hoặc chọn bài báo chưa có trích dẫn: Hiển thị icon bản thảo mở kèm thông điệp gợi ý trang nhã: *"Chọn một câu hỏi mẫu hoặc nhấp vào đoạn văn trên bài báo để bắt đầu đối thoại."*

4. **Error State (Lỗi & Khôi phục):**
   - Khi tệp PDF kéo thả không hợp lệ (vượt 50MB hoặc file mã hóa): Khung upload chuyển viền `border-error` (`#c64545`), hiển thị mã lỗi `UNSUPPORTED_PDF_FORMAT`, kèm nút bấm `[Thử lại]` khôi phục trạng thái ban đầu.

5. **Active / Highlight State (Kích hoạt):**
   - Khi người dùng di chuột hoặc nhấp vào một Citation Badge: Huy hiệu chuyển sang màu San hô `#cc785c`, đồng thời Bounding Box tương ứng trên trang bài báo bên cạnh lập tức chuyển sang viền đậm 2px `#cc785c` kèm hiệu ứng phát sáng nhẹ `box-shadow: 0 0 12px rgba(204, 120, 92, 0.35)`.

---

### 2.5. Quy Chuẩn Tiếp Cận Giao Diện (WAI-ARIA Accessibility Standards)

* **Điều hướng bàn phím hoàn chỉnh:** Toàn bộ liên kết menu, nút bấm CTA và các nút demo có thể duyệt bằng phím `Tab` và kích hoạt bằng `Enter` hoặc `Space`.
* **Focus Indicator rõ ràng:** Viền focus hiển thị rõ nét 2px màu Coral `#cc785c` với offset 2px, loại bỏ viền xanh mặc định của trình duyệt.
* **Hộp thoại có Focus Trap:** `QuickUploadModal` và `VideoDemoModal` tự động bắt tiêu điểm khi mở ra và trả tiêu điểm về nút kích hoạt khi nhấn `Esc`.
* **Trình đọc màn hình (Screen Readers):**
  - Khung Bounding Box có thuộc tính `role="region"` và `aria-label="Đoạn văn trích dẫn bằng chứng tại trang 4"`.
  - Các nút icon-only (đóng modal, thu phóng) bắt buộc có `aria-label` chi tiết.
  - Các huy hiệu trích dẫn có `aria-haspopup="true"` và `aria-expanded="false/true"`.

---

## 3. TRỤ CỘT 2: DATA LAYER, STATE MANAGEMENT & TYPESCRIPT CONTRACTS

### 3.1. Hợp Đồng Kiểu Dữ Liệu TypeScript Khép Kín 1-1 Với Backend (`src/types/`)

Tuyệt đối không sử dụng `any`. Mọi phản hồi và dữ liệu demo đều tuân thủ chặt chẽ định dạng API Envelopes đã định nghĩa tại [design-api.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) và [swagger.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/swagger.md):

```typescript
// apps/web/src/types/api.ts
export interface ApiMeta {
  request_id: string;
  timestamp: string;
}

export interface SingleResponse<T> {
  success: true;
  data: T;
  meta: ApiMeta;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  field?: string | null;
  action?: string | null;
}

export interface ErrorResponse {
  success: false;
  error: ApiErrorDetail;
  meta: ApiMeta;
}

// Bounding Box Coordinate: [x0, y0, x1, y1, page]
// Chuẩn hóa: 0.0 <= x0 < x1 <= 1.0, 0.0 <= y0 < y1 <= 1.0, page >= 1
export type BoundingBox = [number, number, number, number, number];

export interface PageDimensions {
  width_pt: number;
  height_pt: number;
}
```

```typescript
// apps/web/src/types/landing.ts
import { BoundingBox, PageDimensions } from "./api";

export interface DemoCitation {
  id: string;
  label: string; // Ví dụ: "Vaswani et al. • Tr. 6"
  paper_title: string;
  page: number;
  bounding_box: BoundingBox;
  quote_text: string;
  fact_check_status: "supported" | "contradicted" | "unverified";
}

export interface DemoTurn {
  id: string;
  user_query: string;
  ai_thought?: string; // Khối suy luận Thinking Block
  ai_answer_markdown: string;
  citations: DemoCitation[];
  presupposition_corrected: boolean; // Cờ uốn nắn tiền đề Socratic
}

export interface DemoPaper {
  id: string;
  title: string;
  authors: string;
  venue_year: string;
  page_dimensions: PageDimensions;
  rotation_deg: 0 | 90 | 180 | 270;
  sample_turns: DemoTurn[];
}

export interface FeatureMetric {
  metric_value: string;
  metric_label: string;
  description: string;
}
```

---

### 3.2. Phân Tách Quản Lý Trạng Thái: TanStack Query vs Zustand Store

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHÂN TÁCH TRẠNG THÁI FRONTEND                         │
├──────────────────────────────────────┬──────────────────────────────────────┤
│    SERVER CACHE (@tanstack/react-query)│         CLIENT UI STATE (Zustand)    │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Kiểm tra tình trạng Server Health  │ • Tab bài báo Demo đang chọn         │
│   (GET /health)                      │ • Citation / Bounding Box đang active │
│ • Tải lên tài liệu PDF nhanh         │ • Trạng thái mở Modal (Upload/Video) │
│   (POST /api/v1/documents)           │ • Bộ đệm Typewriter rAF Animation    │
│ • Kiểm tra tiến trình Ingestion      │ • Trạng thái đóng/mở Mobile Menu     │
│   (GET /api/v1/documents/{id}/status)│ • Vị trí cuộn trang để kích hoạt Nav  │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

#### Cài đặt Zustand Store cho Landing Page:
```typescript
// apps/web/src/features/landing/stores/useLandingStore.ts
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { DemoCitation } from "@/types/landing";

interface LandingState {
  activePaperId: string;
  activeCitationId: string | null;
  activeCitation: DemoCitation | null;
  isUploadModalOpen: boolean;
  isVideoModalOpen: boolean;
  isMobileMenuOpen: boolean;

  // Actions
  setActivePaperId: (paperId: string) => void;
  setActiveCitation: (citation: DemoCitation | null) => void;
  setUploadModalOpen: (open: boolean) => void;
  setVideoModalOpen: (open: boolean) => void;
  setMobileMenuOpen: (open: boolean) => void;
}

export const useLandingStore = create<LandingState>()(
  devtools((set) => ({
    activePaperId: "demo-paper-attention",
    activeCitationId: null,
    activeCitation: null,
    isUploadModalOpen: false,
    isVideoModalOpen: false,
    isMobileMenuOpen: false,

    setActivePaperId: (paperId) =>
      set({ activePaperId: paperId, activeCitationId: null, activeCitation: null }),
    setActiveCitation: (citation) =>
      set({ activeCitationId: citation?.id ?? null, activeCitation: citation }),
    setUploadModalOpen: (open) => set({ isUploadModalOpen: open }),
    setVideoModalOpen: (open) => set({ isVideoModalOpen: open }),
    setMobileMenuOpen: (open) => set({ isMobileMenuOpen: open }),
  }))
);
```

---

### 3.3. Xử Lý Zero-Jank Typewriter Buffer Qua RequestAnimationFrame (rAF)

Để mang lại cảm giác sinh văn bản thời gian thực mượt mà tựa như LLM Streaming thực tế mà không gây bão re-render (Zero-Jank Engine):

```typescript
// apps/web/src/features/landing/hooks/useDemoStream.ts
import { useState, useRef, useCallback, useEffect } from "react";

export function useDemoStream(fullText: string, speedMs: number = 25) {
  const [displayedText, setDisplayedText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const indexRef = useRef(0);
  const rafIdRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);

  const startStream = useCallback(() => {
    setDisplayedText("");
    setIsStreaming(true);
    indexRef.current = 0;
    lastTimeRef.current = performance.now();

    const loop = (currentTime: number) => {
      const delta = currentTime - lastTimeRef.current;
      if (delta >= speedMs) {
        lastTimeRef.current = currentTime;
        indexRef.current = Math.min(indexRef.current + 2, fullText.length);
        setDisplayedText(fullText.slice(0, indexRef.current));
      }

      if (indexRef.current < fullText.length) {
        rafIdRef.current = requestAnimationFrame(loop);
      } else {
        setIsStreaming(false);
        rafIdRef.current = null;
      }
    };

    rafIdRef.current = requestAnimationFrame(loop);
  }, [fullText, speedMs]);

  useEffect(() => {
    return () => {
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
      }
    };
  }, []);

  return { displayedText, isStreaming, startStream };
}
```

---

## 4. TRỤ CỘT 3: KIẾN TRÚC COMPONENT & TÍCH HỢP BỐ CỤC

### 4.1. Phân Tầng Container (Smart) vs Presentation (Dumb) Components

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONTAINER (SMART) COMPONENTS                          │
│   • LandingPageContainer.tsx: Kết nối Routing, Metadata, Analytics          │
│   • InteractiveDemoContainer.tsx: Đọc useLandingStore, điều phối sự kiện     │
│   • QuickUploadContainer.tsx: Gọi API Mutation upload_document               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Truyền props thuần túy (Dumb Data)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION (DUMB) COMPONENTS                          │
│   • LandingNavbar.tsx: Render thanh menu, logo, CTA buttons                 │
│   • HeroSection.tsx: Hiển thị Typography tiêu đề, CTA, Trust Badges          │
│   • DemoPaperViewer.tsx: Vẽ layout 2 cột trang bài báo, render BBox Overlay  │
│   • DemoChatPanel.tsx: Hiển thị bong bóng chat, thinking block, badge        │
│   • FeatureGridSection.tsx: Hiển thị 3 card tính năng                       │
│   • ProductChromeShowcase.tsx: Render giao diện Dark Navy (#181715)         │
│   • ComparisonMatrix.tsx: Bảng so sánh 5 cột chuẩn học thuật                │
│   • LandingFooter.tsx: 4 cột link và footer tối màu                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4.2. Thuật Toán Chuyển Đổi Tọa Độ Bounding Box Không Gian (Spatial Scaler)

Để khung viền vàng highlight nằm khớp chính xác từng milimet trên trang bài báo mẫu tại bất kỳ kích thước màn hình nào (Desktop, Tablet, Mobile) mà không bị méo lệch:

```typescript
// apps/web/src/lib/bounding-box-scaler.ts
import { BoundingBox, PageDimensions } from "@/types/api";

export interface ComputedBoxStyle {
  left: string;
  top: string;
  width: string;
  height: string;
}

/**
 * Chuyển đổi tọa độ chuẩn hóa [x0, y0, x1, y1, page] thành tọa độ phần trăm CSS
 * Tuyệt đối bất biến với kích thước khung hình và độ phân giải màn hình.
 */
export function computeBoundingBoxStyle(
  bbox: BoundingBox,
  _dimensions: PageDimensions
): ComputedBoxStyle {
  const [x0, y0, x1, y1] = bbox;

  // Rào chắn bảo vệ dữ liệu (Spatial Bounds Guard)
  const clampedX0 = Math.max(0, Math.min(x0, 1));
  const clampedY0 = Math.max(0, Math.min(y0, 1));
  const clampedX1 = Math.max(clampedX0, Math.min(x1, 1));
  const clampedY1 = Math.max(clampedY0, Math.min(y1, 1));

  return {
    left: `${(clampedX0 * 100).toFixed(2)}%`,
    top: `${(clampedY0 * 100).toFixed(2)}%`,
    width: `${((clampedX1 - clampedX0) * 100).toFixed(2)}%`,
    height: `${((clampedY1 - clampedY0) * 100).toFixed(2)}%`,
  };
}
```

---

### 4.3. Tích Hợp Vào Bảng Định Tuyến Ứng Dụng (`apps/web/src/app/routes.tsx`)

```tsx
// Cấu trúc phân luồng chuyển dịch từ Landing Page vào Không Gian Nghiên Cứu:
import { createBrowserRouter } from "react-router-dom";
import { LandingPageContainer } from "@/features/landing/components/LandingPageContainer";
// Lazy load các module nặng bên trong
const LibraryPage = React.lazy(() => import("@/features/library/components/LibraryPage"));
const ReaderWorkspace = React.lazy(() => import("@/features/reader/components/ReaderWorkspace"));

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPageContainer />,
  },
  {
    path: "/library",
    element: <LibraryPage />,
  },
  {
    path: "/sessions/:sessionId",
    element: <ReaderWorkspace />,
  },
]);
```

---

## 5. TRỤ CỘT 4: KẾ HOẠCH KIỂM THỬ ĐA TẦNG & VISUAL AUDIT (VERIFICATION PLAN)

Quy trình kiểm chuẩn chất lượng được thiết kế nghiêm ngặt theo 3 tầng bảo vệ:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TẦNG 1: UNIT & COMPONENT TESTS (Vitest + RTL)             │
│   • Test tính toán ma trận tọa độ Bounding Box (bounding-box-scaler.test.ts)│
│   • Test rAF Typewriter Buffer không gây rò rỉ bộ nhớ                       │
│   • Test tương tác nhấp Citation Badge cập nhật Zustand Store               │
│   • Test tính năng đóng/mở QuickUploadModal và Focus Trap                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TẦNG 2: END-TO-END TESTS (Playwright)                     │
│   • Kiểm tra luồng người dùng: Truy cập trang -> Nhấp Citation -> Highlight  │
│   • Kiểm tra tính năng kéo thả PDF tải lên -> Chuyển hướng vào Workspace    │
│   • Kiểm tra hiển thị responsive: Desktop (1440px), Tablet (768px), Mobile  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TẦNG 3: VISUAL & CONSOLE MCP AUDIT                       │
│   • chrome-devtools MCP: Kiểm tra Console Errors = 0, Network Requests OK   │
│   • puppeteer MCP: Chụp ảnh Snapshot kiểm tra tương phản màu & typography    │
│   • Context7 & Sequential Thinking: Rà soát hiệu năng render 60fps          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.1. Bộ Kịch Bản Kiểm Thử Đơn Vị (Vitest & React Testing Library)
1. `computeBoundingBoxStyle`:
   - Kiểm tra với tọa độ hợp lệ `[0.1, 0.2, 0.8, 0.5, 1]` -> Trả về `left: 10.00%`, `top: 20.00%`, `width: 70.00%`, `height: 30.00%`.
   - Kiểm tra ranh giới ngoại lệ: tọa độ âm hoặc lớn hơn 1.0 -> Tự động kẹp an toàn qua `clamp` trong khoảng `[0%, 100%]`.
2. `LandingNavbar`:
   - Kiểm tra render logo Anthropic radial-spike và wordmark VeriScholar.
   - Kiểm tra nút "Dùng thử ngay" có đường dẫn chính xác tới `/library` hoặc mở Quick Upload.
3. `InteractiveDemo`:
   - Mô phỏng người dùng nhấp vào Citation `[Vaswani et al. • Tr. 6]` -> Đảm bảo thẻ Bounding Box hiển thị class active `ring-2 ring-primary`.

---

### 5.2. Kịch Bản Kiểm Thử E2E (Playwright)
```typescript
// apps/web/tests/e2e/landing-page.spec.ts
import { test, expect } from "@playwright/test";

test.describe("VeriScholar Editorial Landing Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("hiển thị đúng tiêu đề Display Serif và nhịp điệu các band mặt sàn", async ({ page }) => {
    const h1 = page.locator("h1");
    await expect(h1).toBeVisible();
    await expect(h1).toContainText("Nền tảng Trợ lý AI Hỗ trợ Nghiên cứu");

    // Kiểm tra màu nền canvas chuẩn #faf9f5
    const body = page.locator("body");
    await expect(body).toHaveCSS("background-color", "rgb(250, 249, 245)");
  });

  test("tương tác nhấp Citation Badge kích hoạt Bounding Box tương ứng", async ({ page }) => {
    const citationBtn = page.locator('[data-testid="demo-citation-badge"]').first();
    await citationBtn.click();

    const activeBbox = page.locator('[data-testid="demo-bbox-highlight"][data-active="true"]');
    await expect(activeBbox).toBeVisible();
    await expect(activeBbox).toHaveCSS("border-color", "rgb(204, 120, 92)"); // Coral #cc785c
  });

  test("hộp thoại Quick Upload mở ra và bắt phím Esc an toàn", async ({ page }) => {
    await page.locator('[data-testid="hero-quick-upload-btn"]').click();
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();

    await page.keyboard.press("Escape");
    await expect(modal).not.toBeVisible();
  });
});
```

---

### 5.3. Quy Trình Visual & Console Inspection Với MCP Tools
* Sử dụng **`chrome-devtools` MCP**:
  - Khởi chạy phiên duyệt headless ở độ phân giải chuẩn 1440x900.
  - Lắng nghe sự kiện `Console.messageAdded`: **Bắt buộc số lượng lỗi Console Error = 0**.
  - Kiểm tra tab Network: Tất cả các file tĩnh (phông chữ, logo SVG, icons) phải trả về mã `200 OK`, không phát sinh request lỗi `404 Not Found`.
* Sử dụng **`puppeteer` MCP**:
  - Chụp ảnh màn hình toàn trang (Full Page Screenshot) tại 3 điểm ngắt (Mobile 375px, Tablet 768px, Desktop 1440px).
  - So sánh trực quan màu sắc nút bấm Coral (`#cc785c`), màu nền giấy kem (`#faf9f5`) và đường kẻ tóc 1px (`#e6dfd8`) với các tiêu chuẩn đã định nghĩa tại [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md).

---

## 6. TRỤ CỘT 5: NGHIÊN CỨU & ĐỐI SÁNH QUỐC TẾ (BENCHMARKING)

### 6.1. Bảng Ma Trận So Sánh Các Sản Phẩm AI Học Thuật Hàng Đầu Thế Giới

| Tiêu chí Đánh giá | Claude.ai (Anthropic) | Perplexity.ai | Google NotebookLM | ChatPDF / Humata | **VeriScholar (Giải pháp của chúng ta)** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ngôn ngữ Thẩm mỹ (Aesthetic)** | **Warm-Canvas Editorial** (Đỉnh cao nhân văn) | Dark / Light Tech SaaS đại trà | Material You hiện đại | UI SaaS cơ bản, thô cứng | **Kế thừa 100% Warm-Canvas Editorial**, đậm chất hàn lâm thư tịch cổ điển kết hợp công nghệ cao. |
| **Bảo chứng Bằng chứng (Visual Grounding)** | Trích dẫn số dạng văn bản thuần túy | Huy hiệu web URL | Số trang trong tài liệu | Nhảy đến trang PDF thô | **Bounding Box chính xác tuyệt đối `[x0, y0, x1, y1, page]`** vẽ trực tiếp trên trang PDF gốc. |
| **Bảo vệ Bản quyền (Zero-Retention)** | Lưu trữ theo tài khoản | Lưu trữ cloud | Lưu trữ trong hệ sinh thái Google | Lưu trữ máy chủ bên thứ ba | **Zero Data Retention Guarantee:** Xóa vĩnh viễn tệp theo chuẩn CAS ACID, không dùng để train AI. |
| **Tư Duy Sư Phạm (Pedagogical Mentor)** | Dễ mắc hội chứng nịnh hót (Sycophancy) | Trả lời trực diện câu hỏi | Tóm tắt tổng quan | Trả lời dựa trên đoạn cắt ngẫu nhiên | **Socratic Mentor:** Tự động phát hiện và uốn nắn tiền đề sai lầm của người dùng trước khi trả lời. |
| **Công thức Toán & Bảng Biểu** | Hỗ trợ Markdown/LaTeX cơ bản | LaTeX cơ bản | Khó xem bảng vắt trang | Thường bị vỡ công thức nhiều dòng | **Composite Bounding Box & Table Stitching Layer** bảo toàn nguyên vẹn công thức LaTeX và bảng vắt trang. |
| **Nghiên Cứu Ngoại Tuyến (Offline Use)** | Yêu cầu kết nối mạng 100% | Yêu cầu kết nối mạng 100% | Yêu cầu kết nối mạng 100% | Yêu cầu kết nối mạng 100% | **Offline Research Bundle (.zip):** PDF nhúng ISO 32000-1 highlights + Master Lesson + Self-contained HTML. |

---

### 6.2. Đề Xuất Các Cải Tiến Tinh Tế (Micro-Interactions & Motion Design)

1. **Hiệu ứng "Paper Texture Soft Glow":** Khi người dùng di chuột trên các thẻ tính năng ở Band 2 (`surface-card` `#efe9de`), viền thẻ chuyển sắc nhẹ nhàng với một lớp viền mảnh `rgba(204, 120, 92, 0.2)` tạo cảm giác tờ giấy bài báo được nâng nhẹ trong tay.
2. **Keyboard Shortcut Hinting:** Bố trí các huy hiệu phím tắt trang nhã trên thanh tìm kiếm hoặc nút thử nghiệm (ví dụ: `[ ⌘K ]` hoặc `[ Esc ]`) giúp các nhà nghiên cứu chuyên nghiệp thao tác siêu tốc mà không cần rời tay khỏi bàn phím.
3. **Chớp Nháy Bounding Box Mượt Mà:** Khi nhấp vào huy hiệu trích dẫn, Bounding Box trên trang bài báo mẫu không nhảy đột ngột mà chuyển đổi mượt mà qua thuộc tính CSS `transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1)`.

---

## 7. RỦI RO KỸ THUẬT & BIỆN PHÁP PHÒNG NGỪA (RISKS & MITIGATIONS)

| Rủi ro Kỹ thuật | Mức độ | Biện pháp Phòng ngừa & Khắc phục |
| :--- | :---: | :--- |
| **Nghẽn Bundle Size do nạp thư viện toán/PDF** | Cao | Tuyệt đối không nạp `pdfjs-dist` và `katex` toàn phần vào bundle chính của Landing Page. Sử dụng Lightweight Vector Page Simulator viết bằng CSS/SVG thuần; chỉ lazy-load khi người dùng thực sự kích hoạt bản xem trước nâng cao. |
| **Xung đột phiên bản React 19 với các UI libraries** | Trung bình | Sử dụng các bản phân phối tương thích React 19 từ Radix UI Primitives và Tailwind CSS v4, không dùng các thư viện UI cũ phụ thuộc `findDOMNode` hoặc string refs. |
| **Lệch Bounding Box trên màn hình Mobile** | Trung bình | Sử dụng công thức chuyển đổi phần trăm độc lập kích thước `computeBoundingBoxStyle` kết hợp thuộc tính `aspect-ratio: [width_pt / height_pt]` để trang bài báo luôn giữ đúng tỷ lệ khổ giấy A4. |
| **Mất an toàn kiểu dữ liệu khi mở rộng API** | Thấp | Kiểm soát nghiêm ngặt qua CI/CD với `tsc -b --noEmit`, cấm tuyệt đối kiểu `any` theo chuẩn mục 1.1 của [coding-standards.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/coding-standards.md). |

---

## 8. LỘ TRÌNH TRIỂN KHAI 4 GIAI ĐOẠN (STEP-BY-STEP ROADMAP)

Sau khi Kế hoạch Kỹ thuật này được Người Dùng xem xét và chính thức phê duyệt bằng lệnh, quá trình lập trình mã nguồn sẽ được thực thi theo 4 bước tuần tự khép kín:

```text
Giai đoạn 1: Nền tảng Kiến trúc & Cấu hình Semantic Design Tokens (Phase 1)
  ├── 1.1. Cài đặt các thư viện phụ thuộc cốt lõi vào apps/web (tailwindcss v4, @radix-ui, lucide-react, zustand, @tanstack/react-query).
  ├── 1.2. Cấu hình các biến CSS Semantic Tokens chuẩn DESIGN.md tại src/index.css và thiết lập font Cormorant Garamond & Inter tại index.html.
  └── 1.3. Khởi tạo cấu trúc thư mục feature chuẩn: src/features/landing/{components, hooks, types, stores}.
  └── Kiểm chuẩn: pnpm --prefix apps/web exec tsc -b và pnpm --prefix apps/web lint sạch lỗi.

Giai đoạn 2: Xây dựng Bộ UI Primitives & Khung Bố Cục Tĩnh (Phase 2)
  ├── 2.1. Xây dựng các component UI hạt nhân: button, badge, card, dialog, separator, tooltip.
  ├── 2.2. Xây dựng LandingNavbar (Top Nav cao 64px, Sticky, Logo Anthropic Radial-Spike, Menu).
  ├── 2.3. Xây dựng HeroSection (Display-XL Serif h1, Lead paragraph, Coral CTA, Quick Start button).
  ├── 2.4. Xây dựng FeatureGridSection (3-up Cards) và ProductChromeShowcase (Dark Navy #181715).
  ├── 2.5. Xây dựng ComparisonMatrix (Bảng đối sánh 5 nền tảng), WorkflowSteps và LandingFooter.
  └── Kiểm chuẩn: Kiểm tra hiển thị responsive tại 375px, 768px, 1440px.

Giai đoạn 3: Hiện thực hóa Bộ Demo Tương Tác Sống Động & Dữ Liệu Học Thuật (Phase 3)
  ├── 3.1. Xây dựng DemoPaperViewer (Mô phỏng bài báo 2 cột, render Bounding Box tọa độ phần trăm).
  ├── 3.2. Xây dựng DemoChatPanel (Bong bóng chat Socratic Mentor, Thinking Block, Citation Badges).
  ├── 3.3. Tích hợp useLandingStore và useDemoStream (Zero-Jank rAF Typewriter Buffer).
  ├── 3.4. Xây dựng QuickUploadModal tích hợp kéo thả file PDF mẫu.
  └── Kiểm chuẩn: Nhấp Citation Badge -> Bounding Box highlight viền Coral tức thì không độ trễ.

Giai đoạn 4: Kiểm Thử Đa Tầng, Tối Ưu Hiệu Năng & Visual MCP Audit (Phase 4)
  ├── 4.1. Viết bộ Unit Tests với Vitest cho logic tính tọa độ và Zustand store.
  ├── 4.2. Viết kịch bản Playwright E2E cho luồng duyệt trang và tương tác demo.
  ├── 4.3. Chạy chrome-devtools MCP kiểm tra sạch 100% Console Error và Network 404.
  ├── 4.4. Kiểm chuẩn Production Gate: pnpm build, tsc -b, lint đạt Zero Error / Zero Warning.
  └── Báo cáo kết quả kiểm chuẩn toàn diện cho Người Dùng.
```

---

## 9. CHECKLIST BẢO CHỨNG CHẤT LƯỢNG SẢN PHẨM (PRODUCTION QUALITY GATE)

- [ ] **Semantic Design Tokens:** Nền canvas `#faf9f5`, nút San hô `#cc785c`, mặt sàn tối `#181715`, viền 1px `#e6dfd8` được áp dụng chuẩn xác 100%.
- [ ] **Typography Hierarchy:** Tiêu đề h1-h3 dùng Serif (Copernicus / Cormorant Garamond) weight 400 negative tracking; body/button dùng Sans (Inter / StyreneB); code/toán dùng JetBrains Mono.
- [ ] **5 Trạng Thái Giao Diện:** Default, Loading/Skeleton, Empty, Error (kèm Retry), Active Highlight được định nghĩa rõ ràng.
- [ ] **WAI-ARIA Accessibility:** Hỗ trợ đầy đủ phím Tab, Enter, Esc; có Focus Trap cho modal; thuộc tính role và aria-label mạch lạc.
- [ ] **Zero Type Any:** 100% mã nguồn TypeScript định kiểu tường minh, đồng bộ khép kín với OpenAPI schemas.
- [ ] **Zero-Jank Performance:** Quản lý đệm token qua `requestAnimationFrame`, không phát sinh re-render bão táp.
- [ ] **Lightweight Architecture:** Không nạp PDF.js nặng trên Landing Page; điểm FCP < 0.8s.
- [ ] **Zero Console Error:** Kết quả thanh tra qua chrome-devtools MCP không có bất kỳ cảnh báo hoặc lỗi đỏ nào.
- [ ] **An Toàn Quy Trình:** Nhánh git đề xuất `feat/fe-landing-page`, không tự động commit/push, dừng lại chờ người dùng phê duyệt trước khi viết bất kỳ dòng code nào.
