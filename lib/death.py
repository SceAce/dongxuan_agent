# -*- coding: utf-8 -*-
from core import *
SI={"甲":"午","乙":"亥","丙":"酉","丁":"寅","戊":"酉","己":"寅","庚":"子","辛":"巳","壬":"卯","癸":"申"}
MU={"甲":"未","乙":"未","丙":"戌","丁":"戌","戊":"戌","己":"戌","庚":"丑","辛":"丑","壬":"辰","癸":"辰"}
JUE={"甲":"申","乙":"酉","丙":"亥","丁":"子","戊":"亥","己":"子","庚":"寅","辛":"卯","壬":"巳","癸":"午"}
CS={"甲":"亥","乙":"午","丙":"寅","丁":"酉","戊":"寅","己":"酉","庚":"巳","辛":"子","壬":"申","癸":"卯"}
LU={"甲":"寅","乙":"卯","丙":"巳","丁":"午","戊":"巳","己":"午","庚":"申","辛":"酉","壬":"亥","癸":"子"}
KE={"木":"土","土":"水","水":"火","火":"金","金":"木"}
def gate(gan, sc, tp, nian=None):
    hot=[]
    for i,x in enumerate(sc):
        if x==SI[gan]: hot.append((i,x,"死"))
        if x==MU[gan]: hot.append((i,x,"墓"))
        if x==JUE[gan]: hot.append((i,x,"绝"))
    if not hot: return "无死墓绝：未可言死", hot
    # 救一：行年临禄
    if nian and (tp[LU[gan]] and (tp[nian]==LU[gan] or nian==LU[gan])):
        return "死墓绝＋行年临禄：可治", hot
    # 救二：传有长生且不为鬼
    g=WX_GAN[GAN.index(gan)]
    for x in sc:
        if x==CS[gan] and not KE[WX_ZHI[ZHI.index(x)]]==g:
            return "死墓绝＋传有长生(非鬼)：可治", hot
    return "见死墓绝而无救：主死", hot
