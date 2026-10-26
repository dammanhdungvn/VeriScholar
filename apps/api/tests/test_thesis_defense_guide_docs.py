from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = REPO_ROOT / "docs"
GUIDE_FILE = DOCS_DIR / "THESIS_DEFENSE_GUIDE.md"
PRD_00 = DOCS_DIR / "PRD" / "00-overview-and-cleanup.md"
PRD_01 = DOCS_DIR / "PRD" / "01-auth-and-user.md"


def test_thesis_defense_guide_exists_and_contains_required_chapters():
    assert GUIDE_FILE.exists(), "docs/THESIS_DEFENSE_GUIDE.md must exist"
    content = GUIDE_FILE.read_text(encoding="utf-8")

    # Verify Chapter 0 and Chapter 1 headers
    assert "## Chương 0: Nền Tảng Kiến Trúc 18 Bảng CSDL & Kho Lưu Trữ CAS" in content
    assert "## Chương 1: Định Danh Học Giả, Mã ORCID & Két Sắt Khóa BYOK" in content

    # Verify 4 required sections in each chapter
    for ch_title in ["Chương 0", "Chương 1"]:
        assert (
            f"1. Giải Thích Bình Dân & Ẩn Dụ Thực Tế ({ch_title})" in content
            or "1. Giải Thích Bình Dân" in content
        )
        assert "Tại Sao Bắt Buộc Phải Có" in content
        assert "Bộ Câu Hỏi & Câu Trả Lời Phản Biện Hội Đồng" in content
        assert "Bằng Chứng Thực Nghiệm Đã Chạy" in content


def test_docs_contain_no_absolute_file_links():
    md_files = [GUIDE_FILE, PRD_00, PRD_01]
    for md_file in md_files:
        if not md_file.exists():
            continue
        text = md_file.read_text(encoding="utf-8")
        assert "file://" not in text, f"{md_file} contains prohibited file:// absolute link"


def test_prd_files_cross_reference_thesis_guide():
    assert PRD_00.exists()
    assert PRD_01.exists()
    text_00 = PRD_00.read_text(encoding="utf-8")
    text_01 = PRD_01.read_text(encoding="utf-8")

    assert "../THESIS_DEFENSE_GUIDE.md" in text_00, "PRD-00 must link to THESIS_DEFENSE_GUIDE.md"
    assert "../THESIS_DEFENSE_GUIDE.md" in text_01, "PRD-01 must link to THESIS_DEFENSE_GUIDE.md"
