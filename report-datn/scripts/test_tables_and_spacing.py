import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "chapters"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
FRONTMATTER_DIR = Path(__file__).resolve().parent.parent / "frontmatter"
MAIN_TEX = Path(__file__).resolve().parent.parent / "main.tex"


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


def test_no_reduced_font_in_tables():
    """Đảm bảo toàn bộ 17 bảng trong chapters/ dùng font 13pt chuẩn Word,
    tuyệt đối không có lệnh thu nhỏ cỡ chữ (\\small, \\footnotesize, \\scriptsize,
    \\fontsize{10pt}, \\fontsize{11pt}) bên trong môi trường table, tabularx, hoặc xltabular."""
    forbidden_font_patterns = [
        (r"\\small\b", "\\small"),
        (r"\\footnotesize\b", "\\footnotesize"),
        (r"\\scriptsize\b", "\\scriptsize"),
        (r"\\tiny\b", "\\tiny"),
        (r"\\fontsize\{10pt\}", "\\fontsize{10pt}"),
        (r"\\fontsize\{11pt\}", "\\fontsize{11pt}"),
        (r"\\fontsize\{(?:[0-9]|1[0-2])(?:\.[0-9]+)?pt\}", "\\fontsize{<13pt}"),
    ]

    table_count = 0
    for tex_file in CHAPTERS_DIR.glob("**/*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        matches = list(
            re.finditer(
                r"\\begin\{(?:table\*?|xltabular)\}(.*?)\\end\{(?:table\*?|xltabular)\}",
                content,
                re.DOTALL,
            )
        )
        for m in matches:
            table_count += 1
            tbl_block = m.group(1)
            for pattern, name in forbidden_font_patterns:
                found = re.findall(pattern, tbl_block)
                assert not found, f"Phát hiện hạ cỡ chữ {name} trong {tex_file.name}: {found}"

    assert table_count == 17, f"Kỳ vọng 17 bảng trong chapters/, thực tế tìm thấy {table_count}"


def test_arabic_page_numbering_starts_at_muc_luc():
    """Đảm bảo số trang Ả Rập (Trang 1) bắt đầu chính xác từ phần MỤC LỤC,
    các trang trước Mục lục dùng La Mã, và Chương 1 tiếp nối liên tục."""
    content = MAIN_TEX.read_text(encoding="utf-8")

    assert "\\pagenumbering{roman}" in content, (
        "Thiếu \\pagenumbering{roman} cho phần hồ sơ đầu đồ án"
    )

    idx_arabic = content.find(r"\pagenumbering{arabic}")
    idx_page_1 = content.find(r"\setcounter{page}{1}")
    idx_muc_luc = content.find(r"\input{frontmatter/muc_luc}")

    assert idx_arabic != -1, "Không tìm thấy \\pagenumbering{arabic} trong main.tex"
    assert idx_page_1 != -1, "Không tìm thấy \\setcounter{page}{1} trong main.tex"
    assert idx_muc_luc != -1, "Không tìm thấy \\input{frontmatter/muc_luc} trong main.tex"

    assert idx_arabic < idx_muc_luc, (
        "\\pagenumbering{arabic} phải đứng trước \\input{frontmatter/muc_luc}"
    )
    assert idx_page_1 < idx_muc_luc, (
        "\\setcounter{page}{1} phải đứng trước \\input{frontmatter/muc_luc}"
    )
    assert idx_arabic < idx_page_1, (
        "\\pagenumbering{arabic} phải đứng trước hoặc cùng khối với \\setcounter{page}{1}"
    )

    intermediate = content[idx_arabic:idx_muc_luc]
    assert "\\setcounter{page}{1}" in intermediate, (
        "\\setcounter{page}{1} phải nằm giữa \\pagenumbering{arabic} và Mục lục"
    )


def test_all_tables_have_valid_arraystretch():
    """Đảm bảo toàn bộ 17 bảng trong chapters/ đều có \\arraystretch >= 1.20."""
    table_stretches = []
    for tex_file in CHAPTERS_DIR.glob("**/*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if r"\begin{table" in line or r"\begin{xltabular" in line:
                stretch_val = None
                for scan_idx in range(max(0, idx - 15), min(len(lines), idx + 10)):
                    m = re.search(
                        r"\\(?:renewcommand\{\\arraystretch\}|def\\arraystretch)\{([0-9\.]+)\}",
                        lines[scan_idx],
                    )
                    if m:
                        stretch_val = float(m.group(1))
                        break
                assert stretch_val is not None, (
                    f"Không tìm thấy \\arraystretch cho bảng dòng {idx + 1} trong {tex_file.name}"
                )
                assert stretch_val >= 1.20, (
                    f"Bảng dòng {idx + 1} trong {tex_file.name} có "
                    f"\\arraystretch={stretch_val} < 1.20"
                )
                table_stretches.append((tex_file.name, idx + 1, stretch_val))

    assert len(table_stretches) == 17, (
        f"Kỳ vọng 17 bảng, thực tế kiểm tra được {len(table_stretches)}"
    )


def test_casual_inline_bolds():
    """Đảm bảo không có in đậm tùy tiện trong văn xuôi các chương, giữ văn phong học thuật phẳng."""
    findings = []
    for tex_file in sorted(CHAPTERS_DIR.rglob("*.tex")):
        lines = tex_file.read_text(encoding="utf-8").splitlines()
        in_table = False
        in_tikz = False
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if (
                "\\begin{tabular" in stripped
                or "\\begin{table" in stripped
                or "\\begin{xltabular" in stripped
            ):
                in_table = True
            if (
                "\\end{tabular" in stripped
                or "\\end{table" in stripped
                or "\\end{xltabular" in stripped
            ):
                in_table = False
                continue
            if in_table:
                continue

            if "\\begin{tikzpicture}" in stripped:
                in_tikz = True
            if "\\end{tikzpicture}" in stripped:
                in_tikz = False
                continue
            if in_tikz:
                continue

            if stripped.startswith("%"):
                continue

            matches = list(re.finditer(r"\\textbf\{([^{}]+(?:\{[^{}]*\}[^{}]*)*)\}", line))
            for m in matches:
                span_start = m.start()
                prefix = line[:span_start].strip()
                if (
                    prefix.endswith("\\item")
                    or prefix.endswith("\\item[]")
                    or prefix.endswith("\\item[--]")
                    or prefix.endswith("\\item[-]")
                    or prefix == ""
                    or prefix.endswith("\\noindent")
                ):
                    continue
                if "label=\\textbf{" in line:
                    continue
                if "caption" in prefix or "titleformat" in prefix:
                    continue

                findings.append(f"{tex_file.name}:{idx}: {m.group(0)}")

    assert len(findings) == 0, (
        f"Phát hiện {len(findings)} lỗi in đậm tùy tiện trong văn xuôi:\n" + "\n".join(findings)
    )
