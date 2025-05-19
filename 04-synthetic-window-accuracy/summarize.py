import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import defaultdict

RESULTS_DIR = "results"
PLOT_FILENAME_GE_200K = "plot_median_ws_ge_200k.png" 
PLOT_FILENAME_LE_200K = "plot_median_ws_le_200k.png"
WINDOW_SIZE_THRESHOLD = 200000

TITLE_FONTSIZE = 24
AXIS_LABEL_FONTSIZE = 20
TICK_LABEL_FONTSIZE = 18
LEGEND_FONTSIZE = 14 
LEGEND_TITLE_FONTSIZE = 16 
FIGURE_WIDTH = 14
FIGURE_HEIGHT = 8
MARKER_SIZE = 5


def parse_dir_name(dir_name):
    match = re.fullmatch(r"(\d+)_(\d+)", dir_name)
    if match:
        window_size = int(match.group(1))
        test_run = int(match.group(2))
        return window_size, test_run
    return None, None

def collect_and_calculate_median_pvalues():
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
    
    median_aggregated_data = defaultdict(dict)
    for ws, windows_data in data_by_window_size.items():
        for gw_key, pval_list in windows_data.items():
            if pval_list:
                median_aggregated_data[ws][gw_key] = np.median(pval_list)
            else:
                median_aggregated_data[ws][gw_key] = np.nan
    
    return median_aggregated_data


def create_plot_for_window_range(median_data, output_filename, plot_title_suffix):
    if not median_data:
        print(f"No median data to plot for {plot_title_suffix}.")
        return

    plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT)) 
    ax = plt.gca()
    
    sorted_window_sizes = sorted(median_data.keys())

    lines_plotted = False
    for window_size in sorted_window_sizes:
        windows_map = median_data[window_size]
        if not windows_map:
            print(f"No data for window size {window_size} in {plot_title_suffix} to plot.")
            continue

        plot_data_for_ws = []

        for (chr_name, begin, end), median_adj_pval in windows_map.items():
            midpoint = (begin + end) / 2
            
            if pd.isna(median_adj_pval) or median_adj_pval < 0: 
                 neg_log_p_val = np.nan
            elif median_adj_pval == 0:
                neg_log_p_val = -np.log10(np.finfo(float).tiny) 
            else:
                neg_log_p_val = -np.log10(median_adj_pval)
            
            plot_data_for_ws.append({'midpoint': midpoint, 'neg_log_p_val': neg_log_p_val, 'chr': chr_name})

        if not plot_data_for_ws:
            print(f"No valid plot points for window_size {window_size} in {plot_title_suffix}")
            continue
            
        plot_df = pd.DataFrame(plot_data_for_ws)
        plot_df.sort_values(by=['chr', 'midpoint'], inplace=True)

        unique_chromosomes = plot_df['chr'].unique()
        
        for chrom in unique_chromosomes:
            chrom_df = plot_df[plot_df['chr'] == chrom]
            if chrom_df.empty or chrom_df['neg_log_p_val'].isna().all():
                continue 

            ws_label_short = f"{window_size/1000:.0f}k" if window_size >= 1000 else str(window_size)
            plot_label = f"WS {ws_label_short} - {chrom}"
            ax.plot(chrom_df['midpoint'], chrom_df['neg_log_p_val'], marker='o', linestyle='-', markersize=MARKER_SIZE, alpha=0.7, label=plot_label)
            lines_plotted = True

    if not lines_plotted:
        print(f"No lines were plotted for {plot_title_suffix}. Skipping plot generation.")
        plt.close() 
        return

    p_value_threshold = 0.001
    neg_log_p_threshold = -np.log10(p_value_threshold)
    ax.axhline(y=neg_log_p_threshold, color='red', linestyle='--', linewidth=2, label=f'P-value threshold ({p_value_threshold})')

    ax.set_xlabel("Genomic Window Midpoint", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel("-log10(Median Adjusted P-value)", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_title(f"-log10(P-value) vs. Genomic Position (0-1MB)\n{plot_title_suffix}", fontsize=TITLE_FONTSIZE)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    ax.set_xlim(0, 1000000) 
    
    current_xticks = ax.get_xticks()
    ax.set_xticks(current_xticks) 
    ax.tick_params(axis='x', labelsize=TICK_LABEL_FONTSIZE) 
    ax.tick_params(axis='y', labelsize=TICK_LABEL_FONTSIZE) 
    
    if current_xticks.any():
        ax.set_xticklabels([f'{x/1e3:.0f} kb' for x in current_xticks], fontsize=TICK_LABEL_FONTSIZE)
    else:
        ax.set_xticklabels([])


    handles, labels = ax.get_legend_handles_labels()
    if handles:
        legend = ax.legend(title="Legend", loc='best',
                           borderaxespad=0.5, 
                           fontsize=LEGEND_FONTSIZE)
        plt.setp(legend.get_title(), fontsize=LEGEND_TITLE_FONTSIZE)
    
    plt.tight_layout() 

    try:
        plt.savefig(output_filename, dpi=300)
        print(f"Saved plot: {output_filename}")
    except Exception as e:
        print(f"Error saving plot {output_filename}: {e}")
    plt.close() 

if __name__ == '__main__':
    print("Starting p-value collection and median calculation...")
    median_pvalues_data_all = collect_and_calculate_median_pvalues() 
    
    if median_pvalues_data_all:
        print("Data collection and median calculation complete. Preparing data for plots...")

        data_ge_200k = defaultdict(dict)
        data_le_200k = defaultdict(dict)

        for ws, data in median_pvalues_data_all.items():
            if ws >= WINDOW_SIZE_THRESHOLD:
                data_ge_200k[ws] = data
            if ws <= WINDOW_SIZE_THRESHOLD:
                data_le_200k[ws] = data
        
        if data_ge_200k:
            print(f"Generating plot for window sizes >= {WINDOW_SIZE_THRESHOLD/1000:.0f}kb...")
            create_plot_for_window_range(data_ge_200k, PLOT_FILENAME_GE_200K, f"Window Sizes >= {WINDOW_SIZE_THRESHOLD/1000:.0f}kb")
        else:
            print(f"No data for window sizes >= {WINDOW_SIZE_THRESHOLD/1000:.0f}kb to plot.")

        if data_le_200k:
            print(f"Generating plot for window sizes <= {WINDOW_SIZE_THRESHOLD/1000:.0f}kb...")
            create_plot_for_window_range(data_le_200k, PLOT_FILENAME_LE_200K, f"Window Sizes <= {WINDOW_SIZE_THRESHOLD/1000:.0f}kb")
        else:
            print(f"No data for window sizes <= {WINDOW_SIZE_THRESHOLD/1000:.0f}kb to plot.")
            
        print("Plot generation finished.")
    else:
        print("Failed to collect data. Exiting.")
