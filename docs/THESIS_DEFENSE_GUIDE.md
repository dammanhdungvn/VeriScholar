# VERISCHOLAR — SỔ TAY BÁO CÁO & BẢO VỆ ĐỒ ÁN TỐT NGHIỆP
# (ACADEMIC THESIS & DEFENSE HANDBOOK: ARCHITECTURE, USE CASES & Q&A)

> **Tài liệu đặc biệt:** Biên soạn dành riêng cho tác giả phục vụ việc viết Thuyết minh Đồ án Tốt nghiệp Đại học / Thạc sĩ và chuẩn bị bài thuyết trình, trả lời phản biện trước Hội đồng Chấm Đồ án.
> **Quy chuẩn kỹ thuật:** Mọi liên kết tham chiếu tài liệu nội bộ tuân thủ 100% đường dẫn tương đối (Relative Markdown Links).

---

## Lời Mở Đầu: Cách Sử Dụng Sổ Tay Trong Báo Cáo Đồ Án

Khi viết Báo cáo Đồ án Tốt nghiệp ngành Khoa học Máy tính / Công nghệ Thông tin, sinh viên thường gặp 3 khó khăn lớn:
1. **Quá sa đà vào mã nguồn:** Trình bày dài dòng các đoạn mã nhưng thiếu lý giải tổng quan về mặt kiến trúc phần mềm (Software Architecture).
2. **Thiếu lập luận "Tại sao chọn giải pháp này mà không chọn giải pháp khác?":** Dễ bị Hội đồng đặt câu hỏi xoáy làm lung lay kết quả nghiên cứu.
3. **Thiếu số liệu thực nghiệm chứng minh (Empirical Evidence):** Chỉ mô tả tính năng lý thuyết mà không có dữ liệu đo đạc thực tế về độ trễ, số lượng token, mức độ an toàn mật mã và giám sát hệ thống.

Cuốn sổ tay này được thiết kế theo cấu trúc mô-đun hóa tương ứng với các phân hệ đã triển khai. Ở mỗi phân hệ gồm đúng 4 phần phục vụ trực tiếp cho báo cáo:
- **Mục 1 (Dành cho Chương Tổng quan & Slide thuyết trình):** Diễn giải bằng ngôn ngữ đời thường, dùng các ví dụ trực quan dễ hiểu để người nghe không chuyên về kỹ thuật cũng nắm được giá trị cốt lõi.
- **Mục 2 (Dành cho Chương Phân tích Thiết kế & Kiến trúc):** Luận giải tại sao thành phần này là bắt buộc, nếu loại bỏ thì hệ thống sẽ sập ở đâu, và đâu là thành phần mở rộng linh hoạt.
- **Mục 3 (Dành cho Phiên Phản Biện với Hội Đồng):** Tập hợp các câu hỏi hóc búa nhất mà Thầy/Cô phản biện thường hỏi kèm câu trả lời chuẩn xác, có căn cứ khoa học.
- **Mục 4 (Dành cho Chương Thực Nghiệm & Đánh Giá):** Các số liệu đo lường thực tế, kết quả kiểm thử tự động và nhật ký giám sát từ **Langfuse Cloud**.

---

## Chương 0: Nền Tảng Kiến Trúc 18 Bảng CSDL & Kho Lưu Trữ CAS
*(Tương ứng với Phân hệ Nền tảng: PRD-00 & SPEC-00)*

### 1. Giải Thích Bình Dân & Ẩn Dụ Thực Tế (Chương 0)
Hãy hình dung hệ thống VeriScholar giống như một **Thư viện Quốc gia Số hóa**:
* **18 Bảng Cơ sở dữ liệu (PostgreSQL 16 + pgvector):** Giống như một cuốn sổ cái quản lý gồm 18 ngăn phân loại chuyên biệt. Không chỉ lưu tên tài khoản hay mật khẩu, sổ cái này còn ghi nhớ từng mảnh văn bản nhỏ được cắt ra từ bài báo khoa học kèm theo "tọa độ định vị" chính xác trên trang giấy (từ 0 đến 1000). Khi bạn hỏi AI, hệ thống không chỉ trả lời bằng chữ mà còn chỉ rõ: *"Thông tin này nằm ở trang số 5, cột bên trái, tọa độ x: 120, y: 350"*, giúp khung đọc PDF tự động cuộn đến và vẽ khung viền vàng tô sáng cho người đọc kiểm chứng bằng mắt trong 1 giây.
* **Kho Lưu Trữ CAS (Content-Addressable Storage theo SHA-256):** Giống như thủ thư nhận diện sách bằng "dấu vân tay số" thay vì tên file. 
  * *Ví dụ thực tế:* Một lớp học có 50 sinh viên cùng tải lên bài báo kinh điển *"Attention Is All You Need"* nặng 20MB. Ở các hệ thống thông thường, máy chủ sẽ bị tốn $50 \times 20\text{MB} = 1.000\text{MB}$ ổ cứng. Với VeriScholar, hệ thống tính mã băm SHA-256 của file và nhận ra cả 50 người cùng nạp chung một nội dung, nên **chỉ lưu đúng 1 bản duy nhất trên đĩa (tốn 20MB thay vì 1GB, tiết kiệm 98% dung lượng)**. Tuy nhiên, ghi chú, câu hỏi và phiên làm việc của từng sinh viên vẫn được cách ly độc lập hoàn toàn.

---

### 2. Phân Tích Tại Sao Bắt Buộc Phải Có & Bảng Phân Loại Cốt Lõi / Mở Rộng
Hội đồng thường hỏi: *"Tại sao đồ án của em cần tới 18 bảng CSDL và kho lưu trữ riêng mà không dùng giải pháp đơn giản hơn?"*. Bảng dưới đây phân định rõ:

| Thành phần Kiến trúc | Phân loại | Vai trò Nghiệp vụ | Hậu quả nếu Loại bỏ hoặc Giản lược |
| :--- | :--- | :--- | :--- |
| **CSDL Quan hệ phân vùng `user_id`** | **CỐT LÕI (Bắt buộc)** | Cách ly tài sản nghiên cứu giữa các học giả (`WHERE user_id = :current_user_id`). | **Rò rỉ đề tài nghiên cứu:** Người dùng này có thể xem trộm bản thảo chưa công bố hoặc ghi chú của người dùng khác. |
| **Cột Vector `pgvector` (1536 chiều)** | **CỐT LÕI (Bắt buộc)** | Tìm kiếm ngữ nghĩa phục vụ RAG (Retrieval-Augmented Generation) trực tiếp trong PostgreSQL. | **Mất tính năng hỏi đáp thông minh:** Không thể tìm kiếm đoạn văn liên quan theo ngữ nghĩa mà chỉ tìm được từ khóa thô sơ. |
| **Bảng `document_storage_blobs` & CAS** | **CỐT LÕI (Bắt buộc)** | Quản lý vòng đời file PDF vật lý và đếm số lượng tham chiếu (`ref_count`). | **Tràn ổ cứng & Vi phạm bảo mật:** Ổ cứng đầy do trùng lặp file; khi người dùng bấm xóa tài liệu thì file vẫn còn nằm trôi nổi trên đĩa máy chủ. |
| **Tọa độ Bounding Box (`x0, y0, x1, y1`)** | **CỐT LÕI (Bắt buộc)** | Định vị chính xác vị trí trực quan của từng đoạn trích trên trang PDF. | **Mất điểm nhấn sáng tạo:** Trở thành chatbot hỏi đáp chung chung giống ChatGPT, không thể vẽ khung viền vàng trên bản PDF gốc để kiểm chứng số liệu. |
| **Bộ đệm Redis Cache & Khóa phân tán** | *Mở rộng (Tối ưu hóa)* | Tăng tốc độ truy vấn trạng thái và kiểm soát tần suất gửi OTP. | Hệ thống vẫn chạy được trên PostgreSQL thuần nhưng độ trễ khi có tải cao sẽ chậm hơn. |

---

### 3. Bộ Câu Hỏi & Câu Trả Lời Phản Biện Hội Đồng (Defense Q&A — Chương 0)

> **Câu hỏi 1 của Thầy/Cô:** *"Tại sao em không lưu luôn toàn bộ tệp PDF dưới dạng nhị phân (BYTEA hoặc BLOB) thẳng vào trong một cột của PostgreSQL cho tiện mà lại phải tách ra kho tệp CAS trên hệ thống tệp (Filesystem)?"*
>
> **Gợi ý trả lời bảo vệ:**
> *"Thưa Thầy/Cô, việc lưu trữ tệp nhị phân kích thước lớn (lên tới 50MB mỗi bài báo) trực tiếp vào hàng (row) của CSDL quan hệ là một anti-pattern trong kỹ thuật phần mềm vì 3 lý do:*
> 1. *Gây phình to kích thước cơ sở dữ liệu (Database Bloat), làm chậm nghiêm trọng tốc độ sao lưu dự phòng (pg_dump) và quá trình phục hồi dữ liệu khi có sự cố.*
> 2. *Làm ô nhiễm bộ nhớ đệm (Buffer Pool / Shared Buffers) của PostgreSQL, khiến CSDL phải dọn các chỉ mục (Indexes) và bảng dữ liệu truy vấn nhanh ra ngoài RAM để nhường chỗ cho khối nhị phân PDF.*
> 3. *Với kho tệp CAS 2 tầng (`storage/blobs/ab/cd/hash.pdf`), hệ thống tận dụng trực tiếp Page Cache cực nhanh của Linux Kernel và hỗ trợ Stream nhị phân với HTTP Range Requests để trình duyệt có thể mở xem từng trang PDF mà không cần tải toàn bộ 50MB về máy."*

> **Câu hỏi 2 của Thầy/Cô:** *"Tại sao em chọn PostgreSQL tích hợp tiện ích `pgvector` mà không sử dụng một Vector Database chuyên dụng như Pinecone, Weaviate hay Milvus?"*
>
> **Gợi ý trả lời bảo vệ:**
> *"Thưa Thầy/Cô, em chọn kiến trúc Hợp nhất Cơ sở dữ liệu (Unified Database Architecture) bằng PostgreSQL 16 + pgvector vì:*
> 1. *Tính nhất quán giao dịch (ACID Invariant): Khi học giả xóa một bài báo, giao dịch `DELETE` sẽ đồng thời xóa metadata, các đoạn trích (chunks) và vector embedding trong cùng một transaction. Nếu dùng Vector DB độc lập, hệ thống sẽ rơi vào bài toán Distributed Transaction (Giao dịch phân tán), rất dễ xảy ra tình trạng dữ liệu mồ côi (Vector còn tồn tại nhưng bài báo đã bị xóa).*
> 2. *Tối ưu hóa chi phí và hạ tầng vận hành: Một đồ án MVP hoặc một viện nghiên cứu chỉ cần quản trị duy nhất một cụm PostgreSQL dự phòng, không cần trả phí định kỳ cho các dịch vụ SaaS bên thứ ba."*

> **Câu hỏi 3 của Thầy/Cô:** *"Cơ chế Tiêu hủy Vật lý Tức thì (Zero-Retention) của em hoạt động thế nào khi có nhiều người cùng tải lên một tệp PDF?"*
>
> **Gợi ý trả lời bảo vệ:**
> *"Hệ thống áp dụng thuật toán Đếm tham chiếu (Reference Counting) trên bảng `document_storage_blobs`. Mỗi khi một người dùng tải lên bài báo có cùng mã băm SHA-256, hệ thống chỉ tạo bản ghi `documents` mới trỏ về `blob_id` đó và tăng `ref_count` lên 1. Khi học giả A xóa bài báo của mình, hệ thống giảm `ref_count` đi 1. Chỉ khi `ref_count` chạm đáy bằng 0 (nghĩa là không còn bất kỳ học giả nào trong toàn hệ thống sở hữu tệp này), mã lệnh sẽ kích hoạt tiêu hủy vật lý tệp nhị phân trên đĩa cứng ngay trong cùng chu kỳ xử lý, cam kết bảo vệ quyền riêng tư tuyệt đối cho các công trình chưa công bố."*

---

### 4. Bằng Chứng Thực Nghiệm Đã Chạy & Số Liệu Đo Đạc (Chương 0)
* **Trạng thái thực tế trên CSDL Live:** 18 bảng đã được khởi tạo và kiểm tra cấu trúc trên PostgreSQL 16 (`pgvector`) tại máy chủ phát triển.
* **Thời gian đáp ứng (Readiness Probe):** API endpoint `/health/ready` đo đạc độ trễ kết nối CSDL trung bình đạt **1.66 ms**.
* **Độ bao phủ kiểm thử tự động (Test Suite):** **46/46 bài kiểm thử Backend** (`pytest`) chạy tự động kiểm tra toàn vẹn ranh giới Kiến trúc Lục giác, mô hình CSDL và kho lưu trữ CAS đạt 100% tỷ lệ thành công trong thời gian **0.71 giây**.

---

## Chương 1: Định Danh Học Giả, Mã ORCID & Két Sắt Khóa BYOK
*(Tương ứng với Phân hệ Định danh & Khóa Cá nhân: PRD-01 & SPEC-01)*

### 1. Giải Thích Bình Dân & Ẩn Dụ Thực Tế (Chương 1)
Hệ thống xác thực của VeriScholar không chỉ dừng lại ở chức năng đăng nhập thông thường, mà được ví như **Thẻ Căn Cước Học Thuật** và **Két Sắt Số Cá Nhân**:
* **Duy trì mạch nghiên cứu liên tục (Single-Flight Refresh Queue):** Nhà nghiên cứu thường mở cùng lúc 5 – 10 tab trình duyệt để đối chiếu bài báo. Ở các trang web thông thường, khi mã phiên (Access Token) hết hạn, các tab sẽ gửi đồng loạt nhiều yêu cầu gia hạn dẫn đến xung đột và văng người dùng ra trang đăng nhập. VeriScholar tích hợp cơ chế xếp hàng thông minh: chỉ 1 yêu cầu duy nhất được gửi đi làm mới ngầm, tất cả các tab khác tự động dùng chung token mới mà người dùng không hề bị đứt quãng tư duy đọc hiểu.
* **Két sắt Khóa AI Cá Nhân (BYOK - Bring Your Own Key):** Thay vì bắt buộc học giả phải trả tiền cho nền tảng hoặc sử dụng chung một hạn ngạch AI eo hẹp, VeriScholar cho phép học giả tự gắn mã khóa OpenAI cá nhân của họ. Khóa này được mã hóa bảo mật cấp quân đội (**AES-256-GCM**) trước khi lưu vào ổ cứng, và chỉ giải mã tạm thời trên bộ nhớ RAM đúng vào khoảnh khắc gửi câu hỏi sang OpenAI. Trên màn hình giao diện hay nhật ký hệ thống, khóa luôn được che kín dạng `sk-proj-...rwoA`.

---

### 2. Phân Tích Tại Sao Bắt Buộc Phải Có & Cơ Chế Hybrid Thông Minh
Hội đồng có thể hỏi: *"Người dùng chỉ cần đọc bài báo, tại sao lại phải phức tạp hóa với khóa BYOK và mã ORCID?"*. Bảng phân tích thiết kế làm sáng tỏ:

| Thành phần Tính năng | Bản chất Thiết kế | Lý do Bắt buộc hoặc Ý nghĩa Học thuật |
| :--- | :--- | :--- |
| **Phân quyền & Phiên làm việc (Auth)** | **BẮT BUỘC** | Đảm bảo tính pháp lý và đạo đức nghiên cứu: Không ai được phép truy cập ghi chú, bản thảo luận văn của người khác. |
| **Mã hóa AES-256-GCM cho BYOK** | **BẮT BUỘC (Khi lưu khóa)** | Nếu chỉ lưu dạng văn bản thô (Plaintext), khi cơ sở dữ liệu bị sao lưu hoặc quản trị viên truy cập sẽ làm lộ thẻ tín dụng gắn với tài khoản OpenAI của người dùng. |
| **Cơ chế Hybrid: Hệ thống vs. Cá nhân** | **THIẾT KẾ THÔNG MINH** | **Người dùng mới:** Không cần cấu hình gì cả, hệ thống tự động dùng khóa mặc định `.env` của nền tảng để trải nghiệm ngay.<br>**Nhà nghiên cứu chuyên sâu:** Tự điền khóa BYOK của mình để dùng các mô hình lớn (GPT-4o, reasoning effort cao) mà không bị giới hạn hạn ngạch. |
| **Định danh ORCID iD 16 số** | **CHUẨN QUỐC TẾ** | Mã định danh nhà khoa học toàn cầu (ví dụ: `0000-0002-1825-0097`), tự động đồng bộ họ tên, học hàm, đơn vị công tác sang trang bìa các bản thảo LaTeX xuất bản quốc tế. |

---

### 3. Bộ Câu Hỏi & Câu Trả Lời Phản Biện Hội Đồng (Defense Q&A — Chương 1)

> **Câu hỏi 1 của Thầy/Cô:** *"Tại sao em lại sử dụng thuật toán mã hóa đối xứng AES-256-GCM mà không dùng AES-CBC hay mã hóa bất đối xứng RSA để bảo vệ khóa API cá nhân?"*
>
> **Gợi ý trả lời bảo vệ:**
> *"Thưa Thầy/Cô, em lựa chọn AES-256-GCM (Galois/Counter Mode) vì 2 ưu điểm vượt trội:*
> 1. *Tính năng Xác thực Dữ liệu Tích hợp (Authenticated Encryption with Associated Data - AEAD): Khác với chế độ CBC truyền thống chỉ bảo mật nội dung, chế độ GCM tự động sinh ra một thẻ xác thực (Authentication Tag) 16 bytes. Nếu bất kỳ kẻ tấn công nào chỉnh sửa dù chỉ 1 bit dữ liệu mã hóa trong CSDL, hàm giải mã sẽ phát hiện và từ chối ngay lập tức, ngăn chặn hoàn toàn các cuộc tấn công thay đổi bản mã (Padding Oracle Attack).*
> 2. *Hiệu năng xử lý cao: AES-GCM được hỗ trợ tăng tốc trực tiếp bằng phần cứng trên CPU hiện đại (tập lệnh Intel AES-NI), giúp quá trình giải mã trên RAM diễn ra trong chưa đầy 1 mili-giây, không gây trễ cho luồng hỏi đáp học thuật."*

> **Câu hỏi 2 của Thầy/Cô:** *"Nếu quản trị viên máy chủ hoặc kẻ tấn công chiếm được toàn bộ cơ sở dữ liệu PostgreSQL, họ có lấy cắp được khóa OpenAI của người dùng không?"*
>
> **Gợi ý trả lời bảo vệ:**
> *"Thưa Thầy/Cô, kẻ tấn công hoàn toàn KHÔNG THỂ lấy được khóa gốc. Trong cơ sở dữ liệu chỉ chứa chuỗi byte đã được mã hóa kèm Nonce ngẫu nhiên. Khóa chủ dùng để giải mã (`BYOK_ENCRYPTION_KEY`) là khóa 32 bytes độc lập được lưu trữ an toàn trong biến môi trường máy chủ và bộ nhớ dịch vụ, hoàn toàn tách biệt với máy chủ cơ sở dữ liệu. Không có khóa chủ này, việc giải mã chuỗi AES-256 về mặt toán học là bất khả thi trong thời gian thực tế."*

> **Câu hỏi 3 của Thầy/Cô:** *"Khi gửi dữ liệu giám sát sang nền tảng Langfuse Cloud, em giải quyết bài toán rò rỉ thông tin cá nhân (PII) của học giả như thế nào?"*
>
> **Gợi ý trả lời bảo vệ:**
> *"Hệ thống áp dụng nguyên tắc Bảo vệ Quyền riêng tư Ngay từ Thiết kế (Privacy by Design):*
> 1. *Mã định danh người dùng (`user_id`) trước khi gửi lên Langfuse được băm ẩn danh một chiều qua thuật toán HMAC-SHA256 kết hợp mã bí mật của hệ thống (`user_id_hash`). Trên bảng điều khiển Langfuse chỉ nhìn thấy mã băm 64 ký tự, không thể giải mã ngược về email hay tên thật của học giả.*
> 2. *Khóa API và mã phiên đều đi qua bộ lọc biểu thức chính quy (Secret Scrubber), tự động che dấu thành `sk-[REDACTED]` hoặc `Bearer [REDACTED]` trước khi gửi qua mạng."*

---

### 4. Bằng Chứng Thực Nghiệm Đã Chạy & Đối Chiếu Langfuse Cloud (Chương 1)
Kết quả kiểm thử thực tế giữa hệ thống VeriScholar và nền tảng giám sát **Langfuse Cloud (`https://jp.cloud.langfuse.com`)**:

* **Thực nghiệm Gọi Mô hình Học thuật Thực tế:**
  * Mô hình sử dụng: `gpt-5.4-mini` (OpenAI).
  * Khóa xác thực: Giải mã trực tiếp từ két sắt BYOK AES-256-GCM trên RAM.
  * Thống kê tiêu thụ: **33 input tokens**, **66 output tokens**, tổng cộng **99 tokens** (chi phí: `$0.00032175`, thời gian đáp ứng: **3.32 giây**).
* **Bằng chứng Đối Chiếu Trực Tiếp trên Langfuse Cloud (Project ID: `cmv8ub9jl00nvad0je39ueywo`):**
  * **Trace ID Kiểm Thử Toàn Trình:** `f8d087c559790eafd0812e6293d23a34`
    * Observation Root (`CHAIN`): `b4fbdf75cb408081` (Tên: `verischolar_byok_live_verification`).
    * Observation Giải mã RAM (`SPAN`): `395dc2ede402e218` (Tên: `aes256_gcm_ram_decryption`).
    * Observation Gọi LLM (`GENERATION`): `8adfac608bc3f5bf` (Tên: `openai_byok_scholar_inference`).
  * **Trace ID Tự Động Sinh từ Giao Diện Người Dùng (`UserProfileModal.tsx`):**
    * Cập nhật Profile & Mã hóa BYOK: Trace ID `9423ed4e264360d619c4e0494900f4f5` (Observation `0ccabe70d8234e80`).
    * Hỏi đáp Học thuật SSE: Trace ID `c308e29caa04f439ca0ff1b851412f8b` (Observation `fb498b77123ab13a`).

---

*(Sổ tay này sẽ tiếp tục được cập nhật tự động các Chương 2, 3, 4... sau khi hoàn thành từng phân hệ theo lộ trình phát triển VeriScholar MVP).*
