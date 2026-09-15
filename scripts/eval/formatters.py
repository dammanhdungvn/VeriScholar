"""Canonical formatting and report writing utilities for API Evaluation Harness."""

import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.eval.config import ARTIFACTS_DIR, REPORTS_DIR


def sanitize_canonical(obj: Any) -> Any:
    """Recursively sanitize Python data structures for canonical output:

    1. Rounds float values to 4 decimal places.
    2. Sorts dictionary keys.
    3. Preserves ordered lists.
    """
    if isinstance(obj, float):
        return round(obj, 4)
    if isinstance(obj, dict):
        return {k: sanitize_canonical(v) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        return [sanitize_canonical(item) for item in obj]
    return obj


def calculate_file_sha256(filepath: Path) -> str:
    """Compute cryptographic SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def save_raw_artifact(api_name: str, identifier: str, data: Any) -> tuple[Path, str]:
    """Save full raw JSON payload to tests/.artifacts/<api_name>/<identifier>.json.

    Returns:
        tuple[Path, str]: Tuple of (saved_file_path, sha256_checksum).
    """
    target_dir = ARTIFACTS_DIR / api_name
    target_dir.mkdir(parents=True, exist_ok=True)
    clean_id = identifier.replace("/", "_").replace(":", "_")
    target_file = target_dir / f"{clean_id}.json"
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(sanitize_canonical(data), f, indent=2, ensure_ascii=False)
    sha256 = calculate_file_sha256(target_file)
    return target_file, sha256


def write_markdown_report(report_filename: str, markdown_content: str) -> Path:
    """Write markdown evaluation report to docs/eval-reports/<report_filename>."""
    target_file = REPORTS_DIR / report_filename
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    return target_file
