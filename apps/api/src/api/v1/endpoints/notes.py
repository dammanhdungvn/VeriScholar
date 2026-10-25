"""API Endpoints for Smart Research Notes & Knowledge Digest (Module 1)."""

import math
from uuid import UUID

import structlog
from api.db.models.user import UserModel
from api.deps import (
    get_current_user,
    get_note_service,
)
from api.schemas.envelope import (
    PaginatedResponseEnvelope,
    PaginationLinks,
    PaginationMeta,
    ResponseMeta,
    SingleResponseEnvelope,
)
from api.schemas.error import ErrorResponse
from api.schemas.note import (
    CreateNoteRequest,
    NoteListItemResponse,
    NoteResponse,
    UpdateNoteRequest,
)
from api.services.note_service import NoteService
from core.domain.exceptions import (
    ConcurrencyConflictError,
    EntityNotFoundError,
    InvalidNoteDataError,
    NoteNotFoundError,
    PreconditionRequiredError,
)
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import Response as RawResponse

logger = structlog.get_logger("api.endpoints.notes")

router = APIRouter(prefix="/notes", tags=["notes"])


def parse_version_from_etag(etag: str | None) -> int:
    """Parse integer version from If-Match HTTP ETag header (RFC 9110 / RFC 7232)."""
    if not etag:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "PRECONDITION_REQUIRED",
                "message": (
                    "Header 'If-Match' (ETag phiên bản, ví dụ '\"v1\"') là bắt buộc theo RFC 7232."
                ),
                "action": 'Include If-Match: "v{version}" header in request.',
            },
        )
    cleaned = etag.strip(' "W/w')
    if cleaned.startswith(("v", "V")):
        cleaned = cleaned[1:]
    try:
        ver = int(cleaned)
        if ver < 1:
            raise ValueError()
        return ver
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_IF_MATCH_HEADER",
                "message": f"Giá trị If-Match không hợp lệ: '{etag}'. Định dạng chuẩn: '\"v1\"'.",
                "action": "Provide valid If-Match version tag.",
            },
        )


CREATE_NOTE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Lưu trữ đoạn trích dẫn được chọn trực tiếp từ bài báo khoa học kèm ghi chú cá nhân của nhà
nghiên cứu.
Dùng khi người dùng hoặc AI Agent muốn đánh dấu luận điểm quan trọng để ghi nhớ hoặc phục vụ
tổng hợp bài học sau này.

📥 **Tham số đầu vào (Request Body application/json):**
- `selected_text` (string, Bắt buộc): Đoạn văn bản trích dẫn nguyên văn từ bài báo (tối
  thiểu 1 ký tự, tối đa 10,000 ký tự).
- `document_id` (UUID, Tùy chọn): ID của tài liệu nguồn gắn với trích dẫn. Nếu để trống, ghi
  chú lưu dưới dạng ý tưởng tự do (Free Note).
- `chunk_id` (UUID, Tùy chọn): ID của chunk chứa đoạn trích trong tài liệu.
- `page_number` (int, Mặc định: 1): Số trang chứa đoạn văn bản (>= 1).
- `bounding_boxes` (array[5-tuple], Tùy chọn): Danh sách toạ độ chuẩn hoá `[x0, y0, x1, y2,
  page]` (tỷ lệ 0.0 - 1.0) để PDF canvas highlight trực quan.
- `user_note` (string, Tùy chọn): Ghi chú, phân tích chuyên môn hoặc câu hỏi của người
  nghiên cứu.
- `tags` (list[str], Tùy chọn): Danh sách nhãn dán phân loại (tự động loại bỏ trùng lặp và
  chuẩn hóa chữ thường).
- `folder_id` (UUID, Tùy chọn): Thư mục sổ tay cá nhân lưu trữ ghi chú.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 201 Created`: Trả về `SingleResponseEnvelope[NoteResponse]` chứa dữ liệu ghi chú đã
  lưu.
- Headers phản hồi:
  - `Location: /api/v1/notes/{id}`: Đường dẫn tài nguyên vừa tạo.
  - `ETag: "v1"`: Khóa phiên bản khởi tạo phục vụ kiểm soát đồng thời lạc quan (OCC).

🧊 **Cơ chế Frozen Evidence Snapshot (Bảo toàn bằng chứng bất biến):**
Nếu có `document_id`, hệ thống tự động chụp lại và đóng băng vĩnh viễn metadata bài báo
(tiêu đề, tác giả, năm, DOI, chunk) vào trường `frozen_snapshot`. Khi bài báo gốc bị sửa đổi
hoặc xóa, trích dẫn học thuật vẫn được bảo toàn nguyên vẹn (`is_source_detached = True`).

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `400 INVALID_NOTE_DATA`: `selected_text` chỉ chứa khoảng trắng hoặc `page_number < 1`. ->
  **Hành động:** Kiểm tra và chuẩn hoá dữ liệu trước khi gửi.
- `404 DOCUMENT_NOT_FOUND`: `document_id` không tồn tại hoặc không thuộc quyền sở hữu của
  user. -> **Hành động:** Gọi `GET /api/v1/documents` lấy danh sách UUID hợp lệ.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Khi duyệt văn bản phát hiện luận điểm then chốt, hãy gọi API này để tạo ghi chú dẫn chứng.
Lưu lại `id` của ghi chú trả về để sử dụng cho endpoint tổng hợp bài học `POST
/api/v1/notes:synthesize`."""

LIST_NOTES_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Truy xuất danh sách ghi chú nghiên cứu trong sổ tay cá nhân phục vụ hiển thị Sidebar, xem
lại kiến thức, hoặc lọc các ghi chú cần thiết để gửi cho AI tổng hợp bài học.

📥 **Tham số đầu vào (Query Parameters):**
- `document_id` (UUID, Tùy chọn): Lọc các ghi chú thuộc về một bài báo khoa học cụ thể.
- `tag` (string, Tùy chọn): Lọc ghi chú theo thẻ học thuật (sử dụng chỉ mục PostgreSQL GIN).
- `folder_id` (UUID, Tùy chọn): Lọc ghi chú theo thư mục sổ tay.
- `page` (int, Mặc định: 1): Số thứ tự trang kết quả (1-indexed, tối thiểu 1).
- `per_page` (int, Mặc định: 50, Tối đa: 100): Số lượng ghi chú trả về trên mỗi trang.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `PaginatedResponseEnvelope[NoteListItemResponse]`.
  - `data`: Danh sách các ghi chú tóm tắt (`id`, `selected_text`, `user_note`, `tags`,
    `document_id`, `created_at`).
  - `meta`: `PaginationMeta` chứa `total`, `page`, `per_page`, `total_pages`.
  - `links`: `PaginationLinks` chuẩn RFC 8288 (`first`, `prev`, `self`, `next`, `last`).

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `422 VALIDATION_ERROR`: `page < 1` hoặc `per_page > 100`. -> **Hành động:** Điều chỉnh
  tham số trong giới hạn cho phép.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Để chuẩn bị tổng hợp tri thức cho người dùng, AI Agent có thể gọi endpoint này với tham số
`tag` hoặc `document_id` để thu thập danh sách các `id` ghi chú phù hợp."""

GET_NOTE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Lấy toàn bộ thông tin chi tiết của một ghi chú nghiên cứu, bao gồm nội dung trích dẫn, ghi
chú cá nhân, danh sách toạ độ Bounding Boxes, và toàn bộ ảnh chụp bằng chứng đóng băng
`frozen_snapshot`.

📥 **Tham số đầu vào (Path Parameter):**
- `id` (UUID, Bắt buộc): UUID định danh duy nhất của ghi chú nghiên cứu cần truy vấn.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SingleResponseEnvelope[NoteResponse]` chứa dữ liệu toàn vẹn của ghi chú.
- Header phản hồi:
  - `ETag: "v{version}"`: Mã phiên bản hiện tại của ghi chú (ví dụ: `"v1"`, `"v2"`).

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `404 NOTE_NOT_FOUND`: Ghi chú không tồn tại hoặc không thuộc quyền sở hữu của user. ->
  **Hành động:** Gọi `GET /api/v1/notes` để xác minh lại danh sách ghi chú hiện có.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Nếu bạn có ý định cập nhật ghi chú này qua `PATCH /api/v1/notes/{id}`, bạn BẮT BUỘC phải
trích xuất và lưu giữ giá trị của header `ETag` từ endpoint này để truyền vào header
`If-Match`."""

UPDATE_NOTE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Chỉnh sửa nhận xét cá nhân (`user_note`), danh sách thẻ (`tags`), hoặc di chuyển ghi chú
sang thư mục khác (`folder_id`) với cơ chế kiểm soát đồng thời lạc quan (OCC).

📥 **Tham số đầu vào:**
- `id` (UUID, Path, Bắt buộc): UUID của ghi chú cần chỉnh sửa.
- `If-Match` (string, Header, Bắt buộc): Chuỗi ETag phiên bản hiện tại (theo RFC 7232, ví
  dụ: `"v1"` hoặc `"v3"`).
- Request Body (`application/json`):
  - `user_note` (string, Tùy chọn): Nội dung nhận xét, phân tích mới.
  - `tags` (list[str], Tùy chọn): Danh sách nhãn dán mới (thay thế toàn bộ danh sách cũ).
  - `folder_id` (UUID, Tùy chọn): ID thư mục mới.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SingleResponseEnvelope[NoteResponse]` với dữ liệu đã cập nhật.
- Header phản hồi:
  - `ETag: "v{version+1}"`: Khóa phiên bản mới sau khi cập nhật thành công (ví dụ: `"v2"`).

🔄 **Cơ chế Kiểm soát Đồng thời (Optimistic Concurrency Control - OCC):**
- Hệ thống bảo vệ dữ liệu chống ghi đè race condition khi nhiều tab hoặc client cùng chỉnh
  sửa.
- Nếu thiếu header `If-Match`: Trả về lỗi `428 Precondition Required`.
- Nếu giá trị `If-Match` không khớp với phiên bản trong cơ sở dữ liệu: Trả về lỗi `412
  Precondition Failed` (`CONCURRENCY_CONFLICT`).

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `412 CONCURRENCY_CONFLICT`: Ghi chú đã bị sửa đổi bởi một yêu cầu khác trước đó. -> **Hành
  động cho AI Agent:** Gọi ngay `GET /api/v1/notes/{id}` để đọc ETag và dữ liệu mới nhất,
  hòa trộn thay đổi rồi gửi lại request với ETag mới.
- `428 PRECONDITION_REQUIRED`: Thiếu header `If-Match`. -> **Hành động cho AI Agent:** Luôn
  bổ sung header `If-Match: "v{version}"` lấy từ phản hồi GET/POST trước đó.
- `404 NOTE_NOT_FOUND`: Ghi chú không tồn tại.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Tuyệt đối không bỏ qua header `If-Match`. Quy trình chuẩn: `GET /api/v1/notes/{id}` -> Lấy
ETag -> `PATCH /api/v1/notes/{id}` với header `If-Match`."""

DELETE_NOTE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Xóa vĩnh viễn một ghi chú nghiên cứu khỏi sổ tay cá nhân của người dùng (Idempotent 204 No
Content).

📥 **Tham số đầu vào (Path Parameter):**
- `id` (UUID, Bắt buộc): UUID của ghi chú nghiên cứu cần xóa.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 204 No Content`: Xóa thành công, không có body trả về.

🛡️ **Bảo vệ toàn vẹn tài liệu gốc:**
Thao tác xóa ghi chú hoàn toàn KHÔNG làm xóa hay thay đổi bài báo khoa học gốc, các chunk
văn bản hay các ghi chú khác.

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `404 NOTE_NOT_FOUND`: Ghi chú không tồn tại hoặc đã bị xóa trước đó.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Thao tác xóa là vĩnh viễn (hard delete). AI Agent chỉ nên gọi endpoint này khi người dùng
yêu cầu rõ ràng."""


# ==============================================================================
# 16. POST /api/v1/notes (Lưu trích dẫn & ghi chú cá nhân)
# ==============================================================================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleResponseEnvelope[NoteResponse],
    summary="# 16. Lưu trích dẫn & ghi chú cá nhân (Add to Note)",
    description=CREATE_NOTE_DESCRIPTION,
    responses={
        201: {
            "description": "Ghi chú đã được lưu thành công kèm Frozen Evidence Snapshot.",
            "headers": {
                "Location": {
                    "description": "Đường dẫn URI đến ghi chú vừa tạo.",
                    "schema": {"type": "string"},
                },
                "ETag": {
                    "description": "Khóa OCC version khởi tạo ('\"v1\"').",
                    "schema": {"type": "string"},
                },
            },
        },
        400: {"model": ErrorResponse, "description": "Dữ liệu ghi chú không hợp lệ."},
        404: {"model": ErrorResponse, "description": "Tài liệu đính kèm không tồn tại."},
    },
)
async def create_note(
    payload: CreateNoteRequest,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> SingleResponseEnvelope[NoteResponse]:
    """Save academic quote with bounding boxes, personal memo and frozen evidence snapshot."""
    try:
        note_data = await note_service.create_note(user_id=current_user.id, req=payload)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DOCUMENT_NOT_FOUND",
                "message": str(e),
                "action": "Check document_id and try again.",
            },
        )
    except InvalidNoteDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_NOTE_DATA",
                "message": str(e),
                "action": "Provide valid non-empty selected text and positive page number.",
            },
        )

    response.headers["Location"] = f"/api/v1/notes/{note_data.id}"
    response.headers["ETag"] = f'"v{note_data.version}"'
    return SingleResponseEnvelope(data=note_data, meta=ResponseMeta())


# ==============================================================================
# 17. GET /api/v1/notes (Danh sách ghi chú có bộ lọc và phân trang)
# ==============================================================================
@router.get(
    "",
    response_model=PaginatedResponseEnvelope[NoteListItemResponse],
    summary="# 17. Danh sách ghi chú (lọc theo document_id, tag, folder_id)",
    description=LIST_NOTES_DESCRIPTION,
    responses={
        200: {"description": "Danh sách ghi chú kèm phân trang RFC 8288."},
    },
)
async def list_notes(
    request: Request,
    document_id: UUID | None = Query(None, description="Lọc theo ID tài liệu"),
    tag: str | None = Query(None, description="Lọc theo thẻ học thuật"),
    folder_id: UUID | None = Query(None, description="Lọc theo ID thư mục chứa tài liệu"),
    page: int = Query(1, ge=1, description="Số trang (1-indexed)"),
    per_page: int = Query(50, ge=1, le=100, description="Số mục trên mỗi trang"),
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> PaginatedResponseEnvelope[NoteListItemResponse]:
    """Retrieve user research notes collection filtered by document, tag, or folder."""
    items, total = await note_service.list_notes(
        user_id=current_user.id,
        document_id=document_id,
        tag=tag,
        folder_id=folder_id,
        page=page,
        per_page=per_page,
    )

    total_pages = max(1, math.ceil(total / per_page)) if total > 0 else 1
    base_url = str(request.url.remove_query_params(["page", "per_page"]))
    sep = "&" if "?" in base_url else "?"

    links = PaginationLinks(
        first=f"{base_url}{sep}page=1&per_page={per_page}",
        prev=(f"{base_url}{sep}page={page - 1}&per_page={per_page}" if page > 1 else None),
        self=f"{base_url}{sep}page={page}&per_page={per_page}",
        next=(
            f"{base_url}{sep}page={page + 1}&per_page={per_page}" if page < total_pages else None
        ),
        last=f"{base_url}{sep}page={total_pages}&per_page={per_page}",
    )

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )

    return PaginatedResponseEnvelope(data=items, meta=meta, links=links)


# ==============================================================================
# 18. GET /api/v1/notes/{id} (Chi tiết ghi chú kèm Frozen Evidence Snapshot)
# ==============================================================================
@router.get(
    "/{id}",
    response_model=SingleResponseEnvelope[NoteResponse],
    summary="# 18. Chi tiết ghi chú kèm Frozen Evidence Snapshot",
    description=GET_NOTE_DESCRIPTION,
    responses={
        200: {
            "description": "Chi tiết toàn vẹn của ghi chú kèm Frozen Evidence Snapshot.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version hiện tại (ví dụ: '\"v1\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        404: {"model": ErrorResponse, "description": "Ghi chú không tồn tại."},
    },
)
async def get_note(
    id: UUID,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> SingleResponseEnvelope[NoteResponse]:
    """Retrieve full details of a note including immutable evidence snapshot."""
    try:
        data = await note_service.get_note_by_id(note_id=id, user_id=current_user.id)
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOTE_NOT_FOUND",
                "message": str(e),
                "action": "Verify note ID.",
            },
        )

    response.headers["ETag"] = f'"v{data.version}"'
    return SingleResponseEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 19. PATCH /api/v1/notes/{id} (Sửa ghi chú / tag có kiểm soát OCC If-Match)
# ==============================================================================
@router.patch(
    "/{id}",
    response_model=SingleResponseEnvelope[NoteResponse],
    summary="# 19. Sửa ghi chú / tag (Kiểm soát đồng thời OCC If-Match)",
    description=UPDATE_NOTE_DESCRIPTION,
    responses={
        200: {
            "description": "Cập nhật ghi chú thành công.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version mới sau cập nhật (ví dụ: '\"v2\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        400: {"model": ErrorResponse, "description": "Dữ liệu không hợp lệ."},
        404: {"model": ErrorResponse, "description": "Ghi chú không tồn tại."},
        412: {
            "model": ErrorResponse,
            "description": "Xung đột phiên bản đồng thời (CONCURRENCY_CONFLICT).",
        },
        428: {
            "model": ErrorResponse,
            "description": "Thiếu header If-Match bắt buộc.",
        },
    },
)
async def update_note(
    id: UUID,
    payload: UpdateNoteRequest,
    response: Response,
    if_match: str | None = Header(
        None,
        alias="If-Match",
        description="Phiên bản ETag hiện tại bắt buộc (ví dụ: '\"v1\"')",
    ),
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> SingleResponseEnvelope[NoteResponse]:
    """Update personal memo or tags using Optimistic Concurrency Control."""
    try:
        data = await note_service.update_note(
            note_id=id,
            user_id=current_user.id,
            req=payload,
            if_match_header=if_match,
        )
    except PreconditionRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "PRECONDITION_REQUIRED",
                "message": str(e),
                "action": 'Include If-Match: "v{version}" header.',
            },
        )
    except ConcurrencyConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "code": "CONCURRENCY_CONFLICT",
                "message": str(e),
                "action": "Fetch latest note state and retry with updated ETag.",
            },
        )
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOTE_NOT_FOUND",
                "message": str(e),
                "action": "Verify note ID.",
            },
        )

    response.headers["ETag"] = f'"v{data.version}"'
    return SingleResponseEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 20. DELETE /api/v1/notes/{id} (Xóa ghi chú khỏi sổ tay)
# ==============================================================================
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="# 20. Xóa ghi chú khỏi sổ tay",
    description=DELETE_NOTE_DESCRIPTION,
    responses={
        204: {"description": "Ghi chú đã được xóa thành công khỏi sổ tay (Idempotent)."},
    },
)
async def delete_note(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> RawResponse:
    """Delete note idempotently without altering the source academic document."""
    await note_service.delete_note(note_id=id, user_id=current_user.id)
    return RawResponse(status_code=status.HTTP_204_NO_CONTENT)
