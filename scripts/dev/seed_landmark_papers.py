#!/usr/bin/env -S uv run python3
"""CLI script to seed 12 Landmark LLM papers with citations for target users."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "api" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "core" / "src"))

from api.db.models.user import UserModel
from api.db.session import AsyncSessionLocal
from api.services.landmark_papers_seeder import (
    LANDMARK_PAPERS,
    seed_landmark_papers_for_user,
)
from sqlalchemy import select


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed landmark LLM papers for users")
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="Target user email (defaults to dungdam.gg15@gmail.com and dev@verischolar.edu.vn)",
    )
    args = parser.parse_args()

    target_emails = (
        [args.email] if args.email else ["dungdam.gg15@gmail.com", "dev@verischolar.edu.vn"]
    )

    blobs_dir = ROOT_DIR / "storage" / "blobs"
    blobs_dir.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionLocal() as session:
        for email in target_emails:
            user_stmt = select(UserModel).where(UserModel.email == email)
            res = await session.execute(user_stmt)
            user = res.scalar_one_or_none()

            if not user:
                print(f"User {email} not found in database. Skipping.")
                continue

            print(
                f"Seeding {len(LANDMARK_PAPERS)} landmark papers for user: {user.email} ({user.id})..."
            )
            count = await seed_landmark_papers_for_user(session, user.id, blobs_dir)
            print(f"Successfully seeded {count} papers and citation graph for {user.email}!")


if __name__ == "__main__":
    asyncio.run(main())
