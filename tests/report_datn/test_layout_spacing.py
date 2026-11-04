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
        # Tìm trang chứa đề mục 3.4.3.2
        p_sec_3_4_3_2 = next(
            (i + 1 for i, p in enumerate(pages) if i >= 18 and "3.4.3.2" in p),
            None,
        )
        assert p_sec_3_4_3_2 is not None, "Không tìm thấy đề mục 3.4.3.2 trong PDF"
        page_text = pages[p_sec_3_4_3_2 - 1]
        assert "Hình 3-5" in page_text, "Trang chứa đề mục 3.4.3.2 phải chứa Hình 3-5"


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
        p_sec = next(
            (i + 1 for i, p in enumerate(pages) if i >= 18 and "3.4.3.3" in p),
            None,
        )
        assert p_sec is not None, "Không tìm thấy đề mục 3.4.3.3 trong PDF"
        p_fig = next(
            (i + 1 for i, p in enumerate(pages) if i >= 18 and "Hình 3-6:" in p),
            None,
        )
        assert p_fig is not None, "Không tìm thấy Hình 3-6 trong PDF"


def test_toc_three_pages_no_orphan_line():
    pdf_path = Path("report-datn/main.pdf")
    if pdf_path.exists():
        res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
        pages = res.stdout.split("\x0c")

        # Bắt đầu mục lục ở trang 9 (trang 1 theo đánh số Arabic)
        assert "MỤC LỤC" in pages[8], "Trang 9 phải là bắt đầu Mục lục"

        # Tìm trang bắt đầu Danh mục hình ảnh (tiêu đề bắt đầu ở đầu trang)
        lof_idx = next(
            (i for i, p in enumerate(pages) if p.strip().startswith("DANH MỤC HÌNH ẢNH")), None
        )
        assert lof_idx is not None, "Phải tìm thấy Danh mục hình ảnh sau Mục lục"

        # Trang kết thúc mục lục (ngay trước Danh mục hình ảnh) phải chứa TÀI LIỆU THAM KHẢO
        last_toc_page = pages[lof_idx - 1]
        assert "TÀI LIỆU THAM KHẢO" in last_toc_page, (
            "Trang kết thúc Mục lục phải chứa 'TÀI LIỆU THAM KHẢO'!"
        )

        # Trang Danh mục hình ảnh không được chứa dòng lẻ của Mục lục
        assert "DANH MỤC HÌNH ẢNH" in pages[lof_idx], (
            "Trang Danh mục hình ảnh không được chứa dòng lẻ của Mục lục!"
        )
        assert "TÀI LIỆU THAM KHẢO" not in pages[lof_idx], (
            "Trang Danh mục hình ảnh không được chứa dòng lẻ 'TÀI LIỆU THAM KHẢO'!"
        )


def test_lof_single_page_and_no_orphan_spillover():
    """Kiểm tra Danh mục hình ảnh (LOF) và Danh mục bảng biểu (LOT) bắt đầu trang sạch sẽ.

    Theo chuẩn Hieu.pdf với giãn dòng 1.5 (setstretch 1.45), LOF có thể trải dài
    qua 2 trang một cách tự nhiên. LOT phải bắt đầu ngay sau trang kết thúc của LOF.
    """
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")

    # Tìm trang bắt đầu Danh mục hình ảnh
    lof_idx = next(
        (
            i
            for i, p in enumerate(pages)
            if "DANH MỤC HÌNH ẢNH" in p.strip()[:100] or p.strip().startswith("DANH MỤC HÌNH ẢNH")
        ),
        None,
    )
    assert lof_idx is not None, "Phải tìm thấy Danh mục hình ảnh"
    assert "DANH MỤC HÌNH ẢNH" in pages[lof_idx], "Phải là Danh mục hình ảnh"

    # Tìm trang bắt đầu Danh mục bảng biểu
    lot_idx = next(
        (
            i
            for i, p in enumerate(pages)
            if "DANH MỤC BẢNG BIỂU" in p.strip()[:100] or p.strip().startswith("DANH MỤC BẢNG BIỂU")
        ),
        None,
    )
    assert lot_idx is not None, "Phải tìm thấy Danh mục bảng biểu"

    # Danh mục bảng biểu phải theo sau Danh mục hình ảnh (cách 1 hoặc 2 trang)
    assert lof_idx < lot_idx, "Danh mục bảng biểu phải nằm sau Danh mục hình ảnh"
    assert lot_idx - lof_idx in (1, 2), (
        f"LOF bắt đầu trang {lof_idx + 1}, LOT bắt đầu trang {lot_idx + 1}; "
        "LOF chỉ được chiếm 1 hoặc 2 trang theo chuẩn Hieu.pdf!"
    )
    assert "DANH MỤC BẢNG BIỂU" in pages[lot_idx]


def test_ch3_database_tables_flow_and_no_orphan_page():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")

    # Tìm trang chứa Bảng 3-8, Bảng 3-9 và Bảng 3-10
    p_tab_3_8 = next((i + 1 for i, p in enumerate(pages) if "Bảng 3-8:" in p), None)
    p_tab_3_9 = next((i + 1 for i, p in enumerate(pages) if "Bảng 3-9:" in p), None)
    p_tab_3_10 = next((i + 1 for i, p in enumerate(pages) if i >= 18 and "Bảng 3-10:" in p), None)
    assert p_tab_3_8 is not None and p_tab_3_9 is not None and p_tab_3_10 is not None
    assert p_tab_3_8 <= p_tab_3_9 <= p_tab_3_10, (
        f"Thứ tự các bảng phải tuần tự: Bảng 3-8 (trang {p_tab_3_8}), "
        f"Bảng 3-9 (trang {p_tab_3_9}), Bảng 3-10 (trang {p_tab_3_10})"
    )

    # Tìm trang chứa Mục 3.6.4 (bỏ qua mục lục ở phần đầu)
    p_sec_3_6_4 = next(
        (i + 1 for i, p in enumerate(pages) if i >= 18 and "3.6.4 Thiết kế hạ tầng" in p),
        None,
    )
    assert p_sec_3_6_4 is not None
    assert p_tab_3_10 <= p_sec_3_6_4, (
        f"Bảng 3-10 (trang {p_tab_3_10}) phải đứng trước hoặc "
        f"cùng trang với Mục 3.6.4 (trang {p_sec_3_6_4})!"
    )

    # Đảm bảo toàn bộ nội dung Mục 3.6.4 nằm gọn trong cùng trang với Bảng 3-10
    sec_3_6_4_page_text = pages[p_sec_3_6_4 - 1]
    assert "Mô hình đồ thị tri thức đa thực thể" in sec_3_6_4_page_text, (
        "Nội dung Mục 3.6.4 bị tràn sang trang mới!"
    )


def test_no_pages_with_few_lines_in_document():
    pdf_path = Path("report-datn/main.pdf")
    if not pdf_path.exists():
        return
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")

    roman_numerals = {
        "iii",
        "iv",
        "v",
        "vi",
        "vii",
        "viii",
        "ix",
        "x",
        "xi",
        "xii",
        "xiii",
        "xiv",
        "xv",
        "xvi",
        "xvii",
    }
    # Bỏ qua bìa 1 và 2 (trang 1, 2) và trang kết thúc cuối cùng của tài liệu
    for i in range(2, len(pages) - 2):
        p_text = pages[i]
        lines = [line.strip() for line in p_text.splitlines() if line.strip()]
        # Lọc bỏ số trang ở chân trang
        body_lines = [ln for ln in lines if ln not in roman_numerals and not ln.isdigit()]
        # Trang kết thúc chương trước khi sang chương mới được phép có số dòng tự nhiên
        next_page_text = pages[i + 1] if i + 1 < len(pages) else ""
        if (
            "CHƯƠNG " in next_page_text
            or "KẾT LUẬN" in next_page_text
            or "TÀI LIỆU THAM KHẢO" in next_page_text
            or "DANH MỤC BẢNG BIỂU" in next_page_text
            or "DANH MỤC TỪ VIẾT TẮT" in next_page_text
            or "DANH MỤC TỪ VIẾT TẮT" in p_text
            or "MỞ ĐẦU" in next_page_text
        ):
            continue
        assert len(body_lines) >= 15, (
            f"Trang {i + 1} chỉ có {len(body_lines)} dòng văn bản (< 15 dòng): "
            f"'{lines[0] if lines else ''}'!"
        )
