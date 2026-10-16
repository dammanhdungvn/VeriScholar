# Tài Liệu Thiết Kế & Kiến Trúc Frontend: Landing Page (VeriScholar)

> **Vị trí lưu trữ chính thức:** `docs/vi/decided/frontend/landing-page.md`  
> **Mã nguồn tính năng:** [`apps/web/src/features/landing/`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/src/features/landing/)  
> **Trạng thái:** Production Decided (Đã hoàn thiện, kiểm chuẩn & merge vào `main`)  
> **Mục đích tài liệu:** Lưu trữ toàn diện triết lý thiết kế, hệ thống Design System Tokens, các quyết định kiến trúc, lịch sử tối ưu hóa và các bất biến (invariants) để các AI Agent và kỹ sư đời sau nắm rõ bối cảnh, lý do lựa chọn và cách bảo trì an toàn.

---

## 1. TỔNG QUAN & TRIẾT LÝ THIẾT KẾ (ARCHITECTURAL PHILOSOPHY)

Landing Page của VeriScholar không phải là một trang tiếp thị thương mại đại trà, mà là **cửa ngõ truyền tải triết lý học thuật nhân văn (Warm-Canvas Editorial)** và **chứng minh năng lực công nghệ độc bản**:
1. **Cam kết Cốt lõi — Triệt tiêu 100% Ảo giác (Zero Hallucination):** Khác biệt hoàn toàn với các chatbot AI chung chung, VeriScholar cam kết mọi luận điểm trích xuất từ tài liệu đều có **bảo chứng tọa độ Bounding Box trực quan** theo chuẩn ISO 32000-1.
2. **Trải nghiệm Demo Trực quan Không Cần Đăng nhập (In-Place Interactive Demo):** Cho phép người dùng trải nghiệm ngay lập tức trên trang chủ: đọc bài báo IEEE 2 cột, click vào trích dẫn `[Paper • Trang • BBox]`, khung vàng nhảy chính xác đến đoạn văn bản chứng minh mà chưa cần tạo tài khoản.
3. **Bản sắc thị giác Warm-Canvas Editorial (DESIGN.md):** Sự kết hợp tương phản có chủ đích giữa **Nền giấy kem ấm áp (`#FAF9F5`)**, **Nút San hô Coral ấm (`#CC785C`)** và **Mặt sàn công nghệ Dark Obsidian (`#181715`)**.

---

## 2. HỆ THỐNG DESIGN SYSTEM & SEMANTIC TOKENS (DESIGN.MD)

Toàn bộ Landing Page được xây dựng trên nền tảng **Tailwind CSS v4** với các biến CSS ngữ nghĩa (Semantic CSS Variables) thuần khiết, triệt tiêu 100% JavaScript runtime overhead:

### 2.1. Bảng màu Ngữ nghĩa (Semantic Color Tokens)

| Token CSS | Giá trị Light Mode | Giá trị Dark Mode | Ý nghĩa & Vị trí áp dụng |
| :--- | :--- | :--- | :--- |
| `--color-canvas` | `#FAF9F5` (Giấy kem ấm) | `#181715` (Obsidian sâu) | Mặt sàn toàn trang (Page floor) |
| `--color-surface-soft` | `#F5F0E8` (Kem nhạt) | `#201E1B` (Slate tối) | Dải phân cách mềm, ô nhập liệu |
| `--color-surface-card` | `#EFE9DE` (Card kem) | `#262420` (Thẻ nổi tối) | Thẻ tính năng, khung chứa nội dung |
| `--color-surface-cream-strong` | `#E8E0D2` | `#2E2A24` | Tab active, đường biên card nổi bật |
| `--color-primary` | `#CC785C` (San hô Coral) | `#CC785C` | Nút hành động chính (Primary CTA), liên kết |
| `--color-primary-active` | `#A9583E` (San hô đậm) | `#A9583E` | Trạng thái active/hover của nút chính |
| `--color-accent-amber` | `#E8A55A` (Hổ phách) | `#E8A55A` | **Khung viền Bounding Box Highlight** |
| `--color-accent-teal` | `#5DB8A6` (Xanh ngọc) | `#5DB8A6` | Huy hiệu trạng thái kết nối, verify |
| `--color-hairline` | `#E6DFD8` (Viền 1px) | `#332F28` | Đường viền tóc ngăn cách cấu trúc |
| `--color-ink` | `#141413` (Đen mực) | `#F5F3ED` (Kem sáng) | Tiêu đề chính h1, h2, văn bản đậm |
| `--color-body` | `#3D3D3A` | `#D1CCC2` | Văn bản nội dung thông thường |
| `--color-muted` | `#6C6A64` | `#9C988F` | Chú thích phụ, ngày tháng, nhãn mờ |

### 2.2. Phân cấp Typography (Font Hierarchy)
* **Display Serif (`font-display`):** `Cormorant Garamond` / `Copernicus`, serif. Áp dụng cho các tiêu đề chính h1, h2, trích dẫn Richard Feynman. Đặc tính: thanh lịch, trang nhã, học thuật cổ điển (weight 400 - 500, letter-spacing -0.5px đến -1px).
* **Humanist Sans (`font-sans`):** `Inter` / `StyreneB`, sans-serif. Áp dụng cho thân bài, nhãn nút bấm, thẻ metadata. Đặc tính: rõ ràng, dễ đọc trên màn hình mật độ cao (weight 400, 500, 600).
* **Monospace (`font-mono`):** `JetBrains Mono`, monospace. Áp dụng cho thông số tọa độ `[x0, y0, x1, y1]`, tên file PDF, mã SHA-256, số trang bài báo.

### 2.3. Quy chuẩn Bo góc (Radius Scale)
* **Controls & Buttons:** `rounded-lg` (8px - 10px).
* **Thẻ Card & Khung Mockup:** `rounded-2xl` (16px).
* **Thanh Floating Island Navbar:** `rounded-2xl` (16px) với `backdrop-blur-2xl`.
* **Huy hiệu Badges & Chips:** `rounded-full` (9999px).

---

## 3. CÁC QUYẾT ĐỊNH THIẾT KẾ CỐT LÕI & LỊCH SỬ ĐỔI MỚI (DECISIONS & ITERATIONS)

### 3.1. Quyết định 1: Không Tải Thư Viện PDF.js Nặng Trên Landing Page
* **Bối cảnh:** Cần hiển thị bài báo khoa học 2 cột để minh họa việc nhảy Bounding Box.
* **Đánh đổi:** Nếu nạp toàn bộ `pdfjs-dist` + Web Worker, bundle size tăng thêm > 800KB, First Contentful Paint (FCP) bị đẩy lên > 2.4s.
* **Giải pháp:** Xây dựng **DOM-Based Vector Paper Simulator** ([`DemoPaperViewer.tsx`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/src/features/landing/components/DemoPaperViewer.tsx)).
  * Dữ liệu mock chuẩn IEEE 2 cột ([`mock-papers.ts`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/src/features/landing/data/mock-papers.ts)).
  * Ma trận tỷ lệ chuẩn hóa `[x0, y0, x1, y1, page]` với tọa độ thực relative `[0.0, 1.0]`.
  * **Kết quả:** Tốc độ tải trang < 0.6s, đạt điểm Google PageSpeed 99/100, hoàn toàn mượt mà 60fps.

---

### 3.2. Quyết định 2: Cuộc Cách Mạng Favicon & Browser Tab Chuẩn Big-Tech
* **Vấn đề ban đầu:** Icon tab trình duyệt trông bé, lọt thỏm và thành một ô vuông tối do nhét nguyên cả logo phức tạp (khung 4 góc, ngôi sao, lề đệm lớn) vào canvas 16×16 px. Khi bật Chrome Dark Mode, cánh phải màu đen bị chìm vào nền tab tối, khiến logo *"bị mất nửa chữ V bên phải"*.
* **Bài học từ GitHub (Octocat) & Vercel (Triangle):** Tối giản tuyệt đối, phóng to tối đa diện tích quang học (Optical Fill ~85%–90%).
* **Giải pháp triển khai:**
  1. **Tách riêng Core Favicon Mark:** Chỉ giữ lại biểu tượng nhận diện lõi: Cánh chim học thuật (Scholar Coral) và Vết tích xác thực chữ V (Verification Arm).
  2. **Bộ Asset Đa Định Dạng trong [`apps/web/public/`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/public/):**
     * `favicon-dark.svg`, `favicon-dark-32x32.png`, `favicon-dark.ico`: Cánh phải màu **Trắng tinh khiết (`#FFFFFF`)** cho Chrome Dark Mode.
     * `favicon-light.svg`, `favicon-light-32x32.png`, `favicon-light.ico`: Cánh phải màu **Đen mực (`#1E1B18`)** cho Chrome Light Mode.
     * `apple-touch-icon.png` (180×180 px với nền Obsidian bo góc cho iOS).
     * `site.webmanifest` (cấu hình PWA chuẩn).
  3. **Cơ chế Đồng bộ Chế độ Trình duyệt Hai Tầng:**
     * **Tầng 1 (Parser-blocking script trong `<head>`):** Thực thi đồng bộ trong microsecond trước khi parse DOM body, gán tức thì file `-dark` hoặc `-light` phù hợp với `prefers-color-scheme`.
     * **Tầng 2 ([`favicon.ts`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/src/lib/favicon.ts)):** Lắng nghe sự kiện `change` của hệ thống để đổi màu icon theo thời gian thực mà không cần reload trang.

---

### 3.3. Quyết định 3: Tinh Chỉnh Neural Particle Canvas (`AtmosphericBackground.tsx`)
* **Lịch sử tối ưu:**
  * Ban đầu: Dark mode có 45 hạt bụi sao nhẹ nhàng.
  * Thử nghiệm 1 (Light mode): Tăng kích thước hạt x2.6 và thêm quầng hào quang (+4.5px outer halo). Người dùng phản ánh: *"Sao to quá vậy, bé lại ngay"*.
  * **Giải pháp Tỷ lệ Vàng Hoàn Thiện:**
    * Bán kính hạt Light Mode: `Math.max(2.2, p1.radius * 1.15)` — hạt gọn gàng, tinh tế.
    * Độ dày đường synapse: mảnh nhẹ `0.95px`.
    * Hạt xung thần kinh (Synaptic Pulse Bead): `2.2px` chuyển động dọc đường kết nối.
    * Loại bỏ hoàn toàn vòng tròn quầng halo thô cứng; thay bằng lõi san hô terracotta `#CC785C` viền `#B96549` sắc nét trên nền kem.
    * Tốc độ trôi Brownian dịu nhẹ (`speed: 0.28`), tắt tương tác chuột khi cuộn để không giật lag.

---

### 3.4. Quyết định 4: Thanh Điều Hướng Floating Island Navbar Chuẩn Big-Tech (Streamlined Action Cluster)
* **Cấu trúc:** Thanh nổi bo góc mềm nằm cố định cách đỉnh màn hình 16px (`sticky top-4`), nền bán trong suốt `bg-canvas/80 dark:bg-[#22201c]/80 backdrop-blur-2xl`.
* **Cụm hành động (Action Cluster) theo tiêu chuẩn SaaS hàng đầu (Linear, Claude, Perplexity):**
  * **Tránh trùng lặp (Anti-Redundancy):** Ban đầu giao diện đặt nút chữ "Đăng nhập" cạnh nút "Dùng thử ngay". Thiết kế này gây thừa thãi thị giác (visual clutter) và phân tán chú ý vì cả hai đều dẫn tới luồng xác thực.
  * **Luồng Người dùng Tối giản (Streamlined Flow):**
    1. **Khi Chưa Đăng Nhập (Guest Mode):**
       * Logo Academic (bấm vào quay về trang chủ `/`).
       * Nút GitHub Repository (icon SVG với hiệu ứng hover scale 110%).
       * Nút chính duy nhất **"Dùng thử ngay"** (`data-testid="nav-try-btn"`): Nút màu San hô Coral nổi bật với icon Sparkles + ArrowUpRight. Khi click, điều hướng trực tiếp sang `/login`.
       * Tại trang `/login`, người dùng hiện hữu đăng nhập bằng Email / Google / ORCID / Tài khoản demo 1-click; người dùng mới chưa có tài khoản bấm liên kết *"Đăng ký tài khoản"* để chuyển sang `/register`. Đăng nhập/đăng ký thành công đều chuyển thẳng sang `/dashboard`.
    2. **Khi Đã Đăng Nhập (Authenticated Mode — Cải tiến tinh giản theo yêu cầu):**
        * Logo Academic (dẫn về `/`).
        * Nút GitHub Repository.
        * **Nút chính "Dashboard" (`data-testid="nav-dashboard-btn"`):** Thay thế nút "Dùng thử ngay", điều hướng thẳng vào `/dashboard` để tiếp tục phiên nghiên cứu.
        * **Triệt tiêu Visual Clutter:** Ẩn hoàn toàn nhãn tên user và nút `LogOut` trên Navbar của Landing Page nhằm bảo đảm tính liền mạch, thanh thoát tối đa của trang giới thiệu sản phẩm. (Việc quản lý tài khoản và Đăng xuất được thực hiện tại góc dưới thanh Taskbar của `/dashboard`).
    3. **Nút Chuyển đổi Giao diện Sáng/Tối (Theme Toggle):** Luôn cố định ở vị trí ngoài cùng bên phải, chuyển đổi mượt mà giữa Dark và Light mode.

---

## 4. BẢN ĐỒ CẤU TRÚC THÀNH PHẦN (COMPONENT ARCHITECTURE)

```text
apps/web/src/features/landing/
├── components/
│   ├── LandingPageContainer.tsx    # Container gốc kết nối toàn bộ các section
│   ├── AtmosphericBackground.tsx   # Canvas vẽ mạng nơ-ron học thuật & sao vi mô
│   ├── LandingNavbar.tsx           # Floating island navbar + theme + auth trigger
│   ├── HeroSection.tsx             # Tiêu đề chính, Slogan Feynman, CTA kép
│   ├── InteractiveDemo.tsx         # Khung Demo: chia đôi Paper Viewer & Chat Panel
│   ├── DemoPaperViewer.tsx         # Mô phỏng bài báo IEEE 2 cột, lớp BBox highlight
│   ├── DemoChatPanel.tsx           # Panel chat đối thoại Socratic, SSE token stream
│   ├── QuickUploadModal.tsx        # Modal kéo thả PDF, tính SHA-256 idempotency
│   └── LandingFooter.tsx           # Footer học thuật, chuẩn ISO, liên kết tài liệu
├── data/
│   └── mock-papers.ts              # Dữ liệu bài báo mẫu IEEE (Attention Is All You Need)
├── hooks/
│   ├── useDemoStream.ts            # Hook đọc stream từng từ qua requestAnimationFrame
│   └── useLandingApi.ts            # Hook upload tài liệu (hỗ trợ real API + fallback)
├── stores/
│   ├── useLandingStore.ts          # Zustand store quản lý active tab, paper, bbox
│   └── useLandingStore.test.ts     # Unit tests cho store
└── types/
    └── landing.ts                  # Schema Paper, Citation, BoundingBox, ChatTurn
```

---

## 5. ĐẶC TẢ CHI TIẾT TỪNG COMPONENT

### 5.1. `AtmosphericBackground.tsx` (Dual-Mode Neural Canvas)
* **Kỹ thuật:** HTML5 Canvas với `requestAnimationFrame`.
* **Khả năng tự thích ứng chế độ:**
  * **Dark Mode (Vũ trụ Tri thức):**
    * 45 hạt bụi sao trôi dạt với hiệu ứng lấp lánh (twinkle pha $\sin$).
    * Màu hạt: `#CC785C` (san hô), `#5DB8A6` (ngọc bích), `#FAF9F5` (trắng kem).
    * Đường kết nối synapse chỉ xuất hiện khi khoảng cách giữa 2 hạt $< 130px$.
  * **Light Mode (Mạng Lưới Thần Kinh Tơ Lụa):**
    * 38 nút nơ-ron trí tuệ với viền terracotta ấm áp.
    * Hạt xung thần kinh (Synaptic Pulse Bead) di chuyển liên tục dọc theo các sợi liên kết.
* **Tối ưu hiệu năng:** Tự động phát hiện kích thước màn hình qua `ResizeObserver`, hạ số lượng hạt trên thiết bị di động để duy trì 60fps trên GPU yếu.

---

### 5.2. `DemoPaperViewer.tsx` (IEEE Two-Column Viewer & Bounding Box)
* **Bố cục:** Mô phỏng bài báo khoa học định dạng 2 cột kinh điển:
  * Cột 1: Abstract, Introduction, Model Architecture.
  * Cột 2: Multi-Head Attention, Scaled Dot-Product, Positional Encoding.
* **Lớp phủ Bounding Box (Highlight Layer):**
  * Tọa độ Bounding Box chuẩn: `[x0, y0, x1, y1, page]`.
  * Khi người dùng bấm vào một trích dẫn ở Chat Panel (ví dụ: `[Paper 1 • Trang 3]`), `useLandingStore.activeBbox` được kích hoạt.
  * Khung viền vàng Hổ phách `--color-accent-amber: #E8A55A` nhấp nháy êm dịu, cuộn mượt (smooth scroll) đến đúng đoạn văn bản chứng minh.

---

### 5.3. `DemoChatPanel.tsx` (Socratic Mentor Chat Interface)
* **Mô hình đối thoại:** Trợ lý Socratic không chỉ trả lời kết quả thô, mà dẫn dắt từng bước suy luận khoa học:
  1. *Câu hỏi của nhà nghiên cứu:* "Giải thích cơ chế Multi-Head Attention?"
  2. *Suy luận của AI:* Phân tách truy vấn thành Q, K, V và phép nhân ma trận.
  3. *Câu trả lời kèm Bằng chứng:* Mỗi khẳng định đều đính kèm một Badge Trích Dẫn tương tác:
     ```tsx
     <CitationBadge
       paperId="p1"
       page={3}
       bbox={[0.18, 0.32, 0.82, 0.44]}
       text="Trích đoạn tọa độ BBox chứng minh"
     />
     ```
* **Cơ chế Zero-Jank Streaming ([`useDemoStream.ts`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/src/features/landing/hooks/useDemoStream.ts)):**
  * Token từ văn bản được nạp vào một hàng đợi (buffer).
  * Hàm `requestAnimationFrame` rút từng từ ra để render vào DOM mỗi frame.
  * Triệt tiêu hoàn toàn hiện tượng bão re-render (re-render storm) khi hiển thị văn bản dài.

---

### 5.4. `QuickUploadModal.tsx` (Drag-and-Drop Ingestion)
* **Tuân thủ Invariant Độc Bản:** Bất biến Idempotency dựa trên **SHA-256 Content Hash**.
* **Luồng xử lý:**
  1. Người dùng kéo thả file PDF vào vùng Dropzone (hỗ trợ tối đa 50MB theo cấu hình `VITE_MAX_UPLOAD_SIZE_BYTES`).
  2. Client tính toán hash SHA-256 bằng Web Crypto API `crypto.subtle.digest("SHA-256", arrayBuffer)`.
  3. Nếu file trùng hash với tài liệu đã có, hệ thống lập tức tái sử dụng tài liệu mà không tốn công đoạn index lại.
  4. Hiển thị thanh tiến trình tải lên với hoạt ảnh quét Bounding Box trực quan.

---

## 6. QUẢN LÝ TRẠNG THÁI (STATE MANAGEMENT ARCHITECTURE)

### 6.1. `useLandingStore` (Zustand)
```typescript
interface LandingState {
  activePaperId: string;
  activeBbox: BoundingBox | null;
  isUploadModalOpen: boolean;
  selectedQuestionIndex: number;
  setActivePaper: (id: string) => void;
  setActiveBbox: (bbox: BoundingBox | null) => void;
  setUploadModalOpen: (open: boolean) => void;
  setSelectedQuestionIndex: (idx: number) => void;
}
```
* **Nguyên tắc:** Dùng **Fine-grained Selectors** (e.g. `useLandingStore(s => s.activeBbox)`) để các section tĩnh khác (Hero, Footer) không bị kích hoạt re-render khi người dùng tương tác trong demo.

### 6.2. `useTheme` (Dual-Mode System)
* Quản lý trạng thái `"light" | "dark"`.
* Đồng bộ 3 chiều:
  1. Thuộc tính DOM: `document.documentElement.classList.toggle("dark")`, `setAttribute("data-theme")`, `style.colorScheme`.
  2. LocalStorage: `verischolar_theme`.
  3. Hệ thống OS: Tự động nhận diện `window.matchMedia("(prefers-color-scheme: dark)")` khi chưa có cài đặt thủ công.

---

## 7. QUY CHUẨN KIỂM THỬ & KIỂM ĐỊNH (QUALITY ASSURANCE)

Mọi thay đổi trên Landing Page bắt buộc vượt qua bộ 5 cổng kiểm tra:

1. **Linting Check:**
   ```bash
   pnpm --prefix apps/web lint
   # Yêu cầu: oxlint exit 0, 0 warning, 0 error
   ```
2. **TypeScript Compilation:**
   ```bash
   pnpm --prefix apps/web exec tsc -b
   # Yêu cầu: tsc exit 0, nghiêm ngặt tuân thủ verbatimModuleSyntax
   ```
3. **Unit & Integration Tests (Vitest):**
   ```bash
   pnpm --prefix apps/web test
   # Yêu cầu: 100% test suites passed (HeroSection, AcademicLogo, button, useTheme, useLandingStore, favicon...)
   ```
4. **Production Build Validation:**
   ```bash
   pnpm --prefix apps/web build
   # Yêu cầu: Vite build production bundle thành công, dung lượng asset tối ưu
   ```
5. **Visual Audit (Puppeteer Headless):**
   * Kiểm tra sạch Console: `Console Errors = 0`.
   * Kiểm tra giao diện đối chiếu ở cả 2 chế độ:
     * Desktop Light (`1440×900`)
     * Desktop Dark (`1440×900`)
     * Mobile (`375×812`)
   * Tỷ lệ tương phản chữ WCAG AA $\ge 4.5:1$ trên mọi khối văn bản.

---

## 8. CẨM NANG CHO AI AGENT & KỸ SƯ TƯƠNG LAI (INVARIANTS & GUIDELINES)

Khi thực hiện bảo trì, tối ưu hoặc mở rộng Landing Page, **BẮT BUỘC TUÂN THỦ CÁC BẤT BIẾN SAU**:

1. **Bất biến Tọa độ Bounding Box (Atomic Evidence Invariant):**
   * Đơn vị trích xuất bắt buộc phải lưu trữ tọa độ chuẩn hóa `[x0, y0, x1, y1, page]`.
   * `page`: Số nguyên đánh chỉ mục từ 1 (`page >= 1`).
   * `x0, y0, x1, y1`: Số thực chuẩn hóa `[0.0, 1.0]` tương đối với kích thước trang.
   * Điểm gốc tọa độ `(0, 0)` luôn luôn là **Top-Left** (Góc trên bên trái).
   * **TUYỆT ĐỐI KHÔNG** hạ cấp bằng chứng trích dẫn thành chuỗi văn bản trần không có tọa độ.
2. **Bất biến Hiệu năng Bundle Size:**
   * **KHÔNG ĐƯỢC PHÉP** import trực tiếp thư viện `pdfjs-dist` hoặc các parser PDF nặng vào bundle của Landing Page. Chỉ dùng lightweight DOM/Vector simulation.
3. **Bất biến Nhận diện Tab Trình duyệt (Favicon Invariant):**
   * Không bao giờ nhét viền thẻ card hoặc chi tiết mảnh vào favicon. Luôn duy trì tỷ lệ phủ quang học ~85%–90%.
   * Luôn duy trì cơ chế phân định màu cánh phải của chữ V: màu **Trắng tinh khiết (`#FFFFFF`)** trên tab tối và màu **Đen mực (`#1E1B18`)** trên tab sáng.
4. **Bất biến Bố cục Thanh Điều Hướng (Navbar Order):**
   * Thứ tự các thành phần trong cụm action cluster trên Navbar bắt buộc phải giữ vững:
     `GitHub Icon` $\rightarrow$ `Auth State (Đăng nhập / User)` $\rightarrow$ `Dùng thử ngay` $\rightarrow$ `Theme Toggle`.
   * Theme toggle luôn là phần tử ngoài cùng bên phải để tạo sự ổn định về vị trí nhấn cho người dùng.
5. **Bất biến Cập nhật Tài liệu:**
   * Mỗi khi có thay đổi về thiết kế, bảng màu, component hoặc luồng dữ liệu của Landing Page, **BẮT BUỘC CẬP NHẬT TÀI LIỆU NÀY** (`docs/vi/decided/frontend/landing-page.md`) để duy trì tính toàn vẹn tri thức của dự án.
