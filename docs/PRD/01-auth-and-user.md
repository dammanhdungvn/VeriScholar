# VERISCHOLAR MVP — TÀI LIỆU YÊU CẦU SẢN PHẨM: XÁC THỰC, HỒ SƠ HỌC GIẢ & BẢO MẬT KHÓA BYOK
# (PRODUCT REQUIREMENTS DOCUMENT: AUTHENTICATION, SCHOLAR PROFILE & BYOK PRIVACY)

**Mã phân hệ:** `PRD-01`  
**Phiên bản:** `2.0-OFFICIAL`  
**Vai trò phụ trách:** Chuyên viên Phân tích Nghiệp vụ (Lead Business Analyst — BA)  
**Tài liệu Kỹ thuật liên đới:** [`01-auth-and-user-spec.md`](../specs/01-auth-and-user-spec.md)  
**Trạng thái:** CHÍNH THỨC BAN HÀNH (RELEASE CANDIDATE)

---

## 1. Tầm Nhìn & Nỗi Đau Nghiệp Vụ (Vision & Real-World Pain Points)

### 1.1. Tầm nhìn phân hệ
Cung cấp một cổng truy cập an toàn, tin cậy và tiện lợi, bảo vệ tính riêng tư tuyệt đối cho các tài sản học thuật của người nghiên cứu (bài báo chưa công bố, ghi chú ý tưởng, bản thảo khoa học), đồng thời trao quyền cho học giả tự chủ về năng lực tính toán AI thông qua cơ chế tự cung cấp khóa API cá nhân (BYOK).

### 1.2. Nỗi đau thực tế của học giả
1. **Nguy cơ rò rỉ ý tưởng nghiên cứu:** Bản thảo và tài liệu khoa học là tài sản sở hữu trí tuệ vô giá. Nếu hệ thống cho phép người dùng này xem hoặc đoán được tài liệu của người dùng khác, uy tín học thuật sẽ bị hủy hoại hoàn toàn.
2. **Phiền toái khi đổi thiết bị làm việc:** Học giả thường làm việc xen kẽ giữa máy tính phòng thí nghiệm, máy tính thư viện và laptop cá nhân. Cơ chế xác thực phải linh hoạt (hỗ trợ cả tài khoản email và đăng nhập nhanh 1-Click qua Google/GitHub), đồng thời tự động duy trì phiên làm việc không gián đoạn.
3. **Giới hạn hạn mức AI (Rate Limit & Cost Ceiling):** Sinh viên và nhà nghiên cứu có nhu cầu sử dụng AI chuyên sâu với khối lượng lớn thường gặp phải rào cản giới hạn câu hỏi trên các gói tài khoản miễn phí. Nền tảng cần hỗ trợ cơ chế cho phép người dùng tự nhập khóa API riêng (BYOK) để sử dụng không giới hạn, nhưng khóa này phải được mã hóa tuyệt đối an toàn trên máy chủ.

---

## 2. Chân Dung Tác Nhân (Actors & Personas)

* **Học giả đã xác thực (Verified Scholar):** Người dùng đã đăng ký và xác nhận email, có toàn quyền tạo phiên đọc, tải tài liệu, tạo bản thảo và cấu hình khóa BYOK cá nhân.
* **Học giả mới đăng ký (Unverified Scholar):** Tài khoản vừa tạo, được phép khám phá hệ thống nhưng cần hoàn tất xác thực email để kích hoạt các tính năng xuất bản và bảo mật nâng cao.
* **Khách vãng lai (Guest User):** Người dùng chưa đăng nhập, chỉ được xem trang giới thiệu (Landing Page) và được điều hướng đến màn hình Đăng nhập/Đăng ký khi bấm bắt đầu.

---

## 3. Đặc Tả Chi Tiết Các Use Cases Nghiệp Vụ (Detailed Use Cases)

### UC-AUTH-01: Đăng Ký Tài Khoản Học Giả Mới
* **Tác nhân:** Khách vãng lai.
* **Điều kiện tiên quyết:** Chưa đăng nhập vào hệ thống.
* **Sự kiện kích hoạt:** Bấm nút "Đăng ký" trên trang Landing Page hoặc chuyển từ form Đăng nhập.
* **Luồng chuẩn (Happy Path):**
  1. Người dùng nhập: Họ và tên, Địa chỉ Email, Mật khẩu (tối thiểu 8 ký tự, có chữ và số), và Xác nhận mật khẩu.
  2. Người dùng bấm "Tạo tài khoản".
  3. Hệ thống kiểm tra tính hợp lệ của dữ liệu đầu vào và kiểm tra email chưa tồn tại trên hệ thống.
  4. Hệ thống tạo tài khoản mới ở trạng thái chờ xác thực, tự động gửi email chứa liên kết/mã OTP xác nhận đến hòm thư người dùng.
  5. Hệ thống cấp phiên làm việc tức thì và chuyển hướng người dùng đến màn hình chính kèm thông báo nhắc xác thực email.
* **Luồng ngoại lệ (Alternative & Exception Flows):**
  * *1a. Email đã tồn tại:* Hệ thống hiển thị thông báo lỗi rõ ràng: "Địa chỉ email này đã được sử dụng. Vui lòng đăng nhập hoặc sử dụng tính năng quên mật khẩu."
  * *1b. Mật khẩu không đủ độ mạnh:* Hệ thống hiển thị lỗi ngay dưới ô nhập liệu: "Mật khẩu phải chứa ít nhất 8 ký tự bao gồm chữ cái và số."
  * *1c. Lỗi gửi email xác thực:* Hệ thống vẫn cho phép vào trang chính nhưng hiển thị nút "Gửi lại email xác thực" trên thanh thông báo.

---

### UC-AUTH-02: Đăng Nhập & Duy Trì Phiên Làm Việc
* **Tác nhân:** Học giả đã có tài khoản.
* **Điều kiện tiên quyết:** Có tài khoản email/mật khẩu hoặc tài khoản Google/GitHub.
* **Sự kiện kích hoạt:** Bấm "Đăng nhập" từ màn hình chính.
* **Luồng chuẩn (Happy Path):**
  * **Cách A — Email & Mật khẩu:**
    1. Người dùng nhập Email, Mật khẩu và tùy chọn tích chọn "Ghi nhớ đăng nhập" (Remember Me).
    2. Người dùng bấm nút "Đăng nhập".
    3. Hệ thống kiểm tra thông tin chính xác, cấp phiên truy cập an toàn và đưa người dùng vào Không gian làm việc.
  * **Cách B — Đăng nhập 1-Click (Google / GitHub OAuth):**
    1. Người dùng bấm biểu tượng "Đăng nhập với Google" hoặc "Đăng nhập với GitHub".
    2. Cửa sổ ủy quyền nhà cung cấp xuất hiện; người dùng đồng ý cấp quyền email và hồ sơ cơ bản.
    3. Hệ thống tự động liên kết hoặc tạo tài khoản mới nếu lần đầu đăng nhập, sau đó chuyển thẳng vào Không gian làm việc.
* **Luồng ngoại lệ:**
  * *1a. Sai email hoặc sai mật khẩu:* Hệ thống hiển thị thông báo chung: "Email hoặc mật khẩu không chính xác" (không chỉ đích danh sai trường nào để chống dò quét tài khoản).
  * *1b. Phiên làm việc hết hạn:* Trong quá trình học giả đang đọc bài báo, hệ thống tự động gia hạn phiên làm việc ngầm mà không làm gián đoạn việc đọc hay làm mất nội dung đang gõ.

---

### UC-AUTH-03: Khôi Phục Mật Khẩu Bằng Mã OTP
* **Tác nhân:** Học giả quên mật khẩu truy cập.
* **Điều kiện tiên quyết:** Đã có tài khoản trên hệ thống.
* **Sự kiện kích hoạt:** Bấm "Quên mật khẩu?" tại form Đăng nhập.
* **Luồng chuẩn (Happy Path):**
  1. Người dùng nhập địa chỉ email đã đăng ký và bấm "Gửi mã khôi phục".
  2. Hệ thống gửi mã OTP gồm 6 chữ số (hiệu lực trong 10 phút) đến email của người dùng và hiển thị màn hình nhập OTP.
  3. Người dùng nhập mã OTP 6 chữ số và nhập mật khẩu mới.
  4. Hệ thống xác nhận mã OTP chính xác, cập nhật mật khẩu mới và thông báo "Đổi mật khẩu thành công! Vui lòng đăng nhập lại."
* **Luồng ngoại lệ:**
  * *1a. Nhập email chưa từng đăng ký:* Để bảo vệ tính riêng tư chống dò quét tài khoản (Anti-Enumeration), hệ thống vẫn hiển thị thông báo thành công: "Nếu email tồn tại, mã xác thực đã được gửi." nhưng thực tế không phát sinh email.
  * *3a. Nhập sai OTP quá 5 lần:* Hệ thống vô hiệu hóa mã OTP hiện tại và yêu cầu người dùng chờ 10 phút trước khi yêu cầu mã mới.

---

### UC-AUTH-04: Quản Lý Hồ Sơ Học Thuật Cá Nhân
* **Tác nhân:** Học giả đang đăng nhập.
* **Điều kiện tiên quyết:** Đã đăng nhập vào hệ thống.
* **Sự kiện kích hoạt:** Truy cập mục `👤 Tài khoản & Cấu hình` trên thanh Sidebar.
* **Luồng chuẩn (Happy Path):**
  1. Màn hình hiển thị đầy đủ thông tin: Ảnh đại diện, Họ tên, Email, Đơn vị công tác (Viện / Trường Đại học), Học hàm / Học vị (Sinh viên, Thạc sĩ, Tiến sĩ, PGS, GS), Mã định danh khoa học quốc tế ORCID, và Giới thiệu ngắn gọn hướng nghiên cứu.
  2. Người dùng cập nhật các thông tin học thuật mong muốn và bấm "Lưu thay đổi".
  3. Hệ thống cập nhật hồ sơ và hiển thị thông báo thành công.
* **Luồng ngoại lệ:**
  * *2a. Định dạng ORCID không chuẩn:* Hệ thống cảnh báo định dạng hợp lệ (dạng `0000-0000-0000-0000`).

---

### UC-AUTH-05: Cấu Hình Khóa Riêng Tư AI (Bring Your Own Key — BYOK)
* **Tác nhân:** Học giả muốn sử dụng khóa API riêng để mở rộng năng lực tính toán.
* **Điều kiện tiên quyết:** Sở hữu khóa API từ nhà cung cấp (OpenAI API Key).
* **Sự kiện kích hoạt:** Người dùng mở tab "Cấu hình AI & Khóa riêng" trong trang Cài đặt tài khoản.
* **Luồng chuẩn (Happy Path):**
  1. Màn hình hiển thị trạng thái hiện tại: "Đang sử dụng hạn mức mặc định của nền tảng".
  2. Người dùng nhập khóa cá nhân vào ô "Khóa OpenAI API cá nhân (BYOK)". Ký tự khóa tự động bị ẩn dưới dạng `sk-...••••••••`.
  3. Người dùng bấm "Lưu & Xác thực khóa".
  4. Hệ thống kiểm tra khóa hợp lệ với máy chủ nhà cung cấp, mã hóa bảo mật cấp cao trước khi lưu trữ, và cập nhật trạng thái: "Đã kích hoạt khóa riêng thành công".
  5. Kể từ thời điểm này, mọi tác vụ hỏi đáp RAG và biên dịch AI trong phiên làm việc của người dùng sẽ ưu tiên sử dụng hạn mức từ khóa riêng này.
* **Luồng ngoại lệ:**
  * *3a. Khóa API không hợp lệ hoặc hết hạn ngạch:* Hệ thống cảnh báo ngay lập tức: "Không thể kết nối đến nhà cung cấp với khóa API đã nhập. Vui lòng kiểm tra lại hạn mức tài khoản của bạn." và không lưu khóa sai.
  * *Người dùng muốn xóa khóa riêng:* Người dùng bấm "Gỡ khóa riêng", hệ thống xóa vĩnh viễn khóa và hoàn trả về hạn mức mặc định.

---

### UC-AUTH-06: Chuyển Đổi Chủ Đề Giao Diện Sáng / Tối
* **Tác nhân:** Mọi học giả đang tương tác trên giao diện.
* **Điều kiện tiên quyết:** Đang mở ứng dụng.
* **Sự kiện kích hoạt:** Bấm nút biểu tượng Mặt trời / Mặt trăng trên thanh công cụ hoặc chọn trong trang Cài đặt.
* **Luồng chuẩn (Happy Path):**
  1. Người dùng chọn 1 trong 3 tùy chọn: Sáng (Light), Tối (Dark), hoặc Theo hệ thống (System Default).
  2. Giao diện đổi màu mượt mà ngay lập tức (< 50ms) không cần tải lại trang.
  3. Hệ thống lưu tùy chọn này vào tài khoản của người dùng để đồng bộ khi mở trên thiết bị khác.

---

## 4. Tiêu Chí Nghiệm Thu Hành Vi (Gherkin Acceptance Criteria)

```gherkin
@auth @registration
Feature: Đăng ký tài khoản học giả mới
  Scenario: Đăng ký thành công với thông tin hợp lệ
    Given khách vãng lai đang ở màn hình Đăng ký
    When nhập họ tên "Nguyễn Văn Khoa", email "khoa.nguyen@univ.edu.vn", mật khẩu "Science2026@"
    And bấm nút "Tạo tài khoản"
    Then hệ thống tạo tài khoản mới và gửi mã xác nhận đến email "khoa.nguyen@univ.edu.vn"
    And chuyển hướng người dùng vào trang Không gian làm việc

  Scenario: Đăng ký thất bại do trùng lặp email
    Given một tài khoản với email "khoa.nguyen@univ.edu.vn" đã tồn tại trên hệ thống
    When khách vãng lai cố gắng đăng ký với email "khoa.nguyen@univ.edu.vn"
    Then hệ thống từ chối đăng ký và hiển thị thông báo "Địa chỉ email này đã được sử dụng"

@auth @byok
Feature: Bảo mật khóa riêng cá nhân BYOK
  Scenario: Thiết lập khóa BYOK thành công
    Given học giả đang đăng nhập và truy cập trang Cài đặt Khóa riêng
    When nhập khóa OpenAI hợp lệ dạng "sk-proj-..."
    And bấm nút "Lưu & Xác thực khóa"
    Then hệ thống xác nhận khóa hợp lệ, mã hóa an toàn và thông báo "Đã kích hoạt khóa riêng thành công"
    And giao diện ẩn các ký tự khóa chỉ hiển thị 4 ký tự cuối

@auth @isolation
Feature: Cô lập dữ liệu đa người dùng tuyệt đối
  Scenario: Không thể truy cập tài nguyên của học giả khác
    Given học giả A đang đăng nhập với tài khoản "userA@univ.edu.vn"
    When học giả A cố tình truy cập vào đường dẫn tài liệu hoặc phiên đọc thuộc sở hữu của học giả B
    Then hệ thống phản hồi thông báo "Không tìm thấy tài nguyên"
    And tuyệt đối không hiển thị bất kỳ tiêu đề hay nội dung nào của học giả B
```

---

## 5. Quy Tắc Nghiệp Vụ Bất Biến (Business Rules & Invariants)

1. **Khóa Ngoại Buộc Thuộc Người Dùng (User Ownership Invariant):** Toàn bộ dữ liệu bài báo, phiên đọc, bản thảo và ghi chú đều là tài sản riêng của học giả sở hữu. Khi một học giả xóa tài khoản, toàn bộ dữ liệu thuộc sở hữu của họ phải bị xóa sạch khỏi hệ thống.
2. **Không Tiết Lộ Danh Tính Qua Thông Báo Lỗi (Anti-Enumeration Rule):** Mọi thông báo lỗi đăng nhập hoặc quên mật khẩu phải dùng câu chữ trung tính, không để lộ thông tin email đó có tồn tại trên hệ thống hay không.
3. **Bảo Mật Tuyệt Đối Khóa BYOK:** Khóa riêng tư của học giả chỉ được dùng để phục vụ các yêu cầu AI phát sinh từ chính tài khoản đó; máy chủ không bao giờ trả về nguyên vẹn khóa thô sau khi đã lưu.
