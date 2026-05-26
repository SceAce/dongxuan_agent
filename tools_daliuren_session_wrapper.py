#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parent / "daliuren_agent"
SITE_PACKAGES = Path("/home/source/Tmp/dongxuan_agent/.venv/lib/python3.14/site-packages")
if SITE_PACKAGES.exists():
    sys.path.insert(0, str(SITE_PACKAGES))
sys.path.insert(0, str(TOOL_ROOT))

from daliuren_session import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
