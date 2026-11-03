import subprocess
from pathlib import Path


def test_section_3_5_flow_and_no_clearpage():
    tex_path = Path("report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra KHÔNG có \clearpage trước \section{...}
    sec_pos = content.find("\\section{Phân tích một số biểu đồ tuần tự chính của hệ thống}")
    clearpage_pos = content.find("\\clearpage")
    assert clearpage_pos == -1 or clearpage_pos > sec_pos, (
        "Không được có \\clearpage trước Section 3.5 để kéo nội dung 3.5 lên trang trước"
    )


def test_ch1_no_orphan_line():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")

    # Kiểm tra không có trang nào chỉ chứa duy nhất 'rộng hệ thống.'
    for i, p in enumerate(pages):
        lines = [line.strip() for line in p.split("\n") if line.strip()]
        assert "rộng hệ thống." not in lines, f"Trang {i + 1} chứa dòng mồ côi 'rộng hệ thống.'!"


def test_no_raw_latex_macros_in_pdf():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)

    # Đảm bảo không còn ký tự backslash trong văn bản xuất bản
    assert "\\" not in res.stdout, (
        "Phát hiện ký tự gạch chéo ngược '\\' chưa thoát hoặc rò rỉ mã nguồn trong PDF"
    )

    # Đảm bảo không còn macro rò rỉ
    for word in ["bold", "RR", "argmax"]:
        assert f"\\{word}" not in res.stdout, f"Phát hiện macro thô \\{word} trong PDF"


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
        "Hình 2-4 hoặc Mục 2.5.4 cần có chốt chặn \\FloatBarrier hoặc [H]"
    )

    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")
    # Kiểm tra không có trang nào kết thúc bằng câu dở dang về khóa API BYOK bị ngắt bởi Hình 2-4
    for i, p in enumerate(pages):
        if "Người dùng trực tiếp cung cấp khóa API từ các nhà cung cấp (như" in p:
            assert "gpt-4o-mini" in p, f"Câu văn bị cắt đôi ở cuối trang {i + 1} trước Hình 2-4!"


def test_all_figures_no_broken_sentences():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")

    broken_instances = []
    # Quét qua các trang nội dung chính (từ trang 18 trở đi)
    for i in range(17, len(pages) - 1):
        prev_lines = [line.strip() for line in pages[i].split("\n") if line.strip()]
        curr_lines = [line.strip() for line in pages[i + 1].split("\n") if line.strip()]
        if not prev_lines or not curr_lines:
            continue
        # Bỏ qua số trang ở cuối
        last_line = (
            prev_lines[-2] if len(prev_lines) > 1 and prev_lines[-1].isdigit() else prev_lines[-1]
        )

        # Kiểm tra xem trang curr có bắt đầu bằng hoặc chứa Hình vẽ ở phần trên không
        first_few = curr_lines[:10]
        fig_idx = next(
            (idx for idx, line in enumerate(first_few) if line.startswith("Hình ")), None
        )
        if fig_idx is not None and fig_idx < 6:
            # Có hình ở phần đầu trang
            after_fig = curr_lines[fig_idx + 1] if fig_idx + 1 < len(curr_lines) else ""
            if (
                after_fig
                and not after_fig.isdigit()
                and not after_fig.startswith("Bảng ")
                and not after_fig.startswith("Hình ")
                and not after_fig.startswith("3.")
                and not after_fig.startswith("4.")
            ):
                # Nếu trang trước kết thúc bằng một từ dở dang (không phải dấu chấm, hai chấm)
                if last_line and last_line[-1] not in [".", ":", ";", "!", "?"]:
                    broken_instances.append(
                        f"Page {i + 1} -> {i + 2}: '{last_line}' -> "
                        f"{first_few[fig_idx]} -> '{after_fig}'"
                    )

    assert not broken_instances, f"Phát hiện hình ảnh chèn cắt ngang câu văn: {broken_instances}"


def test_standard_spacing_and_no_titlespacing_override_in_main():
    main_tex = Path("report-datn/main.tex").read_text(encoding="utf-8")
    assert "\\setstretch" not in main_tex, (
        "main.tex không được chứa \\setstretch nén ép khoảng cách dòng"
    )
    assert "\\onehalfspacing" in main_tex, (
        "main.tex phải thiết lập \\onehalfspacing chuẩn cho phần nội dung chính"
    )
    assert "\\titlespacing*" not in main_tex, (
        "main.tex không được chứa \\titlespacing* ghi đè nén khoảng cách tiêu đề"
    )


def test_usecase_3_4_3_2_and_fig_3_5_on_page_32():
    tex_path = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra không có \clearpage trước 3.4.3.2
    target_heading = (
        "\\subsubsection{Phân tích Use Case ``Hỏi đáp đọc sâu và kiểm chứng trích dẫn tọa độ''}"
    )
    pos_heading = content.find(target_heading)
    assert pos_heading != -1, "Không tìm thấy đề mục 3.4.3.2 trong tệp TeX"

    # Vùng 100 ký tự trước heading không được có \clearpage
    pre_heading = content[max(0, pos_heading - 100) : pos_heading]
    assert "\\clearpage" not in pre_heading, (
        "Không được dùng \\clearpage trước đề mục 3.4.3.2 để kéo nội dung lên trang 32"
    )

    pdf_path = Path("report-datn/main.pdf")
    if pdf_path.exists():
        res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
        pages = res.stdout.split("\x0c")
        # Tìm trang chứa Bảng 3-2 (trong phần thân bài, bỏ qua danh mục bảng biểu ở frontmatter)
        p_tab_3_2 = next(
            (
                i + 1
                for i, p in enumerate(pages)
                if i >= 18
                and (
                    "Đặc tả Use Case ``Tra cứu và tải tài liệu nghiên cứu''" in p
                    or "Bảng 3-2:" in p
                )
            ),
            None,
        )
        assert p_tab_3_2 is not None, "Không tìm thấy Bảng 3-2 trong PDF"
        page_text = pages[p_tab_3_2 - 1]
        assert "3.4.3.2" in page_text, "Trang 32 phải chứa đề mục 3.4.3.2"
        assert "Hình 3-5" in page_text, "Trang 32 phải chứa Hình 3-5"


def test_sequence_diagrams_no_newpage_and_flow():
    tex_path = Path("report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex")
    content = tex_path.read_text(encoding="utf-8")
    assert "\\newpage" not in content, (
        "Không được dùng \\newpage cưỡng bức trong 3_5_bieu_do_tuan_tu.tex"
    )

    pdf_path = Path("report-datn/main.pdf")
    if pdf_path.exists():
        res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
        pages = res.stdout.split("\x0c")
        p_fig_3_8 = next((i + 1 for i, p in enumerate(pages) if i >= 18 and "Hình 3-8:" in p), None)
        p_fig_3_9 = next((i + 1 for i, p in enumerate(pages) if i >= 18 and "Hình 3-9:" in p), None)
        p_fig_3_10 = next(
            (i + 1 for i, p in enumerate(pages) if i >= 18 and "Hình 3-10:" in p), None
        )
        p_fig_3_11 = next(
            (i + 1 for i, p in enumerate(pages) if i >= 18 and "Hình 3-11:" in p), None
        )
        assert p_fig_3_8 is not None and p_fig_3_9 is not None
        assert p_fig_3_10 is not None and p_fig_3_11 is not None
        assert p_fig_3_8 == p_fig_3_9, (
            f"Hình 3-8 (trang {p_fig_3_8}) và Hình 3-9 (trang {p_fig_3_9}) "
            "phải cùng nằm trên trang 36!"
        )
        assert p_fig_3_10 == p_fig_3_11, (
            f"Hình 3-10 (trang {p_fig_3_10}) và Hình 3-11 (trang {p_fig_3_11}) "
            "phải cùng nằm trên trang 37!"
        )


def test_usecase_3_4_3_3_and_fig_3_6_on_page_33():
    tex_path = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex")
    content = tex_path.read_text(encoding="utf-8")

    target_heading = (
        "\\subsubsection{Phân tích Use Case ``Khai phá Đồ thị tri thức và biên soạn tri thức học"
        " thuật''}"
    )
    pos_heading = content.find(target_heading)
    assert pos_heading != -1, "Không tìm thấy đề mục 3.4.3.3 trong tệp TeX"

    pre_heading = content[max(0, pos_heading - 100) : pos_heading]
    assert "\\clearpage" not in pre_heading, (
        "Không được dùng \\clearpage trước đề mục 3.4.3.3 để kéo nội dung lên trang 33"
    )

    pdf_path = Path("report-datn/main.pdf")
    if pdf_path.exists():
        res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
        pages = res.stdout.split("\x0c")
        p_tab_3_3 = next(
            (i + 1 for i, p in enumerate(pages) if i >= 18 and "Bảng 3-3:" in p),
            None,
        )
        assert p_tab_3_3 is not None, "Không tìm thấy Bảng 3-3 trong PDF"
        page_text = pages[p_tab_3_3 - 1]
        assert "3.4.3.3" in page_text, "Trang 33 phải chứa đề mục 3.4.3.3"
        assert "Hình 3-6" in page_text, "Trang 33 phải chứa Hình 3-6"


def test_toc_three_pages_no_orphan_line():
    pdf_path = Path("report-datn/main.pdf")
    if pdf_path.exists():
        res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
        pages = res.stdout.split("\x0c")

        # Trang 9 (ix), 10 (x), 11 (xi) là 3 trang mục lục
        assert "MỤC LỤC" in pages[8], "Trang 9 (ix) phải là bắt đầu Mục lục"
        assert "TÀI LIỆU THAM KHẢO" in pages[10], (
            "Trang 11 (xi) phải chứa 'TÀI LIỆU THAM KHẢO', không để tòi sang trang mới!"
        )

        # Trang 12 (xii) phải là Danh mục hình ảnh, không chứa dòng lẻ của Mục lục
        assert "DANH MỤC HÌNH ẢNH" in pages[11], (
            "Trang 12 (xii) phải là Danh mục hình ảnh, không được chứa dòng lẻ của Mục lục!"
        )
        assert "TÀI LIỆU THAM KHẢO" not in pages[11], (
            "Trang 12 (xii) không được chứa dòng lẻ 'TÀI LIỆU THAM KHẢO'!"
        )
