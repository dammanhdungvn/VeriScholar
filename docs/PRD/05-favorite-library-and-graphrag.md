# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (PRD): KHO BÀI BÁO YÊU THÍCH & MẠNG TRI THỨC HỌC THUẬT 4 THỰC THỂ
# (FAVORITE PAPERS LIBRARY & 4-ENTITY ACADEMIC KNOWLEDGE GRAPH)

**Mã tài liệu:** `PRD-05`  
**Thuộc giải pháp:** VeriScholar AI Research Assistant  
**Vai trò tác giả:** Chuyên viên Phân tích Nghiệp vụ (Business Analyst)  
**Tài liệu kỹ thuật đối ứng:** [`05-favorite-library-and-graphrag-spec.md`](../specs/05-favorite-library-and-graphrag-spec.md)  
**File nền tảng liên đới:** [`00-overview-and-cleanup.md`](./00-overview-and-cleanup.md)  

---

## 1. Tầm Nhìn Nghiệp Vụ & Nỗi Đau Người Dùng (Business Context & Pain Points)

Trong chu kỳ nghiên cứu khoa học kéo dài nhiều tháng hoặc nhiều năm, một học giả phải tiếp cận, tích lũy và đối chiếu hàng trăm công trình học thuật khác nhau:
- **Nỗi đau 1 — Thư viện tài liệu trở thành "kho phế liệu" hỗn độn:** Khi đọc nhiều bài báo trên các nền tảng phân tán, học giả thường lưu trữ tệp tài liệu rải rác trong các thư mục máy tính cá nhân hoặc danh sách dấu trang trình duyệt. Sau vài tháng, họ không còn nhớ bài báo chứng minh định lý toán này nằm ở đâu, bài báo đạt độ chính xác cao nhất về thị giác máy tính tên là gì, dẫn đến việc phải tìm kiếm và đọc lại từ đầu.
- **Nỗi đau 2 — Tri thức giữa các bài báo bị phân mảnh và cô lập (Isolated Silos):** Các bài báo khoa học trong cùng một chuyên ngành luôn có mối quan hệ hữu cơ: bài báo A đề xuất mô hình gốc, bài báo B cải tiến hàm tối ưu của mô hình đó, bài báo C thử nghiệm trên tập dữ liệu chuẩn mới. Hiện nay, các phần mềm quản lý trích dẫn thông thường chỉ xem bài báo như các tệp tĩnh đơn lẻ, không thể cho người dùng thấy được mạng lưới quan hệ chéo giữa các phương pháp và kết quả thực nghiệm.
- **Nỗi đau 3 — Mất từ 30 đến 50 giờ làm việc căng thẳng để tổng hợp bảng so sánh thực nghiệm SOTA khi bị Reviewer #2 chất vấn:** Trong các kỳ phản biện hội nghị khoa học quốc tế uy tín (như NeurIPS, ICML, ICLR, CVPR, ACL, KDD) hoặc các tạp chí nhóm Q1/A* (IEEE TPAMI, ACM TOIS), thời gian phản hồi (Rebuttal) thường bị siết chặt trong vòng 7 đến 10 ngày. Khi phản biện viên thứ hai (Reviewer #2) đưa ra những chất vấn gay gắt: *"Tại sao tác giả không đối chiếu thực nghiệm với các công trình nền tảng công bố năm 2024?", "Bảng thực nghiệm thiếu so sánh định lượng với baseline X trên tập dữ liệu benchmark Y"*, tác giả phải đối mặt với áp lực khổng lồ. Họ phải mất từ **30 đến 50 giờ làm việc căng thẳng** để lật lại 20–30 bài báo gốc, rà soát từng bảng kết quả thử nghiệm mở rộng và phần phụ lục (Appendix), thủ công sao chép từng con số đo lường (như BLEU, Top-1 Accuracy, F1-score, độ trễ suy luận). Công việc này vừa gây kiệt sức, vừa tiềm ẩn rủi ro chí mạng: chỉ cần chép sai một chữ số thập phân hoặc nhầm phiên bản phân chia tập dữ liệu kiểm thử, bài báo có thể bị nghi ngờ về tính trung thực học thuật và nhận quyết định từ chối xuất bản.
- **Nỗi đau 4 — Phân hóa và xung đột số liệu thực nghiệm giữa các công bố độc lập (Divergent Experimental Results):** Trong thực tế nghiên cứu, nhiều bài báo cùng đánh giá một mô hình nền tảng trên cùng một tập dữ liệu benchmark nhưng lại công bố các con số hiệu năng chênh lệch đáng kể (do khác biệt về cách tiền xử lý dữ liệu, thiết lập siêu tham số hoặc điều kiện phần cứng thử nghiệm). Người nghiên cứu hiện thiếu một công cụ đồ thị tự động phát hiện, cảnh báo sự phân hóa số liệu này và cung cấp ngữ cảnh đối chiếu đa chiều phục vụ lập luận khoa học chặt chẽ.

VeriScholar giải quyết trọn vẹn những thách thức trên thông qua phân hệ:
1. **Kho Bài Báo Yêu Thích & Cây Thư Mục Đề Tài:** Cho phép người dùng phân loại tài liệu tâm đắc theo từng dự án hoặc chủ đề nghiên cứu cá nhân.
2. **Mạng Tri Thức Học Thuật 4 Thực Thể (4-Entity Knowledge Graph):** Tự động bóc tách bài báo thành các thực thể chuẩn hóa và kết nối chúng thành một đồ thị tri thức sống động.
3. **Truy Vấn Tổng Hợp Đa Tài Liệu Tức Thì (Cross-Paper Synthesis Query):** Cho phép hỏi đáp so sánh thực nghiệm giữa tất cả các bài báo trong kho chỉ bằng một câu lệnh ngôn ngữ tự nhiên.

---

## 2. Các Tác Nhân Tham Gia (Actors)

| Tác nhân | Vai trò trong phân hệ | Trách nhiệm & Kỳ vọng |
| :--- | :--- | :--- |
| **Nhà Nghiên Cứu / Học Giả** | Người sở hữu và khai thác kho tri thức cá nhân | Đánh dấu yêu thích bài báo, tạo cây thư mục đề tài, tra cứu tổng hợp và so sánh thực nghiệm đa tài liệu. |
| **Động Cơ Tri Thức Đồ Thị** | Hệ thống tự động phân tích và kết nối tri thức | Tự động bóc tách 4 loại thực thể học thuật khi bài báo được yêu thích, hợp nhất các khái niệm dùng chung và liên kết quan hệ chéo. |
| **Trợ Lý Soạn Thảo Tích Hợp** | Tác nhân liên thông trong quy trình viết bài | Tự động truy cập mạng tri thức trong kho để trích xuất bằng chứng số liệu và tài liệu tham khảo phục vụ soạn thảo bản thảo. |

---

## 3. Danh Sách Use Cases Chi Tiết (Structured Use Cases)

### UC-LIB-01: Quản Lý Cây Thư Mục Đề Tài & Phân Loại Bài Báo
- **Tác nhân:** Nhà Nghiên Cứu.
- **Tiền điều kiện:** Người dùng đã đăng nhập vào hệ thống và truy cập màn hình Kho Thư Viện.
- **Sự kiện kích hoạt:** Người dùng muốn tổ chức lại các tài liệu nghiên cứu theo chủ đề.
- **Luồng sự kiện chính (Happy Path):**
  1. Người dùng nhấp vào nút `[➕ Thư mục mới]` trên thanh điều hướng bên trái.
  2. Hệ thống hiển thị hộp thoại cho phép nhập:
     - Tên thư mục (ví dụ: *"Luận văn Cao học — Thị giác Máy tính"*).
     - Màu sắc nhận diện để trực quan hóa.
     - Mô tả ngắn gọn về phạm vi nghiên cứu của thư mục.
     - Thư mục cha (nếu muốn tổ chức theo dạng cây phân cấp nhiều tầng).
  3. Người dùng xác nhận lưu. Thư mục mới xuất hiện ngay trên cây thư mục kèm số lượng tài liệu ban đầu là `0`.
  4. Người dùng có thể kéo thả hoặc chọn gán các bài báo trong kho vào thư mục này.
  5. Người dùng có thể đổi tên, đổi màu hoặc xóa thư mục khi kết thúc đề tài.
- **Hậu điều kiện (Post-conditions):**
  1. Thư mục mới được ghi nhận vào cây thư mục cá nhân của người dùng và hiển thị trên giao diện điều hướng.
  2. Các bài báo được phân loại vào thư mục giữ nguyên tính toàn vẹn nội dung và có thể truy xuất lọc theo thư mục bất kỳ lúc nào.
  3. Việc thay đổi cấu trúc thư mục không làm ảnh hưởng đến dữ liệu gốc của các bài báo trong kho tri thức chung.
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Xóa thư mục đang chứa tài liệu:* Hệ thống cảnh báo rõ ràng rằng hành động này chỉ xóa cấu trúc thư mục phân loại, toàn bộ các bài báo bên trong vẫn được bảo toàn nguyên vẹn trong kho tài liệu chung của người dùng.
  - *Tạo thư mục trùng tên trong cùng thư mục cha:* Hệ thống cảnh báo tên thư mục đã tồn tại ở cấp này và yêu cầu người dùng đặt tên khác để tránh nhầm lẫn khi phân loại đề tài nghiên cứu.
  - *Di chuyển thư mục vào chính nó hoặc vào thư mục con của nó (Vòng lặp phân cấp cây):* Hệ thống chặn hành động di chuyển có nguy cơ gây vòng lặp phân cấp vô hạn, thông báo rõ ràng vị trí đích không hợp lệ và hoàn tác lại vị trí ban đầu của thư mục.

---

### UC-LIB-02: Đánh Dấu Bài Báo Yêu Thích & Kích Hoạt Mạng Tri Thức
- **Tác nhân:** Nhà Nghiên Cứu.
- **Tiền điều kiện:** Người dùng đang đọc một tài liệu trong phiên nghiên cứu hoặc xem danh sách tài liệu.
- **Sự kiện kích hoạt:** Người dùng nhấp vào biểu tượng ngôi sao `[⭐ Yêu thích]`.
- **Luồng sự kiện chính (Happy Path):**
  1. Biểu tượng ngôi sao chuyển sang trạng thái vàng sáng, hệ thống hiển thị menu nhanh cho phép người dùng chọn lưu vào một Thư mục đề tài cụ thể hoặc lưu vào danh sách Yêu thích chung.
  2. Bài báo được thêm ngay vào danh mục Kho Yêu Thích của người dùng.
  3. **Kích hoạt ngầm động cơ tri thức đồ thị:**
     - Hệ thống âm thầm quét nội dung bài báo để bóc tách các thực thể học thuật chuẩn hóa.
     - Trích xuất các phương pháp được đề xuất, các bộ dữ liệu thử nghiệm và các con số thực nghiệm đạt được.
     - Tự động kết nối các thực thể này vào mạng lưới tri thức sẵn có của người dùng.
- **Hậu điều kiện (Post-conditions):**
  1. Bài báo được đánh dấu yêu thích và xuất hiện trong danh mục Kho Thư Viện Cá Nhân của người dùng.
  2. Các thực thể học thuật và quan hệ trích xuất được kết nối hoàn tất vào mạng tri thức đồ thị cá nhân.
  3. Dữ liệu tri thức sẵn sàng phục vụ các truy vấn hỏi đáp tổng hợp và hỗ trợ trợ lý viết bài khoa học.
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Bỏ đánh dấu yêu thích (Unstar):* Người dùng nhấp lại vào ngôi sao để gỡ bài báo. Hệ thống lập tức loại bài báo này khỏi phạm vi truy vấn đồ thị tri thức để đảm bảo người dùng và trợ lý viết bài không trích dẫn nhầm tài liệu đã bị loại bỏ. Các thực thể dùng chung (như tên phương pháp nền tảng) vẫn được giữ lại nếu còn bài báo khác liên kết tới.
  - *Tài liệu dạng scan mờ, văn bản hỏng hoặc nhận dạng ký tự kém (OCR Failure):* Nếu tài liệu có chất lượng hình ảnh quá kém không thể bóc tách cấu trúc văn bản, hệ thống vẫn lưu bài báo vào kho yêu thích nhưng hiển thị huy hiệu thông báo: *"Không thể tự động bóc tách thực thể tri thức do định dạng tài liệu không chuẩn"*, đồng thời hướng dẫn người dùng nhập bổ sung thông tin phương pháp thủ công hoặc tải bản in kỹ thuật số rõ nét hơn.
  - *Tài liệu thuộc thể loại tổng thuật lý thuyết thuần túy (không có dữ liệu thực nghiệm hoặc con số đo lường):* Hệ thống chỉ trích xuất thực thể Bài Báo và Phương Pháp lý thuyết, bỏ qua thực thể Tập Dữ Liệu và Chỉ Số Đo Lường mà không làm gián đoạn quy trình kích hoạt mạng tri thức.

---

### UC-LIB-03: Mạng Tri Thức Đồ Thị 4 Thực Thể Chuẩn Hóa
- **Tác nhân:** Động Cơ Tri Thức Đồ Thị & Nhà Nghiên Cứu.
- **Tiền điều kiện:** Bài báo đã được đánh dấu yêu thích và đưa vào kho.
- **Sự kiện kích hoạt:** Hệ thống hoàn tất bóc tách dữ liệu bài báo.
- **Quy chuẩn 4 Loại Thực Thể Học Thuật Cố Định:**
  Hệ thống tuyệt đối tuân thủ mô hình 4 thực thể cố định để đảm bảo tính chuẩn tắc và tránh phân mảnh:
  1. **Bài Báo Khoa Học (Paper):** Đơn vị công trình gốc (Tên bài, tác giả, năm công bố, nơi xuất bản).
  2. **Phương Pháp / Mô Hình (Method):** Tên thuật toán, kiến trúc hoặc phương pháp kỹ thuật (ví dụ: *Transformer*, *Diffusion*, *ResNet-50*).
  3. **Tập Dữ Liệu Thực Nghiệm (Dataset):** Bộ dữ liệu chuẩn hoặc benchmark đánh giá (ví dụ: *ImageNet-1K*, *WMT-2014*, *GLUE*).
  4. **Chỉ Số & Kết Quả Đo Lường (MetricResult):** Con số định lượng cụ thể kèm thước đo (ví dụ: *BLEU 28.4*, *Độ chính xác Top-1 89.2%*).
- **Quy chuẩn 4 Kiểu Mối Quan Hệ:**
  1. `Đề Xuất (PROPOSES):` Bài Báo $\rightarrow$ Phương Pháp.
  2. `Đánh Giá Trên (EVALUATED_ON):` Bài Báo / Phương Pháp $\rightarrow$ Tập Dữ Liệu.
  3. `Đạt Được (ACHIEVES):` Phương Pháp $\rightarrow$ Chỉ Số & Kết Quả (kèm số trang chứng minh gốc).
  4. `Trích Dẫn (CITES):` Bài Báo $\rightarrow$ Bài Báo khác trong kho.
- **Nguyên Tắc Hợp Nhất Thực Thể Dùng Chung (Canonical Hub):**
  - Khi nhiều bài báo trong kho cùng sử dụng một phương pháp (ví dụ: cùng dùng mô hình *"Transformer"*), hệ thống tự động gộp thành một điểm nút trung tâm duy nhất kết nối tới tất cả các bài báo đó, tạo thành mạng lưới tri thức liên thông thực sự.
- **Hậu điều kiện (Post-conditions):**
  1. Đồ thị tri thức cá nhân của người dùng được cập nhật đầy đủ các điểm nút và cạnh quan hệ theo chuẩn 4 thực thể.
  2. Các thực thể dùng chung (phương pháp, tập dữ liệu) được hợp nhất chuẩn xác về điểm nút trung tâm, tạo sự liên kết chéo giữa các bài báo độc lập.
  3. Mọi kết quả đo lường và điểm số thực nghiệm đều được gắn chặt với số trang và bài báo nguồn làm bằng chứng khoa học không thể tách rời.
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Hai bài báo báo cáo kết quả thực nghiệm trái ngược hoặc bất nhất trên cùng một tập dữ liệu benchmark (Divergent Empirical Results):* Ví dụ: Bài báo A công bố phương pháp X đạt độ chính xác 85.2% trên tập dữ liệu benchmark ImageNet-1K, nhưng bài báo B (một công trình độc lập) tái lập lại chỉ ghi nhận 82.1% trên cùng tập dữ liệu này. Động cơ tri thức không loại bỏ hay tự ý ghi đè số liệu, mà tạo lập cả 2 thực thể kết quả đo lường độc lập gắn liền với từng bài báo nguồn tương ứng, đồng thời tạo liên kết ghi chú ngữ cảnh thực nghiệm (như khác biệt về thiết lập siêu tham số hay kỹ thuật tăng cường dữ liệu) để người dùng có cái nhìn đối chiếu khách quan, đa chiều.
  - *Tên phương pháp hoặc tập dữ liệu có nhiều biến thể viết tắt hoặc cách đặt tên khác nhau (Synonym / Variant Naming):* Ví dụ: *"BERT-base"*, *"BERT base uncased"*, *"BERT (Devlin et al.)"*. Hệ thống nhận diện sự tương đồng ngữ nghĩa, liên kết các biến thể này về một họ phương pháp chung nhưng vẫn ghi nhận tên gọi nguyên văn từ bài báo gốc nhằm tránh mất mát thông tin ngữ cảnh học thuật.

---

### UC-LIB-04: Hỏi Đáp Tổng Hợp & So Sánh Đa Tài Liệu Trong Kho
- **Tác nhân:** Nhà Nghiên Cứu.
- **Tiền điều kiện:** Kho yêu thích đã có từ 2 bài báo trở lên đã hoàn tất bóc tách đồ thị tri thức.
- **Sự kiện kích hoạt:** Người dùng đặt câu hỏi tra cứu tổng hợp tại thanh tìm kiếm của Kho Thư Viện.
- **Luồng sự kiện chính (Happy Path):**
  1. Người dùng nhập câu hỏi so sánh ngôn ngữ tự nhiên:
     > *"Trong kho yêu thích của tôi, những bài báo nào xử lý bài toán nhận diện hình ảnh trên tập dữ liệu ImageNet và đạt độ chính xác cao nhất?"*
  2. Hệ thống phân tích câu hỏi, xác định thực thể trọng tâm (*ImageNet*, *Nhận diện hình ảnh*) và duyệt trên mạng tri thức đồ thị.
  3. Hệ thống trả về câu trả lời tổng hợp rõ ràng:
     - So sánh chi tiết các phương pháp được sử dụng giữa các bài báo khác nhau.
     - Bảng đối chiếu con số thực nghiệm minh bạch kèm trích dẫn chính xác tên bài báo và số trang gốc.
     - Sơ đồ mạng lưới quan hệ trực quan (Mini Knowledge Graph) giúp người dùng nhìn thấy ngay mối liên kết giữa các công trình.
- **Hậu điều kiện (Post-conditions):**
  1. Người dùng nhận được phản hồi phân tích so sánh toàn diện bằng văn phong khoa học chuẩn mực.
  2. Bảng đối chiếu thực nghiệm được hiển thị minh bạch kèm trích dẫn số trang gốc từ từng tài liệu nguồn.
  3. Sơ đồ mạng lưới tri thức trực quan tương ứng được hiển thị trên giao diện và lưu vết trong phiên tra cứu.
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Không tìm thấy thực thể tương ứng trong kho:* Hệ thống phản hồi rõ ràng rằng kho hiện tại chưa có bài báo nào thử nghiệm trên tập dữ liệu này và gợi ý người dùng bổ sung tài liệu mới qua tính năng Khám phá bài báo.
  - *Phát hiện mâu thuẫn số liệu thực nghiệm giữa các bài báo khi phản biện (Reviewer #2 Contradiction Discovery):* Khi người dùng truy vấn so sánh hiệu năng giữa hai phương pháp mà dữ liệu trong kho cho thấy hai công trình báo cáo kết quả mâu thuẫn nhau trên cùng một tập dữ liệu, hệ thống tự động làm nổi bật sự mâu thuẫn này trong bảng tổng hợp: chỉ rõ bài báo nào báo cáo con số nào, trích dẫn số trang tương ứng, và chú giải điều kiện kiểm thử của từng nhóm tác giả để nhà nghiên cứu chuẩn bị luận cứ vững chắc khi phản biện với hội đồng khoa học.
  - *Câu hỏi tra cứu quá mơ hồ hoặc thiếu tiêu chí định lượng cụ thể:* Ví dụ người dùng chỉ hỏi *"Mô hình nào tốt hơn?"* mà không nêu rõ tập dữ liệu hay chỉ số đo lường nào. Hệ thống phân tích các tập dữ liệu và chỉ số chung mà các mô hình đó cùng được thử nghiệm trong kho, liệt kê danh sách gợi ý để người dùng chọn nhanh phạm vi đối chiếu chuẩn xác.

---

## 4. Tiêu Chí Nghiệm Thu Nghiệp Vụ (Acceptance Criteria - Gherkin)

### Kịch bản 1: Quản lý thư mục đề tài không làm mất tài liệu gốc
```gherkin
Given người dùng đang có một thư mục đề tài chứa 3 bài báo khoa học
When người dùng thực hiện thao tác xóa thư mục này
Then cấu trúc thư mục phân loại phải bị gỡ bỏ khỏi cây thư mục
  And cả 3 bài báo bên trong vẫn tồn tại nguyên vẹn trong kho tài liệu chung của người dùng
  And toàn bộ ghi chú và trích dẫn liên quan đến các bài báo này không bị mất
```

### Kịch bản 2: Bóc tách tự động và hợp nhất thực thể dùng chung
```gherkin
Given trong kho đã có bài báo A đề xuất phương pháp "Transformer"
When người dùng đánh dấu yêu thích thêm bài báo B cũng áp dụng phương pháp "Transformer"
Then hệ thống phải nhận diện phương pháp "Transformer" là một khái niệm dùng chung duy nhất
  And hệ thống không tạo ra hai thực thể phương pháp trùng lặp
  And trên mạng tri thức, cả bài báo A và bài báo B đều liên kết đến cùng một điểm nút "Transformer"
```

### Kịch bản 3: Hỏi đáp tổng hợp thực nghiệm đa bài báo chính xác
```gherkin
Given kho yêu thích có 2 bài báo cùng thử nghiệm trên tập dữ liệu "WMT-2014 English-to-German"
  And bài báo A đạt điểm "BLEU: 28.4", bài báo B đạt điểm "BLEU: 27.5"
When người dùng đặt câu hỏi: "Bài báo nào đạt điểm BLEU cao hơn trên tập WMT-2014?"
Then câu trả lời của hệ thống phải khẳng định bài báo A đạt điểm cao hơn với điểm số 28.4
  And câu trả lời phải kèm dẫn chứng số trang trích xuất từ cả hai bài báo
  And giao diện hiển thị sơ đồ kết nối trực quan giữa 2 bài báo và điểm số thực nghiệm
```

### Kịch bản 4: Dọn dẹp sạch phạm vi tri thức khi người dùng bỏ yêu thích
```gherkin
Given một bài báo đang được đánh dấu yêu thích và có các nút thực thể trong mạng tri thức
When người dùng nhấp bỏ dấu sao yêu thích (Unstar) bài báo đó
Then bài báo đó lập tức bị loại khỏi phạm vi trả lời của các câu hỏi tra cứu tổng hợp
  And các liên kết thực nghiệm độc nhất của bài báo đó bị thu hồi khỏi đồ thị
  And các thực thể phương pháp nền tảng dùng chung với bài báo khác vẫn được bảo toàn nguyên vẹn
```

---

## 5. Quy Tắc Nghiệp Vụ Bất Biến (Business Invariants)

1. **Nguyên Tắc 4 Thực Thể Chuẩn Hóa Cố Định (Strict 4-Entity Schema):**
   - Đồ thị tri thức chỉ chấp nhận duy nhất 4 loại thực thể: `Bài Báo (Paper)`, `Phương Pháp (Method)`, `Tập Dữ Liệu (Dataset)`, và `Kết Quả Đo Lường (MetricResult)`.
   - Tuyệt đối không cho phép trí tuệ nhân tạo tự sáng tạo thêm các loại nhãn tùy tiện gây hỗn loạn cấu trúc mạng tri thức.
2. **Nguyên Tắc Điểm Nút Tri Thức Dùng Chung (Canonical Entity Merging):**
   - Các phương pháp hoặc tập dữ liệu có cùng bản chất tên gọi trong phạm vi tài khoản của một người dùng bắt buộc phải được hợp nhất về cùng một thực thể chuẩn.
   - Nhờ đó, tri thức giữa các bài báo riêng rẽ mới tạo thành một mạng lưới liên kết hữu cơ.
3. **Nguyên Tắc Cô Lập Dữ Liệu Cá Nhân Tuyệt Đối (Strict Scholar Data Privacy):**
   - Mạng tri thức và cây thư mục của người dùng nào chỉ thuộc quyền sở hữu duy nhất của người dùng đó.
   - Hệ thống tuyệt đối không trộn lẫn hoặc để lộ dữ liệu tri thức giữa các tài khoản khác nhau.
4. **Nguyên Tắc Minh Chứng Số Liệu Thực Nghiệm (Grounded Metric Evidence):**
   - Mọi kết quả đo lường và điểm số thực nghiệm trong đồ thị bắt buộc phải gắn liền với nguồn gốc cụ thể (tên bài báo và số trang nơi xuất hiện con số).
   - Tuyệt đối cấm hiển thị số liệu không có bằng chứng gốc.
