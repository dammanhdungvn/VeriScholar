from pathlib import Path


def test_preamble():
    content = Path("report-datn/config/preamble.tex").read_text(encoding="utf-8")
    assert "\\textit{\\thepage}" not in content, "Số trang vẫn còn in nghiêng"
    assert "cftsecaftersnum}{.}" not in content, "Mục lục section vẫn còn dấu chấm"
    assert "cftsubsecaftersnum}{.}" not in content, "Mục lục subsection vẫn còn dấu chấm"
    assert "cftchapaftersnum}{:\\" in content, "Mục lục chapter phải có dấu hai chấm theo chuẩn Hieu.pdf"
    assert "cftchapfont}{\\normalfont" in content, "Mục lục chapter không được in đậm theo chuẩn Hieu.pdf"
    assert "cfttabpresnum}{\\bfseries" not in content, "LoT chữ Bảng vẫn còn in đậm"
    assert "cftfigpresnum}{\\bfseries" not in content, "LoF chữ Hình vẫn còn in đậm"
    assert "tocdepth}{2}" in content, "tocdepth phải là 2"
    assert "Đồ án tốt nghiệp ngành Công nghệ thông tin" not in content, "Header cũ vẫn tồn tại"
    print("test_preamble PASSED")


def test_phieu_giao_de_tai():
    content = Path("report-datn/frontmatter/phieu_giao_de_tai.tex").read_text(encoding="utf-8")
    assert "\\begin{enumerate}" not in content, "Vẫn còn enumerate trong phiếu giao đề tài"
    assert "cụ thể sau:" in content, "Thiếu câu dẫn nhiệm vụ cụ thể sau:"
    assert "\nsau:\n" not in content, "Chữ 'sau:' vẫn bị rơi đơn độc một dòng"
    assert "\\setstretch{1.10}" not in content, "Vẫn còn ép giãn dòng setstretch{1.10}"
    assert "\\item[--]" in content, "Thiếu gạch đầu dòng item[--] cho nhiệm vụ cụ thể"
    print("test_phieu_giao_de_tai PASSED")


def test_ket_luan_spacing():
    content = Path("report-datn/chapters/ket_luan.tex").read_text(encoding="utf-8")
    assert "\\setstretch" not in content, "Vẫn còn lệnh setstretch trong ket_luan.tex"
    print("test_ket_luan_spacing PASSED")


def test_de_cuong_datn():
    content = Path("report-datn/frontmatter/de_cuong_datn.tex").read_text(encoding="utf-8")
    assert "\\textbf{BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC}" in content, (
        "Tiêu ngữ chưa đúng BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC"
    )
    assert "Bộ môn Hệ thống thông tin và Tri thức" in content, (
        "Kế hoạch tuần 10 thiếu tên Bộ môn đầy đủ chuẩn chính tả"
    )
    assert "\\setstretch{1.06}" not in content, "Vẫn còn setstretch{1.06}"
    assert "\\setstretch{1.05}" not in content, "Vẫn còn setstretch{1.05}"
    assert "\\setstretch{1.12}" not in content, "Vẫn còn setstretch{1.12}"
    print("test_de_cuong_datn PASSED")


def test_frontmatter_bolds():
    cam_on = Path("report-datn/frontmatter/loi_cam_on.tex").read_text(encoding="utf-8")
    assert "\\textbf{Vũ Lan Phương}" not in cam_on, "Tên GVHD trong lời cảm ơn vẫn bị in đậm"
    assert "\\textbf{VeriScholar}" not in cam_on, "Tên VeriScholar trong lời cảm ơn vẫn bị in đậm"
    assert "Bộ môn Hệ thống thông tin và Tri thức" in cam_on, (
        "Tên Bộ môn trong lời cảm ơn chưa chuẩn"
    )

    mo_dau = Path("report-datn/frontmatter/loi_mo_dau.tex").read_text(encoding="utf-8")
    assert "\\textbf{hiện tượng ảo giác" not in mo_dau, (
        "Cụm hiện tượng ảo giác trong lời mở đầu vẫn bị in đậm"
    )
    print("test_frontmatter_bolds PASSED")


if __name__ == "__main__":
    test_preamble()
    test_phieu_giao_de_tai()
    test_de_cuong_datn()
    test_frontmatter_bolds()
    test_ket_luan_spacing()
    from scan_inline_bolds import find_casual_bolds

    assert len(find_casual_bolds()) == 0, "Vẫn còn casual inline bolds trong chapters"
    print("test_chapters_bolds PASSED")
