# -*- coding: utf-8 -*-
"""断课体系执行器：按八步输出依据，不打分、不算概率。"""
import json
from core import *
from engine import qin2
from death import gate, LU
from ming2 import xingnian, rel
LIB=json.load(open('/root/workspace/liuren/leixiang.json'))
TAG=json.load(open('/root/workspace/liuren/leixiang_tag.json'))
HAND={"婚":{"戌":"网罗","酉":"私门","卯":"门户","午":"升堂","巳":"不谐"},"讼":{"亥":"勾连","辰":"勾","酉":"雀","午":"官"},
 "官":{"申":"驿马","寅":"天吏","辰":"印绶","未":"印绶"},"财":{"戌":"火库","丑":"财库","酉":"财","亥":"财"},
 "宅":{"子":"宅","辰":"旧冢","戌":"旧冢"},"产":{"寅":"胎","午":"胎"},"坟":{"辰":"坟地","戌":"虚穴"},
 "失":{"酉":"物","戌":"物","午":"物","卯":"物","未":"物","丑":"物","亥":"物"},"病":{"午":"心","酉":"血","申":"肺","辰":"皮","亥":"肾","戌":"足"}}

LEISHEN={
 "婚":["天喜","六合","天后","青龙"],"官":["正官","日禄","驿马","青龙","太常"],
 "财":["财爻","青龙","劫煞"],"讼":["官鬼","勾陈","朱雀","贵人"],
 "病":["类神","天医","生气","病符","白虎","吊客"],"宅":["支辰","太阴","天后","玄武"],
 "产":["胎神","生气","天喜","驿马","浴盆"],"坟":["日墓","天空","青龙","白虎"],
 "失":["类神","玄武","勾陈"],"盗":["玄武","勾陈","劫煞"],"行":["驿马","信神"],
}
JIANG_GONG=json.load(open('/root/workspace/liuren/leixiang.json'))  # 复用
def run(gan,zhi,r,lei='?',age=None,nz=None,wu=None):
    tp,sk,sc,js,kong=r['tp'],r['sk'],r['sc'],r['js'],r['kong']
    g=wxg(gan); out=[]
    # 1 类神
    ls=LEISHEN.get(lei[0] if lei else '', ['类神未定，须先问事'])
    out.append(f"① 事类「{lei}」→ 类神：{'、'.join(ls)}")
    # 2 用神课体
    out.append(f"② 用神＝初传{sc[0]}（{qin2(g,wxb(sc[0]))}·{js[sc[0]]}），课体＝{r['kind']}")
    # 3 三传
    chain=[wxb(x) for x in sc]
    KE={"木":"土","土":"水","水":"火","火":"金","金":"木"}; SH={"木":"火","火":"土","土":"金","金":"水","水":"木"}
    rels=[]
    for i in range(2):
        a,b=chain[i],chain[i+1]
        rels.append("生" if SH[a]==b else "克" if KE[a]==b else "被克" if KE[b]==a else "受生" if SH[b]==a else "比")
    s3=f"③ 三传 {''.join(sc)}（{'→'.join(chain)}，{'-'.join(rels)}）"
    if all(SH[x]==g for x in chain): s3+="；三传生日，百事宜"
    if all(KE[x]==g for x in chain): s3+="；三传克日，众鬼难堪"
    if SH[g]==chain[0]: s3+="；初传脱气"
    out.append(s3)
    # 4 煞
    from audit import audit
    au=audit(gan,zhi,r,None,age,nz,lei)
    sha=[x for x in au if any(k in x for k in ("伏尸","天狱","六阴","周遍","贵多","禄空","墓空","官空","死门","三合成","破碎","羊刃"))]
    if wu and lei and lei[0] in "失盗":
        WU={"狗":"戌","鸡":"酉","马":"午","羊":"未","牛":"丑","猪":"亥","船":"卯","银":"酉","婢":"酉","奴":"戌","酒":"酉","牒":"朱雀"}
        ls2=WU.get(wu[0])
        if ls2 and ls2 in sc:
            i=sc.index(ls2)
            if js[ls2]=="白虎" or any(KE[wxb(x)]==wxb(ls2) for x in sc):
                sha.append(f"类神{ls2}（{wu}）在{'初中末'[i]}传而受损：物毁或不得")
            else: sha.append(f"类神{ls2}（{wu}）在{'初中末'[i]}传：物可见")
        elif ls2: sha.append(f"类神{ls2}（{wu}）不在传：难寻")
    out.append("④ 披煞："+("；".join(sha) if sha else "无可启用之煞（煞须临干支年命且与所问相犯）"))
    # 5 类象
    x=[]
    for i,s in enumerate(sc):
        pos=["初","中","末"][i]
        x.append(f"{pos}传{s}＝{LIB.get(s,['?'])[0]}／{js[s]}")
    out.append("⑤ 类象：支象×将象×六亲 → "+"；".join(x))
    try:
        from pair import pairs as _pr
        pr=_pr(sc)
        if pr: out.append("⑤c 器物相加："+"；".join(f"{a}＝{b}" for a,b in pr))
        else:
            from place import locate
            loc=[]
            for i,s2 in enumerate(sc):
                q=[p2 for p2 in range(12) if tp[ZHI[p2]]==s2][0]
                a,b=locate(ZHI[q], js[s2])
                loc.append(f"{'初中末'[i]}{s2}临{ZHI[q]}（{a}）乘{js[s2]}（{b}）")
            out.append("⑤c 类神临处："+"；".join(loc))
        # 阴神：每一传所临地盘之上神
        yin=[]
        for i,s2 in enumerate(sc):
            # 阴神：取该神本位之上神（四课法：本神作地盘，取其上天盘）
            y=tp[s2]; yj=js.get(y,'?')
            tag=""
            if s2 in kong: tag="（本神空）"
            yin.append(f"{'初中末'[i]}{s2}的阴神={y}乘{yj}{tag}")
        out.append("⑤d 阴神："+"；".join(yin))
    except Exception as e: pass
    # 5b 取象次序（人→物→事→处→变）
    from core import wxg as _wxg
    def layer(pos,s):
        p=[q for q in range(12) if tp[ZHI[q]]==s][0]
        wu_ok = None
        if wu:
            WU2={"狗":"戌","鸡":"酉","马":"午","羊":"未","牛":"丑","猪":"亥","船":"卯","银":"酉","婢":"酉","奴":"戌","酒":"酉"}
            if WU2.get(wu[0])==s: wu_ok=wu
        if not wu_ok:
            h=HAND.get(lei[0] if lei else '', {}).get(s)
            t=TAG.get(s,{}).get(lei[0] if lei else '', [])
            wu_ok = h or (t[0] if t else LIB.get(s,['?'])[0])
        return f"{pos}{s}：人＝{qin2(g,wxb(s))}｜物＝{wu_ok}｜事＝{js[s]}｜处＝{ZHI[p]}｜变＝{'空' if s in kong else '常'}"
    out.append("⑤b 取象次序："+" ；".join(layer(['初','中','末'][i],s) for i,s in enumerate(sc)))
    # 6 类比
    y=[f"日上{sk[0][0]}（{rel(gan,sk[0][0])}）", f"支上{sk[2][0]}（{rel(gan,sk[2][0])}）"]
    if nz: y.append(f"本命{nz}上{tp[nz]}（{rel(gan,tp[nz])}）")
    if age: y.append(f"行年{xingnian(age)}上{tp[xingnian(age)]}（{rel(gan,tp[xingnian(age)])}）")
    out.append("⑥ 类比："+"；".join(y))
    # 7 应期
    SHU={"子":9,"午":9,"丑":8,"未":8,"寅":7,"申":7,"卯":6,"酉":6,"辰":5,"戌":5,"巳":4,"亥":4}
    # 新法：候选＝三传之支＋日支；次序 初传→日支→中传→末传
    cand=[("初传",sc[0]),("日支",zhi),("中传",sc[1]),("末传",sc[2])]
    seen=[]; seq=[]
    for tag,zz in cand:
        if zz not in seen:
            seen.append(zz); seq.append(f"{tag}{zz}(数{SHU[zz]})")
    t7="⑦ 应期（三传＋日支）："+" → ".join(seq)
    if sc[2] in kong: t7+="；末空则无终"
    if any(x in kong for x in sc): t7+="；空者待填实"
    out.append(t7)
    # 8 取舍
    out.append("⑧ 取舍：必有＝课体＋用神＋类神三者同指；应有＝二者同指；或有＝一象独见")
    return out
