# VERISCHOLAR MVP — TÀI LIỆU YÊU CẦU SẢN PHẨM: KHÁM PHÁ BÀI BÁO & QUẢN LÝ TÀI LIỆU PDF
# (PRODUCT REQUIREMENTS DOCUMENT: SCHOLARLY DISCOVERY & DOCUMENTS MANAGEMENT)

**Mã phân hệ:** `PRD-02`  
**Phiên bản:** `2.0-OFFICIAL`  
**Vai trò phụ trách:** Chuyên viên Phân tích Nghiệp vụ (Lead Business Analyst — BA)  
**Tài liệu Kỹ thuật liên đới:** [`02-discovery-and-documents-spec.md`](../specs/02-discovery-and-documents-spec.md)  
**File nền tảng liên đới:** [`00-overview-and-cleanup.md`](./00-overview-and-cleanup.md)  
**Trạng thái:** CHÍNH THỨC BAN HÀNH (RELEASE CANDIDATE)

---

## 1. Tầm Nhìn & Nỗi Đau Nghiệp Vụ (Vision & Pain Points)

### 1.1. Tầm nhìn phân hệ
Trao quyền cho người làm nghiên cứu bắt đầu hành trình học thuật tức thì ngay cả khi chưa có sẵn tài liệu trong máy tính thông qua công cụ tìm kiếm bài báo theo ngữ nghĩa học thuật; đồng thời cung cấp kho quản lý tài liệu PDF cá nhân trực quan, tự động bóc tách cấu trúc 2 cột chuẩn xác và cam kết tiêu hủy vật lý dứt điểm khi người dùng xóa bài.

### 1.2. Nỗi đau thực tế của học giả (Có Định Lượng Nghiệp Vụ)
1. **Lãng phí thời gian chuẩn bị tài liệu rời rạc (60 – 90 phút/bài báo mới):** Học giả phải chuyển qua lại giữa nhiều kho dữ liệu (Google Scholar, arXiv, Semantic Scholar), tải thủ công từng tệp PDF về ổ cứng, đổi tên tệp và nhập lại vào công cụ đọc. Quy trình thủ công này làm tiêu tốn trung bình **5 – 8 giờ mỗi tuần** chỉ cho khâu tìm kiếm và sắp xếp sơ cấp trước khi thực sự đọc bài.
2. **Bất lực trước tệp PDF quét ảnh cổ không có lớp văn bản (Scanned Image PDF Agony):** Nhiều tài liệu kỷ yếu trước năm 2010 hoặc bản quét thư viện chỉ là ảnh chụp thuần túy không có lớp chữ số hóa. Nếu hệ thống nhận bừa các tệp này mà không kiểm tra trước, trợ lý AI sẽ sinh ra các câu trả lời đoán mò hoàn toàn sai lệch.
3. **Vỡ thứ tự đọc trên bài báo khoa học bố cục 2 cột (Two-Column Layout & Math Distortion):** Hơn 85% bài báo chuẩn quốc tế (IEEE, ACM, NeurIPS, Springer) trình bày theo bố cục 2 cột kèm công thức toán nhiều dòng. Các trình trích xuất thông thường quét ngang từ trái sang phải xuyên qua cả hai cột khiến câu chữ bị ghép chéo vô nghĩa và làm hỏng ngữ cảnh công thức toán học.
4. **Nỗi lo tồn lưu bản thảo mật sau khi xóa (Zero-Retention Anxiety):** Các bản thảo đang trong kỳ phản biện kín (Double-blind review) hoặc chứa kết quả chưa công bố đòi hỏi cam kết tiêu hủy tệp vật lý ngay lập tức khi học giả bấm xóa, thay vì vẫn âm thầm giữ lại tệp trên ổ đĩa máy chủ.

### 1.3. Bảng Đối Chiếu Giá Trị Trước & Sau Khi Áp Dụng Khám Phá & Quản Lý Tài Liệu (Before vs. After Value Matrix)

| Tiêu chí Nghiệp vụ Học thuật | Quy trình Tìm kiếm & Lưu trữ Truyền thống | Phân hệ Khám Phá & Tài Liệu VeriScholar |
| :--- | :--- | :--- |
| **Từ lúc tìm kiếm đến lúc đọc sâu** | Tìm Google Scholar $\rightarrow$ Tải PDF về máy $\rightarrow$ Tạo phiên đọc thủ công (mất 5 – 10 phút). | Bấm **1-Click `[📖 Mở đọc ngay]`** $\rightarrow$ Vào thẳng Không gian Đọc sâu trong **< 500ms**. |
| **Kiểm soát chất lượng tệp PDF nạp vào** | Nhận cả tệp hỏng hoặc tệp ảnh quét trống làm AI trả lời sai lệch. | **Kiểm tra lớp văn bản ngay từ trang đầu**, từ chối minh bạch tệp ảnh quét hoặc tệp khóa mật khẩu. |
| **Đọc bài báo 2 cột & Mục lục** | Ghép nhầm dòng cột trái với cột phải; phải tự cuộn tìm từng phần. | **Bóc tách chuẩn thứ tự 2 cột học thuật**, tự động dựng cây Mục lục và lưu tọa độ Khung viền vàng. |
| **Xóa bản thảo nhạy cảm** | Xóa trên giao diện nhưng tệp gốc vẫn nằm lại trên máy chủ. | **Tiêu hủy vật lý đồng bộ (Zero-Retention)** ngay khi không còn người dùng nào lưu trữ. |

---

## 2. Chân Dung Tác Nhân (Actors & Personas)

* **Học giả khám phá (Exploring Scholar):** Cần tìm kiếm nhanh các bài báo liên quan đến một chủ đề mới và mở đọc ngay bản truy cập mở (Open Access) mà không cần tải tệp về máy.
* **Học giả có sẵn tài liệu (Document Uploader):** Đã có sẵn tệp PDF trong máy tính và muốn tải lên hệ thống để phân tích sâu, trích xuất mục lục và đối chiếu trích dẫn.
* **Động cơ bóc tách tài liệu tự động (Automated Document Parsing Engine):** Tác nhân hệ thống thực hiện phân tích trang, phát hiện mục lục, trích xuất đoạn văn theo thứ tự đọc học thuật 2 cột và lưu tọa độ không gian trên trang PDF.

---

## 3. Đặc Tả Chi Tiết Các Use Cases Nghiệp Vụ (Detailed Use Cases)

### UC-DISC-01: Khám Phá Bài Báo Học Thuật Theo Chủ Đề
* **Tác nhân:** Học giả khám phá.
* **Điều kiện tiên quyết:** Đang ở Màn hình chính (`Dashboard`) hoặc Trang Khám phá (`Discovery`).
* **Sự kiện kích hoạt:** Nhập từ khóa hoặc câu hỏi chủ đề vào ô tìm kiếm và bấm "Tìm kiếm".
* **Luồng chuẩn (Happy Path):**
  1. Người dùng nhập câu truy vấn học thuật bằng Tiếng Việt hoặc Tiếng Anh (ví dụ: *"Self-attention mechanisms in medical imaging"*).
  2. Hệ thống tìm kiếm trên các kho học thuật mở quốc tế, khử trùng lặp theo mã DOI và hiển thị danh sách kết quả liên quan nhất.
  3. Mỗi bài báo hiển thị đầy đủ thẻ thông tin: Tiêu đề, Tác giả, Năm xuất bản, Nơi công bố, Mã định danh DOI / arXiv, Đoạn tóm tắt và nhãn trạng thái truy cập:
     * **`[🟢 Có sẵn PDF Open Access]`**: Bài báo có bản toàn văn PDF miễn phí.
     * **`[🟡 Chỉ có Tóm tắt]`**: Bài báo thuộc nguồn thu phí, chỉ có thông tin tóm tắt.
* **Kết quả đầu ra (Post-conditions):**
  * Danh sách các bài báo học thuật khớp nhất được hiển thị kèm nhãn phân biệt rõ trạng thái toàn văn hay tóm tắt.
* **Luồng ngoại lệ (Exception Flows):**
  * *1a. Từ khóa tìm kiếm để trống hoặc không có kết quả khớp:* Hệ thống nhắc người dùng nhập từ khóa hợp lệ hoặc gợi ý mở rộng thuật ngữ chuyên ngành bằng tiếng Anh.
  * *1b. Cổng tìm kiếm học thuật quốc tế phản hồi chậm quá 15 giây:* Hệ thống ngắt chờ an toàn, hiển thị thông báo kết nối nguồn học thuật ngoài đang bận và gợi ý thử lại hoặc tự tải tệp PDF từ máy tính.

---

### UC-DISC-02: Mở Đọc Ngay Bài Báo Từ Kết Quả Tìm Kiếm (1-Click Zero-to-Reading)
* **Tác nhân:** Học giả khám phá.
* **Điều kiện tiên quyết:** Đang xem danh sách kết quả tìm kiếm bài báo.
* **Sự kiện kích hoạt:** Người dùng bấm nút `[📖 Mở đọc ngay]` (hoặc `[📄 Xem Tóm tắt]`) trên thẻ bài báo.
* **Luồng chuẩn (Happy Path):**
  1. **Tầng 1 — Phản hồi tức thì (< 500ms):** Hệ thống lưu ngay thông tin bài báo và phần Tóm tắt vào danh mục của học giả, khởi tạo một Phiên đọc sâu mới và chuyển thẳng người dùng vào Không gian đọc sâu.
  2. **Tầng 2 — Nạp và bóc tách toàn văn ngầm:** Nếu bài báo có nhãn `[🟢 Có sẵn PDF Open Access]`, hệ thống âm thầm tải tệp PDF về kho lưu trữ, bóc tách cấu trúc 2 cột và tự động mở khung đọc PDF gốc ngay khi hoàn tất.
* **Kết quả đầu ra (Post-conditions):**
  * Học giả vào được Không gian Đọc sâu trong dưới 500ms để hỏi đáp ngay trên bản Tóm tắt và chuyển sang đọc toàn văn PDF ngay khi tiến trình tải ngầm hoàn tất.
* **Luồng ngoại lệ (Exception Flows):**
  * *2a. Bài báo thuộc nguồn thu phí (`Chỉ có Tóm tắt`) hoặc đường dẫn PDF ngoài bị lỗi tải về:* Hệ thống mở Không gian Đọc sâu ở chế độ **Thẻ Tóm Tắt Học Thuật** và cung cấp nút `[📤 Tải lên file PDF đầy đủ]` để học giả tự đính kèm tệp PDF nếu có bản quyền cá nhân.

---

### UC-DOC-01: Tải Lên Tài Liệu PDF Cá Nhân Từ Máy Tính
* **Tác nhân:** Học giả có sẵn tài liệu.
* **Điều kiện tiên quyết:** Đã đăng nhập vào hệ thống.
* **Sự kiện kích hoạt:** Kéo thả tệp PDF vào khu vực nạp tài liệu hoặc bấm nút "Tải tài liệu lên".
* **Luồng chuẩn (Happy Path):**
  1. Người dùng chọn tệp PDF từ máy tính (dung lượng tối đa 50MB, độ dài tối đa 100 trang).
  2. Hệ thống kiểm tra tính hợp lệ ngay lập tức: đúng định dạng PDF, không bị khóa mật khẩu và có lớp văn bản số hóa đọc được.
  3. Hệ thống kiểm tra khử trùng lặp thông minh (nếu tệp nhị phân giống hệt đã có trên máy chủ thì tái sử dụng lưu trữ vật lý nhưng vẫn tạo bản ghi sở hữu riêng cho học giả).
  4. Sau khi tải xong 100%, tài liệu xuất hiện trong danh mục cá nhân và tự động kích hoạt tiến trình bóc tách cấu trúc ngầm.
* **Kết quả đầu ra (Post-conditions):**
  * Bản ghi tài liệu của học giả được khởi tạo thành công, tệp vật lý được lưu trữ an toàn và tiến trình bóc tách ngầm được kích hoạt.
* **Luồng ngoại lệ (Exception Flows):**
  * *1a. Tệp vượt quá 50MB hoặc dài quá 100 trang:* Hệ thống từ chối nhận tệp và thông báo rõ giới hạn tối đa 50MB và 100 trang.
  * *1b. Tệp PDF quét ảnh thuần túy không có lớp văn bản (dưới 50 ký tự ở trang đầu):* Hệ thống từ chối nạp và hướng dẫn học giả cung cấp bản PDF kỹ thuật số hoặc đã qua nhận diện chữ (OCR) để đảm bảo độ chính xác trích dẫn.
  * *1c. Tệp PDF bị khóa mật khẩu hoặc hỏng cấu trúc:* Hệ thống thông báo rõ tệp đang bị khóa bảo vệ hoặc bị hư hại và yêu cầu mở khóa tệp trước khi tải lên.

---

### UC-DOC-02: Bóc Tách Cấu Trúc 2 Cột & Tạo Lập Mục Lục Thông Minh
* **Tác nhân:** Động cơ bóc tách tài liệu tự động.
* **Điều kiện tiên quyết:** Tệp PDF hợp lệ đã được nạp vào hệ thống.
* **Sự kiện kích hoạt:** Tự động kích hoạt ngay sau khi nạp tệp hoặc khi học giả bấm nút "Phân tích lại".
* **Luồng chuẩn (Happy Path):**
  1. Hệ thống đọc phân tích từng trang theo đúng thứ tự bố cục học thuật 2 cột (đọc hết cột trái từ trên xuống dưới rồi mới chuyển sang cột phải).
  2. Hệ thống trích xuất cây mục lục bài báo (`Introduction`, `Related Work`, `Methodology`, `Experiments`...), danh mục tài liệu tham khảo cuối bài và bản tóm tắt 3 phần cốt lõi.
  3. Nội dung bài báo được chia thành các đoạn trích ngữ nghĩa gắn kèm số trang và tọa độ hình học chuẩn hóa (`0..1000`) để phục vụ tính năng vẽ Khung viền vàng.
  4. Trạng thái tài liệu chuyển sang "Sẵn sàng nghiên cứu" (`Ready`).
* **Kết quả đầu ra (Post-conditions):**
  * Cây mục lục, các đoạn trích có tọa độ không gian và danh mục tham khảo được lưu trữ đầy đủ, sẵn sàng cho hỏi đáp bảo chứng.
* **Luồng ngoại lệ (Exception Flows):**
  * *2a. Tiến trình bóc tách ngầm gặp sự cố gián đoạn:* Trạng thái tài liệu chuyển sang "Cần xử lý lại" kèm nút bấm cho phép học giả kích hoạt phân tích lại mà không cần tải lại tệp PDF.

---

### UC-DOC-03: Quản Lý Danh Mục Bài Báo Cá Nhân (Xem, Lọc, Đính Kèm PDF)
* **Tác nhân:** Học giả sở hữu tài liệu.
* **Điều kiện tiên quyết:** Đã đăng nhập và truy cập danh mục tài liệu cá nhân.
* **Sự kiện kích hoạt:** Tìm kiếm, lọc danh sách hoặc cập nhật thông tin bài báo.
* **Luồng chuẩn (Happy Path):**
  1. Hệ thống hiển thị danh sách bài báo thuộc sở hữu của học giả kèm tiêu đề, tác giả, năm, số trang và trạng thái xử lý.
  2. Học giả có thể lọc nhanh theo từ khóa tiêu đề/tác giả, lọc theo trạng thái gắn sao yêu thích (`Starred`) hoặc theo thư mục đề tài (`Folder`).
  3. Đối với các bài báo đang ở chế độ "Chỉ có Tóm tắt", học giả có thể bấm đính kèm tệp PDF toàn văn từ máy tính để nâng cấp bài báo lên trạng thái "Sẵn sàng nghiên cứu" đầy đủ.
* **Kết quả đầu ra (Post-conditions):**
  * Danh mục tài liệu phản ánh chính xác bộ lọc và trạng thái nâng cấp toàn văn của từng bài báo.
* **Luồng ngoại lệ (Exception Flows):**
  * *3a. Đính kèm thêm PDF vào bài báo đã có sẵn toàn văn:* Hệ thống từ chối thao tác thừa và giữ nguyên tệp PDF hiện hành của bài báo.

---

### UC-DOC-04: Tiêu Hủy Tài Liệu Cá Nhân An Toàn (Safe Purge & Zero-Retention)
* **Tác nhân:** Học giả sở hữu tài liệu.
* **Điều kiện tiên quyết:** Học giả muốn xóa vĩnh viễn một bài báo khỏi kho cá nhân.
* **Sự kiện kích hoạt:** Bấm nút Xóa tài liệu và xác nhận trong hộp thoại cảnh báo.
* **Luồng chuẩn (Happy Path):**
  1. Hệ thống hiển thị hộp thoại xác nhận xóa vĩnh viễn bài báo.
  2. Khi người dùng xác nhận, hệ thống xóa bài báo và toàn bộ các đoạn trích văn bản thuộc bài báo đó khỏi không gian của học giả, đồng thời gỡ tab bài báo này khỏi các phiên đọc đang mở.
  3. **Cam kết Tiêu hủy Vật lý (Zero-Retention):** Nếu không còn bất kỳ bản ghi tài liệu nào khác trên hệ thống tham chiếu tới cùng tệp nhị phân đó, hệ thống xóa vĩnh viễn tệp PDF vật lý trên ổ đĩa máy chủ ngay trong cùng thao tác xử lý.
* **Kết quả đầu ra (Post-conditions):**
  * Bài báo bị xóa sạch khỏi danh mục của học giả, tệp vật lý mồ côi bị tiêu hủy ngay lập tức, trong khi các ghi chú đã lưu trong sổ tay phiên đọc vẫn giữ được bản chụp đoạn trích đóng băng.
* **Luồng ngoại lệ (Exception Flows):**
  * *4a. Người dùng cố tình gọi xóa mã tài liệu không tồn tại hoặc thuộc sở hữu của học giả khác:* Hệ thống chặn đứng và trả về thông báo không tìm thấy tài liệu.

---

## 4. Tiêu Chí Nghiệm Thu Hành Vi (Gherkin Acceptance Criteria)

```gherkin
@discovery @search
Feature: Tìm kiếm bài báo học thuật mở
  Scenario: Tìm kiếm trả về kết quả có sẵn PDF Open Access
    Given học giả đang ở ô tìm kiếm Discovery
    When nhập từ khóa "Graph Neural Networks fraud detection" và bấm Tìm kiếm
    Then hệ thống trả về danh sách các bài báo có tiêu đề, tác giả, năm và DOI
    And các bài báo có bản quyền mở hiển thị nhãn "[🟢 Có sẵn PDF Open Access]" kèm nút "Mở đọc ngay"

  Scenario: 1-Click mở đọc bài báo không cần tải về máy
    Given kết quả tìm kiếm có bài báo "Attention Is All You Need" với nhãn Open Access
    When học giả bấm nút "Mở đọc ngay"
    Then hệ thống tự động đưa bài báo vào tài khoản người dùng
    And tự động tạo một phiên đọc mới và chuyển thẳng người dùng vào không gian Đọc sâu

@documents @upload
Feature: Tải tài liệu PDF từ máy tính
  Scenario: Tải lên tài liệu hợp lệ thành công
    Given học giả chọn tệp "ResNet_Paper.pdf" dung lượng 12MB (45 trang) có lớp văn bản số hóa
    When kéo thả tệp vào vùng nạp tài liệu
    Then hệ thống hiển thị tiến độ tải lên từ 0 đến 100%
    And tệp được nạp thành công và chuyển sang trạng thái bóc tách mục lục ngầm

  Scenario: Từ chối tệp quá dung lượng hoặc tệp ảnh quét không có lớp chữ
    Given học giả chọn tệp "Heavy_Book.pdf" dung lượng 65MB hoặc tệp scan ảnh trống
    When cố gắng tải tệp lên
    Then hệ thống từ chối nhận tệp và hiển thị thông báo rõ nguyên nhân từ chối

@documents @zero_retention
Feature: Tiêu hủy dữ liệu vật lý tức thì
  Scenario: Xóa bài báo tiêu hủy file vật lý khi không còn người dùng nào trỏ tới
    Given học giả A sở hữu bài báo "Confidential_Draft.pdf" (chỉ có duy nhất học giả A lưu bài này)
    When học giả A bấm xác nhận "Xóa vĩnh viễn"
    Then hệ thống xóa bài báo khỏi danh sách của học giả A
    And tệp nhị phân vật lý trên đĩa cứng máy chủ bị tiêu hủy dứt điểm ngay trong thao tác này
```

---

## 5. Quy Tắc Nghiệp Vụ Bất Biến (Business Rules & Invariants)

1. **Giới Hạn Tệp Nạp Chuẩn Mực:** Tệp PDF tải lên giới hạn tối đa `50 MB`, tối đa `100 trang` và bắt buộc là PDF kỹ thuật số có lớp văn bản trích xuất được (tối thiểu 50 ký tự ở trang đầu).
2. **Khử Trùng Lặp Lưu Trữ Nhưng Cô Lập Quyền Sở Hữu:** Các tệp PDF trùng khớp hoàn toàn về nội dung nhị phân chỉ lưu một bản vật lý duy nhất trên đĩa, nhưng bản ghi tài liệu, đoạn trích và ghi chú của từng học giả luôn tách biệt tuyệt đối.
3. **Tiêu Hủy Vật Lý Đồng Bộ (Zero-Retention Invariant):** Ngay khi một tài liệu bị xóa và số lượng tham chiếu về `0`, tệp vật lý trên máy chủ bị xóa vĩnh viễn ngay trong cùng chu kỳ xử lý.
4. **Không Để Lại Tab Mồ Côi:** Khi xóa một bài báo, mọi Phiên đọc đang mở bài báo đó tự động gỡ tab tương ứng ra khỏi thanh tab đọc.
