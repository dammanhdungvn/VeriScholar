# HỒ SƠ ĐỊNH DANH ĐỀ TÀI VÀ MỤC LỤC ĐẶC TẢ KỸ THUẬT VERISCHOLAR (INFORMATION.md)

> **Căn cứ pháp lý và Thẩm quyền học thuật:**  
> - Quyết định giao đề tài tốt nghiệp của Khoa Công nghệ Thông tin — Trường Đại học Mỏ - Địa chất (HUMG).  
> - Đề cương ĐATN Đại học được phê duyệt bởi Giảng viên hướng dẫn và Bộ môn Hệ thống thông tin và Tri thức.  
> - Toàn bộ mã nguồn thực tế, lược đồ cơ sở dữ liệu và kết quả kiểm thử đã vượt qua 100% trong Monorepo VeriScholar.  
>
> **Ranh giới thẩm quyền và Nguồn chân lý duy nhất (Single Source of Truth — SSOT):**  
> Tài liệu này là **Nguồn Chân Lý Duy Nhất (SSOT)** lưu trữ toàn bộ thông tin định danh sinh viên, giảng viên hướng dẫn, tên đề tài, lịch trình 10 tuần, số liệu thực nghiệm khóa cứng, danh mục 10 tài liệu tham khảo chính thức (giới hạn tối đa <= 20) và **Bản đồ mục lục phân loại đặc tả kỹ thuật coding** tại thư mục [`../docs`](../docs).  
> Toàn bộ quy chuẩn về kiểu chữ, cỡ chữ, căn lề trang, định dạng bảng `tabularx`, kỹ nghệ sơ đồ TikZ, phong cách hành văn học thuật và quy trình phối hợp của AI Agent tuân thủ nghiêm ngặt theo [**`report-datn/AGENTS.md`**](./AGENTS.md).

---

## PHẦN 1: HỒ SƠ ĐỊNH DANH SINH VIÊN VÀ CÁN BỘ HƯỚNG DẪN

### 1.1. Thông tin sinh viên thực hiện
* **Họ và tên sinh viên:** Đàm Mạnh Dũng
* **Mã sinh viên (MSSV):** `2221050359`
* **Lớp sinh hoạt:** `DCCTCT67_09B` (Khóa K67)
* **Ngành đào tạo:** Công nghệ thông tin
* **Mã ngành đào tạo:** `7480201`
* **Chuyên ngành:** Hệ thống thông tin
* **Đơn vị đào tạo:** Khoa Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất (HUMG)
* **Số điện thoại liên hệ:** `0978461865`
* **Email công vụ / cá nhân:** `dammanhdungvn@gmail.com`
* **Hệ đào tạo:** Đại học chính quy
* **Năm thực hiện:** `2026`

### 1.2. Thông tin Giảng viên hướng dẫn
* **Họ và tên giảng viên:** Vũ Lan Phương
* **Học hàm, học vị:** Thạc sĩ (`ThS.`)
* **Chức danh học thuật đầy đủ:** ThS. Vũ Lan Phương
* **Mã cán bộ (CB):** `0802-09`
* **Đơn vị công tác:** Bộ môn Công nghệ thông tin, Khoa Công nghệ thông tin, Trường Đại học Mỏ - Địa chất
* **Số điện thoại:** `0984223379`
* **Email công vụ:** `vulanphuong@humg.edu.vn`

### 1.3. Cơ sở đào tạo và Nơi thực hiện đồ án
* **Cơ quan chủ quản:** Bộ Giáo dục và Đào tạo
* **Cơ sở đào tạo:** Trường Đại học Mỏ - Địa chất (HUMG) — Số 18 Phố Viên, Phường Đức Thắng, Quận Bắc Từ Liêm, Hà Nội
* **Khoa chuyên môn:** Khoa Công nghệ thông tin
* **Bộ môn quản lý chuyên ngành:** Bộ môn Hệ thống thông tin và Tri thức
* **Nơi thực hiện đồ án:** Trường Đại học Mỏ - Địa chất

---

## PHẦN 2: ĐẶC TẢ ĐỀ TÀI NGHIÊN CỨU VÀ TÍNH CẤP THIẾT

### 2.1. Tên đề tài tốt nghiệp chính thức
* **Tên tiếng Việt:**  
  *Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn*
* **Tên tiếng Anh:**  
  *Building an AI Platform for Research and Scientific Paper Writing at VinUni Based on Agentic RAG, Academic Knowledge Retrieval, and Citation Grounding*
* **Tên hệ thống sản phẩm:** Nền tảng Trợ lý Nghiên cứu Khoa học VeriScholar (*VeriScholar Academic AI Platform*).

### 2.2. Bối cảnh bài toán và Tính cấp thiết học thuật
1. **Bối cảnh thực tiễn:**  
   Trong bối cảnh bùng nổ ấn phẩm nghiên cứu khoa học, giảng viên, nghiên cứu sinh và học giả tại Trường Đại học VinUni (VinUni) phải xử lý khối lượng lớn tài liệu học thuật quốc tế đa nguồn cần đọc hiểu, tổng hợp và thẩm định. Việc tiếp cận nhanh chóng các phương pháp tiên tiến đồng thời duy trì năng suất công bố khoa học chuẩn IEEE/ACM là nhu cầu thường trực.
2. **Khoảng trống công nghệ và Vấn nạn ảo giác tri thức:**  
   - Các mô hình ngôn ngữ lớn (LLM) hiện nay thường mắc lỗi ảo giác tri thức (*Hallucination*), tự bịa đặt trích dẫn hoặc dẫn chiếu sai lệch số liệu khoa học.
   - Các công cụ đọc hiểu phổ biến (như ChatPDF) làm mất bố cục 2 cột đặc trưng của các bài báo khoa học và thiếu liên kết tọa độ hộp viền trực quan (Bounding Box) để kiểm chứng minh chứng gốc.
   - Quá trình biên soạn bản thảo học thuật bằng LaTeX thường tốn nhiều công sức để hiệu chỉnh lỗi cú pháp biên dịch mà không có công cụ tự động hóa khép kín.

### 2.3. Mô hình 4 Không gian khép kín (4 Spaces)
Hệ thống VeriScholar được thiết kế kiến trúc phân tách thành 4 Không gian nghiên cứu độc lập nhưng tương hỗ chặt chẽ:
1. **Discovery Space (Không gian Khám phá):** Tìm kiếm bài báo đa nguồn (arXiv, Semantic Scholar, CrossRef), chuẩn hóa metadata, lọc bài đã bình duyệt và lưu trữ nhị phân chống trùng lặp (CAS SHA-256 Deduplication).
2. **Deep Reading Space (Không gian Đọc sâu và Đối soát):** Bộ đọc PDF bảo toàn bố cục 2 cột, chia đoạn thông minh, trích xuất tọa độ Bounding Box và kích hoạt chu trình hỏi đáp tăng cường truy xuất Hybrid RAG có kiểm chứng trích dẫn.
3. **Knowledge Library Space (Không gian Thư viện Tri thức):** Lưu trữ tài liệu yêu thích, cấu trúc cây thư mục phân cấp và xây dựng đồ thị tri thức (GraphRAG) với 4 thực thể học thuật lõi trên PostgreSQL.
4. **Writing Studio Space (Không gian Soạn thảo Kiểm chứng):** Môi trường biên tập LaTeX trực tuyến, tích hợp tác nhân AI tự động hóa sửa lỗi cú pháp biên dịch trong máy ảo MicroVM cách ly an toàn.

### 2.4. Bốn đóng góp kỹ thuật cốt lõi của đề tài
1. **Đóng góp 1 — Kiến trúc truy xuất học thuật Hybrid RAG:** Tích hợp véc-tơ ngữ nghĩa HNSW (1536 chiều) và chỉ mục từ khóa toàn văn PostgreSQL `tsvector`/`tsquery` qua thuật toán Reciprocal Rank Fusion (RRF với hằng số $k = 60$), kết hợp cổng phân loại độ tin cậy CRAG.
2. **Đóng góp 2 — Đọc sâu kiểm chứng tọa độ:** Thuật toán phân tách bố cục 2 cột (`mid_x = 250`) kết hợp đối soát tọa độ khung viền vàng Bounding Box với ngưỡng $\text{IoU} \ge 0{,}85$.
3. **Đóng góp 3 — GraphRAG 4 thực thể trên PostgreSQL ACID:** Mô hình hóa đồ thị tri thức với 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) trên cơ sở dữ liệu quan hệ thuần nhất kết hợp phân cụm Louvain, bảo đảm toàn vẹn giao dịch ACID.
4. **Đóng góp 4 — Soạn thảo an toàn và Tác nhân tự sửa lỗi:** Tác nhân LangGraph ReAct phối hợp sandbox E2B MicroVM tự động sửa lỗi cú pháp LaTeX đạt tỷ lệ thành công 96.0% (vượt ngưỡng mục tiêu $\ge 90\%$), đi kèm cơ chế két khóa cá nhân BYOK mã hóa AES-256-GCM với vector khởi tạo $J_0$.

---

## PHẦN 3: KẾ HOẠCH THỰC HIỆN 10 TUẦN CHI TIẾT (ĐỀ CƯƠNG ĐATN)

Kế hoạch 10 tuần thực hiện đề tài ĐATN chính thức (từ ngày **24/08/2026** đến ngày **02/11/2026**):

| Tuần | Khoảng Thời Gian | Nội Dung Công Việc Kỹ Thuật Và Học Thuật | Sản Phẩm Giao Nộp / Minh Chứng |
| :---: | :---: | :--- | :--- |
| **Tuần 1** | 24/08/2026 – 30/08/2026 | Khảo sát bài toán, nhận đề tài, thu thập tài liệu và viết Đề cương ĐATN. | Đề cương chi tiết được GVHD duyệt. |
| **Tuần 2** | 31/08/2026 – 06/09/2026 | Nghiên cứu kiến trúc Lục giác, mô hình dữ liệu quan hệ PostgreSQL 16 và pgvector. | Schema 20 bảng SQLAlchemy ban đầu. |
| **Tuần 3** | 07/09/2026 – 13/09/2026 | Cài đặt Discovery Space: Adapter API arXiv, Semantic Scholar, CrossRef, lưu trữ CAS SHA-256. | API Khám phá tài liệu và Deduplication test pass. |
| **Tuần 4** | 14/09/2026 – 20/09/2026 | Cài đặt Deep Reading Space: Pipeline băm nhỏ văn bản 2 cột, tính toán BBox, Hybrid RAG và CRAG. | Luồng SSE trả về trích dẫn tọa độ viền vàng. |
| **Tuần 5** | 21/09/2026 – 27/09/2026 | Cài đặt Knowledge Library: Đồ thị tri thức 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`), thuật toán Louvain. | Pipeline GraphRAG và Wiki tóm tắt cộng đồng. |
| **Tuần 6** | 28/09/2026 – 04/10/2026 | **CỘT MỐC ĐÁNH GIÁ TIẾN ĐỘ GIỮA KỲ VỚI BỘ MÔN VÀ GVHD.** Báo cáo khối lượng đã hoàn thành. | Demo chạy thử 3 Không gian; Biên bản xác nhận tiến độ Tuần 6. |
| **Tuần 7** | 05/10/2026 – 11/10/2026 | Cài đặt Writing Studio: Trình soạn thảo Monaco Editor, máy ảo E2B MicroVM và tác nhân ReAct tự sửa lỗi LaTeX. | Luồng biên dịch PDF và tác nhân tự phục hồi cú pháp. |
| **Tuần 8** | 12/10/2026 – 18/10/2026 | Kiểm thử toàn diện: Viết bộ 580 ca kiểm thử đơn vị và tích hợp, đo lường độ trễ CSDL và benchmark. | Báo cáo kiểm thử tự động đạt 100% exit code 0. |
| **Tuần 9** | 19/10/2026 – 25/10/2026 | Triển khai hạ tầng VPS Azure, thiết lập giám sát Langfuse Cloud, tinh chỉnh giao diện Next.js tối giản. | Hệ thống hoạt động tại https://verischolar.duckdns.org. |
| **Tuần 10** | 26/10/2026 – 02/11/2026 | Hoàn thiện toàn văn báo cáo XeLaTeX, rà soát liêm chính học thuật, chuẩn bị slide và bản nộp lưu chiểu. | Quyển báo cáo đóng bìa theo quy định và đĩa mềm/bản mềm lưu trữ. |

### Quy chuẩn đóng gói bản mềm nộp lưu trữ:
- Định dạng thư mục nộp lưu trữ: `MãSinhViên_HọTên_Khóa` (Ví dụ: `2221050359_DamManhDung_K67`).
- Thành phần lưu trữ: Bản PDF báo cáo đồ án toàn văn, toàn bộ mã nguồn chương trình (`packages/core`, `apps/api`, `apps/web`), tài liệu hướng dẫn và các bản vẽ sơ đồ kiến trúc hệ thống.

---

## PHẦN 4: MỤC LỤC VÀ BẢN ĐỒ TRA CỨU ĐẶC TẢ KỸ THUẬT CODING (`./docs`)

Toàn bộ đặc tả kỹ thuật chi tiết về mã nguồn, sơ đồ thiết kế hệ thống, hợp đồng API và kiểm thử được lưu trữ tại thư mục [`../docs`](../docs). Dưới đây là Bảng mục lục phân loại và bản đồ tra cứu tương ứng:

| Phân Hệ / Miền Kỹ Thuật | Tài Liệu Đặc Tả Kỹ Thuật (Specs) | Tài Liệu Nghiệp Vụ (PRD) / Sơ Đồ | Vai Trò Kỹ Thuật & Phạm Vi Chi Tiết |
| :--- | :--- | :--- | :--- |
| **Kiến trúc Lục giác và CSDL** | [`00-foundation-architecture-and-db.md`](../docs/specs/00-foundation-architecture-and-db.md) | [`DATABASE_ERD.md`](../docs/DATABASE_ERD.md), [`00-overview-and-cleanup.md`](../docs/PRD/00-overview-and-cleanup.md) | Phân tầng Domain Core/Ports/Adapters, chuẩn hóa 20 bảng PostgreSQL pgvector, loại bỏ 4 bảng ảo. |
| **Xác thực và Két Khóa BYOK** | [`01-auth-and-user-spec.md`](../docs/specs/01-auth-and-user-spec.md) | [`01-auth-and-user.md`](../docs/PRD/01-auth-and-user.md) | Xác thực JWT, quản lý phiên làm việc, két sắt lưu trữ khóa API cá nhân mã hóa AES-256-GCM với vector $J_0$. |
| **Khám phá và Thu thập Đa nguồn** | [`02-discovery-and-documents-spec.md`](../docs/specs/02-discovery-and-documents-spec.md) | [`02-discovery-and-documents-crud.md`](../docs/PRD/02-discovery-and-documents-crud.md) | Adapter tích hợp arXiv, CrossRef, Semantic Scholar; bộ lưu trữ nhị phân CAS phân giải mã băm SHA-256 chống trùng lặp. |
| **Đọc sâu và BBox Grounding** | [`03-sessions-and-deep-reading-spec.md`](../docs/specs/03-sessions-and-deep-reading-spec.md) | [`03-sessions-and-deep-reading-crud.md`](../docs/PRD/03-sessions-and-deep-reading-crud.md) | Phân tách văn bản 2 cột (`mid_x = 250`), trích xuất tọa độ Bounding Box, Hybrid RAG (HNSW + BM25), cổng CRAG và 5 luồng SSE. |
| **Bảng Ngữ Cảnh và Tiến Trình** | [`04-context-table-and-roadmap-spec.md`](../docs/specs/04-context-table-and-roadmap-spec.md) | [`04-context-table-and-roadmap.md`](../docs/PRD/04-context-table-and-roadmap.md) | Bảng tổng hợp ngữ cảnh nghiên cứu cá nhân hóa và quản lý lộ trình học thuật của học giả. |
| **Thư viện Tri thức và GraphRAG** | [`05-favorite-library-and-graphrag-spec.md`](../docs/specs/05-favorite-library-and-graphrag-spec.md) | [`05-favorite-library-and-graphrag.md`](../docs/PRD/05-favorite-library-and-graphrag.md) | Mô hình đồ thị tri thức 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`), thuật toán phân cụm Louvain và tóm tắt cộng đồng. |
| **Soạn thảo Agentic và Sandbox** | [`06-agentic-overleaf-writing-spec.md`](../docs/specs/06-agentic-overleaf-writing-spec.md) | [`06-agentic-overleaf-writing.md`](../docs/PRD/06-agentic-overleaf-writing.md) | Môi trường biên dịch LaTeX E2B MicroVM, tác nhân ReAct tự động phân tích log và tự sửa lỗi cú pháp. |
| **Giám sát và Langfuse Tracing** | [`07-monitoring-and-langfuse-spec.md`](../docs/specs/07-monitoring-and-langfuse-spec.md) | [`07-monitoring-and-langfuse.md`](../docs/PRD/07-monitoring-and-langfuse.md) | Đo lường độ trễ, Trace ID, đếm Token sử dụng và giám sát chi phí vận hành mô hình ngôn ngữ lớn qua Langfuse Cloud. |
| **Tác tử Tự hành Harness** | [`08-universal-agent-harness-spec.md`](../docs/specs/08-universal-agent-harness-spec.md) | [`.agents/AGENTS.md`](../.agents/AGENTS.md) | Cấu trúc Monorepo Agent Harness, Router kỹ năng, quy tắc kiểm thử TDD bắt buộc và 4 Cổng kiểm định chất lượng. |
| **Triển khai và Đánh giá Thực nghiệm** | [`09-deployment-cicd-and-evaluation-spec.md`](../docs/specs/09-deployment-cicd-and-evaluation-spec.md) | [`08-deployment-and-system-evaluation.md`](../docs/PRD/08-deployment-and-system-evaluation.md), [`thesis_benchmark_results.json`](../docs/benchmarks/thesis_benchmark_results.json) | Script triển khai 1-click VPS Azure, CI/CD pipeline và bộ số liệu đo lường định lượng thực nghiệm gốc của đề tài. |
| **Cẩm nang Bảo vệ và Đề cương** | [`THESIS_DEFENSE_GUIDE.md`](../docs/THESIS_DEFENSE_GUIDE.md) | [`THESIS_OUTLINE_MAPPING.md`](../docs/THESIS_OUTLINE_MAPPING.md) | Cẩm nang trả lời phản biện trước Hội đồng tốt nghiệp và bảng ánh xạ cấu trúc đề cương 4 chương. |

---

## PHẦN 5: BẢNG THAM SỐ ĐỊNH LƯỢNG VÀ BENCHMARKS KHÓA CỨNG

Mọi số liệu thực nghiệm trong báo cáo tốt nghiệp bắt buộc phải đối chiếu khớp 100% với bộ số liệu đo lường định lượng thực tế đã được kiểm chứng độc lập:

### 5.1. Bộ chỉ số đo lường thực nghiệm gốc (Ground Truth Benchmarks)
* **Tổng số bài kiểm thử tự động đã vượt qua:** Đúng **`580`** unit và integration tests (100% pass, exit code 0).
* **Tổng thời gian thực thi toàn bộ test suite:** Đúng **`13.02` giây** (`13.02s`).
* **Độ trễ trung bình truy vấn cơ sở dữ liệu:** Đúng **`1.66` mili-giây** (`1.66ms`).
* **Thời gian trả về token đầu tiên (TTFT - Time-to-First-Token):** Đạt ngưỡng **`< 1.5` giây** (`< 1.5s`).
* **Độ trùng khớp tọa độ trích dẫn (IoU Bounding Box):** Đạt ngưỡng $\text{IoU} \ge 0{,}85$ (thực tế trung bình $0{,}88$).
* **Tỷ lệ tự động sửa lỗi cú pháp LaTeX của Tác nhân ReAct:** Đạt **`96.0%`** (24/25 trường hợp kiểm thử tự phục hồi thành công).

### 5.2. Danh sách 20 bảng cơ sở dữ liệu SQLAlchemy thực tế
Cơ sở dữ liệu của VeriScholar gồm đúng **20 bảng** chuẩn hóa:
1. `users`: Tài khoản học giả và thông tin xác thực (`hashed_password`).
2. `scholar_profiles`: Hồ sơ học giả VinUni, khoa viện, ORCID.
3. `user_api_keys`: Két sắt khóa API cá nhân BYOK mã hóa AES-256-GCM.
4. `document_storage_blobs`: Lưu trữ nhị phân CAS xác định theo mã băm SHA-256.
5. `documents`: Hồ sơ bài báo khoa học, DOI, metadata.
6. `document_chunks`: Đoạn văn bản băm nhỏ kèm véc-tơ `embedding` (1536 chiều) và chỉ mục `content_tsv`.
7. `document_summaries`: Tóm tắt phân cấp văn bản.
8. `reference_items`: Danh mục trích dẫn học thuật liên kết bài báo.
9. `folders`: Cây thư mục tổ chức nghiên cứu phân cấp.
10. `research_sessions`: Phiên tương tác Agentic của học giả.
11. `session_documents`: Bảng liên kết nhiều-nhiều giữa phiên nghiên cứu và bài báo.
12. `session_turns`: Lịch sử các lượt tương tác hỏi đáp trong phiên.
13. `research_notes`: Ghi chú nghiên cứu cá nhân.
14. `graph_nodes`: Thực thể mạng tri thức (4 loại: Paper, Method, Dataset, MetricResult).
15. `graph_edges`: Quan hệ liên kết giữa các thực thể tri thức.
16. `folder_community_summaries`: Tóm tắt cụm cộng đồng Louvain theo cấp độ phân cấp.
17. `wiki_pages`: Các trang bách khoa toàn thư tri thức tự động sinh.
18. `drafts`: Bản thảo bài báo khoa học trực tuyến.
19. `draft_assets`: Tệp đính kèm và hình ảnh cho bản thảo LaTeX.
20. `draft_messages`: Nhật ký tương tác biên soạn và lịch sử sửa lỗi cú pháp.

*(Bốn bảng giả định bị loại bỏ vĩnh viễn: `extracted_figures`, `extracted_tables`, `draft_sections`, `latex_compilations`).*

---

## PHẦN 6: DANH MỤC 10 TÀI LIỆU THAM KHẢO CHÍNH THỨC CỦA ĐỀ TÀI (GIỚI HẠN TỐI ĐA <= 20)

Toàn bộ 10 tài liệu tham khảo chính thức được chọn lọc tinh hoa, đồng bộ 100% với tệp `report-datn/chapters/tai_lieu_tham_khao.tex`, xếp thứ tự phẳng theo bảng chữ cái A--Z họ tác giả đầu tiên, tuân thủ nghiêm ngặt trần $N_{\text{refs}} \le 20$:

1. **Asai, Akari, et al.** (2023), "Self-RAG: Learning to retrieve, generate, and critique through self-reflection", *International Conference on Learning Representations (ICLR 2024)*.
2. **Cormack, Gordon V., Clarke, Charles L., and Buettcher, Stefan** (2009), "Reciprocal rank fusion outperforms condorcet and individual rank learning methods", *Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval*, pp. 758--759.
3. **Edge, Darren, et al.** (2024), "From Local to Global: A Graph RAG Approach to Query-Focused Summarization", *arXiv preprint arXiv:2404.16130*.
4. **Gao, Yunfan, et al.** (2023), "Retrieval-Augmented Generation for Large Language Models: A Survey", *arXiv preprint arXiv:2312.10997*.
5. **Lewis, Patrick, et al.** (2020), "Retrieval-augmented generation for knowledge-intensive NLP tasks", *Advances in Neural Information Processing Systems (NeurIPS 2020)*, vol. 33, pp. 9459--9474.
6. **Malkov, Yury A., and Yashunin, Dmitry A.** (2018), "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs", *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 42, no. 4, pp. 824--836.
7. **Robertson, Stephen E., et al.** (1995), "Okapi at TREC-3", *Overview of the Third Text REtrieval Conference (TREC-3)*, NIST Special Publication 500-225, pp. 109--126.
8. **Shinn, Noah, et al.** (2023), "Reflexion: Language agents with verbal reinforcement learning", *Advances in Neural Information Processing Systems (NeurIPS 2023)*, vol. 36, pp. 8634--8652.
9. **Yan, Shi-Qi, et al.** (2024), "Corrective Retrieval Augmented Generation", *arXiv preprint arXiv:2401.15884*.
10. **Yao, Shunyu, et al.** (2022), "ReAct: Synergizing reasoning and acting in language models", *International Conference on Learning Representations (ICLR 2023)*.

