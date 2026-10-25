# VERISCHOLAR MVP — TÀI LIỆU YÊU CẦU SẢN PHẨM: KHÁM PHÁ BÀI BÁO & QUẢN LÝ TÀI LIỆU PDF
# (PRODUCT REQUIREMENTS DOCUMENT: SCHOLARLY DISCOVERY & DOCUMENTS MANAGEMENT)

**Mã phân hệ:** `PRD-02`  
**Phiên bản:** `2.1-ENHANCED`  
**Vai trò phụ trách:** Chuyên viên Phân tích Nghiệp vụ (Lead Business Analyst — BA)  
**Tài liệu Kỹ thuật liên đới:** [`02-discovery-and-documents-spec.md`](../specs/02-discovery-and-documents-spec.md)  
**Trạng thái:** CHÍNH THỨC BAN HÀNH (RELEASE CANDIDATE)

---

## 1. Tầm Nhìn & Nỗi Đau Nghiệp Vụ (Vision & Pain Points)

### 1.1. Tầm nhìn phân hệ
Trao quyền cho người làm nghiên cứu bắt đầu hành trình học thuật một cách tức thì ngay cả khi chưa có sẵn file tài liệu trong máy tính, thông qua công cụ tìm kiếm bài báo chuyên sâu theo ngữ nghĩa học thuật; đồng thời cung cấp hệ thống quản lý tài liệu cá nhân trực quan, bảo mật và hỗ trợ bóc tách tự động cấu trúc nội dung từ trang bìa đến trang tài liệu tham khảo.

### 1.2. Nỗi đau thực tế của học giả
1. **Định lượng thời gian mất mát do quy trình phân mảnh (Quantified Zero-to-Research Delay):**
   - Học giả, nghiên cứu sinh và giảng viên thường tiêu tốn từ **60–90 phút cho mỗi bài báo mới** chỉ để tìm kiếm qua lại giữa các kho dữ liệu học thuật phân mảnh (Google Scholar, arXiv, PubMed, IEEE Xplore, ScienceDirect), tải thủ công từng file PDF về máy tính, tự đặt tên file để lưu trữ và đối soát mã định danh DOI.
   - Sau khi tải xong, học giả mất thêm **30–45 phút** để loay hoay xử lý các lỗi định dạng, sao chép trích dẫn bị lỗi font hoặc cắt dán thủ công từng đoạn nội dung vào các công cụ ghi chú rời rạc. Tổng cộng mỗi người làm nghiên cứu lãng phí **5–8 giờ mỗi tuần** chỉ cho các khâu chuẩn bị sơ cấp trước khi thực sự bắt đầu đọc và đào sâu nội dung bài báo.

2. **Nỗi đau gặp file PDF scan ảnh không bôi đen được (Scanned Image PDF & Zero-Selectability Agony):**
   - Rất nhiều tài liệu khoa học kinh điển, kỷ yếu hội nghị trước năm 2010, sách chuyên khảo hoặc luận án tiến sĩ lưu trữ trong thư viện các trường đại học chỉ tồn tại dưới dạng file quét ảnh thuần túy (Scanned Image PDF), hoàn toàn không có lớp văn bản số hóa (No Digital Text Layer).
   - Khi mở các tài liệu này, học giả hoàn toàn bất lực vì **không thể bôi đen quét chọn khối chữ, không thể sao chép trích dẫn, không thể tra cứu từ khóa**. Các công cụ trợ lý AI thông thường lập tức báo lỗi hoặc tạo ra các đoạn suy diễn ảo giác (hallucination) vô nghĩa. Học giả buộc phải tự tay gõ lại từng định lý, bảng số liệu và đoạn văn tốn hàng giờ đồng hồ mệt mỏi và rất dễ phát sinh sai sót số liệu nghiêm trọng.

3. **Nỗi đau PDF 2 cột bị vỡ thứ tự đọc công thức toán (Two-Column Layout Distortion & Broken Math Formulas):**
   - Hơn 85% bài báo khoa học chuẩn quốc tế (IEEE, ACM, Springer, Elsevier, Nature, NeurIPS) được định dạng theo bố cục 2 cột (Two-Column Layout). Các công cụ đọc PDF và bóc tách thông thường có cơ chế đọc quét ngang từ trái sang phải qua cả 2 cột (reading across columns horizontally) thay vì đọc hết cột trái rồi mới sang cột phải.
   - Hệ quả là các dòng chữ ở cột 1 và cột 2 bị ghép lẫn lộn vào nhau tạo thành những câu vô nghĩa. Nguy hiểm hơn, **các công thức toán học nhiều dòng (multiline equations, LaTeX formulas) bị bẻ gãy thứ tự, ma trận và tích phân bị phân mảnh, ký hiệu chỉ số trên/dưới bị xáo trộn**, dẫn đến việc trợ lý AI giải thích sai hoàn toàn bản chất thuật toán và mô hình khoa học.

4. **Mối lo ngại về quyền riêng tư & rò rỉ bản thảo chưa công bố (Intellectual Property & Zero-Retention Anxiety):**
   - Các bản thảo đang gửi phản biện kín (Double-blind peer review) hoặc tài liệu nghiên cứu chứa bí mật công nghệ chưa đăng ký sáng chế có rủi ro bị rò rỉ nếu hệ thống lưu trữ file mồ côi trên máy chủ sau khi người dùng bấm xóa trên giao diện. Nỗi sợ này khiến học giả ngần ngại tải các tài liệu quan trọng lên nền tảng đám mây nếu không có cam kết tiêu hủy vật lý dứt điểm.

---

## 2. Chân Dung Tác Nhân (Actors & Personas)

* **Học giả khám phá (Exploring Scholar):** Cần tìm kiếm nhanh các bài báo liên quan đến một chủ đề mới và mở đọc ngay bản Open Access mà không cần tải file về máy.
* **Học giả có sẵn tài liệu (Document Uploader):** Đã có sẵn file PDF trong máy tính (bài báo tải từ thư viện trường hoặc bản thảo của nhóm nghiên cứu) và muốn tải lên để phân tích sâu.
* **Hệ thống bóc tách tài liệu tự động (Automated Document Parsing Engine):** Tác nhân hệ thống thực hiện phân tích trang, phát hiện mục lục, trích xuất đoạn văn theo thứ tự đọc học thuật 2 cột và lưu giữ tọa độ không gian trên trang PDF.

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
     * **`[🟢 Có sẵn PDF Open Access]`**: Bài báo có thể đọc trực tiếp miễn phí toàn văn.
     * **`[🟡 Chỉ có Tóm tắt]`**: Bài báo thuộc nguồn đóng phí, chỉ xem được tóm tắt và thông tin tác giả.
* **Luồng ngoại lệ (Alternative & Exception Flows):**
  * *1a. Không tìm thấy kết quả phù hợp do thuật ngữ hiếm gặp:* Hệ thống hiển thị trạng thái rỗng thân thiện: "Không tìm thấy bài báo khớp với chủ đề này. Hãy thử mở rộng từ khóa, bỏ bớt từ viết tắt hoặc chuyển sang tiếng Anh chuyên ngành."
  * *1b. Gián đoạn kết nối máy chủ học thuật quốc tế:* Nếu các kho lưu trữ ngoài (arXiv, Semantic Scholar) phản hồi chậm hoặc đang bảo trì, hệ thống hiển thị cảnh báo nhẹ: "Kết nối đến nguồn học thuật quốc tế đang bị nghẽn. Vui lòng thử lại sau vài giây hoặc sử dụng tính năng tải file PDF cá nhân."
  * *1c. Trùng lặp phiên bản bài báo giữa nhiều kho lưu trữ:* Khi cùng một công trình có cả bản tiền ấn phẩm (Preprint arXiv) và bản xuất bản chính thức (Conference/Journal), hệ thống tự động gộp thông minh theo mã định danh DOI, ưu tiên cung cấp liên kết tới bản có sẵn PDF toàn văn mở.
* **Hậu điều kiện (Post-conditions):**
  * *Thành công:* Danh sách tối đa 20 bài báo học thuật khớp nhất được hiển thị trên giao diện kèm nhãn trạng thái truy cập rõ ràng; học giả có thể chọn mở đọc ngay hoặc xem tóm tắt chỉ bằng 1 thao tác.
  * *Thất bại:* Không lưu lại các truy vấn rác; hệ thống giữ nguyên ô tìm kiếm kèm gợi ý chỉnh sửa từ khóa; không phát sinh trạng thái đơ hoặc tải trang vô tận.

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
  * *1a. Đường liên kết PDF mở bị gián đoạn hoặc bị chặn bởi tường lửa trường viện:* Hệ thống thông báo rõ: "Nguồn tải bài báo bị gián đoạn do chính sách mạng hoặc liên kết gốc thay đổi. Bạn có thể sử dụng nút Tự tải PDF lên từ máy tính."
  * *1b. Tải dở dang do đường truyền mạng bị ngắt giữa chừng:* Hệ thống đánh dấu trạng thái và hiển thị nút "Thử nạp lại bài báo" để học giả kích hoạt lại mà không cần tìm kiếm từ đầu.
  * *1c. Bài báo thuộc nguồn đóng phí (Paywall) chỉ có Tóm tắt:* Khi người dùng chọn bài có nhãn `[🟡 Chỉ có Tóm tắt]`, hệ thống vẫn mở Không gian đọc sâu ở chế độ Thẻ Tóm Tắt (`Abstract Viewer`) và hiển thị nút lớn: `[📤 Tải lên file PDF đầy đủ]` để người dùng tự tải bản PDF có sẵn từ thư viện trường lên.
* **Hậu điều kiện:**
  * *Thành công:* Bài báo được ghi nhận vào kho tài liệu riêng của học giả; một phiên đọc sâu mới được kích hoạt tức thì; giao diện hiển thị tài liệu chuẩn xác sẵn sàng đối thoại với trợ lý AI.
  * *Thất bại:* Không tạo các phiên đọc rác hoặc tài liệu lỗi trong danh mục người dùng; hiển thị thông báo nguyên nhân cụ thể và hoàn trả người dùng về trang tìm kiếm an toàn.

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
  * *1a. File vượt quá 50MB hoặc quá 100 trang:* Hệ thống từ chối nạp và thông báo: "Kích thước tệp vượt quá giới hạn 50MB hoặc quá 100 trang của gói sử dụng hiện tại."
  * *1b. File ảnh scan không có lớp chữ (Scanned Image PDF):* Hệ thống phát hiện ngay tại trang đầu tiên và cảnh báo: "Tài liệu này là tệp quét ảnh thuần túy không có lớp văn bản số hóa. Trợ lý AI cần file PDF kỹ thuật số để đọc chính xác từng dòng và công thức toán."
  * *1c. File PDF bị cài mật khẩu bảo vệ bản quyền (DRM / Password Protected):* Hệ thống thông báo: "Tệp PDF đang được bảo vệ bằng mật khẩu hoặc bị khóa bản quyền trích xuất. Vui lòng mở khóa tệp trước khi tải lên."
  * *1d. File PDF chứa khổ giấy bản vẽ khoa học đặc biệt (khổ A0, A1, hoặc xoay ngang):* Hệ thống tự động nhận diện và tính toán tỷ lệ co giãn phù hợp để hiển thị trọn vẹn trong khung đọc.
  * *1e. Tải tệp trùng lặp đã có:* Hệ thống thông báo tệp đã tồn tại trong kho tài liệu và đưa học giả vào xem bài báo ngay lập tức mà không tiêu tốn thêm băng thông.
* **Hậu điều kiện:**
  * *Thành công:* Tệp tài liệu được ghi nhận vào kho riêng của học giả; thanh tiến độ đạt 100%; tiến trình bóc tách cấu trúc ngầm được khởi động ngay lập tức; học giả có thể mở đọc ngay.
  * *Thất bại:* Tệp không hợp lệ bị từ chối; không chiếm dụng dung lượng lưu trữ của máy chủ; giao diện giải thích lý do từ chối rõ ràng kèm hướng dẫn khắc phục.

---

### UC-DOC-02: Bóc Tách Cấu Trúc & Tạo Lập Mục Lục Thông Minh
* **Tác nhân:** Hệ thống bóc tách tài liệu tự động.
* **Điều kiện tiên quyết:** File PDF đã được nạp thành công vào hệ thống.
* **Sự kiện kích hoạt:** Tự động kích hoạt ngay sau khi nạp file.
* **Luồng chuẩn (Happy Path):**
  1. Hệ thống phân tích cấu trúc bài báo theo đúng thứ tự đọc học thuật 2 cột (từ trên xuống dưới, từ cột trái sang cột phải, không đọc đan chéo cột).
  2. Bóc tách cây mục lục bài báo (`Document Structure`): Tiêu đề, Tóm tắt, Mục 1 (Introduction), Mục 2 (Related Work), Mục 3 (Methodology), v.v. kèm số trang chính xác.
  3. Cắt nhỏ nội dung thành các đoạn trích ngữ nghĩa, lưu giữ tọa độ hình học (Bounding Box) của từng đoạn trên trang PDF để phục vụ việc tô sáng viền vàng trực quan khi hỏi đáp sau này.
  4. Trạng thái tài liệu chuyển sang "Sẵn sàng nghiên cứu" (`Ready`). Người dùng có thể bấm vào bất kỳ mục nào trong Bảng Mục lục để cuộn trang PDF đến đúng vị trí tương ứng.
* **Luồng ngoại lệ:**
  * *1a. Bài báo không theo cấu trúc chuẩn (ví dụ báo cáo kỹ thuật không có mục Tóm tắt hoặc không đánh số phần):* Hệ thống tự động phân cấp tiêu đề dựa trên cỡ chữ và khoảng cách dòng, tạo lập cây mục lục tương đối để hỗ trợ điều hướng.
  * *1b. Tài liệu chứa khối công thức toán nhiều tầng hoặc bảng dữ liệu phức tạp:* Hệ thống bảo toàn tính toàn vẹn của khối không gian văn bản, đảm bảo việc tô sáng viền vàng trích dẫn sau này không bị lệch tọa độ.
  * *1c. Gián đoạn tiến trình phân tích ngầm:* Trạng thái bài báo chuyển sang "Cần xử lý lại" kèm nút "Phân tích lại tài liệu" trên giao diện để học giả kích hoạt lại chỉ với 1 cú click.
* **Hậu điều kiện:**
  * *Thành công:* Cây mục lục thông minh được trích xuất hoàn chỉnh; toàn bộ các đoạn văn bản được gắn tọa độ không gian chính xác; trạng thái tài liệu chuyển sang "Sẵn sàng nghiên cứu"; học giả có thể bấm mục lục để nhảy trang tức thì.
  * *Thất bại:* Trạng thái tài liệu hiển thị chỉ báo cần xử lý lại; học giả vẫn có thể xem file PDF bản gốc ở dạng tĩnh; không làm hỏng tài liệu gốc đã tải lên.

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
* **Luồng ngoại lệ:**
  * *1a. Không tìm thấy bài báo theo từ khóa lọc:* Hệ thống hiển thị: "Không tìm thấy tài liệu phù hợp trong kho cá nhân. Bạn có thể tìm kiếm trên kho mở quốc tế qua trang Khám phá."
  * *1b. Thư mục đề tài nghiên cứu trống:* Hiển thị khung gợi ý kéo thả tài liệu vào thư mục để phân loại theo đề tài.
  * *1c. Tài liệu đang trong tiến trình bóc tách ngầm:* Thẻ tài liệu hiển thị huy hiệu trạng thái "Đang phân tích cấu trúc..." kèm phần trăm tiến độ trực quan và tự động chuyển sang sẵn sàng khi hoàn tất.
* **Hậu điều kiện:**
  * *Thành công:* Danh mục tài liệu được hiển thị trực quan, phân loại khoa học theo đề tài và gắn sao yêu thích; học giả dễ dàng mở bất kỳ bài báo nào vào phiên nghiên cứu sâu.
  * *Thất bại:* Không làm xáo trộn danh mục tài liệu hiện có; khôi phục danh sách đầy đủ khi xóa từ khóa lọc.

---

### UC-DOC-04: Tiêu Hủy Tài Liệu Cá Nhân An Toàn (Safe Purge & Zero-Retention)
* **Tác nhân:** Học giả sở hữu tài liệu.
* **Điều kiện tiên quyết:** Học giả muốn gỡ bỏ một bài báo khỏi kho nghiên cứu.
* **Sự kiện kích hoạt:** Bấm biểu tượng Thùng rác (Xóa tài liệu) trên thẻ bài báo.
* **Luồng chuẩn (Happy Path):**
  1. Hệ thống hiển thị hộp thoại cảnh báo: "Bạn có chắc chắn muốn xóa bài báo này? Toàn bộ các đoạn trích và trích dẫn liên quan sẽ bị xóa vĩnh viễn."
  2. Người dùng xác nhận "Xóa vĩnh viễn".
  3. Hệ thống gỡ bài báo khỏi danh mục của người dùng, tự động đóng tab bài báo này trong mọi phiên đọc đang mở để tránh tình trạng lỗi trang trắng.
  4. **Cam kết Tiêu hủy Vật lý (Zero-Retention):** Nếu không còn tài khoản nào khác trong hệ thống lưu trữ bài báo này, tệp nhị phân vật lý trên đĩa cứng máy chủ sẽ bị tiêu hủy ngay lập tức trong cùng chu kỳ xử lý, cam kết không tồn lưu file mồ côi.
  5. Hệ thống hiển thị thông báo "Đã tiêu hủy tài liệu thành công".
* **Luồng ngoại lệ:**
  * *1a. Tài liệu đang được mở đọc đồng thời trong phiên nghiên cứu trên thiết bị khác:* Hệ thống tự động đóng phiên đọc liên quan trên thiết bị kia để bảo đảm tính nhất quán dữ liệu.
  * *1b. Học giả yêu cầu xóa tài liệu đang trong tiến trình bóc tách ngầm:* Hệ thống lập tức hủy bỏ tác vụ nền, thu hồi toàn bộ tài nguyên xử lý và tiêu hủy file an toàn.
  * *1c. Học giả chọn Hủy bỏ trong hộp thoại cảnh báo:* Thao tác dừng lại ngay lập tức, tài liệu và các phiên đọc liên quan được giữ nguyên vẹn 100%.
* **Hậu điều kiện:**
  * *Thành công:* Bài báo bị xóa vĩnh viễn khỏi danh mục của học giả; các tab bài báo liên quan tự động đóng an toàn; tệp vật lý bị tiêu hủy dứt điểm nếu không còn người dùng nào sở hữu; dữ liệu mồ côi không tồn lưu trên hệ thống.
  * *Thất bại:* Khi học giả hủy thao tác, toàn bộ dữ liệu tài liệu và phiên đọc được giữ nguyên vẹn không suy suyển.

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
    Then hệ thống từ chối nhận tệp và hiển thị thông báo "Kích thước tệp vượt quá giới hạn 50MB của gói sử dụng hiện tại"

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

1. **Giới Hạn Tệp Nạp Chuẩn Mực:** Tệp PDF tải lên giới hạn tối đa `50 MB`, tối đa `100 trang` và bắt buộc là Digital PDF có lớp văn bản đọc được.
2. **Khử Trùng Lặp Thông Minh:** Các bài báo kinh điển trùng khớp nội dung khi được tải lên bởi nhiều người dùng chỉ lưu 1 bản sao vật lý duy nhất để tiết kiệm không gian máy chủ, nhưng quyền sở hữu và dữ liệu ghi chú của từng người dùng hoàn toàn cô lập độc lập.
3. **Tiêu Hủy Vật Lý Đồng Bộ (Zero-Retention Invariant):** Ngay khi một tài liệu bị xóa và không còn người dùng nào sở hữu, tệp vật lý trên máy chủ bị xóa vĩnh viễn ngay lập tức trong chu kỳ xử lý này.
4. **Không Để Lại Tab Mồ Côi:** Khi xóa một bài báo, tất cả các Phiên đọc đang mở bài báo đó phải tự động gỡ tab của bài này ra khỏi thanh tab, không để xảy ra tình trạng người dùng bấm vào tab bị lỗi không tìm thấy tài nguyên.
