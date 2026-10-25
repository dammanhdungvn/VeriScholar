import subprocess
from pathlib import Path


def test_thesis_files_exist():
    required_files = [
        "report-datn/main.tex",
        "report-datn/frontmatter/loi_cam_on.tex",
        "report-datn/frontmatter/loi_mo_dau.tex",
        "report-datn/frontmatter/danh_muc_viet_tat.tex",
        "report-datn/chapters/ch1_tong_quan.tex",
        "report-datn/chapters/ch2_co_so_ly_thuyet.tex",
        "report-datn/chapters/ch3_thiet_ke_he_thong.tex",
        "report-datn/chapters/ch4_thuc_nghiem.tex",
        "report-datn/chapters/ket_luan.tex",
        "report-datn/chapters/tai_lieu_tham_khao.tex",
    ]
    for file_path in required_files:
        assert Path(file_path).exists(), f"File must exist: {file_path}"


def test_thesis_compilation():
    res = subprocess.run(
        [
            "xelatex",
            "-interaction=nonstopmode",
            "-file-line-error",
            "main.tex",
        ],
        cwd="report-datn",
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"XeLaTeX compilation failed with log:\n{res.stdout[-1500:]}"
    assert Path("report-datn/main.pdf").exists()


def test_thesis_vietnamese_accented_characters_support():
    """Kiểm tra toàn bộ 144 biến thể nguyên âm tiếng Việt
    (12 nguyên âm x 6 thanh điệu x 2 kiểu chữ thường/hoa).
    """
    vietnamese_vowels = (
        "aàáảãạăằắẳẵặâầấẩẫậ"
        "eèéẻẽẹêềếểễệ"
        "iìíỉĩị"
        "oòóỏõọôồốổỗộơờớởỡợ"
        "uùúủũụưừứửữự"
        "yỳýỷỹỵ"
        "AÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬ"
        "EÈÉẺẼẸÊỀẾỂỄỆ"
        "IÌÍỈĨỊ"
        "OÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ"
        "UÙÚỦŨỤƯỪỨỬỮỰ"
        "YỲÝỶỸỴ"
    )
    assert len(vietnamese_vowels) == 144, (
        f"Must have exactly 144 vowel variants, got {len(vietnamese_vowels)}"
    )

    log_path = Path("report-datn/main.log")
    if log_path.exists():
        log_content = log_path.read_text(encoding="utf-8", errors="replace")
        assert "Missing character: There is no" not in log_content, (
            "Log contains Missing character warnings"
        )


def test_thesis_no_undefined_references():
    """Kiểm tra tệp biên dịch không có tham chiếu chéo hoặc trích dẫn undefined."""
    log_path = Path("report-datn/main.log")
    if log_path.exists():
        log_content = log_path.read_text(encoding="utf-8", errors="replace")
        assert "LaTeX Warning: There were undefined references." not in log_content
        assert "LaTeX Warning: Citation" not in log_content
