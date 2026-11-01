import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "chapters"

def test_no_booktabs_rules():
    """Đảm bảo không còn \\toprule, \\midrule, \\bottomrule trong các file chương."""
    for tex_file in CHAPTERS_DIR.glob("**/*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        assert "\\toprule" not in content, f"Phát hiện \\toprule trong {tex_file.name}"
        assert "\\midrule" not in content, f"Phát hiện \\midrule trong {tex_file.name}"
        assert "\\bottomrule" not in content, f"Phát hiện \\bottomrule trong {tex_file.name}"

def test_ch4_ui_no_unnecessary_clearpage():
    """Đảm bảo không còn \\clearpage cưỡng bức giữa các tiểu mục giao diện trong 4_2_giao_dien.tex."""
    ui_tex = CHAPTERS_DIR / "ch4" / "4_2_giao_dien.tex"
    content = ui_tex.read_text(encoding="utf-8")
    clearpage_count = len(re.findall(r"\\clearpage", content))
    assert clearpage_count == 0, f"4_2_giao_dien.tex vẫn còn {clearpage_count} lệnh \\clearpage"

def test_ch2_and_ch3_no_extraneous_clearpage():
    """Đảm bảo không còn \\clearpage cưỡng bức giữa các tiểu mục trong 2_5_agentic_react và 3_5_bieu_do_tuan_tu."""
    react_tex = CHAPTERS_DIR / "ch2" / "2_5_agentic_react.tex"
    seq_tex = CHAPTERS_DIR / "ch3" / "3_5_bieu_do_tuan_tu.tex"
    
    react_count = len(re.findall(r"\\clearpage", react_tex.read_text(encoding="utf-8")))
    seq_count = len(re.findall(r"\\clearpage", seq_tex.read_text(encoding="utf-8")))
    
    assert react_count == 0, f"2_5_agentic_react.tex vẫn còn {react_count} lệnh \\clearpage"
    assert seq_count == 0, f"3_5_bieu_do_tuan_tu.tex vẫn còn {seq_count} lệnh \\clearpage"
