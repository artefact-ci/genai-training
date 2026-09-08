"""Check that a machine is ready for the labs.

Run this at the start of day one, before anything else:

    uv run python commun/setup/check_env.py

It reports every problem it finds rather than stopping at the first one, so a
participant can fix them in one pass.
"""

from __future__ import annotations

import sys

MIN_PYTHON = (3, 11)


def _check_python() -> str | None:
    if sys.version_info < MIN_PYTHON:
        current = ".".join(str(part) for part in sys.version_info[:3])
        wanted = ".".join(str(part) for part in MIN_PYTHON)
        return f"Python {wanted}+ is required, this interpreter is {current}."
    return None


def _check_imports() -> str | None:
    try:
        import commun.llm  # noqa: F401
    except ImportError:
        return (
            "Cannot import `commun.llm`. Run `uv sync` from the repository root, "
            "then run this script with `uv run`."
        )
    return None


def _check_settings() -> str | None:
    from commun.llm import ConfigurationError, get_settings

    try:
        get_settings()
    except ConfigurationError as exc:
        return str(exc)
    return None


def _check_model_call() -> str | None:
    from commun.llm import complete

    try:
        answer = complete(
            [{"role": "user", "content": "Réponds exactement: OK"}], max_tokens=10
        )
    except Exception as exc:  # noqa: BLE001 - we want to report anything that goes wrong
        return f"The model call failed: {type(exc).__name__}: {exc}"

    print(f"  model      : {answer.model}")
    print(f"  answer     : {answer.text.strip()!r}")
    print(f"  tokens     : {answer.total_tokens}")
    return None


def main() -> int:
    checks = (
        ("Python version", _check_python),
        ("Repository installed", _check_imports),
        ("Environment variables", _check_settings),
        ("Model reachable", _check_model_call),
    )

    failures: list[str] = []
    for label, check in checks:
        if failures:
            # Later checks depend on earlier ones; reporting them would be noise.
            print(f"[skip] {label}")
            continue
        problem = check()
        if problem:
            print(f"[fail] {label}\n       {problem}")
            failures.append(label)
        else:
            print(f"[ok]   {label}")

    if failures:
        print("\nEnvironment not ready. See commun/setup/README.md.")
        return 1

    print("\nEnvironment ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
