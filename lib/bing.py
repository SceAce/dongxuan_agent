# -*- coding: utf-8 -*-
"""占病专用：按「日上／支上起手」的次序输出，不走三传。"""
from core import ZHI, wxg, wxb
from engine import qin2
ZHANG={'子':'肾','亥':'肾','丑':'脾腹','未':'脾腹','寅':'肝胆','卯':'肝胆',
       '巳':'心目血','午':'心目血','申':'肺齿骨','酉':'肺齿骨','辰':'脾胃','戌':'脾胃'}
BINGXING={'螣蛇':'惊搐、扰动、棒伤','勾陈':'迟滞、壅塞、肿','白虎':'血光、刀急痛、丧',
          '玄武':'暗湿、疝、白浊、盗耗','天后':'水湿、妇人病、厌秽','太阴':'内伤、藏而不显',
          '天空':'虚、气不足','朱雀':'火、炎症、口舌','青龙':'酒食过度','太常':'酒食过度、伤身',
          '贵人':'得医、有人救'}
def bing(r, gan):
    g=wxg(gan); tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    d=sk[0][0]; c=sk[2][0]
    out={}
    out['一 上下']=f"日上{d}({js[d]}·{ZHANG.get(d,'?')})｜支上{c}({js[c]}·{ZHANG.get(c,'?')})"
    # 上下俱脱
    from core import wxg as W
    def rel(x):
        from core import WX_ZHI
        KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
        SH={'木':'火','火':'土','土':'金','金':'水','水':'木'}
        w=wxb(x)
        if w==g: return '比'
        if KE[w]==g: return '克我'
        if KE[g]==w: return '我克'
        if SH[w]==g: return '生我'
        if SH[g]==w: return '我生(脱)'
    out['二 上下之生克']=f"日上{rel(d)}｜支上{rel(c)}"
    if rel(d)=='我生(脱)' and rel(c) in ('我生(脱)','克我'):
        out['上下俱脱']="是 → 虚损、泄泻、痨伤"
    out['三 三传脏腑']='，'.join(f"{s}={ZHANG.get(s,'?')}" for s in sc)
    out['四 病性']='，'.join(f"{s}={BINGXING.get(js[s],'?')}" for s in sc)
    # 几见
    from collections import Counter
    cnt=Counter([d,c]+list(sc))
    out['五 几见']='、'.join(f"{z}见{n}次" for z,n in cnt.items() if n>=2) or '无重见'
    # 禁忌
    jj=[]
    if d=='午' or c=='午' or '午' in sc: jj.append("午为天之真火，克日则不宜灸；为天医则不宜服药")
    if any(s in kong for s in [d,c]+list(sc)): jj.append("有空亡者，主「偏」不主「无」")
    out['六 禁忌']='；'.join(jj) or '无'
    return out
