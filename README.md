# eMCDP reproducibility

This repository contains the data used for the experiments.

## 01-synthetic

This directory contains data and results of time and memory experiments comparing eMCDP, MCDP [3] and MCDP[2] when performing whole-genome analysis and comparing the variants of eMCDP. The dataset used is the *01-synthetic* dataset from the [mcdp2-reproducibility repository](https://github.com/fmfi-compbio/mcdp2-reproducibility), which is the reproducibility repository for the MCDP2 study [2].

This directory consists of:
- `data/` directory containing the *01-synthetic* dataset from the [mcdp2-reproducibility repository](https://github.com/fmfi-compbio/mcdp2-reproducibility), which is the reproducibility repository for the MCDP2 study [2], which containes chromosome sizes and reference annotations in files `ref_{annotation_size}_{test_id}.bed` and query annotations in files `query_{annotation_size}_{test_id}.bed`
- `{emcdp|mcdp|mcdp2}_results/` directories each consisiting of directories `{annotation_size}_{test_id}`, each of these directories contains a log file (`log.txt`), metrics file (`metrics.tsv`) and the output file (`output.tsv`)
- `test_emcdp.sh`, `test_mcdp.sh` and `test_mcdp2.sh` bash script used for comparing each software on the `data/` dataset, produces results into the respective `{emcdp|mcdp|mcdp2}_results/` directory. the scripts assume the emcdp binary is located at `../../code/bin/emcdp`, the mcdp repository is located at `../../testing/mc-overlaps` and the mcdp2 is installed on the system as per its installation guide. the locations can be changed to whatever you want 
- `metrics/` directory containing the summarized metrics from `{emcdp|mcdp|mcdp2}_results/` directories and a `graphing.py` python script for converting the summaries into graphs (requires `pands` and `matplotlib`)
- `metrics_stats.sh` bash script, which summarizes the metrics from `{emcdp|mcdp|mcdp2}_results/` into the `metrics/` directory. the path to the binary assumes it is located at `../../code/bin/emcdp` when running the script from its location, it can be changed to whatever you want
- `window_benchmark_results/` directory contains the results of variant comparison on the `data/` directory running a window analysis with window size to window step ratiof 5, 10 and 20. the directory is populated by the `window_benchmark.sh` bash script which assumes the location of the emcdp binary is `../../code/bin/emcdp`
- `window_benchmak_metrics/` directory cotains the summary of metrics for each combination of `{naive|slow_bad|slow|fast_bad|fast}_div{step_ratio=5|10|20}` and a `graphing.py` python script used to create the graph for the thesis (requires `pandas` and `matplotlib`)

## 02-zarrei

This directory contains data and results of experiments on the Zarrei et al. (2015) [1] dataset, which we got from the [mcdp2-reproducibility repository](https://github.com/fmfi-compbio/mcdp2-reproducibility), which is the reproducibility repository for the MCDP2 study [2].

This directory consists of:
- `data/` directory containing the chromosome sizes, copy number losses annotation (`inclusive.loss`) and the annotations of exons of all genes, exons of all non-coding genes and exons of all protein coding genes.
- `results/` directory, which consists of directories corresponding to each combination of `{gene_annotation_file}!{reference_annotation_file}_{enrichment/depletion}_ws{window_size_used}`, each of these directories contains a log file (`log.txt`), metrics file (`metrics.tsv`), output file (`output.tsv`) and bedgraphs of adjusted p-values (`p-values_adjusted.bedgraph`) and z-scores (`z-score.bedgraph`), which can be imported into the UCSC Genome Browser [3] (make sure to copy the contents of the bedgraph files manually, since importing them into the browser directly did not work for some reason)
- `experiments.tsv` containting the combination of files for the experiments
- `run.sh` bash script, which was used to run the analysis for all experiments in the `experiments_list.tsv` file. the path to the binary assumes it is located at `../../code/bin/emcdp` when running the script from its location, it can be changed to whatever you want
- `table_summary_data.tsv` tab-separated file with summary of the results used in the Results chapter of the thesis created by the `summarize_into_tsv.py` python script (requires `pandas` and `numpy`)
- `convert_to_bedgraph.py` python script used to convert each `output.tsv` output file into the bedgraph files (requires `pandas` and `numpy`)

## 03-synthetic-dependency

This directory contains data and results of experiments examing the ability of eMCDP to detect significant and non-significant overlap in windows.

It consists of:
- `data/` directory containing chromosome sizes in `chr_sizes.txt`, reference annotations `ref_depfac{dependency_factor}_{test_id}.bed` and query annotations `query_depfac{dependency_factor}_{test_id}.bed`, the experiments used pairs of a reference and query annotations with the same dependency factor and test id
- `results/` directory contains logs (`log.txt`), metrics (`metrics.tsv`) and output (`output.tsv`) for each test mentioned in the previous item of this list in its own directory
- `run.sh` bash script, which was used to run the analysis for the tests mentioned in the first item of this list. the path to the binary again assumes it is located at `../../code/bin/emcdp`, it can be changed to whatever you want
- `generate_annotations.py` python script used to generate annotations as described in the Significance detection section of the thesis
- `summarize.py` python script used to generate graphs from the results of the analyses (requires `pandas`, `numpy` and `matplotlib`)

## 04-synthetic-window-accuracy

This directory contains data and results of experiments examing the ability of eMCDP to detect significant overlap with varying window sizes.

It consists of:
- `data/` directory containing chromosome sizes in `chr_sizes.txt`, reference annotations `ref_{test_id}.bed` and query annotations `query_{test_id}.bed`, the experiments used pairs of a reference and query annotations with the same test id and run the eMCDP program for window sizes of 800kb, 600kb, 400kb, 200kb, 100kb, 80kb, 60kb, 40kb, 20kb and 10kb for each test, window step was set to minimum of 5kb and 1/10th of the window size as mentioned in the thesis
- `results/` directory contains logs (`log.txt`), metrics (`metrics.tsv`) and output (`output.tsv`) for each test mentioned in the previous item of this list in its own directory in format `{window_size}_{test_id}`
- `run.sh` bash script, which was used to run the analysis for the tests mentioned in the first item of this list. the path to the binary again assumes it is located at `../../code/bin/emcdp`, it can be changed to whatever you want
- `generate_annotations.py` python script used to generate annotations as described in the Significance detection section of the thesis
- `summarize.py` python script used to generate graphs from the results of the analyses (requires `pandas`, `numpy` and `matplotlib`)

## References

> [1] Mehdi Zarrei, Jeffrey R. MacDonald, Daniele Merico, and Stephen W. Scherer.
> A copy number variation map of the human genome. Nature Reviews Genetics,
> 16(3):172–183, Mar 2015

> [2] Askar Gafurov, Tomáš Vinař, Paul Medvedev, Bronislava Brejová. Efficient Analysis of Annotation Colocalization Accounting for Genomic Contexts. In: Ma, J. (eds) Research in Computational Molecular Biology. RECOMB 2024. Lecture Notes in Computer Science, vol 14758. Springer, Cham. https://doi.org/10.1007/978-1-0716-3989-4_3

> [3] Askar Gafurov, Bronislava Brejová, Paul Medvedev.
> Markov chains improve the significance computation of overlapping genome annotations,
> Bioinformatics, Volume 38, Issue Supplement_1, July 2022, Pages i203–i211, https://doi.org/10.1093/bioinformatics/btac255
