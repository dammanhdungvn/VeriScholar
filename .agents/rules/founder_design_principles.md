# Nguyên Tắc Thiết Kế Giao Diện & Trải Nghiệm Người Dùng (Founder Design Principles)

Tài liệu này ghi lại các nguyên tắc thiết kế bắt buộc được đề ra bởi Founder / Product Owner cho toàn bộ các thành viên và AI Agents tham gia phát triển VeriScholar.

---

## 1. Triết Lý "Ngăn Tủ / Chiếc Túi Gọn Gàng" (Clean Drawers Principle)

> *"Giao diện càng ít hiển thị toàn bộ ra càng tốt. Bạn biết tại sao lại cần chia ra các ngăn tủ không? Vì để chúng vào cùng một ngăn cho gọn gàng và dễ sắp xếp. Nguyên lý thiết kế: Show ra ít thứ trên giao diện càng tốt, hãy để nó vào các 'chiếc túi' (dropdown/popover bằng cách bấm vào button mới mở ra để chọn). Thiết kế như vậy cho nó gọn mắt."*

### Quy tắc áp dụng cụ thể:
1. **Tối Giản Màn Hình Chính:** Không phơi bày tràn lan các thanh công cụ, nút bấm hoặc toggle options trên giao diện đọc và soạn thảo. Chỉ hiển thị các nút thao tác chính yếu nhất (như Lưu, Biên dịch, Gửi tin nhắn).
2. **Gom Nhóm Vào Ngăn Tủ (Popovers / Drawers):** Các tùy chọn phụ trợ (Bố cục, Phóng to/Thu nhỏ, Chọn chế độ xem, Xuất bản, Công cụ định dạng LaTeX, Đổi theme) phải được đóng gói gọn trong các Popover ("ngăn tủ") xuất hiện khi click vào nút đại diện.
3. **Thanh Công Cụ Tự Động Ẩn Sau 5 Giây (5s Auto-Hide Secondary Ribbon):**
   - Bất kỳ thanh công cụ bổ trợ nào (secondary ribbon/toolbar) đều phải tự động ẩn đi sau 5 giây nếu người dùng không tương tác/hover vào.
   - Khi người dùng rê chuột (hover) vào khu vực hoặc bấm nút đánh thức, thanh công cụ phải hiển thị trở lại mượt mà để hỗ trợ thao tác, tối ưu hóa không gian cho việc đọc tài liệu.
4. **Chế Độ Đọc Gọn Gàng (Reading Mode Selectdown):** Nút chọn chế độ đọc đặt ở vị trí thuận tiện nhưng mở ra một popover danh sách các chế độ (Single Page, Continuous, Dual Page, Presentation) thay vì trải dài các tab gây rối mắt.

---

## 2. Chuẩn Mực Học Thuật & Trích Dẫn Minh Bạch (Academic Precision & Citations)

1. **Inline Citation Chuyển Đến Bounding Box:**
   - Khi câu trả lời trích dẫn từ bài báo khoa học, thẻ trích dẫn (`[^cit_x]`) phải xuất hiện trực tiếp ngay dòng nội dung liên quan.
   - Khi người dùng nhấp vào thẻ trích dẫn, hệ thống lập tức cuộn trang và làm nổi bật chính xác Bounding Box (khối tọa độ) của đoạn văn bản nguồn trên file PDF.
2. **Công Thức Toán, Mã Nguồn & Sơ Đồ Kiến Trúc (Math, Code, Mermaid):**
   - Hiển thị công thức toán học sắc nét thông qua KaTeX.
   - Highlight cú pháp mã nguồn chuẩn xác với nút sao chép nhanh.
   - Hỗ trợ trực quan hóa Mermaid.js (flowchart, architecture diagram, mindmap) khi người dùng yêu cầu vẽ sơ đồ hoặc tổng hợp bài báo.

---

## 3. Các Không Gian Làm Việc Chuẩn Theo PRD

1. **Writing Workspace (Không gian Viết Paper Khoa học):**
   - Tự động nạp mẫu bài báo LaTeX học thuật chuẩn (`STANDARD_ACADEMIC_LATEX_TEMPLATE`) khi tạo mới hoặc mở tài liệu trống.
   - Tự động biên dịch sang PDF và hiển thị preview ngay lập tức, không bắt người dùng phải tự bấm biên dịch thủ công lần đầu.
   - Áp dụng thanh công cụ "Ngăn tủ" với Bố cục, Công cụ & Xuất bản, cùng thanh ribbon tự ẩn 5 giây.
2. **Project Workspace (Quản Lý Dự Án Nghiên Cứu):**
   - Header dạng ChatGPT Project: `[📁 VeriScholar] [Chia sẻ]`.
   - Chuyển đổi linh hoạt giữa 2 chế độ chính: `[Trò chuyện (Chat)]` và `[Kế hoạch thực thi (Work)]`.
   - Hai ngăn phụ quản lý: `[Đoạn chat (Chats)]` và `[Tài liệu nguồn (Sources)]`, cùng nút `+ Đoạn chat mới trong Dự án`.
3. **Library Workspace (Kho Lưu Trữ Tri Thức & Ma Trận So Sánh):**
   - Giao diện toàn màn hình thay thế modal cũ.
   - Thanh tìm kiếm tài liệu đa năng, nút chuyển đổi dạng lưới (Grid) / danh sách (List), nút `+ Thêm tài liệu`.
   - Tabs lọc nhanh: `[Gợi ý]`, `[Yêu thích (⭐)]`, `[Thư mục (📁)]`, `[Sơ đồ & Mindmap (📊)]`, `[Tất cả]`.
   - Nút ghim sao yêu thích đồng bộ tức thì, cùng nút mở nhanh Ma Trận So Sánh Đối Chiếu (Comparison Matrix).
