# Scholarly Discovery, 2-Tier Ingestion & Document Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa hành trình Khám phá Đề tài từ con số 0 (Zero-to-Reading) tích hợp tìm kiếm đa nguồn học thuật mở (Exa AI, Semantic Scholar, arXiv), quy trình nạp tài liệu 2 tầng bất đối xứng (< 500ms cho Tầng 1 metadata, Tầng 2 chạy ngầm PyMuPDF bóc tách theo đúng thứ tự đọc học thuật 2 cột gắn tọa độ Bounding Box và sinh Vector 1536), kho lưu trữ bất biến CAS khử trùng lặp qua SHA-256 và cơ chế tiêu hủy vật lý dứt điểm (Zero-Retention).

**Architecture:** Áp dụng Kiến trúc Lục giác (Hexagonal Architecture): Cổng trừu tượng `IScholarlySearchPort`, bộ chuẩn hóa tọa độ Bounding Box và các ràng buộc kiểm tra tính hợp lệ của tệp PDF nằm trong `packages/core`; dịch vụ `DocumentService`, Adapter tìm kiếm học thuật ngoài và đường ống bóc tách PyMuPDF nằm trong `apps/api`; tầng lưu trữ dữ liệu kết hợp PostgreSQL (`documents`, `document_chunks`, `document_storage_blobs`) và kho CAS tệp nhị phân (`storage/blobs/`); tầng giao diện `apps/web` cung cấp trang `DiscoveryPage` với phân loại thẻ trực quan (`Open Access PDF` vs `Abstract Only`) và modal tải lên tài liệu cá nhân.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16+ (`pgvector`), PyMuPDF (`fitz`), Exa AI SDK, React 19, TypeScript, Tailwind CSS, Zustand v5.

**Spec:** [`docs/specs/02-discovery-and-documents-spec.md`](../../specs/02-discovery-and-documents-spec.md) & [`docs/PRD/02-discovery-and-documents-crud.md`](../../PRD/02-discovery-and-documents-crud.md).

---

## Global Constraints

- 100% mã nguồn trong `packages/core/` chỉ dùng Python Standard Library và `pydantic`, cấm tuyệt đối import `fastapi`, `sqlalchemy`, `pymupdf`, `fitz`, `httpx`.
- Giới hạn tệp PDF nạp vào hệ thống: tối đa **50 MB** ($52.428.800$ bytes) và tối đa **100 trang**; vượt quá phải trả về mã `413 PDF_FILE_TOO_LARGE` hoặc `422 PDF_PAGE_LIMIT_EXCEEDED`.
- Tệp PDF bắt buộc là Digital PDF có lớp văn bản số hóa (trang 1 có ít nhất 50 ký tự trích xuất được); tệp scan ảnh thuần túy phải bị từ chối với mã `422 PDF_NO_TEXT_LAYER`.
- Mọi thao tác truy vấn tài liệu trong `documents` bắt buộc lọc theo `WHERE user_id = :current_user_id`. Khi truy vấn ID không thuộc quyền sở hữu, trả về `404 DOCUMENT_NOT_FOUND`.
- Cam kết Tiêu hủy Vật lý Đồng bộ (Zero-Retention Invariant): Khi xóa tài liệu (`DELETE /api/v1/documents/{id}`), nếu `ref_count` trong `document_storage_blobs` giảm về 0, tệp nhị phân trên đĩa cứng máy chủ (`storage/blobs/ab/cd/hash.pdf`) bắt buộc phải bị tiêu hủy dứt điểm ngay trong cùng chu kỳ xử lý đó.
- Bảng mã lỗi phản hồi bắt buộc tuân thủ 100% Ma Trận Mã Lỗi Chuẩn Hóa trong Mục 4.D của [`docs/specs/02-discovery-and-documents-spec.md`](../../specs/02-discovery-and-documents-spec.md).
- Toàn bộ liên kết trong tài liệu Markdown dùng đường dẫn tương đối (`./...`, `../...`, `../../...`), tuyệt đối không dùng link tuyệt đối máy chủ.
- Bốn Cổng Xác Minh Bắt Buộc (`uv run ruff check .`, `uv run pytest`, `npm --prefix apps/web run test`, `npm --prefix apps/web run build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **Scanned Image PDF Text Layer Absence Detection:** Khi người dùng tải lên một tệp PDF quét ảnh thuần túy mà trang 1 có ít hơn 50 ký tự trích xuất được, quy trình nạp tài liệu phải từ chối ngay lập tức ở bước xác thực với mã lỗi `422 PDF_NO_TEXT_LAYER` trước khi đẩy vào tác vụ ngầm, đồng thời trả về thông điệp tiếng Việt hướng dẫn người dùng cung cấp bản số hóa có OCR.
2. **Two-Column Academic Reading Order Preservation:** Với các bài báo khoa học 2 cột (IEEE, ACM, Nature), thuật toán bóc tách khối văn bản PyMuPDF phải phân loại và sắp xếp các khối theo thứ tự đọc học thuật (đọc hết cột trái từ trên xuống dưới rồi mới sang cột phải), bảo toàn tính toàn vẹn của các công thức toán học nhiều dòng (multiline LaTeX equations) và tránh xáo trộn ngữ nghĩa.
3. **Zero-Retention Physical Purge on Zero References:** Khi học giả gọi `DELETE /api/v1/documents/{id}`, hệ thống phải kiểm tra bảng `document_storage_blobs`. Nếu không còn bất kỳ tài liệu nào khác trỏ tới cùng mã băm SHA-256 (`ref_count = 0`), tệp nhị phân trên ổ đĩa (`storage/blobs/ab/cd/hash.pdf`) phải bị xóa vĩnh viễn ngay lập tức trong cùng chu kỳ request, cam kết không tồn lưu tệp mồ côi.
4. **Seamless Abstract-Only to Ready Upgrade via Attach-PDF:** Khi một bài báo được tạo ở chế độ chỉ có tóm tắt (`status = 'abstract_only'`), endpoint `POST /api/v1/documents/{id}/attach-pdf` phải nâng cấp bài báo lên `status = 'parsing'` và hoàn tất sang `status = 'ready'`, tự động thay thế chunk 0 bằng các đoạn trích toàn văn mà không làm hỏng phiên đọc đang mở.
5. **Upstream Academic Search Timeout & Graceful Degradation:** Khi cổng tìm kiếm học thuật ngoài (Exa AI, Semantic Scholar, arXiv) phản hồi chậm quá 15 giây hoặc gặp sự cố máy chủ, API phải ngắt kết nối an toàn với mã `504 SEARCH_UPSTREAM_TIMEOUT` hoặc `502 SEARCH_UPSTREAM_ERROR`, không để xảy ra tình trạng treo worker thread của FastAPI.

---

## Implementation Tasks

### Task 1: Core Domain PDF Invariant Validators & Coordinate Bounding Box Normalizer (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/pdf_validator.py`
- Modify: `packages/core/src/core/domain/value_objects/bounding_box.py`
- Modify: `packages/core/src/core/domain/exceptions.py`
- Test: `packages/core/tests/test_pdf_validator_core.py`

**Interfaces:**
- Consumes: Python Standard Library (`dataclasses`, `typing`), `pydantic.BaseModel`.
- Produces:
  - `MAX_PDF_FILE_SIZE_BYTES = 52_428_800` (50 MB).
  - `MAX_PDF_PAGE_COUNT = 100`.
  - `MIN_FIRST_PAGE_TEXT_CHARS = 50`.
  - `validate_pdf_metadata_invariants(file_size: int, page_count: int, first_page_chars: int, is_encrypted: bool) -> None` (ném `DomainValidationError` với các mã: `PDF_FILE_TOO_LARGE`, `PDF_PAGE_LIMIT_EXCEEDED`, `PDF_NO_TEXT_LAYER`, `PDF_PASSWORD_PROTECTED`).
  - `normalize_bbox_coordinates(raw_x0: float, raw_y0: float, raw_x1: float, raw_y1: float, page_width: float, page_height: float) -> tuple[int, int, int, int]` (chuẩn hóa tỷ lệ sang thang đo nguyên $0..1000$).

- [x] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_pdf_validator_core.py`:
```python
import pytest
from core.services.pdf_validator import (
    MAX_PDF_FILE_SIZE_BYTES,
    MAX_PDF_PAGE_COUNT,
    validate_pdf_metadata_invariants,
    normalize_bbox_coordinates,
)
from core.domain.exceptions import DomainValidationError


def test_pdf_validator_enforces_size_and_page_limits():
    # File too large
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(MAX_PDF_FILE_SIZE_BYTES + 1, 10, 100, False)
    assert exc.value.code == "PDF_FILE_TOO_LARGE"

    # Pages exceeded
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(1000, MAX_PDF_PAGE_COUNT + 1, 100, False)
    assert exc.value.code == "PDF_PAGE_LIMIT_EXCEEDED"


def test_pdf_validator_detects_scanned_pdf_without_text():
    # Only 10 chars on page 1 -> scanned image
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(1000, 10, 10, False)
    assert exc.value.code == "PDF_NO_TEXT_LAYER"


def test_pdf_validator_detects_password_protection():
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(1000, 10, 100, True)
    assert exc.value.code == "PDF_PASSWORD_PROTECTED"


def test_normalize_bbox_coordinates_scales_to_thousand():
    # Raw box in center of 600x800 page
    norm = normalize_bbox_coordinates(150.0, 200.0, 450.0, 600.0, 600.0, 800.0)
    assert norm == (250, 250, 750, 750)
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_pdf_validator_core.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.pdf_validator'`.

- [x] **Step 3: Implement `packages/core/src/core/services/pdf_validator.py` and update bounding box VO**

Cài đặt các hằng số kiểm tra giới hạn, hàm xác thực bất biến `validate_pdf_metadata_invariants()` và hàm chuẩn hóa tọa độ `normalize_bbox_coordinates()` thuần túy không dùng thư viện ngoài.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_pdf_validator_core.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add packages/core/src/core/services/pdf_validator.py packages/core/src/core/domain/value_objects/bounding_box.py packages/core/tests/test_pdf_validator_core.py
git commit -m "feat(core): add PDF limit invariants validator and normalized 0..1000 bbox scaler"
```

---

### Task 2: Scholarly Search Port, Multi-Source Search Adapter & Discovery Search Endpoints (`packages/core` & `apps/api`)

**Files:**
- Create: `packages/core/src/core/ports/scholarly_search.py`
- Create: `apps/api/src/api/adapters/scholarly_search_adapter.py`
- Create: `apps/api/src/api/v1/endpoints/discovery.py`
- Test: `apps/api/tests/test_discovery_search_endpoints.py`

**Interfaces:**
- Consumes: Cổng trừu tượng `IScholarlySearchPort`, Exa AI SDK (`category="research paper"`), arXiv API, Semantic Scholar API.
- Produces:
  - Thực thể `ScholarlyPaperSearchResult` (title, authors, publication_year, venue, doi, arxiv_id, abstract, access_status, pdf_url).
  - Endpoint `POST /api/v1/discovery/search` (khử trùng lặp kết quả theo DOI, phân loại `open_access_pdf` vs `abstract_only`).
  - Xử lý mã lỗi chuẩn hóa: `SEARCH_QUERY_EMPTY`, `SEARCH_LIMIT_OUT_OF_RANGE`, `SEARCH_UPSTREAM_ERROR`, `SEARCH_UPSTREAM_TIMEOUT`.

- [x] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_discovery_search_endpoints.py`:
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_discovery_search_empty_query_rejected(async_client: AsyncClient, auth_headers: dict):
    res = await async_client.post("/api/v1/discovery/search", headers=auth_headers, json={"query": "   "})
    assert res.status_code == 400
    err = res.json()["error"]
    assert err["code"] == "SEARCH_QUERY_EMPTY"
    assert "không được để trống" in err["message"]


@pytest.mark.asyncio
async def test_discovery_search_returns_scholarly_results(async_client: AsyncClient, auth_headers: dict):
    res = await async_client.post("/api/v1/discovery/search", headers=auth_headers, json={
        "query": "Direct Preference Optimization",
        "limit": 5
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert isinstance(data, list)
    if len(data) > 0:
        paper = data[0]
        assert "title" in paper
        assert "authors" in paper
        assert paper["access_status"] in ["open_access_pdf", "abstract_only"]
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_discovery_search_endpoints.py -v`  
Expected: FAIL with `404 Not Found` (endpoint `/api/v1/discovery/search` chưa tồn tại).

- [x] **Step 3: Implement `IScholarlySearchPort`, `ScholarlySearchAdapter`, and `discovery.py` endpoint**

Tạo port trong `packages/core/src/core/ports/scholarly_search.py`, cài đặt adapter trong `apps/api/src/api/adapters/scholarly_search_adapter.py` có cơ chế timeout 15s và gộp kết quả theo DOI, sau đó mount router `/discovery` vào `api_v1_router`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_discovery_search_endpoints.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add packages/core/src/core/ports/scholarly_search.py apps/api/src/api/adapters/scholarly_search_adapter.py apps/api/src/api/v1/endpoints/discovery.py apps/api/tests/test_discovery_search_endpoints.py
git commit -m "feat(api): add IScholarlySearchPort, multi-source search adapter, and discovery search endpoint"
```

---

### Task 3: 2-Tier Ingestion Pipeline, CAS Deduplication & Documents Management Endpoints (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/services/document_service.py`
- Modify: `apps/api/src/api/v1/endpoints/documents.py`
- Modify: `apps/api/src/api/v1/endpoints/discovery.py` (`open-reading`)
- Test: `apps/api/tests/test_document_ingestion_and_cas.py`

**Interfaces:**
- Consumes: `validate_pdf_metadata_invariants`, `normalize_bbox_coordinates`, PyMuPDF (`fitz`), `BackgroundTasks`, `IBlobStoragePort`.
- Produces:
  - `POST /api/v1/discovery/open-reading`:
    - Tầng 1 (< 500ms): Lưu metadata + abstract, tạo `DocumentModel` và `ResearchSessionModel`, trả về `session_id`.
    - Tầng 2 (`BackgroundTasks`): Tải PDF về kho CAS, bóc tách khối văn bản 2 cột PyMuPDF, gán Bounding Box và sinh `Vector(1536)`.
  - `POST /api/v1/documents` (`/upload`): Kiểm tra dung lượng `<= 50MB`, `<= 100 trang`, tính SHA-256 khử trùng lặp CAS, quản lý `ref_count`.
  - `POST /api/v1/documents/{id}/attach-pdf`: Nâng cấp bài báo `abstract_only` lên `ready`.
  - `DELETE /api/v1/documents/{id}`: Giảm `ref_count`; nếu về 0, tiêu hủy tệp vật lý ngay lập tức trên đĩa (`storage/blobs/ab/cd/hash.pdf`).

- [x] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_document_ingestion_and_cas.py`:
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cas_deduplication_and_ref_count(async_client: AsyncClient, auth_headers: dict):
    # Upload same PDF twice
    pdf_content = b"%PDF-1.4 mock content with text layer " + (b"word " * 100)
    files = {"file": ("test_paper.pdf", pdf_content, "application/pdf")}
    
    res1 = await async_client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert res1.status_code == 202
    doc1_id = res1.json()["data"]["id"]

    # Upload same file content again
    files2 = {"file": ("test_paper_copy.pdf", pdf_content, "application/pdf")}
    res2 = await async_client.post("/api/v1/documents/upload", headers=auth_headers, files=files2)
    assert res2.status_code == 202
    doc2_id = res2.json()["data"]["id"]
    assert doc1_id != doc2_id  # Separate document records sharing same blob


@pytest.mark.asyncio
async def test_zero_retention_purges_physical_blob_when_last_reference_deleted(async_client: AsyncClient, auth_headers: dict):
    pdf_content = b"%PDF-1.4 unique confidential draft content " + (b"text " * 100)
    files = {"file": ("confidential.pdf", pdf_content, "application/pdf")}
    res_up = await async_client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert res_up.status_code == 202
    doc_id = res_up.json()["data"]["id"]

    res_del = await async_client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["data"]["purged_physical_file"] is True
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_document_ingestion_and_cas.py -v`  
Expected: FAIL (thiếu endpoint `open-reading` hoặc logic xóa vật lý CAS chưa hoàn tất).

- [x] **Step 3: Implement 2-Tier ingestion, CAS deduplication, and Zero-Retention cascade purge**

Cập nhật `DocumentService` trong `apps/api/src/api/services/document_service.py`, bổ sung endpoint `open-reading` trong `discovery.py`, và hoàn thiện các phương thức CRUD tài liệu trong `documents.py`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_document_ingestion_and_cas.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add apps/api/src/api/services/document_service.py apps/api/src/api/v1/endpoints/documents.py apps/api/src/api/v1/endpoints/discovery.py apps/api/tests/test_document_ingestion_and_cas.py
git commit -m "feat(api): implement 2-tier ingestion, PyMuPDF 2-column chunking, CAS dedup, and Zero-Retention purge"
```

---

### Task 4: Frontend Discovery Page, Scholarly Result Cards & PDF Ingestion UI (`apps/web`)

**Files:**
- Modify: `apps/web/src/features/discovery/components/DiscoveryPage.tsx`
- Create: `apps/web/src/features/discovery/components/ScholarlyResultCard.tsx`
- Modify: `apps/web/src/features/documents/components/DocumentUploadModal.tsx`
- Test: `apps/web/src/features/discovery/__tests__/DiscoveryPage.test.tsx`

**Interfaces:**
- Consumes: Endpoints `POST /api/v1/discovery/search`, `POST /api/v1/discovery/open-reading`, `POST /api/v1/documents/upload`.
- Produces:
  - Ô tìm kiếm trung tâm lớn với danh sách gợi ý chủ đề học thuật phổ biến.
  - `ScholarlyResultCard`:
    - Huy hiệu `🟢 Có sẵn PDF Open Access` kèm nút `[📖 Mở Đọc Sâu (Full PDF)]`.
    - Huy hiệu `🔒 Chỉ có Tóm tắt (Paywall)` kèm nút `[📄 Xem Tóm Tắt (Abstract)]`.
    - Bấm nút gọi `open-reading` và chuyển hướng tức thì sang `/dashboard/{sessionId}` (< 500ms).
  - `DocumentUploadModal`: Vùng kéo thả PDF với kiểm tra giới hạn 50MB / 100 trang tại client và thanh tiến độ tải lên trực quan.

- [x] **Step 1: Write the failing test**

Tạo `apps/web/src/features/discovery/__tests__/DiscoveryPage.test.tsx`:
```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { DiscoveryPage } from '@/features/discovery/components/DiscoveryPage';

describe('DiscoveryPage Component', () => {
  it('renders search bar and displays Open Access vs Abstract Only cards', async () => {
    render(<DiscoveryPage />);
    
    const searchInput = screen.getByPlaceholderText(/tìm kiếm bài báo/i);
    expect(searchInput).toBeInTheDocument();
    
    fireEvent.change(searchInput, { target: { value: 'Transformer language models' } });
    fireEvent.keyDown(searchInput, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
      expect(screen.getByText(/Mở Đọc Sâu/i)).toBeInTheDocument();
    });
  });
});
```

- [x] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- DiscoveryPage`  
Expected: FAIL with component missing or elements not found.

- [x] **Step 3: Implement `DiscoveryPage.tsx`, `ScholarlyResultCard.tsx`, and `DocumentUploadModal.tsx`**

Cập nhật giao diện Discovery gọi đúng API `discoveryApi.search()`, render danh sách thẻ kết quả bài báo với 2 loại nút bấm và kết nối luồng nạp 2 tầng Zero-to-Reading.

- [x] **Step 4: Run test and build to verify all 4 verification gates pass**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`  
Expected: 100% PASS (exit code 0)

- [x] **Step 5: Commit**

```bash
git add apps/web/src/features/discovery/ apps/web/src/features/documents/
git commit -m "feat(web): add Discovery search page, ScholarlyResultCard with 2 access modes, and PDF upload modal"
```
