# -*- coding: utf-8 -*-
"""起命宫与十二宫（据《大六壬断八字·身命占》原文）。

原文：
  起命宫。男女皆以正月起子，逆数十二位至本生月止，月上据本生时，
  复顺数至卯止，逢卯为立命。
  一命宫，二财帛，三兄弟，四田宅，五男女，六奴仆，
  七妻妾，八疾厄，九迁移，十官禄，十一福德，十二相貌。
  （「十二便为父母乡，又名相貌从逆得」→ 宫序逆行）
"""
from core import ZHI
# 十二宫次序（原文）
GONG12=['命宫','财帛','兄弟','田宅','男女','奴仆','妻妾','疾厄','迁移','官禄','福德','相貌']
# 「又名相貌，从逆得」：宫序逆行
# 五星五行（七政）: 申巳水 辰酉金 卯戌火 寅亥木 子丑土 午日 未月
WUXING5={'申':'水','巳':'水','辰':'金','酉':'金','卯':'火','戌':'火',
         '寅':'木','亥':'木','子':'土','丑':'土','午':'日','未':'月'}

def yue_pos(month):
    """正月起子，逆数至本生月。month: 1=正月 … 12=十二月"""
    return ZHI[(0-(month-1))%12]

def minggong(month, hour_zhi, mode='shengri'):
    """起命宫。
    mode='shengri'：正月起子逆数至生月 → 得支P；P上据生时；顺数至卯，逢卯为命。
    mode='jiang'  ：以时加太阳（月将），遇卯为命（《占平生课法起例》）。需另传 jiang。
    """
    if mode=='jiang':
        raise ValueError("此模式请用 minggong_jiang(jiang, hour_zhi)")
    P=yue_pos(month)
    pi=ZHI.index(P); hi=ZHI.index(hour_zhi); mao=ZHI.index('卯')
    mg=ZHI[(pi+mao-hi)%12]
    return {'生月':month,'生月所得支':P,'生时':hour_zhi,'命宫':mg}

def minggong_jiang(jiang, hour_zhi):
    """以时加太阳（月将），顺数至卯，遇卯为命。"""
    ji=ZHI.index(jiang); hi=ZHI.index(hour_zhi); mao=ZHI.index('卯')
    return ZHI[(ji+mao-hi)%12]

def gong12(ming):
    """自命宫起，逆行排十二宫。"""
    i=ZHI.index(ming)
    return [{'序':k+1,'宫':GONG12[k],'支':ZHI[(i-k)%12],'五星':WUXING5[ZHI[(i-k)%12]]}
            for k in range(12)]

def xiaoxian(ming, age):
    """行年（小限）：自立命宫逆行，遇当年太岁即行年。
    此处按「生年支→行年至太岁」的通行法给出：行年支 = 命宫顺数 age-1（视太岁）。
    原文未给算式，故本函数只做「逆行十二位」的展示。"""
    i=ZHI.index(ming)
    return ZHI[(i-(age-1))%12]
