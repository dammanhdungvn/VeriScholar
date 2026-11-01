import re
from pathlib import Path

def test_preamble():
    content = Path("report-datn/config/preamble.tex").read_text(encoding="utf-8")
    assert "\\textit{\\thepage}" not in content, "Số trang vẫn còn in nghiêng"
    assert "cftsecaftersnum}{.}" not in content, "Mục lục section vẫn còn dấu chấm"
    assert "cftsubsecaftersnum}{.}" not in content, "Mục lục subsection vẫn còn dấu chấm"
    assert "cftchapaftersnum}{:\\" not in content, "Mục lục chapter vẫn còn dấu hai chấm"
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

def test_de_cuong_datn():
    content = Path("report-datn/frontmatter/de_cuong_datn.tex").read_text(encoding="utf-8")
    assert "\\textbf{BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC}" in content, "Tiêu ngữ chưa đúng BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC"
    assert "Bộ môn Hệ thống thông tin và Tri thức" in content or "Bộ môn Hệ thống Thông tin và Tri Thức" in content, "Kế hoạch tuần 10 thiếu tên Bộ môn đầy đủ"
    assert "\\setstretch{1.06}" not in content, "Vẫn còn setstretch{1.06}"
    assert "\\setstretch{1.05}" not in content, "Vẫn còn setstretch{1.05}"
    assert "\\setstretch{1.12}" not in content, "Vẫn còn setstretch{1.12}"
    print("test_de_cuong_datn PASSED")

if __name__ == "__main__":
    test_preamble()
    test_phieu_giao_de_tai()
    test_de_cuong_datn()
