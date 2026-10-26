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
