// 模块：salmon quant。逐样本执行——N 个样本 = N 个并发任务，无需写循环。

process SALMON_QUANT {
    tag   "${meta.id}"
    label 'process_medium'

    conda     "bioconda::salmon=1.10.3"
    container "quay.io/biocontainers/salmon:1.10.3--haf24da9_3"

    publishDir "${params.outdir}/quant", mode: params.publish_mode

    input:
    tuple val(meta), path(reads)
    path index                          // 来自 value channel，可被 N 个样本重复消费

    output:
    tuple val(meta), path("${meta.id}.quant.sf"), emit: quant
    path  "${meta.id}",                           emit: dir
    path  "versions.yml",                         emit: versions

    script:
    """
    salmon quant -i ${index} -l ${params.salmon_libtype} \\
        -1 ${reads[0]} -2 ${reads[1]} \\
        -p ${task.cpus} ${params.salmon_extra} \\
        -o ${meta.id}

    # salmon 的输出恒名为 quant.sf；N 个样本同名文件汇到一处会被 Nextflow
    # 自动改名成 quant.sf / quant.2.sf …，样本身份就丢了。这里先带上样本名。
    cp ${meta.id}/quant.sf ${meta.id}.quant.sf

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        salmon: \$(salmon --version 2>&1 | sed 's/^salmon //')
    END_VERSIONS
    """

    stub:
    """
    mkdir -p ${meta.id}
    printf 'Name\\tLength\\tEffectiveLength\\tTPM\\tNumReads\\n' >  ${meta.id}.quant.sf
    printf 'tx0001\\t1500\\t1300.0\\t500000.0\\t120.0\\n'        >> ${meta.id}.quant.sf
    printf 'tx0002\\t1500\\t1300.0\\t500000.0\\t80.0\\n'         >> ${meta.id}.quant.sf
    cp ${meta.id}.quant.sf ${meta.id}/quant.sf
    echo '"${task.process}": {salmon: stub}' > versions.yml
    """
}
