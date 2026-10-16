# Đặc Tả Tính Năng: Phân Giải Tài Liệu Tham Khảo & Nạp Vào Phiên Đọc Sâu (PRD §3.3)
## Academic Reference Resolving & In-Session Ingestion

**Module:** Module 3 — Multi-Paper Cross Synthesis & Automated Literature Review  
**Quy chuẩn:** PRD §3.3 (Reference Extraction, Resolution & In-Session Ingestion)  
**Nhánh Git:** `feat/module3-cross-synthesis` (Commit `dfa0a43` & `d96df89`)

---

## 1. MỤC TIÊU NGHIỆP VỤ

Trong quá trình đọc bài báo tại Module 1, người dùng có nhu cầu mở rộng sang các công trình được trích dẫn trong danh mục tham khảo (References).

Quy trình giải quyết gồm 3 bước khép kín:
1. **Bóc tách danh mục tham khảo (Reference Extraction):** Quét tiêu đề `References`/`Bibliography` ở cuối file PDF, phân rã các dòng trích dẫn thành tiêu đề (`title`), tác giả (`authors`), năm (`year`), mã `doi`, `arxiv_id`.
2. **Phân giải học thuật thông minh (Deterministic Academic Resolving):**
   - Cổng trừu tượng `IAcademicSearchResolverPort` gọi `ExaAcademicResolverAdapter` (sử dụng Exa API thực tế với category `research paper`).
   - Trích xuất tự động siêu dữ liệu công khai: số lượt trích dẫn (`citation_count`), tóm tắt (`abstract`), và liên kết tải toàn văn mở (`open_access_pdf_url`).
   - Bộ đệm `GlobalAcademicCache` lưu trữ kết quả phân giải dựa trên khóa chuẩn hóa DOI/arXiv (< 10ms hit latency).
   - **Public-Only Cache Isolation:** Tuyệt đối chỉ lưu tài liệu công khai; bản thảo riêng tư của người dùng bị chặn ngay tại cổng vào bộ đệm.
3. **Nạp vào phiên nghiên cứu (In-Session Ingestion):**
   - Người dùng lựa chọn các bài báo mong muốn từ bảng thẻ tham khảo `SmartReferenceDrawer.tsx`.
   - **Ràng buộc Ngưỡng trần Phiên (Session Capacity Cap $\le 5$ papers):**
     - Tổng số bài báo mở trong một phiên đọc sâu không được vượt quá 5 bài.
     - Backend trả về `HTTP 422 Unprocessable Entity` (`SESSION_CAPACITY_EXCEEDED`) nếu `current_docs + selected_refs > 5`.
     - Frontend tự động vô hiệu hóa nút nạp bài và hiển thị banner cảnh báo.
   - Khi nạp thành công, hệ thống tải PDF, khởi tạo `DocumentModel`, liên kết vào `session_documents` và mở rộng tab trên `DocumentTabBar.tsx`.

---

## 2. THIẾT KẾ DỮ LIỆU & KIẾN TRÚC

### Entity Domain ([`ResolvedAcademicReference`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/src/core/domain/entities/reference.py))
```python
class ResolvedAcademicReference(BaseModel):
    ref_index: int
    raw_text: str
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    open_access_pdf_url: str | None = None
    abstract: str | None = None
    citation_count: int | None = None
    sources: list[str] = Field(default_factory=list)
    landing_url: str | None = None
    is_ingested: bool = False
    resolved_document_id: UUID | None = None
```

### Port Lục Giác ([`IAcademicSearchResolverPort`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/src/core/ports/academic_resolver.py))
```python
class IAcademicSearchResolverPort(ABC):
    @abstractmethod
    async def resolve_reference(self, reference: ExtractedReference) -> ResolvedAcademicReference:
        pass

    @abstractmethod
    async def resolve_batch(self, references: list[ExtractedReference]) -> list[ResolvedAcademicReference]:
        pass
```

---

## 3. REST API ENDPOINTS

### 1. `POST /api/v1/documents/{document_id}/references:resolve`
- **Chức năng:** Phân giải danh mục tài liệu tham khảo đã bóc tách của bài báo.
- **Query params:** `ref_indices` (tùy chọn: chỉ phân giải các chỉ số được chỉ định).
- **Phản hồi (`200 OK`):** Trả về danh sách `ResolvedAcademicReference` kèm cờ nhận diện Open-Access.

### 2. `POST /api/v1/sessions/{session_id}/references:ingest`
- **Chức năng:** Nạp các bài báo tham khảo đã chọn vào phiên nghiên cứu hiện tại.
- **Body:** `{"document_id": UUID, "selected_ref_indices": list[int]}`.
- **Ràng buộc:** Nếu vượt quá 5 bài $\rightarrow$ Trả về `HTTP 422 SESSION_CAPACITY_EXCEEDED`.

---

## 4. GIAO DIỆN NGƯỜI DÙNG: `SmartReferenceDrawer.tsx`
- Bảng hiển thị 3 cột trực quan:
  1. *Cột 1:* Checkbox chọn lẻ và master checkbox "Chọn tất cả / Bỏ chọn".
  2. *Cột 2:* Tiêu đề in đậm (mở tab ngoài), tác giả, năm, tóm tắt và Thẻ trạng thái: `[🟢 Đã tìm thấy PDF Open-Access]` vs `[🟡 Chỉ có Abstract]`.
  3. *Cột 3:* Thẻ định danh nguồn (arXiv, Crossref, Semantic Scholar, Exa) kèm icon mở liên kết ngoài `↗`.
- Bộ đếm sức chứa phiên: `Đang mở: X/5 bài. Còn trống: Y bài`.
- Vô hiệu hóa nút và cảnh báo đỏ khi người dùng tích chọn vượt quá dung lượng trống.
