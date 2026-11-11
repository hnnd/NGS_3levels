#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch11_annotation_bias.py — 两套注释口径对同一批合成基因组造出大批假
「菌株特异基因」的可复现机制演示（合成算例）

服务章节：第 11 章 §11.5 失效条件第 1 条（各基因组注释流程不统一 → 假
「物种特异基因」，泛基因组前必须统一重注释）与 §11.4 比较基因组小节。

数据性质：【合成算例】基因组为固定种子的随机 DNA + 人工植入的已知真基因，
与任何真实菌株无关；不得写成真实样本的实测结果。本课贯穿面板
（Xoo 12 株完成图 + Prokka 统一重注释）的真实核查需在集群进行（unverified）。

模型简化（文件头声明，正文引用时须连带说明）：
  1. 合成注释规则 = 「起始密码子集合 + 最小长度」的 ORF 扫描器，是
     Prodigal/Prokka 参数差异（起始密码子打分、最小基因长度）的**极简替身**——
     真实软件还有密码子使用偏好多项式等编码势模型，本演示刻意不含；
  2. 背景区用 AT 富集的 iid 碱基生成（三个阅读框的终止子密度都 ≈0.10，
     模拟真实基因间隔区不长 ORF 的事实；真实间隔区还有编码势缺失，本演示
     用终止子富集近似）；真基因由无终止子的意义密码子串构成——保证两套
     规则在真基因上行为一致、只在规则参数处分叉；
  3. 菌株间只引入点突变（不模拟 indel/水平转移）；株特异真基因按泊松块植入，
     用来给「真实特异基因」一个已知数量的正对照。

正文引用的输出：
  - 同一祖先基因组、三套合成规则下的预测基因数梯度
  - 12 株合成面板混注注释（11 株规则 P1 + 1 株规则 P2）的每株基因数与
    「菌株特异家族」数——复现 m02 讲义 §⑨-2 的 Statistics_PerSpecies.tsv 形态
  - 特异基因分解：背景噪声 ORF / 真基因·其他株注释漏检（假特异）/
    真实株特异（正对照）——给出假特异的占比

参数含义：
  --genome-size  祖先合成基因组长度（bp）
  --n-genes      植入的真基因数（15% 为 90–300 bp 小基因，模拟 sORF 层）
  --sub-rate     菌株间点突变率（合成）
  --seed         随机种子（固定，保证可复现）
  --selftest     断言上述正文引用数字
"""
import argparse
import sys

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

# 碱基编码 A=0,C=1,G=2,T=3；密码子码 = a*16+b*4+c
STOP_CODES = (3 * 16 + 0 * 4 + 0,   # TAA
              3 * 16 + 0 * 4 + 2,   # TAG
              3 * 16 + 2 * 4 + 0)   # TGA
START_CODES = {"ATG": 0 * 16 + 3 * 4 + 2, "GTG": 2 * 16 + 3 * 4 + 2,
               "TTG": 3 * 16 + 3 * 4 + 2, "ATT": 0 * 16 + 3 * 4 + 3,
               "CTG": 1 * 16 + 3 * 4 + 2}
SENSE_CODONS = [c for c in range(64) if c not in STOP_CODES]

# 三套合成注释规则：(名称, 起始密码子集合, 最小 CDS 长度 bp)
# P1↔P2 的最小长度差（180 vs 90）是真实「标准 vs 宽松」注释口径的替身：
# 宽松口径放行的大量 90–180 bp 短 ORF 正是假特异基因的主要来源。
RULES = {
    "P1_标准": (("ATG", "GTG", "TTG"), 180),
    "P2_宽松": (("ATG", "GTG", "TTG", "ATT", "CTG"), 90),
    "P3_严格": (("ATG",), 300),
    "P0_体检": (("ATG", "GTG", "TTG", "ATT", "CTG"), 90),  # 核酸层面「物理存在」核查
}


def draw_gene_body(rng, length):
    """无终止子的意义密码子串，首密码子固定 ATG（模拟真实起始）。"""
    n_codons = max(1, length // 3)
    codes = np.array(SENSE_CODONS, dtype=np.int64)
    body = codes[rng.integers(0, len(codes), size=n_codons)]
    body[0] = START_CODES["ATG"]
    seq = np.empty(n_codons * 3, dtype=np.int8)
    seq[0::3] = body // 16
    seq[1::3] = (body // 4) % 4
    seq[2::3] = body % 4
    return seq


def stop_codon(rng):
    c = STOP_CODES[rng.integers(0, 3)]
    return np.array([c // 16, (c // 4) % 4, c % 4], dtype=np.int8)


def biased_background(rng, n):
    """基因间隔背景：iid 碱基、AT 富集（P(A)=P(T)=0.34, P(G)=0.2625,
    P(C)=0.0575）——三个阅读框的终止子密度都 ≈0.10（对齐密码子生成的背景
    只有帧 0 达标，偏移帧会被稀释，故用碱基层生成）。AT 富集也符合真实
    基因间隔区的组成偏向。"""
    u = rng.random(n)
    seq = np.empty(n, dtype=np.int8)
    seq[u < 0.34] = 0                                # A
    seq[(u >= 0.34) & (u < 0.68)] = 3                # T
    seq[(u >= 0.68) & (u < 0.9425)] = 2              # G
    seq[u >= 0.9425] = 1                             # C
    return seq


def build_ancestor(rng, genome_size, n_genes):
    """祖先基因组：富含终止子的背景 + 非重叠真基因（± 链）。返回基因组与基因表。"""
    g = biased_background(rng, genome_size)
    genes = []                                       # (gs, ge, strand)
    pos = 2000
    for _ in range(n_genes):
        if rng.random() < 0.15:                      # 15% 小基因（90–300 bp）
            ln = int(rng.integers(90, 301))
        else:
            ln = int(np.clip(rng.lognormal(np.log(650), 0.45), 150, 2200))
        pos += int(rng.integers(80, 900))            # 基因间隔
        if pos + ln + 3 >= genome_size:
            break
        strand = "+" if rng.random() < 0.5 else "-"
        body = draw_gene_body(rng, ln)
        if strand == "+":
            g[pos:pos + len(body)] = body
            g[pos + len(body):pos + len(body) + 3] = stop_codon(rng)
            genes.append((pos, pos + len(body), strand))
        else:
            g[pos:pos + len(body)] = (3 - body[::-1])
            g[pos - 3:pos] = stop_codon(rng)
            genes.append((pos, pos + len(body), strand))
        pos += len(body) + 3
    return g, genes


def make_strain(rng, ancestor, n_genes, sub_rate, lam_unique=6.0):
    """祖先 + 点突变 + 株特异真基因块。返回 (基因组, 株特异基因表[(gs,ge,strand,fam)])。"""
    g = ancestor.copy()
    m = rng.random(g.shape) < sub_rate
    g[m] = (g[m] + rng.integers(1, 4, int(m.sum()))) % 4
    blocks, fam = [], n_genes
    tail = g
    for _ in range(int(rng.poisson(lam_unique))):
        body = draw_gene_body(rng, int(rng.integers(90, 1200)))
        gap = biased_background(rng, 100)
        start = len(tail) + len(gap)                # 间隔背景
        tail = np.concatenate([tail, gap, body, stop_codon(rng)])
        blocks.append((start, start + len(body), "+", fam))
        fam += 1
    return tail, blocks


class OrfIndex:
    """预计算每个基因组的密码子码表与分阅读框终止位点，供多套规则复用。"""

    def __init__(self, genome):
        self.L = len(genome)
        self.codes = {}
        for strand, arr in (("+", genome), ("-", (3 - genome[::-1]))):
            w = sliding_window_view(arr, 3)
            codes = (w[:, 0].astype(np.int16) * 16
                     + w[:, 1].astype(np.int16) * 4 + w[:, 2].astype(np.int16))
            frames = np.arange(len(codes)) % 3
            stops = {f: np.where(np.isin(codes, STOP_CODES) & (frames == f))[0]
                     for f in range(3)}
            self.codes[strand] = (codes, frames, stops)

    def predict(self, rule_name):
        """按规则返回预测 CDS 区间数组 (gs, ge, strand)；ge 不含终止子。"""
        start_codes, min_len = RULES[rule_name]
        sc = np.array([START_CODES[s] for s in start_codes], dtype=np.int16)
        out = []
        for strand in ("+", "-"):
            codes, frames, stops = self.codes[strand]
            smask = np.isin(codes, sc)
            gs_list, ge_list = [], []
            for f in range(3):
                stop_pos = stops[f]
                sp_all = np.where(smask & (frames == f))[0]
                idx = np.searchsorted(stop_pos, sp_all, side="right")
                ok = idx < len(stop_pos)
                sp, ep = sp_all[ok], stop_pos[idx[ok]]
                keep = (ep - sp) >= min_len
                sp, ep = sp[keep], ep[keep]
                order = np.lexsort((sp, ep))       # 同一终止子取最长（起点最靠前）
                sp, ep = sp[order], ep[order]
                _, first = np.unique(ep, return_index=True)
                gs_list.append(sp[first])
                ge_list.append(ep[first])
            gs = np.concatenate(gs_list)
            ge = np.concatenate(ge_list)
            if strand == "+":
                out.append(np.stack([gs, ge, np.full(len(gs), 1)], axis=1))
            else:
                out.append(np.stack([self.L - ge - 3, self.L - gs,
                                     np.full(len(gs), -1)], axis=1))
        return np.vstack(out).astype(np.int64)


def map_to_families(preds, genes, blocks):
    """把预测映射到真基因家族：同链、覆盖 ≥60% 预测长度。返回 (家族集合, 背景噪声数)。"""
    g_arr = np.array([(s, e, 1 if st == "+" else -1) for s, e, st in genes],
                     dtype=np.int64)
    starts = g_arr[:, 0]
    order = np.argsort(starts)
    fams = set()
    n_noise = 0
    ps, pe, pst = preds[:, 0], preds[:, 1], preds[:, 2]
    idx = np.searchsorted(starts[order], ps, side="right") - 1
    for i in range(len(preds)):
        hit = False
        if idx[i] >= 0:
            gi = order[idx[i]]
            gs, ge, gst = g_arr[gi]
            if gst == pst[i]:
                ov = min(pe[i], ge) - max(ps[i], gs)
                if ov >= 0.6 * (pe[i] - ps[i]):
                    fams.add(gi)
                    hit = True
        if not hit:
            for bs, be, bst, bfam in blocks:
                if bst == "+" and min(pe[i], be) - max(ps[i], bs) >= 0.6 * (pe[i] - ps[i]):
                    fams.add(bfam)
                    hit = True
                    break
        if not hit:
            n_noise += 1
    return fams, n_noise


def run_panel(seed=20261104, genome_size=900_000, n_genes=800, sub_rate=0.002,
              verbose=True):
    rng = np.random.default_rng(seed)
    anc, genes = build_ancestor(rng, genome_size, n_genes)
    idx_anc = OrfIndex(anc)

    if verbose:
        print("=== 单基因组 × 三套合成注释规则（同一祖先，合成算例）===")
        counts = {}
        for name in ("P1_标准", "P2_宽松", "P3_严格"):
            pr = idx_anc.predict(name)
            counts[name] = len(pr)
            lens = pr[:, 1] - pr[:, 0]
            print(f"  [{name}] 预测基因 {len(pr):5d} 条；长度中位数 "
                  f"{int(np.median(lens)):4d} bp，最短 {int(lens.min()):3d} bp")
        p1 = idx_anc.predict("P1_标准")
        p2 = idx_anc.predict("P2_宽松")
        p2_lens = p2[:, 1] - p2[:, 0]
        p1_keys = set(map(tuple, p1[:, :2]))
        p2_only = [i for i in range(len(p2))
                   if tuple(p2[i, :2]) not in p1_keys]
        thr = RULES["P1_标准"][1]
        print(f"  [P2−P1] P2 多出 {len(p2_only)} 条；其中长度 <{thr} bp 的 "
              f"{int((p2_lens[p2_only] < thr).sum())} 条（最小长度规则直接放行）"
              f"，中位长度 {int(np.median(p2_lens[p2_only]))} bp")

    strains, strain_blocks = [], []
    for _ in range(12):
        g, bl = make_strain(rng, anc, len(genes), sub_rate)
        strains.append(OrfIndex(g))
        strain_blocks.append(bl)

    def annotate(j, rule):
        pr = strains[j].predict(rule)
        return map_to_families(pr, genes, strain_blocks[j]) + (pr,)

    # 统一面板：12 株全部 P1
    uni_fams, uni_noise, uni_preds = [], [], []
    for j in range(12):
        f, n, pr = annotate(j, "P1_标准")
        uni_fams.append(f)
        uni_noise.append(n)
        uni_preds.append(pr)
    # 混合面板：11 株 P1 + 第 12 株 P2（模拟「混入一套别的注释流程」）
    mix_fams, mix_noise, mix_preds = [], [], []
    for j in range(11):
        mix_fams.append(uni_fams[j])
        mix_noise.append(uni_noise[j])
        mix_preds.append(uni_preds[j])
    f, n, pr = annotate(11, "P2_宽松")
    mix_fams.append(f)
    mix_noise.append(n)
    mix_preds.append(pr)

    # 核酸层面「物理存在」体检：P0 宽松规则在每株上的家族覆盖
    relaxed = []
    for j in range(12):
        pr0 = strains[j].predict("P0_体检")
        f0, _ = map_to_families(pr0, genes, strain_blocks[j])
        relaxed.append(f0)

    def specific_counts(fams, noises):
        """菌株特异家族 = 真基因家族仅本株有 + 背景噪声 ORF（各自成单例家族，
        与 OrthoFinder 把未分配基因记为 species-specific orthogroups 同理）。"""
        out = []
        for j in range(12):
            others = set().union(*[fams[k] for k in range(12) if k != j])
            out.append(len(fams[j] - others) + noises[j])
        return out

    uni_spec = specific_counts(uni_fams, uni_noise)
    mix_spec = specific_counts(mix_fams, mix_noise)

    if verbose:
        print("\n=== 12 株面板：统一注释（全 P1）===")
        print("  Number of genes                     "
              + "  ".join(f"{len(p):5d}" for p in uni_preds))
        print("  Number of strain-specific families  "
              + "  ".join(f"{s:5d}" for s in uni_spec))
        print("  （特异家族 ≈ 背景噪声 ORF + 株特异真基因正对照）")
        print("\n=== 12 株面板：混入 1 株 P2（第 12 株）===")
        print("  Number of genes                     "
              + "  ".join(f"{len(p):5d}" for p in mix_preds))
        print("  Number of strain-specific families  "
              + "  ".join(f"{s:5d}" for s in mix_spec))
        # 第 12 株特异家族的三分类
        others = set().union(*[mix_fams[k] for k in range(11)])
        spec12 = mix_fams[11] - others
        n_noise12 = mix_noise[11]
        n_miss, n_real = 0, 0
        for fam in spec12:
            if fam >= len(genes):
                n_real += 1                       # 株特异真基因（植入正对照）
                continue
            present = sum(1 for k in range(11) if fam in relaxed[k])
            if present >= 11:
                n_miss += 1                       # 其他株基因组里物理存在、P1 漏检
            else:
                n_real += 1
        print(f"\n  第 12 株特异家族 {len(spec12) + n_noise12} 的分解：")
        print(f"    背景噪声 ORF（不映射任何真基因）          {n_noise12:5d}")
        print(f"    真基因·其余 11 株物理存在但 P1 漏检       {n_miss:5d}"
              f"  ← 假『菌株特异基因』主体")
        print(f"    真实株特异（株特异植入 + 真实缺失）       {n_real:5d}")
        tot = len(spec12) + n_noise12
        print(f"    假特异占比：{(n_noise12 + n_miss) / tot:.1%}")
    return dict(counts=counts if verbose else None,
                uni_genes=[len(p) for p in uni_preds],
                uni_spec=uni_spec, mix_genes=[len(p) for p in mix_preds],
                mix_spec=mix_spec, n_noise12=n_noise12, n_miss=n_miss,
                n_real=n_real)


def selftest():
    """固定种子复现正文引用的关键数字。"""
    print("=== SELFTEST（合成算例，固定种子 20261104）===")
    r = run_panel(seed=20261104)
    c = r["counts"]
    assert c["P2_宽松"] > c["P1_标准"] > c["P3_严格"], \
        f"三套规则应形成基因数梯度：{c}"
    assert max(r["uni_spec"]) <= 1.8 * (sum(r["uni_spec"]) / 12), \
        f"统一面板各株特异数应相近：{r['uni_spec']}"
    assert r["mix_spec"][11] >= 4 * max(r["uni_spec"]), \
        f"混入 P2 后第 12 株特异数应暴涨：{r['mix_spec'][11]} vs {r['uni_spec']}"
    tot = r["mix_spec"][11]
    assert (r["n_noise12"] + r["n_miss"]) / tot >= 0.90, \
        f"假特异占比应 ≥90%，得 {(r['n_noise12'] + r['n_miss']) / tot:.1%}"
    assert 1 <= r["n_real"] <= 40, \
        f"真实株特异应只有植入正对照量级（≈6/株），得 {r['n_real']}"
    print("SELFTEST PASS：规则梯度、统一面板特异数相近、混入 1 株宽松规则后"
          "特异数暴涨且 ≥90% 为假特异（背景噪声 ORF + 真基因漏检）均复现")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="两套合成注释规则造出假『菌株特异基因』的机制演示"
                    "（合成算例，非真实样本结果）")
    ap.add_argument("--genome-size", type=int, default=900_000)
    ap.add_argument("--n-genes", type=int, default=800)
    ap.add_argument("--sub-rate", type=float, default=0.002)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    run_panel(seed=args.seed, genome_size=args.genome_size,
              n_genes=args.n_genes, sub_rate=args.sub_rate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
