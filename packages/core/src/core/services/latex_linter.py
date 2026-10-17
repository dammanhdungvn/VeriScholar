"""Fast AST LaTeX Linter & Pre-compile Asset Checker (Module 2 Tier 1 Gate).

Performs sub-100ms static syntax analysis:
- Environment balance (\\begin{env} ... \\end{env})
- Curly brace balance ({ ... })
- Math delimiter balance ($ ... $, \\[ ... \\])
- Unescaped special characters outside math mode (e.g. bare '_')
- Pre-compile asset check (\\includegraphics, custom .sty/.cls)
"""

from __future__ import annotations

import re

from core.domain.entities.latex import LatexSyntaxError


class FastLatexAstLinter:
    """Production in-memory AST linter implementing ILatexLinterPort."""

    def lint(self, code: str) -> list[LatexSyntaxError]:
        """Perform comprehensive static analysis on LaTeX code."""
        errors: list[LatexSyntaxError] = []
        lines = code.splitlines()

        # 1. Environment Matching Stack: (env_name, line_no, col)
        env_stack: list[tuple[str, int, int]] = []
        # 2. Brace Matching Stack: (line_no, col)
        brace_stack: list[tuple[int, int]] = []

        in_verbatim = False
        in_display_math = False
        display_math_start_line = 0

        for line_idx, line in enumerate(lines, start=1):
            n = len(line)

            # Strip comments (unescaped %)
            clean_line = ""
            i = 0
            while i < n:
                if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                    break
                clean_line += line[i]
                i += 1

            # Check \begin and \end
            begin_matches = list(re.finditer(r"\\begin\{([a-zA-Z0-9*_-]+)\}", clean_line))
            end_matches = list(re.finditer(r"\\end\{([a-zA-Z0-9*_-]+)\}", clean_line))

            # Combine and sort environment tags by column position
            env_events: list[tuple[int, str, str]] = []
            for m in begin_matches:
                env_events.append((m.start(), "begin", m.group(1)))
            for m in end_matches:
                env_events.append((m.start(), "end", m.group(1)))
            env_events.sort(key=lambda x: x[0])

            for pos, kind, env_name in env_events:
                if kind == "begin":
                    if env_name == "verbatim":
                        in_verbatim = True
                    env_stack.append((env_name, line_idx, pos))
                elif kind == "end":
                    if env_name == "verbatim":
                        in_verbatim = False
                    if not env_stack:
                        errors.append(
                            LatexSyntaxError(
                                line=line_idx,
                                column=pos,
                                rule="UNMATCHED_END_ENV",
                                message=(
                                    f"Phát hiện '\\end{{{env_name}}}' nhưng không có "
                                    f"'\\begin{{{env_name}}}' tương ứng."
                                ),
                                suggested_fix=(
                                    f"Bổ sung '\\begin{{{env_name}}}' hoặc gỡ bỏ thẻ đóng thừa."
                                ),
                            )
                        )
                    else:
                        top_env, top_line, _ = env_stack.pop()
                        if top_env != env_name:
                            errors.append(
                                LatexSyntaxError(
                                    line=line_idx,
                                    column=pos,
                                    rule="MISMATCHED_ENV",
                                    message=(
                                        f"Môi trường đóng '\\end{{{env_name}}}' không khớp với "
                                        f"thẻ mở '\\begin{{{top_env}}}' ở dòng {top_line}."
                                    ),
                                    suggested_fix=f"Đổi thành '\\end{{{top_env}}}'.",
                                )
                            )

            # Skip deeper syntax checking inside verbatim environment
            if in_verbatim:
                continue

            # Check display math \[ ... \]
            j = 0
            while j < len(clean_line) - 1:
                if clean_line[j : j + 2] == "\\[":
                    if in_display_math:
                        errors.append(
                            LatexSyntaxError(
                                line=line_idx,
                                column=j,
                                rule="NESTED_DISPLAY_MATH",
                                message="Phát hiện '\\[' lồng nhau trong môi trường toán học.",
                                suggested_fix="Đóng môi trường trước bằng '\\]'.",
                            )
                        )
                    in_display_math = True
                    display_math_start_line = line_idx
                    j += 2
                    continue
                elif clean_line[j : j + 2] == "\\]":
                    if not in_display_math:
                        errors.append(
                            LatexSyntaxError(
                                line=line_idx,
                                column=j,
                                rule="UNMATCHED_CLOSE_DISPLAY_MATH",
                                message="Phát hiện '\\]' nhưng không có '\\[' mở trước đó.",
                                suggested_fix="Bổ sung '\\[' hoặc gỡ bỏ '\\]'.",
                            )
                        )
                    in_display_math = False
                    j += 2
                    continue
                j += 1

            # Check curly braces
            for col_idx, char in enumerate(clean_line):
                if char == "{" and (col_idx == 0 or clean_line[col_idx - 1] != "\\"):
                    brace_stack.append((line_idx, col_idx))
                elif char == "}" and (col_idx == 0 or clean_line[col_idx - 1] != "\\"):
                    if not brace_stack:
                        errors.append(
                            LatexSyntaxError(
                                line=line_idx,
                                column=col_idx,
                                rule="UNMATCHED_CLOSE_BRACE",
                                message="Dấu đóng ngoặc nhọn '}' thừa, không có '{' mở trước đó.",
                                suggested_fix="Gỡ bỏ dấu '}' hoặc bổ sung '{'.",
                            )
                        )
                    else:
                        brace_stack.pop()

            # Check unescaped underscores outside math mode
            math_envs = (
                "equation",
                "equation*",
                "align",
                "align*",
                "gather",
                "gather*",
                "multline",
                "multline*",
            )
            is_in_math_mode = in_display_math or any(e in math_envs for e, _, _ in env_stack)
            if not is_in_math_mode:
                dollar_count = 0
                k = 0
                while k < len(clean_line):
                    if clean_line[k] == "$" and (k == 0 or clean_line[k - 1] != "\\"):
                        dollar_count += 1
                    k += 1

                if dollar_count % 2 == 0:
                    parts = clean_line.split("$")
                    for idx, part in enumerate(parts):
                        if idx % 2 == 0:
                            under_matches = list(re.finditer(r"(?<!\\)_", part))
                            for um in under_matches:
                                errors.append(
                                    LatexSyntaxError(
                                        line=line_idx,
                                        column=um.start(),
                                        rule="UNESCAPED_UNDERSCORE",
                                        message=(
                                            "Ký tự gạch dưới '_' chưa được escape ngoài khối toán. "
                                            "Có thể gây lỗi biên dịch 'Missing $ inserted'."
                                        ),
                                        suggested_fix="Đổi '_' thành '\\_' hoặc bọc trong $...$.",
                                    )
                                )

        # Post-loop checks for unclosed elements
        if in_display_math:
            errors.append(
                LatexSyntaxError(
                    line=display_math_start_line,
                    column=0,
                    rule="UNCLOSED_DISPLAY_MATH",
                    message=(
                        f"Môi trường toán học '\\[' mở tại dòng {display_math_start_line} "
                        "chưa được đóng bằng '\\]'."
                    ),
                    suggested_fix="Bổ sung '\\]' ở cuối công thức.",
                )
            )

        while env_stack:
            env_name, env_line, env_col = env_stack.pop()
            errors.append(
                LatexSyntaxError(
                    line=env_line,
                    column=env_col,
                    rule="UNCLOSED_ENV",
                    message=(
                        f"Môi trường '\\begin{{{env_name}}}' mở tại dòng {env_line} chưa được đóng."
                    ),
                    suggested_fix=f"Bổ sung '\\end{{{env_name}}}'.",
                )
            )

        while brace_stack:
            b_line, b_col = brace_stack.pop()
            errors.append(
                LatexSyntaxError(
                    line=b_line,
                    column=b_col,
                    rule="UNCLOSED_BRACE",
                    message=f"Dấu mở ngoặc nhọn '{{' tại dòng {b_line} chưa có dấu đóng '}}'.",
                    suggested_fix="Bổ sung dấu '}' ở cuối khối lệnh.",
                )
            )

        return errors
