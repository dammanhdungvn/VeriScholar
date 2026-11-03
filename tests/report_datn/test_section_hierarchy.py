import re
from pathlib import Path

CH4_DIR = Path("report-datn/chapters/ch4")


def _get_clean_lines(file_path: Path) -> list[str]:
    lines = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        clean_line = re.sub(r"(?<!\\)%.*$", "", line)
        lines.append(clean_line)
    return lines


def _extract_headings(file_path: Path) -> list[tuple[str, str]]:
    text = "\n".join(_get_clean_lines(file_path))
    pattern = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]+)\}")
    return pattern.findall(text)


def test_ch4_no_singleton_subsections():
    r"""Kiểm tra quy tắc cấm tiểu mục đơn lẻ (No Singleton Subsections) trong toàn bộ Chương 4.
    - Mỗi \section nếu có \subsection con thì bắt buộc phải có ít nhất 2 \subsection.
    - Mỗi \subsection nếu có \subsubsection con thì bắt buộc phải có ít nhất 2 \subsubsection.
    """
    ch4_files = sorted(CH4_DIR.glob("4_*_*.tex"))
    assert len(ch4_files) >= 4, f"Thiếu tệp Chương 4: tìm thấy {len(ch4_files)} tệp"

    # Xây dựng cây đề mục từ các tệp trong Chương 4
    all_headings: list[tuple[str, str, Path]] = []
    for f in ch4_files:
        for level, title in _extract_headings(f):
            all_headings.append((level, title, f))

    # Duyệt kiểm tra không có singleton
    current_section = None
    subsections_under_section: list[str] = []
    current_subsection = None
    subsubsections_under_subsection: list[str] = []

    def check_subsections(sec_title: str | None, subs: list[str]):
        if sec_title is not None and len(subs) == 1:
            msg = (
                f"Lỗi Singleton Subsection tại Section '{sec_title}': "
                f"chỉ có 1 subsection '{subs[0]}'!"
            )
            raise AssertionError(msg)

    def check_subsubsections(sub_title: str | None, subsubs: list[str]):
        if sub_title is not None and len(subsubs) == 1:
            msg = (
                f"Lỗi Singleton Subsubsection tại Subsection '{sub_title}': "
                f"chỉ có 1 subsubsection '{subsubs[0]}'!"
            )
            raise AssertionError(msg)

    for level, title, _ in all_headings:
        if level == "section":
            check_subsubsections(current_subsection, subsubsections_under_subsection)
            check_subsections(current_section, subsections_under_section)
            current_section = title
            subsections_under_section = []
            current_subsection = None
            subsubsections_under_subsection = []
        elif level == "subsection":
            check_subsubsections(current_subsection, subsubsections_under_subsection)
            subsections_under_section.append(title)
            current_subsection = title
            subsubsections_under_subsection = []
        elif level == "subsubsection":
            subsubsections_under_subsection.append(title)

    # Kiểm tra nhóm cuối cùng
    check_subsubsections(current_subsection, subsubsections_under_subsection)
    check_subsections(current_section, subsections_under_section)


def test_ch4_section_4_2_restructuring_and_no_banned_phrases():
    r"""Kiểm tra Mục 4.2 (4_2_giao_dien.tex):
    - Đã nâng cấp các mục con thành 6 \subsection tương ứng với 6 giao diện chính.
    - Không còn \subsubsection đơn lẻ hay cấp lồng thừa thãi.
    - Tuyệt đối không chứa từ cấm 'dưới đây'.
    """
    file_4_2 = CH4_DIR / "4_2_giao_dien.tex"
    assert file_4_2.exists(), "Tệp 4_2_giao_dien.tex không tồn tại"
    content = file_4_2.read_text(encoding="utf-8")

    # Kiểm tra từ cấm
    assert "dưới đây" not in content, "Tệp 4_2_giao_dien.tex vẫn còn từ cấm 'dưới đây'!"

    headings = _extract_headings(file_4_2)
    subsections = [title for level, title in headings if level == "subsection"]
    subsubsections = [title for level, title in headings if level == "subsubsection"]

    assert len(subsections) == 6, (
        f"Mục 4.2 phải có đúng 6 \\subsection, hiện tại có {len(subsections)}: {subsections}"
    )
    assert len(subsubsections) == 0, (
        f"Mục 4.2 không được giữ \\subsubsection, "
        f"hiện tại có {len(subsubsections)}: {subsubsections}"
    )


def test_ch4_section_4_3_two_balanced_subsections():
    r"""Kiểm tra Mục 4.3 (4_3_kiem_thu.tex):
    - Có 2 \subsection cân đối: 4.3.1 (kịch bản kiểm thử)
      và 4.3.2 (đánh giá kết quả kiểm thử và độ tin cậy).
    - Có chứa bảng 4 cổng xác minh.
    """
    file_4_3 = CH4_DIR / "4_3_kiem_thu.tex"
    assert file_4_3.exists(), "Tệp 4_3_kiem_thu.tex không tồn tại"

    headings = _extract_headings(file_4_3)
    subsections = [title for level, title in headings if level == "subsection"]

    assert len(subsections) == 2, (
        f"Mục 4.3 phải có đúng 2 \\subsection, hiện tại có {len(subsections)}: {subsections}"
    )
    assert "Kịch bản kiểm thử" in subsections[0], (
        f"Tiểu mục 4.3.1 phải là kịch bản kiểm thử, hiện tại là: '{subsections[0]}'"
    )
    assert "Đánh giá kết quả kiểm thử" in subsections[1], (
        f"Tiểu mục 4.3.2 phải là đánh giá kết quả kiểm thử, hiện tại là: '{subsections[1]}'"
    )
