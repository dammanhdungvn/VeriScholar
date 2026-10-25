# VERISCHOLAR MVP — TÀI LIỆU YÊU CẦU SẢN PHẨM: TỔNG QUAN HỆ THỐNG & ĐỊNH HÌNH PHẠM VI
# (PRODUCT REQUIREMENTS DOCUMENT: SYSTEM OVERVIEW & SCOPE BOUNDARIES)

**Mã phân hệ:** `PRD-00`  
**Phiên bản:** `2.0-OFFICIAL`  
**Vai trò phụ trách:** Chuyên viên Phân tích Nghiệp vụ (Lead Business Analyst — BA)  
**Tài liệu Kỹ thuật liên đới:** [`00-foundation-architecture-and-db.md`](../specs/00-foundation-architecture-and-db.md)  
**Trạng thái:** CHÍNH THỨC BAN HÀNH (RELEASE CANDIDATE)

---

## 1. Tầm Nhìn Sản Phẩm & Bối Cảnh Nghiệp Vụ (Vision & Problem Statement)

### 1.1. Tầm nhìn sản phẩm (Product Vision)
**VeriScholar** là nền tảng trợ lý trí tuệ nhân tạo toàn trình phục vụ hoạt động nghiên cứu khoa học, được thiết kế chuyên biệt cho sinh viên tài năng, học viên cao học, nghiên cứu sinh và giảng viên đại học. Hệ thống giải quyết trọn vẹn chu trình nghiên cứu học thuật khép kín: từ lúc người học chưa có tài liệu, bắt đầu khám phá đề tài, đọc hiểu sâu bài báo có bảo chứng nguồn gốc trực quan, mở rộng mạng lưới tri thức đa bài báo, đến tự động hóa quy trình soạn thảo và xuất bản báo cáo khoa học theo chuẩn LaTeX/Overleaf.

### 1.2. Nỗi đau thực tế của người làm nghiên cứu (Target Pain Points — Có Định Lượng Học Thuật)
Qua khảo sát thực tế quy trình nghiên cứu khoa học tại các phòng thí nghiệm (Research Labs) thuộc khối ngành Khoa học Máy tính, Trí tuệ Nhân tạo và Khoa học Tự nhiên:
1. **Khởi đầu bế tắc & Nhiễu loạn nguồn tin (Cold-Start & Predatory Noise):** Khi bắt đầu tiếp cận một hướng nghiên cứu mới (Literature Review), sinh viên và học viên cao học mất trung bình **45% – 60% thời gian tuần đầu tiên** chỉ để lọc thủ công qua hàng trăm kết quả tìm kiếm từ khóa rời rạc, dễ bị lạc vào các bài báo chưa qua phản biện hoặc các tạp chí săn mồi (Predatory Journals) thay vì tiếp cận đúng các công trình nền tảng (Seminal Papers).
2. **Rào cản ngôn ngữ hàn lâm và nỗi sợ Ảo giác số liệu (Empirical AI Hallucination):** Các bài báo đỉnh cao (hội nghị hạng A* như NeurIPS, ICML, ACL, CVPR hoặc tạp chí Q1) sử dụng tiếng Anh học thuật cô đọng với mật độ ký hiệu toán học dày đặc. Khi đưa bài báo vào các công cụ AI đàm thoại phổ thông, tỷ lệ AI **tự bịa đặt số liệu bảng thực nghiệm (Ablation/Baseline Tables) hoặc trộn lẫn công thức giữa các bài báo lên tới 30% – 40%**. Đối với học giả, một con số trích dẫn sai vào khóa luận hay bài báo quốc tế đồng nghĩa với việc hủy hoại uy tín khoa học. Hơn nữa, AI phổ thông thường giải thích nhảy cóc từ khái niệm cơ bản sang định lý phức tạp mà thiếu lộ trình sư phạm tuần tự.
3. **Đứt gãy mạch tư duy khi truy vết tài liệu tham khảo (Context-Switching Fatigue):** Khi đang đọc hiểu một phương pháp ở trang 4 và bắt gặp ký hiệu trích dẫn quan trọng (ví dụ `[14]`), học giả buộc phải dừng đọc, cuộn xuống mục Tài liệu tham khảo ở trang cuối, sao chép tiêu đề, mở tab trình duyệt mới, tìm tệp PDF, tải về máy và mở bằng ứng dụng đọc rời rạc. Các nghiên cứu về nhận thức chỉ ra mỗi lần chuyển ngữ cảnh thủ công này làm tiêu tốn **15 – 23 phút** để não bộ khôi phục lại trạng thái tập trung sâu (Deep Flow) ban đầu.
4. **Cô lập tri thức cá nhân & Thất thoát phát hiện nghiên cứu (Fragmented Knowledge Silos):** Sau khi đọc từ 20 đến 50 bài báo cho một đề tài, hơn **70% ghi chú cá nhân** bị bỏ quên trong các tệp văn bản rời rạc hoặc sổ tay cá nhân. Học giả không có công cụ trực quan để liên kết *Phương pháp (Method)* của bài báo A với *Tập dữ liệu (Dataset)* của bài báo B và *Chỉ số đánh giá (Metric Result)* của bài báo C nhằm phát hiện khoảng trống nghiên cứu (Research Gap) cho mục *Related Work*.
5. **Cực hình cơ học trong soạn thảo LaTeX (LaTeX Mechanical Friction):** Trong giai đoạn viết báo cáo hoặc bản thảo công bố quốc tế, các nhóm nghiên cứu mất trung bình **6 – 10 giờ cho mỗi bản thảo** chỉ để xử lý các công việc cơ học lặp đi lặp lại: kẻ bảng kết quả phức tạp (`\multirow`, `\multicolumn`), đồng bộ thủ công khóa trích dẫn BibTeX (tránh lỗi hiển thị `[?]` trên bản in), và dò tìm từng dòng nhật ký biên dịch dài hàng nghìn dòng khi thiếu dấu ngoặc hoặc xung đột gói lệnh.

### 1.3. Bảng Đối Chiếu Giá Trị Trước & Sau Khi Áp Dụng VeriScholar (Before vs. After Value Matrix)

| Tiêu chí Nghiệp vụ Học thuật | Quy trình truyền thống (Zotero + Trình đọc PDF + AI rời rạc + Overleaf) | Quy trình Hợp nhất Toàn trình trên VeriScholar MVP |
| :--- | :--- | :--- |
| **Tìm kiếm & Khởi tạo đọc** | Tìm trên Google Scholar $\rightarrow$ Tải file về ổ cứng $\rightarrow$ Nhập vào phần mềm quản lý $\rightarrow$ Mở trình đọc (4 công cụ rời rạc). | Nhập ý niệm nghiên cứu $\rightarrow$ Xem tóm tắt học thuật $\rightarrow$ Bấm **1-Click mở thẳng vào Không gian Đọc sâu** (< 10 giây). |
| **Kiểm chứng câu trả lời của AI** | Tự đọc dò lại từng trang PDF bằng mắt thường để xem AI có bịa số liệu hay không (mất 5 – 10 phút/câu). | Bấm vào huy hiệu dẫn chứng $\rightarrow$ Khung đọc tự cuộn đến đúng trang và vẽ **Khung viền vàng (Visual Grounding)** trong **< 1 giây**. |
| **Tra cứu trích dẫn trong bài `[14]`** | Cuộn xuống cuối bài $\rightarrow$ Copy tên bài $\rightarrow$ Tìm Google $\rightarrow$ Mở tab mới (Đứt mạch tư duy hoàn toàn). | Xem tóm tắt tức thì tại **Bảng Ngữ cảnh 3 Cột (< 500ms)** và mở ngay thành **Tab đọc song song** trong cùng màn hình. |
| **Tổng hợp mục Related Work** | Mở hàng chục cửa sổ PDF cạnh nhau, tự ghi nhớ bài nào dùng phương pháp gì trên tập dữ liệu nào. | Nhìn trực quan trên **Đồ thị Tri thức 4 Thực thể** và hỏi đáp tổng hợp chéo có bảo chứng đa bài báo. |
| **Soạn thảo & Sửa lỗi LaTeX** | Tự copy-paste mã LaTeX qua lại giữa cửa sổ chat AI và trình soạn thảo; tự đọc log sửa lỗi biên dịch. | **Trợ lý Đồng tác giả AI** tự tra cứu kho bài báo, tự chèn trích dẫn, tự biên dịch hộp cát và tự sửa lỗi trước khi trình bày. |

---

## 2. Chân Dung Tác Nhân Sử Dụng Hệ Thống (User Personas & Actors)

Hệ thống phục vụ 3 nhóm tác nhân chính:

| Tác nhân (Actor) | Bối cảnh sử dụng | Mục tiêu cốt lõi | Yêu cầu trải nghiệm quan trọng nhất |
| :--- | :--- | :--- | :--- |
| **Sinh viên & Nghiên cứu sinh mới (Junior Researcher)** | Bắt đầu làm khóa luận tốt nghiệp hoặc nghiên cứu đề tài khoa học sinh viên. | Hiểu đúng bản chất thuật toán, nắm được số liệu thực nghiệm gốc và có lộ trình học tuần tự không nhảy cóc. | Mọi câu trả lời của AI phải bấm vào được để nhảy đến đúng trang PDF và hiển thị **Khung viền vàng** bao quanh đoạn văn gốc để kiểm chứng bằng mắt trong 1 giây. |
| **Nghiên cứu sinh & Giảng viên (Senior Scholar / Mentor)** | Viết bài báo khoa học công bố quốc tế, chuẩn bị tài liệu giảng dạy, đối chiếu phương pháp. | Mở rộng nhanh ngữ cảnh bài báo liên quan, tổng hợp tri thức đa bài báo và tự động hóa soạn thảo LaTeX. | Không gian viết 3 cột đồng bộ, AI gợi ý chỉnh sửa trực tiếp vào mã nguồn bản thảo và kiểm tra biên dịch không lỗi. |
| **Hệ thống xử lý ngầm (System Background Worker)** | Tác nhân tự động của nền tảng chạy ngầm độc lập. | Tải file PDF từ nguồn mở, bóc tách cấu trúc tài liệu, tính toán vector và trích xuất đồ thị tri thức. | Hoạt động tin cậy, không làm gián đoạn trải nghiệm tương tác thời gian thực của người dùng trên giao diện. |

---

## 3. Cấu Trúc Điều Hướng Toàn Cục & Ranh Giới Tính Năng (Global Navigation & Boundaries)

Nhằm tối ưu hóa công thái học (Ergonomics) và loại bỏ hoàn toàn tình trạng giao diện cồng kềnh, phân tán, VeriScholar thống nhất giao diện ứng dụng xoay quanh đúng **4 mục điều hướng cốt lõi trên thanh Sidebar toàn cục**:

```text
+-----------------------------------------------------------------------------------+
| VERISCHOLAR GLOBAL NAVIGATION                                                     |
+-----------------------------------------------------------------------------------+
| [1] 🔍 Khám phá & Phiên đọc (/discovery & /dashboard)                             |
|     - Khám phá bài báo theo chủ đề (Học thuật mở Exa AI & arXiv).                 |
|     - Tải tài liệu PDF cá nhân lên hệ thống (Kèm cam kết tiêu hủy vật lý).        |
|     - Quản lý danh sách các Phiên đọc sâu đa bài báo (Sessions).                  |
|                                                                                   |
| [2] ⭐ Kho Yêu thích (/library)                                                   |
|     - Quản lý cây thư mục đề tài nghiên cứu phân cấp.                             |
|     - Tra cứu và tổng hợp liên kết trên Đồ thị Tri thức học thuật 4 thực thể.     |
|                                                                                   |
| [3] ✍️ Soạn thảo LaTeX (/writing)                                                 |
|     - Quản lý danh sách Bản thảo học thuật cá nhân.                               |
|     - Không gian làm việc 3 cột: Cây tệp -> Trình soạn thảo -> Khung xem trước.   |
|     - Trợ lý AI đồng tác giả hỗ trợ viết, sửa lỗi biên dịch và xuất bản thảo.     |
|                                                                                   |
| [4] 👤 Tài khoản & Cấu hình (/profile & /settings)                                |
|     - Quản lý hồ sơ nghiên cứu cá nhân (ORCID, học hàm, đơn vị công tác).         |
|     - Quản lý khóa riêng tư bảo mật BYOK (Bring Your Own Key).                   |
|     - Chuyển đổi giao diện Sáng / Tối (Light / Dark Mode).                         |
+-----------------------------------------------------------------------------------+
```

---

## 4. Chuỗi 6 Luồng Giá Trị Học Thuật Khép Kín (The 6 Closed Value Flows)

1. **Khởi đầu từ con số 0 (Academic Discovery):** Người dùng nhập từ khóa hoặc chủ đề nghiên cứu $\rightarrow$ Hệ thống tra cứu qua kho tri thức học thuật mở $\rightarrow$ Xem trước tóm tắt và mở đọc trực tiếp bài báo Open Access chỉ với 1 thao tác bấm.
2. **Đọc sâu & Hỏi đáp có Bảo chứng Trực quan (Deep Reading & Grounded RAG):** Đọc PDF gốc trên khung đọc bên trái, trao đổi bằng Tiếng Việt với Trợ lý AI bên phải; mọi nhận định, số liệu thực nghiệm đều gắn huy hiệu dẫn chứng. Bấm vào huy hiệu, màn hình tự động cuộn đến trang gốc và vẽ **Khung viền vàng (Visual Grounding Bounding Box)** bao quanh chứng cứ. Cung cấp **Lộ trình học tuần tự (A $\rightarrow$ B $\rightarrow$ C $\rightarrow$ D)** để giải thích từ gốc rễ.
3. **Mở rộng Ngữ cảnh Không đứt mạch (Context Table & 2-Tier Resolution):** Tự động bóc tách danh mục tài liệu tham khảo cuối bài báo sang Bảng Ngữ cảnh 3 Cột; bấm 1-Click xem ngay tóm tắt tài liệu liên quan (< 500ms) và tải ngầm bài báo để mở thêm Tab đọc song song (tối đa 5 bài).
4. **Kho Tri thức & Mạng lưới Liên kết Chéo (Favorite Library & Cross-Paper Graph):** Đánh dấu bài báo quan tâm vào Thư mục đề tài $\rightarrow$ Tự động phân tích và kết nối thành Đồ thị Tri thức 4 thực thể (`Bài báo`, `Phương pháp`, `Tập dữ liệu`, `Kết quả thực nghiệm`), cho phép đặt các câu hỏi tổng hợp chéo giữa các bài báo trong kho.
5. **Soạn thảo Bản thảo Học thuật Tự động (Agentic LaTeX Writing Workspace):** Kế thừa tài liệu và các trích dẫn quan trọng từ phiên đọc sang không gian soạn thảo 3 cột; Trợ lý AI đóng vai trò Đồng tác giả tự động chỉnh sửa nội dung, quản lý file trích dẫn, và biên dịch kiểm thử độc lập trong môi trường cách ly an toàn.
6. **Bảo mật Riêng tư & Minh bạch Hệ thống (Privacy & Tracing):** Đồng bộ mã định danh giám sát xuyên suốt hành trình; cam kết tiêu hủy vật lý tức thì tài liệu khi học giả xóa bài báo (Zero-Retention Guarantee); hỗ trợ người dùng tự mang khóa API cá nhân (BYOK) được mã hóa bảo mật.

### 4.1. Kịch Bản Nghiệp Vụ Cốt Lõi: Hành Trình Nghiên Cứu Khép Kín Toàn Trình (`UC-SYS-01`)
* **Tác nhân chính:** Học giả nghiên cứu (Sinh viên / Nghiên cứu sinh / Giảng viên).
* **Điều kiện tiên quyết (Pre-conditions):** Học giả đã đăng nhập vào tài khoản cá nhân trên VeriScholar và cấu hình sẵn khóa AI cá nhân (hoặc sử dụng hạn mức mặc định của hệ thống).
* **Sự kiện kích hoạt (Trigger):** Học giả bắt đầu một đề tài nghiên cứu mới từ một ý tưởng sơ khởi và cần hoàn thành một bản thảo tổng quan tài liệu (Literature Review) chuẩn học thuật.
* **Luồng sự kiện chính (Happy Path):**
  1. Học giả truy cập mục **Khám phá & Phiên đọc**, nhập chủ đề nghiên cứu để tìm kiếm các bài báo nguồn mở uy tín và chọn nạp bài báo nền tảng đầu tiên vào hệ thống.
  2. Hệ thống phân tích cấu trúc bài báo và mở ra **Không gian Đọc sâu**. Học giả đặt câu hỏi bằng Tiếng Việt và bấm vào huy hiệu trích dẫn để kiểm chứng trực tiếp qua **Khung viền vàng** trên trang PDF gốc; đồng thời lưu lại các đoạn nhận định đắt giá vào **Sổ tay Phiên đọc**.
  3. Khi gặp một trích dẫn nền tảng quan trọng trong bài, học giả mở **Bảng Ngữ cảnh 3 Cột**, xem tóm tắt nhanh trong chưa đầy nửa giây và bấm mở bài báo đó thành **Tab đọc thứ hai** ngay trong cùng phiên làm việc để đối chiếu.
  4. Học giả đánh dấu Yêu thích (Star) các bài báo cốt lõi vào một Thư mục đề tài trong **Kho Yêu thích**, quan sát **Đồ thị Tri thức 4 Thực thể** tự động kết nối các phương pháp và tập dữ liệu giữa các bài, sau đó thực hiện truy vấn tổng hợp chéo.
  5. Từ phiên đọc, học giả bấm chuyển sang **Không gian Soạn thảo LaTeX 3 Cột**, yêu cầu Trợ lý Đồng tác giả AI viết mục Tổng quan tài liệu dựa trên các bài báo và ghi chú đã thu thập. Hệ thống tự động cập nhật mã nguồn, điền danh mục trích dẫn và biên dịch ra bản xem trước PDF hoàn chỉnh.
* **Kết quả đầu ra (Post-conditions):**
  * Học giả sở hữu một bộ sưu tập bài báo đã được kiểm chứng số liệu gốc, một đồ thị tri thức liên kết rõ ràng, và một bản thảo khoa học biên dịch thành công sẵn sàng tải xuống nộp bài.
  * Toàn bộ lịch sử hội thoại, ghi chú trích dẫn và nhật ký giám sát chất lượng được lưu trữ cô lập tuyệt đối trong không gian cá nhân của học giả.
* **Luồng ngoại lệ & Ràng buộc an toàn toàn cục (System-Wide Exception Flows):**
  * **Ngoại lệ 4.1a — Truy vấn thông tin nằm ngoài phạm vi tài liệu (Out-of-Document Empirical Query):** Nếu học giả yêu cầu trích xuất một con số thực nghiệm hoặc siêu tham số không hề tồn tại trong các bài báo đang mở, hệ thống bắt buộc từ chối suy đoán, thông báo rõ *"Thông tin này không được đề cập trong các tài liệu hiện tại"* và tuyệt đối không tự sinh số liệu giả.
  * **Ngoại lệ 4.1b — Ngăn chặn truy cập chéo trái phép (Cross-Tenant Access Attempt):** Nếu một người dùng cố tình truy cập đường dẫn tài liệu, phiên đọc, thư mục hoặc bản thảo thuộc sở hữu của học giả khác, hệ thống lập tức chặn đứng và trả về thông báo không tìm thấy tài nguyên, đảm bảo bí mật nghiên cứu tuyệt đối.
  * **Ngoại lệ 4.1c — Thu hồi và tiêu hủy tài liệu chưa công bố (Zero-Retention Purge):** Khi học giả xóa một bài báo nhạy cảm khỏi hệ thống, tệp vật lý và toàn bộ dữ liệu trích xuất bị xóa sạch ngay lập tức, nhưng các ghi chú cá nhân trong sổ tay phiên đọc vẫn được bảo toàn nguyên vẹn dưới dạng bản chụp văn bản độc lập để không làm mất công sức ghi chép của học giả.

---

## 5. Ranh Giới Nghiệp Vụ Nghiêm Ngặt (Strict Scope Boundaries)

Để đảm bảo tính khả thi, chất lượng hoàn thiện cao nhất và sự tập trung tuyệt đối vào trải nghiệm cốt lõi của đồ án, nền tảng đặt ra các ranh giới bất biến sau:

### 5.1. Phạm vi chuẩn mực thực hiện (In-Scope)
* Hoàn thiện trọn vẹn và mượt mà chuỗi 6 luồng giá trị nêu trên.
* Đảm bảo đầy đủ các thao tác nghiệp vụ **Thêm / Xem / Sửa / Xóa (CRUD)** cho toàn bộ các đối tượng dữ liệu của người dùng: Tài khoản cá nhân, Tài liệu nghiên cứu, Phiên đọc sâu & Hội thoại, Thư mục đề tài, và Bản thảo LaTeX kèm hình ảnh tài sản.
* Cung cấp trải nghiệm thị giác nhất quán trên cả hai chế độ màu Sáng (Light) và Tối (Dark).

### 5.2. Ranh giới tuyệt đối không thực hiện trong MVP (Strictly Out-of-Scope)
1. **Không dịch toàn văn PDF sang Tiếng Việt để thay thế khung đọc gốc:** Khung đọc bên trái luôn hiển thị trung thực bản PDF tiếng Anh gốc của tác giả nhằm đảm bảo tính chính xác học thuật cao nhất. Nhu cầu dịch hoặc giải thích được đáp ứng linh hoạt qua khung hội thoại AI bên phải hoặc menu bôi đen văn bản nhanh.
2. **Không làm tính năng cộng tác nhóm nhiều người cùng gõ đồng thời (Real-time Collaborative Editing):** MVP tập trung vào không gian làm việc cá nhân của từng học giả độc lập; không xây dựng hệ thống phân quyền tổ chức phức tạp hay con trỏ chuột nhiều người kiểu Google Docs.
3. **Không tích hợp dịch vụ biên dịch đám mây ngoài (như gọi sang web Overleaf công cộng):** Toàn bộ quy trình soạn thảo và biên dịch PDF xem trước được xử lý nội bộ, bảo vệ quyền riêng tư tuyệt đối cho các ý tưởng nghiên cứu chưa công bố.
4. **Không xây dựng tính năng Ma trận So sánh hàng trăm bài báo (Comparison Matrix):** Nghiệp vụ tổng hợp tri thức tập trung vào đồ thị liên kết chéo 4 thực thể gọn gàng, tránh tạo ra các bảng số liệu dàn trải kém giá trị.

### 5.3. Các điều cấm kỵ nghiệp vụ (Anti-Goals — Vi phạm coi như lỗi nghiêm trọng)
1. **Tuyệt đối cấm AI tự bịa đặt số liệu (Zero-Hallucination on Empirical Data):** Mọi con số thực nghiệm, tên mô hình cơ sở hay cấu hình siêu tham số do AI đưa ra bắt buộc phải bám sát nội dung bài báo đang mở trong phiên đọc. Nếu thông tin không có trong bài, AI phải nói rõ là tài liệu không đề cập.
2. **Tuyệt đối cấm rò rỉ dữ liệu giữa các học giả (Zero-Cross-Tenant Leakage):** Tài liệu PDF, câu hỏi hội thoại và bản thảo nghiên cứu của học giả A tuyệt đối không bao giờ được hiển thị hoặc gợi ý cho học giả B dưới bất kỳ hình thức nào.
3. **Tuyệt đối không lưu trữ tài liệu mồ côi (Zero-Retention Violation):** Khi học giả quyết định xóa bài báo, toàn bộ dữ liệu văn bản và tệp vật lý tương ứng trên máy chủ phải bị tiêu hủy dứt điểm.

---

## 6. Danh Mục 8 Tài Liệu PRD Chuyên Biệt Theo Phân Hệ (PRD Module Index)

Toàn bộ tài liệu nghiệp vụ chi tiết được phân rã thành các tệp độc lập, đóng gói hoàn chỉnh theo từng cụm tính năng:

| Mã PRD | Tên Tệp Tài Liệu | Nội Dung Nghiệp Vụ Chuyên Trách | Tài Liệu Kỹ Thuật Tương Ứng |
| :--- | :--- | :--- | :--- |
| **PRD-00** | [`00-overview-and-cleanup.md`](./00-overview-and-cleanup.md) | Tổng quan kiến trúc, ranh giới phạm vi, 4 mục điều hướng chính và các bất biến sản phẩm. | [`00-foundation-architecture-and-db.md`](../specs/00-foundation-architecture-and-db.md) |
| **PRD-01** | [`01-auth-and-user.md`](./01-auth-and-user.md) | Đăng ký, Đăng nhập, Xác thực mã OTP, Hồ sơ học giả, Cấu hình giao diện và Cơ chế bảo vệ khóa riêng BYOK. | [`01-auth-and-user-spec.md`](../specs/01-auth-and-user-spec.md) |
| **PRD-02** | [`02-discovery-and-documents-crud.md`](./02-discovery-and-documents-crud.md) | Khám phá bài báo học thuật mở theo chủ đề, Tải tài liệu PDF lên và Quản lý danh mục bài báo cá nhân. | [`02-discovery-and-documents-spec.md`](../specs/02-discovery-and-documents-spec.md) |
| **PRD-03** | [`03-sessions-and-deep-reading-crud.md`](./03-sessions-and-deep-reading-crud.md) | Không gian Đọc sâu đa bài báo (1–5 tab), Hỏi đáp có Khung viền vàng Bounding Box, Menu bôi đen và Sổ tay trích dẫn nhúng. | [`03-sessions-and-deep-reading-spec.md`](../specs/03-sessions-and-deep-reading-spec.md) |
| **PRD-04** | [`04-context-table-and-roadmap.md`](./04-context-table-and-roadmap.md) | Bảng Ngữ cảnh 3 Cột phân tích tài liệu tham khảo cuối bài, Nạp thông tin 2 tầng và Gợi ý Lộ trình học tuần tự (A $\rightarrow$ B $\rightarrow$ C $\rightarrow$ D). | [`04-context-table-and-roadmap-spec.md`](../specs/04-context-table-and-roadmap-spec.md) |
| **PRD-05** | [`05-favorite-library-and-graphrag.md`](./05-favorite-library-and-graphrag.md) | Đánh dấu Star, Quản lý Cây thư mục đề tài nghiên cứu và Mạng lưới Đồ thị Tri thức học thuật 4 thực thể. | [`05-favorite-library-and-graphrag-spec.md`](../specs/05-favorite-library-and-graphrag-spec.md) |
| **PRD-06** | [`06-agentic-overleaf-writing.md`](./06-agentic-overleaf-writing.md) | Màn hình viết bài LaTeX 3 cột, Quản lý bản thảo & hình ảnh, Trợ lý AI đồng tác giả và Biên dịch hộp cát an toàn. | [`06-agentic-overleaf-writing-spec.md`](../specs/06-agentic-overleaf-writing-spec.md) |
| **PRD-07** | [`07-monitoring-and-langfuse.md`](./07-monitoring-and-langfuse.md) | Giám sát chất lượng phản hồi AI, Đánh giá độ tin cậy trích dẫn, Cảnh báo sự cố máy chủ và Kiểm tra sức khỏe hệ thống. | [`07-monitoring-and-langfuse-spec.md`](../specs/07-monitoring-and-langfuse-spec.md) |
