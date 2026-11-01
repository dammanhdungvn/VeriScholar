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

if __name__ == "__main__":
    test_preamble()
