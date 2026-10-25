# VERISCHOLAR MVP — TÀI LIỆU YÊU CẦU SẢN PHẨM: XÁC THỰC, HỒ SƠ HỌC GIẢ & BẢO MẬT KHÓA BYOK
# (PRODUCT REQUIREMENTS DOCUMENT: AUTHENTICATION, SCHOLAR PROFILE & BYOK PRIVACY)

**Mã phân hệ:** `PRD-01`  
**Phiên bản:** `2.1-ENHANCED`  
**Vai trò phụ trách:** Chuyên viên Phân tích Nghiệp vụ (Lead Business Analyst — BA)  
**Tài liệu Kỹ thuật liên đới:** [`01-auth-and-user-spec.md`](../specs/01-auth-and-user-spec.md)  
**Trạng thái:** CHÍNH THỨC BAN HÀNH (RELEASE CANDIDATE)

---

## 1. Tầm Nhìn & Nỗi Đau Nghiệp Vụ (Vision & Real-World Pain Points)

### 1.1. Tầm nhìn phân hệ
Cung cấp một cổng truy cập an toàn, tin cậy và tiện lợi, bảo vệ tính riêng tư tuyệt đối cho các tài sản học thuật của người nghiên cứu (bài báo chưa công bố, ghi chú ý tưởng, bản thảo khoa học), đồng thời trao quyền cho học giả tự chủ về năng lực tính toán AI thông qua cơ chế tự cung cấp khóa API cá nhân (BYOK).

### 1.2. Nỗi đau thực tế của học giả
1. **Định lượng thời gian mất mát do gián đoạn phiên làm việc (Quantified Time Drain):**
   - Học giả, nghiên cứu sinh và giảng viên thường xuyên làm việc luân phiên giữa 3–4 thiết bị mỗi ngày: máy trạm tại phòng lab thí nghiệm, máy tính tra cứu tại thư viện trường, laptop cá nhân và máy tính để bàn tại nhà riêng.
   - Việc cơ chế phiên đăng nhập thường xuyên bị ngắt quãng, bắt buộc nhập lại mật khẩu liên tục, thất lạc các tab tài liệu đang nghiên cứu dở và phải thiết lập lại môi trường làm việc gây lãng phí trung bình **30–45 phút mỗi ngày** (tương đương hơn 15 giờ mỗi tháng). Đây là khoảng thời gian lãng phí vô ích làm phân tán mạch tư duy học thuật đỉnh cao.

2. **Nỗi sợ lộ khóa API cá nhân gắn thẻ tín dụng (Personal API Key & Financial Dread):**
   - Để sử dụng các mô hình ngôn ngữ lớn tiên tiến nhất nhằm phân tích dữ liệu chuyên sâu, nhiều nhà nghiên cứu phải tự chi trả tiền túi thông qua thẻ tín dụng cá nhân liên kết trực tiếp với tài khoản nhà cung cấp AI với hạn mức thanh toán tự động lên tới hàng trăm hoặc hàng nghìn USD mỗi tháng.
   - **Nỗi sợ hãi tột cùng của học giả là khóa API cá nhân bị rò rỉ công khai hoặc bị lưu trữ không an toàn trên máy chủ của bên thứ ba**. Nếu khóa bị đánh cắp, kẻ gian có thể rút cạn hạn mức thẻ tín dụng chỉ trong vài giờ với số tiền khổng lồ, đồng thời làm lộ lịch sử các câu hỏi nghiên cứu mật chứa đựng các ý tưởng phát minh hoặc bản thảo độc quyền chưa công bố.

3. **Rủi ro cạn hạn ngạch AI giữa chừng khi đang đọc bài (Mid-Reading Quota Exhaustion & Deadline Panic):**
   - Khi đang tập trung cao độ để phân tích một bài báo khoa học dài 40–50 trang trước thềm hạn chót (deadline) nộp bản thảo hội nghị hoặc bảo vệ luận án (chỉ còn vài giờ), việc các nền tảng AI dùng chung bất ngờ báo lỗi cạn kiệt hạn ngạch (*"Bạn đã hết lượt sử dụng trong gói, vui lòng thử lại sau 3 giờ"*) là một thảm họa đối với tiến độ nghiên cứu.
   - Dòng tư duy phân tích bị bẻ gãy đột ngột, học giả bị đẩy vào tình thế bị động, hoang mang và có nguy cơ trễ hạn nộp bài. Nền tảng cần cơ chế tự chủ hạn ngạch giúp học giả hoàn toàn làm chủ tiến độ nghiên cứu của chính mình.

4. **Nguy cơ rò rỉ ý tưởng nghiên cứu & bản thảo chưa công bố (Intellectual Property Risks):**
   - Bản thảo và tài liệu khoa học là tài sản sở hữu trí tuệ vô giá quyết định học vị và uy tín học thuật của nhà nghiên cứu. Nếu hệ thống cho phép người dùng này xem hoặc vô tình đoán được tài liệu của người dùng khác qua các kẽ hở phân quyền, toàn bộ công trình dày công chuẩn bị có thể bị chiếm đoạt hoặc công bố trước, gây thiệt hại không thể cứu vãn.

---

## 2. Chân Dung Tác Nhân (Actors & Personas)

* **Học giả đã xác thực (Verified Scholar):** Người dùng đã đăng ký và xác nhận email học thuật, có toàn quyền tạo phiên đọc sâu, tải tài liệu PDF, quản lý bản thảo và cấu hình khóa riêng tư cá nhân (BYOK).
* **Học giả mới đăng ký (Unverified Scholar):** Tài khoản vừa tạo, được phép khám phá hệ thống nhưng cần hoàn tất xác thực thư điện tử để kích hoạt các tính năng xuất bản, chia sẻ và bảo mật nâng cao.
* **Khách vãng lai (Guest User):** Người dùng chưa đăng nhập, chỉ được xem trang giới thiệu (Landing Page) và được điều hướng đến màn hình Đăng nhập/Đăng ký khi bấm bắt đầu trải nghiệm.

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
  4. Hệ thống tạo tài khoản mới ở trạng thái chờ xác thực, tự động gửi email chứa liên kết và mã xác nhận đến hòm thư người dùng.
  5. Hệ thống cấp phiên làm việc tức thì và chuyển hướng người dùng đến màn hình chính kèm thông báo nhắc xác thực email.
* **Luồng ngoại lệ (Alternative & Exception Flows):**
  * *1a. Email đã tồn tại:* Hệ thống hiển thị thông báo lỗi rõ ràng: "Địa chỉ email này đã được sử dụng. Vui lòng đăng nhập hoặc sử dụng tính năng quên mật khẩu."
  * *1b. Mật khẩu không đủ độ mạnh:* Hệ thống hiển thị lỗi ngay dưới ô nhập liệu: "Mật khẩu phải chứa ít nhất 8 ký tự bao gồm chữ cái và số."
  * *1c. Tường lửa thư tín viện trường chặn email xác thực:* Hệ thống thư tín của các trường đại học (`.edu.vn`, `.ac.uk`) thường kích hoạt bộ lọc thư rác nghiêm ngặt khiến email kích hoạt bị đưa vào hòm thư rác hoặc bị giữ lại kiểm duyệt; hệ thống duy trì trạng thái đăng ký tạm thời, cho phép vào không gian làm việc cơ bản và cung cấp nút bấm "Gửi lại email xác thực" kèm gợi ý kiểm tra hòm thư rác.
  * *1d. Tên người dùng chứa học hàm/học vị hoặc ký tự đặc biệt khoa học:* Người dùng nhập các danh xưng học thuật như `PGS. TS. Trần Văn B` hoặc ký tự có dấu bản ngữ; hệ thống giữ nguyên định dạng danh xưng trang trọng mà không làm lỗi hiển thị giao diện.
  * *1e. Nhấn đúp chuột liên tục do mạng phòng lab gián đoạn:* Hệ thống tự động vô hiệu hóa nút bấm ngay sau lần nhấn đầu tiên, hiển thị chỉ báo đang xử lý để ngăn chặn việc tạo trùng yêu cầu.
* **Hậu điều kiện (Post-conditions):**
  * *Thành công:* Bản ghi tài khoản học giả được tạo ở trạng thái chờ xác thực; phiên làm việc ban đầu được cấp phát; thư điện tử xác thực được gửi đi thành công; học giả được chuyển đến Không gian làm việc cá nhân.
  * *Thất bại:* Không có tài khoản rác nào được lưu lại trên hệ thống; không cấp phiên đăng nhập; mật khẩu nhập vào được xóa sạch khỏi bộ nhớ giao diện; hiển thị cảnh báo lỗi cụ thể để học giả chỉnh sửa.

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
  * *1a. Sai email hoặc sai mật khẩu:* Hệ thống hiển thị thông báo chung: "Email hoặc mật khẩu không chính xác" (không chỉ đích danh trường nào sai nhằm ngăn chặn hành vi dò quét danh tính học giả).
  * *1b. Gián đoạn kết nối mạng thư viện/phòng lab:* Nếu mạng wifi bị ngắt khi đang thao tác, giao diện chuyển sang trạng thái ngoại tuyến tạm thời, lưu trữ nội dung ghi chú đang gõ vào bộ đệm trình duyệt và tự động đồng bộ lại ngay khi có mạng mà không làm văng phiên đăng nhập.
  * *1c. Phiên làm việc hết hạn trong lúc đang phân tích bài báo:* Hệ thống tự động gia hạn phiên làm việc ngầm mà không làm mới lại trang, không làm gián đoạn việc cuộn đọc tài liệu PDF và không làm mất nội dung đang đối thoại với trợ lý AI.
  * *1d. Chính sách trường học chặn ủy quyền bên thứ ba:* Nếu tổ chức khóa đăng nhập Google bên thứ ba, hệ thống hướng dẫn người dùng chuyển sang khôi phục tài khoản qua Email chính thống.
* **Hậu điều kiện:**
  * *Thành công:* Học giả có phiên đăng nhập hợp lệ; danh mục tài liệu, phiên đọc sâu và ghi chú học thuật riêng được tải đầy đủ; cấu hình giao diện sáng/tối được áp dụng đúng chuẩn.
  * *Thất bại:* Phiên làm việc không được cấp; không rò rỉ bất kỳ thông tin nào về sự tồn tại của tài khoản; giao diện giữ nguyên form đăng nhập kèm thông báo lỗi trung tính.

---

### UC-AUTH-03: Khôi Phục Mật Khẩu Bằng Mã OTP
* **Tác nhân:** Học giả quên mật khẩu truy cập.
* **Điều kiện tiên quyết:** Đã có tài khoản trên hệ thống.
* **Sự kiện kích hoạt:** Bấm "Quên mật khẩu?" tại form Đăng nhập.
* **Luồng chuẩn (Happy Path):**
  1. Người dùng nhập địa chỉ email đã đăng ký và bấm "Gửi mã khôi phục".
  2. Hệ thống gửi mã xác thực gồm 6 chữ số (hiệu lực trong 5 phút) đến email của người dùng và hiển thị màn hình nhập mã.
  3. Người dùng nhập mã xác thực 6 chữ số và nhập mật khẩu mới.
  4. Hệ thống xác nhận mã chính xác, cập nhật mật khẩu mới và thông báo "Đổi mật khẩu thành công! Vui lòng đăng nhập lại."
* **Luồng ngoại lệ:**
  * *1a. Nhập email chưa từng đăng ký:* Để bảo vệ tính riêng tư chống dò quét tài khoản (Anti-Enumeration), hệ thống vẫn hiển thị thông báo thành công: "Nếu email tồn tại trên hệ thống, mã xác thực đã được gửi." nhưng thực tế không phát sinh thư gửi đi.
  * *2a. Mã xác thực đến chậm do hệ thống thư tín học viện:* Hệ thống hiển thị bộ đếm ngược 60 giây trước khi cho phép bấm nút "Gửi lại mã", đồng thời kéo dài thời gian hiệu lực của mã lên 5 phút để học giả kịp nhận và xử lý.
  * *3a. Sao chép dính khoảng trắng:* Nếu học giả sao chép mã từ email bị dính khoảng trắng ở đầu hoặc cuối, hệ thống tự động loại bỏ khoảng trắng thừa trước khi đối soát.
  * *3b. Nhập sai mã quá 5 lần:* Hệ thống vô hiệu hóa mã hiện tại, khóa tạm thời tính năng gửi lại mã cho email này trong 15 phút để ngăn chặn hành vi dò mã tự động.
* **Hậu điều kiện:**
  * *Thành công:* Mật khẩu mới được cập nhật an toàn; mã xác thực cũ bị hủy bỏ ngay lập tức; toàn bộ các phiên đăng nhập đang hoạt động trên các thiết bị khác (nếu có) bị đăng xuất bắt buộc; học giả có thể đăng nhập bằng mật khẩu mới.
  * *Thất bại:* Mật khẩu cũ không bị thay đổi; hồ sơ người dùng giữ nguyên vẹn; tài khoản không bị xóa hoặc hỏng dữ liệu; thông báo hướng dẫn người dùng thử lại sau khoảng thời gian quy định.

---

### UC-AUTH-04: Quản Lý Hồ Sơ Học Thuật Cá Nhân
* **Tác nhân:** Học giả đang đăng nhập.
* **Điều kiện tiên quyết:** Đã đăng nhập vào hệ thống.
* **Sự kiện kích hoạt:** Truy cập mục `👤 Tài khoản & Cấu hình` trên thanh điều hướng.
* **Luồng chuẩn (Happy Path):**
  1. Màn hình hiển thị đầy đủ thông tin: Ảnh đại diện, Họ tên, Email, Đơn vị công tác (Viện / Trường Đại học), Khoa / Bộ môn, Học hàm / Học vị (Sinh viên, Thạc sĩ, Tiến sĩ, PGS, GS), Mã định danh khoa học quốc tế ORCID, và Giới thiệu ngắn gọn hướng nghiên cứu.
  2. Người dùng cập nhật các thông tin học thuật mong muốn và bấm "Lưu thay đổi".
  3. Hệ thống cập nhật hồ sơ và hiển thị thông báo thành công.
* **Luồng ngoại lệ:**
  * *2a. Định dạng ORCID không chuẩn quốc tế:* Nếu người dùng nhập sai cấu trúc 16 ký tự phân tách bằng dấu gạch ngang (ví dụ không đúng dạng `0000-0000-0000-0000`), hệ thống cảnh báo cụ thể: "Mã ORCID phải tuân thủ định dạng chuẩn quốc tế gồm 16 chữ số phân tách bằng dấu gạch ngang."
  * *2b. Tên viện nghiên cứu quốc tế dài vượt mức:* Giao diện tự động co giãn dòng hiển thị thông minh, đảm bảo thông tin hiển thị đầy đủ và trang trọng mà không làm vỡ khung giao diện hồ sơ.
  * *2c. Đường dẫn Google Scholar không đúng cấu trúc:* Hệ thống nhắc nhở bổ sung đúng tiền tố liên kết học thuật hợp lệ.
* **Hậu điều kiện:**
  * *Thành công:* Dữ liệu hồ sơ học thuật được ghi nhận chuẩn xác; thông tin danh xưng và mã ORCID hiển thị đồng bộ trên thẻ tác giả trong toàn bộ các bản thảo nghiên cứu của người dùng; trạng thái đồng bộ hoàn tất trên mọi thiết bị.
  * *Thất bại:* Dữ liệu hồ sơ cũ được bảo toàn tuyệt đối; các trường thông tin sai quy chuẩn được làm nổi bật với thông báo khắc phục rõ ràng; không xảy ra hiện tượng lưu dở dang dữ liệu.

---

### UC-AUTH-05: Cấu Hình Khóa Riêng Tư AI (Bring Your Own Key — BYOK)
* **Tác nhân:** Học giả muốn sử dụng khóa API riêng để mở rộng năng lực tính toán không giới hạn.
* **Điều kiện tiên quyết:** Sở hữu khóa API hợp lệ từ nhà cung cấp mô hình trí tuệ nhân tạo (OpenAI).
* **Sự kiện kích hoạt:** Người dùng mở tab "Cấu hình AI & Khóa riêng" trong trang Cài đặt tài khoản.
* **Luồng chuẩn (Happy Path):**
  1. Màn hình hiển thị trạng thái hiện tại: "Đang sử dụng hạn mức mặc định của nền tảng".
  2. Người dùng nhập khóa cá nhân vào ô "Khóa OpenAI API cá nhân (BYOK)". Ký tự khóa tự động bị ẩn dưới dạng ký tự che chở `sk-...••••••••`.
  3. Người dùng bấm "Lưu & Xác thực khóa".
  4. Hệ thống thực hiện kiểm tra tính hợp lệ của khóa với máy chủ nhà cung cấp, mã hóa an toàn tuyệt đối cấp độ cao trước khi lưu trữ, và cập nhật trạng thái: "Đã kích hoạt khóa riêng thành công" kèm hiển thị 4 ký tự cuối (ví dụ: `sk-...4f8A`).
  5. Kể từ thời điểm này, mọi tác vụ hỏi đáp phân tích tài liệu và biên dịch học thuật trong phiên làm việc của người dùng sẽ ưu tiên sử dụng hạn mức từ khóa riêng này, hoàn toàn không phụ thuộc vào hạn ngạch chung của nền tảng.
* **Luồng ngoại lệ:**
  * *3a. Khóa API đúng cú pháp nhưng tài khoản cạn số dư (Insufficient Quota):* Hệ thống kết nối kiểm tra và cảnh báo ngay lập tức: "Khóa hợp lệ nhưng tài khoản của bạn tại nhà cung cấp AI đã hết số dư tín dụng hoặc chưa kích hoạt thanh toán. Vui lòng nạp tiền vào tài khoản nhà cung cấp."
  * *3b. Khóa API bị vô hiệu hóa hoặc thu hồi (Revoked / Invalid Key):* Hệ thống từ chối lưu và hiển thị thông báo: "Khóa không hợp lệ hoặc đã bị vô hiệu hóa bởi nhà cung cấp. Vui lòng kiểm tra lại trên bảng điều khiển của bạn."
  * *3c. Khóa sao chép dính khoảng trắng:* Hệ thống tự động cắt gọt khoảng trắng thừa trước khi gửi yêu cầu xác thực.
  * *3d. Mạng nội bộ trường viện chặn kết nối tới máy chủ AI bên ngoài:* Hệ thống thông báo lỗi đường truyền mạng và đề xuất học giả kiểm tra lại kết nối mạng hoặc thử lại trên đường truyền khác.
  * *3e. Học giả muốn gỡ bỏ khóa riêng:* Người dùng bấm nút "Gỡ khóa riêng", hệ thống xóa vĩnh viễn khóa khỏi máy chủ và hoàn trả tài khoản về sử dụng hạn ngạch tiêu chuẩn của nền tảng một cách mượt mà.
* **Hậu điều kiện:**
  * *Thành công:* Khóa cá nhân của học giả được mã hóa bảo mật toàn vẹn; trạng thái khóa hiển thị đã kích hoạt; các tác vụ phân tích học thuật tiếp theo sử dụng hạn ngạch riêng của học giả; khóa thô không bao giờ hiển thị lại trên giao diện.
  * *Thất bại:* Khóa lỗi bị hủy bỏ ngay khỏi bộ nhớ, không được lưu trữ dưới bất kỳ dạng nào; hệ thống giữ nguyên trạng thái sử dụng hạn ngạch nền tảng; thông báo lỗi chỉ dẫn đúng nguyên nhân kỹ thuật từ nhà cung cấp.

---

### UC-AUTH-06: Chuyển Đổi Chủ Đề Giao Diện Sáng / Tối
* **Tác nhân:** Mọi học giả đang tương tác trên giao diện.
* **Điều kiện tiên quyết:** Đang mở ứng dụng.
* **Sự kiện kích hoạt:** Bấm nút biểu tượng Mặt trời / Mặt trăng trên thanh công cụ hoặc chọn trong trang Cài đặt.
* **Luồng chuẩn (Happy Path):**
  1. Người dùng chọn 1 trong 3 tùy chọn: Sáng (Light), Tối (Dark), hoặc Theo hệ thống (System Default).
  2. Toàn bộ giao diện (thanh công cụ, bảng danh mục, khung đọc tài liệu, biểu đồ) chuyển đổi màu sắc mượt mà tức thì (< 50ms) mà không cần tải lại trang.
  3. Hệ thống lưu tùy chọn này vào hồ sơ học giả để đồng bộ tự động khi đăng nhập trên bất kỳ thiết bị nào khác.
* **Luồng ngoại lệ:**
  * *1a. Thiết bị công cộng ở thư viện chặn quyền lưu trữ trình duyệt:* Giao diện vẫn áp dụng chủ đề tức thì cho phiên đọc hiện tại và lưu vào hồ sơ tài khoản từ xa để đảm bảo lần đăng nhập sau trên thiết bị cá nhân vẫn đúng chủ đề mong muốn.
  * *1b. Hệ điều hành tự động đổi giao diện theo khung giờ hoàng hôn/bình minh:* Khi chọn chế độ "Theo hệ thống", giao diện tự động thích ứng đồng bộ theo thiết lập của máy tính người dùng mà không cần can thiệp thủ công.
* **Hậu điều kiện:**
  * *Thành công:* Toàn bộ bảng màu ứng dụng chuyển đổi sang tông màu tương ứng đạt độ tương phản chuẩn học thuật, chống mỏi mắt cho người đọc ban đêm; trạng thái cài đặt được đồng bộ vào hồ sơ học giả.
  * *Thất bại:* Giao diện duy trì chủ đề hiển thị mặc định thân thiện; không làm phát sinh lỗi hiển thị hoặc gián đoạn tài liệu đang đọc.

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

1. **Ràng Buộc Quyền Sở Hữu Toàn Vẹn Của Học Giả (Scholar Ownership Invariant):** Toàn bộ dữ liệu bài báo, phiên đọc, bản thảo và ghi chú đều là tài sản riêng của học giả sở hữu. Khi một học giả xóa tài khoản, toàn bộ dữ liệu thuộc sở hữu của họ phải bị xóa sạch vĩnh viễn khỏi hệ thống, không để lại dữ liệu mồ côi.
2. **Không Tiết Lộ Danh Tính Qua Thông Báo Lỗi (Anti-Enumeration Rule):** Mọi thông báo lỗi đăng nhập hoặc quên mật khẩu phải dùng câu chữ trung tính, không để lộ thông tin email đó có tồn tại trên hệ thống hay không.
3. **Bảo Mật Tuyệt Đối Khóa BYOK:** Khóa riêng tư của học giả chỉ được dùng để phục vụ các yêu cầu AI phát sinh từ chính tài khoản đó; hệ thống không bao giờ trả về nguyên vẹn khóa thô sau khi đã lưu, chỉ hiển thị ký tự che chở và 4 ký tự cuối cùng để nhận diện.
4. **Bảo Toàn Mạch Nghiên Cứu Không Gián Đoạn (Seamless Research Continuity):** Quá trình làm mới phiên làm việc phải diễn ra ngầm định hoàn toàn, tuyệt đối không làm đứt mạch đọc tài liệu, không làm mất ghi chú nháp hoặc gián đoạn luồng trao đổi học thuật đang diễn ra.
