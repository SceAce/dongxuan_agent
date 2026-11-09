# -*- coding: utf-8 -*-
from core import *
from death import gate
from ming2 import xingnian
from engine import dun as dun_
KE={"木":"土","土":"水","水":"火","火":"金","金":"木"}
SH={"木":"火","火":"土","土":"金","金":"水","水":"木"}
YIN=set("丑亥酉卯")
TIANMU={"春":"辰","夏":"未","秋":"戌","冬":"丑"}
def season(m):
    return "春" if m in "寅卯辰" else "夏" if m in "巳午未" else "秋" if m in "申酉戌" else "冬"
JIANG_GONG={
"贵人":{"子":"解纷","丑":"升堂","寅":"凭几","卯":"登车","巳":"受贡","午":"受贡","辰":"天牢怀怒","戌":"地狱怀怒","申":"移途","未":"列席","亥":"还绛宫","酉":"入私室"},
"螣蛇":{"子":"掩目","丑":"蟠龟","寅":"生角","酉":"露齿","巳":"乘雾","午":"飞空","未":"入林","亥":"坠水","卯":"当门","戌":"入冢","辰":"象龙"},
"朱雀":{"子":"损羽","丑":"掩目","寅":"安巢","卯":"安巢","辰":"投网","戌":"投网","申":"厉嘴","午":"衔符","未":"临坟","亥":"入水","酉":"夜噪","巳":"昼翔"},
"六合":{"亥":"待命","巳":"不谐","子":"反目","酉":"私窜","寅":"乘轩","辰":"违理","戌":"亡羞","午":"升堂","卯":"入室","丑":"纳采","未":"妆严"},
"勾陈":{"丑":"受越","子":"投机","寅":"遭囚","巳":"捧印","卯":"临门","酉":"披刃","辰":"升堂(狱吏勾连)","午":"反目","未":"入驿","戌":"下狱","申":"趋户","亥":"褰裳"},
"青龙":{"丑":"蟠泥","未":"蟠泥","戌":"登魁","辰":"飞天","巳":"飞天","午":"飞天","寅":"乘云","卯":"驱雷","申":"伤鳞","酉":"摧角","子":"入海","亥":"游江"},
"天空":{},"白虎":{"子":"溺水","亥":"溺水","午":"焚身","巳":"焚身","卯":"临门","酉":"临门","丑":"在野","未":"在野","寅":"登山","戌":"落阱","申":"衔牒","辰":"咥人"},
"太常":{"子":"遭枷","寅":"侧目","卯":"遗冠","戌":"逆命","申":"衔杯","丑":"受爵","巳":"铸印","未":"捧觚","午":"乘轩","辰":"佩印","亥":"征召","酉":"券书"},
"玄武":{"子":"散发","丑":"升堂","寅":"入林","辰":"失路","卯":"窥户","巳":"反顾","亥":"伏藏","未":"败于酒食","午":"截路","酉":"拔剑","申":"折足","戌":"遭囚"},
"太阴":{"子":"垂帘","丑":"入内","戌":"被察","辰":"造庭","寅":"跣足","午":"脱巾","亥":"裸形","巳":"伏枕","酉":"闭户","未":"观书","卯":"微行","申":"执政"},
"天后":{"子":"守闺","亥":"治事","酉":"倚户","卯":"临门","戌":"褰帷","午":"伏枕","巳":"裸体","辰":"毁妆","寅":"理发","申":"修容","丑":"偷窥","未":"沐浴"}}
def audit(gan,zhi,r,month=None,age=None,nz=None,shi_lei=None):
    tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    out=[]
    # 1 天目加支
    if month:
        tm=TIANMU[season(month)]
        if sk[2][0]==tm: out.append(f"天目({tm})加支 → 宅有伏尸、不利畜（秋戌夏未春辰冬丑）")
    # 2 六阴
    pool=[sk[0][0],sk[2][0]]+list(sc)
    n=sum(1 for x in pool if x in YIN)
    if n>=4: out.append(f"六阴俱备({n}/5) → 阴盛不利，日传入夜尤甚")
    # 3 干支关系
    ji=ZHI[JI[gan]]; wj=wxb(ji); wz=wxb(zhi)
    rilin=(tp[zhi]==ji); linri=(tp[ZHI[JI[gan]]]==zhi)
    if linri and KE[wz]==wj: out.append("辰临日而受克 → 赘婿（不能自立）")
    if linri and SH[wz]==wj: out.append("辰临日生日 → 自在（恢宏之志）")
    if linri and SH[wj]==wz: out.append("辰临日受生 → 归福")
    if rilin and KE[wj]==wz: out.append("日临辰而受克 → 乱首（行悖逆）")
    if rilin and SH[wz]==wj: out.append("日临辰受生 → 俸就（荣显）")
    if rilin and SH[wj]==wz: out.append("日临辰生辰 → 历虚（脱气无措）")
    # 4 三传与日干
    g=WX_GAN[GAN.index(gan)]
    if all(SH[g]==wxb(x) or True for x in sc):
        pass
    sc_g=[wxb(x) for x in sc]
    if all(SH[x]==g for x in sc_g): out.append("三传生日 → 百事宜")
    if all(SH[g]==x for x in sc_g): out.append("日生三传 → 财源耗（脱气）")
    if all(KE[g]==x for x in sc_g): out.append("日克三传 → 求财可羡")
    if all(KE[x]==g for x in sc_g): out.append("三传克日 → 众鬼难堪")
    # 5 空亡
    k=[x for x in sc if x in kong]
    if k: out.append(f"传中空亡：{''.join(k)} → {'初空事虚' if sc[0] in kong else ''}{'末空无终' if sc[2] in kong else ''}")
    # 6 十二宫＋死门
    st=stages(gan,sc)
    bad=[f"{x}{n}" for x,n in st if n in ("死","墓","绝","病")]
    if bad: out.append("传见死墓绝病："+"/".join(bad))
    if shi_lei and any(k in shi_lei for k in ("病","身","寿","终","命","死")):
        res,_=gate(gan,sc,tp,xingnian(age) if age else None)
        out.append("死门："+res)

    # 9 天狱：天罡所临＝日干寄宫
    jg=ZHI[JI[gan]]
    gz=[ZHI[p] for p in range(12) if tp[ZHI[p]]=="辰"]
    if gz and gz[0]==jg:
        bad = (sc[0] in kong) or (KE[wxb(sc[0])]==WX_GAN[GAN.index(gan)]) or any(js[x] in ("白虎","螣蛇") for x in sc)
        if bad: out.append("天狱（天罡加日本＋用神凶）：主大服大祸、争讼")
    # 10 一旬周遍：干上旬尾、支上旬首
    head=[p for p in range(12) if True]
    _,head2=dun_(gan,zhi)
    shou=ZHI[head2]; wei=ZHI[(head2+9)%12]
    if sk[0][0]==wei and sk[2][0]==shou: out.append("一旬周遍：干上旬尾支上旬首，我事毕而彼事又起")
    # 11 官空
    g5=WX_GAN[GAN.index(gan)]
    guan=[x for x in sc if KE[wxb(x)]==g5]
    if shi_lei and any(k in shi_lei for k in ("官","讼","任","试","职")) and guan and all(x in kong for x in guan) and (sk[0][0] in guan or sc[0] in guan):
        out.append("官空临干或发用：官星落空，反作鬼论")

    # 12 贵多不贵
    gs=[x for x in (sk[0][0],sk[2][0],sk[3][0])+tuple(sc) if js[x]=="贵人"]
    if len(gs)>=2: out.append("贵多不贵：遍地贵人，多谋少成、多差使")
    # 13 禄空
    from death import LU as _LU, JUE as _JUE, MU as _MU
    if _LU[gan] in sc and _LU[gan] in kong: out.append("禄空：禄神入传而空，前程无实禄")
    # 14 鬼贵人：贵人临日干绝地
    jue=_JUE[gan]
    if any(x==jue and js[x]=="贵人" for x in sc): out.append("鬼贵人：贵人临日干绝地，不可近、不可交财")
    # 15 墓空可脱
    mu=_MU[gan]
    if mu in sc and mu in kong: out.append("墓空：本命之墓落空，渐次脱去")
    # 16 财库/火库（末传为财之库则收，为火库则熔）

    # 17 三合局与化气
    JU={"申子辰":"水","亥卯未":"木","寅午戌":"火","巳酉丑":"金"}
    KE2={"木":"土","土":"水","水":"火","火":"金","金":"木"}
    g6=WX_GAN[GAN.index(gan)]
    for k,v in JU.items():
        if set(k)<=set(sc):
            rel = "财" if KE2[g6]==v else "鬼" if KE2[v]==g6 else "父" if SH[v]==g6 else "子" if SH[g6]==v else "比"
            us=wxb(sk[0][0])
            out.append(f"三合成{v}局（{k}）＝{rel}"+("；局反生日上，已化" if SH[v]==us else ""))
    # 18 连茹
    idx=[ZHI.index(x) for x in sc]
    if (idx[1]-idx[0])%12==1 and (idx[2]-idx[1])%12==1: out.append("三传顺连茹：事连而起")
    if (idx[0]-idx[1])%12==1 and (idx[1]-idx[2])%12==1: out.append("三传逆连茹：事退而止")
    # 19 三交（三传全四仲）
    if all(x in "子午卯酉" for x in sc): out.append("三交：四仲全见，事多交杂")
    # 7 将临宫
    for pos,x in (("日上",sk[0][0]),("支上",sk[2][0])):
        j=js[x]; gong=ZHI[[p for p in range(12) if tp[ZHI[p]]==x][0]]
        nm=JIANG_GONG.get(j,{}).get(gong)
        if nm: out.append(f"{pos}{x}·{j}临{gong} → {nm}")
    for i,x in enumerate(sc):
        j=js[x]; gong=ZHI[[p for p in range(12) if tp[ZHI[p]]==x][0]]
        nm=JIANG_GONG.get(j,{}).get(gong)
        if nm: out.append(f"{['初','中','末'][i]}传{x}·{j}临{gong} → {nm}")
    return out

SHENG12={}
def build12():
    yang={"甲":"亥","丙":"寅","戊":"寅","庚":"巳","壬":"申"}
    yin={"乙":"午","丁":"酉","己":"酉","辛":"子","癸":"卯"}
    order="长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养".split()
    for g,s in yang.items():
        i=ZHI.index(s)
        for k,n in enumerate(order): SHENG12.setdefault(g,{})[ZHI[(i+k)%12]]=n
    for g,s in yin.items():
        i=ZHI.index(s)
        for k,n in enumerate(order): SHENG12.setdefault(g,{})[ZHI[(i-k)%12]]=n
build12()
WX_START={"木":"亥","火":"寅","土":"申","金":"巳","水":"申"}
_ORD="长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养".split()
STAGE12={w:{ZHI[(ZHI.index(s)+i)%12]:_ORD[i] for i in range(12)} for w,s in WX_START.items()}
def stages(gan,sc):
    w=WX_GAN[GAN.index(gan)]
    return [(x,STAGE12[w][x]) for x in sc]
