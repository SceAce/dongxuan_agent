# -*- coding: utf-8 -*-
"""复验器：同一结论用多条规则分别取象，看能对上几条。"""
from core import ZHI, GAN, wxg, wxb
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
def stage(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(g)]))%12]

def fuyan(r,gan,zhi,claim):
    """claim: 一句结论，如'物未出宅'。返回支持与反对的象。"""
    tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    sup=[];opp=[]
    # 通用复验点
    # 1 类神是否加干（自归）
    d=sk[0][0]
    # 2 三传是否出四课
    skz=set([a for a,b in sk]+[b for a,b in sk])
    in_ke = all(s in skz for s in sc)
    # 3 玄武是否临干支
    xw=[z for z in [a for a,b in sk] if js.get(z)=='玄武']
    # 4 末传状态
    last=sc[2]
    out={}
    out['三传不出四课']=in_ke
    out['玄武临干支']=xw if xw else '无'
    out['末传']=f"{last}·{stage(gan,last)}"+("（空）" if last in kong else "")
    out['日上神']=f"{d}·{js[d]}"+("（空）" if d in kong else "")
    # 5 类神所临
    out['类神临处']={s:ZHI[[p for p in range(12) if tp[ZHI[p]]==s][0]] for s in sc}
    return out
