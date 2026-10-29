"""Structured parser for TeX/LaTeX compilation log output.

Extracts structured LatexDiagnostic records (file, line, column, severity,
message, context, hint) from compiler output logs.
"""

from __future__ import annotations

import re
from typing import Literal, TypedDict


class LatexDiagnostic(TypedDict):
    """Structured diagnostic representation of a LaTeX error or warning."""

    file: str
    line: int
    column: int
    severity: Literal["error", "warning", "info"]
    message: str
    context: str
    hint: str


class LatexLogParser:
    """Structured parser extracting errors and warnings from raw LaTeX compiler logs."""

    @classmethod
    def parse_log(cls, raw_log: str) -> list[LatexDiagnostic]:
        """Parse raw compiler log text and return structured list of LatexDiagnostic items."""
        if not raw_log or not raw_log.strip():
            return []

        diagnostics: list[LatexDiagnostic] = []
        lines = raw_log.splitlines()
        total_lines = len(lines)
        current_file = "main.tex"

        # Regex patterns
        line_context_re = re.compile(r"^l\.(\d+)\s*(.*)$")
        file_line_error_re = re.compile(r"^(?:\./)?([a-zA-Z0-9_\-.]+\.tex):(\d+):\s*(.*)$")
        warning_re = re.compile(
            r"^(?:LaTeX|Package\s+[\w\-]+)\s+Warning:\s*(.*?)(?:\s+on input line\s+(\d+)\.|\.|$)",
            re.IGNORECASE,
        )
        warning_with_line_re = re.compile(r"on input line\s+(\d+)\.?", re.IGNORECASE)
        file_open_re = re.compile(r"\(([./a-zA-Z0-9_\-]+\.tex)\b")

        i = 0
        while i < total_lines:
            line = lines[i].rstrip()

            # Track active TeX file if visible in log
            file_match = file_open_re.search(line)
            if file_match:
                file_cand = file_match.group(1).lstrip("./")
                if file_cand:
                    current_file = file_cand

            # 0. GCC-style file:line:error format
            file_line_m = file_line_error_re.match(line)
            if file_line_m:
                matched_file = file_line_m.group(1).lstrip("./")
                line_num = int(file_line_m.group(2))
                error_msg = file_line_m.group(3).strip()
                diagnostics.append(
                    LatexDiagnostic(
                        file=matched_file or current_file,
                        line=line_num,
                        column=1,
                        severity="error",
                        message=error_msg,
                        context=line,
                        hint=cls._generate_hint("error", error_msg),
                    )
                )
                i += 1
                continue

            # 1. Error block starting with "! "
            if line.startswith("!"):
                error_msg = line[1:].strip()
                # Skip cascade fatal markers that are not root causes
                if error_msg.startswith("==> Fatal error occurred"):
                    i += 1
                    continue
                if error_msg == "Emergency stop." and diagnostics:
                    i += 1
                    continue

                line_num = 1
                col_num = 1
                context_str = ""

                # Check if error message itself contains "on input line (\d+)"
                m_inline = warning_with_line_re.search(error_msg)
                if m_inline:
                    line_num = int(m_inline.group(1))

                # Scan ahead for line indicator (e.g. "l.42 \invalidcommand")
                j = i + 1
                lookahead_limit = min(total_lines, i + 12)
                while j < lookahead_limit:
                    candidate = lines[j].strip()
                    if candidate.startswith("!"):
                        break
                    m_line = line_context_re.match(candidate)
                    if m_line:
                        line_num = int(m_line.group(1))
                        context_str = m_line.group(2).strip()
                        if j + 1 < total_lines and lines[j + 1].startswith(" "):
                            continuation = lines[j + 1].strip()
                            if continuation:
                                context_str = f"{context_str} {continuation}".strip()
                        break
                    m_cand_inline = warning_with_line_re.search(candidate)
                    if m_cand_inline and line_num == 1:
                        line_num = int(m_cand_inline.group(1))
                    j += 1

                diagnostics.append(
                    LatexDiagnostic(
                        file=current_file,
                        line=line_num,
                        column=col_num,
                        severity="error",
                        message=error_msg,
                        context=context_str,
                        hint=cls._generate_hint("error", error_msg),
                    )
                )
                i = j if j > i + 1 else i + 1
                continue

            # 2. Warning block (LaTeX Warning or Package Warning)
            if "Warning:" in line:
                w_match = warning_re.match(line)
                if w_match:
                    warn_body = w_match.group(1).strip()
                    line_str = w_match.group(2)
                    line_num = int(line_str) if line_str else 1
                    context_str = line

                    # Check if warning spans onto next line
                    j = i + 1
                    while line_str is None and j < min(total_lines, i + 4) and lines[j].strip():
                        sub_line = lines[j].strip()
                        m_sub_line = warning_with_line_re.search(sub_line)
                        if m_sub_line:
                            line_num = int(m_sub_line.group(1))
                            warn_body = f"{warn_body} {sub_line}".strip()
                            context_str = f"{context_str} {sub_line}".strip()
                            break
                        if not sub_line.startswith(("!", "LaTeX", "Package")):
                            warn_body = f"{warn_body} {sub_line}".strip()
                            context_str = f"{context_str} {sub_line}".strip()
                        j += 1

                    diagnostics.append(
                        LatexDiagnostic(
                            file=current_file,
                            line=line_num,
                            column=1,
                            severity="warning",
                            message=warn_body or line,
                            context=context_str,
                            hint=cls._generate_hint("warning", warn_body or line),
                        )
                    )
                    i += 1
                    continue

            i += 1

        return diagnostics

    @classmethod
    def _generate_hint(cls, severity: str, message: str) -> str:
        msg_lower = message.lower()
        if "undefined control sequence" in msg_lower:
            return (
                "Kiểm tra lại cú pháp tên lệnh LaTeX hoặc nạp gói bổ trợ cần thiết "
                "(\\usepackage{...}) trong phần preamble."
            )
        if "citation" in msg_lower and "undefined" in msg_lower:
            return (
                "Khóa trích dẫn chưa tồn tại trong references.bib hoặc cần chạy lại bibtex/biber."
            )
        if "reference" in msg_lower and "undefined" in msg_lower:
            return "Nhãn tham chiếu \\label tương ứng chưa được khai báo trong tài liệu."
        if "file" in msg_lower and "not found" in msg_lower:
            return "Tệp hoặc gói LaTeX không tìm thấy trong thư mục dự án hoặc hệ thống."
        if "missing $" in msg_lower:
            return (
                "Ký tự toán học nằm ngoài môi trường công thức toán. Hãy bọc bằng $...$ "
                "hoặc \\begin{equation}."
            )
        if "environment" in msg_lower and "undefined" in msg_lower:
            return (
                "Môi trường chưa được định nghĩa. Hãy bổ sung gói macro tương ứng trong preamble."
            )
        if severity == "error":
            return "Kiểm tra cú pháp mã LaTeX quanh vị trí dòng được chỉ định."
        return "Cảnh báo định dạng hoặc tham chiếu; tài liệu vẫn có thể xuất PDF."
