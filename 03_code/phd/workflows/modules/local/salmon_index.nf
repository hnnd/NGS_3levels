// 模块：salmon index。全流程只跑一次——它的输入里没有 meta，因此 DAG 上只有一个节点。

process SALMON_INDEX {
    tag   "salmon_index"
    label 'process_high'

    conda     "bioconda::salmon=1.10.3"
    container "quay.io/biocontainers/salmon:1.10.3--haf24da9_3"

    publishDir "${params.outdir}/index", mode: params.publish_mode

    input:
    path transcriptome

    output:
    path "salmon_index", emit: index
    path "versions.yml", emit: versions

    script:
    """
    salmon index -t ${transcriptome} -i salmon_index \\
        -k ${params.salmon_kmer} -p ${task.cpus}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        salmon: \$(salmon --version 2>&1 | sed 's/^salmon //')
    END_VERSIONS
    """

    stub:
    """
    mkdir -p salmon_index && echo stub > salmon_index/info.json
    echo '"${task.process}": {salmon: stub}' > versions.yml
    """
}
