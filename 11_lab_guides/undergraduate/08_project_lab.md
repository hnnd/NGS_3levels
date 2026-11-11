---
title: "实验指导 u08：综合实践项目——未知细菌基因组从组装到泛基因组"
level: undergraduate
topic: u08
textbook: [ch11, ch06, ch07, ch08, ch09]
lecture: ../02_lectures/undergraduate/unit08_project/08_project_lecture.md
env: ngs_ug_assembly / ngs_ug_annot / ngs_ug_phylo
---

# 实验指导 u08：综合实践项目

> 上机时手边打开的这份文件。流程与命令锚定《学生实验操作手册》
> （`<课程材料目录>/学生实验操作手册.md`，下称「手册」），
> 判据与原理在教材（主章第 11 章，参照第 6–9 章）。标「预期区间（未实测）」的数字
> 是课程写下的自查范围，不是实测结果；本课没有在集群真实跑完过全流程。

## 0. 本实验对应什么

- **教材**：主章第 11 章（ANI 定种、系统发育、泛基因组），参照第 8 章（组装与 BUSCO）、
  第 9 章（注释与 `##FASTA`）、第 6–7 章（质控、回贴）。本科学习目标 LO08-01–04、
  LO09-01–04、LO11-01–03；讲义 ① 七条目标与六模块一一对应。
- **学时与权重**：24 学时（3 天 × 8 小时，课堂集中），占全课程总成绩 90%，
  另 10% 为 L0 前置（讲义首页，契约同口径）。
- **三天节奏**（讲义 ⑤5.2）：Day 1 投 M1 并尽早并发投 Canu/Flye，傍晚前敲定
  `genome.fasta` 选型；Day 2 M3 注释、M4 定种并下好 5–10 株近缘参考；
  Day 3 M5 建树出图、M6 泛基因组、定稿报告。
- **环境**：M1/M2 `ngs_ug_assembly`，M3 与 M6 批量注释 `ngs_ug_annot`，M4/M5 与
  M6 Roary `ngs_ug_phylo`（讲义 ⑤5.3）；ggtree 出图**只在 `ngs_ug_phylo`，不在
  `ngs_ug_base`**（`02_plot_tree_and_pangenome.R` 脚本头 L10）。
- **计算纪律**：一切计算一律 `qsub`（或 `qrsh`）投递计算节点，登录节点只做下载、建环境、
  编辑（讲义 ⑨E1）；作业头含 `#$ -pe smp 4`、`#$ -l h_vmem=8G`（讲义 ②2.2）。`Killed` /
  `fork: retry` 是资源超限指纹，先查作业日志与 `qstat -j <作业号>`，别在登录节点跑计算。

## 1. 实验前检查

- **前置模块**（讲义 ②2.1）：`l0_01_linux`–`l0_06` 自测全过，`l0_06_stats` ≥80%
  （统计口径全靠它）。
- **四个环境逐个核验**（SGE 作业不继承交互环境，每个作业脚本头部都要
  `source /opt/miniconda3/bin/activate && conda activate <环境名>`，讲义 ⑨E2）：

  ```bash
  conda activate ngs_ug_assembly && command -v jellyfish canu flye quast.py busco
  conda activate ngs_ug_annot   && command -v prokka antismash
  conda activate ngs_ug_phylo   && command -v mash fastANI mashtree GToTree iqtree roary
  conda activate ngs_ug_phylo   && Rscript -e 'pkgs <- c("ggtree","ape","readr","dplyr","ggplot2","tidyr"); ok <- sapply(pkgs, function(p) requireNamespace(p, quietly=TRUE)); print(ok); if (!all(ok)) quit(status=1)'
  ```

  前三条各打印一行工具路径；第四条打印六个 `TRUE` 才算 R 出图链路就绪（出图脚本
  头部加载 readr/dplyr/ggplot2，分类函数用 tidyr，树图用 ggtree/ape），`FALSE` 时
  命令非零退出、停下报教师。**已知课程侧缺口**：`env_ug_phylo.yml` 未声明 `r-readr`
  （tidyr 同此）而出图脚本头部无条件 `library(readr)`（课程侧待补 yml）。GenomeScope
  **不在任何 conda 环境**（契约豁免工具），`wget` 下载 `genomescope.R` 后 `Rscript` 运行。
- **工作目录**（手册 §3.4 原句）：
  `mkdir -p /d3/scratch/${USER}/ngs/{survey,assem,anno,ident,phylo,pangenome,fq}`。
  原始数据只软链接不拷贝，**不要放家目录**（配额小且属规范性扣分项，项目说明 §1）。
- **数据核验**：校内确认 `/data/lab/ngs/reads.fa` 与 `/data/lab/ngs/db/` 存在；校外先跑 §2 下载与自查，数字对不上别往下做。
- **出错信号**：`canu: command not found` 一类 → 作业内环境未激活（讲义 ⑨E2）；
  `conda activate` 报环境不存在 → 回 u01 流程找教师。

## 2. 实验数据

两条轨道，**步骤相同、输入不同，不要混平台**：k-mer 扫描只用低错误率短读长，
组装只用长读长（教材 8.5.3）。登录号全部已登记 `06_data/accessions.tsv`
（项目 `PRJEB100987`，西非 Xoo 群体）：

| 轨道 | 勘测输入（短读长） | 组装输入（长读长） | 泛基因组面板 |
|---|---|---|---|
| 校内（手册锚定） | `/data/lab/ngs/reads.fa`（PacBio，见步骤 1 特殊处置） | 同左（`genomeSize=4m` 外部先验） | M4 定种后按 Mash 结果自选 5–10 株近缘参考 |
| 校外（公开数据自学） | `ERR15732342` Illumina 双端 229 Mb（≈48×，README §2.1 登记值） | `ERR15732384` ONT 302 Mb（≈63×，课程降采样至 40×） | 12 株完成图 + 2 株外群（下表） |

- **校外下载**（README §三原句）：`bash 06_data/undergraduate/download_ug.sh --run
  --subsample --depth 40`；只做 u08 只需完成图与外群 ≈67 MB（README §2.4）。
- **校外自查**（README §四，登记值）：ONT ≈38,078 条 / 302 Mb；Illumina 双端行数
  相等（`PAIRED_OK`）；完成图长度量级 4.6–5.1 Mb；md5 由下载脚本校验。
- **校外面板**（README §2.2–2.3，全部已登记）：12 株 Xoo 完成图，其中 CIX4481
  （`GCA_987216485`，4,768,212 bp，登记值）**就是 u06 你自己组装那株的作者发表完成图**——
  放进面板等于留自检位：它明显离群时先查自己的组装与注释，不要先编生物学故事
  （教材 11.6）。外群：`GCA_030177815`（Xoc HB8，同种不同致病变种）、
  `GCA_024298585`（Xcc CN02，不同种）。
- **面板选择要写进报告**：纳入哪几株、是否纳入外群、为什么。把 Xcc（ANI 87.10%，
  异种）放进面板预期核心骤降、泛基因组虚增——这是「混入非同种基因组」的现成对照（教材 11.6）。

## 3. 实验步骤

> 命令对手册逐节锚定，参数名与输出文件名和手册现版一致（修订时已逐条比对，见任务回执）；
> 集群真实运行未实测，一切区间写「预期，未实测」。手册里的 `conda activate ngs` 按 §0
> 映射表换环境；手册写在作业内的下载（Mash 库、NCBI 参考基因组）挪到**登录节点**——计算
> 节点不通外网。路径以 `/d3/scratch/${USER}/ngs` 为根；手册 §4.6 的 `/D3/SCRATCH` 一律
> 小写（Linux 区分大小写，讲义 ⑨E6）。

### 步骤 0：投递前准备（手册 §3.4、§4.1.3 步骤 1）

- **目的**：目录、数据、环境在作业排队前就位。
- **命令**（登录节点）：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/{survey,assem,anno,ident,phylo,pangenome,fq}
  cd /d3/scratch/${USER}/ngs/fq
  # 校内：ln -sf /data/lab/ngs/reads.fa ./     （勘测直接解引用真实文件，讲义 ⑨E5）
  # 校外：ln -sf <课程仓库路径>/06_data/raw/undergraduate/reads/ERR15732342_*.fastq.gz ./
  ls -lh /d3/scratch/${USER}/ngs/fq      # 链接指向真实文件（ls -lL 不报红）
  ```

- **产出**：七个目录就绪；`fq/` 下有输入文件。
- **检查点**：`ls -lh` 看到输入；规模对上 §2 自查数字（校外 ONT 302 Mb / Illumina 229 Mb，登记值）。
- **出错信号**：链接报红 → 先修数据路径，别投作业；校外数字对不上 → 停，重跑下载脚本的校验。

### 步骤 1：M1 k-mer 勘测（手册 §4.1.3 步骤 2–4；预算 20–40 min，讲义 ⑤5.1）

- **目的**：低错误率短读长数三档 k（21/17/25）k-mer 频数，产出 GenomeScope 输入
  直方图；勘测只回答「基因组多大、重复多少、有没有混序列」，不是判决（教材 8.4.3）。
- **命令**（`ngs_ug_assembly`，作业脚本照手册 §4.1.3 步骤 2 头部写）：

  ```bash
  cd /d3/scratch/${USER}/ngs/survey
  # 校外轨道（fq/ 里是 Illumina *.fastq.gz，手册原命令直接可用）：
  jellyfish count -C -m 21 -s 1000000000 -t 4 -o reads.jf <(zcat ../fq/*.fastq.gz)
  jellyfish histo -t 4 reads.jf > reads.histo
  jellyfish count -C -m 17 -s 1000000000 -t 4 -o reads.k17.jf <(zcat ../fq/*.fastq.gz)
  jellyfish histo -t 4 reads.k17.jf > reads.k17.histo
  jellyfish count -C -m 25 -s 1000000000 -t 4 -o reads.k25.jf <(zcat ../fq/*.fastq.gz)
  jellyfish histo -t 4 reads.k25.jf > reads.k25.histo
  # 校内轨道：fq/ 里是 PacBio reads.fa（FASTA 非压缩），把 <(zcat ...) 换成 ../fq/reads.fa
  # GenomeScope：登录节点先 cd 进 survey/ 下载脚本（完整 URL，省略号不是合法网址），
  # 下载位置与下面 Rscript 的相对路径同目录；拟合投 qsub/qrsh：
  #   wget https://raw.githubusercontent.com/schatzlab/genomescope/master/genomescope.R
  Rscript genomescope.R reads.histo 21 100 gs_k21 1000      # histo k 读长 输出目录 最大深度
  Rscript genomescope.R reads.k17.histo 17 100 gs_k17 1000  # 读长 100 与 u06 脚本 READ_LEN=100 同源
  Rscript genomescope.R reads.k25.histo 25 100 gs_k25 1000
  ```
- **产出**：`reads.histo`、`reads.k17.histo`、`reads.k25.histo`；`gs_k21/`、`gs_k17/`、`gs_k25/` 各含 `summary.txt` 与拟合图。
- **检查点**：
  1. 定性判据：完整直方图有**一个显著主峰**；主峰缺失时勘测数字**不可用**（教材
     8.5.3：判断标准是频谱有没有主峰，不是平台标签）。校内 PacBio 谱很可能没有
     清晰主峰——不是做错了，但**不能硬抄勘测数**：M2 改用外部先验 `genomeSize=4m`
     （手册参数），组装后以总长对账（步骤 3）。
  2. 校外对账基准：基因组大小 4.4–4.9 Mb、杂合度 ≈0%（README §四，**预期，未实测**）；
     杂合度显著非零先按教材 8.4.3 四条基本检查排查混菌/污染。`Model Fit` 只作
     诊断量（拟合曲线贴不贴主峰看图判读），**不存在合格线**（教材 8.4.4）。
  3. 三档 k 报告三档结果、说明哪一档频谱形状最清楚及理由；差多少算合格
     **没有通用阈值**（旧讲义「收敛 5%」口径已撤下）。
  4. 合成自查（课程仓库根目录运行）：`PYTHONDONTWRITEBYTECODE=1 python3
     textbook/demos/ch08_kmer_spectrum.py --selftest`——主峰 19×、错误尾 81.5%、G 偏差
     2.4%；加 `--error-rate 0.10` 复现主峰塌掉（rc=0）。
- **出错信号**：完整直方图单调滑落无主峰 → 误用高错误率长读长（→ 教材 §8.5.3；
  校内 PacBio 轨道按检查点 1 处置）；`zcat: … not in gzip format` → 输入形态与
  手册假定不符，按真实文件改（讲义 ⑨E5）；`std::bad_alloc` → 哈希表超内存，
  `-s` 降一级（讲义 ⑨E2）。

### 步骤 2：M2 双组装（手册 §4.2.3 步骤 2–3；Canu 1.5–4 h、Flye 25–60 min，讲义 ⑤5.1）

- **目的**：同一批长读长跑两套独立算法（Canu OLC 与 Flye repeat graph），让算法假设互相检验（教材 8.4.5）。
- **命令**（`ngs_ug_assembly`；手册 §4.2.3 步骤 2–3 是「建子目录→写作业脚本→
  qsub」，两个作业并发投递。最小作业外壳照下面写，后面各步骤说「同款外壳」就指它）：

  ```bash
  cd /d3/scratch/${USER}/ngs/assem
  mkdir -p canu flye
  # 作业一：Canu（手册原命令换环境；cd 进 canu/ 再跑，产物落在 canu/test-pacbio/）
  cat > run_canu.sh <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u08_canu
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  #$ -l h_vmem=8G
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_assembly
  cd /d3/scratch/${USER}/ngs/assem/canu
  canu -p test -d test-pacbio genomeSize=4m -pacbio /data/lab/ngs/reads.fa
  EOF
  qsub run_canu.sh
  # 作业二：Flye：外壳照抄 run_canu.sh，只改 #$ -N u08_flye 与命令行——
  #   cd /d3/scratch/${USER}/ngs/assem/flye
  #   flye --pacbio-raw /data/lab/ngs/reads.fa --out-dir out_pacbio --genome-size 4m --threads 4
  ```

  校外 ONT 轨道换平台参数（u06 实验指导步骤 3 同一改法）：Canu `-pacbio` → `-nanopore`、
  Flye `--pacbio-raw` → `--nano-raw`，输入换 `ERR15732384_ont_40x.fastq.gz`。`genomeSize=4m`
  量纲最易写错（写成 `4g` 按 40 亿 bp 规划资源，讲义 ⑨E3）；Canu 若在作业里再向 SGE 投
  子作业（日志出现 grid/qsub 字样后挂起），按 u06 实验指导步骤 3 在个人副本上加
  `useGrid=false maxThreads=4 maxMemory=28g` 再投。
- **产出**：`canu/test-pacbio/test.contigs.fasta`；`flye/out_pacbio/assembly.fasta`
  与元数据 `flye/out_pacbio/assembly_info.txt`（含 `circ.` 列）。作业日志
  `run_canu.o*`/`run_flye.o*` 落在 assem/（`#$ -cwd`＝投递时所在目录）。
- **检查点**：
  1. 粗检：`grep -c '^>' canu/test-pacbio/test.contigs.fasta` 数 Canu contig 条数；
     `cat flye/out_pacbio/assembly_info.txt` 看 Flye `circ.` 列。校外自查基准：
     contig **1–5 条**、总长 **4.6–4.9 Mb**（README §四，预期，未实测）。
  2. `circ.=Y` 是**有用的阳性信号，不是完成证明**——不证明染色体完整、无错接、
     质粒齐全（教材 8.4.6）。
  3. 深度手算对账：读段总碱基 ÷ `genomeSize` = 期望深度，与 Canu 日志对照
     （教材 8.5.3 算例：1.6×10⁸ bp 按 4 Mb → 40×）。
- **出错信号**：日志出 `(1.28 times coverage)` 式荒谬深度但作业正常结束 →
  `genomeSize` 量级写错（→ 教材 §8.5.3），改参数后**清空整个输出目录**再跑；
  `Killed` / `fork: retry` → 资源超限（讲义 ⑨E1）：查作业日志与 `qstat -j`
  确认原因，回 qsub 或加大 `h_vmem`；几天不结束 → 查 `genomeSize` 是否写成
  `4g`（讲义 ⑨E3）；`command not found` → 讲义 ⑨E2。

### 步骤 3：M2-QC 评估与选型（手册 §4.2.3 步骤 4–5；预算 25–55 min，讲义 ⑤5.1）

- **目的**：QUAST 比连续性、BUSCO 比完整性，按证据链选型锁定唯一 `genome.fasta`（教材 8.4.9：总长 → 结构 → 同库 BUSCO → 连续性）。
- **命令**（`ngs_ug_assembly`；手册 QUAST 命令无 `-r`，校内无参考属正常）。
  下面三条放进步骤 2 同款作业外壳（`#$ -N u08_qc`，cd 到 assem）再 qsub：

  ```bash
  cd /d3/scratch/${USER}/ngs/assem
  quast.py canu/test-pacbio/test.contigs.fasta flye/out_pacbio/assembly.fasta -o quast_results -t 4
  busco -i canu/test-pacbio/test.contigs.fasta -o busco_canu -m genome -l bacteria_odb10 -c 4 \
      --offline --download_path /d3/scratch/${USER}/ngs/busco_lib
  busco -i flye/out_pacbio/assembly.fasta    -o busco_flye -m genome -l bacteria_odb10 -c 4 \
      --offline --download_path /d3/scratch/${USER}/ngs/busco_lib
  ```

  **课程侧缺口，按顺序先补再投递**（手册命令本身不改，离线参数本指导已内嵌）：
  ① 计算节点无外网：登录节点先 `busco --download bacteria_odb10 --download_path
  /d3/scratch/${USER}/ngs/busco_lib`（同 u06 实验指导步骤 4；qsub 按提交时的
  脚本执行，投递后无法再补参数，所以要先下载再投）。
  ② lineage 两把尺：本步用 `bacteria_odb10`（n=124），README 的 C>97% 预期按
  `xanthomonadales_odb10` 写，两库**分数不可比**（教材 8.4.8）——只要求「同一库
  自比＋报告写明库名与 n」，不得把本步的 C 对照 README 的 97%。
- **产出**：`quast_results/report.txt`；`busco_canu/short_summary*.txt`、`busco_flye/short_summary*.txt`。
- **检查点**：
  1. BUSCO 加法自检 `C=S+D`、`C+F+M=100%`（教材 8.4.8）；n=124 时 1 个基因 =
     0.81 个百分点（在课程仓库根目录运行：`PYTHONDONTWRITEBYTECODE=1 python3
     textbook/demos/ch08_n50_vs_completeness.py --example 4`，rc=0）——**C 差不到
     1 个百分点不定优劣**，不存在「差 2% 一票否决」。
  2. 结构证据：本步 QUAST 无参考，错接一栏是空的——**无参考 ≠ 正确性通过**。校内
     用 minimap2 回贴深度查塌缩（约 2×）与断点（骤降＋跨越读段缺失），命令与判读见
     教材 §8.4.9 与第 7 章；不做就写「未检查错接」（教材 §8.5.2）。校外可手动补
     `-r`（u06 步骤 5 同款）：`quast.py <你的组装> -r <课程仓库路径>/06_data/raw/
     undergraduate/genomes/CIX4481.fna`，总长差异 <1%（README §四，预期，未实测）。
  3. 选型结论按证据链写：总长明显偏短查塌缩/丢段、偏长查冗余/污染，再看结构
     证据，再同库 BUSCO，最后才看 contig 数、N50 与 `circ.`。
- **出错信号**：`Errno -3` / name resolution → 计算节点无外网，不是 BUSCO 缺陷
  （→ 教材 §8.5.4；回登录节点预下载＋补离线参数）；接近全 Missing → lineage 选错；
  只填了 N50 和 C 两行就下结论 → 回 §4 把三维证据补全（教材 §8.5.2）。

### 步骤 4：M3 注释（手册 §4.3.3；Prokka 8–20 min、antiSMASH 30–90 min，讲义 ⑤5.1）

- **目的**：Prokka 结构注释（`.gff`/`.faa`），antiSMASH 找次级代谢产物基因簇；`.gff` 是 M6 的**唯一合法输入**（教材 9.5.2）。
- **命令**（`ngs_ug_annot`；手册 §4.3.3 步骤 2 的软链接默认指向 Canu 产物——**必须
  改成步骤 3 选定的组装**：嘴上 Flye、链接 Canu 是技术准确性事故，讲义 ④4.3 约束 3）：

  ```bash
  cd /d3/scratch/${USER}/ngs/anno
  # 软链接必须指向步骤 3 选定的组装。<> 占位符在 bash 里是重定向符，直接复制会报
  # syntax error；二选一填真路径（另一行删掉）：
  #   选 Canu：ln -sf /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta ./genome.fasta
  #   选 Flye：ln -sf /d3/scratch/${USER}/ngs/assem/flye/out_pacbio/assembly.fasta ./genome.fasta
  prokka --outdir prokka_out --prefix mygenome --kingdom Bacteria --cpus 4 genome.fasta
  antismash --output-dir antismash_out --genefinding-tool prodigal --taxon bacteria --cpus 4 genome.fasta
  ```

  两条命令放进步骤 2 同款作业外壳（`#$ -N u08_anno`，cd 到 anno）再 qsub。
  antiSMASH 数据库须**登录节点预先下载**（conda 版只含程序不含库，教材 9.5.5；
  与 u07 实验指导步骤 4 同一写法）：

  ```bash
  source /opt/miniconda3/bin/activate && conda activate ngs_ug_annot
  download-antismash-databases || antismash --prepare-data   # 前一个失败/找不到就换后一个
  ```
  手册步骤 4 的 `emapper.py` 功能注释不在四个课程环境内，需自建环境——时间紧可
  跳过，但报告须写明哪一步未做、为什么，内容完整性按手册 §5.1 口径核。
- **产出**：`prokka_out/mygenome.gff`（保留末尾 `##FASTA`，M6 要验）、`mygenome.faa`、`mygenome.txt`；`antismash_out/index.html`。
- **检查点**：
  1. 校外对账基准：Prokka 预测 4,000–4,600 个/株（Xoo 4.7 Mb，README §四，
     预期，未实测），换算密度 851–979 个/Mb（教材 9.4.5 算术）。
  2. 课程**没有**为编码密度、假定蛋白比例、rRNA 数写下可作判据的通用区间（教材
     9.4.5）——偏离时按 9.4.5 竞争解释表逐层排查（输入 → 参数 → 污染 → 生物学）。
  3. `grep -c '^>' prokka_out/mygenome.faa` 记录蛋白数，与 M6 每株体检前后对照。
- **出错信号**：CDS 数异常少 → 先查组装碎片化把基因截断（教材 9.4.5）；
  contig 名过长触发 Prokka 规范报错 → 教材 §9.5.2；antiSMASH 报找不到数据库 →
  回登录节点预下载（教材 §9.5.5）；antiSMASH 报 0 个簇**不是分析失败**，如实报告。

### 步骤 5：M4 定种（手册 §4.4.3；Mash 约 30 min 含库下载、FastANI 5–15 min，讲义 ⑤5.1）

- **目的**：Mash 从数万参考里筛 Top 命中，FastANI 给全基因组相似度定种；**M4 的
  副产物（参考基因组清单）是 M5/M6 的原料**，参考选错下游全错（讲义 ④4.3 约束 1）。
- **命令**（`ngs_ug_phylo`）。6 GB 的 Mash 库在**登录节点**先下载——先 cd 进
  ident/ 再下，作业与库同目录，相对路径才找得到：

  ```bash
  cd /d3/scratch/${USER}/ngs/ident
  wget -c https://gembox.cbcb.umd.edu/mash/refseq.genomes.k21s1000.msh    # 登录节点（6 GB）
  ```

  定种作业（步骤 2 同款外壳，`#$ -N u08_mash`，cd 到 ident）：

  ```bash
  cd /d3/scratch/${USER}/ngs/ident
  # 软链接二选一（同步骤 4；Canu：assem/canu/test-pacbio/test.contigs.fasta，
  # Flye：assem/flye/out_pacbio/assembly.fasta），下行以 Canu 为例：
  ln -sf /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta ./genome.fasta
  mash screen -w -p 4 refseq.genomes.k21s1000.msh genome.fasta > mash_screen.tab
  sort -gr mash_screen.tab | head -n 10 > top10_species.tab
  ```

  按 Mash 结果下载 5–10 株近缘参考（**登录节点**；编号必须换成你自己的 Mash
  结果——照抄任何示例编号 = 拿别人的参考分析你的菌株，技术准确性直接扣分）。
  登录号取自 `top10_species.tab` 第 1 列，两条课程验证过的下载通道：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/ident/ref_genomes
  cd /d3/scratch/${USER}/ngs/ident/ref_genomes
  # 通道一：ENA 浏览器 API（与 06_data/undergraduate/download_ug.sh 同一入口，认 GCA_ 号）：
  curl -sL "https://www.ebi.ac.uk/ena/browser/api/fasta/GCA_030177815?download=false" -o Xoc_HB8.fna
  # 通道二：NCBI FTP（认 GCA_/GCF_ 号；路径按登录号三位一级展开，末级组装目录先列目录确认）：
  #   wget -qO- https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/030/177/815/ | grep GCA_030177815
  #   → GCA_030177815.1_ASM3017781v1/，下载其中 <登录号>_<组装名>_genomic.fna.gz 并 gunzip
  # 校外轨道：面板已由 download_ug.sh 下好，ln -sf <课程仓库路径>/06_data/raw/undergraduate/genomes/*.fna ./ 即可
  ```

  FastANI 作业（参考下完再投；步骤 2 同款外壳，`#$ -N u08_fastani`）：

  ```bash
  cd /d3/scratch/${USER}/ngs/ident
  ls ref_genomes/*.fna > ref_list.txt
  fastANI -q genome.fasta --rl ref_list.txt -o fastani_results.txt -t 4
  # FastANI 默认片段 3000 bp、k=16（FastANI 文档口径）
  ```
- **产出**：`mash_screen.tab`、`top10_species.tab`、`fastani_results.txt`、`ref_genomes/`。
- **检查点**：
  1. 校外三档自查基准（README §四，本仓库 MinHash k=21、sketch=5000 估计）：其余
     11 株 Xoo 99.83–99.95%、Xoc HB8 97.87%、Xcc CN02 87.10%；FastANI 实跑有小数位
     差异，**三档排序与间距稳定**才算对上。
  2. ANI 95% 是经验边界不是自然常数；95–96% 灰区三证据同看（比对片段占比、Mash
     排序、树的位置）；ANI 高但片段很少 = 只有局部同源（教材 11.4.5、11.6）。教学点：
     ANI **分得了种、分不了致病变种**——97.87% 仍 >95%，区分 Xoo/Xoc 须另找证据（教材 11.6）。
- **出错信号**：`ftp://` 下载挂死 → 全改 `https://` ＋ `-c`（讲义 ⑨E4）；
  top10 全是模式生物 → 怀疑 `genome.fasta` 链接错了输入。

### 步骤 6：M5 系统发育（手册 §4.5.3；预算 30–70 min，讲义 ⑤5.1）

- **目的**：Mashtree 快速树与 GToTree+IQ-TREE 单拷贝超矩阵树互相参照（手册 §4.5.4 要求比较两树差异）。
- **命令**（`ngs_ug_phylo`，三步可拆三个作业）：

  ```bash
  cd /d3/scratch/${USER}/ngs/phylo
  mkdir -p genomes && cd genomes
  # 软链接二选一（同步骤 4；Canu 例）：
  ln -sf /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta ./mygenome.fasta
  ln -s /d3/scratch/${USER}/ngs/ident/ref_genomes/*.fna ./
  # 校外轨道再加：ln -sf <课程仓库路径>/06_data/raw/undergraduate/genomes/*.fna ./
  cd ..
  mashtree --numcpus 4 genomes/*.fasta genomes/*.fna > mashtree.dnd
  ls /d3/scratch/${USER}/ngs/phylo/genomes/*.fasta /d3/scratch/${USER}/ngs/phylo/genomes/*.fna > genome_files.txt
  GToTree -f genome_files.txt -H Bacteria -j 4 -o gtotree_out
  cd gtotree_out && iqtree -s Aligned_SCGs.faa -m LG+F+I+G4 -bb 1000 -alrt 1000 -nt 4
  ```

  三条计算命令各自放进步骤 2 同款外壳（`#$ -N u08_mash / u08_gtotree / u08_iqtree`，
  都 cd 到 phylo；iqtree 作业 cd 到 gtotree_out）再 qsub。GToTree 的 Bacteria 集是
  74 个单拷贝保守基因 HMM（GToTree 文档口径）；出图用课程脚本（**只在
  `ngs_ug_phylo`**，见 §1 的 R 核验），两棵树都要画（手册 §4.5.4 要求比较两树差异）：

  ```bash
  Rscript <课程仓库路径>/03_code/undergraduate/scripts/02_plot_tree_and_pangenome.R \
      /d3/scratch/${USER}/ngs/phylo/figures \
      tree:/d3/scratch/${USER}/ngs/phylo/gtotree_out/Aligned_SCGs.faa.treefile
  # 脚本固定写 core_gene_tree.pdf，输出目录分开才不会互相覆盖：
  Rscript <课程仓库路径>/03_code/undergraduate/scripts/02_plot_tree_and_pangenome.R \
      /d3/scratch/${USER}/ngs/phylo/figures_mash \
      tree:/d3/scratch/${USER}/ngs/phylo/mashtree.dnd
  ```
- **产出**：`mashtree.dnd`、`gtotree_out/Aligned_SCGs.faa.treefile`、
  `figures/core_gene_tree.pdf`（GToTree 树图）、`figures_mash/core_gene_tree.pdf`（Mashtree 树图）。
- **检查点**：
  1. 节点标号是 UFBoot 与 SH-aLRT 两项支持值（`-bb`/`-alrt` 是重抽样次数 1000，不是
     阈值）。支持值衡量**重抽样下的稳定性，不是「该分支为真的概率」**；UFBoot 与标准
     bootstrap 不在同一尺度（脚本尾提示与教材口径一致，讲义 ⑥6.4/⑩Q4）。常用强支持线
     UFBoot ≥95 / SH-aLRT ≥80 是 IQ-TREE 文档约定，引用时挂 IQ-TREE 文档入口，不裸写进判据。
  2. 拓扑只作参考；树枝长是每位点替换数，**不是时间**（教材 11.4.6 口径）。
- **出错信号**：出图报缺 ggtree/ape 或 readr → 你在错的环境，换 `ngs_ug_phylo`
  （缺 readr 报教师，见 §1）；目标株落在树最外侧且支持值低 → 回 M4 补近缘参考
  再建；两树差异大 → 如实讨论，不硬凑一致。

### 步骤 7：M6 泛基因组（手册 §4.6.3；批量注释 40–80 min、Roary 20–50 min，讲义 ⑤5.1）

- **目的**：全部面板基因组**统一 Prokka 重注释**后喂 Roary 得核心/附属存在矩阵；纪律：一个脚本一个环境，**拆成两个串联作业**（讲义 ④4.3 约束 2）。
- **命令**（作业一，`ngs_ug_annot`，手册 §4.6.3 步骤 3；作业二，`ngs_ug_phylo`，
  手册 §4.6.3 步骤 4–5）。先备面板（**登录节点**，建链接不是计算）：

  ```bash
  cd /d3/scratch/${USER}/ngs/pangenome
  mkdir -p genomes
  # 自己的组装（二选一，同步骤 4；Canu 例）：
  ln -sf /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta ./genomes/mygenome.fasta
  # 参考面板：校内 ln -sf /d3/scratch/${USER}/ngs/ident/ref_genomes/*.fna ./genomes/
  #          校外 ln -sf <课程仓库路径>/06_data/raw/undergraduate/genomes/*.fna ./genomes/
  #          校外按需加外群：ln -sf <课程仓库路径>/06_data/raw/undergraduate/outgroup/*.fna ./genomes/
  ls genomes/    # 株数与 §2 面板对账（校外含自己组装与外群应 ≥ 13）
  ```

  作业一（步骤 2 同款外壳，`#$ -N u08_prokka`，cd 到 pangenome）：

  ```bash
  cd /d3/scratch/${USER}/ngs/pangenome
  for genome in genomes/*; do
      base=$(basename $genome | sed 's/\.[^.]*$//')
      prokka --outdir annotations/$base --prefix $base --kingdom Bacteria --cpus 4 $genome
  done
  ```

  作业二（步骤 2 同款外壳，`#$ -N u08_roary`，cd 到 pangenome）：

  ```bash
  cd /d3/scratch/${USER}/ngs/pangenome
  mkdir -p gff_files
  for dir in annotations/*; do cp $dir/*.gff gff_files/; done
  roary -f roary_out -e -n -v -p 4 gff_files/*.gff
  Rscript <课程仓库路径>/03_code/undergraduate/scripts/02_plot_tree_and_pangenome.R \
      /d3/scratch/${USER}/ngs/pangenome/figures \
      roary:/d3/scratch/${USER}/ngs/pangenome/roary_out/gene_presence_absence.csv
  ```

  先用内置设例验证出图链路（数字为代码内置设例，本课未现跑，unverified；先确认 §1
  的 R 核验六个 TRUE）：`Rscript <课程仓库路径>/03_code/undergraduate/scripts/02_plot_tree_and_pangenome.R /d3/scratch/${USER}/ngs/pangenome/figures --demo`
- **产出**：`annotations/*/`（每株一套注释）、`roary_out/gene_presence_absence.csv`、
  `roary_out/core_gene_alignment.aln`、`figures/pangenome_composition.pdf`。
- **检查点**：
  1. **跑 Roary 之前**先看每株蛋白数（`grep -c '^>' annotations/*/*.faa`）：某一列
     接近 0 或高一个量级 = 警报（合成算例：统一注释各株 2,088–2,132、特异家族
     1,629–1,657，混入一株宽松规则跳到 8,150、99.9% 假特异——课程仓库根目录运行
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch11_annotation_bias.py --selftest`，rc=0）。
  2. 每份 `.gff` 抽查行数与末尾 `##FASTA`：必须是 Prokka 原生含 `##FASTA` 的原件
     （教材 9.5.2；喂裁剪版 `.igv.gff` 或裸 `.fna`，Roary 可能报错，也可能**正常跑完
     但矩阵无效**——讲义 ⑨E8）。
  3. 核心/附属计数按 Roary 口径（存在比例 ≥99%）报告，并**同时报 `n`、`m`、允许
     缺失 `k` 株**：n=12 时三档等价（都要求 12/12），缺 1 株 = 11/12 = 91.67%
     （课程仓库根目录运行 `PYTHONDONTWRITEBYTECODE=1 python3
     textbook/demos/ch11_core_threshold.py --selftest`，rc=0）。
  4. 核心占比**只作观测描述**，写明样本量与选株方式；占比偏低只做两步：查混入
     非同种（回 M4 的 ANI）、查某一株注释失败（教材 11.4.4，不设百分比红线）。
- **出错信号**：`Error: cannot find any GFF files` → 查 gff_files/ 与软链接（讲义 ⑨E8）；
  核心基因数异常少甚至为 0 → 先查空/裁剪的 `.gff`，再查混入异种（→ 教材 §11.5.1）；
  `roary:` 出图报缺列 → 确认喂的是 Roary 原生 `gene_presence_absence.csv`（脚本只认
  `No. isolates` 列）。

### 步骤 8：报告与提交

- **目的**：把手册 §5.1 六模块＋总结写进报告模板 §2–§8；图表编号、图题在下表题在上；参考文献 GB/T 7714-2015（手册 §5.2）。
- **命令**：无新计算；把 §4 结果记录表逐项誊入报告对应章节。
- **产出**：`学号_姓名_NGS综合项目报告.pdf` ＋ 数据包 zip（见 §7）。
- **检查点**：① 每个数都能在 §4 找到出处，「预期区间（未实测）」不得写成实测；
  ② 选型论证按教材 8.4.9 顺序，无参考轨道写明「未检查错接」；③ 泛基因组报
  `n`、`m`、`k` 与选株方式，不写「95% 核心」；④ 脚本集可原样重跑，不写死他人绝对路径。
- **出错信号**：报告里出现教材已撤下的判据（D 百分比红线、「收敛 5%」、
  「circ.=Y 证明完成」一类）→ 回教材对应节改写法。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果。BUSCO 一栏必须写库名与 `n`；ANI 一栏注明工具与参数。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 M1 | 主峰 D_k（k=17/21/25）/ 三档大小估计 / 杂合度 | × / bp / % | | 主峰存在且显著，缺失即勘测不可用（教材 8.4.3/8.5.3）；校外预期 4.4–4.9 Mb、≈0%（README §四，未实测） |
| 2 M2 | Canu contig 数 / 总长 / N50 | 条 / bp / bp | | 校外预期 1–5 条、4.6–4.9 Mb（README §四，未实测） |
| 2 M2 | Flye contig 数 / 总长 / N50 / circ. | 条 / bp / bp / Y-N | | 同上；circ.=Y 是阳性信号不是完成证明（教材 8.4.6） |
| 3 QC | QUAST 指标（注明有无 `-r`） | 按报告 | | 无参考时错接栏为空，写「未检查错接」（教材 8.5.2） |
| 3 QC | BUSCO（同库）C/S/D/F/M，n= | %，注明库名 | | 加法自检 C=S+D（教材 8.4.8）；1 基因 = 0.81 pp（n=124，demo --example 4） |
| 3 选型 | 最终选择 + 证据链顺序 | 文字 | | 总长对账 → 结构 → 同库 BUSCO → 连续性（教材 8.4.9） |
| 4 M3 | Prokka CDS/蛋白/rRNA 数；antiSMASH 基因簇数 | 个 | | 校外预期 4,000–4,600（README §四，未实测）；密度 851–979/Mb（教材 9.4.5）；0 簇不是失败 |
| 5 M4 | Mash top10 / ANI 最高值与三档 | 文字 / % | | 校外基准 99.83–99.95 / 97.87 / 87.10（README §四，MinHash 估计）；两工具排序一致 |
| 6 M5 | 两树差异 / 目标株位置 / UFBoot·SH-aLRT | 文字 / 两项值 | | 支持值 ≠ 后验概率（教材 11.4.6、讲义 ⑥6.4）；挂 IQ-TREE 文档入口；拓扑只作参考 |
| 7 M6 | 每株蛋白数（n= 株） | 个/株 | | 无某一列接近 0 或高一个量级（教材 11.5.1、ch11 demo） |
| 7 M6 | 核心数 / 泛基因组数（报 n、m、k） | 个家族 | | 三档阈值同时报；缺 1 株 = 91.67%（ch11_core_threshold demo） |
| 7 M6 | 面板构成与选株方式 | 文字 | | 写明是否纳入外群及理由（教材 11.6） |

## 5. 失效条件对照（教材 §8.5/§9.5/§11.5，本实验里在哪一步察觉）

1. **高错误率长读长做 k-mer 勘测 / genomeSize 量级写错**（教材 8.5.3）｜察觉：步骤 1
   直方图单调滑落无主峰（校内 PacBio 轨道按步骤 1 检查点 1 处置，改用外部先验＋总长
   对账）；步骤 2 Canu 日志出荒谬深度。手算「读段总碱基 ÷ genomeSize」与日志对照，
   改后清空输出目录。含错直觉（8.5.3 算术）：21-mer、错误率 0.10 时 89.1% 的 k-mer 带错。
2. **只报连续性/完整性，不查结构**（教材 8.5.2；8.4.9 顺序）｜察觉：步骤 3 QUAST
   无参考版错接栏为空——总长、N50、C 都好看也可能是错接/塌缩；回贴深度塌缩处约
   2×、断点骤降＋跨越读段缺失。报告写明「未检查错接」或给出 minimap2 回贴证据（校外
   轨道用 `GCA_987216485` 手动补 `-r`）。
3. **注释流程不统一 / `##FASTA` 被切：假特异膨胀、核心收缩，且不报错**（教材 11.5.1、
   9.5.2）｜察觉：步骤 7 跑 Roary 前看每株蛋白数＋抽查每份 `.gff` 行数与 `##FASTA`；
   合成复现 `python3 textbook/demos/ch11_annotation_bias.py --selftest`（rc=0）。处置：
   同一软件同一版本同一参数重注释全部输入。
4. **小样本上「95% 核心」与 100% 等价；核心占比是采样与方法的属性**（教材 11.5.2、
   11.5.3）｜察觉：步骤 7 任何核心数同时报 `n`、`m`、`k`（n=12 三档全为 12/12，缺 1
   株 = 91.67%；`python3 textbook/demos/ch11_core_threshold.py --selftest`，rc=0）；
   占比结论写样本量与选株方式。开放/封闭只说观测窗口内的趋势——γ 随选株改变
   （近缘 12 株 γ=0.253、混簇 12 株 γ=0.317；`python3 textbook/demos/ch11_pan_rarefaction.py
   --selftest`，rc=0），不写成物种属性。

## 6. 思考题（指向教材习题，不给答案）

1. 你的面板有 12 株。按「存在比例至少 95%」「至少 99%」「100%」三种写法各算
   需要存在的株数与允许缺失株数；「允许缺失 1 株」对应的存在比例是多少？扩到
   20 株呢？（教材 §11.9 习题 1 → 11.4.4）
2. 存在/缺失矩阵中某几行的存在株数为 12、11、2、1：各属哪一类？`m=1` 的行
   同时属于哪两个类别，报告怎么声明才不重复计数？（§11.9 习题 2 → 11.4.4）
3. 泛基因组曲线末端三个点仍在上升、核心曲线末端仍在下降：各说明什么？报告
   至少还要补哪三项信息？（§11.9 习题 4 → 11.4.5）
4. 你的选型证据链里，哪一条证据能排除哪一类错误？哪一类错误本科流程看不见、
   报告该怎么写？（教材 §8.7 习题 8 的本科版 → 8.4.9/8.5.2）
5. 某株注释半途被杀，交付一个只有头行的空 `.gff`：这个上游静默故障会在 Roary
   矩阵和哪张图上最先暴露？为什么「没有报错」不等于输入完整？（讲义 ⑩Q3 → 教材
   11.4.4 空输入两条路径）

## 7. 提交物

- **对应作业**：u08 综合项目（`08_assessment/undergraduate/project/undergrad_project.md`）。
  评分 30/30/20/10/10＝内容完整性/技术准确性/分析深度/报告规范性/创新性
  （手册 §5.3 与作业规格同口径）。
- **提交**（作业规格 §3）：① 报告 PDF：`学号_姓名_NGS综合项目报告.pdf`；
  ② 数据包：`学号_姓名_NGS综合项目.zip`，内含 `genome.fasta`、对应 `.gff` 与
  可重跑脚本集（脚本不得写死他人绝对路径）。
- **诚实红线**：「预期区间（未实测）」不得写成实测；无参考轨道写明「未检查错接」；
  跳过的步骤写明哪一步、为什么；参考文献只列读过的、DOI 核验过的条目（GB/T 7714-2015）。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材 | 主章 `textbook/chapters/ch11/manuscript.qmd` §11.4 / §11.5 / §11.9；参照 `chapters/ch08/manuscript.qmd` §8.4–8.5、`chapters/ch09/manuscript.qmd` §9.4–9.5 |
| 本单元讲义（原理、⑤日程、⑨排错 E1–E8） | `02_lectures/undergraduate/unit08_project/08_project_lecture.md` |
| 锚定手册（流程与命令以此为准） | `<课程材料目录>/学生实验操作手册.md` §4.1–§4.6、§5 |
| M1/M2 校外轨道脚本链（同 u06） | `03_code/undergraduate/scripts/06_kmer_survey.sh`、`06_assemble_compare.sh`、`06_assembly_eval.sh`；五栏细节见 `11_lab_guides/undergraduate/06_assembly_basics_lab.md` 步骤 1–5 |
| M5/M6 出图脚本 | `03_code/undergraduate/scripts/02_plot_tree_and_pangenome.R`（`tree:` / `roary:` / `--demo` 三入口，只在 `ngs_ug_phylo` 运行） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch11_core_threshold.py`、`ch11_annotation_bias.py`、`ch11_pan_rarefaction.py`、`ch08_n50_vs_completeness.py`、`ch08_kmer_spectrum.py` |
| 数据说明、下载与预期区间 | `06_data/undergraduate/README.md` §2（清单）、§三（降采样）、§四（自查区间）；`06_data/undergraduate/download_ug.sh` |
| 环境定义 | `07_envs/conda/env_ug_assembly.yml`、`env_ug_annotation.yml`、`env_ug_phylo.yml`、`env_ug_base.yml` |
| 作业与报告模板 | `08_assessment/undergraduate/project/undergrad_project.md`、`undergrad_report_template.md` |
