# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (PRD): KHO BÀI BÁO YÊU THÍCH & MẠNG TRI THỨC HỌC THUẬT 4 THỰC THỂ
# (FAVORITE PAPERS LIBRARY & 4-ENTITY ACADEMIC KNOWLEDGE GRAPH)

**Mã tài liệu:** `PRD-05`  
**Thuộc giải pháp:** VeriScholar AI Research Assistant  
**Vai trò tác giả:** Chuyên viên Phân tích Nghiệp vụ (Business Analyst)  
**Tài liệu kỹ thuật đối ứng:** [`05-favorite-library-and-graphrag-spec.md`](../specs/05-favorite-library-and-graphrag-spec.md)  
**File nền tảng liên đới:** [`00-overview-and-cleanup.md`](./00-overview-and-cleanup.md)  

---

## 1. Tầm Nhìn Nghiệp Vụ & Nỗi Đau Người Dùng (Business Context & Pain Points)

Trong chu kỳ nghiên cứu khoa học kéo dài nhiều tháng hoặc nhiều năm, một học giả phải tiếp cận, tích lũy và đối chiếu hàng trăm bài báo khác nhau:
- **Nỗi đau 1 — Thư viện tài liệu trở thành "kho phế liệu" hỗn độn:** Khi đọc nhiều bài báo trên các nền tảng phân tán, học giả thường lưu trữ file PDF rải rác trong các thư mục máy tính cá nhân hoặc danh sách bookmark trình duyệt. Sau vài tháng, họ không còn nhớ bài báo chứng minh định lý toán này nằm ở đâu, bài báo đạt độ chính xác cao nhất về xử lý ảnh tên là gì, dẫn đến việc phải tìm kiếm và đọc lại từ đầu.
- **Nỗi đau 2 — Tri thức giữa các bài báo bị phân mảnh và cô lập (Isolated Silos):** Các bài báo khoa học trong cùng một chuyên ngành luôn có mối quan hệ hữu cơ: bài báo A đề xuất mô hình, bài báo B cải tiến mô hình đó, bài báo C thử nghiệm trên tập dữ liệu mới. Hiện nay, các phần mềm quản lý trích dẫn chỉ xem bài báo như các tệp tĩnh đơn lẻ, không thể cho người dùng thấy được mạng lưới quan hệ chéo giữa các phương pháp và kết quả thực nghiệm.
- **Nỗi đau 3 — Mất hàng tuần để tổng hợp bảng so sánh thực nghiệm (Benchmark Synthesis):** Khi bắt tay vào viết phần So sánh Thực nghiệm (Experiments & Results) cho công trình cá nhân, tác giả phải mở lại hàng chục bài báo cũ, dò tìm từng bảng số liệu để trích xuất điểm số (như BLEU, Accuracy, F1-score). Công việc này vừa nhàm chán, tốn thời gian, vừa tiềm ẩn nguy cơ chép sai số liệu khoa học.

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
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Xóa thư mục đang chứa tài liệu:* Hệ thống cảnh báo rõ ràng rằng hành động này chỉ xóa cấu trúc thư mục phân loại, toàn bộ các bài báo bên trong vẫn được bảo toàn nguyên vẹn trong kho tài liệu chung.

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
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Bỏ đánh dấu yêu thích (Unstar):* Người dùng nhấp lại vào ngôi sao để gỡ bài báo. Hệ thống lập tức loại bài báo này khỏi phạm vi truy vấn đồ thị tri thức để đảm bảo người dùng và trợ lý viết bài không trích dẫn nhầm tài liệu đã bị loại bỏ. Các thực thể dùng chung (như tên phương pháp nền tảng) vẫn được giữ lại nếu còn bài báo khác liên kết tới.

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
- **Luồng sự kiện ngoại lệ (Exception Flows):**
  - *Không tìm thấy thực thể tương ứng trong kho:* Hệ thống phản hồi rõ ràng rằng kho hiện tại chưa có bài báo nào thử nghiệm trên tập dữ liệu này và gợi ý người dùng bổ sung tài liệu mới qua tính năng Khám phá bài báo.

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
   - Tuyệt đối không cho phép AI tự sáng tạo thêm các loại nhãn tùy tiện gây hỗn loạn cấu trúc mạng tri thức.
2. **Nguyên Tắc Điểm Nút Tri Thức Dùng Chung (Canonical Entity Merging):**
   - Các phương pháp hoặc tập dữ liệu có cùng bản chất tên gọi trong phạm vi tài khoản của một người dùng bắt buộc phải được hợp nhất về cùng một thực thể chuẩn.
   - Nhờ đó, tri thức giữa các bài báo riêng rẽ mới tạo thành một mạng lưới liên kết hữu cơ.
3. **Nguyên Tắc Cô Lập Dữ Liệu Cá Nhân Tuyệt Đối (Strict Scholar Data Privacy):**
   - Mạng tri thức và cây thư mục của người dùng nào chỉ thuộc quyền sở hữu duy nhất của người dùng đó.
   - Hệ thống tuyệt đối không trộn lẫn hoặc để lộ dữ liệu tri thức giữa các tài khoản khác nhau.
4. **Nguyên Tắc Minh Chứng Số Liệu Thực Nghiệm (Grounded Metric Evidence):**
   - Mọi kết quả đo lường và điểm số thực nghiệm trong đồ thị bắt buộc phải gắn liền với nguồn gốc cụ thể (tên bài báo và số trang nơi xuất hiện con số).
   - Tuyệt đối cấm hiển thị số liệu không có bằng chứng gốc.
