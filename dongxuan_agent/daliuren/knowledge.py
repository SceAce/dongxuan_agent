from __future__ import annotations

from pathlib import Path

from ..core.knowledge import relative_source, resolve_knowledge_location


MODERN_CASE_SOURCE = Path("sources/林烽-大六壬经典案例解析-clean.md")
MODERN_CASE_PAGE = Path("cases/daliuren/林烽-大六壬经典案例解析.md")


def build_daliuren_knowledge_context() -> dict:
    location = resolve_knowledge_location()
    root = location.root
    return {
        "availability": {
            "status": location.status,
            "source": location.source,
        },
        "layer_priority": ["理法", "象根", "案例"],
        "policy": "先理后象，案例只作类比和验例，不得越过课传结构直接定断。",
        "topic_pages": [
            {
                "name": "大六壬-理法",
                "source": relative_source(root / "topics" / "大六壬-理法.md", root),
                "role": "先定课体、四课、三传、旺衰、遁干、空亡与判断秩序。",
                "key_points": ["四课定结构", "三传看过程与归结", "旺衰空亡校正虚实", "象理合参边界"],
            },
            {
                "name": "大六壬-象根",
                "source": relative_source(root / "topics" / "大六壬-象根.md", root),
                "role": "解释十二天将、五行、十二支等象义来源与边界。",
                "key_points": ["象从何来", "象能延伸到哪里", "固定象义只能当词库"],
            },
            {
                "name": "大六壬-案例总览",
                "source": relative_source(root / "topics" / "大六壬-案例总览.md", root),
                "role": "提供古案、近代案、现代案的取象路径与验辞样本。",
                "key_points": ["邵彦和断案新编", "牧夫占验", "林烽现代案例", "案例只做类比"],
            },
        ],
        "principle_pages": [
            _page("课体与三传", Path("principles/daliuren/课体与三传.md"), "先看发用与三传归结，不先落固定象义。"),
            _page("四课与类神", Path("principles/daliuren/四课与类神.md"), "先定人我、主客、内外，再找类神落点。"),
            _page("旺衰空亡与遁干", Path("principles/daliuren/旺衰空亡与遁干.md"), "以力量、虚实、暗线和应期校正断语。"),
            _page("象理合参", Path("principles/daliuren/象理合参.md"), "象义只能解释理法已经成立的关系。"),
        ],
        "image_pages": [
            _page("十二天将象根", Path("images/daliuren/十二天将象根.md"), "把天将当成人事状态与角色来源，不当成结论本身。"),
            _page("五行与十二支本义", Path("images/daliuren/五行与十二支本义.md"), "保留五行、方位、时令、身体、场景的根义。"),
            _page("类象边界", Path("images/daliuren/类象边界.md"), "明确固定象义的使用边界，防止一象多断。"),
        ],
        "case_pages": [
            _page("邵彦和-断案新编", Path("cases/daliuren/邵彦和-断案新编.md"), "古案主轴，观察课式、问类、断语与验辞。"),
            _page("牧夫占验", Path("cases/daliuren/牧夫占验.md"), "补充近现代语境下的占验路径。"),
            _page("林烽-大六壬经典案例解析", MODERN_CASE_PAGE, "现代案例目录源，优先用 clean 版与可复核文本。"),
        ],
        "source_status": {
            "modern_case_clean": relative_source(root / MODERN_CASE_SOURCE, root),
            "modern_case_page": relative_source(root / MODERN_CASE_PAGE, root),
            "modern_case_ocr": "现阶段 OCR 文本质量不足，只作目录与归档源，不作全文断案依据。",
        },
    }


def render_daliuren_knowledge_markdown() -> str:
    lines = [
        "### 大六壬知识分层",
        "",
        "- 层级顺序：理法 -> 象根 -> 案例",
        "- 取用原则：先理后象，案例只作类比和验例",
        "",
        "#### 主题页",
    ]
    for item in build_daliuren_knowledge_context()["topic_pages"]:
        lines.append(f"- {item['name']}：{item['source']}")
    lines.extend(
        [
            "",
            "#### 运行提示",
            "- 理法页用于判断秩序与结构。",
            "- 象根页用于解释象义来源与边界。",
            "- 案例页用于学习取象路径，不把单案结论直接升格为通法。",
        ]
    )
    return "\n".join(lines)


def _page(name: str, path: Path, role: str) -> dict:
    return {
        "name": name,
        "source": path.as_posix(),
        "role": role,
    }
