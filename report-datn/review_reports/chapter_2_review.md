# BÁO CÁO RÀ SOÁT ĐỘC LẬP CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ
**Dự án:** Nền tảng Trợ lý AI Nghiên cứu Khoa học VeriScholar  
**Đối tượng thẩm định:** Toàn bộ các tệp `.tex` trong `report-datn/chapters/ch2/` và tệp điều phối `report-datn/chapters/ch2_co_so_ly_thuyet.tex`  
**Chuyên gia thẩm định (Reviewer):** Chapter 2 Independent Reviewer  
**Ngày thực hiện:** 02/11/2026  
**Tài liệu đối soát quy chuẩn:**
- `report-datn/AGENTS.md` (Cẩm nang quy chuẩn biên soạn & SOP học thuật)
- `report-datn/INFORMATION.md` (Hồ sơ đề tài, CSDL 20 bảng & Benchmarks khóa cứng)
- `report-datn/guide/` (4 tài liệu quy chế và hướng dẫn ĐATN của Khoa CNTT — HUMG)
- Mã nguồn thực tế dự án VeriScholar (`packages/core/`, `apps/api/`, `apps/web/`, `pyproject.toml`, `package.json`)

---

## TỔNG QUAN HIỆN TRẠNG CHƯƠNG 2

Qua khảo sát toàn diện và biên dịch thử nghiệm XeLaTeX trên tệp `main.tex`, hiện trạng Chương 2 được ghi nhận như sau:
- **Số trang chiếm dụng hiện tại:** **29 trang** (từ trang 10 đến hết trang 38 của bản in `main.pdf`), bắt đầu tại trang 10 và Chương 3 bắt đầu tại trang 39.
- **Ngân sách trang quy chuẩn (Page Budget theo AGENTS.md Mục 2.7):** **10 -- 12 trang** (~18% tổng quy mô đồ án).
- **Mức độ phình to:** **241%** (gấp gần 2,5 lần ngân sách cho phép), là nguyên nhân trực tiếp khiến toàn bộ đồ án bị phình to lên tới **115 trang** (vượt xa trần chuẩn 50 -- 65 trang của ĐATN đại học).
- **Cơ cấu tổ chức tệp:** Gồm 1 tệp điều phối (`chapters/ch2_co_so_ly_thuyet.tex`) nạp 9 tệp con (`2_1` đến `2_9`).
- **Tổng số hình ảnh / sơ đồ:** **23 hình** (gồm **11 ảnh bitmap PNG logo** tải từ Internet và **12 sơ đồ TikZ**).
- **Tổng số bảng biểu:** **01 bảng** (`tab:search_comparison`).
- **Tổng số công thức toán học:** **05 khối phương trình** (`eq:cosine_sim`, `eq:bm25`, `eq:rrf_calc`, `eq:react_cycle`, `eq:aes_gcm`).

---

## PHẦN 1: NỘI DUNG LÝ THUYẾT DƯ THỪA, SAO CHÉP GIÁO TRÌNH VÀ SAI LỆCH VỚI THỰC TẾ DỰ ÁN

Qua rà soát đối chiếu từng tệp nguồn với mã nguồn triển khai thực tế của Monorepo VeriScholar, phát hiện 4 nhóm vi phạm nội dung nghiêm trọng:

### 1.1. Vi phạm AP-01: Chép lý thuyết giáo trình đại cương (Wikipedia / Textbook Dump)

Tài liệu `AGENTS.md` (Mục 3.2, dòng 445 và Mục 3.3, dòng 462) đã ra chỉ thị cấm tuyệt đối:
> *"Cấm chép lý thuyết giáo trình chung chung (Wikipedia / Textbook Dump): Dành 5-7 trang chép định nghĩa chung về Docker, Python, PostgreSQL, REST API, React mà không gắn với bài toán... LƯỢC BỎ: Định nghĩa cơ bản chung chung giáo trình về Docker, Python, REST API."*

Tuy nhiên, Chương 2 đang tồn tại các khối nội dung sao chép sách giáo khoa sơ cấp rất nặng nề:
1. **Tệp `2_9_tools_languages.tex` (Toàn bộ tệp — 63 dòng):**
   - Dành toàn bộ diện tích để trình bày các khái niệm mà mọi sinh viên tốt nghiệp ngành CNTT đều đã biết:
     + Định nghĩa ngôn ngữ lập trình Python, cú pháp gợi ý kiểu dữ liệu tĩnh (dòng 27).
     + Định nghĩa web framework FastAPI, máy chủ ASGI Starlette, thư viện Pydantic (dòng 28).
     + Định nghĩa ngôn ngữ TypeScript, phần mở rộng có kiểu tĩnh của JavaScript (dòng 43).
     + Định nghĩa thư viện React, kiến trúc thành phần, Document Object Model ảo (Virtual DOM) (dòng 44).
     + Định nghĩa nền tảng ảo hóa Docker, Containerization (dòng 59).
     + Định nghĩa khung kiểm thử Pytest và Vitest (dòng 60--61).
   - Đi kèm là 4 ảnh logo khổng lồ chèn vào thân bài. Toàn bộ tệp `2_9` hoàn toàn không có hàm lượng nghiên cứu khoa học, vi phạm trực tiếp AP-01, biến đồ án tốt nghiệp cử nhân/kỹ sư thành tài liệu hướng dẫn học lập trình cơ bản.

2. **Tệp `2_3_advanced_rag.tex` (Mục Naive RAG — Dòng 7--78):**
   - Trình bày dài dòng về kiến trúc Naive RAG (RAG truyền thống sơ cấp) kèm theo một sơ đồ TikZ khổng lồ (`fig:naive_rag` chiếm hơn nửa trang in).
   - Thực tế dự án VeriScholar ngay từ đầu đã thiết kế theo kiến trúc Advanced RAG đa tầng (Bố cục PDF 2 cột, Bounding Box IoU $\ge 0{,}85$, Hybrid Search GIN + BM25, RRF $k=60$ và FlashRank Reranker). Hệ thống **hoàn toàn không cài đặt hay sử dụng Naive RAG**. Việc mô tả quá chi tiết và vẽ hình to cho Naive RAG là hoàn toàn dư thừa, làm loãng trọng tâm khoa học của đề tài.

### 1.2. Trình bày các mẫu kiến trúc "ảo" không có trong thực tế dự án (Tệp `2_5_agentic_react.tex`)

Tệp `2_5_agentic_react.tex` là tệp phình to bất thường nhất trong Chương 2 (dài **691 dòng**, dung lượng **43 KB**, chứa tới **7 sơ đồ TikZ**).
Tệp này liệt kê chi tiết 6 mẫu thiết kế tác nhân (*Agent Design Patterns*), nhưng đối chiếu với mã nguồn thực tế tại `packages/core/` và `apps/api/`, hệ thống VeriScholar **chỉ triển khai Tác nhân đơn lẻ (Single-Agent Orchestrator) theo chu trình ReAct kết hợp gọi công cụ ngoại vi (Tool Use) và máy trạng thái LangGraph**:

| Mẫu kiến trúc trong báo cáo | Mô tả trong `2_5_agentic_react.tex` | Thực tế triển khai trong VeriScholar | Đánh giá học thuật |
| :--- | :--- | :--- | :--- |
| **Planning Pattern** (Mục 2.5.2, dòng 122--224) | Vẽ sơ đồ `fig:planning_pattern`, chia pha Analyze $\to$ Decompose $\to$ Sequence $\to$ Execute. | **KHÔNG DÙNG**. Bản thân văn bản báo cáo (dòng 223) thừa nhận: *"tư duy lập kế hoạch được tích hợp trực tiếp vào pha suy luận (Thought)... mà không phát sinh độ trễ của một tầng lập kế hoạch tách rời."* | **DƯ THỪA**. Vẽ sơ đồ và phân tích lý thuyết không dùng thật. |
| **Reflection / Reflexion Pattern** (Mục 2.5.5, dòng 407--502) | Vẽ sơ đồ `fig:reflection_pattern_loop`, mô tả vòng lặp LLM tự đánh giá sinh phản hồi ngôn từ (*verbal feedback*) đa lượt. | **KHÔNG DÙNG**. Bản thân văn bản báo cáo (dòng 501) thừa nhận: *"thay vì kích hoạt một vòng lặp LLM tự phê bình đa lượt tốn kém chi phí mã thông báo, nguyên lý kiểm định đầu ra được hiện thực hóa bằng các rào chắn xác định (Deterministic Guardrails)..."* | **DƯ THỪA**. Trình bày cơ chế LLM self-reflection tốn kém mà thực tế dùng code rule xác định. |
| **Multi-Agent Collaboration** (Mục 2.5.6, dòng 504--598) | Vẽ sơ đồ `fig:multi_agent_pattern` gồm Coordinator điều phối 4 tác nhân chuyên trách: Data Agent, Analysis Agent, Writing Agent, Review Agent. | **KHÔNG DÙNG**. Bản thân văn bản báo cáo (dòng 597) thừa nhận: *"VeriScholar triển khai kiến trúc tác tử đơn điều phối trung tâm (Single-Agent ReAct Orchestrator)... mô hình phối hợp đa tác tử phân cấp đóng vai trò là nền tảng lý thuyết định hướng cho giai đoạn mở rộng tiếp theo..."* | **SAI THỰC TẾ**. Dự án chưa có hệ thống đa tác tử như sơ đồ; đưa vào làm Hội đồng lầm tưởng sinh viên đã cài đặt Multi-Agent. |
| **Human-in-the-Loop Pattern** (Mục 2.5.7, dòng 600--691) | Vẽ sơ đồ `fig:hitl_pattern`, cơ chế tạm dừng luồng (*Pause for Review*) chờ học giả bấm duyệt (*Approved?*). | **KHÔNG DÙNG**. Dòng 690 thừa nhận: *"cơ chế điểm dừng tạm khóa luồng thực thi (Interrupt Checkpoints) là hướng mở rộng tương lai."* Thực tế chỉ là giao diện PDF hiển thị BBox cho người dùng xem. | **DƯ THỪA**. Vẽ sơ đồ kiến trúc tương lai vào phần lý thuyết nền tảng. |

$\rightarrow$ **Hậu quả:** Mục 2.5 chiếm tới **8 trang in** vô ích chỉ để trình bày các lý thuyết mà đề tài thừa nhận là "không dùng trong thực tế" hoặc "hướng phát triển tương lai", vi phạm nghiêm trọng tính cô đọng của báo cáo ĐATN.

### 1.3. Vi phạm nguyên tắc lập luận "Tại sao chọn" (Justification-Driven)

Quy chế HUMG (`Huong-dan-viet-DATN.md` dòng 133) và `AGENTS.md` (Mục 3.1, Nguyên tắc 4) yêu cầu bắt buộc:
> *"Lưu ý có những đánh giá, nhận định để đi đến kết luận tại sao lại chọn công nghệ/ngôn ngữ lập trình/framework đó để thực hiện đề tài. Không chỉ nêu định nghĩa mà bắt buộc phải trả lời câu hỏi cốt tử của Hội đồng: 'Tại sao đề tài chọn giải pháp này mà không chọn giải pháp khác?'"*

Chương 2 hiện tại hầu hết chỉ dừng lại ở mức **định nghĩa tính năng** (PostgreSQL có MVCC, Redis có In-Memory, LangGraph có StateGraph...), **hoàn toàn thiếu vắng các bảng so sánh đối chứng đa tiêu chí và luận giải khoa học chuyên sâu**:
- **Thiếu luận giải PostgreSQL pgvector vs. Dedicated Vector Database:** Tại sao đề tài chọn PostgreSQL tích hợp pgvector thay vì dùng các cơ sở dữ liệu vector chuyên dụng đình đám như Milvus, Pinecone, Weaviate hay Qdrant? Lý do khoa học then chốt là:
  1. Bảo toàn tính toàn vẹn giao dịch ACID tuyệt đối (khi xóa/sửa một tài liệu khoa học, cả bản ghi quan hệ và vector nhúng được cập nhật đồng thời trong một giao dịch duy nhất, không phát sinh lỗi dữ liệu mồ côi).
  2. Triệt tiêu độ phức tạp và chi phí vận hành kiến trúc phân tán đa cơ sở dữ liệu trên môi trường máy chủ đơn (VPS Azure).
  3. Cho phép truy vấn lai (Hybrid Query) kết hợp lọc trường quan hệ (`WHERE user_id = ...`) và tìm kiếm vector trong cùng một câu lệnh SQL hiệu năng cao.
- **Thiếu luận giải Kiến trúc Lục giác vs. Kiến trúc 3 tầng truyền thống:** Tại sao không dùng MVC hay 3-tier thông thường? (Vì AI LLM thay đổi nhanh chóng, kiến trúc Hexagonal cho phép mock adapter để chạy 580 automated tests mà không tốn tiền API hay phụ thuộc mạng ngoài).
- **Thiếu luận giải ReAct Agent vs. Plan-and-Solve / Chain-of-Thought:** Tại sao chọn ReAct? (Vì giải quyết được bài toán ảo giác thông qua vòng lặp quan sát Observation từ môi trường thực tế).

### 1.4. Thiếu hụt công thức toán học cốt lõi đã cam kết trong AGENTS.md

Tài liệu `AGENTS.md` (Mục 3.3, dòng 462) quy định rõ nội dung bắt buộc phải GIỮ & NÂNG TẦM tại Chương 2:
> *"Thuật toán phân cụm đồ thị Louvain và hàm mục tiêu Modularity $Q$."*

Tuy nhiên, tại tệp `2_4_knowledge_graph_wiki.tex` (dòng 95--97 và 170--171), văn bản chỉ nhắc đến tên thuật toán Louvain một cách định tính, **hoàn toàn không xuất hiện công thức toán học tính hàm mục tiêu độ mô-đun Modularity $Q$**:
$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$
Việc thiếu công thức này làm giảm hàm lượng toán học và tính thuyết phục của cơ sở lý thuyết GraphRAG.

---

## PHẦN 2: LỖI FORMAT VÀ VI PHẠM QUY CHUẨN ĐỊNH DẠNG THEO AGENTS.MD, INFORMATION.MD VÀ HƯỚNG DẪN KHOA CNTT - HUMG

Qua rà soát chi tiết từng dòng lệnh LaTeX trong 9 tệp nguồn, phát hiện hàng loạt lỗi vi phạm quy chuẩn chế bản học thuật nghiêm trọng:

### 2.1. Vi phạm quy chuẩn Danh ngữ hóa tiêu đề và Lỗi đặt tiêu đề dạng câu hỏi ("... là gì?")

`AGENTS.md` Mục 2.4 (dòng 283--286) và Mục 3.1 (Nguyên tắc 5) quy định:
> *"Mọi tiêu đề mục từ cấp 1 đến cấp 4 phải là một cụm danh từ cô đọng từ 3 đến 7 từ, định danh trực diện đối tượng khoa học/kỹ thuật. Tuyệt đối cấm tiêu đề dạng mệnh đề kể lể mở đầu bằng động từ ('Nghiên cứu về...', 'Tìm hiểu giải pháp...') hoặc dạng câu hỏi."*

Chương 2 vi phạm lỗi này một cách có hệ thống trên hầu hết các tệp:

1. **Lỗi tiêu đề mục cấp 1 mở đầu bằng động từ hoặc cụm từ kể lể (8/9 mục vi phạm):**
   - Mục 2.1 (`2_1_postgresql_redis.tex:2`): `\section{Tổng quan về PostgreSQL và Redis}` $\rightarrow$ Chứa cụm từ kể lể "Tổng quan về...".
   - Mục 2.2 (`2_2_hexagonal.tex:2`): `\section{Tổng quan về Hexagonal Architecture}` $\rightarrow$ Chứa "Tổng quan về...".
   - Mục 2.3 (`2_3_advanced_rag.tex:2`): `\section{Tổng quan về Advanced RAG}` $\rightarrow$ Chứa "Tổng quan về...".
   - Mục 2.4 (`2_4_knowledge_graph_wiki.tex:2`): `\section{Tổng quan về GraphRAG, Knowledge Graph và Graph Wiki}` $\rightarrow$ Chứa "Tổng quan về...".
   - Mục 2.5 (`2_5_agentic_react.tex:2`): `\section{Tìm hiểu về Agentic AI và ReAct}` $\rightarrow$ **Mở đầu bằng động từ** "Tìm hiểu về...".
   - Mục 2.6 (`2_6_langgraph.tex:2`): `\section{Tổng quan về LangGraph}` $\rightarrow$ Chứa "Tổng quan về...".
   - Mục 2.7 (`2_7_azure_e2b_byok.tex:2`): `\section{Tìm hiểu về Azure OpenAI và E2B Sandbox}` $\rightarrow$ **Mở đầu bằng động từ** "Tìm hiểu về...".
   - Mục 2.8 (`2_8_langfuse.tex:2`): `\section{Tổng quan về Langfuse}` $\rightarrow$ Chứa "Tổng quan về...".

2. **Lỗi tiêu đề tiểu mục cấp 2 đặt tên theo dạng câu hỏi ngô nghê ("... là gì?") (11 tiểu mục vi phạm):**
   - `2_1_postgresql_redis.tex:5`: `\subsection{PostgreSQL là gì?}`
   - `2_1_postgresql_redis.tex:38`: `\subsection{Redis là gì?}`
   - `2_2_hexagonal.tex:5`: `\subsection{Hexagonal Architecture là gì?}`
   - `2_3_advanced_rag.tex:5`: `\subsection{RAG là gì? (Retrieval-Augmented Generation)}`
   - `2_3_advanced_rag.tex:81`: `\subsection{Advanced RAG là gì?}`
   - `2_4_knowledge_graph_wiki.tex:5`: `\subsection{GraphRAG là gì?}`
   - `2_4_knowledge_graph_wiki.tex:99`: `\subsection{Knowledge Graph là gì? (Đồ thị tri thức)}`
   - `2_4_knowledge_graph_wiki.tex:168`: `\subsection{Graph Wiki là gì? (Pre-compiled Community Wiki)}`
   - `2_6_langgraph.tex:5`: `\subsection{LangGraph là gì?}`
   - `2_7_azure_e2b_byok.tex:23`: `\subsection{E2B Sandbox là gì?}`
   - `2_8_langfuse.tex:5`: `\subsection{Langfuse là gì? (LLM Tracing and Observability)}`

   *Nhận xét:* Cách đặt tiêu đề dạng câu hỏi "... là gì?" hoàn toàn không phù hợp với văn phong một bản báo cáo Đồ án Tốt nghiệp Đại học chính quy, tạo cảm giác sao chép từ các bài viết blog hỏi-đáp trên mạng Internet.

### 2.2. Lỗi nghiêm trọng: Đặt tiêu đề Bảng biểu ở PHÍA DƯỚI Bảng

`AGENTS.md` Mục 2.5 (dòng 312--315) và `Huong-dan-viet-DATN.md` dòng 169 quy định bất biến:
> *"ĐẦU ĐỀ BẢNG BIỂU: BẮT BUỘC ĐẶT Ở PHÍA TRÊN BẢNG.*  
> *ĐẦU ĐỀ HÌNH VẼ: BẮT BUỘC ĐẶT Ở PHÍA DƯỚI HÌNH.*  
> *Vi phạm vị trí đầu đề bảng/hình bị coi là lỗi định dạng nghiêm trọng bị trừ điểm trực tiếp trong quy chế chấm đồ án."*

- **Vị trí vi phạm:** Tại `report-datn/chapters/ch2/2_3_advanced_rag.tex`, dòng 241--261:
  ```latex
  \begin{table}[H]
  \centering
  \singlespacing
  \small
  \renewcommand{\arraystretch}{1.2}
  \begin{tabular}{|p{3.0cm}|p{5.2cm}|p{5.2cm}|}
  ...
  \end{tabular}
  \caption{So sánh đặc tính giữa tìm kiếm ngữ nghĩa Dense Vector và từ khóa BM25}
  \label{tab:search_comparison}
  \end{table}
  ```
  `\caption` được đặt tại dòng 259, **ngay sau** `\end{tabular}` thay vì đặt ở phía trên! Đây là bảng duy nhất trong Chương 2 nhưng lại mắc lỗi sơ đẳng này.

### 2.3. Vi phạm quy chuẩn Bảng biểu nâng cao (`tabularx` vs `tabular`)

`AGENTS.md` Mục 2.5 (dòng 324--328) quy định:
> *"Mọi bảng có chứa nội dung văn bản dài... bắt buộc phải sử dụng môi trường tabularx với độ rộng đúng bằng \textwidth (\begin{tabularx}{\textwidth}{|...|}). Sử dụng cột loại X để tự động ngắt dòng, tuyệt đối không dùng cột p cố định khiến bảng không lấp đầy lề hoặc đâm thủng lề."*

- Bảng `tab:search_comparison` sử dụng `\begin{tabular}{|p{3.0cm}|p{5.2cm}|p{5.2cm}|}` với tổng độ rộng $3{,}0 + 5{,}2 + 5{,}2 = 13{,}4\,\text{cm}$, trong khi chiều rộng thân bài khả dụng của trang in là đúng **$15{,}0\,\text{cm}$** ($21{,}0 - 3{,}5 - 2{,}5 = 15{,}0\,\text{cm}$). Bảng bị hụt $1{,}6\,\text{cm}$, tạo khoảng trống lệch về bên phải, không chuyên nghiệp.

### 2.4. Vi phạm quy chuẩn thông số vị trí Floats (Sử dụng `[H]` thay vì `[!htbp]`)

`AGENTS.md` Mục 2.2 (dòng 254) quy định về Kỹ thuật chống khoảng trống đáy trang (Anti-Bottom-Gap Standard):
> *"Tất cả các đối tượng trôi nổi (Floats: Bảng biểu và Hình vẽ) bắt buộc phải khai báo tham số vị trí linh hoạt: `\begin{table}[!htbp]` và `\begin{figure}[!htbp]`. Tuyệt đối cấm sử dụng `[H]` cứng nhắc vì sẽ ép buộc XeLaTeX đẩy toàn bộ khối hình lớn sang trang tiếp theo, để lại 1/3 đến 1/2 trang giấy trắng mồ côi ở đáy trang trước."*

- **Thực tế Chương 2:** Toàn bộ **22 khối figure** và **01 khối table** trong Chương 2 đều sử dụng tham số cứng `[H]` (`\begin{figure}[H]`, `\begin{table}[H]`).
- Hậu quả trực quan: Khi biên dịch, các sơ đồ TikZ lớn (như `fig:planning_pattern`, `fig:multi_agent_pattern`) không thể nhét vừa trang hiện tại, bị ép nhảy sang trang mới, tạo ra hàng loạt khoảng trắng khổng lồ ở đáy các trang 14, 18, 25, 29.

### 2.5. Phân mảnh cấu trúc chương thành quá nhiều mục nhỏ cấp 1

Chương 2 hiện tại được chia thành **9 mục cấp 1** (`2.1` đến `2.9`). Việc chia quá vụn này làm cho chương có cấu trúc manh mún như một danh sách kiểm kê công nghệ (Technology Inventory) thay vì một bức tranh kiến trúc học thuật mạch lạc gồm các khối giải pháp lớn. Bản đồ kiến trúc ban đầu tại `report-datn/ROADMAP.md` (dòng 52--56) chỉ quy hoạch 5 mục cốt lõi, nhưng quá trình biên soạn đã bị xé nhỏ quá đà.

---

## PHẦN 3: ĐÁNH GIÁ CHI TIẾT TỪNG HÌNH ẢNH / SƠ ĐỒ TRONG CHƯƠNG 2

Dưới đây là Bảng danh mục và thẩm định chi tiết toàn bộ **23 hình ảnh / sơ đồ** xuất hiện trong Chương 2:

| STT | Tệp nguồn & Dòng | Nhãn `\label` | Caption hiện tại | Định dạng | Đánh giá giá trị học thuật & Tính cần thiết | Kiến nghị | Giải trình lý do & Hành động cụ thể |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **1** | `2_1_postgresql_redis.tex:11` | `fig:logo_postgresql` | PostgreSQL | Ảnh PNG (`3.4cm`) | **Không có giá trị học thuật.** Logo con voi PostgreSQL tải từ mạng. | **BỎ** | Loại bỏ hoàn toàn hình logo. Tiết kiệm diện tích trang in. |
| **2** | `2_1_postgresql_redis.tex:44` | `fig:logo_redis` | Redis | Ảnh PNG (`3.2cm`) | **Không có giá trị học thuật.** Logo Redis tải từ mạng. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **3** | `2_2_hexagonal.tex:35--125` | `fig:hexagonal_arch` | Mô hình phân rã module và cấu trúc cổng -- điều hợp (Ports and Adapters) | Sơ đồ TikZ (`scale=0.74`) | **Rất cao.** Thể hiện chuẩn mực 3 phân vùng Driving Adapters, Core Domain/Ports, Driven Adapters; luồng phụ thuộc hướng tâm đảo ngược (DIP). | **GIỮ** | Giữ nguyên sơ đồ TikZ chất lượng cao này. Đổi tham số vị trí `[H]` thành `[!htbp]`. |
| **4** | `2_3_advanced_rag.tex:20--77` | `fig:naive_rag` | Mô hình kiến trúc tạo sinh tăng cường truy xuất truyền thống (Naive RAG) | Sơ đồ TikZ (`scale=0.88`) | **Thấp.** Sơ đồ Naive RAG rất to (chiếm hơn nửa trang), nhưng VeriScholar không dùng Naive RAG. | **BỎ** | Loại bỏ sơ đồ Naive RAG để tránh loãng trang và giải phóng không gian in ấn. |
| **5** | `2_3_advanced_rag.tex:96--210` | `fig:advanced_rag` | Mô hình kiến trúc tạo sinh tăng cường truy xuất nâng cao (Advanced RAG) | Sơ đồ TikZ (`scale=0.68`) | **Trung bình - Khá.** Sơ đồ tổng quát 3 giai đoạn theo Gao et al. 2023. | **SỬA** | Tinh gọn, liên kết chặt chẽ hơn với quy trình xử lý BBox và Hybrid RAG của VeriScholar. |
| **6** | `2_3_advanced_rag.tex:274--357` | `fig:hybrid_search_rrf` | Cơ chế tìm kiếm lai (Hybrid Search) kết hợp thuật toán hợp nhất xếp hạng đảo ngược (RRF) | Sơ đồ TikZ (`scale=0.72`) | **Rất cao.** Minh họa trực quan 3 tầng: Dense Vector Search (Cosine HNSW) song song Sparse Keyword Search (GIN BM25), tính điểm định lượng cụ thể qua RRF $k=60$. | **GIỮ** | Giữ nguyên sơ đồ TikZ xuất sắc này. Đây là đóng góp kỹ thuật cốt lõi của đề tài. Đổi `[H]` thành `[!htbp]`. |
| **7** | `2_4_knowledge_graph_wiki.tex:13--90` | `fig:graphrag_arch` | Mô hình kiến trúc tạo sinh tăng cường truy xuất dựa trên đồ thị tri thức (GraphRAG) | Sơ đồ TikZ (`scale=0.68`) | **Trung bình.** Sơ đồ luồng khái niệm trừu tượng của Microsoft Research, trùng lặp nội dung với sơ đồ hình 8. | **BỎ** | Loại bỏ để tránh lặp hình. Giữ lại sơ đồ thực thể chi tiết ở Hình 8 là đủ. |
| **8** | `2_4_knowledge_graph_wiki.tex:114--164` | `fig:academic_kg_wiki` | Cấu trúc đồ thị tri thức học thuật (Academic Knowledge Graph) và cơ chế biên dịch trang bách khoa (Graph Wiki) | Sơ đồ TikZ (`scale=0.68`) | **Rất cao.** Mô hình hóa chính xác 4 thực thể học thuật hạt nhân (`Paper`, `Method`, `Dataset`, `MetricResult`) khớp 100% với CSDL PostgreSQL và cơ chế Wiki. | **GIỮ** | Giữ nguyên sơ đồ TikZ chất lượng cao này. Đổi `[H]` thành `[!htbp]`. |
| **9** | `2_5_agentic_react.tex:21--116` | `fig:react_agent_loop` | Kiến trúc tác nhân AI độc lập (LLM-Powered Autonomous Agent) | Sơ đồ TikZ (`scale=0.72`) | **Trung bình.** Sơ đồ 4 trụ cột của Lilian Weng mang tính giáo trình đại cương. | **BỎ** | Loại bỏ để tập trung vào kiến trúc ReAct thực tế. |
| **10** | `2_5_agentic_react.tex:130--212` | `fig:planning_pattern` | Mẫu kiến trúc lập kế hoạch và phân rã nhiệm vụ (Planning Pattern) | Sơ đồ TikZ (`scale=0.75`) | **Rất thấp.** Hệ thống không cài đặt Planning Pattern tách rời. | **BỎ** | Loại bỏ hoàn toàn sơ đồ và nội dung mục 2.5.2. |
| **11** | `2_5_agentic_react.tex:234--307` | `fig:tool_use_pattern` | Mẫu kiến trúc Agent sử dụng công cụ ngoại vi (Tool Use Pattern) | Sơ đồ TikZ (`scale=0.70`) | **Khá.** Minh họa Decision Maker kết nối các công cụ. | **SỬA** | Tinh gọn và hợp nhất trực tiếp vào sơ đồ vòng lặp ReAct của Tác nhân sửa lỗi LaTeX. |
| **12** | `2_5_agentic_react.tex:330--396` | `fig:react_pattern_loop` | Mẫu kiến trúc suy luận và hành động ReAct (Reasoning and Acting Pattern) | Sơ đồ TikZ (`scale=0.72`) | **Rất cao.** Chu trình Thought $\to$ Action $\to$ Observation. | **GIỮ / SỬA** | Giữ sơ đồ này, nâng cấp bổ sung nhánh kết nối với Sandbox E2B MicroVM để thể hiện rõ bài toán tự sửa lỗi LaTeX. |
| **13** | `2_5_agentic_react.tex:415--491` | `fig:reflection_pattern_loop` | Cơ chế Reflection và tự sửa sai Reflexion (Reflection Pattern) | Sơ đồ TikZ (`scale=0.74`) | **Rất thấp.** Hệ thống không dùng vòng lặp LLM Reflection đa lượt. | **BỎ** | Loại bỏ hoàn toàn sơ đồ và nội dung mục 2.5.5. |
| **14** | `2_5_agentic_react.tex:512--588` | `fig:multi_agent_pattern` | Mẫu kiến trúc phối hợp đa Agent chuyên trách (Multi-Agent Collaboration Pattern) | Sơ đồ TikZ (`scale=0.75`) | **Rất thấp.** Hệ thống thực tế chỉ chạy Single-Agent ReAct, không có Coordinator đa tác tử. | **BỎ** | Loại bỏ hoàn toàn sơ đồ và nội dung mục 2.5.6. |
| **15** | `2_5_agentic_react.tex:608--680` | `fig:hitl_pattern` | Mẫu tương tác người trong vòng lặp (Human-in-the-Loop Pattern) | Sơ đồ TikZ (`scale=0.72`) | **Rất thấp.** Hệ thống không dùng cơ chế ngắt luồng khóa tiến trình (Interrupt Checkpoint). | **BỎ** | Loại bỏ hoàn toàn sơ đồ và nội dung mục 2.5.7. |
| **16** | `2_6_langgraph.tex:11` | `fig:logo_langgraph` | LangGraph | Ảnh PNG (`3.2cm`) | **Không có giá trị học thuật.** Logo LangGraph tải từ mạng. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **17** | `2_7_azure_e2b_byok.tex:11` | `fig:logo_azure` | Microsoft Azure | Ảnh PNG (`3.2cm`) | **Không có giá trị học thuật.** Logo Azure tải từ mạng. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **18** | `2_7_azure_e2b_byok.tex:29` | `fig:logo_e2b` | E2B Sandbox | Ảnh PNG (`3.2cm`) | **Không có giá trị học thuật.** Logo E2B tải từ mạng. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **19** | `2_8_langfuse.tex:11` | `fig:logo_langfuse` | Langfuse | Ảnh PNG (`3.2cm`) | **Không có giá trị học thuật.** Logo Langfuse tải từ mạng. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **20** | `2_9_tools_languages.tex:13` | `fig:logo_python` | Python | Ảnh PNG (`2.9cm`) | **Không có giá trị học thuật.** Logo Python giáo trình. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **21** | `2_9_tools_languages.tex:20` | `fig:logo_fastapi` | FastAPI | Ảnh PNG (`2.9cm`) | **Không có giá trị học thuật.** Logo FastAPI giáo trình. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **22** | `2_9_tools_languages.tex:37` | `fig:logo_react` | React | Ảnh PNG (`3.2cm`) | **Không có giá trị học thuật.** Logo React giáo trình. | **BỎ** | Loại bỏ hoàn toàn hình logo. |
| **23** | `2_9_tools_languages.tex:53` | `fig:logo_docker` | Docker | Ảnh PNG (`3.2cm`) | **Không có giá trị học thuật.** Logo Docker giáo trình. | **BỎ** | Loại bỏ hoàn toàn hình logo. |

### Thống kê tổng hợp kết quả thẩm định hình ảnh:
- **Tổng số hình ảnh / sơ đồ hiện tại:** 23 hình.
- **Kiến nghị LOẠI BỎ (BỎ):** **18 hình** (Tỷ lệ loại bỏ: **78,3%**), bao gồm:
  + Toàn bộ **11 ảnh logo PNG** (PostgreSQL, Redis, LangGraph, Azure, E2B, Langfuse, Python, FastAPI, React, Docker).
  + **7 sơ đồ TikZ** lý thuyết chung chung hoặc không áp dụng trong thực tế dự án (Naive RAG, GraphRAG trừu tượng, Autonomous Agent 4 pillars, Planning Pattern, Reflection Pattern, Multi-Agent Collaboration, HITL Pattern).
- **Kiến nghị GIỮ NGUYÊN (GIỮ):** **3 sơ đồ TikZ** chất lượng cao, đúng trọng tâm kỹ thuật cốt lõi:
  + `fig:hexagonal_arch`: Kiến trúc Lục giác Ports & Adapters.
  + `fig:hybrid_search_rrf`: Cơ chế tìm kiếm lai Hybrid Search và hợp nhất xếp hạng RRF ($k=60$).
  + `fig:academic_kg_wiki`: Cấu trúc đồ thị tri thức 4 thực thể học thuật và biên dịch Graph Wiki.
- **Kiến nghị CHỈNH SỬA / HỢP NHẤT (SỬA):** **2 sơ đồ TikZ**:
  + `fig:advanced_rag`: Tinh gọn luồng xử lý.
  + `fig:react_pattern_loop` (hợp nhất với `fig:tool_use_pattern`): Biểu diễn vòng lặp ReAct gọi công cụ E2B MicroVM Sandbox tự động sửa lỗi cú pháp LaTeX.

$\rightarrow$ **Kết quả sau tinh gọn:** Chương 2 chỉ còn lại **4 -- 5 sơ đồ kỹ thuật vector TikZ xuất sắc**, sạch bóng 100% rác logo, giải phóng trực tiếp hơn **12 trang giấy** chiếm dụng lãng phí!

---

## PHẦN 4: DANH SÁCH KIẾN NGHỊ HÀNH ĐỘNG TINH GỌN TOÀN DIỆN CHO CHƯƠNG 2

Nhằm đưa Chương 2 từ **29 trang** về đúng **ngân sách chuẩn 10 -- 12 trang**, nâng tầm hàm lượng học thuật và tuân thủ 100% quy chế của Khoa CNTT — HUMG và `AGENTS.md`, kiến nghị lộ trình 5 hành động tinh gọn cụ thể như sau:

### Hành Động 1: Tái cấu trúc phân rã mục từ 9 mục manh mún thành 5 mục chuẩn mực

Quy hoạch lại toàn bộ cấu trúc Chương 2 thành đúng **5 mục lớn chuyên sâu** (khớp với kiến trúc hệ thống và bản đồ `ROADMAP.md`):

```
CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ NỀN TẢNG (10 -- 12 trang)
├── 2.1. Kiến trúc Lục giác và Phân tầng hệ thống (Hexagonal Architecture)
│   ├── 2.1.1. Nguyên lý phân tách ranh giới và đảo ngược phụ thuộc (DIP)
│   ├── 2.1.2. Cơ chế cổng trừu tượng và bộ điều hợp (Ports and Adapters)
│   └── 2.1.3. Luận giải lựa chọn kiến trúc trong phát triển phần mềm AI
├── 2.2. Cơ sở dữ liệu hợp nhất quan hệ và véc-tơ ngữ nghĩa
│   ├── 2.2.1. Hệ quản trị cơ sở dữ liệu tích hợp PostgreSQL và tiện ích pgvector
│   ├── 2.2.2. Cấu trúc chỉ mục láng giềng gần đúng phân tầng HNSW
│   ├── 2.2.3. Hệ thống đệm dữ liệu truy cập ngẫu nhiên Redis
│   └── 2.2.4. Luận giải lựa chọn PostgreSQL pgvector thay thế Dedicated Vector DB
├── 2.3. Cơ chế truy xuất học thuật kết hợp và chuẩn hóa không gian tài liệu
│   ├── 2.3.1. Phân tích bố cục tài liệu PDF hai cột và chuẩn hóa tọa độ hộp viền
│   ├── 2.3.2. Cơ chế tìm kiếm lai (Hybrid Search: Cosine HNSW và GIN BM25)
│   ├── 2.3.3. Thuật toán hợp nhất xếp hạng đảo ngược (RRF) và Tái xếp hạng
│   └── 2.3.4. Cổng phân loại độ tin cậy và cơ chế kiểm soát ảo giác (CRAG)
├── 2.4. Mô hình đồ thị tri thức và cơ chế bách khoa cộng đồng
│   ├── 2.4.1. Mô hình đồ thị tri thức học thuật 4 thực thể trên quan hệ ACID
│   ├── 2.4.2. Thuật toán phân cụm cộng đồng Louvain và hàm mục tiêu Modularity Q
│   └── 2.4.3. Cơ chế biên dịch trước trang bách khoa tri thức (Graph Wiki)
└── 2.5. Tác nhân ReAct tự phục hồi lỗi và an toàn bảo mật
    ├── 2.5.1. Mô hình suy luận và hành động ReAct phối hợp gọi công cụ
    ├── 2.5.2. Máy trạng thái hữu hạn LangGraph và điều phối luồng tự sửa lỗi LaTeX
    ├── 2.5.3. Môi trường máy ảo siêu nhỏ cô lập hạt nhân E2B MicroVM
    └── 2.5.4. Két khóa cá nhân BYOK và chuẩn mã hóa đối xứng xác thực AES-256-GCM
```

* **Xóa bỏ hoàn toàn Mục 2.9 (Các công cụ và ngôn ngữ phát triển hệ thống):** Toàn bộ lý thuyết sơ cấp về Python, TypeScript, React, Docker được loại bỏ hoàn toàn khỏi Chương 2. Các công nghệ này chỉ được tóm tắt trong một bảng cấu hình môi trường triển khai thực tế ở Chương 4 hoặc Lời mở đầu.
* **Tích hợp Langfuse (Mục 2.8 cũ):** Tích hợp ngắn gọn 1 đoạn văn vào Mục 2.5 dưới vai trò hệ thống quan sát truy vết suy luận (LLM Tracing & Observability) không lưu vết khóa bí mật, bỏ hẳn mục cấp 1 độc lập.

### Hành Động 2: Chuẩn hóa 100% tiêu đề theo quy tắc Danh ngữ hóa (Triệt tiêu "... là gì?")

Sửa đổi dứt điểm 11 tiêu đề tiểu mục vi phạm:
- `PostgreSQL là gì?` $\rightarrow$ `Hệ quản trị cơ sở dữ liệu đối tượng quan hệ PostgreSQL`
- `Redis là gì?` $\rightarrow$ `Hệ thống đệm dữ liệu bộ nhớ truy cập nhanh Redis`
- `Hexagonal Architecture là gì?` $\rightarrow$ `Nguyên lý kiến trúc Lục giác (Ports and Adapters)`
- `RAG là gì?` $\rightarrow$ `Nguyên lý tạo sinh tăng cường truy xuất tri thức`
- `Advanced RAG là gì?` $\rightarrow$ `Kiến trúc RAG nâng cao đa giai đoạn`
- `GraphRAG là gì?` $\rightarrow$ `Kiến trúc truy xuất tăng cường dựa trên đồ thị tri thức`
- `Knowledge Graph là gì?` $\rightarrow$ `Mô hình biểu diễn mạng lưới tri thức học thuật`
- `Graph Wiki là gì?` $\rightarrow$ `Cơ chế trang bách khoa cộng đồng biên dịch sẵn`
- `LangGraph là gì?` $\rightarrow$ `Khung điều phối tác tử có trạng thái LangGraph`
- `E2B Sandbox là gì?` $\rightarrow$ `Môi trường máy ảo siêu nhỏ cô lập hạt nhân E2B MicroVM`
- `Langfuse là gì?` $\rightarrow$ `Nền tảng quan sát và truy vết tác tử Langfuse`

### Hành Động 3: Thanh lọc triệt để 18 hình ảnh / sơ đồ dư thừa

1. **Xóa bỏ 11 khối chèn ảnh logo:** Xóa bỏ toàn bộ các tệp ảnh logo PNG trong `figures/logos/` khỏi mã nguồn `.tex` của Chương 2.
2. **Xóa bỏ 7 sơ đồ TikZ lý thuyết không dùng:**
   - Xóa `fig:naive_rag` trong `2_3_advanced_rag.tex`.
   - Xóa `fig:graphrag_arch` trong `2_4_knowledge_graph_wiki.tex`.
   - Xóa 5 sơ đồ trong `2_5_agentic_react.tex`: `fig:react_agent_loop`, `fig:planning_pattern`, `fig:reflection_pattern_loop`, `fig:multi_agent_pattern`, `fig:hitl_pattern`.
3. **Chỉnh sửa nâng cấp 2 sơ đồ:**
   - Hợp nhất `fig:react_pattern_loop` với `fig:tool_use_pattern` thành 1 sơ đồ TikZ duy nhất thể hiện Tác nhân ReAct điều phối công cụ E2B MicroVM tự sửa lỗi cú pháp LaTeX.

### Hành Động 4: Sửa toàn bộ lỗi định dạng bảng, caption và thông số vị trí Floats

1. **Sửa vị trí Caption của Bảng `tab:search_comparison`:**
   Chuyển `\caption{...}` từ vị trí dưới bảng lên TRÊN bảng theo đúng chuẩn quy chế HUMG.
2. **Chuyển đổi sang môi trường `tabularx`:**
   Thay `\begin{tabular}{|p{3.0cm}|p{5.2cm}|p{5.2cm}|}` bằng:
   ```latex
   \begin{table}[!htbp]
   \centering
   \caption{So sánh đặc tính kỹ thuật giữa tìm kiếm ngữ nghĩa Dense Vector và từ khóa BM25}
   \label{tab:search_comparison}
   \singlespacing
   \small
   \begin{tabularx}{\textwidth}{|>{\raggedright\arraybackslash\bfseries}p{3.2cm}|X|X|}
   \hline
   \textbf{Tiêu chí so sánh} & \textbf{Dense Vector (Cosine HNSW)} & \textbf{Sparse Keyword (BM25 GIN)} \\
   \hline
   ...
   \hline
   \end{tabularx}
   \end{table}
   ```
3. **Thay thế toàn bộ `[H]` thành `[!htbp]`:**
   Đổi tất cả khai báo `\begin{figure}[H]` thành `\begin{figure}[!htbp]`.

### Hành Động 5: Bổ sung các nội dung khoa học chuyên sâu còn thiếu

1. **Bổ sung công thức hàm mục tiêu Modularity $Q$ của Louvain** vào Mục 2.4:
   \begin{equation}
   \label{eq:louvain_modularity}
   Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)
   \end{equation}
   kèm giải thích tường minh các tham số: $A_{ij}$ là trọng số cạnh, $k_i, k_j$ là bậc của đỉnh, $m$ là tổng trọng số các cạnh trong mạng, $c_i$ là cộng đồng chứa đỉnh $i$, và $\delta$ là hàm Kronecker.
2. **Bổ sung Bảng so sánh luận chứng "Tại sao chọn" (Why-chosen Table):**
   - Bổ sung bảng so sánh đa tiêu chí giữa PostgreSQL pgvector với Dedicated Vector DB (Milvus, Pinecone, Qdrant) trên 5 tiêu chí: Toàn vẹn giao dịch ACID, chi phí hạ tầng, độ phức tạp kiến trúc, độ trễ truy vấn kết hợp và khả năng sao lưu phục hồi.
   - Bổ sung đoạn văn khẳng định sự lựa chọn dựa trên ràng buộc triển khai thực tế của đề tài tại VinUni.

---

## KẾT LUẬN THẨM ĐỊNH

Báo cáo rà soát độc lập đã chỉ ra toàn diện và chính xác các điểm nghẽn của Chương 2:
1. **Về nội dung:** Bị loãng do chép lý thuyết đại cương (Python, React, Docker, Naive RAG) và diễn giải 4 mẫu kiến trúc tác nhân "ảo" không dùng thật; thiếu luận chứng "Tại sao chọn" và thiếu công thức toán học Modularity $Q$.
2. **Về hình thức:** 11/11 tiểu mục vi phạm tiêu đề dạng câu hỏi "... là gì?", 8/9 mục cấp 1 vi phạm danh ngữ hóa; caption bảng đặt sai vị trí (dưới bảng); 100% floats lạm dụng `[H]`.
3. **Về hình ảnh:** Lạm dụng 11 ảnh logo PNG vô bổ học thuật và 7 sơ đồ TikZ lý thuyết ngoài luồng.
4. **Về quy mô:** Phình to 29 trang (so với ngân sách 10--12 trang).

Việc thực thi nghiêm túc 5 nhóm hành động kiến nghị tinh gọn trên sẽ giúp Chương 2 giảm ngay **17--19 trang**, đưa dung lượng về mức chuẩn mực **10--12 trang**, loại bỏ 100% rác hình ảnh, nâng cao vượt bậc tính chuyên nghiệp học thuật và bảo đảm sự đồng bộ hoàn hảo giữa báo cáo với mã nguồn thực tế của hệ thống VeriScholar.
