---
title: "实验指导 p03：双 RNA-seq 拆分定量、分开归一化与效应子候选排序"
level: phd
topic: p03
textbook: [ch16, ch11]
lecture: ../02_lectures/phd/topic03_host_pathogen/03_host_pathogen_lecture.md
env: ngs_phd_interaction
---

# 实验指导 p03：双 RNA-seq 拆分定量、分开归一化与效应子候选排序

> 上机时手边打开的这份文件。每步回答五件事：做什么、敲什么、产出哪个文件、看到什么算对、看到什么说明错了。
> 原理与判据在教材第 16 章（§16.4 概念方法、§16.5 五条失效条件、§16.6 边界、§16.7 习题、§16.10 数字索引），比较基因组那一段接第 11 章 §11.4.8。
> **数字标注规则（全篇遵守）**：检查点里的每个数只来自三类合格入口——① `06_data/phd/README.md` p03 节的登记实测（全量 104 GB、默认每样本前 200 万条约 2 GB、单端、文件头部非随机）；
> ② 教材正文带复现入口（手算式如 `D_used = P/f_P`、`1/f_P`、`19.9 ÷ 0.233 ≈ 85.4`、自由度 `18−6=12`；脚本现跑值如 19.5553 / 4.8761 / 0.8833 / 0.2329%、61.2× / 0.701 / 1.023、功效 0.049–0.765 与上限 0.766）；
> ③ 教材明确标「设例／经验法则」的量级（`ε`、`q`、`P`、`3` 千、0.85、`CS pos: 17-18`、分泌组 5%–10%）。
> 真实 18 样本全流程**集群未复跑**（教材 §16.6 L471 明写本章无实测），故凡属真实样本结果的检查点一律标「预期（未实测）」或只给定性判据，数值由你自己的日志填进 §4 记录表。教材已撤下的经验阈值本指导一个不用；
> 报错原文里的体量/上限**照录只用于认出这条报错**，不是推荐值。

## 0. 本实验对应什么

- **教材**：第 16 章为主（§16.4 方法与 §16.5.1–§16.5.5 五条失效条件），博士层目标 LO16-01–04；
  第 11 章 §11.4.8 为参照（直系同源输出怎么读、特异基因为什么只是候选）。硕士层 LO16-05/06 只作选读。
- **讲义**：p03 ② 前置表、④ 4.1–4.10、⑤ 5.1–5.6、⑥ 6.1、⑧ AI 任务、⑨ E1–E8、⑩ 练习题、⑪ 文献。
- **学时**：p03 共 4 学时（`00_design/course_contract.yaml`）；作业建议上机 6–8 小时（两次建索引与
  OrthoFinder 都要排队）、写报告 3 小时（`08_assessment/phd/assignments/p03_host_pathogen_practice.md`）。
- **环境**：`ngs_phd_interaction`（`07_envs/conda/env_phd_interaction.yml`）。现 pin：STAR 2.7.10b（L21）、
  Salmon 1.10.3（L22）、samtools 1.17（L24）、OrthoFinder 2.5.5（L27）、r-base 4.3.1（L39）；`bioconductor-deseq2`（L23）与 `hmmer`（L33）**未钉版** → 方法学里不写这两个版本号，改为打印实际值（§16.3）。
- **两个工具不在 conda 里**（契约 `env_exempt_tools`）：SignalP 6.0 需 DTU 许可（官网申请后
  `pip install signalp-6-package/`）、EffectorP 3.0 走 GitHub clone（`EFFECTORP_PY` 指到 `EffectorP.py`）。**不要 `conda install signalp / tmhmm2`**（会得到 `PackagesNotFoundError`，讲义 ⑨-E6）。
- **三个脚本的顺序不能颠倒**：`03_dual_rnaseq_quant.sh` → `03_effector_screen.sh` → `03_dual_deseq2_lrt.R`。
  **先跑 R 会直接停**：R 的第 4–6 个位置参数都由 `03_effector_screen.sh` 产出（后者 L168–175 也明写这笔交接）。
- **本实验做不了的两件事**（§16.6）：没有抗病品种 N3 → 做不了抗/感等位比较；没有病原体外纯培养样本 →
  做不了 in planta 与 in vitro 对比。只能写进报告的限制一节，不能用分析手法补上。
- **计算纪律**：两个 `.sh` 带 `-pe smp 16` 与 `h_vmem` 作业头；R 脚本**没有** SGE 头，必须用 3.11 的
  `run_lrt.sh` 包装投递。登录节点只做下载、建环境、编辑、查文件与看日志，一切计算 `qsub`（脚本头明令）；投递后无法再补参数，改任何一个值都要重投。

## 1. 实验前检查

- **前置自测**：`08_assessment/prerequisites/` 里 `l0_01_linux` 第 9 题、`l0_02_r` 第 8/10 题、
  `l0_03_conda` 第 9/10 题（SGE 里激活环境，上机必做）、`l0_04_formats` 第 4/6/9 题、`l0_05_qc` 第 4/9 题、`l0_06_stats` 第 3/5/6/9 题；`l1_phd` 第 5/6 题（负二项 LRT、OrthoFinder 输出，补课约 90 min）。
- **建/激活环境并核验工具链**（建环境与下载都在登录节点）。**在课程仓库根目录敲**：

  ```bash
  conda env create -f 07_envs/conda/env_phd_interaction.yml     # 只需一次
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_interaction
  for t in seqkit samtools STAR salmon orthofinder diamond hmmscan hmmpress; do command -v $t; done
  command -v signalp6 || echo "缺 signalp6：按 §0 申请安装，不进 conda"
  command -v tmhmm || echo "缺 tmhmm：跨膜排除要改用 DeepTMHMM，见 3.9"
  EFFECTORP_PY=<EffectorP-3.0 目录>/EffectorP.py        # 换成你的实际路径
  python "${EFFECTORP_PY}" -h | head -3                   # 能打出用法才算部署成功
  Rscript -e 'cat(as.character(packageVersion("DESeq2")), "\n")'
  ```

  这条命令在做什么：SGE 作业不继承终端的 conda 变量，两个 shell 脚本各自开头激活一次（`03_dual_rnaseq_quant.sh` L26、`03_effector_screen.sh` L34），L28–30 与 L50–52 还逐个 `command -v` 守卫；
  EffectorP 不在 conda 里，脚本 L55 才查它，所以要在登录节点先验一次，别等排队几小时后 FATAL。**只查「有没有」、不查版本号**：DESeq2 与 hmmer 未 pin，写预期值就是编；已 pin 的四个以实查为准并记进 §4。
- **Pfam 库**：`03_effector_screen.sh` L154 缺 `.h3i` 时自动 `hmmpress`，缺这步报 `use hmmpress first`（⑨-E7）。
  **集群预置先别自己下**：`06_data/reference/README.md` 登记只读库在 `/data/db/pfam/`。先 `ls -l ${NGS_DB:-/data/db}/pfam/` 看有没有 `Pfam-A.hmm` 与四个索引（`.h3i/.h3m/.h3f/.h3p`），实际文件名以 `ls` 为准；
  索引不全就补 `hmmpress`（要写权限，只读部署就把 `.hmm` 拷到个人目录再压）。自备才走 `wget -c https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz && gunzip Pfam-A.hmm.gz`，并在方法学写明版本与下载日期。
- **参考基因组**：水稻 IRGSP-1.0（`GCA_001433935`，已在 `06_data/accessions.tsv` 登记）＋稻瘟菌 70-15
  （**装配号未登记，本指导只写「70-15」**）。两套 FASTA ＋ GTF 放同一目录，文件名记进报告。**集群预置**：`06_data/reference/README.md` 登记合并参考在 `/data/db/dual_ref/`；
  先 `ls -l ${NGS_DB:-/data/db}/dual_ref/` 看清是**索引**还是**四件原始文件**——有原始四件就直接指过去，只有索引就自己备四件并写明来源与下载日期，不要把不同装配版本混用。
  **两侧 GTF 的 `gene_id` 必须带同一套前缀**，见 3.1 检查点 4（本步最容易漏的一条）。
- **脚本静态检查**（课程仓库根目录；应空输出、退出码 0、不产生文件）：

  ```bash
  bash -n 03_code/phd/scripts/03_dual_rnaseq_quant.sh
  bash -n 03_code/phd/scripts/03_effector_screen.sh
  bash -n 06_data/phd/download_phd.sh
  Rscript -e "invisible(parse('03_code/phd/scripts/03_dual_deseq2_lrt.R'))"
  ```

  **两类命令不能混**：`bash -n` 只对 `.sh` 有意义，对 `.R` 会报 `syntax error near unexpected token`；R 脚本的静态检查是 `parse()`（只解析、不执行，语法错立刻报行号）。
- **自查演示**（不需要集群，三个脚本各自 `SELFTEST PASS`）：

  ```bash
  cd <课程仓库路径>/textbook && export PYTHONDONTWRITEBYTECODE=1
  python3 demos/ch16_cross_mapping_leakage.py --selftest
  python3 demos/ch16_mixed_tpm_bias.py --selftest
  python3 demos/ch16_pathogen_power.py --selftest
  ```

  三组数是 3.3/3.4/3.11 与 §5 的读图标尺，**都是合成算例，只对其生成模型成立**：交叉比对虚增随病原占比下降，实现值 **19.5553 / 4.8761 / 0.8833 / 0.2329%**（闭式 19.9 / 4.9 / 0.9 / 0.233%）；
  顺序过滤的缺失量恒在 `c` 附近（**0.1092 / 0.1031 / 0.1070 / 0.0976%**），竞争性比对两侧各 ≈0.1%——**同量级、方向对称，这正是「可披露」与「不可披露」的分界**；
  合并矩阵里恒定病原基因表观 **61.2×**（模型 60.0×）、恒定宿主基因 **0.701**（模型 0.704）、分开归一化后 **1.023**；功效表 `0.049 → 0.528 → 0.765`、上限 **0.766 < 0.8**，且正态近似在 `μ1=1` 档失真（MC 0.095 vs 解析 0.164，脚本已打印告警）。

## 2. 实验数据

- **来源与规模**：`PRJNA661210`（同 `GSE157400`），两号均已登记（`06_data/accessions.tsv` L11／L12）。
  全因子 `2×2×4×3 = 48`；教学子集 `1×2×3×3 = 18`（手算，§16.6）：日本晴 × {接种, 模拟} × 12/24/48 hpi × 3 重复。
- **下载**（登录节点做；体量为 `06_data/phd/README.md` p03 节登记值）。**先把路径变量定死，后面所有步骤都用它们**：

  ```bash
  DATA=/d3/scratch/${USER}/ngs/data          # 下载根目录，= --outdir
  P03=$DATA                                  # 本实验的全部路径都从 $P03 展开
  export P03 DATA                            # 本终端交互命令要用；作业不继承，见下
  bash 06_data/phd/download_phd.sh --topic p03                    # 先 dry-run 看命令
  bash 06_data/phd/download_phd.sh --topic p03 --run --outdir "$DATA"   # 真下：约 2 GB（截取模式）
  ls -1 "$P03/p03_dual_rnaseq"/*.fastq.gz | wc -l                 # 必须打印 18
  ```

  落盘在 `--outdir` 下的 `p03_dual_rnaseq/`，即 **`$P03/p03_dual_rnaseq/`**——`--outdir` 与 glob 的根是同一个 `$P03`，不要再多套一层 `p03/`（多一层时 glob 一个文件都匹配不到，循环静默产出只有表头的样本表）。
  每样本一个 `<sample_title>.sub.fastq.gz`（`--full` 时无 `.sub`，全量约 104 GB）。清单见 `06_data/phd/manifests/p03_runs.tsv`：**19 行 = 表头 + 18 行**。
  **18 个 run 号未在 `accessions.tsv` 登记**，故报告只写 `PRJNA661210` 与「18 个 run」，**不要抄 run 号**。
  **`P03` 只在当前终端有效**：SGE 作业不继承它、作业头也没有 `-V`，而两个 `.sh` 都是 `set -u`——副本里写 `SAMPLES=$P03/work/samples.tsv` 会直接 `unbound variable`。**副本里一律写展开后的绝对路径**，投递前 `grep -n 'P03' 副本` 确认零残留。
- **样本表 `samples.tsv` 自己派生，不要手抄**（脚本要的列口径是 `sample R1 R2 treatment time`，
  `03_dual_rnaseq_quant.sh` L37；写错一个字符就是 18 个样本全错）：

  ```bash
  mkdir -p "$P03/work" && cd "$P03/work"
  printf 'sample\tR1\tR2\ttreatment\ttime\n' > samples.tsv
  n=0
  for f in "$P03"/p03_dual_rnaseq/*.fastq.gz; do
      [[ -s "$f" ]] || { echo "没有匹配到 fastq：$f"; exit 1; }
      t=$(basename "$f" .fastq.gz); t=${t%.sub}          # 去掉截取模式加的后缀
      case "$(echo "$t" | cut -d_ -f2)" in
          G11) trt=inoculated ;; H2O) trt=mock ;;
          *) echo "未知处理：$t（规范形如 Nip_G11_12_1）"; exit 1 ;; esac
      printf '%s\t%s\t-\t%s\t%s\n' "$t" "$(realpath "$f")" "$trt" \
             "$(echo "$t" | cut -d_ -f3)" >> samples.tsv     # 12 / 24 / 48
      n=$((n+1))
  done
  echo "样本行数：$n（必须是 18）"
  awk -F'\t' 'NF!=5 || $3==""' samples.tsv        # 必须无输出
  tail -n +2 samples.tsv | cut -f4 | sort -u      # 必须恰好 inoculated / mock 两行
  tail -n +2 samples.tsv | cut -f5 | sort -u      # 必须恰好 12 / 24 / 48 三行
  ```

  **报「未知处理」时怎么查**（三个地方，按顺序）：`ls "$P03/p03_dual_rnaseq" | head` 看文件名是不是 `<品种>_<处理>_<时点>_<重复>` 四段（下划线只有三段或多了 run 前缀都会让 `cut -f2` 取错）；
  `cut -d_ -f2` 取到的是 `G11` 还是 `H2O`（大小写与拼写要一致）；`n` 打印的数字与 `ls | wc -l` 是否相同。文件名不合规范时 **先改名再跑这个循环**，不要在循环里加分支硬凑——`treatment` 取值错会一路传到 R 脚本的 `relevel`。
  **两处口径必须盯住**：① 单端时 `R2` 列写 `-`（或 `NA`），**不能留空**——连续空字段会被 `read` 合并，`treatment` 整体前移进 R2 列（§16.5.3，脚本 L38–39 注释）；
  ② `treatment` 只有 `mock` 与 `inoculated` 两个值——R 脚本 L49 用 `relevel(..., ref = "mock")` 定参考水平，写成 `H2O`／`G11` 会让交互项失去参照。这是**本实验最容易在第一步就埋下的错**。
- **唯一合格的自查判据（README L85，定性）**：`H2O` 对照行分配给稻瘟菌的读段比例应**很低**（本流程的
  交叉比对本底）；`G11` 接种行的病原读段比例应随 hpi **单调上升**。对照组与接种组相当 → 回查前缀同步与比对参数，不要先怀疑生物学。
  **只写定性读法、不写百分比阈值**：§16.6 明写 README 给的是定性判据、本章未在集群复跑，具体数值由你自己的 `biomass.tsv` 填进 §4。
- **README 必知第 2 条**：默认截取的是 FASTQ **文件头部，不是随机抽样**（按 flowcell 位置排序），质量与 GC
  可能有偏 → **绝对丰度类结论不可靠**。要写定量结论就用 `--full` 下全量再 `seqtk sample`，并在方法学写明取舍。这一条决定你的 `path_pct` 只能作曲线形状判读，不能当生物量定量。
- **数据缺陷写进限制**：只有日本晴、没有 N3；没有体外纯培养。缺前者丢抗/感等位比较，缺后者丢 in planta
  诱导峰值与体内外对比——这正是 §16.4.6 说「脚本里没有 in planta 诱导峰值这一项」的原因。

## 3. 实验步骤

> 每步五栏：**目的 / 命令 / 产出文件 / 检查点 / 出错信号（→ 教材节号）**。命令调用 `03_code/phd/scripts/` 现有脚本，不复制全文；脚本名、参数名、输出文件名已逐个与现版源码核对（行号对现版）。
> 真实数据全流程**集群未复跑**：真实样本结果的检查点一律标「预期（未实测）」或定性。
> 工作目录 `$P03/work`（`$P03` 即 §2 定的 `DATA=/d3/scratch/${USER}/ngs/data`），三个产物目录 `Q=$P03/work/p03_dual`、`S=$P03/work/p03_screen`、`L=$P03/work/lrt`。
> `03_code/`、`06_data/`、`07_envs/` 只读：要改任何值都走「`cp` 个人副本 → 改指定行 → `grep` 确认 → `qsub` 副本」。
> **重跑规则按脚本分别看，不是「三个都幂等」**：① `03_dual_rnaseq_quant.sh` 有三处跳过守卫——`ref/dual.fa.fai` 在就跳步骤一（L54）、`dual_idx/SA` 在就跳步骤二（L78）、某样本的 `<S>_ReadsPerGene.out.tab` 在就跳该样本的比对（L93）；
> 但**步骤四每次都重写 `qc/biomass.tsv`**。② `03_effector_screen.sh` 只在 `${ORTHO}/out` 目录已存在时跳 OrthoFinder（L69）；
> 清洗（L61–65）、两路特异基因（L84/L88/L95）、SignalP（L103）、成熟肽（L116）、`hmmscan`（L155）**每次全部重算并覆盖**（特异基因那一步还是 `>>` 追加后再 `sort -u`，重跑不会脏，但改了 `FOCAL` 就要先删旧文件）。
> ③ `03_dual_deseq2_lrt.R` **没有任何跳过判断**，每次运行都把四张结果重算覆盖。因此「改了参数也生效」只对 R 脚本和步骤一/二/三各自的产物成立；其余步骤想干净重跑，先删对应产物目录。

### 3.1 构建加前缀的双参考，并同步 GTF 第 1 列

- **目的**：把两个物种的序列名用 `HOST_`／`PATH_` 前缀物理隔离，让「这条读段属于谁」在基因名上就能回答，
  同时让 GTF 的染色体名与 FASTA 一致。**只改一边是最高频的错**：此时 `samtools faidx` 只警告、STAR 不报错，计数会静默落在少数几条序列上（教材 §16.5.1）。
- **命令**（`qsub`；参数用绝对路径写进个人副本）：

  ```bash
  cd "$P03/work"
  cp <课程仓库路径>/03_code/phd/scripts/03_dual_rnaseq_quant.sh ./dual_quant.sh
  # 在副本 L33 之前插入六行赋值（脚本用 ${X:?…} 空值即 FATAL；别写在 L33 之后）
  #   HOST_FA=<宿主基因组 fasta 绝对路径>      HOST_GTF=<宿主注释 gtf 绝对路径>
  #   PATH_FA=<病原基因组 fasta 绝对路径>      PATH_GTF=<病原注释 gtf 绝对路径>
  #   SAMPLES=<展开后的绝对路径>/work/samples.tsv
  #   OUTDIR=<展开后的绝对路径>/work/p03_dual
  grep -n 'HOST_FA=\|HOST_GTF=\|PATH_FA=\|PATH_GTF=\|SAMPLES=\|OUTDIR=\|h_vmem\|-pe' dual_quant.sh
  grep -c '\$P03' dual_quant.sh        # 必须 0：作业里 $P03 未定义，留着就是 unbound variable
  qsub dual_quant.sh
  qstat -u "$USER"
  ```

  为什么要改副本而不是 `HOST_FA=… qsub`：那个前缀只给 `qsub` 命令自身设环境变量，不转交给作业进程，作业头也没有 `-V`，脚本 L33 的 `${HOST_FA:?…}` 会直接让作业失败。
  `qsub -v` 是另一种可行写法，但本机无 SGE、**集群未实测**，统一走「改副本 + `grep` 确认」。脚本这一段做什么：作业头 `-pe smp 16`（L6）、`h_vmem=64G`（L7）、`-j y`（L5）；L25 `set -euo pipefail`；L26 激活环境；
  L56–57 `seqkit replace` 给两侧 FASTA 加前缀，L58 `cat` 成 `dual.fa`；L60–63 用 `awk` 给两个 GTF 的**第 1 列**加同样的前缀并拼成 `dual.gtf`；L66 数重名、L67–68 非空即 `[FATAL]`；L69 `samtools faidx`；
  L71–74 `comm -23` 查「GTF 有、FASTA 没有」的序列名，非空即 `[FATAL]`。
- **⚠ 第 1 列不是唯一的锚点：`gene_id` 也得带前缀**。`ReadsPerGene.out.tab` 的**第 1 列取的是 GTF 第 9 列的
  `gene_id` 属性**，不是染色体名。脚本 L60–63 只改 `$1`，所以照原样跑出来的计数表里基因名是 `Os01g…`／`MGG_…`，3.3 的 `awk 'NR>4 && $1 ~ /^HOST_/'` 会**返回 0 行**（两个矩阵都是空的，流程不报错）。
  **做法**：在个人副本里把那两条 `awk` 各补一个 `gene_id` 前缀（同样走「改副本 → `grep` 确认 → `qsub`」）：

  ```bash
  # 打开 dual_quant.sh 的 L60 与 L62，两条 awk 都要改两处：BEGIN 加 FS、{…} 加 gene_id 前缀
  #   BEGIN{FS=OFS="\t"} /^#/{print; next}
  #   {$1=p $1; if ($9 ~ /gene_id "/) sub(/gene_id "/, "gene_id \"" p, $9);
  #    else print "[WARN] 第 9 列没有 gene_id：" $1 > "/dev/stderr"; print}
  grep -n 'FS=OFS\|gene_id "/' dual_quant.sh   # 必须命中 2 行（L60、L62 各一行，各含 FS=OFS 与 gene_id 两处）
  ```

  **`FS` 与 `OFS` 必须一起设**。原脚本 L60/L62 只写 `BEGIN{OFS="\t"}`：awk 于是按空白拆行，第 9 列的 `gene_id "Os01g…"; transcript_id …` 被拆成 `gene_id`、`"Os01g…";` 等多段，`sub(/gene_id "/, …)` 匹配不到，注释列被重排成 `gene_id` + 制表符 + `"Os01g…";`——`dual.gtf` 看着还在，STAR 却报 `Fatal INPUT FILE error, no valid exon lines in the GTF file`（本机 STAR 2.7.11b 实测）。`sub(...)` 里的 `"` 仍要转义：少一个反斜杠会把第 9 列写成 `gene_id HOST_Os01g…`（引号被吃）。补齐后先跑检查点 4 看一眼 `dual.gtf`，再投递。
- **产出文件**：`$Q/ref/dual.fa`、`$Q/ref/dual.gtf`、`$Q/ref/dual.fa.fai`、
  `$Q/qc/dup_seqnames.txt`、`$Q/qc/gtf_not_in_fasta.txt`（后两个**正常情况下是空文件**）。
- **检查点**：
  1. 两个清单都**存在且为空**（`ls -l` 看 0 字节）；非空说明你走到了 `[FATAL]` 那一行，日志里会有说明；
  2. **索引对账**：`wc -l < $Q/ref/dual.fa.fai` 必须等于 `grep -c '^>' $Q/ref/dual.fa`。这是「索引实际收到了
     几条序列」的唯一证据，与清单①不重复——清单查输入，对账查索引（教材 §16.5.1 ③）；
  3. 两侧前缀都真的加上了：`cut -f1 $Q/ref/dual.gtf | grep -v '^#' | sort -u | head` 应全部带 `HOST_` 或
     `PATH_`，且不出现裸 `chr1`；`grep -c '^>HOST_' $Q/ref/dual.fa` 与 `grep -c '^>PATH_'` 都大于 0。
  4. **`gene_id` 也带上了前缀（这一条决定 3.3 拆不拆得开）**：
     ```bash
     grep -v '^#' "$Q/ref/dual.gtf" | cut -f9 | grep -o 'gene_id "[^"]*"' | head -3
     grep -v '^#' "$Q/ref/dual.gtf" | grep -c 'gene_id "HOST_'    # 宿主侧的基因数
     grep -v '^#' "$Q/ref/dual.gtf" | grep -c 'gene_id "PATH_'    # 病原侧的基因数
     grep -v '^#' "$Q/ref/dual.gtf" | cut -f9 | grep -c 'gene_id "'   # 与上面两条之和相等才算全覆盖
     ```
     前三条里出现**不带 `HOST_`/`PATH_` 的 `gene_id`**，就是没补前缀（3.3 会得到两张空表）。再补一道**坏格式**检查：`grep -Ec 'gene_id "[A-Z]+_"[A-Za-z]' "$Q/ref/dual.gtf"` 应为 0——命中说明引号被吃掉了（`gene_id "HOST_"Os01g…`）。
     用量词 `[A-Z]+` 而不是 `[A-Z]*`：后者允许前缀后一个字符都没有，`gene_id "HOST_"Os01g…` 与 `gene_id "HOST_"` 无法区分；对 `"contig1_1"`、`"P03_MGG_0001"` 这类名字则一律 0 命中——检查形同虚设（本机正反两路实测）。
     更严格的一道是要求 `gene_id` 以 `";` 收尾（注释行不计）：`grep -v '^#' "$Q/ref/dual.gtf" | grep -vcE 'gene_id "(HOST|PATH)_[A-Za-z0-9_.|:-]+";'` 应为 0；非 0 时把这几行单独打出来就是坏格式清单。
- **出错信号**：`[FATAL] 双参考中有重名序列` → 两套参考本来就有同名染色体，加前缀前就要发现（这正是前缀的
  意义）；`[FATAL] GTF 中有 FASTA 里不存在的序列名` → GTF 第 1 列没同步改，或改成了另一套命名；
  日志里 `samtools faidx` 打出 `[W::fai_insert_index] Ignoring duplicate sequence` 而 rc=0 → **它只保留第一条、不替你拦**，必须回看清单①与③（→ §16.5.1）。
  最危险的一档是「三个文件都在、对账也过、但某一侧的基因因为 GTF 行被静默丢弃而根本没有条目」——回 3.3 看两侧计数文件的行数是否对得上各自注释的基因数（→ §16.5.1）。

### 3.2 STAR 建复合索引

- **目的**：为「一次比对、两侧竞争」建一个索引。它比单物种索引大得多，内存是这一步的主要风险；
  但**脚本预留的 60 GB（L43 `GENOME_RAM`）与队列申请的 64 GB（L7）都是保护上限，不是实测需求**（教材 §16.4.2：按复合参考 ≈0.41 Gb 的体量外推，建索引用量在个位数 GB 量级，集群未实测）。
- **命令**：3.1 的同一作业的第 2 步，无需额外命令。要点是 L83 用 `--sjdbOverhang $((READLEN - 1))`
  （`READLEN` 默认 150，L41）而不是写死 149；L84 用 `--limitGenomeGenerateRAM "${GENOME_RAM}"`。单独重建时：删掉 `$Q/dual_idx/SA` 后重投 3.1 的作业。
- **产出文件**：`$Q/dual_idx/`（`SA`、`SAindex`、`chrName.txt`、`chrLength.txt`、`genomeParameters.txt`、
  `sjdbInfo.txt` 等）、`$Q/dual_idx/Log.out`。
- **检查点**：
  1. `$Q/dual_idx/SA` 存在且非空（脚本 L78 就是拿它当「已建好」的判据）；
  2. `$Q/dual_idx/chrName.txt` 里的序列数等于 `grep -c '^>' $Q/ref/dual.fa`，且**没有重复行**——
     重名时 STAR 不报错，`chrName.txt` 会老老实实列两条同名（教材 §16.5.1）；把建索引的墙钟时间与峰值内存记进 §4（作业日志里 `qstat -j` 或 `-j y` 的输出）；
  3. `genomeParameters.txt` 里 `sjdbOverhang` 的值等于你的读长 − 1（读长 150 时是 149，设例）。
- **出错信号**：`not enough memory`／作业被 SGE 直接杀 → `GENOME_RAM` 必须**小于** `h_vmem`，
  两个一起调（作业失分点里写 `--limitBAMsortRAM` 是错的，本步用的是 `--limitGenomeGenerateRAM`）；内存不够又不想调队列 → 改走 Salmon gentrome 路线（教材 §16.4.2 硕士选读块），但那要另写一套命令，与本脚本不兼容。
  `chrName.txt` 出现重复名却一路跑通 → 索引里的重名序列已经被合进一个键（→ §16.5.1）。

### 3.3 竞争性比对与按前缀拆分

- **目的**：一次比对让两个物种竞争同一个读段，只保留唯一比对（`--outFilterMultimapNmax 1`，L103），
  再按基因名前缀把计数拆成**两份互不混合**的矩阵。这一步的产出决定后面所有结论，而它错的时候不报错。
- **命令**：同一作业第 3 步（L89–111）。循环从 `samples.tsv` 逐行读 `sample r1 r2 _rest`（L90）；
  L94–95 **按 R2 列自动判单/双端**（空、`-`、`NA` 都只传一个文件）；L96–98 逐个检查读段文件存在；L100–104 调 STAR（`--quantMode GeneCounts`、`--outSAMtype BAM SortedByCoordinate`）；L105 `samtools index`；
  L107–110 用 `awk` 按 `^HOST_`／`^PATH_` 拆成 `counts/host/<S>.tsv` 与 `counts/path/<S>.tsv`，取 `$STRAND_COL` 列（默认 4，L46）。
- **产出文件**：每样本 `$Q/star/<S>_ReadsPerGene.out.tab`、`<S>_Log.final.out`、
  `<S>_Aligned.sortedByCoord.out.bam`（＋`.bai`）；`$Q/counts/host/<S>.tsv`、`$Q/counts/path/<S>.tsv`。
- **检查点**：
  1. 日志里 `[INFO] <S>: 单端`（L99）应出现 18 次且**全是单端**（`PRJNA661210` 是单端数据）；
  2. 两份计数文件的基因名分别**只**带一种前缀，行数分别等于该物种注释的基因数——两个数都要抄进 §4，
     对不上就是「有些基因根本没条目」（回 3.1 的检查点 3／4）；
  3. **链特异性列选对没有，用数据自己验**。`ReadsPerGene.out.tab` 的第 2/3/4 列是**无链/正链/反链**三套计数，
     三者满足恒等式 `第 2 列 = 第 3 列 + 第 4 列`（每一行都成立）——这是 STAR 的输出定义，可用你自己的表直接核：
     ```bash
     awk 'NR>4 && $2 != $3 + $4 {print "恒等式破了:", $0}' "$Q/star/<你的一个样本>_ReadsPerGene.out.tab"  # 必须无输出
     ```
     判据是**正链与反链的关系**，不是「比无链列高」：链特异性建库时，正确的那一列会拿到绝大多数计数，另一列接近 0（本例的链特异性答案是让 `STRAND_COL` 取 3 或 4 中的一个）；
     **无链建库时第 3、4 列近似各占一半、无链列是两者的和**，此时 `STRAND_COL` 一律取 2。所以先看 `第 3 列 / 第 4 列` 的比值：一边压倒另一边 → 链特异性文库，`STRAND_COL` 取压倒的那一列；两者接近对半 → 无链文库，取 2。
     **本数据的建库方案以 README p03 节/方法学为准**，拿不准时按无链（2）跑一遍并与链特异性结果对照，不要凭「三列差不多就是没链特异性」下结论（那条推理是错的：无链列本来就该等于另两列之和）。
  4. **不要只看列，还要看基因方向**：链特异性的「正/反」是相对基因的 `+`/`-` 而言。抽 3–5 个基因，
     把 `dual.gtf` 第 7 列（strand）与计数表并起来看：
     ```bash
     awk -F'\t' '!/^#/ && $3=="gene" {print $9}' "$Q/ref/dual.gtf" > /dev/null   # 仅确认属性列可读
     grep -v '^#' "$Q/ref/dual.gtf" | awk -F'\t' '$3=="gene" && match($9, /gene_id "[^"]*"/) {g=substr($9,RSTART+9,RLENGTH-10); print g"\t"$7}' > genes_strand.tsv
     awk -F'\t' 'NR==FNR{s[$1]=$2; next} FNR>4 && ($1 in s) {print $1"\t链="s[$1]"\t无链="$2"\t正链="$3"\t反链="$4}' genes_strand.tsv "$Q/star/<你的一个样本>_ReadsPerGene.out.tab" | head
     ```
     `链=+` 的基因应当是「正链列」占优、`链=-` 的应当是「反链列」占优；**混着占优或者刚好相反**，说明列选反了（读成噪声矩阵而流程照常跑完），回到上一步重选。
- **出错信号**：`[FATAL] <S>: 找不到读段文件（FASTQ）`（L97 原文）→ 多半是 `samples.tsv` 的 R2 列留空，
  导致 `treatment` 错位进 R2、标签被拿去当文件名查（教材 §16.5.3 第一处风险，报错指向处理标签而不是列错位）；同一文件被写进 R1 与 R2 → STAR 会把两个文件名当一对读入、按双端解释；
  **具体定量后果教材未在授权环境验证，本章因此不写任何定量断言**，只把它列为「必须用样本表拦截的输入形态错误」（教材 §16.5.3 第二处风险）；
  `multimap_pct` 很高但两侧计数都正常 → 那是重复序列与旁系同源基因家族造成的同物种多重命中，**不能直接读成「跨物种歧义严重」**（该列是混合指标，教材 §16.4.2）。
  计数矩阵看着能吃但结论反了：`STRAND_COL` 全选默认 4，就会得到一份几乎全是噪声的矩阵（→ §16.5.1 的静默链末端，也在 §16.5.3）。

### 3.4 生物量曲线与交叉比对本底

- **目的**：把「病原占比」逐时点算出来，一是看接种是否同步（重复间是否同数量级），二是**把交叉比对本底
  变成一个可披露的数**（未接种对照行）。这正是三条拆分路线里「可审计 vs 不可审计」的分界（教材 §16.4.2）。
- **命令**：同一作业第 4 步（L114–129）。L116 写表头；L117 重新读 `sample r1 r2 treatment time`
  （**这次要 treatment 与 time**，所以 3.1 的样本表口径在这里才真正生效）；L121–122 两侧计数求和；L124 从 `_Log.final.out` 的 `multiple loci` 行取多重比对率；L125–127 用 `awk` 算 `path_pct`。
- **产出文件**：`$Q/qc/biomass.tsv`（7 列：`sample treatment time host_reads path_reads path_pct multimap_pct`）。
- **检查点**：
  1. **19 行 = 表头 + 18**；`treatment` 列只有 `mock`／`inoculated` 两种值，`time` 列只有 12/24/48；
  2. **定性判据（README L85）**：`mock` 行的 `path_pct` **应接近 0**（把这三个数抄进 §4 并标「本流程的
     交叉比对本底」）；`inoculated` 行的 `path_pct` **应随 hpi 单调上升**（预期、未实测，看形状不看小数）；
  3. `multimap_pct` **逐时点报告**，不要只给全表平均——它是教材 §16.4.3 三道防线里唯一能在结果里留下痕迹的
     那一道；`host_reads + path_reads = 0` 的行，`path_pct` 的 0 是**占位值**，记缺失、不参与计算。
- **出错信号**：`mock` 行 `path_pct` 与 `inoculated` 相当 → 交叉比对本底失控（前缀没错的话先查比对参数与
  是否混进了别的样本）；同一时点重复间**跨一个数量级** → 接种不同步，建模前必须处理并在方法学写明；全表 `path_pct` 都是 0 → 数错在 3.3 的前缀拆分或 `STRAND_COL`；
  曲线很漂亮但下游不可用 → 你用的是「文件头部截取」样本，**绝对丰度不可信**，只能作形状判读（→ §16.5.3：功效贴地板、`P = D_used × f_P` 必须自己粗算一遍再解读「没有显著基因」）。

### 3.5 清洗蛋白 header（OrthoFinder 的输入前提）

- **目的**：OrthoFinder 只取每个 header 第一个空格前的部分当 accession，带描述的 header 极易跨文件撞名；
  更根本的是**所有菌株的蛋白集必须用同一注释流程、同一版本、同一参数产生**，否则「物种特异基因」是注释伪影（脚本头 L26–27、教材 §11.4.8）。
- **命令**（`qsub`；第一次投 `03_effector_screen.sh`）：

  ```bash
  cd "$P03/work"
  cp <课程仓库路径>/03_code/phd/scripts/03_effector_screen.sh ./effector_screen.sh
  # 在副本 L37 之前插入六行赋值（同样是 ${X:?…}，且不能出现 $P03）
  #   PROT_DIR=<各菌株 .faa 目录绝对路径>   FOCAL=<目标菌株 faa 文件名主干，见下>
  #   HOST_PROT=<宿主蛋白 fasta 绝对路径>
  #   PFAM_HMM=<${NGS_DB:-/data/db}/pfam 下的 Pfam-A.hmm 绝对路径>
  #   EFFECTORP_PY=<EffectorP-3.0 目录>/EffectorP.py
  #   OUTDIR=<展开后的绝对路径>/work/p03_screen
  grep -n 'PROT_DIR=\|FOCAL=\|HOST_PROT=\|PFAM_HMM=\|EFFECTORP_PY=\|ORGANISM=\|NLR_PFAM=\|h_vmem' effector_screen.sh
  grep -c '\$P03' effector_screen.sh        # 必须 0
  qsub effector_screen.sh
  ```

  脚本这一段做什么：L50–52 检查五个工具、L53–54 缺 `signalp6` 直接 FATAL、L55 检查 `EFFECTORP_PY` 路径；L61–65 每株 `seqkit replace -p '\s.*' -r '' -w 0` 去掉空格后的描述，再给 ID 加 `<株>|` 前缀。
- **`PROT_DIR` 的蛋白集从哪来（集群没预置，脚本 L37 标「主线数据待定」）**：`06_data/reference/README.md` 只登记了 `/data/db/dual_ref/`（宿主＋病原**转录组**，给 Salmon decoy 索引用）与 `/data/db/pfam/`，**没有多菌株蛋白集**。所以 `PROT_DIR` 一定是你自建的目录；能跑通的最小集是三份**同一 release** 的蛋白 FASTA。Ensembl Genomes release-61 直链（登录节点联网，2026-11-11 核过 HTTP 200）：

  ```bash
  mkdir -p "$P03/work/proteomes"; B=https://ftp.ensemblgenomes.ebi.ac.uk/pub
  # 病原 70-15：目录名 magnaporthe_oryzae，assembly 名 MG8，基因 ID 为 MGG_…（与 3.1 的病原 GTF 同源）
  curl -sSL "$B/fungi/release-61/fasta/magnaporthe_oryzae/pep/Magnaporthe_oryzae.MG8.pep.all.fa.gz" | zcat > "$P03/work/proteomes/70-15.faa"
  # 近缘种（非水稻病原，做「菌株特异」的对照用）：Magnaporthe poae
  curl -sSL "$B/fungi/release-61/fasta/magnaporthe_poae/pep/Magnaporthe_poae.Mag_poae_ATCC_64411_V1.pep.all.fa.gz" | zcat > "$P03/work/proteomes/Mp_64411.faa"
  # 宿主（植物库 IRGSP-1.0）
  curl -sSL "$B/plants/release-61/fasta/oryza_sativa/pep/Oryza_sativa.IRGSP-1.0.pep.all.fa.gz" | zcat > "$P03/work/proteomes/Oryza_IRGSP1.faa"
  grep -c '^>' "$P03/work/proteomes/"*.faa              # 三份都非 0，数记进 §4
  head -1 "$P03/work/proteomes/70-15.faa" | cut -c1-50 # 应形如 >MGG_07573T0 pep chromosome:MG8:…
  ```

  三条同时成立才不算注释伪影（教材 §11.4.8）：① 全部同一 release（上面都是 61），**不要混用 NCBI 的 70-15 注释**——ID 体系不同，3.12 的 `match` 会成片 `NA`；② 只在同一注释流程的产物之间比，跨来源（Ensembl 预测 vs 自己 Braker 重注释）先统一重注释；③ 蛋白 ID 能对上病原 GTF 的 `gene_id`（下面的 `head`+`grep` 一起验）。真实课题要 ≥4 株（含弱毒/非致病近缘种）才有生物学意义，上面只是**让流程跑通的最小集**，报告里要写明。
- **产出文件**：`$S/ortho/proteomes_clean/<株>.faa`（每株一个）。
- **检查点**：
  1. 每株一个 `.faa`，条数记进 §4（同一注释流程下各株应在同一量级；**不设具体阈值**）；
  2. header 已是 `<株>|<gene>` 形态：`grep '^>' $S/ortho/proteomes_clean/<株>.faa | head -3` 应无空格、
     无描述词；`grep -c ' ' …` 只看 header 行应为 0。
- **出错信号**：`OrthoFinder ERROR: A duplicate accession was found` → header 没清干净（讲义 ⑨-E5）；
  某株特异基因数高出数倍 → **先查注释一致性，不能当生物学发现写进报告**（教材 §11.4.8 与讲义 ⑥ 末行）。
  这一路最终会进 3.12 的 `strain_specific` 证据列：注释不一致时这一列本身失真，而排序表照常输出 → 属于「证据链缺列/错列仍出表」的那一类（→ §16.5.4 第三处核对）。
- **`FOCAL` 到底填哪个菌株（这一条填错会让 3.12 出现大量 `NA`）**：`FOCAL` 是**蛋白文件名主干**，
  而 3.12 用 `strip_pfx` 去掉 `PATH_`／`<株>|` 前缀后按 **基因 ID** 与病原侧 LRT 结果对齐。病原转录组是用哪份 GTF 比对进去的，`FOCAL` 就必须是**同一份注释的同名字空间**（本课程是 70-15）。
  接种用的是 `Guy11`（样本表里写作 `G11`），那是**叶片里的活菌株名**，不等于参考注释的菌株；若把它当成 `FOCAL` 填进去而 `PROT_DIR` 里那份 70-15 蛋白的 ID 与之不同名，3.7 的 `specific_genes` 与 3.12 的 `lrt_padj` 会整列 `NA`（流程不报错）。
  **照做**：

  ```bash
  ls "$PROT_DIR"                                  # 看 <主干>.faa 的实际文件名
  head -1 "$PROT_DIR/<主干>.faa"                  # 看蛋白 ID 命名（应能对上病原 GTF 的 gene_id）
  grep -v '^#' <病原 GTF> | awk -F'\t' '$3=="gene"' | grep -o 'gene_id "[^"]*"' | head -3
  ```

  两处 ID 去掉引号与前缀后**同名前缀一致**（如都是 `MGG_` 开头）才可填。

### 3.6 OrthoFinder 直系同源聚类

- **目的**：得到跨菌株的直系同源群，才能谈「哪些基因只有目标菌株有」。这是一条耗时作业，排队期间写报告。
- **命令**：同一作业第 2 步（L69–70）：`orthofinder -f "${CLEAN}" -t "${THREADS}" -a 4 -S diamond -o "${ORTHO}/out"`。
  L71–72 用 `find` 定位 `Results_*`，找不到即 `[FATAL]`。
- **产出文件**：`$S/ortho/out/Results_<日期>/`（`Orthogroups/`、`Phylogenetic_Hierarchical_Orthogroups/`、
  `Comparative_Genomics_Statistics/`、`Species_Tree/`）。
- **检查点**：
  1. `Results_*` 目录存在，`Orthogroups/Orthogroups.GeneCount.tsv` 与 `Orthogroups_UnassignedGenes.tsv` 都在
     （后两个是 3.7 的两路输入）；
  2. 录入运行时长、`-S diamond` 与版本（`orthofinder -h | head -2`）；`Comparative_Genomics_Statistics/`
     里各株的基因总数与 3.5 的计数一致。
- **出错信号**：`A duplicate accession` → 回 3.5；`找不到 OrthoFinder 结果目录`（L72 原文）→ 作业中途失败、
  或 `-f` 指到了父目录而不是 `proteomes_clean`；同一批数据两次跑出不同的特异基因条数 → OrthoFinder 的物种树与 `-a` 设置变了，报告里要写清用的是哪一版结果（**不要拿两次结果拼表**）。
  特异基因条数异常本身不是报错，它会以「候选表里 strain_specific 一列几乎全真」的形式悄悄进排序 → 回 §16.5.4 的量级与证据链核对。

### 3.7 物种特异基因：两个来源都要取

- **目的**：只取孤儿基因会**系统性漏掉株内扩张的特异家族**（脚本 L74–76 的注释与教材 §11.4.8）。
  两个来源并集才是可辩护的输入。
- **命令**：同一作业第 3 步（L77–95）。L82–84 从 `Orthogroups.GeneCount.tsv` 取「只有 FOCAL 计数 > 0」的
  orthogroup——**内层循环必须到 `NF-1`**，因为末列是 `Total`；L86–88 取 `Orthogroups_UnassignedGenes.tsv` 里 FOCAL 的孤儿基因；L90–94 把特异 orthogroup 内 FOCAL 的成员基因追加进去（注意是 `>>` 追加）；L95 `sort -u` 去重。
- **产出文件**：`$S/ortho/specific_OGs.txt`、`$S/ortho/specific_genes.txt`。
- **检查点**：
  1. 两个文件都非空；抄进 §4 的条数要注明「两来源并集」。**不要拿「基因数 > orthogroup 数」当判据**——
     一个扩家族可能只含 1 个成员，孤儿基因也可能整族未进 orthogroup，两个数的大小关系由数据决定，不满足不是漏项。**改用逐 ID 核对**：
     ```bash
     wc -l < "$S/ortho/specific_genes.txt"
     sort -u "$S/ortho/specific_genes.txt" | wc -l        # 与上一行必须相等（脚本 L95 已 sort -u）
     cut -d'|' -f1 "$S/ortho/specific_genes.txt" | sort -u   # 只应打印 FOCAL 一个名字
     # 特异 OG 那一侧到底贡献了几条：拿 OG 表里 FOCAL 的成员数与孤儿数分别数一遍，两数之和≥并集条数
     ws="$S/ortho/out/Results_"*
     awk -v f="<你的 FOCAL>" 'BEGIN{FS="\t"} NR==1{for(i=2;i<=NF;i++) if($i==f) k=i; next}
          {n=0; for(i=2;i<NF;i++) if(i!=k && $i>0) n++; if(k && $k>0 && n==0) s+=split($k,a,", ")}
          END{print "特异 OG 贡献成员条数：", s}' "${ws}/Orthogroups/Orthogroups.GeneCount.tsv"
     ```
     第三行出现别的株名 → `FOCAL` 与 `GeneCount.tsv` 表头不匹配，或 `>>` 追加时串了文件。最后那条 awk 的 `s` 必须 > 0：为 0 说明第二个来源（扩家族）根本没贡献，只走到了孤儿基因。
  2. **每条候选仍须 `tblastn` 回查其他菌株的基因组**，脚本不代做（L97–99），这一步的结论写进报告的方法节。
- **出错信号**：`specific_genes.txt` 只有几百条而目标是数千基因的菌株 → `FOCAL` 名字与 `GeneCount.tsv`
  表头对不上（`awk` 里 `k` 为空会静默输出空表）；条数对但大量是「蛋白集里没有」→ 那是注释漏注，`tblastn` 回查基因组能区分「真缺失」与「漏注释」；
  把 `strain_specific` 当毒力证据直接写结论 → 它只是候选排序的一列证据，不是功能鉴定（→ §16.5.4）。

### 3.8 SignalP 6：先认列，再认数

- **目的**：拿到每个蛋白的信号肽概率与切割位点。**列序取错不会报错**，只会把整张候选表的证据方向反转
  （教材 §16.5.4 明写的历史案例）。
- **命令**：同一作业第 4 步（L103–104）：
  `signalp6 --fastafile "${CLEAN}/${FOCAL}.faa" --organism "${ORGANISM}" --format none --output_dir "${SEC}/signalp" --mode fast`；L106–107 按 `$2 != "OTHER"` 抽 `secreted_ids.txt`。`ORGANISM` 默认 `eukarya`（L42），真菌/卵菌都用它。
- **产出文件**：`$S/secretome/signalp/prediction_results.txt`、`$S/secretome/secreted_ids.txt`。
- **检查点**：
  1. **列名**：`head -1 $S/secretome/signalp/prediction_results.txt`，确认**第 2 列 `Prediction`、第 3 列
     `OTHER`、第 4 列 `SP(Sec/SPI)`**、末列 `CS Position`；
  2. **行级抽检**：挑一行 `Prediction = OTHER` 的记录，它的第 3 列应高、第 4 列应低；反了就是取错列；
  3. 量级：分泌组一般占蛋白组 5%–10%（经验法则），`secreted_ids.txt` 的行数与 3.5 的蛋白总数一起抄进 §4。
- **出错信号**：`command not found: signalp6` → 不在 conda 里，按 §0 申请安装（讲义 ⑨-E6）；
  取第 3 列当信号肽概率（**方向整体反了、且不报错**，因为取到的确实是 0–1 的合法数）→ 这是教材 §16.5.4 的核心案例，回看你的列名核对；
  `--organism` 配错 → 命中数掉到个位数（→ §16.5.4：候选数量异常的两个方向都说明输入形态错了，不是生物学发现少了）。

### 3.9 切成熟肽、跨膜排除、EffectorP

- **目的**：把三个步骤串成一条**证据链**：信号肽 → 成熟肽上做跨膜排除 → 分类器给后验概率。
  跨膜排除**必须做在成熟肽上**：信号肽的疏水 h 区与跨膜螺旋理化性质高度重合，做在全长上会把真效应子批量剔除，而流程不报错（教材 §16.4.6 第二步）。
- **命令**：同一作业 L110–149。L110–114 从 `CS pos: a-b` 解析出成熟肽起点：**`CS pos: 17-18` 表示切在第 17
  与第 18 个残基之间，成熟肽首残基是第 18 位（`a+1`）**，脚本写 `a[3]+1`；L115 `seqkit grep` 抽全长；L116–136 用内联 Python 按起点切片，写出 `mature.faa`；
  L139–148 有 `tmhmm` 就跑并抽无跨膜 ID，**没有则 `[WARN]` 并把 `mature.faa` 复制成 `mature_noTM.faa`**；L149 `python "${EFFECTORP_PY}" -i "${SEC}/mature_noTM.faa" -o "${SEC}/effectorp.tsv"`。
- **产出文件**：`$S/secretome/secreted_full.faa`、`cs_pos.tsv`、`mature.faa`、`mature_noTM.faa`、
  `effectorp.tsv`；有 tmhmm 时另有 `tmhmm.out`、`no_tm_ids.txt`。
- **检查点**：
  1. **EffectorP 的输入必须是 `mature_noTM.faa`**（L149 写死），不是 `secreted_full.faa`，也不是 `mature.faa`。
     **没有 `tmhmm` 时这一步是「没做完」而不是「做完了」**：脚本 L145–147 只打一行 `[WARN]` 就把 `mature.faa` 原样复制成 `mature_noTM.faa`，跨膜候选一个没剔，接着 L149 照样跑 EffectorP。两条路选一条走到底：
     - **走 A（补做，推荐）**：把 `mature.faa` 传到 <https://dtu.biolib.com/DeepTMHMM>（登录节点才能联网），
       下载结果后自己重建无跨膜 FASTA，并**重跑 EffectorP 与 3.12 的排序**：
       ```bash
       # 1) 从 DeepTMHMM 结果里取「无跨膜」的 ID（列名以服务实际输出为准，下面是常见形态）
       grep -v '^#' <DeepTMHMM 的 prediction 结果> | awk -F'\t' '$2=="0" || $2=="False"{print $1}' | sort -u > "$S/secretome/no_tm_ids.txt"
       # 2) 用这些 ID 从成熟肽重建真正过滤过的 FASTA
       seqkit grep -f "$S/secretome/no_tm_ids.txt" "$S/secretome/mature.faa" -w 0 > "$S/secretome/mature_noTM.faa"
       grep -c '^>' "$S/secretome/no_tm_ids.txt" ; grep -c '^>' "$S/secretome/mature_noTM.faa"   # 两个数应相同
       # 3) 重跑分类器（模板见 3.5 的副本做法，单独投一个小作业）
       python "$EFFECTORP_PY" -i "$S/secretome/mature_noTM.faa" -o "$S/secretome/effectorp.tsv"
       ```
       重跑 EffectorP 后**必须回到 3.11/3.12 重算候选表**（`candidate_effectors.tsv` 的行来自 `effectorp.tsv`），否则排序表里还是那批未过滤的候选。
     - **走 B（不补做）**：候选表与方法学里**逐处标明「未做跨膜排除」**，候选数按「未过滤」报告，
       报告结论只写「含跨膜蛋白的候选集」，不得写成「已完成三步筛选」。加分项是走 A。
  2. `cs_pos.tsv` 抽一行对账：`CS pos: 17-18` 那条的起点应写 18，且 `mature.faa` 里该蛋白长度正好少 17 个残基
     （教材 §16.4.6 的设例）；用 `seqkit fx2tab -l -n` 比全长与成熟肽的长度差即可；
  3. `effectorp.tsv` 的列数与前 3 行：第一列是蛋白 ID，后验概率列名含 `prob` 或 `score`
     （R 脚本 L104 就是按这个名字取列，L125 存成 `effectorp_prob`）。
- **出错信号**：日志里 `[WARN] 未找到 tmhmm：跳过跨膜排除` → **这不是提示而是缺口**，按检查点 1 走 A 或 B；
  候选数突破三千 → 先查是不是把**未切信号肽的全长序列**（甚至核酸序列）投给了分类器（教材 §16.5.4 原文口径）；`seqkit grep` 抽到 0 条 → `secreted_ids.txt` 是空的（回 3.8）；
  整条链看着跑完、候选表也出来了，但用的是 prompt 里那句「EffectorP 阈值 0.85，所以假阳性被控制」——**0.85 是设例**，EffectorP 给的是后验概率、没有零假设，把 0.5 调到 0.8 只换切点，不产生 FDR（→ §16.5.4：预测不是鉴定）。

### 3.10 宿主 NLR 结构域扫描

- **目的**：在宿主蛋白组里找出「既有 NB-ARC、又伴随 LRR 或 TIR」的候选。**找到的是结构域，不是功能基因**：
  单个 NB-ARC 片段可能是退化假基因，脱离 NB-ARC 的单 LRR 命中没有特异性（教材 §16.4.7 三道落差）。
- **命令**：同一作业第 5 步（L154–165）。L154 缺 `.h3i` 时 `hmmpress`；L155–156
  `hmmscan --cpu "${THREADS}" -E 1e-5 --domtblout "${NLR}/host_pfam.domtbl" -o /dev/null "${PFAM_HMM}" "${HOST_PROT}"`；L157–160 每个 Pfam 号写一个 `hit_<PF>.txt`；
  L162–164 `comm -12` 取 `PF00931 ∩ (PF00560 ∪ PF07723 ∪ PF01582)`（`NLR_PFAM` 默认值 L45）。
- **产出文件**：`$S/nlr/host_pfam.domtbl`、`$S/nlr/hit_PF00931.txt`、`hit_PF00560.txt`、`hit_PF07723.txt`、
  `hit_PF01582.txt`、`$S/nlr/nlr_candidates.txt`。
- **检查点**：
  1. 四个 `hit_*.txt` 都存在；`nlr_candidates.txt` 的条数（L165 直接打印）**不大于** `hit_PF00931.txt`
     的条数——交集只能等于或小于被交集的那一侧，**相等不算错**（一个基因可能既有 NB-ARC 又带 LRR，此时候选集就是整个 NB-ARC 集合）。**要用 ID 核对交集真的生效，而不是拿不等号当判据**：
     ```bash
     comm -23 <(sort -u "$S/nlr/nlr_candidates.txt") <(sort -u "$S/nlr/hit_PF00931.txt")   # 必须无输出
     comm -12 <(sort -u "$S/nlr/nlr_candidates.txt") \
              <(cat "$S/nlr/hit_PF00560.txt" "$S/nlr/hit_PF07723.txt" "$S/nlr/hit_PF01582.txt" | sort -u) \
              | wc -l                                                    # 必须等于候选总数
     wc -l < "$S/nlr/hit_PF00931.txt" ; wc -l < "$S/nlr/nlr_candidates.txt"
     ```
     第一条非空 = 候选里混进了没有 NB-ARC 的基因（交集逻辑被改坏了）；第二条小于候选总数 = 有候选缺 LRR/TIR。
  2. 判据必须是「NB-ARC ∩ (LRR ∪ TIR)」：只有 LRR 命中的**不在**候选里（脚本 L161 的注释与教材 §16.4.7 一致）；
     报告里要写明这一点，并说明「交集等于全集」是可能的合法结果，不是漏项。
  3. 报告里必须写清这一条限制：参考注释会漏 NLR，正式分析需用 NLR-Annotator 在基因组上回补（L166）。
- **出错信号**：`Failed to open binary auxfiles for Pfam-A.hmm: use hmmpress first`（讲义 ⑨-E7）→ 索引没建，
  L154 已自动补，若仍报就是 `PFAM_HMM` 指错了文件或没有写权限；`domtblout` 是空的 → `HOST_PROT` 与 `PFAM_HMM` 传反了（hmmscan 的参数顺序是 `库 查询`）；把结构域命中当抗病基因写进结论 → 教材 §16.4.7 三道落差；
  再叠上「侵染后显著上调」这条硬过滤会系统性漏掉组成型低表达的核心 NLR（→ §16.5.4 的「结构域 ≠ 功能」；对应的练习是教材 §16.7 第 9 题）。

### 3.11 分开归一化 + 两套 LRT + 诊断图

- **目的**：宿主与病原**分别**建 `DESeqDataSet`、**分别**估 size factor。合起来算 TPM 或塞进同一个 `dds`，
  方向性错误就已经发生，后面的检验拦不住（教材 §16.5.2）。
- **命令**（7 个位置参数；`Rscript` 也必须在计算节点跑，把下面存成 `run_lrt.sh` 再 `qsub`）：

  ```bash
  cd "$P03/work"
  cp <课程仓库路径>/03_code/phd/scripts/03_dual_deseq2_lrt.R ./dual_deseq2_lrt.R
  # ① heredoc 用带引号的 <<'EOF'：内容原样落盘，$ 与反引号都不被当前 shell 展开
  cat > run_lrt.sh <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N p03_lrt
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  #$ -l h_vmem=8G
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_interaction
  Rscript "__WORK__/dual_deseq2_lrt.R" "__WORK__/p03_dual/counts/host" \
          "__WORK__/p03_dual/counts/path" "__WORK__/samples.tsv" \
          "__WORK__/p03_screen/secretome/effectorp.tsv" \
          "__WORK__/p03_screen/secretome/signalp/prediction_results.txt" \
          "__WORK__/p03_screen/ortho/specific_genes.txt" \
          "__WORK__/lrt"
  EOF
  # ② 把占位符换成你自己的绝对路径（本地替换，不写进作业）
  sed -i "s|__WORK__|$P03/work|g" run_lrt.sh
  grep -c '__WORK__' run_lrt.sh      # 必须 0：占位符没换干净，作业会去找不存在的目录
  grep -c '\$P03' run_lrt.sh         # 必须 0：作业不继承 $P03
  cat run_lrt.sh                     # 投递前逐行核对：绝对路径已内联、7 个参数齐全、作业头 #$ 完好
  bash -n run_lrt.sh                 # 语法自检，应空输出
  grep -n 'dual_deseq2_lrt.R' run_lrt.sh   # 必须是绝对路径，不是 ./dual_deseq2_lrt.R
  qsub run_lrt.sh
  ```

  **为什么走「占位符 + 就地替换」而不是直接写 `${P03}`**：§2 已定「作业不继承 `$P03`」。heredoc 若写成不带引号的 `<<EOF`，`${P03}` 会在**生成脚本的那个终端**里被展开——当时看着没问题，换个终端或重开会话再做就得到空串（`Rscript "/work/dual_deseq2_lrt.R"`，本机实测）；若写成带引号的 `<<'EOF'` 却仍写 `${P03}`，它会原样留在作业里，投递后 `set -u` 直接 `unbound variable`（本机实测）。所以 heredoc 只负责落盘骨架、路径由 `sed` 就地内联，两条 `grep -c` 必须都是 0。

  **R 脚本路径也写绝对路径**：`#$ -cwd` 让作业以投递目录为工作目录，`./` 通常能解析；但一旦换目录投递或作业被重启，`Rscript ./dual_deseq2_lrt.R` 就报 `cannot open file`。前面 7 个数据参数全是绝对路径，脚本自己也该是。

  `h_vmem=8G` 是**申请值、不是实测需求**（本步只用 R 与 ggplot2）。脚本做什么：L34–44 读计数并按基因名取交集对齐（**不依赖各文件行序**），缺文件报 `缺少计数文件: …`（L37）；
  L46–50 读样本表、断言三列齐全、`relevel(ref="mock")`、`time` 转因子；
  **宿主侧** L59 `design = ~ treatment + time + treatment:time`、L60 `rowSums(counts >= 10) >= 3` 过滤、L61 `estimateSizeFactors`、L62 `DESeq(test="LRT", reduced = ~ treatment + time)`、L64 写结果；
  **病原侧** L68–69 只取 `inoculated`、L70 `design = ~ time`、L71 `rowSums(counts) > 0`、L73 `estimateSizeFactors(type = "poscounts")`、L74 `reduced = ~ 1`、L76 写结果；L80–93 出诊断表与散点图。
- **产出文件**：`$L/host_timecourse_LRT.csv`（L64）、`$L/pathogen_timecourse_LRT.csv`（L76）、
  `$L/pathogen_sizefactor_diagnostic.csv`、`$L/pathogen_sizefactor_diagnostic.png`（L85–93）。**注意这是 CSV（逗号分隔）**：脚本 L64/L76 用的是 `write.csv`。§7 要交的是 `.tsv`，**改名不会改分隔符**，按 TSV 读会把整行当一列。
  转换要保留**行名**（基因 ID 就在行名里，丢掉就再也对不上 3.12 的表）。**不要用 `tr ',' '\t'`**：CSV 里带引号与逗号的字段会被拆坏。走 R 最稳（在计算节点、同一环境里跑）：

  ```bash
  # $L 是 shell 变量、通常没有 export：用位置参数传进去，不要用 Sys.getenv("L")
  # （Sys.getenv 读到空串时 file.path("", "x.csv") 得到 "/x.csv"，报错信息离现场很远——本机实测）
  Rscript -e 'a <- commandArgs(TRUE); L <- a[1]
  for (s in c("host","pathogen")) {
      f <- file.path(L, paste0(s, "_timecourse_LRT.csv"))
      o <- file.path(L, paste0(s, "_lrt.tsv"))
      x <- read.csv(f, row.names = 1, check.names = FALSE)   # row.names=1 保住基因 ID 列
      write.table(x, o, sep = "\t", quote = FALSE, col.names = NA)  # col.names=NA 给行名留表头位
  }' "$L"
  ```

  要保住这个变量就先 `export L=$P03/work/lrt`；但**用位置参数比靠环境变量稳**，写成 `Rscript … "$L"` 时 `$L` 由当前 shell 展开，与 export 与否无关。若改成投 `conv_lrt.sh`，同一行要写成展开后的绝对路径（理由同 3.11 的 heredoc，见上）。

  更彻底的做法是改副本让脚本直接写 TSV（不动 `03_code/`）：把 L64/L76 的 `write.csv(…)` 换成 `write.table(…, sep="\t", quote=FALSE, col.names=NA)`，文件名同时改成 `.tsv`。无论哪种做法，转换后必须核对（三条都过才算成功）：

  ```bash
  awk -F'\t' '{print NF}' "$L/host_lrt.tsv" | sort -u   # 只打印一个数，且 = CSV 列数 + 1（多出的是行名列）
  wc -l < "$L/host_lrt.tsv" ; wc -l < "$L/host_timecourse_LRT.csv"   # 两个行数必须相等
  head -1 "$L/host_lrt.tsv" | cat -A                   # 表头以 ^I 分隔、以 ^I 开头（给行名留的空表头位）
  ```
- **检查点**：
  1. **先看诊断图再看任何 p 值**（L142 的 message 就是这句）。读法是**警示信号，不是诊断结论**：
     点沿侵染时点单调漂移 → **强烈提示** size factor 在吸收全局生物量变化，此时病原侧 p 值不能直接用；
     但**「点落在过原点虚线附近、不按时间排序」并不能证明归一化正确**——教材 §16.4.4 明写形态不能单独证明归一化正确（原因至少有三类：文库总量与组成同时变化、批次/操作差异、真实的全基因组上调）；
     也不能据此把时间漂移**断言**为「size factor 吸收了生物量」——那是机制假设，不是图的推论。**能说的话**：形态与「深度≈其唯一变异来源」的假设一致；**不能说**：归一化已被这张图证明正确。
     要判归一化是否成立，得另配独立对照（mock 组、加标/ERCC 一类的绝对量参照、技术重复），本数据只有 mock 组，所以「无法识别绝对变化」这条限制必须写进报告（教材 §16.5.2）。
  2. 两套设计写对了吗：宿主侧 `reduced` 是 `~ treatment + time`（不是 `~ 1`），病原侧是 `~ 1`；
     自由度手算进 §4——宿主 18 样本、6 个系数（含截距）→ 残差 `18−6=12`，交互项 `Λ` df=2；病原 9 样本、3 个系数（截距 + 两个时间对比）→ 残差 `9−3=6`；
  3. 病原侧用了 `poscounts`：`sizeFactors(dds_p)` 不再因为「每个基因至少有一个零」而算不出来；
     把 `pathogen_sizefactor_diagnostic.csv` 里 `size_factor` 的范围抄进 §4（**具体值以你的输出为准**）。
- **出错信号**：`缺少计数文件: …`（L37 原文）→ 目录传错，或 `samples.tsv` 的 `sample` 与 3.3 写出的
  文件名对不上（这是最常见的）；`every gene contains at least one zero, cannot compute log geometric means` → 病原侧早期稀疏，脚本已默认 `poscounts`，若仍出现说明你改的是另一个 `dds`；
  `the model matrix is not full rank` → 你把占比当协变量塞进了模型（讲义 ⑨-E4），本脚本不会这么干。最危险的是**没有任何报错**：宿主侧出现「全基因组普遍下调」这种大范围趋势、或诊断散点沿时间漂移却照常往下做。
  **这两种现象的正确表述是「第一嫌疑在分母」而不是「已证明是分母」**：合并矩阵/归一化出错会是这类形态，真实的全局响应也会（→ §16.5.2），本数据缺纯培养与绝对量参照，无法把两者分开。

### 3.12 候选效应子排序表

- **目的**：把三条证据合成一张可复排的排序表，并**明确权重是主观的**。它不是鉴定结果。
- **命令**：同一条 R 命令的后半（L124–138）。L124 以 `effectorp.tsv` 的 ID 为行；L125–129 依次挂上
  `effectorp_prob`、`signalp_prob`（按注释表头定位 `SP(Sec/SPI)`，找不到才回退第 4 列并 `warning`，L109–118）、`log2_baseMean`、`lrt_padj`、`strain_specific`；L131–132 `rank01()` 把每列换成 0–1 的秩；
  **L133–135 `score` = `log2_baseMean`、`signalp_prob`、`strain_specific` 三列秩的等权平均**；L136 按 `score` 降序；L137–138 写表。
- **产出文件**：`$L/candidate_effectors.tsv`（列：`gene`、`effectorp_prob`、`signalp_prob`、
  `log2_baseMean`、`lrt_padj`、`strain_specific`、`score`）。
- **检查点**：
  1. 表有数据行且行数等于 3.9 里 EffectorP 的候选条数（L143 会打印条数）；
  2. **`effectorp_prob` 与 `lrt_padj` 只作原始列输出、不进 `score`**——这一点与讲义原表的「四指标」不同，
     以脚本为准；报告里必须写明你用的权重与理由（L144–145 的提醒），并附三列原始值让读者能自己重排；
  3. `strain_specific` 是逻辑值转 0/1，与 3.7 的 `specific_genes.txt` 逐条能对上；`score` 落在 0–1 之间
     且表按它降序。
- **出错信号**：`score` 相同的一大批 → 三列里有两列是常量（`strain_specific` 全 TRUE 或全 FALSE）；
  按 `log2FoldChange` 做主排序 → LRT 下它只是某一对比较的附带值，不是被检验的量（教材 §16.4.5）；把 `score` 当 FDR → 它没有零假设；
  候选表很漂亮但报告写「鉴定了 N 个效应子」→ 动词越界（→ §16.5.4：预测与鉴定之间隔着分泌活性、瞬时表达、定位与敲除致病力四层实验）。

## 4. 结果记录表（学生填写，不预填；「自查判据」列给来源口径）

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 | 实查版本：STAR / Salmon / samtools / OrthoFinder / DESeq2 / hmmer / R | 版本号 | | 前四个应为 2.7.10b / 1.10.3 / 1.17 / 2.5.5（yml pin，L21/22/24/27）；**R 的 pin 是 4.3.1**（`r-base=4.3.1`，L39）；**DESeq2 与 hmmer 未 pin，填打印的实际值**（§16.3） |
| 3.1 | `dup_seqnames.txt` / `gtf_not_in_fasta.txt` | 空/非空 | | **两个都必须为空**；非空即 `[FATAL]`（脚本 L67/L73） |
| 3.1 | `.fai` 行数 vs FASTA 条数 | 条 | | 两者相等；不等＝重名（§16.5.1 ③） |
| 3.1 | 带 `HOST_`/`PATH_` 前缀的 `gene_id` 条数 vs 注释基因总数 | 条 | | 两侧之和＝总条数；出现裸 `gene_id` ＝没补第 9 列，3.3 会出两张空表（§16.5.1） |
| 3.2 | 建索引墙钟时间 / 峰值内存 | min / GB | | 60 GB 与 64 G 是**保护上限不是需求**（§16.4.2），你的实测值填这里 |
| 3.2 | `chrName.txt` 序列数 | 条 | | 等于 FASTA 条数、无重复行（STAR 遇重名不报错，§16.5.1） |
| 3.3 | 单/双端判定计数 | 次 | | 日志 `[INFO] …: 单端` 应为 18 次（`PRJNA661210` 单端） |
| 3.3 | 计数矩阵行数（宿主侧 / 病原侧） | 条 | | 各等于该物种注释基因数；对不上＝GTF 行被静默丢弃（§16.5.1） |
| 3.3 | 链特异性判读：第 3 列 vs 第 4 列的比值 / `STRAND_COL` 最终取值 | 比值 / 2·3·4 | | 恒等式 `第2列＝第3列+第4列` 必须逐行成立；一边压倒另一边＝链特异性，取压倒的那列；两者对半＝无链，取 2（§16.5.3） |
| 3.3 | 抽 3–5 个基因的 `链`（`+`/`-`）与占优列是否对应 | 对应/相反 | | `链=+` 应正链列占优、`链=-` 应反链列占优；相反或混占＝列选反了 |
| 3.4 | `biomass.tsv` 行数 / `multimap_pct` 逐时点 | 行 / % | | 19 行＝表头+18；`multimap_pct` 是**混合指标**，不可反推跨物种泄漏（§16.4.2） |
| 3.4 | `mock` 行 `path_pct`（交叉比对本底） | 定性/缺失 | | README L85：应**很低**；`host+path=0` 时 0 是占位值，记缺失（§16.5.3） |
| 3.4 | `inoculated` 行 `path_pct` 是否随 hpi 上升 | 是/否 | | 定性判据（预期、未实测）；跨数量级＝接种不同步 |
| 3.4 | `P = D_used × f_P` 粗算（用你自己的表） | 计数 | | 手算入口 §16.4.1.1；`D_used` 取 `host_reads+path_reads`，`f_P` 取 `path_pct/100` |
| 3.5 | 每株蛋白条数 | 条 | | 同一注释流程下同量级；注释不一致→特异基因伪影（§11.4.8） |
| 3.6 | OrthoFinder 结果目录 / 运行时长 / 版本 | 路径 / min | | `Results_*` 存在且两路输入表齐全 |
| 3.7 | `specific_OGs.txt` 行数 / `specific_genes.txt` 条数 | 条 | | 两来源并集，**大小关系由数据决定，不作判据**；改看 3.7 检查点 1 的三条 ID 核对（去重后条数不变、只剩 `FOCAL` 一个前缀、特异 OG 贡献成员数 > 0）；`tblastn` 回查未做则标「未复核」 |
| 3.8 | SignalP 第 3 列名 / 第 4 列名 | 列名 | | 必须是 `OTHER` / `SP(Sec/SPI)`；抽一行 OTHER 复核高低（§16.5.4） |
| 3.8 | 分泌组占比（`secreted_ids.txt` ÷ 蛋白总数） | 百分比 | | 经验法则 5%–10%；超出先查 `--organism` 与输入形态 |
| 3.9 | `cs_pos.tsv` 抽检：全长与成熟肽长度差 | 残基 | | 对 `CS pos: 17-18` 那条应为 17（设例，§16.4.6）；EffectorP 输入是 `mature_noTM.faa` |
| 3.9 | tmhmm 是否可用 / 补做工具 | 有/无 | | 无则这一环是「未做完」：按 3.9 检查点 1 走 A（重建无跨膜 FASTA → 重跑 EffectorP → 重算 3.12）或走 B（逐处标「未过滤」）；只在方法学写 DeepTMHMM 不算处置 |
| 3.10 | 四个 `hit_*.txt` 条数 / `nlr_candidates.txt` 条数 | 条 | | 候选条数**不大于** `hit_PF00931`（相等是合法结果）；判据是 NB-ARC ∩ (LRR ∪ TIR)，用 3.10 检查点 1 的 `comm` 两条核对交集真的生效（§16.4.7） |
| 3.11 | 诊断散点形态（正常/沿时间漂移） | 定性 | | **只作警示不作证明**：过原点直线且不按时间排序＝没看到可疑形态，不等于归一化正确；沿时间漂移＝要停下来查分母（§16.4.4、§16.5.2） |
| 3.11 | 两套模型与自由度 | 公式 / df | | 宿主 `~treatment+time+treatment:time`，reduced `~treatment+time`，残差 12；病原 `~time`，reduced `~1`，残差 6 |
| 3.11 | `sizeFactors(dds_p)` 范围 | 数值区间 | | 取诊断 CSV；设例 0.25→3.8 只说明方向，不作判据（§16.10） |
| 3.11 | 两侧显著基因数（各带检验名与 `reduced`） | 个 | | LRT + `padj`；早期时点无显著基因＝证据不足不是「没表达」（§16.5.3） |
| 3.12 | 候选表行数 / `score` 的三列构成 | 行 / 列名 | | 行数＝EffectorP 候选数；score 只用三列秩，`effectorp_prob` 与 `lrt_padj` 不进权重（§16.4.6） |

## 5. 失效条件对照（教材 §16.5，本实验里在哪一步、看什么能察觉）

1. **〔博〕合并参考的静默链：重名、未命中、歧义读段的两种归宿**（§16.5.1）｜3.1／3.2／3.3。`faidx` 只警告、
   STAR 不报错、GTF 未命中被静默丢弃——每一步都成功。**察觉**：两个清单为空 ＋ `.fai` 对账 ＋ `chrName.txt` 无重名 ＋ 两侧计数矩阵行数各自对得上。
   再有歧义读段：本章默认的唯一比对过滤**不偏袒任何一侧**，代价是两侧都损失深度且必须披露 `multimap_pct`；顺序归属把歧义全给先比的一方，且**不产生可审计的数**（教材 §16.4.2 三档）。
   量级标尺：`ch16_cross_mapping_leakage.py --selftest` 的 19.5553→0.2329%（naive 虚增）对比 0.1092…0.0976% 与 0.0990…0.0997%（竞争性两侧，均 ≈ `c`）。
2. **〔硕〕合并矩阵：TPM 方向恒定，size factor 方向不定**（§16.5.2）｜3.11。报告里出现「全基因组普遍下调／
   病原全面暴涨」时，**第一嫌疑在分母而不是生物学结论**——但也只是第一嫌疑：真实的全局响应同样会长成这样，本数据缺纯培养与绝对量参照，分不开两者。**察觉**：① 方法学里有没有「两个独立容器、各自估 size factor」；
   ② 诊断散点是过原点直线还是沿时间漂移（**警示信号，不是诊断结论**）；③ 病原侧有没有撞上「每个基因至少一个零」（脚本已用 `poscounts`）。
   量级标尺：`ch16_mixed_tpm_bias.py --selftest` 的合并/分开中位比 0.0050／0.0201／0.1005／0.3014 ≈ `p`，恒定病原基因表观 61.2×、恒定宿主 0.701、分开后 1.023；`1/f_P` 在 0.5% 时是 200×、30% 时 3.3×。
   **「size factor 看起来合理」不构成归一化正确的证据**——它的畸变方向取决于哪个物种占中位数基因。
3. **〔博〕病原占比低：功效贴地板；以及单端数据照抄双端命令**（§16.5.3）｜3.3／3.4／3.11。**察觉**：
   `P = D_used × f_P` 粗算后与功效表对照（`0.049 → 0.528 → 0.765`；这是**合成算例的解析近似**，设定为 2 倍变化、离散度 `α = 0.1`、每组 3 个重复；
   上限 0.766 只在同一设定下成立，**加测序量也到不了 0.8**——上限由离散度与重复数决定，不由深度决定）；样本表 `awk -F'\t' 'NF!=5 || $3==""'` 空输出；`[INFO] … 单端` 满 18 次。
   早期时点的「没有显著基因」只能读成「证据量不足，检验没有分辨力」，不能读成「这些基因没表达」。
4. **〔博〕效应子三步与结构域扫描：预测不是鉴定**（§16.5.4）｜3.5–3.10／3.12。**察觉**：列名核对
   （第 3 列 `OTHER`、第 4 列 `SP(Sec/SPI)`，再抽一行 OTHER 看高低）＋数量级（分泌组 5%–10%、候选数十至数百；
   突破三千＝输入形态错，个位数＝先查物种界）＋证据链（每条候选是否都有「信号肽＋成熟肽无跨膜＋分类器阳性＋表达或特异基因证据」四列原始值）。
   **证据链里的「成熟肽无跨膜」一环在没有 `tmhmm` 时是缺口而不是提示**：按 3.9 检查点 1 走 A（重建无跨膜 FASTA → 重跑 EffectorP → 回 3.11/3.12 重算）或走 B（逐处标「未过滤」），只在方法学写一句「用 DeepTMHMM 补做了」不算处置。
   最后一条最容易被忽略：**阴性预测不能当排除证据**，「没进候选表」≠「不是效应子」；NLR 侧同理，命中结构域不等于有抗病功能。
5. **〔博〕把时间当生物量：严格共线报错，近似共线沉默**（§16.5.5）｜3.11 的病原侧。**察觉**：拟合前看
   `model.matrix` 的秩与 `kappa()`（量级到 10⁴ 就要停；微扰 `1×10⁻⁴` 后满秩、条件数 2.43×10⁴ 是**设例**，入口见教材 §16.10 数字索引「共线两档」一行）；拟合后看系数表标准误，某系数 SE 异常大通常就是共线；
   报告里必须有一句「本数据的病原侧模型无法分离时间与生物量，结论限于时点间相对比较」。课程数据没有体外纯培养样本，连「以体外为参照做体内外比较」也走不了。
6. **不在五条失效内、但必须写进限制的两条**（§16.6）：缺抗病品种 N3 → 做不了抗/感等位比较（教材 §16.7 第 9 题③）；
   缺病原体外纯培养 → 做不了 in planta 与 in vitro 对比，因此**也做不出「in planta 诱导峰值」这一项证据**（这正是候选排序表只有三列证据的原因）。

## 6. 思考题（指向教材 §16.7 博士层，不给答案）

1. 讲义与旧材料里常有「先比宿主、剩下的再比病原」的写法。用你自己 3.4 的 `biomass.tsv` 说明这条路线
   会把偏倚藏在哪个数里、为什么 `multimap_pct` 反推不出来，并给出两种能把它变成一个可披露数字的做法。（§16.7 第 2 题的博士版 → §16.4.2、§16.5.1）
2. 设某早期样本病原计数占比 0.8%、宿主向病原的渗漏率 0.08%：分别算出占比升到 20% 时的虚增量，并说明
   这两个数如何否定「分别比对后不做扣除」；再指出这个计算在什么条件下不成立。（§16.7 第 4 题 → §16.4.3；三个数都是设例）
3. 若要求病原侧至少积累 `1.5×10⁷` 条有效计数，写出早期占比 0.5% 与 0.2% 两档所需的归属计数与名义深度
   （复合参考按 0.41 Gb、读长按 150 bp），并回答在这个量级上 §16.4.1 的三个折中你会选哪一个、牺牲什么。（§16.7 第 5 题 → §16.4.1.1）
4. 你在 3.11 拿到了诊断图。若 `sizeFactors(dds_p)` 从 0.25 持续升到 3.8（设例）而各时相原始文库总量基本一致：
   说明机制、给两套相互独立的补救预案并各写一条代价、并写出「什么形态算正常／什么形态算异常」的判据。（§16.7 第 7 题 → §16.4.4、§16.5.2）
5. 打开你自己的 `candidate_effectors.tsv`：把 `score` 换成「`signalp_prob` 与 `effectorp_prob` 各半」重排一遍，
   列出排名变化最大的前 5 个，并说明这两种权重各自隐含了什么假设、报告里该怎样交代权重的主观性。（§16.7 第 8 题的延伸 → §16.4.6、§16.5.4）
6. 教材说结构域扫描找到的是结构域不是功能。用你 3.10 的四个命中表说明：为什么「侵染后显著上调」这条硬过滤
   会系统性漏掉一类核心 NLR、替代的交集策略是什么、以及本数据为什么做不了抗/感等位比较。（§16.7 第 9 题 → §16.4.7、§16.6）
7. 选做（硕士层）：① 水稻—细菌互作该选 poly(A) 还是双 rRNA 去除，误选后病原矩阵什么形态、流程报不报错；
   ③ 为什么必须链特异性建库，不做的后果落在哪一类基因上。（§16.7 第 1 题 → §16.4.1.2）

## 7. 提交物

- **对应作业**：`08_assessment/phd/assignments/p03_host_pathogen_practice.md`（占课程总成绩 **3%**），
  打包 `学号_姓名_p03.zip`（≤ 200 MB；**去掉 BAM 与 STAR 索引**）。解压后：

  ```
  学号_姓名_p03/
  ├── report.pdf                      # 正文 ≤ 8 页；五节：双参考与本底 / 生物量曲线判读 /
  │                                   # 归一化诊断 / 时序 LRT 与模式聚类 / 效应子候选排序
  ├── scripts/
  │   ├── dual_quant.sh               # 你实际投递的 SGE 脚本（改自 03_dual_rnaseq_quant.sh）
  │   └── dual_deseq2_lrt.R           # 你实际用的那份（改过就标注改了哪几行）
  ├── results/
  │   ├── biomass.tsv                 # 3.4 原样（含未接种对照行）
  │   ├── crossmap_background.txt     # 对照行本底实测值 + 一句话结论
  │   ├── host_lrt.tsv                # 3.11 宿主侧：host_timecourse_LRT.csv 转换而来（改名不算，见 3.11）
  │   ├── path_lrt.tsv                # 3.11 病原侧：同上，转换后核对列数与行数
  │   ├── candidate_effectors.tsv     # 3.12 原样
  │   └── ai_audit.tsv                # ⑧ 的四条逐条判定表
  ├── figs/                           # 标题/轴/图例一律英文（集群 R 下中文会变方块）
  │   ├── fig1_biomass_curve.png      ├── fig2_sizefactor_diag.png
  │   ├── fig3_lrt_clusters.png       └── fig4_effector_funnel.png
  │   └── **只有 fig2 由脚本产出**（3.11 的 L85–93 写 diagnostic.png）；
  │       fig1 用 3.4 的 biomass.tsv、fig3 用 3.11 的两张 LRT 表 + padj、
  │       fig4 用 3.5–3.12 的四级数量，这三张要自己画并注明数据来源
  ├── ai_logs/prompt_and_reply.md     # ⑧ 的原文往返（提示词原样，不许预先提示）
  └── env_snapshot.yml                # conda env export --no-builds
  ```

- **五节报告各自要对上一个文件**：第 1 节 ↔ `biomass.tsv` 的对照行；第 2 节 ↔ `fig1`；第 3 节 ↔ `fig2`
  与 `pathogen_sizefactor_diagnostic.csv`；第 4 节 ↔ `host_lrt.tsv`／`path_lrt.tsv`；第 5 节 ↔ `candidate_effectors.tsv` 与 `fig4` 的四级漏斗（蛋白总数 → 分泌组 → 无跨膜 → EffectorP 候选，各级数量都写在图上）。
- **四个薄弱处要单独交代**（作业 §④ 的失分点同源）：`samples.tsv` 的 R2 列口径与 `treatment` 取值；
  `STRAND_COL` 的依据；未接种对照本底的实测值（没有对照的同学按 §6 第 1 题的写法说明能问与不能问的问题）；效应子候选的三列证据与权重理由。
- **评分口径**（作业 §④，满分 100）：完成度与结果正确性 50、判断与讨论质量 28、AI 使用与验证记录 10、
  报告质量 12。**「AI 使用与验证记录」只考可复核性**：提示词原文、模型与日期、AI 给了什么（原样）、哪里错了、你怎么发现的；通篇「AI 输出全部正确」且无验证过程的，本栏不得分；未用 AI 的写明原因即可，不扣分。
- **截止与迟交**：p03 课后**第 10 天 23:59**；迟交 3 天内按 90%、超 3 天按 70%、超 7 天不计分（可在截止前申请
  一次不扣分延期）；允许截止前重复提交，以最后一次为准。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材（概念、失效条件、习题、数字索引） | `textbook/chapters/ch16/manuscript.qmd`：§16.4.1（占比与深度、建库、对照）、§16.4.2（三种拆分路线与内存口径）、§16.4.3（交叉比对的量级）、§16.4.4（分开归一化）、§16.4.5（两套模型与共线两档）、§16.4.6（效应子三步）、§16.4.7（结构域≠功能）、§16.4.8（技术前沿边界）、§16.5.1–§16.5.5、§16.6、§16.7（博士层 4–11 题）、§16.9、§16.10 |
| 比较基因组接口 | `textbook/chapters/ch11/manuscript.qmd` §11.4.8（直系同源输出、特异基因的相对性、移交边界） |
| 本专题讲义 | `02_lectures/phd/topic03_host_pathogen/03_host_pathogen_lecture.md`：② 前置表、④ 4.1–4.10、⑤ 5.1–5.6、⑥ 6.1、⑧ AI 任务四步、⑨ E1–E8、⑩ 练习题、⑪ 文献 20 条 |
| 双参考与比对（只读；改参数走个人副本） | `03_code/phd/scripts/03_dual_rnaseq_quant.sh`：作业头 L3–7、守卫 L25–30、参数 L33–46、目录 L49–51、步骤一 L54–75、步骤二 L78–86、步骤三 L89–111、步骤四 L114–129、收尾提示 L131–134 |
| 效应子与 NLR（只读） | `03_code/phd/scripts/03_effector_screen.sh`：头注 L17–31、参数 L37–45、守卫 L50–55、清洗 L59–65、OrthoFinder L68–72、特异基因 L74–98、SignalP L101–114、成熟肽 L116–136、跨膜 L139–148、EffectorP L149–150、NLR L154–166、交接 L168–175 |
| 归一化与排序（只读） | `03_code/phd/scripts/03_dual_deseq2_lrt.R`：用法 L9–10、参数 L23–30、读入 L34–44、样本表 L46–55、宿主 L59–64、病原 L68–76、诊断 L80–93、候选表 L97–138、收尾 L140–145 |
| 合成自查演示 | `textbook/demos/ch16_cross_mapping_leakage.py`、`ch16_mixed_tpm_bias.py`、`ch16_pathogen_power.py`（均带 `--selftest`，在课程仓库根目录或 `textbook/` 下运行） |
| 数据说明与下载 | `06_data/phd/README.md` p03 节（48／18、104 GB、200 万条约 2 GB、单端、头部截取、`H2O` 定性判据）；`06_data/phd/download_phd.sh --topic p03`；`06_data/phd/manifests/p03_runs.tsv`（19 行＝表头+18） |
| 环境定义 | `07_envs/conda/env_phd_interaction.yml`（`ngs_phd_interaction`，pin 见 §0） |
| 作业规格 | `08_assessment/phd/assignments/p03_host_pathogen_practice.md`（① 背景 ② 交付物 ③ 步骤 ④ 评分 ⑤ 提交 ⑥ 常见失分点） |
| 前置自测 | `08_assessment/prerequisites/l0_01_linux_selftest.md`、`l0_02_r_selftest.md`、`l0_03_conda_selftest.md`、`l0_04_formats_selftest.md`、`l0_05_qc_selftest.md`、`l0_06_stats_selftest.md`；`02_lectures/prerequisites/l1_phd/`（`l1_phd.md`、`l1_phd_selftest.md`） |
