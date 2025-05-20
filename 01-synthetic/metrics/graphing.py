import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def load_data(files):
    dfs = []
    for f in files:
        df = pd.read_csv(f, sep='\t')
        df['method'] = f.split('.')[0]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def plot_comparison(data, y_col, y_label, title, output_file, log=False):
    plt.figure(figsize=(12, 7))
    
    methods = data['method'].unique()
    colors = {'mcdp': '#1f77b4', 'emcdp': '#ff7f0e', 'mcdp2': '#2ca02c'}
    
    for method in methods:
        method_data = data[data['method'] == method]
        plt.plot(
            method_data['group'],
            method_data[y_col],
            label="eMCDP" if method == "emcdp" else method.upper(),
            color=colors.get(method, '#d62728'),
            markersize=8,
            linewidth=2
        )

    if log:
        plt.xscale('log')
        plt.yscale('log')
    else:
        plt.grid(True, which='both', linestyle='--', alpha=0.7)
    plt.xlabel('Number of Reference Intervals', fontsize=20)
    plt.ylabel(y_label, fontsize=20)
    plt.title(title, fontsize=24)
    plt.legend(fontsize=18)
    
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
    plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())

    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def main():
    data = load_data(["mcdp.tsv", "emcdp.tsv", "mcdp2.tsv"])

    for log in [0, 1]:
        plot_comparison(
            data,
            y_col='time_seconds_avg',
            y_label='Average Runtime (s)',
            title='Runtime Comparison by Method',
            output_file=f"runtime_comparison{"_log" if log else ""}.png",
            log=log
        )

    for log in [0, 1]:
        plot_comparison(
            data,
            y_col='mem_mb_avg',
            y_label='Average Memory Usage (MB)',
            title='Memory Usage Comparison by Method',
            output_file=f"memory_comparison{"_log" if log else ""}.png",
            log=log
        )

    print(f"Graphs saved")

if __name__ == '__main__':
    main()
