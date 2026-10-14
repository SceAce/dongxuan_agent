from __future__ import annotations

from pathlib import Path

from ..core.knowledge import read_knowledge_json, relative_source, resolve_knowledge_location

SYMBOLIC_LAYERS_SOURCE = Path("structured/bazi_symbolic_layers.json")
TOPIC_SOURCE = Path("topics/八字.md")

REQUIRED_SYMBOLIC_SECTIONS = (
    "traditional_symbols",
    "middle_images",
    "modern_landing_rules",
    "imagery_runtime",
    "discipline_runtime",
)


def load_bazi_symbolic_layers() -> tuple[dict, str, str]:
    location = resolve_knowledge_location()
    source = relative_source(location.root / SYMBOLIC_LAYERS_SOURCE, location.root)
    if location.status != "available":
        return {}, location.status, source
    data, status = read_knowledge_json(location.root / SYMBOLIC_LAYERS_SOURCE)
    if status != "available":
        return {}, status, source
    if not _valid_symbolic_layers(data):
        return {}, "invalid", source
    return data, status, source


def _valid_symbolic_layers(data: dict) -> bool:
    if data.get("schema_version") != 2:
        return False
    return all(key in data and isinstance(data[key], (dict, list)) for key in REQUIRED_SYMBOLIC_SECTIONS)


def build_bazi_knowledge_context() -> dict:
    location = resolve_knowledge_location()
    _, symbolic_status, _ = load_bazi_symbolic_layers()
    return {
        "availability": {
            "status": symbolic_status,
            "source": location.source,
        },
        "layer_priority": ["理法", "象法", "案例"],
        "book_sets": {
            "principle": [
                "《子平真诠》本义 / 徐伟刚《子平真诠》评注",
                "《三命通会》",
                "《滴天髓》及任铁樵注",
                "《千里命稿》",
                "《四柱八字基础知识大全》",
                "《四柱八字基础应用》",
            ],
            "symbolic": [
                "《五行大义·渊海子平》",
                "《滴天髓》",
                "《子平真诠》",
                "《八字之门》",
                "现有 bazi_symbolic_layers.json",
            ],
            "cases": [
                "《千里命稿》实断",
                "《三命通会》命例",
                "《滴天髓》注解案例",
                "《四柱古籍经典合集》中的可归属子平/禄命实断",
                "《四柱八字基础应用》与《四柱八字基础知识大全》的现代案例",
            ],
        },
        "case_policy": {
            "prefer": "禄命派",
            "avoid": "默认案例层不使用盲派材料作为主案例。",
            "fallback": "只有在没有足够禄命派案例时，才把其他材料作为旁证，不作为默认案例层。",
        },
        "topic_pages": [
            {
                "name": "八字-理法",
                "source": relative_source(location.root / TOPIC_SOURCE, location.root),
                "role": "原局、大运、流年、强弱、调候、格局、病药的总纲入口。",
                "key_points": ["先体后用", "先强弱后取象", "先三层后结论"],
            },
            {
                "name": "八字-象法",
                "source": relative_source(location.root / SYMBOLIC_LAYERS_SOURCE, location.root),
                "role": "五行、十神、宫位、格局与现代落点的结构化象义入口。",
                "key_points": ["传统象", "中间画像", "现代落点"],
            },
            {
                "name": "八字-案例总览",
                "source": relative_source(location.root / TOPIC_SOURCE, location.root),
                "role": "禄命派案例总览入口，后续可拆分为单独案例页。",
                "key_points": ["千里命稿", "三命通会", "滴天髓", "四柱古籍经典合集"],
            },
        ],
        "source_status": {
            "symbolic_layers": {
                "source": relative_source(location.root / SYMBOLIC_LAYERS_SOURCE, location.root),
                "status": symbolic_status,
            },
            "topic_page": {
                "source": relative_source(location.root / TOPIC_SOURCE, location.root),
                "status": "available" if (location.root / TOPIC_SOURCE).is_file() else "missing",
            },
        },
    }
