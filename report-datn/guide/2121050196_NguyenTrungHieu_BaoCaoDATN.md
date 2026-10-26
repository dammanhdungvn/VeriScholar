**BỘ GIÁO DỤC VÀ ĐÀO TẠO TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT** 

**---------------------------------------** 

**NGUYỄN TRUNG HIẾU ĐỒ ÁN TỐT NGHIỆP** 

**NGÀNH CÔNG NGHỆ THÔNG TIN** 

**TÊN ĐỀ TÀI:** 

**XÂY DỰNG HỆ THỐNG QUẢN LÝ VÀ HỖ TRỢ ĐẶT LỊCH KHÁM CHỮA BỆNH TÍCH HỢP CHATBOT TƯ VẤN TẠI BỆNH VIỆN ĐA KHOA TRUNG ƯƠNG THÁI NGUYÊN** 

**Hà Nội - Năm 2025** 

**BỘ GIÁO DỤC VÀ ĐÀO TẠO TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT** 

**---------------------------------------** 

**ĐỒ ÁN TỐT NGHIỆP** 

**CHUYÊN NGÀNH: KHOA HỌC MÁY TÍNH** 

GIÁO VIÊN HƯỚNG DẪN                   SINH VIÊN THỰC HIỆN 

_(Chữ ký)                                                     (Chữ ký)_ 

**LÊ HỒNG ANH                       NGUYỄN TRUNG HIẾU** 

**Hà Nội – Năm 2025** 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **MỤC LỤC** 

|MỤC LỤC ............................................................................................................... i|
|---|
|DANH MỤC HÌNH ẢNH ................................................................................... vii|
|DANH MỤC BẢNG BIỂU ................................................................................... x|
|DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT .......................................... xii|
|LỜI CẢM ƠN ........................................................................................................ 1|
|LỜI MỞ ĐẦU ........................................................................................................ 2|
|CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI ............................................................. 3|
|1.1. Giới thiệu đề tài ........................................................................................... 3|
|1.2. Tính cấp thiết của đề tài ............................................................................... 4|
|1.3. Mục tiêu nghiên cứu .................................................................................... 4|
|1.4. Nội dung nghiên cứu.................................................................................... 5|
|1.5. Phạm vi nghiên cứu ..................................................................................... 5|
|1.6. Bố cục báo cáo đồ án tốt nghiệp .................................................................. 6|
|CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ....................................... 7|
|2.1. Tổng quan về MySQL và Xampp Apache .................................................. 7|
|2.1.1. Tổng quan về MySQL ........................................................................... 7|
|2.1.2. Tổng quan về Xampp Apache ............................................................... 8|
|2.2. Tổng quan về kiến trúc MVC ...................................................................... 8|
|2.3. Ngôn ngữ lập trình PHP .............................................................................. 9|
|2.4. Tổng quan về Laravel Framework ............................................................. 10|
|2.4.1. Laravel Framework là gì?.................................................................... 10|
|2.4.2. Kiến trúc của một thư mục Laravel ..................................................... 11|
|2.5. Tìm hiểu về HTML, CSS, JavaScript và Bootstrap .................................. 12|
|2.5.1. HTML là gì ? (Hypertext Markup Language) ..................................... 12|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_i_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|2.5.2. CSS là gì ? (Cascading Style Sheets) .................................................. 13|
|---|
|2.5.3. Javascript là gì? ................................................................................... 14|
|2.5.4. Bootstrap là gì? .................................................................................... 14|
|2.6. Tìm hiểu về các công nghệ xử lý văn bản tự nhiên ................................... 15|
|2.6.1. Tổng quan về Regex ............................................................................ 16|
|2.6.2. Tổng quan về NLP .............................................................................. 16|
|2.7. Tổng quan về PHPUnit .............................................................................. 18|
|2.8. Tổng quan về Docker ................................................................................. 19|
|2.9. Tìm hiểu về các công cụ hỗ trợ trực quan hóa dữ liệu với Python và Jupyter|
|Notebook ........................................................................................................... 20|
|2.9.1. Tìm hiểu về các công cụ trực quan hóa dữ liệu với Python ................ 20|
|2.9.2. Tìm hiểu về Jupyter Notebook ............................................................ 22|
|CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG ................................... 23|
|3.1. Mô tả bài toán ............................................................................................ 23|
|3.2. Khảo sát nghiệp vụ, quy trình và tổ chức khám chữa bệnh tại bệnh viện Đa|
|khoa Trung Ương Thái Nguyên ........................................................................ 24|
|3.2.1. Khảo sát quy trình đăng ký khám chữa bệnh tại bệnh viện ................ 24|
|3.2.2. Khảo sát cơ cấu tổ chức các khoa khám chữa bệnh và dịch vụ khám|
|bệnh tại bệnh viện Đa khoa Trung Ương Thái Nguyên ................................ 25|
|3.2.3. Khảo sát quy trình khám chữa bệnh của bác sĩ ................................... 28|
|3.2.4. Khảo sát quy trình quản lý hồ sơ thông tin bệnh nhân tại bệnh viện .. 29|
|3.2.5. Khảo sát quy trình quản lý bác sĩ tại bệnh viện .................................. 30|
|3.3. Giới thiệu các tác nhân và các ca sử dụng tương ứng đối với từng tác nhân|
|trong hệ thống ................................................................................................... 31|
|3.4. Phân tích các ca sử dụng của hệ thống ...................................................... 33|
|3.4.1. Phân tích các ca sử dụng phía quản trị viên ........................................ 35|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_ii_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|3.4.1.1. Phân tích ca sử dụng “Quản lý thống kê” ..................................... 35|
|---|
|3.4.1.2. Phân tích ca sử dụng “Quản lý khoa khám bệnh” ........................ 37|
|3.4.1.3. Phân tích ca sử dụng “Quản lý dịch vụ khám chữa bệnh” ........... 39|
|3.4.1.4. Phân tích ca sử dụng “Quản lý bác sĩ” .......................................... 41|
|3.4.1.5. Phân tích ca sử dụng “Quản lý bệnh nhân” .................................. 43|
|3.4.1.6. Phân tích ca sử dụng “Quản lý lịch khám chữa bệnh” ................. 46|
|3.4.1.7. Phân tích ca sử dụng “Quản lý lịch làm việc” .............................. 49|
|3.4.1.8. Phân tích ca sử dụng “Quản lý tin tức” ......................................... 51|
|3.4.1.9. Phân tích ca sử dụng “Quản lý vai trò người dùng” ..................... 52|
|3.4.2. Phân tích các ca sử dụng phía bệnh nhân ............................................ 53|
|3.4.2.1. Phân tích ca sử dụng “Sử dụng Chatbot tư vấn” .......................... 53|
|3.4.2.2. Phân tích ca sử dụng “Xem khoa khám bệnh” ............................. 56|
|3.4.2.3. Phân tích ca sử dụng “Xem dịch vụ khám chữa bệnh”................. 57|
|3.4.2.4. Phân tích ca sử dụng “Tìm kiếm nhanh bác sĩ” ............................ 58|
|3.4.2.5. Phân tích ca sử dụng “Đặt lịch khám chữa bệnh” ........................ 59|
|3.4.2.6. Phân tích ca sử dụng “Theo dõi lịch khám chữa bệnh” ................ 61|
|3.4.3. Phân tích các ca sử dụng phía bác sĩ ................................................... 62|
|3.4.3.1. Phân tích ca sử dụng “Quản lý bệnh nhân” .................................. 62|
|3.4.3.2. Phân tích ca sử dụng “Quản lý lịch khám chữa bệnh” ................. 63|
|3.4.3.3. Phân tích ca sử dụng “Quản lý lịch làm việc” .............................. 63|
|3.4.3.4. Phân tích ca sử dụng “Quản lý tài khoản” .................................... 64|
|3.5. Phân tích một số biểu đồ tuần tự chính của hệ thống ................................ 64|
|3.5.1. Biểu đồ tuần tự cho ca sử dụng “Đăng ký tài khoản” ......................... 65|
|3.5.2. Biểu đồ tuần tự cho ca sử dụng “Đăng nhập” ..................................... 66|
|3.5.3. Biểu đồ tuần tự cho ca sử dụng “Sử dụng chatbot tư vấn” ................. 67|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_iii_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|3.5.4. Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm nhanh bác sĩ” (phía trang|
|---|
|người dùng) ................................................................................................... 68|
|3.5.5. Biểu đồ tuần tự cho ca sử dụng “Đặt lịch khám chữa bệnh” .............. 69|
|3.5.6. Biểu đồ tuần tự cho ca sử dụng “Đăng ký lịch làm việc” của bác sĩ .. 70|
|3.5.7. Biểu đồ tuần tự cho ca sử dụng “Cập nhật trạng thái lịch khám chữa|
|bệnh”.............................................................................................................. 71|
|3.5.8. Biểu đồ tuần tự cho ca sử dụng “Thêm mới khoa khám bệnh” .......... 72|
|3.5.9. Biểu đồ tuần tự cho ca sử dụng “Thêm mới bác sĩ” ............................ 72|
|3.5.10. Biểu đồ tuần tự cho ca sử dụng “Cập nhật thông tin bệnh nhân” ..... 73|
|3.5.11. Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm bệnh nhân” ................... 74|
|3.5.12. Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm lịch khám bệnh” ........... 75|
|3.5.13. Biểu đồ tuần tự cho ca sử dụng “Xuất báo cáo thống kê bệnh nhân” 76|
|3.6. Phân tích thiết kế Chatbot tư vấn bệnh nhân ............................................. 76|
|3.6.1. Mục tiêu xây dựng Chatbot tư vấn ...................................................... 76|
|3.6.2. Các chức năng chính của Chatbot tư vấn ............................................ 77|
|3.6.3. Kiến trúc của Chatbot .......................................................................... 77|
|3.7. Xây dựng biểu đồ lớp ................................................................................ 79|
|3.7.1. Xây dựng biểu đồ lớp nhóm 1 – Quản lý người dùng và phân quyền 79|
|3.7.2. Xây dựng biểu đồ lớp cho nhóm 2 – Quản lý lịch khám chữa bệnh ... 81|
|3.7.3. Xây dựng biểu đồ lớp cho nhóm 3 – Chatbot tư vấn bệnh nhân ......... 84|
|3.7.4. Xây dựng biểu đồ lớp cho nhóm 4 – Tương tác và phản hồi .............. 85|
|3.8. Thiết kế cơ sở dữ liệu cho hệ thống ........................................................... 87|
|3.8.1. Thiết kế cơ sở dữ liệu của hệ thống..................................................... 87|
|3.8.2. Đặc tả một số bảng cơ sở dữ liệu của hệ thống ................................... 88|
|3.9. Xây dựng biểu đồ thành phần .................................................................... 92|
|3.10. Xây dựng biểu đồ triển khai .................................................................... 93|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_iv_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|CHƯƠNG 4: THỰC NGHIỆM ........................................................................... 95|
|---|
|4.1. Môi trường thực nghiệm ............................................................................ 95|
|4.1.1. Cài đặt Visual Studio Code ................................................................. 95|
|4.1.2. Cài đặt Xampp Version 7.4.16 ............................................................ 95|
|4.1.3. Triển khai thực nghiệm hệ thống tại Bệnh viện Đa khoa Trung Ương|
|Thái Nguyên .................................................................................................. 96|
|4.2. Kết quả thực nghiệm .................................................................................. 97|
|4.2.1. Một số giao diện của hệ thống ............................................................ 97|
|4.2.1.1. Giao diện đăng ký khám bệnh của bệnh nhân .............................. 97|
|4.2.1.2. Giao diện đăng nhập ..................................................................... 98|
|4.2.1.3. Giao diện Chatbot tư vấn .............................................................. 98|
|4.2.1.4. Giao diện tìm kiếm nhanh bác sĩ................................................... 99|
|4.2.1.5. Giao diện thông tin các khoa khám bệnh ...................................... 99|
|4.2.1.6. Giao diện thông tin các dịch vụ khám bệnh ................................ 100|
|4.2.1.7. Giao diện thông tin bác sĩ ........................................................... 100|
|4.2.1.8. Giao diện đặt lịch khám chữa bệnh ............................................. 100|
|4.2.1.9. Giao diện theo dõi lịch khám chữa bệnh .................................... 101|
|4.2.1.10. Giao diện quản trị viên .............................................................. 103|
|4.2.1.11. Giao diện quản lý khoa khám bệnh .......................................... 103|
|4.2.1.12. Giao diện quản lý bác sĩ ............................................................ 104|
|4.2.1.13. Giao diện quản lý lịch khám chữa bệnh .................................... 104|
|4.2.1.14. Giao diện quản lý và đăng ký lịch làm việc cho bác sĩ ............. 105|
|4.2.1.15. Giao diện xuất báo cáo thống kê bệnh nhân ............................. 105|
|4.2.1.16. Giao diện quản lý bệnh nhân .................................................... 106|
|4.2.1.17. Giao diện quản lý dịch vụ khám chữa bệnh .............................. 107|
|4.2.2. Xây dựng các ca kiểm thử tự động hệ thống với PHPUnit ............... 107|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_v_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|4.2.3. Kết quả thực nghiệm hệ thống tại Bệnh viện Đa khoa Trung Ương Thái|
|---|
|Nguyên ........................................................................................................ 110|
|KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN ......................................................... 115|
|TÀI LIỆU THAM KHẢO .................................................................................. 116|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_vi_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **DANH MỤC HÌNH ẢNH** 

|**Hình 1-1:**Tình trạng quá tải ở các bệnh viện ........................................................ 3|
|---|
|**Hình 2-1:**MySQL ................................................................................................. 7|
|**Hình 2-2:**XamPP .................................................................................................. 8|
|**Hình 2-3:**Kiến trúc MVC ..................................................................................... 9|
|**Hình 2-4:**Luồng xử lý mô hình MVC .................................................................. 9|
|**Hình 2-5:**Ngôn ngữ lập trình PHP...................................................................... 10|
|**Hình 2-6:**Các đặc trưng của Laravel .................................................................. 11|
|**Hình 2-7:**HTML ................................................................................................. 13|
|**Hình 2-8:**CSS ..................................................................................................... 13|
|**Hình 2-9:**Javascript ............................................................................................ 14|
|**Hình 2-10:**Bootstrap ........................................................................................... 15|
|**Hình 2-11:**Mô tả về Regex ................................................................................. 16|
|**Hình 2-12:**Kiến trúc căn bản của NLP ............................................................... 17|
|**Hình 2-13:**PHPUnit ............................................................................................ 18|
|**Hình 2-14:**Kiến trúc tổng quan của Docker ....................................................... 19|
|**Hình 2-15:**Giới thiệu về Seaborn ....................................................................... 21|
|**Hình 2-16:**Giới thiệu về Matplotlib ................................................................... 21|
|**Hình 2-17:**Giới thiệu về Jupyter Notebook ........................................................ 22|
|**Hình 3-1:**Biểu đồ ca sử dụng tổng quan của hệ thống ....................................... 34|
|**Hình 3-2:**Biểu đồ ca sử dụng “Quản lý thống kê” ............................................. 35|
|**Hình 3-3:**Biểu đồ ca sử dụng“Quản lý khoa khám bệnh” .................................. 37|
|**Hình 3-4:**Biểu đồ ca sử dụng “Quản lý dịch vụ khám chữa bệnh” .................... 39|
|**Hình 3-5:**Biểu đồ ca sử dụng “Quản lý bác sĩ” .................................................. 41|
|**Hình 3-6:**Biểu đồ ca sử dụng “Quản lý bệnh nhân” ........................................... 43|
|**Hình 3-7:**Biểu đồ ca sử dụng “Quản lý lịch khám chữa bệnh” .......................... 46|
|**Hình 3-8:**Biểu đồ ca sử dụng “Quản lý lịch làm việc” ...................................... 49|
|**Hình 3-9:**Biểu đồ ca sử dụng “Quản lý tin tức” ................................................. 51|
|**Hình 3-10:**Biểu đồ ca sử dụng “Quản lý vai trò người dùng” ........................... 52|
|**Hình 3-11:**Biểu đồ ca sử dụng “Sử dụng Chatbot tư vấn” ................................. 53|
|**Hình 3-12:**Biểu đồ ca sử dụng “Xem khoa khám bệnh” .................................... 56|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_vii_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|**Hình 3-13:**Biểu đồ ca sử dụng “Xem dịch vụ khám chữa bệnh” ....................... 57|
|---|
|**Hình 3-14:**Biểu đồ ca sử dụng “Tìm kiếm nhanh bác sĩ khám chữa bệnh” ....... 58|
|**Hình 3-15:**Biểu đồ ca sử dụng“Đặt lịch khám chữa bệnh” ................................ 59|
|**Hình 3-16:**Biểu đồ ca sử dụng “Theo dõi lịch khám chữa bệnh” ...................... 61|
|**Hình 3-17:**Biểu đồ ca sử dụng “Quản lý bệnh nhân”(phía bác sĩ) ..................... 62|
|**Hình 3-18:**Biểu đồ ca sử dụng “Quản lý lịch khám chữa bệnh”(Phía bác sĩ) .... 63|
|**Hình 3-19:**Biểu đồ ca sử dụng “Quản lý lịch làm việc”(Phía bác sĩ) ................ 63|
|**Hình 3-20:**Biểu đồ ca sử dụng “Quản lý tài khoản”(Phía bác sĩ) ...................... 64|
|**Hình 3-21:**Biểu đồ tuần tự cho ca sử dụng “Đăng ký tài khoản” ...................... 65|
|**Hình 3-22:**Biểu đồ tuần tự cho ca sử dụng “Đăng nhập”................................... 66|
|**Hình 3-23:**Biểu đồ tuần tự  cho ca sử dụng “Sử dụng Chatbot tư vấn” ............. 67|
|**Hình 3-24:**Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm nhanh bác sĩ” (phía trang|
|người dùng) .......................................................................................................... 68|
|**Hình 3-25:**Biểu đồ tuần tự cho ca sử dụng “Đặt lịch khám chữa bệnh” ............ 69|
|**Hình 3-26:**Biểu đồ tuần tự cho ca sử dụng “Đăng ký lịch làm việc” của bác sĩ 70|
|**Hình 3-27:**Biểu đồ tuần tự cho ca sử dụng “Cập nhật trạng thái lịch khám chữa|
|bệnh” .................................................................................................................... 71|
|**Hình 3-28:**Biểu đồ tuần tự cho ca sử dụng “Thêm mới khoa khám bệnh” ........ 72|
|**Hình 3-29:**Biểu đồ tuần tự cho ca sử dụng “Thêm mới bác sĩ” ......................... 72|
|**Hình 3-30:**Biểu đồ tuần tự cho ca sử dụng “Cập nhật thông tin bệnh nhân” ..... 73|
|**Hình 3-31:**Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm bệnh nhân” ................... 74|
|**Hình 3-32:**Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm lịch khám chữa bệnh” .. 75|
|**Hình 3-33:**Biểu đồ tuần tự cho ca sử dụng “Xuất báo cáo thống kê bệnh nhân|
|khám chữa bệnh” .................................................................................................. 76|
|**Hình 3-34:**Kiến trúc Chatbot tư vấn bệnh nhân ................................................. 78|
|**Hình 3-35:**Biểu đồ lớp nhóm 1 – Quản lý người dùng và phân quyền .............. 80|
|**Hình 3-36:**Biểu đồ lớp cho nhóm 2 – Quản lý lịch khám chữa bệnh ................ 82|
|**Hình 3-37:**Biểu đồ lớp cho nhóm 3 – Chatbot tư vấn bệnh nhân ...................... 85|
|**Hình 3-38:**Biểu đồ lớp cho nhóm 4 – Tương tác và phản hồi............................ 86|
|**Hình 3-39:**Mối quan hệ giữa các bảng trong hệ quản trị cơ sở dữ liệu .............. 92|
|**Hình 3-40:**Biểu đồ thành phần của hệ thống ...................................................... 92|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_viii_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|**Hình 3-41:**Biểu đồ triển khai của hệ thống ........................................................ 93|
|---|
|**Hình 4-1:**Giao diện đăng kí tài khoản của hệ thống........................................... 97|
|**Hình 4-2:**Giao diện đăng nhập của hệ thống ...................................................... 98|
|**Hình 4-3:**Giao diện Chatbot tư vấn bệnh nhân .................................................. 98|
|**Hình 4-4:**Form tìm kiếm nhanh bác sĩ ............................................................... 99|
|**Hình 4-5:**Danh sách các khoa khám bệnh .......................................................... 99|
|**Hình 4-6:**Danh sách dịch vụ khám chữa bệnh ................................................. 100|
|**Hình 4-7:**Giao diện thông tin và lịch làm việc của bác sĩ ................................ 100|
|**Hình 4-8:**Giao diện đặt lịch khám chữa bệnh .................................................. 101|
|**Hình 4-9:**Hiển thị đặt lịch khám thành công .................................................... 101|
|**Hình 4-10:**Giao diện theo dõi lịch khám chữa bệnh của bệnh nhân ................ 102|
|**Hình 4-11:**Tiến độ lịch khám chữa bệnh được gửi về Email của bệnh nhân ... 102|
|**Hình 4-12:**Giao diện quản trị viên hệ thống ..................................................... 103|
|**Hình 4-13:**Giao diện quản lý khoa khám bệnh ................................................ 103|
|**Hình 4-14:**Giao diện quản lý bác sĩ .................................................................. 104|
|**Hình 4-15:**Giao diện thêm mới bác sĩ .............................................................. 104|
|**Hình 4-16:**Giao diện quản lý lịch khám chữa bệnh ......................................... 105|
|**Hình 4-17:**Giao diện quản lý và đăng ký lịch làm việc cho bác sĩ .................. 105|
|**Hình 4-18:**Giao diện xuất báo cáo thống kê bệnh nhân ................................... 106|
|**Hình 4-19:**Giao diện quản lý bệnh nhân .......................................................... 106|
|**Hình 4-20:**Giao diện cập nhật thông tin bệnh nhân ......................................... 107|
|**Hình 4-21:**Giao diện quản lý dịch vụ khám chữa bệnh ................................... 107|
|**Hình 4-22:**Trực quan hóa kết quả khảo sát mức độ sử dụng và đánh giá hệ thống|
|của bệnh nhân ..................................................................................................... 112|
|**Hình 4-23:**Trực quan hóa kết quả khảo sát mức độ hài lòng của các bác sĩ và y tá|
|khi sử dụng hệ thống quản lý ............................................................................. 114|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_ix_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **DANH MỤC BẢNG BIỂU** 

|**Bảng 3-1:**Danh sách khoa khám bệnh và dịch vụ tương ứng tại bệnh viện ....... 26|
|---|
|**Bảng 3-2:**Các ca sử dụng chính đối với mỗi tác nhân ........................................ 32|
|**Bảng 3-3:**Bảng đặc tả ca sử dụng “Quản lý thống kê” ....................................... 35|
|**Bảng 3-4:**Đặc tả ca sử dụng “Xuất báo cáo thống kê bệnh nhân” ..................... 36|
|**Bảng 3-5:**Đặc tả ca sử dụng “Quản lý khoa khám bệnh” ................................... 37|
|**Bảng 3-6:**Đặc tả ca sử dụng “Cập nhật khoa khám bệnh” ................................. 38|
|**Bảng 3-7:**Đặc tả ca sử dụng “Quản lý dịch vụ khám chữa bệnh” ...................... 39|
|**Bảng 3-8:**Đặc tả ca sử dụng “Thêm mới dịch vụ khám chữa bệnh” .................. 40|
|**Bảng 3-9:**Đặc tả ca sử dụng “Tìm kiếm dịch vụ khám chữa bệnh” ................... 40|
|**Bảng 3-10:**Đặc tả ca sử dụng “Quản lý bác sĩ” .................................................. 41|
|**Bảng 3-11:**Đặc tả ca sử dụng “Thêm mới bác sĩ” .............................................. 42|
|**Bảng 3-12:**Đặc tả ca sử dụng “Tìm kiếm bác sĩ” ............................................... 42|
|**Bảng 3-13:**Bảng đặc tả ca sử dụng “Quản lý bệnh nhân” .................................. 44|
|**Bảng 3-14:**Đặc tả ca sử dụng “Thêm mới bệnh nhân” ....................................... 44|
|**Bảng 3-15:**Đặc tả ca sử dụng “Tìm kiếm bệnh nhân” ........................................ 45|
|**Bảng 3-16:**Đặc tả ca sử dụng “Quản lý lịch khám chữa bệnh” .......................... 46|
|**Bảng 3-17:**Đặc tả ca sử dụng “Xem danh sách lịch khám chữa bệnh” .............. 47|
|**Bảng 3-18:**Đặc tả ca sử dụng “Tìm kiếm lịch khám chữa bệnh” ....................... 47|
|**Bảng 3-19:**Đặc tả ca sử dụng “Cập nhật trạng thái lịch khám bệnh” ................. 48|
|**Bảng 3-20:**Đặc tả ca sử dụng “Quản lý lịch làm việc” ...................................... 49|
|**Bảng 3-21:**Đặc tả ca sử dụng “Xem danh sách lịch làm việc” ........................... 50|
|**Bảng 3-22:**Đặc tả ca sử dụng “Tìm kiếm lịch làm việc” .................................... 50|
|**Bảng 3-23:**Đặc tả ca sử dụng “Quản lý tin tức” ................................................. 51|
|**Bảng 3-24:**Đặc tả ca sử dụng “Quản lý vai trò người dùng” ............................. 52|
|**Bảng 3-25:**Đặc tả ca sử dụng “Sử dụng Chatbot tư vấn” ................................... 53|
|**Bảng 3-26:**Đặc tả ca sử dụng “Tìm lịch khám còn trống theo bác sĩ” ............... 54|
|**Bảng 3-27:**Đặc tả ca sử dụng “Tìm kiếm lịch khám còn trống theo dịch vụ khám|
|bệnh” .................................................................................................................... 55|
|**Bảng 3-28:**Đặc tả ca sử dụng “Tra cứu giá tiền khám bệnh của bác sĩ” ............ 55|
|**Bảng 3-29:**Đặc tả ca sử dụng “Xem khoa khám bệnh” ...................................... 56|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_x_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|**Bảng 3-30:**Đặc tả ca sử dụng “Xem dịch vụ khám chữa bệnh” ......................... 57|
|---|
|**Bảng 3-31:**Đặc tả ca sử dụng “Tìm kiếm nhanh bác sĩ khám chữa bệnh” ......... 59|
|**Bảng 3-32:**Đặc tả ca sử dụng “Đặt lịch khám chữa bệnh” ................................. 60|
|**Bảng 3-33:**Đặc tả ca sử dụng “Theo dõi lịch khám chữa bệnh” ........................ 61|
|**Bảng 3-34:**Bảng phân tích biểu đồ lớp cho nhóm 1 – Quản lý người dùng và phân|
|quyền người dùng ................................................................................................. 80|
|**Bảng 3-35:**Bảng phân tích biểu đồ lớp cho nhóm 2 – Quản lý lịch khám chữa|
|bệnh ...................................................................................................................... 83|
|**Bảng 3-36:**Bảng phân tích biểu đồ lớp nhóm 3 – Chatbot tư vấn bệnh nhân .... 85|
|**Bảng 3-37:**Bảng phân tích biểu đồ lớp cho nhóm 4 – Tương tác và phản hồi ... 87|
|**Bảng 3-38:**Các bảng cơ sở dữ liệu của hệ thống ................................................ 88|
|**Bảng 3-39:**Bảng Users ........................................................................................ 88|
|**Bảng 3-40:**Bảng Bookings ................................................................................. 89|
|**Bảng 3-41:**Bảng Specialties ............................................................................... 90|
|**Bảng 3-42:**Bảng Clinics ..................................................................................... 91|
|**Bảng 3-43:**Bảng Bot_knowledge ....................................................................... 91|
|**Bảng 4-2:**Bảng liệt kê các TC kiểm thử tự động hệ thống với PHPUnit ......... 108|
|**Bảng 4-3:**Bảng kết quả khảo sát mức độ sử dụng và đánh giá hệ thống đặt lịch|
|khám của bệnh nhân ........................................................................................... 111|
|**Bảng 4-4:**Bảng kết quả khảo sát mức độ hài lòng của các bác sĩ và y tá khi sử|
|dụng hệ thống ..................................................................................................... 113|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_xi_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT** 

|**STT**|**Ký hiệu / viết tắt**|**Ý nghĩa**|
|---|---|---|
|1|NLP|Natural Language Processing – Xử lý<br>ngôn ngữ tự nhiên|
|2|Regex|Regular Expression – Biểu thức chính<br>quy|
|3|MVC|Kiến trúc phần mềm MVC mà Laravel<br>framework sử dụng|
|4|HTTP|Hypertext Transfer Protocol|
|5|AI|Artificial Intelligence – Trí tuệ nhân<br>tạo|
|6|Client|Bệnh nhân (luồng Chatbot)|
|7|NLU|Natural Language Understanding – lớp<br>hiểu ý định và thực thể (luồng Chatbot)|
|8|Controller & Service|Lớp điều khiển nghiệp vụ (luồng<br>Chatbot)|
|9|Database & Search<br>Engine|Lớp dữ liệu và tìm kiếm dữ liệu (luồng<br>Chatbot)|
|10|Response Builder|Lớp phản hồi (luồng Chatbot)|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_xii_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **LỜI CẢM ƠN** 

Em xin gửi lời cảm ơn thầy PGS.TS Lê Hồng Anh – Trưởng khoa Công nghệ Thông tin, Trưởng bộ môn Khoa học Máy tính, Trường Đại học Mỏ - Địa chất, người đã trực tiếp hướng dẫn và định hướng em trong suốt quá trình thực hiện đề tài đồ án tốt nghiệp. Những đóng góp quý báu của thầy về mặt học thuật, phương pháp nghiên cứu  và xây dựng sản phẩm đồ án tốt nghiệp đã giúp em tiếp cận đề tài một cách logic, khoa học và hiệu quả hơn, đồng thời xây dựng được một hệ thống mang tính ứng dụng thực tiễn và gắn liền với quy trình nghiệp vụ tại bệnh viện Đa khoa Trung ương Thái Nguyên. 

Em cũng xin gửi lời cảm ơn chân thành tới các thầy cô trong bộ môn Khoa học Máy tính, khoa Công nghệ Thông tin cũng đã giúp đỡ em trong quá trình lên ý tưởng, phân tích thiết kế hệ thống,  hoàn thiện sản phẩm và báo cáo đồ án tốt nghiệp. 

Và cuối cùng, em xin cảm ơn các bác sĩ, y tá, điều dưỡng và bệnh nhân tại bệnh viện Đa khoa Trung Ương Thái Nguyên đã góp công rất lớn đối với em trong quá trình khảo sát quy trình nghiệp vụ khám và đăng kí chữa bệnh. Đồng thời hỗ trợ em trong quá trình triển khai thực nghiệm hệ thống và lấy ý kiến phản hồi bệnh nhân tại bệnh viện. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_1_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **LỜI MỞ ĐẦU** 

Trong bối cảnh cách mạng công nghiệp 4.0, công nghệ thông tin đã và đang đóng vai trò quan trọng trong việc chuyển đổi số các lĩnh vực kinh tế - xã hội, đặc biệt là ngành y tế. Y tế là một trong những lĩnh vực nhạy cảm và đòi hỏi tính chính xác cao, nơi mà sự hỗ trợ kịp thời và hiệu quả có thể cứu sống hàng triệu bệnh nhân. Tại Việt Nam, hệ thống y tế đang đối mặt với nhiều thách thức lớn, nổi bật là tình trạng quá tải tại các bệnh viện lớn, đặc biệt ở các tỉnh miền núi và trung du như Thái Nguyên. Bệnh viện Đa khoa Trung ương Thái Nguyên, một trong những cơ sở y tế hàng đầu khu vực Đông Bắc, hàng ngày tiếp nhận hàng nghìn lượt bệnh nhân, dẫn đến tình trạng chen chúc, chờ đợi kéo dài và khó khăn trong việc đặt lịch khám chữa bệnh. Những vấn đề này không chỉ ảnh hưởng đến chất lượng dịch vụ y tế mà còn làm giảm sự hài lòng của người dân, đồng thời tăng áp lực lên đội ngũ y bác sĩ. 

Trước thực trạng đó, việc ứng dụng công nghệ thông tin để xây dựng các hệ thống quản lý thông minh trở thành giải pháp cấp thiết. Hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot tư vấn là một hướng tiếp cận hiện đại, kết hợp giữa quản lý dữ liệu truyền thống và trí tuệ nhân tạo (AI). Chatbot không chỉ hỗ trợ tư vấn sơ bộ, trả lời thắc mắc mà còn giúp tối ưu hóa quy trình đặt lịch, giảm thiểu tình trạng bỏ lỡ lịch khám và nâng cao trải nghiệm người dùng. Đề tài "Xây dựng hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot tư vấn tại Bệnh viện Đa khoa Trung ương Thái Nguyên" được thực hiện nhằm giải quyết những vấn đề trên, góp phần thúc đẩy chuyển đổi số trong ngành y tế địa phương. Mục tiêu chính của đề tài là thiết kế và triển khai một hệ thống web-based toàn diện, bao gồm các chức năng quản lý lịch khám, hỗ trợ đặt lịch trực tuyến và tích hợp chatbot dựa trên AI để tư vấn y tế cơ bản. Hệ thống sẽ phục vụ ba nhóm người dùng chính: bệnh nhân (người dùng cuối), quản trị viên (quản lý bệnh viện, nhân viên bệnh viện) và bác sĩ. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_2_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI** 

## **1.1. Giới thiệu đề tài** 

Trong bối cảnh chuyển đổi số diễn ra mạnh mẽ trên toàn cầu, ngành y tế đang chứng kiến những bước tiến vượt bậc nhờ ứng dụng công nghệ thông tin. Tại Việt Nam, các bệnh viện lớn, đặc biệt là những cơ sở y tế tuyến trung ương như Bệnh viện Đa khoa Trung ương Thái Nguyên, thường xuyên đối mặt với tình trạng quá tải do lượng bệnh nhân đông đảo. Quy trình đặt lịch khám chữa bệnh truyền thống, chủ yếu dựa vào đăng ký trực tiếp hoặc qua điện thoại, gây ra nhiều bất tiện như thời gian chờ đợi lâu, nhầm lẫn lịch hẹn và khó khăn trong việc quản lý thông tin bệnh nhân. Bên cạnh đó, nhu cầu tư vấn y tế ban đầu của người dân ngày càng tăng, đặc biệt trong bối cảnh hậu đại dịch COVID-19, khi các dịch vụ y tế trực tuyến trở nên phổ biến. 



<!-- Start of picture text -->
eee Os<br>eryde® . iA eee‘ye .<br>a er Bey |<br><!-- End of picture text -->

**Hình 1-1:** _Tình trạng quá tải ở các bệnh viện_ 

Đề tài “Xây dựng hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot tư vấn tại Bệnh viện Đa khoa Trung ương Thái Nguyên” được thực hiện nhằm giải quyết các vấn đề trên. Hệ thống được thiết kế để cung cấp một nền tảng trực tuyến cho phép người dùng đặt lịch khám dễ dàng, quản trị viên quản lý lịch hẹn hiệu quả, bác sĩ theo dõi lịch trình công việc và tích hợp một chatbot thông minh để hỗ trợ tư vấn y tế cơ bản. Đề tài kết hợp các công nghệ hiện đại như lập trình web, cơ sở dữ liệu và trí tuệ nhân tạo (AI) để xây dựng một giải pháp toàn diện, đáp ứng nhu cầu thực tế tại bệnh viện. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_3_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **1.2. Tính cấp thiết của đề tài** 

Bệnh viện Đa khoa Trung ương Thái Nguyên là một trong những cơ sở y tế lớn nhất khu vực Đông Bắc Việt Nam, phục vụ hàng nghìn lượt bệnh nhân mỗi ngày. Tuy nhiên, quy trình quản lý lịch khám thủ công hiện tại dẫn đến nhiều vấn đề như: thời gian chờ đợi lâu, sai sót trong việc sắp xếp lịch hẹn, và thiếu kênh tư vấn nhanh chóng cho bệnh nhân. Những hạn chế này không chỉ làm giảm trải nghiệm của bệnh nhân mà còn gây áp lực lớn lên đội ngũ y bác sĩ và nhân viên hành chính. 

Đặc biệt, nhu cầu đăng ký khám bệnh với bác sĩ cụ thể, chẳng hạn như bác sĩ mà bệnh nhân khám dịch vụ cụ thể mà bệnh nhân mong muốn, bác sĩ có học hàm giáo sư hoặc phó giáo sư, đang ngày càng tăng. Các hệ thống đặt lịch khám đã tồn tại thường không đáp ứng được yêu cầu này, khiến bệnh nhân gặp khó khăn trong việc lựa chọn bác sĩ phù hợp với nhu cầu cá nhân. Những hạn chế này không chỉ làm giảm trải nghiệm của bệnh nhân mà còn gây áp lực lớn lên đội ngũ y bác sĩ và nhân viên hành chính. 

Việc ứng dụng công nghệ thông tin để xây dựng một hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot là một giải pháp cấp thiết. Bệnh nhân có thể nhanh chóng tìm kiếm bác sĩ khám phù hợp với nhu cầu của mình. Ngoài ra, Chatbot có thể trả lời các câu hỏi thường gặp, hướng dẫn quy trình đặt lịch và cung cấp thông tin y tế cơ bản, giúp giảm tải cho nhân viên bệnh viện. Hơn nữa, trong bối cảnh chuyển đổi số y tế đang được Chính phủ Việt Nam thúc đẩy, việc triển khai một hệ thống như vậy tại Bệnh viện Đa khoa Trung ương Thái Nguyên không chỉ cải thiện hiệu quả hoạt động mà còn tạo tiền đề để nhân rộng mô hình cho các cơ sở y tế khác. 

## **1.3. Mục tiêu nghiên cứu** 

- Xây dựng một hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh trực tuyến, đáp ứng nhu cầu quản lý và đặt lịch khám online cho ba nhóm người dùng chính: bệnh nhân, quản trị viên và bác sĩ, bám sát nghiệp vụ quản lý và khám chữa bệnh tại bệnh viện Đa khoa Trung Ương Thái Nguyên. 

- Tích hợp chatbot tư vấn sử dụng công nghệ AI để hỗ trợ giải đáp thắc mắc, 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_4_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

cung cấp thông tin y tế cơ bản, hướng dẫn đặt lịch khám và tra cứu nhanh lịch khám còn trống, giá khám của dịch vụ khám chữa bệnh, bác sĩ, tra cứu và theo dõi thông tin lịch khám, tiến độ lịch khám. 

- Đẩy hệ thống lên domain với tên miền cụ thể, tiến hành xây dựng các ca kiểm thử tự động cho chức năng hệ thống, ứng dụng Docker để vận hành hệ thống. 

- Thực nghiệm hệ thống tại Bệnh viện Đa khoa Trung ương Thái Nguyên, tiến hành cho bệnh nhân và bác sĩ trải nghiệm sử dụng hệ thống, thu thập phản hồi từ người dùng để đánh giá hiệu quả và cải tiến. 

- Đảm bảo hệ thống hoạt động ổn định, dễ sử dụng, và có khả năng mở rộng để áp dụng tại các cơ sở y tế khác. 

## **1.4. Nội dung nghiên cứu** 

- Khảo sát và phân tích thực trạng quy trình nghiệp vụ và quản lý, tổ chức khám chữa bệnh tại bệnh viện đa khoa Trung Ương Thái Nguyên. 

- Nghiên cứu các công nghệ được sử dụng trong quá trình phát triển hệ thống, công nghệ lập trình web, quản lý cơ sở dữ liệu, công nghệ xử lý luồng dữ liệu đối với Chatbot, kiểm thử thử tự động hệ thống, vận hành hệ thống. 

- Phân tích và thiết kế hệ thống với các biểu đồ UML, xây dựng các biểu đồ Workflow mô tả quy trình đặt lịch khám và theo dõi lịch khám, xây dựng kiển trúc Chatbot. 

- Xây dựng hệ thống với đầy đủ chức năng bám sát vào nghiệp vụ tổ chức và quản lý khám chữa bệnh tại bệnh viện. 

- Thực hiện kiểm thử tự động bằng PHPUnit, vận hành hệ thống với Docker và triển khai thực nghiệm tại bệnh viện để thu thập phản hồi từ người dùng. 

## **1.5. Phạm vi nghiên cứu** 

- **Phạm vi không gian** : Đề tài tập trung triển khai và thực nghiệm tại Bệnh viện Đa khoa Trung ương Thái Nguyên, với khả năng mở rộng áp dụng cho các cơ sở y tế khác trong tương lai. 

- **Phạm vi nội dung** : Nghiên cứu tập trung vào việc xây dựng hệ thống quản lý và hỗ trợ đặt lịch khám và tích hợp chatbot tư vấn cơ bản, tra cứu thông 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_5_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

tin lịch khám bác sĩ, dịch vụ khám chữa bệnh, không bao gồm các chức năng như chẩn đoán y khoa chuyên sâu hoặc tích hợp với các thiết bị y tế. 

- **Công nghệ sử dụng:** Phát triển trên nền tàng PHP Larvel MVC, Database MySQL với Xampp Apache, Chatbot sử dụng công nghệ Regex để xử lý văn bản sau đó Query tới cơ sở dữ liệu để trả về lịch khám còn trống của bác sĩ và dịch vụ khám bệnh. Kiểm thử tự động và vận hành hệ thống với PHPUnit và Docker. Xử lý dữ liệu, trực quan hóa dữ liệu thực nghiệm hệ thống với Python và với JupyterNotebook. 

## **1.6. Bố cục báo cáo đồ án tốt nghiệp** 

Báo cáo đề tài đồ án tốt nghiệp sẽ có 4 chương chính: 

- **Chương 1 - Tổng quan về đề tài:** Trình bày cơ sở vấn đề, tính cấp thiết của đề tài, mục tiêu và phạm vi nghiên cứu. 

- **Chương 2 – Cơ sở lý thuyết và công nghệ:** Trình bày về các khái niệm liên quan đến nền tảng kiến thức về công nghệ được sử dụng trong quá trình phát triển hệ thống, xây dựng Chatbot và triển khai thực nghiệm hệ thống. 

- **Chương 3 – Phân tích và thiết kế hệ thống:** Mô tả bài toán, trình bày kết quả khảo sát nghiệp vụ và quy trình quản lý, tổ chức khám chữa bệnh tại bệnh viện Đa khoa Trung Ương Thái Nguyên. Phân tích và thiết kế hệ thống, xây dựng các biểu đồ hướng tới 3 tác nhân đại diện cho 3 phía giao diện chính của hệ thống đó là bệnh nhân, quản trị viên, bác sĩ. Thiết kế và xây dựng Chatbot. 

- **Chương 4 – Thực nghiệm:** Mô tả môi trường thực nghiệp, kết quả thực nghiệm bao gồm giao diện hệ thống, kết quả thực nghiệm và khảo sát phản hồi người dùng tại bệnh viện Đa khoa Trung Ương Thái Nguyên, xây dựng các ca kiểm thử tự động hệ thống và vận hành triển khai hệ thống với Docker. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_6_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ** 

## **2.1. Tổng quan về MySQL và Xampp Apache** 

## **_2.1.1. Tổng quan về MySQL_** 

MySQL là một hệ quản trị cơ sở dữ liệu quan hệ (RDBMS) mã nguồn mở, được sử dụng rộng rãi trong các ứng dụng web để lưu trữ và quản lý dữ liệu. MySQL sử dụng ngôn ngữ truy vấn có cấu trúc (SQL) để thực hiện các thao tác như thêm, sửa, xóa và truy vấn dữ liệu. Với hiệu suất cao, khả năng mở rộng và tính ổn định, MySQL phù hợp cho các hệ thống quản lý lớn như hệ thống đặt lịch khám chữa bệnh. 



<!-- Start of picture text -->
MySQL.<br><!-- End of picture text -->

**Hình 2-1:** _MySQL_ 

Trong đề tài này, MySQL được sử dụng để lưu trữ thông tin về bệnh nhân, bác sĩ, lịch hẹn và các dữ liệu liên quan đến hoạt động của chatbot. Đặc điểm chính của MySQL 

- **Mã nguồn mở:** Cho phép người dùng sử dụng, sửa đổi và phân phối miễn phí, giúp tiết kiệm chi phí và tùy chỉnh theo nhu cầu. 

- **Dựa trên SQL:** Sử dụng  (Structured Query Language) để truy vấn, thao tác và quản lý dữ liệu trong cơ sở dữ liệu. 

- **Cơ sở dữ liệu quan hệ:** Lưu trữ dữ liệu dưới dạng các bảng, với các hàng và cột, và các mối quan hệ giữa chúng. 

- **Cộng đồng hỗ trợ lớn:** Có một cộng đồng nhà phát triển và người dùng tích cực, cung cấp tài liệu, hướng dẫn và hỗ trợ kỹ thuật. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_7_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_2.1.2. Tổng quan về Xampp Apache_** 

XAMPP là một bộ công cụ mã nguồn mở cung cấp môi trường phát triển web cục bộ, bao gồm máy chủ Apache, cơ sở dữ liệu MySQL, PHP, và Perl. XAMPP được sử dụng trong đề tài này để xây dựng và kiểm thử hệ thống quản lý kho trên localhost trước khi triển khai lên máy chủ trực tuyến. 



<!-- Start of picture text -->
f=) XAMPP<br><!-- End of picture text -->

**Hình 2-2:** _XamPP_ 

Trong đề tài đồ án tốt nghiệp của em, XAMPP được sử dụng để: 

- **Chạy máy chủ web** : Apache trong XAMPP xử lý các yêu cầu HTTP để chạy ứng dụng Laravel. 

- **Quản lý cơ sở dữ liệu** : MySQL trong XAMPP được sử dụng để lưu trữ và kiểm thử cơ sở dữ liệu của hệ thống. 

- **Kiểm thử ứng dụng** : XAMPP cung cấp môi trường localhost để kiểm thử các chức năng của hệ thống trước khi triển khai. 

## **2.2. Tổng quan về kiến trúc MVC** 

MVC (Model-View-Controller) là một mẫu kiến trúc phần mềm được sử dụng rộng rãi trong việc phát triển ứng dụng để tạo ra các giao diện người dùng trực quan và có khả năng tương tác cao. 

MVC chia một ứng dụng thành 3 phần chính và mỗi phần có một vai trò riêng biệt: 

- Model là lớp đại diện cho dữ liệu của ứng dụng. Model chịu trách nhiệm lưu trữ, truy xuất và cập nhật dữ liệu. 

- View là lớp giao diện người dùng. Nó hiển thị dữ liệu từ Model cho người dùng và cho phép người dùng tương tác với ứng dụng. 

- Controller là lớp điều khiển luồng của ứng dụng. Nó nhận các yêu cầu từ người dùng, cập nhật Model và chọn View phù hợp để hiển thị. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_8_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
MVC Architecture Pattern<br>!pulls data via ant pulls data via getters<br>H initiates ControllerBrain modifies i:<br>H controls and decides |<br>H how data is displayed Hi<br>View Model<br>Ul Data<br>Represents current Data Logic<br>model state updates data sets data<br>via setters and —_via setters<br>event handlers<br><!-- End of picture text -->

**Hình 2-3:** _Kiến trúc MVC_ 



<!-- Start of picture text -->
—<br>S Data<br>Ro t Model<br>&<br>oO<br>iS)<br>ing<br>%y0, View<br>Se<br><!-- End of picture text -->

**Hình 2-4:** _Luồng xử lý mô hình MVC_ 

Mô hình MVC có luồng xử lý qua các bước sau: 

- Khi một yêu cầu của từ máy khách (Client) gửi đến Server. Thì bị Controller trong MVC chặn lại để xem đó là URL request hay sự kiện. 

- Sau đó, Controller xử lý input của user rồi giao tiếp với Model trong MVC. 

- Model chuẩn bị data và gửi lại cho Controller. 

- Cuối cùng, khi xử lý xong yêu cầu thì Controller gửi dữ liệu trở lại View và hiển thị cho người dùng trên trình duyệt. 

## **2.3. Ngôn ngữ lập trình PHP** 

PHP (Hypertext Preprocessor) là một ngôn ngữ lập trình kịch bản phía máy 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_9_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

chủ (server-side) được thiết kế chủ yếu cho phát triển ứng dụng web. 

PHP được sử dụng rộng rãi trong việc xây dựng các hệ thống quản lý nội dung (CMS), thương mại điện tử, và các ứng dụng web động nhờ vào các ưu điểm sau: 

- **Hỗ trợ đa nền tảng** : PHP hoạt động trên nhiều hệ điều hành như Windows, Linux, và macOS, phù hợp với các môi trường phát triển và triển khai khác nhau. 



<!-- Start of picture text -->
J) PHP<br><!-- End of picture text -->

**Hình 2-5:** _Ngôn ngữ lập trình PHP_ 

- **Tích hợp với cơ sở dữ liệu** : PHP hỗ trợ kết nối với nhiều hệ quản trị cơ sở dữ liệu như MySQL, PostgreSQL, SQLite, và Oracle, trong đó MySQL là lựa chọn phổ biến nhất. 

## **2.4. Tổng quan về Laravel Framework** 

## **_2.4.1. Laravel Framework là gì?_** 

Trong quá trình xây dựng các hệ thống quản lý và ứng dụng web hiện nay, việc lựa chọn framework phù hợp đóng vai trò hết sức quan trọng. Trong phạm vi đề tài, em đã lựa chọn Laravel Framework – một framework của PHP. 

Điểm nổi bật của Laravel là việc áp dụng mô hình MVC (Model – View – Controller), từ đó tách biệt phần xử lý dữ liệu, giao diện và điều khiển luồng chương trình. Ngoài ra, Laravel còn cung cấp các tính năng như hệ thống định tuyến (routing) linh hoạt, cơ chế quản lý cơ sở dữ liệu thông qua Eloquent ORM, 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_10_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

công cụ template engine Blade hỗ trợ xây dựng giao diện nhanh chóng, và nhiều cơ chế bảo mật tích hợp sẵn. 



<!-- Start of picture text -->
S .<br>Authent-<br>ication J innovativebe<br>Template<br>Engine<br>f Libraries<br>and Effective<br>Modular J ORM<br>’ Features<br>of<br>Laravel<br>mvc<br>Architecture<br>Support<br>FT vnicue if Secure<br>f Unit. Migration<br>\ testing System<br><!-- End of picture text -->

**Hình 2-6:** _Các đặc trưng của Laravel_ 

Laravel còn mang lại sự an toàn, khả năng mở rộng, và đặc biệt là tính linh hoạt khi triển khai trên các hệ thống khác nhau 

## **_2.4.2. Kiến trúc của một thư mục Laravel_** 

Khi khởi tạo một dự án Laravel, framework sẽ sinh ra sẵn một cấu trúc thư mục tiêu chuẩn. Cấu trúc này không chỉ giúp việc tổ chức mã nguồn rõ ràng mà còn hỗ trợ quá trình bảo trì và phát triển mở rộng sau này: 

- **app/** : Đây là thư mục quan trọng nhất, chứa các thành phần lõi của ứng dụng. Tại đây lập trình viên sẽ viết các model, controller, middleware và các lớp xử lý chính. 

- **bootstrap/** : Thư mục chịu trách nhiệm khởi động ứng dụng và nạp các tệp cấu hình ban đầu. 

- **config/** : Lưu trữ toàn bộ các tệp cấu hình của hệ thống như cấu hình cơ sở dữ liệu, email, cache hay session. 

- **database/** : Quản lý migration, seeder và factory để thao tác và khởi tạo dữ liệu mẫu cho hệ thống. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_11_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- **public/** : Là nơi đặt tệp index.php – điểm vào (entry point) của ứng dụng, đồng thời chứa các tài nguyên tĩnh như CSS, JavaScript, hình ảnh. 

- **resources/** : Chứa các giao diện (view) viết bằng Blade template, các file ngôn ngữ và tài nguyên chưa được biên dịch. 

- **routes/** : Nơi định nghĩa các tuyến đường (route) cho ứng dụng. Ví dụ: web.php dành cho giao diện web, api.php cho API. 

- **storage/** : Lưu trữ các file tạm, log hệ thống, cache, session và file do người dùng tải lên. 

- **tests/** : Dùng để viết và quản lý các đoạn mã kiểm thử, đảm bảo chất lượng hệ thống. 

- **vendor/** : Chứa toàn bộ thư viện cài đặt thông qua Composer – công cụ quản lý gói của PHP. 

Việc tuân thủ cấu trúc thư mục của Laravel giúp nhóm phát triển dễ dàng phối hợp, hạn chế sự chồng chéo trong code, đồng thời nâng cao khả năng bảo trì hệ thống. 

## **2.5. Tìm hiểu về HTML, CSS, JavaScript và Bootstrap** 

## **_2.5.1. HTML là gì ? (Hypertext Markup Language)_** 

HTML là chữ viết tắt của cụm từ HyperText Markup Language (dịch là Ngôn ngữ đánh dấu siêu văn bản) được sử dụng để tạo một trang web, trên một website có thể sẽ chứa nhiều trang và mỗi trang được quy ra là một tài liệu HTML. 

**Đặc điểm của HTML:** 

- Là ngôn ngữ đánh dấu, không phải ngôn ngữ lập trình. 

- Sử dụng các thẻ (tags) để định nghĩa cấu trúc nội dung. 

- Dễ học, dễ sử dụng, phù hợp cho người mới bắt đầu. 

- Tất cả các trình duyệt đều hỗ trợ. 

- Phiên bản mới nhất là HTML5, bổ sung các thẻ hỗ trợ video, audio, canvas, API cho web ứng dụng. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_12_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



**Hình 2-7:** _HTML_ 

## **_2.5.2. CSS là gì ? (Cascading Style Sheets)_** 

CSS là từ viết tắt của Cascading Style Sheets: công dụng dùng để trang trí trang web và thường được gắn với các ngôn ngữ như HTML, PHP dùng làm nổi bật trang web và hình ảnh trang web. Trong Style Sheet này chứa những câu lệnh CSS. Mỗi câu lệnh CSS sẽ định dạng một phần nhất định của HTML, ví dụ như: font của chữ, đường viền, màu nền, căn chỉnh hình ảnh,… 



**Hình 2-8:** _CSS_ 

**Đặc điểm của CSS:** 

- Giúp tách biệt nội dung (HTML) và hình thức trình bày (CSS). 

- Cho phép định dạng đồng bộ nhiều trang web chỉ với một file CSS. 

- Hỗ trợ thiết kế giao diện responsive (tự động điều chỉnh phù hợp với nhiều kích thước màn hình). 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_13_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- Có thể nhúng trực tiếp trong HTML hoặc tách thành file riêng .css. 

- Phiên bản mới nhất là CSS3, bổ sung nhiều hiệu ứng và tính năng hiện đại (animation, transition, flexbox, grid). 

## **_2.5.3. Javascript là gì?_** 

JavaScript là một ngôn ngữ lập trình kịch bản dựa trên đối tượng được phát triển từ các ý niệm nguyên mẫu được tạo ra vào năm 1995 bởi Brendan Eich tại Netscape. Mục đích ban đầu để nâng cao khả năng tương tác của trang web với người sử dụng. 

JavaScript được hỗ trợ hầu như trên tất cả các trình duyệt như Firefox, Chrome,... thậm chí các trình duyệt trên thiết bị di động cũng hỗ trợ. 

JavaScript là một ngôn ngữ lập trình dự trên nguyên mẫu với cú pháp phát triển từ C. JavaScript có khái niệm từ khóa, do đó gần như JavaScript không được mở rộng. Cũng giống như C, JavaScript không có bộ xử lý xuất/nhập riêng. Trong khi C sử dụng thư viện xuất/nhập chuẩn, JavaScript dựa vào phần mềm ngôn ngữ được gắn vào để thực hiện xuất/nhập. 



<!-- Start of picture text -->
JS<br><!-- End of picture text -->

**Hình 2-9:** _Javascript_ 

## **_2.5.4. Bootstrap là gì?_** 

Bootstrap là một framework front-end mã nguồn mở, được phát triển bởi Twitter. Bootstrap cung cấp sẵn các thành phần giao diện (UI Components) như nút bấm, form, bảng, thanh điều hướng. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_14_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



**Hình 2-10:** _Bootstrap_ 

## **Đặc điểm của Bootstrap:** 

- Cung cấp bộ công cụ dựng sẵn gồm HTML, CSS và JavaScript. 

- Hỗ trợ responsive design, giúp website hiển thị tốt trên mọi thiết bị (desktop, tablet, mobile). 

- Dễ sử dụng, có thể tùy chỉnh linh hoạt theo nhu cầu. 

- Tích hợp sẵn nhiều thành phần giao diện như navbar, modal, carousel. 

- Có cộng đồng lớn và tài liệu hướng dẫn chi tiết. 

## **2.6. Tìm hiểu về các công nghệ xử lý văn bản tự nhiên** 

Trong kỷ nguyên công nghệ số hiện nay, xử lý ngôn ngữ tự nhiên (Natural Language Processing – NLP) là một lĩnh vực quan trọng của trí tuệ nhân tạo, cho phép máy tính có thể hiểu, phân tích, và tạo ra ngôn ngữ của con người. NLP đóng vai trò cầu nối giữa máy tính và con người, giúp phát triển các hệ thống như: chatbot, công cụ dịch máy, trợ lý ảo, phân tích dữ liệu văn bản, và nhiều ứng dụng khác trong đời sống. 

Trong phạm vi đề tài, công nghệ xử lý văn bản cơ bản và được sử dụng nhiều là Regex (Regular Expression). Regex hỗ trợ tìm kiếm, kiểm tra, và trích xuất dữ liệu văn bản thông qua các mẫu biểu thức chính quy, đồng thời nó cũng là một công cụ mạnh mẽ được phát triển riêng cho ngôn ngữ tiếng Việt, cung cấp nhiều chức năng như tách từ, gán nhãn từ loại, phân tích cú pháp. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_15_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_2.6.1. Tổng quan về Regex_** 

Regex (Regular Expression) là một ngôn ngữ dùng để mô tả các mẫu chuỗi ký tự (pattern) nhằm tìm kiếm và xử lý văn bản. Thay vì phải viết nhiều dòng lệnh phức tạp, Regex cho phép định nghĩa các quy tắc ngắn gọn, từ đó có thể kiểm tra dữ liệu đầu vào, trích xuất thông tin, hoặc thay thế các chuỗi theo mong muốn. 



<!-- Start of picture text -->
Regular expression boundary<br>as many times as<br>match anything possible match upper and<br>contained within match the @ lower case A<br>[ brackets "| / symbol through Z<br>/\\w._%+-]+@[\w.-]+\.0 . - . -Z}\{2,4)/7:<br>), x match the . symbol matchtimes  atbut leastno more two<br>match any character match any .,_%t- than four times<br>A-Z upper or lower<br>case and any<br>number0 to 9<br><!-- End of picture text -->

**Hình 2-11:** _Mô tả về Regex_ 

**Đặc điểm của Regex:** 

- Ngắn gọn, súc tích, có thể thay thế nhiều đoạn code xử lý chuỗi phức tạp. 

- Hỗ trợ hầu hết các ngôn ngữ lập trình như PHP, Python, Java, JavaScript. 

- Có khả năng biểu diễn các mẫu từ đơn giản đến rất phức tạp. 

- Học cú pháp ban đầu tương đối khó, dễ gây nhầm lẫn nếu biểu thức dài. 

- Thích hợp cho các tác vụ xử lý văn bản mang tính quy tắc, nhưng hạn chế khi áp dụng vào các ngữ cảnh phức tạp cần hiểu ngữ nghĩa. 

**Ứng dụng trong thực tế:** 

   - Kiểm tra dữ liệu người dùng nhập vào (email, số điện thoại, ngày sinh). 

   - Trích xuất thông tin từ văn bản lớn (ví dụ: tìm các mã bệnh, số thẻ BHYT trong dữ liệu bệnh viện). 

   - Làm sạch dữ liệu trước khi đưa vào mô hình NLP. 

- **_2.6.2. Tổng quan về NLP_** 

Xử lý ngôn ngữ tự nhiên (Natural Language Processing – NLP) là một lĩnh 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_16_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

vực thuộc Trí tuệ nhân tạo (AI) và Khoa học máy tính, tập trung vào việc giúp máy tính có khả năng hiểu, diễn giải và tạo ra ngôn ngữ của con người một cách tự nhiên nhất. 



<!-- Start of picture text -->
| Cord seementaton }=> =aw<br>z text<br>=[_& Postagging> Annotation<br>3 object<br>i Annotated<br>" -—> tex<br>| (CBependeneyparsing =><br><!-- End of picture text -->

**Hình 2-12:** _Kiến trúc căn bản của NLP_ 

Một hệ thống NLP thường gồm các bước xử lý sau: 

- **Tiền xử lý ngôn ngữ (Text Preprocessing):** Loại bỏ dấu câu, chuẩn hóa văn bản, tách từ (tokenization), gán nhãn từ loại (POS tagging). 

- **Phân tích cú pháp và ngữ nghĩa:** Xác định cấu trúc ngữ pháp, quan hệ giữa các từ, trích xuất thông tin quan trọng. 

- **Hiểu ngữ cảnh và ý định:** Ứng dụng các mô hình ngôn ngữ (Language Models) như BERT, GPT, LLaMA để suy luận ngữ nghĩa. 

- **Sinh phản hồi tự nhiên (Natural Language Generation – NLG):** Tạo ra câu trả lời hoặc phản hồi có ý nghĩa, mạch lạc và tự nhiên. 

**Ứng dụng trong thực tế:** NLP kết hợp giữa ngôn ngữ học tính toán (Computational Linguistics) và học máy (Machine Learning) để phân tích cú pháp, ngữ nghĩa và ngữ cảnh của văn bản hoặc lời nói. Trong các hệ thống hiện đại, NLP đóng vai trò then chốt trong nhiều ứng dụng như: 

- Chatbot và trợ lý ảo (ví dụ: ChatGPT, Google Assistant, Siri) 

- Phân loại và trích xuất thông tin từ văn bản 

- Dịch tự động, tóm tắt văn bản, sinh văn bản tự động 

- Phân tích cảm xúc, nhận diện thực thể (NER) 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_17_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **2.7. Tổng quan về PHPUnit** 

Trong phát triển phần mềm, kiểm thử (testing) là một giai đoạn quan trọng nhằm đảm bảo chất lượng, tính ổn định và độ tin cậy của hệ thống trước khi triển khai thực tế. 

PHPUnit là một framework kiểm thử đơn vị (Unit Testing Framework) dành cho PHP, được phát triển dựa trên mô hình xUnit. Công cụ này cho phép lập trình viên viết và thực thi các đoạn mã kiểm thử một cách tự động, giúp phát hiện sớm lỗi logic trong quá trình lập trình và đảm bảo các thành phần trong hệ thống hoạt động đúng như mong đợi. 



<!-- Start of picture text -->
©, PHPUnit<br><!-- End of picture text -->

**Hình 2-13:** _PHPUnit_ 

**Đặc điểm của PHPUnit:** 

- Cung cấp môi trường để viết kiểm thử đơn vị (unit test) cho từng hàm, phương thức hoặc lớp trong ứng dụng. 

- Hỗ trợ kiểm thử tự động, giúp giảm thiểu thời gian và công sức so với kiểm thử thủ công. 

- Có thể tích hợp dễ dàng với các framework PHP như Laravel, Symfony, CodeIgniter. 

- Là công cụ mã nguồn mở, thường xuyên được cập nhật và hỗ trợ từ cộng đồng lập trình viên PHP. 

**Ứng dụng trong thực tế:** 

- Đảm bảo chất lượng và độ tin cậy của các chức năng quan trọng trong hệ thống (ví dụ: đăng ký tài khoản, đặt lịch khám, xử lý thanh toán). 

- Hỗ trợ phát hiện và khắc phục lỗi sớm ngay trong quá trình phát triển. 

- Giúp dễ dàng kiểm tra lại sau khi nâng cấp hoặc chỉnh sửa mã nguồn, đảm 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_18_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

bảo không phát sinh lỗi mới (regression testing). 

- Nâng cao tính chuyên nghiệp và chuẩn mực trong phát triển phần mềm. 

## **2.8. Tổng quan về Docker** 

Docker là một nền tảng mã nguồn mở dùng để đóng gói (package), triển khai (deploy) và chạy (run) các ứng dụng trong môi trường container – một dạng môi trường ảo nhẹ, cô lập và linh hoạt. Docker giúp nhà phát triển đảm bảo ứng dụng của mình chạy nhất quán trên mọi hệ thống, bất kể khác biệt về môi trường, thư viện hay cấu hình hệ điều hành. 



<!-- Start of picture text -->
Docker Architecture<br>cocker buia<br>docker pull =<br>¥ Docker Daemon<br>docker run rf Containers images [i —_ @<br><7 =<br>e+ oe<br>a / [<br>@ / J seeeeeee build<br>User vy —_— pull |<br><!-- End of picture text -->

**Hình 2-14:** _Kiến trúc tổng quan của Docker_ 

Container trong Docker tương tự như một “hộp” chứa toàn bộ mã nguồn, thư viện, và các phụ thuộc cần thiết để ứng dụng hoạt động. Không giống như máy ảo (Virtual Machine) phải mô phỏng toàn bộ hệ điều hành, container chia sẻ kernel của hệ thống chủ, nên khởi động nhanh hơn, tốn ít tài nguyên hơn và dễ dàng mở rộng. Nhờ Docker, toàn bộ hệ thống có thể được đóng gói – di chuyển – khởi chạy chỉ bằng một lệnh duy nhất (docker-compose up), đảm bảo tính ổn định, hiệu năng và khả năng tái sử dụng lại cao. 

**Thành phần chính của Docker** 

- **Docker Engine:** Thành phần lõi, chịu trách nhiệm tạo và quản lý container. 

- **Docker Image:** Mẫu (template) chứa sẵn mã nguồn và môi trường chạy của ứng dụng. 

- **Docker Container:** Phiên bản đang chạy của một image. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_19_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- **Dockerfile:** Tập tin mô tả cách build một image (các lệnh cài đặt, copy, cấu hình, v.v.). 

- **Docker Hub / Registry:** Kho lưu trữ và chia sẻ các image. 

## **2.9. Tìm hiểu về các công cụ hỗ trợ trực quan hóa dữ liệu với Python và Jupyter Notebook** 

Trong quá trình phân tích và đánh giá dữ liệu thực nghiệm thu thập từ hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh, việc trực quan hóa dữ liệu đóng vai trò quan trọng trong việc giúp người nghiên cứu dễ dàng nhận biết xu hướng, hành vi và mối quan hệ giữa các biến. 

Các công cụ trực quan hóa cho phép chuyển đổi dữ liệu dạng bảng hoặc số liệu khô khan thành biểu đồ, đồ thị sinh động, hỗ trợ quá trình đánh giá hiệu quả hoạt động của hệ thống, hành vi người dùng và ra quyết định quản lý. Trong đồ án của em, ngôn ngữ Python kết hợp với các thư viện Matplotlib và Seaborn được sử dụng để trực quan hóa dữ liệu thực nghiệm, trong khi Jupyter Notebook đóng vai trò là môi trường lập trình, thử nghiệm và trình bày kết quả phân tích một cách trực quan, linh hoạt và dễ theo dõi. 

## **_2.9.1. Tìm hiểu về các công cụ trực quan hóa dữ liệu với Python_** 

Trực quan hóa dữ liệu (Data Visualization) là quá trình biểu diễn dữ liệu dưới dạng đồ thị, biểu đồ hoặc hình ảnh nhằm giúp người phân tích dễ dàng nhận biết xu hướng, quy luật và mối quan hệ trong dữ liệu. 

Python là ngôn ngữ lập trình mạnh mẽ, được sử dụng rộng rãi trong khoa học dữ liệu nhờ hệ sinh thái thư viện phong phú và dễ mở rộng. Trong đồ án này, em sử dụng hai thư viện chính để trực quan hóa dữ liệu là Matplotlib và Seaborn. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_20_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
@sea born<br><!-- End of picture text -->

**Hình 2-15:** _Giới thiệu về Seaborn_ 

- Matplotlib: Là thư viện trực quan hóa dữ liệu cơ bản và phổ biến nhất trong Python. Matplotlib cho phép vẽ nhiều loại biểu đồ như biểu đồ cột, biểu đồ tròn, biểu đồ phân bố, biểu đồ đường,… với khả năng tùy biến linh hoạt. Trong đồ án, Matplotlib được sử dụng để trực quan hóa phân bố độ tuổi bệnh nhân, số lượng bác sĩ theo khoa và số lượng kết quả khảo sát theo từng câu hỏi. 



<!-- Start of picture text -->
@ python &&<br><!-- End of picture text -->

**Hình 2-16:** _Giới thiệu về Matplotlib_ 

- Seaborn: Được xây dựng dựa trên nền Matplotlib, Seaborn cung cấp giao diện trực quan và dễ sử dụng hơn, đồng thời hỗ trợ nhiều loại biểu đồ thống kê nâng cao, được ứng dụng trong việc phân tích mối quan hệ giữa các thuộc tính. 

Việc sử dụng kết hợp Matplotlib và Seaborn giúp quá trình trực quan hóa dữ liệu trong đồ án trở nên hiệu quả, trực quan và dễ hiểu, hỗ trợ quá trình phân tích và đánh giá dữ liệu thu thập từ hệ thống thực nghiệm. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_21_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_2.9.2. Tìm hiểu về Jupyter Notebook_** 

Jupyter Notebook là một công cụ mã nguồn mở được sử dụng phổ biến trong lĩnh vực khoa học dữ liệu, học máy và nghiên cứu. Môi trường này cho phép người dùng viết mã, chạy mã, hiển thị kết quả và ghi chú mô tả trong cùng một giao diện tương tác. 



<!-- Start of picture text -->
A Quick egum<br>Introduction Jupyter<br>to Jupyter<br>Notebooks ~~<br><!-- End of picture text -->

**Hình 2-17:** _Giới thiệu về Jupyter Notebook_ 

Trong quá trình phát triển đồ án, Jupyter Notebook được em sử dụng làm môi trường lập trình và trình bày kết quả trực quan hóa dữ liệu bệnh nhân và bác sĩ. Cụ thể: 

- Trực quan hóa phân bố độ tuổi của bệnh nhân nhằm nhận biết cơ cấu nhóm tuổi sử dụng dịch vụ khám chữa bệnh. 

- Trực quan hóa số lượng bác sĩ theo từng khoa và chức vụ để đánh giá cơ cấu nhân lực trong bệnh viện. 

- Trực quan hóa kết quả khảo sát đánh giá dịch vụ theo từng câu hỏi, phục vụ cho quá trình phân tích mức độ hài lòng của người bệnh. 

Nhờ đặc tính linh hoạt, trực quan và dễ sử dụng, Jupyter Notebook giúp quá trình phân tích và trình bày dữ liệu trở nên mạch lạc, khoa học và thuận tiện cho cả giai đoạn thực nghiệm lẫn báo cáo kết quả. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_22_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG** 

## **3.1. Mô tả bài toán** 

Trước đây, tại bệnh viện Đa khoa Trung Ương Thái Nguyên nói riêng và các bệnh viện lớn nhỏ khác nói chung,  khi có nhu cầu đi khám bệnh, bệnh nhân thường phải chủ động sắp xếp thời gian và đi sớm đến bệnh viện để xếp hàng đăng ký. Người bệnh phải chờ đợi trong hàng dài, qua nhiều khâu trung gian như lấy số thứ tự, xuất trình giấy tờ tùy thân (CMND/CCCD), thẻ bảo hiểm y tế (nếu có), sau đó mua sổ khám và điền thông tin khám để nhân viên y tế ghi nhận, phân loại, sắp xếp bác sĩ theo đúng chuyên khoa. Tiếp đó, bệnh nhân phải đến phòng khám được chỉ định và chờ đến lượt được bác sĩ gọi vào. 

Quy trình trên thường gây mất nhiều thời gian, công sức, đặc biệt trong những ngày cao điểm khi lượng bệnh nhân đông. Nhiều người phải chờ đợi hàng tiếng, thậm chí đến từ rất sớm trước giờ làm việc của bệnh viện chỉ để được lấy số khám. Điều này ảnh hưởng đến trải nghiệm của người bệnh, gây mệt mỏi và đôi khi còn làm tình trạng sức khỏe trở nên nghiêm trọng hơn trong lúc chờ đợi. 

Với sự phát triển mạnh mẽ của công nghệ thông tin, các hệ thống đặt lịch khám bệnh trực tuyến đã ra đời nhằm khắc phục những hạn chế nói trên. Thông qua website hoặc ứng dụng, bệnh nhân có thể dễ dàng tra cứu thông tin và đặt lịch khám bất kỳ lúc nào, đồng thời biết trước được thời gian làm việc của bác sĩ hoặc chuyên gia y tế. Nhờ đó, người bệnh không còn phải xếp hàng chờ đợi lâu, tiết kiệm đáng kể thời gian và công sức, đồng thời nâng cao chất lượng dịch vụ y tế. 

Tuy nhiên, một nhu cầu ngày càng rõ rệt của người bệnh hiện nay là mong muốn được lựa chọn dịch vụ khám phù hợp và bác sĩ có trình độ chuyên môn cao. Đặc biệt, nhiều bệnh nhân có xu hướng lựa chọn khám với các bác sĩ giữ chức danh giáo sư, phó giáo sư, trưởng khoa, phó khoa hoặc các chuyên gia đầu ngành. Đây là những yếu tố giúp bệnh nhân yên tâm hơn về chất lượng chẩn đoán và điều trị. Các hệ thống truyền thống trước đây mới chỉ dừng lại ở việc phân bổ bác sĩ theo chuyên khoa chung, chưa đáp ứng được nhu cầu lựa chọn bác sĩ cụ thể, nhất là đối với các bác sĩ có học hàm, học vị cao hoặc vị trí quản lý chuyên môn. 

Do đó, việc xây dựng hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh có 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_23_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

tích hợp chatbot tư vấn không chỉ giúp giải quyết bài toán giảm tải thời gian chờ đợi mà còn đáp ứng nhu cầu mới của người bệnh: được chủ động lựa chọn dịch vụ, chọn bác sĩ phù hợp với yêu cầu cá nhân và đặc biệt là các bác sĩ có chuyên môn cao trong bệnh viện. 

## **3.2. Khảo sát nghiệp vụ, quy trình và tổ chức khám chữa bệnh tại bệnh viện Đa khoa Trung Ương Thái Nguyên** 

Để xây dựng hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot tư vấn, em đã tiến hành khảo sát thực tế tại Bệnh viện Đa khoa Trung Ương Thái Nguyên. Việc khảo sát tập trung vào hai đối tượng chính là bệnh nhân và đội ngũ y bác sĩ. 

- Về phía bệnh nhân: Em tìm hiểu những khó khăn, bất tiện trong quá trình đăng ký, chờ đợi và lựa chọn dịch vụ khám bệnh thủ công và đặt lịch khám từ xa. Đặc biệt, trong việc đăng ký lịch khám chữa bệnh, nhu cầu ngày càng cao trong việc lựa chọn bác sĩ phù hợp theo chuyên khoa, học hàm, học vị (giáo sư, phó giáo sư, trưởng/phó khoa) và mong muốn có thể đặt lịch khám nhanh chóng, thuận tiện hơn. 

- Về phía bác sĩ và nhân viên y tế: Em khảo sát về quy trình tiếp nhận, thăm khám, chỉ định xét nghiệm, tư vấn điều trị cũng như những khó khăn trong quản lý hồ sơ bệnh án, phân bổ thời gian khám cho bệnh nhân, và những bất cập trong việc điều phối lịch khám khi lượng bệnh nhân quá đông. 

Thông qua khảo sát, em đã thu thập được cái nhìn tổng quan về nghiệp vụ khám chữa bệnh, tổ chức các khoa khám bệnh, dịch vụ, quy trình làm việc của bác sĩ, quy trình quản lý hồ sơ bệnh nhân và thông tin bác sĩ. Đây là cơ sở quan trọng để đề xuất giải pháp công nghệ phù hợp, giúp cải thiện trải nghiệm cho bệnh nhân và tối ưu hiệu quả công việc cho đội ngũ y tế. 

## **_3.2.1. Khảo sát quy trình đăng ký khám chữa bệnh tại bệnh viện_** 

Hiện nay, quy trình đăng ký khám chữa bệnh tại Bệnh viện Đa khoa Trung Ương Thái Nguyên vẫn chủ yếu thực hiện theo hình thức truyền thống. Khi đặt lịch khám từ xa, người bệnh sẽ phải liên hệ qua tổng đài để nhân viên hỗ trợ đặt lịch khám. Người bệnh khi đến khám phải trực tiếp đến quầy tiếp nhận để làm thủ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_24_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

tục. Cụ thể: 

- Bệnh nhân đến quầy tiếp nhận, xuất trình giấy tờ tùy thân (CMND/CCCD), thẻ bảo hiểm y tế (nếu có). 

- Nhân viên y tế kiểm tra thông tin, hướng dẫn người bệnh mua sổ khám bệnh và điền thông tin cần thiết. 

- Sau đó, bệnh nhân sẽ được sắp xếp số thứ tự và phân luồng đến phòng khám chuyên khoa phù hợp. 

- Người bệnh đến phòng khám, ngồi đợi đến lượt để được bác sĩ gọi vào khám. 

**Hạn chế đối với bệnh nhân** : 

- Phải đến sớm và xếp hàng dài để lấy số thứ tự, tốn nhiều thời gian và công sức. 

- Không thể chủ động lựa chọn bác sĩ theo chuyên khoa hoặc theo chức danh (giáo sư, phó giáo sư, trưởng/phó khoa). 

- Khi bệnh viện đông, bệnh nhân phải chờ đợi hàng giờ, ảnh hưởng đến sức khỏe, đặc biệt là người già, trẻ nhỏ hoặc người bệnh nặng. 

- Thông tin về lịch làm việc của bác sĩ không được công khai rõ ràng, bệnh nhân thường chỉ được phân luồng thụ động, thiếu sự lựa chọn phù hợp với nhu cầu cá nhân. 

Với sự phát triển của công nghệ thông tin, bệnh viện đã bước đầu triển khai các giải pháp đăng ký khám trực tuyến, tuy nhiên vẫn chưa phổ biến và chưa đáp ứng được nhu cầu ngày càng đa dạng của bệnh nhân như: lựa chọn bác sĩ theo chuyên môn, chức danh (giáo sư, phó giáo sư, trưởng khoa, phó khoa), hay lựa chọn dịch vụ khám chất lượng cao. 

**_3.2.2. Khảo sát cơ cấu tổ chức các khoa khám chữa bệnh và dịch vụ khám bệnh tại bệnh viện Đa khoa Trung Ương Thái Nguyên_** 

Để xây dựng một hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh hiệu quả, việc đầu tiên cần nắm rõ đó là cơ cấu tổ chức của các khoa khám bệnh và dịch vụ khám chữa bệnh tại bệnh viện. Do đó, em đã tiến hành khảo sát các bác sĩ, nhân viên y tế và tài liệu giới thiệu của bệnh viện để thu thập thông tin. 

Kết quả khảo sát cho thấy, tại Bệnh viện Đa khoa Trung Ương Thái Nguyên 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_25_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

hiện có 12 khoa khám bệnh chính, mỗi khoa đảm nhận một chuyên môn riêng biệt và đi kèm với các dịch vụ khám chữa bệnh tương ứng. Ngoài ra, bệnh viện còn cung cấp nhiều dịch vụ khám đa dạng, từ khám bảo hiểm y tế, khám thông thường đến các dịch vụ khám theo yêu cầu, khám nhanh và khám với bác sĩ có chức danh cao (giáo sư, phó giáo sư, trưởng/phó khoa). 

Việc hiểu rõ cơ cấu này giúp hệ thống đặt lịch có thể: 

- Quản lý và hiển thị danh sách các khoa khám bệnh một cách khoa học. 

- Cho phép bệnh nhân tìm các bác sĩ ưng ý bằng cách chọn khoa, chọn dịch vụ phù hợp với nhu cầu, đồng thời người bệnh có thể nắm được thông tin các khoa khám bệnh và thông tin khám đối với mỗi dịch vụ. 

- Đáp ứng nhu cầu ngày càng tăng của người bệnh trong việc chủ động lựa chọn bác sĩ theo chuyên khoa và dịch vụ đi kèm. 

**Bảng 3-1:** _Danh sách khoa khám bệnh và dịch vụ tương ứng tại bệnh viện_ 

|**Khoa khám bệnh**<br>**Dịch vụ**|
|---|
|Khám viêm mũi xoang, đau họng, ù<br>tai|
|**Khoa Tai – Mũi – Họng**<br>Khám viêm tai giữa, viêm amidan|
|Tư vấn nội soi TMH|
|Hút mũi, khí dung, làm thuốc tai|
|Khám mụn, viêm da, dị ứng|
|Khám nấm, lang ben, zona|
|**Khoa Da Liễu**<br>Tư vấn chăm sóc da thẩm mỹ|
|Tư vấn và điều trị rối loạn sắc tố da<br>(nám, tàn nhang)|
|Khám và điều trị viêm phổi, viêm phế<br>quản|
|**Khoa Nhi**<br>Tư vấn dinh dưỡng, phát triển thể chất<br>cho trẻ|
|Tiêm chủng dịch vụ|
|Khám và điều trị tiêu chảy, rối loạn|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_26_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||tiêu hóa cho trẻ|
|---|---|
||Khám thai định kỳ, siêu âm thai|
|**Khoa Phụ Sản**|Khám viêm nhiễm phụ khoa<br>Tư vấn và điều trị rối loạn kinh<br>nguyệt, vô sinh hiếm muộn|
||Khám sỏi thận, bí tiểu, tiểu buốt|
|**Khoa Thận – Tiết Niệu**|Siêu âm thận, bàng quang|
||Tư vấn viêm tuyến tiền liệt|
||Khám đau bụng, đầy hơi, khó tiêu|
|**Khoa Tiêu Hóa**|Khám viêm gan, xơ gan|
||Tư vấn nội soi dạ dày, đại tràng|
||Khám đau vai gáy, thoái hóa khớp|
|**Khoa Cơ – Xương Khớp**|Khám cột sống, thoát vị đĩa đệm|
||Tư vấn điều trị Gout, loãng xương|
||Khám đau đầu, rối loạn tiền đình|
|**Khoa Thần Kinh**|Khám sau tai biến, đột quỵ|
||Tư vấn rối loạn thần kinh thực vật|
|**Kh U Bớ**|Tư vấn và theo dõi bệnh nhân sau điều<br>trị hóa trị/xạ trị|
|**oa ng ưu**|Tư vấn khám và tầm soát ung thư định<br>kỳ|
||Tư vấn và quản lý bệnh nhân sau can<br>thiệp tim mạch|
||Khám và điều trị bệnh mạch vành, suy|
|**Khoa Nội – Tim Mạch**|tim|
||Đo điện tâm đồ, siêu âm tim|
||Khám định kì huyết áp, mỡ máu, gan<br>nhiễm mỡ|
||Khám và tư vấn các bệnh về mắt|
|**Khoa Mắt**|Khám và điều trị nhãn nhi (bệnh mắt|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_27_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||ở trẻ em)|
|---|---|
||Khám và phẫu thuật thẩm mỹ nhãn<br>khoa|
||Tư vấn phẫu thuật thủy tinh thể|
||Khám và phẫu thuật thẩm mỹ nhãn|
||khoa|
||Nhổ răng, tiểu phẫu răng khôn, răng|
|**Khoa Răng – Hàm – Mặt**|mọc lệch<br>|
||Điều Trị Bệnh Lý Nha Chu (Viêm Lợi,|
||Viêm Quanh Răng)|
||Khám và Tư Vấn Chỉnh Nha – Phục|
||Hình Răng Thẩm Mỹ|



## **_3.2.3. Khảo sát quy trình khám chữa bệnh của bác sĩ_** 

Đối với bác sĩ, quy trình làm việc sẽ diễn ra như sau: 

- Vào cuối mỗi tuần, các bác sĩ sẽ kiểm tra lịch công tác, lịch phẫu thuật, ca trực và những nhiệm vụ chuyên môn đặc biệt khác để đăng ký lịch làm việc phù hợp cho tuần kế tiếp. 

- Dựa trên lịch đã được sắp xếp, vào mỗi ngày làm việc, nhân viên y tế tại quầy tiếp nhận sẽ phân luồng bệnh nhân thủ công đến các phòng khám, tương ứng với các bác sĩ có lịch khám trong ngày hôm đó. 

- Bác sĩ tiếp nhận bệnh nhân theo số thứ tự, thực hiện khám, chỉ định cận lâm sàng nếu cần và đưa ra phương án điều trị. 

**Hạn chế đối với bác sĩ:** 

- Do lịch làm việc chỉ được cập nhật theo tuần và phân luồng thủ công, bác sĩ khó chủ động tối ưu lịch khám của mình, nhất là trong những ngày số lượng bệnh nhân tăng đột biến. 

- Thời gian dành cho mỗi bệnh nhân có thể bị hạn chế do áp lực số lượng bệnh nhân đông. 

- Việc phân luồng thủ công có thể dẫn đến tình trạng mất cân đối, phòng khám quá tải trong khi phòng khác còn trống. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_28_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- Khó khăn trong công tác quản lý và theo dõi: Do chưa có một hệ thống tập trung để quản lý toàn bộ dữ liệu bệnh nhân, lịch hẹn và tiến độ khám chữa bệnh, bác sĩ phải phụ thuộc nhiều vào hồ sơ giấy hoặc các hệ thống đơn lẻ. 

- Giảm khả năng phối hợp liên khoa: Trong nhiều trường hợp bệnh nhân cần sự phối hợp giữa các khoa khác nhau, bác sĩ gặp khó khăn khi lịch khám không được đồng bộ, dẫn đến sự chồng chéo hoặc gián đoạn trong quy trình điều trị. 

## **_3.2.4. Khảo sát quy trình quản lý hồ sơ thông tin bệnh nhân tại bệnh viện_** 

Trong hoạt động khám chữa bệnh, quản lý hồ sơ thông tin bệnh nhân là một trong những nghiệp vụ quan trọng và diễn ra thường xuyên nhất tại bệnh viện. Qua quá trình khảo sát tại bệnh viện, có thể thấy quy trình hiện nay vẫn còn mang tính thủ công và phân tán ở nhiều bộ phận. 

Hiện tại, thông tin bệnh nhân được ghi nhận và lưu trữ chủ yếu thông qua các giấy tờ hành chính, bao gồm: 

- Số căn cước công dân (CCCD) hoặc số chứng minh nhân dân – dùng để định danh cá nhân. 

- Số thẻ bảo hiểm y tế (BHYT) – dùng để tra cứu quyền lợi và hỗ trợ chi phí khám chữa bệnh. 

- Thông tin cá nhân cơ bản như họ tên, ngày tháng năm sinh, giới tính, quê quán, địa chỉ cư trú, số điện thoại liên hệ. 

Tuy nhiên, trong thực tế, việc quản lý hồ sơ bệnh nhân theo phương thức truyền thống này còn tồn tại một số hạn chế như: 

   - Dữ liệu bệnh nhân bị phân tán giữa các khoa, phòng khám, gây khó khăn trong việc tổng hợp và truy xuất lịch sử khám chữa bệnh. 

   - Khó khăn trong việc tra cứu thông tin theo số CCCD hoặc BHYT do quy trình nhập liệu thủ công, dễ sai sót hoặc trùng lặp. 

   - Việc lưu trữ hồ sơ giấy làm tăng chi phí bảo quản, tốn diện tích lưu trữ, và không đảm bảo tính bảo mật cao. 

- Từ những hạn chế nêu trên, có thể thấy việc xây dựng một hệ thống tích hợp 

- chức năng quản lý hồ sơ bệnh nhân điện tử là hết sức cần thiết. Hệ thống này cần 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_29_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

đáp ứng các yêu cầu sau: 

- Quản lý thống nhất thông tin bệnh nhân dựa trên số CCCD và số thẻ BHYT như hai định danh chính, giúp tra cứu nhanh chóng, chính xác và tránh trùng lặp hồ sơ. 

- Lưu trữ và theo dõi lịch sử khám bệnh của từng bệnh nhân qua các lần khám, bao gồm thông tin đặt lịch, kết quả khám, chẩn đoán, kê đơn thuốc, và hướng dẫn điều trị. 

- Hỗ trợ truy xuất nhanh kết quả khám cho bệnh nhân hoặc bác sĩ, phục vụ công tác tái khám, thống kê và báo cáo. 

- Đảm bảo tính bảo mật, toàn vẹn và an toàn dữ liệu theo quy định của ngành y tế. 

Việc triển khai hệ thống quản lý hồ sơ bệnh nhân điện tử không chỉ giúp bệnh viện nâng cao hiệu quả hoạt động, giảm sai sót trong nhập liệu, mà còn tạo nền tảng cho việc số hóa toàn diện công tác quản lý y tế, góp phần tiến tới mô hình bệnh viện thông minh (Smart Hospital) trong thời đại chuyển đổi số hiện nay. 

## **_3.2.5. Khảo sát quy trình quản lý bác sĩ tại bệnh viện_** 

Trong hệ thống khám chữa bệnh, đội ngũ bác sĩ là lực lượng nòng cốt quyết định trực tiếp đến chất lượng dịch vụ y tế và hiệu quả hoạt động của bệnh viện. Vì vậy, việc quản lý thông tin bác sĩ một cách khoa học, chính xác và đầy đủ là yêu cầu thiết yếu trong công tác quản trị. 

Qua khảo sát thực tế tại bệnh viện, việc quản lý bác sĩ hiện nay chủ yếu được thực hiện thông qua hồ sơ hành chính và sổ sách thủ công, bao gồm các thông tin cơ bản như: 

- Họ tên, giới tính, năm sinh. 

- Khoa làm việc, dịch vụ khám chữa bệnh và vị trí công tác. 

- Chức vụ chuyên môn (bác sĩ điều trị, trưởng khoa, phó khoa, v.v.). 

- Số điện thoại, địa chỉ liên hệ, và lịch làm việc hàng tuần. 

Quy trình này giúp bệnh viện có thể nắm bắt được tình hình nhân sự cơ bản, tuy nhiên vẫn còn nhiều hạn chế: 

- Thông tin bác sĩ còn được lưu trữ một cách thủ công, vì vậy khó khăn đối với đội ngũ bác sĩ và bệnh viện trong quá trình quản lý thông tin cá nhân và 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_30_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

sắp xếp nhân sự bệnh viện. 

- Việc phân công, sắp xếp lịch làm việc còn phụ thuộc vào thao tác thủ công, dễ dẫn đến trùng lịch hoặc sai sót khi điều phối nhân sự. 

- Chưa có hệ thống theo dõi năng suất, số lượng ca khám hoặc lịch sử công tác của từng bác sĩ một cách thống nhất. 

Từ thực trạng đó, việc xây dựng hệ thống tích hợp chức năng quản lý bác sĩ điện tử là hết sức cần thiết. Hệ thống này cần đảm bảo các chức năng: 

- Quản lý hồ sơ bác sĩ tập trung, bao gồm thông tin cá nhân, khoa phụ trách, dịch vụ khám chữa bệnh, chức vụ và lịch làm việc. 

- Phân loại bác sĩ theo chuyên khoa và chức vụ, giúp lãnh đạo dễ dàng tra cứu và phân công công việc. 

- Theo dõi số lượng lịch khám, số ca khám và hiệu suất làm việc của từng bác sĩ, phục vụ công tác thống kê, đánh giá và quản lý chất lượng khám chữa bệnh. 

- Tích hợp với hệ thống đặt lịch khám của bệnh nhân, đảm bảo tự động đồng bộ lịch làm việc và tránh trùng lặp giữa các ca khám. 

Việc áp dụng hệ thống quản lý bác sĩ số hóa không chỉ nâng cao hiệu quả điều hành nhân sự, mà còn góp phần hiện đại hóa quy trình quản lý bệnh viện, giúp tối ưu hoá việc phân bổ nguồn lực, tăng tính minh bạch và hỗ trợ quá trình chuyển đổi số trong ngành y tế. 

## **3.3. Giới thiệu các tác nhân và các ca sử dụng tương ứng đối với từng tác nhân** 

## **trong hệ thống** 

Từ việc khảo sát nghiệp vụ, quy trình khám chữa bệnh thực tế tại Bệnh viện Đa khoa Trung Ương Thái Nguyên (phần 3.2), có thể nhận thấy nhu cầu cấp thiết trong việc xây dựng một hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot tư vấn. 

Kết quả khảo sát cho thấy: 

- Bệnh nhân hiện nay gặp nhiều bất cập trong việc đăng ký khám bệnh theo phương thức truyền thống như: phải xếp hàng lấy số thứ tự, chờ đợi lâu, khó lựa chọn bác sĩ phù hợp, phải liên hệ tới tổng đài để đặt lịch khám. Đặc biệt, nhu cầu lựa chọn bác sĩ ngày càng tăng nhưng chưa có hệ thống nào 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_31_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

hỗ trợ tốt. 

- Bác sĩ phải chịu áp lực công việc lớn khi số lượng bệnh nhân đông, việc phân bổ lịch khám chưa khoa học, đồng thời vẫn phải xử lý nhiều thủ tục hành chính ngoài chuyên môn. 

- Quản trị viên cần một hệ thống cho phép quản lý tập trung thông tin bác sĩ, bệnh nhân, dịch vụ khám bệnh, đồng thời theo dõi hoạt động của hệ thống, bảo mật và báo cáo số liệu phục vụ công tác điều hành. 

Từ những yêu cầu thực tế trên, em đề xuất hệ thống được thiết kế với **3 tác nhân chính** : 

- **Quản trị viên (Admin)** 

- **Bệnh nhân (Patient)** 

- **Bác sĩ (Doctor)** 

Các ca sử dụng chính đối với mỗi tác nhân được liệt kê trong bảng sau: 

**Bảng 3-2:** _Các ca sử dụng chính đối với mỗi tác nhân_ 

|**Tên tác nhân**|**Ca sử dụng**|
|---|---|
||Đăng ký tài khoản|
||Đăng nhập tài khoản|
||Sử dụng chatbot tư vấn|
||Xem khoa khám bệnh|
||Xem dịch vụ khám chữa bệnh|
|**Bệnh nhân**|Tìm kiếm nhanh bác sĩ|
||Đặt lịch khám chữa bệnh|
||Liên hệ tư vấn|
||Xem tin tức|
||Đánh giá bác sĩ|
||Theo dõi lịch khám chữa bệnh|
||Quản lý thống kê (Dashboard)|
||Quản lý khoa khám bệnh|
|**Quản trị viên**|Quản lý dịch vụ khám chữa bệnh|
||Quản lý bệnh nhân|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_32_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
Quản lý bác sĩ<br>Quản lý lịch làm việc<br>Quản lý lịch khám chữa bệnh<br>Quản lý tin tức<br>Quản lý đánh giá bác sĩ<br>Quản lý Banner<br>Quản lý liên hệ/hỏi đáp<br>Quản lý phân quyền<br>Xuất báo cáo thống kê bệnh nhân<br>Quản lý tài khoản<br>Quản lý bệnh nhân<br>Bác sĩ  Đăng ký lịch làm việc<br>Quản lý lịch khám chữa bệnh<br>Quản lý thống kê<br><!-- End of picture text -->

## **3.4. Phân tích các ca sử dụng của hệ thống** 

Từ bảng các ca sử dụng đối với từng tác nhân được xây dựng từ mô tả bài toán của hệ thống, có thể xây dựng biểu đồ ca sử dụng (Use Case Diagram) để minh họa tổng quan mối quan hệ giữa các tác nhân và hệ thống như sau: 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_33_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



**Hình 3-1:** Biểu đồ _ca sử dụng tổng quan của hệ thống_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_34_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.4.1. Phân tích các ca sử dụng phía quản trị viên_** 

_3.4.1.1. Phân tích ca sử dụng “Quản lý thống kê”_ 



<!-- Start of picture text -->
RN, *s. canend>><br>Quin trjvién KS<br>4 ON, ecedendos<br><!-- End of picture text -->

**Hình 3-2:** _Biểu đồ ca sử dụng “Quản lý thống kê”_ 

**Bảng 3-3:** _Bảng đặc tả ca sử dụng “Quản lý thống kê”_ 

|**Tên UseCase**|**Quản lý thống kê**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
||Cho phép quản trị viên thống kê và xuất báo cáo về|
|**Mục tiêu**|hoạt động khám chữa bệnh của bệnh viện (theo lịch<br>làm việc, lịch khám, khoa, dịch vụ, bác sĩ, bệnh<br>nhân).|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; dữ liệu bệnh nhân đã<br>tồn tại trong hệ thống.|
|**Điều kiện kết thúc**|Hệ thống hiển thị và/hoặc xuất báo cáo thống kê<br>theo yêu cầu.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn chức năng “Quản lý thống kê”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_35_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||2. Hệ thống hiển thị các tùy chọn thống kê (lịch làm<br>việc, lịch khám, khoa, dịch vụ, bác sĩ, bệnh nhân).<br>3. Quản trị viên chọn loại thống kê mong muốn.<br>4. Hệ thống xử lý và hiển thị kết quả thống kê.<br>5. Quản trị viên có thể xuất báo cáo thống kê<br>(PDF/Excel).|
|---|---|
||- Nếu không có dữ liệu thống kê trong khoảng thời<br>gian yêu cầu → Hệ thống thông báo “Không có dữ|
|**Luồng thay thế/ngoại lệ**|liệu”.<br>- Nếu lỗi kết nối CSDL → Hệ thống thông báo lỗi<br>và yêu cầu thử lại.|



**Bảng 3-4:** _Đặc tả ca sử dụng “Xuất báo cáo thống kê bệnh nhân”_ 

|**Tên UseCase**|**Xuất báo cáo thống kê bệnh nhân**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Quản trị viên xuất báo cáo chi tiết về số lượng và<br>thông tin bệnh nhân (theo thời gian, khoa, dịch vụ,<br>bác sĩ).|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; dữ liệu bệnh nhân đã<br>tồn tại trong hệ thống.|
|**Điều kiện kết thúc**|File báo cáo (PDF/Excel) được xuất thành công.|
||1. Quản trị viên chọn chức năng “Xuất báo cáo<br>thống kê bệnh nhân”.|
|**Luồng sự kiện chính**|2. Quản trị viên chọn bộ lọc<br>3. Hệ thống truy vấn dữ liệu.<br>4. Hệ thống tạo file báo cáo.<br>5. Hệ thống cung cấp báo cáo để tải về.|
||- Nếu không có dữ liệu phù hợp bộ lọc → Hệ thống|
|**Luồng thay thế/ngoại lệ**|thông báo “Không có dữ liệu phù hợp để xuất báo<br>cáo”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_36_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## _3.4.1.2. Phân tích ca sử dụng “Quản lý khoa khám bệnh”_ 



<!-- Start of picture text -->
ecinclude>}<br>: <<exteng>-*”<br>ae<br><!-- End of picture text -->

**Hình 3-3:** _Biểu đồ ca sử dụng“Quản lý khoa khám bệnh”_ 

**Bảng 3-5:** _Đặc tả ca sử dụng “Quản lý khoa khám bệnh”_ 

|**Tên UseCase**|**Quản lý khoa khám bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên thêm mới, cập nhật, xóa, tìm<br>kiếm và xem danh sách khoa khám bệnh trong hệ<br>thống.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Danh sách khoa khám bệnh được cập nhật chính xác<br>theo các thao tác của quản trị viên.|
||1. Quản trị viên chọn chức năng “Quản lý khoa<br>khám bệnh”.|
|**Luồng sự kiện chính**|2. Hệ thống hiển thị các tùy chọn: thêm mới, cập<br>nhật, xóa, xem danh sách, tìm kiếm.<br>3. Quản trị viên chọn thao tác cụ thể.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_37_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||4. Hệ thống xử lý và hiển thị kết quả tương ứng.|
|---|---|
||- Nếu dữ liệu nhập sai hoặc thiếu → Hệ thống hiển|
|**Luồng thay thế/ngoại lệ**|thị thông báo lỗi.<br>- Nếu tìm kiếm không có kết quả → Hệ thống hiển|
||thị “Không tìm thấy khoa khám bệnh”.|



**Bảng 3-6:** _Đặc tả ca sử dụng “Cập nhật khoa khám bệnh”_ 

|**Tên UseCase**|**Cập nhật khoa khám bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên chỉnh sửa thông tin của một<br>khoa đã tồn tại.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; khoa cần cập nhật đã<br>tồn tại trong hệ thống.|
|**Điều kiện kết thúc**|Thông tin khoa được chỉnh sửa và lưu vào CSDL.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn khoa cần chỉnh sửa trong danh<br>sách.<br>2. Quản trị viên thay đổi thông tin (tên khoa, mô tả,<br>vị trí).<br>3. Hệ thống kiểm tra dữ liệu.<br>4. Hệ thống lưu thông tin cập nhật.|
|**Luồng thay thế/ngoại lệ**|- Nếu dữ liệu nhập thiếu hoặc sai → Hệ thống yêu<br>cầu nhập lại.<br>- Nếu tên khoa mới trùng với tên khoa khác → Hệ<br>thống báo lỗi “Tên khoa đã tồn tại”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_38_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## _3.4.1.3. Phân tích ca sử dụng “Quản lý dịch vụ khám chữa bệnh”_ 



<!-- Start of picture text -->
=><br><!-- End of picture text -->

**Hình 3-4:** _Biểu đồ ca sử dụng “Quản lý dịch vụ khám chữa bệnh”_ 

**Bảng 3-7:** _Đặc tả ca sử dụng “Quản lý dịch vụ khám chữa bệnh”_ 

|**Tên UseCase**|**Quản lý dịch vụ khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên thêm mới, cập nhật, xóa, xem<br>danh sách và tìm kiếm dịch vụ khám chữa bệnh.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Danh sách dịch vụ được cập nhật chính xác theo thao<br>tác của quản trị viên.|
||1. Quản trị viên chọn chức năng “Quản lý dịch vụ<br>khám chữa bệnh”.|
|**Luồng sự kiện chính**|2. Hệ thống hiển thị các tùy chọn: thêm mới, cập<br>nhật, xóa,xem danh sách, tìm kiếm.<br>3. Quản trị viên chọn thao tác mong muốn.<br>4. Hệ thống xử lý và hiển thị kết quả tương ứng.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_39_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||- Nếu dữ liệu nhập sai hoặc thiếu → Hệ thống hiển|
|---|---|
|**Luồng thay thế/ngoại**|thị thông báo lỗi.|
|**lệ**|- Nếu tìm kiếm không có kết quả → Hệ thống hiển|
||thị “Không tìm thấy dịch vụ phù hợp”.|



**Bảng 3-8:** _Đặc tả ca sử dụng “Thêm mới dịch vụ khám chữa bệnh”_ 

|**Tên UseCase**|**Thêm mới dịch vụ khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Quản trị viên thêm dịch vụ khám chữa bệnh mới vào<br>hệ thống.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Dịch vụ mới được lưu vào CSDL.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn “Thêm dịch vụ khám chữa<br>bệnh”.<br>2. Nhập thông tin dịch vụ (tên dịch vụ, mô tả, chi<br>phí, khoa phụ trách).<br>3. Hệ thống kiểm tra dữ liệu.<br>4. Hệ thống lưu thông tin dịch vụ mới.|
|**Luồng thay thế/ngoại lệ**|- Nếu tên dịch vụ đã tồn tại → Hệ thống báo lỗi “Tên<br>dịch vụ đã tồn tại”.<br>- Nếu dữ liệu nhập thiếu → Hệ thống yêu cầu bổ<br>sung.|



**Bảng 3-9:** _Đặc tả ca sử dụng “Tìm kiếm dịch vụ khám chữa bệnh”_ 

|**Tên UseCase**|**Tìm kiếm dịch vụ khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Hỗ trợ quản trị viên tra cứu dịch vụ khám chữa bệnh<br>nhanh chóng theo nhiều tiêu chí.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; hệ thống có dữ liệu dịch<br>vụ.|
|**Điều kiện kết thúc**|Hệ thống hiển thị kết quả dịch vụ phù hợp với tiêu|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_40_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||chí tìm kiếm.|
|---|---|
||1. Quản trị viên chọn chức năng “Tìm kiếm dịch<br>vụ”.|
|**Luồng sự kiện chính**|2. Nhập tiêu chí tìm kiếm (tên dịch vụ, khoa khám<br>bệnh, hoặc cả hai).|
||3. Hệ thống truy vấn dữ liệu dịch vụ.|
||4. Hệ thống hiển thị danh sách kết quả.|
|**Luồng thay thế/ngoại lệ**|- Nếu không có dịch vụ phù hợp → Hệ thống hiển<br>thị thông báo “Không tìm thấy dịch vụ phù hợp”.|



## _3.4.1.4. Phân tích ca sử dụng “Quản lý bác sĩ”_ 



<!-- Start of picture text -->
sxincudess ——)<br><!-- End of picture text -->

**Hình 3-5:** _Biểu đồ ca sử dụng “Quản lý bác sĩ”_ 

**Bảng 3-10:** _Đặc tả ca sử dụng “Quản lý bác sĩ”_ 

|**Tên UseCase**|**Quản lý bác sĩ**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên thêm mới, cập nhật, xóa,<br>xem danh sách và tìm kiếm thông tin bác sĩ.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_41_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|---|---|
|**Điều kiện kết thúc**|Danh sách bác sĩ được cập nhật chính xác theo thao<br>tác của quản trị viên.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn chức năng “Quản lý bác sĩ”.<br>2. Hệ thống hiển thị các tùy chọn: thêm mới, cập<br>nhật, xóa, xem danh sách, tìm kiếm.<br>3. Quản trị viên chọn thao tác mong muốn.<br>4. Hệ thống xử lý và hiển thị kết quả.|
|**Luồng thay thế/ngoại lệ**|- Nếu dữ liệu nhập thiếu hoặc sai → Hệ thống hiển<br>thị thông báo lỗi.<br>- Nếu tìm kiếm không có kết quả → Hệ thống hiển<br>thị “Không tìm thấy bác sĩ phù hợp”.|



**Bảng 3-11:** _Đặc tả ca sử dụng “Thêm mới bác sĩ”_ 

|**Tên UseCase**|**Thêm mới bác sĩ**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên thêm một bác sĩ mới vào hệ<br>thống.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Thông tin bác sĩ mới được lưu vào CSDL.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn “Thêm mới bác sĩ”.<br>2. Nhập thông tin bác sĩ (họ tên, khoa khám bệnh,<br>dịch vụ khám bệnh, chức vụ, chức danh, số điện<br>thoại, email,…).<br>3. Hệ thống kiểm tra dữ liệu.<br>4. Hệ thống lưu thông tin bác sĩ.|
|**Luồng thay thế/ngoại lệ**|- Nếu thông tin nhập thiếu → Hệ thống yêu cầu bổ<br>sung.|



**Bảng 3-12:** _Đặc tả ca sử dụng “Tìm kiếm bác sĩ”_ 

|**Tên UseCase**||**Tìm kiếm bác sĩ**|
|---|---|---|
|**Tác nhân (Actor)**|Quản trị viên||



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_42_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|**Mục tiêu**|Hỗ trợ quản trị viên tìm kiếm bác sĩ nhanh chóng<br>theo nhiều tiêu chí (tên, mã bác sĩ, khoa khám<br>bệnh).|
|---|---|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; hệ thống có dữ liệu bác<br>sĩ.|
|**Điều kiện kết thúc**|Danh sách bác sĩ phù hợp với tiêu chí tìm kiếm<br>được hiển thị.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn chức năng “Tìm kiếm bác sĩ”.<br>2. Nhập tiêu chí tìm kiếm bác sĩ (Tìm kiếm theo mã<br>bác sĩ, tên bác sĩ, lọc theo khoa khám bệnh, lọc theo<br>dịch vụ khám chữa bệnh)<br>3. Hệ thống truy vấn dữ liệu.<br>4. Hệ thống hiển thị kết quả tìm kiếm.|
|**Luồng thay thế/ngoại lệ**|- Nếu không tìm thấy bác sĩ phù hợp → Hệ thống<br>hiển thị “Không tìm thấy bác sĩ”.|



## _3.4.1.5. Phân tích ca sử dụng “Quản lý bệnh nhân”_ 



**Hình 3-6:** _Biểu đồ ca sử dụng “Quản lý bệnh nhân”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_43_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 3-13:** _Bảng đặc tả ca sử dụng “Quản lý bệnh nhân”_ 

|**Tên UseCase**|**Quản lý bệnh nhân**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên thêm mới, cập nhật, xóa,<br>xem danh sách và tìm kiếm bệnh nhân trong hệ<br>thống.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Danh sách bệnh nhân được cập nhật chính xác theo<br>thao tác của quản trị viên.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn chức năng “Quản lý bệnh<br>nhân”.<br>2. Hệ thống hiển thị các tùy chọn: thêm mới, cập<br>nhật, xóa, xem danh sách, tìm kiếm.<br>3. Quản trị viên chọn thao tác mong muốn.<br>4. Hệ thống xử lý và hiển thị kết quả.|
|**Luồng thay thế/ngoại lệ**|- Nếu dữ liệu nhập thiếu hoặc sai → Hệ thống báo<br>lỗi.<br>- Nếu tìm kiếm không có kết quả → Hệ thống hiển<br>thị “Không tìm thấy bệnh nhân phù hợp”.|



**Bảng 3-14:** _Đặc tả ca sử dụng “Thêm mới bệnh nhân”_ 

|**Tên UseCase**|**Thêm mới bệnh nhân**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên thêm thông tin bệnh nhân<br>mới vào hệ thống.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Thông tin bệnh nhân mới được lưu vào CSDL.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn “Thêm mới bệnh nhân”.<br>2. Nhập thông tin bệnh nhân (họ tên, ngày sinh, giới<br>tính, CCCD, số thẻ BHYT, địa chỉ, số điện<br>thoại,…).|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_44_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||3. Hệ thống kiểm tra dữ liệu.|
|---|---|
||4. Hệ thống lưu thông tin bệnh nhân.|
||- Nếu thông tin nhập thiếu → Hệ thống yêu cầu bổ|
|**Luồng thay thế/ngoại lệ**|sung.<br>- Nếu CCCD hoặc số BHYT đã tồn tại → Hệ thống|
||báo lỗi.|



**Bảng 3-15:** _Đặc tả ca sử dụng “Tìm kiếm bệnh nhân”_ 

|**Tên UseCase**|**Tìm kiếm bệnh nhân**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Hỗ trợ quản trị viên tìm kiếm bệnh nhân nhanh<br>chóng theo nhiều tiêu chí (tên, CCCD, số thẻ bảo<br>hiểm, mã bệnh nhân).|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; hệ thống có dữ liệu<br>bệnh nhân.|
|**Điều kiện kết thúc**|Danh sách bệnh nhân phù hợp với tiêu chí tìm kiếm<br>được hiển thị.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn “Tìm kiếm bệnh nhân”.<br>2. Nhập tiêu chí tìm kiếm (tên, CCCD, số thẻ<br>BHYT, hoặc mã BN).<br>3. Hệ thống truy vấn dữ liệu.<br>4. Hệ thống hiển thị kết quả tìm kiếm.|
|**Luồng thay thế/ngoại lệ**|- Nếu không tìm thấy bệnh nhân phù hợp → Hệ<br>thống hiển thị “Không tìm thấy bệnh nhân”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_45_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## _3.4.1.6. Phân tích ca sử dụng “Quản lý lịch khám chữa bệnh”_ 



<!-- Start of picture text -->
ead o egeando<br>Quin tien “cating Re, cor)<br>‘ Coat) omni Cinna<br><!-- End of picture text -->

**Hình 3-7:** _Biểu đồ ca sử dụng “Quản lý lịch khám chữa bệnh”_ 

**Bảng 3-16:** _Đặc tả ca sử dụng “Quản lý lịch khám chữa bệnh”_ 

|**Tên UseCase**|**Quản lý lịch khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Quản trị viên quản lý toàn bộ lịch khám chữa bệnh:<br>xem, tìm kiếm, cập nhật trạng thái, trả kết quả khám<br>cho bệnh nhân.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Danh sách và trạng thái lịch khám chữa bệnh được<br>cập nhật chính xác.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn chức năng “Quản lý lịch khám<br>chữa bệnh”.<br>2. Hệ thống hiển thị các chức năng: Xem danh sách,<br>Tìm kiếm, Cập nhật trạng thái.<br>3. Quản trị viên chọn thao tác mong muốn.<br>4. Hệ thống xử lý và trả kết quả.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_46_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- Nếu dữ liệu không tồn tại → Hệ thống báo “Không **Luồng thay thế/ngoại lệ** tìm thấy lịch khám chữa bệnh”.. 

**Bảng 3-17:** _Đặc tả ca sử dụng “Xem danh sách lịch khám chữa bệnh”_ 

|**Tên UseCase**|**Xem danh sách lịch khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Hiển thị toàn bộ danh sách lịch khám chữa bệnh<br>trong hệ thống.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; hệ thống có dữ liệu lịch<br>khám.|
|**Điều kiện kết thúc**|Danh sách lịch khám hiển thị trên giao diện.|
||1. Quản trị viên chọn “Xem danh sách lịch khám<br>chữa bệnh”.|
|**Luồng sự kiện chính**|2. Hệ thống truy vấn dữ liệu từ CSDL.<br>3. Hệ thống hiển thị danh sách lịch khám với thông<br>tin cơ bản|
|**Luồng thay thế/ngoại lệ**|- Nếu chưa có lịch khám nào → Hiển thị “Chưa có<br>lịch khám chữa bệnh”.|



**Bảng 3-18:** _Đặc tả ca sử dụng “Tìm kiếm lịch khám chữa bệnh”_ 

|**Tên UseCase**|**Tìm kiếm lịch khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
||Hỗ trợ quản trị viên tìm kiếm lịch khám theo nhiều|
|**Mục tiêu**|tiêu chí: tên bệnh nhân, mã bệnh nhân, ngày khám,|
||tên bác sĩ, khoa khám bệnh.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; hệ thống có dữ liệu lịch<br>khám.|
|**Điều kiện kết thúc**|Hệ thống hiển thị danh sách lịch khám phù hợp với<br>tiêu chí.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn chức năng “Tìm kiếm lịch<br>khám chữa bệnh”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_47_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||2. Nhập tiêu chí tìm kiếm.<br>3. Hệ thống truy vấn dữ liệu.|
|---|---|
||4. Hệ thống hiển thị kết quả.|
|**Luồng thay thế/ngoại lệ**|- Nếu không có lịch khám nào phù hợp → Hệ thống<br>hiển thị “Không tìm thấy lịch khám”.|



**Bảng 3-19:** _Đặc tả ca sử dụng “Cập nhật trạng thái lịch khám bệnh”_ 

|**Tên UseCase**|**Cập nhật trạng thái lịch khám bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên cập nhật trạng thái của lịch<br>khám bệnh trong hệ thống.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; lịch khám tồn tại trong<br>hệ thống.|
|**Điều kiện kết thúc**|Trạng thái lịch khám được cập nhật thành công.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn lịch khám cần cập nhật.<br>2. Chọn trạng thái mới: Hủy, KH xác nhận, NV xác<br>nhận, Đã<br>thanh toán, Đã khám, Đã trả kết quả.<br>3. Hệ thống kiểm tra quy trình chuyển trạng thái.4.<br>Hệ thống lưu và hiển thị trạng thái mới.|
|**Luồng thay thế/ngoại lệ**|- Nếu không có lịch khám nào phù hợp → Hệ thống<br>hiển thị “Không tìm thấy lịch khám”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_48_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## _3.4.1.7. Phân tích ca sử dụng “Quản lý lịch làm việc”_ 



<!-- Start of picture text -->
<sinclude>> “<br><!-- End of picture text -->

**Hình 3-8:** _Biểu đồ ca sử dụng “Quản lý lịch làm việc”_ 

**Bảng 3-20:** _Đặc tả ca sử dụng “Quản lý lịch làm việc”_ 

|**Tên UseCase**|**Quản lý lịch làm việc**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Quản lý lịch làm việc của bác sĩ: xem, tìm kiếm,<br>thêm mới, xóa.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; hệ thống có dữ liệu bác<br>sĩ/khoa.|
|**Điều kiện kết thúc**|Lịch làm việc được hiển thị/cập nhật chính xác theo<br>thao tác.|
|**Luồng sự kiện chính**|1) Chọn “Quản lý lịch làm việc”.<br>2) Hệ thống hiển thị các chức năng: Xem danh sách,<br>Tìm kiếm, Thêm mới, Xóa.<br>3) Quản trị viên chọn chức năng mong muốn.<br>4) Hệ thống xử lý và trả kết quả.|
|**Luồng thay thế/ngoại lệ**|- Không có dữ liệu phù hợp → thông báo “Không<br>có lịch làm việc”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_49_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 3-21:** _Đặc tả ca sử dụng “Xem danh sách lịch làm việc”_ 

|**Tên UseCase**|**Xem danh sách lịch làm việc**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Hiển thị đầy đủ lịch làm việc của bác sĩ.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; có dữ liệu lịch làm việc.|
|**Điều kiện kết thúc**|Danh sách lịch làm việc được hiển thị (có thể phân<br>trang/sort).|
|**Luồng sự kiện chính**|1) Chọn “Xem danh sách lịch làm việc”.<br>2) Hệ thống truy xuất CSDL.<br>3) Hiển thị các trường cơ bản: Mã lịch, Bác sĩ,<br>Khoa, Ngày, Ca/khung giờ, Trạng thái|
|**Luồng thay thế/ngoại lệ**|- Chưa có lịch → thông báo “Chưa có lịch làm<br>việc”.|



**Bảng 3-22:** _Đặc tả ca sử dụng “Tìm kiếm lịch làm việc”_ 

|**Tên UseCase**|**Tìm kiếm lịch làm việc**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Tìm nhanh lịch làm việc theo nhiều tiêu chí.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập; có dữ liệu lịch làm việc.|
|**Điều kiện kết thúc**|Hiển thị danh sách lịch trùng khớp tiêu chí.|
|**Luồng sự kiện chính**|1) Chọn “Tìm kiếm lịch làm việc”.<br>2) Nhập tiêu chí (một hoặc nhiều): mã bác sĩ, tên<br>bác sĩ, ngày làm việc (hoặc khoảng ngày).<br>3) Hệ thống truy vấn CSDL.<br>4) Hiển thị kết quả phù hợp (giữ nguyên các cột như<br>phần xem danh sách).|
|**Luồng thay thế/ngoại lệ**|- Không có kết quả → thông báo “Không tìm thấy<br>lịch làm việc phù hợp”.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_50_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## _3.4.1.8. Phân tích ca sử dụng “Quản lý tin tức”_ 



<!-- Start of picture text -->
<cinclude?><br>f xxexteno> |<br>j <extend>><br>2xpxtend>> Gosia)<br><!-- End of picture text -->

**Hình 3-9:** _Biểu đồ ca sử dụng “Quản lý tin tức”_ 

**Bảng 3-23:** _Đặc tả ca sử dụng “Quản lý tin tức”_ 

|**Tên UseCase**|**Quản lý tin tức**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên quản lý các tin tức của bệnh<br>viện: thêm mới, sửa, xóa và xem danh sách tin tức.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Danh sách tin tức được cập nhật chính xác theo thao<br>tác của quản trị viên.|
|**Luồng sự kiện chính**|1. Quản trị viên chọn chức năng “Quản lý tin tức”.<br>2. Hệ thống hiển thị các tùy chọn: Xem danh sách,<br>Thêm mới, Sửa, Xóa.<br>3. Quản trị viên chọn chức năng mong muốn.<br>4. Hệ thống xử lý và hiển thị kết quả.|
|**Luồng thay thế/ngoại lệ**|- Nếu dữ liệu nhập sai hoặc thiếu khi thêm/sửa →<br>Hệ thống yêu cầu nhập đầy đủ dữ liệu.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_51_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## _3.4.1.9. Phân tích ca sử dụng “Quản lý vai trò người dùng”_ 



<!-- Start of picture text -->
eeinctudess”<br>a — Gam)<br>Seen<br>“sy, cenceen<br><!-- End of picture text -->

**Hình 3-10:** _Biểu đồ ca sử dụng “Quản lý vai trò người dùng”_ 

**Bảng 3-24:** _Đặc tả ca sử dụng “Quản lý vai trò người dùng”_ 

|**Tên UseCase**|**Quản lý vai trò người dùng**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Cho phép quản trị viên quản lý các vai trò trong hệ<br>thống: xem danh sách, cập nhật và xóa vai trò người<br>dùng.|
|**Điều kiện tiên quyết**|Quản trị viên đã đăng nhập hệ thống.|
|**Điều kiện kết thúc**|Các vai trò người dùng được hiển thị/cập nhật/xóa<br>đúng theo thao tác của quản trị viên.|
||1. Quản trị viên chọn chức năng “Quản lý vai trò<br>người dùng”.|
|**Luồng sự kiện chính**|2. Hệ thống hiển thị các tùy chọn cho quản trị viên<br>3. Quản trị viên chọn chức năng mong muốn.<br>4. Hệ thống xử lý và hiển thị kết quả tương ứng.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_52_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- Nếu dữ liệu nhập thiếu/sai khi cập nhật → Hệ **Luồng thay thế/ngoại lệ** thống yêu cầu nhập lại. 

## **_3.4.2. Phân tích các ca sử dụng phía bệnh nhân_** 

## _3.4.2.1. Phân tích ca sử dụng “Sử dụng Chatbot tư vấn”_ 



<!-- Start of picture text -->
_ “ ‘9 kinchia bf<br>O — aire Eocing din guyiin  teakleh 94Khoy  v4 even S(Ag:<br>in i be<br>Béah whi SN geome Sia<br>So<<erings> Fringdin kim c40,.-°°°<<even5>> ciru gla tiém kim<br>: ich vy chia bfah ‘cae deh vy at<br>— Fgh Khim eo) sre. (mihi "enc _(Tim theo egg tec?<br>. tring bie tinbiedt Fe ‘hit ian<br>. felch<br>., Weekhioa cia tréaQ)—<cincuies> feoOatS e ens>> >)<br>Airacisbjah ginKMID),—<e>><br>cia biest<br><!-- End of picture text -->

**Hình 3-11:** _Biểu đồ ca sử dụng “Sử dụng Chatbot tư vấn”_ 

**Bảng 3-25:** _Đặc tả ca sử dụng “Sử dụng Chatbot tư vấn”_ 

|**Tên UseCase**|**Sử dụng Chatbot tư vấn**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
|**Mục tiêu**|Bệnh nhân trao đổi với Chatbot để: tìm lịch khám còn<br>trống theo bác sĩ/dịch vụ, tra cứu giá khám, thông tin<br>khám bệnh,…|
|**Điều kiện tiên quyết**|Hệ thống Chatbot hoạt động; có kết nối tới<br>Function/DB lịch khám, danh mục dịch vụ, giá dịch<br>v. Bệnh nhân truy cập ứng dụng/web.|
|**Điều kiện kết thúc**|Chatbot trả lời đúng nhu cầu (kết quả lịch trống/giá<br>khám) hoặc hướng dẫn bước tiếp theo (đặt lịch, liên<br>hệ…).|
||1) Bệnh nhân mở khung chat và đặt câu hỏi tự nhiên.|
|**Luồng sự kiện chính**|2) Chatbot NLP nhận diện intent (tìm lịch bác sĩ/dịch<br>vụ, tra giá) và trích entity (tên bác sĩ, khoa, dịch vụ,|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_53_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||ngày…).<br>3) Chatbot gọi Function/DB tương ứng.<br>4) Chatbot hiển thị kết quả ngắn gọn + tùy chọn hành<br>động tiếp (đặt lịch, xem thêm).|
|---|---|
|**Luồng thay thế/ngoại lệ**|- Không hiểu intent → Chatbot hỏi lại/đưa gợi ý.<br>- Thiếu entity quan trọng → Chatbot hỏi bổ sung.<br>- Không có lịch trống/không có giá → Thông báo rõ<br>ràng và gợi ý lựa chọn thay thế (khung giờ/ngày<br>khám khác).<br>- Chatbot bị lỗi → Hiển thị thông báo xin lỗi, vui lòng<br>thử lại sau.|



**Bảng 3-26:** _Đặc tả ca sử dụng “Tìm lịch khám còn trống theo bác sĩ”_ 

|**Tên UseCase**|**Tìm lịch khám còn trống theo bác sĩ**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
|**Mục tiêu**|Tìm các khung giờ còn trống của một bác sĩ theo<br>ngày/tuần.|
|**Điều kiện tiên quyết**|Danh mục bác sĩ và lịch làm việc đồng bộ; Chatbot<br>truy cập được bảng lịch làm việc của bác sĩ.|
|**Điều kiện kết thúc**|Danh sách slot trống (ngày/giờ) của bác sĩ được hiển<br>thị.|
|**Luồng sự kiện chính**|1) Bệnh nhân nhắn: “Cho tôi lịch trống của bác sĩ A<br>ngày cụ thể”.<br>2) Chatbot nhận intent tìm lịch khám, tên bác sĩ,<br>ngày/trạng từ  chỉ thời gian theo nhu cầu khám chữa<br>bệnh của bệnh nhân.<br>3) Gọi hàm kiểm tra lịch làm việc − lịch đã đặt⇒<br>tính slot trống.<br>4) Trả về các lịch khám còn trống của bác sĩ trong<br>thời gian được yêu cầu.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_54_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||- Thiếu bác sĩ/ngày → hỏi bổ sung.|
|---|---|
|**Luồng thay thế/ngoại lệ**|- Không có slot trống → trả về thông báo không còn<br>slot.|
||- Tên bác sĩ không tồn tại → gợi ý bác sĩ gần đúng.|



**Bảng 3-27:** _Đặc tả ca sử dụng “Tìm kiếm lịch khám còn trống theo dịch vụ khám bệnh”_ 

|**Tên UseCase**|**Tìm lịch khám còn trống theo dịch vụ khám bệnh**|
|---|---|
|**Tác nhân (Actor)**|Quản trị viên|
|**Mục tiêu**|Tìm lịch khám còn trống các bác sĩ khám dịch vụ chữa<br>bệnh theo ngày/tuần cụ thể.|
|**Điều kiện tiên quyết**|Danh mục**dịch vụ ↔ khoa ↔ bác sĩ**được mapping;<br>Hàm tìm lịch hoạt động.|
|**Điều kiện kết thúc**|Danh sách slot trống cho dịch vụ (kèm bác sĩ phụ trách<br>nếu có) được hiển thị.|
|**Luồng sự kiện chính**|1) Bệnh nhân nhắn: “Có lịch trống dịch vụ A vào thời<br>gian (thời gian cụ thể) không?”.<br>2) Chatbot nhận intent tìm lịch khám còn trống theo<br>tên dịch vụ, ngày khám.<br>3) Truy vấn các bác sĩ/dịch vụ khám đó → hợp nhất<br>lịch trống theo tiêu chí.<br>4) Hiển thị slot trống (bác sĩ, ngày/giờ, phòng).|
|**Luồng thay thế/ngoại**<br>**lệ**|- Dịch vụ không tồn tại/không rõ → gợi ý dịch vụ gần<br>đúng.<br>- Không có lịch trống → đề xuất ngày khác.|



**Bảng 3-28:** _Đặc tả ca sử dụng “Tra cứu giá tiền khám bệnh của bác sĩ”_ 

|**Tên UseCase**|**Tra cứu giá tiền khám bệnh của bác sĩ**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
||Cho phép bệnh nhân tra cứu giá tiền khám bệnh của|
|**Mục tiêu**|bác sĩ (Giá tiền này phụ thuộc vào chức danh của bác|
||sĩ trong khoa)|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_55_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
Điều kiện tiên quyết  Bảng giá được cấu hình (theo bác sĩ)<br>Chatbot hiển thị mức giá/biểu phí của bác sĩ tương<br>Điều kiện kết thúc<br>ứng<br>1) Bệnh nhân nhắn: “Giá khám của bác sĩ A là bao<br>nhiêu?”.<br>2) Chatbot nhận intent tìm giá khám bác sĩ/dịch vụ<br>Luồng sự kiện chính<br>3) Truy vấn bảng giá theo ưu tiên: (bác sĩ + dịch vụ)<br>→ (bác sĩ chung) → (giá dịch vụ chuẩn).<br>4) Trả về giá và ghi chú<br>- Không tìm thấy tên bác sĩ/dịch vụ → hiển thị giá<br>Luồng thay thế/ngoại lệ<br>khám dịch vụ/bác sĩ gần nhất.<br><!-- End of picture text -->

## _3.4.2.2. Phân tích ca sử dụng “Xem khoa khám bệnh”_ 



<!-- Start of picture text -->
O ‘Kem thongkhoa  tinkham tongbénh quan ve<br><<extend>><br>Ben ahin Xem khoa kham bénh Soe<br>See ss sesextend>>“+... (Kem théngKhoa tinkhém cdc  bénhbie si thuge<br>wa chon cdc bac si trong khoa<br>dé dat lich kham<br><!-- End of picture text -->

**Hình 3-12:** _Biểu đồ ca sử dụng “Xem khoa khám bệnh”_ 

**Bảng 3-29:** _Đặc tả ca sử dụng “Xem khoa khám bệnh”_ 

|**Tên UseCase**|**Xem khoa khám bệnh**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
||Cho phép bệnh nhân xem thông tin tổng quan về|
|**Mục tiêu**|các khoa khám bệnh, thông tin bác sĩ trong khoa và<br>lựa chọn bác sĩ để đặt lịch khám.|
||Bệnh nhân đã truy cập hệ thống (web/app). Dữ liệu|
|**Điều kiện tiên quyết**|khoa và bác sĩ đã được quản trị viên cập nhật trong<br>CSDL.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_56_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|**Điều kiện kết thúc**|Thông tin khoa khám bệnh và danh sách bác sĩ được<br>hiển thị, bệnh nhân có thể chọn bác sĩ để tiến hành<br>đặt lịch.|
|---|---|
|**Luồng sự kiện chính**|1. Bệnh nhân chọn chức năng “Xem khoa khám<br>bệnh”.<br>2. Hệ thống hiển thị danh sách các khoa khám bệnh.<br>3. Bệnh nhân chọn một khoa cụ thể.<br>4. Hệ thống hiển thị thông tin tổng quan về khoa,<br>danh sách bác sĩ thuộc khoa.<br>5. Bệnh nhân có thể chọn bác sĩ trong khoa để<br>chuyển sang UC “Đặt lịch khám”.|
|**Luồng thay thế/ngoại lệ**|- Nếu chưa có dữ liệu khoa → Hệ thống hiển thị<br>thông báo<br>“Chưa có thông tin khoa khám bệnh”.<br>- Nếu khoa chưa có bác sĩ nào → Hiển thị thông báo<br>“Chưa<br>có bác sĩ trong khoa này”.|



## _3.4.2.3. Phân tích ca sử dụng “Xem dịch vụ khám chữa bệnh”_ 



<!-- Start of picture text -->
O ‘Kemdich thingvy khamtia tagchira quanbénh ve<br><<enen>> SS<br>cocina<br>Bénh nhan bénh bénk oss.“ (Kem thong tin ede bite si kim<br>oa Scene pene<br>aya chon cac bac si kham dich<br>vu dé dit lich kham<br><!-- End of picture text -->

**Hình 3-13:** _Biểu đồ ca sử dụng “Xem dịch vụ khám chữa bệnh”_ 

**Bảng 3-30:** _Đặc tả ca sử dụng “Xem dịch vụ khám chữa bệnh”_ 

|**Tên UseCase**|**Xem dịch vụ khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
|**Mục tiêu**|Cho phép bệnh nhân xem thông tin tổng quan về|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_57_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||các dịch vụ khám chữa bệnh, thông tin bác sĩ thực<br>hiện dịch vụ và lựa chọn bác sĩ để đặt lịch khám|
|---|---|
|**Điều kiện tiên quyết**|Bệnh nhân đã truy cập hệ thống (web/app). Dữ liệu<br>dịch vụ khám và bác sĩ đã được quản trị viên cập<br>nhật trong CSDL.|
|**Điều kiện kết thúc**|Hệ thống hiển thị thông tin dịch vụ và danh sách<br>bác sĩ, bệnh nhân có thể chọn bác sĩ để đặt lịch.|
|**Luồng sự kiện chính**|1. Bệnh nhân chọn chức năng “Xem dịch vụ khám<br>chữa bệnh”.<br>2. Hệ thống hiển thị danh sách các dịch vụ khám<br>chữa bệnh.<br>3. Bệnh nhân chọn một dịch vụ cụ thể.<br>4. Hệ thống hiển thị thông tin tổng quan về dịch vụ,<br>danh sách<br>bác sĩ thực hiện dịch vụ.<br>5. Bệnh nhân có thể chọn bác sĩ để chuyển sang UC<br>“Đặt lịch khám”.|
|**Luồng thay thế/ngoại lệ**|- Nếu chưa có dữ liệu dịch vụ → Hệ thống hiển thị<br>thông báo “Chưa có dịch vụ nào”.|



_3.4.2.4. Phân tích ca sử dụng “Tìm kiếm nhanh bác sĩ”_ 



<!-- Start of picture text -->
O _-{. Tim kiém theo tén bac si<br><cextend>>7"<br>“a Wy “exten<br>im kiém nhanh bie sb<br>Bénh nhan Kham chitabénh 77> --. =<br>S<<extend>> Loc theo khoa kham bénh<br>‘Hoe theo dich vy khim ehira<br>bénh<br><!-- End of picture text -->

**Hình 3-14:** _Biểu đồ ca sử dụng “Tìm kiếm nhanh bác sĩ khám chữa bệnh”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_58_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 3-31:** _Đặc tả ca sử dụng “Tìm kiếm nhanh bác sĩ khám chữa bệnh”_ 

|**Tên UseCase**|**Tìm kiếm nhanh bác sĩ khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
|**Mục tiêu**|Cho phép bệnh nhân nhanh chóng tìm kiếm bác sĩ<br>để đặt lịch khám theo nhiều tiêu chí khác nhau (tên<br>bác sĩ, khoa khám bệnh, dịch vụ khám chữa bệnh).|
|**Điều kiện tiên quyết**|Bệnh nhân đã truy cập hệ thống (web/app). Thông<br>tin bác sĩ, khoa, dịch vụ đã tồn tại trong CSDL.|
|**Điều kiện kết thúc**|Hệ thống hiển thị danh sách bác sĩ phù hợp với tiêu<br>chí tìm kiếm, kèm tùy chọn đặt lịch.|
|**Luồng sự kiện chính**|1. Bệnh nhân chọn chức năng “Tìm kiếm nhanh bác<br>sĩ khám chữa bệnh”.<br>2. Hệ thống hiển thị các tiêu chí tìm kiếm: theo tên<br>bác sĩ, theo khoa, theo dịch vụ.<br>3. Bệnh nhân nhập tiêu chí tìm kiếm.<br>4. Hệ thống truy vấn CSDL.<br>5. Hệ thống hiển thị danh sách bác sĩ phù hợp, kèm<br>thông tin cơ bản (họ tên, khoa, dịch vụ, lịch trống).|
|**Luồng thay thế/ngoại lệ**|- Nếu không có kết quả phù hợp → Hiển thị “Không<br>tìm thấy bác sĩ nào phù hợp”.|



_3.4.2.5. Phân tích ca sử dụng “Đặt lịch khám chữa bệnh”_ 



<!-- Start of picture text -->
oO A Lyga chon khoa khim bénh<br>Benh wh ‘Dat lich kim chira) 7<br>a bénh ia nduuseof E¥# chon dichbeakvy khdim chika)<br>‘<br>‘Liya chon Ijeh khim phit hep<br><!-- End of picture text -->

**Hình 3-15:** _Biểu đồ ca sử dụng“Đặt lịch khám chữa bệnh”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_59_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 3-32:** _Đặc tả ca sử dụng “Đặt lịch khám chữa bệnh”_ 

|**Tên UseCase**|**Đặt lịch khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
|**Mục tiêu**|Cho phép bệnh nhân đặt lịch khám chữa bệnh theo<br>khoa, dịch vụ, bác sĩ và chọn lịch khám phù hợp.|
|**Điều kiện tiên quyết**|Bệnh nhân đã đăng nhập hệ thống. CSDL đã có<br>thông tin khoa, dịch vụ, bác sĩ và lịch làm việc.|
|**Điều kiện kết thúc**|Lịch khám được đặt thành công và lưu trong hệ<br>thống, bệnh nhân nhận được xác nhận.|
|**Luồng sự kiện chính**|1. Bệnh nhân chọn chức năng “Đặt lịch khám chữa<br>bệnh”.<br>2. Hệ thống hiển thị các tùy chọn: chọn khoa khám<br>bệnh, chọn dịch vụ khám chữa bệnh, chọn bác sĩ<br>mong muốn, chọn lịch khám phù hợp.<br>3. Bệnh nhân lần lượt thực hiện các bước lựa chọn.<br>4. Hệ thống kiểm tra tính khả dụng của lịch khám.<br>5. Hệ thống lưu thông tin lịch khám và gửi xác nhận<br>cho bệnh nhân.|
|**Luồng thay thế/ngoại lệ**|- Nếu bác sĩ không có lịch làm việc → Hiển thị<br>thông báo bác sĩ chưa đăng ký lịch làm việc.<br>- Nếu khung giờ đã được đặt kín → Hệ thống thông<br>báo để bệnh nhân chọn khung giờ khác.|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_60_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## _3.4.2.6. Phân tích ca sử dụng “Theo dõi lịch khám chữa bệnh”_ 



<!-- Start of picture text -->
‘Theo doi tién 49 kham chira<br>‘én trén hé thong.<br><<inctudes” + ecentend>> ‘Theo<br>oO - rheo dai tién 49 kham chira\, - bénh giridai tiénvé Email69 khimbénh chira nhan<br>Béab ohin  Sentene ‘liy lich khim.  chita bénh: Theo dai‘qua tién Ch a }tbotlich Khim<br>.<br>7 <<ertend>><br>as<br><!-- End of picture text -->

**Hình 3-16:** _Biểu đồ ca sử dụng “Theo dõi lịch khám chữa bệnh”_ 

**Bảng 3-33:** _Đặc tả ca sử dụng “Theo dõi lịch khám chữa bệnh”_ 

|**Tên UseCase**|**Theo dõi lịch khám chữa bệnh**|
|---|---|
|**Tác nhân (Actor)**|Bệnh nhân|
|**Mục tiêu**|Cho phép bệnh nhân theo dõi tiến độ khám chữa<br>bệnh, hủy lịch, xem thông tin chi tiết và nhận kết<br>quả khám.|
|**Điều kiện tiên quyết**|Bệnh nhân đã đăng nhập hệ thống; hệ thống có dữ<br>liệu lịch khám và tiến độ xử lý.|
|**Điều kiện kết thúc**|Bệnh nhân xem được tiến độ, thông tin lịch khám<br>và nhận kết quả khám (nếu có).|
|**Luồng sự kiện chính**|1. Bệnh nhân chọn chức năng “Theo dõi lịch khám<br>chữa bệnh”.<br>2. Hệ thống hiển thị danh sách lịch khám của bệnh<br>nhân.<br>3. Bệnh nhân có thể:<br>• Theo dõi tiến độ khám chữa bệnh (trên hệ thống<br>hoặc qua email hoặc qua Chatbot).<br>• Hủy lịch khám chữa bệnh (Trong trường hợp<br>trạng thái lịch khám là “Tiếp nhận”)|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_61_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
• Xem thông tin chi tiết lịch khám.<br>• Nhận kết quả khám chữa bệnh khi hoàn tất.<br>4. Hệ thống xử lý và cập nhật kết quả theo yêu<br>cầu.<br>- Nếu lịch khám đã hoàn tất → Hệ thống hiển thị<br>thông báo<br>“Đã trả kết quả” và cung cấp kết quả.<br>- Nếu bệnh nhân đã xác nhận lịch khám → Hệ thống<br>không cho phép bệnh nhân huỷ lịch khám<br>Luồng thay thế/ngoại lệ<br>- Nếu không có lịch khám nào → Hệ thống hiển thị<br>“Bạn<br>chưa có lịch khám nào”.<br>- Lỗi kết nối/email không gửi được → Hệ thống<br>thông báo lỗi và gợi ý thử lại.<br><!-- End of picture text -->

## **_3.4.3. Phân tích các ca sử dụng phía bác sĩ_** 

## _3.4.3.1. Phân tích ca sử dụng “Quản lý bệnh nhân”_ 



<!-- Start of picture text -->
<<include>>””<br>a<br><<extend>><br>“\cextond>> ">>.<br>M <<extend>><br>Comin—<br>SS. <cextond>”<br><!-- End of picture text -->

**Hình 3-17:** _Biểu đồ ca sử dụng “Quản lý bệnh nhân”(phía bác sĩ)_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_62_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- _3.4.3.2. Phân tích ca sử dụng “Quản lý lịch khám chữa bệnh”_ 



<!-- Start of picture text -->
<sincude>?”<br>eo <eten> <cenen<br>Rea or Retent>><br>ici<br>Bacsi ‘ “Sesextend>> ne <<evtent>><br><!-- End of picture text -->

**Hình 3-18:** _Biểu đồ ca sử dụng “Quản lý lịch khám chữa bệnh”(Phía bác sĩ)_ 

- _3.4.3.3. Phân tích ca sử dụng “Quản lý lịch làm việc”_ 



<!-- Start of picture text -->
<<incude>>”<br>oo Seextend>><br>NON _ssinclude>><br>BN<br>Bac si SS geexdente Site<br>Ss<cextend>S<br><!-- End of picture text -->

**Hình 3-19:** _Biểu đồ ca sử dụng “Quản lý lịch làm việc”(Phía bác sĩ)_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_63_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- _3.4.3.4. Phân tích ca sử dụng “Quản lý tài khoản”_ 



<!-- Start of picture text -->
<<include>”<br>;<br>oo Comin)<br>~"S<extend>><br>*esextend>><br>Bac si wee<br><!-- End of picture text -->

**Hình 3-20:** _Biểu đồ ca sử dụng “Quản lý tài khoản”(Phía bác sĩ)_ 

## **3.5. Phân tích một số biểu đồ tuần tự chính của hệ thống** 

Biểu đồ tuần tự (Sequence Diagram) là công cụ UML dùng để mô tả quá trình tương tác theo trình tự thời gian giữa các tác nhân bên ngoài với các đối tượng trong hệ thống. Thông qua biểu đồ tuần tự, ta có thể thấy rõ thứ tự các thông điệp được gửi đi – nhận lại, đồng thời minh họa cách hệ thống xử lý một chức năng cụ thể từ khi người dùng gửi yêu cầu đến khi hệ thống phản hồi. 

Trong hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot tư vấn, các biểu đồ tuần tự được xây dựng nhằm mô tả những ca sử dụng quan trọng và điển hình. Các biểu đồ này không chỉ giúp hiểu rõ quy trình hoạt động, mà còn là cơ sở quan trọng để thiết kế chi tiết, triển khai và kiểm thử hệ thống. 

Cụ thể, các biểu đồ tuần tự được phân tích trong phần này bao gồm: đăng ký, đăng nhập, sử dụng chatbot tư vấn, tìm kiếm bác sĩ, đặt lịch khám chữa bệnh, đánh giá bác sĩ, gửi liên hệ phản hồi, đăng ký lịch làm việc của bác sĩ, quản lý lịch khám chữa bệnh, thêm mới khoa khám bệnh, thêm mới bác sĩ, tìm kiếm bệnh nhân, và tìm kiếm lịch khám bệnh. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_64_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.1. Biểu đồ tuần tự cho ca sử dụng “Đăng ký tài khoản”_** 



<!-- Start of picture text -->
Neuiidng<br>fa(Binh abn) [ssi tence<br>1. Chon chic ning ding kj<br>enn: Forming}<br>‘3. Nhip thing tint oda, ch ahin i<br>4.Giiydu cu ding ky jl<br>[at ) (Kid tra tring CCCDSé thé BEYT]<br>4, Kiem tra tring thing tin (CCDS thd BHYT)<br>6 Ketqui kiém tr<br>[ u ) {Thing tin bi tring hoc king hep 1) ‘ta Tri bi chi tet (field, message) q<br>‘ia, Hida thi thing bio Mi (error message) | [©°°7-"°"™™ cree .<br>Ship i thing Gin H<br>10a. Git lai yu ci dingky (retry)<br>Quay laibude § dé kid tra<br>(Thing tin hop |<br>‘Tb. Tao ti khoin (hash mit kh, sinh wser_code)<br>Sh. Lam hgtin hin cng<br>10, Thinghebidingze i 4h. Tri ket qui ok<br>aon hin cng (acess message)<br><!-- End of picture text -->

**Hình 3-21:** _Biểu đồ tuần tự cho ca sử dụng “Đăng ký tài khoản”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_65_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.2. Biểu đồ tuần tự cho ca sử dụng “Đăng nhập”_** 



<!-- Start of picture text -->
‘Ngwir dutyABen nin) co<br>1. Chon chic ningding ip<br>‘2-H hi Form dingohip 1<br>2. Nhpthing in hoi mith vnc ing hip ere Peso) Thm User theo thingtin ding ip<br>6 Tr User(pussord_bash tran thi boc NULL<br>alt) | (Khing tontu bode mit hin si) "Trt:Ti kin bing tu ta’Ti Khoi<br>Su, Hi hi thg bio i (error mesa) Tocmit hn Lng dang<br>9a. Nbip lai théng tn ding whip<br>— ‘We. Gili yé ci ing mip (retry) +!<br>(Quay lai bude § dé kiem tra<br>(Tin bc ich 7.Tr i: rng hit in hing co<br>$b. hing bio tng hp ding uhip j<br>thai ai hod (error messaze)<br>x. Quay li io dién ding whip<br>10, ri dn ia Lich ost<br>‘ait kon<br>img whip hop I] ‘7c. Cip abit last Joga<br>10c. ok. Tri hit qui OK<br>von thanThing biocing (sucess ding nh message)tii }« H<br><!-- End of picture text -->

**Hình 3-22:** _Biểu đồ tuần tự cho ca sử dụng “Đăng nhập”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_66_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.3. Biểu đồ tuần tự cho ca sử dụng “Sử dụng chatbot tư vấn”_** 



<!-- Start of picture text -->
‘evi ding (Béahahin)<br>Twp ) (evidingipavii ci<br>I | Giicinkitevia iiacen, sin i)<br>4. Thin cinith cha i)<br>4. Roger (Thich tint, ni, ayer)<br>| Tray vin rit ate, ees, especies)<br>‘Gch Khim(Ket conqui traytring thing vi (ichtm i mm gc bee,bic, ch va)<br>alt / acting ng aij cin<br>Sa Bia hp ca<br>(fCh ol] tity duty ey<br>————eTC~<br>(Quay lai bic § dé kim tra<br>"inc ca Try hh ing H H H<br>Sb Ti citi rte) 7b.Chép template, chin entscontent<br>« ‘Phin bei mew dans i :<br><!-- End of picture text -->

**Hình 3-23:** _Biểu đồ tuần tự  cho ca sử dụng “Sử dụng Chatbot tư vấn”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_67_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.4. Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm nhanh bác sĩ” (phía trang người dùng)_** 



<!-- Start of picture text -->
i ee<br>Newii ding (bénh nin)<br>1. Chon chi ning "Tim én ahaa bic”<br>‘ hues iad incerta ay] H<br>| .Niptabi ste how, dich Kh ah i<br>4. Giri yéuci tim ern Try vin thing in bic tn hou dch vw hin)<br>|, 6 Tri ket quibic si phi hop i)<br>ait (Rng im tybcs pt bop] .<br>____ Tr ing tim hy cs phi hp<br>St Trivé kit qui king im ths bic spi bop<br>4. Nhip atin bic stoi Khoi vu Kim Dinh 1a.Gita yacht iets) 4<br>(Quay lai bua 5 dé kiem tra<br>(im ty cp bl ‘7h Tri dtquibic s+ ich lim ge<br>Sev Tei hitachikop H<br>9h. Chon bic side rem chi i dt ch i<br>10b, Dida burg dntrang chi titbic stich H<br><!-- End of picture text -->

**Hình 3-24:** _Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm nhanh bác sĩ” (phía trang người dùng)_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_68_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.5. Biểu đồ tuần tự cho ca sử dụng “Đặt lịch khám chữa bệnh”_** 



<!-- Start of picture text -->
Newii ding (béah nhin) DB Schedne<br>1 Timi bic pi bop (theo ou vi ich va him bs 1 iinca° imbiest 4. Truyvda anh sich bic ph bop<br>. Rd gai dan sich ict i<br>_ STrivé danhsich bic sich Dab hin<br>‘ 6a th bcs mong main<br>1. Chga bic svi ag him mong $i yuccacai sebics<br>il cs train cick<br>UL Trivett M0. gui tray vim ich im vic ci cst<br>12 ith limicin ic sfchink hin cen vide<br>13. Choo ich kin mong moda a<br>14 Gi yd ci intra ca hi ci rng 15,Kod tra trang thi ca hin<br>| 16.Két qi im tra trang thi (Cntring) |<br>‘7a. Tri thing bio i (ca him i dy ch’)<br>1H thei yn ci chu bg<br>194. Chon gi him tic } Givin ery (Quay lai boc 15 dékiem tra<br>(Cai td<br>co. 2T0-Biathi<br>15%, for ip hg cnn<br>Nipthing tin i nin 29. Gi thing tn itch ‘0b. Lo thingtinit ich<br>. . 21 thin cng<br>2. Thing bi dt ich think cng (acces message) sec, 22 Nicitic thin cng<br><!-- End of picture text -->

**Hình 3-25:** _Biểu đồ tuần tự cho ca sử dụng “Đặt lịch khám chữa bệnh”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_69_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**_3.5.6. Biểu đồ tuần tự cho ca sử dụng “Đăng ký lịch làm việc” của bác sĩ_** 



<!-- Start of picture text -->
0<br>qT 7h DB ses<br>(Quin tri/\ ieuBie st a“1 Ee’<br>1.Chom chit ning "him michlim vide” | H<br>Me ‘Hi ci form ing lich lim vie :<br>Chon bic sng im vi, ca kh, 36 BN tid | H<br>4 Git yin ci tao lich lim vide H<br>5. Kim ta thng tin bic vi ch am il rng ip<br>46. Ket qui kiémtra(Tmt, cha ci)<br>[ a) (Di dingy Khim] ‘a Tri thing bio i H<br>By "Lich im vig ido ding by” H<br>“ Su. Ha thi thing bi i Geneneee eh am ie dg ding.<br>9h. Np hing ine a vie 10a. itywe H<br>chu idm te (try) H<br>{ (Quay lai bus § kgm tra<br>"ha gi ikitn 7 saaseeeceumeaieaueameeaeaa macaaialals H<br>H ToL lich am ie H<br>Sb Tri ket qui Ok ‘$8, Lathcng lich lm vide H<br>| ib Thiag bi ing ihi i inh cing<br><!-- End of picture text -->

**Hình 3-26:** _Biểu đồ tuần tự cho ca sử dụng “Đăng ký lịch làm việc” của bác sĩ_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_70_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**_3.5.7. Biểu đồ tuần tự cho ca sử dụng “Cập nhật trạng thái lịch khám chữa bệnh”_** 



<!-- Start of picture text -->
(ui tri/\ies BesingCouroler. DBBoing'<br>1. Cho chic ning "Qui ch im chin ih” 2 Tithing inh hich bia ‘viva iti 1<br>‘deg dn sic kin u<br>S Trivddaoschkhin<br>| Ti dich ki itr hil tw<br>1. ehittrang hi ici ic on $8. Giiyucin<br>ip ahit Goin tates) $.cipmttrgitmagn da a<br>k 6 Cipabit hin cing i]<br>at) (rang thi mi = Bi tanh tia] 1a Sihpli ing thi chi bah i<br>1a Tri plil ding I 10a Lapin ihcng |bd<br>ia ath ding vic pipas ding<br>Ee eae i, isc hin inp igiit<br>Tian ti iit) ii ip iia<br>\ 10h Limp it qu ih cng |<br>1h Cipabit trang i= "Bit tui” A<br>19 Tipb quivi tg iit \|° ‘Mh Cpt hah cng i<br>1 ith gui vi thing bi hh cing |<br>1 Te bt qui cpa rg ti he |<br>‘8 Thine cp shit tng ai in cng<br><!-- End of picture text -->

**Hình 3-27:** _Biểu đồ tuần tự cho ca sử dụng “Cập nhật trạng thái lịch khám chữa bệnh”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_71_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- **_3.5.8. Biểu đồ tuần tự cho ca sử dụng “Thêm mới khoa khám bệnh”_** 



<!-- Start of picture text -->
Quin tr‘Ayiéa Bie st “<br>1.Choa chic ning "Toi méi ne Khim bab”<br>cnn: orm hip thing on imbi<br>4. Nip ta Khon, mt, hia, logo Khon Km bin,<br>A.Giiyinc him miibbonhimbiad<br>5. raring<br>tn Koa hi Bah<br>coo Hgeben a l<br>i {4 Thingbie bi i rorror memesa)<br>$a. hip<br>i hing in hoki bia i<br>| __te Ua G iaisiachs&inininets _:i<br>{Ten koabgp I) ‘Lew thing tinte<br>$b. Triabequi OX k S.Lev in cing<br>gH Thing bi hin hn hin ig i<br><!-- End of picture text -->

**Hình 3-28:** _Biểu đồ tuần tự cho ca sử dụng “Thêm mới khoa khám bệnh”_ 

## **_3.5.9. Biểu đồ tuần tự cho ca sử dụng “Thêm mới bác sĩ”_** 



<!-- Start of picture text -->
vin fr vig 7 7 '<br>{_4. Chon chite nang "Thém méi bie si” H i H<br>2 Higm th form them méi bie si :<br>1 ALNhjp thing din bi 3 hou kim ah, | : H<br>dich vy Khim, ehite<br>i vy vi cht dank 4. Gi yeu ci thm mst bie st H: Hi<br>H 5. vate thing in H<br>6 Thm User mit (Role Doctor, sahID Doctor)<br>A Te Lau thin cong<br>Tri kd gui hi cing H<br><!-- End of picture text -->

**Hình 3-29:** _Biểu đồ tuần tự cho ca sử dụng “Thêm mới bác sĩ”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_72_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.10. Biểu đồ tuần tự cho ca sử dụng “Cập nhật thông tin bệnh nhân”_** 



<!-- Start of picture text -->
(0)<br>(Quin itn<br>1 Chon chic ing "ip mit ing Gina hin”<br>H 2LLiy so bia ai in H bu ‘ i<br>{Trae sebi abi i<br>a cota . 4. Toy i ig bg an ahi<br>j 6. ifm Tr hing tibia hin in<br>ip ait<br>1.Nbip igi thing tincp mit H H<br>H $.Gitiyéucu cip ait H<br>9 Nad in H<br>10 Kl tring CCCDBEYT<br>UL Kétqui kim tra |<br>alt) (TringCCCD/BHYTvii bfah nbin ki} 1s TeilCCCDBHYTdita ti<br>‘a. Chin si hing in H<br>‘Sa. Gailai yéu clu cip mbit (retry)<br>H (Quay Ii bee 10 kimtra tring ip<br>Hop Iq 12. Lo thing tin cia ah hin<br>1h Le ie cig<br>. ‘Mb. Tri kdt qui OK }<br>te 15b, Thing bio cip abit thinh cong, ff<br><!-- End of picture text -->

**Hình 3-30:** _Biểu đồ tuần tự cho ca sử dụng “Cập nhật thông tin bệnh nhân”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_73_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.11. Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm bệnh nhân”_** 



<!-- Start of picture text -->
(intr itnbic i !<br>1 Chon chug "Tn tm bah hin” : |<br>\ 1 Hie ior im i (en ma BN, a BN CCD, BVT) : '<br>{.Nhip i cin H '<br>‘Giiyénca en '<br>Tyan bah ahi te bi ci }<br>| (gui tro in (an schbrig)<br>a) (ing ktqui ‘Trib quite binpbitop H<br>, ‘a Hii bingbia 1<br>n Nhl thin tin bah bin hh ic ‘ i<br>‘Du Gili yécin ine (rey '<br>(Quy abc ta ia "<br>(Cit ul 1h idkih aban | |<br>\ $i nh dik [" :<br>Cuil dnd 10.Yeuciac thinghiginciit Déuh ainta(patientid) Uh Tryin thing chiibaa '<br>, Dh.Thing in tia abi ]<br>1h Trivia ein :<br>hutch itba aia : !<br><!-- End of picture text -->

**Hình 3-31:** _Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm bệnh nhân”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_74_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **_3.5.12. Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm lịch khám bệnh”_** 



<!-- Start of picture text -->
0<br>\ bi<br>(Quin ti iene si i H<br>Chen chic in i it ichhci” H<br>1a ifr in (emi BN BNBis, } :<br>\ tie 1B gy timid) H<br>‘Lk cin it H !<br>4. iyi int ' '<br>k|__iimmiaiiatedediteie§Try vi(Trin dnKb hensich bl chiui  it |H<br>a Uehing et ui nH inhibin inhib '<br>i {Hien th ket qui king i ch hi congo diag H<br>9.Nhip il chitin it . !<br>10a ch imi (et) H H<br>(Quay ibe try vin<br>(Coke qi] :<br>k ‘hiveKhim lbp H H<br>¥ ‘$b. Tre damh sich lich kip ho chong ding i<br><!-- End of picture text -->

**Hình 3-32:** _Biểu đồ tuần tự cho ca sử dụng “Tìm kiếm lịch khám chữa bệnh”_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_75_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- **_3.5.13. Biểu đồ tuần tự cho ca sử dụng “Xuất báo cáo thống kê bệnh nhân”_** 



<!-- Start of picture text -->
9)<br>/<br>quinn vi<br>hah nig Tah ch hh aki<br>2 ache<br>tbc tvs a<br>« uth cede ie ie<br>{Chain<br>ight4. Yeu edu chon Kchoangngthai giamtg xuit bio cio (ti(ce agy- agiy . démln ug)ngiy) I<br>Che ig hi iin<br>| (ity ca ica<br>lo thes Koa Kh ha a<br>Tibet<br>pnhn a<br>[sic<br>I Td ea hing beim ah<br>oy agi<br>ec Bet de aa ik ing<br>{Bao cdo theo djchvy kham béah] ‘To Tray vin ich"iinng Khiahub theo dich vy Khimah  bah<br>Su Trl ab athngt<br>ede oy<br>psi<br>1 Tbh ese ng chta teyina<br>{Bio ch theo bc stim bak “eyinn ine tin isinWak<br>hg i ah<br>Tid hing eis<br>Me evden gd) hs Sb bio cning tx de ick ah<br>e<br><!-- End of picture text -->

**Hình 3-33:** _Biểu đồ tuần tự cho ca sử dụng “Xuất báo cáo thống kê bệnh nhân khám chữa bệnh”_ 

## **3.6. Phân tích thiết kế Chatbot tư vấn bệnh nhân** 

**_3.6.1. Mục tiêu xây dựng Chatbot tư vấn_** 

Việc xây dựng Chatbot tư vấn bệnh nhân có mục tiêu chính là: 

- **Hỗ trợ bệnh nhân** nhanh chóng tiếp cận thông tin về dịch vụ khám chữa bệnh tại Bệnh viện Đa khoa Trung ương Thái Nguyên. 

- **Giảm tải cho nhân viên y tế** , hạn chế tình trạng bệnh nhân phải liên hệ trực tiếp hoặc gọi điện để được giải đáp. 

- **Cung cấp dịch vụ 24/7** , giúp bệnh nhân có thể tra cứu thông tin bất kỳ lúc nào, ngay cả ngoài giờ hành chính, góp phần hiện đại hóa hoạt động quản lý và chăm sóc bệnh nhân trong bệnh viện. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_76_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**_3.6.2. Các chức năng chính của Chatbot tư vấn_** 

Chatbot tư vấn bệnh nhân được thiết kế với các chức năng chính sau: 

1. **Tìm kiếm lịch khám còn trống theo bác sĩ** : Cho phép bệnh nhân nhập tên bác sĩ để hệ thống đưa ra các khung giờ còn trống. 

2. **Tìm kiếm lịch khám còn trống theo dịch vụ khám** : Người bệnh có thể chọn dịch vụ hoặc chuyên khoa để Chatbot trả về các lịch khám khả dụng. 

3. **Tìm kiếm lịch làm việc của bác sĩ** : Người bệnh có thể xem bác sĩ làm việc vào thời gian nào trong tuần giúp lựa chọn lịch khám phù hợp nhất. 

4. **Tra cứu chi phí khám bệnh** : Chatbot hỗ trợ bệnh nhân kiểm tra mức giá khám bệnh theo từng bác sĩ hoặc từng dịch vụ cụ thể. 

5. **Tra cứu thông tin lịch khám** : Sau khi đặt lịch khám, bệnh nhân sẽ được cấp mã phiếu đặt lịch, bệnh nhân có thể tra cứu thông tin phiếu qua chatbot bằng cách nhập mã phiếu. 

6. **Hỗ trợ giải đáp câu hỏi thường gặp (FAQ)** : Cung cấp thông tin cơ bản về quy định khám chữa bệnh, thủ tục hành chính, và liên hệ hỗ trợ. 

## **_3.6.3. Kiến trúc của Chatbot_** 

Kiến trúc của Chatbot tư vấn bệnh nhân được thiết kế theo mô hình nhiều lớp, đảm bảo khả năng mở rộng, dễ bảo trì và đáp ứng hiệu quả nhu cầu tư vấn của bệnh nhân. Hệ thống bao gồm  7 lớp chính: lớp giao tiếp với bệnh nhân (client), lớp tiếp nhận yêu cầu (API Gateway), lớp xử lý ngôn ngữ tự nhiên (NLP), lớp hiểu ý định và thực thể (NLU), lớp điều khiển nghiệp vụ (Controller và Service), lớp dữ liệu (Database và Search Engine), và cuối cùng là lớp phản hồi (Response Builder). 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_77_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
Cent a Application Layer<br>(Béah hin) IngresiGatenay Cached)ache(Redis<br>— (Cutigh Web Routes (ChatSend) Chatbot Controller Booking Services<br>Match eye tip. 7 Function Controller' Validate,tng hop kt qui<br>: ; |<br>(cin hiv tnx Reges Function Token, Embedding |<br>y (topwords, patter. Vector \<br>\<br>Data Layer | \<br>Tim kiémdg trén \<br>keyword | \|<br>(Doctors, Database | \<br>Services, Prices,Schedles,Bot Knowledge)Broking, || \|<br>| \<br>Response Builder<br>(imhingac ich iahtin tring, tra ehintent, kh, keyword gd FAQ), tim (biepiuTighsi hoa kk, xt dich Entity agin) vy, mi (Eallback,Policyshin) Rulehaibé Engine sung,xie rng,‘Trinhbic bieby sikh ktthingguilttindich eh vu,himKh m) l i ch cinkim Thingbis"" nah(xed<br><!-- End of picture text -->

**Hình 3-34:** _Kiến trúc Chatbot tư vấn bệnh nhân_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_78_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **3.7. Xây dựng biểu đồ lớp** 

Biểu đồ lớp (Class Diagram) được sử dụng để mô tả cấu trúc tĩnh của hệ thống, thể hiện các lớp dữ liệu, thuộc tính, phương thức và mối quan hệ giữa các lớp trong hệ thống. 

Trong quá trình thiết kế biểu đồ lớp cho hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp Chatbot tư vấn tại Bệnh viện Đa khoa Trung ương Thái Nguyên, em tiến hành chia nhỏ các lớp thành bốn nhóm chính tương ứng với từng phân hệ chức năng của hệ thống. 

## **_3.7.1. Xây dựng biểu đồ lớp nhóm 1 – Quản lý người dùng và phân quyền_** 

Đây là nhóm có vai trò quan trọng trong việc đảm bảo an toàn và kiểm soát truy cập của toàn bộ hệ thống. Thông qua cơ chế phân quyền theo vai trò (RoleBased Access Control - RBAC), mỗi người dùng chỉ được phép thực hiện các chức năng phù hợp với vai trò được gán. Hệ thống cho phép quản trị viên tạo mới vai trò, nhóm quyền, gán quyền cho vai trò và gán vai trò cho người dùng. Nhờ đó, dữ liệu người dùng được bảo mật, tránh truy cập trái phép và giúp việc quản lý vận hành hệ thống linh hoạt, hiệu quả và mở rộng dễ dàng. 

**Xác định các lớp đối tượng cho nhóm 1 – Quản lý người dùng và phân quyền:** 

- **User:** Quản lý thông tin người dùng (bệnh nhân, bác sĩ, quản trị…), phục vụ xác thực, phân quyền và gán khoa/chuyên khoa. 

- **Role:** Đại diện vai trò (Admin, Bác sĩ, Nhân viên, Bệnh nhân) để nhóm các quyền ở mức chức năng. 

- **Permission:** Quyền tác nghiệp chi tiết (tạo/sửa/xóa/xem…) áp dụng cho các chức năng cụ thể. 

- **GroupPermission:** Gom nhóm các quyền theo chủ đề/chức năng, thuận tiện tổ chức và gán hàng loạt. 

- **RoleUser:** Lớp liên kết nhiều–nhiều giữa User và Role (mỗi người dùng có thể có nhiều vai trò). 

- **PermissionRole:** Lớp liên kết nhiều–nhiều giữa Role và Permission (mỗi vai trò có thể có nhiều quyền). 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_79_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
(Groxp Person<br>id: bigit<br># description: txt<br># ceed at tinetamp<br>opted<br>name: varcha(255)2 timetamp<br>|<br>~ +adiPemnissoaT Group)<br>Aid bigot emovePemisiooFromGroup)<br>ida: date<br>Hur# gander inyint Role User -<br>¥ usr<br>=<br>description: txt<br>*ce= id bigint [Femina; | pane<br>timestamp :<br>updated:name:#wsr_code:varchar(255)varchar) —H Ss|<br># email: varchar(255) !H<br>.<br># phone: varchar(255) :<br>pasword varchar255) ae oe<br>heresaddress: varchar(255) Hl | =<br># fid bgt . i ‘desertion: tet<br>tivepositon i_omber:-varcha(255) varchara sat se<br>insurance, — |<br>card br:rach) ] wei , =<br>ee<br>‘regiteUiet) # day name:varharQ55) tem 5<br>ae= |<br>updateRole) eredePermisson()<br>+searchilser)<br>ierHele) HalelRale)sseachBole) ~apdo+deP rmissoe e Pemisica )<br>riUieDetald Ses a=<br>‘tehangePassword()<br><!-- End of picture text -->

**Hình 3-35:** _Biểu đồ lớp nhóm 1 – Quản lý người dùng và phân quyền_ 

**Bảng 3-34:** _Bảng phân tích biểu đồ lớp cho nhóm 1 – Quản lý người dùng và_ _<u>phân quyền người dùng</u>_ 

|**STT**|**Lớp A**|**Lớp B**|**Kiểu quan hệ**|**Miêu tả chi tiết**|
|---|---|---|---|---|
|1|GroupPermission|Permission|1 – *<br>(Aggregation)|Một nhóm quyền<br>gom<br>nhiều<br>quyền; quyền có<br>thể tồn tại độc lập<br>hoặc thuộc nhóm<br>khác.|
|2|User|RoleUser|1 – *<br>(Composition)|Mỗi user có thể<br>có nhiều bản ghi<br>ánh<br>xạ<br>User–<br>Role; RoleUser|
|||||phụ thuộc vòng|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_80_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|||||đời User.|
|---|---|---|---|---|
|3|Role|RoleUser|1 – *<br>(Composition)|Một role có thể<br>gán cho nhiều<br>user;<br>RoleUser<br>phụ thuộc vòng<br>đời Role.|
|4|Role|PermissionRole|1 – *<br>(Composition)|Một<br>role<br>có<br>nhiều<br>quyền<br>thông qua bảng<br>liên kết;<br>PermissionRole<br>phụ thuộc vào<br>Role.|
|5|Permission|PermissionRole|1 – *<br>(Composition)|Một quyền có thể<br>gán cho nhiều<br>role;<br>PermissionRole<br>phụ<br>thuộc<br>Permission.|



## **_3.7.2. Xây dựng biểu đồ lớp cho nhóm 2 – Quản lý lịch khám chữa bệnh_** 

Đây là nhóm chức năng lõi nghiệp vụ của toàn bộ hệ thống, chịu trách nhiệm quản lý quy trình khám chữa bệnh, bao gồm tổ chức khoa, chuyên khoa, bác sĩ, lịch làm việc và phiếu đặt lịch khám của bệnh nhân. Nhóm này đóng vai trò trung tâm trong việc liên kết giữa các đối tượng như bác sĩ, bệnh nhân, dịch vụ và thời gian khám. 

**Xác định các lớp đối tượng cho nhóm 2 – Quản lý lịch khám chữa bệnh:** 

- **User:** Đại diện cho người dùng là bác sĩ hoặc bệnh nhân, lưu trữ thông tin cá nhân, CCCD, BHYT, chuyên khoa và liên kết với các lịch khám. 

- **Clinic:** Quản lý thông tin các khoa trong bệnh viện, bao gồm tên khoa, địa chỉ, liên hệ và mô tả hoạt động. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_81_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- **Specialty:** Đại diện cho các dịch vụ khám chữa bệnh (chuyên khoa). 

- **ClinicSpecialty:** Lớp liên kết nhiều–nhiều giữa Clinic và Specialty, thể hiện một khoa có thể cung cấp nhiều dịch vụ và một dịch vụ có thể thuộc nhiều khoa khác nhau. 

- **UserSpecialty:** Lớp liên kết nhiều–nhiều giữa bác sĩ (User) và dịch vụ khám (Specialty), cho phép một bác sĩ phụ trách nhiều chuyên khoa và ngược lại. 

- **Schedule:** Quản lý lịch làm việc tổng quát của bác sĩ theo ngày, ca và trạng thái, giúp hệ thống tự động xác định khung thời gian còn trống. 

- **ScheduleTime:** Quản lý các khung giờ chi tiết trong mỗi lịch làm việc. 

- **Booking:** Lưu trữ thông tin đặt lịch khám của bệnh nhân, bao gồm bác sĩ, dịch vụ, thời gian, trạng thái và mã đặt lịch. 



<!-- Start of picture text -->
a)<br>riestonesameaaieit<br>nee<br>secs ener oe<br>—- 1 =<br>pi eee<br>lupe ound teey<br>te som a<br>re 1 et<br>Peni— stbisontit nm)girsann)<br>pate 1 ons Do) » ee Sa<br>ech egSit — apear teeie seamingren) e—ee Setine<br>pean. |__| pd ier F<br>*decipoundpin emis teeayt 1 ee) 1+ emarya tereie — seine Paleaame igie<br>=noe, rear) és[naaa : oo1g ster age<br>ered) gd seep Ani san umd teey<br>pie acs) tg an) a<br>pane we) me tse)<br>sc) nee) svete)<br>‘ld‘tecsee) Seime  eos)9 i.ee dlein)<br>ree dambe reas) | sn aber) ~ peti)<br>ama ater) bea)<br>— —"<br>eeae) lt Stas)z saan.<br>pint) —<br>diet) ebntegDe)<br>svar) ‘xin Fy<br>emda) 7<br>7 [spas<br>10 ibe<br>= i’ —sz cptat<br>vee Ss pc<br>caecg ventasme be amng eta)we)<br>a) ot ety sm ey<br>ered) soins a<br>fete)lop dx) —pcg)<br>ioprigl are)<br>pd eee fp _sk nett<br>ne) soak he<br>pica eyspunea be<br>re) ote<br>emily— (|<br><!-- End of picture text -->

**Hình 3-36:** _Biểu đồ lớp cho nhóm 2 – Quản lý lịch khám chữa bệnh_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_82_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 3-35:** _Bảng phân tích biểu đồ lớp nhóm 2 – Quản lý lịch khám chữa bệnh_ 

|**STT**|**Lớp A**|**Lớp B**|**Kiểu quan hệ**|**Miêu tả chi tiết**|
|---|---|---|---|---|
|1|Clinic|User|1 – 0..*<br>(Aggregation)|Mỗi khoa có thể có<br>nhiều bác sĩ; bác sĩ<br>vẫn tồn tại khi thay<br>đổi/xóa khoa (FK<br>lỏng).|
|2|Specialty|User|1 – 0..*<br>(Aggregation)|Một chuyên khoa có<br>thể là “chuyên khoa<br>chính” của nhiều bác<br>sĩ; liên kết lỏng qua<br>specialty_id.|
|3|User|UserSpecialty|1 – *<br>(Composition)|Bác sĩ có thể gắn<br>nhiều chuyên khoa<br>(phụ);<br>record<br>UserSpecialty<br>phụ<br>thuộc User.|
|4|Specialty|UserSpecialty|1 – *<br>(Composition)|Một chuyên khoa có<br>thể gắn nhiều bác sĩ<br>qua bảng liên kết;<br>record phụ thuộc<br>Specialty.|
|5|Clinic|ClinicSpecialty|1 – *<br>(Composition)|Một khoa cấu hình<br>nhiều<br>dịch<br>vụ;<br>record<br>ClinicSpecialty phụ<br>thuộc Clinic.|
|6|Specialty|ClinicSpecialty|1 – *<br>(Composition)|Một dịch vụ có thể<br>được cung cấp tại<br>nhiều khoa; record|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_83_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|||||phụ thuộc Specialty.|
|---|---|---|---|---|
|7|User (Doctor)|Schedule|1 – *<br>(Aggregation)|Mỗi bác sĩ có nhiều<br>lịch làm việc; lịch<br>tồn tại độc lập với<br>vòng đời bác sĩ (tùy<br>chính sách xóa).|
|8|Schedule|ScheduleTime|1 – *<br>(Composition)|Mỗi lịch gồm nhiều<br>khung giờ con; xóa<br>lịch → xóa toàn bộ<br>khung giờ.|
|9|ScheduleTime|Booking|1 – 0..*<br>(Aggregation)|Mỗi khung giờ có<br>thể có nhiều phiếu<br>đặt; hủy phiếu không<br>ảnh hưởng khung<br>giờ.|
|10|User (Doctor)|Booking|1 – 0..*<br>(Aggregation)|Một bác sĩ có nhiều<br>phiếu đặt; hủy/đổi<br>phiếu<br>không<br>ảnh<br>hưởng tới bác sĩ.|
|11|User (Patient)|Booking|1 – 0..*<br>(Aggregation)|Một bệnh nhân có<br>thể có nhiều phiếu<br>đặt; xóa phiếu không<br>ảnh hưởng tới bệnh<br>nhân.|
|12|Specialty|Booking|1 – 0..*<br>(Aggregation)|Mỗi phiếu đặt gắn<br>một dịch vụ khám;<br>dịch vụ tồn tại độc<br>lập khi phiếu bị hủy.|



## **_3.7.3. Xây dựng biểu đồ lớp cho nhóm 3 – Chatbot tư vấn bệnh nhân_** 

Nhóm này chịu trách nhiệm xây dựng và quản lý cơ sở tri thức (Knowledge 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_84_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

Base) dùng cho Chatbot tự động tư vấn bệnh nhân. 

**Xác định các lớp đối tượng cho nhóm 3 – Chatbot tư vấn bệnh nhân:** 

- **BotKnowledge:** Quản lý các cặp câu hỏi – câu trả lời (question–answer) cùng độ tin cậy (confidence), là nguồn dữ liệu mà Chatbot sử dụng để phản hồi. 



<!-- Start of picture text -->
# id: bigint<br># question: text<br># answer: longtext<br># confidence: float<br># created_at: timestamp<br># updated_at: timestamp<br>+createQA()<br>+updateQAQ)<br>+deleteQAQ)<br>+searchKnowledge()<br>+importKnowledgeBase()<br><!-- End of picture text -->

**Hình 3-37:** _Biểu đồ lớp cho nhóm 3 – Chatbot tư vấn bệnh nhân_ 

**Bảng 3-36:** _Bảng phân tích biểu đồ lớp nhóm 3 – Chatbot tư vấn bệnh nhân_ 

|**STT**|**Lớp A**|**Lớp B**|**Kiểu quan**<br>**hệ**|**Miêu tả chi tiết**|
|---|---|---|---|---|
|1|BotKnowledge|—|—|Lớp độc lập lưu tri thức (cặp|
|||||hỏi–đáp, độ tin cậy) cho|
|||||Chatbot; không có FK bắt|
|||||buộc sang nhóm khác.|



## **_3.7.4. Xây dựng biểu đồ lớp cho nhóm 4 – Tương tác và phản hồi_** 

Nhóm này tập trung vào việc nâng cao trải nghiệm người dùng và tạo kênh tương tác hai chiều giữa bệnh nhân và bệnh viện. Các lớp trong nhóm hỗ trợ việc bình luận, đánh giá, gửi liên hệ, hiển thị banner quảng bá và đăng tải tin tức. Nhờ vậy, bệnh viện có thể thu thập phản hồi thực tế từ người bệnh. 

**Xác định các lớp đối tượng cho nhóm 4 – Tương tác và phản hồi:** 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_85_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- **Comment:** Quản lý các bình luận và phản hồi của người bệnh đối với bác sĩ hoặc dịch vụ, hỗ trợ cấu trúc bình luận cha – con. 

- **Rating:** Lưu trữ các đánh giá của bệnh nhân (số sao, nội dung, trạng thái) về bác sĩ hoặc dịch vụ khám chữa bệnh. 

- **Contact:** Quản lý các liên hệ, góp ý và phản hồi của bệnh nhân gửi đến hệ thống, cho phép nhân viên bệnh viện xử lý và phản hồi lại. 

- **Slide:** Đại diện cho các banner hoặc hình ảnh trình chiếu trên giao diện chính của hệ thống, giúp quảng bá thông tin, dịch vụ, chương trình ưu đãi. 

- **Article:** Quản lý các bài viết, tin tức, thông báo của bệnh viện, phục vụ cho hoạt động truyền thông và cung cấp thông tin cho bệnh nhân. 



<!-- Start of picture text -->
=<br>sictignt<br>ide<br>type: tiny<br>[ery Conmeat<br>‘® clinic_id: bigint =<br>E iti<br>+# pci description: text iit 1 doctor=id (Doctor) fees5Si [aa<br>= Lo astra fr<br>‘met ne sree sats tit<br>ane vacha85 Le re)<br>we code:varehar55) 1 facet a :<br>fe emecret tend Pain) |e int Herel<br>‘aise a doc<br>password: i:bit<br>‘# avatar: varchar(255) varcha(25) aaH Eya eestt a<br>a 1 4 ex: ac) ae)<br>postion tai 58) i rae<br>edn idmomber vasa) 1 . a<br>= sseeiontet)<br>[mesperpa varie er sae<br>ptt) | -pearhComment) rece<br>caeo docto_id Doctor) +uodenteConment) a<br>gone)<br>sepa)<br>eit)<br>ssearchUser()<br>view UserDetail()<br>sehangePassword)sword ae ee =<br>id bint id:se‘cietybigint iit<br>- (ae stint<br>tide patent. pn iit ech<br>— id Patient) |star inyint =)<br>vate ioo ‘ # linkimage: vavarchar(255)55)<br>ae —— ee<br>‘category<br>+# content: longtext E c= Li :<br>ume vacha(259)i bigat eS ——<br>screed ‘+deleteRating() tdeleteSlide()<br>4 updatedat timestamp 2 canis<br>[sevens — —<br>setae<br>pdatedic)<br>‘sdeleteArticle()<br>uh)<br>(ratbleided)<br><!-- End of picture text -->

**Hình 3-38:** _Biểu đồ lớp cho nhóm 4 – Tương tác và phản hồi_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_86_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 3-37:** _Bảng phân tích biểu đồ lớp cho nhóm 4 – Tương tác và phản hồi_ 

|**STT**|**Lớp A**|**Lớp B**|**Kiểu quan hệ**|**Miêu tả chi tiết**|
|---|---|---|---|---|
|1|User<br>(Doctor)|Comment|1 – 0..*<br>(Aggregation)|Bác sĩ có thể nhận nhiều<br>bình luận; bình luận tồn<br>tại độc lập với vòng đời<br>bác sĩ.|
|2|User<br>(Patient)|Comment|1 – 0..*<br>(Aggregation)|Một bệnh nhân có thể gửi<br>nhiều bình luận.|
|3|Comment<br>(parent)|Comment<br>(child)|1 – 0..*<br>(Composition)|Cây bình luận: bình luận<br>con phụ thuộc bình luận<br>cha; xóa cha → xóa con.|
|4|User<br>(Doctor)|Rating|1 – 0..*<br>(Aggregation)|Một bác sĩ có nhiều đánh<br>giá từ bệnh nhân.|
|5|User<br>(Patient)|Rating|1 – 0..*<br>(Aggregation)|Một bệnh nhân có thể gửi<br>nhiều đánh giá.|



**3.8. Thiết kế cơ sở dữ liệu cho hệ thống** 

## **_3.8.1. Thiết kế cơ sở dữ liệu của hệ thống_** 

Cơ sở dữ liệu của hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh được thiết kế nhằm phục vụ ba nhóm nghiệp vụ chính: 

1. **Quản lý thông tin người dùng** – bao gồm bệnh nhân, bác sĩ, quản trị viên. 

2. **Quản lý và hỗ trợ đặt lịch khám chữa bệnh** – lưu trữ các thông tin về lịch khám, dịch vụ, chuyên khoa khám bệnh, và kết quả khám bệnh. 

3. **Hỗ trợ tương tác và tư vấn thông minh** – phục vụ cho hoạt động Chatbot tư vấn, tra cứu, đặt lịch và phản hồi bệnh nhân. 

Cơ sở dữ liệu bao gồm các nhóm bảng chính sau: 

- **Nhóm bảng người dùng:** users, roles, permissions. 

- **Nhóm bảng đặt lịch và quản lý khám:** bookings, schedules, schedule_times, specialties, clinics. 

- **Nhóm bảng hỗ trợ dữ liệu chatbot:** bot_knowledge. 

- **Nhóm bảng hỗ trợ tư vấn và phản hồi:** comments, contacts, ratings. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_87_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 3-38:** _Các bảng cơ sở dữ liệu của hệ thống_ 

|**Tên bảng**|**Ý nghĩa**|
|---|---|
|Users|Người dùng|
|Roles|Vai trò|
|Permission|Quyền hạn|
|Group_permission|Nhóm quyền|
|Bookings|Lịch khám chữa bệnh|
|Schedules|Lịch làm việc|
|Specialties|Dịch vụ khám chữa bệnh|
|Clinics|Khoa khám bệnh|
|Bot_knowledge|Tri thức Chatbot|
|Comments|Bình luận của bệnh nhân|
|Contacts|Liên lạc|
|Ratings|Đánh giá bác sĩ|
|Slides|Background hệ thống|
|Article|Tin tức của bệnh viện|



## **_3.8.2. Đặc tả một số bảng cơ sở dữ liệu của hệ thống_** 

**Bảng 3-39:** _Bảng Users_ 

|**Tên cột**|**Kiểu dữ liệu**|**Ràng buộc**|**Mô tả**|
|---|---|---|---|
|ID|bigint<br>unsigned|Pk, auto_increment|Khóa chính|
|name|varchar(255)|Not null|Tên người<br>dùng|
|user_code|varchar(255)|Unique, Not null|Mã người<br>dùng|
|email|varchar(255)|Unique, Not null|Email đăng<br>nhập|
|phone|varchar(255)|Not null|Số điện thoại|
|password|varchar(255)|Not null|Mật khẩu<br>đăng nhập|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_88_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|avatar|varchar(255)|Định dạng PNG,<br>JPG|Ảnh đại diện|
|---|---|---|---|
|address|varchar(255)|Not null|Địa chỉ|
|birthday|date|Not null|Ngày sinh|
|type|tinyint(4)|not null default 0|Loại user (hệ<br>thống/role<br>phụ).|
|gender|tinyint(4)|not null default 1|Giới tính.|
|clinic_id|bigint<br>unsigned|FK→clinics(id),<br>NULL|Khóa phụ liên<br>kết khoa<br>khám bệnh.|
|specialty_id|bigint<br>unsigned|FK→specialties(id),<br>NULL|Khóa phụ liên<br>kết dịch vụ<br>khám chữa<br>bệnh|
|position|varchar(255)|NULL|Chức danh|
|description|text|NULL|Mô tả ngắn|
|citizen_id_number|varchar(50)|Unique, Not null|Số CCCD|
|insurance_card_number|varchar(50)|Unique, Not null|Số BHYT|



**Bảng 3-40:** _Bảng Bookings_ 

|**Tên cột**|**Kiểu dữ liệu**|**Ràng buộc**|**Mô tả**|
|---|---|---|---|
|ID|bigint<br>unsigned|Pk, auto_increment|Khóa chính|
|booking_code|varchar(255)|Index, not null|Mã đặt lịch|
|doctor_id|bigint<br>unsigned|FK→users(id),<br>NULL|Khóa phụ<br>liên kết tới<br>bảng Users|
|patient_id|bigint<br>unsigned|FK→users(id),<br>NULL|Khóa phụ<br>liên kết tới<br>bảng Users|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_89_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|name|varchar(255)|Not null|Tên bệnh<br>nhân|
|---|---|---|---|
|email|varchar(255)|Not null|Email liên hệ|
|phone|varchar(255)|Not null|Số điện thoại|
|address|varchar(255)|Not null|Địa chỉ|
|birthday|date|Not null|Ngày sinh|
|book_for|tinyint(4)|not null default 0|Đặt cho ai|
|gender|tinyint(4)|not null default 1|Giới tính.|
|schedule_time_id|bigint(20)|Not null|Slot giờ<br>(tham chiếu<br>lịch chi tiết)|
|specialty_id|bigint<br>unsigned|FK→specialties(id),<br>NULL|Liên kết dịch<br>vụ khám<br>chữa bệnh|
|address|varchar(255)|Not null|Địa chỉ bệnh<br>nhân|
|reason_other|text|Not null|Lý do khám|
|number|int(11)|auto_increment|Số thứ tự|
|status|tinyint(4)|DEFAULT 1|Trạng thái<br>đặt lịch|
|date_booking|date|Not null|Ngày khám|
|citizen_id_number|varchar(50)|Unique, Not null|Số CCCD|
|insurance_card_number|varchar(50)|Unique, Not null|Số BHYT|
||**Bảng 3-41:**_Bản_|_g Specialties_||



|**Tên cột**|**Kiểu dữ liệu**|**Ràng buộc**|**Mô tả**|
|---|---|---|---|
|ID|bigint unsigned|Pk, auto_increment|Khóa chính|
|name|varchar(255)|Not null|Tên dịch vụ<br>khám chữa bệnh|
|price|bigint|Not null|Giá khám/lượt|
|description|text|Not null|Mô tả|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_90_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|image<br>avatar|varchar(255)<br>varchar(255)|Định dạng PNG, JPG<br>Định dạng PNG, JPG|Ảnh đại diện<br>Ảnh đại diện|
|---|---|---|---|



**Bảng 3-42:** _Bảng Clinics_ 

|**Tên cột**|**Kiểu dữ liệu**|**Ràng buộc**|**Mô tả**|
|---|---|---|---|
|ID|bigint unsigned|Pk, auto_increment|Khóa chính|
|name|varchar(255)|Not null|Tên khoa khám<br>bệnh|
|email|varchar(255)|Not null|Email|
|phone|varchar(255)|Not null|Số điện thoại|
|address|varchar(255)|Not null|Vị trí khoa khám<br>bệnh|
|description|text|Not null|Mô tả|
|logo|varchar(255)|Định dạng PNG,<br>JPG|Logo khoa khám<br>bệnh|
|link_website|varchar(255)|Not null|Link website|
|avatar|varchar(255)|Định dạng PNG,<br>JPG|Ảnh đại diện|
|created_at|timestamp|NULL|Thời gian tạo|
|updated_at|timestamp|NULL|Thời gian cập<br>nhật|



**Bảng 3-43:** _Bảng Bot_knowledge_ 

|**Tên cột**|**Kiểu dữ liệu**|**Ràng buộc**|**Mô tả**|
|---|---|---|---|
|ID|bigint unsigned|Pk, auto_increment|Khóa chính|
|question|text|FullText (question)|Câu hỏi (FAQ).|
|answer|text|Not null|Câu trả lời.|
|confidence|int(11)|Not null, Default 0|Độ tin cậy.|
|created_at|timestamp|NULL|Thời gian tạo|
|updated_at|timestamp|NULL|Thời gian cập<br>nhật|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_91_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
— ——<— = no a =<<br>ae | AT tee eo oping<br>es | C—O SS ee<br>Fiancee) = array oven eoce ementstionsre oa ——SS — ——————<br>atee w e womenoes bf eea |e {eres|ieaine =a ==<br>aan | ae anata<br>a Se = ==<br>= een Beasssieetee [Jmpeesees hese tomo eine<br>roo 5 Ot beaten eee<br>2S Pmt) <a cos eee Ticeameenn HR<br>cies a ee ee eee<br>— ———J<br>CEES tee SET EER ap peep —<br><!-- End of picture text -->

**Hình 3-39:** _Mối quan hệ giữa các bảng trong hệ quản trị cơ sở dữ liệu_ 

## **3.9. Xây dựng biểu đồ thành phần** 

Biểu đồ thành phần (Component Diagram) được sử dụng để mô tả cấu trúc logic của hệ thống thông qua các thành phần (component) và mối quan hệ giữa chúng. 



<!-- Start of picture text -->
1 Quin thlng ke, i)<br>= a os<br>ees  panain<br>emma en Gna t oo col<br>5 Sit =n 2 mse<br>Seunwvinmin iE i A AAS. Coy<br>atts Wt AF H i AS co<br>gonna LS i H BAL<br>SS Quingtatntois FF fi ee 2 GianaBist PtaN  oma<br>A Quinifraitrd 7 i)<br>TJ sitdung Chatbot<br>mo tuvin<br><!-- End of picture text -->

**Hình 3-40:** _Biểu đồ thành phần của hệ thống_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_92_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

## **3.10. Xây dựng biểu đồ triển khai** 

Biểu đồ triển khai (Deployment Diagram) mô tả cách thức triển khai các thành phần phần mềm lên các phần cứng vật lý, thể hiện mối quan hệ giữa phần mềm và phần cứng trong quá trình vận hành hệ thống. Biểu đồ này giúp làm rõ cách các thành phần hệ thống được cài đặt, phân bố và tương tác trong môi trường thực tế. 

Đối với hệ thống quản lý và hỗ trợ đặt lịch khám tích hợp chatbot, kiến trúc triển khai được thiết kế theo mô hình Client – Server kết hợp với dịch vụ chatbot, đảm bảo khả năng mở rộng và hiệu năng cao. 



<!-- Start of picture text -->
—————7<br>DB Server ——,<br>MysQt Backup & Monitoring<br>phpMyAdmin —a Logs Collector (La)<br>db_doctorbooking— Backup scripts]<br>————, a —,<br>Web Browser Web + Application Server<br>Client XAMPP 7.4.16 - Apache + Laravel<br>| Chrome / Edge/ Firefox! ‘Apache + PHP”<br>erevelArpe | ChatController (regen) |<br>_ Chatbot Server<br>Regex Engine! )<br><!-- End of picture text -->

**Hình 3-41:** _Biểu đồ triển khai của hệ thống_ 

Biểu đồ triển khai của hệ thống gồm 5 thành phần chính: 

1. **Web Browser (Client):** Giao diện người dùng được triển khai trên các thiết bị của bác sĩ, nhân viên y tế và quầy tiếp đón. Người dùng truy cập hệ thống qua trình duyệt web để đặt lịch, tra cứu thông tin, quản lý lịch làm việc và trò chuyện với chatbot. 

2. **Web + Application Server (XAMPP – Apache + Laravel):** Trung tâm xử lý nghiệp vụ của hệ thống, vận hành trên nền tảng XAMPP 7.4.16. Laravel 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_93_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

đảm nhiệm các chức năng quản lý lịch khám, bệnh nhân, bác sĩ, khoa phòng, dịch vụ, hóa đơn, đồng thời tích hợp ChatController để vận hành chatbot dựa trên Regex. 

3. **DB Server (MySQL):** Lưu trữ toàn bộ dữ liệu hệ thống như bệnh nhân, lịch hẹn, bác sĩ, dịch vụ và lịch sử trò chuyện. Sử dụng phpMyAdmin để quản trị và sao lưu dữ liệu. 

4. **Chatbot Server:** Thành phần xử lý hội thoại, có thể chạy độc lập hoặc tích hợp trong ứng dụng Laravel. Chatbot phân tích câu hỏi, nhận dạng ý định và phản hồi tự động các thông tin liên quan đến khám chữa bệnh. 

5. **Backup & Monitoring Server:** Thực hiện sao lưu định kỳ và giám sát hoạt động của hệ thống, đảm bảo an toàn dữ liệu và ổn định vận hành. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_94_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **CHƯƠNG 4: THỰC NGHIỆM** 

## **4.1. Môi trường thực nghiệm** 

## **_4.1.1. Cài đặt Visual Studio Code_** 

Visual Studio Code (VS Code) là một công cụ soạn thảo mã nguồn mạnh mẽ, hỗ trợ đa ngôn ngữ lập trình và nhiều extension phục vụ phát triển web, AI và hệ thống quản lý. 

Trong quá trình xây dựng và triển khai hệ thống, VS Code được lựa chọn làm môi trường phát triển chính nhờ các ưu điểm: 

- Miễn phí, đa nền tảng (Windows, macOS, Linux). 

- Hỗ trợ tích hợp Git/GitHub thuận tiện cho việc quản lý mã nguồn. 

- Kho extension phong phú (PHP, Laravel, MySQL, REST Client, v.v.), giúp tăng tốc độ phát triển. 

- Giao diện trực quan, nhẹ, dễ sử dụng. 

Cài đặt được thực hiện như sau: 

   1. Truy cập https://code.visualstudio.com/, tải phiên bản mới nhất tương thích với hệ điều hành. 

   2. Tiến hành cài đặt theo hướng dẫn mặc định của trình cài đặt. 

- **_4.1.2. Cài đặt Xampp Version 7.4.16_** 

Để triển khai và kiểm thử hệ thống quản lý đặt lịch khám chữa bệnh, cần một môi trường server mô phỏng trên máy cá nhân. Em lựa chọn sử dụng **XAMPP version 7.4.16** , bao gồm Apache, PHP 7.4 và MySQL. 

**Lý do lựa chọn:** 

- Tích hợp sẵn Apache và MySQL, thuận tiện triển khai ứng dụng web. 

- Tương thích tốt với Laravel framework (yêu cầu PHP ≥ 7.3). 

- Quản lý đơn giản thông qua _XAMPP Control Panel_ . 

**Các bước cài đặt:** 

1. Truy cập https://www.apachefriends.org/ và tải XAMPP 7.4.16. 

2. Cài đặt với cấu hình mặc định, bật các module cần thiết 

3. Kiểm tra cài đặt: mở trình duyệt và truy cập http://localhost/phpmyadmin 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_95_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

để xác nhận MySQL đã hoạt động. 

## **_4.1.3. Triển khai thực nghiệm hệ thống tại Bệnh viện Đa khoa Trung Ương Thái Nguyên_** 

Để chứng minh tính ứng dụng thực tiễn và khả năng đáp ứng yêu cầu nghiệp vụ của hệ thống, em tiến hành triển khai bản thử nghiệm tại Bệnh viện Đa khoa Trung ương Thái Nguyên. 

**Quy trình triển khai:** 

1. **Đẩy domain website** 

   - Sau khi hoàn thiện hệ thống trên môi trường phát triển cục bộ, em thực hiện cấu hình và triển khai hệ thống lên domain với tên miền: https://bvtrunguongthainguyen.online/ 

   - Domain được lựa chọn đáp ứng đầy đủ các yêu cầu kỹ thuật: hỗ trợ PHP 7.4, MySQL, Laravel Framework và đảm bảo băng thông để phục vụ số lượng người dùng đồng thời. 

2. **Thực nghiệm tại bệnh viện** 

   - Hệ thống được trình bày và chạy thử trực tiếp trong môi trường thực tế tại Bệnh viện Đa khoa Trung ương Thái Nguyên. 

   - Em mời một số bệnh nhân tham gia sử dụng chức năng tra cứu thông tin bác sĩ, đặt lịch khám trực tuyến với bác sĩ phù hợp, theo dõi lịch khám chữa bệnh và nhận tư vấn từ chatbot. 

   - Đồng thời, các bác sĩ chuyên khoa, y tá, các bác sĩ nội trú, thực tập sinh trong một số khoa (như Nội – Tim mạch, Tai – Mũi – Họng, Da liễu, v.v.) cũng được trải nghiệm hệ thống ở vai trò đăng ký lịch làm việc, quản lý thông tin bệnh nhân, thực hiện quy trình quản lý lịch khám. 

3. **Thu thập phản hồi** 

   - Bệnh nhân phản hồi về: mức độ dễ sử dụng của giao diện, tiện lợi trong việc đặt lịch, tìm kiếm và đặt được lịch khám với bác sĩ phù hợp với nhu cầu, tính năng tư vấn tìm lịch khám còn trống của bác sĩ qua chatbot. 

   - Bác sĩ phản hồi về: tính chính xác của thông tin đặt lịch, khả năng 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_96_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- quản lý lịch hẹn và hỗ trợ trong công tác tổ chức khám chữa bệnh. 

- `o` Các ý kiến được ghi nhận nhằm đánh giá tính phù hợp và đề xuất cải tiến hệ thống trong tương lai. 

Kết quả triển khai thử nghiệm tại bệnh viện Đa khoa Trung Ương Thái Nguyên được trình bày và trực quan hóa tại **mục 4.2.3.** 

## **4.2. Kết quả thực nghiệm** 

Trong quá trình triển khai và thử nghiệm, hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp chatbot đã được xây dựng với các giao diện trực quan, thân thiện với người dùng. Các giao diện này được thiết kế bám sát theo quy trình nghiệp vụ tại bệnh viện. 

## **_4.2.1. Một số giao diện của hệ thống_** 

## _4.2.1.1. Giao diện đăng ký khám bệnh của bệnh nhân_ 



<!-- Start of picture text -->
Ho vatén mail ding nhap<br>Mat khdu dng nhap hp lai mat khau dng nhap<br>Ngay sit GiGi tinh<br>Oo<br>$6 dién thoa Bia chi<br>hiém<br>Can cud céngda 6 thé bao<br><!-- End of picture text -->

**Hình 4-1:** _Giao diện đăng kí tài khoản của hệ thống_ 

Giao diện này giúp cho bệnh nhân đăng kí tài khoản hệ thống. Thông qua tài khoản cá nhân, bệnh nhân có thể theo dõi được tiến độ lịch khám chữa bệnh, nhận kết quả khám chữa bệnh qua các lần khám của mình. Mỗi tài khoản chỉ được sử dụng 1 số thẻ BHYT/ số CCCD, đây cũng chính là mã định dành bệnh nhân mà bệnh viện sử dụng để quản lý bệnh nhân. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_97_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- _4.2.1.2. Giao diện đăng nhập_ 



**Hình 4-2:** _Giao diện đăng nhập của hệ thống_ 

- _4.2.1.3. Giao diện Chatbot tư vấn_ 



<!-- Start of picture text -->
jj x |<br>Xin chao! Téi cé thé giuip gi cho d<br>ban?<br>i<br>i<br>Nhép tin nhan cua ban a)<br>wee<br>wp Q<br><!-- End of picture text -->

**Hình 4-3:** _Giao diện Chatbot tư vấn bệnh nhân_ 

Tại giao diện này, bệnh nhân tiến hành đặt các câu hỏi Q&A, tra cứu nhanh lịch khám, lịch làm việc của bác sĩ, tra cứu lịch khám dịch vụ theo khoảng thời gian mong muốn. Đồng thời Chatbot còn hỗ trợ bệnh nhân theo dõi thông tin lịch khám, tiến độ lịch khám và giá khám bệnh / lượt đối với bác sĩ và dịch vụ. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_98_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- _4.2.1.4. Giao diện tìm kiếm nhanh bác sĩ_ 



<!-- Start of picture text -->
ee] . Ww ~<br>i E wr. é<br>oe 44 L Di dl ag<br>‘<br>iér ten bac ‘Khoa khém bénh v Dich ww ¥ :<br>DANH SACH GAG DICH VU<br><!-- End of picture text -->

**Hình 4-4:** _Form tìm kiếm nhanh bác sĩ_ 

Form tìm kiếm nhanh bác sĩ sẽ hỗ trợ bệnh nhân tìm kiếm bác sĩ chuyên khoa mà bản thân mình mong muốn một cách nhanh chóng nhất, sau khi tìm kiếm bác sĩ, hệ thống sẽ hiển thị thông tin bác sĩ bao gồm chức danh/khoa khám bệnh/dịch vụ khám và lịch làm việc của bác sĩ để bệnh nhân tiến hành đăng ký khám chữa bệnh. 

- _4.2.1.5. Giao diện thông tin các khoa khám bệnh_ 

Giao diện này sẽ hiển thị danh sách khoa khám bệnh, thông tin về từng khoa khám bệnh và danh sách các bác sĩ thuộc khoa khám bệnh để bệnh nhân đặt lịch khám. 



<!-- Start of picture text -->
Khoa Da Lieu Khoa Nhi<br>KHOA DA LEU ior<br>Khoa Phu sin Khoa Than - Tiel Ni¢u<br>OF fe )<br>Coins Caw<br>Khoa Tiéu héa Khoa Co - Xuong<br>Khép<br><!-- End of picture text -->

**Hình 4-5:** _Danh sách các khoa khám bệnh_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_99_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- _4.2.1.6. Giao diện thông tin các dịch vụ khám bệnh_ 

Giao diện này sẽ hiển thị danh sách các dịch vụ khám bệnh, thông tin dịch vụ khám bệnh và danh sách các bác sĩ khám dịch vụ để bệnh nhân dễ dàng lựa chọn và đăng ký khám chữa bệnh. 



<!-- Start of picture text -->
DICH VL<br>fs<br>Gf)<br>va tevinplu thug any tinh ane oyBhim va phd Unudt thd my nan Khoa<br>x 2<br>y UFO)<br>Ep twin<br>va digu tjroi logn sit 0 da (nim, tn Fess) Teevin ngi soi'tS<br>88 $,<br>:e<br><!-- End of picture text -->

**Hình 4-6:** _Danh sách dịch vụ khám chữa bệnh_ 

- _4.2.1.7. Giao diện thông tin bác sĩ_ 



<!-- Start of picture text -->
aPGS.TS Nguyén Van Minh<br>+ aor<br>chi dan malt<br>Dinh gid<br>© chow: as00006<br>GidiTrungtnigukhoa Noi Tim mach, Bénh vign Da khoa Trung wong Thai Nguyén (e.)<br><!-- End of picture text -->

**Hình 4-7:** _Giao diện thông tin và lịch làm việc của bác sĩ_ 

- _4.2.1.8. Giao diện đặt lịch khám chữa bệnh_ 

Giao diện này sẽ hỗ trợ bệnh nhân điền thông tin đặt lịch khám và hoàn tất thủ tục đặt lịch khám bác sĩ mong muốn. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_100_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
lakh :450,0004<br>THONG TIN DAT LICH KHAM<br>Hovaten © Ngaysinn<br>®<br>‘S6dién thoai piachi<br>an cube céng din 6 thé bio hiém<br>Gidi tinh Email<br>Dichwy © ‘Dat cho:<br><!-- End of picture text -->

**Hình 4-8:** _Giao diện đặt lịch khám chữa bệnh_ 



<!-- Start of picture text -->
Thong bao<br>nghan lichlich kh km thnh cng ching ti8 inhé 8 xd<br><!-- End of picture text -->

**Hình 4-9:** _Hiển thị đặt lịch khám thành công_ 

Sau khi tiến hành đặt lịch khám thành công, hệ thống sẽ hiển thị thông báo và gửi Email về cho bệnh nhân xác nhận, nhân viên sẽ gọi điện cho bệnh nhân để xác nhận lịch khám 1 lần nữa. 

- _4.2.1.9. Giao diện theo dõi lịch khám chữa bệnh_ 

Giao diện này sẽ cho phép bệnh nhân theo dõi tiến trình lịch khám chữa bệnh, 

dễ dàng hủy lịch khám và nhận kết quả khám chữa bệnh từ bác sĩ. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_101_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
MENU LUA CHON: Danh sachA datseilich<br>SIT Thangtin béesi Ngay him Thiigian Giékhim Trang thé<br>1  dauhong 2025.09.17 715-730 4500008 sbsivkas<br>2 5 . oe “ 2025-09-26 7:00-7:15 450,000 se ahi<br><!-- End of picture text -->

**Hình 4-10:** _Giao diện theo dõi lịch khám chữa bệnh của bệnh nhân_ 



<!-- Start of picture text -->
Cam on ban da dat lich kham tai hé thong cua bénh vién Da khoa Trung Vong<br>Thai Nguyén<br>Xin chao : VG Thi Nu<br>Théng tin cho cudc hen da dat<br>Tén bac si: Giang 8ire Thinh<br>Dich vu: Kham viém mii xoang, dau hong, u tai<br>Thoi gian: 7:15-7:30<br>Ngay: 2025-09-17<br>Gia tién : 450.000 vng<br>Trang thai - Lich kham cia ban da dug dng ky thanh cong<br>86 thir ty kam : 2<br>Hé théng sé tu d6ng giti email théng bao cudc hen duoc xac nhan hoan tat. Cam on ban !<br>Day 1a email ty déng xin vui khéng Khéng tra Idi vao email nay<br>Tran trong cam on !<br><!-- End of picture text -->

**Hình 4-11:** _Tiến độ lịch khám chữa bệnh được gửi về Email của bệnh nhân_ 

Đối với mỗi trạng thái của lịch khám, hệ thống sẽ tự động gửi Email thông tin về cho bệnh nhân, giúp cho bệnh nhân theo dõi lịch khám một cách rất dễ dàng. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_102_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- _4.2.1.10. Giao diện quản trị viên_ 



<!-- Start of picture text -->
a Quan ly lich kham @<br>. anh sch thing<br>a<br>Sa ch1  tim wife hm may ‘So12khoa kh bénh ‘SS41 ¢ichwy<br>7 = mune =<br>. 85<br>~ . ‘Sébénh akin<br>e<br>renin<br>.<br>*<br>- Shogo maven gan eet | rye Tg ah ng<br><!-- End of picture text -->

**Hình 4-12:** _Giao diện quản trị viên hệ thống_ 

Tại giao diện Dashboard, quản trị viên có thể nắm bắt được nhanh số lượng lịch khám trong ngày, số lịch làm việc của bác sĩ, số lượng khoa khám bệnh, dịch vụ, số lượng bệnh nhân và số bác sĩ. 

- _4.2.1.11. Giao diện quản lý khoa khám bệnh_ 

Giao diện này bao gồm các chức năng quản lý khoa khám bệnh của quản trị viên, cho phép xem danh sách khoa khám bệnh, thêm mới, cập nhật, tìm kiếm và xóa khoa khám bệnh. 



<!-- Start of picture text -->
@ ausntrinedsite Foc tn Kien<br>a<br>°<br>= ha Ps _ rene a mee | nes<br>a (7m, »<br>7 1 nnn gon cual Tngztab ing ao<br>5<br>= yy<br><!-- End of picture text -->

**Hình 4-13:** _Giao diện quản lý khoa khám bệnh_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_103_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

- _4.2.1.12. Giao diện quản lý bác sĩ_ 

Giao diện này bao gồm các chức năng quản lý bác sĩ của quản trị viên, cho phép xem danh sách bác sĩ, thêm mới, cập nhật, tìm kiếm và xóa bác sĩ một cách dễ dàng. 



<!-- Start of picture text -->
@ ouintsiwedsite = ® see<br>a f§f<br>=<br>c<br><!-- End of picture text -->

**Hình 4-14:** _Giao diện quản lý bác sĩ_ 



<!-- Start of picture text -->
@ auintiwersite = @® sain<br>a *<br>— Hovitin? mai xust bin<br>Bois Phone”) chew" Chie dan<br>a7 Khoa khdm bénh!! Dich vy kiéu nguéi ding.<br>‘Chon“khoakhém bénh . Quant .<br>*<br>.<br>Gi kien in aby sinh ‘Tinh / Quin huyén<br>a<br><!-- End of picture text -->

**Hình 4-15:** _Giao diện thêm mới bác sĩ_ 

- _4.2.1.13. Giao diện quản lý lịch khám chữa bệnh_ 

Giao diện này bao gồm các chức năng quản lý lịch khám chữa bệnh của bệnh nhân, cho phép bác sĩ xem danh sách lịch khám chữa bệnh, cập nhật trạng thái lịch khám, tìm kiếm lịch khám chữa bệnh. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_104_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
Convince aT<br>c) : a .<br>cig<br>mums<br><!-- End of picture text -->

**Hình 4-16:** _Giao diện quản lý lịch khám chữa bệnh_ 

- _4.2.1.14. Giao diện quản lý và đăng ký lịch làm việc cho bác sĩ_ 

Căn cứ theo tiến độ công việc, lịch làm việc, phẫu thuật và nhu cầu cá nhân, vào mỗi cuối tuần bác sĩ sẽ tiến hành đăng ký lịch làm việc vào tuần kế tiếp. Giao diện này hỗ trợ quản trị viên và bác sĩ đăng ký lịch làm việc và thời gian khám bệnh theo ngày, đồng thời dễ dàng tìm kiếm và cập nhật, xóa lịch làm việc. 



<!-- Start of picture text -->
Ohm<br>a S) .<br>° [+700]<br>8a tertimat [=n]Sao mr ror] veer] me] re]<br>B ai [sans] xonn monn | sone] sm]<br>5 5 [=n]Soo mom aos wen |e<br>= Paseo]Sao vere]<br>A [==Soosvi wins ie |<br><!-- End of picture text -->

**Hình 4-17:** _Giao diện quản lý và đăng ký lịch làm việc cho bác sĩ_ 

- _4.2.1.15. Giao diện xuất báo cáo thống kê bệnh nhân_ 

Giao diện này hỗ trợ quản trị viên xuất báo cáo thống kê danh sách bệnh nhân đặt lịch khám chữa bệnh theo khoa khám bệnh, theo dịch vụ và theo bác sĩ khám bệnh. Góp phần dễ dàng trong việc quản lý của bệnh viện và bộ y tế trong việc 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_105_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

quản lý bảo hiểm y tế của người dân khi khám chữa bệnh tại bệnh viện. Báo cáo thống kê được xuất ra với đầy đủ thông tin cá nhân, số thẻ BHYT và số CCCD của 

bệnh nhân. 



<!-- Start of picture text -->
Cores :<br>:<br>”<br>1 bsocio git<br>Bos<br>*<br>=<br>oC<br><!-- End of picture text -->

**Hình 4-18:** _Giao diện xuất báo cáo thống kê bệnh nhân_ 

## _4.2.1.16. Giao diện quản lý bệnh nhân_ 

Giao diện này hỗ trợ quản trị viên dễ dàng quản lý, xem danh sách bệnh nhân, tìm kiếm bệnh nhân theo số CCCD, số thẻ BHYT, cập nhật thông tin bệnh 

nhân một cách nhanh chóng. 



<!-- Start of picture text -->
@ovnriversie<br>a Fomtim kin<br># einen<br>3 oxen<br>Ac<br>ST Misihohin tin<br>ears cosON ipso ii em race To Hg<br>a 1 ome Ngftangin oS as HOLST meneame otis EY<br>Dis:, 5 MOOD BEVIN ng secs HSIENSUS eHOTHL Non banenggtion oss tontcie EY<br><!-- End of picture text -->

**Hình 4-19:** _Giao diện quản lý bệnh nhân_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_106_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
@ awinteiwebsite = ee<br>a<br>&Bénhohan oessronass Anh dai dién<br>=" ‘ . Gin culdc cing din $6 thé bio hiém<br>Winn5 gy sin Trangenai NS v4<br>ov/ox/isa DF @roseaing oF Kase chontee<br>ore<br><!-- End of picture text -->

**Hình 4-20:** _Giao diện cập nhật thông tin bệnh nhân_ 

- _4.2.1.17. Giao diện quản lý dịch vụ khám chữa bệnh_ 

Giao diện này bao gồm các chức năng quản lý dịch vụ khám chữa bệnh của quản trị viên, cho phép xem danh sách dịch vụ khám chữa bệnh, thêm mới, cập nhật, tìm kiếm và xóa khoa khám bệnh. 



<!-- Start of picture text -->
a i ty Tun ph thn oom ao<br>% den 2<br>mann hoa 30,0006 ag<br>eeeA 7 ffusEs: Kn puthudtthim<br>Bu mr:<br>5 (<br> osngs<br>4 “ Khim<br>s a vi tu vin cdc bg i vbmit 350,000 ao<br>Fs {<br><!-- End of picture text -->



<!-- Start of picture text -->
Hình 4-21:  Giao diện quản lý dịch vụ khám chữa bệnh<br><!-- End of picture text -->

## **_4.2.2. Xây dựng các ca kiểm thử tự động hệ thống với PHPUnit_** 

Để đảm bảo hệ thống hoạt động đúng theo yêu cầu đề ra và hạn chế tối đa lỗi trong quá trình triển khai, em tiến hành xây dựng các ca kiểm thử tự động sử dụng công cụ PHPUnit – framework kiểm thử phổ biến dành cho ứng dụng PHP và Laravel. Việc kiểm thử tự động giúp: 

- Xác minh tính đúng đắn của các chức năng quan trọng như đăng ký tài 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_107_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

khoản, đăng nhập, đặt lịch khám, quản lý lịch khám, theo dõi trạng thái lịch khám và kết quả khám qua Email. 

- Tiết kiệm thời gian so với kiểm thử thủ công, đồng thời tăng tính chính xác và độ tin cậy, đồng thời hỗ trợ phát hiện và khắc phục lỗi sớm trong quá trình phát triển, đảm bảo hệ thống ổn định khi đưa vào vận hành thực tế. 

Trong phần này, em sẽ trình bày một số ca kiểm thử tiêu biểu đã được xây dựng, cùng với kết quả mong đợi để chứng minh tính đúng đắn và khả năng vận hành ổn định của hệ thống, đồng thời giải quyết các lỗi, vấn đề phát sinh trong quá trình hoàn thành hệ thống trước khi đưa vào thực nghiệm. 

**Bảng 4-1:** _Bảng liệt kê các TC kiểm thử tự động hệ thống với PHPUnit_ 

|**Mã TC**|**Nội dung kiểm thử**|**Mục tiêu**|**Kết quả mong đợi**|
|---|---|---|---|
|**TC-01**|Hiển thị trang đặt<br>lịch khi có lịch khám<br>và khung giờ hợp lệ|Đảm bảo hệ thống hiển<br>thị đúng giao diện đặt<br>lịch|Trang đặt lịch được<br>hiển thị, trả về địa<br>chỉ HTTP 200|
|**TC-02**|Truy cập lịch hẹn<br>không tồn tại|Kiểm tra khả năng xử lý<br>lỗi khi ID lịch không có<br>trong hệ thống|Chuyển hướng về<br>trang chủ, thông<br>báo lỗi “Thông tin<br>lịch khám không<br>tồn tại”|
|**TC-03**|Đặt lịch khi số lượng<br>bệnh nhân / ca khám<br>vượt quá quy định|Đảm bảo không có thêm<br>lịch khám được đặt khi<br>ca khám đã đủ số người|Chuyển<br>hướng,<br>hiển thị thông báo<br>lỗi phù hợp|
|**TC-04**|Người dùng đặt lịch<br>trùng (cùng số điện<br>thoại và khung giờ)|Tránh việc một bệnh<br>nhân đặt trùng nhiều lần|Hệ thống từ chối đặt<br>lịch,<br>thông<br>báo<br>“Lịch khám đã tồn<br>tại”|
|**TC-05**|Đặt lịch khám bệnh<br>với dữ liệu hợp lệ|Xác minh chức năng đặt<br>lịch hoạt động khi nhập<br>đầy đủ thông tin|Yêu cầu được xử lý,<br>phản hồi kết quả và<br>giả lập gửi Email<br>xác nhận|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_108_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

|**TC-06**|Đặt lịch với dữ liệu<br>thiếu (thiếu trường<br>bắt buộc)|Kiểm tra tính năng kiểm<br>tra dữ liệu đầu vào<br>(validate)|Hệ thống báo lỗi,<br>yêu cầu nhập đầy đủ<br>thông tin|
|---|---|---|---|
|**TC-07**|Đặt lịch khi chưa<br>đăng<br>nhập<br>(fake<br>thông tin Email)|Cho phép bệnh nhân<br>chưa đăng nhập đặt lịch,<br>nhưng đảm bảo kiểm<br>soát dữ liệu hợp lệ và<br>thông báo kết quả phù<br>hợp.|Hệ thống tiếp nhận<br>thông tin và phản<br>hồi kết quả|
|**TC-08**|Xác nhận lịch khám<br>(Trường hợp lịch<br>hẹn không tồn tại)|Trường hợp lịch hẹn<br>không tồn tại: hệ thống<br>sẽ từ chối xác nhận và<br>thông báo lỗi.|Chuyển hướng về<br>trang chủ, hiển thị<br>thông báo lỗi|
|**TC-09**|Xác nhận lịch khám<br>(Trường hợp lịch<br>hẹn hợp lệ)|Hệ thống cập nhật trạng<br>thái thành công, tăng số<br>thứ tự khám cho bệnh<br>nhân, đồng thời giả lập<br>gửi email thông báo.|Trạng thái lịch được<br>cập nhật, số thứ tự<br>tăng chính xác, giả<br>lập gửi email|
|**TC-10**|Xác nhận lịch khám<br>bệnh (confirm) – lỗi<br>hệ thống (exception)|Hệ thống vẫn xử lý an<br>toàn, không gây gián<br>đoạn, và phản hồi theo<br>hướng “graceful”|Hệ thống xử lý và<br>đưa ra thông báo<br>“Có lỗi đã xảy ra,<br>vui lòng thử lại sau”|
|**TC-11**|Đặt lịch khi đã đăng<br>nhập<br>(thông<br>tin<br>Email là chính xác)|Kiểm tra xem hệ thống<br>xử lý thế nào khi một<br>bệnh nhân đã đăng nhập<br>và có thông tin Email là<br>chính xác|Hệ thống tiếp nhận<br>thông tin và phản<br>hồi kết quả qua<br>Email<br>của<br>bệnh<br>nhân|
|**TC-12**|Đặt lịch với đầy đủ<br>thông tin bệnh nhân|Kiểm tra hệ thống tiếp<br>nhận dữ liệu mở rộng|Hệ thống phản hồi<br>kết quả, đảm bảo dữ<br>liệu được ghi nhận|
|**TC-13**|Xác nhận lịch khám|Kiểm tra khả năng xử lý|Hệ thống không|



_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_109_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

||khi có lỗi hệ thống<br>(exception)|lỗi an toàn|gián đoạn, phản hồi<br>kết quả thành công|
|---|---|---|---|
|**TC-14**|Đặt lịch với lỗi trong<br>transaction<br>(exception)|Đảm bảo rằng hệ thống<br>có<br>cơ<br>chế<br>rollback<br>transaction và xử lý lỗi<br>một cách an toàn.|Hệ thống chuyển<br>hướng,<br>báo<br>lỗi,<br>không<br>gây<br>gián<br>đoạn|
|**TC-15**|Sinh mã đặt lịch tự<br>động|Kiểm tra việc phát sinh<br>mã định danh chuẩn|Mỗi booking có mã<br>đúng<br>định<br>dạng<br>PKxxxxxx|
|**TC-16**|Tăng số thứ tự khám<br>(number)|Kiểm tra cấp phát số thứ<br>tự chính xác|Lượt đặt lịch mới<br>được gán số thứ tự<br>kế tiếp (+1)|



## **_4.2.3. Kết quả thực nghiệm hệ thống tại Bệnh viện Đa khoa Trung Ương Thái Nguyên_** 

Trong phần này, em sẽ trình bày kết quả triển khai thực nghiệm tại Bệnh viện Đa khoa Trung Ương Thái Nguyên sau quá trình thu thập thu thập khảo sát mức độ hài lòng sau khi sử dụng và đánh giá hệ thống của bệnh nhân, mức độ hài lòng của bác sĩ và y tá khi sử dụng hệ thống quản lý. Sau đó, em tiến hành trực quan hóa dữ liệu sử dụng bộ công cụ Matplotlib và Seaborn của Python để có cái nhìn khái quát và rõ ràng nhất cho kết quả triển khai thực nghiệm. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_110_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 4-2:** _Bảng kết quả khảo sát mức độ sử dụng và đánh giá hệ thống đặt lịch khám của bệnh nhân_ 

|**Nhóm tuối**|**Giao diện dễ**<br>**sử dụng**|**Dễ tìm kiếm bác sĩ**<br>**theo khoa khám**<br>**bệnh**|**Dễ tìm kiếm bác sĩ**<br>**theo dịch vụ khám**<br>**bệnh**|**Dễ theo dõi tiến**<br>**độ lịch khám &**<br>**trả kết quả**|**Tìm được lịch**<br>**khám phù hợp**<br>**qua Chatbot**|
|---|---|---|---|---|---|
|Dưới 25 tuổi|Có:**96.6%**|Có:**94.8%**|Có:**96.6%**|Có:**93.1%**|Có:**96.6%**|
|(58 bệnh nhân)|Không: 3.4%|Không: 5.2%|Không: 3.4%|Không: 6.9%|Không: 3.4%|
|Từ 25–40 tuổi|Có:**93.1%**|Có:**92.2%**|Có:**96.1%**|Có:**95.1%**|Có:**94.1%**|
|(102 bệnh nhân)|Không: 6.9%|Không: 7.8%|Không: 3.9%|Không: 4.9%|Không: 5.9%|
|Từ 41–60 tuổi|Có:**88.5%**|Có:**92.3%**|Có:**98.1%**|Có:**100%**|Có:**92.3%**|
|(52 bệnh nhân)|Không: 11.5%|Không: 7.7%|Không: 1.9%|Không: 0%|Không: 7.7%|
|Trên 60 tuổi|Có:**100%**|Có:**95.0%**|Có:**100%**|Có:**90.0%**|Có:**95.0%**|
|(20 bệnh nhân)|Không: 0%|Không: 5%|Không: 0%|Không: 10%|Không: 5.0%|
|**Tổng**<br>**232 bệnh nhân**|Có:**93.5%**|Có:**93.1%**|Có:**94.8%**|Có:**95.3%**|Có:**94.8%**|
||Không: 6.5%|Không: 6.9%|Không: 5.2%|Không: 4.7%|Không: 5.2%|



**Nhận xét:** 

Kết quả khảo sát cho thấy mức độ hài lòng chung của bệnh nhân đối với hệ thống đạt rất cao, với tỷ lệ lựa chọn **“** Có” trung bình trên 93% ở tất cả các tiêu chí và đối với các nhóm bệnh nhân khác nhau mặc dù khác biệt về độ tuổi và khả năng sử dụng công nghệ, phản ánh rằng giao diện và các chức năng của hệ thống được người dùng đánh giá tích cực, dễ sử dụng và mang lại trải nghiệm tốt. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_111_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
100 Giao dign dé sir dung 00.0%<br>53 rs<br>»<br>=-*<br>z<br>cs<br>Fs<br>»<br>.Durdi 25 twbi Tit 25-40 wii Tir 41-60 wii Trén 60 wii<br><!-- End of picture text -->



<!-- Start of picture text -->
Dé tim kiém bie si theo dich vu khim bénh<br>wo . 00%<br>»<br>e Nhdm twai<br>g Dus 25 i<br>2 Tir 25-40 wi<br>ze « mmBE TrenTis) 060 wii<br>»<br>e Dui 25 twit Ta25-40 wii ‘Tir41-60 wai Trin 60 tdi<br><!-- End of picture text -->



<!-- Start of picture text -->
PhanAn bébé bénhbé  nhanai theo nhém6 tudifi<br>Tir 41-60 twdt<br>“Tren<br>6%C60 tut, 24%»<br>Dud28.0%25 tdi<br>Tie25-400%adi<br><!-- End of picture text -->



<!-- Start of picture text -->
Dex theo doiwe tienek dé lich KhamS  & tra= ketLA qua2<br>oo : 100.0%<br>9.0%<br>#<br>_<br>2<br>z<br>”<br>»<br>10.0%<br>0<br>Durdi 25 tui Tir 25-40 tudi Tir 41-60 di Tren60 tai<br><!-- End of picture text -->

**Hình 4-22:** Trực quan hóa kết quả khảo sát mức độ sử dụng và đánh giá hệ thống của bệnh nhân 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_112_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

**Bảng 4-3:** _Bảng kết quả khảo sát mức độ hài lòng của các bác sĩ và y tá khi sử dụng hệ thống_ 

|**Nhóm đối tượng**|**Giao diện dễ**<br>**sử dụng**|**Dễ dàng quản lý**<br>**thông tin bệnh**<br>**nhân**|**Dễ dàng đăng ký**<br>**lịch làm việc**|**Dễ dàng quản lý**<br>**lịch khám chữa**<br>**bệnh**|**Báo cáo thống kê**<br>**hiển thị chính**<br>**xác, dễ quản lý**|
|---|---|---|---|---|---|
|Bác sĩ chuyên khoa|Có:**96.8%**|Có:**93.5%**|Có:**96.8%**|Có:**100%**|Có:**96.8%**|
|(31 bác sĩ)|Không: 3.2%|Không: 6.5%|Không: 3.2%|Không: 0%|Không: 3.2%|
|Y tá|Có:**100%**|Có:**100%**|Có:**100%**|Có:**100%**|Có:**100%**|
|(15 y tá)|Không: 0%|Không: 0%|Không: 0%|Không: 0%|Không: 0%|
|Bác sĩ nội trú|Có:**100%**|Có:**100%**|Có:**100%**|Có:**94.4%**|Có:**94.4%**|
|(18 bác sĩ)|Không: 0%|Không: 0%|Không: 0%|Không: 5.6%|Không: 5.6%|
|Thực tập|Có:**100%**|Có:**100%**|Có:**100%**|Có:**100%**|Có:**93.3%**|
|(15 bác sĩ)|Không: 0%|Không: 0%|Không: 0%|Không: 0%|Không: 6.7%|
|**Tổng**<br>**79 bác sĩ/y tá**|Có:**98.7%**<br>Không: 1.3%|Có:**97.5%**<br>Không: 2.5%|Có:**98.7%**<br>Không: 1.3%|Có:**98.7%**<br>Không: 1.3%|Có:**96.2%**<br>Không: 3.8%|



## **Nhận xét:** 

Tất cả các tiêu chí đều đạt mức đồng thuận trên 95%, khẳng định rằng hệ thống quản lý đáp ứng tốt yêu cầu của đội ngũ bác sĩ và nhân viên y tế trong công tác quản lý, vận hành và theo dõi quy trình khám chữa bệnh. Điều này chứng minh hệ thống không chỉ hướng đến trải nghiệm người bệnh, mà còn tối ưu hóa quy trình công tác nội bộ, góp phần nâng cao hiệu quả điều hành, giảm tải công việc và tăng năng suất chuyên môn của bệnh viện. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_113_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 



<!-- Start of picture text -->
wo Dé dang100.0% quin ly théng tin0.07% bénh nhan 190.0%<br>9<br>_«@<br>z<br>Pg<br>z<br>“<br>»<br>oi<br>Bic si chuyén khoa Yta Bac si ndi tr ‘Thue tip<br><!-- End of picture text -->



<!-- Start of picture text -->
soo are DE ding10. quan I lich khim chia bénh 100.0%<br>ma<br>9<br>© Chi wy<br>g MB Bic si chuyén khoa<br>Pa my<br>Fy WE Bic sini tri<br>“ Thue tip<br>»<br>50%<br>0<br>Bas si chuyén khoa Yti Bic st npi tra Thue tip<br><!-- End of picture text -->



<!-- Start of picture text -->
co D éS d angang ding ding k yylich llich t a mm viéevik 10.0%<br>o<br>®<br>2<br>»<br>»<br>°<br>Bac si chuyén khoa Yu Bac si ndi tra Thye tip<br><!-- End of picture text -->



<!-- Start of picture text -->
we tin‘in ‘bdba vi tri congdng  tietae  ct ac i ta  bieba  st<br>era 19.0%<br>Bic si chuyén khoa — 39.2%<br>Bae sf nf tri — 22.8%<br><!-- End of picture text -->

**Hình 4-23:** _Trực quan hóa kết quả khảo sát mức độ hài lòng của các bác sĩ và y tá khi sử dụng hệ thống quản lý_ 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_114_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN** 

Sau một khoảng thời gian nghiên cứu, tìm hiểu và xây dựng sản phẩm đề tài đồ án tốt nghiệp “Xây dựng hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh tích hợp Chatbot tư vấn tại bệnh viện Đa khoa Trung Ương Thái Nguyên”, em đã đạt được các kết quả sau: 

   - Xây dựng thành công hệ thống quản lý và hỗ trợ đặt lịch khám chữa bệnh bám sát nghiệp vụ tổ chức khám chữa bệnh tại bệnh viện Đa khoa Trung Ương Thái Nguyên và mục tiêu nghiên cứu ban đầu đề ra. 

   - Ứng dụng trợ lý ảo AI vào bài toán cụ thể, hỗ trợ tư vấn bệnh nhân tìm kiếm lịch khám theo bác sĩ, dịch vụ khám như mong muốn và các thông tin liên quan. 

   - Xây dựng các ca kiểm thử tự động bằng PHPUnit, đồng thời tiến hành vận hành hệ thống với Docker. 

   - Tiến hành đẩy Domain hệ thống với tên miền cụ thể, thực nghiệm tại bệnh viện Đa khoa Trung Ương Thái Nguyên, lấy ý kiến phản hồi của bệnh nhân và các y bác sĩ, đạt được kết quả rất tích cực. 

   - Vận dụng tối đa các kiến thức được học trong suốt 4 năm đại học phát triển đồ án tốt nghiệp theo hướng Fullstack Developer. 

- Mặc dù hệ thống đã hoàn thiện về mặt chức năng và vận hành ổn định, song vẫn 

- còn một số hướng phát triển tiềm năng nhằm mở rộng khả năng ứng dụng và tối ưu hiệu suất trong tương lai: 

   - Phát triển Chatbot thông minh hơn: Tích hợp mô hình ngôn ngữ lớn (LLM) để Chatbot hiểu ngữ cảnh sâu hơn, phản hồi tự nhiên hơn, đồng thời có khả năng phân tích tài liệu, đưa ra quyết định hỗ trợ bác sĩ trong quá trình khám chữa bệnh. 

   - Xây dựng ứng dụng di động (Mobile/App): Xây dựng ứng dụng góp phần cải thiện tính tương tác cho bệnh nhân, bệnh nhân dễ dàng đặt lịch khám, theo dõi tiến trình khám và quản lý kết quả khám bệnh của mình một cách nhanh chóng. 

   - Tích hợp hệ thống thanh toán trực tuyến cho bệnh nhân, góp phần giảm thiểu tối đa thời gian chờ đợi tại bệnh viện. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_115_ 

**Đồ án tốt nghiệp ngành Công nghệ thông tin** 

# **TÀI LIỆU THAM KHẢO** 

**Tài liệu tiếng Việt** 

[1] Nguyễn Văn Ba, _Phân tích và thiết kế hệ thống thông tin_ , NXB Đại học Quốc gia Hà Nội, 2006. 

[2] Phan Anh Cang, Lê Thị Hạnh Hiền & Trần Phan An Trường, _Giáo trình Phát triển ứng dụng Web_ , Nhà xuất bản Khoa học & Kỹ thuật, Hà Nội, 2021. 

[3] Lê Đình Thanh & Nguyễn Việt Anh, _Giáo trình Phát triển ứng dụng Web (PTUD Web)_ , Trường Đại học Công nghệ – Đại học Quốc gia Hà Nội, Hà Nội, 2018. 

[4] Phan Hữu Phước, _Giáo trình: Mô-đun Lập trình Web với Laravel Framework_ , Trường Cao đẳng Kỹ thuật Công nghệ Bà Rịa – Vũng Tàu, 2020. 

[5] Bộ Y tế Việt Nam, _Quyết định 5316/QĐ-BYT ngày 22/12/2020 phê duyệt “Chương trình chuyển đổi số y tế đến năm 2025, định hướng đến năm 2030”_ , Hà Nội, 2020. 

[6] Bệnh viện Đa khoa Trung ương Thái Nguyên, _Báo cáo nghiệp vụ và nhu cầu tin học hóa quy trình quản lý khám chữa bệnh_ , Thái Nguyên, 2024. 

[7] Bùi Ngọc Quang, _Nghiên cứu và xây dựng chatbot tư vấn người dùng trong y tế da liễu_ , Luận văn Thạc sĩ Công nghệ Thông tin, Trường Đại học Công nghệ – Đại học Quốc gia Hà Nội, Hà Nội, 2022. 

**Tài liệu tiếng Anh** 

[8] G. Booch, R. Maksimchuk, M. Engle, and others, _Object-Oriented Analysis and Design with Applications_ , 3rd ed., Addison-Wesley, 2007. 

[9] S. Seixas, _Laravel: Up & Running – A Framework for Building Modern PHP Apps_ , 3rd ed., O’Reilly Media, 2024. 

[10] P. M. V. Bosch and D. C. Dietz, “Appointment scheduling in health care: Challenges and opportunities,” _Health Care Management Science_ , vol. 11, no. 1, pp. 43–52, 2008. 

[11] A. Aggarwal, R. L. Sanchez-Vazquez, and A. Sabherwal, “Artificial Intelligence–Based Chatbots for Promoting Health Behaviour Change: Systematic Review,” _Journal of Medical Internet Research_ , vol. 25, no. 4, e10007007, 2023. 

_SVTH: Nguyễn Trung Hiếu – Lớp: KHMTUD K66E_ 

_116_ 

