#!/bin/bash

EXPERIMENTS_TSV="../mc-overlaps-reproducibility/04-synthetic-data-time-mem/experiments.tsv"
BASE_DIR=$(dirname "$EXPERIMENTS_TSV")
BINARY_PATH="../code/bin/e-mcdp"

if [ ! -f "$BINARY_PATH" ]; then
  echo "Error: e-mcdp binary not found at $BINARY_PATH"
  exit 1
fi

if [ ! -f "$EXPERIMENTS_TSV" ]; then
  echo "Error: Experiments TSV not found at $EXPERIMENTS_TSV"
  exit 1
fi

tail -n +2 "$EXPERIMENTS_TSV" | while IFS=$'\t' read -r label reference query chr_sizes; do
  ref_file="$BASE_DIR/$reference"
  query_file="$BASE_DIR/$query"
  chr_sizes_file="$BASE_DIR/$chr_sizes"

  if [ ! -f "$ref_file" ]; then
    echo "Error: Reference file $ref_file not found for experiment $label"
    exit 1
  fi

  if [ ! -f "$query_file" ]; then
    echo "Error: Query file $query_file not found for experiment $label"
    exit 1
  fi

  if [ ! -f "$chr_sizes_file" ]; then
    echo "Error: Chromosome sizes file $chr_sizes_file not found for experiment $label"
    exit 1
  fi

  echo "Running experiment: $label"
  "$BINARY_PATH" --r "$ref_file" --q "$query_file" --chs "$chr_sizes_file"

  if [ $? -ne 0 ]; then
    echo "Error: Experiment $label failed to execute"
  fi
done

echo "All experiments executed"
