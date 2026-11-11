#!/usr/bin/env nextflow
// ============================================
// 文件名称：main.nf
// 功能描述：p07 最小 Nextflow DSL2 流程 —— fastp 质控 → salmon 定量 → 合并计数矩阵
//           它是 03_code/master/pipelines/Snakefile 的等价物，用于范式对照与转换练习
// 作者：王运生
// 日期：2026-08-29
// ============================================
//
// 运行：
//   nextflow run . -stub-run                      # 零依赖空跑，验证 DAG 与 channel 接线
//   nextflow run . -profile conda --transcriptome demo/ref/transcripts.fa
//   nextflow run . -profile singularity,slurm -resume
//
// 设计约束：
//   1. main.nf 只做「编排」——不写任何 shell 命令；命令全在 modules/ 里。
//   2. 任何路径 / 阈值 / 资源都不写死在 .nf 里，全部经 params 从 nextflow.config 进来。
//   3. 每个 process 必须有 stub:，使流程在没装任何生信软件的机器上也能验证接线。

nextflow.enable.dsl = 2

include { QUANTIFY     } from './subworkflows/local/quantify.nf'
include { MERGE_COUNTS } from './modules/local/merge_counts.nf'


def helpMessage() {
    log.info """
    用法：nextflow run . --transcriptome <ref.fa> [--samplesheet <csv>] [-profile conda,slurm]

      --samplesheet    样本清单 CSV，必须含 sample,fq1,fq2,condition 四列
                       （默认：${params.samplesheet}）
      --transcriptome  参考转录组 FASTA（salmon index 的输入，必填）
      --outdir         结果输出目录（默认：${params.outdir}）

    常用 profile：conda / docker / singularity / slurm / sge / test
    常用选项    ：-stub-run（空跑）、-resume（续跑）、-with-dag dag.html
    """.stripIndent()
}


workflow {

    if (params.help) {
        helpMessage()
        exit 0      // 新版 Nextflow（≥26.10）禁止在 workflow 体内 return，用 exit 退出
    }

    // ---- 参数自检：让错误在第 0 秒暴露，而不是在第 3 个 process 里 ----
    if (!params.transcriptome) {
        error "缺少 --transcriptome。这是 salmon index 的输入，没有它整条流程无法起步。"
    }

    // ---- queue channel：N 个样本 → N 个元素，被消费一次即空 ----
    ch_reads = Channel
        .fromPath(params.samplesheet, checkIfExists: true)
        .splitCsv(header: true)
        .map { row ->
            if (!row.sample || !row.fq1 || !row.fq2) {
                error "样本清单缺列：${row}。必须含 sample,fq1,fq2,condition"
            }
            // meta 是「样本的元信息」，随数据一路流下去；
            // Snakemake 用 wildcards 承担同样职责，但 wildcards 只能是字符串，
            // meta 可以是任意 map——这是两种范式在「样本身份」上的第一个分岔。
            def meta = [ id: row.sample, condition: row.condition ]
            tuple( meta, [ file(row.fq1, checkIfExists: true),
                           file(row.fq2, checkIfExists: true) ] )
        }

    // ---- value channel：1 份参考，需要被 N 个样本重复消费 ----
    // Channel.value() 建出来的是 value channel，取之不尽；
    // 若这里误用 Channel.fromPath()，它是 queue channel，只够第 1 个样本用。
    ch_transcriptome = Channel.value( file(params.transcriptome, checkIfExists: true) )

    QUANTIFY( ch_reads, ch_transcriptome )

    // ---- toSortedList：把 N 份 quant.sf 收成 1 个「有序」列表 ----
    // 用 .collect() 也能收拢，但顺序取决于哪个任务先跑完 →
    // 每次运行输入不同 → 任务 hash 不同 → -resume 永远不命中（讲义 ⑨-4）。
    ch_quants = QUANTIFY.out.quant
        .map { meta, quant -> quant }
        .toSortedList { a, b -> a.name <=> b.name }

    MERGE_COUNTS( ch_quants )

    // ---- 版本记录：可重复性的最低要求，必须随结果一起产出 ----
    QUANTIFY.out.versions
        .mix( MERGE_COUNTS.out.versions )
        .map { it.text }        // 取内容而非文件对象，才能按内容去重
        .unique()               // 4 个样本产出 4 份完全相同的 fastp 版本记录，只留 1 份
        .collectFile( name: 'versions.yml', storeDir: "${params.outdir}/pipeline_info",
                      sort: true )

}
