#!/bin/bash

BASE_DIR="."
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="emcdp_results"
GENOME_SIZES="${DATA_DIR}/genomeSize"
BINARY_PATH="../../code/bin/emcdp"

if [ ! -f "$BINARY_PATH" ]; then
  echo "Error: emcdp binary not found at $BINARY_PATH"
  exit 1
fi

#rm -rf "${RESULTS_DIR}"
mkdir -p "${RESULTS_DIR}"

run_testcase() {
    local ref_file="$1"
    local query_file="$2"
    local num_intervals="$3"
    local test_id="$4"

    local output_dir="${RESULTS_DIR}/${num_intervals}_${test_id}"
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
    )

    echo -e "real_time\tuser_time\tsys_time\tmax_rss\texit_status" > "${metrics_file}"

    /usr/bin/time -f "%e\t%U\t%S\t%M\t%x" \
        -o "${metrics_file}" \
        --append \
        "${cmd[@]}" > /dev/null 2>&1

    echo "Processed ${num_intervals}_${test_id}"
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
    query_file="${DATA_DIR}/query_${num_intervals}_${test_id}.bed"

    if [[ ! -f "${query_file}" ]]; then
        echo "Missing query file for ${num_intervals}_${test_id}"
        continue
    fi

    run_testcase "${ref_file}" "${query_file}" "${num_intervals}" "${test_id}"
done

echo "All test cases processed"
