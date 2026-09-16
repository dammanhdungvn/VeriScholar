"""Formatters, smart terminal printers, and snapshot report generators for VeriScholar."""

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from scripts.eval.config import (
    ARTIFACTS_DIR,
    TEMP_OUTPUT_TEST_DIR,
)


def compute_sha256(data: Any) -> str:
    """Computes SHA-256 hash string for arbitrary JSON-serializable structure."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def check_and_prepare_output_file(report_filename: str | Path, interactive: bool = False) -> Path:
    """Checks if the target markdown report file already exists in temp/output/test/.

    If it exists:
    - If interactive=True, prompts the user (y/n) to overwrite.
    - If interactive=False (default/CI), cleanly deletes the old report and prepares for refresh.
    """
    TEMP_OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    target_path = TEMP_OUTPUT_TEST_DIR / Path(report_filename).name

    if target_path.exists():
        if interactive:
            print(
                f"\n[CẢNH BÁO] Tệp báo cáo '{target_path.name}' đã tồn tại tại {TEMP_OUTPUT_TEST_DIR}."
            )
            choice = (
                input("Bạn có muốn ghi đè và làm mới snapshot này không? (y/N): ").strip().lower()
            )
            if choice not in ("y", "yes"):
                print("[*] Đã hủy thao tác theo yêu cầu của bạn.")
                sys.exit(0)
        else:
            print(
                f"[*] Tệp báo cáo cũ đã tồn tại: {target_path.name} -> Tự động làm mới (Clean Refresh)..."
            )

    return target_path


def smart_fold_for_terminal(
    val: Any,
    max_list_items: int = 3,
    max_str_len: int = 120,
    max_vector_dims: int = 4,
) -> Any:
    """Recursively process response payloads for safe, readable terminal rendering."""
    if isinstance(val, (bytes, bytearray)):
        return f"[Binary stream payload: {len(val):,} bytes]"

    if isinstance(val, dict):
        folded_dict = {}
        for k, v in val.items():
            k_lower = k.lower()
            # 1. Truncate long hex / binary strings
            if isinstance(v, str) and ("hash" in k_lower or "sha256" in k_lower or len(v) > 64):
                if re.fullmatch(r"[a-fA-F0-9]{64,}", v):
                    folded_dict[k] = f"{v[:8]}...{v[-8:]} (hash {len(v)} hex)"
                    continue

            # 2. Vector embedding folding
            if (
                isinstance(v, list)
                and len(v) > max_vector_dims
                and all(isinstance(x, (int, float)) for x in v[:5])
            ):
                head = [round(x, 4) if isinstance(x, float) else x for x in v[:3]]
                folded_dict[k] = f"[{', '.join(map(str, head))}, ...] (vector len: {len(v)})"
                continue

            # 3. List of items: keep head and tail if long
            if isinstance(v, list) and len(v) > max_list_items:
                head_items = [
                    smart_fold_for_terminal(x, max_list_items, max_str_len, max_vector_dims)
                    for x in v[:2]
                ]
                tail_item = smart_fold_for_terminal(
                    v[-1], max_list_items, max_str_len, max_vector_dims
                )
                omitted_count = len(v) - 3
                folded_dict[k] = head_items + [
                    f"... [{omitted_count} items omitted] ...",
                    tail_item,
                ]
                continue

            folded_dict[k] = smart_fold_for_terminal(
                v, max_list_items, max_str_len, max_vector_dims
            )
        return folded_dict

    if isinstance(val, list):
        if len(val) > max_list_items:
            head_items = [
                smart_fold_for_terminal(x, max_list_items, max_str_len, max_vector_dims)
                for x in val[:2]
            ]
            tail_item = smart_fold_for_terminal(
                val[-1], max_list_items, max_str_len, max_vector_dims
            )
            omitted_count = len(val) - 3
            return head_items + [f"... [{omitted_count} items omitted] ...", tail_item]
        return [
            smart_fold_for_terminal(x, max_list_items, max_str_len, max_vector_dims) for x in val
        ]

    if isinstance(val, str):
        if len(val) > max_str_len:
            omitted_chars = len(val) - max_str_len
            return f"{val[:max_str_len]}... [{omitted_chars} ký tự tiếp theo]"
        return val

    return val


def format_terminal_box(
    method: str,
    path: str,
    req_headers: dict[str, Any] | None = None,
    form_data: dict[str, Any] | None = None,
    req_body: Any | None = None,
    status_code: int = 200,
    latency_ms: float = 0.0,
    res_headers: dict[str, Any] | None = None,
    res_body: Any | None = None,
    quality_checks: list[tuple[bool, str]] | None = None,
) -> str:
    """Renders a structured, beautiful 3-part Unicode boxed HTTP exchange on the terminal.

    Box 1: [REQUEST INPUT]
    Box 2: [RESPONSE OUTPUT] (with smart payload folding)
    Box 3: [KIỂM CHỨNG CHẤT LƯỢNG NGHIỆP VỤ]
    """
    lines: list[str] = []

    # 1. REQUEST INPUT BOX
    lines.append("┌── [REQUEST INPUT] ──────────────────────────────────────────────────────────")
    lines.append(f"│ METHOD : {method.upper()} {path}")
    if req_headers:
        lines.append("│ HEADERS:")
        for hk, hv in req_headers.items():
            if hk.lower() in (
                "x-user-id",
                "content-type",
                "accept",
                "authorization",
                "idempotency-key",
                "range",
            ):
                lines.append(f"│   {hk:<13}: {hv}")
    if form_data:
        lines.append("│ FORM-DATA:")
        for fk, fv in form_data.items():
            lines.append(f"│   {fk:<13}: {fv}")
    if req_body is not None:
        lines.append("│ BODY:")
        folded_req = smart_fold_for_terminal(req_body)
        body_text = json.dumps(folded_req, indent=2, ensure_ascii=False)
        for bl in body_text.splitlines():
            lines.append(f"│ {bl}")
    lines.append("└─────────────────────────────────────────────────────────────────────────────")

    # 2. RESPONSE OUTPUT BOX
    lines.append(
        f"\n┌── [RESPONSE OUTPUT] (HTTP {status_code} | {latency_ms:.1f} ms) ─────────────────────"
    )
    if res_headers:
        lines.append("│ HEADERS:")
        for rhk, rhv in res_headers.items():
            if rhk.lower() in (
                "content-type",
                "x-request-id",
                "content-length",
                "content-range",
                "accept-ranges",
                "content-disposition",
            ):
                lines.append(f"│   {rhk:<19}: {rhv}")
    if res_body is not None:
        lines.append("│ BODY:")
        folded_res = smart_fold_for_terminal(res_body)
        res_text = json.dumps(folded_res, indent=2, ensure_ascii=False)
        for rl in res_text.splitlines():
            lines.append(f"│ {rl}")
    lines.append("└─────────────────────────────────────────────────────────────────────────────")

    # 3. QUALITY ASSURANCE & VERIFICATION BOX
    if quality_checks:
        lines.append(
            "\n┌── [KIỂM CHỨNG CHẤT LƯỢNG NGHIỆP VỤ] ────────────────────────────────────────"
        )
        for passed, label in quality_checks:
            icon = "✓" if passed else "✗"
            lines.append(f"│ {icon} {label}")
        lines.append(
            "└─────────────────────────────────────────────────────────────────────────────"
        )

    return "\n".join(lines)


def fold_heavy_payload(data: Any, max_vector_dim: int = 4, max_list_items: int = 3) -> Any:
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
                    fold_heavy_payload(v[0], max_vector_dim, max_list_items),
                    f"... {len(v) - 2} items folded (inspect via CLI) ...",
                    fold_heavy_payload(v[-1], max_vector_dim, max_list_items),
                ]
            else:
                folded[k] = fold_heavy_payload(v, max_vector_dim, max_list_items)
        return folded
    elif isinstance(data, list):
        if len(data) > max_list_items:
            return [
                fold_heavy_payload(data[0], max_vector_dim, max_list_items),
                f"... {len(data) - 2} items folded (inspect via CLI) ...",
                fold_heavy_payload(data[-1], max_vector_dim, max_list_items),
            ]
        return [fold_heavy_payload(item, max_vector_dim, max_list_items) for item in data]
    return data


def save_raw_artifact(endpoint_name: str, scenario_tag: str, payload: Any) -> tuple[Path, str]:
    """Saves raw untruncated JSON payload into tests/.artifacts/<endpoint_name>/."""
    endpoint_dir = ARTIFACTS_DIR / endpoint_name
    endpoint_dir.mkdir(parents=True, exist_ok=True)

    artifact_file = endpoint_dir / f"{scenario_tag}.json"
    with open(artifact_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    sha = compute_sha256(payload)
    return artifact_file, sha


def write_markdown_report(report_name: str, content: str) -> Path:
    """Writes standardized evaluation markdown report into temp/output/test/."""
    TEMP_OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    report_path = TEMP_OUTPUT_TEST_DIR / Path(report_name).name

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    return report_path
