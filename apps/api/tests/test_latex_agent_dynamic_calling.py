"""Tests for dynamic OpenAI function/tool calling schema in LangGraph LaTeX Agent.

Verifies:
1. LATEX_AGENT_TOOLS schema defines the 4 specialized agent tools:
   - edit_latex_files
   - list_project_files
   - query_library_graph_rag
   - compile_latex_e2b
2. When openai_client is provided, reason_and_plan invokes chat.completions.create
   with tools=LATEX_AGENT_TOOLS and tool_choice="auto".
3. When tool_calls are returned by the LLM, the agent extracts tool_name and tool_input
   and executes the corresponding tool.
4. When openai_client is None, reason_and_plan deterministically falls back to
   heuristic keyword matching.
5. When openai_client encounters an error, it gracefully falls back without crashing.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from api.agents.latex_agent import (
    LATEX_AGENT_TOOLS,
    build_latex_coauthor_graph,
    reason_and_plan,
)


class MockCLSICompiler:
    """Mock compiler for deterministic testing."""

    def __init__(self, success: bool = True) -> None:
        self.call_count = 0
        self.success = success

    async def compile(self, draft_id: Any, main_tex: str, **kwargs: Any) -> dict[str, Any]:
        self.call_count += 1
        return {
            "draft_id": draft_id,
            "success": self.success,
            "pdf_path": f"/tmp/drafts/{draft_id}/output.pdf",
            "synctex_path": f"/tmp/drafts/{draft_id}/output.synctex.gz",
            "diagnostics": [],
            "errors": [],
            "logs": "Compiled successfully.",
        }


def test_latex_agent_tools_schema_definition():
    """Verify LATEX_AGENT_TOOLS contains 4 specialized tool definitions with required params."""
    assert isinstance(LATEX_AGENT_TOOLS, list)
    assert len(LATEX_AGENT_TOOLS) == 4

    tool_names = {t["function"]["name"] for t in LATEX_AGENT_TOOLS}
    expected_names = {
        "edit_latex_files",
        "list_project_files",
        "query_library_graph_rag",
        "compile_latex_e2b",
    }
    assert tool_names == expected_names

    tools_by_name = {t["function"]["name"]: t["function"] for t in LATEX_AGENT_TOOLS}

    # edit_latex_files parameters
    edit_props = tools_by_name["edit_latex_files"]["parameters"]["properties"]
    assert "target_file" in edit_props
    assert "content" in edit_props

    # list_project_files parameters
    list_props = tools_by_name["list_project_files"]["parameters"]["properties"]
    assert isinstance(list_props, dict)

    # query_library_graph_rag parameters
    rag_props = tools_by_name["query_library_graph_rag"]["parameters"]["properties"]
    assert "query" in rag_props
    assert "top_k" in rag_props

    # compile_latex_e2b parameters
    compile_props = tools_by_name["compile_latex_e2b"]["parameters"]["properties"]
    assert "clear_cache" in compile_props


@pytest.mark.asyncio
async def test_latex_agent_invokes_dynamic_tool_calling():
    """When openai_client returns a tool call for query_library_graph_rag, it is executed."""
    graph = build_latex_coauthor_graph()
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()

    # Simulate OpenAI returning a tool call for query_library_graph_rag
    tool_call_obj = MagicMock()
    tool_call_obj.function.name = "query_library_graph_rag"
    tool_call_obj.function.arguments = '{"query": "attention mechanism", "top_k": 3}'
    choice = MagicMock()
    choice.message.tool_calls = [tool_call_obj]
    choice.message.content = None
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[choice]))

    initial_state = {
        "draft_id": uuid4(),
        "user_id": uuid4(),
        "message": "Find empirical benchmarks for Attention",
        "main_tex": "\\documentclass{article}\n\\begin{document}\n\\end{document}",
        "bib_content": "",
        "assets": [],
        "compile_count": 0,
        "max_compile_attempts": 3,
        "seen_hashes": [],
        "openai_client": mock_client,
        "compiler": MockCLSICompiler(success=True),
    }

    result = await graph.ainvoke(initial_state)

    # 1. Verify OpenAI client was invoked with tools and tool_choice
    assert mock_client.chat.completions.create.called
    kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert kwargs.get("tools") == LATEX_AGENT_TOOLS
    assert kwargs.get("tool_choice") == "auto"

    # 2. Verify GraphRAG was executed and result injected into rag_context
    assert result.get("rag_context") is not None
    assert "Transformer" in result.get("main_tex", "") or "Attention" in result.get("main_tex", "")
    assert result.get("status") == "completed"


@pytest.mark.asyncio
async def test_reason_and_plan_direct_tool_call_dispatch():
    """Verify reason_and_plan parses tool call arguments and emits thinking event."""
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()

    tool_call_obj = MagicMock()
    tool_call_obj.function.name = "list_project_files"
    tool_call_obj.function.arguments = "{}"
    choice = MagicMock()
    choice.message.tool_calls = [tool_call_obj]
    choice.message.content = None
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[choice]))

    state = {
        "draft_id": uuid4(),
        "user_id": uuid4(),
        "message": "What files are in this paper?",
        "main_tex": "\\documentclass{article}\n\\begin{document}\n\\end{document}",
        "openai_client": mock_client,
    }

    plan_res = await reason_and_plan(state)
    assert plan_res.get("tool_to_call") == "list_project_files"
    assert plan_res.get("tool_input") == {}

    # Verify thinking event was emitted
    new_events = plan_res.get("new_events", [])
    assert any("list_project_files" in str(ev) for ev in new_events)


@pytest.mark.asyncio
async def test_latex_agent_fallback_when_client_is_none():
    """When openai_client is None, reason_and_plan deterministically falls back to heuristic matching."""
    state = {
        "draft_id": uuid4(),
        "user_id": uuid4(),
        "message": "Hãy tìm kiếm bằng chứng sota từ thư viện",
        "main_tex": "\\documentclass{article}\n\\begin{document}\n\\end{document}",
        "openai_client": None,
    }

    plan_res = await reason_and_plan(state)
    assert plan_res.get("tool_to_call") == "query_library_graph_rag"
    assert "query" in plan_res.get("tool_input", {})


@pytest.mark.asyncio
async def test_latex_agent_fallback_on_llm_exception():
    """When openai_client raises an exception, reason_and_plan catches it and falls back gracefully."""
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=RuntimeError("OpenAI API rate limited")
    )

    state = {
        "draft_id": uuid4(),
        "user_id": uuid4(),
        "message": "Hãy tìm kiếm bằng chứng sota từ thư viện",
        "main_tex": "\\documentclass{article}\n\\begin{document}\n\\end{document}",
        "openai_client": mock_client,
    }

    plan_res = await reason_and_plan(state)
    # Falls back gracefully to heuristic matching for sota keyword
    assert plan_res.get("tool_to_call") == "query_library_graph_rag"
