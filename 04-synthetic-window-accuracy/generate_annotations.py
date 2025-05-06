from random import random
from argparse import ArgumentParser
import os

CHROMOSOME_SIZE = 1_000_000
COVERAGE = 0.1
CHROMOSOME_CNT = 1
INTERVAL_LENGTH = 100
CHR_SIZES_FILENAME = 'chr_sizes.txt'

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
            
            if random() * INTERVAL_LENGTH < COVERAGE * (1 if pos < CHROMOSOME_SIZE * 9 / 20 or pos >= CHROMOSOME_SIZE * 11 / 20 else dep_fac if chroms[chr_num - 1][pos] else 1 / dep_fac):
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

def save_annotation(output_dir, intervals, prefix, test_run):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    annotation_path = os.path.join(output_dir, f"{prefix}_{test_run}.bed")
    with open(annotation_path, 'w') as f:
        f.write('\n'.join(f"{i[0]}\t{i[1]}\t{i[2]}" for i in intervals))

    print(f"{'Reference' if prefix == 'ref' else 'Query'} annotation saved successfully in {annotation_path}")
    return annotation_path

def main():
    parser = ArgumentParser(description="generate annotations which are dependent on one chromosome and independent in the other")
    parser.add_argument('-o', '--output-dir', type=str, help='output directory')
    args = parser.parse_args()

    save_chr_sizes(args.output_dir)

    dep_fac = 10
    
    for test_run in range(1, 11):
        ref_ints, chroms = generate_random_annotation()
        save_annotation(args.output_dir, ref_ints, 'ref', test_run)

        query_ints = generate_dependent_annotation(dep_fac, chroms)
        save_annotation(args.output_dir, query_ints, 'query', test_run)

if __name__ == "__main__":
    main()
