"""Evaluation Script Runner for Cross-Document Q&A & Ambiguity Resolution API Snapshot.

Target: POST /api/v1/sessions/{id}/messages & Session Turns (#52 - #54)
Design Document: docs/vi/design-api-eval-snapshots.md
Output Report: temp/output/test/post_sessions_chat.md
"""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.context import EvaluationContext  # noqa: E402
from scripts.eval.runners.post_sessions_chat import PostSessionsChatAPIRunner  # noqa: E402


def setup_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="VeriScholar Cross-Document Chat & Ambiguity Resolution API Evaluator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL của backend server (mặc định: http://localhost:8000, fallback ASGI in-process)",
    )
    parser.add_argument(
        "--paper",
        default="Attention Is All You Need.pdf",
        help="Tên tệp PDF chuẩn trong data/papers/ dùng để đánh giá",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Giữ lại tài liệu và phiên trong cơ sở dữ liệu sau khi chạy (mặc định: tự động dọn sạch)",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Bật chế độ hỏi xác nhận ghi đè tệp báo cáo cũ (y/n)",
    )
    parser.add_argument(
        "--debug-sql",
        action="store_true",
        help="Bật log truy vấn SQL chi tiết (SQLAlchemy engine ECHO)",
    )
    return parser


async def run_chat_evaluation(
    base_url: str,
    paper: str,
    keep_data: bool = False,
    interactive: bool = False,
    debug_sql: bool = False,
) -> bool:
    if not debug_sql:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    print("=" * 78)
    print("  VERISCHOLAR API EVALUATION SNAPSHOT: CROSS-DOCUMENT CHAT (#52 - #54)")
    print("=" * 78)

    runner = PostSessionsChatAPIRunner()

    async with EvaluationContext(base_url=base_url, keep_data=keep_data) as ctx:
        mode_str = "In-Process ASGI" if ctx._is_asgi_fallback else f"Live HTTP ({base_url})"
        print(f"[*] Phiên làm việc: {ctx.session_tag} | Kết nối: {mode_str}")
        print(f"[*] Tài liệu kiểm thử: {paper}")

        result = await runner.evaluate(
            ctx=ctx,
            paper=paper,
            interactive=interactive,
        )

        all_passed = result.get("all_passed", False)
        report_path = result.get("report_path", "temp/output/test/post_sessions_chat.md")

        print("\n" + "=" * 78)
        if all_passed:
            print("  [PASS] Toàn bộ test scenarios thành công! (100% Invariants Verified)")
        else:
            print("  [FAIL] Một hoặc nhiều test scenario không đạt yêu cầu.")
        print(f"  -> Tệp báo cáo Markdown: {report_path}")
        print("=" * 78 + "\n")

        return all_passed


def main() -> None:
    parser = setup_cli()
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = None

    def handle_signal(sig, frame):
        nonlocal main_task
        print("\n[WARN] Nhận tín hiệu dừng (SIGINT/SIGTERM). Tiến hành dọn dẹp qua REST API...")
        if main_task and not main_task.done():
            main_task.cancel()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        main_task = loop.create_task(
            run_chat_evaluation(
                base_url=args.base_url,
                paper=args.paper,
                keep_data=args.keep_data,
                interactive=args.interactive,
                debug_sql=args.debug_sql,
            )
        )
        passed = loop.run_until_complete(main_task)
        sys.exit(0 if passed else 1)
    except asyncio.CancelledError:
        print("[*] Quá trình kiểm thử đã dừng an toàn.")
        sys.exit(130)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
