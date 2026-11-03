from pathlib import Path


def test_loi_mo_dau_included_in_main():
    r"""Kiểm tra tệp frontmatter/loi_mo_dau được nạp vào main.tex đúng vị trí:
    1. Tệp frontmatter/loi_mo_dau.tex tồn tại.
    2. main.tex có dòng \input{frontmatter/loi_mo_dau}.
    3. Nằm trong phần Frontmatter: sau \input{frontmatter/danh_muc_viet_tat}
       và trước \pagenumbering{arabic}.
    """
    main_tex_path = Path("report-datn/main.tex")
    loi_mo_dau_path = Path("report-datn/frontmatter/loi_mo_dau.tex")

    assert loi_mo_dau_path.exists(), "Tệp frontmatter/loi_mo_dau.tex không tồn tại!"
    assert main_tex_path.exists(), "Tệp report-datn/main.tex không tồn tại!"

    content = main_tex_path.read_text(encoding="utf-8")

    input_pattern = r"\input{frontmatter/loi_mo_dau}"
    assert input_pattern in content, r"main.tex chưa nạp \input{frontmatter/loi_mo_dau}!"

    pos_loi_mo_dau = content.find(input_pattern)
    pos_danh_muc_viet_tat = content.find(r"\input{frontmatter/danh_muc_viet_tat}")
    pos_arabic = content.find(r"\pagenumbering{arabic}")

    assert pos_danh_muc_viet_tat != -1, (
        r"Không tìm thấy \input{frontmatter/danh_muc_viet_tat} trong main.tex"
    )
    assert pos_arabic != -1, r"Không tìm thấy \pagenumbering{arabic} trong main.tex"

    assert pos_danh_muc_viet_tat < pos_loi_mo_dau, (
        r"\input{frontmatter/loi_mo_dau} phải đứng sau \input{frontmatter/danh_muc_viet_tat}"
    )
    assert pos_loi_mo_dau < pos_arabic, (
        r"\input{frontmatter/loi_mo_dau} phải nằm trong Frontmatter (trước \pagenumbering{arabic})"
    )


def test_loi_mo_dau_added_to_toc():
    r"""Kiểm tra tệp frontmatter/loi_mo_dau.tex có khai báo
    \addcontentsline{toc}{chapter}{LỜI MỞ ĐẦU} ngay sau \chapter*{LỜI MỞ ĐẦU}
    để xuất hiện trong Mục lục luận văn."""
    loi_mo_dau_path = Path("report-datn/frontmatter/loi_mo_dau.tex")
    assert loi_mo_dau_path.exists(), "Tệp frontmatter/loi_mo_dau.tex không tồn tại!"

    content = loi_mo_dau_path.read_text(encoding="utf-8")
    toc_entry = r"\addcontentsline{toc}{chapter}{LỜI MỞ ĐẦU}"
    assert toc_entry in content, (
        r"frontmatter/loi_mo_dau.tex chưa có \addcontentsline{toc}{chapter}{LỜI MỞ ĐẦU}!"
    )
