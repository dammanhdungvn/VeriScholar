#!/usr/bin/env python3
"""
Sync local Dev PostgreSQL database to remote VPS (UAT/Staging).
Uses asyncpg/SQLAlchemy to export tables from local DB and pipes to remote psql.
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_DB_URL = os.getenv(
    "LOCAL_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://verischolar:verischolar@localhost:5432/verischolar",
    ),
)
SSH_KEY = os.getenv("SSH_KEY", "/home/dammanhdungvn/Downloads/VPS/VeriScholar_key.pem")
SSH_HOST = os.getenv("SSH_HOST", "48.193.46.15")
SSH_USER = os.getenv("SSH_USER", "VeriScholar")
REMOTE_CONTAINER = os.getenv("REMOTE_CONTAINER", "verischolar-postgres-dev")
REMOTE_DB = os.getenv("REMOTE_DB", "verischolar")


def format_sql_value(val) -> str:
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, UUID):
        return f"'{str(val)}'"
    if isinstance(val, datetime):
        return f"'{val.isoformat()}'"
    if isinstance(val, (dict, list)):
        dumped = json.dumps(val).replace("'", "''")
        return f"'{dumped}'::jsonb"
    if isinstance(val, bytes):
        hex_val = val.hex()
        return f"'\\x{hex_val}'::bytea"
    s = str(val).replace("'", "''")
    return f"'{s}'"


async def generate_sync_sql() -> tuple[str, dict[str, int]]:
    engine = create_async_engine(LOCAL_DB_URL)
    sql_lines = [
        "BEGIN;",
        "SET session_replication_role = 'replica';",
    ]
    summary = {}

    # Define table ordering to respect logical hierarchies
    preferred_order = [
        "users",
        "scholar_profiles",
        "user_api_keys",
        "research_sessions",
        "folders",
        "documents",
        "document_storage_blobs",
        "document_summaries",
        "document_chunks",
        "reference_items",
        "session_documents",
        "session_turns",
        "research_notes",
        "graph_nodes",
        "graph_edges",
        "drafts",
        "draft_assets",
        "draft_messages",
    ]

    async with engine.connect() as conn:
        # Get all public tables
        res = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            )
        )
        existing_tables = {r[0] for r in res.fetchall()}

        ordered_tables = [t for t in preferred_order if t in existing_tables]
        for t in existing_tables:
            if t not in ordered_tables:
                ordered_tables.append(t)

        for table in ordered_tables:
            # Check row count
            count_res = await conn.execute(text(f"SELECT count(*) FROM {table};"))
            count = count_res.scalar()
            if not count:
                continue

            summary[table] = count
            rows_res = await conn.execute(text(f"SELECT * FROM {table};"))
            rows = rows_res.mappings().fetchall()

            for r in rows:
                cols = list(r.keys())
                vals = [format_sql_value(r[c]) for c in cols]
                cols_str = ", ".join(f'"{c}"' for c in cols)
                vals_str = ", ".join(vals)

                if table == "document_storage_blobs":
                    update_set = ", ".join(
                        f'"{c}" = EXCLUDED."{c}"' for c in cols if c not in ("id", "content_hash")
                    )
                    sql_lines.append(
                        f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str}) '
                        f'ON CONFLICT ("content_hash") DO UPDATE SET {update_set};'
                    )
                elif "id" in cols:
                    update_set = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in cols if c != "id")
                    sql_lines.append(
                        f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str}) '
                        f'ON CONFLICT ("id") DO UPDATE SET {update_set};'
                    )
                elif table == "session_documents":
                    sql_lines.append(
                        f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str}) '
                        f'ON CONFLICT ("session_id", "document_id") DO NOTHING;'
                    )
                else:
                    sql_lines.append(
                        f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str}) '
                        f"ON CONFLICT DO NOTHING;"
                    )

    # Ensure document blob_id references match canonical CAS blob id by content_hash
    sql_lines.append(
        'UPDATE "documents" d SET blob_id = b.id FROM "document_storage_blobs" b '
        "WHERE d.content_hash = b.content_hash AND (d.blob_id IS NULL OR d.blob_id != b.id);"
    )

    sql_lines.append("SET session_replication_role = 'origin';")
    sql_lines.append("COMMIT;")
    await engine.dispose()
    return "\n".join(sql_lines), summary


def sync_to_remote(sql_payload: str) -> None:
    remote_cmd = (
        f"docker exec -i {REMOTE_CONTAINER} psql -U verischolar -d {REMOTE_DB} -v ON_ERROR_STOP=1"
    )
    ssh_cmd = [
        "ssh",
        "-i",
        SSH_KEY,
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{SSH_USER}@{SSH_HOST}",
        remote_cmd,
    ]

    proc = subprocess.Popen(
        ssh_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate(input=sql_payload)

    if proc.returncode != 0:
        print(f"Error during remote sync (code {proc.returncode}):\n{stderr}", file=sys.stderr)
        sys.exit(proc.returncode)


def main():
    print("=== [VeriScholar Dev DB Sync] Connecting to local PostgreSQL ===")
    sql_payload, summary = asyncio.run(generate_sync_sql())

    if not summary:
        print("No rows found in local database to sync.")
        return

    print("Tables and rows to sync:")
    for tbl, count in summary.items():
        print(f"  • {tbl}: {count} row(s)")

    print(f"-> Streaming SQL payload to {SSH_USER}@{SSH_HOST} ({REMOTE_CONTAINER})...")
    sync_to_remote(sql_payload)
    print("=== [VeriScholar Dev DB Sync] Database sync completed successfully! ===")


if __name__ == "__main__":
    main()
