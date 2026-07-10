import importlib
import subprocess
import sys
from pathlib import Path


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


def test_root_tool_wrappers_delegate_to_canonical_modules():
    mappings = {
        "tools_bazi_chart_wrapper": "tools.bazi.chart_wrapper",
        "tools_bazi_session_wrapper": "tools.bazi.session_wrapper",
        "tools_daliuren_chart_wrapper": "tools.daliuren.chart_wrapper",
        "tools_daliuren_session_wrapper": "tools.daliuren.session_wrapper",
        "tools_liuyao_chart_wrapper": "tools.liuyao.chart_wrapper",
        "tools_liuyao_session_wrapper": "tools.liuyao.session_wrapper",
    }

    for root_module_name, canonical_module_name in mappings.items():
        root_module = importlib.import_module(root_module_name)
        canonical_module = importlib.import_module(canonical_module_name)

        assert root_module.main is canonical_module.main


def test_root_tool_wrappers_do_not_inject_legacy_tool_path():
    wrapper_paths = [
        "tools_bazi_chart_wrapper.py",
        "tools_bazi_session_wrapper.py",
        "tools_daliuren_chart_wrapper.py",
        "tools_daliuren_session_wrapper.py",
        "tools_liuyao_chart_wrapper.py",
        "tools_liuyao_session_wrapper.py",
    ]

    for wrapper_path in wrapper_paths:
        source = Path(wrapper_path).read_text()

        assert "daliuren_agent" not in source
        assert "sys.path" not in source
        assert "from pathlib import Path" not in source
