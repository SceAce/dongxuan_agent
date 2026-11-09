# -*- coding: utf-8 -*-
from core import *
KE={"木":"土","土":"水","水":"火","火":"金","金":"木"}
XING={"子":"卯","卯":"子","寅":"巳","巳":"申","申":"寅","丑":"戌","戌":"未","未":"丑",
      "辰":"辰","午":"午","酉":"酉","亥":"亥"}
CHONG={b:ZHI[(ZHI.index(b)+6)%12] for b in ZHI}
def is_fuyin(jy,shi): return jy==shi
def is_fanyin(jy,shi): return ZHI[(ZHI.index(shi)+6)%12]==jy
BAZE_DAYS=set("甲寅 丁未 己未 庚申 癸丑".split())
def is_bazhuan(gan,zhi): return (gan+zhi) in BAZE_DAYS
def fuyin_sc(gan,zhi):
    ji=JI[gan]; s1=ZHI[ji]; s3=zhi
    gang = GAN.index(gan)%2==0
    # 乙癸日有克
    if gan in "乙癸":
        ch = "辰" if gan=="乙" else "丑"
        if gan=="乙": zh=CHONG["辰"]; mo=XING[zh]
        else: zh=XING["丑"]; mo=XING[zh]
        return [ch,zh,mo],"伏吟"
    ch = s1 if gang else s3
    zh = XING[ch]
    if zh==ch:                       # 自刑: 刚先日后辰
        zh = s3 if gang else s1
        mo = XING[zh]
        if mo==zh: mo = CHONG[zh]
        return [ch,zh,mo],"伏吟"
    mo = XING[zh]
    if mo==zh: mo = CHONG[zh]
    return [ch,zh,mo],"伏吟"

def fanyin_sc(gan,zhi,tp):
    # 无克四柔日：以辰冲为用。丑冲巳、未冲亥；取天盘该支上神为初传
    WU_KE=set("丁丑 己丑 辛丑 丁未 己未 辛未".split())
    gz=gan+zhi
    if gz in WU_KE:
        chong = "巳" if zhi=="丑" else "亥"
        ch = tp[chong]           # 天盘该支上神
        zh = tp[zhi]
        mo = tp[ZHI[JI[gan]]]
        return [ch,zh,mo],"返吟"
    return None,None

def baze_sc(gan,zhi,tp,sk):
    """八专（景祐原文）：两课。有克用比涉害；无克则
    刚日从日上阳神顺数三辰为初传，柔日从辰上阴神逆数三辰为初传；
    中传、末传以日辰上神重之。"""
    from engine import keylist
    D,U=keylist(sk)
    if D: cand=[a for _,a in D]; k="八专"
    elif U: cand=[a for _,a in U]; k="八专"
    else:
        yang=GAN.index(gan)%2==0
        if yang:
            start = sk[0][0]              # 日上阳神
            ch = ZHI[(ZHI.index(start)+2)%12]   # 顺数三辰（含本神为第一）
        else:
            start = sk[3][0]              # 辰上阴神（第四课）
            ch = ZHI[(ZHI.index(start)-2)%12]   # 逆数三辰
        ri = sk[0][0]                     # 日上神
        chen = sk[2][0]                   # 辰上神
        return [ch,ri,chen],"八专"
    ch=cand[0]
    return [ch,tp[ch],tp[tp[ch]]],k

def biezhe_sc(gan,zhi,tp):
    """别责：刚日取干合上神，柔日取支合上神；中末俱取日上神。"""
    HE={"甲":"己","己":"甲","乙":"庚","庚":"乙","丙":"辛","辛":"丙","丁":"壬","壬":"丁","戊":"癸","癸":"戊"}
    ZHE={"子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯","辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"}
    yang=GAN.index(gan)%2==0
    if yang:
        hg=HE[gan];  # 干合之干所寄宫
        src=tp[ZHI[JI[hg]]]
    else:
        src=tp[ZHE[zhi]]
    ri=tp[ZHI[JI[gan]]]
    return [src,ri,ri],"别责"

def paipan2(gan,zhi,jy,shi,night=True):
    from engine import paipan
    r=paipan(gan,zhi,jy,shi,night)
    tp=r['tp']; sk=r['sk']
    if is_fuyin(jy,shi):
        sc,k=fuyin_sc(gan,zhi); r['sc']=sc; r['kind']="伏吟"
        return r
    if is_fanyin(jy,shi):
        sc,k=fanyin_sc(gan,zhi,tp)
        if sc: r['sc']=sc
        r['kind']="返吟"
        return r
    if is_bazhuan(gan,zhi):
        sc,k=baze_sc(gan,zhi,tp,sk); r['sc']=sc; r['kind']="八专"
        return r
    # 别责：四课不备且无克无遥
    from engine import keylist
    D,U=keylist(sk)
    if not D and not U:
        rec=[a for a,b in sk if KE[wxg(gan)]==wxb(a)]
        rok=[a for a,b in sk if KE[wxb(a)]==wxg(gan)]
        if not rec and not rok:
            sc,k=biezhe_sc(gan,zhi,tp); r['sc']=sc; r['kind']=k
    return r
