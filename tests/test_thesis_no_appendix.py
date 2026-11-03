from pathlib import Path


def test_no_appendix_in_main_and_filesystem():
    main_tex = Path("report-datn/main.tex").read_text(encoding="utf-8")
    assert "\\input{chapters/phu_luc}" not in main_tex
    assert "PHỤ LỤC" not in main_tex
    assert not Path("report-datn/chapters/phu_luc.tex").exists()


def test_no_broken_appendix_references():
    csdl_tex = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex").read_text(encoding="utf-8")
    assert "Phụ lục A" not in csdl_tex
    assert "Phụ lục~A" not in csdl_tex
