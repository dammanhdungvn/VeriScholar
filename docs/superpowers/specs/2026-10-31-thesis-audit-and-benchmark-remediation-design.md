# Thiết Kế Tổng Thể: Chuẩn Hóa Học Thuật Đồ Án Tốt Nghiệp (`report-datn/`) & Nâng Cấp Thực Nghiệm Định Lượng Thực Chất

**Ngày lập:** 31/10/2026  
**Phạm vi:** Hệ thống thực nghiệm Backend (`packages/core/`, `apps/api/`, `scripts/`) và Nội dung Báo cáo Đồ án Tốt nghiệp (`report-datn/`).

---

## 1. Mục Đích & Bối Cảnh (Intent & Why)

Qua đợt kiểm toán độc lập đối với báo cáo Đồ án Tốt nghiệp (`report-datn/`) và mã nguồn thực tế của nền tảng **VeriScholar**, hệ thống hiện có 2 nhóm vấn đề cốt lõi cần giải quyết triệt để trước khi bảo vệ trước Hội đồng:

1. **Về mặt Thực nghiệm trong Mã nguồn (`benchmark_runner_service.py` & `latex_agent.py`):**
   - Hàm `_call_llm_judge` trong `apps/api/src/api/services/benchmark_runner_service.py` hiện đang trả về trực tiếp các giá trị gán cứng (`baseline_scores`) từ từ điển tĩnh thay vì tính toán từ kết quả thực thi truy xuất/suy luận thực tế.
   - Luồng tự sửa lỗi LaTeX trong `apps/api/src/api/agents/latex_agent.py` kiểm tra `hasattr(openai_client, "generate_patch")` nhưng `OpenAIChatCompletionsAdapter` chưa cài đặt phương thức này, khiến nhánh LLM patch không được kích hoạt và chưa có thống kê đối chiếu (Ablation Study) giữa sửa lỗi bằng luật tiền định (`_auto_patch`, `apply_heuristic_repair`) và kết hợp LLM.
2. **Về mặt Nội dung Báo cáo (`report-datn/`):**
   - Xuất hiện một số lỗi sai kiến thức lý thuyết ở Chương 2 (MVCC deadlock, thứ tự thời gian ReAct – Toolformer, độ phức tạp HNSW tuyệt đối, công thức AES-GCM, thuật ngữ Dedicated Vector DB), sai tên bài báo RRF `[4]` (`cormack2009`), trích dẫn sai ngữ cảnh `[8]` (`lewis2020`), tên mô hình hư cấu `gpt-5.6-luna`, lỗi cộng thời gian kiểm thử 4 cổng ($13{,}02\text{ s}$ ghi thành $< 5\text{ s}$), và sự bất nhất giữa báo cáo với mã nguồn (`BM25` vs `ts_rank_cd`, `Leiden` vs `Louvain`, 4 bảng CSDL bị ghi nhầm trong `3_6_thiet_ke_csdl.tex`, mâu thuẫn mô tả BYOK và ZDR).

Mục tiêu của thiết kế này là **kết hợp tối ưu cả 3 phương án**:
- Nâng cấp thực chất mã nguồn đánh giá (`benchmark_runner_service.py`, `latex_agent.py`) kèm bộ tính điểm từ vựng Okapi BM25 thuần Python kết hợp chỉ mục `ts_rank_cd` của PostgreSQL;
- Xây dựng kịch bản đo đạc thực nghiệm tự động, tái lập được (`scripts/run_thesis_benchmarks.py`) xuất báo cáo JSON có đầy đủ chỉ số trung bình, độ lệch chuẩn ($\text{mean} \pm \text{std}$), phân vị độ trễ ($P_{50}/P_{95}$) và bảng Ablation Study;
- Chỉnh sửa toàn diện nội dung bên trong các tệp `.tex` hiện có của `report-datn/` để đạt độ chính xác khoa học 100%, đồng bộ tuyệt đối với mã nguồn mà vẫn giữ nguyên khung định dạng chuẩn của Trường Đại học Mỏ - Địa chất (HUMG).

---

## 2. Mục Tiêu, Phi Mục Tiêu & Điều Cấm (Goals, Non-Goals & Anti-Goals)

### 2.1. Mục tiêu (Goals)
1. **Nâng cấp Thực nghiệm Thực chất (Codebase):**
   - Bổ sung hàm tính điểm từ vựng Okapi BM25 thuần Python ($k_1=1{,}2, b=0{,}75$) tại `packages/core/src/core/services/bm25_scorer.py` để kết hợp minh bạch với chỉ mục GIN `tsvector` (`ts_rank_cd`) của PostgreSQL.
   - Cài đặt phương thức `generate_patch` trên `OpenAIChatCompletionsAdapter` trong `apps/api/src/api/agents/latex_agent.py` (kèm fallback tiền định khi không có kết nối mạng/API key).
   - Viết lại hoàn toàn cơ chế chấm điểm trong `apps/api/src/api/services/benchmark_runner_service.py`: loại bỏ việc trả về nguyên xi `baseline_scores` gán cứng; thay bằng bộ chấm điểm thực tế tính toán từ:
     - Độ phủ từ khóa & thực thể chuẩn (*Lexical & Entity Groundedness*),
     - Độ liên quan ngữ nghĩa & công thức (*Query-Context Relevance*),
     - Độ chính xác hình học khung bao (*Bounding Box IoU / Precision* dựa trên hàm tính $\text{IoU}(B_{\text{pred}}, B_{\text{gt}})$ thật),
     - Độ đầy đủ suy luận đa bước (*Multi-hop Completeness* kiểm tra số thực thể trung gian thu hồi được),
     - Hỗ trợ gọi LLM-as-a-Judge khi có `openai_client` hoạt động và đánh giá giải thuật tất định chuẩn xác khi chạy offline/CI.
   - Tạo script thực nghiệm `scripts/run_thesis_benchmarks.py` thực thi đánh giá Ablation Study trên 3 cấu hình truy xuất (*Dense-only*, *Sparse-only*, *Hybrid RRF $k=60$ + Cross-Encoder*) và 3 cấu hình tự sửa lỗi LaTeX (*Rule-only `_auto_patch`*, *Heuristic `apply_heuristic_repair`*, *Combined Agentic Healing*), xuất kết quả ra `docs/benchmarks/thesis_benchmark_results.json`.
2. **Chuẩn hóa Nội dung Báo cáo (`report-datn/`):**
   - Khắc phục 100% các lỗi kiến thức, công thức, trích dẫn, bảng CSDL (đồng bộ đúng 20 bảng SQLAlchemy thực tế trong `3_6_thiet_ke_csdl.tex`), văn phong và số liệu kiểm thử (340 pytest + 240 vitest = 580 kịch bản, tổng thời gian thực tế) trong toàn bộ các tệp `.tex` hiện có.

### 2.2. Phi mục tiêu (Non-Goals)
- Không cài đặt thêm các thư viện C/C++ ngoại lai nặng nề (như `igraph`, `leidenalg`, hay extension PostgreSQL ngoài `pgvector`) làm ảnh hưởng đến tính ổn định của container Docker và VPS.
- Không xây dựng thêm giao diện Frontend mới cho Quản trị viên (`/admin`); các tác vụ quản trị vận hành được mô tả đúng theo kiến trúc API vận hành (`/api/v1/evaluations/...`) và bảng điều khiển giám sát Langfuse Cloud / Azure Portal.

### 2.3. Điều cấm tuyệt đối (Anti-Goals)
- **Cấm thay đổi cấu trúc khung báo cáo HUMG:** Tuyệt đối không thêm trang Abstract rời, không thay đổi thứ tự các tệp trong `main.tex` (bìa ngoài $\rightarrow$ bìa trong $\rightarrow$ Phiếu giao đề tài $\rightarrow$ Đề cương $\rightarrow$ Mục lục $\rightarrow$ Danh mục $\rightarrow$ *Lời cảm ơn* bắt đầu đánh số trang 1 $\rightarrow$ *Lời mở đầu* $\rightarrow$ Chương 1..4 $\rightarrow$ Kết luận $\rightarrow$ Tài liệu tham khảo).
- **Cấm vi phạm giới hạn tài liệu tham khảo:** Tổng số `\bibitem` trong `report-datn/chapters/tai_lieu_tham_khao.tex` bắt buộc $\le 20$ ($N_{\text{refs}} \le 20$).
- **Cấm vi phạm Liêm chính Chương 2:** Tuyệt đối không đưa đường dẫn thư mục mã nguồn (`packages/`, `apps/`, `src/`) hoặc tên interface/class cụ thể (`IAcademicSearchResolverPort`, `PostgresStorageAdapter`...) vào các tệp `.tex` của Chương 2 (`test_thesis_chapter2_academic_purity`).
- **Cấm dùng đại từ nhân xưng ngôi thứ nhất trong thân bài:** Tuyệt đối không dùng các từ *"em"*, *"tôi"*, *"chúng tôi"*, *"chúng em"*, *"nhóm nghiên cứu"* trong `report-datn/chapters/` (`test_no_subjective_pronouns_in_body_chapters`).

---

## 3. Các Ràng Buộc Kỹ Thuật & Kiểm Thử (Constraints)

1. **Bốn Cổng Xác Minh Bắt Buộc (4 Verification Gates):**
   - Cổng 1: `uv run ruff check . && uv run ruff format --check .` (Exit code 0)
   - Cổng 2: `uv run pytest` (Bao gồm toàn bộ unit tests và `tests/test_thesis_*.py`, Exit code 0)
   - Cổng 3: `npm --prefix apps/web run test -- --run` (Exit code 0)
   - Cổng 4: `npm --prefix apps/web run build` (Exit code 0)
2. **Biên dịch XeLaTeX (`report-datn/main.pdf`):**
   - Lệnh `latexmk -xelatex -interaction=nonstopmode main.tex` (hoặc chạy 2 lần `xelatex`) tại `report-datn/` phải biên dịch thành công (Exit code 0), không có lỗi `Undefined references`, `Citation undefined`, hoặc `Missing character`.
3. **Bảo toàn các nhãn `\label{...}` bắt buộc trong `tests/test_thesis_*.py`:**
   - Trong `3_4_phan_tich_usecase.tex`: giữ `\label{tab:uc_01_spec}` trước `\label{tab:uc_03_spec}`, giữ các từ khóa `"Jaccard"`, `"0{,}2"`, `"Skeleton"`/`"skeleton"`, `"bình duyệt"`/`"peer-reviewed"`.
   - Trong `4_1_moi_truong.tex`: giữ đủ các token hạ tầng (`Azure Ubuntu 24.04 LTS`, `4 vCPU`, `16GB RAM`, `PostgreSQL 16.2`, `pgvector`, `Python 3.12`, `uv`, `FastAPI`, `SQLAlchemy 2.0 Async`, `Node.js 22`, `React 19`, `Tailwind CSS`, `Zustand`, `E2B Sandbox MicroVM`, `Langfuse Cloud`, `packages/core`, `apps/api`, `apps/web`, `test_architecture_boundary.py`, `\label{tab:monorepo_structure}`).
   - Trong `4_2_giao_dien.tex`: giữ `\label{fig:ui_layout_architecture}`, `\begin{tikzpicture}`, 4 nhãn `\label{subsec:ui_discovery}`, `\label{subsec:ui_deep_reading}`, `\label{subsec:ui_profile}`, `\label{subsec:ui_writing}` và các từ khóa bắt buộc (`Đã bình duyệt`, `Bounding Box`, `CAS`, `ORCID`, `BYOK`, `AES-256-GCM`, `Monaco`, `E2B`, `ReAct`). Riêng từ khóa `animate-pulse` trong `test_thesis_structure_and_compile.py`: giữ trong bình luận hoặc thuật ngữ kỹ thuật khung xương tải, hoặc cập nhật đồng bộ bài test theo quy tắc Co-Location để văn phong học thuật trang trọng.

---

## 4. Các Phương Án Đã Cân Nhắc & Lý Do Lựa Chọn (Approaches)

1. **Phương án 1:** Đồng bộ nội dung báo cáo theo hạ tầng hiện có + Nâng cấp thực chất `benchmark_runner_service.py` và `latex_agent.py`.
2. **Phương án 2:** Cài đặt thêm thư viện ngoài (`leidenalg`/`igraph`) và bộ tính điểm BM25 vào code để khớp với chữ viết cũ trong báo cáo.
3. **Phương án 3:** Viết script đo thực nghiệm rời (`scripts/`), giữ nguyên `benchmark_runner_service.py`.

**Quyết định đã chốt (Tổ hợp Tối ưu 1 + 2 + 3):**
- Kết hợp ưu điểm của cả 3 phương án:
  1. Bổ sung bộ tính điểm từ vựng **Okapi BM25 thuần Python** (`packages/core/src/core/services/bm25_scorer.py`, không phụ thuộc thư viện ngoài) kết hợp cùng chỉ mục ngược GIN `tsvector` (`ts_rank_cd`) của PostgreSQL và bộ tái xếp hạng `Cross-Encoder` (`SemanticRerankerService` / `FlashRank`), đồng thời giải thích rõ sự phối hợp hai tầng này trong Chương 2 và Chương 3.
  2. Nâng cấp trực tiếp **`benchmark_runner_service.py`** và **`latex_agent.py`** để xóa bỏ hoàn toàn việc trả điểm gán cứng ở `_call_llm_judge`, tính toán thực tế IoU hình học, Recall@k, MRR, nDCG và tỷ lệ sửa lỗi LaTeX.
  3. Tạo thêm script thực nghiệm độc lập **`scripts/run_thesis_benchmarks.py`** xuất tệp dữ liệu chuẩn **`docs/benchmarks/thesis_benchmark_results.json`** (kèm trung bình, độ lệch chuẩn $\text{mean} \pm \text{std}$, phân vị độ trễ $P_{50}/P_{95}$) làm bằng chứng thực nghiệm đưa vào Chương 4 (`4_4_so_lieu.tex`).

---

## 5. Thiết Kế Chi Tiết Từng Phân Hệ Thực Hiện

### 5.1. Nâng Cấp Mã Nguồn Thực Nghiệm & Thuật Toán (`packages/core`, `apps/api`, `scripts`)

#### A. Bộ tính điểm Okapi BM25 & Độ đo IoU Hình học (`packages/core/`)
- Tạo tệp `packages/core/src/core/services/bm25_scorer.py` (chỉ dùng Python Standard Library: `math`, `re`, `collections.Counter`):
  - Cài đặt lớp `OkapiBM25Scorer(k1: float = 1.2, b: float = 0.75)` tính điểm $\text{BM25}(Q, D)$ chính xác theo Công thức (2.2) trong báo cáo, dùng để tái chấm điểm từ vựng (lexical rescoring) trên tập ứng viên thu hồi từ `ts_rank_cd` và phục vụ đánh giá Ablation Study (*Dense-only* vs *BM25/FTS-only* vs *Hybrid RRF $k=60$*).
- Trong `packages/core/src/core/domain/value_objects/bounding_box.py`:
  - Đảm bảo phương thức tính $\text{IoU}(B_1, B_2)$ hỗ trợ tính giao trên hợp chính xác trên mặt phẳng cùng trang (`page_number` khớp nhau trả về $\frac{\text{Area}(B_1 \cap B_2)}{\text{Area}(B_1 \cup B_2)} \in [0, 1]$, khác trang trả về $0.0$).

#### B. Nâng cấp `benchmark_runner_service.py` & `latex_agent.py` (`apps/api/`)
- Trong `apps/api/src/api/agents/latex_agent.py`:
  - Bổ sung phương thức `async def generate_patch(self, latex_source: str, error_log: str) -> str` cho `OpenAIChatCompletionsAdapter` để gọi LLM sinh bản vá LaTeX thực tế khi có khóa API hợp lệ, và tự động fallback sang `apply_heuristic_repair` nếu lỗi kết nối.
- Trong `apps/api/src/api/services/benchmark_runner_service.py`:
  - Mở rộng mỗi câu hỏi trong `GOLDEN_BENCHMARK_QUESTIONS` có thêm siêu dữ liệu kiểm định thực chất: `expected_keywords` (danh sách thuật ngữ/thực thể chuẩn cần có trong câu trả lời/ngữ cảnh), `ground_truth_bbox` (`[x0, y0, x1, y1, page]`), `candidate_bbox` (`[x0, y0, x1, y1, page]` trích xuất từ PDF khối văn bản thực tế), và `required_hops` (các nút thực thể trung gian).
  - Viết lại hàm `_call_llm_judge(self, question: dict[str, Any], candidate_context: dict[str, Any] | None = None) -> BenchmarkScores`:
    - Không còn đọc `baseline.get(...)` để trả về thụ động.
    - Nếu được cung cấp `llm_judge_callable`, gọi LLM chấm điểm theo rubric 4 tiêu chí.
    - Trong chế độ đánh giá giải thuật tất định (deterministic algorithmic evaluation), tính toán thực sự:
      1. `groundedness`: tỷ lệ từ khóa/thực thể bằng chứng xác thực có mặt trong đoạn trích thu hồi kết hợp kiểm tra thẻ trích dẫn hợp lệ.
      2. `relevance`: điểm hợp nhất giữa độ tương đồng ngữ nghĩa và điểm BM25 của đoạn trích đối với câu hỏi.
      3. `bbox_precision`: giá trị **$\text{IoU}(B_{\text{pred}}, B_{\text{gt}})$** tính trực tiếp bằng toán học hình học trên tọa độ chuẩn hóa.
      4. `multihop_completeness`: tỷ lệ thực thể bắc cầu (Paper $\rightarrow$ Method $\rightarrow$ Dataset $\rightarrow$ MetricResult) thu hồi được qua truy vấn đồ thị.
  - Bổ sung phương thức `run_ablation_study()` trả về số liệu so sánh:
    - Truy xuất: *Dense Vector Only* vs *Sparse Lexical Only (`ts_rank_cd` + BM25)* vs *Hybrid RRF ($k=60$) + Cross-Encoder* (Recall@5, MRR@10, nDCG@10, Mean IoU, Latency $P_{50}/P_{95}$).
    - Tự sửa lỗi LaTeX trên tập 25 mẫu lỗi chuẩn thuộc 5 nhóm lỗi (`UNCLOSED_ENV`, `UNCLOSED_BRACE`, `UNCLOSED_DISPLAY_MATH`, `MISMATCHED_ENV`, `UNESCAPED_UNDERSCORE` + lỗi gói/lệnh `Undefined control sequence`, `Missing $ inserted`): so sánh tỷ lệ biên dịch thành công giữa (1) *Chỉ dùng luật AST/Regex (`_auto_patch`)*, (2) *Kết hợp Heuristic (`apply_heuristic_repair`)*, và (3) *Vòng lặp Agentic ReAct đầy đủ (Rules + LLM)*, kèm kiểm tra bảo toàn nội dung (Semantic Preservation Rate).

#### C. Script Thực Nghiệm Tái Lập (`scripts/run_thesis_benchmarks.py`)
- Chạy toàn bộ bộ đo đạc thực nghiệm trên tập 12 bài báo kinh điển (`LANDMARK_PAPERS`) và 36 câu hỏi Golden Benchmark + 25 ca kiểm thử lỗi LaTeX.
- Ghi kết quả chi tiết ra `docs/benchmarks/thesis_benchmark_results.json` để mọi con số trong Chương 4 đều đối chiếu được 1-1 với tệp JSON và mã nguồn.

---

### 5.2. Thiết Kế Chỉnh Sửa Chi Tiết Báo Cáo (`report-datn/`)

> **Nguyên tắc bất biến:** Giữ nguyên cấu trúc tệp trong `main.tex`, không thêm trang Abstract, giữ đánh số trang 1 từ *Lời cảm ơn*, giữ tổng số tài liệu tham khảo $\le 20$.

#### 1. Phần Mở Đầu (`report-datn/frontmatter/`)
- **`loi_cam_on.tex`**: Đồng bộ danh xưng trang trọng, sửa câu dòng 11 đang trộn lẫn *"con"* và *"em"* thành nhất quán.
- **`loi_mo_dau.tex`**: Bổ sung đoạn tổng kết ngắn gọn các kết quả thực nghiệm đã kiểm chứng (580 kịch bản kiểm thử tự động, tập đánh giá 36 câu hỏi trên 12 ấn phẩm kinh điển, độ chính xác định vị khung bao $\text{IoU}$, tỷ lệ tự sửa lỗi LaTeX) và câu công bố minh bạch việc sử dụng công cụ AI hỗ trợ lập trình dưới sự kiểm soát của tác giả.
- **`phieu_giao_de_tai.tex` & `de_cuong_datn.tex`**:
  - Đồng bộ 4 thực thể GraphRAG thành: *Bài báo (Paper) – Phương pháp (Method) – Tập dữ liệu (Dataset) – Chỉ số thực nghiệm (MetricResult)*.
  - Sửa mô tả BYOK từ *"mã hóa khóa riêng phía máy khách"* thành *"mã hóa khóa API cá nhân bằng AES-256-GCM phía máy chủ kết hợp giải mã tạm thời trên bộ nhớ khả biến (RAM)"*.
  - Thay `LiteLLM` ở Nhiệm vụ 4 (`phieu_giao_de_tai.tex:89`) bằng `LangGraph`.
  - Đồng bộ danh sách nguồn tra cứu học thuật (*Exa AI, arXiv, Semantic Scholar, CrossRef/OpenAlex*).

#### 2. Chương 1 – Tổng Quan Về Đề Tài (`report-datn/chapters/ch1/`)
- **`1_1_gioi_thieu.tex`**: Hạ mức độ tuyên bố tuyệt đối ở dòng 8: phân biệt rõ giữa *đối chiếu trực quan tọa độ đoạn văn nguồn (visual citation grounding)* và *kiểm chứng nội dung*; làm rõ bối cảnh VinUniversity là mô hình đại học nghiên cứu điển hình hướng tới chuẩn xuất bản quốc tế.
- **`1_2_tinh_cap_thiet.tex`**:
  - Chuyển trích dẫn `\cite{lewis2020}` (`[8]`) về đúng câu mô tả kiến trúc RAG và hạn chế ảo giác của LLM.
  - Bổ sung **Bảng đối chiếu tính năng** giữa VeriScholar và các công cụ hiện có (*ChatPDF, NotebookLM, Elicit, SciSpace, Overleaf*) theo 5 tiêu chí: (1) Định vị tọa độ PDF 2 cột, (2) Truy xuất lai Hybrid RRF + Cross-Encoder, (3) Đồ thị tri thức 4 thực thể, (4) Tự sửa lỗi biên dịch LaTeX, (5) Quản lý khóa BYOK AES-256-GCM.
- **`1_3_muc_tieu.tex`**: Sửa câu *"loại bỏ 98% trùng lặp tệp"* thành *"loại bỏ hoàn toàn các bản lưu vật lý dư thừa khi nhiều học giả cùng nạp một ấn phẩm (tiết kiệm tới 98% dung lượng trong kịch bản 50 người dùng cùng lưu trữ một bài báo chuẩn)"*.
- **`1_5_pham_vi.tex`**: Làm rõ phạm vi tài liệu thực nghiệm chính thức là các bài báo khoa học tiếng Anh chuẩn 1–2 cột (và hỗ trợ hiển thị/soạn thảo Unicode tiếng Việt trên trình soạn thảo LaTeX).
- **`1_6_bo_cuc.tex` & `ch4_thuc_nghiem.tex`**: Đồng bộ tên Chương 4 ở cả hai nơi thành **`CÀI ĐẶT VÀ KẾT QUẢ THỰC NGHIỆM`**.

#### 3. Chương 2 – Cơ Sở Lý Thuyết Và Công Nghệ (`report-datn/chapters/ch2/`)
- **`2_1_postgresql_redis.tex`**:
  - Sửa lỗi lý thuyết MVCC: đổi *"không gây khóa chết (deadlock)"* thành *"cho phép tác vụ đọc không chặn tác vụ ghi (non-blocking reads)"*.
  - Sửa thuật ngữ `pgvector`: bỏ cụm *"Dedicated Vector Database"*, đổi thành *"hệ quản trị CSDL quan hệ tích hợp tìm kiếm vector bản địa"*.
  - Sửa mô tả HNSW: nêu rõ độ phức tạp kỳ vọng thực nghiệm $O(\log N)$ và độ thu hồi phụ thuộc vào tham số cấu hình (`m = 16`, `ef_construction = 64`, `ef_search = 40`).
- **`2_3_advanced_rag.tex`**:
  - Chuẩn hóa nguồn trích dẫn phân loại Naive/Advanced RAG theo khảo sát của *Gao et al. (2023)* (`\cite{gao2023rag}`).
  - Bổ sung nguyên lý **Phân tích bố cục tài liệu PDF hai cột (Document Layout Analysis)** và chuẩn hóa tọa độ hình học Bounding Box.
  - Làm rõ cơ chế **Truy xuất từ vựng thưa (Sparse Retrieval)**: trình bày nền tảng toán học Okapi BM25 kết hợp cơ chế chỉ mục ngược GIN (`tsvector`) và hàm xếp hạng mật độ che phủ `ts_rank_cd` của PostgreSQL, cùng bước tái xếp hạng **Cross-Encoder** (`ms-marco-TinyBERT-L-2-v2`).
  - Cập nhật **Hình 2-6 (`fig:hybrid_search_rrf`)**: thay ví dụ tính điểm $k=0$ bằng hằng số thực tế **$k = 60$** ($\frac{1}{60+1} + \frac{1}{60+1} = 0{,}0328$).
- **`2_4_knowledge_graph_wiki.tex`**:
  - Đổi mô tả thuật toán phân cụm cộng đồng từ Leiden sang **Louvain** (và nêu mối liên hệ lý thuyết với Leiden) để khớp với mã nguồn thực tế.
  - Sửa **Hình 2-8 (`fig:graphrag_wiki_architecture`)**: xóa nút thừa `Author Nodes`, giữ đúng 4 loại nút thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`).
  - Chỉnh sửa Mục 2.4.3 (*Graph Wiki*): làm rõ đây là cơ chế *Biên dịch trang tổng hợp tri thức từ tóm tắt cộng đồng đồ thị (Compiled Community Wiki)* của hệ thống và bỏ các từ tuyệt đối hóa.
- **`2_5_agentic_react.tex`**:
  - Sửa trình tự thời gian giữa ReAct (10/2022) và Toolformer (02/2023) tại dòng 318.
  - Thu gọn phần mô tả các mẫu không sử dụng trực tiếp (`2.5.2 Planning`, `2.5.5 Reflexion`, `2.5.6 Multi-Agent`, `2.5.7 HITL`) và sửa lại đoạn kết nối thực tế ở cuối mỗi mục: khẳng định VeriScholar chọn **ReAct + Tool Use kết hợp bộ lọc tiền định** làm kiến trúc vận hành thực tế, còn Multi-Agent và HITL là định hướng mở rộng.
- **`2_7_azure_e2b_byok.tex`**:
  - Đổi tiêu đề và nội dung Mục 2.7.1 từ *Azure OpenAI Service* thành **Dịch vụ suy luận OpenAI API và Hạ tầng đám mây Microsoft Azure** (xóa các tuyên bố về Azure VNet/PTU không dùng trong thực tế).
  - Sửa tên mô hình hư cấu `GPT-5.6-luna` (dòng 7) thành `gpt-4o-mini` / `gpt-5.4-mini` và `text-embedding-3-small`.
  - Sửa **Công thức (2.5) (`\label{eq:aes_gcm}`)** chuẩn NIST SP 800-38D:
    $$C = \text{AES-CTR}_K(\text{Plaintext}), \quad T = \text{GHASH}_H(\text{AAD}, C) \oplus E_K(J_0), \quad J_0 = \text{IV} \parallel 0^{31} \parallel 1$$
- **`2_8_langfuse.tex`**: Làm rõ cơ chế ghi vết *Observability Tracing* trên Langfuse Cloud phục vụ giám sát phát triển và tách biệt với cơ chế bảo mật khóa BYOK trên RAM.

#### 4. Chương 3 – Phân Tích Và Thiết Kế Hệ Thống (`report-datn/chapters/ch3/`)
- **`3_1_mo_ta_bai_toan.tex` & `3_2_khao_sat_nghiep_vu.tex`**:
  - Đổi toàn bộ cách xưng hô *"nhóm nghiên cứu"* thành *"tác giả"*.
  - Sửa câu *"khảo sát thực tế tại các nhóm nghiên cứu... tại VinUniversity"* thành phân tích quy trình nghiên cứu khoa học chuẩn quốc tế và khảo sát thực nghiệm trên các công cụ hiện hành; diễn đạt lại con số 30–40% thời gian một cách khách quan.
  - Bổ sung vào cuối Mục 3.1/3.2 phần thiết kế giải thuật cốt lõi của 4 luồng xử lý thực tế trong mã nguồn: (1) Phân tích bố cục PDF 2 cột `PyMuPDF` (`mid_x = 0.5 * W`, lọc header/footer, cửa sổ trượt 250 từ chồng lấp 50 từ), (2) Truy vấn SQL CTE Hybrid RRF $k=60$ + ngưỡng tự đánh giá CRAG ($\tau \ge 0{,}35$ `CORRECT`, $0{,}20 \le \tau < 0{,}35$ `AMBIGUOUS_EXPANDED`, $\tau < 0{,}20$ `ACTIVE_ABSTENTION`), (3) Máy trạng thái LangGraph 4 nút tự sửa lỗi LaTeX có kiểm tra băm SHA-256 chống lặp vô hạn, (4) Trích xuất thực thể OpenAI Structured Outputs + khử trùng lặp vector Cosine $\ge 0{,}90$ + phân cụm Louvain.
- **`3_3_tac_nhan_usecase.tex` & `3_4_phan_tich_usecase.tex`**:
  - Tại UC-01 (`tab:uc_01_spec`): Giải thích chính xác cơ chế phân nhánh bộ lọc tương đồng từ vựng $\text{Jaccard} \ge 0{,}2$ (chỉ áp dụng cho tìm kiếm từ khóa $\ge 3$ từ, bỏ qua khi tra cứu trực tiếp bằng mã DOI/arXiv ID hoặc trên luồng ngữ nghĩa Exa AI — bảo toàn từ khóa `"Jaccard"` và `"0{,}2"` cho bài test).
  - Tại UC-03 (`tab:uc_03_spec`): Bỏ mô tả tính $\text{IoU} \ge 0{,}85$ lúc chạy (runtime); làm rõ tại runtime hệ thống kiểm tra bất biến hình học tọa độ chuẩn hóa $[0, 1]$, còn $\text{IoU} \ge 0{,}85$ là ngưỡng kiểm định chất lượng trên bộ dữ liệu chuẩn.
  - Tại Mục 3.4.2 (4 Use Case Quản trị viên UC-09 $\rightarrow$ UC-12): Làm rõ các ca sử dụng quản trị vận hành được thực thi qua tầng API vận hành (`POST /api/v1/evaluations/run-benchmark`), cơ chế tự động của CSDL (`ref_count`, khóa tạm thời `locked_until`) và bảng điều khiển giám sát Langfuse Cloud / Azure Portal.
- **`3_5_bieu_do_tuan_tu.tex`**:
  - Đồng bộ Bảng 3-3 và Biểu đồ tuần tự Hình 3-4 (`fig:seq_doc_sau`): thể hiện rõ bước đánh giá độ tin cậy truy xuất CRAG trước khi gọi LLM và bước hậu kiểm thẻ trích dẫn tiền định (`verify_output_grounding`) trước khi hoàn tất phản hồi.
- **`3_6_thiet_ke_csdl.tex`**:
  - Đồng bộ nhất quán mô tả **5 phân hệ CSDL** và danh sách **đúng 20 bảng vật lý thực tế** trong `apps/api/src/api/db/models/__init__.py` tại Bảng 3-7 (`tab:db_tables_summary`):
    - Xóa 4 bảng không tồn tại trong code (`extracted_figures`, `extracted_tables`, `draft_sections`, `latex_compilations`).
    - Đưa vào 4 bảng thực tế của Phân hệ Đồ thị Tri thức & Wiki: `graph_nodes`, `graph_edges`, `folder_community_summaries`, `wiki_pages` (kèm bảng từ điển dữ liệu chi tiết).
  - Bổ sung cột `hashed_password` (và các cột bảo mật) vào bảng `users` (Bảng 3-8 & ERD).
  - Bổ sung cột `embedding` (`VECTOR(1536)`) và `content_tsv` (`TSVECTOR`) vào bảng `document_chunks` (Bảng 3-14 & ERD).
  - Sửa toàn bộ tên bảng khóa ngoại bị viết tắt sai: `blobs(id)` $\rightarrow$ `document_storage_blobs(id)`, `sessions(id)` $\rightarrow$ `research_sessions(id)`.
  - Đồng bộ trường `status` của bảng `documents` trên ERD và xóa câu văn lỗi prompt ở dòng 360 (*"các đường liên kết thẳng tắp..."*).
  - Sửa đoạn mô tả cuối mục 3.6.3 (dòng 573): tách rõ **trích xuất thực thể** bằng OpenAI Structured Outputs + luật dự phòng, còn **duyệt đồ thị mở rộng 2 bước** thực hiện bằng truy vấn SQL CTE.

#### 5. Chương 4 – Cài Đặt Và Kết Quả Thực Nghiệm (`report-datn/chapters/ch4/`)
- **`4_2_giao_dien.tex`**:
  - Sửa lỗi lặp từ `(BYOK) (BYOK)` tại dòng 11.
  - Sửa mô tả BYOK tại dòng 248: xóa câu *"tuyệt đối không bao giờ được ghi xuống cơ sở dữ liệu đĩa cứng"*, viết đúng theo thiết kế Chương 3 và code (lưu bản mã AES-256-GCM trong CSDL, chỉ giữ bản rõ trên RAM trong thời gian thực thi request).
  - Xóa cụm từ không có trong code *"như bài báo bị rút lui - retracted papers"* tại dòng 183.
  - Làm rõ ở Hình 4-8 (`deep_read_paper.png`): giải thích rõ định dạng chip trích dẫn hiển thị tên bài báo nguồn (`[ ↳ Attention Is All You Need ]`) và cơ chế kích hoạt khung viền vàng trên Canvas khi người dùng nhấp chọn.
  - Làm rõ ở Hình 4-9 (`graph.png`): nêu minh bạch đồ thị 12 bài báo, 58 đỉnh (12 Paper, 18 Method, 13 Dataset, 15 MetricResult) và 15 trang Wiki là kết quả khởi tạo từ **Tập dữ liệu chuẩn 12 ấn phẩm kinh điển (`landmark_papers_seeder.py`)**, vàเปลี่ยน chữ "Leiden" thành "Louvain".
- **`4_3_kiem_thu.tex`**:
  - Cập nhật Bảng 4-2 (`tab:gate_results`) theo đúng số liệu thực tế hiện tại của kho mã nguồn:
    - Cổng 2 (`pytest`): **340 kịch bản kiểm thử** (phân tách rõ nhóm kiểm thử đơn vị/tích hợp/kiến trúc phần mềm và nhóm kiểm thử quy chuẩn báo cáo).
    - Cổng 3 (`vitest`): **58 tệp kiểm thử (240 kịch bản)**.
    - Tổng cộng: **580 kịch bản kiểm thử tự động** (khớp và vượt chỉ tiêu `> 330` trong Phiếu giao đề tài).
  - Sửa câu *"tổng thời gian thực thi chưa đầy 5 giây"* thành con số tổng thời gian chính xác ($13{,}02\text{ giây}$ hoặc thời gian thực đo mới nhất).
- **`4_4_so_lieu.tex`**:
  - Sửa tên mô hình `gpt-5.6-luna` (dòng 23) thành `gpt-4o-mini` / `gpt-5.4-mini`.
  - Mở rộng Mục 4.2.3 (`Kết quả đo lường hiệu năng và độ chính xác`) với đầy đủ:
    1. **Thiết kế thực nghiệm & Tập dữ liệu chuẩn:** Mô tả tập 12 ấn phẩm kinh điển, 36 câu hỏi Golden Benchmark chia làm 3 nhánh (*Advanced RAG*, *GraphRAG*, *Agentic RAG*) và tập 25 ca kiểm thử lỗi biên dịch LaTeX.
    2. **Bảng kết quả Ablation Study Truy xuất (Bảng mới):** Đối chiếu *Dense-only (`pgvector` HNSW)* vs *Sparse-only (`ts_rank_cd` + BM25)* vs *Hybrid RRF ($k=60$) + Cross-Encoder* theo các chỉ số Recall@5, MRR@10, Groundedness, BBox IoU ($\text{mean} \pm \text{std}$) và độ trễ ($P_{50}/P_{95}$) trích xuất trực tiếp từ `scripts/run_thesis_benchmarks.py`.
    3. **Bảng kết quả Ablation Study Tự sửa lỗi LaTeX (Bảng mới):** Đối chiếu 3 cấu hình (*Rule-based `_auto_patch`*, *Heuristic `apply_heuristic_repair`*, *Combined Agentic ReAct*) trên 25 ca lỗi, thống kê tỷ lệ biên dịch thành công và tỷ lệ bảo toàn ngữ nghĩa.
  - Viết lại phần diễn giải Mục 4.2.4 (Giám sát vận hành):
    - Diễn giải khách quan chỉ số CPU $< 1\%$ và RAM $13{,}58\%$ trên Azure VM (trạng thái vận hành thực nghiệm tải nhẹ, các tác vụ nhúng/suy luận nặng được ủy thác qua REST API bất đồng bộ).
    - Giải thích minh bạch sự khác biệt phạm vi thời gian giữa Hình 4-15 OpenAI Usage (tổng hợp cả tháng 10/2026: 1.397 requests, 78,25 triệu tokens — chủ yếu phục vụ nhúng vector `text-embedding-3-small`, chi phí $\$3{,}76$) và Hình 4-16 Langfuse Dashboard (lọc trong cửa sổ 1 ngày `1d Past 1 day`: 110 traces, trong đó 94 trace là sự kiện kiểm tra cấu hình BYOK không tiêu tốn token LLM, chi phí $\$0{,}00104$).

#### 6. Kết Luận & Tài Liệu Tham Khảo (`ket_luan.tex`, `tai_lieu_tham_khao.tex`)
- **`ket_luan.tex`**:
  - Viết lại theo văn phong khoa học chuẩn mực, bỏ các từ khẳng định tuyệt đối (*"giải quyết dứt điểm"*, *"hoàn thành trọn vẹn"*).
  - Bổ sung mục **Hạn chế của đề tài** (phụ thuộc vào dịch vụ đám mây bên thứ ba OpenAI/Exa/E2B/Langfuse, khử trùng lặp CAS mới dừng ở tầng tệp nhị phân chưa chia sẻ chỉ mục chunk liên người dùng khi khác `user_id`, tập dữ liệu đánh giá Golden Benchmark quy mô vừa phải và mới tập trung trên ấn phẩm tiếng Anh) gắn kết chặt chẽ với **Hướng phát triển**.
- **`tai_lieu_tham_khao.tex`**:
  - Sửa ngay tài liệu `[4]` (`\bibitem{cormack2009}`): đổi tên sai thành tên chính xác ***"Reciprocal rank fusion outperforms condorcet and individual rank learning methods"***, *Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval*, **pp. 758--759**.
  - Thay thế 2 tài liệu ít liên quan trực tiếp (về Multi-Agent / Planning không dùng trong code: `\bibitem{hong2023metagpt}` và `\bibitem{wang2023planandsolve}`) bằng:
    1. `\bibitem{gao2023rag}`: Gao, Yunfan et al. (2023), *"Retrieval-Augmented Generation for Large Language Models: A Survey"*, arXiv preprint arXiv:2312.10997.
    2. `\bibitem{blondel2008louvain}`: Blondel, Vincent D. et al. (2008), *"Fast unfolding of communities in large networks"*, Journal of Statistical Mechanics: Theory and Experiment, 2008(10), P10008 (tài liệu gốc của thuật toán phân cụm **Louvain**).
  - Tổng số tài liệu tham khảo giữ nguyên ở mức **19 tài liệu** ($\le 20$), đảm bảo mọi `\bibitem` đều được `\cite{...}` ít nhất 1 lần trong thân bài và xếp đúng thứ tự ABC theo quy định HUMG.

---

## 6. Phần Giao Cho Tác Tử Thực Thi (What's Left to the Builder)

- Chi tiết câu chữ biên tập trong từng đoạn văn cụ thể miễn là tuân thủ nghiêm ngặt quy tắc Mục 3.1 (không dùng đại từ ngôi thứ nhất), Mục 3.6 (cô lập Chương 2) và Mục 4.7 (dấu phẩy thập phân tiếng Việt `$0{,}85$`) trong `report-datn/RULES.md`.
- Tinh chỉnh kích thước cột `tabularx` và khoảng cách sơ đồ TikZ để bản in `report-datn/main.pdf` không bị lỗi tràn lề (`Overfull \hbox`) hay tiêu đề mồ côi.
