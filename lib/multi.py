# -*- coding: utf-8 -*-
"""一式多断：同一课按十类事分别输出。"""
from core import ZHI, GAN, wxg, wxb
from engine import qin2
KE={"木":"土","土":"水","水":"火","火":"金","金":"木"}
SH={"木":"火","火":"土","土":"金","金":"水","水":"木"}
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
TAI={'甲':'酉','己':'酉','乙':'申','庚':'申','丙':'未','辛':'未','丁':'午','壬':'午','戊':'巳','癸':'巳'}
def stg(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[g]))%12]
def ten(r,gan,zhi,night=False,age=None,birth=None):
    tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    g=wxg(gan); out={}
    # 课体特性
    if r['kind']=='返吟':
        out['_课体']="返吟：凡事反复，问晴得晴、问雨得雨皆反之"
    # 天时
    tg=[ZHI[p] for p in range(12) if tp[ZHI[p]]=='辰'][0]
    jm='孟' if tg in '寅申巳亥' else ('仲' if tg in '子午卯酉' else '季')
    water=[s for s in sc if wxb(s) in '水']
    out['天时']=f"天罡临{tg}({jm})；"+(f"传见水神{''.join(water)}" if water else "传无水神")+("；水神空→阴而不雨" if any(w in kong for w in water) else "")
    # 疾病
    zang={'丑':'脾腹','未':'脾腹','亥':'肾','子':'肾','寅':'肝胆','卯':'肝胆','巳':'心','午':'心','申':'肺','酉':'肺'}
    WXZ={'水':'肾','木':'肝胆','火':'心','土':'脾胃','金':'肺'}
    from collections import Counter
    ws=[wxb(x) for x in sc]; cw=Counter(ws)
    dom=cw.most_common(1)[0]
    tz=f"三传五行：{'/'.join(ws)}"
    if dom[1]>=2: tz+=f"（{dom[0]}占{dom[1]}，主{WXZ[dom[0]]}）"
    out['疾病']=tz+"；支象："+"、".join(f"{s}{zang[s]}" for s in sc if s in zang)
    # 胎产
    t=TAI[gan]; out['胎产']=f"胎神{t}"+("（空→未孕）" if t in kong else ("（在传）" if t in sc else "（不在课）"))
    # 婚姻
    d,c=sk[0][0],sk[2][0]
    mv=[]
    if d in kong: mv.append("日上神空→我无意")
    if c in kong: mv.append("支上空→对方无意")
    out['婚姻']="；".join(mv) if mv else "日上支上俱不空，看财官旺衰"
    # 求财
    pool=list(sc)+[sk[0][0],sk[1][0],sk[2][0],sk[3][0]]
    cai=[s for s in pool if KE[g]==wxb(s)]
    out['求财']=(f"财爻{''.join(cai)}" if cai else "财不入传")+("（空→难得）" if any(c in kong for c in cai) else "")
    # 仕宦
    LU={'甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}
    lu=LU[gan]; out['仕宦']=f"禄{lu}"+("（空→位不实）" if lu in kong else ("（在传）" if lu in sc else ("（在四课）" if lu in pool else "（不在课）")))
    # 家宅
    out['家宅']=f"支上{c}({js[c]})"+("（空→宅基未定）" if c in kong else "")+(f"；支{c}为{g}之墓→宅有旧冢" if stg(g,zhi)=='墓' else "")
    # 行人
    out['行人']={'孟':'未动','仲':'在途','季':'已至'}[jm]
    # 出行
    ma=[s for s in sc if s in ('寅','申')]
    out['出行']=("驿马在传" if ma else "马不入传")+("（空→难行）" if any(m in kong for m in ma) else "")
    # 贵人登天门（昼占）
    gui_t=[ZHI[p] for p in range(12) if tp[ZHI[p]]==r['gui']][0]
    if gui_t in ('亥','子','丑') and not night:
        out['仕宦'] += "；贵人登天门（昼占）→利禄、得上人荐"
    # 蛇伤财禄
    if js.get(sc[0])=='螣蛇':
        out['家宅'] += "；初传乘蛇→财禄被蛇伤"
    # 印绶（考试）：辰戌丑未为印，朱雀为文书
    yin=[s2 for s2 in pool if s2 in ('辰','戌','丑','未')]
    zhu=[s2 for s2 in pool if js.get(s2)=='朱雀']
    if yin and zhu:
        out['印绶']="印（"+"".join(yin)+"）与朱雀（"+"".join(zhu)+"）同见→考试及第之象"
    elif zhu:
        out['印绶']="朱雀（"+"".join(zhu)+"）见，文书之事"
    # 行年（若给年龄）
    if age:
        try:
            from ming2 import xingnian
            ny=xingnian(age,True,birth)
            nys=tp[ny]; nyj=js.get(nys,'?')
            out['行年']=f"行年在{ny}，上神{nys}乘{nyj}"+("（空）" if nys in kong else "")
        except Exception: pass
    # 兵
    out['兵']="勾陈上下相生则不战，相克则战"
    return out
