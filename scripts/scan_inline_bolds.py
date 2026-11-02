import re
from pathlib import Path

CHAPTERS_DIR = Path("report-datn/chapters")


def find_casual_bolds():
    findings = []
    for tex_file in sorted(CHAPTERS_DIR.rglob("*.tex")):
        lines = tex_file.read_text(encoding="utf-8").splitlines()
        in_table = False
        in_tikz = False
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if "\\begin{tabular" in stripped or "\\begin{table" in stripped:
                in_table = True
            if "\\end{tabular" in stripped or "\\end{table" in stripped:
                in_table = False
                continue
            if in_table:
                continue

            if "\\begin{tikzpicture}" in stripped:
                in_tikz = True
            if "\\end{tikzpicture}" in stripped:
                in_tikz = False
                continue
            if in_tikz:
                continue

            if stripped.startswith("%"):
                continue

            # Look for \textbf{...}
            matches = list(re.finditer(r"\\textbf\{([^{}]+(?:\{[^{}]*\}[^{}]*)*)\}", line))
            for m in matches:
                span_start = m.start()
                prefix = line[:span_start].strip()
                inner_text = m.group(1).strip()
                # Check if this bold is at the start of an item (label)
                if (
                    prefix.endswith("\\item")
                    or prefix.endswith("\\item[]")
                    or prefix.endswith("\\item[--]")
                    or prefix.endswith("\\item[-]")
                    or prefix == ""
                    or prefix.endswith("\\noindent")
                ):
                    # It's an item label / leading heading
                    continue
                if "label=\\textbf{" in line:
                    continue
                if "caption" in prefix or "titleformat" in prefix:
                    continue

                # It is a casual in-sentence bold!
                findings.append(
                    {
                        "file": str(tex_file),
                        "line_num": idx,
                        "text": m.group(0),
                        "inner": inner_text,
                        "line": stripped,
                    }
                )
    return findings


if __name__ == "__main__":
    findings = find_casual_bolds()
    print(f"Total casual bold findings: {len(findings)}")
    for f in findings:
        print(f"{f['file']}:{f['line_num']} -> {f['text']}")
    assert len(findings) == 0, f"Found {len(findings)} casual inline bolds that must be cleaned!"
    print("ALL CASUAL INLINE BOLDS CLEANED!")
