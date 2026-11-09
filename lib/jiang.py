# -*- coding: utf-8 -*-
from core import *
JN=["贵人","螣蛇","朱雀","六合","勾陈","青龙","天空","白虎","太常","玄武","太阴","天后"]
GUI={"甲":("丑","未"),"戊":("丑","未"),"庚":("丑","未"),"乙":("子","申"),"己":("子","申"),
     "丙":("亥","酉"),"丁":("亥","酉"),"壬":("巳","卯"),"癸":("巳","卯"),"辛":("午","寅")}
def jiang(tp, gan, day=True):
    g = GUI[gan][0 if day else 1]
    p = [q for q in range(12) if tp[ZHI[q]]==g][0]
    d = 1 if ZHI[p] in "亥子丑寅卯辰" else -1
    return {tp[ZHI[(p+d*k)%12]]: JN[k] for k in range(12)}
