"""Unit & integration tests for LangGraph ReAct LaTeX Co-Author Agent (latex_agent.py).

Verifies:
1. Availability of 4 specialized tools: edit_latex_files, list_project_files,
   query_library_graph_rag, compile_latex_e2b.
2. Self-healing loop up to 3 attempts with diagnostics analysis.
3. Anti-Oscillation Guard: SHA-256 detection stops oscillation loops safely.
4. GraphRAG retrieval context injection for scholarly SOTA evidence.
5. Execution streaming events for SSE unbuffered output (tool_start, tool_end, compile_attempt).
"""

from typing import Any
from uuid import uuid4

import pytest
from api.agents.latex_agent import (
    LatexAgentState,
    LatexCoauthorAgent,
    build_latex_coauthor_graph,
    compile_latex_e2b,
    edit_latex_files,
    list_project_files,
    query_library_graph_rag,
)
from core.services.latex_log_parser import LatexDiagnostic


class MockCLSICompiler:
    """Mock compiler for deterministic testing of self-healing and error reporting."""

    def __init__(self, responses: list[dict[str, Any]] | None = None) -> None:
        self.responses = responses or []
        self.call_count = 0
        self.last_compiled_tex: str = ""

    async def compile(
        self,
        draft_id: Any,
        main_tex: str,
        bib_content: str = "",
        assets: list[dict[str, Any]] | None = None,
        clear_cache: bool = False,
        timeout_seconds: float = 15.0,
    ) -> dict[str, Any]:
        self.call_count += 1
        self.last_compiled_tex = main_tex

        if self.responses:
            idx = min(self.call_count - 1, len(self.responses) - 1)
            resp = dict(self.responses[idx])
            resp["call_count"] = self.call_count
            return resp

        # Default fallback: success
        return {
            "draft_id": draft_id,
            "success": True,
            "pdf_path": f"/tmp/drafts/{draft_id}/output.pdf",
            "synctex_path": f"/tmp/drafts/{draft_id}/output.synctex.gz",
            "diagnostics": [],
            "errors": [],
            "logs": "Output written on output.pdf (1 page).",
        }


class MockGraphRAGService:
    """Mock GraphRAG service returning scholarly evidence."""

    def __init__(
        self,
        answer: str = "Transformer outperforms CNN on WMT14.",
        evidence: list[dict] | None = None,
    ) -> None:
        self.answer = answer
        self.evidence = evidence or [
            {
                "title": "Attention Is All You Need",
                "authors": ["Vaswani et al."],
                "year": 2017,
                "text": "The Transformer achieves 28.4 BLEU on WMT14 task.",
            }
        ]
        self.called = False

    async def query_graph(self, *args, **kwargs) -> dict[str, Any]:
        self.called = True
        return {
            "mode_used": "hybrid",
            "answer": self.answer,
            "evidence_chunks": self.evidence,
            "subgraph": {"nodes": [], "edges": []},
            "meta": {"matched_entities": 1},
        }


@pytest.mark.asyncio
async def test_four_tools_availability():
    """Test 1: Availability and behavior of the 4 specialized agent tools."""
    # Verify graph builder
    graph = build_latex_coauthor_graph()
    assert graph is not None
    assert hasattr(graph, "astream")

    # 1. edit_latex_files
    state: LatexAgentState = {
        "draft_id": uuid4(),
        "user_id": uuid4(),
        "message": "test",
        "main_tex": r"\documentclass{article}\begin{document}Old\end{document}",
        "bib_content": "@article{old2020}",
        "assets": [],
        "compile_count": 0,
        "max_compile_attempts": 3,
        "seen_hashes": [],
        "oscillation_detected": False,
        "diagnostics": [],
        "compile_result": None,
        "steps": [],
        "current_plan": None,
        "tool_to_call": None,
        "tool_input": None,
        "tool_output": None,
        "rag_context": None,
        "final_answer": None,
        "status": "in_progress",
        "events": [],
    }

    new_tex = r"\documentclass{article}\begin{document}Updated Content\end{document}"
    res_edit = edit_latex_files(target_file="main.tex", content=new_tex, state=state)
    assert res_edit["target_file"] == "main.tex"
    assert "Updated Content" in res_edit["content"]
    assert state["main_tex"] == new_tex

    # 2. list_project_files
    assets = [
        {"filename": "arch.png"},
        {"filename": "benchmark_table.pdf"},
    ]
    files = list_project_files(assets=assets, state=state)
    assert "main.tex" in files
    assert "references.bib" in files
    assert "figures/arch.png" in files
    assert "figures/benchmark_table.pdf" in files

    # 3. query_library_graph_rag
    mock_rag = MockGraphRAGService()
    rag_result = await query_library_graph_rag(
        query="Transformer vs CNN",
        top_k=5,
        graph_rag_service=mock_rag,
    )
    assert mock_rag.called is True
    assert "Transformer outperforms CNN" in rag_result["answer"]
    assert len(rag_result["evidence_chunks"]) == 1

    # 4. compile_latex_e2b
    mock_compiler = MockCLSICompiler()
    draft_id = uuid4()
    compile_result = await compile_latex_e2b(
        draft_id=draft_id,
        main_tex=state["main_tex"],
        bib_content=state["bib_content"],
        assets=assets,
        clear_cache=False,
        compiler=mock_compiler,
    )
    assert mock_compiler.call_count == 1
    assert compile_result["success"] is True
    assert "output.pdf" in compile_result["pdf_path"]


@pytest.mark.asyncio
async def test_self_healing_loop_up_to_3_attempts():
    """Test 2: Agent analyzes compiler diagnostics and self-heals code up to 3 attempts."""
    draft_id = uuid4()
    user_id = uuid4()

    broken_tex = r"""\documentclass{article}
\begin{document}
\undefinedCommandXYZ
Working document
\end{document}
"""

    err_diagnostic: LatexDiagnostic = {
        "file": "main.tex",
        "line": 3,
        "column": 1,
        "severity": "error",
        "message": "Undefined control sequence.",
        "context": r"\undefinedCommandXYZ",
        "hint": "Command is not defined. Check package imports or fix typo.",
    }

    # Attempt 1: Fails with undefined control sequence
    # Attempt 2: Succeeds after healing
    compiler = MockCLSICompiler(
        responses=[
            {
                "draft_id": draft_id,
                "success": False,
                "pdf_path": None,
                "synctex_path": None,
                "diagnostics": [err_diagnostic],
                "errors": [err_diagnostic],
                "logs": "! Undefined control sequence.\nl.3 \\undefinedCommandXYZ",
            },
            {
                "draft_id": draft_id,
                "success": True,
                "pdf_path": f"/tmp/drafts/{draft_id}/output.pdf",
                "synctex_path": f"/tmp/drafts/{draft_id}/output.synctex.gz",
                "diagnostics": [],
                "errors": [],
                "logs": "Output written on output.pdf (1 page).",
            },
        ]
    )

    agent = LatexCoauthorAgent(compiler=compiler)

    events: list[dict[str, Any]] = []
    async for ev in agent.run(
        draft_id=draft_id,
        user_id=user_id,
        message="Hãy kiểm tra và biên dịch bản thảo này.",
        main_tex=broken_tex,
        bib_content="",
    ):
        events.append(ev)

    done_events = [e for e in events if e.get("event") == "done" or e.get("type") == "done"]
    assert len(done_events) == 1
    final_payload = done_events[0].get("data", {})

    # Self-healing should succeed on attempt 2 (compile_count <= 3)
    assert compiler.call_count == 2
    assert final_payload.get("compile_count") == 2
    assert final_payload.get("success") is True
    # The healed code in compiler's last call shouldn't have the broken macro
    assert r"\undefinedCommandXYZ" not in compiler.last_compiled_tex

    # Scenario B: Persistent failure must terminate safely at attempt 3
    persist_fail_compiler = MockCLSICompiler(
        responses=[
            {
                "draft_id": draft_id,
                "success": False,
                "pdf_path": None,
                "diagnostics": [err_diagnostic],
                "errors": [err_diagnostic],
                "logs": "Persistent error",
            }
        ]
        * 10
    )

    agent_failing = LatexCoauthorAgent(compiler=persist_fail_compiler)
    events_fail: list[dict[str, Any]] = []
    async for ev in agent_failing.run(
        draft_id=draft_id,
        user_id=user_id,
        message="Biên dịch bản thảo",
        main_tex=r"\documentclass{article}\begin{document}\bad\end{document}",
        bib_content="",
    ):
        events_fail.append(ev)

    # Must stop exactly at max 3 attempts
    assert persist_fail_compiler.call_count <= 3
    done_fail = [e for e in events_fail if e.get("event") == "done" or e.get("type") == "done"][0]
    assert done_fail["data"]["compile_count"] <= 3
    assert done_fail["data"]["success"] is False


@pytest.mark.asyncio
async def test_anti_oscillation_guard():
    """Test 3: Anti-Oscillation Guard stops infinite patch oscillation when SHA-256 matches."""
    draft_id = uuid4()
    user_id = uuid4()

    code_a = r"\documentclass{article}\begin{document}State A\invalid\end{document}"
    code_b = r"\documentclass{article}\begin{document}State B\invalid\end{document}"

    err_diagnostic: LatexDiagnostic = {
        "file": "main.tex",
        "line": 1,
        "column": 1,
        "severity": "error",
        "message": "Undefined control sequence.",
        "context": r"\invalid",
        "hint": "",
    }

    # Custom mock LLM client that alternates patches between code_a and code_b
    class OscillatingClient:
        def __init__(self):
            self.turn = 0

        async def generate_patch(self, *args, **kwargs) -> str:
            self.turn += 1
            # Turn 1 -> produce code_b
            # Turn 2 -> produce code_a (which matches initial code_a hash!)
            return code_b if self.turn % 2 == 1 else code_a

    compiler = MockCLSICompiler(
        responses=[
            {
                "draft_id": draft_id,
                "success": False,
                "pdf_path": None,
                "diagnostics": [err_diagnostic],
                "errors": [err_diagnostic],
                "logs": "Error",
            }
        ]
        * 10
    )

    agent = LatexCoauthorAgent(compiler=compiler, openai_client=OscillatingClient())

    events: list[dict[str, Any]] = []
    async for ev in agent.run(
        draft_id=draft_id,
        user_id=user_id,
        message="Sửa lỗi biên dịch",
        main_tex=code_a,
        bib_content="",
    ):
        events.append(ev)

    done_events = [e for e in events if e.get("event") == "done" or e.get("type") == "done"]
    assert len(done_events) == 1
    done_data = done_events[0]["data"]

    # Oscillation must be detected and loop terminated safely
    assert done_data.get("oscillation_detected") is True
    # Should terminate early without burning max attempts
    assert compiler.call_count < 3 or done_data.get("status") == "oscillation_stopped"


@pytest.mark.asyncio
async def test_graph_rag_retrieval_context_injection():
    """Test 4: User asks for SOTA evidence, agent invokes GraphRAG and injects retrieved context."""
    draft_id = uuid4()
    user_id = uuid4()

    initial_tex = r"""\documentclass{article}
\begin{document}
\section{Related Work}
% Cần bổ sung đánh giá các mô hình SOTA
\end{document}
"""

    mock_rag = MockGraphRAGService(
        answer="Các mô hình Transformer đạt độ chính xác SOTA trên nhiều benchmark dịch máy.",
        evidence=[
            {
                "title": "Attention Is All You Need",
                "authors": ["Vaswani et al."],
                "year": 2017,
                "text": "Transformer architecture achieves 28.4 BLEU score.",
            }
        ],
    )
    mock_compiler = MockCLSICompiler()

    agent = LatexCoauthorAgent(compiler=mock_compiler, graph_rag_service=mock_rag)

    events: list[dict[str, Any]] = []
    async for ev in agent.run(
        draft_id=draft_id,
        user_id=user_id,
        message="Hãy bổ sung bằng chứng SOTA về mô hình Transformer từ thư viện vào mục Related Work.",
        main_tex=initial_tex,
        bib_content="",
    ):
        events.append(ev)

    assert mock_rag.called is True
    done_event = [e for e in events if e.get("event") == "done" or e.get("type") == "done"][0]
    final_tex = done_event["data"].get("main_tex", "")

    # Injected content or citation should appear in main_tex or rag_context
    assert ("Transformer" in final_tex) or ("Attention Is All You Need" in final_tex)
    assert done_event["data"].get("rag_context") is not None


@pytest.mark.asyncio
async def test_execution_streaming_events():
    """Test 5: Agent yields execution steps formatted for SSE streaming."""
    draft_id = uuid4()
    user_id = uuid4()

    compiler = MockCLSICompiler()
    agent = LatexCoauthorAgent(compiler=compiler)

    events: list[dict[str, Any]] = []
    async for ev in agent.run(
        draft_id=draft_id,
        user_id=user_id,
        message="Biên dịch tài liệu này",
        main_tex=r"\documentclass{article}\begin{document}Hello\end{document}",
        bib_content="",
    ):
        events.append(ev)

    event_types = [e.get("event") or e.get("type") for e in events]

    # Verify execution streaming event sequence
    assert "tool_start" in event_types
    assert "tool_end" in event_types
    assert "compile_attempt" in event_types
    assert "done" in event_types

    # Validate structure of events
    compile_attempt_ev = [
        e for e in events if (e.get("event") or e.get("type")) == "compile_attempt"
    ][0]
    assert "attempt" in compile_attempt_ev["data"]
    assert "success" in compile_attempt_ev["data"]
