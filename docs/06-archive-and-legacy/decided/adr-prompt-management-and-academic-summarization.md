# ADR: Chuẩn Quản Lý Prompts-as-Code & Tóm Tắt Học Thuật Độ Sâu Thích Ứng

- **Trạng thái:** Chấp thuận (Accepted)
- **Ngày quyết định:** 2026-09-16
- **Phạm vi:** Toàn bộ hệ thống AI / LLM pipeline (Module 1, Module 2, Module 3)

---

## 1. Ngữ Cảnh (Context)
Trước đây, chuỗi System Prompt tóm tắt tài liệu được nhúng trực tiếp (hardcoded) trong mã nguồn Python adapter (`apps/api/src/api/adapters/llm_summarizer.py`).
Hơn nữa, prompt chỉ yêu cầu tóm tắt 1 câu ngắn gọn, dẫn đến tình trạng mô hình LLM trả ra nội dung quá ngắn, liệt kê từ khóa hời hợt, không đáp ứng được yêu cầu chuyên sâu của người dùng học thuật và nhà nghiên cứu.

## 2. Quyết Định Kiến Trúc (Decisions)
1. **Chuẩn chất lượng học thuật "Adaptive Informative Depth":**
   - Không ép ngắn nhân tạo để tiết kiệm token; ưu tiên tối đa chất lượng truyền đạt tri thức.
   - Mỗi chiều trong 3 ý cốt lõi (`problem_statement`, `contributions`, `limitations`) phải đạt độ sâu 2-3 câu chứa đựng nguyên nhân kỹ thuật (*Why*), cơ chế đột phá (*How*) và số liệu thực nghiệm (*Empirical gains*).
   - Bảo toàn 100% nguyên tắc *Visual Grounding*: mỗi ý kèm một câu trích dẫn nguyên văn (*verbatim quote*) có tọa độ bounding box 5 phần tử `[x0, y0, x1, y1, page]`.

2. **Kiến trúc quản lý Prompts-as-Code (.prompt.md):**
   - Chuẩn hóa định dạng file prompt kết hợp **YAML Frontmatter** (metadata, model, temperature, input variables) và **Markdown + Jinja2 Templating** (nội dung hướng dẫn và context linh hoạt).
   - Tổ chức tập trung trong `packages/core/src/core/prompts/`.
   - Xây dựng module `PromptTemplate` / `PromptRegistry` nhẹ nhàng trong `packages/core` để load và render an toàn.

## 3. Hệ Quả & Lợi Ích (Consequences)
- **Tách biệt mối quan tâm (SoC):** Kỹ sư AI và chuyên gia nội dung có thể tinh chỉnh prompt trong tệp `.prompt.md` độc lập, xem xét diff trực quan trên Git mà không cần can thiệp logic Python.
- **Tính tái lập & Đánh giá (Eval Reproducibility):** Lưu vết phiên bản prompt (`version: 1.1.0`) vào snapshot và audit metrics để benchmark định lượng sự tiến bộ của mô hình.
- **Chất lượng người dùng vượt bậc:** Người dùng nhận được bản tóm tắt giàu giá trị học thuật, bám sát các phát hiện thực nghiệm của bài báo thay vì các câu tóm lược chung chung.
