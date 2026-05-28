from __future__ import annotations

from .chart import build_liuyao_chart


def build_liuyao_context(**kwargs) -> dict:
    return build_liuyao_chart(**kwargs).to_dict()
