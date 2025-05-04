#!/bin/bash

BASE_DIR="./01-synthetic"
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="01-synthetic/window_benchmark_results"
GENOME_SIZES="${DATA_DIR}/genomeSize"
BINARY_PATH="../code/bin/e-mcdp"

# rm -rf "${RESULTS_DIR}"
mkdir -p "${RESULTS_DIR}"

# ALGORITHMS=("naive" "slow_bad" "slow" "fast_bad" "fast")
ALGORITHMS=("naive" "slow")
STEPS_DIVISORS=(5 10 20)

run_testcase() {
    local ref_file="$1"
    local query_file="$2"
    local num_intervals="$3"
    local test_id="$4"
    local algorithm="$5"
    
    for divisor in "${STEPS_DIVISORS[@]}"; do
        local step_size=$((1000000 / divisor))
        local output_dir="${RESULTS_DIR}/${num_intervals}_${test_id}/${algorithm}_div${divisor}"
        mkdir -p "${output_dir}"
        
        local log_file="${output_dir}/log.txt"
        local output_file="${output_dir}/output.tsv"
        local metrics_file="${output_dir}/metrics.tsv"
        
        local cmd=(
            "${BINARY_PATH}"
            --r "${ref_file}"
            --q "${query_file}"
            --chs "${GENOME_SIZES}"
            --log "${log_file}"
            --o "${output_file}"
            --algorithm "${algorithm}"
            --windows.source dense
            --windows.size 1000000
            --windows.step "${step_size}"
        )
        
        echo -e "real_time\tuser_time\tsys_time\tmax_rss\texit_status" > "${metrics_file}"
        
        /usr/bin/time -f "%e\t%U\t%S\t%M\t%x" \
            -o "${metrics_file}" \
            --append \
            "${cmd[@]}" > /dev/null 2>&1
        
        echo "Processed ${num_intervals}_${test_id} with algorithm ${algorithm} and step divisor ${divisor}"
    done
}

process_test_group() {
    local ref_file="$1"
    local num_intervals="$2"
    local test_id="$3"
    local query_file="${DATA_DIR}/query_${num_intervals}_${test_id}.bed"
  
    if [[ ! -f "${query_file}" ]]; then
        echo "Missing query file for ${num_intervals}_${test_id}"
        return 
    fi
    
    for algorithm in "${ALGORITHMS[@]}"; do
      run_testcase "${ref_file}" "${query_file}" "${num_intervals}" "${test_id}" ${algorithm}
    done
}

find "${DATA_DIR}" -name 'ref_*.bed' | while read -r ref_file; do
    filename=$(basename "${ref_file}")
    [[ $filename =~ ref_([0-9]+)_([0-9]+)\.bed ]] || continue
   
    num_intervals_str="${BASH_REMATCH[1]}"
    test_id_str="${BASH_REMATCH[2]}"
    
    num_intervals_int=$((10#${num_intervals_str}))
    test_id_int=$((10#${test_id_str}))

    printf "%05d\t%05d\t%s\t%s\t%s\n" \
        "${num_intervals_int}" \
        "${test_id_int}" \
        "${num_intervals_str}" \
        "${test_id_str}" \
        "${ref_file}"
done | sort -k1,1n -k2,2n | while IFS=$'\t' read -r _ _ num_intervals test_id ref_file; do
    if [ "$num_intervals" -le 5000 ]; then
      continue 
    fi

    process_test_group "${ref_file}" "${num_intervals}" "${test_id}"
done

echo "All test cases processed"
