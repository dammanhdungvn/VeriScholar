from pathlib import Path


def test_preamble_configuration():
    preamble_path = Path("report-datn/config/preamble.tex")
    assert preamble_path.exists()
    content = preamble_path.read_text(encoding="utf-8")

    # Kiểm tra các thông số quy chuẩn HUMG
    assert "top=2.5cm" in content
    assert "bottom=2.5cm" in content
    assert "left=3.5cm" in content
    assert "right=2.5cm" in content
    assert "fontsize=13pt" in content
    assert "Times New Roman" in content
    assert "Đàm Mạnh Dũng" in content
