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


def test_all_chapters_zero_clearpage():
    """Đảm bảo không còn \\clearpage cưỡng bức trong toàn bộ các tệp chương nội dung."""
    for tex_file in CHAPTERS_DIR.glob("**/*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        clearpage_count = len(re.findall(r"\\clearpage", content))
        assert clearpage_count == 0, f"{tex_file.name} vẫn còn {clearpage_count} lệnh \\clearpage"


def test_table_1_1_full_grid_borders():
    """Đảm bảo Bảng 1-1 có đầy đủ viền ngoài và vạch phân tách ô khép kín."""
    tinh_cap_thiet = CHAPTERS_DIR / "ch1" / "1_2_tinh_cap_thiet.tex"
    content = tinh_cap_thiet.read_text(encoding="utf-8")
    assert "\\begin{tabularx}{\\textwidth}{|>" in content, "Bảng 1-1 thiếu vạch biên dọc |"
    assert "\\hline" in content, "Bảng 1-1 thiếu đường kẻ ngang \\hline"
    assert "\\toprule" not in content and "\\bottomrule" not in content
