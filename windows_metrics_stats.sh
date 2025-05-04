#!/bin/bash

# Usage: bash summarize_metrics.sh <input_dir> <output_dir>
# Example: bash summarize_metrics.sh 01-synthetic/window_benchmark_results 01-synthetic/window_benchmark_metrics

if [ $# -ne 2 ]; then
    echo "Error: Invalid number of arguments"
    echo "Usage: bash $0 <input_directory> <output_dir>"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"

rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

declare -A processed_combinations

while IFS= read -d '' -r method_dir; do
    dir_name=$(basename "$method_dir")
    method=$(echo "$dir_name" | sed 's/_div[0-9]\+$//')
    divisor=$(echo "$dir_name" | grep -oP '(?<=_div)\d+$')
    combination="${method}_div${divisor}"

    if [[ -n "${processed_combinations[$combination]}" ]]; then
        continue
    fi
    processed_combinations[$combination]=1

    OUTPUT_FILE="${OUTPUT_DIR}/${method}_div${divisor}.tsv"
    echo -e "group\ttime_seconds_avg\ttime_seconds_sd\tmem_mb_avg\tmem_mb_sd" > "${OUTPUT_FILE}"
    
    declare -A time_values mem_values group_counts

    while IFS= read -d '' -r metrics_file; do
        group=$(echo "$metrics_file" | awk -F'/' '{print $(NF-2)}' | cut -d'_' -f1)
        
        while IFS=$'\t' read -r real_time _ _ max_rss _; do
            mem_mb=$(echo "scale=4; $max_rss/1024" | bc)
            
            time_values["$group"]+="$real_time "
            mem_values["$group"]+="$mem_mb "
            ((group_counts["$group"]++))
        done < <(tail -n +2 "$metrics_file")
    done < <(find "$INPUT_DIR" -path "*/${dir_name}/metrics.tsv" -print0)

    export LC_NUMERIC=C

    sorted_groups=($(
        for group in "${!group_counts[@]}"; do 
            echo "$group"
        done | sort -n
    ))

    for group in "${sorted_groups[@]}"; do
        read -ra times <<< "${time_values[$group]}"
        read -ra mems <<< "${mem_values[$group]}"
        n=${group_counts[$group]}
        
        time_sum=0
        mem_sum=0
        for ((i=0; i<n; i++)); do
            time_sum=$(echo "$time_sum + ${times[i]}" | bc)
            mem_sum=$(echo "$mem_sum + ${mems[i]}" | bc)
        done
        time_mean=$(echo "scale=4; $time_sum / $n" | bc)
        mem_mean=$(echo "scale=4; $mem_sum / $n" | bc)
       
        time_var=0
        mem_var=0
        for ((i=0; i<n; i++)); do
            time_diff=$(echo "${times[i]} - $time_mean" | bc)
            mem_diff=$(echo "${mems[i]} - $mem_mean" | bc)
            time_var=$(echo "$time_var + ($time_diff)^2" | bc)
            mem_var=$(echo "$mem_var + ($mem_diff)^2" | bc)
        done
        time_var=$(echo "scale=4; $time_var / $n" | bc)
        mem_var=$(echo "scale=4; $mem_var / $n" | bc)
        
        time_sd=$(echo "sqrt($time_var)" | bc -l)
        mem_sd=$(echo "sqrt($mem_var)" | bc -l)

        printf "%s\t%.4f\t%.4f\t%.4f\t%.4f\n" \
            "$group" "$time_mean" "$time_sd" "$mem_mean" "$mem_sd" >> "$OUTPUT_FILE"
    done

    echo "Metrics summary saved to $OUTPUT_FILE"
    
    unset time_values mem_values group_counts
done < <(find "$INPUT_DIR" -mindepth 2 -maxdepth 2 -type d -name "*_div*" -print0 | sort -z)

echo "All metrics summaries completed"
