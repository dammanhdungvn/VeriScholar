import subprocess
from pathlib import Path


def test_clearpage_before_section_3_5():
    tex_path = Path("report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra có \clearpage trước \section{Phân tích một số biểu đồ tuần tự chính của hệ thống}
    sec_pos = content.find("\\section{Phân tích một số biểu đồ tuần tự chính của hệ thống}")
    clearpage_pos = content.find("\\clearpage")
    assert clearpage_pos != -1 and clearpage_pos < sec_pos, (
        "Bắt buộc có \\clearpage trước Section 3.5 để chuyển toàn bộ Mục 3.5 sang đầu trang mới"
    )


def test_section_3_5_and_fig3_8_on_same_page():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    # Tìm trang chứa Section 3.5 và trang chứa Hình 3-8
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
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
    msg = (
        f"Section 3.5 (trang {p_sec_3_5}) và Hình 3-8 (trang {p_fig_3_8}) "
        f"phải cùng nằm trên 1 trang!"
    )
    assert p_sec_3_5 == p_fig_3_8, msg


def test_fig2_4_no_sentence_break():
    preamble_path = Path("report-datn/config/preamble.tex")
    preamble_content = preamble_path.read_text(encoding="utf-8")
    assert (
        "\\usepackage{float}" in preamble_content
        and "\\usepackage" in preamble_content
        and "placeins" in preamble_content
    ), "Cần nạp \\usepackage{float} và \\usepackage{placeins} trong preamble.tex"

    ch2_path = Path("report-datn/chapters/ch2/2_5_agentic_react.tex")
    ch2_content = ch2_path.read_text(encoding="utf-8")
    assert "\\FloatBarrier" in ch2_content or "\\begin{figure}[H]" in ch2_content, (
        "Hình 2-4 hoặc Mục 2.5.4 cần có chốt chặn \\FloatBarrier hoặc [H] để tránh tràn sang tiểu mục sau"
    )

    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")
    # Kiểm tra không có trang nào kết thúc bằng câu dở dang về khóa API BYOK bị ngắt bởi Hình 2-4
    for i, p in enumerate(pages):
        if "Người dùng trực tiếp cung cấp khóa API từ các nhà cung cấp (như" in p:
            assert "gpt-4o-mini" in p, f"Câu văn bị cắt đôi ở cuối trang {i+1} trước Hình 2-4!"

