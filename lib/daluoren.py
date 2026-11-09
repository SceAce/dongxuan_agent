# -*- coding: utf-8 -*-
"""大六壬排盘与断课入口。用法：
    from daluoren import pan, judge
    r = pan('丁','卯','酉','申', night=False)
    print(judge(r, '婚', age=30))
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix import paipan2
from xitong import run as _run
from pair import pairs as _pairs
from place import locate as _locate
from multi import ten as _ten
from core import ZHI

SHU={"子":9,"午":9,"丑":8,"未":8,"寅":7,"申":7,"卯":6,"酉":6,"辰":5,"戌":5,"巳":4,"亥":4}

def pan(gan, zhi, jy, shi, night=None):
    """排盘。gan/zhi/jy/shi 均为单字地支或天干。
    night 省略时按占时自动判昼夜（酉戌亥子丑寅为夜）。"""
    if night is None:
        night = shi in "酉戌亥子丑寅"
    return paipan2(gan, zhi, jy, shi, night=night)

def judge(r, lei='?', age=None, nz=None, wu=None, gan=None, zhi=None):
    """按八步输出断课依据。lei＝事类单字（婚/病/讼/官/财/宅/产/坟/失/行/盗）。"""
    out = _run(gan, zhi, r, lei, age, nz, wu)
    return out

def pairs_of(r):
    return _pairs(r['sc'])

def locate_of(shen, jiang):
    return _locate(shen, jiang)

def ten(r, gan, zhi, night=False):
    """一式多断：同一课按十类事分别输出"""
    return _ten(r, gan, zhi, night)

def brief(r):
    """一行摘要"""
    return (f"课体{r['kind']} 三传{''.join(r['sc'])} "
            f"日上{r['sk'][0][0]}({r['js'][r['sk'][0][0]]}) "
            f"支上{r['sk'][2][0]}({r['js'][r['sk'][2][0]]}) "
            f"空{''.join(r['kong'])} 贵临{r['gui']}{r['dir']}")
