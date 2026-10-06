#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社区服务信息主视觉设计 · 生成《物料交付与验收清单 v1.2》
=========================================================
在 v1.0 物料单基础上，补充「工作流程图阶段」（14 节点 + 5 个人工判断点）的
产物与验收项，并保持 v1.0 的外观（复用它的 styles.xml / theme1.xml / 列宽 / 页签色）。

- 只用 Python 标准库，没有第三方依赖（本机没有 openpyxl，所以直接写 OOXML）。
- 重跑会覆盖输出文件；人工填写的实测值请另存一份。
- 想要修改内容：改下面的数据区，再跑一次即可。

用法：
    python3 生成物料清单.py
输出：
    ../05_物料交付与验收清单.xlsx
"""

import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_assets", "物料交付与验收清单_v1.0.xlsx")
OUT = os.path.abspath(os.path.join(HERE, os.pardir, "05_物料交付与验收清单.xlsx"))

# ============================================================ 样式常量
# 全部沿用 v1.0 的 styleId，含义见 _assets 里的原文件
S_TITLE = 2      # 表标题
S_BAND = 55      # 标题右侧色带 / 空列
S_STRIPE = 56    # 标题下的深色细条（行高 3）
S_H1 = 11        # 表头第一列
S_HM = 25        # 表头中间列
S_HL = 12        # 表头最后一列
S_BODY = 17      # 正文
S_BODY_L = 18    # 正文（表格最后一行，多一条左边界）
S_CTR = 28       # 居中正文（序号列）
S_CTR_L = 30     # 居中正文（最后一行）
S_PRI = {        # 优先级徽章：必需 / 强烈建议 / 复用加分
    "必需": 39, "强烈建议": 40, "复用加分": 41,
}
S_PRI_L = 42     # 最后一行优先级徽章
S_LIMIT = 37     # 期限列
S_LIMIT_L = 38
S_GATE = 47      # Gate 标签
S_GATE_L = 48
S_GATE_D = 49    # Gate 时间列
S_GATE_DL = 50
S_RISK = 53      # 风险标签
S_RISK_L = 54
S_NOTE = 58      # 说明标签

MARK = "【v1.1 新增】"
MARK12 = "【v1.2 新增】"
UP = "【v1.1 升级】"

# ============================================================ 数据区

# ---------- 表 2：交付清单 ----------
# (优先级, 交付物, 文件名/路径, 规格与内容, 备注)
DELIVERY = [
    # --- v1.0 原有：必需 ---
    ("必需", "中文版海报（PNG）", "poster-cn_a3_v1.0_YYYYMMDD.png",
     "A3 竖版 297×420 mm；成品 3508×4961 px ／ 含出血 3579×5032 px @300 dpi；PNG-24；sRGB；无透明底", MARK12),
    ("必需", "中文版海报（PDF）", "poster-cn_a3_v1.0_YYYYMMDD.pdf",
     "同尺寸同版；每边 3 mm 出血 = 303×426 mm；含裁切线；打印店交付用", MARK12),
    ("必需", "英文版海报（PNG）", "poster-en_a3_v1.0_YYYYMMDD.png",
     "条件必需：仅当目标受众含国际居民（A06）时交付，否则本项标 N/A；规格同中文版", MARK12),
    ("必需", "英文版海报（PDF）", "poster-en_a3_v1.0_YYYYMMDD.pdf", "条件必需：受众含 A06 时交付；规格同中文版", MARK12),
    ("必需", "校验报告", "check-report.md", "每项写明 PASS / FAIL / 豁免理由，以及实测值 vs 目标值", ""),
    ("必需", "母本对照", "copy-diff.md",
     "按 theme.yaml 声明的信息项逐条列出母本原文与成品实际文本；差异应为空（示例主题为 9 项）", UP),
    ("必需", "Gate 1记录", "gate-records/gate1.md",
     "签字人、时间、AI提交物、判断依据、结论、退回意见、回退目标", ""),
    ("必需", "Gate 2记录", "gate-records/gate2.md", "同上", ""),
    ("必需", "Gate 3记录", "gate-records/gate3.md", "同上", ""),
    ("必需", "Gate 4记录", "gate-records/gate4.md", "同上", ""),
    ("必需", "设计系统", "design-tokens.json", "色值、字体、字号阶梯和栅格的具体数值", ""),
    # --- v1.1 新增：必需（流程图阶段的产物与证据链）---
    ("必需", "输入包清点", "intake.md",
     "按 references/01-classic-input-taxonomy.md 把来料逐条归入六类（服务对象 / 服务事项 / 时间地点 / 行动步骤 / 注意事项 / 图形素材），输出“序号 | 类别 | 原文逐字 | 主归 | 副归 | 来源句ID | 缺失存疑”；缺类显式写“无”并写明影响；判不准的进 unclassified 并标 NEEDS_HUMAN（节点 N1）", MARK),
    ("必需", "信息项字段表", "fact-table.md",
     "每条信息一行：字段化文本 + 官方来源链接或文号；图形素材需求另列（节点 N3）", MARK),
    ("必需", "视觉方向候选", "candidates.md",
     "≥3 个方向，每个写明“是什么 / 不是什么 / 风险”；只描述不落地（节点 N4，用于证明“冻结前 AI 只出候选”）", MARK),
    ("必需", "主视觉线框", "wireframes/",
     "2–3 版结构线框，只定信息层级不做修饰；每版标注所用骨架编号 S1–S9（节点 N5）", MARK),
    ("必需", "合规核查记录", "compliance-record.md",
     "字体授权、素材授权、肖像处理、标识使用规则四项逐条结论（节点 N10）", MARK),
    ("必需", "设计系统冻结记录", "freeze-record.md",
     "写明谁在什么时间依据什么冻结、DesignTokens 版本号；冻结后再改需走迷你评审（对应 Gate 3）", MARK),
    ("必需", "Gate 5记录", "gate-records/gate5.md",
     "双语一致性与对外责任：签字人、时间、AI提交物、判断依据、结论、退回意见、回退目标（对应 Gate 5）", MARK),
    ("必需", "SKILL.md 技能包", "skill/",
     "SKILL.md + references/ + adapters/；含 14 个编号步骤与 5 个 [HUMAN GATE]（节点 N13）", MARK),
    ("必需", "校验脚本", "scripts/",
     "verify_copy.py 等：母本字符比对、字号与对比度阈值、禁止元素扫描；脚本可复现才算证据链（节点 N12）", MARK),
    # --- v1.0 原有：强烈建议 ---
    ("强烈建议", "中文可编辑源文件", "poster_zh_source.svg", "文本、图形和版式可编辑", ""),
    ("强烈建议", "英文可编辑源文件", "poster_en_source.svg", "文本、图形和版式可编辑", ""),
    ("强烈建议", "交付说明", "00_交付说明.md", "说明这是什么、怎么改、谁签字、有效期", ""),
    ("强烈建议", "分类结果", "theme.yaml",
     "包含 domain、function、audience、timeliness、authority 五个字段 + 唯一主骨架（Gate 1 的判定对象）", UP),
    # --- v1.1 新增：强烈建议 ---
    ("强烈建议", "图标与图形规范", "icon-list.md",
     "图标清单 + 线宽 / 圆角 / 用色规则 + 素材来源与授权（节点 N6）", MARK),
    ("强烈建议", "缺项登记", "needs-human.md",
     "所有需要人类补齐的字段与决策，逐条含责任人、截止时间、影响范围（N1 与 fail-closed 规则）", MARK),
    # --- v1.0 原有：复用加分 ---
    ("复用加分", "空模板", "template_4x5.svg", "保留版式和样式，替换文案即可复用", ""),
    ("复用加分", "指令包", "prompt-pack.md", "下次可直接提交给AI使用", ""),
    ("复用加分", "复用说明", "reuse-guide.md", "说明更换日期、地点、语言时需要修改的位置", ""),
    # --- v1.1 新增：复用加分 ---
    ("复用加分", "内容包模板", "content/_template/",
     "theme.yaml + master_zh / master_en + assets 占位；换主题只需新增一个内容包", MARK),
    ("复用加分", "分类路由表", "taxonomy.yaml",
     "15 领域 / 9 骨架 / 8 受众 / 4 时效 / 5 权威等级 + fail-closed 规则（AI 直接读取）", MARK),
]

# 交付清单的“名称 → 序号”索引：后文引用一律走查表，增删条目也不会错位
IDX = {name: i for i, (_, name, _p, _s, _n) in enumerate(DELIVERY, start=1)}
EIDX = {name: i for i, (name, *_r) in enumerate(EXTRA, start=1)} if False else {}


def D(*names):
    """生成“是（交付清单 N）”引用"""
    return "是（交付清单 " + " / ".join(str(IDX[n]) for n in names) + "）"


def DRS(*names):
    """生成“交付清单 N–M”引用（用于补充说明表）"""
    nums = [IDX[n] for n in names]
    return f"交付清单 {nums[0]}–{nums[-1]}" if len(nums) > 1 else f"交付清单 {nums[0]}"


# ---------- 表 3：场景追加 ----------
# (追加物料, 文件名建议, 触发条件, 验收要求, 备注)
EXTRA = [
    ("纯文字版", "notice_zh.txt", "建议默认提供；尤其用于微信群发和读屏",
     "信息完整；阅读顺序正确；电话、日期、地点清晰", ""),
    ("大字版", "poster_zh_large_v1.0_YYYYMMDD.png", "受众包含老年人或低视力人士",
     "正文为标准版×1.5，且不低于48 px", ""),
    ("灰度版PDF", "poster_zh_grayscale_v1.0_YYYYMMDD.pdf", "使用场所只有黑白打印机",
     "灰度下保持4级信息层级", ""),
    ("横屏版", "poster_zh_screen_v1.0_YYYYMMDD.png", "用于电梯屏或社区大屏",
     "1920×1080；重新排版，不得拉伸竖版", ""),
    ("素材授权记录", "source.md", "使用图片、插图、图标或第三方素材",
     "写明来源、作者、授权类型、是否可商用", ""),
    ("有效期说明", "validity.md", "突发事件或应急信息",
     "写明失效时间、撤换责任人与撤换方式", ""),
    ("依据来源", "sources.md", "L1法定强制或L5商业便民类",
     "列出正式依据、发布日期、发布机构和链接/文号", ""),
    ("“禁止＋正确”成对图", "按项目命名", "S5警示禁止类",
     "禁止示例和正确做法必须成对出现；只交一张即不合格", ""),
    ("回退日志", "rollback-log.md", "发生任何Gate退回或版本回退",
     "每次写明回退步骤、原因和回退目标", ""),
    ("变更日志", "CHANGELOG.md", "出现两个及以上版本",
     "每个版本一行：修改内容、原因、批准人", ""),
    # --- v1.1 新增：派生物料（步骤 9：AI 必须先问用户）---
    ("派生物料·信息卡", "card_zh_v1.0_YYYYMMDD.png", "步骤 9 AI 主动询问后，用户确认需要",
     "与海报同一套设计系统；信息项不得新增；4:5 或 A6 卡面", MARK),
    ("派生物料·群消息图", "wechat_zh_v1.0_YYYYMMDD.png", "同上",
     "竖版 1:1 或 3:4；手机缩略下可读；母本不得改写", MARK),
    ("派生物料·导视牌", "sign_zh_v1.0_YYYYMMDD.pdf", "同上",
     "A4/A3 竖版；3 米内可识别；只保留“去哪里 / 几点 / 怎么办”", MARK),
    ("派生物料·折页", "leaflet_zh_v1.0_YYYYMMDD.pdf", "同上",
     "A4 对折或三折；阅读顺序正确；正反面信息不冲突", MARK),
    ("派生物料确认记录", "derivatives-confirm.md", "每次步骤 9 询问后",
     "写明问了什么、用户答什么、最终生成了哪些；未确认即未生成", MARK),
    ("冻结变更记录", "change-after-freeze.md", "冻结后又修改了设计系统或母本",
     "写明改了什么、谁批准、影响哪些物料、是否重跑 Gate 3", MARK),
]

# ---------- 表 4：成品规格 ----------
# (检查项, 目标值/判定标准, 备注)
SPEC = [
    ("文件命名", "{物料}_{语言}_{版本}_{日期}.{扩展名}", ""),
    ("画布尺寸", "A3 竖版 297×420 mm（@300 dpi = 3508×4961 px；单一规格，无第二套尺寸）", MARK12),
    ("画面比例", "A3 竖版 1:1.414（297:420），容差 ±1 mm；严禁拉伸", MARK12),
    ("几何完整性", "未因适配A3或其他纸型而拉伸", ""),
    ("PNG格式", "PNG-24", ""),
    ("色彩空间", "sRGB", ""),
    ("背景", "无透明通道，背景完全不透明", ""),
    ("文件大小", "A3 @300 dpi 含出血 PNG ≤ 25 MB；PDF ≤ 10 MB", MARK12),
    ("母本文字", "按 theme.yaml 声明的信息项字符级100%命中，包括标点和空格（示例主题 9 项）", UP),
    ("电话排版", "电话号码不跨行", ""),
    ("时间排版", "时间信息不跨行", ""),
    ("正文对比度", "≥4.5:1（受众含老年人或残障人士时为 ≥7:1，见第 25 项）", ""),
    ("大标题对比度", "≥3:1", ""),
    ("正文字号", "≥26 pt（≈9.2 mm）；受众含老年人或残障人士时为 ≥31 pt（见第 24 项）", MARK12),
    ("关键内容安全区", "电话、地点、日期不进入成品区最外圈 18 mm", MARK12),
    ("灰度层级", "转灰度后仍有4级可区分信息层级", ""),
    ("双语专名一致", "同一实体在所有位置写法完全一致；中英各自锁定，不做跨语言“统一”（示例：两处 Community … Center 分属不同实体）", UP),
    ("CMYK软打样", "冻结色彩前已检查印刷转换效果", ""),
    ("A3 打印版分辨率", "A3 成品区 3508×4961 px @300 dpi（含出血 3579×5032 px）", MARK12),
    ("A3 出血", "每边 3 mm；含出血 303×426 mm = 3579×5032 px；背景色块必须铺满出血区", MARK12),
    # --- v1.1 新增：分类型专属校验 ---
    ("分类路由产物", "theme.yaml 五个字段齐全且取值合法（D01–D15 / S1–S9 / 受众 / T1–T4 / L1–L5）", MARK),
    ("主骨架唯一性", "全图只用一个主骨架；骨架与信息功能匹配；未擅自更换已冻结骨架", MARK),
    ("S7·S8 合规", "未使用数据公示型（除非有真实数据源）与空间导视型（除非有已确认示意图）", MARK),
    ("字号升档", "受众含老年人或残障人士时，正文 ≥31 pt（≈11 mm），且不低于标准版", MARK12),
    ("对比度升档", "受众含老年人或残障人士时，正文对比度 ≥7:1", MARK),
    ("信息不单独依赖颜色", "灰度或色觉障碍模拟下，警示与分类信息仍可由图标、文字或形状区分", MARK),
    ("S5 禁止与正确成对", "警示禁止型必须同时给出“禁止项”与“正确做法”，只交一半即不合格", MARK),
    ("S9 电话为主视觉", "求助联络型中电话号码是画面最强视觉元素，且完全无遮挡", MARK),
    ("时效字段完整", "T3 一次性类含具体日期与报名截止；T4 突发应急类含发布时间（精确到小时）与有效期", MARK),
    ("权威等级合规", "L5 商业便民类未使用政务视觉语言（徽标、警示色、公文版式）", MARK),
    ("双语信息等价", "中英两版信息项数量与含义一致；英文无删词，只允许换行 / 缩一档 / 加块高", MARK),
    ("中英行数对齐", "每条英文行数 ≤ 中文行数 + 1 且 ≤ 3 行（齐平优先）；额度 英文字符 ≈ 中文字数 × 2；中英同项同字号", MARK12),
    ("禁止元素扫描", "无虚构标识、无原文没有的承诺、无商业促销语气", MARK),
    ("官方来源可追溯", "D02 社保救助、D09 安全应急类附官方来源链接或文号", MARK),
    ("画布比例正确", "画布固定 A3 竖版 1:1.414；无拉伸变形（原“4:5 贴到 A3”的方案已废弃）", MARK12),
    ("安全边距", "成品区四周 ≥18 mm；栏宽 242 mm（保证中文 25 字/行、英文 49 字符/行）", MARK12),
    ("A3 裁切线位置", "裁切线在成品区（297×420 mm）四角外侧，不进入成品区；成品区内无裁切标记压字", MARK12),
    ("双格式齐备", "每语言 PNG + PDF 同版齐备（修改后必须同时重出）；英文版仅在受众含 A06 时交付", MARK12),
]

# ---------- 表 5：Gate 记录 ----------
# (Gate, 建议审核重点, 默认回退目标)
GATES = [
    ("Gate 1", "主题分类与路由：domain / function / audience / timeliness / authority 五字段是否正确；"
               "主骨架是否唯一且与信息功能匹配；受众是否漏掉老年人或残障人士；是否误用 S7 / S8。"
               "提交物：theme.yaml", "不通过回步骤 2（N2 分类与路由）"),
    ("Gate 2", "事实与母本：机构全称、电话、地名、时间是否逐字正确；标点与空格是否与母本一致；"
               "官方来源是否可追溯；是否出现 AI 润色过的句子。提交物：fact-table.md、copy-diff.md、source.md",
     "不通过回步骤 3（母本本身缺失则回步骤 1）"),
    ("Gate 3", "设计系统冻结：风格关键词、色彩语义、字体授权、字号阶梯、对比度阈值、必含与禁止元素是否定稿；"
               "CMYK 软打样与灰度层级是否预检。提交物：candidates.md、design-tokens.json、freeze-record.md",
     "不通过回步骤 4（N4 方向候选生成）"),
    ("Gate 4", "中文版内容与可读性：信息项是否 100% 完整；电话与时间是否不跨行、无遮挡；"
               "老年受众是否可读；是否出现禁止元素；S5 是否做到禁止与正确成对；A3 版是否等比未拉伸、居中、留白 20 mm、出血与裁切线正确。提交物：poster-cn 屏幕版 + A3 版、check-report.md",
     "不通过回步骤 7（骨架本身不成立则回步骤 5）"),
    ("Gate 5", "双语一致性与对外责任：中英两版信息是否等价且无删词；落款、发布主体、发布日期、免责口径是否可对外；"
               "派生物料是否与主干一致；回退日志与变更日志是否齐全。提交物：poster_en、derivatives-confirm.md",
     "不通过回步骤 8（派生物料问题回步骤 9）"),
]

# ---------- 表 6：风险控制 ----------
RISKS = [
    ("CMYK变色", "鲜艳青蓝印刷后发灰或偏色", "冻结色彩前完成一次CMYK软打样", "未检查印刷转换效果且直接定稿"),
    ("灰度塌层级", "橙色警示条与浅灰背景混为一体",
     "层级同时使用边框、图标、粗细和明度差，不只依赖颜色", "灰度下无法识别4级层级"),
    ("缺少证据链", "只交两张PNG，无法证明内容可靠",
     "同步提交copy-diff、五个Gate记录及适用的回退日志", "必需记录缺失或无法追溯审批过程"),
    ("主题漂移", "换主题后仍沿用上一个主题的内容、配色与地名",
     "每次换主题重跑步骤 2 分类路由并过 Gate 1；内容全部放进 content/ 内容包", "未重新分类就直接套用旧内容包"),
    ("骨架偷换", "冻结后为省事更换主骨架，或混搭两种骨架",
     "Gate 3 冻结骨架编号；成品与冻结记录核对骨架是否一致", "成品骨架与冻结记录不一致"),
    ("派生物料失控", "AI 未经确认自行生成大量变体，交付物数量失控",
     "步骤 9 必须先询问用户；生成结果写入 derivatives-confirm.md", "出现未确认的派生物料"),
    ("冻结后偷改", "交付后为改文案直接重导出，未留痕",
     "冻结后任何修改走迷你评审并写入 CHANGELOG；版本号递增", "出现无版本记录的静默修改"),
    ("A3 拉伸变形", "为铺满 A3 纸面把 4:5 画面拉宽",
     "画面等比缩放居中；脚本检查宽高比是否仍为 1.25", "画面比例偏离 4:5 超过 ±1%"),
    ("出血与裁切线错位", "背景没铺到出血线，裁切后露出白边；裁切线压到正文",
     "背景色块铺满含出血画布；裁切线放在成品区四角外侧", "裁切后出现白线，或裁切线进入成品区"),
]

RISK_NOTES = [
    "计数口径：全部交付物 31 件 = 必需 18 + 强烈建议 8 + 复用加分 5；按交付类别计为 14 类。",
    "“必需 18 件”按文件计（含 5 个 Gate 记录与 9 项流程阶段产物）；流程阶段产物共 14 项，逐项见「流程阶段产物」表。",
    "打印版总尺寸“约2471×3071 px”按3 mm出血近似值记录；最终输出需结合实际页面尺寸与300 dpi设置复核。",
]

# ---------- 表 7：流程阶段产物 ----------
# (阶段, 节点, 产物, 文件名建议, 验收标准, 对应 Gate/回退, 交付清单引用)
STAGES = [
    ("输入", "N1", "输入包清点", "intake.md",
     "六类经典输入逐类标注“有 / 无 / 待补”；缺项写入 needs-human.md", "—", D("输入包清点")),
    ("路由", "N2", "分类结果", "theme.yaml",
     "五字段齐全且取值合法；主骨架唯一并与信息功能匹配", "G1 → 不通过回 N2", D("分类结果")),
    ("路由", "N2", "缺项登记", "needs-human.md",
     "每条含责任人、截止时间、影响范围", "G1（fail-closed）", D("缺项登记")),
    ("事实", "N3", "信息项字段表", "fact-table.md",
     "每条信息含字段化文本 + 官方来源链接或文号", "G2 → 不通过回 N3（母本缺失回 N1）", D("信息项字段表")),
    ("方向", "N4", "视觉方向候选", "candidates.md",
     "≥3 个方向，每个含“是什么 / 不是什么 / 风险”；只描述不落地", "G3 → 不通过回 N4", D("视觉方向候选")),
    ("方向", "G3", "设计系统与冻结记录", "design-tokens.json + freeze-record.md",
     "写明谁在什么时间依据什么冻结；含版本号", "冻结后再改走迷你评审", D("设计系统", "设计系统冻结记录")),
    ("结构", "N5", "主视觉线框", "wireframes/",
     "2–3 版，只定信息层级；每版标注骨架编号 S1–S9", "—", D("主视觉线框")),
    ("图形", "N6", "图标与图形规范", "icon-list.md",
     "图标清单 + 线宽 / 圆角 / 用色规则 + 来源授权", "—", D("图标与图形规范")),
    ("成稿", "N7", "中文版成稿（A3 画布）", "poster-cn_a3.png / .pdf",
     "母本零改写；字号 ≥26 pt、对比度达受众阈值；画布 A3、出血与裁切线正确", "G4 → 不通过回 N7（骨架不成立回 N5）",
     D("中文版海报（PNG）", "中文版海报（PDF）")),
    ("成稿", "N8", "英文版成稿（仅双语主题）", "poster-en_a3.png / .pdf",
     "受众含 A06 才执行；独立重排不套用中文行结构；永不删词；与中文版同画布", "G5 → 不通过回 N8",
     D("英文版海报（PNG）", "英文版海报（PDF）")),
    ("派生", "N9", "派生物料与确认记录", "derivatives/ + derivatives-confirm.md",
     "未确认不生成；确认记录写明问了什么、答了什么、生成了哪些", "G5（派生物料问题回 N9）", "是（场景追加 11–15）"),
    ("合规", "N10", "合规核查记录", "compliance-record.md",
     "字体授权 / 素材授权 / 肖像处理 / 标识使用规则四项逐条结论", "—", D("合规核查记录")),
    ("校验", "N12", "校验报告与脚本", "check-report.md + scripts/",
     "每项 PASS / FAIL / 豁免 + 实测值 vs 目标值；脚本可复现；含 A3 几何检查", "—", D("校验报告", "校验脚本")),
    ("交付", "N13–N14", "技能包与交付说明", "skill/ + 00_交付说明.md",
     "SKILL.md 含 14 步与 5 个 [HUMAN GATE]；交付说明写清“是什么 / 怎么改 / 谁签字 / 有效期”",
     "—", D("SKILL.md 技能包", "交付说明")),
]

# ---------- 表 8：补充说明（v1.1 + v1.2） ----------
# (补充位置, 补充内容, 为什么补, 依据)
DELTA = [
    # ---- v1.2：中英双语 × 双载体规格定死 ----
    ("【v1.2】" + DRS("中文版海报（PNG）", "英文版海报（PDF）") + " 区段",
     "v1.2 曾把打印方案拆成 4 个文件（中英 × PDF/PNG）；**v1.5 已简化为每语言 PNG + PDF 两个文件**，画布统一 A3",
     "当时为保证打印与屏幕各有一份；v1.5 统一 A3 后同一条产线即可覆盖两者", "04_SKILL.md Output / F1"),
    ("【v1.5】画布统一 A3 单一方案",
     "废弃“4:5 屏幕版 + A3 打印版”两套尺寸：画布统一为 A3 竖版 297×420 mm（3 mm 出血 = 303×426 mm），每语言只出 PNG + PDF 两个文件；字号改用 pt/mm 计（正文 ≥26 pt）；文件大小上限放宽到 25 MB",
     "两套尺寸意味着两套排版与两次校对；统一 A3 后屏幕与打印共用同一条产线，交付件从 6 个减到 2 个（双语 4 个）",
     "本轮需求确认 / 04_SKILL.md F1 · F13"),
    ("【v1.4】语言版本随受众",
     "交付清单中的英文版海报与英文版 A3 改为条件必需：仅当目标受众含 A06 国际居民时交付；否则只出中文（也不生成英文母本）",
     "避免为不需要英文的社区白做一套英文版，也让交付清单与实际交付一致", "04_SKILL.md F15"),
    ("【v1.4】信息项与任务概述以用户为准",
     "用户明确给出的信息项、任务概述、输出尺寸、目标受众、事实值一律优先于本包默认值；冲突时改锁 F1/F13 并重算",
     "用户给的是任务事实；本包默认只是兜底。此前 9:16 与默认 4:5 冲突时，应按用户尺寸执行", "04_SKILL.md F16"),
    ("【v1.4】受众缺失时自拟并询问",
     "用户未给目标受众时，AI 依主题拟定并主动询问确认；未确认前标“AI 拟定，待确认”",
     "受众决定语言版本、字号档位与内容取舍，不能由 AI 静默决定", "04_SKILL.md 步骤 1 / F16"),
    ("【v1.2】04_SKILL.md F1 / F13",
     "画布规格由“竖版 4:5 PNG”改为双载体：屏幕版 4:5（1080×1350）+ A3 打印版（297×420 mm、3 mm 出血）；"
     "新增 F13 A3 载体规则（画面等比居中、留白 20 mm、不拉伸不裁切、裁切线在成品区外侧）",
     "A3 是 1:1.414、4:5 是 1:1.25，比例不同；不写死放置规则就会被拉伸或被裁掉内容", "本轮需求确认（方案 A + 3 mm 出血）"),
    ("【v1.2】成品规格 2 / 3 / 19 / 20",
     "四条检查改为 A3 口径：成品 3508×4961 px、含出血 3579×5032 px、出血 303×426 mm、成品区 A3 竖版 297:420",
     "尺寸必须给到 px 级，否则打印店按低分辨率出图会糊", "300 dpi 换算"),
    ("【v1.2】成品规格新增 4 条",
     "A3 画面等比未拉伸（容差 ±1%）、A3 居中与留白（左右 20 mm）、A3 裁切线位置、A3 双格式齐备（PDF+PNG 同版）",
     "A3 版最常见的三种翻车：拉伸变形、裁切后露白边、裁切线压到正文", "本轮需求确认"),
    ("【v1.2】成品规格新增「中英行数对齐」",
     "新增检查项：每条英文行数 ≤ 中文行数 + 1 且 ≤ 3 行；额度为英文字符 ≈ 中文字数 × 2；中英同项必须同字号",
     "双语海报最常见的翻车是中文 1 行、英文挤成 2–3 行，导致字号被迫缩小、两版看起来不像一套", "references/03-line-parity.md"),
    ("【v1.2】风险控制新增 2 条",
     "新增“A3 拉伸变形”“出血与裁切线错位”两类风险及否决条件",
     "这是 A3 载体新引入的风险，v1.1 只覆盖了屏幕版", "本轮需求确认"),
    ("【v1.2】Gate 4",
     "中文版 Gate 的审核重点补上 A3 检查：等比未拉伸、居中、留白 20 mm、出血与裁切线正确",
     "A3 是新增的交付载体，必须有人签字确认几何正确", "本轮需求确认"),
    # ---- v1.1：流程图阶段产物 ----
    (DRS("输入包清点", "校验脚本"), "新增 9 项流程阶段产物为必需交付物：输入包清点、信息项字段表、视觉方向候选、"
                    "主视觉线框、合规核查记录、冻结记录、Gate 5 记录、SKILL.md 技能包、校验脚本",
     "v1.0 只覆盖成品与 4 个 Gate 记录，无法证明“人机协作流程有效”；这些是流程的中间产物与证据链",
     "工作流程图 N1–N13"),
    ("交付清单 " + str(IDX["分类结果"]), "“分类结果 theme.yaml”由强烈建议升为必需",
     "它是 Gate 1 的判定对象；没有它，分类路由无法复核，15 类分支也无法验证",
     "工作流程图 N2 / G1"),
    (DRS("图标与图形规范", "缺项登记"), "新增“图标与图形规范”“缺项登记”为强烈建议",
     "图形统一化（N6）与 fail-closed 缺项登记是流程节点的直接产物", "N6 / taxonomy fail-closed"),
    (DRS("内容包模板", "分类路由表"), "新增“内容包模板”“分类路由表”为复用加分",
     "换主题只需新增一个内容包，是“适配 15 类分支”这件事的复用证据", "06 分类体系 / taxonomy.yaml"),
    ("交付清单 4、成品规格 9、17", "把写死的“9 项母本”“两个 Community … Center”改为按 theme.yaml 声明的信息项"
                            "与“同一实体写法一致”的通用判定",
     "顶层 Skill 适配 15 类分支，信息项数量与专名都不固定，写死会导致换主题即失效", "06 分类体系"),
    ("场景追加 11–15", "新增四类派生物料（信息卡 / 群消息图 / 导视牌 / 折页）+ 派生物料确认记录，"
                   "触发条件写成“AI 询问后用户确认”",
     "对应步骤 9：AI 必须先问用户，未确认即不生成", "04_SKILL.md 步骤 9"),
    ("场景追加 16", "新增“冻结变更记录”，触发条件为冻结后又修改",
     "冻结后任何修改都要走迷你评审并留痕，否则版本不可追溯", "03 人类前置准备清单 A 节"),
    ("成品规格 21–23", "新增分类路由三类检查：五字段合法性、主骨架唯一性、S7/S8 合规",
     "分类错了后面全错，必须在校验阶段拦一次", "taxonomy.yaml routing"),
    ("成品规格 24–25", "新增字号与对比度的“升档”检查（含老年人或残障受众时 ≥40 px、≥7:1）",
     "v1.0 只写了 34 px / 4.5:1，漏了升档规则，老年受众场景会不合格", "06 分类体系 轴 3"),
    ("成品规格 26", "新增“信息不单独依赖颜色”检查",
     "灰度与色觉障碍场景下不能只靠颜色传递警示或分类信息", "06 分类体系 轴 3 受众禁忌"),
    ("成品规格 27–28", "新增 S5 成对、S9 电话为主视觉两条骨架专属检查",
     "这两类骨架最常见的失败模式就是“只交一半”和“电话不够大”", "06 分类体系 轴 2 反模式"),
    ("成品规格 29–30", "新增时效字段完整性与权威等级合规检查",
     "T4 突发应急缺发布时间即失效；L5 商业便民不得使用政务视觉语言", "06 分类体系 轴 4"),
    ("成品规格 31–33", "新增双语信息等价、禁止元素扫描、官方来源可追溯",
     "输出兜底三件套，对应 Gate 2 与 Gate 5 的判定依据", "04_SKILL.md 铁律 1 / 3 / 4"),
    ("Gate 记录", "由 4 个 Gate 改为 5 个，并为每条写入审核重点与默认回退目标",
     "工作流程图定稿为 5 个人工判断点，每个都必须写“不通过回哪个节点”", "工作流程图 G1–G5"),
    ("风险控制（v1.1 新增）", "新增主题漂移、骨架偷换、派生物料失控、冻结后偷改四类风险",
     "都是“一套 Skill 适配 15 类分支”带来的新风险", "工作流程图 / 06 分类体系"),
    ("新增工作表「流程阶段产物」", "把 14 个节点的产物、文件名、验收标准、对应 Gate 与回退目标一次列清",
     "老师可据此逐节点验收；换主题时也可对照检查有没有漏产物", "工作流程图 N1–N14"),
]

# ============================================================ XML 工具

def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def col_letter(i):
    """1 → A, 27 → AA"""
    s = ""
    while i > 0:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def cell(ref, style, value=None, numeric=False):
    if value is None or value == "":
        return f'<x:c r="{ref}" s="{style}" />'
    if numeric:
        return f'<x:c r="{ref}" s="{style}"><x:v>{esc(value)}</x:v></x:c>'
    return f'<x:c r="{ref}" s="{style}" t="str"><x:v>{esc(value)}</x:v></x:c>'


def row_xml(r, cells, height=None, stripe=False):
    """cells: [(colIndex, style, value, numeric)]"""
    attrs = f'r="{r}"'
    if stripe:
        attrs += ' ht="3" customHeight="1"'
    elif height:
        attrs += f' ht="{height}" customHeight="1"'
    body = "".join(cell(f"{col_letter(c)}{r}", s, v, n) for c, s, v, n in cells)
    return f"<x:row {attrs}>{body}</x:row>"


def pad(cells, width, style):
    """把一行补齐到 width 列（用色带样式填充空列）"""
    have = {c for c, _, _, _ in cells}
    out = list(cells)
    for c in range(1, width + 1):
        if c not in have:
            out.append((c, style, None, False))
    return sorted(out, key=lambda x: x[0])


# ============================================================ 各表生成

def sheet_head(title, tab_color, cols_xml, ncols, freeze=True):
    pane = ('<x:pane ySplit="4" topLeftCell="A5" activePane="bottomLeft" state="frozen" />'
            if freeze else "")
    return ('<?xml version="1.0" encoding="utf-8"?>'
            '<x:worksheet xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<x:sheetPr><x:tabColor rgb="{tab_color}" /></x:sheetPr>'
            '<x:sheetViews><x:sheetView showGridLines="0" workbookViewId="0">'
            f'{pane}</x:sheetView></x:sheetViews>'
            '<x:sheetFormatPr defaultRowHeight="15" />'
            f'<x:cols>{cols_xml}</x:cols><x:sheetData>'
            + row_xml(2, pad([(1, S_TITLE, title, False)], ncols, S_BAND))
            + row_xml(3, [(c, S_STRIPE, None, False) for c in range(1, ncols + 1)], stripe=True)
            + row_xml(4, [(c, S_BAND, None, False) for c in range(1, ncols + 1)]))


def table_head(r, headers, ncols):
    """表头行：第一列 s11，最后一列 s12，中间 s25"""
    cells = []
    for i, h in enumerate(headers, start=1):
        s = S_H1 if i == 1 else (S_HL if i == ncols else S_HM)
        cells.append((i, s, h, False))
    return row_xml(r, pad(cells, ncols, S_HM), height=30)


def build_overview(tab, cols_xml):
    n = 8
    xml = sheet_head("物料交付与验收总览", tab, cols_xml, n, freeze=False)
    left = [
        ("项目名称", "社区服务信息主视觉设计（适配 D01–D15 共 15 类分支）"),
        ("交付版本", "v1.2（v1.0 物料单 + 流程图阶段产物 + 中英双语 × 双载体规格）"),
        ("计划交付日期", ""),
        ("总负责人", ""),
        ("备注", "本表以“14 个节点 + 5 个人工判断点”的工作流程为准；海报交付规格：中英双语两版 × （屏幕版 4:5 + A3 打印版）；改动留痕见「补充说明」表"),
    ]
    n_must = sum(1 for row in DELIVERY if row[0] == "必需")
    right = [
        ("必需交付物（按文件计）", n_must),
        ("全部交付物", len(DELIVERY)),
        ("已触发的场景追加项", 0),
        ("成品规格检查", len(SPEC)),
        ("流程阶段产物", len(STAGES)),
    ]
    r = 5
    xml += table_head(r, ["项目字段", "填写内容", "", "指标", "总数", "已完成/通过", "完成率", "待处理"], n)
    r += 1
    for i, (k, v) in enumerate(left):
        last = (i == len(left) - 1)
        cells = [(1, S_BODY_L if last else S_BODY, k, False),
                 (2, S_BODY_L if last else S_BODY, v, False),
                 (3, S_BAND, None, False)]
        if i < len(right):
            mk, mv = right[i]
            cells += [(4, S_BODY_L if last else S_BODY, mk, False),
                      (5, S_CTR_L if last else S_CTR, mv, True),
                      (6, S_CTR_L if last else S_CTR, 0, True),
                      (7, S_CTR_L if last else S_CTR, 0, True),
                      (8, S_CTR_L if last else S_CTR, mv, True)]
        else:
            cells += [(c, S_BAND, None, False) for c in (4, 5, 6, 7, 8)]
        xml += row_xml(r, pad(cells, n, S_BAND))
        r += 1
    # Gate 状态块
    r += 1
    xml += row_xml(r, pad([(4, S_H1, "Gate状态", False), (5, S_HM, "总数", False),
                           (6, S_HM, "已通过", False), (7, S_HL, "待处理", False)], n, S_BAND), height=30)
    r += 1
    xml += row_xml(r, pad([(4, S_BODY_L, f"Gate 1–{len(GATES)}", False), (5, S_CTR_L, len(GATES), True),
                           (6, S_CTR_L, 0, True), (7, S_CTR_L, 5, True)], n, S_BAND))
    # 使用说明
    r += 1
    xml += row_xml(r, [(c, S_NOTE, "使用说明", False) for c in range(1, n + 1)])
    notes = [
        "1. 在“交付清单”中填写负责人、期限和状态；必需项缺一不可。",
        "2. 在“场景追加”中先判断是否触发，再跟踪状态；未触发项可标记为不适用。",
        "3. 在“成品规格”中填写实测值，并选择 PASS、FAIL 或豁免；豁免必须写明理由。",
        "4. 五个 Gate 均需记录签字人、时间、提交物、判断依据、结论，以及退回信息与回退目标。",
        "5. 流程阶段产物（intake / fact-table / candidates / 线框 / 合规记录 / Gate 记录）是证据链，"
        "缺一项即视为流程不可追溯；逐项见「流程阶段产物」表。",
        "6. 派生物料（信息卡 / 群消息图 / 导视牌 / 折页）必须先经用户确认再生成，确认记录随包交付。",
        "7. 换主题时先重跑步骤 2 的分类路由并过 Gate 1，不得直接套用上一个主题的内容与配色。",
        "8. 中英双语为必做：每版都要出“屏幕版 4:5 PNG”与“A3 打印版 PDF + PNG”；"
        "A3 版由同一张 4:5 画面等比居中放置，任何拉伸都会在成品规格中被判 FAIL。",
        "9. A3 打印前先做一次 CMYK 软打样与灰度检查（见风险控制表），确认后再定稿。",
    ]
    for i, t in enumerate(notes):
        last = (i == len(notes) - 1)
        xml += row_xml(r + 1 + i, [(c, S_BODY_L if last else S_BODY, t if c == 1 else "", False)
                                   for c in range(1, n + 1)], height=26)
    return xml + "</x:sheetData></x:worksheet>"


def build_delivery(tab, cols_xml):
    n = 9
    xml = sheet_head("物料交付清单", tab, cols_xml, n)
    xml += table_head(4, ["序号", "优先级", "交付物", "文件名/路径", "规格与内容", "状态", "负责人", "期限", "备注"], n)
    r = 5
    for i, (pri, name, path, spec, note) in enumerate(DELIVERY, start=1):
        last = (i == len(DELIVERY))
        xml += row_xml(r, [
            (1, S_CTR_L if last else S_CTR, i, True),
            (2, S_PRI_L if last else S_PRI[pri], pri, False),
            (3, S_BODY_L if last else S_BODY, name, False),
            (4, S_BODY_L if last else S_BODY, path, False),
            (5, S_BODY_L if last else S_BODY, spec, False),
            (6, S_CTR_L if last else S_CTR, "未开始", False),
            (7, S_CTR_L if last else S_CTR, "", False),
            (8, S_LIMIT_L if last else S_LIMIT, "", False),
            (9, S_BODY_L if last else S_BODY, note, False),
        ])
        r += 1
    return xml + "</x:sheetData></x:worksheet>"


def build_extra(tab, cols_xml):
    n = 9
    xml = sheet_head("按场景追加物料", tab, cols_xml, n)
    xml += table_head(4, ["序号", "追加物料", "文件名建议", "触发条件", "验收要求", "是否触发", "状态", "负责人", "备注"], n)
    r = 5
    for i, (name, path, trig, acc, note) in enumerate(EXTRA, start=1):
        last = (i == len(EXTRA))
        xml += row_xml(r, [
            (1, S_CTR_L if last else S_CTR, i, True),
            (2, S_BODY_L if last else S_BODY, name, False),
            (3, S_BODY_L if last else S_BODY, path, False),
            (4, S_BODY_L if last else S_BODY, trig, False),
            (5, S_BODY_L if last else S_BODY, acc, False),
            (6, S_CTR_L if last else S_CTR, "待判断", False),
            (7, S_CTR_L if last else S_CTR, "未开始", False),
            (8, S_CTR_L if last else S_CTR, "", False),
            (9, S_BODY_L if last else S_BODY, note, False),
        ])
        r += 1
    return xml + "</x:sheetData></x:worksheet>"


def build_spec(tab, cols_xml):
    n = 6
    xml = sheet_head("成品文件规格检查", tab, cols_xml, n)
    xml += table_head(4, ["序号", "检查项", "目标值/判定标准", "实测值", "结论", "豁免理由/备注"], n)
    r = 5
    for i, (name, target, note) in enumerate(SPEC, start=1):
        last = (i == len(SPEC))
        xml += row_xml(r, [
            (1, S_CTR_L if last else S_CTR, i, True),
            (2, S_BODY_L if last else S_BODY, name, False),
            (3, S_BODY_L if last else S_BODY, target, False),
            (4, S_BODY_L if last else S_BODY, "", False),
            (5, S_CTR_L if last else S_CTR, "待检查", False),
            (6, S_BODY_L if last else S_BODY, note, False),
        ])
        r += 1
    return xml + "</x:sheetData></x:worksheet>"


def build_gates(tab, cols_xml):
    n = 9
    xml = sheet_head("Gate 1–5 审核记录", tab, cols_xml, n)
    xml += table_head(4, ["Gate", "建议审核重点", "签字人", "时间", "AI提交物", "判断依据",
                          "结论", "退回意见", "回退目标"], n)
    r = 5
    for i, (g, focus, back) in enumerate(GATES, start=1):
        last = (i == len(GATES))
        xml += row_xml(r, [
            (1, S_GATE_L if last else S_GATE, g, False),
            (2, S_BODY_L if last else S_BODY, focus, False),
            (3, S_BODY_L if last else S_BODY, "", False),
            (4, S_GATE_DL if last else S_GATE_D, "", False),
            (5, S_BODY_L if last else S_BODY, "", False),
            (6, S_BODY_L if last else S_BODY, "", False),
            (7, S_CTR_L if last else S_CTR, "待审核", False),
            (8, S_BODY_L if last else S_BODY, "", False),
            (9, S_BODY_L if last else S_BODY, back, False),
        ], height=62)
        r += 1
    return xml + "</x:sheetData></x:worksheet>"


def build_risks(tab, cols_xml):
    n = 4
    xml = sheet_head("重点风险控制", tab, cols_xml, n, freeze=False)
    xml += table_head(4, ["风险", "常见问题", "必做控制", "否决条件"], n)
    r = 5
    for i, (risk, prob, ctrl, veto) in enumerate(RISKS, start=1):
        last = (i == len(RISKS))
        xml += row_xml(r, [
            (1, S_RISK_L if last else S_RISK, risk, False),
            (2, S_BODY_L if last else S_BODY, prob, False),
            (3, S_BODY_L if last else S_BODY, ctrl, False),
            (4, S_BODY_L if last else S_BODY, veto, False),
        ], height=56)
        r += 1
    r += 1
    xml += row_xml(r, [(c, S_NOTE, "说明", False) for c in range(1, n + 1)])
    for i, t in enumerate(RISK_NOTES):
        last = (i == len(RISK_NOTES) - 1)
        xml += row_xml(r + 1 + i, [(1, S_BODY_L if last else S_BODY, t, False)]
                       + [(c, S_BODY_L if last else S_BODY, "", False) for c in range(2, n + 1)],
                       height=34)
    return xml + "</x:sheetData></x:worksheet>"


def build_stages(tab, cols_xml):
    n = 8
    xml = sheet_head("流程阶段产物（按 14 个节点）", tab, cols_xml, n)
    xml += table_head(4, ["序号", "阶段", "节点", "产物", "文件名建议", "验收标准",
                          "对应 Gate / 回退", "是否已列入交付清单"], n)
    r = 5
    for i, (stage, node, art, path, acc, gate, listed) in enumerate(STAGES, start=1):
        last = (i == len(STAGES))
        xml += row_xml(r, [
            (1, S_CTR_L if last else S_CTR, i, True),
            (2, S_BODY_L if last else S_BODY, stage, False),
            (3, S_CTR_L if last else S_CTR, node, False),
            (4, S_BODY_L if last else S_BODY, art, False),
            (5, S_BODY_L if last else S_BODY, path, False),
            (6, S_BODY_L if last else S_BODY, acc, False),
            (7, S_BODY_L if last else S_BODY, gate, False),
            (8, S_BODY_L if last else S_BODY, listed, False),
        ])
        r += 1
    return xml + "</x:sheetData></x:worksheet>"


def build_delta(tab, cols_xml):
    n = 5
    xml = sheet_head("补充说明（v1.1–v1.2）", tab, cols_xml, n)
    xml += table_head(4, ["序号", "补充位置", "补充内容", "为什么补", "依据"], n)
    r = 5
    for i, (where, what, why, basis) in enumerate(DELTA, start=1):
        last = (i == len(DELTA))
        xml += row_xml(r, [
            (1, S_CTR_L if last else S_CTR, i, True),
            (2, S_BODY_L if last else S_BODY, where, False),
            (3, S_BODY_L if last else S_BODY, what, False),
            (4, S_BODY_L if last else S_BODY, why, False),
            (5, S_BODY_L if last else S_BODY, basis, False),
        ])
        r += 1
    return xml + "</x:sheetData></x:worksheet>"


# ============================================================ 打包

CONTENT_TYPES_TAIL = (
    '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml" />'
    '<Override PartName="/xl/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml" />'
    '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml" />'
)


def main():
    src = zipfile.ZipFile(SRC)
    styles = src.read("xl/styles.xml")
    theme = src.read("xl/theme/theme1.xml")
    # 复用 v1.0 的列宽与页签色
    cols_xml, tabs = {}, {}
    for i in range(1, 7):
        x = src.read(f"xl/worksheets/sheet{i}.xml").decode("utf-8")
        cols_xml[i] = re.search(r"<x:cols>.*?</x:cols>", x, re.S).group(0)
        tabs[i] = re.search(r'<x:tabColor rgb="(\w+)"', x).group(1)

    sheets = [
        ("总览", tabs[1], build_overview(tabs[1], cols_xml[1])),
        ("交付清单", tabs[2], build_delivery(tabs[2], cols_xml[2])),
        ("场景追加", tabs[3], build_extra(tabs[3], cols_xml[3])),
        ("成品规格", tabs[4], build_spec(tabs[4], cols_xml[4])),
        ("Gate记录", tabs[5], build_gates(tabs[5], cols_xml[5])),
        ("风险控制", tabs[6], build_risks(tabs[6], cols_xml[6])),
        ("流程阶段产物", tabs[2], build_stages(tabs[2], cols_xml[2])),
        ("补充说明", tabs[3], build_delta(tabs[3], cols_xml[3])),
    ]

    # workbook.xml + rels
    wb_sheets, wb_rels, ct_overrides = [], [], []
    for idx, (name, _tab, _xml) in enumerate(sheets, start=1):
        rid = f"Rsheet{idx}"
        wb_sheets.append(f'<x:sheet name="{esc(name)}" sheetId="{idx}" r:id="{rid}" '
                         f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" />')
        wb_rels.append('<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                       f'Target="/xl/worksheets/sheet{idx}.xml" Id="{rid}" />')
        ct_overrides.append('<Override PartName="/xl/worksheets/sheet%d.xml" '
                            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml" />' % idx)

    workbook = ('<?xml version="1.0" encoding="utf-8"?>'
                '<x:workbook xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<x:sheets>{"".join(wb_sheets)}</x:sheets></x:workbook>')
    wb_rels_xml = ('<?xml version="1.0" encoding="utf-8"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
                   'Target="/xl/styles.xml" Id="Rstyles" />'
                   '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" '
                   'Target="/xl/theme/theme1.xml" Id="Rtheme" />'
                   '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
                   'Target="/xl/sharedStrings.xml" Id="Rsst" />'
                   + "".join(wb_rels) + '</Relationships>')
    rels = ('<?xml version="1.0" encoding="utf-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="/xl/workbook.xml" Id="Rroot" /></Relationships>')
    content_types = ('<?xml version="1.0" encoding="utf-8"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="xml" ContentType="application/xml" />'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />'
                     '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml" />'
                     + CONTENT_TYPES_TAIL + "".join(ct_overrides) + '</Types>')
    shared = ('<?xml version="1.0" encoding="utf-8"?>'
              '<x:sst xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="0" uniqueCount="0" />')

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)
        z.writestr("xl/styles.xml", styles)
        z.writestr("xl/theme/theme1.xml", theme)
        z.writestr("xl/sharedStrings.xml", shared)
        for idx, (_name, _tab, xml) in enumerate(sheets, start=1):
            z.writestr(f"xl/worksheets/sheet{idx}.xml", xml.encode("utf-8"))

    print("已生成：", OUT)
    print(f"工作表 {len(sheets)} 张：", "、".join(s[0] for s in sheets))
    print(f"交付清单 {len(DELIVERY)} 项 ｜ 场景追加 {len(EXTRA)} 项 ｜ 成品规格 {len(SPEC)} 项 "
          f"｜ Gate {len(GATES)} 个 ｜ 风险 {len(RISKS)} 条 ｜ 流程阶段产物 {len(STAGES)} 项 ｜ 补充说明 {len(DELTA)} 条")


if __name__ == "__main__":
    main()
