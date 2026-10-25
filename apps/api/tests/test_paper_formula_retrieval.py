"""Regression tests for paper formula extraction and retrieval relevance."""

from uuid import uuid4

import pymupdf
from api.adapters.chunk_extractor import PyMuPDFChunkExtractor
from api.services.session_chat_service import SessionChatService


def _pdf_with_formula() -> bytes:
    document = pymupdf.open()
    page = document.new_page(width=612, height=792)
    page.insert_text(
        (72, 90), "We optimize the objective using the following equation:", fontsize=11
    )
    page.insert_text((72, 120), "L = -sum(y * log(p))", fontsize=11)
    return document.tobytes()


def test_formula_block_is_retained_with_normalized_evidence() -> None:
    chunks = PyMuPDFChunkExtractor().extract_chunks(_pdf_with_formula(), uuid4())

    formula_chunks = [chunk for chunk in chunks if chunk.formula_text]
    assert formula_chunks
    formula = formula_chunks[0]
    assert formula.page_number == 1
    assert formula.formula_text == r"L = -\sum(y * \log(p))"
    assert formula.bounding_boxes
    assert all(box.page == 1 for box in formula.bounding_boxes)
    assert all(0.0 <= value <= 1.0 for box in formula.bounding_boxes for value in box.to_list()[:4])


def test_formula_evidence_is_not_dropped_for_short_formula_chunks() -> None:
    service = object.__new__(SessionChatService)
    formula = type(
        "Chunk",
        (),
        {
            "content": r"x=\\sqrt(y)",
            "formula_text": r"x=\\sqrt(y)",
            "chunk_index": 0,
        },
    )()
    prose = type("Chunk", (), {"content": "A generic paragraph.", "chunk_index": 1})()

    ranked = service._score_and_rank_chunks([(formula,), (prose,)], "What is the formula?")

    assert ranked[0][0][0] is formula


def test_formula_question_ranks_formula_content() -> None:
    service = object.__new__(SessionChatService)
    formula = type("Chunk", (), {"content": "L = -sum(y * log(p))", "chunk_index": 0})()
    prose = type(
        "Chunk", (), {"content": "The model is trained on scientific papers.", "chunk_index": 1}
    )()

    ranked = service._score_and_rank_chunks([(formula,), (prose,)], "What is the loss equation?")

    assert ranked[0][0][0] is formula
    assert ranked[0][1] > 0
