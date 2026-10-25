# VERISCHOLAR MVP — TÀI LIỆU YÊU CẦU SẢN PHẨM: KHÁM PHÁ BÀI BÁO & QUẢN LÝ TÀI LIỆU PDF
# (PRODUCT REQUIREMENTS DOCUMENT: SCHOLARLY DISCOVERY & DOCUMENTS MANAGEMENT)

**Mã phân hệ:** `PRD-02`  
**Phiên bản:** `2.0-OFFICIAL`  
**Vai trò phụ trách:** Chuyên viên Phân tích Nghiệp vụ (Lead Business Analyst — BA)  
**Tài liệu Kỹ thuật liên đới:** [`02-discovery-and-documents-spec.md`](../specs/02-discovery-and-documents-spec.md)  
**Trạng thái:** CHÍNH THỨC BAN HÀNH (RELEASE CANDIDATE)

---

## 1. Tầm Nhìn & Nỗi Đau Nghiệp Vụ (Vision & Pain Points)

### 1.1. Tầm nhìn phân hệ
Trao quyền cho người làm nghiên cứu bắt đầu hành trình học thuật một cách tức thì ngay cả khi chưa có sẵn file tài liệu trong máy tính, thông qua công cụ tìm kiếm bài báo chuyên sâu theo ngữ nghĩa học thuật; đồng thời cung cấp hệ thống quản lý tài liệu cá nhân trực quan, bảo mật và hỗ trợ bóc tách tự động cấu trúc nội dung từ trang bìa đến trang tài liệu tham khảo.

### 1.2. Nỗi đau thực tế của học giả
1. **Khởi đầu trắng tay (Zero-to-Research Delay):** Khi muốn tìm hiểu một chủ đề mới (ví dụ: *"Ứng dụng Transformer trong dự báo chuỗi thời gian y tế"*), sinh viên phải truy cập nhiều trang web học thuật rời rạc (Google Scholar, arXiv, PubMed), tự tải thủ công từng file PDF về máy tính, rồi mới tìm phần mềm để đọc và ghi chú. Quy trình phân mảnh này tốn rất nhiều thời gian chuẩn bị.
2. **Khó khăn khi xử lý file PDF scan hoặc hỏng cấu trúc:** Nhiều tài liệu PDF học thuật có bố cục 2 cột phức tạp, khiến việc bôi đen sao chép văn bản bị nhảy dòng lộn xộn, làm sai lệch ngữ nghĩa khi đưa vào các công cụ AI.
3. **Mối lo ngại về quyền riêng tư khi xóa tài liệu:** Người dùng lo ngại các bài báo chưa công bố khi đã xóa trên giao diện thì file nhị phân vẫn còn nằm lại trên máy chủ của nhà cung cấp.

---

## 2. Chân Dung Tác Nhân (Actors & Personas)

* **Học giả khám phá (Exploring Scholar):** Cần tìm kiếm nhanh các bài báo liên quan đến một chủ đề mới và mở đọc ngay bản Open Access.
* **Học giả có sẵn tài liệu (Document Uploader):** Đã có sẵn file PDF trong máy tính (bài báo tải từ thư viện trường hoặc bản thảo của nhóm nghiên cứu) và muốn tải lên để phân tích sâu.
* **Tiến trình bóc tách tài liệu tự động (Document Parsing Service):** Tác nhân hệ thống thực hiện phân tích trang, phát hiện mục lục, trích xuất đoạn văn và tọa độ không gian trên trang PDF.

---

## 3. Đặc Tả Chi Tiết Các Use Cases Nghiệp Vụ (Detailed Use Cases)

### UC-DISC-01: Khám Phá Bài Báo Học Thuật Theo Chủ Đề
* **Tác nhân:** Học giả khám phá.
* **Điều kiện tiên quyết:** Đang ở Màn hình chính (`Dashboard`) hoặc Trang Khám phá (`Discovery`).
* **Sự kiện kích hoạt:** Nhập từ khóa hoặc câu hỏi chủ đề vào ô tìm kiếm và bấm "Tìm kiếm" (hoặc nhấn phím Enter).
* **Luồng chuẩn (Happy Path):**
  1. Người dùng nhập câu truy vấn học thuật bằng Tiếng Việt hoặc Tiếng Anh (ví dụ: *"Self-attention mechanisms in medical imaging"*).
  2. Hệ thống tìm kiếm trên các kho học thuật mở quốc tế và hiển thị danh sách kết quả (tối đa 20 bài báo liên quan nhất).
  3. Mỗi bài báo hiển thị đầy đủ thẻ thông tin: Tiêu đề, Tác giả, Năm xuất bản, Tên hội nghị/tạp chí, Mã định danh DOI / arXiv, và Đoạn tóm tắt nổi bật (Abstract Highlights).
  4. Hệ thống gắn nhãn trực quan trạng thái tài liệu:
     * **`[🟢 Có sẵn PDF Open Access]`**: Bài báo có thể đọc trực tiếp miễn phí.
     * **`[🟡 Chỉ có Tóm tắt]`**: Bài báo thuộc nguồn đóng phí, chỉ xem được tóm tắt và thông tin tác giả.
* **Luồng ngoại lệ:**
  * *1a. Không tìm thấy kết quả phù hợp:* Hệ thống hiển thị trạng thái rỗng thân thiện: "Không tìm thấy bài báo khớp với chủ đề này. Hãy thử mở rộng từ khóa hoặc chuyển sang tiếng Anh."
  * *1b. Lỗi kết nối nguồn học thuật ngoài:* Hệ thống hiển thị cảnh báo nhẹ và gợi ý người dùng thử lại sau vài giây.

---

### UC-DISC-02: Mở Đọc Ngay Bài Báo Từ Kết Quả Tìm Kiếm (1-Click Zero-to-Reading)
* **Tác nhân:** Học giả khám phá.
* **Điều kiện tiên quyết:** Danh sách bài báo tìm kiếm có nhãn `[🟢 Có sẵn PDF Open Access]`.
* **Sự kiện kích hoạt:** Người dùng bấm nút "Mở đọc ngay" trên thẻ bài báo.
* **Luồng chuẩn (Happy Path):**
  1. Hệ thống tự động nạp bài báo vào danh mục tài liệu của người dùng.
  2. Hệ thống tự động tạo một Phiên đọc sâu mới (`Deep Reading Session`) gắn liền với bài báo này.
  3. Hệ thống chuyển hướng người dùng ngay lập tức vào Không gian đọc sách: Khung đọc PDF bên trái hiển thị bản gốc, Khung Chat AI bên phải sẵn sàng nhận câu hỏi. Toàn bộ chu trình hoàn tất trong dưới 2 giây.
* **Luồng ngoại lệ:**
  * *1a. File PDF từ nguồn mở bị lỗi đường link hoặc chặn tải:* Hệ thống thông báo rõ: "Nguồn tải bài báo bị gián đoạn. Bạn có thể sử dụng nút Tự tải PDF lên từ máy tính."

---

### UC-DOC-01: Tải Lên Tài Liệu PDF Cá Nhân Từ Máy Tính
* **Tác nhân:** Học giả có sẵn tài liệu.
* **Điều kiện tiên quyết:** Đã đăng nhập vào hệ thống.
* **Sự kiện kích hoạt:** Kéo thả file PDF vào khu vực nạp tài liệu hoặc bấm nút "Tải tài liệu lên".
* **Luồng chuẩn (Happy Path):**
  1. Người dùng chọn file PDF từ máy tính (dung lượng tối đa 50MB, tối đa 100 trang).
  2. Hệ thống kiểm tra tính hợp lệ của tệp:
     - Đúng định dạng PDF kỹ thuật số (Digital PDF) có chứa lớp ký tự văn bản.
     - Kiểm tra khử trùng lặp: nếu cùng một file đã từng được tải lên trước đó, hệ thống tái sử dụng ngay lập tức mà không phải tốn thời gian tải lại.
  3. Hệ thống hiển thị thanh tiến độ tải lên (Upload Progress: 0% $\rightarrow$ 100%).
  4. Sau khi tải xong, tài liệu xuất hiện trong danh mục "Tài liệu của tôi" và tự động kích hoạt tiến trình bóc tách nội dung ngầm.
* **Luồng ngoại lệ:**
  * *1a. File vượt quá 50MB hoặc quá 100 trang:* Hệ thống từ chối nạp và thông báo: "Kích thước tệp vượt quá giới hạn 50MB hoặc quá 100 trang của gói MVP."
  * *1b. File ảnh scan không có lớp chữ (Scanned Image PDF):* Hệ thống cảnh báo: "Tài liệu này là tệp quét ảnh thuần túy không có lớp văn bản. Trợ lý AI cần file PDF kỹ thuật số để đọc chính xác từng dòng."

---

### UC-DOC-02: Bóc Tách Cấu Trúc & Tạo Lập Mục Lục Thông Minh
* **Tác nhân:** Tiến trình bóc tách tài liệu tự động.
* **Điều kiện tiên quyết:** File PDF đã được nạp thành công vào hệ thống.
* **Sự kiện kích hoạt:** Tự động kích hoạt ngay sau khi nạp file.
* **Luồng chuẩn (Happy Path):**
  1. Tiến trình phân tích cấu trúc bài báo theo đúng thứ tự đọc học thuật 2 cột (từ trên xuống dưới, từ cột trái sang cột phải).
  2. Bóc tách cây mục lục bài báo (`Document Structure`): Tiêu đề, Tóm tắt, Mục 1 (Introduction), Mục 2 (Related Work), Mục 3 (Methodology), v.v. kèm số trang chính xác.
  3. Cắt nhỏ nội dung thành các đoạn trích ngữ nghĩa (Chunks), lưu giữ tọa độ hình học (Bounding Box) của từng đoạn trên trang PDF để phục vụ việc tô sáng viền vàng khi hỏi đáp sau này.
  4. Trạng thái tài liệu chuyển sang "Sẵn sàng nghiên cứu" (`Ready`). Người dùng có thể bấm vào bất kỳ mục nào trong Bảng Mục lục để cuộn trang PDF đến đúng vị trí tương ứng.

---

### UC-DOC-03: Quản Lý Danh Mục Bài Báo Cá Nhân (Xem, Lọc, Tìm Kiếm)
* **Tác nhân:** Học giả sở hữu tài liệu.
* **Điều kiện tiên quyết:** Đã có ít nhất 1 bài báo trong danh mục.
* **Sự kiện kích hoạt:** Truy cập tab "Tài liệu của tôi" hoặc thanh danh sách tài liệu.
* **Luồng chuẩn (Happy Path):**
  1. Danh sách hiển thị các bài báo dưới dạng thẻ hoặc lưới: Tên bài, Tác giả chính, Năm, Số trang, và Ngày thêm vào kho.
  2. Người dùng có thể:
     - Gõ từ khóa để lọc nhanh bài báo theo tiêu đề hoặc tác giả.
     - Lọc danh sách theo trạng thái đã gắn sao yêu thích (`Starred`).
     - Lọc danh sách theo thư mục đề tài nghiên cứu (`Folder`).
  3. Bấm vào bài báo để xem bảng thông tin chi tiết hoặc mở vào một Phiên đọc sâu mới.

---

### UC-DOC-04: Tiêu Hủy Tài Liệu Cá Nhân An Toàn (Safe Purge & Zero-Retention)
* **Tác nhân:** Học giả sở hữu tài liệu.
* **Điều kiện tiên quyết:** Học giả muốn gỡ bỏ một bài báo khỏi kho nghiên cứu.
* **Sự kiện kích hoạt:** Bấm biểu tượng Thùng rác (Xóa tài liệu) trên thẻ bài báo.
* **Luồng chuẩn (Happy Path):**
  1. Hệ thống hiển thị hộp thoại cảnh báo: "Bạn có chắc chắn muốn xóa bài báo này? Toàn bộ các đoạn trích và trích dẫn liên quan sẽ bị xóa vĩnh viễn."
  2. Người dùng xác nhận "Xóa vĩnh viễn".
  3. Hệ thống gỡ bài báo khỏi danh mục của người dùng, tự động đóng tab bài báo này trong mọi phiên đọc đang mở để tránh lỗi trang trắng.
  4. **Cam kết Tiêu hủy Vật lý (Zero-Retention):** Nếu không còn tài khoản nào khác trong hệ thống lưu trữ bài báo này, tệp nhị phân vật lý trên đĩa cứng máy chủ sẽ bị tiêu hủy ngay lập tức trong cùng chu kỳ xử lý, cam kết không tồn lưu file mồ côi.
  5. Hệ thống hiển thị thông báo "Đã tiêu hủy tài liệu thành công".

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
    And tự động tạo một phiên đọc mới và chuyển thẳng người dùng vào không gian Đọc sâu với PDF hiển thị sẵn

@documents @upload
Feature: Tải tài liệu PDF từ máy tính
  Scenario: Tải lên tài liệu hợp lệ thành công
    Given học giả chọn tệp "ResNet_Paper.pdf" dung lượng 12MB (45 trang)
    When kéo thả tệp vào vùng nạp tài liệu
    Then hệ thống hiển thị tiến độ tải lên từ 0 đến 100%
    And tệp được nạp thành công và chuyển sang trạng thái bóc tách mục lục ngầm

  Scenario: Từ chối tệp quá dung lượng cho phép
    Given học giả chọn tệp "Heavy_Book.pdf" dung lượng 65MB
    When cố gắng tải tệp lên
    Then hệ thống từ chối nhận tệp và hiển thị thông báo "Kích thước tệp vượt quá giới hạn 50MB của MVP"

@documents @zero_retention
Feature: Tiêu hủy dữ liệu vật lý tức thì
  Scenario: Xóa bài báo tiêu hủy file vật lý khi không còn người dùng nào trỏ tới
    Given học giả A sở hữu bài báo "Confidential_Draft.pdf" (chỉ có duy nhất học giả A lưu bài này)
    When học giả A bấm xác nhận "Xóa vĩnh viễn"
    Then hệ thống xóa bài báo khỏi danh sách của học giả A
    And tệp nhị phân vật lý trên đĩa cứng máy chủ bị tiêu hủy dứt điểm ngay trong chu kỳ request
```

---

## 5. Quy Tắc Nghiệp Vụ Bất Biến (Business Rules & Invariants)

1. **Giới Hạn Tệp Nạp Chuẩn Mực:** Tệp PDF tải lên giới hạn tối đa `50 MB`, tối đa `100 trang` và bắt buộc là Digital PDF có lớp văn bản đọc được.
2. **Khử Trùng Lặp Thông Minh:** Các bài báo kinh điển trùng khớp nội dung khi được tải lên bởi nhiều người dùng chỉ lưu 1 bản sao vật lý duy nhất để tiết kiệm không gian máy chủ, nhưng quyền sở hữu và dữ liệu ghi chú của từng người dùng hoàn toàn cô lập độc lập.
3. **Tiêu Hủy Vật Lý Đồng Bộ (Zero-Retention Invariant):** Ngay khi một tài liệu bị xóa và không còn người dùng nào sở hữu, tệp vật lý trên máy chủ bị xóa vĩnh viễn ngay lập tức.
4. **Không Để Lại Tab Mồ Côi:** Khi xóa một bài báo, tất cả các Phiên đọc đang mở bài báo đó phải tự động gỡ tab của bài này ra khỏi thanh tab, không để xảy ra tình trạng người dùng bấm vào tab bị lỗi 404.
