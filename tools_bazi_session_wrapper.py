#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parent / "daliuren_agent"
sys.path.insert(0, str(TOOL_ROOT))

from bazi_session import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
