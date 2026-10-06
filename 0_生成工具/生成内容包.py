#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社区服务信息主视觉设计 · 内容包生成器
=====================================
一份数据源（下面 CLASSES）→ 生成：
  content/<id>/master_zh.txt   中文母本（逐字锁定）
  content/<id>/master_en.txt   英文母本（逐字锁定，已按 07 行数对齐规则压缩）
  content/<id>/theme.yaml      五轴字段 + 槽位 + L2 来源 + 待人类确认 + 骨架专属校验
  references/04-master-copy-tables.md   15 类中英母本总表（自动生成，勿手改）

语言规则（v1.4）：
  受众含 A06（新市民与国际居民）→ 生成 master_en.txt（中英双语）；
  否则→ 只写 master_zh.txt（仅中文）。英文文案始终保留在本文件的数据源里，
  给某类 audience 加上 "A06" 再重跑即可启用。

规则依据：
  references/01-classic-input-taxonomy.md   六类经典输入归类
  references/02-master-copy-rules.md        母本内容法则（含语句逻辑七查）
  references/03-line-parity.md              中英行数对齐（英文字符 ≈ 中文字数 × 2）

用法：
    python3 生成内容包.py          # 生成全部 15 类
    python3 生成内容包.py D01      # 只生成某类（按 domain 前缀匹配）
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
CONTENT = os.path.join(PKG, "content")
REFS = os.path.join(PKG, "references")

CANVAS = """  size_mm: [297, 420]            # 默认 A3 竖版（裁切线内）；用户指定其他尺寸时以其为准
  ratio: "1:1.414"
  bleed_mm: 3
  total_mm: [303, 426]
  px_300dpi: [3508, 4961]        # 成品
  px_300dpi_bleed: [3579, 5032]  # 含出血
  format: [PNG, PDF]             # PNG 供屏幕/微信，PDF 供打印店
  color: sRGB
  transparent: false
  safe_margin_mm: 18
  body_font_min_pt: 26           # 含老年人/残障受众 → 31
  crop_marks: true
  design_units: [1080, 1527]     # 等比基准；每行容量 中文 25 字 / 英文 49 字符"""

# ============================================================ 数据源：15 类
# 每条信息项：(中文标签, 中文文案, 英文标签, 英文文案)
# 英文已按 references/03压缩：字符数 ≈ 中文字数 × 2，行数齐平或最多 +1

CLASSES = [
    dict(
        id="D01_service", domain="D01", field="政务办事与证照",
        title_zh="居住证办理指南", title_en="Residence Permit Application Guide",
        org_zh="社区事务受理服务中心", org_en="Community Service Center",
        function="S2", skeleton="S2（步骤流程型）", audiences=["A01", "A06"], timeliness="T1",
        authority="L2", phone="400-123-2021",
        sites_zh="社区事务受理服务中心 3 号窗口", sites_en="Window 3, Community Service Center",
        hours_zh="周一至周五 9:00-17:00", hours_en="Mon-Fri 9:00-17:00",
        items=[
            ("机构标识", "社区事务受理服务中心", "Organisation", "Community Service Center"),
            ("主标题", "居住证办理指南", "Title", "Residence Permit Application Guide"),
            ("触发提示", "在本社区居住登记满半年的居民，可申请居住证。", "Trigger notice",
             "Registered here six months? You can apply."),
            ("服务对象", "非本市户籍居民、新就业群体和随迁家属均可申请。", "Audience",
             "Open to non-local residents and their families."),
            ("步骤 1", "携带身份证和居住证明到受理窗口登记。", "Step 1",
             "Register at the window with ID and address proof."),
            ("步骤 2", "现场采集人像并填写申请表。", "Step 2",
             "Have your photo taken and fill in the form."),
            ("步骤 3", "材料齐全后 15 个工作日内制证。", "Step 3",
             "Card issued within 15 working days."),
            ("步骤 4", "收到短信通知后凭回执领证。", "Step 4",
             "Collect with your receipt after the SMS notice."),
            ("注意事项", "材料不齐可先受理，补正后继续办理。", "Precautions",
             "Missing documents? You can supplement later."),
            ("时间地点", "受理窗口：社区事务受理服务中心 3 号窗口。周一至周五 9:00-17:00。",
             "Time and place", "Service window: Window 3, Community Service Center. Mon-Fri 9:00-17:00."),
            ("咨询电话", "咨询电话：400-123-2021", "Information line", "Information line: 400-123-2021"),
        ],
        sources=[("步骤 3 制证时限", "居住证办理法定时限（各地略有差异，须按本市口径核对）", "L2")],
        needs_human=["本市居住登记满半年的起算口径", "制证时限是否为 15 个工作日", "窗口号与办公时间",
                     "是否支持线上预审", "材料清单是否含居住证明的具体形式"],
        checks=["S2：步骤必须动词开头、等宽编号，顺序不可打乱", "正文 ≥34px；含 A06 新市民 → 关键信息配英文或图标",
                "母本 11 项 100% 命中；电话两版一致"],
    ),
    dict(
        id="D02_relief", domain="D02", field="社会保障与民政救助",
        title_zh="临时救助申请指南", title_en="Temporary Assistance Application Guide",
        org_zh="社区民政服务站", org_en="Community Civil Affairs Service Station",
        function="S3", skeleton="S3（清单条目型）+ S4 辅助", audiences=["A01", "A02"], timeliness="T1",
        authority="L2", phone="400-123-2022",
        sites_zh="社区民政服务站 1 号窗口", sites_en="Window 1, Community Civil Affairs Service Station",
        hours_zh="周一至周五 9:00-17:00", hours_en="Mon-Fri 9:00-17:00",
        items=[
            ("机构标识", "社区民政服务站", "Organisation", "Community Civil Affairs Service Station"),
            ("主标题", "临时救助申请指南", "Title", "Temporary Assistance Application Guide"),
            ("触发提示", "因突发事件导致基本生活困难的居民，可申请临时救助。", "Trigger notice",
             "Sudden hardship? Apply for temporary assistance."),
            ("服务对象", "低保边缘家庭、突发重病或意外事故家庭。", "Audience",
             "Low-income, sudden illness or accident families."),
            ("材料 1", "身份证、户口簿和家庭收入证明。", "Document 1",
             "ID, household register, and income proof."),
            ("材料 2", "医疗票据、事故证明或相关佐证材料。", "Document 2",
             "Medical bills, accident reports, or other evidence."),
            ("材料 3", "本人银行卡复印件（用于发放救助金）。", "Document 3",
             "Bank card copy for the assistance payment."),
            ("办理流程", "提交申请 → 社区初审 → 街道审核 → 公示后发放。", "Process",
             "Apply, community review, street approval, payment."),
            ("注意事项", "救助金额按家庭困难程度核定，非固定标准。", "Precautions",
             "Amount assessed by need; no fixed standard."),
            ("时间地点", "受理窗口：社区民政服务站 1 号窗口。周一至周五 9:00-17:00。",
             "Time and place", "Window 1, Civil Affairs Service Station. Mon-Fri 9:00-17:00."),
            ("咨询电话", "咨询电话：400-123-2022", "Information line", "Information line: 400-123-2022"),
        ],
        sources=[("救助范围与流程", "《社会救助暂行办法》临时救助条款（具体标准由本市规定）", "L2")],
        needs_human=["本市临时救助的金额标准与分档", "公示天数", "审核时限", "是否需要家庭经济状况核对授权书",
                     "窗口号与办公时间"],
        checks=["S3：材料条目必须等宽、图标一一对应", "涉及资格判定 → 措辞逐字，不得改写", "金额不得写具体数字（未由人类提供前）"],
    ),
    dict(
        id="D03_elder", domain="D03", field="养老与为老服务",
        title_zh="助餐服务与探访关爱", title_en="Meal Service and Home Visits",
        org_zh="社区为老服务中心", org_en="Community Senior Service Center",
        function="S1", skeleton="S1（时间地点公告型）+ S9 求助联络", audiences=["A02"], timeliness="T1",
        authority="L3", phone="400-123-2023",
        sites_zh="社区服务中心一层助餐点", sites_en="Meal point, ground floor, Community Service Center",
        hours_zh="每日 11:00-12:30", hours_en="daily 11:00-12:30",
        items=[
            ("机构标识", "社区为老服务中心", "Organisation", "Community Senior Service Center"),
            ("主标题", "助餐服务与探访关爱", "Title", "Meal Service and Home Visits"),
            ("触发提示", "社区为 60 岁以上居民提供助餐与探访服务。", "Trigger notice",
             "Meals and visits for residents 60 and over."),
            ("服务对象", "独居、高龄和行动不便的老年人优先。", "Audience",
             "Priority: alone, advanced age, limited mobility."),
            ("服务 1", "助餐点提供午餐，可堂食或送餐上门。", "Service 1",
             "Lunch at the meal point, dine in or delivered home."),
            ("服务 2", "每周一次上门探访，可代购代办。", "Service 2",
             "A home visit each week; errands can be arranged."),
            ("行动提示", "首次使用请携带身份证到中心登记。", "Action",
             "Register at the center with your ID the first time."),
            ("求助方式", "如连续两天联系不上，请通知中心上门查看。", "Seek help",
             "If unreachable for two days, the center will visit."),
            ("时间地点", "助餐点：社区服务中心一层。每日 11:00-12:30 供餐。",
             "Time and place", "Meal point: Community Service Center, ground floor. Daily 11:00-12:30."),
            ("咨询电话", "咨询电话：400-123-2023", "Information line", "Information line: 400-123-2023"),
        ],
        sources=[("助餐与探访服务内容", "社区居家养老服务规范（服务频次以本街道实际为准）", "L2"),
                 ("送餐上门", "为老助餐服务通行做法", "L2")],
        needs_human=["服务对象年龄门槛是否为 60 岁", "送餐上门的范围与是否收费", "探访频次（每周/每两周）",
                     "是否提供代购代办的费用结算方式", "助餐点实际位置与供餐时间"],
        checks=["受众为 A02 老年人 → 正文 ≥40px、对比度 ≥7:1、电话特大", "S9：电话号码为画面最强视觉元素且无遮挡",
                "涉及收费必须由人类提供，不得写“免费”"],
    ),
    dict(
        id="D04_health", domain="D04", field="医疗卫生与健康",
        title_zh="流感疫苗接种与健康防护", title_en="Flu Vaccination and Health Protection",
        org_zh="社区健康与服务中心", org_en="Community Health and Service Center",
        function="S1", skeleton="S1（时间地点公告型）", audiences=["A02", "A04", "A01"], timeliness="T2",
        authority="L2", phone="400-123-2026",
        sites_zh="社区卫生服务站、东门驿站临时接种点",
        sites_en="Community Health Station; East Gate Station (temporary)",
        hours_zh="每周一至周六 9:00-16:00", hours_en="Mon-Sat 9:00-16:00",
        items=[
            ("机构标识", "社区健康与服务中心", "Organisation", "Community Health and Service Center"),
            ("主标题", "流感疫苗接种与健康防护", "Title", "Flu Vaccination and Health Protection"),
            ("触发提示", "流感高发季期间，请及时接种疫苗并做好日常防护。", "Trigger notice",
             "Flu season: get vaccinated promptly, keep daily protection."),
            ("服务对象", "老年人、儿童、孕产妇和慢性病患者建议优先接种。", "Audience",
             "Older adults, children, pregnant women, and chronic patients first."),
            ("行动 1", "接种前请如实告知健康状况和过敏史。", "Action 1",
             "Tell staff your health conditions and allergies."),
            ("行动 2", "携带身份证或医保卡前往接种点。", "Action 2",
             "Bring ID or insurance card to the site."),
            ("行动 3", "接种后请留观 30 分钟。", "Action 3", "Stay 30 minutes for observation."),
            ("行动 4", "勤洗手、常通风，咳嗽时遮掩口鼻。", "Action 4",
             "Wash hands often, air rooms, and cover coughs."),
            ("行动 5", "如出现持续发热或明显不适，请及时就医并告知接种情况。", "Action 5",
             "If a fever persists or you feel unwell, seek care and report your vaccination."),
            ("时间地点", "接种点：社区卫生服务站、东门驿站临时接种点。每周一至周六 9:00-16:00 开放。",
             "Time and place", "Sites: Community Health Station; East Gate Station (temporary). Mon-Sat 9:00-16:00."),
            ("咨询电话", "咨询电话：400-123-2026", "Information line", "Information line: 400-123-2026"),
        ],
        sources=[("接种后留观 30 分钟", "国家卫生健康委 / 中国疾控中心 预防接种科普口径", "L2"),
                 ("优先接种人群", "国家卫生健康委 流感疫苗接种建议", "L2"),
                 ("接种前如实告知健康状况", "预防接种工作规范（禁忌判定由医护人员负责）", "L2"),
                 ("勤洗手、常通风、咳嗽遮掩口鼻", "中国疾控中心 呼吸道传染病健康科普", "L2")],
        needs_human=["接种点本季是否真实开放", "开放时间是否含节假日", "咨询电话是否可对外公开",
                     "疫苗种类与费用口径（严禁自行写“免费”）", "发布日期与有效期（T2 必填下次日期）"],
        checks=["S1：时间与地点为画面最高优先级", "受众含 A02 → 正文 ≥40px、对比度 ≥7:1",
                "不替医护做医学判断；“发热”限定为“持续发热”", "不得出现诊断 / 治疗建议与效果承诺"],
    ),
    dict(
        id="D05_child", domain="D05", field="育儿与青少年",
        title_zh="暑期儿童安全提示", title_en="Summer Child Safety Notice",
        org_zh="社区儿童之家", org_en="Community Children's Center",
        function="S5", skeleton="S5（警示禁止型）+ S2 辅助", audiences=["A03", "A01"], timeliness="T2",
        authority="L2", phone="400-123-2025",
        sites_zh="社区服务中心二层儿童之家", sites_en="Children's Center, 2nd floor, Community Service Center",
        hours_zh="每周一至周六 9:00-17:00", hours_en="Mon-Sat 9:00-17:00",
        items=[
            ("机构标识", "社区儿童之家", "Organisation", "Community Children's Center"),
            ("主标题", "暑期儿童安全提示", "Title", "Summer Child Safety Notice"),
            ("禁止 1", "请勿让儿童独自到河道、水塘边玩耍。", "Prohibition 1",
             "Do not let children play alone by rivers or ponds."),
            ("正确做法", "请到社区儿童之家参加有看护的活动。", "Correct practice",
             "Join supervised activities at the Children's Center."),
            ("禁止 2", "请勿将儿童单独留在车内或家中。", "Prohibition 2",
             "Do not leave children alone in cars or at home."),
            ("行动提示", "教会孩子记住家长电话和 110 报警。", "Action",
             "Teach children your number and 110 for emergencies."),
            ("求助方式", "发现儿童走失或遇险，请立即拨打 110。", "Seek help",
             "If a child is lost or in danger, call 110."),
            ("时间地点", "活动地点：社区服务中心二层儿童之家。每周一至周六 9:00-17:00。",
             "Time and place", "Children's Center, 2nd floor, Service Center. Mon-Sat 9:00-17:00."),
            ("咨询电话", "咨询电话：400-123-2025", "Information line", "Information line: 400-123-2025"),
        ],
        sources=[("防溺水与监护提示", "教育部 中小学生防溺水安全提示（六不）", "L2"),
                 ("110 报警", "公安机关报警电话（公共号码）", "L2")],
        needs_human=["儿童之家暑期是否开放及实际时段", "是否提供托管与看护（决定措辞强度）",
                     "附近水域与危险点的正式名称", "是否需要家长签署安全承诺书"],
        checks=["S5：禁止项 [03][05] 与正确做法 [04] 必须成对出现", "受众含 A03 儿童 → 图形化、禁惊悚画面",
                "110 为紧急号码，不得与非紧急事项同句"],
    ),
    dict(
        id="D06_job", domain="D06", field="就业与社保",
        title_zh="社区招聘会与技能培训", title_en="Job Fair and Skills Training",
        org_zh="社区就业服务站", org_en="Community Employment Service Station",
        function="S1", skeleton="S1（时间地点公告型）+ S3 清单", audiences=["A01", "A07"], timeliness="T2",
        authority="L2", phone="400-123-2027",
        sites_zh="社区服务中心多功能厅", sites_en="Multi-purpose Hall, Community Service Center",
        hours_zh="每月第一个周六 9:00-12:00", hours_en="first Saturday monthly, 9:00-12:00",
        items=[
            ("机构标识", "社区就业服务站", "Organisation", "Community Employment Service Station"),
            ("主标题", "社区招聘会与技能培训", "Title", "Job Fair and Skills Training"),
            ("触发提示", "社区每月举办一场招聘会与免费技能培训。", "Trigger notice",
             "A job fair and free training are held monthly."),
            ("服务对象", "失业人员、高校毕业生和新就业群体均可参加。", "Audience",
             "Unemployed, graduates, new workers: all welcome."),
            ("服务 1", "现场提供 20 家企业岗位与简历指导。", "Service 1",
             "20 employers on site, plus resume coaching."),
            ("服务 2", "培训含电工、家政、护理和电商课程。", "Service 2",
             "Training: electrical, home care, nursing, e-commerce."),
            ("行动提示", "携带身份证和简历到场登记即可参加。", "Action",
             "Bring ID and a resume; register on site."),
            ("注意事项", "培训名额有限，请提前电话预约。", "Precautions",
             "Training seats are limited; book by phone."),
            ("时间地点", "地点：社区服务中心多功能厅。每月第一个周六 9:00-12:00。",
             "Time and place", "Multi-purpose Hall, Service Center. First Saturday monthly, 9:00-12:00."),
            ("咨询电话", "咨询电话：400-123-2027", "Information line", "Information line: 400-123-2027"),
        ],
        sources=[("招聘与培训服务", "公共就业服务通行做法（场次与课程以本街道实际为准）", "L2")],
        needs_human=["企业数量与岗位真实性（不得虚报）", "培训课程名称与是否发证", "每月场次的具体日期",
                     "是否收取押金或材料费（若有须写明）"],
        checks=["S1：时间地点为最高优先级；含 A07 户外劳动者 → 手机竖屏可读",
                "“免费”仅限培训且需人类确认，不得扩展到其他服务"],
    ),
    dict(
        id="D07_lift", domain="D07", field="住房与物业",
        title_zh="既有住宅加装电梯流程", title_en="Adding a Lift to an Existing Building",
        org_zh="社区物业服务中心", org_en="Community Property Service Center",
        function="S2", skeleton="S2（步骤流程型）+ S4 辅助", audiences=["A01", "A02"], timeliness="T3",
        authority="L3", phone="400-123-2028",
        sites_zh="社区物业服务中心", sites_en="Community Property Service Center",
        hours_zh="周一至周五 9:00-17:00", hours_en="Mon-Fri 9:00-17:00",
        items=[
            ("机构标识", "社区物业服务中心", "Organisation", "Community Property Service Center"),
            ("主标题", "既有住宅加装电梯流程", "Title", "Adding a Lift to an Existing Building"),
            ("触发提示", "本单元三分之二以上业主同意即可启动申请。", "Trigger notice",
             "Start when two-thirds of owners in the unit agree."),
            ("步骤 1", "本单元业主协商并签署同意书。", "Step 1", "Owners discuss and sign the consent form."),
            ("步骤 2", "向社区提交申请与业主签字材料。", "Step 2", "Submit the application and signed forms."),
            ("步骤 3", "街道组织公示，为期 10 天。", "Step 3", "The street office posts it for 10 days."),
            ("步骤 4", "公示无异议后办理规划与施工手续。", "Step 4",
             "With no objection, planning and works proceed."),
            ("注意事项", "费用分摊比例由业主协商确定，社区不指定。", "Precautions",
             "Cost sharing is agreed by owners, not set by us."),
            ("注意事项 2", "低层住户意见须记录并说明处理方式。", "Note",
             "Record lower-floor concerns and the response."),
            ("时间地点", "受理地点：社区物业服务中心。周一至周五 9:00-17:00。",
             "Time and place", "Location: Community Property Service Center. Mon-Fri 9:00-17:00."),
            ("咨询电话", "咨询电话：400-123-2028", "Information line", "Information line: 400-123-2028"),
        ],
        sources=[("业主同意比例与公示要求", "《民法典》关于既有住宅加装电梯的表决与公示规定（比例以本市细则为准）", "L2")],
        needs_human=["本市同意比例的准确表述（三分之二 / 双三分之二）", "公示天数是否为 10 天",
                     "费用分摊是否另有政府补贴", "低层住户补偿机制是否存在"],
        checks=["S2：步骤顺序不可打乱；涉及利益冲突 → 措辞须经 Gate 2 逐字核对", "不得承诺“政府补贴”“免费安装”"],
    ),
    dict(
        id="D08_waste", domain="D08", field="环境与环卫",
        title_zh="生活垃圾分类与定时投放", title_en="Household Waste Sorting and Scheduled Drop-off",
        org_zh="社区环境服务中心", org_en="Community Environmental Service Center",
        function="S4", skeleton="S4（分类对比型）", audiences=["A01", "A02"], timeliness="T1",
        authority="L2", phone="400-123-2031",
        sites_zh="1 号点、2 号点、3 号点", sites_en="No.1, No.2, and No.3",
        hours_zh="每日 7:00-9:00、18:00-20:00", hours_en="daily 7:00-9:00 and 18:00-20:00",
        items=[
            ("机构标识", "社区环境服务中心", "Organisation", "Community Environmental Service Center"),
            ("主标题", "生活垃圾分类与定时投放", "Title",
             "Household Waste Sorting and Scheduled Drop-off"),
            ("触发提示", "本社区实行生活垃圾定时定点投放，请按分类标准投放。", "Trigger notice",
             "Sorted waste only, at fixed points and hours."),
            ("分类 1 · 可回收物", "可回收物：纸张、塑料瓶、金属和玻璃。", "Category 1 - Recyclables",
             "Recyclables: paper, plastic bottles, metal, glass."),
            ("分类 2 · 厨余垃圾", "厨余垃圾：剩菜剩饭、果皮和菜叶。", "Category 2 - Food waste",
             "Food waste: leftovers, peels, vegetable leaves."),
            ("分类 3 · 有害垃圾", "有害垃圾：电池、灯管、药品和油漆。", "Category 3 - Hazardous waste",
             "Hazardous waste: batteries, tubes, medicines, paint."),
            ("分类 4 · 其他垃圾", "其他垃圾：纸巾、烟头和陶瓷碎片。", "Category 4 - Other waste",
             "Other waste: tissues, cigarette butts, ceramics."),
            ("注意事项", "请勿将有害垃圾混入其他垃圾，也请勿在非投放时段堆放。", "Precautions",
             "Do not mix hazardous with other waste; do not leave bags outside drop-off hours."),
            ("注意事项 · 特殊垃圾", "大件垃圾与装修垃圾请勿投入分类桶，请联系环境服务中心。",
             "Precautions - special waste",
             "Do not put bulky or construction waste in sorting bins; contact the service center."),
            ("时间地点", "投放点：1 号点、2 号点、3 号点（位置见点位图）。每日 7:00-9:00、18:00-20:00 开放。",
             "Time and place", "Drop-off points: No.1, No.2, No.3 (see the site map). Daily 7:00-9:00 and 18:00-20:00."),
            ("咨询电话", "咨询电话：400-123-2031", "Information line", "Information line: 400-123-2031"),
        ],
        sources=[("四分类名称与举例", "生活垃圾分类国家标准与本市分类目录（用词须按本市口径替换）", "L2"),
                 ("有害垃圾不得混投", "城市管理部门分类投放要求", "L2"),
                 ("大件垃圾与装修垃圾不得投入分类桶", "城市管理部门大件垃圾管理要求", "L2")],
        needs_human=["本市分类名称与色标（不得自创）", "投放点数量与正式名称；是否需要并提供点位图",
                     "时段是否含节假日", "大件与装修垃圾的正式投放方式"],
        checks=["S4：四个分区并列、每区一色 + 一图标；分类色须与本市标准一致",
                "受众含 A02 → 正文 ≥40px、对比度 ≥7:1；不得仅靠颜色区分四类"],
    ),
    dict(
        id="D09_safety", domain="D09", field="安全与应急",
        title_zh="电动自行车充电安全提示", title_en="E-Bike Charging Safety Notice",
        org_zh="社区安全服务站", org_en="Community Safety Service Station",
        function="S5", skeleton="S5（警示禁止型）+ S2 辅助", audiences=["A01", "A07"], timeliness="T1",
        authority="L1", phone="400-123-2032",
        sites_zh="社区服务中心东侧车棚、东门驿站北侧",
        sites_en="East Shed, Community Service Center; East Gate Station north",
        hours_zh="每日 6:00-23:00", hours_en="Daily 6:00-23:00",
        items=[
            ("机构标识", "社区安全服务站", "Organisation", "Community Safety Service Station"),
            ("主标题", "电动自行车充电安全提示", "Title", "E-Bike Charging Safety Notice"),
            ("禁止 1 · 红线", "为防范火灾，请勿在楼道、门厅等公共区域为电动自行车充电。",
             "Prohibition 1 - red line", "Fire risk: no e-bike charging in shared areas."),
            ("正确做法", "请到集中充电点充电，并使用原装充电器。", "Correct practice",
             "Use charging points and the original charger."),
            ("禁止 2", "请勿占用消防通道停放或充电。", "Prohibition 2",
             "Do not park or charge in fire lanes."),
            ("禁止 3", "请勿将电池带入室内充电或过夜充电。", "Prohibition 3",
             "Do not charge batteries indoors or overnight."),
            ("求助 · 火情", "发现火情，请立即拨打 119，并通知物业协助处置。", "Seek help - fire",
             "Fire: call 119, then notify property management."),
            ("求助 · 违规充电", "发现违规充电，请联系物业或社区安全服务站。", "Seek help - unsafe charging",
             "Unsafe charging: report to property management or the safety station."),
            ("时间地点", "集中充电点：社区服务中心东侧车棚、东门驿站北侧。每日 6:00-23:00 开放。",
             "Time and place", "Charging: East Shed (Service Center), East Gate Station north. Daily 6:00-23:00."),
            ("咨询电话", "咨询电话：400-123-2032", "Information line", "Information line: 400-123-2032"),
        ],
        sources=[("禁止在楼道、门厅等公共区域充电", "国家消防救援局 / 应急管理部 电动自行车火灾防范科普", "L2"),
                 ("禁止占用消防通道", "《消防法》疏散通道、安全出口不得占用的规定", "L2"),
                 ("禁止室内充电与过夜充电", "国家消防救援局 电池充电安全提示", "L2"),
                 ("使用原装充电器", "市场监管部门 / 消防救援局 充电器安全提示", "L2"),
                 ("火情拨 119、违规充电联系物业", "119 为火警专线；非紧急事项应联系物业或社区服务站", "L2")],
        needs_human=["集中充电点是否真实可用", "充电收费方式（严禁自行写“免费”）", "物业联系方式与值守时间",
                     "是否需标注发布单位与依据文号（L1 建议标注）"],
        checks=["S5：禁止项 [03][05][06] 与正确做法 [04] 必须成对出现，缺一半即 FAIL",
                "红色面积须人工确认，禁止整张变红墙", "紧急与非紧急必须分句：119 不得与非紧急对象同句"],
    ),
    dict(
        id="D10_legal", domain="D10", field="法律与调解",
        title_zh="法律援助与人民调解", title_en="Legal Aid and Mediation",
        org_zh="社区法律服务站", org_en="Community Legal Service Station",
        function="S3", skeleton="S3（清单条目型）+ S9 求助联络", audiences=["A01"], timeliness="T1",
        authority="L2", phone="400-123-2033",
        sites_zh="社区服务中心 105 室", sites_en="Room 105, Community Service Center",
        hours_zh="周一至周五 9:00-17:00", hours_en="Mon-Fri 9:00-17:00",
        items=[
            ("机构标识", "社区法律服务站", "Organisation", "Community Legal Service Station"),
            ("主标题", "法律援助与人民调解", "Title", "Legal Aid and Mediation"),
            ("触发提示", "遇到纠纷或权益受损，可先来社区申请调解。", "Trigger notice",
             "Disputes or rights issues? Start with mediation."),
            ("服务 1", "每周三下午有律师现场提供免费咨询。", "Service 1",
             "A lawyer gives free advice on Wednesday afternoons."),
            ("服务 2", "人民调解不收费，双方自愿参加。", "Service 2",
             "Mediation is free and voluntary for both sides."),
            ("行动提示", "携带身份证和相关证据材料到场。", "Action", "Bring your ID and any evidence."),
            ("注意事项", "调解不成可引导申请法律援助或诉讼。", "Precautions",
             "If mediation fails, legal aid or court is an option."),
            ("求助方式", "遭遇家暴或人身危险，请立即拨打 110。", "Seek help",
             "In domestic violence or danger, call 110 at once."),
            ("时间地点", "服务点：社区服务中心 105 室。周一至周五 9:00-17:00。",
             "Time and place", "Service point: Room 105, Community Service Center. Mon-Fri 9:00-17:00."),
            ("咨询电话", "咨询电话：400-123-2033", "Information line", "Information line: 400-123-2033"),
        ],
        sources=[("人民调解不收费", "《人民调解法》关于人民调解不收取费用的规定", "L2"),
                 ("律师现场咨询", "公共法律服务通行做法（值守时间以本街道实际为准）", "L2"),
                 ("家暴报警", "《反家庭暴力法》与 110 报警（公共号码）", "L2")],
        needs_human=["律师值班的准确时间与频次", "是否可代理诉讼", "法律援助的经济困难标准",
                     "服务点房间号与办公时间"],
        checks=["措辞法律风险高 → 不得给出实体法律结论", "S9：电话号码为主视觉且无遮挡",
                "110 为紧急号码，不得与非紧急事项同句"],
    ),
    dict(
        id="D11_culture", domain="D11", field="文化与体育",
        title_zh="图书室开放与本月活动", title_en="Library Hours and This Month's Events",
        org_zh="社区文化活动中心", org_en="Community Culture Center",
        function="S1", skeleton="S1（时间地点公告型）+ S6 招募", audiences=["A01"], timeliness="T2",
        authority="L3", phone="400-123-2034",
        sites_zh="社区服务中心三层图书室", sites_en="Library, 3rd floor, Community Service Center",
        hours_zh="周二至周日 9:00-20:00", hours_en="Tue-Sun 9:00-20:00",
        items=[
            ("机构标识", "社区文化活动中心", "Organisation", "Community Culture Center"),
            ("主标题", "图书室开放与本月活动", "Title", "Library Hours and This Month's Events"),
            ("触发提示", "图书室免费开放，凭身份证即可办证借阅。", "Trigger notice",
             "Free library; register with ID to borrow."),
            ("服务内容", "现有藏书 6000 册，含少儿绘本与报刊。", "Service",
             "6,000 books, including children's titles and papers."),
            ("本月活动", "本月活动：亲子读书会与公益电影。", "This month",
             "This month: parent-child reading and a free film."),
            ("行动提示", "活动需提前一天在服务台报名。", "Action",
             "Sign up at the desk one day in advance."),
            ("注意事项", "请勿携带食品入内，保持安静。", "Precautions", "No food inside; please keep quiet."),
            ("时间地点", "开放时间：周二至周日 9:00-20:00。地点：社区服务中心三层。",
             "Time and place", "Hours and place: Library, 3rd floor, Service Center. Tue-Sun 9:00-20:00."),
            ("咨询电话", "咨询电话：400-123-2034", "Information line", "Information line: 400-123-2034"),
        ],
        sources=[("免费开放与办证借阅", "公共图书馆免费开放通行做法（借阅规则以本馆实际为准）", "L2")],
        needs_human=["藏书数量与是否含少儿绘本", "本月活动的正式名称与时间", "是否需押金或办证费用",
                     "开放时间是否含节假日"],
        checks=["S1：开放时间与地点为最高优先级", "活动名称不得虚构；无活动时删该条而不是编"],
    ),
    dict(
        id="D12_volunteer", domain="D12", field="志愿与公益",
        title_zh="社区志愿者招募", title_en="Community Volunteers Wanted",
        org_zh="社区志愿服务站", org_en="Community Volunteer Service Station",
        function="S6", skeleton="S6（招募邀约型）+ S3 清单", audiences=["A01"], timeliness="T2",
        authority="L4", phone="400-123-2035",
        sites_zh="社区服务中心 101 室", sites_en="Room 101, Community Service Center",
        hours_zh="周一至周五 9:00-17:00", hours_en="Mon-Fri 9:00-17:00",
        items=[
            ("机构标识", "社区志愿服务站", "Organisation", "Community Volunteer Service Station"),
            ("主标题", "社区志愿者招募", "Title", "Community Volunteers Wanted"),
            ("触发提示", "社区长期招募志愿者，服务时长可累计。", "Trigger notice",
             "We recruit volunteers year-round; hours are recorded."),
            ("服务对象", "年满 16 周岁、身体健康即可报名。", "Audience",
             "Anyone aged 16 or over in good health may apply."),
            ("岗位 1", "助老岗：每周一次探访与代购代办。", "Role 1",
             "Elder support: weekly visits and errands."),
            ("岗位 2", "环保岗：每月一次社区清洁与分类引导。", "Role 2",
             "Green team: monthly clean-up and sorting guidance."),
            ("行动提示", "扫码或到服务站填写报名表即可。", "Action",
             "Scan the code or sign up at the station."),
            ("注意事项", "报名后需参加一次岗前培训。", "Precautions",
             "One training session is required after signing up."),
            ("时间地点", "服务站开放：周一至周五 9:00-17:00。地址：社区服务中心 101 室。",
             "Time and place", "Station hours: Room 101, Service Center. Mon-Fri 9:00-17:00."),
            ("咨询电话", "咨询电话：400-123-2035", "Information line", "Information line: 400-123-2035"),
        ],
        sources=[("志愿服务时长记录", "志愿服务记录与证明出具办法（时长以平台记录为准）", "L2")],
        needs_human=["是否提供志愿服务证明与保险", "岗位实际需求与服务时段", "报名二维码是否可用",
                     "年龄门槛是否为 16 周岁"],
        checks=["L4 社区自治 → 语气可亲和，但不得冒充政府公告", "S6：报名方式与截止时间必须显眼"],
    ),
    dict(
        id="D13_meeting", domain="D13", field="邻里自治与公共事务",
        title_zh="业主议事会公告", title_en="Owners' Meeting Notice",
        org_zh="社区居民委员会", org_en="Residents' Committee",
        function="S1", skeleton="S1（时间地点公告型）+ S3 清单", audiences=["A01"], timeliness="T3",
        authority="L4", phone="400-123-2036",
        sites_zh="社区服务中心多功能厅", sites_en="Multi-purpose Hall, Community Service Center",
        hours_zh="本月 20 日 19:00", hours_en="the 20th of this month, 19:00",
        items=[
            ("机构标识", "社区居民委员会", "Organisation", "Residents' Committee"),
            ("主标题", "业主议事会公告", "Title", "Owners' Meeting Notice"),
            ("触发提示", "本小区将于本月召开业主议事会，讨论公共收益使用。", "Trigger notice",
             "A meeting will discuss how common income is used."),
            ("议题", "议题：电梯维保、停车管理与绿化改造。", "Topics",
             "Topics: lift upkeep, parking, greening."),
            ("服务对象", "本小区业主均可参加，凭房产证明入场。", "Audience",
             "Owners may attend with proof of ownership."),
            ("行动提示", "有议题提案请于会前三天提交居委会。", "Action",
             "Submit proposals three days before the meeting."),
            ("注意事项", "会议纪要将在会后七日内在公告栏公示。", "Precautions",
             "Minutes will be posted within seven days."),
            ("异议渠道", "对公示内容有异议，请在公示期内书面反馈。", "Objections",
             "Written objections within the posting period."),
            ("时间地点", "会议时间：本月 20 日 19:00。地点：社区服务中心多功能厅。",
             "Time and place", "Multi-purpose Hall, Service Center. The 20th of this month, 19:00."),
            ("咨询电话", "咨询电话：400-123-2036", "Information line", "Information line: 400-123-2036"),
        ],
        sources=[("业主共同决定事项与公示", "《民法典》业主共同决定与公示要求（具体程序以本小区议事规则为准）", "L2")],
        needs_human=["会议日期与地点（本月 20 日是否准确）", "议题清单是否完整", "公示天数与异议受理方式",
                     "是否需要业主身份核验方式说明"],
        checks=["公示类必须留意见反馈渠道与截止日期（本条已含）", "L4 → 不得使用政府公告的公文口吻",
                "T3 一次性 → 必填具体日期时间"],
    ),
    dict(
        id="D14_inclusive", domain="D14", field="特殊群体与专项服务",
        title_zh="退役军人服务与无障碍服务", title_en="Veteran and Accessibility Services",
        org_zh="社区综合服务站", org_en="Community Integrated Service Station",
        function="S3", skeleton="S3（清单条目型）+ S9 求助联络", audiences=["A05", "A01"], timeliness="T1",
        authority="L2", phone="400-123-2037",
        sites_zh="社区服务中心 1 号窗口", sites_en="Window 1, Community Service Center",
        hours_zh="周一至周五 9:00-17:00", hours_en="Mon-Fri 9:00-17:00",
        items=[
            ("机构标识", "社区综合服务站", "Organisation", "Community Integrated Service Station"),
            ("主标题", "退役军人服务与无障碍服务", "Title", "Veteran and Accessibility Services"),
            ("触发提示", "社区为退役军人和残障居民提供专属服务窗口。", "Trigger notice",
             "Special windows: veterans, residents with disabilities."),
            ("服务 1", "退役军人：优待证办理与就业推荐。", "Service 1",
             "Veterans: preference card and job referrals."),
            ("服务 2", "无障碍：轮椅借用与上门代办服务。", "Service 2",
             "Access: wheelchair loan and home errands."),
            ("服务 3", "提供大字版材料与手语视频指引。", "Service 3",
             "Large-print materials and sign-language videos."),
            ("行动提示", "行动不便可电话预约上门办理。", "Action",
             "Book a home visit by phone if mobility is limited."),
            ("注意事项", "服务不收取任何费用，谨防代办收费。", "Precautions",
             "All services are free; beware of paid agents."),
            ("时间地点", "服务窗口：社区服务中心 1 号窗口。周一至周五 9:00-17:00。",
             "Time and place", "Service window: Window 1, Community Service Center. Mon-Fri 9:00-17:00."),
            ("咨询电话", "咨询电话：400-123-2037", "Information line", "Information line: 400-123-2037"),
        ],
        sources=[("优待证办理", "退役军人事务部门优待证申领通行做法", "L2"),
                 ("无障碍服务", "《无障碍环境建设法》关于社区无障碍服务的要求", "L2")],
        needs_human=["优待证办理是否在本窗口受理", "轮椅借用的押金与归还方式", "手语视频是否存在（无则删该条）",
                     "上门服务的预约时限"],
        checks=["受众含 A05 残障人士 → 正文 ≥40px、对比度 ≥7:1，不得仅靠颜色传递信息",
                "用词须按官方口径，避免标签化表述", "S9：电话为主视觉且无遮挡"],
    ),
    dict(
        id="D15_canteen", domain="D15", field="商业与便民生活",
        title_zh="社区食堂供餐信息", title_en="Community Canteen: Menu and Hours",
        org_zh="社区便民服务点", org_en="Community Convenience Service Point",
        function="S1", skeleton="S1（时间地点公告型）+ S3 清单", audiences=["A01", "A02"], timeliness="T1",
        authority="L5", phone="400-123-2038",
        sites_zh="社区服务中心一层", sites_en="Ground floor, Community Service Center",
        hours_zh="每日 11:00-13:00、17:00-19:00", hours_en="daily 11:00-13:00 and 17:00-19:00",
        items=[
            ("机构标识", "社区便民服务点", "Organisation", "Community Convenience Service Point"),
            ("主标题", "社区食堂供餐信息", "Title", "Community Canteen: Menu and Hours"),
            ("触发提示", "社区食堂提供午餐与晚餐，可堂食或打包。", "Trigger notice",
             "Lunch and dinner are served; eat in or take away."),
            ("服务对象", "60 岁以上居民凭卡享受优惠价。", "Audience",
             "Residents aged 60 and over enjoy a discount."),
            ("供餐 · 午餐", "午餐：四菜一汤，15 元；优惠价 12 元。", "Lunch",
             "Lunch: 4 dishes + soup, 15 yuan (12 with card)."),
            ("供餐 · 晚餐", "晚餐：面食与小炒，10 元起。", "Dinner",
             "Dinner: noodles and stir-fry from 10 yuan."),
            ("行动提示", "首次用餐请到服务台办卡充值。", "Action",
             "Get a card at the desk before your first meal."),
            ("注意事项", "高峰期请错峰用餐，餐具请自助回收。", "Precautions",
             "Avoid peak hours; return your tray yourself."),
            ("时间地点", "供餐时间：每日 11:00-13:00、17:00-19:00。地点：社区服务中心一层。",
             "Time and place", "Ground floor, Service Center. Daily 11:00-13:00 and 17:00-19:00."),
            ("咨询电话", "咨询电话：400-123-2038", "Information line", "Information line: 400-123-2038"),
        ],
        sources=[("老年助餐优惠", "社区老年助餐服务通行做法（价格与优惠以运营方公示为准）", "L2")],
        needs_human=["菜品与价格（示例值，发布前必须替换）", "优惠年龄门槛与办卡押金", "是否提供送餐",
                     "运营方全称与食品经营许可信息"],
        checks=["L5 商业便民 → 严禁使用政务视觉语言（徽标、国标警示色、公文版式）",
                "价格必须由运营方提供并逐字核对，不得自行拟定"],
    ),
]


# ============================================================ 生成
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(text)


FAMILY = {"D01": 1, "D02": 1, "D06": 1, "D03": 2, "D04": 2, "D05": 2,
          "D07": 3, "D08": 3, "D15": 3, "D09": 4, "D10": 4, "D13": 4,
          "D11": 5, "D12": 5, "D14": 5}
FAMILY_NAME = {1: "办事与保障", 2: "健康与照护", 3: "居住与环境", 4: "安全与秩序", 5: "文化与参与"}


def gen_pack(c):
    d = os.path.join(CONTENT, c["id"])
    n = len(c["items"])
    fam = FAMILY[c["domain"]]
    famname = FAMILY_NAME[fam]
    bilingual = "A06" in c["audiences"]          # A06 = 新市民与国际居民
    lang = "bilingual" if bilingual else "zh-only"
    # ---------- 中文母本 ----------
    zh = [
        "# " + "=" * 58,
        f"# {c['domain']} · {c['field']} —— 中文母本（逐字锁定）",
        f"# 主题：{c['title_zh']}",
        f"# 骨架 {c['skeleton']} ｜ 权威等级 {c['authority']} ｜ 时效 {c['timeliness']}"
        f" ｜ 受众 {'/'.join(c['audiences'])}",
        "# 画布：屏幕版 4:5（1080×1350 PNG-24 sRGB）+ A3 打印版（297×420 mm，3 mm 出血）",
        "# 标点：全角 ，。：、 ｜ 数字与中文之间保留空格 ｜ 连字符为 ASCII \"-\"",
        "# 铁律：AI 只能搬运与排版，不得改写、不得精简、不得调换标点",
        "# 规则：references/01-classic-input-taxonomy.md（六类归类）"
        " · 02-master-copy-rules.md（母本法则与语句逻辑七查）",
        f"# 语言版本：{'中英双语（受众含 A06 国际居民）' if bilingual else '仅中文（受众不含国际居民 → 不生成英文版）'}",
        "# 版本：v1.0 ｜ 本文件中的专名与时间为示例值，发布前必须替换为人类提供的事实",
        "# " + "=" * 58,
        "",
    ]
    for i, (zl, zt, _el, _et) in enumerate(c["items"], 1):
        zh += [f"[{i:02d}] {zl}", zt, ""]
    zh += [
        "# " + "-" * 58,
        f"# 校验：信息项 {n} 条 ｜ 中文标点全角 ｜ 连字符 ASCII ｜ 电话中英一致",
        "# L2 常识（须挂官方来源，见 theme.yaml → sources）",
        "# 行数对齐（references/03-line-parity.md）：正文 25 字/行，英文 49 字符/行",
        "# 禁止写入：原文没有的承诺（免费、24 小时、保证有效等）",
        "# " + "-" * 58,
        "",
    ]
    write(os.path.join(d, "master_zh.txt"), "\n".join(zh))

    # ---------- 英文母本 ----------
    en = [
        "# " + "=" * 58,
        f"# {c['domain']} · {c['field']} —— English master copy (verbatim, locked)",
        f"# Theme: {c['title_en']}",
        f"# Skeleton {c['skeleton']} | Authority {c['authority']} | Timeliness {c['timeliness']}"
        f" | Audience {'/'.join(c['audiences'])}",
        "# Canvas: screen 4:5 (1080x1350 PNG-24 sRGB) + A3 print (297x420 mm, 3 mm bleed)",
        "# Punctuation: half-width , . : | serial (Oxford) comma | ASCII hyphen \"-\"",
        "# Line parity: English chars <= 2 x Chinese chars; at most +1 line, never > 3 lines",
        "# Rule: the AI may only carry and typeset this text - never rewrite, shorten, or restyle it",
        "# Version: v1.0 | Proper nouns and times are sample values; replace before publishing",
        "# " + "=" * 58,
        "",
    ]
    for i, (_zl, _zt, el, et) in enumerate(c["items"], 1):
        en += [f"[{i:02d}] {el}", et, ""]
    en += [
        "# " + "-" * 58,
        f"# Checks: {n} items | half-width punctuation | Oxford comma in 3+ lists",
        "# Phone string identical to the Chinese version | no ALL CAPS",
        "# Never add promises not present in the source (free, 24 hours, guaranteed, etc.)",
        "# " + "-" * 58,
        "",
    ]
    en_path = os.path.join(d, "master_en.txt")
    if bilingual:
        write(en_path, "\n".join(en))
    elif os.path.exists(en_path):
        os.remove(en_path)                       # 非双语主题不留英文母本


    # ---------- theme.yaml ----------
    aud = ", ".join(c["audiences"])
    src = "\n".join(f'  - item: "{a}"\n    basis: "{b}"\n    level: {lvl}' for a, b, lvl in c["sources"])
    nh = "\n".join(f'  - "{x}"' for x in c["needs_human"])
    ck = "\n".join(f'  - "{x}"' for x in c["checks"])
    ty = f"""# content/{c['id']}/theme.yaml
# {c['domain']} {c['field']} —— {c['title_zh']}
# 五轴分类（见 taxonomy.yaml）+ 槽位 + L2 来源 + 待人类确认 + 骨架专属校验
# 由 0_生成工具/生成内容包.py 生成，勿手改（改数据源后重跑）

theme_id: {c['id']}
title_zh: "{c['title_zh']}"
title_en: "{c['title_en']}"

# ---------- 语言版本（v1.4 规则）----------
language: {lang}          # bilingual（受众含 A06 国际居民）| zh-only（仅中文）
language_rule: "受众含 A06 → 出中英双语；否则只出中文海报与相关内容"

# ---------- 风格来源（v1.6：先按五大类，15 类暂不细分）----------
family: F{fam}                    # {famname}
style_ref: references/05-style-spec.md#F{fam}
style_status: 待填（人类补全五大类风格要求表后自动生效；本类继承 F{fam}，不单独改）

# ---------- 五轴 ----------
domain: {c['domain']}
function: {c['function']}
audience: [{aud}]
audience_status: "AI 按主题拟定，待用户确认"   # 用户给出受众时以用户为准
timeliness: {c['timeliness']}
authority: {c['authority']}
skeleton: {c['function']}

# ---------- 画布：默认固定 A3（用户指定尺寸时才改，见 04_SKILL.md 尺寸决策规则）----------
canvas:
{CANVAS}

# ---------- 母本 ----------
items: {n}
org: {{zh: "{c['org_zh']}", en: "{c['org_en']}"}}
placeholders:                    # 全部为示例值，发布前必须替换
  ORG_ZH: "{c['org_zh']}"
  ORG_EN: "{c['org_en']}"
  TITLE_ZH: "{c['title_zh']}"
  TITLE_EN: "{c['title_en']}"
  SITES_ZH: "{c['sites_zh']}"
  SITES_EN: "{c['sites_en']}"
  HOURS_ZH: "{c['hours_zh']}"
  HOURS_EN: "{c['hours_en']}"
  PHONE: "{c['phone']}"

# ---------- L2 通用常识的来源（Gate 2 逐条复核）----------
sources:
{src}

# ---------- 待人类确认（未填齐不得出图）----------
needs_human:
{nh}

# ---------- 骨架与分类专属校验 ----------
checks:
{ck}
  - "行数对齐：英文行数 ≤ 中文行数 + 1 且 ≤ 3 行（references/03-line-parity.md）"
  - "母本 {n} 项字符级 100% 命中；电话两版字符一致"
"""
    write(os.path.join(d, "theme.yaml"), ty)
    return n


def gen_tables(done):
    """生成 references/04-master-copy-tables.md（15 类中英母本总表）"""
    L = [
        "# 04 · 中英母本总表（15 类）",
        "",
        "> **本文件由 `0_生成工具/生成内容包.py` 自动生成，请勿手改**——改数据源后重跑即可。",
        "> **内容包**：`content/<id>/`（`master_zh.txt` + `master_en.txt` + `theme.yaml`）",
        "> **规则依据**：`references/01-classic-input-taxonomy.md`（六类归类）· `02-master-copy-rules.md`（母本法则与语句逻辑七查）· `03-line-parity.md`（行数对齐）",
        "> ⚠️ 表中所有具体值（机构名 / 点位 / 电话 / 时间 / 价格）**均为示例值，发布前必须由人替换并核对**。",
        "",
        "## 0. 15 类一览",
        "",
        "| 类 | 领域 | 主题 | 骨架 | 权威 | 受众 | 项数 | 语言 | 内容包 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in CLASSES:
        bil = "A06" in c["audiences"]
        L.append(f"| {c['domain']} | {c['field']} | {c['title_zh']} | {c['skeleton'].split('（')[0]} | "
                 f"{c['authority']} | {'/'.join(c['audiences'])} | {len(c['items'])} | "
                 f"{'中英双语' if bil else '仅中文'} | `content/{c['id']}/` |")
    total = sum(len(c["items"]) for c in CLASSES)
    L += ["", f"**合计**：15 类 · **{total} 条信息项** · 中英各一套（共 {total * 2} 条母本文案）。", "", "---", ""]

    for c in CLASSES:
        bil = "A06" in c["audiences"]
        L += [f"## {c['domain']} · {c['field']} —— {c['title_zh']}", "",
              f"**{c['title_en']}** ｜ 骨架 `{c['skeleton']}` ｜ 权威 `{c['authority']}` ｜ 时效 `{c['timeliness']}` "
              f"｜ 受众 `{'/'.join(c['audiences'])}` ｜ {len(c['items'])} 项 ｜ "
              f"**{'中英双语' if bil else '仅中文'}**", ""]
        if bil:
            L += ["| 项 | 信息项 | 中文示例母本（逐字） | English sample (verbatim) |", "|---|---|---|---|"]
            for i, (zl, zt, el, et) in enumerate(c["items"], 1):
                L.append(f"| {i:02d} | {zl} / {el} | {zt} | {et} |")
        else:
            L += ["| 项 | 信息项 | 中文示例母本（逐字） |", "|---|---|---|"]
            for i, (zl, zt, _el, _et) in enumerate(c["items"], 1):
                L.append(f"| {i:02d} | {zl} | {zt} |")
            L += ["", "> 本主题受众不含国际居民 → **只出中文**；英文备用文案保留在 "
                  "`0_生成工具/生成内容包.py` 数据源中，给 audience 加上 `A06` 即可启用。"]
        L += ["", f"**机构**：{c['org_zh']} / {c['org_en']} ｜ **咨询电话**：{c['phone']}（示例值）", "",
              "**L2 来源**：" + "；".join(f"{a}（{lvl}）" for a, _b, lvl in c["sources"]), "",
              "**待人类确认**：" + "；".join(c["needs_human"]), "", "---", ""]
    write(os.path.join(REFS, "04-master-copy-tables.md"), "\n".join(L))
    return total


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    todo = [c for c in CLASSES if not only or c["domain"] == only]
    for c in todo:
        n = gen_pack(c)
        print(f"  ✓ content/{c['id']}/  3 个文件（{n} 条信息项）")
    if not only:
        total = gen_tables(todo)
        print(f"  ✓ references/04-master-copy-tables.md（15 类 · {total} 条）")
    print(f"完成：{len(todo)} 个内容包")


if __name__ == "__main__":
    main()
