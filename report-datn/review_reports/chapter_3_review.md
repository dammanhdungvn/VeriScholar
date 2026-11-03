# BÁO CÁO ĐÁNH GIÁ ĐỘC LẬP CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
## NỀN TẢNG TRỢ LÝ AI NGHIÊN CỨU KHOA HỌC VERISCHOLAR

> **Người thực hiện rà soát:** Chuyên gia Đánh giá Báo cáo Đồ án Tốt nghiệp (Chapter 3 Independent Reviewer)  
> **Thời điểm đánh giá:** Ngày 02 tháng 11 năm 2026  
> **Phạm vi thẩm định:** Toàn bộ các tệp nguồn `.tex` tại `report-datn/chapters/ch3/` và tệp điều phối `report-datn/chapters/ch3_thiet_ke_he_thong.tex`  
> **Tài liệu căn cứ & chuẩn đối soát:**  
> - `report-datn/AGENTS.md` (Cẩm nang quy chuẩn biên soạn & SOP chuẩn hóa)  
> - `report-datn/INFORMATION.md` (Hồ sơ đề tài, SSOT lược đồ CSDL 20 bảng và bộ số liệu thực nghiệm khóa cứng)  
> - `report-datn/guide/` (4 tài liệu quy chế và hướng dẫn ĐATN của Khoa CNTT — Trường Đại học Mỏ - Địa chất)  
> - Mã nguồn thực tế hệ thống VeriScholar: `packages/core/`, `apps/api/`, `apps/web/`, `docs/PRD/`, `docs/specs/`  
> **Tệp báo cáo kết quả:** `report-datn/review_reports/chapter_3_review.md`

---

## TỔNG QUAN HIỆN TRẠNG CHƯƠNG 3

Chương 3 của báo cáo đồ án tốt nghiệp có tiêu đề **"PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG"** (nhãn `\label{ch:thiet_ke_he_thong}`), được phân rã và điều phối qua 6 tệp mã nguồn con:
1. `chapters/ch3/3_1_mo_ta_bai_toan.tex` (4.6 KB): Mô tả bối cảnh bài toán và nhu cầu nghiên cứu.
2. `chapters/ch3/3_2_khao_sat_nghiep_vu.tex` (19.6 KB): Khảo sát quy trình nghiên cứu khoa học, mô hình chuyển đổi AS-IS sang TO-BE, và thuật toán cốt lõi.
3. `chapters/ch3/3_3_tac_nhan_usecase.tex` (3.6 KB): Giới thiệu Actor và bảng tổng hợp các Use Case chính.
4. `chapters/ch3/3_4_phan_tich_usecase.tex` (37.9 KB): Biểu đồ Use Case tổng quan, 5 sơ đồ phân rã Use Case con và 5 bảng đặc tả nghiệp vụ chi tiết.
5. `chapters/ch3/3_5_bieu_do_tuan_tu.tex` (12.6 KB): Ba biểu đồ tuần tự (Sequence Diagrams) cho 3 luồng chức năng chính.
6. `chapters/ch3/3_6_thiet_ke_csdl.tex` (58.7 KB): Biểu đồ lớp thực thể (Class Diagram), bảng tổng hợp 20 bảng CSDL, 16 bảng từ điển dữ liệu chi tiết, sơ đồ ERD và mô hình lưu trữ phụ trợ (Vector & Graph).

### Thống kê khối lượng và Ngân sách trang (Page Budget)
- **Vị trí trong tài liệu (`main.pdf`):** Chương 3 bắt đầu từ **Trang 39** và kết thúc tại **Trang 71** (theo `main.toc`), chiếm tổng cộng **33 trang in**.
- **So sánh với Ngân sách trang quy chuẩn:**  
  Theo `report-datn/AGENTS.md` (Bảng phân bổ trang in Mục 2.6, dòng 396):  
  $$\text{Ngân sách quy chuẩn Chương 3:} \quad \mathbf{18 \text{ -- } 24 \text{ trang}} \quad (\approx 40\% \text{ khối lượng toàn đồ án})$$  
  Hiện trạng thực tế (33 trang) đang **vượt ngân sách từ 9 đến 15 trang** (vượt từ $37{,}5\%$ đến $83{,}3\%$). Khối lượng trang bị phình to chủ yếu do việc nhồi nhét 16 bảng từ điển CSDL chi tiết (chiếm 9 trang in liên tục) và việc vẽ các sơ đồ Use Case con quá vụn vặt cho các tác vụ quản trị viên vốn không có giao diện người dùng.
- **Thống kê đối tượng đồ họa & bảng biểu:**  
  - Tổng số hình ảnh/sơ đồ: **12 hình vẽ** (toàn bộ $100\%$ là sơ đồ vector TikZ nội suy trong LaTeX, không có ảnh raster bitmap ngoại lai).
  - Tổng số bảng biểu: **24 bảng biểu** (gồm 1 bảng tổng hợp Use Case, 5 bảng đặc tả Use Case, 1 bảng phân tích quan hệ lớp, 1 bảng tổng hợp 20 bảng CSDL, và 16 bảng từ điển thuộc tính CSDL chi tiết).

---

## MỤC 1: NỘI DUNG DƯ THỪA, KHÔNG CẦN THIẾT HOẶC SAI LỆCH THỰC TẾ KIẾN TRÚC VERISCHOLAR

Qua quá trình đối soát từng dòng mã nguồn `.tex` trong Chương 3 với kiến trúc thực tế của hệ thống (`packages/core`, `apps/api`, `apps/web`, `docs/specs/`), chuyên gia phát hiện nhiều điểm bất hợp lý, dư thừa, thiếu hụt cấu trúc và sai lệch kỹ thuật nghiêm trọng:

### 1.1. Các nội dung dư thừa, trùng lặp cần tinh gọn triệt để

1. **Mục 3.1 (`3_1_mo_ta_bai_toan.tex`) trùng lặp hoàn toàn với Chương 1:**
   - *Hiện trạng:* Mục 3.1 có tiêu đề `\section{Mô tả bài toán}`. Nội dung từ dòng 5 đến 17 hoàn toàn nhắc lại bối cảnh nghiên cứu thủ công 4 bước của học giả (Tìm kiếm, Đọc PDF mất bố cục 2 cột, Lập bảng đối chiếu, Soạn thảo LaTeX) và kết luận bằng tuyên bố "việc nghiên cứu và xây dựng nền tảng trợ lý AI... là hết sức cấp thiết".
   - *Phân tích bất hợp lý:* Nội dung này sao chép gần như nguyên vẹn ý tưởng của Chương 1 (Mục 1.1 "Giới thiệu đề tài", Mục 1.2 "Tính cấp thiết của đề tài", và Mục 1.3 "Mục tiêu nghiên cứu"). Trong cấu trúc một bản ĐATN chuẩn mực của Khoa CNTT — HUMG (`guide/Huong-dan-viet-DATN.md`), Chương 1 là "Mô tả bài toán" (Làm gì? Cho ai?), trong khi Chương 3 là "Phương pháp, quy trình thực hiện giải quyết bài toán". Việc mở đầu Chương 3 bằng một mục lại mang tên "Mô tả bài toán" là sai lạc cấu trúc học thuật và gây lãng phí dung lượng.
   - *Kiến nghị:* **XÓA BỎ** hoặc **CHUYỂN HÓA** Mục 3.1 thành `\section{Khảo sát yêu cầu người dùng học thuật}` hoặc gộp trực tiếp vào đầu Mục 3.2 làm lời dẫn nhập phân tích nghiệp vụ, loại bỏ các đoạn văn mô tả tính cấp thiết đã có ở Chương 1.

2. **Tiểu mục 3.2.6 (`3_2_khao_sat_nghiep_vu.tex`) đặt sai vị trí phân cấp học thuật:**
   - *Hiện trạng:* Mục 3.2 mang tiêu đề "Khảo sát nghiệp vụ và quy trình xử lý tài liệu nghiên cứu" (thuộc giai đoạn Phân tích yêu cầu - Requirements Analysis). Tuy nhiên, tiểu mục 3.2.6 lại có tiêu đề `\subsection{Thiết kế chi tiết các thuật toán xử lý cốt lõi của hệ thống}`. Nội dung tiểu mục này trình bày chi tiết công thức toán học chiếu tọa độ BBox $\hat{B} \in [0, 1]^4$ (Công thức 3.1), logic chấm điểm RRF, ngưỡng gating CRAG $\tau$, đồ thị hữu hạn trạng thái LangGraph ReAct và phân cụm Louvain.
   - *Phân tích bất hợp lý:* Thiết kế thuật toán (Algorithm Design) là nghiệp vụ thuộc pha Thiết kế hệ thống (System Design), không thể nằm bên trong phần "Khảo sát nghiệp vụ". Hơn nữa, việc diễn giải sâu cơ sở toán học RRF, CRAG, Louvain ở đây gây trùng lặp trực tiếp với Chương 2 (Mục 2.3 Advanced RAG, Mục 2.4 GraphRAG, Mục 2.5 Agentic ReAct) và đặc tả Use Case tại Mục 3.4.
   - *Kiến nghị:* Chuyển nội dung thiết kế thuật toán này sang phần Thiết kế kiến trúc xử lý của hệ thống (bổ sung vào Mục 3.3 mới), tinh gọn các diễn giải lý thuyết toán học (viện dẫn bằng `\cite{...}` về Chương 2) và chỉ giữ lại luồng xử lý kỹ nghệ đặc thù của VeriScholar.

3. **Lạm phát Use Case của Quản trị viên (Admin) không có giao diện người dùng:**
   - *Hiện trạng:* Mục 3.4.2 phân bổ 2 tiểu mục lớn (3.4.2.1 và 3.4.2.2) với 2 biểu đồ Use Case con (Hình 3-5, Hình 3-6) và 2 bảng đặc tả BA (Bảng 3.5, Bảng 3.6) cho Actor Quản trị viên (Admin).
   - *Phân tích bất hợp lý:* Chính bản báo cáo tại dòng 355 (`3_4_phan_tich_usecase.tex`) đã thừa nhận: *"Theo quy chuẩn tối giản hóa sản phẩm 80/20, các tác vụ quản trị vận hành... không tách thành một trang giao diện quản trị độc lập cồng kềnh mà được thực thi trực tiếp thông qua hệ thống điểm cuối REST... và bảng điều khiển giám sát từ xa trên Langfuse Cloud và Azure Portal"*. Việc vẽ các sơ đồ ca sử dụng con chi tiết (với các ellipse như "Bảo vệ kho khóa API mã hóa AES-256-GCM", "Thu hồi khối tệp mồ côi cập nhật ref_count CAS") cho một tác nhân không có giao diện ứng dụng thực tế là "vẽ bài tập lớn", thiếu thực tế và làm loãng trọng tâm khoa học của đề tài (nền tảng phục vụ Học giả).
   - *Kiến nghị:* **LOẠI BỎ** hai sơ đồ ca sử dụng con Hình 3-5 và Hình 3-6; chuyển các tác vụ quản trị thành một tiểu mục thuyết minh ngắn gọn về "Cơ chế bảo mật và vận hành hệ thống", hoặc tích hợp vào bảng tổng quan Use Case mà không cần vẽ phân rã riêng.

4. **16 bảng từ điển CSDL chi tiết gây nghẽn trang (Trang 59 – 67):**
   - *Hiện trạng:* Mục 3.6.3 trình bày 16 bảng đặc tả cấu trúc bảng CSDL vật lý (từ Bảng 3.3 đến Bảng 3.18), kéo dài suốt 9 trang in liên tục.
   - *Phân tích bất hợp lý:* Việc bê nguyên xi cấu trúc bảng CSDL (tên cột, kiểu dữ liệu, PK/FK, mô tả) vào thân bài báo cáo ĐATN với số lượng lên tới 16 bảng là hình thức trình bày kiểu "tài liệu kỹ thuật nội bộ" (Data Dictionary dump), không phải phong cách ấn phẩm học thuật. Hội đồng chấm đồ án đánh giá cao tư duy thiết kế mô hình quan hệ, tính toàn vẹn dữ liệu và chỉ mục vector/GIN hơn là việc đọc hàng trăm dòng định nghĩa kiểu dữ liệu `VARCHAR`, `UUID`. Hơn nữa, việc liệt kê 16 bảng này làm cho Danh mục bảng biểu (LoT) ở phần Frontmatter bị kéo dài lê thê và mục lục (`main.toc`) có tới 16 dòng `subsubsection` liên tiếp.
   - *Kiến nghị:* Giữ lại Bảng tổng hợp 20 bảng CSDL (Bảng 3.2), chọn lọc **chỉ 4 đến 5 bảng hạt nhân đặc trưng nhất** của đề tài để trình bày đặc tả chi tiết trong thân bài (ví dụ: `documents`, `document_chunks` chứa vector/BBox, `graph_nodes` chứa GraphRAG, `user_api_keys` chứa két BYOK, `drafts` chứa bản thảo). Toàn bộ các bảng còn lại chuyển vào **Phụ lục kỹ thuật (Appendix)** của đồ án. Giải pháp này giúp cắt giảm ngay lập tức **6 đến 8 trang in dư thừa**, đưa dung lượng Chương 3 trở về đúng ngân sách 20 trang.

---

### 1.2. Các thiếu sót cấu trúc cốt lõi so với đặc tả & quy chuẩn

1. **THIẾU HOÀN TOÀN MỤC THIẾT KẾ KIẾN TRÚC TỔNG THỂ HỆ THỐNG:**
   - *Căn cứ quy chuẩn:*  
     - `report-datn/AGENTS.md` (Mục 1.4, dòng 96): Bước 2 trong quy trình 5 bước kỹ nghệ phần mềm là: *"Thiết kế hệ thống: Thiết kế kiến trúc tổng thể (kiến trúc phần mềm phân tầng, kiến trúc tích hợp)..."*.  
     - `report-datn/ROADMAP.md` (Bảng phân bổ Chương 3, dòng 67): Mục 3.3 được quy hoạch là `chapters/ch3/3_3_kien_truc.tex` — *"Thiết kế kiến trúc hệ thống và luồng dữ liệu"*, ánh xạ từ `.agents/ARCHITECTURE_PRINCIPLES.md`.  
     - `report-datn/INFORMATION.md` (Mục 2.3): Đặc tả mô hình kiến trúc 4 Không gian nghiên cứu (Discovery, Deep Reading, Knowledge Library, Writing Studio).
   - *Hiện trạng:* Trong Chương 3 hiện tại, **hoàn toàn không có bất kỳ mục nào về Thiết kế kiến trúc**! File `3_3_kien_truc.tex` theo quy hoạch không hề tồn tại trong thư mục `report-datn/chapters/ch3/`. Thay vào đó, tệp `3_3_tac_nhan_usecase.tex` nhảy cóc thẳng vào Actor và Use Case. Toàn bộ Chương 3 không có một sơ đồ kiến trúc phần mềm nào (không có sơ đồ Kiến trúc Lục giác Hexagonal Architecture, không có sơ đồ phân tầng Domain Core / Ports / Adapters, không có sơ đồ tương tác giữa React 19 Frontend và FastAPI Backend).
   - *Đánh giá:* Đây là một **lỗ hổng học thuật đặc biệt nghiêm trọng** đối với một chương có tiêu đề "Phân tích và Thiết kế hệ thống". Đồ án CNTT không thể thiếu sơ đồ kiến trúc phần mềm tổng thể.

2. **THIẾU ĐẶC TẢ USE CASE VÀ BIỂU ĐỒ TUẦN TỰ CHO PHÂN HỆ ĐỒ THỊ TRI THỨC (GRAPHRAG):**
   - *Hiện trạng:* GraphRAG 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) trên PostgreSQL ACID là **Đóng góp kỹ thuật cốt lõi số 3** của đề tài (`INFORMATION.md` Mục 2.4). Tính năng này có mã nguồn đồ sộ tại `apps/api/src/api/services/graph_rag_service.py`, `graph_extraction_service.py`, `graph_community_service.py`. Tuy nhiên:
     - Tại Mục 3.4 (Phân tích Use Case): Không hề có sơ đồ phân rã Use Case con và bảng đặc tả nghiệp vụ nào cho việc Khai phá Đồ thị tri thức hoặc Tạo trang Academic Wiki!
     - Tại Mục 3.5 (Biểu đồ tuần tự): Hoàn toàn không có biểu đồ tuần tự mô hình hóa luồng trích xuất thực thể hoặc luồng truy vấn bắc cầu 2-hop Graph Traversal!
   - *Đánh giá:* Trong khi các Use Case quản trị viên (vốn không có UI) được vẽ tới 2 sơ đồ phân rã, thì tính năng học thuật mới mẻ và là đóng góp khoa học chính của sinh viên lại bị bỏ quên không đặc tả.

3. **THIẾU ĐẶC TẢ USE CASE QUẢN TRỊ ĐỊNH DANH ORCID VÀ XÁC THỰC:**
   - Trong Bảng 3.1, Use Case 1 là "Đăng ký / Đăng nhập tài khoản" và Use Case 7 là "Quản lý hồ sơ định danh ORCID và Kho khóa API BYOK", nhưng ở Mục 3.4 hoàn toàn không có bảng đặc tả chi tiết nào cho luồng xác thực và liên kết ORCID iD này.

---

### 1.3. Các sai lệch kỹ thuật so với mã nguồn thực tế VeriScholar

1. **Sai lệch nghiêm trọng về phân tầng trách nhiệm trong Biểu đồ lớp (Hình 3-10):**
   - Trong Hình 3-10 (`fig:class_diagram_model`), các lớp thực thể được gán các phương thức (methods) vi phạm trực tiếp nguyên lý Kiến trúc Lục giác (Hexagonal Architecture) và DDD của VeriScholar:
     - Lớp `DocumentChunk` có phương thức `+ cosine_sim(vec): float`, `+ bm25_match(q): float`. Trong thực tế, việc tính độ tương đồng Cosine được thực hiện hoàn toàn dưới tầng cơ sở dữ liệu PostgreSQL thông qua toán tử vector `<=>` của extension `pgvector` và chỉ mục HNSW; việc so khớp từ khóa được thực hiện bởi chỉ mục GIN trên cột `content_tsv` qua hàm `ts_rank_cd`. Thực thể `DocumentChunk` (tại `packages/core/src/core/domain/entities/chunk.py`) là một Pydantic model thuần túy, tuyệt đối không chứa logic truy vấn DB.
     - Lớp `Draft` có phương thức `+ compile_e2b(): PDFResult`, `+ auto_heal_error(): bool`. Trong thực tế, `Draft` là thực thể dữ liệu miền (`packages/core/.../entities/draft.py`); quá trình gọi máy ảo đám mây E2B MicroVM và điều phối Agent LangGraph tự sửa lỗi là trách nhiệm của Application Service / Port Adapter (`LatexAgent`, `CLSILatexCompiler` tại `apps/api/src/api/services/`). Việc gán các phương thức hạ tầng I/O này vào thực thể miền nghiệp vụ là sai lệch kiến trúc nghiêm trọng.
   - *Thuộc tính sai khác giữa Class Diagram và mã nguồn SQLAlchemy Model:*
     - Lớp `GraphNode` ghi thuộc tính `+ cluster_id: int`. Thực tế mã nguồn `GraphNodeModel` (`apps/api/src/api/db/models/graph.py`) không hề có cột `cluster_id` (kết quả phân cụm Louvain được lưu độc lập trong bảng `folder_community_summaries`).
     - Tên thuộc tính trong Class Diagram bị "bịa đặt" không khớp mã nguồn: `session_title` (mã nguồn là `title`), `latex_content` (mã nguồn là `content`), `template_type` (mã nguồn là `template`), `blob_hash` (mã nguồn liên kết qua foreign key `blob_id: UUID`).

2. **Lược đồ ERD (Hình 3-12) cắt xén tùy tiện, thiếu 8 bảng CSDL:**
   - Trong Mục 3.6, tác giả khẳng định cơ sở dữ liệu gồm đúng 20 bảng chuẩn hóa (liệt kê tại Bảng 3.2). Tuy nhiên, sơ đồ ERD (Hình 3-12, `fig:erd_model`) chỉ hiển thị đúng **12 bảng**, âm thầm bỏ sót **8 bảng**:
     1. Toàn bộ 4 bảng phân hệ GraphRAG: `graph_nodes`, `graph_edges`, `folder_community_summaries`, `wiki_pages`!
     2. 4 bảng nghiệp vụ trọng yếu: `document_summaries`, `session_documents` (bảng liên kết N-N giữa phiên và bài báo), `research_notes` (ghi chú neo giữ tọa độ), và `draft_assets` (tệp hình ảnh đính kèm bản thảo).
   - *Đánh giá:* Việc sơ đồ ERD thiếu tới $40\%$ số lượng bảng trong hệ thống mà không có một lời chú thích giải trình (ví dụ: "ERD phân hệ cốt lõi") là một lỗi kỹ thuật nặng, gây ấn tượng rằng sinh viên thiết kế dở dang hoặc copy sơ đồ từ tài liệu cũ chưa cập nhật.
   - *Sai lệch tên cột trong ERD:* Bảng `RESEARCH_SESSIONS` trong sơ đồ ERD ghi khóa ngoại là `active_doc_id: UUID`, nhưng trong mã nguồn thực tế `apps/api/src/api/db/models/session.py` (dòng 23) và migration DDL (`init_db.py` dòng 183), tên cột chính xác là `active_document_id`.

3. **Sai lệch bản chất an ninh của mô hình BYOK:**
   - Trong Bảng 3.1, BYOK được xếp vào Actor Học giả (Scholar mang khóa riêng). Nhưng trong Mục 3.4.2 và Hình 3-5, BYOK lại bị xếp vào ca sử dụng của Quản trị viên (`Quản trị người dùng và chính sách bảo mật BYOK`), trong đó Admin thực hiện chức năng `Bảo vệ kho khóa API mã hóa AES-256-GCM`.
   - *Bản chất kỹ thuật:* BYOK (Bring Your Own Key) là cơ chế bảo mật cá nhân hóa, nơi khóa của người dùng được mã hóa bằng thuật toán Envelope Encryption / AES-256-GCM với vector $J_0$ và chỉ được giải mã trên bộ nhớ RAM khi người dùng gửi yêu cầu suy luận. Quản trị viên hệ thống **tuyệt đối không có quyền can thiệp hay quản lý khóa này**. Việc đưa BYOK vào Use Case của Admin làm sai lệch nguyên lý bảo mật của đề tài.

---

## MỤC 2: LỖI FORMAT VÀ VI PHẠM QUY CHUẨN THEO AGENTS.MD, INFORMATION.MD, GUIDE/

Quá trình rà soát đối chiếu văn bản Chương 3 với bộ quy chuẩn biên soạn phát hiện các lỗi định dạng và vi phạm thể thức học thuật sau:

### 2.1. Vi phạm 100% quy chuẩn bảng biểu nâng cao (`tabularx`)
- **Quy định tại `report-datn/AGENTS.md` (Mục 2.5.4, dòng 325):**  
  *"Mọi bảng có chứa nội dung văn bản dài, đặc tả nghiệp vụ hoặc từ điển CSDL bắt buộc phải sử dụng môi trường `tabularx` với độ rộng đúng bằng `\textwidth` (`\begin{tabularx}{\textwidth}{|...|}`). Sử dụng cột loại `X` (hoặc `>{\raggedright\arraybackslash}X`) để bảng tự động ngắt dòng chữ, tuyệt đối không dùng cột `l` hay `c` khiến dòng chữ bị đâm thủng lề phải 15,0 cm."*
- **Thực tế vi phạm:**  
  Toàn bộ **24/24 bảng biểu trong Chương 3** đều sử dụng môi trường `\begin{tabular}{|...|}` với độ rộng cột được gán cứng bằng đơn vị xentimét (`p{2.9cm}`, `p{4.0cm}`, `p{9.0cm}`, `p{10.2cm}`).  
  - Ví dụ Bảng 3.1 (`tab:actors_usecases`): Cột 2 rộng `4.0cm`, Cột 3 rộng `9.0cm`, cộng khoảng đệm cột khiến bảng không khớp chính xác với độ rộng lề văn bản `\textwidth`.
  - Toàn bộ 16 bảng đặc tả CSDL (từ Bảng 3.3 đến Bảng 3.18) đều dùng `\begin{tabular}{|c|>{\raggedright\arraybackslash}p{2.9cm}|>{\raggedright\arraybackslash}p{2.9cm}|>{\raggedright\arraybackslash}p{2.5cm}|>{\raggedright\arraybackslash}p{4.6cm}|}`. Cách định dạng thủ công này làm mất tính co giãn tự động của LaTeX khi chuyển đổi layout hoặc kích thước phông.

### 2.2. Vi phạm quy chuẩn trích dẫn khoa học (Lỗi Zero Citations)
- **Quy định tại `report-datn/AGENTS.md` (Mục 2.6.2, dòng 377):**  
  *"Cấm tuyệt đối trích dẫn mồ côi (Zero Orphan References): 100% tài liệu liệt kê trong danh mục cuối bài bắt buộc phải được dẫn chiếu trực tiếp bằng lệnh `\cite{...}` (dạng `[1]`, `[2]`) ít nhất một lần trong phần nội dung thân bài."*
- **Thực tế vi phạm:**  
  Trong toàn bộ 33 trang của Chương 3, **tuyệt đối không xuất hiện bất kỳ một lệnh `\cite{...}` nào**!  
  Mặc dù Chương 3 nhắc đến và mô tả chi tiết rất nhiều công nghệ và thuật toán kinh điển đã được liệt kê trong danh mục 20 tài liệu tham khảo chính thức tại `INFORMATION.md` (Phần 6):
  - Thuật toán Reciprocal Rank Fusion (RRF) của Cormack et al. (2009) — Tài liệu tham khảo `[7]`.
  - Thuật toán xếp hạng Okapi BM25 của Robertson et al. (1995) — Tài liệu tham khảo `[15]`.
  - Chỉ mục đồ thị phân cấp HNSW của Malkov & Yashunin (2018) — Tài liệu tham khảo `[13]`.
  - Cổng kiểm định độ tự tin Corrective RAG (CRAG) của Yan et al. (2024) — Tài liệu tham khảo `[20]`.
  - Tác nhân ReAct và cơ chế tự sửa sai Reflexion của Shinn et al. (2023) — Tài liệu tham khảo `[17]`, Weng (2023) — `[19]`.
  - Phân cụm cộng đồng Louvain của Blondel et al. (2008) — Tài liệu tham khảo `[5]`.
  - Phương pháp GraphRAG của Edge et al. (2024) — Tài liệu tham khảo `[9]`.
  - Chuẩn mã hóa Galois/Counter Mode (AES-GCM) của NIST SP 800-38D (Dworkin, 2007) — Tài liệu tham khảo `[8]`.
  - Ảo hóa siêu nhẹ Firecracker / E2B MicroVM của Agache et al. (2020) — Tài liệu tham khảo `[3]`.
  Việc diễn giải sâu kỹ thuật mà không đính kèm trích dẫn `\cite{...}` là vi phạm nghiêm trọng tính liêm chính và quy chuẩn học thuật của một đồ án tốt nghiệp đại học.

### 2.3. Lỗi nhãn tham chiếu chéo trùng lặp (Duplicate / Double Labels)
- Tại tệp `chapters/ch3/3_4_phan_tich_usecase.tex`:
  - Bảng đặc tả Use Case khám phá (dòng 139–140) khai báo đồng thời 2 nhãn:
    ```latex
    \label{tab:uc_kham_pha_spec}
    \label{tab:uc_01_spec}
    ```
  - Bảng đặc tả Use Case đọc sâu (dòng 232–233) khai báo đồng thời 2 nhãn:
    ```latex
    \label{tab:uc_doc_sau_spec}
    \label{tab:uc_03_spec}
    ```
- *Hậu quả kỹ thuật:* Việc đặt 2 nhãn `\label` cho cùng một đối tượng float gây xung đột chỉ mục trong tệp `.aux` và rủi ro tham chiếu sai số thứ tự bảng khi biên dịch chéo.

### 2.4. Vi phạm quy chuẩn cấm tham chiếu tương đối (No Relative Citations)
- **Quy định tại `report-datn/AGENTS.md` (Mục 2.5.3, dòng 316):**  
  *"TUYỆT ĐỐI CẤM sử dụng các cụm từ tương đối như: 'như trong hình dưới đây', 'kết quả ở bảng sau', 'trong sơ đồ trên', 'ở các mục trước'..."*
- **Các vị trí vi phạm cụ thể trong mã nguồn:**
  - `3_6_thiet_ke_csdl.tex` (dòng 5): *"Căn cứ vào các yêu cầu nghiệp vụ và các Use Case đã được phân tích ở các mục trước..."* $\rightarrow$ Lỗi dùng cụm từ tương đối mơ hồ "ở các mục trước", không có `\ref{...}` tường minh.
  - `3_6_thiet_ke_csdl.tex` (dòng 718): *"Từ các bảng cơ sở dữ liệu và các ràng buộc toàn vẹn... đã được đặc tả chi tiết ở trên..."* $\rightarrow$ Lỗi dùng cụm từ tương đối "ở trên".
  - `3_2_khao_sat_nghiep_vu.tex` (dòng 127): *"Để hiện thực hóa quá trình chuyển đổi từ quy trình AS-IS sang TO-BE nêu trên..."* $\rightarrow$ Lỗi dùng cụm từ tương đối "nêu trên" thay vì dẫn chiếu `Hình~\ref{fig:workflow_as_is_to_be}`.
  - `3_6_thiet_ke_csdl.tex` (dòng 931): *"Bên cạnh lược đồ thực thể quan hệ RDBMS chuẩn mực nêu trên..."* $\rightarrow$ Lỗi dùng cụm từ tương đối "nêu trên".

### 2.5. Lỗi trùng lặp tiêu đề mục và lạm phát mục con trong Mục lục
- **Trùng lặp tiêu đề:**  
  - Mục 3.6 mang tiêu đề: `\section{Thiết kế cơ sở dữ liệu cho hệ thống}`.
  - Ngay sau đó, Tiểu mục 3.6.2 lại mang tiêu đề: `\subsection{Thiết kế cơ sở dữ liệu của hệ thống}`.
  Việc dùng 2 tiêu đề gần như y hệt nhau làm cấu trúc văn bản thiếu tính phân cấp và nghèo nàn về văn phong học thuật.
- **Lạm phát tiểu mục cấp 4:**  
  Việc khai báo 16 tiểu mục `\subsubsection{Đặc tả bảng ...}` (từ 3.6.3.1 đến 3.6.3.16) làm tràn ngập gần 1 trang trong Mục lục (`main.toc`, dòng 85–100), vi phạm nguyên tắc trình bày súc tích của cẩm nang HUMG (`guide/Huong-dan-viet-DATN.md` Mục III.2).

---

## MỤC 3: ĐÁNH GIÁ CHI TIẾT TỪNG HÌNH ẢNH / SƠ ĐỒ TRONG CHƯƠNG 3

Chương 3 hiện có đúng **12 sơ đồ** (đều là môi trường `\begin{tikzpicture}`). Dưới đây là bảng danh mục rà soát độc lập, đánh giá tính cần thiết, chất lượng đồ họa, độ phân giải/kích thước và kiến nghị hành động cụ thể (**GIỮ / BỎ / SỬA / GỘP**) kèm giải trình kỹ thuật chi tiết:

| STT | Mã Nhãn (`\label`) & Tên Sơ Đồ | Vị Trí File & Dòng | Khảo Sát Hiện Trạng Đồ Họa & Tỷ Lệ Scale | Đánh Giá Tính Cần Thiết & Chuẩn Mực UML | Kiến Nghị | Giải Trình Kỹ Thuật Chi Tiết |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | `fig:workflow_as_is_to_be`<br>Mô hình đối chiếu chuyển đổi quy trình AS-IS và TO-BE | `3_2_khao_sat_nghiep_vu.tex`<br>Dòng 54--122 | TikZ vector, `scale=0.76`. Khung màu đỏ/xanh tương phản, mũi tên nối rõ ràng, chiều rộng $\le 12{,}5\,\text{cm}$. | Cần thiết cao. Phản ánh trực quan 4 điểm nghẽn của quy trình cũ và 4 giải pháp tương ứng của VeriScholar. | **GIỮ** | Sơ đồ đạt chuẩn mực đồ họa cao, không bị tràn lề, thể hiện tốt tư duy giải quyết vấn đề của đồ án tốt nghiệp. |
| **2** | `fig:usecase_overview`<br>Biểu đồ Use Case tổng quan của hệ thống VeriScholar | `3_4_phan_tich_usecase.tex`<br>Dòng 7--66 | TikZ vector, `scale=0.72`. Có boundary hệ thống, tác nhân hình người que UML (`umlactor`), phân tách 2 phía Scholar/Admin. | Cần thiết bắt buộc. Là sơ đồ nghiệp vụ trung tâm của toàn bộ hệ thống. | **SỬA** | Cần sửa lỗi logic: xóa đường liên kết từ Actor Admin nối vào Use Case "Quản lý ORCID và Khóa BYOK" (dòng 60), vì đây là quyền riêng tư của Scholar; bổ sung biểu tượng Use Case "Khai phá Đồ thị tri thức (GraphRAG)" rõ nét hơn. |
| **3** | `fig:uc_kham_pha_sub`<br>Biểu đồ ca sử dụng con "Tra cứu và tải tài liệu nghiên cứu" | `3_4_phan_tich_usecase.tex`<br>Dòng 78--132 | TikZ vector, `scale=0.70`. Có quan hệ `<<include>>` và `<<extend>>`, nhãn trắng cách ly trên đường vẽ. | Cần thiết. Làm rõ luồng lọc Jaccard và Deduplication SHA-256 CAS. | **GIỮ** | Đồ họa sắc nét, đúng chuẩn UML use case decomposition, hỗ trợ trực tiếp cho thuật toán CAS và tìm kiếm đa nguồn. |
| **4** | `fig:uc_doc_sau_sub`<br>Biểu đồ ca sử dụng con "Hỏi đáp đọc sâu và kiểm chứng trích dẫn tọa độ" | `3_4_phan_tich_usecase.tex`<br>Dòng 177--225 | TikZ vector, `scale=0.70`. Mô hình hóa các ca thành phần (Hybrid RAG, CRAG, BBox grounding, SSE). | Cần thiết cốt lõi. Đây là tính năng đột phá quan trọng nhất của đề tài. | **SỬA** | Sửa quan hệ: `ext2` ("Thiết lập khóa API cá nhân BYOK") không nên là quan hệ `<<extend>>` của Đọc sâu, mà nên chuyển thành điều kiện tiên quyết (Precondition). Đồ họa TikZ cần giãn cách nhẹ giữa các node include để chống ríu rít. |
| **5** | `fig:uc_bien_soan_sub`<br>Biểu đồ ca sử dụng con "Biên soạn bản thảo và tự phục hồi lỗi LaTeX" | `3_4_phan_tich_usecase.tex`<br>Dòng 270--316 | TikZ vector, `scale=0.70`. Thể hiện tương tác Monaco Editor, E2B MicroVM và vòng lặp ReAct Agent. | Cần thiết. Đại diện cho Không gian Soạn thảo (Writing Studio). | **GIỮ** | Bố cục mạch lạc, thể hiện rõ tính tự động hóa và cơ chế phòng vệ của tác nhân sửa lỗi bản thảo. |
| **6** | `fig:uc_admin_users_sub`<br>Biểu đồ ca sử dụng con "Quản trị người dùng và chính sách bảo mật BYOK" | `3_4_phan_tich_usecase.tex`<br>Dòng 362--408 | TikZ vector, `scale=0.70`. Actor Admin nối với các node kiểm tra ORCID, khóa tự động, AES-256, ref_count CAS. | Không cần thiết. Hệ thống không có giao diện Admin; các tác vụ này thực chất là cơ chế ngầm của CSDL và backend. | **BỎ** | Loại bỏ để tiết kiệm 1 trang in. Nội dung quản trị người dùng đã được thể hiện ở Use Case tổng quan; không cần vẽ phân rã riêng cho tác nhân phụ. |
| **7** | `fig:uc_admin_logs_sub`<br>Biểu đồ ca sử dụng con "Giám sát hệ thống và Trace mô hình" | `3_4_phan_tich_usecase.tex`<br>Dòng 443--489 | TikZ vector, `scale=0.70`. Actor Admin nối với benchmark endpoint, Langfuse telemetry, Azure Portal. | Không cần thiết. Việc chạy benchmark và xem Langfuse là thao tác vận hành/thực nghiệm, không phải Use Case ứng dụng của người dùng. | **BỎ** | Loại bỏ để tinh giản đồ án. Thao tác benchmark đã được mô tả chi tiết ở Chương 4 (Mục 4.2 và 4.4). Việc bỏ 2 sơ đồ Admin này giúp giảm ngay 2 trang in thừa. |
| **8** | `fig:seq_kham_pha`<br>Biểu đồ tuần tự Use Case Tra cứu và tải tài liệu nghiên cứu | `3_5_bieu_do_tuan_tu.tex`<br>Dòng 12--67 | TikZ vector, `scale=0.74`. 5 lifeline gióng phẳng tại $y=-8.0$, có khối `opt` Deduplication CAS SHA-256. | Cần thiết. Làm rõ dòng thời gian tương tác giữa Web UI, Backend API, Scholarly API và Kho CAS. | **GIỮ** | Sơ đồ chuẩn UML Sequence, lifelines gióng phẳng hoàn hảo, thông điệp rõ ràng, thể hiện đúng quy trình lưu trữ CAS. |
| **9** | `fig:seq_doc_sau`<br>Biểu đồ tuần tự Use Case Hỏi đáp đọc sâu và kiểm chứng trích dẫn tọa độ | `3_5_bieu_do_tuan_tu.tex`<br>Dòng 75--135 | TikZ vector, `scale=0.74`. 5 lifeline, có khối `loop` SSE và xác thực trích dẫn, có nested activation tự gọi cuộn trang BBox. | Cần thiết cốt lõi. Minh họa trực quan chu trình Hybrid RAG $\rightarrow$ CRAG $\rightarrow$ LLM $\rightarrow$ BBox Canvas. | **GIỮ** | Thiết kế kỹ nghệ xuất sắc, đáp ứng đầy đủ 7 Nguyên tắc vàng TikZ của `AGENTS.md`, làm nổi bật đóng góp kỹ thuật kiểm chứng trích dẫn. |
| **10** | `fig:seq_bien_soan`<br>Biểu đồ tuần tự Use Case Biên soạn bản thảo và tự phục hồi lỗi LaTeX | `3_5_bieu_do_tuan_tu.tex`<br>Dòng 143--195 | TikZ vector, `scale=0.74`. 5 lifeline, có khối `alt` xử lý khi biên dịch thất bại và gọi Agent ReAct tự sinh bản vá. | Cần thiết. Làm rõ luồng tương tác với môi trường máy ảo E2B MicroVM. | **GIỮ** | Đạt chuẩn UML, phân định rõ ràng giữa luồng biên dịch thành công và luồng kích hoạt tác nhân tự phục hồi cú pháp. |
| **11** | `fig:class_diagram_model`<br>Biểu đồ lớp (Class Diagram) cấu trúc thực thể và quan hệ nghiệp vụ | `3_6_thiet_ke_csdl.tex`<br>Dòng 14--243 | TikZ vector, `scale=0.52`. 11 lớp chia làm 4 cột. Do scale quá nhỏ ($0.52$) nên chữ rất bé, mật độ đường nối dày đặc. | Cần thiết bắt buộc theo quy định của Khoa CNTT — HUMG (Mô hình lớp miền thực thể nghiệp vụ). | **SỬA** | 1. Tăng scale lên tối thiểu $0.62$ bằng cách bố cục lại 3 cột thoáng hơn.<br>2. Sửa lỗi vi phạm kiến trúc Lục giác: xóa các phương thức DB (`cosine_sim`, `bm25_match`) khỏi `DocumentChunk`; xóa `compile_e2b` khỏi `Draft`.<br>3. Chuẩn hóa tên trường khớp $100\%$ với mã nguồn (`title`, `content`, `template`, `blob_id`). |
| **12** | `fig:erd_model`<br>Lược đồ quan hệ giữa các bảng trong hệ quản trị CSDL quan hệ (ERD) | `3_6_thiet_ke_csdl.tex`<br>Dòng 720--926 | TikZ vector, `scale=0.52`. 12 bảng chia làm 4 cột. Thiếu hoàn toàn 8 bảng (toàn bộ 4 bảng GraphRAG và 4 bảng nghiệp vụ khác). | Cần thiết bắt buộc. Là sơ đồ xương sống của toàn bộ thiết kế cơ sở dữ liệu. | **SỬA HOẶC TÁCH PHÂN HỆ** | 1. Sửa lỗi thiếu bảng: Bổ sung 4 bảng GraphRAG (`graph_nodes`, `graph_edges`, `folder_community_summaries`, `wiki_pages`) vào sơ đồ.<br>2. Để tránh sơ đồ bị thu nhỏ quá mức (hiện scale 0.52 là quá bé), kiến nghị tách thành **2 sơ đồ ERD phân hệ chuyên biệt**: (i) *ERD Phân hệ Định danh, Tài liệu CAS và Hội thoại Đọc sâu* (10 bảng); (ii) *ERD Phân hệ Đồ thị Tri thức GraphRAG và Soạn thảo Bản thảo* (10 bảng). Điều này cho phép duy trì scale $\ge 0.68$, chữ to rõ ràng, chuẩn in ấn xuất bản. |

---

### Đánh giá nhu cầu bổ sung sơ đồ mới còn thiếu

Để Chương 3 thực sự hoàn thiện, đạt điểm tối đa trước Hội đồng ĐATN và phản ánh trung thực toàn bộ năng lực kỹ thuật của hệ thống VeriScholar, tác giả cần bổ sung **02 sơ đồ trọng yếu**:

1. **SƠ ĐỒ BỔ SUNG 1: Biểu đồ Kiến trúc Tổng thể Hệ thống (Overall System & Hexagonal Architecture Diagram):**
   - *Vị trí đề xuất:* Đặt tại Mục 3.3 (mới bổ sung: "Thiết kế kiến trúc hệ thống và phân tầng Lục giác").
   - *Nội dung sơ đồ:* Thể hiện kiến trúc Lục giác phân tầng nghiêm ngặt của VeriScholar:
     - Lõi trung tâm: `packages/core` (Domain Entities, Value Objects, Pure Business Logic).
     - Tầng Cổng (Ports): Primary Ports (Use Case Interfaces) và Secondary Ports (Repository / Service Interfaces).
     - Tầng Bộ điều hợp (Adapters): Web REST API (FastAPI), Database Adapter (SQLAlchemy Async, PostgreSQL 16 pgvector, Redis Cache), External Adapters (arXiv, Semantic Scholar, CrossRef, OpenAI API, Langfuse Tracing, E2B MicroVM Sandbox), và Frontend Interface (Next.js / React 19).
     - Mô hình 4 Không gian nghiên cứu (4 Spaces).

2. **SƠ ĐỒ BỔ SUNG 2: Biểu đồ Use Case con hoặc Biểu đồ tuần tự cho Phân hệ Đồ thị Tri thức (GraphRAG):**
   - *Vị trí đề xuất:* Thay thế vị trí của 2 sơ đồ Admin bị loại bỏ, đặt tại Mục 3.4 (Use Case GraphRAG) hoặc Mục 3.5 (Biểu đồ tuần tự GraphRAG).
   - *Nội dung sơ đồ:* Mô hình hóa chu trình trích xuất 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`), khử trùng lặp đỉnh bằng Cosine $\ge 0{,}90$, phân cụm Louvain và truy vấn bắc cầu 2-hop Graph Traversal. Đây là minh chứng kỹ thuật then chốt bảo vệ Đóng góp cốt lõi số 3 của đồ án.

---

## MỤC 4: DANH MỤC HÀNH ĐỘNG KIẾN NGHỊ TINH GỌN CỤ THỂ CHO CHƯƠNG 3

Dựa trên kết quả khảo sát toàn diện, nhóm rà soát đề xuất Bản kế hoạch hành động 5 điểm (Action Plan) nhằm tái cấu trúc và tinh gọn Chương 3:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   LỘ TRÌNH 5 BƯỚC TINH GỌN VÀ NÂNG CẤP CHƯƠNG 3                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ BƯỚC 1: TÁI CẤU TRÚC TIÊU ĐỀ VÀ DỌN DẸP NỘI DUNG DƯ THỪA (Giảm ~4 trang)         │
│   ├─► Xóa bỏ hoặc gộp Mục 3.1 "Mô tả bài toán" vào đầu Mục 3.2 làm lời dẫn.      │
│   ├─► Di dời Mục 3.2.6 (Thiết kế thuật toán) sang Mục Thiết kế Kiến trúc 3.3.    │
│   └─► Sửa tiêu đề trùng lặp: Đổi tên 3.6.2 thành "Lược đồ 20 bảng cơ sở dữ liệu".│
├──────────────────────────────────────────────────────────────────────────────────┤
│ BƯỚC 2: BỔ SUNG MỤC THIẾT KẾ KIẾN TRÚC HỆ THỐNG VÀ GRAPHRAG                      │
│   ├─► Xây dựng Mục 3.3: "Thiết kế kiến trúc hệ thống và phân tầng Lục giác".     │
│   ├─► Bổ sung sơ đồ TikZ Kiến trúc Lục giác và mô hình 4 Không gian.             │
│   └─► Bổ sung đặc tả Use Case / Tuần tự cho Phân hệ Đồ thị Tri thức GraphRAG.    │
├──────────────────────────────────────────────────────────────────────────────────┤
│ BƯỚC 3: LOẠI BỎ CÁC USE CASE VỤN VẶT CỦA QUẢN TRỊ VIÊN (Giảm ~3 trang)           │
│   ├─► Xóa bỏ 2 sơ đồ ca sử dụng con Hình 3-5 (Admin Users) và Hình 3-6 (Admin Log).│
│   └─► Xóa bỏ 2 bảng đặc tả BA Bảng 3.5 và Bảng 3.6 của Admin.                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│ BƯỚC 4: THU GỌN 16 BẢNG TỪ ĐIỂN CSDL VÀ CHUYỂN PHỤ LỤC (Giảm ~7 trang)           │
│   ├─► Giữ lại Bảng tổng hợp 20 bảng CSDL (Bảng 3.2).                             │
│   ├─► Chỉ giữ lại 5 bảng đặc tả chi tiết hạt nhân trong thân bài.                │
│   └─► Chuyển 11 bảng còn lại vào Phụ lục A (Appendix) ở cuối đồ án.              │
├──────────────────────────────────────────────────────────────────────────────────┤
│ BƯỚC 5: HIỆU CHỈNH CHUẨN MỰC FORMAT VÀ ĐỒ HỌA (LAYOUT COMPLIANCE)                │
│   ├─► Chuyển đổi 100% môi trường `tabular` sang `tabularx` với độ rộng \textwidth.│
│   ├─► Bổ sung đầy đủ trích dẫn \cite{...} cho các thuật toán (RRF, CRAG, Louvain).│
│   ├─► Khắc phục các lỗi tham chiếu tương đối ("ở trên", "nêu trên").             │
│   ├─► Cập nhật Class Diagram và ERD khớp 100% tên trường mã nguồn SQLAlchemy.    │
│   └─► Bố cục lại ERD (chia 2 phân hệ hoặc scale hợp lý) hiển thị đủ 20 bảng.     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Dự toán hiệu quả sau khi thực hiện tinh gọn:
- **Số trang in của Chương 3:** Giảm từ **33 trang** xuống còn khoảng **20 -- 22 trang**, hoàn toàn khớp chuẩn ngân sách trang ($18 \text{ -- } 24 \text{ trang}$) theo quy định của Khoa CNTT — HUMG.
- **Tính học thuật và thẩm mỹ:** Bổ sung trọn vẹn mảnh ghép Kiến trúc hệ thống còn thiếu; đưa GraphRAG vào đúng vị thế đóng góp cốt lõi; nâng cao chất lượng in ấn bảng biểu bằng `tabularx`; triệt tiêu $100\%$ các lỗi trích dẫn mồ côi và nhãn trùng lặp.
- **Tính trung thực kỹ thuật:** Sơ đồ lớp và ERD khớp chính xác từng tên cột, kiểu dữ liệu với mã nguồn Python/SQLAlchemy trong Monorepo VeriScholar.

---

## KẾT LUẬN

Chương 3 của bản thảo đồ án tốt nghiệp hiện tại đã hoàn thành được một khối lượng công việc rất lớn và đáng ghi nhận: toàn bộ 12 sơ đồ đều được vẽ kỳ công bằng mã nguồn TikZ vector sắc nét, các luồng tương tác tuần tự được mô hình hóa chi tiết, và lược đồ cơ sở dữ liệu đã bám sát mô hình 20 bảng thực tế trên PostgreSQL 16.

Tuy nhiên, chương này đang mắc phải 3 vấn đề lớn:
1. **Phình to dung lượng do nhồi nhét chi tiết kỹ thuật cơ học:** 16 bảng từ điển CSDL và các ca sử dụng quản trị viên không có UI làm loãng nội dung, khiến số trang vượt ngân sách $83\%$.
2. **Khuyết thiếu kiến trúc hệ thống tổng thể:** Bỏ quên phần thiết kế Kiến trúc Lục giác và phân hệ GraphRAG vốn là trọng tâm đóng góp kỹ thuật của sinh viên.
3. **Lỗi quy chuẩn thể thức và sai lệch phân tầng:** Thiếu trích dẫn `\cite{...}`, vi phạm môi trường `tabularx`, và gán nhầm các phương thức database/infrastructure vào thực thể lớp miền trong Class Diagram.

Việc thực thi nghiêm túc Bản danh mục hành động kiến nghị tinh gọn nêu trên sẽ giúp Chương 3 lột xác trở thành một chương thiết kế hệ thống mẫu mực, chuyên nghiệp, chuẩn mực học thuật quốc tế và bảo đảm tuyệt đối tính liêm chính trước Hội đồng chấm ĐATN Đại học Mỏ - Địa chất.
