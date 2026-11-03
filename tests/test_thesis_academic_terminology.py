from pathlib import Path


def test_no_clunky_terminology_in_chapters():
    chapters_dir = Path("report-datn/chapters")
    forbidden_phrases = [
        "két an toàn",
        "Két an toàn",
        "két khóa",
        "Két khóa",
        "cô lập hạt nhân",
        "ranh giới hạt nhân",
    ]
    violations = []
    for tex_file in chapters_dir.rglob("*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            if phrase in content:
                violations.append(f"{tex_file}: contains forbidden phrase '{phrase}'")
    assert not violations, "Found forbidden clunky terminology:\n" + "\n".join(violations)


def test_byok_terminology_standards():
    sec_2_5 = Path("report-datn/chapters/ch2/2_5_agentic_react.tex").read_text(encoding="utf-8")
    assert "Bring Your Own Key (BYOK)" in sec_2_5
    assert (
        "\\subsection{Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK) và chuẩn"
        " mã hóa AES-256-GCM}"
        in sec_2_5
    )
    assert "cô lập hạt nhân" not in sec_2_5
    assert "Môi trường máy ảo MicroVM E2B cô lập cấp hệ điều hành" in sec_2_5


def test_byok_in_abbreviations_table():
    abbr = Path("report-datn/frontmatter/danh_muc_viet_tat.tex").read_text(encoding="utf-8")
    assert "BYOK" in abbr
    assert "Bring Your Own Key" in abbr
