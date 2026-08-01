#!/usr/bin/env python3
"""CI / local entry point for the foundation security test suite (SECMIG-P5-006).

Runs only tests marked ``@pytest.mark.security``. Does not change runtime
application behavior.

Usage (from ``backend/``)::

    python scripts/run_security_tests.py
    python scripts/run_security_tests.py -q

Equivalent::

    pytest -m security
"""

from __future__ import annotations

import sys

import pytest


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    return pytest.main(["-m", "security", *args])


if __name__ == "__main__":
    raise SystemExit(main())
