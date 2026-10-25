---
name: agent-maintenance
description: Quy trình bảo trì hệ thống Agent Harness, rà soát quy tắc và chống suy thoái nhận thức (Rule Rot) cho VeriScholar.
---

# Agent Harness Maintenance & Anti-Rot Protocol

Tài liệu này hướng dẫn cách bảo trì bộ công cụ Agent Harness và giữ cho các quy tắc luôn đồng bộ với mã nguồn thực tế của VeriScholar.

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

## 3. Rà Soát Định Kỳ Với Bài Test Ranh Giới Kiến Trúc
Chạy bài test kiểm tra ranh giới kiến trúc để phát hiện vi phạm:
```bash
uv run pytest apps/api/tests/test_architecture_boundary.py -v
```
Bài test sẽ tự động kiểm tra:
* Không vi phạm Kiến trúc Lục giác trong `packages/core/`.
* Không có chuỗi ký tự di sản cấm (`aiosqlite`, `sqlite3`, `neo4j`, `ComparisonMatrix`, `DeBERTa`).
* File `AGENTS.md` không bị phình to quá 200 dòng.
