"""Formatters, smart terminal printers, and snapshot report generators for VeriScholar."""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.eval.config import (
    ARTIFACTS_DIR,
    LEGACY_REPORTS_DIR,
    REPORTS_DIR,
    TEMP_OUTPUT_TEST_DIR,
)


def compute_sha256(data: Any) -> str:
    """Computes SHA-256 hash string for arbitrary JSON-serializable structure."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def check_and_prepare_output_file(report_filename: str | Path, interactive: bool = False) -> Path:
    """Checks if the target markdown report file already exists in temp/output/test/.

    If exists, either prompts the developer for overwrite permission or cleanly refreshes it.
    """
    TEMP_OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    report_path = (
        report_filename
        if isinstance(report_filename, Path) and report_filename.is_absolute()
        else TEMP_OUTPUT_TEST_DIR / Path(report_filename).name
    )

    if report_path.exists():
        if interactive:
            sys.stdout.write(
                f"\n[?] Tệp '{report_path.name}' đã tồn tại trong temp/output/test/.\n"
                "    Bạn có muốn làm mới và ghi đè? (y/n): "
            )
            sys.stdout.flush()
            choice = sys.stdin.readline().strip().lower()
            if choice not in ("y", "yes"):
                print("    [!] Hủy tiến trình ghi đè báo cáo theo yêu cầu.")
                return report_path

        print(f"[*] Tệp báo cáo cũ đã tồn tại: {report_path.name} -> Tự động làm mới (Clean Refresh)...")
        try:
            report_path.unlink()
        except OSError:
            pass

    return report_path


def save_raw_artifact(endpoint_name: str, test_scenario: str, payload: Any) -> tuple[Path, str]:
    """Saves raw API response into hermetic artifact folder, decoupled from report Markdown."""
    target_dir = ARTIFACTS_DIR / endpoint_name
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{test_scenario}.json"
    file_path = target_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return file_path, compute_sha256(payload)


def fold_heavy_payload(data: Any, max_list_items: int = 3) -> Any:
    """Recursively folds massive data fields (embeddings, base64 strings, long lists)

    to ensure logs and markdown summaries never cause context overflow (< 50 KB).
    """
    if isinstance(data, dict):
        folded: dict[str, Any] = {}
        for k, v in data.items():
            # 1. Fold high-dimensional float vectors (e.g. embeddings)
            if k in ("embedding", "embeddings", "vector", "vectors", "dense_vector") and isinstance(
                v, list
            ):
                folded[k] = f"[float x {len(v)} dimensions]"
            # 2. Fold binary/base64 strings
            elif (
                k in ("thumbnail", "thumbnail_base64", "pdf_bytes")
                and isinstance(v, str)
                and len(v) > 100
            ):
                folded[k] = f"[base64 string ({len(v)} bytes)]"
            # 3. Fold long item lists (e.g. chunks, pages)
            elif isinstance(v, list) and len(v) > max_list_items:
                folded[k] = [
                    fold_heavy_payload(v[0], max_list_items),
                    f"... {len(v) - 2} items folded (inspect via CLI) ...",
                    fold_heavy_payload(v[-1], max_list_items),
                ]
            else:
                folded[k] = fold_heavy_payload(v, max_list_items)
        return folded
    elif isinstance(data, list):
        if len(data) > max_list_items:
            return [
                fold_heavy_payload(data[0], max_list_items),
                f"... {len(data) - 2} items folded (inspect via CLI) ...",
                fold_heavy_payload(data[-1], max_list_items),
            ]
        return [fold_heavy_payload(x, max_list_items) for x in data]
    return data


def smart_fold_for_terminal(data: Any, max_list_items: int = 2, max_str_len: int = 200) -> Any:
    """Intelligently folds massive fields (vectors, binaries, base64, long arrays)

    for terminal display to keep the screen readable, fast, and prevent freezing.
    """
    if isinstance(data, (bytes, bytearray)):
        return f"[Binary stream: {len(data):,} bytes]"

    if isinstance(data, str):
        if data.startswith("data:image/") or (len(data) > 500 and " " not in data[:100]):
            return f"[base64 payload ({len(data):,} bytes)]"
        if len(data) > max_str_len:
            return data[:max_str_len] + f"... [{len(data) - max_str_len} ký tự tiếp theo]"
        return data

    if isinstance(data, dict):
        folded: dict[str, Any] = {}
        for k, v in data.items():
            # Vectors
            if k in ("embedding", "embeddings", "vector", "vectors", "dense_vector") and isinstance(
                v, list
            ):
                if v and all(isinstance(x, (int, float)) for x in v[:5]):
                    preview = f"{v[0]:.3f}, {v[1]:.3f}, ... {v[-1]:.3f}" if len(v) >= 2 else ""
                    folded[k] = f"[float vector x {len(v)} dimensions: {preview}]"
                    continue
            # Binaries / Base64
            if (
                k in ("thumbnail", "thumbnail_base64", "pdf_bytes", "content_bytes")
                and isinstance(v, str)
                and len(v) > 80
            ):
                folded[k] = f"[base64 payload ({len(v):,} bytes)]"
                continue
            folded[k] = smart_fold_for_terminal(v, max_list_items, max_str_len)
        return folded

    if isinstance(data, list):
        if not data:
            return []
        # Float vector check
        if len(data) > 10 and all(isinstance(x, (int, float)) for x in data[:5]):
            preview = f"{data[0]:.3f}, {data[1]:.3f}, ... {data[-1]:.3f}"
            return f"[float vector x {len(data)} dimensions: {preview}]"

        if len(data) > max_list_items:
            first_folded = smart_fold_for_terminal(data[0], max_list_items, max_str_len)
            folded_list = [first_folded]
            if max_list_items >= 2 and len(data) > 2:
                second_folded = smart_fold_for_terminal(data[1], max_list_items, max_str_len)
                folded_list.append(second_folded)
            folded_list.append(
                f"... [{len(data) - len(folded_list)} phần tử đã được gấp gọn - xem toàn bộ tại file markdown] ..."
            )
            folded_list.append(smart_fold_for_terminal(data[-1], max_list_items, max_str_len))
            return folded_list

        return [smart_fold_for_terminal(x, max_list_items, max_str_len) for x in data]

    return data


def format_terminal_box(
    method: str,
    path: str,
    req_headers: dict[str, Any] | None,
    form_data: dict[str, Any] | None,
    req_body: Any | None,
    status_code: int,
    latency_ms: float,
    res_headers: dict[str, Any] | None,
    res_body: Any | None,
    quality_checks: list[tuple[bool, str]],
) -> str:
    """Renders a beautiful 3-part boxed HTTP Exchange view for developer & AI terminal inspection."""
    lines: list[str] = []
    w = 78

    # 1. REQUEST INPUT BOX
    lines.append("┌── [REQUEST INPUT] " + "─" * (w - 20))
    lines.append(f"│ METHOD : {method} {path}")
    if req_headers:
        lines.append("│ HEADERS:")
        for k, v in req_headers.items():
            lines.append(f"│   {k:<13}: {v}")
    if form_data:
        lines.append("│ FORM-DATA:")
        for k, v in form_data.items():
            lines.append(f"│   {k:<13}: {v}")
    elif req_body is not None:
        lines.append("│ BODY:")
        folded_req = smart_fold_for_terminal(req_body)
        body_json = json.dumps(folded_req, indent=2, ensure_ascii=False)
        for bline in body_json.splitlines():
            lines.append(f"│ {bline}")
    lines.append("└" + "─" * (w - 1))

    # 2. RESPONSE OUTPUT BOX
    res_title = f"HTTP {status_code} | {latency_ms:.1f} ms"
    lines.append(f"\n┌── [RESPONSE OUTPUT] ({res_title}) " + "─" * max(2, w - 24 - len(res_title)))
    if res_headers:
        lines.append("│ HEADERS:")
        for k in ("content-type", "x-request-id", "content-length"):
            if k in res_headers:
                lines.append(f"│   {k:<13}: {res_headers[k]}")
    lines.append("│ BODY:")
    if isinstance(res_body, (bytes, bytearray)):
        lines.append(f"│ [Binary stream payload: {len(res_body):,} bytes - application/pdf]")
    elif res_body is not None:
        folded_res = smart_fold_for_terminal(res_body)
        body_str = (
            json.dumps(folded_res, indent=2, ensure_ascii=False)
            if isinstance(folded_res, (dict, list))
            else str(folded_res)
        )
        for bline in body_str.splitlines():
            lines.append(f"│ {bline}")
    lines.append("└" + "─" * (w - 1))

    # 3. QUALITY CHECK MATRIX BOX
    lines.append("\n┌── [KIỂM CHỨNG CHẤT LƯỢNG NGHIỆP VỤ] " + "─" * (w - 38))
    for passed, detail in quality_checks:
        icon = "✓" if passed else "✗"
        lines.append(f"│ {icon} {detail}")
    lines.append("└" + "─" * (w - 1))

    return "\n".join(lines)


def write_markdown_report(report_name: str, content: str) -> Path:
    """Writes standardized evaluation markdown report into temp/output/test/ and mirrors to legacy."""
    TEMP_OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    report_path = TEMP_OUTPUT_TEST_DIR / Path(report_name).name

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    # Mirror to legacy docs/eval-reports for backward compatibility
    try:
        LEGACY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        legacy_path = LEGACY_REPORTS_DIR / Path(report_name).name
        with open(legacy_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
    except OSError:
        pass

    return report_path
