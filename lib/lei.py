# -*- coding: utf-8 -*-
"""类神表：问什么 → 取什么类神。类神定了，象才有归属。"""
from core import ZHI, wxg, wxb
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
LU={'甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}
# 固定类神（支）
FIXED={'马':'午','牛':'丑','羊':'未','鸡':'酉','犬':'戌','猪':'亥',
       '车':'卯','舟':'卯','船':'卯','门':'卯','井':'未','灶':'巳',
       '田':'丑','宅':'丑','坟':'辰','狱':'辰'}
def leizhi(gan, zhi, shi):
    """按所问之事定类神。返回 (类神, 说明)。shi 为事类关键词。"""
    g=wxg(gan)
    for k,v in FIXED.items():
        if k in shi: return v, f"所失之物为{k}，类神取{v}"
    if any(k in shi for k in ('财','钱','利','买卖','生意')):
        # 我克者为财
        for z in ZHI:
            if KE[g]==wxb(z): return z+"(及同类)", f"我克者为财，{g}克{wxb(z)}，故财为{wxb(z)}之支"
    if any(k in shi for k in ('婚','娶','嫁','感情')):
        return None, "婚以六合为类神，兼取妻财（男占）／官星（女占）"
    if any(k in shi for k in ('病','疾')):
        return None, "病以日干为身、支辰为宅；以白虎为病神，支象定脏腑"
    if any(k in shi for k in ('讼','官','告','争')):
        return None, "讼以官鬼为对方、朱雀为词讼、贵人为主断者"
    if any(k in shi for k in ('行人','走失','寻人')):
        return None, "行人以驿马、日支、类神所临定方位"
    if any(k in shi for k in ('前程','功名','考试','升迁')):
        return None, "前程以禄（俸）、官星（位）、学堂（学）为类神"
    if any(k in shi for k in ('失','丢','寻物')):
        return None, "失物以所失之物定类神（问物名）；不知则取类神之阴神"
    return None, "事类未明，须先定类神"
