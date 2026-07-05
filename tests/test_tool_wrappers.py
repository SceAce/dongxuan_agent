import importlib


def test_root_chart_wrappers_import_after_cli_package_move():
    assert importlib.import_module("tools_bazi_chart_wrapper").main
    assert importlib.import_module("tools_liuyao_chart_wrapper").main
