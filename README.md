# 高通量测序技术与数据分析（三层次课程材料）

面向本科生、硕士生、博士生的三层次课程：讲义、幻灯片、上机实验指导、分析脚本、conda 环境与考核材料。
所有实践数据都是公共数据库的公开数据（ENA / SRA / MetaboLights 等），登录号见 `06_data/accessions.tsv`，
校外读者也可以照着自学。

| 层次 | 专题 |
|---|---|
| 本科（u01–u08） | Linux 与 conda、R 可视化、测序原理与格式、质控与预处理、比对与 BAM、组装基础、注释与 IGV、综合项目 |
| 硕士（m01–m08） | 测序原理与实验设计、组装与泛基因组、重测序、转录组、调控组、扩增子、宏基因组、工作流工程 |
| 博士（p01–p08） | AI 辅助工作流、单细胞与空间、宿主–病原、群体遗传、GWAS、多组学、Nextflow 工作流、课题设计 |

## 目录

```
02_lectures/      讲义（每专题一个目录）
03_code/          分析脚本（按层次分 undergraduate / master / phd）
04_slides/        Marp 幻灯片源文件；figsrc/ 是配图的生成脚本，master/narration/ 是硕士幻灯片逐页旁白
06_data/          数据下载与登录号核验脚本、数据说明（不含数据本身）
07_envs/          conda 环境定义（yml）
08_assessment/    前置自测、作业与项目规格（参考答案按课程设计公开）
11_lab_guides/    上机实验指导（每专题一份；master/dist/ 有 m01 的 HTML/PDF 版）
textbook/demos/   教材配套的合成算例脚本（固定随机种子，带 --selftest）
```

## 怎么用

- **上机**：打开对应专题的 `11_lab_guides/<层次>/<专题>_lab.md`，每一步都写了命令、检查点和出错信号。
- **环境**：`conda env create -f 07_envs/conda/<env>.yml`；环境名以 yml 里的 `name:` 为准。
- **数据**：`06_data/<层次>/download_*.sh` 从公共库下载，下载后按指导里的 MD5 与 read 数验收。
- **幻灯片**：用 [Marp](https://marp.app/) 渲染，主题在 `04_slides/themes/ngs.css`，
  如 `marp --no-stdin --theme-set 04_slides/themes -- 04_slides/master/01_ngs_design_slides.md`。

## 说明

- 指导与脚本里的 `/d3/lab/...`、`/d3/scratch/...` 和 `qsub` 是**课程集群（SGE）**的路径与用法，
  校内上课以课堂公布为准；在自己的机器上运行时，把这些路径换成本地目录、把 `qsub` 换成直接 `bash`。
  `<课程仓库路径>`、`<课程数据目录>` 是占位符，填你本地的对应目录。
- 部分讲义、实验指导会引用课程教材（`textbook/chapters/...`），教材尚未公开，这类链接暂时无法打开。
- 博士层 p06、p08 的实验指导和部分幻灯片仍在修订，会陆续更新。

## 更新方式（维护者）

本仓库是课程主仓库公开部分的导出快照，由主仓库的 `10_platform/export_public.sh` 生成；
请在主仓库修改后重新导出，不要直接在这里改。
