# -*- coding: utf-8 -*-
from core import *
CN={"零":0,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
def cn2int(s):
    if not s: return None
    if "十" in s:
        a,b=s.split("十")
        return (CN.get(a,1) if a else 1)*10 + (CN.get(b,0) if b else 0)
    if len(s)==1: return CN.get(s)
    if len(s)==2: return CN.get(s[0],0)*10+CN.get(s[1],0)
    if len(s)==3: return CN.get(s[0],0)*100+CN.get(s[1],0)*10+CN.get(s[2],0)
    return None
XUN_START={  # 生年旬 -> (男一岁支, 女一岁支)
 "甲子":("寅","申"),"甲戌":("子","午"),"甲申":("戌","辰"),
 "甲午":("申","寅"),"甲辰":("午","子"),"甲寅":("辰","戌")}
def xun_of(year_gz):
    """由生年干支求其旬首（甲X）"""
    g=GAN.index(year_gz[0]); z=ZHI.index(year_gz[1])
    head=ZHI[(z-g)%12]
    return "甲"+head
def xingnian(age, male=True, birth_year=None):
    """行年：男顺女逆，自本旬之起支行至本年岁数。
    birth_year 为生年干支（如'辛酉'）；缺省按甲子旬。"""
    key=xun_of(birth_year) if birth_year else "甲子"
    st=XUN_START.get(key, ("寅","申"))[0 if male else 1]
    i=ZHI.index(st)
    return ZHI[(i+(age-1))%12] if male else ZHI[(i-(age-1))%12]
def rel(gan,shen):
    g=wxg(gan); w=wxb(shen)
    S={"木":"火","火":"土","土":"金","金":"水","水":"木"}
    K={"木":"土","土":"水","水":"火","火":"金","金":"木"}
    if g==w: return "比"
    if S[g]==w: return "脱气"
    if S[w]==g: return "生我"
    if K[g]==w: return "我克(财)"
    if K[w]==g: return "克我(鬼)"
