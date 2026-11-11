# m08 最小可重复流程（Snakemake + Quarto）

配套讲义：`02_lectures/master/topic08_workflow_engineering/08_workflow_engineering_lecture.md`

## 这是什么

一条把 **m04 转录组**里手敲过的命令固化下来的最小流程：
`fastp 质控 → salmon 建索引 → salmon 定量 → 合并计数矩阵 → Quarto 报告`。
5 条工作 rule + 1 条 `rule all`，**每条 rule 都带 `log:` 与 `benchmark:`**（项目规范）。

它刻意**只用课程范围内的 Snakemake 特性**：`rule` / `input` / `output` / `params` /
`threads` / `log` / `benchmark` / `shell` / `wildcards` / `rule all` / `expand` /
`configfile` / `conda`。`checkpoint`、动态输出、remote provider、wrapper 一律没有——
那是博士 p07 的内容。

## 怎么跑

```bash
conda activate ngs_ms_workflow

# 0) 没有主线数据时，先造一份微型演示数据（固定随机种子，可重复）
python3 scripts/make_demo_data.py --outdir data

# 1) 空跑：先看它打算做什么，再让它动手
snakemake -n

# 2) 画 DAG
snakemake --dag | dot -Tpng > dag.png

# 3) 真跑（每条 rule 用自己的 envs/*.yaml 建环境）
snakemake --use-conda -c 8

# 4) 断点续跑演示：删掉一个中间结果，看它只重跑受影响的部分
rm -rf results/quant/CK_1 && snakemake --use-conda -c 8 -n
```

## 跑出来是什么

```
results/
├── clean/    {sample}_1.fq.gz / _2.fq.gz     fastp 过滤后的 reads
├── qc/       {sample}.fastp.html / .json     质控报告
├── index/    salmon/                         转录组索引（只建一次）
├── quant/    {sample}/quant.sf               每样本定量
├── counts/   counts_matrix.tsv, tpm_matrix.tsv
└── report/   report.html                     Quarto 报告
logs/         每条 rule 的 stdout+stderr（排错第一现场）
benchmarks/   每条 rule 的耗时与峰值内存（申请资源的依据）
```

`results/` `logs/` `benchmarks/` `.snakemake/` 都可以整个删掉重建，**不要提交进 git**。
入库的是 `Snakefile` / `config.yaml` / `samples.tsv` / `envs/` / `scripts/` / `report/`。

## 换成你自己的数据

只改两个文件，`Snakefile` 一行不动：

1. `samples.tsv` —— 样本名、双端 fastq 路径、分组；
2. `config.yaml` —— 参考转录组路径、线程数、fastp / salmon 参数、报告标题与阈值记录。

## 集群提交

```bash
snakemake --use-conda -j 50 \
  --cluster "qsub -S /bin/bash -cwd -j y -pe smp {threads} -N {rule}_{wildcards}"
```

作业脚本里必须自己激活 conda（SGE 不继承登录 shell 环境），
见讲义 ⑨-4。
