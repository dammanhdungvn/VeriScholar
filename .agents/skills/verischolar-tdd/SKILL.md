---
name: verischolar-tdd
description: Cẩm nang thực hành Kiểm thử Hướng Phát triển (TDD), transaction rollback fixture và deterministic mocks cho VeriScholar.
---

# VeriScholar TDD & Testing Protocols

Tài liệu này là cẩm nang bắt buộc khi viết unit, integration và domain tests trong monorepo VeriScholar.

---

## 1. Chu Kỳ TDD Bắt Buộc (Red-Green-Refactor)
1. **RED:** Viết một test case ngắn gọn chứng minh hành vi mong đợi. Chạy test và xác nhận test **FAIL** đúng lý do (ví dụ: hàm chưa tồn tại, hoặc assertion sai kết quả).
2. **GREEN:** Viết lượng code sản xuất tối thiểu để bài test **PASS** (tất cả các test trong test suite đều xanh).
3. **REFACTOR:** Dọn dẹp mã nguồn, tối ưu hóa cấu trúc mà vẫn giữ toàn bộ test suite màu xanh.

---

## 2. Fixture Cơ Sở Dữ Liệu Tự Động Rollback
Mọi test case tương tác với PostgreSQL đều chạy trong một transaction lồng nhau và tự động rollback khi hoàn thành test để bảo toàn trạng thái CSDL:
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def db_session(engine) -> AsyncSession:
    connection = await engine.connect()
    trans = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await session.close()
    await trans.rollback()
    await connection.close()
```

---

## 3. Mocks Xác Định Không Phụ Thuộc Mạng (Deterministic Mocks)
* **Mock OpenAI Embeddings & Completions:**
  ```python
  from unittest.mock import AsyncMock, patch

  @pytest.fixture
  def mock_openai():
      with patch("api.services.llm.AsyncOpenAI") as mock:
          client = mock.return_value
          client.embeddings.create = AsyncMock(return_value=MockEmbeddingResponse([0.0] * 1536))
          client.chat.completions.create = AsyncMock(return_value=MockChatResponse("Phân tích học thuật mẫu"))
          yield client
  ```
* **Mock E2B Compiler Sandbox:**
  ```python
  @pytest.fixture
  def mock_e2b_sandbox():
      with patch("api.services.latex.E2BCompilerService.compile") as mock_compile:
          mock_compile.return_value = LatexCompilationResult(
              success=True,
              pdf_bytes=b"%PDF-1.4 sample",
              compile_log="Output written on document.pdf",
              duration_ms=120,
          )
          yield mock_compile
  ```

---

## 4. Kiểm Thử Cô Lập Đa Người Dùng (Multi-Tenant Isolation Test)
Mỗi API endpoint có tương tác dữ liệu cá nhân phải có test case kiểm thử ranh giới người dùng:
```python
async def test_user_cannot_access_other_users_document(client, user_a_token, user_b_document):
    response = await client.get(
        f"/api/v1/documents/{user_b_document.id}",
        headers={"Authorization": f"Bearer {user_a_token}"},
    )
    # Khẳng định trả về 404 NOT_FOUND, không phải 403 FORBIDDEN
    assert response.status_code == 404
```
