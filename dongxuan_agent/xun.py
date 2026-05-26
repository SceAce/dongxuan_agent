from __future__ import annotations

from .constants import BRANCHES, JIAZI, STEMS


def build_xun_dun(day_gz: str) -> dict:
    idx = JIAZI.index(day_gz)
    xun_start_idx = (idx // 10) * 10
    xun_start = JIAZI[xun_start_idx]
    branch_to_stem: dict[str, str | None] = {branch: None for branch in BRANCHES}
    for offset in range(10):
        gz = JIAZI[xun_start_idx + offset]
        branch_to_stem[gz[1]] = gz[0]
    return {
        "xun_start": xun_start,
        "branch_to_stem": branch_to_stem,
        "xun_empty": tuple(branch for branch, stem in branch_to_stem.items() if stem is None),
    }
