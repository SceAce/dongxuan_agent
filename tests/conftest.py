from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_knowledge_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    root = tmp_path / "missing-knowledge"
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))
    return root


@pytest.fixture
def available_knowledge_root(
    isolated_knowledge_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Path:
    root = tmp_path / "wiki"
    structured = root / "structured"
    entities = root / "entities"
    structured.mkdir(parents=True)
    entities.mkdir(parents=True)

    payload = {
        "traditional_symbols": [
            {"name": name, "kind": kind, "sources": ["test fixture"]}
            for name, kind in {
                "食神": "十神",
                "正印": "十神",
                "正官": "十神",
                "正财": "十神",
                "劫财": "十神",
                "年柱": "宫位",
                "月柱": "宫位",
                "日支": "宫位",
                "食神格": "格局",
                "子午冲": "干支作用",
            }.items()
        ],
        "middle_images": [
            {"name": name}
            for name in (
                "信息处理",
                "技能输出",
                "工程系统",
                "规则训练",
                "资源经营",
                "文本表达",
                "制度法理",
                "教育训练",
                "公共传播",
                "人文研究",
            )
        ],
        "modern_landing_rules": [
            {
                "name": "软件工程",
                "requires_all": ["信息处理", "技能输出"],
                "prefers_any": ["工程系统", "规则训练"],
                "excludes_if": ["纯资源经营强于技能输出", "信息处理无力且无项目输出"],
            },
            {
                "name": "电气工程",
                "requires_all": ["工程系统", "规则训练"],
                "prefers_any": ["火象显化", "控制系统", "器械设备"],
                "excludes_if": ["火弱受制且信息处理明显强于控制设备象"],
            },
            {
                "name": "信息管理",
                "requires_all": ["信息处理", "资源经营"],
                "prefers_any": ["规则训练", "平台体系"],
                "excludes_if": ["资源经营无力且技能输出明显强于管理象"],
            },
            {
                "name": "汉语言文学",
                "requires_all": ["文本表达", "人文研究"],
                "prefers_any": ["技能输出", "规则训练"],
                "excludes_if": ["文本表达弱于工程系统", "人文研究缺少印星承载"],
            },
            {
                "name": "法学",
                "requires_all": ["制度法理", "规则训练"],
                "prefers_any": ["文本表达", "工程系统"],
                "excludes_if": ["制度法理无印承载", "规则训练弱于技术项目输出"],
            },
            {
                "name": "教育学",
                "requires_all": ["教育训练", "规则训练"],
                "prefers_any": ["文本表达", "人文研究"],
                "excludes_if": ["教育训练缺少印食配合", "表达输出弱于工程项目训练"],
            },
            {
                "name": "新闻传播学",
                "requires_all": ["公共传播", "文本表达"],
                "prefers_any": ["信息处理", "资源经营"],
                "excludes_if": ["公共传播缺少财星外显或受众连接", "表达输出被重扰"],
            },
        ],
    }
    (structured / "bazi_symbolic_layers.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    for term in ("五行", "十神", "旺衰", "干支"):
        (entities / f"{term}.md").write_text(
            f"# {term}\n\n这是测试用的最小知识条目。",
            encoding="utf-8",
        )

    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))
    return root
