# Thiết Kế Chi Tiết: Bố Cục alphaXiv Tối Giản, Khắc Phục Bugs Frontend & Nâng Cấp Trải Nghiệm AI Thinking, Sơ Đồ Mermaid

> **Trạng thái:** DRAFT — Trình duyệt Phương án 1  
> **Tác giả:** VeriScholar Engineering Pair  
> **Ngày:** 2026-10-28  
> **Mục tiêu:** Tái cấu trúc giao diện `/dashboard/:id` tiệm cận 100% chuẩn tối giản quốc tế của `alphaXiv.org`, khắc phục 4 lỗi frontend nghiêm trọng (scroll, Bounding Box, con trỏ cam), tích hợp khối tư duy `Thinking Finished` đếm giây và bộ xuất ảnh SVG/PNG cho sơ đồ Mermaid.

---

## 1. Bối Cảnh & Động Lực (Context & Motivation)
Người dùng nghiên cứu khoa học cần một không gian đọc bài báo tập trung, thoáng đãng, không bị phân tán bởi các thanh công cụ cồng kềnh. Đồng thời, quá trình đối thoại với AI cần đạt chuẩn mực thẩm mỹ cao như các sản phẩm hàng đầu (ChatGPT, Claude, alphaXiv):
1. **Lỗi cuộn trang:** Trong khi AI stream, toàn bộ trang bị kéo tụt xuống dưới và xuất hiện thanh scroll ngang nhấp nháy, làm mất thanh tiêu đề và che khuất nội dung.
2. **Quá tải Bounding Box:** Click trích dẫn sinh ra nhiều khung viền rải rác che lấp bài báo, không có nút tắt tức thì khiến người dùng phải F5.
3. **Con trỏ cam thô:** Vạch cam `|` to bản nằm độc lập trên dòng trống gây giật mắt.
4. **Thiếu khối tư duy trực quan:** Người dùng cần theo dõi thời gian và chuỗi lập luận của AI dạng viên thuốc `✓ Thinking Finished ∨` co giãn linh hoạt.
5. **Nhu cầu trực quan hóa sơ đồ:** Người dùng muốn AI có thể vẽ sơ đồ kiến trúc, thuật toán và xuất ra file ảnh SVG/PNG để tái sử dụng.
6. **Bố cục alphaXiv:** Người dùng yêu cầu bài báo có thể xem toàn màn hình 100%, có Bong bóng nổi AI Assistant ở góc phải dưới, click vào để mở bảng chat 50/50 và có nút `✕` đóng lại.

---

## 2. Kiến Trúc & Thiết Kế Giải Pháp (Technical Architecture)

### 2.1 Khắc phục Triệt để 4 Bugs Frontend
1. **Khắc phục lỗi cuộn trang lan truyền (Bug 1 & Bug 2):**
   - Trong `DashboardWorkspace.tsx`, loại bỏ lệnh `bboxRef.current.scrollIntoView({ behavior: "smooth", block: "center" })` toàn cục.
   - Thay thế bằng việc cuộn cục bộ trong `PdfCanvasViewer`: tìm phần tử cha có thuộc tính `overflow-y-auto` và điều chỉnh `container.scrollTop` nội bộ, tuyệt đối không tác động lên `window` hay `document.body`.
   - Bổ sung `overflow-x-hidden` và `h-screen overflow-hidden` trên toàn bộ container gốc của Dashboard.
   - Điều chỉnh khung `DashboardChatInputBox` và `TypingWaveIndicator` đảm bảo width luôn $\le 100\%$, ngăn chặn tình trạng tràn viền tạo scrollbar ngang.

2. **Chuẩn hóa 1 Bounding Box duy nhất & Cơ chế Tắt tức thì (Bug 3):**
   - Trong `useReaderStore.ts` và `DashboardWorkspace.tsx`, khi click vào trích dẫn `citation`:
     - Chỉ trích xuất đúng 1 Bounding Box tiêu điểm (`primaryBox = bboxes[0] || citation.bbox`).
     - Đặt `activeBbox = primaryBox` và không nạp mảng `activeBboxes` thừa thãi.
   - **Cơ chế tắt tức thì:**
     - **Toggle:** Click lại vào chính trích dẫn đang mở sẽ hủy Bounding Box (`setActiveBboxStore(null)`).
     - **Click ngoài:** Click vào bất kỳ vị trí trống nào trên trang PDF sẽ đóng khung.
     - **Phím tắt Esc:** Lắng nghe sự kiện phím `Escape` để hủy Bounding Box.
     - **Pill điều khiển:** Hiển thị một huy hiệu nhỏ gọn trên thanh điều hướng: `"Đang làm nổi bật [1] — ✕ Tắt"`.

3. **Loại bỏ con trỏ cam thô `|` (Bug 4):**
   - Trong `AcademicMarkdownRenderer.tsx`, loại bỏ khối `<span className="w-1.5 h-4 ml-1 bg-[#cc785c] ... />` nằm trên dòng trống độc lập.
   - Thay thế bằng hiệu ứng con trỏ mảnh tinh tế `inline-block w-[2px] h-[1em] ml-0.5 bg-coral-500/80 animate-pulse align-middle` gắn liền sau từ ngữ cuối cùng khi đang stream, tự động biến mất khi hoàn thành.

---

### 2.2 Bố Cục Đọc alphaXiv & Bong Bóng AI Nổi (Floating Assistant FAB)

```
+----------------------------------------------------------------------------+
| [Abstract] [Paper]   | 1 / 15 |  (-) (+) (⬇) (🖨)      | ⓘ  📝  [ 🤖 ]   |
+---------------------------------------------------------+------------------+
|                                                         | Assistant  (+) ✕ |
|                                                         |------------------|
|                   PDF READER 100%                       | ✓ Thinking Finish|
|                                                         |------------------|
|               (Toàn màn hình tập trung)                 | Nội dung AI trả  |
|                                                         | lời với Mermaid &|
|                                                         | Trích dẫn [1]    |
|                                                         |------------------|
|                                         [ 🤖 Bong bóng ]| Prompt Input     |
+---------------------------------------------------------+------------------+
```

1. **Trạng thái Mặc định (Full Paper 100%):**
   - Màn hình bài báo chiếm 100% không gian hiển thị chính.
   - Ở góc dưới cùng bên phải màn hình hiển thị **Bong bóng nổi AI Assistant (FAB)**: nút tròn bo mềm, màu cam san hô (#cc785c / primary), icon Socratic / Sparkles, có hiệu ứng hover và tooltip *"Mở Socratic Copilot"*.
2. **Trạng thái Mở Khung Chat (Slide-Over Split 50/50):**
   - Khi bấm vào bong bóng nổi, bảng điều khiển bên phải trượt mở mượt mà (chiếm 50% hoặc tỉ lệ người dùng tùy chỉnh).
   - Thanh tiêu đề bên phải hiển thị:
     - Tên: **"Assistant"** (font serif thanh lịch).
     - Nút **`(+) Đoạn chat mới`**.
     - Nút **`✕` Đóng bảng chat**: khi bấm vào, bảng chat đóng lại, bài báo nở rộng về 100% và bong bóng nổi xuất hiện trở lại ở góc dưới bên phải.
3. **Thanh Dock Tiện Ích Dọc (Vertical Edge Dock):**
   - Tọa lạc ở cạnh phải màn hình gồm các icon nhỏ gọn:
     - `ⓘ` Thông tin bài báo & Tóm tắt nhanh.
     - `📝` Sổ tay ghi chú (Notes).
     - `🤖` Toggle Assistant (đồng bộ với bong bóng nổi).
   - Loại bỏ thanh 5 tab cồng kềnh phía trên, mang lại sự tối giản triệt để chuẩn alphaXiv.

---

### 2.3 Khối Tư Duy AI (`SocraticThinkingBlock`)
1. **Giao diện Capsule chuẩn alphaXiv / ChatGPT:**
   - Khi AI đang xử lý (nhận event SSE `reasoning` hoặc `thought`):
     - Hiển thị viên thuốc bo tròn: `<span className="animate-pulse">✦ Đang phân tích... {seconds}s</span>`.
     - Đồng hồ đếm giây tăng theo thời gian thực.
   - Khi AI hoàn tất (bắt đầu stream nội dung hoặc xong):
     - Chuyển thành trạng thái hoàn thành: `✓ Đã suy nghĩ trong {seconds}s ∨` (mặc định đóng gọn).
     - Người dùng bấm vào nút mũi tên để bung toàn bộ nội dung Chain-of-Thought và chuỗi hành động kiểm tra Bounding Box, tra cứu tài liệu.

---

### 2.4 Trực Quan Hóa Sơ Đồ Mermaid & Xuất Ảnh SVG / PNG
1. **Biên dịch Mermaid sang SVG:**
   - `AcademicMarkdownRenderer.tsx` nhận diện các khối ````mermaid ... ````.
   - `MermaidRenderer.tsx` dùng thư viện `mermaid.js` kết xuất thành thẻ `<svg>` an toàn với bảng màu chuẩn (Dark/Light Mode).
2. **Thanh công cụ Xuất Ảnh (Export Toolbar):**
   - Trên góc phải của thẻ sơ đồ, cung cấp các nút thao tác nhanh:
     - **Sao chép mã** (`Copy Code`).
     - **Tải SVG** (`Download SVG`): Tạo blob vector `.svg` cho chất lượng in ấn vô hạn.
     - **Tải PNG** (`Download PNG`): Sử dụng canvas chuyển đổi SVG sang raster `.png` sắc nét (scale 2x retina).
     - **Xem toàn màn hình** (`Expand Modal`): Bấm để phóng to sơ đồ khi cấu trúc quá rộng.
3. **System Prompt Kích Hoạt Sơ Đồ:**
   - Bổ sung chỉ dẫn vào `session_chat_service.py` để Socratic Copilot chủ động dựng sơ đồ Mermaid khi phân tích kiến trúc mô hình, quy trình dữ liệu hoặc khi người dùng yêu cầu trực quan hóa.

---

## 3. Danh Mục Tệp Thay Đổi (File Breakdown)

| Tệp tin | Vai trò & Trách nhiệm |
| :--- | :--- |
| `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx` | Layout alphaXiv, 100% Paper view, Floating AI FAB, nút `✕` đóng Assistant, xử lý scroll container |
| `apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx` | Component hiển thị khối tư duy đếm giây `✓ Thinking Finished ∨` |
| `apps/web/src/features/dashboard/components/VerticalEdgeDock.tsx` | Thanh dock biểu tượng dọc mép phải (`ⓘ`, `📝`, `🤖`) thay thế 5 tab cũ |
| `apps/web/src/features/reader/components/BboxHighlightLayer.tsx` | Giới hạn 1 Bounding Box duy nhất, xử lý nút đóng và phím `Esc` |
| `apps/web/src/features/reader/stores/useReaderStore.ts` | Action dọn sạch và toggle Bounding Box |
| `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx` | Xóa con trỏ cam thô `|`, kết xuất Mermaid chuẩn và con trỏ mảnh |
| `apps/web/src/components/shared/MermaidRenderer.tsx` | Tích hợp nút xuất ảnh SVG / PNG và phóng to sơ đồ |
| `apps/web/src/features/dashboard/hooks/useStreamingChat.ts` | Bắt chuẩn sự kiện SSE `reasoning` và đo thời gian suy nghĩ |
| `apps/api/src/api/services/session_chat_service.py` | Hướng dẫn System Prompt sinh cú pháp Mermaid hợp lệ khi cần trực quan hóa |

---

## 4. Kế Hoạch Kiểm Thử TDD & 4 Cổng Xác Minh
- **Kiểm thử Đơn vị Frontend (Vitest):**
  - `DashboardAlphaXivLayout.test.tsx`: Kiểm tra chế độ xem 100% paper, click Floating FAB mở Assistant, click `✕` đóng Assistant.
  - `BboxSingleHighlightAndDismiss.test.tsx`: Kiểm tra chỉ vẽ 1 Bounding Box, nhấn `Esc` hoặc click ngoài để xóa highlight.
  - `SocraticThinkingBlock.test.tsx`: Kiểm tra đồng hồ đếm giây, trạng thái hoàn tất co gọn và mở rộng xem thought log.
  - `MermaidExport.test.tsx`: Kiểm tra render SVG và chức năng xuất ảnh SVG/PNG.
- **4 Cổng Xác Minh Bắt Buộc:**
  - Cổng 1: `uv run ruff check . && uv run ruff format --check .`
  - Cổng 2: `uv run pytest`
  - Cổng 3: `npm --prefix apps/web run test`
  - Cổng 4: `npm --prefix apps/web run build`
- **VPS Rollout:** `bash scripts/deploy_to_vps.sh --fast` và kiểm tra trực tiếp trên `https://verischolar.duckdns.org`.
