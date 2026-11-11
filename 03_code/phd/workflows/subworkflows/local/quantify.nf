// 子工作流：质控 + 定量。
// 它把「三个 process 怎么接线」封装成一个可复用单元——
// 别的流程 include { QUANTIFY } 之后，不必知道内部有几个 process。

include { FASTP        } from '../../modules/local/fastp.nf'
include { SALMON_INDEX } from '../../modules/local/salmon_index.nf'
include { SALMON_QUANT } from '../../modules/local/salmon_quant.nf'

workflow QUANTIFY {

    take:
    ch_reads          // queue channel: [ meta, [fq1, fq2] ]，N 个样本
    ch_transcriptome  // value channel : 参考转录组 FASTA，1 份

    main:
    FASTP( ch_reads )
    SALMON_INDEX( ch_transcriptome )

    // ⚠ 全流程最容易写错的一行，AI 做 Snakemake→Nextflow 转换时几乎必错。
    //
    // 规则：process 输出 channel 的类型**继承自输入**。
    //   · 若 ch_transcriptome 是 value channel（main.nf 里就是），
    //     SALMON_INDEX.out.index 也是 value channel，取之不尽，`.first()` 多余——
    //     Nextflow 会打印 "The operator `first` is useless when applied to a value
    //     channel"。**看到这条 WARN 是好事**，说明上游写对了。
    //   · 若有人把它改成 Channel.fromPath()（queue channel），index 就变成只含
    //     1 个元素的 queue channel。Nextflow 按位配对两条输入 channel：第 1 个样本
    //     配走索引后 channel 即空，其余 N-1 个样本永远等不到输入 ——
    //     流程「成功结束」却只产出 1 份 quant.sf，**且不报任何错**。
    //
    // 所以 `.first()` 留着：它是一道成本为零的保险。
    ch_index = SALMON_INDEX.out.index.first()

    SALMON_QUANT( FASTP.out.reads, ch_index )

    emit:
    quant      = SALMON_QUANT.out.quant
    fastp_json = FASTP.out.json
    versions   = FASTP.out.versions
                     .mix( SALMON_INDEX.out.versions )
                     .mix( SALMON_QUANT.out.versions )
}
