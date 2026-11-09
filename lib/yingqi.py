# -*- coding: utf-8 -*-
"""应期推算：三传之支 + 日支，按空亡/墓/冲开加权。"""
from core import ZHI, GAN, wxg, wxb
from lunar_python import Solar
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
def stage(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(g)]))%12]

def yingqi(r, gan, zhi, start_date=None, days=60):
    """返回候选应期日，按权重排序。
    start_date: 'YYYY-MM-DD'，缺省用今天。"""
    import datetime
    sc, kong = r['sc'], r['kong']
    cands={}
    # 1 三传之支值日（初传最速，末传少应）
    w={'初':3,'中':2,'末':1}
    for i,s in enumerate(sc):
        cands.setdefault(s,0); cands[s]+=w['初中末'[i]]*2
    # 2 日支值日
    cands[zhi]=cands.get(zhi,0)+2
    # 3 空亡待填实：空亡之支值日，即为填实，权重高（实证：沉香案次日亥日得）
    for s in kong:
        cands.setdefault(s,0); cands[s]+=4
    # 4 墓待冲开：若三传有日干之墓，取其冲
    for s in sc:
        if stage(gan,s)=='墓':
            c=ZHI[(ZHI.index(s)+6)%12]
            cands[c]=cands.get(c,0)+2
    # 5 三合：三传成局时，局之三支皆可应
    SANHE=[('申','子','辰'),('亥','卯','未'),('寅','午','戌'),('巳','酉','丑')]
    scs=set(sc)
    for tri in SANHE:
        if len(scs & set(tri))>=2:
            for t2 in tri: cands[t2]=cands.get(t2,0)+1
    # 6 返吟：主速，近日即应
    if r['kind']=='返吟':
        for d0 in range(1,4):
            pass
    # 7 旬空之支若在三传，其冲亦动
    base = datetime.date.fromisoformat(start_date) if start_date else datetime.date.today()
    out=[]
    for d in range(1,days+1):
        day=base+datetime.timedelta(days=d)
        try:
            l=Solar.fromYmdHms(day.year,day.month,day.day,12,0,0).getLunar()
            gz=l.getDayInGanZhi()
        except Exception: continue
        if gz[1] in cands:
            out.append((cands[gz[1]], day.isoformat(), gz, f"值{cands[gz[1]]}分"))
    out.sort(key=lambda x:(-x[0],x[1]))
    res=out[:8]
    if r['kind']=='返吟':
        res.insert(0,(99,'（返吟主速）近三日','——','返吟课应期速，勿按常规推'))
    return res
