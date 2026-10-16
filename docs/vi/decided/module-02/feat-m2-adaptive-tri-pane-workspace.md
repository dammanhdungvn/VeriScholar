# Module 2: Không Gian Soạn Thảo Thích Ứng 3 Cột (Adaptive Tri-Pane Workspace)

## 1. Tổng quan & Triết lý Thiết kế
Không gian làm việc Module 2 giải quyết đồng thời 3 nhu cầu cấp thiết của nhà nghiên cứu:
1. **Soạn thảo mã nguồn trực tiếp (Code & Text Editor):** Can thiệp mã LaTeX/Markdown với đánh số dòng và hiển thị cảnh báo lỗi linter theo thời gian thực.
2. **Xem trước bản dựng PDF trực tiếp (Live PDF Preview):** Hiển thị bản biên dịch PDF tức thì với khả năng phủ khung viền Bounding Box dẫn chứng vàng.
3. **Trợ lý AI & SAFE Fact-Checking (AI Writing & SAFE Assistant):** Khung điều khiển kích hoạt kiểm chứng mệnh đề sự thật và hỗ trợ viết Literature Review.

---

## 2. 5 Chế Độ Chuyển Đổi Khung Hình Linh Hoạt (Workspace Modes)
Người dùng có thể chuyển đổi nhanh 1-click thông qua thanh công cụ `WritingHeaderBar`:

| Chế độ | Layout | Mục đích sử dụng |
|---|---|---|
| **Tri-Pane Mode** (`tri-pane`) | `[Code] \| [PDF] \| [AI]` | Màn hình lớn (Desktop / Ultra-wide), làm việc đa nhiệm toàn diện |
| **Dual-Pane Code & Preview** (`dual-code`) | `[Code] \| [PDF]` | Sửa thủ công chi tiết và đối chiếu ngay kết quả hiển thị trên PDF |
| **Dual-Pane AI & Preview** (`dual-ai`) | `[PDF] \| [AI]` | Tập trung trao đổi với AI, tinh chỉnh câu từ và rà soát các thẻ trích dẫn |
| **Zen PDF Mode** (`zen-pdf`) | `[PDF 100%]` | Rà soát toàn trang in ấn, kiểm tra ngắt dòng và bố cục trước khi nộp |
| **Zen Code Mode** (`zen-code`) | `[Code 100%]` | Tập trung chuyên sâu gõ văn bản dài mà không bị phân tán thị giác |

---

## 3. Kiến trúc Thành phần Frontend (`apps/web/src/features/writing/`)

```
apps/web/src/features/writing/
├── api/
│   ├── draftsApi.ts             # API client (CRUD, OCC If-Match, SAFE verify, Compile, Export)
│   └── draftsApi.test.ts        # Unit tests cho draftsApi
├── components/
│   ├── WritingHeaderBar.tsx     # Header bar: Tên bài, v{version}, Save, Compile, Export, Mode toggles
│   ├── WritingHeaderBar.test.tsx# Unit tests cho HeaderBar
│   ├── WritingEditorPane.tsx    # Cột 1: Monospace editor, Line numbers, Linter diagnostic panel
│   ├── WritingPreviewPane.tsx   # Cột 2: Live PDF viewer, Zoom controls, BoundingBox highlight layer
│   ├── WritingAssistantPane.tsx # Cột 3: SAFE summary bar, Atomic claim cards, AI prompt suggestions
│   ├── WritingWorkspace.tsx     # Container điều phối 3 cột theo WorkspaceMode & phím tắt Ctrl+S
│   └── WritingPage.tsx          # Trang định tuyến router (/writing và /writing/:draftId)
├── stores/
│   ├── useWritingStore.ts       # Zustand store: activeDraft, editorContent, boundingBoxes, OCC state
│   └── useWritingStore.test.ts  # Unit tests cho Zustand store
└── types/
    └── index.ts                 # TypeScript interfaces (Draft, AtomicClaim, CompileDraftResponse, ...)
```

---

## 4. Tương tác Hai Chiều & Bounding Box Navigation Invariant
- Khi người dùng nhấp vào bất kỳ thẻ mệnh đề nào trong danh sách SAFE Fact-Checking (cột 3):
  - Hệ thống lấy mảng tọa độ `evidence_bounding_boxes: [[x0, y0, x1, y1, page], ...]` và số trang `evidence_page`.
  - Cột 2 (PDF Preview) tự động vẽ khung highlight viền vàng óng ánh (`amber-500` với nền bán trong suốt `amber-400/25` và nhãn `Dẫn chứng #X`) chính xác 100% theo chuẩn tọa độ Top-Left `[0.0, 1.0]`.
- Phím tắt bàn phím: `Ctrl + S` (hoặc `⌘ + S`) tự động kích hoạt lưu ngầm bản thảo và cập nhật thẻ phiên bản OCC `v{version}` trên header.
