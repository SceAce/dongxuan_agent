# -*- coding: utf-8 -*-
"""多重死象检测：数出死象几条、救神几条，据此定断。"""
from core import ZHI, GAN, wxg, wxb
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
SH={'木':'火','火':'土','土':'金','金':'水','水':'木'}
def st(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(g)]))%12]
WXW={'寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土',
     '申':'金','酉':'金','戌':'土','亥':'水','子':'水','丑':'土'}

def sis(r, gan, zhi, month_zhi=None, xingnian_zhi=None, benming=None):
    """返回 (死象list, 救神list)"""
    g=wxg(gan); tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    d,c=sk[0][0], sk[2][0]
    last=sc[2]
    S=[]; J=[]
    # 1 末传克日
    if KE[wxb(last)]==g: S.append("末传克日")
    # 2 末传入墓
    if st(gan,last)=='墓': S.append("末传入墓")
    # 3 末传空亡
    if last in kong: S.append("末传空亡")
    # 4 传归死墓：末传为死或墓
    if st(gan,last) in ('死','墓','绝'): S.append(f"传归{st(gan,last)}")
    # 5 上下俱脱
    def rel(x):
        w=wxb(x)
        if w==g: return '比'
        if KE[w]==g: return '克我'
        if KE[g]==w: return '我克'
        if SH[w]==g: return '生我'
        if SH[g]==w: return '脱'
    if rel(d)=='脱' and rel(c) in ('脱','克我'): S.append("上下俱脱")
    # 6 四课俱下贼（绝阴）
    from engine import keylist
    D,U=keylist(sk)
    if len(D)==4 and not U: S.append("四课俱下贼(绝阴)")
    # 7 本命上神临死墓绝胎养
    bm=benming or zhi
    if st(gan,tp[bm]) in ('死','墓','绝','胎','养'): S.append(f"本命上神临{st(gan,tp[bm])}")
    # 7b 本命本身临死墓绝
    if st(gan,bm) in ('死','墓','绝'): S.append(f"本命临{st(gan,bm)}")
    # 8 日干在月令死绝
    if month_zhi:
        mw=WXW[month_zhi]
        # 旺相休囚死：克我者当令→我死；我克者当令→我囚
        if KE[mw]==g: S.append("日干在月令死")
        elif KE[g]==mw: S.append("日干在月令囚")
        elif SH.get(mw)==g: J.append("日干在月令相")
    # 9 死神带虎克日＋空
    if js.get(last)=='白虎' and KE[wxb(last)]==g and last in kong: S.append("死神带虎克日又空(黄泉鬼)")
    # 10 壬日行丑寅卯进脱＋支上绝神
    if gan=='壬' and sc[:3]==['丑','寅','卯'] and st(gan,c)=='绝': S.append("壬日丑寅卯进脱+支上绝神")
    # 11 行年入三传
    if xingnian_zhi and xingnian_zhi in sc: S.append("行年入三传")
    # 12 干支各乘墓
    if st(gan,zhi)=='墓': S.append("支为日干之墓")
    if st(gan,d)=='墓': S.append("日上为日干之墓")
    # 救神
    if xingnian_zhi and xingnian_zhi not in sc:
        # 行年在传后
        order={s:i for i,s in enumerate(sc)}
        if st(gan,xingnian_zhi) in ('长生','临官','帝旺'): J.append("行年临禄旺(引退就禄)")
    # 本命上神长生旺相，但若同时又克日，则「恩中有害」，不算救
    if st(gan,tp[bm]) in ('长生','冠带','临官','帝旺') and KE[wxb(tp[bm])]!=g:
        J.append("本命上神长生旺相")
    if js.get(d)=='贵人': J.append("贵德临身")
    if month_zhi and (WXW[month_zhi]==g or SH.get(WXW[month_zhi])==g): J.append("时令旺身")
    # 制鬼之神＝良医
    for s in sc:
        if KE[wxb(s)]==g and any(KE[wxb(x)]==wxb(s) for x in sc): J.append("有制鬼之神(良医)")
        break
    return S,J

def duan(r,gan,zhi,month_zhi=None,xingnian_zhi=None,benming=None):
    S,J=sis(r,gan,zhi,month_zhi,xingnian_zhi,benming)
    sk=r['sk']; sc=r['sc']; kong=r['kong']; last=sc[2]
    d,c=sk[0][0], sk[2][0]
    from core import wxg as _w, wxb as _b
    g=_w(gan)
    # 三问：落空否／有制否／能改否
    JIE=[]
    for x in list(S):
        if x.startswith("末传") and last in kong: JIE.append(f"{x}→落空不发")
        if x=="上下俱脱" and (d in kong or c in kong): JIE.append("上下俱脱→一处落空，脱不成立")
    for s2 in sc:
        if KE[wxb(s2)]==g and any(KE[wxb(x)]==wxb(s2) for x in sc):
            JIE.append(f"{s2}为病神，有制之者→转机"); break
    if JIE:
        S=[x for x in S if not any(x in j for j in JIE)]
    # 铁律：上下俱脱者，月令旺相不能救（脱从两处泄，月令补不上）
    if "上下俱脱" in S:
        J=[x for x in J if x not in ("日干在月令相","时令旺身")]
        S.append("上下俱脱→月令不能救")
    # 三问过滤（不是加减）
    # 一问：此凶落空否 → 空则不发
    # 二问：有制之者否 → 有制则转
    # 三问：能改否（人事）→ 能改则免
    S2=[x for x in S]
    notes=[]
    # 一问
    if last in kong and any('末传' in x for x in S2):
        S2=[x for x in S2 if '末传' not in x]; notes.append("末传落空→该凶不发")
    # 二问（已由 JIE 处理）
    if JIE: notes.append("病神有制→转机")
    # 三问：人事可改者（迁居、改向、戒欲）——须外部给
    # 判
    n=len(S2)
    strong=sum(1 for x in J if x in ("行年临禄旺(引退就禄)","时令旺身","有制鬼之神(良医)","日干在月令相"))
    if n>=3 and strong==0: v="可断死（三问俱无解）"
    elif n>=3 and strong>0: v=f"危而可救（死象{n}，有{strong}项解）"
    elif n==2: v="断「危」，不给死期"
    elif n==1: v="只作「关口」"
    else: v="不断死"
    S=S2
    return {"死象":S,"救神":J,"解":JIE,"死象数":len(S),"判":v}
