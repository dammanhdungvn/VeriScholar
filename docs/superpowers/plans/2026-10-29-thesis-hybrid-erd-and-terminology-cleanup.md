# Kế Hoạch Tái Thiết Kế Hybrid ERD CSDL, Thoáng Đãng Bố Cục & Chuẩn Hóa Thuật Ngữ ĐATN

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

---

## 1. Mục Tiêu & Tiêu Chí Nghiệm Thu (Goal & Acceptance Criteria)
- **Mục tiêu 1:** Tái thiết kế Sơ đồ CSDL Mục 3.4 (`report-datn/chapters/ch3/3_4_csdl.tex`) thành bản vẽ **Hybrid Relational-Vector-Graph ERD** chuẩn UML / Crow's Foot thể hiện rõ các trường, khóa chính `PK`, khóa ngoại `FK`, kiểu dữ liệu `vector(1536)`, `tsvector`, `jsonb`, loại bỏ hoàn toàn các khối hộp chung chung.
- **Mục tiêu 2:** Khử hoàn toàn hiện tượng "code leak" (`document_chunks`, `storage_blobs`, `user_secrets` dạng snake_case trong văn phong) $\to$ chuyển thành Plaintext chuẩn chuyên ngành (`Chunking Documents / Document Chunks`, `CAS Storage Blobs`, `User Secrets Vault`).
- **Mục tiêu 3:** Tách thoáng bố cục Trang 34, giải tỏa va chạm giữa Hình 3-3 (Reflexion Dual Band) và Hình 3-4 (Agent Execution Trace), bảo đảm mỗi sơ đồ có hành lang thở $\ge 2\,\text{cm}$.
- **Mục tiêu 4:** Chuẩn hóa đồng bộ 100% thuật ngữ chuyên ngành tiếng Anh (`Pipeline`, `Retrieval`, `Chunking`, `Embedding`, `Bounding Box`, `Re-ranking`), triệt tiêu các từ dịch thô kệch ("đường ống dẫn", "phân mảnh thô"), bổ sung diễn giải bắc cầu sư phạm gần gũi.
- **Tiêu chí nghiệm thu bất biến:**
  1. `report-datn/main.pdf` biên dịch sạch, $0$ lỗi `Overfull \hbox`, duy trì chính xác **51 trang** ($N_{\text{pages}} = 51$).
  2. Băng qua toàn bộ 6/6 test trong `tests/test_thesis_structure_and_compile.py`.
  3. Gate 1 (`ruff`) pass 100%, commit trên worktree nhánh `docs/thesis-architecture-update`.

---

## 2. Bảng Phân Tách Nhiệm Vụ (Task Decomposition)

### Task 1: Thiết kế Bản vẽ Hybrid ERD CSDL trong `3_4_csdl.tex` & Chuẩn hóa Plaintext
- **Tệp sửa:** `report-datn/chapters/ch3/3_4_csdl.tex`
- **Nội dung:**
  - Thay thế `fig:erd_model` bằng bản vẽ TikZ Hybrid ERD 3 phân vùng:
    - Vùng 1 (RDBMS Core & CAS): `[USERS]`, `[USER SECRETS VAULT]`, `[ACADEMIC DOCUMENTS]`, `[CAS STORAGE BLOBS]`, `[READING SESSIONS]`.
    - Vùng 2 (pgvector & Spatial Store): `[DOCUMENT CHUNKS]` với `PK id: UUID`, `FK document_id: UUID`, `embedding: vector(1536)`, `content_tsv: tsvector`, `bbox: JSONB`.
    - Vùng 3 (GraphRAG Knowledge Entities): `[PAPER NODES]`, `[METHOD NODES]`, `[DATASET NODES]`, `[METRIC RESULTS]`.
  - Thay thế toàn bộ tên snake_case trong văn phong và caption bảng sang Plaintext (`Document Chunks / Chunking Documents`, `CAS Storage Blobs`, `User Secrets Vault`).
- **Các bước:**
  - [ ] Cập nhật mã nguồn TikZ Hình 3-5 trong `3_4_csdl.tex`.
  - [ ] Cập nhật văn bản mô tả thực thể và tiêu đề Bảng 3-4, 3-5, 3-6.
  - [ ] Biên dịch thử XeLaTeX, xác nhận không có `Overfull \hbox`.

### Task 2: Tách thoáng Bố cục Trang 34 cho Hình 3-3 & Hình 3-4
- **Tệp sửa:** `report-datn/chapters/ch3/3_3_kien_truc.tex`
- **Nội dung:**
  - Căn chỉnh chiều cao dọc của Hình 3-3 (Dual-Band Reflexion) và Hình 3-4 (Agent Execution Trace) để phân bổ trang tự nhiên, không bị ép sát nhau trên Trang 34.
  - Bảo đảm khoảng cách giữa tiêu đề, hình ảnh và văn bản thông thoáng $\ge 1.5 - 2\,\text{cm}$.
- **Các bước:**
  - [ ] Tối ưu hóa kích thước dọc của Hình 3-4 (Agent Execution Trace boxes) trong `3_3_kien_truc.tex`.
  - [ ] Biên dịch XeLaTeX, kiểm tra phân bổ trang.
  - [ ] Render PNG Trang 33, 34, 35 để thẩm định thị giác.

### Task 3: Quét & Chuẩn Hóa Đồng Bộ Thuật Ngữ Chuyên Ngành
- **Tệp sửa:**
  - `report-datn/chapters/ch2/2_2_hybrid_rag.tex`
  - `report-datn/chapters/ch2/2_3_graph_rag.tex`
  - `report-datn/chapters/ch2/2_4_react_agent.tex`
  - `report-datn/chapters/ch3/3_1_khao_sat.tex`
  - `report-datn/chapters/ch3/3_2_usecase.tex`
  - `report-datn/chapters/ch3/3_3_kien_truc.tex`
  - `report-datn/chapters/ch3/3_4_csdl.tex`
- **Nội dung:**
  - Thay thế triệt để các cụm từ "đường ống", "đường ống dẫn", "đường ống dữ liệu thô" $\to$ `Pipeline` / `RAG Pipeline` / `Data Pipeline`.
  - Giữ nguyên các thuật ngữ chuẩn: `Chunking`, `Retrieval`, `Embedding`, `Bounding Box`, `Re-ranking`, `Agent Execution Trace`.
  - Bổ sung câu diễn giải bắc cầu đời thường sau các công thức toán học trọng yếu.
- **Các bước:**
  - [ ] Quét và thay thế các từ ngữ thô gượng ép.
  - [ ] Bổ sung diễn giải thực tế cho các thuật ngữ và công thức.
  - [ ] Đảm bảo tính nhất quán 100% xuyên suốt toàn bộ các chương.

### Task 4: Kiểm Thử XeLaTeX, Khóa Bất Biến 51 Trang & Cổng Xác Minh
- **Nội dung:**
  - Biên dịch XeLaTeX 2 lần: xác nhận $0$ lỗi `Overfull \hbox`, không còn cảnh báo.
  - Kiểm tra `pdfinfo`: đúng chính xác **51 trang** ($N_{\text{pages}} = 51$).
  - Chạy `uv run pytest tests/test_thesis_structure_and_compile.py` đạt 6/6 (100%).
  - Chạy Gate 1: `uv run ruff check . && uv run ruff format --check .`.
  - Đồng bộ các tệp `report-datn/` sang thư mục gốc nếu cần và commit git trên worktree `docs/thesis-architecture-update`.
- **Các bước:**
  - [ ] Chạy biên dịch và kiểm tra trang.
  - [ ] Chạy test suite.
  - [ ] Commit git.
