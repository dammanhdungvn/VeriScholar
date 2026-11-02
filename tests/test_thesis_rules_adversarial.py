import re
import sys
from pathlib import Path

# Add scripts directory to sys.path so helper scripts can be imported cleanly
sys.path.insert(0, str(Path("scripts").resolve()))


def test_adversarial_actor_boxes_no_rectangular_exceptions():
    """Adversarial check:
    Verify that AGENTS.md strictly prohibits rectangular actor boxes and requires UML stick figures,
    and that all Use Case diagrams in the report use UML stick figures and never boxes.
    """
    agents_text = Path("report-datn/AGENTS.md").read_text(encoding="utf-8")

    # 1. Ensure stick figure requirement is present in AGENTS.md
    assert "stick figure" in agents_text.lower()
    assert "hình người que" in agents_text.lower()

    # 2. Ensure rectangular actor boxes are explicitly prohibited
    assert "CẤM" in agents_text and "hình hộp chữ nhật" in agents_text
    assert "TUYỆT ĐỐI CẤM" in agents_text

    # 3. Adversarial negative check: ensure AGENTS.md contains no permissive phrases
    permissive_patterns = [
        re.compile(
            r"(cho phép|chấp nhận|có thể dùng|được phép).*(hộp chữ nhật|hình hộp)", re.IGNORECASE
        ),
        re.compile(r"actor.*(có thể là|được là|vẽ bằng|dùng).*(hộp|rectangle|box)", re.IGNORECASE),
    ]
    for pat in permissive_patterns:
        match_agents = pat.search(agents_text)
        assert not match_agents, (
            f"AGENTS.md contains permissive actor box phrasing: {match_agents.group(0)}"
        )

    # 4. Check actual LaTeX Use Case diagrams in 3_4_phan_tich_usecase.tex
    uc_file = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex")
    assert uc_file.exists()
    uc_content = uc_file.read_text(encoding="utf-8")

    # All TikZ diagrams in this file must define umlactor pic
    assert "umlactor/.pic" in uc_content
    # There are 6 TikZ Use Case figures: 1 overview + 5 sub-usecase diagrams
    assert uc_content.count("umlactor/.pic") == 6
    assert (
        uc_content.count("{umlactor}") == 7
    )  # 2 in overview (scholar + admin) + 1 each in 5 sub-use cases

    # Verify no actor node is styled as a rectangle or box
    for line in uc_content.splitlines():
        if "node" in line and (
            "Học giả" in line or "Quản trị viên" in line or "Scholar" in line or "Admin" in line
        ):
            assert "draw" not in line and "rectangle" not in line, (
                f"Actor label node styled with draw/rectangle: {line}"
            )


def test_adversarial_domain_class_diagram_placement():
    """Adversarial check:
    Verify that Domain Class Diagram placement is clearly specified before database tables
    in AGENTS.md, and that in report LaTeX code the Class Diagram strictly precedes
    database tables and ERD.
    """
    agents_text = Path("report-datn/AGENTS.md").read_text(encoding="utf-8")

    # 1. Authoring standard check in AGENTS.md
    assert (
        "đặt ở vị trí ngay trước các bảng dữ liệu" in agents_text.lower()
        or "đặt trước các bảng dữ liệu" in agents_text.lower()
    )
    assert "mục 3.6" in agents_text.lower()

    # 2. LaTeX code check in 3_6_thiet_ke_csdl.tex
    csdl_file = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex")
    assert csdl_file.exists()
    csdl_content = csdl_file.read_text(encoding="utf-8")

    # Locate positions
    pos_class_fig = csdl_content.find("\\label{fig:class_diagram_model}")
    pos_class_tab = csdl_content.find("\\label{tab:class_relationships_analysis}")
    pos_csdl_overview = csdl_content.find("\\label{subsec:csdl_tong_quan}")
    pos_table_users = csdl_content.find("\\label{tab:spec_users}")
    pos_erd_fig = csdl_content.find("\\label{fig:erd_model}")

    assert pos_class_fig != -1, "fig:class_diagram_model not found"
    assert pos_class_tab != -1, "tab:class_relationships_analysis not found"
    assert pos_csdl_overview != -1, "subsec:csdl_tong_quan not found"
    assert pos_table_users != -1, "tab:spec_users not found"
    assert pos_erd_fig != -1, "fig:erd_model not found"

    # Strict ordering assertions: Class diagram MUST precede CSDL overview, tables, and ERD
    assert pos_class_fig < pos_class_tab, "Class diagram figure must precede class analysis table"
    assert pos_class_tab < pos_csdl_overview, (
        "Class analysis table must precede subsec:csdl_tong_quan"
    )
    assert pos_csdl_overview < pos_table_users, "subsec:csdl_tong_quan must precede DB tables"
    assert pos_class_fig < pos_table_users, "Class diagram figure must precede DB tables"


def test_adversarial_sub_usecase_diagrams_precede_specs():
    """Adversarial check:
    Verify that all sub-use case diagrams are placed strictly before
    their respective BA specifications.
    """
    uc_file = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex")
    content = uc_file.read_text(encoding="utf-8")

    sub_uc_pairs = [
        ("\\label{fig:uc_kham_pha_sub}", "\\label{tab:uc_kham_pha_spec}"),
        ("\\label{fig:uc_doc_sau_sub}", "\\label{tab:uc_doc_sau_spec}"),
        ("\\label{fig:uc_bien_soan_sub}", "\\label{tab:uc_bien_soan_spec}"),
        ("\\label{fig:uc_admin_users_sub}", "\\label{tab:uc_admin_users}"),
        ("\\label{fig:uc_admin_logs_sub}", "\\label{tab:uc_admin_logs}"),
    ]

    for fig_label, spec_label in sub_uc_pairs:
        pos_fig = content.find(fig_label)
        pos_spec = content.find(spec_label)
        assert pos_fig != -1, f"Missing figure label: {fig_label}"
        assert pos_spec != -1, f"Missing spec label: {spec_label}"
        assert pos_fig < pos_spec, (
            f"Sub-use case diagram {fig_label} (pos {pos_fig}) "
            f"must appear before its specification table {spec_label} (pos {pos_spec})!"
        )


def test_adversarial_negative_constraints_enforceable():
    """Adversarial check:
    Verify negative constraints:
    - No inline arbitrary numbering (e.g., (1), (2), (3) or 1. 2. 3. in casual prose)
    - No casual bolding in prose
    - No '&' used in Vietnamese prose or headings
    """
    chapters_dir = Path("report-datn/chapters")

    # 1. Inline numbering check: (1), (2), etc.
    inline_num_pattern = re.compile(r"\(([1-9])\)\s+[A-ZÀ-Ỹa-ỹ]")
    for tex_file in chapters_dir.rglob("*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        matches = inline_num_pattern.findall(content)
        assert not matches, (
            f"File {tex_file.name} contains forbidden inline numbering pattern '(1) ...': {matches}"
        )

    # 2. Casual bolding check using scan_inline_bolds
    from scan_inline_bolds import find_casual_bolds

    casual_bolds = find_casual_bolds()
    assert len(casual_bolds) == 0, f"Found {len(casual_bolds)} casual bolds: {casual_bolds}"

    # 3. Ampersand check in Vietnamese prose/headings:
    # Any ' & ' or ' \& ' outside tabular / lstlisting / tikz / math
    for tex_file in chapters_dir.rglob("*.tex"):
        lines = tex_file.read_text(encoding="utf-8").splitlines()
        in_table = False
        in_tikz = False
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if "\\begin{tabular" in s or "\\begin{table" in s:
                in_table = True
            if "\\end{tabular" in s or "\\end{table" in s:
                in_table = False
                continue
            if in_table:
                continue

            if "\\begin{tikzpicture}" in s:
                in_tikz = True
            if "\\end{tikzpicture}" in s:
                in_tikz = False
                continue
            if in_tikz:
                continue

            if s.startswith("%"):
                continue

            # Check headings: \chapter, \section, \subsection, \subsubsection, \caption
            if any(
                h in s
                for h in [
                    "\\chapter{",
                    "\\section{",
                    "\\subsection{",
                    "\\subsubsection{",
                    "\\caption{",
                ]
            ):
                assert "&" not in s and "\\&" not in s, (
                    f"Heading in {tex_file.name}:{idx} contains '&': {s}"
                )

    # Also check headings in AGENTS.md:
    agents_lines = Path("report-datn/AGENTS.md").read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(agents_lines, 1):
        if line.startswith("#"):
            assert " & " not in line, f"AGENTS.md heading at line {idx} contains ' & ': {line}"


def test_adversarial_faculty_regulations_accuracy():
    """Adversarial check:
    Verify faculty regulations are accurately captured in both INFORMATION.md and AGENTS.md:
    - 3 softcover copies before defense
    - 1 hardcover copy with gold leaf lettering within 10 days after defense
    - Softcopy directory format MSSV_HoTen_Khoa
    - 10 weeks schedule with Week 6 mid-term checkpoint
    - 4 dismissal/suspension conditions (in AGENTS.md)
    - 3 core questions (in AGENTS.md)
    """
    info_text = Path("report-datn/INFORMATION.md").read_text(encoding="utf-8")
    agents_text = Path("report-datn/AGENTS.md").read_text(encoding="utf-8")

    # 3 softcover copies
    assert "03 quyển" in agents_text or "3 quyển" in agents_text
    assert "bìa mềm" in agents_text

    # 1 hardcover copy & 10 days
    assert "01 quyển" in agents_text or "1 quyển" in agents_text
    assert "bìa cứng" in agents_text
    assert "nhũ vàng" in agents_text
    assert "10 ngày" in agents_text

    # Softcopy directory format in both files
    assert "MãSinhViên_HọTên_Khóa" in info_text or "MSSV_HoTen_Khoa" in info_text
    assert "MãSinhViên_HọTên_Khóa" in agents_text or "MSSV_HoTen_Khoa" in agents_text

    # Week 6 mid-term checkpoint in both files
    assert "Tuần 6" in info_text
    assert "Bộ môn" in info_text
    assert "Tuần 6" in agents_text

    # 4 dismissal/suspension conditions in AGENTS.md
    for condition_kw in ["chưa thanh toán", "không gặp GVHD", "không nộp", "không đạt yêu cầu"]:
        assert condition_kw in agents_text, (
            f"AGENTS.md missing dismissal condition keyword: {condition_kw}"
        )

    # 3 core questions in AGENTS.md
    assert (
        "Làm gì?" in agents_text
        and "Làm như thế nào?" in agents_text
        and "Kết quả ra sao?" in agents_text
    )


def test_adversarial_rules_agents_no_conflicts():
    """Adversarial check:
    Verify that INFORMATION.md and AGENTS.md agree completely on all criteria:
    - Formal typography in AGENTS.md: 13pt Times New Roman, line spacing 1.5,
      margins 2.5/3.5, usable 15.0cm, page budget 50-65
    - Ground truth benchmarks in INFORMATION.md: 580 tests, 13.02s,
      DB latency 1.66ms, IoU 0.85, 20 tables & 20 refs
    - Both agree on eliminating 4 fake tables
    """
    info_text = Path("report-datn/INFORMATION.md").read_text(encoding="utf-8")
    agents_text = Path("report-datn/AGENTS.md").read_text(encoding="utf-8")

    typography_tokens = [
        "13pt",
        "Times New Roman",
        "1.5",
        "2.5",
        "3.5",
        "15{,}0",
        "50",
        "65",
    ]
    for token in typography_tokens:
        assert token in agents_text, f"AGENTS.md missing expected typography token: {token}"

    benchmark_tokens = [
        "580",
        "13.02",
        "1.66",
        "0{,}85",
        "20",
    ]
    for token in benchmark_tokens:
        assert token in info_text, f"INFORMATION.md missing expected benchmark token: {token}"

    assert ("30%" in agents_text or "30\\%" in agents_text) and (
        "70%" in agents_text or "70\\%" in agents_text
    )

    # Verify both acknowledge the same 4 eliminated fake tables
    fake_tables = ["extracted_figures", "extracted_tables", "draft_sections", "latex_compilations"]
    for ft in fake_tables:
        assert ft in info_text or ft in agents_text


def test_adversarial_table_borders_and_tabularx():
    """Adversarial check:
    Verify that AGENTS.md mandates closed grid borders |...| and \\hline for tables,
    forbids booktabs (\\toprule, \\midrule, \\bottomrule), and mandates tabularx with column X.
    """
    agents_text = Path("report-datn/AGENTS.md").read_text(encoding="utf-8")

    assert "tabularx" in agents_text
    assert "booktabs" in agents_text
    assert "\\hline" in agents_text


def test_adversarial_format_scripts_pass_without_false_positives():
    """Adversarial check:
    Execute existing format verification scripts and confirm clean exit code 0.
    """
    import subprocess

    res_format = subprocess.run(
        [sys.executable, "scripts/verify_thesis_format.py"], capture_output=True, text=True
    )
    assert res_format.returncode == 0, (
        f"verify_thesis_format.py failed:\n{res_format.stderr}\n{res_format.stdout}"
    )

    res_tables = subprocess.run(
        [sys.executable, "report-datn/scripts/test_tables_and_spacing.py"],
        capture_output=True,
        text=True,
    )
    assert res_tables.returncode == 0, (
        f"test_tables_and_spacing.py failed:\n{res_tables.stderr}\n{res_tables.stdout}"
    )

    res_preamble = subprocess.run(
        [sys.executable, "scripts/test_preamble_config.py"], capture_output=True, text=True
    )
    assert res_preamble.returncode == 0, (
        f"test_preamble_config.py failed:\n{res_preamble.stderr}\n{res_preamble.stdout}"
    )
