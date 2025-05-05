import pandas as pd
import math
import os
import argparse

def tsv_to_bedgraph(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('output.tsv'):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.bedgraph'
            output_path = os.path.join(output_dir, output_filename)
            
            df = pd.read_csv(input_path, sep='\t')
            
            df['data_value'] = df['p-value_adjusted'].apply(
                lambda x: -math.log10(x) if x > 0 else 0
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
            
            print(f"Converted {filename} to {output_filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert TSV files to BedGraph format'
    )
    parser.add_argument(
        '-i', '--input', 
        required=True,
        help='Input directory containing TSV files'
    )
    parser.add_argument(
        '-o', '--output', 
        required=True,
        help='Output directory for BedGraph files'
    )
    
    args = parser.parse_args()
    
    tsv_to_bedgraph(args.input, args.output)
