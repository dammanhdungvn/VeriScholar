"""Unit & integration tests for Overleaf CLSI LaTeX Compiler & SyncTeX runner."""

import os
import shutil
import tarfile
from uuid import uuid4

import pytest
from api.services.clsi_latex_compiler import CLSILatexCompiler

HAS_LATEXMK = shutil.which("latexmk") is not None
HAS_XELATEX = shutil.which("xelatex") is not None
requires_latexmk = pytest.mark.skipif(not HAS_LATEXMK, reason="latexmk not installed on system")
requires_xelatex = pytest.mark.skipif(
    not (HAS_LATEXMK and HAS_XELATEX), reason="xelatex not installed on system"
)


def test_auto_engine_detection():
    """Test 1: Auto engine detection for pdflatex vs xelatex."""
    compiler = CLSILatexCompiler()

    # If code contains fontspec -> xelatex (-xelatex)
    code_xe = r"\documentclass{article}\usepackage{fontspec}\begin{document}Xin chào\end{document}"
    engine_name, engine_flag = compiler.detect_engine(code_xe)
    assert engine_name == "xelatex"
    assert engine_flag == "-xelatex"

    code_xe_opts = (
        r"\documentclass{article}\usepackage[utf8]{fontspec}\begin{document}Hi\end{document}"
    )
    engine_name2, engine_flag2 = compiler.detect_engine(code_xe_opts)
    assert engine_name2 == "xelatex"
    assert engine_flag2 == "-xelatex"

    # If code does not contain fontspec -> pdflatex (-pdf)
    code_pdf = r"\documentclass{article}\begin{document}Hello World\end{document}"
    engine_name3, engine_flag3 = compiler.detect_engine(code_pdf)
    assert engine_name3 == "pdflatex"
    assert engine_flag3 == "-pdf"


def test_detect_engine_selects_xelatex_for_vietnamese_unicode():
    """Detect XeLaTeX automatically when Unicode Vietnamese characters are present."""
    vietnamese_tex = r"\title{KIẾN TRÚC MÔ HÌNH SOCRATIC COPILOT: TỰ ĐỘNG PHẢN BIỆN}"
    engine, flag = CLSILatexCompiler.detect_engine(vietnamese_tex)
    assert engine == "xelatex"
    assert flag == "-xelatex"


@requires_xelatex
@pytest.mark.asyncio
async def test_compile_vietnamese_template_succeeds_with_xelatex(tmp_path):
    """Compile Vietnamese content succeeds with XeLaTeX."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    content = "\\documentclass{article}\\begin{document}Học giả VeriScholar\\end{document}"
    res = await compiler.compile(draft_id=uuid4(), main_tex=content)
    assert res["success"] is True
    assert res["engine"] == "xelatex"
    assert res["pdf_path"] is not None
    assert os.path.exists(res["pdf_path"])


@pytest.mark.asyncio
async def test_compilation_missing_binary_returns_diagnostic(tmp_path):
    """When latexmk executable is missing, compiler returns success=False without crashing."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path), latexmk_binary="/nonexistent/bin/latexmk")
    res = await compiler.compile(
        draft_id=uuid4(),
        main_tex=r"\documentclass{article}\begin{document}Hi\end{document}",
    )
    assert res["success"] is False
    assert res["pdf_path"] is None
    assert any("not found" in d.get("message", "").lower() for d in res["diagnostics"])


@requires_latexmk
@pytest.mark.asyncio
async def test_compilation_with_latexmk_and_auxdir(tmp_path):
    """Test 2: Compilation with latexmk, auxdir cache, and incremental speedup."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\begin{document}
Hello World
\end{document}
"""

    # First compilation: clean build, not cached
    res1 = await compiler.compile(draft_id=draft_id, main_tex=main_tex)
    assert res1["success"] is True
    assert res1["is_cached"] is False
    assert os.path.exists(res1["pdf_path"])
    assert res1["synctex_path"] is not None
    assert os.path.exists(res1["synctex_path"])

    # Check cache directory contains generated auxiliary files
    cache_dir = os.path.join(tmp_path, str(draft_id), "cache")
    assert os.path.isdir(cache_dir)
    assert any(os.listdir(cache_dir))

    # Second compilation: incremental build, cache is recognized
    res2 = await compiler.compile(draft_id=draft_id, main_tex=main_tex)
    assert res2["success"] is True
    assert res2["is_cached"] is True


@requires_latexmk
@pytest.mark.asyncio
async def test_clear_cache_flag(tmp_path):
    """Test 3: Clear cache flag wipes auxdir before compiling."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\begin{document}
Hello Cache Test
\end{document}
"""

    # Initial build to populate cache
    res1 = await compiler.compile(draft_id=draft_id, main_tex=main_tex)
    assert res1["success"] is True
    cache_dir = os.path.join(tmp_path, str(draft_id), "cache")
    assert os.path.isdir(cache_dir)
    assert any(os.listdir(cache_dir))

    # Recompile with clear_cache=True
    res2 = await compiler.compile(draft_id=draft_id, main_tex=main_tex, clear_cache=True)
    assert res2["success"] is True
    assert res2["is_cached"] is False
    assert any(os.listdir(cache_dir))


@requires_latexmk
@pytest.mark.asyncio
async def test_diagnostics_on_compilation_error(tmp_path):
    """Test 4: Compilation with syntax error returns success=False and structured diagnostics."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    invalid_tex = r"""\documentclass{article}
\begin{document}
Hello \invalidcommand World
\end{document}
"""

    res = await compiler.compile(draft_id=draft_id, main_tex=invalid_tex)
    assert res["success"] is False
    assert len(res["diagnostics"]) > 0

    # Ensure diagnostic parsed from LatexLogParser
    has_cmd_error = any(
        "invalidcommand" in d.get("context", "")
        or "invalidcommand" in d.get("message", "")
        or "Undefined control sequence" in d.get("message", "")
        for d in res["diagnostics"]
    )
    assert has_cmd_error
    assert any(d.get("severity") == "error" for d in res["diagnostics"])


@requires_latexmk
@pytest.mark.asyncio
async def test_synctex_forward_and_inverse_search(tmp_path):
    """Test 5: SyncTeX forward (source -> pdf) and inverse (pdf -> source) search."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\begin{document}
Line 3 of document for SyncTeX.
\end{document}
"""

    compile_res = await compiler.compile(draft_id=draft_id, main_tex=main_tex)
    assert compile_res["success"] is True

    # SyncTeX Forward
    fwd = await compiler.synctex_forward(draft_id=draft_id, file="main.tex", line=3, column=1)
    assert "page" in fwd and fwd["page"] == 1
    assert "h" in fwd and isinstance(fwd["h"], (int, float))
    assert "v" in fwd and isinstance(fwd["v"], (int, float))
    assert "width" in fwd and isinstance(fwd["width"], (int, float))
    assert "height" in fwd and isinstance(fwd["height"], (int, float))

    # SyncTeX Inverse
    inv = await compiler.synctex_inverse(
        draft_id=draft_id, page=1, x=float(fwd["h"] + 5.0), y=float(fwd["v"] + 1.0)
    )
    assert "file" in inv
    assert "main.tex" in inv["file"]
    assert "line" in inv and inv["line"] >= 1
    assert "column" in inv and inv["column"] >= 1


@requires_latexmk
@pytest.mark.asyncio
async def test_compile_with_bib_and_assets(tmp_path):
    """Test asset writing and BibTeX support."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\begin{document}
Citing something.
\end{document}
"""
    bib_content = """@article{test2026,
  author = {Test, A.},
  title = {Paper Title},
  journal = {Test Journal},
  year = {2026}
}"""
    assets = [
        {"filename": "test_chart.png", "content": b"fake_png_data"},
    ]

    res = await compiler.compile(
        draft_id=draft_id,
        main_tex=main_tex,
        bib_content=bib_content,
        assets=assets,
    )
    assert res["success"] is True
    draft_dir = os.path.join(tmp_path, str(draft_id))
    assert os.path.exists(os.path.join(draft_dir, "references.bib"))
    assert os.path.exists(os.path.join(draft_dir, "figures", "test_chart.png"))


@requires_latexmk
@pytest.mark.asyncio
async def test_cache_restore_from_tar_archive(tmp_path):
    """Test cache archiving and restoration without nested cache/cache/ directories."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\begin{document}
Cache restore test
\end{document}
"""
    # 1. Compile initially to generate cache and durable cache.tar.gz
    res1 = await compiler.compile(draft_id=draft_id, main_tex=main_tex)
    assert res1["success"] is True
    assert res1["is_cached"] is False

    draft_dir = os.path.join(tmp_path, str(draft_id))
    cache_dir = os.path.join(draft_dir, "cache")
    cache_archive = os.path.join(draft_dir, "cache.tar.gz")
    assert os.path.exists(cache_archive)

    # Invariant: tar archive must contain entries at its root (e.g., output.aux), NOT cache/...
    with tarfile.open(cache_archive, "r:gz") as tar:
        names = tar.getnames()
        assert any(n == "output.aux" or n.endswith(".aux") for n in names)
        assert not any(n.startswith("cache/") or n == "cache" for n in names)

    # 2. Simulate fresh container: wipe cache_dir
    shutil.rmtree(cache_dir)
    assert not os.path.exists(cache_dir)

    # 3. Recompile: should extract cache.tar.gz into cache_dir directly
    res2 = await compiler.compile(draft_id=draft_id, main_tex=main_tex)
    assert res2["success"] is True
    assert res2["is_cached"] is True
    assert os.path.isdir(cache_dir)

    # Invariant: aux/fls files must exist directly in cache_dir, never nested in cache/cache/
    assert os.path.exists(os.path.join(cache_dir, "output.aux"))
    assert not os.path.exists(os.path.join(cache_dir, "cache"))


@requires_latexmk
@pytest.mark.asyncio
async def test_assets_path_traversal_guard(tmp_path):
    """Dangerous asset filenames must not crash compilation or escape figures directory."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\begin{document}
Assets Path Traversal Guard Test
\end{document}
"""
    assets = [
        {"filename": "..", "content": b"malicious traversal"},
        {"filename": "/etc/passwd", "content": b"root:x:0:0:..."},
        {"filename": ".hidden", "content": b"hidden file"},
        {"filename": "../../evil.png", "content": b"fake evil content"},
        {"filename": "valid_chart.png", "content": b"valid image data"},
    ]

    res = await compiler.compile(
        draft_id=draft_id,
        main_tex=main_tex,
        assets=assets,
    )
    # The compilation must succeed without raising IsADirectoryError, ZipSlipSecurityError or OSError
    assert res["success"] is True
    figures_dir = os.path.join(tmp_path, str(draft_id), "figures")

    # Invariant: Only valid_chart.png should exist in figures_dir
    assert os.path.exists(os.path.join(figures_dir, "valid_chart.png"))
    assert not os.path.exists(os.path.join(figures_dir, ".hidden"))
    assert not os.path.exists(os.path.join(figures_dir, "passwd"))
    assert not os.path.exists(os.path.join(tmp_path, "evil.png"))


@requires_latexmk
@pytest.mark.asyncio
async def test_compilation_timeout(tmp_path):
    """Compilation with tiny timeout must terminate cleanly and return success=False with diagnostic."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\begin{document}
Timeout Test
\end{document}
"""
    res = await compiler.compile(
        draft_id=draft_id,
        main_tex=main_tex,
        timeout_seconds=0.001,
    )
    assert res["success"] is False
    assert res["pdf_path"] is None
    assert res["synctex_path"] is None
    assert any("timed out" in d.get("message", "").lower() for d in res["diagnostics"])


@requires_xelatex
@pytest.mark.asyncio
async def test_compile_with_xelatex(tmp_path):
    """Document with fontspec package compiles successfully via XeLaTeX."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()
    main_tex = r"""\documentclass{article}
\usepackage{fontspec}
\begin{document}
Testing XeLaTeX UTF-8 with fontspec: Tiếng Việt có dấu.
\end{document}
"""
    res = await compiler.compile(draft_id=draft_id, main_tex=main_tex)
    assert res["success"] is True
    assert res["engine"] == "xelatex"
    assert res["pdf_path"] is not None
    assert os.path.exists(res["pdf_path"])


@requires_latexmk
@pytest.mark.asyncio
async def test_stale_pdf_not_returned_on_failure(tmp_path):
    """Compiler must not return stale pdf_path or synctex_path if a subsequent compilation fails."""
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    draft_id = uuid4()

    valid_tex = r"""\documentclass{article}
\begin{document}
First valid build
\end{document}
"""
    res1 = await compiler.compile(draft_id=draft_id, main_tex=valid_tex)
    assert res1["success"] is True
    assert res1["pdf_path"] is not None
    assert os.path.exists(res1["pdf_path"])

    # Subsequent compilation with syntax error
    invalid_tex = r"""\documentclass{article}
\begin{document}
\invalidcommand
\end{document}
"""
    res2 = await compiler.compile(draft_id=draft_id, main_tex=invalid_tex)
    assert res2["success"] is False
    assert res2["pdf_path"] is None
    assert res2["synctex_path"] is None
    # Verify stale output.pdf was deleted
    output_pdf = os.path.join(tmp_path, str(draft_id), "output", "output.pdf")
    assert not os.path.exists(output_pdf)
