---
name: verischolar-backend
description: Quy chuẩn phát triển backend VeriScholar trên FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16+ pgvector và Kiến trúc Lục giác.
---

# VeriScholar Backend Development Guidelines

Tài liệu này là cẩm nang bắt buộc khi triển khai API, dịch vụ miền, hoặc tương tác cơ sở dữ liệu trên backend VeriScholar (`apps/api`).

---

## 1. Cấu Trúc Monorepo & Router
* **Vị trí router:** Mọi HTTP endpoint phải nằm trong `apps/api/src/api/v1/endpoints/`.
* **Đăng ký router:** Router con phải được tổng hợp tại `apps/api/src/api/v1/router.py`.
* **Chuẩn đặt tên URI:**
  * Danh từ số nhiều: `/api/v1/documents`, `/api/v1/sessions`, `/api/v1/drafts`.
  * Tác vụ tùy chỉnh (Custom Methods theo AIP-136): Sử dụng dấu hai chấm `:` hoặc danh từ rõ nghĩa, ví dụ:
    * `POST /api/v1/drafts/{id}/compile`
    * `POST /api/v1/drafts/{id}:undo`
    * `POST /api/v1/folders/synthesis` (alias: `POST /api/v1/library/graph-query`)

---

## 2. Quản Lý Phiên Cơ Sở Dữ Liệu (Session Management)
* **Request HTTP thông thường:** Bắt buộc dùng FastAPI Dependency Injection:
  ```python
  from fastapi import Depends
  from sqlalchemy.ext.asyncio import AsyncSession
  from api.db.session import get_db

  @router.get("/documents")
  async def list_documents(
      current_user: User = Depends(get_current_active_user),
      db: AsyncSession = Depends(get_db),
  ):
      ...
  ```
* **Tác vụ nền (`BackgroundTasks`):** Tuyệt đối **không** truyền `db: AsyncSession` của request vào background task vì request session sẽ bị đóng khi response hoàn tất. Bắt buộc tạo session mới độc lập:
  ```python
  from api.db.session import AsyncSessionLocal

  async def process_document_background(doc_id: UUID, user_id: UUID):
      async with AsyncSessionLocal() as session:
          # Thao tác CSDL an toàn trong background
          ...
          await session.commit()
  ```

---

## 3. Cô Lập Đa Người Dùng & Bảo Mật (Multi-Tenant Isolation)
* **Quy tắc vàng:** Mọi truy vấn SELECT, UPDATE, DELETE trên bảng nghiệp vụ bắt buộc có điều kiện lọc `user_id = :current_user_id`:
  ```python
  stmt = select(DocumentModel).where(
      DocumentModel.id == doc_id,
      DocumentModel.user_id == current_user.id,
  )
  result = await db.execute(stmt)
  doc = result.scalar_one_or_none()
  if not doc:
      raise HTTPException(status_code=404, detail="Document not found")
  ```
* Tuyệt đối không trả về `403 FORBIDDEN` khi người dùng đoán mò ID của người khác — luôn trả về `404 NOT_FOUND` để chống ID enumeration.

---

## 4. Truy Vấn Hybrid Search Bằng SQL RRF (Reciprocal Rank Fusion)
Kết hợp Vector Cosine Distance (`<->` với chỉ mục HNSW) và Full-Text Search (`to_tsvector('simple', content)` với chỉ mục GIN) trong cùng câu SQL:
```sql
WITH vector_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> :query_vector) AS rank_vec
    FROM document_chunks
    WHERE user_id = :user_id
    LIMIT 60
),
fts_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(content_tsv, plainto_tsquery('simple', :query_text)) DESC) AS rank_fts
    FROM document_chunks
    WHERE user_id = :user_id AND content_tsv @@ plainto_tsquery('simple', :query_text)
    LIMIT 60
)
SELECT COALESCE(v.id, f.id) AS chunk_id,
       (COALESCE(1.0 / (60 + v.rank_vec), 0.0) + COALESCE(1.0 / (60 + f.rank_fts), 0.0)) AS rrf_score
FROM vector_ranked v
FULL OUTER JOIN fts_ranked f ON v.id = f.id
ORDER BY rrf_score DESC
LIMIT 10;
```
