import importlib
import subprocess
import sys


def test_daliuren_package_public_exports_are_lazy():
    script = """
import sys
import dongxuan_agent.daliuren
print('dongxuan_agent.daliuren.chart' in sys.modules)
print('dongxuan_agent.daliuren.divination' in sys.modules)
from dongxuan_agent.daliuren import build_chart, build_divination, DaliurenChart, DaliurenDivination
print(callable(build_chart), callable(build_divination), DaliurenChart.__name__, DaliurenDivination.__name__)
"""

    result = subprocess.run([sys.executable, "-c", script], check=True, capture_output=True, text=True)

    assert result.stdout.splitlines() == [
        "False",
        "False",
        "True True DaliurenChart DaliurenDivination",
    ]


def test_root_chart_wrappers_import_after_cli_package_move():
    assert importlib.import_module("tools_bazi_chart_wrapper").main
    assert importlib.import_module("tools_liuyao_chart_wrapper").main
    assert importlib.import_module("tools_daliuren_chart_wrapper").main
