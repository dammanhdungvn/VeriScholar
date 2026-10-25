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

### 1.2. Nỗi đau thực tế của người làm nghiên cứu (Target Pain Points)
Qua khảo sát thực tế quy trình nghiên cứu khoa học tại các trường đại học khối ngành Công nghệ và Khoa học Tự nhiên:
1. **Khởi đầu bế tắc (Cold-Start Problem):** Khi bắt đầu tiếp cận một chủ đề mới, sinh viên không biết tìm kiếm bài báo chuẩn mực ở đâu, thường bị lạc vào các nguồn tài liệu trôi nổi kém chất lượng.
2. **Rào cản ngôn ngữ và toán học chuyên sâu:** Các bài báo đỉnh cao (Top-tier Conferences/Journals) sử dụng tiếng Anh học thuật hàn lâm với mật độ công thức toán dày đặc. Khi tra cứu qua các công cụ AI đàm thoại thông thường (ChatGPT/Claude), người dùng luôn lo sợ hiện tượng **ảo giác (AI Hallucination)** — AI tự bịa đặt số liệu thực nghiệm, đoán mò xuất xứ tài liệu, hoặc giải thích nhảy cóc từ khái niệm cơ bản sang định lý phức tạp mà không có lộ trình sư phạm.
3. **Hiện tượng đứt mạch tư duy (Context Switching Fatigue):** Khi đang đọc bài báo bắt gặp trích dẫn quan trọng (ví dụ `[14]`), học giả buộc phải cuộn xuống mục References ở cuối trang, mở tab trình duyệt mới, tìm kiếm file PDF và đọc độc lập. Thao tác thủ công này làm phân mảnh sự chú ý và mất tính liền mạch trong suy nghĩ.
4. **Cô lập tri thức cá nhân (Fragmented Knowledge):** Đọc xong bài báo, các ghi chú và phát hiện quan trọng thường bị bỏ quên trong các file Word hoặc sổ tay cá nhân rải rác, không thể liên kết phương pháp của bài báo A với tập dữ liệu của bài báo B để tìm ra ý tưởng nghiên cứu mới.
5. **Cực hình soạn thảo học thuật (LaTeX Friction):** Việc viết báo cáo hoặc bài báo bằng LaTeX đòi hỏi người viết phải tự gõ từng cấu trúc bảng biểu, quản lý thủ công tệp trích dẫn BibTeX và tự xử lý hàng loạt lỗi biên dịch khó hiểu từ trình biên dịch.

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
