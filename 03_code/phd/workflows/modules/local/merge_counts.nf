// 模块：把 N 份 quant.sf 汇成 counts / TPM 矩阵。
// 脚本放在 bin/ 下——Nextflow 自动把项目根的 bin/ 加进每个任务的 PATH，
// 因此这里直接写 `merge_quant.py`，不写绝对路径（换机器不用改）。

process MERGE_COUNTS {
    tag   "merge_counts"
    label 'process_low'

    conda "conda-forge::python=3.10"

    publishDir "${params.outdir}/counts", mode: params.publish_mode

    input:
    path quants

    output:
    path "counts_matrix.tsv", emit: counts
    path "tpm_matrix.tsv",    emit: tpm
    path "versions.yml",      emit: versions

    script:
    // 样本名由文件名反解，与 quants 的顺序严格对齐——不要另开一条 channel 传样本名，
    // 两条 channel 的顺序不保证一致（讲义 ⑨-3）。
    def names = quants.collect { it.name.replaceAll(/\.quant\.sf$/, '') }.join(' ')
    """
    merge_quant.py \\
        --quant-files ${quants} \\
        --sample-names ${names} \\
        --counts-out counts_matrix.tsv \\
        --tpm-out tpm_matrix.tsv

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python3 --version | sed 's/^Python //')
    END_VERSIONS
    """

    stub:
    // 本步骤只用标准库 Python，没有生信依赖，所以 stub 直接跑真命令：
    // -stub-run 也能产出一个真实的计数矩阵，用于验证下游脚本。
    def names = quants.collect { it.name.replaceAll(/\.quant\.sf$/, '') }.join(' ')
    """
    merge_quant.py \\
        --quant-files ${quants} \\
        --sample-names ${names} \\
        --counts-out counts_matrix.tsv \\
        --tpm-out tpm_matrix.tsv
    echo '"${task.process}": {python: stub}' > versions.yml
    """
}
