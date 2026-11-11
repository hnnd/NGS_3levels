# 04_slides — 三层幻灯片（Marp）

> 契约来源：`00_design/course_contract.yaml` → `slide_template`
> 校验：`python3 03_code/tools/validate_course.py --check slide_deck_match`
> 样板 deck：`phd/05_gwas_slides.md`（其余 deck 按它的骨架与密度编写）

## 定位

幻灯片是讲义的**课堂投影版**，不是讲义的复制：

- 讲义承载全部细节；deck 只承载课堂上要**说出口**的骨架
- **每讲约 60 页（50–70）**，一页一个意思；版式与密度规则见下文「版式与密度（D123）」
- 图表（若有）标题 / 轴 / 图例用英文；页面正文用中文
- **本科层**：u01–u07 的 deck 是课堂 Day 0「关键点串讲」的投影（u01–u05 共 1.5 h、u06 2 h、u07 1.5 h），
  同时是自制录屏的脚本骨架；u08 是 3 天项目导航 deck
- **硕博层**：一个专题 4 学时（2 h 理论 + 2 h 实践），deck 覆盖理论部分并在末页给实践"任务卡"

## 文件约定

```
04_slides/
├── themes/ngs.css            # 统一主题；class: undergraduate | master | phd 决定强调色
├── build_slides.sh           # marp 批量编译（HTML 默认 / --pdf / --pptx / --watch）
├── dist/                     # 编译产物（git 忽略）
├── undergraduate/NN_<slug>_slides.md
├── master/NN_<slug>_slides.md
└── phd/NN_<slug>_slides.md   # 文件名 = 讲义文件名把 _lecture 换成 _slides
```

每个 deck：

1. frontmatter 固定 `marp: true` / `theme: ngs` / `paginate: true` / `class: <level>`，
   `header` 写层次 + 专题 id + 标题，`footer` 写讲义路径 + 环境名
2. 用 `<!-- @section: <id> -->` 标记各段起始页，id 集合见契约 `slide_template.sections`
   （cover / objectives / prerequisites / background / principles / procedure /
   interpretation / stats_plugin* / ai_task* / troubleshooting / wrapup；
   `*` 仅名单内专题出现，名单外专题**不得**出现该标记）
3. `interpretation` 段必须含一页"结果不对时长什么样"
4. `wrapup` 段只给讲义 ⑪ 的指针，**不重复列文献**（避免两处维护）

## 构建

```bash
bash 04_slides/build_slides.sh                      # 全部 → dist/<level>/*.html
bash 04_slides/build_slides.sh --pdf --level phd    # PDF 需本机 Chrome/Chromium（已实测可用）
bash 04_slides/build_slides.sh --watch phd/05_gwas_slides.md   # 编辑时实时预览
```

## 版式与密度（D123，2026-11-10）

主题 `themes/ngs.css` v2：16:9、正文 30px、顶部层次色条、页码徽标。**每讲 50–70 页，每页少字**：

| 规则 | 上限 |
|---|---|
| 要点 | ≤ 4 条/页，每条 ≤ 22 个汉字（不写成句子段落） |
| 正文段落 | 不用；需要整句时用 `statement` 版式，一页一句 |
| 表格 | ≤ 4 行 × 3 列，单元格 ≤ 12 字 |
| 代码块 | ≤ 8 行，每行 ≤ 60 字符 |
| 出处 | 只放在 `<div class="ref">教材 §8.4.4</div>`，不占正文 |

版式类（`<!-- _class: <level> <版式> -->`）：

| 版式 | 用途 |
|---|---|
| `cover` | 封面（深色底），只放标题、一句话、2 行元信息 |
| `divider` | 段落分隔：`<div class="num">01</div>` + `# 标题` + 一行说明；每个 `@section` 或大块前一页 |
| `statement` | 一句话结论/金句页 |
| `figure` | 大图页：`##` 标题 + 图（不加 `w:` 尺寸指令，主题统一定高）+ **一行**说明 |
| `warn` | 出错/失效页（橙色），`interpretation` 的「结果不对时长什么样」与 `troubleshooting` 用它 |
| `quiz` | 课堂提问页，一页一问 |

页内组件：`.cols`/`.cols3`（两三栏）、`.card`（卡片，`.card.bad`/`.card.good`）、`.kpi`（大数字）、`.tag`、`.muted`。
节奏建议：每 3–5 页内容页插一页 `statement`/`quiz`/`figure`，避免连续多页纯列表。
footer 写短：`u06 基因组组装原理与质量评估 ｜ 环境 ngs_ug_assembly`（讲义路径放封面 meta）。

## 幻灯片插图（D125，2026-11-10）

**重要概念与算法必须配图**；目标：每讲 ≥ 1/3 的内容页有图（约 18–25 张），算法/流程/判读类页面一律有图。

来源优先级：
1. **讲义已有图**（`02_lectures/**/imgs/`，已登记 `09_resources/illustrations/manifest.tsv`，教材 `textbook/figures/chNN_figures.yml` 未标 hold_redraw、图面无错字乱码）；讲义图多为信息密集的海报式，**只在 figure 版式整页用**。
2. **新绘幻灯片原生图**（主渠道）：Python 脚本生成 SVG，源码 `04_slides/figsrc/<专题>/<NN>_<概念>.py`，
   产物 `04_slides/<level>/imgs/<slug>/<NN>_<概念>.svg`，脚本可重跑（固定种子、无网络）。
   - 画布 `viewBox="0 0 1600 900"`（16:9）；或放在 `.cols` 一栏时 `0 0 800 700`
   - 字号 ≥ 30（viewBox 单位）、字号层级 ≤ 3、每图文字 ≤ 30 个汉字；一图一个焦点
   - 配色沿用课程插图规范 `.scratch/illustrations/spec.md` §2（多彩语义色；红 `#E64B35` 只标关键事件/易错点）
   - 字体 `"Noto Sans CJK SC","PingFang SC",sans-serif`；纸底透明或 `#FAFAF7`
   - **数据图**（k-mer 谱、N50 条形等）直接调用 `textbook/demos/` 演示脚本的函数或复用其参数生成，图中数字必须与 demos 输出一致并在 deck 的 `.ref` 注明「合成数据，demos/<脚本> 参数」
3. 开放许可图（Wikimedia Commons 等，登记许可证）——仅用于真实仪器/样本照片类。
4. AI 生图（gpt-image-2）只用于生物形态示意，**不得用于算法/数据图**，不得在图中渲染文字。

用法：整页图用 `figure` 版式；图文并排用 `.cols`（左图右 ≤ 3 条要点）。
所有新图逐行登记 `09_resources/illustrations/manifest.tsv`（channel=svg-slide，license=自绘）。

## 越界检查（D130）

图文并排页的图按高度约束（主题 `.cols img` 最高 400px），但仍须实测：

```bash
marp --no-stdin --html --allow-local-files --theme-set 04_slides/themes/ngs.css -o /tmp/x.html -- <deck>.md
node 04_slides/check_overflow.mjs /tmp/x.html     # 逐页测量，任何元素越过页底/右侧安全区即报页码
```

PNG 目检看不出「刚好擦边」的越界（换浏览器/投影分辨率就被截断），以本检查为准。
