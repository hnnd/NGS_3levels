---
title: "实验指导 u07：基因组注释与 IGV 可视化核查"
level: undergraduate
topic: u07
textbook: [ch09]
lecture: ../02_lectures/undergraduate/unit07_annotation_igv/07_annotation_igv_lecture.md
env: ngs_ug_annot
---

# 实验指导 u07：基因组注释与 IGV 可视化核查

> 上机时手边打开的这份文件。每一步回答四件事：这条命令在做什么、敲什么、看到什么算对、
> 看到什么说明错了。原理与判据在教材第 9 章（§9.4 概念、§9.5 失效条件），本指导只放操作
> 与自查入口。所有标「预期区间（未实测）」的数字都是课程写下的自查范围，不是实测结果；
> 本课没有在集群真实跑完注释与 IGV 全流程，相关步骤标「未实测」。

## 0. 本实验对应什么

- **教材**：第 9 章 基因组注释与可视化核查；本实验覆盖本科学习目标 LO09-01（结构/功能注释
  与证据边界）、LO09-02（Prodigal 与 Prokka 分工、输出文件用途）、LO09-03（注释统计指标
  只能触发审查）、LO09-04（IGV 证据记录）。
- **学时**：u07 为 4 学时线上自学单元；本实验是其上机部分，直接对应 u08 综合项目的
  「模块 3 基因组注释」与《学生实验操作手册》§4.3。
- **主线数据**：Xoo 菌株 CIX4481——输入是 u06 评估后选定的组装 FASTA；同株作者完成图
  `GCA_987216485`（4,768,212 bp，数据登记值）只作对照自查。
- **环境**：`ngs_ug_annot`（注释，prokka/antismash/checkm-genome 未钉版本，`env_ug_annotation.yml`）；
  IGV 与 samtools 在 `ngs_ug_base`（samtools=1.17）；minimap2 在 `ngs_ug_assembly`
  （`env_ug_assembly.yml`）。环境名以 yml 的 `name:` 字段为准。
- **流程**：`genome.fasta` → Prokka 注释 → 统计质检 → antiSMASH 基因簇 → 准备 IGV 三轨输入 → IGV 人工核查 → 报告模板 §4。
- **计算纪律**：一切计算一律 `qsub` 投递计算节点——包括步骤 0 的 FASTA 自检、步骤 2 的
  统计脚本与步骤 4 的 IGV 输入准备（这两步本指导给最小作业写法；脚本头「可在登录节点
  跑」的注明不豁免课程纪律）；登录节点只做下载数据库、建软链接、编辑与投递。

## 1. 实验前检查

- **前置模块**（讲义 ②，先确认自测能过）：`l0_01_linux` Q03/Q07/Q09（qsub 与软链接）、`l0_03_conda` Q02/Q08（作业内激活环境）、`l0_04_formats` Q04/Q05/Q10（FASTA/GFF3/BAM 坐标与命名）。本讲不依赖 `l0_06_stats`（讲义 ⑦）。
- **激活环境并核验工具链**：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_annot
  command -v prokka antismash
  prokka --version && antismash --version     # 版本号记进报告（环境未钉版本，以实装为准）
  conda activate ngs_ug_base
  command -v igv samtools                     # samtools 只装在 base；步骤 4 的排序与索引靠它
  conda activate ngs_ug_assembly
  command -v minimap2                         # 比对作业所在环境；该环境未装 samtools
  ```

  这条命令在做什么：SGE 作业不继承终端里的 conda 变量，每个作业脚本开头自己激活环境
  （如 `07_run_prokka.sh` L35–36 的 source+activate）；`command -v` 确认工具在 PATH 里，缺一个就别往下跑。
  三个环境逐一核到——`ngs_ug_assembly` 只有 minimap2 且**没有** samtools（yml 已核），
  所以步骤 4 不做 `minimap2 | samtools` 跨环境管道，排序索引交给 prep 脚本在 `ngs_ug_base`
  里做。版本数字以实际输出为准（教材 9.4.4：环境未钉版本）。
- **预期**：路径与版本号全部打印。
- **出错信号**：`command not found` / `CommandNotFoundError` → 环境没建好或没激活（讲义 E7，
  作业里须先 `source /opt/miniconda3/bin/activate`）；prokka 在 `ngs_ug_base` 找不到是
  正常的——注释工具只在 `ngs_ug_annot`（讲义 ②）。

## 2. 实验数据

本实验的硬输入只有一个：u06 评估后**选定**的组装 FASTA（Canu 或 Flye 二选一，用你 u06
选型定下的那一个）。读段只在做 IGV 比对轨道时用。登录号全部已登记 `06_data/accessions.tsv`
（项目 `PRJEB100987`，西非 Xoo 群体，基因组约 4.7 Mb）：

| 数据 | 说明 | 位置 |
|---|---|---|
| u06 选定组装 | 本实验唯一输入，软链接固定命名为 `genome.fasta` | `/d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta` 或 `…/assem/flye/out_pacbio/assembly.fasta` |
| `GCA_987216485` | 同株作者发表完成图，4,768,212 bp（登记值），对照自查用 | 校外：`${REPO_DIR}/06_data/raw/undergraduate/genomes/CIX4481.fna`；校内路径由教师指认 |
| 校内读段 | `/data/lab/ngs/reads.fa`（PacBio），步骤 4 比对轨道用 | 实验室集群 |
| `ERR15732384` | 校外 ONT 长读长，302 Mb ≈63×（登记值），步骤 4 比对轨道用 | 校外：`bash 06_data/undergraduate/download_ug.sh --run` |

- **两条轨道步骤相同，只有读段与比对预设不同**（步骤 4 写明）；校外下载文件名以实落盘为准（README §三）。
- **工作目录**：`/d3/scratch/${USER}/ngs/anno/`（讲义 ⑤5.0）。原始数据只软链接不拷贝——**不要把数据放家目录**（家目录配额小，且属规范性扣分项）。
- **数据自查**（步骤 0 的两条命令）：contig 数与总长必须和 u06 评估报告一致，量级对照 4,768,212 bp（登记值）；对不上就别往下做。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出 / 检查点 / 出错信号。命令里的脚本名、参数名、输出文件名与
> `03_code/undergraduate/scripts/` 现版逐字一致（本指导修订时已逐个 grep 核对，见任务回执）。
> 真实 Prokka/antiSMASH/IGV 流程本课未实测，一切区间写「预期区间（未实测）」。
>
> **在哪敲命令**：SSH 登录后当前目录是家目录；下文 scratch 路径以 `/d3/scratch/${USER}/ngs`
> 为根；课程仓库路径用变量 `${REPO_DIR}` 表示（步骤 0 定义，校内值以教师公布为准，校外为
> git clone 路径）。**不要**原样输入 `<...>` 尖括号占位符——`<` 是 Bash 重定向符，会把命令截断。
> 四个课程脚本与手写最小作业都带 `#$ -cwd`：作业日志（`*.o<作业号>`）写在投递时所在目录，
> 产出写在脚本内部指定目录——找不到文件先分清找哪一类。课程脚本自己激活 conda 环境，
> 投递前不必手动 activate（手写最小作业里已写明激活语句）。

### 步骤 0：工作区与输入自检

- **目的**：承接 u06 的选定组装，建注释工作区，确认输入没拿错。
- **命令**（登录节点执行；两条计数也是计算，投最小作业）：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/anno && cd /d3/scratch/${USER}/ngs/anno
  REPO_DIR=<课程仓库路径>   # 课程仓库一行定义、全文复用（校内示例，以教师公布为准；校外为 git clone 路径）

  # 用你在 u06 评估后选定的那一个组装；"test" 是 canu -p 输出前缀，不是 Canu 测试数据；Flye 换成 …/flye/out_pacbio/assembly.fasta
  ln -sf /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta ./genome.fasta
  # ln -sf 对不存在的目标会静默成功（悬空链接），必须立刻验：
  test -s genome.fasta || echo "[ERROR] genome.fasta 链接目标不存在，请核查 u06 实际输出路径！"

  cat > u07_check.job <<EOF
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u07_check
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  cd /d3/scratch/${USER}/ngs/anno
  grep -c "^>" genome.fasta                                      # contig 数量
  awk '/^>/{next}{n+=length(\$0)}END{print "总长 (bp):", n}' genome.fasta
  EOF
  qsub u07_check.job
  ```

  这条命令在做什么：软链接把 u06 选定组装固定命名为 `genome.fasta`——四个 07 脚本的默认
  输入都是它。两条计数按纪律投最小作业；heredoc 不加引号，`${USER}` 在创建作业文件时就
  展开成真实路径。两个数留在作业日志 `u07_check.o<作业号>` 里，作与 u06 报告对账的凭据。
- **产出**：`genome.fasta`（软链接）＋ 作业日志 `u07_check.o<作业号>` 里的 contig 数、总长两个数。
- **检查点**：日志里的两个数与 u06 评估报告一致；量级对照同株完成图 4,768,212 bp（`GCA_987216485`，
  登记值）。u06 口径预期 contig 1–5 条、总长 4.6–4.9 Mb（README §四，「u06 预期」，未实测）。
- **出错信号**：`[ERROR] genome.fasta 链接目标不存在` → u06 实际输出路径与示例不符（作业名/
  前缀差异），修好链接再投；对不上 u06 报告 → 拿错文件（教材 9.4.5 把「查输入」列为排查
  第一步）；讲义 ⑤5.0 示例只写 Canu 路径，选 Flye 的换成 Flye 路径即可。

### 步骤 1：Prokka 注释（`qsub 07_run_prokka.sh`）

- **目的**：一次运行完成结构注释与功能注释，产出下游全部输入文件（GFF/FAA/GBK/TSV）。
- **命令**（登录节点投递）：

  ```bash
  cd /d3/scratch/${USER}/ngs/anno
  qsub ${REPO_DIR}/03_code/undergraduate/scripts/07_run_prokka.sh   # SGE 头 -pe smp 4，无 h_vmem 行
  qstat -u ${USER}        # qw 排队 / r 运行 / Eqw 报错
  ```

  这条命令在做什么：位置参数 `GENOME PREFIX OUTDIR` 默认 `genome.fasta mygenome prokka_out`
  （L20–25），无参调用与显式传默认值等价；换输出目录用第三个位置参数（见出错信号第 2 条）。
  内置 `--kingdom Bacteria --locustag MYGENOME`（L26–27），线程取 SGE 核数（L28）。contig 名
  长度预检：最长名超过 37 字符自动追加 `--compliant --centre XXX` 重编号（L49–59，37 是
  Prokka 1.14.6 源码上限，教材 9.4.4；环境未钉版本，以报错原文为准）。跑完写日期、版本与
  `--listdb` 库清单到 `software_versions.txt`（L66–68），`mygenome.txt` 摘要随作业日志打印（L75）。
- **产出**：`prokka_out/mygenome.{gff,faa,ffn,fna,gbk,tsv,txt,log,err}` ＋ `prokka_out/software_versions.txt`。
  统计摘要：`cat prokka_out/mygenome.txt`，或 `tail -30 prokka.o*`——SGE 作业静默运行，不往终端打印。
- **检查点**：
  1. 输出目录是本次新建——脚本预检拦已存在目录（L43–47）；`mygenome.txt`/日志末尾有完整统计摘要，不是旧目录残留；
  2. CDS 数落在课程预期 4,000–4,600（Xoo 约 4.7 Mb 口径，数据 README §四，**预期，
     未实测**），换算密度约 851–979 个/Mb（教材 9.6 算术，随预期而非实测）；
  3. `grep -c "^>" prokka_out/mygenome.faa` 与 CDS 数一致（讲义 ⑤5.2：蛋白序列条数必须等于 CDS 数）。
- **出错信号**：
  - `[ERROR] 输入基因组不存在或为空` exit 1（L38–42）→ 步骤 0 软链接没建好，回 u06 确认产物路径；
  - `[ERROR] 输出目录已存在` exit 1（L43–47）→ 按脚本接口换输出目录重投：
    `qsub ${REPO_DIR}/03_code/undergraduate/scripts/07_run_prokka.sh genome.fasta mygenome prokka_out2`
    （第三个位置参数），后续步骤里所有 `prokka_out` 换成新目录名；不要绕过脚本手动跑
    prokka 加 `--force`——脚本只认三个位置参数，不透传选项（讲义 E2 说的是手工跑 Prokka）；
  - 日志出现 `Contig ID must <= 37 chars long` → 说明绕过了脚本预检手动跑了命令；走脚本会
    自动重编号，**但此后下游所有文件都基于新 contig 名**（教材 9.5.2），只改 FASTA 头行
    必须同步重建 GFF、`.fai` 与 BAM 的 `@SQ`；步骤 4 届时改用 `prokka_out/mygenome.fna`（步骤 4 开头有判写法）；
  - CDS 数明显偏离预期 → 先查上游组装与参数，不先怀疑 Prokka（教材 9.4.5 竞争解释：碎片化、
    最短 contig 阈值、`--kingdom`、质粒缺失、真实小基因组）。方向也要读对：**重复区塌缩
    把多份拷贝压成一份、让计数偏低**——偏多时塌缩不是候选解释，另找冗余组装、污染或重复
    预测的证据（教材 9.6 末段）。

### 步骤 2：注释统计（qsub 最小作业）

- **目的**：把 Prokka 输出算成一张质检表——特征计数、CDS 密度、编码比例、平均 CDS 长、tRNA/rRNA 数、hypothetical 占比。
- **命令**（统计也是计算，按纪律投最小作业）：

  ```bash
  cd /d3/scratch/${USER}/ngs/anno
  cat > u07_stats.job <<EOF
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u07_stats
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  bash ${REPO_DIR}/03_code/undergraduate/scripts/07_annotation_stats.sh prokka_out mygenome
  EOF
  qsub u07_stats.job
  ```

  这条命令在做什么：qsub 只回显一行 "Your job … has been submitted"，质检表收在作业日志
  `u07_stats.o*` 里。脚本先查 `.gff/.fna/.tsv` 三件套非空（L20–28，防旧目录冒充）；特征计数
  取 GFF 第 3 列（L34）；编码密度＝Σ(End−Start+1)÷总长（L37–38，**逐条求和口径**）；hypothetical
  取 `.tsv` 中 CDS 且 product 含 `hypothetical protein` 的行数（L42–43），输出成 Markdown 表。
- **产出**：质检表打印在作业日志 `u07_stats.o*` 里（`cat u07_stats.o*` 查看）——也是报告 §4.1 的底稿。
- **检查点**：
  1. 表里的 CDS 数与步骤 1 日志中 `mygenome.txt` 的数一致；
  2. rRNA **特征条数 ≠ 完整操纵子套数**：6 条 rRNA 特征推不出「恰好两套完整 rrn」，须看
     5S/16S/23S 是否成套且相邻（教材 9.4.5）；
  3. 报告写明编码密度口径是**逐条求和**——重叠区会被重复计入（教材 9.4.5 设例：CDS
     101–300 与 251–450，求和 400 bp、并集 350 bp；1,000 bp 上 40.0% 对 35.0%，差 5 个百分点）；
  4. hypothetical 占比写全分子与分母（`H/n_CDS`）；
  5. 脚本输出的「正常参考范围」列是脚本注释里的课程经验值——按数字纪律**不作检查点判据，
     也不写进报告当合格线**（教材 9.4.5：课程没有为这类指标写下可作判据的通用区间；偏离
     只触发审查，不是诊断）。
- **出错信号**：
  - `[ERROR] 缺少或为空：prokka_out/mygenome.gff（Prokka 是否成功跑完？看 mygenome.log）`
    exit 1（L24）→ 步骤 1 没跑完，回去看作业日志，别用残留文件算数；
  - tRNA/rRNA 特征数近零 → 触发排查，先别下结论（教材 9.4.5）：组装侧竞争解释是保守
    操纵子处断裂或塌缩（回 u06 看 QUAST/BUSCO 证据；完成图不应出现）；输入/参数侧
    先读 `prokka_out/mygenome.log` 看 Barrnap/Aragorn 有没有告警、核对 contig 数与总长
    （总长正常、只有 rRNA 近零时注释侧更可疑）。两组证据都拿到再写进报告。

### 步骤 3：antiSMASH 基因簇预测（先登录节点备库，再 `qsub`）

- **目的**：预测次级代谢产物生物合成基因簇（BGC），读 region 坐标与 `on contig edge` 标签。
- **命令**（① 登录节点备库；② 投递作业）：

  ```bash
  # ① 首次使用先在登录节点下载数据库（计算节点不通外网；conda 包只含程序不含库）
  source /opt/miniconda3/bin/activate && conda activate ngs_ug_annot
  # 备库命令随版本不同：前一个失败或找不到就换后一个（脚本 L50–51 同款提示）；磁盘紧张加 --database-dir /d3/scratch/${USER}/db/antismash
  download-antismash-databases || antismash --prepare-data
  # ② 投递（自定义库目录时带同一路径，见下行注释）
  cd /d3/scratch/${USER}/ngs/anno
  qsub ${REPO_DIR}/03_code/undergraduate/scripts/07_run_antismash.sh
  # 自定义库目录时：qsub -v ANTISMASH_DB=/d3/scratch/${USER}/db/antismash ${REPO_DIR}/03_code/undergraduate/scripts/07_run_antismash.sh
  ```

  **运行预期**：antiSMASH 要比对大量 HMM 谱模型与已知簇库，运行明显长于 Prokka 属正常，
  长时间没有新文件不代表卡死；想看进度 `tail -f antismash.o<作业号>`。不要凭 `qstat`
  一直是 `r` 就 `qdel`，先问助教（耗时无实测入口，不给数值预期）。

  这条命令在做什么：脚本输入默认 `prokka_out/mygenome.gbk`（L19）——.gbk 带基因边界，**无需**
  `--genefinding-tool`（裸 FASTA 才自动加 prodigal，L56–61）。运行前用 `--check-prereqs`
  预检数据库（L48–54；预检/准备命令随版本不同，以 `--help` 为准，教材 9.4.8），再跑
  `antismash --output-dir antismash_out --taxon bacteria --cpus 4`（L65–66），最后把版本与
  数据库子目录写进 `software_versions.tsv`（L69–78）。【集群未实测】
- **产出**：`antismash_out/` 整目录（含 `index.html`）＋ `software_versions.tsv`。
- **检查点**：
  1. `index.html` 能打开、有 region 列表；
  2. `software_versions.tsv` 记录了 antiSMASH 版本与数据库路径——**报告方法节必须引用**
     （教材 9.5.5：程序版本与数据库版本分开记录，换库后同一基因可能改名、结果不可比）；
  3. 逐条 region 记录坐标并按**贴边规则**判定：起点＝1 或终点＝该 contig 长度即
     `on contig edge`，另一端隔几百 bp 不取消判定（教材 9.5.4；习题 6 设例：region
     `contig_3:1–28400`、contig 长 28,850 bp，右端余 450 bp 仍算贴边）；
  4. 报告措辞写「**具备合成某类化合物的遗传潜力**」，不写「能合成某化合物」；
     KnownClusterBlast 相似度按「参考簇基因数作分母的匹配比例」读——是基因层面匹配信息，
     不是产物同一性，即使 100% 也不保证同一化合物（教材 9.4.8）。本科只固定这条边界与 edge 判定。
- **出错信号**：
  - 预检失败 exit 1（L48–54，详情在 `antismash_prereqs.log`）→ ① 没做或没做对：回登录节点
    下载库，**不要**在计算节点联网重试（讲义 E3 的 `Missing data files` 指纹）；
  - 某簇标 `on contig edge` → 簇可能被组装断点截断、完整性未知，报告必须写明（教材 9.5.4）；
  - 只 `scp` 单个 `index.html` 回本地 → 白页（依赖同目录 js/css），**整目录**拉回（L80–81）。

### 步骤 4：IGV 输入准备（含 BAM 生成）

- **目的**：生成 IGV 三轨输入（`.fai`、排序索引 BAM、切尾 GFF）并做一致性预检，把
  「加载成功却一片空白」挡在投递之前。
- **BAM 从哪来（先想清楚再动手）**：IGV 的 BAM 是**用第 7 章的比对方法、把读段比对到本讲
  这份基因组 FASTA** 的产物——不是 u05 比对到参考基因组的 BAM（两套参考 contig 名/长度
  不同，prep 脚本的 `@SQ` 检查会拦）。校内轨读段 `/data/lab/ngs/reads.fa`（PacBio），校外
  轨是 ONT 的 `ERR15732384`（文件名以实落盘为准，README §三）。
- **参考序列二选一（先看步骤 1 日志再定）**：步骤 1 没有 `[WARN] contig 名超过 37 字符`（常见）
  → 用 `genome.fasta`；出现该 `[WARN]`（自动 `--compliant` 重编号）→ 下游全部改用
  `prokka_out/mygenome.fna`——`--compliant` 还附带最短 contig 过滤（mincontiglen=200，
  教材 9.4.4），名字与内容都可能变，不能拿旧 FASTA 改头行顶替：

  ```bash
  REF=genome.fasta                # 常见情形
  # REF=prokka_out/mygenome.fna   # 步骤 1 出现 [WARN] 自动重编号时改用这行（并注释掉上一行）
  ```
- **命令① 比对作业（只调用 minimap2，输出未排序 SAM）**：

  ```bash
  cat > /d3/scratch/${USER}/ngs/anno/u07_aln.job <<EOF
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u07_aln
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  set -euo pipefail
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_assembly
  cd /d3/scratch/${USER}/ngs/anno
  # 校内 PacBio 轨：-ax map-pb；校外 ONT 轨：改 -ax map-ont，读段路径换下载实落盘文件
  minimap2 -ax map-pb ${REF} /data/lab/ngs/reads.fa > reads.sam
  [[ -s reads.sam ]] && grep -q '^@SQ' reads.sam && echo "[INFO] 比对完成：reads.sam"
  EOF
  cd /d3/scratch/${USER}/ngs/anno && qsub u07_aln.job
  ```

  这条命令在做什么：`ngs_ug_assembly` 里只有 minimap2、**没有 samtools**（yml 已核），本作业
  不做跨环境管道，只输出未排序 SAM `reads.sam`；排序与索引交给命令②的 prep 脚本（它自己
  激活 `ngs_ug_base`）。预设与平台不对应（PacBio 用 `map-ont` 或反之）不报错但比对质量
  受损，按你的数据平台选。末行校验不过则作业非零退出，不会留下空文件往下走。【本流程
  未在集群现跑，标 unverified；教材 9.4.6 的 BAM 口径同此】
- **命令② prep 作业（排序、索引与一致性预检）**：

  ```bash
  cd /d3/scratch/${USER}/ngs/anno
  cat > u07_prep.job <<EOF
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u07_prep
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  cd /d3/scratch/${USER}/ngs/anno
  bash ${REPO_DIR}/03_code/undergraduate/scripts/07_prep_igv_inputs.sh ${REF} reads.sam prokka_out/mygenome.gff
  EOF
  qsub u07_prep.job
  ```

  这条命令在做什么：REPO_DIR（步骤 0）与 REF（本步开头）在创建作业文件时展开，作业自带
  真实路径；脚本自己激活 `ngs_ug_base`（L21、L24–26），作业里无需再写激活。`samtools faidx`
  建 `${REF}.fai`（L30）；`reads.sam` 头无 `SO:coordinate` → `samtools sort` 成
  `reads.sorted.bam` 再索引（L37–47）——本课统一走 `reads.sam → reads.sorted.bam`，后文
  scp 与 IGV 加载都用它；BAM 的 `@SQ` 与 FASTA 的 `.fai` 逐项比对，不一致 exit 1（L51–63，
  IGV 四条前置里最容易被跳过的第三条，教材 9.4.6）；`awk '/^##FASTA/{exit}{print}'` 切出
  IGV 版 GFF（L74），切尾版**只能给 IGV**，原始 GFF 留给 Roary（L76）；`comm -23` 查 GFF
  contig 名都在 FASTA 中（L79–87）；日志末尾列出拉回本机的清单（L91–96）。
- **产出**：`${REF}.fai`、`reads.sorted.bam`＋`reads.sorted.bam.bai`、`mygenome.igv.gff`；
  检查 INFO 与文件清单在作业日志 `u07_prep.o<作业号>` 里。
- **检查点**：日志出现三行 `[INFO]`——「BAM 未排序，执行 samtools sort」（SAM 输入必现；
  出现「跳过 sort」说明误传了 bam）、「BAM @SQ 与 FASTA 名称/长度一致」（L64）、
  「contig 名一致性检查通过」（L88）；`.bai` 与 BAM 同名同批，拉回成对。
- **出错信号**：
  - `[ERROR] BAM 的 @SQ 与 ${REF} 的序列名/长度不一致` exit 1（L55–62）→ 读段比对了另一份
    序列：确认作业①的 `REF` 与本步一致后重投比对（教材 9.4.6 排查表「有读段但位置明显不对」行）；
  - `[ERROR] GFF 中存在 FASTA 里没有的 contig 名` exit 1（L81–86）→ IGV 空白的头号原因：
    步骤 1 出现过 [WARN] 重编号而你仍用 `genome.fasta` 时必现——`REF` 换成
    `prokka_out/mygenome.fna`、作业①②重投（改名必须 GFF、`.fai`、BAM 的 `@SQ` 同步，
    教材 9.5.2）；无重编号则逐字核对 GFF 第 1 列与 FASTA 头行（大小写、后缀都算，教材
    9.4.6 排查表第一行）。

### 步骤 5：IGV 桌面核查（本地 `ngs_ug_base`）

- **目的**：把注释、覆盖度、读段证据叠在同一坐标上，记录可疑位点的证据。本章只看线索、
  不下真伪裁决——裁决是第 10 章的事。
- **命令/操作**：
  1. 把 prep 日志末尾列出的文件拉回本机同一目录。macOS / Linux 终端（支持花括号展开）：
     `scp ${USER}@10.7.254.22:/d3/scratch/${USER}/ngs/anno/{genome.fasta*,mygenome.igv.gff,reads.sorted.bam*} ./`
     （本地与集群账号不同就替换 `${USER}`；重编号时把 `genome.fasta*` 换成 `prokka_out/mygenome.fna*`。）
     **Windows PowerShell 不支持花括号展开**，会报找不到路径——先在集群登录节点打包再拉
     压缩包：集群上 `tar -czf igv_pack.tar.gz genome.fasta* mygenome.igv.gff reads.sorted.bam*`，
     本地 `scp ${USER}@10.7.254.22:/d3/scratch/${USER}/ngs/anno/igv_pack.tar.gz ./` 后
     `tar -xzf igv_pack.tar.gz`（PowerShell 里替换 `${USER}`；打包清单同样以 prep 日志为准）。
  2. 本地激活 `ngs_ug_base`，启动 `igv`；
  3. `Genomes → Load Genome from File…` 加载 `${REF}`（常见为 `genome.fasta`，重编号时
     为 `prokka_out/mygenome.fna`；**不是** File 菜单，讲义 ⑤5.6）；
  4. `File → Load from File…` 依次加载 `mygenome.igv.gff`、`reads.sorted.bam`；
  5. 定位框输入基因名或坐标；序列名**用你组装的真实名字**（IGV 顶部下拉列表里选，或查
     prep 所建 `.fai` 的第 1 列）——Flye 的 `contig_1:100000-120000`、Canu 的
     `tig00000001:100000-120000` 都只是设例，照抄不存在的名字会弹 `Unknown feature or
     locus`。逐步放大到能看见单条读段——窗口过宽不画比对是常见默认行为（设置项
     `SAM.MAX_VISIBLE_RANGE`，可调，教材 9.4.6）；
  6. 右键比对轨道 `Color alignments by → read strand` 按链着色；
  7. 截图：`File → Save PNG Image`，先 `Remove` 用不到的轨道；**正常区＋可疑区各存一张**，
     支撑报告的注释模块。
- **产出**：两张 PNG 截图 ＋ 每个可疑位点的证据记录（填入 §4 记录表）。
- **检查点**（教材 9.4.6 四项前置全过——`.fai` 在、BAM 排序索引、`@SQ` 一致、seqid 逐字
  一致——再谈读图；可疑位点按 9.4.7 逐项记录）：
  1. 记录七项：覆盖深度、alt 读段数与比例、alt 正反链条数（alt 正链占比）、alt 的 MAPQ
     分布、变异位点在读段内的位置、附近软剪切/indel、局部重复或旁系同源＋当前降采样与
     过滤设置；
  2. 结论只写「证据支持/质疑变异，理由……，下一步检查……」，**不写「已确认/已排除」**
     （教材 9.5.3）；alt 比例明显低于 1 不直接当假也不直接当真——单倍体克隆样本真变异
     预期接近 1，中间比例本身是需另查的信号（教材 9.4.7）；
  3. 计数练手用合成算例（课程仓库根目录运行，rc=0）：
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch09_igv_false_signals.py --selftest`
     四场景计数 real 0.40/0.00/0.07、strand 1.00/0.00/0.07、mapq0 0.40/1.00/0.07、
     endbias 0.40/0.00/1.00；脚本里的 0.2–0.8 与 >0.5 是**合成场景规则，不是判据**，不得抄进报告。
- **出错信号**：
  - 加载成功但空白 → 按教材 9.4.6 四步排查：seqid 逐字一致 → 放大窗口 → 换切尾版 GFF →
    查 `@SQ` 与索引；四步走完仍空白才怀疑数据本身；
  - 一堆白色空心读段堆出的「变异」 → MAPQ=0 只说明位置不唯一（重复区、旁系同源、组装塌缩
    都可能），不说明碱基必错：先降低信任、按原始 BAM 补证据（教材 9.4.7）；
  - 注释有基因但覆盖为 0 → 先逐项排除组装断点、真实缺失、比对过滤、参考错误，之后才考虑
    嵌合/假 ORF——零深度不是嵌合的专利（教材 9.4.6 排查表）。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 0 输入 | contig 数 / 总长 | 条 / bp | | 与 u06 评估报告一致；量级对照 4,768,212 bp（完成图登记值） |
| 1 Prokka | 版本与 `--listdb` 库摘要 | 文字 | | 抄 `software_versions.txt`；环境未钉版本，以实测为准 |
| 1 Prokka | CDS 数 / CDS 密度 | 个 / 个每 Mb | | 预期 4,000–4,600、约 851–979 个/Mb（README §四预期＋教材 9.6 算术，未实测）；偏离只触发审查 |
| 2 统计 | 编码比例（注明求和口径）/ 平均 CDS 长 | % / bp | | 分子分母写全（教材 9.4.5）；脚本参考列不作判据 |
| 2 统计 | tRNA / rRNA 特征数 | 条 | | rRNA 特征数 ≠ 操纵子套数（教材 9.4.5）；近零触发排查（步骤 2 出错信号） |
| 2 统计 | hypothetical 占比 | `H/n_CDS` % | | 写全分子分母；不按比例区间打分（教材 9.4.3） |
| 3 antiSMASH | 版本与数据库路径 / region 数与贴边情况 | 文字 / 个 | | 抄 `software_versions.tsv`；贴边按起点=1 或终点=contig 长判定（教材 9.5.4） |
| 5 IGV | 可疑位点七项证据 | 逐项记录 | | 结论只写支持/质疑＋理由＋下一步（教材 9.5.3） |

## 5. 失效条件对照（教材 §9.5：本实验里在哪一步、看什么能察觉）

1. **注释是预测不是实测**（§9.5.1）｜步骤 2 与 5：关键基因分开记三类证据——结构（边界/起始
   密码子/是否贴 contig 边缘）、同源与结构域（命名来自哪类库、覆盖度与相似度）、命名来源
   （GFF `inference` 属性＋库清单与参数）；hypothetical 看是否集中在重复区、短 contig 或
   异常 GC 区，不按「比例区间」打分。
2. **contig 名过长中断；GFF 尾部 `##FASTA` 误切使下游结果无效**（§9.5.2）｜步骤 1 出现
   `[WARN] contig 名超过 37 字符` 即知自动重编号生效，此后下游全部基于新名字，只改 FASTA
   头行必须同步重建 GFF/`.fai`/BAM；步骤 4 切尾版只给 IGV、原始 GFF 留给 Roary——下游核心
   基因计数变 0 这类静默失败，第一反应查输入文件形态，不是查生物学。
3. **IGV 三类假变异信号：链偏、末端聚集、MAPQ=0**（§9.5.3）｜步骤 5：三类各按计数记录；
   命中任一线索先**降低信任并补充证据**（按原始 BAM 重算两链条数、换文库或加深复测），
   不写「已确认/已排除」。
4. **antiSMASH 预测到簇 ≠ 该化合物被合成**（§9.5.4）｜步骤 3：贴边按坐标判定（起点=1
   或终点=contig 长度，另一端有余量不取消）；报告写「具备合成某类化合物的遗传潜力」，要谈
   产物须补表达、代谢物、活性或敲除证据。
5. （硕士层备选）**程序装好 ≠ 数据库就位**（§9.5.5）｜步骤 3 前置：数据库只在登录节点
   下载、计算节点只读；程序版本与数据库版本/路径分开记录，写进报告方法节。

## 6. 思考题（教材 §9.7 习题，不给答案）

1. 「四种碱基等概率、密码子独立、标准遗传密码」模型下，连续 300 个密码子无终止的概率是多少？
   这个数说明「长 ORF」是何种证据、不能说明什么？（习题 1 → 9.4.2；`demos/ch09_orf_length.py --selftest` 可复现）
2. 一条 GFF 记录 start=1042、end=2340（设例）：长度是多少？第 6 列 `.` 与第 8 列 `0`
   各表示什么？FASTA 头行是 `contig_1` 而 GFF 第 1 列写 `Contig_1`，IGV 里会发生什么？
   （习题 3 → 9.4.4）
3. 某 4.2 Mb 基因组注释出 3,980 个 CDS、86 个 tRNA、6 个 rRNA、编码比例 88.2%、hypothetical
   28.5%（设例）：算 CDS 密度与平均 CDS 长，并说明编码比例按逐条求和与按区间并集差在哪。（习题 4 → 9.4.5）
4. 你的统计表里哪个数字偏离预期时先回 u06 查组装？哪个数字偏离时塌缩不是候选解释、又该往哪里查？（习题 4 的竞争解释 → 9.4.5、9.6）
5. IGV 里某点 45× 覆盖、15 条 alt 全在正链、30 条反链全为参考型（设例）：算出 alt 比例与
   alt 正链占比，写出你的记录措辞——哪些能写、哪些不能写？（习题 5 → 9.4.7、9.5.3）
6. antiSMASH 报告某 region 坐标 `contig_3:1–28400`，contig 长 28,850 bp（设例）：算 region
   长度与右端剩余，按坐标规则判断是否贴边；报告能不能写「完整鉴定到该通路」？（习题 6 → 9.5.4）

## 7. 提交物

- **对应作业**：u08 综合项目的「模块 3 基因组注释」（评分维度见
  `08_assessment/undergraduate/project/undergrad_project.md` 的内容完整性与技术准确性）。
- **报告落点**：仓库报告模板 `undergrad_report_template.md` §4.1（基因预测统计——步骤 2
  质检表）与 §4.2（功能分析——antiSMASH 解读与两张 IGV 截图）；模板无 IGV 专栏，截图与
  讨论也可放 §8。《学生实验操作手册》§5.1 是另一套口径——两口径并存时**以手册为准**
  （u08 项目锚定手册）。
- **打包**：按课程统一命名 `学号_姓名_<作业号>.zip`；u07 阶段包含：`prokka_out/software_versions.txt`
  与 `antismash_out/software_versions.tsv`（在各自输出子目录里，不在 `anno/` 顶层，别漏）、
  本指导 §4 结果记录表、两张 IGV 截图、`prokka_out/mygenome.{txt,gff,faa,gbk}`、
  `antismash_out/` 目录整体打包。
- **诚实红线**：一切「预期区间（未实测）」不得写成实测；版本号以你机器上的实测输出为准；IGV 记录只写线索与下一步，不写真伪裁决。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/习题） | `textbook/chapters/ch09/manuscript.qmd` §9.4 / §9.5 / §9.7 |
| 本单元讲义（原理细节、⑨ 错误排查 E1–E8） | `02_lectures/undergraduate/unit07_annotation_igv/07_annotation_igv_lecture.md` |
| 四个脚本 | `03_code/undergraduate/scripts/07_run_prokka.sh`、`07_annotation_stats.sh`、`07_run_antismash.sh`、`07_prep_igv_inputs.sh`（BAM 比对作业按步骤 4 的最小作业写法投递） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch09_orf_length.py`、`ch09_igv_false_signals.py` |
| 数据说明、登录号与预期区间 | `06_data/undergraduate/README.md` §2.1（登记值）、§三（下载）、§四（预期区间）；`06_data/accessions.tsv` |
| 环境定义 | `07_envs/conda/env_ug_annotation.yml`（`ngs_ug_annot`）、`env_ug_base.yml`（`ngs_ug_base`）、`env_ug_assembly.yml`（`ngs_ug_assembly`） |
| 作业规格与报告模板 | `08_assessment/undergraduate/project/undergrad_project.md`、`undergrad_report_template.md` |
