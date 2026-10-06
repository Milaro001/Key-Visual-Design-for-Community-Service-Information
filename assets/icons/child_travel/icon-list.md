# icon-list.md · 儿童出行（示例）

> **主题**：儿童出行 ｜ **画布**：A3 竖版 297×420 mm（默认规格）
> **流水线**：① 定形状 ✅ → ② 取图（PNG）✅ → ③ Gate 3 确认 ⬜ 待签 → ④ 美化（GPT 生图）⬜ 待做 → ⑤ 登记 ✅（本文件）
> **版本**：v1.0
> ⚠️ **本表当前全部为「骨架版」**：单色线性，**只用于定“要哪些图标、代表什么”**，**不是最终视觉**。
> 最终图标须**彩色**，并按人类参考图的风格做 **AI 二次绘制 + 上色**（规则见 `references/07-icon-style-matching.md`）。

| 图标名 | 含义 | 用在 | 来源 | 授权 | 是否需署名 | 尺寸 / 颜色 | 形状核对 |
|---|---|---|---|---|---|---|---|
| `mdi_human-child` | 儿童 | 标题 / 服务对象 | `mdi:human-child` | Pictogrammers Free License | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `mdi_human-male-child` | 大人牵小孩 | 行动 1「家长陪同」 | `mdi:human-male-child` | Pictogrammers Free License | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_road` | 斑马线 / 道路 | 行动 2「走斑马线」 | `tabler:road` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_traffic-lights` | 红绿灯 | 行动 3「看信号灯」 | `tabler:traffic-lights` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_bus` | 校车 / 公交 | 服务事项「校车接送」 | `tabler:bus` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `mdi_school` | 学校区域 | 风险区域「校门口」 | `mdi:school` | Pictogrammers Free License | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_helmet` | 安全头盔 | 行动 4「骑车戴头盔」 | `tabler:helmet` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `mdi_seatbelt` | 安全带 / 儿童座椅 | 行动 5「坐车系安全带」 | `mdi:seatbelt` | Pictogrammers Free License | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_bike` | 自行车 / 电动车 | 场景提示 | `tabler:bike` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_car` | 汽车 | 场景提示 | `tabler:car` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_phone-off` | 不看手机 | 注意事项「过街不看手机」 | `tabler:phone-off` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_hand-stop` | 停车让行 / 举手示意 | 行动 6「举手过街」 | `tabler:hand-stop` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_map-pin` | 集合点 | 时间地点 | `tabler:map-pin` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `tabler_clock` | 集合时间 | 时间地点 | `tabler:clock` | MIT | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| `noto_warning` | 当心警示（彩色版） | 备选：警示条 | `noto:warning` | Apache-2.0 | 否 | 512px → 24mm｜原色 | ⬜ |
| `mdi_block-helper` | 禁止（库版） | 备选：禁止项 | `mdi:block-helper` | Pictogrammers Free License | 否 | 512px → 24mm｜`#1B2A38` | ⬜ |
| **`gb_prohibition`** | **国标禁止标志** | 禁止类（**强制用这个**） | 按 GB 2894 几何生成 | 公开标准 | 否 | 512px → 24mm｜红 `#C0392B` | ⬜ |
| **`gb_warning`** | **国标警告标志** | 警示类（**强制用这个**） | 按 GB 2894 几何生成 | 公开标准 | 否 | 512px → 24mm｜黄 `#F2C200` + 黑 | ⬜ |

**授权结论**：全部来自 **MIT / Pictogrammers Free / Apache-2.0 / 公开国标** → **均无需署名**，画面上不必写来源。
⚠️ 使用前建议点开 Iconify 对应集页再确认一次许可（本次 API 查询超时，未能程序化核验）。

---

## GPT 生图美化提示词（第 ④ 步，你直接用）

> **核心约束：只加质感，不改形状。**

```
请把这张图标 PNG 做「质感美化」，规则严格如下：
1. 保持图标的外轮廓、比例、线宽、线条端点形状完全不变；只允许：
   - 线条边缘更干净锐利（抗锯齿优化）
   - 轻微的内阴影 / 极浅的渐变，让线条有纸面质感
   - 在图形内部加入极细微的颗粒或网点（不超过 8% 不透明度）
2. 颜色只允许在给定色值附近微调明度，不得改变色相：
   线性图标 #1B2A38；国标警告 #F2C200 + 黑 #1B2A38；国标禁止 #C0392B
3. 背景必须是完全透明（不要白底、不要阴影投影、不要外发光）。
4. 禁止：改变符号含义（禁止斜杠方向、三角形 vs 圆形）、加装饰边框、
   加文字、加立体 3D 效果、加投影。
5. 输出 PNG，长边 1024px 以上，透明背景。
```

**验收（美化回来后逐条比对）**：
- [ ] 与原件并排比对，外轮廓重合（叠图无明显偏移）
- [ ] 线宽一致（最细处未变粗/变细）
- [ ] 禁止类斜杠方向未变、三角/圆形未变、色相未变
- [ ] 背景仍为透明
- [ ] A3 落版到 24 mm 时仍清晰（不糊、不锯齿）

---

## 本轮修掉的 3 个转换器 Bug（供后续复用）

| # | 症状 | 根因 | 修法 |
|---|---|---|---|
| 1 | 10 个图标转出来是**空白图** | 描边属性写在父级 `<g>` 上，转换器只读元素自身属性 | 支持 **`<g>` 属性继承**（栈式合并，内层覆盖外层） |
| 2 | `<line x1=… y1=…>` 报错 | 属性名正则不允许数字，`x1` 没被解析 | 属性名正则改为 `[a-zA-Z][a-zA-Z0-9-]*` |
| 3 | 彩色图标（noto）报错 | `fill="url(#渐变)"` 被当成十六进制色值 | 新增 `parse_color()`：忽略 `url()` / `var()`，支持 `currentColor` |
