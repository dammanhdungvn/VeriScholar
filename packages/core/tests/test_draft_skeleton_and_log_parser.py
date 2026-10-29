import pytest
from core.services.draft_skeleton import (
    escape_bibtex_value,
    generate_academic_skeleton,
    sanitize_and_validate_asset_filename,
)
from core.services.latex_log_parser import LatexLogParser


def test_parse_latex_log_extracts_syntax_error():
    sample_log = """
! Undefined control sequence.
l.42 \\invalidcommand
                    {test}
The control sequence at the end of the top line
"""
    diagnostics = LatexLogParser.parse_log(sample_log)
    assert len(diagnostics) >= 1
    assert diagnostics[0]["line"] == 42
    assert diagnostics[0]["severity"] == "error"
    assert "Undefined control sequence" in diagnostics[0]["message"]
    assert diagnostics[0]["file"] == "main.tex"
    assert "hint" in diagnostics[0]


def test_parse_latex_log_extracts_citation_warning():
    sample_log = "LaTeX Warning: Citation 'vaswani2017' on page 2 undefined on input line 80."
    diagnostics = LatexLogParser.parse_log(sample_log)
    assert len(diagnostics) == 1
    assert diagnostics[0]["line"] == 80
    assert diagnostics[0]["severity"] == "warning"
    assert "vaswani2017" in diagnostics[0]["message"]
    assert (
        "references.bib" in diagnostics[0]["hint"]
        or "trích dẫn" in diagnostics[0]["hint"]
        or "citation" in diagnostics[0]["hint"].lower()
    )


def test_parse_latex_log_extracts_missing_file_error():
    sample_log = """
! LaTeX Error: File 'amsmath.sty' not found.

Type X to quit or <RETURN> to proceed,
or enter new name. (Default extension: sty)
"""
    diagnostics = LatexLogParser.parse_log(sample_log)
    assert len(diagnostics) >= 1
    assert diagnostics[0]["severity"] == "error"
    assert "amsmath.sty" in diagnostics[0]["message"]


def test_parse_latex_log_handles_empty_or_clean_log():
    assert LatexLogParser.parse_log("") == []
    assert LatexLogParser.parse_log("   \n\t  ") == []
    clean_log = """
This is pdfTeX, Version 3.141592653-2.6-1.40.24 (TeX Live 2022) (preloaded format=pdflatex)
entering extended mode
Output written on main.pdf (1 page, 12345 bytes).
Transcript written on main.log.
"""
    assert LatexLogParser.parse_log(clean_log) == []


def test_escape_bibtex_value_handles_special_characters():
    raw = "Deep Learning & Transformers: A 50% Speedup with $E=mc^2$ in file_1 #42"
    escaped = escape_bibtex_value(raw)
    assert r"\&" in escaped
    assert r"\%" in escaped
    assert r"\$" in escaped
    assert r"\_" in escaped
    assert r"\#" in escaped

    # Does not double-escape
    re_escaped = escape_bibtex_value(escaped)
    assert re_escaped == escaped


def test_skeleton_generator_escapes_bibtex_special_characters():
    papers = [
        {
            "title": "Deep Learning & Transformers: A 50% Speedup",
            "authors": ["Vaswani, A."],
            "year": 2017,
            "citation_key": "vaswani2017",
        }
    ]
    main_tex, bib_content = generate_academic_skeleton("Test Project", papers, [])
    assert r"\&" in bib_content
    assert r"\%" in bib_content
    assert r"\cite{vaswani2017}" in main_tex
    assert r"\title{" in main_tex
    assert r"\section{Introduction}" in main_tex
    assert r"\section{Related Work}" in main_tex
    assert r"\bibliography{references}" in main_tex


def test_skeleton_generator_with_notes_and_special_chars_in_title():
    papers = [
        {
            "title": "Methods_v2 #1",
            "authors": "Smith, J.",
            "year": 2023,
            "citation_key": "smith2023",
        }
    ]
    notes = [{"content": "Important note regarding Transformers"}]
    main_tex, bib_content = generate_academic_skeleton("AI & ML: 100% #1", papers, notes)
    assert r"\_" in bib_content
    assert r"\#" in bib_content
    assert r"\cite{smith2023}" in main_tex
    assert "Important note regarding Transformers" in main_tex


def test_sanitize_asset_filename_accepts_valid_names():
    assert sanitize_and_validate_asset_filename("figure1.png", 1024) == "figure1.png"
    assert sanitize_and_validate_asset_filename("arch_diagram-2.jpg", 2048) == "arch_diagram-2.jpg"
    assert sanitize_and_validate_asset_filename("plot_2026.webp", 5000) == "plot_2026.webp"
    assert sanitize_and_validate_asset_filename("appendix_chart.pdf", 5000) == "appendix_chart.pdf"


def test_sanitize_asset_filename_rejects_path_traversal():
    bad_filenames = [
        "../../evil.png",
        "/etc/passwd",
        "foo/bar.png",
        "..\\evil.png",
        "sub/dir/img.png",
        "../test.jpg",
    ]
    for bad_name in bad_filenames:
        with pytest.raises(ValueError):
            sanitize_and_validate_asset_filename(bad_name, 1024)


def test_sanitize_asset_filename_rejects_oversized_file():
    with pytest.raises(ValueError):
        sanitize_and_validate_asset_filename("huge_image.png", 11 * 1024 * 1024)


def test_sanitize_asset_filename_rejects_invalid_size_or_hidden_file():
    with pytest.raises(ValueError):
        sanitize_and_validate_asset_filename("", 1024)
    with pytest.raises(ValueError):
        sanitize_and_validate_asset_filename(".hidden.png", 1024)
    with pytest.raises(ValueError):
        sanitize_and_validate_asset_filename("noextension", 1024)
    with pytest.raises(ValueError):
        sanitize_and_validate_asset_filename("test.png", 0)
    with pytest.raises(ValueError):
        sanitize_and_validate_asset_filename("test.png", -10)


def test_parse_latex_log_extracts_file_line_error_format():
    sample_log = """
./main.tex:73: Undefined control sequence.
<argument> \\nonexistentcommand
                                l.73 \\nonexistentcommand{arg}
"""
    diagnostics = LatexLogParser.parse_log(sample_log)
    assert len(diagnostics) >= 1
    assert diagnostics[0]["line"] == 73
    assert diagnostics[0]["severity"] == "error"
    assert "Undefined control sequence" in diagnostics[0]["message"]
    assert diagnostics[0]["file"] == "main.tex"


def test_parse_latex_log_extracts_on_input_line_error():
    sample_log = """
! LaTeX Error: Environment align undefined on input line 55.

See the LaTeX manual or LaTeX Companion for explanation.
"""
    diagnostics = LatexLogParser.parse_log(sample_log)
    assert len(diagnostics) >= 1
    assert diagnostics[0]["line"] == 55
    assert diagnostics[0]["severity"] == "error"
    assert "Environment align undefined" in diagnostics[0]["message"]
