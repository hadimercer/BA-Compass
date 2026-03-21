"""Shared styling and layout helpers for the BA Compass Streamlit interface."""

from __future__ import annotations

import streamlit as st

from components.auth import logout_user


def inject_css(hide_sidebar: bool = False) -> None:
    """Inject the global BA Compass dark theme and component styling.

    Args:
        hide_sidebar: When True, hides the sidebar entirely (for login/register pages).
    """
    st.markdown(
        """
        <style>
            :root {
                --bg: #0F1117;
                --surface: #1A1F2E;
                --card: #1E2538;
                --border: #2D3550;
                --accent: #2E75B6;
                --accent-lt: #4A9FD4;
                --text: #F0F4F8;
                --text-secondary: #8B9CBD;
                --success: #10B981;
                --warning: #F59E0B;
                --danger: #EF4444;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(74, 159, 212, 0.18), transparent 34%),
                    linear-gradient(180deg, #0C1019 0%, var(--bg) 55%, #0D1421 100%);
                color: var(--text);
            }

            .main .block-container {
                padding-top: 0 !important;
                padding-bottom: 1rem !important;
                max-width: 100% !important;
            }

            .block-container {
                padding-top: 0 !important;
            }

            header[data-testid="stHeader"] {
                display: none !important;
                height: 0 !important;
                min-height: 0 !important;
            }

            div[data-testid="stToolbar"] {
                display: none !important;
            }

            div[data-testid="stDecoration"] {
                display: none !important;
            }

            div[data-testid="stStatusWidget"] {
                display: none !important;
            }

            section[data-testid="stSidebar"] {
                display: flex !important;
                transform: none !important;
                min-width: 244px !important;
                max-width: 244px !important;
                background: linear-gradient(180deg, rgba(26, 31, 46, 0.98) 0%, rgba(15, 17, 23, 0.98) 100%);
                border-right: 1px solid rgba(45, 53, 80, 0.9);
            }

            [data-testid="collapsedControl"] {
                display: none !important;
            }

            /* Hide Streamlit auto-generated pages navigation list.
               Descendant combinator ensures we only match nav content
               INSIDE the sidebar, never the sidebar element itself. */
            section[data-testid="stSidebar"] [data-testid="stSidebarNav"],
            section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
            section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
                display: none !important;
            }

            div[data-testid="stForm"],
            div[data-testid="stExpander"] {
                border: 1px solid rgba(45, 53, 80, 0.9);
                background: rgba(30, 37, 56, 0.82);
                border-radius: 18px;
                box-shadow: 0 22px 48px rgba(0, 0, 0, 0.22);
            }

            div[data-testid="stForm"] {
                padding: 0.35rem 0.5rem 0.75rem;
            }

            div[data-testid="stTextInput"] label,
            div[data-testid="stTextArea"] label,
            div[data-testid="stExpander"] summary {
                color: var(--text);
            }

            div[data-testid="stTextInput"] input,
            div[data-testid="stTextArea"] textarea {
                background: rgba(15, 17, 23, 0.72);
                color: var(--text);
                border: 1px solid var(--border);
                border-radius: 12px;
            }

            div[data-testid="stTextInput"] input:focus,
            div[data-testid="stTextArea"] textarea:focus {
                border-color: var(--accent-lt);
                box-shadow: 0 0 0 1px var(--accent-lt);
            }

            div.stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                width: 100%;
                border-radius: 12px;
                border: 1px solid rgba(74, 159, 212, 0.55);
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-lt) 100%);
                color: white;
                font-weight: 600;
                padding: 0.7rem 1rem;
                box-shadow: 0 14px 30px rgba(46, 117, 182, 0.25);
            }

            div.stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                border-color: rgba(74, 159, 212, 0.85);
                filter: brightness(1.04);
            }

            .auth-shell {
                display: block;
                padding-top: 1.5rem;
            }

            .auth-card {
                background: linear-gradient(180deg, rgba(30, 37, 56, 0.95) 0%, rgba(22, 29, 43, 0.92) 100%);
                border: 1px solid rgba(74, 159, 212, 0.22);
                border-radius: 24px;
                padding: 2rem;
                box-shadow: 0 26px 60px rgba(0, 0, 0, 0.35);
            }

            .auth-kicker {
                display: inline-block;
                padding: 0.35rem 0.7rem;
                border-radius: 999px;
                font-size: 0.78rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: var(--accent-lt);
                background: rgba(46, 117, 182, 0.16);
                border: 1px solid rgba(74, 159, 212, 0.2);
                margin-bottom: 1rem;
            }

            .auth-title {
                font-size: 2rem;
                font-weight: 700;
                color: var(--text);
                margin-bottom: 0.35rem;
            }

            .auth-subtitle,
            .auth-link-copy,
            .muted-copy {
                color: var(--text-secondary);
            }

            .page-header {
                background: linear-gradient(135deg, rgba(30, 37, 56, 0.9) 0%, rgba(26, 31, 46, 0.78) 100%);
                border: 1px solid rgba(45, 53, 80, 0.95);
                border-radius: 22px;
                padding: 1.4rem 1.5rem;
                margin-bottom: 1.25rem;
                box-shadow: 0 18px 38px rgba(0, 0, 0, 0.18);
            }

            .page-title {
                font-size: 1.9rem;
                font-weight: 700;
                color: var(--text);
                margin-bottom: 0.2rem;
            }

            .sidebar-brand {
                padding: 0.9rem 0 1.2rem;
            }

            .sidebar-kicker {
                color: var(--accent-lt);
                font-size: 0.72rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.4rem;
            }

            .sidebar-title {
                color: var(--text);
                font-size: 1.2rem;
                font-weight: 700;
            }

            .sidebar-link {
                padding: 0.72rem 0.85rem;
                border: 1px solid transparent;
                border-radius: 14px;
                margin-bottom: 0.5rem;
                color: var(--text-secondary);
                background: rgba(255, 255, 255, 0.02);
            }

            .sidebar-link.active {
                color: var(--text);
                background: rgba(46, 117, 182, 0.16);
                border-color: rgba(74, 159, 212, 0.35);
            }

            .sidebar-link.disabled {
                opacity: 0.62;
            }

            .dashboard-card {
                height: 240px;
                background: linear-gradient(180deg, rgba(30, 37, 56, 0.92) 0%, rgba(22, 29, 43, 0.92) 100%);
                border: 1px solid rgba(45, 53, 80, 0.95);
                border-radius: 20px;
                padding: 1.15rem;
                box-shadow: 0 18px 36px rgba(0, 0, 0, 0.18);
                margin-bottom: 1rem;
                overflow: hidden;
            }

            .dashboard-card h3 {
                color: var(--text);
                font-size: 1.1rem;
                margin-bottom: 0.75rem;
            }

            .card-meta {
                color: var(--text-secondary);
                font-size: 0.92rem;
                margin-bottom: 0.4rem;
            }

            .status-badge {
                display: inline-block;
                padding: 0.3rem 0.65rem;
                border-radius: 999px;
                font-size: 0.8rem;
                font-weight: 600;
                margin: 0.55rem 0 0.8rem;
                border: 1px solid transparent;
            }

            .status-badge.active,
            .status-badge.complete {
                background: rgba(16, 185, 129, 0.14);
                color: #A7F3D0;
                border-color: rgba(16, 185, 129, 0.35);
            }

            .status-badge.in-progress {
                background: rgba(46, 117, 182, 0.14);
                color: #B9DEFF;
                border-color: rgba(74, 159, 212, 0.32);
            }

            .status-badge.skipped,
            .status-badge.warning {
                background: rgba(245, 158, 11, 0.14);
                color: #FCD34D;
                border-color: rgba(245, 158, 11, 0.3);
            }

            .status-badge.not-started,
            .status-badge.default {
                background: rgba(139, 156, 189, 0.16);
                color: var(--text-secondary);
                border-color: rgba(139, 156, 189, 0.25);
            }

            .empty-state {
                text-align: center;
                padding: 3.25rem 1.5rem;
                background: linear-gradient(180deg, rgba(30, 37, 56, 0.86) 0%, rgba(20, 26, 39, 0.9) 100%);
                border: 1px dashed rgba(74, 159, 212, 0.28);
                border-radius: 24px;
                margin: 1rem 0 1.25rem;
            }

            .empty-state h2 {
                color: var(--text);
                margin-bottom: 0.55rem;
            }

            .empty-state p {
                color: var(--text-secondary);
                max-width: 620px;
                margin: 0 auto;
                line-height: 1.65;
            }

            div[data-testid="stToolbar"] {
                display: none !important;
            }

            .ka-header {
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.09em;
                text-transform: uppercase;
                color: var(--accent-lt);
                padding: 0.55rem 0 0.45rem;
                border-bottom: 1px solid rgba(45, 53, 80, 0.7);
                margin-bottom: 0.75rem;
                margin-top: 0.5rem;
            }

            .module-card {
                background: linear-gradient(180deg, rgba(30,37,56,0.92) 0%, rgba(22,29,43,0.92) 100%);
                border: 1px solid rgba(45,53,80,0.95);
                border-radius: 16px;
                padding: 1rem 1.1rem 0.85rem;
                margin-bottom: 0.55rem;
                height: 148px;
                overflow: hidden;
            }

            .module-card:hover {
                border-color: rgba(74,159,212,0.3);
            }

            .module-card-name {
                font-size: 0.92rem;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 0.35rem;
                line-height: 1.35;
            }

            .module-card-desc {
                font-size: 0.78rem;
                color: var(--text-secondary);
                line-height: 1.5;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }

            .m-badge {
                display: inline-block;
                font-size: 0.7rem;
                font-weight: 600;
                padding: 0.18rem 0.55rem;
                border-radius: 999px;
                margin-bottom: 0.45rem;
            }

            .m-badge-not-started  { background:rgba(139,156,189,0.16); color:#8B9CBD; border:1px solid rgba(139,156,189,0.25); }
            .m-badge-in-progress  { background:rgba(46,117,182,0.18);  color:#B9DEFF; border:1px solid rgba(74,159,212,0.32); }
            .m-badge-complete     { background:rgba(16,185,129,0.14);  color:#A7F3D0; border:1px solid rgba(16,185,129,0.35); }
            .m-badge-skipped      { background:rgba(245,158,11,0.14);  color:#FCD34D; border:1px solid rgba(245,158,11,0.3);  }

            .progress-track {
                background: rgba(255,255,255,0.08);
                border-radius: 999px;
                height: 7px;
                margin: 0.5rem 0 0.25rem;
            }

            .progress-fill {
                background: linear-gradient(90deg, var(--accent) 0%, var(--accent-lt) 100%);
                border-radius: 999px;
                height: 7px;
                transition: width 0.4s ease;
            }

            .project-meta-row {
                display: flex;
                gap: 0.6rem;
                flex-wrap: wrap;
                margin-top: 0.5rem;
            }

            .project-meta-pill {
                font-size: 0.78rem;
                color: var(--text-secondary);
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(45,53,80,0.8);
                border-radius: 999px;
                padding: 0.2rem 0.65rem;
            }

            section[data-testid="stSidebar"] div.stButton > button {
                background: transparent !important;
                border: 1px solid transparent !important;
                box-shadow: none !important;
                color: var(--text-secondary) !important;
                font-weight: 400 !important;
                padding: 0.72rem 0.85rem !important;
                border-radius: 14px !important;
                text-align: left !important;
                justify-content: flex-start !important;
                margin-bottom: 0.3rem;
            }

            section[data-testid="stSidebar"] div.stButton > button:hover {
                background: rgba(255, 255, 255, 0.04) !important;
                border-color: rgba(74, 159, 212, 0.25) !important;
                color: var(--text) !important;
            }

            /* ── Selectbox ─────────────────────────────────────────────────── */

            div[data-testid="stSelectbox"] label {
                color: var(--text);
            }

            div[data-testid="stSelectbox"] > div > div {
                background: rgba(15, 17, 23, 0.72) !important;
                border: 1px solid var(--border) !important;
                border-radius: 12px !important;
                color: var(--text) !important;
            }

            div[data-testid="stSelectbox"] > div > div:focus-within {
                border-color: var(--accent-lt) !important;
                box-shadow: 0 0 0 1px var(--accent-lt) !important;
            }

            div[data-testid="stSelectbox"] svg {
                fill: var(--text-secondary) !important;
            }

            /* ── Tabs ──────────────────────────────────────────────────────── */

            button[data-baseweb="tab"] {
                font-size: 1rem !important;
                font-weight: 600 !important;
                padding: 0.55rem 1.1rem !important;
                border-radius: 0.5rem 0.5rem 0 0 !important;
                color: var(--text-secondary) !important;
                background: transparent !important;
                border: 1px solid transparent !important;
            }

            button[data-baseweb="tab"][aria-selected="true"] {
                background: rgba(46, 117, 182, 0.22) !important;
                border: 1px solid rgba(74, 159, 212, 0.4) !important;
                border-bottom: none !important;
                color: var(--text) !important;
            }

            button[data-baseweb="tab"]:hover {
                color: var(--text) !important;
                background: rgba(255, 255, 255, 0.04) !important;
            }

            div[data-testid="stTabsContent"] {
                background: rgba(255, 255, 255, 0.025);
                border-radius: 0 0 0.6rem 0.6rem;
                padding: 1.2rem 1.5rem 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-top: none;
                margin-top: 0;
            }

            /* ── Download button ───────────────────────────────────────────── */

            div[data-testid="stDownloadButton"] > button {
                width: 100%;
                border-radius: 12px;
                border: 1px solid rgba(74, 159, 212, 0.55);
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-lt) 100%);
                color: white;
                font-weight: 600;
                padding: 0.7rem 1rem;
                box-shadow: 0 14px 30px rgba(46, 117, 182, 0.25);
            }

            div[data-testid="stDownloadButton"] > button:hover {
                border-color: rgba(74, 159, 212, 0.85);
                filter: brightness(1.04);
            }

            /* ── Metric ────────────────────────────────────────────────────── */

            div[data-testid="stMetric"] {
                background: rgba(30, 37, 56, 0.82);
                border: 1px solid rgba(45, 53, 80, 0.9);
                border-radius: 14px;
                padding: 0.8rem 1rem;
            }

            div[data-testid="stMetric"] label {
                color: var(--text-secondary) !important;
                font-size: 0.8rem !important;
            }

            div[data-testid="stMetricValue"] {
                color: var(--text) !important;
            }

            div[data-testid="stMetricDelta"] {
                color: var(--text-secondary) !important;
            }

            /* ── Chat bubbles ──────────────────────────────────────────────── */

            .chat-bubble-user {
                display: flex;
                justify-content: flex-end;
                margin-bottom: 0.75rem;
            }

            .chat-bubble-user > div {
                background: rgba(46, 117, 182, 0.22);
                border: 1px solid rgba(74, 159, 212, 0.3);
                border-radius: 14px 14px 4px 14px;
                padding: 0.75rem 1rem;
                max-width: 82%;
                color: #F0F4F8;
                font-size: 0.92rem;
                line-height: 1.6;
                white-space: pre-wrap;
            }

            .chat-bubble-ai {
                display: flex;
                justify-content: flex-start;
                margin-bottom: 0.75rem;
            }

            .chat-bubble-ai > div {
                background: rgba(30, 37, 56, 0.9);
                border: 1px solid rgba(45, 53, 80, 0.9);
                border-radius: 14px 14px 14px 4px;
                padding: 0.75rem 1rem;
                max-width: 82%;
                color: #F0F4F8;
                font-size: 0.92rem;
                line-height: 1.6;
                white-space: pre-wrap;
            }

            /* ── Info / success / error / warning overrides ────────────────── */

            div[data-testid="stAlert"] {
                border-radius: 12px;
                border-left-width: 3px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if hide_sidebar:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
                [data-testid="collapsedControl"] {
                    display: none !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )



def render_sidebar(current_page: str) -> None:
    """Render the BA Compass sidebar with current-page state and logout."""
    nav_items = [
        ("dashboard", "Dashboard"),
        ("divider", "divider"),
        ("intake", "Project Intake"),
        ("roadmap", "Roadmap"),
        ("module", "Co-Pilot"),
        ("gap_analysis", "Gap Analysis"),
        ("export", "Export"),
    ]

    # Expand this set as each page is fully implemented
    NAVIGABLE = {"dashboard", "intake", "roadmap", "module", "gap_analysis", "export"}

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-kicker">Business Analysis Co-Pilot</div>
                <div class="sidebar-title">BA Compass</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pid = st.session_state.get("active_project_id")
        if pid:
            pname = st.session_state.get("active_project_name", "Active Project")
            st.markdown(
                f"<div style='font-size:0.72rem;color:#4A9FD4;padding:0.3rem 0.7rem 0;"
                f"letter-spacing:0.05em;text-transform:uppercase;'>Current Project</div>"
                f"<div style='font-size:0.82rem;color:#F0F4F8;padding:0.1rem 0.7rem 0.65rem;"
                f"font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                f"max-width:200px;'>{pname}</div>",
                unsafe_allow_html=True,
            )

        for key, label in nav_items:
            if key == "divider":
                st.divider()
                continue

            if key == current_page:
                st.markdown(f"<div class='sidebar-link active'>{label}</div>", unsafe_allow_html=True)
            elif key in NAVIGABLE:
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.session_state["page"] = key
                    st.rerun()
            else:
                st.markdown(f"<div class='sidebar-link disabled'>{label}</div>", unsafe_allow_html=True)

        st.divider()
        if st.button("Log out", key="sidebar_logout", use_container_width=True):
            logout_user()
            st.session_state["page"] = "login"
            st.session_state.pop("_user", None)
            st.rerun()
            st.stop()


def render_page_header(title: str, subtitle: str = "") -> None:
    """Render a consistent page header block."""
    subtitle_markup = f"<p class='muted-copy'>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-title">{title}</div>
            {subtitle_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )
