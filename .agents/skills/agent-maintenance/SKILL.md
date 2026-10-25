---
name: agent-maintenance
description: Use when maintaining the VeriScholar Agent Harness, updating rules after architecture changes, or executing the /learn mistake-learning protocol after user feedback to guarantee zero recurrence.
---

# Agent Harness Maintenance, Anti-Rot & `/learn` Zero-Recurrence Protocol

Tài liệu này quy định cách bảo trì bộ công cụ Agent Harness, giữ quy tắc đồng bộ với mã nguồn thực tế và thực thi vòng lặp **Học Từ Lỗi & Chống Tái Phạm Tuyệt Đối (`/learn`)** cho VeriScholar.

---

## 1. Quy Tắc Cam Kết Cùng Vị Trí (Co-Location Commit Rule)
Mọi tác nhân khi phát triển dự án phải tuân thủ nguyên tắc:
1. **Thêm Endpoint mới:** Viết code + test $\rightarrow$ Bổ sung quy chuẩn vào `verischolar-backend/SKILL.md` trong cùng commit.
2. **Sửa đổi CSDL:** Tạo migration $\rightarrow$ Cập nhật `verischolar-backend/SKILL.md` và `scripts/dev/seed.py` trong cùng commit.
3. **Xóa một tính năng:** Xóa mã nguồn + test $\rightarrow$ Xóa bỏ hướng dẫn tương ứng trong `.agents/skills/` và bổ sung tên class/từ khóa vào blacklist cấm của `test_architecture_boundary.py`.

---

## 2. Tháp Thẩm Quyền Phân Xử Mâu Thuẫn (Authority Hierarchy)
Khi phát hiện sự sai lệch giữa tài liệu và mã nguồn, Agent bắt buộc giải quyết theo thứ tự ưu tiên:
$$\mathbf{Code\ Thực\ Tế\ \&\ Tests\ Đang\ Pass} > \mathbf{Tài\ Liệu\ Specs\ (docs/specs/)} > \mathbf{Tài\ Liệu\ Skills\ (.agents/skills/)}$$

Nếu một quy tắc trong Skill mâu thuẫn với bài test đang PASS, Agent phải coi Skill là lỗi thời và tiến hành cập nhật lại Skill theo bài test.

---

## 3. Giao Thức Học Từ Lỗi & Chống Tái Phạm (`/learn` Zero-Recurrence Protocol)

Khi User phản hồi AI làm sai hoặc kích hoạt `/learn`, TUYỆT ĐỐI KHÔNG chỉ xin lỗi và sửa tạm thời. Bắt buộc thực hiện đúng 4 bước:

1. **Bước 1 — Cô lập nguyên nhân & Lời biện minh (Root Cause Isolation):**
   Xác định chính xác: (a) Hành vi sai là gì, (b) Tại sao AI lại chọn hành vi đó (áp lực ngữ cảnh, hiểu sai phạm vi, hay thiếu cổng kiểm tra), và (c) Quy tắc thuộc phạm vi toàn cục (`.agents/AGENTS.md`) hay chuyên biệt (`.agents/skills/<skill>/SKILL.md`).
2. **Bước 2 — Trình duyệt `learning_proposal.md` (Proposal Gate):**
   Tạo/cập nhật artifact `learning_proposal.md` (`RequestFeedback: true`) nêu rõ file dự kiến sửa và bài test dự kiến thêm. Dừng lại chờ User phê duyệt trước khi sửa `.agents/`.
3. **Bước 3 — Chuyển hóa thành Cổng Chặn Cơ Học (Mechanical Gate First):**
   Nếu lỗi có thể phát hiện bằng AST, Regex, cấu trúc file hoặc độ dài dòng, BẮT BUỘC viết thêm hàm kiểm thử vào `apps/api/tests/test_architecture_boundary.py` (chứng minh RED khi có lỗi $\rightarrow$ GREEN khi sửa lỗi).
4. **Bước 4 — Chuẩn hóa Công Thức Dương & Bảng Chặn Biện Minh (Positive Recipe & Red-Flag Table):**
   Với các quy tắc về văn phong/nghiệp vụ không thể bắt hoàn toàn bằng Regex, ghi nhận vào bảng **Locked Anti-Recurrence Registry** bên dưới dưới dạng **Positive Recipe (Công thức cấu trúc đầu ra)** kèm **Red-Flag Rationalizations**.

### Locked Anti-Recurrence Registry (Danh Mục Các Lỗi Đã Khóa)

| Mã lỗi | Hành vi sai đã từng xảy ra | Lời biện minh bị cấm (Red Flags) | Cơ chế khóa chống tái phạm (Defense Layer) |
| :--- | :--- | :--- | :--- |
| **ERR-01: Absolute URL Leak** | Dùng URL tuyệt đối máy chủ (`file://...`) hoặc liên kết tương đối bị đứt trong các file `.md` của repo (`docs/`, `.agents/`, `README.md`). | *"System prompt yêu cầu dùng file:// cho link"* (Nhầm giữa câu trả lời chat và tài liệu lưu trữ trong Git). | **Mechanical Gate:** `test_no_absolute_file_urls_in_markdown()` và `test_no_broken_relative_links_in_markdown()` trong `test_architecture_boundary.py`. |
| **ERR-02: PRD Scope Creep & Bloat ("Mớ bòng bong")** | Tự bịa thêm tính năng ngoài kiến trúc trong Luồng ngoại lệ (offline sync, giấy A0/A1, nhập tay Graph, Draft Mode) hoặc viết văn xuôi dài dòng. | *"Thêm tính năng phụ để xử lý ngoại lệ trông chuyên nghiệp hơn"* | **Positive Recipe + Gate:** `test_prd_conciseness_and_structure_invariants()` ép mỗi file `docs/PRD/*.md` giữ trong khoảng `120–210` dòng, đủ 4 mục chuẩn; Luồng ngoại lệ chỉ trả mã lỗi/thông báo hoặc điều hướng về tính năng có sẵn trong Specs. |
| **ERR-03: Plan Code Placeholders** | Để lại `...` hoặc `# TODO` bên trong khối code kiểm thử/triển khai của `docs/superpowers/plans/*.md`. | *"Viết `...` cho ngắn gọn vì Subagent tự hiểu được"* | **Mechanical Gate:** `test_no_code_placeholders_in_superpowers_plans()` trong `test_architecture_boundary.py`. |
| **ERR-04: Coder-Cluttered Mermaid Diagrams** | Nhồi tên file code (`.tsx`, `.py`), thẻ HTML (`<b>`, `<br/>`) hoặc danh sách tên hàm unit test vào trong các ô sơ đồ Mermaid khiến ảnh xuất ra báo cáo bị rối và bé li ti. | *"Viết tên file code và danh sách test vào sơ đồ cho chi tiết"* (Sơ đồ là để con người/Hội đồng nhìn luồng khái niệm & giao thức; tên file code và danh sách test phải đặt ở Bảng Markdown bên dưới). | **Mechanical Gate:** `test_mermaid_diagrams_are_human_centric_paper_grade()` trong `test_architecture_boundary.py`. |
| **ERR-05: Engineering-Centric & Verbose UI Copy** | Đưa tên thuật toán (AES-256, HMAC), chuẩn ISO 32000-1, chính sách Zero-Retention, mã màu (#hex), danh xưng rườm rà ("Nhà nghiên cứu Khoa học", "Học giả đã xác thực") lên giao diện. | *"Khoe công nghệ để trông uy tín, giải thích dài dòng cho rõ"* (Người dùng chỉ cần trải nghiệm tối giản 80/20 như Apple, Stripe, Linear; tích xanh nhỏ thay thế badge). | **Mechanical Gate:** `test_no_engineering_brag_or_forbidden_copy_in_frontend()` trong `test_architecture_boundary.py`. |

---

## 4. Rà Soát Định Kỳ Với Bài Test Ranh Giới Kiến Trúc
Chạy bài test kiểm tra ranh giới kiến trúc để phát hiện vi phạm:
```bash
uv run pytest apps/api/tests/test_architecture_boundary.py -v
```
Bài test sẽ tự động kiểm tra:
* Không vi phạm Kiến trúc Lục giác trong `packages/core/`.
* Không có chuỗi ký tự di sản cấm (`aiosqlite`, `sqlite3`, `neo4j`, `ComparisonMatrix`, `DeBERTa`).
* File `AGENTS.md` không bị phình to quá 200 dòng.
* Không có URL tuyệt đối `file:///` hoặc liên kết tương đối bị đứt trong toàn bộ tài liệu Markdown.
* Toàn bộ PRD giữ đúng cấu trúc BA tinh gọn (`120–210` dòng) và các bản kế hoạch (`docs/superpowers/plans/`) không chứa placeholder `...`.
