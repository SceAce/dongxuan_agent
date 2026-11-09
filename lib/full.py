# -*- coding: utf-8 -*-
"""全断：一课输出四套（十断 / 器物 / 类神临处 / 旺衰成败）。"""
from core import ZHI, GAN, wxg, wxb
from engine import qin2
from multi import ten, stg, ORD, WX, TAI
from pair import pairs
from place import locate
KE={"木":"土","土":"水","水":"火","火":"金","金":"木"}
def full(r,gan,zhi,night=False):
    tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    g=wxg(gan); L=[]
    L.append(("【一 十断】", ten(r,gan,zhi,night)))
    # 二 器物
    pr=pairs(sc)
    L.append(("【二 器物相加】", {a:b for a,b in pr} if pr else {"无":"三传不成对，改看类神临处"}))
    # 三 类神临处
    loc={}
    for i,s in enumerate(sc):
        q=[p for p in range(12) if tp[ZHI[p]]==s][0]
        a,b=locate(ZHI[q],js[s])
        loc[f"{'初中末'[i]}{s}临{ZHI[q]}乘{js[s]}"]=f"处={a}；境={b}"
    L.append(("【三 类神临处】", loc))
    # 四 成败（旺衰）
    ch={}
    for i,s in enumerate(sc):
        ch[f"{'初中末'[i]}{s}"]=f"{qin2(g,wxb(s))}·{stg(g,s)}"
    last=sc[2]
    verdict=[]
    if KE[wxb(last)]==g: verdict.append("末传克日→凶（100%）")
    if last in kong: verdict.append("末传空→无终")
    if stg(g,last)=='墓': verdict.append("末传入墓→事止")
    d=sk[0][0]
    if d in kong: verdict.append("日上神空→我无意/我不实")
    if not verdict: verdict=["末传不克日、不空、不入墓→事有终"]
    ch["判"]="；".join(verdict)
    L.append(("【四 成败】", ch))
    return L
