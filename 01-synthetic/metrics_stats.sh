#!/bin/bash

# Usage: bash summarize_metrics.sh <input_dir> <output_file>
# Example: bash summarize_metrics.sh mcdp_results metrics/mcdp.tsv

if [ $# -ne 2 ]; then
    echo "Error: Invalid number of arguments"
    echo "Usage: bash $0 <input_directory> <output_file>"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$(dirname $2)"
OUTPUT_FILE="$2"

mkdir -p "${OUTPUT_DIR}"
echo -e "group\ttime_seconds_avg\ttime_seconds_sd\tmem_mb_avg\tmem_mb_sd" > "${OUTPUT_FILE}"

declare -A time_values mem_values group_counts

while IFS= read -d '' -r dir; do
    group=$(basename "$dir" | cut -d'_' -f1)
    
    while IFS= read -d '' -r metrics_file; do
        while IFS=$'\t' read -r real_time _ _ max_rss _; do
            mem_mb=$(echo "scale=4; $max_rss/1024" | bc)
            
            time_values["$group"]+="$real_time "
            mem_values["$group"]+="$mem_mb "
            ((group_counts["$group"]++))
        done < <(tail -n +2 "$metrics_file")
    done < <(find "$dir" -name 'metrics.tsv' -print0)
done < <(find "$INPUT_DIR" -mindepth 1 -maxdepth 1 -type d -print0)

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
