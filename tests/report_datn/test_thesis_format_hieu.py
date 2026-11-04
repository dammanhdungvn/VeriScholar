import re
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parents[2] / "report-datn"

def test_no_truong_bo_mon_in_phieu_giao_de_tai():
    content = (REPORT_DIR / "frontmatter/phieu_giao_de_tai.tex").read_text(encoding="utf-8")
    assert "TRƯỞNG BỘ MÔN" not in content
    assert "Trưởng Bộ môn" not in content

def test_fixed_submission_date():
    for rel_path in ["frontmatter/phieu_giao_de_tai.tex", "frontmatter/de_cuong_datn.tex", "frontmatter/loi_cam_on.tex"]:
        content = (REPORT_DIR / rel_path).read_text(encoding="utf-8")
        assert "06 tháng 11 năm 2026" in content or "06/11/2026" in content

def test_role_titles_title_case():
    for rel_path in ["frontmatter/bia_phu.tex", "frontmatter/phieu_giao_de_tai.tex", "frontmatter/de_cuong_datn.tex"]:
        content = (REPORT_DIR / rel_path).read_text(encoding="utf-8")
        assert "Giảng viên hướng dẫn" in content
        assert "Sinh viên thực hiện" in content
        assert "GIẢNG VIÊN HƯỚNG DẪN" not in content
        assert "SINH VIÊN THỰC HIỆN" not in content

def test_no_line_compression_setstretch_1241():
    for tex_file in REPORT_DIR.rglob("*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        assert "1.241" not in content, f"Found 1.241 compression in {tex_file}"

def test_no_small_fonts_in_tables_and_forms():
    for rel_path in ["frontmatter/de_cuong_datn.tex", "frontmatter/phieu_giao_de_tai.tex"]:
        content = (REPORT_DIR / rel_path).read_text(encoding="utf-8")
        assert "\\fontsize{9" not in content
        assert "\\fontsize{8" not in content

def test_toc_non_bold_and_page_one_arabic():
    preamble = (REPORT_DIR / "config/preamble.tex").read_text(encoding="utf-8")
    assert "\\renewcommand{\\cftchapfont}{\\normalfont}" in preamble
    main = (REPORT_DIR / "main.tex").read_text(encoding="utf-8")
    # Verify arabic page numbering starts before or at muc_luc
    toc_idx = main.find("frontmatter/muc_luc")
    arabic_idx = main.find("\\pagenumbering{arabic}")
    assert arabic_idx != -1 and arabic_idx < toc_idx

def test_cover1_spine_and_cover2_no_title():
    bia_chinh = (REPORT_DIR / "frontmatter/bia_chinh.tex").read_text(encoding="utf-8")
    assert "ĐÀM MẠNH DŨNG" in bia_chinh
    assert "HỆ THỐNG THÔNG TIN" in bia_chinh
    assert "KHOÁ 67" in bia_chinh or "KHÓA 67" in bia_chinh
    bia_phu = (REPORT_DIR / "frontmatter/bia_phu.tex").read_text(encoding="utf-8")
    assert "XÂY DỰNG NỀN TẢNG" not in bia_phu

def test_no_arbitrary_bold_or_italic_in_body():
    ch_files = list((REPORT_DIR / "chapters").glob("ch*/*.tex"))
    for f in ch_files:
        content = f.read_text(encoding="utf-8")
        # Check no inline textit in body paragraphs (outside comments)
        lines = [line for line in content.splitlines() if not line.strip().startswith("%")]
        clean_text = "\n".join(lines)
        # Should not have raw \textit in body text
        assert "\\textit{" not in clean_text, f"Found \\textit in {f}"

def test_all_external_figures_png():
    for f in (REPORT_DIR / "figures").rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            assert f.suffix.lower() == ".png", f"Non-png image found: {f}"
