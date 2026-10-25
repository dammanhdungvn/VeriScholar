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
