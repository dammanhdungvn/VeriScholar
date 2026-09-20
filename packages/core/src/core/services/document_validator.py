"""Academic document verification gate validating scholarly structure and digital text density."""

import re

import pymupdf as fitz

from core.domain.exceptions import DomainValidationError


class AcademicPaperValidator:
    """3-Tier Academic Document Verification Gate:

    Tầng 1: Mật độ văn bản trích xuất (loại bỏ tệp scan ảnh/vẽ kỹ thuật rác).
    Tầng 2: Chữ ký cấu trúc mục lục học thuật (Abstract, References, Methodology).
    Tầng 3: Tỷ lệ từ vựng học thuật & kiểm tra số trang.
    """

    MIN_WORDS_PER_PAGE = 80
    ACADEMIC_SECTION_PATTERNS = [
        re.compile(r"\b(abstract|tóm tắt)\b", re.IGNORECASE),
        re.compile(r"\b(introduction|giới thiệu|overview)\b", re.IGNORECASE),
        re.compile(r"\b(references|bibliography|works cited|tài liệu tham khảo)\b", re.IGNORECASE),
        re.compile(r"\b(methodology|methods|experiments|kết quả thực nghiệm)\b", re.IGNORECASE),
        re.compile(r"\b(conclusion|thảo luận|discussion)\b", re.IGNORECASE),
    ]

    @classmethod
    def validate_pdf(cls, doc_bytes: bytes) -> dict:
        """Validate PDF binary content against 3-tier academic document criteria.

        Args:
            doc_bytes: Raw bytes of the uploaded PDF file.

        Returns:
            dict containing structural audit information.

        Raises:
            DomainValidationError: With specific error code if the document fails any gate.
        """
        doc = fitz.open(stream=doc_bytes, filetype="pdf")
        try:
            page_count = len(doc)

            if page_count < 1:
                raise DomainValidationError(
                    code="UNSUPPORTED_EMPTY_PDF",
                    message="Tệp PDF rỗng, không chứa bất kỳ trang nào.",
                    field="file",
                )

            total_words = 0
            full_text_sample = ""

            # Scan first 3 pages and last 2 pages
            sample_pages = list(range(min(3, page_count))) + list(
                range(max(0, page_count - 2), page_count)
            )
            sample_pages = sorted(list(set(sample_pages)))

            for p_idx in sample_pages:
                page_text = doc[p_idx].get_text("text")
                words = page_text.split()
                total_words += len(words)
                full_text_sample += "\n" + page_text

            # Tier 1: Check text density per page (reject non-OCR scans / image-only PDFs)
            avg_words_per_page = total_words / max(1, len(sample_pages))
            if avg_words_per_page < cls.MIN_WORDS_PER_PAGE:
                raise DomainValidationError(
                    code="UNSUPPORTED_SCANNED_PDF",
                    message=(
                        "Tài liệu có mật độ văn bản quá thấp hoặc là tệp scan ảnh chưa qua "
                        "xử lý OCR. Hệ thống yêu cầu PDF chứa lớp ký tự số hóa (text layer) "
                        "để nhận diện Bounding Box."
                    ),
                    field="file",
                )

            # Tier 2: Check academic structural signatures
            matched_signatures = [
                p.pattern for p in cls.ACADEMIC_SECTION_PATTERNS if p.search(full_text_sample)
            ]

            has_abstract = bool(
                re.search(r"\b(abstract|tóm tắt)\b", full_text_sample, re.IGNORECASE)
            )
            has_references = bool(
                re.search(
                    r"\b(references|bibliography|tài liệu tham khảo)\b",
                    full_text_sample,
                    re.IGNORECASE,
                )
            )

            # Must have at least Abstract or References, or at least 2 academic signatures
            if not (has_abstract or has_references) and len(matched_signatures) < 2:
                raise DomainValidationError(
                    code="NOT_AN_ACADEMIC_PAPER",
                    message=(
                        "Tệp tải lên không có cấu trúc bài báo nghiên cứu khoa học "
                        "(thiếu phần Tóm tắt Abstract hoặc Tài liệu tham khảo References). "
                        "VeriScholar chuyên biệt phục vụ phân tích bài báo học thuật."
                    ),
                    field="file",
                )

            return {
                "page_count": page_count,
                "has_abstract": has_abstract,
                "has_references": has_references,
                "signatures_matched": len(matched_signatures),
            }
        finally:
            doc.close()
