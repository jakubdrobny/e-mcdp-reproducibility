from random import random
from argparse import ArgumentParser
import os

CHROMOSOME_SIZE = 1_000_000
COVERAGE = 0.1
CHROMOSOME_CNT = 2
INTERVAL_LENGTH = 100
CHR_SIZES_FILENAME = 'chr_sizes.txt'
EXPERIMENTS_LIST_PATH = 'experiments_list.tsv'

def generate_random_annotation():
    cur_ints = []
    chroms = []
    for chr_num in range(1, CHROMOSOME_CNT+1):
        cur_chrom_ints, chrom = [], [0 for _ in range(CHROMOSOME_SIZE)]
        for pos in range(0, CHROMOSOME_SIZE):
            if pos + INTERVAL_LENGTH >= CHROMOSOME_SIZE:
                break
            
            if cur_chrom_ints and cur_chrom_ints[-1][-1] > pos:
                continue
            
            if random() * INTERVAL_LENGTH < COVERAGE:
                cur_chrom_ints.append([f"chr{chr_num}", pos, pos + INTERVAL_LENGTH])
                for npos in range(pos, pos + INTERVAL_LENGTH):
                    chrom[npos] = 1
        
        cur_ints.extend(cur_chrom_ints)
        chroms.append(chrom)

    return cur_ints, chroms

def generate_dependent_annotation(dep_fac, chroms):
    cur_ints = []
    for chr_num in range(1, CHROMOSOME_CNT+1):
        cur_chrom_ints = []
        for pos in range(0, CHROMOSOME_SIZE):
            if pos + INTERVAL_LENGTH >= CHROMOSOME_SIZE:
                break
            
            if cur_chrom_ints and cur_chrom_ints[-1][-1] > pos:
                continue
            
            if random() * INTERVAL_LENGTH < COVERAGE * (1 if chr_num != 1 else dep_fac if chroms[chr_num - 1][pos] else 1 / dep_fac):
                cur_chrom_ints.append([f"chr{chr_num}", pos, pos + INTERVAL_LENGTH])
        
        cur_ints.extend(cur_chrom_ints)

    return cur_ints

def save_chr_sizes(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    chr_sizes_path = os.path.join(output_dir, CHR_SIZES_FILENAME)
    with open(chr_sizes_path, 'w') as f:
        f.write('\n'.join(f"chr{chr_num}\t{CHROMOSOME_SIZE}" for chr_num in range(1, CHROMOSOME_CNT + 1)))

    print(f"Chromosome sizes saved successfully in {chr_sizes_path}")
    return chr_sizes_path

def save_annotation(output_dir, intervals, prefix, dep_fac, test_run):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    annotation_path = os.path.join(output_dir, f"{prefix}_depfac{dep_fac}_{test_run}.bed")
    with open(annotation_path, 'w') as f:
        f.write('\n'.join(f"{i[0]}\t{i[1]}\t{i[2]}" for i in intervals))

    print(f"{'Reference' if prefix == 'ref' else 'Query'} annotation saved successfully in {annotation_path}")
    return annotation_path

def save_experiments_list(experiments_list):
    with open(EXPERIMENTS_LIST_PATH, 'w') as f:
        f.write('label\treference\tquery\tchr_sizes\n'+'\n'.join(f"{e[0]}\t{e[1]}\t{e[2]}\t{e[3]}" for e in experiments_list))

    print(f"Experiments list saved successfully in {EXPERIMENTS_LIST_PATH}")

def main():
    parser = ArgumentParser(description="generate annotations which are dependent on one chromosome and independent in the other")
    parser.add_argument('-o', '--output-dir', type=str, help='output directory')
    args = parser.parse_args()

    for dep_fac10 in range(100, 201, 10):
        dep_fac = dep_fac10 / 100
        for test_run in range(1, 11):
            ref_ints, chroms = generate_random_annotation()
            save_annotation(args.output_dir, ref_ints, 'ref', dep_fac, test_run)

            query_ints = generate_dependent_annotation(dep_fac, chroms)
            save_annotation(args.output_dir, query_ints, 'query', dep_fac, test_run)

if __name__ == "__main__":
    main()
