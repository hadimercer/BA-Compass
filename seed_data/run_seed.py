"""
Idempotent seed script for BA Compass.
Run once after db_init.sql to populate modules and roadmap templates.

Usage (from the BA-Compass project root):
    python seed_data/run_seed.py

Requires NEON_DB_URL as an environment variable or in a .env file at project root.
"""

from __future__ import annotations

import json
import os
import sys

import psycopg2
from psycopg2.extras import RealDictCursor

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_data.modules import MODULES
from seed_data.templates import TEMPLATES

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; env var can be set directly


def get_conn():
    url = os.environ.get("NEON_DB_URL")
    if not url:
        sys.exit(
            "ERROR: NEON_DB_URL environment variable not set.\n"
            "Add it to a .env file in the project root or set it in your shell."
        )
    return psycopg2.connect(url, cursor_factory=RealDictCursor, connect_timeout=15)


def seed_modules(conn) -> dict[str, str]:
    """Insert all modules if the table is empty. Returns {name: module_id} lookup."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM modules")
        count = cur.fetchone()["cnt"]

    if count > 0:
        print(f"  modules: already contains {count} rows — skipping insert.")
        with conn.cursor() as cur:
            cur.execute("SELECT module_id, name FROM modules")
            return {row["name"]: str(row["module_id"]) for row in cur.fetchall()}

    print(f"  modules: inserting {len(MODULES)} rows...")
    with conn.cursor() as cur:
        for m in MODULES:
            cur.execute(
                """
                INSERT INTO modules (name, knowledge_area, description)
                VALUES (%s, %s, %s)
                RETURNING module_id, name
                """,
                (m["name"], m["knowledge_area"], m.get("description")),
            )
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("SELECT module_id, name FROM modules")
        lookup = {row["name"]: str(row["module_id"]) for row in cur.fetchall()}

    print(f"  modules: inserted {len(lookup)} rows.")
    return lookup


def seed_templates(conn, module_lookup: dict[str, str]) -> None:
    """Insert all roadmap templates if the table is empty."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM roadmap_templates")
        count = cur.fetchone()["cnt"]

    if count > 0:
        print(f"  roadmap_templates: already contains {count} rows — skipping insert.")
        return

    print(f"  roadmap_templates: inserting {len(TEMPLATES)} rows...")
    errors = []

    with conn.cursor() as cur:
        for t in TEMPLATES:
            sequence_ids = []
            for module_name in t["module_sequence"]:
                module_id = module_lookup.get(module_name)
                if not module_id:
                    errors.append(
                        f"  WARNING: module '{module_name}' not found in DB "
                        f"(template: {t['engagement_type']} / {t['scale_tier']})"
                    )
                    continue
                sequence_ids.append(module_id)

            cur.execute(
                """
                INSERT INTO roadmap_templates (engagement_type, scale_tier, module_sequence)
                VALUES (%s, %s, %s)
                """,
                (t["engagement_type"], t["scale_tier"], json.dumps(sequence_ids)),
            )

    conn.commit()

    if errors:
        print("\n".join(errors))
    print(f"  roadmap_templates: inserted {len(TEMPLATES)} rows.")


def main():
    print("BA Compass seed — connecting to database...")
    conn = get_conn()
    try:
        module_lookup = seed_modules(conn)
        seed_templates(conn, module_lookup)
        print("Seed complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
