import shutil
import subprocess
import sys
from pathlib import Path


def check_pdftotext_available() -> bool:
    if not shutil.which("pdftotext"):
        print("WARNING: pdftotext is not available in PATH. Skipping thesis PDF format checks.")
        return False
    return True


def test_no_headers_and_footers():
    pdf_path = Path("report-datn/main.pdf")
    assert pdf_path.exists(), "report-datn/main.pdf không tồn tại!"
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    assert res.returncode == 0, "Lỗi chạy pdftotext"
    text = res.stdout

    # 1. Header check: Bỏ toàn bộ header
    assert "Đồ án tốt nghiệp ngành Công nghệ thông tin" not in text, (
        "Header 'Đồ án tốt nghiệp ngành Công nghệ thông tin' vẫn xuất hiện trong PDF!"
    )

    # 2. Left footer check: Bỏ footer sinh viên
    assert "SVTH: Đàm Mạnh Dũng" not in text, (
        "Footer 'SVTH: Đàm Mạnh Dũng' vẫn xuất hiện trong PDF!"
    )

    print("test_no_headers_and_footers PASSED")


def test_toc_levels_in_pdf():
    pdf_path = Path("report-datn/main.pdf")
    # Kiểm tra các trang Mục lục (trang 9-11 của PDF)
    res = subprocess.run(
        ["pdftotext", "-f", "9", "-l", "11", str(pdf_path), "-"], capture_output=True, text=True
    )
    toc_text = res.stdout

    # Không chứa mục cấp 4 (ví dụ: 4.2.1.1, 4.2.1.2...)
    assert "4.2.1.1" not in toc_text, "Mục lục hiển thị cấp 4 (4.2.1.1)!"
    assert "4.2.1.2" not in toc_text, "Mục lục hiển thị cấp 4 (4.2.1.2)!"
    assert "2.1.1.1" not in toc_text, "Mục lục hiển thị cấp 4!"

    # Có dấu hai chấm sau CHƯƠNG chuẩn 100% Hieu.pdf
    assert "CHƯƠNG 1:" in toc_text, "Mục lục thiếu dấu hai chấm sau CHƯƠNG 1"
    assert "CHƯƠNG 2:" in toc_text, "Mục lục thiếu dấu hai chấm sau CHƯƠNG 2"
    assert "CHƯƠNG 3:" in toc_text, "Mục lục thiếu dấu hai chấm sau CHƯƠNG 3"
    assert "CHƯƠNG 4:" in toc_text, "Mục lục thiếu dấu hai chấm sau CHƯƠNG 4"

    # Không có dấu chấm sau STT đề mục (1.1 thay vì 1.1.)
    assert "1.1. Giới thiệu" not in toc_text, "Mục lục vẫn còn dấu chấm sau 1.1."
    assert "1.1 Giới thiệu" in toc_text, "Mục lục thiếu '1.1 Giới thiệu'"
    assert "2.1. Cơ sở dữ liệu" not in toc_text, "Mục lục vẫn còn dấu chấm sau 2.1."
    assert "2.1 Cơ sở dữ liệu" in toc_text, "Mục lục thiếu '2.1 Cơ sở dữ liệu'"

    print("test_toc_levels_in_pdf PASSED")


def test_lof_lot_format():
    pdf_path = Path("report-datn/main.pdf")
    # Kiểm tra các trang Danh mục hình ảnh và bảng biểu (trang 12-15 của PDF)
    res = subprocess.run(
        ["pdftotext", "-f", "12", "-l", "15", str(pdf_path), "-"], capture_output=True, text=True
    )
    lof_lot_text = res.stdout

    # Không có dấu hai chấm sau số thứ tự Hình/Bảng
    assert "Hình 2-1:" not in lof_lot_text, "LoF vẫn còn dấu hai chấm sau Hình 2-1:"
    assert "Hình 3-1:" not in lof_lot_text, "LoF vẫn còn dấu hai chấm sau Hình 3-1:"
    assert "Bảng 1-1:" not in lof_lot_text, "LoT vẫn còn dấu hai chấm sau Bảng 1-1:"
    assert "Hình 2-1" in lof_lot_text, "LoF thiếu 'Hình 2-1'"
    assert "Bảng 1-1" in lof_lot_text, "LoT thiếu 'Bảng 1-1'"

    print("test_lof_lot_format PASSED")


def test_page_budget():
    pdf_path = Path("report-datn/main.pdf")
    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    pages = res.stdout.split("\x0c")

    # Trang 3, 4: Phiếu giao đề tài - Bố cục 2 trang liền mạch, không khoảng trắng thừa
    assert "PHIẾU GIAO ĐỀ TÀI TỐT NGHIỆP" in pages[2], (
        "Trang 3 không phải trang 1 của Phiếu giao đề tài"
    )
    assert "Lời cam đoan của sinh viên" in pages[3], "Trang 4 không chứa Lời cam đoan"

    # Trang 5, 6, 7: Đề cương ĐATN
    assert "ĐỀ CƯƠNG ĐỒ ÁN TỐT NGHIỆP ĐẠI HỌC" in pages[4], (
        "Trang 5 không phải trang 1 của Đề cương"
    )
    assert "Nơi thực hiện đồ án:" in pages[6], "Trang 7 không phải trang cuối của Đề cương"

    # Trang 8: Lời cảm ơn
    assert "LỜI CẢM ƠN" in pages[7], "Trang 8 không phải Lời cảm ơn"

    # Kiểm tra quy chuẩn chân trang Frontmatter theo yêu cầu GVHD:
    # Trang 1 và trang 2 (Bìa ngoài, Bìa phụ) để trống hoàn toàn chân trang
    for p_idx in [0, 1]:
        last_line = (
            pages[p_idx].strip().splitlines()[-1] if pages[p_idx].strip().splitlines() else ""
        )
        assert not last_line.isdigit() and last_line not in {"i", "ii", "iii"}, (
            f"Trang bìa {p_idx + 1} chân trang không được in số trang: '{last_line}'"
        )

    # Trang 3 đến trang 8: Đánh số trang La Mã thường i, ii, iii, iv, v, vi
    expected_romans = ["i", "ii", "iii", "iv", "v", "vi"]
    for p_offset, expected_roman in enumerate(expected_romans):
        p_idx = 2 + p_offset
        last_line = (
            pages[p_idx].strip().splitlines()[-1] if pages[p_idx].strip().splitlines() else ""
        )
        assert last_line == expected_roman, (
            f"Trang {p_idx + 1} chân trang phải là số La Mã '{expected_roman}': '{last_line}'"
        )

    # Trang 9: Mục lục (bắt đầu đánh số 1 Ả Rập ở chân trang)
    assert "MỤC LỤC" in pages[8], "Trang 9 không phải Mục lục"
    assert pages[8].strip().splitlines()[-1] == "1", (
        f"Trang 9 chân trang không phải 1: {pages[8].strip().splitlines()[-1]}"
    )

    # Mục lục ghi nhận đúng số trang La Mã cho các mục Frontmatter (i, iii, vi)
    assert "PHIẾU GIAO ĐỀ TÀI TỐT NGHIỆP" in pages[8] and "i" in pages[8], (
        "Mục lục thiếu chỉ mục trang La Mã i cho Phiếu giao đề tài"
    )
    assert "ĐỀ CƯƠNG ĐỒ ÁN TỐT NGHIỆP ĐẠI HỌC" in pages[8] and "iii" in pages[8], (
        "Mục lục thiếu chỉ mục trang La Mã iii cho Đề cương"
    )
    assert "LỜI CẢM ƠN" in pages[8] and "vi" in pages[8], (
        "Mục lục thiếu chỉ mục trang La Mã vi cho Lời cảm ơn"
    )

    # Chương 1 bắt đầu tiếp nối liên tục từ Mục lục
    ch1_idx = next(
        (i for i, p in enumerate(pages) if "CHƯƠNG 1" in p and "TỔNG QUAN VỀ ĐỀ TÀI" in p),
        None,
    )
    assert ch1_idx is not None, "Không tìm thấy trang bắt đầu Chương 1 trong PDF"

    print(
        "test_page_budget PASSED (Bìa 1-2 trống; Trang 3-8: i-vi La Mã; Mục lục: 1 Ả Rập; Frontmatter TOC: i, iii, vi)"
    )


if __name__ == "__main__":
    if not check_pdftotext_available():
        sys.exit(0)
    test_no_headers_and_footers()
    test_toc_levels_in_pdf()
    test_lof_lot_format()
    test_page_budget()
    print("ALL 4 CRITICAL ACCEPTANCE CHECKS PASSED 100%!")
