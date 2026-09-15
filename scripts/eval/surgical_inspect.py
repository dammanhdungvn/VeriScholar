"""Surgical Inspection CLI tool for API artifacts.

Enables engineers and AI agents to examine specific slices of heavy JSON payloads
without flooding the terminal or overflowing the context window.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.config import ARTIFACTS_DIR, TEMP_OUTPUT_TEST_DIR  # noqa: E402
from scripts.eval.metrics import (  # noqa: E402
    EntitySanityMetric,
    SpatialGeometryMetric,
    TextIntegrityMetric,
)


def list_available_artifacts() -> None:
    """Lists all available raw artifact files and markdown test reports."""
    print("=" * 72)
    print("  DANH MỤC CÁC TỆP ARTIFACT & BÁO CÁO KIỂM THỬ KHẢ DỤNG")
    print("=" * 72)

    # 1. Reports
    print(f"\n[📁] Báo cáo kiểm thử Markdown: {TEMP_OUTPUT_TEST_DIR}")
    reports = sorted(TEMP_OUTPUT_TEST_DIR.glob("*.md")) if TEMP_OUTPUT_TEST_DIR.exists() else []
    if reports:
        for r in reports:
            sz_kb = r.stat().st_size / 1024
            print(f"  ├── {r.name:<45} ({sz_kb:.1f} KB)")
    else:
        print("  └── (Chưa có báo cáo nào. Hãy chạy: uv run python scripts/eval_api.py --api upload)")

    # 2. Raw JSON Artifacts
    print(f"\n[📁] Tệp Artifact Raw JSON: {ARTIFACTS_DIR}")
    endpoints = sorted([d for d in ARTIFACTS_DIR.iterdir() if d.is_dir()]) if ARTIFACTS_DIR.exists() else []
    if endpoints:
        for ep in endpoints:
            files = sorted(ep.glob("*.json"))
            print(f"  ├── [{ep.name}] ({len(files)} tệp)")
            for f in files:
                sz_kb = f.stat().st_size / 1024
                print(f"  │     • {f.name:<40} ({sz_kb:.1f} KB)")
    else:
        print("  └── (Chưa có artifact nào)")

    print("\n" + "=" * 72)
    print("  GỢI Ý LỆNH:")
    print("  • Soi chi tiết payload:  uv run python scripts/eval/surgical_inspect.py -a <tên_file_hoặc_endpoint>")
    print("  • Soi chunk thứ n:       uv run python scripts/eval/surgical_inspect.py -a <tên_file> --chunk 0")
    print("  • Soi lỗi bất thường:    uv run python scripts/eval/surgical_inspect.py -a <tên_file> --errors-only")
    print("=" * 72 + "\n")


def resolve_artifact_path(path_str: str) -> Path:
    """Resolve user-provided artifact path (supports relative, absolute, and artifact-relative)."""
    p = Path(path_str)
    if p.is_file():
        return p
    # Try relative to ARTIFACTS_DIR
    art_path = ARTIFACTS_DIR / path_str
    if art_path.is_file():
        return art_path
    # Search within ARTIFACTS_DIR
    matches = list(ARTIFACTS_DIR.glob(f"**/*{path_str}*"))
    for match in matches:
        if match.is_file() and match.suffix == ".json":
            return match
    raise FileNotFoundError(f"Artifact not found: '{path_str}'")


def inspect_summary(data: Any, filepath: Path) -> None:
    """Print high-level lightweight summary (< 1 KB)."""
    stat = filepath.stat()
    size_kb = stat.st_size / 1024
    print(f"=== Artifact Summary: {filepath.name} ===")
    print(f"Location: {filepath}")
    print(f"File Size: {size_kb:.2f} KB ({stat.st_size:,} bytes)")

    if isinstance(data, dict):
        keys = list(data.keys())
        print(f"Top-level keys ({len(keys)}): {', '.join(keys)}")
        data_payload = data.get("data")
        if isinstance(data_payload, dict):
            inner_keys = list(data_payload.keys())
            print(f"data.* keys ({len(inner_keys)}): {', '.join(inner_keys)}")
            for k in inner_keys:
                v = data_payload[k]
                if isinstance(v, list):
                    print(f"  - data.{k}: list with {len(v)} items")
                elif isinstance(v, dict):
                    print(f"  - data.{k}: object with {len(v)} fields")
                else:
                    val_str = str(v)
                    if len(val_str) > 60:
                        val_str = val_str[:60] + "..."
                    print(f"  - data.{k}: {val_str}")
        elif isinstance(data_payload, list):
            print(f"data: list with {len(data_payload)} items")
    elif isinstance(data, list):
        print(f"Root: list with {len(data)} items")


def inspect_chunk(data: Any, chunk_idx: int) -> None:
    """Extract and print single chunk by index."""
    payload = data.get("data", data) if isinstance(data, dict) else data
    chunks = payload.get("chunks", []) if isinstance(payload, dict) else payload

    if not isinstance(chunks, list):
        print(f"Error: Payload does not contain a list of chunks (type: {type(chunks)})", file=sys.stderr)
        return

    if chunk_idx < 0 or chunk_idx >= len(chunks):
        print(f"Error: Chunk index {chunk_idx} out of range (total chunks: {len(chunks)})", file=sys.stderr)
        return

    target = chunks[chunk_idx]
    print(f"=== Surgical Inspection: Chunk [{chunk_idx}/{len(chunks) - 1}] ===")
    print(json.dumps(target, indent=2, ensure_ascii=False))


def inspect_ref(data: Any, ref_idx: int) -> None:
    """Extract and print single reference by index."""
    payload = data.get("data", data) if isinstance(data, dict) else data
    refs = payload.get("references", []) if isinstance(payload, dict) else payload

    if not isinstance(refs, list):
        print(f"Error: Payload does not contain a list of references (type: {type(refs)})", file=sys.stderr)
        return

    if ref_idx < 0 or ref_idx >= len(refs):
        print(f"Error: Reference index {ref_idx} out of range (total references: {len(refs)})", file=sys.stderr)
        return

    target = refs[ref_idx]
    print(f"=== Surgical Inspection: Reference [{ref_idx}/{len(refs) - 1}] ===")
    print(json.dumps(target, indent=2, ensure_ascii=False))


def inspect_errors_only(data: Any) -> None:
    """Run metrics and output only detected quality anomalies."""
    payload = data.get("data", data) if isinstance(data, dict) else data
    chunks = payload.get("chunks") if isinstance(payload, dict) else None

    print("=== Quality Anomalies & Semantic Diagnostics ===")

    # 1. Text Integrity Check
    text_metric = TextIntegrityMetric()
    text_result = text_metric.measure(chunks or payload)
    if not text_result.passed or text_result.error_samples:
        print(f"\n❌ [TEXT INTEGRITY] Score: {text_result.score:.2f}")
        for err in text_result.error_samples:
            print(f"  - {err.get('error')} at index {err.get('index')}: {err.get('detail')}")
    else:
        print("✅ [TEXT INTEGRITY] Passed (0 anomalies)")

    # 2. Entity Sanity Check
    entity_metric = EntitySanityMetric()
    entity_result = entity_metric.measure(payload)
    if not entity_result.passed or entity_result.error_samples:
        print(f"\n❌ [ENTITY SANITY] Score: {entity_result.score:.2f}")
        for err in entity_result.error_samples:
            print(f"  - {err.get('error')} at index {err.get('index')}: {err.get('detail')}")
    else:
        print("✅ [ENTITY SANITY] Passed (0 anomalies)")

    # 3. Spatial Geometry Check
    spatial_metric = SpatialGeometryMetric()
    spatial_result = spatial_metric.measure(chunks or payload)
    if not spatial_result.passed or spatial_result.error_samples:
        print(f"\n❌ [SPATIAL GEOMETRY] Score: {spatial_result.score:.2f}")
        for err in spatial_result.error_samples:
            print(f"  - {err.get('error')} at index {err.get('index')}: {err.get('detail')}")
    else:
        print("✅ [SPATIAL GEOMETRY] Passed (0 anomalies)")

    print("\n=============================================")


def main():
    parser = argparse.ArgumentParser(
        description="Surgical Inspection CLI for VeriScholar evaluation artifacts."
    )
    parser.add_argument(
        "--artifact",
        "-a",
        nargs="?",
        const="",
        default=None,
        help="Path or partial name of artifact JSON file. If omitted, lists available artifacts.",
    )
    parser.add_argument(
        "--summary",
        "-s",
        action="store_true",
        help="Display high-level summary of payload structure.",
    )
    parser.add_argument(
        "--chunk", "-c", type=int, default=None, help="Inspect single chunk by index."
    )
    parser.add_argument(
        "--ref", "-r", type=int, default=None, help="Inspect single reference by index."
    )
    parser.add_argument(
        "--errors-only", "-e", action="store_true", help="Print only detected quality anomalies."
    )

    args = parser.parse_args()

    # If no artifact specified, list available artifacts cleanly
    if not args.artifact:
        list_available_artifacts()
        return

    try:
        artifact_path = resolve_artifact_path(args.artifact)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nKhả dụng hiện tại:")
        list_available_artifacts()
        sys.exit(1)

    with open(artifact_path, encoding="utf-8") as f:
        data = json.load(f)

    if args.chunk is not None:
        inspect_chunk(data, args.chunk)
    elif args.ref is not None:
        inspect_ref(data, args.ref)
    elif args.errors_only:
        inspect_errors_only(data)
    else:
        inspect_summary(data, artifact_path)


if __name__ == "__main__":
    main()
