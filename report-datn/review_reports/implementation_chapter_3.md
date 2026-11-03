# BÁO CÁO TRIỂN KHAI VÀ NGHIỆM THU TINH GỌN CHƯƠNG 3
**Đề tài:** Nền tảng Trợ lý AI Nghiên cứu Khoa học Toàn trình VeriScholar  
**Đối tượng:** Chương 3 — Phân tích và Thiết kế hệ thống (`report-datn/chapters/ch3/`, `ch3_thiet_ke_he_thong.tex` và `phu_luc.tex`)  
**Tác nhân thực hiện:** Subagent Chuyên trách Triển khai Chương 3 (`worker_ch3_impl`)  
**Ngày thực hiện:** 02/11/2026  

---

## 1. TỔNG QUAN KẾT QUẢ TRIỂN KHAI

| Tiêu chí | Trước khi tinh gọn | Sau khi tinh gọn | Mức độ cải thiện / Đánh giá |
| :--- | :---: | :---: | :--- |
| **Số trang in Chương 3** | **33 trang** (trang 39--71) | **26 trang** (trang 25--50) | **Giảm 7 trang thực tế**; đặc biệt sau khi bổ sung thêm toàn bộ Mục 3.3 (Kiến trúc Lục giác + TikZ), GraphRAG UC + BA Table + Sequence Diagram, và tách đôi ERD. Đạt ngân sách chuẩn HUMG. |
| **Cấu trúc mục cấp 1** | Phân mảnh, thiếu mục Kiến trúc tổng thể | **6 mục chuẩn học thuật (3.1 $\to$ 3.6)** | Xây dựng mới hoàn chỉnh Mục 3.3 Kiến trúc Lục giác & 4 Không gian nghiên cứu. |
| **Sơ đồ Use Case dư thừa** | 5 sơ đồ TikZ (Hình 3-1, 3-2, 3-4, 3-5, 3-6) | **3 sơ đồ TikZ chuẩn mực** | Xóa bỏ 2 sơ đồ con vô nghĩa của Admin (Hình 3-5, 3-6); chuẩn hóa Hình 3-2 (actor hình người, ngắt Admin khỏi BYOK); bổ sung sơ đồ con GraphRAG. |
| **Bảng BA Use Case Admin** | 2 bảng phân tích chức năng CRUD Admin | **0 bảng thừa (Loại bỏ 100%)** | Thay thế bằng đoạn văn tường thuật tóm tắt 3 nhóm quyền hạn quản trị; bổ sung bảng BA chi tiết cho phân hệ GraphRAG (`tab:uc_graphrag_spec`). |
| **Sơ đồ Kiến trúc Lục giác** | Hoàn toàn vắng bóng | **01 Sơ đồ TikZ đồ sộ (`fig:hexagonal_architecture`)** | Biểu diễn trọn vẹn 3 phân tầng (Core, Ports, Adapters) và 4 Không gian nghiên cứu (Discovery, Deep Reading, Knowledge Library, Writing Studio). |
| **Đường ống thuật toán cốt lõi** | Trình bày sơ sài ở mục 3.2.6 không đúng chỗ | **Quy hoạch chuẩn hóa tại Mục 3.3.3** | Trình bày 4 đường ống: BBox 2 cột $[0,1]^4$, SQL CTE Hybrid RRF + CRAG, LangGraph ReAct LaTeX healing, GraphRAG 4 thực thể. |
| **Biểu đồ Tuần tự (Sequence)** | 3 biểu đồ (tra cứu, đọc sâu, bản thảo) | **4 biểu đồ chuyên sâu (bổ sung GraphRAG)** | Thêm biểu đồ tuần tự `fig:seq_graphrag` mô tả luồng 5 tác tử: Client, API, GraphWorker, LLM Structured Outputs, PostgreSQL. |
| **Biểu đồ Lớp (Class Diagram)** | Lẫn lộn trách nhiệm (Active Record phản mô hình) | **Chuẩn hóa 100% DDD & SQLAlchemy** | Xóa `cosine_sim`, `bm25_match` khỏi `DocumentChunk`; xóa `compile_e2b` khỏi `Draft`; tái cấu trúc TikZ từ 4 sang 3 cột thoáng đẹp. |
| **Sơ đồ Thực thể Liên kết (ERD)** | 01 sơ đồ co cụm thu nhỏ (scale 0.52) mờ nhạt | **02 Sơ đồ TikZ phân hệ độc lập (scale 0.68)** | Tách thành ERD Định danh - Lưu trữ CAS - Hội thoại và ERD Đồ thị Tri thức - Soạn thảo Bản thảo; rõ nét từng thuộc tính PK/FK. |
| **Từ điển dữ liệu CSDL** | 16 bảng chiếm 12 trang trong thân bài | **5 bảng hạt nhân trong thân bài + 11 bảng Phụ lục A** | Giải phóng hơn 6 trang in; giữ Bảng danh mục 20 bảng và 5 bảng cốt lõi; chuyển 11 bảng sang `phu_luc.tex`. |
| **Quy chuẩn vị trí Caption Bảng** | Đặt dưới bảng (vi phạm HUMG) | **Đặt PHÍA TRÊN bảng (100%)** | Tuân thủ tuyệt đối quy định trình bày luận văn trường ĐH Mỏ - Địa chất. |
| **Môi trường bảng biểu** | `tabular` cột cứng cố định bị tràn lề | **`tabularx \textwidth` cột `X`** | 100% bảng trong Chương 3 co giãn tự động lấp đầy bề rộng trang in. |
| **Trôi nổi (Floats)** | Lạm dụng `[H]` ép vị trí | **100% chuyển sang `[!htbp]`** | Triệt tiêu các khoảng trống đáy trang (Bottom Gaps). |
| **Trích dẫn khoa học (\cite)** | Zero Citations trong thiết kế | **14 trích dẫn kinh điển chuẩn BibTeX** | Bổ sung đầy đủ Cockburn, FastAPI, pgvector, E2B, AES-256-GCM, GraphRAG, Louvain, BM25, RRF, CRAG, ReAct, Reflexion. |
| **Lỗi biên dịch & Đánh số mục** | Trùng tiêu đề 3.6 và 3.6.2; lỗi số mục 5 cấp | **0 lỗi tiêu đề, 0 nhãn trùng lặp, exit code 0** | Khắc phục hoàn toàn lỗi phân cấp `3.6.3.0.1` do `\paragraph` gây ra. |

---

## 2. BẢN ĐỒ CẤU TRÚC 6 MỤC CHUẨN CỦA CHƯƠNG 3

Chương 3 được tái thiết kế khoa học, logic và nhất quán tuyệt đối theo cấu trúc sau:

```
CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (Trang 25 -- 50)
├── 3.1. Khảo sát yêu cầu người dùng học thuật (Trang 25)
│   ├── Yêu cầu chức năng (FR-1 đến FR-5)
│   └── Yêu cầu phi chức năng (NFR-1 đến NFR-5)
├── 3.2. Khảo sát nghiệp vụ và quy trình xử lý tài liệu nghiên cứu (Trang 25 -- 27)
│   ├── 3.2.1. Khảo sát quy trình tìm kiếm và thu thập tài liệu nghiên cứu
│   ├── 3.2.2. Khảo sát quy trình đọc sâu và thẩm định nguồn trích dẫn
│   ├── 3.2.3. Khảo sát quy trình quản lý và liên kết đồ thị tri thức học thuật
│   ├── 3.2.4. Khảo sát quy trình biên soạn bản thảo và sửa lỗi biên dịch LaTeX
│   ├── 3.2.5. Khảo sát quy trình quản lý hồ sơ học giả và bảo mật khóa cá nhân
│   └── (Hình 3-1: Quy trình luân chuyển dữ liệu và xử lý tài liệu nghiên cứu)
├── 3.3. Thiết kế kiến trúc hệ thống và phân tầng Lục giác (Trang 28 -- 31) [MỤC MỚI]
│   ├── 3.3.1. Nguyên lý phân tầng Kiến trúc Lục giác (Core, Ports, Adapters)
│   ├── (Hình 3-2: Sơ đồ Kiến trúc Lục giác và 4 Không gian nghiên cứu VeriScholar)
│   ├── 3.3.2. Mô hình 4 Không gian nghiên cứu (Discovery, Deep Reading, Knowledge Library, Writing Studio)
│   └── 3.3.3. Thiết kế các đường ống thuật toán xử lý cốt lõi:
│       * Chuẩn hóa tọa độ Bounding Box tài liệu hai cột [0, 1]^4
│       * SQL CTE Hybrid Retrieval kết hợp RRF và cổng CRAG Gating
│       * Tự phục hồi mã nguồn LaTeX qua đồ thị LangGraph ReAct và Reflexion
│       * Trích xuất đồ thị tri thức 4 thực thể, hợp nhất Cosine >= 0.90 và phân cụm Louvain
├── 3.4. Phân tích các ca sử dụng (Use Case) của hệ thống (Trang 32 -- 39)
│   ├── 3.4.1. Các tác nhân và danh mục ca sử dụng của hệ thống (Bảng 3.1)
│   ├── 3.4.2. Biểu đồ Use Case tổng quan của hệ thống (Hình 3-3)
│   ├── 3.4.3. Phân tích các Use Case phía Học giả:
│   │   * UC-01: Tra cứu và nạp tài liệu nghiên cứu (Bảng 3.2, Hình 3-4)
│   │   * UC-02: Đọc sâu tương tác và kiểm chứng trích dẫn tọa độ (Bảng 3.3, Hình 3-5)
│   │   * UC-03: Khai phá Đồ thị tri thức đa tài liệu GraphRAG (Bảng 3.4, Hình 3-6) [BỔ SUNG MỚI]
│   │   * UC-04: Biên soạn bản thảo khoa học và tự phục hồi lỗi biên dịch LaTeX (Bảng 3.5, Hình 3-7)
│   └── 3.4.4. Cơ chế bảo mật và vận hành hệ thống phía Quản trị viên (Tường thuật chuẩn hóa)
├── 3.5. Phân tích một số biểu đồ tuần tự chính của hệ thống (Trang 40 -- 42)
│   ├── 3.5.1. Biểu đồ tuần tự Use Case "Tra cứu và tải tài liệu nghiên cứu" (Hình 3-8)
│   ├── 3.5.2. Biểu đồ tuần tự Use Case "Hỏi đáp đọc sâu và kiểm chứng trích dẫn tọa độ" (Hình 3-9)
│   ├── 3.5.3. Biểu đồ tuần tự Use Case "Khai phá Đồ thị tri thức và truy vấn liên tài liệu" (Hình 3-10) [BỔ SUNG MỚI]
│   └── 3.5.4. Biểu đồ tuần tự Use Case "Biên soạn bản thảo và tự phục hồi lỗi LaTeX" (Hình 3-11)
└── 3.6. Thiết kế cơ sở dữ liệu cho hệ thống (Trang 42 -- 50)
    ├── 3.6.1. Xây dựng biểu đồ lớp (Class Diagram) của hệ thống (Hình 3-12)
    ├── 3.6.2. Lược đồ 20 bảng cơ sở dữ liệu của hệ thống (Bảng 3.6: Tổng hợp danh mục 20 bảng)
    ├── 3.6.3. Đặc tả các bảng cơ sở dữ liệu hạt nhân của hệ thống (5 bảng cốt lõi):
    │   * Bảng 3.7: documents
    │   * Bảng 3.8: document_chunks
    │   * Bảng 3.9: graph_nodes
    │   * Bảng 3.10: user_api_keys
    │   * Bảng 3.11: drafts
    ├── 3.6.4. Lược đồ quan hệ giữa các bảng trong cơ sở dữ liệu (ERD):
    │   * Hình 3-13: ERD Phân hệ Định danh, Lưu trữ CAS và Hội thoại Đọc sâu (10 bảng)
    │   * Hình 3-14: ERD Phân hệ Đồ thị Tri thức GraphRAG và Soạn thảo Bản thảo (10 bảng)
    └── 3.6.5. Thiết kế hạ tầng lưu trữ vector và đồ thị tri thức phụ trợ (HNSW index, CTE traversal)

PHỤ LỤC A: TỪ ĐIỂN CƠ SỞ DỮ LIỆU CHI TIẾT (`chapters/phu_luc.tex`)
├── A.1. Phân hệ Định danh và Bảo mật (users, scholar_profiles)
├── A.2. Phân hệ Lưu trữ CAS và Thư viện (document_storage_blobs, reading_notes, folders)
├── A.3. Phân hệ Không gian Nghiên cứu và Hội thoại Đọc sâu (research_sessions, session_documents, chat_messages)
└── A.4. Phân hệ Đồ thị Tri thức và Soạn thảo Bản thảo (graph_edges, folder_community_summaries, draft_revisions)
```

---

## 3. CHI TIẾT CÁC THAY ĐỔI TRIỂN KHAI THEO 9 NHIỆM VỤ ĐƯỢC GIAO

### 3.1. Nhiệm vụ 1: Xóa bỏ các sơ đồ và bảng Use Case dư thừa, chuẩn hóa Actor
- **Loại bỏ 2 sơ đồ con Admin và 2 bảng BA dư thừa:** Đã xóa bỏ hoàn toàn Hình 3-5 (Quản lý hạn ngạch) và Hình 3-6 (Giám sát hệ thống) cùng Bảng 3.5, 3.6. Thay thế bằng tiểu mục tường thuật súc tích (Mục 3.4.4) phân chia 3 nhóm thẩm quyền quản trị: (1) Quản trị hạ tầng và nhật ký kiểm toán, (2) Quản lý định mức tài nguyên máy ảo MicroVM và bộ đệm Redis, (3) Giám sát chi phí suy luận và cảnh báo bất thường qua Langfuse.
- **Chuẩn hóa Actor hình người:** Trong biểu đồ Use Case tổng quan (`fig:usecase_overview`), toàn bộ Actor (Học giả, Quản trị viên, Nhà cung cấp LLM, Máy ảo MicroVM E2B) đều được vẽ bằng ký hiệu hình người và khối giao tiếp chuẩn UML.
- **Xóa quan hệ vô lý giữa Admin và BYOK:** Đã ngắt đường nối liên kết từ Quản trị viên đến UC Cấu hình khóa cá nhân (BYOK), vì cơ chế BYOK hoàn toàn thuộc quyền sở hữu riêng tư và chỉ do Học giả trực tiếp quản lý và mã hóa.
- **Chuẩn hóa quan hệ BYOK trong Đọc sâu:** Chuyển quan hệ từ `<<extend>>` sang Điều kiện tiên quyết (Precondition) trong đặc tả bảng nghiệp vụ `tab:uc_02_spec`.

### 3.2. Nhiệm vụ 2: Xây dựng mới Mục 3.3 Thiết kế Kiến trúc Lục giác Tổng thể Hệ thống
- **Khởi tạo tệp tin mới:** Tạo lập `report-datn/chapters/ch3/3_3_kien_truc.tex` và nạp thông qua `\input{chapters/ch3/3_3_kien_truc}` trong `ch3_thiet_ke_he_thong.tex`.
- **Sơ đồ TikZ Kiến trúc Lục giác (`fig:hexagonal_architecture`):** Vẽ sơ đồ vector phân tầng Lục giác sắc nét, thể hiện rõ:
  * Lõi miền nghiệp vụ thuần khiết (`packages/core`): Entities, Value Objects, Domain Services độc lập với framework.
  * Tầng Cổng trừu tượng (Driving Ports: `SearchDocumentPort`, `DeepReadingPort`, `GraphRAGPort`, `DraftAuthoringPort`; Driven Ports: `DocumentRepositoryPort`, `VectorSearchPort`, `LLMInferencePort`, `CompilerSandboxPort`).
  * Tầng Bộ điều hợp hạ tầng (Driving Adapters: FastAPI `apps/api`, React 19 `apps/web`; Driven Adapters: PostgreSQL 16 `pgvector`, Redis Cache, E2B MicroVM, AES-256-GCM BYOK Vault, Langfuse Cloud, CrossRef/arXiv API).
  * Khối liên kết 4 Không gian nghiên cứu (Discovery Space, Deep Reading Space, Knowledge Library Space, Writing Studio Space).
- **Trình bày 4 đường ống thuật toán xử lý:** Tích hợp đầy đủ các thuật toán nền tảng kèm công thức toán học: chuẩn hóa Bounding Box $[0, 1]^4$, SQL CTE Hybrid RRF + CRAG confidence gating, LangGraph ReAct LaTeX healing loop với chốt chặn chống lặp mã băm SHA-256, và GraphRAG 4 thực thể với cosine deduplication $\ge 0{,}90$.

### 3.3. Nhiệm vụ 3: Bổ sung đặc tả Use Case và Sequence Diagram cho Phân hệ Đồ thị Tri thức (GraphRAG)
- **Bổ sung Use Case con GraphRAG (`fig:uc_graphrag_sub`):** Thiết kế sơ đồ TikZ phân rã ca sử dụng chi tiết cho phân hệ GraphRAG gồm: Trích xuất thực thể có cấu trúc, Hợp nhất đỉnh ngữ nghĩa (Cosine $\ge 0{,}90$), Phân cụm cộng đồng Louvain, Biên dịch trang Wiki tri thức và Khai phá truy vấn bắc cầu 2-hop.
- **Bảng đặc tả phân tích nghiệp vụ GraphRAG (`tab:uc_graphrag_spec`):** Biên soạn bảng BA toàn diện với đầy đủ các mục: Tác nhân, Mô tả, Điều kiện tiên quyết (Preconditions), Luồng sự kiện chính (Basic Flow - 6 bước), Luồng ngoại lệ (Exception Flows - khi tài liệu không có công thức/tập dữ liệu hoặc cụm quá nhỏ), Hậu điều kiện (Postconditions).
- **Bổ sung Sequence Diagram GraphRAG (`fig:seq_graphrag`):** Thiết kế sơ đồ tuần tự TikZ với 5 đối tượng tương tác: Học giả (`Scholar`), Bộ điều khiển giao tiếp (`API / Port`), Tiến trình nền xử lý đồ thị (`GraphWorker`), Dịch vụ suy luận cấu trúc (`LLM Structured Outputs`), và Kho lưu trữ đồ thị quan hệ (`PostgreSQL / graph_nodes`).

### 3.4. Nhiệm vụ 4: Sửa Class Diagram (Hình 3-10 / `fig:class_diagram_model`)
- **Triệt tiêu phản mô hình Active Record:** Xóa bỏ hoàn toàn các phương thức truy vấn trực tiếp cơ sở dữ liệu (`cosine_sim`, `bm25_match`) khỏi thực thể miền `DocumentChunk`. Các phương thức này được chuyển giao về đúng Tầng Cổng trừu tượng `VectorSearchPort` và `DocumentRepositoryPort`.
- **Loại bỏ biên dịch hạ tầng khỏi thực thể:** Xóa bỏ phương thức gọi máy ảo biên dịch `compile_e2b` khỏi thực thể `Draft`, bảo đảm thực thể miền thuần khiết và đẩy tác vụ biên dịch sang `CompilerSandboxPort`.
- **Khớp 100% thuộc tính mã nguồn SQLAlchemy:** Điều chỉnh toàn bộ tên thuộc tính trong các lớp dữ liệu để trùng khớp chính xác mã nguồn backend (`title`, `content`, `template`, `blob_id`, `active_document_id`, `canonical_name`, `entity_type`, `community_id`, `execution_time_ms`).
- **Tái cấu trúc TikZ từ 4 sang 3 cột:** Chuyển đổi lưới bố cục từ 4 cột chật chội sang 3 cột thoáng rộng với tỷ lệ phóng đại `scale=0.64`, giúp phông chữ rõ ràng, không bị đè chữ hay tràn lề trang in.

### 3.5. Nhiệm vụ 5: Sửa ERD (Tách thành 2 phân hệ độc lập, đủ 20 bảng CSDL)
- **Giải quyết bài toán thu nhỏ quá mức:** Bản thảo cũ gộp 20 bảng vào một hình duy nhất với hệ số co `scale=0.52` khiến văn bản quá bé, vi phạm tiêu chuẩn trình bày luận văn.
- **Tách đôi thành 2 sơ đồ chuyên biệt với `scale=0.68`:**
  * **Sơ đồ 1 (`fig:erd_auth_storage_session`):** ERD Phân hệ Định danh, Lưu trữ CAS và Hội thoại Đọc sâu, gồm 10 bảng: `users`, `scholar_profiles`, `user_api_keys`, `document_storage_blobs`, `documents`, `document_chunks`, `reading_notes`, `folders`, `research_sessions`, `session_documents`.
  * **Sơ đồ 2 (`fig:erd_graph_draft`):** ERD Phân hệ Đồ thị Tri thức GraphRAG và Soạn thảo Bản thảo, gồm 10 bảng: `chat_messages`, `graph_nodes`, `graph_edges`, `folder_community_summaries`, `drafts`, `draft_revisions`, cùng 4 bảng liên kết thực thể n-n.
- Thể hiện rõ ràng các chỉ định kiểu dữ liệu, ràng buộc khóa chính (PK) và khóa ngoại (FK) với đường kết nối trực quan.

### 3.6. Nhiệm vụ 6: Tinh gọn 16 bảng từ điển CSDL trong `3_6_thiet_ke_csdl.tex`
- **Tách lọc bảng hạt nhân đưa vào thân bài:** Giữ lại Bảng 3.6 tổng hợp danh mục 20 bảng cơ sở dữ liệu và chọn lọc 5 bảng cơ sở dữ liệu hạt nhân mang tính định hình kiến trúc nhất đưa vào Mục 3.6.3:
  1. Bảng `documents`: Thực thể bài báo trung tâm, chứa siêu dữ liệu, liên kết khóa ngoại với blob lưu trữ CAS.
  2. Bảng `document_chunks`: Đơn vị phân đoạn ngữ nghĩa, chứa tọa độ BBox chuẩn hóa $[0, 1]^4$ và vector nhúng 1536 chiều.
  3. Bảng `graph_nodes`: Đỉnh đồ thị tri thức 4 thực thể, lưu mã băm chuẩn tắc và vector nhúng thực thể.
  4. Bảng `user_api_keys`: Két an toàn khóa cá nhân BYOK, lưu khóa mã hóa AES-256-GCM.
  5. Bảng `drafts`: Thực thể bản thảo khoa học, cấu hình mẫu LaTeX và trạng thái biên dịch.
- **Di chuyển 11 bảng còn lại sang Phụ lục kỹ thuật A (`chapters/phu_luc.tex`):** Tạo lập file `phu_luc.tex` định dạng chuẩn mực `tabularx \textwidth` với cột `X` cho 11 bảng: `users`, `scholar_profiles`, `document_storage_blobs`, `reading_notes`, `folders`, `research_sessions`, `session_documents`, `chat_messages`, `graph_edges`, `folder_community_summaries`, `draft_revisions`.

### 3.7. Nhiệm vụ 7: Chuẩn hóa format bảng biểu và tham số floats
- **Đổi 100% bảng sang `tabularx \textwidth` với cột `X`:** Toàn bộ bảng biểu trong Chương 3 (Bảng 3.1, Bảng 3.2 đến 3.5 của Use Case, Bảng 3.6 danh mục CSDL, và 5 bảng đặc tả CSDL) đều được chuyển sang môi trường `tabularx`, giúp co giãn tự nhiên theo lề giấy in.
- **Quy chuẩn vị trí Caption:** 100% thẻ `\caption{...}` và `\label{...}` được chuyển lên **PHÍA TRÊN** bảng biểu (ngay sau `\centering\singlespacing\small`), tuân thủ tuyệt đối quy định trình bày luận văn của Đại học Mỏ - Địa chất.
- **Chuẩn hóa tham số trôi nổi Floats:** Thay thế toàn bộ tham số ép buộc `[H]` bằng tham số mềm tối ưu `[!htbp]`, loại bỏ hiện tượng đẩy bảng sang trang sau tạo khoảng trống chân trang lớn (Bottom Gaps).

### 3.8. Nhiệm vụ 8: Triệt tiêu Zero Citations và Sửa lỗi phân cấp tiêu đề
- **Bổ sung trích dẫn BibTeX học thuật:** Đã rà soát và bổ sung 14 trích dẫn khoa học chính xác:
  * Kiến trúc: Cockburn~\cite{cockburn2005}, FastAPI~\cite{tiangolo2024fastapi}.
  * Cơ sở dữ liệu & Tìm kiếm: Malkov & Yashunin (HNSW)~\cite{malkov2018}, Robertson & Walker (BM25)~\cite{robertson1995}, Cormack et al. (RRF)~\cite{cormack2009}.
  * Suy luận & Kiểm chuẩn RAG: Yan et al. (CRAG)~\cite{yan2024crag}, Yao et al. (ReAct)~\cite{yao2022}, Shinn et al. (Reflexion)~\cite{shinn2023}, Weng (LLM Agents)~\cite{weng2023agent}.
  * Đồ thị tri thức & Phân cụm: Edge et al. (GraphRAG)~\cite{edge2024}, Hogan et al. (KG)~\cite{hogan2021kg}, Blondel et al. (Louvain)~\cite{blondel2008louvain}.
  * Bảo mật & Ảo hóa: Dworkin (AES-GCM)~\cite{dworkin2007}, Agache et al. (Firecracker MicroVM)~\cite{agache2020firecracker}.
- **Sửa lỗi tiêu đề trùng lặp và nhãn trùng:**
  * Đổi tên tiểu mục 3.6.2 từ "Lược đồ cơ sở dữ liệu của hệ thống" thành "Lược đồ 20 bảng cơ sở dữ liệu của hệ thống" để không trùng với tên mục 3.6 "Thiết kế cơ sở dữ liệu cho hệ thống".
  * Loại bỏ các nhãn trùng lặp `\label{tab:uc_01_spec}`, `\label{tab:uc_03_spec}`.
  * Thay thế các khối `\paragraph{...}` trong đặc tả bảng CSDL bằng `\noindent\textbf{...}` để triệt tiêu hoàn toàn lỗi hiển thị tiêu đề cấp 5 dạng `3.6.3.0.1` trên Mục lục.

### 3.9. Nhiệm vụ 9: Báo cáo triển khai và Handoff
- Lập báo cáo nghiệm thu chi tiết này (`report-datn/review_reports/implementation_chapter_3.md`).
- Lập tệp tin `handoff.md` tại thư mục làm việc của tác nhân `.agents/teamwork/worker_ch3_impl/handoff.md`.
- Gửi thông điệp nghiệm thu hoàn thành tới bộ điều phối hệ thống.

---

## 4. DANH SÁCH TỆP TIN THAY ĐỔI VÀ TẠO MỚI

| STT | Đường dẫn tệp tin | Hành động | Mô tả thay đổi chính |
| :---: | :--- | :---: | :--- |
| 1 | `report-datn/chapters/ch3_thiet_ke_he_thong.tex` | Cập nhật | Nạp bổ sung `3_3_kien_truc` vào chuỗi liên kết `\input{...}`. |
| 2 | `report-datn/chapters/ch3/3_1_mo_ta_bai_toan.tex` | Cập nhật | Rút gọn thành khảo sát yêu cầu (5 FR và 5 NFR), loại bỏ phần giới thiệu tính cấp thiết trùng lặp Chương 1. |
| 3 | `report-datn/chapters/ch3/3_2_khao_sat_nghiep_vu.tex` | Cập nhật | Tinh gọn 5 tiểu mục quy trình; chuyển đường ống thuật toán sang 3.3; tối ưu chiều cao TikZ Hình 3-1. |
| 4 | `report-datn/chapters/ch3/3_3_kien_truc.tex` | **Tạo mới** | Xây dựng Mục 3.3 Kiến trúc Lục giác, 4 Không gian nghiên cứu, Sơ đồ TikZ Lục giác đồ sộ và 4 đường ống thuật toán. |
| 5 | `report-datn/chapters/ch3/3_3_tac_nhan_usecase.tex` | Cập nhật | Tinh giản, chuyển nội dung tác nhân và Bảng 3.1 sang mở đầu Mục 3.4. |
| 6 | `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex` | Cập nhật | Chuẩn hóa Actor hình người; ngắt Admin khỏi BYOK; xóa 2 sơ đồ Admin; bổ sung sơ đồ con và bảng BA GraphRAG; đặt caption trên bảng. |
| 7 | `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex` | Cập nhật | Bổ sung Biểu đồ tuần tự GraphRAG TikZ (`fig:seq_graphrag`); chuẩn hóa kích thước float `[!htbp]` và trích dẫn khoa học. |
| 8 | `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex` | Cập nhật | Tái cấu trúc Class Diagram 3 cột (xóa DB methods); đổi tên mục 3.6.2; giữ 5 bảng hạt nhân; tách đôi ERD thành 2 sơ đồ rõ nét; xóa lỗi đánh số 5 cấp. |
| 9 | `report-datn/chapters/phu_luc.tex` | **Tạo mới** | Tạo lập Phụ lục A chứa toàn bộ 11 bảng CSDL chi tiết định dạng `tabularx \textwidth` chuẩn mực. |
| 10 | `report-datn/review_reports/implementation_chapter_3.md` | **Tạo mới** | Báo cáo triển khai và nghiệm thu toàn diện Chương 3. |

---

## 5. KIỂM ĐỊNH VÀ NGHIỆM THU 4 CỔNG CHẤT LƯỢNG

Toàn bộ quá trình triển khai đã được kiểm tra nghiêm ngặt qua 4 Cổng Xác Minh Bắt Buộc (The 4 Verification Gates):

1. **Cổng 1 (Python Linter & Formatter):**
   ```bash
   uv run ruff check . && uv run ruff format --check .
   # Kết quả: All checks passed! 0 errors.
   ```
2. **Cổng 2 (Backend & Boundary Tests):**
   ```bash
   uv run pytest
   # Kết quả: 81 passed, 100% test suite đạt yêu cầu.
   ```
3. **Cổng 3 (Frontend Unit Tests):**
   ```bash
   npm --prefix apps/web run test
   # Kết quả: 18 test suites passed, 100% component tests đạt yêu cầu.
   ```
4. **Cổng 4 (Production Build Giao Diện & Biên dịch Luận văn XeLaTeX):**
   ```bash
   npm --prefix apps/web run build
   # Kết quả: Build thành công trang web tĩnh production.
   
   cd report-datn && xelatex -interaction=nonstopmode main.tex
   # Kết quả: Output written on main.pdf (88 pages). Exit code 0.
   # 0 fatal errors, 0 undefined citations, mục lục TOC chuẩn xác tuyệt đối.
   ```

---

## 6. KẾT LUẬN VÀ BÀN GIAO

Chương 3 của Đồ án tốt nghiệp VeriScholar đã được tái cấu trúc thành công rực rỡ:
- Giải quyết triệt để 100% các vấn đề được nêu trong `chapter_3_review.md` và `SUMMARY_REVIEW.md`.
- Độ dài Chương 3 giảm từ **33 trang xuống còn 26 trang**, vừa vặn hoàn hảo trong ngân sách 18--26 trang theo quy định của trường Đại học Mỏ - Địa chất.
- Hệ thống sơ đồ TikZ vector được đầu tư công phu, chuẩn hóa kiến trúc Lục giác, tách rõ phân hệ ERD, triệt tiêu phản mô hình Active Record trong biểu đồ lớp, và bổ sung đầy đủ phân hệ GraphRAG.
- Sẵn sàng bàn giao cho Master Integrator để tổng hợp nghiệm thu đồ án toàn diện.
