# PHÂN HỆ BẢNG NGỮ CẢNH 3 CỘT & LỘ TRÌNH HỌC TUẦN TỰ (A → B → C → D)
# (3-COLUMN CONTEXT TABLE, 2-TIER INGESTION & SOCRATIC ROADMAP)

---

## 1. Mục Tiêu Phân Hệ
Giải quyết hai nỗi đau lớn nhất khi đọc hiểu chuyên sâu một bài báo khoa học:
1. **Chống học nhảy cóc (A $\rightarrow$ D):** Khi người đọc hỏi một kiến thức nâng cao (D) mà bài báo hiện tại chỉ nhắc lướt qua vì kế thừa từ kiến thức nền tảng (B, C) trong các bài báo tham khảo khác, AI tự động phát hiện và gợi ý lộ trình học tuần tự từ gốc đến ngọn.
2. **Mở rộng ngữ cảnh 1-Click không đứt mạch đọc:** Bóc tách mục References cuối bài theo mã định danh chuẩn (DOI / arXiv ID) kết hợp **Exa AI**, hiển thị thành **Bảng 3 Cột** để người dùng bấm nạp thêm bài báo vào phiên chat trong `< 500ms`.

---

## 2. Gợi Ý Lộ Trình Học Tuần Tự (Socratic Bridge Hint: A → B → C → D)

### A. Tình huống kích hoạt
* Khi người dùng đặt câu hỏi về một công thức, thuật toán hoặc cơ chế (D) trong bài báo đang đọc, nhưng trong văn bản gốc tác giả không giải thích từ đầu mà dẫn chiếu tới bài báo tham khảo `[k]` (ví dụ: *"như đã trình bày trong [3], chúng tôi áp dụng cơ chế Multi-Head Attention..."*).

### B. Cách AI phản hồi & Giao diện Gợi ý Bắc cầu
1. **Phần giải thích trực tiếp:** AI dùng kiến thức nền để giải thích khái quát ý nghĩa của bước (D) để người dùng nắm được ý chính ngay.
2. **Thẻ Gợi ý Lộ trình Học Tuần tự (Bridge Hint Card):** Ở cuối câu trả lời, AI đối chiếu với danh sách `reference_items` của bài báo hiện tại và hiển thị một hộp gợi ý rõ ràng:
   > *"💡 **Lộ trình học tuần tự gợi ý:** Để hiểu thật sâu công thức này (Bước D), bạn nên nắm vững kiến thức nền tảng **[Tên khái niệm B / C]** được trình bày chi tiết trong bài báo tham khảo **[3] Attention Is All You Need (Vaswani et al., 2017)**. Bạn có muốn nạp bài [3] vào phiên chat này để tìm hiểu bước B trước không?"*
   > Kèm nút bấm 1-Click: **`[➕ Nạp bài [3] vào phiên chat]`**.
3. **Liên thông xử lý khi bấm nút:**
   * Khi người dùng bấm `[➕ Nạp bài [3] vào phiên chat]`, hệ thống gọi trực tiếp API Nạp 2 Tầng (`POST /api/v1/sessions/{session_id}/references:ingest` với `ref_index = 3`) mà không bắt người dùng phải tự mở Bảng References đi tìm.
   * Nếu phiên đọc đã mở đủ `5/5 bài báo`, hệ thống hiển thị thông báo nhắc người dùng đóng bớt 1 bài ít dùng trên Thanh Tab PDF hoặc Bảng 3 Cột trước khi nạp.

---

## 3. Bảng Quản Lý Ngữ Cảnh 3 Cột (References + Exa Search 2 Tầng)

### A. Trích xuất & Định danh chuẩn xác (Chống tìm nhầm bài báo trùng tên)
1. **Quét danh mục References (`POST /api/v1/documents/{document_id}:extract-references`, `GET /api/v1/documents/{document_id}/references`):**
   * Bóc tách danh sách tài liệu tham khảo ở cuối bài báo gồm: số thứ tự `[ref_index]`, tiêu đề (`parsed_title`), tác giả (`parsed_authors`), năm xuất bản (`parsed_year`), và đặc biệt ưu tiên trích xuất mã **`doi`** hoặc **`arxiv_id`**.
2. **Xác thực đường dẫn qua Exa AI & Nguồn học thuật (`GET /api/v1/documents/{document_id}/references:resolve`):**
   * Nếu có mã `arXiv ID` hoặc `DOI`: Xác thực chính xác 100% bài báo qua arXiv / Semantic Scholar / Crossref kết hợp **Exa AI**.
   * Nếu không có mã định danh: Truy vấn qua **Exa AI Neural Search** (`category="research paper"`) kết hợp kiểm tra độ khớp tiêu đề + tên tác giả đầu tiên để lấy đúng đường dẫn gốc và tóm tắt học thuật.

### B. Giao diện Bảng 3 Cột (`ReferenceListModal.tsx` / `SmartReferenceDrawer.tsx`)
Khi người dùng bấm nút **`[📚 Bảng References & Mở rộng Context]`** trên thanh công cụ đọc bài, hệ thống hiển thị Bảng 3 Cột rõ ràng, có ô tìm kiếm nhanh theo tên bài/tác giả/mã DOI:

| Cột 1: Name (Tên bài báo, Tác giả, Năm & Mã định danh) | Cột 2: URL (Đường dẫn gốc) | Cột 3: Action (Thao tác Ngữ cảnh Chat) |
| :--- | :--- | :--- |
| **[1] Attention Is All You Need**<br>*(Vaswani et al., 2017 • arXiv:1706.03762)*<br>`🟢 Có sẵn PDF Open Access` | [arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762) ↗ | **`[➕ Thêm vào đoạn chat này]`**<br>*(Nếu đã thêm: hiện **`[🗑️ Xóa khỏi chat]`**)* |
| **[2] Deep Residual Learning for Image Recognition**<br>*(He et al., 2016 • DOI:10.1109/CVPR.2016.90)*<br>`🟡 Chỉ có Tóm tắt (Bản gốc thu phí)` | [doi.org/10.1109/CVPR.2016.90](https://doi.org/10.1109/CVPR.2016.90) ↗ | **`[➕ Thêm vào đoạn chat này]`**<br>*(Kèm nút nhỏ `[📤 Tự tải PDF lên]`)* |

---

## 4. Chiến Lược Nạp Ngữ Cảnh 2 Tầng Đồng Bộ Với Thanh Tab PDF

Khi người dùng bấm **`[➕ Thêm vào đoạn chat này]`** ở Cột 3 (hoặc bấm từ thẻ Gợi ý Lộ trình Học Tuần tự):

### Tầng 1: Nạp Nhanh Tức Thì (`< 500ms` — Fast Context Injection)
* Hệ thống nạp ngay lập tức **Tiêu đề, Tác giả, Năm, Abstract và Điểm cốt lõi (Exa Summary/Highlights)** của bài báo đó vào bộ nhớ ngữ cảnh của phiên chat hiện tại.
* Nút ở Cột 3 chuyển thành trạng thái đã nạp (kèm nút **`[🗑️ Xóa khỏi chat]`** nếu muốn gỡ ra).
* Người dùng có thể hỏi ngay các câu hỏi tổng quan/so sánh giữa bài đang đọc và bài vừa thêm mà không phải chờ đợi.

### Tầng 2: Tải Ngầm PDF Toàn Văn & Tự Động Mở Tab PDF Mới (Background Full-Text Ingestion)
* **Trường hợp bài báo có link PDF Open Access miễn phí:**
  1. Hệ thống chạy ngầm việc tải file PDF về máy chủ, bóc tách cấu trúc + các khối văn bản (`chunks`) kèm tọa độ `Bounding Box`.
  2. Ngay khi hoàn tất, hệ thống **tự động mở thêm 1 Tab PDF của bài báo đó trên Thanh Tab khung đọc bên trái** để người dùng và AI có thể bấm xem khung viền vàng `Bounding Box` trên cả bài mới thêm.
* **Cơ chế Fallback trung thực khi Tầng 2 đang tải dở (Chống AI bịa công thức):**
  * Nếu người dùng vừa bấm thêm bài được 2 giây đã hỏi ngay: *"Công thức số (12) ở cuối bài báo vừa thêm là gì?"* trong khi Tầng 2 mới tải được `45%`:
  * Hệ thống kiểm tra trạng thái `document.status != "ready"` và buộc AI trả lời trung thực:
    > *"⏳ Hệ thống đang tải và bóc tách toàn văn PDF của bài báo **[Tên bài]** (tiến độ hiện tại: **45%**). Hiện tôi mới có phần Tóm tắt (Abstract) nên chưa thể trích xuất chính xác công thức ở cuối bài. Bạn vui lòng đợi khoảng vài giây để quá trình tải hoàn tất 100% rồi hỏi lại nhé!"*
* **Trường hợp bài báo bị khóa thu phí (Paywall Fallback — Không có PDF miễn phí):**
  * Tiến trình Tầng 2 không bị treo ở `0%` mà đánh dấu ngay trạng thái bài báo là **`abstract_only`** với nhãn **`[🟡 Chỉ có Tóm tắt (Bản gốc thu phí — Bấm để tải file PDF từ máy nếu bạn có)]`**.
  * AI vẫn sử dụng dữ liệu Tầng 1 (Abstract + Highlights từ Exa) để trả lời các câu hỏi tổng quan và nói rõ cho người dùng biết bài báo này hiện chỉ có bản Tóm tắt trừ khi người dùng tải file PDF của họ lên.
