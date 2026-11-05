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
    assert "research\\_sessions(id)" in csdl_tex
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


def test_tables_center_aligned():
    # 1. Bảng 1-1: Cột nền tảng căn giữa
    ch1_tex = Path("report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex").read_text(encoding="utf-8")
    assert (
        ">{\\centering\\arraybackslash}m{2.3cm}" in ch1_tex
        or ">{\\bfseries\\centering\\arraybackslash}m{2.3cm}" in ch1_tex
    )

    # 2. Bảng 2-1: Cột tiêu chí căn giữa
    ch2_tex = Path("report-datn/chapters/ch2/2_1_postgresql_redis.tex").read_text(encoding="utf-8")
    assert (
        ">{\\centering\\arraybackslash}m{3.0cm}" in ch2_tex
        or ">{\\centering\\arraybackslash\\bfseries}m{3.0cm}" in ch2_tex
    )

    # 3. Bảng 3-1: Cột tên Actor căn giữa
    ch3_uc = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex").read_text(encoding="utf-8")
    assert ">{\\centering\\arraybackslash}m{3.8cm}" in ch3_uc

    # 4. Bảng 4-1: Cột phân vùng Monorepo căn giữa
    ch4_env = Path("report-datn/chapters/ch4/4_1_moi_truong.tex").read_text(encoding="utf-8")
    assert ">{\\centering\\arraybackslash}m{2.6cm}" in ch4_env

    # 5. Bảng 4-2: Cột cổng kiểm thử căn giữa
    ch4_test = Path("report-datn/chapters/ch4/4_3_kiem_thu.tex").read_text(encoding="utf-8")
    assert ">{\\centering\\arraybackslash}m{2.2cm}" in ch4_test

    # 6. Bảng 4-3 & 4-4: Các cột số liệu thực nghiệm căn giữa
    ch4_data = Path("report-datn/chapters/ch4/4_4_so_lieu.tex").read_text(encoding="utf-8")
    assert ">{\\centering\\arraybackslash}m{2.3cm}" in ch4_data
    assert ">{\\centering\\arraybackslash}m{2.6cm}" in ch4_data
