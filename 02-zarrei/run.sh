#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SCRIPT_DIR}"
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="${BASE_DIR}/results"
EXPERIMENTS_LIST="${BASE_DIR}/experiments_list.tsv"
BINARY_PATH="../../code/bin/e-mcdp"

mkdir -p "${RESULTS_DIR}"

if [[ ! -f "${BINARY_PATH}" ]]; then
    echo "Error: Binary not found at ${BINARY_PATH}"
    exit 1
fi

tail -n +2 "${EXPERIMENTS_LIST}" | while IFS=$'\t' read -r label reference query chr_sizes; do
    ref_file="${DATA_DIR}/${reference}"
    query_file="${DATA_DIR}/${query}"
    chr_sizes_file="${DATA_DIR}/${chr_sizes}"
    output_dir="${RESULTS_DIR}/${label}"
    
    mkdir -p "${output_dir}"
    
    log_file="${output_dir}/log.txt"
    output_file="${output_dir}/output.tsv"
    metrics_file="${output_dir}/metrics.tsv"
    
    echo "Processing ${label}..."
    echo "  Reference: ${ref_file}"
    echo "  Query: ${query_file}"
    echo "  Chr sizes: ${chr_sizes_file}"
    echo "  Output dir: ${output_dir}"

    cmd=(
        "${BINARY_PATH}"
        --r "${ref_file}"
        --q "${query_file}"
        --chs "${chr_sizes_file}"
        --log "${log_file}"
        --o "${output_file}"
        --algorithm slow
        --windows.source dense
        --windows.size 1000000
        --windows.step 100000
    )
        
    echo -e "real_time\tuser_time\tsys_time\tmax_rss\texit_status" > "${metrics_file}"
        
    /usr/bin/time -f "%e\t%U\t%S\t%M\t%x" \
      -o "${metrics_file}" \
      --append \
      "${cmd[@]}" #> /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        echo "  Successfully processed ${label}"
    else
        echo "  Error processing ${label}"
    fi
done

echo "All experiments completed"
