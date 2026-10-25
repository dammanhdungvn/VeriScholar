# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (PRD): KHÔNG GIAN SOẠN THẢO HỌC THUẬT & ĐỒNG TÁC GIẢ AI TỰ TRỊ
# (AGENTIC SCHOLARLY WRITING WORKSPACE & AUTONOMOUS AI CO-AUTHOR)

**Mã tài liệu:** `PRD-06`  
**Thuộc giải pháp:** VeriScholar AI Research Assistant  
**Vai trò tác giả:** Chuyên viên Phân tích Nghiệp vụ (Business Analyst)  
**Tài liệu kỹ thuật đối ứng:** [`06-agentic-overleaf-writing-spec.md`](../specs/06-agentic-overleaf-writing-spec.md)  
**File nền tảng liên đới:** [`00-overview-and-cleanup.md`](./00-overview-and-cleanup.md)  

---

## 1. Tầm Nhìn Nghiệp Vụ & Nỗi Đau Người Dùng (Business Context & Pain Points)

Soạn thảo một bài báo khoa học chuẩn quốc tế hay một báo cáo đồ án tốt nghiệp là giai đoạn gian nan nhất trong toàn bộ quy trình nghiên cứu:
- **Nỗi đau 1 — Đứt gãy giữa khâu đọc tài liệu và khâu viết bài:** Sau khi hoàn thành phiên đọc sâu 3–5 bài báo, học giả phải mở một phần mềm soạn thảo bên ngoài từ con số không. Họ phải tự đi tìm lại từng mã trích dẫn, gõ lại cấu trúc khung bài báo, sao chép từng ghi chú rời rạc. Sự rời rạc này tạo nên "hội chứng sợ trang giấy trắng", làm tiêu tốn hàng giờ đồng hồ quý báu chỉ để thiết lập môi trường viết ban đầu.
- **Nỗi đau 2 — Ác mộng lỗi cú pháp biên dịch tài liệu học thuật:** Để có bản in khoa học đẹp chuẩn mực, các học giả bắt buộc phải sử dụng các định dạng học thuật chuyên dụng. Tuy nhiên, chỉ cần thiếu một dấu ngoặc, sai một ký tự đặc biệt hoặc một trích dẫn không khớp, tài liệu sẽ lập tức bị lỗi biên dịch với những thông báo dòng lệnh khó hiểu. Người viết thường mất nhiều thời gian sửa lỗi cú pháp hơn là tập trung sáng tạo nội dung khoa học.
- **Nỗi đau 3 — Thiếu một đồng tác giả AI thấu hiểu toàn diện bối cảnh nghiên cứu:** Các công cụ sinh văn bản thông thường chỉ tạo ra những đoạn văn chung chung, không có khả năng tự động liên kết với kho bài báo yêu thích của học giả, không biết cách trích xuất số liệu thực nghiệm chính xác và không thể tự giác sửa chữa lỗi định dạng khi xảy ra sự cố.

VeriScholar giải quyết triệt để các rào cản trên bằng một giải pháp đột phá:
1. **Cầu Nối "Đọc Sang Viết" Tự Động:** Khởi tạo tức thì một bản thảo học thuật hoàn chỉnh từ phiên đọc, nạp sẵn toàn bộ danh mục tài liệu trích dẫn chuẩn chỉ sau một cú nhấp chuột.
2. **Không Gian Soạn Thảo 3 Cột Tương Tác Trực Quan:** Tích hợp quản lý tệp, soạn thảo mã nguồn, xem trước bản in PDF thời gian thực và khung đối thoại với trợ lý AI.
3. **Đồng Tác Giả AI Tự Trị & Vòng Lặp Tự Vá Lỗi Biên Dịch:** AI có khả năng tự soạn thảo, tự tra cứu số liệu từ kho tri thức, tự gửi biên dịch và tự giác sửa chữa lỗi cú pháp đến khi tài liệu hoàn toàn xuất bản thành công mà không đòi hỏi người dùng phải can thiệp thủ công.

---

## 2. Các Tác Nhân Tham Gia (Actors)

| Tác nhân | Vai trò trong phân hệ | Trách nhiệm & Kỳ vọng |
| :--- | :--- | :--- |
| **Nhà Nghiên Cứu / Tác Giả** | Chủ sở hữu bản thảo | Định hướng đề tài, ra lệnh cho AI soạn thảo từng mục, tự do chỉnh sửa thủ công và quyết định chấp nhận hay hoàn tác các thay đổi của AI. |
| **Đồng Tác Giả AI (AI Co-Author)** | Trợ lý soạn thảo tự trị chuyên sâu | Viết nội dung học thuật chuẩn mực, tự bổ sung khóa trích dẫn, tra cứu số liệu đối chiếu từ kho tài liệu và tự sửa chữa lỗi cú pháp tài liệu. |
| **Động Cơ Biên Dịch Học Thuật** | Hạ tầng biên dịch đám mây cô lập an toàn | Tiếp nhận toàn bộ gói mã nguồn bài báo, biên dịch thành bản in PDF chuẩn quốc tế, và cung cấp phản hồi chi tiết nếu phát sinh lỗi định dạng. |

---

## 3. Danh Sách Use Cases Chi Tiết (Structured Use Cases)

### UC-WRITE-01: Chuyển Giao Khung Sườn Liền Mạch Từ Phiên Đọc (Reading-to-Writing Handover)
- **Tác nhân:** Nhà Nghiên Cứu.
- **Tiền điều kiện:** Người dùng đang ở trong một phiên nghiên cứu có tài liệu và các ghi chú trích dẫn.
- **Sự kiện kích hoạt:** Người dùng nhấp vào nút `[✍️ Bắt đầu viết bài từ phiên này]` trên thanh công cụ đọc.
- **Luồng sự kiện chính (Happy Path):**
  1. Hệ thống tự động tạo một bản thảo nghiên cứu mới gắn liền với phiên đọc hiện tại.
  2. Hệ thống tự động sinh **Khung Sườn Học Thuật Chuẩn**:
     - Danh mục trích dẫn đã được nạp đầy đủ 100% tất cả các bài báo đang mở trong phiên đọc kèm mã định danh trích dẫn chuẩn mực.
     - Mã nguồn bài báo đã được thiết lập sẵn cấu trúc hoàn chỉnh: Tiêu đề gợi ý theo đề tài, phần Giới thiệu, phần Tổng quan Nghiên cứu (đã chèn sẵn các câu dẫn chiếu tới các bài báo vừa đọc), phần Phương pháp luận và phần Thực nghiệm.
     - Toàn bộ ghi chú cá nhân người dùng đã lưu trong phiên đọc được nạp vào bộ nhớ ngữ cảnh của trợ lý viết bài.
  3. Hệ thống tự động chuyển người dùng sang Không Gian Soạn Thảo 3 Cột, bản xem trước PDF lập tức hiển thị sắc nét trong vòng chưa đầy 2 giây.
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Người dùng muốn tạo bản thảo độc lập không từ phiên đọc:* Hệ thống cung cấp tùy chọn tạo bản thảo mới từ trang danh sách, cho phép chọn mẫu định dạng chuẩn (IEEE, ACM, Báo cáo Đồ án hoặc Bản trống).

---

### UC-WRITE-02: Không Gian Soạn Thảo Học Thuật 3 Cột (3-Column Scholarly Workspace)
- **Tác nhân:** Nhà Nghiên Cứu.
- **Tiền điều kiện:** Người dùng đã mở một bản thảo nghiên cứu.
- **Sự kiện kích hoạt:** Giao diện không gian soạn thảo được hiển thị.
- **Bố cục 3 Cột Tinh Gọn:**
  1. **Cột 1 (Trái) — Quản lý Tài liệu & Ô Soạn Thảo Mã Nguồn:**
     - Cây danh mục dự án: Chuyển đổi linh hoạt giữa tệp mã nguồn chính, tệp danh mục trích dẫn và thư mục hình ảnh của bài báo.
     - Trình soạn thảo mã nguồn có số dòng, tô màu cú pháp rõ ràng, hỗ trợ chỉnh sửa thủ công bất kỳ lúc nào.
     - Nút `[⚙️ Biên dịch PDF]` thủ công và nút `[↩️ Hoàn tác thay đổi của AI]`.
  2. **Cột 2 (Giữa) — Bản Xem Trước Bản In PDF:**
     - Hiển thị trực tiếp bản PDF được biên dịch từ mã nguồn.
     - Hỗ trợ công cụ phóng to, thu nhỏ, cuộn trang mượt mà và nút xuất tải gói tài liệu hoàn chỉnh.
  3. **Cột 3 (Phải) — Trợ Lý Đồng Tác Giả AI:**
     - Khung đối thoại với trợ lý AI, lưu trữ bền vững toàn bộ lịch sử trao đổi.
     - Hiển thị huy hiệu trạng thái hành động trực quan theo thời gian thực để người dùng nắm rõ AI đang làm gì.
- **Cơ chế Chống Ghi Đè & Hoàn Tác 1-Click (1-Click Undo):**
  - Trước khi cho phép AI chỉnh sửa mã nguồn, hệ thống tự động chụp lại một bản sao lưu trạng thái hiện tại.
  - Ngay sau khi AI hoàn tất chỉnh sửa, nút `[↩️ Hoàn tác thay đổi của AI]` sáng lên. Người dùng có thể quay về trạng thái ban đầu chỉ với 1 cú nhấp chuột nếu không hài lòng với nội dung AI tạo ra.

---

### UC-WRITE-03: Đồng Tác Giả AI Soạn Thảo & Tích Hợp Tri Thức Kho Yêu Thích
- **Tác nhân:** Nhà Nghiên Cứu & Đồng Tác Giả AI.
- **Tiền điều kiện:** Bản thảo đang mở và người dùng nhập yêu cầu vào khung chat Cột 3.
- **Sự kiện kích hoạt:** Người dùng gửi yêu cầu soạn thảo (ví dụ: *"Hãy viết mục Tổng quan nghiên cứu so sánh cơ chế Attention của bài Vaswani với CNN truyền thống, có trích dẫn chuẩn"*).
- **Luồng sự kiện chính (Happy Path):**
  1. Trợ lý AI tiếp nhận yêu cầu, phân tích nội dung cần viết.
  2. AI tự động truy vấn vào Kho Bài Báo Yêu Thích và Mạng Tri Thức Đồ Thị để trích xuất các luận điểm và con số thực nghiệm chính xác.
  3. AI kiểm tra danh mục trích dẫn; nếu bài báo chưa có trong danh mục, AI tự động bổ sung thông tin trích dẫn mới.
  4. AI viết đoạn văn học thuật mới trực tiếp vào tệp mã nguồn chính với câu từ trang trọng, đúng văn phong nghiên cứu quốc tế và chèn mã trích dẫn chuẩn xác.
  5. AI tự động kích hoạt tiến trình biên dịch tài liệu để cập nhật bản xem trước PDF ở Cột 2.
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Yêu cầu vượt quá dữ liệu có trong kho:* AI phản hồi rõ ràng những điểm thiếu tài liệu minh chứng và khuyến nghị người dùng nạp thêm bài báo liên quan thay vì tự ý bịa đặt trích dẫn.

---

### UC-WRITE-04: Biên Dịch Tự Động & Vòng Lặp Tự Sửa Lỗi Cú Pháp (Zero-Click Self-Healing Compilation)
- **Tác nhân:** Đồng Tác Giả AI & Động Cơ Biên Dịch Học Thuật.
- **Tiền điều kiện:** Bản thảo được yêu cầu biên dịch (do người dùng bấm nút hoặc do AI kích hoạt sau khi viết).
- **Sự kiện kích hoạt:** Mã nguồn được gửi tới Động cơ Biên dịch.
- **Luồng sự kiện chính (Happy Path):**
  1. Động cơ Biên dịch tiếp nhận toàn bộ gói mã nguồn, thực thi quy trình dựng bản in trong môi trường cô lập an toàn.
  2. Biên dịch thành công: Bản in PDF mới nhất lập tức hiển thị trên Cột 2.
- **Luồng Tự Sửa Lỗi Tự Trị (Self-Healing Loop — Tối đa 3 vòng lặp):**
  1. Nếu biên dịch thất bại do lỗi cú pháp (ví dụ: thiếu dấu ngoặc công thức toán, sai nhãn trích dẫn):
  2. Đồng tác giả AI lập tức tự động can thiệp mà không làm phiền người dùng.
  3. AI đọc thông báo lỗi từ động cơ biên dịch, xác định chính xác dòng bị lỗi và nguyên nhân cú pháp.
  4. AI tự động chỉnh sửa trực tiếp mã nguồn để vá lỗi cú pháp.
  5. AI tự động gửi lại lệnh biên dịch để kiểm tra lại. Quy trình này tự động lặp lại cho đến khi biên dịch thành công (ngân sách tối đa 3 lần thử).
  6. Suốt quá trình, khung chat Cột 3 hiển thị huy hiệu tiến trình minh bạch: *`⚠️ Phát hiện lỗi dòng 42` $\rightarrow$ `✍️ AI đang tự vá cú pháp` $\rightarrow$ `⚙️ Biên dịch lại (Lần 2/3)` $\rightarrow$ `🎉 Hoàn tất!`*.
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Vượt quá 3 lần tự sửa lỗi mà vẫn thất bại:* AI dừng vòng lặp an toàn, bảo toàn nguyên vẹn mã nguồn, thông báo rõ ràng dòng bị lỗi kèm hướng dẫn cụ thể để người dùng cùng xử lý.

---

### UC-WRITE-05: Quản Lý Tài Nguyên Đồ Họa & Đóng Gói Xuất Bản Thảo (Assets & Export)
- **Tác nhân:** Nhà Nghiên Cứu.
- **Tiền điều kiện:** Bản thảo đang mở.
- **Sự kiện kích hoạt:** Người dùng muốn chèn hình ảnh hoặc tải toàn bộ công trình để nộp bài.
- **Luồng sự kiện chính (Happy Path):**
  - **Quản lý tài nguyên đồ họa:**
    1. Người dùng nhấp `[➕ Tải ảnh lên]` trong mục hình ảnh ở Cột 1 để tải sơ đồ kiến trúc hoặc biểu đồ thực nghiệm (hỗ trợ định dạng ảnh chuẩn và PDF vector).
    2. Tệp ảnh hiển thị trong danh mục tài nguyên. Người dùng chỉ cần nhấp vào tên ảnh là hệ thống tự động chèn đoạn mã mẫu chèn hình học thuật vào vị trí con trỏ trong mã nguồn.
    3. AI khi được yêu cầu mô tả sơ đồ cũng có thể nhận biết danh sách tệp ảnh này để chèn đúng vị trí.
  - **Đóng gói xuất bản thảo nộp bài:**
    1. Người dùng nhấp nút `[📦 Xuất gói nộp bài]`.
    2. Hệ thống tự động đóng gói toàn bộ dự án thành một tệp nén `.zip` hoàn chỉnh gồm: Tệp mã nguồn chính, tệp danh mục trích dẫn, toàn bộ thư mục hình ảnh và bản PDF đã biên dịch thành công.
    3. Gói nén này tương thích 100% với các nền tảng nộp bài quốc tế và hệ thống Overleaf.

---

## 4. Tiêu Chí Nghiệm Thu Nghiệp Vụ (Acceptance Criteria - Gherkin)

### Kịch bản 1: Tạo bản thảo tức thì từ phiên đọc với khung sườn học thuật hợp lệ
```gherkin
Given người dùng đang có một phiên đọc sâu chứa 3 bài báo khoa học và các ghi chú trích dẫn
When người dùng nhấp nút "[✍️ Bắt đầu viết bài từ phiên này]"
Then hệ thống phải tạo ngay một bản thảo mới gắn với đề tài phiên đọc
  And danh mục trích dẫn phải nạp đầy đủ mã chuẩn của cả 3 bài báo
  And mã nguồn bài báo phải có sẵn các mục Giới thiệu, Tổng quan có trích dẫn và Phương pháp luận
  And bản xem trước PDF phải hiển thị thành công trong vòng chưa đầy 2 giây mà không có lỗi cú pháp
```

### Kịch bản 2: AI tự động vá lỗi biên dịch cú pháp tối đa 3 lần
```gherkin
Given mã nguồn bài báo bị lỗi cú pháp thiếu dấu đóng ngoặc công thức toán ở dòng 42
When tiến trình biên dịch tài liệu được kích hoạt
Then hệ thống không được báo lỗi chặn người dùng ngay lập tức
  And đồng tác giả AI phải tự động đọc thông báo lỗi và tự sửa lại mã nguồn
  And AI tự động gửi biên dịch lại cho đến khi thành công
  And toàn bộ tiến trình tự vá lỗi phải hiển thị huy hiệu trạng thái rõ ràng ở Cột 3
  And số lần tự sửa lỗi tối đa không được vượt quá 3 lần
```

### Kịch bản 3: Hoàn tác 1-Click bảo toàn quyền kiểm soát của tác giả
```gherkin
Given đồng tác giả AI vừa thực hiện chỉnh sửa nội dung trong mã nguồn bài báo
When người dùng cảm thấy nội dung AI viết chưa đúng ý và nhấp nút "[↩️ Hoàn tác]"
Then mã nguồn bài báo và danh mục trích dẫn phải lập tức khôi phục chính xác về trạng thái trước khi AI chỉnh sửa
  And bản xem trước PDF phải được tự động biên dịch lại về đúng trạng thái ban đầu
```

### Kịch bản 4: Xuất gói nộp bài hoàn chỉnh tương thích tuyệt đối
```gherkin
Given bản thảo nghiên cứu có mã nguồn, danh mục trích dẫn và 2 tệp ảnh sơ đồ
When người dùng nhấp nút "[📦 Xuất gói nộp bài]"
Then hệ thống phải tải xuống một tệp nén .zip chuẩn
  And bên trong tệp nén phải có đủ tệp mã nguồn chính, tệp trích dẫn, thư mục hình ảnh và bản in PDF
  And tệp nén có thể mở và biên dịch thành công ngay lập tức trên các nền tảng học thuật chuẩn
```

---

## 5. Quy Tắc Nghiệp Vụ Bất Biến (Business Invariants)

1. **Nguyên Tắc Tác Giả Nắm Quyền Tối Thượng (Author Sovereignty Invariant):**
   - Mọi chỉnh sửa của AI đều bắt buộc phải lưu lại bản sao chụp dự phòng.
   - Người dùng luôn có quyền hoàn tác 1-Click (`Undo`) để khôi phục trạng thái nguyên bản của mình bất kỳ lúc nào.
2. **Nguyên Tắc Ngân Sách Tự Khắc Phục Lỗi An Toàn (Self-Healing Retry Budget):**
   - Vòng lặp tự động sửa lỗi cú pháp của AI được giới hạn nghiêm ngặt ở mức tối đa **3 lần thử**.
   - Tuyệt đối cấm vòng lặp vô hạn gây tiêu tốn tài nguyên và treo trải nghiệm của người dùng.
3. **Nguyên Tắc Toàn Vẹn Gói Nộp Bài (Submission Bundle Integrity):**
   - Bản xuất gói nộp bài bắt buộc phải tự chứa đầy đủ mọi thành phần phụ thuộc (mã nguồn, danh mục trích dẫn, hình ảnh).
   - Khi giải nén trên bất kỳ hệ thống chuẩn nào đều phải biên dịch được ngay mà không bị thiếu tệp.
4. **Nguyên Tắc Bảo Mật Thực Thi Cô Lập (Sandboxed Execution Isolation):**
   - Mọi hoạt động biên dịch mã nguồn bắt buộc phải diễn ra trong môi trường ảo hóa cô lập hoàn toàn.
   - Tuyệt đối ngăn chặn các đoạn mã độc hại có khả năng truy cập tài nguyên máy chủ hay rò rỉ dữ liệu của người dùng khác.
