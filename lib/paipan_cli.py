# -*- coding: utf-8 -*-
"""命令行排盘：python3 paipan_cli.py 丁 卯 酉 申 [day|night]
也可给公历：python3 paipan_cli.py 2014-03-09 18:30  （自动算四柱、月将、旬空）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import ZHI, GAN
from daluoren import pan, brief

def from_datetime(y,mo,d,h,mi=0):
    try:
        from lunar_python import Solar
    except ImportError:
        print("需要 lunar_python：pip install lunar-python"); sys.exit(1)
    s=Solar.fromYmdHms(y,mo,d,h,mi,0); l=s.getLunar()
    yg,yz = l.getYearInGanZhi()[0], l.getYearInGanZhi()[1]
    dg,dz = l.getDayInGanZhi()[0], l.getDayInGanZhi()[1]
    tg = l.getTimeInGanZhi()[1]   # 时支
    # 往前找最近的中气（中气换将）
    ZHONG=["雨水","春分","谷雨","小满","夏至","大暑","处暑","秋分","霜降","小雪","冬至","大寒"]
    t=l.getJieQiTable()
    now=s.getSolar().toYmdHms() if hasattr(s,'getSolar') else s.toYmdHms()
    import datetime
    cur_dt=datetime.datetime(y,mo,d,h,mi)
    best=None
    for name in ZHONG:
        j=t.get(name)
        if not j: continue
        dt=datetime.datetime(j.getYear(),j.getMonth(),j.getDay(),j.getHour(),j.getMinute())
        if dt<=cur_dt and (best is None or dt>best[0]): best=(dt,name)
    jq=best[1] if best else l.getPrevJieQi().getName()
    # 中气换将：雨水后亥、春分后戌、谷雨后酉、小满后申、夏至后未、大暑后午、
    # 处暑后巳、秋分后辰、霜降后卯、小雪后寅、冬至后丑、大寒后子
    JQ={"雨水":"亥","春分":"戌","谷雨":"酉","小满":"申","夏至":"未","大暑":"午",
        "处暑":"巳","秋分":"辰","霜降":"卯","小雪":"寅","冬至":"丑","大寒":"子"}
    jy=JQ.get(jq)
    if not jy:
        print(f"当前节气 {jq} 非中气，请手动指定月将"); sys.exit(1)
    return dg,dz,jy,tg

if __name__=="__main__":
    a=sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    if '-' in a[0]:
        y,mo,d=map(int,a[0].split('-'))
        hh,mm=(map(int,a[1].split(':')) if len(a)>1 else (12,0))
        dg,dz,jy,tg=from_datetime(y,mo,d,hh,mm)
        print(f"日{dg}{dz} 月将{jy} 时{tg}")
    else:
        dg,dz,jy,tg=a[:4]
    r=pan(dg,dz,jy,tg)
    print(brief(r))
    print("四课:", ' '.join(f"{a_}/{b_}" for a_,b_ in r['sk']))
    print("三传:", ' '.join(f"{s}({r['js'][s]})" for s in r['sc']))
