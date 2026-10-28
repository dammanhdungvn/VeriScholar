import pytest
from api.services.session_chat_service import SessionChatService


@pytest.mark.asyncio
async def test_condense_query_resolves_numeric_selection():
    chat_history = [
        {
            "role": "user",
            "content": "Bài báo đề cập những câu hỏi nghiên cứu chính nào?",
        },
        {
            "role": "assistant",
            "content": (
                "Bài báo đặt ra 3 câu hỏi nghiên cứu chính:\n"
                "1. Sự phù hợp của GNN đối với phát hiện gian lận tài chính\n"
                "2. Triển khai GNN trong các kịch bản thực tế\n"
                "3. Các yếu tố thiết kế nâng cao hiệu quả"
            ),
        },
    ]

    service = SessionChatService(db=None)
    condensed = await service._condense_query("1", chat_history)

    assert "Sự phù hợp của GNN" in condensed or "phát hiện gian lận tài chính" in condensed


@pytest.mark.asyncio
async def test_condense_query_resolves_anaphora_phuong_phap_do():
    chat_history = [
        {
            "role": "user",
            "content": "GraphSAGE là gì trong bài báo này?",
        },
        {
            "role": "assistant",
            "content": "GraphSAGE là thuật toán lấy mẫu láng giềng và tổng hợp đặc trưng cục bộ.",
        },
    ]

    service = SessionChatService(db=None)
    condensed = await service._condense_query("Phương pháp đó hoạt động thế nào?", chat_history)

    assert "GraphSAGE" in condensed


@pytest.mark.asyncio
async def test_condense_query_resolves_elliptical_chi_tiet_hon():
    chat_history = [
        {
            "role": "user",
            "content": "Phần kết luận nói gì về hạn chế của GNN?",
        },
        {
            "role": "assistant",
            "content": "Kết luận chỉ ra vấn đề mất cân bằng dữ liệu và khả năng giải thích.",
        },
    ]

    service = SessionChatService(db=None)
    condensed = await service._condense_query("Nói chi tiết hơn", chat_history)

    assert (
        "kết luận" in condensed.lower()
        or "gnn" in condensed.lower()
        or "hạn chế" in condensed.lower()
    )
