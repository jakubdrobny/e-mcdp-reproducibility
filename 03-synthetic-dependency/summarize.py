import os
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import defaultdict
import numpy as np

RESULTS_DIR = "results"
# Updated output file name to reflect even larger fonts
OUTPUT_FILE = "pvalues_plot_median_threshold_large_font.png"
SIGNIFICANCE_THRESHOLD = 0.001

def collect_pvalues():
    raw_pvalues_by_depfac = defaultdict(lambda: {'chr1': [], 'chr2': []})
    dir_pattern = re.compile(r"depfac(\d+\.?\d*)_(\d+)") 

    if not os.path.exists(RESULTS_DIR):
        print(f"Error: Results directory '{RESULTS_DIR}' not found.")
        return {}, []

    for item_name in os.listdir(RESULTS_DIR):
        item_path = os.path.join(RESULTS_DIR, item_name)
        if not os.path.isdir(item_path):
            continue

        match = dir_pattern.fullmatch(item_name)
        if not match:
            continue
            
        depfac_value_str = match.group(1)
        
        output_file_path = os.path.join(item_path, "output.tsv")
        
        if not os.path.exists(output_file_path):
            print(f"Warning: output.tsv not found in {item_path}")
            continue
            
        try:
            df = pd.read_csv(output_file_path, sep='\t')
            
            if 'chr_name' not in df.columns or 'p-value' not in df.columns:
                print(f"Warning: 'chr_name' or 'p-value' column missing in {output_file_path}")
                continue

            chr1_rows = df[df['chr_name'] == 'chr1']
            chr2_rows = df[df['chr_name'] == 'chr2']
            
            if chr1_rows.empty:
                print(f"Warning: No 'chr1' data found in {output_file_path}")
            else:
                chr1_pval = chr1_rows['p-value'].values[0]
                raw_pvalues_by_depfac[depfac_value_str]['chr1'].append(chr1_pval)
            
            if chr2_rows.empty:
                print(f"Warning: No 'chr2' data found in {output_file_path}")
            else:
                chr2_pval = chr2_rows['p-value'].values[0]
                raw_pvalues_by_depfac[depfac_value_str]['chr2'].append(chr2_pval)
            
        except Exception as e:
            print(f"Error processing {output_file_path}: {str(e)}")
            continue
    
    median_pvalues = {'chr1': [], 'chr2': []}
    unique_depfac_values_str = sorted(raw_pvalues_by_depfac.keys(), key=float)

    if not unique_depfac_values_str:
        print("No valid p-value data collected.")
        return {}, []

    for depfac_str in unique_depfac_values_str:
        chr1_pvals = raw_pvalues_by_depfac[depfac_str]['chr1']
        chr2_pvals = raw_pvalues_by_depfac[depfac_str]['chr2']
        
        if chr1_pvals:
            median_pvalues['chr1'].append(np.median(chr1_pvals))
        else:
            print(f"Warning: No chr1 p-values found for depfac {depfac_str} to calculate median.")
            median_pvalues['chr1'].append(np.nan)

        if chr2_pvals:
            median_pvalues['chr2'].append(np.median(chr2_pvals))
        else:
            print(f"Warning: No chr2 p-values found for depfac {depfac_str} to calculate median.")
            median_pvalues['chr2'].append(np.nan)
            
    return median_pvalues, unique_depfac_values_str

def plot_pvalues(pvalues, dependency_factors_str):
    if not dependency_factors_str or not pvalues['chr1'] or not pvalues['chr2']:
        print("No data to plot.")
        return

    try:
        dependency_factors_numeric = [float(df_str) for df_str in dependency_factors_str]
        x_values = dependency_factors_numeric
        x_ticks_labels = dependency_factors_str
    except ValueError:
        print("Warning: Could not convert all dependency factors to numbers. Using strings for x-axis.")
        x_values = dependency_factors_str
        x_ticks_labels = dependency_factors_str

    # Significantly increased font sizes
    TITLE_FONTSIZE = 24
    AXIS_LABEL_FONTSIZE = 20
    TICK_LABEL_FONTSIZE = 18
    LEGEND_FONTSIZE = 18

    # Increased figure size and marker size
    plt.figure(figsize=(16, 10)) 
    
    plt.plot(x_values, pvalues['chr1'], 
             'o-', label='Chromosome 1 (dependent) - Median p-value', color='#1f77b4', markersize=8) # Larger marker
    
    plt.plot(x_values, pvalues['chr2'], 
             's--', label='Chromosome 2 (independent) - Median p-value', color='#ff7f0e', markersize=8) # Larger marker
    
    plt.axhline(y=SIGNIFICANCE_THRESHOLD, color='red', linestyle='--', 
                label=f'Significance Threshold ({SIGNIFICANCE_THRESHOLD})')
    
    plt.xlabel('Dependency Factor', fontsize=AXIS_LABEL_FONTSIZE)
    plt.ylabel('Median p-value', fontsize=AXIS_LABEL_FONTSIZE)
    plt.title('Median p-values vs Dependency Factor (across tests)', fontsize=TITLE_FONTSIZE)
    
    plt.xticks(ticks=x_values, labels=x_ticks_labels, rotation=45, ha="right", fontsize=TICK_LABEL_FONTSIZE)
    plt.yticks(fontsize=TICK_LABEL_FONTSIZE)
    
    plt.yscale('log')
    
    all_plot_pvals = [p for p in pvalues['chr1'] if not np.isnan(p)] + \
                     [p for p in pvalues['chr2'] if not np.isnan(p)]
    
    if all_plot_pvals: 
        min_data_pval = min((p for p in all_plot_pvals if p > 0), default=SIGNIFICANCE_THRESHOLD) 
        max_data_pval = max(all_plot_pvals, default=SIGNIFICANCE_THRESHOLD)

        current_ymin, current_ymax = plt.ylim()
        final_ymin = min(current_ymin, min_data_pval * 0.5, SIGNIFICANCE_THRESHOLD * 0.5)
        final_ymax = max(current_ymax, max_data_pval * 2, SIGNIFICANCE_THRESHOLD * 2)
        
        if final_ymin <= 0:
            smallest_positive_candidates = [val for val in [min_data_pval, SIGNIFICANCE_THRESHOLD] if val > 0]
            if smallest_positive_candidates:
                smallest_positive = min(smallest_positive_candidates)
                final_ymin = smallest_positive / 10 
            else: 
                final_ymin = 1e-10 
            
        plt.ylim(final_ymin, final_ymax)

    plt.minorticks_off()
    
    plt.grid(True, linestyle=':', alpha=0.7, which='both')
    plt.legend(fontsize=LEGEND_FONTSIZE)
    plt.tight_layout() # This is important for fitting larger labels
    
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Plot saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    pvalues, dependency_factors = collect_pvalues()
   
    if dependency_factors:
        plot_pvalues(pvalues, dependency_factors)
    else:
        print("No dependency factors found or processed. Plot will not be generated.")
