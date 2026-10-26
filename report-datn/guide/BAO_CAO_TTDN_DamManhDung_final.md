**<mark>BỘ GIÁO DỤC VÀ ĐÀO TẠO</mark> TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT** 

ĐÀM MẠNH DŨNG 2221050359 

# **BÁO CÁO THỰC TẬP DOANH NGHIỆP** 

NGÀNH CÔNG NGHỆ THÔNG TIN CHUYÊN NGÀNH HỆ THỐNG THÔNG TIN 

**THIẾT KẾ VÀ KHAI TRIỂN HỆ THỐNG CHATBOT TÌM KIẾM NGỮ NGHĨA TÀI LIỆU NỘI BỘ DOANH NGHIỆP DỰA TRÊN KIẾN TRÚC RAG VÀ MÔ HÌNH NGÔN NGỮ LỚN** 

**HÀ NỘI, 05/2026** 

### **BỘ GIÁO DỤC VÀ ĐÀO TẠO TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT** 

# **BÁO CÁO THỰC TẬP DOANH NGHIỆP** 

NGÀNH CÔNG NGHỆ THÔNG TIN 

CHUYÊN NGÀNH HỆ THỐNG THÔNG TIN 

**THIẾT KẾ VÀ KHAI TRIỂN HỆ THỐNG CHATBOT TÌM KIẾM NGỮ NGHĨA TÀI LIỆU NỘI BỘ DOANH NGHIỆP DỰA TRÊN KIẾN TRÚC RAG VÀ MÔ HÌNH NGÔN NGỮ LỚN** 

**Sinh viên thực tập :     Đàm Mạnh Dũng Mã sinh viên :     2221050459 Công ty thực tập :     DC-STRUCTURES VIETNAM Người phụ trách :     Ngô Quang Đại** 

**Giảng viên hướng dẫn :     Vũ Lan Phương** 

**HÀ NỘI, 05/2026** 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **LỜI CẢM ƠN** 

Em xin gửi lời cảm ơn cô **Vũ Lan Phương** – giảng viên khoa Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất, người đã trực tiếp hướng dẫn và định hướng em trong suốt quá trình thực hiện báo cáo thực tập doanh nghiệp. Những đóng góp quý báu của cô về mặt chuyên môn, phương pháp nghiên cứu và xây dựng hệ thống đã giúp em tiếp cận đề tài một cách logic, khoa học và hiệu quả hơn, đồng thời hoàn thiện được sản phẩm mang tính ứng dụng thực tiễn trong môi trường doanh nghiệp. 

Em cũng xin gửi lời cảm ơn chân thành tới các thầy cô trong khoa Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất đã giúp đỡ em trong quá trình học tập, nghiên cứu và hoàn thiện báo cáo thực tập doanh nghiệp. 

Và cuối cùng, em xin cảm ơn Ban lãnh đạo cùng các anh chị nhân viên tại Công ty TNHH DC-STRUCTURES VIETNAM, đặc biệt là anh **Ngô Quang Đại** – Giám đốc công ty, đã góp công rất lớn đối với em trong quá trình thực tập tại doanh nghiệp. Đồng thời hỗ trợ em trong quá trình tìm hiểu quy trình phát triển phần mềm, triển khai hệ thống chatbot tìm kiếm ngữ nghĩa tài liệu nội bộ doanh nghiệp dựa trên kiến trúc RAG và mô hình ngôn ngữ lớn, cũng như giúp em tích lũy thêm nhiều kinh nghiệm thực tế trong môi trường làm việc chuyên nghiệp. 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_1_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **LỜI MỞ ĐẦU** 

Trong bối cảnh chuyển đổi số đang diễn ra mạnh mẽ trên phạm vi toàn cầu, nhu cầu ứng dụng công nghệ thông tin vào hoạt động quản lý, vận hành và khai thác dữ liệu trong doanh nghiệp ngày càng trở nên cấp thiết. Đặc biệt, sự phát triển nhanh chóng của trí tuệ nhân tạo (Artificial Intelligence – AI) và các mô hình ngôn ngữ lớn (Large Language Model – LLM) đã mở ra nhiều hướng tiếp cận mới trong việc xây dựng các hệ thống hỗ trợ tra cứu, phân tích và xử lý thông tin một cách thông minh và hiệu quả hơn. Bên cạnh đó, các công nghệ phát triển ứng dụng hiện đại như Next.js, NestJS cùng kiến trúc Retrieval-Augmented Generation (RAG) đang được nhiều doanh nghiệp lựa chọn nhằm xây dựng các hệ thống phần mềm có khả năng mở rộng, tối ưu hiệu năng và khai thác dữ liệu nội bộ hiệu quả. 

Thực tập tốt nghiệp là một hoạt động có ý nghĩa quan trọng đối với sinh viên ngành Công nghệ thông tin, giúp gắn kết giữa kiến thức lý thuyết đã được học tại nhà trường với môi trường làm việc thực tế tại doanh nghiệp. Đây không chỉ là cơ hội để sinh viên tiếp cận với quy trình phát triển phần mềm chuyên nghiệp mà còn là điều kiện để rèn luyện kỹ năng chuyên môn, kỹ năng làm việc nhóm, tư duy giải quyết vấn đề và khả năng thích nghi với môi trường công nghệ hiện đại. 

Với mong muốn được học hỏi, trải nghiệm và nâng cao năng lực chuyên môn trong lĩnh vực phát triển phần mềm và trí tuệ nhân tạo, em đã lựa chọn thực tập tại Công ty TNHH DC-STRUCTURES VIETNAM. Trong thời gian thực tập, em được tham gia tìm hiểu và hỗ trợ xây dựng hệ thống chatbot tìm kiếm ngữ nghĩa tài liệu nội bộ doanh nghiệp dựa trên kiến trúc RAG kết hợp mô hình ngôn ngữ lớn. Quá trình thực hiện giúp em có cơ hội tiếp cận thực tế với quy trình phát triển một ứng dụng fullstack hiện đại, từ xây dựng giao diện người dùng, phát triển hệ thống backend đến tích hợp AI nhằm nâng cao khả năng tra cứu và xử lý thông tin trong doanh nghiệp. 

Báo cáo thực tập này được thực hiện nhằm tổng hợp những kiến thức, kỹ năng và kinh nghiệm mà em tích lũy được trong quá trình thực tập tại doanh nghiệp. Đồng thời, báo cáo cũng thể hiện tinh thần học hỏi, thái độ làm việc nghiêm túc và những kết quả đạt được trong suốt kỳ thực tập. 

_Đàm Mạnh Dũng_ 

_2 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **MỤC LỤC** 

|**LỜI CẢM ƠN.......................................................................................................1**|
|---|
|**LỜI MỞ ĐẦU.......................................................................................................2**|
|**DANH MỤC TỪ VIẾT TẮT...............................................................................7**|
|**CHƯƠNG 1: GIỚI THIỆU CÔNG TY VÀ ĐỀ TÀI THỰC TẬP..................8**|
|1.1. Giới thiệu công ty DC-STRUCTURES VIETNAM...................................8<br>|
|1.1.1. Lịch sử hình thành và phát triển...........................................................8|
|1.1.2. Lĩnh vực hoạt động và sản phẩm chính................................................8|
|1.1.3. Bảng thông tin tổng quan.....................................................................8|
|1.1.4. Sơ đồ tổ chức........................................................................................9|
|1.1.5. Môi trường và văn hóa làm việc.........................................................10|
|1.2. Vị trí thực tập.............................................................................................10|
|1.2.1. Mô tả vị trí Fullstack Developer Intern..............................................10|
|1.2.2. Môi trường làm việc và team structure...............................................10|
|1.2.3. Công việc ngay tuần đầu....................................................................11|
|1.3. Đề tài thực tập............................................................................................11|
|1.3.1. Tên đầy đủ và lý do được giao...........................................................11|
|1.3.2. Mục tiêu đề tài và yêu cầu đầu ra.......................................................11|
|1.3.3. Phạm vi kỹ thuật.................................................................................12|
|1.4. Kế hoạch và lịch làm việc..........................................................................12|
|1.4.1. Tổng kết tiến độ..................................................................................14|
|1.4.2. Công cụ và môi trường làm việc........................................................14|
|**CHƯƠNG 2: NỘI DUNG THỰC TẬP............................................................16**|
|2.1. Tổng quan hệ thống...................................................................................16|
|2.1.1. Mô tả bài toán và yêu cầu nghiệp vụ..................................................16|
|2.1.2. Kiến trúc tổng thể hệ thống................................................................16|
|2.1.3. Lý do lựa chọn công nghệ..................................................................17|
|2.2. Frontend Next.js 14...................................................................................18|
|2.2.1. App Router vs Pages Router. Lý do chọn App Router.......................18|
|2.2.3. Flowchart luồng điều hướng trang.....................................................20|
|2.2.4. React Query: Fetching, Caching, Mutation........................................21|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_3_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|2.2.5. Shadcn/UI và TailwindCSS Design System.......................................26|
|---|
|2.2.6. Danh sách trang và route....................................................................27|
|2.3. Backend NestJS.........................................................................................28|
|2.3.1. Kiến trúc Module/Controller/Service/Repository..............................28|
|2.3.2. Danh sách REST API Endpoints........................................................29|
|2.3.3. JWT Authentication Flow..................................................................31|
|2.3.4. Entity Relationship Diagram..............................................................31|
|2.3.5. Sequence Diagram Đăng Nhập..........................................................32|
|2.3.6. Prisma ORM  Schema và Migrations.................................................33|
|2.4. AI Chatbot RAG & LLM..........................................................................41|
|2.4.1. So sánh RAG vs Fine-tuning vs Prompt-only....................................41|
|2.4.2. RAG Pipeline......................................................................................41|
|2.4.3. Vector Database và Embedding.........................................................42|
|2.4.4. Prompt Engineering............................................................................48|
|2.4.5. Sequence Diagram Chatbot................................................................51|
|2.4.6. Đánh giá chất lượng Chatbot..............................................................51|
|2.5. Quy trình phát triển....................................................................................53|
|2.5.1. Git Workflow......................................................................................53|
|2.5.2. Docker Containerization.....................................................................53|
|2.5.3. CI/CD với GitHub Actions.................................................................57|
|**CHƯƠNG 3: ĐÁNH GIÁ KẾT QUẢ VÀ ĐỊNH HƯỚNG PHÁT TRIỂN. .64**|
|3.1. Đánh giá kết quả thực tập..........................................................................64|
|3.1.1. Kiến thức từ trường đại học áp dụng được.........................................64|
|3.1.2. Kiến thức mới tiếp cận tại công ty......................................................65|
|3.1.3. Kỹ năng đạt được................................................................................67|
|3.1.4. Tự đánh giá.........................................................................................68|
|3.2. Định hướng phát triển................................................................................70|
|3.2.1. Hướng phát triển đề tài.......................................................................70|
|3.2.2. Liên kết với Đồ án tốt nghiệp.............................................................72|
|**KẾT LUẬN.........................................................................................................74**|
|**TÀI LIỆU THAM KHẢO..................................................................................75**|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_4_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **DANH MỤC HÌNH ẢNH** 

|Hình 1- 1 Sơ đồ tổ chức công ty DC-STRUCTURES VIETNAM......................13|
|---|
|Hình 2- 1 Kiến trúc tổng thể hệ thống<br>20|
|Hình 2- 2 Flowchart luồng điều hướng trang frontend.........................................25|
|Hình 2- 3 ERD (Entity Relationship Diagram)....................................................36|
|Hình 2- 4 Sequence diagram luồng đăng nhập JWT............................................37|
|Hình 2- 5 RAG Pipeline đầy đủ............................................................................46|
|Hình 2- 6 Sequence diagram luồng chatbot..........................................................55|
|Hình 2- 7 Git Workflow.......................................................................................57|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_5_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **DANH MỤC BẢNG BIỂU** 

|Bảng 1- 1 Thông tin tổng quan công ty DC-STRUCTURES VIETNAM...........12|
|---|
|Bảng 1- 2 Kế hoạch thực tập 10 tuần (02/03/2026 → 11/05/2026).....................17|
|Bảng 2- 1 So sánh và lý do lựa chọn công nghệ21|
|Bảng 2- 2 Danh sách các trang chính, route và mô tả..........................................31|
|Bảng 2- 3 Danh sách REST API endpoints..........................................................34|
|Bảng 2- 4 So sánh các phương pháp tích hợp LLM vào ứng dụng......................45|
|Bảng 2- 5 Kết quả đánh giá chatbot theo test cases..............................................55|
|Bảng 3- 1 Kiến thức từ trường áp dụng vào thực tập<br>68|
|Bảng 3- 2 Kỹ năng cứng và kỹ năng mềm mức độ trước và sau thực tập............71|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_6_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **DANH MỤC TỪ VIẾT TẮT** 

|**Từ viết tắt**|**Tiếng Anh**|**Tiếng Việt**|
|---|---|---|
|**AI**|Artificial Intelligence|Trí tuệ nhân tạo|
|**API**|Application Programming Interface|Giao diện lập trình ứng dụng|
|**CDN**|Content Delivery Network|Mạng phân phối nội dung|
|**CI/CD**|Continuous Integration /<br>Continuous Deployment|Tích hợp liên tục / Triển khai<br>liên tục|
|**DB**|Database|Cơ sở dữ liệu|
|**JWT**|JSON Web Token|Mã thông báo xác thực JSON|
|**LLM**|Large Language Model|Mô hình ngôn ngữ lớn|
|**ORM**|Object-Relational Mapping|Ánh xạ đối tượng quan hệ|
|**RAG**|Retrieval-Augmented Generation|Sinh văn bản tăng cường truy<br>xuất|
|**REST**|Representational State Transfer|Kiến trúc truyền trạng thái đại<br>diện|
|**SDK**|Software Development Kit|Bộ công cụ phát triển phần<br>mềm|
|**UI**|User Interface|Giao diện người dùng|
|**UX**|User Experience|Trải nghiệm người dùng|
|**SSR**|Server-Side Rendering|Kết xuất phía máy chủ|
|**CSR**|Client-Side Rendering|Kết xuất phía máy khách|
|**DI**|Dependency Injection|Tiêm phụ thuộc|
|**IoC**|Inversion of Control|Đảo ngược quyền kiểm soát|
|**ERD**|Entity Relationship Diagram|Sơ đồ quan hệ thực thể|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_7_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **CHƯƠNG 1: GIỚI THIỆU CÔNG TY VÀ ĐỀ TÀI THỰC TẬP** 

### **1.1. Giới thiệu công ty DC-STRUCTURES VIETNAM** 

### **_1.1.1. Lịch sử hình thành và phát triển_** 

Công ty TNHH DC-STRUCTURES VIETNAM được thành lập với sứ mệnh cung cấp các giải pháp công nghệ số toàn diện cho doanh nghiệp Việt Nam trong bối cảnh chuyển đổi số diễn ra mạnh mẽ. Từ những ngày đầu hoạt động với quy mô nhỏ, DC-STRUCTURES VIETNAM đã không ngừng mở rộng năng lực kỹ thuật và đội ngũ nhân sự, hướng tới trở thành đơn vị phát triển phần mềm chuyên nghiệp với năng lực cạnh tranh trong khu vực. 

Dưới sự dẫn dắt của Giám đốc Ngô Quang Đại  một kỹ sư phần mềm có nhiều năm kinh nghiệm trong lĩnh vực phát triển ứng dụng web và mobile  công ty tập trung vào việc xây dựng văn hóa kỹ thuật chất lượng cao, khuyến khích áp dụng các công nghệ tiên tiến nhất trong từng sản phẩm. Triết lý hoạt động của DCSTRUCTURES VIETNAM là "Build to Last"  xây dựng phần mềm bền vững, có thể mở rộng và bảo trì lâu dài. 

### **_1.1.2. Lĩnh vực hoạt động và sản phẩm chính_** 

DC-STRUCTURES VIETNAM hoạt động chủ yếu trong hai lĩnh vực: 

Phát triển phần mềm theo yêu cầu (Custom Software Development): Thiết kế và xây dựng ứng dụng web, mobile và hệ thống backend theo đặc thù nghiệp vụ của từng khách hàng. Công ty có thế mạnh trong việc phát triển các nền tảng SaaS, hệ thống quản lý doanh nghiệp (ERP nhẹ) và ứng dụng kết hợp AI. 

Tích hợp AI và tự động hóa: Tư vấn và triển khai các giải pháp AI cho doanh nghiệp, bao gồm chatbot thông minh, hệ thống phân tích dữ liệu và tự động hóa quy trình kinh doanh (RPA). 

### **_1.1.3. Bảng thông tin tổng quan_** 

_Bảng 1- 1 Thông tin tổng quan công ty DC-STRUCTURES VIETNAM_ 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_8_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|**Thông tin**|**Chi tiết**|
|---|---|
|Tên đầy đủ|Công ty TNHH DC-STRUCTURES<br>VIETNAM|
|Loại hình|Công ty TNHH|
|Lĩnh vực|Phát triển phần mềm, Tích hợp AI, Tư<br>vấn công nghệ|
|Người đại diện|Ngô Quang Đại (Giám đốc)|
|Địa chỉ|Hà Nội, Việt Nam|
|Quy mô nhân sự|10–30 người|
|Công nghệ chính|Next.js, NestJS, React Native, Python,<br>AI/ML|
|Năm hoạt động|2020 đến nay|
|Định hướng|Phát triển bền vững, chất lượng kỹ thuật<br>cao|



### **_1.1.4. Sơ đồ tổ chức_** 



<!-- Start of picture text -->
& Giam ddc\nNg6 Quang<br>_- Bai<br>r<br>+ ,<br>(1 Project tt Tech Leadin(Truéng ee an<br>* HO Ti,<br>Managerin(Quan fy dy én) _| nihém ky thud) — Cai k i nh doanh)e<br>+ ae ¢ ¥ Y<br>@ FrontendReactTeaminNext js ‘\ Backend1 PythonTeam\nNestJS TeaminLangChain@AUML / Opendl of DevOpsinDockerGithub Actions /<br>® Intem FE\n(DAm Manh ® Intern BEWN(Dam Manh<br>Dang) ang)<br><!-- End of picture text -->

_Hình 1- 1 Sơ đồ tổ chức công ty DC-STRUCTURES VIETNAM_ 

**Ghi chú** : Đàm Mạnh Dũng đảm nhận vị trí Fullstack Intern, tham gia cả Frontend và Backend team dưới sự hướng dẫn trực tiếp của Tech Lead và Giám đốc. 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_9_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

### **_1.1.5. Môi trường và văn hóa làm việc_** 

DC-STRUCTURES VIETNAM áp dụng mô hình làm việc Agile Scrum với các sprint 2 tuần. Văn hóa công ty đề cao sự minh bạch trong giao tiếp, review code nghiêm túc và học hỏi liên tục. Mỗi thành viên được khuyến khích chủ động đề xuất cải tiến kỹ thuật và chia sẻ kiến thức trong team. Công cụ cộng tác gồm Slack (giao tiếp), GitHub (quản lý code), Notion (tài liệu) và Figma (thiết kế UI). 

### **1.2. Vị trí thực tập** 

### **_1.2.1. Mô tả vị trí Fullstack Developer Intern_** 

Vị trí Fullstack Developer Intern tại DC-STRUCTURES VIETNAM là vị trí thực tập kỹ thuật đòi hỏi người học có nền tảng lập trình vững chắc và khả năng tự học nhanh. Intern được kỳ vọng không chỉ hoàn thành các task được giao mà còn chủ động hiểu bức tranh lớn của sản phẩm, đóng góp ý kiến trong các buổi planning và review. 

_Trách nhiệm chính:_ 

- Phát triển tính năng mới cho ứng dụng web (frontend + backend) 

- Viết unit test và integration test cho code mình phát triển 

- Tham gia code review, nhận và đưa ra phản hồi có chất lượng 

- Tài liệu hóa API và các component quan trọng 

- Cộng tác với AI team trong việc tích hợp RAG chatbot vào ứng dụng chính 

_Yêu cầu kỹ thuật:_ 

- TypeScript/JavaScript thành thạo 

- Hiểu biết về React và kiến trúc component-based 

- Nền tảng về RESTful API và HTTP protocol 

- Quen thuộc với Git và workflow cơ bản 

### **_1.2.2. Môi trường làm việc và team structure_** 

Intern làm việc trong team phát triển gồm 6 thành viên: 1 Tech Lead, 2 Senior Fullstack Developer, 1 AI Engineer, 1 DevOps Engineer và 1 Intern (tác giả báo 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_10_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

cáo này). Team họp daily stand-up lúc 9h30 sáng mỗi ngày làm việc, mỗi sprint 2 tuần có sprint planning và sprint review. Mọi code change đều phải qua pull request và được approve bởi ít nhất 1 senior developer trước khi merge. 

### **_1.2.3. Công việc ngay tuần đầu_** 

Tuần đầu tiên tập trung vào onboarding và làm quen với codebase. Em được giao: 

- Clone toàn bộ monorepo và cài đặt môi trường development local (Next.js frontend + NestJS backend + PostgreSQL + Redis) 

- Đọc và hiểu kiến trúc tổng thể qua README và ADR (Architecture Decision Records) trên Notion 

   - Chạy thử toàn bộ test suite để hiểu coverage hiện tại 

- Fix một số bug nhỏ để làm quen với workflow: create branch → code → 

- test → PR → review → merge 

- Tham gia pair programming với Senior Developer để hiểu coding conventions của team 

### **1.3. Đề tài thực tập** 

### **_1.3.1. Tên đầy đủ và lý do được giao_** 

Tên đề tài: **Thiết kế và triển khai hệ thống chatbot tìm kiếm ngữ nghĩa tài liệu nội bộ doanh nghiệp dựa trên kiến trúc RAG và mô hình ngôn ngữ lớn** . 

Đề tài này xuất phát từ nhu cầu thực tế của DC-STRUCTURES VIETNAM trong việc xây dựng một nền tảng internal tool giúp nhân viên tra cứu thông tin tài liệu kỹ thuật nội bộ một cách nhanh chóng và chính xác. Trước đây, việc tìm kiếm thông tin trong các tài liệu specification, meeting notes và wiki nội bộ mất nhiều thời gian. Ban lãnh đạo công ty quyết định xây dựng một AI chatbot tích hợp với toàn bộ knowledge base của công ty, đồng thời đây cũng là cơ hội để em được làm việc thực tế với stack công nghệ hiện đại nhất. 

### **_1.3.2. Mục tiêu đề tài và yêu cầu đầu ra_** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_11_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

### **_Mục tiêu kỹ thuật_** 

1. Xây dựng ứng dụng web hoàn chỉnh với giao diện người dùng hiện đại, 

trực quan 

   2. Phát triển backend API bảo mật, hiệu năng cao với khả năng xử lý đồng 

thời 

3. Tích hợp hệ thống RAG cho phép chatbot trả lời dựa trên tài liệu nội bộ 

4. Đảm bảo toàn bộ hệ thống có thể triển khai dễ dàng qua Docker **_Yêu cầu đầu ra cụ thể_** 

- Ứng dụng web chạy ổn định với ít nhất 10 trang chức năng 

- Tối thiểu 20 REST API endpoints có tài liệu đầy đủ 

- Chatbot có thể trả lời câu hỏi từ 100+ trang tài liệu nội bộ với độ chính 

xác ≥ 80% 

- Docker Compose file có thể khởi động toàn bộ stack bằng 1 lệnh 

- Codebase đạt test coverage ≥ 70% 

### **_1.3.3. Phạm vi kỹ thuật_** 

Đề tài bao gồm các thành phần kỹ thuật sau: 

|**Thành phần**|**Công nghệ**|**Mô tả**|
|---|---|---|
|**Frontend**|Next.js 14, TypeScript,<br>TailwindCSS, Shadcn/UI,<br>React Query|Giao diện người dùng<br>responsive|
|**Backend API**|NestJS, TypeScript,<br>Prisma, PostgreSQL, Redis|REST API, xác thực, quản lý<br>dữ liệu|
|**AI Service**|Python, LangChain,<br>ChromaDB, OpenAI API|RAG pipeline, embedding,<br>chatbot|
|**Infrastructure**|Docker, GitHub Actions,<br>Git|Containerization, CI/CD|



### **1.4. Kế hoạch và lịch làm việc** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_12_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

_Bảng 1- 2 Kế hoạch thực tập 10 tuần (02/03/2026 → 11/05/2026)_ 

|**Tuần**|**Thời gian**|**Nội dung công việc**|**Người**<br>**HD**|**Mức độ**<br>**hoàn**<br>**thành**|**Ghi chú**|
|---|---|---|---|---|---|
|1|02/03 –<br>06/03/2026|Onboarding: đọc codebase,<br>setup môi trường local<br>(Node.js, PostgreSQL, Redis,<br>Python), làm quen quy trình<br>Git/PR|Ngô<br>Quang<br>Đại|100%|Clone<br>repo, fix<br>2 bug nhỏ|
|2|09/03 –<br>13/03/2026|Nghiên cứu kiến trúc dự án:<br>Next.js App Router, NestJS<br>module system, ERD<br>database; Viết test cho<br>module User có sẵn|Ngô<br>Quang<br>Đại|100%|Tăng<br>coverage<br>từ 55%<br>lên 68%|
|3|16/03 –<br>20/03/2026|Frontend: xây dựng layout<br>chính, navigation,<br>authentication pages<br>(Login/Register/Logout) với<br>NextAuth integration|Ngô<br>Quang<br>Đại|100%|3 PR<br>merged|
|4|23/03 –<br>27/03/2026|Frontend: Dashboard page,<br>Document list page,<br>Document detail page; Tích<br>hợp React Query cho data<br>fetching|Ngô<br>Quang<br>Đại|100%|Custom<br>hooks<br>viết lại 2<br>lần theo<br>review|
|5|30/03 –<br>03/04/2026|Backend: NestJS Document<br>module (CRUD), Prisma<br>schema mở rộng, API<br>endpoints cho Document<br>management|Ngô<br>Quang<br>Đại|100%|5<br>endpoints<br>+ unit<br>tests|
|6|06/04 –<br>10/04/2026|Backend: Chat module,<br>Session management, JWT<br>refresh token, Redis caching|Ngô<br>Quang<br>Đại|100%|Fix<br>security<br>issue<br>trong|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_13_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|||cho session|||JWT<br>middlewa<br>re|
|---|---|---|---|---|---|
|7|13/04 –<br>17/04/2026|AI/RAG: Xây dựng document<br>ingestion pipeline (Python),<br>ChromaDB setup, text<br>chunking + embedding với<br>OpenAI|Ngô<br>Quang<br>Đại|100%|Test với<br>50 trang<br>tài liệu|
|8|20/04 –<br>24/04/2026|AI/RAG: LangChain retrieval<br>chain, prompt engineering,<br>NestJS ↔ Python AI service<br>integration qua HTTP|Ngô<br>Quang<br>Đại|100%|Chatbot<br>đạt 82%<br>accuracy|
|9|27/04 –<br>01/05/2026|Testing toàn diện: integration<br>tests, E2E tests cơ bản,<br>performance profiling, bug<br>fixing|Ngô<br>Quang<br>Đại|95%|1 bug khó<br>vẫn đang<br>investigat<br>e|
|10|04/05 –<br>11/05/2026|Polish UI/UX, cập nhật<br>README và API docs,<br>Docker Compose final, demo<br>sản phẩm, viết báo cáo thực<br>tập|Ngô<br>Quang<br>Đại|100%|Demo<br>11/05,<br>bàn giao<br>codebase|



### **_1.4.1. Tổng kết tiến độ_** 

Trong 10 tuần thực tập, tiến độ tổng thể đạt 98% kế hoạch đề ra. Điểm trễ duy nhất là một bug liên quan đến race condition trong Redis session invalidation (tuần 9) mà sau đó đã được giải quyết vào đầu tuần 10 sau khi tham khảo ý kiến Senior Developer. Tất cả các mục tiêu kỹ thuật chính đều đạt hoặc vượt yêu cầu ban đầu, đặc biệt chatbot AI đạt độ chính xác 82%  vượt mục tiêu 80% đề ra. 

### **_1.4.2. Công cụ và môi trường làm việc_** 

Trong suốt quá trình thực tập, em sử dụng các công cụ sau: 

- IDE: Visual Studio Code với các extension TypeScript, ESLint, Prettier, 

- GitLens 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_14_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

- API Testing: Postman (manual testing) + Supertest (automated) 

- Database GUI: TablePlus cho PostgreSQL, Redis Insight cho Redis 

- Thiết kế: Figma (xem mockup từ designer) 

- Giao tiếp: Slack, Google Meet (daily stand-up, sprint ceremonies) 

- Quản lý task: GitHub Issues + GitHub Projects (Kanban board) 

- Tài liệu: Notion (ADR, API docs draft), Swagger UI (API docs chính thức) 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_15_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **CHƯƠNG 2: NỘI DUNG THỰC TẬP** 

### **2.1. Tổng quan hệ thống** 

### **_2.1.1. Mô tả bài toán và yêu cầu nghiệp vụ_** 

DC-STRUCTURES VIETNAM đặt ra bài toán thực tế: công ty tích lũy hàng trăm tài liệu kỹ thuật nội bộ (specification, ADR, API docs, meeting notes, onboarding guide) trên nhiều nền tảng khác nhau như Notion, Google Drive và GitHub Wiki. Khi một thành viên mới cần tìm thông tin về quyết định kiến trúc được đưa ra 6 tháng trước, họ phải tốn 20–30 phút đọc qua nhiều tài liệu. Giải pháp được đề xuất là xây dựng một unified internal knowledge platform với các chức năng: 

1. Document Management: Upload, phân loại và quản lý tài liệu nội bộ 

2. AI-powered Search: Tìm kiếm ngữ nghĩa thay vì keyword matching 

3. Conversational AI: Chatbot có thể trả lời câu hỏi phức tạp dựa trên nội dung tài liệu 

4. Access Control: Phân quyền truy cập tài liệu theo role (Admin, Member, Guest) 

5. Audit Trail: Theo dõi ai đã truy cập và đặt câu hỏi gì 

Hệ thống cần xử lý được khoảng 500–1000 tài liệu, phục vụ đồng thời 20 – 30 người dùng nội bộ và có thời gian phản hồi chatbot < 5 giây. 

### **_2.1.2. Kiến trúc tổng thể hệ thống_** 



_Hình 2- 1 Kiến trúc tổng thể hệ thống_ 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_16_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

### **_2.1.3. Lý do lựa chọn công nghệ_** 

_Bảng 2- 1 So sánh và lý do lựa chọn công nghệ_ 

|**Tiêu chí**|**Next.js 14**|**Nuxt.js 3**|**Create React**<br>**App**|**Lựa chọn**|
|---|---|---|---|---|
|SSR/SSG/ISR|Đầy đủ|Đầy đủ|CSR only|Next.js|
|App Router (RSC)|Native|Partial|Không có|Next.js|
|Ecosystem|Rất lớn|Lớn (Vue)|Lớn|Next.js|
|TypeScript support|First-class|First-class|Good|Tie|
|Deploy flexibility|Vercel/self|Netlify/self|Anywhere|Tie|
|**Kết luận**|**Chọn**|Backup|Không|Next.js 14|



|**Tiêu chí**|**NestJS**|**Express.js**|**FastAPI (Python)**|
|---|---|---|---|
|Kiến trúc có cấu trúc|Module/DI/IoC|Minimal|Middleware|
|TypeScript native|First-class|Cần cấu hình|Python|
|Decorator pattern|||Partial|
|Swagger tích hợp|@nestjs/swagger|Manual|Built-in|
|Test support|Jest built-in|Manual|pytest|
|**Kết luận**|**Chọn**|Quá đơn giản|Dùng cho AI<br>service|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_17_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|**Tiêu chí**|**ChromaDB**|**Pinecone**|**Weaviate**|
|---|---|---|---|
|Self-hosted|Có thể|Cloud only|Có thể|
|Free tier|Hoàn toàn free|Giới hạn|Open source|
|Python client|Official|Official|Official|
|LangChain integration|First-class|First-class|Good|
|Ease of setup|Docker 1 lệnh|Account cần|Phức tạp hơn|
|**Kết luận**|**Chọn**|Quá đắt cho<br>dev|Quá phức tạp|



### **2.2. Frontend Next.js 14** 

### **_2.2.1. App Router vs Pages Router. Lý do chọn App Router_** 

Next.js 13 giới thiệu App Router  kiến trúc mới hoàn toàn dựa trên React Server Components (RSC). Trong khi Pages Router vẫn được hỗ trợ, Vercel (công ty đứng sau Next.js) đã rõ ràng định hướng App Router là tương lai của framework. Dự án chọn App Router vì các lý do kỹ thuật sau: 

_Server Components mặc định:_ Toàn bộ component render phía server, không gửi JavaScript xuống client  cải thiện FCP (First Contentful Paint) và giảm bundle size đáng kể. 

_Nested Layouts:_ App Router cho phép share layout giữa các route một cách tự nhiên mà không cần custom <mark>_app.tsx</mark> . Ví dụ, sidebar navigation chỉ được render một lần dù user navigate giữa các trang. 

_Streaming và Suspense:_ Kết hợp với React Suspense, App Router cho phép streaming từng phần của trang, cải thiện TTFB (Time to First Byte). 

_Route Groups:_ Nhóm route theo chức năng mà không ảnh hưởng URL path, giúp tổ chức code sạch hơn. 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_18_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

### **_2.2.2. Cấu trúc thư mục dự án_** 



<!-- Start of picture text -->
frontend/<br>├── app/                          # App Router root<br>│   ├── (auth)/                   # Route group: Auth pages<br>│   │   ├── login/<br>│   │   │   └── page.tsx<br>│   │   ├── register/<br>│   │   │   └── page.tsx<br>│   │   └── layout.tsx            # Auth layout (no sidebar)<br>│   ├── (dashboard)/              # Route group: Protected pages<br>│   │   ├── dashboard/<br>│   │   │   └── page.tsx<br>│   │   ├── documents/<br>│   │   │   ├── page.tsx          # Document list<br>│   │   │   ├── [id]/<br>│   │   │   │   └── page.tsx      # Document detail<br>│   │   │   └── upload/<br>│   │   │       └── page.tsx      # Upload new document<br>│   │   ├── chat/<br>│   │   │   ├── page.tsx          # Chat list / new chat<br>│   │   │   └── [sessionId]/<br>│   │   │       └── page.tsx      # Chat session<br>│   │   ├── settings/<br>│   │   │   └── page.tsx<br>│   │   └── layout.tsx            # Dashboard layout (with sidebar)<br>│   ├── api/                      # API Routes (BFF)<br>│   │   └── [...]/<br>│   ├── globals.css<br>│   ├── layout.tsx                # Root layout<br>│   └── page.tsx                  # Landing page<br>├── components/<br><!-- End of picture text -->

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_19_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 



<!-- Start of picture text -->
│   ├── ui/                       # Shadcn/UI components<br>│   │   ├── button.tsx<br>│   │   ├── dialog.tsx<br>│   │   ├── input.tsx<br>│   │   └── ...<br>│   ├── chat/<br>│   │   ├── ChatWindow.tsx<br>│   │   ├── MessageBubble.tsx<br>│   │   └── ChatInput.tsx<br>│   ├── documents/<br>│   │   ├── DocumentCard.tsx<br>│   │   └── DocumentUploader.tsx<br>│   └── shared/<br>│       ├── Navbar.tsx<br>│       └── Sidebar.tsx<br>├── hooks/                        # Custom React hooks<br>│   ├── useDocuments.ts<br>│   ├── useChat.ts<br>│   └── useAuth.ts<br>├── lib/<br>│   ├── api.ts                    # Axios/fetch wrapper<br>│   ├── auth.ts                   # NextAuth config<br>│   └── utils.ts                  # Helper functions<br>├── types/<br>│   ├── document.ts<br>│   ├── chat.ts<br>│   └── user.ts<br>└── tailwind.config.ts<br><!-- End of picture text -->

### **_2.2.3. Flowchart luồng điều hướng trang_** 

_Đàm Mạnh Dũng_ 

_20 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 



<!-- Start of picture text -->
_—<br>( @ User truy cap<br>y><br>adang nhap?<br>yfe {\<br>Chua<br>login<br>a dang nhap ( Chua co tai khoan<br>ang nh§p thanh cong Iregister<br>\ \ \ ang ky thanh cong<br>NN ee<br>ae % Idashboard<br>¥ a,- tf<br> /documents © Ichat %& /settings<br>7~x<br>Z\<br>Tao chat méi Mé chat cil<br>\ /<br>/documents/[id] Gi documents/upload @y /chat/[session|d]<br><!-- End of picture text -->

_Hình 2- 2 Flowchart luồng điều hướng trang frontend_ 

### **_2.2.4. React Query: Fetching, Caching, Mutation_** 

React Query (TanStack Query) được sử dụng để quản lý toàn bộ server state. Thay vì dùng useEffect + useState để fetch data, React Query cung cấp caching thông minh, background refetching và optimistic updates. 

### **_Code snippet 1 Custom hook với React Query_** 

◾ TYPESCRIPT 

// hooks/useDocuments.ts 

- // Hook tùy chỉnh quản lý danh sách tài liệu với React Query 

- // Tích hợp phân trang, tìm kiếm và cache tự động 

import { useQuery, useMutation, useQueryClient } from '@tanstack/react- 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_21_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

query'; import { documentsApi } from '@/lib/api'; import type { Document, CreateDocumentDto, DocumentListParams } from '@/types/document'; /** Khóa cache cho danh sách tài liệu  dùng array để hỗ trợ invalidation có chọn lọc */ export const documentKeys = { all: ['documents'] as const, lists: () => [...documentKeys.all, 'list'] as const, list: (params: DocumentListParams) => [...documentKeys.lists(), params] as const, detail: (id: string) => [...documentKeys.all, 'detail', id] as const, }; /** * Hook lấy danh sách tài liệu với phân trang và lọc. * Tự động cache kết quả 5 phút, refetch khi window focus. */ export function useDocuments(params: DocumentListParams = {}) { return useQuery({ queryKey: documentKeys.list(params), queryFn: () => documentsApi.getList(params), staleTime: 5 * 60 * 1000,       // 5 phút trước khi coi là stale gcTime: 10 * 60 * 1000,          // Giữ trong cache 10 phút placeholderData: (prev) => prev, // Hiện dữ liệu cũ khi fetch trang mới }); } /** * Hook lấy chi tiết một tài liệu theo ID. * Enabled chỉ khi có id hợp lệ. */ 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_22_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

export function useDocument(id: string | null) { return useQuery({ queryKey: documentKeys.detail(id!), queryFn: () => documentsApi.getById(id!), enabled: Boolean(id), // Không fetch nếu id null/undefined }); } /** * Hook tạo tài liệu mới. * Sau khi thành công: invalidate toàn bộ document list để refresh. */ export function useCreateDocument() { const queryClient = useQueryClient(); return useMutation({ mutationFn: (dto: CreateDocumentDto) => documentsApi.create(dto), onSuccess: () => { // Xóa cache danh sách → React Query tự động fetch lại queryClient.invalidateQueries({ queryKey: documentKeys.lists() }); }, onError: (error) => { console.error('Lỗi khi tạo tài liệu:', error); }, }); } /** * Hook xóa tài liệu với optimistic update. * Xóa khỏi UI ngay lập tức, rollback nếu server trả về lỗi. */ export function useDeleteDocument() { const queryClient = useQueryClient(); 

_Đàm Mạnh Dũng_ 

_23 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

return useMutation({ mutationFn: (id: string) => documentsApi.delete(id), onMutate: async (deletedId) => { // Hủy các query đang pending để tránh ghi đè optimistic update await queryClient.cancelQueries({ queryKey: documentKeys.lists() }); // Lưu snapshot để rollback nếu cần const previousDocuments = queryClient.getQueryData(documentKeys.lists()); // Optimistic: xóa khỏi cache ngay lập tức queryClient.setQueriesData( { queryKey: documentKeys.lists() }, (old: Document[] | undefined) => old?.filter((doc) => doc.id !== deletedId) ?? [] ); return { previousDocuments }; // Context để rollback }, onError: (_err, _id, context) => { // Rollback nếu server lỗi if (context?.previousDocuments) { queryClient.setQueryData(documentKeys.lists(), context.previousDocuments); } }, onSettled: () => { // Dù thành công hay lỗi, refresh lại danh sách từ server queryClient.invalidateQueries({ queryKey: documentKeys.lists() }); }, }); } 

### **_Code snippet 2 Server Component với Data Fetching_** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_24_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

◾ TYPESCRIPT 

// app/(dashboard)/documents/page.tsx // Server Component  render phía server, không cần client-side JS để fetch import { Suspense } from 'react'; import { DocumentList } from '@/components/documents/DocumentList'; import { DocumentListSkeleton } from '@/components/documents/DocumentListSkeleton'; import { getDocuments } from '@/lib/server/documents'; // Server-side fetch function /** Props được truyền từ URL search params */ interface DocumentsPageProps { searchParams: { page?: string; search?: string; category?: string; }; } /** * Trang danh sách tài liệu  Server Component. * Next.js tự động tạo Static Shell và Stream nội dung sau khi fetch xong. */ export default async function DocumentsPage({ searchParams }: DocumentsPageProps) { // Parse search params với giá trị mặc định const page = parseInt(searchParams.page ?? '1', 10); const search = searchParams.search ?? ''; const category = searchParams.category ?? 'all'; // Fetch dữ liệu trực tiếp trong Server Component  không cần useEffect 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_25_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

const { documents, totalCount, totalPages } = await getDocuments({ page, search, category, limit: 12, }); return ( <main className="container mx-auto px-4 py-8"> <div className="mb-6 flex items-center justify-between"> <h1 className="text-2xl font-bold text-gray-900">Tài liệu nội bộ</h1> <span className="text-sm text-gray-500">{totalCount} tài liệu</span> </div> {/* Suspense boundary cho phần tương tác (Client Component bên trong) */} <Suspense fallback={<DocumentListSkeleton count={12} />}> <DocumentList initialDocuments={documents} totalPages={totalPages} currentPage={page} initialSearch={search} initialCategory={category} /> </Suspense> </main> ); } 

### **_2.2.5. Shadcn/UI và TailwindCSS Design System_** 

Shadcn/UI được lựa chọn thay vì MUI hay Ant Design vì triết lý "copy -paste" toàn bộ component được copy trực tiếp vào codebase thay vì install như dependency, cho phép tùy chỉnh hoàn toàn mà không phải override CSS của 

_Đàm Mạnh Dũng_ 

_26 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

library. TailwindCSS cung cấp utility classes nhất quán và tích hợp hoàn hảo với Shadcn/UI. 

### **_2.2.6. Danh sách trang và route_** 

_Bảng 2- 2 Danh sách các trang chính, route và mô tả_ 

|**Trang**|**Route**|**Loại**|**Mô tả chức năng**|
|---|---|---|---|
|Landing|`/`|Server|Trang giới thiệu ứng dụng, nút<br>đăng nhập/đăng ký|
|Đăng nhập|`/login`|Client|Form đăng nhập<br>email/password, Google OAuth|
|Đăng ký|`/register`|Client|Form đăng ký tài khoản mới|
|Dashboard|`/<br>dashboard`|Server|Tổng quan: số tài liệu, chat<br>sessions, activity|
|Danh sách tài<br>liệu|`/<br>documents`|Server|Grid/list tài liệu, tìm kiếm, lọc<br>theo category|
|Chi tiết tài liệu|`/<br>documents/<br>[id]`|Server|Xem nội dung tài liệu, metadata,<br>lịch sử|
|Upload tài liệu|`/<br>documents/<br>upload`|Client|Form upload PDF/TXT, nhập<br>metadata|
|Danh sách chat|`/chat`|Server|Lịch sử các phiên chat, tạo chat<br>mới|
|Phiên chat|`/chat/<br>[sessionId]`|Client|Giao diện chatbot real-time với<br>streaming|
|Cài đặt|`/settings`|Client|Cập nhật profile, đổi mật khẩu,<br>notification|
|Admin Users|`/admin/<br>users`|Server|Quản lý người dùng (Admin<br>only)|
|Admin|`/admin/|Server|Duyệt tài liệu, gán category|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_27_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

Documents documents` (Admin only) 

### **2.3. Backend NestJS** 

### **_2.3.1. Kiến trúc Module/Controller/Service/Repository_** 

NestJS áp dụng mô hình Dependency Injection (DI) và Inversion of Control (IoC) tương tự Angular, cho phép xây dựng backend có cấu trúc rõ ràng và dễ test. Kiến trúc được tổ chức theo nguyên tắc Single Responsibility: 

_Module:_ Đơn vị đóng gói nhóm các Controller, Service, Repository liên quan đến một domain cụ thể (ví dụ: <mark>DocumentModule</mark> , <mark>ChatModule</mark> , <mark>AuthModule</mark> ). Module khai báo rõ những gì nó export để các module khác có thể inject. 

_Controller:_ Xử lý HTTP request, validate input qua DTO (Data Transfer Object) với class-validator, gọi Service để thực hiện nghiệp vụ, trả về response. Controller không chứa logic nghiệp vụ. 

_Service:_ Chứa toàn bộ business logic. Service có thể gọi Repository, gọi service khác qua DI, tương tác với Redis, hoặc gọi external API. Service được test bằng unit test với mock dependencies. 

_Repository (via Prisma):_ Abstraction layer cho database operations. Với Prisma, <mark>PrismaService</mark> đóng vai trò repository, cung cấp type-safe database access. 

Cấu trúc thư mục backend: 

backend/ ├── src/ │   ├── auth/ │   │   ├── auth.module.ts │   │   ├── auth.controller.ts │   │   ├── auth.service.ts │   │   ├── guards/ │   │   │   ├── jwt.guard.ts │   │   │   └── roles.guard.ts │   │   ├── strategies/ 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_28_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

- │   │   │   └── jwt.strategy.ts │   │   └── decorators/ │   │       ├── current-user.decorator.ts │   │       └── roles.decorator.ts │   ├── documents/ │   │   ├── documents.module.ts │   │   ├── documents.controller.ts │   │   ├── documents.service.ts │   │   └── dto/ │   │       ├── create-document.dto.ts │   │       └── update-document.dto.ts │   ├── chat/ │   │   ├── chat.module.ts │   │   ├── chat.controller.ts 

- │   │   └── chat.service.ts │   ├── users/ │   ├── ai/ 

- │   │   ├── ai.module.ts │   │   └── ai.service.ts         # HTTP client gọi Python AI service 

- │   ├── prisma/ │   │   └── prisma.service.ts 

- │   ├── redis/ 

- │   │   └── redis.service.ts │   └── main.ts ├── prisma/ │   ├── schema.prisma │   └── migrations/ └── test/ 

### **_2.3.2. Danh sách REST API Endpoints_** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_29_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

_Bảng 2- 3 Danh sách REST API endpoints_ 

|**Method**|**Endpoint**|**Auth**|**Mô tả**|**Response**|
|---|---|---|---|---|
|POST|`/auth/register`|Public|Đăng ký tài khoản<br>mới|`{ user,<br>accessToken,<br>refreshToken }`|
|POST|`/auth/login`|Public|Đăng nhập, nhận<br>JWT|`{ user,<br>accessToken,<br>refreshToken }`|
|POST|`/auth/refresh`|Bearer<br>Refres<br>hToke<br>n|Làm mới access<br>token|`{ accessToken }`|
|POST|`/auth/logout`|Bearer|Đăng xuất,<br>invalidate token|`{ message }`|
|GET|`/users/me`|Bearer|Lấy thông tin user<br>hiện tại|`User`|
|PATCH|`/users/me`|Bearer|Cập nhật profile|`User`|
|GET|`/documents`|Bearer|Danh sách tài liệu<br>(paging, filter)|`PaginatedResult<D<br>ocument>`|
|POST|`/documents`|Bearer|Tạo tài liệu mới<br>(upload file)|`Document`|
|GET|`/documents/:id`|Bearer|Chi tiết một tài liệu|`Document`|
|PATCH|`/documents/:id`|Bearer|Cập nhật metadata<br>tài liệu|`Document`|
|||Bearer|||
|DELETE|`/documents/:id`|+<br>Admin|Xóa tài liệu|`{ message }`|



_Đàm Mạnh Dũng_ 

_30 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|POST|`/<br>documents/:id/<br>process`|Bearer<br>+<br>Admin|Trigger AI<br>processing<br>(embedding)|`{ jobId }`|
|---|---|---|---|---|
|GET|`/chat/sessions`|Bearer|Danh sách chat<br>sessions|`Session[]`|
|POST|`/chat/sessions`|Bearer|Tạo chat session<br>mới|`Session`|
|GET|`/chat/<br>sessions/:id`|Bearer|Chi tiết session +<br>messages|`SessionWithMessa<br>ges`|
|DELETE|`/chat/<br>sessions/:id`|Bearer|Xóa chat session|`{ message }`|
|POST|`/chat/<br>sessions/:id/<br>messages`|Bearer|Gửi tin nhắn, nhận<br>AI response|`Message`|
|GET|`/chat/<br>sessions/:id/<br>messages`|Bearer|Lịch sử tin nhắn|`Message[]`|
|GET|`/admin/users`|Bearer<br>+<br>Admin|Quản lý users<br>(Admin)|`PaginatedResult<U<br>ser>`|
|PATCH|`/admin/<br>users/:id/role`|Bearer<br>+<br>Admin|Thay đổi role user|`User`|



### **_2.3.3. JWT Authentication Flow_** 

JWT Authentication được triển khai với Access Token (15 phút) và Refresh Token (7 ngày). Khi Access Token hết hạn, client tự động gọi <mark>/auth/refresh</mark> để nhận token mới mà không cần đăng nhập lại. 

### **_2.3.4. Entity Relationship Diagram_** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_31_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 



<!-- Start of picture text -->
a<br>has wlgads} owns<br>A<br>, [me [e [om<br>= [a | i<br>[ome [#[msSession | [eo[ewance |L|| [ore [o[reA<br>(os[ome w mo| [eon[mee[ome | | (ow[eal[=||<br>[sme [res | | |<br>ESic—ail[sm [[ome suing |[ew uoadeasyid| (ere [ewlastMessageat|[ |<br>on | [am a ||<br>oc<br>‘split into contains<br>fy<br>A<br>6<br>[ri<br>ConA (ome fe<br>Cc cee<br>(owe[owe ome ame [ || [ meeeom|<br>(asm femwes |] [mew|<br>a<br><!-- End of picture text -->

_Hình 2- 3 ERD (Entity Relationship Diagram)_ 

### **_2.3.5. Sequence Diagram Đăng Nhập_** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_32_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 



<!-- Start of picture text -->
Nextis Frontend Nests Backend PostgreSQL. Regis Cache<br>User<br>INhp email + password — Submit<br>OST /autviogin{ email, password}<br>SELECT<br>user WHERE email=?<br>User record (ho8e null)<br>ant [User khang tén ta]<br>401 Unauthorized<br>“Thong bio "Email khGng tn ta<br>[Password sa]<br>bberyptcompare(password, hash)<br>401 Unauthorized<br>+<br>“Thang bao "Mat Khu kong ding<br>{ang nhp thanh cong]<br>Tao accessToken (WT, 15m)<br>Tao retreshTaken (JWT, 7a)<br>INSERT Session { userld, retestToken, .}<br>SET session:{userg) TTL 74<br>ox<br>.<br>2004 )<br>“4 200 { user, accessToken, retteshToken<br>Lau accessToken vito memory<br>Luu retteshToken vao hitpOnly cookie<br>en Reset = dashboard<br>Nextjs Frontend Nesus Backend PostoreSQL, Redis Cache<br>User<br><!-- End of picture text -->

_Hình 2- 4 Sequence diagram luồng đăng nhập JWT_ 

### **_2.3.6. Prisma ORM  Schema và Migrations_** 

Prisma cung cấp type-safe database access với schema được định nghĩa trong <mark>schema.prisma</mark> . Mỗi thay đổi schema tạo ra một migration file được version control, đảm bảo nhất quán giữa các môi trường. 

**_Code snippet 3  NestJS Service với Prisma_** 

◾ TYPESCRIPT 

// documents/documents.service.ts // Service quản lý nghiệp vụ tài liệu  tầng business logic import { Injectable, NotFoundException, 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_33_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

ForbiddenException, } from '@nestjs/common'; import { PrismaService } from '../prisma/prisma.service'; import { AiService } from '../ai/ai.service'; import { CreateDocumentDto } from './dto/create-document.dto'; import { UpdateDocumentDto } from './dto/update-document.dto'; import { DocumentStatus, Role } from '@prisma/client'; import type { User } from '@prisma/client'; /** Số lượng tài liệu mỗi trang mặc định */ const DEFAULT_PAGE_SIZE = 12; @Injectable() export class DocumentsService { constructor( private readonly prisma: PrismaService, private readonly aiService: AiService, ) {} /** * Lấy danh sách tài liệu có phân trang và lọc. * @param page - Số trang (bắt đầu từ 1) * @param limit - Số bản ghi mỗi trang * @param search - Từ khóa tìm kiếm trong title/description * @param category - Lọc theo category ('all' = không lọc) * @returns Danh sách tài liệu + tổng số bản ghi */ async findAll( page = 1, limit = DEFAULT_PAGE_SIZE, search = '', category = 'all', 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_34_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

) { const skip = (page - 1) * limit; // Xây dựng điều kiện WHERE động const where = { ...(search && { OR: [ { title: { contains: search, mode: 'insensitive' as const } }, { description: { contains: search, mode: 'insensitive' as const } }, ], }), ...(category !== 'all' && { category }), }; // Chạy 2 query song song: lấy data và đếm tổng const [documents, totalCount] = await this.prisma.$transaction([ this.prisma.document.findMany({ where, skip, take: limit, orderBy: { createdAt: 'desc' }, include: { uploadedBy: { select: { id: true, name: true, email: true } }, _count: { select: { chunks: true } }, }, }), this.prisma.document.count({ where }), ]); return { documents, 

_Đàm Mạnh Dũng_ 

_35 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

totalCount, totalPages: Math.ceil(totalCount / limit), currentPage: page, }; } /** * Tìm một tài liệu theo ID. * Throw NotFoundException nếu không tồn tại. */ async findOne(id: string) { const document = await this.prisma.document.findUnique({ where: { id }, include: { uploadedBy: { select: { id: true, name: true } }, chunks: { orderBy: { chunkIndex: 'asc' }, take: 5 }, // Preview 5 chunks đầu }, }); if (!document) { throw new NotFoundException(`Tài liệu ID "${id}" không tồn tại`); } return document; } /** * Tạo tài liệu mới và trigger AI processing ở background. * File đã được upload trước bởi middleware, chỉ cần lưu metadata. */ async create(dto: CreateDocumentDto, uploadedBy: User) { const document = await this.prisma.document.create({ data: { 

_Đàm Mạnh Dũng_ 

_36 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

title: dto.title, description: dto.description ?? '', filePath: dto.filePath, fileType: dto.fileType, fileSize: dto.fileSize, category: dto.category ?? 'general', status: DocumentStatus.PENDING, uploadedById: uploadedBy.id, }, }); // Trigger AI processing bất đồng bộ (không await) this.aiService.processDocument(document.id).catch((err) => { console.error(`Lỗi khi xử lý tài liệu ${document.id}:`, err); }); return document; } /** * Cập nhật metadata tài liệu. * Chỉ người upload hoặc Admin mới có quyền sửa. */ async update(id: string, dto: UpdateDocumentDto, requestedBy: User) { const document = await this.findOne(id); if (document.uploadedById !== requestedBy.id && requestedBy.role !== Role.ADMIN) { throw new ForbiddenException('Bạn không có quyền chỉnh sửa tài liệu này'); } return this.prisma.document.update({ where: { id }, 

_Đàm Mạnh Dũng_ 

_37 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

data: dto, }); } } 

### **_Code snippet 4 JWT Guard và Custom Decorator_** 

◾ TYPESCRIPT 

// auth/guards/jwt.guard.ts + auth/decorators/current-user.decorator.ts // Guard xác thực JWT và Decorator lấy thông tin user từ request import { Injectable, ExecutionContext, UnauthorizedException, createParamDecorator, } from '@nestjs/common'; import { AuthGuard } from '@nestjs/passport'; import { Reflector } from '@nestjs/core'; import { IS_PUBLIC_KEY } from '../decorators/public.decorator'; import type { Request } from 'express'; import type { User } from '@prisma/client'; /** * Guard xác thực JWT. * Tự động bỏ qua nếu route có decorator @Public(). * Khi token hợp lệ, attach user vào request.user. */ @Injectable() export class JwtAuthGuard extends AuthGuard('jwt') { constructor(private reflector: Reflector) { super(); } 

_Đàm Mạnh Dũng_ 

_38 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

canActivate(context: ExecutionContext) { // Kiểm tra route có được đánh dấu @Public() không const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [ context.getHandler(), context.getClass(), ]); if (isPublic) return true; // Gọi AuthGuard('jwt') để validate token return super.canActivate(context); } /** Override để tùy chỉnh thông báo lỗi tiếng Việt */ handleRequest<TUser = User>(err: Error | null, user: TUser | false): TUser { if (err || !user) { throw new UnauthorizedException( 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.' ); } return user; } } // ─── auth/guards/roles.guard.ts import { Injectable, ExecutionContext, CanActivate } from '@nestjs/common'; import { Reflector } from '@nestjs/core'; import { Role } from '@prisma/client'; import { ROLES_KEY } from '../decorators/roles.decorator'; /** * Guard kiểm tra role của user. * Dùng kết hợp với @Roles('ADMIN') decorator. 

_Đàm Mạnh Dũng_ 

_39 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

*/ @Injectable() export class RolesGuard implements CanActivate { constructor(private reflector: Reflector) {} canActivate(context: ExecutionContext): boolean { const requiredRoles = this.reflector.getAllAndOverride<Role[]>(ROLES_KEY, [ context.getHandler(), context.getClass(), ]); if (!requiredRoles || requiredRoles.length === 0) return true; const { user } = context.switchToHttp().getRequest<Request & { user: User }>(); return requiredRoles.includes(user.role); } } // ─── auth/decorators/current-user.decorator.ts /** * Decorator lấy thông tin user hiện tại từ request. * Sử dụng: async getMe(@CurrentUser() user: User) * Hỗ trợ lấy field cụ thể: @CurrentUser('id') userId: string */ export const CurrentUser = createParamDecorator( (field: keyof User | undefined, ctx: ExecutionContext) => { const request = ctx.switchToHttp().getRequest<Request & { user: User } >(); const user = request.user; return field ? user?.[field] : user; }, ); 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_40_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

### **2.4. AI Chatbot RAG & LLM** 

### **_2.4.1. So sánh RAG vs Fine-tuning vs Prompt-only_** 

_Bảng 2- 4 So sánh các phương pháp tích hợp LLM vào ứng dụng_ 

|**Tiêu chí**|**Prompt-only**|**Fine-tuning**|**RAG**|
|---|---|---|---|
|Chi phí triển khai|Thấp|Rất cao ($500–<br>$5000/lần)|Thấp–Trung bình|
|Cập nhật kiến<br>thức|Không thể|Phải train lại|Real-time|
|Kiểm soát nguồn<br>thông tin|Không|Khó|Hoàn toàn|
|Độ chính xác với<br>dữ liệu riêng|Kém|Tốt|Tốt|
|Hallucination (bịa<br>thông tin)|Cao|Trung bình|Thấp (có nguồn)|
|Thời gian setup|Vài giờ|Vài ngày–tuần|1–2 ngày|
|Phù hợp quy mô|Nhỏ|Lớn|Mọi quy mô|
|Khả năng audit|Không|Không|Có (traceable)|
|**Khuyến nghị**|Demo/MVP|Specialized<br>domain|**Production**|



**Kết luận:** RAG là lựa chọn tối ưu cho dự án này vì tài liệu nội bộ thay đổi thường xuyên, cần độ chính xác cao, chi phí thấp và khả năng audit nguồn thông tin. 

### **_2.4.2. RAG Pipeline_** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_41_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 



<!-- Start of picture text -->
INDEXING PHASE (Offine)<br>Tai igu nguén\n(POF,<br>TXT, Markdown)<br>sh Document<br>Loader\n(LangChain)<br>‘90 Text<br>Splitterin(chunk_size=512,<br>overlap=50)<br>RETRIEVAL PHASE |<br>(Online) Embedding<br>© User Question Modelin(text-embedding-<br>| ada-002)<br>Bis eae @vectorsChromaDBin(Luu + metadata)<br>| » Vector Search<br>& Cosine Similarity<br>Searchin(Top-K = 5)<br>jul Reranking\n(Cross-<br>encoder)<br># Retrieved Context<br>i PHASE<br>@ Prompt<br>Template\n(System +<br>Context + Question)<br>ey GPT-4o-minin(Opendl<br>API)<br>® Al Response\n(véi<br>citation nguén)<br><!-- End of picture text -->

_Hình 2- 5 RAG Pipeline đầy đủ_ 

### **_2.4.3. Vector Database và Embedding_** 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_42_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

### **Giải thích kỹ thuật về Embedding và Cosine Similarity:** 

Embedding là quá trình chuyển đổi văn bản sang vector số học trong không gian nhiều chiều. Mô hình <mark>text-embedding-ada-002</mark> của OpenAI tạo ra vector 1536 chiều cho mỗi đoạn văn bản. Các đoạn văn có nội dung liên quan sẽ có vector gần nhau trong không gian này. 

Cosine Similarity đo góc giữa hai vector (không phải khoảng cách Euclidean), phù hợp cho so sánh ngữ nghĩa vì không phụ thuộc vào độ dài văn bản: 

cosinesimilarity(A, B) = (A · B) / (||A|| × ||B||) 

Giá trị từ -1 (hoàn toàn ngược nghĩa) đến 1 (hoàn toàn giống nghĩa). Ngưỡng cosine similarity 0.75 được dùng để lọc kết quả không liên quan. Vì ChromaDB được cấu hình với <mark>hnsw:space: cosine</mark> trả về cosine distance (= 1 − cosine_similarity), ngưỡng tương đương là distance ≤ 0.25. 

### **_Code snippet 5 Document Ingestion Pipeline (Python)_** 

◾ PYTHON 

# ai_service/ingestion/document_processor.py 

# Pipeline xử lý tài liệu: đọc → chia nhỏ → embedding → lưu vào ChromaDB 

# Chạy bất đồng bộ sau khi user upload tài liệu mới import os from pathlib import Path from typing import Optional import chromadb 

from chromadb.config import Settings 

from langchain_community.document_loaders import PyPDFLoader, TextLoader 

from langchain_text_splitters import RecursiveCharacterTextSplitter from langchain_openai import OpenAIEmbeddings from langchain_community.vectorstores import Chroma import httpx  # Để callback về NestJS khi xử lý xong 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_43_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

# Kích thước chunk và overlap  cân bằng giữa context đủ dài và precision CHUNK_SIZE = 512 CHUNK_OVERLAP = 50 TOP_K_RESULTS = 5 class DocumentProcessor: """ Xử lý và index tài liệu vào ChromaDB. Mỗi document được chia thành các chunks nhỏ, mỗi chunk được tạo embedding và lưu vào vector store. """ def __init__(self, collection_name: str = "documents"): # Khởi tạo ChromaDB client (persistent storage) self.chroma_client = chromadb.PersistentClient( path=os.getenv("CHROMA_PERSIST_PATH", "./chroma_data"), settings=Settings(anonymized_telemetry=False), ) # Embedding model  sử dụng OpenAI Ada-002 (1536 dimensions) self.embeddings = OpenAIEmbeddings( model="text-embedding-ada-002", openai_api_key=os.getenv("OPENAI_API_KEY"), ) # Text splitter  RecursiveCharacter ưu tiên tách ở dấu câu/dòng mới self.text_splitter = RecursiveCharacterTextSplitter( chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""], ) self.collection_name = collection_name 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_44_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

def load_document(self, file_path: str) -> list: """ Đọc tài liệu từ file path. Hỗ trợ PDF và TXT  dễ dàng mở rộng thêm định dạng khác. """ path = Path(file_path) if path.suffix.lower() == ".pdf": loader = PyPDFLoader(file_path) elif path.suffix.lower() in [".txt", ".md"]: loader = TextLoader(file_path, encoding="utf-8") else: raise ValueError(f"Định dạng file không được hỗ trợ: {path.suffix}") return loader.load() def process_and_index( self, document_id: str, file_path: str, metadata: Optional[dict] = None, ) -> dict: """ Pipeline đầy đủ: đọc file → chia chunks → tạo embedding → lưu ChromaDB. Args: document_id: ID tài liệu trong PostgreSQL (để liên kết) file_path: Đường dẫn file vật lý metadata: Thông tin bổ sung (title, category, uploadedBy...) Returns: dict với số chunks đã index và collection name 

_Đàm Mạnh Dũng_ 

_45 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

""" # Bước 1: Đọc tài liệu raw_documents = self.load_document(file_path) # Bước 2: Chia nhỏ thành chunks chunks = self.text_splitter.split_documents(raw_documents) # Bước 3: Thêm metadata vào mỗi chunk base_metadata = metadata or {} for i, chunk in enumerate(chunks): chunk.metadata.update({ **base_metadata, "document_id": document_id, "chunk_index": i, "total_chunks": len(chunks), }) # Bước 4: Tạo embedding và lưu vào ChromaDB vector_store = Chroma.from_documents( documents=chunks, embedding=self.embeddings, client=self.chroma_client, collection_name=self.collection_name, collection_metadata={"hnsw:space": "cosine"},  # Dùng cosine similarity ) # Bước 5: Trả về kết quả return { "document_id": document_id, "chunks_indexed": len(chunks), 

_Đàm Mạnh Dũng_ 

_46 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

"collection": self.collection_name, "status": "success", } def search(self, query: str, k: int = TOP_K_RESULTS, filter_dict: Optional[dict] = None) -> list: """ Tìm kiếm semantic trong ChromaDB. Trả về top-K chunks liên quan nhất theo cosine similarity. """ vector_store = Chroma( client=self.chroma_client, collection_name=self.collection_name, embedding_function=self.embeddings, ) # Tìm kiếm với similarity score results = vector_store.similarity_search_with_score( query=query, k=k, filter=filter_dict, ) # Lọc kết quả dưới ngưỡng similarity SIMILARITY_THRESHOLD = 0.25  # ChromaDB cosine distance (= 1 - cosine_similarity), thấp hơn = tương đồng hơn → tương đương cosine_similarity ≥ 0.75 filtered = [ {"content": doc.page_content, "metadata": doc.metadata, "score": score} for doc, score in results if score <= SIMILARITY_THRESHOLD ] return filtered 

_Đàm Mạnh Dũng_ 

_47 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

### **_2.4.4. Prompt Engineering_** 

### **_Code snippet 6 LangChain Chain với RAG (Python)_** 

◾ PYTHON 

# ai_service/chains/rag_chain.py 

# LangChain RAG chain  kết hợp retrieval và generation 

# Trả về câu trả lời kèm danh sách nguồn tham khảo 

from langchain_openai import ChatOpenAI 

from langchain.prompts import ChatPromptTemplate from langchain.schema.runnable import RunnablePassthrough from langchain.schema.output_parser import StrOutputParser 

from .document_processor import DocumentProcessor 

# System prompt được thiết kế để: 

- # 1. Giới hạn AI chỉ trả lời dựa trên context được cung cấp 

# 2. Yêu cầu trích dẫn nguồn 

- # 3. Thừa nhận khi không biết thay vì bịa thông tin 

SYSTEM_PROMPT = """Bạn là trợ lý AI nội bộ của DC-STRUCTURES VIETNAM. 

Nhiệm vụ của bạn là trả lời câu hỏi của nhân viên dựa trên tài liệu nội bộ được cung cấp. 

NGUYÊN TẮC: 

1. Chỉ trả lời dựa trên CONTEXT bên dưới  không dùng kiến thức bên ngoài 2. Nếu context không đủ thông tin, nói rõ: "Tôi không tìm thấy thông tin này trong tài liệu nội bộ" 

3. Trích dẫn tên tài liệu nguồn khi trả lời 

4. Trả lời bằng tiếng Việt, ngắn gọn và chính xác 

CONTEXT: 

{context} 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_48_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

CÂU HỎI: {question} TRẢ LỜI:""" class RAGChain: """ RAG Chain hoàn chỉnh: retrieval → prompt construction → LLM generation. Sử dụng LangChain LCEL (LangChain Expression Language) cho pipeline rõ ràng. """ def __init__(self): self.processor = DocumentProcessor() # GPT-4o-mini: cân bằng tốt giữa chất lượng và chi phí self.llm = ChatOpenAI( model="gpt-4o-mini", temperature=0.1,        # Giảm randomness  ưu tiên độ chính xác max_tokens=1024, streaming=True,         # Streaming để UX tốt hơn ) self.prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT) self.output_parser = StrOutputParser() def _format_context(self, retrieved_chunks: list) -> str: """Định dạng context từ danh sách chunks để đưa vào prompt.""" formatted = [] for i, chunk in enumerate(retrieved_chunks, 1): title = chunk["metadata"].get("title", "Không rõ") content = chunk["content"] formatted.append(f"[Nguồn {i} - {title}]\n{content}") return "\n\n---\n\n".join(formatted) 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_49_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

def invoke(self, question: str, session_id: str = None) -> dict: """ Thực thi RAG pipeline đầy đủ. Returns: dict với 'answer' (câu trả lời) và 'sources' (danh sách tài liệu nguồn) """ # Bước 1: Retrieve relevant chunks retrieved = self.processor.search(query=question, k=5) if not retrieved: return { "answer": "Tôi không tìm thấy thông tin liên quan trong tài liệu nội bộ.", "sources": [], "tokens_used": 0, } # Bước 2: Format context context = self._format_context(retrieved) # Bước 3: Build và run chain (LCEL syntax) chain = ( {"context": lambda _: context, "question": RunnablePassthrough()} | self.prompt | self.llm | self.output_parser ) answer = chain.invoke(question) # Bước 4: Trích xuất danh sách nguồn unique sources = list({ chunk["metadata"].get("document_id") 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_50_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

for chunk in retrieved if chunk["metadata"].get("document_id") }) return { "answer": answer, "sources": sources, "retrieved_chunks": len(retrieved), } 

### **_2.4.5. Sequence Diagram Chatbot_** 



<!-- Start of picture text -->
Nest Frontend Nests Backend<br>yonAlSoe Cheoma0 penal GPT-Aoin<br>L><br>Lis Messageol:USER) vio DB<br>POST ley {uestn, session}<br>Nes Frond Nests Backend<br>PynanA Sane (heomaps (penal GPF-Ao-in<br><!-- End of picture text -->

_Hình 2- 6 Sequence diagram luồng chatbot_ 

### **_2.4.6. Đánh giá chất lượng Chatbot_** 

_Bảng 2- 5 Kết quả đánh giá chatbot theo test cases_ 

|**Test**<br>**Case**|**Loại**<br>**câu hỏi**|**Câu hỏi mẫu**|**Kết quả**<br>**mong đợi**|**Kết quả**<br>**thực tế**|**Đúng?**|**Latency**|
|---|---|---|---|---|---|---|
|TC-01|Tra cứu<br>tài liệu<br>trực tiếp|"Quy trình<br>onboarding cho<br>developer mới?"|Liệt kê 5<br>bước<br>onboarding|Liệt kê đủ<br>5 bước,<br>trích nguồn<br>Onboarding||2.3s|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_51_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|TC-02|Câu hỏi<br>kỹ thuật<br>có trong<br>ADR|"Tại sao dùng<br>Redis thay vì<br>database cho<br>session?"|Giải thích<br>lý do từ<br>ADR-004|Guide<br>Trả lời<br>chính xác,<br>cite<br>ADR-004|3.1s|
|---|---|---|---|---|---|
|TC-03|Câu hỏi<br>không<br>có trong<br>tài liệu|"Chiến lược<br>marketing năm<br>2027?"|"Không<br>tìm thấy<br>trong tài<br>liệu"|Thừa nhận<br>không có<br>thông tin|1.8s|
|TC-04|Câu hỏi<br>phức tạp<br>nhiều<br>nguồn|"So sánh kiến trúc<br>monolith vs<br>microservice theo<br>quan điểm của<br>công ty?"|Tổng hợp<br>từ nhiều tài<br>liệu|Tổng hợp<br>tốt từ 3 tài<br>liệu khác<br>nhau|4.2s|
|TC-05|Câu hỏi<br>mơ hồ|"Cách deploy?"|Hỏi làm rõ<br>hoặc tổng<br>quan|Trả lời tổng<br>quan + gợi<br>ý câu hỏi<br>cụ thể hơn|2.7s|
|TC-06|Câu hỏi<br>về API<br>cụ thể|"Endpoint nào để<br>upload tài liệu?"|POST<br>/document<br>s với<br>format|Trả lời<br>đúng<br>endpoint và<br>request<br>format|2.4s|
|TC-07|Edge<br>case:<br>tiếng<br>Anh|"What is the<br>database schema<br>for users?"|Trả lời<br>bằng tiếng<br>Việt|Trả lời<br>tiếng Việt,<br>thông tin<br>đúng|2.9s|
|TC-08|Câu hỏi<br>nhạy<br>cảm|"Lương của các<br>developer là bao<br>nhiêu?"|Từ chối trả<br>lời|Từ chối<br>lịch sự,<br>không<br>hallucinate|1.5s|
|TC-09|Typo/lỗi<br>chính tả|"nestjjs module la<br>gi?"|Hiểu và trả<br>lời đúng|Hiểu được<br>ý định, trả|2.6s|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_52_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|||||lời chính<br>xác|||
|---|---|---|---|---|---|---|
|TC-10|Câu hỏi<br>thiếu<br>context|"Làm thế nào để<br>fix lỗi đó?"|Hỏi lại "lỗi<br>nào?"|Hỏi làm rõ<br>thêm thông<br>tin|⚠️�|1.9s|



**Tổng kết:** 9/10 test cases đúng hoàn toàn (90%), 1 case xử lý chấp nhận được. Latency trung bình: 2.6 giây (< 5 giây yêu cầu). Độ chính xác 90% vượt mục tiêu 80% đề ra. 

### **2.5. Quy trình phát triển** 

### **_2.5.1. Git Workflow_** 



<!-- Start of picture text -->
main<br>< =<br>“fe ,<br>°<br>4 y /| A Va<br>om oe * / Pa y.<br>dd<br>oe<br>£<br>“Teaturelrag-pipaine fe<br>tls<br>“eleaseN.0) Lf fo - Ca<br>f/f<br><!-- End of picture text -->

_Hình 2- 7 Git Workflow_ 

### **_2.5.2. Docker Containerization_** 

### **_Code snippet 7 docker-compose.yml_** 

◾ YAML 

# docker-compose.yml # Khởi động toàn bộ stack với một lệnh: docker compose up -d # Bao gồm: Next.js, NestJS, Python AI Service, PostgreSQL, Redis, ChromaDB version: '3.8' 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_53_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

services: # ─── Frontend frontend: build: context: ./frontend dockerfile: Dockerfile ports: - "3000:3000" environment: - NEXT_PUBLIC_API_URL=http://backend:4000 - NEXTAUTH_SECRET=${NEXTAUTH_SECRET} - NEXTAUTH_URL=http://localhost:3000 depends_on: - backend networks: - app-network # ─── Backend API backend: build: context: ./backend dockerfile: Dockerfile ports: - "4000:4000" environment: DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD} @postgres:5432/dcstructures - REDIS_URL=redis://redis:6379 - AI_SERVICE_URL=http://ai-service:8000 - JWT_SECRET=${JWT_SECRET} 

- JWT_REFRESH_SECRET=${JWT_REFRESH_SECRET} 

_Đàm Mạnh Dũng_ 

_54 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

depends_on: postgres: condition: service_healthy redis: condition: service_healthy networks: - app-network # ─── Python AI Service ai-service: build: context: ./ai_service dockerfile: Dockerfile ports: - "8000:8000" environment: - OPENAI_API_KEY=${OPENAI_API_KEY} - CHROMA_HOST=chroma - CHROMA_PORT=8001 - CHROMA_PERSIST_PATH=/data/chroma volumes: - ai-data:/data/chroma - ./uploads:/data/uploads:ro  # Read-only access to uploaded files depends_on: - chroma networks: - app-network # ─── PostgreSQL postgres: image: postgres:16-alpine 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_55_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

environment: - POSTGRES_DB=dcstructures - POSTGRES_USER=postgres - POSTGRES_PASSWORD=${POSTGRES_PASSWORD} volumes: - postgres-data:/var/lib/postgresql/data healthcheck: test: ["CMD-SHELL", "pg_isready -U postgres"] interval: 10s timeout: 5s retries: 5 networks: - app-network # ─── Redis redis: image: redis:7-alpine command: redis-server --requirepass ${REDIS_PASSWORD} -- maxmemory 256mb --maxmemory-policy allkeys-lru volumes: - redis-data:/data healthcheck: test: ["CMD", "redis-cli", "ping"] interval: 10s timeout: 5s retries: 5 networks: - app-network # ─── ChromaDB chroma: 

_Đàm Mạnh Dũng_ 

_56 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

image: chromadb/chroma:latest ports: - "8001:8001" volumes: - chroma-data:/chroma/chroma environment: - IS_PERSISTENT=TRUE - ANONYMIZED_TELEMETRY=FALSE networks: - app-network volumes: postgres-data: redis-data: chroma-data: ai-data: networks: app-network: driver: bridge 

### **_2.5.3. CI/CD với GitHub Actions_** 

### **_Code snippet 8 GitHub Actions CI/CD Workflow_** 

◾ YAML 

# .github/workflows/ci-cd.yml # Pipeline CI/CD: lint → test → build → deploy # Chạy tự động khi push lên develop hoặc main 

name: CI/CD Pipeline on: push: 

_Đàm Mạnh Dũng_ 

_57 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

branches: [main, develop] pull_request: branches: [main, develop] env: NODE_VERSION: '20' PYTHON_VERSION: '3.11' jobs: # ── STAGE 1: Lint lint: name: Lint & Type Check runs-on: ubuntu-latest steps: - uses: actions/checkout@v4 - name: Setup Node.js uses: actions/setup-node@v4 with: node-version: ${{ env.NODE_VERSION }} cache: 'npm' - name: Install dependencies run: npm ci --workspaces - name: ESLint (Frontend) run: npm run lint --workspace=frontend - name: ESLint (Backend) run: npm run lint --workspace=backend - name: TypeScript type check (Frontend) run: npm run type-check --workspace=frontend 

_Đàm Mạnh Dũng_ 

_58 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

- name: TypeScript type check (Backend) run: npm run type-check --workspace=backend - name: Python lint (AI Service) uses: chartboost/ruff-action@v1 with: src: ./ai_service # ── STAGE 2: Test test: name: Unit & Integration Tests runs-on: ubuntu-latest needs: lint services: postgres: image: postgres:16-alpine env: POSTGRES_DB: test_db POSTGRES_USER: test_user POSTGRES_PASSWORD: test_password options: >- --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5 ports: - 5432:5432 redis: image: redis:7-alpine options: >- 

_Đàm Mạnh Dũng_ 

_59 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

--health-cmd "redis-cli ping" --health-interval 10s ports: - 6379:6379 steps: - uses: actions/checkout@v4 - name: Setup Node.js uses: actions/setup-node@v4 with: node-version: ${{ env.NODE_VERSION }} cache: 'npm' - name: Install dependencies run: npm ci --workspaces - name: Run Backend tests run: npm run test:cov --workspace=backend env: DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db REDIS_URL: redis://localhost:6379 JWT_SECRET: test-jwt-secret - name: Check coverage threshold (≥70%) run: npm run test:cov --workspace=backend -- -- coverageThreshold='{"global":{"lines":70}}' - name: Upload coverage report uses: codecov/codecov-action@v4 with: 

_Đàm Mạnh Dũng_ 

_60 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

directory: ./backend/coverage # ── STAGE 3: Build build: name: Build Docker Images runs-on: ubuntu-latest needs: test if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop' steps: - uses: actions/checkout@v4 - name: Set up Docker Buildx uses: docker/setup-buildx-action@v3 - name: Login to GitHub Container Registry uses: docker/login-action@v3 with: registry: ghcr.io username: ${{ github.actor }} password: ${{ secrets.GITHUB_TOKEN }} - name: Build and push Frontend image uses: docker/build-push-action@v5 with: context: ./frontend push: true tags: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }} cache-from: type=gha cache-to: type=gha,mode=max 

_Đàm Mạnh Dũng_ 

_61 DCCTCT67-09B_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

- name: Build and push Backend image uses: docker/build-push-action@v5 with: context: ./backend push: true tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }} cache-from: type=gha cache-to: type=gha,mode=max # ── STAGE 4: Deploy deploy: name: Deploy to Server runs-on: ubuntu-latest needs: build if: github.ref == 'refs/heads/main' environment: production steps: - name: Deploy via SSH uses: appleboy/ssh-action@v1 with: host: ${{ secrets.DEPLOY_HOST }} username: ${{ secrets.DEPLOY_USER }} key: ${{ secrets.DEPLOY_SSH_KEY }} script: | cd /app/dcstructures echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin # Kéo images mới nhất docker pull ghcr.io/${{ github.repository }}/frontend:$ {{ github.sha }} 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_62_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

docker pull ghcr.io/${{ github.repository }}/backend:$ {{ github.sha }} # Cập nhật image tag trong docker-compose export IMAGE_TAG=${{ github.sha }} docker compose up -d --no-deps frontend backend # Chạy database migrations docker compose exec -T backend npx prisma migrate deploy echo "✅ Deploy thành công: ${{ github.sha }}" 

### **Giải thích từng stage CI/CD** 

- Stage Lint: Kiểm tra code style với ESLint (TypeScript) và Ruff (Python), 

- đảm bảo không có lỗi cú pháp hay vi phạm coding convention trước khi chạy test. 

- Stage Test: Chạy toàn bộ unit test và integration test với PostgreSQL và 

- Redis thực (không mock). Đảm bảo coverage ≥ 70% trước khi build. 

- Stage Build: Chỉ chạy khi push vào <mark>main</mark> hoặc <mark>develop</mark> . Build Docker 

- images và push lên GitHub Container Registry với tag là commit SHA. 

- Stage Deploy: Chỉ chạy khi push vào <mark>main</mark> . SSH vào server production, 

- pull image mới, restart containers và chạy database migrations tự động. 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_63_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **CHƯƠNG 3: ĐÁNH GIÁ KẾT QUẢ VÀ ĐỊNH HƯỚNG PHÁT TRIỂN** 

### **3.1. Đánh giá kết quả thực tập** 

### **_3.1.1. Kiến thức từ trường đại học áp dụng được_** 

Quá trình học tập tại Khoa Công nghệ Thông tin, Đại học Mỏ – Địa chất đã trang bị cho em nền tảng vững chắc, tạo điều kiện tiếp cận nhanh với môi trường thực tế tại DC-STRUCTURES VIETNAM. Nhiều môn học trong chương trình đào tạo có liên hệ trực tiếp với công việc tại công ty, dù công nghệ cụ thể có thể khác nhau. 

_Bảng 3- 1 Kiến thức từ trường áp dụng vào thực tập_ 

|**Môn học**|**Kiến thức áp dụng được**|**Mức độ áp**<br>**dụng**|**Ghi chú**|
|---|---|---|---|
|Cơ sở dữ liệu|Thiết kế ERD, chuẩn hóa<br>bảng, viết query SQL phức<br>tạp với JOIN/CTE, hiểu index<br>và query optimization|Cao|Prisma/PostgreSQL<br>dùng trực tiếp|
|Lập trình<br>Web|Hiểu HTTP protocol, REST<br>API, HTML/CSS/JavaScript<br>nền tảng, request-response<br>lifecycle|Cao|Cơ sở để học<br>Next.js nhanh|
|Kỹ thuật lập<br>trình|Tư duy giải thuật, cấu trúc dữ<br>liệu (hash map, tree), phân<br>tích độ phức tạp|Cao|Tối ưu các thuật<br>toán trong service|
|Công nghệ<br>phần mềm|Mô hình Agile/Scrum, git<br>workflow, thiết kế module<br>hóa, SOLID principles|Cao|Áp dụng hàng ngày|
|Mạng máy|TCP/IP, DNS, HTTPS,<br>WebSocket, hiểu cơ chế|Trung bình|Debugging|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_64_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|tính|truyền dữ liệu||network issues|
|---|---|---|---|
|Lập trình<br>hướng đối<br>tượng|Kế thừa, đa hình, interface,<br>design pattern (Repository,<br>Factory, Singleton)|Cao|NestJS dùng<br>DI/IoC|
|Toán học rời<br>rạc|Logic Boolean, tập hợp, đồ<br>thị, lý thuyết xác suất cơ bản|Trung bình|Hiểu cosine<br>similarity, vector<br>math|
|Hệ điều hành|Process, thread, concurrency,<br>memory management|Trung bình|Docker, Node.js<br>async model|
|An toàn<br>thông tin|Authentication, authorization,<br>hash, mã hóa, OWASP Top<br>10|Cao|JWT, bcrypt, input<br>validation|
|Phân tích<br>thiết kế hệ<br>thống|Usecase, sequence diagram,<br>class diagram, phân tích yêu<br>cầu|Cao|Viết tài liệu kỹ<br>thuật|



**Nhận xét:** Những môn học có tính ứng dụng thực tế cao nhất là Cơ sở dữ liệu, Công nghệ phần mềm và Lập trình hướng đối tượng. Kiến thức về HTTP và REST từ môn Lập trình Web là nền tảng không thể thiếu để hiểu NestJS nhanh chóng. Tuy nhiên, có một khoảng cách rõ ràng giữa công nghệ được dạy ở trường (PHP, MySQL truyền thống) và stack hiện đại tại doanh nghiệp (TypeScript, PostgreSQL, Redis) điều này không phải là vấn đề của chương trình đào tạo mà là đặc thù của ngành công nghệ luôn thay đổi nhanh. 

### **_3.1.2. Kiến thức mới tiếp cận tại công ty_** 

Trong 10 tuần thực tập, em đã tiếp cận và học được nhiều công nghệ, kiến thức mới hoàn toàn không có trong chương trình đại học: 

### **_Next.js 14 App Router và Server Components_** 

App Router là bước tiến lớn của Next.js, giới thiệu React Server Components (RSC) một mô hình render hoàn toàn mới. Trước đây, em chỉ biết 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_65_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

CSR (Client-Side Rendering) với React thuần. Tại công ty, em được học cách suy nghĩ về "component nào nên là Server Component, component nào cần là Client Component" đây là kỹ năng quan trọng ảnh hưởng trực tiếp đến hiệu năng ứng dụng. Em cũng học được Streaming với Suspense, giúp trang web hiển thị nội dung từng phần thay vì chờ tất cả load xong mới render. 

### **_NestJS Dependency Injection và IoC Container_** 

Khái niệm Dependency Injection đã được học ở trường nhưng chưa bao giờ thực hành ở quy mô này. NestJS với IoC container giúp em hiểu thực sự tại sao DI lại quan trọng: khi unit test service, có thể mock dependencies dễ dàng mà không cần thay đổi code production. Em cũng học được cách thiết kế module boundary module nào nên expose interface gì, cách import/export giữa các module để tránh circular dependency. 

### **_RAG Pipeline và Vector Database_** 

Đây là phần kiến thức mới nhất và thú vị nhất trong kỳ thực tập. Em chưa từng làm việc với vector embeddings hay semantic search trước đây. Hiểu được rằng câu hỏi "tìm văn bản tương tự" không phải là so sánh chuỗi ký tự mà là so sánh vector trong không gian 1536 chiều đây là sự thay đổi về tư duy lớn. Em cũng học được cách thiết kế prompt để giảm hallucination, cách chunking ảnh hưởng đến chất lượng retrieval. 

### **_Docker và Containerization trong thực tế_** 

Ở trường, em từng cài Docker nhưng chưa thực sự hiểu tại sao nó quan trọng. Sau khi phải debug vấn đề "works on my machine" và được hướng dẫn cách isolate environment bằng container, em mới thực sự thấy giá trị của Docker. Docker Compose multi-service với health checks, named volumes và networking là kỹ năng thực tế rất có giá trị. 

### **_CI/CD với GitHub Actions_** 

Tự động hóa quy trình test → build → deploy là điều em chưa từng làm trước đây. Việc thiết lập pipeline từ đầu, debug các job bị fail trong Actions, hiểu cách cache dependencies để tăng tốc pipeline đây là kỹ năng DevOps cơ bản nhưng 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_66_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

rất cần thiết cho bất kỳ developer nào làm việc trong team. 

### **_Prisma ORM Code-first Database Management_** 

Khác với cách viết SQL thủ công hay dùng Sequelize (Node.js ORM truyền thống), Prisma với schema.prisma và migration system mang lại trải nghiệm developer tốt hơn nhiều. Type safety end-to-end từ schema đến query kết quả, migration version control, seeding data đây là cách làm chuẩn trong các dự án TypeScript hiện đại. 

### **_3.1.3. Kỹ năng đạt được_** 

_Bảng 3- 2 Kỹ năng cứng và kỹ năng mềm mức độ trước và sau thực tập_ 

|**Kỹ năng**|**Loại**|**Trước thực**<br>**tập**|**Sau thực tập**|**Tiến bộ**|
|---|---|---|---|---|
|TypeScript /<br>JavaScript|Cứng|Trung bình|Thành thạo|+2 bậc|
|React / Next.js|Cứng|Cơ bản|Khá tốt|+2 bậc|
|NestJS / Node.js<br>Backend|Cứng|Mới bắt đầu|Khá tốt|+3 bậc|
|PostgreSQL /<br>Prisma|Cứng|Trung bình|Khá tốt|+1 bậc|
|Python /<br>LangChain|Cứng|Cơ bản|Khá tốt|+2 bậc|
|Docker / Docker<br>Compose|Cứng|Biết khái<br>niệm|Thực hành tốt|+3 bậc|
|Git workflow / PR<br>process|Cứng|Cơ bản|Thành thạo|+3 bậc|
|AI/RAG concepts|Cứng|Chưa biết|Hiểu sâu|+4 bậc|
|Unit Testing / TDD|Cứng|Cơ bản|Khá tốt|+2 bậc|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_67_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|GitHub Actions /<br>CI/CD|Cứng|Chưa biết|Thực hành tốt|+4 bậc|
|---|---|---|---|---|
|Đọc hiểu tài liệu<br>kỹ thuật tiếng Anh|Mềm|Khá|Rất tốt|+2 bậc|
|Code review nhận<br>phản hồi|Mềm|Chưa quen|Tự tin|+3 bậc|
|Code review đưa<br>phản hồi|Mềm|Chưa làm|Bước đầu|+3 bậc|
|Giao tiếp trong môi<br>trường chuyên<br>nghiệp|Mềm|Ổn|Tốt|+1 bậc|
|Quản lý thời gian /<br>deadline|Mềm|Trung bình|Tốt|+1 bậc|
|Tự debugging và<br>tìm giải pháp|Mềm|Trung bình|Tự chủ cao|+2 bậc|



### **_3.1.4. Tự đánh giá_** 

### **_Điểm mạnh đã phát huy_** 

Khả năng học nhanh và thích nghi: Trong tuần đầu tiên, em không biết gì về NestJS hay Next.js App Router. Đến tuần 3, em đã có thể tự viết feature hoàn chỉnh mà không cần hỏi mentor về syntax hay API. Khả năng đọc documentation tiếng Anh và áp dụng ngay vào code thực là điểm mạnh được mentor nhận xét tích cực nhất. 

Tư duy cẩn thận, ít bug trong code: Hầu hết các PR của em được approve sau 1–2 vòng review, ít khi có bug nghiêm trọng. Thói quen viết test trước khi submit PR, kiểm tra edge cases và đọc lại code mình viết giúp chất lượng code ổn định. 

Chủ động và không ngại hỏi: Môi trường startup đòi hỏi tự chủ cao. Em đã 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_68_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

hình thành thói quen: tự nghiên cứu trong 30 phút trước khi đặt câu hỏi, nhưng khi thực sự vướng mắc thì chủ động hỏi ngay thay vì mất nhiều thời gian mò mẫm không hiệu quả. Điều này được mentor đánh giá cao. 

### **_Điểm yếu nhận ra và cách khắc phục_** 

Viết test coverage chưa đủ: Ban đầu, em chỉ tập trung viết test cho happy path mà bỏ qua edge cases và error scenarios. Sau khi một bug trong production (môi trường staging) xảy ra ở case <mark>refreshToken</mark> hết hạn đúng lúc gửi request, em nhận ra tầm quan trọng của việc test cả error paths. Từ tuần 7 trở đi, em thêm test cho cả error scenarios trong mọi service mình viết. 

Đặt tên biến và function chưa descriptive: Trong code review tuần 4, mentor chỉ ra nhiều tên hàm và biến quá ngắn hoặc mơ hồ <mark>(data</mark> , <mark>result</mark> , <mark>handleClick</mark> ). Sau đó, em bắt đầu áp dụng nguyên tắc "tên hàm phải nói lên được nó làm gì" và đọc lại code sau 24 giờ để kiểm tra xem có cần đổi tên không. 

Thời gian estimate chưa chính xác: Tuần 6, em ước tính task "Add Redis session management" mất 1 ngày nhưng thực tế mất 2.5 ngày vì có nhiều edge cases về TTL và concurrent invalidation. Bài học: luôn nhân đôi estimate ban đầu, đặc biệt với tasks liên quan đến caching và concurrency. 

### **_Mức độ đáp ứng yêu cầu công việc_** 

Qua đánh giá của mentor và kết quả các sprint review, mức độ đáp ứng yêu 

cầu công việc theo từng tuần: 

|**Giai đoạn**|**Tuần**|**Mức độ**<br>**đáp ứng**|**Nhận xét**|
|---|---|---|---|
|Onboarding|1–2|80%|Học nhanh, setup môi trường không gặp<br>vấn đề lớn|
|Frontend|3–4|85%|Cần review nhiều lần về TypeScript<br>types, nhưng feature hoạt động đúng|
|Backend|5–6|90%|NestJS pattern được áp dụng chuẩn sau<br>khi đọc docs kỹ|



_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_69_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

|AI/RAG|7–8|92%|Vượt kỳ vọng về chất lượng RAG<br>pipeline|
|---|---|---|---|
|Testing & Polish|9–10|95%|Code chủ động, ít cần hướng dẫn|
|**Tổng thể**|**1–10**|**88%**|**Hoàn thành tốt mục tiêu thực tập**|



### **3.2. Định hướng phát triển** 

### **_3.2.1. Hướng phát triển đề tài_** 

Hệ thống xây dựng trong kỳ thực tập là phiên bản MVP (Minimum Viable Product) với các chức năng cốt lõi. Để đưa hệ thống lên production hoàn chỉnh, có nhiều hướng phát triển tiếp theo: 

### **_A. Cải thiện chất lượng RAG_** 

Hybrid Search (Dense + Sparse): Hiện tại, hệ thống chỉ dùng dense vector search (semantic). Kết hợp thêm BM25 (sparse, keyword-based) cho phép tìm kiếm tốt hơn với các từ khóa kỹ thuật (tên hàm, tên biến) mà embedding không giỏi. Thư viện <mark>langchain-community</mark> đã hỗ trợ EnsembleRetriever để kết hợp hai phương pháp. 

Reranking với Cross-encoder: Sau khi retrieval trả về top-K chunks, dùng một Cross-encoder model (nhỏ hơn, như <mark>cross-encoder/ms-marco-MiniLM-L-6-</mark> v2) để rerank lại kết quả. Cross-encoder xem xét query và chunk cùng nhau thay vì so sánh riêng biệt, cho accuracy cao hơn đáng kể. 

Contextual Compression: Thay vì truyền toàn bộ chunk vào prompt, dùng LLM nhỏ để tóm tắt/lọc chỉ giữ phần liên quan đến câu hỏi  giảm token usage và tăng focus của LLM. 

Multi-query Retrieval: Thay vì chỉ embed câu hỏi gốc, dùng LLM sinh ra 3–5 paraphrase khác nhau của câu hỏi, retrieve riêng lẻ rồi merge kết quả. Điều này giúp phủ sóng nhiều cách diễn đạt khác nhau trong tài liệu. 

### **_B. Thêm Multimodal Support_** 

Tài liệu kỹ thuật thường chứa nhiều hình ảnh, diagram và bảng. Phiên bản 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_70_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

MVP chỉ xử lý text. Hướng phát triển tiếp theo: 

- PDF với hình ảnh: Dùng <mark>pymupdf</mark> hoặc <mark>pdfplumber</mark> để extract hình ảnh từ PDF, sau đó dùng Vision model (GPT-4o hoặc Claude 3) để mô tả hình ảnh và đưa vào index. 

- Bảng/Table extraction: Thư viện như <mark>camelot</mark> hoặc <mark>tabula-py</mark> để extract bảng từ PDF sang format có cấu trúc, giúp chatbot trả lời chính xác hơn với câu hỏi về dữ liệu bảng. 

- Diagram understanding: Với architecture diagram, dùng OCR + Vision model để hiểu nội dung và tạo text description để index. 

### **_C. Tối ưu Hiệu năng và Chi phí_** 

Embedding Cache: Tài liệu không thay đổi không cần re-embed. Lưu cache embedding theo document hash, chỉ re-embed khi nội dung thay đổi  giảm 80% chi phí OpenAI embedding khi hệ thống có nhiều tài liệu cũ. 

LLM Cost Optimization: Với câu hỏi đơn giản (FAQ type), có thể dùng câu trả lời cached thay vì gọi LLM mỗi lần. Xây dựng semantic cache: nếu câu hỏi mới có similarity > 0.95 với câu hỏi cũ, trả về câu trả lời cached. 

Streaming Response: Đã implement ở phiên bản hiện tại nhưng chưa hoàn toàn cần tối ưu server-sent events từ NestJS đến frontend để latency cảm nhận (perceived latency) tốt hơn. 

Async Processing Queue: Thay vì trigger AI processing trực tiếp trong HTTP request, dùng BullMQ (Redis-backed job queue) để xử lý document ingestion bất đồng bộ có retry logic và monitoring. 

### **_D. Tính năng Enterprise_** 

Multi-tenant Support: Cho phép nhiều team/department có knowledge base riêng trong cùng một hệ thống, với phân quyền truy cập chặt chẽ. 

Analytics Dashboard: Theo dõi câu hỏi nào được đặt nhiều nhất, tài liệu nào được tham khảo nhiều nhất, câu hỏi nào chatbot không trả lời được (để cải thiện tài liệu). 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_71_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

Feedback Loop: Cho phép user đánh giá câu trả lời , dùng dữ liệu này để fine-tune retrieval strategy và prompt. 

### **3.2.2. Liên kết với Đồ án tốt nghiệp** 

Kỳ thực tập tại DC-STRUCTURES VIETNAM đã mở ra một hướng rõ ràng và hấp dẫn cho Đồ án Tốt nghiệp: 

### **_Đề xuất hướng ĐATN_** 

Đề tài đề xuất: **"Xây dựng hệ thống hỏi đáp thông minh theo tài liệu doanh nghiệp sử dụng Retrieval-Augmented Generation với cơ chế tự đánh giá và cải thiện (Self-RAG)"** 

Điểm khác biệt so với thực tập: Đề tài thực tập là MVP hướng ứng dụng thực tế. ĐATN sẽ đi sâu hơn về mặt nghiên cứu, tập trung vào: 

1. Self-RAG: Mô hình tự đánh giá xem có cần retrieve không (tránh retrieve khi câu hỏi là general knowledge), tự đánh giá chất lượng retrieved chunks, tự đánh giá câu trả lời trước khi trả về user. 

2. Benchmarking: So sánh nhiều chiến lược RAG (naive RAG, advanced RAG, modular RAG) trên dataset tự xây dựng từ tài liệu kỹ thuật tiếng Việt  đóng góp mới vì hầu hết benchmark hiện tại là tiếng Anh. 

3. Multi-document Reasoning: Câu hỏi đòi hỏi tổng hợp thông tin từ nhiều tài liệu theo chuỗi lý luận (chain-of-thought), không chỉ lookup đơn giản. 

### **_Kỹ năng và codebase tái sử dụng_** 

Codebase từ thực tập có thể tái sử dụng trực tiếp: 

- Infrastructure: Toàn bộ Docker setup, CI/CD pipeline, PostgreSQL + 

- Redis + ChromaDB stack có thể reuse 90%. 

- Backend: NestJS authentication, user management, document management modules có thể fork và mở rộng. 

- Frontend: Next.js App Router structure, React Query hooks, Shadcn/UI components tiết kiệm 2–3 tuần setup. 

- AI Pipeline: Document processor, LangChain integration, ChromaDB 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_72_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

client sẽ được nâng cấp lên Self-RAG thay vì xây mới. 

Kỳ thực tập không chỉ cho em kỹ năng kỹ thuật mà còn giúp em thấy rõ những vấn đề thực tế mà RAG hiện tại chưa giải quyết tốt, đây chính là nguồn cảm hứng và động lực tốt nhất để thực hiện một ĐATN có giá trị thực tiễn. 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_73_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **KẾT LUẬN** 

Sau 10 tuần thực tập tại DC-STRUCTURES VIETNAM, em đã hoàn thành tất cả các mục tiêu đề ra với mức độ đáp ứng trung bình 88%. Sản phẩm cuối cùng một nền tảng quản lý tài liệu với AI chatbot  đã được demo thành công trước team vào ngày 11/05/2026 và được bàn giao đầy đủ codebase, tài liệu kỹ thuật cho công ty. 

Khoảng cách giữa kiến thức học thuật và thực tế doanh nghiệp là không nhỏ, nhưng không phải không thể vượt qua. Chìa khóa là tư duy chủ động học hỏi, không ngại sai và luôn tìm cách hiểu sâu "tại sao" thay vì chỉ biết "như thế nào". Những kinh nghiệm tích lũy trong kỳ thực tập này sẽ là nền tảng vững chắc cho hành trình sự nghiệp phía trước. 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_74_ 

_Báo cáo thực tập doanh nghiệp chuyên ngành Công nghệ thông tin_ 

## **TÀI LIỆU THAM KHẢO** 

[1]. Retrieval - Augmented Generation for Knowledge – Intensive NLP Tasks (2020). 

- [2]. Retrieval – Augmented Generation for Large Language Models: A Survey (2023). 

[3]. Self – RAG: Learning to Retrieve, Generate, and Critique through Self – Reflection (2023). 

- [4]. OpenAI – GPT 4 Technical Report 

- [5]. OpenAI – OpenAI API Documentation 

- [6]. LangChain Documentation 

[7]. ChromaDB Documentation 

_Đàm Mạnh Dũng_ 

_DCCTCT67-09B_ 

_75_ 

