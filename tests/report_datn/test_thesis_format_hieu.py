import re
import subprocess
from pathlib import Path

import pytest

REPORT_DIR = Path(__file__).resolve().parents[2] / "report-datn"


def test_no_truong_bo_mon_in_phieu_giao_de_tai():
    file_path = REPORT_DIR / "frontmatter/phieu_giao_de_tai.tex"
    content = file_path.read_text(encoding="utf-8")
    assert "TRƯỞNG BỘ MÔN" not in content, f"Found 'TRƯỞNG BỘ MÔN' in {file_path}"
    assert "Trưởng Bộ môn" not in content, f"Found 'Trưởng Bộ môn' in {file_path}"


def test_fixed_submission_date():
    file_path = REPORT_DIR / "frontmatter/phieu_giao_de_tai.tex"
    content = file_path.read_text(encoding="utf-8")
    assert "06 tháng 11 năm 2026" in content or "06/11/2026" in content, (
        f"Missing fixed submission date in {file_path}"
    )


def test_phieu_giao_de_tai_no_printed_names():
    file_path = REPORT_DIR / "frontmatter/phieu_giao_de_tai.tex"
    content = file_path.read_text(encoding="utf-8")

    sec4_idx = content.find("4. Lời cam đoan của sinh viên:")
    assert sec4_idx != -1, f"Missing '4. Lời cam đoan của sinh viên:' in {file_path}"
    sig_block = content[sec4_idx:]

    gvhd_idx = sig_block.find("Giảng viên hướng dẫn")
    assert gvhd_idx != -1, f"Missing 'Giảng viên hướng dẫn' in {file_path}"
    sig_table = sig_block[gvhd_idx:]

    assert "Vũ Lan Phương" not in sig_table, (
        f"Found printed supervisor name 'Vũ Lan Phương' under signature line in {file_path}"
    )
    assert "Đàm Mạnh Dũng" not in sig_table, (
        f"Found printed student name 'Đàm Mạnh Dũng' under signature line in {file_path}"
    )


def test_de_cuong_no_signature_table_and_date():
    file_path = REPORT_DIR / "frontmatter/de_cuong_datn.tex"
    content = file_path.read_text(encoding="utf-8")

    marker = "Nơi thực hiện"
    idx = content.find(marker)
    assert idx != -1, f"Missing '{marker}' in {file_path}"
    end_part = content[idx:]

    assert "Giảng viên hướng dẫn" not in end_part, (
        f"Found 'Giảng viên hướng dẫn' signature block after '{marker}' in {file_path}"
    )
    assert "Sinh viên thực hiện" not in end_part, (
        f"Found 'Sinh viên thực hiện' signature block after '{marker}' in {file_path}"
    )
    assert "06 tháng 11 năm 2026" not in end_part, (
        f"Found submission date after '{marker}' in {file_path}"
    )
    assert "Hà Nội, ngày" not in end_part, f"Found date line after '{marker}' in {file_path}"


def test_loi_cam_on_no_signature_and_date():
    file_path = REPORT_DIR / "frontmatter/loi_cam_on.tex"
    content = file_path.read_text(encoding="utf-8")

    assert "Sinh viên thực hiện" not in content, f"Found 'Sinh viên thực hiện' in {file_path}"
    assert "Đàm Mạnh Dũng" not in content, f"Found 'Đàm Mạnh Dũng' in {file_path}"
    assert "06 tháng 11 năm 2026" not in content, (
        f"Found date '06 tháng 11 năm 2026' in {file_path}"
    )
    assert "Hà Nội, ngày" not in content, f"Found date line 'Hà Nội, ngày' in {file_path}"


def test_danh_muc_lists_have_no_singlespace():
    rel_paths = [
        "frontmatter/danh_muc_hinh.tex",
        "frontmatter/danh_muc_bang.tex",
    ]
    for rel_path in rel_paths:
        file_path = REPORT_DIR / rel_path
        content = file_path.read_text(encoding="utf-8")
        assert "\\begin{singlespace}" not in content, (
            f"Found \\begin{{singlespace}} in {file_path} (must use 1.5 line spacing)"
        )
        assert "\\end{singlespace}" not in content, f"Found \\end{{singlespace}} in {file_path}"


def test_cover1_front_face_no_khoa_67():
    bia_chinh_path = REPORT_DIR / "frontmatter/bia_chinh.tex"
    content = bia_chinh_path.read_text(encoding="utf-8")

    # Spine must contain KHOÁ 67 or KHÓA 67
    assert "KHOÁ 67" in content or "KHÓA 67" in content, f"Missing cohort spine in {bia_chinh_path}"

    # Front face is outside the spine block (tikzpicture overlay or rotatebox)
    front_face = re.sub(
        r"\\begin\{tikzpicture\}\[.*?overlay.*?\].*?\\end\{tikzpicture\}",
        "",
        content,
        flags=re.DOTALL,
    )
    front_face = re.sub(
        r"\\rotatebox\{[-]?90\}\{.*?\}",
        "",
        front_face,
        flags=re.DOTALL,
    )

    assert "KHOÁ 67" not in front_face and "KHÓA 67" not in front_face, (
        f"Found 'KHOÁ 67' on the front cover face of {bia_chinh_path} "
        "(it should only appear on the spine)"
    )


def test_actors_usecases_table_stt_and_symbols():
    file_path = REPORT_DIR / "chapters/ch3/3_4_phan_tich_usecase.tex"
    content = file_path.read_text(encoding="utf-8")
    table_start = content.find("\\label{tab:actors_usecases}")
    assert table_start != -1, f"Missing tab:actors_usecases in {file_path}"

    begin_table = content.rfind("\\begin{table", 0, table_start)
    end_table = content.find("\\end{table}", table_start)
    assert begin_table != -1 and end_table != -1, (
        f"Cannot locate table environment for tab:actors_usecases in {file_path}"
    )
    table_text = content[begin_table:end_table]

    # In Hieu.pdf, STT column contains only 1 (Học giả) and 2 (Quản trị viên)
    # Row indices 3 to 12 must NOT appear as STT column cells
    for n in range(3, 13):
        pattern = rf"(^|\n)\s*{n}\s*&"
        assert not re.search(pattern, table_text), (
            f"STT column in tab:actors_usecases must only have 1 and 2, but found row index {n}"
        )

    # Use Case items inside the table must use dashes '--' or bullets
    assert "--" in table_text or "\\textbullet" in table_text, (
        "tab:actors_usecases Use Case column should use dashes '--' or bullets for items"
    )


def test_usecase_spec_tables_step_conventions():
    file_path = REPORT_DIR / "chapters/ch3/3_4_phan_tich_usecase.tex"
    content = file_path.read_text(encoding="utf-8")

    spec_labels = [
        "tab:uc_kham_pha_spec",
        "tab:uc_doc_sau_spec",
        "tab:uc_graphrag_spec",
        "tab:uc_bien_soan_spec",
    ]
    for label in spec_labels:
        lbl_pos = content.find(f"\\label{{{label}}}")
        assert lbl_pos != -1, f"Missing {label} in {file_path}"

        begin_table = content.rfind("\\begin{table", 0, lbl_pos)
        end_table = content.find("\\end{table}", lbl_pos)
        assert begin_table != -1 and end_table != -1, (
            f"Cannot locate table environment for {label} in {file_path}"
        )
        table_text = content[begin_table:end_table]

        # Main flow must use en-dashes '--' and abolish 'Bước 1:', 'Bước 2:'
        assert "Bước 1:" not in table_text and "Bước 2:" not in table_text, (
            f"{label}: Luồng sự kiện chính must not use 'Bước 1:', 'Bước 2:' prefix"
        )
        main_flow_marker = "Luồng sự kiện chính"
        alt_flow_marker = "Luồng thay thế"
        main_pos = table_text.find(main_flow_marker)
        alt_pos = table_text.find(alt_flow_marker)
        assert main_pos != -1, f"{label}: Missing 'Luồng sự kiện chính'"
        main_part = table_text[main_pos:alt_pos] if alt_pos != -1 else table_text[main_pos:]
        assert "--" in main_part or "\\item[--]" in main_part, (
            f"{label}: Luồng sự kiện chính must use dashes '--'"
        )
        # Ensure no citation markers [1], [2], [i] in table
        assert not re.search(r"\[[0-9i]+\]", table_text), (
            f"{label}: Table contains citation-like brackets [number] or [i]"
        )

        # Alternative / exception flow must use dashes '--'
        alt_flow_marker = "Luồng thay thế"
        alt_pos = table_text.find(alt_flow_marker)
        if alt_pos != -1:
            alt_part = table_text[alt_pos:]
            assert "--" in alt_part or "\\item[--]" in alt_part, (
                f"{label}: Luồng thay thế / Ngoại lệ must use dashes '--'"
            )


def test_no_table_arraystretch_compression():
    ch_files = list((REPORT_DIR / "chapters").glob("ch*/*.tex"))
    for f in ch_files:
        content = f.read_text(encoding="utf-8")
        matches = re.finditer(r"\\renewcommand\{\\arraystretch\}\{([0-9.]+)\}", content)
        for m in matches:
            val = float(m.group(1))
            assert val >= 1.15, (
                f"Found compressed arraystretch {val} in {f.name}, "
                "expected >= 1.15 to match Word 1.5 line spacing"
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


def test_de_cuong_sections_numbering_and_table_layout():
    file_path = REPORT_DIR / "frontmatter/de_cuong_datn.tex"
    content = file_path.read_text(encoding="utf-8")

    expected_sections = [
        "1. Sinh viên thực hiện",
        "2. Giảng viên hướng dẫn",
        "3. Tên đề tài",
        "4. Lý do chọn đề tài",
        "5. Mục tiêu của đề tài",
        "6. Các nhiệm vụ cụ thể",
        "7. Kế hoạch thực hiện",
        "8. Nơi thực hiện đồ án:",
    ]
    for sec in expected_sections:
        assert sec in content, f"Missing section '{sec}' in {file_path} (must match Hieu.pdf 1-8)"

    # Class name must be broken across lines to prevent border collision
    assert "DCCTCT67\\newline" in content or "DCCTCT67-" in content, (
        f"Class name in {file_path} must be line-wrapped to avoid overflowing into phone column"
    )


def test_all_external_figures_png():
    for f in (REPORT_DIR / "figures").rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            assert f.suffix.lower() == ".png", f"Non-png image found: {f}"


def test_bibliography_10_milestone_papers_flat_alphabetical():
    ref_file = REPORT_DIR / "chapters/tai_lieu_tham_khao.tex"
    content = ref_file.read_text(encoding="utf-8")

    # Không chứa phân nhóm La Mã và không chứa quy chế HUMG
    assert "Tài liệu tiếng Việt" not in content, "Không được chứa tiêu đề 'Tài liệu tiếng Việt'"
    assert "Tài liệu tiếng Anh" not in content, "Không được chứa tiêu đề 'Tài liệu tiếng Anh'"
    assert "Khoa Công nghệ Thông tin" not in content, "Phải xóa bỏ tài liệu quy chế HUMG 2022"

    bibitems = re.findall(r"\\bibitem\{([^}]+)\}", content)
    assert len(bibitems) == 10, f"Danh mục phải có chính xác 10 bài báo, tìm thấy {len(bibitems)}"

    # Thứ tự A-Z chuẩn xác theo họ tác giả đầu tiên
    expected_order = [
        "asai2023selfrag",
        "cormack2009",
        "edge2024",
        "gao2023rag",
        "lewis2020",
        "malkov2018",
        "robertson1995",
        "shinn2023",
        "yan2024crag",
        "yao2022",
    ]
    assert bibitems == expected_order, f"Thứ tự tài liệu chưa đúng chuẩn A-Z: {bibitems}"

    # Đảm bảo đầy đủ siêu dữ liệu số trang và năm
    assert "758--759" in content
    assert "824--836" in content
    assert "9459--9474" in content


def test_caption_font_is_13pt():
    """Verify that Table and Figure captions in preamble.tex use 13pt font matching Word standards."""
    preamble = (REPORT_DIR / "config/preamble.tex").read_text(encoding="utf-8")
    assert "fontsize{13" in preamble and "size13" in preamble, (
        "Caption font in preamble.tex must be configured as size13 (13pt Times New Roman)"
    )
    assert "size12" not in preamble, "Found legacy size12 in preamble.tex; captions must be 13pt!"


def test_zero_citation_brackets_in_entire_body():
    """Ensure no citation-like brackets [1], [2], [14] exist anywhere in body chapters."""
    ch_files = list((REPORT_DIR / "chapters").glob("ch*/*.tex"))
    leaks = []
    for f in ch_files:
        content = f.read_text(encoding="utf-8")
        matches = re.finditer(r"\[\d+\]", content)
        for m in matches:
            leaks.append(f"{f.name}: found '{m.group(0)}'")
    assert not leaks, f"Found citation brackets in body chapters: {leaks}"


def test_bibliography_fits_single_page():
    """Verify that the 10 landmark papers in tai_lieu_tham_khao fit completely on a single page."""
    pdf_path = REPORT_DIR / "main.pdf"
    if not pdf_path.exists():
        pytest.skip("main.pdf not yet compiled")
    out = subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode("utf-8")
    pages = out.split("\x0c")
    heading_page = next((i + 1 for i, p in enumerate(pages) if "TÀI LIỆU THAM KHẢO" in p and "[1]" in p), None)
    yao_page = next((i + 1 for i, p in enumerate(pages) if "(ICLR 2023)" in p), None)
    assert heading_page is not None, "Missing TÀI LIỆU THAM KHẢO heading in PDF"
    assert yao_page == heading_page, (
        f"Bibliography spilled over: heading on page {heading_page}, but end on page {yao_page}"
    )


def test_no_near_empty_chapter_end_pages():
    """Verify that the final page of each chapter has adequate text density (>= 12 lines)."""
    pdf_path = REPORT_DIR / "main.pdf"
    if not pdf_path.exists():
        pytest.skip("main.pdf not yet compiled")
    out = subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode("utf-8")
    pages = out.split("\x0c")
    for i, p in enumerate(pages):
        if "CHƯƠNG 3:" in p and "..." not in p and i > 0:
            ch2_end_page = pages[i - 1]
            ch2_lines = [l for l in ch2_end_page.splitlines() if l.strip()]
            assert len(ch2_lines) >= 12, (
                f"Chapter 2 end page {i} has only {len(ch2_lines)} lines, creating an unsightly blank gap!"
            )
        if "CHƯƠNG 4:" in p and "..." not in p and i > 0:
            ch3_end_page = pages[i - 1]
            ch3_lines = [l for l in ch3_end_page.splitlines() if l.strip()]
            assert len(ch3_lines) >= 12, (
                f"Chapter 3 end page {i} has only {len(ch3_lines)} lines, creating an unsightly blank gap!"
            )



