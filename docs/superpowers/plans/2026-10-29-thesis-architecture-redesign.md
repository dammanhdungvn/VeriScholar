# Kế Hoạch Tái Thiết Kế Kiến Trúc TikZ Trực Giao & Chụp Ảnh Giao Diện Thực Tế Báo Cáo ĐATN

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

---

## 1. Mục Tiêu & Tiêu Chí Nghiệm Thu (Goal & Acceptance Criteria)
- **Mục tiêu 1:** Tái thiết kế lại các sơ đồ kiến trúc cốt lõi tại Chương 2 và Chương 3 trong `report-datn` bằng TikZ tối giản trực giao theo Phương án A, tích hợp đầy đủ tri thức từ 5 hình ảnh kiến trúc quốc tế tham khảo và tài liệu `docs/PRD`, `docs/specs`.
- **Mục tiêu 2:** Chụp 4 ảnh màn hình giao diện thực tế của VeriScholar trực tiếp từ `http://localhost:5173` (đang chạy live kết nối Backend `http://localhost:8000`), lưu vào `report-datn/figures/` và nhúng vào `report-datn/chapters/ch4/4_2_giao_dien.tex`.
- **Tiêu chí nghiệm thu bất biến:**
  1. `report-datn/main.pdf` biên dịch không lỗi, $0$ cảnh báo `Overfull \hbox`, duy trì chính xác **51 trang** ($N_{\text{pages}} = 51$).
  2. Tuân thủ 100% Quy chuẩn Liêm chính học thuật (Rule 7) và Chuẩn paper quốc tế (Rule 8) trong `AGENTS.md`.
  3. Vượt qua 4 Cổng Xác Minh Bắt Buộc (`uv run ruff check .`, `uv run pytest`, `npm test`, `npm run build`) và đồng bộ VPS tự động (`bash scripts/deploy_to_vps.sh --fast`).

---

## 2. Bảng Phân Tách Nhiệm Vụ (Task Decomposition)

### Task 1: Tự động hóa chụp 4 ảnh màn hình giao diện thực tế từ Localhost
- **Tệp tạo/sửa:**
  - `scripts/capture_thesis_screenshots.mjs`: Script Node.js điều khiển Chrome headless qua WebSocket CDP.
  - `report-datn/figures/fig_ui_discovery.png`: Ảnh Phân hệ Khám phá tài liệu khoa học.
  - `report-datn/figures/fig_ui_deep_reading.png`: Ảnh Phân hệ Đọc sâu & Bounding Box Canvas.
  - `report-datn/figures/fig_ui_profile.png`: Ảnh Phân hệ Hồ sơ học giả, ORCID & Két sắt BYOK.
  - `report-datn/figures/fig_ui_writing.png`: Ảnh Phân hệ Soạn thảo \LaTeX\ Monaco Editor.
- **Các bước:**
  - [ ] Viết script Node.js `scripts/capture_thesis_screenshots.mjs` inject JWT token vào `localStorage` và chụp 4 phân hệ với kích thước và góc nhìn trực quan tối ưu.
  - [ ] Chạy script, lưu các tệp ảnh vào `report-datn/figures/`.
  - [ ] Kiểm tra thị giác từng ảnh qua `read_file` để đảm bảo độ sắc nét, thông tin chuẩn chỉnh.

### Task 2: Tái thiết kế Sơ đồ Hình 2-2 — Mô hình Advanced RAG 3 Giai đoạn
- **Tệp sửa:** `report-datn/chapters/ch2/2_2_hybrid_rag.tex`
- **Nội dung thiết kế:**
  - Giai đoạn 1 (Pre-Retrieval): Câu hỏi học giả $\to$ Cross-Lingual HyDE & Query Routing.
  - Giai đoạn 2 (Retrieval & Fusion): Hai luồng Dense HNSW 1536d + Sparse GIN BM25 $\to$ RRF Rank Fusion ($k=60$).
  - Giai đoạn 3 (Post-Retrieval & CRAG): Reranking $\to$ CRAG Formula Window Expansion $\to$ Ngữ cảnh $\to$ LLM Generator $\to$ Visual Grounding (Golden BBox $[0..1000]$).
  - Vòng lặp phản hồi: Tuyến Tool Choice nạp tri thức và phản tư trực giao.
- **Các bước:**
  - [ ] Cập nhật mã nguồn TikZ Hình 2-2 trong `report-datn/chapters/ch2/2_2_hybrid_rag.tex`.
  - [ ] Biên dịch thử XeLaTeX, kiểm tra không bị `Overfull \hbox`.
  - [ ] Render trang 19/20 sang PNG để kiểm tra thị giác: đường nét trực giao song song, không chạm đè.

### Task 3: Tái thiết kế Sơ đồ Hình 2-3 — Đường ống Dữ liệu GraphRAG Phân tầng
- **Tệp sửa:** `report-datn/chapters/ch2/2_3_graph_rag.tex`
- **Nội dung thiết kế:**
  - Pha 1 (Ingestion & TextUnits): Nạp tài liệu $\to$ Phân đoạn TextUnits có Bounding Box.
  - Pha 2 (Graph Extraction): Trích xuất 4 Thực thể DNA (`Paper`, `Method`, `Dataset`, `MetricResult`) & Bóc tách Research Gap.
  - Pha 3 (Hierarchical Community Detection): Thuật toán Leiden phân cụm đồ thị.
  - Pha 4 (Dual-Level Retrieval): Tóm tắt cộng đồng vĩ mô $\parallel$ Thực thể vi mô.
- **Các bước:**
  - [ ] Cập nhật mã nguồn TikZ Hình 2-3 trong `report-datn/chapters/ch2/2_3_graph_rag.tex`.
  - [ ] Cập nhật phần văn bản giải thích đường ống dữ liệu phân tầng tương ứng.
  - [ ] Biên dịch XeLaTeX, kiểm tra thị giác trang 21/22.

### Task 4: Căn chỉnh trực giao Hình 3-2 & Hình 3-3 (Chương 3)
- **Tệp sửa:**
  - `report-datn/chapters/ch3/3_2_usecase.tex` (Hình 3-2: Năng lực chức năng hệ thống VeriScholar)
  - `report-datn/chapters/ch3/3_3_kien_truc.tex` (Hình 3-3: Kiến trúc Phân tầng Tự phản biện hai dải màu)
- **Nội dung thiết kế:**
  - Hình 3-2: Mở rộng khoảng cách thẻ, căn lề thẳng đứng, đồng bộ thuật ngữ với Chương 2 (HyDE, RRF, CRAG, Leiden Community, MicroVM).
  - Hình 3-3: Căn chỉnh hai dải ReAct Band và Reflexion Band song hành trực giao, không chạm nét, thêm chỉ dẫn luồng Tool Choice.
- **Các bước:**
  - [ ] Cập nhật mã nguồn TikZ Hình 3-2 và 3-3.
  - [ ] Biên dịch XeLaTeX, kiểm tra thị giác trang 29 và 34.

### Task 5: Nhúng 4 ảnh chụp giao diện thực tế vào Mục 4.2 và Cân đối số trang
- **Tệp sửa:** `report-datn/chapters/ch4/4_2_giao_dien.tex`
- **Nội dung:**
  - Nhúng ảnh chụp thực tế vào từng tiểu mục tương ứng:
    - `subsec:ui_discovery`: Nhúng `fig_ui_discovery.png` với chú thích minh chứng bộ lọc Đã bình duyệt và thẻ chống tràn.
    - `subsec:ui_deep_reading`: Nhúng `fig_ui_deep_reading.png` với chú thích minh chứng khung Canvas 2 cột và Bounding Box viền vàng.
    - `subsec:ui_profile`: Nhúng `fig_ui_profile.png` với chú thích minh chứng xác thực ORCID và két sắt BYOK.
    - `subsec:ui_writing`: Nhúng `fig_ui_writing.png` với chú thích minh chứng Monaco Editor và máy ảo E2B.
  - Cân đối tỷ lệ scale ảnh (`width=0.88\textwidth` hoặc bố cục 2 cột) để giữ toàn bộ đồ án đạt chính xác **51 trang** ($N_{\text{pages}} = 51$).
- **Các bước:**
  - [ ] Cập nhật `report-datn/chapters/ch4/4_2_giao_dien.tex`.
  - [ ] Biên dịch XeLaTeX 2 lần để giải quyết trọn vẹn cross-references.
  - [ ] Kiểm tra `pdfinfo main.pdf | grep Pages` $\to$ Đúng 51 trang.
  - [ ] Kiểm tra `test_thesis_structure_and_compile.py` passed 100%.

### Task 6: Kiểm tra 4 Cổng Xác Minh Bắt Buộc & Đồng Bộ VPS
- **Các bước:**
  - [ ] Chạy Cổng 1: `uv run ruff check . && uv run ruff format --check .`
  - [ ] Chạy Cổng 2: `uv run pytest`
  - [ ] Chạy Cổng 3: `npm --prefix apps/web run test`
  - [ ] Chạy Cổng 4: `npm --prefix apps/web run build`
  - [ ] Commit git trên nhánh `docs/thesis-architecture-update` trong worktree.
  - [ ] Chạy `bash scripts/deploy_to_vps.sh --fast`.
