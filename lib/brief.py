# -*- coding: utf-8 -*-
"""一键出「喂给断课者的课盘」——象在前，理在后。

次序：先摆象（画面），后附理（只用于验、定应期）。
"""
from core import ZHI, wxg, wxb
from daluoren import pan
from layers import seven
from pair import pairs
from place import locate
from taixuan import n as tx
from bing import bing as _bing

# 支之基本象（用于拼画面，非穷举）
ZX = {'子':'水、房室、耳、盗','丑':'土、田宅、库、阁、僧','寅':'木、门户、庙、道路、吏人',
      '卯':'木、门、舟车、竹木、沙门','辰':'土、水库、堤岸、狱、网罗','巳':'火、灶、店业、口、弓',
      '午':'火、马、堂屋、目、心、丝绵','未':'土、庭院、衣帛、眷属、酒食','申':'金、道路、行人、僧、磨、刀',
      '酉':'金、婢、酒、血、私门、金银','戌':'土、山岗、坟墓、印绶、欺诈','亥':'水、厕、天门、头、楼台'}

def _compose(r, s, i):
    """把一个传拼成一张画：支（物）乘将（事）临处（位）。"""
    tp, js = r['tp'], r['js']
    q = [p for p in range(12) if tp[ZHI[p]] == s][0]
    j = js[s]
    a, b = locate(ZHI[q], j)
    a = a.split('、')[0:3]
    b = b.split('、')[0:2]
    return (f"{'初中末'[i]}{s}（{ZX.get(s,'?')}）乘{j}，临{ZHI[q]}："
            f"{'、'.join(a)}／{'、'.join(b)}")

def brief_text(gan, zhi, jy, shi, month_zhi=None, age=None, birth_gz=None,
               night=None, benming=None, age2=None, birth_gz2=None, benming2=None):
    r = pan(gan, zhi, jy, shi, night=night)
    tp, js, sc, sk, kong = r['tp'], r['js'], r['sc'], r['sk'], r['kong']
    L = []
    L.append(f"## 课盘")
    L.append(f"**{gan}{zhi}日　{jy}将{shi}时　{r['kind']}　旬空 {'、'.join(kong)}　贵人临{r['gui']}{r['dir']}**")
    L.append("")
    L.append("四课（上神/下神）：" + "　".join(f"{a}/{b}" for a, b in sk))
    L.append("三传：" + " → ".join(f"{s}({js[s]})" for s in sc))
    L.append("")

    # ===== 一 摆象（先看这个）=====
    L.append("## 一 摆象（先看这个，象自己会说话）")
    L.append("### 三传三张画")
    for i, s in enumerate(sc):
        L.append(f"- {_compose(r, s, i)}")
    L.append("")

    L.append("### 日上·支上（我与彼）")
    d, c = sk[0][0], sk[2][0]
    for nm, x in (("日上（我）", d), ("支上（彼）", c)):
        q = [p for p in range(12) if tp[ZHI[p]] == x][0]
        a, b = locate(ZHI[q], js[x])
        L.append(f"- {nm}：{x}（{ZX.get(x,'?')}）乘{js[x]}，" +
                 "、".join(b.split('、')[0:2]))
    L.append("")

    # 类神两重位置（对三传各支）
    L.append("### 类神两重位置（问「在哪」看第一重；问「往哪去」看第二重）")
    for s in sc:
        where = [ZHI[p] for p in range(12) if tp[ZHI[p]] == s]
        L.append(f"- {s}：地盘上神＝{tp[s]}｜作天盘神时临地盘＝{'、'.join(where)}")
    # 日支的两重（失物、走失常用）
    where_zhi = [ZHI[p] for p in range(12) if tp[ZHI[p]] == zhi]
    L.append(f"- **日支{zhi}（事体）**：地盘上神＝{tp[zhi]}｜作天盘神时临地盘＝{'、'.join(where_zhi)}")
    L.append("")

    pw = pairs(sc)
    if pw:
        L.append("### 器物相加（两物合一物）")
        for a, b in pw:
            L.append(f"- {a}：{b}")
        L.append("")

    # 年命
    if age and birth_gz:
        from ming2 import xingnian
        ny = xingnian(age, True, birth_gz)
        bm = benming or birth_gz[1]
        L.append("### 年命所关")
        L.append(f"- 本命{bm}：上神{tp[bm]}乘{js.get(tp[bm],'—')}（{ZX.get(tp[bm],'?')}）")
        L.append(f"- {age}岁行年{ny}：上神{tp[ny]}乘{js.get(tp[ny],'—')}")
        L.append(f"- 本命是否在传：{'在' if bm in sc else '不在'}｜行年是否在传：{'在' if ny in sc else '不在'}")
        # 对方年命（占婚、占合伙等）
        if benming2 or (age2 and birth_gz2):
            bm2 = benming2 or birth_gz2[1]
            ny2 = None
            if age2 and birth_gz2:
                ny2 = xingnian(age2, False, birth_gz2)
            L.append("")
            L.append("### 双方年命互乘（占婚必看）")
            L.append(f"- 我方：本命{bm}（上神{tp[bm]}）行年{ny}（上神{tp[ny]}）")
            if ny2:
                L.append(f"- 对方：本命{bm2}（上神{tp[bm2]}）行年{ny2}（上神{tp[ny2]}）")
            else:
                L.append(f"- 对方：本命{bm2}（上神{tp[bm2]}）")
            hit = []
            if tp[bm2] == bm or tp[bm2] == ny: hit.append(f"对方本命上神{tp[bm2]}＝我方本命/行年 → **对方命乘我**")
            if tp[bm] == bm2 or tp[bm] == ny2: hit.append(f"我本命上神{tp[bm]}＝对方本命/行年 → **我命乘对方**")
            if ny2 and tp[ny2] == bm: hit.append(f"对方行年上神{tp[ny2]}＝我本命 → **对方年乘我**")
            if tp[ny] == bm2: hit.append(f"我行年上神{tp[ny]}＝对方本命 → **我年乘对方**")
            L.append("- " + ("；".join(hit) if hit else "**未见互乘**"))
        L.append("")

    # 空墓处
    L.append("### 空亡·入墓·破碎（藏着未发之事）")
    marks = []
    for x in [d, c] + list(sc):
        if x in kong:
            marks.append(f"{x}空")
    for x in [d, c] + list(sc):
        pass
    from core import wxg as _w
    WX = {'木':'亥','火':'寅','土':'申','金':'巳','水':'申'}
    ORD = '长生 沐浴 冠带 临官 帝旺 衰 病 死 墓 绝 胎 养'.split()
    def _st(z):
        return ORD[(ZHI.index(z) - ZHI.index(WX[_w(gan)])) % 12]
    for x in [d, c] + list(sc):
        if _st(x) == '墓':
            marks.append(f"{x}为日干之墓")
        if _st(x) == '绝':
            marks.append(f"{x}为日干之绝")
    L.append("- " + ("；".join(marks) if marks else "无"))
    L.append("")

    # ===== 二 理（只用于验与定时）=====
    L.append("## 二 理（**不要用它推结论**，只用来验象、定应期）")
    L.append("### 七层")
    for k, v in seven(r, gan, zhi).items():
        L.append(f"- **{k}**：{v}")
    L.append("")
    L.append(f"### 太玄数　三传 " + "、".join(f"{s}={tx(s)}" for s in sc)
             + f"　相加={sum(tx(s) for s in sc)}")
    L.append("")
    L.append("### 占病专项（若问病，看这节）")
    for k, v in _bing(r, gan).items():
        L.append(f"- **{k}**：{v}")
    L.append("")
    if month_zhi:
        from extra import shensha
        ss = shensha(gan, month_zhi, None, sc)
        L.append(f"### 月建　月破{ss['月破']}　{ss['日干在月令']}")
    return "\n".join(L)


def lei_brief(gan, zhi, jy, shi_zhi, lei, month_zhi=None, age=None,
              birth_gz=None, night=None, benming=None):
    """以类神为核心摆象。lei 为类神之支（如失马取'午'）。"""
    r = pan(gan, zhi, jy, shi_zhi, night=night)
    tp, js, sc, sk, kong = r['tp'], r['js'], r['sc'], r['sk'], r['kong']
    L = []
    L.append(f"## 课盘　{gan}{zhi}日 {jy}将{shi_zhi}时 {r['kind']}　空{'、'.join(kong)}")
    L.append("")
    L.append(f"# 一 类神：{lei}（{ZX.get(lei,'?')}）")
    # 在不在传——这本身是断语
    in_sc = lei in sc
    pos = [f"{'初中末'[i]}传" for i, s in enumerate(sc) if s == lei]
    L.append("")
    L.append("## 一之一　类神在不在三传（**这一条本身就是答案**）")
    if in_sc:
        L.append(f"- **在传**：{'、'.join(pos)}")
        L.append("- 断：事显、在办、可寻。类神在传，事有下落。")
    else:
        L.append("- **不在三传**")
        L.append("- 断：**事隐、不显、难寻**。类神不入传，事不在眼前。")
        if lei in [x for p in sk for x in p]:
            L.append(f"- 但见於四课（在课不在传）：有心而未见行")
        if lei in kong:
            L.append("- **且类神旬空**：事本虚，求之无根")
    L.append("")
    # 两重位置
    up = tp[lei]
    where = [ZHI[p] for p in range(12) if tp[ZHI[p]] == lei]
    L.append("## 一之二　类神两重位置")
    kongmark = "　**⚠旬空**" if up in kong else ""
    L.append(f"- **第一重（现在何处）**：地盘{lei}之上神为 **{up}**，乘{js.get(up,'—')}（{ZX.get(up,'?')}）{kongmark}")
    if up in kong:
        L.append(f"  - **类神之上神旬空 → 类神虚、在眼前而不可得**")
    if lei in kong:
        L.append(f"  - **类神本身旬空 → 事本无根**")
    if up in sc:
        L.append(f"  - 类神之上神 {up} 在三传（{'、'.join(['初中末'[i] for i,x in enumerate(sc) if x==up])}）→ 事在传中显")
    L.append(f"- **第二重（往哪去）**：{lei}作天盘神时，临地盘 **{'、'.join(where)}**（{ZX.get(where[0],'?')}）")
    L.append("")
    L.append("> 问「在哪」看第一重；问「往哪去／被谁带走」看第二重。")
    L.append("> **直译：看到象，直接说事。不要过七层、不要串联。**")
    L.append("")
    # 所乘之将
    L.append("## 一之三　类神乘何将（将定其事）")
    if in_sc:
        L.append(f"- {lei}在传，乘 **{js[lei]}**")
    L.append(f"- 类神之上神 {up} 乘 **{js.get(up,'—')}**（类神所处之境）")
    L.append("")
    # 与谁相加
    L.append("## 一之四　类神与谁相加")
    hit = []
    for a, b in sk:
        if lei in (a, b):
            hit.append(f"{a}/{b}")
    pair = pairs([lei, up] + list(sc))
    if hit:
        L.append(f"- 类神所在之课：{'、'.join(hit)}")
    if pair:
        for a, b in pair[:3]:
            L.append(f"- {a}：{b}")
    if not hit and not pair:
        L.append("- 无")
    L.append("")
    # 年命
    if age and birth_gz:
        from ming2 import xingnian
        ny = xingnian(age, True, birth_gz)
        bm = benming or birth_gz[1]
        L.append("## 一之五　年命与类神")
        L.append(f"- 本命{bm}（上神{tp[bm]}）｜{age}岁行年{ny}（上神{tp[ny]}）")
        rel = []
        if bm == lei: rel.append("本命即类神")
        if ny == lei: rel.append("行年即类神")
        if tp[bm] == lei: rel.append("本命上神即类神")
        if tp[ny] == lei: rel.append("行年上神即类神")
        if lei in sc and bm in sc: rel.append("本命与类神同在三传")
        L.append("- " + ("；".join(rel) if rel else "年命与类神无直接相涉"))
        L.append("")
    # 附：全课象（次要）
    # 合（占婚、占合伙必查）
    SANHE=[('申','子','辰'),('亥','卯','未'),('寅','午','戌'),('巳','酉','丑')]
    LIUHE=[('子','丑'),('寅','亥'),('卯','戌'),('辰','酉'),('巳','申'),('午','未')]
    pool=[lei, up] + list(sc) + [a for p in sk for a in p]
    hits=[]
    for a,b in LIUHE:
        if a in pool and b in pool: hits.append(f"六合：{a}＋{b}")
    for tri in SANHE:
        got=set(tri)&set(pool)
        if len(got)==3: hits.append(f"三合全：{'、'.join(tri)}")
        elif len(got)==2: hits.append(f"半合：{'、'.join(sorted(got))}")
    if hits:
        L.append("## 一之六　合（占婚、占合伙必查）")
        for x in hits[:6]: L.append(f"- {x}")
        L.append("")
    L.append("# 二 全课之象（**次要，只作旁证，勿据此推主断**）")
    for i, s in enumerate(sc):
        L.append(f"- {_compose(r, s, i)}")
    L.append(f"- 日上{sk[0][0]}乘{js[sk[0][0]]}｜支上{sk[2][0]}乘{js[sk[2][0]]}")
    L.append("")
    L.append("# 三 理（**不要用它推结论**，只验象、定应期）")
    for k, v in seven(r, gan, zhi).items():
        L.append(f"- **{k}**：{v}")
    L.append(f"- 太玄数：{lei}={tx(lei)}；三传和={sum(tx(s) for s in sc)}")
    if month_zhi:
        from extra import shensha
        ss = shensha(gan, month_zhi, None, sc)
        L.append(f"- 月破{ss['月破']}　{ss['日干在月令']}")
    return "\n".join(L)
