import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, Tuple

_PYTHON = sys.executable


def _normalize(s: str, mode: str) -> str:
    s = s.strip()
    if mode == "lower_strip":
        return s.lower()
    if mode == "collapse_ws":
        return re.sub(r"\s+", " ", s.lower().strip())
    return s


def validate_submission(validator: Dict[str, Any], payload: Dict[str, Any]) -> Tuple[bool, str]:
    kind = validator.get("kind")
    if kind == "python_io":
        code = (payload.get("code") or "").strip()
        if not code:
            return False, "Submit your code."
        tests = validator.get("tests") or []
        return _run_python_io_tests(code, tests)
    if kind == "mcq":
        correct = int(validator.get("correct_index", -1))
        chosen = payload.get("choice_index")
        if chosen is None:
            return False, "Select an option."
        try:
            chosen = int(chosen)
        except (TypeError, ValueError):
            return False, "Invalid selection."
        if chosen == correct:
            return True, "Correct."
        return False, "Not quite — review the scenario and try again."
    if kind == "text_match":
        raw = (payload.get("answer") or "").strip()
        expected = validator.get("answer", "")
        norm = validator.get("normalize", "strip")
        got = _normalize(raw, norm)
        exp = _normalize(expected, norm)
        if got == exp:
            return True, "Correct."
        return False, "Answer does not match the expected response."
    return False, f"Unknown validator kind: {kind!r}"


def _run_python_io_tests(code: str, tests: list) -> Tuple[bool, str]:
    for i, t in enumerate(tests):
        stdin = t.get("stdin", "")
        expected_out = t.get("expected_stdout", "")
        ok, msg = _run_one_python_snippet(code, stdin, expected_out)
        if not ok:
            return False, f"Test {i + 1}: {msg}"
    return True, "All tests passed."


def _run_one_python_snippet(code: str, stdin: str, expected_stdout: str) -> Tuple[bool, str]:
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".py", text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)
        proc = subprocess.run(
            [_PYTHON, tmp],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=8,
            cwd=os.path.dirname(tmp) or None,
        )
    except subprocess.TimeoutExpired:
        return False, "Timed out (code took too long)."
    except Exception as exc:
        return False, str(exc)
    finally:
        if tmp and os.path.isfile(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()[:500]
        return False, f"Runtime error: {err or proc.returncode}"

    out = proc.stdout or ""
    exp = expected_stdout.replace("\r\n", "\n")
    got = out.replace("\r\n", "\n")
    if got.strip() != exp.strip():
        return False, f"Expected stdout {exp!r}, got {got!r}"
    return True, "ok"
