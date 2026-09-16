"""VeriScholar API Evaluation & Snapshot Automation Harness.

Orchestrates sequential testing of Module 1 APIs against the Golden Papers Dataset,
enforcing Quality Budgets, Zero-Cost VCR replay, and Anti-Cheat Invariants.
"""

import argparse
import asyncio
import json
import logging
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.config import (  # noqa: E402
    ARTIFACTS_DIR,
    DATA_PAPERS_DIR,
    REPORTS_DIR,
    TEMP_OUTPUT_TEST_DIR,
)
from scripts.eval.context import EvaluationContext  # noqa: E402
from scripts.eval.runners import (  # noqa: E402
    MODULE_1_ORDER,
    RUNNERS_MAP,
)


def check_ground_truth_integrity(allow_blessed: bool = False) -> tuple[bool, str]:
    """Anti-Cheat Invariant 1: Ensures Golden Dataset ground truth files have not been modified."""
    if allow_blessed:
        return True, "Snapshot Blessing enabled (--bless)."

    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", str(DATA_PAPERS_DIR)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            dirty_files = []
            for line in proc.stdout.strip().splitlines():
                if len(line) >= 3:
                    file_path = line[3:].strip()
                    if file_path.endswith(".expected.json") or file_path.endswith(
                        "golden_eval_dataset.json"
                    ):
                        dirty_files.append(file_path)

            if dirty_files:
                return False, (
                    "PHÁT HIỆN GIAN LẬN: Tệp Ground Truth bị thay đổi trái phép:\n  "
                    + "\n  ".join(dirty_files)
                    + "\nSử dụng cờ --bless nếu bạn chủ đích cập nhật dữ liệu chuẩn đối chứng."
                )
    except Exception as e:
        return True, f"Bỏ qua kiểm tra git: {e}"

    return True, "Ground Truth integrity verified."


async def run_single_api(
    api_alias: str,
    base_url: str,
    ci_gate: bool = False,
    keep_data: bool = False,
    user_id: str | None = None,
    paper: str | None = None,
    interactive: bool = False,
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

    async with EvaluationContext(
        base_url=base_url,
        keep_data=keep_data,
        user_id=user_id,
    ) as ctx:
        mode_str = "In-Process ASGI" if ctx._is_asgi_fallback else f"Live HTTP ({base_url})"
        print(f"[*] Phiên làm việc: {ctx.session_tag} | Kết nối: {mode_str}")
        if keep_data:
            print("[*] Chế độ Seed Data (--keep-data): Bảo tồn bản ghi database và tệp vật lý.")

        result = await runner.evaluate(ctx, paper=paper, interactive=interactive)
        passed = result.get("all_passed", False)
        status_tag = "[PASS]" if passed else "[FAIL]"
        report_path = TEMP_OUTPUT_TEST_DIR / runner.report_filename
        print(f"\n{status_tag} Kết quả: {status_tag} | Báo cáo đầy đủ: {report_path}")

        if not passed and ci_gate:
            return False
        return passed


async def run_all_apis(
    base_url: str,
    ci_gate: bool = False,
    keep_data: bool = False,
    user_id: str | None = None,
    interactive: bool = False,
) -> bool:
    """Execute end-to-end sequential evaluation for all 9 Module 1 APIs."""
    print("\n" + "=" * 72)
    print("  BẮT ĐẦU CHẠY TOÀN BỘ 9 AUTOTEST APIS (MODULE 1: INGESTION & DEEP READ)")
    print("=" * 72)

    total = len(MODULE_1_ORDER)
    passed_count = 0
    all_results: dict[str, Any] = {}

    async with EvaluationContext(
        base_url=base_url,
        keep_data=keep_data,
        user_id=user_id,
    ) as ctx:
        for idx, alias in enumerate(MODULE_1_ORDER, 1):
            runner_cls = RUNNERS_MAP[alias]
            runner = runner_cls()
            print(f"\n[{idx}/{total}] Đang đánh giá: [{runner.http_method}] {runner.route_path}...")
            try:
                res = await runner.evaluate(ctx, interactive=interactive)
                all_results[alias] = res
                if res.get("all_passed", False):
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
    print(f"  Thư mục báo cáo Markdown: {TEMP_OUTPUT_TEST_DIR}")
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
    parser.add_argument(
        "--paper",
        type=str,
        default=None,
        help="Chỉ định tệp paper PDF cụ thể để kiểm thử (ví dụ: 'Attention Is All You Need.pdf')",
    )
    parser.add_argument(
        "--keep-data",
        "-k",
        action="store_true",
        help="Giữ lại dữ liệu đã tạo trong DB (không dọn dẹp) để phục vụ kiểm thử thủ công/Swagger",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=None,
        help="Gán session/user ID cụ thể cho việc nạp tài liệu (ví dụ để kiểm tra qua Swagger)",
    )
    parser.add_argument(
        "--confirm-overwrite",
        "-i",
        action="store_true",
        help="Dừng lại hỏi xác nhận ghi đè trước khi làm mới tệp báo cáo markdown đã tồn tại",
    )
    parser.add_argument(
        "--debug-sql",
        action="store_true",
        help="Bật in log SQL chi tiết từ SQLAlchemy Engine ra terminal",
    )

    args = parser.parse_args()

    # Query log hygiene: silence verbose SQL logging unless explicitly asked
    if not args.debug_sql:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    if not args.api and not args.all:
        parser.print_help()
        sys.exit(0)

    # Invariant Gate: Check Ground Truth integrity against Git
    gt_ok, gt_msg = check_ground_truth_integrity(allow_blessed=args.bless)
    if not gt_ok:
        print(f"\n[CRITICAL SECURITY GATE] {gt_msg}\n", file=sys.stderr)
        sys.exit(2)

    # Signal-Safe Cancellation setup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = None

    def handle_sig():
        if main_task and not main_task.done():
            main_task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_sig)
        except NotImplementedError:
            pass

    async def _runner():
        if args.api:
            return await run_single_api(
                api_alias=args.api,
                base_url=args.base_url,
                ci_gate=args.ci_gate,
                keep_data=args.keep_data,
                user_id=args.user_id,
                paper=args.paper,
                interactive=args.confirm_overwrite,
            )
        else:
            return await run_all_apis(
                base_url=args.base_url,
                ci_gate=args.ci_gate,
                keep_data=args.keep_data,
                user_id=args.user_id,
                interactive=args.confirm_overwrite,
            )

    main_task = loop.create_task(_runner())
    try:
        success = loop.run_until_complete(main_task)
        sys.exit(0 if success else 1)
    except asyncio.CancelledError:
        print("\n[WARN] Nhận tín hiệu dừng (SIGINT). Đã dọn dẹp khép kín qua REST API.")
        sys.exit(130)


if __name__ == "__main__":
    main()
