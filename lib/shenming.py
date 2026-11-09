# -*- coding: utf-8 -*-
"""身命占：以本人生年月日时起终身命盘（据《大六壬论命秘要》）。

起法：取本人生月合神（月将）加于本人生时之上；以本人生日立四课；取三传。
  身＝日干（生日之干）；命＝本命（生年之支）。
"""
from core import ZHI, GAN, wxg, wxb, tianpan, sike
from fix import paipan2
from lunar_python import Solar
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
def stg(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(g)]))%12]

def cast(birth_year,month,day,hour=12,minute=0):
    """以出生时间起终身命盘。返回命盘 dict。"""
    s=Solar.fromYmdHms(birth_year,month,day,hour,minute,0)
    l=s.getLunar()
    year_gz=l.getYearInGanZhi()
    day_gz=l.getDayInGanZhi()
    time_gz=l.getTimeInGanZhi()
    gan, zhi = day_gz[0], day_gz[1]
    shi = time_gz[1]
    benming = year_gz[1]
    # 生月合神（月将）：以出生之日所在中气定
    import datetime
    t=l.getJieQiTable()
    ZHONG={"雨水":"亥","春分":"戌","谷雨":"酉","小满":"申","夏至":"未","大暑":"午",
           "处暑":"巳","秋分":"辰","霜降":"卯","小雪":"寅","冬至":"丑","大寒":"子"}
    cur=datetime.datetime(birth_year,month,day,12,0)
    best=None
    for name in ZHONG:
        j=t.get(name)
        if not j: continue
        dt=datetime.datetime(j.getYear(),j.getMonth(),j.getDay(),j.getHour(),j.getMinute())
        if dt<=cur and (best is None or dt>best[0]): best=(dt,ZHONG[name])
    jy=best[1] if best else '亥'
    r=paipan2(gan,zhi,jy,shi,night=(shi in '酉戌亥子丑寅'))
    r['birth']=f"{birth_year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
    r['year_gz']=year_gz; r['day_gz']=day_gz; r['time_gz']=time_gz
    r['benming']=benming; r['shen']=gan; r['jiang']=jy
    try:
        from minggong import minggong as _mg
        _mon=s.getLunar().getMonth()
        r['minggong']=_mg(_mon, shi)['命宫']
    except Exception:
        r['minggong']=benming
    return r

def shenming(r):
    """断身命：身、命、三限、寿夭。"""
    gan=r['shen']; bm=r['benming']; tp=r['tp']; js=r['js']; sc=r['sc']; kong=r['kong']
    sk=r['sk']
    # 命上神
    ming_shang=tp[bm]
    shen_shang=sk[0][0]
    out={}
    out['身（日干）']=f"{gan}，{stg(gan,shen_shang)}（身临{shen_shang}乘{js[shen_shang]}）"
    out['命（本命）']=f"{bm}，命上神{ming_shang}乘{js[ming_shang]}，{stg(gan,ming_shang)}"
    if ming_shang in kong: out['命上神空']="一身作事无成，多谋少遂，难立家计"
    if stg(gan,ming_shang)=='墓': out['命上入墓']="一世昏晦不明，行藏动静必不亨快"
    # 三限
    xian=[]
    for i,s in enumerate(sc):
        xian.append(f"{'少壮老'[i]}限·{['初','中','末'][i]}传{s}乘{js[s]}·{stg(gan,s)}")
    out['三限']=xian
    # 寿夭（专看本命上神）
    stage=stg(gan,ming_shang)
    if stage in ('长生',): out['寿夭']="本命上神长生→寿"
    elif stage in ('冠带','临官','帝旺'): out['寿夭']=f"本命上神{stage}→壮健可望寿"
    elif stage=='沐浴': out['寿夭']="沐浴→好色多病，备气不足"
    elif stage in ('死','墓','绝','胎','养'): out['寿夭']=f"本命上神{stage}→主夭"
    # 四孟仲季作传
    san=[('寅','申','巳','亥'),('子','午','卯','酉'),('辰','戌','丑','未')]
    nm=['四孟','四仲','四季']
    for i,grp in enumerate(san):
        if all(s in grp for s in sc):
            out['三传体']=f"{nm[i]}作三传→"+["主长寿（四孟）","不夭不寿（四仲）","命无寿（四季）"][i]
    return out

def gongwei(r, start=None):
    """十二宫（原文宫序，逆行）。start 缺省用 r['minggong']，否则本命支。"""
    from minggong import gong12
    tp=r['tp']; js=r['js']; kong=r['kong']; gan=r['shen']
    from gongwei import PAN
    from core import ZHI, wxg
    WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
    ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
    def stg(z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(gan)]))%12]
    mg=start or r.get('minggong') or r['benming']
    res=[]
    for g in gong12(mg):
        z=g['支']; up=tp[z]; j=js.get(up,'—')
        s2=f"{g['序']}.{g['宫']}（{z}·{g['五星']}）：上神{up}乘{j}·{stg(up)}"
        if z in kong or up in kong: s2+="·空"
        note=PAN.get(g['宫'],'')
        if note: s2+=f"｜{note}"
        res.append(s2)
    return res
