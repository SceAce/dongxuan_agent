# -*- coding: utf-8 -*-
from core import *
from jiang import jiang, JN
GUI_DAY={"甲":"丑","戊":"丑","庚":"丑","乙":"子","己":"子","丙":"亥","丁":"亥","壬":"巳","癸":"巳","辛":"午"}
GUI_NIGHT={"甲":"未","戊":"未","庚":"未","乙":"申","己":"申","丙":"酉","丁":"酉","壬":"卯","癸":"卯","辛":"寅"}
SHENG={"木":"火","火":"土","土":"金","金":"水","水":"木"}
KE={"木":"土","土":"水","水":"火","火":"金","金":"木"}
def dun(gan,zhi):
    g=GAN.index(gan); z=ZHI.index(zhi)
    head=(z-g)%12                      # 旬首支
    return {b: (None if (ZHI.index(b)-head)%12>=10 else GAN[(ZHI.index(b)-head)%12]) for b in ZHI}, head
def kong(head): return (ZHI[(head+10)%12], ZHI[(head+11)%12])
def qin2(g,w):
    if g==w: return "兄"
    if KE[g]==w: return "财"
    if KE[w]==g: return "官"
    if SHENG[g]==w: return "子"
    if SHENG[w]==g: return "父"
# 地支藏干（本气＋中气＋余气）
CANG={'子':['癸'],'丑':['己','癸','辛'],'寅':['甲','丙','戊'],'卯':['乙'],
      '辰':['戊','乙','癸'],'巳':['丙','庚','戊'],'午':['丁','己'],
      '未':['己','丁','乙'],'申':['庚','壬','戊'],'酉':['辛'],
      '戌':['戊','辛','丁'],'亥':['壬','甲']}
WXG='木木火火土土金金水水'
from core import GAN as _G
def cang_wx(z):
    """支之藏干五行集合"""
    return set(WXG[_G.index(g)] for g in CANG.get(z,[]))
def keylist(sk):
    """取克。

    「卯加辰，卯木辰内乙亦木不克」——乙寄宫在辰，卯加辰即卯加乙，
    卯与乙同为木，故不克。此非地支藏干之辨，乃**寄宫**之辨。
    （乙巳日戌将亥时案，邵彦和以此断为「四课俱不克，当以遥克」）
    """
    D=[];U=[]
    for i,(a,b) in enumerate(sk):
        wb = wxb(b) if b in ZHI else wxg(b)
        wa = wxb(a)
        # 上神与下神同类（含寄宫之干）→ 不克
        if wa == wb: continue
        if KE[wb]==wa: D.append((i+1,a))
        elif KE[wa]==wb: U.append((i+1,a))
    return D,U
def shehai(tp,s,gan):
    q=[p for p in range(12) if tp[ZHI[p]]==s][0]   # 现临地盘
    target=ZHI.index(s); n=0
    p=q
    for _ in range(12):
        if p==target: break
        p=(p+1)%12
        if KE[wxb(tp[ZHI[p]])]==wxb(ZHI[p]) or KE[wxb(ZHI[p])]==wxb(tp[ZHI[p]]): n+=1
    return n
def sanchuan(gan,zhi,tp,sk):
    D,U=keylist(sk)
    if D: cand=[a for _,a in D]; kind="重审"
    elif U: cand=[a for _,a in U]; kind="元首"
    else:
        # 遥克
        rec=[a for a,b in sk if KE[wxg(gan)]==wxb(a)]      # 日遥克神
        rok=[a for a,b in sk if KE[wxb(a)]==wxg(gan)]      # 神遥克日
        if rok: cand=rok; kind="遥克"
        elif rec: cand=rec; kind="遥克"
        else:
            kind="昴星"
            if GAN.index(gan)%2==0:  # 刚日
                ch=tp["酉"]; zhong=tp[zhi]; mo=tp[ZHI[JI[gan]]]
                return [ch,zhong,mo],"昴星"
            else:
                ch=[p for p in range(12) if tp[ZHI[p]]=="酉"][0]
                ch=ZHI[ch]; zhong=tp[ZHI[JI[gan]]]; mo=tp[zhi]
                return [ch,zhong,mo],"昴星"
    if len(cand)>1:
        yy=GAN.index(gan)%2
        bi=[a for a in cand if ZHI.index(a)%2==yy]
        if bi and len(bi)<len(cand): cand=bi; kind="知一"
        else:
            kind="涉害"
            # 指南：用孟名曰见机。先取所临地盘为四孟者
            meng=[a for a in cand if ZHI[[q for q in range(12) if tp[ZHI[q]]==a][0]] in "寅申巳亥"]
            if meng: cand=meng
            if len(cand)>1:
                sc={a:shehai(tp,a,gan) for a in cand}
                mx=max(sc.values()); cand=[a for a in cand if sc[a]==mx]
            if len(cand)>1:
                # 复等：刚用日比，柔用辰比
                yang = GAN.index(gan)%2==0
                pref = sk[0][0] if yang else sk[2][0]
                if pref in cand: cand=[pref]
    ch=cand[0]; zh=tp[ch]; mo=tp[zh]
    return [ch,zh,mo],kind
def paipan(gan,zhi,jy,shi,night=True):
    tp=tianpan(jy,shi); sk=sike(gan,zhi,tp)
    ch,kind=sanchuan(gan,zhi,tp,sk)
    gui = GUI_NIGHT[gan] if night else GUI_DAY[gan]
    p=[q for q in range(12) if tp[ZHI[q]]==gui][0]
    d=1 if ZHI[p] in "亥子丑寅卯辰" else -1
    js={tp[ZHI[(p+d*k)%12]]: JN[k] for k in range(12)}
    dg,head=dun(gan,zhi); kk=kong(head)
    return dict(tp=tp,sk=sk,sc=ch,kind=kind,js=js,dun=dg,kong=kk,gui=ZHI[p],dir=("顺" if d==1 else "逆"))
