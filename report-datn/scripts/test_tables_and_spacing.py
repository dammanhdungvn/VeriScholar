import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "chapters"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
FRONTMATTER_DIR = Path(__file__).resolve().parent.parent / "frontmatter"


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


def test_indentfirst_loaded_in_preamble():
    """Đảm bảo gói indentfirst được nạp trong config/preamble.tex để thụt lề cả đoạn đầu tiên."""
    preamble = CONFIG_DIR / "preamble.tex"
    content = preamble.read_text(encoding="utf-8")
    assert "\\usepackage{indentfirst}" in content, (
        "Thiếu \\usepackage{indentfirst} trong config/preamble.tex"
    )


def test_global_parindent_is_1cm():
    """Đảm bảo thụt lề dòng đầu toàn cục được đặt là 1.0cm."""
    preamble = CONFIG_DIR / "preamble.tex"
    content = preamble.read_text(encoding="utf-8")
    assert "\\setlength{\\parindent}{1.0cm}" in content, (
        "Thiếu \\setlength{\\parindent}{1.0cm} trong config/preamble.tex"
    )


def test_phieu_giao_de_tai_matches_hieu_pdf():
    """Đảm bảo Phiếu giao đề tài khớp 100% mẫu khoa và HIeu.pdf trang 3-4."""
    phieu_file = FRONTMATTER_DIR / "phieu_giao_de_tai.tex"
    content = phieu_file.read_text(encoding="utf-8")

    # Tiêu đề
    assert "PHIẾU GIAO ĐỀ TÀI TỐT NGHIỆP" in content

    # Thông tin chung khớp cấu trúc HIeu.pdf
    assert "Tên đề tài:" in content
    assert "Họ và tên:" in content
    assert "Điện thoại liên lạc:" in content
    assert "Email:" in content
    assert "Lớp:" in content
    assert "Hệ đào tạo:" in content
    assert "Đồ án tốt nghiệp được thực hiện tại:" in content
    assert "Thời gian làm ĐATN:" in content

    # Lời cam đoan
    assert "Em -- Đàm Mạnh Dũng -- cam kết đồ án tốt nghiệp" in content
    assert "cô Vũ Lan Phương" in content
    assert "Hà Nội, ngày 06 tháng 11 năm 2026" in content

    # Khối chữ ký: Xác nhận của GVHD & Tác giả ĐATN
    assert "Xác nhận của GVHD" in content
    assert "Tác giả ĐATN" in content
    assert "(Ký và ghi rõ họ tên)" not in content

    # Không in sẵn tên trong khối chữ ký
    # Tách khối chữ ký sau dòng ngày tháng
    signature_section = content.split("Hà Nội, ngày 06 tháng 11 năm 2026")[-1]
    assert "Đàm Mạnh Dũng" not in signature_section
    assert "Vũ Lan Phương" not in signature_section


def test_de_cuong_datn_structure():
    """Đảm bảo Đề cương ĐATN chuẩn theo mẫu khoa & HIeu.pdf."""
    de_cuong_file = FRONTMATTER_DIR / "de_cuong_datn.tex"
    content = de_cuong_file.read_text(encoding="utf-8")

    # Bảng 1 & 2 dùng tabcolsep = 3.5pt
    assert "\\tabcolsep = 3.5pt" in content or "\\setlength{\\tabcolsep}{3.5pt}" in content

    # Chống tràn email với allowbreak
    assert "\\allowbreak" in content

    # Cột của Bảng 1 và Bảng 2: TT (0.7cm), Mã (2.3cm),
    # Họ tên (2.8cm), Lớp/Đơn vị (2.2cm), SĐT (2.1cm), Email (X)
    assert "m{0.7cm}" in content
    assert "m{2.3cm}" in content
    assert "m{2.8cm}" in content
    assert "m{2.2cm}" in content
    assert "m{2.1cm}" in content

    # Bảng kế hoạch có arraystretch = 1.20 hoặc 1.2
    assert (
        "\\renewcommand{\\arraystretch}{1.20}" in content
        or "\\renewcommand{\\arraystretch}{1.2}" in content
    )
    assert "\\renewcommand{\\arraystretch}{1.0}" not in content

    # Mục 8 là mục cuối cùng, không có bảng chữ ký hay ngày tháng ở cuối
    after_sec_8 = content.split("8. Nơi thực hiện đồ án:")[-1]
    assert "Xác nhận của GVHD" not in after_sec_8
    assert "Giảng viên hướng dẫn" not in after_sec_8
    assert "Sinh viên thực hiện" not in after_sec_8
    assert "ngày" not in after_sec_8


def test_no_singlespace_in_frontmatter():
    """Đảm bảo không còn môi trường singlespace nào trong toàn bộ thư mục frontmatter."""
    for tex_file in FRONTMATTER_DIR.glob("**/*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        assert "singlespace" not in content, (
            f"Phát hiện môi trường singlespace trong frontmatter: {tex_file.name}"
        )


def test_usecase_continuation_headers_13pt():
    """Đảm bảo các continuation header Bảng 3-X (tiếp theo) không bị hạ cỡ chữ xuống 11pt."""
    usecase_file = CHAPTERS_DIR / "ch3" / "3_4_phan_tich_usecase.tex"
    content = usecase_file.read_text(encoding="utf-8")
    assert "\\fontsize{11pt}" not in content, (
        "Phát hiện \\fontsize{11pt} trong chapters/ch3/3_4_phan_tich_usecase.tex"
    )
