---
title: "实验指导 p02：单细胞聚类稳定性、伪重复诊断与空间转录组"
level: phd
topic: p02
textbook: [ch17]
lecture: ../02_lectures/phd/topic02_scrnaseq_spatial/02_scrnaseq_spatial_lecture.md
env: ngs_phd_sc
---

# 实验指导 p02：单细胞聚类稳定性、伪重复诊断与空间转录组

> 每步五栏：做什么、敲什么、产出哪个文件、看到什么算对、看到什么说明错了。原理与判据在教材第 17 章
> （§17.4 概念方法、§17.5 四条失效条件、§17.7 习题）。
>
> **数字标注规则**：检查点里的数只来自四类入口——① `06_data/phd/README.md` 登记实测（4,515 条码、332/64 MB）；
> ② 教材正文带复现入口（如 `1 - pbinom(k-1, n, p)` 算出的 1,568，§17.4.10；事实性规格 55/100/45 µm）；
> ③ 合成演示 `--selftest` 现跑（0.723 / 0.930 / 0.731）；④ 本指导命令在本数据上的**实测值**（每处写明复算命令）。
> 其余只给**判据形态**或标「预期、未实测」；报错原文的体量（如 future 的 500 MiB）只用于认出该报错，不是阈值。
> 教材已撤下的经验阈值（比对率、内存、主成分数、resolution 区间、显著基因数降幅）本指导不用。

## 0. 本实验对应什么

- **教材**：第 17 章。覆盖 LO17-04（伪重复与 pseudobulk 落地）、LO17-05（数据驱动质控与多分辨率稳定性）、LO17-06（过度校正与完全混杂不可辨识）、LO17-07（空间结论表述与捕获预算）；失效条件对应 §17.5.1–§17.5.4。讲义对应 p02 ⑤（5.0–5.3）、⑥、⑦（⑦-1/⑦-2/⑦-3）、⑨（E1–E10）、⑩。
- **学时与作业**：p02 共 4 学时（2 理论 + 2 实践，`00_design/course_contract.yaml`）；作业另建议上机 5–7 小时（`SCTransform`/`FindAllMarkers` 需排队）、写报告 3 小时，占课程总成绩 **4.5%**（专题实践 27% 中的一份）。
- **环境**：`ngs_phd_sc`（`07_envs/conda/env_phd_singlecell.yml`）。R 侧 r-base 4.3.1、r-seurat 5.3.0、r-harmony 1.2.3、bioconductor-singler 2.4.0、bioconductor-deseq2 1.42.0、r-ggplot2 3.4.2、r-patchwork 1.3.2；Python 侧 python 3.10、scanpy 1.11.5、squidpy 1.6.5。**这些版本号写进报告方法节**（教材 §17.3）。前置只依赖 L0 五个模块。
- **计算纪律与两条路径**：一切计算 `qsub` 投计算节点，登录节点只做下载、建环境、编辑、实查前缀（根 `CLAUDE.md`）。**主路径**＝3.1（合并）＋3.2（主流程）两次提交；3.3–3.9 的逐段 `Rscript` 用于：① 没有 SGE 的个人机器；② 某段失败后单独重跑排错；③ 改参数重算某段。两条路径产物同名同结构，**你走哪条要写进报告**。

## 1. 实验前检查

- **前置自测**（讲义 ② 的表，题号在 `08_assessment/prerequisites/` 五个文件里逐一存在）：`l0_02_r` 第 1/2/5/9/10 题；`l0_06_stats` 第 5/7/10 题；`l0_05_qc` 第 2/4 题；`l0_03_conda` 第 9/10 题；`l0_01_linux` 第 9 题。
- **建/激活环境并核验版本**（建环境在登录节点做）。**在课程仓库根目录敲**：

  ```bash
  conda env create -f 07_envs/conda/env_phd_singlecell.yml     # 只需一次
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_sc
  #   ↑ 个人电脑上没有该路径时直接 conda activate ngs_phd_sc
  Rscript -e 'for (p in c("Seurat","harmony","SingleR","DESeq2","ggplot2","patchwork")) cat(p, as.character(packageVersion(p)), "\n")'
  python -c "import scanpy, squidpy; print(scanpy.__version__, squidpy.__version__)"
  ```

  核对 yml 的 pin（§0 列的八个版本 + R 4.3.1）。**版本只在环境里真有 pin 时才写**（教材 §17.3），对不上以实查为准；本指导起草机是 R 4.5.2 / Seurat 5.5.0，**该机上所有运行记录只作「逻辑跑得通」的证据，从不当版本判据**。
- **脚本静态检查**（课程仓库根目录；应空输出、退出码 0、不产生文件）：

  ```bash
  bash -n 03_code/phd/scripts/02_run_seurat.sh
  bash -n 06_data/phd/download_phd.sh
  for f in 02_seurat_pipeline 02_pseudobulk_de 02_power_cells 02_spatial_visium; do
      Rscript -e "invisible(parse('03_code/phd/scripts/$f.R'))" && echo "OK $f"
  done
  ```

  **为什么两类命令**：`bash -n` 只对 `.sh` 有意义；对 `.R` 跑它会报 `syntax error near unexpected token`——那是用错了检查器，R 脚本的静态检查是 `parse()`。
- **前缀实查与归属核验**（登录节点就能做，不需要算力）。**数据还没下载也能做**：跳到 §2 或直接读共享只读目录 `<课程数据目录>/phd/p02_scrnaseq_spatial/`（下文记作 `$P02`）。

  ```bash
  S=$P02/scrna/GSM6926986_CK0828_features.tsv.gz
  zcat $S | cut -f1,2 | head -3           # 第 1 列基因 ID、第 2 列符号：先看真实命名空间
  for p in '^MT-' '^mt-' '^ATMG' '^ATCG' '^trn' '^rrn' '^tRNA'; do
      printf '%-8s %s\n' "$p" "$(zcat $S | cut -f2 | grep -c "$p")"
  done
  ```

  这条命令数的是**解压后第 2 列**里以该前缀开头的行数。**普通 `grep` 直接读 `.gz` 数的是压缩字节**（教材 §17.5.2）。动物/拟南芥前缀在这份水稻数据上全部命中 0，这是正常的。**但「名字命中」不等于「归属正确」**，必须再按 GFF 核验——这是本专题最容易错的地方：

  ```bash
  curl -sO https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/release-59/gff3/oryza_sativa/Oryza_sativa.IRGSP-1.0.59.gff3.gz
  zcat Oryza_sativa.IRGSP-1.0.59.gff3.gz | awk -F'\t' '($3=="gene"||$3=="ncRNA_gene")&&($1=="Mt"||$1=="Pt"){
     id="";n=split($9,a,";");for(i=1;i<=n;i++){if(a[i]~/^gene_id=/)id=substr(a[i],9);else if(a[i]~/^ID=/&&id=="")id=substr(a[i],4)}
     print id"\t"$1}' > org_ids.tsv
  zcat $S | awk -F'\t' 'NR==FNR{o[$1]=$2;next}{p="other";if($2~/^trn/||$2~/^rrn/)p="trn|rrn";
     else if($2~/^tRNA/)p="tRNA";if(p!="other")print p"\t"(o[$1]?o[$1]:"核内/其它")}' org_ids.tsv - | sort | uniq -c
  ```

  **本数据实测**（2026-11-11，命令即上方两条）：`^trn` 17 条 + `^rrn` 3 条 = **20 条，全部属于 Mt**；`^tRNA` **228 条**里只有 **5 条属 Mt、38 条属 Pt，其余 185 条在核染色体上**（`ENSRNA…` 是核 tRNA 扫描结果）。所以写法只能是：**`--mt-pattern '^trn|^rrn'`（GFF 核验为线粒体）；`^tRNA` 不能并进 `percent.mt`，也不能当叶绿体指标**。**叶绿体在本数据标「不适用」**：按 GFF 归到 Pt 的 65 行合计只有 **95 条 UMI**（全矩阵 4.33 亿），等于没有叶绿体信号——不是阈值问题，是这套原生质体样本里叶绿体转录本基本没被测到，别硬造一个 `percent.cp`。Mt 侧 39 行匹配到矩阵，但**只有 9 行有计数**，`trnP` 一个基因占 Mt 全部 UMI 的 87%（1,602,267 / 1,832,770）：报告里要写明这个 `percent.mt` 是「哪 20 个基因的合计、由谁主导」（`rowSums` 排序自查）。
- **自查演示**（不需要集群，三脚本各 5/5 PASS）：

  ```bash
  cd <课程仓库路径> && export PYTHONDONTWRITEBYTECODE=1
  python3 textbook/demos/ch17_pseudorep_vs_pseudobulk.py --selftest
  python3 textbook/demos/ch17_mt_threshold_sensitivity.py --selftest
  python3 textbook/demos/ch17_resolution_ari.py --selftest
  ```

  这些数是 3.3/3.4/3.7 的读图标尺（教材 §17.5.1–§17.5.3）：零假设下每样本 250/1,000/4,000 个细胞的细胞级假阳性率 **0.723 / 0.854 / 0.925**，pseudobulk 稳在 **0.068**（对照 0.051）；5% 阈值下叶肉样类型保留 **93.0%**、保卫细胞样只留 **0.2%**；ARI 在 k=7 处 **0.731**（k=2 处 0.228、k=16 处 0.603）。

## 2. 实验数据

- **单细胞主线 `GSE222584`**（已在 `06_data/accessions.tsv` 登记）：水稻 RRSV / RGSV 侵染茎基部 10X 数据，
  **9 个样本 = 3 处理（Mock / RGSV / RRSV）× 3 时点（7 / 14 / 21 dpi）**，每个组合只有 1 个样本，
  **没有同条件的生物学重复**。已是 CellRanger 产物（每样本三件套），不必跑 CellRanger、不必自建参考。
- **下载**（登录节点做；体量为 README 登记值，**下载体积 ≠ 碱基数**）：

  ```bash
  bash 06_data/phd/download_phd.sh --topic p02                 # 先 dry-run 看命令
  bash 06_data/phd/download_phd.sh --topic p02 --run \
       --outdir /d3/scratch/${USER}/ngs/data                   # 真下：332 MB + 64 MB
  export P02=/d3/scratch/${USER}/ngs/data/p02_scrnaseq_spatial # 全篇只用这一个定义
  ls $P02 && ls $P02/scrna | wc -l                            # scrna/ 与 spatial/ 两级；27 个文件
  ```

  下载脚本自己在 `<outdir>/p02_scrnaseq_spatial` 建目录，**不要**把 `$P02` 定义成 `<outdir>` 或多加一级 `p02/`——后者会让 3.1
  报 `dir.exists(scr) is not TRUE`。共享只读副本在 `<课程数据目录>/phd/p02_scrnaseq_spatial/`，可直接当
  `$P02` 的替身（`work/`、`results/` 仍放你自己的目录）。
- **唯一合格的自查判据（README 实测）**：`CK0828`（Mock、7 dpi）的 `barcodes.tsv.gz` 共 **4,515** 条细胞条码，带 `-1` 后缀：
  `zcat $P02/scrna/*_CK0828_barcodes.tsv.gz | wc -l` → 期望 4515。其余八个样本只核一条：九个文件 `zcat` 后合计 **55,978**
  （`zcat $P02/scrna/*_barcodes.tsv.gz | wc -l`，本数据实测；单个样本 4,404–8,832，不必逐个数）。
- **README 里的一个陷阱，必须点名**：p02 节同一句既写 `nFeature_RNA > 200`（人类 PBMC 教程的数），又写「植物没有线粒体
  比例这个通用指标」。本实验**不抄 200 当判据**：`nFeature` 的界由本数据分位数定（1%/99%），`percent.mt` 由 95% 分位定（3.3）。
  报告里引用 `200` 必须说明它来自哪里、为什么不用。
- **批次与 dpi 共线（贯穿全篇的设计限制，不是缺陷）**：文件名里的 `0828`/`0904`/`0911` 是三次采样日期，与 7/14/21 dpi 一一
  对应。3.1 的逐细胞表会打印两张列联表，**看形态不看数字**：

  | 表 | 期望形态（本数据实测） | 含义 |
  |---|---|---|
  | `table(batch, condition)` | 3×3，**每格都非 0** | 处理与批次不是一一对应 → 处理比较可做（仍受样本量限制） |
  | `table(batch, dpi)` | 3×3，**只有对角线非 0** | 批次与时点完全共线 → 时间效应不可辨识 |

  两张表看着都「有结构」，含义完全不同——3.6 的要点全在这两张表的差别上。
- **空间数据：10X 官方 `V1_Mouse_Brain_Sagittal_Anterior`（非植物，须在报告声明）**。公开植物 Visium 数据稀缺，故空间部分只学
  方法。`GSE316219`（水稻根—丛枝菌根真菌）与 `GSE284052`（番茄—根结线虫）**只作阅读对象，不跑流程**。下载脚本取到 1.1.0 版
  两包（三件套 tar + spatial tar），**spatial 目录里是旧名 `tissue_positions_list.csv`**（4,992 行），不是新版
  `tissue_positions.csv`。矩阵实测 **2,695** 条 spot（`zcat … | wc -l` 可自查）。

## 3. 实验步骤

> 命令调用 `03_code/phd/scripts/` 现有脚本，不复制全文；参数名与输出文件名已与现版源码核对（按函数名/参数名指认，
> 不按行号）。真实数据全流程**集群未复跑**，属真实样本结果的检查点一律标「预期（未实测）」或只给定性判据。
> `03_code/`、`06_data/`、`07_envs/` 只读；要改脚本一律「cp 个人副本 → 改 → grep 确认 → qsub 副本」。

### 3.1 合并 9 个样本、生成逐细胞元数据（投计算节点）

- **目的**：`Read10X()` 一次只读**一个**目录且要求文件名恰好是三件套，而下载得到 27 个带前缀的文件；同时主流程
  `--meta` 要的是**逐细胞**元数据（按条码取行），不是 9 行的样本表。这一步做错，3.6 会静默跳过整合。
- **为什么投作业**：读 9 份矩阵、稀疏矩阵 `cbind`、写出 332 MB 级文件属计算工作，按根 `CLAUDE.md` 不在登录节点跑。
  下面的脚本**一次产出三件套 + `meta_percell.tsv`**，不需要手填占位符。

  ```bash
  mkdir -p $P02/work && cd $P02/work
  cat > merge_p02_10x.R <<'EOF'
  #!/usr/bin/env Rscript
  # 用法：Rscript merge_p02_10x.R <scrna 目录> <输出目录>
  suppressPackageStartupMessages({ library(Seurat); library(Matrix) })
  a <- commandArgs(trailingOnly = TRUE); scr <- a[1]; out <- a[2]
  stopifnot(dir.exists(scr)); dir.create(out, showWarnings = FALSE, recursive = TRUE)
  bc_files <- list.files(scr, pattern = "_barcodes.tsv.gz$", full.names = TRUE)
  link_dir <- function(s) {                    # 只含标准文件名的临时目录
    tmp <- file.path(tempdir(), s); dir.create(tmp, showWarnings = FALSE)
    for (k in c("barcodes.tsv.gz", "features.tsv.gz", "matrix.mtx.gz")) {
      src <- file.path(scr, paste0(s, "_", k)); stopifnot(file.exists(src))
      suppressWarnings(file.symlink(normalizePath(src), file.path(tmp, k)))
    }
    tmp
  }
  aff <- list()
  for (f in bc_files) {
    s <- sub("_barcodes.tsv.gz$", "", basename(f))
    m <- Read10X(link_dir(s)); colnames(m) <- paste0(s, "_", colnames(m))
    aff[[s]] <- m; cat("[read]", s, dim(m), "\n")
  }
  g <- Reduce(intersect, lapply(aff, rownames))
  cat("samples =", length(aff), " genes =", length(g), " cells =", sum(sapply(aff, ncol)), "\n")
  M <- do.call(cbind, lapply(aff, function(x) x[g, , drop = FALSE]))
  f1 <- read.delim(file.path(scr, paste0(names(aff)[1], "_features.tsv.gz")),
                   header = FALSE, quote = "", stringsAsFactors = FALSE)
  writeLines(colnames(M), gzfile(file.path(out, "barcodes.tsv.gz")))
  write.table(f1, gzfile(file.path(out, "features.tsv.gz")), sep = "\t",
              quote = FALSE, row.names = FALSE, col.names = FALSE)
  tmpm <- tempfile(fileext = ".mtx"); writeMM(M, tmpm)        # 见要点 ④
  system2("gzip", c("-c", "-f", shQuote(tmpm)), stdout = file.path(out, "matrix.mtx.gz"))
  unlink(tmpm)
  chk <- Read10X(out); stopifnot(identical(rownames(chk), g), ncol(chk) == ncol(M))
  cat("[ok] 回读校验通过:", dim(chk), "\n")                  # 这行不出现就别往下走
  # ---- 逐细胞元数据：设计列从文件名推，不手抄样本表 ----
  smp   <- sub("_[ACGTN]+-1$", "", colnames(M))              # 留 登录号_短名
  ids   <- sub("_barcodes.tsv.gz$", "", basename(bc_files))
  alias <- sub("^[^_]*_", "", ids)                           # 留 CK0828 之类
  design <- data.frame(sample = ids,
    condition = sub("\\d{4}$", "", alias),                   # CK/RGSV/RRSV（CK 是 Mock 的文件写法）
    batch     = sub("^[A-Z]+", "", alias),                   # 0828/0904/0911
    dpi       = unname(c("0828" = 7, "0904" = 14, "0911" = 21)[sub("^[A-Z]+", "", alias)]))
  design$condition[design$condition == "CK"] <- "Mock"
  md <- cbind(sample = smp, design[match(smp, design$sample), -1], row.names = colnames(M))
  stopifnot(!anyNA(md$condition), nrow(md) == ncol(M))
  write.table(md, file.path(out, "meta_percell.tsv"), sep = "\t", quote = FALSE, col.names = NA)
  print(table(md$batch, md$condition)); print(table(md$batch, md$dpi))
  EOF
  cat > merge_p02.qsub <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N p02_merge
  #$ -cwd
  #$ -j y
  #$ -pe smp 2
  #$ -l h_vmem=16G
  set -euo pipefail
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_sc
  export P02=/d3/scratch/${USER}/ngs/data/p02_scrnaseq_spatial
  Rscript "$P02/work/merge_p02_10x.R" "$P02/scrna" "$P02/work/merged"
  EOF
  bash -n merge_p02.qsub && grep -n 'P02\|merged' merge_p02.qsub
  qsub merge_p02.qsub && qstat -u "$USER"
  ```

  要点四处：① 每样本建符号链接目录，`Read10X()` 才认三件套；② 条码**必须加样本前缀**（九样本条码会重复，直接 `cbind` 会把细胞数算错）；③ 九个 `features.tsv.gz` 顺序一致，取交集后按行名对齐；④ **`writeMM` 不能直接写 `gzfile()` 连接**：不 `close(con)` 文件压根不出现，显式 `close(con)` 得到几乎空的 gz；可靠做法是先写纯文本 `.mtx` 再 `gzip -c`（如上），写完 `gunzip -t` 复查一遍。**作业内 `export P02` 是必需的**：SGE 不继承登录终端的变量，`set -u` 下未定义的 `$P02` 会让作业直接失败。
- **产出文件**：`$P02/work/merged/` 三件套 + `meta_percell.tsv`（行名＝合并后条码，四列 `sample/condition/batch/dpi`）。
- **检查点**（**集群未实测**；数值是本数据实测值）：
  1. 日志出现 `samples = 9`、`genes = 38866`、`cells = 55978` 与 `[ok] 回读校验通过`——最后一行是「写出的三件套能被 `Read10X` 读回」的唯一证据，没它别往下走；
  2. `meta_percell.tsv` 行数比条码数多 1（表头）：与 `zcat …/barcodes.tsv.gz | wc -l` 对账，两者必须一致；
  3. 两张列联表与 §2 的期望形态一致（前者每格有数、后者只有对角线）；
  4. **条码必须带样本前缀**：`zcat $P02/work/merged/barcodes.tsv.gz | head -1` 应形如 `<登录号>_CK0828_AAAC…-1`；没有前缀说明 9 次 `Read10X` 被直接 `cbind`，细胞数会算错。
- **出错信号**：`Barcode file missing` → 文件名不是标准三件套（链接没建成）；`dir.exists(scr) is not TRUE` → `$P02` 的层级不对（回 §2）；3.7 出现 `duplicate 'row.names' are not allowed` → 拿 9 行样本表当逐细胞表，或某样本在设计表里出现两次；`Warning: Feature names cannot have underscores ('_')` → `Read10X` 把符号统一改成连字符，**这条警告必须留档**（写 marker 名要按连字符写法，→ §17.4.7）。若只写了 9 行样本表当 `--meta`，脚本不报错，但 3.6 会打印「跳过整合：列 'batch' 只有 1 个批次」——不是只有一个批次，而是元数据全取成了 `NA`；逐细胞 `sample` 一旦错位，3.7 的 pseudobulk 就不成立（→ §17.5.1）。

### 3.2 提交主流程（主路径，`qsub`）

- **目的**：一次提交跑完「读入 → 质控 → SCTransform → PCA/UMAP → 多分辨率聚类 → marker →（整合诊断）→ 功效 →
  （可选）空间」。`SCTransform` 与 `FindAllMarkers` 是内存与核数大户，登录节点跑会被 OOM 杀（讲义 ⑨-E7）。
- **命令**（**输入路径与参数写进个人副本**，不要改公共脚本，也不要用 `VAR=value qsub`）：

  ```bash
  cd $P02/work                                     # -cwd：作业日志落在投递目录
  R=/<课程仓库路径>/03_code/phd/scripts
  cp $R/02_run_seurat.sh ./run_seurat.sh           # 副本改名，后文一律用 run_seurat.sh
  cp $R/02_seurat_pipeline.R $R/02_pseudobulk_de.R $R/02_power_cells.R $R/02_spatial_visium.R ./
  # 编辑器改副本四处（按变量名定位，不按行号；值写 `echo $P02` 展开后的**字面绝对路径**，
  # 因为作业不继承登录终端变量，副本里的 $P02 会展开成空）：
  #   INDIR      → /…/p02_scrnaseq_spatial/work/merged
  #   OUTDIR     → /…/p02_scrnaseq_spatial/work/results
  #   META       → /…/p02_scrnaseq_spatial/work/merged/meta_percell.tsv
  #   MT_PATTERN → '^trn|^rrn'（CP_PATTERN 留空：叶绿体指标在本数据不适用，见 §1）
  # 若更愿意在副本里写 $P02/…：必须在 `source … activate` 之后加一行 export P02=<同一路径>，否则 set -u 下当场失败
  # 第二段（pseudobulk 调用）整段注释掉：它硬编码 --condition-col condition，三水平必然产出空表（见下条）
  grep -n 'SCRIPT_DIR\|INDIR\|OUTDIR\|META\|MT_PATTERN\|CP_PATTERN\|h_vmem\|-pe\|pseudobulk' run_seurat.sh
  qsub run_seurat.sh && qstat -u "$USER"
  ```

  **为什么写进副本而不是 `VAR=value qsub`**：那个前缀只给 `qsub` 自身设环境变量，不转交给作业；作业头也没有 `-V`，
  作业拿到的 `INDIR` 是空的，`${INDIR:?…}` 会让作业直接失败（`qsub -v` 是另一条路，本机无 SGE、**未实测**）。脚本做的
  事：作业头 `-pe smp 8`、`-l h_vmem=64G`（默认申请值、不是实测需求）、`-j y`（两路合进一个日志）；作业内
  `source activate ngs_phd_sc`；先写 `env_snapshot.yml`；再依次调主流程、pseudobulk、功效、空间（`VISIUM_DIR` 为空时
  打印「未设置 VISIUM_DIR，跳过空间部分。」）。
- **⚠ 主路径的伪重复陷阱（必须先看）**：那段硬编码 `--celltype-col seurat_clusters --condition-col condition`。这份数据
  `condition` 有**三个水平**，而 `02_pseudobulk_de.R` 只在 `length(levels) == 2` 时继续，其余逐簇打印「condition 不是两水平，
  跳过」——**脚本仍正常退出、四段标题齐全、`de/` 里却只有一张 0 数据行的空表**。所以：**「四段标题齐」≠「拿到差异表」**，
  检查点 3 必须核对表的行数。正确的两两对比在 **3.7** 单独投。
- **产出文件**（都在 `$OUTDIR` 下）：`env_snapshot.yml`、`qc_violin.png`、`elbow.png`、`cluster_stability.tsv`、`markers.tsv`、
  `marker_dotplot.png`、`integration_before_after.png`（**只在真的整合了才出现**）、`integrated.rds`、`sessionInfo.txt`、
  `de/`、`power_cells.png`。
- **检查点**：
  1. 日志开头 `[host]` 行打印的**不是**登录节点主机名——「确实在计算节点跑」的唯一证据（本地跑时是本机名，属正常，
     但不能当集群已跑过的证据）；
  2. 四段标题依次出现；没给 `VISIUM_DIR` 时第 4 段应打印跳过语；
  3. **两行规模 + DE 表行数**：`cells = … genes = …`（`CreateSeuratObject` 之后，已含 `min.features = 200` 与
     `min.cells = 3` 的删减）与 `cells after filter = …`（分位数三联过滤之后）。**两行不是同一道过滤**：两数之差**不能**
     归因于 `min.features`（本数据实测：55,978 个细胞在 `min.features ≥ 200` 后剩 55,973，该步只删 5 个；真正的删减发生在
     分位数那步再删 3,690 个、保留 52,283 个、占全量 93.40%）。两行都抄进报告，第三项看 `wc -l $OUTDIR/de/de_comparison_summary.tsv`，
     **必须 > 1 行**，否则回 3.7；
  4. `env_snapshot.yml` 存在且 `grep ngs_phd_sc` 有命中；与 `sessionInfo.txt` 一起交（§7）。
- **出错信号**：`Rscript: command not found` → 作业没继承环境（⑨-E7/E8）；日志只有 `Killed` 而无 R 报错 → 内存触顶
  （调 `h_vmem`，或先抽 3 个样本调通再全量），**不要**在登录节点重跑；`Error: 必须给 --indir` → 变量没进到作业进程
  （最常见是 `INDIR=… qsub` 写在命令前面）。另有一种**跑通了但结论不成立**：`[warn] pseudobulk 跳过：…`、
  `可用样本 < 4，无法做 pseudobulk 推断`，或汇总表只有表头——这时只剩细胞级比较，把它当组间结论写进报告就是
  §17.5.1 的伪重复（→ §17.5.1），回 3.1 补 `sample` 列、再按 3.7 派生两水平。
- **九样本全量必须先把 future 的 globals 上限调开**。`SCTransform` 把函数与工作对象导出给 worker，默认上限 500 MiB；
  九样本合并后容易撞上（错误关键词 `getGlobalsAndPackages` + `exceeds the maximum allowed size ... per plan()`）。报错里的
  GiB 数字由你的数据规模决定，**不是门槛**。解法（**写进报告方法节**）：① 在副本 `02_seurat_pipeline.R` 的 `set.seed(...)`
  之后加 `options(future.globals.maxSize = 8 * 1024^3)`；② 或写 `<work>/rprofile_p02.R`（内容即该 `options` 行），并在
  `run_seurat.sh` 副本的 `source … activate` 之后加 `export R_PROFILE_USER=<同一绝对路径>/work/rprofile_p02.R`——必须写成作业脚本
  内的 export，登录终端里 `export` 后 `qsub` 不生效。**8 GiB 只是起点**，跑通后按实测峰值调；它只解决「交给 worker 的
  对象太大」，不解决内存本身。仍被 `Killed` 就先 `subset` 抽 3 个样本调通，并在报告里区分「调通」与「跑完」。

### 3.3 质控：分位数截断，不抄 PBMC 的数

- **目的**：把「哪些细胞留下」变成可辩护的定量决定。教材 §17.4.4 的纪律：阈值写**本数据的分位数**。植物要**按 GFF
  核过的细胞器基因集**单独看比例（§1 已做）。
- **命令**：本步在 3.2 的同一脚本里。单独重算或补算指标时（**双引号让 bash 展开 `$P02`；单引号内的 `$P02` 是字面量，
  会报 `cannot open file`**）：

  ```bash
  Rscript -e "suppressPackageStartupMessages(library(Seurat)); m <- Read10X('$P02/work/merged')
              f <- read.delim(gzfile('$P02/work/merged/features.tsv.gz'), header=FALSE)
              mt <- grepl('^trn|^rrn', f\$V2); nc <- Matrix::colSums(m)
              pmt <- Matrix::colSums(m[mt,,drop=FALSE])/nc*100
              cat('percent.mt 中位', round(median(pmt),2), '95%', round(quantile(pmt,.95),2),
                  '99%', round(quantile(pmt,.99),2), '\n')"
  ```

  脚本实际做了什么：`PercentageFeatureSet(pattern = mt_pattern)` 建 `percent.mt`；只有 `--cp-pattern` 非空才建
  `percent.cp`；**检查 `sum(percent.mt) == 0` 并给 warning**；画**过滤前**的小提琴图；`nFeature` 取 1%/99% 分位、
  `percent.mt` 取 95% 分位，三联 `subset` 后打印过滤后细胞数。`min.cells = 3` 与 `min.features = 200` 写死在
  `CreateSeuratObject` 里，**不是命令行参数**——要改就 `cp` 副本改那一行再 `qsub`（报告要说明为什么改/不改）。
- **产出文件**：`qc_violin.png`（脚本只出过滤前一张）＋**自建的** `qc_metrics.tsv`（交付物，脚本不产出）。
- **检查点**（本数据实测，命令见上）：`percent.mt` **中位 0.39%、95% 分位 4.70%、99% 分位 25.87%**，只有 0.66% 的细胞
  为 0——**不是一条贴地直线**。判据是「X 明显大于 0 且过滤没把细胞砍掉大半」：三联过滤保留 **52,283 / 55,978 = 93.40%**。
  这三个数按你自己那次运行重算，逐条抄进 `qc_metrics.tsv`，注明「本数据分位数」。**注意**：算得出来不等于它是线粒体
  比例——它由 §1 那 20 个 Mt 基因决定，报告里要写出基因集来源（GFF 核验）与主导基因。
- **出错信号**：`percent.mt` 整列为 0 且日志有「percent.mt 全为 0」warning → 前缀失配（→ §17.5.2）。**在本数据这个错
  是致命的，不只是警告**：全 0 时 `mt_hi = quantile(..., 0.95) = 0`，`subset(percent.mt < 0)` 一个细胞都留不下，脚本
  直接 `Error in subset(): ! No cells found` 退出（前缀全零时必然复现）。照教材 §17.4.4 的断言做：在副本里那条
  `sum(percent.mt) == 0` 的 `if` 块**之后**加 `stopifnot(max(obj$percent.mt) > 0)`，把静默全 0 变成提前失败。
  某类细胞几乎被清空 → 阈值与类型本底冲突（→ §17.5.2 第五步）。

### 3.4 多分辨率聚类：簇数表只是第一层证据

- **目的**：把「我们鉴定出 N 类细胞」换成「在某区间内目标簇稳定存在」。`resolution` 是算法参数，没有脱离证据的
  正确取值（教材 §17.4.6、§17.5.3）。
- **命令**：同一脚本第 5 步。`res_grid <- sort(unique(c(0.2, 0.4, 0.6, 0.8, 1.0, res_main)))`——五档网格**并入**主值：
  默认 0.5 时表里 **6 行**（0.2/0.4/0.5/0.6/0.8/1.0），设成网格已有的值（如 0.4）只有 5 行。**簇数表证明不了「目标簇在
  区间内稳定」**：它只有两列，簇数不变可能是 A 簇散开、B 簇合并相互抵消。还须做**逐分辨率标签匹配**（§17.4.6 第一项）：

  ```bash
  cat > $P02/work/cluster_match.R <<'EOF'
  #!/usr/bin/env Rscript
  # 用法：Rscript cluster_match.R <integrated.rds> <目标簇号> <输出 tsv>
  suppressPackageStartupMessages({ library(Seurat) })
  a <- commandArgs(trailingOnly = TRUE); obj <- readRDS(a[1]); target <- a[2]; out <- a[3]
  cols <- grep("_snn_res\\.", colnames(obj@meta.data), value = TRUE)   # SCT_snn_res.* 或 RNA_snn_res.*
  ref  <- obj$seurat_clusters                                       # 主分辨率下的簇标签
  tab <- do.call(rbind, lapply(cols, function(cl) {
    lab <- obj@meta.data[[cl]]; hit <- lab[ref == target]
    k <- names(which.max(table(hit))); ov <- sum(hit == k)
    data.frame(assigned = cl, best_cluster = k, n_cells = sum(lab == k),
               recall = round(ov / sum(ref == target), 3),
               jaccard = round(ov / (sum(lab == k) + sum(ref == target) - ov), 3))
  }))
  tab <- tab[order(tab$recall, decreasing = TRUE), ]
  write.table(tab, out, sep = "\t", quote = FALSE, row.names = FALSE); print(tab)
  EOF
  Rscript $P02/work/cluster_match.R $P02/work/results/integrated.rds 0 $P02/work/results/cluster_match.tsv
  ```

  判读：`recall`（原目标簇的细胞有多大比例仍落在同一个新簇）与 `jaccard`（两份标签的重叠）**一起看**；recall 高而
  jaccard 低说明该分辨率下这个簇把别的细胞也吸了进来。稳定区间＝两者都不塌的那一段。教材还要求第二、三项（**重抽样
  共聚类频率**、**轮廓系数**），作业「至少两种评估手段」从三项里挑。重抽样最小可跑版：随机抽 80% 细胞（比例自定并
  写明），重跑 `FindNeighbors`＋`FindClusters` 回到同一 `resolution`，再用上面的 `recall/jaccard` 对齐主分辨率标签，
  重复 5 次取均值。
- **产出文件**：`cluster_stability.tsv`（两列，同时 `print` 到日志）＋**自建的** `cluster_match.tsv`。
- **检查点**：1) 表行数 = 6（默认参数），`resolution` 列升序且含 0.5；2) 簇数随 resolution 单调不减（预期、未实测），
  画折线（§7 `fig5`）并标出「簇数不再增长」的拐点段；3) 报告那句话必须带区间且带两个数：先定出目标簇「在多宽的
  resolution 范围内 recall 与 jaccard 都不塌」，再写「在 X–Y 区间内，第 k 簇的细胞归属保持 ≥ Z%（recall），top marker
  排序不变」。**区间按你自己这两张表定**，`0.4–0.8` 只是教材设例。
- **出错信号**：`找不到聚类列 SCT_snn_res.0.5；现有：…` → `--resolution` 主值不在网格里，或副本里改过 `res_grid`；
  找不到 `cluster_stability.tsv` → 作业没跑到第 5 步；`cluster_match.tsv` 里各行 `best_cluster` 互不相同而 recall 都低
  → 该目标簇在那些分辨率下不存在，正是「只在某一档出现」的算法假象（→ §17.5.3）。合成标尺：ARI 在 k=7 处 0.731、
  k=2 处 0.228、k=16 处 0.603（`ch17_resolution_ari.py --selftest`），它只说明**稳定性**，不证明平台区就是真值。

### 3.5 marker：描述性比较，不做组间推断

- **目的**：给每簇一份注释材料，同时划清用途边界：`FindAllMarkers` 是簇内 vs 簇外的描述性比较，不是处理 vs 对照的检验。
- **命令**：同一脚本第 6 步，`--step` 默认 `all`；`all` 与 `annotate` **走同一条路径**（都跑完前 5 步再出 marker）；
  阈值 `only.pos = TRUE`、`min.pct = 0.25`、`logfc.threshold = 0.25`；取每簇 `avg_log2FC` 前 3 个基因画点图。
  **`--singler-ref none`（默认）下不给自动标签**：参考不是 `none` 时脚本只打一行提醒「非模式物种硬套参考会得到一串
  看似合理的错标签」，并不真的调用 SingleR。
- **产出文件**：`markers.tsv`、`marker_dotplot.png`；交付物里改名为 `markers_top.tsv`（§7）。
- **检查点**：列含 `p_val`、`avg_log2FC`、`pct.1`、`pct.2`、`p_val_adj`、`cluster`、`gene`；簇号是整数；报告里若写细胞
  类型名，必须写清那是**你自己按 marker 手工判定的**；`pct.1` 高而 `pct.2` 也高 → 不是类型特异 marker。教材 §17.4.7 只给
  一条经验参考：`pct.1 > 0.6` / `pct.2 < 0.2` 是**经验参考不是判据**，更稳的看法是跨簇梯度。
- **出错信号**：`markers.tsv` 为空（0 行）→ 阈值太严或簇太少；符号写成带下划线的原写法 `5_8S_rRNA` 却查不到 → 3.1 的
  `_`→`-` 改名（→ §17.4.7）。**另有一类更危险的无错**：把 `FindAllMarkers` 换成「Mock vs RRSV」的 `FindMarkers` 并按
  `p_val_adj` 下结论——脚本照样出表、照样成片小 p 值，但检验单位已从样本变成细胞，这正是 §17.5.1。

### 3.6 整合诊断：两张列联表必须分开看

- **目的**：决定「能不能整合」，以及整合后**哪些结论仍成立**。教材 §17.5.3 的两半：过度校正与完全共线不可辨识。
- **命令**：同一脚本第 7 步。逻辑：① `BATCH_COL` 不在元数据里 → 打印跳过并说明缺列；② 有 `condition` 列 → 打印
  `table(batch, condition)`，`confounded <- all(rowSums(tb > 0) <= 1) && ncol(tb) > 1`，判为完全共线时 **warning 并拒绝
  整合**；③ 缺 `condition` 列时告警「无法检查混杂」但**照常整合**；④ 只有一个批次时跳过；⑤ 真整合时
  `RunHarmony(group.by.vars = batch_col, assay.use = "SCT")`，重建 UMAP，出前后对照图。**脚本只查 `batch × condition`，
  不查 `batch × dpi`，也不会因为 dpi 共线而拒绝整合**。共线这件事必须你自己打印、自己写进结论：

  ```bash
  Rscript -e "suppressPackageStartupMessages(library(Seurat)); o <- readRDS('$P02/work/results/integrated.rds')
              print(table(o\$batch, o\$dpi))"
  ```

- **产出文件**：日志里的列联表打印 + 被拒时的 warning；整合成功时才有 `integration_before_after.png`（**没有这张图不等于失败**）。
- **检查点**：
  1. **按目标效应分开判**：`batch × condition` 每格有数（本数据实测）→ **处理比较可做**（仍受样本量与共线牵制）；
     `batch × dpi` 只有对角线（本数据实测）→ **时间效应与批次效应不可辨识**。二者不矛盾，是两件不同的事。本数据可以
     整合来处理比较，但**整合后的 UMAP 与任何跨 dpi 差异都不得解释为独立的时间效应**；报告方法节要有这一句：「采样批次
     与取样时点完全对应，无法将时间效应与批次效应分离，跨时点比较均为探索性描述」；
  2. 整合前后各一张 UMAP，**分别按 `batch` 与按 `condition` 上色**（`fig3` 要前后两版）。判据不是「混得越匀越好」，
     而是「批次混匀**且**处理特异簇还在」（→ §17.5.3）：整合后处理特异簇消失、关键 marker 梯度变钝，就是过度校正。
- **出错信号**：`Error in check_legacy_args(...) : Argument assay.use is unhandled` → **Harmony 版本敏感**：该参数在
  harmony 1.2.3（yml 的 pin）上有效，harmony ≥ 2 会拒绝；按 pin 跑，若环境确实是 harmony ≥ 2 就在副本里删掉该参数
  （这正是「版本号要写进报告」的理由）。打印「跳过整合：列 'batch' 只有 1 个批次」而数据明明有 3 个批次 → 元数据全是
  `NA`（回 3.1）。还有一类「跑通了但错了」：整合后按 `condition` 上色的两张 UMAP 变得一模一样、处理特异簇消失——
  这是过度校正，不是「混得好」。

### 3.7 pseudobulk 对照：换统计单位，不数「掉多少」

- **目的**：同一份数据、同一个比较做两遍：把细胞当独立样本（`FindMarkers`，伪重复）与把样本当独立样本（pseudobulk +
  DESeq2），按**统计单位**判读，不按显著基因数判读（§17.4.9、§17.5.1）。
- **命令**（本数据有**三种处理**而脚本只接受两水平——本步最容易踩的坑。脚本都存文件、路径靠参数传，**不要在
  `Rscript -e '…'` 里写 `$P02`**）：

  ```bash
  cat > $P02/work/make_pair.R <<'EOF'
  #!/usr/bin/env Rscript
  # 用法：Rscript make_pair.R <integrated.rds> <输出目录> <对照水平> <处理水平>
  suppressPackageStartupMessages({ library(Seurat) })
  a <- commandArgs(trailingOnly = TRUE); obj <- readRDS(a[1]); out <- a[2]; ctl <- a[3]; trt <- a[4]
  DefaultAssay(obj) <- "RNA"
  obj[["RNA"]] <- NormalizeData(obj[["RNA"]], verbose = FALSE)   # 见出错信号 2
  obj <- subset(obj, subset = condition %in% c(ctl, trt))
  obj$trt2 <- factor(ifelse(as.character(obj$condition) == ctl, ctl, trt), levels = c(ctl, trt))
  saveRDS(obj, file.path(out, "rds_pair.rds"))
  cat("[ok] pair:", ctl, "vs", trt, " cells =", ncol(obj), "\n"); print(table(obj$sample, obj$trt2))
  EOF
  Rscript $P02/work/make_pair.R $P02/work/results/integrated.rds $P02/work/results Mock RRSV
  Rscript /<课程仓库路径>/03_code/phd/scripts/02_pseudobulk_de.R \
          --rds $P02/work/results/rds_pair.rds \
          --sample-col sample --celltype-col seurat_clusters --condition-col trt2 \
          --min-cells 10 --outdir $P02/work/results/de
  wc -l $P02/work/results/de/de_comparison_summary.tsv      # 必须 > 1
  ```

  脚本做什么：`--celltype-col` 默认 `celltype`、`--condition-col` 默认 `condition`（**本流程都不产生这两列**，照抄讲义
  示例会 `meta.data 缺列`）；`--min-cells` 默认 10；`DefaultAssay <- "RNA"`（Harmony 只改 reduction）；取 RNA 的 `counts`
  层求和（**不是** `AverageExpression`）；簇内细胞 `< 3 * min_cells` 跳过；细胞级 `FindMarkers`（`logfc.threshold = 0`、
  `min.pct = 0.1`）；指示矩阵求和；每样本细胞数 `< min_cells` 的样本剔除；可用样本 `< 4` 跳过；`stopifnot(all(pb %% 1 == 0))`；
  `rowSums(counts) >= 10`；写汇总表。**`sample` 列必须真的存在**（3.1 提供）。**本数据只能做 Mock vs 一种病毒**：一次
  派一对，另一对改参数重跑（每组只有 3 个样本，两对之间不共享样本）。
- **产出文件**：`de_comparison_summary.tsv`（每簇一行：`cell_type, n_cells, n_samples, sig_findmarkers, sig_pseudobulk,
  ratio`）＋每簇两套 `<簇>_findmarkers.tsv` / `<簇>_pseudobulk.tsv`。交付物要**你关注的目标簇**：从各簇结果里挑出你要
  讨论的那一簇（例如处理下最可能的响应簇），复制/改名为 `de_findmarkers.tsv` 与 `de_pseudobulk.tsv`，并在报告写清
  **选它的生物学依据**；若讨论了多个簇就逐簇对比说明（**口径是「挑目标簇」，不是把所有簇堆进一张表**）。
- **检查点**：1) 汇总表**有数据行**，`n_samples` 等于该簇可用样本数（Mock vs RRSV 时最多 6，两侧各 3），每簇细胞数抄进
  报告；2) **两套 `n` 单位不同**：`sig_findmarkers` 的 n 是细胞数、`sig_pseudobulk` 的 n 是样本数——写显著基因数必须带
  单位与检验名；3) 判读按 §17.5.1 四处：检验单位写清了吗、两表 n 与样本表对得上吗、显著基因是否几乎全部显著、p 值是否
  挤在浮点下限（这是**待查信号**，先排除数值实现与过滤设定，§17.4.1）；4) 「掉出显著」的基因要看**个体间分布**：top10
  里若差异由单一样本驱动，pseudobulk 里塌掉是正常的（思考题 2）。
- **出错信号**：
  1. **汇总表只有表头（0 数据行）**：三水平 `condition` 的必然结果——每簇都打印「condition 不是两水平，跳过」，脚本仍
     **正常退出**（本机用同构合成数据复现：表文件仅表头、`wc -l` 为 1）。解法即上面 ①。报告若交空表按未完成计；
  2. `Warning: No layers found matching search pattern provided` + `FindMarkers 失败: … subscript out of bounds`，且
     `sig_findmarkers` 全为 `NA` → **RNA assay 的 `data` 层是空的**（`SCTransform` 只填 SCT assay）。解法：在 ① 里先
     `NormalizeData(obj[["RNA"]])`。⑨-E5 讲的是「别用 Harmony 坐标做差异表达」，这里多一条同族现象：**层没建**同样静默出错；
  3. `Error: meta.data 缺列: sample` → 元数据没有逐细胞 `sample` 列（回 3.1）；
  4. `some values in assay are not integers` → 用了均值/归一化值（⑨-E9）：pseudobulk 必须对**原始 counts** 求和；
  5. `Cell group has fewer than 3 cells` → 该簇在某样本里捕获太少（信息不足，不是 bug，⑨-E6）；
  6. **最隐蔽的一种**：汇总表有数据行、两套数也填上了，但报告只写「pseudobulk 显著基因少很多，说明细胞级结果不可信」
     ——这是把「单位不同」误读成「方法优劣」。判据是统计单位与个体间分布（→ §17.5.1）。

### 3.8 检出功效：设计阶段算，别在结果里补

- **目的**：回答「欲以某把握至少捕获 k 个占比 p 的稀有细胞，需要测多少个细胞」，并弄清**期望捕获达标 ≠ 把握达标**、
  **捕获达标 ≠ 具备检验功效**（教材 §17.4.10）。
- **命令**（`--out` 是 PNG，`n_req` 只打印到 stdout，**必须自己重定向**）：

  ```bash
  Rscript /<课程仓库路径>/03_code/phd/scripts/02_power_cells.R \
          --prop 0.01 --k 10 --power 0.95 --out $P02/work/results/power_cells.png \
          | tee $P02/work/results/power_cells.txt
  # 作业 Q5 版（0.5%、至少 20 个、90%）：同样必须 tee，否则拿不到 power_cells.txt
  Rscript /<课程仓库路径>/03_code/phd/scripts/02_power_cells.R \
          --prop 0.005 --k 20 --power 0.90 --out $P02/work/results/power_cells_q5.png \
          | tee -a $P02/work/results/power_cells.txt
  ```

  脚本做什么：`prob_ge <- function(n, k, p) 1 - pbinom(k - 1, n, p)`（精确二项，不取近似）；从 n = 10 起**以 10 为步长**
  递增到首个达标值；打印 `--> 需要测的细胞数: n_req`；打对照表（含 `round(k/prop)` 那一行）、两条限制、画图。
- **产出文件**：stdout（`power_cells.txt`）＋两张 PNG。**两者不是一回事**：`--out` 只给图。
- **检查点**（可自算：网格值跑脚本，整数最小值用同一 `prob_ge` 逐整数试算；教材 §17.4.10 给同一对数）：
  1. **区分「网格值」与「整数最小值」**：默认参数下脚本给 **1,570**（网格首个达标，P = 0.9507），逐整数最小值 **1,568**
     （P = 0.9502）；作业 Q5 版网格 **5,180**、整数最小 **5,178**（P = 0.90016）。写哪个都要注明口径；
  2. 教材习题版：p = 0.1%、k = 10、95% → 整数 **15,702**、网格 **15,710**；p = 0.3%、k = 15、90% → 整数 **6,707**、
     网格 **6,710**（`--prop 0.003 --k 15 --power 0.90` 复现网格值）；
  3. 「期望达标 ≠ 把握达标」必须抄进记录表：n = 1,000 时期望捕获正好 10 个，把握只有 **0.543**；n = 2,000 时升到
     **0.995**（`1 - pbinom(9, n, 0.01)`；§17.4.10）；
  4. 结论要写业务含义：这个细胞数对预算与通道数意味着什么，且**捕获够了也不等于能做组间比较**。
- **出错信号**：`power_cells.txt` 里只有图路径 → 你把 `--out` 当输出文本了；把网格值写成「精确所需细胞数」→ 口径混淆；
  用泊松近似自算而差一点点（n = 1,570 处 0.9499 vs 精确 0.9507）→ 近似偏保守，不是算术错；把 `n_req` 当成「可以做组间
  比较了」的依据——功效算的是「捕获到细胞」，检验功效取决于**独立个体数**（→ §17.5.1）。

### 3.9 空间转录组：官方演示数据，学方法不学生物学

- **目的**：跑通 Visium 的目录结构、质控、聚类与空间可视化，并**学会写受物理约束限制的结论**（教材 §17.5.4）。
- **命令**：解开两包后目录里只有 mtx 三件套，而公共脚本调用 `Load10X_Spatial()`，它要 `filtered_feature_bc_matrix.h5`。
  **两条路都完整可跑通**：

  ```bash
  SP=$P02/spatial
  mkdir -p $P02/work/visium && cd $P02/work/visium
  tar xzf $SP/V1_Mouse_Brain_Sagittal_Anterior_filtered_feature_bc_matrix.tar.gz
  tar xzf $SP/V1_Mouse_Brain_Sagittal_Anterior_spatial.tar.gz     # 解到同层，得到 spatial/
  ls filtered_feature_bc_matrix spatial                           # 三件套 + tissue_positions_list.csv

  # 路线①（推荐）：取官方 .h5 放进本目录（与 spatial/ 同级），公共脚本原样跑通
  curl -sL -o filtered_feature_bc_matrix.h5 \
    'https://cf.10xgenomics.com/samples/spatial-exp/1.1.0/V1_Mouse_Brain_Sagittal_Anterior/V1_Mouse_Brain_Sagittal_Anterior_filtered_feature_bc_matrix.h5'
  ls -l filtered_feature_bc_matrix.h5                             # 约 20.6 MB（20,554,697 字节）
  Rscript /<课程仓库路径>/03_code/phd/scripts/02_spatial_visium.R \
          --indir $P02/work/visium --outdir $P02/work/results/spatial --resolution 0.8
  ```

  ```bash
  # 路线②：不取 .h5，只把副本里的读入一步换掉，其余五步（质控/聚类/出图/markers/save）一字不改
  cp /<课程仓库路径>/03_code/phd/scripts/02_spatial_visium.R ./spatial_mtx.R
  # 编辑器把 `sp <- Load10X_Spatial(data.dir = indir)` 一行替换为下面四行，然后投/跑：
  #   m   <- Read10X(file.path(indir, "filtered_feature_bc_matrix"))
  #   img <- Read10X_Image(file.path(indir, "spatial"), image.name = "tissue_lowres_image.png")
  #   sp  <- CreateSeuratObject(m, assay = "Spatial"); sp[["slice1"]] <- img[Cells(sp)]
  Rscript ./spatial_mtx.R --indir $P02/work/visium --outdir $P02/work/results/spatial --resolution 0.8
  ```

  两条路的产物同名同结构，差别只在读入方式。**空间数据不按 UMI 硬过滤 spot**（低 UMI 可能是真实的低细胞密度区，
  直接滤掉会人为制造组织空洞——先看图再决定），这是两个版本共同的纪律。
- **产出文件**：`spatial_qc.png`、`spatial_clusters.png`、`spatial_markers.tsv`、`visium.rds`、`sessionInfo.txt`；
  传 `--features` 时才有 `spatial_features.png`。
- **检查点**（**集群未实测**；以下数值是两条路径在本数据上的实测形态）：
  1. 日志 `spots = 2695  genes = 32285`（`zcat filtered_feature_bc_matrix/barcodes.tsv.gz | wc -l` 得 2,695 可自查），
     `spatial_qc.png` 里 UMI 的空间分布应呈组织轮廓而不是随机散点；
  2. `SpatialDimPlot` 的簇分布**与组织结构对得上**（预期、未实测）；若呈规则平行条带且与形态无关，先疑芯片区域/
     图像配准或该基因根本没表达（讲义 ⑥ 末行）；
  3. 报告表述必须停在「55 µm 微区」这一层：spot 直径 55 µm、中心距 100 µm、间隙 45 µm，官方口径一个 spot 覆盖
     **1–10 个细胞**（植物切片 1–3 个是**估计**不是规格），约**七成**面积未被采样（覆盖率手算：方形点阵
     π·27.5²/100² = 23.8%，六角密排 27.4%，按 4,992 spots / 6.5×6.5 mm² 为 28.1%——三个算式写进方法或附录，可计算器复核）；
  4. 「换成自己的植物样本会卡在哪」要能答三处：切片与包埋、参考基因组与探针设计、叶绿体污染（§17.4.11 末段）。
- **出错信号**：
  1. `Error in Load10X_Spatial(data.dir = indir) : File not found` → **本实验最常见的坑**：下载的是 mtx 三件套。按路线①
     取 `.h5`（实测 HTTP 200、20,554,697 字节，放进目录后公共脚本一次跑通），或按路线② 改读入四行。别只画一张
     `SpatialDimPlot` 就交差——交付物要 `spatial_markers.tsv` 与 `spatial_qc.png`；
  2. 报找不到 `tissue_positions_list.csv` 一类错 → 先 `ls spatial/` 看真实文件名。**这份 1.1.0 数据用的是旧名
     `tissue_positions_list.csv`**（4,992 行），新版才是 `tissue_positions.csv`；按实际文件名处理（讲义 ⑨-E10）；
  3. `no slot of name "coordinates"` → 你用了旧版 `img@coordinates` 写法；Seurat 5.x 里这张图是 `VisiumV2` 对象，用
     `img[Cells(obj)]` 再挂到对象上（路线② 已如此写）；
  4. 把 spot 当细胞写结论（「某基因在某类细胞中特异诱导」）→ 结论过强（→ §17.5.4）：只能写「某 55 µm 微区富集表达」；
     要落到细胞层面必须有去卷积**且**参考覆盖组织里可能存在的全部类型，或直接上 RNA 原位杂交/免疫荧光。

## 4. 结果记录表（学生填写，不预填；「自查判据」列给来源口径）

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 | 实查版本：R / Seurat / harmony / SingleR / DESeq2 / scanpy / squidpy | 版本号 | | 4.3.1 / 5.3.0 / 1.2.3 / 2.4.0 / 1.42.0 / 1.11.5 / 1.6.5（yml 的 pin），以实查为准 |
| 1 | 细胞器前缀命中数与 GFF 归属 | 条 | | `^trn`+`^rrn` 必须全为 Mt；`^tRNA` 多为核内，不得并入 `percent.mt`（§1 命令） |
| 3.1 | 合并后样本数 / 特征数 / 细胞数 | 个 | | 9 / 38,866 / 55,978（本数据实测）；`Read10X` 回读校验必须通过 |
| 3.1 | 单样本条码数（CK0828） | 条 | | **4,515**（`06_data/phd/README.md` 实测）；九样本合计 55,978 |
| 3.1 | 两张列联表形态 | 计数表 | | 前者每格有数、后者只有对角线（本数据实测）；含义不同（§17.6） |
| 3.2 | 日志 `[host]` / 四段标题 / `de/` 表行数 | 文本 | | 主机名不是登录节点；`de_comparison_summary.tsv` 必须 >1 行 |
| 3.2 | 读入规模 / 过滤后细胞数 | 个 | | 取日志两行；后者是分位数过滤结果（本数据 52,283，93.40%）；差值不能归因于 `min.features` |
| 3.3 | 过滤前后细胞数 + `nFeature` 分位、`percent.mt` 95% 分位 | 个 / 分位 | | 写「本数据分位数」；中位 0.39%、95% 4.70%（实测）；不抄 5% 与 200 |
| 3.3 | `percent.mt` 是否全 0 | 是/否 | | **必须「否」**；全 0 在本流程以 `No cells found` 终止（→ §17.5.2） |
| 3.4 | `cluster_stability.tsv` 行数 / 各档簇数 / recall-jaccard 区间 | 行 / 个 / 区间 | | 6 行（0.2–1.0 并入主值）；簇数单调不减（预期、未实测）；区间按你自己的 `cluster_match.tsv` 定 |
| 3.5 | 每簇 top marker 与 `pct.1`/`pct.2` | 基因/比例 | | `pct.1>0.6`、`pct.2<0.2` 只是经验参考（§17.4.7）；基因名按 `-` 写法 |
| 3.6 | 两张列联表 / 是否整合 / 时间效应能否解释 | 是/否 | | `batch×condition` 可做处理比较；`batch×dpi` 共线 → 时间效应不可辨识（§17.5.3） |
| 3.7 | 两套显著基因数（各带单位与检验名）/ top10 个体间分布 | 个 / 定性 | | 细胞级 n 是细胞数、pseudobulk n 是样本数；两种分布模式见思考题 2（§17.4.9） |
| 3.8 | 设计算例的 n（注明网格值还是整数最小值） | 个 | | 1,570 / 1,568；15,710 / 15,702；6,710 / 6,707；5,180 / 5,178（§17.4.10） |
| 3.8 | n = 1,000 与 n = 2,000 的把握 | 概率 | | 0.543 / 0.995（`1 - pbinom(9, n, 0.01)` 现算） |
| 3.9 | spots 数 / 簇数 / 空间图形态 / 结论限定句 | 个 / 定性 / 文本 | | `spots = 2695`（条码可自查）；只能写到「55 µm 微区」，官方 1–10 cells/spot（§17.5.4） |

## 5. 失效条件对照（教材 §17.5，本实验里在哪一步、看什么能察觉）

1. **〔博〕把细胞当重复做差异检验：流程不报错，结果表里成片极小 p 值**（§17.5.1）｜3.7：`de_comparison_summary.tsv` 把
   `sig_findmarkers` 与 `sig_pseudobulk` 并列摆着，`n_samples` 只有个位数。**察觉**：①方法里写清检验单位；②两表 `n` 与
   样本表对账；③看显著基因分布（几乎全显著、p 值挤在下限→先疑统计单位与数值实现）；④跑同一比较的 pseudobulk 对照。
   量级标尺：`ch17_pseudorep_vs_pseudobulk.py --selftest` 的 0.723 / 0.854 / 0.925 vs 0.068。**不要把「显著数掉了多少」当结论**。
2. **〔硕〕照搬人类 PBMC 的质控阈值：`percent.mt` 整列 0，图上只是一条贴地线**（§17.5.2）｜3.3：本数据若用 `^MT-`，命中 0 → 全 0 → 脚本先 warning，随后在 `subset` 处 `Error in subset(): ! No cells found` 终止。**察觉**：①前缀命中数必须大于 0 并**按 GFF 核归属**（`^tRNA` 那个坑就在这里）；②加 `stopifnot(max(percent.mt) > 0)`；③画分布图看阈值切在哪；④植物另看叶绿体——**本数据叶绿体信号≈0，标「不适用」也是合格答案**；⑤比较过滤前后各类型的保留比例。量级标尺：5% 阈值下 93.0% vs 0.2%。连带项：`nFeature_RNA > 200` 在 3′ UTR 注释不全的物种上会误杀正常细胞——本实验按分位数定阈。
3. **〔博〕resolution 定稿与过度校正：结论写在单一参数上**（§17.5.3）｜3.4 与 3.6：`cluster_stability.tsv` 只有一列簇数，
   摘要却写「发现 N 类」；或整合后批次完美混匀而处理特异簇消失。**察觉**：分辨率侧——跑 0.2–1.0 网格、读簇数变化、
   **再做逐分辨率标签匹配（recall/jaccard）**＋重抽样共聚类＋轮廓系数，结论限定在区间内；整合侧——打印
   `batch×condition` 与 **`batch×dpi`** 两张表、共线的那一对在方法里声明、前后各画一次按批次/按处理上色的 UMAP。
   本数据的正确落点是**处理比较可做、时间效应不可辨识**。量级标尺：ARI 0.228 / 0.731 / 0.603，稳定性不等于正确性。
4. **〔硕〕Visium 的 spot 不是细胞：把 55 µm 微区的信号写成细胞结论**（§17.5.4）｜3.9：`spatial_clusters.png` 与
   `spatial_markers.tsv` 看着正常，报告却写「某类细胞特异诱导了某基因」。**察觉**：①方法里写 spot 尺寸与中心距；
   ②用组织学切片核对每 spot 细胞数量级（官方 1–10，植物 1–3 是估计）；③出现「某类细胞」就回溯依据是 spot 还是单细胞；
   ④看去卷积参考是否覆盖全部可能类型。盲区三套手算（23.8% / 27.4% / 28.1%）→ 写「约七成」。

## 6. 思考题（指向教材 §17.7 博士层，不给答案）

1. 本实验的 `percent.mt` 若整列为 0，脚本会先给 warning 再在 `subset` 处终止。写出至少三个可能的原因、一个十分钟内能做完
   的排查动作，以及改完前缀后你用哪两个输出确认已修好。（§17.7 第 2 题 → §17.4.4、§17.5.2）
2. 你在 3.7 拿到了两套结果。挑出细胞级检验里顶级显著、在 pseudobulk 里显著性崩塌的前 10 个基因，检查它们在各个独立样本
   间的表达分布，写出你预期看到的两种模式，并说明哪一种更像伪重复造成的。（§17.7 第 6 题 → §17.4.9）
3. 本数据的采样批次与 dpi 完全共线。列出这份数据**能**回答与**不能**回答的问题各两条，并为「不能回答」的两条各写一句可
   放进论文限制一节的话（不许写「需要进一步验证」这类空话）。（§17.7 第 7 题 → §17.6）
4. 把「某处理诱导了 15 类特定亚群」改写成可证伪的结论，写出验证它需要的三项稳定性检查与各自判据；若目标亚群只在
   resolution 0.5 出现、0.6 消失，应如何表述？（§17.7 第 8 题 → §17.4.6、§17.5.3）
5. 目标类型占 0.3%，要求以 90% 把握至少捕获 15 个：写出算式与结果，并讨论若微流控单通道一次回收约 10,000 个细胞（设例），
   需要几个通道、这个数在实际课题里是否可行。（§17.7 第 10 题 → §17.4.10；口径见 3.8 检查点 2）
6. 把 3.9 的一条 spot 层结论（你自己写的那句）改写成符合 Visium 物理约束的表述，并说明要支撑原句还需要什么实验证据。
   （§17.7 第 4 题的博士层版本 → §17.4.11、§17.5.4）
7. 教材 §17.7 第 5 题给了一个**设例**：每组 2 只动物、各捕获 12,000 个单细胞，声称 6,800 个显著差异基因、大量
   `p_adj < 1e-200`。这三处数字都是教材的假设情境，不是你手上的结果。列出三条统计性质疑，每条配一个可执行复核动作，并指出
   哪一条能只靠 3.7 的 `de_comparison_summary.tsv` 完成、哪一条必须回去查每样本细胞数与可用样本数。（§17.7 第 5 题 → §17.4.1、§17.4.9、§17.5.1）

## 7. 提交物

- **对应作业**：`08_assessment/phd/assignments/p02_scrnaseq_spatial_practice.md`（占课程总成绩 4.5%），打包
  `学号_姓名_p02.zip`（≤ 200 MB；超了去掉 `.rds` 中间对象，保留 `results/` 与 `figs/`）。解压后：

  ```
  学号_姓名_p02/
  ├── report.pdf                      # 正文 ≤ 8 页；质控与参数依据 / 聚类稳定性 / 整合诊断 /
  │                                   # 伪重复与 pseudobulk / 方法选择与结果可信度（≤1 页）
  ├── scripts/ run_seurat.sh（你实际投递的 SGE 脚本）、params_rationale.md（四个参数的依据）
  ├── results/ qc_metrics.tsv、cluster_stability.tsv、cluster_match.tsv、markers_top.tsv、
  │            de_findmarkers.tsv、de_pseudobulk.tsv、power_cells.txt、ai_marker_audit.tsv
  ├── figs/                           # 标题/轴/图例一律英文（中文在集群 R 下会变方块）
  │   ├── fig1_qc_violin.png          ├── fig2_elbow.png
  │   ├── fig3_umap_by_batch_*.png    # 整合前后各一版
  │   ├── fig4_umap_by_cluster.png    ├── fig5_stability.png
  │   └── fig6_de_comparison.png
  ├── ai_logs/prompt_and_reply.md     # ⑧ 的 marker 表任务原文往返（含模型名与日期）
  └── env_snapshot.yml                # 3.2 产出的 conda env export --no-builds
  ```

- **六张图的来源**（前两张是重命名，后四张必须自己画；下面的片段已在本机同构数据上跑到出图）：

  ```r
  # fig1 / fig2：直接重命名 $OUTDIR 的产物（cp qc_violin.png figs/fig1_qc_violin.png；elbow 同理）
  dir.create("figs", showWarnings = FALSE)      # 缺这一行 ggsave 报 Cannot find directory 'figs'
  suppressPackageStartupMessages({ library(Seurat); library(ggplot2) })
  P <- Sys.getenv("P02"); o <- readRDS(file.path(P, "work/results/integrated.rds"))  # 存成 .R 文件再跑
  for (rd in intersect(c("umap", "umap_harmony"), names(o@reductions)))      # fig3：整合前后各一版
    ggsave(sprintf("figs/fig3_umap_by_batch_%s.png", rd),
           DimPlot(o, reduction = rd, group.by = "batch") + ggtitle(rd), width = 6.5, height = 4.5, dpi = 200)
  ggsave("figs/fig4_umap_by_cluster.png",                                    # fig4：按簇上色
         DimPlot(o, group.by = "seurat_clusters", label = TRUE), width = 6.5, height = 4.5, dpi = 200)
  cs <- read.delim(file.path(P, "work/results/cluster_stability.tsv"))       # fig5：别手抄数字
  ggsave("figs/fig5_stability.png",
         ggplot(cs, aes(resolution, n_cluster)) + geom_line() + geom_point(size = 2) +
           scale_y_continuous(breaks = pretty(cs$n_cluster)) + theme_bw(), width = 5, height = 4, dpi = 200)
  sm <- read.delim(file.path(P, "work/results/de/de_comparison_summary.tsv"))  # fig6：两套单位并列
  long <- rbind(data.frame(cell_type = sm$cell_type, method = "FindMarkers (cells)", n = sm$sig_findmarkers),
                data.frame(cell_type = sm$cell_type, method = "pseudobulk (samples)", n = sm$sig_pseudobulk))
  ggsave("figs/fig6_de_comparison.png",
         ggplot(long, aes(cell_type, n, fill = method)) + geom_col(position = "dodge") +
           labs(x = "Cluster", y = "Genes with adjusted p < 0.05", fill = NULL) + theme_bw(), width = 6.5, height = 4.5, dpi = 200)
  ```

  **提示**：R 不展开 shell 变量，`$P02` 只在 shell 里有效——所以上面统一用 `Sys.getenv("P02")`；若它在 R 会话里为空，
  就是当初没 `export P02`（本专题最容易返工的一处）。
- **四个参数必须各有本数据的定量依据**（作业 ③ 第 3 步，占评分 30% 的核心）：`percent.mt`（先画分布再定，并写明 GFF
  核过的基因集）、`--npcs`（看 ElbowPlot 拐点，按本数据图确定）、`--resolution`（**是一个区间不是一个值**）、`min.features`
  （写死在 `CreateSeuratObject` 里，要改就动副本并说明为什么下调或不下调）。
- **评分口径**（作业 ④，满分 100）：完成度与结果正确性 48、方法选择与结果可信度说明 30、AI 使用与验证记录 10、报告质量
  12；`figs/` 六张齐全、UMAP 同时给 batch 与 cluster 两版、`results/` 里的数字能与报告对上。**「AI 使用与验证记录」只考
  可复核性**：提示词原文、模型与日期、AI 给了什么（原样）、哪里错了、你怎么发现的；通篇「AI 输出全部正确」且无验证过程
  的，本栏不得分。
- **截止与迟交**：p02 课后**第 10 天 23:59**；迟交 3 天内按 90%、超 3 天按 70%、超 7 天不计分（截止前可申请一次不扣分
  延期）；允许截止前重复提交，以最后一次为准。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材（概念、失效条件、习题、数字索引） | `textbook/chapters/ch17/manuscript.qmd`：§17.4.1–§17.4.11、§17.5.1–§17.5.4、§17.6、§17.7（博士层 5–10 题）、§17.9 |
| 本专题讲义 | `02_lectures/phd/topic02_scrnaseq_spatial/02_scrnaseq_spatial_lecture.md`：② 前置表、③ 应用案例、④ 4.1–4.11、⑤ 5.0–5.3、⑥ 6.1–6.2、⑦ ⑦-1/⑦-2/⑦-3、⑨ E1–E10、⑩ 练习 |
| 主流程脚本（只读；改参数走个人副本） | `03_code/phd/scripts/02_seurat_pipeline.R`：参数解析（`--indir/--outdir/--mt-pattern/--cp-pattern/--npcs/--resolution/--batch-col/--meta/--step/--singler-ref`）、`res_grid`、`CreateSeuratObject(min.cells=3, min.features=200)`、`PercentageFeatureSet`、全 0 warning、分位数过滤、`SCTransform`/`RunPCA`/`ElbowPlot`、多分辨率 `FindClusters` 与 `cluster_stability.tsv`、`FindAllMarkers`、Harmony 分支与 `integration_before_after.png`、`saveRDS` + `sessionInfo` |
| pseudobulk 脚本 | `02_pseudobulk_de.R`：参数（`--rds/--sample-col/--celltype-col/--condition-col/--min-cells/--outdir`）、列检查、`DefaultAssay <- "RNA"`、簇内细胞门槛、细胞级 `FindMarkers`、按样本求和、可用样本 < 4 跳过、整数断言、`rowSums >= 10`、汇总表 |
| 功效脚本 | `02_power_cells.R`：`prob_ge`（精确二项）、步长 10 的网格、打印 `n_req`、对照表、两条限制、PNG |
| 空间脚本 | `02_spatial_visium.R`：`Load10X_Spatial`（要 `.h5`）、质控（不按 UMI 硬过滤）、`SCTransform(assay="Spatial")`、聚类、`SpatialDimPlot`、`--features` 可选、`spatial_markers.tsv` 与提醒 |
| SGE 入口 | `03_code/phd/scripts/02_run_seurat.sh`：作业头、激活环境、`[host]`、七个变量（`INDIR/OUTDIR/META/MT_PATTERN/CP_PATTERN/NPCS/RESOLUTION/BATCH_COL/VISIUM_DIR`）、快照、四段调用、末尾检查清单 |
| 合成自查演示 | `textbook/demos/ch17_pseudorep_vs_pseudobulk.py`、`ch17_mt_threshold_sensitivity.py`、`ch17_resolution_ari.py`（均带 `--selftest`，在课程仓库根目录运行） |
| 数据说明与下载 | `06_data/phd/README.md` p02 节；`06_data/phd/download_phd.sh --topic p02`；`06_data/phd/manifests/p02_gsm.tsv`；共享只读副本 `<课程数据目录>/phd/p02_scrnaseq_spatial/` |
| 细胞器归属核验 | Ensembl Plants release-59 `Oryza_sativa.IRGSP-1.0.59.gff3.gz`（§1 的 `curl` 与 `awk` 两条命令） |
| 环境定义 / 作业规格 / 前置自测 | `07_envs/conda/env_phd_singlecell.yml`；`08_assessment/phd/assignments/p02_scrnaseq_spatial_practice.md`；`08_assessment/prerequisites/` 下 `l0_01_linux`、`l0_02_r`、`l0_03_conda`、`l0_05_qc`、`l0_06_stats` |
| 上下游衔接 | 上游 p01 的《AI 输出验证清单》在本专题 ⑧ marker 表任务里复用；下游 p03 双 RNA-seq 用本专题的「统计单位」判据 |
