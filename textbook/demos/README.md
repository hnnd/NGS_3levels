# 合成演示脚本（lab_designer 写，CASE 阶段现跑验收）

命名 `chNN_<主题>.py`（或 `.R`）。规则：numpy/scipy 或 R base；固定随机种子；`--help`；`--selftest` 断言正文引用的关键输出；
文件头写服务的章节与正文引用的输出。合成数据，不得写成真实样本结果。运行：`PYTHONDONTWRITEBYTECODE=1 python3 demos/chNN_x.py --selftest`。
