# Đặc Tả Thiết Kế: Chuẩn Hóa Độ Chính Xác Tìm Kiếm & Thẻ Bài Báo Học Thuật (Scholarly Search Precision & Cards Design)

> **Mã thiết kế:** `SPEC-2026-10-26-SEARCH-PRECISION-AND-CARDS`  
> **Trạng thái:** Chờ phê duyệt (Pending Approval)  
> **Tác giả:** VeriScholar Core Team  
> **Quy chuẩn:** Tuân thủ 100% [AGENTS.md](../../../AGENTS.md) (Rule 5: Relative links only; Rule 6: Radical Minimalism)

---

## 1. Bối Cảnh & Động Lực (Context & Motivation)
Khi người dùng thực hiện tìm kiếm bài báo chuyên ngành (ví dụ: *"Retrieval-Augmented Generation for Large Language Models: A Survey"*), hệ thống gặp 3 vấn đề nghiêm trọng về trải nghiệm và chất lượng dữ liệu:
1. **Thiếu phản hồi trạng thái:** Giao diện không có hiệu ứng Skeleton loading hoặc spinner rõ ràng, khiến người dùng ngộ nhận hệ thống bị treo.
2. **Tràn bố cục thẻ bài báo:** Thẻ kết quả hiển thị danh sách hàng trăm tác giả (đặc biệt các bài báo vật lý hợp tác CMS/LHCb), tiêu đề dính mã LaTeX thô (`$B^0_s\to\mu^+\mu^-$`), phần tóm tắt quá dài không được giới hạn dòng gây mất cân đối trên mobile/desktop.
3. **Nhiễu kết quả (Search Noise):** Truy vấn arXiv đang dùng cú pháp mở `all:query` không bọc cụm từ và không phân cấp trọng số trường tiêu đề, dẫn đến việc các bài báo vật lý hạt nhân năm 2014 xuất hiện khi tìm kiếm mô hình ngôn ngữ lớn (LLM/RAG).

---

## 2. Mục Tiêu & Giới Hạn (Goals, Non-Goals, Anti-Goals)

### 2.1. Mục Tiêu (Goals)
- **Hiệu ứng tức thì (Instant Feedback):** Hiển thị ngay 3 thẻ Skeleton phát sáng (`animate-pulse`) khi gửi yêu cầu tìm kiếm, kèm spinner trạng thái trực quan tại nút gửi.
- **Thẻ bài báo tinh gọn chuẩn quốc tế (Radical Minimalist Card):**
  - Tác giả: Tối đa 2 tác giả, nếu nhiều hơn thì hiển thị `Tác giả 1, Tác giả 2 và cộng sự` (`et al.`).
  - Tiêu đề: Khử sạch các ký hiệu toán học LaTeX thô (như `$B^0_s\to\mu^+\mu^-$` chuyển thành văn bản chuẩn hoặc KaTeX sạch).
  - Thẻ định danh (Tags): Tinh tế, rõ ràng (`Open Access PDF` vs `Tóm tắt`, `arXiv` vs `Hội nghị/Tạp chí`).
  - Liên kết trực tiếp (Link): Nút dẫn thẳng tới DOI/arXiv gốc.
  - Tóm tắt (Summary): Khống chế cứng tối đa 2 dòng hiển thị (`line-clamp-2`), hỗ trợ nút mở rộng gọn gàng.
- **Mô hình lai lọc bài báo (Hybrid Quality Filter):**
  - Backend: Truy vấn chính xác có trọng số tiêu đề (`ti:`) và lọc tương đồng từ vựng/ngữ nghĩa để loại bỏ hoàn toàn bài rác lạc đề.
  - Frontend: Nút gạt chuyển đổi nhỏ gọn: `Tất cả` vs `Đã bình duyệt (Peer-Reviewed)`.

### 2.2. Phi Mục Tiêu (Non-Goals)
- Không can thiệp hoặc thay đổi các endpoint đọc sâu PDF (`/api/v1/discovery/open-reading`).
- Không tích hợp các nhà cung cấp trả phí ngoài luồng nếu chưa có API key (chỉ tối ưu hóa arXiv, Crossref, Semantic Scholar và Curated Catalog).

### 2.3. Chống Mục Tiêu (Anti-Goals)
- Tuyệt đối không để xảy ra hiện tượng tràn chữ làm hỏng layout trên thiết bị di động.
- Không để lọt các bài báo hoàn toàn không liên quan đến chủ đề tìm kiếm lên top đầu kết quả.
- Không đưa tên thuật toán hoặc cơ chế kỹ thuật nội bộ lên giao diện (Rule 6).

---

## 3. Các Phương Án Kiến Trúc (Approaches Considered)

### Phương án 1: Lọc Tự Động Hoàn Toàn Tại Backend (Zero-Config)
- **Cơ chế:** Backend tự động loại bỏ bài rác và sắp xếp thứ tự hội nghị/tạp chí uy tín lên đầu. Frontend không có nút gạt.
- **Đánh đổi:** Người dùng không có quyền chủ động ép buộc lọc chỉ bài đã bình duyệt khi viết phần tài liệu tham khảo cho luận văn.

### Phương án 2: Mô hình Lai (Được Lựa Chọn - Hybrid Filter & Precision Re-ranking)
- **Cơ chế:**
  - **Tầng 1 (Backend Auto):** Xây dựng truy vấn arXiv chuẩn hóa dạng `ti:"{query}" OR abs:"{query}"`, áp dụng hàm xếp hạng độ tương đồng từ vựng trên tiêu đề (`Jaccard / Token overlap >= 0.25`). Các bài báo không đạt ngưỡng tương đồng sẽ bị loại bỏ hoàn toàn.
  - **Tầng 2 (Frontend Control):** Bổ sung nút gạt mềm dạng Pill `[ Tất cả ] | [ Đã bình duyệt ]` tại thanh kết quả tìm kiếm. Khi chọn "Đã bình duyệt", hệ thống tự động lọc giữ lại các bài có venue xuất bản chính thức (NeurIPS, ICML, CVPR, ACL, IEEE, ACM, Nature, Springer,...).
- **Lý do chọn:** Vừa giải quyết triệt để bài rác ngay từ gốc, vừa cung cấp công cụ tra cứu phân loại chuyên nghiệp chuẩn Google Scholar và Semantic Scholar.

---

## 4. Đặc Tả Kỹ Thuật Chi Tiết (Detailed Technical Specification)

### 4.1. Backend: Nâng Cấp `ScholarlySearchAdapter` & `DiscoverySearchRequest`
1. **Mở rộng Schema `DiscoverySearchRequest`:**
   - Thêm trường tùy chọn: `is_peer_reviewed_only: bool = False`.
2. **Cơ chế truy vấn arXiv chính xác cao:**
   - Chuyển từ `all:{clean_query}` sang truy vấn phối hợp:
     `ti:"{clean_query}" OR (ti:{tokens} AND abs:{tokens})` kết hợp `sortBy=relevance`.
3. **Bộ lọc tương đồng tiêu đề (Relevance Gate):**
   - Loại bỏ các bài báo có tỷ lệ trùng khớp tiêu đề quá thấp so với từ khóa tìm kiếm (ngăn chặn tình trạng từ khóa AI ra bài vật lý hạt nhân).
4. **Phân loại nguồn bình duyệt (Venue Classifier):**
   - Đánh dấu bài báo là `is_peer_reviewed = True` nếu `venue` thuộc danh mục các hội nghị/tạp chí quốc tế đã bình duyệt, hoặc có định danh `doi` không thuộc tiền tố thuần arXiv pre-print.

### 4.2. Frontend: Skeleton Loading & Thẻ Bài Báo Tinh Gọn
1. **Component `ScholarlySkeletonList.tsx`:**
   - Hiển thị 3 khung thẻ giả lập nhấp nháy êm ái khi `isSearching === true`.
   - Nút tìm kiếm đổi sang biểu tượng `Loader2` quay tròn.
2. **Component `ScholarlyResultCard.tsx` Refactor:**
   - **Tác giả:** Rút gọn danh sách: nếu `authors.length > 2`, hiển thị `${authors[0]}, ${authors[1]} và cộng sự`.
   - **Khử mã LaTeX thô:** Thay thế các macro LaTeX toán học (`$...$`, `\to`, `\mu`) bằng ký tự Unicode chuẩn hoặc làm sạch an toàn trước khi render.
   - **Tóm tắt (Abstract):** Áp dụng class `line-clamp-2` cố định; người dùng có thể nhấp để mở rộng nếu cần.
   - **Tags & Link:** Tag `Open Access` / `Bình duyệt` dạng pill thanh mảnh; link trực tiếp tới DOI/arXiv với icon ngoài.
3. **Bộ lọc chuyển đổi nguồn tại `UnifiedHeroWorkspace.tsx`:**
   - Nút gạt mềm: `Tất cả ({total})` và `Đã bình duyệt ({peerReviewedCount})`.

---

## 5. Kế Hoạch Xác Minh (Verification Plan)

### 5.1. Backend Unit Tests
- `test_scholarly_search_precision()`: Kiểm tra từ khóa *"Retrieval-Augmented Generation"* không trả về các bài vật lý hạt nhân năm 2014.
- `test_scholarly_search_peer_reviewed_filter()`: Kiểm tra cờ `is_peer_reviewed_only` chỉ trả về bài báo có venue uy tín.

### 5.2. Frontend Vitest Tests
- `ScholarlyResultCard.test.tsx`:
  - Kiểm tra danh sách tác giả bị rút gọn khi vượt quá 2 người.
  - Kiểm tra tiêu đề chứa mã LaTeX được khử sạch.
  - Kiểm tra phần tóm tắt áp dụng giới hạn 2 dòng.
- `UnifiedHeroWorkspace.test.tsx`:
  - Kiểm tra Skeleton cards hiển thị khi đang tìm kiếm.
  - Kiểm tra nút gạt "Đã bình duyệt" hoạt động đúng.

### 5.3. Bốn Cổng Xác Minh & Triển Khai VPS
- Cổng 1: `uv run ruff check . && uv run ruff format --check .` (exit code 0).
- Cổng 2: `uv run pytest` (100% pass).
- Cổng 3: `npm --prefix apps/web run test` (100% pass).
- Cổng 4: `npm --prefix apps/web run build` (100% pass).
- Triển khai VPS qua `./scripts/deploy_to_vps.sh` và nghiệm thu trực tiếp tại `https://verischolar.duckdns.org`.
