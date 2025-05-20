import os
import re
import pandas as pd
import numpy as np

RESULTS_DIR = "results"
OUTPUT_FILENAME = "table_summary_data.tsv"
SIGNIFICANCE_THRESHOLD = 0.01

DIR_NAME_PATTERN = re.compile(r"(.+?)!inclusive\.loss_(enrichment|depletion|combined)_ws(\d+)")

def main():
    summary_data = []

    if not os.path.isdir(RESULTS_DIR):
        print(f"Error: Results directory '{RESULTS_DIR}' not found.")
        return

    print(f"Processing directories in: {RESULTS_DIR}")
    for dir_name in sorted(os.listdir(RESULTS_DIR)):
        dir_path = os.path.join(RESULTS_DIR, dir_name)

        if not os.path.isdir(dir_path):
            continue

        match = DIR_NAME_PATTERN.fullmatch(dir_name)
        if not match:
            continue

        annotation_type = match.group(1)
        test_type = match.group(2)
        window_size = int(match.group(3))

        if window_size != 1_000_000 or test_type == 'combined':
            continue

        print(f"  Processing: {dir_name} (Annotation: {annotation_type}, Test: {test_type}, WS: {window_size})")

        output_tsv_path = os.path.join(dir_path, "output.tsv")
        metrics_tsv_path = os.path.join(dir_path, "metrics.tsv")

        if not os.path.exists(output_tsv_path):
            print(f"    Warning: 'output.tsv' not found in {dir_path}. Skipping this entry.")
            continue
        if not os.path.exists(metrics_tsv_path):
            print(f"    Warning: 'metrics.tsv' not found in {dir_path}. Skipping this entry.")
            continue

        try:
            df_output = pd.read_csv(output_tsv_path, sep='\t', dtype={'chr_name': str})
            
            required_cols = ['chr_name', 'begin', 'end', 'p-value_adjusted']
            if not all(col in df_output.columns for col in required_cols):
                print(f"    Warning: {output_tsv_path} is missing one or more required columns: {required_cols}. Skipping.")
                continue

            df_output['p-value_adjusted'] = pd.to_numeric(df_output['p-value_adjusted'], errors='coerce')
            df_output.dropna(subset=['p-value_adjusted'], inplace=True)

        except pd.errors.EmptyDataError:
            print(f"    Warning: {output_tsv_path} is empty. Skipping.")
            continue
        except Exception as e:
            print(f"    Error reading or processing {output_tsv_path}: {e}. Skipping.")
            continue

        significant_df = df_output[df_output['p-value_adjusted'] < SIGNIFICANCE_THRESHOLD].copy()

        total_significant_windows = 0
        num_chrom_significant = 0
        most_significant_region_str = "N/A"
        max_neg_log10_p_adj = "N/A"

        if not significant_df.empty:
            total_significant_windows = len(significant_df)
            num_chrom_significant = significant_df['chr_name'].nunique()

            most_significant_row_idx = significant_df['p-value_adjusted'].idxmin()
            most_significant_row = significant_df.loc[most_significant_row_idx]

            begin_val = int(most_significant_row['begin'])
            end_val = int(most_significant_row['end'])
            most_significant_region_str = f"{most_significant_row['chr_name']}:{begin_val}-{end_val}"

            min_p_adj_val = most_significant_row['p-value_adjusted']
            if pd.isna(min_p_adj_val):
                 max_neg_log10_p_adj = "N/A"
            elif min_p_adj_val == 0:
                max_neg_log10_p_adj = -np.log10(np.finfo(float).tiny)
            elif min_p_adj_val > 0:
                max_neg_log10_p_adj = -np.log10(min_p_adj_val)
            else:
                 max_neg_log10_p_adj = np.nan

        emcdp_time_val = "N/A"
        try:
            df_metrics = pd.read_csv(metrics_tsv_path, sep='\t')
            if not df_metrics.empty and 'real_time' in df_metrics.columns:
                emcdp_time_val = df_metrics.iloc[0]['real_time']
        except pd.errors.EmptyDataError:
            print(f"    Warning: {metrics_tsv_path} is empty.")
        except Exception as e:
            print(f"    Error reading {metrics_tsv_path}: {e}.")

        summary_data.append({
            "Annotation Type": annotation_type,
            "Test Type": test_type,
            "Total Significant Windows": total_significant_windows,
            "No. Chromosomes with Significant Window(s)": num_chrom_significant,
            "Most Significant Region (Chr:Start-End)": most_significant_region_str,
            "Max -log10(Adj. P-value)": max_neg_log10_p_adj,
            "eMCDP time (s)": emcdp_time_val
        })

    if not summary_data:
        print("No data processed or found matching criteria. Output file will not be created.")
        return

    summary_df = pd.DataFrame(summary_data)

    output_columns = [
        "Annotation Type",
        "Test Type",
        "Total Significant Windows",
        "No. Chromosomes with Significant Window(s)",
        "Most Significant Region (Chr:Start-End)",
        "Max -log10(Adj. P-value)",
        "eMCDP time (s)"
    ]
    summary_df = summary_df[output_columns]

    summary_df.sort_values(by=["Annotation Type", "Test Type"], inplace=True, ignore_index=True)

    try:
        summary_df.to_csv(OUTPUT_FILENAME, sep='\t', index=False, float_format='%.4f', na_rep='N/A')
        print(f"\nSummary statistics successfully saved to {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"\nError writing output file {OUTPUT_FILENAME}: {e}")

if __name__ == "__main__":
    main()
