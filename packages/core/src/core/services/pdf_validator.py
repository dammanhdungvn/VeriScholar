"""Pure domain PDF metadata invariant validators and coordinate scalers.

Adheres strictly to Hexagonal Architecture: zero external I/O or framework dependencies.
"""

from core.domain.exceptions import DomainValidationError

MAX_PDF_FILE_SIZE_BYTES: int = 52_428_800  # 50 MB
MAX_PDF_PAGE_COUNT: int = 100
MIN_FIRST_PAGE_TEXT_CHARS: int = 50


def validate_pdf_metadata_invariants(
    file_size: int,
    page_count: int,
    first_page_chars: int,
    is_encrypted: bool,
) -> None:
    """Validate core invariants for PDF documents before ingestion.

    Raises:
        DomainValidationError: If size, page limit, encryption, or text layer invariants fail.
    """
    if is_encrypted:
        raise DomainValidationError(
            code="PDF_PASSWORD_PROTECTED",
            message="Tệp PDF đang bị khóa mật khẩu bảo vệ. Vui lòng mở khóa trước khi tải lên.",
            field="file",
        )

    if file_size > MAX_PDF_FILE_SIZE_BYTES:
        raise DomainValidationError(
            code="PDF_FILE_TOO_LARGE",
            message=f"Dung lượng tệp ({file_size} bytes) vượt quá giới hạn tối đa 50MB.",
            field="file",
        )

    if page_count > MAX_PDF_PAGE_COUNT:
        raise DomainValidationError(
            code="PDF_PAGE_LIMIT_EXCEEDED",
            message=f"Số trang tài liệu ({page_count} trang) vượt quá giới hạn tối đa 100 trang.",
            field="file",
        )

    if first_page_chars < MIN_FIRST_PAGE_TEXT_CHARS:
        raise DomainValidationError(
            code="PDF_NO_TEXT_LAYER",
            message=(
                "Tệp PDF là bản quét ảnh thuần túy không có lớp văn bản số hóa. "
                "Vui lòng cung cấp bản có OCR để đảm bảo độ chính xác trích dẫn."
            ),
            field="file",
        )


def normalize_bbox_coordinates(
    raw_x0: float,
    raw_y0: float,
    raw_x1: float,
    raw_y1: float,
    page_width: float,
    page_height: float,
) -> tuple[int, int, int, int]:
    """Normalize raw geometric bounding box coordinates into resolution-independent [0..1000] scale.

    Args:
        raw_x0: Left coordinate in points/pixels
        raw_y0: Top coordinate in points/pixels
        raw_x1: Right coordinate in points/pixels
        raw_y1: Bottom coordinate in points/pixels
        page_width: Total page width in points/pixels
        page_height: Total page height in points/pixels

    Returns:
        tuple[int, int, int, int]: (norm_x0, norm_y0, norm_x1, norm_y1) clamped to [0, 1000].
    """
    if page_width <= 0 or page_height <= 0:
        raise ValueError("Page width and height must be positive non-zero numbers.")

    nx0 = max(0, min(1000, int(round((raw_x0 / page_width) * 1000))))
    ny0 = max(0, min(1000, int(round((raw_y0 / page_height) * 1000))))
    nx1 = max(0, min(1000, int(round((raw_x1 / page_width) * 1000))))
    ny1 = max(0, min(1000, int(round((raw_y1 / page_height) * 1000))))

    return (nx0, ny0, nx1, ny1)
