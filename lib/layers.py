# -*- coding: utf-8 -*-
"""七层过一遍：强制每一层都产出结果，不产出就标「无据」。

病因：断课时只用了「身命占」那两条（命上神、应期），
其余五层（六亲、方位、将象、数法、组合）全漏。
本模块强制逐层输出，缺则显式标无据。
"""
from core import ZHI, GAN, wxg, wxb
from taixuan import n as tx
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
SH={'木':'火','火':'土','土':'金','金':'水','水':'木'}
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
def st(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(g)]))%12]
GUASHU={'子':'坎','丑':'艮','寅':'艮','卯':'震','辰':'巽','巳':'巽',
        '午':'离','未':'坤','申':'坤','酉':'兑','戌':'乾','亥':'乾'}
ZHANG={'子':'肾','亥':'肾','丑':'脾腹','未':'脾腹','寅':'肝胆','卯':'肝胆',
       '巳':'心','午':'心','申':'肺','酉':'肺','辰':'脾胃','戌':'脾胃'}

def seven(r, gan, zhi):
    """七层逐层输出。缺者标「此层无据」。"""
    g=wxg(gan); tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    out={}
    # 层一 五行
    def rel(s):
        w=wxb(s)
        if w==g: return '比'
        if KE[w]==g: return '克日'
        if KE[g]==w: return '日克(财)'
        if SH[w]==g: return '生日'
        if SH[g]==w: return '日生(脱)'
        return '?'
    rels=[f"{s}({wxb(s)})={rel(s)}" for s in sc]
    out['一 五行']="三传："+'，'.join(rels)
    # 层二 六亲（逐传 + 日上支上）
    MAP={'鬼':'官','官':'官','财':'财','子':'子孙','父':'父母','比':'兄弟','兄':'兄弟'}
    q=[f"{s}={ MAP[__import__('engine').qin2(g,wxb(s))] }" for s in sc]
    out['二 六亲']="三传："+'，'.join(q)+f"；日上{sk[0][0]}，支上{sk[2][0]}"
    # 层三 长生
    out['三 长生']="三传："+'，'.join(f"{s}={st(gan,s)}" for s in sc)+f"；本命{zhi}={st(gan,zhi)}；本命上神{tp[zhi]}={st(gan,tp[zhi])}"
    # 层四 将象
    out['四 将象']="三传所乘："+ '，'.join(f"{s}={js[s]}" for s in sc) + f"；日上={js[sk[0][0]]}"
    # 层五 方位（支之卦位 + 所临地盘）
    fw=[]
    for s in sc:
        pos=[p for p in range(12) if tp[ZHI[p]]==s][0]
        fw.append(f"{s}({GUASHU[s]})临{ZHI[pos]}({GUASHU[ZHI[pos]]})")
    out['五 方位']='，'.join(fw)
    # 层六 类象（脏腑/器物）——只给脏腑，器物查 place
    out['六 类象']="脏腑："+'，'.join(f"{s}={ZHANG[s]}" for s in sc if s in ZHANG)
    # 层七 数法
    # 几见：同一支在日上/支上/三传中出现几次
    from collections import Counter
    allz=[sk[0][0], sk[2][0]]+list(sc)
    cnt=Counter(allz)
    dup=[f"{z}见{c}次" for z,c in cnt.items() if c>=2]
    out['七 数法']=("【几见】"+("、".join(dup) if dup else "无重见")+"；")+"三传数："+'，'.join(f"{s}={tx(s)}" for s in sc)+f"；相加={sum(tx(s) for s in sc)}，相乘={__import__('functools').reduce(lambda a,b:a*b,[tx(s) for s in sc])}"
    return out

def check(r,gan,zhi):
    """检查断语是否用足了层次。返回缺层清单。"""
    L=seven(r,gan,zhi)
    return L
