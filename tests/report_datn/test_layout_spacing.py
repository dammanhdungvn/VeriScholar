import subprocess
from pathlib import Path


def test_clearpage_before_section_3_5():
    tex_path = Path("report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra có \clearpage trước \section{Phân tích một số biểu đồ tuần tự chính của hệ thống}
    sec_pos = content.find(
        "\\section{Phân tích một số biểu đồ tuần tự chính của hệ thống}"
    )
    clearpage_pos = content.find("\\clearpage")
    assert clearpage_pos != -1 and clearpage_pos < sec_pos, (
        "Bắt buộc có \\clearpage trước Section 3.5 để chuyển toàn bộ Mục 3.5 sang đầu trang mới"
    )


def test_section_3_5_and_fig3_8_on_same_page():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    # Tìm trang chứa Section 3.5 và trang chứa Hình 3-8
    res = subprocess.run(
        ["pdftotext", str(pdf_path), "-"], capture_output=True, text=True
    )
    pages = res.stdout.split("\x0c")

    p_sec_3_5 = next(
        (
            i + 1
            for i, p in enumerate(pages)
            if i >= 15 and "3.5 Phân tích một số biểu đồ tuần tự" in p
        ),
        None,
    )
    p_fig_3_8 = next(
        (i + 1 for i, p in enumerate(pages) if i >= 15 and "Hình 3-8" in p),
        None,
    )

    assert p_sec_3_5 is not None, "Không tìm thấy Section 3.5 trong PDF"
    assert p_fig_3_8 is not None, "Không tìm thấy Hình 3-8 trong PDF"
    assert p_sec_3_5 == p_fig_3_8, (
        f"Section 3.5 (trang {p_sec_3_5}) và Hình 3-8 (trang {p_fig_3_8}) phải cùng nằm trên 1 trang!"
    )
