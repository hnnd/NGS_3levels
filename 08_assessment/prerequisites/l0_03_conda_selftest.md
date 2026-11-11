# L0-3 自测：Conda / Mamba 环境管理

> 对应材料：`02_lectures/prerequisites/l0_03_conda/l0_03_conda.md`
> 契约来源：`00_design/course_contract.yaml` → `prerequisite_packs.selftest_spec`
> **10 题，其中 2 道上机题（Q9、Q10）** ｜ 建议用时 40 分钟（不含建环境的等待时间）

---

## 先把规则说清楚

**一、计分方式：完成即给分，不按对错计。** 这份自测占总成绩 5–10%（本科 10%，硕博各 8%），
只要交齐就是满分。**目的是拿到诊断数据**——教师会在首次课用 15–20 分钟只讲集中出错的那几个点，
不重讲、不补课。按对错计分会让人抄答案，错题分布随之失真，这个闸门就废了。

**二、参考答案直接附在文末（`## 参考答案与评分要点`）。** 既然不按对错计分，抄答案没有任何收益；
公开答案反而让这份自测同时成为学习工具：做完一题就往下翻一次，当场知道自己错在哪，比等一周拿回批改有用得多。
**请先自己做完再翻。**

**三、为什么必须有上机题。** 选择题能猜也能抄，产出不能。Q9 交的 `environment.yml` 与 Q10 的作业脚本片段
**正是你后续课堂第一天就要用的东西**——做完这两题，你已经把第一次实践课的准备工作做完了。

**四、提交物**（三件，缺一不可）：

| 编号 | 提交内容 | 形式 |
|---|---|---|
| ① | 第 1–8 题的作答 | 一个文本文件或文档 |
| ② | **Q9 导出的 `environment.yml` 文件本体** | **文件，不是截图** |
| ③ | Q10 的 SGE 作业脚本片段 | 文本，可与 ① 合并 |

---

## 一、概念题（Q1–Q8）

### Q1 〔检验出口能力：conda 与 mamba 的关系〕
下列关于 conda 与 mamba 的说法，**错误**的是（　）
A. mamba 的命令语法与 conda 基本兼容，多数场景把 `conda` 换成 `mamba` 即可
B. mamba 快，主要是因为求解器用 C++ 重写并且并行下载 channel 索引
C. mamba 使用与 conda 不同的软件源，所以能装到 conda 装不到的包
D. conda 23.10 之后默认求解器换成了 `libmamba`，两者速度差距已明显缩小

### Q2 〔检验出口能力：channel 优先级〕
下面哪一段 `channels` 写法符合本课程与 bioconda 官方的要求？并**用一句话说明写反了会发生什么**。
```
(A) channels: [bioconda, conda-forge, defaults]
(B) channels: [conda-forge, bioconda, defaults]
(C) channels: [defaults, conda-forge, bioconda]
```

### Q3 〔检验出口能力：channel 优先级 / strict 的含义〕
`conda config --set channel_priority strict` 具体改变了求解器的什么行为？它的**代价**是什么？
（2–3 句话）

### Q4 〔检验出口能力：导出与版本锁定〕
你要把环境交给师妹在另一台服务器上重建。下面三条命令你选哪一条，为什么另外两条不合适？
```
(A) conda env export > environment.yml
(B) conda env export --no-builds > environment.yml
(C) conda env export --from-history > environment.yml
```

### Q5 〔检验出口能力：本课程的环境拆分〕
本课程三层共 **16 个**环境，而不是每层一个大环境。请写出**至少两组**真实的依赖互斥组合，
并说明"按任务拆环境"相比"硬解一个大环境"的实际好处。

### Q6 〔检验出口能力：不走 conda 的工具〕
下列工具中，**不应该**写进课程 conda 环境 yml 的有哪些？（多选）并各写一句原因。
A. samtools　B. SignalP　C. GAPIT　D. BUSCO　E. Cytoscape　F. QIIME2　G. Docker　H. ANNOVAR

### Q7 〔检验出口能力：环境出问题时自行定位〕
你在集群上执行 `conda activate ngs_ug_annotation`，得到：
```
EnvironmentNameNotFound: Could not find conda environment: ngs_ug_annotation
```
但 `07_envs/conda/env_ug_annotation.yml` 明明存在，你也确实用它建过环境。原因是什么？怎么查出正确名字？

### Q8 〔检验出口能力：环境出问题时自行定位〕
把下面 4 条报错与它的**首选处理动作**配对（写成 1-x 的形式），并任选**两条**补一句原因：

| 报错 | | 首选动作 |
|---|---|---|
| ① `CommandNotFoundError: Your shell has not been properly configured to use 'conda activate'.` | | (a) `conda clean -a`，并考虑把 `envs_dirs` 迁到 scratch |
| ② `Solving environment: failed with initial frozen solve.` 之后长时间无进展 | | (b) 换到登录节点建环境，或按管理员给的镜像源配 `~/.condarc` |
| ③ `CondaHTTPError: HTTP 000 CONNECTION FAILED for url <https://conda.anaconda.org/bioconda/linux-64/repodata.json>` | | (c) `source /opt/miniconda3/bin/activate` |
| ④ `Disk quota exceeded`（建环境到一半失败） | | (d) 改用 `mamba`，并确认 `channel_priority strict` 与 channel 顺序 |

---

## 二、上机题（Q9、Q10 —— 必做，产出即提交物）

### Q9（上机 ★ 必考题）：建一个环境并导出 `environment.yml`

〔检验出口能力：**能创建、激活、导出、复现一个分析环境**〕

在集群或任一联网 Linux 上完成，**提交导出的 yml 文件本体**：

1. 手写一份 `environment.yml`，环境名 `l0_test`，channels 按正确顺序写全，依赖包含 **`samtools` 与 `bwa`**；
2. 先 `conda env create -f environment.yml --dry-run` 试解，通过后再真正创建；
3. `conda activate l0_test`，用 **`which samtools`** 与 **`conda list bwa`** 验证工具确实来自这个环境
   （把这两条命令的输出粘进作答文件）；
4. `conda env export --no-builds > environment.yml` 覆盖导出，**提交这一份**。

**提交检查表**（自己先对一遍）：
- [ ] yml 里 `name:` 是 `l0_test`
- [ ] `channels` 顺序为 `conda-forge` → `bioconda` → `defaults`
- [ ] `dependencies` 里能找到 `samtools` 和 `bwa`，且**带版本号**（`--no-builds` 导出的结果应形如 `samtools=1.17`）
- [ ] 文件是 `conda env export` 的产物（几十到上百行），**不是**你手写的那 8 行

### Q10（上机 ★ 必做）：写一个能在 SGE 上正确激活环境的作业脚本片段

〔检验出口能力：**在环境出问题时自行定位**——正面对准最高频的那个坑〕

下面这段作业脚本 `qsub` 之后秒退，日志里只有一行 `samtools: command not found`：

```bash
#!/bin/bash
#$ -N my_job
#$ -cwd
conda activate l0_test
samtools --version
```

要求：
1. **一句话说明**它为什么失败（关键词：非交互 shell）；
2. 写出**修正后的完整脚本片段**（含 SGE 头、两行激活、一条自证环境名的 `echo`、一条实际命令）；
3. 说明你**怎么验证**它这次真的对了（写出你会看哪个文件里的哪一行）。

> 有集群账号的同学请实际 `qsub` 一次并把日志内容贴上来；暂时没有账号的，写出脚本与验证方法即可，同样给分。

---

## 参考答案与评分要点

> 再说一次：**不按对错计分**。下面这份答案是给你自查用的——做完对一遍，把不一致的地方标出来，
> 那些就是首次课上会被重点讲的内容。

**Q1** 答案 **C**。mamba 与 conda 用的是**同一批 channel（同样的 anaconda.org 源）**，
包的可得性完全一样；它只是求解与下载更快。A、B、D 均正确。

**Q2** 选 **(B)**。bioconda 的包依赖 conda-forge 编译的底层库，这是 bioconda 官方要求的顺序。
写反（如 A、C）会让 conda 从 `defaults` 取到不兼容的底层库，表现为 **solve 极慢、或装完一跑就崩**。

**Q3** 要点：**strict** 表示一个包只要在**高优先级 channel 里存在**，就**不再考虑**低优先级 channel 的版本
（而非在所有 channel 里挑最高版本）。收益是求解空间大幅缩小、solve 失败率显著下降；
代价是偶尔某个只在低优先级 channel 有较新版本的包会装不上或版本偏旧。

**Q4** 选 **(B) `--no-builds`**。(A) 含 build 号，绑定具体平台与架构，换机器往往解不出来；
(C) `--from-history` 只列你显式装过的包（版本也只保留你当初亲手写下的那部分），**不含传递依赖**，最干净但复现性最弱，适合作为新 yml 的起点而非交付物。
本课程**交作业、写报告附录一律用 (B)**。

**Q5** 三组标准答案（写出任意两组即可）：
① **BUSCO / QUAST vs antiSMASH**——augustus、sepp 与 antiSMASH 的 Python 依赖链版本互斥；
② **QIIME2 vs 其他一切**——官方明确要求独立环境；
③ **GATK4 vs R 栈**——Java 运行时与 `r-base` 依赖纠缠，solve 时间极长。
好处：solve 更容易成功且快得多；一个环境装坏了不影响其他专题；环境小、导出的 yml 也小，更容易复现。

**Q6** 应选 **B、C、E、F、G、H**（A samtools、D BUSCO 是正常的 bioconda 包，该写进 yml）。
原因：SignalP 需 DTU 学术许可单独申请；GAPIT 是 R 包、非 bioconda 渠道；Cytoscape 是桌面 Java 应用；
QIIME2 官方要求独立环境；Docker 是系统级容器运行时需管理员安装；ANNOVAR 需官网注册后下载。
这批工具在契约 `env_exempt_tools` 中已豁免——**找不到它们的 conda 包不是你的错**。

**Q7** 原因：**你把 yml 文件名当成环境名了**。环境名只由 yml 内的 `name:` 字段决定，
`env_ug_annotation.yml` 的 `name:` 是 **`ngs_ug_annot`**——这是本课程一处已知的别扭点。
查法：`conda env list` 看真实名字（`*` 标记当前激活的），或 `grep '^name:' env_ug_annotation.yml`。

**Q8** 配对：**①-(c)　②-(d)　③-(b)　④-(a)**。
① 是 conda 程序找得到但 `conda activate` 这个 **shell 函数**没被定义；
② 是求解器在巨大版本空间里回溯，先换 mamba + strict，仍不行就拆环境；
③ 是网络不通，注意**集群计算节点常常不能直连外网**，应在登录节点建好环境；
④ 是 conda 的 `envs/` 与 `pkgs/` 缓存吃满了家目录配额（一个生信环境几个 GB 很常见）。

**Q9 评分要点**（完成即给分，以下用于自查）：交上来的必须是 **`conda env export --no-builds` 的产物**，
即包含几十到上百行传递依赖、每个包都带版本号；`name: l0_test`；channels 顺序正确；
能在 `dependencies` 里找到 `samtools` 与 `bwa`。若只交了手写的那 8 行 yml，说明第 4 步没做。
`which samtools` 的正确输出形如 `/opt/miniconda3/envs/l0_test/bin/samtools`——**指向 `/usr/bin/` 就是没激活成功**。

**Q10 参考答案**：
1. 失败原因：`qsub` 的作业跑在**非交互 shell** 里，**不读 `.bashrc`**，conda 从未初始化，
   所以 `conda activate` 这个 shell 函数根本不存在（脚本继续往下跑，于是 `samtools` 也找不到）。
   **作业脚本不会继承你登录终端的环境状态**——这是本模块最高频、代价最大的坑。
2. 修正版：
```bash
#!/bin/bash
#$ -N my_job
#$ -cwd
#$ -j y
source /opt/miniconda3/bin/activate    # 【必须】让 conda 命令与 activate 函数存在
conda activate l0_test                 # 【必须】切到目标环境
echo "env=${CONDA_DEFAULT_ENV}"        # 自证：日志里应打印 env=l0_test
which samtools
samtools --version | head -1
```
3. 验证：看提交目录下的 `my_job.o<作业号>`，其中 **`env=` 那一行必须是 `l0_test`**，
   `which samtools` 必须指向 `.../envs/l0_test/bin/samtools`，且有版本号输出。
   若作业状态是 `Eqw`，多为 `#$ -cwd` 指向的提交目录不存在——`Eqw` 不会自愈，须 `qdel` 后改正重提。

---

*自测版本 v1.0 ｜ 依据 contract_version 1.1 ｜ 最后更新 2026-08-29*
