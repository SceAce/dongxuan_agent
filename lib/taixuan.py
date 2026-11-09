# -*- coding: utf-8 -*-
"""太玄数：甲己子午九，乙庚丑未八，丙辛寅申七，丁壬卯酉六，戊癸辰戌五，巳亥单四。"""
NUM={'甲':9,'己':9,'子':9,'午':9,
     '乙':8,'庚':8,'丑':8,'未':8,
     '丙':7,'辛':7,'寅':7,'申':7,
     '丁':6,'壬':6,'卯':6,'酉':6,
     '戊':5,'癸':5,'辰':5,'戌':5,
     '巳':4,'亥':4}
def n(x): return NUM.get(x,0)
def calc(parts, mode='add'):
    """parts: 干支列表。mode: add/mul/half/double"""
    vs=[n(p) for p in parts]
    if mode=='add': return sum(vs), vs, '+'.join(map(str,vs))
    if mode=='mul':
        r=1
        for v in vs: r*=v
        return r, vs, '×'.join(map(str,vs))
    if mode=='half': return sum(vs)//2, vs, f"({'+'.join(map(str,vs))})/2"
    if mode=='double': return sum(vs)*2, vs, f"({'+'.join(map(str,vs))})×2"
