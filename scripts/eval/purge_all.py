"""Utility script to cleanly purge all documents from the database and CAS storage via REST API."""

import asyncio
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.context import EvaluationContext  # noqa: E402


async def purge_all_documents() -> None:
    print("=" * 70)
    print("  DỌN DẸP TOÀN BỘ DỮ LIỆU TÀI LIỆU TRÊN HỆ THỐNG (ZERO-RETENTION PURGE)")
    print("=" * 70)

    async with EvaluationContext() as ctx:
        assert ctx.client is not None

        # 1. Fetch all documents currently in the system
        res = await ctx.client.get("/api/v1/documents?page=1&per_page=100")
        if res.status_code != 200:
            print(f"[!] Lỗi khi truy vấn danh sách documents: HTTP {res.status_code}")
            sys.exit(1)

        payload = res.json()
        docs = payload.get("data", [])
        total = payload.get("meta", {}).get("total", len(docs))

        if not docs:
            print("[✓] Cơ sở dữ liệu hiện tại đã hoàn toàn sạch sẽ (0 documents).")
            return

        print(f"[*] Tìm thấy {total} tài liệu cần xóa sạch. Đang tiến hành xóa từng bản ghi...\n")

        deleted_count = 0
        for doc in docs:
            doc_id = doc["id"]
            filename = doc.get("filename", "Unknown")
            del_res = await ctx.client.delete(f"/api/v1/documents/{doc_id}")
            if del_res.status_code in (200, 204):
                deleted_count += 1
                print(f"  ✓ Đã xóa [{deleted_count}/{len(docs)}]: {doc_id} ({filename})")
            else:
                print(f"  ✗ Xóa thất bại [{doc_id}]: HTTP {del_res.status_code}")

        # 2. Verify final count
        verify_res = await ctx.client.get("/api/v1/documents?page=1&per_page=10")
        final_total = verify_res.json().get("meta", {}).get("total", 0)

        print("\n" + "=" * 70)
        print(f"[✓] HOÀN TẤT DỌN DẸP: Đã xóa thành công {deleted_count} tài liệu.")
        print(f"[✓] Tổng số bản ghi còn lại trên database: {final_total}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(purge_all_documents())
