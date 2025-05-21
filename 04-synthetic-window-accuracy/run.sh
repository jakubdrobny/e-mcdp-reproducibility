#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SCRIPT_DIR}"
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="${BASE_DIR}/results"
BINARY_PATH="../../code/bin/emcdp"
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

window_sizes=(800000 600000 400000 200000 100000 80000 60000 40000 20000 10000)

for label in "${window_sizes[@]}"; do
    for test_run in {1..10}
    do
        output_dir="${RESULTS_DIR}/${label}_${test_run}"
        mkdir -p "${output_dir}"

        log_file="${output_dir}/log.txt"
        output_file="${output_dir}/output.tsv"
        metrics_file="${output_dir}/metrics.tsv"

        ref_file="${DATA_DIR}/ref_${test_run}.bed"
        query_file="${DATA_DIR}/query_${test_run}.bed"

        echo "Processing ${label}_${test_run}..."
        echo "  Reference: ${ref_file}"
        echo "  Query: ${query_file}"
        echo "  Chr sizes: ${chr_sizes_file}"
        echo "  Output dir: ${output_dir}"

        # step_size=$((label / 10))
        step_size=$(( label / 10 > 5000 ? 5000 : label / 10))

        cmd=(
            "${BINARY_PATH}"
            --r "${ref_file}"
            --q "${query_file}"
            --chs "${chr_sizes_file}"
            --log "${log_file}"
            --o "${output_file}"
            --algorithm slow
            --windows.source dense
            --windows.size "${label}"
            --windows.step "${step_size}"
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
done
