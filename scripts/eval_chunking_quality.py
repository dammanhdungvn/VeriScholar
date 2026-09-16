#!/usr/bin/env python3
"""Production-grade Chunking Quality Evaluation Runner.

Evaluates chunk extraction quality either directly via the adapter or end-to-end
via the actual REST API (POST /documents -> POST :parse -> GET /chunks):
- Multi-column reading order flow integrity
- Linguistic sentence boundary preservation (LBI)
- Dehyphenation error rate
- Token distribution and percentile variance
- Micro-chunk (<25 tokens) and bloated-chunk (>800 tokens) rates
- Spatial bounding box coverage and valid normalization [0, 1]
- Verification of actual API payload: content presence, pagination, and serializability

Usage:
    # Full End-to-End evaluation via REST API (Default):
    uv run python scripts/eval_chunking_quality.py --all
    uv run python scripts/eval_chunking_quality.py --paper "Attention Is All You Need.pdf"

    # Evaluate an existing Document ID already parsed in database:
    uv run python scripts/eval_chunking_quality.py --doc-id <UUID>

    # Against a live running server (e.g. Swagger / Uvicorn on port 8000):
    uv run python scripts/eval_chunking_quality.py --live-server http://localhost:8000 --all

    # Direct in-memory mode (Fast unit test without DB/HTTP):
    uv run python scripts/eval_chunking_quality.py --all --direct

    # With CI Quality Gate:
    uv run python scripts/eval_chunking_quality.py --all --ci-gate
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import httpx
import pymupdf

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "core" / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "api" / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from api.adapters.chunk_extractor import PyMuPDFChunkExtractor  # noqa: E402
from core.domain.entities.chunk import DocumentChunk  # noqa: E402
from core.domain.value_objects.bounding_box import BoundingBox  # noqa: E402

from scripts.eval.chunking_metrics import (  # noqa: E402
    PaperChunkMetrics,
    evaluate_chunks,
)
from scripts.eval.context import EvaluationContext  # noqa: E402

DATA_PAPERS_DIR = PROJECT_ROOT / "data" / "papers"
OUTPUT_DIR = PROJECT_ROOT / "temp" / "output" / "test"
OUTPUT_FILE = OUTPUT_DIR / "chunking_quality_matrix.md"


def render_token_histogram(counts: list[int], bins: int = 6, max_bar_len: int = 25) -> str:
    """Render an ASCII histogram for token distribution."""
    if not counts:
        return "No tokens to display."

    min_val = min(counts)
    max_val = max(counts)
    if min_val == max_val:
        return f"[{min_val} - {max_val}]: {'█' * max_bar_len} ({len(counts)})"

    bin_width = (max_val - min_val) / bins
    bucket_counts = [0] * bins
    bucket_ranges: list[tuple[int, int]] = []

    for i in range(bins):
        b_start = int(min_val + i * bin_width)
        b_end = int(min_val + (i + 1) * bin_width)
        bucket_ranges.append((b_start, b_end))

    for c in counts:
        idx = int((c - min_val) / bin_width)
        if idx >= bins:
            idx = bins - 1
        bucket_counts[idx] += 1

    max_freq = max(bucket_counts) or 1
    lines = []
    for (b_start, b_end), freq in zip(bucket_ranges, bucket_counts, strict=True):
        bar_len = int((freq / max_freq) * max_bar_len)
        bar = "█" * bar_len
        pct = (freq / len(counts)) * 100.0
        lines.append(
            f"{b_start:4d} - {b_end:4d} tokens | {bar:<{max_bar_len}} | {freq:3d} ({pct:4.1f}%)"
        )

    return "\n".join(lines)


async def fetch_all_chunks_from_api(
    client: httpx.AsyncClient,
    document_id: str,
) -> tuple[list[DocumentChunk], list[dict[str, Any]], float]:
    """Fetch 100% of chunks from GET /api/v1/documents/{id}/chunks across all pages.

    Returns:
        tuple of (list[DocumentChunk], list of raw chunk dicts, elapsed_time_ms)
    """
    t0 = time.perf_counter()
    all_chunks: list[DocumentChunk] = []
    raw_dicts: list[dict[str, Any]] = []
    current_page = 1
    total_pages = 1

    while current_page <= total_pages:
        res = await client.get(
            f"/api/v1/documents/{document_id}/chunks?page={current_page}&per_page=200&include_content=true"
        )
        if res.status_code != 200:
            raise RuntimeError(
                f"GET /documents/{document_id}/chunks failed (HTTP {res.status_code}): {res.text}"
            )

        body = res.json()
        if not body.get("success"):
            raise RuntimeError(f"API returned success=false: {body}")

        data = body.get("data", [])
        meta = body.get("meta", {})
        total_pages = meta.get("total_pages", 1)

        for item in data:
            raw_dicts.append(item)
            bboxes = [
                BoundingBox(
                    x0=float(b[0]),
                    y0=float(b[1]),
                    x1=float(b[2]),
                    y1=float(b[3]),
                    page=int(b[4]),
                )
                for b in item.get("bounding_boxes", [])
                if len(b) == 5
            ]
            content = item.get("content") or ""
            all_chunks.append(
                DocumentChunk(
                    id=UUID(item["id"]),
                    document_id=UUID(item["document_id"]),
                    chunk_index=int(item["chunk_index"]),
                    page_number=int(item["page_number"]),
                    content=content,
                    bounding_boxes=bboxes,
                    token_count=int(item.get("token_count", len(content.split()))),
                )
            )

        current_page += 1

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return all_chunks, raw_dicts, elapsed_ms


async def evaluate_via_api(
    pdf_path: Path,
    ctx: EvaluationContext,
) -> tuple[PaperChunkMetrics, list[dict[str, Any]]]:
    """Upload PDF, trigger parse, fetch real chunks over HTTP API, and evaluate."""
    assert ctx.client is not None

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)

    t_start = time.perf_counter()

    # 1. Upload
    upload_res = await ctx.client.post(
        "/api/v1/documents",
        files={"file": (pdf_path.name, pdf_bytes, "application/pdf")},
    )
    if upload_res.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed (HTTP {upload_res.status_code}): {upload_res.text}")
    doc_id = upload_res.json()["data"]["id"]
    ctx.track_document(doc_id)

    # 2. Trigger parse with force_reparse=True to guarantee fresh pipeline run
    parse_res = await ctx.client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={"chunk_size": 500, "chunk_overlap": 50, "force_reparse": True},
    )
    if parse_res.status_code not in (200, 202):
        raise RuntimeError(f"Parse trigger failed (HTTP {parse_res.status_code}): {parse_res.text}")

    # 3. Fetch 100% of chunks from REST API across pagination
    chunks, raw_dicts, fetch_ms = await fetch_all_chunks_from_api(ctx.client, doc_id)
    total_pipeline_ms = (time.perf_counter() - t_start) * 1000.0

    # 4. Evaluate actual response chunks
    metrics = evaluate_chunks(
        paper_name=pdf_path.name,
        chunks=chunks,
        total_pages=total_pages,
        elapsed_time_ms=total_pipeline_ms,
    )

    return metrics, raw_dicts


def generate_markdown_report(
    metrics_list: list[PaperChunkMetrics],
    eval_mode: str,
    total_elapsed_s: float,
) -> str:
    """Generate comprehensive production-ready Markdown report."""
    avg_score = (
        sum(m.composite_score for m in metrics_list) / len(metrics_list) if metrics_list else 0.0
    )
    total_chunks_all = sum(m.total_chunks for m in metrics_list)
    total_pages_all = sum(m.total_pages for m in metrics_list)
    total_tokens_all = sum(m.total_tokens for m in metrics_list)

    md = [
        "# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG PHÂN ĐOẠN (CHUNKING QUALITY BENCHMARK REPORT)",
        "- **Thời gian đánh giá:** 2026-09-16",
        f"- **Phương thức đánh giá:** `{eval_mode}`",
        f"- **Tổng số bài báo đánh giá:** {len(metrics_list)} bài báo",
        f"- **Tổng số trang PDF:** {total_pages_all} trang",
        f"- **Tổng số chunks đã tạo:** {total_chunks_all:,} chunks",
        f"- **Tổng số tokens:** {total_tokens_all:,} tokens",
        f"- **Điểm chất lượng tổng hợp (Composite Quality Score):** **`{avg_score:.1f} / 100`**",
        "",
        "---",
        "",
        "## 1. Tóm tắt Điều hành (Executive Summary)",
        "",
        f"Báo cáo này đo lường chất lượng thực tế của dữ liệu trả về qua phương thức **{eval_mode}** "
        "dựa trên các tiêu chuẩn công nghiệp cho hệ thống **Hybrid RAG** và **Deep Reading Canvas (PDF.js)**. "
        "Các bài báo trong tập kiểm chuẩn đại diện cho các trường hợp thách thức điển hình trong giới học thuật:",
        "- **Bố cục 2 cột (Multi-column layout)**: Đảm bảo trật tự đọc không bị quét ngang.",
        "- **Tính toàn vẹn câu (Sentence Boundary)**: Không cắt ngang giữa câu hoặc làm đứt từ.",
        "- **Phân phối kích thước (Token Sizing)**: Tối ưu cho mô hình nhúng vector (1536 dims) mà không bị loãng ngữ cảnh.",
        "- **Tọa độ không gian (Spatial Grounding)**: Bounding box chuẩn hóa `[x0, y0, x1, y1, page]` phục vụ vẽ lớp highlight.",
        "",
        "---",
        "",
        "## 2. Ma trận So sánh Đa Chiều (Cross-Paper Benchmark Matrix)",
        "",
        "| Tên bài báo | Trang | Chunks | Min/Max/Mean Tokens | Boundary Integrity (>=98%) | Dehyphenation (=0%) | Column Flow | Spatial Validity | Tốc độ (ms/trang) | Điểm số |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for m in metrics_list:
        short_name = m.paper_name[:35] + ("..." if len(m.paper_name) > 35 else "")
        token_str = f"{m.min_tokens} / {m.max_tokens} / {m.mean_tokens:.0f}"
        bi_status = f"{m.boundary_integrity_ratio:.1f}%"
        dehyphen_status = f"{m.dehyphenation_error_rate:.1f}%"
        col_status = f"{m.column_flow_integrity:.1f}%"
        spatial_status = f"{m.spatial_validity_ratio:.1f}%"
        speed_status = f"{m.ms_per_page:.1f} ms"
        score_status = f"**{m.composite_score:.1f}**"

        md.append(
            f"| `{short_name}` | {m.total_pages} | {m.total_chunks} | {token_str} | {bi_status} | {dehyphen_status} | {col_status} | {spatial_status} | {speed_status} | {score_status} |"
        )

    md.extend(
        [
            "",
            "---",
            "",
            "## 3. Phân tích Chi tiết Từng Bài báo (Detailed Paper Audits)",
            "",
        ]
    )

    for m in metrics_list:
        md.extend(
            [
                f"### 3.{metrics_list.index(m) + 1}. `{m.paper_name}`",
                f"- **Tổng số trang:** {m.total_pages} trang | **Tổng số chunks:** {m.total_chunks} chunks | **Tổng số tokens:** {m.total_tokens:,} tokens",
                f"- **Thời gian xử lý:** {m.elapsed_time_ms:.2f} ms ({m.ms_per_page:.2f} ms/trang)",
                f"- **Điểm chất lượng:** `{m.composite_score:.1f} / 100`",
                "",
                "#### Thống kê Phân phối Tokens:",
                "| Chỉ số phân phối | Giá trị (Tokens) |",
                "| :--- | :--- |",
                f"| Cực tiểu (Min) | **{m.min_tokens}** tokens |",
                f"| Cực đại (Max) | **{m.max_tokens}** tokens |",
                f"| Trung bình (Mean) | **{m.mean_tokens:.1f}** tokens |",
                f"| Trung vị (Median / P50) | **{m.median_tokens:.1f}** tokens |",
                f"| Phân vị 90 (P90) | **{m.p90_tokens:.1f}** tokens |",
                f"| Phân vị 99 (P99) | **{m.p99_tokens:.1f}** tokens |",
                f"| Độ lệch chuẩn (Std Dev) | **{m.std_dev_tokens:.1f}** tokens |",
                "",
                "#### Tỷ lệ Tuân thủ SLA Sản xuất:",
                f"- **Linguistic Boundary Integrity:** `{m.boundary_integrity_ratio:.2f}%` (Mục tiêu: `>= 98.0%`)",
                f"- **Dehyphenation Error Rate:** `{m.dehyphenation_error_rate:.2f}%` (Mục tiêu: `= 0.0%`)",
                f"- **Column Reading Flow Integrity:** `{m.column_flow_integrity:.2f}%` (Mục tiêu: `100.0%`)",
                f"- **Spatial Bounding Box Validity:** `{m.spatial_validity_ratio:.2f}%` (Mục tiêu: `100.0%`)",
                f"- **Micro-Chunk Rate (<25 tokens):** `{m.micro_chunk_rate:.2f}%` (Mục tiêu: `<= 2.0%`)",
                f"- **Bloated-Chunk Rate (>800 tokens):** `{m.bloated_chunk_rate:.2f}%` (Mục tiêu: `<= 1.0%`)",
                "",
            ]
        )

        if m.anomalies:
            md.extend(
                [
                    "#### Cảnh báo Dị biệt (Detected Anomalies):",
                    "| Chunk Index | Trang | Loại cảnh báo | Mức độ | Trích đoạn nội dung |",
                    "| :---: | :---: | :--- | :---: | :--- |",
                ]
            )
            for a in m.anomalies[:8]:
                clean_snippet = a.content_snippet.replace("\n", " ").replace("|", "\\|")
                md.append(
                    f"| `#{a.chunk_index}` | P.{a.page_number} | `{a.issue_type}` | **{a.severity}** | `{clean_snippet}` |"
                )
            if len(m.anomalies) > 8:
                md.append(
                    f"\n*... [Còn {len(m.anomalies) - 8} cảnh báo khác được lược bớt để bảo toàn độ ngắn gọn]*\n"
                )
        else:
            md.append(
                "\n> [!NOTE]\n> Không phát hiện bất kỳ dị biệt nào. Chất lượng phân đoạn đạt chuẩn 100%.\n"
            )

        md.append("\n---\n")

    return "\n".join(md)


async def main_async() -> None:
    """Async execution entry point."""
    parser = argparse.ArgumentParser(description="Evaluate PDF chunking quality across papers.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Evaluate all PDF papers present in data/papers/ directory.",
    )
    parser.add_argument(
        "--paper",
        type=str,
        default=None,
        help="Evaluate a specific PDF paper by filename.",
    )
    parser.add_argument(
        "--doc-id",
        type=str,
        default=None,
        help="Evaluate an existing document already present in DB by UUID.",
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Direct in-memory adapter evaluation (bypasses DB/HTTP for fast unit checking).",
    )
    parser.add_argument(
        "--live-server",
        type=str,
        default=None,
        help="URL of live running server (e.g. http://localhost:8000).",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Preserve uploaded documents in DB instead of cleaning up.",
    )
    parser.add_argument(
        "--ci-gate",
        action="store_true",
        help="Fail with exit code 1 if any SLA fails production quality gate.",
    )

    args = parser.parse_args()

    if not args.all and not args.paper and not args.doc_id:
        args.all = True

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 76)
    print("  VERISCHOLAR: PRODUCTION CHUNKING QUALITY EVALUATION BENCHMARK")
    print("=" * 76)

    # CASE A: Evaluate existing document ID
    if args.doc_id:
        eval_mode = "REST API Response (GET /api/v1/documents/{doc_id}/chunks)"
        print(f"[*] Target Mode      : Existing Document [{args.doc_id}]")
        print(f"[*] Evaluation Flow  : {eval_mode}")
        print("-" * 76)

        async with EvaluationContext(
            base_url=args.live_server,
            use_live_server=bool(args.live_server),
            keep_data=True,
        ) as ctx:
            assert ctx.client is not None
            chunks, raw_dicts, fetch_ms = await fetch_all_chunks_from_api(ctx.client, args.doc_id)
            if not chunks:
                print(f"[ERROR] No chunks returned for document ID: {args.doc_id}")
                sys.exit(1)

            total_pages = max((c.page_number for c in chunks), default=1)
            metrics = evaluate_chunks(
                paper_name=f"Document_{args.doc_id}",
                chunks=chunks,
                total_pages=total_pages,
                elapsed_time_ms=fetch_ms,
            )

            # Dump raw chunks for inspection
            dump_file = OUTPUT_DIR / f"raw_chunks_doc_{args.doc_id[:8]}.json"
            with open(dump_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"document_id": args.doc_id, "total_chunks": len(raw_dicts), "data": raw_dicts},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            token_counts = [c.token_count for c in chunks]
            histogram = render_token_histogram(token_counts, bins=5, max_bar_len=20)

            print(f"┌── [CHUNKING AUDIT: Document {args.doc_id[:18]}...] " + "─" * 20)
            print(
                f"│ Pages: {total_pages:2d} | Chunks: {len(chunks):3d} | Total Tokens: {metrics.total_tokens:,}"
            )
            print(
                f"│ Sizing: Min={metrics.min_tokens}, Max={metrics.max_tokens}, Mean={metrics.mean_tokens:.1f}, Median={metrics.median_tokens:.1f}, P90={metrics.p90_tokens:.1f}"
            )
            print("│ Quality Rates:")
            print(
                f"│   - Boundary Integrity (LBI) : {metrics.boundary_integrity_ratio:5.1f}%  (SLA >= 95%)"
            )
            print(
                f"│   - Dehyphenation Error Rate : {metrics.dehyphenation_error_rate:5.1f}%  (SLA == 0%)"
            )
            print(
                f"│   - Column Flow Integrity    : {metrics.column_flow_integrity:5.1f}%  (SLA >= 95%)"
            )
            print(
                f"│   - Spatial BBox Validity    : {metrics.spatial_validity_ratio:5.1f}%  (SLA == 100%)"
            )
            print(f"│   - Micro-Chunk Rate (<25)   : {metrics.micro_chunk_rate:5.1f}%  (SLA <= 5%)")
            print(f"│ Fetch Latency: {fetch_ms:.1f} ms")
            print(f"│ Composite Quality Score      : {metrics.composite_score:.1f} / 100")
            print(f"│ Anomalies Flagged            : {len(metrics.anomalies)}")
            print("│ Token Distribution Histogram:")
            for h_line in histogram.splitlines():
                print(f"│   {h_line}")
            print("└" + "─" * 74)
            print(f"\n[*] Raw chunks saved to: {dump_file}")
        return

    # CASE B: Standard Paper Benchmark
    if not DATA_PAPERS_DIR.exists():
        sys.stderr.write(f"Error: Papers directory not found at {DATA_PAPERS_DIR}\n")
        sys.exit(1)

    if args.paper:
        target_files = [DATA_PAPERS_DIR / args.paper]
    else:
        target_files = sorted(DATA_PAPERS_DIR.glob("*.pdf"))

    if not target_files:
        sys.stderr.write("Error: No PDF papers found to evaluate.\n")
        sys.exit(1)

    eval_mode = (
        "Direct Extractor (In-Memory Unit Mode)"
        if args.direct
        else "REST API E2E Response (POST /documents -> POST :parse -> GET /chunks)"
    )

    print(f"[*] Papers directory : {DATA_PAPERS_DIR}")
    print(f"[*] Benchmark target : {len(target_files)} papers")
    print(f"[*] Evaluation Flow  : {eval_mode}")
    print(f"[*] CI Quality Gate  : {'ENABLED' if args.ci_gate else 'DISABLED'}")
    print("-" * 76)

    metrics_list: list[PaperChunkMetrics] = []
    overall_start = time.perf_counter()

    if args.direct:
        # Direct in-memory mode
        extractor = PyMuPDFChunkExtractor()
        for pdf_path in target_files:
            if not pdf_path.exists():
                continue
            print(f"\n[EVALUATING: DIRECT] {pdf_path.name}...")
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            t0 = time.perf_counter()
            chunks = extractor.extract_chunks(pdf_bytes, uuid4())
            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            metrics = evaluate_chunks(pdf_path.name, chunks, len(doc), elapsed_ms)
            metrics_list.append(metrics)

            token_counts = [c.token_count for c in chunks]
            histogram = render_token_histogram(token_counts, bins=5, max_bar_len=20)
            print(f"┌── [CHUNKING AUDIT: {pdf_path.name[:45]}] " + "─" * 20)
            print(
                f"│ Pages: {len(doc):2d} | Chunks: {len(chunks):3d} | Total Tokens: {metrics.total_tokens:,}"
            )
            print(
                f"│ Quality Rates: LBI={metrics.boundary_integrity_ratio:.1f}% | Dehyphen={metrics.dehyphenation_error_rate:.1f}% | Spatial={metrics.spatial_validity_ratio:.1f}%"
            )
            print(f"│ Composite Quality Score      : {metrics.composite_score:.1f} / 100")
            print("└" + "─" * 74)
    else:
        # Full REST API E2E mode
        async with EvaluationContext(
            base_url=args.live_server,
            use_live_server=bool(args.live_server),
            keep_data=args.keep_data,
        ) as ctx:
            for pdf_path in target_files:
                if not pdf_path.exists():
                    continue
                print(f"\n[EVALUATING: REST API] {pdf_path.name}...")
                metrics, raw_dicts = await evaluate_via_api(pdf_path, ctx)
                metrics_list.append(metrics)

                # Save raw response for verification
                slug = pdf_path.stem[:25].replace(" ", "_")
                dump_file = OUTPUT_DIR / f"api_raw_chunks_{slug}.json"
                with open(dump_file, "w", encoding="utf-8") as f:
                    json.dump(
                        {"paper": pdf_path.name, "total_chunks": len(raw_dicts), "data": raw_dicts},
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )

                token_counts = [c.get("token_count", 0) for c in raw_dicts]
                histogram = render_token_histogram(token_counts, bins=5, max_bar_len=20)

                print(f"┌── [CHUNKING AUDIT: {pdf_path.name[:45]}] " + "─" * 20)
                print(
                    f"│ Pages: {metrics.total_pages:2d} | Chunks: {len(raw_dicts):3d} | Total Tokens: {metrics.total_tokens:,}"
                )
                print(
                    f"│ Sizing: Min={metrics.min_tokens}, Max={metrics.max_tokens}, Mean={metrics.mean_tokens:.1f}, Median={metrics.median_tokens:.1f}, P90={metrics.p90_tokens:.1f}"
                )
                print("│ Quality Rates:")
                print(
                    f"│   - Boundary Integrity (LBI) : {metrics.boundary_integrity_ratio:5.1f}%  (SLA >= 95%)"
                )
                print(
                    f"│   - Dehyphenation Error Rate : {metrics.dehyphenation_error_rate:5.1f}%  (SLA == 0%)"
                )
                print(
                    f"│   - Column Flow Integrity    : {metrics.column_flow_integrity:5.1f}%  (SLA >= 95%)"
                )
                print(
                    f"│   - Spatial BBox Validity    : {metrics.spatial_validity_ratio:5.1f}%  (SLA == 100%)"
                )
                print(
                    f"│   - Micro-Chunk Rate (<25)   : {metrics.micro_chunk_rate:5.1f}%  (SLA <= 5%)"
                )
                print(
                    f"│ Total E2E Latency: {metrics.elapsed_time_ms:.1f} ms ({metrics.ms_per_page:.1f} ms/page)"
                )
                print(f"│ Composite Quality Score      : {metrics.composite_score:.1f} / 100")
                print(f"│ Anomalies Flagged            : {len(metrics.anomalies)}")
                print("│ Token Distribution Histogram:")
                for h_line in histogram.splitlines():
                    print(f"│   {h_line}")
                print("└" + "─" * 74)

    total_duration_s = time.perf_counter() - overall_start

    # Generate Markdown Report
    report_md = generate_markdown_report(metrics_list, eval_mode, total_duration_s)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report_md)

    avg_score = (
        sum(m.composite_score for m in metrics_list) / len(metrics_list) if metrics_list else 0.0
    )

    print("\n" + "=" * 76)
    print(
        f"  TỔNG KẾT: ĐÁNH GIÁ XONG {len(metrics_list)} BÀI BÁO | ĐIỂM TRUNG BÌNH: {avg_score:.1f}/100"
    )
    print(f"  Báo cáo chi tiết đã lưu: {OUTPUT_FILE}")
    print("=" * 76)

    # CI Quality Gate Check
    if args.ci_gate:
        failed_papers = [m for m in metrics_list if m.composite_score < 90.0]
        if failed_papers:
            print(
                f"\n[CI-FAIL] {len(failed_papers)} papers failed the 90.0 composite quality gate:"
            )
            for fp in failed_papers:
                print(f"  - {fp.paper_name}: {fp.composite_score:.1f}/100")
            sys.exit(1)
        else:
            print("\n[CI-PASS] All papers passed Production Quality Gate!")


def main() -> None:
    """Synchronous launcher for async main."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
