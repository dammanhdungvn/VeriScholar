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


def test_graduation_forms_compliance():
    """Kiểm tra tính chuẩn hóa và liêm chính học thuật của 2 biểu mẫu hành chính:
    Phiếu giao đề tài (phieu_giao_de_tai.tex) và Đề cương ĐATN (de_cuong_datn.tex).
    """
    phieu_path = Path("report-datn/frontmatter/phieu_giao_de_tai.tex")
    decuong_path = Path("report-datn/frontmatter/de_cuong_datn.tex")

    assert phieu_path.exists(), "phieu_giao_de_tai.tex must exist"
    assert decuong_path.exists(), "de_cuong_datn.tex must exist"

    phieu_content = phieu_path.read_text(encoding="utf-8")
    decuong_content = decuong_path.read_text(encoding="utf-8")

    # 1. Số điện thoại chính xác của tác giả
    assert "0978461865" in phieu_content, "phieu_giao_de_tai.tex must contain phone 0978461865"
    assert "0978461865" in decuong_content, "de_cuong_datn.tex must contain phone 0978461865"
    assert "0398686955" not in phieu_content, (
        "phieu_giao_de_tai.tex must not contain old phone 0398686955"
    )
    assert "0398686955" not in decuong_content, (
        "de_cuong_datn.tex must not contain old phone 0398686955"
    )

    # 2. Loại bỏ phân đoạn vụn vặt và rò rỉ mã nguồn nội bộ
    assert "Về sản phẩm (tiếp theo)" not in phieu_content, (
        "phieu_giao_de_tai.tex must not contain 'Về sản phẩm (tiếp theo)'"
    )
    assert "packages/core" not in phieu_content, (
        "phieu_giao_de_tai.tex must not contain 'packages/core'"
    )
    assert "packages/core" not in decuong_content, (
        "de_cuong_datn.tex must not contain 'packages/core'"
    )

    # 3. Kế hoạch thời gian 10 tuần chuẩn xác (24/08/2026 -> 02/11/2026)
    assert "24/08/2026" in decuong_content, "de_cuong_datn.tex must start week 1 at 24/08/2026"
    assert "02/11/2026" in decuong_content, "de_cuong_datn.tex must end week 10 at 02/11/2026"


def test_no_subjective_pronouns_in_body_chapters():
    """Kiểm tra Mục 3.1 trong RULES.md: Ngôi văn khách quan chuẩn mực.
    Tuyệt đối cấm sử dụng đại từ nhân xưng ngôi thứ nhất (em, tôi, chúng tôi, chúng em)
    trong toàn bộ các chương nội dung báo cáo (Chương 1 - Chương 4, Kết luận).
    Ngoại lệ kỹ thuật: chữ viết tắt metric học thuật Exact Match (EM).
    """
    import re

    chapters_dir = Path("report-datn/chapters")
    assert chapters_dir.exists(), "chapters directory must exist"

    # Regex bắt từ 'em' (chữ thường hoặc viết hoa đầu câu Em, nhưng không bắt EM viết hoa toàn bộ)
    em_pattern = re.compile(r"\b(em|Em)\b")
    subjective_pattern = re.compile(
        r"\b(tôi|Tôi|chúng tôi|Chúng tôi|chúng em|Chúng em|của tôi|của em)\b"
    )

    for tex_file in chapters_dir.rglob("*.tex"):
        if tex_file.name == "tai_lieu_tham_khao.tex":
            continue
        content = tex_file.read_text(encoding="utf-8")

        em_matches = em_pattern.findall(content)
        assert not em_matches, (
            f"File {tex_file.relative_to(chapters_dir)} vi phạm Mục 3.1: "
            f"chứa đại từ nhân xưng bị cấm '{em_matches[0]}'"
        )

        subj_matches = subjective_pattern.findall(content)
        assert not subj_matches, (
            f"File {tex_file.relative_to(chapters_dir)} vi phạm Mục 3.1: "
            f"chứa đại từ nhân xưng bị cấm '{subj_matches[0]}'"
        )


def test_frontmatter_ch1_and_bibliography_remediation():
    """Kiểm tra chuẩn hóa phần mở đầu (Frontmatter), Chương 1, Kết luận và Tài liệu tham khảo:
    - tai_lieu_tham_khao.tex sửa đúng tiêu đề & số trang bài báo RRF (Cormack et al., 2009),
      bổ sung gao2023rag và blondel2008louvain, tổng số \\bibitem <= 20.
    - phieu_giao_de_tai.tex đồng bộ 4 thực thể GraphRAG (Paper, Method, Dataset, MetricResult),
      không chứa LiteLLM hoặc mã hóa phía máy khách.
    - loi_cam_on.tex đồng bộ đại từ xưng hô, không trộn lẫn 'con xin' và 'em xin'.
    - 1_2_tinh_cap_thiet.tex có bảng đối chiếu tab:related_systems_comparison.
    """
    import re

    ref_content = Path("report-datn/chapters/tai_lieu_tham_khao.tex").read_text(encoding="utf-8")
    assert (
        "Reciprocal rank fusion outperforms condorcet and individual rank learning methods"
        in ref_content
    )
    assert "758--759" in ref_content
    assert "cite space algorithms" not in ref_content
    assert "\\bibitem{gao2023rag}" in ref_content
    assert "\\bibitem{blondel2008louvain}" in ref_content
    bibitems = re.findall(r"\\bibitem\{([^}]+)\}", ref_content)
    assert 0 < len(bibitems) <= 20

    phieu_content = Path("report-datn/frontmatter/phieu_giao_de_tai.tex").read_text(
        encoding="utf-8"
    )
    assert "LiteLLM" not in phieu_content
    assert "phía máy khách" not in phieu_content
    assert "Paper, Method, Dataset, MetricResult" in phieu_content or (
        "Bài báo" in phieu_content
        and "Phương pháp" in phieu_content
        and "Tập dữ liệu" in phieu_content
        and "Chỉ số thực nghiệm" in phieu_content
    )

    loi_cam_on_content = Path("report-datn/frontmatter/loi_cam_on.tex").read_text(encoding="utf-8")
    assert "con xin" not in loi_cam_on_content

    ch1_2_content = Path("report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex").read_text(
        encoding="utf-8"
    )
    assert "\\label{tab:related_systems_comparison}" in ch1_2_content


def test_chapter2_theoretical_rigor_remediation():
    """Kiểm tra chuẩn hóa cơ sở lý thuyết Chương 2 (Task 4):
    - 2_1_postgresql_redis.tex: sửa MVCC đọc không chặn ghi, bỏ 'không gây khóa chết'
      và 'Dedicated Vector Database'.
    - 2_3_advanced_rag.tex: trích dẫn \\cite{gao2023rag}, nêu cơ chế ts_rank_cd + BM25
      và Cross-Encoder, ví dụ RRF dùng k = 60 (bỏ 'k = 0 dùng để minh họa').
    - 2_4_knowledge_graph_wiki.tex: trích dẫn \\cite{blondel2008louvain} (Louvain) và
      loại bỏ 'Author Nodes' khỏi sơ đồ đồ thị tri thức (đồng bộ 4 loại nút).
    - 2_5_agentic_react.tex: không chứa trích dẫn thừa hong2023metagpt / wang2023planandsolve,
      đồng bộ biên độ cài đặt ReAct + Tool Use đơn tác tử.
    - 2_7_azure_e2b_byok.tex: bỏ 'GPT-5.6-luna', cập nhật công thức eq:aes_gcm chứa J_0.
    """
    ch2_dir = Path("report-datn/chapters/ch2")

    ch2_1 = (ch2_dir / "2_1_postgresql_redis.tex").read_text(encoding="utf-8")
    assert "không gây khóa chết" not in ch2_1
    assert "Dedicated Vector Database" not in ch2_1
    assert "đọc không chặn ghi" in ch2_1

    ch2_3 = (ch2_dir / "2_3_advanced_rag.tex").read_text(encoding="utf-8")
    assert "\\cite{gao2023rag}" in ch2_3
    assert "ts\\_rank\\_cd" in ch2_3 or "ts_rank_cd" in ch2_3
    assert "Cross-Encoder" in ch2_3
    assert "k = 0 \\text{ dùng để minh họa}" not in ch2_3
    assert "k = 0 dùng để minh họa" not in ch2_3

    ch2_4 = (ch2_dir / "2_4_knowledge_graph_wiki.tex").read_text(encoding="utf-8")
    assert "\\cite{blondel2008louvain}" in ch2_4
    assert "Author Nodes" not in ch2_4

    ch2_5 = (ch2_dir / "2_5_agentic_react.tex").read_text(encoding="utf-8")
    assert "\\cite{hong2023metagpt}" not in ch2_5
    assert "\\cite{wang2023planandsolve}" not in ch2_5

    ch2_7 = (ch2_dir / "2_7_azure_e2b_byok.tex").read_text(encoding="utf-8")
    assert "GPT-5.6-luna" not in ch2_7
    assert "gpt-4o-mini" in ch2_7
    assert "J_0" in ch2_7


def test_chapter3_database_and_analysis_remediation():
    """Kiểm tra chuẩn hóa phân tích hệ thống, thuật toán và thiết kế CSDL 20 bảng Chương 3 (Task 5):
    - 3_1_mo_ta_bai_toan.tex và 3_2_khao_sat_nghiep_vu.tex không chứa 'nhóm nghiên cứu'.
    - 3_2_khao_sat_nghiep_vu.tex bổ sung thiết kế thuật toán cho 4 pipeline cốt lõi.
    - 3_4_phan_tich_usecase.tex và 3_5_bieu_do_tuan_tu.tex đồng bộ CRAG, verify_output_grounding,
      bộ lọc Jaccard >= 3 từ khóa và cơ chế vận hành quản trị viên.
    - 3_6_thiet_ke_csdl.tex chứa đủ 20 bảng SQLAlchemy thực tế (bao gồm graph_nodes, graph_edges,
      folder_community_summaries, wiki_pages), loại bỏ 4 bảng ảo (extracted_figures,
      extracted_tables, draft_sections, latex_compilations), bổ sung hashed_password vào users,
      embedding và content_tsv vào document_chunks, sửa khóa ngoại blobs(id)/sessions(id)
      và xóa văn bản thừa 'mũi tên cụt trực quan'.
    """
    ch3_dir = Path("report-datn/chapters/ch3")

    ch3_1 = (ch3_dir / "3_1_mo_ta_bai_toan.tex").read_text(encoding="utf-8")
    ch3_2 = (ch3_dir / "3_2_khao_sat_nghiep_vu.tex").read_text(encoding="utf-8")
    assert "nhóm nghiên cứu" not in ch3_1
    assert "nhóm nghiên cứu" not in ch3_2

    ch3_2_norm = ch3_2.replace("\\_", "_")
    for algo_token in [
        "mid_x",
        "250",
        "HNSW",
        "ts_rank_cd",
        "0{,}35",
        "0{,}20",
        "reason_and_plan",
        "healing_router",
        "_auto_patch",
        "apply_heuristic_repair",
        "OpenAI Structured Outputs",
        "0{,}90",
        "Louvain",
    ]:
        assert algo_token in ch3_2_norm, (
            f"3_2_khao_sat_nghiep_vu.tex must specify algorithm token '{algo_token}'"
        )

    ch3_4_norm = (
        (ch3_dir / "3_4_phan_tich_usecase.tex").read_text(encoding="utf-8").replace("\\_", "_")
    )
    ch3_5_norm = (
        (ch3_dir / "3_5_bieu_do_tuan_tu.tex").read_text(encoding="utf-8").replace("\\_", "_")
    )
    assert "verify_output_grounding" in ch3_4_norm
    assert "verify_output_grounding" in ch3_5_norm
    assert "/api/v1/evaluations/run-benchmark" in ch3_4_norm
    assert "Langfuse Cloud" in ch3_4_norm

    ch3_6_raw = (ch3_dir / "3_6_thiet_ke_csdl.tex").read_text(encoding="utf-8")
    ch3_6_norm = (
        ch3_6_raw.replace("\\allowbreak ", "")
        .replace("\\allowbreak", "")
        .replace("\\_", "_")
        .replace("$\\to$", "->")
    )

    required_20_tables = [
        "users",
        "scholar_profiles",
        "user_api_keys",
        "document_storage_blobs",
        "documents",
        "document_chunks",
        "document_summaries",
        "reference_items",
        "folders",
        "research_sessions",
        "session_documents",
        "session_turns",
        "research_notes",
        "graph_nodes",
        "graph_edges",
        "folder_community_summaries",
        "wiki_pages",
        "drafts",
        "draft_assets",
        "draft_messages",
    ]
    for tbl in required_20_tables:
        assert tbl in ch3_6_norm, f"3_6_thiet_ke_csdl.tex must include real table '{tbl}'"

    forbidden_fake_tables = [
        "extracted_figures",
        "extracted_tables",
        "draft_sections",
        "latex_compilations",
    ]
    for tbl in forbidden_fake_tables:
        assert tbl not in ch3_6_norm, f"3_6_thiet_ke_csdl.tex must not include fake table '{tbl}'"

    assert "hashed_password" in ch3_6_norm
    assert "embedding" in ch3_6_norm
    assert "content_tsv" in ch3_6_norm
    assert "FK -> blobs(id)" not in ch3_6_norm
    assert "FK -> sessions(id)" not in ch3_6_norm
    assert "FK -> document_storage_blobs(id)" in ch3_6_norm
    assert "FK -> research_sessions(id)" in ch3_6_norm
    assert "mũi tên cụt trực quan" not in ch3_6_raw
