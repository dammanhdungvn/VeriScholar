"""Concurrency Stress Testing and Resource Benchmarking Suite (Module UAT).

Simulates concurrent user sessions on VeriScholar UAT environment (VPS 2 vCPUs, 8GB RAM):
- Stage 1: 5 concurrent sessions
- Stage 2: 10 concurrent sessions

Each session executes:
1. GET /health/ready (Readiness probe)
2. POST /api/v1/sessions/{id}/messages (Research session chat with SSE streaming)
3. POST /api/v1/drafts/{id}/verify-facts (SAFE fact verification)

Tracks:
- System Peak RAM (MB) & Uvicorn Peak RSS (MB)
- CPU Load (%)
- Success Rate (%)
- Latencies: Min, Mean, p50, p95, Max
- Audit log verification (storage/logs/api-audit.log)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUDIT_LOG = PROJECT_ROOT / "storage" / "logs" / "api-audit.log"
RAM_LIMIT_MB = 6656.0  # 6.5 GB out of 8 GB max ceiling


@dataclass
class RequestMetric:
    """Latency and status record for a single HTTP call."""

    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    success: bool
    error_message: str | None = None


@dataclass
class StageResult:
    """Aggregated benchmark metrics for a concurrency stage."""

    concurrency: int
    duration_seconds: float
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    success_rate_pct: float = 0.0
    baseline_ram_mb: float = 0.0
    peak_ram_mb: float = 0.0
    ram_delta_mb: float = 0.0
    peak_uvicorn_rss_mb: float = 0.0
    avg_cpu_pct: float = 0.0
    peak_cpu_pct: float = 0.0
    audit_logs_recorded: int = 0
    endpoint_metrics: dict[str, list[float]] = field(default_factory=dict)
    endpoint_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def get_system_ram_mb() -> tuple[float, float, float]:
    """Read /proc/meminfo to get (Total_MB, Available_MB, Used_MB)."""
    mem_total_kb = 0.0
    mem_avail_kb = 0.0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_total_kb = float(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_avail_kb = float(line.split()[1])
                if mem_total_kb > 0 and mem_avail_kb > 0:
                    break
        total_mb = mem_total_kb / 1024.0
        avail_mb = mem_avail_kb / 1024.0
        used_mb = total_mb - avail_mb
        return total_mb, avail_mb, used_mb
    except Exception:
        return 8192.0, 4096.0, 4096.0


def get_uvicorn_pids() -> list[int]:
    """Find process IDs for running uvicorn instances."""
    pids: list[int] = []
    try:
        out = subprocess.check_output(["pgrep", "-f", "uvicorn api:app"], text=True)
        for line in out.strip().splitlines():
            pid = int(line.strip())
            if pid != os.getpid():
                pids.append(pid)
    except Exception:
        pass
    return pids


def get_uvicorn_rss_mb(pids: list[int]) -> float:
    """Read VmRSS from /proc/{pid}/status for uvicorn processes."""
    total_rss_kb = 0.0
    for pid in pids:
        try:
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        total_rss_kb += float(line.split()[1])
                        break
        except Exception:
            continue
    return total_rss_kb / 1024.0


def read_cpu_jiffies() -> tuple[float, float]:
    """Read CPU (idle_jiffies, total_jiffies) from /proc/stat."""
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()[1:]
            vals = [float(x) for x in parts]
            idle = vals[3] + vals[4]
            total = sum(vals)
            return idle, total
    except Exception:
        return 0.0, 1.0


class SystemResourceSampler:
    """Background sampling loop for CPU and RAM consumption."""

    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self.ram_samples: list[float] = []
        self.uvicorn_rss_samples: list[float] = []
        self.cpu_samples: list[float] = []
        self.uvicorn_pids = get_uvicorn_pids()

    async def _sample_loop(self) -> None:
        prev_idle, prev_total = read_cpu_jiffies()
        while self._running:
            await asyncio.sleep(self.sample_interval)
            _, _, used_mb = get_system_ram_mb()
            self.ram_samples.append(used_mb)

            rss_mb = get_uvicorn_rss_mb(self.uvicorn_pids)
            self.uvicorn_rss_samples.append(rss_mb)

            curr_idle, curr_total = read_cpu_jiffies()
            delta_total = curr_total - prev_total
            delta_idle = curr_idle - prev_idle
            if delta_total > 0:
                cpu_pct = max(0.0, min(100.0, (1.0 - delta_idle / delta_total) * 100.0))
                self.cpu_samples.append(cpu_pct)
            prev_idle, prev_total = curr_idle, curr_total

    def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._sample_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


def calc_percentile(data: list[float], p: float) -> float:
    """Calculate p-th percentile (0-100) using linear interpolation."""
    if not data:
        return 0.0
    sorted_d = sorted(data)
    idx = (len(sorted_d) - 1) * (p / 100.0)
    floor_idx = int(idx)
    ceil_idx = min(floor_idx + 1, len(sorted_d) - 1)
    weight = idx - floor_idx
    val = sorted_d[floor_idx] * (1.0 - weight) + sorted_d[ceil_idx] * weight
    return round(val, 2)


async def execute_user_session(
    session_id_idx: int,
    base_url: str,
    timeout_seconds: float = 45.0,
) -> list[RequestMetric]:
    """Simulate complete researcher session lifecycle."""
    metrics: list[RequestMetric] = []
    unique_suffix = f"{int(time.time())}_{session_id_idx}_{uuid.uuid4().hex[:6]}"
    email = f"stress_user_{unique_suffix}@verischolar.test"
    password = f"P@ssword_{unique_suffix}"
    full_name = f"Stress User {session_id_idx}"

    timeout = httpx.Timeout(timeout_seconds, connect=10.0)
    async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
        # 0. User Registration / Authentication
        auth_headers: dict[str, str] = {}
        try:
            t0 = time.perf_counter()
            resp = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "full_name": full_name,
                    "institution": "VeriScholar Benchmark Lab",
                },
            )
            lat = (time.perf_counter() - t0) * 1000
            if resp.status_code == 201:
                token = resp.json()["data"]["tokens"]["access_token"]
                auth_headers = {"Authorization": f"Bearer {token}"}
                metrics.append(RequestMetric("/api/v1/auth/register", "POST", 201, lat, True))
            else:
                metrics.append(
                    RequestMetric(
                        "/api/v1/auth/register", "POST", resp.status_code, lat, False, resp.text
                    )
                )
                return metrics
        except Exception as exc:
            metrics.append(
                RequestMetric(
                    "/api/v1/auth/register",
                    "POST",
                    0,
                    0.0,
                    False,
                    f"Register Exception: {type(exc).__name__}: {exc}",
                )
            )
            return metrics

        # 1. Health Probe (/health/ready)
        try:
            t0 = time.perf_counter()
            resp = await client.get("/health/ready")
            lat = (time.perf_counter() - t0) * 1000
            is_ok = resp.status_code == 200 and resp.json().get("status") == "ready"
            metrics.append(
                RequestMetric(
                    "/health/ready",
                    "GET",
                    resp.status_code,
                    lat,
                    is_ok,
                    None if is_ok else resp.text,
                )
            )
        except Exception as exc:
            metrics.append(
                RequestMetric(
                    "/health/ready", "GET", 0, 0.0, False, f"Health error: {type(exc).__name__}"
                )
            )

        # 2. Research Session Creation & Chat SSE Stream
        research_session_id: str | None = None
        try:
            t0 = time.perf_counter()
            resp = await client.post(
                "/api/v1/sessions",
                headers=auth_headers,
                json={"title": f"Benchmarking Session {session_id_idx}"},
            )
            lat = (time.perf_counter() - t0) * 1000
            if resp.status_code in (200, 201):
                research_session_id = resp.json()["data"]["id"]
                metrics.append(
                    RequestMetric("/api/v1/sessions", "POST", resp.status_code, lat, True)
                )
            else:
                metrics.append(
                    RequestMetric(
                        "/api/v1/sessions", "POST", resp.status_code, lat, False, resp.text
                    )
                )
        except Exception as exc:
            metrics.append(
                RequestMetric(
                    "/api/v1/sessions",
                    "POST",
                    0,
                    0.0,
                    False,
                    f"Session error: {type(exc).__name__}",
                )
            )

        if research_session_id:
            try:
                t0 = time.perf_counter()
                chunks_received = 0
                async with client.stream(
                    "POST",
                    f"/api/v1/sessions/{research_session_id}/messages",
                    headers=auth_headers,
                    json={
                        "question": "Summarize the architectural trade-offs of self-attention mechanisms.",
                        "stream": True,
                        "scope": "multi_paper",
                    },
                ) as stream_resp:
                    status_c = stream_resp.status_code
                    if status_c == 200:
                        async for _chunk in stream_resp.aiter_text():
                            chunks_received += 1
                        lat = (time.perf_counter() - t0) * 1000
                        metrics.append(
                            RequestMetric(
                                "/api/v1/sessions/{id}/messages",
                                "POST[SSE]",
                                200,
                                lat,
                                True,
                            )
                        )
                    else:
                        lat = (time.perf_counter() - t0) * 1000
                        metrics.append(
                            RequestMetric(
                                "/api/v1/sessions/{id}/messages",
                                "POST[SSE]",
                                status_c,
                                lat,
                                False,
                                f"Stream failed with status {status_c}",
                            )
                        )
            except Exception as exc:
                metrics.append(
                    RequestMetric(
                        "/api/v1/sessions/{id}/messages",
                        "POST[SSE]",
                        0,
                        0.0,
                        False,
                        f"Chat error: {type(exc).__name__}: {exc}",
                    )
                )

        # 3. Draft Creation & SAFE Fact Verification (/verify-facts)
        draft_id: str | None = None
        try:
            t0 = time.perf_counter()
            resp = await client.post(
                "/api/v1/drafts",
                headers=auth_headers,
                json={
                    "title": f"Benchmarking Draft {session_id_idx}",
                    "content": (
                        "\\section{Introduction}\n"
                        "Transformers rely on multi-head attention to model sequences without recurrence. "
                        "Recent studies show low-rank adaptation reduces fine-tuning parameters substantially."
                    ),
                    "format": "latex",
                },
            )
            lat = (time.perf_counter() - t0) * 1000
            if resp.status_code in (200, 201):
                draft_id = resp.json()["data"]["id"]
                metrics.append(RequestMetric("/api/v1/drafts", "POST", resp.status_code, lat, True))
            else:
                metrics.append(
                    RequestMetric("/api/v1/drafts", "POST", resp.status_code, lat, False, resp.text)
                )
        except Exception as exc:
            metrics.append(
                RequestMetric(
                    "/api/v1/drafts", "POST", 0, 0.0, False, f"Draft error: {type(exc).__name__}"
                )
            )

        if draft_id:
            try:
                t0 = time.perf_counter()
                resp = await client.post(
                    f"/api/v1/drafts/{draft_id}/verify-facts",
                    headers=auth_headers,
                    json={},
                )
                lat = (time.perf_counter() - t0) * 1000
                is_ok = resp.status_code == 200
                metrics.append(
                    RequestMetric(
                        "/api/v1/drafts/{id}/verify-facts",
                        "POST",
                        resp.status_code,
                        lat,
                        is_ok,
                        None if is_ok else resp.text,
                    )
                )
            except Exception as exc:
                metrics.append(
                    RequestMetric(
                        "/api/v1/drafts/{id}/verify-facts",
                        "POST",
                        0,
                        0.0,
                        False,
                        f"Verify-facts error: {type(exc).__name__}: {exc}",
                    )
                )

    return metrics


def count_audit_logs(audit_log_path: Path) -> int:
    """Count number of lines in api-audit.log."""
    if not audit_log_path.exists():
        return 0
    try:
        count = 0
        with open(audit_log_path, encoding="utf-8", errors="ignore") as f:
            for _ in f:
                count += 1
        return count
    except Exception:
        return 0


async def run_stage(
    concurrency: int,
    base_url: str,
    audit_log_path: Path,
) -> StageResult:
    """Execute a single concurrency test stage with live monitoring."""
    total_mem_mb, _, baseline_ram = get_system_ram_mb()
    audit_start_count = count_audit_logs(audit_log_path)

    sampler = SystemResourceSampler(sample_interval=0.1)
    sampler.start()

    t_start = time.perf_counter()
    tasks = [
        execute_user_session(idx, base_url, timeout_seconds=60.0)
        for idx in range(1, concurrency + 1)
    ]
    all_session_metrics = await asyncio.gather(*tasks, return_exceptions=True)
    t_end = time.perf_counter()

    await sampler.stop()
    audit_end_count = count_audit_logs(audit_log_path)

    stage = StageResult(
        concurrency=concurrency,
        duration_seconds=round(t_end - t_start, 2),
        baseline_ram_mb=round(baseline_ram, 1),
        audit_logs_recorded=max(0, audit_end_count - audit_start_count),
    )

    if sampler.ram_samples:
        stage.peak_ram_mb = round(max(sampler.ram_samples), 1)
        stage.ram_delta_mb = round(stage.peak_ram_mb - stage.baseline_ram_mb, 1)
    else:
        stage.peak_ram_mb = stage.baseline_ram_mb

    if sampler.uvicorn_rss_samples:
        stage.peak_uvicorn_rss_mb = round(max(sampler.uvicorn_rss_samples), 1)

    if sampler.cpu_samples:
        stage.avg_cpu_pct = round(sum(sampler.cpu_samples) / len(sampler.cpu_samples), 1)
        stage.peak_cpu_pct = round(max(sampler.cpu_samples), 1)

    for res in all_session_metrics:
        if isinstance(res, Exception):
            stage.failed_requests += 1
            stage.total_requests += 1
            stage.errors.append(f"Task exception: {type(res).__name__}: {res}")
            continue

        for m in res:
            stage.total_requests += 1
            if m.success:
                stage.successful_requests += 1
            else:
                stage.failed_requests += 1
                if m.error_message:
                    stage.errors.append(f"[{m.endpoint}] {m.error_message}")

            if m.endpoint not in stage.endpoint_metrics:
                stage.endpoint_metrics[m.endpoint] = []
                stage.endpoint_counts[m.endpoint] = {"success": 0, "failed": 0}

            stage.endpoint_metrics[m.endpoint].append(m.latency_ms)
            if m.success:
                stage.endpoint_counts[m.endpoint]["success"] += 1
            else:
                stage.endpoint_counts[m.endpoint]["failed"] += 1

    if stage.total_requests > 0:
        stage.success_rate_pct = round(
            (stage.successful_requests / stage.total_requests) * 100.0, 2
        )
    else:
        stage.success_rate_pct = 0.0

    return stage


def format_markdown_report(
    stages: list[StageResult],
    total_mem_mb: float,
    audit_log_path: Path,
) -> str:
    """Format benchmark results into clean GitHub-flavored markdown report."""
    lines: list[str] = []
    lines.append("# BÁO CÁO ĐO LƯỜNG TẢI ĐỒNG THỜI & TÀI NGUYÊN (STRESS TEST REPORT)")
    lines.append(f"**Môi trường:** UAT (VPS 2 vCPUs, {total_mem_mb / 1024:.1f} GB RAM)")
    lines.append(f"**Thời gian đo:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    lines.append(f"**Audit Log File:** `{audit_log_path}`")
    lines.append("")

    # Summary table
    lines.append("## 1. TỔNG HỢP HIỆU NĂNG TẢI ĐỒNG THỜI")
    lines.append(
        "| Mức tải (Concurrent) | Thời gian (s) | Tổng Requests | Thành công (%) | Peak RAM (MB) | "
        "Peak RSS (MB) | CPU TB (%) | CPU Đỉnh (%) | DoD Status |"
    )
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    all_passed = True
    for s in stages:
        dod_pass = s.success_rate_pct >= 95.0 and s.peak_ram_mb <= RAM_LIMIT_MB
        if not dod_pass:
            all_passed = False
        status_str = "PASSED" if dod_pass else "FAILED"
        lines.append(
            f"| **{s.concurrency} Sessions** | {s.duration_seconds}s | {s.total_requests} | "
            f"**{s.success_rate_pct}%** | {s.peak_ram_mb} MB | {s.peak_uvicorn_rss_mb} MB | "
            f"{s.avg_cpu_pct}% | {s.peak_cpu_pct}% | **{status_str}** |"
        )
    lines.append("")

    # Detailed per-endpoint breakdown
    lines.append("## 2. CHI TIẾT ĐỘ TRỄ THEO TỪNG ENDPOINT (LATENCY BREAKDOWN)")
    for s in stages:
        lines.append(f"### Mức tải: {s.concurrency} Concurrent Sessions")
        lines.append(
            "| Endpoint | Calls | Success % | Min (ms) | Avg (ms) | p50 (ms) | p95 (ms) | Max (ms) |"
        )
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for ep, lats in s.endpoint_metrics.items():
            counts = s.endpoint_counts.get(ep, {"success": 0, "failed": 0})
            total = counts["success"] + counts["failed"]
            pct = round((counts["success"] / max(1, total)) * 100.0, 1)
            min_l = round(min(lats), 1) if lats else 0.0
            avg_l = round(sum(lats) / max(1, len(lats)), 1) if lats else 0.0
            p50 = calc_percentile(lats, 50)
            p95 = calc_percentile(lats, 95)
            max_l = round(max(lats), 1) if lats else 0.0
            lines.append(
                f"| `{ep}` | {total} | {pct}% | {min_l} | {avg_l} | **{p50}** | **{p95}** | {max_l} |"
            )
        lines.append("")

    # Resource Ceiling & DoD
    lines.append("## 3. ĐÁNH GIÁ NGUY CƠ OOM & ĐỐI CHIẾU TIÊU CHÍ HOÀN THÀNH (DoD)")
    max_peak_ram = max(s.peak_ram_mb for s in stages) if stages else 0.0
    ram_headroom = total_mem_mb - max_peak_ram
    min_success_rate = min(s.success_rate_pct for s in stages) if stages else 0.0

    lines.append(
        f"- **Tiêu chí 1: Tỷ lệ thành công >= 95%:** "
        f"{'ĐẠT' if min_success_rate >= 95.0 else 'KHÔNG ĐẠT'} (Thấp nhất: **{min_success_rate}%**)"
    )
    lines.append(
        f"- **Tiêu chí 2: RAM không vượt quá 6.5GB (6656 MB):** "
        f"{'ĐẠT' if max_peak_ram <= RAM_LIMIT_MB else 'KHÔNG ĐẠT'} (Đỉnh: **{max_peak_ram} MB** / 8192 MB)"
    )
    lines.append(
        f"- **Khoảng an toàn bộ nhớ (Memory Headroom):** Còn trống **{ram_headroom:.1f} MB** "
        f"({(ram_headroom / total_mem_mb) * 100:.1f}% tổng RAM)"
    )
    total_audit = sum(s.audit_logs_recorded for s in stages)
    lines.append(
        f"- **Kiểm tra Storage Audit Log:** Đã ghi nhận tổng cộng **{total_audit} bản ghi** vào `{audit_log_path.name}`"
    )
    lines.append("")
    lines.append(
        f"> **KẾT LUẬN CHUNG:** {'ĐẠT CHUẨN UAT (ALL GATES PASSED)' if all_passed else 'CẦN TỐI ƯU THÊM'}"
    )

    return "\n".join(lines)


async def main() -> int:
    """CLI Entrypoint for load test."""
    parser = argparse.ArgumentParser(description="VeriScholar Load & Concurrency Benchmark")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API Base URL (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--stages",
        default="5,10",
        help="Comma-separated concurrency stages (default: 5,10)",
    )
    parser.add_argument(
        "--audit-log",
        default=str(DEFAULT_AUDIT_LOG),
        help=f"Path to api-audit.log (default: {DEFAULT_AUDIT_LOG})",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional path to write raw JSON output",
    )
    args = parser.parse_args()

    total_mem_mb, _, _ = get_system_ram_mb()
    audit_path = Path(args.audit_log)
    concurrency_stages = [int(x.strip()) for x in args.stages.split(",") if x.strip()]

    print("=" * 80)
    print("VERISCHOLAR CONCURRENCY & STRESS BENCHMARK (UAT)")
    print(f"Target URL: {args.base_url}")
    print(f"System: 2 vCPUs | {total_mem_mb / 1024:.1f} GB RAM")
    print(f"Concurrency Stages: {concurrency_stages}")
    print(f"Audit Log File: {audit_path}")
    print("=" * 80 + "\n")

    # Quick preflight check
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{args.base_url}/health/ready")
            if resp.status_code != 200:
                print(f"ERROR: Server at {args.base_url} returned status {resp.status_code}")
                return 1
    except Exception as exc:
        print(f"ERROR: Cannot connect to {args.base_url}: {exc}")
        return 1

    results: list[StageResult] = []
    for stage_idx, concurrency in enumerate(concurrency_stages, 1):
        print(f"[*] Starting Stage {stage_idx}: {concurrency} Concurrent Sessions...")
        res = await run_stage(concurrency, args.base_url, audit_path)
        results.append(res)
        print(
            f"    -> Finished in {res.duration_seconds}s | Requests: {res.total_requests} | "
            f"Success: {res.success_rate_pct}% | Peak RAM: {res.peak_ram_mb} MB | "
            f"Peak RSS: {res.peak_uvicorn_rss_mb} MB"
        )
        if stage_idx < len(concurrency_stages):
            print("    -> Cooling down for 2 seconds...\n")
            await asyncio.sleep(2.0)

    print("\n" + "=" * 80)
    report = format_markdown_report(results, total_mem_mb, audit_path)
    print(report)
    print("=" * 80 + "\n")

    if args.output_json:
        out_path = Path(args.output_json)
        out_data = {
            "timestamp": time.time(),
            "total_mem_mb": total_mem_mb,
            "stages": [
                {
                    "concurrency": s.concurrency,
                    "duration_seconds": s.duration_seconds,
                    "total_requests": s.total_requests,
                    "successful_requests": s.successful_requests,
                    "failed_requests": s.failed_requests,
                    "success_rate_pct": s.success_rate_pct,
                    "baseline_ram_mb": s.baseline_ram_mb,
                    "peak_ram_mb": s.peak_ram_mb,
                    "peak_uvicorn_rss_mb": s.peak_uvicorn_rss_mb,
                    "avg_cpu_pct": s.avg_cpu_pct,
                    "peak_cpu_pct": s.peak_cpu_pct,
                    "audit_logs_recorded": s.audit_logs_recorded,
                    "endpoint_metrics": s.endpoint_metrics,
                    "errors": s.errors,
                }
                for s in results
            ],
        }
        out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
        print(f"Saved raw metrics to {out_path}")

    # Return code based on DoD
    all_ok = all(s.success_rate_pct >= 95.0 and s.peak_ram_mb <= RAM_LIMIT_MB for s in results)
    return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
