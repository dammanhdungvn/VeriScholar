# CẨM NANG VẬN HÀNH AI AGENT BIÊN SOẠN BÁO CÁO ĐỒ ÁN TỐT NGHIỆP (AGENTS.md)

> **Cơ sở pháp lý & Tiêu chuẩn ban hành:**  
> - Khoa Công nghệ Thông tin — Trường Đại học Mỏ - Địa chất (HUMG).  
> - Quy chế và Hướng dẫn thực hiện Đồ án Tốt nghiệp Đại học (`report-datn/guide/Huong-dan-viet-DATN.md`).  
> - Bộ Quy chuẩn Kỹ thuật và Định dạng Bất biến XeLaTeX (`report-datn/RULES.md`).  
> - Bản đồ Phân rã Cấu trúc Vi mô và Ngân sách Trang (`report-datn/ROADMAP.md`).  
> - Hiến pháp Hệ thống VeriScholar Monorepo (`.agents/AGENTS.md`).  
>
> **Đề tài tốt nghiệp chính thức:**  
> *Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn*  
> **Sinh viên thực hiện:** Đàm Mạnh Dũng — Lớp: DCCTCT67_09B — MSSV: 2221050359  
> **Giáo viên hướng dẫn:** ThS. Vũ Lan Phương — Bộ môn Công nghệ Thông tin, HUMG  
> **Năm thực hiện:** 2026  

---

## LỜI NÓI ĐẦU & TÔN CHỈ VẬN HÀNH

Tài liệu `AGENTS.md` này là **Cẩm nang Quy trình Thao tác Chuẩn (SOP - Standard Operating Procedure)** và bộ quy tắc vận hành bắt buộc dành cho tất cả các AI Agent tham gia vào toàn bộ vòng đời nghiên cứu, lập đề cương, thiết kế kiến trúc, biên soạn văn bản, hiệu chỉnh kỹ thuật và chuẩn bị bảo vệ Đồ án Tốt nghiệp (ĐATN) ngành Công nghệ Thông tin.

Báo cáo đồ án tốt nghiệp đại học không phải là một tập tài liệu ghi chú phát triển phần mềm nội bộ, mà là một **ấn phẩm học thuật chính thức** chịu sự chế tài nghiêm ngặt của Quy chế Đào tạo Đại học, Tiêu chuẩn đánh giá của Hội đồng chấm luận án và Uy tín khoa học của Nhà trường. Do đó, AI Agent không được phép hoạt động theo cảm tính mà phải tuyệt đối tuân thủ tôn chỉ:

1. **Tuyệt đối trung thực học thuật (Academic Integrity):** Không bịa đặt số liệu thực nghiệm, không sinh trích dẫn ma, không tạo lập cấu trúc cơ sở dữ liệu giả và không tạo facade đối phó kiểm thử.
2. **Kỹ nghệ thực hành chuyên sâu (Engineering Rigor):** Tập trung làm nổi bật năng lực thiết kế kiến trúc, mô hình dữ liệu, thuật toán lõi và kết quả đo lường định lượng có khả năng tái lập (Reproducibility).
3. **Tuân thủ thể thức tuyệt đối (Layout Compliance):** Mọi trang in, bảng biểu, hình vẽ và công thức toán học phải chuẩn xác theo từng milimét theo quy định của Khoa CNTT - ĐH Mỏ - Địa chất.

---

## PHẦN 1: MỤC TIÊU CỐT LÕI, QUY TRÌNH KỸ NGHỆ & KỶ LUẬT ĐATN

### 1.1. Ba Câu Hỏi Cốt Lõi Của Sinh Viên Thực Hiện ĐATN
Mỗi sinh viên và từng AI Agent khi xây dựng bất kỳ chương mục nào của báo cáo bắt buộc phải trả lời trọn vẹn, thuyết phục 3 câu hỏi lớn:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   3 CÂU HỎI HỌC THUẬT CỐT LÕI CỦA ĐỒ ÁN TỐT NGHIỆP               │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. LÀM GÌ? CHO ĐỐI TƯỢNG NÀO? (What & For Whom)                                  │
│    └─► Bối cảnh bài toán, tính cấp thiết, mục tiêu tổng quát/cụ thể, đối tượng   │
│        thụ hưởng, giới hạn phạm vi nghiên cứu (Lời mở đầu & Chương 1).           │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 2. LÀM NHƯ THẾ NÀO? (How to do it)                                               │
│    └─► Cơ sở lý thuyết, công nghệ nền tảng, luận giải "Tại sao chọn", quy trình  │
│        5 bước kỹ nghệ, kiến trúc hệ thống, CSDL, Use Case (Chương 2 & Chương 3). │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 3. KẾT QUẢ RA SAO? (What are the results & Impact)                               │
│    └─► Kết quả cài đặt, hình ảnh giao diện, minh chứng đo lường định lượng thực  │
│        nghiệm, đánh giá ưu/nhược điểm, hướng mở rộng (Chương 4 & Kết luận).     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

1. **Câu hỏi 1: "Làm gì? Cho đối tượng nào?" (Chương 1 & Lời mở đầu):**
   - Xác định rõ hiện trạng thực tế, khó khăn tồn tại của đối tượng nghiên cứu (học giả, nghiên cứu sinh, giảng viên).
   - Định nghĩa bài toán khoa học: Hỗ trợ khám phá bài báo hai tầng tin cậy, đọc sâu với đối soát tọa độ khung viền vàng (Bounding Box IoU $\ge 0{,}85$ / $0.85$), xây dựng đồ thị tri thức GraphRAG 4 thực thể và biên soạn LaTeX tự sửa lỗi trong sandbox MicroVM.
   - Xác định ranh giới và phạm vi giải pháp (Scope & Boundary), chỉ rõ những gì hệ thống giải quyết và những gì nằm ngoài phạm vi đề tài.

2. **Câu hỏi 2: "Làm như thế nào?" (Chương 2 & Chương 3):**
   - Trình bày cơ sở khoa học, lý luận, mô hình toán học và công nghệ nền tảng.
   - Bắt buộc đưa ra luận chứng khoa học khẳng định lý do lựa chọn giải pháp này thay vì giải pháp cạnh tranh khác (*Justification-Driven*).
   - Thể hiện chi tiết quy trình 5 bước kỹ nghệ: Phân tích yêu cầu $\rightarrow$ Thiết kế kiến trúc/CSDL $\rightarrow$ Cài đặt $\rightarrow$ Kiểm thử $\rightarrow$ Hiệu chỉnh.

3. **Câu hỏi 3: "Kết quả ra sao?" (Chương 4 & Kết luận):**
   - Trình bày kết quả cài đặt và triển khai thực tế trên hạ tầng cụm máy chủ.
   - Đưa ra các bằng chứng định lượng khách quan: bộ kiểm thử 580 tests chạy trong 13.02 giây, độ trễ truy vấn CSDL 1.66 ms, thời gian sinh token đầu tiên TTFT < 1.5 giây, tỷ lệ tự sửa lỗi biên dịch $\ge 90\%$.
   - Đối chiếu trung thực với mục tiêu ban đầu; thẳng thắn nêu bật các điểm hạn chế tồn đọng.

---

### 1.2. Quy Trình 5 Bước Kỹ Nghệ Phần Mềm Kinh Điển
Tại Chương 3 của đồ án, toàn bộ phương pháp giải quyết bài toán bắt buộc phải diễn giải theo đúng chu trình 5 bước kỹ nghệ phần mềm:

1. **Bước 1 — Phân tích yêu cầu (Requirements Analysis):** Khảo sát nghiệp vụ thực tế của học giả, xác định các tác nhân (Actors: *Người dùng học thuật, Tác nhân AI ReAct, Hệ thống lưu trữ, Quản trị viên*), lập danh sách và ma trận 30 ca sử dụng (Use Cases) chuẩn BA.
2. **Bước 2 — Thiết kế hệ thống (System Design):**
   - *Kiến trúc phần mềm:* Áp dụng Kiến trúc Lục giác (Hexagonal Architecture) phân tách độc lập tầng Core nghiệp vụ, tầng Ports giao tiếp và tầng Adapters hạ tầng.
   - *Kiến trúc dữ liệu:* Thiết kế mô hình CSDL quan hệ và vector chuẩn hóa gồm đúng 20 bảng SQLAlchemy thực tế; lập sơ đồ quan hệ thực thể ERD và Từ điển dữ liệu (Data Dictionary).
   - *Hành vi tương tác:* Xây dựng biểu đồ tuần tự UML (Sequence Diagrams) cho các luồng nghiệp vụ cốt lõi.
   - *Giao diện người dùng (UI/UX):* Thiết kế giao diện khoa học, tuân thủ nguyên lý tối giản Radical Minimalism.
3. **Bước 3 — Cài đặt hệ thống (Implementation):** Hiện thực hóa mã nguồn Backend (FastAPI, LangGraph StateGraph, PostgreSQL `pgvector`, Redis cache), Frontend (Next.js App Router, Tailwind CSS, SSE streaming) và môi trường thực thi an toàn E2B MicroVM.
4. **Bước 4 — Kiểm thử hệ thống (Verification & Testing):** Thực thi chiến lược Lập trình hướng kiểm thử (TDD), vượt qua 4 Cổng kiểm định chất lượng: Unit Test, Integration Test, Linting/Type Checking, và Production Build.
5. **Bước 5 — Hiệu chỉnh và tối ưu hóa (Refinement & Optimization):** Tinh chỉnh tham số thuật toán ($k=60$ trong RRF, ngưỡng Jaccard $\ge 0{,}20$, Louvain resolution), xử lý ngoại lệ biên, tối ưu hóa bộ đệm và hoàn thiện theo phản hồi của GVHD.

---

### 1.3. Kế Hoạch 10 Tuần Chi Tiết & Cột Mốc Tuần 6 (Mid-term Checkpoint)
Kế hoạch tiến độ thực hiện ĐATN được thiết lập nghiêm ngặt trong 10 tuần (khớp với lịch trình chính thức từ ngày 24/08/2026 đến ngày 02/11/2026):

| Tuần | Khoảng Thời Gian | Trọng Tâm Nhiệm Vụ | Đầu Ra / Bằng Chứng Bắt Buộc |
| :---: | :---: | :--- | :--- |
| **Tuần 1** | 24/08 -- 30/08/2026 | Nhận đề tài, khảo sát bài toán thực tế, thu thập và đọc tài liệu tham khảo nền tảng. Lập đề cương chi tiết ĐATN. | Đề cương chi tiết và kế hoạch 10 tuần được GVHD phê duyệt và ký thông qua. |
| **Tuần 2** | 31/08 -- 06/09/2026 | Khảo sát quy trình nghiên cứu học thuật; xác định tác nhân, xây dựng biểu đồ Use Case tổng thể và đặc tả chi tiết các Use Case chính. | Sơ đồ Use Case tổng quan, bảng đặc tả Use Case chuẩn BA (Mục 3.4). |
| **Tuần 3** | 07/09 -- 13/09/2026 | Nghiên cứu cơ sở lý thuyết (Hexagonal, RAG, GraphRAG); thiết kế kiến trúc hệ thống và thiết kế CSDL quan hệ/vector. | Bản thảo Chương 2, sơ đồ ERD và bảng từ điển CSDL 20 bảng (Mục 3.6). |
| **Tuần 4** | 14/09 -- 20/09/2026 | Thiết kế giao diện UI/UX tối giản; xây dựng các biểu đồ tuần tự UML cho luồng xác thực, nạp tài liệu CAS và hỏi đáp tri thức. | 4 biểu đồ tuần tự UML (Mục 3.5), wireframe/mockup các màn hình chức năng. |
| **Tuần 5** | 21/09 -- 27/09/2026 | Khởi tạo cấu trúc monorepo; cài đặt tầng Core nghiệp vụ, cơ chế băm CAS SHA-256, két sắt mã hóa khóa BYOK AES-256-GCM. | Mã nguồn tầng Core, test suite xác thực bảo mật và lưu trữ vượt qua 100%. |
| **Tuần 6** | **28/09 -- 04/10/2026** | **CỘT MỐC ĐÁNH GIÁ TIẾN ĐỘ GIỮA KỲ (MID-TERM CHECKPOINT):**<br>• *Kỹ thuật lõi:* Hiện thực hóa động cơ truy xuất lai Hybrid RAG (Dense + BM25) kết hợp thuật toán RRF $k=60$ và thuật toán phân tách tài liệu 2 cột `mid_x`.<br>• *Học thuật & Kỷ luật:* Báo cáo toàn bộ tiến độ giữa kỳ với GVHD; rà soát khối lượng công việc hoàn thành. GVHD đánh giá tiến độ sinh viên. Nếu sinh viên không duy trì báo cáo hoặc không gặp GVHD tính đến mốc này, GVHD và Bộ môn sẽ ghi nhận vi phạm để xem xét đình chỉ tư cách bảo vệ! | Báo cáo tiến độ Tuần 6; demo chạy thực nghiệm thuật toán truy xuất lai; biên bản xác nhận tiến độ giữa kỳ của GVHD. |
| **Tuần 7** | 05/10 -- 11/10/2026 | Hiện thực hóa phân hệ nâng cao: Đồ thị tri thức học thuật 4 thực thể (GraphRAG), Tác nhân ReAct LangGraph và sandbox MicroVM tự vá lỗi LaTeX. | Thuật toán phân cụm Louvain, đồ thị tri thức trên PostgreSQL, sandbox E2B. |
| **Tuần 8** | 12/10 -- 18/10/2026 | Xây dựng giao diện Frontend hoàn chỉnh: Trình xem PDF hỗ trợ khung viền vàng Bounding Box, trình soạn thảo LaTeX và luồng truyền tải SSE. | Ứng dụng Web hoàn chỉnh kết nối API thời gian thực, hiển thị trực quan dữ liệu. |
| **Tuần 9** | 19/10 -- 25/10/2026 | Tích hợp hệ thống toàn trình; chạy toàn bộ 4 Cổng kiểm định chất lượng (Unit, Lint, Boundary, Build); viết hoàn thiện bản thảo báo cáo ĐATN. | Toàn văn bản thảo đồ án (Chương 1--4, Kết luận, TLTK); 580 tests đạt trạng thái PASS. |
| **Tuần 10** | 26/10 -- 02/11/2026 | Đo đạc chỉ số thực nghiệm trên tập bài báo thật; nộp đồ án cho GVHD duyệt và ký xác nhận; nộp bản thảo về Bộ môn (hạn chót 02/11/2026); chuẩn bị slide và bảo vệ thử. | 03 quyển đồ án bìa mềm có chữ ký GVHD; slide thuyết trình; video demo sản phẩm; thư mục bản mềm `MSSV_HoTen_Khoa`. |

---

### 1.4. Ý Thức Kỷ Luật & 4 Điều Kiện Đình Chỉ Bảo Vệ Tốt Nghiệp
Căn cứ Quy chế của Trường Đại học Mỏ - Địa chất (`Huong-dan-viet-DATN.md`, dòng 29--50):

* **Nghĩa vụ gặp GVHD hàng tuần:** Sinh viên có trách nhiệm bắt buộc phải **gặp GVHD định kỳ hàng tuần** để báo cáo kết quả công việc đã thực hiện trong tuần, trình bày vướng mắc kỹ thuật và xin ý kiến chỉ đạo cho tuần tiếp theo. Sinh viên phải chủ động thống nhất điều kiện, phương tiện và địa điểm làm việc; có ý thức bảo quản tài sản, máy móc và chấp hành nghiêm kỷ luật lao động.
* **4 Điều kiện Hội đồng Bộ môn ra quyết định ĐÌNH CHỈ BẢO VỆ ĐỒ ÁN:**
  1. Sinh viên **chưa thanh toán hết các khoản nợ** đối với Nhà trường (học phí, sách thư viện, các khoản lệ phí hành chính).
  2. Sinh viên trong suốt quá trình làm đồ án **không gặp GVHD sau lần giao nhiệm vụ đầu tiên**, hoặc **hàng tuần không báo cáo tiến độ làm việc với GVHD**.
  3. Sinh viên **không nộp đồ án đúng thời hạn quy định** của Bộ môn và Nhà trường.
  4. **Giáo viên hướng dẫn đánh giá đồ án không đạt yêu cầu**.

---

### 1.5. Quy Cách Nộp Lưu Trữ Bản Cứng & Bản Mềm
Quy cách nộp lưu trữ sản phẩm ĐATN được chuẩn hóa đồng bộ 2 hình thức:

1. **Bản cứng (Hard Copy):**
   - *Trước khi bảo vệ:* Sinh viên nộp **03 quyển đồ án đóng bìa mềm có chữ ký xác nhận của GVHD**:
     - 02 quyển nộp cho Bộ môn (01 quyển gửi Hội đồng chấm, 01 quyển gửi Giảng viên phản biện).
     - 01 quyển nộp cho GVHD.
   - *Sau khi bảo vệ:* Sinh viên tiếp thu, chỉnh sửa và hoàn thiện toàn bộ nội dung đồ án theo đúng kết luận/góp ý của Hội đồng chấm. Sau đó đóng **01 quyển bìa cứng in chữ mạ nhũ vàng** (đầy đủ dấu tiếng Việt, trình bày trang nhã theo mẫu Phụ lục 01) nộp cho Bộ môn để lưu trữ vĩnh viễn trong thư viện khoa học.

2. **Bản mềm (Soft Copy — Phương tiện lưu trữ số/quang):**
   - Sinh viên nộp cho Bộ môn bản mềm lưu trữ toàn bộ sản phẩm đồ án đặt trong **duy nhất 01 thư mục gốc**.
   - **Quy chuẩn đặt tên thư mục:** Bắt buộc tuân theo định dạng: `MãSinhViên_HọTên_Khóa` (viết liền không dấu hoặc gạch dưới chuẩn hóa).
     - *Ví dụ mẫu quy chế:* `1821050189_NguyenVanAnh_K63`
     - *Định danh thực tế của đề tài:* `2221050359_DamManhDung_DCCTCT67_09B` (hoặc `2221050359_DamManhDung_K67`).
   - **Cấu trúc dữ liệu bên trong thư mục bản mềm:**
     - `BaoCao_ToanVan.pdf`: Toàn văn file báo cáo đồ án hoàn chỉnh xuất bản từ XeLaTeX (bao gồm cả trang bìa, mục lục, sơ đồ, nội dung, phụ lục).
     - `Slide_BaoVe.pdf` (hoặc `.pptx`): Bản trình chiếu báo cáo trước Hội đồng.
     - `SourceCode/`: Toàn bộ mã nguồn chương trình có thể chạy được, cấu trúc monorepo sạch sẽ, có tệp `README.md` hướng dẫn cài đặt và khởi chạy.
     - `Data_and_Tests/`: Dữ liệu bài báo mẫu, kịch bản kiểm thử tự động và nhật ký đo lường thực nghiệm.

---

## PHẦN 2: BỐ CỤC TOÀN VĂN & QUY CHUẨN ĐỊNH DẠNG XELATEX

### 2.1. Trật Tự Bố Cục Chuẩn Mực Toàn Văn Quyển Đồ Án
Căn cứ Mục B.I, B.II `Huong-dan-viet-DATN.md`, toàn văn quyển đồ án phải sắp xếp theo đúng trình tự phân đoạn:

```
+─────────────────────────────────────────────────────────────────────────────────────────+
│                       TRẬT TỰ BỐ CỤC TOÀN VĂN QUYỂN ĐỒ ÁN TỐT NGHIỆP                    │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ [FRONTMATTER — PHẦN ĐẦU KHÓA] (Đánh số trang La Mã thường: i, ii, iii...)               │
│  1. Trang bìa ngoài (Bìa chính — in chữ nhũ vàng theo Mẫu Phụ lục 01)                  │
│  2. Trang bìa trong (Bìa phụ — theo Mẫu Phụ lục 02, có chữ ký GVHD & SVTH)             │
│  3. Phiếu giao đề tài tốt nghiệp (Nhiệm vụ ĐATN có xác nhận Bộ môn & GVHD)              │
│  4. Đề cương thực hiện đồ án tốt nghiệp (Kế hoạch 10 tuần chi tiết)                     │
│  5. Lời cảm ơn                                                                          │
│  6. Tóm tắt đồ án (Abstract tiếng Việt / tiếng Anh — nếu có)                            │
│  7. Mục lục                                                                             │
│  8. Danh mục các ký hiệu và chữ viết tắt (sắp xếp theo thứ tự bảng chữ cái ABC)         │
│  9. Danh mục các bảng (LoT — Bảng X.Y)                                                  │
│ 10. Danh mục các hình vẽ, đồ thị (LoF — Hình X.Y)                                       │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ [MAIN BODY — NỘI DUNG CHÍNH] (Bắt đầu đánh số trang Ả Rập: 1, 2, 3...)                  │
│ 11. Mở đầu / Lời mở đầu (Bối cảnh, tính cấp thiết, mục tiêu, đối tượng, phạm vi)        │
│ 12. Chương 1: Mô tả bài toán / Tổng quan về đề tài                                      │
│ 13. Chương 2: Cơ sở lý thuyết và công nghệ về vấn đề cần giải quyết                     │
│ 14. Chương 3: Phương pháp, quy trình thực hiện giải quyết bài toán                      │
│ 15. Chương 4: Kết quả thực nghiệm và đánh giá                                           │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ [BACKMATTER — PHẦN KẾT THÚC] (Tiếp tục đánh số trang Ả Rập)                             │
│ 16. Kết luận & Hướng phát triển (Đóng góp đạt được, hạn chế, 3 hướng mở rộng)          │
│ 17. Danh mục tài liệu tham khảo (Phân nhóm Việt trước, Anh sau; N_refs <= 20)           │
│ 18. Phụ lục (Mã nguồn thuật toán, biểu mẫu, nhật ký — CẤM dày hơn phần chính)           │
+─────────────────────────────────────────────────────────────────────────────────────────+
```

---

### 2.2. Toàn Bộ Quy Chuẩn Định Dạng Bắt Buộc (Typography Standards)
Mọi tệp cấu hình và chế bản XeLaTeX trong `report-datn/` phải tuân thủ nghiêm ngặt các thông số hình học:

1. **Khổ giấy & Căn lề trang (Geometry):**
   - Khổ giấy: **A4 chuẩn** ($210 \times 297\,\text{mm}$), in trên một mặt giấy trắng.
   - **Lề trên (Top):** đúng **$2{,}5\,\text{cm}$**.
   - **Lề dưới (Bottom):** đúng **$2{,}5\,\text{cm}$**.
   - **Lề trái (Left — gáy sách):** đúng **$3{,}5\,\text{cm}$** (chừa khoảng cách bắt buộc để đóng gáy bìa cứng mạ nhũ vàng không bị che khuất văn bản).
   - **Lề phải (Right):** đúng **$2{,}5\,\text{cm}$**.
   - $\rightarrow$ **Chiều rộng thân bài khả dụng:** Đúng **$15{,}0\,\text{cm}$** ($21{,}0 - 3{,}5 - 2{,}5 = 15{,}0\,\text{cm}$).
2. **Phông chữ, Dãn dòng & Thụt lề:**
   - Phông chữ tiêu chuẩn: `Times New Roman` (hoặc `Liberation Serif` tương đương nạp qua `fontspec` hỗ trợ đầy đủ 144 biến thể dấu tiếng Việt Unicode UTF-8).
   - Cỡ chữ thân bài (Body text): Đúng **13pt**.
   - Mật độ chữ: Bình thường, tuyệt đối **không được nén hoặc kéo dãn khoảng cách giữa các chữ**.
   - Dãn dòng (Line spacing): Đặt ở chế độ **1.5 lines** (`\onehalfspacing`) thống nhất toàn bài.
   - Thụt lề đầu dòng (First-line Indent): Chuẩn **$1{,}0\,\text{cm}$** (`\setlength{\parindent}{1.0cm}`).
   - Căn lề đoạn văn: Căn đều hai bên lề (Justified).
3. **Quy tắc đánh số trang:**
   - **Vị trí:** Đánh ở **dưới, phía bên phải mỗi trang giấy** (`\fancyfoot[R]`).
   - **Hệ số trang:**
     - Phần mở đầu (Frontmatter): Đánh số bằng **chữ số La Mã thường** (`i, ii, iii, iv...`).
     - Phần nội dung chính (từ Lời cảm ơn / Lời mở đầu / Chương 1 đến hết Kết luận, TLTK, Phụ lục): Đánh số bằng **chữ số Ả Rập** (`1, 2, 3...`).
   - Hình thức: In đứng thông thường, không trang trí rườm rà.

---

### 2.3. Ma Trận Phân Cấp Cỡ Chữ & Tiêu Đề Văn Bản
Bảng phân định kích thước, kiểu dáng và vị trí của từng thành phần văn bản:

| Cấp Bậc / Thành Phần | Cỡ Chữ (Size) | Định Dạng (Style) | Căn Lề | Khoảng Cách Trước / Sau | Cấu Hình Kỹ Thuật Trong XeLaTeX |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Bìa ngoài / Bìa trong** | 16pt | In hoa, Đậm | Giữa | Theo mẫu phụ lục | `\fontsize{16}{20}\selectfont\bfseries` |
| **Nhãn "ĐỒ ÁN TỐT NGHIỆP"** | 32pt -- 40pt | In hoa, Đậm | Giữa | Nổi bật giữa trang | `\fontsize{36}{44}\selectfont\bfseries` |
| **Tiêu đề Chương (`\chapter`)** | 16pt | In hoa, Đậm | Giữa | Trước 0pt, Sau 18pt | `\titleformat{\chapter}[block]` |
| **Mục cấp 1 (`\section` X.Y)** | 14pt | In đậm | Trái | Trước 12pt, Sau 6pt | `\titleformat{\section}` |
| **Tiểu mục cấp 2 (`\subsection` X.Y.Z)** | 13pt | In đậm | Trái | Trước 9pt, Sau 4pt | `\titleformat{\subsection}` |
| **Tiểu mục cấp 3 (`\subsubsection` X.Y.Z.W)** | 13pt | In đậm nghiêng | Trái | Trước 6pt, Sau 3pt | `\titleformat{\subsubsection}` |
| **Thân bài (Body text)** | **13pt** | Thường, dãn dòng 1.5 | Đều 2 bên | Thụt lề 1.0cm | `\usepackage[fontsize=13pt]{scrextend}` |
| **Tiêu đề Bảng (`\caption` trên)** | 12pt | Nhãn Đậm, Tên Nghiêng | Giữa | Trên bảng, cách 6pt | `\captionsetup[table]{position=top}` |
| **Tiêu đề Hình (`\caption` dưới)** | 12pt | Nhãn Đậm, Tên Nghiêng | Giữa | Dưới hình, cách 6pt | `\captionsetup[figure]{position=bottom}` |
| **Header & Footer** | 10pt | Header Đậm, Footer Nghiêng | Trái / Phải | Cách mép giấy 1.5--2.0cm | `\fontsize{10}{12}\selectfont` |
| **Chú thích chân trang (`\footnote`)** | 10pt | Thường, dãn đơn | Đều 2 bên | Dưới chân trang | `\fontsize{10}{13}\selectfont` |

---

### 2.4. Quy Tắc Phân Cấp Đề Mục & Luật Bất Biến Cấm Tiểu Mục Đơn Lẻ
1. **Độ sâu phân cấp tối đa 4 cấp:** Các tiểu mục được đánh số thành nhóm số nhiều nhất gồm 4 chữ số: `Chương.Mục.TiểuMục.Nhóm` (ví dụ `4.1.2.1` chỉ tiểu mục 1 nhóm tiểu mục 2 mục 1 chương 4). Tuyệt đối không đánh số cấp thứ 5 (như `3.1.2.1.1`).
2. **LUẬT BẤT BIẾN CẤM TIỂU MỤC ĐƠN LẺ (NO SINGLETON SUBSECTIONS):**
   - Tại mỗi nhóm tiểu mục bắt buộc phải có **ít nhất hai tiểu mục**. Quy tắc cấm tiểu mục đơn lẻ (singleton subsection rule) yêu cầu mỗi nhóm phải có tối thiểu 2 mục con.
   - Nghĩa là: **Tuyệt đối không thể có tiểu mục `2.1.1` mà không có tiểu mục `2.1.2` tiếp theo**. Nếu một nội dung không đủ để phân chia thành 2 tiểu mục con độc lập, bắt buộc phải viết trực tiếp dưới mục cha `2.1` mà không đánh số phân cấp!
3. **Danh ngữ hóa tiêu đề & Độ dài chuẩn mực (3 đến 7 từ):**
   - Mọi tiêu đề mục từ cấp 1 đến cấp 4 phải là một cụm danh từ cô đọng, định danh trực diện đối tượng khoa học/kỹ thuật.
   - Tuyệt đối cấm tiêu đề dạng mệnh đề kể lể mở đầu bằng động từ (*"Nghiên cứu về..."*, *"Tìm hiểu giải pháp..."*, *"Hiện thực hóa luồng..."*).
4. **Chống tiêu đề mồ côi (No Orphan Headings):** Tuyệt đối cấm để tiêu đề mục nằm trơ trọi ở dòng cuối cùng của trang in mà không có ít nhất 2-3 dòng văn bản thân bài đi kèm bên dưới. Sử dụng `\nopagebreak` hoặc điều chỉnh dãn cách.
5. **Độ sâu hiển thị Mục lục (ToC Depth):** Mục lục chỉ hiển thị đến cấp 2 hoặc cấp 3 (`\setcounter{tocdepth}{2}`) để giữ sự tinh tế, trang nhã.

---

### 2.5. Quy Chuẩn Bảng Biểu, Hình Vẽ, Công Thức Toán & Cấm Dẫn Chiếu Tương Đối
1. **Đánh số đối tượng gắn liền với số chương:**
   - Mọi hình vẽ, bảng biểu, công thức toán phải đánh số theo định dạng hai chữ số: `Hình X.Y`, `Bảng X.Y`, `Công thức (X.Y)`. Trong đó $X$ là số thứ tự chương và $Y$ là số thứ tự đối tượng trong chương đó (ví dụ: `Bảng 3.4` là bảng thứ 4 trong Chương 3).
2. **Quy tắc vị trí đặt đầu đề (Caption Placement Invariant):**
   - **ĐẦU ĐỀ BẢNG BIỂU: BẮT BUỘC ĐẶT Ở PHÍA TRÊN BẢNG**.
   - **ĐẦU ĐỀ HÌNH VẼ: BẮT BUỘC ĐẶT Ở PHÍA DƯỚI HÌNH**.
   - Vi phạm vị trí đầu đề bảng/hình bị coi là lỗi định dạng nghiêm trọng bị trừ điểm trực tiếp trong quy chế chấm đồ án.
3. **LUẬT TUYỆT ĐỐI CẤM THAM CHIẾU TƯƠNG ĐỐI (NO RELATIVE CITATIONS):**
   - Khi dẫn giải đến bất kỳ hình vẽ, bảng biểu hoặc công thức nào trong bài, **bắt buộc phải gọi đích danh mã định danh chính xác**: `"kết quả được tổng hợp trong Bảng 4.2"`, `"(xem Hình 3.1)"`, `"tính toán theo Công thức (2.3)"`.
   - **TUYỆT ĐỐI CẤM SỬ DỤNG CÁC CỤM TỪ TƯƠNG ĐỐI NHƯ:**
     - ❌ *"như trong hình dưới đây"*
     - ❌ *"kết quả ở bảng sau"*
     - ❌ *"trong sơ đồ trên"*
     - ❌ *"như bảng ngay sau đây"*
   - *Lý do khoa học:* Trong chế bản in ấn, hình ảnh và bảng biểu là các đối tượng trôi dạt (Floats), có thể tự động nhảy sang trang tiếp theo; việc dùng tham chiếu tương đối làm mất tính chính xác khoa học.
4. **Kỹ nghệ bảng biểu nâng cao (Advanced Tabular Engineering):**
   - Mọi bảng có chứa nội dung văn bản dài, đặc tả nghiệp vụ hoặc từ điển CSDL bắt buộc phải sử dụng môi trường `tabularx` với độ rộng đúng bằng `\textwidth` (`\begin{tabularx}{\textwidth}{|...|}`).
   - Sử dụng cột loại `X` (hoặc `>{\raggedright\arraybackslash}X`) để bảng tự động ngắt dòng chữ, tuyệt đối không dùng cột `l` hay `c` khiến dòng chữ bị đâm thủng lề phải $15{,}0\,\text{cm}$.
   - **Quy chuẩn kẻ khung viền đồ án:** Bảng phải có khung viền khép kín 4 góc ngoài (`|...|`) và các đường kẻ ngang `\hline` phân cách từng dòng theo đúng mẫu ĐATN truyền thống (tuyệt đối không dùng bảng hở cạnh `booktabs` như `\toprule`, `\midrule`, `\bottomrule` gây đứt đoạn vạch kẻ dọc).
   - Nếu bảng quá dài phải ngắt qua trang, bảng ở trang mới phải có dòng tiêu đề cột lặp lại kèm nhãn `Bảng X.Y (tiếp theo)`.
5. **Kỹ nghệ sơ đồ chuẩn Paper khoa học quốc tế (Human-Centric Academic Paper Architecture & 7 Nguyên Tắc Vàng):**
   - **Kiến trúc cho người đọc, không phải cho máy đọc:** Mọi sơ đồ kiến trúc và mô tả hệ thống trong báo cáo đồ án (đặc biệt tại Chương 2 và Chương 3) phải được thiết kế theo tư duy của các bài báo khoa học quốc tế uy tín (như mô hình Transformer Attention, kiến trúc RAG, GraphRAG của cộng đồng nghiên cứu).
   - **Tập trung vào dòng chảy tri thức và khối thuật toán:** Thể hiện rõ nét luồng biến đổi dữ liệu toán học (*Dataflow & Knowledge Transformation*), các khối chức năng trừu tượng hóa mức độ cao (*Embedding, Retrieval, Rank Fusion, Reasoning Loop*), tuyệt đối cấm vẽ sơ đồ kiểu máy móc (class diagram với getter/setter, endpoint REST, đường dẫn code, thao tác CRUD vụn vặt). Sơ đồ phải đóng vai trò là một mô hình tư duy học thuật (*Academic Mental Model*) tự giải thích, giúp người đọc nắm bắt ngay đóng góp khoa học và tính mới của đề tài.
   - **7 Nguyên Tắc Vàng TikZ:**
     - (1) *Tối giản ruột node:* Tối đa 2 dòng văn bản trong một khối chức năng (`\textbf{Tên}`, `\scriptsize (Ký hiệu)`).
     - (2) *Kích thước cố định:* Luôn khai báo `text width` và `minimum height` tường minh.
     - (3) *Bố cục phân dải màu:* Gom nhóm bằng khung bao màu pastel bo tròn góc (`rounded corners=8pt`).
     - (4) *Định tuyến trực giao:* Mũi tên góc vuông `|-` hoặc `-|`, tuyệt đối cấm vẽ đường xiên chéo cắt qua mặt chữ.
     - (5) *Hành lang độc lập:* Các luồng song song hoặc phản hồi phải cách nhau tối thiểu $\Delta y \ge 0{,}6\,\text{cm}$.
     - (6) *Nhãn mũi tên cách ly:* Nhãn trên đường vẽ bắt buộc có nền trắng `fill=white` để không bị đè vạch kẻ.
     - (7) *Khổ giấy an toàn:* Khai báo `scale=0.74` đến `0.80`, bảo đảm chiều ngang sơ đồ luôn $\le 15{,}0\,\text{cm}$.
6. **Công thức toán học & Trình bày độ đo:**
   - Công thức căn giữa trên dòng riêng, đánh số thứ tự trong ngoặc đơn đặt sát lề phải `(X.Y)`.
   - Ngay sau công thức, bắt buộc có mệnh đề giải nghĩa toàn bộ biến số (*"Trong đó: $A$ là...; $B$ là..."*).
   - Biến số đơn ký tự in nghiêng (`$q, d$`); ký hiệu vector/ma trận in đậm (`\mathbf{u}`); tên độ đo nhiều ký tự bắt buộc bọc trong `\text{...}` hoặc `\operatorname{...}`: $\text{IoU} \ge 0{,}85$, $\text{RRF}(d)$, $\text{BLEU}$, $\text{F1-score}$.
   - Số thập phân tiếng Việt phải bọc dấu phẩy trong ngoặc nhọn: `$0{,}85$`, `$1{,}66\,\text{ms}$` để tránh khoảng trắng toán học.

---

### 2.6. Quy Chuẩn Từ Viết Tắt & Danh Mục Tài Liệu Tham Khảo
1. **Quy tắc sử dụng từ viết tắt:**
   - Chỉ viết tắt những thuật ngữ chuyên ngành được sử dụng nhiều lần trong đồ án.
   - Không lạm dụng viết tắt; không viết tắt những cụm từ dài hoặc mệnh đề.
   - **Tuyệt đối cấm viết tắt trong tên chương và tên mục chính**.
   - Lần đầu xuất hiện trong bài: Phải viết đầy đủ thuật ngữ kèm chữ viết tắt trong ngoặc đơn. Ví dụ: *Cơ sở dữ liệu (CSDL)* hoặc *Retrieval-Augmented Generation (RAG)*.
   - Bảng *Danh mục các ký hiệu và chữ viết tắt* ở phần Frontmatter bắt buộc phải sắp xếp theo **thứ tự bảng chữ cái ABC**.
2. **Quy chuẩn sắp xếp Danh mục Tài liệu tham khảo (Phụ lục 3 HUMG):**
   - **Phân nhóm ngôn ngữ bắt buộc:** Phân tách rõ ràng thành 2 nhóm:
     - `I. Tài liệu tiếng Việt` (đặt lên đầu tiên).
     - `II. Tài liệu tiếng Anh` (và tiếng nước ngoài khác đặt sau).
   - **Bảo toàn nguyên văn:** Tài liệu tiếng nước ngoài phải giữ nguyên văn, không phiên âm, không dịch.
   - **Thứ tự sắp xếp bảng chữ cái ABC:**
     - Tác giả Việt Nam: Xếp thứ tự ABC theo **TÊN** của tác giả, nhưng **giữ nguyên thứ tự thông thường Họ Tên** (ví dụ: *"Nguyễn Đình Thúc"* xếp vần T, không được đảo thành *"Thúc, Nguyễn Đình"*).
     - Tác giả nước ngoài: Xếp thứ tự ABC theo **HỌ (Surname)** của tác giả (ví dụ: *"Vaswani A."* xếp vần V).
     - Tài liệu không có tên tác giả cá nhân: Xếp thứ tự ABC theo chữ cái đầu của **tên cơ quan ban hành** ấn phẩm (ví dụ: *Bộ Giáo dục và Đào tạo* xếp vần B).
   - **Quy cách trình bày thông tin:**
     - *Sách, đồ án, giáo trình:* Tên tác giả (Năm xuất bản), *Tên sách/đồ án (in nghiêng)*, Nhà xuất bản, Nơi xuất bản.
     - *Bài báo tạp chí, kỷ yếu hội thảo:* Tên tác giả (Năm công bố), "Tên bài báo (ngoặc kép, đứng)", *Tên tạp chí/kỷ yếu (in nghiêng)*, Tập(Số), Các số trang.
   - **Quy cách thụt lề dòng thứ hai (Hanging Indent):** Nếu tài liệu dài hơn 1 dòng, từ **dòng thứ hai trở đi bắt buộc lùi vào $1{,}0\,\text{cm}$** so với dòng thứ nhất để danh mục rõ ràng, chuyên nghiệp.
   - **Giới hạn số lượng tài liệu tham khảo ($\le 20$):**
     - Toàn bộ danh mục tài liệu tham khảo bắt buộc phải thỏa mãn: $\mathbf{0 < N_{\text{refs}} \le 20}$.
     - Tuyệt đối không nhồi nhét tài liệu rác để kéo dài số lượng. Chỉ trích dẫn các công trình nền tảng có bình duyệt (Peer-reviewed) và tài liệu quy chế chính thức.
   - **Cấm tuyệt đối trích dẫn mồ côi (Zero Orphan References):** 100% tài liệu liệt kê trong danh mục cuối bài bắt buộc phải được dẫn chiếu trực tiếp bằng lệnh `\cite{...}` (dạng `[1]`, `[2]`) ít nhất một lần trong phần nội dung thân bài.

---

### 2.7. Tỷ Lệ Phân Bổ Nội Dung Vàng (Content Golden Ratio)
Dựa trên khảo sát thực tế các ĐATN đạt điểm Xuất sắc tại Khoa CNTT - HUMG, phân bổ dung lượng báo cáo bắt buộc phải tuân theo **Tỷ Lệ Phân Bổ Vàng**:

$$\mathbf{Lý\ thuyết\ (Chương\ 1\ +\ Chương\ 2)\ \le\ 30\%} \quad \Big\vert \quad \mathbf{Thiết\ kế\ \&\ Thực\ nghiệm\ (Chương\ 3\ +\ Chương\ 4)\ \ge\ 70\%}$$

```
+─────────────────────────────────────────────────────────────────────────────────────────+
│              MA TRẬN PHÂN BỔ DUNG LƯỢNG & SỐ TRANG CHUẨN MỰC (50 -- 65 TRANG)           │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ Khối Nội Dung          │ Mục Tiêu Trọng Tâm               │ Ngân Sách Trang │ Tỷ Lệ %  │
+────────────────────────┼──────────────────────────────────┼─────────────────┼──────────+
│ Lời mở đầu & Chương 1  │ Bối cảnh, mục tiêu, phạm vi      │ 6 -- 8 trang    │ ~12%     │
│ Chương 2               │ Cơ sở lý thuyết & Why-chosen     │ 10 -- 12 trang  │ ~18%     │
│ ──► TỔNG LÝ THUYẾT     │ Khảo sát & Nền tảng khoa học     │ 16 -- 20 trang  │ <= 30%   │
+────────────────────────┼──────────────────────────────────┼─────────────────┼──────────+
│ Chương 3               │ 5 bước kỹ nghệ, Use Case, CSDL   │ 18 -- 24 trang  │ ~40%     │
│ Chương 4               │ Cài đặt, UI, 580 tests, đo lường │ 12 -- 16 trang  │ ~26%     │
│ Kết luận & Hướng đi    │ Đóng góp đạt được & Hướng mở rộng│ 2 -- 3 trang    │ ~4%      │
│ ──► TỔNG THỰC HÀNH     │ Kỹ nghệ hệ thống & Thực nghiệm   │ 32 -- 43 trang  │ >= 70%   │
+────────────────────────┼──────────────────────────────────┼─────────────────┼──────────+
│ TỔNG QUY MÔ BÁO CÁO    │ Ruột nội dung chính              │ 50 -- 65 trang  │ 100%     │
+─────────────────────────────────────────────────────────────────────────────────────────+
```

---

## PHẦN 3: NGUYÊN TẮC VẬN HÀNH CHO AI AGENT & HÀNG RÀO PHÒNG NGỪA 7 ANTI-PATTERNS

### 3.1. Năm Nguyên Tắc Vận Hành Bất Biến Cho AI Agent

#### Nguyên Tắc 1: Tháp Thẩm Quyền Học Thuật & Chân Lý Duy Nhất (Single Source of Truth)
Khi có sự sai lệch hoặc mâu thuẫn thông tin giữa các tài liệu, AI Agent bắt buộc phải tuân thủ thứ bậc thẩm quyền:
$$\mathbf{Quy\ chế\ HUMG\ \&\ RULES.md} = \mathbf{Mã\ nguồn\ thực\ tế\ \&\ Test\ Pass} > \mathbf{Tài\ liệu\ specs/docs/} > \mathbf{Suy\ luận\ nội\ suy\ của\ AI}$$
*AI Agent tuyệt đối không tự bịa đặt tính năng, thông số hiệu năng hoặc cấu trúc bảng CSDL mà không có trong mã nguồn thực tế hoặc bài kiểm thử đã pass.*

#### Nguyên Tắc 2: Kỷ Luật Ngữ Cảnh Vi Mô (Micro-Modular Context Discipline)
Một quyển đồ án 65 trang chứa hàng chục nghìn dòng LaTeX. Nếu nạp toàn bộ báo cáo vào Context Window sẽ gây hiện tượng "ảo giác vị trí" (*Lost in the Middle*) và dễ gây lỗi sửa lan (*Collateral Damage*).
*Agent chỉ được phép nạp duy nhất 1 tệp vi mô `.tex` mục tiêu kết hợp tệp chỉ mục điều hướng `report-datn/ROADMAP.md`. Tuyệt đối không đọc toàn bộ báo cáo trong một tác vụ đơn lẻ.*

#### Nguyên Tắc 3: Biên Soạn XeLaTeX Phòng Thủ (Defensive XeLaTeX Editing)
XeLaTeX là trình biên dịch nghiêm ngặt; một lỗi ký tự chưa thoát có thể làm đổ vỡ toàn bộ chu trình build:
- **Thoát ký tự nhạy cảm:** Mọi ký tự `\_`, `\%`, `\&`, `\#`, `\$`, `\{`, `\}` xuất hiện trong văn bản thường, tên biến (`user\_id`, `paper\_id`), tên trường CSDL bắt buộc phải thoát dấu gạch chéo ngược hoặc bọc trong `\texttt{...}`.
- **Bất biến nhãn tham chiếu (`\label{...}` Invariance):** Tuyệt đối không xóa, đổi tên hoặc sửa nhãn của các Hình (`fig:...`) và Bảng (`tab:...`) đã được xác lập trong hệ thống kiểm thử tự động (như `tab:uc_01_spec`, `fig:hexagonal_arch`, `fig:react_agent_loop`, `tab:monorepo_structure`).
- **Cấm để lộ mã thô:** Trong mọi bản nháp duyệt trước, trích dẫn phải hiển thị chuẩn dạng số `[1]`, `[2]`, tuyệt đối không để lộ mã LaTeX thô như `\cite{...}. T`.

#### Nguyên Tắc 4: Lập Luận "Tại Sao Chọn" (Justification-Driven)
Khác với tài liệu hướng dẫn kỹ thuật thông thường, đồ án đại học đòi hỏi tư duy phản biện khoa học. Khi giới thiệu bất kỳ công nghệ hoặc giải pháp nào ở Chương 2, AI Agent không chỉ nêu khái niệm mà bắt buộc phải trả lời câu hỏi cốt tử của Hội đồng: *"Tại sao đề tài chọn giải pháp này mà không chọn giải pháp khác?"*:
- Nêu rõ bản chất lý thuyết và nguyên lý hoạt động.
- Lập bảng so sánh đa tiêu chí với các giải pháp cạnh tranh.
- Đưa ra đoạn văn khẳng định lý do lựa chọn gắn chặt với ràng buộc bài toán (ví dụ: chọn PostgreSQL `pgvector` thay vì Pinecone để đảm bảo ACID và bảo mật on-premise; chọn Hybrid RAG với RRF $k=60$ để cân bằng giữa từ khóa hiếm và ngữ nghĩa khái quát).

#### Nguyên Tắc 5: Văn Phong Khách Quan & Kim Tự Tháp Minto
- **Ngôi văn khách quan chuẩn mực:** Tuyệt đối cấm sử dụng đại từ nhân xưng ngôi thứ nhất (*"tôi"*, *"em"*, *"chúng tôi"*, *"chúng em"*). Toàn bộ nội dung dùng ngôi thứ ba học thuật: *"tác giả"*, *"đề tài"*, *"nghiên cứu này"*, *"hệ thống VeriScholar"*.
- **Danh ngữ hóa tiêu đề:** Mọi tiêu đề mục từ cấp 2 đến cấp 4 phải là cụm danh từ cô đọng từ 3 đến 7 từ. Cấm mở đầu tiêu đề bằng động từ kể lể.
- **Cấu trúc đoạn văn Minto Pyramid:** Câu đầu đoạn (Topic sentence) nêu trực diện luận điểm cốt lõi; các câu tiếp theo đưa ra số liệu, công thức, bảng so sánh đối chứng; câu cuối chốt ý nghĩa và dẫn chiếu chéo `Hình~\ref{...}` hoặc `Bảng~\ref{...}`.

---

### 3.2. Hàng Rào Phòng Ngừa 7 Anti-Patterns Học Thuật (AP-01 đến AP-07)
Nhằm triệt tiêu triệt để các lỗi thường gặp của AI khi biên soạn tài liệu học thuật, ma trận 7 Anti-Patterns và hàng rào phòng vệ được thiết lập:

| Mã | Anti-Pattern Cần Triệt Tiêu | Biểu Hiện Vi Phạm Của AI | Hậu Quả Học Thuật | Hàng Rào Bảo Vệ Bắt Buộc (Guardrail) |
| :---: | :--- | :--- | :--- | :--- |
| **AP-01** | **Chép lý thuyết giáo trình chung chung (Wikipedia / Textbook Dump)** | Dành 5-7 trang chép định nghĩa chung về Docker, Python, PostgreSQL, REST API, React mà không gắn với bài toán. | Làm loãng hàm lượng khoa học; Hội đồng đánh giá sao chép giáo trình, trừ điểm năng lực. | **Hàng rào Giới hạn Định nghĩa & Móc nối Kiến trúc:**<br>• Định nghĩa cơ bản $\le 2$ đoạn văn.<br>• Bắt buộc có phần "Luận giải lựa chọn kỹ thuật trong VeriScholar".<br>• Tuân thủ nghiêm ngặt bảng lọc OMIT/KEEP tại Phần 5 của `RULES.md`. |
| **AP-02** | **Rò rỉ chi tiết mã nguồn vào Chương 2 (Source Code Spillover into Ch2)** | Chèn đường dẫn file repo (`packages/core/...`), tên interface code (`IAcademicSearchResolverPort`) vào Chương 2. | Vi phạm nguyên tắc phân tách ranh giới học thuật giữa Lý thuyết (Ch2) và Thiết kế/Cài đặt (Ch3/Ch4). | **Hàng rào Cách ly Học thuật Chương 2 (Chapter 2 Isolation):**<br>• Chương 2 chỉ trình bày mô hình toán học, nguyên lý thuật toán và kiến trúc khái niệm.<br>• Kiểm tra tự động bằng bài test `test_thesis_chapter2_academic_purity`. |
| **AP-03** | **Dán mã nguồn thô hàng trăm dòng (Raw Source Code Dumps)** | Sao chép nguyên khối code TypeScript/Python dài hàng chục, hàng trăm dòng từ repo vào thân bài để "kéo trang". | Biến đồ án thành tệp in code; vi phạm nghiêm trọng tính cô đọng học thuật. | **Hàng rào Trích dẫn Tinh gọn:**<br>• Cấm dán code thô quá 15-20 dòng trong thân bài.<br>• Chỉ dùng mã giả giải thuật (`algorithm2e`) hoặc khối hàm logic hạt nhân.<br>• Toàn bộ code đầy đủ chuyển vào Phụ lục hoặc đĩa mềm. |
| **AP-04** | **Số liệu thực nghiệm bịa đặt / Ảo giác chỉ số (Hallucinated Metrics)** | AI tự điền các con số không có thật: "độ chính xác đạt 99.8%", "thời gian phản hồi 0.001s", "đã kiểm thử 10.000 ca". | Gian lận học thuật; sinh viên sẽ bị trượt ngay khi Hội đồng yêu cầu mở log kiểm chứng. | **Hàng rào Bằng chứng Đo lường Thực tế (Empirical Proof):**<br>• Mọi số liệu trong Chương 4 phải khớp 100% với output thật: 580 tests (340 Pytest + 240 Vitest) trong 13.02s, DB latency 1.66ms, TTFT < 1.5s, IoU $\ge 0{,}85$ ($0.85$), Langfuse Trace ID. |
| **AP-05** | **Trích dẫn ma & Thổi phồng số lượng tài liệu (Phantom & Bloated References)** | AI tự bịa bài báo không tồn tại, hoặc thêm 50-60 tài liệu từ blog không rõ nguồn gốc để làm danh mục đồ sộ. | Vi phạm liêm chính khoa học quốc tế; dễ bị phát hiện qua Google Scholar. | **Hàng rào Trần Tham Chiếu Tinh Hoa:**<br>• Bắt buộc số lượng tài liệu tham khảo $N_{\text{refs}} \le 20$.<br>• Chỉ trích dẫn bài báo gốc (Vaswani 2017, Cormack 2009, Gao 2023, Blondel 2008...).<br>• Cấm trích dẫn mồ côi (100% ref đều phải có `\cite` trong thân bài). |
| **AP-06** | **Thiết kế CSDL & Sơ đồ "ma" không thể tái lập (Irreproducible Architecture)** | Vẽ sơ đồ hoặc khai báo bảng CSDL không có thật trong code (như 4 bảng ảo `extracted_figures`, `latex_compilations`...). | Đồ án không có tính tái lập (*Non-reproducible*); không thể bảo vệ trước câu hỏi kỹ thuật. | **Hàng rào Đồng bộ Schema 1:1:**<br>• Bắt buộc mô tả đúng 20 bảng SQLAlchemy thực tế.<br>• Đúng tên khóa ngoại (`FK -> document_storage_blobs(id)`).<br>• Đúng thuật toán thực tế (`mid_x` phân tách 2 cột, Jaccard $\ge 0{,}20$, Louvain). |
| **AP-07** | **Sơ đồ ríu rít, đâm thủng lề & Bảng biểu vỡ khung (Visual Overflow & Clutter)** | Vẽ TikZ mũi tên xiên chéo cắt qua mặt chữ, bảng dài vượt quá lề phải 15cm, tạo ra trang trắng mồ côi. | Báo cáo in ra bị lỗi hình thức nghiêm trọng, mất thẩm mỹ chuyên nghiệp. | **Hàng rào 7 Nguyên Tắc Vàng TikZ & Tabularx:**<br>• Bề rộng sơ đồ $\le 15{,}0\,\text{cm}$, scale 0.74 -- 0.80.<br>• Định tuyến góc vuông (`\|-`), nhãn nền trắng `fill=white`.<br>• Bắt buộc dùng `tabularx` có viền khép kín `\|...\|`. |

---

### 3.3. Đảm Bảo Tính Tái Lập (Reproducibility) Với Số Liệu Khóa Cứng
Để bảo đảm tính tái lập khoa học, bất kỳ học giả hoặc kỹ sư nào đọc báo cáo cũng có thể dựng lại chính xác hệ thống dựa trên các tham số kỹ thuật được khóa cứng:
1. **Kiến trúc phần mềm:** Kiến trúc Lục giác phân lập 3 tầng, chuẩn hóa mô hình monorepo với `packages/core` (miền thuần khiết), `apps/api` (FastAPI), `apps/web` (Next.js 14).
2. **Cơ sở dữ liệu vật lý:** Chuẩn hóa đúng **20 bảng SQLAlchemy thực tế**, bao gồm:
   - *Quản lý người dùng & phân quyền (3 bảng):* `users`, `scholar_profiles`, `user_api_keys`.
   - *Tài liệu & Lập chỉ mục CAS (5 bảng):* `document_storage_blobs`, `documents`, `document_chunks`, `document_summaries`, `reference_items`.
   - *Phiên làm việc & Tương tác Agentic (5 bảng):* `folders`, `research_sessions`, `session_documents`, `session_turns`, `research_notes`.
   - *Đồ thị tri thức GraphRAG (4 bảng):* `graph_nodes`, `graph_edges`, `folder_community_summaries`, `wiki_pages`.
   - *Bản thảo nghiên cứu & Soạn thảo LaTeX (3 bảng):* `drafts`, `draft_assets`, `draft_messages`.
   *(Loại bỏ vĩnh viễn 4 bảng giả định: `extracted_figures`, `extracted_tables`, `draft_sections`, `latex_compilations`).*
3. **Thuật toán hạt nhân:**
   - Thuật toán phân tích bố cục PDF 2 cột dựa trên trục hoành `mid_x = 250` và phân nhóm đoạn văn.
   - Thuật toán truy xuất lai Hybrid RAG: Kết hợp Vector Cosine HNSW 1536 chiều và BM25 toàn văn với hàm xếp hạng dung hợp:
     $$\text{RRF}(d) = \sum_{m \in \{\text{dense}, \text{bm25}\}} \frac{1}{60 + r_m(d)}$$
   - Thuật toán trích xuất đồ thị tri thức 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) và phân cụm phát hiện cộng đồng Louvain đa tỷ lệ.
   - Thuật toán đối soát tọa độ khung viền vàng Bounding Box với chỉ số giao trên hợp:
     $$\text{IoU}(B_{\text{pred}}, B_{\text{gt}}) = \frac{|B_{\text{pred}} \cap B_{\text{gt}}|}{|B_{\text{pred}} \cup B_{\text{gt}}|} \ge 0{,}85 \quad (\text{IoU} \ge 0.85)$$
   - Chu trình sửa lỗi cú pháp LaTeX ReAct StateGraph tự động vá lỗi trong sandbox E2B MicroVM đạt tỷ lệ thành công $\ge 90\%$.
4. **Bộ số liệu thực nghiệm khóa cứng:**
   - Tổng số bài kiểm thử tự động: **580 tests** (340 Pytest + 240 Vitest), hoàn thành trong **13.02 giây** (13,02 giây).
   - Độ trễ kết nối cơ sở dữ liệu: **$1{,}66\,\text{ms}$** (1,66 ms / 1.66 ms).
   - Thời gian sinh token đầu tiên (TTFT): **$< 1{,}5\,\text{giây}$** (< 1.5 giây).
   - Bộ giám sát thực nghiệm: Tích hợp Langfuse Cloud theo dõi trực tiếp Trace ID, Token Usage và Latency.

---

## PHẦN 4: HỆ THỐNG 6 PERSONA CHUYÊN BIỆT CHO AI AGENT

Nhằm vận hành quy trình phát triển và hoàn thiện đồ án tốt nghiệp một cách chuyên nghiệp, đề xuất mô hình cộng tác gồm **6 Nhân diện Agent chuyên biệt** với ranh giới trách nhiệm rõ ràng:

```
                      ┌─────────────────────────────────────────┐
                      │        thesis-planner (Chỉ huy)         │
                      │        Quản lý Roadmap & Budget         │
                      └────────────────────┬────────────────────┘
                                           │ Phân công nhiệm vụ vi mô
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│ thesis-researcher│             │ thesis-architect │             │  thesis-writer   │
│  (Nghiên cứu &   │             │ (Kiến trúc Sư &  │             │  (Biên soạn văn  │
│  Cơ sở lý thuyết)│             │  Đặc tả hệ thống)│             │   phong học thuật│
└────────┬─────────┘             └────────┬─────────┘             └────────┬─────────┘
         │ Bản nháp lý thuyết              │ Sơ đồ/Bảng BA                 │ Bản thảo .tex vi mô
         └─────────────────────────────────┼─────────────────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       thesis-reviewer (Kiểm định)       │
                      │       Liêm chính & Thẩm định học thuật  │
                      └────────────────────┬────────────────────┘
                                           │ Đạt chuẩn nội dung
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       thesis-formatter (Chế bản)        │
                      │       Định dạng & Biên dịch XeLaTeX     │
                      └─────────────────────────────────────────┘
```

### 1. `thesis-planner` (Tác tử Lập kế hoạch & Điều phối Bố cục)
- **Trách nhiệm chính:** Quản trị tệp chỉ mục `report-datn/ROADMAP.md`; giám sát ngân sách số trang (Page Budget) từng chương đảm bảo tổng quy mô 50 -- 65 trang chuẩn mực; theo dõi tiến độ theo Kế hoạch 10 tuần của HUMG; bảo đảm 3 câu hỏi cốt lõi ("Làm gì? Làm thế nào? Kết quả ra sao?") được phân bổ cân đối.
- **Hàng rào tuân thủ:** Không trực tiếp viết nội dung kỹ thuật; điều phối phân rã tác vụ theo từng mục vi mô; kiểm soát tiến độ chạm mốc Tuần 6 (Mid-term Checkpoint).

### 2. `thesis-researcher` (Tác tử Nghiên cứu Học thuật & Cơ sở Khoa học)
- **Trách nhiệm chính:** Phụ trách Chương 1 (Bối cảnh, tính cấp thiết, mục tiêu) và Chương 2 (Cơ sở lý thuyết và công nghệ); trích xuất các công thức toán học chính xác (công thức RRF, Cosine Similarity, Louvain, IoU); chọn lọc danh mục tài liệu tham khảo tinh hoa ($N_{\text{refs}} \le 20$); soạn thảo lập luận "Tại sao chọn" cho từng công nghệ.
- **Hàng rào tuân thủ:** Tuyệt đối cấm đưa đường dẫn file code (`packages/`, `apps/`, `src/`) và tên interface nội bộ vào Chương 2; bảo đảm mọi tài liệu đều có `\bibitem` chuẩn IEEE/HUMG và được dẫn chiếu ít nhất 1 lần trong thân bài.

### 3. `thesis-architect` (Tác tử Kiến trúc Sư & Phân tích Nghiệp vụ BA)
- **Trách nhiệm chính:** Phụ trách Chương 3 (Phân tích và Thiết kế hệ thống); đọc hiểu mã nguồn thực tế tại `packages/core`, `apps/api`, `apps/web` để trích xuất thiết kế thực tế; xây dựng bảng đặc tả 30 Use Case chuẩn BA; thiết kế biểu đồ tuần tự UML; thiết kế CSDL 20 bảng quan hệ và vector; phác thảo sơ đồ kiến trúc chuẩn paper quốc tế theo 7 Nguyên tắc vàng TikZ.
- **Hàng rào tuân thủ:** Bảo đảm tính tái lập 100% (schema phải khớp với SQLAlchemy models; luồng tuần tự phải khớp với endpoints API thực tế; loại bỏ 4 bảng giả định).

### 4. `thesis-writer` (Tác tử Biên soạn Văn phong Học thuật)
- **Trách nhiệm chính:** Hiện thực hóa các ý tưởng, công thức và sơ đồ thành các tệp `.tex` vi mô hoàn chỉnh; duy trì văn phong khoa học khách quan ngôi thứ ba; áp dụng danh ngữ hóa tiêu đề (3-7 từ) và cấu trúc đoạn văn Minto Pyramid; xử lý thoát toàn bộ ký tự đặc biệt trong XeLaTeX (`\_`, `\%`...).
- **Hàng rào tuân thủ:** Cấm xưng hô cảm tính (*"tôi"*, *"em"*, *"chúng tôi"*); cấm tiêu đề dạng kể lể (*"Nghiên cứu về..."*); cấm ngắt trang tùy tiện `\clearpage`.

### 5. `thesis-reviewer` (Tác tử Kiểm định Chất lượng & Liêm chính Học thuật)
- **Trách nhiệm chính:** Đóng vai trò Hội đồng phản biện độc lập; rà soát tính nhất quán giữa các chương; kiểm tra các Anti-Patterns (phát hiện rò rỉ mã nguồn ở Ch2, phát hiện bảng CSDL giả, phát hiện số liệu bịa đặt); đối chiếu số liệu ở Chương 4 với output thật của test suite (580 tests, 13.02s); chạy các bài kiểm thử `test_thesis_rules.py`.
- **Hàng rào tuân thủ:** Từ chối thông qua bất kỳ bản thảo nào có trích dẫn mồ côi, vi phạm trần 20 tài liệu tham khảo hoặc số liệu không có căn cứ thực nghiệm.

### 6. `thesis-formatter` (Tác tử Chế bản & Kỹ nghệ Định dạng XeLaTeX)
- **Trách nhiệm chính:** Chịu trách nhiệm về hình thức thẩm mỹ trang in và sự toàn vẹn của mã XeLaTeX; kiểm soát căn lề 2.5-2.5-3.5-2.5cm, phông chữ Times New Roman 13pt, dãn dòng 1.5; kiểm soát tỷ lệ scale của TikZ không quá 15cm; định dạng bảng `tabularx` khép kín viền ngoài; triệt tiêu trang trắng mồ côi và tiêu đề mồ côi; biên dịch XeLaTeX 2 lần để cập nhật số trang và mục lục không lỗi.
- **Hàng rào tuân thủ:** Bắt buộc `main.log` không có cảnh báo undefined references và `main.pdf` được sinh ra hoàn chỉnh.

---

## PHẦN 5: GIAO THỨC TƯƠNG TÁC TỆP AN TOÀN & QUY TRÌNH PHỐI HỢP

### 5.1. Quy Trình 6 Bước Thao Tác Tệp XeLaTeX An Toàn
Để loại bỏ nguy cơ xung đột mã nguồn, vỡ định dạng và lãng phí token ngân sách, bất kỳ AI Agent nào khi thực hiện nhiệm vụ đều phải tuân thủ nghiêm ngặt quy trình 6 bước:

```
BƯỚC 1: Đọc ROADMAP.md & Xác định Tệp Vi mô Mục tiêu
   │
   ▼
BƯỚC 2: Nạp Ngữ cảnh Tối thiểu (Chỉ đọc Tệp Vi mô + Tài liệu Tham chiếu Cần thiết)
   │
   ▼
BƯỚC 3: Biên soạn / Hiệu chỉnh (Tuân thủ Thoát Ký tự Nhạy cảm & Bất biến Nhãn)
   │
   ▼
BƯỚC 4: Biên dịch Thử nghiệm XeLaTeX 2 Lần (cd report-datn && xelatex main.tex)
   │
   ▼
BƯỚC 5: Chạy Bộ Kiểm tra Tự động (test_thesis_rules.py & test_tables_and_spacing.py)
   │
   ▼
BƯỚC 6: Cập nhật Trạng thái ROADMAP.md & Lập Báo cáo Bàn giao (Handoff Report)
```

1. **Bước 1 — Định vị tệp vi mô:** Đọc `report-datn/ROADMAP.md` để xác định chính xác tệp `.tex` cần thao tác (ví dụ: `chapters/ch3/3_4_phan_tich_usecase.tex`).
2. **Bước 2 — Nạp ngữ cảnh tối thiểu:** Chỉ mở tệp vi mô mục tiêu và các tệp spec tham chiếu trực tiếp. Tuyệt đối không đọc toàn bộ báo cáo vào prompt.
3. **Bước 3 — Biên soạn phòng thủ:** Thực hiện sửa đổi bằng các công cụ chỉnh sửa chính xác (`replace_file_content`). Luôn kiểm tra thoát dấu gạch dưới `\_` trong tên biến/trường CSDL; bảo toàn nguyên vẹn các `\label{...}` quan trọng.
4. **Bước 4 — Biên dịch kiểm tra:** Chạy lệnh biên dịch XeLaTeX 2-pass để bảo đảm không có lỗi cú pháp, không đứt đoạn tham chiếu và cập nhật chuẩn mục lục:
   ```bash
   cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex && cd ..
   ```
5. **Bước 5 — Kiểm tra bài test:** Chạy bộ kiểm thử tự động để xác nhận không vi phạm quy tắc:
   ```bash
   uv run pytest tests/test_thesis_rules.py
   uv run pytest report-datn/scripts/test_tables_and_spacing.py
   ```
6. **Bước 6 — Cập nhật bản đồ tiến độ:** Đánh dấu trạng thái hoàn thành trong `ROADMAP.md` và viết báo cáo bàn giao `handoff.md` theo thể thức 5 thành phần chuẩn mực.

---

### 5.2. Phân Quyền & Quy Tắc Thao Tác Từng Nhóm Tệp
1. **Nhóm tệp điều phối (`main.tex`, `chapters/chX_*.tex`):**
   - *Quyền hạn:* CHỈ ĐỌC (Read-only).
   - Chỉ được chỉnh sửa khi có chỉ định bổ sung/loại bỏ một mục cấp 2 (`\input{...}`). Tuyệt đối cấm viết trực tiếp đoạn văn nội dung vào các tệp điều phối này.
2. **Nhóm tệp cấu hình (`config/preamble.tex`, `config/commands.tex`):**
   - *Quyền hạn:* ĐÓNG BĂNG (Frozen).
   - Không được tự ý thay đổi lề trang, cỡ chữ, phông chữ hoặc nạp thêm các gói lệnh bên ngoài có nguy cơ xung đột (như `booktabs`).
3. **Nhóm tệp vi mô nội dung (`chapters/chX/X_Y_*.tex`):**
   - *Quyền hạn:* ĐỌC VÀ GHI (Read/Write) có kiểm soát.
   - Luôn duy trì dòng đầu tiên chỉ định tệp gốc: `% !TEX root = ../../main.tex`.
   - Sử dụng tiền tố nhãn chuẩn hóa: `sec:`, `subsec:`, `fig:`, `tab:`, `eq:`.
4. **Nhóm tệp tài liệu tham khảo & biểu mẫu (`tai_lieu_tham_khao.tex`, `frontmatter/*.tex`):**
   - Tuân thủ nghiêm ngặt trần $N_{\text{refs}} \le 20$; bảo đảm số điện thoại chính xác của tác giả (`0978461865`), ngày tháng kế hoạch 10 tuần (`24/08/2026 -- 02/11/2026`).

---

## PHẦN 6: BẢNG KIỂM TỰ ĐÁNH GIÁ TRƯỚC KHI BÀN GIAO (PRE-COMMIT CHECKLIST)

Trước khi xác nhận hoàn thành bất kỳ tác vụ nào trong `report-datn/`, AI Agent bắt buộc phải tự đối chiếu và xác nhận đạt **100% các tiêu chí** trong Bảng kiểm tự đánh giá Pre-Commit Checklist:

```markdown
### CHECKLIST TỰ KIỂM ĐỊNH CHẤT LƯỢNG ĐATN CỦA AI AGENT (PRE-COMMIT CHECKLIST)

- [ ] 1. Mục tiêu & 3 Câu hỏi cốt lõi: Đã làm rõ Làm gì? (Ch1), Làm như thế nào? (Ch2 & Ch3), Kết quả ra sao? (Ch4).
- [ ] 2. Quy trình 5 bước kỹ nghệ: Chương 3 trình bày đầy đủ Phân tích -> Thiết kế -> Cài đặt -> Kiểm thử -> Hiệu chỉnh.
- [ ] 3. Kế hoạch 10 tuần: Khớp lịch trình 24/08/2026 -> 02/11/2026; nhấn mạnh cột mốc Tuần 6 (Mid-term Checkpoint).
- [ ] 4. Kỷ luật & Nộp lưu trữ: Nêu rõ nghĩa vụ gặp GVHD hàng tuần, 4 điều kiện đình chỉ, 3 quyển bìa mềm trước bảo vệ, 1 bìa cứng mạ chữ nhũ vàng sau bảo vệ, thư mục bản mềm `MãSinhViên_HọTên_Khóa`.
- [ ] 5. Bố cục toàn văn: Đúng trình tự Frontmatter (i, ii...) -> Thân bài 4 chương (1, 2...) -> Backmatter (Kết luận, TLTK, Phụ lục).
- [ ] 6. Căn lề & Typography: Khổ A4; lề Trên 2.5cm, Dưới 2.5cm, Trái 3.5cm, Phải 2.5cm; phông Times New Roman 13pt; dãn dòng 1.5; thụt lề 1.0cm; số trang góc dưới bên phải.
- [ ] 7. Phân cấp đề mục: Tối đa 4 cấp (X.Y.Z.W); CẤM TIỂU MỤC ĐƠN LẺ (mỗi nhóm >= 2 mục con); tiêu đề danh ngữ hóa 3-7 từ; không có tiêu đề mồ côi.
- [ ] 8. Bảng biểu & Hình vẽ: Tiêu đề Bảng ở TRÊN; Tiêu đề Hình ở DƯỚI; đánh số theo chương (X.Y); TUYỆT ĐỐI CẤM tham chiếu tương đối ("hình dưới đây", "bảng sau").
- [ ] 9. Bảng tabularx & TikZ: Bảng có viền khép kín `|...|` và `\hline`, cột `X` ngắt dòng; sơ đồ TikZ tuân thủ 7 Nguyên tắc vàng, chiều ngang <= 15.0cm.
- [ ] 10. Tài liệu tham khảo: Tiếng Việt trước, tiếng Anh sau; xếp ABC chuẩn; hanging indent 1.0cm; giới hạn <= 20 tài liệu; 100% tài liệu được trích dẫn (không mồ côi).
- [ ] 11. Tỷ lệ nội dung vàng: Lý thuyết (Ch1 + Ch2) <= 30%; Thiết kế & Thực nghiệm (Ch3 + Ch4) >= 70%; tổng dung lượng ruột đạt 50 -- 65 trang.
- [ ] 12. Triệt tiêu 7 Anti-Patterns: Không chép giáo trình (AP-01), cô lập Chương 2 không lộ code (AP-02), không dán code thô > 20 dòng (AP-03), số liệu thực 580 tests / 13.02s (AP-04), trần 20 ref (AP-05), CSDL 20 bảng thực tế (AP-06), sơ đồ/bảng không đâm thủng lề (AP-07).
```

---

> **LỜI KẾT DÀNH CHO CÁC TÁC TỬ:**  
> Mọi dòng văn bản, bảng biểu và công thức xuất bản trong quyển Đồ án Tốt nghiệp này là minh chứng danh dự cho trí tuệ, năng lực kỹ nghệ và sự lao động nghiêm cẩn của tác giả và nhóm tác tử hỗ trợ. Hãy luôn giữ vững chuẩn mực học thuật cao nhất trong từng thao tác!
