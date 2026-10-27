"""API Endpoints for Research Sessions (Module 1: Dual-Pane Research Workspace)."""

from uuid import UUID, uuid4

import structlog
from api.db.models.user import UserModel
from api.deps import (
    get_academic_resolver,
    get_current_user,
    get_idempotency_port,
    get_session_chat_service,
    get_session_service,
)
from api.schemas.envelope import PaginationLinks, PaginationMeta, ResponseMeta
from api.schemas.error import ErrorResponse
from api.schemas.session import (
    SessionAddDocumentRequest,
    SessionChatMessageRequest,
    SessionCreateRequest,
    SessionHistoryEnvelope,
    SessionIngestReferencesEnvelope,
    SessionIngestReferencesRequest,
    SessionSingleEnvelope,
    SessionTurnListEnvelope,
    SessionUpdateMetadataRequest,
    SessionUpdateViewportRequest,
)
from api.services.session_chat_service import SessionChatService
from api.services.session_service import SessionService
from core.ports.academic_resolver import IAcademicSearchResolverPort
from core.ports.idempotency import IIdempotencyPort
from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse, StreamingResponse

logger = structlog.get_logger("api.endpoints.sessions")

router = APIRouter(prefix="/sessions", tags=["sessions"])


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


SESSION_CREATE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Khởi tạo phiên nghiên cứu đa bài báo mới (Multi-paper Research Workspace).
Cho phép người dùng hoặc AI Agent tạo không gian làm việc chứa từ 0 đến tối đa 5 bài báo
khoa học để phân tích, tổng hợp và hỏi đáp đối chiếu chéo.

📥 **Tham số đầu vào:**
- `Idempotency-Key` (string, Header, Tùy chọn): Khóa định danh chống gửi trùng lặp request
  (cửa sổ lưu cache kết quả 24 giờ).
- `include_documents` (boolean, Query, Mặc định: False): Tùy chọn nhúng danh sách metadata
  chi tiết của các bài báo trong phản hồi.
- Request Body (`application/json`):
  - `title` (string, Tùy chọn): Tiêu đề của phiên. Nếu để trống, hệ thống tự động đặt tên
    theo bài báo đầu tiên hoặc thời gian hiện tại.
  - `initial_document_ids` (list[UUID], Tùy chọn, Mặc định: `[]`): Danh sách bài báo ban đầu
    nạp vào phiên (tối đa 5 bài).

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 201 Created`: `SessionSingleEnvelope` chứa thông tin phiên nghiên cứu, danh sách
  `document_ids`, `viewport_state` mặc định, và `version: 1`.
- `HTTP 200 OK (Idempotent Hit)`: Trả về kết quả phiên đã tạo trước đó kèm header `X-Cache:
  Idempotent-Hit`.
- Headers phản hồi:
  - `Location: /api/v1/sessions/{id}`: Đường dẫn URI đến phiên vừa tạo.
  - `ETag: "v1"`: Khóa phiên bản khởi tạo.

🛡️ **Ràng buộc nghiệp vụ & Dung lượng trần:**
- Tối đa 5 bài báo trong một phiên nghiên cứu (`400 SESSION_CAPACITY_EXCEEDED`).
- Tất cả tài liệu trong `initial_document_ids` phải thuộc quyền sở hữu của người dùng hiện
  tại (`404 DOCUMENT_NOT_FOUND`).

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `400 SESSION_CAPACITY_EXCEEDED`: Vượt quá 5 bài báo. -> **Hành động:** Giảm số lượng tài
  liệu xuống <= 5.
- `404 DOCUMENT_NOT_FOUND`: Một hoặc nhiều tài liệu không tồn tại. -> **Hành động:** Kiểm
  tra danh sách UUID tài liệu.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Khi bắt đầu hỗ trợ người dùng phân tích một chủ đề mới, hãy gọi API này để lấy `id` của
phiên làm việc. Sử dụng `id` này cho toàn bộ các thao tác hỏi đáp, nạp tài liệu và lưu ghi
chú tiếp theo."""

SESSION_LIST_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Lấy danh sách lịch sử các phiên nghiên cứu của người dùng hiện tại phục vụ hiển thị thanh
Sidebar hoặc danh mục tìm kiếm.

📥 **Tham số đầu vào (Query Parameters):**
- `page` (int, Mặc định: 1): Số thứ tự trang (1-indexed, tối thiểu 1).
- `per_page` (int, Mặc định: 20, Tối đa: 100): Số lượng phiên trả về trên mỗi trang.
- `include_archived` (boolean, Mặc định: False): Khi `True`, bao gồm cả các phiên đã bị lưu
  trữ do quá hạn TTL 7 ngày.
- `q` (string, Tùy chọn): Từ khóa tìm kiếm mờ không phân biệt hoa thường theo tiêu đề phiên.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SessionHistoryEnvelope` gồm danh sách tóm tắt phiên (`id`, `title`,
  `document_count`, `message_count`, `is_archived`, `updated_at`).
- Sắp xếp mặc định: `updated_at DESC` (phiên tương tác gần nhất lên đầu).
- Hỗ trợ đầy đủ `meta` phân trang và `links` RFC 8288.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Dùng endpoint này để tìm kiếm phiên làm việc cũ liên quan đến chủ đề người dùng đang hỏi
trước khi quyết định tạo phiên mới."""

SESSION_DETAIL_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Khôi phục nguyên vẹn trạng thái phiên nghiên cứu khi người dùng quay lại từ Sidebar hoặc
reload trình duyệt.

📥 **Tham số đầu vào (Path Parameter):**
- `id` (UUID, Bắt buộc): UUID định danh duy nhất của phiên nghiên cứu cần khôi phục.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SessionSingleEnvelope` khôi phục toàn vẹn:
  - `document_ids`: Danh sách ID các bài báo trong phiên.
  - `active_document_id`: Bài báo đang hiển thị trên canvas.
  - `viewport_state`: Tọa độ cuộn (`scroll_top`), số trang (`page`), tỷ lệ phóng to
    (`zoom_ratio`).
  - `active_tab`: Tab chức năng đang mở (`chat`, `notes`, `highlights`).
  - `version`: Số phiên bản hiện tại.
- Header phản hồi:
  - `ETag: "v{version}"`: Khóa phiên bản phục vụ kiểm soát đồng thời.

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `404 SESSION_NOT_FOUND`: Phiên không tồn tại hoặc không thuộc quyền sở hữu của user.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Bắt buộc gọi endpoint này để khôi phục ngữ cảnh làm việc và lưu lại giá trị header `ETag`
trước khi thực hiện các thao tác cập nhật hoặc hỏi đáp."""

SESSION_UPDATE_METADATA_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Đổi tên tiêu đề hoặc cập nhật metadata phiên nghiên cứu với cơ chế kiểm soát đồng thời lạc
quan (OCC).

📥 **Tham số đầu vào:**
- `id` (UUID, Path, Bắt buộc): UUID của phiên nghiên cứu.
- `If-Match` (string, Header, Bắt buộc): Chuỗi ETag phiên bản hiện tại (ví dụ: `"v1"` hoặc
  `"v3"`).
- Request Body (`application/json`):
  - `title` (string, Bắt buộc): Tiêu đề mới của phiên (1 đến 255 ký tự, không được chỉ chứa
    khoảng trắng).

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SessionSingleEnvelope` với tiêu đề đã cập nhật.
- Header phản hồi:
  - `ETag: "v{version+1}"`: Khóa phiên bản mới sau khi cập nhật thành công.

🔄 **Cơ chế Kiểm soát Đồng thời (Optimistic Concurrency Control - OCC):**
- Ngăn chặn ghi đè tiêu đề khi người dùng mở nhiều tab hoặc thiết bị.
- Nếu thiếu header `If-Match`: Trả về `428 Precondition Required`.
- Nếu `If-Match` không khớp CSDL: Trả về `412 Precondition Failed` (`CONCURRENCY_CONFLICT`).

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `412 CONCURRENCY_CONFLICT`: Phiên đã bị cập nhật bởi tiến trình khác. -> **Hành động cho
  AI Agent:** Gọi `GET /api/v1/sessions/{id}` lấy ETag mới nhất rồi retry.
- `428 PRECONDITION_REQUIRED`: Thiếu header `If-Match`. -> **Hành động cho AI Agent:** Bổ
  sung header `If-Match: "v{version}"`.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Khi người dùng yêu cầu đổi tên phiên làm việc, hãy đọc ETag từ lần truy vấn chi tiết gần
nhất và truyền vào header `If-Match`."""

SESSION_UPDATE_VIEWPORT_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Tự động lưu trạng thái hiển thị canvas đọc PDF của người dùng bao gồm vị trí cuộn trang
(`scroll_top`), số trang (`page`), tỷ lệ zoom (`zoom_ratio`), tab đang chọn (`active_tab`)
và bài báo đang mở (`active_document_id`).

📥 **Tham số đầu vào:**
- `id` (UUID, Path, Bắt buộc): UUID của phiên nghiên cứu.
- `If-Match` (string, Header, Bắt buộc): Chuỗi ETag phiên bản hiện tại (ví dụ: `"v1"`).
- Request Body (`application/json`):
  - `viewport_state` (object, Bắt buộc): `{ "page": int >= 1, "zoom_ratio": float (0.25 -
    5.0), "scroll_top": float >= 0 }`.
  - `active_tab` (string, Tùy chọn): Tab đang mở (`chat`, `notes`, `highlights`, `mindmap`).
  - `active_document_id` (UUID, Tùy chọn): UUID bài báo đang xem trên canvas (phải thuộc
    phiên).

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SessionSingleEnvelope` với trạng thái viewport mới.
- Header phản hồi: `ETag: "v{version+1}"`.

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `412 CONCURRENCY_CONFLICT`: Xung đột phiên bản đồng thời.
- `422 UNPROCESSABLE_ENTITY`: `active_document_id` không nằm trong danh sách bài báo của
  phiên.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Dùng để đồng bộ trải nghiệm xem tài liệu, ví dụ khi giải thích một biểu đồ ở trang 5, AI
Agent có thể cập nhật `viewport_state` đưa người dùng trực tiếp đến trang 5."""

SESSION_DELETE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Xóa vĩnh viễn một phiên nghiên cứu và xóa xếp chồng (cascade) toàn bộ lịch sử trò chuyện và
liên kết tài liệu trong phiên đó.

📥 **Tham số đầu vào (Path Parameter):**
- `id` (UUID, Bắt buộc): UUID của phiên nghiên cứu cần xóa.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 204 No Content`: Xóa thành công, không có body trả về.

🛡️ **Bảo vệ toàn vẹn tài liệu gốc:**
Việc xóa phiên nghiên cứu tuyệt đối KHÔNG xóa các tệp PDF và dữ liệu bài báo gốc trong thư
viện chung của người dùng.

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `404 SESSION_NOT_FOUND`: Phiên không tồn tại hoặc đã bị xóa trước đó.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Thao tác này là vĩnh viễn và không thể hoàn tác. Chỉ thực hiện khi người dùng xác nhận yêu
cầu xóa phiên."""

SESSION_ADD_DOCUMENT_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Nạp thêm bài báo khoa học vào phiên nghiên cứu đang hoạt động bằng định dạng Pure JSON
(không dùng multipart form).

📥 **Tham số đầu vào:**
- `id` (UUID, Path, Bắt buộc): UUID của phiên nghiên cứu.
- Request Body (`application/json`):
  - `source_type` (string, Bắt buộc): Nguồn nạp bài báo: `"document_id"` (có sẵn trong thư
    viện) hoặc `"url"` (đường dẫn arXiv, PubMed, DOI).
  - `document_id` (UUID, Tùy chọn): Bắt buộc khi `source_type == "document_id"`.
  - `url` (string, Tùy chọn): Bắt buộc khi `source_type == "url"`.
  - `title` (string, Tùy chọn): Tiêu đề gợi nhớ tùy chọn khi nạp bài qua URL.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 202 Accepted`: Trả về trạng thái xử lý:
  - `status: "associated"` nếu nạp tài liệu có sẵn từ thư viện.
  - `status: "queued"` nếu đưa URL vào hàng đợi xử lý tải và bóc tách nền.

🛡️ **Kiểm soát dung lượng trần & Trùng lặp:**
- Mỗi phiên chỉ chứa tối đa 5 bài báo (`422 SESSION_CAPACITY_EXCEEDED`).
- Trả về lỗi `409 Conflict` nếu bài báo đã tồn tại trong phiên
  (`DOCUMENT_ALREADY_IN_SESSION`).

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Khi người dùng muốn mở rộng phạm vi nghiên cứu bằng một bài báo mới (cung cấp link hoặc ID),
hãy gọi endpoint này để bổ sung tài liệu vào phiên làm việc."""

SESSION_POST_MESSAGE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Gửi câu hỏi nghiên cứu đa bài báo và nhận luồng dữ liệu trả lời trực tiếp thời gian thực
theo định dạng Server-Sent Events (`text/event-stream`).

📥 **Tham số đầu vào & Headers:**
- Headers:
  - `Last-Event-ID` (string, Tùy chọn): ID của sự kiện SSE nhận được cuối cùng để hỗ trợ nối
    lại luồng stream khi kết nối mạng bị gián đoạn (RFC 8895 Stream Resumption).
- `id` (UUID, Path, Bắt buộc): UUID của phiên nghiên cứu.
- Request Body (`application/json`):
  - `question` (string, Bắt buộc): Câu hỏi nghiên cứu (1 đến 2,000 ký tự).
  - `stream` (boolean, Mặc định: True): Yêu cầu luồng dữ liệu SSE thời gian thực.
  - `scope` (string, Mặc định: `"multi_paper"`): Phạm vi truy vấn: `"multi_paper"` (toàn bộ
    các bài trong phiên) hoặc `"active_paper"` (chỉ bài báo đang mở).
  - `interactive_response` (dict, Tùy chọn): Dữ liệu phản hồi tùy chọn khi người dùng tương tác
    với thẻ chẩn đoán (`persona_id`, `quiz_answers`, `action_id`) từ AT-CoT Options.

📤 **Đầu ra & Cấu trúc Luồng Sự kiện SSE chuẩn SOTA (`text/event-stream`):**
Mọi sự kiện SSE được định danh tuần tự bằng `id: <seq_id>`:
1. `event: start`: Bắt đầu sinh câu trả lời, trả về `turn_id` và `message_id`.
   `data: {"turn_id": "...", "message_id": "..."}`
2. `event: reasoning`: (Chuẩn CoT Thinking Stream) Quá trình suy luận phản biện logic học thuật
   của mô hình trước khi xuất tokens câu trả lời, cho phép UI hiển thị collapsible thought box.
   `data: {"thought": "..."}`
3. `event: interactive_options`: (Tùy chọn) Phát sinh khi hệ thống phát hiện ý định mơ hồ
   hoặc cần chẩn đoán lộ trình học (AT-CoT Intent Elicitation). Trả về cấu trúc JSON chứa
   Personas và Micro-Quiz để Frontend render thẻ 1-click thay vì yêu cầu người dùng gõ phím.
   `data: {"type": "diagnostic_quiz", "personas": [...], "quiz": [...]}`
4. `event: citations`: Danh sách trích dẫn đối chiếu chéo kèm tên bài báo, số trang và toạ
   độ Bounding Box `[x0, y0, x1, y2, page]`.
   `data: {"citations": [...]}`
5. `event: token`: Từng token văn bản câu trả lời được stream trực tiếp.
   `data: {"token": "..."}`
6. `event: done`: Hoàn tất câu trả lời kèm thống kê token usage, latency, intent, và ambiguity_type.
   `data: {"finish_reason": "completed", "intent": "...", "ambiguity_type": "..."}`
7. `event: error`: Báo lỗi chi tiết nếu pipeline xử lý gặp sự cố.

⚡ **Tối ưu hóa & Client Disconnect Guard:**
Hệ thống liên tục kiểm tra `request.is_disconnected` để lập tức hủy tác vụ LLM phía server
khi client đóng kết nối, giúp tiết kiệm tài nguyên tính toán.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Khi người dùng đặt câu hỏi so sánh hoặc đối chiếu, hãy sử dụng `scope: "multi_paper"`. Lắng
nghe sự kiện `citations` để hiển thị căn cứ nguồn cho câu trả lời."""

SESSION_GET_MESSAGES_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Lấy lịch sử các lượt hội thoại (Session turns) của phiên nghiên cứu có phân trang, bao gồm
toàn bộ câu hỏi, câu trả lời, và danh sách trích dẫn dẫn chứng đã lưu.

📥 **Tham số đầu vào (Query Parameters):**
- `id` (UUID, Path, Bắt buộc): UUID của phiên nghiên cứu.
- `page` (int, Mặc định: 1): Số thứ tự trang (1-indexed).
- `per_page` (int, Mặc định: 50, Tối đa: 100): Số lượt hỏi đáp trên mỗi trang.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SessionTurnListEnvelope` chứa danh sách các lượt hỏi đáp theo thứ tự thời
  gian tăng dần kèm đầy đủ trích dẫn và toạ độ Bounding Boxes.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Gọi endpoint này để nạp lại toàn bộ ngữ cảnh hội thoại trước đó khi tiếp tục phiên làm việc
với người dùng."""

SESSION_DELETE_MESSAGES_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Xóa toàn bộ lịch sử hỏi đáp trong một phiên nghiên cứu (Idempotent 204 No Content) mà không
làm mất phiên hoặc danh sách các bài báo đã nạp.

📥 **Tham số đầu vào (Path Parameter):**
- `id` (UUID, Bắt buộc): UUID của phiên nghiên cứu cần xóa lịch sử chat.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 204 No Content`: Lịch sử hội thoại đã được dọn sạch thành công.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Dùng khi người dùng muốn bắt đầu một chủ đề thảo luận hoàn toàn mới trong cùng một tập hợp
bài báo mà không bị nhiễu bởi các câu hỏi trước."""

SESSION_RESTORE_ARCHIVED_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Tải lại tệp PDF gốc để kích hoạt lại phiên nghiên cứu đã bị chuyển vào trạng thái lưu trữ
lạnh (Cold Storage) do quá hạn TTL (7 ngày không hoạt động).

📥 **Tham số đầu vào (multipart/form-data):**
- `id` (UUID, Path, Bắt buộc): UUID của phiên nghiên cứu đã bị lưu trữ (`is_archived ==
  True`).
- `file` (UploadFile, Bắt buộc): Tệp PDF gốc hợp lệ (kiểm tra magic bytes `%PDF-`).

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SessionSingleEnvelope` với trạng thái `is_archived: False` và khóa `ETag`
  mới.

⚠️ **Mã lỗi thường gặp & Hướng xử lý cho AI/Client:**
- `400 INVALID_PDF_HEADER`: Tệp tải lên không phải là định dạng PDF hợp lệ.
- `404 SESSION_NOT_FOUND`: Phiên không tồn tại hoặc không thuộc quyền sở hữu của user.

🤖 **Chỉ dẫn tự động hóa cho AI Agent:**
Khi phát hiện phiên có cờ `is_archived == True`, AI Agent cần hướng dẫn người dùng cung cấp
lại tệp PDF gốc để gọi API này tái kích hoạt phiên."""


# ==============================================================================
# 45. POST /api/v1/sessions (Khởi tạo phiên nghiên cứu mới)
# ==============================================================================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SessionSingleEnvelope,
    summary="# 45. Khởi tạo phiên nghiên cứu đa bài mới (Research Session)",
    description=SESSION_CREATE_DESCRIPTION,
    responses={
        201: {"description": "Phiên nghiên cứu đã được khởi tạo thành công."},
        200: {"description": "Phiên nghiên cứu đã được tạo trước đó (Idempotent Cache Hit)."},
        400: {"model": ErrorResponse, "description": "Vượt quá dung lượng 5 bài báo."},
        404: {"model": ErrorResponse, "description": "Tài liệu không tồn tại."},
        422: {"model": ErrorResponse, "description": "Dữ liệu không hợp lệ."},
    },
)
async def create_session(
    payload: SessionCreateRequest,
    response: Response,
    include_documents: bool = Query(
        False, description="Nhúng danh sách metadata chi tiết của các bài báo"
    ),
    idempotency_key: str | None = Header(
        None,
        alias="Idempotency-Key",
        description="Khóa định danh chống trùng lặp request (24h)",
    ),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    idempotency: IIdempotencyPort = Depends(get_idempotency_port),
) -> SessionSingleEnvelope | JSONResponse:
    """Create a new multi-paper research session with idempotency and auto-naming support."""
    if idempotency_key:
        cache_key = f"idempotency:session_create:{current_user.id}:{idempotency_key}"
        cached_resp = await idempotency.get_response(cache_key)
        if cached_resp:
            session_id = cached_resp.get("data", {}).get("id")
            version = cached_resp.get("data", {}).get("version", 1)
            response.headers["X-Cache"] = "Idempotent-Hit"
            response.headers["Location"] = f"/api/v1/sessions/{session_id}"
            response.headers["ETag"] = f'"v{version}"'
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=cached_resp,
                headers=dict(response.headers),
            )

    data = await session_service.create_session(
        user_id=current_user.id,
        title=payload.title,
        initial_document_ids=payload.initial_document_ids,
        include_documents=include_documents,
    )

    response.headers["Location"] = f"/api/v1/sessions/{data.id}"
    response.headers["ETag"] = f'"v{data.version}"'

    envelope = SessionSingleEnvelope(data=data, meta=ResponseMeta())

    if idempotency_key:
        cache_key = f"idempotency:session_create:{current_user.id}:{idempotency_key}"
        await idempotency.store_response(
            key=cache_key,
            response_data=envelope.model_dump(mode="json"),
            status_code=status.HTTP_201_CREATED,
        )

    return envelope


# ==============================================================================
# 46. GET /api/v1/sessions (Lấy lịch sử các phiên nghiên cứu - Sidebar History)
# ==============================================================================
@router.get(
    "",
    response_model=SessionHistoryEnvelope,
    summary="# 46. Lấy lịch sử các phiên nghiên cứu (Sidebar History)",
    description=SESSION_LIST_DESCRIPTION,
    responses={
        200: {"description": "Danh sách lịch sử các phiên nghiên cứu phân trang thành công."}
    },
)
async def list_sessions(
    page: int = Query(1, ge=1, description="Chỉ số trang (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Số lượng mục trên mỗi trang"),
    include_archived: bool = Query(
        False, description="Bao gồm cả các phiên đã lưu trữ quá hạn TTL"
    ),
    q: str | None = Query(None, description="Từ khóa tìm kiếm theo tiêu đề phiên"),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionHistoryEnvelope:
    """List research sessions for current user sidebar history."""
    items, total = await session_service.list_sessions(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        include_archived=include_archived,
        query=q,
    )
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    base_url = f"/api/v1/sessions?page={page}&per_page={per_page}"
    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
    links = PaginationLinks(
        first=f"/api/v1/sessions?page=1&per_page={per_page}",
        prev=f"/api/v1/sessions?page={page - 1}&per_page={per_page}" if page > 1 else None,
        self=base_url,
        next=f"/api/v1/sessions?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None,
        last=f"/api/v1/sessions?page={max(1, total_pages)}&per_page={per_page}",
    )
    return SessionHistoryEnvelope(data=items, meta=meta, links=links)


# ==============================================================================
# 47. GET /api/v1/sessions/{id} (Khôi phục nguyên vẹn phiên)
# ==============================================================================
@router.get(
    "/{id}",
    response_model=SessionSingleEnvelope,
    summary="# 47. Khôi phục nguyên vẹn phiên (Snapshots, Tabs, Viewport)",
    description=SESSION_DETAIL_DESCRIPTION,
    responses={
        200: {
            "description": "Chi tiết toàn vẹn phiên nghiên cứu.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version hiện tại (ví dụ: '\"v14\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def get_session(
    id: UUID,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Restore complete state of a research session (Snapshot, Tabs, Viewport)."""
    data = await session_service.get_session_detail(session_id=id, user_id=current_user.id)
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 48. PATCH /api/v1/sessions/{id} (Cập nhật tiêu đề / metadata phiên nghiên cứu)
# ==============================================================================
@router.patch(
    "/{id}",
    response_model=SessionSingleEnvelope,
    summary="# 48. Cập nhật tiêu đề / metadata phiên nghiên cứu (OCC If-Match)",
    description=SESSION_UPDATE_METADATA_DESCRIPTION,
    responses={
        200: {
            "description": "Cập nhật tiêu đề thành công.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version mới sau cập nhật (ví dụ: '\"v15\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        412: {
            "model": ErrorResponse,
            "description": "Xung đột phiên bản đồng thời (CONCURRENCY_CONFLICT).",
        },
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
        428: {"model": ErrorResponse, "description": "Thiếu header If-Match."},
    },
)
async def update_session_metadata(
    id: UUID,
    payload: SessionUpdateMetadataRequest,
    response: Response,
    if_match: str | None = Header(
        None,
        alias="If-Match",
        description="Phiên bản ETag hiện tại bắt buộc (ví dụ: '\"v1\"')",
    ),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Update research session title using Optimistic Concurrency Control."""
    expected_version = parse_version_from_etag(if_match)
    data = await session_service.update_metadata_occ(
        session_id=id,
        user_id=current_user.id,
        title=payload.title,
        expected_version=expected_version,
    )
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 49. PATCH /api/v1/sessions/{id}/viewport (Tự động lưu vị trí cuộn trang & Tab)
# ==============================================================================
@router.patch(
    "/{id}/viewport",
    response_model=SessionSingleEnvelope,
    summary="# 49. Tự động lưu vị trí cuộn trang PDF và Tab đang mở (OCC)",
    description=SESSION_UPDATE_VIEWPORT_DESCRIPTION,
    responses={
        200: {
            "description": "Lưu trạng thái viewport thành công.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version mới sau cập nhật",
                    "schema": {"type": "string"},
                }
            },
        },
        412: {"model": ErrorResponse, "description": "Xung đột phiên bản đồng thời."},
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def update_session_viewport(
    id: UUID,
    payload: SessionUpdateViewportRequest,
    response: Response,
    if_match: str | None = Header(
        None,
        alias="If-Match",
        description="Phiên bản ETag hiện tại bắt buộc (ví dụ: '\"v1\"')",
    ),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Save viewport state, zoom ratio, scroll offset, and active tab with OCC."""
    expected_version = parse_version_from_etag(if_match)
    data = await session_service.update_viewport_occ(
        session_id=id,
        user_id=current_user.id,
        viewport_state=payload.viewport_state.model_dump(),
        active_tab=payload.active_tab,
        active_document_id=payload.active_document_id,
        expected_version=expected_version,
    )
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 50. DELETE /api/v1/sessions/{id} (Xóa phiên nghiên cứu)
# ==============================================================================
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="# 50. Xóa phiên nghiên cứu",
    description=SESSION_DELETE_DESCRIPTION,
    responses={
        204: {"description": "Xóa phiên thành công (No Content)."},
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def delete_session(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> Response:
    """Delete a research session and cascade cleanup its associations."""
    await session_service.delete_session(session_id=id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# 51. POST /api/v1/sessions/{id}/documents (Nạp bài vào phiên - Pure JSON)
# ==============================================================================
@router.post(
    "/{id}/documents",
    status_code=status.HTTP_202_ACCEPTED,
    summary="# 51. Nạp bài vào phiên (Pure JSON: url hoặc document_id)",
    description=SESSION_ADD_DOCUMENT_DESCRIPTION,
    responses={
        202: {"description": "Yêu cầu nạp bài đã được chấp nhận và lên lịch."},
        422: {"model": ErrorResponse, "description": "Vượt quá ngưỡng trần 5 bài báo."},
        409: {"model": ErrorResponse, "description": "Tài liệu đã tồn tại trong phiên."},
        404: {"model": ErrorResponse, "description": "Phiên hoặc bài báo không tồn tại."},
    },
)
async def add_document_to_session(
    id: UUID,
    payload: SessionAddDocumentRequest,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> JSONResponse:
    """Add a document into an active session with capacity cap of 5 papers."""
    result = await session_service.add_document_to_session(
        session_id=id,
        user_id=current_user.id,
        source_type=payload.source_type,
        document_id=payload.document_id,
        url=payload.url,
        title=payload.title,
    )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "success": True,
            "data": result,
            "meta": ResponseMeta().model_dump(mode="json"),
        },
    )


# ==============================================================================
# 51b. DELETE /api/v1/sessions/{id}/documents/{document_id} (Đóng tab bài báo)
# ==============================================================================
@router.delete(
    "/{id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="# 51b. Đóng tab bài báo trong phiên và tự động gán lại active_document_id",
    responses={
        204: {"description": "Đã gỡ bài báo khỏi phiên làm việc thành công."},
        404: {
            "model": ErrorResponse,
            "description": "Phiên hoặc tài liệu không tồn tại trong phiên.",
        },
    },
)
async def remove_document_from_session(
    id: UUID,
    document_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> Response:
    """Remove a document from active session tabs and reassign active_document_id if needed."""
    await session_service.remove_document_from_session(
        session_id=id,
        document_id=document_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# 52. POST /api/v1/sessions/{id}/messages (Hỏi đáp đa bài báo & Stream SSE)
# ==============================================================================
@router.post(
    "/{id}/messages",
    summary="# 52. Gửi câu hỏi & Stream SSE (Cross-Document Namespacing)",
    description=SESSION_POST_MESSAGE_DESCRIPTION,
    responses={
        200: {
            "description": "Dòng sự kiện SSE chứa câu trả lời và trích dẫn bounding box.",
            "content": {"text/event-stream": {}},
        },
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
        403: {"model": ErrorResponse, "description": "Phiên đã bị lưu trữ."},
    },
)
async def post_session_message(
    id: UUID,
    payload: SessionChatMessageRequest,
    request: Request,
    last_event_id: str | None = Header(
        None,
        alias="Last-Event-ID",
        description="ID sự kiện cuối cùng nhận được để khôi phục luồng stream (RFC 8895)",
    ),
    current_user: UserModel = Depends(get_current_user),
    chat_service: SessionChatService = Depends(get_session_chat_service),
) -> StreamingResponse:
    """Stream chat Q&A using Cross-Document Context Namespacing, Reasoning, and Disconnect Guard."""
    request_id = (
        (getattr(request.state, "request_id", None) if request else None)
        or (request.headers.get("x-request-id") if request else None)
        or str(uuid4())
    )
    generator = chat_service.stream_chat(
        session_id=id,
        user_id=current_user.id,
        request=payload,
        is_disconnected=request.is_disconnected,
        last_event_id=last_event_id,
        request_id=request_id,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Request-ID": request_id,
        },
    )


# ==============================================================================
# 53. GET /api/v1/sessions/{id}/messages (Lịch sử hội thoại của phiên)
# ==============================================================================
@router.get(
    "/{id}/messages",
    response_model=SessionTurnListEnvelope,
    summary="# 53. Lấy lịch sử hội thoại của phiên (phân trang)",
    description=SESSION_GET_MESSAGES_DESCRIPTION,
    responses={200: {"description": "Lịch sử hội thoại theo trình tự thời gian."}},
)
async def get_session_messages(
    id: UUID,
    page: int = Query(1, ge=1, description="Chỉ số trang (1-indexed)"),
    per_page: int = Query(50, ge=1, le=100, description="Số lượng lượt trên mỗi trang"),
    current_user: UserModel = Depends(get_current_user),
    chat_service: SessionChatService = Depends(get_session_chat_service),
) -> SessionTurnListEnvelope:
    """List conversation messages and citations in chronological order."""
    items, total = await chat_service.get_messages(
        session_id=id,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
    )
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    base_url = f"/api/v1/sessions/{id}/messages?page={page}&per_page={per_page}"
    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
    links = PaginationLinks(
        first=f"/api/v1/sessions/{id}/messages?page=1&per_page={per_page}",
        prev=f"/api/v1/sessions/{id}/messages?page={page - 1}&per_page={per_page}"
        if page > 1
        else None,
        self=base_url,
        next=f"/api/v1/sessions/{id}/messages?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None,
        last=f"/api/v1/sessions/{id}/messages?page={max(1, total_pages)}&per_page={per_page}",
    )
    return SessionTurnListEnvelope(data=items, meta=meta, links=links)


# ==============================================================================
# 54. DELETE /api/v1/sessions/{id}/messages (Xóa toàn bộ tin nhắn - Idempotent)
# ==============================================================================
@router.delete(
    "/{id}/messages",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="# 54. Xóa toàn bộ lịch sử hội thoại của phiên (Idempotent 204)",
    description=SESSION_DELETE_MESSAGES_DESCRIPTION,
    responses={204: {"description": "Đã xóa sạch lịch sử tin nhắn."}},
)
async def delete_session_messages(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    chat_service: SessionChatService = Depends(get_session_chat_service),
) -> Response:
    """Clear all conversation history in the session (Idempotent 204)."""
    await chat_service.clear_messages(session_id=id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# 55. POST /api/v1/sessions/{id}:restore-archived (Khôi phục phiên quá hạn TTL)
# ==============================================================================
@router.post(
    "/{id}:restore-archived",
    response_model=SessionSingleEnvelope,
    summary="# 55. Tải lại file PDF gốc để kích hoạt lại phiên quá hạn TTL",
    description=SESSION_RESTORE_ARCHIVED_DESCRIPTION,
    responses={
        200: {"description": "Kích hoạt lại phiên nghiên cứu thành công."},
        400: {"model": ErrorResponse, "description": "Tệp PDF không hợp lệ."},
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def restore_archived_session(
    id: UUID,
    response: Response,
    file: UploadFile = File(..., description="Tệp PDF gốc để tái kích hoạt phiên"),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Reactivate an archived session by uploading original document binary."""
    data = await session_service.restore_archived_session(
        session_id=id,
        user_id=current_user.id,
        file=file,
    )
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 57. POST /api/v1/sessions/{id}/references:ingest (Nạp bài tham khảo mở - PRD §3.3)
# ==============================================================================
@router.post(
    "/{id}/references:ingest",
    status_code=status.HTTP_200_OK,
    response_model=SessionIngestReferencesEnvelope,
    summary="Nạp tài liệu tham khảo mở vào phiên đọc sâu (PRD §3.3)",
    description=(
        "Nạp các bài báo tham khảo mở (Open-Access) từ danh mục bóc tách của bài báo nguồn "
        "vào phiên nghiên cứu. Ràng buộc: Tổng số bài báo trong phiên không vượt quá 5 bài. "
        "Nếu vượt quá 5 bài sẽ trả về lỗi HTTP 422 Unprocessable Entity."
    ),
    responses={
        200: {"model": SessionIngestReferencesEnvelope, "description": "Nạp bài báo thành công."},
        422: {"model": ErrorResponse, "description": "Vượt quá ngưỡng trần 5 bài báo của phiên."},
        404: {"model": ErrorResponse, "description": "Phiên hoặc tài liệu không tồn tại."},
    },
)
async def ingest_session_references(
    id: UUID,
    payload: SessionIngestReferencesRequest,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    resolver: IAcademicSearchResolverPort = Depends(get_academic_resolver),
) -> SessionIngestReferencesEnvelope:
    """Ingest selected open-access references into the active research session (Cap <= 5)."""
    data = await session_service.ingest_references(
        session_id=id,
        user_id=current_user.id,
        document_id=payload.document_id,
        selected_ref_indices=payload.selected_ref_indices,
        resolver=resolver,
    )
    return SessionIngestReferencesEnvelope(
        success=True,
        data=data,
        meta=ResponseMeta(),
    )
