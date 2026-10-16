# Đặc Tả Tính Năng: Đồ Thị Trích Dẫn & Bẻ Gãy Chu Trình (PRD §3.3)
## Academic Citation Graph, Cycle Breaking & Foundational Reading Path

**Module:** Module 3 — Multi-Paper Cross Synthesis & Automated Literature Review  
**Quy chuẩn:** PRD §3.3 (Graph-Augmented RAG, Cycle Breaking & Reading Path)  
**Nhánh Git:** `feat/module3-cross-synthesis` (Commit `dfa0a43`)

---

## 1. MỤC TIÊU NGHIỆP VỤ

Khi một phiên nghiên cứu chứa nhiều bài báo (từ 1 đến tối đa 5 bài), các bài báo này thường có mối quan hệ trích dẫn chéo lẫn nhau (A trích dẫn B, B trích dẫn C, hoặc A và B trích dẫn lẫn nhau).

Hệ thống cung cấp:
1. **Mô hình hóa Đồ thị Trích dẫn (Citation Graph Modeling):**
   - Nút (Nodes): Đại diện cho các bài báo (bao gồm các bài có sẵn trong phiên và các bài tham khảo mở rộng).
   - Cạnh (Edges): Đại diện cho quan hệ trích dẫn ngữ nghĩa:
     - `CITES`: Bài A trích dẫn bài B.
     - `EXTENDS`: Bài A phát triển, mở rộng phương pháp của bài B.
     - `BENCHMARKS_ON`: Bài A thử nghiệm so sánh kết quả trên cùng tập dữ liệu với bài B.
2. **Khống chế độ sâu $k \le 2$ & Bẻ gãy chu trình (Graph Cycle Breaking):**
   - Để ngăn chặn vòng lặp vô tận (infinite circular recursion) khi các bài báo trích dẫn vòng tròn:
     - Giới hạn độ sâu khai phá đa bước tối đa không vượt quá 2 bước nhảy ($k \le 2$).
     - Thuật toán duyệt BFS/DFS tích hợp tập đỉnh và cạnh đã thăm `visited_nodes` và `edge_set`.
     - Tự động bỏ qua các self-loops ($A \to A$) và quan hệ đối xứng đã tồn tại ($A \leftrightarrow B$).
3. **Lộ trình Đọc Nền tảng (Foundational Reading Path):**
   - Áp dụng thuật toán sắp xếp Topo (Topological Sorting - Kahn's Algorithm) trên đồ thị quan hệ phụ thuộc.
   - Sắp xếp thứ tự đọc tối ưu: Bắt đầu từ công trình nền móng (earliest publication year, in-degree cao) $\rightarrow$ các bài mở rộng $\rightarrow$ các bài thực nghiệm so sánh.

---

## 2. THIẾT KẾ DỮ LIỆU & KIẾN TRÚC

### Schemas Phản Hồi ([`SessionCitationGraphResponse`](file:///home/VeriScholar/Workspace/VeriScholar/apps/api/src/api/schemas/session.py))
```python
class CitationGraphNode(BaseModel):
    id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    is_session_document: bool = False
    depth: int = 0

class CitationGraphEdge(BaseModel):
    source: str
    target: str
    relation: str = "CITES"  # CITES | EXTENDS | BENCHMARKS_ON
    confidence: float = 1.0

class SessionCitationGraphResponse(BaseModel):
    session_id: UUID
    nodes: list[CitationGraphNode]
    edges: list[CitationGraphEdge]
    reading_path: list[str]  # Sắp xếp Topo các node IDs
```

---

## 3. REST API ENDPOINT

### `GET /api/v1/sessions/{session_id}/citation-graph`
- **Method:** `GET`
- **Path Parameter:** `session_id` (UUID phiên làm việc).
- **Quyền truy cập:** Chỉ chủ sở hữu phiên (`session.user_id == current_user.id`) mới có quyền truy vấn.
- **Thuật toán xử lý trên máy chủ:**
  1. Lấy danh sách tài liệu hiện có trong phiên qua `SessionDocumentModel` (gán `depth = 0`, `is_session_document = True`).
  2. Bóc tách danh mục tham khảo cấp 1 từ các bài trong phiên (gán `depth = 1`).
  3. Bóc tách danh mục tham khảo cấp 2 (gán `depth = 2`).
  4. Lọc bỏ toàn bộ chu trình qua `edge_set` và bỏ qua self-loops.
  5. Chạy thuật toán Kahn tính toán mảng `reading_path`.
- **Phản hồi (`200 OK`):** Envelope chứa `SessionCitationGraphResponse`.

---

## 4. BẰNG CHỨNG KIỂM THỬ ĐỘC LẬP
- Kiểm thử tại [`apps/api/tests/test_reference_ingestion.py`](file:///home/VeriScholar/Workspace/VeriScholar/apps/api/tests/test_reference_ingestion.py):
  - `test_citation_graph_construction_and_topo_path`: Xác minh cấu trúc đồ thị node-link và thứ tự đọc Topo hợp lệ.
  - `test_citation_graph_cycle_breaking`: Đưa vào đồ thị trích dẫn vòng tròn ($A \leftrightarrow B$ và $A \to B \to C \to A$), xác minh thuật toán bẻ gãy chu trình thành công, không bị lặp vô tận và trả về đồ thị DAG hữu hạn.
- Đã được nghiệm thu độc lập đạt **`VERDICT: PASS`** tại [`docs/handoff/module3-acceptance-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/module3-acceptance-review.md).
