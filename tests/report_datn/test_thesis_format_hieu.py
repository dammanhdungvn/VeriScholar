from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parents[2] / "report-datn"


def test_no_truong_bo_mon_in_phieu_giao_de_tai():
    file_path = REPORT_DIR / "frontmatter/phieu_giao_de_tai.tex"
    content = file_path.read_text(encoding="utf-8")
    assert "TRƯỞNG BỘ MÔN" not in content, f"Found 'TRƯỞNG BỘ MÔN' in {file_path}"
    assert "Trưởng Bộ môn" not in content, f"Found 'Trưởng Bộ môn' in {file_path}"


def test_fixed_submission_date():
    rel_paths = [
        "frontmatter/phieu_giao_de_tai.tex",
        "frontmatter/de_cuong_datn.tex",
        "frontmatter/loi_cam_on.tex",
    ]
    for rel_path in rel_paths:
        file_path = REPORT_DIR / rel_path
        content = file_path.read_text(encoding="utf-8")
        assert "06 tháng 11 năm 2026" in content or "06/11/2026" in content, (
            f"Missing fixed submission date in {file_path}"
        )


def test_role_titles_title_case():
    rel_paths = [
        "frontmatter/bia_phu.tex",
        "frontmatter/phieu_giao_de_tai.tex",
        "frontmatter/de_cuong_datn.tex",
    ]
    for rel_path in rel_paths:
        file_path = REPORT_DIR / rel_path
        content = file_path.read_text(encoding="utf-8")
        assert "Giảng viên hướng dẫn" in content, f"Missing 'Giảng viên hướng dẫn' in {file_path}"
        assert "Sinh viên thực hiện" in content, f"Missing 'Sinh viên thực hiện' in {file_path}"
        assert "GIẢNG VIÊN HƯỚNG DẪN" not in content, (
            f"Found all-caps 'GIẢNG VIÊN HƯỚNG DẪN' in {file_path}"
        )
        assert "SINH VIÊN THỰC HIỆN" not in content, (
            f"Found all-caps 'SINH VIÊN THỰC HIỆN' in {file_path}"
        )


def test_no_line_compression_setstretch_1241():
    for tex_file in REPORT_DIR.rglob("*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        assert "1.241" not in content, f"Found 1.241 compression in {tex_file}"


def test_no_small_fonts_in_tables_and_forms():
    rel_paths = [
        "frontmatter/de_cuong_datn.tex",
        "frontmatter/phieu_giao_de_tai.tex",
    ]
    for rel_path in rel_paths:
        file_path = REPORT_DIR / rel_path
        content = file_path.read_text(encoding="utf-8")
        assert "\\fontsize{9" not in content, f"Found \\fontsize{{9 in {file_path}"
        assert "\\fontsize{8" not in content, f"Found \\fontsize{{8 in {file_path}"


def test_toc_non_bold_and_page_one_arabic():
    preamble = (REPORT_DIR / "config/preamble.tex").read_text(encoding="utf-8")
    assert "\\renewcommand{\\cftchapfont}{\\normalfont}" in preamble
    main = (REPORT_DIR / "main.tex").read_text(encoding="utf-8")
    # Verify arabic page numbering starts before or at muc_luc
    toc_idx = main.find("frontmatter/muc_luc")
    arabic_idx = main.find("\\pagenumbering{arabic}")
    assert arabic_idx != -1 and arabic_idx < toc_idx


def test_cover1_spine_and_cover2_no_title():
    bia_chinh_path = REPORT_DIR / "frontmatter/bia_chinh.tex"
    bia_chinh = bia_chinh_path.read_text(encoding="utf-8")
    assert "ĐÀM MẠNH DŨNG" in bia_chinh, f"Missing author spine in {bia_chinh_path}"
    assert "HỆ THỐNG THÔNG TIN" in bia_chinh, f"Missing major spine in {bia_chinh_path}"
    assert "KHOÁ 67" in bia_chinh or "KHÓA 67" in bia_chinh, (
        f"Missing cohort spine in {bia_chinh_path}"
    )
    bia_phu_path = REPORT_DIR / "frontmatter/bia_phu.tex"
    bia_phu = bia_phu_path.read_text(encoding="utf-8")
    assert "XÂY DỰNG NỀN TẢNG" not in bia_phu, (
        f"Unexpected thesis title in sub-cover {bia_phu_path}"
    )


def test_no_arbitrary_bold_or_italic_in_body():
    ch_files = list((REPORT_DIR / "chapters").glob("ch*/*.tex"))
    env_tokens = (
        "\\begin{table}",
        "\\begin{tabular",
        "\\begin{tikzpicture}",
        "\\begin{figure}",
    )
    end_tokens = (
        "\\end{table}",
        "\\end{tabular",
        "\\end{tikzpicture}",
        "\\end{figure}",
    )
    for f in ch_files:
        content = f.read_text(encoding="utf-8")
        clean_lines = []
        in_env = 0
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("%"):
                continue
            if any(tok in stripped for tok in env_tokens):
                in_env += 1
            if in_env == 0:
                clean_lines.append(stripped)
            if any(tok in stripped for tok in end_tokens) and in_env > 0:
                in_env -= 1
        clean_text = "\n".join(clean_lines)
        assert "\\textit{" not in clean_text, f"Found \\textit in {f}"
        assert "\\textbf{" not in clean_text, f"Found \\textbf in {f}"


def test_all_external_figures_png():
    for f in (REPORT_DIR / "figures").rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            assert f.suffix.lower() == ".png", f"Non-png image found: {f}"
