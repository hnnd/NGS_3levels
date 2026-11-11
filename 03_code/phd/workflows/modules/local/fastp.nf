// 模块：fastp 质控。一个 process = 一个文件，可被任意流程 include。
// 对照 03_code/master/pipelines/Snakefile 的 `rule fastp`。

process FASTP {
    tag   "${meta.id}"                 // 任务标签：日志与报告里用它区分样本，等价于 Snakemake 的 wildcards 显示
    label 'process_medium'             // 资源等级：具体给多少 CPU/内存由 conf/base.config 决定

    conda     "bioconda::fastp=0.23.4"                          // 换 PATH：宿主文件系统不变
    container "quay.io/biocontainers/fastp:0.23.4--h5f740d0_0"  // 换整个用户态：镜像自带 glibc 与系统库

    publishDir "${params.outdir}/clean", mode: params.publish_mode, pattern: "*.clean.fq.gz"
    publishDir "${params.outdir}/qc",    mode: params.publish_mode, pattern: "*.fastp.{html,json}"

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*.clean.fq.gz"),   emit: reads
    tuple val(meta), path("*.fastp.json"),    emit: json
    path  "*.fastp.html",                     emit: html
    path  "versions.yml",                     emit: versions

    script:
    """
    fastp \\
        -i ${reads[0]} -I ${reads[1]} \\
        -o ${meta.id}_1.clean.fq.gz -O ${meta.id}_2.clean.fq.gz \\
        -h ${meta.id}.fastp.html -j ${meta.id}.fastp.json \\
        -w ${task.cpus} \\
        --qualified_quality_phred ${params.fastp_qual} \\
        --length_required ${params.fastp_minlen} \\
        ${params.fastp_extra}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        fastp: \$(fastp --version 2>&1 | sed 's/^fastp //')
    END_VERSIONS
    """

    stub:
    // stub 的职责只有一个：产出**名字正确**的空文件，让下游 channel 能接上。
    // 它不验证科学正确性，只验证「接线」。
    """
    printf '' | gzip -c > ${meta.id}_1.clean.fq.gz
    printf '' | gzip -c > ${meta.id}_2.clean.fq.gz
    echo '{"summary":{"stub":true}}' > ${meta.id}.fastp.json
    echo '<html>stub</html>'         > ${meta.id}.fastp.html
    echo '"${task.process}": {fastp: stub}' > versions.yml
    """
}
