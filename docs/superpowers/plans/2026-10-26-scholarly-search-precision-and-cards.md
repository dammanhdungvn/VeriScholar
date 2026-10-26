# Kế Hoạch Triển Khai: Chuẩn Hóa Độ Chính Xác Tìm Kiếm & Thẻ Bài Báo Học Thuật (Scholarly Search Precision & Cards Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khắc phục triệt để 3 vấn đề tìm kiếm: hiển thị Skeleton loading mượt mà khi tìm kiếm, tái cấu trúc thẻ bài báo siêu tinh gọn chống tràn (tối đa 2 tác giả, khử LaTeX thô, tóm tắt 2 dòng), và triển khai mô hình lai (Hybrid: tự động lọc rác tại backend + nút gạt lọc bài bình duyệt trên frontend).

**Architecture:** Nâng cấp `ScholarlySearchAdapter` tại backend với truy vấn có trường tiêu đề (`ti:`) và lọc tương đồng tiêu đề; bổ sung trường `is_peer_reviewed` vào `ScholarlyPaperSearchResult`. Tại frontend, bổ sung `ScholarlySkeletonList`, tinh giản `ScholarlyResultCard` và tích hợp bộ lọc chuyển đổi nguồn tại `UnifiedHeroWorkspace`.

**Tech Stack:** FastAPI, Python 3.12, httpx, React 19, Tailwind CSS, Lucide Icons, Vitest, Pytest.

**Spec:** [../specs/2026-10-26-scholarly-search-precision-and-cards-design.md](../specs/2026-10-26-scholarly-search-precision-and-cards-design.md)

## Global Constraints
- `AGENTS.md` Rule 5: Tuyệt đối dùng đường dẫn tương đối trong toàn bộ tài liệu Markdown nội bộ.
- `AGENTS.md` Rule 6: Không đưa tên cơ chế nội bộ hoặc văn mẫu sáo rỗng lên giao diện.
- Bắt buộc vượt qua 100% 4 Verification Gates trước khi triển khai lên máy chủ VPS.

## Review Focus
1. Truy vấn bài báo chính xác theo tên (ví dụ: *"Retrieval-Augmented Generation for Large Language Models: A Survey"*) phải trả về đúng bài RAG Survey, không bao giờ được trả về bài vật lý hạt nhân CMS/LHCb 2014.
2. Bài báo có hơn 50 tác giả không được làm vỡ giao diện; phải hiển thị `Tác giả 1, Tác giả 2 và cộng sự`.
3. Tiêu đề chứa ký tự công thức LaTeX thô như `$B^0_s\to\mu^+\mu^-$` phải được làm sạch thành văn bản dễ đọc.
4. Tóm tắt bài báo (`abstract`) trên mọi kích thước màn hình bị khống chế tối đa 2 dòng hiển thị (`line-clamp-2`).
5. Khi người dùng bấm tìm kiếm, phải hiển thị ngay 3 thẻ Skeleton phát sáng để người dùng biết hệ thống đang xử lý.

---

### Task 1: Backend Precision Query Generation, Relevance Filtering & Peer-Reviewed Tagging

**Files:**
- Modify: `packages/core/src/core/ports/scholarly_search.py`
- Modify: `apps/api/src/api/adapters/scholarly_search_adapter.py`
- Modify: `apps/api/src/api/schemas/discovery.py`
- Modify: `apps/api/src/api/v1/endpoints/discovery.py`
- Test: `apps/api/tests/test_discovery_search_endpoints.py`

- [x] **Step 1.1: Viết test kiểm tra tìm kiếm chính xác và lọc rác**
  Viết test trong `apps/api/tests/test_discovery_search_endpoints.py`:
  - `test_scholarly_search_precision_no_particle_physics()`: Tìm *"Retrieval-Augmented Generation"* không chứa bài vật lý hạt nhân 2014.
  - `test_scholarly_search_peer_reviewed_filter()`: Tìm kiếm với `is_peer_reviewed_only=True` lọc bỏ các bài thuần arXiv pre-print không có venue xuất bản.
- [x] **Step 1.2: Chạy test để xác nhận test đỏ**
  Chạy `uv run pytest apps/api/tests/test_discovery_search_endpoints.py`.
- [x] **Step 1.3: Mở rộng `ScholarlyPaperSearchResult` và `DiscoverySearchRequest`**
  - Thêm `is_peer_reviewed: bool = False` vào `ScholarlyPaperSearchResult`.
  - Thêm `is_peer_reviewed_only: bool = False` vào `DiscoverySearchRequest`.
- [x] **Step 1.4: Nâng cấp `ScholarlySearchAdapter`**
  - Xây dựng truy vấn arXiv chính xác: `ti:"{clean_query}" OR (ti:{tokens} AND abs:{tokens})`.
  - Thêm hàm tính điểm tương đồng tiêu đề (Jaccard token overlap): loại bỏ các bài có điểm tương đồng < 0.2 nếu query có từ 3 từ trở lên.
  - Phân loại `is_peer_reviewed`: kiểm tra nếu venue thuộc các tổ chức/hội nghị uy tín (NeurIPS, ICML, CVPR, ACL, IEEE, ACM, Nature, Science, Springer) hoặc DOI không phải thuần arXiv.
  - Áp dụng bộ lọc `is_peer_reviewed_only` khi có yêu cầu.
- [x] **Step 1.5: Chạy lại pytest để xác nhận test xanh**
  Chạy `uv run pytest apps/api/tests/test_discovery_search_endpoints.py`.
- [x] **Step 1.6: Commit Task 1**
  `git commit -m "feat(api): implement precision scholarly search with relevance filtering and peer-reviewed classification"`

---

### Task 2: Frontend Skeleton Loading State & Search Button Indicator

**Files:**
- Create: `apps/web/src/features/discovery/components/ScholarlySkeletonList.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx`
- Modify: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`

- [x] **Step 2.1: Viết test cho Skeleton Loading khi đang tìm kiếm**
  Viết test trong `apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx` kiểm tra khi `isSearching === true`, hiển thị container Skeleton có `data-testid="scholarly-skeleton-list"`.
- [x] **Step 2.2: Tạo component `ScholarlySkeletonList.tsx`**
  Thiết kế 3 thẻ giả lập nhấp nháy (`animate-pulse`) với cấu trúc:
  - Header tag nhấp nháy
  - Tiêu đề 2 dòng
  - Tác giả 1 dòng
  - Tóm tắt 2 dòng
- [x] **Step 2.3: Tích hợp Skeleton vào `UnifiedHeroWorkspace.tsx`**
  - Thay thế loader chữ đơn điệu bằng `<ScholarlySkeletonList />` khi `isSearching === true`.
  - Đảm bảo vùng dropzone và gợi ý ẩn mượt mà trong khi tìm kiếm.
- [x] **Step 2.4: Bổ sung spinner trực tiếp trên nút Gửi của `DashboardChatInputBox.tsx`**
  Khi `isGenerating` hoặc `isSearching` bật, nút mũi tên chuyển thành biểu tượng `Loader2` quay tròn.
- [x] **Step 2.5: Chạy vitest để xác nhận test xanh**
  Chạy `npm --prefix apps/web run test`.
- [x] **Step 2.6: Commit Task 2**
  `git commit -m "feat(web): add scholarly skeleton loading cards and animated search button indicator"`

---

### Task 3: Tái Cấu Trúc `ScholarlyResultCard` Siêu Tinh Gọn (Radical Minimalism)

**Files:**
- Modify: `apps/web/src/features/discovery/components/ScholarlyResultCard.tsx`
- Test: `apps/web/src/features/discovery/__tests__/ScholarlyResultCard.test.tsx`

- [x] **Step 3.1: Viết test kiểm thử các trường hợp giới hạn của Thẻ bài báo**
  - Test rút gọn tác giả: 50 tác giả hiển thị `${authors[0]}, ${authors[1]} và cộng sự`.
  - Test làm sạch mã LaTeX thô trong tiêu đề: `$B^0_s\to\mu^+\mu^-$` chuyển thành văn bản sạch không còn ký tự thô.
  - Test tóm tắt bị giới hạn 2 dòng với class `line-clamp-2`.
- [x] **Step 3.2: Triển khai hàm `formatScholarlyAuthors(authors: string[])`**
  - Nếu `authors.length === 0`: `"Chưa rõ tác giả"`.
  - Nếu `authors.length <= 2`: `authors.join(", ")`.
  - Nếu `authors.length > 2`: `${authors[0]}, ${authors[1]} và cộng sự`.
- [x] **Step 3.3: Triển khai hàm `sanitizeAcademicTitle(title: string)`**
  - Khử các ký tự bọc LaTeX `$`, các lệnh `\to`, `\mu`,... chuyển về dạng ký tự chuẩn hoặc loại bỏ ký tự rác.
- [x] **Step 3.4: Tinh gọn Badge Tags và Abstract**
  - Tag dạng pill thanh mảnh: `Open Access PDF` (xanh ngọc) hoặc `Tóm tắt` (xám).
  - Thêm tag `Đã bình duyệt` (tím nhạt) nếu `paper.is_peer_reviewed`.
  - Thẻ tóm tắt cố định `line-clamp-2`, hỗ trợ mở rộng/thu gọn nếu cần.
  - Link DOI / arXiv trực tiếp, mở tab mới an toàn với `rel="noreferrer"`.
- [x] **Step 3.5: Chạy vitest để kiểm tra component**
  Chạy `npm --prefix apps/web run test`.
- [x] **Step 3.6: Commit Task 3**
  `git commit -m "refactor(web): transform ScholarlyResultCard into radical minimalist format with author clamping and LaTeX sanitization"`

---

### Task 4: Nút Gạt Bộ Lọc Nguồn "Tất Cả" vs "Đã Bình Duyệt" tại `UnifiedHeroWorkspace`

**Files:**
- Modify: `apps/web/src/features/discovery/api/discoveryApi.ts`
- Modify: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`

- [x] **Step 4.1: Cập nhật `discoveryApi.ts`**
  Thêm `is_peer_reviewed?: boolean` vào interface `ScholarlyPaper` và thêm cờ `is_peer_reviewed_only` vào `discoveryApi.search()`.
- [x] **Step 4.2: Tích hợp Pill Filter Toggle vào Header kết quả**
  - Hiển thị thanh đếm kết quả kèm nút gạt:
    `[ Tất cả (N) ]` | `[ Đã bình duyệt (M) ]`.
  - Khi nhấp vào "Đã bình duyệt", danh sách kết quả lọc tức thì các bài có `is_peer_reviewed === true`.
- [x] **Step 4.3: Viết test cho hành vi chuyển đổi bộ lọc**
  Test chuyển đổi giữa "Tất cả" và "Đã bình duyệt" thay đổi số lượng bài báo hiển thị.
- [x] **Step 4.4: Chạy vitest**
  Chạy `npm --prefix apps/web run test`.
- [x] **Step 4.5: Commit Task 4**
  `git commit -m "feat(web): add hybrid peer-reviewed filter toggle to search results hub"`

---

### Task 5: Xác Minh 4 Cổng Toàn Trình & Triển Khai Production Lên VPS

**Files:**
- Run: `./scripts/deploy_to_vps.sh`

- [x] **Step 5.1: Chạy Cổng 1 - Linter & Formatter Python**
  `uv run ruff check . && uv run ruff format --check .` (PASS - 152 files)
- [x] **Step 5.2: Chạy Cổng 2 - Backend Pytest Suite**
  `uv run pytest` (PASS - 84/84 tests)
- [x] **Step 5.3: Chạy Cổng 3 - Frontend Vitest Suite**
  `npm --prefix apps/web run test` (PASS - 24/24 tests)
- [x] **Step 5.4: Chạy Cổng 4 - Production Web Build**
  `npm --prefix apps/web run build` (PASS - exit code 0)
- [x] **Step 5.5: Triển khai 1-Click Rollout lên VPS**
  Thực thi `./scripts/deploy_to_vps.sh` để đồng bộ code và bundle web mới nhất lên `https://verischolar.duckdns.org` (bundle: `assets/index-DP_3HI-j.js`).
- [x] **Step 5.6: Kiểm chứng trực tiếp trên máy chủ VPS**
  - Chạy `curl -fsS https://verischolar.duckdns.org/health` (xác nhận 200).
  - Chạy `POST /api/v1/discovery/search` với từ khóa *"Retrieval-Augmented Generation for Large Language Models: A Survey"*, xác nhận 100% kết quả là bài RAG Survey, loại bỏ hoàn toàn các bài vật lý hạt nhân CMS/LHCb 2014.
- [x] **Step 5.7: Đóng Goal với `<!-- GOAL_COMPLETE -->`**
