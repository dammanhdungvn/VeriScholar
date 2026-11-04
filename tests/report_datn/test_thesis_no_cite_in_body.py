import re
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parents[2] / "report-datn"


def test_no_cite_commands_in_chapters():
    chapter_files = list((REPORT_DIR / "chapters").glob("**/*.tex"))
    # Exclude tai_lieu_tham_khao.tex which defines bibitems
    body_files = [f for f in chapter_files if f.name != "tai_lieu_tham_khao.tex"]

    violations = []
    for f in body_files:
        content = f.read_text(encoding="utf-8")
        matches = re.findall(r"\\cite\{[^}]+\}", content)
        if matches:
            violations.append(f"{f.name}: {matches}")

    assert not violations, f"Phát hiện lệnh \\cite trong thân bài: {violations}"


def test_no_conversational_author_phrases():
    chapter_files = list((REPORT_DIR / "chapters").glob("**/*.tex"))
    body_files = [f for f in chapter_files if f.name != "tai_lieu_tham_khao.tex"]

    forbidden_phrases = [
        "và cộng sự",
        "do Lewis",
        "theo khảo sát của Gao",
        "do Asai",
        "do Yan",
        "của Cockburn",
        "do Yao",
        "của Shinn",
        "của Weng",
    ]
    violations = []
    for f in body_files:
        content = f.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            if phrase in content:
                violations.append(f"{f.name}: chứa '{phrase}'")
    assert not violations, f"Phát hiện tên tác giả kể lể trong thân bài: {violations}"
