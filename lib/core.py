# -*- coding: utf-8 -*-
ZHI = "子丑寅卯辰巳午未申酉戌亥"
GAN = "甲乙丙丁戊己庚辛壬癸"
JI  = dict(zip(GAN,[2,4,5,7,5,7,8,10,11,1]))  # 干寄宫: 甲寅 乙辰 丙戊巳 丁己未 庚申 辛戌 壬亥 癸丑
WX_ZHI = "水土木木土火火土金金土水"
WX_GAN = "木木火火土土金金水水"
def wxb(b): return WX_ZHI[ZHI.index(b)]
def wxg(g): return WX_GAN[GAN.index(g)]
def ke(a,b):  # a克b ?
    return {"木":"土","土":"水","水":"火","火":"金","金":"木"}[a]==b
def qin(gan, shen):
    g,s = wxg(gan), wxb(shen)
    if g==s: return "兄"
    if ke(g,s): return "财"
    if ke(s,g): return "官"
    if ke(s,g) is False and ke(g,s) is False:
        pass
    # 生
    sheng={"木":"火","火":"土","土":"金","金":"水","水":"木"}
    if sheng[g]==s: return "子"
    if sheng[s]==g: return "父"
    return "?"
def tianpan(jiang, shi):
    return {ZHI[p]: ZHI[(ZHI.index(jiang)+p-ZHI.index(shi))%12] for p in range(12)}
def sike(gan, zhi, tp):
    a1 = tp[ZHI[JI[gan]]]
    a2 = tp[a1]
    a3 = tp[zhi]
    a4 = tp[a3]
    return [(a1,gan),(a2,a1),(a3,zhi),(a4,a3)]
