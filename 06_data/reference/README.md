# 06_data/reference — 参考基因组、注释与数据库

> 本目录在集群上只放**软链接**与本记录文件；参考序列与数据库本体由集群统一部署在 `/data/db/`（只读）。
> 文档版本：v1.0 ｜ 2026-08-29
> 原则：**只汇总讲义已写明的来源**；新增参考须先在讲义 ⑤/⑪ 写明版本与 URL，再回填本表。

## 一、各讲义用到的参考与数据库

| 使用专题 | 资源 | 版本 / lineage | 来源（讲义已列） | 部署位置 | 讲义出处 |
|----------|------|----------------|------------------|----------|----------|
| u05 | *E. coli* K-12 MG1655 参考基因组 | RefSeq `GCF_000005845.2`（ASM584v2） | `https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/` | 学生自行 `wget -c` 到 scratch | u05 ⑤ 5.1、⑪ |
| u06 / u08 / m02 | BUSCO lineage 库 | `bacteria_odb10`（约 124 个基因） | `busco --download bacteria_odb10 --download_path /data/db/busco_downloads`（登录节点执行；计算节点不通外网） | `/data/db/busco_downloads/` | u06 ⑤、u08 ⑨、m02 ⑨ |
| u08 | RefSeq Mash 库（细菌鉴定，约 6 GB） | 手册 §4.4 所用版本 | 《学生实验操作手册》§4.4 | `/data/lab/ngs/db/` | u08 讲义（Day 2 必须下好） |
| u08 | 参考基因组（建树 / 泛基因组用） | 按学生 Mash / ANI 结果选定，**手册 GCF 编号只是示例** | NCBI genomes FTP | 学生 scratch `genomes/*.fna` | u08 ④、⑨ 9.4 |
| u07 | CheckM 数据库 | `checkm_data_2015_01_16` | `https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz` | `/data/db/checkm/` | u07 ⑨ |
| m03 | SnpEff 自建库 | 由 Xoo 参考 `GCA_024981335`（CIX2779 完成图）FASTA + GFF3 自建（`snpEff build`） | 已定（第 7 轮） | `/data/db/snpeff/` | m03 ⑤ |
| m06 | DADA2 训练集：SILVA（16S）/ UNITE（ITS） | 版本号须写进方法学 | `https://zenodo.org/communities/dada2` ｜ `https://www.arb-silva.de/` ｜ `https://unite.ut.ee/` | `/data/db/dada2/` | m06 ⑤、⑪ |
| m07 | Kraken2 预建库 | `Standard-8`（约 8 GB；完整库 > 100 GB 不用） | `https://benlangmead.github.io/aws-indexes/k2` | `/data/db/kraken2/` | m07 ②「数据库说明」、⑪ |
| m07 | eggNOG-mapper 数据库（约 50 GB） | 与 emapper 版本匹配 | `https://github.com/eggnogdb/eggnog-mapper/wiki` | `/data/db/eggnog/` | m07 ②、⑪ |
| m07 | 宿主基因组 Bowtie2 索引（去宿主） | 水稻 IRGSP-1.0 `GCA_001433935` | 已定（第 7 轮） | `/data/db/host_bt2/` → 本目录软链接 | m07 ② |
| p02 | 单细胞参考（Cell Ranger / Space Ranger 参考包） | 视主线体系（真核）而定 | `https://www.10xgenomics.com/support/software/cell-ranger` ｜ Ensembl Plants / Metazoa | `/data/db/cellranger_ref/` | p02 ⑪ |
| p03 | 宿主 + 病原合并参考（单个 gentrome 索引） | 水稻 IRGSP-1.0（Ensembl Plants）+ 稻瘟菌 70-15（Ensembl Fungi）转录组 + decoy | 已定（第 7 轮）；Salmon decoy-aware 索引 | `/data/db/dual_ref/` | p03 ④、⑤（`STAR --runMode genomeGenerate`） |
| p03 | Pfam（NB-ARC 扫描） | 写明 Pfam 版本 | Pfam 官方（讲义 ⑪ Mistry 2021） | `/data/db/pfam/` | p03 ⑤（`03_effector_screen.sh`） |
| p04 / p05 | p04：稻瘟菌 70-15 参考 + GFF3 ｜ p05：RDP1 自带 MSU6 坐标的 44K 基因型，无需另备参考 | 已定（第 7 轮） | — | — | p04 ⑤ 5.1、p05 ⑤ 5.8 |

> 【2026-08-30 第 7 轮回填】契约 `main_dataset` 三层均已 `determined`，上表原「主线体系待定」各行已按定案填写。
> 各层数据的完整清单、下载命令与预期结果区间见 `06_data/<level>/README.md`；
> 登录号一律先经 `06_data/verify_accessions.sh` 核验并登记于 `06_data/accessions.tsv`。

## 二、软链接约定

```bash
# 在集群上、仓库的 06_data/reference/ 下执行；只建链接，不复制
ln -s /data/db/busco_downloads   busco_downloads
ln -s /data/db/kraken2/Standard-8 kraken2_standard8
ln -s /data/db/eggnog            eggnog
readlink -f kraken2_standard8     # 验证链接目标
```

作业脚本里通过 `06_data/reference/<link>` 或 `${NGS_DB:-/data/db}` 引用，不写死绝对路径。

## 三、哈希与版本记录（必做）

每个参考文件 / 数据库目录到位后，在本目录追加一行到 `REFERENCE_MANIFEST.tsv`（不入 git，随集群部署维护）：

```
sha256_12    file_or_dir    version    source_url    date    recorded_by
```

- 单文件：`sha256sum <file> | cut -c1-12`
- 目录型数据库（Kraken2 / eggNOG / BUSCO）：记录官方发布日期或版本号 + 主索引文件（如 `hash.k2d`）的哈希前 12 位
- 参考基因组同时记录 `samtools faidx` 后的序列条数与总长度，与讲义 / 报告中的数字对照

> 为什么要做：报告方法学里的"参考基因组 GRCh38 release 110"这类信息只有在下载时记下来才是真的；
> 事后回忆的版本号是 p01 讲的"看起来合法的错误"的一种。
