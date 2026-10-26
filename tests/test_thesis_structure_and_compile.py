import subprocess
from pathlib import Path


def test_thesis_files_exist():
    required_files = [
        "report-datn/main.tex",
        "report-datn/ROADMAP.md",
        "report-datn/frontmatter/muc_luc.tex",
        "report-datn/frontmatter/loi_cam_on.tex",
        "report-datn/frontmatter/loi_mo_dau.tex",
        "report-datn/frontmatter/danh_muc_viet_tat.tex",
        "report-datn/chapters/ch1_tong_quan.tex",
        "report-datn/chapters/ch1/1_1_gioi_thieu.tex",
        "report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex",
        "report-datn/chapters/ch1/1_3_muc_tieu.tex",
        "report-datn/chapters/ch1/1_4_noi_dung.tex",
        "report-datn/chapters/ch1/1_5_pham_vi.tex",
        "report-datn/chapters/ch1/1_6_bo_cuc.tex",
        "report-datn/chapters/ch2_co_so_ly_thuyet.tex",
        "report-datn/chapters/ch2/2_1_hexagonal.tex",
        "report-datn/chapters/ch2/2_2_hybrid_rag.tex",
        "report-datn/chapters/ch2/2_3_graph_rag.tex",
        "report-datn/chapters/ch2/2_4_react_agent.tex",
        "report-datn/chapters/ch2/2_5_cas_byok.tex",
        "report-datn/chapters/ch3_thiet_ke_he_thong.tex",
        "report-datn/chapters/ch3/3_1_khao_sat.tex",
        "report-datn/chapters/ch3/3_2_usecase.tex",
        "report-datn/chapters/ch3/3_3_kien_truc.tex",
        "report-datn/chapters/ch3/3_4_csdl.tex",
        "report-datn/chapters/ch4_thuc_nghiem.tex",
        "report-datn/chapters/ch4/4_1_moi_truong.tex",
        "report-datn/chapters/ch4/4_2_giao_dien.tex",
        "report-datn/chapters/ch4/4_3_kiem_thu.tex",
        "report-datn/chapters/ch4/4_4_so_lieu.tex",
        "report-datn/chapters/ket_luan.tex",
        "report-datn/chapters/tai_lieu_tham_khao.tex",
    ]
    for file_path in required_files:
        assert Path(file_path).exists(), f"File must exist: {file_path}"


def test_thesis_compilation():
    res = None
    for _ in range(2):
        res = subprocess.run(
            [
                "xelatex",
                "-interaction=nonstopmode",
                "-file-line-error",
                "main.tex",
            ],
            cwd="report-datn",
            capture_output=True,
            text=True,
        )
    assert res is not None and res.returncode == 0, (
        f"XeLaTeX compilation failed with log:\n{res.stdout[-1500:] if res else ''}"
    )
    assert Path("report-datn/main.pdf").exists()


def test_thesis_vietnamese_accented_characters_support():
    """Kiểm tra toàn bộ 144 biến thể nguyên âm tiếng Việt
    (12 nguyên âm x 6 thanh điệu x 2 kiểu chữ thường/hoa).
    """
    vietnamese_vowels = (
        "aàáảãạăằắẳẵặâầấẩẫậ"
        "eèéẻẽẹêềếểễệ"
        "iìíỉĩị"
        "oòóỏõọôồốổỗộơờớởỡợ"
        "uùúủũụưừứửữự"
        "yỳýỷỹỵ"
        "AÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬ"
        "EÈÉẺẼẸÊỀẾỂỄỆ"
        "IÌÍỈĨỊ"
        "OÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ"
        "UÙÚỦŨỤƯỪỨỬỮỰ"
        "YỲÝỶỸỴ"
    )
    assert len(vietnamese_vowels) == 144, (
        f"Must have exactly 144 vowel variants, got {len(vietnamese_vowels)}"
    )

    log_path = Path("report-datn/main.log")
    if log_path.exists():
        log_content = log_path.read_text(encoding="utf-8", errors="replace")
        assert "Missing character: There is no" not in log_content, (
            "Log contains Missing character warnings"
        )


def test_thesis_no_undefined_references():
    """Kiểm tra tệp biên dịch không có tham chiếu chéo hoặc trích dẫn undefined."""
    log_path = Path("report-datn/main.log")
    if log_path.exists():
        log_content = log_path.read_text(encoding="utf-8", errors="replace")
        assert "LaTeX Warning: There were undefined references." not in log_content
        assert "LaTeX Warning: Citation" not in log_content


def test_thesis_ch4_section_4_1_environment_and_monorepo():
    """Kiểm tra cấu trúc và nội dung học thuật chi tiết của Mục 4.1:
    - 4.1.1: Cấu hình hạ tầng phần cứng & phần mềm (Azure Ubuntu 24.04 LTS, 4 vCPU, 16GB RAM,
      PostgreSQL pgvector, Python 3.12 uv, React 19, E2B MicroVM, Langfuse Cloud).
    - 4.1.2: Phân tách kiến trúc Monorepo 3 phân vùng và rào chắn kiểm thử AST tự động.
    - Bảng so sánh tab:monorepo_structure đối chiếu quy tắc ranh giới 3 phân vùng.
    """
    sec4_1_file = Path("report-datn/chapters/ch4/4_1_moi_truong.tex")
    assert sec4_1_file.exists(), "4_1_moi_truong.tex must exist"
    content = sec4_1_file.read_text(encoding="utf-8")

    # 1. Kiểm tra các tham số hạ tầng đám mây và công nghệ nền tảng (4.1.1)
    required_infrastructure_tokens = [
        "Azure Ubuntu 24.04 LTS",
        "4 vCPU",
        "16GB RAM",
        "PostgreSQL 16.2",
        "pgvector",
        "Python 3.12",
        "uv",
        "FastAPI",
        "SQLAlchemy 2.0 Async",
        "Node.js 22",
        "React 19",
        "Tailwind CSS",
        "Zustand",
        "E2B Sandbox MicroVM",
        "Langfuse Cloud",
    ]
    for token in required_infrastructure_tokens:
        assert token in content, f"Missing required infrastructure token in 4.1: {token}"

    # 2. Kiểm tra phân tách Monorepo 3 phân vùng (4.1.2)
    required_monorepo_tokens = [
        "packages/core",
        "apps/api",
        "apps/web",
        "test_architecture_boundary.py",
    ]
    content_normalized = content.replace(r"\_", "_")
    for token in required_monorepo_tokens:
        assert token in content_normalized, (
            f"Missing required monorepo/boundary token in 4.1: {token}"
        )

    # 3. Kiểm tra nhãn bảng so sánh kiến trúc ranh giới
    assert "\\label{tab:monorepo_structure}" in content, (
        "Missing \\label{tab:monorepo_structure} in 4_1_moi_truong.tex"
    )


def test_thesis_ch4_section_4_2_ui_subsystems():
    """Kiểm tra cấu trúc và nội dung học thuật chi tiết của Mục 4.2:
    - Sơ đồ vector TikZ fig:ui_layout_architecture thể hiện kiến trúc 4 phân hệ tương tác.
    - 4.2.1 Phân hệ Khám phá tài liệu khoa học (subsec:ui_discovery):
      Skeleton animate-pulse, thẻ chống tràn, lọc Đã bình duyệt.
    - 4.2.2 Phân hệ Đọc sâu và Bounding Box (subsec:ui_deep_reading):
      Khung kép PDF Canvas và Chat SSE, Bounding Box viền vàng.
    - 4.2.3 Phân hệ Quản lý tài liệu & Hồ sơ học giả (subsec:ui_profile):
      Khử trùng lặp CAS SHA-256, liên kết ORCID, két sắt BYOK AES-256-GCM.
    - 4.2.4 Phân hệ Soạn thảo & Tự sửa lỗi LaTeX (subsec:ui_writing):
      Monaco Editor, E2B MicroVM Sandbox, chu trình ReAct.
    """
    sec4_2_file = Path("report-datn/chapters/ch4/4_2_giao_dien.tex")
    assert sec4_2_file.exists(), "4_2_giao_dien.tex must exist"
    content = sec4_2_file.read_text(encoding="utf-8")

    # 1. Kiểm tra sơ đồ vector TikZ và nhãn hình ảnh
    assert "\\label{fig:ui_layout_architecture}" in content, (
        "Missing \\label{fig:ui_layout_architecture} in 4_2_giao_dien.tex"
    )
    assert "\\begin{tikzpicture}" in content, "Missing \\begin{tikzpicture} in 4_2_giao_dien.tex"

    # 2. Kiểm tra 4 tiểu mục bắt buộc
    required_subsections = [
        "\\label{subsec:ui_discovery}",
        "\\label{subsec:ui_deep_reading}",
        "\\label{subsec:ui_profile}",
        "\\label{subsec:ui_writing}",
    ]
    for sub in required_subsections:
        assert sub in content, f"Missing subsection label in 4.2: {sub}"

    # 3. Kiểm tra các thuật ngữ kỹ thuật cốt lõi của 4 phân hệ
    required_keywords = [
        "animate-pulse",
        "Đã bình duyệt",
        "Bounding Box",
        "CAS",
        "ORCID",
        "BYOK",
        "AES-256-GCM",
        "Monaco",
        "E2B",
        "ReAct",
    ]
    for kw in required_keywords:
        assert kw in content, f"Missing core technical keyword in 4.2: {kw}"
