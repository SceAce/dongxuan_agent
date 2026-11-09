# -*- coding: utf-8 -*-
"""补足：本命行年、将之虚实、月建月破、弹射/遥克之分、三层取象。"""
from core import ZHI, GAN, wxg, wxb
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
JI={'贵人':1,'螣蛇':0,'朱雀':0,'六合':1,'勾陈':0,'青龙':1,'天空':0,'白虎':0,'太常':1,'玄武':0,'太阴':0,'天后':1}
def stage(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(g)]))%12]

def yaoke_type(r,gan):
    """判遥克是「神遥克日」还是「日遥克神」"""
    if r['kind']!='遥克': return None
    g=wxg(gan); sc=r['sc']
    KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
    for s in sc[:1]:
        if KE[wxb(s)]==g: return '神遥克日（它来找我）'
        if KE[g]==wxb(s): return '日遥克神（我去够它）'
    return '遥克'

def jiang_xushi(r):
    """将之虚实：吉将／凶将各落何处，空否"""
    tp,js,kong=r['tp'],r['js'],r['kong']
    ji=[];xiong=[]
    for p in range(12):
        s=tp[ZHI[p]]
        j=js.get(s)
        if not j: continue
        item=f"{j}在{s}{'（空）' if s in kong else ''}"
        (ji if JI.get(j,0) else xiong).append(item)
    return {'吉将':ji,'凶将':xiong,
            '断':"吉将落空者乐不落地；凶将落实者烦心落实"}

def shensha(gan, month_zhi, year_zhi=None, sc=None):
    """月建／月破／岁破／日干在月令旺衰。month_zhi、year_zhi 须外部给。"""
    WXW={'寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土',
         '申':'金','酉':'金','戌':'土','亥':'水','子':'水','丑':'土'}
    out={}
    g=wxg(gan)
    # 月破：月建所冲
    out['月建']=month_zhi
    out['月破']=ZHI[(ZHI.index(month_zhi)+6)%12]
    if year_zhi: out['岁破']=ZHI[(ZHI.index(year_zhi)+6)%12]
    # 日干在月令旺衰（旺相休囚死）
    mw=WXW[month_zhi]
    SH={'木':'火','火':'土','土':'金','金':'水','水':'木'}
    SHENG={v:k for k,v in SH.items()}
    KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
    if mw==g: q='旺'
    elif SH.get(mw)==g: q='相'
    elif SHENG.get(mw)==g: q='休'
    elif KE.get(g)==mw: q='囚'
    else: q='死'
    out['日干在月令']=f"{gan}（{g}）在{month_zhi}月为{q}"
    if sc: out['三传逢破']=[s2 for s2 in sc if s2==out['月破']]
    return out

def benming_xingnian(birth_zhi,age,sex_male=True,birth_year_gz=None):
    """birth_zhi: 本命地支；birth_year_gz: 生年干支（如'乙亥'）"""
    from ming2 import xingnian
    ny=xingnian(age,sex_male,birth_year_gz)
    return {'本命':birth_zhi,'行年':ny,'行年地支':ny}

def san_ceng(r,gan,zhi):
    """三层取象：本义 / 临位 / 合成"""
    tp,sc,js=r['tp'],r['sc'],r['js']
    LINWEI={'申':'高处（坤为高阜）','亥':'暗处、水边','丑':'库、仓库','戌':'墓、山岗',
            '卯':'门户','酉':'私门、金属','巳':'灶、电器','午':'堂屋、灯',
            '辰':'堤岸、水库','未':'庭院、橱柜','子':'水、卧室','寅':'木器、庙'}
    out=[]
    for s in sc:
        q=[p for p in range(12) if tp[ZHI[p]]==s][0]
        base=f"{s}临{ZHI[q]}乘{js[s]}"
        out.append(f"{base}｜本义={s}｜临位={LINWEI.get(ZHI[q],ZHI[q])}｜将境={js[s]}")
    return out
