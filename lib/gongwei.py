# -*- coding: utf-8 -*-
"""十二宫：就六壬盘上十二支位分之，每宫看地盘该支之上的天盘神与天将。"""
from core import ZHI, wxg, wxb
WX={'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
ORD='长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
def stg(g,z): return ORD[(ZHI.index(z)-ZHI.index(WX[wxg(g)]))%12]
# 十二宫固定次序
GONG=['命宫','兄弟','夫妻','子女','财帛','疾厄','迁移','奴仆','官禄','田宅','福德','相貌']
YUAN_SHU={'奴仆','妻妾','疾厄','迁移','官禄','福德','相貌'}   # 原书有的七宫
# 各宫判词（据《论命秘要》）
PAN={
 '奴仆':"受克为顺，生则不逊。遇虎勾并厌煞→惹祸累主人",
 '夫妻':"怕刑冲；无刑无劫便佳。有善逢吉为良德→益夫益子善持家",
 '疾厄':"却喜空。支忌丘墓莫相逢。遇德神为有救，遭恶将定主凶",
 '迁移':"逢二空→空空如也。若迁到处人钦敬，则德禄马在对宫",
 '官禄':"天驿二马动人应。无马官不显，无禄官缺俸。学堂龙德禄官星后作空→非官职有革，便为庸庸世上翁",
 '福德':"遇吉为荣凶则寒。逢空遇劫煞→一生坎坷无足言。有吉神良将会→优游子孙绵",
 '相貌':"看时辰。带勾玄并蛇虎→五官有破。贵常龙合旺相吉→相貌魁伟人敬亲",
}
def shier(r, start=None, shun=True):
    """排十二宫。start 为命宫所居之支，缺省取本命支。shun=True 顺行。"""
    tp=r['tp']; js=r['js']; kong=r['kong']
    gan=r['shen']
    start=start or r['benming']
    i=ZHI.index(start)
    out=[]
    for k,name in enumerate(GONG):
        z=ZHI[(i+k)%12] if shun else ZHI[(i-k)%12]
        up=tp[z]           # 天盘上神
        j=js.get(up,'—')
        row={'宫':name,'地支':z,'上神':up,'天将':j,'上神长生':stg(gan,up),
             '空':z in kong or up in kong}
        out.append(row)
    return out
def duan(r, start=None, shun=True):
    rows=shier(r,start,shun)
    res=[]
    for x in rows:
        note=PAN.get(x['宫'],'')
        s=f"{x['宫']}（{x['地支']}）：上神{x['上神']}乘{x['天将']}·{x['上神长生']}"
        if x['空']: s+="·空"
        if note: s+=f"｜{note}"
        elif x['宫'] not in ('命宫',): s+="｜（此宫名原书未见）"
        res.append(s)
    return res
