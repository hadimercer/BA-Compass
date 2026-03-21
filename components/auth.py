"""Authentication helpers for BA Compass email and password sign-in."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Any

import bcrypt
from psycopg2 import errorcodes
import streamlit as st

from components.db import run_query


def _get_query_param_token() -> str | None:
    """Read the session token from query params when present."""
    token = st.query_params.get("token")
    if isinstance(token, list):
        return token[0] if token else None
    return token


def _remove_query_param_token() -> None:
    """Remove the session token from query params."""
    try:
        st.query_params.pop("token")
    except KeyError:
        pass


def _get_user_by_token(session_token: str) -> dict[str, Any] | None:
    """Fetch a user record for a session token and drop expired sessions."""
    user_rows = run_query(
        """
        SELECT user_id, email, session_token, session_expires_at, created_at
        FROM users
        WHERE session_token = %s
        LIMIT 1
        """,
        (session_token,),
        fetch=True,
    )

    if not user_rows:
        return None

    user = dict(user_rows[0])
    expires_at = user.get("session_expires_at")
    if expires_at and expires_at.replace(tzinfo=None) < datetime.utcnow():
        try:
            run_query(
                """
                UPDATE users
                SET session_token = NULL,
                    session_expires_at = NULL
                WHERE user_id = %s
                """,
                (user["user_id"],),
                fetch=False,
            )
        except RuntimeError:
            pass
        return None

    return user


def _normalize_email(email: str) -> str:
    """Normalize email addresses before persistence and lookup."""
    return email.strip().lower()


def _clear_session_state() -> None:
    """Remove session-specific state from Streamlit."""
    st.session_state.pop("session_token", None)
    st.session_state.pop("active_project_id", None)


def hash_password(password: str) -> str:
    """Return a bcrypt hash for the supplied password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_user(email: str, password: str) -> dict[str, Any]:
    """Create a new user record and return the stored user."""
    normalized_email = _normalize_email(email)
    query = """
        INSERT INTO users (email, password_hash)
        VALUES (%s, %s)
        RETURNING user_id, email, created_at
    """

    try:
        rows = run_query(query, (normalized_email, hash_password(password)), fetch=True)
    except RuntimeError as exc:
        if getattr(exc.__cause__, "pgcode", None) == errorcodes.UNIQUE_VIOLATION:
            raise ValueError("An account with that email already exists.") from exc
        raise

    return dict(rows[0])


def login_user(email: str, password: str) -> dict[str, Any] | None:
    """Authenticate a user, issue a database-backed session token, and return the session user."""
    normalized_email = _normalize_email(email)
    user_rows = run_query(
        """
        SELECT user_id, email, password_hash, created_at
        FROM users
        WHERE email = %s
        LIMIT 1
        """,
        (normalized_email,),
        fetch=True,
    )

    if not user_rows:
        return None

    user = user_rows[0]
    if not verify_password(password, user["password_hash"]):
        return None

    session_token = secrets.token_hex(32)
    session_expires_at = datetime.utcnow() + timedelta(days=7)
    session_rows = run_query(
        """
        UPDATE users
        SET session_token = %s,
            session_expires_at = %s
        WHERE user_id = %s
        RETURNING user_id, email, session_token, session_expires_at, created_at
        """,
        (session_token, session_expires_at, user["user_id"]),
        fetch=True,
    )

    return dict(session_rows[0])


def get_current_user() -> dict[str, Any] | None:
    """Validate the active session token against the database and return the current user."""
    session_token = st.session_state.get("session_token")
    if not session_token:
        return None

    user = _get_user_by_token(session_token)
    if user is None:
        _clear_session_state()
        _remove_query_param_token()
        return None

    return user


def logout_user() -> None:
    """Invalidate the current session token in both the database and Streamlit."""
    session_token = st.session_state.get("session_token")
    if session_token:
        try:
            run_query(
                """
                UPDATE users
                SET session_token = NULL,
                    session_expires_at = NULL
                WHERE session_token = %s
                """,
                (session_token,),
                fetch=False,
            )
        except RuntimeError:
            pass

    _clear_session_state()
    _remove_query_param_token()


def require_auth() -> dict[str, Any]:
    """Redirect unauthenticated users to the login page and halt execution."""
    try:
        if not st.session_state.get("session_token"):
            query_token = _get_query_param_token()
            if query_token:
                restored_user = _get_user_by_token(query_token)
                if restored_user is not None:
                    st.session_state["session_token"] = query_token
                else:
                    _remove_query_param_token()

        user = get_current_user()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if user is None:
        st.session_state["page"] = "login"
        st.session_state.pop("_user", None)
        st.rerun()
        st.stop()

    st.query_params["token"] = st.session_state["session_token"]
    return user
