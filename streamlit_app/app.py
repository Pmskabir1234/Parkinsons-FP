"""
Full-Stack Dev Experience Simulator — Streamlit UI (Django API backend).
"""
import time
from typing import Any, Dict, Optional

import streamlit as st

from api_client import (
    dashboard as api_dashboard,
    get_challenge,
    list_challenges,
    login as api_login,
    public_meta,
    refresh_token,
    register as api_register,
    submit_challenge,
)

st.set_page_config(
    page_title="Dev Experience Simulator",
    page_icon="👾",
    layout="wide",
)


def _init_session() -> None:
    defaults = {
        "access_token": None,
        "refresh_token": None,
        "username": None,
        "page": "dashboard",
        "challenge_id": None,
        "timer_start": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _ensure_access() -> Optional[str]:
    access = st.session_state.access_token
    if not access:
        return None
    return access


def _try_refresh() -> bool:
    ref = st.session_state.refresh_token
    if not ref:
        return False
    try:
        data = refresh_token(ref)
        st.session_state.access_token = data.get("access")
        if data.get("refresh"):
            st.session_state.refresh_token = data["refresh"]
        return True
    except Exception:
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.username = None
        return False


def _request_with_refresh(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        if _try_refresh():
            return fn(*args, **kwargs)
        raise


def render_auth() -> None:
    st.title("Dev Experience Simulator")
    st.caption("Fix bugs, ship code, survive realistic scenarios — timed, validated, tracked.")
    try:
        meta = public_meta()
        st.info(
            f"MVP catalog: **{meta.get('total', 0)}** challenges across "
            f"bug fixes, coding tasks, and dev scenarios."
        )
    except Exception as exc:
        st.warning(f"API unreachable ({exc}). Start Django: `python manage.py runserver`.")
    tab_login, tab_reg = st.tabs(["Log in", "Register"])
    with tab_login:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Log in", type="primary"):
            try:
                data = api_login(u, p)
                st.session_state.access_token = data.get("access")
                st.session_state.refresh_token = data.get("refresh")
                st.session_state.username = u
                st.session_state.page = "dashboard"
                st.rerun()
            except Exception as exc:
                st.error(f"Login failed: {exc}")
    with tab_reg:
        u2 = st.text_input("Username", key="reg_u")
        e2 = st.text_input("Email (optional)", key="reg_e")
        p2 = st.text_input("Password (min 8 chars)", type="password", key="reg_p")
        if st.button("Create account"):
            try:
                api_register(u2, p2, e2)
                data = api_login(u2, p2)
                st.session_state.access_token = data.get("access")
                st.session_state.refresh_token = data.get("refresh")
                st.session_state.username = u2
                st.session_state.page = "dashboard"
                st.rerun()
            except Exception as exc:
                st.error(f"Registration failed: {exc}")


def render_dashboard(access: str) -> None:
    st.subheader("Dashboard")
    try:
        data = _request_with_refresh(api_dashboard, access)
    except Exception as exc:
        st.error(f"Could not load dashboard: {exc}")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Points", data.get("total_points", 0))
    c2.metric("Current streak", data.get("current_streak", 0))
    c3.metric("Best streak", data.get("longest_streak", 0))
    done = data.get("challenges_completed", 0)
    total = data.get("challenges_total", 0)
    c4.metric("Challenges completed", f"{done} / {total}")
    st.divider()
    st.markdown("**Per-challenge progress**")
    rows = data.get("progress") or []
    if not rows:
        st.caption("No attempts yet — open **Challenges** and submit your first solution.")
    else:
        for row in rows:
            status = "✅" if row.get("completed") else "⏳"
            bt = row.get("best_time_seconds")
            bt_s = f"{bt:.1f}s" if bt is not None else "—"
            st.write(
                f"{status} **{row.get('challenge_title')}** "
                f"({row.get('category')}) — attempts: {row.get('attempts')}, best: {bt_s}"
            )


def render_challenge_list(access: str) -> None:
    st.subheader("Challenges")
    try:
        items = _request_with_refresh(list_challenges, access)
    except Exception as exc:
        st.error(f"Could not list challenges: {exc}")
        return
    labels = {
        "bug_fix": "Bug fix",
        "code_challenge": "Code challenge",
        "dev_scenario": "Dev scenario",
    }
    for ch in items:
        cat = labels.get(ch.get("category"), ch.get("category"))
        with st.expander(f"[{cat}] {ch.get('title')}", expanded=False):
            st.markdown(ch.get("description", ""))
            if st.button("Open", key=f"open_{ch.get('id')}"):
                st.session_state.page = "challenge"
                st.session_state.challenge_id = ch.get("id")
                st.session_state.timer_start = None
                st.rerun()


def _reset_timer_for_challenge(cid: int) -> None:
    if st.session_state.get("timer_challenge_id") != cid:
        st.session_state.timer_challenge_id = cid
        st.session_state.timer_start = time.monotonic()


def render_challenge_workspace(access: str) -> None:
    cid = st.session_state.challenge_id
    if not cid:
        st.session_state.page = "challenges"
        st.rerun()
        return
    try:
        ch: Dict[str, Any] = _request_with_refresh(get_challenge, access, int(cid))
    except Exception as exc:
        st.error(f"Could not load challenge: {exc}")
        return
    _reset_timer_for_challenge(int(cid))
    limit = float(ch.get("time_limit_seconds") or 300)
    elapsed = time.monotonic() - float(st.session_state.timer_start)
    remaining = max(0.0, limit - elapsed)
    pv = ch.get("public_validator") or {}
    kind = pv.get("kind")

    st.markdown(f"## {ch.get('title')}")
    st.caption(f"Category: `{ch.get('category')}` · Points: **{ch.get('points')}** · Limit: **{int(limit)}s**")
    t1, t2 = st.columns([3, 1])
    with t1:
        st.progress(min(1.0, elapsed / limit) if limit > 0 else 0.0)
    with t2:
        st.metric("Time left", f"{remaining:.0f}s" if remaining > 0 else "0s (over)")
    st.markdown(ch.get("description", ""))

    payload_base = {"time_elapsed_seconds": min(elapsed, limit + 1.0)}

    if kind == "python_io":
        sk = f"code_{int(cid)}"
        if sk not in st.session_state:
            st.session_state[sk] = ch.get("starter_code") or ""
        code = st.text_area("Your code", height=320, key=sk)
        if st.button("Submit solution", type="primary"):
            if elapsed > limit:
                st.error("Time limit exceeded — reset the timer from the list or pick the challenge again.")
            else:
                res = submit_challenge(
                    access,
                    int(cid),
                    {**payload_base, "code": code},
                )
                _show_submit_result(res)

    elif kind == "mcq":
        prompt = pv.get("prompt") or "Choose the best answer."
        st.markdown(f"**{prompt}**")
        options = pv.get("options") or []
        choice = st.radio("Options", list(range(len(options))), format_func=lambda i: options[i])
        if st.button("Submit answer", type="primary"):
            if elapsed > limit:
                st.error("Time limit exceeded.")
            else:
                res = submit_challenge(
                    access,
                    int(cid),
                    {**payload_base, "choice_index": int(choice)},
                )
                _show_submit_result(res)
    elif kind == "text_match":
        ans = st.text_input(pv.get("prompt") or "Your answer")
        if st.button("Submit", type="primary"):
            if elapsed > limit:
                st.error("Time limit exceeded.")
            else:
                res = submit_challenge(
                    access,
                    int(cid),
                    {**payload_base, "answer": ans},
                )
                _show_submit_result(res)
    else:
        st.warning("Unsupported challenge type in this MVP client.")

    if st.button("← Back to list"):
        st.session_state.page = "challenges"
        st.session_state.challenge_id = None
        st.rerun()


def _show_submit_result(res: Dict[str, Any]) -> None:
    if res.get("ok"):
        st.success(res.get("message") or "Success.")
        st.balloons()
    else:
        st.error(res.get("message") or res.get("detail") or "Incorrect.")
    st.json(
        {
            k: res.get(k)
            for k in (
                "completed",
                "attempts",
                "best_time_seconds",
                "total_points",
                "current_streak",
                "longest_streak",
            )
            if k in res
        }
    )


def main() -> None:
    _init_session()
    access = _ensure_access()
    if not access:
        render_auth()
        return
    with st.sidebar:
        st.markdown(f"Signed in as **{st.session_state.username}**")
        if st.button("Log out"):
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.username = None
            st.session_state.page = "dashboard"
            st.rerun()
        st.divider()
        idx = 0
        if st.session_state.page in ("challenges", "challenge"):
            idx = 1
        nav = st.radio(
            "Navigate",
            ("Dashboard", "Challenges"),
            index=idx,
        )
        if nav == "Dashboard":
            st.session_state.page = "dashboard"
        else:
            st.session_state.page = "challenges"

    if st.session_state.page == "challenge":
        render_challenge_workspace(access)
        return

    if st.session_state.page == "dashboard":
        render_dashboard(access)
    else:
        render_challenge_list(access)


main()
