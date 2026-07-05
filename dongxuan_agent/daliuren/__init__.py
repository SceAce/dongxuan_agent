from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chart import DaliurenChart, build_chart
    from .divination import DaliurenDivination, build_divination


__all__ = ["DaliurenChart", "DaliurenDivination", "build_chart", "build_divination"]

_EXPORTS = {
    "DaliurenChart": (".chart", "DaliurenChart"),
    "build_chart": (".chart", "build_chart"),
    "DaliurenDivination": (".divination", "DaliurenDivination"),
    "build_divination": (".divination", "build_divination"),
}


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = _EXPORTS[name]
    value = getattr(import_module(module_name, __name__), attribute_name)
    globals()[name] = value
    return value
