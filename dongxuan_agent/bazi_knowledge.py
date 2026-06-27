from __future__ import annotations

from pathlib import Path


WIKI_ROOT = Path("/home/source/Documents/东玄知识库/wiki")


def build_bazi_knowledge_context() -> dict:
    return {
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
                "path": str(WIKI_ROOT / "topics" / "八字.md"),
                "role": "原局、大运、流年、强弱、调候、格局、病药的总纲入口。",
                "key_points": ["先体后用", "先强弱后取象", "先三层后结论"],
            },
            {
                "name": "八字-象法",
                "path": str(WIKI_ROOT / "structured" / "bazi_symbolic_layers.json"),
                "role": "五行、十神、宫位、格局与现代落点的结构化象义入口。",
                "key_points": ["传统象", "中间画像", "现代落点"],
            },
            {
                "name": "八字-案例总览",
                "path": str(WIKI_ROOT / "topics" / "八字.md"),
                "role": "禄命派案例总览入口，后续可拆分为单独案例页。",
                "key_points": ["千里命稿", "三命通会", "滴天髓", "四柱古籍经典合集"],
            },
        ],
        "source_status": {
            "symbolic_layers": str(WIKI_ROOT / "structured" / "bazi_symbolic_layers.json"),
            "topic_page": str(WIKI_ROOT / "topics" / "八字.md"),
        },
    }

