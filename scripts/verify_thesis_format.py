import subprocess
from pathlib import Path


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

    # Không có dấu hai chấm sau CHƯƠNG
    assert "CHƯƠNG 1:" not in toc_text, "Mục lục vẫn còn dấu hai chấm sau CHƯƠNG 1"
    assert "CHƯƠNG 2:" not in toc_text, "Mục lục vẫn còn dấu hai chấm sau CHƯƠNG 2"
    assert "CHƯƠNG 3:" not in toc_text, "Mục lục vẫn còn dấu hai chấm sau CHƯƠNG 3"
    assert "CHƯƠNG 4:" not in toc_text, "Mục lục vẫn còn dấu hai chấm sau CHƯƠNG 4"

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

    # Trang 3, 4: Phiếu giao đề tài (iii, iv) - Bố cục 2 trang liền mạch, không khoảng trắng thừa
    assert "PHIẾU GIAO ĐỀ TÀI TỐT NGHIỆP" in pages[2], (
        "Trang 3 không phải trang 1 của Phiếu giao đề tài"
    )
    assert "Lời cam đoan của sinh viên" in pages[3], "Trang 4 không chứa Lời cam đoan (trang iv)"
    assert "iii" in pages[2].strip().splitlines()[-1], (
        f"Trang 3 chân trang không phải iii: {pages[2].strip().splitlines()[-1]}"
    )
    assert "iv" in pages[3].strip().splitlines()[-1], (
        f"Trang 4 chân trang không phải iv: {pages[3].strip().splitlines()[-1]}"
    )

    # Trang 5, 6, 7: Đề cương ĐATN (v, vi, vii)
    assert "ĐỀ CƯƠNG ĐỒ ÁN TỐT NGHIỆP ĐẠI HỌC" in pages[4], (
        "Trang 5 không phải trang 1 của Đề cương"
    )
    assert "Nơi thực hiện đồ án:" in pages[6], "Trang 7 không phải trang cuối của Đề cương"
    assert "v" in pages[4].strip().splitlines()[-1], (
        f"Trang 5 chân trang không phải v: {pages[4].strip().splitlines()[-1]}"
    )
    assert "vi" in pages[5].strip().splitlines()[-1], (
        f"Trang 6 chân trang không phải vi: {pages[5].strip().splitlines()[-1]}"
    )
    assert "vii" in pages[6].strip().splitlines()[-1], (
        f"Trang 7 chân trang không phải vii: {pages[6].strip().splitlines()[-1]}"
    )

    # Trang 8: Lời cảm ơn (viii)
    assert "LỜI CẢM ƠN" in pages[7], "Trang 8 không phải Lời cảm ơn"
    assert "viii" in pages[7].strip().splitlines()[-1], (
        f"Trang 8 chân trang không phải viii: {pages[7].strip().splitlines()[-1]}"
    )

    # Trang 9: Mục lục (ix)
    assert "MỤC LỤC" in pages[8], "Trang 9 không phải Mục lục"
    assert "ix" in pages[8].strip().splitlines()[-1], (
        f"Trang 9 chân trang không phải ix: {pages[8].strip().splitlines()[-1]}"
    )

    # Chương 1 bắt đầu bằng số trang 1 Ả Rập
    ch1_idx = next(
        (i for i, p in enumerate(pages) if "CHƯƠNG 1" in p and p.strip().splitlines()[-1] == "1"),
        None,
    )
    assert ch1_idx is not None, "Không tìm thấy trang bắt đầu Chương 1 (số trang 1) trong PDF"
    assert "TỔNG QUAN VỀ ĐỀ TÀI" in pages[ch1_idx], (
        f"Trang {ch1_idx + 1} không chứa tiêu đề Chương 1"
    )

    print(
        "test_page_budget PASSED (Phiếu giao: iii-iv; Đề cương: v-vii; Lời cảm ơn: viii; Mục lục: ix; Chương 1: 1)"
    )


if __name__ == "__main__":
    test_no_headers_and_footers()
    test_toc_levels_in_pdf()
    test_lof_lot_format()
    test_page_budget()
    print("ALL 4 CRITICAL ACCEPTANCE CHECKS PASSED 100%!")
