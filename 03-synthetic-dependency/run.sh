#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SCRIPT_DIR}"
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="${BASE_DIR}/results"
BINARY_PATH="../../code/bin/e-mcdp"
CHR_SIZES_BASENAME="chr_sizes.txt" 

mkdir -p "${RESULTS_DIR}"

if [[ ! -f "${BINARY_PATH}" ]]; then
    echo "Error: Binary not found at ${BINARY_PATH}"
    exit 1
fi

if [[ ! -d "${DATA_DIR}" ]]; then
    echo "Error: Data directory not found at ${DATA_DIR}"
    exit 1
fi

chr_sizes_file="${DATA_DIR}/${CHR_SIZES_BASENAME}"
if [[ ! -f "${chr_sizes_file}" ]]; then
    echo "Error: Chromosome sizes file not found: ${chr_sizes_file}"
    exit 1
fi

echo "Scanning for reference files in ${DATA_DIR} matching ref_depfac*_test*.bed..."

found_any_ref_files=false
for ref_file_full_path in "${DATA_DIR}"/ref_depfac*_*.bed; do
    if [[ ! -f "${ref_file_full_path}" ]]; then
        if ! ${found_any_ref_files}; then 
           echo "No reference files matching 'ref_depfac*_*.bed' found in ${DATA_DIR}."
        fi
        break
    fi
    found_any_ref_files=true

    ref_filename=$(basename "${ref_file_full_path}")

    if [[ "${ref_filename}" =~ ref_(depfac[0-9]+\.?[0-9]*)_([0-9]+)\.bed ]]; then
        depfac_part="${BASH_REMATCH[1]}"
        testid_part="${BASH_REMATCH[2]}"
        label="${depfac_part}_${testid_part}"
    else
        echo "  Warning: Filename ${ref_filename} does not match expected pattern ref_depfacX_testY.bed. Skipping."
        continue
    fi

    query_filename="${ref_filename/ref_/query_}"
    query_file_full_path="${DATA_DIR}/${query_filename}"

    output_dir="${RESULTS_DIR}/${label}"
    mkdir -p "${output_dir}"

    log_file="${output_dir}/log.txt"
    output_file="${output_dir}/output.tsv"
    metrics_file="${output_dir}/metrics.tsv"

    echo "Processing ${label}..."
    echo "  Reference: ${ref_file_full_path}"
    echo "  Query: ${query_file_full_path}"
    echo "  Chr sizes: ${chr_sizes_file}"
    echo "  Output dir: ${output_dir}"

    if [[ ! -f "${query_file_full_path}" ]]; then
        echo "  Error: Query file not found: ${query_file_full_path}"
        continue
    fi

    cmd=(
        "${BINARY_PATH}"
        --r "${ref_file_full_path}"
        --q "${query_file_full_path}"
        --chs "${chr_sizes_file}"
        --log "${log_file}"
        --o "${output_file}"
        --algorithm slow
        --windows.source basic
        --windows.size 1000000
    )

    echo -e "real_time\tuser_time\tsys_time\tmax_rss\texit_status" > "${metrics_file}"

    ( /usr/bin/time -f "%e\t%U\t%S\t%M\t%x" \
      -o "${metrics_file}" \
      --append \
      "${cmd[@]}" > /dev/null 2>&1 )

    sleep 0.1
    if [[ ! -s "${metrics_file}" ]]; then
        echo "  Error: Metrics file ${metrics_file} is empty or not created. Command likely failed pre-execution."
        echo "  Command was: ${cmd[@]}"
        continue
    fi
    
    actual_command_exit_status=$(tail -n 1 "${metrics_file}" | awk -F'\t' '{print $NF}')

    if [[ "${actual_command_exit_status}" -eq 0 ]]; then
        echo "  Successfully processed ${label}"
    else
        echo "  Error processing ${label} (Exit status: ${actual_command_exit_status})"
        if [[ -f "${log_file}" ]]; then
            echo "  Last 5 lines of log:"
            tail -n 5 "${log_file}" | sed 's/^/    /'
        else
            echo "  Log file ${log_file} not found."
        fi
        echo "  Metrics from ${metrics_file}:"
        tail -n 1 "${metrics_file}" | sed 's/^/    /'
    fi
done

if ! ${found_any_ref_files}; then
    echo "No experiments were processed as no matching reference files were found."
else
    echo "All experiments completed."
fi
