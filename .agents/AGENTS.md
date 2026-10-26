# VERISCHOLAR UNIVERSAL AGENT CONSTITUTION & ROUTER

> **Bản quyền kiến trúc:** VeriScholar MVP — Monorepo Agent Harness
> **Quy chuẩn:** Giữ file này tối giản (< 150 dòng). Hướng dẫn chi tiết nạp qua `.agents/skills/`.

---

## 1. Mục Tiêu & Phạm Vi (Scope)
VeriScholar là nền tảng Trợ lý AI Nghiên cứu Khoa học Toàn trình phục vụ học giả, nhà nghiên cứu và giảng viên.
Toàn bộ mã nguồn phải bám sát 100% tài liệu nghiệp vụ tại [`docs/PRD/`](../docs/PRD) và đặc tả kỹ thuật tại [`docs/specs/`](../docs/specs).

---

## 2. Quy Tắc Vận Hành Bất Biến (Operating Rules)
1. **Lập Trình Hướng Kiểm Thử (TDD Bắt Buộc):** Viết test đỏ trước $\rightarrow$ Viết code xanh tối thiểu $\rightarrow$ Tối ưu hóa (Refactor). Không commit code sản xuất nếu chưa có test chứng minh.
2. **Kiến Trúc Lục Giác (Hexagonal Isolation):** `packages/core/` là lõi miền nghiệp vụ thuần khiết (chỉ dùng Python Standard Library và `pydantic`). Tuyệt đối cấm import từ `apps/api`, database ORM, web framework hoặc thư viện I/O.
3. **Tháp Thẩm Quyền (Authority Hierarchy):** Khi có mâu thuẫn nhận thức, ưu tiên:
   $$\mathbf{Code\ \&\ Passing\ Tests} > \mathbf{Technical\ Specs\ (docs/specs/)} > \mathbf{Agent\ Skills\ (.agents/skills/)}$$
4. **Co-Location Commit Rule:** Sửa endpoint, schema hoặc loại bỏ tính năng $\rightarrow$ cập nhật hoặc xóa skill tương ứng trong cùng commit.
5. **Quy Chuẩn Liên Kết Markdown (Relative Markdown Links Only):** Tuyệt đối cấm sử dụng URL tuyệt đối máy chủ (`file://...`) trong toàn bộ tài liệu Markdown (`docs/`, `.agents/`, `README.md`). Mọi liên kết tham chiếu tài liệu nội bộ phải dùng đường dẫn tương đối (ví dụ: `../PRD/...`, `./...`, `../../apps/...`).
6. **Quy Chuẩn Ngôn Từ & Bố Cục Tối Giản 80/20 (Product-Grade Radical Minimalism):** Tuyệt đối cấm văn mẫu, khẩu hiệu sáo rỗng, tên thuật toán (AES-256, HMAC, SHA-256), chuẩn kỹ thuật (ISO 32000-1, RFC), cơ chế nội bộ (RAM Zero-Retention, Token TTL, UUID) và mã màu kỹ thuật (#hex) trên giao diện. Danh xưng không cần thiết bị loại bỏ; trạng thái xác thực biểu thị bằng icon tích xanh nhỏ cạnh họ tên người dùng thay vì badge cồng kềnh; giao diện chỉ giữ lại các thành phần cốt lõi thật sự cần thiết theo chuẩn các sản phẩm quốc tế hàng đầu (Apple, Stripe, Linear, Claude).
7. **Quy Chuẩn Liêm Chính Học Thuật Đồ Án (Academic Purity & Thesis Invariants):**
   - **Chương 2 là không gian khoa học thuần khiết:** Tuyệt đối cấm đưa đường dẫn thư mục repository (`packages/`, `apps/`, `src/`) và tên interface mã nguồn nội bộ (`IAcademicSearchResolverPort`, `PostgresStorageAdapter`) vào Chương 2. Mọi khái niệm phải diễn đạt bằng thuật ngữ kiến trúc khoa học (Tầng lõi nghiệp vụ, Tầng cổng trừu tượng, Tầng điều hợp hạ tầng). Chi tiết mã nguồn chỉ được phép xuất hiện tại Chương 3 và Chương 4.
   - **Cấm lộ mã LaTeX thô trong bản thảo duyệt:** Trong mọi bản thảo Markdown gửi người dùng xem trước, trích dẫn phải hiển thị chuẩn dạng số học thuật `[1]`, `[2]` hoặc `(Tác giả, Năm)`; tuyệt đối không để sót các thẻ thô như `\cite{...}. T`, `\ref{...}` hay macro LaTeX chưa render.
   - **Giới hạn tham chiếu tinh hoa (Reference Cap Invariant):** Toàn bộ danh mục tài liệu tham khảo (Bibliography) của đồ án bắt buộc phải $\le 20$ tài liệu ($N_{\text{refs}} \le 20$). Mọi tài liệu trích dẫn phải là các ấn phẩm kinh điển, hội nghị/tạp chí uy tín hàng đầu hoặc quy chế chính thống, tuyệt đối cấm đưa tài liệu lấp chỗ trống.
8. **Quy Chuẩn Kiến Trúc Báo Cáo Chuẩn Paper Khoa Học (Human-Centric Academic Paper Architecture):**
   - **Kiến trúc cho người đọc, không phải cho máy đọc:** Mọi sơ đồ kiến trúc và mô tả hệ thống trong báo cáo đồ án (đặc biệt tại Chương 2 và Chương 3) phải được thiết kế theo tư duy của các bài báo khoa học quốc tế uy tín (như mô hình Transformer Attention, kiến trúc RAG, GraphRAG của cộng đồng nghiên cứu).
   - **Tập trung vào dòng chảy tri thức và khối thuật toán:** Thể hiện rõ nét luồng biến đổi dữ liệu toán học (*Dataflow & Knowledge Transformation*), các khối chức năng trừu tượng hóa mức độ cao (*Embedding, Retrieval, Rank Fusion, Reasoning Loop*), tuyệt đối cấm vẽ sơ đồ kiểu máy móc (class diagram với getter/setter, endpoint REST, đường dẫn code, thao tác CRUD vụn vặt). Sơ đồ phải đóng vai trò là một mô hình tư duy học thuật (*Academic Mental Model*) tự giải thích, giúp người đọc nắm bắt ngay đóng góp khoa học và tính mới của đề tài.

---

## 3. Bộ Định Tuyến Kỹ Năng (Skill Router - Progressive Disclosure)
Trước khi bắt đầu tác vụ chuyên biệt, nạp hướng dẫn kỹ thuật từ `.agents/skills/`:

| Lĩnh vực tác vụ | Skill cần nạp | Đường dẫn tham chiếu |
| :--- | :--- | :--- |
| **Backend / API / DB** | `verischolar-backend` | [`.agents/skills/verischolar-backend/SKILL.md`](./skills/verischolar-backend/SKILL.md) |
| **Frontend / PDF / SSE** | `verischolar-frontend` | [`.agents/skills/verischolar-frontend/SKILL.md`](./skills/verischolar-frontend/SKILL.md) |
| **Unit & Integration Test** | `verischolar-tdd` | [`.agents/skills/verischolar-tdd/SKILL.md`](./skills/verischolar-tdd/SKILL.md) |
| **Bảo trì / Sửa quy tắc / Học từ lỗi (`/learn`)** | `agent-maintenance` | [`.agents/skills/agent-maintenance/SKILL.md`](./skills/agent-maintenance/SKILL.md) |
| **UI/UX & Design** | `ui-ux-pro-max`, `ui-styling` | [`.agents/skills/ui-ux-pro-max/SKILL.md`](./skills/ui-ux-pro-max/SKILL.md) |

Nguyên tắc kiến trúc tối thượng: Đọc [`.agents/ARCHITECTURE_PRINCIPLES.md`](./ARCHITECTURE_PRINCIPLES.md).

---

## 4. Bốn Cổng Xác Minh Bắt Buộc (The 4 Verification Gates)
Trước khi hoàn thành bất kỳ task nào hoặc tạo commit, bắt buộc xác nhận 100% exit code 0:
```bash
uv run ruff check . && uv run ruff format --check .  # Cổng 1: Linter & Formatter Python
uv run pytest                                        # Cổng 2: Toàn bộ Backend & Boundary Tests
npm --prefix apps/web run test                       # Cổng 3: Frontend Unit Tests
npm --prefix apps/web run build                      # Cổng 4: Production Build Giao Diện
```
