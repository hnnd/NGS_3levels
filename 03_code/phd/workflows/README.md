# p07 配套流程：最小 Nextflow DSL2 流程

> 博士专题 p07《Nextflow / Snakemake 工作流开发》配套代码。
> 讲义：`02_lectures/phd/topic07_workflow_nextflow/07_workflow_nextflow_lecture.md`
> 环境：`conda activate ngs_phd_workflow`（Docker / Singularity 不在其中，见下）

本流程与硕士 `03_code/master/pipelines/Snakefile` **做的是同一件事**（fastp 质控 →
salmon 定量 → 合并计数矩阵），刻意保持功能等价，用于范式对照与 AI 转换核查练习。

## 目录

```
workflows/
├── main.nf                          # 只做编排：建 channel、调子流程，不含任何 shell 命令
├── nextflow.config                  # 全部 params + profiles（conda/docker/singularity/slurm/sge/test）
├── conf/
│   ├── base.config                  # 资源等级（withLabel）与失败重试策略
│   ├── slurm.config                 # SLURM executor
│   ├── sge.config                   # SGE executor
│   └── test.config                  # 课堂用最小配置
├── modules/local/                   # 一个 process 一个文件，可被任意流程 include
│   ├── fastp.nf
│   ├── salmon_index.nf
│   ├── salmon_quant.nf
│   └── merge_counts.nf
├── subworkflows/local/quantify.nf   # 子工作流：质控 + 定量的接线封装
├── bin/merge_quant.py               # bin/ 自动进入每个任务的 PATH，脚本里不写绝对路径
└── assets/samples.csv               # 样本清单：sample,fq1,fq2,condition
```

## 三分钟跑通

```bash
conda activate ngs_phd_workflow

# 1) 造演示数据（固定随机种子，离线可生成；直接复用硕士流程的生成脚本）
python3 ../../master/pipelines/scripts/make_demo_data.py --outdir demo --reads-per-sample 3000

# 2) 空跑：不装任何生信软件也能验证 DAG 与 channel 接线是否正确
nextflow run . -stub-run -profile test

# 3) 真跑（需要 fastp / salmon，由 -profile conda 自动建环境，首次需联网）
nextflow run . -profile test,conda

# 4) 断点续跑：改一个参数或删一个中间结果后再跑，观察哪些任务命中缓存
nextflow run . -profile test,conda -resume

# 5) 集群提交
nextflow run . -profile test,singularity,slurm --queue your_queue -resume
```

`-stub-run` 的期望输出：`completed=10`（4 × FASTP + 1 × SALMON_INDEX + 4 × SALMON_QUANT
+ 1 × MERGE_COUNTS）；紧接着加 `-resume` 再跑一次应为 `cached=10`。
**这两个数字是本流程的验收标准**——对不上说明 channel 接线或缓存有问题。

## 三个必须看懂的设计点

| 位置 | 要点 |
|---|---|
| `main.nf` 的 `Channel.value(...)` | 参考序列必须是 **value channel**，才能被 N 个样本重复消费 |
| `subworkflows/local/quantify.nf` 的 `.first()` | process 输出 channel 的类型继承自输入；`.first()` 是零成本保险 |
| `main.nf` 的 `.toSortedList { }` | 汇总步骤必须**有序**收集，否则 `-resume` 永不命中 |

## 与硕士 Snakemake 版的对照

| 概念 | Snakemake（m08） | Nextflow（本流程） |
|---|---|---|
| 驱动方向 | 从 `rule all` 的目标文件**倒推**（pull） | 从 channel 源头**推动**（push） |
| 样本身份 | `wildcards.sample`（只能是字符串） | `meta` map（可带 condition 等任意字段） |
| 参数外置 | `config.yaml` + `configfile:` | `params` + `nextflow.config` |
| 资源声明 | `threads:` + `--cluster` 模板 | `label` + `conf/base.config` 的 `withLabel` |
| 环境 | `conda:` 指向 `envs/*.yaml` | `conda` 指令 / `container` 指令，由 profile 切换 |
| 缓存 | 文件时间戳 + 元数据 | 任务输入的 **hash** → `work/` 目录 |
| 空跑 | `snakemake -n` | `nextflow run . -stub-run`（真建文件）/ `-preview` |

## 已知约束

- **Docker 与 Singularity/Apptainer 不在 `ngs_phd_workflow` 里**：它们是系统级容器运行时，
  需管理员安装（契约 `env_exempt_tools`）。没有管理员装的机器只能用 `-profile conda`。
- **流程所在路径不能含非 ASCII 字符**：Nextflow 24+ 的解析器会把 `include` 判为
  `Invalid include source`。本仓库路径含中文，因此运行前请把本目录拷到纯英文路径下。
- **`-profile test` 把 `salmon_kmer` 调到 21**：演示转录本较短，默认 31 会让 salmon 报错。
