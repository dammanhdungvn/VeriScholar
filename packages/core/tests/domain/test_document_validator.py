"""Unit tests for AcademicPaperValidator 3-tier academic document gate."""

import fitz  # PyMuPDF
import pytest
from core.domain.exceptions import DomainValidationError
from core.services.document_validator import AcademicPaperValidator


def _create_mock_pdf(pages_text: list[str]) -> bytes:
    """Helper to generate an in-memory PDF with specified text per page."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page(width=595, height=842)
        page.insert_textbox(fitz.Rect(36, 36, 559, 806), text, fontsize=10)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_document_validator_paper_success() -> None:
    """A scholarly paper with sufficient word density and academic signatures passes."""
    model_desc = (
        "The dominant sequence transduction models are based on complex recurrent or "
        "convolutional neural networks. "
    )
    intro_desc = (
        "Recurrent neural networks have been firmly established as state of the art "
        "approaches in sequence modeling. "
    )
    academic_text_p1 = (
        "Attention Is All You Need\nAbstract\n"
        + model_desc * 10
        + "\n1 Introduction\n"
        + intro_desc * 10
    )
    arch_desc = (
        "The Transformer follows this overall architecture using stacked self-attention "
        "and point-wise layers. "
    )
    academic_text_p2 = (
        "3 Methodology & Model Architecture\n"
        + arch_desc * 15
        + "\nReferences\n"
        + "[1] Vaswani et al. Attention is all you need. In NeurIPS, 2017.\n"
        + "[2] Ba et al. Layer normalization. arXiv preprint, 2016.\n"
    )

    pdf_bytes = _create_mock_pdf([academic_text_p1, academic_text_p2])

    result = AcademicPaperValidator.validate_pdf(pdf_bytes)

    assert result["page_count"] == 2
    assert result["has_abstract"] is True
    assert result["has_references"] is True
    assert result["signatures_matched"] >= 2


def test_document_validator_reject_scan_image() -> None:
    """A scanned image PDF without a digital text layer (< 80 words/page) is rejected."""
    # Only 5 words on the page -> low density
    scanned_text = "Scanned receipt page 1"
    pdf_bytes = _create_mock_pdf([scanned_text])

    with pytest.raises(DomainValidationError) as exc_info:
        AcademicPaperValidator.validate_pdf(pdf_bytes)

    assert exc_info.value.code == "UNSUPPORTED_SCANNED_PDF"
    assert "mật độ văn bản quá thấp" in exc_info.value.message


def test_document_validator_reject_invoice() -> None:
    """A document with high word density but no scholarly structure is rejected."""
    payment_desc = (
        "Payment processed via credit card terminal authorization code 987654321 for monthly "
        "enterprise subscription. "
    )
    invoice_text = (
        "INVOICE & PAYMENT RECEIPT - ACME CORP\n"
        "Bill To: Customer 12345 Account Details and Payment Information.\n"
        "Item description quantity unit price total tax discount subtotal balance due terms.\n"
        + payment_desc
        * 15
    )
    pdf_bytes = _create_mock_pdf([invoice_text])

    with pytest.raises(DomainValidationError) as exc_info:
        AcademicPaperValidator.validate_pdf(pdf_bytes)

    assert exc_info.value.code == "NOT_AN_ACADEMIC_PAPER"
    assert "không có cấu trúc bài báo nghiên cứu" in exc_info.value.message


def test_document_validator_reject_empty_pdf() -> None:
    """A 0-page empty PDF is rejected."""
    empty_pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
        b"xref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n"
        b"trailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n115\n%%EOF"
    )

    with pytest.raises(DomainValidationError) as exc_info:
        AcademicPaperValidator.validate_pdf(empty_pdf_bytes)

    assert exc_info.value.code == "UNSUPPORTED_EMPTY_PDF"
