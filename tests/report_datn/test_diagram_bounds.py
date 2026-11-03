from pathlib import Path


def test_fig3_2_coordinates_within_safe_margins():
    tex_path = Path("report-datn/chapters/ch3/3_3_kien_truc.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra scale đã giảm về <= 0.68 (0.65 để an toàn tuyệt đối cách lề >= 5mm)
    assert "scale=0.65" in content or "scale=0.68" in content, (
        "Hình 3-2 phải sử dụng scale <= 0.68 để vừa vặn lề in textwidth=16cm"
    )

    # Kiểm tra chiều rộng portbox đã thu nhỏ <= 2.2cm để tạo khe hở cho thân mũi tên
    assert "minimum width=2.1cm" in content or "minimum width=2.0cm" in content, (
        "Cần thu hẹp portbox về <= 2.1cm để tạo khoảng trống cho thân mũi tên -->"
    )

    # Kiểm tra tọa độ nới rộng: Adapter tại +- 9.2 và Port tại +- 6.1, Core tại +- 4.4
    assert "(9.2," in content, "Thiếu tọa độ x=9.2 cho Driven Adapter để tạo khe hở thân mũi tên"
    assert "(-9.2," in content, "Thiếu tọa độ x=-9.2 cho Driving Adapter để tạo khe hở thân mũi tên"
    assert "(6.1," in content, "Thiếu tọa độ x=6.1 cho Driven Port"
    assert "(-6.1," in content, "Thiếu tọa độ x=-6.1 cho Driving Port"
    assert "(-4.4," in content and "(4.4," in content, "Khung Core domain cần điều chỉnh x=+-4.4"

    # Kiểm tra đáy Core domain có text width khống chế không chọc thủng viền
    assert "text width=7.8cm" in content or "text width=8.0cm" in content, (
        "Cần text width khống chế khung nghiệp vụ đáy Core domain không đâm thủng viền"
    )
    assert "E2B MicroVM Sandbox" in content, (
        "Cần dùng nhãn ngắt gọn trong Sandbox Adapter để tránh đầu mũi tên đè chữ"
    )


def test_fig2_4_loop_and_label_styling():
    tex_path = Path("report-datn/chapters/ch2/2_5_agentic_react.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra cung tròn vòng lặp đỏ không vồng quá cao
    assert "to[out=110, in=250]" in content or "to[out=115, in=245]" in content, (
        "Cung lặp đỏ cần dùng out=110, in=250 để không vượt quá đỉnh hộp agent"
    )

    # Kiểm tra nhãn rẽ nhánh có padding và fill=white
    assert "inner sep=2pt" in content, (
        "Nhãn rẽ nhánh hình thoi cần inner sep=2pt để không dính nét vẽ hình thoi"
    )

    # Kiểm tra có đệm vspace trước caption
    assert "\\vspace{4pt}" in content or "\\vspace{6pt}" in content, (
        "Cần vspace trước caption để tránh đáy hộp PDF dính sát caption"
    )

    # Kiểm tra hộp final answer được dời xuống thấp để có đủ khoảng hở cho mũi tên thẳng đứng
    assert "(final) at (0, -4.5)" in content or "(final) at (0, -4.4)" in content, (
        "Hộp final answer cần đặt tại y <= -4.4 để tạo khe hở >= 10mm cho mũi tên Yes"
    )

    # Kiểm tra nhãn Yes (Exit 0) đặt lệch sườn phải không đè lên mũi tên hay viền hộp
    assert "Yes (Exit 0)" in content and ("right=10pt" in content or "right=8pt" in content), (
        "Nhãn Yes (Exit 0) cần đặt lệch phải (right=10pt) để thoáng đãng không đè nét"
    )


def test_fig3_12_class_diagram_styling():
    tex_path = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra inner sep/ysep đã được tinh gọn để tạo khoảng hở giữa các hộp lớp
    assert (
        "inner sep=2.0pt" in content
        or "inner sep=2.2pt" in content
        or "inner ysep=3.0pt" in content
    ), "Cần giảm inner sep của umlclass để thu hẹp chiều cao hộp lớp"

    # Kiểm tra không còn nhãn đè vào điểm neo south/north không có khoảng lùi an toàn
    assert "yshift=-3.5pt" not in content, (
        "Khoảng lệch yshift=-3.5pt quá nhỏ khiến nhãn đè vào đường phân cách hoặc thân hộp"
    )

    # Kiểm tra đường nối User -> Draft không rơi thẳng đứng cắt xuyên GraphNode và GraphEdge
    assert "-| (draft.north)" not in content, (
        "Đường nối -| (draft.north) cắt xuyên qua GraphNode và GraphEdge!"
    )
    assert "-- (draft.east)" in content, (
        "Đường nối User -> Draft cần đi vòng sườn ngoài kết nối vào draft.east"
    )

    # Kiểm tra hai đầu kim cương tại doc.east được phân tách cao độ
    assert "([yshift=-4pt]doc.east)" in content or "([yshift=4pt]doc.east)" in content, (
        "Cần phân tách cao độ neo tại doc.east để tránh đè 2 đầu kim cương"
    )


def test_sequence_diagrams_spacing_and_float_padding():
    seq_path = Path("report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex")
    seq_content = seq_path.read_text(encoding="utf-8")

    # Kiểm tra cả 4 hình sử dụng style stage_card và stage_arrow
    assert "stage_card" in seq_content, "Các sơ đồ Mục 3.5 phải dùng style stage_card"
    assert "stage_arrow" in seq_content, "Các sơ đồ Mục 3.5 phải dùng style stage_arrow"

    # Kiểm tra không còn lifeline kéo dài quá -10cm
    assert "-- (0, -10.5)" not in seq_content, "Không còn sử dụng lifeline kéo dài gây choán trang"
    assert "-- (0, -10.4)" not in seq_content, "Không còn sử dụng lifeline kéo dài gây choán trang"

    # Kiểm tra cả 4 hình sử dụng định vị [H]
    assert seq_content.count("\\begin{figure}[H]") >= 4, (
        "Cả 4 sơ đồ Mục 3.5 cần sử dụng [H] để định vị chắc chắn, tránh khoảng trống đáy trang"
    )

    # Kiểm tra float spacing trong main.tex được tăng thêm 0.5 dòng (~10pt)
    main_path = Path("report-datn/main.tex")
    main_content = main_path.read_text(encoding="utf-8")
    assert (
        "\\setlength{\\intextsep}{10pt" in main_content
        or "\\setlength{\\intextsep}{11pt" in main_content
        or "\\setlength{\\intextsep}{12pt" in main_content
    ), "Cần tăng \\intextsep lên khoảng 10-12pt để có đệm 0.5 dòng với text"


def test_table_3_5_no_overfull_hbox():
    tex_path = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex")
    content = tex_path.read_text(encoding="utf-8")

    # 1. Kiểm tra Bảng 3-5 có điểm ngắt dòng allowbreak cho chuỗi document_storage_blobs
    assert "\\allowbreak" in content, (
        "Bảng 3-5 cần bổ sung \\allowbreak để ngắt dòng chuỗi định danh dài trong cột 3.2cm"
    )
    expected_pattern = (
        "\\allowbreak\\texttt{document\\_}"
        "\\allowbreak\\texttt{storage\\_}"
        "\\allowbreak\\texttt{blobs}"
        "\\allowbreak\\texttt{(id)}"
    )
    assert expected_pattern in content, (
        "Bảng 3-5 cần phân rã chuỗi document_storage_blobs(id) thành các phần tử ngắt dòng"
    )

    # 2. Kiểm tra nếu log biên dịch tồn tại thì không còn lỗi Overfull \\hbox
    log_path = Path("report-datn/main.log")
    if log_path.exists():
        log_content = log_path.read_text(encoding="utf-8", errors="ignore")
        overfull_found = any(
            "Overfull \\hbox" in block and "document_storage_blobs" in block
            for block in log_content.split("\n\n")
        )
        assert not overfull_found, (
            "File report-datn/main.log vẫn còn Overfull \\hbox với document_storage_blobs"
        )
