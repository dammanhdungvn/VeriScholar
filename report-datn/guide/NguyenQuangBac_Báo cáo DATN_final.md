## **<mark>BỘ GIÁO DỤC VÀ ĐÀO TẠO</mark> TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT ----------------**  **----------------** 

**NGUYỄN QUANG BẮC ĐỐ ÁN TỐT NGHIỆP** 

**NGÀNH CÔNG NGHỆ THÔNG TIN** 

**TÊN ĐỀ TÀI:  XÂY DỰNG MÔ HÌNH DATA WAREHOUSE VÀ ỨNG DỤNG PHÂN TÍCH DỮ LIỆU TÀI CHÍNH TRÊN NỀN TẢNG POWER BI** 

**HÀ NỘI 11/2025** 

## **BỘ GIÁO DỤC VÀ ĐÀO TẠO TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT ----------------**  **----------------** 

**ĐỒ ÁN TỐT NGHIỆP CHUYÊN NGÀNH KHOA HỌC MÁY TÍNH ỨNG DỤNG** 

# **ĐỀ TÀI** 

**XÂY DỰNG MÔ HÌNH DATA WAREHOUSE VÀ ỨNG DỤNG PHÂN TÍCH DỮ LIỆU TÀI CHÍNH TRÊN NỀN TẢNG POWER BI (Building a Data Warehouse Model and Applying Financial Data Analytics on Power BI)** 

**GIÁO VIÊN HƯỚNG DẪN SINH VIÊN THỰC HIỆN ThS. Nguyễn Thùy Dương Nguyễn Quang Bắc - 2121051042** 

**HÀ NỘI 11/2025** 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **MỤC LỤC** 

|**MỤC LỤC ............................................................................................................. 3**|
|---|
|**DANH MỤC KÝ HIỆU VÀ CHỮ VIẾT TẮT .................................................. 5**|
|**DANH MỤC HÌNH VẼ ....................................................................................... 6**|
|**DANH MỤC BẢNG BIỂU .................................................................................. 8**|
|**LỜI CẢM ƠN ....................................................................................................... 9**|
|**LỜI MỞ ĐẦU ..................................................................................................... 10**|
|**CHƯƠNG 1. TỔNG QUAN VỀ ĐỀ TÀI ......................................................... 11**|
|1.1. Lý do chọn đề tài ...................................................................................... 11|
|1.2. Mục tiêu của đề tài .................................................................................... 12|
|1.3. Nội dung nghiên cứu ................................................................................. 13|
|1.4. Phạm vi nghiên cứu .................................................................................. 14|
|1.5. Cơ sở khoa học và tính thực tiễn của đề tài .............................................. 15|
|1.5.1. Cơ sở khoa học .................................................................................. 15|
|1.5.1. Tính thực tiễn .................................................................................... 15|
|1.6. Bố cục của đồ án ....................................................................................... 16|
|**CHƯƠNG 2. CƠ SỞ LÝ THUYẾT .................................................................. 17**|
|2.1. Tổng quan về Data Warehouse ................................................................. 17|
|2.1.1. Kiến trúc của Data Warehouse .......................................................... 17|
|2.1.2. Cấu trúc dữ liệu cho Data Warehouse ............................................... 19|
|2.1.3. Các loại lược đồ của Data Warehouse .............................................. 21|
|2.1.4. Điểm khác biệt giữa Database, Data warehouse và Data lake .......... 28|
|2.2. Quy trình ETL dữ liệu .............................................................................. 32|
|2.2.1. Trích xuất dữ liệu .............................................................................. 32|
|2.2.2. Chuyển đổi dữ liệu ............................................................................ 33|
|2.2.3. Tải dữ liệu .......................................................................................... 34|
|2.2.4. So sánh ETL và ELT ......................................................................... 34|
|2.3. Khái quát về dữ liệu tài chính ................................................................... 37|
|2.4. Các công cụ, công nghệ sử dụng .............................................................. 39|
|2.4.1. SQL Server Integration Services (SSIS) ........................................... 39|
|2.4.2. SQL Server ........................................................................................ 41|
|2.4.2. Ngôn ngữ truy vấn SQL .................................................................... 42|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

3 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|2.4.3. Ngôn ngữ lập trình Python ................................................................ 43|
|---|
|2.4.4. Power BI ............................................................................................ 44|
|2.4.5. Microsoft Power Platform ................................................................. 46|
|**CHƯƠNG 3. THIẾT KẾ VÀ XÂY DỰNG MÔ HÌNH DATA WAREHOUSE**<br>**.............................................................................................................................. 48**|
|3.1. Khảo sát yêu cầu và dữ liệu ...................................................................... 48|
|3.2. Thiết kế mô hình Data Warehouse ........................................................... 53|
|3.2.1. Vùng Landing .................................................................................... 53|
|3.2.1. Vùng Staging ..................................................................................... 54|
|3.2.1. Vùng Atomic ..................................................................................... 55|
|3.3. Xây dựng luồng ETL dữ liệu .................................................................... 63|
|3.3.1. Luồng ETL tổng quan ....................................................................... 63|
|3.3.2. Xây quy trình ETL trên SSIS ............................................................ 64|
|**CHƯƠNG 4. ỨNG DỤNG PHÂN TÍCH DỮ LIỆU TÀI CHÍNH TRÊN**|
|**POWER BI ......................................................................................................... 71**|
|4.1. Tích hợp dữ liệu trên Data Warehouse với Power BI .............................. 71|
|4.2. Xây dựng các Dashboard báo cáo tài chính .............................................. 73|
|4.2.1. Báo cáo tổng quan Cân đối kế toán ................................................... 73|
|4.2.2. Báo cáo Cơ cấu tài sản chi tiết .......................................................... 74|
|4.2.3. Báo cáo Cơ cấu nguồn vốn chi tiết .................................................... 77|
|4.2.4. Báo cáo Tổng quan chuyển lưu tiền tệ .............................................. 80|
|4.2.5. Báo cáo Tổng quan kết quả kinh doanh ............................................ 82|
|4.2.6. Báo cáo Hiệu quả kinh doanh............................................................ 84|
|4.3. Trợ lý AI ................................................................................................... 87|
|4.4. Tự động cập nhật dữ liệu và gửi báo cáo trên Power Platform ................ 92|
|**KẾT LUẬN ......................................................................................................... 97**|
|**TÀI LIỆU THAM KHẢO ................................................................................. 99**|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

4 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **DANH MỤC KÝ HIỆU VÀ CHỮ VIẾT TẮT** 

|**Ký hiệu viết tắt**|**Từ viết tắt**|**Ý nghĩa**|
|---|---|---|
|BI|Business Intelligence|Kinh doanh thông minh|
|DWH|Data warehouse|Kho dữ liệu|
|Dim|Dimension|Ngữ cảnh dữ liệu|
|Fact|Fact|Dữ liệu định lượng|
|Dashboard|Dashboard|Bảng điều khiển trực quan|
|ETL|Extract - Transform - Load|Trích xuất - Chuyển đổi- Tải|
|ELT|Extract - Load - Transform|Trích xuất - Tải - Chuyển đổi|
|Flow|Flow|Luồng chạy|
|SCD|Slowly Changing Dimensions|Kích thước thay đổi chậm|
|STG|Staging|Vùng tạm|
|IT|Information Technology|Công nghệ thông tin|
|AI|Artificial Intelligence|Trí tuệ nhân tạo|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

5 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **DANH MỤC HÌNH VẼ** 

|_Hình 2. 1: Hình ảnh mô tả kiến trúc tổng thể của kho dữ liệu_............................ 18|
|---|
|_Hình 2. 2: Hình minh họa dữ kiện tạo ra nhiều chiều dữ kiện_............................ 19|
|_Hình 2. 3: Mô hình lược đồ hình sao_................................................................... 21|
|_Hình 2. 4: Mô hình ví dụ về mô hình sao_............................................................. 22|
|_Hình 2. 5: Mô hình lược đồ bông tuyết_................................................................ 23|
|_Hình 2. 6: Mô hình ví dụ về mô hình bông tuyết_.................................................. 24|
|_Hình 2. 7: Mô hình ví dụ so với mô hình bông tuyết_............................................ 25|
|_Hình 2. 8: Mô hình ví dụ so với mô hình sao_....................................................... 25|
|_Hình 2. 9: Mô hình lược đồ thiên hà_.................................................................... 26|
|_Hình 2. 10: Mô hình ví dụ về mô hình thiên hà_................................................... 27|
|_Hình 2. 11: Hình minh họa quy trình ETL dữ liệu_............................................... 32|
|_Hình 2. 12: Hình mô tả mục đích ETL_................................................................. 35|
|_Hình 2. 13: Hình mô tả mục đích ELT_................................................................. 35|
|_Hình 3. 1: Hình minh họa báo cáo cân đối kế toán…………………………………_48|
|_Hình 3. 2: Mô tả 3 tầng trong Data warehouse_................................................... 53|
|_Hình 3. 3: Các bảng lưu trữ tại vùng Landing_.................................................... 54|
|_Hình 3. 4: Các bảng dữ liệu được lưu trữ tại vùng Staging_................................ 54|
|_Hình 3. 5: Sơ đồ liên kết dữ liệu DWH_................................................................ 55|
|_Hình 3. 6: Mô tả quy trình ETL dữ liệu_............................................................... 63|
|_Hình 3. 7: Mô tả quy trình ETL trên SSIS_............................................................ 64|
|_Hình 3. 8: Sơ đồ mô tả Extract Data_................................................................... 65|
|_Hình 3. 9: Sơ đồ mô tả check delete_..................................................................... 66|
|_Hình 3. 10: Sơ đồ mô tả transformation_.............................................................. 67|
|_Hình 3. 11: Sơ đồ mô tả load các bảng dim_......................................................... 68|
|_Hình 3. 12: Sơ đồ mô tả load các bảng fact_......................................................... 69|
|_Hình 3. 13: Sơ đồ mô tả update delete trong Atomic_........................................... 70|
|_Hình 4. 1: Hình minh họa bảng dữ liệu fact lưu chuyển tiền tệ trong DWH……._71|
|_Hình 4. 2: Kết nối Power Bi với Data Warehouse_............................................... 72|
|_Hình 4. 3: Mô hình quan hệ các bảng dữ liệu được tải lên Power BI_................. 72|
|_Hình 4. 4: Báo cáo tổng quan cân đối kế toán_.................................................... 73|
|_Hình 4. 5: Biểu đồ cơ cấu tổng tài sản_................................................................ 73|
|_Hình 4. 6: Báo cáo cơ cấu tài sản chi tiết_............................................................ 75|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

6 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|_Hình 4. 7: Biểu đồ chỉ số thanh toán_................................................................... 75|
|---|
|_Hình 4. 8: Biểu đồ chỉ tiêu hiệu quả hoạt động_................................................... 76|
|_Hình 4. 9: Biểu đồ thể hiện cơ cấu tài sản_........................................................... 76|
|_Hình 4. 10: Báo cáo cơ cấu nguồn vốn chi tiết_.................................................... 77|
|_Hình 4. 11: Biểu đồ thể hiện biến động chỉ tiêu nguồn vốn_................................. 78|
|_Hình 4. 12: Biểu đồ cơ cấu vốn vay ngắn và dài hạn_.......................................... 78|
|_Hình 4. 13: Biểu đồ biến động nguồn vốn_........................................................... 79|
|_Hình 4. 14: Báo cáo tổng quan chuyển lưu tiền tệ_.............................................. 80|
|_Hình 4. 15: Biểu đồ thể hiện tiền mặt cuối kỳ_...................................................... 80|
|_Hình 4. 16: Biểu đồ biến động dòng tiền vào và ra_............................................. 81|
|_Hình 4. 17: Biểu đồ dòng tiền theo nguồn gốc_.................................................... 82|
|_Hình 4. 18: Báo cáo tổng quan kết quả kinh doanh_............................................ 83|
|_Hình 4. 19: Biểu đồ cơ cấu lợi nhuận trước thuế_................................................ 83|
|_Hình 4. 20: Biểu đồ lợi nhuận thu và chi_............................................................. 84|
|_Hình 4. 21: Báo cáo Hiệu quả kinh doanh_.......................................................... 85|
|_Hình 4. 22: Biểu đồ nhóm chỉ số chi phí_.............................................................. 85|
|_Hình 4. 23: Biểu đồ cơ cấu chi phí theo tháng_.................................................... 86|
|_Hình 4. 24: API key của OpenAI_.......................................................................... 87|
|_Hình 4. 25: Sơ đồ luồng cho trợ lý AI tích hợp chatgpt_....................................... 88|
|_Hình 4. 26: Minh họa chatbot về bảng dữ liệu_.................................................... 89|
|_Hình 4. 27: Minh họa chatbot về các cột dữ liệu trong bảng_.............................. 89|
|_Hình 4. 28: Minh họa chatbot vẽ biểu đồ_............................................................ 90|
|_Hình 4. 29: Minh họa cahtbot yêu cầu tạo câu truy vấn_..................................... 90|
|_Hình 4. 30: Minh họa chatbot trợ lý AI_............................................................... 91|
|_Hình 4. 31: Dashboard và dữ liệu trong worksapce PowerBi service_................ 92|
|_Hình 4. 32: Báo cáo được đẩy lên môi trường service_........................................ 92|
|_Hình 4. 33: Luồng resfresh dữ liệu trên PowerApps_........................................... 93|
|_Hình 4. 34: Thông báo được gửi khi cập nhật thành công_.................................. 94|
|_Hình 4. 35: Cấu hình lập lịch cho việc gửi báo cáo_............................................ 94|
|_Hình 4. 36: Báo cáo được gửi tự động qua email_................................................ 95|
|_Hình 4. 37: Lịch sử luồng chạy tự động ..............................................................._95|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

7 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **DANH MỤC BẢNG BIỂU** 

|_Bảng 2. 1: Bảng so sánh giữa bảng Fact và bảng Dim_....................................... 20|
|---|
|_Bảng 2. 2: Bảng so sánh các mô hình lược đồ_..................................................... 28|
|_Bảng 2. 3: Bảng so sánh Database và Data Warehouse_..................................... 30|
|_Bảng 2. 4: Bảng so sánh Data Lake và Data Warehouse_.................................... 31|
|_Bảng 2. 5: So sánh ETL và ELT_........................................................................... 35|
|_Bảng 3. 1: Bảng dữ liệu cân đối kế toán…………………………………………….._50|
|_Bảng 3. 2: Bảng dữ liệu danh mục cân đối kế toán_............................................. 50|
|_Bảng 3. 3: Bảng dữ liệu chỉ tiêu hiệu quả hoạt động_.......................................... 51|
|_Bảng 3. 4: Bảng dữ liệu báo cáo hợp nhất_.......................................................... 51|
|_Bảng 3. 5: Bảng dữ liệu danh mục báo cáo kinh doanh_...................................... 51|
|_Bảng 3. 6: Bảng dữ liệu báo cáo chuyển lưu tiền tệ_............................................ 52|
|_Bảng 3. 7: Bảng dữ liệu danh mục báo cáo chuyển lưu tiền tệ_........................... 52|
|_Bảng 3. 8: Bảng dữ liệu thông tin doanh nghiệp_................................................. 52|
|Bảng 3. 9:_Bảng dữ liệu dim_account_.................................................................. 56|
|_Bảng 3. 10: Bảng dữ liệu dim_account_level03_.................................................. 56|
|_Bảng 3. 11: Bảng dữ liệu dim_account_level02_.................................................. 57|
|_Bảng 3. 12: Bảng dữ liệu dim_account_level01_.................................................. 57|
|_Bảng 3. 13: Bảng dữ liệu dim_cf_item_................................................................. 57|
|_Bảng 3. 14: Bảng dữ liệu dim_pnl_dict_............................................................... 58|
|_Bảng 3. 15: Bảng dữ liệu dim_company_.............................................................. 58|
|_Bảng 3. 16: Bảng dữ liệu dim_kpi_....................................................................... 59|
|_Bảng 3. 17: Bảng dữ liệu dim_date_..................................................................... 60|
|_Bảng 3. 18: Bảng dữ liệu fact_balance_sheet_..................................................... 61|
|_Bảng 3. 19: Bảng dữ liệu fact_cashflow_.............................................................. 61|
|_Bảng 3. 20: Bảng dữ liệu fact_consolidated_........................................................ 62|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

8 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **LỜI CẢM ƠN** 

Em xin gửi lời cảm ơn chân thành và sâu sắc nhất tới trường Đại học Mỏ - Địa chất, đặc biệt là khoa Công nghệ thông tin cùng bộ môn Khoa học máy tính đã tạo điều kiện thuận lợi cho em trong suốt quá trình học tập và thực hiện đồ án tốt nghiệp.Chính nhờ môi trường học tập năng động cùng sự tận tâm giảng dạy của các thầy cô, em đã được trang bị những kiến thức nền tảng và kỹ năng chuyên môn quý báu để có thể vận dụng vào đề tài này cũng như trong công việc thực tế sau này. 

Em đặc biệt bày tỏ lòng biết ơn sâu sắc tới cô Nguyễn Thùy Dương, người đã trực tiếp hướng dẫn, định hướng và tận tình giúp đỡ em trong suốt quá trình thực hiện đồ án. Những góp ý và hướng dẫn của cô không chỉ giúp em hoàn thiện nội dung đề tài mà còn giúp em mở rộng tư duy, rèn luyện phương pháp làm việc khoa học và tự tin hơn trong nghiên cứu. 

Một lần nữa em xin trân trọng gửi lời cảm ơn chân thành tới các thầy cô trong Trường, Khoa và Bộ môn đã tận tình giảng dạy, dìu dắt, cùng toàn thể bạn bè đã luôn đồng hành, hỗ trợ và chia sẻ trong suốt quá trình học tập và thực hiện đồ án. 

Em xin chân thành cảm ơn! 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

9 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **LỜI MỞ ĐẦU** 

Trong bối cảnh chuyển đổi số đang diễn ra mạnh mẽ trên toàn cầu, dữ liệu đã trở thành tài sản cốt lõi quyết định sự phát triển và năng lực cạnh tranh của các tổ chức. Việc thu thập, lưu trữ và phân tích dữ liệu không chỉ mang lại cái nhìn toàn diện về hoạt động của doanh nghiệp mà còn giúp đưa ra những chiến lược kinh doanh chính xác và kịp thời. Dữ liệu hiện diện trong mọi lĩnh vực từ kinh tế, xã hội, giáo dục cho đến khoa học và đóng vai trò quan trọng trong quá trình ra quyết định ở mọi cấp độ. 

Hiện nay, các công ty, doanh nghiệp trong các lĩnh vực tài chính đang sở hữu dữ liệu rất đa dạng tới từ rất nhiều nguồn khác nhau. Tuy nhiên các công ty này đã và đang gặp rất nhiều khó khăn trong việc khai thác, tổng hợp lại các nguồn dữ liệu đó. 

Xuất phát từ thực trạng này, đề tài “ **Xây dựng mô hình Data Warehouse và ứng dụng phân tích dữ liệu tài chính trên nền tảng Power BI** ” được thực hiện với mục tiêu đề xuất và xây dựng một giải pháp kho dữ liệu tập trung, giúp doanh nghiệp chuẩn hóa, tích hợp và khai thác hiệu quả các nguồn dữ liệu sẵn có. Thông qua mô hình Data Warehouse, các công ty tài chính có thể dễ dàng truy xuất, phân tích và tổng hợp thông tin, từ đó hỗ trợ đưa ra các quyết định kinh doanh chính xác, kịp thời và nâng cao năng lực cạnh tranh trên thị trường. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

10 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **CHƯƠNG 1. TỔNG QUAN VỀ ĐỀ TÀI** 

### **1.1. Lý do chọn đề tài** 

Trong bối cảnh chuyển đổi số mạnh mẽ hiện nay, dữ liệu được xem là “nguồn dầu mỏ mới” của mọi tổ chức, đặc biệt là trong lĩnh vực tài chính - ngân hàng. Sự gia tăng nhanh chóng về khối lượng, tốc độ và sự đa dạng của dữ liệu đã mang lại cả cơ hội lẫn thách thức cho các doanh nghiệp. Việc quản lý, xử lý và khai thác dữ liệu một cách hiệu quả không chỉ giúp doanh nghiệp nắm bắt được tình hình hoạt động mà còn đóng vai trò then chốt trong việc đưa ra các quyết định chiến lược. 

Đối với các công ty tài chính, dữ liệu phát sinh từ rất nhiều nguồn: giao dịch cổ phiếu, báo cáo kết quả kinh doanh, cân đối kế toán, tài sản – vốn chủ sở hữu, thông tin khách hàng, dữ liệu thị trường, chỉ số định giá, tăng trưởng lợi nhuận… và nhiều nguồn dữ liệu khác. Tuy nhiên, thực tế cho thấy dữ liệu thường tồn tại ở nhiều hệ thống rời rạc, không đồng nhất về cấu trúc và định dạng. Điều này gây ra khó khăn lớn trong việc tổng hợp, chuẩn hóa và khai thác dữ liệu. Hơn nữa, dữ liệu thô thường chứa nhiều giá trị thiếu, không chính xác hoặc trùng lặp, dẫn đến việc phân tích bị sai lệch, làm giảm tính tin cậy của báo cáo. 

Trong khi đó, nhu cầu về phân tích dữ liệu tài chính ngày càng cao. Các nhà quản lý cần các báo cáo nhanh chóng, chính xác và trực quan để kịp thời đánh giá hiệu quả hoạt động, phát hiện rủi ro và đưa ra quyết định phù hợp. Nếu chỉ dựa trên các báo cáo truyền thống, được tổng hợp thủ công từ nhiều file rời rạc, thì vừa tốn nhiều thời gian, vừa khó đảm bảo tính chính xác và kịp thời. 

Chính vì vậy, việc xây dựng một hệ thống Data Warehouse tập trung để lưu trữ, tích hợp và chuẩn hóa dữ liệu tài chính từ nhiều nguồn khác nhau là hết sức cần thiết. Data Warehouse sẽ đóng vai trò như một “kho dữ liệu tập trung”, giúp giảm thiểu sự phân mảnh dữ liệu, đồng thời tạo nền tảng vững chắc cho các hệ thống phân tích và báo cáo. Khi dữ liệu đã được chuẩn hóa và quản lý tập trung, các công cụ phân tích như Power BI có thể dễ dàng kết nối, trực quan hóa và cung cấp những báo cáo tài chính sinh động, đa chiều và chính xác. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

11 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Đặc biệt, trong lĩnh vực tài chính, rủi ro từ việc ra quyết định dựa trên dữ liệu thiếu tin cậy có thể dẫn đến thiệt hại rất lớn. Do đó, việc triển khai Data Warehouse kết hợp với phân tích dữ liệu trên Power BI không chỉ mang lại giá trị trong việc nâng cao hiệu quả quản trị mà còn góp phần giảm thiểu rủi ro, tối ưu hóa hoạt động kinh doanh và hỗ trợ doanh nghiệp thích ứng tốt hơn với sự biến động của thị trường. 

Từ những yêu cầu cấp thiết đó, em quyết định lựa chọn đề tài “ **Xây dựng mô hình Data Warehouse và ứng dụng phân tích dữ liệu tài chính trên nền tảng Power BI** ” nhằm nghiên cứu, thiết kế và triển khai một giải pháp lưu trữ, phân tích dữ liệu tập trung, phục vụ cho công tác quản trị và hỗ trợ ra quyết định trong lĩnh vực tài chính. 

### **1.2. Mục tiêu của đề tài** 

Xuất phát từ những vấn đề đã nêu, đề tài hướng đến việc nghiên cứu, xây dựng và triển khai một hệ thống Data Warehouse tập trung, đóng vai trò như nền tảng lưu trữ và quản lý dữ liệu tài chính một cách nhất quán. Trên cơ sở đó, đề tài sử dụng công cụ Power BI để thực hiện phân tích, trực quan hóa và khai thác dữ liệu, giúp việc tiếp cận thông tin trở nên nhanh chóng và chính xác hơn. 

Cụ thể, các mục tiêu chính cần đạt được bao gồm: 

- ➢ Nghiên cứu cơ sở lý thuyết về Data Warehouse, phân tích dữ liệu và các phương pháp khai thác dữ liệu trong lĩnh vực tài chính. 

- ➢ Tìm hiểu và lựa chọn công nghệ phù hợp cho ETL, hệ quản trị cơ sở dữ liệu, Power BI… phục vụ cho việc xây dựng kho dữ liệu và phân tích. 

- ➢ Tiền xử lý và chuẩn hóa dữ liệu: làm sạch dữ liệu thô, xử lý dữ liệu thiếu, trùng lặp, sai định dạng để đảm bảo độ tin cậy. 

- ➢ Thiết kế và xây dựng mô hình Data Warehouse: xác định lược đồ dữ liệu, các bảng dữ liệu cần thiết nhằm lưu trữ tập trung và tối ưu cho truy vấn phân tích. 

- ➢ Xây dựng quy trình ETL: xử lý dữ liệu từ nguồn vào kho dữ liệu tập trung, đảm bảo dữ liệu được đồng bộ. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

12 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- ➢ Sử dụng Power BI để phân tích, trực quan hóa dữ liệu tài chính: xây dựng các dashboard, báo cáo động, biểu đồ trực quan để phản ánh các khía cạnh quan trọng như doanh thu, lợi nhuận, tài sản, hiệu quả kinh doanh, chuyển lưu tiền tệ cho công ty trong lĩnh vực tài chính. 

- ➢ Triển khai và đồng bộ dữ liệu lên Power BI Service: Tự động làm mới dữ liệu sau mỗi chu kỳ nạp, đảm bảo các dashboard luôn hiển thị thông tin mới nhất. 

- ➢ Thiết lập cơ chế gửi báo cáo tự động trên nền tảng Power Platform: Cấu hình Power BI để xuất báo cáo định kỳ dưới dạng PDF hoặc hình ảnh và gửi đến email người dùng theo lịch, giúp lãnh đạo và các bộ phận liên quan nắm bắt tình hình kịp thời mà không cần thao tác thủ công. 

- ➢ Xây dựng chatbot trợ lý AI tích hợp OpenAI hỗ trợ người dùng sử dụng kho dữ liệu được xây dựng, đưa ra gợi ý các câu truy vấn SQL giúp người dùng dễ dàng truy vẫn dữ liệu. 

### **1.3. Nội dung nghiên cứu** 

Xuất phát từ những mục tiêu đã xác định, đề tài sẽ được triển khai thông qua các nội dung nghiên cứu sau: 

- ➢ Nghiên cứu tổng quan về Data Warehouse: tìm hiểu kiến trúc, các mô hình thiết kế phổ biến, quy trình xây dựng và vai trò của Data Warehouse trong việc quản lý tập trung và phân tích dữ liệu tài chính. 

- ➢ Nghiên cứu các công cụ và công nghệ phục vụ triển khai đề tài: bao gồm SQL để thiết kế và quản lý cơ sở dữ liệu, công cụ ETL để tích hợp dữ liệu từ nhiều nguồn, và Power BI để trực quan hóa và phân tích dữ liệu. 

- ➢ Nghiên cứu các phương pháp tiền xử lý và làm sạch dữ liệu: chuẩn hóa định dạng dữ liệu, xử lý dữ liệu thiếu, dữ liệu trùng lặp, và chuẩn hóa các chỉ tiêu tài chính để đảm bảo tính nhất quán và chính xác. 

- ➢ Phân tích đặc trưng dữ liệu tài chính: nghiên cứu cấu trúc dữ liệu báo cáo tài chính, bảng cân đối kế toán, báo cáo kết quả kinh doanh và các chỉ số tài chính từ đó xác định các bảng Fact và Dimension cần thiết trong Data Warehouse. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

13 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- ➢ Thiết kế và xây dựng mô hình Data Warehouse: tổ chức dữ liệu theo mô hình quan hệ, thiết kế các bảng Fact, Dimension và luồng ETL để nạp dữ liệu, đảm bảo tính toàn vẹn, khả năng mở rộng và hiệu quả trong truy vấn. 

- ➢ Sử dụng Power BI cho trực quan hóa và phân tích dữ liệu: xây dựng báo cáo, dashboard thể hiện các chỉ số tài chính quan trọng, phân tích xu hướng, phát hiện rủi ro và hỗ trợ quá trình ra quyết định trong lĩnh vực tài chính. 

- ➢ Sử dụng Power automate để xây dựng các luồng tự động cập nhật dữ liệu cũng nhưu gửi báo cáo tự động. 

### **1.4. Phạm vi nghiên cứu** 

Phạm vi nghiên cứu của đề tài tập trung vào việc xây dựng mô hình Data Warehouse lưu trữ tập trung, nhằm tận dụng ưu điểm về khả năng mở rộng, tính linh hoạt và hiệu quả trong quản lý dữ liệu tài chính. Giúp giảm thiểu chi phí đầu tư hạ tầng ban đầu mà còn đảm bảo khả năng đáp ứng nhu cầu truy xuất dữ liệu nhanh chóng, an toàn và phù hợp với xu hướng chuyển đổi số trong ngành tài chính. 

Về dữ liệu đầu vào, đề tài giới hạn phạm vi nghiên cứu trong các báo cáo tài chính cơ bản và quan trọng nhất, bao gồm: 

- ➢ Bảng cân đối kế toán: phản ánh tình hình tài sản, nợ phải trả và vốn chủ sở hữu tại một thời điểm nhất định. 

- ➢ Báo cáo lưu chuyển tiền tệ: cung cấp thông tin về dòng tiền vào – ra trong kỳ, giúp đánh giá khả năng thanh toán và quản lý dòng tiền. 

- ➢ Báo cáo kết quả kinh doanh hợp nhất: thể hiện doanh thu, chi phí và lợi nhuận, hỗ trợ phân tích hiệu quả hoạt động kinh doanh. 

- ➢ Một số chỉ số tài chính tổng hợp khác như: khả năng sinh lời (ROA, ROE, Gross Profit Margin), khả năng thanh khoản (Liquidity Ratios), và khả năng thanh toán dài hạn (Solvency Ratios). 

Trong khuôn khổ đề tài, nội dung nghiên cứu tập trung vào: 

- ➢ Thiết kế mô hình dữ liệu đa chiều với các bảng fact và dimension nhằm lưu trữ, chuẩn hóa và tích hợp dữ liệu tài chính từ nhiều nguồn khác nhau. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

14 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- ➢ Xây dựng quy trình ETL (Extract – Transform – Load): để làm sạch, chuẩn hóa dữ liệu, đồng thời đảm bảo tính toàn vẹn và nhất quán khi đưa vào Data Warehouse. 

- ➢ Triển khai báo cáo và dashboard phân tích trên nền tảng Power BI: trực quan hóa dữ liệu tài chính, hỗ trợ theo dõi hiệu quả kinh doanh, quản lý rủi ro và đưa ra quyết định. 

### **1.5. Cơ sở khoa học và tính thực tiễn của đề tài** 

### **_1.5.1. Cơ sở khoa học_** 

Về mặt khoa học, đề tài góp phần bổ sung và hệ thống hóa cơ sở lý thuyết liên quan đến việc xây dựng Data Warehouse trong lĩnh vực tài chính. Điểm nổi bật là sự kết hợp giữa mô hình dữ liệu tài chính với các phương pháp trực quan hóa hiện đại bằng Power BI, giúp hình thành cách tiếp cận toàn diện từ khâu thiết kế, quản lý đến khai thác dữ liệu. 

Một số đóng góp cụ thể về khoa học có thể kể đến: 

- ➢ Đề tài cụ thể hóa việc áp dụng các mô hình dữ liệu quan hệ - đa chiều vào bài toán tài chính, từ đó minh họa rõ mối liên hệ giữa lý thuyết dữ liệu và các chỉ số tài chính trong thực tế. 

- ➢ Đề tài không dừng lại ở việc trình bày các báo cáo tài chính dưới dạng tĩnh, mà đề xuất cách triển khai hệ thống báo cáo động, có thể phân tích, lọc và drill-down dữ liệu trực tiếp. Đây là bước cải tiến so với cách tiếp cận truyền thống. 

- ➢ Thông qua quá trình mô hình hóa và trực quan hóa, nghiên cứu cho thấy việc chuẩn hóa dữ liệu và tích hợp trong Data Warehouse không chỉ giúp tăng tính chính xác mà còn mở ra khả năng phân tích đa chiều, hỗ trợ dự báo rủi ro và hiệu quả kinh doanh. Đây là góc nhìn đáng chú ý trong bối cảnh khoa học dữ liệu ngày càng được ứng dụng rộng rãi. 

### **_1.5.1. Tính thực tiễn_** 

Về tính thực tiễn, ngành tài chính – ngân hàng hiện đang bước vào giai đoạn chuyển đổi số mạnh mẽ, trong đó dữ liệu được xem là tài sản chiến lược. Khối 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

15 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

lượng dữ liệu tài chính ngày càng lớn, phức tạp và đa dạng, bao gồm: báo cáo kết quả kinh doanh, bảng cân đối kế toán, dòng tiền, dữ liệu giao dịch chứng khoán, chỉ số thị trường và nhiều nguồn dữ liệu phi cấu trúc khác. Trong thực tế, việc quản lý dữ liệu thủ công hoặc phân tán dễ dẫn đến trùng lặp, sai lệch, khó khai thác, làm giảm hiệu quả quản trị và gia tăng rủi ro trong quyết định kinh doanh. Chính vì vậy, các doanh nghiệp tài chính, ngân hàng lớn đã và đang tập trung xây dựng hệ thống kho dữ liệu tập trung để chuẩn hóa, đồng bộ và khai thác dữ liệu một cách hiệu quả. 

Từ thực tiễn đó, đề tài có ý nghĩa rõ ràng: minh họa cách áp dụng một mô hình Data Warehouse trong quản lý và phân tích dữ liệu tài chính, kết hợp cùng Power BI để xây dựng các báo cáo trực quan, dễ hiểu và giàu thông tin. Đây sẽ là cơ sở tham khảo hữu ích cho những tổ chức tài chính mong muốn ứng dụng hệ thống kho dữ liệu hiện đại nhằm nâng cao hiệu quả phân tích, giảm thiểu rủi ro và hỗ trợ ra quyết định chiến lược. 

### **1.6. Bố cục của đồ án** 

Với yêu cầu và mục đích của đồ án này, nội dung nghiên cứu cụ thể sẽ được trình bày bao gồm 4 chương dưới đây: 

- ➢ **Chương 1: Tổng quan về đề tài** - Trình bày lý do chọn đề tài, mục tiêu, phạm vi, cơ sở khoa học và thực tiễn. Đồng thời khái quát tầm quan trọng của dữ liệu tài chính và định hướng nghiên cứu. 

- ➢ **Chương 2: Cơ sở lý thuyết** - Trình bày tổng quan về các khái niệm, cơ sở lý thuyết và các công nghệ được ứng dụng để xây dựng mô hình Data Warehouse. 

- ➢ **Chương 3: Thiết kế và xây dựng mô hình hệ thống Data Warehouse** - Trình bày về thiết kế mô hình hệ thống, thiết kế cấu trúc các bảng lưu trữ và tiến hành xây dựng mô hình hệ thống. 

- ➢ **Chương 4: Ứng dụng phân tích dữ liệu tài chính trên Power BI** - Kết nối và khai thác dữ liệu từ Data Warehouse bằng Power BI, xây dựng các dashboard trực quan, phân tích các chỉ số tài chính. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

16 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **CHƯƠNG 2. CƠ SỞ LÝ THUYẾT** 

### **2.1. Tổng quan về Data Warehouse** 

### **_2.1.1. Kiến trúc của Data Warehouse_** 

Data Warehouse (DWH) hay còn gọi là kho dữ liệu là một hệ thống lưu trữ dữ liệu có tổ chức, được thiết kế để tập hợp thông tin từ nhiều nguồn khác nhau như phần mềm bán hàng, kế toán, quản lý nhân sự, hệ thống lõi ngân hàng, hoặc các hệ thống nghiệp vụ chuyên biệt khác. Điểm mạnh của Data Warehouse nằm ở khả năng tích hợp dữ liệu từ nhiều môi trường không đồng nhất, xử lý và chuẩn hóa chúng, sau đó lưu trữ trong một cấu trúc chung, cho phép việc khai thác trở nên nhanh chóng, chính xác và hiệu quả hơn. Nhờ đó, Data Warehouse không chỉ đóng vai trò là nơi lưu trữ, mà còn trở thành nền tảng quan trọng phục vụ cho báo cáo quản trị, phân tích kinh doanh và hỗ trợ ra quyết định chiến lược. 

Về bản chất, Data Warehouse hoạt động như một kho lưu trữ trung tâm. Dữ liệu được đưa vào kho từ các hệ thống giao dịch và nhiều cơ sở dữ liệu liên quan khác. Trước khi đến tay người dùng, dữ liệu được xử lý và chuyển đổi để đảm bảo tính toàn vẹn, thống nhất và độ chính xác. Sau đó, dữ liệu đã được chuẩn hóa có thể được truy cập và khai thác thông qua các công cụ Business Intelligence (BI), các công cụ trực quan hóa dữ liệu như Power BI, Tableau hoặc thậm chí thông qua SQL client, Excel, và các hệ thống báo cáo khác. 

Mô hình kiến trúc cơ bản của Data Warehouse thường bao gồm bốn thành phần chính: 

- Dữ liệu nguồn (Data Sources): Là dữ liệu đầu vào, được lấy từ nhiều hệ thống khác nhau như cơ sở dữ liệu quan hệ (Oracle, SQL Server, MySQL…), file Excel, CSV, hoặc từ các hệ thống ứng dụng nghiệp vụ. Đây chính là "nguyên liệu thô" cần được tập hợp để phục vụ cho quá trình phân tích. 

- Khu xử lý dữ liệu (Staging/ETL Processing): Đây là giai đoạn dữ liệu được thu thập, làm sạch, chuẩn hóa và chuyển đổi theo một mô hình cụ thể. Quá 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

17 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

   - trình này thường được thực hiện thông qua cơ chế ETL (Extract - Transform - Load), giúp loại bỏ dữ liệu trùng lặp, xử lý dữ liệu bị thiếu, đồng bộ hóa định dạng, đồng thời chuyển đổi dữ liệu theo đúng cấu trúc yêu cầu của kho dữ liệu. 

- Kho lưu trữ dữ liệu (Data Warehouse Storage): Sau khi đã được xử lý và chuẩn hóa, dữ liệu sẽ được nạp vào kho dữ liệu. Tại đây, dữ liệu được tổ chức theo các mô hình đặc trưng như mô hình hình sao (Star Schema) hoặc mô hình bông tuyết (Snowflake Schema), với các bảng fact lưu trữ số liệu định lượng và các bảng dimension lưu trữ thông tin mô tả, nhằm hỗ trợ tối ưu cho việc truy vấn, phân tích và tạo báo cáo. 

- Người dùng cuối: Đây là đối tượng trực tiếp khai thác dữ liệu từ kho dữ liệu thông qua các công cụ phân tích, trực quan hóa và báo cáo. Người dùng cuối có thể là nhà quản lý, chuyên viên phân tích, hoặc nhân viên nghiệp vụ cần dữ liệu để đưa ra quyết định kinh doanh. Họ có thể thực hiện các thao tác từ đơn giản (xem báo cáo định kỳ) đến phức tạp (khai phá dữ liệu, xây dựng mô hình phân tích dự báo). 



<!-- Start of picture text -->
=<br>yg<br>=> Dachitu liguda —<br>SS =<br>ES<br>Bio cdo Bio bio<br>Hé thing<br>ngudn =<br>Khai pha dit ligu<br><!-- End of picture text -->

_Hình 2. 1: Hình ảnh mô tả kiến trúc tổng thể của kho dữ liệu_ 

Như vậy, Data Warehouse không chỉ đơn thuần là nơi tập hợp dữ liệu mà còn là một hệ thống được thiết kế có chủ đích, nhằm phục vụ cho các nhu cầu phân 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

18 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

tích ở mức độ chiến lược. Nó giúp doanh nghiệp và tổ chức không còn phải mất nhiều thời gian cho việc truy xuất thủ công từ nhiều hệ thống, mà thay vào đó có thể dễ dàng truy cập dữ liệu tập trung, nhất quán, đáng tin cậy và được cập nhật theo thời gian. Điều này mang lại lợi thế lớn trong việc phát hiện xu hướng, đánh giá hiệu quả hoạt động, dự báo tương lai và hỗ trợ ra quyết định dựa trên dữ liệu. 

### **_2.1.2. Cấu trúc dữ liệu cho Data Warehouse_** 

Trong Data Warehouse, dữ liệu thường được tổ chức và quản lý theo mô hình đa chiều (Multidimensional Model). Mô hình này gồm hai loại bảng chính: Fact (bảng sự kiện) và Dimension (bảng chiều). Đây là cấu trúc cốt lõi giúp tối ưu cho việc lưu trữ, phân tích và trực quan hóa dữ liệu trong các công cụ BI (Business Intelligence) như Power BI. 



<!-- Start of picture text -->
Neeser<br>We<br>aN<br><!-- End of picture text -->

_Hình 2. 2: Hình minh họa dữ kiện tạo ra nhiều chiều dữ kiện_ 

Bảng Dimension là bảng chứa các thuộc tính (attributes) mô tả các thông tin của 01 chiều (dimension) của dữ liệu. Bạn có thể hiểu nôm nay cứ một bảng dimension thường sẽ ứng với một loại đối tượng (class hoặc type) trong hiện thực. Mỗi dòng trong bảng đó là một đối tượng (object) thực tế. 

Bảng Fact là bảng chứa các thông tin số lượng (measurements) của dữ liệu. Thông thường, bảng Fact được xây dựng từ các raw data, và được thống kê theo giờ, ngày, tuần, tháng và năm. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

19 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

_Bảng 2. 1: Bảng so sánh giữa bảng Fact và bảng Dim_ 

|**Đặc điểm**|**Bảng Fact**|**Bảng Dimension**|
|---|---|---|
|Định nghĩa|Bao gồm các chỉ số đo lường<br>các hoạt động trong tổ chức.|Bảng thông tin các đối tượng<br>có liên quan tới bảng Fact.|
|Thuộc tính|Trung tâm trong Star schema<br>và Snowflake schema, xung<br>quanh là các bảng Dim.|Nằm xung quanh bảng Fact<br>trong Star schema và<br>Snowflake Schema.|
|Thiết kế|Thiết kế đúng với trọng tâm<br>của vấn đề hay nhu cầu.|Phải bao quát các thông tin<br>của một đối tượng. Tránh<br>nhét vào nhiều thông tin của<br>nhiều đối tượng cùng một<br>nơi.|
|Phục vụ|Một bảng Fact tập hợp các<br>chỉ số đo lượng có liên quan<br>tới các bảng Dim, dùng cho<br>báo cáo, thống kê.|Thu thập các thông tin liên<br>quan tới một đối tượng nào<br>đó trong tổ chức (như thông<br>tin cửa hàng chẳng hạn).|
|Kiểu dữ liệu|Bảng Fact chứa các cột dữ<br>liệu số liên quan tới các cột<br>đối tượng, khoá ngoại của<br>bảng Dim.|Mỗi bảng Dim chứa các<br>thông tin về một đối tượng.<br>Ví dụ bảng Product gồm<br>Product Id, Category,<br>SubCategory…|
|Khoá chính|Khoá chính của bảng Fact là<br>tập hợp không lặp lại các<br>khoá ngoại từ các bảng Dim.|Mỗi bảng Dim đều có một<br>khoá chính để xác định rõ<br>tính độc nhất của mỗi dòng<br>trong bảng.|
|Lưu trữ|Được dùng để lưu trữ chỉ số,<br>đồng thời để lọc kết quả trên<br>nó dựa theo thông tin từ các<br>bảng Dim.|Lưu trữ dữ liệu các đối tượng<br>một cách chi tiết.|
|Sự phân cấp|Không có.|Có sự phân cấp: Ví dụ đối<br>tượng Địa Điểm có thể chứa<br>Quốc Gia, Khu vực,<br>Quận/Huyện, Mã Zip…|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

20 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **_2.1.3. Các loại lược đồ của Data Warehouse_** 

### *** Mô hình sao (Star Schema)** 

Lược đồ hình sao là dạng cơ bản của mô hình chiều, trong đó dữ liệu được tổ chức thành các dữ kiện và các chiều. Thực tế là một sự kiện được tính hoặc đo lường, chẳng hạn như bán hàng hoặc đăng nhập. Thứ nguyên bao gồm dữ liệu tham chiếu về thực tế, chẳng hạn như ngày, mặt hàng hoặc khách hàng. 



<!-- Start of picture text -->
Fact Table<br><!-- End of picture text -->

_Hình 2. 3: Mô hình lược đồ hình sao_ 

Star Schema là một lược đồ quan hệ trong đó một lược đồ quan hệ có thiết kế đại diện cho một mô hình dữ liệu đa chiều. Star Schema là lược đồ kho dữ liệu rõ ràng. Nó được gọi là giản đồ sao vì biểu đồ mối quan hệ thực thể của lược đồ này mô phỏng một ngôi sao, với các điểm, phân kỳ từ một bảng trung tâm. Trung tâm của lược đồ bao gồm một bảng dữ kiện lớn và các điểm của ngôi sao là bảng kích thước. 

Ví dụ: Giả sử một giản đồ hình sao bao gồm một bảng dữ kiện, SALES và một số bảng thứ nguyên được kết nối với nó cho thời gian, chi nhánh, mặt hàng và vị trí địa lý. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

21 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Bảng TIME có một cột cho mỗi ngày,tháng, quý và năm. Bảng ITEM có các cột cho từng item_Key, item_name, brand, type, provider_type. Bảng BRANCH có các cột cho mỗi branch_key, branch_name, branch_type. Bảng LOCATION có các cột dữ liệu địa lý, bao gồm đường phố, thành phố, tiểu bang và quốc gia. 



<!-- Start of picture text -->
Dimension Table Dimension Table<br>time_key<br>day Sales Fact Table<br>day_of_the_week<br>zo —ae<br>Quarter<br>ra ae<br>|__ location key | Dimension Table<br>Dimension Table =<br><!-- End of picture text -->

_Hình 2. 4: Mô hình ví dụ về mô hình sao_ 

Trong trường hợp này, bảng SALES chỉ chứa bốn cột có ID từ bảng thứ nguyên, TIME, ITEM, BRANCH và LOCATION, thay vì bốn cột cho dữ liệu thời gian, bốn cột cho dữ liệu ITEM, ba cột cho dữ liệu BRANCH và bốn cột cho dữ liệu LOCATION. Như vậy, kích thước của bảng dữ kiện được giảm đi đáng kể. Khi cần thay đổi một mục, chúng ta chỉ cần thực hiện một thay đổi duy nhất trong bảng thứ nguyên, thay vì thực hiện nhiều thay đổi trong bảng dữ kiện. 

### *** Mô hình bông tuyết (Snowflake Schema)** 

Snowflake Schema là sự mở rộng của lược đồ sao trong đó mỗi điểm của ngôi sao bùng nổ thành nhiều điểm hơn. Nó được gọi là giản đồ Snowflake vì biểu đồ của giản đồ Snowflake giống với một bông tuyết. Snowflaking là một phương pháp chuẩn hóa bảng dimension trong lược đồ STAR. Khi chúng tôi chuẩn hóa hoàn toàn tất cả các bảng kích thước, cấu trúc kết quả giống như một bông tuyết với bảng dữ kiện ở giữa. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

22 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Snowflaking được sử dụng để phát triển hiệu suất của các truy vấn cụ thể. Lược đồ được lập sơ đồ với mỗi dữ kiện được bao quanh bởi các dimension liên quan của nó và những dimension đó có liên quan đến các dimension khác, phân nhánh thành một mô hìnhSnowflake. 

Snowflake Schema bao gồm một bảng dữ kiện được liên kết với nhiều bảng dimension, có thể được liên kết với các bảng dimension khác thông qua mối quan hệ nhiều đối một. Các bảng trong Snowflake Schema thường được chuẩn hóa thành dạng chuẩn thứ ba. Mỗi bảng dimension thực hiện chính xác một cấp trong hệ thống phân cấp. 



<!-- Start of picture text -->
samumm Dimension! ummm Dimension? mumam= Dimension?<br>me Level3 momen Level2 moos Level<br>4<br>H d<br>Sa Facttable<br>CT 1<br>J<br>a<br>1<br>mamm=men Dimension2Level3 samamameme Dimension2Level2 samamamene DimensionLevel] 2<br>q<br>H H<br><!-- End of picture text -->

_Hình 2. 5: Mô hình lược đồ bông tuyết_ 

Ví dụ:  Hình cho thấy một Snowflake Schema với bảng dữ kiện Bán hàng, với các bảng dimension Cửa hàng, Vị trí, Thời gian, Sản phẩm, Dòng và Gia đình. dimension Thị trường có hai bảng dimension với Cửa hàng là bảng dimension chính và Vị trí là bảng dimension bên ngoài. dimension sản phẩm có ba bảng dimension với Sản phẩm là bảng dimension chính và bảng Dòng và Dòng là bảng dimension bên ngoài. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

23 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
Location<br>Postal code ID<br>Postal code<br>Region name<br>Region director<br>State name<br>State director<br>State population<br>City name<br>City population<br>Family<br>Store<br>Family ID<br>Store ID Family name<br>StoreStore namesize Family description<br>Store address Sales fact Line<br>Postal code ID Store ID<br>Time TimeProduct ID ID Line  IDname<br>Time ID SaleCost of goods sold Line description<br>Advertising<br>Year FamilyID<br>Quarter number Product<br>Quater name<br>Month number Product ID<br>Month name Product name<br>Week of year Product description<br>Day name Product ounces<br>Weekday Product caffeinated<br>Holiday Line ID<br>Day of year<br>Day of month<br>Fiscal year<br>Fiscal quarter number<br>Fiscal month number<br><!-- End of picture text -->

_Hình 2. 6: Mô hình ví dụ về mô hình bông tuyết_ 

Một giản đồ hình sao lưu trữ tất cả các thuộc tính cho một dimension vào một bảng không chuẩn hóa. Điều này cần nhiều dung lượng đĩa hơn so với một giản đồ snowflake chuẩn hóa hơn. snowflaking chuẩn hóa dimension bằng cách di chuyển các thuộc tính có số lượng thấp vào các bảng dimension riêng biệt có liên quan đến bảng dimension cốt lõi bằng cách sử dụng các khóa ngoại. Không nên trượt tuyết với mục đích duy nhất là giảm thiểu dung lượng ổ đĩa, vì nó có thể tác động xấu đến hiệu suất truy vấn. 

Trong snowflake, các bảng lược đồ được chuẩn hóa để xóa phần dư thừa. Trong các bảng kích thướcSnowflake bị hỏng thành các bảng nhiều kích thước. 

Hình cho thấy một giản đồ sao đơn giản để bán hàng trong một công ty sản xuất. Bảng thông tin bán hàng bao gồm số lượng, giá cả và các chỉ số liên quan khác. SALESREP, CUSTOMER, PRODUCT và TIME là các bảng dimension. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

24 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
PRODUCT CUSTOMER<br>Customer Key<br>ProductProductnameKey CustomerCustomercodename<br>Product code Marital status<br>Brand name ‘Address<br>Product category State<br>Package type Zip<br>SALES FACTS<br>Product Key<br>Time key<br>"CustomerSalesrep KeyKey 7<br>Sales dollars<br>TIME SALESREP<br>Ah Salesrep Key<br>Quarter Terttory name<br>Yor Region name<br>STAR Schema<br><!-- End of picture text -->

_Hình 2. 7: Mô hình ví dụ so với mô hình bông tuyết_ 

Lược đồ STAR cho bán hàng, như được hiển thị ở trên, chỉ chứa năm bảng, trong khi phiên bản chuẩn hóa hiện mở rộng đến mười một bảng. Chúng ta sẽ nhận thấy rằng trong Snowflake Schema, các thuộc tính có số lượng thấp trong mỗi bảng kích thước ban đầu sẽ bị loại bỏ để tạo thành các bảng riêng biệt. Các bảng mới này được kết nối trở lại bảng kích thước ban đầu thông qua các khóa nhân tạo. 



<!-- Start of picture text -->
CATEGORY COUNTRY<br>cata kay CUSTOMER Gey<br>Product Category | country nama<br>BRAND X CustomernameCustomerkey 7 §<br>Brand Key PRODUCT ee<br>Brand namo Soman Sue<br>2129002 FE productoduct nameKey Zip REGION<br>Product code Country Key<br><n Region Key<br>Y randkey Region name<br>PACKAGE, SALESFACTS TERRITORY<br>Package Key 7<br>package type Ny Productkey Territory Key<br>Customer‘Time KeyKey TerritoryRS name<br>TIME SalesSalesrepquantityKey,<br>JZ Sales dollars SALESREP<br>Time Key salespriceMargin =— NNN<br>Data Salesrap Key I<br>Month Salesperson name<br>QuarterYear TerritoryKey<br>Snowflake Schema<br><!-- End of picture text -->

_Hình 2. 8: Mô hình ví dụ so với mô hình sao_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

25 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Snowflake Schema được thiết kế để truy vấn linh hoạt trên các dimension và mối quan hệ phức tạp hơn. Nó phù hợp với nhiều đến nhiều và một đến nhiều mối quan hệ giữa các mức dimension. 

   - Lợi thế của Snowflake 

      - Ưu điểm chính của Snowflake Schema là sự phát triển về hiệu suất truy vấn do các yêu cầu lưu trữ đĩa được giảm thiểu và tham gia các bảng tra cứu nhỏ hơn. 

      - Nó cung cấp khả năng mở rộng lớn hơn trong mối quan hệ qua lại giữa các mức dimension và các thành phần. 

      - Không dư thừa nên dễ bảo trì hơn. 

   - Nhược điểm của Snowflake Schema 

      - Nhược điểm chính của Snowflake Schema là cần phải có thêm các nỗ lực bảo trì do số lượng bảng tra cứu ngày càng tăng. Nó còn được gọi là giản đồ sao đa sự thật. 

      - Có nhiều truy vấn phức tạp hơn và do đó, khó hiểu. 

      - Nhiều bảng hơn tham gia nên thời gian thực hiện truy vấn nhiều hơn. 

- **Mô hình thiên hà (Galaxy Schema)** 



<!-- Start of picture text -->
Branch JD<br>Dealer JO / Address<br>Locating<br>~ Branch<br>Country 3D | Ravens // Country \ Product<br>Dealer_NM DhID , Product.Product Name| |Ba Fragareat<br>Revenue XN Date Dim VA VariantJD<br>\.\)| DateJD VA<br>Year | /<br>Month //<br>Quarter<br>Date<br><!-- End of picture text -->

_Hình 2. 9: Mô hình lược đồ thiên hà_ 

Một galaxy schema sử dụng nhiều fact tables được kết nối với các bảng dim, trái ngược với star schema và snowflake schema, vốn chỉ sử dụng một fact table. Một galaxy schema có sự liên kết chặt chẽ và được chuẩn hóa, gần như loại bỏ hoàn toàn sự dư thừa và không nhất quán của dữ liệu. Galaxy schemas được 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

26 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

biết đến với độ chính xác và chất lượng dữ liệu cao, đồng thời cung cấp nền tảng cho việc phân tích và báo cáo hiệu quả, khiến chúng trở thành một lựa chọn mạnh mẽ cho các hệ thống cơ sở dữ liệu phức tạp. 

Chúng ta có thể nhìn vào 2 mô hình trên như là 2 data mart, 1 là cho phòng bán hàng (sales) 2 là cho bộ phận nhà cung cấp (supply). Mỗi cái đó bao gồm chỉ một bảng fact và một vài bảng dimension. Nếu chúng ta muốn kết hợp 2 data mart vào làm một. Đây là kiểu mô hình chứa vài bảng fact và chia sẻ các bảng dimension nó được gọi là mô hình galaxy (galaxy schema). Chia sẻ các bảng dimension có thể giảm kích thước của cơ sở dữ liệu đặc biết là khi chia sẻ các bảng dimension có nhiều giá trị. Ý tưởng là các bảng dimension trong cả 2 data mart có chung 1 cách thức. Nếu không chúng ta sẽ phải căn chỉnh cho nó phù hợp với cả 2. 

Một mô hình thiên hà (galaxy schema) được xây dựng lên với 2 ví dụ data mart, được hiển thị như hình: 



<!-- Start of picture text -->
suoperid int<br>; = re supplier_addres varchar(256)<br>sales_type_i int city varchar(128)<br>typename varchar(128) eon varchar(128)<br>statecountry varchar(128)varchar(128)<br>ni 4<br>[feet sates f<br>product dint PKFK| productid int Px<br>time_id int PK FK Eso product_nam varchar(256) od product.id int FK<br>store id int PK FK’ product type varchar(256) time_id~ int FK<br>employee_id int PK FK| supplierid int PK FK|<br>sales_type_id int PK FK’<br>price o<| employeeid int FK<br>quantity decimal( s8 ,2) pricequantity decimal( s8 ,2)<br>yY WV [___dim_ e mpioyee | 4<br>‘employefirst_name id —_varchar(128)int PK<br>lastname —_varchar(128)<br>birth_year int<br>time id int PK<br>action date date<br>actionweek int<br>[dimstorestore id intstore Pk| action"monthaction_yearaction_weekda intintvarchar(16)<br>varchar(128)<br>city addres varchar(256)<br>region varchar(128)<br>state varchar(128)<br>country _varchar(128)<br><!-- End of picture text -->

_<mark>Hình 2. 10: Mô hình ví dụ về mô hình thiên hà</mark>_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

27 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

_<u>Bảng 2. 2: Bảng so sánh các mô hình lược đồ</u>_ 

|**Tiêu chí**|**Star Schema**|**Snowflake**<br>**Schema**|**Galaxy Schema**|
|---|---|---|---|
|Cấu trúc|Đơn giản, chỉ có 1<br>cấp (1 Fact Table<br>liên kết trực tiếp<br>với Dimension)|Phân nhánh, phân<br>cấp nhiều lớp|Nhiều Fact Table<br>cùng kết nối với<br>các Dimension, có<br>thể có phân cấp|
|Hiệu suất truy vấn|Nhanh|Chậm hơn|Chậm hơn cả Star<br>và Snowflake, phù<br>hợp cho phân tích<br>dữ liệu lớn và<br>phức tạp|
|Tính Dễ hiểu và<br>bảo trì|Cao|Thấp|Thấp|
|Mức độ chuẩn hóa<br>dữ liệu|Ít chuẩn hóa|Chuẩn hóa cao|Chuẩn hóa, gần<br>như loại bỏ dư<br>thừa dữ liệu|
|Khả năng mở rộng|Tốt trong phạm vi<br>báo cáo BI|Tốt hơn trong hệ<br>thống DW phức<br>tạp|Rất tốt cho hệ<br>thống lớn, phức<br>tạp, cần nhiều Fact<br>Table|



### **_2.1.4. Điểm khác biệt giữa Database, Data warehouse và Data lake_** 

### ❖ **Database** 

Database (cơ sở dữ liệu) là một bộ sưu tập dữ liệu được tổ chức bày bản và thường được truy cập từ hệ thống máy tính hoặc tồn tại dưới dạng tập tin trong hệ quản trị cơ sở dữ liệu. Database được sử dụng để lưu trữ, tìm kiếm và báo cáo về dữ liệu có cấu trúc từ một nguồn duy nhất. 

* Một số mô hình database phổ biến hiện nay: 

- Cơ sở dữ liệu dạng file: 

- + Thường gặp nhất, dữ liệu được lưu trữ dưới dạng file. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

28 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- + Dễ dàng truy xuất. 

- + Đơn giản trong việc tổ chức dữ liệu. 

- Cơ sở dữ liệu quan hệ: 

- + Các nguồn dữ liệu khác nhau sẽ cùng được quy hợp, lưu trữ cùng một bảng dữ liệu. 

- + Các dữ liệu này phải có quan hệ với nhau. 

- + Một số cơ sở dữ liệu có hỗ trợ Database quan hệ: Oracle, MS SQL Server. 

- Cơ sở dữ liệu hướng đối tượng: 

- + Cũng là một bảng dữ liệu thuần. 

- + Bổ sung thêm các trường hướng đối tượng khác như hành vi đối tượng. 

- + Các đối tượng này được phân cấp rõ ràng, mỗi cấp được gọi là một lớp dữ liệu. 

- + Tập hợp các nhóm đối tượng trong cùng 1 bảng và thể hiện bằng dòng dữ liệu. 

- Cơ sở dữ liệu bán cấu trúc: 

- + Có thể lưu trữ nhiều dạng dữ liệu khác nhau. 

- + Thường được lưu trữ dưới định dạng XML. 

- + Các thông tin mô tả dữ liệu và đối tượng đều được trinhg bày trong các tag. 

- + Vừa có thể dễ dạng mở rộng, vừa tiện lợi giúp người dùng có thể dễ dàng truy xuất những thông tin cần thiết. 

### ❖ **Data Warehouse** 

Data warehouse ban đầu được định nghĩa là một tập dữ liệu được dùng để hỗ trợ quy trình ra quyết định. Theo quá trình phát triển, DWH được định nghĩa là một môi trường thông tin (từ môi trường thông tin thể hiện nó không phải là một sản phẩm), có các chức năng: 

- Cung cấp một góc nhìn toàn diện về doanh nghiệp. 

- Cung cấp đầy đủ thông tin hiện tại và lịch sử của doanh nghiệp, và sẵn sàng cho việc khai thác, sử dụng cho việc hỗ trợ ra quyết định chiến lược. 

- Đảm báo thông tin có tính nhất quán. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

29 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

   - Là nguồn thông tin mềm dẻo và có tính tương tác, tức là người dùng có thể lấy các thông tin khác nhau của cùng 1 đối tượng, với nhiều thao tác thay vì trả lại một danh sách tĩnh. 

- Những đặc tính của Data Warehouse: 

   - Hướng chủ đề (Subject-oriented): thông tin trong Data warehouse sẽ được tổ chức và sắp xếp theo một chủ đề nhất định. 

   - Được tích hợp (Integrated): khả năng tổng hợp dữ liệu từ nhiều nguồn vào một kho dữ liệu. 

   - Có gán nhãn thời gian (Time variant): Việc gán thời gian sẽ giúp dễ dàng so sánh dữ liệu với nhau để biết được các thay đổi đang đi theo chiều hướng tích cực hay tiêu cực. 

   - Bất biến (non-volatile): Dữ liệu trong Data warehouse có chức năng báo cáo lại các chỉ số về hoạt động kinh doanh thực tế đã xảy ra do đó không thể cập nhật, thay đổi vì nó sẽ không phản ánh đúng thực tế. Với Data warehouse sẽ chỉ có 2 thao tác chính là tải dữ liệu vào kho và đọc dữ liệu từ kho. 

Database là nền tảng xây dựng Data Warehouse: Database là một phần quan trọng trong việc xây dựng Data Warehouse. Trong quá trình xây dựng Data Warehouse, các tập dữ liệu từ nhiều nguồn khác nhau sẽ được thu thập, tối ưu hóa, và lưu trữ trong các Database. Dữ liệu trong Database sẽ được xử lý và tích hợp lại với nhau để tạo ra các tập dữ liệu liên quan đến các chủ đề hoặc mục tiêu phân tích. 

_Bảng 2. 3: Bảng so sánh Database và Data Warehouse_ 

|**Tiêu chí**|**Database**|**Data Warehouse**|
|---|---|---|
|Mục đích sử|Quản lý và lưu trữ dữ liệu cho|Lưu trữ dữ liệu lớn, phân tích và|
|dụng|các ứng dụng phần mềm|báo cáo|
|Thiết kế cơ sở<br>dữ liệu|Kiến trúc đơn giản, dễ quản<br>lý với các bảng dữ liệu được|Kiến trúc phức tạp hơn với các<br>phân vùng dữ liệu và các kỹ<br>thuật phân tích dữ liệu phức tạp|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

30 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

||thiết kế để hỗ trợ các ứng<br>dụng cụ thể||
|---|---|---|
|Tính chất dữ<br>liệu|Dữ liệu giao dịch (dữ liệu<br>được thêm mới, cập nhật hoặc<br>xóa bỏ thường xuyên)|<br>Dữ liệu phân tích (dữ liệu đã<br>được xử lý, tổng hợp và tối ưu<br>phục vụ phân tích và báo cáo)|
|Tốc độ truy<br>vấn|Nhanh hơn|Chậm hơn|



### ❖ **Data lake** 

Data Lake (hay Hồ dữ liệu) là một kho lưu trữ tập trung được thiết kế để lưu trữ, xử lý và bảo mật một lượng lớn dữ liệu có cấu trúc, bán cấu trúc và phi cấu trúc. 

Nó có thể lưu trữ dữ liệu ở định dạng gốc và xử lý mọi loại dữ liệu khác nhau, bỏ qua các giới hạn về kích thước. Điều này cho phép người dùng sử dụng nhiều định dạng dữ liệu khác nhau, đồng thời làm tăng khả năng phân tích trên các nền tảng. Nó cung cấp số lượng dữ liệu cao để tăng hiệu suất phân tích và tích hợp gốc. 

Data Lake và Data Warehouse đều được sử dụng rộng rãi để lưu trữ dữ liệu lớn, nhưng chúng không phải là những thuật ngữ có thể thay thế cho nhau. Data Lake là một Data Warehouse thô rộng lớn, mục đích của nó vẫn chưa được xác định. Data Warehouse là một kho lưu trữ dữ liệu có cấu trúc, đã được lọc, đã được xử lý cho một mục đích cụ thể. 

_Bảng 2. 4: Bảng so sánh Data Lake và Data Warehouse_ 

|**Tiêu chí**|**Data Lake**|**Data Warehouse**|
|---|---|---|
|Loại dữ liệu|Dữ liệu có cấu trúc, bán cấu<br>trúc và phi cấu trúc|Dữ liệu có cấu trúc|
|Xử lý|Dữ liệu chủ yếu chưa được xử<br>lý|Dữ liệu được xử lý cao|
|Nhiệm vụ|Chia sẻ quyền quản lý dữ liệu|Tối ưu hóa để truy xuất dữ liệu|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

31 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|Độ phức tạp<br>khi thay đổi|Ít phức tạp hơn|Phức tạp|
|---|---|---|
|Mục đích của<br>dữ liệu|Có thể chưa rõ ràng|Đã biết|
|Bảo mật|Cung cấp khả năng kiểm soát<br>thấp hơn|Cho phép kiểm soát dữ liệu tốt<br>hơn|



### **2.2. Quy trình ETL dữ liệu** 

### **_2.2.1. Trích xuất dữ liệu_** 

Bước đầu tiên trong quy trình ETL (Extract – Transform – Load) chính là trích xuất dữ liệu. Đây là giai đoạn thu thập dữ liệu từ nhiều nguồn khác nhau nhằm phục vụ cho quá trình xử lý và phân tích sau này. 



<!-- Start of picture text -->
ETL Process<br><!-- End of picture text -->

_Hình 2. 11: Hình minh họa quy trình ETL dữ liệu_ 

Nguồn dữ liệu có thể đến từ: 

- Cơ sở dữ liệu quan hệ (SQL Server, MySQL, Oracle, …) – nơi lưu trữ các bảng dữ liệu giao dịch, tài chính, nhân sự, bán hàng. 

- Hệ thống ứng dụng nghiệp vụ (ERP, CRM, Core Banking, …) – chứa thông tin quản lý khách hàng, kế toán, giao dịch ngân hàng. 

- Tệp dữ liệu phi cấu trúc hoặc bán cấu trúc như CSV, Excel, JSON, XML. 

- Nguồn dữ liệu trực tuyến như API, trang web, hoặc dữ liệu từ đối tác. 

Mục tiêu chính của bước trích xuất là: 

- Thu thập đầy đủ dữ liệu cần thiết để phục vụ cho báo cáo và phân tích, không bỏ sót các trường thông tin quan trọng. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

32 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Đảm bảo tính toàn vẹn dữ liệu, không bị mất mát hoặc sai lệch trong quá trình trích xuất. 

- Tối ưu hiệu suất trích xuất, tránh gây ảnh hưởng đến hệ thống nguồn (ví dụ: không làm chậm hệ thống giao dịch khi thực hiện ETL). 

Có hai hình thức trích xuất phổ biến: 

   - Trích xuất toàn bộ (Full Extract): Sao chép toàn bộ dữ liệu từ nguồn vào hệ thống đích. Thường dùng trong lần tải dữ liệu đầu tiên hoặc khi quy mô dữ liệu nhỏ. 

   - Trích xuất theo thay đổi (Incremental Extract): Chỉ lấy những dữ liệu mới hoặc đã thay đổi so với lần trích xuất trước. Phương pháp này tiết kiệm tài nguyên và phù hợp với hệ thống lớn, dữ liệu thay đổi liên tục. 

- Trích xuất dữ liệu là bước nền tảng, ảnh hưởng trực tiếp đến chất lượng dữ liệu trong Data Warehouse. Nếu quá trình này không được thiết kế cẩn thận, dữ liệu bị thiếu, sai hoặc trùng lặp sẽ dẫn đến sai lệch trong phân tích và báo cáo. 

### **_2.2.2. Chuyển đổi dữ liệu_** 

Sau khi dữ liệu đã được trích xuất, bước tiếp theo trong quy trình ETL là Chuyển đổi dữ liệu. Đây là giai đoạn quan trọng nhằm đảm bảo dữ liệu đưa vào Data Warehouse có chất lượng cao, nhất quán và phù hợp với cấu trúc đã thiết kế. Các hoạt động chính trong giai đoạn chuyển đổi bao gồm: 

- Làm sạch dữ liệu (Data Cleansing): 

- Loại bỏ dữ liệu trùng lặp, sai lệch hoặc không hợp lệ. 

- Xử lý các giá trị thiếu (missing values) bằng cách loại bỏ, thay thế hoặc ước lượng. 

- Chuẩn hóa định dạng dữ liệu (ví dụ: ngày tháng theo cùng định dạng YYYY-MM-DD). 

Chuẩn hóa dữ liệu (Standardization): 

- Chuyển đổi đơn vị đo lường để đồng nhất (VD: USD → VND, hoặc mét → cm). 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

33 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Đồng nhất mã định danh (VD: mã khách hàng KH001 và 001KH phải được quy đổi về cùng chuẩn). 

- Chuẩn hóa tên trường, loại dữ liệu, để phù hợp với mô hình dữ liệu mục tiêu. 

Tích hợp dữ liệu (Integration): 

- Hợp nhất dữ liệu từ nhiều nguồn khác nhau (cơ sở dữ liệu giao dịch, hệ thống CRM, file Excel, API bên ngoài, …). 

- Giải quyết vấn đề khác biệt về cấu trúc giữa các nguồn dữ liệu (VD: một hệ thống lưu ngày dưới dạng date, hệ thống khác lưu dưới dạng string). 

- Chuyển đổi định dạng dữ liệu (Data Transformation): 

- Chuyển đổi kiểu dữ liệu (VD: string sang integer, hoặc varchar sang date). 

- Tính toán thêm các chỉ số mới (VD: từ dữ liệu giao dịch, tính toán thêm Doanh thu thuần, Biên lợi nhuận gộp, ROE, …). 

- Áp dụng các quy tắc kinh doanh (business rules) để chuẩn hóa dữ liệu theo nhu cầu phân tích. 

Ánh xạ dữ liệu (Data Mapping): 

- Xác định mối quan hệ giữa dữ liệu nguồn và dữ liệu đích (fact tables và dimension tables trong Data Warehouse). 

- Đảm bảo dữ liệu được đưa vào đúng bảng, đúng cột theo thiết kế của mô hình Star Schema, Snowflake Schema, hay Galaxy Schema. 

### **_2.2.3. Tải dữ liệu_** 

Bước cuối cùng của quy trình ETL là Tải dữ liệu. Sau khi dữ liệu đã được chuẩn bị và chuyển đổi, nó sẽ được tải vào kho dữ liệu hoặc cơ sở dữ liệu mục tiêu. Việc tải có thể được thực hiện theo lịch trình hoặc theo yêu cầu, tùy thuộc vào nhu cầu của tổ chức. 

### **_2.2.4. So sánh ETL và ELT_** 

ETL là tên viết tắt của Extract, Transform và Load. Trong quá trình này, một công cụ ETL trích xuất dữ liệu từ các hệ thống nguồn RDBMS khác nhau sau 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

34 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

đó chuyển đổi dữ liệu như áp dụng các biến đổi dữ liệu và sau đó tải dữ liệu vào hệ thống Data Warehouse. ETL là những luồng từ nguồn tới đích. Trong quá trình ETL, engine chuyển đổi sẽ xử lý mọi thay đổi dữ liệu. 



<!-- Start of picture text -->
A<br>A} |B<br>B<br>Source c » TransformationEngine c Ip<br>D E|(F Target<br>E<br>F<br><!-- End of picture text -->

_Hình 2. 12: Hình mô tả mục đích ETL_ 

ELT là một phương pháp khác để tiếp cận công cụ chuyển động dữ liệu. Thay vì chuyển đổi dữ liệu trước khi viết, ELT cho phép hệ thống đích chuyển đổi trước. Dữ liệu đầu tiên được sao chép vào đích và sau đó được chuyển đổi tại đó. ELT thường được sử dụng với các database No-SQL như Hadoop, Data Appliance hoặc Cloud Installation. 



<!-- Start of picture text -->
A —’‘<br>A B<br>B<br>Source c __, ¢| (p> TraansformTarget<br>D Target E iz<br>E _/<br>E<br><!-- End of picture text -->

_Hình 2. 13: Hình mô tả mục đích ELT_ 

Sự khác nhau giữa ETL và ELT: 

_Bảng 2. 5: So sánh ETL và ELT_ 

||**ETL**|**ELT**|
|---|---|---|
|1.Quy trình|Dữ liệu được chuyển đổi từ<br>server staging sau đó được<br>transfer tới Data warehouse DB|<br> <br>Dữ liệu vẫn còn trong DB của<br>Data warehouse|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

35 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|2.Code Usage<br>|Được sử dụng cho:-Những biến<br>đổi chuyên sâu về tính toán-<br>Lượng data nhỏ<br>|<br>Được sử dụng cho lượng data<br>rất lớn<br> <br>|
|---|---|---|
|3.Biến đổi dữ<br>liệu|Các biến đổi được thực hiện<br>trong ETL server/staging|<br>Các biến đổi được thực hiện bên<br>trong “hệ thống đích”|
|4.Thời gian<br>load|Dữ liệu trước tiên được load<br>vào staging sau đó mới load vào<br>“đích”. Cần nhiều thời gian|<br> <br>Dữ liệu được load vào “đích”<br>chỉ 1 lần sau đó mới biến đổi.<br>Nhanh hơn|
|5.Thời gian<br>biến đổi|Quá trình ETL bắt buộc cần quá<br>trình “Tranform” hoàn tất. Khi<br>kích thước dữ liệu tăng lên, thời<br>gian chuyển đổi cũng tăng theo.|<br> <br> <br> <br>. Trong quá trình ELT, tốc độ<br>không bao giờ phụ thuộc vào<br>kích thước của dữ liệu.|
|6.Thời gian<br>bảo trì|Nhu cầu bảo trì là rất cao vì cần<br>phải chọn dữ liệu để load và<br>transform|<br> <br>Nhu cầu bảo trì là rất thấp vì dữ<br>liệu luôn có sẵn|
|7.Độ phức tạp<br>khi bắt đầu|Ở giai đoạn đầu thực hiện rất dễ<br>dàng|<br>Để thực hiện quá trình ELT, cần<br>phải có những kiến thức rất sâu<br>về các tools và kĩ năng chuyên<br>môn|
|8.Hỗ trợ Data<br>warehouse|Mô hình ETL được sử dụng cho<br>dữ liệu on-premise, quan hệ và<br>có cấu trúc|<br> <br>Được sử dụng cho cơ sở hạ tầng<br>cloud có thể support các nguồn<br>dữ liệu có cấu trúc và phi cấu<br>trúc|
|9.Hỗ trợ Data<br>Lake|Không support|Cho phép sử dụng Data Lake<br>với dữ liệu phi cấu trúc|
|10.Độ phức tạp|Quá trình ETL chỉ load những<br>dữ liệu quan trọng, như đã được<br>xác định trước từ thời điểm<br>design|<br> <br> <br>Quá trình này bao gồm tất cả<br>quá trình phát triển từ output-<br>backward và load những dữ liệu<br>liên quan|
|11.Chi phí|Chi phí rất cao cho các doanh<br>nghiệp vừa và nhỏ|<br>Chi phí đầu vào thấp khi sử<br>dụng các phần mềm online làm<br>Services Platforms|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

36 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **2.3. Khái quát về dữ liệu tài chính** 

Dữ liệu là ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự khác, được thu thập, lưu trữ và xử lý để sử dụng trong nhiều lĩnh vực khác nhau. Dữ liệu là nền tảng sử dụng cho các giải pháp thông tin, trí tuệ doanh nghiệp và quyết định dựa trên phân tích dữ liệu. Nền tảng dữ liệu bao gồm việc tích hợp dữ liệu từ nhiều nguồn khác nhau thành một dạng đáng tin cậy, dễ hiểu để sử dụng trong phân tích và biến dữ liệu thành tài sản của doanh nghiệp. 

Tài chính là hệ thống các quan hệ kinh tế phát sinh trong quá trình phân phối các nguồn lực tài chính thông qua việc tạo lập và sử dụng các quỹ tiền tệ nhằm thực hiện các mục tiêu kinh tế - xã hội nhất định của các chủ thể. Nguồn lực tài chính luân chuyển theo nhiều kênh, chúng hình thành, vận động xoay quanh thị trường tài chính. Trên thị trường tài chính các nguồn cung và cầu về vốn sẽ gặp nhau một cách trực tiếp hoặc gián tiếp thông qua các trung gian tài chính, có vai trò điều hòa các nguồn vốn từ nơi thừa đến nơi thiếu và cho phép huy động tối đa mọi nguồn tài chính hiện có để tạo lập quỹ tiền tệ. 

Như vậy, dữ liệu tài chính là tất cả các thông tin được thu thập về tài chính, về hệ thống các quan hệ kinh tế phát sinh trong quá trình phân phối các nguồn lực tài chính. Dữ liệu tài chính có thể bao gồm thông tin của doanh nghiệp hoặc ngành về doanh thu, lợi nhuận, tài sản, nợ phải trả và các chỉ số tài chính khác, dữ liệu về giao dịch cổ phiếu, trái phiếu, tiền tệ, hàng hóa, các số liệu kinh tế vĩ mô… Đây là những thông tin quan trọng, được sử dụng nhằm thực hiện các mục tiêu kinh tế - xã hội nhất định như ổn định kinh tế vĩ mô, phân bổ các nguồn lực đầu tư trong nền kinh tế, hay để đánh giá và phân tích hiệu suất kinh doanh, đưa ra quyết định đầu tư và lập kế hoạch cho tương lai... 

* Các loại dữ liệu tài chính thường gặp: 

Hệ thống tài chính bao gồm tài chính công, tài chính doanh nghiệp và tài chính tổ chức xã hội/hộ gia đình/cá nhân. Trong đó: 

Tài chính công: Ngân sách nhà nước là khâu tài chính quan trọng trong hệ thống tài chính, là cơ sở để thực hiện điều tiết vĩ mô nền kinh tế. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

37 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Tài chính doanh nghiệp: Bao gồm các hoạt động tài chính của các doanh nghiệp sản xuất/thương mại/dịch vụ và doanh nghiệp tài chính (ngân hàng, công ty tài chính, quỹ tín dụng, bảo hiểm, công ty chứng khoán…). Hoạt động tài chính của các doanh nghiệp được thực hiện thông qua việc tạo lập nguồn vốn, có thể thông qua thị trường tài chính (phát hành cổ phiếu, trái phiếu, vay vốn qua trung gian tài chính…). 

Tài chính hộ gia đình/cá nhân: Bao gồm các hoạt động tài chính liên quan đến thu nhập (lương, sản xuất kinh doanh, tiết kiệm, đầu tư…) và chi tiêu/tiêu dùng. Tài chính tổ chức xã hội gồm tài chính của các tổ chức xã hội thông qua việc hình thành các quỹ tiền tệ được sử dụng cho mục đích tiêu dùng, duy trì hoạt động của tổ chức hoặc tham gia thị trường tài chính. 

* Liên quan đến hệ thống tài chính, các loại dữ liệu tài chính thường gặp bao gồm: 

- Dữ liệu về vĩ mô, tình hình nền kinh tế xã hội: GDP, CPI, FDI, PMI, Cung tiền M2, Tỷ giá, Lãi suất, Dân số, Xuất – Nhập khẩu,… 

- Dữ liệu về tài chính doanh nghiệp: là nguồn thông tin quan trọng phản ánh toàn diện tình hình hoạt động và sức khỏe tài chính của doanh nghiệp. Thành phần dữ liệu này bao gồm báo cáo tài chính như bảng cân đối kế toán, báo cáo kết quả kinh doanh và báo cáo lưu chuyển tiền tệ, cung cấp cái nhìn chi tiết về tài sản, nguồn vốn, doanh thu, chi phí và dòng tiền. Bên cạnh đó, các chỉ số tài chính như ROE, ROA, tỷ lệ nợ vay hay hệ số thanh toán được tính toán từ số liệu gốc, giúp đánh giá khả năng sinh lời, mức độ an toàn tài chính và hiệu quả sử dụng vốn. Nhờ việc kết hợp giữa báo cáo và các chỉ số, dữ liệu tài chính doanh nghiệp không chỉ phục vụ cho phân tích hiện tại mà còn hỗ trợ dự báo, hoạch định chiến lược và ra quyết định quản trị. 

- Dữ liệu về ngành: Bao gồm các dữ liệu tài chính và giao dịch của các cổ phiếu đã được phân loại theo ngành nghề hoạt động kinh doanh 

- Dữ liệu về thị trường giao dịch cổ phiếu: Gồm thông tin về biến động giá, khối lượng giao dịch của các cổ phiếu trên sàn, các thống kê về giao dịch của các bên liên quan trên thị trường như: Nhà đầu tư nước ngoài, Tự doanh 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

38 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Dữ liệu về thị trường giao dịch trái phiếu: Bao gồm dữ liệu về các trái phiếu niêm yết, trái phiếu riêng lẻ, trái phiếu sắp giao dịch, mua lại, hoán đổi trái phiếu, thực hiện chứng quyền, trái phiếu hủy đăng ký / hết hiệu lực. 

### **2.4. Các công cụ, công nghệ sử dụng** 

### **_2.4.1. SQL Server Integration Services (SSIS)_** 

SSIS là viết tắt của SQL Server Integration Services – một công cụ tích hợp và quản lý dữ liệu đi kèm với cơ sở dữ liệu Microsoft SQL Server. 

SSIS giúp lưu trữ dữ liệu linh hoạt và nhanh chóng hơn với các tính năng như 1 công cụ ETL (trích xuất lượng lớn dữ liệu từ nhiều nguồn dữ liệu trong các định dạng khác nhau, chỉnh sửa và làm sạch dữ liệu sau đó tải chúng vào kho dữ liệu đã được thiết kế). 

Các công ty hiện nay sử dụng SSIS với mục đích lưu trữ dữ liệu, trích xuất và tải dữ liệu, quản lý dữ liệu, làm sạch, hợp nhất dữ liệu, v.v. 

Trước khi có SSIS, việc di chuyển dữ liệu giữa các nơi lưu trữ thường rất khó bởi vì cấu trúc của các dữ liệu khác nhau và chúng cần phải được thay đổi trước khi di chuyển đến nơi lưu trữ mới. 

Tuy nhiên với SSIS, nó có thể trích xuất dữ liệu từ nhiều nguồn khác nhau như cơ sở dữ liệu SQL Server, tệp Excel, cơ sở dữ liệu Oracle và DB2,… để đưa đến đích một cách dễ dàng. 

Ngoài ra, SSIS cũng bao gồm các công cụ đồ họa và trình hướng dẫn để thực hiện các chức năng của quy trình công việc như gửi thư email, hoạt động truyền tải tập tin, trích xuất nguồn dữ liệu và truyền tải dữ liệu đến đích. 

Một trong những tính năng vượt trội nhất của SSIS là khả năng trích xuất và đồng bộ dữ liệu nhanh chóng và linh hoạt. SSIS cung cấp một nền tảng thuận tiện để di chuyển dữ liệu một cách dễ dàng từ nguồn này sang nguồn khác. 

SSIS bạn trích xuất dữ liệu từ nhiều nguồn khác nhau như cơ sở dữ liệu SQL, cơ sở dữ liệu Qracle, cơ sở dữ liệu DB2 và các tệp Micrisoft Excel lên kho 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

39 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

dữ liệu sau đó sắp xếp và đồng bộ chúng. Nó có thể tải hàng triệu tệp dữ liệu từ nguồn này sang nguồn khác chỉ trong vài phút 

Ngoài ra một trong những lý do tại sao SSIS được sử dụng rộng rãi là do tính linh hoạt của nó. SSIS hỗ trợ nhiều loại cơ sở dữ liệu và đồ họa giao diện người dùng (GUI) đơn giản giúp người dùng mới hoàn thành các tác vụ chuyển đổi và lưu trữ dữ liệu vô cùng dễ dàng. Người thể tự thiết kế một quy trình ETL (Trích xuất – biến đổi – tải) như ý muốn. 

* Lợi ích: 

SSIS mang một tính linh hoạt cao giống như một công cụ ETL hay một công cụ chuyển đổi dữ liệu. Người dùng có thể nhập dữ liệu từ các nguồn dữ liệu không đồng nhất và sau đó biến đổi dữ liệu theo cách họ thấy phù hợp. Các tùy chọn cấu hình như luồng điều khiển và luồng dữ liệu cho phép người dùng kiểm soát toàn bộ quy trình đó. 

Việc kết nối giao diện người dùng với cấu hình SSIS vô cùng đơn giản. Mọi thứ bạn cần đều dễ dàng tìm thấy và bạn có thể nhấp vào các tab luồng điều khiển và luồng dữ liệu mà không cần tìm kiếm lâu. Nếu bạn không hiểu rõ về cấu trúc, bạn có thể kiểm tra thông qua Package Explorer. 

SSIS cung cấp một số tính năng cho phép bạn tạo tài liệu mới khi bạn chuyển đổi dữ liệu ban đầu. Bạn có thể thêm các gói có chú thích, luồng điều khiển và luồng dữ liệu. Trình viết mô tả cho các thành phần trong 1 cấu hình SSIS cho phép bạn ghi lại những thao tác mà bạn thực hiện. 

* Hạn chế: 

Một trong những hạn chế lớn nhất của SSIS là nó chỉ hỗ trợ Microsoft Windows. Ngay cả khi đã tích hợp thêm nhiều mã nguồn thì việc không hỗ trợ các hệ điều hành khác cũng gây nên sự hạn chế khi muốn trích xuất và tích hợp dữ liệu từ nhiều nguồn khác nhau không phải của Windows. 

Tuy nhiên nếu bạn chủ yếu làm việc trên nền tảng Microsoft Windows thì nhược điểm này sẽ ít đáng kể hơn. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

40 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **_2.4.2. SQL Server_** 

SQL Server hay Microsoft SQL Server là một hệ thống quản trị cơ sở dữ liệu quan hệ (Relational Database Management System – RDBMS) được phát triển bởi Microsoft vào năm 1988. Nó được sử dụng để tạo, duy trì, quản lý và triển khai hệ thống RDBMS. 

Được thiết kế để quản lý và lưu trữ dữ liệu, SQL Server cho phép người dùng truy vấn, thao tác và quản lý dữ liệu một cách hiệu quả và an toàn. SQL Server là một trong những hệ quản trị cơ sở dữ liệu phổ biến nhất trên thế giới và được sử dụng rộng rãi trong các doanh nghiệp. 

Phần mềm SQL Server được sử dụng khá rộng rãi vì nó được tối ưu để có thể chạy trên môi trường cơ sở dữ liệu rất lớn lên đến Tera – Byte cùng lúc phục vụ cho hàng ngàn user. Bên cạnh đó, ứng dụng này cung cấp đa dạng kiểu lập trình SQL từ ANSI SQL (SQL truyền thống) đến SQL và cả T-SQL (Transaction-SQL) được sử dụng cho cơ sở dữ liệu quan hệ nâng cao. 

T-SQL là một ngôn ngữ mở rộng của SQL với các tính năng bổ sung như biến, điều kiện, vòng lặp và xử lý ngoại lệ, giúp người dùng viết các đoạn mã SQL mạnh mẽ và linh hoạt hơn. 

SQL Server được sử dụng để tạo và duy trì các cơ sở dữ liệu quan hệ, cung cấp nền tảng vững chắc cho việc lưu trữ và quản lý dữ liệu. Các chức năng chính bao gồm: 

- Quản lý dữ liệu: SQL Server cho phép người dùng tạo, sửa đổi và xóa các bảng dữ liệu, chỉ mục, và các mối quan hệ giữa các bảng. Hệ thống quản lý dữ liệu của SQL Server hỗ trợ các thao tác CRUD,giúp quản lý dữ liệu một cách hiệu quả. 

- Bảo mật dữ liệu: SQL Server cung cấp các tính năng bảo mật mạnh mẽ như mã hóa dữ liệu, kiểm soát truy cập dựa trên vai trò và xác thực người dùng. Các biện pháp bảo mật này đảm bảo rằng dữ liệu được bảo vệ khỏi các mối đe dọa và truy cập trái phép. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

41 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Quản lý giao dịch: SQL Server hỗ trợ các tính năng quản lý giao dịch như Atomicity, Consistency, Isolation và Durability (ACID), đảm bảo rằng các thay đổi trong cơ sở dữ liệu được thực hiện một cách nhất quán và an toàn. Điều này rất quan trọng đối với các ứng dụng yêu cầu độ tin cậy cao như tài chính, ngân hàng và thương mại điện tử. 

- Sao lưu và phục hồi: SQL Server cung cấp các tính năng sao lưu và phục hồi dữ liệu, cho phép người dùng tạo các bản sao lưu toàn bộ, gia tăng và khác biệt. Các tính năng này giúp bảo vệ dữ liệu khỏi mất mát do lỗi phần cứng, phần mềm hoặc lỗi con người và đảm bảo rằng dữ liệu có thể được phục hồi nhanh chóng trong trường hợp xảy ra sự cố. 

### **_2.4.2. Ngôn ngữ truy vấn SQL_** 

SQL được viết tắt từ Structured Query Language, là ngôn ngữ truy vấn có cấu trúc. Về cơ bản, Ngôn ngữ truy vấn có cấu trúc này được sử dụng để truy xuất dữ liệu hoặc giao diện khác như tạo, xóa trong cơ sở dữ liệu, lấy các hàng và sửa đổi các hàng .v.v. với cơ sở dữ liệu quan hệ. 

SQL cho phép bạn truy cập và thao tác cơ sở dữ liệu. Nó là ngôn ngữ được dành riêng cho sử dụng trong lập trình và được thiết kế quản lý dữ liệu được giữ trong hệ thống quản lý cơ sở dữ liệu quan hệ hoặc để xử lý luồng trong hệ thống quản lý luồng dữ liệu quan hệ. SQL được sử dụng để giao tiếp với cơ sở dữ liệu. Theo ANSI (American National Standards Institute_Viện Tiêu chuẩn Quốc gia Hoa Kỳ), SQL là ngôn ngữ tiêu chuẩn cho các hệ thống quản lý cơ sở dữ liệu quan hệ. 

Các chức năng của SQL: 

- Với SQL, người dùng có thể thực thi các truy vấn đối với cơ sở dữ liệu 

- Lấy dữ liệu từ cơ sở dữ liệu 

- Chèn các records (bản ghi) trong cơ sở dữ liệu 

- Cập nhật các records trong cơ sở dữ liệu 

- Xóa các bản ghi từ cơ sở dữ liệu 

- Tạo cơ sở dữ liệu mới 

- Tạo các thủ tục được lưu trữ trong cơ sở dữ liệu 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

42 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Tạo các view, stored procedure, functions trong cơ sở dữ liệu 

- SQL còn cho phép thiết lập quyền truy cập trên bảng, procedure và view 

Cách SQL Database hoạt động bao gồm việc thực thi các lệnh truy vấn đến máy chủ, sau đó máy chủ xử lý các truy vấn này và trả về kết quả. 

### **_2.4.3. Ngôn ngữ lập trình Python_** 

Python là một ngôn ngữ lập trình thông dịch, dễ đọc và dễ hiểu. Nền tảng nổi tiếng với cú pháp đơn giản và được sử dụng rộng rãi trong nhiều lĩnh vực khác nhau. Điển hình như phát triển web, phân tích dữ liệu, trí tuệ nhân tạo và nhiều ứng dụng khác. Python có cú pháp linh hoạt và cấu trúc dữ liệu mạnh mẽ, công nghệ được hỗ trợ bởi một cộng đồng lớn. Điều này đã mang đến các thư viện và framework phong phú mà người dùng có thể sử dụng để xây dựng các ứng dụng phức tạp. Python cũng là một trong những ngôn ngữ phổ biến cho người mới học lập trình nhờ vào tính linh hoạt của nó. 

* Một số lợi ích của ngôn ngữ như sau: 

- Cú pháp đơn giản và dễ đọc, phù hợp cho người mới học lập trình và cũng dễ dàng cho những người có kinh nghiệm. 

- Python được sử dụng trong nhiều lĩnh vực như phát triển web, phân tích dữ liệu, trí tuệ nhân tạo, khoa học dữ liệu và nhiều ứng dụng khác. Điều này làm cho Python trở thành một ngôn ngữ lập trình linh hoạt và tiện lợi. 

- Cộng đồng Python khá lớn và luôn hoạt động tích cực nhằm cung cấp nhiều thư viện, framework hữu ích. Người dùng sẽ được nhận sự hỗ trợ từ cộng đồng thông qua tài liệu, diễn đàn và các nguồn thông tin trực tuyến. 

- Python cung cấp nhiều thư viện mạnh mẽ cho phân tích dữ liệu như Pandas, NumPy, và Matplotlib. Bộ ngôn ngữ giúp người dùng xử lý và thể hiện dữ liệu một cách hiệu quả. 

- Python có thể chạy trên nhiều hệ điều hành khác nhau và trở thành một trong những ngôn ngữ lập trình chéo phổ biến. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

43 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Ngôn ngữ Python là mã nguồn mở và miễn phí, cho phép người dùng tự do sử dụng, phân phối và thay đổi phiên bản của nó. 

* Một số ứng dụng của Python: 

- Phát triển trang web trên máy chủ. 

- Tập lệnh Python tự động hóa. 

- Ứng dụng trong khoa học dữ liệu. 

- Python phát triển phần mềm. 

### **_2.4.4. Power BI_** 

Power BI là một thành phần trong Power Platform của Microsoft. Ngoài Power BI, Microsoft Power Platform còn bao gồm Power Apps, Power Pages, Power Automate và Power Virtual Agents, là bộ các công cụ hỗ trợ cho phân tích dữ liệu, xây dựng giải pháp và tự động hóa quy trình, giúp các doanh nghiệp thúc đẩy kinh doanh. 

Power BI đóng vai trò là một công cụ Kinh doanh thông minh đem đến khả năng xử lý, tổ chức, phân tích và trực quan hóa dữ liệu, mang dữ liệu từ dạng thô trở thành các thông tin hữu ích hỗ trợ cho việc ra quyết định của các công ty, tổ chức, doanh nghiệp. Thể hiện của Power BI là các biểu đồ, bảng điều khiển không chỉ đẹp mà còn chứa đựng nhiều thông tin có giá trị giúp diễn giải, kiểm soát tình hình kinh doanh và dự báo cho tương lai. 

* Tính năng: 

- Kết nối dữ liệu đa dạng: từ file (Excel, CSV, PDF), cơ sở dữ liệu (SQL Server, MySQL…), nguồn web, SharePoint đến các hệ thống ERP/SAP. 

- Làm sạch & biến đổi dữ liệu bằng Power Query trước khi phân tích. 

- Xây dựng mô hình dữ liệu với các bảng liên kết, giúp quản lý dữ liệu gọn và truy xuất hiệu quả. 

- Trực quan hóa linh hoạt bằng biểu đồ, dashboard tương tác hỗ trợ phân tích từ tổng quan đến chi tiết. 

- Hỗ trợ ngôn ngữ DAX để tính toán và phân tích dữ liệu mạnh mẽ. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

44 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Ứng dụng: 

   - Tận dụng dữ liệu doanh nghiệp: Power BI giúp khai thác dữ liệu phát sinh từ hoạt động sản xuất – kinh doanh, hỗ trợ theo dõi, kiểm soát và phân tích tình hình. Nhờ đó, lãnh đạo và các bộ phận có thể đưa ra quyết định chính xác dựa trên dữ liệu đã được phân tích. 

   - Xem báo cáo mọi lúc – mọi nơi: Cung cấp bảng biểu, biểu đồ và dashboard trên web và ứng dụng di động, giúp người dùng truy cập báo cáo linh hoạt. Power BI còn hỗ trợ real-time data, cho phép theo dõi số liệu tức thời và phản ứng nhanh trong kinh doanh. 

   - Bảo mật mạnh mẽ: Cho phép phân quyền đến từng người hoặc từng bộ phận, đảm bảo mỗi nhóm chỉ xem được dữ liệu liên quan. Điều này giúp duy trì tính minh bạch, tránh xung đột lợi ích và bảo vệ dữ liệu doanh nghiệp. 

   - Tự động làm mới dữ liệu: Hỗ trợ schedule refresh và dataflow, giúp báo cáo và dữ liệu luôn được cập nhật theo lịch thiết lập. Điều này giảm thời gian xử lý thủ công và tối ưu chi phí vận hành. 

- So sánh Power Bi Desktop và Power Bi Service 

### Power BI Desktop 

   - Ứng dụng miễn phí cài trên máy tính. 

   - Dùng để kết nối, xử lý, mô hình dữ liệu và tạo báo cáo hoàn chỉnh. 

   - Có Query Editor và hỗ trợ xây dựng data model mạnh mẽ. 

   - Báo cáo được tạo tại Desktop thường được publish lên Power BI Service. 

- Power BI Service 

   - Dịch vụ chạy trên nền tảng đám mây. 

   - Dùng để xem, chia sẻ, cộng tác và tạo dashboard. 

   - Có thể kết nối dữ liệu nhưng khả năng mô hình hóa hạn chế hơn Desktop. 

   - Lưu trữ báo cáo phân trang và cho phép chia sẻ dataset để người khác tạo báo cáo. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

45 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **_2.4.5. Microsoft Power Platform_** 

Microsoft Power Platform là một tập hợp các giải pháp do Microsoft cung cấp và phát triển nhằm tối ưu hóa việc phân tích dữ liệu, tự động hóa quy trình kinh doanh. Đây là một nền tảng low code hoặc không cần mã nên người dùng có thể sử dụng dễ dàng, không cần có nhiều kiến thức về công nghệ thông tin. 

Microsoft Power Platform có khả năng kết nối thông qua trình liên kết dữ liệu với một số ứng dụng khác của Microsoft như Office 365, Dynamics 365, Azure… Điều này giúp cho quá trình quản lý và làm việc với dữ liệu của các doanh nghiệp trở nên dễ dàng hơn. 

Microsoft Power Platform bao gồm 4 công cụ chính là Power BI, Power Apps, Power Automate và Power Virtual Agents. Dưới đây là một số đặc điểm của 4 sản phẩm này: 

* Power BI: 

Power BI là một công cụ dùng để phân tích dữ liệu từ nhiều nguồn khác nhau. Power BI bao gồm 2 ứng dụng cơ bản là Power BI Desktop và Power BI Service được lưu trữ trên điện toán đám mây. 

Tổ chức có thể thực hiện các thao tác sửa đổi, định hình và chuyển đổi dữ liệu trong Power BI một cách đơn giản. Thông thường, những dữ liệu sẽ được trình bày qua dạng đồ thị hoặc biểu đồ để người dùng dễ dàng phân tích và đưa ra các báo cáo khi cần thiết. 

* Power Apps: 

Power Apps cung cấp các tính năng kéo và thả hỗ trợ cho quá trình xây dựng giao diện người dùng trên ứng dụng di động. Thông qua công cụ này, người dùng có thể thêm vào giao diện các hộp văn bản, trường lựa chọn… một cách nhanh chóng. 

Các ứng dụng được xây dựng bởi Power Apps có thể chạy trên bất kỳ trình duyệt web nào từ Chrome, Firefox, Cốc cốc… Không chỉ vậy, những ứng dụng đó có thể hoạt động được cả trên các hệ điều hành như  Android, iOS hoặc Windows. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

46 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

* Power Automate: 

Power Automate là một thành phần quan trọng của Microsoft Power Platform. Công cụ này có chức năng chính là tự động hóa quy trình làm việc trong tổ chức mà không cần viết bất kỳ mã nào. Nhờ đó mà mọi công việc trong doanh nghiệp sẽ được giải quyết nhanh chóng thay vì phải xử lý thủ công như trước đây. 

Power Automate cung cấp cho người dùng nhiều mẫu quy trình công việc khác nhau. Doanh nghiệp có thể lựa chọn các mẫu có sẵn hoặc tự thiết kế một quy trình cho riêng mình. Nhưng nhìn chung, tất cả quy trình công việc trên Power Automate sẽ được chia thành 3 loại chính như sau: 

Quy trình công việc tự động: Một số công việc tự động được kích hoạt ngay sau khi công việc trước đó đã hoàn thành. 

Quy trình công việc đã lên lịch: Các công việc cần làm sẽ được lên lịch theo ngày, tuần hoặc tháng. 

Quy trình công việc theo các nút: Quy trình này sẽ được kích hoạt khi người dùng nhấp vào nút đã được cài đặt trước đó. 

* Power Virtual Agents: 

Power Virtual Agents là một dịch vụ xây dựng bot dành cho doanh nghiệp. Qua công cụ này, người dùng có thể tạo nên một trợ lý trò chuyện ảo mà không cần phải viết một dòng mã code. 

Power Virtual Agents có khả năng tạo ra một vòng đời trọn vẹn cho một con chatbot bao gồm từ tạo hộp thoại, tác nhân ảo, một kênh như Slack, Skype, Teams… Bên cạnh đó, công cụ này còn được tích hợp với Power Automate để nâng cao chất lượng của sản phẩm được tạo ra. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

47 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **CHƯƠNG 3. THIẾT KẾ VÀ XÂY DỰNG MÔ HÌNH DATA WAREHOUSE** 

### **3.1. Khảo sát yêu cầu và dữ liệu** 

Công ty Cổ phần Chứng khoán Thiên Việt là một trong những công ty chứng khoán uy tín tại Việt Nam, hoạt động trong các lĩnh vực môi giới, tư vấn đầu tư, quản lý quỹ và nghiên cứu đánh giá tín nhiệm doanh nghiệp.Trong quá trình hoạt động, công ty thường xuyên cần phân tích tình hình tài chính của các doanh nghiệp nhằm phục vụ cho công tác đánh giá tín nhiệm, ra quyết định đầu tư và hỗ trợ tư vấn khách hàng. 

Hiện nay, các dữ liệu tài chính doanh nghiệp công ty thu thập được được lưu trữ phân tán ở nhiều định dạng khác nhau như file Excel, báo cáo PDF và cơ sở dữ liệu nội bộ. 



<!-- Start of picture text -->
BANG CAN DOI KE TOAN<br>SEPARATE BALANCE SHEET<br>Tai ngay‘As at 3131 thangDecember 201312 nam 2013 on vj tinh: VNB<br>Currency: VND.<br>a sé |TAISAN Thuyét Ngay 31/12/2013 Ngay 31/12/2012<br>Code |AsseTs mint 31-Dec-2013 31-Dec-2012<br>100 |A TAISANNGAN HAN 4.214.204.104.024| 4.595.208.741.775<br>110 | TiénCURRENTva céc ASSETS khodn trong durong tién 4 1.511.653.564.168] 1.712.297.012.483<br>a fi. CashCashTin  andon hand cash equivalents 1.222.653, 564.168 696.567.012.489<br>112 2, Gaekhodn tong dong tan 289.000.000.009 1.015.730.000.009<br>Cash equivalents<br>120 |W. Cac khodn dau tu tai chinh ngan han 1.208.811.808.953) 1.776.063.689.378|<br>‘Short-term financial investments<br>ya1 |i, Bautu ngdn han 61 1.251.185.673.088} 1.822.166 942.418]<br>129 |2. ‘ShortDy phéng trm investmentsgidm gid dau tu ngan han 63 (42.373.864.135)| (46.103.253.040)]<br>Provision for short-term investments<br>130 |. Céc khoan phai thu ngén han 1.489.920.517.726 1.100.593.798.651|<br>nar ft. ‘Short-termPhaiReceivables thu cbareceivables omkhachcustomersnang 7 913.645.353.416 499.708.484.016<br>132 fa, Tra tude cho nguts ban 7 €.066 208.100 3€8.358.019<br>‘Advances to supplers<br>135. [3. Phai thu noat dong giao dich ching knoan 7 185.010262| sa.smi.oz<br>Receivables om secures wading acties<br>138 |4, Cac Khodn phi th kha 7 659.153.321.374 811.353.953.245<br>Other recohvables<br>139 |s. Dy phéng phai thu ng han 8 (01.129.375.426) (214.435.507.621)<br>Provision or doubt recewvabes<br>150 |IV. Tai sn ngan han khéc 9 3.848.293.177| 6.339.241.263|<br>151 [1 — ChiphitrdOther currentrede ngénassets han 2.238.609.717] 4.428,098.616|<br>Propaid expenses<br>152 2. Thué GTGTdugc khéu tir 54.592.720| 119.318.128}<br>Value-added tx deductible<br><!-- End of picture text -->

_<mark>Hình 3. 1: Hình minh họa báo cáo cân đối kế toán</mark>_ 

Điều này gây khó khăn trong việc tổng hợp, đối chiếu và phân tích các chỉ tiêu tài chính, đặc biệt khi cần theo dõi cơ cấu nguồn vốn, khả năng thanh toán, và hiệu quả hoạt động của doanh nghiệp trong giai đoạn cụ thể. Quá trình tổng hợp 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

48 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

báo cáo hiện tại chủ yếu thực hiện thủ công, dẫn đến mất nhiều thời gian, thiếu tính linh hoạt và khó đảm bảo tính cập nhật khi số lượng doanh nghiệp được phân tích ngày càng tăng. 

Xuất phát từ yêu cầu trên, trong đồ án này em sẽ xây dựng và triển khai một mô hình Data Warehouse theo kiến trúc Snowflake Schema - một mô hình được đánh giá là phù hợp cho các hệ thống dữ liệu phức tạp, có cấu trúc phân cấp nhiều cấp độ, đặc biệt là trong lĩnh vực tài chính - ngân hàng. Mô hình này được thiết kế nhằm phục vụ cho việc phân tích, tổng hợp và trực quan hóa dữ liệu tài chính thông qua công cụ Power BI, giúp người dùng không chỉ xem được các báo cáo định kỳ mà còn có khả năng khai thác chuyên sâu, phát hiện các xu hướng và vấn đề tiềm ẩn trong hoạt động tài chính của doanh nghiệp. 

Mục tiêu của hệ thống là tạo ra một nền tảng dữ liệu tập trung, nơi toàn bộ dữ liệu tài chính từ nhiều nguồn khác nhau được tích hợp, làm sạch, chuẩn hóa và lưu trữ trong cấu trúc thống nhất. Từ đó, người dùng có thể dễ dàng truy cập, đối chiếu và phân tích thông tin tài chính một cách nhanh chóng, chính xác và trực quan, phục vụ cho công tác ra quyết định chiến lược cũng như đánh giá hiệu quả hoạt động kinh doanh. 

Để hệ thống Data Warehouse đáp ứng được mục tiêu trên, trước hết cần khảo sát và xác định rõ yêu cầu nghiệp vụ và nhu cầu sử dụng dữ liệu. Trong lĩnh vực tài chính, các yêu cầu này chủ yếu xoay quanh việc tổng hợp, đối chiếu và phân tích các báo cáo tài chính - những công cụ cơ bản phản ánh toàn diện tình hình hoạt động và sức khỏe của doanh nghiệp. Cụ thể, hệ thống cần hỗ trợ phân tích bốn nhóm dữ liệu chính sau: 

Bảng cân đối kế toán: Cung cấp cái nhìn toàn cảnh về tài sản, nợ phải trả và nguồn vốn của doanh nghiệp tại một thời điểm cụ thể. Đây là nền tảng để đánh giá mức độ ổn định tài chính, khả năng thanh toán và cấu trúc vốn. 

Báo cáo kết quả kinh doanh: Trình bày chi tiết về doanh thu, chi phí và lợi nhuận của doanh nghiệp trong từng kỳ kế toán, qua đó phản ánh khả năng sinh lời, hiệu quả hoạt động và xu hướng tăng trưởng trong giai đoạn phân tích. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

49 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Báo cáo lưu chuyển tiền tệ: Mô tả dòng tiền vào và ra từ các hoạt động kinh doanh, đầu tư và tài chính, giúp đánh giá khả năng tạo ra và sử dụng tiền mặt của doanh nghiệp. 

Các chỉ số tài chính: Là tập hợp các tỷ lệ được tính toán từ dữ liệu tài chính, bao gồm các chỉ số như ROE, ROA, Debt Ratio, Equity Ratio, Gross Profit Margin,… giúp nhà quản trị có thể đánh giá khả năng sinh lời, hiệu quả sử dụng vốn và mức độ rủi ro tài chính. 

* Các bảng dữ liệu: 

_Bảng 3. 1: Bảng dữ liệu cân đối kế toán_ 

|**STT**|**Tên cột**|**Ý nghĩa**|
|---|---|---|
|1|source_name|Tên file báo cáo cân đối kế toán|
|2|account_name|Tên chỉ tiêu của giá trị|
|3|code|Mã số chỉ được quy định|
|4|begin_of_period|Giá trị đầu kỳ|
|5|end_of_period|Giá trị cuối kỳ|



_Bảng 3. 2: Bảng dữ liệu danh mục cân đối kế toán_ 

|**STT**|**Tên cột**|**Ý nghĩa**|
|---|---|---|
|1|account_id|Mã số chỉ tiêu theo chuẩn BCTC|
|2|sign|Ý nghĩa: quy ước dấu số khi đưa vào<br>DWH|
|3|account_name|Tên chỉ tiêu tương ứng|
|4|acct_level_01|Tên chỉ tiêu cấp 1|
|5|lv01_id|Mã chỉ tiêu cấp 1|
|6|acct_level_02|Tên chỉ tiêu cấp 2|
|7|lv02_id|Mã chỉ tiêu cấp 2|
|8|acct_level_03|Tên chỉ tiêu cấp 3|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

50 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|9|lv03_id|Mã chỉ tiêu cấp 3|
|---|---|---|
|10||Phân loại tùy chỉnh (có thể giống hoặc|
||acct_level_custom|khác lv02)|
|11|lv_custom_id|Mã phân loại tùy chỉnh|



_Bảng 3. 3: Bảng dữ liệu chỉ tiêu hiệu quả hoạt động_ 

|**STT**|**Tên cột**|**Ý nghĩa**|
|---|---|---|
|1|chi_tieu|Chỉ số tài chính|
|2||Số thứ tự sắp xếp các chỉ tiêu trong toàn|
||Sort|bộ danh mục.|
|3|group|Nhóm chức năng của chỉ tiêu|
|4|group_sort|Thứ tự sắp xếp các nhóm|



_Bảng 3. 4: Bảng dữ liệu báo cáo hợp nhất_ 

|**STT**|**Tên cột**|**Ý nghĩa**|
|---|---|---|
|1|sourcename|Nguồn|
|2|ma_so|Mã số|
|3|chi_tieu|Chỉ tiêu|
|4|thuyet_minh|Tham chiếu đến Thuyết minh Báo cáo tài<br>chính (notes)|
|5|ky_nay|Giá trị thực tế của chỉ tiêu ở kỳ báo cáo|



_Bảng 3. 5: Bảng dữ liệu danh mục báo cáo kinh doanh_ 

|**STT**|**Tên cột**|**Ý nghĩa**|
|---|---|---|
|1|sign|Dấu hiệu tính toán: 1 = cộng, -1 = trừ khi<br>tổng hợp báo cáo|
|2|account_id|Mã định danh duy nhất của chỉ tiêu|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

51 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|3|account_name|Tên chỉ tiêu gốc trong báo cáo|
|---|---|---|
|4|account_type|Loại chỉ tiêu|
|5|report|Loại báo cáo mà chỉ tiêu thuộc về|
|6|Level|Cấp bậc phân loại chỉ tiêu|
|7|account_name_for_report|Tên chuẩn hóa để hiển thị trên báo cáo|



_Bảng 3. 6: Bảng dữ liệu báo cáo chuyển lưu tiền tệ_ 

|**STT**|**Tên cột**|**Ý nghĩa**|
|---|---|---|
|1|Code|Mã số chỉ tiêu theo quy định trong báo<br>cáo tài chính|
|2|chi_tieu|Tên chỉ tiêu trong báo cáo kết quả kinh<br>doanh|
|3|Company|Mã công ty/doanh nghiệp|
|4|Period|Kỳ báo cáo|
|5|Value|Giá trị kỳ báo cáo|



_Bảng 3. 7: Bảng dữ liệu danh mục báo cáo chuyển lưu tiền tệ_ 

|**STT**|**Tên cột**|**Ý nghĩa**|
|---|---|---|
|1|Code|Mã chỉ tiêu của báo cáo lưu chuyển tiền<br>tệ.|
|2|chi_tieu|Tên chỉ tiêu cụ thể trong báo cáo|
|3|Level|Cấp độ hiển thị trong báo cáo|
|4|Level 1|Nhóm lớn hơn mà chỉ tiêu này thuộc về|



_Bảng 3. 8: Bảng dữ liệu thông tin doanh nghiệp_ 

|**STT**<br>1|**Tên cột**<br>ticker|**Ý nghĩa**<br>Mã chứng khoán niêm yết|
|---|---|---|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

52 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|2|org_name|Tên đầy đủ của công ty|
|---|---|---|
|3|org_short_name|Tên viết tắt của công ty|
|4|stock_exchange_unique_id|Sàn giao dịch mà cổ phiếu niêm yết|
|5|sector|Ngành nghề chính của doanh nghiệp|



### **3.2. Thiết kế mô hình Data Warehouse** 

Mô hình Data Warehouse trong đề tài được thiết kế theo kiến trúc Snowflake Schema gồm ba tầng chính là Landing, Staging, và Atomic 



<!-- Start of picture text -->
ie ) {= ()<br><!-- End of picture text -->

_Hình 3. 2: Mô tả 3 tầng trong Data warehouse_ 

Dữ liệu tài chính được tổ chức thành các bảng Fact và Dim nhằm phục vụ mục tiêu báo cáo, phân tích và trực quan hóa. 

Các bảng Fact chứa dữ liệu định lượng - là trung tâm của mô hình, ghi nhận các giá trị cần phân tích như: bảng dữ liệu báo cáo cân đối kế toán, bảng dữ liệu báo cáo báo cáo kinh doanh, bảng dữ liệu báo cáo chuyển lưu tiền tệ. 

Các bảng Dimension cung cấp thông tin mô tả cho dữ liệu trong các bảng Fact, giúp người dùng có thể phân tích dữ liệu theo nhiều khía cạnh khác nhau. Một số bảng Dimension quan trọng bao gồm các bảng danh mục báo cáo cho từng phần cũng như bảng dữ liệu thời gian. 

### **_3.2.1. Vùng Landing_** 

Vùng Landing là lớp đầu tiên trong kiến trúc Data Warehouse đóng vai trò tiếp nhận và lưu trữ dữ liệu thô được trích xuất trực tiếp từ các nguồn khác nhau trước khi được xử lý, làm sạch và chuyển đổi. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

53 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Tại vùng Landing dữ liệu sẽ được giữ nguyên từ dữ liệu nguồn đẩy lên mà không qua xử lý làm sạch. 



<!-- Start of picture text -->
LANDING<br>Bao_cao_hop_nhat Can_doi_ke_toan Chuyen_luu_tien_te<br>Danh_muc_can_doi_ke_toan Thong_tin_doanh_nghiep ‘hi_tieu_hieu_qua_hoat_dong<br>Danh_muc_bao_cao_kinh_doanh Danh_muc_bao_cao_chuyen_luu_tien_te<br>0<br><!-- End of picture text -->

_Hình 3. 3: Các bảng lưu trữ tại vùng Landing_ 

### **_3.2.1. Vùng Staging_** 

Vùng Staging nằm trung gian trong kiến trúc Data Warehouse, nằm giữa vùng Landing và vùng Data Warehouse chính thức. Nhiệm vụ của STG là làm sạch, chuẩn hóa và chuyển đổi dữ liệu nhằm đảm bảo tính nhất quán, toàn vẹn và sẵn sàng cho việc nạp vào kho dữ liệu trung tâm. 

Tại vùng Staging có các bảng dữ liệu sau khi đẩy dữ liệu từ vùng Landing: 



<!-- Start of picture text -->
STAGING<br><!-- End of picture text -->

_Hình 3. 4: Các bảng dữ liệu được lưu trữ tại vùng Staging_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

54 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Sau khi được xử lý dữ liệu thì các bảng dữ liệu sẽ được lưu trữ theo từng bảng dim, fact tương ứng cho từng bảng. Các bảng dữ liệu tại đây cũng đã được làm sạch và phân cấp cho từng mục. 

### **_3.2.1. Vùng Atomic_** 

Vùng Atomic là tầng lõi của Data Warehouse, nơi lưu trữ dữ liệu chi tiết nhất sau khi đã được xử lý và làm sạch từ vùng Staging. Dữ liệu tại đây được chuẩn hóa, có đầy đủ khóa thay thế và khóa ngoại để đảm bảo mối quan hệ giữa các bảng Fact và Dimension. 

Vùng này đóng vai trò trung tâm, cung cấp dữ liệu đầu vào cho các tầng phân tích tiếp theo như trực quan hóa dữ liệu trên các công cụ báo cáo như Power BI. 

- Sơ đồ liên kết dữ liệu trong Data Warehouse: 



<!-- Start of picture text -->
fiom id<br>(ic ee E |<br>— 1 _<br>amt<br>== P in scum evel?<br>(dim date in “ 7<br>:<br>- |dim account levell1<br>ee dim_pal dict -<br><!-- End of picture text -->

_Hình 3. 5: Sơ đồ liên kết dữ liệu DWH_ 

Các bảng trên sẽ được đẩy dữ liệu vào thông qua một quá trình ETL từ những dữ liệu có được từ Staging. Qua đó, ta sẽ thu được các bảng tại DWH như sau: 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

55 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- dim_account : Bảng dim danh mục báo kế toán 

Bảng 3. 9: _Bảng dữ liệu dim_account_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|account_nk|nvarchar|Mã duy nhất định danh cho<br>từng danh mục|
|2|account_name|nvarchar|Tên đầy đủ của danh mục|
|3|sign|nvarchar|Giá trị biểu thị hướng ghi nhận<br>của tài khoản|
|4|lv01_id|nvarchar|Mã cấp 1 -  nhóm chi tiết nhất|
|5|lv02_id|nvarchar|Mã cấp 2 - nhóm tổng hợp<br>trung gian|
|6|lv03_id|nvarchar|Mã cấp 3 - là nhóm tổng hợp<br>cao nhất|
|7|created_date|datetime2|Thời điểm ghi nhận hoặc thêm<br>mới bản ghi|
|8|updated_at|datetime2|Thời điểm cập nhật gần nhất<br>của dữ liệu.|
|9|is_delete|bit|Cờ trạng thái logic|



- dim_account_level03: Bảng danh mục phân cấp level 3 

_Bảng 3. 10: Bảng dữ liệu dim_account_level03_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|lv03_id|nvarchar|Mã phân cấp lv3|
|2|lv03_name|nvarchar|Tên danh mục phân cấp|
|3|updated_at|datetime2|Ngày cập nhật dữ liệu|
|4|is_delete|bit|Cờ trạng thái|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

56 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- dim_account_level02: Bảng danh mục phân cấp level 2 

_Bảng 3. 11: Bảng dữ liệu dim_account_level02_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|lv02_id|nvarchar|Mã phân cấp lv2|
|2|lv02_name|nvarchar|Tên danh mục phân cấp|
|3|updated_at|datetime2|Ngày cập nhật dữ liệu|
|4|is_delete|bit|Cờ trạng thái|



- dim_account_level01: Bảng danh mục phân cấp level 1 

_Bảng 3. 12: Bảng dữ liệu dim_account_level01_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|lv01_id|nvarchar|Mã phân cấp lv1|
|2|lv01_name|nvarchar|Tên danh mục phân cấp|
|3|updated_at|datetime2|Ngày cập nhật dữ liệu|
|4|is_delete|bit|Cờ trạng thái|



- dim_cf_item: Bảng danh mục báo chuyển lưu tiền tệ 

_Bảng 3. 13: Bảng dữ liệu dim_cf_item_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|cf_item_nk|nvarchar|Mã định danh duy nhất cho chỉ<br>tiêu chuyển lưu tiền tệ|
|2|chi_tieu|nvarchar|Tên hoặc mô tả chi tiết của chỉ<br>tiêu chuyển lưu tiền tệ|
|3|level|int|Cấp độ của chỉ tiêu trong cấu<br>trúc phân cấp báo cáo|
|4|level_1|nvarchar|Mã hoặc tên của nhóm cấp 1|
|5|created_date|datetime2|Thời điểm tạo bản ghi|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

57 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|6|updated_at|datetime2|Thời điểm cập nhật gần nhất<br>của bản ghi|
|---|---|---|---|
|7|is_delete|bit|Cờ logic cho biết bản ghi có còn<br>hiệu lực hay không|



- dim_pnl_dict: Bảng dữ liệu danh mục báo cáo kết quả kinh doanh 

_Bảng 3. 14: Bảng dữ liệu dim_pnl_dict_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|pnl_nk|nvarchar|Mã định danh duy nhất cho chỉ<br>tiêu kết quả kinh doanh.|
|2|pnl_name|nvarchar|Tên chi tiết của chỉ tiêu|
|3|pnl_type|nvarchar|Loại chỉ tiêu|
|4|pnl_report|nvarchar|Tên báo cáo|
|5|pnl_level|int|Cấp độ của chỉ tiêu trong cấu<br>trúc phân cấp báo cáo|
|6|pnl_name_for_report|nvarchar|Tên hiển thị rút gọn của chỉ tiêu<br>dùng|
|7|pnl_stt|int|Số thứ tự hiển thị của chỉ tiêu<br>trong báo cáo|
|8|updated_at|datetime2|Thời điểm cập nhật gần nhất|
|9|is_delete|bit|Cờ logic đánh dấu trạng thái|



- dim_company: Bảng dữ liệu thông tin doanh nghiệp 

_Bảng 3. 15: Bảng dữ liệu dim_company_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|company_nk|nvarchar|Mã định danh duy nhất của<br>doanh nghiệp.|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

58 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|2|ticker|nvarchar|Mã chứng khoán niêm yết của<br>doanh nghiệp.|
|---|---|---|---|
|3|org_name|nvarchar|Tên đầy đủ của doanh nghiệp|
|4|org_short_name|nvarchar|Tên viết tắt|
|5|stock_exchange_uniq<br>ue_id|nvarchar|Mã hoặc tên sàn giao dịch<br>chứng khoán nơi doanh nghiệp<br>niêm yết|
|6|sector|nvarchar|Ngành nghề hoặc lĩnh vực hoạt<br>động của doanh nghiệp|
|7|created_date|datetime2|Ngày tạo bản ghi trong hệ<br>thống.|
|8|updated_at|datetime2|Thời điểm bản ghi được cập<br>nhật gần nhất trong quy trình<br>ETL.|
|9|is_delete|bit|Cờ đánh dấu trạng thái bản ghi.|



***** dim_kpi: Bảng chỉ tiêu hiệu quả hoạt động 

_Bảng 3. 16: Bảng dữ liệu dim_kpi_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|kpi_sk|int|Định danh duy nhất cho mỗi chỉ<br>tiêu|
|2|unique_id|nvarchar|Mã hệ thống gốc của chỉ tiêu<br>KPI.|
|3|chi_tieu|nvarchar|Tên chỉ tiêu tài chính|
|4|sort|int|Thứ tự hiển thị của chỉ tiêu<br>trong báo cáo|
|5|group|nvarchar|Nhóm phân loại của chỉ tiêu|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

59 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|6|group_sort|int|Thứ tự hiển thị của nhóm chỉ<br>tiêu trong báo cáo|
|---|---|---|---|
|7|created_date|datetime2|Ngày tạo bản ghi trong hệ thống|
||||Thời điểm bản ghi được cập|
|8|updated_at|datetime2|nhật gần nhất trong quy trình|
||||ETL.|
|9|is_delete|bit|Cờ đánh dấu trạng thái bản ghi|



* dim_date: Bảng dữ liệu thời gian 

_Bảng 3. 17: Bảng dữ liệu dim_date_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|date_sk|int|Khóa định danh của bảng thời<br>gian.|
|2|full_date|date|Ngày đầy đủ|
|3|year|int|Năm của ngày tương ứng|
|4|month|int|Tháng của năm|
|5|month_name|nvarchar|Tên của tháng|
|6|end_of_month|date|Ngày cuối cùng của tháng<br>tương ứng,|
|7|month_year|nvarchar|Biểu diễn dạng chuỗi của tháng<br>và năm.|
|8|month_year_sort|int|Cột hỗ trợ sắp xếp tháng-năm<br>theo thứ tự thời gian|
|9|updated_at|datetime2|Thời điểm cập nhật gần nhất<br>của bản ghi trong hệ thống.|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

60 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- fact_balance_sheet: Bảng dữ liệu báo cáo cân đối kế toán 

_Bảng 3. 18: Bảng dữ liệu fact_balance_sheet_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|bs_sk|int|Khóa chính của bảng|
|2|row_id|nvarchar|Mã định danh trong hệ thống<br>nguồn|
|3|account_nk|nvarchar|Mã<br>liên<br>kết<br>tới<br>bảng<br>dim_account|
|4|date_sk|int|Mã liên kết tới bảng dim_date|
|5|end_value|decimal|Giá trị cuối kỳ|
|6|begin_value|decimal|Giá trị đầu kỳ|
|7|created_date|datetime2|Thời điểm dữ liệu được nạp vào<br>hệ thống lần đầu|
|8|updated_at|datetime2|Thời điểm cập nhật gần nhất|
|9|is_delete|bit|Cờ đánh dấu trạng thái bản ghi|



- fact_cashflow: Bảng dữ liệu báo cáo chuyển lưu tiền tệ 

_Bảng 3. 19: Bảng dữ liệu fact_cashflow_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|cashflow_sk|int|Khóa chính định danh duy nhất<br>cho từng bản ghi|
|2|row_id|nvarchar|Mã định danh trong hệ thống<br>nguồn|
|3|cf_item_nk|nvarchar|Mã liên kết đến dim_cf_item,<br>xác định loại chỉ tiêu tiền tệ|
|4|company_nk|nvarchar|Mã liên kết với dim_company,<br>xác định doanh nghiệp.|
|5|date_sk|int|Mã liên kết tới dim_date|
|6|value|decimal|Giá trị tiền tệ của chỉ tiêu|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

61 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

|7|created_date|datetime2|Thời điểm dữ liệu được nạp|
|---|---|---|---|
|8|updated_at|datetime2|Thời điểm cập nhật gần nhất.|
|9|is_delete|bit|Cờ trạng thái bản ghi|



* fact_consolidated: Bảng dữ liệu báo cáo kết quả kinh doanh 

_Bảng 3. 20: Bảng dữ liệu fact_consolidated_ 

|**STT**|**Tên cột**|**Kiểu dữ liệu**|**Ý nghĩa**|
|---|---|---|---|
|1|cons_sk|int|Khóa chính định danh duy nhất<br>cho mỗi bản ghi|
|2|row_id|nvarchar|Mã định danh trong hệ thống<br>nguồn|
|3|pnl_nk|nvarchar|Mã liên kết với dim_pnl, thể<br>hiện loại chỉ tiêu trong báo cáo<br>kết quả kinh doanh|
|4|value|decimal|Giá trị của chỉ tiêu tài chính<br>tương ứng trong kỳ báo cáo|
|5|date_sk|int|Mã liên kết tới dim_date|
|6|created_date|datetime2|Thời điểm dữ liệu được nạp|
|7|updated_at|datetime2|Thời điểm dữ liệu được cập<br>nhật gần nhất|
|8|is_delete|bit|Cờ trạng thái bản ghi|



_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

62 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **3.3. Xây dựng luồng ETL dữ liệu** 

### **_3.3.1. Luồng ETL tổng quan_** 

Hệ thống được xây dựng theo mô hình ETL ba tầng (Landing đến Staging đến Atomic), nhằm đảm bảo dữ liệu được chuẩn hóa, kiểm soát chất lượng và tối ưu hiệu suất truy vấn cho báo cáo và dashboard. 



<!-- Start of picture text -->
sau<br>U [ al “ _ {~( - ] ) '<br><!-- End of picture text -->

_Hình 3. 6: Mô tả quy trình ETL dữ liệu_ 

Data Sources: vùng dữ liệu bao gồm các nguồn dữ liệu các thông số tài chính, chỉ số phục vụ cho xây dựng báo cáo. 

Landing: Đây là tầng đầu tiên trong mô hình, có nhiệm vụ tiếp nhận dữ liệu thô từ nhiều nguồn khác nhau. Tại đây, dữ liệu được lưu trữ nguyên bản như từ nguồn gốc, chưa qua bất kỳ bước xử lý hoặc chuyển đổi nào, nhằm đảm bảo tính toàn vẹn khi cần đối chiếu hoặc kiểm tra. 

Staging: Tầng trung gian có nhiệm vụ làm sạch, chuẩn hóa và ánh xạ dữ liệu trước khi nạp vào kho dữ liệu chính. Các thao tác xử lý phổ biến bao gồm loại bỏ giá trị trống, loại bỏ trùng lặp, chuẩn hóa định dạng dữ liệu và mã danh mục. Dữ liệu tại tầng này được chuẩn bị kỹ lưỡng để sẵn sàng cho quá trình tải lên tầng Atomic. 

Atomic: Đây là tầng trung tâm của Data Warehouse, nơi dữ liệu đã được chuẩn hóa và lưu trữ theo mô hình Snowflake Schema. Tầng này bao gồm các bảng 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

63 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Dimension và Fact được thiết kế theo quan hệ khóa ngoại – khóa chính, phục vụ cho việc phân tích, tổng hợp và trực quan hóa dữ liệu tài chính trên Power BI. 

### **_3.3.2. Xây quy trình ETL trên SSIS_** 

Quy trình ETL được thiết kế và triển khai trên công cụ SQL Server Integration Services (SSIS) nhằm tự động hóa việc trích xuất, xử lý và nạp dữ liệu vào hệ thống Data Warehouse. Các bước thực hiện trong quy trình được mô tả như sau: 



<!-- Start of picture text -->
Trich xudt di ligu<br>'<br>Y<br>Load dim Lv1<br>Load dim Lv2<br><!-- End of picture text -->

_Hình 3. 7: Mô tả quy trình ETL trên SSIS_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

64 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **_3.3.2.1. Trích xuất dữ liệu (Extract):_** 



<!-- Start of picture text -->
Load Data<br>y<br>Doc dif ligu tu nguén<br>y<br>Yow Check Business Key da N<br>| t6n tai trong Landing ° y<br>co<br>thudc tinh duge Insert new data<br>thay déi<br>—yYes—1__No— y<br>*<br>Cap nhat di liéu Stop<br>y<br><!-- End of picture text -->

_Hình 3. 8: Sơ đồ mô tả Extract Data_ 

Dữ liệu gốc được lấy từ các hệ thống nguồn và đưa vào vùng Landing. Tại đây, dữ liệu được lưu tạm thời để phục vụ cho quá trình xử lý tiếp theo. 

- Các bảng dữ liệu được đọc ra từ nguồn sau đó: 

- + Với lần 1: Đẩy dữ liệu thẳng vào Landing 

+ Với lần 2 trở đi: Ta sẽ kiểm tra dữ liệu đã tồn tại hay chưa bằng các sử dụng SCD để kiểm tra. Nó so sánh dữ liệu mới từ nguồn với dữ liệu hiện có trong bảng đích để xác định: 

- Bản ghi mới chưa tồn tại (New Output) 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

65 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

   - Bản ghi đã tồn tại nhưng có thuộc tính thay đổi (Changing Attribute Updates Output) 

- **_3.3.2.2. Check delete dữ liệu_** 



<!-- Start of picture text -->
Check Delete<br>Start<br>y<br>Doc dif ligu tang can<br>check<br>y<br>Tén tai Check Business Key vdi<br>| tang dau vao<br>Khéng tén tai<br>y<br>Xoa di ligu &<br>tang can check<br>y<br><!-- End of picture text -->

_Hình 3. 9: Sơ đồ mô tả check delete_ 

Bước này kiểm tra các bản ghi đã bị xóa hoặc không còn hợp lệ trong dữ liệu nguồn. Nếu phát hiện, hệ thống sẽ loại bỏ tương ứng để đảm bảo dữ liệu không bị trùng lặp hoặc sai lệch trong các tầng tiếp theo. 

Trong SSIS, việc kiểm tra này được thực hiện thông qua thành phần Lookup. Lookup giúp đối chiếu dữ liệu hiện tại với dữ liệu nguồn dựa trên khóa định danh. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

66 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Nếu bản ghi không còn tồn tại trong nguồn (Lookup No Match Output), hệ thống sẽ xử lý bằng OLE DB Command để cập nhật hoặc đánh dấu bản ghi đó là đã xóa bằng câu lệnh SQL. Ngược lại, các bản ghi còn hợp lệ sẽ được giữ lại để tiếp tục xử lý và nạp sang tầng kế tiếp. 

### **_3.3.2.3. Xử lý dữ liệu (Transform)_** 



<!-- Start of picture text -->
Transformation<br>Y<br>Y<br>Chuyén déifxit ly dav tigu<br>y<br>we Check Business Key da No<br>| tén tai trong Staging y<br>6<br>thudc tinh duge Insert new data<br>thay adi<br>Yes No- +<br>**<br>-<br>Cap nhat da ligu Stop<br>Y<br><!-- End of picture text -->

_Hình 3. 10: Sơ đồ mô tả transformation_ 

Dữ liệu được làm sạch và chuẩn hóa theo các quy tắc nghiệp vụ, bao gồm phân tách các bảng dữ liệu, loại bỏ giá trị null, chuyển đổi kiểu dữ liệu, sắp xếp mã hóa các giá trị khóa thay thế, xử lý SCD và lưu trữ vào Staging. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

67 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **_3.3.2.4. Load dữ liệu_** 

- Load dữ liệu các bảng dim: 



<!-- Start of picture text -->
Load Dim<br>¥<br>Boe dif ligu ti’ Satging<br>A<br>Ndi key cdc bang con véi<br>nhau<br>y<br>7i Check Business Key da No<br>| tén tai trong Atomic y<br>cé<br>thudc tinh duge Insert new data<br>thay déi<br>‘Yes- ‘No- 1<br>+ |<br>Cap nhat di tigu Stop<br>y<br><!-- End of picture text -->

_Hình 3. 11: Sơ đồ mô tả load các bảng dim_ 

Tải dữ liệu vào các bảng Dimension cấp 1 (ví dụ: dim_account_level01, dim_company, dim_date...) vào tầng Atomic . Đây là các bảng mô tả thông tin tham chiếu cho các dữ liệu nghiệp vụ chứ thông tin mô tả, ngữ cảnh cho các bảng fact. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

68 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Load dữ liệu các bảng fact: 



<!-- Start of picture text -->
Load fact<br>Y y<br>Boe dif ligu fact ti Doc dif ligu cdc bang<br>Satging dim tis Atomic<br>y<br>Néi key cae bang véi nhau<br>y<br>Check Business<br>Yes Key bang fact da ton tai ‘No<br>| trong Atomic y<br>co<br>‘thuéc tinh duge Insert new data<br>thay déi<br>—Yes—4——No— 1<br>+ +<br>Cp nhat ee di ligu Stop<br><!-- End of picture text -->

_Hình 3. 12: Sơ đồ mô tả load các bảng fact_ 

Dữ liệu giao dịch chi tiết được nạp vào các bảng Fact (như fact_finance, fact_balance_sheet...). Các bảng này lưu trữ giá trị đo lường và liên kết với các bảng Dimension thông qua khóa ngoại (Foreign Key). 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

69 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **_3.3.2.4. Update delete_** 



<!-- Start of picture text -->
Update Delete<br>y<br>Doc dif liéu tang<br>Atomic<br>y<br>an ook Check Business Key vdi<br>Ton tai: .<br>tang Staging<br>y<br>Cp nhat is_delete<br>Atomic la 1<br>y<br><!-- End of picture text -->

_Hình 3. 13: Sơ đồ mô tả update delete trong Atomic_ 

Bước kiểm tra cuối đảm bảo tính toàn vẹn dữ liệu giữa các tầng Dim – Fact, đồng thời phát hiện và xử lý các bản ghi bị xóa từ hệ thống nguồn. Tại đây dữ liệu sẽ không bị xóa bỏ, nếu dữ liệu so sánh từ Staging bị xóa thì tại Atomic sẽ cập nhật is_delete trong bảng là 1 để đánh dấu là đã bị xóa. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

70 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **CHƯƠNG 4. ỨNG DỤNG PHÂN TÍCH DỮ LIỆU TÀI CHÍNH TRÊN  POWER BI** 

### **4.1. Tích hợp dữ liệu trên Data Warehouse với Power BI** 

Sau khi đã xây dựng và hoàn thiện kho dữ liệu, toàn bộ dữ liệu thu thập của doanh nghiệp đã được tổng hợp, chuẩn hóa và lưu trữ tập trung. Cụ thể, dữ liệu bao gồm các nhóm thông tin chính như báo cáo cân đối kế toán, báo cáo kết quả kinh doanh, báo cáo lưu chuyển tiền tệ, cùng với các chỉ tiêu đánh giá tín nhiệm, quy mô vốn và hiệu quả hoạt động của từng doanh nghiệp qua các kỳ kế toán. 



<!-- Start of picture text -->
100% ~<br>& Results gi Messages<br>cashflow_sk _rowid cf_item_nk<br>1 ff [EBA 28 company7BOBFCF26..nk date_sk20210101 value2033508801.00 created_date2025-09-21 21:20:04.9400000 updated_at2025-10-14 16:06:50.0684247 is_delete0<br>2 2 61c3. 22 TBOBFCF26.. 20220401 -217619793088.00 2025-09-21 21:29:04.9270000 2025-10-14 16:06:50.0745510 0<br>33 CBOF.. 28 7BOBFCF26.. 20220401 7289952791.00 2025-09-21 21:29:04.9400000 2025-10-14 16:06:50.0745510 0<br>44 BEF. 23 TBOBFCF26.. 20220401 3819595312.00 2025-09-21 21:29:04.9300000 2025-10-14 16:06:50.0756891 0<br>5 5 SFF3B. 42 7BOBFCF26.. 20220401 354992967431.00 2025-09-21 21:29:04.9670000 2025-10-14 16.06:50.0756891 0<br>6 6 o1D9.. 29 TBOBFCF26.. 20220401 -18718438614700 2025-09-21 21:29:04.9400000 2025-10-14 16:06:50.0756891 0<br>7 7 800c.. 5 TBOBFCF26... 20220401 -33405924941.00 2025-09-21 21:29:04.8900000 2025-10-14 16.06:50.0767018 0<br>8 8 Bol. 7 TBOBFCF26... 20220401 -8217773187.00 2025-09-21 21:20:04.8930000 2025-10-14 16:06:50.0767018 0<br>9 9 85037... 20 7BOBFCF26.. 20220401 -184851366869.00 2025-09-21 21-29:04.9230000 2025-10-14 16.06:50.0767018 0<br>10 10 7F787... 10 TBOBFCF26.. 20220401 1710518192803.00 2025-09-21 21:29:04.9000000 2025-10-14 16.06:50.0767018 0<br>nou 34770... 38 TBOBFCF26... 20220401 207619462093.00 2025-09-21 21:29:04.9570000 2025-10-14 16.06:50.0777156 0<br>2 2 EBC. 12 TBOBFCF26... 20220401 7583901753120 2025-09-21 21:20:04.9070000 2025-10-14 16:06:50.0777156 0<br>3 13 scD2.. 16 BOBFCF26.. 20220401 -133244384672.00 2025-09-21 21:29:04.9170000 2025-10-14 16:06:50.0777156 0<br>“14 3E4C.. 19 TBOBFCF26.. 20220401 4095602076100 2025-09-21 21:29:04.9200000 2025-10-14 16:06:50.0787200 0<br>1% 15 1076. 8 TBOBFCF26... 20220401 127478302030.00 2025-09-21 21:29:04.8970000 2025-10-14 16:06:50.0787200 0<br>16 16 TISFI.. 2 TBOBFCF26... 20220401 1040948687119.00 2025-09-21 21:20:04.8870000 2025-10-14 16:06:50.0787200 0<br>wow £7783. 17 7BOBFCF26.. 20220401 -302615781690.00 2025-09-21 21-29:04.9200000 2025-10-14 16:06:50.0787200 0<br>%~ 18 C03. 6 7BOBFCF26.. 20220401 227006537900 2025-09-21 21:20:04 8930000 2025-10-14 16:06:50.0797236 0<br>19 19 3330... 30 TBOBFCF26... 20220401 -164416290923.00 2025-09-21 21:29:04.9600000 2025-10-14 16:06:50.0797236 0<br>2 20 p91. 34 TBOBFCF26... 20220401 -20384441666238.00 2025-09-21 21:20:04.9500000 2025-10-14 16:06:50.0797236 0<br>© Query executed successfully. @ DESKTOP-19B73T3\BAC (16.0 RTM) DESKTOP-19B73T3\HNC (55) Atomic Finance 00:0¢<br><!-- End of picture text -->

_<mark>Hình 4. 1: Hình minh họa bảng dữ liệu fact lưu chuyển tiền tệ trong DWH</mark>_ 

Trên cơ sở dữ liệu tập trung này, bước tiếp theo là tích hợp Data Warehouse với công cụ Power BI nhằm khai thác, trực quan hóa và trình bày thông tin dưới dạng các báo cáo động. 

Power BI sẽ được sử dụng như công cụ trình bày, cho phép người dùng truy xuất dữ liệu nhanh chóng, thực hiện phân tích đa chiều và theo dõi các chỉ số tài chính trọng yếu như doanh thu, chi phí, lợi nhuận, cơ cấu vốn và khả năng sinh lời của doanh nghiệp. 

Thông qua việc tích hợp này, hệ thống Power BI giúp kết nối liền mạch giữa tầng lưu trữ dữ liệu và tầng hiển thị thông tin, tạo nên một quy trình phân tích - 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

71 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

báo cáo tự động, chính xác và linh hoạt, phục vụ hiệu quả cho công tác đánh giá tín nhiệm và ra quyết định. 

Từ Power BI kết nối với Data Warehouse , ta sẽ tiến hành trích xuất dữ liệu ra để làm báo cáo một cách dễ dàng. 



<!-- Start of picture text -->
Fie Home Inset Mode<br>G la BIy ae a<br>|» = Soe ua ir outs me loons >) «<br>1 smsony oon Ebem<br>cI= a ee we<br>(EE apa x nha a mhFat ite ng owe FOOBDAa®<br>Errer sme ete 288<br>a “ Rial f e@08<br>Be 1dr hat 08 c 5 fe &<br>al Page | rere enon<br><!-- End of picture text -->

_Hình 4. 2: Kết nối Power Bi với Data Warehouse_ 

Mô hình quan hệ dữ liệu trong Power BI được xây dựng dựa trên cấu trúc của Data Warehouse, đảm bảo tính thống nhất và đồng bộ giữa hai hệ thống, các mối quan hệ giữa các bảng được thiết lập tương tự như trong Data Warehouse: 



<!-- Start of picture text -->
Benmts Doccomiane Dineen Bom scout evan<br>i<br>1<br>ij Blamscare a<br>Bamatnen mo — -<br>= oa : : Danone _ 7 :<br><!-- End of picture text -->

_Hình 4. 3: Mô hình quan hệ các bảng dữ liệu được tải lên Power BI_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

72 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **4.2. Xây dựng các Dashboard báo cáo tài chính** 

### **_4.2.1. Báo cáo tổng quan Cân đối kế toán_** 

- Bối cảnh: 

   - Dữ liệu đến từ kế toán tổng hợp nhiều bảng 

   - Ban lãnh đạo cần bức tranh nhanh về tổng tài sản, cơ cấu vốn, tỷ lệ nợ/vốn chủ, biến động theo tháng/quý và so sánh giữa các kỳ. 



<!-- Start of picture text -->
Finance Deshboerd | Bio cho Cin bik tosn<br>; O—O chat wot at a === ==<br>dco = 3 | a en<br>poe | ee beer eel one tam<br>CO CAU TONG NGUON VON (Gaphiet etc dtes 149166 269.64 122202 453<br>i ge j 5 Baan 1491897237108 1258793528<br>Poon@ | H SoREbeGbeote Oman=) wo? soasepanna<br>j oo) TSP) OP PP PoP fo bdo popoaog ate i 10168 1860 sos a7<br>i a ~ reat anmes |ensrea?—zse0zs ssasens 7a)<br><!-- End of picture text -->

_Hình 4. 4: Báo cáo tổng quan cân đối kế toán_ 



<!-- Start of picture text -->
cOcku Tone hi sAN THEO THANG<br><!-- End of picture text -->

_Hình 4. 5: Biểu đồ cơ cấu tổng tài sản_ 

Tổng giá trị tài sản của doanh nghiệp theo từng tháng và được chia thành 2 nhóm chính tài sản dài hạn và tài sản ngắn hạn. Mục tiêu là giúp người xem hiểu 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

73 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

doanh nghiệp đang phân bổ tài sản như thế nào và tỷ lệ thanh khoản của tổng tài sản. 

Tỷ trọng giữa 2 nhóm : 

- Ở các kỳ thông thường, tài sản ngắn hạn chiếm khoảng 45-55% tổng tài sản, doanh nghiệp vận hành chủ yếu bằng vốn lưu động (hàng tồn, tiền mặt, khoản phải thu) 

- Riêng tháng 12/2021 và 1/2022, tỷ trọng tài sản ngắn hạn tăng mạnh, cho thấy xu hướng tăng tính thanh khoản, có thể để chuẩn bị cho thanh toán, đầu tư ngắn hạn hoặc trả nợ ngắn hạn. 

- Tài sản dài hạn ít biến động, cho thấy cơ sở vật chất và đầu tư dài hạn ổn định ít rủi ro tài sản cố định. 

Một vài nhận định: 

- Doanh nghiệp tăng tổng tài sản và vốn chủ liên tục sức khỏe tài chính tốt, khả năng mở rộng cao. Tài sản tăng mạnh đầu và cuối năm, tập trung ở tài sản ngắn hạn. 

- Cơ cấu thiên về vốn tự có, tỷ lệ nợ thấp suy ra ít rủi ro lãi vay. 

- Tài sản ngắn hạn tăng mạnh suy ra khả năng thanh toán cao, linh hoạt dòng tiền. 

- Có thể chuyển một phần tài sản ngắn hạn sang đầu tư dài hạn để tối ưu lợi nhuận. Giảm vay ngắn hạn, tăng vốn chủ, theo dõi dòng tiền hoạt động. 

### **_4.2.2. Báo cáo Cơ cấu tài sản chi tiết_** 

* Bối cảnh: 

- Cần đo lường khả năng thanh toán ngắn hạn mà không phụ thuộc vào hàng tồn kho, giúp đánh giá mức độ sẵn sàng của doanh nghiệp trong việc chi trả các khoản nợ ngắn hạn nếu gặp khủng hoảng thanh khoản. 

- Đo hiệu quả sử dụng tài sản (vòng quay vốn, tồn kho, tiền mặt). 

- Tối ưu cơ cấu tài sản – nguồn vốn để hạn chế rủi ro lãi vay 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

74 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
Finance Dashboard | Co’ cdu nguén von chi tiét<br>i ro wee H<br>alFecccmeins OSDM MOI oo= Chinunign suit host dng ous f= 5 H<br>FE contgnan GA A A AE OS Pt EA SF = i<br>ral codetisn une Béndingeceninen H<br><!-- End of picture text -->

_Hình 4. 6: Báo cáo cơ cấu tài sản chi tiết_ 



<!-- Start of picture text -->
av ve<br>Backto report | chi SO THANHTOAN THEO THANG<br>i Fe os Sd<br><!-- End of picture text -->

_Hình 4. 7: Biểu đồ chỉ số thanh toán_ 

Mỗi quý đều có chu kỳ rơi - phục hồi. Điều này phản ánh mô hình dòng tiền mùa vụ - có thể do doanh nghiệp nhập hàng / trả công nợ vào giữa và cuối năm, sau đó thu tiền đầu quý. 

Chỉ số thanh toán duy trì quanh mức 1.3–1.5, đảm bảo an toàn nhưng biến động mạnh theo chu kỳ quý. Khoảng cách Current và Quick ratio 0.2–0.3 phản ánh hàng tồn chiếm 1/4 tài sản ngắn hạn. Doanh nghiệp cần giảm hàng chậm luân chuyển và tăng dự trữ tiền mặt để ổn định dòng vốn lưu động. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

75 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
ny v<br>&Backto report | cui Tidy wiGU SUATHOATDONG THEO THANG<br>j '<br>|Aa<br><!-- End of picture text -->

_Hình 4. 8: Biểu đồ chỉ tiêu hiệu quả hoạt động_ 

Cả hai chỉ số đều có chu kỳ 3–4 tháng/lần, với các đỉnh vào tháng 3 - 4 mùa bán cao điểm. Tháng 8 - 9 mùa tái nhập - tái bán. Cho thấy mô hình hoạt động mang tính mùa vụ rõ rệt: đầu và giữa năm doanh thu tăng, cuối năm hàng tồn tăng. 

Khi vòng quay hàng tồn kho > vòng quay tài sản thì hàng hóa bán ra nhanh hơn tốc độ tăng tài sản (hiệu quả tốt). Khi vòng quay hàng tồn kho < vòng quay tài sản thì doanh nghiệp đang tích trữ tài sản nhiều hơn doanh thu sinh ra. 

Một vài nhận định: 

- Hiệu suất hoạt động của doanh nghiệp dao động theo chu kỳ quý, đạt đỉnh vào tháng 4 và 9, giảm sâu cuối năm. 

- Khoảng cách giữa vòng quay hàng tồn kho và tài sản cho thấy cuối năm vốn bị ứ đọng trong kho và đầu tư dài hạn. 

- Cần điều chỉnh kế hoạch nhập hàng và đầu tư để tránh mất cân đối dòng tiền, đồng thời nâng hiệu suất khai thác tài sản hiện có. 



<!-- Start of picture text -->
«<br>168) 09<br>sr009<br>sea) SS:<br>neem<br><!-- End of picture text -->

_Hình 4. 9: Biểu đồ thể hiện cơ cấu tài sản_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

76 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Tại thời điểm báo cáo, tài sản dài hạn chiếm tới 70%, trong đó 33% tài sản dài hạn khác - phản ánh xu hướng mở rộng nhưng tiềm ẩn rủi ro dòng tiền. Tiền mặt chỉ đạt 11%, cần được bổ sung để đảm bảo thanh khoản. Doanh nghiệp nên cân bằng lại cơ cấu đầu tư, ưu tiên hoàn thiện dự án và tăng vốn lưu động trong ngắn hạn. 

### **_4.2.3. Báo cáo Cơ cấu nguồn vốn chi tiết_** 

- Bối cảnh: 

   - Phòng Tài chính mong muốn đo lường mức độ an toàn và hiệu quả sử dụng nguồn vốn của doanh nghiệp theo thời gian, bằng cách theo dõi tỷ lệ nợ trên vốn chủ sở hữu, tỷ trọng nợ ngắn hạn - dài hạn, và sự biến động của các khoản vốn chủ. 

   - Đánh giá khả năng tự chủ tài chính và mức độ phụ thuộc vào vốn vay. 

   - Theo dõi xu hướng cơ cấu nguồn vốn để phát hiện sớm rủi ro thanh khoản hoặc mất cân đối tài chính. 

   - Hỗ trợ ra quyết định tái cấu trúc vốn, tối ưu hóa chi phí lãi vay và đảm bảo sức khỏe tài chính dài hạn cho doanh nghiệp. 



<!-- Start of picture text -->
2. fMLP |<br><!-- End of picture text -->

_Hình 4. 10: Báo cáo cơ cấu nguồn vốn chi tiết_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

77 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
ay ve<br>< Secktoreport | BIEN BONO che eH TEU NEUON VON THEO THANG<br>ohnot hinpon di i<br>i a os<br>j on<br><!-- End of picture text -->

_Hình 4. 11: Biểu đồ thể hiện biến động chỉ tiêu nguồn vốn_ 

Nguồn vốn chủ có xu hướng tăng cuối kỳ, giúp giảm nhẹ tỷ lệ D/E và củng cố năng lực tài chính. Tuy nhiên, chưa có dấu hiệu tăng trưởng liên tục nên doanh nghiệp vẫn phụ thuộc nhiều vào vốn vay. 

Biên độ lợi nhuận thấp và thiếu ổn định phản ánh khả năng sinh lời biến động theo chu kỳ hoạt động. Đỉnh cao nhất vào tháng 1, thấp nhất vào tháng 11 lợi nhuận có xu hướng giảm dần nửa cuối năm. Giai đoạn cuối năm dù vốn chủ tăng mạnh, lợi nhuận chưa cải thiện tương xứng hiệu quả đầu tư vốn chưa cao. 

Mục tiêu thời gian tới là nâng cao hiệu quả kinh doanh và duy trì biên lợi nhuận dương ổn định, để tăng vốn tự có mà không cần huy động thêm. 



<!-- Start of picture text -->
ry vo<br>oy<Backsagt to reportie st| COCAU VONge VAY NGAN& DAIHAN THEO THANG<br>i see<br>i<br><!-- End of picture text -->

_Hình 4. 12: Biểu đồ cơ cấu vốn vay ngắn và dài hạn_ 

Nợ ngắn hạn chiếm trung bình 92-97%, chỉ còn lại 3-8% là nợ dài hạn.Điều này cho thấy doanh nghiệp đang phụ thuộc rất mạnh vào nguồn vốn ngắn hạn, chủ yếu phục vụ vốn lưu động và thanh toán ngắn kỳ. Doanh nghiệp có khả năng xoay 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

78 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

vòng vốn nhanh, nhưng chịu áp lực lớn về dòng tiền và chi phí tài chính do kỳ hạn vay ngắn. 

Cuối năm, ta đã có tín hiệu tích cực khi tăng tỷ trọng nợ dài hạn lên gần 30%, tuy nhiên sang đầu năm sau tỷ lệ này lại giảm trở lại. Điều này cho thấy chính sách vốn của doanh nghiệp vẫn chưa ổn định. Trong thời gian tới, mục tiêu của phòng tài chính là duy trì cơ cấu nợ hợp lý 70-30 giữa ngắn và dài hạn, đồng thời tận dụng nguồn vay dài để giảm rủi ro thanh khoản và chi phí lãi vay. 



<!-- Start of picture text -->
< BIEN DONG NGUONVON<br>— —<br><!-- End of picture text -->

_Hình 4. 13: Biểu đồ biến động nguồn vốn_ 

Tổng nguồn vốn đầu kỳ đạt 7.244 tỷ, nhưng cuối kỳ gần như về 0. Đây là mô phỏng sự phân rã nguồn vốn, thể hiện tổng mức giảm trừ ở tất cả các khoản mục trong kỳ. 

Các khoản như phải trả người lao động, thuế và nghĩa vụ Nhà nước, chi phí phải trả ngắn hạn... đều giảm, thể hiện doanh nghiệp đang thực hiện thanh toán đầy đủ các nghĩa vụ ngắn hạn. Đây là tín hiệu tích cực về quản trị công nợ, nhưng cũng làm dòng tiền ra tăng, ảnh hưởng thanh khoản ngắn hạn. 

Doanh nghiệp ưu tiên giảm vay ngắn hạn, nhưng chưa có nguồn vốn dài hạn bù đắp, dẫn tới co hẹp tổng nguồn vốn. Lợi nhuận thấp → không đủ tái đầu tư → vốn chủ không tăng, dẫn đến hiệu ứng thu hẹp kép giữa nợ và vốn tự có. Thiếu kế hoạch phân bổ vốn thay thế khi trả nợ → nguồn vốn bị “rút” khỏi chu kỳ hoạt động. 

Trong thời gian tới, cần tập trung vào cân bằng lại cơ cấu vốn - duy trì tỷ lệ nợ hợp lý, đồng thời nâng hiệu quả sinh lời để tạo vốn nội sinh cho tái đầu tư. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

79 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **_4.2.4. Báo cáo Tổng quan chuyển lưu tiền tệ_** 

- Bối cảnh: 

Cần đo lường dòng tiền vào và ra của doanh nghiệp trong chu kỳ hoạt động. So sánh dòng tiền vào và dòng tiền ra để xác định thặng dư hoặc thâm hụt dòng tiền. Giúp đánh giá khả năng tạo tiền, thanh khoản, khả năng trả nợ và hiệu quả sử dụng vốn. 



<!-- Start of picture text -->
i cing wince penn é) - H<br>HB|<br><!-- End of picture text -->

_Hình 4. 14: Báo cáo tổng quan chuyển lưu tiền tệ_ 



<!-- Start of picture text -->
g<br>§<br>8m49<br>Ee<br>3 ons<br>3 coo<br>é<br>an wea<br>Gere Yor<br><!-- End of picture text -->

_Hình 4. 15: Biểu đồ thể hiện tiền mặt cuối kỳ_ 

Doanh nghiệp chưa có dòng tiền hoạt động ổn định; các đợt tăng tiền đều mang tính thời điểm, không duy trì qua nhiều quý. Sau đỉnh 2022Q1, tiền mặt giảm liên tục 4 quý liền. Mức trung bình tiền cuối kỳ 2022 chỉ khoảng 330 tỷ, thấp hơn 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

80 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

2-3 lần so với 2021, đây là dấu hiệu rút vốn hoặc tăng chi trả, có thể do: Tăng chi phí đầu vào, trả nợ vay ngắn hạn, dòng tiền hoạt động âm cho hàng tồn kho cao, thu tiền chậm. 

Cứ mỗi 3-4 quý, tiền lại chạm đáy rồi tăng trở lại cho thấy chu kỳ kinh doanh hoặc thu hồi vốn kéo dài 9–12 tháng. Điều này quan trọng khi lập kế hoạch dòng tiền năm tài chính: Cần tăng dự phòng tiền mặt vào các quý thấp điểm, duy trì vay quay vòng để tránh hụt vốn sản xuất. 



<!-- Start of picture text -->
ye<br>€ Back<br>to report | BIEN DONG DONG TIEN THEO GUE<br>eng tin vio © Ding tén ra<br>ox<br>ox<br>3K<br>15K<br>250K an<br>=Baox 39K aK 40K aK<br>8<br>5§ 30K 2K 2K<br>A aK<br>$= 20K 17K 19K 1K<br>3 x 1K 13K<br>. i10K : i<br>« 202VQH 2022 -202QS_— 0A! 202-7022Cuarter Year 202GI_—0ZQA_—202FQI_—in 20272<br><!-- End of picture text -->

_Hình 4. 16: Biểu đồ biến động dòng tiền vào và ra_ 

Năm 2021 là năm doanh nghiệp đạt hiệu quả vận hành cao nhất, dòng tiền vào luôn lớn hơn dòng tiền ra, chứng tỏ khả năng tạo tiền tốt, xoay vòng vốn linh hoạt. 

Sau 2021, doanh nghiệp bước vào giai đoạn siết dòng tiền. Hoạt động kinh doanh vẫn dương nhưng biên tạo tiền mỏng, phần lớn tiền vào ra được dùng để trả nợ hoặc bổ sung vốn lưu động. 

Từ đầu 2023, dòng tiền vào và ra gần như cân bằng, thể hiện mức độ co hẹp hoạt động. Cần tập trung đẩy mạnh dòng tiền từ hoạt động kinh doanh, kiểm soát chặt chi phí đầu tư, và duy trì mức tiền mặt tối thiểu để đảm bảo thanh khoản bền vững. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

81 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
< situ DOno pono rien tueo novON ode Taco<br>2x<br>85 1K | 15K 19K.<br>§ 08k on 08k 0.7K<br>3& 0.8K 1.1K 09K a - oak 1.5K 0.6K.<br>© ax 14K 13K<br>aK<br>aera zoavar §202vas eaves aoarar ame mre maar aATaI_ FW<br><!-- End of picture text -->

_Hình 4. 17: Biểu đồ dòng tiền theo nguồn gốc_ 

Giai đoạn 2021, doanh nghiệp vận hành tốt - dòng tiền kinh doanh dương liên tục, tài chính âm do trả nợ hoặc chia cổ tức là dấu hiệu lành mạnh. 

2022 là năm căng thẳng thanh khoản. Doanh nghiệp rút mạnh tiền từ tài chính , dòng tiền kinh doanh dương lớn, giúp cân bằng. Tuy nhiên, mức âm tài chính lớn báo hiệu trả nợ cao hoặc giảm vay vốn, gây áp lực tiền mặt. 

Dòng tiền cho thấy doanh nghiệp đang trong giai đoạn co vốn - giảm vay, tự xoay vòng bằng lợi nhuận kinh doanh, nhưng điều này cũng khiến tiền mặt suy giảm nhanh. 

Nếu duy trì mô hình này, cần đảm bảo biên lợi nhuận và vòng quay tiền mặt cao, nếu không sẽ thiếu vốn hoạt động 

### **_4.2.5. Báo cáo Tổng quan kết quả kinh doanh_** 

* Bối cảnh: 

- Theo dõi hiệu quả kinh doanh theo tháng/kỳ báo cáo. 

- Đánh giá cấu trúc doanh thu - chi phí - lợi nhuận, xác định điểm mạnh/yếu theo từng giai đoạn. 

- Cung cấp dữ liệu trực quan để ra quyết định điều chỉnh giá bán, kiểm soát chi phí, hoặc tái cơ cấu danh mục sản phẩm. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

82 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
Finance Dashboard § | Bao cao két qua kinh doanh<br>H | coche bot we ) :<br>i & soe [RET oUx mT DOAN = }<br>oe | - chiiew Mass Kybiocio Kysosinh Chénhléeh | |<br>;Ei i ~ = . ‘DoanSpach2.Cickhodngiimtrirdoanh than hingricang 12 62280142758 7692763 6630041worse | |<br>la * am seo 3.oeashthathain<br>7<br>——; = ings cmgedp dichéhinve 10 64290050 7697763 56587287 :<br>oo<br>: = a = .Gavéa hang bin 11 ss667334 7479929 saismase|<br>H¥—: cxclyradn . aw aaPan Hoe Se Sie et He Si Hy Sew aHea Hy eH vacangSDemiakonSiehSUotahusn7. phi tiip dich chinkgiprobinhingrsGiogiit 20zi22 39025362sns64oa2eauz 2.10704555724ans 308065799730037azaane| | |<br>A rll UNTT THEO CAU PHAN DOANH THU, CHI PHI Chi phi tai chin -Chi phi ii 23 5172863 3.144.06 4858657, |<br>degen ‘chiphi bin hing 24 s7o1s11 932937 7971594<br>i || 9chiphiqentydombaghp 25 7477730 sz0sas enocras) £<br>; shin olor<br>3 thuin host 30 48149662 1720036 42420026 |<br>engin doa<br>2 ibaqui kinds onpa i 12.Chiphi khae 32 69,25281 3470.77 85,782.08, |<br>a) a 13.01 nhuda Khe 40 3765103 277022 34s8081| |<br>; L4Tingliniuinhétein 50 a4na0zs5. 1997850 42082427<br>i§ cnn st wr EE doa15.Chi phiaghip thué hie thu han nhip_ 51 754,937.93 13,719.76 74121817, |:<br>H oo Viginhainsmuthacthy 60 97944819 3369039 94595036<br>; ship doa neh :<br><!-- End of picture text -->

_Hình 4. 18: Báo cáo tổng quan kết quả kinh doanh_ 



<!-- Start of picture text -->
rd vy<br>Back re co cAuuNrT Heo THANG<br>(©10.10% nhusin thin ti hoat dng kink doanh @ 13.10% nhusin Khde<br>3529<br>to<br>a)<br>z s1ss<br>5<br>=<br>Z40 44.02 4229 35.68 2296<br>2002 2859 2640<br>20 as Oe i 1991 19.98<br>1301 2535 3<br>; | | | = | ne 5<br>gs - & = = 2 38 € @ € €@ 3 § €<br>2 2 3 2 § $2  € Gs € 2<br>2 °° g§ g¢ 4 f<br>& 2 8<br>2024 2022<br><!-- End of picture text -->

_Hình 4. 19: Biểu đồ cơ cấu lợi nhuận trước thuế_ 

Đỉnh cao vào 5/2021 với lợi nhuận trước thuế là 85.29 tỷ  gấp 4 lần trung bình các tháng khác, phản ánh mùa vụ hoặc bùng nổ doanh số. 

Các tháng thấp điểm như 6/2021, 10/2021, 11/2021 dao động 10-20 tỷ, cho thấy chu kỳ lợi nhuận ngắn hạn và phụ thuộc doanh thu. 

Năm 2022 trở đi, lợi nhuận trước thuế vẫn dương, chứng tỏ doanh nghiệp duy trì lãi ổn định dù biên độ giảm. Dòng tiền kinh doanh vẫn tích cực, nhưng hiệu quả tài chính cần được tối ưu để tránh biến động lớn theo mùa. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

83 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
< LTT THEO CAU PHAN DOANH THU, CHI PHI<br>100%<br>Tong Doanh th<br>Chi ph quan DN<br>wr<br><!-- End of picture text -->

_Hình 4. 20: Biểu đồ lợi nhuận thu và chi_ 

Cơ cấu chi phí hiện tập trung cao ở tài chính và giá vốn, phản ánh doanh nghiệp phụ thuộc nặng vào nguồn vốn vay hoặc chi phí sản xuất tăng. 

Nếu tối ưu được chi phí tài chính (giảm lãi suất vay, tái cấu trúc nợ), biên lợi nhuận có thể cải thiện thêm 2-3%, tương đương hàng chục tỷ đồng mỗi kỳ. 

Báo cáo kết quả kinh doanh cho thấy, doanh nghiệp đạt tăng trưởng mạnh cả doanh thu lẫn lợi nhuận, tuy nhiên biên lợi nhuận còn mỏng do chi phí tài chính cao. 

Cần tập trung vào tái cấu trúc vốn vay, giảm chi phí lãi suất và nâng hiệu quả vận hành, từ đó hướng đến mức lợi nhuận bền vững hơn, không phụ thuộc vào thời vụ hay biến động giá nguyên liệu. 

### **_4.2.6. Báo cáo Hiệu quả kinh doanh_** 

- Bối cảnh: 

Cần ttheo dõi mức độ hiệu quả trong việc sử dụng chi phí để tạo ra lợi nhuận, cụ thể: 

- Đánh giá hiệu quả vận hành qua chi phí bán hàng, quản lý, tài chính. 

- Theo dõi khả năng sinh lời qua các chỉ số ROA, ROS, ROE. 

- Liên kết hiệu quả - chi phí - doanh thu để nhận diện nguyên nhân thay đổi lợi nhuận. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

84 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
Finance Dashboard | _Hiéu qua kinh doanh<br>; bess Whiecie :<br>i Nin chi 9 hpi ne i<br>Ee A cute . sp . i<br>_ | oom rr a cfu chips :<br>Jodeci A :<br>E coctouiain * Y \, 8 as a H<br>: ER Be EE A PM it eee;<br>i a (Chis Wha nang sinh lot ees sine ‘BEN DONG CAc cH THEU RKO (eect: na bie i<br>Hier 2 7 i H<br>_aepom EIx x» \y  a ASeedae oh yt.S & eS ii<br><!-- End of picture text -->

_Hình 4. 21: Báo cáo Hiệu quả kinh doanh_ 



<!-- Start of picture text -->
{ tocktorepot | NNWeH sO eM pn THEO THANG<br>Chitigu @cPQIN/DT ©cPTC/OT @GVHE/OT<br>a<br>138 192<br>1st<br>1 oso bso 036 7, is<br>on<br>obs 31 0it aw 36et oor ns ast on omgoat<br>Jannate2021 Mar2021—-May2021.-=—=«Julis 2021.»wheySep2021.——Nov2021.003 —* —009‘Jan 2022,» Mar 202200s<br>Year<br><!-- End of picture text -->

_Hình 4. 22: Biểu đồ nhóm chỉ số chi phí_ 

Giá vốn hàng bán / Doanh thu đỉnh 6.9 vào 5/2021, khả năng cao do giá nguyên vật liệu tăng hoặc doanh thu bị sụt mạnh, khiến tỷ lệ chi phí/doanh thu tăng vọt. Sau đó, giảm mạnh xuống dưới 1 từ 6/2021, chứng tỏ doanh nghiệp đã xử lý tồn kho hoặc tái thương lượng giá đầu vào thành công. 

Chi phí tài chính / Doanh thu duy trì quanh 0.05–0.1, không xuất hiện biến động bất thường cho thấy cơ cấu tài chính an toàn. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

85 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Chi phí quản lý / Doanh thu, giai đoạn 5/2021 tăng nhẹ 0.69 có thể do mở rộng nhân sự hoặc chi phí quản trị mùa vụ. Sau đó, ổn định quanh 0.05–0.1, phản ánh bộ máy gọn nhẹ, hiệu suất cao. 



<!-- Start of picture text -->
2.<br>rs 66 6<br>r _ 39<br>33 31<br>ee ee ee ee li EE ee ES<br>s6S = *< 2 -§ ©& §Hl 5&€ 3§ 6S¢ 2<br>2021 a 2 a 2022<br>Month<br><!-- End of picture text -->

_Hình 4. 23: Biểu đồ cơ cấu chi phí theo tháng_ 

Giá vốn hàng bán chiếm tỷ trọng lớn nhất 70-80%, là yếu tố quyết định tổng chi phí. 

Tháng 4/2021 chi phí tăng đột biến 127 tỷ- gấp đôi các tháng trước, chủ yếu do giá vốn tăng mạnh 94 đơn vị suy ra khả năng cao liên quan đến biến động giá nguyên liệu hoặc doanh thu sụt giảm. 

Từ tháng 5/2021 trở đi, chi phí giảm nhanh và ổn định quanh 40-90 tỷ, thể hiện doanh nghiệp kiểm soát chi phí hiệu quả hơn. 

Chi phí bán hàng, quản lý và tài chính dao động nhẹ 6-10 tỷ/tháng, chứng tỏ bộ máy tinh gọn, chi phí cố định ổn định. 

Năm 2022, tổng chi phí duy trì mức thấp hơn năm trước 31-53,dấu hiệu tối ưu vận hành và cải thiện hiệu suất lợi nhuận. 

Doanh nghiệp có giai đoạn chi phí tăng bất thường vào tháng 4/2021, nhưng đã nhanh chóng ổn định và duy trì chi phí hợp lý từ nửa cuối 2021 đến 2022, phản ánh khả năng kiểm soát giá vốn và chi phí vận hành tốt hơn rõ rệt. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

86 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **4.3. Trợ lý AI** 

Trong quá trình làm việc và triển khai các hoạt động khai thác dữ liệu trong phạm vi đồ đán tốt nghiệp này, em nhận thấy rằng mức độ phức tạp của hệ thống Data Warehouse có thể gây khó khăn cho những người dùng không am hiểu sâu về SQL. Do đó, việc dựng một trợ lý AI dưới dạng chatbot tích hợp ChatGPT thông qua OpenAI API để nhằm hỗ trợ người dùng khai thác dữ liệu trong Data Warehouse mà không cần kiến thức chuyên sâu về SQL hay cấu trúc cơ sở dữ liệu trở nên cần thiết. Trợ lý này cho phép người dùng tương tác với hệ thống thông qua ngôn ngữ tự nhiên, từ đó có thể tự thực hiện các thao tác như truy vấn dữ liệu, xem thông tin bảng kho dữ liệu hoặc yêu cầu tạo các biểu đồ trực quan đơn giản. 

* Mục tiêu của trợ lý AI: 

- Hỗ trợ truy vấn dữ liệu bằng ngôn ngữ tự nhiên, giúp người dùng dễ dàng lấy thông tin mà không cần kỹ năng SQL. 

- Giảm tải khối lượng công việc cho bộ phận IT/Data, khi không phải hỗ trợ những truy vấn đơn giản lặp đi lặp lại. 

- Tăng khả năng tiếp cận kho dữ liệu cho các bộ phận nghiệp vụ như: tài chính, kinh doanh, kế toán, quản lý rủi ro… 

Để triển khai chức năng trợ lý AI, hệ thống sử dụng mô hình ngôn ngữ tự nhiên của ChatGPT thông qua API do OpenAI cung cấp. Ứng dụng sẽ gửi câu hỏi của người dùng qua API. ChatGPT phân tích nội dung câu hỏi, xác định mục tiêu truy vấn và các thực thể dữ liệu liên quan như “doanh thu”, “tháng 3”, “năm 2023”. Sau đó, ChatGPT sinh ra câu lệnh SQL tương ứng hoặc mô tả thao tác cần thực hiện. 

_<mark>Hình 4. 24: API key của OpenAI</mark>_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

87 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 



<!-- Start of picture text -->
Sơ đồ luồng của Chatbot:<br><!-- End of picture text -->



<!-- Start of picture text -->
GPT phan tich<br>cau hdi<br>Liét ké bang Cac cét cla bang query sql/chart<br>Doc DB tra vé list cac LAy danh sach cdc pk ah<br>cat tiv DB Sinh sql/vé biéu do Chatgpt gen<br>Backend tra JSON<br>phan hai cho frontend<br>Hién thi két qua cho<br>ngudi dung<br><!-- End of picture text -->

_Hình 4. 25: Sơ đồ luồng cho trợ lý AI tích hợp chatgpt_ Trợ lý AI có khả năng cung cấp cho người dùng toàn bộ thông tin liên quan đến cấu trúc dữ liệu trong cơ sở dữ liệu - bao gồm danh sách các bảng, các trường trong bảng, kiểu dữ liệu của mỗi trường. Nhờ khả năng cung cấp thông tin cấu trúc đầy đủ, người dùng có thể: 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

88 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Dễ dàng xác định bảng nào chứa dữ liệu mình cần. 

- Hiểu được ngữ nghĩa của từng trường, tránh nhầm lẫn khi phân tích 

- Nhanh chóng nắm được mô hình dữ liệu tổng thể của Data Warehouse 

- Tự tin hơn khi đặt câu hỏi truy vấn hoặc yêu cầu AI viết SQL 

- Giảm phụ thuộc vào tài liệu kỹ thuật 



<!-- Start of picture text -->
doanh nghiép va hé tre trong viée ra quyét dinh dau tu hodc quan ly.<br>@ FinTech<br>ChatBot<br>Ut ké cic bang dt ibutrong db<br>1 Cicbing<br><dbo.dim account<br><dbo.dim account Jevel0T<br>dbo.dim account Jevel02<br>dbo dim account Jevelo3<br>‘dbo.dim<br><dbo.dimdbodim cfdatecompany item<br>dbo im kp<br><dbodim<br>dbo fact balancepol dict sheet<br>dbotact cashfow<br>dbo fact consolidated<br>dbo sysdiagrams<br><!-- End of picture text -->

_Hình 4. 26: Minh họa chatbot về bảng dữ liệu_ 



<!-- Start of picture text -->
Trong bang dbo factbalance_sheet c6 nhiing c6t nao<br>If Cac c6t trong dbo fact_balancesheet:<br>~ bs_sk: int NOT NULL<br>~ row_id: nvarchar(100) NULL<br>= account_nk: nvarchar(100) NULL<br>~ date_sk: int NULL<br>- end_value: decimal NULL<br>- begin value: decimal NULL<br>- created_date: datetime? NULL<br>- updated_at: datetime2 NULL<br>- is_delete: bit NOT NULL<br><!-- End of picture text -->

_Hình 4. 27: Minh họa chatbot về các cột dữ liệu trong bảng_ 

Trợ lý AI có thể tạo câu lệnh SQL theo yêu cầu và tự động vẽ các biểu đồ trực quan từ dữ liệu, giúp người dùng khai thác Data Warehouse một cách dễ dàng mà không cần kỹ năng kỹ thuật chuyên sâu. Thay vì phải viết truy vấn phức tạp hoặc xử lý dữ liệu thủ công, người dùng chỉ cần mô tả yêu cầu bằng ngôn ngữ tự nhiên, mọi phần còn lại sẽ được AI thực hiện tự động. Nhờ khả năng này, mọi 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

89 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

phòng ban trong doanh nghiệp bao gồm kinh doanh, tài chính, kế toán, vận hành… đều có thể chủ động truy vấn và phân tích dữ liệu từ Data Warehouse bất cứ khi nào cần. 



_<mark>Hình 4. 29: Minh họa cahtbot yêu cầu tạo câu truy vấn</mark>_ 



_<mark>Hình 4. 28: Minh họa chatbot vẽ biểu đồ</mark>_ 

Giống như các Chatbot AI thông minh phổ biến hiện nay, hệ thống Trợ lý AI trong giải pháp này không giới hạn người dùng chỉ trong phạm vi dữ liệu của Data Warehouse. Người dùng có thể đặt bất kỳ câu hỏi nào thuộc mọi lĩnh vực, từ kiến 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

90 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

thức tổng quát, nghiệp vụ tài chính - ngân hàng, công nghệ, cho đến các vấn đề đời sống thường ngày. 

Ví dụ người dùng có thể hỏi: 

- “Giải thích giúp tôi sự khác nhau giữa lãi đơn và lãi kép?” 

- “Hướng dẫn cài Python trên Windows?” 

- “Tóm tắt báo cáo tài chính là gì?” 

- “Viết giúp tôi đoạn mô tả công việc vị trí Data Analyst.” 



<!-- Start of picture text -->
tata<br>Powecing cing ce<br>Ic rt hp bn 6<br>cha<br>Srvc. Ngst cnahingt=ch Pomr geBho pip ng hing ha bo cho dsb v8 ng mip hak i thng gn ower<br>i ln BW hgne<br><!-- End of picture text -->

_Hình 4. 30: Minh họa chatbot trợ lý AI_ 

Nhờ tích hợp nền tảng ChatGPT, chatbot có khả năng: 

- Hiểu ngôn ngữ tự nhiên giống hệt một cuộc trò chuyện giữa hai người. 

- Phân tích ngữ cảnh câu hỏi, kể cả khi câu hỏi không liên quan đến cơ sở dữ liệu. 

- Trả lời như một chatbot AI tổng quát, bao gồm giải thích khái niệm, hướng dẫn kỹ thuật, cung cấp công thức, tóm tắt tài liệu, hỗ trợ tính toán logic. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

91 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

### **4.4. Tự động cập nhật dữ liệu và gửi báo cáo trên Power Platform** 

- Triển khai báo cáo dashboard lên PowerBI service: 

Sau khi hoàn thiện báo cáo trên Power BI Desktop, bước tiếp theo là triển khai lên Power BI Service để người dùng nội bộ có thể truy cập trực tuyến, chia sẻ, và làm việc cộng tác. Quy trình triển khai giúp đưa toàn bộ dataset, dữ liệu mô hình, và dashboard lên môi trường cloud của Microsoft. 



<!-- Start of picture text -->
a Workspacet @ 8cmtetetepemtypsinn CB Grmtegy SB Mewes) Wenger stings<br>fo} .<br>5«<br>Choose from predesigned task flows or add a task to build one<br>a<br>2 sansa<br>J<br><!-- End of picture text -->

_<mark>Hình 4. 31: Dashboard và dữ liệu trong worksapce PowerBi service</mark>_ 

Việc triển khai lên Power BI Service báo cáo được truy cập mọi lúc mọi nơi, đảm bảo tính minh bạch và kịp thời trong việc ra quyết định. Đây là bước quan trọng trong quá trình đưa giải pháp phân tích dữ liệu vào vận hành thực tế trong 

doanh nghiệp. 



<!-- Start of picture text -->
Brae Die» ryt » ef shar | m Bolo & Suteobe 0 Setdet © Mentor | 7 Eat o-a 2<br>eee B Iencase ogee ee<br>©, [recent =} | nen ==<br>- 5 a Be<br>ic —f - ee<br>. = | milli... |< poe<br>= 2 am memee sceteeonsetee SE Se as<br>rn =<<br>i = :<br><!-- End of picture text -->

_<mark>Hình 4. 32: Báo cáo được đẩy lên môi trường service</mark>_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

92 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

- Cập nhật dữ liệu lên báo cáo: 

Trong hệ thống Data Warehouse, việc làm mới dữ liệu và gửi báo cáo định kỳ là rất quan trọng để đảm bảo thông tin luôn cập nhật, hỗ trợ quá trình phân tích và ra quyết định của doanh nghiệp. Để tự động hóa hai bước này, chúng ta sẽ thiết lập một luồng tự động trong Power Apps với mục đích: 

Tự động làm mới dữ liệu cho các báo cáo hoặc dataset trên Power BI Service theo lịch định sẵn. Việc này giúp hệ thống luôn đảm bảo dữ liệu báo cáo được đồng bộ mới nhất từ kho dữ liệu mà không cần thao tác thủ công. 

Gửi email thông báo kết quả Refresh, bao gồm trạng thái thành công hoặc thất bại, kèm ngày giờ thực hiện cụ thể. Thông tin này được gửi tự động tới nhóm phụ trách hoặc người quản trị hệ thống để theo dõi và xử lý kịp thời nếu có lỗi xảy ra trong quá trình làm mới dữ liệu. 

Việc áp dụng luồng tự động này giúp giảm thiểu rủi ro do thao tác thủ công, tiết kiệm thời gian vận hành, đồng thời tăng tính ổn định và tính sẵn sàng của hệ thống báo cáo Power BI. 



<!-- Start of picture text -->
am oa—<br>B Apps Vv<br>B wbies Z<br>poner Paio<br><!-- End of picture text -->

_Hình 4. 33: Luồng resfresh dữ liệu trên PowerApps_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

93 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Sau khi cập nhật dữ liệu theo lịch đã được thiết lập thành công thì hệ thống sẽ gửi về mail đã cập nhật thành công: 



<!-- Start of picture text -->
«+ 808 SB: 110 5 > @-<br>Power BI Refresh Succeeded 04/11/2025 20:23 Hep huraéa x ea<br>a NGUYEN QUANG BAC 3 * Oa:<br><!-- End of picture text -->

_Hình 4. 34: Thông báo được gửi khi cập nhật thành công_ 

- Gửi báo cáo tự động 

Flow sẽ được cấu hình tính năng tự động để gửi báo cáo Power BI định kỳ qua email. Khi đến lịch, Power BI sẽ tự động làm mới dữ liệu, xuất báo cáo dưới dạng PDF và gửi trực tiếp đến email của người nhận đã đăng ký. 

Flow này giúp bạn tự động hóa quy trình xuất báo cáo Power BI định kỳ, thông báo kết quả qua email, đồng thời lưu trữ bản báo cáo PDF vào OneDrive cá nhân. Đây là một bước quan trọng trong hành trình nâng cao hiệu suất làm việc và giảm thao tác thủ công. 



<!-- Start of picture text -->
Power Piatto o_""<br><!-- End of picture text -->

_Hình 4. 35: Cấu hình lập lịch cho việc gửi báo cáo_ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

94 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Báo cáo sau khi được tạo sẽ được tự động chuyển đổi sang định dạng PDF để đảm bảo tính ổn định và dễ dàng chia sẻ. File PDF này sẽ được gửi kèm qua email đến các nhóm người dùng đã được cấu hình sẵn, đúng theo lịch chạy định kỳ đã thiết lập. Nhờ đó, người dùng luôn nhận được báo cáo kịp thời mà không cần thao tác thủ công.: 



<!-- Start of picture text -->
« @O8 SB: 1 tong ‘ > @-<br>PowerBlExportSuccess—04/11/2025 22:08 Hopthuaénx ea<br>[o) NGUYEN QUANG BAC in *v* On:<br>Mét tép dinh kém + Do Gmail quét © @ Thém vao Drive<br><!-- End of picture text -->

_Hình 4. 36: Báo cáo được gửi tự động qua email_ 

Hệ thống cung cấp một giao diện quản lý luồng chạy trực quan, giúp người quản trị dễ dàng giám sát, kiểm tra và đánh giá hiệu suất của các flow đang được sử dụng trong Power Apps hoặc Power Automate. 



_<mark>Hình 4. 37: Lịch sử luồng chạy tự động</mark>_ 

Việc đẩy báo cáo lên Power BI Service giúp báo cáo được quản lý tập trung trong workspace, đảm bảo người dùng có thể truy cập đúng nơi và đúng quyền. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

95 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

Sau khi triển khai, hệ thống cần được thiết lập lịch làm mới dữ liệu để báo cáo luôn cập nhật theo thời định kỳ được thiết lập, đồng thời đảm bảo gateway và nguồn dữ liệu hoạt động ổn định. Cuối cùng, tính năng gửi báo cáo tự động qua email giúp người dùng nhận báo cáo định kỳ mà không cần truy cập thủ công, miễn là họ có quyền xem báo cáo. Nhờ đó, toàn bộ quy trình vận hành báo cáo trở nên tự động, nhất quán và thuận tiện hơn cho người dùng. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

96 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **KẾT LUẬN** 

Trong đồ án “ **Xây dựng mô hình Data warehouse và ứng dụng phân tích dữ liệu tài chính trên nền tảng Power BI** ”, em đã nghiên cứu và ứng dụng các kiến thức đã học để xây dựng một hệ thống kho dữ liệu ứng dụng cho việc tổng hợp, phân tích và trực quan hóa thông tin tài chính, qua đó hoàn thành được các mục tiêu đã đặt ra cho đồ án. 

**1. Kết quả đạt được:** 

   - Nghiên cứu cơ sở lý thuyết về Data Warehouse, bao gồm kiến trúc, mô hình dữ liệu, các phương pháp lưu trữ và kỹ thuật phân tích trong lĩnh vực tài chính; đồng thời tìm hiểu các khái niệm, chỉ tiêu và cấu trúc của các báo cáo tài chính như báo cáo kết quả kinh doanh, bảng cân đối kế toán, báo cáo lưu chuyển tiền tệ để đảm bảo việc thiết kế mô hình dữ liệu phù hợp và phản ánh đúng nghiệp vụ thực tế. 

   - Thiết kế mô hình Data Warehouse theo cấu trúc Fact - Dimension trong mô hình Snowflake, đảm bảo đúng chuẩn mô hình phân tích, tối ưu hóa cho các truy vấn tổng hợp dữ liệu tài chính và phục vụ báo cáo nhanh chóng, ổn định. 

   - Xây dựng quy trình ETL để thu thập, tích hợp và làm sạch dữ liệu từ nguồn đầu vào, đảm bảo dữ liệu được chuẩn hóa, đồng bộ và luôn sẵn sàng cho nhu cầu phân tích. 

   - Xây dựng báo cáo Power BI trực quan, thể hiện các chỉ số tài chính hỗ trợ người dùng nắm bắt nhanh tình hình hoạt động kinh doanh của doanh nghiệp. 

   - Triển khai báo cáo lên Power BI Service và xây dựng các luồng tự động trên nền tảng Power Platform, bao gồm làm mới dữ liệu định kỳ và gửi báo cáo qua email theo lịch. Nhờ đó, người dùng luôn nhận được thông tin cập nhật mới nhất mà không cần thực hiện bất kỳ thao tác thủ công nào. 

   - Xây dựng chatbot trợ lý AI tích hợp OpenAI, giúp người dùng truy vấn dữ liệu bằng ngôn ngữ tự nhiên, tự động sinh câu lệnh SQL, thông tin bảng dữ 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

97 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

liệu và biểu đồ trực quan, qua đó nâng cao khả năng khai thác kho dữ liệu một cách dễ dàng, linh hoạt. 

**2. Hướng phát triển trong tương lai:** 

   - Tích hợp thêm nhiều nguồn dữ liệu thực tế như hệ thống kế toán, ERP, CRM để phản ánh toàn diện hoạt động tài chính. 

   - Tối ưu hóa hiệu suất và thời gian xử lý dữ liệu, nâng cao tốc độ cập nhật báo cáo. 

   - Phát triển hệ thống Near Real-Time để hỗ trợ phân tích giao dịch phát sinh theo thời gian thực. 

   - Tăng cường bảo mật và kiểm soát chất lượng dữ liệu nhằm đảm bảo tính chính xác và an toàn. 

   - Mở rộng thêm khu vực Data Lake để lưu trữ dữ liệu đa dạng, phục vụ phân tích nâng cao và ứng dụng trí tuệ nhân tạo. 

Với những hướng phát triển này, hệ thống Data Warehouse có thể trở thành nền tảng dữ liệu chiến lược, giúp doanh nghiệp tài chính đưa ra quyết định nhanh chóng và hiệu quả hơn. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

98 

**_Đồ án tốt nghiệp ngành Công nghệ Thông tin_** 

## **TÀI LIỆU THAM KHẢO** 

**_Tài liệu tiếng Việt_** 

[1]. Đặng Hữu Nghị, Hoàng Kim Bảng, Bùi Thị Vân Anh (2011), Giáo trình Hệ quản trị cơ sở dữ liệu. Hà Nội, Knxb. 

[2]. Viện dầu khí Việt Nam (2023), “Sáng tạo sản phẩm số Ai cũng dùng AI Ứng dụng Power BI Service và AutoML trong lĩnh vực dầu khí, Nhà xuất bản thông tin và truyền thông. 

[3]. PGS.TS. Thân Quang Khoát PGS.TS. Nguyễn Thị Kim Anh TS. Đỗ Tiến Dũng TS. Ngô Văn Linh TS. Nguyễn Đức Anh (2024), Nhập Môn Học Máy Và Khai Phá Dữ Liệu, Khoa Khoa Học Máy Tính Đại học Bách Khoa Hà Nội. 

**_Tài liệu tiếng Anh_** 

[4]. Jesús Rogel-Salazar (2023), “An overview of evolutionary algorithms for parameter optimization”, Chapman & Hall/CRC, Taylor & Francis Group, LLC. **_Tài liệu từ Internet_** 

[5]. “Tổng hợp tài liệu tự học Power BI 2024”, https://datapot.vn/tong-hop-tai <u>lieu-tu-hoc-power-bi-2024/.</u> 

[6] “SQL Query Optimization: 15 Techniques for Better Performance”, https://www.datacamp.com/blog/sql-query-optimization. 

_Nguyễn Quang Bắc – 212105142 – DCCTCT66_07C_ 

99 

