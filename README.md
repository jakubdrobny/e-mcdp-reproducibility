# eMCDP reproducibility

This repository contains the data used for the experiments.

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
