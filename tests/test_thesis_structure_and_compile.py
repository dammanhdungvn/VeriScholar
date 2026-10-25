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
