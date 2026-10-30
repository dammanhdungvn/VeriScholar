"""Integration and workflow tests for LatexCoauthorAgent ReAct engine."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from api.agents.latex_agent import LatexCoauthorAgent


class MockCLSICompiler:
    """Deterministic mock compiler for coauthor agent tests."""

    def __init__(self, success: bool = True) -> None:
        self.call_count = 0
        self.success = success

    async def compile(self, draft_id, main_tex, **kwargs):
        self.call_count += 1
        return {
            "draft_id": draft_id,
            "success": self.success,
            "pdf_path": f"/tmp/drafts/{draft_id}/output.pdf",
            "synctex_path": f"/tmp/drafts/{draft_id}/output.synctex.gz",
            "diagnostics": [],
            "errors": [],
            "logs": "Compilation succeeded.",
        }


@pytest.mark.asyncio
async def test_latex_coauthor_agent_end_to_end_workflow():
    """Verify LatexCoauthorAgent runs workflow with dynamic tool client."""
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()

    tool_call_obj = MagicMock()
    tool_call_obj.function.name = "compile_latex_e2b"
    tool_call_obj.function.arguments = '{"clear_cache": false}'
    choice = MagicMock()
    choice.message.tool_calls = [tool_call_obj]
    choice.message.content = None
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[choice]))

    compiler = MockCLSICompiler(success=True)
    agent = LatexCoauthorAgent(compiler=compiler, openai_client=mock_client)

    events = []
    async for ev in agent.run(
        draft_id=uuid4(),
        user_id=uuid4(),
        message="Vui lòng biên dịch tài liệu LaTeX này",
        main_tex=r"\documentclass{article}\begin{document}Test\end{document}",
    ):
        events.append(ev)

    event_types = [e.get("event") or e.get("type") for e in events]
    assert "done" in event_types
    assert compiler.call_count >= 1
