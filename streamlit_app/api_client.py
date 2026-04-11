import os
from typing import Any, Dict, Optional

import requests

DEFAULT_API = os.environ.get("DEV_SIM_API", "http://127.0.0.1:8000").rstrip("/")


def _headers(access: Optional[str] = None) -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if access:
        h["Authorization"] = f"Bearer {access}"
    return h


def register(username: str, password: str, email: str = "") -> Dict[str, Any]:
    r = requests.post(
        f"{DEFAULT_API}/api/auth/register/",
        json={"username": username, "password": password, "email": email},
        headers=_headers(),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def login(username: str, password: str) -> Dict[str, Any]:
    r = requests.post(
        f"{DEFAULT_API}/api/auth/token/",
        json={"username": username, "password": password},
        headers=_headers(),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def refresh_token(refresh: str) -> Dict[str, Any]:
    r = requests.post(
        f"{DEFAULT_API}/api/auth/token/refresh/",
        json={"refresh": refresh},
        headers=_headers(),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def me(access: str) -> Dict[str, Any]:
    r = requests.get(
        f"{DEFAULT_API}/api/auth/me/",
        headers=_headers(access),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def list_challenges(access: str) -> list:
    r = requests.get(
        f"{DEFAULT_API}/api/challenges/",
        headers=_headers(access),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def get_challenge(access: str, pk: int) -> Dict[str, Any]:
    r = requests.get(
        f"{DEFAULT_API}/api/challenges/{pk}/",
        headers=_headers(access),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def submit_challenge(access: str, pk: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(
        f"{DEFAULT_API}/api/challenges/{pk}/submit/",
        json=payload,
        headers=_headers(access),
        timeout=60,
    )
    return r.json()


def dashboard(access: str) -> Dict[str, Any]:
    r = requests.get(
        f"{DEFAULT_API}/api/dashboard/",
        headers=_headers(access),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def public_meta() -> Dict[str, Any]:
    r = requests.get(f"{DEFAULT_API}/api/meta/", timeout=15)
    r.raise_for_status()
    return r.json()
