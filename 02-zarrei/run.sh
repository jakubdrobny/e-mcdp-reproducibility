#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SCRIPT_DIR}"
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="${BASE_DIR}/results"
EXPERIMENTS_LIST="${BASE_DIR}/experiments_list.tsv"
BINARY_PATH="../../code/bin/emcdp"

mkdir -p "${RESULTS_DIR}"

if [[ ! -f "${BINARY_PATH}" ]]; then
    echo "Error: Binary not found at ${BINARY_PATH}"
    exit 1
fi

SIGNIFICANCE_TYPES=("enrichment" "depletion" "combined")
WINDOW_SIZES=("1000000" "10000000")

tail -n +2 "${EXPERIMENTS_LIST}" | while IFS=$'\t' read -r label reference query chr_sizes; do
    ref_file="${DATA_DIR}/${reference}"
    query_file="${DATA_DIR}/${query}"
    chr_sizes_file="${DATA_DIR}/${chr_sizes}"

    if [[ ! -f "${ref_file}" ]]; then
        echo "Error: Reference file not found: ${ref_file} for label ${label}"
        break 
    fi
    if [[ ! -f "${query_file}" ]]; then
        echo "Error: Query file not found: ${query_file} for label ${label}"
        continue 
    fi
    if [[ ! -f "${chr_sizes_file}" ]]; then
        echo "Error: Chromosome sizes file not found: ${chr_sizes_file} for label ${label}"
        continue
    fi

    for sig_type in "${SIGNIFICANCE_TYPES[@]}"; do
        for ws in "${WINDOW_SIZES[@]}"; do
            output_dir_label="${label}_${sig_type}_ws${ws}"
            output_dir="${RESULTS_DIR}/${output_dir_label}"
    
            mkdir -p "${output_dir}"
    
            log_file="${output_dir}/log.txt"
            output_file="${output_dir}/output.tsv"
            metrics_file="${output_dir}/metrics.tsv"
    
            echo "Processing ${output_dir_label}..."
            echo "  Reference: ${ref_file}"
            echo "  Query: ${query_file}"
            echo "  Chr sizes: ${chr_sizes_file}"
            echo "  Significance: ${sig_type}"
            echo "  Windows size: ${ws}"
            echo "  Output dir: ${output_dir}"

            cmd=(
                "${BINARY_PATH}"
                --r "${ref_file}"
                --q "${query_file}"
                --chs "${chr_sizes_file}"
                --log "${log_file}"
                --o "${output_file}"
                --algorithm slow
                --significance "${sig_type}"
                --windows.source dense
                --windows.size "${ws}"
                --windows.step 100000
            )
        
            echo -e "real_time\tuser_time\tsys_time\tmax_rss\texit_status" > "${metrics_file}"
        
            /usr/bin/time -f "%e\t%U\t%S\t%M\t%x" \
                -o "${metrics_file}" \
                --append \
                "${cmd[@]}" #> /dev/null 2>&1
    
            if [[ $? -eq 0 ]]; then
                echo "  Successfully processed ${output_dir_label}"
            else
                echo "  Error processing ${output_dir_label}"
            fi
        done
    done
done

echo "All experiments completed"
