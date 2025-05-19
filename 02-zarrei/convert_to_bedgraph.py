import pandas as pd
import math
import os
import argparse

def tsv_to_bedgraph(input_dir):
    for cur_dir in os.listdir(input_dir):
        for stati in ['z-score', 'p-value_adjusted']:
            input_path = os.path.join(input_dir, cur_dir, "output.tsv")
            output_path = os.path.splitext(input_path)[0].replace('output', stati) + '.bedgraph'
            df = pd.read_csv(input_path, sep='\t')
            
            if stati != 'z-score':
                df['data_value'] = df['p-value_adjusted'].apply(
                    lambda x: max(0.0, -math.log10(x)) if x > 0 else 0
                )
            else:
                df['end'] = df['end'].apply(lambda x: x - 900000 * (1 if cur_dir.endswith('1000000') else 11))
                df['data_value'] = df['z-score'].fillna(0.0)
            
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
