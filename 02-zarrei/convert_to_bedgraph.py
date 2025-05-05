import pandas as pd
import math
import os
import argparse

def tsv_to_bedgraph(input_dir):
    for cur_dir in os.listdir(input_dir):
        input_path = os.path.join(input_dir, cur_dir, "output.tsv")
        output_path = os.path.splitext(input_path)[0] + '.bedgraph'
        df = pd.read_csv(input_path, sep='\t')
        
        df['data_value'] = df['p-value_adjusted'].apply(
            lambda x: max(0.0, -math.log10(x)) if x > 0 else 0
        )
        
        bedgraph_df = df[[
            'chr_name', 
            'begin', 
            'end', 
            'data_value'
        ]].copy()
        
        bedgraph_df = bedgraph_df.sort_values(['chr_name', 'begin', 'end'])
        
        bedgraph_df.to_csv(
            output_path,
            sep='\t',
            header=False,
            index=False,
            float_format='%.10f'
        )
        
        print(f"Converted {input_path} to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert TSV files to BedGraph format'
    )
    parser.add_argument(
        '-i', '--input', 
        required=True,
        help='Input directory containing TSV files'
    ) 
    
    args = parser.parse_args()
    
    tsv_to_bedgraph(args.input)
