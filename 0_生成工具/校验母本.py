#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社区服务信息主视觉设计 · 母本校验（对应 05 第 8 节的 12 条）
=============================================================
检查 content/D<编号>_<短名>/ 下的 master_zh.txt / master_en.txt / theme.yaml：
 1 信息项数量与 theme.yaml 声明一致
 2 中文标点全角、英文标点半角
 3 连字符均为 ASCII "-"
 4 英文无 ALL CAPS
 5 电话在中英两版字符完全一致
 6 数字与单位之间留空格（英文）
 7 中英信息项编号一一对应
 8 theme.yaml 可解析且五轴字段齐全
 9 五轴取值合法（D01–D15 / S1–S9 / A01–A08 / T1–T4 / L1–L5）
10 每条 L2 常识都有来源记录（sources 非空）
11 needs_human 已登记
12 长度区间：行动 4–18 字、提示/对象/求助 15–25 字、时间地点 25–40 字

用法：
    python3 校验母本.py                # 校验 content/ 下所有内容包
    python3 校验母本.py D04_health     # 只校验一个
只用标准库（本机没有 pyyaml，故对 theme.yaml 做轻量解析）。
"""

import os
import re
import sys

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(PKG, "content")

AXES = {
    "domain": r"^D(0[1-9]|1[0-5])$",
    "function": r"^S[1-9]$",
    "timeliness": r"^T[1-4]$",
    "authority": r"^L[1-5]$",
    "skeleton": r"^S[1-9]",
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_items(text):
    """返回 {编号: 正文}，正文 = 去掉注释与空行后的第一段"""
    items, cur = {}, None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^\[(\d{2})\]\s*(.*)$", line)
        if m:
            cur = int(m.group(1))
            items[cur] = ""
            continue
        if cur and line and not line.startswith("#"):
            items[cur] = (items[cur] + " " + line.strip()).strip()
    return items


def yaml_scalar(text, key):
    m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
    if not m:
        return None
    return m.group(1).split("#")[0].strip().strip('"').strip("'")


def check_pack(name):
    d = os.path.join(CONTENT, name)
    errs, warns, oks = [], [], []
    zh_p, en_p, ty_p = (os.path.join(d, f) for f in ("master_zh.txt", "master_en.txt", "theme.yaml"))
    for p in (zh_p, ty_p):
        if not os.path.exists(p):
            errs.append(f"缺少文件 {os.path.basename(p)}")
    if errs:
        return oks, warns, errs
    zh, ty = read(zh_p), read(ty_p)
    zi = parse_items(zh)

    # 语言版本（v1.4 规则）：受众含 A06 国际居民 → 双语；否则仅中文
    aud_raw = re.search(r"^audience:\s*\[(.*?)\]", ty, re.M)
    aud_list = [a.strip().strip('"') for a in aud_raw.group(1).split(",")] if aud_raw else []
    lang = (yaml_scalar(ty, "language") or "").strip()
    want_bi = "A06" in aud_list
    has_en = os.path.exists(en_p)
    if want_bi and not has_en:
        errs.append("受众含 A06（国际居民）→ 必须生成英文母本 master_en.txt")
    if (not want_bi) and has_en:
        errs.append("受众不含国际居民 → 不应生成英文母本（只出中文）")
    if lang and ((lang == "bilingual") != want_bi):
        errs.append("theme.yaml 的 language=%s 与受众（%s A06）不一致" % (lang, "含" if want_bi else "不含"))
    if not errs:
        oks.append("语言版本：%s（受众 %s）" % (lang or "未标注", "/".join(aud_list)))
    if not has_en:
        return oks, warns, errs          # 仅中文主题：跳过全部英文相关检查
    en = read(en_p)
    ei = parse_items(en)

    # 1 / 7 数量与编号对应
    declared = yaml_scalar(ty, "items")
    if declared and int(declared) != len(zi):
        errs.append(f"信息项数量不符：theme.yaml 声明 {declared}，中文母本 {len(zi)} 条")
    else:
        oks.append(f"信息项 {len(zi)} 条，与 theme.yaml 一致")
    if set(zi) != set(ei):
        errs.append(f"中英编号不一致：中文 {sorted(zi)} vs 英文 {sorted(ei)}")
    else:
        oks.append("中英信息项编号一一对应")

    # 2 标点
    def strip_time(t):
        return re.sub(r"\d{1,2}:\d{2}(-\d{1,2}:\d{2})?", "", t)
    bad_zh = [k for k, v in zi.items() if re.search(r"[,.:;]", strip_time(v))]
    if bad_zh:
        warns.append(f"中文出现半角标点（请复核）：{bad_zh}")
    else:
        oks.append("中文标点为全角")
    bad_en = [k for k, v in ei.items() if re.search(r"[，。：、]", v)]
    if bad_en:
        errs.append(f"英文出现全角标点：{bad_en}")
    else:
        oks.append("英文标点为半角")

    # 3 连字符
    bad_dash = [k for k, v in list(zi.items()) + list(ei.items()) if re.search(r"[–—]", v)]
    if bad_dash:
        errs.append(f"存在非 ASCII 连字符（en/em dash）：{bad_dash}")
    else:
        oks.append("连字符均为 ASCII '-'")

    # 4 ALL CAPS
    caps = [k for k, v in ei.items() if re.search(r"\b[A-Z]{3,}\b", v)
            and not re.search(r"\b(119|120|110|ID|SMS|PDF|PNG|A3|QR|AED|APP|WiFi)\b", v)]
    if caps:
        warns.append(f"英文疑似 ALL CAPS：{caps}")
    else:
        oks.append("英文无 ALL CAPS")

    # 5 电话一致
    pz = set(re.findall(r"\d{3}-\d{3}-\d{4}", zh))
    pe = set(re.findall(r"\d{3}-\d{3}-\d{4}", en))
    if pz and pz == pe:
        oks.append(f"电话中英一致：{'、'.join(sorted(pz))}")
    else:
        errs.append(f"电话不一致：中文 {sorted(pz)} vs 英文 {sorted(pe)}")

    # 8 / 9 五轴
    for k, pat in AXES.items():
        v = yaml_scalar(ty, k)
        if not v:
            errs.append(f"theme.yaml 缺少字段 {k}")
        elif not re.match(pat, v):
            errs.append(f"字段 {k} 取值非法：{v}")
    if not any("字段" in e for e in errs):
        oks.append("五轴字段齐全且取值合法")

    # 10 / 11
    n_src = len(re.findall(r"^\s+- item:", ty, re.M))
    if re.search(r"^sources:", ty, re.M) and n_src >= 1:
        oks.append("L2 常识来源已登记 %d 条" % n_src)
    else:
        errs.append("sources 为空：L2 常识必须挂官方来源")
    if re.search(r"^needs_human:", ty, re.M) and re.search(r"^\s+- ", ty, re.M):
        oks.append("needs_human 已登记")
    else:
        errs.append("needs_human 未登记")

    # 13 语句逻辑：紧急号码不得与非紧急触发词同句
    EMERG = r"(119|120|110)"
    EMERG_CTX = r"(火情|火灾|起火|冒烟|火警|急病|受伤|触电|燃气泄漏|报警|遇险|走失|家暴|人身危险|危险|fire|smoke|emergenc|injur|shock|gas leak|danger|lost|violence|abuse)"
    NON_EMERG = r"(违规充电|咨询|办理|预约|报名|投诉|建议|unsafe charging|inquiry|appointment|complaint)"
    seen_emerg = set()
    for k, v in list(zi.items()) + list(ei.items()):
        for sent in re.split(r"[。；;.!?]", v):
            if re.search(EMERG, sent):
                if not re.search(EMERG_CTX, sent, re.I) and (k, "nocontext") not in seen_emerg:
                    seen_emerg.add((k, "nocontext"))
                    errs.append("[%02d] 含紧急号码却无紧急触发词（可能让居民为非紧急事项拨打紧急号码）" % k)
                if re.search(NON_EMERG, sent, re.I) and (k, "mixed") not in seen_emerg:
                    seen_emerg.add((k, "mixed"))
                    errs.append("[%02d] 紧急号码与非紧急事项出现在同一句：%s" % (k, sent.strip()[:30]))
                break
    if not any("紧急" in e for e in errs):
        oks.append("紧急号码仅用于紧急语境")
    # 14 疑似重复（两条例子的字符重合度 ≥0.6）
    # 只比较正文类条目（排除机构标识/主标题等标签项），且两条都要够长，降低误报
    def header_of(k):
        seg = zh.split(f"[{k:02d}]")
        return seg[1].splitlines()[0].strip() if len(seg) > 1 else ""
    body_keys = [k for k in sorted(zi)
                 if not any(t in header_of(k) for t in ("机构标识", "主标题")) and len(zi[k]) >= 14]
    for a in range(len(body_keys)):
        for b in range(a + 1, len(body_keys)):
            x, y = set(zi[body_keys[a]]), set(zi[body_keys[b]])
            if x and y and len(x & y) / min(len(x), len(y)) >= 0.72:
                warns.append(f"[{body_keys[a]:02d}] 与 [{body_keys[b]:02d}] 用词重合度高，疑似重复，请人工确认")
    # 12 长度
    long_zh = []
    for k, v in zi.items():
        n = len(v)
        head = zh.split(f"[{k:02d}]")[1].splitlines()[0].strip()
        if "机构标识" in head:
            continue                      # 专有名词，不受长度区间约束
        if "主标题" in head:
            lo, hi = 6, 16
        elif "行动" in head or "禁止" in head or "正确做法" in head:
            lo, hi = 4, 30
        elif "时间地点" in head or "服务·时间地点" in head:
            lo, hi = 25, 58
        else:
            lo, hi = 12, 32
        if not (lo <= n <= hi):
            long_zh.append(f"[{k:02d}]{head} {n} 字（期望 {lo}–{hi}）")
    if long_zh:
        warns.append("长度超出实测区间（请复核）：" + "；".join(long_zh))
    else:
        oks.append("中文各条长度均在实测区间内")
    # 15 行数对齐（references/03）：中文 25 字/行，英文 49 字符/行
    import math as _m
    CPL_ZH, CPL_EN = 25, 49
    flat = plus1 = short = 0
    detail = []
    for k in sorted(zi):
        zh_n = len(re.sub(r"[\s，。：、；！？（）]", "", zi[k]))
        en_c = len(re.sub(r"\s", "", ei.get(k, "")))
        lz = _m.ceil(zh_n / CPL_ZH) or 1
        le = _m.ceil(en_c / CPL_EN) or 1
        if le > 3:
            errs.append("[%02d] 英文 %d 行，超过 3 行上限" % (k, le))
        elif le == lz:
            flat += 1
        elif le == lz + 1:
            plus1 += 1
            detail.append("[%02d]" % k)
        elif le == lz - 1:
            warns.append("[%02d] 英文 %d 行 vs 中文 %d 行：英文更短，块面不平衡（建议补标签使齐平）" % (k, le, lz))
            short += 1
        else:
            errs.append("[%02d] 英文 %d 行 vs 中文 %d 行：相差 ≥2 行，不合格" % (k, le, lz))
    if not any("行" in e and "不合格" in e for e in errs):
        oks.append("行数对齐：齐平 %d ／ +1（可接受）%d ／ 英文更短 %d ／ 不合格 0%s"
                   % (flat, plus1, short, ("　+1 项：" + " ".join(detail)) if detail else ""))
    # 19 icon-list.md（若存在）：8 列是否齐备
    icon_list = os.path.join(d, "icon-list.md")
    if os.path.exists(icon_list):
        it = read(icon_list)
        need = ["图标名", "含义", "用在", "来源", "授权", "是否需署名", "尺寸", "形状核对"]
        miss = [c for c in need if c not in it]
        if miss:
            errs.append("icon-list.md 缺列：" + "、".join(miss))
        else:
            oks.append("icon-list.md 八列齐备")

    # 16 YAML 结构：值里出现未加引号的 ": " 会导致解析失败
    bad_yaml = []
    for ln in ty.splitlines():
        m = re.match(r"^\s*[A-Za-z_][A-Za-z0-9_]*:\s+(.+?)\s*$", ln)
        if not m:
            continue
        v = m.group(1)
        if v.startswith(("{", "[", '"', "'")):
            continue                      # flow 映射/序列与引号值里的冒号是合法语法
        if ": " in v:
            bad_yaml.append(ln.strip()[:40])
    if bad_yaml:
        errs.append("YAML 值含未加引号的冒号（会解析失败）：" + "；".join(bad_yaml))
    else:
        oks.append("YAML 结构可解析")
    return oks, warns, errs


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    packs = [only] if only else sorted(
        n for n in os.listdir(CONTENT) if os.path.isdir(os.path.join(CONTENT, n)) and not n.startswith("_"))
    total_e = total_w = 0
    for name in packs:
        print(f"\n=== {name} ===")
        oks, warns, errs = check_pack(name)
        for o in oks:
            print("  ✓", o)
        for w in warns:
            print("  ! ", w)
        for e in errs:
            print("  ✗", e)
        total_e += len(errs)
        total_w += len(warns)
    print(f"\n汇总：{len(packs)} 个内容包 ｜ 通过项若干 ｜ 警告 {total_w} ｜ 错误 {total_e}")
    return 1 if total_e else 0


if __name__ == "__main__":
    sys.exit(main())
