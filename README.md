# 电商舆情周报 Skill

[简体中文](README.md) | [English](README.en.md)

一款面向电商、用户研究（UXR）和竞品分析团队的 Codex Skill。它按照指定市场与自然周检索公开信息，将分散的新闻、监管公告、平台卖家政策、消费者投诉和行业数据，整理成适合群内快速浏览的中文周报。

> Skill 名称：`ecom-sentiment-weekly-reporter`  
> 作者：cty

## 它能做什么

- 按市场监测电商动态，默认支持美国、英国，也可自行扩展。
- 覆盖 Amazon、Temu、SHEIN、TikTok Shop、eBay、Walmart、Meta / Instagram、Google 等平台。
- 将信息清楚标记为“新闻”“政策信号”或“用户舆情”。
- 关注监管与合规、卖家治理、物流履约、退货退款、价格促销、内容电商、广告推荐、支付安全、商品真实性和客服体验。
- 为每条信息补充情绪判断、关键事实、UXR 关联指标、发布日期和原始来源。
- 生成 Markdown 周报，或生成适合群聊阅读的紧凑型 HTML 报告。
- 可根据个人配置将报告发送到飞书群，并归档到飞书文档；没有飞书能力时仍可正常生成本地报告。

## 报告长什么样

默认的紧凑型 HTML 报告会把多个市场放在同一份文件中，例如先美国、后英国，并采用单栏全宽布局：

1. 最多 3 条跨市场核心结论；
2. 按市场和平台组织信息；
3. 每条包含类型、情绪、标题、加粗关键事实、2–4 句摘要、UXR 影响、日期和来源；
4. 默认不使用图片，减少装饰和无效留白；
5. 移动端自动保持单栏，方便直接发到群里浏览。

### 实际生成效果

下面是 Skill 实际生成的紧凑型 HTML 报告片段。每条信息将平台、类型、情绪、标题、关键事实、摘要、UXR 影响、日期和原始来源集中在同一阅读流中。

![电商舆情周报实际生成效果](assets/report-example.png)

> 截图仅用于展示报告版式；每次运行的新闻内容、平台覆盖和结论会随指定市场、日期及来源变化。

## 安装

### 在 Codex 中安装

把下面这句话发给 Codex：

```text
请从 https://github.com/caitianyuaan/ecom-sentiment-weekly-reporter 安装这个 Skill
```

安装完成后，重新打开一个任务，或让 Codex 使用 `$ecom-sentiment-weekly-reporter`。

### 手动安装

将仓库放到 Codex 的个人 Skill 目录：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/caitianyuaan/ecom-sentiment-weekly-reporter.git \
  ~/.codex/skills/ecom-sentiment-weekly-reporter
```

如果已经安装，可在该目录执行 `git pull` 获取更新。

## 快速开始

安装后，可以直接描述需要的市场、时间和输出格式：

```text
使用 $ecom-sentiment-weekly-reporter，生成 7 月第一周的美国和英国电商舆情周报。
美国在前、英国在后，每个市场争取 8–12 条，覆盖新闻、监管公告、平台卖家政策、消费者投诉和行业数据。
清楚标注“新闻”“政策信号”“用户舆情”，输出一份紧凑型中文 HTML，不要图片，署名 cty。
```

也可以使用简短指令运行已经保存的个人配置：

```text
使用 $ecom-sentiment-weekly-reporter，按我的配置生成本周电商舆情报告。
```

## 首次配置

Skill 会按以下优先级读取参数：

1. 当前指令中明确提供的要求；
2. `~/.ecom-sentiment-weekly-reporter/config.json` 中的个人配置；
3. 配置缺失时，引导完成首次设置。

首次设置有三种方式：

- 沿用作者设置：复制默认市场、平台、主题和来源范围，再填写自己的发送信息。
- 基于作者设置调整：保留默认范围，再增删市场、平台、主题或来源。
- 完全自定义：从头指定监测范围、报告语言、输出形式和飞书地址。

可使用脚本从模板创建个人配置：

```bash
cd ~/.codex/skills/ecom-sentiment-weekly-reporter
python3 scripts/init_user_config.py \
  --mode follow_creator_settings \
  --from-template
```

验证配置：

```bash
python3 scripts/init_user_config.py --validate
```

个人配置中的主要字段如下：

| 字段 | 用途 |
| --- | --- |
| `markets` | 监测市场，例如 `US`、`UK` |
| `platforms` | 重点平台列表 |
| `topics` | 重点议题列表 |
| `source_profile` | 来源策略，如 `default`、`official_first` |
| `sources.include/exclude` | 自定义纳入或排除的来源 |
| `items_per_platform` | 每个平台期望的信息数量 |
| `report_language` | 报告语言，例如 `zh-CN` |
| `output.html` | HTML 是否启用、布局、市场是否合并、是否使用图片 |
| `feishu_group_id` | 飞书群 ID；仅本地生成时可不执行发送 |
| `feishu_doc_url` | 飞书归档文档；仅本地生成时可不执行归档 |
| `sender_name` | 报告署名 |

示例配置见 [`references/sample-config.template.json`](references/sample-config.template.json)。

## 常用指令

### 生成当周报告

```text
使用 $ecom-sentiment-weekly-reporter，按我的配置生成本周报告，仅保存到本地。
```

### 指定日期范围

```text
生成 2026-07-01 至 2026-07-07 的美国和英国电商舆情周报，输出中文 HTML。
```

### 只看特定平台或主题

```text
监测英国市场的 Amazon、TikTok Shop 和 Temu，只关注卖家政策、退货退款与消费者投诉。
```

### 强调信息密度

```text
采用 consulting_compact 格式，不要图片。每条保留关键事实和 2–4 句摘要，新闻重点加粗，减少卡片留白。
```

### 发送并归档到飞书

```text
按我的配置生成本周报告，发送到已配置的飞书群，并归档到飞书文档。
```

## 日期与数量兜底机制

日期范围是硬约束，数量只是目标：

- 仅纳入发布日期位于指定周期内，或与该周期直接相关且可验证的信息。
- 不会使用更早的背景报道、过期调研或周期结束后的跟进新闻凑数。
- 不会因为事件仍然相关，就把旧文章改标为本周日期。
- 达不到目标条数时，会保留实际可验证条目并明确说明缺口。
- 多家媒体重复报道同一事件时，优先保留最强来源，其他来源只用于交叉验证。

因此，“每个市场 8–12 条”表示期望覆盖范围，不代表必须牺牲时效性或真实性凑满数量。

## 信息质量与来源

Skill 优先使用官方公告、监管机构、平台新闻中心、公司博客、主流媒体和具有明确出处的行业分析。执行时会：

- 按市场、平台、主题和日期组合检索；
- 记录实际执行的查询和已检查的候选信息；
- 对候选信息进行相关性、UXR 价值、市场针对性和来源质量评分；
- 合并重复链接和同一事件的重复报道；
- 生成内部覆盖检查，识别未搜索、无候选、候选被拒或来源过度集中的情况。

“用户舆情”通常代表经过核验的消费者或卖家反馈样本，不应将单个帖子直接外推为整个平台的整体表现。

## 输出文件

- Markdown：适合作为标准文本底稿、复制到文档或继续编辑。
- HTML：适合浏览器打开、截图、群内分享或作为咨询式管理简报。
- 飞书消息与归档：在配置了有效目标且当前环境具备对应能力时执行。

HTML 布局规范见 [`references/report-format-html.md`](references/report-format-html.md)。

## 常见问题

### 为什么某个市场不足 8 条？

指定周期内没有足够的高质量、可验证信息时，Skill 会主动减少条数并说明原因，不会拿旧新闻补位。

### 为什么默认没有新闻图片？

默认报告面向群聊快速阅读。去掉图片可以提升信息密度，也能避免使用与具体事件不完全对应的配图。如确有需要，可将 `output.html.include_images` 设为 `true`，并要求只使用属于该事件的图片。

### 可以只生成本地文件吗？

可以。在指令中明确写“仅本地生成，不发送飞书、不归档”即可。

### 可以监测其他国家或平台吗？

可以。直接在指令或个人配置中添加市场、平台、主题及首选来源。

### 能否完全自动定期执行？

可以在 Codex 中创建周期任务，并使用短指令：

```text
运行 ecom-sentiment-weekly-reporter，使用我的已保存配置。
```

定期执行前，建议先手动运行一次，确认日期口径、输出目录、来源范围和飞书目标均正确。

## 仓库结构

```text
ecom-sentiment-weekly-reporter/
├── SKILL.md              # Skill 的核心工作流与规则
├── agents/openai.yaml    # Codex 界面展示信息
├── references/           # 来源策略、配置模板与报告格式规范
├── scripts/              # 配置、周期、预检、状态与验证脚本
└── tests/                # 稳定性和格式测试
```

## 使用边界

- 报告基于公开来源，不替代法律、合规、投资或财务意见。
- 新闻与政策可能持续更新，重要决策应回到原始来源复核。
- 消费者投诉和社区反馈属于定性信号，除非来源提供可靠统计，否则不应视作发生率或总体比例。
