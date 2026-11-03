from pathlib import Path


def test_usecase_diagram_precedes_table():
    tex_path = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Vị trí của biểu đồ Use Case tổng quan phải xuất hiện trước bảng đặc tả tác nhân
    fig_pos = content.find("\\subsection{Biểu đồ Use Case tổng quan của hệ thống}")
    tab_pos = content.find("\\subsection{Các tác nhân và danh mục ca sử dụng của hệ thống}")

    assert fig_pos != -1, "Không tìm thấy tiểu mục Biểu đồ Use Case tổng quan"
    assert tab_pos != -1, "Không tìm thấy tiểu mục Các tác nhân và danh mục ca sử dụng"
    assert fig_pos < tab_pos, (
        f"Biểu đồ Use Case (pos {fig_pos}) phải đứng trước Bảng tác nhân (pos {tab_pos})!"
    )

    # Nhắc đến Hình 3-3 trước Bảng 3-1 trong văn bản dẫn
    ref_fig_pos = content.find("\\ref{fig:usecase_overview}")
    ref_tab_pos = content.find("\\ref{tab:actors_usecases}")
    assert ref_fig_pos < ref_tab_pos, "Tham chiếu Hình 3-3 phải xuất hiện trước tham chiếu Bảng 3-1"
