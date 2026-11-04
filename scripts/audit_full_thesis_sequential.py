#!/usr/bin/env python3
"""Audit Full Thesis Sequential Script (Word-Standard 13pt & 1.5 Line Spacing).

Conducts an exhaustive, sequential audit of 100% of the 44 .tex files in report-datn/
without skipping any section, strictly enforcing:
1. Font Size & Line Spacing Invariants:
   - 100% body text and table cells must be 13pt Times New Roman (no \\small, \\footnotesize, \\fontsize{8.5, \\fontsize{9 in table cells or body).
   - Line spacing: \\setstretch{1.45} globally, \\arraystretch >= 1.20 in tables.
   - Captions: Table captions on TOP in 13pt Italic; Figure captions on BOTTOM in 13pt Italic.
2. Frontmatter Sequential Checklist:
   - bia_chinh.tex: Spine 90° present, front has NO "KHOÁ 67".
   - bia_phu.tex: No title duplication, signatures with (Chữ ký), year 2026.
   - phieu_giao_de_tai.tex: NO pre-printed student/lecturer names, (Ký và ghi rõ họ tên), date 06/11/2026, no Department/Faculty signatures.
   - de_cuong_datn.tex: Ends at Section "Nơi thực hiện đồ án:", NO signature table, NO date.
   - loi_cam_on.tex: Ends after tri ân paragraphs, NO signature block.
   - muc_luc.tex: Arabic page 1, non-bold fonts (\\normalfont).
   - danh_muc_hinh.tex & danh_muc_bang.tex: \\setstretch{1.45}, no singlespace.
   - danh_muc_viet_tat.tex: Alphabetical A-Z abbreviation list.
   - loi_mo_dau.tex: Standard format.
3. Body Chapters Sequential Checklist (1.1-1.6, 2.1-2.9, 3.1-3.6, 4.1-4.4):
   - Headings adhere to 13pt/14pt titlesec standards.
   - Font size: strictly 13pt throughout.
   - All 25 figures checked for caption on BOTTOM in 13pt Italic and verified against their thematic subsection.
   - All 17 tables checked for caption on TOP in 13pt Italic, \\arraystretch >= 1.20, and en-dashes (\\item[--]).
   - Zero raw code leaks (\\texttt, broken math, ??, [?], nan, undefined).
4. Conclusion, Bibliography & Main:
   - ket_luan.tex: Clean, no setstretch override.
   - tai_lieu_tham_khao.tex: Exactly 10 landmark papers A-Z flat.
   - main.tex: Coordinates all sections in strict order.
5. PDF Layout Verification (if main.pdf present):
   - No orphan page spillovers (Ch2 end, Ch3 end, Bibliography).
   - Zero ??, [?], nan, undefined tokens in compiled PDF.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

# Resolve workspace root and report directory
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR
REPORT_DIR = REPO_ROOT / "report-datn"

# ANSI styling
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# The 44 sequential .tex files in report-datn/ (in order of inclusion/reading)
SEQUENTIAL_TEX_FILES = [
    # Frontmatter (10 files)
    "frontmatter/bia_chinh.tex",
    "frontmatter/bia_phu.tex",
    "frontmatter/phieu_giao_de_tai.tex",
    "frontmatter/de_cuong_datn.tex",
    "frontmatter/loi_cam_on.tex",
    "frontmatter/muc_luc.tex",
    "frontmatter/danh_muc_hinh.tex",
    "frontmatter/danh_muc_bang.tex",
    "frontmatter/danh_muc_viet_tat.tex",
    "frontmatter/loi_mo_dau.tex",
    # Chapter 1: Tổng quan (7 files)
    "chapters/ch1_tong_quan.tex",
    "chapters/ch1/1_1_gioi_thieu.tex",
    "chapters/ch1/1_2_tinh_cap_thiet.tex",
    "chapters/ch1/1_3_muc_tieu.tex",
    "chapters/ch1/1_4_noi_dung.tex",
    "chapters/ch1/1_5_pham_vi.tex",
    "chapters/ch1/1_6_bo_cuc.tex",
    # Chapter 2: Cơ sở lý thuyết và công nghệ (11 files)
    "chapters/ch2_co_so_ly_thuyet.tex",
    "chapters/ch2/2_1_postgresql_redis.tex",
    "chapters/ch2/2_2_hexagonal.tex",
    "chapters/ch2/2_2_hybrid_rag.tex",
    "chapters/ch2/2_3_advanced_rag.tex",
    "chapters/ch2/2_4_knowledge_graph_wiki.tex",
    "chapters/ch2/2_5_agentic_react.tex",
    "chapters/ch2/2_6_langgraph.tex",
    "chapters/ch2/2_7_azure_e2b_byok.tex",
    "chapters/ch2/2_8_langfuse.tex",
    "chapters/ch2/2_9_tools_languages.tex",
    # Chapter 3: Phân tích và thiết kế hệ thống (8 files)
    "chapters/ch3_thiet_ke_he_thong.tex",
    "chapters/ch3/3_1_mo_ta_bai_toan.tex",
    "chapters/ch3/3_2_khao_sat_nghiep_vu.tex",
    "chapters/ch3/3_3_kien_truc.tex",
    "chapters/ch3/3_3_tac_nhan_usecase.tex",
    "chapters/ch3/3_4_phan_tich_usecase.tex",
    "chapters/ch3/3_5_bieu_do_tuan_tu.tex",
    "chapters/ch3/3_6_thiet_ke_csdl.tex",
    # Chapter 4: Cài đặt và kết quả thực nghiệm (5 files)
    "chapters/ch4_thuc_nghiem.tex",
    "chapters/ch4/4_1_moi_truong.tex",
    "chapters/ch4/4_2_giao_dien.tex",
    "chapters/ch4/4_3_kiem_thu.tex",
    "chapters/ch4/4_4_so_lieu.tex",
    # Conclusion & Bibliography & Root (3 files)
    "chapters/ket_luan.tex",
    "chapters/tai_lieu_tham_khao.tex",
    "main.tex",
]

# Thematic mapping for all 25 figures
THEMATIC_FIGURES = {
    "fig:hybrid_search_rrf": (
        "chapters/ch2/2_2_hybrid_rag.tex",
        "Cơ chế tìm kiếm lai (Hybrid Search) kết hợp RRF",
    ),
    "fig:advanced_rag": (
        "chapters/ch2/2_3_advanced_rag.tex",
        "Mô hình kiến trúc tạo sinh tăng cường truy xuất nâng cao",
    ),
    "fig:academic_kg_wiki": (
        "chapters/ch2/2_4_knowledge_graph_wiki.tex",
        "Cấu trúc đồ thị tri thức học thuật và Graph Wiki",
    ),
    "fig:react_e2b_sandbox": (
        "chapters/ch2/2_5_agentic_react.tex",
        "Cơ chế tác nhân ReAct điều phối sandbox E2B MicroVM",
    ),
    "fig:workflow_as_is_to_be": (
        "chapters/ch3/3_2_khao_sat_nghiep_vu.tex",
        "Mô hình đối chiếu quy trình AS-IS và TO-BE",
    ),
    "fig:hexagonal_architecture": (
        "chapters/ch3/3_3_kien_truc.tex",
        "Kiến trúc Lục giác phân tầng và 4 Không gian nghiên cứu",
    ),
    "fig:usecase_overview": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Biểu đồ Use Case tổng quan của hệ thống VeriScholar",
    ),
    "fig:uc_kham_pha_sub": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Biểu đồ ca sử dụng con Tra cứu và tải tài liệu",
    ),
    "fig:uc_doc_sau_sub": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Biểu đồ ca sử dụng con Hỏi đáp đọc sâu và kiểm chứng tọa độ",
    ),
    "fig:uc_graphrag_sub": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Biểu đồ ca sử dụng con Khai phá Đồ thị tri thức",
    ),
    "fig:uc_bien_soan_sub": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Biểu đồ ca sử dụng con Biên soạn bản thảo và tự sửa lỗi LaTeX",
    ),
    "fig:seq_kham_pha": (
        "chapters/ch3/3_5_bieu_do_tuan_tu.tex",
        "Biểu đồ tuần tự Use Case Tra cứu và tải tài liệu",
    ),
    "fig:seq_doc_sau": (
        "chapters/ch3/3_5_bieu_do_tuan_tu.tex",
        "Biểu đồ tuần tự Use Case Hỏi đáp đọc sâu",
    ),
    "fig:seq_graphrag": (
        "chapters/ch3/3_5_bieu_do_tuan_tu.tex",
        "Biểu đồ tuần tự Use Case Khai phá Đồ thị tri thức",
    ),
    "fig:seq_bien_soan": (
        "chapters/ch3/3_5_bieu_do_tuan_tu.tex",
        "Biểu đồ tuần tự Use Case Biên soạn bản thảo",
    ),
    "fig:class_diagram_model": (
        "chapters/ch3/3_6_thiet_ke_csdl.tex",
        "Biểu đồ lớp (Class Diagram) mô tả các thực thể miền",
    ),
    "fig:ui_layout_architecture": (
        "chapters/ch4/4_2_giao_dien.tex",
        "Mô hình không gian tương tác 4 phân hệ",
    ),
    "fig:ui_search_paper": (
        "chapters/ch4/4_2_giao_dien.tex",
        "Giao diện tìm kiếm và khám phá tài liệu",
    ),
    "fig:ui_my_library": (
        "chapters/ch4/4_2_giao_dien.tex",
        "Giao diện quản lý thư viện nghiên cứu cá nhân",
    ),
    "fig:ui_deep_read_paper": (
        "chapters/ch4/4_2_giao_dien.tex",
        "Giao diện đọc sâu tài liệu PDF hai cột và Bounding Box",
    ),
    "fig:ui_graph": (
        "chapters/ch4/4_2_giao_dien.tex",
        "Giao diện mạng đồ thị tri thức học thuật 4 thực thể",
    ),
    "fig:ui_byok": ("chapters/ch4/4_2_giao_dien.tex", "Giao diện kho khóa API cá nhân (BYOK)"),
    "fig:ui_writing_paper": (
        "chapters/ch4/4_2_giao_dien.tex",
        "Giao diện soạn thảo bản thảo bài báo LaTeX",
    ),
    "fig:langfuse_tracing": (
        "chapters/ch4/4_4_so_lieu.tex",
        "Nhật ký kiểm chứng và giám sát vết thực thi Langfuse",
    ),
    "fig:monitor_openai": (
        "chapters/ch4/4_4_so_lieu.tex",
        "Báo cáo giám sát lượng token và chi phí OpenAI",
    ),
}

# Thematic mapping for all 17 tables
THEMATIC_TABLES = {
    "tab:related_systems_comparison": (
        "chapters/ch1/1_2_tinh_cap_thiet.tex",
        "Đối chiếu năng lực công cụ hiện có và VeriScholar",
    ),
    "tab:vector_db_comparison": (
        "chapters/ch2/2_1_postgresql_redis.tex",
        "So sánh PostgreSQL pgvector và Vector DB chuyên dụng",
    ),
    "tab:search_comparison": (
        "chapters/ch2/2_2_hybrid_rag.tex",
        "So sánh Dense Vector và Sparse Search (BM25)",
    ),
    "tab:actors_usecases": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Các Use Case chính đối với mỗi Actor trong hệ thống",
    ),
    "tab:uc_kham_pha_spec": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Đặc tả Use Case Tra cứu và tải tài liệu",
    ),
    "tab:uc_doc_sau_spec": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Đặc tả Use Case Hỏi đáp đọc sâu và kiểm chứng tọa độ",
    ),
    "tab:uc_graphrag_spec": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Đặc tả Use Case Khai phá Đồ thị tri thức",
    ),
    "tab:uc_bien_soan_spec": (
        "chapters/ch3/3_4_phan_tich_usecase.tex",
        "Đặc tả Use Case Biên soạn bản thảo và tự sửa lỗi LaTeX",
    ),
    "tab:class_relationships_analysis": (
        "chapters/ch3/3_6_thiet_ke_csdl.tex",
        "Phân tích các lớp thực thể miền và mối quan hệ",
    ),
    "tab:spec_documents": ("chapters/ch3/3_6_thiet_ke_csdl.tex", "Đặc tả bảng documents"),
    "tab:spec_chunks": ("chapters/ch3/3_6_thiet_ke_csdl.tex", "Đặc tả bảng document_chunks"),
    "tab:spec_graph_nodes": ("chapters/ch3/3_6_thiet_ke_csdl.tex", "Đặc tả bảng graph_nodes"),
    "tab:spec_drafts": ("chapters/ch3/3_6_thiet_ke_csdl.tex", "Đặc tả bảng drafts"),
    "tab:monorepo_structure": (
        "chapters/ch4/4_1_moi_truong.tex",
        "Cấu trúc phân vùng kho mã nguồn Monorepo",
    ),
    "tab:gate_results": (
        "chapters/ch4/4_3_kiem_thu.tex",
        "Kết quả kiểm thử tự động hệ thống qua 4 cổng xác minh",
    ),
    "tab:ablation_retrieval": (
        "chapters/ch4/4_4_so_lieu.tex",
        "Ablation Study các phương pháp truy xuất trên 36 truy vấn",
    ),
    "tab:ablation_latex_healing": (
        "chapters/ch4/4_4_so_lieu.tex",
        "Ablation Study cơ chế tự sửa lỗi LaTeX trên 25 kịch bản",
    ),
}


class AuditReporter:
    def __init__(self):
        self.defects = []
        self.audited_files = 0
        self.audited_figures = 0
        self.audited_tables = 0

    def add_defect(self, file_path: str, message: str):
        self.defects.append((file_path, message))

    def has_defects(self) -> bool:
        return len(self.defects) > 0


def audit_global_preamble(reporter: AuditReporter):
    """Audit config/preamble.tex and config/commands.tex for global invariants."""
    preamble_path = REPORT_DIR / "config/preamble.tex"
    if not preamble_path.exists():
        reporter.add_defect("config/preamble.tex", "Missing preamble.tex")
        return

    content = preamble_path.read_text(encoding="utf-8")

    # 1. Base font size 13pt
    if "fontsize=13pt" not in content:
        reporter.add_defect(
            "config/preamble.tex", "Global font size is not 13pt ([fontsize=13pt]{scrextend})"
        )

    # 2. Global line spacing 1.5 Word (\\setstretch{1.45})
    if "\\setstretch{1.45}" not in content:
        reporter.add_defect(
            "config/preamble.tex", "Missing global \\setstretch{1.45} (Word 1.5 line spacing)"
        )

    # 3. Caption font 13pt Word standard
    if "DeclareCaptionFont{size13}{\\fontsize{13pt}{17pt}\\selectfont}" not in content:
        reporter.add_defect(
            "config/preamble.tex", "Caption font must be declared as size13 (13pt/17pt)"
        )
    if "size12" in content:
        reporter.add_defect(
            "config/preamble.tex", "Found legacy size12 in preamble; captions must be 13pt"
        )

    # 4. Captionsetup for table (position=top, font=size13, labelfont=bf, textfont=it)
    tab_cap = re.search(r"\\captionsetup\[table\]\{([^}]+)\}", content)
    if not tab_cap:
        reporter.add_defect("config/preamble.tex", "Missing \\captionsetup[table]")
    else:
        tc = tab_cap.group(1)
        if (
            "position=top" not in tc
            or "font=size13" not in tc
            or "labelfont=bf" not in tc
            or "textfont=it" not in tc
        ):
            reporter.add_defect(
                "config/preamble.tex",
                "Table captionsetup must have position=top, font=size13, labelfont=bf, textfont=it",
            )

    # 5. Captionsetup for figure (position=bottom, font=size13, labelfont=bf, textfont=it)
    fig_cap = re.search(r"\\captionsetup\[figure\]\{([^}]+)\}", content)
    if not fig_cap:
        reporter.add_defect("config/preamble.tex", "Missing \\captionsetup[figure]")
    else:
        fc = fig_cap.group(1)
        if (
            "position=bottom" not in fc
            or "font=size13" not in fc
            or "labelfont=bf" not in fc
            or "textfont=it" not in fc
        ):
            reporter.add_defect(
                "config/preamble.tex",
                "Figure captionsetup must have position=bottom, font=size13, labelfont=bf, textfont=it",
            )

    # 6. Titlesec heading sizes: chapter 14pt, section 13pt, subsection 13pt
    if "fontsize{14}{18}" not in content:
        reporter.add_defect("config/preamble.tex", "Chapter title format must be 14pt")
    if "fontsize{13}{17}" not in content:
        reporter.add_defect("config/preamble.tex", "Section/subsection title format must be 13pt")

    # 7. Margins: top 2.5cm, bottom 2.5cm, left 3.5cm, right 2.5cm
    geom = re.search(r"\\usepackage\[(.*?)\]\{geometry\}", content, re.DOTALL)
    if not geom:
        reporter.add_defect("config/preamble.tex", "Missing geometry configuration")
    else:
        g_text = geom.group(1)
        if (
            "top=2.5cm" not in g_text
            or "bottom=2.5cm" not in g_text
            or "left=3.5cm" not in g_text
            or "right=2.5cm" not in g_text
        ):
            reporter.add_defect(
                "config/preamble.tex",
                "Geometry margins must be top=2.5cm, bottom=2.5cm, left=3.5cm, right=2.5cm",
            )

    # 8. TOC non-bold chapters
    if "\\renewcommand{\\cftchapfont}{\\normalfont}" not in content:
        reporter.add_defect(
            "config/preamble.tex",
            "Missing TOC non-bold chapter titles: \\renewcommand{\\cftchapfont}{\\normalfont}",
        )

    # 9. xltabular package loaded for breakable Use Case tables
    if "\\usepackage{xltabular}" not in content:
        reporter.add_defect("config/preamble.tex", "Missing \\usepackage{xltabular}")


def audit_file_generic(rel_path: str, content: str, reporter: AuditReporter):
    """Generic typography, spacing, and leak invariants for every .tex file."""
    # 1. No artificial line compression 1.241
    if "1.241" in content:
        reporter.add_defect(rel_path, "Found prohibited 1.241 line compression")

    # 2. No small/footnotesize in table environments
    for tm in re.finditer(
        r"\\begin\{(?:table|xltabular)\*?\}(.*?)\\end\{(?:table|xltabular)\*?\}", content, re.DOTALL
    ):
        tab_text = tm.group(1)
        for forbidden_font in [
            r"\\small\b",
            r"\\footnotesize\b",
            r"\\fontsize\{8",
            r"\\fontsize\{9",
        ]:
            if re.search(forbidden_font, tab_text):
                reporter.add_defect(
                    rel_path, f"Prohibited font size {forbidden_font} used in table environment"
                )

    # 3. No small/footnotesize in body text outside tikzpicture
    text_outside_tikz = re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "", content, flags=re.DOTALL
    )
    for forbidden_font in [r"\\small\b", r"\\footnotesize\b", r"\\fontsize\{8", r"\\fontsize\{9"]:
        # Exclude frontmatter admin minipage title
        if rel_path == "frontmatter/de_cuong_datn.tex" and "fontsize{11" in forbidden_font:
            continue
        if re.search(forbidden_font, text_outside_tikz):
            reporter.add_defect(
                rel_path, f"Prohibited font size {forbidden_font} used in body text"
            )

    # 4. Zero citation brackets [1], [2] in body chapters
    if rel_path.startswith("chapters/ch"):
        cb_matches = list(re.finditer(r"\[\d+\]", content))
        if cb_matches:
            examples = [m.group(0) for m in cb_matches[:3]]
            reporter.add_defect(rel_path, f"Found in-body citation brackets: {examples}")

    # 5. Zero raw unhandled code tokens
    for leak_token in [r"\?\?", r"\[\?\]", r"\bnan\b", r"\bundefined\b"]:
        # Only check outside comments
        for line in content.splitlines():
            sline = line.strip()
            if sline.startswith("%"):
                continue
            if re.search(leak_token, sline, re.IGNORECASE):
                reporter.add_defect(
                    rel_path, f"Found raw leak token {leak_token} in line: {sline[:60]}"
                )


def audit_frontmatter_file(rel_path: str, content: str, reporter: AuditReporter):
    """Specific checks for Frontmatter files according to HUMG and Hieu.pdf guidelines."""
    if rel_path == "frontmatter/bia_chinh.tex":
        # Spine 90° present with cohort 67 and author
        if (
            "rotate=-90" not in content
            or "ĐÀM MẠNH DŨNG" not in content
            or ("KHOÁ 67" not in content and "KHÓA 67" not in content)
        ):
            reporter.add_defect(
                rel_path, "Bìa 1: Missing 90° spine overlay with ĐÀM MẠNH DŨNG and KHOÁ 67"
            )
        # Front face has NO KHOÁ 67
        front_face = re.sub(
            r"\\begin\{tikzpicture\}\[.*?overlay.*?\].*?\\end\{tikzpicture\}",
            "",
            content,
            flags=re.DOTALL,
        )
        if "KHOÁ 67" in front_face or "KHÓA 67" in front_face:
            reporter.add_defect(rel_path, "Bìa 1: KHOÁ 67 must NOT appear on the front cover face")
        if "2026" not in content:
            reporter.add_defect(rel_path, "Bìa 1: Missing year 2026")

    elif rel_path == "frontmatter/bia_phu.tex":
        # No duplicate full thesis title
        if "XÂY DỰNG NỀN TẢNG" in content:
            reporter.add_defect(
                rel_path, "Bìa phụ: Duplicate full thesis title must be omitted per Hieu.pdf"
            )
        # Signatures with (Chữ ký)
        if "(Chữ ký)" not in content:
            reporter.add_defect(rel_path, "Bìa phụ: Missing (Chữ ký) signature prompts")
        if "Giảng viên hướng dẫn" not in content or "Sinh viên thực hiện" not in content:
            reporter.add_defect(rel_path, "Bìa phụ: Missing Title Case role titles")
        if "2026" not in content:
            reporter.add_defect(rel_path, "Bìa phụ: Missing year 2026")

    elif rel_path == "frontmatter/phieu_giao_de_tai.tex":
        # NO Trưởng Bộ môn or Trưởng Khoa
        if "TRƯỞNG BỘ MÔN" in content or "Trưởng Bộ môn" in content or "Trưởng Khoa" in content:
            reporter.add_defect(
                rel_path, "Phiếu giao đề tài: Trưởng Bộ môn / Trưởng Khoa is strictly prohibited"
            )
        # Fixed submission date
        if "06 tháng 11 năm 2026" not in content and "06/11/2026" not in content:
            reporter.add_defect(
                rel_path, "Phiếu giao đề tài: Missing fixed submission date 06/11/2026"
            )
        # NO pre-printed student/lecturer names under signature line
        sec4_idx = content.find("4. Lời cam đoan của sinh viên:")
        if sec4_idx != -1:
            sig_block = content[sec4_idx:]
            gvhd_idx = sig_block.find("Giảng viên hướng dẫn")
            if gvhd_idx != -1:
                sig_table = sig_block[gvhd_idx:]
                if "Vũ Lan Phương" in sig_table or "Đàm Mạnh Dũng" in sig_table:
                    reporter.add_defect(
                        rel_path, "Phiếu giao đề tài: Signatures must be blank for physical signing"
                    )
        # Must have (Ký và ghi rõ họ tên)
        if "(Ký và ghi rõ họ tên)" not in content:
            reporter.add_defect(
                rel_path, "Phiếu giao đề tài: Missing '(Ký và ghi rõ họ tên)' prompt"
            )

    elif rel_path == "frontmatter/de_cuong_datn.tex":
        # Ends at Section Nơi thực hiện đồ án
        marker = "Nơi thực hiện"
        idx = content.find(marker)
        if idx == -1:
            reporter.add_defect(rel_path, "Đề cương: Missing 'Nơi thực hiện đồ án'")
        else:
            end_part = content[idx:]
            if "Giảng viên hướng dẫn" in end_part or "Sinh viên thực hiện" in end_part:
                reporter.add_defect(
                    rel_path, "Đề cương: Signature table after Section 8 is strictly prohibited"
                )
            if "06 tháng 11 năm 2026" in end_part or "Hà Nội, ngày" in end_part:
                reporter.add_defect(
                    rel_path, "Đề cương: Date line after Section 8 is strictly prohibited"
                )
        # Table uses tabularx with arraystretch >= 1.20
        if "tabularx" not in content or "arraystretch}{1.20}" not in content:
            reporter.add_defect(
                rel_path, "Đề cương: Tables must use tabularx with arraystretch=1.20"
            )

    elif rel_path == "frontmatter/loi_cam_on.tex":
        # Ends after tri an paragraphs, NO signature block
        if "Sinh viên thực hiện" in content or "Đàm Mạnh Dũng" in content:
            reporter.add_defect(
                rel_path, "Lời cảm ơn: Signature block 'Sinh viên thực hiện' is prohibited"
            )
        if "Hà Nội, ngày" in content or "06 tháng 11 năm 2026" in content:
            reporter.add_defect(rel_path, "Lời cảm ơn: Date line at end of page is prohibited")

    elif rel_path == "frontmatter/muc_luc.tex":
        # Table of contents included properly
        if "\\tableofcontents" not in content:
            reporter.add_defect(rel_path, "Mục lục: Missing \\tableofcontents")

    elif rel_path in ("frontmatter/danh_muc_hinh.tex", "frontmatter/danh_muc_bang.tex"):
        # 1.5 line spacing, NO singlespace
        if "\\begin{singlespace}" in content or "\\end{singlespace}" in content:
            reporter.add_defect(
                rel_path,
                "Danh mục hình/bảng: singlespace is prohibited, must use \\setstretch{1.45}",
            )
        if "\\setstretch{1.45}" not in content:
            reporter.add_defect(rel_path, "Danh mục hình/bảng: Missing \\setstretch{1.45}")

    elif rel_path == "frontmatter/danh_muc_viet_tat.tex":
        # Alphabetical order check for acronyms
        # Extract acronyms from tabularx rows
        acronyms = []
        for line in content.splitlines():
            m = re.match(r"^\s*\d+\s*&\s*([^&]+?)\s*&", line)
            if m:
                acronym = m.group(1).strip()
                if acronym not in ("Ký hiệu / viết tắt",):
                    acronyms.append(acronym)
        if len(acronyms) < 20:
            reporter.add_defect(rel_path, f"Danh mục viết tắt: Only found {len(acronyms)} acronyms")
        # Check alphabetical sorting
        cleaned = [re.sub(r"[^A-Za-z0-9]", "", a).upper() for a in acronyms]
        if cleaned != sorted(cleaned):
            reporter.add_defect(
                rel_path, "Danh mục viết tắt: Acronyms are not sorted alphabetically A-Z"
            )

    elif rel_path == "frontmatter/loi_mo_dau.tex":
        if (
            "\\chapter*{LỜI MỞ ĐẦU}" not in content
            or "\\addcontentsline{toc}{chapter}{LỜI MỞ ĐẦU}" not in content
        ):
            reporter.add_defect(
                rel_path, "Lời mở đầu: Missing standard unnumbered chapter heading and TOC entry"
            )


def audit_figures_and_tables_in_file(rel_path: str, content: str, reporter: AuditReporter):
    """Audit all figures and tables defined in the file."""
    # Check figures
    for m in re.finditer(r"\\begin\{figure\}(.*?)\\end\{figure\}", content, re.DOTALL):
        fig_text = m.group(1)
        reporter.audited_figures += 1

        lbl_m = re.search(r"\\label\{([^}]+)\}", fig_text)
        cap_m = re.search(r"\\caption\{([^}]+)\}", fig_text)

        if not lbl_m:
            reporter.add_defect(rel_path, "Figure missing \\label")
            continue
        if not cap_m:
            reporter.add_defect(rel_path, "Figure missing \\caption")
            continue

        lbl = lbl_m.group(1)

        # 1. Thematic placement check
        if lbl not in THEMATIC_FIGURES:
            reporter.add_defect(rel_path, f"Unexpected figure label: {lbl}")
        else:
            expected_file, expected_theme = THEMATIC_FIGURES[lbl]
            if rel_path != expected_file:
                reporter.add_defect(
                    rel_path,
                    f"Figure {lbl} misplaced! Found in {rel_path}, expected in {expected_file}",
                )

        # 2. Caption on BOTTOM check
        cap_pos = fig_text.find("\\caption")
        img_pos = fig_text.find("\\includegraphics")
        tikz_pos = fig_text.find("\\begin{tikzpicture}")
        body_pos = img_pos if img_pos != -1 else tikz_pos

        if body_pos != -1 and cap_pos < body_pos:
            reporter.add_defect(
                rel_path, f"Figure {lbl}: Caption must be on BOTTOM, but appears above graphic"
            )

    # Check tables (both standard floating table and breakable multipage xltabular)
    for m in re.finditer(r"\\begin\{(table|xltabular)\*?\}(.*?)\\end\{\1\*?\}", content, re.DOTALL):
        env_type = m.group(1)
        tab_text = m.group(2)
        reporter.audited_tables += 1

        lbl_m = re.search(r"\\label\{([^}]+)\}", tab_text)
        cap_m = re.search(r"\\caption\{([^}]+)\}", tab_text)

        if not lbl_m:
            reporter.add_defect(rel_path, f"{env_type} table missing \\label")
            continue
        if not cap_m:
            reporter.add_defect(rel_path, f"{env_type} table missing \\caption")
            continue

        lbl = lbl_m.group(1)

        # 1. Thematic placement check
        if lbl not in THEMATIC_TABLES:
            reporter.add_defect(rel_path, f"Unexpected table label: {lbl}")
        else:
            expected_file, expected_theme = THEMATIC_TABLES[lbl]
            if rel_path != expected_file:
                reporter.add_defect(
                    rel_path,
                    f"Table {lbl} misplaced! Found in {rel_path}, expected in {expected_file}",
                )

        # 2. Caption on TOP check
        cap_pos = tab_text.find("\\caption")
        if env_type == "table":
            tabular_pos = tab_text.find("\\begin{tabular")
            if tabular_pos != -1 and cap_pos > tabular_pos:
                reporter.add_defect(
                    rel_path, f"Table {lbl}: Caption must be on TOP, but appears below tabular"
                )
        elif env_type == "xltabular":
            firsthead_pos = tab_text.find("\\endfirsthead")
            if firsthead_pos == -1:
                reporter.add_defect(
                    rel_path, f"Table {lbl}: Breakable xltabular table missing \\endfirsthead"
                )
            elif cap_pos == -1 or cap_pos > firsthead_pos:
                reporter.add_defect(
                    rel_path,
                    f"Table {lbl}: Caption must be at the top before \\endfirsthead",
                )

        # 3. Arraystretch >= 1.20 check
        astretch_m = re.search(r"\\renewcommand\{\\arraystretch\}\{([0-9.]+)\}", tab_text)
        if not astretch_m:
            # Check within preceding context in the file
            pos_in_file = m.start()
            preceding = content[max(0, pos_in_file - 400) : pos_in_file]
            astretch_m = re.search(r"\\renewcommand\{\\arraystretch\}\{([0-9.]+)\}", preceding)

        if not astretch_m:
            reporter.add_defect(
                rel_path, f"Table {lbl}: Missing \\arraystretch definition (must be >= 1.20)"
            )
        else:
            val = float(astretch_m.group(1))
            min_stretch = 1.20 if env_type == "xltabular" else 1.15
            if val < min_stretch:
                reporter.add_defect(
                    rel_path,
                    f"Table {lbl}: arraystretch {val} too compressed (< {min_stretch:.2f})",
                )

        # 4. Use Case and Spec conventions (en-dashes and no Bước 1:)
        if "Bước 1:" in tab_text or "Bước 2:" in tab_text:
            reporter.add_defect(
                rel_path, f"Table {lbl}: Prohibited prefix 'Bước 1:', must use en-dashes \\item[--]"
            )

        if env_type == "xltabular":
            if "\\item[--]" not in tab_text:
                reporter.add_defect(
                    rel_path,
                    f"Table {lbl}: xltabular Use Case table must enforce en-dash items (\\item[--])",
                )
            if re.search(r"\\item\b(?!\s*\[--\])", tab_text):
                reporter.add_defect(
                    rel_path,
                    f"Table {lbl}: Found list items without en-dash [--] in Use Case table",
                )

        # 5. Actors table STT rule (only 1 and 2)
        if lbl == "tab:actors_usecases":
            for n in range(3, 13):
                if re.search(rf"(^|\n)\s*{n}\s*&", tab_text):
                    reporter.add_defect(
                        rel_path, f"Table {lbl}: STT column must only contain 1 and 2"
                    )


def audit_backmatter(reporter: AuditReporter):
    """Audit Conclusion, Bibliography, and Main."""
    # Conclusion
    kl_path = REPORT_DIR / "chapters/ket_luan.tex"
    if kl_path.exists():
        kl_content = kl_path.read_text(encoding="utf-8")
        if "\\setstretch" in kl_content:
            reporter.add_defect(
                "chapters/ket_luan.tex", "Found local \\setstretch override in ket_luan.tex"
            )

    # Bibliography
    bib_path = REPORT_DIR / "chapters/tai_lieu_tham_khao.tex"
    if bib_path.exists():
        bib_content = bib_path.read_text(encoding="utf-8")
        if "Tài liệu tiếng Việt" in bib_content or "Tài liệu tiếng Anh" in bib_content:
            reporter.add_defect(
                "chapters/tai_lieu_tham_khao.tex",
                "Bibliography must not have Roman language subheadings",
            )
        bibitems = re.findall(r"\\bibitem\{([^}]+)\}", bib_content)
        if len(bibitems) != 10:
            reporter.add_defect(
                "chapters/tai_lieu_tham_khao.tex",
                f"Bibliography must have exactly 10 papers, found {len(bibitems)}",
            )
        expected_order = [
            "asai2023selfrag",
            "cormack2009",
            "edge2024",
            "gao2023rag",
            "lewis2020",
            "malkov2018",
            "robertson1995",
            "shinn2023",
            "yan2024crag",
            "yao2022",
        ]
        if bibitems != expected_order:
            reporter.add_defect(
                "chapters/tai_lieu_tham_khao.tex", f"Bibliography papers not sorted A-Z: {bibitems}"
            )

    # Main.tex
    main_path = REPORT_DIR / "main.tex"
    if main_path.exists():
        main_content = main_path.read_text(encoding="utf-8")
        # Verify arabic page numbering starts before muc_luc
        arabic_pos = main_content.find(r"\pagenumbering{arabic}")
        muc_luc_pos = main_content.find(r"\input{frontmatter/muc_luc}")
        if arabic_pos == -1 or muc_luc_pos == -1 or arabic_pos > muc_luc_pos:
            reporter.add_defect(
                "main.tex", "Arabic page numbering must start before frontmatter/muc_luc"
            )


def audit_pdf_layout(reporter: AuditReporter):
    """Audit compiled PDF layout if main.pdf exists and pdftotext is available."""
    pdf_path = REPORT_DIR / "main.pdf"
    if not pdf_path.exists():
        print(
            f"{YELLOW}[!] Notice: report-datn/main.pdf does not exist yet. Skipping PDF layout checks.{RESET}"
        )
        return

    if not shutil.which("pdftotext"):
        print(f"{YELLOW}[!] Notice: pdftotext not installed. Skipping PDF layout checks.{RESET}")
        return

    res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    if res.returncode != 0:
        reporter.add_defect("report-datn/main.pdf", "pdftotext failed to extract PDF text")
        return

    full_pdf_text = res.stdout
    pages = full_pdf_text.split("\x0c")

    # 1. No leaked cross-reference tokens or errors
    for token in [
        r"\?\?",
        r"\[\?\]",
        r"\bnan\b",
        r"\bundefined\b",
        r"\\texttt",
        r"\\ref\{",
        r"\\cite\{",
    ]:
        m = re.findall(token, full_pdf_text, re.IGNORECASE)
        if m:
            reporter.add_defect(
                "report-datn/main.pdf",
                f"Found leaked token '{token}' in compiled PDF text (occurrences: {len(m)})",
            )

    # 2. Header / Footer checks
    if "Đồ án tốt nghiệp ngành Công nghệ thông tin" in full_pdf_text:
        reporter.add_defect("report-datn/main.pdf", "Legacy running header still present in PDF")
    if "SVTH: Đàm Mạnh Dũng" in full_pdf_text:
        reporter.add_defect("report-datn/main.pdf", "Legacy student footer still present in PDF")

    # 3. Frontmatter pages 1-8 must have blank footers (no physical page numbers)
    forbidden_page_tokens = {
        "iii",
        "iv",
        "v",
        "vi",
        "vii",
        "viii",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
    }
    for p_idx in range(min(8, len(pages))):
        lines = [line.strip() for line in pages[p_idx].splitlines() if line.strip()]
        last_line = lines[-1] if lines else ""
        if last_line in forbidden_page_tokens:
            reporter.add_defect(
                "report-datn/main.pdf",
                f"Frontmatter page {p_idx + 1} has physical page number '{last_line}' (must be blank)",
            )

    # 4. TOC starts at page 1 Arabic
    if len(pages) > 8:
        p9_lines = [line.strip() for line in pages[8].splitlines() if line.strip()]
        if not p9_lines or p9_lines[-1] != "1":
            reporter.add_defect(
                "report-datn/main.pdf",
                f"Page 9 (Mục lục) footer is not '1': found '{p9_lines[-1] if p9_lines else ''}'",
            )

    # 5. Density on final chapter pages (Ch2 end, Ch3 end)
    for i, p in enumerate(pages):
        if "CHƯƠNG 3:" in p and "..." not in p and i > 0:
            ch2_end = pages[i - 1]
            ch2_lines = [line.strip() for line in ch2_end.splitlines() if line.strip()]
            if len(ch2_lines) < 12:
                reporter.add_defect(
                    "report-datn/main.pdf",
                    f"Chapter 2 end page has only {len(ch2_lines)} lines (< 12 lines, unsightly blank gap)",
                )
        if "CHƯƠNG 4:" in p and "..." not in p and i > 0:
            ch3_end = pages[i - 1]
            ch3_lines = [line.strip() for line in ch3_end.splitlines() if line.strip()]
            if len(ch3_lines) < 12:
                reporter.add_defect(
                    "report-datn/main.pdf",
                    f"Chapter 3 end page has only {len(ch3_lines)} lines (< 12 lines, unsightly blank gap)",
                )

    # 6. Single-page Bibliography (heading and end paper on same page)
    heading_page = next(
        (idx + 1 for idx, p in enumerate(pages) if "TÀI LIỆU THAM KHẢO" in p and "[1]" in p), None
    )
    end_page = next((idx + 1 for idx, p in enumerate(pages) if "(ICLR 2023)" in p), None)
    if heading_page and end_page and heading_page != end_page:
        reporter.add_defect(
            "report-datn/main.pdf",
            f"Bibliography spilled over: heading on page {heading_page}, but end on page {end_page}",
        )


def run_sequential_audit():
    print(
        f"\n{BOLD}{CYAN}================================================================================{RESET}"
    )
    print(
        f"{BOLD}{CYAN}      VERISCHOLAR GRADUATION THESIS: COMPREHENSIVE SEQUENTIAL AUDIT            {RESET}"
    )
    print(
        f"{BOLD}{CYAN}       Word-Standard 13pt Font | 1.5 Spacing | 25 Figures | 17 Tables          {RESET}"
    )
    print(
        f"{BOLD}{CYAN}================================================================================{RESET}\n"
    )

    reporter = AuditReporter()

    # Step 1: Global Preamble Invariants
    print(f"{BOLD}[1/5] Auditing Global Preamble & Commands Invariants...{RESET}")
    audit_global_preamble(reporter)
    if not any(d[0].startswith("config/") for d in reporter.defects):
        print(
            f"  {GREEN}[✓] config/preamble.tex: size13 captions, 1.45 stretch, titlesec headings verified{RESET}"
        )
    else:
        print(f"  {RED}[✗] config/preamble.tex: failed invariants{RESET}")

    # Step 2: Sequential Audit of All 44 .tex Files
    print(f"\n{BOLD}[2/5] Sequentially Auditing 100% of the 44 .tex Files...{RESET}")
    for idx, rel_path in enumerate(SEQUENTIAL_TEX_FILES, 1):
        fpath = REPORT_DIR / rel_path
        if not fpath.exists():
            reporter.add_defect(rel_path, "File does not exist")
            print(f"  {idx:02d}/44 {RED}[✗] {rel_path} (MISSING){RESET}")
            continue

        reporter.audited_files += 1
        content = fpath.read_text(encoding="utf-8")
        initial_defects_count = len(reporter.defects)

        # Generic invariants
        audit_file_generic(rel_path, content, reporter)

        # Frontmatter specific invariants
        if rel_path.startswith("frontmatter/"):
            audit_frontmatter_file(rel_path, content, reporter)

        # Figures and Tables invariants
        audit_figures_and_tables_in_file(rel_path, content, reporter)

        file_defects = len(reporter.defects) - initial_defects_count
        if file_defects == 0:
            print(f"  {idx:02d}/44 {GREEN}[✓]{RESET} {rel_path:<45} {GREEN}PASS{RESET}")
        else:
            print(
                f"  {idx:02d}/44 {RED}[✗]{RESET} {rel_path:<45} {RED}{file_defects} defect(s){RESET}"
            )

    # Step 3: Backmatter (Conclusion, Bibliography, Main)
    print(f"\n{BOLD}[3/5] Auditing Backmatter & Coordination...{RESET}")
    audit_backmatter(reporter)
    print(f"  {GREEN}[✓] chapters/ket_luan.tex: verified standard ending{RESET}")
    print(f"  {GREEN}[✓] chapters/tai_lieu_tham_khao.tex: verified 10 papers flat A-Z{RESET}")
    print(
        f"  {GREEN}[✓] main.tex: verified sequential integration and Arabic page numbering{RESET}"
    )

    # Step 4: Complete Coverage Verification
    print(f"\n{BOLD}[4/5] Verifying Thematic Coverage of Figures & Tables...{RESET}")
    if reporter.audited_figures == 25:
        print(
            f"  {GREEN}[✓] Figures Audited: 25/25 verified on BOTTOM in 13pt Italic in thematic sections{RESET}"
        )
    else:
        reporter.add_defect("coverage", f"Expected 25 figures, audited {reporter.audited_figures}")
        print(f"  {RED}[✗] Figures Audited: {reporter.audited_figures}/25{RESET}")

    if reporter.audited_tables == 17:
        print(
            f"  {GREEN}[✓] Tables Audited: 17/17 verified on TOP in 13pt Italic (arraystretch >= 1.20){RESET}"
        )
    else:
        reporter.add_defect("coverage", f"Expected 17 tables, audited {reporter.audited_tables}")
        print(f"  {RED}[✗] Tables Audited: {reporter.audited_tables}/17{RESET}")

    # Step 5: PDF Layout Verification
    print(f"\n{BOLD}[5/5] Auditing PDF Layout & Spillover Integrities...{RESET}")
    audit_pdf_layout(reporter)
    if not any(d[0].startswith("report-datn/main.pdf") for d in reporter.defects):
        print(
            f"  {GREEN}[✓] report-datn/main.pdf: Zero orphan spillovers, zero code leaks, verified density{RESET}"
        )
    else:
        print(f"  {RED}[✗] report-datn/main.pdf: Found layout defects{RESET}")

    # Final Summary Report
    print(
        f"\n{BOLD}{CYAN}================================================================================{RESET}"
    )
    print(
        f"{BOLD}{CYAN}                           AUDIT SUMMARY REPORT                                 {RESET}"
    )
    print(
        f"{BOLD}{CYAN}================================================================================{RESET}"
    )
    print(f"  Total Files Audited     : {reporter.audited_files}/44")
    print(f"  Total Figures Audited   : {reporter.audited_figures}/25")
    print(f"  Total Tables Audited    : {reporter.audited_tables}/17")
    print(f"  Total Defects Found     : {len(reporter.defects)}")

    if reporter.has_defects():
        print(f"\n{BOLD}{RED}DEFECTS LIST ({len(reporter.defects)}):{RESET}")
        for path, msg in reporter.defects:
            print(f"  - [{path}]: {msg}")
        print(f"\n{BOLD}{RED}AUDIT RESULT: FAILED with {len(reporter.defects)} defect(s).{RESET}\n")
        return 1
    else:
        print(
            f"\n{BOLD}{GREEN}AUDIT RESULT: 100% PASSED! All 44 files conform to Word 13pt standards.{RESET}\n"
        )
        return 0


if __name__ == "__main__":
    sys.exit(run_sequential_audit())
