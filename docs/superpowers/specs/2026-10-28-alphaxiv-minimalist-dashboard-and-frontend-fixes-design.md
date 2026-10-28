# Thiết Kế Chi Tiết: Bố Cục alphaXiv Tối Giản, Khắc Phục Bugs Frontend & Nâng Cấp Trải Nghiệm AI Thinking Stepper, Concept Pills & Sơ Đồ Mermaid

> **Trạng thái:** DRAFT — Cập nhật đầy đủ theo hình ảnh thực tế của người dùng  
> **Tác giả:** VeriScholar Engineering Pair  
> **Ngày:** 2026-10-28  
> **Mục tiêu:** Tái cấu trúc giao diện `/dashboard/:id` theo chuẩn tối giản quốc tế của `alphaXiv.org` và mô hình Agent Stepper hiện đại (Antigravity / Claude / ChatGPT):
> 1. Khắc phục 4 lỗi frontend (scroll lan truyền, quá tải Bounding Box, con trỏ cam thô).
> 2. Khối tư duy Agent Activity Stepper: Hiển thị các bước `Working`, `Reading...`, `Thought for Xs`, tự động thu gọn thành `Worked for Xs >` (click `v` mở rộng xem chi tiết, click `^` thu gọn).
> 3. Trích dẫn Concept Pills & Popover Preview: Bỏ hoàn toàn `[1] [2]` và chân trang trích dẫn, thay bằng thẻ khái niệm `[ ↪ Architecture ]`; hover hiện thẻ xem trước snippet + `Page X`, click cuộn sang PDF viền 1 Bounding Box duy nhất.
> 4. Xuất ảnh sơ đồ Mermaid sang SVG / PNG.
> 5. Bố cục alphaXiv: Bài báo 100%, Bong bóng AI nổi (FAB) góc phải dưới, khung Assistant trượt mở có nút `✕` và Vertical Edge Dock.

---

## 1. Chi Tiết Khối Tư Duy Agent Activity Stepper (`SocraticThinkingBlock`)
Theo đúng nguyên mẫu trong Ảnh 1, 2, 3, 4:
1. **Khi AI đang làm việc (Active / Streaming):**
   - Ban đầu: hiển thị chữ `Working` mờ nhẹ hoặc xoay nhẹ.
   - Khi thực hiện tác vụ:
     - `Reading chunk... ∨`
     - `Thought for {s}s >` (đồng hồ đếm giây tăng theo thời gian thực)
     - `Analyzed Bounding Box #Page {num}`
2. **Khi AI hoàn tất (Finished / Standby):**
   - Tự động co lại thành một dòng tiêu đề duy nhất: `Worked for {total_s}s >` (Ảnh số 4).
   - **Click `>` / `v` (Mở rộng - Ảnh số 3):**
     - Bung ra toàn bộ danh sách các bước đã thực hiện (`Explored file`, `Analyzed...`).
     - Hiển thị khối nội dung suy nghĩ / lập luận Chain-of-Thought (`Thought for Xs`) dạng văn bản chi tiết.
   - **Click `^` / `v` (Thu gọn - Ảnh số 4):**
     - Đóng gọn lại ngay lập tức để người dùng tập trung đọc câu trả lời chính của AI.

---

## 2. Chi Tiết Trích Dẫn Khái Niệm & Thẻ Xem Trước (`Grounded Concept Pills`)
Theo đúng nguyên mẫu trong Ảnh 2 & Ảnh 3:
1. **Loại bỏ cơ chế cũ:**
   - Tuyệt đối không hiển thị `[1]`, `[2]`, `[3]`.
   - Xóa bỏ hoàn toàn phần chân trang `"Nguồn trích dẫn (2)"` ở cuối tin nhắn.
2. **Thẻ Khái Niệm Nội Dòng (Semantic Concept Pills):**
   - Thay thế bằng các thẻ capsule bo tròn tinh tế: `[ ↪ Architecture ]`, `[ ↪ Multi-Head Attention ]`, `[ ↪ Main Idea ]`.
   - Bảng màu: Nền xám đen nhẹ `#22211e`, viền `#38342e`, chữ `#dcd7cc`, icon `↪` thanh mảnh.
3. **Tương tác Hover (Thẻ Xem Trước Nổi - Popover Card):**
   - Khi di chuột (hover) vào thẻ khái niệm:
     - Bật lên một Popover Tooltip Card nổi ngay tại vị trí trỏ chuột.
     - Bên trong hiển thị đoạn trích dẫn nguyên văn từ bài báo (hỗ trợ công thức KaTeX).
     - Ở góc trên bên phải của thẻ hiển thị huy hiệu `Page X` (ví dụ: `Page 5`).
4. **Tương tác Click (Nhảy Bounding Box):**
   - Khi click vào thẻ khái niệm:
     - PDF bên trái tự động cuộn đến trang `Page X`.
     - Vẽ **đúng 1 Bounding Box duy nhất** viền nét đứt màu xanh/cam quanh đoạn văn bản/công thức tương ứng.

---

## 3. Khắc Phục 4 Lỗi Frontend
1. **Lỗi cuộn lan truyền (Bug 1 & 2):** Cô lập layout bằng `h-screen overflow-hidden` và `overflow-x-hidden`. Thay thế `scrollIntoView` toàn cục trên Bounding Box bằng cuộn cục bộ trong container PDF.
2. **Giới hạn 1 Bounding Box & Tắt tức thì (Bug 3):** Chỉ cho phép tối đa 1 Bounding Box hoạt động. Hỗ trợ tắt khung ngay khi bấm `Esc`, click lại thẻ trích dẫn, hoặc click ra ngoài canvas.
3. **Con trỏ cam thô `|` (Bug 4):** Xóa khối cam to bản trên dòng trống; thay bằng con trỏ mảnh tinh tế gắn liền sau ký tự cuối cùng.

---

## 4. Bố Cục alphaXiv & Xuất Ảnh Mermaid
1. **Bài báo 100% & Bong bóng nổi (FAB):**
   - Khi Assistant đóng: Bài báo bung 100% toàn màn hình; ở góc dưới cùng bên phải có nút tròn AI Assistant (FAB).
   - Khi click FAB: Bảng Assistant mở ra (50/50 split), góc trên có tiêu đề "Assistant", `(+) New Chat`, và nút `✕` đóng.
   - Mép phải có `VerticalEdgeDock.tsx` với icon `ⓘ`, `📝`, `🤖` thay thế thanh 5 tab cồng kềnh.
2. **Sơ đồ Mermaid:**
   - Tự động biên dịch sang SVG.
   - Thêm nút "Tải SVG" và "Tải PNG" (2x retina) cùng nút sao chép mã trên góc sơ đồ.

---

## 5. Danh Mục Tệp Thay Đổi
- `apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx`: Component Agent Activity Stepper với các bước `Working`, `Thought for Xs`, thu gọn `Worked for Xs >`.
- `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx`: Concept Pills `[ ↪ Concept ]`, xóa `[1] [2]` và footer trích dẫn, popover preview card on hover.
- `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`: Layout alphaXiv, 100% paper, Floating AI FAB, nút `✕`, chặn scroll lan truyền.
- `apps/web/src/features/reader/components/BboxHighlightLayer.tsx`: Giới hạn 1 Bounding Box, lắng nghe phím `Esc` và click ngoài.
- `apps/web/src/components/shared/MermaidRenderer.tsx`: Tích hợp xuất ảnh SVG & PNG.
- `apps/api/src/api/services/session_chat_service.py`: Cập nhật System Prompt sinh concept tags thay vì số `[1] [2]` và xuất Mermaid khi cần.
