"""VeriScholar Unified API Evaluation Harness CLI.

Allows executing automated autotest runner for a single API endpoint:
    uv run python scripts/eval_api.py --api upload

Or executing all 9 Module 1 endpoints sequentially in a unified test run:
    uv run python scripts/eval_api.py --all

Includes Anti-Cheating Invariant Gate: protects Ground Truth baseline immutability.
"""

import argparse
import asyncio
import json
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure project root and API package source are in Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
apps_api_src = PROJECT_ROOT / "apps" / "api" / "src"
if apps_api_src.exists() and str(apps_api_src) not in sys.path:
    sys.path.insert(0, str(apps_api_src))
packages_core_src = PROJECT_ROOT / "packages" / "core" / "src"
if packages_core_src.exists() and str(packages_core_src) not in sys.path:
    sys.path.insert(0, str(packages_core_src))

from scripts.eval.config import ARTIFACTS_DIR, REPORTS_DIR  # noqa: E402
from scripts.eval.context import EvaluationContext  # noqa: E402
from scripts.eval.runners import MODULE_1_ORDER, RUNNERS_MAP  # noqa: E402


def check_ground_truth_integrity(allow_blessed: bool = False) -> tuple[bool, str]:
    """Verify that Ground Truth files have not been secretly tampered with."""
    if allow_blessed:
        return True, "Ground truth modifications explicitly permitted via --bless."

    try:
        cmd = [
            "git",
            "status",
            "--porcelain",
            "--",
            "data/papers/",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]

        # Detect modifications to existing tracked expected json files
        tampered = []
        for line in lines:
            status_code = line[:2]
            filename = line[3:]
            if any(ext in filename for ext in [".expected.json", "golden_eval_dataset.json"]):
                if any(c in status_code for c in ["M", "D", "R"]):
                    tampered.append(f"  [{status_code}] {filename}")

        if tampered:
            msg = (
                "[CRITICAL] VIOLATION: Phát hiện thay đổi trái phép trong Ground Truth baseline!\n"
                + "\n".join(tampered)
                + "\nĐể ngăn chặn Reward Hacking (Specification Gaming), runner tự hủy.\n"
                "Nếu đây là thay đổi hợp thức do con người phê duyệt, hãy chạy kèm cờ: --bless"
            )
            return False, msg

        return True, "Ground truth integrity verified (No illicit modifications)."
    except Exception as e:
        return True, f"Git status check skipped: {e}"


async def run_single_api(
    api_alias: str,
    base_url: str,
    ci_gate: bool = False,
) -> bool:
    """Execute evaluation for a single API endpoint."""
    if api_alias not in RUNNERS_MAP:
        print(f"[ERROR] Không tìm thấy runner cho API alias: '{api_alias}'")
        print(f"Danh sách hợp lệ: {', '.join(RUNNERS_MAP.keys())}")
        return False

    runner_cls = RUNNERS_MAP[api_alias]
    runner = runner_cls()
    print("\n" + "=" * 70)
    print(f"  Chạy Autotest Snapshot: [{runner.http_method}] {runner.route_path}")
    print("=" * 70)

    async with EvaluationContext(base_url=base_url) as ctx:
        mode_str = "In-Process ASGI" if ctx._is_asgi_fallback else f"Live HTTP ({base_url})"
        print(f"[*] Phiên làm việc: {ctx.session_tag} | Kết nối: {mode_str}")

        result = await runner.evaluate(ctx)
        passed = result.get("all_passed", False)
        status_tag = "[PASS]" if passed else "[FAIL]"
        report_path = REPORTS_DIR / runner.report_filename
        print(f"{status_tag} Kết quả: {status_tag} | Báo cáo: {report_path}")

        if not passed and ci_gate:
            return False
        return passed


async def run_all_apis(
    base_url: str,
    ci_gate: bool = False,
) -> bool:
    """Execute end-to-end sequential evaluation for all 9 Module 1 APIs."""
    print("\n" + "=" * 72)
    print("  BẮT ĐẦU CHẠY TOÀN BỘ 9 AUTOTEST APIS (MODULE 1: INGESTION & DEEP READ)")
    print("=" * 72)

    total = len(MODULE_1_ORDER)
    passed_count = 0
    all_results: dict[str, Any] = {}

    async with EvaluationContext(base_url=base_url) as ctx:
        mode_str = "In-Process ASGI" if ctx._is_asgi_fallback else f"Live HTTP ({base_url})"
        print(f"[*] Session Tenant: {ctx.session_tag} | Transport: {mode_str}\n")

        # Share primary document_id across pipeline flow when possible
        shared_doc_id = None

        for idx, alias in enumerate(MODULE_1_ORDER, 1):
            runner_cls = RUNNERS_MAP[alias]
            runner = runner_cls()
            banner = f"[{idx}/{total}] Đánh giá: [{runner.http_method}] {runner.route_path} ..."
            print(banner, end=" ")

            try:
                res = await runner.evaluate(ctx, document_id=shared_doc_id)
                passed = res.get("all_passed", False)
                all_results[alias] = res

                # Capture uploaded document_id for downstream pipeline endpoints
                if alias == "upload":
                    for c in res.get("cases", []):
                        if c.get("doc_id"):
                            shared_doc_id = c["doc_id"]
                            break

                if passed:
                    passed_count += 1
                    print("✓ PASSED")
                else:
                    print("✗ FAILED")
            except Exception as e:
                print(f"✗ ERROR: {e}")
                all_results[alias] = {"all_passed": False, "error": str(e)}

        # Output summary metrics JSON
        summary_file = ARTIFACTS_DIR / "eval_metrics.json"
        summary_payload = {
            "total_apis": total,
            "passed_apis": passed_count,
            "failed_apis": total - passed_count,
            "quality_gate_passed": passed_count == total,
            "session_tag": ctx.session_tag,
            "endpoints": all_results,
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 72)
    print(f"  TỔNG KẾT: {passed_count}/{total} APIs ĐẠT CHUẨN QUALITY GATE")
    print(f"  Tệp chỉ số máy đọc: {summary_file}")
    print(f"  Thư mục báo cáo Markdown: {REPORTS_DIR}")
    print("=" * 72 + "\n")

    is_success = passed_count == total
    if not is_success and ci_gate:
        return False
    return is_success


def main() -> None:
    parser = argparse.ArgumentParser(description="VeriScholar API Snapshot & Evaluation Runner")
    parser.add_argument(
        "--api",
        type=str,
        choices=list(RUNNERS_MAP.keys()),
        help="Chạy autotest riêng cho 1 API chỉ định",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Chạy tự động toàn bộ autotest của tất cả 9 APIs Module 1",
    )
    parser.add_argument(
        "--ci-gate",
        action="store_true",
        help="Thoát với exit code 1 nếu có bất kỳ API nào không đạt ngân sách chất lượng",
    )
    parser.add_argument(
        "--bless",
        action="store_true",
        help="Cho phép thay đổi Ground Truth baseline (bảo vệ chống Reward Hacking)",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Địa chỉ gốc của API server (Mặc định: http://localhost:8000)",
    )

    args = parser.parse_args()

    if not args.api and not args.all:
        parser.print_help()
        sys.exit(0)

    # Invariant Gate: Check Ground Truth integrity against Git
    gt_ok, gt_msg = check_ground_truth_integrity(allow_blessed=args.bless)
    if not gt_ok:
        print(f"\n{gt_msg}\n", file=sys.stderr)
        sys.exit(2)

    # Attach signal handler for graceful cleanup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = None

    def handle_signal():
        if main_task and not main_task.done():
            print("\n[WARN] Nhận tín hiệu ngắt. Kích hoạt dọn dẹp tài nguyên trước khi thoát...")
            main_task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal)
        except NotImplementedError:
            pass

    async def runner_wrapper():
        if args.api:
            return await run_single_api(args.api, base_url=args.base_url, ci_gate=args.ci_gate)
        else:
            return await run_all_apis(base_url=args.base_url, ci_gate=args.ci_gate)

    try:
        main_task = loop.create_task(runner_wrapper())
        success = loop.run_until_complete(main_task)
        sys.exit(0 if success else 1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[INFO] Đã hủy tiến trình đánh giá theo yêu cầu.")
        sys.exit(130)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
