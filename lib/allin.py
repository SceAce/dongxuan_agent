# -*- coding: utf-8 -*-
"""全断入口：排盘 + 四套 + 补足五事，一次出齐。"""
from daluoren import pan
from full import full
from extra import yaoke_type, jiang_xushi, shensha, san_ceng, benming_xingnian
from taixuan import n as tx
from yingqi import yingqi
from layers import seven
from ming2 import xingnian

def allin(gan,zhi,jy,shi,month_zhi=None,year_zhi=None,age=None,birth_zhi=None,birth_gz=None,sex_male=True,night=False,start_date=None):
    r=pan(gan,zhi,jy,shi,night=night)
    out=[("【零 课体】", {
        "课体":r['kind'],
        "遥克类型":yaoke_type(r,gan) or "非遥克",
        "三传":''.join(r['sc']),
        "旬空":''.join(r['kong']),
        "贵人":f"临{r['gui']}{r['dir']}",
    })]
    out+=full(r,gan,zhi,night)
    if month_zhi or year_zhi:
        out.append(("【五 月建岁破】", shensha(gan,month_zhi or ZHI_MONTH(zhi),year_zhi,r['sc'])))
    out.append(("【六 将之虚实】", jiang_xushi(r)))
    out.append(("【七 三层取象】", {f"{i+1}":v for i,v in enumerate(san_ceng(r,gan,zhi))}))
    if age and birth_zhi:
        out.append(("【八 本命行年】", benming_xingnian(birth_zhi,age,sex_male,birth_gz)))
    # 八·五 七层过一遍（强制）
    out.append(("【八·五 七层】", seven(r,gan,zhi)))
    # 九 太玄数
    parts=[gan,zhi]+list(r['sc'])
    out.append(("【九 太玄数】", {
        "干支数": {x:tx(x) for x in [gan,zhi]},
        "三传数": {x:tx(x) for x in r['sc']},
        "干支和": tx(gan)+tx(zhi),
        "三传和": sum(tx(x) for x in r['sc']),
    }))
    # 十 应期
    if start_date:
        out.append(("【十 应期】", {f"{i+1}":f"{v[1]} {v[2]} {v[3]}" for i,v in enumerate(yingqi(r,gan,zhi,start_date)[:6])}))
    return r,out

def ZHI_MONTH(zhi):
    return zhi
