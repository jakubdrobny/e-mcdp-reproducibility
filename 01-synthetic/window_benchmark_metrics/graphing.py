import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def load_data(files):
    dfs = []
    for f in files:
        df = pd.read_csv(f, sep='\t')
        df['method'] = f.split('_div')[0]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def plot_comparison(data, y_col, y_label, title, output_file, log=False):
    plt.figure(figsize=(12, 7))
    
    methods = data['method'].unique()
    # colors = {'slow_bad': '#51a5e1', 'slow': '#1f77b4', 'fast_bad': '#5fd35f', 'fast': '#2ca02c'}
    colors = {'naive': '#ff7f0e', 'slow': '#1f77b4', 'fast': '#2ca02c'}
    
    for method in methods:
        method_data = data[data['method'] == method]
        plt.plot(
            method_data['group'],
            method_data[y_col],
            label=method,
            color=colors.get(method, '#d62728'),
            markersize=8,
            linewidth=2,
            linestyle='-'
        )

    if log:
        plt.xscale('log')
        plt.yscale('log')
    else:
        plt.grid(True, which='both', linestyle='--', alpha=0.7)
    plt.xlabel('Number of Reference Intervals', fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend(fontsize=12)
    
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
    plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

method = ["naive", "slow_bad", "slow", "fast_slow", "fast"]
step_divisors = [5, 10, 20]

def main():
    for step in step_divisors:
        if step != 10:
            continue

        # data = load_data([f"slow_bad_div{step}.tsv", f"slow_div{step}.tsv", f"fast_bad_div{step}.tsv", f"fast_div{step}.tsv"])
        data = load_data([f"slow_div{step}.tsv", f"naive_div{step}.tsv", f"fast_div{step}.tsv"])

        for log in [False, True]:
            plot_comparison(
                data,
                y_col='time_seconds_avg',
                y_label='Average Runtime (s)',
                title='Runtime Comparison by Method',
                output_file=f"3_method_runtime_comparison{"_log" if log else ""}.png",
                log=log
            )

        for log in [False, True]:
            plot_comparison(
                data,
                y_col='mem_mb_avg',
                y_label='Average Memory Usage (MB)',
                title='Memory Usage Comparison by Method',
                output_file=f"3_method_memory_comparison{"_log" if log else ""}.png",
                log=log
            )

    print(f"Graphs saved")

if __name__ == '__main__':
    main()
