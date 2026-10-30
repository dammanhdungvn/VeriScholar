from pathlib import Path


def test_thesis_rules_file_exists_and_valid():
    rules_path = Path("report-datn/RULES.md")
    assert rules_path.exists(), "report-datn/RULES.md must exist"
    content = rules_path.read_text(encoding="utf-8")

    # Kiểm tra các phần cốt lõi bắt buộc
    required_sections = [
        "KIẾN TRÚC & CẤU HÌNH KỸ THUẬT XELATEX",
        "QUY CHUẨN ĐỊNH DẠNG TRANG & HÌNH THỨC",
        "VĂN PHONG & QUY TẮC HÀNH VĂN BẤT BIẾN",
        "QUY TẮC BẢNG BIỂU, HÌNH VẼ & DẪN CHIẾU CHÉO",
        "CHIẾN LƯỢC CHẮT LỌC NỘI DUNG TỪ DOCS",
    ]
    for section in required_sections:
        assert section in content, f"Missing required section: {section}"

    # Kiểm tra không chứa URL tuyệt đối (Quy tắc 5 AGENTS.md)
    assert "file://" not in content, "RULES.md must not contain file:// links"


def test_thesis_chapter2_academic_purity():
    """Kiểm tra Chương 2 (Cơ sở lý thuyết & Công nghệ) không bị rò rỉ mã nguồn:
    Tuyệt đối cấm chứa đường dẫn file repository (packages/, apps/, src/)
    và tên interface/adapter nội bộ trong các file .tex của Chương 2.
    """
    ch2_dir = Path("report-datn/chapters/ch2")
    assert ch2_dir.exists(), "ch2 directory must exist"

    forbidden_tokens = [
        "packages/",
        "apps/",
        "src/",
        "IAcademicSearchResolverPort",
        "IPdfExtractorPort",
        "ICasStoragePort",
        "PostgresStorageAdapter",
    ]

    for tex_file in ch2_dir.glob("*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in content, (
                f"File {tex_file.name} vi phạm Liêm chính học thuật Chương 2: "
                f"chứa chi tiết mã nguồn bị cấm '{token}'"
            )


def test_thesis_rules_academic_architecture_paradigm():
    """Kiểm tra Quy tắc 8 trong AGENTS.md và Mục 3.7 trong RULES.md:
    Bắt buộc phải có quy chuẩn kiến trúc hệ thống chuẩn paper khoa học
    hướng người đọc (Human-Centric Paper Architecture).
    """
    agents_path = Path(".agents/AGENTS.md")
    rules_path = Path("report-datn/RULES.md")

    assert agents_path.exists(), ".agents/AGENTS.md must exist"
    assert rules_path.exists(), "report-datn/RULES.md must exist"

    agents_content = agents_path.read_text(encoding="utf-8")
    rules_content = rules_path.read_text(encoding="utf-8")

    assert "Human-Centric Academic Paper Architecture" in agents_content, (
        "AGENTS.md must contain Rule 8 about Human-Centric Academic Paper Architecture"
    )
    assert (
        "Quy Chuẩn Biểu Diễn Sơ Đồ Kiến Trúc Hệ Thống Chuẩn Paper Khoa Học Quốc Tế" in rules_content
    ), "RULES.md must contain Section 3.7 on Academic Paper Architecture Paradigm"
    assert "Quy Chuẩn Kỹ Nghệ Sơ Đồ TikZ Chống Chồng Đè & Ríu Rít" in rules_content, (
        "RULES.md must contain Section 3.8 on TikZ Anti-Crowding Standard"
    )
    assert "Quy Chuẩn Kỹ Nghệ Bảng Biểu Nâng Cao" in rules_content, (
        "RULES.md must contain Section 4.6 on Advanced Tabular Engineering"
    )


def test_thesis_reference_count_within_cap():
    """Kiểm tra Giới hạn số lượng tài liệu tham khảo (Reference Cap Invariant):
    Danh mục tài liệu tham khảo của báo cáo đồ án bắt buộc phải <= 20 tài liệu.
    """
    import re

    ref_file = Path("report-datn/chapters/tai_lieu_tham_khao.tex")
    assert ref_file.exists(), "tai_lieu_tham_khao.tex must exist"

    content = ref_file.read_text(encoding="utf-8")
    bibitems = re.findall(r"\\bibitem\{([^}]+)\}", content)

    assert 0 < len(bibitems) <= 20, (
        f"Số lượng tài liệu tham khảo vi phạm quy chuẩn ({len(bibitems)} tài liệu). "
        f"Bắt buộc: 0 < N_refs <= 20."
    )

    # Kiểm tra quy tắc đã được thể chế hóa trong RULES.md và AGENTS.md
    rules_content = Path("report-datn/RULES.md").read_text(encoding="utf-8")
    agents_content = Path(".agents/AGENTS.md").read_text(encoding="utf-8")

    assert "20" in rules_content and "tài liệu tham khảo" in rules_content
    assert "20" in agents_content and "tài liệu tham khảo" in agents_content


def test_ch3_uc01_two_tier_discovery_spec():
    """Kiểm tra sự hiện diện và tính toàn vẹn của Bảng đặc tả ca sử dụng UC-01
    (Khám phá bài báo học thuật hai tầng tin cậy) trong Chương 3.
    """
    uc_file = Path("report-datn/chapters/ch3/3_4_phan_tich_usecase.tex")
    assert uc_file.exists(), "3_4_phan_tich_usecase.tex must exist"

    content = uc_file.read_text(encoding="utf-8")

    # Kiểm tra nhãn bảng đặc tả UC-01
    assert "\\label{tab:uc_01_spec}" in content or "\\label{tab:uc_kham_pha_spec}" in content, (
        "Missing \\label{tab:uc_01_spec} in 3_4_phan_tich_usecase.tex"
    )

    # Kiểm tra vị trí: tab:uc_01_spec phải xuất hiện trước tab:uc_03_spec
    pos_uc01 = (
        content.find("\\label{tab:uc_01_spec}")
        if "\\label{tab:uc_01_spec}" in content
        else content.find("\\label{tab:uc_kham_pha_spec}")
    )
    pos_uc03 = (
        content.find("\\label{tab:uc_03_spec}")
        if "\\label{tab:uc_03_spec}" in content
        else content.find("\\label{tab:uc_doc_sau_spec}")
    )
    assert pos_uc03 != -1, "Missing \\label{tab:uc_03_spec} in 3_4_phan_tich_usecase.tex"
    assert pos_uc01 < pos_uc03, "tab:uc_01_spec must appear before tab:uc_03_spec"

    # Kiểm tra các từ khóa kỹ thuật cốt lõi của động cơ kiểm soát độ tin cậy 2 tầng
    assert "Jaccard" in content, "UC-01 must specify Jaccard token overlap filter"
    assert "0.2" in content or "0{,}2" in content, "UC-01 must specify threshold 0.2"
    assert "Skeleton" in content or "skeleton" in content, (
        "UC-01 must specify instant skeleton loading"
    )
    assert "bình duyệt" in content or "peer-reviewed" in content, (
        "UC-01 must specify peer-reviewed filtering"
    )
