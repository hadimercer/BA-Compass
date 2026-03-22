"""Database connection and query helpers for BA Compass."""

from __future__ import annotations

import json
import logging
from typing import Any

import psycopg2
from psycopg2.extras import Json, RealDictCursor
import streamlit as st


LOGGER = logging.getLogger(__name__)


def get_connection() -> psycopg2.extensions.connection:
    """Open a new database connection for a single request."""
    try:
        return psycopg2.connect(
            st.secrets["neon_db_url"],
            cursor_factory=RealDictCursor,
            connect_timeout=15,
        )
    except Exception as exc:
        LOGGER.exception("Unable to establish the database connection.")
        raise RuntimeError(
            "Unable to connect to the database. Please verify the configured secrets."
        ) from exc


def generate_roadmap_from_template(project_id: str, engagement_type: str, scale_tier: str) -> int:
    """Instantiate a live roadmap for a project from the matching template.

    Deletes any existing roadmap items for the project first (supports reclassification).
    Returns the number of modules inserted, or 0 if no matching template exists.
    """
    rows = run_query(
        "SELECT module_sequence FROM roadmap_templates WHERE engagement_type = %s AND scale_tier = %s LIMIT 1",
        (engagement_type, scale_tier),
        fetch=True,
    )
    if not rows:
        return 0

    import json as _json
    module_ids: list[str] = _json.loads(rows[0]["module_sequence"]) if isinstance(rows[0]["module_sequence"], str) else rows[0]["module_sequence"]

    run_query("DELETE FROM project_roadmap_items WHERE project_id = %s", (project_id,), fetch=False)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for order, module_id in enumerate(module_ids, start=1):
                cur.execute(
                    """
                    INSERT INTO project_roadmap_items (project_id, module_id, sequence_order, status)
                    VALUES (%s, %s, %s, 'not_started')
                    """,
                    (project_id, module_id, order),
                )
        conn.commit()
    finally:
        conn.close()

    return len(module_ids)


def get_conversation_history(project_id: str, module_id: str) -> list[dict]:
    """Return all co-pilot messages for a project+module, ordered chronologically."""
    rows = run_query(
        """
        SELECT role, content, created_at
        FROM conversation_history
        WHERE project_id = %s AND module_id = %s
        ORDER BY created_at
        """,
        (project_id, module_id),
        fetch=True,
    )
    return [dict(r) for r in rows]


def save_message(project_id: str, module_id: str, role: str, content: str) -> None:
    """Persist a single co-pilot message turn."""
    run_query(
        "INSERT INTO conversation_history (project_id, module_id, role, content) VALUES (%s, %s, %s, %s)",
        (project_id, module_id, role, content),
        fetch=False,
    )


def get_latest_artifact(project_id: str, module_id: str) -> dict | None:
    """Return the highest-version artifact for a project+module, or None."""
    rows = run_query(
        """
        SELECT artifact_id, artifact_type, content, version, updated_at
        FROM artifacts
        WHERE project_id = %s AND module_id = %s
        ORDER BY version DESC
        LIMIT 1
        """,
        (project_id, module_id),
        fetch=True,
    )
    return dict(rows[0]) if rows else None


def save_artifact(project_id: str, module_id: str, artifact_type: str, content_text: str) -> dict:
    """Insert a new versioned artifact. Returns the new artifact_id and version."""
    rows = run_query(
        "SELECT COALESCE(MAX(version), 0) AS max_ver FROM artifacts WHERE project_id = %s AND module_id = %s",
        (project_id, module_id),
        fetch=True,
    )
    next_version = (rows[0]["max_ver"] if rows else 0) + 1
    result = run_query(
        """
        INSERT INTO artifacts (project_id, module_id, artifact_type, content, version)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING artifact_id, version
        """,
        (project_id, module_id, artifact_type, Json({"text": content_text}), next_version),
        fetch=True,
    )
    return dict(result[0]) if result else {}


def get_completed_artifacts_summary(project_id: str, exclude_module_id: str) -> list[dict]:
    """Return name + content text for all complete-status modules with saved artifacts."""
    rows = run_query(
        """
        SELECT DISTINCT ON (a.module_id)
            m.name AS module_name,
            a.content,
            a.version
        FROM artifacts a
        JOIN modules m ON m.module_id = a.module_id
        WHERE a.project_id = %s AND a.module_id::text != %s
        ORDER BY a.module_id, a.version DESC
        """,
        (project_id, exclude_module_id),
        fetch=True,
    )
    result = []
    for r in rows:
        content = r["content"]
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        result.append({"module_name": r["module_name"], "text": text[:800]})
    return result


def get_all_project_artifacts(project_id: str, exclude_module_id: str) -> list[dict]:
    """Return full text of all saved artifacts for a project (excluding the current module).

    Includes created_at and knowledge_area so the caller can apply token-aware truncation.
    Results are ordered oldest-first so the caller can easily identify the most-recent-N.
    """
    rows = run_query(
        """
        SELECT DISTINCT ON (a.module_id)
            m.name AS module_name,
            m.knowledge_area,
            a.content,
            a.version,
            a.created_at
        FROM artifacts a
        JOIN modules m ON m.module_id = a.module_id
        WHERE a.project_id = %s AND a.module_id::text != %s
        ORDER BY a.module_id, a.version DESC
        """,
        (project_id, exclude_module_id),
        fetch=True,
    )
    result = []
    for r in rows:
        content = r["content"]
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        result.append({
            "module_name": r["module_name"],
            "knowledge_area": r["knowledge_area"],
            "version": r["version"],
            "created_at": r["created_at"],
            "text": text,
        })
    result.sort(key=lambda x: x["created_at"] or "")
    return result


def set_last_active_project(user_id: str, project_id: str) -> None:
    """Persist the last active project ID to the user record."""
    run_query(
        "UPDATE users SET last_active_project_id = %s WHERE user_id = %s",
        (project_id, user_id),
        fetch=False,
    )


def get_last_active_project(user_id: str) -> str | None:
    """Return the user's last active project ID, or None."""
    rows = run_query(
        "SELECT last_active_project_id FROM users WHERE user_id = %s LIMIT 1",
        (user_id,),
        fetch=True,
    )
    if rows and rows[0].get("last_active_project_id"):
        return str(rows[0]["last_active_project_id"])
    return None


def run_query(sql: str, params: tuple = None, fetch: bool = True) -> list[Any] | None:
    """Execute a SQL statement and return results.

    Opens and closes a connection per call — safe for multi-session use.
    Commits automatically for non-SELECT statements.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall() if fetch and cursor.description else []
        if sql.lstrip().split(None, 1)[0].upper() != "SELECT":
            conn.commit()
        return rows if fetch else None
    except Exception as exc:
        conn.rollback()
        LOGGER.exception("Database query failed.")
        raise RuntimeError(
            "We couldn't complete that database request. Please try again."
        ) from exc
    finally:
        conn.close()
