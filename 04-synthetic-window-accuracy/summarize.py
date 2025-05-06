import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import defaultdict

RESULTS_DIR = "results"
COMBINED_PLOT_FILENAME = "plot_all_window_sizes.png"

def parse_dir_name(dir_name):
    match = re.fullmatch(r"(\d+)_(\d+)", dir_name)
    if match:
        window_size = int(match.group(1))
        test_run = int(match.group(2))
        return window_size, test_run
    return None, None

def collect_and_average_pvalues():
    data_by_window_size = defaultdict(lambda: defaultdict(list))

    if not os.path.exists(RESULTS_DIR):
        print(f"Error: Results directory '{RESULTS_DIR}' not found.")
        return None

    for dir_name in os.listdir(RESULTS_DIR):
        dir_path = os.path.join(RESULTS_DIR, dir_name)
        if not os.path.isdir(dir_path):
            continue

        window_size, test_run = parse_dir_name(dir_name)
        if window_size is None:
            continue

        output_tsv_path = os.path.join(dir_path, "output.tsv")
        if not os.path.exists(output_tsv_path):
            print(f"Warning: output.tsv not found in {dir_path}")
            continue

        try:
            df = pd.read_csv(output_tsv_path, sep='\t')
            if 'p-value_adjusted' not in df.columns or \
               'chr_name' not in df.columns or \
               'begin' not in df.columns or \
               'end' not in df.columns:
                print(f"Warning: Required columns missing in {output_tsv_path}")
                continue

            for _, row in df.iterrows():
                genomic_window_key = (row['chr_name'], int(row['begin']), int(row['end']))
                adj_pval = row['p-value_adjusted']
                if pd.notna(adj_pval):
                    data_by_window_size[window_size][genomic_window_key].append(float(adj_pval))
        except Exception as e:
            print(f"Error processing file {output_tsv_path}: {e}")
            continue
    
    averaged_data = defaultdict(dict)
    for ws, windows_data in data_by_window_size.items():
        for gw_key, pval_list in windows_data.items():
            if pval_list:
                averaged_data[ws][gw_key] = np.mean(pval_list)
            else:
                averaged_data[ws][gw_key] = np.nan
    
    return averaged_data


def create_combined_plot(averaged_data):
    if not averaged_data:
        print("No averaged data to plot.")
        return

    plt.figure(figsize=(18, 10)) 
    ax = plt.gca()
    
    sorted_window_sizes = sorted(averaged_data.keys())

    for window_size in sorted_window_sizes:
        windows_map = averaged_data[window_size]
        if not windows_map:
            print(f"No data for window size {window_size} to plot.")
            continue

        plot_data_for_ws = []

        for (chr_name, begin, end), avg_adj_pval in windows_map.items():
            midpoint = (begin + end) / 2
            
            if pd.isna(avg_adj_pval) or avg_adj_pval < 0:
                 neg_log_p_val = np.nan
            elif avg_adj_pval == 0:
                neg_log_p_val = -np.log10(np.finfo(float).tiny) 
            else:
                neg_log_p_val = -np.log10(avg_adj_pval)
            
            plot_data_for_ws.append({'midpoint': midpoint, 'neg_log_p_val': neg_log_p_val, 'chr': chr_name})

        if not plot_data_for_ws:
            print(f"No valid plot points for window_size {window_size}")
            continue
            
        plot_df = pd.DataFrame(plot_data_for_ws)
        plot_df.sort_values(by=['chr', 'midpoint'], inplace=True)

        unique_chromosomes = plot_df['chr'].unique()
        
        for chrom in unique_chromosomes:
            chrom_df = plot_df[plot_df['chr'] == chrom]
            ws_label_short = f"{window_size/1000:.0f}k" if window_size >= 1000 else str(window_size)
            plot_label = f"WS {ws_label_short} - {chrom}"
            ax.plot(chrom_df['midpoint'], chrom_df['neg_log_p_val'], marker='o', linestyle='-', markersize=3, alpha=0.7, label=plot_label)

    p_value_threshold = 0.001
    neg_log_p_threshold = -np.log10(p_value_threshold)
    ax.axhline(y=neg_log_p_threshold, color='red', linestyle='--', linewidth=1.5, label=f'P-value threshold ({p_value_threshold:.0e})')

    ax.set_xlabel("Genomic Window Midpoint", fontsize=12)
    ax.set_ylabel("-log10(Average Adjusted P-value)", fontsize=12)
    ax.set_title("-log10(P-value) vs. Genomic Position (0 - 1MB)", fontsize=14)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    ax.set_xlim(0, 1000000)
    
    current_xticks = ax.get_xticks()
    ax.set_xticks(current_xticks) 
    
    if current_xticks.any():
        ax.set_xticklabels([f'{x/1e3:.0f} kb' for x in current_xticks])
    else:
        ax.set_xticklabels([])


    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(title="Legend", loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0., fontsize='small')
    
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    plot_filepath = COMBINED_PLOT_FILENAME 
    try:
        plt.savefig(plot_filepath, dpi=300)
        print(f"Saved combined plot: {plot_filepath}")
    except Exception as e:
        print(f"Error saving plot {plot_filepath}: {e}")
    plt.close()

if __name__ == '__main__':
    print("Starting p-value collection and averaging...")
    averaged_pvalues_data = collect_and_average_pvalues()
    
    if averaged_pvalues_data:
        print("Data collection complete. Starting combined plot generation...")
        create_combined_plot(averaged_pvalues_data)
        print("Plot generation finished.")
    else:
        print("Failed to collect data. Exiting.")
