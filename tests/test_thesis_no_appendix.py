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


def test_csdl_structure_streamlined():
    csdl_tex = Path("report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex").read_text(encoding="utf-8")
    assert "\\label{fig:erd_auth_storage_session}" not in csdl_tex
    assert "\\label{fig:erd_graph_draft}" not in csdl_tex
    assert "\\label{fig:erd_model}" not in csdl_tex
    assert "\\label{tab:db_tables_summary}" not in csdl_tex
    assert "\\label{tab:spec_documents}" in csdl_tex
    assert "\\label{tab:spec_chunks}" in csdl_tex
    assert "\\label{tab:spec_graph_nodes}" in csdl_tex
    assert "\\label{tab:spec_drafts}" in csdl_tex
    assert "research_sessions(id)" in csdl_tex
    assert "document\\_storage\\_blobs(id)" in csdl_tex


def test_tikz_diagram_spacing_refinements():
    # 1. Hình 3-5 Use Case con: khoảng cách dọc không được hẹp 0.75
    uc_tex = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex").read_text(encoding="utf-8")
    assert "(11.5, 0.75)" not in uc_tex

    # 2. Hình 2-4 ReAct: nhãn Yes không được đặt đè sát mũi tên nhọn
    react_tex = Path("report-datn/chapters/ch2/2_5_agentic_react.tex").read_text(encoding="utf-8")
    assert "node[midway, right=6pt" not in react_tex

    # 3. Hình 3-2 Lục giác: scale không được quá bé 0.58
    arch_tex = Path("report-datn/chapters/ch3/3_3_kien_truc.tex").read_text(encoding="utf-8")
    assert "scale=0.58" not in arch_tex
