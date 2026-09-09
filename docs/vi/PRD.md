# TÀI LIỆU YÊU CẦU SẢN PHẨM (PRD - PRODUCT REQUIREMENTS DOCUMENT)

## 1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)
* **Tên sản phẩm:** Nền tảng Trợ lý AI Hỗ trợ Nghiên cứu và Soạn thảo Bài báo Khoa học (Academic Research & Writing Assistant).
* **Mục tiêu sản phẩm:** Giúp người làm nghiên cứu tiết kiệm thời gian đọc và viết bài báo khoa học, đồng thời đảm bảo mọi thông tin và trích dẫn đều có nguồn gốc chính xác, không bịa đặt.

---

## 2. BÀI TOÁN, NGƯỜI DÙNG & CAM KẾT BẢO MẬT

### 2.1. Người dùng mục tiêu
Sinh viên làm nghiên cứu khoa học, học viên cao học, nghiên cứu sinh và giảng viên đại học.

### 2.2. Nỗi đau thực tế của người dùng
1. **Đọc quá nhiều bài báo:** Mỗi bài dài hàng chục trang tiếng Anh, đọc rất mất thời gian mới hiểu phương pháp và kết quả.
2. **Mau quên, khó tìm lại:** Đọc xong vài chục bài thì không nhớ bài nào viết cái gì, muốn so sánh các bài với nhau cũng khó.
3. **Sợ AI "chém gió" (Bịa nguồn):** Dùng ChatGPT viết bài rất hay bịa ra các trích dẫn không có thật, hoặc trích dẫn sai nội dung tác giả viết.
4. **Mệt mỏi vì format trích dẫn và biên dịch tài liệu:**
   - Dân Kỹ thuật (dùng LaTeX/Overleaf): Phải đi copy thủ công từng đoạn mã BibTeX của 30 - 40 bài báo, hay bị lỗi biên dịch dấu câu.
   - Dân Xã hội/Kinh tế (dùng Word): Phải căn chỉnh từng dấu chấm, dấu phẩy, chữ in nghiêng theo chuẩn APA hay IEEE.

### 2.3. Cam kết Bảo mật & Quyền riêng tư của Bản thảo (Data Privacy & Confidentiality)
* **Quyền sở hữu trí tuệ:** Người nghiên cứu thường xuyên làm việc với các bản thảo chưa công bố (unpublished drafts/preprints). Mọi tài liệu do người dùng tải lên thuộc quyền sở hữu 100% của tác giả.
* **Không dùng dữ liệu để huấn luyện (Opt-out Policy):** Hệ thống cam kết không sử dụng tài liệu của người dùng để làm dữ liệu huấn luyện hoặc tinh chỉnh (fine-tune) bất kỳ mô hình AI nào.
* **Quyền kiểm soát lưu trữ:** Cho phép người dùng xóa hoàn toàn dữ liệu bản thảo và tài liệu tải lên khỏi hệ thống bất cứ lúc nào (Zero-retention on demand).

---

## 3. PHẠM VI CHỨC NĂNG CỐT LÕI (CORE SCOPE - 4 MODULES)

### Module 1: Đọc và Hiểu sâu Từng Bài báo (Tập trung vào 1 file PDF)
**Note:** Module 1 (Đọc 1 bài báo): Advanced RAG (Hybrid Search + Reranking). Cần xử lý truy vấn cục bộ (DataLocal), yêu cầu tốc độ phản hồi dưới 5s và bám sát vị trí gốc (BoundingBox).
* **Hỏi đáp trực tiếp trên bài báo:** 
  - Người dùng tải lên 1 file PDF bài báo và chat với AI như một trợ lý.
  - Có thể hỏi: *"Phương pháp chính của bài này là gì?"*, *"Công thức số (3) có ý nghĩa gì?"*, *"Kết quả thử nghiệm đạt bao nhiêu %?"*.
* **Tóm tắt nhanh 3 ý cốt lõi:** 
  - Không cần đọc hết 20 trang, AI tóm tắt ngay: (1) Bài này giải quyết vấn đề gì? (2) Đóng góp mới là gì? (3) Điểm yếu/hạn chế còn lại là gì?
* **Bấm vào câu trả lời để xem ngay trang gốc:** 
  - Khi AI trả lời bất kỳ câu nào, người dùng chỉ cần click vào là màn hình tự nhảy đến đúng số trang và đoạn văn gốc trong file PDF để đối chiếu, không sợ AI nói bừa.
* **Sổ tay lưu nhanh ý hay (Ghi chú):** 
  - Thấy đoạn văn nào hay hoặc số liệu nào quan trọng, người dùng bấm 1 nút là lưu ngay vào sổ tay để sau này lấy ra viết bài.

---

### Module 2: Hỗ trợ Viết bài và Kiểm tra Trích dẫn (Tập trung vào viết)
**Note:** Module 2 (Viết bài & Chống bịa nguồn): Không phải là RAG hỏi đáp đơn thuần, mà là Knowledge-Augmented Verification (tương tự như mô hình SAFE của Google DeepMind)
* **Phương thức nhập liệu linh hoạt:** Người dùng có thể soạn thảo trực tiếp trên trình soạn thảo thông minh của hệ thống, dán đoạn văn bản thô, hoặc tải lên file bản thảo `.tex` / `.md`.
* **Viết phần tổng quan tài liệu (Literature Review):** 
  - Giúp người dùng ghép nối các ý từ những bài báo đã đọc và Sổ tay nghiên cứu thành một đoạn văn viết mở đầu hoặc tổng quan tài liệu mạch lạc.
* **Kiểm tra xem câu mình viết có đúng sự thật không (Chống trích dẫn bậy):** 
  - Khi người dùng viết: *"Phương pháp của tác giả A đạt độ chính xác 95%"*, AI sẽ tự lục lại bài báo của A để kiểm tra xem có đúng là 95% không. Nếu sai hoặc không có trong bài báo, AI sẽ cảnh báo ngay.
* **Sửa câu từ cho chuẩn văn phong khoa học:** 
  - Chỉnh sửa câu văn tiếng Anh/tiếng Việt sao cho trang trọng, chuẩn mực học thuật, loại bỏ cách hành văn lủng củng hoặc cảm tính.
* **Xuất bản thảo hoàn chỉnh & trích dẫn chuẩn bằng 1 click:** 
  - **Cho người dùng LaTeX / Overleaf:** Xuất ra file mã `references.bib` hoàn chỉnh VÀ hỗ trợ biên dịch xuất bản thảo thành file PDF hoàn chỉnh đã được tự động sửa sạch lỗi cú pháp.
  - **Cho người dùng Word:** Xuất ra danh sách tài liệu đã được định dạng chuẩn từng dấu câu theo APA hoặc IEEE để dán vào cuối bài viết.

---

### Module 3: Tìm kiếm và Mở rộng Tài liệu (Tập trung vào tìm kiếm)
**Note:** Module 3 (Mở rộng & Lộ trình đọc): Graph-Augmented RAG. Cần mô hình hóa mối quan hệ: bài báo A trích dẫn bài báo B, bài C mở rộng bài A.
* **Tự bóc tách danh mục tài liệu tham khảo:** 
  - Người dùng tải bài báo lên, AI tự động quét và liệt kê ra danh sách tất cả các bài báo mà tác giả đó đã trích dẫn ở cuối bài.
* **Gợi ý các bài báo liên quan nên đọc:** 
  - AI tự động tìm trên mạng các bài báo có cùng chủ đề, các bài viết mở rộng từ bài này, hoặc các bài đặt nền móng quan trọng mà người dùng không nên bỏ qua.
* **Chỉ dẫn thứ tự đọc hợp lý:** 
  - Đưa ra lộ trình đọc gợi ý: *"Nên đọc bài A trước để hiểu khái niệm cơ bản, sau đó mới đọc bài B và bài C"*.

---

### Module 4: Quản lý Thư viện Bài báo Cá nhân (Tập trung vào kho nhiều bài)
**Note:** Module 4 (Kho nhiều bài, so sánh tự động): Agentic Workflow / Hierarchical RAG. Khi người dùng hỏi một câu trên 50 bài báo, hệ thống không thể ném hàng nghìn chunk vào một lần truy xuất. Cần một Agent phân rã bài toán: quét metadata của 50 bài báo $\to$ lọc ra 5 bài liên quan nhất $\to$ trích xuất thông số $\to$ tổng hợp bảng so sánh.
* **Kho lưu trữ bài báo theo thư mục:** 
  - Cho phép người dùng gom các bài báo đã tải lên vào từng thư mục hoặc đề tài nghiên cứu riêng (ví dụ: thư mục "Thị giác máy tính", thư mục "Xử lý ngôn ngữ tự nhiên").
* **Nạp tài liệu hàng loạt siêu tốc (Bulk Import):**
  - Bên cạnh việc tải từng file PDF, người dùng có thể nạp nhanh 10 - 50 bài báo cùng lúc bằng cách: Tải lên file danh mục `references.bib` hoặc dán danh sách mã DOI / ArXiv ID. Hệ thống sẽ tự động truy vết và tải toàn văn mở về kho.
* **Hỏi đáp xuyên suốt nhiều bài báo cùng lúc:** 
  - Người dùng có thể hỏi một câu cho toàn bộ kho tài liệu của mình, ví dụ: *"Trong 15 bài báo tôi đã lưu, có những bài nào dùng mô hình Transformer và kết quả bài nào tốt nhất?"*.
* **Lập bảng so sánh tự động:** 
  - AI tự gom thông tin từ nhiều bài báo lại và vẽ thành 1 bảng so sánh rõ ràng gồm các cột: Tên bài | Phương pháp | Dữ liệu thử nghiệm | Kết quả đạt được. Người dùng không cần phải tự mở từng bài ra kẻ bảng.

---

## 4. CHỈ SỐ CHẤT LƯỢNG & GIỚI HẠN KỸ THUẬT (NFRs & SLAs)

* **Giới hạn dung lượng tải lên:** Hỗ trợ file PDF dung lượng tối đa 50 MB và độ dài tối đa 100 trang cho mỗi bài báo.
* **Độ trễ phân tích tài liệu (Ingestion Latency):** Phân tích và bóc tách bố cục một bài báo 15 - 20 trang hoàn tất dưới 15 giây.
* **Thời gian phản hồi hỏi đáp (Q&A Latency):** Trả lời câu hỏi kèm số trang trích dẫn dưới 5 giây.
* **Thời gian kiểm chứng luận điểm (Fact-checking SLA):** Hoàn thành rà soát và gán nhãn đúng/sai cho một đoạn văn bản (3 - 5 câu trích dẫn) trong vòng dưới 10 giây thông qua cơ chế xử lý song song.
* **Thời gian biên dịch tài liệu Sandbox:** Giới hạn tối đa 60 giây cho mỗi lượt biên dịch file PDF.

---

## 5. CÁC HƯỚNG MỞ RỘNG CHO TƯƠNG LAI
*(Giai đoạn 2 - Tính năng mở rộng nâng cao, chỉ thực hiện khi 4 module cốt lõi đã hoàn thiện và còn thời gian)*

1. **Vẽ sơ đồ mạng lưới bài báo (Citation Graph):** 
   - Vẽ các bài báo thành các chấm tròn và đường nối trên màn hình để người dùng nhìn thấy trực quan bài nào sinh ra từ bài nào, bài nào là trung tâm của ngành.
2. **Đóng vai người phản biện khó tính (Reviewer):** 
   - AI đóng vai giáo sư khó tính chấm thử bài viết của sinh viên, chỉ ra các chỗ viết còn thiếu bằng chứng, lập luận yếu để sửa trước khi nộp bài.
3. **Đồng bộ trực tiếp hai chiều với Zotero và Mendeley:** 
   - Bấm 1 nút để đồng bộ hóa kho tài liệu trực tiếp với tài khoản Zotero/Mendeley của người dùng.
